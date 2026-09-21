#include "monitor.h"
#include "ui.h"

#define LOGFILE "monitor.log"

static volatile sig_atomic_t g_interrupted = 0;
static pid_t g_bg_pid = -1;

/* ==================== CO-3 : signal handlers ==================== */

static void on_sigint(int sig)
{
    (void)sig;
    g_interrupted = 1;
    const char *msg = "\n  [SIGINT caught safely]\n";
    write(STDOUT_FILENO, msg, strlen(msg));
}

static void on_sigchld(int sig)
{
    (void)sig;
    int saved = errno, status;
    pid_t p;
    while ((p = waitpid(-1, &status, WNOHANG)) > 0) {
        if (p == g_bg_pid) g_bg_pid = -1;
    }
    errno = saved;
}

static void on_sigusr1(int sig)
{
    (void)sig;
    const char *msg = "\n  [SIGUSR1] custom user signal received.\n";
    write(STDOUT_FILENO, msg, strlen(msg));
}

static void install_handlers(void)
{
    struct sigaction sa;

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_sigint;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_sigchld;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    sigaction(SIGCHLD, &sa, NULL);

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_sigusr1;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGUSR1, &sa, NULL);

    signal(SIGPIPE, SIG_IGN);
}

/* ==================== input ==================== */

void read_line(char *buf, size_t n)
{
    if (!fgets(buf, n, stdin)) {
        clearerr(stdin);
        buf[0] = '\0';
        return;
    }
    buf[strcspn(buf, "\n")] = '\0';
}

static void pause_enter(void)
{
    char t[8];
    printf("\n");
    ui_center(C_DIM "press ENTER to return to the menu..." C_RESET);
    fflush(stdout);
    read_line(t, sizeof(t));
    g_interrupted = 0;
}

/* ============ CO-2 : fork + pipe + waitpid (single sample) ============ */

static void cpu_usage_via_child(void)
{
    int fd[2];
    if (pipe(fd) == -1) { ui_err("pipe() failed"); return; }

    sigset_t block, old;
    sigemptyset(&block); sigaddset(&block, SIGCHLD);
    sigprocmask(SIG_BLOCK, &block, &old);

    pid_t pid = fork();
    if (pid < 0) {
        ui_err("fork() failed");
        close(fd[0]); close(fd[1]);
        sigprocmask(SIG_SETMASK, &old, NULL);
        return;
    }

    if (pid == 0) {                         /* ---- CHILD ---- */
        close(fd[0]);
        double usage = get_cpu_usage();
        char b[64];
        int len = snprintf(b, sizeof(b), "%.2f", usage);
        write(fd[1], b, len);
        close(fd[1]);
        _exit(0);
    }

    /* ---- PARENT ---- */
    close(fd[1]);
    printf("\n");
    ui_info("parent pid=%d  forked child pid=%d", (int)getpid(), (int)pid);

    char buf[64] = {0};
    ssize_t r = read(fd[0], buf, sizeof(buf) - 1);
    close(fd[0]);

    int status;
    waitpid(pid, &status, 0);
    sigprocmask(SIG_SETMASK, &old, NULL);

    printf("\n");
    ui_box_top("CPU USAGE   (source: /proc/stat)");
    if (r > 0) {
        buf[r] = '\0';
        double usage = atof(buf);
        if (usage < 0) {
            ui_row("CPU counters did not advance during the sample window.");
        } else {
            ui_bar("CPU", usage);
            ui_box_mid();
            ui_kv("Sample window",  "1 second (two /proc/stat reads)");
            ui_kv("IPC mechanism",  "pipe()  child -> parent");
        }
    } else {
        ui_row("No data received from the child process.");
    }
    ui_box_mid();
    ui_kv("Parent PID", "%d", (int)getpid());
    ui_kv("Child PID",  "%d", (int)pid);
    if (WIFEXITED(status))
        ui_kv("Child exit status", "%d  (reaped by waitpid)", WEXITSTATUS(status));
    ui_box_bottom();
}

/* ========== CO-2 + CO-3 : LIVE DASHBOARD (streaming pipe) ========== */

