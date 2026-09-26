---
name: {{PACK_TITLE}} {{PACK_VERSION}} — Standard Pack Install Guide
audience: the AI coding tool (hoặc người) đang cài package này vào một dự án đích
target_layout: project root đã có `.ai-work/` (AIWS đã cài) và `.claude/skills/`
generated_by: .ai-work/tooling/build_standard_pack_package.py
template: .ai-work/tooling/templates/standard_pack_install_guide.template.md
---

# Install Guide — {{PACK_TITLE}} (`{{PACK_ID}}`) {{PACK_VERSION}}

> **Package này KHÔNG phải package AIWS.** Nó chở **một Standard Pack** (nội dung chuẩn của một
> tổ chức: process · template · checklist · guideline · rule · aip_template · skill) và cài **lên
> trên** một dự án đã có AIWS. Cài AIWS bằng package AIWS riêng; hai package không thay nhau và
> không chồng file của nhau.

| | |
|---|---|
| `pack_id` | `{{PACK_ID}}` |
| `pack_version` | `{{PACK_VERSION}}` |
| Chủ nội dung (`owner`) | {{OWNER}} |
| `aiws_min_version` | **{{AIWS_MIN_VERSION}}** |
| Areas | {{AREAS}} |
| Build date | {{BUILD_DATE}} |
| Assets / metas trong package | {{ASSET_COUNT}} asset → {{META_COUNT}} meta |

---

## 0. Guard trước khi chép byte nào (§9.3)

Từ chối cài — **không chép gì cả** — khi bất kỳ điều nào đúng:

1. Dự án đích **không có `.ai-work/`** → chưa cài AIWS. Cài AIWS trước.
2. Bản AIWS của dự án **thấp hơn `{{AIWS_MIN_VERSION}}`** (`aiws_min_version` là hợp đồng một
   chiều: pack khai cần AIWS từ bản nào, không bao giờ khai "AIWS tối đa" — §2.1).
3. Dự án **đã có `.ai-work/standard_pack/`** của một pack khác `pack_id`, hoặc của cùng pack ở
   version khác → **dừng, hỏi người**. Nâng cấp pack luôn là hành động tường minh (§9.1).

Cài dở dang tệ hơn không cài.

---

## 1. Payload mapping

{{PAYLOAD_TABLE}}

Tổng số file trong `payload/`: **{{TOTAL_FILES}}** (xem `MANIFEST.md` để có danh sách đầy đủ —
`MANIFEST.md` đếm cây payload thật sau khi build xong, không đếm danh sách dự định).

Quy tắc chép:

- `payload/standard_pack/` → `.ai-work/standard_pack/` — **chép nguyên cây**. Đây chính là layout mà
  mọi `artifact_locator` trong metas trỏ tới (§12), nên đổi đích = làm hỏng toàn bộ meta.
- `payload/standard_pack_wiki/` → `.ai-work/wiki_sources/aiws_meta/standard_pack/` — nhóm meta
  riêng trong namespace `aiws`, cạnh methodology / wiki_guidelines / preset_knowledge.
- `payload/wiki_source_profiles/standard_asset.yml` → `.ai-work/wiki_sources/profiles/` —
  **MERGE, không đè**: thư mục profiles là của dự án; chỉ thêm file còn thiếu. Xem §2 — file này
  bắt buộc, không phải tuỳ chọn.

---

## 2. `standard_asset.yml` là BẮT BUỘC — profile đi theo gói

`lint_wiki._allowed_source_types()` hợp nhất khoá `source_type` đọc từ **các file `.yml` trong thư
mục profiles của chính dự án tiêu thụ** — không phải từ package, không phải từ repo AIWS. Metas của
pack khai `source_type: standard_asset`.

Hệ quả đã đo: **thiếu `standard_asset.yml` trong `.ai-work/wiki_sources/profiles/` thì mọi dự án cài
pack sẽ báo `meta_source_type_unknown` cho từng meta của pack khi lint.** Không phải cảnh báo vô hại
kiểu "thiếu metadata" — nó nói rằng dự án không biết loại nguồn này tồn tại.

