# Knowledge Relationship (Related Sources) Spec for AI Work System MVP
Version: 0.5 (three relation registers + object-node representation; two-kind node)
Status: Canonical spec
Scope: Knowledge Hub / Specs / Guidelines

> **Revision History** (1 dòng/version — chi tiết: CR file + git history; nén editorial theo CR-AIWS-2026-08-031)
> - **v0.1–v0.2** — superseded (CR-AIWS-2026-05-005; retired shapes — xem `Knowledge_Object_Model_Spec_MVP` §8).
> - **v0.3 (2026-05-30, CR-AIWS-2026-05-020 / AIP-EXEC-038)** — quan hệ cross-artifact = section
>   **`## Related Sources`** (typed roles) trong từng artifact meta (mô hình 2-layer).
> - **v0.4 (2026-05-30, CR-AIWS-2026-05-022 / AIP-EXEC-040)** — typed registry (base ∪ `x:`; unknown bare type =
>   WARNING only — §4.1) + confidence note (§4.2, net-new) + projection **`relations.jsonl`** (§6A, one-hop reverse
>   index; §5 "no precomputed global graph" UNCHANGED).
> - **v0.5 (2026-05-31, CR-AIWS-2026-05-023 / AIP-EXEC-045)** — **three relation registers** (§4.0: documentary /
>   representation / domain); domain types dùng trực tiếp trên object node; `contains` = navigation-only
>   (DP5/INV-3); registry membership stays guidance/warn.

---

# 1. Purpose of this spec

Spec này định nghĩa **quan hệ tri thức có hướng** giữa các artifact trong Knowledge Hub (mô hình 2-layer),
để Knowledge Hub không chỉ **search** mà còn **dẫn hướng mở rộng tri thức**:

- quan hệ là gì, khác gì alias / keyword / generic similarity,
- AI nên đi tiếp sang knowledge nào sau hit đầu tiên,
- task lens ảnh hưởng thứ tự expansion thế nào.

Quan hệ được biểu diễn bằng section **`## Related Sources`** trong artifact meta (Lớp 1) — không qua bất kỳ
field nào của retired KO record (xem `Knowledge_Object_Model_Spec_MVP` §8).

Lưu ý: đây là spec logic, không phải graph-traversal algorithm implementation; không thay thế routing spec
nhưng là thành phần lõi để routing hoạt động tốt.

---

# 2. Một relationship (`## Related Sources` entry) là gì / không là gì

## 2.1. Là gì
> liên kết **có hướng, có role, task-useful**, giúp AI biết từ artifact này nên đi tiếp sang source nào.

Trả lời câu hỏi: "Từ artifact này, knowledge tiếp theo nào đáng xem nhất cho task hiện tại?"

## 2.2. Không là gì
- alias, keyword, weak semantic similarity,
- mọi relation tìm được trong graph,
- flat traceability (`related_artifact_refs`) — cái đó không typed, không lens-aware.

---

# 3. Cấu trúc một `## Related Sources` entry

Mỗi entry trong section `## Related Sources` của meta gồm:
- **target source** — `source_id` của artifact liên quan,
- **role** — typed, có hướng,
- **why/when** — ngắn, khi nào nên mở.

```markdown
## Related Sources
- **SRC-BD-F04** — role: upstream_input — BD gốc của function này; mở khi cần xác nhận business intent
- **SRC-ITTC-F04** — role: downstream_target — test case của function; mở khi verify scope
```

---

# 4. Relation type registry (typed relations)

Base role set (giữ nguyên từ CR-AIWS-2026-05-004 Change 8 — the documentary/representation register):
`upstream_input · downstream_navigation · downstream_target · triggered_flow · system_foundation ·
companion_design · companion_requirement · output_template · related`.

## 4.0. Three relation registers (v0.5 — two-kind node)

Roles được tổ chức thành **ba registers** theo endpoint kind (membership = **guidance/warn**, không hard lint — §4.1):

| Register | Endpoints | Roles | Ghi chú |
|---|---|---|---|
| **documentary** | Artifact → Artifact | 9 base roles (§4: `upstream_input`/`downstream_*`/`companion_*`/`output_template`/`related`/…) | quan hệ giữa tài liệu |
| **representation** | Object ↔ Artifact | `represents` / `represented_by` | tài liệu mô tả một object (RD/BD/DD/Testcase ↔ function/screen/table); inverse pair có sẵn §6A |
| **domain** | Object → Object | `x:`-namespaced (vd `x:calls`, `x:part_of`, `x:migrates_to`) | quan hệ nghiệp vụ/kỹ thuật giữa các object |

