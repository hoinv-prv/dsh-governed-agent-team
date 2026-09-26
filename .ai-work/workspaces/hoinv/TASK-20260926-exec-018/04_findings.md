# Findings

## STEP-00 — Selective review confirmation

The HUMAN confirmed an evidence-bound comparison of `DURABLE_AGENT_TEAM_REFERENCE.md` with the current GAT reference. Only material, non-duplicative design deltas should be incorporated, and target contracts must remain distinguished from installed behavior.

Evidence: current-session HUMAN confirmation on 2026-09-26.

## STEP-01 — Material delta analysis

### Accepted target-architecture deltas

1. **Disabled-state boundary:** no Durable Agent catalog/context is injected while the Session Team is disabled; files on disk remain inert and never authorize dispatch.
2. **Bounded authorized catalog:** derive discovery metadata only from the enabled authorized roster; include name/description/scope/capabilities/status, exclude full prompt/SOUL/memory, and never treat discovery as authority escalation.
3. **Delegated-context invariants:** inject only the selected target's SOUL and relevant memory; reload SOUL/index per task; verify profile binding; keep memory advisory; require explicit task authority.
4. **Learning/promotion boundary:** selected reusable findings begin as candidates and are routed separately to agent memory, project knowledge, guideline/process review, or discard; duplication/conflict and HUMAN/authorized review are mandatory.
5. **Durable-file security:** fail closed for profile conflicts and malformed/oversized/NUL/non-file/symlinked controlled files; secrets are prohibited in profiles, SOUL, memory, catalogs, messages, and task artifacts.

### Accepted operational guidance

- Inspect roster source and diagnostics after Enable; high-governance work may require exact workspace-manifest provenance and reject built-in fallback.
- Before delegation verify enabled/live roster, role fit, explicit objective/scope/output/constraints/verification, governance gates, write-scope coordination, and independent reviewer separation.
- Provide a concise `AGENTS.md` pointer and an adoption/acceptance checklist rather than copying the full external document.

### Duplicate — do not repeat

- Manifest path/schema, route preflight, partial provisioning.
- Manifest/profile authority split and storage-not-activation rule.
- Fallback members not automatically durable-authorized.
- Shared checkout and advisory write scopes.
- One-way Enable and new-Session reload behavior.

### Unsupported — preserve as proposed

- Live GAT use of `storage_scope` or global-agent discovery.
- A finalized literal prompt ordering.
- Session-bound immutable manifest snapshot authorization.

### Contradictions to retain as explicit gaps

- Exact SOUL placement versus current GAT system-prompt assembly.
- Runtime fallback roster versus Durable Agent manifest authorization.
- Session snapshot authorization versus current live manifest reload.
- Global scope intent versus current GAT strict parser rejection.

## STEP-02 — Applied design deltas and review corrections

Updated `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` with AIP-EXEC-018 attribution and concise sections for:

- disabled-state authorization and bounded discovery catalog;
- delegation readiness and target-only context assembly;
- learning-candidate and promotion boundaries;
- target workspace adoption acceptance;
- controlled-file validation and secret handling;
- source and maintenance mapping.

Independent review corrections:

- security/authorization failures now fail closed; degraded continuation is limited to explicitly surfaced lifecycle failure;
- file validation is stated per file type rather than applying every condition uniformly;
- absence of locking/CAS is described as a specification gap, not an explicit MiniMVP statement;
- failure rules are labeled target contract;
- adoption checks separate current bridge preparation from installed integration acceptance.

## STEP-03 — Final verification

- Final independent focused review found no remaining material discrepancy.
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` contains AIP-EXEC-018 attribution, §§7.9–7.12, and the external source mapping.
- `git diff --check` passed for the document and task artifacts.
- AIWS scoped task lint passed with 0 errors and 0 warnings.
- CAP-001 was deferred to BL-018-CAP-001 for separate HUMAN curation; no Wiki or Truth was changed.
- No unresolved open point remains.
