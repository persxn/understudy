#!/usr/bin/env python3
"""Tests for what a `state: docker` book makes in Docker (scripts/us_state.py and its use in us_run.py).
Prints one line per test and "N passed, M failed"; exit 1 on failure. The Docker tests are skipped where
`docker ps` does not work; they build their images from a C program (no download) and remove all they make.

    python3 tests/run/state.py
"""
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "scripts", "us_run.py")
RESULTS = []
TMP = tempfile.mkdtemp(prefix="us-state-tests-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import us_state  # noqa: E402


def test(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else f": {detail}"))


def env():
    e = dict(os.environ)
    if os.geteuid() == 0:
        try:
            e["US_RUN_USER"] = pwd.getpwnam(os.environ.get("US_RUN_USER", "ubuntu")).pw_name
        except KeyError:
            pass
    return e


def us_run(*args):
    p = subprocess.run([sys.executable, SCRIPT] + list(args), capture_output=True, text=True, env=env())
    return p.returncode, p.stdout, p.stderr


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def exists(kind, name):
    fmt = {"container": "ps -a --format {{.Names}}", "volume": "volume ls --format {{.Name}}",
           "image": "images --format {{.Repository}}:{{.Tag}}", "network": "network ls --format {{.Name}}"}[kind]
    return name in sh("docker " + fmt).stdout.split()


def running(name):
    return name in sh("docker ps --format {{.Names}}").stdout.split()


# ---------------------------------------------------------------- without Docker

def offline():
    d = us_state.Docker(os.path.join(TMP, "offline"))
    masks = [re.compile(p) for p in d.masks]

    def masked(text):
        for p in masks:
            text = p.sub("~", text)
        return re.sub(r"[ \t]+", " ", text)
    a = ("ustest-a   Exited (0) 2 seconds ago   3f2a9c1b7e44\n"
         "Successfully built sha256:" + "ab" * 32 + " in 0.1s\n2026-11-18 01:10:22 +0000 UTC  Up 3 seconds\n")
    b = ("ustest-a   Exited (0) About a minute ago   9c1b7e443f2a\n"
         "Successfully built sha256:" + "cd" * 32 + " in 12.4s\n2026-11-19 07:00:01 +0000 UTC  Up Less than a second\n")
    test("masks: ids, digests, times, dates and Up/ago ages are ignored", masked(a) == masked(b), (masked(a), masked(b)))
    test("masks: real text still differs", masked(a) != masked(a.replace("ustest-a", "ustest-b")))
    for cmd in ("docker system prune -af", "docker image prune", "docker volume prune -f", "docker builder prune",
                "docker rm -f $(docker ps -aq)", "docker stop `docker ps -q`", "docker ps -q | xargs docker kill",
                "docker swarm leave --force", "docker volume rm $(docker volume ls -q)"):
        test(f"refused: {cmd}", d.danger(cmd), cmd)
    for cmd in ("docker rm -f web", "docker run --rm hi", "docker compose down -v", "docker image ls"):
        test(f"allowed: {cmd}", not d.danger(cmd), cmd)
    test("note: -p 8080:80 publishes to the whole network",
         d.note("docker run -d -p 8080:80 web") == "publishes the port to the whole network; write -p 127.0.0.1:8080:80")
    test("note: --publish=0.0.0.0:9000:9000 too", "127.0.0.1:9000:9000" in d.note("docker run --publish=0.0.0.0:9000:9000 x"))
    test("no note for -p 127.0.0.1:8080:80", d.note("docker run -p 127.0.0.1:8080:80 web") == "")
    test("unknown state kind gives no tracker", us_state.tracker("vagrant", TMP) is None)


# ---------------------------------------------------------------- with Docker

def images(work):
    write(os.path.join(work, "hi.c"), '#include <stdio.h>\nint main(void){puts("hi");return 0;}\n')
    write(os.path.join(work, "loop.c"), '#include <unistd.h>\nint main(void){for(;;)pause();}\n')
    for name in ("hi", "loop"):
        d = os.path.join(work, name)
        os.makedirs(d)
        r = sh(f"cd {d} && gcc -static -o {name} ../{name}.c && printf 'FROM scratch\\nCOPY {name} /\\n"
               f"CMD [\"/{name}\"]\\n' > Dockerfile && docker build -q -t ustest-{name}:1 .")
        if r.returncode:
            return r.stdout + r.stderr
    os.chmod(os.path.join(work, "hi", "hi"), 0o755)
    return ""


CHAPTER = """# Chapter 1: One

## 1.1 A

<!-- code: id=first timeout=60 -->
```console
$ docker run --name ustest-first ustest-hi:1
$ docker network create ustest-net
$ docker volume create ustest-vol
$ docker ps -a --filter name=ustest-first --format '{{.Names}} {{.ID}} {{.Status}}'
```

<!-- code: id=build timeout=60 -->
```console
$ mkdir -p img && cp %(hi)s img/ && printf 'FROM scratch\\nCOPY hi /\\nCMD ["/hi"]\\n' > img/Dockerfile
$ docker build -q -t ustest-built:1 img
```
"""


