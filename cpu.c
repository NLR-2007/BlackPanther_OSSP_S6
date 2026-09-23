#include "monitor.h"

/* Read aggregate CPU jiffies from /proc/stat */
static int read_cpu_times(unsigned long long *idle_out,
                          unsigned long long *total_out)
{
    FILE *fp = fopen("/proc/stat", "r");
    if (!fp) { perror("fopen /proc/stat"); return -1; }

    char label[16];
    unsigned long long user = 0, nice = 0, sys = 0, idle = 0,
                       iowait = 0, irq = 0, softirq = 0, steal = 0;

    int n = fscanf(fp, "%15s %llu %llu %llu %llu %llu %llu %llu %llu",
                   label, &user, &nice, &sys, &idle,
                   &iowait, &irq, &softirq, &steal);
    fclose(fp);

    if (n < 5) return -1;

    *idle_out  = idle + iowait;
    *total_out = user + nice + sys + idle + iowait + irq + softirq + steal;
    return 0;
}

/* Sample twice, 1 second apart, return CPU busy percentage */
double get_cpu_usage(void)
{
    unsigned long long idle1, total1, idle2, total2;

    if (read_cpu_times(&idle1, &total1) < 0) return -1.0;
    sleep(1);
    if (read_cpu_times(&idle2, &total2) < 0) return -1.0;

    unsigned long long total_diff = total2 - total1;
    unsigned long long idle_diff  = idle2  - idle1;

    if (total_diff == 0) return 0.0;
    return (double)(total_diff - idle_diff) * 100.0 / (double)total_diff;
}
