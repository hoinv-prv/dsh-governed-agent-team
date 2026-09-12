# Upgrade Reconcile Record — template (AP-CR-27 / FR-AI-09/10)

HUMAN per-change decision when reconciling an Instance against a newer Blueprint (`/aiws-agent-upgrade`).
The tool PRESENTS; the HUMAN decides; the tool records the decision (re-pin + snapshot + `reconcile_log`). The
instance-learned layer (`memory/`, `training/`, `context/`, `local_guidelines`) is **never** auto-overwritten.

## Drift
- instance: `<instance_id>`  ·  pinned `<from_version>` → current `<to_version>`  ·  signal: `[outdated]|[drift]`

## Per-change decisions (adopt vs skip — by rationale)
| Blueprint change (kind · why) | Instance side (customization/learned · why) | Decision | Note |
|---|---|---|---|
| `<kind: fix/improvement/breaking · why>` | `<override/learned · why>` | adopt / skip | `<why this call — anti-degrade>` |

> Adopt = HUMAN applies it to the **instance-override** layer (manual edit). Skip = keep the instance's version (rationale recorded). Learned-layer entries are advisory — never deleted by reconcile.

## Record (run after deciding)
```
py tooling/run_agent.py upgrade <instance> --reconcile --to-version "<to_version>" --decisions "adopted X, skipped Y"
```
Writes: `blueprint_ref.yaml` version pin + `reconcile_log` entry · refreshed `.atdb_snapshot/` · instance `changelog.md` entry.
