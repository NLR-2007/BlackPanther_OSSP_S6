#ifndef PROCESS_ENGINE_H
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#define PROCESS_ENGINE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <signal.h>

#ifdef __cplusplus
extern "C" {
#endif

// Process State Enum (Module 9)
typedef enum {
    PROC_STATE_RUNNING,       // R - Running
    PROC_STATE_SLEEPING,      // S - Sleeping
    PROC_STATE_UNINTERRUPTIBLE,// D - Disk / Uninterruptible Sleep
    PROC_STATE_STOPPED,       // T - Stopped
    PROC_STATE_ZOMBIE,        // Z - Zombie
    PROC_STATE_UNKNOWN
} process_state_e;

// Process Information Structure (Module 7)
typedef struct {
    int pid;
    int ppid;
    char name[256];
    char user[64];
    char state_char;
    process_state_e state;
    char state_label[32];
    uint32_t threads;
    int priority; // Nice value (-20 to 19)
    double cpu_percent;
    uint64_t mem_rss_kb;
    uint64_t mem_virt_kb;
    double mem_percent;
} process_info_t;

// Process Memory Map Entry (Module 10)
typedef struct {
    uint64_t start_addr;
    uint64_t end_addr;
    char perms[8];
    uint64_t offset;
    char dev[16];
    uint64_t inode;
    char pathname[256];
    char region_type[32]; // High Address (Stack), Heap, Data, Code
} process_map_entry_t;

// File Descriptor Entry (Module 11)
typedef struct {
    int fd;
    char type[32]; // File, Socket, Pipe, Anon, Char
    char path[512];
} process_fd_entry_t;

// Thread Info Entry (Module 12)
typedef struct {
    int tid;
    char name[128];
    char state_char;
    double cpu_percent;
} process_thread_entry_t;

// System Call Record (Module 13)
typedef struct {
    char syscall_name[64];
    char timestamp[32];
    char details[256];
    int return_code;
} syscall_record_t;

// C Engine API Functions for Process Control & Inspection
int procmon_list_processes(process_info_t **out_list, int *out_count);
void procmon_free_process_list(process_info_t *list);

int procmon_send_signal(int pid, int sig);
int procmon_terminate_process(int pid);
int procmon_kill_process(int pid);
int procmon_pause_process(int pid);
int procmon_resume_process(int pid);
int procmon_launch_process(const char *command);

int procmon_get_memory_maps(int pid, process_map_entry_t **out_maps, int *out_count);
void procmon_free_memory_maps(process_map_entry_t *maps);

int procmon_get_file_descriptors(int pid, process_fd_entry_t **out_fds, int *out_count);
void procmon_free_file_descriptors(process_fd_entry_t *fds);

int procmon_get_threads(int pid, process_thread_entry_t **out_threads, int *out_count);
void procmon_free_threads(process_thread_entry_t *threads);

int procmon_get_syscall_trace(int pid, syscall_record_t **out_records, int *out_count);
void procmon_free_syscall_trace(syscall_record_t *records);

#ifdef __cplusplus
}
#endif

#endif // PROCESS_ENGINE_H
