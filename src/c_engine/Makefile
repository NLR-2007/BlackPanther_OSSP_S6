CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC -D_GNU_SOURCE
LDFLAGS = -shared

TARGET = libsysmonitor.so
SRCS = sysmonitor_engine.c process_engine.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
