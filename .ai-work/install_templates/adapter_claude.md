## How to run AIWS here (Claude Code)

- **Execution entry:** non-trivial task → `/aiws-aip create` (nếu chưa có AIP) → `/aiws-aip run` để wire workspace → làm việc trong workspace files → `/aiws-lint` trước khi finalize.
- **Skills** [.claude/skills/](.claude/skills/) — `/aiws-aip create`, `/aiws-aip run`, `/aiws-aip init-workspace`, `/aiws-pkg install`, `/aiws-wiki lookup`, `/aiws-wiki build-meta`, `/aiws-lint`. Mỗi skill có `SKILL.md` riêng; đọc SKILL.md của verb trước khi chạy.
- **Settings:** mọi permission/config mới → `.claude/settings.local.json` (không phải `.claude/settings.json`; `settings.json` chỉ sửa khi cần share với team).
