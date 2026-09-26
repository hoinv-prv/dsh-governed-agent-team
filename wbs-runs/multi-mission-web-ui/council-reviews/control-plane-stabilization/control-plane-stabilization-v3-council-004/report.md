# Council Review Report

- **Review:** `control-plane-stabilization-v3-council-004`
- **Verdict:** `needs_revision`
- **Confidence:** `high`
- **Decision owner:** `human: HUMAN-current-user`
- **Authority:** Advisory evidence only; this report does not accept, merge, deploy, publish, activate, or modify the reviewed artifact.

## Scope and immutable identity

Determine whether control-plane-stabilization-design.v3.md corrects the run-002 findings and run-003 raw observations and defines the smallest feasible procedural fail-closed pre-charge admission design without claiming non-bypassable runtime enforcement, elimination of the irreducible TOCTOU race, invented authority, hidden attempt cost, weakened evidence, or an unsupported runtime service. Review exact pinned bytes only; advise whether revision is required before any WBS build.

Modes: `design`, `governance`.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v3-council-004",
  "artifacts": [
    {
      "artifact_id": "design-v3",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v3.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/design-v3",
      "sha256": "8fc33a7d5a09ed5eb53d90d4b34ccfee0b58d061342bd561c5d986f793824bf2",
      "size_bytes": 27665,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 384
        }
      ]
    },
    {
      "artifact_id": "sanitized-design-v3",
      "role": "sanitized",
      "source_artifact_id": "design-v3",
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v3.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/sanitized-design-v3",
      "sha256": "8fc33a7d5a09ed5eb53d90d4b34ccfee0b58d061342bd561c5d986f793824bf2",
      "size_bytes": 27665,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 384
        }
      ]
    },
    {
      "artifact_id": "repo-rules",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/AGENTS.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/repo-rules",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/aiws-architecture",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/runtime-review-method",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/gat-proposal",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/failure-model",
      "sha256": "1a9ce89726d11d7f52e62739d611b76f36ebd51ae067c1d710be97073363eb05",
      "size_bytes": 14483,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 129
        }
      ]
    },
    {
      "artifact_id": "council-contract",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/contracts.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/council-contract",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/snapshots/council-routing",
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
    "invocation_id": "inv4-auth-001",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v41",
    "attempt": 1,
    "packet_sha256": "4fc2eb09c798ba3c299237a7016a1d25c3aea386b1e2b7e1ce7095af5df4c9bc",
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
    "invocation_id": "inv4-auth-002",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v41",
    "attempt": 2,
    "packet_sha256": "4fc2eb09c798ba3c299237a7016a1d25c3aea386b1e2b7e1ce7095af5df4c9bc",
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
    "invocation_id": "inv4-adv-001",
    "lane": "internal-adversarial",
    "role": "internal-reviewer",
    "provider": "openai-codex",
    "model": "gpt-5.6-terra",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "5181a24db1d6ac6dada4ea62b0a5615fbb1ebf913a0fc88552ee4adbab3c25b1",
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
    "invocation_id": "inv4-ext-001",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "01d262ffab0296d5031530b1f7a6040bb1cb4b3dd956ceb3f70cecfd260493b3",
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
    "invocation_id": "inv4-chair-001",
    "lane": "chairman",
    "role": "chairman",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "df1c8a70459158d829811602b0715ff7daaf11847a22e2a8b377ba4ef1c29c76",
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
    "degradation_id": "DEG4-001",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-authority",
    "detail": "Read-only/tool restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG4-002",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-adversarial",
    "detail": "Read-only/tool restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG4-003",
    "kind": "prompt_only_read_only",
    "affected_lane": "external-outside-view",
    "detail": "Read-only/tool restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG4-004",
    "kind": "unknown_cost",
    "affected_lane": "all",
    "detail": "Duration, token and cost telemetry were unavailable from model adapters.",
    "verdict_consequence": "pass_with_notes_at_best"
  }
]
```

## Findings and deterministic verification

| ID | Severity | Verification | Claim |
|---|---|---|---|
| `r4auth002a2-f1` | `high` | `confirmed` | The design mandates that every mutable mission-control artifact have exactly one declared owner and write mechanism, yet the charge/boundary record - the sole mandatory pre-charge write - is assigned to 'the owning charge operation', an operation the design elsewhere states is not identified by any pinned Source of Truth; the mandatory pre-charge control surface therefore has no existing owner, and closing it requires inventing the capability the design forbids. |
| `r4auth002a2-f2` | `medium` | `confirmed` | The design claims to follow repository precedence but collapses the pinned content hierarchy Project Wiki, Local Wiki, Common Wiki and History into one post-skills 'Wiki' tier and drops History entirely, so precedence for wiki-tier or History conflicts is undeclared while the design asserts the pinned order governs. |
| `r4auth002a2-f3` | `medium` | `confirmed` | The design introduces the new persisted contract identifier 'gat-admission-bundle/1' with new fields and delegates the bundle to a 'read-only prepare operation', but names no owning schema authority, validator or exact command, so the schema-validation half of the required dual validation has no declared owner and the P1/P2 evidence cannot cite a validatable contract. |

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v3-council-004",
  "executor": "parent-orchestrator",
  "artifact_manifest_sha256": "19fb90c391090e84ef9297e21e9d36fe0df6de9cfdd23fb898942405c0645305",
  "records": [
    {
      "verification_id": "verify-authority-findings",
      "finding_ids": [
        "r4auth002a2-f1",
        "r4auth002a2-f2",
        "r4auth002a2-f3"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "confirmed",
      "exit_code": null,
      "output_excerpt": "All three normalized authority findings confirmed against immutable design-v3 and repo-rule snapshots.",
      "reason": "The named charge operation, exact precedence, and proposed bundle schema/validator ownership are absent as claimed.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v3",
          "sha256": "8fc33a7d5a09ed5eb53d90d4b34ccfee0b58d061342bd561c5d986f793824bf2"
        },
        {
          "artifact_id": "repo-rules",
          "sha256": "9260216bebe60f86e08e3b745a4d822afd0120ce560a631285d17a3b59221177"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v3",
          "sha256": "8fc33a7d5a09ed5eb53d90d4b34ccfee0b58d061342bd561c5d986f793824bf2"
        },
        {
          "artifact_id": "repo-rules",
          "sha256": "9260216bebe60f86e08e3b745a4d822afd0120ce560a631285d17a3b59221177"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/verifier/verify-authority-findings.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v3-council-004/verifier/raw/verify-authority-findings.txt",
      "raw_output_sha256": "e38c668a30ff96f10035d4129e3d878ba481e2ec3e731c7777aa92301be10f00",
      "raw_output_size_bytes": 1226
    }
  ]
}
```

