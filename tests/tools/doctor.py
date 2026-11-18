#!/usr/bin/env python3
"""Tests for scripts/us_doctor.py (the machine check) and the machine.md that us_init.py makes.
Prints one line per test and "N passed, M failed"; exit 1 on failure.

    python3 tests/tools/doctor.py
"""
import os
import pwd
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
TMP = tempfile.mkdtemp(prefix="us-doctor-test-")
os.chmod(TMP, 0o755)          # checks run as an ordinary user must reach their working folder
PRIVATE = os.path.join(TMP, "private")
MACHINE = os.path.join(PRIVATE, "machine.md")
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=PRIVATE, TMPDIR=TMP)
TESTS = []
SKIPPED = []


def test(fn):
    TESTS.append(fn)
    return fn


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


class Skip(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def doctor(*args, env=None, scripts=SCRIPTS):
    """Run us_doctor.py: (exit code, output lines)."""
    proc = subprocess.run([sys.executable, os.path.join(scripts, "us_doctor.py")] + list(args),
                          capture_output=True, text=True, env=env or ENV)
    return proc.returncode, [l for l in (proc.stdout + proc.stderr).splitlines() if not l.startswith("warning:")]


def plan(name, header):
    """A fake book whose PLAN.md has these header lines."""
    path = os.path.join(TMP, name)
    write(os.path.join(path, "PLAN.md"), header + "\n# Fake book\n\n## Chapter 1: Start\n")
    return path


def docker_usable():
    try:
        return subprocess.run(["docker", "ps"], capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def blocked(out):
    return [l for l in out if l.startswith("- blocked:")]

# ---------------------------------------------------------------- tests


@test
def no_book_measures_and_writes():
    code, out = doctor("--again")
    check(code == 0, out)
    for key in ("- system: ", "- memory: ", "disk free: ", "- python: ", "- git: "):
        check(any(key in l for l in out), "no %r in %s" % (key, out))
    check(not blocked(out) and out[-1].startswith("machine check: ok"), out)
    text = read(MACHINE)
    check(text.startswith("# This machine and its limits\n\n## Measured (us_doctor.py, "), text)
    check("## Told by the learner\n- internet:\n- usage plan:\n- how I learn:\n" in text, text)


@test
def told_by_the_learner_is_kept():
    doctor("--again")
    text = read(MACHINE)
    write(MACHINE, text.replace("- internet:\n", "- internet: hostel Wi-Fi, 1.5 GB a day\n"))
    code, out = doctor("--again")
    check(code == 0, out)
    text = read(MACHINE)
    check("- internet: hostel Wi-Fi, 1.5 GB a day\n" in text and text.count("## Told by the learner") == 1, text)
    check(text.count("## Measured") == 1, text)


@test
def plan_checks_run_and_block():
    book = plan("checks", "check: true\ncheck: false\ncheck: echo oops >&2; exit 3")
    code, out = doctor(book, "--again")
    check(code == 1, out)
    check("- check: `true` works" in out, out)
    bad = blocked(out)
    check(len(bad) == 2, out)
    check("`false` fails here (exit 1)" in bad[0], bad)
    check("(exit 3: oops)" in bad[1], bad)
    check(bad[0] in read(MACHINE), "blocked line not written to machine.md")
    check(out[-1].startswith("machine check: 2 blocked"), out)


@test
def result_is_kept_for_the_day():
    book = plan("cache", "check: true\ncheck: false")
    code, out = doctor(book, "--again")
    check(code == 1, out)
    write(os.path.join(book, "PLAN.md"), "check: true\n\n# Fake book\n")   # fixed, but not measured again
    code, out = doctor(book)
    check(code == 1 and "from earlier today" in out[-1] and len(blocked(out)) == 1, out)
    code, out = doctor(book, "--again")
    check(code == 0 and not blocked(out) and "earlier" not in out[-1], out)
    code, out = doctor()               # another book (none) is measured afresh
    check(code == 0 and "earlier" not in out[-1], out)


@test
def check_that_never_ends_is_cut_off():
    book = plan("slow", "check: python3 -c 'import time; time.sleep(600)'")
    env = dict(ENV)
    code, out = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import us_doctor as d; "
                                "d.LIMIT = 2; sys.exit(d.main([%r, '--again']))" % (SCRIPTS, book)],
                               capture_output=True, text=True, env=env, timeout=60).returncode, None
    text = read(MACHINE)
    check(code == 1 and "did not finish in 2 seconds" in text, text)


