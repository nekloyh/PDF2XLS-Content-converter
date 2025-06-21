import pandas as pd
import os
from datetime import datetime


def export_results(
    all_data, output_dir, combine_files, base_filename="conversion_result"
):
    """
    Xuất kết quả đã xử lý ra file(s) Excel, với mỗi dòng trong 'invoice_records'
    của dữ liệu đầu vào trở thành một hàng riêng biệt trong Excel.

    Args:
        all_data (list): Danh sách các dictionary, mỗi dict chứa dữ liệu từ một file PDF.
                         Expected keys for this specific use case: 'file_name', 'invoice_records'.
        output_dir (str): Thư mục để lưu file Excel.
        combine_files (bool): Nếu True, gộp tất cả các invoice_records từ tất cả các file vào một file Excel duy nhất.
                              Nếu False, tạo một file Excel riêng cho mỗi file PDF, mỗi file chứa các invoice_records của nó.
        base_filename (str): Tên file cơ sở cho file Excel kết hợp hoặc làm tiền tố.
    """
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            raise Exception(f"Không thể tạo thư mục output '{output_dir}': {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if combine_files:
        # Gộp tất cả các invoice_records từ tất cả các file thành 1 Excel
        combined_invoice_rows = []
        for data_item in all_data:
            if not data_item:
                continue

            invoice_records = data_item.get("invoice_records", [])
            for record in invoice_records:
                # Thêm tên file gốc vào mỗi record nếu cần để dễ truy xuất nguồn gốc
                record_with_filename = record.copy()
                record_with_filename["Original_File_Name"] = data_item.get(
                    "file_name", "N/A"
                )
                combined_invoice_rows.append(record_with_filename)

        if not combined_invoice_rows:
            print("Không có dữ liệu 'invoice_records' để xuất ra file Excel kết hợp.")
            return []

        df = pd.DataFrame(combined_invoice_rows)
        safe_base_filename = "".join(c if c.isalnum() else "_" for c in base_filename)
        output_filename = f"{safe_base_filename}_combined_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, output_filename)

        try:
            df.to_excel(output_path, index=False, engine="openpyxl")
            print(f"Đã xuất thành công file Excel kết hợp: {output_path}")
            return [output_path]
        except Exception as e:
            raise Exception(f"Lỗi khi xuất file Excel kết hợp '{output_path}': {e}")

    else:
        # Mỗi file PDF tạo 1 Excel riêng, chứa các invoice_records của nó
        output_paths = []
        for data_item in all_data:
            if not data_item:
                continue

            invoice_records = data_item.get("invoice_records", [])
            if not invoice_records:
                print(
                    f"Không có dữ liệu 'invoice_records' để xuất cho {data_item.get('file_name', 'N/A')}"
                )
                continue

            df = pd.DataFrame(invoice_records)

            original_file_name = data_item.get("file_name", "unknown_file")
            base_output_name = os.path.splitext(original_file_name)[0]
            safe_output_name = "".join(
                c if c.isalnum() else "_" for c in base_output_name
            )
            output_filename = f"{safe_output_name}_invoice_records_{timestamp}.xlsx"
            output_path = os.path.join(output_dir, output_filename)

            try:
                df.to_excel(output_path, index=False, engine="openpyxl")
                output_paths.append(output_path)
                print(
                    f"Đã xuất thành công file Excel riêng cho '{original_file_name}': {output_path}"
                )
            except Exception as e:
                print(f"Lỗi khi xuất file Excel cho '{original_file_name}': {e}")

        return output_paths
