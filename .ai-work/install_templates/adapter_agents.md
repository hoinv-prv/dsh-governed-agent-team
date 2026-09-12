## How to run AIWS here (Codex / agent tools reading AGENTS.md)

Tool của bạn **không có cơ chế "skill"** như Claude Code. Các file skill của AIWS vẫn là Markdown thường —
đọc chúng bằng file-tool theo đường dẫn, rồi làm theo.

- **Execution entry:** non-trivial task → đọc `.claude/skills/aiws-aip/SKILL.md` (router) → đọc
  `.claude/skills/aiws-aip/operations/create.md` để lập AIP, rồi `operations/run.md` để wire workspace và chạy từng step.
  Các domain khác cùng khuôn: `.claude/skills/aiws-wiki/`, `.claude/skills/aiws-lint/`, `.claude/skills/aiws-pkg/`.
  (Thư mục tên `.claude/` chỉ là nơi cài đặt — nội dung là Markdown trung lập, không phụ thuộc tool nào.)
- **Chạy tool:** luôn từ project root, `python .ai-work/tooling/<tool>.py …` (stdlib, không cần cài gì).
  Hay dùng: `lookup_wiki_source.py` (tìm doc) · `wiki_relations.py` (quan hệ) · `run_aip.py` (start/resume/step) ·
  `lint_all.py` (finalize) · `lint_aip.py` (kiểm 1 AIP).
- **Các HARD GATE trong SKILL.md là bắt buộc với bạn y như với mọi tool khác.** Ở Claude Code chúng được
  diễn đạt qua skill; ở đây bạn tự thực thi. Cụ thể:
  - Trước khi mở bất kỳ spec/design nào làm input → **lookup wiki trước**, đừng Grep/Glob thẳng.
  - Gặp chỗ mơ hồ, thiếu Truth, hoặc cần promote lên Wiki/canonical → **DỪNG và hỏi HUMAN**; không tự quyết.
  - Không sửa Truth (`.ai-work/truth/`) và không tự apply canonical change khi chưa có CR được duyệt.
  - Kết thúc task: chạy lint và báo kết quả thật (kể cả khi đỏ).
- **Đừng chép nội dung rule sang file khác.** Sửa rule chung → sửa `.ai-work/AIWS.md` rồi chạy
  `python .ai-work/tooling/compose_aiws_rules.py --refresh --apply`.
