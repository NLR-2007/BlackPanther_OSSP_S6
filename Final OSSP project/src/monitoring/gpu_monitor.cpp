#include "sysmonitor_engine.h"

class GPUMonitorCPP {
public:
    gpu_stats_t getStats() {
        gpu_stats_t stats;
        sysmon_read_gpu(&stats);
        return stats;
    }
};
