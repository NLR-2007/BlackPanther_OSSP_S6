#include "sysmonitor_engine.h"

class NetworkMonitorCPP {
public:
    network_stats_t getStats() {
        network_stats_t stats;
        sysmon_read_network(&stats);
        return stats;
    }
};
