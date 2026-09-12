#!/usr/bin/env python3
"""Unit tests for handoff stub writer (Wave 2 Item 1).

Tests the idempotent handoff stub creation in run_aip.py when advancing steps.
"""
import json
import tempfile
from pathlib import Path
import sys
from io import StringIO

# Add tooling to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_aip import _extract_step_number, _write_handoff_stub
from _common import write_text, parse_frontmatter


def _create_test_aip(aip_path: Path, steps_text: str) -> None:
    """Create a test AIP with the given step content."""
    frontmatter = """---
artifact_type: aip_exec
artifact_id: AIP-TEST-0099
title: Test AIP
status: active
project: test
owner: test
updated_at: 2026-08-25
---

"""
    write_text(aip_path, frontmatter + steps_text)


def _create_test_workspace(ws_path: Path, current_step: str) -> None:
    """Create a test workspace with a pointer."""
    ws_path.mkdir(parents=True, exist_ok=True)
    pointer = {
        "step_id": current_step,
        "status": "active",
        "updated_at": "2026-08-25"
    }
    pointer_file = ws_path / ".current_step.json"
    write_text(pointer_file, json.dumps(pointer))


def test_extract_step_number():
    """Test step number extraction from step_id."""
    assert _extract_step_number("STEP-01") == 1
    assert _extract_step_number("STEP-02") == 2
    assert _extract_step_number("STEP-10") == 10
    assert _extract_step_number("STEP-99") == 99
    assert _extract_step_number("INVALID") == 0
    assert _extract_step_number("") == 0
    print("✓ test_extract_step_number passed")


def test_idempotent_write():
    """Test that handoff stub write is idempotent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ws = tmpdir / "workspace"
        aip_path = tmpdir / "test.md"

        # Create test AIP with step
        steps_content = """
## Step: STEP-01 — Design
### Objective
Design the handoff.
### Expected Outputs
- `01_design.md` — design document
"""
        _create_test_aip(aip_path, steps_content)
        _create_test_workspace(ws, "STEP-02")

        # First write
        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        meta_file = ws / "step_outputs" / "STEP-01.meta.yml"
        assert meta_file.exists(), "First write should create meta file"
        first_content = meta_file.read_text(encoding="utf-8")
        first_mtime = meta_file.stat().st_mtime

        # Second write (should skip)
        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})
        second_content = meta_file.read_text(encoding="utf-8")
        second_mtime = meta_file.stat().st_mtime

        assert first_content == second_content, "Content should not change"
        assert first_mtime == second_mtime, "File should not be modified on second write"
        print("✓ test_idempotent_write passed")


def test_output_locator_extraction():
    """Test output_locator extraction from Expected Outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ws = tmpdir / "workspace"
        aip_path = tmpdir / "test.md"

        steps_content = """
## Step: STEP-01 — Design
Objective:
Design the handoff.

Recommended Mode:
Planning

Expected Outputs:
- `01_design.md` — handoff workflow design
- `02_implementation.md` — implementation plan
"""
        _create_test_aip(aip_path, steps_content)
        _create_test_workspace(ws, "STEP-02")

        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        meta_file = ws / "step_outputs" / "STEP-01.meta.yml"
        content = meta_file.read_text(encoding="utf-8")

        # Should extract first line as output_locator (including the backticks)
        assert "01_design.md" in content, \
            "Should extract first line from Expected Outputs"
        print("✓ test_output_locator_extraction passed")


def test_fallback_output_locator():
    """Test fallback to canonical location when no Expected Outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ws = tmpdir / "workspace"
        aip_path = tmpdir / "test.md"

        steps_content = """
## Step: STEP-01 — Design
Objective:
Design the handoff.

Expected Outputs:
"""
        _create_test_aip(aip_path, steps_content)
        _create_test_workspace(ws, "STEP-02")

        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        meta_file = ws / "step_outputs" / "STEP-01.meta.yml"
        content = meta_file.read_text(encoding="utf-8")

        # Should fallback to canonical location
        assert "output_locator: 04_findings.md#STEP-01" in content, \
            "Should fallback to canonical location when no Expected Outputs"
        print("✓ test_fallback_output_locator passed")


def test_index_jsonl_appending():
    """Test that index.jsonl is created and appended correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ws = tmpdir / "workspace"
        aip_path = tmpdir / "test.md"

        steps_content = """
## Step: STEP-01 — Design
Objective:
Design step 1.

Expected Outputs:
- `01_design.md`

## Step: STEP-02 — Implement
Objective:
Implement step 2.

Expected Outputs:
- `02_impl.md`
"""
        _create_test_aip(aip_path, steps_content)

        # Advance to STEP-02 → creates handoff for STEP-01
        _create_test_workspace(ws, "STEP-02")
        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        # Advance to STEP-03 → creates handoff for STEP-02
        _create_test_workspace(ws, "STEP-03")
        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        index_file = ws / "step_outputs" / "index.jsonl"
        assert index_file.exists(), "index.jsonl should be created"

        rows = []
        for line in index_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))

        assert len(rows) == 2, "Should have 2 entries (for STEP-01 and STEP-02)"
        assert rows[0]["step_id"] == "STEP-01", "First entry should be for STEP-01"
        assert rows[1]["step_id"] == "STEP-02", "Second entry should be for STEP-02"
        assert rows[0]["source_id"] == "OUT-0099-01-01"
        assert rows[1]["source_id"] == "OUT-0099-02-01"
        print("✓ test_index_jsonl_appending passed")


def test_no_write_on_first_step():
    """Test that no handoff is created when at STEP-01."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ws = tmpdir / "workspace"
        aip_path = tmpdir / "test.md"

        steps_content = """
## Step: STEP-01 — Design
Objective:
Design step 1.

Expected Outputs:
- `01_design.md`
"""
        _create_test_aip(aip_path, steps_content)
        _create_test_workspace(ws, "STEP-01")

        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        step_outputs_dir = ws / "step_outputs"
        # Directory might exist but should be empty or have no meta files
        meta_files = list(step_outputs_dir.glob("*.meta.yml")) if step_outputs_dir.exists() else []
        assert len(meta_files) == 0, "No handoff should be created at STEP-01"
        print("✓ test_no_write_on_first_step passed")


def test_correct_meta_fields():
    """Test that all required meta fields are present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ws = tmpdir / "workspace"
        aip_path = tmpdir / "test.md"

        steps_content = """
## Step: STEP-01 — Design
Objective:
Design step 1.

Expected Outputs:
- `01_design.md` — design
"""
        _create_test_aip(aip_path, steps_content)
        _create_test_workspace(ws, "STEP-02")

        _write_handoff_stub(ws, aip_path, {"artifact_id": "AIP-TEST-0099"})

        meta_file = ws / "step_outputs" / "STEP-01.meta.yml"
        content = meta_file.read_text(encoding="utf-8")

        required_fields = [
            "output_id: OUT-0099-01-01",
            "step_id: STEP-01",
            "result_type: output",
            "review_status: draft",
            "output_locator:",
            "source_refs: []",
            'notes: ""'
        ]

        for field in required_fields:
            assert field in content, f"Meta file should contain '{field}'"

        print("✓ test_correct_meta_fields passed")


if __name__ == "__main__":
    test_extract_step_number()
    test_idempotent_write()
    test_output_locator_extraction()
    test_fallback_output_locator()
    test_no_write_on_first_step()
    test_correct_meta_fields()
    test_index_jsonl_appending()

    print("\n✅ All tests passed!")
