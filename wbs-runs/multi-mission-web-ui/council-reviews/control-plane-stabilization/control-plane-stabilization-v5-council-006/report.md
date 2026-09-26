# Council Review Report

- **Review:** `control-plane-stabilization-v5-council-006`
- **Verdict:** `needs_revision`
- **Confidence:** `high`
- **Decision owner:** `human: HUMAN-current-user`
- **Authority:** Advisory evidence only; this report does not accept, merge, deploy, publish, activate, or modify the reviewed artifact.

## Scope and immutable identity

Determine whether control-plane-stabilization-design.v5.md corrects all run-004/run-005 verified findings and earlier observations and defines the smallest feasible procedural fail-closed pre-charge admission design without claiming non-bypassable runtime enforcement, elimination of the irreducible TOCTOU race, invented authority, hidden attempt cost, weakened evidence, or an unsupported runtime service. Review exact pinned bytes only; advise whether revision is required before any WBS build.

Modes: `design`, `governance`.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v5-council-006",
  "artifacts": [
    {
      "artifact_id": "design-v5",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v5.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/design-v5",
      "sha256": "72277a8fae125305266a48c5de5122e145a7c72cd12fd949f19b7d40ed8a7aec",
      "size_bytes": 34842,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 408
        }
      ]
    },
    {
      "artifact_id": "sanitized-design-v5",
      "role": "sanitized",
      "source_artifact_id": "design-v5",
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v5.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/sanitized-design-v5",
      "sha256": "72277a8fae125305266a48c5de5122e145a7c72cd12fd949f19b7d40ed8a7aec",
      "size_bytes": 34842,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 408
        }
      ]
    },
    {
      "artifact_id": "repo-rules",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/AGENTS.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/repo-rules",
      "sha256": "9260216bebe60f86e08e3b745a4d822afd0120ce560a631285d17a3b59221177",
      "size_bytes": 10570,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 134
        }
      ]
    },
    {
      "artifact_id": "aiws-architecture",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/aiws-architecture",
      "sha256": "5e4c399d63f7c066db471918961288bc9bfc8cac24334e7c7f9ea28031b54ff9",
      "size_bytes": 18303,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 28,
          "end_line": 220
        },
        {
          "start_line": 320,
          "end_line": 430
        }
      ]
    },
    {
      "artifact_id": "runtime-review-method",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/runtime-review-method",
      "sha256": "fb8a49d426a6b98c7d1525a4a46e1905b40c08d98981ac99ac4f40e9a3bf1ffe",
      "size_bytes": 11454,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 20,
          "end_line": 108
        },
        {
          "start_line": 133,
          "end_line": 146
        }
      ]
    },
    {
      "artifact_id": "gat-proposal",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/gat-proposal",
      "sha256": "dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee",
      "size_bytes": 66815,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 13,
          "end_line": 64
        },
        {
          "start_line": 92,
          "end_line": 205
        }
      ]
    },
    {
      "artifact_id": "failure-model",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/failure-model",
      "sha256": "35865c65ffb388eaded796703b1530f17e2d0879c7889d121539c1b4c5ba324e",
      "size_bytes": 16931,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 147
        }
      ]
    },
    {
      "artifact_id": "council-contract",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/contracts.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/council-contract",
      "sha256": "24252c322bc43eaec3ad38f77ae79653ffc3a404b31da6ea586af0e5abfa6c60",
      "size_bytes": 24858,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 13,
          "end_line": 107
        }
      ]
    },
    {
      "artifact_id": "council-routing",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/risk-and-routing.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/snapshots/council-routing",
      "sha256": "c946c21caeeee25e460eacacb1466f9371f2d7534ed18b5c8bfbd61ee4d205e8",
      "size_bytes": 6123,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 45
        }
      ]
    }
  ]
}
```

## Routing, budget, and degradation

```json
[
  {
    "invocation_id": "inv6-auth-001",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v41",
    "attempt": 1,
    "packet_sha256": "62b2b5cde96eb78495339ca4b76ae883a8c4117871f4b81e146a3437ee1fc75b",
    "restriction_mode": "prompt-only",
    "capabilities": {
      "persona": false,
      "tool_filter": false,
      "output_schema": false
    },
    "status": "completed",
    "failure_code": null
  },
  {
    "invocation_id": "inv6-adv-001",
    "lane": "internal-adversarial",
    "role": "internal-reviewer",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "1ad8d2fd407392167f6c256ef4495fc83788e0af44423630477bd660318b4776",
    "restriction_mode": "prompt-only",
    "capabilities": {
      "persona": false,
      "tool_filter": false,
      "output_schema": false
    },
    "status": "completed",
    "failure_code": null
  },
  {
    "invocation_id": "inv6-ext-001",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "754e626ef401c0ddde4d7d42d4537f2abf0ec19ec0cdb3fd5e8a35b39002ba39",
    "restriction_mode": "prompt-only",
    "capabilities": {
      "persona": false,
      "tool_filter": false,
      "output_schema": false
    },
    "status": "failed",
    "failure_code": "schema_invalid"
  },
  {
    "invocation_id": "inv6-ext-002",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt5",
    "attempt": 2,
    "packet_sha256": "754e626ef401c0ddde4d7d42d4537f2abf0ec19ec0cdb3fd5e8a35b39002ba39",
    "restriction_mode": "prompt-only",
    "capabilities": {
      "persona": false,
      "tool_filter": false,
      "output_schema": false
    },
    "status": "completed",
    "failure_code": null
  },
  {
    "invocation_id": "inv6-chair-001",
    "lane": "chairman",
    "role": "chairman",
    "provider": "openai-codex",
    "model": "gpt-5.6-terra",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "5aebc606b91780b78b8f4b7e920e6eccfb884315abc9391a25a37edcb596c469",
    "restriction_mode": "prompt-only",
    "capabilities": {
      "persona": false,
      "tool_filter": false,
      "output_schema": false
    },
    "status": "completed",
    "failure_code": null
  }
]
```

```json
{
  "maximum_model_calls": 8,
  "initial_lane_calls": 3,
  "retry_allowance": 3,
  "reserved_chairman": 1,
  "reserved_adjudicator": 1,
  "worst_case_required": 8
}
```

```json
[
  {
    "degradation_id": "DEG6-001",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-authority",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG6-002",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-adversarial",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG6-003",
    "kind": "prompt_only_read_only",
    "affected_lane": "external-outside-view",
    "detail": "Read-only restrictions were prompt-only; initial envelope was schema-invalid and one typed retry succeeded.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG6-004",
    "kind": "unknown_cost",
    "affected_lane": "all",
    "detail": "Duration, token and cost telemetry were unavailable.",
    "verdict_consequence": "pass_with_notes_at_best"
  }
]
```

## Findings and deterministic verification

| ID | Severity | Verification | Claim |
|---|---|---|---|
| `r6adv001-f1` | `high` | `confirmed` | The AdmissionBundle contract has no field or receipt for P13's exact HUMAN WBS decision or P15's HUMAN bootstrap decision ID and raw hash; prepared_from.decisions_sha256 binds only an undifferentiated artifact hash, so a sealed READY bundle cannot itself identify the authority records those invariants require. |
| `r6adv001-f2` | `high` | `confirmed` | P3 validates only the pre-commit execution.json, while the commit protocol writes structurally new attempt, boundary, and charge data without requiring strict validation of the exact post-write candidate bytes before the charge or a strict PASS before dispatch. |
| `r6adv001-f3` | `high` | `confirmed` | The fallback rule requires only a distinct invocation identity and does not require the fallback's provider/model route family to preserve the two-family diversity required for high-risk review when either primary lane is lost. |
| `r6auth001a1-f1` | `medium` | `confirmed` | Section 5.1 forbids every mutable mission-control write in NOT_READY, READY and EXPIRED, but the mandatory abort path in Section 5.2 step 3 requires the coordinator to append an AdmissionInvalidation record in exactly those states, and Section 10 lists AdmissionInvalidation among generated or mutable mission-control artifacts owned by the coordinator through an approved append operation; no exception, owning command or receipt is declared for that write. |
| `r6auth001a1-f2` | `medium` | `confirmed` | Section 7.1 requires the HUMAN ceiling/reallocation and contingency decision to be bound to the successor WBS's exact revision and SHA-256 before that WBS may be built or admitted, while Section 16 makes the HUMAN selection of that same ceiling/contingency policy a precondition for building the WBS; because the revision and hash exist only after the WBS bytes are authored and the design states no ordering or provisional-binding rule, the two entry gates are mutually blocking. |
| `r6auth001a1-f3` | `medium` | `confirmed` | P8 asserts as an admission invariant that a delegated subagent cannot charge, but Section 5.3 concedes that no pinned Source of Truth identifies a non-bypassable native charge entry point and claims only procedural fail-closed governance; the design names no existing guard that denies the version-guarded execution.json charge write to a delegated writer, so P8 records an unconditional capability denial that its own topology observation does not establish. |

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v5-council-006",
  "executor": "parent-orchestrator",
  "artifact_manifest_sha256": "b8bde6fc86f2325ba7b26cf0cd93a56a8756513c89ef3e1218fef70e99d961fa",
  "records": [
    {
      "verification_id": "verify-all-findings",
      "finding_ids": [
        "r6auth001a1-f1",
        "r6auth001a1-f2",
        "r6auth001a1-f3",
        "r6adv001-f1",
        "r6adv001-f2",
        "r6adv001-f3"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "confirmed",
      "exit_code": null,
      "output_excerpt": "All six normalized findings confirmed against immutable design-v5.",
      "reason": "Each claimed required binding, ordering rule or procedural qualification is absent as stated.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v5",
          "sha256": "72277a8fae125305266a48c5de5122e145a7c72cd12fd949f19b7d40ed8a7aec"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v5",
          "sha256": "72277a8fae125305266a48c5de5122e145a7c72cd12fd949f19b7d40ed8a7aec"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/verifier/verify-all-findings.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v5-council-006/verifier/raw/verify-all-findings.txt",
      "raw_output_sha256": "acae751aa46cba7bce1d8f7dc64122a4532da1d1563d43b0c56f1a9901a48281",
      "raw_output_size_bytes": 1345
    }
  ]
}
```

