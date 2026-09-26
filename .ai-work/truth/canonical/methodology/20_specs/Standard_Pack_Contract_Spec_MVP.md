# Standard Pack Contract Spec for AI Work System MVP
Version: 0.1 (draft — CR-AIWS-2026-09-001)
Status: Canonical MVP spec (applied by CR-AIWS-2026-09-001, 2026-09-11)
Scope: MVP — hợp đồng giữa AIWS và một Standard Pack do bên khác sở hữu

> **Authority:** spec này định nghĩa *hợp đồng*, không định nghĩa *nội dung*. AIWS sở hữu layout, frontmatter,
> schema task catalog, lint và mọi tool đọc pack. Bên sở hữu pack (với `vti_standard_pack` là QA Team) sở hữu
> toàn bộ nội dung: process, template, checklist, guideline, rule, AIP template, skill.
> **Placement:** `product/methodology/ai_work_system/20_specs/Standard_Pack_Contract_Spec_MVP.md`
> + mirror `.ai-work/truth/canonical/methodology/20_specs/`.

---

# 1. Mục đích và phạm vi

Một **Standard Pack** là gói tài sản quy trình có version của một tổ chức, được AIWS chở tới dự án để dự án
làm việc theo chuẩn công ty ngay sau khi cài, và tailoring khi cần.

Spec này chốt sáu thứ, đủ để viết tool và viết test:

1. **Layout** của một pack (§2).
2. **Frontmatter** bắt buộc của mỗi asset (§3).
3. **Ngữ nghĩa classification** — dự án được đổi gì (§4).
4. **Phân vai AIP / Skill / Rule** trong một task (§5).
5. **Schema task catalog** — task theo bước quy trình, bind sang asset (§6).
6. **Ranh giới pack ↔ bản tailored của dự án**, versioning, và lint (§8–§11).

Ngoài phạm vi: nội dung quy trình; bootstrap framework nhiều pack; engine hợp nhất
"effective project process"; AI tự tailoring. Dự án tailoring **bằng tay** (quyết định D043 của pilot).

---

# 2. Layout của một pack

Pack là một cây thư mục, gốc có `pack.yml`. Tổ chức **theo area trước** (area = một bước lớn của
vòng đời: `RD`, `BD`, `DD`, `CD`, `UT`, `IT`, `ST`), vì tailoring và bàn giao đều diễn ra theo area.

```
<pack-root>/
  pack.yml
  README.md
  CHANGELOG.md
  common/                       # dùng chung mọi area
    roles.yml                   # BẮT BUỘC khi có task nào khai roles (§6.4)
    <asset>.md ...
  areas/
    DD/
      process.md                # asset kind=process của area
      task_catalog.yml          # §6
      templates/    <asset>.md
      checklists/   <asset>.md
      guidelines/   <asset>.md
      rules/        <asset>.md
      aip_templates/<asset>.md
      skills/       <skill-name>/SKILL.md      # §7
    CD/ …  UT/ …
```

**Luật layout:**

- Thư mục kind (`templates/`, `checklists/`, `guidelines/`, `rules/`, `aip_templates/`, `skills/`) là **tuỳ chọn**:
  vắng nghĩa là area không có asset kind đó. Không tạo thư mục rỗng để "cho đủ".
- Một area **có tài liệu** phải có `process.md` và `task_catalog.yml`. Một area **chưa có tài liệu** chỉ cần
  `README.md` nói rõ đang thiếu gì; không dựng task catalog giả.
- `common/` không có `task_catalog.yml` — task luôn thuộc một area.
- Đường dẫn quyết định `area` và `kind` của asset, nhưng **frontmatter mới là nguồn sự thật** (§3); lint so hai
  bên và báo khi lệch.

## 2.1 `pack.yml`

```yaml
pack_id: vti_standard_pack        # BẮT BUỘC — slug, [a-z0-9_], duy nhất giữa các pack
pack_version: 0.1.0               # BẮT BUỘC — semver, KHÔNG tiền tố "v"
title: VTI Engineering Standard Pack   # BẮT BUỘC
owner: QA Team                    # BẮT BUỘC — ai chịu trách nhiệm nội dung
aiws_min_version: v1.2.1          # BẮT BUỘC — bản AIWS tối thiểu chạy được pack này
areas: [DD]                       # BẮT BUỘC — danh sách area có nội dung; phải khớp areas/ trên đĩa
description: >                    # tuỳ chọn
  Bộ chuẩn engineering của VTI cho pilot AI-enabled development process.
```

`aiws_min_version` là **hợp đồng một chiều**: pack tuyên bố cần AIWS từ bản nào. Tool cài từ chối khi bản
AIWS của dự án thấp hơn (§9.3). Pack không bao giờ khai "AIWS tối đa".

