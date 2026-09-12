#!/usr/bin/env python3
"""project_profile.py — create, check and complete `.ai-work/project_profile.yml`.

CR-AIWS-2026-08-128 C2. Modelled on `account_id.py`: one small tool per config file, callable by the
install skill, runnable by a HUMAN, importable by a linter.

    py .ai-work/tooling/project_profile.py init                 # seed it if absent; never overwrite
    py .ai-work/tooling/project_profile.py check                # what is missing / inconsistent
    py .ai-work/tooling/project_profile.py refresh              # show what would be added (dry run)
    py .ai-work/tooling/project_profile.py refresh --apply      # add the missing keys

WHY THIS TOOL EXISTS. `project_profile.yml` was a file only the AIWS repo had: not shipped, seeded by
no installer, and absent in both real downstream installs — so every adopting project ran on
absent-file defaults with no way to discover the surface existed. The HUMAN ruled on 2026-08-27 that
each project gets one, that install creates it blank when absent, and that an incomplete file is
completed **by asking rather than by guessing**.

TWO CONTRACTS THIS TOOL WILL NOT BREAK.

1. It never rewrites what it did not write. All edits go through `_common.profile_upsert`, which is
   line-addressed: it replaces the one line it means to and leaves every other byte alone. Parsing this
   file and dumping it back would collapse it — measured on the AIWS repo's own profile, 2470 B -> 124 B,
   taking all 30 comment lines with it. Those comments are where the reasons live.

2. "Asking" never means `input()`. Install runs in CI, inside agent runs, and in tool calls where stdin
   is closed. So `check` and `refresh` print exactly what is missing, name the command that supplies it,
   and exit non-zero — the same halt-and-ask contract `lookup_wiki_source.py` uses for `--system`.

`set-mode` is deliberately NOT a verb here: `switch_system_mode.py` keeps it. That tool is in
PAYLOAD_EXCLUDES and two tests assert the exclusion, so folding it into this (shipped) tool would have
been a silent ship-set change.

stdlib only; UTF-8; cp932-safe stdout.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    PROJECT_PROFILE_SCHEMA,
    PROJECT_PROFILE_SCHEMA_VERSION,
    ProjectProfileUnreadable,
    find_ai_work_root,
    profile_upsert,
    project_profile_report,
    read_project_config,
)

PROFILE_NAME = "project_profile.yml"
TEMPLATE_NAME = "project_profile.template.yml"


def _out() -> None:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def _ai_work(explicit: "str | None") -> Path:
    if explicit:
        return Path(explicit).resolve()
    return find_ai_work_root(Path.cwd()) / ".ai-work"


def _template(ai_work: Path) -> "Path | None":
    """The shipped skeleton, if this install received one.

    Looked up in the installed tree first, then in the source tree, so the tool works both in an
    adopting project and in the AIWS repo that builds the package.
    """
    for cand in (ai_work / "install_templates" / TEMPLATE_NAME,
                 ai_work.parent / "product" / "install_templates" / TEMPLATE_NAME):
        if cand.is_file():
            return cand
    return None


def _missing_required(cfg: dict) -> "list[tuple[str, str]]":
    """[(key, why it matters)] for required keys that are absent."""
    out = []
    for key, spec in PROJECT_PROFILE_SCHEMA.items():
        required = spec.get("required", False)
        iff = spec.get("required_iff")
        if iff and cfg.get(iff):
            required = True
        if required and key not in cfg["_present"]:
            out.append((key, spec.get("doc", "")))
    return out


def cmd_init(ns) -> int:
    ai_work = _ai_work(ns.ai_work)
    dest = ai_work / PROFILE_NAME
    if dest.exists():
        print(f"[OK] {dest} already exists — not overwritten.")
        print("     Run `project_profile.py check` to see whether it is complete.")
        return 0
    tpl = _template(ai_work)
    if tpl is None:
        print("error: no shipped skeleton found "
              f"({ai_work}/install_templates/{TEMPLATE_NAME}).\n"
              "       This install predates the template, or the payload was not copied. "
              "Re-run the install, or copy the file from the package.", file=sys.stderr)
        return 2
    ai_work.mkdir(parents=True, exist_ok=True)
    # byte copy: the skeleton's comments are the documentation, and re-rendering would lose them
    dest.write_bytes(tpl.read_bytes())
    print(f"[OK] seeded {dest} from the shipped skeleton.")
    print("     It is yours to edit. AIWS only touches the AIWS:BEGIN block.")
    return 0


def _load(ai_work: Path) -> "tuple[dict | None, int]":
    dest = ai_work / PROFILE_NAME
    if not dest.exists():
        print(f"error: {dest} does not exist.\n"
              f"       Create it:  py .ai-work/tooling/project_profile.py init", file=sys.stderr)
        return None, 2
    try:
        return read_project_config(ai_work), 0
    except ProjectProfileUnreadable as e:
        # ABSENT and UNPARSEABLE are different facts (C3). A damaged profile used to read as a healthy
        # single-system project, which is how a guard goes quiet without anyone noticing.
        print(f"error: {dest} exists but could not be parsed.\n       {e}\n"
              "       Fix the file by hand — this tool will not rewrite a file it cannot read.",
              file=sys.stderr)
        return None, 2


def cmd_check(ns) -> int:
    ai_work = _ai_work(ns.ai_work)
    cfg, rc = _load(ai_work)
    if cfg is None:
        return rc

    missing = _missing_required(cfg)
    violations = project_profile_report(cfg)

    if not missing and not violations:
        print(f"[OK] {ai_work / PROFILE_NAME} is complete "
              f"(schema v{cfg.get('schema_version') or PROJECT_PROFILE_SCHEMA_VERSION}).")
        return 0

    # "Complete" is keys AND invariants (HUMAN ruling 2026-08-27). A file can carry every required key
    # and still be broken: `systems: []` under `multi_system: true` is exactly that shape, and it is the
    # shape that used to accept any system id.
    print(f"INCOMPLETE: {ai_work / PROFILE_NAME}")
    for key, why in missing:
        print(f"  missing key   {key:20s} {why}")
    for code, msg, guard in violations:
        print(f"  broken rule   {code:20s} {msg}")
        print(f"  {'':32s}protects: {guard}")
    print("\nSupply them by editing the file, then re-run `check`.")
    print("To add only the MISSING KEYS with their defaults (never touching your own lines):")
    print("    py .ai-work/tooling/project_profile.py refresh          # dry run")
    print("    py .ai-work/tooling/project_profile.py refresh --apply")
    print("A broken rule is a decision, not a default — this tool will not guess it for you.")
    return 1


def cmd_refresh(ns) -> int:
    ai_work = _ai_work(ns.ai_work)
    cfg, rc = _load(ai_work)
    if cfg is None:
        return rc

    dest = ai_work / PROFILE_NAME
    additions = {k: spec["default"] for k, spec in PROJECT_PROFILE_SCHEMA.items()
                 if k not in cfg["_present"]}
    if cfg.get("schema_version") != PROJECT_PROFILE_SCHEMA_VERSION:
        additions["schema_version"] = PROJECT_PROFILE_SCHEMA_VERSION

    if not additions:
        print(f"[OK] {dest} already carries every schema key (v{PROJECT_PROFILE_SCHEMA_VERSION}).")
        violations = project_profile_report(cfg)
        if violations:
            print("     But it is still INCOMPLETE — see `check`; the broken rules are decisions "
                  "this tool will not make for you.")
            return 1
        return 0

    if not ns.apply:
        print(f"DRY RUN — {dest} would gain, inside the AIWS:BEGIN block:")
        for k, v in additions.items():
            print(f"  + {k}: {'true' if v is True else 'false' if v is False else v}")
        print("\nNothing outside that block is touched — your keys and comments are left exactly as "
              "they are.\nRe-run with --apply to write.")
        return 0

    before = dest.read_bytes()
    changed = profile_upsert(dest, additions)
    after = dest.read_bytes()
    b_lines = before.decode("utf-8", "replace").splitlines()
    a_lines = after.decode("utf-8", "replace").splitlines()
    removed = [l for l in b_lines if l not in a_lines]
    # A refresh that deletes a line is a bug, not a refresh. Say so loudly rather than quietly.
    if removed:
        print(f"error: refresh removed {len(removed)} line(s) — this must never happen. "
              "The file has been left as written; inspect it with `git diff` immediately.",
              file=sys.stderr)
        for l in removed[:5]:
            print(f"  -{l}", file=sys.stderr)
        return 3
    print(f"[OK] {dest}: added {', '.join(changed)}")
    print(f"     lines removed: 0 · comment lines preserved: "
          f"{sum(1 for l in b_lines if l.strip().startswith('#'))} -> "
          f"{sum(1 for l in a_lines if l.strip().startswith('#'))}")
    return 0


def main() -> int:
    _out()
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ai-work", help="path to .ai-work (default: found by walking up from CWD)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="seed the profile from the shipped skeleton if absent")
    sub.add_parser("check", help="report missing keys and broken invariants; non-zero if incomplete")
    r = sub.add_parser("refresh", help="add missing schema keys inside the AIWS block")
    r.add_argument("--apply", action="store_true", help="write (default is a dry run)")
    ns = p.parse_args()
    return {"init": cmd_init, "check": cmd_check, "refresh": cmd_refresh}[ns.cmd](ns)


if __name__ == "__main__":
    raise SystemExit(main())
