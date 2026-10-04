# BS1 Design Baseline

## identity
```json
{
  "model_family": "durable-agent-basic-design",
  "schema_version": "bs1-canonical-model/1",
  "semantic_source_set_id": "sha256:4980450586affb034adca81911c081eccc112bbb42b056d065a63440a81c5681"
}
```

## source_bindings
```json
[
  {
    "logical_id": "dto_plan_boundary",
    "path": "wbs-runs/durable-agent-bs1-basic-design/design/dto-plan-boundary.json",
    "sha256": "bec9c536ba4076366d00aafaa1d044d2c2df59e67c0ad7fab7df6febe2eb6284"
  },
  {
    "logical_id": "effect_boundary",
    "path": "wbs-runs/durable-agent-bs1-basic-design/design/effect-boundary.json",
    "sha256": "3cb1e42149d16fdb6d69c131a90d62417d4575ee379cd590122e3ef5c3f149f5"
  },
  {
    "logical_id": "state_handoff_boundary",
    "path": "wbs-runs/durable-agent-bs1-basic-design/design/state-handoff-boundary.json",
    "sha256": "a8a5e2e8056ce73e5d6625b12a0ae75dd77a4d95928546870f5746a33851d9c8"
  },
  {
    "logical_id": "component_ownership_dag",
    "path": "wbs-runs/durable-agent-bs1-basic-design/design/component-ownership-dag.json",
    "sha256": "b0620c8271063290e673f1639723ea2a4f0295b2bf8a8fae667a1403f5e5a7b9"
  },
  {
    "logical_id": "component_flow_closure",
    "path": "wbs-runs/durable-agent-bs1-basic-design/design/component-flow-closure.json",
    "sha256": "87c1cd6c7614ad4f93971079a0337b61d6a97a848aa892c2d0057d0751383ce0"
  },
  {
    "logical_id": "test_sizing_gate",
    "path": "wbs-runs/durable-agent-bs1-basic-design/design/test-sizing-gate.json",
    "sha256": "c5069ba124e80d2dd9ca8dbf2e5c742caf002e25726156c98c1c156fe74ffd59"
  }
]
```

## ownership_interfaces
```json
[
  {
    "components": [
      {
        "component": "ContractPlanBoundary",
        "df": "DF1",
        "external_effects": [],
        "owns": [
          "TaskContract and PlanProposal validation",
          "deterministic normalization",
          "AcceptedPlan or TypedBlock production"
        ]
      },
      {
        "component": "SequentialTaskControl",
        "df": "DF2",
        "external_effects": [],
        "owns": [
          "one-active-task admission",
          "accepted-plan activation",
          "ordered step selection",
          "reason-step result",
          "effect dispatch decision",
          "observational assertion dispatch",
          "retry or replan decision",
          "typed result routing",
          "terminal status decision"
        ]
      },
      {
        "component": "ContainedFileEffects",
        "df": "DF3",
        "external_effects": [
          "one contained read/write/append"
        ],
        "owns": [
          "no-symlink containment",
          "bounded file read",
          "bounded file write",
          "bounded file append",
          "observational file/hash/content/schema read execution",
          "FileEffectResult production"
        ]
      },
      {
        "component": "ExactCommandEffects",
        "df": "DF4",
        "external_effects": [
          "one exact local process spawn"
        ],
        "owns": [
          "one exact allowlisted shell:false process spawn",
          "ordinary command execution",
          "exact-command verification through the ordinary command path",
          "CommandEffectResult production"
        ]
      },
      {
        "component": "CheckpointRecovery",
        "df": "DF5",
        "external_effects": [
          "one governed checkpoint replacement"
        ],
        "owns": [
          "checkpoint bytes",
          "attempt debit",
          "current-effect intent persistence",
          "result persistence",
          "restart classification",
          "task-to-handoff settlement persistence"
        ]
      },
      {
        "component": "HandoffSettlement",
        "df": "DF6",
        "external_effects": [
          "one create-once handoff artifact commit"
        ],
        "owns": [
          "deterministic TaskHandoff rendering",
          "exact handoff key/path derivation",
          "create-once handoff commit",
          "handoff commit classification"
        ]
      }
    ],
    "forbidden_components": [
      "cross-task scheduler",
      "assignment queue",
      "delegation manager",
      "WBS dependency loader",
      "generic history service",
      "plugin model/provider port",
      "network transport",
      "PM acceptance service",
      "second file/command/verify executor",
      "shadow checkpoint or handoff store"
    ],
    "id": "owners",
    "unique_owner_rule": "Every accepted transition and external effect has exactly one owning DF. Dispatch, validation, consumption, and acknowledgement do not transfer ownership."
  },
  {
    "entries": [
      {
        "consumers": [
          "DF1"
        ],
        "name": "TaskContract+PlanProposal",
        "producer": "HostAdapter",
        "visibility": "public host input"
      },
      {
        "consumers": [
          "DF2"
        ],
        "name": "AcceptedPlan|TypedBlock",
        "producer": "DF1",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF3"
        ],
        "name": "FileEffectRequest",
        "producer": "DF2",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF2"
        ],
        "name": "FileEffectResult",
        "producer": "DF3",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF4"
        ],
        "name": "CommandEffectRequest",
        "producer": "DF2",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF2"
        ],
        "name": "CommandEffectResult",
        "producer": "DF4",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF3"
        ],
        "name": "ObservationalVerifyDispatch",
        "producer": "DF2",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF2"
        ],
        "name": "ObservationalVerifyResult",
        "producer": "DF3",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF4"
        ],
        "name": "ExactCommandVerifyRequest",
        "producer": "DF2",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF4"
        ],
        "name": "ContainmentGrantForCwd",
        "producer": "DF3",
        "visibility": "internal versioned seam"
      },
      {
        "consumers": [
          "DF5"
        ],
        "name": "CheckpointTransitionIntent",
        "producer": "DF2",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF2"
        ],
        "name": "PersistedCheckpointAck",
        "producer": "DF5",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF6"
        ],
        "name": "CommittedTerminalSnapshot",
        "producer": "DF5",
        "visibility": "internal"
      },
      {
        "consumers": [
          "DF5",
          "DF2"
        ],
        "name": "HandoffCommitResult",
        "producer": "DF6",
        "visibility": "internal"
      },
      {
        "consumers": [
          "IndependentReviewer",
          "PMReviewer"
        ],
        "name": "TaskHandoff",
        "producer": "DF6",
        "visibility": "public provisional artifact"
      }
    ],
    "id": "interfaces",
    "rule": "Each interface has exactly one producer and a finite consumer list; no interface grants new path, command, effect, persistence, scheduling, or acceptance authority."
  },
  {
    "components": [
      {
        "may_effect": false,
        "name": "EffectBoundaryValidator",
        "owner": "DF2 control boundary",
        "responsibility": "Validate the closed effect request, declared authority, canonical units, finite limits, and operation kind before persistence or effect dispatch."
      },
      {
        "may_effect": false,
        "name": "StrictNoSymlinkContainment",
        "owner": "shared DF3 containment component consumed by DF4 cwd validation",
        "responsibility": "Perform component-aware lexical containment, lstat every existing component without following symlinks, distinguish absent final targets, enforce kind rules, and immediately revalidate before one effect."
      },
      {
        "may_effect": true,
        "name": "FileEffectExecutor",
        "owner": "DF3",
        "responsibility": "Execute one bounded read, write, or append only from a validated containment grant and emit FileEffectResult."
      },
      {
        "may_effect": true,
        "name": "ExactCommandExecutor",
        "owner": "DF4",
        "responsibility": "Spawn one exact allowlisted argv record with a contained cwd, shell fixed false, bounded timeout and output capture, then emit CommandEffectResult."
      },
      {
        "may_effect": false,
        "name": "VerifyRouter",
        "owner": "DF4 for command checks and DF2 for observational assertion dispatch",
        "responsibility": "Route observational checks to bounded reads and every process-based check through ExactCommandExecutor with the same persistence, attempt, result, and recovery path as an ordinary command step."
      }
    ],
    "id": "component_ownership",
    "one_tracked_effect_path": true,
    "persist_before_effect_dependency": "DF2/DF5 must durably record current step and debit the attempt before FileEffectExecutor or ExactCommandExecutor is invoked."
  }
]
```