---

# 3. Frontmatter của asset

Mọi file asset (`.md`) đều mở đầu bằng YAML frontmatter. Đây là khác biệt cố ý với `20_specs/` của AIWS
(vốn dùng khối `Version:`/`Status:`): asset của pack được **máy đọc** — bởi lint, resolver, builder meta —
nên nó cần trường có tên, không phải văn xuôi.

```yaml
---
artifact_type: standard_asset     # BẮT BUỘC — hằng, đúng chuỗi này
asset_id: DD-CHK-dd-review        # BẮT BUỘC — §3.1
pack_id: vti_standard_pack        # BẮT BUỘC — khớp pack.yml
area: DD                          # BẮT BUỘC — một area trong pack.yml, hoặc COMMON
kind: checklist                   # BẮT BUỘC — §3.2
title: DD Review Checklist        # BẮT BUỘC
classification: default           # BẮT BUỘC — §4
owner: QA Team                    # BẮT BUỘC
status: active                    # BẮT BUỘC — draft | active | retired
applies_to_tasks: [DD-REVIEW]     # tuỳ chọn — back-link, tiện đọc; task_catalog mới là nguồn bind
criteria_for: DD                  # tuỳ chọn — §4.3, đánh dấu asset mang "definition of good"
tailoring_note: >                 # BẮT BUỘC khi classification=mandatory; nên có ở mọi asset
  Vì sao cố định (mandatory) HOẶC dự án được đổi phần nào (default/tailorable).
---
```

## 3.1 `asset_id`

Dạng `<AREA>-<KIND3>-<slug>`:

- `<AREA>` = `area` viết hoa, hoặc `COMMON`.
- `<KIND3>` = mã ba chữ của kind: `PRC` process · `TPL` template · `CHK` checklist · `GDL` guideline ·
  `RUL` rule · `AIP` aip_template · `SKL` skill.
- `<slug>` = `[a-z0-9-]+`.

`asset_id` **duy nhất trong toàn pack** và **ổn định**: nó là thứ task catalog, bản tailored của dự án và
wiki meta đều trỏ tới. Đổi `asset_id` là một thay đổi phá vỡ, phải đi cùng bump `pack_version` và ghi vào
`CHANGELOG.md`.

## 3.2 `kind` — bảy giá trị

| `kind` | Thư mục | Là gì | Task bind qua |
|---|---|---|---|
| `process` | `<area>/process.md` | WHAT của area: input/output, gate, trách nhiệm | `assets.process` |
| `template` | `templates/` | Khuôn deliverable | `assets.templates[]` |
| `checklist` | `checklists/` | Danh mục kiểm, có trạng thái từng mục | `assets.checklists[]` |
| `guideline` | `guidelines/` | Hướng dẫn cách làm, không ràng buộc cứng | `assets.guidelines[]` |
| `rule` | `rules/` | Ràng buộc phải tuân, kiểm được | `assets.rules[]` |
| `aip_template` | `aip_templates/` | Khuôn AIP cho một task tạo/sửa deliverable | `aip.template` |
| `skill` | `skills/<name>/SKILL.md` | Năng lực tái dùng, AI gọi được | `skills[]` |

---

# 4. Ngữ nghĩa `classification`

Bốn giá trị. Đây là chỗ duy nhất định nghĩa dự án được đổi gì, và là thứ lint cưỡng chế.

| `classification` | Dự án được làm gì | Ràng buộc kiểm được |
|---|---|---|
| `mandatory` | Dùng nguyên bản | Bản tailored phải khai `deviation_ref` (§8.2); thiếu → lint error |
| `default` | Dùng khi không có bản tailored | Tailor tự do, chỉ cần header provenance |
| `tailorable` | Nên tailor cho hợp dự án | Pack chỉ là điểm xuất phát |
| `reference` | Tham khảo | Không được bind vào `human_gate` của task (§6.5) |

## 4.1 Ranh giới process ↔ dự án

Quy trình quy định **WHAT**: input/output bắt buộc, tiêu chí chất lượng, gate, trách nhiệm.
Dự án và thành viên quyết **HOW** trong ranh giới đó. Một asset mô tả HOW mà đánh `mandatory` là dấu hiệu
phân loại sai — `tailoring_note` phải giải thích được vì sao HOW đó buộc phải cố định.

## 4.2 Ai đổi được classification

Chỉ chủ pack. Dự án không đổi `classification` trong bản tailored của mình: `classification` mô tả *tài sản
của công ty*, không mô tả *bản sao của dự án*. Muốn nới thì xin chủ pack, hoặc dùng `deviation_ref`.

