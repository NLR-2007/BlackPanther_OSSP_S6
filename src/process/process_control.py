import os
import signal
import subprocess
import psutil

class ProcessControl:
    @staticmethod
    def launch_process(command_line):
        try:
            cmd = command_line.strip()
            # If launcher requested dummy_process, locate or auto-compile it
            if "dummy_process" in cmd:
                pwd = os.getcwd()
                dummy_bin = os.path.join(pwd, "dummy_process")
                dummy_c = os.path.join(pwd, "dummy_process.c")
                if not os.path.exists(dummy_bin) and os.path.exists(dummy_c):
                    subprocess.run(f"gcc \"{dummy_c}\" -o \"{dummy_bin}\" -lpthread", shell=True)
                if os.path.exists(dummy_bin):
                    cmd = f"\"{dummy_bin}\""

            # Launch as a new persistent process group on Linux
            p = subprocess.Popen(cmd, shell=True, start_new_session=True)
            return True, f"Process started successfully (PID {p.pid})"
        except Exception as e:
            return False, f"Failed to launch process: {str(e)}"

    @staticmethod
    def terminate_process(pid):
        try:
            if hasattr(os, 'kill'):
                os.kill(pid, signal.SIGTERM)
            else:
                p = psutil.Process(pid)
                p.terminate()
            return True, f"SIGTERM signal sent to PID {pid}"
        except Exception as e:
            return False, f"Error terminating PID {pid}: {str(e)}"

    @staticmethod
    def kill_process(pid):
        try:
            if hasattr(os, 'kill'):
                os.kill(pid, signal.SIGKILL)
            else:
                p = psutil.Process(pid)
                p.kill()
            return True, f"SIGKILL signal sent to PID {pid}"
        except Exception as e:
            return False, f"Error killing PID {pid}: {str(e)}"

    @staticmethod
    def pause_process(pid):
        try:
            if hasattr(signal, 'SIGSTOP') and hasattr(os, 'kill'):
                os.kill(pid, signal.SIGSTOP)
            else:
                p = psutil.Process(pid)
                p.suspend()
            return True, f"SIGSTOP (Pause) signal sent to PID {pid}"
        except Exception as e:
            return False, f"Error pausing PID {pid}: {str(e)}"

    @staticmethod
    def resume_process(pid):
        try:
            if hasattr(signal, 'SIGCONT') and hasattr(os, 'kill'):
                os.kill(pid, signal.SIGCONT)
            else:
                p = psutil.Process(pid)
                p.resume()
            return True, f"SIGCONT (Resume) signal sent to PID {pid}"
        except Exception as e:
            return False, f"Error resuming PID {pid}: {str(e)}"

    @staticmethod
    def restart_process(pid):
        try:
            p = psutil.Process(pid)
            cmd = " ".join(p.cmdline())
            p.terminate()
            if cmd:
                subprocess.Popen(cmd, shell=True, start_new_session=True)
                return True, f"Process {pid} restarted with command: {cmd}"
            return True, f"Process {pid} terminated"
        except Exception as e:
            return False, f"Error restarting PID {pid}: {str(e)}"
