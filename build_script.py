"""
Script để build executable từ PDF to Excel GUI
Chạy script này để tạo file .exe
"""

import subprocess
import shutil
from pathlib import Path


def build_executable():
    """Build executable với PyInstaller"""

    print("🚀 Bắt đầu build executable...")

    # Kiểm tra PyInstaller
    try:
        import PyInstaller

        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt!")
        print("Chạy: pip install pyinstaller")
        return False

    # Tạo thư mục build nếu chưa có
    build_dir = Path("build_output")
    build_dir.mkdir(exist_ok=True)

    # Các tham số PyInstaller
    pyinstaller_args = [
        "pyinstaller",
        "--onefile",  # Tạo 1 file exe duy nhất
        "--windowed",  # Không hiện console (GUI app)
        "--name=PDF_to_Excel_Converter",  # Tên file exe
        "--icon=icon.ico",  # Icon (tùy chọn)
        "--distpath=build_output",  # Thư mục output
        "--workpath=build_temp",  # Thư mục temp
        "--specpath=build_temp",  # Thư mục spec
        "--add-data=README.md;.",  # Thêm README
        "--hidden-import=pdfplumber",
        "--hidden-import=pytesseract",
        "--hidden-import=pdf2image",
        "--hidden-import=PIL",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=concurrent.futures",
        "--hidden-import=multiprocessing",
        # Added hidden imports for the new application modules
        "--hidden-import=pdf_converter_app.gui",
        "--hidden-import=pdf_converter_app.pdf_processor",
        "--hidden-import=pdf_converter_app.excel_exporter",
        # "--hidden-import=pdf_converter_app.utils", # utils.py is not used
        "--collect-all=pdfplumber",
        # "--collect-all=pytesseract", # Assuming Tesseract is installed by user and in PATH
        "--noupx",  # Không nén để tránh lỗi antivirus
        "pdf_excel_gui.py",
    ]

    # Loại bỏ icon nếu file không tồn tại
    if not Path("icon.ico").exists():
        pyinstaller_args = [
            arg for arg in pyinstaller_args if not arg.startswith("--icon")
        ]
        print("⚠️  Không tìm thấy icon.ico, bỏ qua icon")

    # Chạy PyInstaller
    try:
        print("🔨 Đang build executable...")
        result = subprocess.run(pyinstaller_args, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Build thành công!")

            # Kiểm tra file exe
            exe_path = build_dir / "PDF_to_Excel_Converter.exe"
            if exe_path.exists():
                exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"📁 File exe: {exe_path}")
                print(f"📏 Kích thước: {exe_size:.1f} MB")

                # Tạo thư mục phân phối
                dist_dir = Path("distribution")
                dist_dir.mkdir(exist_ok=True)

                # Copy exe và tạo gói phân phối
                shutil.copy2(exe_path, dist_dir)
                create_distribution_package(dist_dir)

                print(f"🎉 Hoàn thành! File exe tại: {dist_dir}")
                return True
            else:
                print("❌ Không tìm thấy file exe sau khi build")
                return False
        else:
            print("❌ Build thất bại!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Lỗi build: {e}")
        return False