## 4.3 "Definition of good" nằm ở đâu

Tiêu chí chất lượng của một deliverable **không** có kind riêng. Nó là một `checklist` (khi dùng để kiểm từng
mục) hoặc một `rule` (khi là ràng buộc cứng), và đánh dấu bằng `criteria_for: <AREA>`. Lý do: thêm một kind
`quality_criteria` sẽ tạo hai đường bind cho cùng một thứ trong task catalog, còn AIWS thì không có cách nào
kiểm nội dung tiêu chí — nó chỉ kiểm được liên kết.

---

# 5. AIP vs Skill vs Rule — ba vai, không chồng nhau

| | Là gì | Sở hữu | Bind ở đâu |
|---|---|---|---|
| **AIP** | Hợp đồng thực thi của **một task cụ thể**: objective, scope, step, done criteria | AIWS định nghĩa khuôn; pack cung cấp instance theo task | `aip.template` |
| **Skill** | **Năng lực tái dùng** dùng lại được ở nhiều task | AIWS (skill lõi) hoặc pack (skill của quy trình) | `skills[]` |
| **Rule** | **Ràng buộc** mà output phải thoả | Pack | `assets.rules[]` |

**Luật bắt buộc:** task tạo hoặc sửa deliverable (`archetype` là `generate_artifact` hoặc `update_artifact`)
**phải** bind `aip.template` với `aip.mode: mandatory`. Đây là D024 của pilot, và cũng là gate D0 của
`SOP_DevelopmentTasks` trong Truth của dự án. Lint cưỡng chế bằng `deliverable_task_no_aip` (§11).

Không được biểu diễn cùng một thứ hai lần: một checklist đã là `assets.checklists[]` thì không đồng thời là
một skill "chạy checklist"; một ràng buộc đã là `rule` thì AIP template không chép lại nội dung ràng buộc đó
mà trỏ tới `asset_id`.

---

# 6. `task_catalog.yml`

Một file cho mỗi area. Đây là **instance** — AIWS chỉ sở hữu schema và resolver.

```yaml
schema_version: 1                 # BẮT BUỘC — hằng 1 ở MVP
pack_id: vti_standard_pack        # BẮT BUỘC — khớp pack.yml
area: DD                          # BẮT BUỘC — khớp thư mục
tasks:
  - task_id: DD-CREATE            # BẮT BUỘC — §6.1
    title: Tạo DD từ BD đã duyệt  # BẮT BUỘC
    step: 3                       # BẮT BUỘC — thứ tự bước trong area (int ≥ 1)
    archetype: generate_artifact  # BẮT BUỘC — §6.2
    roles:                        # tuỳ chọn — §6.4
      owner: dev
      reviewer: [leader, brse]
      approver: leader
    inputs: [approved_BD]         # tuỳ chọn — nhãn tự do, mô tả input nghiệp vụ
    assets:                       # BẮT BUỘC (có thể rỗng từng nhóm)
      process: DD-PRC-dd-process
      templates: [DD-TPL-dd]
      checklists: [DD-CHK-dd-self-check]
      guidelines: []
      rules: []
    aip:                          # BẮT BUỘC — §5
      mode: mandatory             # mandatory | recommended | none
      template: DD-AIP-create-dd  # BẮT BUỘC khi mode ≠ none
    skills: [DD-SKL-dd-self-check, aiws-runtime-review-checklist]   # tuỳ chọn — §7.3
    outputs: [DD_draft, why_evidence]   # BẮT BUỘC — nhãn deliverable
    human_gate:                   # BẮT BUỘC
      required: true
      checker: leader             # BẮT BUỘC khi required=true — một role của §6.4
    machine_verification: []      # tuỳ chọn — nhãn kiểm máy (compile/lint/test/coverage)
    downstream: [DD-REVIEW]       # tuỳ chọn — task_id kế tiếp, trong hoặc ngoài area
```

## 6.1 `task_id`

Dạng `<AREA>-<VERB>`, `[A-Z0-9-]+`, duy nhất **toàn pack** (không chỉ trong area) — vì `downstream` và
override của dự án đều trỏ tới nó không kèm area.

## 6.2 `archetype` — sáu giá trị

`plan` · `understand` · `generate_artifact` · `review_artifact` · `update_artifact` · `verify_execute`.

Tập này là tập con của mười archetype trong bản brainstorming: bốn cái còn lại (`monitor`, `report`,
`decision_support`, `capture`) thuộc PM và Quality Intelligence, ngoài phạm vi pilot. Mở rộng tập này phải
qua CR vì lint và resolver đọc nó.

**`generate_artifact` và `update_artifact` là hai archetype "tạo deliverable"** — chúng kích hoạt luật AIP ở §5.

