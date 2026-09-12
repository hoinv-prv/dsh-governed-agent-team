# AGENT_USAGE_GUIDE — Dùng AIWS Agents (Task Desks) trong thực thi AIP

> **Beta notice:** Task Desk (for Agent) hiện là Beta. Hãy trial trong project với phạm vi nhỏ, review output và governance trước khi dùng cho production.

Agent chỉ thực thi step đang active của Working AIP. ASC là runtime view được derive từ step, không thay Working AIP; Workspace mới là nơi persist output, decision và candidate capture.

> **Status: CANONICAL (guideline) — áp dụng cho AI Agents Pack v0.9 (beta)** (pack version: xem `PACK_VERSION.md` tại pack root — `product/agents/` canonical · `.ai-work/agents/` khi installed). Added by CR (xem Revision History).
> **Đối tượng:** người lập AIP và vận hành agents trong dự án AIWS. **Phạm vi:** dùng agent để THỰC THI AIP (giao việc cả AIP / từng step, và cách dùng đỡ tốn token). KHÔNG cover tạo/clone/upgrade/rename desk — xem `docs/rollout/user_guide.md` + `docs/rollout/command_usage_guide.md` trong pack.

## 0. Khái niệm trong 30 giây

Theo vocabulary authority `docs/agent_runtime_design.md` §0 (mọi path pack-root-relative):

- **Agent Task Desk (ATD)** — formerly *agent instance* — "bàn làm việc" bền vững per role: identity (`desk.yaml`) + `memory/` + `process/` + `training/` + `workspace/`. Desk giữ mọi thứ học được.
- **Agent** — worker THỰC THI một run: main session đóng vai (executor `main_session`, mặc định) hoặc Claude sub-agent spawn theo shim `.claude/agents/<desk_id>.md` (executor `claude_subagent`). Agent stateless per run; state sống ở desk.
- **ATDB (blueprint)** — khuôn tạo desk (thin archetype). Không dùng trực tiếp khi chạy task.
- **Run** — MỘT lần giao việc: `một run = một task assignment` — từ CR-AIWS-2026-08-046, một assignment có thể là MỘT CHUỖI step liên tiếp cùng desk trong 1 driving AIP ("span", §1). Tool `run_agent.py` chỉ chuẩn bị state (ARC + run folder + gates) — **không bao giờ** tự gọi LLM hay tự chạy task.
- **Activation — DEFAULT = KHÔNG chỉ định (CR-AIWS-2026-08-044 C0):** giao việc cho agent/desk là OPTIONAL feature. Step không khai `Assigned Agent:` → main session thực thi như **AIWS thuần** (không run, không desk); `Difficulty`/`Kind` một mình = metadata. Giao việc = chỉ định **AGENT** (handle == desk_id; desk là toolkit + state anchor, không phải bên nhận việc); executor (`Executor:` step field / `--executor`) + tier (`--tier`) là lựa chọn **plan-time của HUMAN/AIP**. Dự án tắt/bật cả cơ chế: `pack_config.yaml dispatch_enabled` (vắng = ON). Main muốn dùng đồ nghề desk để THỰC THI → bắt buộc một RUN executor `main_session` (tra cứu `list`/`memory` thì tự do).
- **Tier (CR-AIWS-2026-08-045)** — mức năng lực per-dispatch, phi trạng thái: registry 2 lớp `agents/execution_tiers.yaml` (tier trừu tượng + provider profile map tier→{model, effort}; MVP: claude). Desk khai `capability.tiers_supported: {tier: ceiling}`; run stamp tier + resolved values.
- **ARC** (`00_active_run_context.md`) — bề mặt đọc DUY NHẤT agent cần để làm việc (§3): task + định nghĩa role từ ATDB + context + confirmed memory (digest) + output contract + guardrails.

Điều kiện chung trước khi giao việc: desk đã tồn tại (`py .ai-work/agents/tooling/run_agent.py list`), AIP đã tạo qua `/aiws-aip create` và đã `run start` (status `active`), desk khai `run_policy.aip_driven: true` thì **bắt buộc** `--aip`.

## 1. Giao agent chạy TOÀN BỘ một AIP

Cơ chế: **1 driving AIP + gán desk vào từng step** (CR-AIWS-2026-07-018). Không có lệnh "chạy trọn AIP một phát" — mỗi run thực thi MỘT step, tuần tự (1 active run/Task Workspace — Phase-1).