## Conflicts and dissent

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v5-council-006",
  "triggered": false,
  "trigger_reasons": [],
  "invocation_id": null,
  "disputed_finding_ids": [],
  "dispositions": [],
  "preserved_dissent": []
}
```

## Outside-view advisory register

Outside-view hypotheses have `decision_weight: none` and do not determine the verdict.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v5-council-006",
  "observations": [],
  "advisory_hypotheses": [],
  "promoted_observation_ids": []
}
```

## Chairman recommendation

Revise the reviewed artifact to address all six accepted findings, then submit a new review run.

## Residual risks and unreviewed observations

```json
[
  "The control plane remains at risk until all six accepted findings are resolved and independently re-reviewed."
]
```

```json
[]
```

## Lineage

No predecessor lineage.

## Reproducibility and limitations

```json
{
  "telemetry": {
    "schema_version": 1,
    "review_id": "control-plane-stabilization-v5-council-006",
    "calls": [
      {
        "invocation_id": "inv6-auth-001",
        "role": "internal-reviewer",
        "lane": "internal-authority",
        "provider": "deepseek-official",
        "model": "deepseek-flash",
        "attempt": 1,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv6-adv-001",
        "role": "internal-reviewer",
        "lane": "internal-adversarial",
        "provider": "openai-codex",
        "model": "gpt-5.6-sol",
        "attempt": 1,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv6-ext-001",
        "role": "outside-view",
        "lane": "external-outside-view",
        "provider": "openai-codex",
        "model": "gpt-5.6-luna",
        "attempt": 1,
        "status": "failed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv6-ext-002",
        "role": "outside-view",
        "lane": "external-outside-view",
        "provider": "openai-codex",
        "model": "gpt-5.6-luna",
        "attempt": 2,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv6-chair-001",
        "role": "chairman",
        "lane": "chairman",
        "provider": "openai-codex",
        "model": "gpt-5.6-terra",
        "attempt": 1,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      }
    ],
    "calls_reserved": 8,
    "calls_released": 1,
    "calls_attempted": 5,
    "calls_remaining": 1,
    "maximum_model_calls": 8,
    "durations_complete": false,
    "token_usage_complete": false,
    "cost_usage_complete": false
  },
  "closure": {
    "valid": true,
    "reviewed_artifacts_unchanged": true
  }
}
```

This report is rendered from the exact executable template bytes identified by `report_template_sha256`. It derives from the persisted request, immutable manifests and packets, parent-owned dispatch ledger, validated reviewer records, ledger, verifier evidence, adjudication, Chairman disposition, telemetry, degradation records, and optional lineage. Missing evidence is reported as missing, not PASS.

## Non-authority statement

The named HUMAN or Leader remains the decision owner. Council completion is not project acceptance. **Verified exact byte equality:** for every reviewed artifact, the final raw-byte SHA-256 and byte size exactly equal the values pinned before the first model call.

