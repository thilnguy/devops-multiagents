# SKILL: Live Documentation Fetching
**Mô tả:** Sử dụng khi cần dữ liệu thực tế ngoài Project hoặc cập nhật syntax mới nhất.

**Quy trình thực hiện:**
1. **Search:** Nếu chưa có URL, gọi `google-search` để tìm trang tài liệu chính thống.
2. **Fetch:** Gọi `fetch_url` để lấy nội dung Markdown từ trang đó.
3. **Analyze:** Trích xuất các đoạn code mẫu (examples) và áp dụng vào Project hiện tại.
4. **Cite:** Luôn ghi chú nguồn tài liệu đã tham khảo vào phần comment của code.