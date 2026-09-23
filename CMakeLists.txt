cmake_minimum_required(VERSION 3.16)
project(SmartLinuxSysMonitor VERSION 1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 COMPONENTS Widgets Core Gui REQUIRED)

# Include C Engine Headers
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/c_engine)

# C Engine Library
add_library(sysmonitor_c_engine STATIC
    src/c_engine/sysmonitor_engine.c
    src/c_engine/process_engine.c
)

# C++ Source Files
set(SOURCES
    src/main.cpp
    src/monitoring/cpu_monitor.cpp
    src/monitoring/memory_monitor.cpp
    src/monitoring/disk_monitor.cpp
    src/monitoring/network_monitor.cpp
    src/monitoring/gpu_monitor.cpp
    src/process/process_manager.cpp
    src/process/process_control.cpp
    src/filesystem/fd_monitor.cpp
    src/memory/memory_analyzer.cpp
    src/threads/thread_monitor.cpp
)

add_executable(SmartLinuxSysMonitor ${SOURCES})

target_link_libraries(SmartLinuxSysMonitor PRIVATE
    sysmonitor_c_engine
    Qt6::Widgets
    Qt6::Core
    Qt6::Gui
)
