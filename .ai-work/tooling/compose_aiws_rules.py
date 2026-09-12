#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compose_aiws_rules.py — render AIWS rules into per-tool rule files (CR-AIWS-2026-08-066 C3).

ONE source of rules, N tool files. Core rules live in `.ai-work/AIWS.md`; per-tool adapters live in
`.ai-work/install_templates/adapter_<tool>.md`. Everything this tool generates sits inside a single
AIWS-owned block:

    <!-- AIWS:BEGIN rules v=<version> target=<tool> -->
    AIWS rules <version> (target=<tool>) — do not edit inside this block
    …adapter…
    …core (inline) or `@.ai-work/AIWS.md` (Claude import)…
    <!-- AIWS:END rules -->

Bytes OUTSIDE that block are project-owned and are never touched: the tool reads/writes BYTES,
preserves the target's EOL style and BOM, backs the file up, and self-verifies the outside-block
bytes after writing (restoring the backup if they moved). Text-mode writes are deliberately unused:
`.ai-work/tests/test_cr059_060_wave.py` T1 pins that no corpus writer calls write_text bare, and
bytes I/O is what makes "preserve the target's own EOL" possible in the first place.

Version comes from ONE place, resolved in two tiers and never guessed:
  1. `.ai-work/install_templates/VERSION`  — stamped at package build, carried by the section copy
  2. source tree only: `product/aiws_version.md` pin + `-src` suffix (a repo that BUILDS the package
     never installs one, so it has no manifest)
  3. neither → error (no `.aiws-version` fallback: install/quick-install do not write that file)

Verbs (all default to DRY-RUN; pass --apply to write):
  --init --tools claude,agents,copilot [--claude-file CLAUDE.local.md|CLAUDE.md] [--project-name X]
  --migrate-legacy --tools …     wrap a hand-written AIWS section into the block
  --refresh [--tools …]          replace the block contents (adapter + core + version)
  --check                        report every rule file's block version; non-zero if they disagree

Python 3.8+, stdlib only.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import find_ai_work_root, parse_frontmatter  # noqa: E402  (also forces UTF-8 stdout)

TOOLS = ("claude", "agents", "copilot")
CLAUDE_FILES = ("CLAUDE.local.md", "CLAUDE.md")
# Core-rules filename. ONE constant so a rename touches one line (CR-AIWS-2026-08-070).
CORE_FILENAME = "AIWS.md"
CORE_IMPORT_LINE = f"@.ai-work/{CORE_FILENAME}"
DEFAULT_MAX_BYTES = 32768  # Codex `project_doc_max_bytes` default

BEGIN_RE = re.compile(r"<!--\s*AIWS:BEGIN rules v=(?P<ver>\S+) target=(?P<target>\S+)\s*-->")
BEGIN_LOOSE = re.compile(r"<!--\s*AIWS:BEGIN rules\b[^>]*-->")
END_LITERAL = "<!-- AIWS:END rules -->"

# Headings a hand-written AIWS rules section is made of (used ONLY by --migrate-legacy to decide
# what to wrap). Anything not on this list is project-owned and stays outside the block.
LEGACY_HEADINGS = (
    "adopted canonical knowledge", "core concepts", "precedence", "hot operational rules",
    "aip stability rules", "execution protocol", "execution policy", "execution quick-start",
    "tooling & skills", "tooling & skills — pointers", "tooling — pointers", "tooling",
    "aiws knowledge sources", "aiws knowledge sources (installed)", "notes",
    "always-on safety rules", "always-on safety rules (every session)", "settings file rule",
    "environment", "project identity",
)
LEGACY_FINGERPRINT = "AI Work System MVP"


class ComposeError(Exception):
    """Anything that must stop the run with a clear message instead of a guess."""


# --------------------------------------------------------------------------- bytes / EOL helpers

class TextFile:
    """A target file as bytes + its surface conventions (BOM, EOL), so a rewrite can restore them."""

    def __init__(self, path: Path):
        self.path = path
        self.exists = path.exists()
        raw = path.read_bytes() if self.exists else b""
        self.bom = raw.startswith(b"\xef\xbb\xbf")
        body = raw[3:] if self.bom else raw
        self.crlf = b"\r\n" in body
        self.text = body.decode("utf-8").replace("\r\n", "\n")

    def encode(self, text: str) -> bytes:
        data = text.replace("\n", "\r\n") if self.crlf else text
        return (b"\xef\xbb\xbf" if self.bom else b"") + data.encode("utf-8")


