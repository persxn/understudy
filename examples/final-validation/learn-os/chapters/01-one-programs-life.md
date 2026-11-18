# Chapter 1: From ./a.out to "hello": one program's life

<!-- contents -->
- [1.1 Run it and ask what happened: the trace this book follows](#11-run-it-and-ask-what-happened-the-trace-this-book-follows)
- [1.2 Why programs cannot touch the hardware: user mode, kernel mode and the trap](#12-why-programs-cannot-touch-the-hardware-user-mode-kernel-mode-and-the-trap)
- [1.3 System calls: the only door into the kernel, watched with strace](#13-system-calls-the-only-door-into-the-kernel-watched-with-strace)
- [1.4 printf is not a system call: the C library sits in between](#14-printf-is-not-a-system-call-the-c-library-sits-in-between)
- [1.5 What a process is made of: address space, registers, open files, the process table](#15-what-a-process-is-made-of-address-space-registers-open-files-the-process-table)
- [1.6 Interrupts and the timer: how the kernel takes the CPU back](#16-interrupts-and-the-timer-how-the-kernel-takes-the-cpu-back)
- [1.7 When a step fails: errno, a bad pointer and a segmentation fault](#17-when-a-step-fails-errno-a-bad-pointer-and-a-segmentation-fault)
- [1.8 Practice: predict, then strace, three small programs](#18-practice-predict-then-strace-three-small-programs)
<!-- /contents -->

## 1.1 Run it and ask what happened: the trace this book follows

### The question your lectures skipped

You have run thousands of programs. You type `./a.out`, press Enter, and a line appears. Your OS lectures gave you the words for what happens in between: process, system call (§1.3), kernel mode (§1.2), context switch (§1.6), scheduler (chapter 3). You can probably write a definition of each one. But if someone asked you, in an interview, "what exactly happens between pressing Enter and the line appearing on the screen?", the honest answer might be "the OS runs it". This chapter replaces that sentence with the real order of events, one step at a time, and you will watch most of the steps happen on your own laptop.

This book keeps coming back to that one event. Chapter 1 follows it from start to end at low resolution, the way a map of India shows the main roads but not the streets. Each later chapter zooms into one stretch of the road: how the process is made (chapter 2), how it gets the processor (chapter 3), how two threads share data safely (chapter 4), where its bytes live in memory (chapter 5), and how its output reaches a file on disk (chapter 6). Everything in your syllabus hangs somewhere on this one trace.

### The smallest program worth tracing

Open a terminal. Make a folder for this book's work and go into it: `mkdir -p` makes the folder and any missing folders above it, `cd` moves into it, and `pwd` prints where you are. Everything in this chapter happens in `~/os/ch01`.

<!-- code: id=make-folder -->
```console
$ mkdir -p os/ch01 && cd os/ch01
$ pwd
/home/you/os/ch01
```

Now type this program into a file called `hello.c`, with any editor you like (`nano hello.c` works):

<!-- code: id=hello -->
```c
#include <stdio.h>

int main(void)
{
    printf("hello, world\n");
    return 0;
}
```
```text
hello, world
```

Compile it with warnings switched on (`-Wall -Wextra`), with debugging information (`-g`, used in 1.7) and with the output file named `hello` (`-o hello`); look at what the compiler made, and run it:

<!-- code: id=hello-run -->
```console
$ gcc -Wall -Wextra -g -o hello hello.c
$ ls -l hello
-rwxr-xr-x 1 ubuntu ubuntu 17064 Nov 18 06:35 hello
$ ./hello
hello, world
```


Two different things appear here, and the whole subject rests on the difference between them.

<!-- teaches: program-vs-process = program, process, executable file -->
`hello` in the `ls -l` line is a **program**: a file on the disk, about sixteen thousand bytes of machine instructions and data, sitting there doing nothing. It would sit there for ten years if nobody ran it. It has a name, a size, permissions (the `x` letters say it may be executed) and a date. It is exactly as alive as `hello.c`.

What happened when you typed `./hello` is that something took that file, gave it memory, loaded its instructions into that memory, pointed the processor at the first one, gave it a way to print, and later cleaned up after it. The running thing that existed for a few milliseconds is a **process**: a program in execution, plus everything the operating system keeps about it while it runs. One program can be several processes at once: open three terminals and run `./hello` in each, and there are three processes of one program. The file on disk is the recipe; the process is the cooking.

You can see a process from the inside without writing any code. Linux shows every process as a small folder of text files under `/proc`, and `/proc/self` always means "the process that is reading this". So when `grep` reads `/proc/self/status`, it reads its own entry:

<!-- code: id=proc-self varies -->
```console
$ grep -E '^(Name|State|Pid|PPid|Threads)' /proc/self/status
Name:   grep
State:  R (running)
Pid:    3986
PPid:   3985
Threads:        1
```


`Name: grep` is the program that is running. `State: R (running)` says it was on the processor when it read the file, which is obvious when you think about it: it was the one reading. `Pid` is the number the kernel gave this process, and `PPid` is the number of its parent, the shell that started it; both get their full story in section 2.1. Your numbers will differ from the ones printed here, and they change every time you run the command, because each run is a new process. The program `grep` stays the same file on disk; the process is new each time.

### The office counter

Here is a picture that the whole book uses. Think of a government office. The files, the stamps, the safe and the printer are behind a counter. You, the visitor, cannot walk behind the counter, however reasonable your reason. You stand at the window, fill in a form saying exactly what you want ("print this line", "open this file", "give me more memory"), and the clerk behind the counter checks the form, does the job, and hands back a result, or a rejection with a reason.

Your program is the visitor. The **kernel**, the core of the operating system that is always in memory, is the clerk. The hardware (processor control registers, disk, screen, network card, all of memory) is behind the counter. Every useful thing your program does to the outside world, it does by asking at the window.

The picture stops being true in one important way: a clerk in an office only acts when someone is standing at the window. The kernel also acts on its own. A hardware clock taps it on the shoulder many times a second, the disk announces that data has arrived, and the kernel then takes the processor away from whatever program had it. Section 1.6 is about that. Keep the counter in mind, and remember the clerk can also walk out and stop you mid-sentence.

### The trace, at low resolution

<!-- teaches: os-role = operating system, kernel, referee, illusionist -->
Here is everything that happens between your Enter key and the next prompt, in order. Read it as a story, not a list to memorise; every row is a later section.

| Step | Who acts | What happens | Where in this book |
|---|---|---|---|
| 1 | the terminal and the kernel | your key presses travel from the keyboard to the kernel, which hands the line `./hello` to the shell that was waiting to read it | 1.3 (read), 1.6 (interrupts) |
| 2 | the shell (bash) | bash is an ordinary process; it asks the kernel to make a copy of itself, a new process | 2.1 |
| 3 | the new process and the kernel | the copy asks the kernel to throw away bash's program and load the file `./hello` in its place | 2.2 |
| 4 | the kernel | it builds a fresh address space for the process, maps in the program and the C library (1.4), and sets the processor going at the program's start | 1.5, 5.2 |
| 5 | the scheduler | the new process waits its turn for one of your laptop's processor cores | chapter 3 |
| 6 | your code | `main` runs; `printf` builds the bytes `hello, world\n` in a buffer inside your own process | 1.4 |
| 7 | the C library and the kernel | the buffer is handed to the kernel with the `write` system call; the processor switches into kernel mode, the kernel copies the bytes to the terminal, and switches back | 1.2, 1.3 |
| 8 | your code and the kernel | `main` returns 0; the C library calls `exit`, the kernel frees the memory and closes the files, and tells the parent the exit code | 1.5, 2.2 |
| 9 | the shell | bash, which was waiting, wakes up and prints the next prompt | 2.2, 2.3 |

Notice three things about that table, because they are the three jobs of an operating system.

First, the kernel is a **referee**. Nine steps, and your code acts alone in only one of them. Every time the program needs something outside its own memory (the screen, a file, more memory, another process), it goes through the kernel, which can say no. That is how one buggy program on your laptop cannot wipe another program's memory or the disk.

Second, the kernel is an **illusionist**. While `hello` runs, your laptop has perhaps 300 other processes and only a few processor cores. Yet `hello` was written as if it had the processor and the memory all to itself: no line of it says "wait for the others". The kernel keeps up that illusion by switching processes many times a second (chapter 3) and giving each its own private view of memory (chapter 5).

Third, the kernel is the **glue**, the common services every program needs and nobody wants to write: files, terminals, networks, timers. `printf` would be thousands of lines of driver code without it.

### What goes wrong with the usual picture

The most common wrong picture after a lecture course is that "the OS" is a program that runs *beside* yours, the way a music player runs beside a browser. Then questions like "who runs the OS while my program runs?" have no answer. The truer picture: the kernel is not a separate process taking turns with yours. It is code that runs *when something enters it*: your program asking at the counter (a system call), the hardware raising its hand (an interrupt), or your program doing something forbidden (a fault). Between those moments, the kernel is not running at all; your program has the processor. Sections 1.2 and 1.6 make this concrete.

A second wrong picture is that a process is the same as a program. Then "how many processes does this program make?" sounds like a strange question. It is the question of chapter 2.

**Check yourself**

1. You run `./hello` in three terminals at the same moment. How many programs and how many processes are involved (count only `hello`, not the shells)? What do the three processes share, and what does each have of its own?

<details>
<summary>Answer</summary>

One program, the file `hello` on disk, and three processes. They share the file they were loaded from (the kernel even shares the read-only machine code in memory between them, as chapter 5 shows). Each has its own process number, its own memory, its own place in the processor queue and its own exit code. The tempting wrong answer is "three programs": the file was not copied three times.

</details>

2. Run `grep -E '^(Name|Pid)' /proc/self/status` twice. Predict which line changes between the runs and which stays the same, and say why.

<details>
<summary>Answer</summary>

`Name: grep` stays the same: it is the same program. `Pid` changes: every run is a new process, and the kernel hands out a new number each time. If `Pid` had stayed the same, it would mean the same process read the file twice, which cannot happen because `grep` exits after one run.

</details>

3. A friend says "while my C program runs, the operating system runs in the background and watches it". Find the fault in that sentence, and say what really happens when the program prints.

<details>
<summary>Answer</summary>

On a single processor core, while your program runs, the kernel is not running: your program has the core. The kernel runs only when something enters it: your program makes a system call (like `write` when it prints), the hardware raises an interrupt (like the timer, section 1.6), or the program does something forbidden (a fault, section 1.7). To print, the program itself enters the kernel through the `write` system call; the kernel does the copy and returns to the program.

</details>

## 1.2 Why programs cannot touch the hardware: user mode, kernel mode and the trap

### What stops a program from doing anything it likes?

Your `hello` program is machine code, and the processor runs machine code. The kernel is also machine code, running on the very same processor. So what stops `hello` from simply containing the kernel's instructions? Why can't a program write directly to the disk controller, switch off the timer, or read another program's memory? "The OS doesn't allow it" is not an answer, because, as you saw in 1.1, while your program runs the kernel is not running at all. Nobody is there to forbid anything.

The answer is in the processor itself, and you can watch it work in two small programs.

### Try to stop the computer

The x86-64 processor in your laptop has an instruction called `hlt`, "halt": stop executing instructions until the next interrupt arrives. The kernel uses it when there is nothing to do, to save power. Put it in a program and see what happens. The odd-looking `__asm__` line asks gcc to place one raw machine instruction into the program at that point:

<!-- code: id=halt mode=crash nosan -->
```c
#include <stdio.h>

int main(void)
{
    printf("about to stop the whole computer\n");
    fflush(stdout);
    __asm__ volatile ("hlt");
    printf("the computer is still running\n");
    return 0;
}
```
```text
about to stop the whole computer
Segmentation fault
```

(`fflush` pushes the first line out before the crash; why that is needed is section 1.4.)

The computer did not stop. Your terminal is fine, the music you had playing kept playing, and the second line never printed. The *program* died, and the message is the same one you get from a bad pointer: `Segmentation fault`. Now try reading a byte of the kernel's own memory. On x86-64 Linux the kernel lives at the very top of every process's address range, at addresses starting with `0xffff...`:

<!-- code: id=peek mode=crash nosan -->
```c
#include <stdio.h>

int main(void)
{
    volatile char *kernel = (volatile char *) 0xffffffff81000000UL;
    printf("reading one byte of kernel memory\n");
    fflush(stdout);
    char c = *kernel;
    printf("got %d\n", c);
    return 0;
}
```
```text
reading one byte of kernel memory
Segmentation fault
```


Same ending. Two different forbidden things, one instruction and one memory read, both stopped before they could do any harm, with nobody "watching". The thing that stopped them is a single bit inside the processor.

<!-- teaches: user-mode = user mode, ring 3 -->
<!-- teaches: kernel-mode = kernel mode, supervisor mode, ring 0 -->
### Two modes, one bit

At every moment, the processor is running in one of two **modes**. In **kernel mode** (also called supervisor mode; on x86 it is "ring 0") every instruction is allowed and every byte of memory can be reached. In **user mode** ("ring 3" on x86) a list of instructions is forbidden and the memory marked as the kernel's cannot be touched. The current mode is held in the processor itself, in bits the program cannot write.


<!-- teaches: privileged-instruction = privileged instruction, general protection fault -->
The forbidden instructions are called **privileged instructions**. They are exactly the ones that would let a program take over the machine: `hlt` (stop the processor), `cli` (switch off interrupts, so the timer can never take the processor back), the instructions that load a new page table (and so choose which memory is visible), the instructions that talk directly to devices (`in` and `out`), and the instructions that change the mode bit itself. Every one of them, used in user mode, makes the processor refuse.

What does "refuse" mean, in hardware? The processor does not skip the instruction and carry on. It stops what it is doing, switches itself into kernel mode, and jumps to an address the kernel stored in a table when the computer booted. For a privileged instruction the fault is called a *general protection fault*; for a forbidden memory address it is a *page fault* (section 5.5 treats page faults fully). The kernel's code at that address looks at what happened, sees that a user program broke the rules, and decides the punishment: on Linux, a signal called `SIGSEGV`, which by default kills the process. That is the `Segmentation fault` you saw. The bash shell prints those words when its child process dies of `SIGSEGV`.

You can watch the kernel deliver the signal with `strace` (`2>&1 | tail -3` sends its lines through the pipe and keeps only the last three), a tool that shows a process's dealings with the kernel (section 1.3 introduces it properly; here, just read the last lines):

<!-- code: id=halt-strace exit=139 -->
```console
$ gcc -Wall -Wextra -g -o halt halt.c
$ strace ./halt 2>&1 | tail -3
) = 33
--- SIGSEGV {si_signo=SIGSEGV, si_code=SI_KERNEL, si_addr=NULL} ---
+++ killed by SIGSEGV +++
$ ./halt
about to stop the whole computer
Segmentation fault
```


`si_code=SI_KERNEL` says the signal was sent by the kernel itself, not by another process. `killed by SIGSEGV` is how the process ended. The exit status the shell sees is 139, which is 128 plus 11, the number of `SIGSEGV`.

### The order of events in a fault

Here is the `hlt` program's death, step by step. Watch where the mode bit changes.

| Step | Mode | What happens |
|---|---|---|
| 1 | user | `main` runs; `printf` and `fflush` print the first line (with a short visit to the kernel, which you will meet in a moment) |
| 2 | user | the processor reaches `hlt`; it checks the mode bit: user mode, and `hlt` is privileged |
| 3 | user → kernel | the processor raises a general protection fault: it saves where the program was, switches to kernel mode and jumps to the kernel's fault handler |
| 4 | kernel | the handler sees the fault came from user mode; it marks `SIGSEGV` as pending for this process |
| 5 | kernel | on the way back out, the kernel delivers the signal; the default action for `SIGSEGV` is to end the process, so it never returns to user mode |
| 6 | kernel | the process's memory and files are released and its parent (bash) is told it died of signal 11 |
| 7 | user (bash) | bash wakes and prints `Segmentation fault` |

The one-way door in step 3 is the core of the whole design: the processor itself carries the program into the kernel, to an address the program did not choose. A program can never jump into the middle of the kernel's code or run the kernel's instructions in kernel mode, because the only ways into kernel mode go through entry points that the kernel set up at boot.

### A door that is meant to be used: the trap

If every way into kernel mode were a punishment, a program could never print anything. So the processor also has a polite door: an instruction that means "I want to ask the kernel something". On x86-64 this instruction is called `syscall`. It does what a fault does, on purpose: switches to kernel mode, saves where the program was, and jumps to the kernel's single entry point for requests. The kernel reads which service was asked for from a register, does the work if the request is allowed, puts the answer in a register, and uses the matching instruction `sysret` to drop back into user mode just after the `syscall`.

<!-- teaches: trap = trap, syscall instruction, mode switch -->
An entry into the kernel that the program makes on purpose, by an instruction, is called a **trap** (textbooks also say "software interrupt", from the older x86 instruction `int 0x80` that did the same job). Faults and traps share the same machinery; the difference is intention. A fault is the processor dragging the program to the counter for breaking a rule; a trap is the program walking up to the counter with a form.


Here is the counter picture again, now with the hardware in it:

<!-- fig: id=modes
kind: layers
title: Two modes, and the doors between them
layer user: User mode (ring 3)
in user: app = `./hello`; lib = C library
layer door: Doors: the CPU switches mode
in door: trap = trap: `syscall`; fault = fault: `hlt`; intr = interrupt
layer kern: Kernel mode (ring 0)
in kern: entry = entry points; work = handlers
layer hw: Hardware
in hw: cpu = CPU mode bit; dev = disk, screen, timer
hot: trap fault intr
-->
![Layers, top to bottom. User mode (ring 3) holds ./hello and C library. Doors: the CPU switches mode holds trap: syscall, fault: hlt and interrupt. Kernel mode (ring 0) holds entry points and handlers. Hardware holds CPU mode bit and disk, screen, timer. trap: syscall, fault: hlt and interrupt are highlighted.](fig/01-one-programs-life/modes.svg)

### Why build it this way, and what it costs

Before processors had two modes (early PCs running MS-DOS, for example), any program could do anything. A bug in a game could overwrite the disk's directory, and one program in a loop with interrupts switched off froze the machine until you pulled the plug. The two-mode design makes the kernel the only code that can touch shared things, so a bad program can only hurt itself. That is the referee job from 1.1, enforced by hardware, not by good manners.

The price is time. Crossing into the kernel and back means saving the program's registers, switching stacks, checking the request, and returning. On a modern processor a trivial system call costs somewhere around a hundred nanoseconds to a microsecond, compared with under a nanosecond for an ordinary instruction. That is why the C library (1.4) tries hard to make few system calls (1.3), which you will see in 1.4.


### When it goes wrong

- **"Segmentation fault" from code that never touched a pointer.** You will meet this when you try inline assembly or copy code that uses `in`, `out` or `cli` from an old DOS-era textbook. The program is not buggy in the usual sense: it ran a privileged instruction in user mode. `strace` shows `si_code=SI_KERNEL`.
- **Thinking `sudo` gets you into kernel mode.** It does not. A program started with `sudo` still runs in user mode, so `sudo ./halt` meets the same refusal from the processor. `sudo` makes the kernel answer more requests with yes (it changes who you are, the user root); it never changes the processor's mode. Root programs still run in user mode and still ask at the counter.
- **Mixing up "kernel" and "root".** Root is a user with permission to ask for anything. The kernel is the code that answers. Even root's requests go through the kernel's checks.

**Check yourself**

1. Predict what `sudo ./peek` prints, and explain why.

<details>
<summary>Answer</summary>

The same as without `sudo`: the first line, then `Segmentation fault`. Running as root changes which requests the kernel grants, but the program still runs in user mode, and the processor itself refuses user-mode access to kernel addresses. The tempting answer, "root can read kernel memory", mixes up the user (root) with the processor mode (kernel mode).

</details>

2. Put these in order for a program that calls `write`, and mark the mode at each step: the kernel copies the bytes to the terminal; the program executes `syscall`; the processor switches back to user mode; the processor jumps to the kernel's entry point; the program continues after `syscall`.

<details>
<summary>Answer</summary>

1. The program executes `syscall` (user mode). 2. The processor switches to kernel mode and jumps to the kernel's entry point (now kernel mode). 3. The kernel copies the bytes to the terminal (kernel mode). 4. The processor switches back to user mode with `sysret` (kernel, then user). 5. The program continues after `syscall` (user mode).

</details>

3. Decide: a classmate suggests making system calls faster by letting programs run in kernel mode "when they are trusted". What would be lost?

<details>
<summary>Answer</summary>

The protection. A program in kernel mode can run any instruction and touch any memory, so one bug (a wrong pointer, a loop with interrupts off) could corrupt the kernel, other programs or the disk, or freeze the machine; nothing would stop it, because the mode bit is the only thing that does. "Trusted" code still has bugs. Systems that want fewer crossings instead batch work into fewer system calls, which is what the C library's buffer does (section 1.4).

</details>

## 1.3 System calls: the only door into the kernel, watched with strace

### How many times did hello ask?

Section 1.2 left you with a counter and a door: a program asks the kernel for something by executing the `syscall` instruction. Now count. How many times do you think `hello`, a program with one line in `main`, walked up to the counter? Write your guess down before reading on. Most people say one or two: "one for the print, maybe one for the exit".

<!-- teaches: strace = strace, system call trace -->
You do not have to guess. **strace** is a program that starts another program and prints one line every time that program enters the kernel through a system call: the name of the call, its arguments, and what the kernel answered. It works because the kernel itself offers a way for one process to be told about another's system calls (the `ptrace` facility that debuggers such as gdb also use). If your terminal says `strace: command not found`, `sudo apt install strace` adds it; some Ubuntu installs include it and some do not.


strace writes its lines to the error stream, so they mix with the program's own output on the screen. Run it on `hello`:

<!-- code: id=strace-hello varies -->
```console
$ strace ./hello
execve("./hello", ["./hello"], 0x7fff96a79db0 /* 17 vars */) = 0
brk(NULL)                               = 0x55ab88a2d000
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f8a703dc000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=54703, ...}) = 0
mmap(NULL, 54703, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f8a703ce000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\220\243\2\0\0\0\0\0"..., 832) = 832
pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
fstat(3, {st_mode=S_IFREG|0755, st_size=2129424, ...}) = 0
pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
mmap(NULL, 2174352, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f8a70000000
mmap(0x7f8a70028000, 1609728, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x28000) = 0x7f8a70028000
mmap(0x7f8a701b1000, 323584, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1b1000) = 0x7f8a701b1000
mmap(0x7f8a70200000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1ff000) = 0x7f8a70200000
mmap(0x7f8a70206000, 52624, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f8a70206000
close(3)                                = 0
mmap(NULL, 12288, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f8a703cb000
arch_prctl(ARCH_SET_FS, 0x7f8a703cb740) = 0
set_tid_address(0x7f8a703cba10)         = 4017
set_robust_list(0x7f8a703cba20, 24)     = 0
rseq(0x7f8a703cc060, 0x20, 0, 0x53053053) = 0
mprotect(0x7f8a70200000, 16384, PROT_READ) = 0
mprotect(0x55ab783cc000, 4096, PROT_READ) = 0
mprotect(0x7f8a7041c000, 8192, PROT_READ) = 0
prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
munmap(0x7f8a703ce000, 54703)           = 0
fstat(1, {st_mode=S_IFCHR|0600, st_rdev=makedev(0x88, 0), ...}) = 0
getrandom("\xd0\x1c\xc6\x1d\xde\xed\xaa\x11", 8, GRND_NONBLOCK) = 8
brk(NULL)                               = 0x55ab88a2d000
brk(0x55ab88a4e000)                     = 0x55ab88a4e000
write(1, "hello, world\n", 13hello, world
)          = 13
exit_group(0)                           = ?
+++ exited with 0 +++
```


Thirty-odd lines for one `printf`. Your guess was probably too low by a factor of fifteen, and every one of those lines is a real trip through the door of 1.2. The numbers in the addresses will be different on your laptop and on every run (section 5.1 explains why the addresses move); the shape will be the same.

### Reading the trace, from top to bottom

<!-- teaches: system-call = system call, syscall -->
Each line is one **system call**: a request from a process to the kernel, made through the trap, for a service only the kernel can perform. The format is always `name(arguments) = result`. Read the trace in four groups, which are the stages of the program's life you saw in the 1.1 table.

**1. Becoming `hello`: `execve`.** The first line, `execve("./hello", ["./hello"], ...) = 0`, is the call that turned a copy of strace into `hello` (chapter 2 explains this fully, in section 2.2). The `= 0` means the kernel succeeded. From here on, the process is running the code of `hello`, but not your `main` yet.

**2. The dynamic loader getting ready: `brk`, `mmap`, `openat`, `read`, `pread64`, `fstat`, `close`, `mprotect`.** Your program does not contain the code of `printf`. It contains a note saying "I need the C library". Before `main` can start, a small program called the dynamic loader (`ld-linux-x86-64.so.2`) runs inside your process and fetches the library. Follow it on the trace:

- `openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3`: open the cache file that says where libraries live. The kernel answers with **3**, a small number that from now on stands for this open file inside this process. These numbers are called file descriptors, and they are the subject of section 1.5. For now: 0, 1 and 2 are already taken by the terminal, so the first file a program opens gets 3.
- `mmap(..., 3, 0) = 0x7f...`: map that file into the process's memory so it can be read like an array, then `close(3)`: give the number back.
- `openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", ...) = 3`: open the C library itself. The number 3 is free again, so it is used again.
- `read(3, "\177ELF...", 832) = 832`: read the library's header. `\177ELF` are the four bytes that start every Linux executable and library.
- several more `mmap` calls: map the library's code (`PROT_READ|PROT_EXEC`: may be read and run) and its data (`PROT_READ|PROT_WRITE`) into memory; then `mprotect`: make some of it read-only once it is set up.

**3. The C library setting up house: `arch_prctl`, `set_tid_address`, `set_robust_list`, `rseq`, `prlimit64`, `getrandom`, `brk`.** Small bits of bookkeeping before `main`: where the thread's private data lives, a random number for security checks, and `brk`, which asks for room for the heap (the memory `malloc` hands out; `printf` needs a buffer from it).

**4. Your program: `fstat`, `write`, `exit_group`.** Here, at last, is your line. `fstat(1, ...)` asks "what is file descriptor 1?" (the answer, a character device, tells the library that output goes to a terminal; section 1.4 says why it cares). Then:

```text
write(1, "hello, world\n", 13hello, world
)          = 13
```

That is your `printf`, as the kernel sees it: write to descriptor 1 (standard output), these bytes, 13 of them. The kernel's answer, `= 13`, says all 13 were written. The `hello, world` in the middle of the line is the program's real output landing on the screen while strace was still printing its own line. Last, `exit_group(0) = ?`: `main` returned 0, the library passed it to the kernel, and the process ended. There is no result, `?`, because there is no process left to receive one.

### Counting instead of reading

For a long-running program, the line-by-line trace is too much. `strace -c` counts instead:

<!-- code: id=strace-count varies -->
```console
$ strace -c ./hello
hello, world
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
  0.00    0.000000           0         1           read
  0.00    0.000000           0         1           write
  0.00    0.000000           0         2           close
  0.00    0.000000           0         3           fstat
  0.00    0.000000           0         8           mmap
  0.00    0.000000           0         3           mprotect
  0.00    0.000000           0         1           munmap
  0.00    0.000000           0         3           brk
  0.00    0.000000           0         2           pread64
  0.00    0.000000           0         1         1 access
  0.00    0.000000           0         1           execve
  0.00    0.000000           0         1           arch_prctl
  0.00    0.000000           0         1           set_tid_address
  0.00    0.000000           0         2           openat
  0.00    0.000000           0         1           set_robust_list
  0.00    0.000000           0         1           prlimit64
  0.00    0.000000           0         1           getrandom
  0.00    0.000000           0         1           rseq
------ ----------- ----------- --------- --------- ----------------
100.00    0.000000           0        34         1 total
```


The table has one row per kind of system call, with how many times it was made (`calls`) and how many failed (`errors`). Read the `total` row: that is the number you guessed at the start (34 here; the trace above showed one line more, `exit_group`, which never returns, so `-c` does not count it). Notice that `write` appears exactly once. Almost all the work of a tiny program is starting up; for a program that runs for minutes, the start-up calls are lost in the noise.

The time columns say how long the kernel spent inside each call. On a short program they are tiny and change from run to run; do not read meaning into them.

### A number for every service

<!-- teaches: syscall-number = system call number, system call table -->
When the program executes `syscall`, how does the kernel know whether it means `write` or `openat`? Before the trap, the program puts a **system call number** in the processor's `rax` register, and the arguments in other registers (`rdi`, `rsi`, `rdx`, and so on, in order). The kernel uses the number as an index into its *system call table*, an array of pointers to the functions that do each job. The numbers are fixed forever on a given architecture, because every compiled program on Earth has them built in. They are listed in a header file that came with your compiler:

<!-- code: id=syscall-numbers -->
```console
$ grep -w -E '__NR_(read|write|openat|close|exit_group)' /usr/include/x86_64-linux-gnu/asm/unistd_64.h
#define __NR_read 0
#define __NR_write 1
#define __NR_close 3
#define __NR_exit_group 231
#define __NR_openat 257
```


So `write` is call number 1 on x86-64 Linux. You can make that call yourself, by number, without `printf`. The C library has a general function, `syscall`, that puts its first argument in `rax`, the others in the argument registers, and executes the instruction:

<!-- code: id=rawwrite -->
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/syscall.h>

int main(void)
{
    syscall(SYS_write, 1, "hello from syscall 1\n", 21);
    return 0;
}
```
```text
hello from syscall 1
```

`SYS_write` is just the number 1 with a name. The three arguments are the same three you saw on the strace line: descriptor 1, the address of the bytes, and how many. (`#define _GNU_SOURCE` asks the C library headers to declare `syscall`, which is not part of standard C. `unistd.h` and `sys/syscall.h` are POSIX and Linux headers, not standard C: they exist because the program talks to an operating system, which is the point of this book.) No `printf`, no buffer, no library formatting; one trap, one answer.


Here is the order of events for that one call, from the program's side to the screen and back:

| Step | Mode | Where | What happens |
|---|---|---|---|
| 1 | user | your program | `syscall()` in the library puts 1 in `rax`, 1 in `rdi`, the address of the text in `rsi`, 21 in `rdx` |
| 2 | user → kernel | processor | `syscall` instruction: save the return point, switch to kernel mode, jump to the kernel's entry point |
| 3 | kernel | entry code | save the program's registers; look up entry 1 in the system call table |
| 4 | kernel | `write` handler | check descriptor 1 belongs to this process and is open for writing; check the address really lies in the process's own memory; copy the 21 bytes into the terminal's buffer |
| 5 | kernel | entry code | put the result (21, the count written) in `rax`; restore the registers |
| 6 | kernel → user | processor | `sysret`: back to user mode, at the instruction after `syscall` |
| 7 | user | your program | `syscall()` returns 21 |

Step 4 is the counter clerk checking your form. The kernel never trusts a pointer from a user program: if you had passed an address inside the kernel, it would not fault the way 1.2's `peek` did; it would refuse politely and return an error, which section 1.7 shows.

### Why so many calls, and is it a problem?

You might be alarmed: thirty-five trips to the counter for one line. Two points. First, nearly all of them are start-up, paid once. A program that prints a million lines does not make a million times thirty-five calls. Second, the design choice behind the loader's calls is *dynamic linking*: one copy of the C library on disk and in memory, shared by every program, and fixed everywhere at once when the library gets a security update. The cost is a few dozen system calls at start. You could avoid them by building with `gcc -static`, which copies the library into the program; the trace shrinks to a handful of lines, but the file grows from around 16 KB to around 800 KB and must be rebuilt for every library fix.


### When it goes wrong

- **`strace: command not found`.** Install it as above. On a locked-down machine (some school computers), you may not be allowed to; the lab can be read here instead.
- **`strace: ptrace(PTRACE_TRACEME, ...): Operation not permitted`.** Some containers and security settings forbid one process from tracing another. On your own Ubuntu laptop this does not happen for your own programs. Inside a Docker container it can.
- **The program's output and strace's lines are tangled.** They share the screen. Send strace's lines to a file with `strace -o trace.txt ./hello`, or show only some calls with `-e trace=write`.
- **"I don't see my `printf` in the trace."** You are looking for the wrong name. The kernel never hears the word `printf`; it hears `write`. Why, is the next section.

**Check yourself**

1. Predict: how many `openat` lines will `strace ./rawwrite` show, and how many `write` lines? Then run `strace ./rawwrite` and check.

<details>
<summary>Answer</summary>

Two `openat` lines (the loader cache and `libc.so.6`): `rawwrite` is still dynamically linked, because `syscall()` itself is a C library function. And one `write`: `write(1, "hello from syscall 1\n", 21) = 21`. There is no `fstat(1, ...)` before it this time, because no `printf` buffer was set up.

</details>

2. In the trace of `hello`, the C library is opened with `openat(...) = 3` and then closed. The next `openat` also returns 3. A friend says this is a bug: two files cannot have the same number. Who is right?

<details>
<summary>Answer</summary>

There is no bug. A file descriptor names an open file *only while it is open*. After `close(3)`, number 3 is free, and the kernel always hands out the lowest free number, so the next `openat` gets 3 again. At no moment are two files open under the same number.

</details>

3. Change `rawwrite.c` so it passes 100 as the count instead of 21, and predict what appears on the screen, then try it. Why does the kernel not refuse?

<details>
<summary>Answer</summary>

The kernel writes 100 bytes starting at the address of the string: the 21 bytes of text, then 79 bytes of whatever lies after it in the program's memory (often other strings, the end-of-string zero bytes, or bits of the program's data), which can show as odd characters. The kernel only checks that the 100 bytes lie inside memory that belongs to the process; it cannot know where *your* string ends. The kernel protects other processes from you, not you from yourself.

</details>

## 1.4 printf is not a system call: the C library sits in between

The kernel never hears the word `printf`. It hears `write`. Between the two sits the **C library** (glibc on Ubuntu), ordinary code that runs in user mode inside your process. Here is a program that prints three lines; count the `write` calls it makes, first to the terminal and then into a file:

<!-- code: id=lines -->
```c
#include <stdio.h>

int main(void)
{
    printf("one\n");
    printf("two\n");
    printf("three\n");
    return 0;
}
```
```text
one
two
three
```

<!-- code: id=lines-strace -->
```console
$ gcc -Wall -Wextra -g -o lines lines.c
$ strace -e trace=write ./lines
write(1, "one\n", 4one
)                    = 4
write(1, "two\n", 4two
)                    = 4
write(1, "three\n", 6three
)                  = 6
+++ exited with 0 +++
$ strace -e trace=write ./lines > out.txt
write(1, "one\ntwo\nthree\n", 14)       = 14
+++ exited with 0 +++
$ cat out.txt
one
two
three
```

<!-- teaches: libc-wrapper = C library, glibc, wrapper function -->
To the terminal: three `write` calls, one per line. Into a file: one `write` with all fourteen bytes. The program did not change; only where its output went.

<!-- teaches: stdout-buffer = stdout buffer, line buffering, full buffering, fflush -->
What happened is the **stdout buffer**. `printf` does not call the kernel. It formats your text into a block of memory inside your own process (a few kilobytes, set up on the first `printf`) and returns. The library calls `write` only when it decides to empty, or *flush*, the buffer. When it decides depends on where descriptor 1 leads, which is why `hello` asked `fstat(1, ...)` in the trace of 1.3:

| stdout leads to | Buffering | The buffer is flushed when |
|---|---|---|
| a terminal | line buffered | a `\n` is printed, the buffer fills, or the program exits |
| a file or a pipe | fully buffered | the buffer fills (typically 4096 bytes) or the program exits normally |


The reason is the cost you met in 1.2: every `write` is a trip through the door. A program writing a million short lines to a file makes about 3,000 system calls instead of a million. To a terminal, a person is watching, so the library gives up some speed to show each line as soon as it is complete.

The mistake this causes is real and common. A program prints a progress message without `\n`, or its output goes into a pipe, and then it crashes: the text is still sitting in the buffer inside the process when the process dies, and it is never written. That is why the `halt` and `peek` programs of 1.2 called `fflush(stdout)`: it means "make the `write` call now". Without it, under a pipe, the line "about to stop the whole computer" would vanish with the process. When you debug a crash with `printf`, print to `stderr` (`fprintf(stderr, ...)`), which is not buffered, or flush.

**Check yourself**

1. Predict how many `write` calls `strace -e trace=write ./lines | cat` shows, and why.

<details>
<summary>Answer</summary>

One. With `| cat`, descriptor 1 of `lines` leads to a pipe, not the terminal, so stdout is fully buffered: the three lines wait in the buffer and are written together when the program exits. strace's own lines go to the error stream, which still reaches the terminal, so you see them. The tempting answer, three, assumes that what you finally see on the screen (through `cat`) is what `lines` wrote to.

</details>

2. Remove the `\n` from all three `printf` calls in `lines.c`, run it under `strace -e trace=write` to the terminal, and predict the number of `write` calls.

<details>
<summary>Answer</summary>

One: `write(1, "onetwothree", 11)`. With no newline, the line-buffered stream never sees the end of a line, so nothing is written until the program exits and the library flushes everything at once.

</details>

## 1.5 What a process is made of: address space, registers, open files, the process table

### What does the kernel keep about `hello`?

In 1.1 you met the process as "a program in execution, plus everything the operating system keeps about it". That second half was a promise. When the timer takes the processor away from `hello` in the middle of a loop (section 1.6), and hands it back a few milliseconds later, `hello` must carry on from the exact instruction, with every variable as it was, and with its files still open at the same place. Something must remember all of that while `hello` is not running. What, exactly, and where?

### A folder of papers for each process

Think of the office from 1.1 again. For every visitor currently being served, the clerk keeps a folder: who they are, which forms they have handed in, which documents they have borrowed, and, if they were interrupted mid-sentence, a note of exactly where they were. When a visitor steps aside and comes back, the clerk opens the folder and carries on.

The kernel keeps such a folder for every process. The picture breaks in one place, which chapter 2 shows: two *threads* of one process share most of one folder, each with only its own small "where was I" note.

### Looking inside your own process

Here is a program that looks at three things the kernel keeps about it: its open files, a couple of addresses in its memory, and the map of its memory as the kernel lists it. It uses `/proc/self` from 1.1, from inside C this time, and `open`, `readlink` and `close` from the POSIX headers `fcntl.h` and `unistd.h`: these are operating-system calls, not standard C. Type it into `inside.c`:

<!-- code: id=inside varies -->
```c
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

int counter = 42;                     /* a global variable */

int main(void)
{
    int local = 7;                    /* a variable on the stack */

    int fd = open("hello.c", O_RDONLY);
    if (fd == -1) {
        perror("open hello.c");
        return 1;
    }
    printf("open gave descriptor %d\n", fd);

    /* 1. the open files of this process */
    for (int i = 0; i <= fd; i++) {
        char link[64], target[256];
        snprintf(link, sizeof link, "/proc/self/fd/%d", i);
        ssize_t n = readlink(link, target, sizeof target - 1);
        if (n == -1) {
            perror(link);
            return 1;
        }
        target[n] = '\0';
        printf("fd %d -> %s\n", i, target);
    }

    /* 2. two addresses in the address space */
    printf("counter is at %p\n", (void *) &counter);
    printf("local   is at %p\n", (void *) &local);

    /* 3. the address space as the kernel lists it */
    FILE *maps = fopen("/proc/self/maps", "r");
    if (maps == NULL) {
        perror("/proc/self/maps");
        return 1;
    }
    char line[512];
    while (fgets(line, sizeof line, maps) != NULL) {
        if (strstr(line, "/inside") || strstr(line, "[heap]") || strstr(line, "[stack]"))
            fputs(line, stdout);
    }
    fclose(maps);
    close(fd);
    return 0;
}
```
```text
open gave descriptor 3
fd 0 -> pipe:[1247662]
fd 1 -> /dev/pts/0
fd 2 -> /dev/pts/0
fd 3 -> hello.c
counter is at 0x55f2959cf010
local   is at 0x7ffcd75d61c4
55f2959cb000-55f2959cc000 r--p 00000000 fe:00 1204571                    inside
55f2959cc000-55f2959cd000 r-xp 00001000 fe:00 1204571                    inside
55f2959cd000-55f2959ce000 r--p 00002000 fe:00 1204571                    inside
55f2959ce000-55f2959cf000 r--p 00002000 fe:00 1204571                    inside
55f2959cf000-55f2959d0000 rw-p 00003000 fe:00 1204571                    inside
55f2b596d000-55f2b598e000 rw-p 00000000 00:00 0                          [heap]
7ffcd75b7000-7ffcd75d8000 rw-p 00000000 00:00 0                          [stack]
```


Your addresses, numbers in brackets and the device column will differ, and change on every run. On your machine the file names show in full, such as `/home/you/os/ch01/hello.c` and `/home/you/os/ch01/inside` (with your own user name); the run printed here shortened them. When you run it in your own terminal, descriptor 0 points to your terminal (`/dev/pts/0` or similar) like 1 and 2 do; when its input comes from a pipe or a file, as it did when this book was built, it says so. Now walk through what you are looking at.

### Part one: the open files

<!-- teaches: file-descriptor = file descriptor, standard input, standard output, standard error -->
The first lines show the process's **file descriptors**: small numbers that stand for the files this process has open. Every process starts with three, set up by the shell before your program ran: 0 is *standard input* (where `scanf` reads), 1 is *standard output* (where `printf` writes) and 2 is *standard error* (where `perror` and error messages go). When `open("hello.c", ...)` asked the kernel for a new one, it got 3, the lowest free number, as you predicted in 1.3.

The number itself is just an index. Inside the kernel, each process has a table, and entry 3 of that table points to a structure describing the open file: which file it is, whether it was opened for reading or writing, and the current *offset*, how far into the file the next `read` will start. When your program calls `read(3, buf, 100)`, the kernel looks up entry 3 in *this process's* table. That is why descriptor 3 in `inside` and descriptor 3 in another program are completely different files: each process has its own table. Chapter 6 opens up the structures behind the table (section 6.1).

### Part two: two addresses

`counter`, a global variable, and `local`, a variable inside `main`, sit at very different addresses: the global low, near where the program's file is mapped; the local high, in the region marked `[stack]`. Each is an address in this process's **address space**.

<!-- teaches: address-space = address space, memory map, /proc/self/maps -->
An **address space** is the set of addresses a process can use, and what lies at each one. Every process has its own. The map you printed is the kernel's list of it, one line per region: the address range, the permissions (`r` read, `w` write, `x` execute, `p` private), and what fills it. Read the lines you printed from the top:

| Region | Permissions | What it holds |
|---|---|---|
| `inside`, first lines | `r--p`, then `r-xp` | the program's file mapped into memory: headers, then the machine code (`x`: may be executed) |
| `inside`, last line | `rw-p` | the program's global variables; `counter` is here, which is why its address fell in this range |
| `[heap]` | `rw-p` | memory handed out by `malloc`; `printf`'s buffer from 1.4 lives here |
| `[stack]` | `rw-p` | local variables and function calls; `local` is here |

The full map also has the C library and the loader, which the filter left out (remove the `if` to see them all). Section 5.2 takes the whole layout apart; for now one thing matters. The machine code is `r-x`: readable and executable, not writable. Try to write into your own code and the processor refuses, with the same page fault you met in 1.2. The map is not a description; it is the rule the hardware enforces.

One more surprise is waiting in chapter 5: if you run `inside` twice at once, the two processes can show the very same address for `counter` with different values in it. The addresses a process sees are its own private numbering.

### Part three: what you cannot see from inside, the registers

The processor's **registers** are a few dozen fast storage cells inside the processor itself: the *instruction pointer* (`rip`, the address of the next instruction), the *stack pointer* (`rsp`, the top of the stack), and general registers holding values your code is working on right now. While your program runs, its state is in those registers, not in memory. Your program cannot print "its registers" in a meaningful way, because printing uses them.

When the kernel takes the processor away from a process, the registers are the one part of its state that would be destroyed by the next process, which needs the same registers. So the kernel copies them into the process's folder first, and copies them back before the process runs again. That copying is the *context switch* of section 1.6.

### The folder itself: the process control block

<!-- teaches: process = process, process state -->
<!-- teaches: pcb = process control block, PCB, task_struct, process table -->
Now the whole picture. A **process** is a running program together with its own address space, its saved registers, its open files, and the kernel's bookkeeping about it. The kernel's folder for one process is called the **process control block (PCB)**; on Linux it is a C structure called `task_struct`, with well over a hundred fields (its exact size depends on how the kernel was built). The kernel keeps all of them linked together in a **process table**, which is what `ps` and `top` read.


| What the PCB holds | Seen in this chapter as | Its full story |
|---|---|---|
| identity: process number (pid), parent's number | `Pid`, `PPid` in `/proc/self/status` (1.1) | 2.1 |
| state: running, ready, blocked... | `State: R (running)` (1.1) | 2.3 |
| saved registers, including the instruction pointer | not visible from inside | 1.6 |
| a pointer to the address space and its page tables | `/proc/self/maps` (above) | 5.3 |
| the table of open files | `/proc/self/fd` (above) | 6.1 |
| scheduling information: priority, CPU time used | `nice`, `top` | 3.5 |
| pending signals | the `SIGSEGV` of 1.2 | 1.7 |

<!-- fig: id=process-parts
kind: layers
title: One process: its memory, and its PCB
layer user: Address space (user mode)
in user: code = code, `counter`; heap = heap; stack = stack, `local`
layer kern: PCB in the kernel
in kern: id = pid, state, map; regs = registers; fds = fds 0 1 2 3
layer table: Process table
in table: all = every PCB, linked; ps = read by `ps`
hot: id regs fds
-->
![Layers, top to bottom. Address space (user mode) holds code, counter, heap and stack, local. PCB in the kernel holds pid, state, map, registers and fds 0 1 2 3. Process table holds every PCB, linked and read by ps. pid, state, map, registers and fds 0 1 2 3 are highlighted.](fig/01-one-programs-life/process-parts.svg)

Notice where things are. The address space is the process's own: it can read and write its heap and stack directly, no system call needed. The PCB is in kernel memory: the process cannot read or change its own pid, its state or its open-file table except by asking at the counter (`getpid`, `open`, `close`). That split is the referee job again: a process that could edit its own PCB could give itself any file or any priority.

### When it goes wrong

- **Running out of descriptors.** A program that opens files in a loop and never calls `close` eventually gets `open` returning -1 with the message `Too many open files`. The table in the PCB has a limit per process, often 1024 by default on Ubuntu (`ulimit -n` shows yours). Every `open` needs its `close`.
- **Believing a pointer means something in another process.** Writing an address to a file and reading it back in another process gives a number that points to nothing useful there: each address space has its own numbering (chapter 5).
- **Thinking `/proc` is a folder of real files on disk.** Nothing in `/proc` is stored anywhere. Each time you read `/proc/self/maps`, the kernel writes the text on the spot from the PCB. That is why it is always current, and why `ls -l` shows a size of 0.


**Check yourself**

1. `inside` opens `hello.c` and gets descriptor 3. Predict the descriptor numbers if it opened `hello.c`, then `lines.c`, then closed the first one and opened `inside.c`.

<details>
<summary>Answer</summary>

3 for `hello.c`, 4 for `lines.c`; after `close(3)`, number 3 is the lowest free one, so `inside.c` gets 3. The tempting answer, 5, assumes numbers only ever count up.

</details>

2. Run `./inside < hello.c`. Which line of the output changes, and why?

<details>
<summary>Answer</summary>

The `fd 0` line: it now points to `hello.c` (with its full path), because the shell opened the file and placed it at descriptor 0 before starting the program. The program did not change; the shell changed what its descriptor 0 leads to. (Section 2.2 shows how the shell does that.) Descriptor 3 is still `hello.c` opened by the program itself: one file, opened twice, two separate entries with their own offsets.

</details>

3. Decide: which of these does a process need a system call for, and which can it do directly? (a) changing `counter`; (b) finding its own pid; (c) reading the next byte of `hello.c`; (d) calling a function of its own.

<details>
<summary>Answer</summary>

(a) directly: `counter` is in its own address space. (b) a system call, `getpid`: the pid lives in the PCB in kernel memory. (c) a system call, `read`: the file is behind the counter, and the offset is in the kernel's open-file structure. (d) directly: its own code, in its own address space, in user mode.

</details>

## 1.6 Interrupts and the timer: how the kernel takes the CPU back

### A program that never asks

Every way into the kernel you have seen so far was started by the program: a trap when it asks (1.3), a fault when it breaks a rule (1.2). Now think about a program that does neither. A loop that adds numbers for a minute makes no system call and breaks no rule. On a laptop with one core, while that loop runs, the kernel is not running at all; the loop has the processor. So how does your mouse pointer keep moving? How does the music keep playing? If the kernel only ran when a program walked up to the counter, one busy loop would freeze the whole machine.

This is the place where the counter picture of 1.1 breaks, as promised: the clerk can walk out from behind the counter and stop you mid-sentence.

### Watching the kernel interrupt you

Here is the busy loop, with a way to see what the kernel did to it. Linux counts, in each process's `/proc/self/status`, how many times the process was switched off the processor: `voluntary_ctxt_switches` when the process gave the processor up itself (it asked for something it had to wait for, such as keyboard input), and `nonvoluntary_ctxt_switches` when the kernel took it away. The program prints both before and after a loop of one and a half billion additions. Type it into `spin.c`:

<!-- code: id=spin varies -->
```c
#include <stdio.h>
#include <string.h>

/* Print this process's context-switch counts from /proc/self/status. */
static void show_switches(const char *when)
{
    FILE *f = fopen("/proc/self/status", "r");
    if (f == NULL) {
        perror("/proc/self/status");
        return;
    }
    char line[256];
    while (fgets(line, sizeof line, f) != NULL) {
        if (strstr(line, "ctxt_switches"))
            printf("%-7s %s", when, line);
    }
    fclose(f);
}

int main(void)
{
    show_switches("before");

    volatile unsigned long sum = 0;           /* volatile: keep the loop */
    for (unsigned long i = 0; i < 1500000000UL; i++)
        sum += i;                             /* no system call in here */

    show_switches("after");
    return 0;
}
```
```text
before  voluntary_ctxt_switches:	0
before  nonvoluntary_ctxt_switches:	0
after   voluntary_ctxt_switches:	0
after   nonvoluntary_ctxt_switches:	3
```

The loop contains no system call. Yet the "after" count of non-voluntary switches is higher than the "before" one: while the loop ran, the kernel took the processor away from it several times, and gave it back, without the program noticing anything except that the loop took a little longer. Your numbers depend on how busy your laptop was; on an idle one they may be small, and the next experiment makes them large.

Now make two loops fight for one processor core. `-O0` builds it with no optimisation, so the loop stays (see "When it goes wrong" below); `taskset -c 0` runs a program only on core 0; `&` starts it without waiting, and `wait` waits for both. `time` prints how long the whole thing took on the clock (`real`), how much processor time was spent running user code (`user`), and how much inside the kernel on its behalf (`sys`). `/proc/interrupts` shows how many timer interrupts each core has received so far, on the line marked `LOC`:

<!-- code: id=spin-two varies timeout=30 -->
```console
$ gcc -Wall -Wextra -O0 -o spin spin.c
$ grep LOC /proc/interrupts
LOC:    1278192    1310329   Local timer interrupts
$ time ./spin
before  voluntary_ctxt_switches:        0
before  nonvoluntary_ctxt_switches:     0
after   voluntary_ctxt_switches:        0
after   nonvoluntary_ctxt_switches:     5

real    0m1.183s
user    0m1.167s
sys     0m0.000s
$ time (taskset -c 0 ./spin > one.txt & taskset -c 0 ./spin > two.txt & wait)

real    0m1.782s
user    0m1.758s
sys     0m0.000s
$ cat one.txt two.txt
before  voluntary_ctxt_switches:        1
before  nonvoluntary_ctxt_switches:     0
after   voluntary_ctxt_switches:        1
after   nonvoluntary_ctxt_switches:     220
before  voluntary_ctxt_switches:        0
before  nonvoluntary_ctxt_switches:     0
after   voluntary_ctxt_switches:        0
after   nonvoluntary_ctxt_switches:     221
$ grep LOC /proc/interrupts
LOC:    1278941    1310487   Local timer interrupts
```


One loop alone takes about one second. Two loops on one core take close to two seconds on the clock, and both finish at almost the same moment, each having been switched off its core hundreds of times. The core did not run one loop to the end and then the other: it ran them in turns of a few milliseconds each, so that they shared the second-by-second progress. Meanwhile the `LOC` numbers went up by hundreds per core: the timer kept firing the whole time.

### The interrupt

<!-- teaches: interrupt = interrupt, hardware interrupt, interrupt handler, interrupt vector -->
An **interrupt** is a signal from a hardware device to the processor saying "stop what you are doing and attend to me". The keyboard sends one when a key is pressed, the network card when a packet arrives, the disk when the data you asked for is ready. Between any two instructions, the processor checks whether an interrupt is waiting. If one is, it does what you saw it do for a trap and a fault in 1.2: save where it was, switch to kernel mode, and jump to the kernel's **interrupt handler** for that device, found in a table (the *interrupt vector*) that the kernel filled at boot.

So there are three doors into the kernel, and they are the same mechanism:

| Door | Who starts it | When | Example |
|---|---|---|---|
| trap | the program, on purpose | at a `syscall` instruction | `write` (1.3) |
| fault | the program, by accident | when an instruction breaks a rule | `hlt`, a bad pointer (1.2, 1.7) |
| interrupt | a device, from outside | between any two instructions | a key press, the timer |

The first two happen *because of* the instruction the program is running. An interrupt has nothing to do with the program at all; it can arrive in the middle of your loop, at any instruction, and your program is not told.

<!-- teaches: timer-interrupt = timer interrupt, timer tick, time slice -->
### The timer: an alarm clock the kernel sets for itself

One device exists mainly for the kernel's sake: the **timer**. At boot, while still in kernel mode, the kernel programs a hardware timer on each core to raise an interrupt after a fixed short interval, again and again. Each such **timer interrupt** (also called a *tick*) carries the processor into the kernel, whatever program is running. The kernel looks at how long the current process has had the core. If its share is used up and another process is waiting, the kernel switches; if not, it simply returns to the same program, which carries on, a microsecond or so later.


This is why the user-mode program cannot hold the processor forever: the timer was armed in kernel mode, and the instruction that would switch it off, or switch off interrupts (`cli`), is privileged. You met that rule in 1.2; here is what it protects. If `cli` were allowed in user mode, `for (;;) ;` after a `cli` would freeze a single-core machine for good.

Taking the processor away from a running process without asking it is called *preemption*, and chapter 3 is about deciding whom to give it to next (section 3.4 on time slices in particular). Here the question is only *how* the switch happens.

<!-- teaches: context-switch = context switch, saving registers, kernel stack -->
### The context switch, step by step

Two processes, A (your first `spin`) and B (the second), both ready, one core. A is running. Here is one switch, in order:

| Step | Mode | Who | What happens | Where A's state is |
|---|---|---|---|---|
| 1 | user | A | adding numbers; `rip` points into the loop | in the registers |
| 2 | user → kernel | timer, processor | the tick arrives; the processor saves A's `rip`, `rsp` and flags on A's kernel stack and jumps to the timer handler | partly in registers, partly saved |
| 3 | kernel | timer handler | it adds the time used to A's account in A's PCB; A's share is used up and B is ready, so it calls the scheduler | |
| 4 | kernel | scheduler | it picks B (chapter 3 says how) | |
| 5 | kernel | switch code | it saves A's remaining registers into A's PCB and kernel stack, marks A as ready, not running | all in A's PCB |
| 6 | kernel | switch code | it loads B's saved registers from B's PCB, switches to B's address space (its page tables, 5.3), and marks B running | |
| 7 | kernel → user | processor | return from the interrupt, using B's saved `rip`: B carries on from the exact instruction where it was stopped last time | still in A's PCB |
| ... | | | a few milliseconds later, another tick; the same steps with A and B swapped | |
| n | kernel → user | processor | A's registers are loaded back from its PCB; A's loop continues as if nothing happened | in the registers |

That is a **context switch**: saving the state of the running process into its PCB and loading the state of another from its PCB, so that the other continues exactly where it stopped. "Context" is just a name for everything in the registers that the process needs in order to carry on. The PCB of 1.5 is where it waits.

Notice what A never sees. Between step 1 and step n, A executed no instruction at all. When it resumes, its registers, its stack, its variables are as they were. Only the clock moved. That is the illusionist job of 1.1: every process is written as if it had the processor to itself, and the kernel keeps up the illusion by saving and restoring.

### What a switch costs

A switch is not free. The direct cost is the handler and the saving and loading, on the order of a few microseconds. The indirect cost is larger: the processor's caches and the address-translation cache (the TLB, section 5.4) were full of A's data; after the switch, B runs slowly for a while until its own data is loaded again. That is why the kernel does not switch every microsecond: turns of a few milliseconds keep the cost to a small share of the time, while still feeling instant to a human. Choosing that length is a trade-off you will work through in section 3.4.


In the experiment, two spins on one core took no more than twice as long as one (about 1.8 s against 1.2 s here). If switches were very expensive, they would take noticeably longer than twice. They did not: hundreds of switches cost a few milliseconds in all.

### Voluntary and non-voluntary

The two counters in `/proc/self/status` now make sense. A **non-voluntary** switch is the one in the table: the timer fired, the kernel decided A's turn was over. A **voluntary** switch happens when the process enters the kernel with a system call that has to wait: `read` from the keyboard when no key has been pressed, for instance. The kernel cannot finish the call yet, so it marks the process as waiting and switches to someone else, through the same steps 5 to 7. When the key arrives (an interrupt from the keyboard), the kernel marks the process ready again. Chapter 2 names these states (2.3).

`spin` has almost no voluntary switches: it never asks for anything it must wait for, except perhaps when reading `/proc` at the very start. A text editor waiting for your typing has almost only voluntary ones.

### When it goes wrong

- **"My program is slow because of context switches."** Usually it is not: a few hundred switches a second cost well under one percent. The cases where switches really hurt involve thousands of threads waking each other constantly (chapter 4).
- **Measuring with `time` and believing `real`.** On a busy laptop, `real` includes the time your program sat waiting for its turn. `user` and `sys` count only the time it actually ran. In the two-loop experiment, `user` (about 1.8 s) is the processor time of both programs together, under a second each, yet each program sat about 1.8 s on the clock.
- **Timing a loop that the compiler removed.** Compile `spin.c` with `-O2` and without `volatile`, and the loop may vanish: the compiler sees that `sum` is never used and deletes it. The program finishes instantly and the switch counts stay at zero. That is why `sum` is `volatile` and the experiment is built with `-O0`.

**Check yourself**

1. Predict: if you run `taskset -c 0 ./spin` three times at once (three `&` and a `wait`), roughly how long will the whole thing take on the clock, and what will each program's own `user` time be?

<details>
<summary>Answer</summary>

About three times one run, roughly three seconds of `real` time, because three processes share one core in turns. Each process's own processor time stays about one second: the work did not grow, only the waiting. The tempting answer is "all three take three seconds of processor time each".

</details>

2. Which door into the kernel is used at each moment? (a) your `printf` finally empties its buffer; (b) the music player gets a turn while `spin` runs; (c) `spin` reads `/proc/self/status`; (d) a program executes `cli`.

<details>
<summary>Answer</summary>

(a) a trap: the `write` system call. (b) an interrupt: the timer tick, after which the scheduler picks the music player. (c) a trap: `openat` and `read` system calls. (d) a fault: `cli` is privileged, so a general protection fault, and the process is killed with `SIGSEGV`.

</details>

3. Decide: a student proposes to make programs faster by asking the kernel to switch only every two seconds. What would get better, and what would a person at the laptop notice?

<details>
<summary>Answer</summary>

Fewer switches means less time spent switching and fewer cold caches, so a long batch computation finishes slightly faster. But with two seconds per turn, the mouse, keyboard and music would stall for up to two seconds whenever a busy process held the core: the machine would feel frozen. The few-millisecond turn is a trade-off between the cost of switching and how quickly every process gets a turn, which chapter 3 (3.4) measures.

</details>

## 1.7 When a step fails: errno, a bad pointer and a segmentation fault

### Two ways to fail

Every trip to the counter so far ended well: the kernel said yes. Real programs ask for files that do not exist, and real programs have bugs. What happens then depends on which door the program came through. Ask for something impossible with a system call, and the clerk hands back a polite rejection with a reason; your program carries on and decides what to do. Do something forbidden by accident, with a bad pointer, and the processor drags you to the counter as in 1.2, and the process usually dies. Knowing which is which, and reading the evidence each leaves, is most of debugging a C program.

### The polite rejection

Here is a program that makes two requests the kernel must refuse: opening a file that does not exist, and asking `write` to read bytes from a kernel address (the experiment promised in 1.3). It uses the POSIX calls `open` and `write` (headers `fcntl.h` and `unistd.h`, not standard C). Type it into `oops.c`:

<!-- code: id=oops -->
```c
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

int main(void)
{
    int fd = open("no-such-file.txt", O_RDONLY);
    if (fd == -1) {
        printf("open returned -1, errno is %d (%s)\n", errno, strerror(errno));
        perror("open no-such-file.txt");
    }

    /* hand the kernel an address that is not ours to read from */
    const char *kernel = (const char *) 0xffffffff81000000UL;
    ssize_t n = write(1, kernel, 10);
    if (n == -1)
        perror("write from a kernel address");

    return 0;
}
```
```text
open returned -1, errno is 2 (No such file or directory)
open no-such-file.txt: No such file or directory
write from a kernel address: Bad address
```

<!-- teaches: errno = errno, error number, perror, strerror -->
Neither failure crashed anything. Each system call returned **-1**, the C library's sign that the kernel refused, and set a global variable called **errno** to a number saying why. `errno` 2 is `ENOENT`, "no such file or directory"; the second request got `EFAULT`, "bad address". `strerror` turns the number into the text, and `perror` prints your own words, a colon and that text, to standard error. The program then carried on to `return 0`.

Compare with 1.2's `peek`, which read the same kernel address with an ordinary `*kernel` and died. Same address, opposite outcome. The difference is the door. `peek` touched the address itself, in user mode, and the processor faulted. `oops` handed the address to the kernel and asked it to read; the kernel, which never trusts a pointer from a user program (step 4 of the table in 1.3), checked the address, found it outside the process's own memory, and returned an error instead of touching it.

Watch both rejections from the kernel's side:

<!-- code: id=oops-strace -->
```console
$ gcc -Wall -Wextra -g -o oops oops.c
$ strace -e trace=openat,write ./oops 2>&1 | cat
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "no-such-file.txt", O_RDONLY) = -1 ENOENT (No such file or directory)
write(2, "open no-such-file.txt: No such f"..., 49open no-such-file.txt: No such file or directory
) = 49
write(1, 0xffffffff81000000, 10)        = -1 EFAULT (Bad address)
write(2, "write from a kernel address: Bad"..., 41write from a kernel address: Bad address
) = 41
write(1, "open returned -1, errno is 2 (No"..., 57open returned -1, errno is 2 (No such file or directory)
) = 57
+++ exited with 0 +++
```

Read the trace. The kernel's own answer is on each line: `openat(AT_FDCWD, "no-such-file.txt", O_RDONLY) = -1 ENOENT (No such file or directory)` and `write(1, 0xffffffff81000000, 10) = -1 EFAULT (Bad address)`. In the kernel, a failing call really returns a small negative number (-2 for `ENOENT`); the C library's wrapper turns that into the -1 and `errno` your C code sees. strace shows you the kernel's side.

There is a surprise in the order of the lines, too. The `perror` message for `write` appears *before* the `printf` line about `open`, although the program printed them the other way round. Section 1.4 explains it: with `| cat` on the end, standard output leads to a pipe, so `printf`'s text waited in the buffer until the program exited, while `perror` writes to standard error, which is not buffered, at once. On your terminal the order would look right. Output order is one more piece of evidence to read with care.

### Rules for errno

Three rules, each learned by someone the hard way:

1. **Check the return value first, then read `errno`.** `errno` is only meaningful right after a call that returned failure. A successful call may leave an old value in it, so `if (errno != 0)` on its own is a bug.
2. **Read it at once.** Any other library call, even `printf`, may change `errno`. Save it (`int e = errno;`) if you must do something else first.
3. **Always print the reason.** `perror("open hello.c")` costs one line and turns a mystery into `open hello.c: No such file or directory`. This book does it for every system call (it is habit 2 of the book).


### The fault: a bad pointer

Now the other way to fail. Type this into `null.c`:

<!-- code: id=null mode=crash nosan -->
```c
#include <stdio.h>

int main(void)
{
    int *p = NULL;
    printf("about to write through a NULL pointer\n");
    fflush(stdout);
    *p = 42;
    printf("wrote 42\n");
    return 0;
}
```
```text
about to write through a NULL pointer
Segmentation fault
```

<!-- code: id=null-strace exit=139 -->
```console
$ gcc -Wall -Wextra -g -o null null.c
$ strace ./null 2>&1 | tail -3
) = 38
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=NULL} ---
+++ killed by SIGSEGV +++
$ ./null
about to write through a NULL pointer
Segmentation fault
```

<!-- teaches: segfault = segmentation fault, SIGSEGV, signal, core dump -->
This is a **segmentation fault**: the process touched an address that is not part of its address space, or touched it in a way the map does not allow (writing to read-only code, for example). The strace lines above show it: `--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=NULL} ---`. `SEGV_MAPERR` means "no mapping at this address", and `si_addr=NULL` is the address the program tried to use. Compare 1.2's `hlt`, where `si_code` was `SI_KERNEL`: same signal, different cause, and strace tells them apart.

Here is the order of events, with the parts you met in this chapter:

| Step | Mode | What happens |
|---|---|---|
| 1 | user | `*p = 42` becomes a machine instruction "store 42 at the address in this register"; the register holds 0 |
| 2 | user → kernel | the processor looks address 0 up in the process's map (section 5.3 shows how); there is nothing there; it raises a *page fault* and jumps to the kernel |
| 3 | kernel | the page-fault handler checks the process's list of regions, the same list `/proc/self/maps` printed in 1.5; address 0 is in none of them |
| 4 | kernel | it is the program's mistake, not something the kernel can fix by loading data (that other case is section 5.5), so the kernel sends the process the signal `SIGSEGV`, number 11 |
| 5 | kernel | `null.c` set no handler for that signal, so the default action applies: end the process (and, if allowed, write a *core dump*, a file holding its memory for a debugger) |
| 6 | kernel | the memory and files of the process are released; its parent learns it died of signal 11 |
| 7 | user (bash) | bash prints `Segmentation fault` (with `(core dumped)` if a dump was written); the exit status `$?` is 139, which is 128 + 11 |


A **signal** is the kernel's way of telling a process that something happened to it: a fault, a Ctrl-C from the keyboard (`SIGINT`), a request to stop. The PCB keeps the list of signals waiting for the process (the "pending signals" row of the table in 1.5). Signals get more use in chapter 2.

Why is address 0 never mapped? On purpose. The kernel leaves the lowest addresses of every process empty, so that the most common pointer bug, using a pointer that was never set or was set to `NULL`, crashes at once and visibly instead of quietly corrupting data. The crash is the protection working.


### Finding the line that crashed

The process is dead and the message names no line. Since you compile with `-g`, the debugger can name it. Run the program inside gdb with `gdb -q ./null`, type `run`, and when it stops, `bt` (backtrace): it names `main` at `null.c` and the line number of `*p = 42`. Type `quit` to leave. If gdb is not installed, `sudo apt install gdb`. The other tool worth knowing is the address sanitizer: `gcc -g -fsanitize=address null.c -o null` builds a program that, at the crash, prints the file, the line and what kind of bad access it was.


### When it goes wrong

- **A crash that comes and goes.** A pointer that is not set at all (as opposed to `NULL`) holds whatever was in that memory before. Sometimes that is an address inside the process, and the program writes somewhere wrong and carries on; sometimes it is not, and it crashes. Turn on `-Wall -Wextra` (gcc often warns "may be used uninitialized") and use the sanitizer.
- **"It crashes but my debug printf never appears."** The text was in the stdout buffer when the process died (1.4). Use `fprintf(stderr, ...)` or `fflush(stdout)` before the suspect line.
- **Mistaking -1 for a crash.** A failed `open` is not a crash and does not end the program; if you ignore the -1 and pass it to `read`, `read` fails too, with `EBADF` (bad file descriptor), and the real cause is lines earlier. Check every return value where it happens.
- **Reading `errno` after success.** See rule 1.

**Check yourself**

1. Predict what this prints, and whether the program survives: `char *s = "hello"; s[0] = 'j'; printf("%s\n", s);`. Use what `/proc/self/maps` showed in 1.5.

<details>
<summary>Answer</summary>

It crashes with `Segmentation fault` before printing. A string literal is stored with the program's read-only data, in a region mapped without `w`. Writing to it makes the processor fault (a page fault on a write to a read-only page), and the kernel sends `SIGSEGV`. strace shows `si_code=SEGV_ACCERR` ("access error": the address exists, the permission does not), not `SEGV_MAPERR`. The fix is `char s[] = "hello";`, which copies the text into a writable array on the stack.

</details>

2. A program prints `read: Bad file descriptor`. The `read` line looks fine. Where do you look, and what do you expect to find?

<details>
<summary>Answer</summary>

Look at where the descriptor passed to `read` came from: almost always an `open` a few lines earlier that returned -1, which the program did not check. Its `errno` (for example `ENOENT`) is the real cause, lost because the next call overwrote it. The cure is checking `open` right where it is called.

</details>

3. Decide: `oops` handed the kernel a bad address and survived; `peek` touched it and died. Why does the kernel not simply kill a process that passes it a bad pointer, to be consistent?

<details>
<summary>Answer</summary>

A system call is a request, and a request can be refused with a reason; the program may have a sensible way to recover (try another file, report the error), and only the program knows that. The kernel checks every pointer it is handed precisely so that a bad one cannot make the *kernel* fault on the program's behalf. A fault in user mode, on the other hand, happens in the middle of the program's own instruction: there is no request to refuse and no return value to give, so the only choices are a signal handler the program set up, or the default, ending the process.

</details>

## 1.8 Practice: predict, then strace, three small programs

These tasks climb from a guided prediction to a small program of your own. For each, **write your prediction down before you run anything**: which system calls, in what order, with which descriptor numbers and byte counts. The prediction is the exercise; strace is only the marking scheme. Work in `~/os/ch01` as before. The book's habits apply to everything you write: `gcc -Wall -Wextra -g`, and every system call checked with `perror` on failure.

### Task 1 (guided): a file instead of the screen

This program writes three lines to a file with the C library's `fopen` and `fprintf`, then prints `saved`. Type it into `fileout.c`.

<!-- code: id=fileout -->
```c
#include <stdio.h>

int main(void)
{
    FILE *f = fopen("notes.txt", "w");
    if (f == NULL) {
        perror("fopen notes.txt");
        return 1;
    }
    fprintf(f, "processes\n");
    fprintf(f, "threads\n");
    fprintf(f, "scheduling\n");
    if (fclose(f) != 0) {
        perror("fclose notes.txt");
        return 1;
    }
    printf("saved\n");
    return 0;
}
```
```text
saved
```

Before running it under strace, predict: (a) which system call `fopen` becomes, with which descriptor number as its result; (b) how many `write` calls go to that descriptor, and with how many bytes; (c) when they happen: at each `fprintf`, or later; (d) what `fclose` becomes. Then run `strace -e trace=openat,write,close ./fileout` and compare.

<details>
<summary>Answer</summary>

<!-- code: id=fileout-strace -->
```console
$ gcc -Wall -Wextra -g -o fileout fileout.c
$ strace -e trace=openat,write,close ./fileout 2>&1 | grep -v -E 'ld.so.cache|libc.so'
close(3)                                = 0
close(3)                                = 0
openat(AT_FDCWD, "notes.txt", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3
write(3, "processes\nthreads\nscheduling\n", 29) = 29
close(3)                                = 0
write(1, "saved\n", 6saved
)                  = 6
+++ exited with 0 +++
$ cat notes.txt
processes
threads
scheduling
```

(a) `fopen(..., "w")` becomes `openat(AT_FDCWD, "notes.txt", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3`: open for writing, create if missing, empty it if present. Descriptor 3, the lowest free number. (b) One `write(3, ...)` with all 29 bytes: a `FILE` opened on a file is fully buffered (1.4). (c) At `fclose`, not at any `fprintf`: closing flushes the buffer first. (d) `close(3)`. The two `close(3)` lines at the top belong to the loader (the cache and the library from 1.3), which is why the descriptor was free again. `saved` is a separate `write(1, ...)` to the terminal.

The usual wrong prediction is three writes, one per `fprintf`. The second most usual is forgetting that the file's mode `0666` is further reduced by your *umask* (usually 0002 or 0022), so `ls -l notes.txt` shows `-rw-rw-r--` or `-rw-r--r--`, not `-rw-rw-rw-`.


</details>

### Task 2 (guided): a program that waits for you

This one reads a word from the keyboard. Type it into `echoline.c` and run it; type a word and press Enter.

<!-- code: id=echoline stdin="ping\n" -->
```c
#include <stdio.h>

int main(void)
{
    char line[100];
    printf("type a word: ");
    fflush(stdout);
    if (fgets(line, sizeof line, stdin) == NULL) {
        fprintf(stderr, "no input\n");
        return 1;
    }
    printf("you typed: %s", line);
    return 0;
}
```
```text
type a word: you typed: ping
```

Predict: (a) on which descriptor the program asks for input, and with which system call; (b) how many bytes it asks for and how many it gets when you type `ping` and Enter; (c) what the process is doing, in the terms of 1.6, while you have not typed anything yet; (d) why the program calls `fflush(stdout)` after the prompt, given that standard output is a terminal.

<details>
<summary>Answer</summary>

<!-- code: id=echoline-strace stdin="ping\n" -->
```console
$ gcc -Wall -Wextra -g -o echoline echoline.c
$ strace -e trace=read,write ./echoline 2>&1 | grep -v ELF
write(1, "type a word: ", 13type a word: )           = 13
ping
read(0, "ping\n", 1024)                 = 5
write(1, "you typed: ping\n", 16you typed: ping
)       = 16
+++ exited with 0 +++
```

(a) `read(0, ...)`: descriptor 0, standard input. (The `grep -v ELF` hides the loader's `read` of the C library from 1.3.) (b) It asks for 1024 bytes, the size of the C library's input buffer, not the 100 of your array; it gets 5, `"ping\n"`: on a terminal, `read` returns as soon as one line is complete. (c) It is blocked inside the `read` system call: the kernel cannot answer yet, so it switched to another process (a *voluntary* switch, 1.6). The keyboard interrupt that comes with your Enter key makes it ready again. (d) The prompt has no `\n`, so it waits in the buffer. Typed straight at your terminal, glibc happens to flush standard output itself before it reads from the keyboard, so the prompt would show anyway; but in the trace above standard output is a pipe (`| grep`), fully buffered, and without the `fflush` the prompt's `write` comes after the `read`, joined to the answer as one `write(1, "type a word: you typed: ping\n", 29)`. `fflush` puts the prompt on the screen before the wait wherever the output goes.


</details>

### Task 3 (on your own): find the fault from the trace

A classmate's program is meant to print the first line of `config.txt`. It prints nothing, and does not crash. Here are its last strace lines; the program itself is not shown.

<!-- code: id=fault-trace mode=fragment -->
```text
openat(AT_FDCWD, "config.txt", O_RDONLY) = -1 ENOENT (No such file or directory)
read(-1, 0x7ffd4c0b9e10, 100)           = -1 EBADF (Bad file descriptor)
exit_group(0)                           = ?
+++ exited with 0 +++
```

From these lines alone, say: what the program did, which two checks it is missing, and what it should have printed. Then say what one change to the *program's exit* would let a script that runs it notice the failure.

<details>
<summary>Answer</summary>

It called `open("config.txt", O_RDONLY)`, which failed with `ENOENT` because the file is not in the current folder. It did not check the -1 and passed it straight to `read`, which failed with `EBADF`: -1 is not a descriptor. It did not check that either, printed nothing, and ended with status 0, "success". The missing checks: `if (fd == -1) { perror("config.txt"); return 1; }` after `open`, and a check of `read`'s -1. It should have printed `config.txt: No such file or directory` to standard error. Returning a non-zero status (1) on failure lets the shell and scripts see it with `$?` or `&&`. Note the real cause is the *first* failing line in the trace, not the last.

</details>

### Task 4 (small project): your own `cp`, by system calls only

Write `copy.c` with the POSIX headers `fcntl.h` and `unistd.h` (not standard C), a program run as `./copy FROM TO` that copies a file using only `open`, `read`, `write` and `close`: no `FILE`, no `fopen`, no `printf` except for errors. Requirements:

- a buffer of 4096 bytes, read and written in a loop until `read` returns 0 (end of file);
- every system call checked, with `perror` naming the file on failure, and a non-zero exit;
- the new file created with permissions `0644`, and emptied if it already exists;
- a wrong number of arguments gives a usage message on standard error and exit status 2.

Then, **before running it**, predict exactly the `read` and `write` calls (descriptor, size asked, result) for copying a file of 10,000 bytes, which `head -c 10000 /dev/zero > big.bin` makes. Check with strace, and check the copy with `cmp`.

<details>
<summary>Answer</summary>

One way to write it:

<!-- code: id=copy args="hello.c hello-copy.c" -->
```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

#define CHUNK 4096

int main(int argc, char *argv[])
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s FROM TO\n", argv[0]);
        return 2;
    }
    int in = open(argv[1], O_RDONLY);
    if (in == -1) {
        perror(argv[1]);
        return 1;
    }
    int out = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out == -1) {
        perror(argv[2]);
        close(in);
        return 1;
    }

    char buf[CHUNK];
    ssize_t got;
    while ((got = read(in, buf, sizeof buf)) > 0) {
        ssize_t done = 0;
        while (done < got) {                  /* write may write less than asked */
            ssize_t put = write(out, buf + done, got - done);
            if (put == -1) {
                perror("write");
                return 1;
            }
            done += put;
        }
    }
    if (got == -1) {
        perror("read");
        return 1;
    }
    close(in);
    close(out);
    return 0;
}
```

With 10,000 bytes and a 4096-byte buffer: `read(3, ..., 4096) = 4096`, `write(4, ..., 4096) = 4096`, again 4096 and 4096, then `read = 1808` and `write(4, ..., 1808) = 1808` (10,000 − 8,192 = 1,808), and finally `read(3, "", 4096) = 0`: end of file, the loop stops. Four `read` calls, three `write` calls. The source is descriptor 3 and the new file is 4, because they were opened in that order.

<!-- code: id=copy-strace -->
```console
$ gcc -Wall -Wextra -g -o copy copy.c
$ head -c 10000 /dev/zero > big.bin
$ strace -e trace=read,write ./copy big.bin copy.bin 2>&1 | grep -v ELF
read(3, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
write(4, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
read(3, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
write(4, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
read(3, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 1808
write(4, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 1808) = 1808
read(3, "", 4096)                       = 0
+++ exited with 0 +++
$ cmp big.bin copy.bin && echo same
same
```

The inner loop around `write` matters: `write` may write fewer bytes than asked (to a pipe or a network connection it often does), and a copy that ignores the count silently loses data. To a regular file on your disk it almost never happens, which is why the bug survives testing.

</details>

### Task 5 (design): how big should the buffer be?

Change `CHUNK` to 1 and copy a file of one million bytes (`head -c 1000000 /dev/zero > mb.bin`), timing it with `time` against the 4096 version. Before you do, predict: how many system calls will the 1-byte version make, and roughly how much slower will it be? Then answer the design question: why not use a buffer of 100 MB, so that any file is copied in one `read` and one `write`?

<details>
<summary>Answer</summary>

With a 1-byte buffer, a million bytes take a million `read` calls and a million `write` calls, plus one final `read` returning 0: about two million trips through the door of 1.2, against about 490 with 4096 bytes. At a few hundred nanoseconds per call, that is around half a second, compared with a few milliseconds: hundreds of times slower, most of it in `sys` time (on the machine this book was built on: 0.48 s against 0.002 s, 0.31 s of it `sys`). Run it with `time` to see your own numbers.

A 100 MB buffer goes too far the other way. It needs 100 MB of memory for every copy, even for a 10-byte file; a 2 GB file still does not fit; and almost nothing is saved, because at 4096 bytes the system calls are already a tiny part of the time: the disk and the copying of bytes cost the same whatever the buffer size. Past a few tens of kilobytes, bigger buffers stop helping. The same trade-off is why the C library chose a buffer of a few kilobytes for `stdout` (1.4).


</details>