def create_distribution_package(dist_dir):
    """Tạo gói phân phối hoàn chỉnh"""

    # Tạo README cho người dùng
    readme_content = """# PDF to Excel Converter

## Hướng dẫn sử dụng:

1. **Chạy ứng dụng**: Double-click vào file `PDF_to_Excel_Converter.exe`

2. **Chọn file PDF**: Nhấn "Chọn file PDF" để chọn các file cần xử lý

3. **Chọn thư mục lưu**: Chọn nơi lưu kết quả Excel

4. **Tùy chọn**:
   - ✅ OCR: Xử lý PDF dạng ảnh (chậm hơn)
   - ✅ Gộp file: Tạo 1 Excel chung cho tất cả PDF
   - 🔧 Số luồng: Số file xử lý cùng lúc (4 là tối ưu)

5. **Xử lý**: Nhấn "Bắt đầu xử lý" và chờ hoàn thành

## Yêu cầu hệ thống:
- Windows 10/11 (64-bit)
- RAM: Tối thiểu 4GB, khuyến nghị 8GB+
- Ổ cứng: 500MB trống (chưa bao gồm Tesseract và Poppler)

## YÊU CẦU CHO CHỨC NĂNG OCR (Xử lý PDF dạng ảnh):

Để sử dụng chức năng OCR (nhận dạng ký tự trên PDF dạng ảnh), bạn cần Tesseract OCR và Poppler. Có hai cách để ứng dụng tìm thấy chúng:

**Cách 1: Cài đặt và thêm vào PATH (Khuyến nghị cho sự tiện lợi)**
1.  **Tesseract OCR**:
    *   Tải và cài đặt Tesseract OCR từ trang chính thức của UB Mannheim (khuyến nghị): <https://github.com/UB-Mannheim/tesseract/wiki> (Tìm bản cài đặt cho Windows). Hoặc từ nguồn chính của Tesseract: <https://github.com/tesseract-ocr/tesseract> (có thể cần tự build hoặc tìm bản build sẵn).
    *   **QUAN TRỌNG**: Trong quá trình cài đặt, đảm bảo bạn đã chọn cài đặt gói ngôn ngữ "Vietnamese" (thường có tên `vie`).
    *   Thêm thư mục cài đặt Tesseract vào biến môi trường PATH của hệ thống (ví dụ: `C:\\Program Files\\Tesseract-OCR`).
2.  **Poppler**:
    *   Tải bản build Poppler cho Windows từ (chọn bản mới nhất, ví dụ `poppler-2x.xx.x_x86_64`): <https://github.com/oschwartz10612/poppler-windows/releases>
    *   Giải nén file tải về vào một vị trí cố định trên máy tính của bạn (ví dụ: `C:\\poppler`).
    *   Thêm đường dẫn đến thư mục `bin` (hoặc `Library\bin` tùy thuộc vào cấu trúc bản build Poppler bạn tải) bên trong thư mục Poppler vừa giải nén vào biến môi trường PATH (ví dụ: `C:\\poppler\\bin` hoặc `C:\\poppler\\Library\\bin`).

    **Kiểm tra PATH**: Sau khi cài đặt và cập nhật PATH, mở một Command Prompt *mới* và gõ `tesseract --version` rồi Enter, sau đó gõ `pdftoppm -h` rồi Enter (hoặc `pdfinfo -h` tùy theo file thực thi có trong thư mục `bin` của Poppler). Nếu cả hai lệnh đều chạy và hiển thị thông tin phiên bản/trợ giúp mà không báo lỗi "...is not recognized...", nghĩa là bạn đã cấu hình PATH thành công.

**Cách 2: Chỉ định đường dẫn trực tiếp trong ứng dụng (Nếu GUI hỗ trợ)**
*   Một số phiên bản của ứng dụng này có thể cho phép bạn chỉ định đường dẫn đến Tesseract và Poppler trực tiếp trong giao diện người dùng.
*   Nếu bạn không muốn thêm Tesseract và Poppler vào PATH hệ thống, hãy kiểm tra xem trong phần "Tùy chọn" hoặc "Cài đặt" của ứng dụng có các mục sau không:
    *   "Đường dẫn Tesseract (tesseract.exe)": Nếu có, nhấn "Browse..." và chọn đến file `tesseract.exe` trong thư mục cài đặt Tesseract của bạn.
    *   "Đường dẫn Poppler (thư mục bin)": Nếu có, nhấn "Browse..." và chọn đến thư mục chứa các file thực thi của Poppler (thường là thư mục `bin` hoặc `Library\bin`).
*   Nếu các đường dẫn này được cung cấp trong GUI, ứng dụng sẽ ưu tiên sử dụng chúng. Nếu để trống hoặc không có tùy chọn này trong GUI, ứng dụng sẽ cố gắng tìm Tesseract và Poppler trong PATH hệ thống.

## Lưu ý:
- File PDF càng lớn và phức tạp, thời gian xử lý càng lâu, đặc biệt khi bật OCR.
- Tính năng OCR yêu cầu Tesseract và Poppler được cấu hình đúng (qua PATH hoặc chỉ định trong ứng dụng).
- Bạn có thể xử lý nhiều file cùng lúc để tăng tốc độ làm việc.

## Hỗ trợ và khắc phục sự cố:
Nếu gặp lỗi, vui lòng kiểm tra:
1.  **Đối với lỗi OCR**: Đảm bảo Tesseract và Poppler đã được cài đặt đúng, ngôn ngữ tiếng Việt cho Tesseract đã được cài, và đường dẫn đã được thêm vào PATH chính xác HOẶC đã được chỉ định đúng trong ứng dụng.
2.  File PDF không bị lỗi hoặc không được bảo vệ bằng mật khẩu cấm trích xuất.
3.  Còn đủ dung lượng trống trên ổ cứng.
4.  Ứng dụng không bị chặn bởi phần mềm diệt virus.

---
Phiên bản: 1.0
Ngày build: """ + str(Path.cwd().stat().st_mtime)

    # Ghi README
    with open(dist_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Tạo file batch để chạy nhanh
    batch_content = """@echo off
echo Starting PDF to Excel Converter...
PDF_to_Excel_Converter.exe
pause"""

    with open(dist_dir / "run.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)

    print("📋 Đã tạo README.txt và run.bat")


def create_icon():
    """Tạo icon đơn giản cho app"""
    try:
        from PIL import Image, ImageDraw

        # Tạo icon 64x64
        img = Image.new("RGBA", (64, 64), (70 + 130 + 180 + 255))  # Steel blue
        draw = ImageDraw.Draw(img)

        # Vẽ biểu tượng PDF
        draw.rectangle(
            [10, 10, 54, 54], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255)
        )
        draw.text((18, 25), "PDF", fill=(255, 0, 0, 255))
        draw.text((18, 35), "->XLS", fill=(0, 128, 0, 255))

        # Lưu icon
        img.save("icon.ico", format="ICO")
        print("✓ Đã tạo icon.ico")
        return True

    except Exception as e:
        print(f"⚠️  Không thể tạo icon: {e}")
        return False


def main():
    """Hàm main"""
    print("=" * 50)
    print("📦 PDF to Excel Converter - Build Script")
    print("=" * 50)

    # Tạo icon
    create_icon()

    # Build executable
    success = build_executable()

    if success:
        print("\n🎉 BUILD THÀNH CÔNG!")
        print("\n📋 Các bước tiếp theo:")
        print("1. Kiểm tra thư mục 'distribution/'")
        print("2. Test file .exe trước khi phân phối")
        print("3. Có thể copy toàn bộ thư mục 'distribution' cho người khác")
        print("\n💡 Lưu ý: File exe có thể bị Windows Defender cảnh báo lần đầu")
    else:
        print("\n❌ BUILD THẤT BẠI!")
        print("Vui lòng kiểm tra lỗi ở trên và thử lại")

    input("\nNhấn Enter để thoát...")


if __name__ == "__main__":
    main()
