---
intake_id: IR-YYYY-MM-DD-<slug>          # = tên file (bỏ .md)
title: "<một dòng: triệu chứng hoặc đề xuất>"
origin: "external: <tên dự án của bạn>"
requester: "<tên/đội + email liên hệ>"
received_at: YYYY-MM-DD                  # ngày bạn gửi; AIWS có thể chỉnh khi tiếp nhận
intake_status: open                      # AIWS quản lý từ đây: open|staged|processed|promoted|rejected
disposition: under_consideration         # AIWS quản lý: under_consideration|promoted_to_cr|applied|rejected|idea_reference_only
mapped_to_cr: null                       # AIWS điền khi cấp id chính thức
mapped_to_cr_path: null
source_document: "<đường dẫn file này trong repo dự án bạn>"
aiws_version: "<bản AIWS đang dùng>"
triage_note: ""
---

# IR — <tiêu đề>

> Xoá các dòng hướng dẫn trong `<...>` khi điền xong.

## Bối cảnh
<Đang làm gì thì gặp? Bản AIWS nào? Đã upgrade lên bản mới nhất chưa?>

## Triệu chứng
<Chuyện gì xảy ra, và bạn kỳ vọng gì thay vì thế.>

## Tái lập  ← phần quan trọng nhất

```
<lệnh chính xác đã chạy>
<output thật, dán nguyên văn, đừng tóm tắt>
```

<File/dòng liên quan nếu biết. Nếu không tái lập được thì nói rõ — vẫn gửi được, chỉ là AIWS sẽ mất
thời gian hơn.>

## Phạm vi ảnh hưởng
<Chạm bao nhiêu file/case trong dự án bạn? Có workaround không?>

## Đề xuất hướng xử lý (không bắt buộc)
<Nếu bạn đã có ý tưởng. AIWS có thể chọn hướng khác — họ nhìn được cả các dự án downstream khác.>

## Những gì bạn đã tự kiểm
<Đã grep chưa? Đã thử bản mới chưa? Đã tìm trong release note chưa? Ghi cả những hướng đã loại trừ —
nó giúp AIWS không đi lại đường cụt.>
