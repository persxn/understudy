"""Tests for us_section.py append N.M, patch, and the kind `short`: python3 tests/book/section_fixes.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
FIXTURE = os.path.join(HERE, "fixture")
sys.path.insert(0, SCRIPTS)
import us_bookfmt as bf  # noqa: E402

TMP = tempfile.mkdtemp(prefix="us-section-test-")
os.chmod(TMP, 0o755)  # programs run as an ordinary user when the tests run as root
os.environ["TMPDIR"] = tempfile.tempdir = TMP
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def run(*args, stdin=None):
    """Run us_section.py with args; returns (exit code, output)."""
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_section.py")] + list(args),
                          input=stdin, capture_output=True, text=True, env=ENV)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def fresh_book(name, plan_edit=None):
    """A temp copy of the fixture book, its plan optionally edited."""
    path = os.path.join(TMP, name)
    shutil.copytree(FIXTURE, path)
    shutil.rmtree(os.path.join(path, "sections"))
    if plan_edit:
        plan = os.path.join(path, "PLAN.md")
        bf.write_text(plan, plan_edit(bf.read_text(plan)))
    return path


def section(number):
    """Fixture text of a not-yet-written section."""
    return bf.read_text(os.path.join(FIXTURE, "sections", number + ".md"))


def chapter2(book):
    """Text of chapter 2's file, or None."""
    path = bf.chapter_path(book, 2)
    return bf.read_text(path) if path else None


def status2(book):
    """STATUS.json entry of chapter 2."""
    return json.load(open(os.path.join(book, "STATUS.json")))["chapters"]["2"]


def headings(text):
    """The `## N.M` numbers of a chapter text, in order."""
    return [l.split()[1] for l in text.splitlines() if l.startswith("## ")]

# ---------------------------------------------------------------- append N.M


@test
def append_out_of_order_creates_chapter():
    book = fresh_book("ooo")
    code, out = run("append", book, "2.2", stdin=section("2.2"))
    check(code == 0 and out.startswith("ok 2.2 "), out)
    check(chapter2(book).startswith("# Chapter 2: Choices\n\n## 2.2 "), chapter2(book)[:80])
    check(status2(book)["state"] == "writing" and status2(book)["sections"] == ["2.2"], status2(book))


@test
def append_fills_the_gap_in_order():
    book = fresh_book("gap")
    check(run("append", book, "2.3", stdin=section("2.3"))[0] == 0, "2.3 first")
    code, out = run("append", book, "2", stdin=section("2.1"))
    check(code == 0 and out.startswith("ok 2.1 "), "append N means the first unwritten: " + out)
    check(headings(chapter2(book)) == ["2.1", "2.3"], headings(chapter2(book)))
    check(status2(book)["state"] == "writing", status2(book))
    code, out = run("append", book, "2.2", stdin=section("2.2"))
    check(code == 0, out)
    text = chapter2(book)
    check(headings(text) == ["2.1", "2.2", "2.3"], headings(text))
    check("\n\n## 2.2 " in text and "\n\n## 2.3 " in text and "\n\n\n" not in text, "one blank line between sections")
    st = status2(book)
    check(st["state"] == "written" and st["sections"] == ["2.1", "2.2", "2.3"], st)
    code, out = run("append", book, "2", stdin=section("2.1"))
    check(code == 1 and "fully written" in out, out)


@test
def append_number_refusals():
    book = fresh_book("refuse")
    check(run("append", book, "2.1", stdin=section("2.1"))[0] == 0, "2.1")
    code, out = run("append", book, "2.1", stdin=section("2.1"))
    check(code == 1 and "2.1 is already written; use replace or patch" in out, out)
    code, out = run("append", book, "2.9", stdin=section("2.1"))
    check(code == 1 and "2.9 is not in the plan" in out, out)
    before = chapter2(book)
    code, out = run("append", book, "2.3", stdin=section("2.2"))
    check(code == 1 and "this is 2.2 but 2.3 is expected" in out and "rejected" in out, out)
    code, out = run("append", book, "2.2", stdin=section("2.2").replace("**Check yourself**", "**Questions**"))
    check(code == 1 and "no '**Check yourself**'" in out, "checks still apply: " + out)
    check(chapter2(book) == before, "chapter changed by a refused append")
    code, out = run("append", book, "2.x", stdin=section("2.2"))
    check(code == 1 and "chapter or section number" in out, out)

# ---------------------------------------------------------------- patch


