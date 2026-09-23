#include "monitor.h"

int process_exists(pid_t pid)
{
    if (pid <= 0) return 0;
    if (kill(pid, 0) == 0) return 1;
    return (errno == EPERM);   /* exists but not ours */
}

static void send_signal(pid_t pid, int sig, const char *sname)
{
    if (!process_exists(pid)) {
        printf("PID %d does not exist.\n", (int)pid);
        return;
    }
    if (kill(pid, sig) == -1) {
        fprintf(stderr, "Failed to send %s to %d: %s\n",
                sname, (int)pid, strerror(errno));
        return;
    }
    printf("%s sent to PID %d successfully.\n", sname, (int)pid);
}

void terminate_process(pid_t pid) { send_signal(pid, SIGTERM, "SIGTERM"); }
void kill_process(pid_t pid)      { send_signal(pid, SIGKILL, "SIGKILL"); }
void stop_process(pid_t pid)      { send_signal(pid, SIGSTOP, "SIGSTOP"); }
void continue_process(pid_t pid)  { send_signal(pid, SIGCONT, "SIGCONT"); }

void signal_process_group(pid_t pgid, int sig)
{
    if (kill(-pgid, sig) == -1) {
        fprintf(stderr, "Failed to signal group %d: %s\n",
                (int)pgid, strerror(errno));
        return;
    }
    printf("Signal %d sent to process group %d.\n", sig, (int)pgid);
}
