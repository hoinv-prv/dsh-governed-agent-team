# Council Review Report

- **Review:** `control-plane-stabilization-v18-council-019`
- **Verdict:** `needs_revision`
- **Confidence:** `high`
- **Decision owner:** `human: HUMAN-current-user`
- **Authority:** Advisory evidence only; this report does not accept, merge, deploy, publish, activate, or modify the reviewed artifact.

## Scope and immutable identity

Determine whether control-plane-stabilization-design.v18.md corrects all run-004 through run-018 verified findings and earlier observations and defines the smallest feasible procedural fail-closed pre-charge admission design without claiming non-bypassable runtime enforcement, elimination of the irreducible TOCTOU race, invented authority, hidden attempt cost, weakened evidence, or an unsupported runtime service. Review exact pinned bytes only; advise whether revision is required before any WBS build.

Modes: `design`, `governance`.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v18-council-019",
  "artifacts": [
    {
      "artifact_id": "design-v18",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v18.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/design-v18",
      "sha256": "3bf2635a9337e91a0cce9e1016b1bf979b6eab259b332fab308261b0691a473c",
      "size_bytes": 82561,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 501
        }
      ]
    },
    {
      "artifact_id": "sanitized-design-v18",
      "role": "sanitized",
      "source_artifact_id": "design-v18",
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v18.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/sanitized-design-v18",
      "sha256": "3bf2635a9337e91a0cce9e1016b1bf979b6eab259b332fab308261b0691a473c",
      "size_bytes": 82561,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 501
        }
      ]
    },
    {
      "artifact_id": "repo-rules",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/AGENTS.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/repo-rules",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/aiws-architecture",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/runtime-review-method",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/gat-proposal",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/failure-model",
      "sha256": "ae031e38c34a0ea2e5fa92d9a55bc2ef2740349bd851c458cb129dd60f371536",
      "size_bytes": 33919,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 263
        }
      ]
    },
    {
      "artifact_id": "council-contract",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/contracts.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/council-contract",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/snapshots/council-routing",
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
    "invocation_id": "inv19-auth-001",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v41",
    "attempt": 1,
    "packet_sha256": "17de0e06f7299e315fefa3bf85d964d4cf00647d43934fcb298f212c6d4aee06",
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
    "invocation_id": "inv19-adv-001",
    "lane": "internal-adversarial",
    "role": "internal-reviewer",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "51c6cb4a57f4c085a146f47d1b9bd9f71ab28592253dde9523ae88e0b128ef09",
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
    "invocation_id": "inv19-ext-001",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "017e06de5bd3cc1ba036c20e9f093fe4232174c158a866eec97a7abf9093ed88",
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
    "invocation_id": "inv19-chair-001",
    "lane": "chairman",
    "role": "chairman",
    "provider": "openai-codex",
    "model": "gpt-5.6-terra",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "a7dddbd4233a0c2b76b622e9b537fc45fd4049b3b905065fd742e640e4b91e4b",
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
    "degradation_id": "DEG19-001",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-authority",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG19-002",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-adversarial",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG19-003",
    "kind": "prompt_only_read_only",
    "affected_lane": "external-outside-view",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG19-004",
    "kind": "unknown_cost",
    "affected_lane": "all",
    "detail": "Duration, token and cost telemetry unavailable.",
    "verdict_consequence": "pass_with_notes_at_best"
  }
]
```

## Findings and deterministic verification

| ID | Severity | Verification | Claim |
|---|---|---|---|
| `reviewer19-adversarial-f001` | `high` | `confirmed` | The exhaustive normal-admission write whitelist declares exactly five pre-charge effects but omits the required AdministrativeResourceLedger append, which is itself an additional durable pre-charge write needed to account every allowed call and effect. |
| `reviewer19-adversarial-f002` | `high` | `confirmed` | The commit protocol defines no stable administrative-budget reservation or snapshot across the post-boundary charge-intent seal and the final aggregate-equality check. |
| `reviewer19-adversarial-f003` | `high` | `confirmed` | The uniform transition protocol requires a charge intent to exist before the ledger write but gives no transaction-local rule reconciling that required in-flight intent with P3's rule that any incomplete intent is NOT_READY. |

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v18-council-019",
  "executor": "parent-orchestrator",
  "artifact_manifest_sha256": "6f83b799c23f533f1b028f97d39fa7cb45e0f1f827e735d8e3776f28d24863d9",
  "records": [
    {
      "verification_id": "verify-all-findings",
      "finding_ids": [
        "reviewer19-adversarial-f001",
        "reviewer19-adversarial-f002",
        "reviewer19-adversarial-f003"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "confirmed",
      "exit_code": null,
      "output_excerpt": "All three normalized findings confirmed against immutable design-v18.",
      "reason": "Administrative accounting effect/reservation and in-flight transition rules are incomplete.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v18",
          "sha256": "3bf2635a9337e91a0cce9e1016b1bf979b6eab259b332fab308261b0691a473c"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v18",
          "sha256": "3bf2635a9337e91a0cce9e1016b1bf979b6eab259b332fab308261b0691a473c"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/verifier/verify-all-findings.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v18-council-019/verifier/raw/verify-all-findings.txt",
      "raw_output_sha256": "c0a5ead16bf71bf8d67e124735bac6ec90e6ac122e955d57171ec811e22c12e9",
      "raw_output_size_bytes": 491
    }
  ]
}
```

## Conflicts and dissent

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v18-council-019",
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
  "review_id": "control-plane-stabilization-v18-council-019",
  "observations": [],
  "advisory_hypotheses": [],
  "promoted_observation_ids": []
}
```

## Chairman recommendation

Resolve all three findings and re-review exact revised bytes before WBS build.

## Residual risks and unreviewed observations

```json
[
  "Administrative accounting and in-flight transition semantics remain incomplete until revision."
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
    "review_id": "control-plane-stabilization-v18-council-019",
    "calls": [
      {
        "invocation_id": "inv19-auth-001",
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
        "invocation_id": "inv19-adv-001",
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
        "invocation_id": "inv19-ext-001",
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
        "invocation_id": "inv19-chair-001",
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

