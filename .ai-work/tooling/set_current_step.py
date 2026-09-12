#!/usr/bin/env python3
"""Set the current-step pointer for a workspace.

Writes a small pointer file at <workspace>/.current_step.json and updates
the Active AIP reference markdown so the runtime knows which AIP/step
is active. Does NOT materialize the Active Step Context — use
build_active_step_context.py for that after pointing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    find_ai_work_root,
    parse_frontmatter,
    portable_locator,
    read_text,
    resolve_locator,
    today,
    write_text,
)


def _regenerate_active_aip(ws: Path, aip_id: str, aip_path: str,
                           status: str) -> None:
    """Rewrite 00b_active_aip.md deterministically from AIP frontmatter.

    Previous implementation patched individual lines, which left stale
    fields (AIP Type) when an AIP was swapped. FND-032
    remediation: regenerate the whole file from the AIP frontmatter so
    pointer recovery is a single command.
    """
    aip_type = ""
    if aip_path:
        ap = resolve_locator(aip_path, find_ai_work_root(ws))
        if ap.exists():
            meta, _ = parse_frontmatter(read_text(ap))
            aip_type = str(meta.get("artifact_type", "")).replace("aip_", "")

    body = (
        "# Active AIP Reference\n"
        "\n"
        f"- Source AIP ID: {aip_id}\n"
        f"- Source AIP Path: {aip_path}\n"
        f"- AIP Type: {aip_type}\n"
        f"- Status: {status}\n"
    )
    write_text(ws / "00b_active_aip.md", body)


def main() -> int:
    p = argparse.ArgumentParser(description="Set current step pointer")
    p.add_argument("--workspace", required=True, help="Workspace directory")
    p.add_argument("--aip", required=True,
                   help="Source AIP id, e.g. AIP-PLAN-001")
    p.add_argument("--aip-path", help="Source AIP file path (optional)")
    p.add_argument("--step-id", required=True, help="Step id, e.g. STEP-02")
    p.add_argument("--status", default="active",
                   choices=["active", "blocked", "done"])
    ns = p.parse_args()

    ws = Path(ns.workspace).resolve()
    if not ws.is_dir():
        print(f"error: workspace not found: {ws}", file=sys.stderr)
        return 2

    # CR-AIWS-2026-07-022: persist the AIP path as a portable __PROJECT_ROOT__ token
    # (not a machine-absolute path) so the workspace pointer survives clone/relocation.
    aip_path_portable = (
        portable_locator(ns.aip_path, find_ai_work_root(ws)) if ns.aip_path else ""
    )
    pointer = {
        "aip_id": ns.aip,
        "aip_path": aip_path_portable,
        "step_id": ns.step_id,
        "status": ns.status,
        "updated_at": today(),
    }
    pointer_path = ws / ".current_step.json"
    write_text(pointer_path, json.dumps(pointer, indent=2, ensure_ascii=False) + "\n")

    _regenerate_active_aip(ws, ns.aip, aip_path_portable, ns.status)

    print(f"pointer set: {ns.aip} / {ns.step_id} ({ns.status})")
    print(f"  -> {pointer_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
