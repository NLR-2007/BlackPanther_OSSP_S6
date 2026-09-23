#include "process_engine.h"

class FDMonitorCPP {
public:
    int getFDs(int pid, process_fd_entry_t **out_fds, int *out_count) {
        return procmon_get_file_descriptors(pid, out_fds, out_count);
    }
};