## 6.3 `assets` — bind bằng `asset_id`, không bằng đường dẫn

Mọi phần tử trong `assets`, `aip.template` đều là `asset_id`. Không bao giờ là đường dẫn: đường dẫn đổi khi
pack tái tổ chức, còn `asset_id` thì không, và bản tailored của dự án nằm ở cây khác hẳn (§8).

## 6.4 `roles` và `common/roles.yml`

Role là **nhãn**, khai một chỗ duy nhất:

```yaml
# common/roles.yml
schema_version: 1
roles:
  dev:    {title: Developer,        responsibility: Tạo và cập nhật deliverable}
  leader: {title: Technical Leader, responsibility: Review kỹ thuật, duyệt hướng}
  brse:   {title: BrSE,             responsibility: Review nghiệp vụ và upstream}
  qa:     {title: QA / PQA,         responsibility: Kiểm quy trình, bằng chứng, chất lượng}
```

Mọi role xuất hiện trong `roles` hay `human_gate.checker` của bất kỳ task nào phải có trong file này
(lint `task_role_unknown`). Pack không khai role nào thì `common/roles.yml` được phép vắng — nhưng lúc đó
task cũng không được khai `roles`/`human_gate.checker`.

## 6.5 `human_gate`

`required: true` nghĩa là output của task **không** được chuyển sang bước sau khi chưa có người kiểm
(quyết định D026 của pilot). `checker` phải là một role, không phải một asset. Asset `reference` không được
dùng làm căn cứ gate — nó không mang thẩm quyền.

---

# 7. Skills & Install Mapping — skill của pack và cách cài

## 7.1 Hình dạng

```
areas/DD/skills/<skill-name>/SKILL.md
```

`<skill-name>` là tên thư mục **và** là `name` trong frontmatter của `SKILL.md`. `SKILL.md` mang **cả hai**
loại frontmatter: trường của Claude Code (`name`, `description`) và trường asset của pack (§3):

```yaml
---
name: vti-dd-self-check
description: >
  Chạy self-check DD theo checklist chuẩn VTI trước khi bàn giao cho Leader review. …
artifact_type: standard_asset
asset_id: DD-SKL-dd-self-check
pack_id: vti_standard_pack
area: DD
kind: skill
title: DD Self-check Skill
classification: default
owner: QA Team
status: active
tailoring_note: >
  Dự án đổi được danh mục kiểm; giữ nguyên phần ghi bằng chứng.
---
```

`description` là **tín hiệu duy nhất** để AI chọn skill (thân skill chỉ được đọc sau khi đã chọn), nên nó
phải trả lời *làm gì* và *khi nào dùng*, có cụm kích hoạt tiếng Việt lẫn tiếng Anh. Quy ước đầy đủ:
`guidelines/SKILL_AUTHORING_CONVENTIONS.md`.

## 7.2 Cài

`install_standard_pack.py` chép `areas/<A>/skills/<name>/` sang `<target>/.claude/skills/<name>/`.

- Trùng `name` với một skill đã có trong dự án → **dừng, hỏi người**. Không đè im lặng: skill trùng tên là
  hai năng lực khác nhau tranh cùng một trigger, và bên thua biến mất không dấu vết.
- Gỡ pack không tự xoá skill đã cài; đó là quyết định của dự án.

## 7.3 `skills[]` trong task catalog

Phần tử là **một trong hai**: `asset_id` của một skill trong pack (dạng `<AREA>-SKL-<slug>`), hoặc **tên**
một skill AIWS có thật (ví dụ `aiws-runtime-review-checklist`). Resolver in kèm nguồn (`pack` hay `aiws`) để
người đọc biết skill đó đến từ đâu. Không phân giải được → lint `task_skill_unknown`.

---

# 8. Ranh giới pack ↔ bản tailored của dự án

## 8.1 Hai cây, hai chủ

| Đường dẫn trong dự án | Chủ | Ai ghi | Nâng cấp |
|---|---|---|---|
| `.ai-work/standard_pack/` | **pack** | `install_standard_pack.py` | Bị thay toàn bộ mỗi lần cài/nâng cấp |
| `.ai-work/project_process/` | **dự án** | Người của dự án (sau này có skill tailoring) | Không bao giờ bị tool của pack chạm vào |

Sửa trực tiếp trong `.ai-work/standard_pack/` là mất trắng ở lần nâng cấp kế tiếp. Đó là lý do tồn tại của
cây thứ hai, và là lý do provenance ở §8.2 phải nằm trong chính file tailored.

## 8.2 Header provenance của một bản tailored

Bản sao trong `.ai-work/project_process/` giữ nguyên frontmatter của asset gốc, thêm:

