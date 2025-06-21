import tkinter as tk
import multiprocessing

# Import the main GUI class from the application package
from pdf_converter_app.gui import PDFToExcelGUI


def main():
    """
    Main function to initialize and run the PDF to Excel Converter application.
    """
    # Recommended for applications using multiprocessing, especially when packaged (e.g., with PyInstaller).
    # This should be called as early as possible.
    multiprocessing.freeze_support()

    root = tk.Tk()
    app = PDFToExcelGUI(root)  # Initialize the main application GUI
    root.mainloop()  # Start the Tkinter event loop


if __name__ == "__main__":
    # This ensures that main() is called only when the script is executed directly,
    # not when it's imported as a module by another script.
    main()
