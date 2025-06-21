import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue
import os
from pathlib import Path
import multiprocessing
import time # For logging timestamp

# Relative imports for custom modules within the package
from . import pdf_processor
from . import excel_exporter

# It's good practice to import pytesseract here if setup_tesseract uses it.
import pytesseract 

class PDFToExcelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Excel Converter - Trích xuất dữ liệu PDF")
        self.root.geometry("850x700") # Slightly adjusted size for potentially more widgets/info
        self.root.resizable(True, True)
        
        self.result_queue = queue.Queue()
        self.is_processing = False
        self.selected_files = []

        # Variables for Tesseract and Poppler paths
        self.tesseract_path_var = tk.StringVar()
        self.poppler_path_var = tk.StringVar()
        
        self.create_widgets()
        self.setup_tesseract() # Check Tesseract status on startup
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        
        # Configure root and main_frame resizing behavior
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1) # Allow second column (where listbox and entry are) to expand
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF to Excel Converter (Modular)", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        # File selection area
        ttk.Label(main_frame, text="Chọn file(s) PDF:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.files_listbox = tk.Listbox(main_frame, height=7, width=60) # Increased height
        self.files_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W + tk.E), pady=5)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.files_listbox.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N + tk.S), pady=5)
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        # File selection buttons
        file_buttons_frame = ttk.Frame(main_frame)
        file_buttons_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        ttk.Button(file_buttons_frame, text="Chọn file PDF", 
                  command=self.select_files).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(file_buttons_frame, text="Xóa file đã chọn", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # Output folder selection
        ttk.Label(main_frame, text="Thư mục lưu kết quả:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W + tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1) # Make entry expand
        
        self.output_path_var = tk.StringVar(value=str(Path.home() / "Desktop" / "PDF_Exports"))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=60) # Increased width
        self.output_entry.grid(row=0, column=0, sticky=(tk.W + tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="Chọn thư mục", 
                  command=self.select_output_folder).grid(row=0, column=1)
        
        # Processing options
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn xử lý", padding="10")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W + tk.E), pady=15)
        
        self.use_ocr_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Sử dụng OCR cho PDF dạng ảnh (nếu cần)", 
                       variable=self.use_ocr_var).pack(anchor=tk.W)
        
        self.combine_files_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Gộp tất cả kết quả vào 1 file Excel duy nhất", 
                       variable=self.combine_files_var).pack(anchor=tk.W)
        
        # Thread count option
        thread_frame = ttk.Frame(options_frame)
        thread_frame.pack(anchor=tk.W, pady=(5,0))
        
        ttk.Label(thread_frame, text="Số file xử lý cùng lúc:").pack(side=tk.LEFT)
        # Default to a sensible number, e.g., half of CPUs, min 1, max 4 or based on CPU count
        default_threads = max(1, min(4, multiprocessing.cpu_count() // 2 if multiprocessing.cpu_count() > 1 else 1))
        self.thread_count_var = tk.IntVar(value=default_threads)
        thread_spinbox = ttk.Spinbox(thread_frame, from_=1, to=multiprocessing.cpu_count(), width=5, 
                                   textvariable=self.thread_count_var)
        thread_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(thread_frame, text=f"(Tối đa: {multiprocessing.cpu_count()})").pack(side=tk.LEFT)

        # Tesseract path
        tesseract_frame = ttk.Frame(options_frame)
        tesseract_frame.pack(anchor=tk.W, pady=(5,0), fill=tk.X)
        ttk.Label(tesseract_frame, text="Đường dẫn Tesseract (tesseract.exe):").pack(side=tk.LEFT)
        tesseract_entry = ttk.Entry(tesseract_frame, textvariable=self.tesseract_path_var, width=40)
        tesseract_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(tesseract_frame, text="Browse...", command=lambda: self.browse_file(self.tesseract_path_var, "tesseract.exe")).pack(side=tk.LEFT)

        # Poppler path
        poppler_frame = ttk.Frame(options_frame)
        poppler_frame.pack(anchor=tk.W, pady=(5,0), fill=tk.X)
        ttk.Label(poppler_frame, text="Đường dẫn Poppler (thư mục bin):").pack(side=tk.LEFT)
        poppler_entry = ttk.Entry(poppler_frame, textvariable=self.poppler_path_var, width=40)
        poppler_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(poppler_frame, text="Browse...", command=lambda: self.browse_directory(self.poppler_path_var)).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W + tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10))
        self.status_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Bắt đầu xử lý", 
                                        command=self.start_processing, style="Accent.TButton") # Added style
        self.process_button.grid(row=9, column=0, columnspan=3, pady=20)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Log xử lý", padding="5")
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W + tk.E + tk.N + tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1) # Allow log area to expand vertically
        
        self.log_text = tk.Text(log_frame, height=10, width=80, relief=tk.SOLID, borderwidth=1)
        self.log_text.grid(row=0, column=0, sticky=(tk.W + tk.E + tk.N + tk.S))
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N + tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        # Style configuration (optional, for a slightly more modern look)
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 12, "bold"), padding=5)
        # You can add more styles for other widgets too


    def setup_tesseract(self):
        """Kiểm tra Tesseract và log trạng thái."""
        try:
            # This is a lightweight check. pdf_processor will handle TesseractNotFound more directly.
            pytesseract.get_languages() 
            self.log_message("Tesseract: Đã phát hiện.", "INFO")
        except Exception as e: # More specific exception like TesseractNotFoundError could be caught
            self.log_message(f"Tesseract: Không tìm thấy hoặc lỗi cấu hình. OCR có thể không hoạt động. Chi tiết: {e}", "WARNING")
            # messagebox.showwarning("Tesseract Not Found", 
            #                        "Tesseract is not installed or not in your PATH. OCR functionality will be disabled.")
            
    def log_message(self, message, level="INFO"):
        """Thêm message vào log với timestamp và level."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp} {level}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks() # Ensure GUI updates

    def browse_file(self, path_var, file_description):
        """Mở dialog để chọn một file."""
        # For tesseract.exe, it's better to ask for the file directly.
        if file_description == "tesseract.exe":
            filepath = filedialog.askopenfilename(
                title=f"Chọn file {file_description}",
                filetypes=((f"{file_description} executable", "*.exe"), ("All files", "*.*"))
            )
        else: # Fallback or other file types
            filepath = filedialog.askopenfilename(title=f"Chọn file {file_description}")

        if filepath:
            path_var.set(filepath)
            self.log_message(f"{file_description} được đặt thành: {filepath}", "INFO")

    def browse_directory(self, path_var):
        """Mở dialog để chọn một thư mục."""
        dirpath = filedialog.askdirectory(title="Chọn thư mục")
        if dirpath:
            path_var.set(dirpath)
            self.log_message(f"Thư mục Poppler bin được đặt thành: {dirpath}", "INFO")
        
    def select_files(self):
        """Chọn file PDF và cập nhật listbox."""
        files = filedialog.askopenfilenames(
            title="Chọn file PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        new_files_count = 0
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
                new_files_count +=1
        
        if new_files_count > 0:
            self.log_message(f"Đã chọn thêm {new_files_count} file PDF.", "INFO")
        else:
            self.log_message("Không có file mới nào được thêm.", "INFO")
            
    def clear_files(self):
        """Xóa danh sách file đã chọn."""
        if not self.selected_files:
            self.log_message("Không có file nào để xóa.", "INFO")
            return
        self.selected_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.log_message("Đã xóa tất cả file khỏi danh sách.", "INFO")
        
    def select_output_folder(self):
        """Chọn thư mục output."""
        initial_dir = self.output_path_var.get() if os.path.exists(self.output_path_var.get()) else str(Path.home())
        folder = filedialog.askdirectory(title="Chọn thư mục lưu kết quả", initialdir=initial_dir)
        if folder:
            self.output_path_var.set(folder)
            self.log_message(f"Thư mục output được đặt thành: {folder}", "INFO")
            
    def start_processing(self):
        """Bắt đầu xử lý files trong một thread riêng."""
        if not self.selected_files:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 file PDF để xử lý.")
            return
            
        output_folder = self.output_path_var.get()
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
                self.log_message(f"Đã tạo thư mục output: {output_folder}", "INFO")
            except OSError as e:
                messagebox.showerror("Lỗi", f"Không thể tạo thư mục output: {e}")
                return
            
        if self.is_processing:
            messagebox.showwarning("Đang xử lý", "Quá trình xử lý khác đang chạy. Vui lòng đợi.")
            return

        self.is_processing = True
        self.process_button.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Đang chuẩn bị xử lý...")
        self.log_message("Bắt đầu quá trình xử lý...", "INFO")
        
        # Lấy các giá trị cấu hình từ GUI
        use_ocr = self.use_ocr_var.get()
        combine_results = self.combine_files_var.get()
        num_workers = self.thread_count_var.get()
        tesseract_custom_path = self.tesseract_path_var.get()
        poppler_custom_path = self.poppler_path_var.get()

        # Chạy xử lý trong thread riêng để không block GUI
        processing_thread = threading.Thread(
            target=self._process_files_thread, 
            args=(
                list(self.selected_files), 
                output_folder, 
                use_ocr, 
                combine_results, 
                num_workers,
                tesseract_custom_path,
                poppler_custom_path
            )
        )
        processing_thread.daemon = True #Để thread tự thoát khi chương trình chính đóng
        processing_thread.start()
        
        # Bắt đầu kiểm tra queue để cập nhật GUI
        self.check_processing_result()
        
    def _process_files_thread(self, files_to_process, output_dir, use_ocr, combine_results, num_workers, tesseract_custom_path, poppler_custom_path):
        """
        Hàm chạy trong thread để xử lý file.
        Sử dụng pdf_processor và excel_exporter.
        Truyền đường dẫn tùy chỉnh cho Tesseract và Poppler.
        """
        try:
            total_files = len(files_to_process)
            all_results_data = [] # Để lưu kết quả từ process_single_file
            processed_count = 0

            self.result_queue.put({
                'type': 'log', 'level': 'INFO',
                'value': f"Bắt đầu xử lý {total_files} file với tối đa {num_workers} worker(s)."
            })

            # Sử dụng concurrent.futures.ThreadPoolExecutor để quản lý luồng
            # Không cần import concurrent.futures ở đây vì nó không dùng trực tiếp trong GUI thread
            # mà là trong pdf_excel_gui.py (nếu giữ lại ThreadPoolExecutor)
            # Tuy nhiên, logic xử lý song song file đã được chuyển vào đây.
            # Chúng ta có thể dùng ThreadPoolExecutor ở đây hoặc xử lý tuần tự từng file
            # For simplicity in this refactoring step, let's process one by one if ThreadPool is complex.
            # OR, more correctly, use ThreadPoolExecutor as it was intended.
            # We need to import concurrent.futures if we use it here.
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                future_to_file = {}
                for pdf_path in files_to_process:
                    future = executor.submit(
                        pdf_processor.process_single_file, 
                        pdf_path, 
                        use_ocr,
                        tesseract_exe_path=tesseract_custom_path, # Thêm tham số
                        poppler_bin_path=poppler_custom_path     # Thêm tham số
                    )
                    future_to_file[future] = pdf_path
                
                for future in concurrent.futures.as_completed(future_to_file):
                    pdf_path = future_to_file[future]
                    try:
                        single_file_result = future.result()
                        if single_file_result:
                            all_results_data.append(single_file_result)
                            self.result_queue.put({
                                'type': 'log', 'level': 'SUCCESS',
                                'value': f"✓ Hoàn thành xử lý: {os.path.basename(pdf_path)}"
                            })
                        else:
                            self.result_queue.put({
                                'type': 'log', 'level': 'WARNING',
                                'value': f"✗ Không có dữ liệu trích xuất từ: {os.path.basename(pdf_path)}"
                            })
                    except Exception as e:
                        self.result_queue.put({
                            'type': 'log', 'level': 'ERROR',
                            'value': f"✗ Lỗi khi xử lý {os.path.basename(pdf_path)}: {e}"
                        })
                    
                    processed_count += 1
                    progress = (processed_count / total_files) * 100
                    self.result_queue.put({'type': 'progress', 'value': progress})
            
            if not all_results_data:
                self.result_queue.put({
                    'type': 'error', 
                    'value': "Không có dữ liệu nào được trích xuất từ các file đã chọn."
                })
                return

            self.result_queue.put({'type': 'status', 'value': "Đang xuất kết quả ra Excel..."})
            self.result_queue.put({'type': 'log', 'level': 'INFO', 'value': "Bắt đầu xuất Excel..."})
            
            exported_file_paths = excel_exporter.export_results(
                all_results_data, 
                output_dir, 
                combine_results,
                base_filename="KetQuaChuyenDoiPDF"
            )
            
            if exported_file_paths:
                self.result_queue.put({
                    'type': 'complete',
                    'value': (f"Hoàn thành! Đã xử lý {len(all_results_data)}/{total_files} file PDF.\n"
                              f"Kết quả đã được lưu tại:\n" + "\n".join(exported_file_paths))
                })
            else:
                 self.result_queue.put({
                    'type': 'error', 
                    'value': "Xử lý hoàn tất nhưng không có file Excel nào được tạo."
                })

        except Exception as e:
            # Catch any unexpected errors during the process
            self.result_queue.put({'type': 'error', 'value': f"Lỗi nghiêm trọng trong quá trình xử lý: {e}"})
        finally:
            # Ensure gc.collect is called if it was in the original logic, though it's often not needed here.
            import gc
            gc.collect()


    def check_processing_result(self):
        """Kiểm tra queue và cập nhật GUI. Lặp lại cho đến khi xử lý xong."""
        try:
            while True: # Process all messages currently in queue
                message = self.result_queue.get_nowait() # Non-blocking get
                
                msg_type = message.get('type')
                msg_value = message.get('value')
                msg_level = message.get('level', 'INFO') # Default log level

                if msg_type == 'progress':
                    self.progress_var.set(msg_value)
                    self.status_var.set(f"Đang xử lý... {msg_value:.2f}%")
                elif msg_type == 'status':
                    self.status_var.set(msg_value)
                elif msg_type == 'log':
                    self.log_message(msg_value, msg_level)
                elif msg_type == 'complete':
                    self.is_processing = False
                    self.process_button.config(state="normal")
                    self.status_var.set("Hoàn thành!")
                    self.progress_var.set(100) # Ensure progress bar is full
                    self.log_message(msg_value, "SUCCESS")
                    messagebox.showinfo("Hoàn thành", msg_value)
                    return # Stop polling
                elif msg_type == 'error':
                    self.is_processing = False
                    self.process_button.config(state="normal")
                    self.status_var.set("Có lỗi xảy ra!")
                    self.log_message(msg_value, "ERROR")
                    messagebox.showerror("Lỗi xử lý", msg_value)
                    return # Stop polling
                    
        except queue.Empty:
            # Queue is empty, no new messages for now
            pass 
            
        if self.is_processing:
            # If still processing, schedule this method to run again
            self.root.after(200, self.check_processing_result) # Check every 200ms

# Example of how to run this GUI standalone (for testing purposes)
if __name__ == '__main__':
    # This check is important to prevent issues with multiprocessing,
    # especially on Windows.
    multiprocessing.freeze_support() # Recommended for PyInstaller and multiprocessing

    root = tk.Tk()
    app = PDFToExcelGUI(root)
    root.mainloop()
