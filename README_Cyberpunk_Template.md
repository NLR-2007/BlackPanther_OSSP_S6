```text
    ____  __         ______  ______                   __  __               ____  _____ 
   / __ )/ /___ ____/ / __ \/ __  /____  ____  _____ / /_/ /_  ___  _____ / __ \/ ___/ 
  / __  / / __ `/ ___/ /_/ / /_/ / __  / __ `/ __  // __/ __ \/ _ \/ ___// / / /\__ \  
 / /_/ / / /_/ / /__/ ____/ __  / /_/ / /_/ / / / // /_/ / / /  __/ /   / /_/ /___/ /  
/_____/_/\__,_/\___/_/   /_/ /_/\__,_/\__,_/_/ /_/ \__/_/ /_/\___/_/    \____//____/   
                                                                                       
            -- BLACKPANTHER OPERATING SYSTEM (OSSP - SEMESTER 6) --
```

# ⚡ BLACKPANTHER OS - CORE KERNEL DOCUMENTATION

<p align="left">
  <img src="https://img.shields.io/badge/Kernel-x86__32_Monolithic-00ffcc?style=for-the-badge&logo=linux&logoColor=black"/>
  <img src="https://img.shields.io/badge/Scheduler-Preemptive_Round--Robin-ff0055?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Memory-Paging_2__Level-7000ff?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Production_Ready-00ff66?style=for-the-badge"/>
</p>

---

## ⚡ EXECUTIVE SUMMARY

**BlackPanther OS** is a custom x86 32-bit operating system kernel developed for **OSSP Semester 6**. Designed from bare metal up to Ring 0 Protected Mode, it integrates full memory paging, preemptive context switching, system call interface (`INT 0x80`), and an in-memory Virtual File System (Initrd).

```
+-------------------------------------------------------------------------+
|                              USER LAND                                  |
|         BlackPanther CLI Shell | User Utilities | User Binaries        |
+-------------------------------------------------------------------------+
                                    || INT 0x80 System Call Interface
+-------------------------------------------------------------------------+
|                              KERNEL SPACE                               |
|   +-------------------+  +-------------------+  +-------------------+   |
|   |  PMM & VMM Engine |  |  Round-Robin      |  |  Virtual File     |   |
|   |  (Paging / Heap)  |  |  Scheduler (PCB)  |  |  System (Initrd)  |   |
|   +-------------------+  +-------------------+  +-------------------+   |
|   +-----------------------------------------------------------------+   |
|   |          IDT / ISR / IRQ Interrupt Handlers & Timer Driver       |   |
|   +-----------------------------------------------------------------+   |
+-------------------------------------------------------------------------+
                                    || Hardware Abstraction Layer
+-------------------------------------------------------------------------+
|                             HARDWARE LAYER                              |
|           x86 CPU  |  8254 PIT Timer  |  VGA Display  |  PS/2 Keyboard   |
+-------------------------------------------------------------------------+
```

---

## 🧬 KERNEL SUBSYSTEMS

### 1. Bootstrapping & Hardware Setup
- **Multiboot Entry**: Header located within first 8KB of kernel ELF binary.
- **GDT Configuration**: Null Descriptor, 4GB Kernel Code (0x08), 4GB Kernel Data (0x10), User Code (0x18), User Data (0x20).
- **IDT Remap**: Vector mapping for CPU Exceptions (0-31), IRQ Hardware (32-47), Syscalls (128 / 0x80).

### 2. Memory Engineering
- **Physical Allocation**: 4KB page frame bitmap tracking system RAM.
- **Virtual Memory Paging**: Identity-mapped kernel page table + dynamically allocated page directories.
- **Kernel Heap**: `kmalloc(size)` & `kfree(ptr)` with boundary tag allocation.

### 3. Task Management & Syscalls
- **Preemptive Engine**: Interrupt 0x20 tick context switcher saving EAX, EBX, ECX, EDX, ESI, EDI, EBP, ESP.
- **System Call Table**:
  - `0x01`: `sys_exit`
  - `0x02`: `sys_fork`
  - `0x03`: `sys_read`
  - `0x04`: `sys_write`
  - `0x05`: `sys_open`
  - `0x0B`: `sys_execve`

---

## 🚀 COMPILATION & EXECUTION INSTRUCTIONS

```bash
# Clone repository
git clone https://github.com/NLR-2007/BlackPanther_OSSP_S6.git
cd BlackPanther_OSSP_S6

# Build kernel ELF binary
make

# Boot inside QEMU emulator
make run-qemu

# Clean build artifacts
make clean
```

---

## 👨‍💻 TEAM MEMBERS & AUTHORSHIP

```
+---------------------------------------------------------------------------------------+
|  STUDENT NAME           | REGISTRATION NO | PRIMARY SUBSYSTEM RESPONSIBILITY          |
+-------------------------+-----------------+-------------------------------------------+
| Nimma Lokesh Reddy      | 2520030366      | Kernel Boot, GDT, IDT & Syscall Handler   |
| Ramagiri Rishik Rao     | 2520030333      | Memory Allocators (PMM, VMM, Kernel Heap) |
| Gaddam Sriram Reddy     | 2520030218      | Preemptive Scheduler, VFS & Shell Driver  |
+---------------------------------------------------------------------------------------+
```

---
*BlackPanther OS - OSSP S6 Project Repository*