static void live_dashboard(void)
{
    int fd[2];
    if (pipe(fd) == -1) { ui_err("pipe() failed"); return; }

    sigset_t block, old;
    sigemptyset(&block); sigaddset(&block, SIGCHLD);
    sigprocmask(SIG_BLOCK, &block, &old);

    pid_t pid = fork();
    if (pid < 0) {
        ui_err("fork() failed");
        close(fd[0]); close(fd[1]);
        sigprocmask(SIG_SETMASK, &old, NULL);
        return;
    }

    if (pid == 0) {                         /* ---- CHILD : sampler ---- */
        close(fd[0]);
        signal(SIGINT, SIG_IGN);
        for (;;) {
            double cpu = get_cpu_usage();
            MemInfo m;
            if (get_memory_info(&m) < 0) break;
            char line[192];
            int n = snprintf(line, sizeof(line), "%.2f %.2f %ld %ld\n",
                             cpu, m.used_percent, m.used_kb, m.total_kb);
            if (write(fd[1], line, n) <= 0) break;
        }
        close(fd[1]);
        _exit(0);
    }

    /* ---- PARENT : renderer ---- */
    close(fd[1]);
    FILE *in = fdopen(fd[0], "r");
    if (!in) { ui_err("fdopen failed"); close(fd[0]); return; }

    g_interrupted = 0;
    ui_cursor_hide();

    char line[256];
    double cpu = 0, memp = 0;
    long used = 0, total = 0;
    int ticks = 0;

    while (!g_interrupted) {
        if (!fgets(line, sizeof(line), in)) {
            if (errno == EINTR) { clearerr(in); continue; }
            break;
        }
        if (sscanf(line, "%lf %lf %ld %ld", &cpu, &memp, &used, &total) != 4)
            continue;
        ticks++;

        time_t now = time(NULL);
        char ts[64];
        strftime(ts, sizeof(ts), "%Y-%m-%d  %H:%M:%S", localtime(&now));

        ui_clear();
        ui_banner();
        printf("\n");

        ui_box_top("LIVE DASHBOARD   (child streams via pipe)");
        ui_kv("Timestamp",        "%s", ts);
        ui_kv("Samples received", "%d", ticks);
        ui_box_mid();
        ui_bar("CPU", cpu);
        ui_bar("RAM", memp);
        ui_box_mid();
        ui_kv("RAM used",      "%.1f MB  /  %.1f MB", used / 1024.0, total / 1024.0);
        ui_kv("Parent PID",    "%d  (renderer)", (int)getpid());
        ui_kv("Sampler child", "%d  (writes to pipe)", (int)pid);
        ui_box_bottom();

        printf("\n");
        ui_center(C_DIM "press Ctrl+C to stop and return to the menu" C_RESET);
        printf("\n");
        fflush(stdout);
    }

    ui_cursor_show();
    fclose(in);
    kill(pid, SIGTERM);
    int status;
    waitpid(pid, &status, 0);
    sigprocmask(SIG_SETMASK, &old, NULL);
    g_interrupted = 0;

    printf("\n");
    ui_ok("Dashboard stopped. Child %d reaped (terminated by signal %d).",
          (int)pid, WIFSIGNALED(status) ? WTERMSIG(status) : 0);
}

/* ============ CO-3 : background monitor + process group ============ */

static void start_background_monitor(void)
{
    if (g_bg_pid > 0 && process_exists(g_bg_pid)) {
        ui_info("Background monitor already running (PID %d).", (int)g_bg_pid);
        return;
    }

    pid_t pid = fork();
    if (pid < 0) { ui_err("fork() failed"); return; }

    if (pid == 0) {
        setpgid(0, 0);                 /* own process group */
        signal(SIGINT, SIG_IGN);       /* survive terminal Ctrl+C */

        FILE *log = fopen(LOGFILE, "a");
        if (!log) _exit(1);
        setvbuf(log, NULL, _IOLBF, 0);

        for (;;) {
            double cpu = get_cpu_usage();
            MemInfo m;
            get_memory_info(&m);
            time_t now = time(NULL);
            char ts[64];
            strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", localtime(&now));
            fprintf(log, "[%s]  CPU=%6.2f%%   MEM=%6.2f%%   USED=%8.1f MB\n",
                    ts, cpu, m.used_percent, m.used_kb / 1024.0);
            sleep(4);
        }
    }

    setpgid(pid, pid);
    g_bg_pid = pid;

    printf("\n");
    ui_box_top("BACKGROUND MONITOR STARTED");
    ui_kv("Child PID",     "%d", (int)pid);
    ui_kv("Process group", "%d  (separate PGID)", (int)pid);
    ui_kv("Log file",      "%s", LOGFILE);
    ui_kv("Sample period", "4 seconds");
    ui_box_mid();
    ui_row("Watch it live with :  tail -f %s", LOGFILE);
    ui_row("Inspect group with :  ps -o pid,ppid,pgid,stat,cmd -p %d", (int)pid);
    ui_box_bottom();
}

