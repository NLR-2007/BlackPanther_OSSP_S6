from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtCore import QTimer, Qt

from src.gui.sidebar_nav import SidebarNav
from src.gui.cpu_view import CPUView
from src.gui.memory_view import MemoryView
from src.gui.disk_view import DiskView
from src.gui.network_view import NetworkView
from src.gui.gpu_view import GPUView
from src.gui.process_view import ProcessView

from src.monitoring.cpu_monitor import CPUMonitor
from src.monitoring.memory_monitor import MemoryMonitor
from src.monitoring.disk_monitor import DiskMonitor
from src.monitoring.network_monitor import NetworkMonitor
from src.monitoring.gpu_monitor import GPUMonitor
from src.process.process_manager import ProcessManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Linux Resource Monitoring and Process Control System")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        # Apply Global Dark Windows 11 Task Manager Theme
        self.setStyleSheet("background-color: #191919; color: #FFFFFF;")

        # Instantiate Monitoring Engines
        self.cpu_mon = CPUMonitor()
        self.mem_mon = MemoryMonitor()
        self.disk_mon = DiskMonitor()
        self.net_mon = NetworkMonitor()
        self.gpu_mon = GPUMonitor()
        self.proc_mon = ProcessManager()

        # Central Widget & Layout
        central_widget = QWidget(self)
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Navigation Sidebar
        self.sidebar = SidebarNav(self)
        self.sidebar.item_selected.connect(self._on_nav_selected)
        main_layout.addWidget(self.sidebar)

        # 2. Main Content Container
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Views
        self.cpu_view = CPUView(self)
        self.mem_view = MemoryView(self)
        self.disk_view = DiskView(self)
        self.net_view = NetworkView(self)
        self.gpu_view = GPUView(self)
        self.proc_view = ProcessView(self)

        for view in [self.cpu_view, self.mem_view, self.disk_view, self.net_view, self.gpu_view, self.proc_view]:
            view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.stacked_widget.addWidget(self.cpu_view)    # Index 0
        self.stacked_widget.addWidget(self.mem_view)    # Index 1
        self.stacked_widget.addWidget(self.disk_view)   # Index 2
        self.stacked_widget.addWidget(self.net_view)    # Index 3
        self.stacked_widget.addWidget(self.gpu_view)    # Index 4
        self.stacked_widget.addWidget(self.proc_view)   # Index 5

        main_layout.addWidget(self.stacked_widget, stretch=1)

        # Setup 1-Second Telemetry Loop Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # 1000 ms = 1s
        self.timer.timeout.connect(self._update_all_telemetry)
        self.timer.start()

        # Initial Refresh
        self._update_all_telemetry()

        # Open in Maximized Full Screen mode by default
        self.showMaximized()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showMaximized()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)

    def _on_nav_selected(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def _update_all_telemetry(self):
        # 1. CPU Telemetry
        cpu_data = self.cpu_mon.get_metrics()
        self.cpu_view.update_metrics(cpu_data)
        self.sidebar.update_sidebar_card(0, f"{cpu_data['usage']:.1f}%  {cpu_data['frequency_ghz']:.2f} GHz", cpu_data["history"])

        # 2. Memory Telemetry
        mem_data = self.mem_mon.get_metrics()
        self.mem_view.update_metrics(mem_data)
        self.sidebar.update_sidebar_card(1, f"{mem_data['used_gb']:.1f}/{mem_data['total_gb']:.1f} GB ({mem_data['usage_pct']:.0f}%)", mem_data["history"])

        # 3. Disk Telemetry
        disk_data = self.disk_mon.get_metrics()
        self.disk_view.update_metrics(disk_data)
        self.sidebar.update_sidebar_card(2, f"R: {disk_data['read_mbps']:.1f} MB/s W: {disk_data['write_mbps']:.1f} MB/s", disk_data["history_read"])

        # 4. Network Telemetry
        net_data = self.net_mon.get_metrics()
        self.net_view.update_metrics(net_data)
        self.sidebar.update_sidebar_card(3, f"Send: {net_data['upload_kbps']:.0f} K Recv: {net_data['download_kbps']:.0f} K", net_data["history_down"])

        # 5. GPU Telemetry
        gpu_data = self.gpu_mon.get_metrics()
        self.gpu_view.update_metrics(gpu_data)
        self.sidebar.update_sidebar_card(4, f"{gpu_data['utilization_pct']:.1f}%  {gpu_data['temperature_c']:.0f}°C", gpu_data["history"])

        # 6. Process Manager List
        proc_list = self.proc_mon.get_process_list()
        self.proc_view.update_processes(proc_list)
        self.sidebar.update_sidebar_card(5, f"{len(proc_list)} Processes Active", None)
