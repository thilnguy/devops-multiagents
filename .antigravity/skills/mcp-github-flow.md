# SKILL: GitHub Managed Workflow
**Context:** Sử dụng khi cần tương tác với Repository, Pull Request hoặc Issues.

**Quy trình thực hiện:**
1. **Kiểm tra:** Gọi tool `get_repository` để xác nhận trạng thái branch hiện tại.
2. **Thực thi:** - Nếu sửa bug: Dùng `create_issue` để track trước khi code.
   - Sau khi code xong: Dùng `create_branch` -> `push_files` -> `create_pull_request`.
3. **Tiêu chuẩn PR:** Nội dung PR phải bao gồm tóm tắt các file đã sửa và @mention các Persona liên quan.