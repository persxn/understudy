# Operating systems: what really happens inside your laptop
for: a computer science student who knows C at college level (loops, functions, a little about pointers) and has used the terminal, has sat through OS lectures and can recite definitions, but has never watched the operating system work; Ubuntu laptop with gcc
run: c
kind: system

## Part I · Follow one program through the operating system

### 1 From ./a.out to "hello": one program's life
1.1 Run it and ask what happened: the trace this book follows | teaches: program-vs-process, os-role
1.2 Why programs cannot touch the hardware: user mode, kernel mode and the trap | teaches: user-mode, kernel-mode, privileged-instruction, trap | fig
1.3 System calls: the only door into the kernel, watched with strace | teaches: system-call, syscall-number, strace
1.4 printf is not a system call: the C library sits in between | short | teaches: libc-wrapper, stdout-buffer
1.5 What a process is made of: address space, registers, open files, the process table | teaches: process, pcb, address-space, file-descriptor | fig
1.6 Interrupts and the timer: how the kernel takes the CPU back | teaches: interrupt, timer-interrupt, context-switch | level: 2
1.7 When a step fails: errno, a bad pointer and a segmentation fault | teaches: errno, segfault
1.8 Practice: predict, then strace, three small programs | practice | level: 3

## Part II · Many programs at once

### 2 Making processes and threads
2.1 fork: one process becomes two | teaches: fork, parent-child, pid | needs: process, system-call
2.2 exec and wait: how your shell runs a command | teaches: exec, wait, zombie, orphan | fig
2.3 Process states: running, ready, blocked, and the moves between them | teaches: process-state, ready-queue, blocked-state | needs: context-switch | fig
2.4 Threads: two flows of control in one address space | teaches: thread, pthread-create, pthread-join, shared-memory-threads | needs: address-space
2.5 Processes or threads: what each costs, measured | teaches: thread-vs-process, kernel-thread | level: 2
2.6 Practice: build a tiny shell that runs one command at a time | practice | level: 3

### 3 Who runs next: CPU scheduling
3.1 Why the kernel must choose: CPU bursts and I/O bursts | teaches: cpu-burst, io-burst, scheduler | needs: process-state
3.2 Measuring a schedule: waiting, turnaround and response time | teaches: waiting-time, turnaround-time, response-time, throughput
3.3 First come first served and shortest job first, worked on Gantt charts | teaches: fcfs, sjf, srtf, convoy-effect | fig
3.4 Round robin and the size of the time slice | teaches: round-robin, time-quantum, preemption | needs: timer-interrupt | fig
3.5 Priorities, starvation and ageing | teaches: priority-scheduling, starvation, ageing, nice
3.6 Multilevel feedback queues and what Linux really does (CFS, now EEVDF) | teaches: mlfq, cfs, vruntime, eevdf | level: 2
3.7 Practice: exam-style schedules by hand, then watch nice on your laptop | practice | level: 3

### 4 Sharing safely: synchronisation
4.1 Two threads, one counter, wrong answer | teaches: race-condition, critical-section | needs: thread
4.2 Why count++ is three instructions | short | teaches: atomicity, interleaving | fig
4.3 Mutual exclusion: Peterson's solution and test-and-set | teaches: mutual-exclusion, peterson, test-and-set, spinlock | level: 2
4.4 Mutexes and semaphores in pthreads | teaches: mutex, semaphore, binary-semaphore, counting-semaphore
4.5 Producer and consumer: condition variables | teaches: condition-variable, bounded-buffer, producer-consumer | fig
4.6 Deadlock: the four conditions, the dining philosophers, avoidance with the banker's algorithm | teaches: deadlock, coffman-conditions, resource-allocation-graph, bankers-algorithm | level: 2
4.7 Practice: fix three broken threaded programs, then solve readers and writers | practice | level: 3

## Part III · Where data lives

### 5 Memory: addresses that are not real
5.1 Print an address twice in two processes: same number, different data | teaches: virtual-address, physical-address | needs: fork, address-space
5.2 The layout of a process: text, data, heap, stack | teaches: memory-layout, heap, stack-segment | fig
5.3 From segments to paging: pages, frames and the page table | teaches: segmentation, page, frame, page-table, address-translation | fig
5.4 Making translation fast: the TLB and multi-level page tables | teaches: tlb, multilevel-page-table, effective-access-time | level: 2
5.5 Page faults and demand paging, watched with /usr/bin/time | teaches: page-fault, demand-paging, copy-on-write | needs: fork
5.6 Page replacement: FIFO, optimal, LRU and Belady's anomaly | teaches: page-replacement, fifo-replacement, lru, optimal-replacement, belady-anomaly | fig
5.7 Thrashing and the working set | teaches: thrashing, working-set | level: 2
5.8 Practice: translate addresses and count page faults by hand, then measure | practice | level: 3

### 6 Files: from a name to blocks on a disk
6.1 open, read, write, close: a file seen through system calls | teaches: file-syscalls, open-file-table | needs: file-descriptor, system-call
6.2 Inodes and directories: what a file name really points to | teaches: inode, directory-entry, hard-link, soft-link | fig
6.3 Allocating blocks: contiguous, linked, indexed | teaches: contiguous-allocation, linked-allocation, indexed-allocation | fig
6.4 Free space and the cost of a disk access | teaches: free-space-bitmap, disk-latency
6.5 Caching and a power cut mid-write: fsync and journaling | teaches: page-cache, fsync, journaling | level: 2
6.6 Practice: walk a path to its blocks by hand, then with stat and ls -i | practice | level: 3

