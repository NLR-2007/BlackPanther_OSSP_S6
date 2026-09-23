#include "sysmonitor_engine.h"

class DiskMonitorCPP {
public:
    disk_stats_t getStats() {
        disk_stats_t stats;
        sysmon_read_disk(&stats);
        return stats;
    }
};
