"""Tests for the us_check.py fixes of the Docker test (section C): python3 tests/book/check_fixes.py"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
TMP = tempfile.mkdtemp(prefix="us-check-fixes-")
os.chmod(TMP, 0o755)          # sessions run as an ordinary user must reach their folder
os.environ["TMPDIR"] = tempfile.tempdir = TMP
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []
COUNTER = [0]

PLAN = """# Test book
for: testers
run: console

### 1 Basics
1.1 First steps | teaches: alpha
1.2 Second steps | teaches: beta
1.3 The hub | teaches: docker-hub
{extra}
### 2 Later
2.1 Order of start | teaches: depends-on
"""


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def lesson(number, title, body="", idea=None, words=0):
    """A section with every beat; `words` filler words in The idea; `body` goes in The code."""
    filler = " ".join(["filler"] * words)
    teach = "<!-- teaches: %s -->\n" % idea if idea else ""
    return ("## %s %s\n\n### The question\n\nWhy?\n\n### The picture\n\nA picture.\n\n### The idea\n\n%s**%s** is said here. %s\n\n"
            "### The code\n\n%s\n\n### The trace\n\nIt runs.\n\n### What goes wrong\n\nLittle.\n\n### Remember\n\nThis.\n\n"
            "**Check yourself**\n\n1. One?\n\n<details>\n<summary>Answer</summary>\n\nA.\n\n</details>\n\n"
            "2. Two?\n\n<details>\n<summary>Answer</summary>\n\nB.\n\n</details>\n\n"
            "3. Three?\n\n<details>\n<summary>Answer</summary>\n\nC.\n\n</details>\n\n" % (
                number, title, teach, title, filler, body))


def book(sections, extra=""):
    """A new book in its own root with chapter 1 made of the given section texts; returns its folder."""
    COUNTER[0] += 1
    path = os.path.join(TMP, "r%d" % COUNTER[0], "bk")
    os.makedirs(os.path.join(path, "chapters"))
    with open(os.path.join(path, "PLAN.md"), "w", encoding="utf-8") as f:
        f.write(PLAN.format(extra=extra))
    if sections:
        with open(os.path.join(path, "chapters", "01-basics.md"), "w", encoding="utf-8") as f:
            f.write("# Chapter 1: Basics\n\n" + "\n".join(sections))
    return path


def run(*args):
    """us_check.py with args: (exit code, output lines)."""
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_check.py")] + list(args),
                          capture_output=True, text=True, env=ENV)
    return proc.returncode, (proc.stdout + proc.stderr).splitlines()


def three(first="", second="", third="", words=0, extra=""):
    """A book with 1.1, 1.2, 1.3 written; extra text in The code of each."""
    return book([lesson("1.1", "First steps", first, "alpha = alpha", words), lesson("1.2", "Second steps", second, "beta = beta", words),
                 lesson("1.3", "The hub", third, "docker-hub = Docker Hub", words)], extra)

# ---------------------------------------------------------------- used before taught


@test
def used_before_taught_once_a_section_and_never_in_code():
    b = three("Docker Hub holds images. Docker Hub again. Pull from Docker Hub.",
              "Type `docker login Docker Hub` now.\n\n```console\n$ echo Docker Hub\n```")
    code, out = run(b)
    hits = [l for l in out if "'Docker Hub' is used here" in l]
    check(len(hits) == 1 and "(1.1)" in hits[0], "once in 1.1, none in 1.2's code: %s" % hits)
    check(hits[0].endswith("taught in 1.3; say it in plain words here instead, or, only if the reader must look ahead, add (§1.3) after the sentence"), hits)


@test
def ordinary_english_is_not_a_guessed_idea():
    code, out = run(three("It depends on the network."))
    check(not any("'depends on'" in l for l in out), out)
    code, out = run(three("It **depends on** the network."))
    check(any("(1.1) 'depends on' is used here but taught in 2.1" in l for l in out), out)


@test
def a_reference_inside_a_command_is_an_error():
    b = three(second="Type `docker run (§1.3) alpine` now.\n\n```console\n$ echo (§1.1)\n```\n\nSee §1.1 for more.")
    code, out = run(b)
    hits = [l for l in out if "a section reference inside a command" in l]
    check(code == 1 and len(hits) == 2 and all(l.startswith("ERROR") for l in hits), hits)
    check(any("(§1.3)" in l for l in hits) and any("(§1.1)" in l for l in hits), hits)

# ---------------------------------------------------------------- not run here


SESSION = '<!-- code: id=%s mode=run -->\n```console\n$ echo hi\n```\n\n```text\nhi\n```\n'
UNRUN = '<!-- code: id=%s mode=run unrun="no network here" -->\n```console\n$ docker pull alpine\n```\n'
FRAGMENT = '<!-- code: id=%s mode=fragment -->\n```console\n$ docker system prune\n```\n'
QUIET = '<!-- code: id=%s mode=fragment -->\n```console\nnot a command\n```\n'


@test
def not_run_count_and_limit():
    code, out = run(three(SESSION % "s1" + SESSION % "s2" + SESSION % "s3", SESSION % "s4" + UNRUN % "u1" + QUIET % "q1"), "1")
    check(any(l.startswith("NOTE") and l.endswith("not run here: 1 of 5 (u1)") for l in out), out)
    check(not any("too much of this chapter" in l for l in out), out)
    code, out = run(three(SESSION % "s1" + SESSION % "s2", UNRUN % "u1" + FRAGMENT % "f1" + UNRUN % "u2"), "1")
    check(any(l.endswith("not run here: 3 of 5 (u1, f1, u2)") for l in out), out)
    hit = [l for l in out if "too much of this chapter cannot be run on this machine" in l]
    check(code == 1 and hit and hit[0].startswith("ERROR") and "us_doctor.py" in hit[0], out)
    code, out = run(three(SESSION % "s1"))
    check(not any("not run here" in l for l in out), out)

# ---------------------------------------------------------------- figures, word floors, short


@test
def fig_field_needs_a_figure():
    b = book([lesson("1.1", "First steps", "", "alpha = alpha")], "")
    plan = os.path.join(b, "PLAN.md")
    with open(plan, encoding="utf-8") as f:
        text = f.read().replace("1.1 First steps | teaches: alpha", "1.1 First steps | teaches: alpha | fig")
    with open(plan, "w", encoding="utf-8") as f:
        f.write(text)
    code, out = run(b, "1")
    check(code == 1 and any(l.startswith("ERROR") and "1.1 must contain a drawn figure" in l for l in out), out)
    with open(os.path.join(b, "chapters", "01-basics.md"), encoding="utf-8") as f:
        text = f.read().replace("A picture.", "<!-- fig: id=boxes\nbox a -> box b\n-->\n\n![boxes](fig/01-basics/boxes.svg)")
    with open(os.path.join(b, "chapters", "01-basics.md"), "w", encoding="utf-8") as f:
        f.write(text)
    code, out = run(b, "1")
    check(not any("must contain a drawn figure" in l for l in out), out)


@test
def word_floors():
    code, out = run(three(words=1000), "1")
    check(code == 0 and any(l.startswith("NOTE") and "1.1 has" in l and "a lesson usually runs 1,200 to 3,000" in l for l in out), out)
    code, out = run(three(words=1300), "1")
    check(not any("a lesson usually runs" in l for l in out), out)


@test
def short_sections():
    extra = "1.4 One command | short | teaches: gamma"
    text = "## 1.4 One command\n\n### The idea\n\n<!-- teaches: gamma = gamma -->\n**gamma** is it. %s\n\n### Remember\n\nIt.\n\n" \
           % " ".join(["word"] * 220) + "**Check yourself**\n\n1. Q?\n\n<details>\n<summary>Answer</summary>\n\nA.\n\n</details>\n"
    b = book([lesson("1.1", "First steps", "", "alpha = alpha", 1300), lesson("1.2", "Second steps", "", "beta = beta", 1300),
              lesson("1.3", "The hub", "", "docker-hub = Docker Hub", 1300), text], extra)
    code, out = run(b, "1")
    check(code == 0 and not any(l.startswith("ERROR") for l in out), out)     # headings are free
    check(any(l.startswith("NOTE") and "1.4 has" in l and "a short section usually runs 300 to 700" in l for l in out), out)
    check(not any("1.4 has" in l and "a lesson usually runs" in l for l in out), out)
    code, out = run(book([text.replace("**Check yourself**", "**Questions**")], extra), "1")
    check(any(l.startswith("ERROR") and "1.4 (short) needs a '**Check yourself**'" in l for l in out), out)

# ---------------------------------------------------------------- suspects, index note


@test
def suspects_all_and_forward_excerpt():
    many = "\n\n".join("Line %d always uses 4096 bytes and never fails." % k for k in range(60))
    b = three(second="As §1.1 showed, and §1.3 will show, it works.\n\n" + many)
    code, short = run(b, "1", "--suspects")
    code2, every = run(b, "1", "--suspects", "--all")
    check(code == 0 and code2 == 0 and "shown)" in short[-2] and "shown)" not in every[-2], (short[-2:], every[-2:]))
    check(len(every) > len(short) > 2, (len(short), len(every)))
    fwd = [l for l in every if "forward" in l.split(" ")[1]]
    check(len(fwd) == 1 and fwd[0].split(" ", 2)[2].startswith("§1.3"), fwd)
    code, out = run(b, "1", "--all")
    check(code == 2 and "--suspects" in out[0], out)


def index(path):
    """us_index.py on a book."""
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_index.py"), path], capture_output=True, text=True, env=ENV)
    check(proc.returncode == 0, proc.stdout + proc.stderr)


@test
def index_note_only_when_true():
    b = book([])
    code, out = run(b)
    check(not any("index is older" in l for l in out), "no chapter written: %s" % out)
    b = three()
    index(b)
    chapter = os.path.join(b, "chapters", "01-basics.md")
    later = time.time() + 5
    os.utime(chapter, (later, later))               # touched, the same text: the index is not stale
    code, out = run(b)
    check(not any("index is older" in l for l in out), out)
    os.remove(os.path.join(b, "INDEX.md"))
    code, out = run(b)
    check(any("index is older" in l for l in out), out)


def main():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok    %s" % fn.__name__)
            passed += 1
        except Exception as e:  # noqa: BLE001
            print("FAIL  %s: %s" % (fn.__name__, str(e)[:1500]))
            failed += 1
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