Một meta có thể mang edges thuộc nhiều register. Register **không** thêm field mới — nó chỉ là cách phân loại role
theo node_kind của hai endpoint (xem Knowledge_Object_Model_Spec v0.3 §3bis.6). `node_kind=object` của endpoint
được resolve từ meta của nó (no separate store, INV-1).

## 4.1. Open registry + extension (CR-022 OP-4)
Registry là **open** và **AIWS-owned**. Type canonical mới được promote vào base set **qua CR** (không tự chế
per-project). Một dự án CÓ THỂ thêm type riêng **ngay**, dùng prefix dành riêng **`x:`** (vd `x:foreign_key_to`)
— namespaced type an toàn va chạm với core tương lai.

**Lint stance (warn-not-error cho TYPE semantics — contract mọi relation lint về relationship TYPE phải tuân):**
- base type (trong registry) → OK.
- `x:`-namespaced type → **luôn hợp lệ, không warning**.
- bare type KHÔNG trong registry → **WARNING only, không bao giờ error** (gợi ý: promote qua CR, hoặc namespace `x:`).
Lint KHÔNG fail build vì type lạ; discovery coi mọi type là edge hợp lệ. Registry membership là **guidance**, không
phải hard lint — giữ meta-authoring nhẹ (xem WIKI_META_BUILD_UPDATE_GUIDELINE).

**Phạm vi contract (CR-AIWS-2026-07-032):** contract warn-not-error ở trên áp cho **type-registry semantics**.
**Shape/resolution INTEGRITY** của entry line là class riêng, **ERROR-grade**: bullet không đúng shape §4.3 (thiếu
**bold** target id) hoặc target không resolve về một `source_id` tồn tại (meta set + indexes) → lint ERROR
`relations_edge_unresolvable` (meta-scan), đồng thời `build_relations` **skip** bullet đó kèm warning `[SKIPPED]`
— không bao giờ emit garbage edge, không bao giờ drop im lặng. Edge **parse-valid** không bao giờ bị drop; backstop
projection-level `relations_broken_ref` (WARN) giữ nguyên.

## 4.2. Confidence note (optional; net-new ở v0.4)
Mỗi entry CÓ THỂ mang confidence note — `asserted` (source nói rõ; default) · `inferred` (suy từ context) ·
`candidate` (đề xuất, chưa confirm; surface để review, không dựa vào như fact). Đây là **net-new ở v0.4**, không
reuse từ retired record (xem `Knowledge_Object_Model_Spec_MVP` §8).

## 4.3. Entry line format (v0.4)
Một dòng `## Related Sources` mang: target `source_id`, type (qua `role:`/`type:`), basis note, và confidence tùy chọn:
```
- **<target_source_id>** — role: <type> — <basis note> [<confidence>]
```
Confidence bỏ trống → `asserted`. Dòng legacy untyped (`- **<id>** — <note>`, không `role:`/`type:`) parse thành
`related_to`. **Cả hai dạng đều BẮT BUỘC bold target id** — dòng bullet không có `**<id>**` không phải shape hợp lệ
và bị lint ERROR `relations_edge_unresolvable` + parser skip (§4.1 Phạm vi contract, CR-AIWS-2026-07-032); placeholder
thuần dạng `- (none)` được bỏ qua, scaffold `<SRC-id: TODO>` do warn CR-017 xử lý. **Object node-kind đã land (Knowledge_Object_Model_Spec v0.3, CR-023):** domain type (`x:calls`/`x:reads`/…)
dùng **trực tiếp** trên object node (domain register, §4.0); trên document node vẫn ghi chi tiết trong basis note.
`contains` (inverse của `part_of`, §6A) là **navigation-only** — KHÔNG roll-up nội dung; một object node không bao giờ
aggregate (DP5/INV-3 của Knowledge_Object_Model_Spec v0.3).

## 4.4. Basis note: objective stakes, intent-agnostic (CR-AIWS-2026-06-002)

Basis note được viết **lúc registration**, **trước khi biết intent** của bất kỳ task tiêu thụ nào. Viết nó **khách quan**
để phục vụ MỌI intent hợp lý (review · author một artifact liên quan · hiểu function · impact analysis). Việc của nó là
cho AI đang đọc — đã biết intent của chính mình — đủ chất liệu để **tự quyết read-vs-skip ĐÚNG** (đọc đúng VÀ bỏ đúng).
Nó **không** nhắm một intent cụ thể và **không** ra lệnh.

