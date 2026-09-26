# Council Review Report

- **Review:** `control-plane-stabilization-v38-council-041`
- **Verdict:** `needs_revision`
- **Confidence:** `high`
- **Decision owner:** `human: HUMAN-current-user`
- **Authority:** Advisory evidence only; this report does not accept, merge, deploy, publish, activate, or modify the reviewed artifact.

## Scope and immutable identity

Fresh immutable council review of exact design v38: verify closure of schema-valid run-040 internal findings and independently checked outside content, exact CP registry closure, full evidence/hash bindings, manifest/registry ownership, accounting fixtures, freshness and command-policy rules. Do not build or execute WBS.

Modes: `design`, `governance`.

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v38-council-041",
  "artifacts": [
    {
      "artifact_id": "design-v38",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v38.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/design-v38",
      "sha256": "a210c3d58208fa6145c06f2dcf975b0c966dbb0ad2957bec44614e698d9d2ede",
      "size_bytes": 165548,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 709
        }
      ]
    },
    {
      "artifact_id": "sanitized-design-v38",
      "role": "sanitized",
      "source_artifact_id": "design-v38",
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v38.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/sanitized-design-v38",
      "sha256": "a210c3d58208fa6145c06f2dcf975b0c966dbb0ad2957bec44614e698d9d2ede",
      "size_bytes": 165548,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 709
        }
      ]
    },
    {
      "artifact_id": "repo-rules",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/AGENTS.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/repo-rules",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/aiws-architecture",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/runtime-review-method",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/gat-proposal",
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
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v1-council-002/snapshots/failure-model",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/failure-model",
      "sha256": "434f1613751d8a2b5b8813936404e4567e698ea4ace88ed74863e2a56e4d8b86",
      "size_bytes": 11261,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 102
        }
      ]
    },
    {
      "artifact_id": "consistency-audit-v32",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/control-plane-stabilization-consistency-audit.v32.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/consistency-audit-v32",
      "sha256": "6e91a5bc3d333b052469d4f381e5805a53c7ecc4eb8ba11e5c0dfe64157cfbef",
      "size_bytes": 7456,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 51
        }
      ]
    },
    {
      "artifact_id": "council-contract",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/deepseek-harness/.agents/skills/dsh-council-review/references/contracts.md",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/council-contract",
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
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/council-routing",
      "sha256": "c946c21caeeee25e460eacacb1466f9371f2d7534ed18b5c8bfbd61ee4d205e8",
      "size_bytes": 6123,
      "media_type": "text/markdown",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 45
        }
      ]
    },
    {
      "artifact_id": "run033-ledger",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v33-council-033/ledger.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run033-ledger",
      "sha256": "25a4e907178ead1cf8ee94fab6929f67c9063f91550de80f72c5f96969eaf534",
      "size_bytes": 30282,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 603
        }
      ]
    },
    {
      "artifact_id": "run033-verifier",
      "role": "source-of-truth",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v33-council-033/verifier/manifest.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run033-verifier",
      "sha256": "567e50546ca8979c6dadded30f2f4de85d928abdb4211aa4009706a1ff76f07f",
      "size_bytes": 5551,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 103
        }
      ]
    },
    {
      "artifact_id": "run034-dispatch",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v34-council-034/dispatch-ledger.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run034-dispatch",
      "sha256": "9f382a2bb6a7c960da5399beb16d62398c36f734f527732d9702b875cf1da094",
      "size_bytes": 4271,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 141
        }
      ]
    },
    {
      "artifact_id": "run034-authority",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v34-council-034/reviewers/internal-authority.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run034-authority",
      "sha256": "61cc1b74b5761619c62e4bc66623edede8d8e2b65031870468777e7e8e872c8e",
      "size_bytes": 7917,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 98
        }
      ]
    },
    {
      "artifact_id": "run034-adversarial",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v34-council-034/reviewers/internal-adversarial.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run034-adversarial",
      "sha256": "1f6ef212162061423eb2fbca75902d75fd69edad1249f872a1710b9df13643a5",
      "size_bytes": 1850,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 42
        }
      ]
    },
    {
      "artifact_id": "run038-authority",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v35-council-038/reviewers/internal-authority.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run038-authority",
      "sha256": "2de3070dd80acd2f88868c166baa971bcc41025291121d43a0df558c77c7ccef",
      "size_bytes": 13508,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 182
        }
      ]
    },
    {
      "artifact_id": "run038-adversarial",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v35-council-038/reviewers/internal-adversarial.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run038-adversarial",
      "sha256": "88540d3a756787d1b37e4c3ab60935cc6d9741ad676bb3d3956e9e40d086e692",
      "size_bytes": 5526,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 98
        }
      ]
    },
    {
      "artifact_id": "run038-outside",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v35-council-038/reviewers/external-outside-view.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run038-outside",
      "sha256": "9fc8bc3098a53fae09e0a41257fae2be1ab3cd08d11107d65de5c606bc4f956f",
      "size_bytes": 14929,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 243
        }
      ]
    },
    {
      "artifact_id": "run039-status",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v36-council-039/run-status.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run039-status",
      "sha256": "a75fdc399d799f7925202446a302cd793b75eadac4bf92a9933b8022fd58fa48",
      "size_bytes": 799,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 15
        }
      ]
    },
    {
      "artifact_id": "run039-ledger",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v36-council-039/dispatch-ledger.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run039-ledger",
      "sha256": "98106ec1e28bf6df75587ec9d263b0e1bb8497c7023eea19ce7e98d8f4e968f6",
      "size_bytes": 4806,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 159
        }
      ]
    },
    {
      "artifact_id": "run039-authority-current",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v36-council-039/reviewers/internal-authority.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run039-authority-current",
      "sha256": "33068d1dabb3bb576d8ba4e0841ca01d014e7e8a75f79ca9c6f484e0992ea235",
      "size_bytes": 16897,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 238
        }
      ]
    },
    {
      "artifact_id": "run039-adversarial-current",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v36-council-039/reviewers/internal-adversarial.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run039-adversarial-current",
      "sha256": "737efe845b129552937a4526adf57afa1b5b407e282ba2c785b423e9a530c0a1",
      "size_bytes": 12232,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 210
        }
      ]
    },
    {
      "artifact_id": "run039-outside-current",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v36-council-039/reviewers/external-outside-view.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run039-outside-current",
      "sha256": "795180834042a2050ff294caecb2456b945c513785df29052fe91d4a64b92c95",
      "size_bytes": 26523,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 352
        }
      ]
    },
    {
      "artifact_id": "run040-status",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v37-council-040/run-status.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run040-status",
      "sha256": "a454701dc2484584b3aa93f2d2732d5a92d2aa6db87fd653ede8e4eab27ca1ec",
      "size_bytes": 705,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 15
        }
      ]
    },
    {
      "artifact_id": "run040-authority",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v37-council-040/reviewers/internal-authority.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run040-authority",
      "sha256": "5f3eccb0e4a799743ee01190788f91b877f9af9d93a467ebeb168fb385996bc6",
      "size_bytes": 15581,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 210
        }
      ]
    },
    {
      "artifact_id": "run040-adversarial",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v37-council-040/reviewers/internal-adversarial.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run040-adversarial",
      "sha256": "a131319eca6e423722c2514826ef367bde0d03c7556e222522562cbdb623e05c",
      "size_bytes": 10499,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 158
        }
      ]
    },
    {
      "artifact_id": "run040-outside-invalid",
      "role": "reviewed",
      "source_artifact_id": null,
      "canonical_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v37-council-040/reviewers/external-outside-view.json",
      "snapshot_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/snapshots/run040-outside-invalid",
      "sha256": "bb119504d27026381ddf990cf8eb7bada55d309b8d6673a72e8884b460e04abc",
      "size_bytes": 18823,
      "media_type": "application/json",
      "selected_ranges": [
        {
          "start_line": 1,
          "end_line": 327
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
    "invocation_id": "inv41-auth-001",
    "lane": "internal-authority",
    "role": "internal-reviewer",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v4",
    "attempt": 1,
    "packet_sha256": "e4d88d2ca087f938e987270e83c940b1ae7e572fb714b73e3e1725f2b21aa217",
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
    "invocation_id": "inv41-adv-001",
    "lane": "internal-adversarial",
    "role": "internal-reviewer",
    "provider": "openai-codex",
    "model": "gpt-5.6-luna",
    "route_family": "openai-gpt-5.6",
    "attempt": 1,
    "packet_sha256": "ad902e9e014e690a6b1050585656ffdb1fc0026de4840616b4eef564e4dfac77",
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
    "invocation_id": "inv41-ext-001",
    "lane": "external-outside-view",
    "role": "outside-view",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v4",
    "attempt": 1,
    "packet_sha256": "b4bda4e0152bd70ee1ef72a23eaff9d433c7ab5413816e1bf6040fffe5073153",
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
    "invocation_id": "inv41-adj-001",
    "lane": "adjudication",
    "role": "adjudicator",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "route_family": "openai-gpt-5.6",
    "attempt": 1,
    "packet_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "restriction_mode": "prompt-only",
    "capabilities": {
      "persona": false,
      "tool_filter": false,
      "output_schema": false
    },
    "status": "reserved",
    "failure_code": null
  },
  {
    "invocation_id": "inv41-chair-001",
    "lane": "chairman",
    "role": "chairman",
    "provider": "deepseek-official",
    "model": "deepseek-flash",
    "route_family": "deepseek-v4",
    "attempt": 1,
    "packet_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
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
    "degradation_id": "DEG41-PROMPT-INTERNAL_AUTHORITY",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-authority",
    "detail": "Persona/tool/output restrictions were conveyed by prompt; no preconfigured enforcement instance was available.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG41-PROMPT-INTERNAL_ADVERSARIAL",
    "kind": "prompt_only_read_only",
    "affected_lane": "internal-adversarial",
    "detail": "Persona/tool/output restrictions were conveyed by prompt; no preconfigured enforcement instance was available.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG41-PROMPT-EXTERNAL_OUTSIDE_VIEW",
    "kind": "prompt_only_read_only",
    "affected_lane": "external-outside-view",
    "detail": "Persona/tool/output restrictions were conveyed by prompt; no preconfigured enforcement instance was available.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG41-PROMPT-CHAIRMAN",
    "kind": "prompt_only_read_only",
    "affected_lane": "chairman",
    "detail": "Persona/tool/output restrictions were conveyed by prompt; no preconfigured enforcement instance was available.",
    "verdict_consequence": "pass_with_notes_at_best"
  },
  {
    "degradation_id": "DEG41-EXT-CONTEXT",
    "kind": "external_context_reduction",
    "affected_lane": "external-outside-view",
    "detail": "Required outside lane received only the sanitized design and declared public context, without peer findings or private Sources of Truth.",
    "verdict_consequence": "none"
  },
  {
    "degradation_id": "DEG41-UNKNOWN-COST",
    "kind": "unknown_cost",
    "affected_lane": "all",
    "detail": "Provider adapters did not report token or monetary cost telemetry for the four completed calls.",
    "verdict_consequence": "none"
  }
]
```

## Findings and deterministic verification

| ID | Severity | Verification | Claim |
|---|---|---|---|
| `ADV41-F-001` | `high` | `confirmed` | The exhaustive CP-12 registry omits the failure edges from CHARGED_ACCOUNTING_PENDING or COMPLETION_INDEX_CLOSE_PENDING into CHARGED_ACCOUNTING_BLOCKED, even though the state machine and accounting protocol require those edges when a charged writer, completion, index-close, or accounting append fails. |
| `ADV41-F-002` | `high` | `confirmed` | CP-05 permits FROZEN legacy-ledger migration without stating that an accepted ADMIN_LEDGER_GENESIS and AdministrativeLedgerGenesisReceipt already exist, contradicting the separate prerequisite that migration must occur only after genesis and its canonical administrative ledger are accepted. |
| `ADV41-F-003` | `high` | `confirmed` | The AcceptedDesignRegistry generation schema and AdmissionBundle design_basis do not require an equality binding between the selected current design_raw_sha256 and the artifact/design hash covered by the council ReviewClosureReceipt, so re-hashing both does not prove that the latest HUMAN-accepted design is the council-passed design. |
| `ADV41-F-004` | `medium` | `confirmed` | CP-02 and CP-04 do not enumerate the destinations of their required HUMAN recovery edges, although the state machine requires ADMIN_LEDGER_GENESIS_BLOCKED→ADMIN_LEDGER_GENESIS and BOOTSTRAP_BLOCKED→BOOTSTRAP_MAINTENANCE or a no-effect close to FROZEN. |
| `AUTH41-F-001` | `high` | `confirmed` | The Section 15.1 exact-basis list binds the consistency audit, the run-033 ledger/verifier, run-034 dispatch/authority/adversarial, run-038 authority/adversarial/outside and preserved run-039 current authority/adversarial/outside, but never raw-byte binds the run-040 authority or run-040 adversarial envelope whose findings the same matrix claims to correct, so the run-040 closure rows cannot satisfy the matrix's own 'Absence or mismatch makes the corresponding closure claim not-verifiable' rule. |
| `AUTH41-F-002` | `medium` | `confirmed` | Section 5.0.1 requires the Section 14 coverage index to cover every `allowed_edges` value of the CP-01..CP-16 registry, but the Section 14 failure matrix has no row for the charged-accounting success edge `CHARGED_ACCOUNTING_PENDING→COMPLETION_INDEX_CLOSE_PENDING` (CP-12), the review-return edge `REVIEW_PENDING→REVIEWING` (CP-14), or the CP-15 return edges `ACCEPTANCE_PENDING\|ACCEPTANCE_AUTHORITY_CONFLICT→AWAITING_HUMAN_ACCEPTANCE` and `ACCEPTANCE_VERIFICATION_PENDING\|ACCEPTANCE_VERIFICATION_FAILED→ACCEPTANCE_VERIFYING`, so the claimed coverage is incomplete. |
| `AUTH41-F-003` | `medium` | `confirmed` | CP-16's row declares its sole permitted edge as the terminal completion-chain head while also stating that an explicit acceptance-authority conflict makes `ACCEPTED` non-usable, but it does not register the outgoing `ACCEPTED→ACCEPTANCE_AUTHORITY_CONFLICT` edge, which CP-15 already lists among its allowed edges, so the transition out of a conflicted `ACCEPTED` has no owner row whose `allowed_edges` cell contains it. |
| `AUTH41-F-004` | `low` | `confirmed` | The `TransitionCapabilityManifest` header binds a `design_sha256` field, but neither the `AdmissionBundle.transition_capability_manifest` reference nor P5/P14/P15 requires that field to equal the current `AcceptedDesignRegistry` generation's design hash, so a manifest generation authored for an earlier design revision can still be admitted as `READY`. |
| `EXT41-O-001` | `medium` | `confirmed` | The closed freshness_rule compares a monotonic-clock reading against the wall-clock field `expires_at_utc`, so the mandated time comparison has no single defined clock domain. |
| `EXT41-O-002` | `low` | `confirmed` | Section 14's normative edge-registry coverage statement maps failures to CP-03 through CP-16 but maps no failure row to CP-01 or CP-02, the genesis and genesis-blocked states. |
| `EXT41-O-003` | `low` | `confirmed` | Section 15.1 lists the prior finding ID EXT39R-O-006 twice, in two rows that name different v38 correction locators and different required fixtures. |
| `EXT41-O-004` | `medium` | `confirmed` | Section 9.2 step 2 requires migration to consume an execution-representation decision that P15 and Section 6.1 item (g) produce inside bootstrap, while CP-03 permits BOOTSTRAP_MAINTENANCE only after an accepted migrated base exists. |
| `EXT41-O-005` | `low` | `confirmed` | A differing or partial pre-charge NOT_APPLIED completion is assigned to `NOT_READY` in Section 5.1(e) and to `UNCHARGED_COMPLETION_CORRUPT_BLOCKED` in Section 9.1 and CP-11. |
| `EXT41-O-006` | `low` | `confirmed` | Section 15.1 pins its basis artifacts by SHA-256 only and declares absence or mismatch non-verifiable, yet the design gives no canonical path for the consistency audit and run-033/034/038/039 basis records it requires to be re-hashed. |
| `EXT41-O-007` | `low` | `confirmed` | The edge `REVIEWING→REVISION_REQUIRED_CHARGED` is declared in both the CP-13 and CP-14 registry rows. |
| `EXT41-O-008` | `low` | `confirmed` | The v38 closure matrix row for AUTH38-F-003 and AUTH38-F-004 names an 'explicit v36 locator contract' as its correction locator, retaining an older revision token within the v38 design bytes. |
| `EXT41-O-009` | `info` | `confirmed` | Section 6.1 enumerates eleven bootstrap artifacts and operations (items (a) through (k)) that must be authored, validated, reviewed and HUMAN-accepted before a WBS is built, while the AdmissionBundle section describes the mechanism as 'not a new runtime service'. |
| `EXT41-O-010` | `low` | `confirmed` | Section 6.3 supplies a worked integer fixture for the pre-charge reservation and root recurrence but gives no worked integer example for the post-charge D/B recovery recurrence. |

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v38-council-041",
  "executor": "parent-orchestrator",
  "artifact_manifest_sha256": "f94f521fc6cb9a42eb40052cd64668a066d207dd3337d6b4491da59a216699ed",
  "records": [
    {
      "verification_id": "verify41-confirmed",
      "finding_ids": [
        "ADV41-F-001",
        "ADV41-F-002",
        "ADV41-F-003",
        "ADV41-F-004",
        "AUTH41-F-001",
        "AUTH41-F-002",
        "AUTH41-F-003",
        "AUTH41-F-004",
        "EXT41-O-001",
        "EXT41-O-002",
        "EXT41-O-003",
        "EXT41-O-004",
        "EXT41-O-005",
        "EXT41-O-006",
        "EXT41-O-007",
        "EXT41-O-008",
        "EXT41-O-009",
        "EXT41-O-010"
      ],
      "method": "read",
      "command_id": null,
      "argv": null,
      "cwd": null,
      "timeout_seconds": null,
      "authorized_by_request": true,
      "status": "confirmed",
      "exit_code": null,
      "output_excerpt": "Exact read of immutable design-v38 confirms all normalized observations at their cited locators. Internal findings establish missing CP-12 charged-blocked entry edges, missing genesis prerequisite, missing review-receipt/design equality, incomplete blocked-state destinations, evidence-basis and coverage/ownership/freshness gaps. Outside observations confirm the cited ambiguity/duplication/ordering/fixture issues. These are design defects or advisory scope disclosures; verification makes no correction to reviewed bytes.",
      "reason": "Exact read of immutable design-v38 confirms all normalized observations at their cited locators. Internal findings establish missing CP-12 charged-blocked entry edges, missing genesis prerequisite, missing review-receipt/design equality, incomplete blocked-state destinations, evidence-basis and coverage/ownership/freshness gaps. Outside observations confirm the cited ambiguity/duplication/ordering/fixture issues. These are design defects or advisory scope disclosures; verification makes no correction to reviewed bytes.",
      "artifact_hashes_before": [
        {
          "artifact_id": "design-v38",
          "sha256": "a210c3d58208fa6145c06f2dcf975b0c966dbb0ad2957bec44614e698d9d2ede"
        },
        {
          "artifact_id": "sanitized-design-v38",
          "sha256": "a210c3d58208fa6145c06f2dcf975b0c966dbb0ad2957bec44614e698d9d2ede"
        }
      ],
      "artifact_hashes_after": [
        {
          "artifact_id": "design-v38",
          "sha256": "a210c3d58208fa6145c06f2dcf975b0c966dbb0ad2957bec44614e698d9d2ede"
        },
        {
          "artifact_id": "sanitized-design-v38",
          "sha256": "a210c3d58208fa6145c06f2dcf975b0c966dbb0ad2957bec44614e698d9d2ede"
        }
      ],
      "result_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/verifier/verify41-confirmed.json",
      "raw_output_path": "/home/hoinv/work/dsh-governed-agent-team/wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/control-plane-stabilization-v38-council-041/verifier/raw/verify41-confirmed.txt",
      "raw_output_sha256": "5b1b145de7802aa18e53e33c467bccd0ed6ad5be594182a01ea6df76a81962ea",
      "raw_output_size_bytes": 525
    }
  ]
}
```

## Conflicts and dissent

```json
{
  "schema_version": 1,
  "review_id": "control-plane-stabilization-v38-council-041",
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
  "review_id": "control-plane-stabilization-v38-council-041",
  "observations": [],
  "advisory_hypotheses": [
    {
      "advisory_id": "EXT41-A-001",
      "claim": "The run-033 authority finding AUTH33-F-04, and the run-040 authority findings AUTH40R-F-004 and AUTH40R-F-005, may be unclosed rather than intentionally absent.",
      "basis": "Section 15.1 rows contain AUTH33-F-01/-02/-03/-05 and AUTH40R-F-001/-002/-003/-006/-007, leaving gaps inside both ID ranges without any stated refutation.",
      "missing_project_sot": [
        "run-033 consistency audit basis 6e91a5bc3d333b052469d4f381e5805a53c7ecc4eb8ba11e5c0dfe64157cfbef",
        "run-040 internal authority lane record"
      ],
      "confidence": "medium",
      "decision_weight": "none",
      "suggested_validation": "Run the required finding-ID completeness diff over the pinned audit and run-040 lane records, and record for each gap whether the finding was refuted or omitted."
    },
    {
      "advisory_id": "EXT41-A-002",
      "claim": "Run-033 outside-view observation EXT33R-O-007 and run-040 outside observations EXT40R-O-005/-006/-008/-010 may be unclosed rather than dispositioned.",
      "basis": "Section 15.1 lists EXT33R-O-003/-004/-005/-006/-008/-009/-010 and EXT40R-O-004/-007/-009/-011, with gaps inside both ranges and no adjacent refutation record.",
      "missing_project_sot": [
        "run-033 outside-view lane record",
        "run-040 outside-view lane record"
      ],
      "confidence": "medium",
      "decision_weight": "none",
      "suggested_validation": "Diff the complete outside-view observation ID sets of runs 033 and 040 against Section 15.1 and record each gap as refuted, promoted or omitted."
    },
    {
      "advisory_id": "EXT41-A-003",
      "claim": "Whether every schema-valid run-040 internal finding is closed by v38 cannot be judged from the outside-view packet, because peer findings are omitted by contract.",
      "basis": "The dispatched packet carries one sanitized artifact, no Sources of Truth and omits the internal-history and peer-findings categories, so no run-040 finding set is available to this lane.",
      "missing_project_sot": [
        "run-040 internal-adversarial and internal-authority finding sets"
      ],
      "confidence": "high",
      "decision_weight": "none",
      "suggested_validation": "Have the parent map each run-040 internal finding ID to an exact Section 15.1 row or a recorded refutation, then bind that map into verification evidence."
    },
    {
      "advisory_id": "EXT41-A-004",
      "claim": "The v38 review-state sentence declaring the run-040 outside envelope schema-invalid may drop a formal lane on an unverified process assertion.",
      "basis": "Line 8 asserts the run-040 outside envelope is schema-invalid and supplies no formal lane, but the design bytes contain no validator output or envelope bytes supporting that assertion.",
      "missing_project_sot": [
        "run-040 outside-view envelope bytes",
        "pinned council schema-validation result for that envelope"
      ],
      "confidence": "medium",
      "decision_weight": "none",
      "suggested_validation": "Re-validate the run-040 outside envelope with the pinned council validator and persist the result before treating its content as non-authoritative."
    }
  ],
  "promoted_observation_ids": [
    "EXT41-O-001",
    "EXT41-O-002",
    "EXT41-O-003",
    "EXT41-O-004",
    "EXT41-O-005",
    "EXT41-O-006",
    "EXT41-O-007",
    "EXT41-O-008",
    "EXT41-O-009",
    "EXT41-O-010"
  ]
}
```

## Chairman recommendation

Keep v38 frozen and correct it in a new design revision before any WBS build: register the CP-12 charged-accounting failure edges and the missing CP-02/CP-04 blocked-state destinations; make accepted genesis plus its receipt a CP-05 precondition and resolve the migration/bootstrap representation-decision circularity; add the review-receipt-to-selected-design hash equality and the TransitionCapabilityManifest design_sha256 equality to P5/P14/P15; add Section 14 coverage rows and single-owner attribution for the duplicated and unowned edges; define one clock domain for expires_at_utc; bind canonical path plus raw SHA-256 for every Section 15.1 basis artifact including the run-040 authority and adversarial envelopes; deduplicate the EXT39R-O-006 row, remove the stale v36 token, state the precedence between NOT_READY and UNCHARGED_COMPLETION_CORRUPT_BLOCKED, add the post-charge D/B worked fixture, and disclose the full pre-WBS bootstrap inventory and authority in the HUMAN approval packet; then rerun the affected lanes on the new revision.

## Residual risks and unreviewed observations

```json
[
  "Every lane ran with restriction_mode prompt-only and no persona or tool filter, so lane read-only isolation was prompt-declared rather than sandbox-enforced and cannot be independently proven from the records.",
  "Ten outside-view observations were promoted and accepted without adjudication, and the outside lane received only the sanitized design with no Sources of Truth, so its scope judgements rest on the design bytes alone.",
  "Adjudication was not triggered and no conflict gate was evaluated in a persisted adjudication record, so any latent high-severity disagreement between lanes remains unexamined.",
  "The claim that the run-040 outside-view envelope is schema-invalid remains a process assertion recorded in the design header; it was not re-validated in this run and could have dropped a formal lane.",
  "AcceptedDesignRegistry and AdmissionBundle binding gaps (ADV41-F-003, AUTH41-F-004) mean a future corrected revision could still admit a superseded design or manifest if the equality predicates are added without adversarial fixtures.",
  "No executable validator, schema or fixture was run for this design-only review; all confirmation is read-based, so arithmetic and recurrence claims remain unexercised by execution."
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
    "review_id": "control-plane-stabilization-v38-council-041",
    "calls": [
      {
        "invocation_id": "inv41-auth-001",
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
        "invocation_id": "inv41-adv-001",
        "role": "internal-reviewer",
        "lane": "internal-adversarial",
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
        "invocation_id": "inv41-ext-001",
        "role": "outside-view",
        "lane": "external-outside-view",
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
        "invocation_id": "inv41-chair-001",
        "role": "chairman",
        "lane": "chairman",
        "provider": "deepseek-official",
        "model": "deepseek-flash",
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

