# Control failure — attempt-gat-threat-001

Outcome: FAILED before valid independent acceptance.

The task authored candidate threat/vector files while the fixed Workspace Active Step Context still pointed to historical STEP-03. A fresh durable independent reviewer refused to open those inputs and correctly required `run_aip.py step AIP-EXEC-004 --step STEP-06` plus rebuilt ASC. WBS revision 16 does not grant that command or its `.current_step.json` / `00c_active_step_context.md` writes.

The earlier subagent review and its REVISE findings are retained, but its post-edit rereview did not complete. Current candidate bytes are retained as unaccepted work; no hash, PASS, or HUMAN acceptance is claimed. No package/product code was dispatched.

A reviewed WBS revision is required to add exact AIWS step-transition commands and paths at STEP-06 through STEP-11, preventing the same control mismatch at later phase boundaries. Attempt charge 20 remains consumed.
