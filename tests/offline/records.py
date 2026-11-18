"""Records kept by scripts: lesson answers (us_practice.py record), the resume note, lookup with nothing written.

    python3 tests/offline/records.py

Everything runs on temp copies of the fixture book and a temp private folder.
One line per test, then "N passed, M failed"; exit 1 on any failure.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
FIXTURE = os.path.join(ROOT, "tests", "book", "fixture")
TMP = tempfile.mkdtemp(prefix="us-records-")
TODAY = datetime.date.today()
RESULTS = []


def env(private):
    e = dict(os.environ, UNDERSTUDY_PRIVATE=private)
    e.pop("UNDERSTUDY_TODAY", None)
    return e


def run(script, *args, e=None):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + [str(a) for a in args],
                       capture_output=True, text=True, env=e)
    return p.returncode, p.stdout + p.stderr


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("pass  " if ok else "FAIL  ") + name + ("" if ok else ": " + str(detail).replace("\n", " | ")[:400]))


def day(n):
    return (TODAY + datetime.timedelta(days=n)).isoformat()


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def test_record():
    book, private = os.path.join(TMP, "fx"), os.path.join(TMP, "p1")
    shutil.copytree(FIXTURE, book)
    e = env(private)
    levels, weak = os.path.join(private, "levels.yaml"), os.path.join(private, "weaknesses.md")

    code, out = run("us_practice.py", "record", book, "1.3", "right", e=e)
    data = json.load(open(os.path.join(private, "practice.json")))
    rec = data.get("fx/1.3/lesson", {})
    check("right: logged in practice.json, box 2, back in 3 days", code == 0 and (rec.get("box"), rec.get("due")) == (2, day(3)), (out, rec))
    want = "fx/1: {level: 1, state: in progress, checked: %s, next: %s}" % (TODAY, day(3))
    check("right: levels.yaml gets an in-progress line with a next date", read(levels) == want + "\n", read(levels))
    check("record says exactly what it added to levels.yaml", "levels.yaml: added the line `%s`" % want in out, out)
    check("right: nothing in weaknesses.md", not os.path.exists(weak), read(weak))
    check("record rebuilds the resume note", "resume note written:" in out and os.path.exists(os.path.join(private, "RESUME.md")), out)

    code, out = run("us_practice.py", "record", book, "§1.2", "partly", "--sure", "--note", "mixed up %d and %s", e=e)
    rec = json.load(open(os.path.join(private, "practice.json")))["fx/1.2/lesson"]
    check("partly: box kept (1), back tomorrow", code == 0 and (rec["box"], rec["due"]) == (1, day(1)), (out, rec))
    line = "- %s §1.2 Printing a line (fx): partly, sure: mixed up %%d and %%s" % TODAY
    check("partly: dated line with the note and 'sure' in weaknesses.md", read(weak) == line + "\n", read(weak))
    check("partly: the chapter's next date comes closer (2 days)", read(levels).strip().endswith("next: %s}" % day(2)), read(levels))
    before = (read(levels), read(weak))
    code, out = run("us_practice.py", "record", book, "1.2", "partly", "--sure", "--note", "mixed up %d and %s", e=e)
    check("safe to run again: no second line in either file", code == 0 and (read(levels), read(weak)) == before, (read(levels), read(weak)))
    check("the second answer is still logged", json.load(open(os.path.join(private, "practice.json")))["fx/1.2/lesson"]["history"].__len__() == 2)

    proven = "fx/2: {level: 2, state: proven, checked: 2026-01-01}"
    open(levels, "a").write(proven + "\n")
    code, out = run("us_practice.py", "record", book, "2.1", "no", e=e)
    got = [l for l in read(levels).splitlines() if l.startswith("fx/2:")]
    check("no: a proven level is never lowered, only a next date added",
          got == ["fx/2: {level: 2, state: proven, checked: 2026-01-01, next: %s}" % day(2)] and
          "levels.yaml: added `next: %s` to fx/2" % day(2) in out, (got, out))
    check("no: weak line without note", read(weak).splitlines()[-1] == "- %s §2.1 Comparing values (fx): no" % TODAY, read(weak))
    rec = json.load(open(os.path.join(private, "practice.json")))["fx/2.1/lesson"]
    check("no: box 1, back tomorrow", (rec["box"], rec["due"]) == (1, day(1)), rec)

    code, out = run("us_practice.py", "record", book, "9.9", "right", e=e)
    check("unknown section: exit 1, says what to do", code == 1 and "no section 9.9 in the plan" in out, out)
    code, out = run("us_practice.py", "record", book, "1.2", "maybe", e=e)
    check("bad mark: exit 2 with usage", code == 2 and "right|partly|no" in out, out)
    code, out = run("us_practice.py", book, "--plain", "--count", 50, e=e)
    check("lesson records do not appear as offline questions", code == 0 and "answers given in a lesson" not in out, out[:300])
    code, out = run("us_practice.py", "--stats", e=e)
    check("stats count lesson answers", code == 0 and "§1.2 Printing a line" in out, out)
    return book, private


def test_resume(book, private):
    e = env(private)
    open(os.path.join(private, "now.md"), "w").write("# Now\nStopped in §1.3, mid trace.\nNext: write chapter 1\nAsked about Podman.\n")
    open(os.path.join(private, "build.md"), "w").write("# Project\nfolder: ~/flask-app\nstep: build\ntests: the learner\n"
                                                      "open: port not published\nreview: none\nsixth line\n")
    open(os.path.join(private, "machine.md"), "w").write(
        "# This machine and its limits\n\n## Measured (us_doctor.py, %s)\n- system: Ubuntu 24.04\n"
        "- blocked: Docker Hub cannot be reached from here. No image can be\n  downloaded until that is fixed.\n"
        "- memory: 8 GB\n\n## Told by the learner\n- internet:\n" % TODAY)
    code, out = run("us_resume.py", "--next", "write chapter 2", book, e=e)
    now = read(os.path.join(private, "now.md"))
    check("--next replaces the Next: line and keeps the rest",
          code == 0 and now == "# Now\nStopped in §1.3, mid trace.\nNext: write chapter 2\nAsked about Podman.\n", now)
    note = read(os.path.join(private, "RESUME.md"))
    lines = note.splitlines()
    check("blocked line at the very top, continuation joined",
          lines[2] == "## Blocked on this machine" and
          lines[3] == "- blocked: Docker Hub cannot be reached from here. No image can be downloaded until that is fixed.", lines[:5])
    check("the whole of now.md is shown", "- Stopped in §1.3, mid trace." in note and "- Next: write chapter 2" in note and
          "- Asked about Podman." in note, note)
    check("the open project's first lines are shown", "- folder: ~/flask-app" in note and "- review: none" in note and
          "sixth line" not in note, note)
    check("weak spots from weaknesses.md and practice.json",
          "§2.1 Comparing values (missed 1)" in note and "§1.2 Printing a line (fx): partly, sure" in note, note)
    check("written state comes from the book", "written 1, reviewed none" in note and "next to write: chapter 2" in note, note)
    os.remove(os.path.join(private, "now.md"))
    run("us_resume.py", "--next", "read chapter 1", book, e=e)
    check("--next adds now.md when there is none", read(os.path.join(private, "now.md")) == "Next: read chapter 1\n",
          read(os.path.join(private, "now.md")))
    code, out = run("us_resume.py", "--next", e=e)
    check("--next with no text: exit 2", code == 2 and "--next needs" in out, out)

    text = read(os.path.join(FIXTURE, "sections", "2.1.md"))
    open(os.path.join(book, "chapters", "02-choices.md"), "w").write("# Chapter 2: Choices\n\n" + text)
    run("us_resume.py", book, e=e)
    note = read(os.path.join(private, "RESUME.md"))
    check("a chapter with some sections written is named", "some sections of 2" in note, note)


def test_nothing_written():
    book, private = os.path.join(TMP, "empty"), os.path.join(TMP, "p2")
    os.makedirs(book)
    shutil.copy(os.path.join(FIXTURE, "PLAN.md"), book)
    e = env(private)
    code, out = run("us_resume.py", book, e=e)
    note = read(os.path.join(private, "RESUME.md"))
    check("nothing written: says so, no empty practice line", code == 0 and "Nothing is written yet" in note and
          "due today" not in note and "written none" in note, note)
    check("nothing written: the first chapter's titles to look up and the machine check",
          "Look up what chapter 1, First steps, is about: Where C came from; Printing a line" in note and
          "us_doctor.py" in note, note)
    code, out = run("us_find.py", "printf", "--book", book, e=e)
    check("us_find on a book with nothing written: exit 0, says so", code == 0 and out.startswith("nothing is written yet: "), out)
    code, out = run("us_find.py", "printf", "--book", os.path.join(TMP, "fx"), e=e)
    check("us_find on a written book still goes to the index", "nothing is written yet" not in out, out)


def main():
    book, private = test_record()
    test_resume(book, private)
    test_nothing_written()
    passed = sum(RESULTS)
    print("%d passed, %d failed" % (passed, len(RESULTS) - passed))
    shutil.rmtree(TMP, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
