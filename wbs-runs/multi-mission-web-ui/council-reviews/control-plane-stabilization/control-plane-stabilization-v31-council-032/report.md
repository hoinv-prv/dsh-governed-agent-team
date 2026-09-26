# Council Review Report

- **Review:** `control-plane-stabilization-v31-council-032`
- **Verdict:** `needs_revision`
- **Confidence:** `high`
- **Decision owner:** `human: HUMAN-current-user`
- **Authority:** Advisory evidence only; this report does not accept, merge, deploy, publish, activate, or modify the reviewed artifact.

## Scope and immutable identity

Determine whether control-plane-stabilization-design.v31.md corrects all run-004 through run-031 verified findings and earlier observations and defines the smallest feasible procedural fail-closed pre-charge admission design without claiming non-bypassable runtime enforcement, elimination of the irreducible TOCTOU race, invented authority, hidden attempt cost, weakened evidence, or an unsupported runtime service. Review exact pinned bytes only; advise whether revision is required before any WBS build.

Modes: `design`, `governance`.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v31-council-032",
  "artifacts": [
    {
      "artifact_id": "design-v31",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v31.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/design-v31",
      "sha256": "ee631001e863be02fd4f3fcc122bac19f2054906e8f5d62d0420806fe330935a",
      "size_bytes": 120110,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 564
        }
      ]
    },
    {
      "artifact_id": "sanitized-design-v31",
      "role": "sanitized",
      "source_artifact_id": "design-v31",
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v31.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/sanitized-design-v31",
      "sha256": "ee631001e863be02fd4f3fcc122bac19f2054906e8f5d62d0420806fe330935a",
      "size_bytes": 120110,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 564
        }
      ]
    },
    {
      "artifact_id": "repo-rules",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/AGENTS.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/repo-rules",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/aiws-architecture",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/runtime-review-method",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/gat-proposal",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/failure-model",
      "sha256": "fda41fa9e8de24f6f567c60cfa8ea58b82cba41886230692a6a7f77b0c95d253",
      "size_bytes": 49747,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 366
        }
      ]
    },
    {
      "artifact_id": "council-contract",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/contracts.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/council-contract",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/snapshots/council-routing",
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
    "invocation_id": "inv32-auth-001",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v41",
    "attempt": 1,
    "packet_sha256": "a8b9f6f8b7f34c7438508d04459f4a47052be08fea22353d33bf9f2e203ec5ba",
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
    "invocation_id": "inv32-adv-001",
    "lane": "internal-adversarial",
    "role": "internal-reviewer",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "9c7bd410c37990639a077b5b434135ca80ea626370cda013e3d2dcb185a627d2",
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
    "invocation_id": "inv32-ext-001",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "3d966d0e1a682b87afc0aca03d7fb36fdc023864d3f37d89b5d96a2d5eb7f860",
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
    "invocation_id": "inv32-chair-001",
    "lane": "chairman",
    "role": "chairman",
    "provider": "openai-codex",
    "model": "gpt-5.6-terra",
    "route_family": "openai-gpt5",
    "attempt": 1,
    "packet_sha256": "9297e5329242ca79e827b08acf7597d92eae5505a876234419a451badcd06a64",
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
    "invocation_id": "inv32-chair-002",
    "lane": "chairman",
    "role": "chairman",
    "provider": "openai-codex",
    "model": "gpt-5.6-terra",
    "route_family": "openai-gpt5",
    "attempt": 2,
    "packet_sha256": "9fcfd568517062c3ba9d68b1bbb26d792bc1f031802701ca40786222c0eeffb9",
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
    "degradation_id": "DEG32-001",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-authority",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG32-002",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-adversarial",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG32-003",
    "kind": "prompt_only_read_only",
    "affected_lane": "external-outside-view",
    "detail": "Read-only restrictions were prompt-only.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG32-004",
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
| `AUTH32-F-001` | `critical` | `refuted` | The root-cause and design-basis pin cannot be reproduced from the pinned bytes: line 29 names the immutable run-002 snapshot `snapshots/failure-model` with SHA-256 434f1613751d8a2b5b8813936404e4567e698ea4ace88ed74863e2a56e4d8b86, while the dispatched source_of_truth `failure-model` artifact and its snapshot carry SHA-256 fda41fa9e8de24f6f567c60cfa8ea58b82cba41886230692a6a7f77b0c95d253, and no 434f snapshot is included in the packet. |
| `AUTH32-F-002` | `high` | `refuted` | Every admission predicate is produced by the same coordinator actor whose charge it gates, and the design sets no independent observer/witness requirement for the bypass it concedes, so declared procedural fail-closed governance rests on self-attestation. |
| `AUTH32-F-003` | `medium` | `confirmed` | The design declares that authority and precedence follow the pinned repository rule, but never hash-pins the repository rule or AIWS architecture bytes into the admission bundle or P5 re-hash set, leaving its own authority basis outside the verified evidence chain. |
| `reviewer32-adversarial-001-f001` | `high` | `confirmed` | The claimed acyclic intent construction is internally undefined: PlannedIntentBodyCommitment includes the deterministic intent path before the final intent hash/path is derived, while ExecutionTransitionIntent is required to be content-addressed. |
| `reviewer32-adversarial-001-f002` | `high` | `confirmed` | P3 does not admit the charged completion-corruption recovery that Section 9.1 requires: that recovery makes a CompletionCorruptionTombstone the next P3 source even though P3's closed exceptional-link list omits such a record and every next intent otherwise requires a completion-chain head. |
| `reviewer32-adversarial-001-f003` | `high` | `confirmed` | The post-charge exhaustion branch has no executable accounting transition: reservation R and its retry IDs are immutable and no-refund with all usage constrained to A <= R, yet exhaustion is said to be recoverable by a fresh HUMAN ceiling/recovery decision without defining a new allocation or how it binds the already-open intent. |

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v31-council-032",
  "executor": "parent-orchestrator",
  "artifact_manifest_sha256": "2975b9a6d9b8c65a804d489e1f6fa528375147f0c80f59d773285df703335e3f",
  "records": [
    {
      "verification_id": "verify-confirmed",
      "finding_ids": [
        "AUTH32-F-003",
        "reviewer32-adversarial-001-f001",
        "reviewer32-adversarial-001-f002",
        "reviewer32-adversarial-001-f003"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "confirmed",
      "exit_code": null,
      "output_excerpt": "Five findings confirmed against immutable v31 and the pinned run manifest.",
      "reason": "Evidence packet/design-basis, commitment path, charged recovery lineage and recovery allocation gaps are present.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v31",
          "sha256": "ee631001e863be02fd4f3fcc122bac19f2054906e8f5d62d0420806fe330935a"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v31",
          "sha256": "ee631001e863be02fd4f3fcc122bac19f2054906e8f5d62d0420806fe330935a"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/verifier/verify-confirmed.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/verifier/raw/verify-confirmed.txt",
      "raw_output_sha256": "57e849e725c5fec7b0edd4c37a2df5ffdcdf99356bfa12e358df02b8f8545a37",
      "raw_output_size_bytes": 423
    },
    {
      "verification_id": "verify-refuted",
      "finding_ids": [
        "AUTH32-F-001",
        "AUTH32-F-002"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "refuted",
      "exit_code": null,
      "output_excerpt": "Critical basis claim and witness inference refuted; future packet/path clarity remains advisable.",
      "reason": "The exact 434f basis exists in immutable prior artifacts and was previously verified; the witness claim also misstates external predicates and exceeds scope.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v31",
          "sha256": "ee631001e863be02fd4f3fcc122bac19f2054906e8f5d62d0420806fe330935a"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v31",
          "sha256": "ee631001e863be02fd4f3fcc122bac19f2054906e8f5d62d0420806fe330935a"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/verifier/verify-refuted.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v31-council-032/verifier/raw/verify-refuted.txt",
      "raw_output_sha256": "2494bbe74007d642dca62b448ff58c5430f86ed20aa981cab040a2dec589ac08",
      "raw_output_size_bytes": 482
    }
  ]
}
```

## Conflicts and dissent

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v31-council-032",
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
  "review_id": "control-plane-stabilization-v31-council-032",
  "observations": [],
  "advisory_hypotheses": [],
  "promoted_observation_ids": []
}
```

## Chairman recommendation

Resolve four confirmed findings and include immutable basis explicitly in next packet.

## Residual risks and unreviewed observations

```json
[
  "Authority-basis, commitment, lineage and recovery accounting remain incomplete."
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
    "review_id": "control-plane-stabilization-v31-council-032",
    "calls": [
      {
        "invocation_id": "inv32-auth-001",
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
        "invocation_id": "inv32-adv-001",
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
        "invocation_id": "inv32-ext-001",
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
        "invocation_id": "inv32-chair-001",
        "role": "chairman",
        "lane": "chairman",
        "provider": "openai-codex",
        "model": "gpt-5.6-terra",
        "attempt": 1,
        "status": "failed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      },
      {
        "invocation_id": "inv32-chair-002",
        "role": "chairman",
        "lane": "chairman",
        "provider": "openai-codex",
        "model": "gpt-5.6-terra",
        "attempt": 2,
        "status": "completed",
        "duration_ms": null,
        "input_tokens": null,
        "output_tokens": null,
        "cost": null
      }
    ],
    "calls_reserved": 8,
    "calls_released": 0,
    "calls_attempted": 5,
    "calls_remaining": 0,
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

