#!/usr/bin/env python3
import sys
import os
import time
import signal

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.monitoring.cpu_monitor import CPUMonitor
from src.monitoring.memory_monitor import MemoryMonitor
from src.monitoring.disk_monitor import DiskMonitor
from src.monitoring.network_monitor import NetworkMonitor
from src.monitoring.gpu_monitor import GPUMonitor
from src.process.process_manager import ProcessManager
from src.process.process_control import ProcessControl
from src.memory.memory_analyzer import MemoryAnalyzer
from src.filesystem.fd_monitor import FDMonitor
from src.threads.thread_monitor import ThreadMonitor

# ANSI Color Codes
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_BLUE = "\033[1;34m"
CLR_CYAN = "\033[1;36m"
CLR_PURPLE = "\033[1;35m"
CLR_GREEN = "\033[1;32m"
CLR_YELLOW = "\033[1;33m"
CLR_RED = "\033[1;31m"
CLR_BG_DARK = "\033[40m"

def render_bar(pct, width=25, color=CLR_BLUE):
    fill = int(width * (max(0.0, min(100.0, pct)) / 100.0))
    bar = "█" * fill + "░" * (width - fill)
    return f"{color}[{bar}]{CLR_RESET} {pct:5.1f}%"

def clear_screen():
    print("\033[H\033[J", end="")

def run_cli_dashboard():
    cpu_mon = CPUMonitor()
    mem_mon = MemoryMonitor()
    disk_mon = DiskMonitor()
    net_mon = NetworkMonitor()
    gpu_mon = GPUMonitor()
    proc_mon = ProcessManager()

    print("Starting Smart Linux Task Manager Terminal Dashboard... (Press Ctrl+C to exit)")
    time.sleep(1)

    try:
        while True:
            clear_screen()
            print(f"{CLR_BOLD}{CLR_CYAN}========================================================================================{CLR_RESET}")
            print(f"{CLR_BOLD}{CLR_CYAN}  SMART LINUX RESOURCE MONITOR & PROCESS CONTROL SYSTEM (UBUNTU TERMINAL DASHBOARD)    {CLR_RESET}")
            print(f"{CLR_BOLD}{CLR_CYAN}========================================================================================{CLR_RESET}")

            # 1. CPU
            cpu = cpu_mon.get_metrics()
            print(f"{CLR_BOLD}CPU Usage:   {CLR_RESET} {render_bar(cpu['usage'], color=CLR_BLUE)}  Freq: {CLR_YELLOW}{cpu['frequency_ghz']:.2f} GHz{CLR_RESET}  Cores: {cpu['cores']}/{cpu['logical_processors']}  Procs: {cpu['processes']}  Threads: {cpu['threads']}")

            # 2. Memory
            mem = mem_mon.get_metrics()
            print(f"{CLR_BOLD}Memory RAM:  {CLR_RESET} {render_bar(mem['usage_pct'], color=CLR_PURPLE)}  Used: {CLR_PURPLE}{mem['used_gb']:.1f}/{mem['total_gb']:.1f} GB{CLR_RESET}  Cached: {mem['cached_gb']:.1f} GB  Swap: {mem['swap_used_gb']:.1f} GB")

            # 3. Disk & Network
            disk = disk_mon.get_metrics()
            net = net_mon.get_metrics()
            print(f"{CLR_BOLD}Disk I/O:    {CLR_RESET} {CLR_GREEN}Read: {disk['read_mbps']:.1f} MB/s{CLR_RESET} | {CLR_YELLOW}Write: {disk['write_mbps']:.1f} MB/s{CLR_RESET}  Device: {disk['disk_name']}")
            print(f"{CLR_BOLD}Network:     {CLR_RESET} {CLR_RED}Send: {net['upload_kbps']:.0f} Kbps{CLR_RESET} | {CLR_CYAN}Recv: {net['download_kbps']:.0f} Kbps{CLR_RESET}  Adapter: {net['adapter_name']}")

            # 4. GPU
            gpu = gpu_mon.get_metrics()
            print(f"{CLR_BOLD}GPU Util:    {CLR_RESET} {render_bar(gpu['utilization_pct'], color=CLR_YELLOW)}  VRAM: {gpu['vram_used_mb']/1024:.1f}/{gpu['vram_total_mb']/1024:.1f} GB  Temp: {gpu['temperature_c']}°C")

            print(f"\n{CLR_BOLD}{CLR_BLUE}--- TOP PROCESSES BY CPU & MEMORY (/proc/[pid]) ----------------------------------------{CLR_RESET}")
            print(f"{CLR_BOLD}{'PID':<7} {'NAME':<20} {'USER':<10} {'CPU %':<8} {'MEM (MB)':<10} {'STATE':<14} {'THREADS':<8}{CLR_RESET}")
            print("-" * 88)

            procs = proc_mon.get_process_list()
            procs.sort(key=lambda x: x['cpu_pct'], reverse=True)

            for p in procs[:10]:
                st_color = CLR_GREEN if p['status_code'] == 'R' else CLR_BLUE if p['status_code'] == 'S' else CLR_RED
                st_str = f"{st_color}[{p['status_code']}] {p['status_label']}{CLR_RESET}"
                print(f"{p['pid']:<7} {p['name'][:19]:<20} {p['user'][:9]:<10} {p['cpu_pct']:<8.1f} {p['mem_rss_mb']:<10.1f} {st_str:<23} {p['threads']:<8}")

            print(f"\n{CLR_BOLD}Controls:{CLR_RESET} [q] Quit  | Run GUI version using: {CLR_CYAN}python3 run_task_manager.py{CLR_RESET}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting Terminal Dashboard. Goodbye!")

if __name__ == "__main__":
    run_cli_dashboard()