static void stop_background_monitor(void)
{
    if (g_bg_pid <= 0) { ui_info("No background monitor is running."); return; }

    printf("\n");
    signal_process_group(g_bg_pid, SIGTERM);
    int status;
    waitpid(g_bg_pid, &status, 0);
    ui_ok("Background monitor %d stopped and reaped.", (int)g_bg_pid);
    g_bg_pid = -1;
}

/* ==================== process control submenu ==================== */

static void process_control_menu(void)
{
    char buf[64];

    printf("\n");
    ui_box_top("PROCESS CONTROL   (signals via kill)");
    ui_row("1.  Terminate      SIGTERM    graceful stop, catchable");
    ui_row("2.  Force Kill     SIGKILL    cannot be caught or ignored");
    ui_row("3.  Stop           SIGSTOP    suspend process  (state -> T)");
    ui_row("4.  Continue       SIGCONT    resume a stopped process");
    ui_row("5.  Show details   read /proc/[PID]/status");
    ui_row("6.  Signal GROUP   SIGTERM to an entire process group");
    ui_row("0.  Back to main menu");
    ui_box_bottom();

    printf("\n");
    ui_center("Choice: ");
    fflush(stdout);
    read_line(buf, sizeof(buf));

    int c = atoi(buf);
    if (c == 0 || buf[0] == '\0') { g_interrupted = 0; return; }

    ui_center("Enter %s: ", (c == 6) ? "PGID (group leader)" : "PID");
    fflush(stdout);
    read_line(buf, sizeof(buf));

    pid_t pid = (pid_t)atoi(buf);
    if (pid <= 0) { printf("\n"); ui_err("Invalid PID entered."); return; }

    printf("\n");
    switch (c) {
        case 1: terminate_process(pid);      break;
        case 2: kill_process(pid);           break;
        case 3: stop_process(pid);           break;
        case 4: continue_process(pid);       break;
        case 5: print_process_details(pid);  break;
        case 6: signal_process_group(pid, SIGTERM); break;
        default: ui_err("Invalid choice.");
    }
}

/* ==================== main menu ==================== */

static void show_menu(void)
{
    ui_clear();
    ui_banner();
    printf("\n");

    ui_box_top("PROCESS STATUS");
    ui_kv("Monitor PID",  "%d", (int)getpid());
    ui_kv("Parent PID",   "%d", (int)getppid());
    ui_kv("Process group", "%d", (int)getpgrp());
    if (g_bg_pid > 0)
        ui_kv("Background logger", C_GREEN "RUNNING" C_RESET "  (pid %d)", (int)g_bg_pid);
    else
        ui_kv("Background logger", C_DIM "stopped" C_RESET);
    ui_box_bottom();

    printf("\n");

    ui_box_top("MAIN MENU");
    ui_row("1.  CPU Usage             fork + pipe + waitpid");
    ui_row("2.  Memory Usage          /proc/meminfo");
    ui_row("3.  Running Processes     /proc/[PID]/status");
    ui_row("4.  Process Control       kill / SIGSTOP / SIGCONT");
    ui_row("5.  Live Dashboard        streaming IPC + SIGINT");
    ui_row("6.  Background Monitor    process group + logging");
    ui_row("7.  Exit");
    ui_box_bottom();

    printf("\n");
    ui_center("Enter choice: ");
    fflush(stdout);
}

int main(void)
{
    char buf[64];
    install_handlers();

    for (;;) {
        show_menu();
        read_line(buf, sizeof(buf));

        if (g_interrupted) { g_interrupted = 0; continue; }
        if (buf[0] == '\0') continue;

        switch (atoi(buf)) {
            case 1: cpu_usage_via_child();  pause_enter(); break;
            case 2: print_memory_info();    pause_enter(); break;
            case 3: list_processes();       pause_enter(); break;
            case 4: process_control_menu(); pause_enter(); break;
            case 5: live_dashboard();       pause_enter(); break;
            case 6:
                if (g_bg_pid > 0) stop_background_monitor();
                else              start_background_monitor();
                pause_enter();
                break;
            case 7:
                if (g_bg_pid > 0) stop_background_monitor();
                ui_cursor_show();
                printf("\n");
                ui_ok("Exiting monitor. Goodbye.");
                printf("\n");
                return 0;
            default:
                printf("\n");
                ui_err("Invalid choice. Please enter 1-7.");
                pause_enter();
        }
    }
}
