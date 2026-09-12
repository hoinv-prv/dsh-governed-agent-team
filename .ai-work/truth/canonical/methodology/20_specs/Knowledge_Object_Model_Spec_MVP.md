# Knowledge Unit Model Spec for AI Work System MVP
Version: 0.6 (two-kind node model: artifact | object)
Status: Canonical spec
Scope: Knowledge Hub / Specs / Guidelines

> **Revision History** (1 dòng/version — chi tiết: CR file + git history)
> - **v0.1–v0.2** — superseded (CR-AIWS-2026-05-005 / CR-AIWS-2026-05-020 · AIP-EXEC-038).
> - **v0.3 (2026-05-31, CR-AIWS-2026-05-023 / AIP-EXEC-045)** — two-kind node model (DP1–DP8; anti-KO stop-line
>   INV-1..INV-9; thêm §3bis object discovery/identity + object-authoring gate).
> - **v0.4 (2026-08-13, CR-AIWS-2026-08-030 / AIP-EXEC-1027)** — §3bis.5(7): ngoại lệ hẹp của INV-8 cho
>   deterministic build route đã được PO duyệt (DP-030-A = a).
> - **v0.5 (2026-08-13, CR-AIWS-2026-08-031 / AIP-EXEC-1029)** — editorial: retired shapes quarantine → **§8**
>   (nơi duy nhất nêu tên shape cũ); nén Revision History; khử overload "layer". ZERO semantic change.
> - **v0.6 (2026-08-14, CR-AIWS-2026-08-032 / AIP-EXEC-1032)** — object-authoring gate → **SATISFIED**
>   (đóng CAP-1027-03 / CAP-1029-01).

---

# 1. Purpose of this spec

Tài liệu này định nghĩa **đơn vị tri thức (knowledge unit)** của Knowledge Hub trong baseline canonical hiện tại
(mô hình 2-layer, two-kind node), để:

- AI resolve đúng tri thức từ input của HUMAN (tên chính thức, alias, ID, hoặc cách diễn đạt tự nhiên),
- AI route retrieval theo domain / scope / task lens,
- AI mở rộng từ hit đầu tiên sang tri thức liên quan,
- AI **nhận diện / trích (discover) một Knowledge Object** (function / screen / table / …) từ một tài liệu bằng
  suy đoán, dựa trên object-kind definitions + discovery hints (xem **§3bis**),
- giữ Knowledge Hub **tool-agnostic, retrieval-friendly, expansion-friendly**,

với **knowledge unit là một meta có `node_kind: artifact | object`** trong **cùng một layer meta / một index**
(tên gọi "2-layer" = Meta + Index projection) — KO được hiện thực như một node hạng nhất, **không cần một lớp
Knowledge Object riêng** (retired — xem §8).

Lưu ý:
- đây là **logical model**, không phải storage schema implementation,
- không phụ thuộc graph DB / vector DB / wiki app / MCP server,
- là nền để retrieval/routing guideline hoạt động, không thay thế chúng.

---

# 2. Mô hình 2-layer + two-kind node

```text
Layer 1 — Meta (node_kind: artifact | object) : 1 meta / node (wiki_sources/meta/<id>.md).
          • artifact (default) → 1 meta / source file (artifact_locator = path).
          • object             → 1 meta / logical entity (artifact_locator = __OBJECT__, no backing file).
          Mang identity (source_id, lookup_keys, aliases), summary, task tags,
          và section `## Related Sources` cho quan hệ.
