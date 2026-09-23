#ifndef SYSMONITOR_ENGINE_H
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#define SYSMONITOR_ENGINE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

// CPU Statistics Structure
typedef struct {
    double usage_percent;
    double frequency_ghz;
    uint32_t active_processes;
    uint32_t active_threads;
    uint32_t active_handles;
    uint64_t uptime_seconds;
    uint32_t logical_processors;
    uint32_t physical_cores;
    uint64_t prev_user;
    uint64_t prev_nice;
    uint64_t prev_system;
    uint64_t prev_idle;
    uint64_t prev_iowait;
    uint64_t prev_irq;
    uint64_t prev_softirq;
    uint64_t prev_steal;
} cpu_stats_t;

// Memory Statistics Structure
typedef struct {
    uint64_t total_ram_kb;
    uint64_t used_ram_kb;
    uint64_t available_ram_kb;
    uint64_t cached_ram_kb;
    uint64_t buffers_ram_kb;
    uint64_t total_swap_kb;
    uint64_t free_swap_kb;
    uint64_t used_swap_kb;
    uint64_t paged_pool_kb;
    uint64_t nonpaged_pool_kb;
    double usage_percent;
} memory_stats_t;

// Disk Statistics Structure
typedef struct {
    char disk_name[64];
    double read_speed_mbps;
    double write_speed_mbps;
    double usage_percent;
    uint64_t total_bytes_read;
    uint64_t total_bytes_written;
    uint64_t prev_read_sectors;
    uint64_t prev_write_sectors;
    struct timespec prev_time;
} disk_stats_t;

// Network Statistics Structure
typedef struct {
    char interface_name[64];
    char connection_type[32];
    double upload_speed_kbps;
    double download_speed_kbps;
    uint64_t total_rx_bytes;
    uint64_t total_tx_bytes;
    uint64_t prev_rx_bytes;
    uint64_t prev_tx_bytes;
    struct timespec prev_time;
} network_stats_t;

// GPU Statistics Structure
typedef struct {
    char gpu_name[128];
    double utilization_percent;
    uint64_t memory_used_mb;
    uint64_t memory_total_mb;
    double temperature_c;
    double power_watts;
    double video_decode_percent;
    double video_encode_percent;
} gpu_stats_t;

// C Engine API Functions
int sysmon_init(void);
int sysmon_read_cpu(cpu_stats_t *stats);
int sysmon_read_memory(memory_stats_t *stats);
int sysmon_read_disk(disk_stats_t *stats);
int sysmon_read_network(network_stats_t *stats);
int sysmon_read_gpu(gpu_stats_t *stats);

#ifdef __cplusplus
}
#endif

#endif // SYSMONITOR_ENGINE_H
