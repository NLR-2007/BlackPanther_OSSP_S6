#include "process_engine.h"

class ProcessManagerCPP {
public:
    int getProcesses(process_info_t **out_list, int *out_count) {
        return procmon_list_processes(out_list, out_count);
    }
};