Index    — Projection của Layer 1: lookup surface (wiki_sources/index.jsonl), build từ metas (CÙNG index cho cả 2 kind).
```

**Một store / một index (INV-1).** KO **KHÔNG** có store riêng; mọi field/shape của retired KO record bị cấm
error-grade trong bất kỳ meta nào (INV-2 — danh sách duy nhất tại **§8**).
Object là một **node trong cùng meta+index** như artifact — chỉ khác ở `node_kind` và việc không có file nền.

## 2.1. Đơn vị tri thức = meta (node_kind: artifact | object)

> **Bounded partial reversal of v0.2 §2.1** (unit ≡ artifact), ruled DP1–DP8 (2026-05-30, owner sign-off).

Đơn vị AI resolve / route / expand là **meta**, có thể là:
- **artifact node** (mặc định) — đại diện một source file; identity + lookup keys như cũ;
- **object node** — đại diện một **logical entity** (function/screen/table/api/batch/module/concept);
  - **identity = `source_id` thường** (family prefix khuyến nghị `SRC-FUNC-`/`SRC-SCREEN-`/`SRC-TABLE-`…),
    không field định danh riêng nào của retired record (INV-2 — §8);
  - object subtype **dùng chính `source_type`** (open-union; KHÔNG có `node_subtype` riêng);
  - `artifact_locator = __OBJECT__` (sentinel, INV-9); không có file để đọc;
  - sống trong **CÙNG `index.jsonl`**, tìm bằng **CÙNG lookup** (KHÔNG có `--kind` flag, KHÔNG field index mới —
    `node_kind` là meta-only, INV-7);
  - **never-empty:** summary suy biến → ERROR; phải có ≥1 out-edge (INV-4).

Cả hai kind đều **identifiable** (lookup_keys + aliases), **searchable** (index projection), **linkable**
(`## Related Sources`), **reusable**.

`node_kind` là **field meta tùy chọn, mặc định `artifact`** (zero migration — mọi artifact meta hiện có không đổi).

## 2.2. Object node = POINTER, KHÔNG phải container (hard invariant — SHAPE 2 forbidden)

> Pin của v0.2 §2.2: knowledge unit KHÔNG phải "một object record tổng hợp nhiều metas". Trong two-kind node đây là
> **hard object invariant** (DP5 / INV-3, error-grade lint).

Một object node là **SHAPE 1 — pure relation/identity anchor**. Nó **KHÔNG** được:
- mang field hay aggregation-heading nào của retired record (danh sách: §8),
- roll-up / tổng hợp nội dung của các metas con (**SHAPE 2 — FORBIDDEN**, xem §8),
- tham chiếu một objects-store (INV-1 — §8).

Knowledge unit cũng KHÔNG phải: raw source file; raw chunk do RAG engine tạo.

Quan hệ "object gồm nhiều phần" biểu diễn bằng edge điều hướng `part_of` (navigation-only) — **NEVER** một type
`contains` roll-up nội dung.

---

# 3. Identity, naming, và natural-language resolution

Một function/screen/table/concept được định danh qua **identity của node**:
- với **object node** → `source_id` (family-prefix) + `lookup_keys`/aliases (xem §3bis.2);
- với **artifact node** → identity nằm trong `lookup_keys` + aliases của artifact meta.

- **ID / tên chính thức** → T1 `lookup_keys` (vd bare `F03` vẫn là T1 key dù object id là `SRC-FUNC-F03`).
- **Tên đa ngôn ngữ (vi/ja/en)** → aliases / `lookup_keys`, để AI resolve bất kể ngôn ngữ.
- **Cách diễn đạt tự nhiên** → match qua T2/T3 keys + aliases (xem `Lookup_Key_Strategy_Spec_MVP`).

Khi nhiều artifact mô tả cùng một business function (split design FE/API/BE), chúng được **liên kết với nhau qua
`## Related Sources`** (role `companion_design`). Nếu cần một điểm neo chung cho function đó, dùng một **object node**
(representation register — §3bis.6), KHÔNG gộp nội dung vào một record.

---

# 3bis. Knowledge Object discovery & identity extraction

> **KO concept = unchanged.** Một KO được hiện thực như một **`node_kind: object` meta treated like any source
> artifact** (ordinary `source_id`, CÙNG `index.jsonl`, `## Related Sources`; `artifact_locator: __OBJECT__`).
> **SHAPE 1 only** — không mang bất kỳ shape nào của retired record (INV-1/INV-2 — xem §8).

**Nguyên tắc:** canonical chỉ cung cấp **định nghĩa + hints**; AI **suy đoán** trên tài liệu thật, rồi **đề xuất
candidate** — **HUMAN author** object meta (DP6, never auto-create). Specifics từng dự án → `project_profile` / PMP.

## 3bis.1. Object Kind Catalog (canonical-but-extensible)

Kind = `source_type` subtype của object (DP2, rides open-union `source_type`), kèm family prefix cho `source_id` (DP3):