```yaml
tailored_from: DD-CHK-dd-review           # BẮT BUỘC — asset_id gốc
tailored_from_pack: vti_standard_pack@0.1.0   # BẮT BUỘC — pack_id@pack_version lúc chép
tailored_from_sha256: <sha256 file gốc>   # BẮT BUỘC — để phát hiện gốc đã đổi
tailored_at: 2026-09-10                   # BẮT BUỘC
deviation_ref: <CR/Approved Deviation>    # BẮT BUỘC khi asset gốc là mandatory
```

`tailored_from_sha256` là thứ cho phép trả lời "bản gốc đã đổi sau khi mình chép chưa" mà không cần giữ bản
sao thứ hai. Đây là **drift signal**, không phải khoá: pack đổi không tự làm bản tailored sai.

## 8.3 Thứ tự ưu tiên lúc chạy

Resolver trả bản **của dự án** khi có, ngược lại trả bản của pack, và luôn in nguồn:

```
project > pack
```

Đúng thứ tự SoT của pilot (D021): tài sản đã tailoring của dự án là thứ đang áp dụng; pack là mặc định.

## 8.4 Override task catalog

`.ai-work/project_process/task_catalog.override.yml`, cấu trúc **phẳng** (một tầng theo `task_id`):

```yaml
schema_version: 1
tasks:
  DD-REVIEW:
    enabled: false                       # bỏ task khỏi quy trình dự án
  DD-CREATE:
    assets:
      templates: [DD-TPL-dd-customer]    # THAY danh sách (không merge)
      checklists: +[PRJ-CHK-security]    # THÊM vào danh sách (tiền tố +)
    human_gate: {required: true, checker: brse}
```

Chỉ hai phép: **thay** (giá trị trần) và **thêm** (tiền tố `+` trước danh sách). Không merge sâu — merge sâu
làm người đọc không đoán được kết quả, mà kết quả ở đây là thứ quyết định ai phải review cái gì.

**Asset do dự án tự thêm** (ví dụ `PRJ-CHK-security` ở trên) nằm trong `.ai-work/project_process/`, mang tiền
tố riêng của dự án và **không** chịu luật `asset_id` ở §3.1 — `lint_standard_pack.py` chỉ lint pack, không lint
cây của dự án. Resolver phân giải được chúng vì override khai tường minh; nó in nguồn `project` cho những
asset đó.

---

# 9. Ba lớp version

| Lớp | Nguồn sự thật | Đổi khi |
|---|---|---|
| **AIWS** | `product/aiws_version.md` → bản cài | Cắt release AIWS |
| **Pack** | `pack.yml > pack_version` → `PACK_VERSION.md` trong package | Chủ pack phát hành bản mới |
| **Pin của dự án** | `.ai-work/project_profile.yml`, khối `AIWS:BEGIN`, khoá `standard_pack` | Cài hoặc nâng cấp pack |

```yaml
# .ai-work/project_profile.yml — trong khối AIWS:BEGIN
standard_pack:
  id: vti_standard_pack
  version: 0.1.0
```

## 9.1 Không tự nâng cấp

Nâng cấp pack luôn là hành động tường minh của người (D013). Không có đường nào để một bản cài tự kéo pack
mới về. Lớp version của **bản tailored** chưa được pin ở MVP này — ghi nhận ở §13.2.

## 9.2 Tương thích ngược

Dự án đang chạy không bị buộc nâng cấp. `pack_version` theo semver: đổi `asset_id`, bỏ task, hoặc đổi
`classification` sang `mandatory` là **major**.

## 9.3 Guard lúc cài

`install_standard_pack.py` từ chối (mã ≠ 0, không ghi gì) khi: dự án không có `.ai-work/`, hoặc bản AIWS của
dự án thấp hơn `aiws_min_version`. Từ chối *trước* khi chép byte nào — cài dở dang tệ hơn không cài.

---

# 10. Ngoại lệ rule 8 cho `product/standard_pack/`

Rule 8 của repo AIWS đòi mọi thay đổi tài liệu canonical trong `product/` phải có CR được
AIWS-Product-Owner duyệt. `product/standard_pack/` là **ngoại lệ tường minh**:

- Nội dung dưới `product/standard_pack/` là **pack-owned**. Nó vào repo bằng đúng một đường:
  `pull_standard_pack.py`, và đường đó ghi `PACK_SOURCE.md` (nguồn, commit, thời điểm, `pack_id`, version).
  Không cần CR AIWS cho từng lần pull.
- **Vẫn cần CR** cho: chính spec này, mọi tool đọc/ghi pack, schema, mã lint, và mọi thay đổi làm đổi
  *hợp đồng*. Nói gọn: hình dạng đi qua CR, nội dung thì không.
