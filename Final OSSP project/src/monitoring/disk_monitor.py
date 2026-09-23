import time
import psutil

class DiskMonitor:
    def __init__(self):
        self.last_time = time.time()
        self.last_io = psutil.disk_io_counters()
        self.history_read = [0.0] * 60
        self.history_write = [0.0] * 60

    def get_metrics(self):
        now = time.time()
        dt = max(0.1, now - self.last_time)
        curr_io = psutil.disk_io_counters()

        read_bytes_sec = 0.0
        write_bytes_sec = 0.0
        if curr_io and self.last_io:
            read_bytes_sec = (curr_io.read_bytes - self.last_io.read_bytes) / dt
            write_bytes_sec = (curr_io.write_bytes - self.last_io.write_bytes) / dt

        self.last_time = now
        self.last_io = curr_io

        read_mbps = read_bytes_sec / (1024 * 1024)
        write_mbps = write_bytes_sec / (1024 * 1024)

        usage = psutil.disk_usage('/')
        usage_pct = usage.percent

        self.history_read.append(read_mbps)
        self.history_write.append(write_mbps)
        if len(self.history_read) > 60:
            self.history_read.pop(0)
            self.history_write.pop(0)

        return {
            "disk_name": "SSD NVMe (System Root /)",
            "read_mbps": read_mbps,
            "write_mbps": write_mbps,
            "usage_pct": usage_pct,
            "total_gb": usage.total / (1024**3),
            "used_gb": usage.used / (1024**3),
            "free_gb": usage.free / (1024**3),
            "history_read": list(self.history_read),
            "history_write": list(self.history_write)
        }