## dag
```json
{
  "acyclic": true,
  "edge_semantics": "consumer -> provider",
  "edges": [
    {
      "from": "DF2",
      "interface": "AcceptedPlan|TypedBlock",
      "to": "DF1"
    },
    {
      "from": "DF2",
      "interface": "file effects and observational bounded reads",
      "to": "DF3"
    },
    {
      "from": "DF2",
      "interface": "ordinary command and exact-command verification",
      "to": "DF4"
    },
    {
      "from": "DF2",
      "interface": "checkpoint transitions and acknowledgements",
      "to": "DF5"
    },
    {
      "from": "DF2",
      "interface": "handoff commit classification",
      "to": "DF6"
    },
    {
      "from": "DF4",
      "interface": "versioned cwd containment grant",
      "to": "DF3"
    },
    {
      "from": "DF6",
      "interface": "committed terminal snapshot and settlement",
      "to": "DF5"
    }
  ],
  "forbidden_edges": [
    "any DF -> WBS graph",
    "any DF -> model/provider",
    "DF3 -> DF4 command ownership",
    "DF4 -> DF3 observational dispatch ownership",
    "DF5 -> generic history",
    "DF6 -> PM acceptance"
  ],
  "id": "dependency_dag",
  "topological_order_provider_first": [
    "DF1",
    "DF3",
    "DF4",
    "DF5",
    "DF6",
    "DF2"
  ]
}
```

