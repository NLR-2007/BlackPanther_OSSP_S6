#include "sysmonitor_engine.h"

class CPUMonitorCPP {
public:
    cpu_stats_t getStats() {
        cpu_stats_t stats;
        sysmon_read_cpu(&stats);
        return stats;
    }
};
