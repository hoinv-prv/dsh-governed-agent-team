#!/usr/bin/env python3
"""Build the AIP Registry/Index — CR-AIWS-2026-06-015 v2 (per-account folders).

A small GENERATED projection over every AIP under .ai-work/aip/ (RECURSIVE — covers the
per-account folders `.ai-work/aip/<account_id>/<kind>/` AND legacy flat `.ai-work/aip/<kind>/`,
including archived sub-folders like `exec/done/`). One line per AIP:

  {"aip_id": "...", "account": "...", "status": "...", "captures_triaged": true|false, "open_captures": N}

  - account           — the per-account folder the AIP lives in ("(legacy)" for flat legacy AIPs).
                        Since v2 namespaces new AIPs by FOLDER (id format unchanged), aip_id alone
                        is NOT globally unique — (account, aip_id) is the key, and DUPLICATE-ID
                        detection is ACCOUNT-SCOPED (a bare NNN may legitimately recur across
                        members; only a clash WITHIN one account scope is flagged).
  - status            — frontmatter status (draft/active/done/archived).
  - captures_triaged  — true when NO workspace capture is still status "captured"
                        (aligned with lint_workspace's untriaged check).
  - open_captures     — how many capture rows still need triage.

Rebuilt-from-records, never hand-edited (a projection). §2.3: nothing is written into AIP files.
CR-015 v2 RETIRED the `id_claims.jsonl` ledger, so there is no ledger reconcile anymore — the
allocator's state is the per-account counter in `account_info.yaml` (see allocate_aip_id.py).

Usage:
  py build_aip_index.py                    # rebuild .ai-work/aip/index.jsonl
  py build_aip_index.py --list-untriaged   # also list AIPs whose inbox has open captures
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    append_maintenance_log,
    find_ai_work_root,
    parse_frontmatter,
    portable_locator,
    read_jsonl,
    read_text,
    write_jsonl,
)

_AID_RE = re.compile(r"^AIP-([A-Z]+)-(\d+)$")
KIND_DIRS = ("exec", "plans", "local")
NEEDS_TRIAGE_STATUS = "captured"  # mirror lint_workspace: only 'captured' = untriaged
LEGACY_SCOPE = "(legacy)"
_REL_PENDING: dict = {}  # CR-AIWS-2026-07-008 C4: {aip_id: pending relation-candidate count}


def _iter_aips(ai_work: Path):
    """Yield (path, meta) for every real AIP under aip/ (recursive incl. account folders + done/)."""
    aip_root = ai_work / "aip"
    if not aip_root.is_dir():
        return
    for f in sorted(aip_root.rglob("*.md")):
        try:
            meta, _ = parse_frontmatter(read_text(f))
        except Exception as e:  # noqa: BLE001
            print(f"warn: failed to parse {f}: {e}", file=sys.stderr)
            continue
        aid = str(meta.get("artifact_id", ""))
        if _AID_RE.match(aid) or aid == "AIP-ROOT":  # skip template placeholders (AIP-EXEC-NNN)
            yield f, meta


def _account_scope(path: Path, ai_work: Path) -> str:
    """Account namespace for an AIP path: '<account_id>' under aip/<account_id>/<kind>/,
    or '(legacy)' for flat aip/<kind>/ AIPs."""
    try:
        rel = path.relative_to(ai_work / "aip")
    except ValueError:
        return "(unknown)"
    parts = rel.parts
    if len(parts) <= 1 or parts[0] in KIND_DIRS:
        return LEGACY_SCOPE
    return parts[0]


_WS_NAME_RE = re.compile(r"^TASK-\d{8}-([A-Za-z]+)-(\d+)$")


def aip_id_from_workspace_name(name: str) -> str:
    """`TASK-YYYYMMDD-<kind>-NNNN` -> `AIP-<KIND>-NNNN`, else "" (CR-AIWS-2026-08-125 C4).

    A pure name derivation, deliberately not a search: it either reads the id out of the convention or
    admits it cannot. Names predating the convention (no trailing number, e.g.
    `TASK-20260422-review-vjp-aip-samples`) return "" and the caller warns.
    """
    m = _WS_NAME_RE.match(name.strip())
    return f"AIP-{m.group(1).upper()}-{m.group(2)}" if m else ""


def _open_captures_by_aip(ai_work: Path) -> dict[str, int]:
    """{aip_id: open_capture_count} summed across the AIP's workspace(s).

    'open' = a capture row still in status 'captured' (matches lint_workspace's untriaged check).
    Joined to the AIP via each workspace's .current_step.json back-link. RECURSIVE so per-account
    workspaces .ai-work/workspaces/<account_id>/TASK-... are found alongside legacy flat ones.
    """
    out: dict[str, int] = {}
    ws_root = ai_work / "workspaces"
    if not ws_root.is_dir():
        return out
    # CR-AIWS-2026-08-125 C4: drive the scan from the INBOX, not from the back-link pointer.
    # Driving it from `.current_step.json` made a workspace without one invisible, and its open
    # captures invisible with it — measured here as 13 workspaces holding 18 rows still `captured`.
    for inbox in sorted(ws_root.rglob("08_capture_inbox.jsonl")):
        ws = inbox.parent
        ptr = ws / ".current_step.json"
        aip_id = ""
        if ptr.exists():
            try:
                aip_id = str(json.loads(ptr.read_text(encoding="utf-8")).get("aip_id", ""))
            except Exception:
                aip_id = ""
        if not aip_id:
            aip_id = aip_id_from_workspace_name(ws.name)
        if not aip_id:
            # WARN, never skip silently: a folder that predates the naming convention still holds
            # rows, and a scan that drops them without a word looks exactly like a clean scan.
            print(f"warn: no AIP back-link and no id in folder name: {ws.name} "
                  f"(its capture rows are not counted)", file=sys.stderr)
            continue
        try:
            rows = read_jsonl(inbox)
        except Exception:
            continue  # malformed inbox → no countable open captures here; lint_workspace flags it
        n = sum(1 for r in rows if r.get("status") == NEEDS_TRIAGE_STATUS)
        out[aip_id] = out.get(aip_id, 0) + n
        # CR-AIWS-2026-07-008 C4: relation candidates awaiting a Relations Enrichment CR batch.
        rn = sum(1 for r in rows
                 if r.get("status") == NEEDS_TRIAGE_STATUS
                 and r.get("candidate_kind") == "artifact_relation_update")
        if rn:
            _REL_PENDING[aip_id] = _REL_PENDING.get(aip_id, 0) + rn
    return out


def _log_rebuild(ai_work: Path, out: Path, count: int) -> None:
    append_maintenance_log(ai_work / "aip" / "maintenance_log.jsonl", {
        "log_id": f"AIPIDX-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "maintenance_model_version": "wsm_v1",
        "action": "aip_index_rebuilt",
        "source_id": "(aip-index-projection)",
        "target_artifact": portable_locator(out, ai_work.parent),
        "change_summary": f"Rebuilt AIP registry projection with {count} entries.",
        "review_decision": "projection_rebuilt",
        "rollback_hint": "Restore from git/history; rebuild is idempotent.",
        "runtime_boundary": "AIP index rebuild is projection maintenance, not approval/promotion",
    })


def build(project_root: Path) -> list[dict]:
    ai_work = project_root / ".ai-work"
    open_by_aip = _open_captures_by_aip(ai_work)
    records: list[dict] = []
    seen: dict[tuple[str, str], int] = {}  # (account_scope, aip_id) -> count
    for path, meta in _iter_aips(ai_work):
        aid = str(meta.get("artifact_id", ""))
        scope = _account_scope(path, ai_work)
        seen[(scope, aid)] = seen.get((scope, aid), 0) + 1
        openc = open_by_aip.get(aid, 0)
        rec = {
            "aip_id": aid,
            "account": scope,
            "status": meta.get("status", ""),
            "captures_triaged": openc == 0,
            "open_captures": openc,
        }
        # CR-AIWS-2026-07-008 C4: only emitted when >0 (omit-blank keeps projection slim).
        if _REL_PENDING.get(aid):
            rec["open_relation_captures"] = _REL_PENDING[aid]
        records.append(rec)
    # ACCOUNT-SCOPED duplicate-id check — a bare NNN may legitimately recur across accounts,
    # so only a clash within the SAME account scope is a real duplicate. stderr only.
    dups = {f"{s}/{a}": v for (s, a), v in seen.items() if a and v > 1}
    if dups:
        print(f"warn: duplicate artifact_id(s) within an account scope: {dups}", file=sys.stderr)
    # NO ledger reconcile (CR-015 v2: id_claims.jsonl ledger retired).
    out = ai_work / "aip" / "index.jsonl"
    write_jsonl(out, records)
    _log_rebuild(ai_work, out, len(records))
    print(f"wrote {len(records)} records → {out}")
    print("note: AIP index rebuild is projection maintenance, not approval/promotion")
    return records


def main() -> int:
    p = argparse.ArgumentParser(description="Build AIP registry/index (CR-015 v2, lean)")
    p.add_argument("--list-untriaged", action="store_true",
                   help="After rebuild, list AIPs whose capture inbox has open (captured) items")
    ns = p.parse_args()
    records = build(find_ai_work_root(Path.cwd()))
    if ns.list_untriaged:
        offenders = [r for r in records if r.get("open_captures", 0) > 0]
        print(f"\n=== AIPs with open captures ({len(offenders)}) ===")
        for r in sorted(offenders, key=lambda x: -x["open_captures"]):
            rel = r.get("open_relation_captures", 0)
            rel_note = f" (trong đó {rel} relation-candidate chờ Enrichment CR)" if rel else ""
            print(f"  {r['account']}/{r['aip_id']}: {r['open_captures']} open{rel_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