## flows
```json
[
  {
    "flows": [
      {
        "closed_result": "executing or typed pre-effect block",
        "flow_id": "N01",
        "name": "admit_and_activate",
        "trace": [
          {
            "emit": "TaskContract+PlanProposal",
            "owner": "HostAdapter",
            "to": "DF1"
          },
          {
            "emit": "AcceptedPlan|TypedBlock",
            "owner": "DF1",
            "to": "DF2"
          },
          {
            "action": "one-active-task admission and accepted-plan activation",
            "owner": "DF2"
          },
          {
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist accepted plan checkpoint",
            "emit": "PersistedCheckpointAck",
            "owner": "DF5",
            "to": "DF2"
          }
        ]
      },
      {
        "closed_result": "next step or terminal decision",
        "flow_id": "N02",
        "name": "reason_step",
        "trace": [
          {
            "action": "select and execute reason step; produce concise reason-step result",
            "owner": "DF2"
          },
          {
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist immutable result and next position",
            "emit": "PersistedCheckpointAck",
            "owner": "DF5",
            "to": "DF2"
          }
        ]
      },
      {
        "closed_result": "next step or terminal decision",
        "flow_id": "N03",
        "name": "file_step",
        "trace": [
          {
            "action": "select file step and debit attempt",
            "owner": "DF2"
          },
          {
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist debit and exact current intent before effect",
            "emit": "PersistedCheckpointAck",
            "owner": "DF5",
            "to": "DF2"
          },
          {
            "emit": "FileEffectRequest",
            "owner": "DF2",
            "to": "DF3"
          },
          {
            "action": "one contained file effect",
            "emit": "FileEffectResult",
            "owner": "DF3",
            "to": "DF2"
          },
          {
            "action": "route typed result",
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist result and clear current",
            "emit": "PersistedCheckpointAck",
            "owner": "DF5",
            "to": "DF2"
          }
        ]
      },
      {
        "closed_result": "next step or terminal decision",
        "flow_id": "N04",
        "name": "command_step",
        "trace": [
          {
            "action": "select command step and debit attempt",
            "owner": "DF2"
          },
          {
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist debit and exact current intent before effect",
            "emit": "PersistedCheckpointAck",
            "owner": "DF5",
            "to": "DF2"
          },
          {
            "emit": "CommandEffectRequest",
            "owner": "DF2",
            "to": "DF4"
          },
          {
            "action": "one exact allowlisted shell:false process",
            "emit": "CommandEffectResult",
            "owner": "DF4",
            "to": "DF2"
          },
          {
            "action": "route typed result",
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist result and clear current",
            "emit": "PersistedCheckpointAck",
            "owner": "DF5",
            "to": "DF2"
          }
        ]
      },
      {
        "closed_result": "next step or terminal decision",
        "flow_id": "N05",
        "name": "verify_step",
        "persist_before_effect": true,
        "routes": [
          {
            "kind": "file_hash_content_or_schema",
            "trace": [
              "DF2 CheckpointTransitionIntent -> DF5 PersistedCheckpointAck",
              "DF2 ObservationalVerifyDispatch -> DF3",
              "DF3 ObservationalVerifyResult -> DF2",
              "DF2 CheckpointTransitionIntent -> DF5 PersistedCheckpointAck"
            ]
          },
          {
            "kind": "exact_command",
            "trace": [
              "DF2 CheckpointTransitionIntent -> DF5 PersistedCheckpointAck",
              "DF2 ExactCommandVerifyRequest -> DF4 ordinary command path",
              "DF4 CommandEffectResult -> DF2",
              "DF2 CheckpointTransitionIntent -> DF5 PersistedCheckpointAck"
            ]
          }
        ],
        "separate_executor_or_retry_channel": false
      },
      {
        "closed_result": "provisional artifact; no acceptance",
        "flow_id": "N06",
        "name": "provisional_handoff",
        "trace": [
          {
            "action": "decide completed_provisional and stop normal steps",
            "owner": "DF2"
          },
          {
            "emit": "CheckpointTransitionIntent",
            "owner": "DF2",
            "to": "DF5"
          },
          {
            "action": "persist terminal and handoff_pending",
            "emit": "CommittedTerminalSnapshot",
            "owner": "DF5",
            "to": "DF6"
          },
          {
            "action": "render and create-once commit",
            "emit": "HandoffCommitResult",
            "owner": "DF6",
            "to": [
              "DF5",
              "DF2"
            ]
          },
          {
            "action": "persist successful settlement and release idle",
            "owner": "DF5"
          },
          {
            "emit": "TaskHandoff",
            "owner": "DF6",
            "to": [
              "IndependentReviewer",
              "PMReviewer"
            ]
          }
        ]
      }
    ],
    "id": "normal_flows",
    "interface_rule": "Every cross-owner edge uses an exact accepted interface name from the frozen ownership DAG."
  },
  {
    "all_edges_closed": true,
    "common_trace": [
      "DF2 decides terminal and stops normal dispatch",
      "DF2 CheckpointTransitionIntent -> DF5",
      "DF5 marks remaining steps not_executed, persists terminal, enters handoff_pending",
      "DF5 CommittedTerminalSnapshot -> DF6",
      "DF6 create-once commit -> HandoffCommitResult to DF5 and DF2",
      "DF5 persists settlement then idle",
      "DF6 TaskHandoff -> external reviewers"
    ],
    "direct_terminal_to_idle": false,
    "id": "terminal_flows",
    "statuses": [
      {
        "flow_id": "T01",
        "special_rule": "never accepted internally",
        "status": "completed_provisional"
      },
      {
        "flow_id": "T02",
        "special_rule": "block detail and evidence retained",
        "status": "blocked"
      },
      {
        "flow_id": "T03",
        "special_rule": "failure detail and evidence retained",
        "status": "failed"
      },
      {
        "flow_id": "T04",
        "special_rule": "debit retained; no automatic retry, replay, resume, or refund",
        "status": "unknown_outcome"
      }
    ]
  },
  {
    "id": "restart_routes",
    "routes": [
      {
        "condition": "checkpoint has no persisted current effect",
        "effect_replay": false,
        "owner_trace": [
          "DF5 validates checkpoint and restart position",
          "DF5 PersistedCheckpointAck -> DF2",
          "DF2 selects next incomplete step"
        ],
        "route_id": "R01"
      },
      {
        "condition": "debit/current intent persisted without settled result",
        "effect_replay": false,
        "owner_trace": [
          "DF5 classifies unknown_outcome and retains debit",
          "DF5 PersistedCheckpointAck -> DF2",
          "DF2 performs no executor dispatch",
          "DF5 terminalizes to handoff_pending",
          "DF5 CommittedTerminalSnapshot -> DF6"
        ],
        "refund": false,
        "route_id": "R02"
      },
      {
        "condition": "completed result persisted",
        "effect_replay": false,
        "owner_trace": [
          "DF5 validates immutable result",
          "DF5 PersistedCheckpointAck -> DF2",
          "DF2 skips completed step"
        ],
        "route_id": "R03"
      },
      {
        "condition": "handoff_pending and artifact absent",
        "owner_trace": [
          "DF5 CommittedTerminalSnapshot -> DF6",
          "DF6 reconstructs identical TaskHandoff and create-once commits",
          "DF6 HandoffCommitResult -> DF5 and DF2",
          "DF5 persists settlement"
        ],
        "route_id": "R04",
        "task_effect_replay": false
      },
      {
        "condition": "handoff artifact exists",
        "overwrite": false,
        "owner_trace": [
          "DF6 classifies corruption first, then identity/stale, then fully-current equality, then fully-current conflict",
          "DF6 HandoffCommitResult -> DF5 and DF2",
          "DF5 settles only current idempotent success"
        ],
        "route_id": "R05",
        "task_effect_replay": false
      },
      {
        "condition": "checkpoint settlement and artifact agree",
        "owner_trace": [
          "DF5 validates settlement",
          "DF5 PersistedCheckpointAck -> DF2",
          "DF2 releases idle"
        ],
        "pm_ack_required": false,
        "route_id": "R06"
      }
    ],
    "unknown_rule": "UNKNOWN has no outgoing retry, replay, refund, or resume edge."
  },
  {
    "hidden_stores": [],
    "id": "persistence_and_result_closure",
    "no_replay": "Completed effects/results are immutable and skipped; persisted-current recovery terminalizes UNKNOWN without executor dispatch.",
    "other_persistence_owners": [],
    "persist_before_effect": "DF5 PersistedCheckpointAck is mandatory before DF2 emits FileEffectRequest, CommandEffectRequest, ObservationalVerifyDispatch, or ExactCommandVerifyRequest.",
    "persistence_owners": [
      {
        "bytes": [
          "checkpoint",
          "accepted plan",
          "attempt debit/current intent",
          "step results",
          "terminal state",
          "handoff settlement"
        ],
        "effect": "one governed checkpoint replacement",
        "owner": "DF5:CheckpointRecovery"
      },
      {
        "bytes": [
          "one canonical TaskHandoff"
        ],
        "effect": "one exact create-once artifact commit",
        "owner": "DF6:HandoffSettlement"
      }
    ],
    "result_routes": [
      {
        "consumers": [
          "DF2"
        ],
        "producer": "DF1",
        "result": "AcceptedPlan|TypedBlock",
        "terminal_sink": "DF2 decision then DF5 persistence if activated"
      },
      {
        "consumers": [
          "DF2"
        ],
        "producer": "DF3",
        "result": "FileEffectResult",
        "terminal_sink": "DF5 via CheckpointTransitionIntent"
      },
      {
        "consumers": [
          "DF2"
        ],
        "producer": "DF4",
        "result": "CommandEffectResult",
        "terminal_sink": "DF5 via CheckpointTransitionIntent"
      },
      {
        "consumers": [
          "DF2"
        ],
        "producer": "DF3",
        "result": "ObservationalVerifyResult",
        "terminal_sink": "DF5 via CheckpointTransitionIntent"
      },
      {
        "consumers": [
          "DF2"
        ],
        "producer": "DF5",
        "result": "PersistedCheckpointAck",
        "terminal_sink": "DF2 next decision"
      },
      {
        "consumers": [
          "DF5",
          "DF2"
        ],
        "producer": "DF6",
        "result": "HandoffCommitResult",
        "terminal_sink": "DF5 settlement or retained handoff_pending"
      },
      {
        "consumers": [
          "IndependentReviewer",
          "PMReviewer"
        ],
        "producer": "DF6",
        "result": "TaskHandoff",
        "terminal_sink": "external decision only"
      }
    ]
  },
  {
    "consumer_rule": "A future feature task must bind the accepted hash of this flow-closure artifact in addition to the exact listed hashes; this design does not dispatch it.",
    "id": "downstream_manifests",
    "manifests": [
      {
        "exact_input_hashes": {
          "dto_plan": "bec9c536ba4076366d00aafaa1d044d2c2df59e67c0ad7fab7df6febe2eb6284",
          "effect": "3cb1e42149d16fdb6d69c131a90d62417d4575ee379cd590122e3ef5c3f149f5",
          "ownership_dag": "b0620c8271063290e673f1639723ea2a4f0295b2bf8a8fae667a1403f5e5a7b9",
          "state": "a8a5e2e8056ce73e5d6625b12a0ae75dd77a4d95928546870f5746a33851d9c8"
        },
        "manifest_id": "DF2-FS2",
        "owner": "DF2:SequentialTaskControl",
        "required_interfaces": [
          "AcceptedPlan|TypedBlock",
          "CheckpointTransitionIntent",
          "PersistedCheckpointAck",
          "FileEffectRequest",
          "FileEffectResult",
          "CommandEffectRequest",
          "CommandEffectResult",
          "ObservationalVerifyDispatch",
          "ObservationalVerifyResult",
          "ExactCommandVerifyRequest",
          "HandoffCommitResult"
        ]
      },
      {
        "exact_input_hashes": {
          "dto_plan": "bec9c536ba4076366d00aafaa1d044d2c2df59e67c0ad7fab7df6febe2eb6284",
          "effect": "3cb1e42149d16fdb6d69c131a90d62417d4575ee379cd590122e3ef5c3f149f5",
          "ownership_dag": "b0620c8271063290e673f1639723ea2a4f0295b2bf8a8fae667a1403f5e5a7b9"
        },
        "manifest_id": "DF3-FS3",
        "owner": "DF3:ContainedFileEffects",
        "required_interfaces": [
          "FileEffectRequest",
          "FileEffectResult",
          "ObservationalVerifyDispatch",
          "ObservationalVerifyResult",
          "ContainmentGrantForCwd"
        ]
      },
      {
        "exact_input_hashes": {
          "dto_plan": "bec9c536ba4076366d00aafaa1d044d2c2df59e67c0ad7fab7df6febe2eb6284",
          "effect": "3cb1e42149d16fdb6d69c131a90d62417d4575ee379cd590122e3ef5c3f149f5",
          "ownership_dag": "b0620c8271063290e673f1639723ea2a4f0295b2bf8a8fae667a1403f5e5a7b9"
        },
        "manifest_id": "DF4-FS4",
        "owner": "DF4:ExactCommandEffects",
        "required_interfaces": [
          "CommandEffectRequest",
          "CommandEffectResult",
          "ExactCommandVerifyRequest",
          "ContainmentGrantForCwd"
        ]
      },
      {
        "exact_input_hashes": {
          "ownership_dag": "b0620c8271063290e673f1639723ea2a4f0295b2bf8a8fae667a1403f5e5a7b9",
          "state": "a8a5e2e8056ce73e5d6625b12a0ae75dd77a4d95928546870f5746a33851d9c8"
        },
        "manifest_id": "DF6-FS6",
        "owner": "DF6:HandoffSettlement",
        "required_interfaces": [
          "CommittedTerminalSnapshot",
          "HandoffCommitResult",
          "TaskHandoff"
        ]
      }
    ]
  }
]
```

