"""Scan markdown files for sensitive information and report findings.

Read-only analysis tool — no files are modified.
Use mask_sensitive.py to apply masking after reviewing this report.

Usage:
    # Scan a single file
    python .ai-work/tooling/scan_sensitive.py report.md

    # Scan a specific directory
    python .ai-work/tooling/scan_sensitive.py docs/

    # Scan entire project (omit input → uses current directory)
    python .ai-work/tooling/scan_sensitive.py

    # Scan project with named entities + save JSON report
    python .ai-work/tooling/scan_sensitive.py --names names.json --format json --output scan_report.json

Options:
    input               File or directory to scan. Omit to scan entire project
                        (current working directory, recursive).
    --names FILE        Named-entity lists to detect (same format as mask_sensitive.py)
                        {"PROJECT": ["Alpha", ...], "CUSTOMER": [...], "SYSTEM": [...]}
    --patterns FILE     Extra regex patterns: {"TYPE_NAME": "regex_pattern", ...}
    --exclude PATTERN   Glob pattern to exclude (repeatable). Applied relative to
                        scan root. Default excludes: temp, .git, __pycache__, node_modules.
                        Example: --exclude "archive/**" --exclude "*.bak.md"
    --output FILE       Write report to file instead of stdout
    --format FORMAT     Output format: text (default), json, csv
    --truncate N        Truncate found values to N chars in report (default: 80, 0=full)
    --summary-only      Print only the type/count summary, skip per-line findings

Exit codes:
    0   No findings (all clean)
    1   Usage / configuration error
    2   I/O error
    3   Findings detected
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Force UTF-8 stdout/stderr (Windows cp932 safety)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Sensitive-data patterns  (ordered: more specific first)
# Tuple: (TYPE_NAME, raw_regex, capture_group_or_None)
#   capture_group=None  → report the whole match
#   capture_group=1     → report only group(1)
# ---------------------------------------------------------------------------
_RAW_PATTERNS: List[Tuple[str, str, Optional[int]]] = [
    # URLs with embedded credentials
    (
        "URL_WITH_CREDS",
        r"https?://[A-Za-z0-9_.%+-]+:[A-Za-z0-9_.%+\-@!#$&'*=?]+@[^\s\"'>)]+",
        None,
    ),
    # API key / token assignments
    (
        "API_KEY",
        r'(?i)(?:api[_\-]?key|access[_\-]?token|secret[_\-]?key|auth[_\-]?token'
        r'|bearer|private[_\-]?key)\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{16,})["\']?',
        1,
    ),
    # Password assignments
    (
        "PASSWORD",
        r'(?i)(?:password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\'<>\n]{4,})["\']?',
        1,
    ),
    # Email addresses
    (
        "EMAIL",
        r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        None,
    ),
    # Vietnamese phone numbers
    (
        "PHONE_VN",
        r"(?<!\d)(?:\+?84|0084)?0?(?:3[2-9]|5[6-9]|7[0679]|8[0-9]|9[0-9])\d{7}(?!\d)",
        None,
    ),
    # International phone  +country-code …
    (
        "PHONE_INTL",
        r"(?<!\d)\+(?:[1-9][0-9]{1,2})[\s\-]?(?:[0-9][\s\-]?){6,13}[0-9](?!\d)",
        None,
    ),
    # IPv4 addresses
    (
        "IP_ADDRESS",
        r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)",
        None,
    ),
    # Credit / debit card numbers  (4×4 groups)
    (
        "CREDIT_CARD",
        r"(?<!\d)(?:[0-9]{4}[- ]?){3}[0-9]{4}(?!\d)",
        None,
    ),
    # Vietnamese CCCD (12 digits standalone)
    (
        "VN_CCCD",
        r"(?<!\d)[0-9]{12}(?!\d)",
        None,
    ),
    # Vietnamese CMND (9 digits standalone)
    (
        "VN_CMND",
        r"(?<!\d)[0-9]{9}(?!\d)",
        None,
    ),
]


def _compile_patterns(
    raw: List[Tuple[str, str, Optional[int]]],
) -> List[Tuple[str, re.Pattern, Optional[int]]]:
    return [(name, re.compile(pat), grp) for name, pat, grp in raw]


DEFAULT_PATTERNS = _compile_patterns(_RAW_PATTERNS)


# ---------------------------------------------------------------------------
# Named-entity loader (projects / customers / systems)
# ---------------------------------------------------------------------------

def load_name_patterns(path: Path) -> List[Tuple[str, re.Pattern, Optional[int]]]:
    """Load {TYPE: [name, ...]} JSON and compile into case-insensitive patterns."""
    raw: Dict[str, List[str]] = json.loads(path.read_text(encoding="utf-8"))
    compiled: List[Tuple[str, re.Pattern, Optional[int]]] = []
    for type_name, names in raw.items():
        type_key = type_name.upper().replace(" ", "_")
        if not names:
            continue
        sorted_names = sorted(names, key=len, reverse=True)
        escaped = [re.escape(n) for n in sorted_names]
        union = "|".join(f"(?:{e})" for e in escaped)
        pat = re.compile(
            r"(?<![A-Za-z0-9_])(?:" + union + r")(?![A-Za-z0-9_])",
            re.IGNORECASE,
        )
        compiled.append((type_key, pat, None))
    return compiled


# ---------------------------------------------------------------------------
# Finding dataclass
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    file: str
    line: int       # 1-based
    col: int        # 1-based, start of match (or captured group)
    type: str
    value: str      # raw matched value (full, not truncated)

    def display_value(self, truncate: int) -> str:
        if truncate <= 0 or len(self.value) <= truncate:
            return self.value
        return self.value[:truncate] + "…"


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

def scan_text(
    text: str,
    patterns: List[Tuple[str, re.Pattern, Optional[int]]],
    file_label: str,
) -> List[Finding]:
    """Scan *text* line-by-line and return all findings."""
    findings: List[Finding] = []
    lines = text.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for type_name, pattern, grp in patterns:
            for m in pattern.finditer(line):
                if grp is None:
                    value = m.group(0)
                    col = m.start(0) + 1
                else:
                    try:
                        value = m.group(grp)
                        col = m.start(grp) + 1
                    except IndexError:
                        value = m.group(0)
                        col = m.start(0) + 1
                findings.append(Finding(
                    file=file_label,
                    line=lineno,
                    col=col,
                    type=type_name,
                    value=value,
                ))
    return findings


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_text(
    findings: List[Finding],
    truncate: int,
    summary_only: bool,
    total_files_scanned: int = 0,
) -> str:
    buf = io.StringIO()

    if not findings:
        buf.write("No sensitive data found.\n")
        return buf.getvalue()

    if not summary_only:
        # Group by file for readability
        current_file = None
        for f in sorted(findings, key=lambda x: (x.file, x.line, x.col)):
            if f.file != current_file:
                buf.write(f"\n{f.file}\n")
                current_file = f.file
            buf.write(
                f"  line {f.line:>4}, col {f.col:>3}  [{f.type:<16}]  {f.display_value(truncate)}\n"
            )

    # Summary
    from collections import Counter
    type_counts: Counter = Counter(f.type for f in findings)
    file_counts: Counter = Counter(f.file for f in findings)
    files_affected = len(file_counts)

    buf.write(f"\n--- Summary ---\n")
    for type_name, count in sorted(type_counts.items()):
        buf.write(f"  {type_name:<20} {count:>4} occurrence(s)\n")
    buf.write(f"\n  Total findings : {len(findings)}\n")
    buf.write(f"  Files affected : {files_affected}")
    if total_files_scanned:
        buf.write(f" / {total_files_scanned} scanned")
    buf.write("\n")

    return buf.getvalue()


def format_json(findings: List[Finding], truncate: int) -> str:
    data = [
        {
            "file": f.file,
            "line": f.line,
            "col": f.col,
            "type": f.type,
            "value": f.display_value(truncate),
        }
        for f in findings
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_csv(findings: List[Finding], truncate: int) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["file", "line", "col", "type", "value"])
    for f in findings:
        writer.writerow([f.file, f.line, f.col, f.type, f.display_value(truncate)])
    return buf.getvalue()


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

# Directories that are almost never "project documents"
_DEFAULT_EXCLUDES = {
    "temp",
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}


def collect_markdown_files(
    target: Path,
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """Return sorted list of .md files under *target*, respecting excludes."""
    if target.is_file():
        return [target]

    results: List[Path] = []
    for fpath in target.rglob("*.md"):
        if _should_exclude(fpath, target, exclude_patterns or []):
            continue
        results.append(fpath)
    return sorted(results)


def _should_exclude(
    fpath: Path,
    root: Path,
    extra_patterns: List[str],
) -> bool:
    """Return True if *fpath* matches any default or user-specified exclude."""
    # Check each path component against default excludes
    try:
        rel = fpath.relative_to(root)
    except ValueError:
        rel = fpath

    parts = rel.parts
    for part in parts[:-1]:  # directory components only
        if part in _DEFAULT_EXCLUDES:
            return True

    # Check user-supplied glob patterns (matched against relative path)
    rel_str = rel.as_posix()
    for pattern in extra_patterns:
        if _glob_match(rel_str, pattern):
            return True

    return False


def _glob_match(path_str: str, pattern: str) -> bool:
    """Simple glob match using fnmatch (supports * and **)."""
    import fnmatch
    # fnmatch doesn't support **, so normalise ** → * for basic support
    simple = pattern.replace("**", "*")
    return fnmatch.fnmatch(path_str, simple) or fnmatch.fnmatch(
        path_str.split("/")[-1], simple
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Scan markdown files for sensitive information (read-only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "input",
        nargs="?",
        default=".",
        help="File or directory to scan (default: current directory = full project scan)",
    )
    p.add_argument(
        "--names",
        metavar="FILE",
        help=(
            "JSON file with named-entity lists: "
            '{"PROJECT": ["Alpha", ...], "CUSTOMER": [...], "SYSTEM": [...]}'
        ),
    )
    p.add_argument(
        "--patterns",
        metavar="FILE",
        help='JSON file with extra patterns: {"TYPE_NAME": "regex_pattern", ...}',
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        help="Write report to file (default: stdout)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--truncate",
        type=int,
        default=80,
        metavar="N",
        help="Truncate values to N chars in report (default: 80, 0=full)",
    )
    p.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the summary counts, skip per-line findings",
    )
    p.add_argument(
        "--exclude",
        metavar="PATTERN",
        action="append",
        default=[],
        help=(
            "Glob pattern to exclude relative to scan root (repeatable). "
            "Default exclusions: temp, .git, __pycache__, node_modules, .venv, dist, build."
        ),
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Build pattern list
    patterns = list(DEFAULT_PATTERNS)

    if args.names:
        names_path = Path(args.names)
        if not names_path.exists():
            print(f"ERROR: names file not found: {names_path}", file=sys.stderr)
            return 1
        try:
            name_pats = load_name_patterns(names_path)
            patterns = name_pats + patterns  # named entities first
            loaded = [t for t, _, _ in name_pats]
            print(f"Named-entity types loaded: {', '.join(loaded)}", file=sys.stderr)
        except Exception as exc:
            print(f"ERROR: could not load names file: {exc}", file=sys.stderr)
            return 1

    if args.patterns:
        extra_path = Path(args.patterns)
        if not extra_path.exists():
            print(f"ERROR: patterns file not found: {extra_path}", file=sys.stderr)
            return 1
        try:
            extra = json.loads(extra_path.read_text(encoding="utf-8"))
            for name, pat in extra.items():
                patterns.append((name, re.compile(pat), None))
        except Exception as exc:
            print(f"ERROR: could not load patterns file: {exc}", file=sys.stderr)
            return 1

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 1

    scan_label = "project" if args.input == "." else str(input_path)
    print(f"Scanning: {scan_label}", file=sys.stderr)
    if args.exclude:
        print(f"Excluding patterns: {args.exclude}", file=sys.stderr)

    files = collect_markdown_files(input_path, args.exclude)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        return 0

    print(f"Files to scan: {len(files)}", file=sys.stderr)

    all_findings: List[Finding] = []

    for fpath in files:
        try:
            text = fpath.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"WARN: cannot read {fpath}: {exc}", file=sys.stderr)
            continue

        findings = scan_text(text, patterns, str(fpath))
        if findings:
            print(f"  found  {fpath}  ({len(findings)} finding(s))", file=sys.stderr)
        else:
            print(f"  clean  {fpath}", file=sys.stderr)

        all_findings.extend(findings)

    # Format report
    if args.format == "json":
        report = format_json(all_findings, args.truncate)
    elif args.format == "csv":
        report = format_csv(all_findings, args.truncate)
    else:
        report = format_text(all_findings, args.truncate, args.summary_only, len(files))

    # Output
    if args.output:
        out_path = Path(args.output)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(report, encoding="utf-8")
            print(f"Report written: {out_path}", file=sys.stderr)
        except Exception as exc:
            print(f"ERROR: cannot write report: {exc}", file=sys.stderr)
            return 2
    else:
        print(report)

    return 3 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
