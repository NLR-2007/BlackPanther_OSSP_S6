from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont
from PyQt6.QtCore import Qt, pyqtSignal

class SparklinePreview(QWidget):
    def __init__(self, color="#0078D4", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.history = [0.0] * 30
        self.setFixedSize(54, 28)

    def set_history(self, history):
        if history:
            self.history = list(history[-30:])
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor("#141414"))

        if len(self.history) < 2:
            return

        peak = max(self.history)
        max_val = max(100.0, peak) if peak <= 100.0 else peak
        if max_val <= 0: max_val = 1.0

        n = len(self.history)
        step_x = w / max(1, n - 1)

        path = QPainterPath()
        for i, val in enumerate(self.history):
            x = i * step_x
            y = h - (val / max_val) * (h - 4) - 2
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        painter.setPen(QPen(self.color, 1.5))
        painter.drawPath(path)


class SidebarNavItem(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, index, title, color="#0078D4", parent=None):
        super().__init__(parent)
        self.index = index
        self.title = title
        self.color = color
        self.is_selected = False

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)

        # Left Metric Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.lbl_title = QLabel(title, self)
        self.lbl_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")

        self.lbl_subtitle = QLabel("0%", self)
        self.lbl_subtitle.setFont(QFont("Segoe UI", 8))
        self.lbl_subtitle.setStyleSheet("color: #AAAAAA;")

        info_layout.addWidget(self.lbl_title)
        info_layout.addWidget(self.lbl_subtitle)

        # Mini Sparkline Preview
        self.sparkline = SparklinePreview(color=color, parent=self)

        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(self.sparkline)

        self.update_style()

    def set_metrics(self, text, history=None):
        self.lbl_subtitle.setText(text)
        if history:
            self.sparkline.set_history(history)

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet(f"""
                SidebarNavItem {{
                    background-color: #2D2D2D;
                    border-left: 4px solid {self.color};
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet("""
                SidebarNavItem {
                    background-color: #1F1F1F;
                    border-left: 4px solid transparent;
                    border-radius: 6px;
                }
                SidebarNavItem:hover {
                    background-color: #262626;
                }
            """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
        super().mousePressEvent(event)


class SidebarNav(QWidget):
    item_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setStyleSheet("background-color: #181818;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(6)

        # App Header Label
        lbl_app = QLabel("PERFORMANCE", self)
        lbl_app.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_app.setStyleSheet("color: #777777; margin-left: 8px; margin-bottom: 4px;")
        layout.addWidget(lbl_app)

        # Module 1 Sidebar Cards
        self.items = []
        card_defs = [
            (0, "CPU", "#0078D4"),
            (1, "Memory", "#8764B8"),
            (2, "Disk", "#107C41"),
            (3, "Network", "#E3008C"),
            (4, "GPU", "#744DA9"),
            (5, "Processes", "#00A4EF")
        ]

        for idx, title, color in card_defs:
            item = SidebarNavItem(idx, title, color, self)
            item.clicked.connect(self._on_item_clicked)
            self.items.append(item)
            layout.addWidget(item)

        layout.addStretch(1)
        self.select_item(0)

    def _on_item_clicked(self, index):
        self.select_item(index)
        self.item_selected.emit(index)

    def select_item(self, index):
        for i, item in enumerate(self.items):
            item.set_selected(i == index)

    def update_sidebar_card(self, index, subtitle, history=None):
        if 0 <= index < len(self.items):
            self.items[index].set_metrics(subtitle, history)