## tests
```json
[
  {
    "id": "test_layers",
    "layers": [
      {
        "id": "schema_unit",
        "observable": "closed DTO parse/normalize/result equality and reject code"
      },
      {
        "id": "immutable_oracle",
        "observable": "canonical bytes/hash/order, zero-call spies, unchanged existing bytes"
      },
      {
        "id": "component_integration",
        "observable": "typed request/result and owner-to-owner interface trace"
      },
      {
        "id": "mutation",
        "observable": "one invalid field/route reaches named first rejection gate with zero effect"
      },
      {
        "id": "restart",
        "observable": "checkpoint cut resumes, skips, or terminalizes without replay"
      },
      {
        "id": "collision",
        "observable": "absent/same-byte/conflict/corrupt/stale/cross-identity first-match class"
      },
      {
        "id": "vertical_integration",
        "observable": "contract-to-provisional-handoff trace with persisted debits/results"
      },
      {
        "id": "future_e2e",
        "observable": "local host adapter submits one task and observes provisional settlement; no PM acceptance"
      }
    ],
    "verification_rule": "Every row is a future executable fixture with deterministic state/result/spy assertions; model judgment is never a test oracle."
  },
  {
    "coverage_rule": "Test numbers must equal the integer set 1..15 exactly once.",
    "id": "compatibility_tests",
    "tests": [
      {
        "assertion": "AcceptedPlan bytes, ordered steps, limits, and downstream trace are equal except provenance origin",
        "claim": "Standalone and WBS-derived origins normalize to identical core behavior.",
        "intended_gate": "DF1 normalized-core equality",
        "layers": [
          "schema_unit",
          "immutable_oracle",
          "vertical_integration"
        ],
        "negative": "origin changes a core limit or step",
        "no_effect": true,
        "number": 1,
        "owners": [
          "DF1",
          "DF2"
        ],
        "positive": "same contract/proposal with two allowed origins"
      },
      {
        "assertion": "task reaches executing with WBS-loader spy count zero",
        "claim": "A WBS-derived task runs without loading the WBS graph.",
        "intended_gate": "closed component and forbidden WBS-loader gate",
        "layers": [
          "component_integration",
          "vertical_integration"
        ],
        "negative": "control requests dependency graph/readiness lookup",
        "no_effect": true,
        "number": 2,
        "owners": [
          "DF1",
          "DF2"
        ],
        "positive": "closed WBS-derived TaskContract contains all execution authority"
      },
      {
        "assertion": "AcceptedPlan authority equals contract authority",
        "claim": "WBS metadata cannot widen paths, commands, retries, or budget.",
        "intended_gate": "DF1 authority-subset validation",
        "layers": [
          "schema_unit",
          "mutation"
        ],
        "negative": "metadata adds path/command/retry/budget",
        "no_effect": true,
        "number": 3,
        "owners": [
          "DF1",
          "DF2"
        ],
        "positive": "metadata stays within TaskContract ceilings"
      },
      {
        "assertion": "valid fixture accepted; effect and model spies remain zero during validation",
        "claim": "Missing, malformed, stale, or mismatched PlanProposal rejects before effect with zero plugin model calls.",
        "intended_gate": "DF1 proposal identity/schema gate",
        "layers": [
          "schema_unit",
          "immutable_oracle",
          "mutation"
        ],
        "negative": "four fixtures: missing, malformed, stale, mismatched proposal",
        "no_effect": true,
        "number": 4,
        "owners": [
          "DF1"
        ],
        "positive": "current matching proposal emits AcceptedPlan"
      },
      {
        "assertion": "second returns typed BUSY; active identity/checkpoint unchanged",
        "claim": "A second assignment rejects while executing.",
        "intended_gate": "DF2 one-active-task admission",
        "layers": [
          "component_integration",
          "mutation"
        ],
        "negative": "admit second assignment during executing",
        "no_effect": true,
        "number": 5,
        "owners": [
          "DF2"
        ],
        "positive": "single assignment enters executing"
      },
      {
        "assertion": "second returns BUSY and no queue entry",
        "claim": "A second assignment rejects while handoff_pending.",
        "intended_gate": "DF2 busy-state admission",
        "layers": [
          "component_integration",
          "collision",
          "mutation"
        ],
        "negative": "admit second before successful create-once settlement",
        "no_effect": true,
        "number": 6,
        "owners": [
          "DF2",
          "DF5",
          "DF6"
        ],
        "positive": "handoff_pending retains busy until settlement"
      },
      {
        "assertion": "remaining steps not_executed; matching status reaches canonical TaskHandoff",
        "claim": "All four terminal statuses bypass remaining steps and commit the correct provisional handoff.",
        "intended_gate": "DF2 terminal dispatch gate",
        "layers": [
          "component_integration",
          "vertical_integration"
        ],
        "negative": "terminal fixture dispatches a remaining normal step",
        "no_effect": true,
        "number": 7,
        "owners": [
          "DF2",
          "DF5",
          "DF6"
        ],
        "positive": "four fixtures completed_provisional/blocked/failed/unknown_outcome"
      },
      {
        "assertion": "state becomes idle and next assignment admits with PM-ack spy zero",
        "claim": "After atomic TaskHandoff commit the Agent accepts another task without PM acknowledgement.",
        "intended_gate": "DF5 settlement-before-release gate",
        "layers": [
          "component_integration",
          "collision",
          "future_e2e"
        ],
        "negative": "release idle before successful commit/settlement",
        "no_effect": true,
        "number": 8,
        "owners": [
          "DF5",
          "DF6",
          "DF2"
        ],
        "positive": "current create-once commit plus persisted settlement"
      },
      {
        "assertion": "handoff_pending retained; executor call counts unchanged",
        "claim": "Handoff commit failure stays busy and never replays task effects.",
        "intended_gate": "DF5/DF6 settlement failure gate",
        "layers": [
          "collision",
          "restart",
          "component_integration"
        ],
        "negative": "failure transitions idle or redispatches task effect",
        "no_effect": true,
        "number": 9,
        "owners": [
          "DF6",
          "DF5",
          "DF2"
        ],
        "positive": "injected commit failure"
      },
      {
        "assertion": "re-rendered bytes equal oracle; task-effect spy zero",
        "claim": "Restart before handoff commit reconstructs the correct handoff without replay.",
        "intended_gate": "R04 terminal-snapshot recovery",
        "layers": [
          "restart",
          "immutable_oracle",
          "collision"
        ],
        "negative": "restart selects any normal/effect step",
        "no_effect": true,
        "number": 10,
        "owners": [
          "DF5",
          "DF6"
        ],
        "positive": "terminal checkpoint with absent artifact"
      },
      {
        "assertion": "settlement validates and DF2 releases idle",
        "claim": "Restart after handoff commit returns idle.",
        "intended_gate": "DF6 first-match identity/conflict then DF5 agreement gate",
        "layers": [
          "restart",
          "collision"
        ],
        "negative": "artifact identity/bytes conflict with settlement",
        "no_effect": true,
        "number": 11,
        "owners": [
          "DF5",
          "DF6",
          "DF2"
        ],
        "positive": "checkpoint and current artifact agree"
      },
      {
        "assertion": "debit/current persisted; one ordinary-path shell:false DF4 spawn; typed result persisted",
        "claim": "Command-based verify uses tracked DF4 path and undeclared cases reject before effect.",
        "intended_gate": "TaskContract allowlist then unique DF4 process owner",
        "layers": [
          "component_integration",
          "mutation",
          "vertical_integration"
        ],
        "negative": "undeclared command or DF2 direct spawn",
        "no_effect": true,
        "number": 12,
        "owners": [
          "DF2",
          "DF4",
          "DF5"
        ],
        "positive": "declared exact-command verify"
      },
      {
        "assertion": "success and exact existing bytes unchanged",
        "claim": "Same-byte recommit is idempotent; conflicting, stale, or cross-execution commit rejects without overwrite.",
        "intended_gate": "DF6 first-match collision classification",
        "layers": [
          "collision",
          "immutable_oracle",
          "mutation"
        ],
        "negative": "corrupt, stale, cross-execution, or current conflicting bytes",
        "no_effect": true,
        "number": 13,
        "owners": [
          "DF6"
        ],
        "positive": "absent create then same-key same-byte recommit"
      },
      {
        "assertion": "canonical bytes/hash equal and status remains provisional",
        "claim": "TaskHandoff is deterministic and always provisional.",
        "intended_gate": "TaskHandoff closed schema and authority gate",
        "layers": [
          "schema_unit",
          "immutable_oracle",
          "mutation"
        ],
        "negative": "accepted/next_task/PM-ack field injected",
        "no_effect": true,
        "number": 14,
        "owners": [
          "DF6"
        ],
        "positive": "same committed terminal state rendered twice"
      },
      {
        "assertion": "DF1-DF5 interface bytes and owner traces equal",
        "claim": "Future adapter compatibility does not change DF1-DF5 contracts.",
        "intended_gate": "DF1 closed schema then frozen interface/owner gate",
        "layers": [
          "schema_unit",
          "component_integration",
          "vertical_integration",
          "future_e2e"
        ],
        "negative": "adapter adds field, authority, owner, or alternate effect route",
        "no_effect": true,
        "number": 15,
        "owners": [
          "DF1",
          "DF2",
          "DF3",
          "DF4",
          "DF5"
        ],
        "positive": "two adapters produce identical closed TaskContract/PlanProposal"
      }
    ]
  },
  {
    "id": "invariant_matrix",
    "invariants": [
      {
        "assertion": "accepted authority equals contract",
        "gate": "DF1 schema/subset",
        "id": "closed_contract_authority",
        "layers": [
          "schema_unit",
          "mutation"
        ],
        "negative": "unknown/widening field",
        "no_effect": true,
        "owners": [
          "DF1"
        ],
        "positive": "valid closed contract/proposal"
      },
      {
        "assertion": "one identity only",
        "gate": "DF2 admission",
        "id": "one_active_task",
        "layers": [
          "component_integration",
          "mutation"
        ],
        "negative": "second assignment in any busy state",
        "no_effect": true,
        "owners": [
          "DF2"
        ],
        "positive": "one active assignment"
      },
      {
        "assertion": "ordered event log debit+intent before dispatch",
        "gate": "DF2 dispatch precondition",
        "id": "persist_before_effect",
        "layers": [
          "component_integration",
          "restart",
          "mutation"
        ],
        "negative": "dispatch before ack",
        "no_effect": true,
        "owners": [
          "DF2",
          "DF5"
        ],
        "positive": "ack precedes every effect request"
      },
      {
        "assertion": "DF3 read count one; DF4 spawn zero",
        "gate": "verify-kind ownership",
        "id": "observational_verify_routing",
        "layers": [
          "component_integration",
          "mutation"
        ],
        "negative": "route observation to DF4",
        "no_effect": true,
        "owners": [
          "DF2",
          "DF3"
        ],
        "positive": "file/hash/content/schema verify uses bounded DF3 read"
      },
      {
        "assertion": "one allowlisted shell:false spawn",
        "gate": "unique DF4 process owner",
        "id": "command_verify_routing",
        "layers": [
          "component_integration",
          "mutation"
        ],
        "negative": "DF2 spawn or separate verify executor",
        "no_effect": true,
        "owners": [
          "DF2",
          "DF4"
        ],
        "positive": "exact verify uses ordinary DF4 command path"
      },
      {
        "assertion": "no direct terminal-to-idle edge",
        "gate": "terminal common-trace closure",
        "id": "terminal_convergence",
        "layers": [
          "component_integration",
          "vertical_integration"
        ],
        "negative": "terminal bypasses handoff",
        "no_effect": true,
        "owners": [
          "DF2",
          "DF5",
          "DF6"
        ],
        "positive": "four terminal statuses share handoff_pending trace"
      },
      {
        "assertion": "executor call count zero after restart",
        "gate": "R02/R03 recovery classification",
        "id": "restart_no_replay",
        "layers": [
          "restart",
          "mutation"
        ],
        "negative": "retry/refund/replay unknown or completed",
        "no_effect": true,
        "owners": [
          "DF5",
          "DF2"
        ],
        "positive": "completed skips; persisted-current terminalizes unknown"
      },
      {
        "assertion": "create or idempotent success",
        "gate": "DF6 first-match collision order",
        "id": "create_once_identity",
        "layers": [
          "collision",
          "immutable_oracle"
        ],
        "negative": "corrupt/stale/cross-identity/conflict",
        "no_effect": true,
        "owners": [
          "DF6"
        ],
        "positive": "absent/same-byte current cases"
      },
      {
        "assertion": "acceptance fields absent",
        "gate": "closed handoff schema/authority",
        "id": "provisional_only",
        "layers": [
          "schema_unit",
          "mutation"
        ],
        "negative": "accepted or next-task field",
        "no_effect": true,
        "owners": [
          "DF6"
        ],
        "positive": "all handoffs use provisional terminal status"
      },
      {
        "assertion": "model/WBS/queue/delegation/network spies zero",
        "gate": "closed component/effect set",
        "id": "no_hidden_orchestration_or_model",
        "layers": [
          "immutable_oracle",
          "mutation",
          "vertical_integration"
        ],
        "negative": "add hidden executor/store/scheduler/model port",
        "no_effect": true,
        "owners": [
          "DF1",
          "DF2",
          "DF3",
          "DF4",
          "DF5",
          "DF6"
        ],
        "positive": "frozen six-owner graph"
      }
    ]
  },
  {
    "id": "artifact_negative_vectors",
    "vectors": [
      {
        "expected": "reject",
        "gate": "test number set equals 1..15",
        "id": "missing_test_number"
      },
      {
        "expected": "reject",
        "gate": "test number uniqueness",
        "id": "duplicate_test_number"
      },
      {
        "expected": "reject",
        "gate": "nonempty frozen DF owner list",
        "id": "missing_owner"
      },
      {
        "expected": "reject",
        "gate": "positive fixture and observable assertion required",
        "id": "missing_positive"
      },
      {
        "expected": "reject",
        "gate": "negative mutation and no-effect assertion required",
        "id": "missing_negative"
      },
      {
        "expected": "reject",
        "gate": "negative names intended first gate",
        "id": "wrong_rejection_gate"
      },
      {
        "expected": "reduce_or_split",
        "gate": "bounded units, burden, exclusions, risk, falsifier, triggers required",
        "id": "unsupported_df_marked_feasible"
      },
      {
        "expected": "reject before downstream use",
        "gate": "accepted ownership and flow hashes exact",
        "id": "stale_design_hash"
      }
    ]
  }
]
```

