# Review candidate multi-mission-web-ui, revision 8

- Plan: `wbs.v8.json`
- Exact SHA-256: `f6267a214279d655284268d7a8cc6f571a8ac52cc53062097e63a11e7f6b9955`
- Validation: WBS helper structural validation and workspace inspection passed.
- Product implementation, accepted core/Web reviews, AIWS scope, and final acceptance gate are unchanged.

## Why revision 8 is required

Integration attempt 1 stopped at its first required command. The installer rollback validates the current source against the old compatibility payload before it can clean the target, so changed mission source caused:

```text
gat-installer: payload hash mismatch for packages/core/src/index.ts
```

Exit code was 1. No compatibility regeneration, installation, or verifier command ran.

## Exact delta from revision 7

- Replaces rollback with two explicit commands limited to the dedicated verification worktree:
  1. `git -C <dedicated-worktree> reset --hard c291e7961a515f6d7af9304e7fd1d257929aef26`
  2. `git -C <dedicated-worktree> clean -fdx`
- Then retains the same compatibility generation, installation, and canonical verifier commands.
- Adds one final integration attempt; no third attempt is available.
- Total attempts: 11 → 12. Effort ceiling: 680 → 740 minutes.
- Main DSH checkout remains untouched; destructive cleanup is constrained to the dedicated verification worktree supplied for this purpose.

Approval authorizes only that dedicated-worktree reset/clean recovery and the already-declared downstream commands. It does not activate or restart the live Web GUI.