def _backup(path: Path) -> Path:
    dst = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    n = 0
    while dst.exists():                      # same-second reruns must not clobber a backup
        n += 1
        dst = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}-{n}")
    dst.write_bytes(path.read_bytes())
    return dst


# --------------------------------------------------------------------------- block parsing

def split_block(text: str) -> "tuple[str, str, str] | None":
    """Return (before, block, after) or None when the file has no AIWS block.

    Raises ComposeError on a malformed marker — a half-written block is never repaired by guessing.
    """
    begins = list(BEGIN_LOOSE.finditer(text))
    ends = [m.start() for m in re.finditer(re.escape(END_LITERAL), text)]
    if not begins and not ends:
        return None
    if len(begins) != len(ends):
        raise ComposeError(
            f"malformed AIWS block: {len(begins)} BEGIN marker(s) vs {len(ends)} END marker(s). "
            "Fix the file by hand (or restore a .bak-* copy) — refusing to guess the boundary.")
    if len(begins) > 1:
        raise ComposeError(
            f"malformed AIWS block: {len(begins)} AIWS blocks in one file; exactly one is allowed.")
    b = begins[0]
    e = ends[0]
    if e < b.start():
        raise ComposeError("malformed AIWS block: END marker appears before BEGIN marker.")
    end_stop = e + len(END_LITERAL)
    return text[:b.start()], text[b.start():end_stop], text[end_stop:]


def block_version(block: str) -> "str | None":
    m = BEGIN_RE.search(block)
    return m.group("ver") if m else None


# --------------------------------------------------------------------------- sources

def resolve_version(root: Path) -> "tuple[str, str]":
    """(version, provenance). Two tiers, then hard failure — never a guess."""
    manifest = root / ".ai-work" / "install_templates" / "VERSION"
    if manifest.exists():
        meta, _ = parse_frontmatter(manifest.read_text(encoding="utf-8"))
        ver = str(meta.get("aiws_version", "")).strip()
        if ver:
            return ver, f"manifest {manifest.relative_to(root).as_posix()}"
        raise ComposeError(f"{manifest} has no `aiws_version` — refusing to guess a version.")
    pin = root / "product" / "aiws_version.md"
    if pin.exists():                          # source tree: it BUILDS packages, never installs one
        meta, _ = parse_frontmatter(pin.read_text(encoding="utf-8"))
        ver = str(meta.get("aiws_version", "")).strip()
        if ver:
            return f"{ver}-src", f"source-tree pin {pin.relative_to(root).as_posix()}"
        raise ComposeError(f"{pin} has no `aiws_version` — refusing to guess a version.")
    raise ComposeError(
        "no version source: neither .ai-work/install_templates/VERSION (installed target) nor "
        "product/aiws_version.md (source tree). Re-run the install/upgrade so the install_templates "
        "section — including its VERSION manifest — lands in the target. "
        "(.aiws-version is NOT a fallback: install and quick-install never write it.)")


