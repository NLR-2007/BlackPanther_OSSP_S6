from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.gui.graph_widget import LiveGraphWidget

class GPUView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1F1F1F;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("GPU", self)
        self.lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")

        self.lbl_pct = QLabel("0%", self)
        self.lbl_pct.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.lbl_pct.setStyleSheet("color: #744DA9;")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.lbl_pct)
        layout.addLayout(header_layout)

        # GPU Utilization Graph
        self.graph = LiveGraphWidget(color="#744DA9", title="GPU Utilization", unit="%", max_val=100.0, parent=self)
        layout.addWidget(self.graph)

        # Telemetry Grid Cards
        grid_frame = QFrame(self)
        grid_frame.setStyleSheet("background-color: #262626; border-radius: 8px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(16, 16, 16, 16)
        grid_layout.setHorizontalSpacing(32)
        grid_layout.setVerticalSpacing(16)

        self.val_name = self._add_card(grid_layout, 0, 0, "GPU Model", "Intel Arc / NVIDIA / AMD")
        self.val_vram = self._add_card(grid_layout, 0, 1, "GPU Memory (VRAM)", "1.4 / 8.0 GB")
        self.val_temp = self._add_card(grid_layout, 0, 2, "Temperature", "45 °C")
        self.val_power = self._add_card(grid_layout, 1, 0, "Power Usage", "28.5 W")
        self.val_decode = self._add_card(grid_layout, 1, 1, "Video Decode", "0%")
        self.val_encode = self._add_card(grid_layout, 1, 2, "Video Encode", "0%")

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
        pct = data["utilization_pct"]
        self.lbl_pct.setText(f"{pct:.1f}%")
        self.graph.update_data(data["history"])

        self.val_name.setText(data["gpu_name"])
        self.val_vram.setText(f"{data['vram_used_mb']/1024:.1f} / {data['vram_total_mb']/1024:.1f} GB")
        self.val_temp.setText(f"{data['temperature_c']:.1f} °C")
        self.val_power.setText(f"{data['power_watts']:.1f} W")
        self.val_decode.setText(f"{data['video_decode_pct']:.1f}%")
        self.val_encode.setText(f"{data['video_encode_pct']:.1f}%")
