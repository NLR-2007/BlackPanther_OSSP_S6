#!/usr/bin/env python3
import sys
import os

# Set Qt & Mesa Software Rendering Environment Variables for Ubuntu / WSL compatibility
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["QT_XCB_GL_INTEGRATION"] = "none"
os.environ["QT_QUICK_BACKEND"] = "software"

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set default modern UI Font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