- `pull_standard_pack.py` **chạy lint trước khi ghi** và từ chối khi lint đỏ. Đó là thứ thay cho vòng duyệt CR:
  không có người gác thì phải có máy gác.
- Ngoại lệ này không nới bất kỳ rule nào khác. Rule 9 (không tìm ngoài project root) và rule 2 (không đọc
  binary PDF/DOCX) vẫn áp nguyên.

---

# 11. Lint — `lint_standard_pack.py`

Một lệnh: `py .ai-work/tooling/lint_standard_pack.py --pack <dir> [--format text|json]`.
`rc=0` khi sạch, `rc=2` khi có bất kỳ error nào. Mọi mã dưới đây là **error**.

| Mã | Phát hiện khi | Thông điệp phải nêu |
|---|---|---|
| `pack_yml_missing_key` | `pack.yml` vắng, không parse được, hoặc thiếu một khoá bắt buộc của §2.1 | tên khoá thiếu |
| `asset_frontmatter_missing` | File asset không có frontmatter, hoặc thiếu một trường bắt buộc của §3, hoặc `area`/`kind` lệch đường dẫn | đường dẫn + trường thiếu/lệch |
| `asset_id_dup` | Hai asset cùng `asset_id` | `asset_id` + hai đường dẫn |
| `task_asset_unknown` | `assets.*` hoặc `aip.template` trỏ tới `asset_id` không tồn tại trong pack | `task_id` + `asset_id` |
| `task_asset_kind_mismatch` | `asset_id` tồn tại nhưng sai kind cho vị trí bind (ví dụ một `guideline` nằm trong `assets.templates`) | `task_id` + kind mong đợi và kind thật |
| `aip_template_kind` | `aip.template` trỏ tới asset không phải kind `aip_template` | `task_id` + kind thật |
| `mandatory_no_tailoring_note` | Asset `classification: mandatory` thiếu `tailoring_note` (hoặc chỉ có khoảng trắng) | đường dẫn |
| `aiws_min_version_exceeds` | `aiws_min_version` cao hơn bản AIWS đang chạy lint | hai version |
| `deliverable_task_no_aip` | Task `generate_artifact`/`update_artifact` có `aip.mode: none`, hoặc thiếu `aip.template` | `task_id` + archetype |
| `task_skill_unknown` | Phần tử `skills[]` không phải asset skill của pack và cũng không phải skill AIWS có thật | `task_id` + giá trị |
| `task_role_unknown` | Role trong `roles` hoặc `human_gate.checker` không có trong `common/roles.yml` | `task_id` + role |

**Hai luật cho chính lint:**

1. Lint kiểm **hợp đồng**, không kiểm **nội dung**. Nó không bao giờ phán một checklist thiếu mục hay một
   process viết sai — đó là việc của chủ pack.
2. Mọi mã đều nêu được **chỗ sửa**. Một finding không chỉ ra file hoặc `task_id` là một finding hỏng.

## 11.1 Chỗ khác trong AIWS phải biết pack tồn tại

`lint_all.py` chạy trên toàn cây. Nếu nó quét `product/standard_pack/**/*.md` bằng luật của tài liệu canonical
AIWS (frontmatter, liên kết), asset của pack sẽ đỏ oan — chúng theo §3, không theo khuôn canonical. Điểm này
**chưa đo được** cho tới khi pack thật tồn tại trong cây; xem §13.1.

---

# 12. Wiki projection

Mỗi asset sinh một Wiki Source Meta để dự án tra cứu được ngay sau khi cài:

- `source_id`: `SRC-STDPACK-<asset_id>`
- `source_type` / `profile_id`: `standard_asset`
- `artifact_locator`: `.ai-work/standard_pack/<đường dẫn tương đối trong pack>`
- Nhóm meta: `.ai-work/wiki_sources/aiws_meta/standard_pack/` — cùng namespace `aiws` với methodology,
  wiki_guidelines và preset_knowledge, tách khỏi index của chính dự án.

Meta được sinh lúc **đóng gói** và chép vào dự án lúc **cài**, rồi index được dựng lại tại chỗ — cùng đường
đi mà preset wiki của AIWS đang dùng.

---

# 13. Open points

Hai nhóm. Điều chung cho cả hai: không mục nào dưới đây là một quyết định, và mục nào đổi số mã lint
hay đổi điều kiện phát của một mã đều là **đổi hợp đồng ⇒ phải qua CR** (§10). Chủ pack và/hoặc
AIWS-Product-Owner chốt.

## 13.1 Mở từ lúc soạn spec

