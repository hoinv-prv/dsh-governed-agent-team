#!/usr/bin/env python3
"""
AIWS smoke check helper.

Purpose:
- Verify basic AIWS deployment structure.
- Compile tooling scripts.
- Report missing folders/files.
- Avoid mutating project data.

This is not a full CI/test harness and does not prove semantic correctness.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime


REQUIRED_DIRS = [
    ".ai-work",
    ".ai-work/tooling",
    ".ai-work/aip",
    ".ai-work/workspaces",
    ".ai-work/workspace_templates",
    ".ai-work/wiki_sources",
    ".ai-work/source_profiles",
]

RECOMMENDED_FILES = [
    ".ai-work/project_profile.yml",
]

REQUIRED_TOOLS = [
    "init_workspace.py",
    "run_aip.py",
    "build_active_step_context.py",
    "lint_workspace.py",
    "lint_all.py",
    "lookup_wiki_source.py",
    "build_wiki_source_meta.py",
    "build_wiki_source_index.py",
]


def compile_tool(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"path": str(path), "status": "OK"}
    except Exception as e:
        return {"path": str(path), "status": "FAIL", "error": repr(e)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    aiws = root / ".ai-work"

    result = {
        "smoke_check_id": f"AIWS-SMOKE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "project_root": str(root),
        "python_version": sys.version.split()[0],
        "required_dirs": [],
        "recommended_files": [],
        "tool_compile": [],
        "warnings": [],
        "blocking_issues": [],
        "verdict": "SMOKE_PASS",
        "note": "Smoke check verifies structure/tooling only, not semantic correctness.",
    }

    for rel in REQUIRED_DIRS:
        p = root / rel
        ok = p.exists() and p.is_dir()
        result["required_dirs"].append({"path": rel, "status": "OK" if ok else "MISSING"})
        if not ok:
            result["blocking_issues"].append(f"Missing required directory: {rel}")

    for rel in RECOMMENDED_FILES:
        p = root / rel
        ok = p.exists()
        result["recommended_files"].append({"path": rel, "status": "OK" if ok else "MISSING"})
        if not ok:
            result["warnings"].append(f"Missing recommended file: {rel}")

    tooling = aiws / "tooling"
    for tool in REQUIRED_TOOLS:
        p = tooling / tool
        if not p.exists():
            result["tool_compile"].append({"path": str(p), "status": "MISSING"})
            result["blocking_issues"].append(f"Missing required tool: {tool}")
        else:
            cr = compile_tool(p)
            result["tool_compile"].append(cr)
            if cr["status"] != "OK":
                result["blocking_issues"].append(f"Tool compile failed: {tool}")

    if result["blocking_issues"]:
        result["verdict"] = "SMOKE_FAIL_BLOCKING"
    elif result["warnings"]:
        result["verdict"] = "SMOKE_PASS_WITH_WARNINGS"

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"AIWS Smoke Check: {result['verdict']}")
        print(f"Project root: {root}")
        if result["blocking_issues"]:
            print("\nBlocking issues:")
            for x in result["blocking_issues"]:
                print(f"- {x}")
        if result["warnings"]:
            print("\nWarnings:")
            for x in result["warnings"]:
                print(f"- {x}")

    return 1 if result["blocking_issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
