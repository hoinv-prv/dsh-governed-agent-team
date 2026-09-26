# Council Review Report

- **Review:** `control-plane-stabilization-v11-council-012`
- **Verdict:** `needs_revision`
- **Confidence:** `high`
- **Decision owner:** `human: HUMAN-current-user`
- **Authority:** Advisory evidence only; this report does not accept, merge, deploy, publish, activate, or modify the reviewed artifact.

## Scope and immutable identity

Determine whether control-plane-stabilization-design.v11.md corrects all run-004 through run-011 verified findings and earlier observations and defines the smallest feasible procedural fail-closed pre-charge admission design without claiming non-bypassable runtime enforcement, elimination of the irreducible TOCTOU race, invented authority, hidden attempt cost, weakened evidence, or an unsupported runtime service. Review exact pinned bytes only; advise whether revision is required before any WBS build.

Modes: `design`, `governance`.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v11-council-012",
  "artifacts": [
    {
      "artifact_id": "design-v11",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v11.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/design-v11",
      "sha256": "ed4910113cf96c27b7b3a01640026a29340a45d5060529c331e821810de3662c",
      "size_bytes": 59405,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 469
        }
      ]
    },
    {
      "artifact_id": "sanitized-design-v11",
      "role": "sanitized",
      "source_artifact_id": "design-v11",
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v11.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/sanitized-design-v11",
      "sha256": "ed4910113cf96c27b7b3a01640026a29340a45d5060529c331e821810de3662c",
      "size_bytes": 59405,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 469
        }
      ]
    },
    {
      "artifact_id": "repo-rules",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/AGENTS.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/repo-rules",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/aiws-architecture",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/runtime-review-method",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/gat-proposal",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/failure-model",
      "sha256": "6b3afb2dda07f944aa5015cd7dbc279c8fef322ec6893cad90f91258d00332f2",
      "size_bytes": 24921,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 201
        }
      ]
    },
    {
      "artifact_id": "council-contract",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/contracts.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/council-contract",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/snapshots/council-routing",
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
    "invocation_id": "inv12-auth-001",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v41",
    "attempt": 1,
    "packet_sha256": "4995e1ff46f7b1218c7200f38aed9818ec3d53db7f5fc5b5d17b830dbd11bbb5",
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
    "invocation_id": "inv12-adv-001",
    "lane": "internal-adversarial",
    "role": "internal-reviewer",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "aff4546956a45c9e19a7e8a50307d26b4c84e7cdea60ad8a5dbee45a9c873680",
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
    "invocation_id": "inv12-ext-001",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "a3e01ba6fd72a45f55580f118f00e10e8001256f96afbdbd6bab82c9c77db1a5",
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
    "invocation_id": "inv12-chair-001",
    "lane": "chairman",
    "role": "chairman",
    "provider": "openai-codex",
    "model": "gpt-5.6-terra",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "664b3e18ac03e5ad0c354e444df90aff625b63d2d594a9205444a8acb4ca4f33",
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
    "degradation_id": "DEG12-001",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-authority",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG12-002",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-adversarial",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG12-003",
    "kind": "prompt_only_read_only",
    "affected_lane": "external-outside-view",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG12-004",
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
| `reviewer11-authority-001-f1` | `medium` | `confirmed` | Section 5.1 closes the set of pre-charge writes to two evidence effects, but P6 makes a fresh ASC produced by a declared run_aip transition a mandatory pre-charge predicate and Section 10 assigns that AIP-pointer/ASC write to run_aip.py, so the mandatory P6 transition has no admitted pre-charge owner, state or allowed effect. |
| `reviewer11-authority-001-f2` | `medium` | `confirmed` | The Section 5.2 commit procedure re-observes only live P7-P11 predicates and re-hashes bundle inputs, while P14 additionally requires live re-verification of P13/P15/P16 non-revocation and scope and of the migration-authority receipt, so the documented charge gate never names re-checking revocation. |
| `reviewer12-adversarial-f001` | `high` | `confirmed` | The post-charge invalid-ledger branch names a HUMAN-authorized repair but defines no repair state, source backup, durable candidate/receipt, allowed-effect operation, validator, or lineage rule that can admit the repaired bytes under P3. |
| `reviewer12-adversarial-f002` | `high` | `confirmed` | The AdministrativeResourceLedger does not define how its own guarded append invocation is accounted without creating another append invocation that must itself be accounted. |
| `reviewer12-adversarial-f003` | `high` | `confirmed` | A migrated base produced through MIGRATION_RECOVERY is not required to carry the fresh recovery authorization into migration_authority; first-charge admission re-hashes only the original migration decision. |

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v11-council-012",
  "executor": "parent-orchestrator",
  "artifact_manifest_sha256": "02a598a716894d455424f5aa759f09cacd19823ff72739fe42ba5ee0fce604c1",
  "records": [
    {
      "verification_id": "verify-all-findings",
      "finding_ids": [
        "reviewer11-authority-001-f1",
        "reviewer11-authority-001-f2",
        "reviewer12-adversarial-f001",
        "reviewer12-adversarial-f002",
        "reviewer12-adversarial-f003"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "confirmed",
      "exit_code": null,
      "output_excerpt": "All five normalized findings confirmed against immutable design-v11.",
      "reason": "The pre-charge ownership, full boundary revalidation, post-charge repair, metering recursion and recovery-authority lineage contracts are absent as stated.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v11",
          "sha256": "ed4910113cf96c27b7b3a01640026a29340a45d5060529c331e821810de3662c"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v11",
          "sha256": "ed4910113cf96c27b7b3a01640026a29340a45d5060529c331e821810de3662c"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/verifier/verify-all-findings.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v11-council-012/verifier/raw/verify-all-findings.txt",
      "raw_output_sha256": "bb78ce3fd64ca7730a29f0988375c9d471b1c0d123d07a3a678db9be34d8e030",
      "raw_output_size_bytes": 883
    }
  ]
}
```

## Conflicts and dissent

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v11-council-012",
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
  "review_id": "control-plane-stabilization-v11-council-012",
  "observations": [],
  "advisory_hypotheses": [],
  "promoted_observation_ids": []
}
```

## Chairman recommendation

Resolve all five confirmed findings and re-review exact revised bytes before any WBS build.

## Residual risks and unreviewed observations

```json
[
  "The accepted control-write, revocation, post-charge repair, metering and recovery-lineage gaps remain until revision."
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
    "review_id": "control-plane-stabilization-v11-council-012",
    "calls": [
      {
        "invocation_id": "inv12-auth-001",
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
        "invocation_id": "inv12-adv-001",
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
        "invocation_id": "inv12-ext-001",
        "role": "outside-view",
        "lane": "external-outside-view",
        "provider": "openai-codex",
        "model": "gpt-5.6-luna",
        "attempt": 1,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv12-chair-001",
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
    "calls_attempted": 4,
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