1. **`lint_all` với `product/standard_pack/`** — chưa đo được cho tới khi có pack thật trong cây (§11.1).
   Nếu đỏ: hoặc lint học được rằng pack là vùng riêng (cần CR bổ sung), hoặc pack sửa cho hợp. Không tự
   miễn trừ.
2. **Pin version cho bản tailored của dự án** — lớp thứ ba của §9 hiện chỉ pin pack, chưa pin bản tailored.
   Chờ tới khi skill tailoring tồn tại.
3. **Cảnh báo "có pack mới hơn"** khi nâng cấp AIWS — nằm ngoài MVP này (D013 mở rộng).
4. **Nhiều pack cùng lúc** — `pack_id` đã có mặt trong mọi khoá để sau này mở được, nhưng cài hai pack cùng
   lúc chưa được định nghĩa (`asset_id` trùng giữa hai pack, ai thắng).
5. **`criteria_for` (§4.3)** — nếu chủ pack muốn một kind riêng cho tiêu chí chất lượng thì đó là một CR đổi
   §3.2, không phải một quyết định lúc soạn nội dung.
6. **Role khi tài liệu QMS không khai** — `common/roles.yml` bắt buộc khi có task khai role; tài liệu nguồn
   không nói ai làm gì thì để trống và ghi vào `CONVERSION_LOG.md`, không suy đoán.

## 13.2 Phát hiện lúc thực thi (mission `vti-standard-pack`, T23)

Gộp từ `SPEC_OPEN_POINTS_from_execution.md` của mission lúc apply CR-AIWS-2026-09-001; PO đã thấy danh
sách này ở gate duyệt CR. Bản cài đầu tiên của `.ai-work/tooling/lint_standard_pack.py` giữ nguyên
**11 mã** của §11 — không mã thứ 12 nào được thêm để đóng một trong những điểm dưới đây.

### OP-1 — §5 và §11 bất đồng về điều kiện phát `deliverable_task_no_aip`

- **§5** (câu mệnh lệnh): task `generate_artifact` / `update_artifact` **phải** bind `aip.template`
  **với `aip.mode: mandatory`**.
- **§11** (dòng tóm tắt trong bảng): phát khi task đó có `aip.mode: none`, **hoặc** thiếu `aip.template`.

Một input tách được hai cách đọc: task `generate_artifact` có `aip.mode: recommended` **kèm** `template`
hợp lệ. Theo §5 → đỏ. Theo dòng §11 → xanh (mode không phải `none`, template có mặt).

- **Bản cài hiện theo §5-strict** (`mode != "mandatory" or not template`), tức là **superset** của dòng §11.
- **Câu hỏi cho chủ pack/PO:** sửa dòng §11 cho khớp §5 (`mode` khác `mandatory` hoặc thiếu `template`),
  hay nới lint về đúng chữ §11? Hai lựa chọn cho kết quả khác nhau trên pack thật, không phải chuyện văn phong.
- **Ghi chú:** đây đúng là stop-condition "spec mơ hồ về một rule lint" mà WBS đã khai — nên nó nằm ở đây
  chứ không được tự chốt trong code.

### OP-2 — `asset_frontmatter_missing` gánh nhiều điều kiện hơn §11 mô tả

- §11 mô tả **ba** điều kiện: không có frontmatter · thiếu một trường bắt buộc của §3 · `area`/`kind` lệch
  đường dẫn.
- Bản cài phát mã này ở **13 chỗ** (đo bằng đếm call-site): thêm `artifact_type` sai hằng, `kind` ngoài bảy
  kind, `area` không nằm trong `areas` của `pack.yml`, `pack_id` lệch `pack.yml`, `classification` ngoài §4,
  `status` ngoài §3, `asset_id` sai khuôn `<AREA>-<KIND3>-<slug>`, `asset_id` mang area khác trường `area`,
  `asset_id` mang KIND3 khác trường `kind`.
- Mọi điều kiện thêm đều suy được từ §3/§3.1/§3.2/§4, nhưng tên mã thì nói "missing" trong khi phần lớn là
  "sai giá trị".
- **Câu hỏi:** (a) giữ nguyên và sửa dòng §11 cho liệt kê đủ; hay (b) tách một mã `asset_field_invalid`
  riêng cho nhóm sai-giá-trị (⇒ mã thứ 12, đổi hợp đồng, phải qua CR).

### OP-3 — Ba mã còn thiếu so với thứ spec đòi ở chỗ khác

Cả ba đều là **mã mới ⇒ CR**, không làm trong T23:

