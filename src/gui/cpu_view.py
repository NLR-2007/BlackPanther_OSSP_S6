from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.gui.graph_widget import LiveGraphWidget

class CPUView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1F1F1F;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title & Main Percentage
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("CPU", self)
        self.lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")

        self.lbl_pct = QLabel("0%", self)
        self.lbl_pct.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.lbl_pct.setStyleSheet("color: #0078D4;")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.lbl_pct)
        layout.addLayout(header_layout)

        # 60s Live Area Chart Graph
        self.graph = LiveGraphWidget(color="#0078D4", title="CPU Usage", unit="%", max_val=100.0, parent=self)
        layout.addWidget(self.graph)

        # Telemetry Metric Grid Cards (Windows 11 Task Manager style)
        grid_frame = QFrame(self)
        grid_frame.setStyleSheet("background-color: #262626; border-radius: 8px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(16, 16, 16, 16)
        grid_layout.setHorizontalSpacing(32)
        grid_layout.setVerticalSpacing(16)

        self.val_freq = self._add_metric_card(grid_layout, 0, 0, "Frequency", "0.00 GHz")
        self.val_procs = self._add_metric_card(grid_layout, 0, 1, "Processes", "0")
        self.val_threads = self._add_metric_card(grid_layout, 0, 2, "Threads", "0")
        self.val_handles = self._add_metric_card(grid_layout, 1, 0, "Handles / FDs", "0")
        self.val_uptime = self._add_metric_card(grid_layout, 1, 1, "Up time", "00:00:00")
        self.val_cores = self._add_metric_card(grid_layout, 1, 2, "Cores / Log. Proc", "4 / 8")

        layout.addWidget(grid_frame)
        layout.addStretch(1)

    def _add_metric_card(self, grid, row, col, title, initial_val):
        box = QVBoxLayout()
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 9))
        lbl_t.setStyleSheet("color: #888888;")

        lbl_v = QLabel(initial_val)
        lbl_v.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_v.setStyleSheet("color: #FFFFFF;")

        box.addWidget(lbl_t)
        box.addWidget(lbl_v)
        grid.addLayout(box, row, col)
        return lbl_v

    def update_metrics(self, data):
        usage = data["usage"]
        self.lbl_pct.setText(f"{usage:.1f}%")
        self.graph.update_data(data["history"])

        self.val_freq.setText(f"{data['frequency_ghz']:.2f} GHz")
        self.val_procs.setText(str(data["processes"]))
        self.val_threads.setText(str(data["threads"]))
        self.val_handles.setText(str(data["handles"]))

        # Format Uptime
        sec = data["uptime_sec"]
        hrs = sec // 3600
        mins = (sec % 3600) // 60
        secs = sec % 60
        self.val_uptime.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")

        self.val_cores.setText(f"{data['cores']} / {data['logical_processors']}")