**Bước 1 — Khi tạo AIP, điền `Assigned Agent:` vào các step giao cho desk** (optional step field — AIP_EXEC_TEMPLATE có comment mẫu):

```markdown
### Step: STEP-02 — Review detailed design F02
Objective: ...
Recommended Mode: Executing
Assigned Agent: dd_review        # <- agent handle == desk_id (hoặc `auto` để routing chọn desk)
Executor: claude_subagent        # <- optional (CR-08-044): plan-time; absent = desk default
Difficulty: medium               # <- cũng chọn tier (cheapest-capable) khi desk khai tiers_supported
Kind: review
...
```

> Nhắc (CR-08-044 C0): các step KHÔNG khai `Assigned Agent:` là default — main session tự làm như AIWS thuần, không có run/desk nào tham gia.

Muốn "cả AIP" do một desk làm: điền desk đó vào **mọi step execution**. Lưu ý: step **HARD GATE / Review Note / HUMAN-interaction không dispatch được** (bị chặn bởi eligibility — xem §2), giữ các step đó cho main session + HUMAN.

**Bước 2 — Dispatch từng step:**

```
py .ai-work/agents/tooling/run_agent.py start <desk> --aip AIP-EXEC-123 --step STEP-02 --task "Review DD F02 theo checklist"
```

(hoặc qua router NL: `/aiws-agent "cho <tên desk> chạy STEP-02 của AIP-EXEC-123"` — router chỉ resolve + confirm rồi dispatch, không tự mutate.)

**Gates tự động — chạy TRƯỚC khi scaffold run** (fail thì không có run-folder mồ côi):
- **AP-CR-25**: desk `aip_driven` mà thiếu `--aip` → refuse.
- **AP-CR-41**: AIP `template_source` phải khớp `run_policy.aip_template` của desk (legacy AIP không stamp → warn-and-proceed; `--strict-template` để refuse).
- **Stage-3** (DP-913-D): desk **∉** assigned set của AIP → refuse; AIP không `status: active` → refuse. Revoke = sửa AIP.

**Batch pre-authorization (DP-913-D):** khi plan đã HUMAN-confirm với **run list enumerated** (các step + desk đã liệt kê trong AIP active), main session dispatch từng run mà **không cần router re-confirm per-run**. Run ngoài list vẫn phải confirm.

**Chain qua Task Workspace (TW-reuse, CR-AIWS-2026-06-057 + 018):** mọi run của cùng driving AIP dùng CHUNG Task Workspace của AIP (`runs/<run_id>/` per run) — output step trước là input step sau qua `input_manifest` trỏ TW path (không copy tay); chain ledger = TW `run_log.jsonl`; captures dồn về TW `08_capture_inbox.jsonl`. Main session verify hand-off của từng run rồi mới dispatch run kế.

## 2. Giao agent chạy MỘT step

**Cách A — gán cứng:** điền `Assigned Agent: <desk_id>` đúng step đó (như §1 Bước 1); các step khác main session tự làm. Dispatch đúng step bằng `--step STEP-NN` — `run_request.related_task_card` ghi lại step id; **ASC của step chính là task card** (không có schema riêng).

**Cách B — capability routing (opt-in `auto`, CR-AIWS-2026-07-059/061 + 2026-08-045):** khai trên step `Assigned Agent: auto` (BẮT BUỘC — routing chỉ chạy khi step opt-in; Difficulty/Kind một mình không kích hoạt gì — CR-044 C0) cùng:

```markdown
Difficulty: low | medium | high
Kind: review, research, ...    # task-kind tags
```

Desk khai năng lực trong `desk.yaml` (hoặc kế thừa ATDB):

```yaml
capability:
  complexity_ceiling: medium
  task_kinds: [review, test_design]
```

Main session dùng helper `_route_step` (pure, plan-time): chọn desk có `complexity_ceiling >= Difficulty` **và** `task_kinds ∩ Kind ≠ ∅`; tie-break: `Assigned Agent` gán cứng luôn thắng, còn lại chọn **ceiling thấp nhất đủ dùng** (desk "rẻ" nhất đủ năng lực). Không có desk phù hợp / mơ hồ → STOP hỏi HUMAN. Routing là plan-time — HUMAN thấy assigned set khi duyệt AIP; đổi routing = sửa AIP.

