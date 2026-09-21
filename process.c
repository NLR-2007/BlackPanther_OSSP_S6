#include "monitor.h"
#include "ui.h"

typedef struct {
    int  pid;
    int  ppid;
    long rss;
    char name[32];
    char state[20];
} ProcRow;

static int is_number(const char *s)
{
    if (!s || !*s) return 0;
    for (; *s; s++) if (!isdigit((unsigned char)*s)) return 0;
    return 1;
}

static int read_status(const char *pid, char *name, size_t nsz,
                       char *state, size_t ssz, long *rss, int *ppid)
{
    char path[288], line[512];
    snprintf(path, sizeof(path), "/proc/%s/status", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;

    snprintf(name, nsz, "?");
    snprintf(state, ssz, "?");
    *rss = 0; *ppid = 0;

    while (fgets(line, sizeof(line), fp)) {
        if (!strncmp(line, "Name:", 5))
            sscanf(line + 5, " %31s", name);
        else if (!strncmp(line, "State:", 6))
            sscanf(line + 6, " %19[^\n]", state);
        else if (!strncmp(line, "PPid:", 5))
            sscanf(line + 5, " %d", ppid);
        else if (!strncmp(line, "VmRSS:", 6))
            sscanf(line + 6, " %ld", rss);
    }
    fclose(fp);
    return 0;
}

static int cmp_mem(const void *a, const void *b)
{
    const ProcRow *x = a, *y = b;
    if (y->rss > x->rss) return 1;
    if (y->rss < x->rss) return -1;
    return 0;
}

void list_processes(void)
{
    DIR *d = opendir("/proc");
    if (!d) { ui_err("cannot open /proc"); return; }

    static ProcRow rows[4096];
    int count = 0;
    struct dirent *e;

    while ((e = readdir(d)) != NULL && count < 4096) {
        if (!is_number(e->d_name)) continue;
        ProcRow *r = &rows[count];
        if (read_status(e->d_name, r->name, sizeof(r->name),
                        r->state, sizeof(r->state), &r->rss, &r->ppid) < 0)
            continue;
        r->pid = atoi(e->d_name);
        count++;
    }
    closedir(d);

    qsort(rows, count, sizeof(ProcRow), cmp_mem);

    int show = count < 20 ? count : 20;

    printf("\n");
    ui_box_top("RUNNING PROCESSES   (top 20 by memory)");

    /* header: 7 + 1 + 7 + 1 + 18 + 1 + 12 + 1 + 9 = 57 visible chars */
    char hdr[128];
    snprintf(hdr, sizeof(hdr), "%-7s %-7s %-18s %-12s %9s",
             "PID", "PPID", "NAME", "STATE", "MEM(KB)");
    ui_row(C_BOLD "%s" C_RESET, hdr);
    ui_box_mid();

    for (int i = 0; i < show; i++) {
        ProcRow *r = &rows[i];
        const char *col = ui_state_colour(r->state);

        /* build plain part, then print state in colour separately */
        char left[64], right[32];
        snprintf(left,  sizeof(left),  "%-7d %-7d %-18.18s", r->pid, r->ppid, r->name);
        snprintf(right, sizeof(right), "%9ld", r->rss);

        ui_indent();
        printf(C_CYAN "|  " C_RESET);
        printf("%s ", left);
        printf("%s%-12.12s" C_RESET " ", col, r->state);
        printf("%s", right);
        /* visible: 33 + 1 + 12 + 1 + 9 = 56 ; avail = UI_WIDTH - 4 = 64 */
        for (int k = 56; k < UI_WIDTH - 4; k++) putchar(' ');
        printf(C_CYAN "  |" C_RESET "\n");
    }

    ui_box_mid();
    ui_row("Total processes on system : %d", count);
    ui_row("Legend : R=running  S=sleeping  D=disk-wait  T=stopped  Z=zombie");
    ui_box_bottom();
}

int print_process_details(pid_t pid)
{
    char pidstr[16], name[32], state[20];
    long rss; int ppid;
    snprintf(pidstr, sizeof(pidstr), "%d", (int)pid);

    if (read_status(pidstr, name, sizeof(name),
                    state, sizeof(state), &rss, &ppid) < 0) {
        ui_err("PID %d not found.", (int)pid);
        return -1;
    }

    printf("\n");
    ui_box_top("PROCESS DETAILS");
    ui_kv("PID",     "%d", (int)pid);
    ui_kv("PPID",    "%d", ppid);
    ui_kv("Name",    "%s", name);
    ui_kv("State",   "%s", state);
    ui_kv("Memory",  "%ld KB", rss);
    ui_kv("Source",  "/proc/%d/status", (int)pid);
    ui_box_bottom();
    return 0;
}
