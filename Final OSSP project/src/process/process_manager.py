import os
import psutil
import signal

class ProcessManager:
    def __init__(self):
        pass

    def get_process_list(self):
        processes = []
        total_ram_bytes = psutil.virtual_memory().total

        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'status', 'cpu_percent', 'memory_info', 'num_threads', 'nice']):
            try:
                pinfo = proc.info
                pid = pinfo['pid']
                name = pinfo['name'] or f"proc_{pid}"
                user = pinfo['username'] or "root"
                status_raw = pinfo['status'] or "sleeping"

                # Map state to Task Manager lifecycle pill state
                state_code, state_label = self._map_status(status_raw)

                cpu_pct = pinfo['cpu_percent'] or 0.0
                mem_rss = pinfo['memory_info'].rss if pinfo['memory_info'] else 0
                mem_pct = (mem_rss / total_ram_bytes) * 100.0
                threads = pinfo['num_threads'] or 1
                priority = pinfo['nice'] if pinfo['nice'] is not None else 0

                processes.append({
                    "pid": pid,
                    "ppid": pinfo['ppid'] or 0,
                    "name": name,
                    "user": user,
                    "status_code": state_code,
                    "status_label": state_label,
                    "cpu_pct": cpu_pct,
                    "mem_rss_mb": mem_rss / (1024 * 1024),
                    "mem_pct": mem_pct,
                    "threads": threads,
                    "priority": priority
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def _map_status(self, raw_status):
        s = str(raw_status).lower()
        if 'running' in s:
            return 'R', 'Running'
        elif 'sleeping' in s or 'idle' in s:
            return 'S', 'Sleeping'
        elif 'disk' in s or 'uninterruptible' in s:
            return 'D', 'Uninterruptible'
        elif 'zombie' in s:
            return 'Z', 'Zombie'
        elif 'stopped' in s or 'tracing' in s:
            return 'T', 'Stopped'
        else:
            return 'S', 'Sleeping'
