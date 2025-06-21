
# Project Workflow: PDF to Excel Converter (Modular)

## 1. Initialization (`pdf_excel_gui.py`)

- This is the main entry point when running `python pdf_excel_gui.py`.
- Initializes the Tkinter main window (`root = tk.Tk()`).
- Creates an instance of the `PDFToExcelGUI` class (from `pdf_converter_app.gui`).
- Calls `multiprocessing.freeze_support()` for packaged executables using multiprocessing.
- Starts the Tkinter event loop (`root.mainloop()`), making the GUI interactive.

## 2. GUI Setup (`pdf_converter_app/gui.py` - `PDFToExcelGUI` class)

### `__init__`

- Sets up the main window properties.
- Initializes internal variables like `result_queue`, `selected_files` list.

### `create_widgets`

- Creates and arranges all UI elements (buttons, listboxes, entry fields, labels, progress bar, log area).

### `setup_tesseract`

- Checks for Tesseract availability.
- Logs its status to the GUI's log area.

## 3. User Interaction (Handled in `PDFToExcelGUI`)

- `select_files`: Opens file dialog and stores selected PDFs.
- `clear_files`: Clears the list of selected files.
- `select_output_folder`: Opens dialog to choose output directory.
- UI elements like checkboxes/spinboxes update internal variables for OCR, file combining, and thread count.

## 4. Processing Trigger (`start_processing` method)

- Triggered by "Bắt đầu xử lý" (Start Processing) button.
- Validates inputs and output directory.
- Disables the process button, resets progress bar, updates status.
- Starts a background thread with `_process_files_thread`.
- Periodically calls `check_processing_result` for updates.

## 5. Background Processing (`_process_files_thread`)

- Runs in a separate thread.
- Uses `ThreadPoolExecutor` for concurrent file processing.
- For each file, calls `pdf_processor.process_single_file()` with `pdf_path`, `use_ocr`.
- Collects results and sends updates to `result_queue`.
- After processing, calls `excel_exporter.export_results()`.
- Puts final 'complete' or 'error' messages in the queue.

## 6. Core Data Extraction (Conceptual: `pdf_converter_app/pdf_processor.py`)

**Note:** The source code for `pdf_processor.py` is not included in this public repository. This section describes its conceptual role based on the `pdf_converter_app/pdf_processor_overview.md` document.

### `process_single_file(pdf_path, use_ocr)` (Conceptual)

- **Purpose**: To process a single PDF file, extract text and tabular data.
- **Input**: Path to the PDF file, boolean `use_ocr` indicating if OCR should be applied.
- **Processing Overview**:
  - Utilizes libraries like `pdfplumber` for initial text and table extraction from native PDFs.
  - If `use_ocr` is true (e.g., for scanned PDFs):
    - Employs `pdf2image` to convert PDF pages to images.
    - Uses `pytesseract` (Tesseract OCR engine) to extract text from these images.
  - Implements logic (potentially involving regular expressions or other parsing techniques) to structure the extracted raw text into meaningful information and identify/parse tables.
- **Output**: Typically returns a structured data format (e.g., a Python dictionary) containing:
  - Original filename.
  - Extracted textual data.
  - Extracted tabular data.
- For detailed information on the intended functionality, please refer to `pdf_converter_app/pdf_processor_overview.md`.

## 7. Excel Generation (`pdf_converter_app/excel_exporter.py`)

### `export_results(all_data, output_dir, combine_files, base_filename)`

- Combines all results into one Excel if `combine_files=True`, or creates separate files.
- Saves results as `.xlsx` via `pandas`.
- Returns list of Excel file paths.

## 8. GUI Updates (`check_processing_result`)

- Runs periodically via `root.after()`.
- Checks `result_queue` for updates.
- Updates progress bar, status label, log area.
- Shows success/error message and re-enables the process button.

## 9. Utility Functions (`pdf_converter_app/utils.py`)

- Contains helper functions (e.g., advanced logging, file system helpers).

## 10. Key Points for Modification

- **UI Changes**: Edit `pdf_converter_app/gui.py` (specifically `PDFToExcelGUI.create_widgets` and event handler methods).
- **PDF Processing Logic**: The core PDF processing logic resides in `pdf_converter_app/pdf_processor.py` (which is not in this public repo). To modify or understand this, refer to `pdf_converter_app/pdf_processor_overview.md` and implement/update your local `pdf_processor.py` accordingly.
- **Data Parsing**: If `pdf_processor.py` uses specific parsing functions (like a conceptual `parse_text_info`), those would be part of your local `pdf_processor.py`.
- **Excel Output**: Update logic in `pdf_converter_app/excel_exporter.py`.
- **Main Flow**: Adjust the `_process_files_thread` method in `pdf_converter_app/gui.py` for changes in how files are processed or results are handled.
- **Utility Functions**: If you have a `pdf_converter_app/utils.py`, modifications or additions of helper functions would go there.