## sizing
```json
[
  {
    "id": "df_sizing",
    "judgment_rule": "Conditional feasibility is a falsifiable design estimate, not implementation acceptance. Any split trigger blocks its feature and requires reduce/split before implementation.",
    "rows": [
      {
        "bounded_units": [
          "TaskContract/PlanProposal validation",
          "deterministic normalization",
          "history/replan validation",
          "typed result construction",
          "zero-model spy proof"
        ],
        "conclusion": "feasible_one_feature_sprint_conditional",
        "dependencies": [],
        "df": "DF1",
        "exclusions": [
          "step execution",
          "effects",
          "checkpoint runtime",
          "WBS orchestration",
          "host/provider integration"
        ],
        "falsifier": "any trigger observed changes conclusion to reduce_or_split",
        "inputs": [
          "accepted P0",
          "accepted DTO boundary"
        ],
        "outputs": [
          "AcceptedPlan|TypedBlock",
          "closed DTO codecs"
        ],
        "owner": "ContractPlanBoundary",
        "residual_risk": "production DTO choice may reopen P0",
        "split_triggers": [
          "P0 contradiction",
          "plugin LLM/WBS/scheduler/queue/delegation/network required",
          "bounded units plus independent verification exceed one sprint"
        ],
        "test_burden": [
          "schema/unit",
          "immutable oracle",
          "adapter equality",
          "invalid/stale proposal mutations"
        ]
      },
      {
        "bounded_units": [
          "one-active reducer",
          "N01-N06 selection/dispatch/routing",
          "DF5 ack handshake",
          "four terminal decisions",
          "R01-R06 reactions"
        ],
        "conclusion": "feasible_one_feature_sprint_conditional",
        "dependencies": [
          "DF1",
          "DF3",
          "DF4",
          "DF5",
          "DF6"
        ],
        "df": "DF2",
        "exclusions": [
          "effect execution",
          "persistence bytes",
          "handoff commit",
          "cross-task scheduling"
        ],
        "falsifier": "unclosed reducer state or trigger changes conclusion to reduce_or_split",
        "inputs": [
          "AcceptedPlan|TypedBlock",
          "typed DF3-DF6 results/acks"
        ],
        "outputs": [
          "ordered dispatch decisions",
          "typed terminal decisions"
        ],
        "owner": "SequentialTaskControl",
        "residual_risk": "state-space interaction count",
        "split_triggers": [
          "scheduler/queue/delegation required",
          "new effect/persistence owner required",
          "bounded units plus independent verification exceed one sprint"
        ],
        "test_burden": [
          "reducer unit matrix",
          "busy-state mutations",
          "terminal traces",
          "restart reactions",
          "verify routing"
        ]
      },
      {
        "bounded_units": [
          "no-symlink containment",
          "bounded read/write/append",
          "observational verify read",
          "typed bounded results",
          "nine P1 ceilings"
        ],
        "conclusion": "feasible_one_feature_sprint_conditional",
        "dependencies": [],
        "df": "DF3",
        "exclusions": [
          "general filesystem service",
          "hostile concurrency",
          "cross-platform proof"
        ],
        "falsifier": "any trigger changes conclusion to reduce_or_split",
        "inputs": [
          "FileEffectRequest",
          "ObservationalVerifyDispatch"
        ],
        "outputs": [
          "FileEffectResult",
          "ObservationalVerifyResult",
          "ContainmentGrantForCwd"
        ],
        "owner": "ContainedFileEffects",
        "residual_risk": "platform-specific path semantics",
        "split_triggers": [
          "hostile concurrency or portability proof required",
          "general filesystem service required",
          "bounded units plus independent verification exceed one sprint"
        ],
        "test_burden": [
          "path topology matrix",
          "limit boundaries",
          "zero-outside-effect oracle",
          "observational route"
        ]
      },
      {
        "bounded_units": [
          "one exact shell:false process",
          "allowlist/cwd validation",
          "timeout/output settlement",
          "ordinary-path command verification",
          "typed bounded result"
        ],
        "conclusion": "feasible_one_feature_sprint_conditional",
        "dependencies": [
          "DF3 containment interface"
        ],
        "df": "DF4",
        "exclusions": [
          "general sandbox",
          "network control",
          "separate verify executor"
        ],
        "falsifier": "any trigger changes conclusion to reduce_or_split",
        "inputs": [
          "CommandEffectRequest",
          "ExactCommandVerifyRequest",
          "ContainmentGrantForCwd"
        ],
        "outputs": [
          "CommandEffectResult"
        ],
        "owner": "ExactCommandEffects",
        "residual_risk": "platform process behavior",
        "split_triggers": [
          "general sandbox/network/portability required",
          "separate verify executor required",
          "bounded units plus independent verification exceed one sprint"
        ],
        "test_burden": [
          "argv equality",
          "allowlist/cwd mutations",
          "timeout/output bounds",
          "single-spawn spy"
        ]
      },
      {
        "bounded_units": [
          "closed checkpoint/attempt/result/settlement codecs",
          "atomic replacement/integrity",
          "persist-before-effect reducer",
          "restart convergence",
          "key/hash collision classification"
        ],
        "conclusion": "feasible_one_feature_sprint_conditional",
        "dependencies": [
          "accepted DF1-DF4 manifests"
        ],
        "df": "DF5",
        "exclusions": [
          "generic history",
          "concurrent API",
          "migration",
          "retention/GC",
          "distributed/power-loss guarantee"
        ],
        "falsifier": "any trigger changes conclusion to reduce_or_split",
        "inputs": [
          "CheckpointTransitionIntent",
          "HandoffCommitResult"
        ],
        "outputs": [
          "PersistedCheckpointAck",
          "CommittedTerminalSnapshot"
        ],
        "owner": "CheckpointRecovery",
        "residual_risk": "atomicity limited to cooperative local filesystem",
        "split_triggers": [
          "generic history/orchestration required",
          "hostile concurrency/distributed transaction/migration/power-loss mechanism required",
          "bounded units plus independent verification exceed one sprint"
        ],
        "test_burden": [
          "crash-cut matrix",
          "illegal-state/accounting",
          "restart no-replay",
          "settlement agreement"
        ]
      },
      {
        "bounded_units": [
          "deterministic JSON/Markdown render",
          "exact key/path",
          "create-once commit/recommit",
          "collision classification",
          "handoff retry/settlement"
        ],
        "conclusion": "feasible_one_feature_sprint_conditional",
        "dependencies": [
          "accepted DF1-DF5 manifests"
        ],
        "df": "DF6",
        "exclusions": [
          "task acceptance",
          "PM acknowledgement protocol",
          "Team transport",
          "WBS update",
          "retention/GC",
          "product repair"
        ],
        "falsifier": "any trigger changes conclusion to reduce_or_split",
        "inputs": [
          "CommittedTerminalSnapshot"
        ],
        "outputs": [
          "HandoffCommitResult",
          "TaskHandoff"
        ],
        "owner": "HandoffSettlement",
        "residual_risk": "local create-once primitive/platform semantics",
        "split_triggers": [
          "PM acknowledgement/network required",
          "overwrite/task replay required",
          "bounded units plus independent verification exceed one sprint"
        ],
        "test_burden": [
          "canonical byte oracle",
          "collision matrix",
          "restart before/after commit",
          "busy-to-idle settlement"
        ]
      }
    ]
  },
  {
    "disposition": "provisional_test_and_sizing_candidate",
    "feature_rule": "A DF may enter future feature planning only while all cited accepted hashes remain exact, every bounded unit fits one sprint including independent verification, and no split trigger is observed.",
    "id": "implementation_gate",
    "limitations": [
      "Design mapping only; no test was executed and no feature was implemented.",
      "Future executable fixtures require feature-local approved commands and implementations.",
      "Conditional estimates assume one cooperative owner, local workspace/process/storage, and accepted boundary limits.",
      "Structural selfcheck cannot establish semantic coverage or sprint feasibility."
    ],
    "review_required": "fresh independent BS1 sizing reviewer then coordinator acceptance",
    "unsupported_rule": "Unsupported or falsified feasibility blocks that DF and yields reduce_or_split; it never defaults to feasible."
  },
  {
    "authority": "Sizing is evidence-bound design judgment only; no feature execution or acceptance.",
    "gates": [
      {
        "conclusion": "feasible_one_feature_sprint",
        "df": "DF2",
        "evidence_units": [
          "one-active-task reducer",
          "N01-N06 selection/dispatch/result routing",
          "DF5 acknowledgement handshake",
          "four terminal decisions",
          "R01-R06 control reactions"
        ],
        "sprint": "FS2",
        "stop_split": [
          "cross-task scheduler/queue/delegation required",
          "new persistence/effect owner required",
          "implementation plus independent verification exceeds one sprint"
        ]
      },
      {
        "conclusion": "feasible_one_feature_sprint",
        "df": "DF3",
        "evidence_units": [
          "no-symlink containment",
          "bounded file read/write/append",
          "observational verify read",
          "typed bounded results"
        ],
        "sprint": "FS3",
        "stop_split": [
          "hostile concurrency or cross-platform proof required",
          "general filesystem service required",
          "implementation plus independent verification exceeds one sprint"
        ]
      },
      {
        "conclusion": "feasible_one_feature_sprint",
        "df": "DF4",
        "evidence_units": [
          "one exact shell:false process",
          "timeout/output settlement",
          "ordinary-path exact-command verification",
          "typed bounded result"
        ],
        "sprint": "FS4",
        "stop_split": [
          "general process sandbox/network control required",
          "separate verify executor required",
          "implementation plus independent verification exceeds one sprint"
        ]
      },
      {
        "conclusion": "feasible_one_feature_sprint",
        "df": "DF6",
        "evidence_units": [
          "deterministic TaskHandoff render",
          "exact key/path",
          "create-once commit",
          "first-match collision classification",
          "handoff retry and settlement"
        ],
        "sprint": "FS6",
        "stop_split": [
          "PM acknowledgement or transport required for settlement",
          "overwrite/task replay required",
          "implementation plus independent verification exceeds one sprint"
        ]
      }
    ],
    "id": "sizing_gates"
  }
]
```

