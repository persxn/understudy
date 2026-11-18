#!/usr/bin/env python3
"""Machine check: can this machine do what a book needs, before any usage is spent?

    python3 scripts/us_doctor.py [BOOK] [--again]

Measures the system, memory, free disk, Python and git; with BOOK also looks for the build and run tools of
its `run:` language (the LANGS of us_run.py), runs every `check:` command of its PLAN.md (60 s each, as the
user sessions run as) and, for `state: docker`, checks the client, the service, this user's right to use it
and one tiny test download. Each problem is one `- blocked:` line with its cure.
Writes the result to <private>/machine.md (the "Told by the learner" part is kept) and reuses it for the rest of
the day unless --again. Exit 0 = fine, 1 = something blocks, 2 = bad arguments.
"""
import datetime
import os
import platform
import shutil
import signal
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
from us_lib import ROOT  # noqa: E402

try:   # the same user us_run.py runs sessions as, and the languages it builds and runs
    from us_run import ALIASES, LANGS, ordinary_user
except Exception:  # noqa: BLE001  (us_run.py may be mid-edit; then run as ourselves)
    LANGS, ALIASES = {}, {}

    def ordinary_user():
        return None, ""

TOLD = "## Told by the learner\n- internet:\n- usage plan:\n- how I learn:\n"
EMPTY = "# This machine and its limits\n\n## Measured\n- not measured yet: run python3 scripts/us_doctor.py\n\n" + TOLD
LIMIT = 60
PACKAGES = {"gcc": "gcc", "g++": "g++", "python3": "python3", "node": "nodejs", "javac": "default-jdk",
            "java": "default-jre", "bash": "bash"}   # Debian and Ubuntu package of each tool LANGS names
HUB = ("Docker Hub cannot be reached from here (the network refuses registry-1.docker.io). No image can be "
       "downloaded until that is fixed: ask whoever runs the network, or try another connection.")


def shell(cmd, pw, timeout=None):
    """Run cmd (list, or a string for sh -c) as pw: (exit code or None on time-out, output text)."""
    argv = ["sh", "-c", cmd] if isinstance(cmd, str) else cmd
    env = dict(os.environ)
    if pw:
        env.update(HOME=pw.pw_dir, USER=pw.pw_name, LOGNAME=pw.pw_name)

    def drop():
        os.setsid()
        if pw:
            os.setgid(pw.pw_gid)
            os.initgroups(pw.pw_name, pw.pw_gid)
            os.setuid(pw.pw_uid)
    try:
        proc = subprocess.Popen(argv, cwd=tempfile.gettempdir(), env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=drop)
    except OSError as exc:
        return 127, str(exc)
    try:
        out, _ = proc.communicate(timeout=timeout or LIMIT)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return None, ""
    return proc.returncode, out.decode("utf-8", "replace").strip()