def read_source(root: Path, name: str) -> str:
    p = root / ".ai-work" / "install_templates" / name
    if not p.exists():
        raise ComposeError(f"missing template: {p} — re-run install/upgrade for the "
                           "install_templates section.")
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def read_core(root: Path) -> str:
    p = root / ".ai-work" / CORE_FILENAME
    if not p.exists():
        raise ComposeError(f"missing core rules: {p} — copy install_templates/aiws_core_rules.md "
                           "there (install step) before composing.")
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def ensure_core(root: Path, apply: bool, warns: list) -> "str | None":
    """Materialise `.ai-work/AIWS.md` from `install_templates/aiws_core_rules.md` (CR-089 C2).

    INSTALLED TARGETS ONLY. The discriminator is the same one `resolve_version` already uses:
    an installed tree carries `install_templates/VERSION` (stamped at build); a source tree that
    BUILDS packages carries `product/aiws_version.md` instead. In the source repo `.ai-work/AIWS.md`
    is PROJECT-OWNED and deliberately unlike the shipped template (its own header says "do not sync
    the two") — touching it there would destroy content, so we never do.

    Why a tool does this at all. Only `quick_install_aiws.py` ever created this file, and that
    installer is deliberately not shipped, so the UPGRADE path had no way to refresh it: the core
    rules froze at install time while `install_templates/` kept being updated, and `--check` said OK
    because it compared against the same stale core (IR-2026-08-17 F2). A condition written in prose
    ("copy it yourself") is a condition that gets forgotten — that is CR-AIWS-2026-08-077's thesis,
    and this is a measured instance of it.

    Overwriting is safe by declaration, not by assumption: `install_guide.md` states the file is
    package-owned and that upgrade overwrites it; project-owned content lives OUTSIDE the AIWS block
    in each tool's rule file. Still never silent — a pre-existing file whose content differed is
    reported (DP-089-A + repo rule #3).

    Returns "created" / "refreshed" / None (nothing to do).
    """
    if not (root / ".ai-work" / "install_templates" / "VERSION").exists():
        return None                       # source tree — AIWS.md is project-owned here
    tpl = root / ".ai-work" / "install_templates" / "aiws_core_rules.md"
    if not tpl.exists():
        return None                       # read_source() raises the actionable error later
    core = root / ".ai-work" / CORE_FILENAME
    new = tpl.read_text(encoding="utf-8").replace("\r\n", "\n")
    if core.exists():
        if core.read_text(encoding="utf-8").replace("\r\n", "\n") == new:
            return None
        action = "refreshed"
        warns.append(
            f"{core} differed from the shipped install_templates/aiws_core_rules.md and was "
            f"{'refreshed' if apply else 'MARKED for refresh (dry-run)'}. The file is package-owned "
            "(install_guide: 'upgrade ghi đè'); project-owned rules belong OUTSIDE the AIWS block in "
            "each tool's rule file.")
    else:
        action = "created"
    if apply:
        core.parent.mkdir(parents=True, exist_ok=True)
        with core.open("w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print(f"  [{CORE_FILENAME}] core rules {action} from install_templates/aiws_core_rules.md")
    else:
        print(f"  [{CORE_FILENAME}] would be {action} from install_templates/aiws_core_rules.md "
              "(dry-run)")
    return action


def target_path(root: Path, tool: str, claude_file: str) -> Path:
    if tool == "claude":
        return root / claude_file
    if tool == "agents":
        return root / "AGENTS.md"
    return root / ".github" / "copilot-instructions.md"


# --------------------------------------------------------------------------- rendering

def render_block(root: Path, tool: str, version: str) -> str:
    adapter = read_source(root, f"adapter_{tool}.md").strip("\n")
    if tool == "claude":
        core_part = (
            "<!-- Core rules are imported, not inlined: Claude Code expands `@path` at launch. -->\n"
            f"{CORE_IMPORT_LINE}")
    else:
        core_part = read_core(root).strip("\n")
    return (
        f"<!-- AIWS:BEGIN rules v={version} target={tool} -->\n"
        f"AIWS rules {version} (target={tool}) — do not edit inside this block\n\n"
        f"{adapter}\n\n"
        f"{core_part}\n"
        f"{END_LITERAL}")


def render_identity(root: Path, tool: str, project_name: str, version: str, claude_file: str) -> str:
    title = {"claude": claude_file, "agents": "AGENTS.md",
             "copilot": ".github/copilot-instructions.md"}[tool]
    text = read_source(root, "project_identity.md")
    return (text.replace("<RULE_FILE_TITLE>", title)
                .replace("<PROJECT_NAME>", project_name)
                .replace("<AIWS_VERSION>", version)
                .replace("<YYYY-MM-DD>", time.strftime("%Y-%m-%d")))


# --------------------------------------------------------------------------- write path

def _emit_diff(path: Path, old: str, new: str) -> None:
    diff = list(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                     fromfile=f"a/{path.name}", tofile=f"b/{path.name}"))
    if not diff:
        print(f"  = {path}: no change")
        return
    print(f"  --- diff for {path} ---")
    for line in diff[:80]:
        print("  " + line.rstrip("\n"))
    if len(diff) > 80:
        print(f"  … {len(diff) - 80} more diff line(s)")