## limitations
```json
[
  {
    "id": "limitations",
    "items": [
      "Ownership/interface/DAG design only; sibling flow/persistence/manifest/sizing closure is excluded.",
      "No product implementation or end-to-end execution is exercised.",
      "Accepted effect-boundary cooperative-local limitations remain.",
      "Prior attempts and history are non-authoritative and did not ground a04 decisions.",
      "Exact verification, fresh independent review, and coordinator acceptance remain separate."
    ]
  },
  {
    "id": "provenance_and_limitations",
    "limitations": [
      "No product code, package export, build output, or downstream feature authority is created.",
      "P1 supports only cooperative pinned Linux/POSIX feasibility; hostile TOCTOU, hard links, mounts, Windows, remote filesystems, ACL/quota, and power-loss guarantees remain excluded.",
      "Exact allowlisting and declared-effect validation are not an adversarial subprocess sandbox; production-security certification is excluded.",
      "The existing internal MVP DTOs are topology input only and are explicitly non-authoritative where they admit delete or omit this boundary's limits.",
      "Worker completion and selfcheck success remain provisional pending fresh independent review and coordinator acceptance."
    ],
    "source_refs": [
      "wbs-runs/durable-agent-bs1-basic-design/source-receipt.json",
      "wbs-runs/durable-agent-bs1-basic-design/acceptance-matrix.json",
      "wbs-runs/durable-agent-p1-file-cwd-containment-poc/final-report.md:13-17,40-53,75-103,122-140",
      "durable-agent-plugin/package.json:10-37",
      "durable-agent-plugin/src/index.ts:16-17",
      "durable-agent-plugin/src/mvp/types.ts:11-49,94-102,144-172"
    ]
  },
  {
    "acceptance_owner": "fresh independent flow reviewer then coordinator",
    "forbidden": [
      "product edit",
      "sibling/downstream acceptance",
      "feature dispatch",
      "PM acceptance",
      "learning promotion"
    ],
    "id": "negative_vectors_and_authority",
    "limitations": [
      "design only; no runtime implementation or end-to-end exercise",
      "single cooperative owner, one active task, local workspace/process/storage",
      "accepted effect/state cooperative-local and no-power-loss limitations remain",
      "structural selfcheck cannot prove semantic flow closure"
    ],
    "provisional": true,
    "vectors": [
      {
        "expected": "reject artifact",
        "gate": "all four common-trace closures",
        "id": "open_terminal"
      },
      {
        "expected": "reject artifact",
        "gate": "closed result_routes",
        "id": "unrouted_result"
      },
      {
        "expected": "reject before dispatch",
        "gate": "DF5 ack before every observable effect",
        "id": "persistence_bypass"
      },
      {
        "expected": "terminal UNKNOWN or skip; zero dispatch",
        "gate": "R02/R03 no-replay",
        "id": "restart_replay"
      },
      {
        "expected": "reject downstream readiness",
        "gate": "manifest exact hashes/interfaces",
        "id": "stale_or_missing_manifest"
      },
      {
        "expected": "reject design",
        "gate": "DF5/DF6-only persistence and forbidden scope",
        "id": "hidden_store_or_scheduler"
      },
      {
        "expected": "reject artifact",
        "gate": "accepted owner/interface names and DAG hashes",
        "id": "ownership_id_drift"
      },
      {
        "expected": "split before feature implementation",
        "gate": "bounded units and stop/split rules",
        "id": "unsupported_sizing"
      }
    ]
  }
]
```

