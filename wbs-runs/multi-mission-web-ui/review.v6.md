# Review candidate multi-mission-web-ui, revision 6

- Plan: `wbs.v6.json`
- Exact SHA-256: `a484fdda4d896f3430c7501b5bbc2c8cbf4b9166d0f2ead3d2133ea0ebe59add`
- Validation: WBS helper structural validation and workspace inspection passed.
- Dependency order is unchanged from revision 5.

## Why revision 6 is required

The first revision-5 AIWS recovery command ran exactly as approved but failed with exit 127: `python: command not found`. No allocator, AIP, workspace, or product mutation occurred from that failed command. The relevant AIWS tools declare `#!/usr/bin/env python3`.

## Exact delta from revision 5

- Replaces every approved AIWS command executable token from `python` to `python3`.
- Adds one final 30-minute `aiws-governance-recovery` attempt; no third recovery attempt is available.
- Total task attempts: 10 → 11. Effort ceiling: 650 → 680 minutes.
- Product scope, partial Web bytes, accepted core evidence, external verification commands, human gates, and non-goals are unchanged.

Approval authorizes the corrected AIWS recovery commands, final Web attempt, and already-declared downstream integration/final gates. It does not activate GAT in the live Web profile or modify AIWS Truth/Wiki/tooling.