@test
def patch_changes_one_piece_and_reruns():
    book = fresh_book("patch")
    check(run("append", book, "2.1", stdin=section("2.1"))[0] == 0, "2.1")
    check(run("append", book, "2.2", stdin=section("2.2"))[0] == 0, "2.2")
    before = chapter2(book)
    code, out = run("patch", book, "2.1", "--old", "int x = 3;", "--new", "int x = 42;")
    check(code == 0 and out.startswith("ok 2.1 "), out)
    after = chapter2(book)
    check("int x = 42;" in after and "int x = 3;" not in after, "patched")
    out21 = after.split("## 2.2 ")[0]
    check("\n42\n" in out21, "program re-run, new output pasted: " + out21[out21.find("int x"):][:400])
    check(after.split("## 2.2 ")[1] == before.split("## 2.2 ")[1], "2.2 untouched")


@test
def patch_refusals():
    book = fresh_book("patch-no")
    check(run("append", book, "2.1", stdin=section("2.1"))[0] == 0, "2.1")
    before = chapter2(book)
    code, out = run("patch", book, "2.1", "--old", "no such words here", "--new", "x")
    check(code == 1 and "found 0 times in 2.1" in out and "copy it exactly" in out, out)
    code, out = run("patch", book, "2.1", "--old", "Take it slowly", "--new", "x")
    check(code == 1 and "exactly once" in out and "longer piece" in out, out)
    code, out = run("patch", book, "2.2", "--old", "a", "--new", "b")
    check(code == 1 and "2.2 is not written yet; use append" in out, out)
    code, out = run("patch", book, "2.1", "--old", "**Check yourself**", "--new", "**Questions**")
    check(code == 1 and "no '**Check yourself**'" in out, "checks apply to a patch: " + out)
    code, out = run("patch", book, "2.1", "--old", "x")
    check(code == 1 and "patch needs --old TEXT --new TEXT" in out, out)
    check(chapter2(book) == before, "chapter changed by a refused patch")

# ---------------------------------------------------------------- short


def short_book(name):
    """Fixture with 2.2 planned as a short section."""
    return fresh_book(name, lambda t: t.replace("2.2 Making a choice with if |", "2.2 Making a choice with if | short |"))


def short_text(words=400, beats=("The idea", "The code", "Remember"), answers=1):
    """A short section of about `words` words with the given beats."""
    filler = "Read each line slowly and say what it does before you run it. "  # 12 words
    body = {"The idea": "<!-- teaches: if-statement = if statement -->\n<!-- teaches: else-branch = else branch -->\n"
                        "An **if statement** runs a line only when a test holds; the **else branch** runs otherwise.\n",
            "The code": "<!-- code: id=2-2-if -->\n```c\n#include <stdio.h>\n\nint main(void) {\n    if (2 > 1) "
                        "printf(\"yes\\n\");\n    else printf(\"no\\n\");\n    return 0;\n}\n```\n"}
    n = max(1, (words - 40) // 12 // len(beats))
    parts = ["## 2.2 Making a choice with if\n"]
    for b in beats:
        parts.append("### %s\n\n%s\n%s\n" % (b, body.get(b, ""), filler * n))
    parts.append("**Check yourself**\n")
    for i in range(answers):
        parts.append("%d. Which line runs?\n\n<details>\n<summary>Answer</summary>\n\nThe if line.\n\n</details>\n" % (i + 1))
    return "\n".join(parts)


@test
def short_accepted():
    book = short_book("short-ok")
    code, out = run("append", book, "2.2", stdin=short_text())
    check(code == 0 and out.startswith("ok 2.2 "), out)
    book = short_book("short-ok2")
    code, out = run("append", book, "2.2", stdin=short_text(beats=("The question", "The idea", "The code", "The trace", "Remember")))
    check(code == 0, "optional beats in order are fine: " + out)


@test
def short_refused():
    book = short_book("short-bad")
    code, out = run("append", book, "2.2", stdin=short_text(words=260))          # length is advice
    check(code == 0 and "a short section usually runs 300 to 700" in out, out)
    book = short_book("short-bad-2")
    code, out = run("append", book, "2.2", stdin=short_text(answers=0))
    check(code == 1 and ("no '**Check yourself**'" in out or "0 hidden answers" in out), out)
    code, out = run("append", book, "2.2", stdin=short_text().replace("<!-- teaches: else-branch = else branch -->\n", ""))
    check(code == 1 and "no marker for planned idea 'else-branch'" in out, out)


def main():
    """Run every test; print one line each and a total."""
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
