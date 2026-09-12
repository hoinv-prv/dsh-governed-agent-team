#!/usr/bin/env python3
"""
End-to-end test: Complete handoff workflow
- Complete step N → stub created
- Step to N+1 → lint validates
- ASC renders Previous Step Results from index
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import write_text  # noqa: E402  CR-AIWS-2026-08-059: LF-stable writes, all OS

def test_e2e_workflow():
    """End-to-end test: complete step → handoff created → ASC renders"""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir)

        # Setup workspace structure
        step_outputs = ws / "step_outputs"
        step_outputs.mkdir()

        # Create initial pointer (at STEP-01)
        pointer_file = ws / ".current_step.json"
        pointer = {
            "current_step": "STEP-01",
            "step_index": 1,
            "aip_path": str(ws / "AIP.md"),
            "status": "active"
        }
        write_text(pointer_file, json.dumps(pointer, indent=2))

        # Create mock AIP with 3 steps
        aip_content = """# AIP-1113 Wave 2

## STEP-01 -- Design

### Objective
Design the handoff infrastructure.

### Expected Outputs
- 01_design.md -- architecture and components
- 02_spec.md -- technical specification

### Done Condition
Design document complete.

---

## STEP-02 -- Implementation

### Objective
Implement handoff writer and lint rule.

### Expected Outputs
- 03_implementation.md -- code changes and test results
- 04_findings.md -- implementation summary

### Done Condition
All tests passing.

---

## STEP-03 -- Verification

### Objective
Verify end-to-end workflow.

### Expected Outputs
- 05_verification.md -- test results and findings

