# BlackPanther OS: A 32-Bit Multitasking Kernel Design
**Course:** Operating Systems & Systems Programming (OSSP — Semester 6)  
**Repository:** [github.com/NLR-2007/BlackPanther_OSSP_S6](https://github.com/NLR-2007/BlackPanther_OSSP_S6.git)  

---

## Abstract

BlackPanther OS is a monolithic 32-bit x86 operating system kernel implemented in C and Assembly. It serves as a foundational platform for studying low-level hardware abstraction, paging-based virtual memory management, interrupt-driven I/O, preemptive scheduling, and POSIX-compatible system call dispatching.

---

## Authors & Project Team

* **Nimma Lokesh Reddy** (Reg No: `2520030366`) — *Lead Systems Engineer*  
  Architecture, Multiboot Header, GDT/IDT Initialization, Interrupt Handling (`INT 0x80`).
* **Ramagiri Rishik Rao** (Reg No: `2520030333`) — *Memory Management Specialist*  
  Physical Frame Bitmap Allocator, 2-Level Paging Engine, Kernel Heap (`kmalloc`/`kfree`).
* **Gaddam Sriram Reddy** (Reg No: `2520030218`) — *Scheduler & Drivers Specialist*  
  Preemptive Round-Robin Task Scheduler, Virtual File System (Initrd), VGA & PS/2 Keyboard Drivers.

---

## Key System Modules

### 1. Bootstrapping & Core Descriptor Tables
* **Multiboot Compliance:** Boots directly via GRUB/QEMU bootloaders into 32-bit flat memory model.
* **GDT & IDT:** Configures code/data segment descriptors, Task State Segment (TSS), and 48 interrupt service routine (ISR) gates.

### 2. Memory Subsystem
* **Physical Memory Manager (PMM):** Manages 4KB memory frames using a high-density bitmap array.
* **Virtual Memory Manager (VMM):** Implements page directories and page tables to map virtual to physical addresses.
* **Heap Management:** Dynamic memory pool chunking supporting variable-size runtime kernel allocations.

### 3. Concurrency & Preemption
* **Process Control Block (PCB):** Maintains process states (`READY`, `RUNNING`, `BLOCKED`, `TERMINATED`), register contexts, and stack pointers.
* **Scheduler:** Timer-driven (PIT 8254 @ 100Hz) Round-Robin preemptive context switcher.

---

## Getting Started

### Requirements
* `i686-elf-gcc` or `gcc` (with `-m32` support)
* `nasm` (Netwide Assembler)
* `qemu-system-i386`
* `make`

### Building & Execution

```bash
# Clone the repository
git clone https://github.com/NLR-2007/BlackPanther_OSSP_S6.git
cd BlackPanther_OSSP_S6

# Build kernel ELF image
make all

# Run in QEMU
make qemu
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
