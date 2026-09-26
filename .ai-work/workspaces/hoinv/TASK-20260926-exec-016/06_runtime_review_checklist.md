# Runtime Review Checklist — GAT/Durable Corrections

## Target
`docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` §§6.6, 6.9, and 7 only.

## Sources used
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/src/team-config.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/src/index.ts`
- Focused GAT team-config/tool tests
- `review_plan.md`

## Selected items
HC-01 through HC-09 from the HUMAN's explicit concern list; no exclusions.

## Excluded / N/A
- Entity-column map only: N/A because the scoped contracts expose no application entity/data-model columns; manifest/profile fields are checked as the equivalent interface field map.

## Breakdown

### RI-01 — HC-01 fallback scope
**Assert:** Target fallback wording equals the current loader's catch scope and does not imply Durable authorization.
**Method:** (1) Compare target §6.6 lines 239–260 to `team-config.ts` lines 124–147. (2) Compare target §§7.3/7.6 fallback authorization wording to Durable manifest authorization.
**PASS iff:** every loader read/parse/schema failure is described as GAT built-in selection; route failure is outside fallback; durable storage is not authorized solely by fallback membership.
**FAIL iff:** any listed failure is outside the catch, route failure is described as fallback, or fallback implies Durable authorization.
**N/A iff:** never.
**Evidence:** cited loci above.
**Verdict:** PASS

### RI-02 — HC-02 byte limit
**Assert:** Target states GAT's configurable UTF-8-byte contract, including default and both pre/post-read checks, without attributing that limit to Durable MiniMVP.
**Method:** Compare target §§6.5/6.9 with `team-config.ts` lines 124–139 and `index.ts` config/default lines 21–47, 657–680; compare Durable MiniMVP's absence of a manifest byte constant.
**PASS iff:** target distinguishes GAT's default 65,536-byte configurable limit from unspecified Durable limits and states actual UTF-8 byte enforcement.
**FAIL iff:** constant/scope/unit differs or is attributed to Durable.
**N/A iff:** never.
**Evidence:** cited loci above.
**Verdict:** PASS

### RI-03 — HC-03 route authority
**Assert:** Target distinguishes authorized member definition, effective GAT/DSH runtime route, immutable Durable profile binding, and continuation-provider mechanism.
**Method:** Diff target §§6.7, 7.2, 7.6 against Durable schema/profile/non-goals and GAT `childAgentOptions` + initializer loci.
**PASS iff:** manifest authorizes member route; GAT/DSH resolves and instantiates it; Durable persists/checks it but does not discover/fallback/select runtime routes; fresh/fork providers remain mechanism-only.
**FAIL iff:** authority is assigned to the wrong subsystem or effective route is conflated with continuation provider.
**N/A iff:** never.
**Evidence:** target lines 262–273, 299–313, 383–393; Durable lines 5–17, 59–67, 109–114; `index.ts` lines 83–116, 704–733.
**Verdict:** PASS

### RI-04 — HC-04 SOUL ordering
**Assert:** Target preserves Durable's literal SOUL placement while placing non-overridable host/GAT governance before editable SOUL.
**Method:** Compare target §7.4 lines 358–366 to Durable lines 62 and 88–90 and current GAT system-prompt contribution.
**PASS iff:** authority precedence is not presented as literal order; target requires one integration contract with host commands/governance before SOUL and SOUL before member/task context.
**FAIL iff:** target places SOUL after member/task context or allows SOUL to precede/override host governance.
**N/A iff:** never.
**Evidence:** cited loci above; `index.ts` lines 402–408.
**Verdict:** PASS

### RI-05 — HC-05 per-task loading
**Assert:** Target requires SOUL and bounded memory-index loading before every task, with only relevant memory items opened.
**Method:** Compare target §§7.4/7.5 to Durable lines 62–65, 88–104.
**PASS iff:** SOUL and index are per-task; item bodies are selective; per-turn reload is not claimed as current MiniMVP requirement.
**FAIL iff:** loading is one-time, per-session only, indiscriminate, or incorrectly per-turn mandated.
**N/A iff:** never.
**Evidence:** target lines 346–381; Durable cited loci.
**Verdict:** PASS

### RI-06 — HC-06 manifest snapshots
**Assert:** Target accurately distinguishes current live-manifest reload behavior from proposed Session-bound snapshot/digest integration.
**Method:** Compare target §§7.5/7.6 to Durable lines 33, 107 and GAT Enable-time loader call.
**PASS iff:** target says current Durable APIs reload live manifest; canonical snapshot is proposed; digest alone is insufficient unless atomically verified or snapshot-aware APIs accept it.
**FAIL iff:** target claims snapshot support exists or treats an unverified digest as sufficient authorization.
**N/A iff:** never.
**Evidence:** target lines 368–389; Durable lines 33, 107; `index.ts` lines 691–733.
**Verdict:** PASS

### RI-07 — HC-07 restart admission
**Assert:** Target makes restart revalidation an admission gate before resumed task or durable-context access.
**Method:** Compare target §7.5 item 9 and §7.6 profile/drift rules to Durable fail-closed profile/manifest behavior and GAT cold-resume behavior.
**PASS iff:** integration must reconcile child evidence and revalidate profile before first resumed task or durable access; failure surfaces failed/degraded state rather than silently continuing; wording remains proposed, not implemented.
**FAIL iff:** revalidation is optional/post-admission or claimed implemented in current GAT.
**N/A iff:** never.
**Evidence:** target lines 368–411; Durable lines 33, 67, 107; `tool-team.spec.ts` cold-resume test lines 1075–1094.
**Verdict:** PASS

### RI-08 — HC-08 conditional sharing
**Assert:** Target states global sharing only under explicit compatible authorization by every workspace and denies implicit runtime/team sharing.
**Method:** Compare target §7.3 to Durable lines 35–57 and 67.
**PASS iff:** every participating workspace explicitly declares global scope with same immutable profile; omitted scope stays isolated; no implicit memory copy; global storage does not imply GAT membership/session/mailbox/task sharing.
**FAIL iff:** sharing is unconditional, inferred by name/path alone, or copied automatically.
**N/A iff:** never.
**Evidence:** cited loci above.
**Verdict:** PASS

### RI-09 — HC-09 filesystem ownership
**Assert:** Target distinguishes logical member ownership from actual shared-filesystem enforcement.
**Method:** Compare target §§7.2/7.3/7.6 to Durable `working/` ownership and current GAT shared-checkout policy.
**PASS iff:** member-owned durable artifacts are exclusive by contract/API but ordinary shared file tools are not isolated/locked; integration must define mutation authority/protection/concurrency.
**FAIL iff:** target claims filesystem isolation/locking exists or leaves cross-member mutation/concurrency unaddressed.
**N/A iff:** never.
**Evidence:** target lines 299–344, 383–393; Durable lines 59–67; `index.ts` policy lines 49–56.
**Verdict:** PASS

## Execution result
- Headline: PASS
- Counts: PASS 9 / FAIL 0 / RISK 0 / QUESTION 0 / N/A 0 / NOT_CHECKED 0
- Evidence summary: all nine corrected concerns match the Durable MiniMVP and current GAT loader/tool behavior at the cited loci; no material discrepancy remains.

## Open questions
- None.

## Reference gaps
- GAT and Durable primary docs are not resolved by the current project Wiki Source Index; captured as CAP-016-01 and CAP-016-02.

## Learning-candidate hints
- None beyond the recorded retrieval gaps.
