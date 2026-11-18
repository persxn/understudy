### 12 File handling
12.1 Why files: data that outlives the program | teaches: file, persistence, text-file | needs: C1.FILES_TERMINAL, C10.PROCESS
12.2 Opening and closing a file: fopen(), FILE * and modes | teaches: fopen, file-pointer, file-mode, fclose, fopen-null-check | needs: C8.POINTER_IDEA, C8.NULL_POINTER, C1.INCLUDE_STDIO
12.3 Writing text: fprintf(), fputs() and fputc() | teaches: fprintf, fputs, fputc, write-vs-append | needs: C1.PRINTF, C1.SPECIFIER_IDEA
12.4 Reading text: fgetc(), fgets() and EOF | teaches: fgetc, eof, fgets-file, read-loop | needs: C5.FGETS, C1.CHAR_AS_NUMBER, C3.WHILE
12.5 Reading formatted data: fscanf() and sscanf() | teaches: fscanf, fscanf-return, sscanf, line-then-parse | needs: C1.SCANF, C5.STRING_IDEA
12.6 stdin, stdout and stderr are files too | teaches: standard-streams, stderr, redirection, filename-argument | needs: C8.ARGV
12.7 When things go wrong: errno, perror(), feof() and ferror() | teaches: errno, perror, ferror, feof-trap, exit-status | needs: C1.RETURN_ZERO | level: 2
12.8 Buffering: why your writes arrive late, and fflush() | teaches: stream-buffer, buffer-modes, fflush, lost-output | needs: C7.MEMORY_HIERARCHY | level: 2
12.9 Text mode and binary mode: what is really on disk | teaches: text-vs-binary, binary-mode, newline-translation | needs: C5.ASCII_TABLE, C1.BYTES | level: 2
12.10 fwrite() and fread(): arrays and structs on disk | teaches: fwrite, fread, struct-on-disk, item-count | needs: C9.STRUCT_DEFINE, C1.SIZEOF, C5.ARRAY_DECLARE | level: 2
12.11 Moving around a file: fseek(), ftell() and rewind() | teaches: file-position, fseek, ftell, rewind, random-access, update-mode | needs: C9.STRUCT_ARRAY | level: 2
12.12 Why raw structs make fragile files: padding, endianness and pointers | teaches: file-format, portability-traps, serialise | needs: C9.PADDING, C7.ENDIANNESS | level: 4
12.13 Underneath: the operating system, system calls and file descriptors | teaches: operating-system, system-call, file-descriptor, open-read-write, stdio-on-syscalls | needs: C10.VIRTUAL_MEMORY, C7.IO_DEVICES | level: 2
12.14 From kernel to disk: the page cache, fsync() and saving safely | teaches: page-cache, fsync, atomic-save, remove-rename | level: 4
12.15 Capstone: the student records system, saved to disk | teaches: records-file-capstone | needs: C9.RECORDS_CAPSTONE, C10.VECTOR | level: 3
12.16 Practice: files | practice | teaches: file-practice | level: 5
