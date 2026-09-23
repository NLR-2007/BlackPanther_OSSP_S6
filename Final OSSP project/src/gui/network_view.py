from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.gui.graph_widget import LiveGraphWidget

class NetworkView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1F1F1F;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("Network (Wi-Fi / Ethernet)", self)
        self.lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #FFFFFF;")

        self.lbl_speeds = QLabel("S: 0 Kbps | R: 0 Kbps", self)
        self.lbl_speeds.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_speeds.setStyleSheet("color: #E3008C;")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.lbl_speeds)
        layout.addLayout(header_layout)

        # Live Dual Throughput Graph (Send & Receive)
        self.graph = LiveGraphWidget(color="#E3008C", title="Network Throughput", unit=" Kbps", max_val=500.0, parent=self)
        layout.addWidget(self.graph)

        # Telemetry Grid Cards
        grid_frame = QFrame(self)
        grid_frame.setStyleSheet("background-color: #262626; border-radius: 8px;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(16, 16, 16, 16)
        grid_layout.setHorizontalSpacing(32)
        grid_layout.setVerticalSpacing(16)

        self.val_adapter = self._add_card(grid_layout, 0, 0, "Adapter Name", "wlan0")
        self.val_type = self._add_card(grid_layout, 0, 1, "Connection Type", "Wi-Fi (802.11ac)")
        self.val_down = self._add_card(grid_layout, 0, 2, "Receive (Download)", "0 Kbps")
        self.val_up = self._add_card(grid_layout, 1, 0, "Send (Upload)", "0 Kbps")
        self.val_rx_tot = self._add_card(grid_layout, 1, 1, "Total Received", "0 MB")
        self.val_tx_tot = self._add_card(grid_layout, 1, 2, "Total Sent", "0 MB")

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
        down = data["download_kbps"]
        up = data["upload_kbps"]

        self.lbl_speeds.setText(f"Send: {up:.0f} Kbps | Recv: {down:.0f} Kbps")
        self.graph.update_data(data["history_down"], data["history_up"], max_val=max(100.0, max(down, up) * 1.5))

        self.val_adapter.setText(data["adapter_name"])
        self.val_type.setText(data["connection_type"])
        self.val_down.setText(f"{down:.1f} Kbps")
        self.val_up.setText(f"{up:.1f} Kbps")
        self.val_rx_tot.setText(f"{data['total_rx_mb']:.1f} MB")
        self.val_tx_tot.setText(f"{data['total_tx_mb']:.1f} MB")
