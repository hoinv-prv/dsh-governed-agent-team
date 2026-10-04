# Qualification matrix — STEP-02 checkpoint

Date: 2026-10-04. Candidate: isolated Host c1157f7e, public WK package bytes and experimental source recorded in `qualification-environment.json`. Author evidence only; independent qualification acceptance has not occurred.

| Requirement | Disposition | Evidence / limit |
| --- | --- | --- |
| Actual isolated GAT assignment/admission and real WK service/Consumer through Loader | Demonstrated for this fixture | Public GAT wrapper and execution manager, Loader YAML, public LocalDurableAgentProvider/Consumer; only model transport mocked. Test-only aliases are not a built production-install qualification. |
| Bootstrap/nonexecution bypass; binding before first execution request | PASS, narrow case | Binding map empty after bootstrap; awaited creation sees provisioning; active checks surround Consumer call before first model prompt. |
| Guidance plus selected catalog, no eager memory body | PASS, narrow case | One explicitly selected catalog item in first prompt; no memory read tool/body is installed by this experimental fixture. General filtering/bounds/unauthorized selection remain unqualified. |
| One owner contribution, other prompt retained | PASS, narrow case | Both request prompts retain Host identity and have one WK marker. |
| Fresh context on actual retry | **NG — scope blocker OP-024-03** | Two execution requests, one assembly. Assembled context revision 1; fresh public Consumer context revision 3 after approved fixture commit; retry contains catalog-version-one and revision 1, not catalog-version-two. Final contract assertion fails. |
| Logged reconstruction/persisted first prompt | PASS for observed stale bytes; freshness NG | Public Session snapshot and persisted read after cancellation both contain first catalog and omit changed catalog. Transport received those same stale bytes. |
| Normal cancellation joins release and terminal closure | PASS, narrow case | Cancelled terminal phase; public Consumer snapshot rejects UNAUTHORIZED_REFERENCE after cancellation; persisted Session readable. No cleanup failure/hang/deadline/self-drain qualification follows from this. |
| Current Host default retry contract | PASS baseline | Existing `system-prompt-admission.spec.ts`: 27 tests pass, including retained admitted prompt without repeated assembly. |
| Zero model requests on binding failure, async revocation, identity replacement/generation loss | Unqualified | Production feasibility already blocked; prototype is not an accepted guard implementation. |
| Overlap exclusion and failed physical release quarantine | Unqualified | Seed owner released before single execution provision. No overlap or failing-release fixture. |
| Reviewer packet derivation, exact assignment/candidate ACL and whole-prompt memory exclusion | Unqualified | WK public exports available; authenticated current Host packet derivation remains open. No generic reviewer fallback chosen. |
| Live cold recovery, profile mismatch and terminal denied resume | Unqualified | No restart matrix claimed from normal cancellation. |
| Existing direct adapter regression, built imports, typecheck and keyless snapshot | Not run | Production changes remain gated by missing current-Host operation. |
| Independent qualification/design/source review | Not performed | Producer did not generate an independent verdict. |

## Test receipts

`verification/qualification-attempt-08.log`: 1 characterization test passed, 1 required freshness contract failed, process exit 1. Failure is the expected detected contract gap, not technical acceptance. `qualification-attempt-08.json` binds exact test/config hashes. `qualification-observation.json` contains actual prompts, both Consumer contributions, public Session events and persisted events.

`verification/host-admission-baseline.log`: 27 existing tests passed, exit 0. Its config/source hashes are included in the final checkpoint manifest. Earlier attempts retain launcher/fixture failures separately; they do not count as requirement evidence. Attempt 06/07 already reproduce stale retry; attempt 08 additionally proves persisted Session bytes and normal cancellation/release on the final experimental source.

## Disposition

STEP-02 is awaiting the HUMAN scope decision in `host-prerequisite-proposal.md`. AIP remains active; no STEP-03 acceptance, STEP-04 production implementation, deployment or mission dispatch has occurred. Retry freshness cannot be weakened silently. Remaining matrix rows require actual qualification after the prerequisite decision.