| kind | `is_grouping` | source_id family prefix |
|---|---|---|
| `function` / feature | no | `SRC-FUNC-` |
| `screen` / view | no | `SRC-SCREEN-` |
| `api` / endpoint | no | `SRC-API-` |
| `batch` / job | no | `SRC-BATCH-` |
| `table` / entity | no | `SRC-TABLE-` |
| `module` / subsystem | **yes** (navigation-only `part_of`; NEVER `contains`-rollup) | `SRC-MOD-` |
| `concept` / term | no | `SRC-CPT-` |

`field`/`column`/`business_rule` chưa dùng như object **kind** ở MVP. `field`/`column` xử lý trong parent `screen`/`table`. `business_rule` (volatile + đã được phủ bởi design doc tương ứng) — tri thức nằm trong **parent design doc** qua nội dung / knowledge targets của doc; **KHÔNG** tạo object node `SRC-BIZ-` riêng (tránh maintain 2 nơi). `SRC-BIZ-` vẫn **reserved** — tái kích hoạt sau **không cần re-key, không cần CR mới** (open-union `source_type`, DP2/DP3). Project extend dưới `prj_` source_type — không cần CR.

> **Editing guard (CR-AIWS-2026-06-032):** a kind name above may ALSO be a `knowledge_target`/domain term (e.g. `business_rule`). When editing this catalog, triage each occurrence by ROLE (kind = edit; term = leave) — never blind grep-replace a kind name; it would destroy the term/coverage layer. See `product/guidelines/SKILL_AUTHORING_CONVENTIONS.md` §3.

## 3bis.2. Identity (identity = source_id)

- `source_id`: native `F03` → **`SRC-FUNC-F03`**; synthesized → `SRC-FUNC-create-booking`. Không field định danh riêng (INV-2 — §8).
- **Findability:** bare token `F03` + tên người-đọc (vi/ja/en) là `lookup_keys`/aliases (T1/T2); object ở CÙNG slim index,
  tìm bằng CÙNG lookup. "Everything about F03" = `wiki_relations.py --relations SRC-FUNC-F03` (out+in), KHÔNG phải lookup (DP7).
- `node_kind: object`; `artifact_locator: __OBJECT__` (INV-9); never-empty (degenerate→ERROR; ≥1 out-edge — INV-4).

## 3bis.3. source_id lifecycle (synthesized core)

1. **Rename ≠ re-key:** source_id đóng băng sau khi human-confirm HOẶC bị tham chiếu bởi out-edge `## Related Sources`
   của meta khác (relations.jsonl chỉ là projection, không phải trigger). Rename → name mới = display, name cũ → alias;
   re-key chỉ với old_id giữ làm alias + refs cập nhật + flag.
2. **Deterministic slug** (chỉ cho synthesized core; native core giữ verbatim): trim+collapse → case-fold → NFKC →
   non-`[a-z0-9]`→`-` → strip.
3. **JA/VI:** giữ tên gốc verbatim làm name+alias; core slug ưu tiên native-code → EN/romaji → transliterate(flag) → else để core unresolved.
4. **Collision:** family-prefix namespaced theo kind; trong cùng kind: cùng object→reuse, khác object trùng slug→disambiguate+flag, không rõ→HUMAN gate.
5. **Match-or-mint:** trên bản revised, match identity cũ (source_id→alias→evidence) TRƯỚC khi mint.

## 3bis.4. Discovery hints (heuristic)

Tái dùng `classification_signals` (Artifact_Type_Taxonomy) + `object_extraction_targets` (Wiki Knowledge Profile).
- **identity_source_hints** (precedence): filename → document_title → in-doc heading (機能一覧/機能概要) → cross-ref.
- **locator_doc_hints:** Function List / 機能一覧; project scope / system overview; related req/design docs.

## 3bis.5. Inference contract + necessity test (MVP, inference-first)

1. Detect object kind (object_extraction_targets + reading).
2. Gather identity via hints, kèm **evidence** (1 dòng locator/quote; gắn confidence `asserted|inferred|candidate` —
   `asserted` cần evidence; thiếu evidence → hạ `candidate`, KHÔNG chặn).
