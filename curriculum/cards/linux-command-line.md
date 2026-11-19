# linux-command-line: the Linux shell for people who will run their own software on servers
kind: tool
aliases: linux, bash, shell, terminal, shell scripting
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: missing.csail.mit.edu/2020 (shell, scripting, environment); TLCL contents (nostarch.com);
  man7.org ssh, ssh-keygen, sshd_config, systemd.service, systemd.timer, journalctl, crontab, ss, ip-address; dig,
  rsync manuals; steam-for-linux issue 3671 (a script deleting user files); the rest run in /tmp, as root and as
  `nobody`
unverified: `ssh`, `ss`, `dig`, cron and live systemd (steps 9, 10, 12, 13): man pages only, not run here

## Promise
Work on a remote Linux machine: find and change files, chain tools, run a service and read its logs, write scripts that fail safely, knowing what each command changes.

## The one idea
The shell turns a line into a program name and arguments, starts the program and reports its exit status. Picture: a clerk who rewrites your note (expands `*`, `$VAR`, `~`, wires `>` and `|`) before passing it on. Where it breaks: the program sees only the rewrite, so quoting decides what arrives.

## In production
- Software runs as services on servers reached by `ssh`, diagnosed from logs.
- Scripts run by cron or timers fail loudly, never half-way.

