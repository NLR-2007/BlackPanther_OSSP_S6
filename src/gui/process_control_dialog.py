from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.process.process_control import ProcessControl

class ProcessControlDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run New Task")
        self.resize(480, 180)
        self.setStyleSheet("background-color: #1F1F1F; color: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_desc = QLabel("Type the name of a program, folder, document, or executable command:", self)
        lbl_desc.setFont(QFont("Segoe UI", 9))
        lbl_desc.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(lbl_desc)

        self.txt_cmd = QLineEdit(self)
        self.txt_cmd.setPlaceholderText("e.g., htop, gedit, python3 script.py, xterm")
        self.txt_cmd.setStyleSheet("""
            QLineEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.txt_cmd)

        btn_box = QHBoxLayout()
        btn_box.addStretch(1)

        self.btn_ok = QPushButton("Run (fork / exec)", self)
        self.btn_cancel = QPushButton("Cancel", self)

        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)

        self.btn_ok.clicked.connect(self._on_run)
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(self.btn_ok)
        btn_box.addWidget(self.btn_cancel)

        layout.addLayout(btn_box)

    def _on_run(self):
        cmd = self.txt_cmd.text().strip()
        if cmd:
            ok, msg = ProcessControl.launch_process(cmd)
            if ok:
                QMessageBox.information(self, "Task Started", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Error Starting Task", msg)
