import time
import os
import psutil
from src.c_bridge import c_bridge, CPUSpec

class CPUMonitor:
    def __init__(self):
        self.c_stats = CPUSpec()
        self.history = [0.0] * 60

    def get_metrics(self):
        if c_bridge.lib and hasattr(c_bridge, 'c_stats'):
            try:
                c_bridge.lib.sysmon_read_cpu(c_bridge.c_stats)
                usage = c_bridge.c_stats.usage_percent
                freq = c_bridge.c_stats.frequency_ghz
                proc_count = c_bridge.c_stats.active_processes
                threads = c_bridge.c_stats.active_threads
                handles = c_bridge.c_stats.active_handles
                uptime = c_bridge.c_stats.uptime_seconds
                log_cpus = c_bridge.c_stats.logical_processors
                cores = c_bridge.c_stats.physical_cores
            except Exception:
                usage, freq, proc_count, threads, handles, uptime, log_cpus, cores = self._fallback_metrics()
        else:
            usage, freq, proc_count, threads, handles, uptime, log_cpus, cores = self._fallback_metrics()

        self.history.append(usage)
        if len(self.history) > 60:
            self.history.pop(0)

        return {
            "usage": usage,
            "frequency_ghz": freq,
            "processes": proc_count,
            "threads": threads,
            "handles": handles,
            "uptime_sec": uptime,
            "logical_processors": log_cpus,
            "cores": cores,
            "history": list(self.history)
        }

    def _fallback_metrics(self):
        usage = psutil.cpu_percent(interval=None)
        freq_info = psutil.cpu_freq()
        freq = (freq_info.current / 1000.0) if freq_info and freq_info.current else 2.40
        proc_count = len(psutil.pids())
        
        threads = 0
        handles = 0
        for p in psutil.process_iter(['num_threads']):
            try:
                threads += p.info.get('num_threads') or 1
                try:
                    handles += p.num_fds() if hasattr(p, 'num_fds') else (p.num_handles() if hasattr(p, 'num_handles') else 5)
                except Exception:
                    handles += 5
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if threads == 0: threads = proc_count * 8
        if handles == 0: handles = proc_count * 25
        
        try:
            uptime = int(time.time() - psutil.boot_time())
        except Exception:
            uptime = 86400

        log_cpus = psutil.cpu_count(logical=True) or 8
        cores = psutil.cpu_count(logical=False) or 4
        return usage, freq, proc_count, threads, handles, uptime, log_cpus, cores
