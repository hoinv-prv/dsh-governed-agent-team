# AGENTS.md — dsh-governed-agent-team

Persistent project context. Read first in a new session.

## What this project is

This project builds the **Governed Agent Team** as a DSH plugin. Adopted **AI Work System MVP v1.2.1** as working methodology (since 2026-09-13). Live tree ở `.ai-work/` tại project root.

- **User language:** Vietnamese + English mixed.

<!-- Mọi thứ NGOÀI khối `AIWS:BEGIN rules` bên dưới là project-owned: AIWS không bao giờ ghi đè.
     Local override của dự án nằm ở `.ai-work/AIWS.local.md`; không sửa AIWS block generated bằng tay. -->

## Project AIWS override

For this repository, `.ai-work/AIWS.local.md` is the project-owned override for the generated AIWS block below. If the two conflict, the local override wins.

- AIP creation is optional by default. Do not require or create an AIP merely because a task is non-trivial.
- Create or use an AIP only when the HUMAN explicitly requests it or an approved, task-specific project process requires it.
- Truth and canonical changes still require their applicable approved CR; this policy does not weaken those gates.


## GAT design-first — mandatory workspace rule

Áp dụng cho **mọi agent và subagent** làm việc trong workspace này, với mọi thay đổi source code hoặc design liên quan **Governed Agent Team (GAT)**, kể cả bugfix, refactor, tests, integration và thay đổi qua WBS. Design chính thức của GAT nằm ở `docs/gat-design/` (workspace hiện tại: `/home/hoinv/work/dsh-governed-agent-team/docs/gat-design/`).

1. **Read design before changing source/design.** Trước mỗi thay đổi, tra cứu theo quy trình wiki-first hiện hành rồi đọc các tài liệu GAT liên quan trong `docs/gat-design/`, bao gồm các contract, invariant và phần phụ thuộc bị ảnh hưởng. Không chỉ dựa vào code hiện tại, ký ức phiên trước hoặc tài liệu trong run. Kiểm tra đề xuất với design hiện hữu để tránh conflict; nếu có mâu thuẫn hoặc chưa rõ quyết định cần áp dụng, dừng phần việc bị ảnh hưởng và hỏi HUMAN, không tự ghi đè design cũ.
2. **Design → source, never source → design.** Trước khi sửa source code GAT, phải cập nhật design tương ứng trong `docs/gat-design/` để mô tả thay đổi dự kiến và ảnh hưởng của nó; sau đó mới implement theo design đã cập nhật. Không sửa code trước rồi bổ sung design để hợp thức hóa. Thay đổi design-only cũng phải đối chiếu design hiện hữu theo bước 1.
3. **WBS intermediate artifacts.** Với mission thực hiện bằng WBS, có thể soạn và review design delta/tài liệu trung gian trong `wbs-runs/`. Trong luồng này, design delta tương ứng vẫn phải được cập nhật **trước** source code và phải đối chiếu với `docs/gat-design/`; nó không tự trở thành design chính thức. Khi finalize mission, bắt buộc apply các design delta đã được phê duyệt vào `docs/gat-design/`, bảo đảm design chính thức phản ánh đầy đủ source code cuối cùng. Không finalize/close mission nếu thay đổi design còn chỉ nằm trong `wbs-runs/`.
4. **Delegate with the same gates.** Agent giao việc phải truyền rule này, các đường dẫn design liên quan và thứ tự design-before-code cho subagent; khi chia việc song song, công việc source phụ thuộc vào design delta tương ứng đã sẵn sàng, không chạy trước nó. Reviewer phải kiểm tra cả tính nhất quán với design cũ và sự đồng bộ source/design cuối cùng.
5. **Evidence before finalize.** Báo cáo hoàn tất phải nêu tài liệu design đã tham khảo/cập nhật (đường dẫn và section), phần source bị ảnh hưởng và kết quả kiểm tra tính nhất quán; với WBS, nêu cả mapping từ delta trong run sang design chính thức đã apply. Rule này không bỏ qua review/approval hay CR gate hiện hành cho Truth/canonical; nếu chưa được phép apply thì báo chờ phê duyệt, không tuyên bố finalize.

<!-- AIWS:BEGIN rules v=v1.2.1 target=agents -->
AIWS rules v1.2.1 (target=agents) — do not edit inside this block

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

# AI Work System — core rules