**Chiều tier (CR-AIWS-2026-08-045):** trong desk đã chọn, `_route_tier` chọn tier **rẻ nhất** có `tiers_supported[tier] >= Difficulty` (cheapest-capable nối dài CR-061); dispatch resolve tier → `{model, effort}` qua profile `default_provider` của `execution_tiers.yaml`. Escalation: run tier thấp đuối (blocked/REWORK) → re-dispatch tier cao hơn, quyết định plan-time/HUMAN — model không tự leo thang. **1 span giữ 1 tier.**

**Điều kiện dispatch một step (`_dispatch_eligible`, design §8C)** — thiếu một điều là không giao được cho sub-agent:
- AIP `status: active`, không phải APPLY_CR template;
- `Expected Outputs` của step nằm TRONG Task Workspace (không đụng `product/`, `.ai-work/truth/`, wiki canonical);
- step không phải HARD GATE / Review Note / HUMAN-interaction;
- project `multi_system` → refused ở v1 (rule #12 không waive);
- inputs đã resolve (Deferred lookups xong trước dispatch).

## 3. Lưu ý khi dùng — đặc biệt để đỡ tốn token

Các lever dưới đây đều là cơ chế ĐÃ SHIP trong pack (trích nguồn theo section của `docs/agent_runtime_design.md`):

| # | Lever | Vì sao đỡ token | Nguồn |
|---|---|---|---|
| 1 | **Agent chỉ đọc ARC**, không đọc cả AIP/desk | ARC là digest có chủ đích (task + role + context + memory digest) — vài trăm dòng thay vì cả cây | §3 |
| 2 | **Dispatch brief 3-block** (digest bối cảnh + step info + hand-off contract) | Bơm đúng phần bối cảnh cần, không paste nguyên workspace vào prompt | §8E bước 2 |
| 3 | **Scoped-load desk memory (digest + hints)** — agent KHÔNG đọc hết bàn | Memory nạp dạng digest + index (ARC §5.1 Loaded / §5.2 Index), mở full chỉ khi cần | §8E bước 3, AP-CR-26 |
| 4 | **Tag memory `applies_when` + `scope_tags`** khi confirm learning | Entry chỉ nạp khi khớp task (`function:f02`, `topic:...`); untagged mới always-load — desk càng học nhiều càng phải tag | user_guide Step 6 |
| 5 | **Hand-off contract = summary + POINTERS-only** | Return không lặp nội dung file đã ghi trong workspace — main đọc theo pointer khi cần | §8E bước 4 |
| 6 | **TW-reuse giữa các run** | Không nhân đôi workspace; hand-off giữa steps bằng path qua `input_manifest`, không copy nội dung | §1 (CR-057/018) |
| 7 | **Blocked → mailbox answer → resume-from-inbox** | Không re-run từ đầu: run mới đọc answer ngay trong ARC và finalize | §8B, §8C |
| 8 | **Main "verify, don't re-judge"** | Main kiểm evidence + coherence của verdict, không suy luận lại từ đầu | §8D |
| 9 | **`companion_foldable` output contract** (executor `claude_subagent`) | Companion fold thành MỤC trong report chính — đỡ file-write bị môi trường sub-agent từ chối rồi phải làm lại | §8E (bảng profile, CR-08-012/013) |
| 10 | **Tier cheapest-capable** (`--tier`, CR-08-045) | Việc dễ chạy model/effort rẻ — routing chọn tier rẻ nhất đủ trần trong desk; registry là single point đổi mapping | §8C/§8F |
| 11 | **Multi-step span** (`extend` + continue, CR-08-046) | Desk subagent sống qua chuỗi step liên tiếp: trả sàn ~16k + desk digest MỘT lần, context append-only; thay cho spawn-mới mỗi step khi vẫn cần hand-off per-step | §1/§8E |

**Anti-patterns (tốn token / sai cơ chế):**
- Bảo agent "đọc toàn bộ desk / cả AIP trước khi làm" — phá scoped-load, ARC đã đủ.
- Yêu cầu return chép lại nội dung report — phá POINTERS-only.
- Dispatch step HARD GATE / Review Note — eligibility chặn; các gate đó thuộc HUMAN + main session.
- Re-run từ đầu khi agent blocked — dùng mailbox + resume.
- Gán desk ceiling `high` cho việc `low` — routing đã ưu tiên cheapest-capable; ngược lại desk thiếu ceiling sẽ bị refuse-under-capable.
- Sửa tay shim `.claude/agents/<desk_id>.md` — file generated, generator ghi đè khi create/clone/rename/upgrade.

**Lưu ý vận hành khác:**
- **Shim-registration lag (L-10):** shim sinh giữa phiên chưa chắc dispatch được ngay trong phiên đó — harness đăng ký agent type theo ranh giới session. Dispatch fail "agent type not found" trên shim hợp lệ = **BLOCKED môi trường**, không phải lỗi desk — đừng "sửa" desk; thử lại ở phiên sau. (`docs/rollout/known_limitations_and_backlog.md` L-10.)
- **Executor mặc định `main_session`** — bật `claude_subagent` per-desk chỉ sau khi dogfood PASS (khuyến nghị mở cho review-family trước); desk bật executor mà ATDB thiếu output-contract profile → `start` refuse trước scaffold (CR-08-013).
- **Mọi learning chỉ là candidate** — feedback/run không bao giờ tự ghi confirmed memory; HUMAN confirm qua `/aiws-agent-review-learning`.
- **No chaining:** agent không spawn agent (shim whitelist loại `Agent` tool); collaboration luôn qua driving AIP + main session điều phối.

> **Xem thêm §5 — Prompt cache & context economy:** các lever ở bảng trên cắt *khối lượng* token; §5 cắt *đơn giá* token (cache) và *hình dạng phiên* (fork / session mới / tách phiên).

## 4. Tham chiếu

Pack docs (path pack-root-relative — pack root: `product/agents/` canonical · `.ai-work/agents/` installed; version: `PACK_VERSION.md`):

| Tài liệu | Vai trò |
|---|---|
| `docs/agent_runtime_design.md` | AUTHORITY runtime: run model §1, ARC §3, mailbox §8B, routing/eligibility §8C, executor §8D–§8E |
| `commands/aiws-agent-run.md` | Verb spec run: start/resume/status/stop, plan_first, multi-agent, executor |
| `docs/rollout/user_guide.md` | Lifecycle create → run → feedback → review-learning (per-desk) |
| `docs/rollout/command_usage_guide.md` | Cách dùng từng command (3 nhóm: Core runtime · Desk lifecycle · router) |
| `docs/rollout/known_limitations_and_backlog.md` | Giới hạn hiện tại (L-1..L-10) + backlog J-2 |

AIWS-side: `Assigned Agent` / `Difficulty` / `Kind` step fields — comment mẫu trong `product/aip_templates/AIP_EXEC_TEMPLATE.md` (mirror `.ai-work/aip/templates/`); flow tạo AIP: skill `aiws-aip` operation create.

## 5. Prompt cache & context economy — dùng cache hiệu quả để giảm chi phí

> Tầng NGUYÊN LÝ (bền) nằm ở thân mục này; **số đo tuyệt đối nằm ở Phụ lục A** kèm ngày + môi trường (đo trên PoC nội bộ AIWS 08/2026, Claude Code + Opus 5 — con số có thể đổi theo harness/bảng giá, nguyên lý thì không). Khuyến nghị ở đây là **guidance**, chưa phải luật template/SOP.

### 5.0 Cache hoạt động thế nào — 5 điều tối thiểu

1. Cache khớp theo **prefix byte-identical**: lệch tại vị trí k là mất cache từ k trở đi. Không có "gần giống".
2. Giá tương đối (kiểm bảng giá hiện hành trước khi tính): đọc-từ-cache ≈ **0,1×** giá input · GHI cache đắt hơn input thường (1,25× với TTL 5m, **2,0× với TTL 1h**) · **output ≈ 5× input** — số hạng nhiều người quên nhất.
3. **TTL bất đối xứng:** main session giữ cache ~1h; **sub-agent chỉ ~5 phút** (docs chính thức xác nhận: 5 phút "even on a subscription") — mẫu "warm rồi fan-out" phải khép trong cửa sổ đó. TTL 1h của main là trên subscription; **vượt hạn mức plan (chạy bằng usage credits) harness tự tụt về 5m** — giữ 1h bằng `ENABLE_PROMPT_CACHING_1H=1`.
4. **Sàn cố định không tối ưu được:** mỗi sub-agent trả ~16k token (system prompt + tools) ngay message đầu; main session khởi hành ~57k (system + rules always-loaded + MEMORY + bảng skill). Tính tiết kiệm phải trừ sàn trước.
5. Số "token" harness báo cho sub-agent (`subagent_tokens`) **mù với cache** — nó là ảnh chụp kích thước context lần gọi cuối, không phải chi phí. Muốn nói chuyện chi phí: đọc transcript JSONL (`message.usage.{input, cache_creation, cache_read, output}`; bẫy: streaming ghi nhiều dòng cho một call — giữ bản ghi CUỐI).

### 5.1 Đòn bẩy lớn nhất: đừng fan-out khi không cần

Main session chạy tuần tự với context **chỉ nối thêm** hưởng cache gần trọn vẹn (Phụ lục A: ~12,9% chi phí so với không cache). Chi phí đọc-lại-context chiếm ~nửa tổng và chia đều giữa MAIN và fan-out — hai bên tự triệt tiêu, nên **song song/tuần tự hãy chọn theo wall-clock và nhu cầu cách ly, đừng chọn vì "cache"**. Việc làm được tuần tự trong MỘT context đang ấm → làm tuần tự; fan-out khi cần mù, cần model khác, hoặc cần thời gian.

### 5.2 Fork · named sub-agent · session mới · tách phiên — bảng quyết định

| Tình huống | Dùng | Vì sao |
|---|---|---|
| Nhiều nhánh song song CÙNG điểm xuất phát, cần chung corpus, KHÔNG cần cách ly | **fork — CHỈ từ parent SẠCH chuyên dụng** (mở phiên mới, nạp đúng corpus, rồi fork) | Fork lượt đầu đọc cache của parent. Nhưng mỗi message của fork "chở" cả context parent (`chi phí ≈ parent_size × số_message × 0,1`) ⇒ parent sạch thì lời, parent lẫn tạp thì **lỗ nặng** (Phụ lục A) |
| Việc cần **MÙ / cách ly** (control, đối chứng, chấm độc lập) | **named sub-agent — BẮT BUỘC** | Fork kế thừa TOÀN BỘ hội thoại, gồm cả verdict đã có ⇒ phá tính mù. Cách ly là mục tiêu, không phải chi phí thừa |
| Cần **model rẻ** cho việc nhẹ | **named + field `model`** | Fork thừa hưởng model của parent — không route được |
| Việc **một-lượt ngắn** | Cân nhắc gộp | Named one-shot chịu "thuế cache" (~25% — ghi cache rồi không bao giờ đọc lại) + sàn 16k. Gộp nhiều việc ngắn vào một lượt khi được |
| Task nặng trên session ĐANG dài (lịch sử không liên quan ≥100k) | **SESSION MỚI** + nạp đúng Execution Input Package / ASC ("khởi-hành-sạch") | Kéo lịch sử cũ qua hàng trăm message là khoản chi lớn vô hình (Phụ lục A: −87% context khởi điểm khi làm đúng) |
| Bước cuối chỉ cần artifact (merge / census / finalize) | **Tách phiên artifact-only**, tập chuyển giao ĐÓNG khai trước | Đo được −68% chi phí bước đó; điều kiện: danh sách artifact khai trước, đối chứng dương (kết quả phải khớp), bề mặt render tươi kèm hash |

**Flow khuyến nghị cho AIP nặng** (ghép các dòng trên thành quy trình; SoT: docs Claude Code `prompt-caching` + `sub-agents`, fetch 2026-08-14):

1. **Tạo + review + approve AIP** ở session đang làm việc — context "bẩn" của giai đoạn bàn bạc nằm lại đây.
2. **Mở SESSION MỚI cho execution** — nạp AIP đã approve + Execution Input Package (khởi-hành-sạch); main session của phiên này điều phối dispatch **từng step** (§1–§2) và verify hand-off giữa các run.
3. Trong execution, tách **hai làn**:
   - Step giao **desk** → **named dispatch** như §1–§2. Muốn agent chạy "một mạch" nhiều việc liên tiếp, có HAI lever: (a) **gộp thành một step lớn ngay khi soạn AIP** (zero-code; dùng khi các việc không cần hand-off riêng); (b) **multi-step span (CR-AIWS-2026-08-046):** giữ các step riêng, dispatch step đầu rồi `extend` + main CONTINUE chính desk subagent đó per-step — context append-only, trả sàn ~16k + desk digest một lần, vẫn verify hand-off từng step. Cả hai đều không được vắt qua HARD GATE / HUMAN step; span lợi nhất khi các step sát nhau (TTL cache sub-agent ~5 phút — gap dài thì cache lạnh nhưng vẫn đỡ tái tạo context + thuế one-shot). **KHÔNG dùng fork cho desk:** fork chạy bằng system prompt + tool set của MAIN session, tức mất desk identity / tool whitelist / output contract / tier routing / blindness — bypass governance boundary của pack (luật giữ nguyên; span dùng NAMED continuation, không phải fork).
   - Phân tích **song song cùng điểm xuất phát**, không cần mù → **main session fork N nhánh**. Fork LÀ một loại sub-agent do main spawn — không tồn tại đường "giao cho sub-agent rồi sub-agent fork context của main"; fork cũng không fork tiếp được. **Fan-out càng sớm sau khi nạp corpus càng tốt** — độ sạch parent phân rã theo step (chi phí ≈ `parent_size × số_message × 0,1`); nếu bước fan-out rơi cuối AIP, mở phiên sạch riêng cho bước đó rồi fork. Song song hợp lệ ở mức **trong-step** (pack hiện sequential — 1 active run/TW).
   - Việc cần **mù** hoặc **model rẻ** vẫn bắt buộc **named** (bảng trên).

Lưu ý vận hành:
- **Fork là kỹ thuật tầng harness** (chưa thuộc pack design). Từ Claude Code **v2.1.232, fork mode ON mặc định trong interactive session** (off mặc định ở `-p`/Agent SDK) — không còn là tính năng ẩn sau env var. Khi fork mode on, mọi sub-agent spawn chạy background; fan-out same-prefix được harness tự tối ưu (giữ các fork sau lại tới khi fork đầu tạo xong cache). **Đừng chốt quyết định fork theo một lần đo** — đo lại trên hình dạng task của chính mình.
- **`/compact` KHÔNG thay được session mới:** nội dung sau compact không kiểm soát được ⇒ mất tính tái lập. Session mới + Input Package tường minh thì kiểm được.

### 5.3 Kỷ luật prefix khi soạn prompt / brief

1. **Bất biến đứng đầu — khả biến CHỈ nối vào đuôi.** Thứ tự chuẩn: checklist/universe (pin) → guidelines → corpus snapshot (đóng băng + hash) → phần riêng-từng-worker Ở CUỐI. Đặt tên nhánh / chỉ dẫn riêng / số thứ tự lên ĐẦU prompt là giết toàn bộ cache phía sau nó.
2. **Byte-identical giữa các worker song song:** worker đầu tạo cache, các worker sau đọc gần như miễn phí — nhưng lợi ích **chết khi resume**; đừng thiết kế dựa trên cache sống qua resume.
3. **Tuần tự thì chỉ APPEND** — không đọc lại, không đảo thứ tự (đảo = đắt hơn ~4×). Xếp corpus lớn vào sau.
4. **Snapshot + hash corpus trước khi chia việc** — vừa chống drift vừa là điều kiện để prefix chung hợp lệ; cùng một tài liệu phải được nạp CÙNG MỘT CÁCH ở mọi nơi (đọc lại bằng cách khác = byte khác = trượt prefix).
5. Muốn tối ưu thứ tự/nhóm: chốt bằng **số create/read đo được**, đừng suy từ "corpus khai báo" (mô hình ít-corpus-thì-rẻ từng bị số đo bác).
6. **Model VÀ effort level đều nằm trong cache key** (docs chính thức): đổi `/model` hay `/effort` giữa phiên = mất TOÀN BỘ cache của hội thoại. Chốt model + effort ở ĐẦU phiên; muốn đổi thì đổi ở ranh giới task (sau `/clear`//`/compact`), không đổi giữa task.

### 5.4 Trục output — mỏ tiết kiệm bị quên

Output giá ~5× input và thường chiếm ~1/5 chi phí. Lever thật: **viết ngắn** — hand-off = summary + POINTERS (luật AIWS sẵn có, xem §3 lever 5); evidence = con trỏ + neo 3–5 chữ để script tự trích thay vì bắt model chép nguyên văn. Cấm chiều ngược: đừng để model rẻ "giãn chi tiết" từ output nén của model đắt — đó là bịa phần đã mất.

### 5.5 Kỷ luật đo — trước khi tin một con số

- **Khai đơn vị tối ưu trước** (khối lượng token · $ API · quota subscription · wall-clock · context window) — mọi nhầm lẫn trong chuỗi đo gốc đều bắt nguồn từ trộn đơn vị.
- **Pre-registration:** khoá metric + ngưỡng TRƯỚC khi thấy số; công cụ đo phải có **đối chứng dương** trước khi được tin; ưu tiên **đo hồi cứu** trên transcript sẵn có trước khi dựng thí nghiệm mới.
- Mỗi con số công bố kèm: ngày đo · harness/model · công thức. (Đây là lý do Phụ lục A tách khỏi thân mục.)

### Phụ lục A — Số đo tham chiếu (PoC nội bộ AIWS, 08/2026 · Claude Code + Opus 5 · as-reported)

> Thước chi phí dùng cho các số dưới (chuẩn thuận 2026-08-03): `đơn vị = input×1 + cache_creation×2,0(TTL 1h)|1,25(5m) + cache_read×0,1 + output×5`. Trọng số ghi-cache phải kiểm bằng `usage.cache_creation` của chính lượt đo, không copy hằng số.

| Số | Giá trị | Nguồn (demo project) |
|---|---|---|
| Main tuần tự, context chỉ-nối-thêm | **~12,9%** chi phí so với không cache (98% đọc-từ-cache) | CR-MRBS-2026-08-009 E1 + §12 |
| Fork từ parent SẠCH ~42k | **76%** so với named (66% steady-state) — n=1 | CR-MRBS-009 E8 |
| Fork từ parent LẪN TẠP ~166k | **176%** so với named (LỖ) | CR-MRBS-009 E7 + §2quater.6quinquies |
| Named one-shot ngắn | thuế cache **~25%** (125% vs không cache) | CR-MRBS-009 E6(c) |
| Prompt byte-identical (worker thứ 2+) | chi phí **~21%** lượt cold; đảo thứ tự → **~82%** | CR-MRBS-009 T0′ (E2) |
| Khởi-hành-sạch (session mới) | **−87,1%** context khởi điểm (445k → 57k) | CR-MRBS-011 T1 + MEASURE 2026-08-03 |
| Tách phiên artifact-only bước cuối | **−68%** chi phí bước đó ($12,35 → $3,96) | CR-MRBS-011 T2 vòng 2 |
| Chi phí đọc-lại-context | **~49,9%** tổng, chia đều MAIN↔fan-out | AIWS-CR-INVENTORY-2026-08-04 §4 |
| TTL | main **1h** · sub-agent **5 phút** | CR-MRBS-009 E3 |
| Sàn cố định | sub-agent **~16,3k**/message đầu · main **~57k** khởi hành | CR-MRBS-009 E4 + §13.6 |
| Trục output | **~20,1%** chi phí run; giá **5×** input | CR-MRBS-009 §12.1 |

### Phụ lục B — Hằng số & luật vận hành liên quan (POINTER)

Sáu hằng số đo được (nhiễu lượt-với-lượt 35–38% · recall 50% dù mọi cổng xanh · sàn 57k · −87% · −68% · 49,9%) và sáu luật sự-cố-sinh-ra (V5 pre-registration · V6 pin tool_sha256 · A2 mẫu số bắt buộc · C4 giải trình khi quá đẹp · mù-theo-NỘI-DUNG · luật-phải-vá-bằng-tool) — chi tiết: `AIWS-CR-INVENTORY-2026-08-04-agents.md` §4 (tài liệu nội bộ AIWS, demo project). Chúng áp cho MỌI thiết kế đo/so sánh agent, không riêng cache.

## Revision History

| Date | Change |
|---|---|
| 2026-08-14 | v1 — tạo mới (AIP-EXEC-1034; added by CR-AIWS-2026-08-037) |
| 2026-08-14 | v2 — thêm §5 Prompt cache & context economy + bổ sung §3 (CR-AIWS-2026-08-040; nguồn: PoC đo cache demo 08/2026) |
| 2026-08-14 | v3 — dispatch wave: §0 activation default-off + dispatch-handle + tier · §1 Executor field + nhắc C0 · §2 Cách B opt-in `auto` + chiều tier · §3 lever 10/11 · §5.2 span lever (b) + fork ban giữ nguyên (applied by CR-AIWS-2026-08-044/045/046) |
