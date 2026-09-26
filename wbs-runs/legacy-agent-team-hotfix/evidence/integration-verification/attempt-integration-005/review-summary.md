# Integration attempt 5 preflight review evidence

## Trigger

Final-review attempt 1 (`subagent:92b95a8c-48ba-47b9-96bf-574707863174`) returned `insufficient_evidence` because the current English approval label (`Import approved plan and approve`) contradicted the dashboard golden (`Approve current plan`) and verifier/review evidence was not durably persisted.

## Recovery review

The existing dashboard Missions golden delta was independently reviewed by `subagent:efa9806e-4e50-4588-8601-7a3b0d4ce587` with verdict PASS: the Missions heading, Add Mission button, and No missions yet notice exactly match `TeamAction.tsx` ordering and English locales.

For revision 8, coordinator inspection confirms the additional golden change is limited to the approval button accessible name/text and exactly matches:

- `packages/web/src/client/locales.ts`: `approvePlan: 'Import approved plan and approve'`;
- `packages/web/src/client/TeamAction.tsx`: the button renders `t('approvePlan')`.

No product source behavior is changed in this recovery. Canonical verifier output for attempt 5 is persisted in adjacent `verifier.log` by the approved tee command.
