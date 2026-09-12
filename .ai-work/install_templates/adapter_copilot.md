## How to run AIWS here (GitHub Copilot — repository-wide instructions)

File này phục vụ các Copilot surface **không đọc `AGENTS.md`** (theo support matrix của GitHub: ví dụ
Copilot code review in VS Code, và Chat/code review trong các IDE ngoài VS Code). Surface nào có đọc
AGENTS.md (coding agent, Copilot CLI, Chat in VS Code, code review trên GitHub.com) thì lấy rule từ đó —
nội dung hai nơi được sinh từ cùng một nguồn nên không lệch.

- **Execution entry:** non-trivial task → đọc `.claude/skills/aiws-aip/SKILL.md` rồi `operations/create.md` /
  `operations/run.md` (Markdown thường, đọc theo đường dẫn) → làm việc trong `.ai-work/workspaces/<task-id>/`.
- **Chạy tool:** `python .ai-work/tooling/<tool>.py …` từ project root (stdlib).
- **Bắt buộc:** lookup wiki trước khi mở spec làm input · mơ hồ/thiếu Truth → hỏi HUMAN · không sửa
  `.ai-work/truth/` · không apply canonical change khi chưa có CR duyệt · chạy lint trước khi finalize.
- **Đừng chép rule sang file khác.** Sửa `.ai-work/AIWS.md` rồi `compose_aiws_rules.py --refresh --apply`.
