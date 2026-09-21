CC      = gcc
CFLAGS  = -Wall -Wextra -std=gnu11 -D_GNU_SOURCE -g
TARGET  = monitor
OBJS    = main.o cpu.o memory.o process.o process_control.o ui.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

%.o: %.c monitor.h ui.h
	$(CC) $(CFLAGS) -c $< -o $@

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(OBJS) $(TARGET) monitor.log

.PHONY: all run clean
