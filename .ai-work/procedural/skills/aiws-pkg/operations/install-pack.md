# aiws-pkg — operation: install-pack

> Operation of the `aiws-pkg` domain skill. **New verb — CR-AIWS-2026-09-001.** Every gate herein is
> binding. **Cài một Standard Pack, KHÔNG phải cài AIWS** — nhầm verb là nhầm package.
> Hợp đồng: `Standard_Pack_Contract_Spec_MVP` (§7.2 skill · §8 ranh giới · §9 ba lớp version · §12 wiki).


## Purpose
Cài **mới** và **nâng cấp** một Standard Pack (bộ tài sản quy trình có version của một tổ chức:
process · template · checklist · guideline · rule · aip_template · skill) lên một dự án **đã có AIWS**.
Package pack là package **thứ hai**, độc lập với package AIWS: hai bên không thay nhau, không chồng
file của nhau, và mỗi bên có lớp version riêng.

## Inputs
- `pack_package_path` (required) — thư mục package do `build_standard_pack_package.py` sinh; nhận ra
  bằng `payload/standard_pack/pack.yml`. Thiếu file đó thì đây **không** phải package pack.
- `project_root` (required) — gốc dự án đích, nơi có `.ai-work/`.
- **`mode` KHÔNG phải input.** Fresh-install hay upgrade do tool suy ra từ `.ai-work/standard_pack/`
  đang có trong dự án. Đừng hỏi HUMAN rồi đoán — hỏi cái tool tự biết là mời một câu trả lời sai.

## Flow
1. **Đọc `install_guide.md` của chính package đó** — nó được sinh lúc build từ `INSTALL_MAP` của
   builder, nên nó (không phải file này) là bản authoritative về payload→đích cho **đúng** package
   trong tay. File này mô tả *quy trình*; guide mô tả *nội dung bản dựng đó*.
2. **Dry-run trước, luôn luôn:**
   `py .ai-work/tooling/install_standard_pack.py --package <pkg> --target <project_root> --dry-run`
   In ra plan file-level (added · updated · unchanged · removed) cho từng đích, cộng trạng thái pin.
   Mọi guard đã chạy xong ở bước này, nên một dry-run sạch nghĩa là lượt ghi thật sẽ không bị chặn.
3. **Trình plan cho HUMAN và chờ confirm.** Nêu rõ: fresh install hay upgrade, pack nào → version nào,
   bao nhiêu file bị **xoá** (upgrade thay nguyên cây pack), skill nào sẽ được cài.
4. **Chạy thật** — cùng lệnh, bỏ `--dry-run`. `--dry-run` là **opt-in**: chạy lệnh trần là ghi thật.
5. **Verify sau khi cài** (đúng thứ tự này):
   - `py .ai-work/tooling/lint_standard_pack.py --pack .ai-work/standard_pack` → 0 ERROR
   - `py .ai-work/tooling/lookup_wiki_source.py --query "<một tiêu đề asset trong pack>"` → phải trả
     về ít nhất một `SRC-STDPACK-*`. Không có → index chưa dựng lại, hoặc metas chưa vào đúng chỗ.
   - `py .ai-work/tooling/lint_all.py` (hoặc lint wiki) **không** được báo `meta_source_type_unknown`
     — báo tức là `standard_asset.yml` chưa nằm trong `.ai-work/wiki_sources/profiles/`.
6. **Report cho HUMAN:** pack_id@version đã pin, số file mỗi đích, skill đã cài, skill mà pack **không
   còn ship** (tool để nguyên — gỡ là quyết định của dự án), và câu lệnh tra cứu để họ thử ngay.

## Payload → đích (tool đọc từ `INSTALL_MAP`, đây là bản để đọc)
| payload | đích trong dự án | ngữ nghĩa |
|---|---|---|
| `payload/standard_pack/` | `.ai-work/standard_pack/` | **pack-owned** — bị thay toàn bộ mỗi lần cài/nâng cấp (§8.1) |
| `payload/standard_pack_wiki/` | `.ai-work/wiki_sources/aiws_meta/standard_pack/` | metas, namespace `aiws`, nhóm riêng (§12) |
| `payload/wiki_source_profiles/standard_asset.yml` | `.ai-work/wiki_sources/profiles/` | **MERGE, không đè** — thư mục profiles là của dự án |
| `payload/standard_pack/areas/<A>/skills/<name>/` | `.claude/skills/<name>/` | skill của pack (§7.2) |
| — | `.ai-work/project_profile.yml` | pin `standard_pack: {id, version}` trong khối `AIWS:BEGIN` (§9) |
| — | `index.aiws.jsonl` + `relations.aiws.jsonl` | dựng lại tại chỗ sau khi chép (cùng đường của preset wiki) |

