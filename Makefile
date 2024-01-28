CC = gcc
CFLAGS = -Wall -Wextra -std=c99
LIBS = -lsystemd

parliamentctl: ./src/parliamentctl.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

.PHONY: clean

clean:
	rm -f parliamentctl
