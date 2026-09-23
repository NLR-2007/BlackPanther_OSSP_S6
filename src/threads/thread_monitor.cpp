#include "process_engine.h"

class ThreadMonitorCPP {
public:
    int getThreads(int pid, process_thread_entry_t **out_threads, int *out_count) {
        return procmon_get_threads(pid, out_threads, out_count);
    }
};
