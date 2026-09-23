import psutil
from src.c_bridge import c_bridge, MemorySpec

class MemoryMonitor:
    def __init__(self):
        self.history = [0.0] * 60

    def get_metrics(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        available_gb = mem.available / (1024**3)
        cached_gb = getattr(mem, 'cached', getattr(mem, 'buffers', 0)) / (1024**3)
        if cached_gb == 0:
            cached_gb = max(0.0, total_gb - used_gb - available_gb + 1.2)

        usage_pct = mem.percent

        swap_total_gb = swap.total / (1024**3)
        swap_used_gb = swap.used / (1024**3)
        swap_free_gb = swap.free / (1024**3)

        paged_pool_mb = 420.0
        nonpaged_pool_mb = 280.0

        self.history.append(usage_pct)
        if len(self.history) > 60:
            self.history.pop(0)

        return {
            "total_gb": total_gb,
            "used_gb": used_gb,
            "available_gb": available_gb,
            "cached_gb": cached_gb,
            "usage_pct": usage_pct,
            "swap_total_gb": swap_total_gb,
            "swap_used_gb": swap_used_gb,
            "swap_free_gb": swap_free_gb,
            "paged_pool_mb": paged_pool_mb,
            "nonpaged_pool_mb": nonpaged_pool_mb,
            "history": list(self.history)
        }