def write_file(tf: TextFile, new_text: str, *, apply: bool, max_bytes: int, tool: str,
               warns: list) -> None:
    """Write when --apply; always report. Self-verifies the bytes outside the AIWS block."""
    if new_text == tf.text:
        print(f"  = {tf.path}: already up to date")
        return
    if not apply:
        _emit_diff(tf.path, tf.text, new_text)
        print(f"  (dry-run) {tf.path} NOT written — pass --apply to write")
        return

    backup = _backup(tf.path) if tf.exists else None
    data = tf.encode(new_text)
    tf.path.parent.mkdir(parents=True, exist_ok=True)
    tf.path.write_bytes(data)

    # self-verify: everything outside the block must be byte-identical to what we intended
    written = TextFile(tf.path)
    try:
        got = split_block(written.text)
        want = split_block(new_text)
    except ComposeError as exc:               # pragma: no cover — defensive
        got = want = None
        warns.append(f"self-verify could not re-parse {tf.path}: {exc}")
    if got and want and (got[0], got[2]) != (want[0], want[2]):
        if backup:
            tf.path.write_bytes(backup.read_bytes())
            raise ComposeError(f"self-verify FAILED for {tf.path}: bytes outside the AIWS block "
                               f"changed; restored from {backup.name}.")
        raise ComposeError(f"self-verify FAILED for {tf.path}: bytes outside the AIWS block changed.")

    size = len(data)
    if tool == "agents" and size > max_bytes:
        warns.append(
            f"{tf.path} is {size} bytes (> {max_bytes}). Codex stops adding files once the combined "
            f"instruction chain reaches `project_doc_max_bytes` (default {DEFAULT_MAX_BYTES}), so this "
            "block can be dropped from context: slim the project-owned part or raise that setting.")
    print(f"  + {tf.path}: written ({size} bytes)" + (f", backup {backup.name}" if backup else ""))


# --------------------------------------------------------------------------- verbs

def do_init(root: Path, tools, version: str, args, warns: list) -> int:
    ensure_core(root, apply=bool(getattr(args, "apply", False)), warns=warns)
    for tool in tools:
        path = target_path(root, tool, args.claude_file)
        tf = TextFile(path)
        parsed = split_block(tf.text) if tf.exists else None
        if parsed is not None:
            raise ComposeError(f"{path} already carries an AIWS block — use --refresh to update it.")
        if tf.exists and tf.text.strip():
            if LEGACY_FINGERPRINT in tf.text:
                raise ComposeError(
                    f"{path} looks like a hand-written AIWS rules file (contains "
                    f"'{LEGACY_FINGERPRINT}') but has no AIWS block. Run --migrate-legacy to wrap the "
                    "existing rules instead of adding a second, conflicting copy.")
            if not args.append_existing:
                raise ComposeError(
                    f"{path} already exists and is not an AIWS file. Re-run with --append-existing "
                    "to append the AIWS block below its current content (HUMAN decision).")
            new_text = tf.text.rstrip("\n") + "\n\n" + render_block(root, tool, version) + "\n"
        else:
            identity = render_identity(root, tool, args.project_name, version, args.claude_file)
            new_text = identity.rstrip("\n") + "\n\n" + render_block(root, tool, version) + "\n"
        write_file(tf, new_text, apply=args.apply, max_bytes=args.max_bytes, tool=tool, warns=warns)
    return 0


