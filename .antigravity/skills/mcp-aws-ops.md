# SKILL: AWS Infrastructure Sync
**Context:** Sử dụng khi @Infra-Bot cần xác thực hạ tầng thực tế.

**Quy trình thực hiện:**
1. **Discovery:** Gọi tool `list_instances` hoặc `describe_log_streams` để xem trạng thái vận hành.
2. **Comparison:** Đối chiếu thông số từ MCP trả về với các file trong thư mục `infra/terraform/`.
3. **Action:** Nếu có sự sai lệch (Drift), yêu cầu người dùng xác nhận trước khi cập nhật mã IaC.