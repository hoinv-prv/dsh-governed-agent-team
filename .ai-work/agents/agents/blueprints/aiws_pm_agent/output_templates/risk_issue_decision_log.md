# Risk / Issue / Decision Log

> Output template for the PM Agent (required output). Fill per run. The Decision Log RECORDS HUMAN
> decisions — the agent does not make them. Mapped from PM_Agent_Blueprint/templates/
> RISK_ISSUE_DECISION_LOG_TEMPLATE.md (template_version v0.1).

## 1. Metadata
- log_id:
- created_by_agent:        <!-- instance_id -->
- period / scope:
- source_inputs:           <!-- Wiki-first context + task/meeting/issue data verified -->
- created_at:
- review_status:           <!-- pending / approved / adjusted -->

## 2. Risk Log

| Risk ID | Description | Probability | Impact | Severity | Proposed Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|

## 3. Issue Log

| Issue ID | Description | Severity | Impact | Current Action | Owner | Due | Status |
|---|---|---|---|---|---|---|---|

## 4. Blocker Log

| Blocker ID | Description | Blocking Task | Required Action | Owner | Escalation Needed | Status |
|---|---|---|---|---|---|---|

<!-- "Escalation Needed" is a recommendation; HUMAN decides whether to escalate. -->

## 5. Decision Log

| Decision ID | Decision | Context | Options Considered | Decided By | Date | Impact |
|---|---|---|---|---|---|---|

<!-- "Decided By" must be HUMAN for any official decision; the agent only records it. -->

## 6. Action Item Log

| Action ID | Action | Owner | Due | Related Risk/Issue/Decision | Status |
|---|---|---|---|---|---|
