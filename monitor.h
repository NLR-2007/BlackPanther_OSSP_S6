#ifndef MONITOR_H
#define MONITOR_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <errno.h>
#include <signal.h>
#include <dirent.h>
#include <fcntl.h>
#include <time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>

/* ---- cpu.c ---- */
double get_cpu_usage(void);

/* ---- memory.c ---- */
typedef struct {
    long total_kb;
    long available_kb;
    long used_kb;
    double used_percent;
    long swap_total_kb;
    long swap_used_kb;
} MemInfo;

int  get_memory_info(MemInfo *m);
void print_memory_info(void);

/* ---- process.c ---- */
void list_processes(void);
int  print_process_details(pid_t pid);

/* ---- process_control.c ---- */
int process_exists(pid_t pid);
void terminate_process(pid_t pid);
void kill_process(pid_t pid);
void stop_process(pid_t pid);
void continue_process(pid_t pid);
void signal_process_group(pid_t pgid, int sig);

/* ---- main.c helpers ---- */
void read_line(char *buf, size_t n);

#endif /* MONITOR_H */
