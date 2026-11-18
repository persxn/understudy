#!/usr/bin/env python3
"""Tests for the terminal side of scripts/us_run.py and scripts/us_term.py: the final screen of redrawn
progress displays, typing with wait=, Ctrl-C, the plan's timeout: line, long output cut, and the Docker
cases (skipped where `docker ps` does not work). Prints one line per test and "N passed, M failed".

    python3 tests/run/term.py
"""
import argparse
import os
import pwd
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "scripts", "us_run.py")
RESULTS = []
TMP = tempfile.mkdtemp(prefix="us-term-tests-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import us_run as ur  # noqa: E402
from us_term import final_screen, keys  # noqa: E402


def env():
    e = dict(os.environ)
    if os.geteuid() == 0:
        try:
            e["US_RUN_USER"] = pwd.getpwnam(os.environ.get("US_RUN_USER", "ubuntu")).pw_name
        except KeyError:
            pass
    return e


def test(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else f": {detail!r}"))


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def book(name, head, chapter):
    """A book with one chapter; head: extra PLAN.md header lines. Returns (book, chapter path)."""
    b = os.path.join(TMP, name)
    os.makedirs(os.path.join(b, "chapters"))
    os.chmod(b, 0o755)
    write(os.path.join(b, "PLAN.md"), f"# T\nfor: x\nrun: console\n{head}\n### 1 One\n1.1 A\n1.2 B\n")
    path = os.path.join(b, "chapters", "01-one.md")
    write(path, chapter)
    return b, path


def us_run(*args, stdin=None):
    p = subprocess.run([sys.executable, SCRIPT] + list(args), capture_output=True, text=True, env=env(),
                       input=stdin, timeout=600)
    return p.returncode, p.stdout + p.stderr


def body(text, bid):
    lines = text.splitlines()
    i = next(k for k, x in enumerate(lines) if f"code: id={bid} " in x or f"code: id={bid}-" in x)
    k = i + 2
    while not lines[k].startswith("```"):
        k += 1
    return "\n".join(lines[i + 2:k])


def screens():
    build = ("[+] Building 0.0s (0/1)\n => [internal] load build definition from Dockerfile     0.0s\n"
             "\x1b[2A\x1b[0G\x1b[?25l[+] Building 0.1s (1/2)\x1b[K\n"
             " => [internal] load build definition from Dockerfile     0.0s\x1b[K\n"
             " => [1/1] COPY hi /                                      0.1s\x1b[K\n"
             "\x1b[3A\x1b[0G[+] Building 0.2s (2/2) FINISHED\x1b[K\n"
             " => [internal] load build definition from Dockerfile     0.0s\x1b[K\n"
             " => [1/1] COPY hi /                                      0.1s\x1b[K\n\x1b[?25h")
    test("final_screen: a docker build display redrawn three times comes out once, as its last frame",
         final_screen(build) == "[+] Building 0.2s (2/2) FINISHED\n"
         " => [internal] load build definition from Dockerfile     0.0s\n"
         " => [1/1] COPY hi /                                      0.1s\n", final_screen(build))
    compose = (" ⠋ Network t_default  Creating\n ⠋ Container t-web-1  Creating\n"
               "\x1b[2A\x1b[J ⠙ Network t_default  Created\n ⠙ Container t-web-1  Starting\n"
               "\x1b[2A\x1b[J ✔ Network t_default  Created\n ✔ Container t-web-1  Started\n")
    test("final_screen: compose spinner frames do not survive", final_screen(compose) ==
         " ✔ Network t_default  Created\n ✔ Container t-web-1  Started\n", final_screen(compose))
    shrink = "line one\nline two\nline three\n\x1b[3A\x1b[J\x1b[32mdone\x1b[0m\n"
    test("final_screen: blank lines left by a redraw that got shorter are dropped",
         final_screen(shrink) == "done\n", final_screen(shrink))
    pip = "Downloading x.whl (1 MB)\n   10% |##   |\r\x1b[K   55% |####  |\r\x1b[K   100% |######|\nInstalled\n"
    test("final_screen: a carriage-return progress bar shows its last state",
         final_screen(pip) == "Downloading x.whl (1 MB)\n   100% |######|\nInstalled\n", final_screen(pip))
    test("final_screen: blank lines the program printed stay; text over a carriage return overwrites "
         "letter by letter; tabs and backspaces as on a terminal",
         final_screen("a\n\n\nb\x08B\nabcdef\rXY\nx\ty\n") == "a\n\n\nB\nXYcdef\nx       y\n",
         final_screen("a\n\n\nb\x08B\nabcdef\rXY\nx\ty\n"))
    test("final_screen: no final newline stays none", final_screen("a\nb") == "a\nb")
    test("keys: lines one at a time, ^C and ^D as key presses",
         keys(b"Arjun\nexit\n") == [b"Arjun\n", b"exit\n"] and keys(b"x^Cy^D") == [b"x", b"\x03", b"y", b"\x04"])


