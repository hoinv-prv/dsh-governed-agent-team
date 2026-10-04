# Source ownership and verification

| Design | Source owner | Focused evidence |
|---|---|---|
| DD §7 reserved/refresh | host lifecycle agent: DSH subagent, core/agent, core/agent-loop | reserved state/error/idempotency/restart + per-request retry/context/cutoff |
| DD §7 capabilities | capability agent: DSH core/tools and delegator Consumers | direct/alias/nested/PTC policies before side effects |
| DD §7 authority | authority agent: GAT core/tools + DSH authenticated ingress | HUMAN receipt negatives, canonical task association, full mode/mission/plan matrix |
| formal consistency/build/review | root, Luna inventory/mappings | independent source/build observation, doc/SDK gates and review |

Agents must read root/DSH AGENTS and resolved formal designs before edits. Root intended delta exists first; host owner writes corresponding DSH architecture/subsystem/README/Agent Note intended prose before source. Shared file edits are coordinated with root. Deployment separate.
