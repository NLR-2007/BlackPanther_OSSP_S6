#include "process_engine.h"

class MemoryAnalyzerCPP {
public:
    int getMemoryMaps(int pid, process_map_entry_t **out_maps, int *out_count) {
        return procmon_get_memory_maps(pid, out_maps, out_count);
    }
};
