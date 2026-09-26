# Incident — prohibited DSH read-boundary access

Status: execution stopped; HUMAN disposition required.

While building candidate WBS revision 25 after policy attempt 2 exhausted its task cap, the coordinator invoked the globally installed WBS build helper at `/home/hoinv/.agents/skills/dsh-wbs-build/scripts/wbs.mjs` for read-only validate/order/hash operations. Those invocations returned no output and exit 0. A subsequent `readlink -f` showed that path resolves to `/home/hoinv/deepseek-harness/.agents/skills/dsh-wbs-build/scripts/wbs.mjs`.

This crossed the mission's explicit no-DSH-checkout-access boundary. No DSH source was modified, built, installed, started, imported into `packages/gat`, or used for runtime compatibility claims. Nevertheless, read access itself was prohibited, so execution is stopped rather than minimized or concealed.

Affected claims:
- Candidate v25 has **not** been labeled helper-validated.
- Existing accepted standalone product bytes/tests preceding the incident remain byte-addressed, but continuation requires HUMAN disposition of the boundary incident and exact v25 approval after independent review.
- No v25 execution selection or policy attempt 3 has occurred.
