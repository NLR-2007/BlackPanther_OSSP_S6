from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt
from src.gui.graph_widget import LiveGraphWidget

class MemoryCompositionBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.used_pct = 50.0
        self.cached_pct = 20.0

    def set_composition(self, used_pct, cached_pct):
        self.used_pct = max(0.0, min(100.0, used_pct))
        self.cached_pct = max(0.0, min(100.0 - self.used_pct, cached_pct))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background (Available RAM)
        painter.fillRect(0, 0, w, h, QColor("#333333"))

        used_w = int(w * (self.used_pct / 100.0))
        cached_w = int(w * (self.cached_pct / 100.0))

        # Used RAM (Purple Accent)
        painter.fillRect(0, 0, used_w, h, QColor("#8764B8"))

        # Cached Memory (Dark Purple)
        painter.fillRect(used_w, 0, cached_w, h, QColor("#5C2D91"))


class MemoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1F1F1F;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("Memory", self)
        self.lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")

        self.lbl_summary = QLabel("0.0 / 0.0 GB (0%)", self)
        self.lbl_summary.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_summary.setStyleSheet("color: #8764B8;")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.lbl_summary)
        layout.addLayout(header_layout)

        # 60s Live Memory Chart Graph
        self.graph = LiveGraphWidget(color="#8764B8", title="Memory Usage", unit="%", max_val=100.0, parent=self)
        layout.addWidget(self.graph)

        # Memory Composition Bar Section
        comp_box = QVBoxLayout()
        comp_title = QLabel("Memory Composition", self)
        comp_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        comp_title.setStyleSheet("color: #AAAAAA;")
        self.comp_bar = MemoryCompositionBar(self)

        comp_box.addWidget(comp_title)
        comp_box.addWidget(self.comp_bar)
        layout.addLayout(comp_box)

        # Memory Telemetry Grid Cards
        grid_frame = QFrame(self)
        grid_frame.setStyleSheet("background-color: #262626; border-radius: 8px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(16, 16, 16, 16)
        grid_layout.setHorizontalSpacing(32)
        grid_layout.setVerticalSpacing(16)

        self.val_used = self._add_card(grid_layout, 0, 0, "In Use (RAM)", "0.0 GB")
        self.val_avail = self._add_card(grid_layout, 0, 1, "Available", "0.0 GB")
        self.val_cached = self._add_card(grid_layout, 0, 2, "Cached", "0.0 GB")
        self.val_swap = self._add_card(grid_layout, 1, 0, "Swap File (Used/Total)", "0.0 / 0.0 GB")
        self.val_paged = self._add_card(grid_layout, 1, 1, "Paged Pool", "0 MB")
        self.val_nonpaged = self._add_card(grid_layout, 1, 2, "Non-paged Pool", "0 MB")

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
        total = data["total_gb"]
        used = data["used_gb"]
        pct = data["usage_pct"]

        self.lbl_summary.setText(f"{used:.1f} / {total:.1f} GB ({pct:.0f}%)")
        self.graph.update_data(data["history"])

        cached = data["cached_gb"]
        cached_pct = (cached / total * 100.0) if total > 0 else 0.0
        self.comp_bar.set_composition(pct, cached_pct)

        self.val_used.setText(f"{used:.2f} GB")
        self.val_avail.setText(f"{data['available_gb']:.2f} GB")
        self.val_cached.setText(f"{cached:.2f} GB")
        self.val_swap.setText(f"{data['swap_used_gb']:.2f} / {data['swap_total_gb']:.2f} GB")
        self.val_paged.setText(f"{data['paged_pool_mb']:.0f} MB")
        self.val_nonpaged.setText(f"{data['nonpaged_pool_mb']:.0f} MB")
