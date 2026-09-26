# Governance contracts review — changes required

Independent review confirmed five prior findings closed. One material native Mission mismatch remains:

- Current normalized implementation invents Mission fields `planRevision`, `planPhase`, `planHash`, `approvedPlanHash`, and `snapshotHash` instead of accepting the pinned DSH Mission shape `{id, revision, title, objective, status, plan, approval?: {approvedRevision}}`.
- A distinct adapter-normalized Mission contract must bind native Mission identity/current revision/acceptable status and adapter-computed snapshot hash; bind native approval `approvedRevision` plus adapter-computed approval snapshot hash; require approval revision equals current Mission revision; preserve mapping identity/revision; normalize absent/stale/mismatch to `NATIVE_MISSION_APPROVAL_STALE` without claiming DSH admission enforcement.

The five-test command pass remains preserved but cannot justify acceptance. Both governance attempts are charged; a reviewed WBS revision is required.
