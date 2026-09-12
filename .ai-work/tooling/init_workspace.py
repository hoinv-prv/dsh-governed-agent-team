#!/usr/bin/env python3
"""Initialize a task workspace from the workspace template.

Scaffolds .ai-work/workspaces/<task-id>/ with all runtime files pre-populated
from .ai-work/workspace_templates/task_workspace_template/. Optionally wires
the Task Brief and Active AIP reference to a given AIP id/path.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, today, read_text, write_text, read_account_id, portable_locator  # noqa: E402


def _align_runtime_queue_name(dest: Path) -> None:
    """Ensure new workspaces use 02_runtime_queue.jsonl (per aiws-aip init-workspace
    skill v0.9.12 alignment rule).

    Cases handled:
      - legacy only            → migrate content into runtime_q, remove legacy
      - both exist             → keep runtime_q, remove legacy (defensive: avoids
                                 duplicate queue file when template carries both)
      - runtime only           → no-op
      - neither                → create empty runtime_q

    Existing workspaces are not silently migrated by this function — only
    workspaces just scaffolded by this run.
    """
    runtime_q = dest / "02_runtime_queue.jsonl"
    legacy_q = dest / "02_investigation_queue.jsonl"

    if legacy_q.exists() and not runtime_q.exists():
        write_text(runtime_q, legacy_q.read_text())  # helper is UTF-8 + LF by contract
        legacy_q.unlink()
    elif legacy_q.exists() and runtime_q.exists():
        legacy_q.unlink()
    elif not runtime_q.exists():
        write_text(runtime_q, "")


def _fill_task_brief(path: Path, task_id: str, title: str | None) -> None:
    if not path.exists():
        return
    text = read_text(path)
    text = text.replace("TASK-YYYYMMDD-<slug>", task_id)
    if title:
        text = text.replace("## Goal\n...", f"## Goal\n{title}")
    write_text(path, text)


def _fill_active_aip(path: Path, aip_id: str | None, aip_path: str | None,
                     aip_type: str | None) -> None:
    if not path.exists() or not (aip_id or aip_path):
        return
    text = read_text(path)
    if aip_id:
        text = text.replace("- Source AIP ID:", f"- Source AIP ID: {aip_id}")
    if aip_path:
        text = text.replace("- Source AIP Path:", f"- Source AIP Path: {aip_path}")
    if aip_type:
        text = text.replace("- AIP Type:", f"- AIP Type: {aip_type}")
    text = text.replace("- Status:", "- Status: active")
    write_text(path, text)


def main() -> int:
    p = argparse.ArgumentParser(description="Initialize task workspace")
    p.add_argument("--task-id", required=True, help="TASK-YYYYMMDD-<slug>")
    p.add_argument("--title", help="Optional short goal/title")
    p.add_argument("--project-root",
                   help="Project root; defaults to nearest .ai-work/ ancestor")
    p.add_argument("--template",
                   help="Override path to workspace template directory")
    p.add_argument("--aip", help="Source AIP id, e.g. AIP-PLAN-001")
    p.add_argument("--aip-path", help="Source AIP file path")
    p.add_argument("--aip-type", help="plan|exec|local")
    p.add_argument("--account", help="Account id → per-account workspace folder "
                                     "(default: read account_info.yaml; CR-015 v2)")
    p.add_argument("--force", action="store_true",
                   help="Overwrite existing workspace directory")
    ns = p.parse_args()

    root = Path(ns.project_root).resolve() if ns.project_root else find_ai_work_root(Path.cwd())
    ai = root / ".ai-work"
    tpl = Path(ns.template) if ns.template else (
        ai / "workspace_templates" / "task_workspace_template")
    if not tpl.is_dir():
        print(f"error: template dir not found: {tpl}", file=sys.stderr)
        return 2

    # CR-015 v2: NEW workspaces live under a per-account folder .ai-work/workspaces/<account_id>/.
    # Falls back to legacy flat .ai-work/workspaces/ only when no account_id is set (pre-CR-016).
    account_id = (ns.account or read_account_id(ai)).strip()
    ws_base = (ai / "workspaces" / account_id) if account_id else (ai / "workspaces")
    dest = ws_base / ns.task_id
    if dest.exists():
        if not ns.force:
            print(f"error: workspace already exists: {dest} (use --force)",
                  file=sys.stderr)
            return 2
        shutil.rmtree(dest)

    shutil.copytree(tpl, dest)

    _align_runtime_queue_name(dest)

    _fill_task_brief(dest / "00_task_brief.md", ns.task_id, ns.title)
    _fill_active_aip(
        dest / "00b_active_aip.md",
        aip_id=ns.aip,
        # CR-AIWS-2026-07-022: persist a portable __PROJECT_ROOT__ token, not an absolute path.
        aip_path=(portable_locator(ns.aip_path, root) if ns.aip_path else ns.aip_path),
        aip_type=ns.aip_type,
    )

    asc_path = dest / "00c_active_step_context.md"
    if asc_path.exists():
        text = read_text(asc_path)
        text = text.replace("ASC-<task-id>-<step-id>", f"ASC-{ns.task_id}-STEP-00")
        text = text.replace("TASK-<task-id>", ns.task_id)
        text = text.replace("YYYY-MM-DD", today())
        if ns.aip:
            text = text.replace("source_aip: AIP-PLAN-001", f"source_aip: {ns.aip}")
        write_text(asc_path, text)

    print(f"workspace created: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
