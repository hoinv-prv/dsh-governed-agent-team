# Bảo mật — aiws-doc-convert-skill

Skill chuyển đổi tài liệu → Markdown cho AI. Hai engine: **xberg** (khuyến nghị) và
**docling** (thay thế). Người dùng chọn 1 lần, lưu tại `~/.aiws_doc_convert/engine.json`.

---

## Engine xberg (khuyến nghị)

**Thư viện:** `xberg` là lớp mỏng bọc `kreuzberg` (lõi Rust). Giấy phép **Elastic-2.0**
(source-available). Cho phép dùng và phân phối nội bộ; **không** được cung cấp dưới dạng
dịch vụ hosted cho bên thứ ba; giữ nguyên các thông báo giấy phép.

**Dữ liệu không rời khỏi máy.** Trích xuất lõi (text/tables/render trang) chạy hoàn toàn
cục bộ — không gọi mạng, **không** tải model ML, chạy offline. Cỡ cài đặt ~33 MB.

**Tính năng tùy chọn có thể ra ngoài mạng (mặc định TẮT):**
- OCR bằng LLM/VLM hoặc `StructuredExtractionConfig(llm=…)` — chỉ khi tự bật + có API key.
- Bước "enhancement" (tóm tắt + Mermaid) do **VLM = chính AI đang chạy skill** thực hiện —
  ảnh của các unit được AI đọc. Với tài liệu nhạy cảm/PII, cân nhắc trước khi bật, hoặc trỏ
  LLM về model nội bộ.

---

## Engine docling (thay thế)

Chỉ cài khi người dùng chọn docling. `docling` (IBM Research, giấy phép **MIT**) kéo theo
torch + model ML (~1 GB, tải lần đầu từ Hugging Face của IBM), sau đó chạy offline.
Xem CVE/bản vá trong tài liệu bảo mật của docling-extract khi engine này được bổ sung.

---

## Bản thân skill này

**Tổng thể: Rủi ro thấp, phù hợp dùng nội bộ.**

**Điểm tốt:**
- Không có network call trong pipeline xberg lõi.
- Không `shell=True`, không `eval()`/`exec()` trên nội dung file.
- Handler import thư viện nặng (win32com/pptx) **lazy** — thiếu Office chỉ tắt route đó,
  không làm sập dispatcher.
- COM (Excel/PowerPoint/Word) đóng file trong `finally` — không để process treo.
- Sheet dữ liệu lớn bị lấy mẫu (sampled) kèm cảnh báo ⚠️ + đường dẫn file gốc → không
  ngộ nhận dữ liệu đã đầy đủ.

**Rủi ro cần lưu ý:**
1. **COM có thể chạy macro** — mở file bằng Excel/PowerPoint/Word thật qua `win32com`.
   File `.xlsm`/macro độc hại có thể tự chạy. Chỉ dùng với file từ nguồn tin cậy.
2. **Đường dẫn output không giới hạn** — `<output_dir>` trỏ đâu cũng được. Chấp nhận cho
   tool nội bộ; thêm whitelist nếu tích hợp pipeline nhận input ngoài.
3. **draw.io CLI** (render .drawio → PNG) gọi ứng dụng ngoài; nếu không có CLI, chỉ tạo
   Mermaid (không render) — an toàn.

**Khuyến nghị:**

| Tình huống | Cần làm gì |
|---|---|
| File từ bên ngoài (email, upload) | Scan virus trước khi dùng route Office (COM) |
| Tài liệu nhạy cảm/PII | Giữ bước enhancement (VLM) tắt hoặc dùng model nội bộ |
| Pipeline tự động | Whitelist thư mục output |
| Dùng nội bộ với file của team | An toàn như hiện tại |
