from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.process.process_control import ProcessControl

class ProcessControlDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run New Task (fork / exec)")
        self.resize(540, 260)
        self.setStyleSheet("background-color: #1F1F1F; color: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_desc = QLabel("Type process command to launch, or click a Quick Demo Preset button:", self)
        lbl_desc.setFont(QFont("Segoe UI", 9))
        lbl_desc.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(lbl_desc)

        self.txt_cmd = QLineEdit(self)
        self.txt_cmd.setPlaceholderText("e.g., ./dummy_process, sleep 500, xterm, gedit")
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
        self.txt_cmd.returnPressed.connect(self._on_run)
        layout.addWidget(self.txt_cmd)

        # Quick Preset Buttons Frame for Easy Demonstration
        preset_frame = QFrame(self)
        preset_frame.setStyleSheet("background-color: #262626; border-radius: 6px; padding: 6px;")
        preset_layout = QHBoxLayout(preset_frame)
        preset_layout.setContentsMargins(6, 6, 6, 6)

        btn_preset_c = QPushButton("⚙️ Run C Dummy Task", self)
        btn_preset_cpu = QPushButton("🔥 CPU Stress Load", self)
        btn_preset_sleep = QPushButton("💤 Sleep 500s Task", self)

        for btn in [btn_preset_c, btn_preset_cpu, btn_preset_sleep]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #0078D4;
                    border: 1px solid #0078D4;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0078D4;
                    color: #FFFFFF;
                }
            """)

        btn_preset_c.clicked.connect(lambda: self._run_preset("./dummy_process"))
        btn_preset_cpu.clicked.connect(lambda: self._run_preset('python3 -c "import math; [math.sqrt(i) for i in range(10000000)]"'))
        btn_preset_sleep.clicked.connect(lambda: self._run_preset("sleep 500"))

        preset_layout.addWidget(btn_preset_c)
        preset_layout.addWidget(btn_preset_cpu)
        preset_layout.addWidget(btn_preset_sleep)

        layout.addWidget(preset_frame)

        btn_box = QHBoxLayout()
        btn_box.addStretch(1)

        self.btn_ok = QPushButton("▶ Launch Process (fork/exec)", self)
        self.btn_cancel = QPushButton("Cancel", self)

        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px 18px;
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
                padding: 8px 18px;
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

    def _run_preset(self, cmd):
        self.txt_cmd.setText(cmd)
        self._on_run()

    def _on_run(self):
        cmd = self.txt_cmd.text().strip()
        if cmd:
            ok, msg = ProcessControl.launch_process(cmd)
            if ok:
                QMessageBox.information(self, "Task Started", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Error Starting Task", msg)