Vì vậy package **chở** profile trong `payload/wiki_source_profiles/standard_asset.yml`, và bước cài
phải chép nó vào `.ai-work/wiki_sources/profiles/`. Nếu dự án đã có file cùng tên: **giữ file của dự
án**, so nội dung bằng tay, và chỉ đổi khi người quyết định.

---

## 3. Dựng lại index sau khi chép

Metas chỉ tra cứu được sau khi index namespace `aiws` được dựng lại **tại chỗ** — cùng đường đi mà
preset wiki của AIWS đang dùng (§12):

```bash
py .ai-work/tooling/build_preset_wiki.py --target .
```

Sinh lại `.ai-work/wiki_sources/index.aiws.jsonl` + `relations.aiws.jsonl` từ **toàn bộ**
`aiws_meta/` (gồm cả nhóm `standard_pack/` vừa chép).

---

## 4. Skill của pack (§7.2)

`payload/standard_pack/areas/<AREA>/skills/<name>/` → `<target>/.claude/skills/<name>/`.

- Trùng `name` với một skill đã có trong dự án → **dừng, hỏi người**. Không đè im lặng: hai skill
  cùng tên là hai năng lực khác nhau tranh cùng một trigger, và bên thua biến mất không dấu vết.
- Gỡ pack **không** tự xoá skill đã cài — đó là quyết định của dự án.

---

## 5. Pin version của pack trong dự án (§9)

Sau khi chép xong, ghi lớp version thứ ba vào `.ai-work/project_profile.yml`, trong khối
`AIWS:BEGIN`:

```yaml
standard_pack:
  id: {{PACK_ID}}
  version: {{PACK_VERSION}}
```

Không có đường nào để một bản cài **tự** kéo pack mới về (§9.1). Nâng cấp = chạy lại guide này với
một package mới, do người quyết định.

---

## 6. Khi cần dựng lại metas trong dự án đích

Bình thường **không cần**: metas được sinh lúc đóng gói và chép vào dự án lúc cài. Nhưng nếu dự án
sửa asset (bản tailored — §8) và muốn dựng lại meta:

```bash
py .ai-work/tooling/build_standard_pack_metas.py \
    --pack .ai-work/standard_pack \
    --out .ai-work/wiki_sources/aiws_meta/standard_pack \
    --common          # hoặc --system <id> nếu dự án multi_system
```

> **Tiền đề của builder metas — biết trước để khỏi mất giờ:** nó chỉ chạy khi **pack root nằm dưới
> một cây có `.ai-work/` tổ tiên**. Chạy nó trên một pack nằm ngoài cây như vậy (ví dụ pack vừa
> giải nén ra `C:\Downloads\`, hay một bản copy trong `/tmp`) sẽ **rc=2 với một thông báo lạc đề**:
> lỗi đổ cho một file asset ngẫu nhiên — file nào tình cờ được xử lý trước — chứ không nói "pack
> nằm ngoài cây `.ai-work/`". Cách chạy đúng: chép pack vào `.ai-work/standard_pack/` **trước**,
> rồi mới dựng metas từ đó.

Dựng lại metas xong thì chạy lại §3 (index).

---

## 7. Kiểm tra sau khi cài

```bash
py .ai-work/tooling/lint_standard_pack.py --pack .ai-work/standard_pack
py .ai-work/tooling/lookup_wiki_source.py --query "<một tiêu đề asset trong pack>"
```

- `lint_standard_pack.py` phải 0 ERROR (gồm cả guard `aiws_min_version` ở §0).
- Lookup phải trả về ít nhất một `SRC-STDPACK-*`. Không trả gì → index chưa dựng lại (§3) hoặc
  metas chưa chép đúng chỗ (§1).
- Lint wiki không được báo `meta_source_type_unknown` — báo tức là §2 chưa làm.