def do_migrate(root: Path, tools, version: str, args, warns: list) -> int:
    for tool in tools:
        path = target_path(root, tool, args.claude_file)
        tf = TextFile(path)
        if not tf.exists:
            raise ComposeError(f"{path} does not exist — nothing to migrate (use --init).")
        if split_block(tf.text) is not None:
            raise ComposeError(f"{path} already carries an AIWS block — use --refresh.")

        lines = tf.text.split("\n")
        heads = [(i, ln[3:].strip().lower()) for i, ln in enumerate(lines) if ln.startswith("## ")]
        legacy_idx = [i for i, h in heads if _is_legacy_heading(h)]
        if not legacy_idx:
            raise ComposeError(
                f"{path}: cannot identify the AIWS section (no known AIWS heading found). "
                "Refusing to guess a boundary — move the AIWS rules out by hand, then run --init.")
        start = legacy_idx[0]
        head_pos = [i for i, _ in heads]
        end = len(lines)
        for i in head_pos:
            if i > legacy_idx[-1]:
                end = i
                break
        print(f"  · {path}: wrapping lines {start + 1}-{end} "
              f"({end - start} line(s)) into the AIWS block")
        new_text = ("\n".join(lines[:start]).rstrip("\n") + "\n\n"
                    + render_block(root, tool, version) + "\n"
                    + ("\n" + "\n".join(lines[end:]).lstrip("\n") if end < len(lines) else ""))
        write_file(tf, new_text, apply=args.apply, max_bytes=args.max_bytes, tool=tool, warns=warns)
    return 0


def _is_legacy_heading(h: str) -> bool:
    h = re.sub(r"^\d+[.)]\s*", "", h).strip()
    return any(h == k or h.startswith(k) for k in LEGACY_HEADINGS)


def _refresh_targets(root: Path, tools, args) -> list:
    """Paths to refresh. For `claude` WITHOUT an explicit --claude-file, both supported names are
    swept: a project that wired the team-shared CLAUDE.md would otherwise never be refreshed, because
    the default only names CLAUDE.local.md (`--check` already sweeps both — this keeps them honest).
    CR-AIWS-2026-08-070 apply."""
    out = []
    for tool in tools:
        if tool == "claude" and not args.claude_file_explicit:
            out += [(tool, root / name) for name in CLAUDE_FILES]
        else:
            out.append((tool, target_path(root, tool, args.claude_file)))
    return out


def do_refresh(root: Path, tools, version: str, args, warns: list) -> int:
    ensure_core(root, apply=bool(getattr(args, "apply", False)), warns=warns)
    touched = 0
    for tool, path in _refresh_targets(root, tools, args):
        tf = TextFile(path)
        if not tf.exists:
            if args.tools_explicit:
                raise ComposeError(f"{path} does not exist — nothing to refresh.")
            continue
        parsed = split_block(tf.text)
        if parsed is None:
            if args.tools_explicit:
                raise ComposeError(
                    f"{path} has no AIWS block. If it holds hand-written AIWS rules, run "
                    "--migrate-legacy; otherwise --init --append-existing. Refusing to guess.")
            warns.append(f"{path} has no AIWS block — skipped. Run --migrate-legacy (legacy rules) "
                         "or --init --append-existing.")
            continue
        before, block, after = parsed
        old_ver = block_version(block)
        if old_ver and old_ver != version:
            warns.append(f"{path}: block version {old_ver} != current {version} (drift) — refreshing.")
        fresh = render_block(root, tool, version)
        if old_ver == version and block.strip() != fresh.strip():
            warns.append(f"{path}: content inside the AIWS block differs from the current templates "
                         "— hand edits inside the block are overwritten by this refresh.")
        write_file(tf, before + fresh + after, apply=args.apply, max_bytes=args.max_bytes,
                   tool=tool, warns=warns)
        touched += 1
    if touched == 0 and not args.tools_explicit:
        print("  (no rule file with an AIWS block found)")
    return 0


