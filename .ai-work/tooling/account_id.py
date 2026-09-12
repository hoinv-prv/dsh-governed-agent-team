#!/usr/bin/env python3
"""Provision the local AIWS account_id + account_info.yaml — CR-AIWS-2026-06-016.

`account_info.yaml` (gitignored, one per install) carries `account_id` + the per-member
`next_aip_id` counter that allocate_aip_id.py consumes (CR-015 v2). This tool sets/validates it.
AI NEVER invents an account_id — `set` requires an explicit `--account-id` from the HUMAN.

Subcommands:
  get                     print the current account_id (error if unset)
  set --account-id <id>   validate (dir-safe) + write account_info.yaml (preserve existing
                          next_aip_id, else seed from disk-max+1) + ensure .gitignore ignores it
  validate [--repair]     check account_id (dir-safe) + next_aip_id (exec/plan/local present);
                          --repair re-seeds a missing/partial counter from disk-max+1 (OP-4)
  resolve                 non-interactive resolve for CI / fresh clone / worktree, per the Approved
                          Deviation in AI_WORK_CONTRACT §6 (2026-08-17, CR-AIWS-2026-08-076):
                          file -> env AIWS_ACCOUNT_ID -> single AIP namespace -> STOP.
                          A value NOT read from the file is written with `provisional: true`.

stdlib-only; UTF-8 (cp932-safe).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, parse_frontmatter, write_text  # noqa: E402
from allocate_aip_id import _account_info_path, _disk_max  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

ACCOUNT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")   # dir-safe (OP-2)
_KINDS = ("exec", "plan", "local")
_HEADER = (
    "# AIWS local member identity + AIP id counter — CR-AIWS-2026-06-015 v2 / CR-AIWS-2026-06-016.\n"
    "# LOCAL FILE: gitignored, never committed. account_id + per-member NEXT AIP number per kind.\n"
)


# CR-AIWS-2026-08-076 C2 — non-account directories under .ai-work/aip/. Reuses the set already
# defined in check_aiws_upgrade.py rather than inventing a second one: two hand-kept lists of
# "which dirs are not accounts" would drift, and this one decides whether a namespace is
# UNAMBIGUOUS — the exact condition the §6 deviation is scoped to.
_AIP_NON_ACCOUNT_DIRS = {"exec", "plans", "local", "templates"}

_ENV_ACCOUNT = "AIWS_ACCOUNT_ID"


def _aip_namespaces(ai_work: Path) -> "list[str]":
    """Account-shaped directories under .ai-work/aip/ (CR-AIWS-2026-08-076 C2)."""
    root = ai_work / "aip"
    if not root.is_dir():
        return []
    return sorted(d.name for d in root.iterdir()
                  if d.is_dir() and not d.name.startswith(".")
                  and d.name not in _AIP_NON_ACCOUNT_DIRS)


def resolve_account_id(ai_work: Path, env: "dict | None" = None) -> "tuple[str, str, str]":
    """Ordered, non-interactive resolve. Returns `(account_id, source, problem)`.

    `source` ∈ {"file", "env", "namespace", ""} · `problem` is "" on success, else a message
    explaining why the caller must STOP and ask a HUMAN.

    Order is fixed by the Approved Deviation in AI_WORK_CONTRACT §6 (2026-08-17,
    CR-AIWS-2026-08-076 DP-076-A = a) and this function is the only place it exists:

      1. account_info.yaml            — unchanged behaviour, the HUMAN-declared value
      2. env AIWS_ACCOUNT_ID          — declared by whoever set up the CI/worktree
      3. exactly ONE AIP namespace    — inferable without guessing
      4. anything else                — STOP. 0 namespaces means nothing to infer from; 2+ means a
                                        choice, and choosing here would silently attach an AIP (and
                                        its workspace) to the wrong person. `account_id` IS the
                                        provenance of an AIP id — never guess it.

    Ambiguity is NOT resolved by "most recently modified" or "most files": a rule like that returns
    an answer for every input, which is precisely how a wrong owner would get recorded with no
    signal that anything was decided.
    """
    env = dict(os.environ if env is None else env)

    aid = str(_read(ai_work).get("account_id", "")).strip()
    if aid:
        return (aid, "file", "")

    raw = str(env.get(_ENV_ACCOUNT, "")).strip().lower()
    if raw:
        if not ACCOUNT_ID_RE.match(raw):
            return ("", "", f"{_ENV_ACCOUNT}={raw!r} is not dir-safe "
                            f"(pattern {ACCOUNT_ID_RE.pattern}) — refusing to use it")
        return (raw, "env", "")

    names = _aip_namespaces(ai_work)
    if len(names) == 1:
        return (names[0], "namespace", "")
    if not names:
        return ("", "", "no account_info.yaml, no " + _ENV_ACCOUNT + ", and no AIP namespace under "
                        ".ai-work/aip/ to infer from — a HUMAN must run "
                        "`account_id.py set --account-id <id>`")
    return ("", "", f"no account_info.yaml, no {_ENV_ACCOUNT}, and .ai-work/aip/ holds "
                    f"{len(names)} namespaces {names} — ambiguous, so this STOPS rather than "
                    f"picking one. Set {_ENV_ACCOUNT}, or run "
                    f"`account_id.py set --account-id <id>` (AI_WORK_CONTRACT §6, 2026-08-17)")


def _read(ai_work: Path) -> dict:
    p = _account_info_path(ai_work)
    if not p.exists():
        return {}
    meta, _ = parse_frontmatter("---\n" + p.read_text(encoding="utf-8") + "\n---\n")
    return meta or {}


def _seed_counter(ai_work: Path, account_id: str, existing: dict) -> dict:
    nxt = existing.get("next_aip_id")
    nxt = nxt if isinstance(nxt, dict) else {}
    out = {}
    for kind in _KINDS:
        if str(nxt.get(kind, "")).strip().isdigit():
            out[kind] = int(nxt[kind])
        else:
            out[kind] = _disk_max(ai_work, account_id, kind) + 1   # re-seed from disk (OP-4)
    return out


def _write(ai_work: Path, account_id: str, counter: dict, provisional: str = "") -> None:
    """CR-AIWS-2026-08-076 C2 — `provisional` names the source ("env"/"namespace") when the id was
    NOT declared by a HUMAN. It is written into the file so every later reader sees it: an inferred
    id that looks identical to a declared one is the failure this marker exists to prevent."""
    body = _HEADER
    if provisional:
        body += ("# PROVISIONAL: account_id below was resolved from " + provisional
                 + ", not declared by a HUMAN (AI_WORK_CONTRACT §6, 2026-08-17).\n"
                 "# Ratify with: py .ai-work/tooling/account_id.py set --account-id <id>\n")
    body += f"account_id: {account_id}\n"
    if provisional:
        body += f"provisional: true\nprovisional_source: {provisional}\n"
    body += "next_aip_id:\n"
    for kind in _KINDS:
        body += f"  {kind}: {counter[kind]}\n"
    write_text(_account_info_path(ai_work), body)


def _ensure_gitignore(ai_work: Path) -> bool:
    gi = ai_work.parent / ".gitignore"
    line = ".ai-work/account_info.yaml"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if line in existing:
        return False
    # CR-AIWS-2026-08-101 C3 — .gitignore là file của DỰ ÁN ADOPTER, không phải artifact AIWS:
    # bám EOL đang có của nó, không chuẩn hoá (DP-101-C = a). Text-mode không khai `newline=` sẽ
    # dịch "\n" thành CRLF trên Windows và làm lẫn EOL nếu file đang là LF.
    eol = "\r\n" if (gi.exists() and b"\r\n" in gi.read_bytes()) else "\n"
    with open(gi, "a", encoding="utf-8", newline="") as f:
        if existing and not existing.endswith("\n"):
            f.write(eol)
        f.write(f"{eol}# AIWS local identity (CR-AIWS-2026-06-016) — never commit{eol}{line}{eol}")
    return True


def cmd_get(ns: argparse.Namespace, ai_work: Path) -> int:
    aid = str(_read(ai_work).get("account_id", "")).strip()
    if not aid:
        print("error: account_id not set (run: account_id.py set --account-id <id>)", file=sys.stderr)
        return 2
    print(aid)
    return 0


def cmd_set(ns: argparse.Namespace, ai_work: Path) -> int:
    aid = ns.account_id.strip().lower()
    if not ACCOUNT_ID_RE.match(aid):
        print(f"error: account_id {ns.account_id!r} not dir-safe; allowed pattern: {ACCOUNT_ID_RE.pattern}",
              file=sys.stderr)
        return 2
    counter = _seed_counter(ai_work, aid, _read(ai_work))
    _write(ai_work, aid, counter)
    gi = _ensure_gitignore(ai_work)
    print(f"set account_id: {aid}; next_aip_id={counter}" + ("; .gitignore updated" if gi else ""))
    return 0


def cmd_resolve(ns: argparse.Namespace, ai_work: Path) -> int:
    """CR-AIWS-2026-08-076 C2 — resolve for a non-interactive environment and materialise the file.

    Writing the file (rather than just printing) is deliberate: allocate_aip_id.py's precondition is
    that account_info.yaml EXISTS and it never invents an id. Materialising a file that is visibly
    marked provisional keeps that precondition intact and keeps the allocator unchanged — the
    "inferred" fact travels in the artifact instead of in a second code path.
    """
    aid, source, problem = resolve_account_id(ai_work)
    if problem:
        print("error: " + problem, file=sys.stderr)
        return 2
    if source == "file":
        meta = _read(ai_work)
        prov = str(meta.get("provisional", "")).strip().lower() in ("true", "yes", "1")
        print(aid + ("  (provisional — needs ratify)" if prov else ""))
        return 0
    if ns.dry_run:
        print(f"(dry-run) would resolve account_id={aid} from {source} and mark it provisional")
        return 0
    counter = _seed_counter(ai_work, aid, _read(ai_work))
    _write(ai_work, aid, counter, provisional=source)
    _ensure_gitignore(ai_work)
    print(f"resolved account_id: {aid} (from {source}) — written PROVISIONAL. "
          f"Ratify with: account_id.py set --account-id {aid}")
    return 0


def cmd_validate(ns: argparse.Namespace, ai_work: Path) -> int:
    p = _account_info_path(ai_work)
    if not p.exists():
        print(f"error: {p} missing (run: account_id.py set --account-id <id>)", file=sys.stderr)
        return 2
    info = _read(ai_work)
    aid = str(info.get("account_id", "")).strip()
    problems = []
    if not ACCOUNT_ID_RE.match(aid):
        problems.append(f"account_id {aid!r} missing/not dir-safe")
    nxt = info.get("next_aip_id")
    if not isinstance(nxt, dict) or any(not str(nxt.get(k, "")).strip().isdigit() for k in _KINDS):
        problems.append("next_aip_id missing/partial (need exec/plan/local)")
    if problems and ns.repair and aid and ACCOUNT_ID_RE.match(aid):
        counter = _seed_counter(ai_work, aid, info)
        _write(ai_work, aid, counter)
        print(f"repaired: next_aip_id re-seeded from disk = {counter}")
        return 0
    if problems:
        for pr in problems:
            print(f"  - {pr}", file=sys.stderr)
        print("validate FAILED (use --repair to re-seed next_aip_id)", file=sys.stderr)
        return 1
    print(f"account_info.yaml OK: account_id={aid} next_aip_id={nxt}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Provision AIWS account_id (CR-AIWS-2026-06-016)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("get", help="print the current account_id")
    s = sub.add_parser("set", help="set account_id (write account_info.yaml + .gitignore)")
    s.add_argument("--account-id", required=True, help="dir-safe id; normalized lowercase")
    r = sub.add_parser("resolve", help="non-interactive resolve (CI/fresh clone) — "
                                       "file > env AIWS_ACCOUNT_ID > single AIP namespace > STOP")
    r.add_argument("--dry-run", action="store_true", help="report the resolution, write nothing")
    v = sub.add_parser("validate", help="validate account_info.yaml")
    v.add_argument("--repair", action="store_true", help="re-seed a missing/partial next_aip_id from disk")
    ns = ap.parse_args()
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    return {"get": cmd_get, "set": cmd_set, "validate": cmd_validate,
            "resolve": cmd_resolve}[ns.cmd](ns, ai_work)


if __name__ == "__main__":
    raise SystemExit(main())