## Nâng cấp — **cùng một lệnh**, không có đường tự động
- Nâng cấp pack luôn là hành động tường minh của người (§9.1). Không có cơ chế nào để một bản cài tự
  kéo pack mới về, và AIWS upgrade **không** đụng tới pack.
- Cây pack bị **thay**: asset mà pack chủ đã gỡ phải biến mất khỏi dự án, nếu không dự án còn đang làm
  theo một checklist đã bị khai tử. Tool xoá đúng những file package không còn ship (không rmtree —
  rmtree-rồi-copy làm mọi file trông như đã đổi trên checkout CRLF và chôn mất delta thật).
- Meta của asset đã gỡ cũng bị xoá theo, vì locator của nó đã chết.
- `.ai-work/project_process/` — **bản tailored của dự án — không bao giờ bị chạm.** Đó là lý do cây thứ
  hai tồn tại. Ai sửa thẳng trong `.ai-work/standard_pack/` sẽ mất trắng ở lượt nâng cấp này.

## Rules
- **Mọi guard chạy trước byte đầu tiên** (§9.3). Một lượt từ chối để lại dự án **byte-identical** — cài
  dở dang tệ hơn không cài. Guard nào cũng dừng, không cái nào "cảnh báo rồi chạy tiếp".
- **Từ chối khi:** dự án không có `.ai-work/` (chưa cài AIWS — cài AIWS trước) · không có
  `.ai-work/project_profile.yml` (chỗ chứa pin — `py .ai-work/tooling/project_profile.py init`) · bản
  AIWS thấp hơn `aiws_min_version` của pack · **không đọc được** bản AIWS của dự án (guard không đọc
  được input là guard đang tắt, nên nó dừng thay vì đoán).
- **Đã cài một pack KHÁC `pack_id` → DỪNG, hỏi HUMAN.** Cài hai pack cùng lúc chưa được định nghĩa
  (§13.4), và thay pack này bằng pack kia là quyết định của người, không phải một bước copy.
- **Skill trùng tên → DỪNG, hỏi HUMAN, không đè** (§7.2). Hai skill cùng tên là hai năng lực tranh cùng
  một trigger và bên thua biến mất không dấu vết. Cách gỡ: đổi tên skill của dự án, đổi tên skill của
  pack, hoặc bỏ một bên — cả ba đều là quyết định của người. *(Skill do chính pack này cài lần trước
  thì không tính là trùng — tool đọc cây pack đang cài để biết cái nào là của nó.)*
- **`standard_asset.yml` là BẮT BUỘC, không phải tuỳ chọn.** `lint_wiki` hợp nhất `source_type` từ thư
  mục profiles **của dự án tiêu thụ**; thiếu file này thì mọi meta của pack bị `meta_source_type_unknown`.
  Dự án đã có file cùng tên → **giữ file của dự án**, so bằng tay, chỉ đổi khi người quyết định.
- **Không tự sửa nội dung pack để cho lint xanh.** `lint_standard_pack.py` đỏ ⇒ package hỏng ⇒ trả về
  cho chủ pack. Nội dung là của họ; AIWS chỉ sở hữu hình dạng.
- **Không hứa hộ lookup:** metas chỉ tra cứu được sau khi index namespace `aiws` được dựng lại. Tool
  làm việc đó ở cuối; nếu nó rc≠0 thì file đã cài xong nhưng **chưa** tra cứu được — chạy
  `py .ai-work/tooling/build_preset_wiki.py --target <project_root>` rồi verify lại, đừng báo "xong".
- Gỡ pack **không** tự xoá skill đã cài (§7.2) — đó là quyết định của dự án.