3. **Necessity test (DP6):** thử biểu diễn bằng `## Related Sources companion_design` trên artifact có sẵn TRƯỚC;
   tạo object node CHỈ khi không có host single-artifact tự nhiên.
4. Cardinality (tối giản): 1 chủ thể rõ → 1 object; danh sách (Function List) → nhiều; không rõ → HUMAN gate.
5. **HUMAN-gate checklist** (confirm trước khi candidate thành object được author): cardinality chưa rõ / không có
   evidence / synthesized source_id dùng làm join ≥2 metas / slug clash / kind nhập nhằng.
6. **Output = CANDIDATE** (capture inbox, rule #7). **HUMAN author** object meta (DP6); AI never auto-create; no tool
   instantiates an object meta (INV-8) — **trừ ngoại lệ hẹp ở mục (7)**. `key_objects_and_terms.objects[]`
   (artifact-understanding) chỉ là discovery scratch — KHÔNG phải object persistent (object persistent = object-node meta).
7. **Ngoại lệ của INV-8 (v0.4, CR-AIWS-2026-08-030) — deterministic build route đã được PO duyệt.**
   Một build route **đã được PO duyệt bằng CR** MAY instantiate object meta, khi và chỉ khi **cả hai** điều kiện:
   **(1)** route phải có cách **phân biệt chắc chắn** node của chính nó với node do người viết, và **không bao giờ**
   ghi đè loại thứ hai. Tiền lệ **F10** (`ASP_COBOL_SOURCE_BUILD_GUIDE`): node của builder mang sentinel
   `__OBJECT__`, nên node có `artifact_locator` **thật** chắc chắn không do builder viết.
   ⚠️ Discriminator đó **không phổ quát** — nó chỉ đúng khi object node người viết mang locator thật. Quy ước
   trong `wiki_source_profiles/knowledge_object.yml` lại cho object node **hand-authored** mang chính `__OBJECT__`;
   trong corpus theo quy ước ấy, sentinel **không** phân biệt được ai viết. Route mới phải **tự chứng minh**
   discriminator của mình đúng trong corpus đích, không được mượn F10 như mặc định;
   **(2)** nội dung node **dẫn xuất xác định** từ nguồn/catalog, không từ phán đoán của AI.
   **Vế "AI never auto-create" KHÔNG bị nới:** AI tự tạo object meta theo phán đoán vẫn **CẤM** — đó mới là thứ
   INV-8 sinh ra để chặn. Ngoại lệ này ghi nhận hiện trạng do `CR-AIWS-2026-08-026` (ASP COBOL preset) tạo ra;
   route mới muốn dùng ngoại lệ phải nêu rõ trong CR của nó và chứng minh **cả hai** điều kiện.

> **Object-authoring gate (v0.3 — SATISFIED, CR-AIWS-2026-08-032):** guards (CR-023 Change-5) + INV-5
> named-consumer test đã land; corpus hand-authored đầu tiên = 13 object meta `SRC-CPT-*` (AIP-EXEC-1028).
> Gate áp cho hand-author flow; build route deterministic đi qua ngoại lệ §3bis.5(7).

## 3bis.6. Relations của object node (3 registers — DP4)

- **representation** (Object↔Artifact): object `represented_by` các tài liệu mô tả nó (RD/BD/DD/Testcase); mỗi tài liệu
  `represents` object. (Discovery "owns vs mentions" = primary `represents` vs nhắc thoáng.)
- **domain** (Object→Object, via `x:`): vd `x:calls`, `x:part_of` (navigation-only).
- **migration** (một dạng domain): cross-system = HAI object (as-is / to-be), KHÔNG merge; mapping = `x:migrates_to`
  (inverse `x:migrated_from`) + `x:equivalent_to` (**symmetric — KHÔNG inverse-pair, không auto-normalize**). Cardinality
  = đếm edge; optional `system_side: as_is|to_be|shared` (default absent); ranh giới hệ thống cụ thể → project_profile.
- **Pointer-only (DP5/INV-3):** object meta KHÔNG aggregate (retired shapes — §8) — error-grade.

Xem `Knowledge_Expansion_Link_Spec_MVP.md` (v0.5) cho semantics đầy đủ của 3 registers.

---

# 4. Quan hệ & expansion = `## Related Sources`

Quan hệ được biểu diễn bằng section `## Related Sources` trong từng meta:

- mỗi entry nêu một node liên quan + **role có kiểu** thuộc một trong **3 registers** (documentary: 9 roles
  Artifact→Artifact vd `upstream_input`/`companion_design`/`downstream_target`; representation: `represents`/`represented_by`
  Object↔Artifact; domain: `x:` Object→Object),
- role có hướng và task-useful, dẫn AI từ hit đầu tiên sang tri thức liên quan tiếp theo,
- section được author/scaffold (CR-AIWS-2026-05-004 Change 8, CR-AIWS-2026-05-017),
- **KHÔNG** project vào `index.jsonl`; reverse/impact view = `wiki_relations.py --relations` (one-hop, no global graph).

Xem `Knowledge_Expansion_Link_Spec_MVP.md` (v0.5) cho semantics của relationship roles + 3 registers.

---

# 5. Design goals (intent giữ nguyên, đặt trên substrate 2-layer two-kind node)

- resolve đúng tri thức từ nhiều cách diễn đạt,
- route theo domain / scope / task lens,
- expand sang tri thức liên quan,
- discover object từ tài liệu bằng suy đoán (§3bis),
- tool-agnostic + reusable.

Đạt được bằng: meta (artifact|object, identity + summary) + index (findability) + `## Related Sources` (expansion) —
KO là node trong cùng substrate, không cần lớp object riêng.

---

# 6. Quan hệ với Working AIP / Use Case

- Use Case / task resolve target của nó thành một hoặc nhiều **metas** (artifact hoặc object node).
- AI đọc meta trước (Wiki-first), rồi mở source artifact khi evidence depth yêu cầu (object node không có file → đọc các
  artifact mà nó `represented_by`).
- Working AIP không thay thế Knowledge Hub; Hub cung cấp context object/concept qua metas + Related Sources.

---

# 7. Cross-references

- Mô hình 2-layer + Related Sources + node_kind: `product/wiki_guidelines/core/specs/WIKI_META_INDEX_SPEC.md`
- Relationship-role semantics + 3 registers: `product/methodology/ai_work_system/20_specs/Knowledge_Expansion_Link_Spec_MVP.md` (v0.5)
- Lookup key tiers: `product/wiki_guidelines/core/specs/Lookup_Key_Strategy_Spec_MVP.md`
- Object discovery inputs: `product/wiki_guidelines/core/specs/Artifact_Type_Taxonomy_Spec_MVP.md` (classification_signals),
  `WIKI_KNOWLEDGE_PROFILE_SPEC.md` (object_extraction_targets), `ARTIFACT_UNDERSTANDING_OUTPUT_SCHEMA.md` (key_objects_and_terms)
- Routing / access: `Knowledge_Routing_Spec_MVP.md`, `Knowledge_Access_Interface_Spec_MVP.md`
- Two-kind node model + DP1–DP8 + INV-1..INV-9: `product/change_requests/CR-AIWS-2026-05-023-two-kind-node-model.md`
- Retired-KO removal rationale: `product/change_requests/CR-AIWS-2026-05-005-remove-knowledge-object-layer.md`

---

# 8. Retired shapes — FORBIDDEN (anti-KO stop-line INV-1..INV-9)

Các shape sau thuộc **retired KO record** — cấm error-grade; đây là nơi **duy nhất** trên live tree liệt kê chúng:

| Retired shape | INV |
|---|---|
| Store riêng: `wiki_sources/objects/` · `objects/index.jsonl` | INV-1 |
| Field trong meta: `object_id` · `expansion_links` · `canonical_object_refs` · `source_anchor` | INV-2 / INV-3 |
| SHAPE 2 — container/roll-up: heading `Contents / Aggregated / Synthesized / Child Sources`, tổng hợp nội dung metas con | INV-3 / DP5 |
| Tool refresh-queue · builder ghi object meta · KO skill (`/build-knowledge-object`, `/refresh-knowledge-object`) | INV-8 — ngoại lệ duy nhất: §3bis.5(7) |
| `artifact_locator: __OBJECT__` ↔ `node_kind: object` lệch nhau | INV-9 |

Nguồn: `CR-AIWS-2026-05-023` (invariants) · `CR-AIWS-2026-05-005` (removal).
