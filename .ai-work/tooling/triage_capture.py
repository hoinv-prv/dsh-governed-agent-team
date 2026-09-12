#!/usr/bin/env python3
"""Capture triage: the close sweep, `defer`, and the one-time `migrate` (CR-AIWS-2026-08-125 C3).

Until now a capture had exactly one end state that anyone reached: it stayed `captured` in a workspace
that was then archived. Measured across three projects at draft time: **385** rows still `captured`, and
**76** marked `deferred` of which **0** named a destination. The habit of explaining exists; the
destination does not.

This module gives "later" a real address. A deferred capture leaves the workspace — which is gitignored
and gets archived — and lands in a git-tracked, per-account backlog file as a **self-contained** row. The
workspace row is rewritten once to `deferred` + `deferred_to` and is frozen thereafter; the backlog row is
the live one. Two live copies would reproduce a failure this project has already paid for once, where a
merge that was also an apply left two records disagreeing about the same status.

What this module deliberately does NOT do:

* It does not promote anything. Promotion stays HUMAN-gated, everywhere, always.
* It does not move `captured` rows. `deferred` is a decision that lacks a destination, so moving it is
  lossless; `captured` is *undecided*, and moving it would launder "never triaged" into "consciously
  deferred" — making the data lie about its own history and the backlog count useless as a measure.
* It never invents a `defer_reason`. A deferral with no reason is the thing being replaced.

Verbs:
  sweep    --workspace <ws>                       list rows still `captured` (what `run close` blocks on)
  defer    --workspace <ws> --cap CAP-ID --reason "…"   one row → backlog (idempotent)
  migrate  [--dry-run]                            existing `deferred` rows → backlog, repo-wide
  list     [--account ID] [--status open]         show the backlog
  resolve  --backlog-id BL-… --disposition-ref X  close a backlog row

Usage:
  py triage_capture.py sweep   --workspace .ai-work/workspaces/hoinv/TASK-...
  py triage_capture.py defer   --workspace .ai-work/workspaces/hoinv/TASK-... --cap CAP-001 --reason "..."
  py triage_capture.py migrate --dry-run
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CAPTURE_BACKLOG_README,
    capture_backlog_dir,
    capture_backlog_path,
    find_ai_work_root,
    portable_locator,
    read_account_id,
    read_jsonl,
    read_text,
)

def _force_utf8_stdio() -> None:
    """cp932-safe stdout on Windows, WITHOUT stealing a wrapper an importer already installed.

    Re-wrapping unconditionally closes the previous wrapper's buffer when it is collected, which turns
    any importing test into `ValueError: I/O operation on closed file`. This module is a library first
    and a CLI second, so it only wraps a stream that is not already UTF-8.
    """
    for name in ("stdout", "stderr"):
        s = getattr(sys, name, None)
        if s is None or not hasattr(s, "buffer"):
            continue
        if (getattr(s, "encoding", "") or "").lower().replace("-", "") == "utf8":
            continue
        try:
            setattr(sys, name, io.TextIOWrapper(s.buffer, encoding="utf-8", errors="replace"))
        except Exception:
            pass


_force_utf8_stdio()

CAPTURE_FILE = "08_capture_inbox.jsonl"
NEEDS_TRIAGE = "captured"
DEFERRED = "deferred"
BACKLOG_STATUSES = ("open", "triaged", "promoted", "discarded")

_WS_NAME_RE = re.compile(r"^TASK-\d{8}-([A-Za-z]+)-(\d+)$")
_AIP_NUM_RE = re.compile(r"AIP-[A-Za-z]+-(\d+)")


# ---------------------------------------------------------------- ids and locators


def aip_id_from_workspace_name(name: str) -> str:
    """`TASK-YYYYMMDD-<kind>-NNNN` -> `AIP-<KIND>-NNNN`, else "" (CR-AIWS-2026-08-125 C4)."""
    m = _WS_NAME_RE.match(name.strip())
    return f"AIP-{m.group(1).upper()}-{m.group(2)}" if m else ""


def backlog_id_for(aip_id: str, cap_id: str) -> str:
    """`BL-<aip-number>-<cap_id>` — DERIVED, never allocated.

    Deriving it is what makes `defer` idempotent and makes two concurrent sessions unable to mint the
    same id for different rows. No allocator is involved, which sidesteps the scanner-is-not-a-claim
    hazard this project has already been bitten by: a scan of existing ids tells you what exists, not
    what someone else is about to write.
    """
    m = _AIP_NUM_RE.search(aip_id or "")
    stem = m.group(1) if m else (aip_id or "NOAIP").replace("-", "")
    return f"BL-{stem}-{cap_id}"


def _workspace_origin(ws: Path, ai_work: Path) -> "tuple[str, str]":
    """(aip_id, task_id) for a workspace, via the back-link then the folder-name fallback."""
    task_id = ws.name
    ptr = ws / ".current_step.json"
    if ptr.exists():
        try:
            aid = str(json.loads(read_text(ptr)).get("aip_id", "") or "")
            if aid:
                return aid, task_id
        except Exception:
            pass
    return aip_id_from_workspace_name(task_id), task_id


# ---------------------------------------------------------------- backlog store


def _ensure_backlog_dir(ai_work: Path) -> Path:
    """Create the store on demand and seed its README beside it on first use."""
    d = capture_backlog_dir(ai_work)
    d.mkdir(parents=True, exist_ok=True)
    readme = d / "README.md"
    if not readme.exists():
        with io.open(readme, "w", encoding="utf-8", newline="\n") as f:
            f.write(CAPTURE_BACKLOG_README)
    return d


PROMOTION_LOG_NAME = "_promotion_log.jsonl"


def append_promotion_log(ai_work: Path, entry: dict) -> Path:
    """Append one line to `.ai-work/capture_backlog/_promotion_log.jsonl` (CR-AIWS-2026-08-126 C5).

    Records what a row BECAME - and, crucially, also records REFUSALS, with the gate and the reason.
    Without the refusals the log answers "what got promoted" but not "what the pipeline rejected and
    why", and the second question is the one that says whether the taxonomy is working. Precedent: a
    deployed COBOL-migration install keeps exactly such a log, and its single row is a
    `promotion_gate_hard_stop`.

    Never raises: a logging failure must not fail the disposition it is recording.
    """
    d = _ensure_backlog_dir(ai_work)
    p = d / PROMOTION_LOG_NAME
    try:
        line = json.dumps(entry, ensure_ascii=False)
        json.loads(line)
        with io.open(p, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
    except Exception as e:                                   # noqa: BLE001
        print(f"warn: could not write the promotion log: {e}", file=sys.stderr)
    return p


def read_promotion_log(ai_work: Path) -> "list[dict]":
    p = capture_backlog_dir(ai_work) / PROMOTION_LOG_NAME
    return read_jsonl(p) if p.exists() else []


def read_backlog(ai_work: Path, account_id: str = "") -> "list[dict]":
    p = capture_backlog_path(ai_work, account_id)
    return read_jsonl(p) if p.exists() else []


def _append_backlog(ai_work: Path, rec: dict, account_id: str = "") -> Path:
    _ensure_backlog_dir(ai_work)
    p = capture_backlog_path(ai_work, account_id)
    line = json.dumps(rec, ensure_ascii=False)
    json.loads(line)                                    # re-parse before writing (as append_capture does)
    with io.open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    return p


def backlog_record(cap: dict, *, aip_id: str, task_id: str, ws: Path, project_root: Path,
                   reason: str, account_id: str, when: str) -> dict:
    """Build the self-contained backlog row for one capture.

    Self-contained on purpose: the workspace it came from is gitignored and will be archived, so a row
    that merely pointed at it would rot into an unresolvable reference.
    """
    cap_id = str(cap.get("id", "") or "")
    return {
        "backlog_id": backlog_id_for(aip_id, cap_id),
        "origin": {
            "aip_id": aip_id,
            "task_id": task_id,
            "workspace": portable_locator(ws, project_root),
            "cap_id": cap_id,
        },
        "type": cap.get("type", ""),
        "title": cap.get("title", ""),
        "content": cap.get("content", ""),
        "candidate_kind": cap.get("candidate_kind", ""),
        "suggested_target": cap.get("suggested_target", ""),
        "knowledge_value": cap.get("knowledge_value", ""),
        # AIP-EXEC-1135: `improvement_scope` used to be dropped here. The consumer map in
        # capture_and_triage_rules.md routes on `candidate_kind` + `improvement_scope`, and the field
        # was empty on 171/171 open backlog rows — which reads as "nobody fills it in" and was in fact
        # "the pipe does not carry it": this dict copies an explicit field list, and the field was not
        # on it. COPY, never derive: deriving from the kind is `append_capture`'s job at WRITE time
        # (`resolve_improvement_scope`); inventing a value here would be indistinguishable from one a
        # human chose, and triage routes on it.
        "improvement_scope": cap.get("improvement_scope", ""),
        "discovered_at": cap.get("discovered_at", ""),
        "step": cap.get("step", ""),
        "source_refs": cap.get("source_refs", []) or [],
        "reusable": bool(cap.get("reusable", False)),
        "deferred_at": when,
        "deferred_by": account_id,
        "defer_reason": reason,
        "review_by": "",
        "status": "open",
        "resolution": {},
    }


# ---------------------------------------------------------------- inbox rewrite


def _rewrite_inbox(inbox: Path, records: "list[dict]") -> None:
    """Rule 7 + Rule 11: build the whole file, assert it is not empty, then write it once.

    A `.bak` is written beside the inbox before the first rewrite. Workspaces are gitignored, so git is
    not a safety net here — that is exactly why the backup is unconditional rather than a nicety.
    """
    assert records, "refusing to write an empty inbox"
    lines = []
    for r in records:
        line = json.dumps(r, ensure_ascii=False)
        json.loads(line)
        lines.append(line)
    bak = inbox.with_suffix(inbox.suffix + ".bak")
    if not bak.exists():
        bak.write_bytes(inbox.read_bytes())
    with io.open(inbox, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- verbs


def sweep(ws: Path) -> "list[dict]":
    """Rows still `captured` — what `run close` refuses to flip past."""
    inbox = ws / CAPTURE_FILE
    if not inbox.exists():
        return []
    return [r for r in read_jsonl(inbox) if r.get("status") == NEEDS_TRIAGE]


def defer(ws: Path, cap_id: str, reason: str, *, ai_work: Path, account_id: str = "",
          when: str = "") -> "tuple[str, bool]":
    """Move one capture to the backlog. Returns (backlog_id, wrote_anything).

    Idempotent by construction: the id is derived, so a second call finds the row already present and
    changes nothing rather than minting a duplicate.
    """
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("defer requires a reason — a deferral with no reason is what this replaces")
    inbox = ws / CAPTURE_FILE
    if not inbox.exists():
        raise ValueError(f"no capture inbox in {ws}")

    records = read_jsonl(inbox)
    idx = next((i for i, r in enumerate(records) if str(r.get("id", "")) == cap_id), -1)
    if idx < 0:
        raise ValueError(f"capture {cap_id!r} not found in {inbox}")

    project_root = ai_work.parent
    aip_id, task_id = _workspace_origin(ws, ai_work)
    acc = (account_id or read_account_id(ai_work) or "_unassigned").strip()
    bl_id = backlog_id_for(aip_id, cap_id)

    already = any(str(r.get("backlog_id", "")) == bl_id for r in read_backlog(ai_work, acc))
    row_done = records[idx].get("status") == DEFERRED and records[idx].get("deferred_to") == bl_id
    if already and row_done:
        return bl_id, False

    if not already:
        rec = backlog_record(records[idx], aip_id=aip_id, task_id=task_id, ws=ws,
                             project_root=project_root, reason=reason, account_id=acc,
                             when=when or date.today().isoformat())
        _append_backlog(ai_work, rec, acc)

    if not row_done:
        records[idx] = dict(records[idx], status=DEFERRED, deferred_to=bl_id)
        _rewrite_inbox(inbox, records)
    append_promotion_log(ai_work, {
        "logged_at": when or date.today().isoformat(),
        "backlog_id": bl_id,
        "outcome": "deferred",
        "disposition_ref": "",
        "reason": reason,
        "by": acc,
        "origin": {"aip_id": aip_id, "task_id": task_id, "cap_id": cap_id},
        "candidate_kind": records[idx].get("candidate_kind", ""),
        "improvement_scope": records[idx].get("improvement_scope", ""),
    })
    return bl_id, True


def migrate(ai_work: Path, *, dry_run: bool = True, account_id: str = "",
            when: str = "") -> "list[dict]":
    """Move every existing `status: deferred` row into the backlog. `captured` rows are NOT touched.

    Returns one report dict per row so the caller can reconcile a count against the CR's figure rather
    than trusting a summary line.
    """
    acc = (account_id or read_account_id(ai_work) or "_unassigned").strip()
    project_root = ai_work.parent
    stamp = when or date.today().isoformat()
    existing = {str(r.get("backlog_id", "")) for r in read_backlog(ai_work, acc)}
    report: "list[dict]" = []

    for inbox in sorted((ai_work / "workspaces").rglob(CAPTURE_FILE)):
        ws = inbox.parent
        try:
            records = read_jsonl(inbox)
        except Exception as e:
            print(f"warn: unreadable inbox, skipped: {ws.name}: {e}", file=sys.stderr)
            continue
        hits = [i for i, r in enumerate(records) if r.get("status") == DEFERRED]
        if not hits:
            continue
        aip_id, task_id = _workspace_origin(ws, ai_work)
        changed = False
        for i in hits:
            cap_id = str(records[i].get("id", "") or "")
            bl_id = backlog_id_for(aip_id, cap_id)
            reason = str(records[i].get("triage_note", "") or "").strip() \
                or "migrated from an existing `deferred` row (CR-AIWS-2026-08-125 C8); no reason was recorded at the time"
            row = {"backlog_id": bl_id, "workspace": ws.name, "cap_id": cap_id,
                   "aip_id": aip_id, "already": bl_id in existing}
            report.append(row)
            if bl_id in existing:
                continue
            if not dry_run:
                rec = backlog_record(records[i], aip_id=aip_id, task_id=task_id, ws=ws,
                                     project_root=project_root, reason=reason, account_id=acc,
                                     when=stamp)
                _append_backlog(ai_work, rec, acc)
                records[i] = dict(records[i], deferred_to=bl_id)
                changed = True
            existing.add(bl_id)
        if changed and not dry_run:
            _rewrite_inbox(inbox, records)
    return report


def resolve(ai_work: Path, backlog_id: str, *, disposition_ref: str, status: str = "triaged",
            account_id: str = "", when: str = "") -> bool:
    """Close a backlog row by naming what it BECAME — a CR id, a checklist item, a lint code."""
    if status not in BACKLOG_STATUSES:
        raise ValueError(f"status must be one of {list(BACKLOG_STATUSES)}")
    if not (disposition_ref or "").strip():
        raise ValueError("resolve requires --disposition-ref: what did this row become?")
    acc = (account_id or read_account_id(ai_work) or "_unassigned").strip()
    p = capture_backlog_path(ai_work, acc)
    if not p.exists():
        return False
    rows = read_jsonl(p)
    idx = next((i for i, r in enumerate(rows) if str(r.get("backlog_id", "")) == backlog_id), -1)
    if idx < 0:
        return False
    rows[idx] = dict(rows[idx], status=status, resolution={
        "resolved_at": when or date.today().isoformat(),
        "resolved_by": acc,
        "disposition_ref": disposition_ref.strip(),
    })
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    for l in lines:
        json.loads(l)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    append_promotion_log(ai_work, {
        "logged_at": when or date.today().isoformat(),
        "backlog_id": backlog_id,
        "outcome": status,
        "disposition_ref": disposition_ref.strip(),
        "by": acc,
        "origin": rows[idx].get("origin", {}),
        "candidate_kind": rows[idx].get("candidate_kind", ""),
        "improvement_scope": rows[idx].get("improvement_scope", ""),
    })
    return True


# ---------------------------------------------------------------- CLI


def main() -> int:
    ap = argparse.ArgumentParser(description="Capture triage: sweep, defer, migrate, list, resolve")
    ap.add_argument("--ai-work", default="", help="path to .ai-work (default: discovered upward)")
    sub = ap.add_subparsers(dest="verb", required=True)

    s = sub.add_parser("sweep", help="list rows still `captured` in a workspace")
    s.add_argument("--workspace", required=True)

    d = sub.add_parser("defer", help="move one capture to the backlog")
    d.add_argument("--workspace", required=True)
    d.add_argument("--cap", required=True, help="capture id, e.g. CAP-1123-04")
    d.add_argument("--reason", required=True, help="why it is being deferred — required, never invented")

    m = sub.add_parser("migrate", help="move existing `deferred` rows into the backlog")
    m.add_argument("--dry-run", action="store_true", default=False)
    m.add_argument("--apply", action="store_true", default=False)

    l = sub.add_parser("list", help="show the backlog")
    l.add_argument("--account", default="")
    l.add_argument("--status", default="")
    l.add_argument("--group-by", default="", choices=["", "scope", "kind", "target"],
                   help="summarise counts instead of listing rows (AIP-EXEC-1138); "
                        "`scope` and `kind` use the projected value, not just the stated one")

    r = sub.add_parser("resolve", help="close a backlog row")
    r.add_argument("--backlog-id", required=True)
    r.add_argument("--disposition-ref", required=True)
    r.add_argument("--status", default="triaged", choices=list(BACKLOG_STATUSES))

    ns = ap.parse_args()
    start = Path(ns.ai_work) if ns.ai_work else Path.cwd()
    try:
        ai_work = Path(ns.ai_work).resolve() if ns.ai_work else find_ai_work_root(start) / ".ai-work"
    except SystemExit:
        print("error: no .ai-work/ found — run from a project root or pass --ai-work", file=sys.stderr)
        return 2

    if ns.verb == "sweep":
        rows = sweep(Path(ns.workspace).resolve())
        for r_ in rows:
            print(f"  {r_.get('id','?'):16s} {r_.get('type',''):22s} {str(r_.get('title',''))[:70]}")
        print(f"{len(rows)} row(s) still `captured`.")
        return 1 if rows else 0

    if ns.verb == "defer":
        try:
            bl, wrote = defer(Path(ns.workspace).resolve(), ns.cap, ns.reason, ai_work=ai_work)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        print(f"{'deferred' if wrote else 'already deferred'}: {ns.cap} -> {bl}")
        return 0

    if ns.verb == "migrate":
        # Dry by default: `--apply` is the only thing that writes. A migration that runs by accident
        # is worse than one that has to be asked for twice.
        dry = not ns.apply
        rep = migrate(ai_work, dry_run=dry)
        fresh = [r_ for r_ in rep if not r_["already"]]
        print(f"{'DRY RUN — ' if dry else ''}{len(rep)} deferred row(s) found, "
              f"{len(fresh)} to move, {len(rep) - len(fresh)} already in the backlog.")
        for r_ in rep[:200]:
            print(f"  {r_['backlog_id']:26s} {r_['workspace']:40s} {r_['cap_id']}"
                  f"{'  (already)' if r_['already'] else ''}")
        if len(rep) > 200:
            print(f"  … {len(rep) - 200} more not printed (the count above is the full total)")
        if dry:
            print("nothing written. Re-run with --apply to move them.")
        return 0

    if ns.verb == "list":
        rows = read_backlog(ai_work, ns.account)
        if ns.status:
            rows = [r_ for r_ in rows if r_.get("status") == ns.status]
        # AIP-EXEC-1138: show the routing fields a row IMPLIES, not just the ones it states. 171 of
        # 179 open rows state no `improvement_scope`, which is why nothing could sort this backlog.
        # A `~` prefix marks a DERIVED value — never let the display collapse that distinction, or
        # the projection quietly becomes indistinguishable from what a human chose.
        from lint_workspace import project_capture_fields  # noqa: PLC0415  (read-side only)
        if ns.group_by:
            key = {"scope": "improvement_scope", "kind": "candidate_kind"}.get(ns.group_by)
            groups: "dict[str, int]" = {}
            for r_ in rows:
                val = (project_capture_fields(r_)[key] if key
                       else str(r_.get("suggested_target", "") or "")) or "(unresolved)"
                groups[val] = groups.get(val, 0) + 1
            for val, n in sorted(groups.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"  {val:34s} {n:4d}")
            print(f"{len(rows)} backlog row(s) in {len(groups)} group(s) by {ns.group_by}.")
            return 0
        derived_n = 0
        for r_ in rows:
            proj = project_capture_fields(r_)
            scope = proj["improvement_scope"] or "-"
            if "improvement_scope" in proj["derived"]:
                scope = "~" + scope
                derived_n += 1
            print(f"  {r_.get('backlog_id',''):26s} {r_.get('status',''):10s} {scope:9s} "
                  f"{str(r_.get('title',''))[:56]}")
        print(f"{len(rows)} backlog row(s); {derived_n} scope value(s) marked `~` are DERIVED "
              f"from the kind, not stated on the row.")
        return 0

    if ns.verb == "resolve":
        ok = resolve(ai_work, ns.backlog_id, disposition_ref=ns.disposition_ref, status=ns.status)
        if not ok:
            print(f"error: backlog row not found: {ns.backlog_id}", file=sys.stderr)
            return 2
        print(f"resolved {ns.backlog_id} -> {ns.status} ({ns.disposition_ref})")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
