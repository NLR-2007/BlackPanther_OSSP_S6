from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.gui.graph_widget import LiveGraphWidget

class DiskView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1F1F1F;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("Disk (SSD / NVMe)", self)
        self.lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")

        self.lbl_speeds = QLabel("R: 0.0 MB/s | W: 0.0 MB/s", self)
        self.lbl_speeds.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_speeds.setStyleSheet("color: #107C41;")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.lbl_speeds)
        layout.addLayout(header_layout)

        # Live Graph Widget
        self.graph = LiveGraphWidget(color="#107C41", title="Disk Transfer Rate", unit=" MB/s", max_val=20.0, parent=self)
        layout.addWidget(self.graph)

        # Telemetry Grid Cards
        grid_frame = QFrame(self)
        grid_frame.setStyleSheet("background-color: #262626; border-radius: 8px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(16, 16, 16, 16)
        grid_layout.setHorizontalSpacing(32)
        grid_layout.setVerticalSpacing(16)

        self.val_name = self._add_card(grid_layout, 0, 0, "Device Name", "NVMe SSD")
        self.val_read = self._add_card(grid_layout, 0, 1, "Read Speed", "0.0 MB/s")
        self.val_write = self._add_card(grid_layout, 0, 2, "Write Speed", "0.0 MB/s")
        self.val_usage = self._add_card(grid_layout, 1, 0, "Storage Usage", "0%")
        self.val_capacity = self._add_card(grid_layout, 1, 1, "Capacity (Used / Total)", "0 / 0 GB")
        self.val_type = self._add_card(grid_layout, 1, 2, "Drive Interface", "PCIe NVMe Gen4")

        layout.addWidget(grid_frame)
        layout.addStretch(1)

    def _add_card(self, grid, row, col, title, initial_val):
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
        r_mbps = data["read_mbps"]
        w_mbps = data["write_mbps"]
        self.lbl_speeds.setText(f"R: {r_mbps:.1f} MB/s | W: {w_mbps:.1f} MB/s")
        self.graph.update_data(data["history_read"], data["history_write"], max_val=max(10.0, max(r_mbps, w_mbps) * 1.5))

        self.val_name.setText(data["disk_name"])
        self.val_read.setText(f"{r_mbps:.2f} MB/s")
        self.val_write.setText(f"{w_mbps:.2f} MB/s")
        self.val_usage.setText(f"{data['usage_pct']:.1f}%")
        self.val_capacity.setText(f"{data['used_gb']:.1f} / {data['total_gb']:.1f} GB")
