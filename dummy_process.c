/*
 * Dummy Process Creator for Testing Smart Linux Task Manager
 * Demonstrates: fork(), exec(), pthread_create(), open files, CPU usage
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <fcntl.h>

void *worker_thread(void *arg) {
    int id = *(int *)arg;
    printf("[Thread %d] POSIX Thread running (TID in /proc/self/task)\n", id);
    while (1) {
        // Simple CPU load loop
        double x = 3.14159 * 2.71828;
        usleep(50000); // 50ms sleep
    }
    return NULL;
}

int main() {
    printf("====================================================\n");
    printf("  Test Process Started! PID = %d\n", getpid());
    printf("  Inspect this PID in Task Manager -> Processes Tab!\n");
    printf("====================================================\n");

    // 1. Open test file descriptors (for /proc/PID/fd testing)
    int fd1 = open("/tmp/test_fd1.txt", O_CREAT | O_RDWR, 0644);
    int fd2 = open("/tmp/test_fd2.txt", O_CREAT | O_RDWR, 0644);
    printf("[FDs] Created File Descriptors: FD %d and FD %d\n", fd1, fd2);

    // 2. Spawn POSIX Threads (for /proc/PID/task testing)
    pthread_t t1, t2;
    int id1 = 1, id2 = 2;
    pthread_create(&t1, NULL, worker_thread, &id1);
    pthread_create(&t2, NULL, worker_thread, &id2);

    // 3. Keep main process running
    while (1) {
        sleep(1);
    }

    return 0;
}