## Conflicts and dissent

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v3-council-004",
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
  "review_id": "control-plane-stabilization-v3-council-004",
  "observations": [],
  "advisory_hypotheses": [],
  "promoted_observation_ids": []
}
```

## Chairman recommendation

Revise the artifact to name an attributable owner for the charge operation, restore the complete repository-precedence hierarchy including distinct Wiki tiers and History, and define the AdmissionBundle authority, validator, and exact prepare command; submit the corrected artifact through a new review run.

## Residual risks and unreviewed observations

```json
[
  "The charge/boundary record remains without an attributable owning charge-operation owner until revision.",
  "Repository precedence remains incomplete while Wiki tiers are collapsed and History is omitted.",
  "AdmissionBundle preparation remains underspecified without a named authority, validator, and exact command.",
  "Prompt-only restriction mode limits assurance that reviewer restrictions were enforced."
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
    "review_id": "control-plane-stabilization-v3-council-004",
    "calls": [
      {
        "invocation_id": "inv4-auth-001",
        "role": "internal-reviewer",
        "lane": "internal-authority",
        "provider": "deepseek-official",
        "model": "deepseek-flash",
        "attempt": 1,
        "status": "failed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv4-auth-002",
        "role": "internal-reviewer",
        "lane": "internal-authority",
        "provider": "deepseek-official",
        "model": "deepseek-flash",
        "attempt": 2,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv4-adv-001",
        "role": "internal-reviewer",
        "lane": "internal-adversarial",
        "provider": "openai-codex",
        "model": "gpt-5.6-terra",
        "attempt": 1,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv4-ext-001",
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
        "invocation_id": "inv4-chair-001",
        "role": "chairman",
        "lane": "chairman",
        "provider": "openai-codex",
        "model": "gpt-5.6-sol",
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

