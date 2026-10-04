# Durable binding reuse — proposal review

Date: 2026-10-04 (Asia/Tokyo). Status: source/design inspection; independent review and runtime qualification remain pending.

Recommendation: proceed with a bounded qualification of an additive, explicitly selected `@vuhoi/gat-durable-agent/execution-composition` entry. The proposal has a sound reuse boundary, but is not yet evidence that the current Host can satisfy every acceptance case without extensions.

The HUMAN selected planning an additive isolated-execution adapter while preserving the existing direct-continuable binding. This is planning direction, not implementation, deployment, canonical promotion or Mission Board execution approval.

## Findings and required refinements

| Priority | Finding | Evidence | Planning consequence |
| --- | --- | --- | --- |
| Blocking before implementation | Existing GAT approval selects direct-continuable binding; isolated execution was excluded from that implementation. | GAT `DETAIL_DESIGN.md` §5 opening and §8; `DURABLE_AGENT_INTEGRATION.md` approved WK baseline. | Add a separately reviewed execution-composition design delta; retain the existing contract and entry. HUMAN has selected this planning direction. |
| Blocking qualification | An assignment brief is not a Durable review packet. It has no explicit review-mode field, normalized TaskContract, completion proposal, criterion IDs, test receipts or authenticated machine-check attestations. | DSH `agent-team/src/execution-types.ts`; DA DD-06/DD-07; `review-packet.ts` ReviewPacket and `createReviewPacket`; Consumer `reviewContribution`. | Select an explicit host-owned reviewer role and exact packet input. Reuse the public packet builder and host ACL/digest checks. Never guess reviewer mode from name, prompt text or a generic role. Missing data rejects reviewer admission. |
| Blocking qualification | Awaited child creation is promising, but listener timing alone does not prove first-request admission, refresh frequency or recovery. | DSH Agent initialization awaits serial `agent/created`; execution manager installs an admission waterfall; loop assembles context before pre-step. | Test the real GAT execution manager and Loader with WK provider. Exercise listener registration orders, authority loss and request retry behavior. No loop patch or recursive assembly workaround. |
| Blocking qualification | Cleanup must be joined to GAT terminal settlement, not just eventual fiber disposal. Current GAT finalization awaits `closeContinuableChildren`; its supplied `releaseResources` callback currently releases Jobs. | DSH `agent-team/src/execution.ts` finalization; GAT `index.ts` host callback; `subagent/closing-child` extension. | Qualify an adapter-owned closing-child listener plus child/plugin disposal. A rejected or hung release must not become a successful binding cleanup receipt. Prove no self-drain deadlock during submission. |
| Required refinement | WK provision can reuse an active identical declaration and return the same ref. That is not permission for overlapping adapter owners. | DA DD-02/DD-04; WK `local-provider.ts` provision; GAT `ownership.ts`. | Reserve canonical workspace/name on the exact underlying provider before provisioning; retain reservation through physical cleanup. Distinct provider instances/single-host topology require deployment evidence. |
| Required refinement | WK reads are current per call, not pinned to the preceding catalog snapshot. Consumer tool records describe tools; they do not register or authorize execution. | DA DD-03; conflicts C-02/C-05; GAT tools and binder. | Adapter registers only its authorized read tool, checks selected IDs before and after await, and bounds complete serialized prompt/result. No DSH request-lease guarantee. |
| Required refinement | Restart from configuration must preserve persistent profile identity and cannot redefine the GAT roster. | GAT freeze §3/§8.3; DA DD-02 and provider profile-conflict checks. | Validate exact approved declaration against persisted provider profile and GAT live execution. Missing mappings/profile conflicts fail closed. Qualify changes that retain the same provider name versus remapping it; do not promise detection of every historical configuration change without an authoritative baseline. |
| Required refinement | Memory-free reviewer output still performs a provider snapshot read to authorize its ref. It does not guarantee transport freshness or remove other prompt owners. | Consumer `reviewContribution` calls `snapshot`; DA DD-07, C-07. | Permit the authorization call, but prove no member guidance/catalog/body or memory tools reach the reviewer. Inspect the whole first logged request and fresh Session ancestry. Retain GAT identity/task policy. |
| Deployment gate | Package names/versions and files do not prove the actual Web profile resolves compatible public artifacts. | DA AD-02, C-06; existing GAT package has only root/composition/provider exports and explicit host prerequisites. | Pin WK package bytes, public exports and selected host; qualify built imports. Prepare exact profile diff/storage effects/rollback only after technical acceptance. |

## Durable Agent design consulted

Original sources live under `/home/hoinv/work/dsh-durable-agent/docs/`:

- `DURABLE_AGENT_DESIGN_INDEX.md` §1–3: authority and implementation-family navigation.
- `DURABLE_AGENT_ARCHITECTURE_DESIGN.md` AD-02–AD-05: WK/DSH/LEG separation, one owner per fact, persistent identity versus conversation, selective memory, explicit composition.
- `DURABLE_AGENT_BASIC_DESIGN.md` BD-01–BD-05: interfaces, data ownership, shared task/fresh review and execution lifecycle.
- `DURABLE_AGENT_DETAIL_DESIGN.md` DD-01–DD-04, DD-06–DD-09, DD-11–DD-12: WK port/profile/ref/read/release, reviewer packet, DSH contrast, limits and unimplemented runner boundary.
- `DURABLE_AGENT_DETAIL_SOURCE_MAP.md`: WK-PORT/PROFILE/CONTEXT/CONSUMER/MUTATE/TASK/PACKET/REVIEW and DSH-BIND/GAT-MEMBER.
- `DURABLE_AGENT_DESIGN_CONFLICTS.md`: C-01/02/03/05/06/07/10/11/17. These remain open records; this review does not close them.
- `DURABLE_AGENT_DESIGN_MISSION_DELTAS.md` §3–5: accepted capability versus target task runner, binding and live deployment.

GAT sources consulted: `docs/gat-design/BASIC_DESIGN.md` §7, §10–12 and production delivery; `DETAIL_DESIGN.md` DD-09/DD-15/DD-16, §5, §7 and §8; `DURABLE_AGENT_INTEGRATION.md`; `GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §2–4, §8 and §12. Current metadata summaries lag several appended sections; direct current document sections supplied the comparison.

No official design, provider source, DSH source, roster, profile or existing mission ledger changed during this review. See `source-baseline.json` for exact bytes of planning inputs.

## Planning lessons

- `/home/hoinv/.agents/skills/dsh-wbs-build/references/planning-lessons.md`: prefer existing operations; separate execution-owned output quality from task completion; qualification is a hard prerequisite, not an assumption.
- DA `context-lessons/lessons/shared-versioned-task-contract.md` (advisory): author and reviewer consume the same external specification/packet; no invented reviewer criteria or author self-acceptance.
- DA `context-lessons/lessons/close-blocking-open-points-before-implementation.md` (advisory): isolate demonstrated feasibility questions and do not dispatch implementation while they remain open.

These are planning inputs only and are not implementation/test specifications. This is a new integration mission; no existing Mission Board or prior GAT mission is revised.
