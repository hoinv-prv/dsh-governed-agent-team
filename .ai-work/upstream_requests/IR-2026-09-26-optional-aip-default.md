---
intake_id: IR-2026-09-26-optional-aip-default
title: "Allow downstream projects to make AIP use optional by default"
origin: "external: dsh-governed-agent-team"
requester: "hoinv"
received_at: 2026-09-26
intake_status: open
disposition: under_consideration
mapped_to_cr: null
mapped_to_cr_path: null
source_document: ".ai-work/change_requests/CR-DSH-GAT-2026-09-001-optional-aip-default.md"
aiws_version: "v1.2.2"
triage_note: "Project requests a configurable or project-overridable AIP default."
---

# IR — Allow downstream projects to make AIP use optional by default

## Bối cảnh

This repository upgraded to AI Work System MVP v1.2.2 on 2026-09-26. Its project owner wants to work directly by default and request an AIP only when it is needed.

## Triệu chứng

The installed core rule’s Execution policy requires an AIP before every non-trivial task. This prevents the project from adopting its owner’s intended lightweight default without locally changing a package-owned file.

## Tái lập

```
Read .ai-work/AIWS.md → “Trước khi thực hiện bất kỳ non-trivial task nào ... phải có AIP trước.”
Read .ai-work/truth/canonical/methodology/20_specs/AIWS_Change_Request_Spec_MVP.md §18
→ downstream projects must not directly apply changes to AIWS canonical documents/tools.
```

## Phạm vi ảnh hưởng

One downstream repository currently needs a project-level override. Other teams may also need a lightweight mode; this request does not claim a measured population count.

## Đề xuất hướng xử lý

Make the default AIP policy configurable at installation or explicitly permit a project-owned SOP override. The override should preserve separate CR and Truth approval gates.

## Những gì bạn đã tự kiểm

- Upgraded target from v1.2.1 to v1.2.2.
- Confirmed the local SOP and contract are empty.
- Confirmed that package canonical content requires upstream handling under `AIWS_Change_Request_Spec_MVP.md` §18.