@test
def bad_arguments():
    code, out = doctor(os.path.join(TMP, "nothing-here"))
    check(code == 2 and "no PLAN.md" in out[-1], out)
    code, out = doctor("--frobnicate")
    check(code == 2 and out[-1].startswith("usage:"), out)
    code, out = doctor("--help")
    check(code == 0 and any("us_doctor.py [BOOK]" in l for l in out), out)


@test
def docker_book_reports_hub():
    if not docker_usable():
        raise Skip()
    book = plan("dock", "state: docker\ncheck: docker ps")
    code, out = doctor(book, "--again")
    check(any(l.startswith("- docker: client ") and "may use it" in l for l in out), out)
    check("- check: `docker ps` works" in out, out)
    hub = [l for l in blocked(out) if "Docker Hub" in l or "internet" in l or "connection" in l]
    down = [l for l in out if l.startswith("- download:")]
    check(len(hub) + len(down) == 1, out)
    check(code == (1 if hub else 0), out)
    if hub:   # this machine: the registry refuses us
        check("No image can be downloaded" in hub[0] or "did not finish" in hub[0], hub)


@test
def docker_user_not_in_group():
    if not docker_usable():
        raise Skip()
    try:
        nobody = pwd.getpwnam("nobody")
    except KeyError:
        raise Skip()
    if os.geteuid() != 0 or any(g == "docker" for g in [g for g in os.getgrouplist("nobody", nobody.pw_gid)]):
        raise Skip()
    book = plan("perm", "state: docker")
    code, out = doctor(book, "--again", env=dict(ENV, US_RUN_USER="nobody"))
    check(code == 1, out)
    bad = blocked(out)
    check(len(bad) == 1 and "may not use Docker" in bad[0] and "usermod -aG docker nobody" in bad[0]
          and "log in again" in bad[0], out)


@test
def book_language_tools_are_looked_for():
    book = plan("lang", "run: c")
    code, out = doctor(book, "--again", env=dict(ENV, PATH="/nonexistent"))
    bad = blocked(out)
    check(code == 1 and len(bad) == 1 and "need gcc" in bad[0] and "install gcc: sudo apt install gcc" in bad[0], out)
    if shutil.which("gcc"):
        code, out = doctor(book, "--again")
        check(code == 0 and "- c: gcc found" in out and not blocked(out), out)
    for run in ("none", "console"):
        code, out = doctor(plan("lang-" + run, "run: " + run), "--again", env=dict(ENV, PATH="/nonexistent"))
        check(code == 0 and not blocked(out), "run: %s checks no tool: %s" % (run, out))


@test
def init_makes_empty_machine_md():
    home = os.path.join(TMP, "product")
    os.makedirs(os.path.join(home, "reader"))
    shutil.copytree(SCRIPTS, os.path.join(home, "scripts"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(os.path.join(ROOT, "understudy.yaml"), home)
    write(os.path.join(home, "reader", "index.html"), "<!DOCTYPE html><title>reader</title>\n")
    env = {k: v for k, v in ENV.items() if k != "UNDERSTUDY_PRIVATE"}
    proc = subprocess.run([sys.executable, os.path.join(home, "scripts", "us_init.py")], capture_output=True,
                          text=True, env=env)
    check(proc.returncode == 0, proc.stdout + proc.stderr)
    path = os.path.join(home, "private", "machine.md")
    text = read(path)
    check(text.startswith("# This machine and its limits\n") and text.endswith(
        "## Told by the learner\n- internet:\n- usage plan:\n- how I learn:\n"), text)
    write(path, text.replace("- usage plan:\n", "- usage plan: Pro, two hours a day\n"))
    subprocess.run([sys.executable, os.path.join(home, "scripts", "us_init.py")], capture_output=True, env=env)
    check("Pro, two hours a day" in read(path), "us_init overwrote machine.md")
    code, out = doctor("--again", env=env, scripts=os.path.join(home, "scripts"))
    check(code == 0 and "Pro, two hours a day" in read(path) and "not measured yet" not in read(path), out)


def main():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok    " + fn.__name__)
            passed += 1
        except Skip:
            print("skipped: no usable docker (%s)" % fn.__name__)
        except Exception as exc:  # noqa: BLE001
            print("FAIL  %s: %s" % (fn.__name__, str(exc).replace("\n", " | ")[:400]))
            failed += 1
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
