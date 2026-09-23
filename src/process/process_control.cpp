#include "process_engine.h"

class ProcessControlCPP {
public:
    int sendSignal(int pid, int sig) {
        return procmon_send_signal(pid, sig);
    }
    int terminateProcess(int pid) {
        return procmon_terminate_process(pid);
    }
    int killProcess(int pid) {
        return procmon_kill_process(pid);
    }
    int pauseProcess(int pid) {
        return procmon_pause_process(pid);
    }
    int resumeProcess(int pid) {
        return procmon_resume_process(pid);
    }
    int launchProcess(const char *cmd) {
        return procmon_launch_process(cmd);
    }
};
