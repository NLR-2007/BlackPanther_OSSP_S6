#include "sysmonitor_engine.h"

class MemoryMonitorCPP {
public:
    memory_stats_t getStats() {
        memory_stats_t stats;
        sysmon_read_memory(&stats);
        return stats;
    }
};
