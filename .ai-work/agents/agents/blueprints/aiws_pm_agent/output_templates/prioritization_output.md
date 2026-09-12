# Prioritization Output

> Output template for the PM Agent (optional output; produced in priority review mode). The agent
> PROPOSES priority; the "HUMAN Decision" column stays blank until HUMAN confirms. See
> docs/reference_content/prioritization_guide.md (reference seed). Mapped from PM_Agent_Blueprint/templates/PRIORITIZATION_GUIDE.md
> (template_version v0.1).

## 1. Metadata
- prioritization_id:
- created_by_agent:        <!-- instance_id -->
- source_request:
- source_inputs:           <!-- Wiki-first context + task list/AIP verified -->
- created_at:
- review_status:           <!-- pending / approved / adjusted -->

## 2. Priority Factors Considered
<!-- value / urgency / dependency / risk / effort / confidence / explicit HUMAN priority -->

## 3. Proposed Priorities

| Task ID | Current Priority | Proposed Priority | Reason | Risk if Deferred | HUMAN Decision |
|---|---|---|---|---|---|

<!-- "Proposed Priority" is a recommendation. "HUMAN Decision" stays blank until HUMAN confirms. -->

## 4. Recommended Next Best Actions
<!-- Recommendation only; the agent does not execute. -->

## 5. Open Questions / Unclear Ownership

## 6. HUMAN Decisions Needed
