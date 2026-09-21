#include "monitor.h"
#include "ui.h"

static long read_field(const char *line, const char *key)
{
    size_t klen = strlen(key);
    if (strncmp(line, key, klen) != 0) return -1;
    long val = -1;
    sscanf(line + klen, " %ld", &val);
    return val;
}

int get_memory_info(MemInfo *m)
{
    FILE *fp = fopen("/proc/meminfo", "r");
    if (!fp) { perror("fopen /proc/meminfo"); return -1; }

    char line[256];
    long v;
    memset(m, 0, sizeof(*m));

    while (fgets(line, sizeof(line), fp)) {
        if ((v = read_field(line, "MemTotal:")) >= 0) m->total_kb = v;
        else if ((v = read_field(line, "MemAvailable:")) >= 0) m->available_kb = v;
        else if ((v = read_field(line, "SwapTotal:")) >= 0) m->swap_total_kb = v;
        else if ((v = read_field(line, "SwapFree:")) >= 0) m->swap_used_kb = v;
    }
    fclose(fp);

    if (m->total_kb <= 0) return -1;

    m->swap_used_kb  = m->swap_total_kb - m->swap_used_kb;
    m->used_kb       = m->total_kb - m->available_kb;
    m->used_percent  = (double)m->used_kb * 100.0 / (double)m->total_kb;
    return 0;
}

void print_memory_info(void)
{
    MemInfo m;
    printf("\n");
    if (get_memory_info(&m) < 0) {
        ui_err("Unable to read /proc/meminfo");
        return;
    }

    ui_box_top("MEMORY USAGE  (source: /proc/meminfo)");
    ui_kv("Total RAM",     "%8.2f MB", m.total_kb     / 1024.0);
    ui_kv("Used RAM",      "%8.2f MB", m.used_kb      / 1024.0);
    ui_kv("Available RAM", "%8.2f MB", m.available_kb / 1024.0);
    ui_box_mid();
    ui_bar("RAM", m.used_percent);
    if (m.swap_total_kb > 0) {
        double sp = (double)m.swap_used_kb * 100.0 / (double)m.swap_total_kb;
        ui_bar("SWAP", sp);
        ui_kv("Swap Used", "%8.2f MB / %.2f MB",
              m.swap_used_kb / 1024.0, m.swap_total_kb / 1024.0);
    }
    ui_box_bottom();
}
