# skills/

Place execution-support skill docs here.

Skills are not AIP and not Playbooks.
They support micro-execution of a step.

## Relationship with `product/skills/`

Files here are **brief canonical descriptions** — purpose, inputs/outputs, flow summary, core rules.
They serve as the authoritative reference for what each skill is supposed to do.

The installable full SKILL.md files live in `product/skills/` and may contain additional
practical steps (e.g., lint, gap report, orient phase) beyond what is described here.

**Precedence rule:** If a flow step defined here is absent from `product/skills/`, that is a gap
to fix in `product/skills/`. Extra steps in `product/skills/` that are not here are acceptable
as practical additions, provided they do not contradict the canonical description.

## Domain-router layout (CR-AIWS-2026-07-025)

Từ v1.1.2, các skill cùng mục đích được gom thành **domain skill**: một folder =
`SKILL.md` (router — bảng verb → NL triggers → gates) + `operations/<verb>.md`
(định nghĩa đầy đủ từng operation, giữ nguyên mọi gate). Các domain hiện tại:
`aiws-aip`, `aiws-wiki`, `aiws-eval`, `aiws-pkg`, `aiws-lint`.
Skill standalone (`aiws-util-*`, `aiws-review-plan`, `aiws-runtime-review-checklist`)
giữ nguyên 1 folder = 1 `SKILL.md`. Tên cũ tra tại `product/rename_map.json` (v2).
Invocation: `/aiws-<domain> <verb>` hoặc ngôn ngữ tự nhiên (router dịch).