def sessions():
    chapter = ("# 1 One\n\n<!-- code: id=ask stdin=\"Arjun\\n\" wait=1 timeout=5 -->\n```console\n"
               "$ read -p 'name? ' n; echo \"hello $n\"\n```\n\n"
               "<!-- code: id=stop stdin=\"^C\" wait=1 exit=130 timeout=5 -->\n```console\n$ echo before\n"
               "$ tail -f /dev/null\n```\n\n"
               "<!-- code: id=after -->\n```console\n$ echo still here\n```\n\n"
               "<!-- code: id=slow -->\n```console\n$ python3 -c 'import time; time.sleep(1.5)'\n```\n\n"
               "<!-- code: id=own timeout=3 -->\n```console\n$ python3 -c 'import time; time.sleep(1.5)'\n```\n\n"
               "<!-- code: id=each timeout=1.2 -->\n```console\n$ python3 -c 'import time; time.sleep(0.8)'\n"
               "$ python3 -c 'import time; time.sleep(0.8)'\n```\n")
    b, path = book("plain", "timeout: 1\n", chapter)
    code, out = us_run(path)
    text = read(path)
    test("typing with wait=: the typed line shows after the prompt, then the answer",
         body(text, "ask") == "$ read -p 'name? ' n; echo \"hello $n\"\nname? Arjun\nhello Arjun", body(text, "ask"))
    test("^C with wait=: Ctrl-C stops a program that never ends, shown where it was pressed; exit=130 holds",
         body(text, "stop") == "$ echo before\nbefore\n$ tail -f /dev/null\n^C", body(text, "stop"))
    test("the session after a Ctrl-C runs as usual", body(text, "after") == "$ echo still here\nstill here", out)
    test("the plan's timeout: line is the default time limit", "id=slow" in out and "timed out after 1s" in out, out)
    test("a marker's own timeout= wins over the plan's", "id=own" not in out, out)
    test("the time limit counts per command, not per session", "id=each" not in out, out)
    ch = ur.Chapter(os.path.join(TMP, "loose.md"), argparse.Namespace(ids=None, fresh=True), text="# x\n")
    test("no timeout: line keeps 5 seconds", ch.limit(argparse.Namespace(attrs={})) == 5.0)

    code, out = us_run("try", b, "1", stdin="<!-- code: id=long -->\n```console\n$ seq 70\n```\n")
    test("over the line limit: the first lines are shown and the cut is counted",
         "transcript is 71 lines" in out and "$ seq 70\n1\n2\n" in out and "\n19\n… 51 more lines cut" in out
         and "\n20\n" not in out, out)
    code, out = us_run("try", b, "1", stdin="<!-- code: id=badwait wait=x -->\n```console\n$ true\n```\n")
    test("wait= must be a number", "wait= must be a number" in out, out)


ASK = r'''#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
static void stop(int s) { (void)s; _exit(130); }
int main(int argc, char **argv) {
    char b[100];
    signal(SIGINT, stop);
    if (argc > 1) { puts("running"); fflush(stdout); for (;;) pause(); }
    for (;;) {
        fputs("name? ", stdout); fflush(stdout);
        if (!fgets(b, sizeof b, stdin)) return 0;
        b[strcspn(b, "\n")] = 0;
        if (!strcmp(b, "exit")) { puts("bye"); return 0; }
        printf("hello %s\n", b);
    }
}
'''


def docker():
    try:
        usable = subprocess.run(["docker", "ps"], capture_output=True, timeout=30).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        usable = False
    if not usable or not shutil.which("gcc"):
        print("skipped: no usable docker")
        return
    src = os.path.join(TMP, "img")
    os.makedirs(src)
    write(os.path.join(src, "ask.c"), ASK)
    subprocess.run(["gcc", "-static", "-o", os.path.join(src, "ask"), os.path.join(src, "ask.c")], check=True)
    write(os.path.join(src, "Dockerfile"), 'FROM scratch\nCOPY ask /\nCMD ["/ask"]\n')
    os.chmod(src, 0o755)
    for f in os.listdir(src):
        os.chmod(os.path.join(src, f), 0o755)
    chapter = (f"# 1 One\n\n<!-- code: id=build timeout=120 -->\n```console\n$ cd {src}\n"
               "$ docker build -t ustest-b-ask:1 .\n```\n\n"
               "<!-- code: id=it stdin=\"Arjun\\nexit\\n\" wait=1 timeout=30 -->\n```console\n"
               "$ docker run -it --rm ustest-b-ask:1\n```\n\n"
               "<!-- code: id=ctrlc stdin=\"^C\" wait=2 exit=130 timeout=30 -->\n```console\n"
               "$ docker run -it --rm --name ustest-b-loop ustest-b-ask:1 /ask loop\n```\n")
    try:
        b, path = book("dock", "", chapter)
        code, out = us_run(path)
        text = read(path)
        built = body(text, "build")
        test("docker build: its progress display is pasted once, as the final screen",
             built.count("[+] Building") == 1 and "FINISHED" in built and "\n\n" not in built, built)
        test("docker run -it: typed lines and the program's answers in order",
             body(text, "it") == "$ docker run -it --rm ustest-b-ask:1\nname? Arjun\nhello Arjun\nname? exit\nbye",
             body(text, "it") + out)
        test("docker run -it: ^C stops the program in the container, shown where it was pressed",
             body(text, "ctrlc").endswith("running\n^C"), body(text, "ctrlc") + out)
        left = subprocess.run(["docker", "ps", "-aq", "--filter", "name=ustest-b-loop"], capture_output=True,
                              text=True).stdout.strip()
        test("no container left after Ctrl-C", not left, left)
    finally:
        subprocess.run(["docker", "rm", "-f", "ustest-b-loop"], capture_output=True)
        subprocess.run(["docker", "rmi", "-f", "ustest-b-ask:1"], capture_output=True)


def main():
    try:
        screens()
        sessions()
        docker()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    passed = sum(RESULTS)
    print(f"{passed} passed, {len(RESULTS) - passed} failed")
    return 1 if len(RESULTS) > passed else 0


if __name__ == "__main__":
    sys.exit(main())
