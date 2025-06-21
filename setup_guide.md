# 🚀 Hướng dẫn tạo ứng dụng PDF to Excel Converter

## 📋 Bước 1: Chuẩn bị môi trường

### Cài đặt Python (nếu chưa có)

1. Tải Python từ: <https://www.python.org/downloads/>
2. ✅ **Quan trọng**: Tick "Add Python to PATH" khi cài đặt
3. Kiểm tra: mở Command Prompt, gõ `python --version`

### Cài đặt Tesseract OCR

1. Tải từ: <https://github.com/UB-Mannheim/tesseract/wiki/>
2. Cài đặt với ngôn ngữ Vietnamese
3. Thêm Tesseract vào PATH hoặc đặt trong code:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Cài đặt Poppler (cho pdf2image)

1. Tải bản build Poppler cho Windows từ (chọn bản mới nhất, ví dụ `poppler-24.08.0_x86_64`): <https://github.com/oschwartz10612/poppler-windows/releases>
2. Giải nén file tải về vào một vị trí cố định trên máy tính của bạn (ví dụ: `C:\poppler-24.08.0`).
3. Thêm đường dẫn đến thư mục `bin` bên trong thư mục Poppler vừa giải nén vào biến môi trường PATH (ví dụ: `C:\poppler-24.08.0\Library\bin`).
   Hoặc, bạn có thể chỉ định đường dẫn đến thư mục `bin` của Poppler trực tiếp trong ứng dụng nếu giao diện người dùng hỗ trợ (xem `distribution/README.txt` để biết thêm chi tiết nếu ứng dụng có tính năng này).

## 📂 Bước 2: Tạo dự án

Tạo thư mục dự án. Cấu trúc thư mục dự kiến sẽ như sau:

``` text
pdf_converter/
├── pdf_converter_app/      # Main application package
│   ├── __init__.py
│   ├── gui.py
│   ├── excel_exporter.py
│   ├── pdf_processor_overview.md # Tài liệu mô tả pdf_processor.py (source code không public)
│   └── utils.py            # (Có thể có hoặc không, tùy thuộc vào việc bạn có tạo file này không)
├── pdf_excel_gui.py        # Main script (entry point)
├── build_script.py         # Script to build executable
├── requirements.txt        # Python dependencies
├── setup_guide.md          # This guide
├── workflow.md             # Mô tả luồng hoạt động của dự án
└── icon.ico                # (Optional, if generated/present by build_script.py)
```

Mã nguồn chính của ứng dụng được tổ chức trong thư mục `pdf_converter_app`. File `pdf_excel_gui.py` là điểm khởi chạy chính.
**Lưu ý quan trọng:** File `pdf_converter_app/pdf_processor.py` (chứa logic xử lý PDF cốt lõi) sẽ không được đưa vào repository public này để bảo vệ một số chi tiết triển khai. Thay vào đó, file `pdf_converter_app/pdf_processor_overview.md` sẽ cung cấp một tài liệu mô tả tổng quan về chức năng và cách hoạt động của thành phần này. Khi build ứng dụng từ source, bạn cần đảm bảo có file `pdf_processor.py` với nội dung tương ứng thì ứng dụng mới có thể hoạt động đầy đủ.

## ⚙️ Bước 3: Cài đặt thư viện

Mở Command Prompt trong thư mục dự án:

``` bash
# Cài đặt tất cả thư viện cần thiết
pip install -r requirements.txt

# Hoặc cài từng cái:
pip install pdfplumber pytesseract Pillow pandas pdf2image openpyxl pyinstaller
```

## 🧪 Bước 4: Test ứng dụng

``` bash
# Chạy thử ứng dụng
python pdf_excel_gui.py
```

Lệnh này sẽ khởi chạy giao diện đồ họa của ứng dụng. Đảm bảo bạn đang ở trong thư mục gốc `pdf_converter` khi chạy lệnh này.

Nếu chạy được → OK, tiếp tục build executable

## 🔨 Bước 5: Build executable

```bash
# Chạy script build
python build_script.py
```

Script sẽ:

- ✅ Kiểm tra môi trường
- 🎨 Tạo icon
- 📦 Build file .exe
- 📋 Tạo gói phân phối hoàn chỉnh

## 📁 Bước 6: Kết quả

Sau khi build thành công:

``` text
distribution/
├── PDF_to_Excel_Converter.exe    # File chính
├── README.txt                    # Hướng dẫn cho user
└── run.bat                       # Shortcut chạy nhanh
```

## 🚀 Tính năng đã cải tiến

### ⚡ Xử lý song song

- Có thể xử lý 4-8 file PDF cùng lúc
- Tùy chỉnh số luồng theo cấu hình máy
- Thanh progress và log real-time

### 💾 Tối ưu bộ nhớ

- Tự động giải phóng RAM sau mỗi file
- Resize ảnh lớn để tiết kiệm bộ nhớ
- Xử lý từng file thay vì load tất cả

### 🎯 Dễ sử dụng

- GUI thân thiện, không cần kiến thức kỹ thuật
- Drag & drop files (có thể thêm)
- Tự động detect và xử lý PDF ảnh

## 🐛 Troubleshooting

### Lỗi Tesseract

```python
# Thêm vào đầu file pdf_excel_gui.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Lỗi pdf2image

- Đảm bảo Poppler đã cài đặt
- Hoặc copy poppler binary vào thư mục dự án

### File .exe bị antivirus chặn

- Bình thường với PyInstaller
- Thêm exception trong antivirus
- Hoặc upload lên VirusTotal để scan

### Giảm size file .exe

```bash
# Build với UPX compression (rủi ro cao hơn)
pyinstaller --onefile --upx-dir=upx pdf_excel_gui.py
```

## 📊 Hiệu năng

**Máy cấu hình yếu** (4GB RAM, Core i3):

- 1-2 luồng xử lý
- ~30-60s/file PDF (tùy size)
- OCR chậm nhưng ổn định

**Máy cấu hình tốt** (8GB+ RAM, Core i5+):

- 4-8 luồng xử lý
- ~10-30s/file PDF
- Xử lý song song hiệu quả

## 🎁 Bonus features có thể thêm

1. **Drag & Drop**: Kéo thả file vào GUI
2. **Batch processing**: Xử lý cả thư mục
3. **Template customization**: Tùy chỉnh format Excel
4. **Progress notification**: Thông báo khi hoàn thành
5. **Auto-update**: Tự động cập nhật phiên bản mới

---

## 💡 Tips phân phối

1. **Tạo installer**: Dùng NSIS hoặc Inno Setup
2. **Digital signature**: Ký số để tránh cảnh báo
3. **Portable version**: Không cần cài đặt
4. **Cloud storage**: Upload lên Google Drive/Dropbox

---

## **Chúc bạn thành công! 🎉**
