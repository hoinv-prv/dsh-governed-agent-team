# install_templates — nguồn duy nhất của rule file (CR-AIWS-2026-08-066)

Ba tầng, một nguồn:

| Tầng | File | Chủ sở hữu | Vòng đời |
|---|---|---|---|
| **core** (model-agnostic) | `aiws_core_rules.md` | package | install copy → `.ai-work/AIWS.md`; upgrade **overwrite** |
| **adapter** (per-tool) | `adapter_claude.md` · `adapter_agents.md` · `adapter_copilot.md` | package | render vào AIWS block; upgrade **refresh** |
| **identity** (per-project) | `project_identity.md` | project | ghi 1 lần lúc init, sau đó AIWS **không đụng** |

`VERSION` (YAML frontmatter `aiws_version` + `release_date`) được **stamp tại build** — site duy nhất — và đi
theo section copy tới target. Nó KHÔNG nằm trong cây `product/` này. `compose_aiws_rules.py` đọc nó để đóng dấu
version vào marker; ở source tree (có `product/aiws_version.md`) tool đọc pin đó và gắn hậu tố `-src`.

**Sinh file rule:** `python .ai-work/tooling/compose_aiws_rules.py --init --tools claude,agents,copilot [--claude-file CLAUDE.md] --apply`
→ mỗi target một file, phần AIWS nằm trọn trong `<!-- AIWS:BEGIN rules … -->` … `<!-- AIWS:END rules -->`.

**Surface coverage** (matrix per-surface, không per-IDE):

| Target | File sinh ra | Phục vụ |
|---|---|---|
| `claude` | `CLAUDE.local.md` (mặc định, gitignored) hoặc `CLAUDE.md` (team-shared) | Claude Code — core nạp qua `@.ai-work/AIWS.md` |
| `agents` | `AGENTS.md` (repo root, committed) | Codex · Copilot coding agent/CLI/Chat-in-VS-Code/code-review-GitHub.com · Cursor/Zed… — core **inline** |
| `copilot` | `.github/copilot-instructions.md` (committed) | Copilot surface **không** đọc AGENTS.md (vd code review in VS Code) — core **inline** |

**Conflict rule:** `Truth` > nội dung project-owned **ngoài** block > nội dung **trong** AIWS block.
Sửa tay bên trong block sẽ bị `--refresh` ghi đè (tool cảnh báo trước khi ghi). Sửa rule chung → sửa
`.ai-work/AIWS.md` (hoặc file này ở upstream) rồi refresh.

**Quy tắc nội dung:** core không được nhắc tên tool, slash command, hay thư mục riêng của một tool — những thứ đó
thuộc adapter. Đây là điều kiện để một nguồn phục vụ được mọi tool; vi phạm là bắt đầu của drift-by-copy.