**Theo từng edge:**
- **Dependency edge** (có coupling dữ liệu/contract thật) — nêu như **sự thật khách quan**: (a) **hướng + subject chung**
  (ai đọc/ghi data của ai); (b) **coupling point / cái bị ảnh hưởng** (schema/fields/keys/contract đang ở thế bị tác động).
  Reader nào động tới subject đó thấy nó liên quan; reader không động tới thấy nó skippable.
- **Skippable edge** (không coupling dữ liệu/contract — shared UI component, doc template, navigation) — nói rõ điều đó
  một cách khách quan ("shares the common header component; no data coupling") → cấp phép skip tự tin.
- Giữ **relationship type chính xác** — đây là tín hiệu ưu tiên khi rank nhiều edge dưới reading budget.

**Tránh:** mệnh lệnh "MUST READ"/"always read" (coercive → đọc-tràn mù); conditional trigger mơ hồ ("open **when** you
change X") mà reader tự bào chữa là chưa thỏa (quan sát: **phản tác dụng**); instruction nhắm intent ("read when
reviewing/designing") — note phải **intent-blind**.

**Template**
```
# dependency edge — fact + objective stakes/coupling:
- **<SRC-id>** — role: <type> — <who reads/writes whose data + direction>; coupling = <schema/fields/keys/contract>; <what a change affects>. [confidence]
# skippable edge — objective no-coupling:
- **<SRC-id>** — role: <type> — <what it is>; no data coupling. [confidence]
```

**Worked example** (chain F02 writes CUSTOMER → F03 reads CUSTOMER, writes ORDER → F04 reads ORDER):
```
# on F03's meta:
- **SRC-DD-F02** — role: upstream_input — F03 reads the CUSTOMER master F02 owns/writes; coupling = customer_id FK + customer field names/types/keys F03 consumes. [asserted]
- **SRC-DD-F09** — role: system_foundation — shares the common screen-header component; no data coupling. [asserted]
# on F04's meta (seen from F03 as a reverse `## in` edge):
- **SRC-DD-F03** — role: downstream_target — F04 consumes the ORDER/ORDER_LINE F03 writes; coupling = F03's output schema; a change there propagates to F04. [asserted]
```
Từ CÙNG bộ note, các intent **tự chọn**: *review F03 output* → đọc F04 (output-schema coupling); *sửa typo nhãn F03* →
bỏ F02/F04/F09 (không động input lẫn output); *author một ORDER consumer mới* → đọc F04 (contract của consumer khác);
*hiểu F03 end-to-end* → đọc F02+F04 (data lineage), bỏ F09.

> **Two-surface:** spec mang full convention (governance). SKILL (build/refresh/register) mang **dạng terse** đọc lúc
> runtime — AI **không buộc** mở spec khi chạy. Relations-projection model (`build_relations.py` / `relations.jsonl`
> one-hop) **KHÔNG đổi** — đây là quy ước wording. Metas resolved cũ được **grandfathered** (note thiếu objective stakes →
> `lint_wiki` WARN, không error — §4.1 warn-not-error). DATA_FLOW_TYPES (`upstream_input`/`downstream_target`/`x:reads`/`x:writes`)
> dùng cho heuristic warn `relations_thin_basis`.

---

# 5. Lens-aware expansion (intent giữ nguyên)

Thứ tự AI follow `## Related Sources` phụ thuộc **task lens**:
- task "hiểu business intent" → ưu tiên `upstream_input` / `companion_requirement`,
- task "verify / test" → ưu tiên `downstream_target` (test cases),
- task "apply guideline" → `output_template` / `related` reference sau cùng.

AI follow quan hệ trực tiếp trong `## Related Sources` trước; expansion sâu hơn (multi-hop) thực hiện bằng cách
mở meta của source liên quan rồi đọc `## Related Sources` của nó — **không có precomputed global graph**
(rationale: CR-AIWS-2026-05-005).

---

# 6. Three-Way Separation (2-layer) — ba cơ chế cross-artifact

| Cơ chế | Lớp | Granularity | Mục đích | Routing role |
|-------|-----|-------------|---------|--------------|
| `related_artifact_refs` | Lớp 1 — artifact meta frontmatter | Flat list of artifact IDs | Traceability flat, không typed | **Traceability only** — KHÔNG dùng cho expansion routing |
| `## Related Sources` (typed) | Lớp 1 — trong artifact meta MD | Typed, directed → target `source_id` + type + confidence | Dẫn hướng AI sang source liên quan tiếp (out-edges, authoritative) | **Primary expansion mechanism** (human/AI-authored) |
| `relations.jsonl` (projection) | Projection của Lớp-1 metas | Both endpoints / edge | Reverse / impact / neighbour query (IN-edges) | **Machine reverse index** (one-hop, opt-in) |

> **Retired fields:** xem `Knowledge_Object_Model_Spec_MVP` §8 (CR-005/CR-020). `## Related Sources` **KHÔNG**
> project vào `index.jsonl` (Slim Index). `relations.jsonl` là một projection RIÊNG, cũng **KHÔNG** nhập vào `index.jsonl`.

**Anti-pattern:** dùng `related_artifact_refs` để navigate artifact→artifact — đó là flat list, không type,
không lens-aware. Dùng `## Related Sources` (out-edges) + `relations.jsonl` (reverse) cho navigation.

---

# 6A. `relations.jsonl` — queryable projection (reverse index) [v0.4, CR-022]

`## Related Sources` chỉ ghi **out-edges** của một node và **không** được project vào index — nên câu hỏi reverse/
impact ("từ B00002, ai trỏ NGƯỢC về nó / ai gọi nó?") không trả lời được nếu không mở lại raw artifact hoặc grep.
`relations.jsonl` lấp khoảng trống đó như một **projection bổ sung**.

**Contract:**
- **Location:** `wiki_sources/relations.jsonl` (project) + optional `wiki_sources/relations.local.jsonl` (local),
  mirror `index.jsonl` / `index.local.jsonl`.
- **Projection — never hand-edited.** Rebuild từ tất cả metas' `## Related Sources` bằng `build_relations.py`
  (cùng model `build_wiki_source_index.py`). Meta đổi quan hệ → rebuild.
- **Both endpoints / edge** — một JSON object: `{relationship_type, source_ref, target_ref,
  relationship_basis_note, relationship_confidence_note, declared_in, status}` — cho phép query **bidirectional**
  (out-edges của node VÀ in-edges tới node).
- **Canonical direction — store ONCE (CR-024).** Mỗi inverse pair chỉ lưu MỘT chiều canonical; `build_relations.py`
  normalize dạng nghịch về canonical (flip endpoints) rồi dedupe (union basis notes, giữ confidence mạnh nhất):
  `called_by→calls · part_of→contains · downstream_of→upstream_of · superseded_by→supersedes · represented_by→represents · described_by→describes`.
  Reverse là *hướng query* (in-edge "A --calls--> B" = B called_by A), KHÔNG lưu thành edge riêng. Exact-duplicate cũng dedupe.
  **Authoring:** khai mỗi quan hệ MỘT lần (chiều canonical); dựa reverse query cho chiều kia — thay thói quen cũ "declare both ends"
  (có trước relations.jsonl). Documentary 9-roles (`upstream_input`/`downstream_*`/...) KHÔNG phải inverse pair → không auto-normalize.
- **KHÔNG vào `index.jsonl`** — projection riêng, dành riêng (giữ Slim Index).
- **Broken refs surface, không drop:** `target_ref` không resolve được trong index → vẫn giữ cả 2 endpoint và báo
  `[BROKEN REF]` (một finding, không drop âm thầm).

**Query (opt-in, one-hop):** `wiki_relations.py`
- `--relations <source_id>` → `## out` (node → others) + `## in` (others → node, reverse/impact view).
- `--expand <source_id>` → out-edges từ `## Related Sources` của meta trực tiếp (authoritative).
- `--rebuild` → regenerate `relations.jsonl`.

**Boundary (không đổi so với §5):** `relations.jsonl` là **one-hop reverse index**, KHÔNG phải graph engine — no
BFS, no transitive closure, no maintained graph DB. Multi-hop vẫn AI-driven: mở meta liên quan, đọc `## Related
Sources` của nó. Relations **opt-in per intent** — intent discovery-only không phải trả phí; `lookup_wiki_source.py`
không đổi.

---

# 7. Cross-references

- Mô hình 2-layer + Related Sources doc: `product/wiki_guidelines/core/specs/WIKI_META_INDEX_SPEC.md`
- Knowledge unit model: `product/methodology/ai_work_system/20_specs/Knowledge_Object_Model_Spec_MVP.md`
- Related Sources scaffold + role enum: CR-AIWS-2026-05-004 (Change 8) / CR-AIWS-2026-05-017
- Three registers + object-node + DP1–DP8 + INV-1..9: `product/change_requests/CR-AIWS-2026-05-023-two-kind-node-model.md`
- Retired-KO removal rationale: `product/change_requests/CR-AIWS-2026-05-005-remove-knowledge-object-layer.md`
