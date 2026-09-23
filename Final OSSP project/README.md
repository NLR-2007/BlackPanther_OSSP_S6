# Smart Linux Resource Monitoring and Process Control System

A production-grade, real-time operating system monitoring dashboard and process control system designed as a high-performance Linux equivalent of the **Windows 11 Task Manager Performance and Processes tabs**.

![Task Manager Architecture](https://img.shields.io/badge/Architecture-C%20POSIX%20Engine%20%2B%20Qt6%2FPyQt6-blue)
![Platform](https://img.shields.io/badge/Platform-Linux%20%2F%20POSIX-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🏛️ System Architecture

```
                ┌──────────────────────────────────────────────┐
                │     PyQt6 / Qt6 Modern Win11 Desktop GUI    │
                │  (Sidebar Nav, Live Sparklines, 60s Area     │
                │   Graphs, Interactive Process Table & Dialogs)│
                └──────────────────────┬───────────────────────┘
                                       │ (C bindings / FFI / C++ API)
                ┌──────────────────────▼───────────────────────┐
                │     C Resource Monitoring & Control Engine    │
                │   (sysmonitor_engine.c / process_engine.c)  │
                └──────────────────────┬───────────────────────┘
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     │                                 │                                 │
┌────▼────────┐                 ┌──────▼──────┐                   ┌──────▼──────┐
│ Resource    │                 │ Process     │                   │ OS Memory/  │
│ Monitors    │                 │ Manager     │                   │ Thread/FD   │
│ (CPU, RAM,  │                 │ (fork, exec,│                   │ Analyzers   │
│ Disk, Net,  │                 │  kill, wait)│                   │ (/proc/maps,│
│ GPU)        │                 │             │                   │  /proc/fd,  │
│             │                 │             │                   │  /proc/task)│
└────┬────────┘                 └──────┬──────┘                   └──────┬──────┘
     │                                 │                                 │
┌────▼─────────────────────────────────▼─────────────────────────────────▼──────┐
│                   Linux Kernel Interfaces (/proc, /sys, POSIX APIs)           │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Course Outcome (CO) Mapping

| Course Outcome | Description | Implementation Details |
| :--- | :--- | :--- |
| **CO-1** | Linux architecture, kernel interaction, system calls, resource monitoring | Parsed directly from `/proc/stat`, `/proc/meminfo`, `/proc/diskstats`, `/proc/net/dev`, `/proc/cpuinfo`, and `sysfs` hwmon/drm nodes. Calculates delta metrics `busy_time / total_time`. |
| **CO-2** | Process monitoring, creation, termination, signals | Process creation via `fork()` and `execvp()`, process signal termination via POSIX `kill(pid, SIGTERM)` and `kill(pid, SIGKILL)`. |
| **CO-3** | IPC observation, signals, process groups | Process control using `SIGSTOP` (pause), `SIGCONT` (resume), signal handling, and process group observation. |
| **CO-4** | Memory monitoring, virtual memory, address space | Deep parsing of `/proc/[pid]/maps` to visualize process address space segments: High Address (Stack) $\rightarrow$ Heap $\rightarrow$ Data $\rightarrow$ Code (Low Address). |
| **CO-5** | File descriptors, Linux file abstraction, VFS information | Inspection of `/proc/[pid]/fd` and `/proc/[pid]/fdinfo` to list open files, stdin/stdout/stderr, sockets, pipes, and anonymous inodes. |
| **CO-6** | Threads, POSIX threads, synchronization monitoring | Thread enumeration via `/proc/[pid]/task`, per-thread CPU utilization tracking, state inspection, and POSIX `pthread_create()` / `pthread_join()` integration wrappers. |

---

## 🌟 Modules & Features

### 1. Performance Dashboard & Left Navigation Sidebar (Module 1)
- Left navigation sidebar matching Windows 11 Task Manager layout.
- Embedded **live preview sparklines** on each sidebar item ticking every second.
- Real-time telemetry cards: **CPU**, **Memory**, **Disk**, **Network**, **GPU**, and **Processes**.

### 2. CPU Monitor (Module 2)
- Live updating area chart with 60-second scrolling window (Accent: Fluent Blue `#0078D4`).
- Telemetry: Usage %, Frequency (GHz), Active Processes, Thread count, Handles/FDs, System Uptime, Logical Processors, Physical Core count.
- Delta calculation from `/proc/stat`.

### 3. Memory Monitor (Module 3)
- Live area chart with 60-second history (Accent: Purple `#8764B8`).
- Telemetry: Total RAM, Used RAM, Available RAM, Cached Memory, Swap Total/Used, Paged Pool, Non-paged Pool.
- Custom **Memory Composition Bar** showing proportional breakdown (Used vs Cached vs Available).

### 4. Disk & Storage Monitor (Module 4)
- Live disk I/O throughput graph (Read vs Write speeds in MB/s).
- Device model, Read/Write throughput, usage %, storage capacity.

### 5. Network & Interface Monitor (Module 5)
- Live network throughput dual graph (Upload & Download speeds in Kbps/Mbps).
- Active adapter name, connection type, total sent/received bytes.

### 6. GPU Monitor (Module 6)
- GPU Utilization %, VRAM Usage, Temperature (°C), Power Draw (W), Video Decode %, Video Encode %.
- Multi-vendor sysfs support (Intel Arc, AMD Radeon, NVIDIA GTX/RTX).

### 7. Process Manager & Lifecycle Visualizer (Modules 7, 8, 9)
- Interactive Process Table: PID, Process Name, User, CPU %, Memory (RSS & %), Status, Threads, Priority (Nice).
- Interactive column sorting & filter search bar.
- Process Lifecycle State Mapping:
  - `R` (Running - Green)
  - `S` (Sleeping - Blue)
  - `D` (Uninterruptible - Yellow)
  - `Z` (Zombie - Red)
  - `T` (Stopped - Orange)
- **Process Control Operations**:
  - Start New Task (`fork()` + `exec()`)
  - End Task (`SIGTERM`)
  - Kill Task (`SIGKILL`)
  - Pause Task (`SIGSTOP`)
  - Resume Task (`SIGCONT`)

### 8. Deep OS Analysis Suite (Modules 10, 11, 12, 13)
- **Virtual Memory Layout Analyzer**: Reads `/proc/[pid]/maps` and displays Stack $\rightarrow$ Heap $\rightarrow$ Data $\rightarrow$ Code segments.
- **File Descriptor & VFS Inspector**: Reads `/proc/[pid]/fd` to display FDs, socket URIs, pipes, and files.
- **Thread Monitor**: Reads `/proc/[pid]/task` to list thread IDs (TIDs), names, states, and per-thread CPU usage.
- **System Call Monitor**: Stream tracker for process system calls (`open`, `read`, `write`, `fork`, `exec`, `close`).

---

## 🛠️ Build and Execution Instructions

### Prerequisites
- GCC / C Compiler (`gcc`, `make`, `cmake`)
- Python 3.8+ with `PyQt6` and `psutil`
- Linux kernel environment with `/proc` filesystem

### Quick Start (PyQt6 Desktop Application)
```bash
# Clone or navigate to project directory
cd d:/OS-PROJECT

# Run desktop application launcher
python run_task_manager.py
```

### C Engine Dynamic Library Build
```bash
# Compile libsysmonitor.so
cd src/c_engine
make
```

### C++/Qt6 CMake Compilation
```bash
# Build native Qt6 C++ binary
mkdir build && cd build
cmake ..
make
./SmartLinuxSysMonitor
```

---

## 📂 Project Structure

```
d:/OS-PROJECT/
├── CMakeLists.txt                      # C++/Qt6 & C backend CMake configuration
├── README.md                           # Comprehensive documentation & CO mapping
├── run_task_manager.py                 # Application launcher
├── src/
│   ├── main.cpp                        # C++ Qt6 entry point
│   ├── main.py                         # Python PyQt6 entry point
│   ├── c_bridge.py                     # C Foreign Function Interface FFI loader
│   ├── c_engine/                       # Core C Linux System Programming Engine
│   │   ├── sysmonitor_engine.h         # C API header for system metrics
│   │   ├── sysmonitor_engine.c         # C implementation of procfs/sysfs/POSIX APIs
│   │   ├── process_engine.h            # C API header for process management & control
│   │   ├── process_engine.c            # C implementation for process control (fork, exec, kill, maps, fd)
│   │   └── Makefile                    # Makefile to compile libsysmonitor.so
│   ├── gui/
│   │   ├── main_window.py              # Main Window with Win11 Task Manager layout
│   │   ├── sidebar_nav.py              # Left nav sidebar with mini preview sparklines
│   │   ├── graph_widget.py             # Reusable smooth animated 60s live area graph widget
│   │   ├── cpu_view.py                 # CPU performance dashboard module
│   │   ├── memory_view.py              # Memory performance dashboard & composition bar
│   │   ├── disk_view.py                # Disk performance dashboard module
│   │   ├── network_view.py             # Network performance dashboard module
│   │   ├── gpu_view.py                 # GPU performance dashboard module
│   │   ├── process_view.py             # Process Manager table with search & sorting
│   │   ├── process_details_dialog.py   # Detailed process inspector (Memory maps, FDs, Threads, Syscalls)
│   │   └── process_control_dialog.py   # Process launcher & signal control dialog
│   ├── monitoring/
│   │   ├── cpu_monitor.py / .cpp
│   │   ├── memory_monitor.py / .cpp
│   │   ├── disk_monitor.py / .cpp
│   │   ├── network_monitor.py / .cpp
│   │   └── gpu_monitor.py / .cpp
│   ├── process/
│   │   ├── process_manager.py / .cpp
│   │   └── process_control.py / .cpp
│   ├── filesystem/
│   │   └── fd_monitor.py / .cpp
│   ├── memory/
│   │   └── memory_analyzer.py / .cpp
│   └── threads/
│       └── thread_monitor.py / .cpp
```
