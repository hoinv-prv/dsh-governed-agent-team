# tools/ — project & common tools (candidate → reviewed → active)

Holds tools used/created by agents (Phase F+). Tool lifecycle: candidate tools live **agent-local**
first (`agents/task_desks/<id>/tools/local_tools/`), then may be promoted here after HUMAN review/test.

- `project/` — project-scoped active tools (HUMAN-tested)
- `common/` — reusable common tools (promoted from project after further review)

Tool promotion/activation is **never automatic**. Each tool needs an output schema, usage guide,
limitations note, and validation report before promotion. Empty until Phase F.