1. **`task_archetype_unknown`** — §6.2 định nghĩa đúng sáu archetype, và lint đã có sẵn hằng `ARCHETYPES`
   liệt kê đủ sáu — nhưng **hằng đó không được dùng ở bất kỳ check nào** (đo: chỉ `DELIVERABLE_ARCHETYPES`
   có call-site).
   Hệ quả đo được trên code: một typo (`generate_artefact`) làm task rơi khỏi `DELIVERABLE_ARCHETYPES`,
   nên gate D024 (`deliverable_task_no_aip`) **tắt không tiếng động** — pack mất một luật bắt buộc mà lint
   vẫn rc=0.
2. **`task_id_dup`** — §6.1 đòi `task_id` duy nhất toàn pack; `asset_id_dup` đã có mã tương ứng còn `task_id`
   thì không, trong khi resolver / `downstream` / override đều khoá theo `task_id`.
3. **`area_missing_task_catalog`** — §2 nói area có tài liệu phải có `task_catalog.yml` (và `process.md`).
   Hiện `check_task_catalogs` `continue` im lặng khi thiếu file, viện lẽ "area rỗng là hợp lệ" — không phân
   biệt được *rỗng hợp lệ* với *thiếu file*.

### OP-4 — `task_catalog.yml` không parse được ⇒ hiện `continue` im lặng

`check_task_catalogs` bắt `YamlSubsetError`/`OSError` rồi `continue`; `tasks` không phải list cũng `continue`.
Một pack có `task_catalog.yml` hỏng vì thế được báo là **sạch (rc=0)** — trong khi §10 giao cho chính lint này
vai người gác **duy nhất** của `product/standard_pack/` (`pull_standard_pack.py` từ chối khi lint đỏ).

Cùng họ với nó là ba hình dạng YAML mà parser-subset đọc sai **im lặng** (chưa đo trên pack thật, đo trên
code): plain multi-line scalar làm `_parse_map` bỏ phần còn lại của tài liệu; thụt bằng TAB (`_ind` chỉ đếm
space); và mọi lỗi cú pháp không thành exception.

- **Câu hỏi:** báo dưới mã `pack_yml_missing_key` (sai tên, vì không phải `pack.yml`) hay mở một mã
  `task_catalog_unparseable` (⇒ mã thứ 12, CR)? Trước khi T6/T11 tiêu thụ tool này, im lặng ở đây là rủi ro
  lớn nhất còn lại của lint.

### OP-5 — Rule "mọi file asset phải có `artifact_type: standard_asset`" cần được nói ở đâu và cưỡng chế ở đâu

Advisor của nhóm task metas đo được: một asset khai sai `artifact_type` **biến mất khỏi wiki projection**
(§12) trong khi build vẫn rc=0 — mất mát im lặng, phát hiện được chỉ khi có người đếm meta.
Lint hiện có kiểm hằng này (dưới `asset_frontmatter_missing`, xem OP-2), nhưng §12 không nói rằng projection
lọc theo `artifact_type`, và builder không kiểm.

- **Câu hỏi:** (a) §12 nói rõ projection lọc theo `artifact_type: standard_asset`; và (b) builder/packager có
  phải tự kiểm (đếm asset vs đếm meta sinh ra, lệch thì đỏ) hay dựa hoàn toàn vào lint chạy trước?

### Cái gì KHÔNG nằm trong danh sách này

- Defect đã sửa trong T23: `detect_aiws_version` đọc tier-1 `.ai-work/install_templates/VERSION` bằng
  `split_frontmatter()` (khớp `compose_aiws_rules.py:resolve_version`). Đó là lỗi cài đặt so với §9.3, không
  phải mơ hồ của spec — nên nó được vá, không được hỏi.
- Ba mục advisor xếp là chấp nhận được ở MVP: `reference` bind vào `human_gate` (§6.5 hiện không có slot
  asset — lỗi diễn đạt hơn là lỗi lint), tên SKILL vs tên thư mục (nên do install tool gác), và
  "areas khai trong `pack.yml` mà không có trên đĩa" (chiều ngược lại đã bị bắt).

---

# 14. Quan hệ

- `AIWS_Change_Request_Spec_MVP` — spec này và mọi tool của nó đi qua CR (§10).
- `SOP_DevelopmentTasks` (Truth của dự án) — gate D0 "AIP-first" là lý do luật §5 tồn tại.
- `AIP_Detail_Spec_MVP` — khuôn AIP mà `aip_templates/` của pack phải hợp.
- `SKILL_AUTHORING_CONVENTIONS` — quy ước `SKILL.md` mà §7 áp dụng.
- `Task_Lens_Spec_MVP` — Task Lens là gợi ý lúc tra cứu, **không** phải task catalog; hai thứ không thay nhau.
- `Knowledge_Object_Model_Spec_MVP` — profile/`source_type` của wiki projection ở §12.
