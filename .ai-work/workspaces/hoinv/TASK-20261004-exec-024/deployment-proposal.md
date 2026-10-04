# Deployment proposal — AIP-EXEC-024 (not activated)

This is a concrete proposed plugin configuration and approval input. The final source/artifact has passed independent review; the technical handoff records exact limits. No live profile/provider/storage change has been applied.

## Exact target and entry

Proposed qualification-compatible runtime: DSH c1157f7ed448b40c463c1a43fa595b12294fd50d (0.1.7-rc.2), its current public GAT execution service/initializer, and WK public API1 a8e215433ae050e36e0ba27205701be1a5f114a1 (package0.1.0). The old direct entry remains on Host5c02ce9f3e44dfce3f87498f65cf684194ad4572. Do not infer both Host APIs from the shared package version.

The reviewed joint artifact is already built/packed via scripts/assemble-durable-agent.mjs: `verification/public-artifact/final-attempt-01/packed/vuhoi-gat-durable-agent-0.1.0.tgz`, SHA256 `7f7848ce2eff8f07f01ea3bd778571083441d7db23783e3ddb54e2f80c695065`. Assembly receipt SHA256 `f7f54e6445e210be5fa50d0e93756d41a6498d9aaf090319c978c763f5fb15a7`; packed receipt SHA256 `2948c0a7e96c13542f8d07a9059b0b0b7d835efe15ee16be63121090e3678ac9`. Actual built checks retain Host Cordis4.0.4 and WK own Cordis4.0.2; no dependency override is proposed. Use existing GAT Team initialization and tools, then named @vuhoi/gat-durable-agent/provider and @vuhoi/gat-durable-agent/execution-composition. WK is an exact independently versioned runtime dependency, externalized; its provider/Consumer/execution owner must resolve the same module. No Host version exemption is proposed.

## Proposed task configuration

Proposed canonical workspace: /home/hoinv/work/dsh-governed-agent-team (existing project root). Proposed fresh workspace worker is named worker, provider deepseek-official, model deepseek-v4-flash, description Task memory worker, prompt Role instructions only. The Host roster must use the same approved name/model route and fresh sessions. Configuration assertions dedicatedProvider:true/singleHostWorkspace:true must be independently established by the operator, not inferred from paths or names.

Use required limits maxBodyBytes4096, maxResultBytes8192, maxSelectedItems8, maxReadCalls8, maxReadResultBytes32768. Match the README complete YAML shape. Initial live mode is task only; task briefs select explicit approved durable-memory:<id> references. No inferred semantic retrieval, eager catalog/guidance/body, memory system prompt, candidate/write tool or model-owned declaration configuration is proposed.

## Reviewer workflow gate

Reviewer mode additionally requires an approved concrete Host implementation of gatDurableReviewInput. It must resolve exact revisioned review-packet inputs from approved TaskContract/CompletionProposal, exact distinct candidate/reviewer associations, actual test receipts and ACL byte readers; persist native-call-linked audit and notify synchronous subscribeRevocation BEFORE authorization/candidate/ACL withdrawal. Service replacement must cut off the exact Agent. No fabricated receipts/criteria, ordinary-memory fallback, second runner or final acceptance engine is supplied by this plugin. Qualification fixtures demonstrate the API; a live no-op assertion/subscription is not approved.

## Storage effects and controls

After authorized activation, provider provisioning/read operations can create or reopen WK-owned member state under the approved workspace and update its owned lease/reference lifecycle. Native task/reviewer tool arguments/results remain in normal Session JSONL logs. Approved-memory commit/promote workflows remain external operations. Provisioning bootstrap sessions is skipped. No DSH/Core/Team/WK persistence schema changes or cross-process lock recovery are proposed.

Establish exclusive dedicated provider + one Host process per canonical workspace, approve actual WK storage resolution/permissions, approved memory provenance, roster/model routes and prompt/tool owners before activation. Cold live checkpoint recovery must validate exact persisted assignment/profile/canonical configuration and current Host authorization before admission. Qualified bounded rebind does not prove operating-system crash/lock recovery.

## Rollback

Remove/disable the execution composition through the existing profile operation and await physical cleanup before restarting or replacing the dedicated provider. Cutoff synchronously stops admission and exact Agent activity, then joins admitted callbacks/release. Failed cleanup retains quarantine; do not bypass it by admitting another owner. Preserve native Session evidence and WK data; no reset/delete is part of rollback. Existing direct profile remains a separately qualified option on its compatible Host.

Activation requires HUMAN approval of the exact final artifact, concrete provider/profile/storage effects/topology and reviewer workflow if enabled. This AIP implements and qualifies the plugin; it does not activate it.


## Concrete configuration for approval

```yaml
# Add to the approved current Host profile only after activation approval.
# Existing current GAT core/tools/roster initialization must already be present.
- id: gat-durable-provider
  name: '@vuhoi/gat-durable-agent/provider'
- id: gat-durable-execution
  name: '@vuhoi/gat-durable-agent/execution-composition'
  config:
    workspace: /home/hoinv/work/dsh-governed-agent-team
    dedicatedProvider: true
    singleHostWorkspace: true
    members:
      - mode: task
        declaration:
          name: worker
          scope: workspace
          context: fresh
          provider: deepseek-official
          model: deepseek-v4-flash
          description: Task memory worker
          prompt: Role instructions only
    limits:
      maxBodyBytes: 4096
      maxResultBytes: 8192
      maxSelectedItems: 8
      maxReadCalls: 8
      maxReadResultBytes: 32768
```

This is an uninstalled proposed fragment; operator-approved current Loader profile placement and matching fresh GAT roster are required. Confirm concrete trusted topology/provider storage and approved selected memory IDs before activation. No reviewer mode is proposed for initial activation. Current full-library public declaration checks pass; old direct public consumer uses its supported skipLibCheck:true, with existing duplicated Schemastery diagnostic retained. The current aggregate Host type graph remains NG130 generated remote/client diagnostics. Those limitations are not silently repaired by activation.