def with_docker():
    work = os.path.join(TMP, "work")
    os.makedirs(work)
    os.chmod(work, 0o755)
    bad = images(work)
    if bad:
        test("test images build", False, bad)
        return
    book = os.path.join(TMP, "dock")
    write(os.path.join(book, "PLAN.md"), "# D\nfor: x\nrun: console\nstate: docker\n\n### 1 One\n1.1 A\n")
    ch = os.path.join(book, "chapters", "01-one.md")
    write(ch, CHAPTER % {"hi": os.path.join(work, "hi", "hi")})
    sh("docker create --name ustest-mine ustest-hi:1 && docker volume create ustest-vol-mine")

    code, out, err = us_run(ch)
    test("first run of a docker chapter passes", code == 0 and "ustest-first" in read(ch), out + err)
    test("leftovers are gone after the run (container, network, volume)",
         not exists("container", "ustest-first") and not exists("network", "ustest-net")
         and not exists("volume", "ustest-vol"), sh("docker ps -a; docker network ls; docker volume ls").stdout)
    test("built images stay after a run", exists("image", "ustest-built:1"))
    code, out, err = us_run(ch, "--force")
    test("second run with docker run --name ... passes", code == 0, out + err)
    code, out, err = us_run(ch, "--check", "--force")
    test("--check right after a run reports no difference", code == 0, out + err)
    first = read(ch)
    us_run(ch, "--force")
    test("a new run keeps the pasted text when only ids and times changed", read(ch) == first)

    prune = os.path.join(book, "chapters", "01-one.md")
    write(prune, "# Chapter 1: One\n\n## 1.1 A\n\n<!-- code: id=wipe -->\n```console\n$ docker system prune -f\n```\n\n"
          "<!-- code: id=rmall -->\n```console\n$ docker rm -f $(docker ps -aq)\n```\n\n"
          "<!-- code: id=port timeout=30 -->\n```console\n$ docker create --name ustest-p -p 18089:80 ustest-hi:1\n```\n")
    code, out, err = us_run(prune)
    test("a prune session is refused", code == 1 and "id=wipe  refused: 'docker system prune -f' would touch things "
         "the book did not make" in out and "id=rmall  refused" in out, out + err)
    test("a port published to every address gets a note, not a problem",
         "id=port  note: publishes the port to the whole network; write -p 127.0.0.1:18089:80" in out
         and "id=port  refused" not in out, out)

    write(prune, "# Chapter 1: One\n\n## 1.1 A\n\n<!-- code: id=clash timeout=30 -->\n```console\n"
          "$ docker run --name ustest-mine ustest-hi:1\n```\n")
    code, out, err = us_run(prune)
    test("a name clash with something not the book's is said in plain words",
         "a container named ustest-mine already exists on this machine and was not made by the book's runs" in out,
         out + err)

    write(prune, "# Chapter 1: One\n\n## 1.1 A\n\n<!-- code: id=later unrun=\"no image here\" timeout=30 -->\n"
          "```console\n$ docker run --rm ustest-later:1\n```\n")
    before = read(prune)
    code, out, err = us_run(prune)
    test("an unrun session that cannot run stays quiet", code == 0 and "unrun 1" in out and read(prune) == before,
         out + err)
    sh("docker tag ustest-hi:1 ustest-later:1")
    code, out, err = us_run(prune)
    text = read(prune)
    test("an unrun session is filled in when it can run", code == 0 and "now run: later" in out and
         "unrun=" not in text and "$ docker run --rm ustest-later:1\nhi\n```" in text, out + err + text)

    write(prune, "# Chapter 1: One\n\n## 1.1 A\n\n<!-- code: id=forever timeout=4 -->\n```console\n"
          "$ docker run --name ustest-loop ustest-loop:1\n```\n")
    code, out, err = us_run(prune)
    test("a timed-out session leaves no running container",
         code == 1 and "timed out" in out and not running("ustest-loop") and not exists("container", "ustest-loop"),
         out + err + sh("docker ps -a").stdout)

    code, out, err = us_run("--reset", book)
    test("--reset removes built images too", code == 0 and not exists("image", "ustest-built:1"), out + err)
    test("something made outside the book is never removed",
         exists("container", "ustest-mine") and exists("volume", "ustest-vol-mine") and exists("image", "ustest-hi:1"))


def cleanup():
    sh("docker rm -f ustest-mine ustest-first ustest-p ustest-loop ustest-clash; docker network rm ustest-net; "
       "docker volume rm -f ustest-vol ustest-vol-mine; docker rmi -f ustest-hi:1 ustest-loop:1 ustest-built:1 "
       "ustest-later:1")


def main():
    offline()
    if shutil.which("docker") is None or sh("docker ps").returncode != 0 or shutil.which("gcc") is None:
        print("skipped: no usable docker")
    else:
        try:
            with_docker()
        finally:
            cleanup()
    shutil.rmtree(TMP, ignore_errors=True)
    failed = RESULTS.count(False)
    print(f"{len(RESULTS) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