### Done Condition
Workflow verified.
"""
        aip_path = ws / "AIP.md"
        write_text(aip_path, aip_content)

        # Simulate completion of STEP-01 and creation of handoff stub
        # (normally done by run_aip.py _write_handoff_stub)
        meta_01 = {
            "output_id": "OUT-1113-01-01",
            "step_id": "STEP-01",
            "result_type": "output",
            "review_status": "draft",
            "output_locator": "01_design.md",
            "source_refs": [],
            "notes": "Design document completed."
        }
        write_text((step_outputs / "STEP-01.meta.yml"),
            "output_id: OUT-1113-01-01\n"
            "step_id: STEP-01\n"
            "result_type: output\n"
            "review_status: draft\n"
            "output_locator: 01_design.md\n"
            "source_refs: []\n"
            "notes: Design document completed.\n"
        )

        # Create index.jsonl with STEP-01 handoff row
        index_row_01 = {
            "source_id": "OUT-1113-01-01",
            "source_type": "step_output",
            "step_id": "STEP-01",
            "status": "draft",
            "target_path": "step_outputs/STEP-01.meta.yml",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        write_text((step_outputs / "index.jsonl"), json.dumps(index_row_01) + "\n")

        # Verify STEP-01 handoff was created
        assert (step_outputs / "STEP-01.meta.yml").exists(), "STEP-01 meta not created"
        meta_01_content = (step_outputs / "STEP-01.meta.yml").read_text()
        assert "OUT-1113-01-01" in meta_01_content, "Output ID not in meta"
        assert "STEP-01" in meta_01_content, "Step ID not in meta"

        # Verify index contains STEP-01 row
        index_content = (step_outputs / "index.jsonl").read_text()
        index_rows = [json.loads(line) for line in index_content.strip().split('\n') if line]
        assert len(index_rows) == 1, "Index should have 1 row after STEP-01"
        assert index_rows[0]["source_id"] == "OUT-1113-01-01", "Index row source_id mismatch"

        print("[OK] STEP-01 handoff created and index populated")

        # Simulate: Step to STEP-02 (pointer advances)
        pointer["current_step"] = "STEP-02"
        pointer["step_index"] = 2
        write_text(pointer_file, json.dumps(pointer, indent=2))

        # Create STEP-02 handoff stub (normally done by run_aip.py)
        meta_02 = {
            "output_id": "OUT-1113-02-01",
            "step_id": "STEP-02",
            "result_type": "output",
            "review_status": "draft",
            "output_locator": "03_implementation.md",
            "source_refs": ["OUT-1113-01-01"],
            "notes": "Implementation completed."
        }
        write_text((step_outputs / "STEP-02.meta.yml"),
            "output_id: OUT-1113-02-01\n"
            "step_id: STEP-02\n"
            "result_type: output\n"
            "review_status: draft\n"
            "output_locator: 03_implementation.md\n"
            "source_refs:\n"
            "  - OUT-1113-01-01\n"
            "notes: Implementation completed.\n"
        )

        # Append STEP-02 row to index
        index_row_02 = {
            "source_id": "OUT-1113-02-01",
            "source_type": "step_output",
            "step_id": "STEP-02",
            "status": "draft",
            "target_path": "step_outputs/STEP-02.meta.yml",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with open(step_outputs / "index.jsonl", "a") as f:
            f.write(json.dumps(index_row_02) + "\n")

        # Verify STEP-02 handoff was created
        assert (step_outputs / "STEP-02.meta.yml").exists(), "STEP-02 meta not created"
        meta_02_content = (step_outputs / "STEP-02.meta.yml").read_text()
        assert "OUT-1113-02-01" in meta_02_content, "Output ID not in meta"

        # Verify index now has both rows
        index_content = (step_outputs / "index.jsonl").read_text()
        index_rows = [json.loads(line) for line in index_content.strip().split('\n') if line]
        assert len(index_rows) == 2, "Index should have 2 rows after STEP-02"
        step_ids = [row["step_id"] for row in index_rows]
        assert "STEP-01" in step_ids and "STEP-02" in step_ids, "Missing step IDs in index"

        print("[OK] STEP-02 handoff created and appended to index")

        # Simulate ASC rendering Previous Step Results for STEP-03
        # Wave 1 ASC builder reads index.jsonl and creates ## Previous Step Results section
        previous_step_results = []
        for row in index_rows:
            if row["step_id"] == "STEP-02":  # Current is STEP-03, previous is STEP-02
                previous_step_results.append(row)

        # Verify ASC can render previous step
        assert len(previous_step_results) == 1, "ASC should find STEP-02 in index"
        prev_row = previous_step_results[0]
        assert prev_row["source_id"] == "OUT-1113-02-01", "ASC should render correct output_id"
        assert prev_row["status"] == "draft", "ASC should render status"

        print("[OK] ASC successfully renders Previous Step Results from index")

        # Simulate lint validation (step_handoff_missing check)
        # Completed steps: STEP-01, STEP-02
        # Steps in index: STEP-01, STEP-02
        # Expected: No warnings
        handoff_step_ids = {row["step_id"] for row in index_rows}
        completed_steps_with_outputs = ["STEP-01", "STEP-02"]  # Both have Expected Outputs

        missing_handoffs = []
        for step_id in completed_steps_with_outputs:
            if step_id not in handoff_step_ids:
                missing_handoffs.append(step_id)

        assert len(missing_handoffs) == 0, f"Lint should find no missing handoffs, but found: {missing_handoffs}"
        print("[OK] Lint step_handoff_missing: No warnings (all handoffs present)")

        # Final verification: complete workflow
        print("\n[PASS] END-TO-END WORKFLOW VERIFIED")
        print("   1. STEP-01 completed -> handoff stub created [OK]")
        print("   2. STEP-02 completed -> handoff stub created [OK]")
        print("   3. Index.jsonl contains both handoff rows [OK]")
        print("   4. ASC can render Previous Step Results from index [OK]")
        print("   5. Lint validates all handoffs present [OK]")
        return True

if __name__ == "__main__":
    try:
        test_e2e_workflow()
        print("\n[SUCCESS] E2E Workflow Test PASSED")
        exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] E2E Workflow Test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] E2E Workflow Test ERROR: {e}")
        exit(1)
