"""Scan markdown files for sensitive information and replace with placeholders.

Usage:
    python .ai-work/tooling/mask_sensitive.py <input> [options]

    input               File (.md) or directory to scan (recursive for dirs)

Options:
    --output-dir DIR    Write masked files here (default: alongside originals,
                        suffix _masked before extension)
    --mapping FILE      Save placeholder→original mapping as JSON
                        (default: <output_dir>/mask_mapping.json)
    --in-place          Overwrite originals (mutually exclusive with --output-dir)
    --dry-run           Print findings without writing any files
    --no-mapping        Do not write a mapping file
    --patterns FILE     Load extra regex patterns from a JSON file
                        Format: {"TYPE_NAME": "regex_pattern", ...}
    --names FILE        Load named-entity lists (projects, customers, systems)
                        Format: {"PROJECT": ["Alpha", ...], "CUSTOMER": [...], "SYSTEM": [...]}
                        Any top-level key becomes a mask type, e.g. [PROJECT_1].
                        Matching is case-insensitive, whole-word.

Exit codes: 0 = ok, 1 = usage error, 2 = I/O error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Force UTF-8 stdout/stderr (Windows cp932 safety)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Sensitive-data patterns (ordered — more specific first)
# Each tuple: (TYPE_NAME, compiled_regex, capture_group_index_or_None)
#   - capture_group=None  → replace the whole match
#   - capture_group=1     → replace only group(1), keep surrounding text
# ---------------------------------------------------------------------------
_RAW_PATTERNS: List[Tuple[str, str, Optional[int]]] = [
    # URLs with embedded credentials  user:pass@host
    (
        "URL_WITH_CREDS",
        r"https?://[A-Za-z0-9_.%+-]+:[A-Za-z0-9_.%+\-@!#$&'*=?]+@[^\s\"'>)]+",
        None,
    ),
    # API key / token assignments  (key = "value")
    (
        "API_KEY",
        r'(?i)(?:api[_\-]?key|access[_\-]?token|secret[_\-]?key|auth[_\-]?token'
        r'|bearer|private[_\-]?key)\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{16,})["\']?',
        1,
    ),
    # Password assignments  password = "value"
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
    # Vietnamese phone numbers  (0xx, +84xx, 84xx)
    (
        "PHONE_VN",
        r"(?<!\d)(?:\+?84|0084)?0?(?:3[2-9]|5[6-9]|7[0679]|8[0-9]|9[0-9])\d{7}(?!\d)",
        None,
    ),
    # International phone  +country-code ...  (7–15 digits, not just a year)
    (
        "PHONE_INTL",
        r"(?<!\d)\+(?:[1-9][0-9]{1,2})[\s\-]?(?:[0-9][\s\-]?){6,13}[0-9](?!\d)",
        None,
    ),
    # IPv4 addresses (skip 0.0.0.0 and 255.255.255.255 style all-same)
    (
        "IP_ADDRESS",
        r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)",
        None,
    ),
    # Credit / debit card numbers  (4×4 groups with optional separator)
    (
        "CREDIT_CARD",
        r"(?<!\d)(?:[0-9]{4}[- ]?){3}[0-9]{4}(?!\d)",
        None,
    ),
    # Vietnamese CCCD (12 digits) — must appear as a standalone token
    (
        "VN_CCCD",
        r"(?<!\d)[0-9]{12}(?!\d)",
        None,
    ),
    # Vietnamese CMND (9 digits) — standalone token
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
# Core masking logic
# ---------------------------------------------------------------------------

class SensitiveMasker:
    """Stateful masker: accumulates placeholder→value mapping across calls."""

    def __init__(self, patterns: List[Tuple[str, re.Pattern, Optional[int]]]) -> None:
        self._patterns = patterns
        # mapping: placeholder → original value
        self.mapping: Dict[str, str] = {}
        # counters per type
        self._counters: Dict[str, int] = {}
        # reverse index to reuse placeholders for identical values
        self._value_to_ph: Dict[str, str] = {}

    def _placeholder(self, type_name: str, value: str) -> str:
        if value in self._value_to_ph:
            return self._value_to_ph[value]
        n = self._counters.get(type_name, 0) + 1
        self._counters[type_name] = n
        ph = f"[{type_name}_{n}]"
        self.mapping[ph] = value
        self._value_to_ph[value] = ph
        return ph

    def mask_text(self, text: str) -> Tuple[str, int]:
        """Return (masked_text, count_of_replacements)."""
        total = 0
        for type_name, pattern, grp in self._patterns:
            def _replacer(m: re.Match, tn: str = type_name, g: Optional[int] = grp) -> str:
                nonlocal total
                if g is None:
                    original = m.group(0)
                    ph = self._placeholder(tn, original)
                    total += 1
                    return ph
                else:
                    original = m.group(g)
                    ph = self._placeholder(tn, original)
                    total += 1
                    # Replace only the captured portion, keep surrounding text
                    full = m.group(0)
                    return full[: m.start(g) - m.start(0)] + ph + full[m.end(g) - m.start(0) :]
            text = pattern.sub(_replacer, text)
        return text, total


# ---------------------------------------------------------------------------
# Named-entity (project / customer / system) helpers
# ---------------------------------------------------------------------------

def load_name_patterns(
    path: Path,
) -> List[Tuple[str, re.Pattern, Optional[int]]]:
    """Load a JSON dict of {TYPE: [name, ...]} and compile into patterns.

    Each name is matched case-insensitively as a whole word / phrase.
    Names are sorted longest-first so longer variants win over substrings.
    """
    raw: Dict[str, List[str]] = json.loads(path.read_text(encoding="utf-8"))
    compiled: List[Tuple[str, re.Pattern, Optional[int]]] = []
    for type_name, names in raw.items():
        type_key = type_name.upper().replace(" ", "_")
        if not names:
            continue
        # Sort longest first to avoid shorter name shadowing longer one
        sorted_names = sorted(names, key=len, reverse=True)
        escaped = [re.escape(n) for n in sorted_names]
        # Word boundary: \b works for ASCII; for names ending/starting with
        # non-word chars (e.g. "Corp."), use lookahead/lookbehind on whitespace
        # or start/end-of-string as fallback.
        union = "|".join(f"(?:{e})" for e in escaped)
        pat = re.compile(
            r"(?<![A-Za-z0-9_])(?:" + union + r")(?![A-Za-z0-9_])",
            re.IGNORECASE,
        )
        compiled.append((type_key, pat, None))
    return compiled


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def collect_markdown_files(target: Path) -> List[Path]:
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.md"))


# ---------------------------------------------------------------------------
# Output path helpers
# ---------------------------------------------------------------------------

def masked_path(original: Path, output_dir: Optional[Path], in_place: bool) -> Path:
    if in_place:
        return original
    if output_dir:
        rel = original.name  # flat output — avoids accidental collisions
        return output_dir / (original.stem + "_masked" + original.suffix)
    return original.with_name(original.stem + "_masked" + original.suffix)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Mask sensitive information in Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input", help="Markdown file or directory to scan")
    p.add_argument("--output-dir", metavar="DIR", help="Directory for masked output files")
    p.add_argument(
        "--mapping",
        metavar="FILE",
        help="Path for the JSON mapping file (default: next to output)",
    )
    p.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite originals instead of writing _masked copies",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print findings without writing any files",
    )
    p.add_argument(
        "--no-mapping",
        action="store_true",
        help="Do not write a mapping file",
    )
    p.add_argument(
        "--patterns",
        metavar="FILE",
        help="JSON file with extra patterns: {TYPE_NAME: regex, ...}",
    )
    p.add_argument(
        "--names",
        metavar="FILE",
        help=(
            "JSON file with named-entity lists to mask: "
            '{"PROJECT": ["Alpha", ...], "CUSTOMER": [...], "SYSTEM": [...]}'
        ),
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.in_place and args.output_dir:
        parser.error("--in-place and --output-dir are mutually exclusive")

    # Load patterns
    patterns = list(DEFAULT_PATTERNS)
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

    if args.names:
        names_path = Path(args.names)
        if not names_path.exists():
            print(f"ERROR: names file not found: {names_path}", file=sys.stderr)
            return 1
        try:
            name_patterns = load_name_patterns(names_path)
            # Named entities go first — longer/more specific before generic regex
            patterns = name_patterns + patterns
            loaded_types = [t for t, _, _ in name_patterns]
            print(f"Loaded named-entity types: {', '.join(loaded_types)}")
        except Exception as exc:
            print(f"ERROR: could not load names file: {exc}", file=sys.stderr)
            return 1

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir and not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    files = collect_markdown_files(input_path)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        return 0

    masker = SensitiveMasker(patterns)
    total_files_changed = 0
    total_replacements = 0

    for fpath in files:
        try:
            original_text = fpath.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"WARN: cannot read {fpath}: {exc}", file=sys.stderr)
            continue

        masked_text, count = masker.mask_text(original_text)

        if count == 0:
            print(f"  clean  {fpath}")
            continue

        total_replacements += count
        total_files_changed += 1
        out_path = masked_path(fpath, output_dir, args.in_place)

        if args.dry_run:
            print(f"  DRY    {fpath}  →  {count} replacement(s)")
            # Show what was found
            for ph, val in masker.mapping.items():
                # Only print those found in this file pass (approximate)
                if val in original_text:
                    short = val[:60] + "…" if len(val) > 60 else val
                    print(f"           {ph}  ←  {short!r}")
        else:
            try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(masked_text, encoding="utf-8")
                print(f"  masked {fpath}  →  {out_path}  ({count} replacement(s))")
            except Exception as exc:
                print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
                return 2

    # Summary
    print(
        f"\nDone: {total_files_changed}/{len(files)} file(s) had sensitive data, "
        f"{total_replacements} total replacement(s)."
    )

    # Write mapping
    if not args.dry_run and not args.no_mapping and masker.mapping:
        if args.mapping:
            mapping_path = Path(args.mapping)
        elif output_dir:
            mapping_path = output_dir / "mask_mapping.json"
        else:
            mapping_path = input_path.parent / "mask_mapping.json" if input_path.is_dir() else input_path.with_name("mask_mapping.json")

        try:
            mapping_path.parent.mkdir(parents=True, exist_ok=True)
            mapping_path.write_text(
                json.dumps(masker.mapping, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Mapping saved: {mapping_path}")
        except Exception as exc:
            print(f"WARN: could not write mapping: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
