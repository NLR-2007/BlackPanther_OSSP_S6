from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QPointF, QRectF

class LiveGraphWidget(QWidget):
    def __init__(self, color="#0078D4", fill_gradient=True, title="CPU Usage", unit="%", max_val=100.0, parent=None):
        super().__init__(parent)
        self.primary_color = QColor(color)
        self.fill_gradient = fill_gradient
        self.title = title
        self.unit = unit
        self.max_val = max_val
        self.data_history = [0.0] * 60
        self.second_history = None  # Optional second dataset (e.g. Upload speed)
        self.second_color = QColor("#E3008C")

        self.setMinimumHeight(220)
        self.setMouseTracking(True)
        self.hover_x = -1

    def update_data(self, history, second_history=None, max_val=None):
        if history:
            self.data_history = list(history[-60:])
        if second_history:
            self.second_history = list(second_history[-60:])
        if max_val is not None and max_val > 0:
            self.max_val = max_val
        self.update()

    def mouseMoveEvent(self, event):
        self.hover_x = event.position().x()
        self.update()

    def leaveEvent(self, event):
        self.hover_x = -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Margins for Y-axis scale labels and bottom timeline
        margin_right = 50
        margin_bottom = 24
        margin_top = 10
        margin_left = 10

        chart_w = width - margin_left - margin_right
        chart_h = height - margin_top - margin_bottom

        if chart_w <= 10 or chart_h <= 10:
            return

        # 1. Dark Card Outer Canvas Background & Border
        painter.fillRect(0, 0, width, height, QColor("#141414"))

        # Inner Chart Rectangle Background (Windows 11 Dark Charcoal)
        chart_rect = QRectF(margin_left, margin_top, chart_w, chart_h)
        painter.fillRect(chart_rect, QColor("#1F1F1F"))
        painter.setPen(QPen(QColor("#2B2B2B"), 1))
        painter.drawRect(chart_rect)

        # 2. Render Win11 Grid Lines & Y-Axis Percentage Labels
        grid_pen = QPen(QColor("#2A2A2A"), 1, Qt.PenStyle.SolidLine)
        painter.setPen(grid_pen)
        painter.setFont(QFont("Segoe UI", 8))

        # Y-Axis 5 Horizontal Divisions (0%, 25%, 50%, 75%, 100%)
        for i in range(5):
            ratio = i / 4.0
            y = margin_top + chart_h * (1.0 - ratio)
            if 0 < i < 4:
                painter.drawLine(int(margin_left), int(y), int(margin_left + chart_w), int(y))

            # Y-Axis Scale Text Label on Right Margin
            val_num = self.max_val * ratio
            if self.unit == "%":
                lbl_text = f"{int(val_num)}%"
            elif val_num >= 10.0:
                lbl_text = f"{int(val_num)} {self.unit.strip()}"
            else:
                lbl_text = f"{val_num:.1f}"

            painter.setPen(QColor("#777777"))
            painter.drawText(int(margin_left + chart_w + 8), int(y + 4), lbl_text)
            painter.setPen(grid_pen)

        # X-Axis 4 Vertical Divisions (60s, 45s, 30s, 15s, 0s)
        for i in range(1, 4):
            x = margin_left + (chart_w * i / 4.0)
            painter.drawLine(int(x), int(margin_top), int(x), int(margin_top + chart_h))

        # Bottom Timeline Axis Text (60 seconds -> 0)
        painter.setPen(QColor("#777777"))
        painter.drawText(int(margin_left), int(height - 6), "60 seconds")
        painter.drawText(int(margin_left + chart_w - 15), int(height - 6), "0")

        if not self.data_history or len(self.data_history) < 2:
            return

        # Calculate max scaling ceiling
        peak = max(self.data_history)
        if self.second_history:
            peak = max(peak, max(self.second_history))
        target_max = max(self.max_val, peak * 1.15) if self.max_val != 100.0 else 100.0
        if target_max <= 0: target_max = 1.0

        n = len(self.data_history)
        step_x = chart_w / max(1, n - 1)

        # Build Primary Curve & Area Fill Path
        points = []
        for i, val in enumerate(self.data_history):
            x = margin_left + i * step_x
            y = margin_top + chart_h - (val / target_max) * chart_h
            y = max(margin_top, min(margin_top + chart_h, y))
            points.append(QPointF(x, y))

        path = QPainterPath()
        fill_path = QPainterPath()

        if points:
            path.moveTo(points[0])
            fill_path.moveTo(margin_left, margin_top + chart_h)
            fill_path.lineTo(points[0])

            # Smooth Bezier Curve Fitting
            for i in range(1, len(points)):
                p0 = points[i - 1]
                p1 = points[i]
                cx = (p0.x() + p1.x()) / 2.0
                path.cubicTo(QPointF(cx, p0.y()), QPointF(cx, p1.y()), p1)
                fill_path.cubicTo(QPointF(cx, p0.y()), QPointF(cx, p1.y()), p1)

            fill_path.lineTo(margin_left + chart_w, margin_top + chart_h)
            fill_path.closeSubpath()

        # 3. Render Area Gradient Fill
        if self.fill_gradient:
            gradient = QLinearGradient(0, margin_top, 0, margin_top + chart_h)
            c_top = QColor(self.primary_color)
            c_top.setAlpha(70)  # Windows 11 Fluent 28% top opacity
            c_bot = QColor(self.primary_color)
            c_bot.setAlpha(4)   # Fades down to translucent bottom
            gradient.setColorAt(0.0, c_top)
            gradient.setColorAt(1.0, c_bot)
            painter.fillPath(fill_path, QBrush(gradient))

        # 4. Render Primary Curve Line (2px solid line stroke)
        line_pen = QPen(self.primary_color, 2, Qt.PenStyle.SolidLine)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(path)

        # 5. Render Secondary Curve if present (e.g. Network Upload / Write Speed)
        if self.second_history and len(self.second_history) == n:
            sec_points = []
            for i, val in enumerate(self.second_history):
                x = margin_left + i * step_x
                y = margin_top + chart_h - (val / target_max) * chart_h
                y = max(margin_top, min(margin_top + chart_h, y))
                sec_points.append(QPointF(x, y))

            sec_path = QPainterPath()
            if sec_points:
                sec_path.moveTo(sec_points[0])
                for i in range(1, len(sec_points)):
                    p0 = sec_points[i - 1]
                    p1 = sec_points[i]
                    cx = (p0.x() + p1.x()) / 2.0
                    sec_path.cubicTo(QPointF(cx, p0.y()), QPointF(cx, p1.y()), p1)

                sec_pen = QPen(self.second_color, 2, Qt.PenStyle.DashLine)
                painter.setPen(sec_pen)
                painter.drawPath(sec_path)

        # 6. Interactive Hover Crosshair, Node Glow, and Callout Tooltip
        if margin_left <= self.hover_x <= margin_left + chart_w:
            idx = int((self.hover_x - margin_left) / step_x)
            idx = max(0, min(n - 1, idx))
            hover_val = self.data_history[idx]
            pt = points[idx]

            # Vertical Crosshair Line
            painter.setPen(QPen(QColor("#888888"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(int(pt.x()), int(margin_top), int(pt.x()), int(margin_top + chart_h))

            # Glowing Intersection Node Dot
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.setBrush(QBrush(self.primary_color))
            painter.drawEllipse(pt, 5, 5)

            # Floating Tooltip Pill
            t_sec = 60 - idx
            tip_str = f" {hover_val:.1f}{self.unit} (-{t_sec}s) "
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            fm = QFontMetrics(painter.font())
            tip_w = fm.horizontalAdvance(tip_str) + 12
            tip_h = 24

            tip_x = pt.x() + 10
            if tip_x + tip_w > margin_left + chart_w:
                tip_x = pt.x() - tip_w - 10
            tip_y = max(margin_top + 5, pt.y() - 30)

            # Tooltip Pill Box
            tip_rect = QRectF(tip_x, tip_y, tip_w, tip_h)
            painter.setPen(QPen(QColor("#444444"), 1))
            painter.setBrush(QBrush(QColor("#282828")))
            painter.drawRoundedRect(tip_rect, 4, 4)

            # Tooltip Text
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(tip_rect, Qt.AlignmentFlag.AlignCenter, tip_str)
