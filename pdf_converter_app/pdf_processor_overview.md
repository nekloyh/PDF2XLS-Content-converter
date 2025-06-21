# Tổng quan về `pdf_processor.py` (Conceptual)

**Lưu ý quan trọng:** Mã nguồn thực tế của `pdf_processor.py` không được bao gồm trong repository public này nhằm bảo vệ một số chi tiết triển khai cụ thể. Tài liệu này cung cấp một cái nhìn tổng quan về mục đích, đầu vào, quá trình xử lý và đầu ra dự kiến của module này.

## 1. Mục đích chính

Module `pdf_processor.py` đóng vai trò trung tâm trong việc xử lý nội dung của từng file PDF. Chức năng cốt lõi của nó là đọc, phân tích và trích xuất thông tin hữu ích từ các tài liệu PDF, bao gồm cả văn bản thuần túy và dữ liệu dạng bảng. Module này được thiết kế để xử lý cả PDF gốc (native PDF) và PDF dạng ảnh (scanned PDF) thông qua việc tích hợp công nghệ Nhận dạng ký tự quang học (OCR).

## 2. Đầu vào (Inputs)

Hàm xử lý chính trong module này (thường được gọi là `process_single_file` hoặc tương tự) nhận các đầu vào sau:

- `pdf_path` (kiểu chuỗi): Đường dẫn đầy đủ đến file PDF cần xử lý.
- `use_ocr` (kiểu boolean): Một cờ chỉ định liệu có nên sử dụng OCR để xử lý file PDF hay không.
  - `True`: Áp dụng OCR, hữu ích cho các PDF dạng ảnh hoặc PDF có văn bản không thể chọn/copy trực tiếp.
  - `False`: Chỉ xử lý PDF dưới dạng native, cố gắng trích xuất văn bản và bảng biểu trực tiếp từ cấu trúc PDF.

## 3. Quá trình xử lý chính (Conceptual Overview)

Quá trình xử lý bên trong `pdf_processor.py` có thể được mô tả khái quát qua các bước sau:

1. **Mở và đọc PDF**:
   - Sử dụng thư viện như `pdfplumber` để mở file PDF.
   - Lặp qua từng trang của tài liệu PDF.

2. **Trích xuất văn bản và bảng (Không OCR)**:
    - Đối với mỗi trang, nếu `use_ocr` là `False`, module sẽ cố gắng trích xuất văn bản (`page.extract_text()`) và các bảng biểu (`page.extract_tables()`) bằng các chức năng gốc của `pdfplumber`.

3. **Xử lý OCR (Nếu `use_ocr` là `True`)**:
    - Nếu `use_ocr` là `True` hoặc nếu việc trích xuất trực tiếp không mang lại kết quả (ví dụ, PDF chỉ chứa ảnh), module sẽ tiến hành OCR:
        - Sử dụng thư viện `pdf2image` để chuyển đổi các trang PDF (hoặc toàn bộ file PDF) thành hình ảnh (ví dụ: định dạng PNG hoặc PPM).
        - Sử dụng thư viện `pytesseract` (giao diện Python cho Tesseract OCR Engine) để thực hiện nhận dạng ký tự quang học trên các hình ảnh đã tạo. Quá trình này sẽ chuyển đổi nội dung hình ảnh thành văn bản có thể đọc được bằng máy.
        - Ngôn ngữ cho OCR (ví dụ: 'vie' cho tiếng Việt) được cấu hình để đảm bảo độ chính xác cao nhất.

4. **Phân tích và cấu trúc dữ liệu**:
    - **Văn bản**: Văn bản trích xuất (dù từ OCR hay trích xuất trực tiếp) có thể trải qua các bước tiền xử lý như loại bỏ khoảng trắng thừa, sửa lỗi OCR phổ biến (nếu có thể), hoặc chuẩn hóa định dạng.
    - **Bảng biểu**: Dữ liệu bảng được trích xuất (thường ở dạng danh sách các danh sách - list of lists) có thể cần được làm sạch, chuẩn hóa, và cấu trúc lại để dễ dàng sử dụng hơn.
    - **Logic tùy chỉnh (ẩn)**: Đây là phần "bí mật" của module, có thể bao gồm:
        - Các biểu thức chính quy (regex) phức tạp để tìm kiếm và trích xuất các mẫu thông tin cụ thể từ văn bản (ví dụ: mã số, ngày tháng, tên, địa chỉ, các mục chi tiết trong hóa đơn, v.v.).
        - Các thuật toán để xác định ranh giới của các khối văn bản quan trọng hoặc để liên kết thông tin từ các phần khác nhau của tài liệu.
        - Logic để phân biệt giữa các loại bảng biểu khác nhau hoặc để xử lý các bảng có cấu trúc phức tạp, không đồng nhất.
        - Các quy tắc nghiệp vụ cụ thể để diễn giải dữ liệu đã trích xuất.

5. **Tổng hợp kết quả**:
    - Tất cả thông tin trích xuất và xử lý từ các trang (văn bản, bảng biểu, dữ liệu đã qua phân tích tùy chỉnh) được tổng hợp lại.

## 4. Đầu ra (Outputs)

Hàm xử lý chính của module (`process_single_file`) thường trả về một cấu trúc dữ liệu tổng hợp, ví dụ như một Python dictionary, chứa các thông tin sau:

- `filename` (kiểu chuỗi): Tên của file PDF gốc đã được xử lý.
- `text_data` (kiểu chuỗi hoặc danh sách chuỗi): Toàn bộ nội dung văn bản đã được trích xuất và làm sạch.
- `table_data` (thường là danh sách các đối tượng bảng, mỗi đối tượng bảng có thể là danh sách các hàng, và mỗi hàng là danh sách các ô): Dữ liệu từ các bảng biểu đã được trích xuất và cấu trúc lại.
- `custom_extracted_info` (kiểu dictionary hoặc object): Các thông tin cụ thể khác đã được trích xuất và phân tích theo logic tùy chỉnh (nếu có). Ví dụ: `{'invoice_number': 'INV123', 'total_amount': 5000.00}`.

Cấu trúc đầu ra này sau đó sẽ được sử dụng bởi các module khác (ví dụ: `excel_exporter.py`) để ghi dữ liệu ra file Excel hoặc phục vụ các mục đích khác.

---

Tài liệu này nhằm mục đích cung cấp sự hiểu biết cơ bản về vai trò và cách hoạt động của `pdf_processor.py` trong dự án, ngay cả khi mã nguồn chi tiết của nó không được công khai.