## governance
```json
{
  "format": "bs1-semantic-policy/1",
  "policy_sources": [
    {
      "logical_id": "integration_envelope_hardening",
      "selectors": [
        {
          "extracts": [
            {
              "relative_pointer": "/roles/design",
              "values": [
                "requirements",
                "owners",
                "interfaces",
                "dag",
                "flows",
                "handoff",
                "compatibility_tests",
                "test_layers",
                "df_sizing",
                "limitations"
              ]
            },
            {
              "relative_pointer": "/views",
              "values": [
                "machine_baseline",
                "canonical_human_projection",
                "free_narrative"
              ]
            }
          ],
          "match_field": "id",
          "match_value": "fact_model"
        },
        {
          "extracts": [
            {
              "relative_pointer": "/projection_sections",
              "values": [
                "identity",
                "source_bindings",
                "ownership_interfaces",
                "dag",
                "flows",
                "tests",
                "sizing",
                "limitations",
                "governance",
                "authority"
              ]
            },
            {
              "relative_pointer": "/equality",
              "value": "parse and recursively deep-equal every section"
            }
          ],
          "match_field": "id",
          "match_value": "renderer_contract"
        }
      ],
      "source_format": "bs1-integration-envelope-hardening/1"
    }
  ]
}
```

## authority
```json
[
  {
    "id": "authority_and_zero_model",
    "invariants": [
      "The host runtime owns planning and concise reason production; the plugin only validates, normalizes, persists, or returns a typed block.",
      "The plugin exposes no model/provider port and performs zero live model calls.",
      "No WBS parsing, cross-task readiness, scheduling, queueing, delegation, network transport, or next-task selection enters this boundary.",
      "Origin and producer metadata remain provenance and cannot authorize any effect.",
      "AcceptedPlan and StepResult remain provisional internal results; PM/reviewer retains task acceptance.",
      "Real host transport, provider authentication/routing/recovery, and production sandbox/security proof remain outside this design."
    ],
    "kind": "invariant_boundary"
  },
  {
    "forbidden": [
      "delete",
      "rename",
      "chmod",
      "arbitrary_shell",
      "network_effect",
      "undeclared_path",
      "undeclared_effect",
      "verify_only_effect_channel",
      "symlink_component_or_final_target",
      "parallel_effects"
    ],
    "id": "effect_scope",
    "legacy_dto_disposition": "non_authoritative_and_rejected_where_it_admits_delete",
    "supported_command_mode": "exact_non_shell_local_process",
    "supported_file_operations": [
      "read",
      "write",
      "append"
    ],
    "supported_verify_modes": [
      "observational_file_assertion",
      "tracked_exact_command"
    ]
  },
  {
    "authority": "design only; no product edit, FS5/FS6 execution, runtime effect, acceptance, downstream dispatch, or learning promotion",
    "id": "evidence_limits_and_authority",
    "negative_vectors": [
      "effect_before_debit",
      "unknown_retry",
      "completed_replay",
      "direct_terminal_to_idle",
      "same_key_different_bytes",
      "corrupt_existing",
      "stale_plan",
      "cross_execution",
      "stale_revision"
    ],
    "not_claimed": [
      "hostile concurrent-writer safety",
      "distributed locking or transactions",
      "remote stores or filesystems",
      "power-loss durability or fsync semantics",
      "retention or GC",
      "migration or rollback",
      "production readiness",
      "cross-platform correctness"
    ],
    "supported": [
      "single cooperative owner",
      "one active task",
      "local namespace",
      "observed same-directory and same-device operations"
    ]
  }
]
```

