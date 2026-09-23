import os
import sys
import ctypes
import platform
import time

# Define C Structure Layouts in ctypes
class CPUSpec(ctypes.Structure):
    _fields_ = [
        ("usage_percent", ctypes.c_double),
        ("frequency_ghz", ctypes.c_double),
        ("active_processes", ctypes.c_uint32),
        ("active_threads", ctypes.c_uint32),
        ("active_handles", ctypes.c_uint32),
        ("uptime_seconds", ctypes.c_uint64),
        ("logical_processors", ctypes.c_uint32),
        ("physical_cores", ctypes.c_uint32),
        ("prev_user", ctypes.c_uint64),
        ("prev_nice", ctypes.c_uint64),
        ("prev_system", ctypes.c_uint64),
        ("prev_idle", ctypes.c_uint64),
        ("prev_iowait", ctypes.c_uint64),
        ("prev_irq", ctypes.c_uint64),
        ("prev_softirq", ctypes.c_uint64),
        ("prev_steal", ctypes.c_uint64),
    ]

class MemorySpec(ctypes.Structure):
    _fields_ = [
        ("total_ram_kb", ctypes.c_uint64),
        ("used_ram_kb", ctypes.c_uint64),
        ("available_ram_kb", ctypes.c_uint64),
        ("cached_ram_kb", ctypes.c_uint64),
        ("buffers_ram_kb", ctypes.c_uint64),
        ("total_swap_kb", ctypes.c_uint64),
        ("free_swap_kb", ctypes.c_uint64),
        ("used_swap_kb", ctypes.c_uint64),
        ("paged_pool_kb", ctypes.c_uint64),
        ("nonpaged_pool_kb", ctypes.c_uint64),
        ("usage_percent", ctypes.c_double),
    ]

class DiskSpec(ctypes.Structure):
    _fields_ = [
        ("disk_name", ctypes.c_char * 64),
        ("read_speed_mbps", ctypes.c_double),
        ("write_speed_mbps", ctypes.c_double),
        ("usage_percent", ctypes.c_double),
        ("total_bytes_read", ctypes.c_uint64),
        ("total_bytes_written", ctypes.c_uint64),
        ("prev_read_sectors", ctypes.c_uint64),
        ("prev_write_sectors", ctypes.c_uint64),
    ]

class NetworkSpec(ctypes.Structure):
    _fields_ = [
        ("interface_name", ctypes.c_char * 64),
        ("connection_type", ctypes.c_char * 32),
        ("upload_speed_kbps", ctypes.c_double),
        ("download_speed_kbps", ctypes.c_double),
        ("total_rx_bytes", ctypes.c_uint64),
        ("total_tx_bytes", ctypes.c_uint64),
        ("prev_rx_bytes", ctypes.c_uint64),
        ("prev_tx_bytes", ctypes.c_uint64),
    ]

class GPUSpec(ctypes.Structure):
    _fields_ = [
        ("gpu_name", ctypes.c_char * 128),
        ("utilization_percent", ctypes.c_double),
        ("memory_used_mb", ctypes.c_uint64),
        ("memory_total_mb", ctypes.c_uint64),
        ("temperature_c", ctypes.c_double),
        ("power_watts", ctypes.c_double),
        ("video_decode_percent", ctypes.c_double),
        ("video_encode_percent", ctypes.c_double),
    ]

class CEngineBridge:
    def __init__(self):
        self.lib = None
        self._load_c_library()

    def _load_c_library(self):
        lib_path = os.path.join(os.path.dirname(__file__), "c_engine", "libsysmonitor.so")
        if os.path.exists(lib_path):
            try:
                self.lib = ctypes.CDLL(lib_path)
                self.lib.sysmon_init()
            except Exception as e:
                print(f"[CEngineBridge] Could not load libsysmonitor.so: {e}")
                self.lib = None

    def get_cpu_stats():
        pass

c_bridge = CEngineBridge()