def do_check(root: Path, version: str, args) -> int:
    """Verify every rule file against the manifest — version AND content.

    CR-AIWS-2026-08-081: this used to compare `block_version` only. The install checklist calls
    `--check` the way to verify a rule file, so "rc=0" was read as "your rule files are current" —
    but editing an adapter without re-running `--refresh --apply` leaves every rendered block stale
    with its version marker still matching, and this returned 0. `test_repo_rules_single_source`
    asserts exactly that rc, so nothing anywhere caught it.

    Not hypothetical: hours before this change, applying CR-AIWS-2026-08-077 C6 made AGENTS.md and
    copilot-instructions.md content-stale, `--refresh` warned about it, and `--check` still said OK.

    The comparison itself is not new — `do_refresh` has done `block.strip() != fresh.strip()` all
    along. This calls the SAME `render_block`, so there is one definition of "current", not two.
    Two states, reported apart (DP-081-A = a: both are rc≠0, both fixed by `--refresh --apply`;
    splitting the SEVERITY would only add a rule to remember, but splitting the LABEL tells the
    reader which thing went wrong).
    """
    rows, n_ver, n_stale = [], 0, 0
    seen = set()
    for tool in TOOLS:
        candidates = ([root / c for c in CLAUDE_FILES] if tool == "claude"
                      else [target_path(root, tool, args.claude_file)])
        for path in candidates:
            if not path.exists() or path in seen:
                continue
            seen.add(path)
            try:
                parsed = split_block(TextFile(path).text)
            except ComposeError as exc:
                rows.append((path, "MALFORMED", f"MALFORMED ({exc})"))
                n_ver += 1
                continue
            if parsed is None:
                continue
            ver = block_version(parsed[1]) or "?"
            if ver != version:
                rows.append((path, "BAD", ver))
                n_ver += 1
                continue
            # Version agrees — now ask the question the old check never asked.
            try:
                fresh = render_block(root, tool, version)
            except Exception as exc:                      # noqa: BLE001 - report, never crash --check
                rows.append((path, "UNRENDERABLE", f"{ver} ({exc})"))
                n_ver += 1
                continue
            if parsed[1].strip() != fresh.strip():
                rows.append((path, "STALE", ver))
                n_stale += 1
            else:
                rows.append((path, "OK", ver))
    if not rows:
        print("check: no rule file carries an AIWS block")
        return 0
    print(f"check: manifest version = {version}")
    for path, state, detail in rows:
        print(f"  {state:<12}  {path}  →  {detail}")
    if n_ver or n_stale:
        print(f"check: FAILED — {n_ver} version mismatch/malformed, {n_stale} content-stale "
              f"(block differs from a fresh render of the current templates). "
              f"Both are fixed by: compose_aiws_rules.py --refresh --apply "
              f"(CR-AIWS-2026-08-081)", file=sys.stderr)
        return 2
    return 0


# --------------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render AIWS rules into per-tool rule files.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--init", action="store_true", help="create rule files (identity + AIWS block)")
    mode.add_argument("--refresh", action="store_true", help="replace the AIWS block (dry-run default)")
    mode.add_argument("--migrate-legacy", action="store_true", dest="migrate_legacy",
                      help="wrap a hand-written AIWS section into the block")
    mode.add_argument("--check", action="store_true", help="report block versions; non-zero on drift")
    ap.add_argument("--tools", default="", help="comma list: claude,agents,copilot")
    ap.add_argument("--claude-file", default=CLAUDE_FILES[0], choices=CLAUDE_FILES,
                    help="which Claude rule file to write (default: CLAUDE.local.md)")
    ap.add_argument("--project-name", default="<PROJECT_NAME>")
    ap.add_argument("--target-root", default=None, help="project root (default: detected)")
    ap.add_argument("--apply", action="store_true", help="actually write (default: dry-run)")
    ap.add_argument("--append-existing", action="store_true", dest="append_existing",
                    help="append the block to a pre-existing non-AIWS file (HUMAN decision)")
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                    help=f"size-guard for the agents target (default {DEFAULT_MAX_BYTES})")
    args = ap.parse_args(argv)

    root = Path(args.target_root).resolve() if args.target_root else find_ai_work_root(Path.cwd())
    args.tools_explicit = bool(args.tools)
    args.claude_file_explicit = any(a.startswith("--claude-file") for a in (argv or sys.argv[1:]))
    tools = [t.strip() for t in args.tools.split(",") if t.strip()] or list(TOOLS)
    unknown = [t for t in tools if t not in TOOLS]
    if unknown:
        print(f"error: unknown tool(s): {', '.join(unknown)} (valid: {', '.join(TOOLS)})",
              file=sys.stderr)
        return 2

    warns: list = []
    try:
        version, provenance = resolve_version(root)
        print(f"aiws rules: version {version} (from {provenance}), root {root}")
        if args.check:
            rc = do_check(root, version, args)
        elif args.init:
            rc = do_init(root, tools, version, args, warns)
        elif args.migrate_legacy:
            rc = do_migrate(root, tools, version, args, warns)
        else:
            rc = do_refresh(root, tools, version, args, warns)
    except ComposeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for w in warns:
        print(f"WARN: {w}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
