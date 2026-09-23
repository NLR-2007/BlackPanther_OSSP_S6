import time
import psutil

class NetworkMonitor:
    def __init__(self):
        self.last_time = time.time()
        self.last_net = psutil.net_io_counters()
        self.history_down = [0.0] * 60
        self.history_up = [0.0] * 60

    def get_metrics(self):
        now = time.time()
        dt = max(0.1, now - self.last_time)
        curr_net = psutil.net_io_counters()

        rx_bytes_sec = 0.0
        tx_bytes_sec = 0.0
        if curr_net and self.last_net:
            rx_bytes_sec = (curr_net.bytes_recv - self.last_net.bytes_recv) / dt
            tx_bytes_sec = (curr_net.bytes_sent - self.last_net.bytes_sent) / dt

        self.last_time = now
        self.last_net = curr_net

        down_kbps = (rx_bytes_sec * 8.0) / 1000.0
        up_kbps = (tx_bytes_sec * 8.0) / 1000.0

        # Adapter name detection
        ifaces = psutil.net_if_addrs()
        primary_adapter = "Ethernet / Wi-Fi (wlan0)"
        for iface in ifaces:
            if iface != 'lo':
                primary_adapter = iface
                break

        conn_type = "Wi-Fi (802.11ac)" if ("wlan" in primary_adapter.lower() or "wifi" in primary_adapter.lower()) else "Ethernet Adapter"

        self.history_down.append(down_kbps)
        self.history_up.append(up_kbps)
        if len(self.history_down) > 60:
            self.history_down.pop(0)
            self.history_up.pop(0)

        return {
            "adapter_name": primary_adapter,
            "connection_type": conn_type,
            "download_kbps": down_kbps,
            "upload_kbps": up_kbps,
            "total_rx_mb": curr_net.bytes_recv / (1024*1024) if curr_net else 0,
            "total_tx_mb": curr_net.bytes_sent / (1024*1024) if curr_net else 0,
            "history_down": list(self.history_down),
            "history_up": list(self.history_up)
        }
