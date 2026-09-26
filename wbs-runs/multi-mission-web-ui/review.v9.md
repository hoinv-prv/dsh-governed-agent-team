# Review candidate multi-mission-web-ui, revision 9

- Plan: `wbs.v9.json`
- Exact SHA-256: `382df5570471f84d28e95b0df66ac13102e4db00d6004552c1cdfe6988c66fff`
- WBS helper validation/order completed with exit 0.

## Why revision 9 is required

Revision-8 recovery succeeded through reset, clean, regeneration, and installation. Canonical verification reached focused Vitest and then stopped with 151 passed / 4 failed.

Static diagnosis shows four test defects rather than a demonstrated production defect:
- Core noncontiguous-revision fixture must keep approval metadata internally valid so continuity validation is reached.
- Core synchronous missing-mission Remote throw must be passed to `toThrow` as a function.
- Two Web assertions require accessible/semantic matching because localized status and revision content is split/adjacent in the DOM.

## Exact delta from revision 8

- Adds one fifth/final core attempt, limited to the two diagnosed core test fixtures plus independent review.
- Adds one third/final Web attempt, limited to the two diagnosed Web DOM assertions plus independent review.
- Adds one third/final integration attempt using the already-approved dedicated-worktree reset/clean/regenerate/install/verify sequence.
- Total attempt ceiling: 12 → 15. Effort ceiling: 740 → 980 minutes.
- Product requirements, runtime commands/effects, live-profile prohibition, final report, AIWS lint, and human acceptance are unchanged.

Approval authorizes these bounded test repairs and one final canonical verifier attempt. Any production change or fourth integration attempt requires another reviewed revision.
