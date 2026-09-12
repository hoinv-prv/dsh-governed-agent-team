#!/usr/bin/env python3
"""Unit tests for step_handoff_missing lint rule (Wave 2 Item 2)."""
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lint_workspace import lint_workspace_dir
from _common import LintReport, write_text


def test_missing_handoff_warning():
    """Test that lint warns when a completed step lacks a handoff row."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create workspace structure
        ws = tmpdir / "workspace"
        ws.mkdir()

        # Create required files
        write_text(ws / "00_task_brief.md", "# Task\nTest")
        write_text(ws / "02_runtime_queue.jsonl", "")
        write_text(ws / "04_findings.md", "# Findings\n")
        write_text(ws / "05_open_questions.md", "")
        write_text(ws / "06_capture_inbox.jsonl", "")
        write_text(ws / "07_output_draft.md", "")

        # Create AIP with steps that have Expected Outputs
        aip_path = tmpdir / "test.aip"
        aip_text = """---
artifact_type: aip_exec
artifact_id: AIP-TEST-0050
title: Test
status: active
---

## Step: STEP-01 — Design
Objective:
Design something.

Expected Outputs:
- `design.md` — design document

## Step: STEP-02 — Implement
Objective:
Implement it.

Expected Outputs:
- `impl.md` — implementation
"""
        write_text(aip_path, aip_text)

        # Create pointer pointing at STEP-03 (so STEP-01 and STEP-02 are completed)
        pointer = {
            "step_id": "STEP-03",
            "status": "active",
            "aip_path": str(aip_path),
            "updated_at": "2026-08-25"
        }
        write_text((ws / ".current_step.json"), json.dumps(pointer))

        # Create ASC
        write_text(ws / "00c_active_step_context.md", "# ASC\n")

        # Create step_outputs but with NO handoff rows for STEP-01 and STEP-02
        step_outputs = ws / "step_outputs"
        step_outputs.mkdir()
        write_text((step_outputs / "index.jsonl"), "")

        # Run lint
        report = LintReport(target=str(ws))
        lint_workspace_dir(ws, report)

        # Check for warnings about missing handoff
        warnings = [f for f in report.findings if f.code == "step_handoff_missing"]

        assert len(warnings) >= 1, f"Expected warnings for missing handoff, got: {[f.code for f in report.findings]}"
        assert any("STEP-01" in f.message for f in warnings), "Should warn about STEP-01 missing handoff"
        assert any("STEP-02" in f.message for f in warnings), "Should warn about STEP-02 missing handoff"

        print(f"✓ test_missing_handoff_warning passed ({len(warnings)} warnings)")


def test_no_warning_when_handoff_exists():
    """Test that lint does NOT warn when handoff row exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create workspace structure
        ws = tmpdir / "workspace"
        ws.mkdir()

        # Create required files
        write_text(ws / "00_task_brief.md", "# Task\nTest")
        write_text(ws / "02_runtime_queue.jsonl", "")
        write_text(ws / "04_findings.md", "# Findings\n")
        write_text(ws / "05_open_questions.md", "")
        write_text(ws / "06_capture_inbox.jsonl", "")
        write_text(ws / "07_output_draft.md", "")
        write_text(ws / "00c_active_step_context.md", "# ASC\n")

        # Create AIP
        aip_path = tmpdir / "test.aip"
        aip_text = """---
artifact_type: aip_exec
artifact_id: AIP-TEST-0051
title: Test
status: active
---

## Step: STEP-01 — Design
Objective:
Design something.

Expected Outputs:
- `design.md` — design document
"""
        write_text(aip_path, aip_text)

        # Create pointer pointing at STEP-02 (so STEP-01 is completed)
        pointer = {
            "step_id": "STEP-02",
            "status": "active",
            "aip_path": str(aip_path),
            "updated_at": "2026-08-25"
        }
        write_text((ws / ".current_step.json"), json.dumps(pointer))

        # Create step_outputs WITH handoff row for STEP-01
        step_outputs = ws / "step_outputs"
        step_outputs.mkdir()
        index_row = {
            "source_id": "OUT-0051-01-01",
            "source_type": "step_output",
            "step_id": "STEP-01",
            "status": "draft",
            "target_path": "design.md"
        }
        write_text((step_outputs / "index.jsonl"), json.dumps(index_row) + "\n")

        # Run lint
        report = LintReport(target=str(ws))
        lint_workspace_dir(ws, report)

        # Check that NO warnings about missing handoff
        warnings = [f for f in report.findings if f.code == "step_handoff_missing"]

        assert len(warnings) == 0, f"Should have no warnings, got: {[f.message for f in warnings]}"

        print("✓ test_no_warning_when_handoff_exists passed")


def test_no_warning_for_steps_with_no_expected_outputs():
    """Test that lint does NOT warn for steps without Expected Outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create workspace structure
        ws = tmpdir / "workspace"
        ws.mkdir()

        # Create required files
        write_text(ws / "00_task_brief.md", "# Task\nTest")
        write_text(ws / "02_runtime_queue.jsonl", "")
        write_text(ws / "04_findings.md", "# Findings\n")
        write_text(ws / "05_open_questions.md", "")
        write_text(ws / "06_capture_inbox.jsonl", "")
        write_text(ws / "07_output_draft.md", "")
        write_text(ws / "00c_active_step_context.md", "# ASC\n")

        # Create AIP with step that has NO Expected Outputs
        aip_path = tmpdir / "test.aip"
        aip_text = """---
artifact_type: aip_exec
artifact_id: AIP-TEST-0052
title: Test
status: active
---

## Step: STEP-01 — Review
Objective:
Review something.

Expected Outputs:
"""
        write_text(aip_path, aip_text)

        # Create pointer pointing at STEP-02
        pointer = {
            "step_id": "STEP-02",
            "status": "active",
            "aip_path": str(aip_path),
            "updated_at": "2026-08-25"
        }
        write_text((ws / ".current_step.json"), json.dumps(pointer))

        # Create step_outputs with NO handoff
        step_outputs = ws / "step_outputs"
        step_outputs.mkdir()
        write_text((step_outputs / "index.jsonl"), "")

        # Run lint
        report = LintReport(target=str(ws))
        lint_workspace_dir(ws, report)

        # Check that NO warnings (because step had no Expected Outputs)
        warnings = [f for f in report.findings if f.code == "step_handoff_missing"]

        assert len(warnings) == 0, f"Should not warn for steps without Expected Outputs, got: {[f.message for f in warnings]}"

        print("✓ test_no_warning_for_steps_with_no_expected_outputs passed")


if __name__ == "__main__":
    test_missing_handoff_warning()
    test_no_warning_when_handoff_exists()
    test_no_warning_for_steps_with_no_expected_outputs()
    print("\n✅ All lint tests passed!")
