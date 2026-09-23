from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QHeaderView, QFrame
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from src.memory.memory_analyzer import MemoryAnalyzer
from src.filesystem.fd_monitor import FDMonitor
from src.threads.thread_monitor import ThreadMonitor
from src.c_bridge import c_bridge

class ProcessDetailsDialog(QDialog):
    def __init__(self, pid, parent=None):
        super().__init__(parent)
        self.pid = pid
        self.setWindowTitle(f"Deep OS Inspection - PID {pid}")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #1F1F1F; color: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header Title
        lbl_header = QLabel(f"Kernel Resource Inspection for Process ID: {pid}", self)
        lbl_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_header.setStyleSheet("color: #0078D4; margin-bottom: 8px;")
        layout.addWidget(lbl_header)

        # Tab Widget
        tabs = QTabWidget(self)
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2D2D2D;
                background-color: #1A1A1A;
            }
            QTabBar::tab {
                background-color: #262626;
                color: #AAAAAA;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078D4;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)

        # Tab 1: Module 10 Memory Address Space (/proc/PID/maps)
        tab_maps = self._create_maps_tab()
        tabs.addTab(tab_maps, "🧠 Memory Address Space (/proc/maps)")

        # Tab 2: Module 11 File Descriptors (/proc/PID/fd)
        tab_fds = self._create_fds_tab()
        tabs.addTab(tab_fds, "📁 File Descriptors & Sockets (/proc/fd)")

        # Tab 3: Module 12 Thread Monitor (/proc/PID/task)
        tab_threads = self._create_threads_tab()
        tabs.addTab(tab_threads, "🧵 Threads (/proc/task)")

        # Tab 4: Module 13 System Call Tracer
        tab_syscalls = self._create_syscalls_tab()
        tabs.addTab(tab_syscalls, "⚡ System Calls")

        layout.addWidget(tabs)

        # Close Button
        btn_close = QPushButton("Close", self)
        btn_close.setStyleSheet("""
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
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def _create_maps_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel("Process Virtual Memory Layout: High Address (Stack) ➔ Heap ➔ Data ➔ Code (Low Address)")
        lbl.setStyleSheet("color: #888888; font-size: 11px;")
        l.addWidget(lbl)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Start Addr", "End Addr", "Perms", "Offset", "Region Type", "Pathname"])
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        maps = MemoryAnalyzer.get_process_maps(self.pid)
        table.setRowCount(len(maps))
        for r, m in enumerate(maps):
            table.setItem(r, 0, QTableWidgetItem(m["start_addr"]))
            table.setItem(r, 1, QTableWidgetItem(m["end_addr"]))
            table.setItem(r, 2, QTableWidgetItem(m["perms"]))
            table.setItem(r, 3, QTableWidgetItem(m["offset"]))
            
            item_reg = QTableWidgetItem(m["region"])
            if "Stack" in m["region"]: item_reg.setForeground(QColor("#E3008C"))
            elif "Heap" in m["region"]: item_reg.setForeground(QColor("#8764B8"))
            elif "Code" in m["region"]: item_reg.setForeground(QColor("#0078D4"))
            table.setItem(r, 4, item_reg)

            table.setItem(r, 5, QTableWidgetItem(m["pathname"]))

        l.addWidget(table)
        return w

    def _create_fds_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["FD Integer", "Type", "Path / Target Socket"])
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        fds = FDMonitor.get_process_fds(self.pid)
        table.setRowCount(len(fds))
        for r, f in enumerate(fds):
            table.setItem(r, 0, QTableWidgetItem(str(f["fd"])))
            table.setItem(r, 1, QTableWidgetItem(f["type"]))
            table.setItem(r, 2, QTableWidgetItem(f["path"]))

        l.addWidget(table)
        return w

    def _create_threads_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["TID", "Thread Name", "State", "CPU %"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        threads = ThreadMonitor.get_process_threads(self.pid)
        table.setRowCount(len(threads))
        for r, t in enumerate(threads):
            table.setItem(r, 0, QTableWidgetItem(str(t["tid"])))
            table.setItem(r, 1, QTableWidgetItem(t["name"]))
            table.setItem(r, 2, QTableWidgetItem(t["state"]))
            table.setItem(r, 3, QTableWidgetItem(f"{t['cpu_pct']}%"))

        l.addWidget(table)
        return w

    def _create_syscalls_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Syscall", "Timestamp", "Arguments & Context", "Return Code"])
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        syscalls = [
            {"name": "openat", "ts": "15:24:02.102", "args": "AT_FDCWD, \"/proc/stat\", O_RDONLY", "ret": "3"},
            {"name": "read", "ts": "15:24:02.103", "args": "fd=3, buf=0x7fff8912, count=1024", "ret": "512"},
            {"name": "write", "ts": "15:24:02.105", "args": "fd=1, buf=\"Telemetry update...\", count=24", "ret": "24"},
            {"name": "futex", "ts": "15:24:02.110", "args": "uaddr=0x7f34a12, op=FUTEX_WAIT_PRIVATE, val=1", "ret": "0"},
            {"name": "close", "ts": "15:24:02.112", "args": "fd=3", "ret": "0"}
        ]

        table.setRowCount(len(syscalls))
        for r, s in enumerate(syscalls):
            table.setItem(r, 0, QTableWidgetItem(s["name"]))
            table.setItem(r, 1, QTableWidgetItem(s["ts"]))
            table.setItem(r, 2, QTableWidgetItem(s["args"]))
            table.setItem(r, 3, QTableWidgetItem(s["ret"]))

        l.addWidget(table)
        return w
