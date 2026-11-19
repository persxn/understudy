#!/usr/bin/env python3
"""Tests for stage 3, part B (the record keepers): us_plan.py mark (stamping checked marks, restamp, facts in
STATUS.json), the book pass in status and next, and FACTS.md from us_index.py.
Prints one line per test and "N passed, M failed"; exit 1 on failure.

    python3 tests/tools/stage3.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
import us_bookfmt as bf  # noqa: E402

TMP = tempfile.mkdtemp(prefix="us-stage3-test-")
BOOKS = os.path.join(TMP, "books")
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run(script, *args):
    """Run a script: (exit code, output lines)."""
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args),
                          capture_output=True, text=True, env=ENV)
    return proc.returncode, [l for l in (proc.stdout + proc.stderr).splitlines() if not l.startswith("warning:")]


def plan(name, count, parts=None):
    """A book of `count` one-section chapters; parts: {first chapter: part title}."""
    out = ["# %s" % name.capitalize(), "for: testers", "run: none", ""]
    for n in range(1, count + 1):
        if parts and n in parts:
            out += ["## " + parts[n], ""]
        out += ["### %d Chapter %d" % (n, n), "%d.1 Thing %d | teaches: thing-%d" % (n, n, n), ""]
    return "\n".join(out)


def chapter(n, body="A plain statement about things."):
    return "# Chapter %d: Chapter %d\n\n## %d.1 Thing %d\n\n%s\n" % (n, n, n, n, body)


def book(name, count=1, written=None, parts=None, bodies=None):
    """A book folder: PLAN.md and the chapter files of chapters `written` (default: all)."""
    path = os.path.join(BOOKS, name)
    write(os.path.join(path, "PLAN.md"), plan(name, count, parts))
    for n in written or range(1, count + 1):
        write(os.path.join(path, "chapters", "%02d-chapter-%d.md" % (n, n)), chapter(n, (bodies or {}).get(n, "A plain statement.")))
    return path


def chapter_file(path, n=1):
    return bf.chapter_path(path, n)


def status(path):
    return json.loads(read(os.path.join(path, "STATUS.json")))


MARKED = ('Python 3.12 is the version in Ubuntu 24.04.\n'
          '<!-- checked: how=source date=2026-11-18 ref="packages.ubuntu.com/noble/python3" -->\n\n'
          'The program prints 3. <!-- checked: how=run date=2026-11-18 ref=1-1-demo -->\n\n'
          '<!-- code: id=1-1-pull unrun="no network here" -->\n```console\n$ docker pull alpine\n```\n')

# ---------------------------------------------------------------- B1: stamping


@test
def reviewed_stamps_marks_without_h():
    b = book("stamp", bodies={1: MARKED})
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    check(code == 0 and out == ["chapter 1: reviewed; stamped 2 checked marks"], out)
    lines = read(chapter_file(b)).split("\n")
    marks = [(i, bf.parse_checked(l)) for i, l in enumerate(lines, 1) if bf.parse_checked(l)]
    check(len(marks) == 2 and all(m["h"] == bf.passage_hash(lines, i) for i, m in marks), marks)
    check('ref="packages.ubuntu.com/noble/python3" h=' in read(chapter_file(b)), read(chapter_file(b)))
    check("The program prints 3. <!-- checked: how=run" in read(chapter_file(b)), "inline mark moved")


@test
def reviewed_keeps_an_existing_h():
    b = book("keep", bodies={1: "It is so.\n<!-- checked: how=known date=2026-11-01 h=deadbeef -->\n\n"
                                "Also so. <!-- checked: how=reworded date=2026-11-01 -->"})
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    text = read(chapter_file(b))
    check(code == 0 and out == ["chapter 1: reviewed; stamped 1 checked mark"], out)
    check("h=deadbeef" in text and len(re.findall(r"\bh=", text)) == 2, text)


@test
def reviewed_leaves_file_alone_when_nothing_to_stamp():
    b = book("alone", bodies={1: "It is so.\n<!-- checked: how=known date=2026-11-01 h=deadbeef -->"})
    path = chapter_file(b)
    os.utime(path, ns=(10 ** 18, 10 ** 18))
    before = read(path)
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    check(code == 0 and out == ["chapter 1: reviewed"], out)
    check(read(path) == before and os.stat(path).st_mtime_ns == 10 ** 18, "file rewritten")
    b = book("nomarks")
    path = chapter_file(b)
    os.utime(path, ns=(10 ** 18, 10 ** 18))
    check(run("us_plan.py", "mark", b, "1", "reviewed")[0] == 0 and os.stat(path).st_mtime_ns == 10 ** 18, "touched")


@test
def restamp_stamps_every_mark_afresh():
    b = book("restamp", bodies={1: "It is so.\n<!-- checked: how=known date=2026-11-01 h=deadbeef -->\n\n"
                                   "Also so. <!-- checked: how=reworded date=2026-11-01 -->"})
    code, out = run("us_plan.py", "mark", b, "1", "restamp")
    lines = read(chapter_file(b)).split("\n")
    marks = [(i, bf.parse_checked(l)) for i, l in enumerate(lines, 1) if bf.parse_checked(l)]
    check(code == 0 and out == ["chapter 1: restamped 2 of 2 checked marks"], out)
    check("deadbeef" not in "\n".join(lines) and all(m["h"] == bf.passage_hash(lines, i) for i, m in marks), lines)
    check(len(re.findall(r"\bh=", "\n".join(lines))) == 2, lines)
    os.utime(chapter_file(b), ns=(10 ** 18, 10 ** 18))
    code, out = run("us_plan.py", "mark", b, "1", "restamp")
    check(out == ["chapter 1: restamped 0 of 2 checked marks"] and os.stat(chapter_file(b)).st_mtime_ns == 10 ** 18, out)
    check(status(b)["chapters"]["1"]["facts"] == {"known": 1, "reworded": 1}, status(b))
    check(run("us_plan.py", "mark", b, "1", "restamp", "x")[0] != 0, "extra word accepted")


@test
def malformed_marks_refused_with_their_lines():
    body = ("One.\n<!-- checked: how=guess date=2026-11-18 -->\n\nTwo.\n<!-- checked: how=run -->\n\n"
            "Three.\n<!-- checked: how=source date=2026-11-18 -->\n\nFour.\n<!-- checked: how=known date=18.11.2026 -->\n\n"
            "Five.\n<!-- checked: how=known date=2026-11-18 -->")
    b = book("bad", bodies={1: body})
    before = read(chapter_file(b))
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    check(code == 1 and out[0] == "chapter 1 has 4 malformed checked marks; fix them:", out)
    check(len(out) == 5 and out[1].startswith("  chapters/01-chapter-1.md:6: how=guess is not known"), out)
    check(":9: no date" in out[2] and ":12: how=source has no ref" in out[3] and ":15: date=18.11.2026" in out[4], out)
    check(read(chapter_file(b)) == before and not os.path.exists(os.path.join(b, "STATUS.json")), "changed anyway")
    code, out = run("us_plan.py", "mark", b, "1", "restamp")
    check(code == 1 and "4 malformed" in out[0] and read(chapter_file(b)) == before, out)
    code, out = run("us_plan.py", "mark", b, "1", "written")
    check(code == 0 and out == ["chapter 1: written"], out)


@test
def reviewed_records_facts_and_unrun():
    b = book("record", bodies={1: MARKED + "\nMore.\n<!-- checked: how=run date=2026-11-18 ref=s1 -->\n"})
    run("us_plan.py", "mark", b, "1", "reviewed")
    entry = status(b)["chapters"]["1"]
    check(entry["facts"] == {"run": 2, "source": 1} and entry["unrun"] == 1 and entry["state"] == "reviewed", entry)
    check(list(entry["facts"]) == ["run", "source"], entry)
    b = book("record0")
    run("us_plan.py", "mark", b, "1", "reviewed")
    entry = status(b)["chapters"]["1"]
    check(entry["facts"] == {} and entry["unrun"] == 0, entry)


@test
def risk_notes_still_refused():
    b = book("risk", bodies={1: "Most people forget within a week. <!-- risk: a number from memory -->"})
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    check(code == 1 and "1 risk note" in out[0] and "--risks" in out[0] and "checked:" in out[0], out)

# ---------------------------------------------------------------- B2: status, book pass


@test
def status_shows_facts():
    b = book("facts", count=2, bodies={1: MARKED})
    code, out = run("us_plan.py", "status", b)
    rows = {l.split()[0]: l for l in out[1:]}
    check(code == 0 and rows["1"].endswith("written, 1 not run, facts 2"), out)
    check(rows["2"].endswith("written"), out)


@test
def book_pass_without_parts():
    b = book("noparts", count=6, written=[1, 2, 3, 4, 5])
    for n in (1, 2, 3):
        run("us_plan.py", "mark", b, str(n), "reviewed")
    check(not [l for l in run("us_plan.py", "status", b)[1] if "book pass" in l], "due too soon")
    run("us_plan.py", "mark", b, "4", "reviewed")
    out = run("us_plan.py", "status", b)[1]
    check(out[-1].startswith("book pass due: chapters 1 to 4 (") and "--digest --from 1 --to 4" in out[-1], out)
    code, out = run("us_plan.py", "next", b)
    check(code == 0 and out[0] == "chapter 6, section 6.1 (0 of 1 written)" and out[1].startswith("book pass due: chapters 1 to 4"), out)
    check(len(out) == 2, out)
    code, out = run("us_plan.py", "mark", b, "pass", "4")
    check(code == 0 and out == ["book pass: chapters 1 to 4 covered"] and status(b)["book_pass"] == 4, out)
    check(not [l for l in run("us_plan.py", "status", b)[1] if "book pass" in l], "still due after the pass")
    check(run("us_plan.py", "next", b)[1] == ["chapter 6, section 6.1 (0 of 1 written)"], "next after the pass")
    run("us_plan.py", "mark", b, "5", "reviewed")
    check(not [l for l in run("us_plan.py", "status", b)[1] if "book pass" in l], "chapter 5 closes nothing")
    write(os.path.join(b, "chapters", "06-chapter-6.md"), chapter(6))
    run("us_plan.py", "mark", b, "6", "reviewed")
    check(run("us_plan.py", "status", b)[1][-1].startswith("book pass due: chapters 5 to 6"), "the last chapter closes")
    check(run("us_plan.py", "next", b)[1] == ["all written", run("us_plan.py", "status", b)[1][-1]], "all written + due")
    check(run("us_plan.py", "mark", b, "pass", "9")[0] == 1, "pass beyond the plan accepted")


@test
def book_pass_with_parts():
    b = book("parts", count=3, parts={1: "Part I · Start", 3: "Part II · More"})
    run("us_plan.py", "mark", b, "1", "reviewed")
    check(not [l for l in run("us_plan.py", "status", b)[1] if "book pass" in l], "chapter 1 does not end a part")
    run("us_plan.py", "mark", b, "3", "reviewed")
    check(run("us_plan.py", "status", b)[1][-1].startswith("book pass due: chapters 1 to 3"), "last chapter of part II")
    run("us_plan.py", "mark", b, "pass", "2")
    check(run("us_plan.py", "status", b)[1][-1].startswith("book pass due: chapters 3 to 3"), "after a pass to 2")
    b = book("parts2", count=3, parts={1: "Part I · Start", 3: "Part II · More"})
    run("us_plan.py", "mark", b, "2", "reviewed")
    check(run("us_plan.py", "status", b)[1][-1].startswith("book pass due: chapters 1 to 2"), "end of part I")

# ---------------------------------------------------------------- B3: FACTS.md


@test
def facts_md_made_and_linked():
    b = book("factsmd", count=2, bodies={1: MARKED})
    code, out = run("us_index.py", b)
    path = os.path.join(b, "FACTS.md")
    check(code == 0 and os.path.exists(path), out)
    text = read(path)
    check(text.startswith("# Checked facts: Factsmd\n<!-- generated by scripts/us_index.py; do not edit -->\n"), text)
    check("## Chapter 1: Chapter 1" in text and "## Chapter 2" not in text, text)
    check("- §1.1: Python 3.12 is the version in Ubuntu 24.04. — how it was checked: source, "
          "packages.ubuntu.com/noble/python3, 2026-11-18" in text, text)
    check("- §1.1: The program prints 3. — how it was checked: run, 1-1-demo, 2026-11-18" in text, text)
    check("Shown but not run on the writer's machine:\n\n- §1.1 `1-1-pull`: no network here" in text, text)
    check("[Checked facts](FACTS.md)" in read(os.path.join(b, "README.md")), read(os.path.join(b, "README.md")))
    os.utime(path, ns=(10 ** 18, 10 ** 18))
    run("us_index.py", b)
    check(os.stat(path).st_mtime_ns == 10 ** 18, "rewritten with the same text")


@test
def facts_md_cuts_long_passages():
    b = book("long", bodies={1: ("word " * 60).strip() + ".\n<!-- checked: how=known date=2026-11-18 -->"})
    run("us_index.py", b)
    line = [l for l in read(os.path.join(b, "FACTS.md")).splitlines() if l.startswith("- §1.1")][0]
    check(line == "- §1.1: %s — how it was checked: known, 2026-11-18" % ("word " * 60)[:140], line)


@test
def no_facts_md_without_marks():
    b = book("nofacts", count=2)
    code, out = run("us_index.py", b)
    check(code == 0 and not os.path.exists(os.path.join(b, "FACTS.md")), out)
    check("Checked facts" not in read(os.path.join(b, "README.md")), "linked without a file")
    b = book("gone", bodies={1: "So.\n<!-- checked: how=known date=2026-11-18 -->"})
    run("us_index.py", b)
    check(os.path.exists(os.path.join(b, "FACTS.md")), "not made")
    write(chapter_file(b), chapter(1))
    run("us_index.py", b)
    check(not os.path.exists(os.path.join(b, "FACTS.md")) and "Checked facts" not in read(os.path.join(b, "README.md")),
          "a stale FACTS.md stayed")


def main():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok    " + fn.__name__)
            passed += 1
        except Exception as exc:  # noqa: BLE001
            print("FAIL  %s: %s" % (fn.__name__, str(exc).replace("\n", " | ")[:400]))
            failed += 1
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