> **Core rules (model-agnostic).** Package-owned: installed to `.ai-work/AIWS.md` and rendered into every
> per-tool rule file inside the AIWS block. Edit this file (or `.ai-work/AIWS.md` in the target), never the
> generated block. Nothing here may name a specific AI tool, a slash command, or a tool-specific directory —
> that belongs in an adapter (`adapter_claude.md` / `adapter_agents.md` / `adapter_copilot.md`).

## Adopted canonical knowledge

- **Methodology:** [AI Work System MVP](.ai-work/truth/canonical/methodology/) — `source_of_truth`, `authoritative`. Override mọi `curated`/`reference`/`history` trên conflict.
- **Wiki operational guidance:** [Wiki Guideline Package + deltas](.ai-work/truth/canonical/wiki_guidelines/) — complement methodology. Trên conflict với spec, **spec wins**. Nav: `.ai-work/wiki/reference/document_search_guidelines.md` (project-local — dự án tự tạo khi cần, không ship trong package).
- **Project Truth:** [SOP_MASTER](.ai-work/truth/SOP_MASTER.md), [AI_WORK_CONTRACT](.ai-work/truth/AI_WORK_CONTRACT.md).

Rule mơ hồ → spec wins trừ khi có Approved Deviation trong `AI_WORK_CONTRACT.md`.

## Core concepts

- **Truth** (`.ai-work/truth/`) — authoritative, no silent rewrite.
- **AIP** (`.ai-work/aip/` — PLAN/EXEC/LOCAL) — **stable macro-control**, không phải runtime notebook.
- **Workspace** (`.ai-work/workspaces/<task-id>/`) — runtime execution memory (findings, draft, capture, final output).
- **Wiki** (`.ai-work/wiki/`) — curated knowledge (domain/function/module/data/pattern/reference).
- **History** (`.ai-work/history/`) — trail/evidence/archive.

**Precedence:** Truth → Project Wiki → Local Wiki → Common Wiki → History (content) · SOP → Contract → AIP_PLAN/EXEC → Guidelines → Skills → Wiki → Workspace (artifact). Knowledge classes: `source_of_truth` → `curated` → `reference` → `history`.

## Hot operational rules (MUST follow)

1. **Wiki Source lookup FIRST** — khi user hỏi về concept thuộc canonical knowledge của dự án: chạy `python .ai-work/tooling/lookup_wiki_source.py --query <keyword>` trước, đọc primary MD meta, mở chapter/spec nếu cần.
   - **Match need → tool (3 shapes):** FIND 1 doc = `lookup --query`; ENUMERATE one kind (mọi function/table) = `lookup --source-type <type> --slim`; TRAVERSE ("node liên quan gì / ai phụ thuộc") = `wiki_relations.py --relations <id>`. **Chain rule:** `wiki_relations` cần `source_id` (output của `lookup`) — không bắt đầu ở relations khi chưa có id.
   - ❌ **Đừng đọc nguyên `index.jsonl`/`relations.jsonl`** để enumerate — dùng `--source-type --slim` / `wiki_relations` / grep.
   - **Index miss → bắt buộc escalate:** retry `--mode semantic`, rồi raw search trong artifact dirs tool hint chỉ ra; không im lặng báo "không tìm thấy" sau 1 lần fail.
2. **Never read PDF/DOCX binaries** — follow `companion_of` pointer trong meta về primary MD.
3. **Runtime state lives in Workspace**, không bao giờ trong AIP body (findings/metrics/progress/decisions/draft → workspace files, không phải AIP sections).
4. **No silent drift from AIP** — đổi scope/output/objective phải thêm dated entry vào Re-plan Log; không edit earlier sections silently.
5. **No silent rewrite of Truth hoặc official Wiki** — candidate → review → apply.
6. **Capture first, curate later** — unknowns đi vào `08_capture_inbox.jsonl`, không đi thẳng vào wiki.
7. **SOP first** — task ngoài scope SOP_MASTER phải confirm với user.
8. **Lint là guardrail, không phải reviewer** — không ask tools auto-fix wiki/truth.
9. **`wiki_first` là default behavior**, không bắt buộc. Override chỉ qua explicit HUMAN/rule/AIP instruction; ambiguous → **clarify, không tự suy đoán**. Chi tiết + conflict rules: `.ai-work/wiki/reference/document_search_guidelines.md` (project-local).

