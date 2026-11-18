# Operating systems practices worth teaching

Sources read 2026-11-18 as reading material only:
- [EEVDF] Linux kernel documentation, "EEVDF Scheduler", docs.kernel.org/scheduler/sched-eevdf.html (whole page)
- [man7] Linux man-pages, man7.org/linux/man-pages/ (syscalls(2), fork(2), strace(1), proc(5)), from what is known of them; not re-read this session [unchecked]
- [machine] measured on this machine with getconf, uname and gcc --version, 2026-11-18

## Habits

1. Compile every program with `gcc -Wall -Wextra -g` and fix every warning before running. From chapter 1. [man7, 2026-11-18]
2. Check the return value of every system call and print `errno` with `perror` when it fails. From chapter 1. [man7, 2026-11-18]
3. Predict first, then observe: write down what you expect before running `strace`, `ps` or a timer. From chapter 1.
4. Every `fork` is matched by a `wait` in the parent; no zombies left behind. From chapter 2. [man7, 2026-11-18]
5. Compile threaded programs with `-pthread`, and every `pthread_create` is matched by a `pthread_join`. From chapter 2. [man7, 2026-11-18]
6. Shared data touched by two threads is protected by one named lock, held for as short a time as possible. From chapter 4.

## Facts that change

- Linux began moving from CFS to the EEVDF scheduler in kernel 6.6; EEVDF tracks each task's lag and runs the eligible task with the earliest virtual deadline. [EEVDF, 2026-11-18]
- On x86-64 Linux the page size is 4096 bytes (`getconf PAGESIZE`). [machine, 2026-11-18]
- Ubuntu 24.04's gcc is 13.3; glibc's `printf` to a terminal is line-buffered and to a file or pipe is fully buffered. [machine, man7, 2026-11-18]
- strace prints `openat`, not `open`, for file opens on current glibc. [man7, 2026-11-18] [unchecked]
- Process states seen in `ps` STAT: R running or runnable, S sleeping, D uninterruptible sleep, Z zombie, T stopped. [man7, 2026-11-18]

## Handle with care

- Fork in a loop (fork bomb): can freeze the laptop; the book's loops always bound the count and the reader may set `ulimit -u 200` first. [man7, 2026-11-18]
- Allocating memory until the system swaps or the OOM killer acts: never asked for on an 8 GB laptop; experiments stay under 1 GB.
- `sudo` and writing to `/proc/sys` or `/sys`: changes the running kernel; the book only reads these files.
- `kill -9` on a process you did not start: can lose work; the book only signals its own programs by their PID.
