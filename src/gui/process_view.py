from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont, QColor, QAction
from PyQt6.QtCore import Qt, pyqtSignal
from src.process.process_control import ProcessControl
from src.gui.process_details_dialog import ProcessDetailsDialog
from src.gui.process_control_dialog import ProcessControlDialog

class ProcessView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1F1F1F;")
        self.process_data = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar Header: Search & Action Buttons
        toolbar_layout = QHBoxLayout()

        self.txt_search = QLineEdit(self)
        self.txt_search.setPlaceholderText("🔍 Filter processes by name or PID...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0078D4;
            }
        """)
        self.txt_search.textChanged.connect(self._apply_filter)

        self.btn_new = QPushButton("▶ Run New Task", self)
        self.btn_end = QPushButton("⛔ End Task", self)
        self.btn_pause = QPushButton("⏸ Pause", self)
        self.btn_resume = QPushButton("▶ Resume", self)
        self.btn_inspect = QPushButton("🔍 Deep Inspect OS", self)

        for btn in [self.btn_new, self.btn_end, self.btn_pause, self.btn_resume, self.btn_inspect]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: 1px solid #3D3D3D;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                }
            """)

        self.btn_end.setStyleSheet("""
            QPushButton {
                background-color: #C42B1C;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D83B01;
            }
        """)

        self.btn_new.clicked.connect(self._on_new_task)
        self.btn_end.clicked.connect(self._on_end_task)
        self.btn_pause.clicked.connect(self._on_pause_task)
        self.btn_resume.clicked.connect(self._on_resume_task)
        self.btn_inspect.clicked.connect(self._on_inspect_task)

        toolbar_layout.addWidget(self.txt_search, stretch=1)
        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addWidget(self.btn_end)
        toolbar_layout.addWidget(self.btn_pause)
        toolbar_layout.addWidget(self.btn_resume)
        toolbar_layout.addWidget(self.btn_inspect)

        layout.addLayout(toolbar_layout)

        # Process Table Widget
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "PID", "Name", "User", "CPU %", "Memory (MB)", "Status", "Threads", "Priority"
        ])

        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1A1A1A;
                alternate-background-color: #222222;
                color: #DDDDDD;
                gridline-color: #2A2A2A;
                border: 1px solid #2D2D2D;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #AAAAAA;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #0078D4;
                color: #FFFFFF;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)

    def update_processes(self, proc_list):
        self.process_data = proc_list
        filter_text = self.txt_search.text().lower()

        # Temporarily disable sorting while updating items
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for p in proc_list:
            if filter_text and filter_text not in p["name"].lower() and filter_text not in str(p["pid"]):
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            # PID
            item_pid = QTableWidgetItem()
            item_pid.setData(Qt.ItemDataRole.DisplayRole, p["pid"])
            self.table.setItem(row, 0, item_pid)

            # Name
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))

            # User
            self.table.setItem(row, 2, QTableWidgetItem(p["user"]))

            # CPU %
            item_cpu = QTableWidgetItem()
            item_cpu.setData(Qt.ItemDataRole.DisplayRole, round(p["cpu_pct"], 1))
            self.table.setItem(row, 3, item_cpu)

            # Memory (MB)
            item_mem = QTableWidgetItem()
            item_mem.setData(Qt.ItemDataRole.DisplayRole, round(p["mem_rss_mb"], 1))
            self.table.setItem(row, 4, item_mem)

            # Status Pill Label
            status_str = f"[{p['status_code']}] {p['status_label']}"
            item_status = QTableWidgetItem(status_str)
            if p["status_code"] == 'R':
                item_status.setForeground(QColor("#107C41"))
            elif p["status_code"] == 'S':
                item_status.setForeground(QColor("#0078D4"))
            elif p["status_code"] == 'T':
                item_status.setForeground(QColor("#FF8C00"))
            elif p["status_code"] == 'Z':
                item_status.setForeground(QColor("#C42B1C"))
            self.table.setItem(row, 5, item_status)

            # Threads
            item_threads = QTableWidgetItem()
            item_threads.setData(Qt.ItemDataRole.DisplayRole, p["threads"])
            self.table.setItem(row, 6, item_threads)

            # Priority
            item_prio = QTableWidgetItem()
            item_prio.setData(Qt.ItemDataRole.DisplayRole, p["priority"])
            self.table.setItem(row, 7, item_prio)

        self.table.setSortingEnabled(True)

    def _apply_filter(self):
        self.update_processes(self.process_data)

    def _get_selected_pid(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        pid_item = self.table.item(row, 0)
        return pid_item.data(Qt.ItemDataRole.DisplayRole) if pid_item else None

    def _on_new_task(self):
        dialog = ProcessControlDialog(self)
        dialog.exec()

    def _on_end_task(self):
        pid = self._get_selected_pid()
        if pid:
            ok, msg = ProcessControl.terminate_process(pid)
            QMessageBox.information(self, "Process Control", msg)

    def _on_pause_task(self):
        pid = self._get_selected_pid()
        if pid:
            ok, msg = ProcessControl.pause_process(pid)
            QMessageBox.information(self, "Process Control", msg)

    def _on_resume_task(self):
        pid = self._get_selected_pid()
        if pid:
            ok, msg = ProcessControl.resume_process(pid)
            QMessageBox.information(self, "Process Control", msg)

    def _on_inspect_task(self):
        pid = self._get_selected_pid()
        if pid:
            dialog = ProcessDetailsDialog(pid, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Process Selection", "Please select a process from the table first.")

    def _show_context_menu(self, pos):
        pid = self._get_selected_pid()
        if not pid: return

        menu = QMenu(self)
        menu.setStyleSheet("background-color: #2D2D2D; color: #FFFFFF;")

        act_end = menu.addAction("⛔ End Process (SIGTERM)")
        act_kill = menu.addAction("💀 Kill Process (SIGKILL)")
        act_pause = menu.addAction("⏸ Pause Process (SIGSTOP)")
        act_resume = menu.addAction("▶ Resume Process (SIGCONT)")
        menu.addSeparator()
        act_inspect = menu.addAction("🔍 Deep OS Inspection (/proc/maps, /proc/fd, /proc/task)")

        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == act_end:
            ProcessControl.terminate_process(pid)
        elif action == act_kill:
            ProcessControl.kill_process(pid)
        elif action == act_pause:
            ProcessControl.pause_process(pid)
        elif action == act_resume:
            ProcessControl.resume_process(pid)
        elif action == act_inspect:
            dialog = ProcessDetailsDialog(pid, self)
            dialog.exec()
