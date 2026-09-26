# Upstream Requests — gửi vấn đề / đề xuất lên team AIWS

Thư mục này chứa **Improvement Request (IR)** mà dự án bạn muốn gửi cho team AIWS: bug của
tooling/skill AIWS, chỗ spec chưa rõ, hoặc đề xuất cải tiến.

**Không phải** nơi ghi thay đổi nội bộ của dự án bạn — cái đó ở `.ai-work/change_requests/`.

## Quy tắc quan trọng nhất: KHÔNG tự đặt id trong namespace của AIWS

Đặt tên file theo `IR-YYYY-MM-DD-<slug>.md`. **Tuyệt đối không** dùng `CR-AIWS-*` hay `AP-CR-*`.

Vì sao gắt: những id đó do AIWS cấp bằng công cụ quét toàn bộ cây CR của họ. Dự án bạn không nhìn
thấy cây đó, nên số bạn tự chọn gần như chắc chắn trùng. Đã xảy ra thật — một dự án downstream gửi
lên file tên `CR-AIWS-2026-07-058-...`, trùng đúng một CR đã applied bên AIWS từ trước, phải đánh số
lại lúc tiếp nhận. Một lần khác, **5/5** id do downstream tự đặt đều trùng.

Nếu dự án bạn cần id riêng cho hồ sơ nội bộ, dùng namespace của chính mình: `CR-<TÊN-DỰ-ÁN>-*`.

## Cách gửi

1. Copy `IR_TEMPLATE.md` thành `IR-<ngày>-<slug>.md` trong thư mục này.
2. Điền — **ưu tiên phần "Tái lập"**: team AIWS xác minh lại mọi claim trên repo của họ trước khi
   nhận, nên có sẵn lệnh + output sẽ tiết kiệm hẳn một vòng hỏi đáp.
3. Trước khi gửi, kiểm xem bản AIWS bạn đang dùng đã phải mới nhất chưa. Khá nhiều đề xuất downstream
   hoá ra đã được fix ở bản sau.
4. Gửi file cho team AIWS. Họ sẽ đưa vào hàng đợi tiếp nhận, cấp id chính thức nếu được duyệt, rồi
   link ngược lại file này.

## Sau khi gửi

Giữ nguyên file — đừng xoá. Khi AIWS cấp id chính thức, ghi id đó vào `mapped_to_cr` để hai bên truy
ngược được. File ở đây là bản ghi của **bạn** về việc đã đề xuất gì, ngày nào.
