#include <QApplication>
#include <QMainWindow>
#include <QLabel>
#include <QVBoxLayout>
#include "sysmonitor_engine.h"
#include "process_engine.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    // Initialize C Monitoring Engine
    sysmon_init();

    QMainWindow window;
    window.setWindowTitle("Smart Linux Resource Monitoring and Process Control System");
    window.resize(1200, 800);

    QLabel *label = new QLabel("Smart Linux Task Manager - Qt6 Core System Initialized", &window);
    label->setAlignment(Qt::AlignCenter);
    window.setCentralWidget(label);

    window.show();
    return app.exec();
}