## Teaching order
1. The shell runs programs: arguments, `$PATH`, `type`, `man`, `--help`; exit status `$?`; `"..."` (one argument, `$` expanded) against `'...'` (literal); globs expanded first, checked with `echo`; Tab completion, `history`, Ctrl-R.
2. The file tree: `/`, `~`, absolute and relative paths; `cd`, `ls -la`, `mkdir -p`, `cp -r`, `mv`, `rm`, `ln -s`; `/etc`, `/var/log`, `/tmp`, `/proc`.
3. Reading, finding, editing: `less`, `head`, `tail -f` (`-F` survives log rotation); `find -name -type -mtime`; `grep -rn`, `-v`, `-E` with a first regular expression; `nano`, or enough `vim` to save and quit.
4. Streams and pipes: stdin, stdout, stderr; `>`, `>>`, `> file 2>&1`, `|`, `tee`; `sort`, `uniq -c`, `cut`, `wc -l`, `find -print0 | xargs -0`; one `sed 's/a/b/'`, one `awk '{print $1}'`, on a real log.
5. Permissions: `id`, the mode in `ls -l`, `chmod 640`, `chmod u+x`, `chown user:group`; `r`, `w`, `x` on a directory; the sticky bit on `/tmp`; what root skips; `sudo`, `sudoedit`; packages by `apt` or `dnf`.
6. Processes and signals: `ps aux`, `top`; `kill` (SIGTERM, can be caught) against `kill -9` (SIGKILL, cannot); Ctrl-C, Ctrl-Z, `jobs`, `bg`, `fg`, `&`; SIGHUP, `tmux`, `nohup`; exit status 128 + signal number.
7. Environment and start-up files: `env`, `export`, a child gets a copy; `source`; login shells read `~/.bash_profile` (or `~/.profile`), interactive ones `~/.bashrc`, scripts neither; `alias`.
8. Scripts that fail safely: `#!/usr/bin/env bash`, `"$@"`, `if`, `for`, `while read -r`, `case`, functions; `set -euo pipefail` and its holes; every variable quoted, `"${DIR:?}"`; `mktemp` with `trap 'rm -f "$tmp"' EXIT`; `shellcheck`.
9. A remote machine: `ssh`, `ssh-keygen`, `~/.ssh/authorized_keys` on the server, `~/.ssh/config`, `ssh -L` to a server-only port; `scp`, `rsync -av --dry-run` (a source `dir/` copies its contents); `tar czf`, `tar xzf`.
10. Services and logs: `/etc/systemd/system/app.service` (`ExecStart`, `User`, `Restart`); `systemctl daemon-reload`, `restart`, `status`, `enable --now`; `journalctl -u app -f`, `--since`, `-p err`; `/var/log`.
11. Disks and memory: `df -h`, `df -i`, `du -sh * | sort -h`, `free -h` read by "available"; a deleted file held open (`lsof +L1`, `/proc/PID/fd`).
12. The network from a shell: `ip addr`, `ss -ltnp` (who listens where; others' processes need `sudo`), `curl -v`, `dig`: "not listening" told from "not reachable" (why: networking-basics).
13. Scheduled jobs: `crontab -e`, its five time fields, a job's bare environment (`SHELL=/bin/sh`, no start-up files), `%` as newline, output to a log; a systemd timer (`OnCalendar=`, `systemctl list-timers`).

## State and danger
- [2,5,10] Files with owner and mode; configuration in `/etc`, your units in `/etc/systemd/system` (packages':
  `/usr/lib/systemd/system`); `rm` has no undo.
- [1,8] `rm -rf "$DIR/"*` with `DIR` unset is `rm -rf /*` (`--preserve-root` guards only `/`). Safe: `set -u` or `"${DIR:?}"`; `echo` the line first.
- [4] `sort f > f` leaves `f` empty (`>` truncates before the command runs). Safe: `set -o noclobber`; write elsewhere, then `mv`.
- [5] `chmod -R 777` lets anyone replace the files; old modes are lost. Safe: the least right on one path (`640`, `750`).
- [6] `kill -9` first: no cleanup, a `trap ... EXIT` never runs. Safe: `kill`, wait, then `-9`.
- [5,10] Editing as root: a typo in `sudoers` or `sshd_config` locks you out; `sudo cmd > /etc/f` fails (your shell opens `f`). Safe: a copy first, `visudo`, `cmd | sudo tee f`, a second session.
- [9] `rsync --delete` with a wrong trailing slash deletes at the wrong level. Safe: `--dry-run` first.

## Step notes
### 1
Need: The file is right there in `ls`; why does my command say "No such file or directory" twice?
Show: `f="my report.txt"`, a two-line `args.sh` printing each argument in brackets. `./args.sh $f`: `[my]
[report.txt]`; `"$f"`: one; `'$f'`: `[$f]`; `*.txt`: `[my report.txt]`; no match for `*.log`: `[*.log]`. A typo
gives 127, a script without `x` 126 (bash 5.2 here).
Explain: The shell expands `$f`, splits it on spaces unless double-quoted, then expands globs; the program sees
only the final list and leaves a number in `$?`.
Try: predict: the count for `./args.sh "$f" $f '*.txt' *.txt`; fix: `for f in $(ls)` over a spaced name, as `for
f in *` with `"$f"` (done when each file is handled once).
### 2
Need: I ran the same `cp -r` twice; why is there a folder inside my folder?
Show: `cp -r site backup` copies `site`'s contents; again: `backup/site/` appears. A relative symlink, moved: "No
such file or directory" (run here).
Explain: An existing destination means "copy into", a missing one "copy as"; a link stores a path, read from
where the link sits.
Try: predict: the tree after `mkdir a; mv a b`, run twice; apply: their service's config, logs and `/proc/PID/cmdline` found.
### 3
Need: `tail -f` on the log showed nothing after midnight; is the app dead?
Show: `tail -f app.log` and `tail -F app.log`, then rotate: `mv app.log app.log.1`, a new `app.log` gets "line3".
`-f` stayed on the old file; `-F`: "'app.log' has appeared;  following new file", then "line3" (GNU tail, run here).
Explain: `-f` follows the open file, `-F` the name.
Try: apply: their service's last error, via `find /var/log -mtime -1` and `grep -rn` (much of `/var/log` needs
`sudo`); build: a `grep -E` for 5xx statuses only.
### 4
Need: I sorted a file into itself; why is it empty?
Show: `sort f > f` on a 6-byte file: 0 bytes; with `set -o noclobber`: "cannot overwrite existing file". `ls
/nonexist f 2>&1 > out`: the error on screen, `out` holds `f`; `> out 2>&1`: both in `out` (bash 5.2 here).
Explain: The shell empties every `>` file before the command starts, and wires redirections left to right.
Try: predict: what `grep x f | sort > f` leaves, then run it 200 times and count (here: empty 197 times, whole 3:
both sides start at once, a race); build: their log's top ten client addresses (`awk`, `sort`, `uniq
-c`, `sort -rn`), one count checked with `grep -c`.
### 5
Need: The file is mode 644, readable by everyone; why "Permission denied"?
Show: root's directories, used as `nobody` (an ordinary user): `744`: `ls` lists, `ls -l` shows `-?????????`,
`cat` denied; `711`: `ls` denied, `cat` works; `777`: `nobody` deletes root's mode-444 file; `1777`: "Operation
not permitted". Root reads a mode-000 file, yet `./x.sh` without `x` gives it 126 (run here).
Explain: On a directory `r` reads names, `x` reaches an entry, `w` with `x` adds and deletes any entry whatever
its mode; the sticky bit keeps deletion to owners; root skips read and write checks, not the need for one `x`.
Try: fix: a file denied by a `700` parent, found with `namei -l`; decide: modes for their service's code, config
and logs (done when `sudo -u` checks pass).
### 6
Need: I killed my script and its temp files stayed; what does `kill` do?
Show: a bash script with `trap 'rm -f "$tmp"' EXIT`, looping. `kill`: trap ran, exit 143; `kill -9`: 137, file
left. As `#!/bin/sh` where `/bin/sh` is `dash` (Debian, Ubuntu): no trap on TERM, INT or HUP; `trap 'exit 143'
TERM` fixed it. In a pseudo-terminal, a `&` job outlived a typed `exit`; a terminal closed
under the running shell (a dropped connection) killed it, bash passing SIGHUP on; `nohup` survived (bash 5.2 here).
Explain: A signal is a number the kernel delivers; TERM, INT, HUP can be caught, KILL never; death by signal N
is 128 + N.
Try: predict: `$?` after Ctrl-C; fix: a job started with `&` over ssh, dying on disconnect, moved into `tmux`
(done when it survives a closed laptop).
### 7
Need: It works when I run it by hand; why does it fail in the deploy script?
Show: `~/.bash_profile` adds `~/bin` to `PATH`, exports `APP_ENV`; `deploy.sh` prints it and runs a `~/bin` tool.
Login shell: `production`, "deployed". `env -i HOME=... bash ./deploy.sh`, as cron or CI starts it: unset,
"command not found", 127. A script's `export` is gone after it; `source` keeps it (run here).
Explain: A child copies its parent's environment; login shells read `~/.bash_profile`, interactive ones
`~/.bashrc`, scripts neither.
Try: apply: their deploy script under `env -i HOME="$HOME" PATH=/usr/bin:/bin bash` until it passes; explain: why
`ll`, an alias, is "command not found" (127) in a script even when the script defines it (scripts expand none).
### 8
Need: My backup script exits 0 every night; why is the backup 20 bytes?
Show: `set -eu`; `pg_dump shop | gzip > shop.sql.gz`, database down: pg_dump's error, "backup ok: 20 bytes", exit
0. With `pipefail`: exit 1, the file still 20 bytes: `>` emptied yesterday's first. `set -e` passed `local
x=$(false)`, `if false`, `false && true`. `echo rm -rf "$DIR/"*`, `DIR` unset: `rm -rf /bin /boot ...` (here).
Explain: A pipeline reports its last command unless `pipefail`; `set -e` skips tested failures; so write
elsewhere, `mv` on success.
Try: fix: their backup with `mktemp`, `pipefail`, `trap` and `mv` (done when a stopped database leaves
yesterday's file and exit 1); apply: `"${DIR:?}"`, then `shellcheck` until silent.
### 9
Need: I copied my key to the server; why does ssh still ask for a password?
Show: (no ssh here) `chmod g+w ~/.ssh/authorized_keys` on their server, then `ssh -v`: key offered, password
asked. `StrictModes` "check[s] file modes and ownership ... before accepting login", "The default is yes"
(sshd_config(5), man7.org).
Explain: The server trusts `authorized_keys` only if nobody else could have written it or its directories.
Try: apply: `ssh -L 5433:localhost:5432` (done when local `psql -p 5433` connects); predict: `rsync -av --dry-run`
of `src` against `src/` (rsync(1): the slash avoids "an additional directory level").
### 10
Need: Under systemd my service runs, but its log file never appears; why?
Show: (no systemd running here) `ExecStart=/usr/bin/node app.js > /var/log/app.log`: redirection "not supported"
(systemd.service(5), man7.org). Started here without a shell, node got `['app.js', '>', '/var/log/app.log']`, no
file; under systemd output goes to the journal.
Explain: systemd starts the program itself as `User=`, journals its output (a file only by
`StandardOutput=append:`, systemd.exec(5)), restarts per `Restart=`; no shell unless `sh -c`. System logs need
`sudo` or `systemd-journal`.
Try: build: a unit for their app (done when it survives `kill` and a reboot); fix: a failing unit, via
`journalctl -u app -p err`.
### 11
Need: I deleted the 5 GB log and `df` still says full; why?
Show: a 500 MB `app.log` held by `tail -f`, `rm`ed: `df` still counted it, `du` saw 4 KB; `lsof +L1` and
`/proc/PID/fd` showed `app.log (deleted)`; `: > /proc/PID/fd/3` freed it (run here). As an ordinary user, `lsof
+L1` showed nothing held by root's process: `sudo`.
Explain: `rm` removes a name; the inode's blocks go when no name and no open descriptor remain.
Try: fix: space freed without a reboot via `lsof +L1`; predict: `df -i` with millions of empty files.
### 12
Need: "Address already in use", yet nothing should run; who has the port?
Show: a second `python3 -m http.server` on one port: "Address already in use". `ss -ltnp` finds the holder in
`/proc/PID/fd` (here by hand, from `/proc/net/tcp`); as `nobody`, root's is refused: `sudo` (run here).
Explain: One process listens per address and port (unless both set `SO_REUSEPORT`); refused: nobody listens there (networking-basics 10).
Try: apply: `ss -ltnp` and `curl -v` from inside and outside, naming "not listening", "127.0.0.1 only" or
"filtered"; predict: `dig +short` of their domain.
### 13
Need: The job works by hand; from cron nothing happens, silently; why?
Show: (no cron here) `* * * * * env > /tmp/cron-env.txt`, diffed with `env`: `SHELL=/bin/sh`, `HOME`, `LOGNAME`
(crontab(5), man7.org). `%` becomes a newline, the rest stdin: `date +%F >> log` runs `date +`; run here: a blank
line, no log.
Explain: cron runs each line with `/bin/sh`, no start-up files, output mailed or lost: set `PATH`, use absolute
paths, escape `%`, log yourself.
Try: fix: their job until `env -i /bin/sh -c '<line>'` works, logging `2>&1`; build: it as a timer.

## Go deep, leave for later
- Deep steps: 1, 5, 6, 8 (what the shell does to a line, directory bits, signals, and exit status in scripts:
  where hand-run commands and unattended scripts part ways).
- Later: `vim` in depth, bash arrays, mounts and LVM, firewalls, SELinux.

## Never omit
- A remote or virtual machine, as an ordinary user with `sudo`.
- Look up when planned: the learner's distribution, package manager, init system and shell (macOS: zsh, BSD tools).

## Wrong beliefs
- [1] "The program expands `*`" (the shell does; with no match bash passes `*.log` unchanged).
- [4] "`2>&1 > file` sends both streams to the file" (left to right: errors still reach the terminal).
- [4] "`uniq` removes duplicates" (only adjacent ones: `sort` first).
- [6] "`kill` kills" (it sends SIGTERM, which may be caught or ignored).
- [7] "Running a script that does `export` changes my shell" (a child cannot change its parent; `source` it).
- [6] "An EXIT trap always runs" (not on SIGKILL; dash runs none on an untrapped TERM).
- [8] "`set -e` stops at every failure" (not inside `if`, `&&`, `||` or `local x=$(...)`; without `pipefail` a pipeline reports its last command).

## Failures to diagnose
- [1] `command not found` (exit 127): a typo or not on `PATH`; `Permission denied` (126): a script without `x`.
- [1,8] A name with a space read as two names: an unquoted `$f`.
- [8] A nightly backup that "succeeds" at 20 bytes: a failing command before `|`, no `pipefail`.
- [5] `Permission denied` on a readable file: a directory above it lacks `x`.
- [6] An `&` job dies when the connection drops (SIGHUP): `tmux`, `nohup` or a service.
- [9] Key ignored, password asked: `~/.ssh` or `authorized_keys` writable by others (`StrictModes`).
- [11] Disk full, `du` finds nothing: a deleted file held open; restart its holder.
- [13] Works by hand, fails from cron: a command not on cron's `PATH`, a relative path, a bare `%`.

## Practice and project
Guided: on the learner's machine. On your own: a broken server diagnosed from its logs. Project: the learner's own program on a remote machine as a service under its own user, with a nightly backup script on a timer; finish line: it survives a reboot and a `kill`, the script passes `shellcheck`, refuses an unset variable, keeps seven archives, and a restore works.

## Mastery ladder
- Use: find why a remote service is down with `systemctl`, `journalctl`, `df`, `ss`.
- Explain: say what the shell does to `grep -c "$p" *.log > out 2>&1` before `grep` starts, and what `$?` holds after.
- Build: a backup script others run unattended, loud on failure, cleaning up.
- Design: choose users, groups and modes for a service, its deploy account and logs; defend each bit.

## Words to own
[1] argument, exit status, glob, quoting; [2] absolute path, relative path; [3] regular expression;
[4] standard output, standard error, redirection, pipe; [5] permission bits, owner, group, root, sticky bit;
[6] process, PID, signal, SIGTERM, SIGKILL; [7] environment variable, login shell; [8] shebang, trap;
[9] SSH key, port forwarding; [10] systemd unit, journal; [11] inode; [12] listening port; [13] crontab, timer