## AIP stability rules (CRITICAL)

AIP là stable control artifact (AIP_Detail_Spec §2.3/§10/§11). Vi phạm biến AIP thành live working file — explicitly forbidden.

- ❌ **Never tick `[x]` trong Done Criteria** — declarative criteria, không phải progress checklist.
- ❌ **Never embed runtime metrics** trong AIP (counts, findings, decisions discovered during execution). Thuộc về `04_findings.md`.
- ❌ **Never silently edit earlier sections** để phản ánh scope change. Append Re-plan Log entry TRƯỚC khi edit.
- ❌ **`updated_at` không phải last-touched timestamp** — chỉ bump khi update-by-exception thực sự (§10.1).
- ✅ Allowed updates: objective / scope / expected outputs / major assumptions / explicit re-plan — mỗi update bắt buộc có Re-plan Log entry.
- Linter (`lint_aip.py`) bắt `live_working_file`, `runtime_metric_in_aip`, missing sections. **Treat warnings as errors during review.**

## Execution policy

Trước khi thực hiện bất kỳ non-trivial task nào (review, analysis, implementation, investigation...) — **phải có AIP trước**. Không được làm thẳng trong chat. Sau khi có AIP thì wire workspace và **làm việc trong workspace files, KHÔNG trong AIP**. Lint trước khi finalize.

**Không cần AIP:** Ad hoc Q&A, câu hỏi đơn lẻ, tra cứu nhanh, research ngắn → trả lời thẳng trong chat.

> Cách gọi các bước trên (lệnh/skill cụ thể) khác nhau theo AI tool — xem phần adapter phía trên trong file rule này.

## Operating Memory — đọc khi nào

Bài học vận hành của dự án nằm ở [.ai-work/procedural/operating_memory.md](.ai-work/procedural/operating_memory.md).
**Đường đọc tự động chỉ có hai** — `aiws-aip run start|resume|step` và `aiws-aip create`
(CR-AIWS-2026-08-029); ngoài hai lệnh đó là đọc chủ động, và **điều kiện đọc nằm ở §2.1 của
chính doc đó** — đừng tự dựng danh sách riêng ở đây (CR-AIWS-2026-08-077 C4). §2.1 mang sẵn cảnh báo về
mức tin cậy của kho này; đọc tại chỗ để không mất cảnh báo đó.

## AIWS Knowledge Sources (installed)

Khi user hỏi về AI Work System hoặc cần tạo AIP template → tìm trong các source sau:

- **Methodology** — `.ai-work/truth/canonical/methodology/`
  Dùng khi: câu hỏi về AIWS design, spec, khái niệm, SOP flow
- **Wiki Guidelines** — `.ai-work/truth/canonical/wiki_guidelines/`
  Dùng khi: câu hỏi về Knowledge Hub, wiki source, wiki meta, canonical guideline
- **Preset Knowledge** — `.ai-work/preset_knowledge/`
  Dùng khi: tạo AIP mới — tìm AIP exec template hoặc sample phù hợp
  Nav: `aip_exec/` (exec templates), `aip_samples/` (samples), `AIP_SELECTION_GUIDE.md`

Wiki AIWS đã searchable sẵn sau install: `python .ai-work/tooling/lookup_wiki_source.py --query <keyword>`
(default scope `project,aiws`) và `python .ai-work/tooling/wiki_relations.py --relations <source_id>`.
`local` index là opt-in + authorization-gated (`--scope project,local --authorized human`).

## Tooling — pointers

- **Tooling** [.ai-work/tooling/](.ai-work/tooling/) — Python stdlib, no `pip install`. Full catalog: [README](.ai-work/tooling/README.md).
  - Find a document: `python .ai-work/tooling/lookup_wiki_source.py --query <keyword>`.
  - Find a source's relations (declared edges — one-hop, out + IN): `python .ai-work/tooling/wiki_relations.py --relations <id>`.
- **Spec reference:** [Methodology](.ai-work/truth/canonical/methodology/) · [Wiki Guidelines](.ai-work/truth/canonical/wiki_guidelines/).

## Notes

- Python stdlib only. No `pip install`.
- Windows: tools force UTF-8 stdout (cp932-safe).
- Always work from project root (nơi `.ai-work/` sits).
<!-- AIWS:END rules -->