def first(text):
    """The most telling line of an error output, cut short."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    line = next((l for l in lines if "error" in l.lower() or "denied" in l.lower()), lines[-1] if lines else "")
    return line[:160]


def system_lines():
    """(measured lines, blocked lines) about the system itself."""
    name = platform.system()
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            name = next((l.split("=", 1)[1].strip().strip('"') for l in f if l.startswith("PRETTY_NAME=")), name)
    except OSError:
        pass
    lines, blocked = ["system: %s, %s" % (name, platform.machine())], []
    mem = ""
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            kb = next(int(l.split()[1]) for l in f if l.startswith("MemTotal:"))
        mem = "memory: %.0f GB; " % (kb / 1024 / 1024)
    except (OSError, StopIteration, ValueError):
        pass
    free = shutil.disk_usage(ROOT).free / 1e9
    lines.append("%sdisk free: %.0f GB" % (mem, free))
    if free < 1:
        blocked.append("less than 1 GB of disk is free here: delete files you do not need, then run this again.")
    lines.append("python: %s" % platform.python_version())
    code, out = shell(["git", "--version"], None, 10)
    lines.append("git: " + (out.split()[-1] if code == 0 and out else "not installed (books are kept without history)"))
    return lines, blocked


def docker_lines(pw):
    """(measured lines, blocked lines) for a book with `state: docker`."""
    who = "this user" + (" (%s)" % pw.pw_name if pw else "")
    name = pw.pw_name if pw else os.environ.get("USER", "$USER")
    if not shutil.which("docker"):
        return ["docker: not installed"], ["Docker is not installed: install Docker Engine from Docker's own apt "
                                           "repository (docs.docker.com/engine/install), then run this again."]
    code, client = shell(["docker", "version", "--format", "{{.Client.Version}}"], pw, 20)
    client = client.splitlines()[0] if client[:1].isdigit() else "unknown"
    code, out = shell(["docker", "version", "--format", "{{.Server.Version}}"], pw, 20)
    if code != 0:
        low = out.lower()
        if "permission denied" in low:
            return (["docker: client %s, the service runs, %s may not use it" % (client, who)],
                    ["%s may not use Docker (permission denied on docker.sock): run `sudo usermod -aG docker %s`, "
                     "then log out and log in again." % (who.capitalize(), name)])
        return (["docker: client %s, the service does not answer" % client],
                ["the Docker service is not running (%s): start it with `sudo systemctl start docker`, or start "
                 "Docker Desktop." % (first(out) or "no answer in 20 seconds")])
    lines = ["docker: client %s, service %s, the service answers, %s may use it" % (client, out.splitlines()[0], who)]
    code, out = shell(["docker", "pull", "-q", "hello-world"], pw)
    low = out.lower()
    if code == 0:
        return lines + ["download: a test image (hello-world, about 10 KB) came down from Docker Hub"], []
    if code is None:
        why = ("downloading a 10 KB test image did not finish in %d seconds: the connection is too slow or "
               "blocked; try another connection." % LIMIT)
    elif "toomanyrequests" in low or "rate limit" in low:
        why = ("Docker Hub's download limit for this address is reached (100 pulls per 6 hours): run `docker login` "
               "with a free Docker account, or wait a few hours.")
    elif any(s in low for s in ("no such host", "name resolution", "network is unreachable", "dial tcp: lookup")):
        why = ("this machine has no internet connection (Docker Hub's name cannot be looked up). No image can be "
               "downloaded until it is connected.")
    else:
        why = HUB
    return lines, [why]


def language_lines(book):
    """(measured lines, blocked lines) for the tools the book's `run:` language is built and run with."""
    plan = bf.load_plan(book)
    run = (plan.run if plan else "").strip().lower()
    lang = ALIASES.get(run, run)
    if lang not in LANGS:
        return [], []                  # none, console, or a language the runner does not know
    tools = []
    for step in ("build", "run"):
        word = LANGS[lang][step].split()[0]
        if not word.startswith("{") and word not in tools:
            tools.append(word)
    missing = [t for t in tools if not shutil.which(t)]
    if not missing:
        return ["%s: %s found" % (run, ", ".join(tools))], []
    return [], ["the book's programs (run: %s) need %s, which is not installed: install %s." % (
        run, t, t + (": sudo apt install " + PACKAGES[t] if t in PACKAGES else "")) for t in missing]


def measure(book, pw):
    """All lines of the Measured part and how many are blocked."""
    lines, blocked = system_lines()
    if book:
        more, bad = language_lines(book)
        lines += more
        blocked += bad
        if "docker" in [v.lower() for v in bf.plan_meta(book, "state")]:
            more, bad = docker_lines(pw)
            lines += more
            blocked += bad
        for cmd in bf.plan_meta(book, "check"):
            if not cmd:
                continue
            code, out = shell(cmd, pw)
            if code == 0:
                lines.append("check: `%s` works" % cmd)
            elif code is None:
                blocked.append("the plan's check `%s` did not finish in %d seconds: make it work here, or change "
                               "the plan's check line." % (cmd, LIMIT))
            else:
                blocked.append("the plan's check `%s` fails here (exit %d%s): make it work here before writing, "
                               "or change the plan's check line." % (cmd, code, ": " + first(out) if out else ""))
    return ["- " + l for l in lines] + ["- blocked: " + b for b in blocked], len(blocked)


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    again = "--again" in argv
    args = [a for a in argv if a != "--again"]
    if len(args) > 1 or any(a.startswith("-") for a in args):
        print("usage: python3 scripts/us_doctor.py [BOOK] [--again]")
        return 2
    book = bf.resolve_book(args[0]) if args else ""
    if book and not os.path.exists(os.path.join(book, "PLAN.md")):
        print("no PLAN.md in %s: name a book folder (book/<subject>) or run without a book" % book)
        return 2
    path = os.path.join(bf.private_dir(), "machine.md")
    old = bf.read_text(path) if os.path.exists(path) else EMPTY
    told = old[old.index("## Told by the learner"):] if "## Told by the learner" in old else TOLD
    head = "## Measured (us_doctor.py, %s%s)" % (datetime.date.today().isoformat(),
                                                ", book " + os.path.basename(book.rstrip(os.sep)) if book else "")
    if not again and head + "\n" in old:
        part = old.split(head + "\n", 1)[1].split("\n## ", 1)[0]
        lines = [l for l in part.splitlines() if l.startswith("- ")]
        blocked = sum(l.startswith("- blocked:") for l in lines)
        print("\n".join(lines))
        print("machine check (from earlier today; --again to measure again): %s"
              % ("%d blocked" % blocked if blocked else "ok"))
        return 1 if blocked else 0
    pw, _ = ordinary_user()
    lines, blocked = measure(book, pw)
    bf.write_text(path, "# This machine and its limits\n\n%s\n%s\n\n%s" % (head, "\n".join(lines), told))
    print("\n".join(lines))
    where = os.path.relpath(path, ROOT) if path.startswith(ROOT + os.sep) else path
    print("machine check: %s, written to %s" % ("%d blocked" % blocked if blocked else "ok", where))
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
