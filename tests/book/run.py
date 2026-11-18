"""Tests for us_bookfmt.py, us_plan.py and us_section.py: python3 tests/book/run.py"""
import glob
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
FIXTURE = os.path.join(HERE, "fixture")
REAL = os.environ.get("JOJO_CHAPTERS", "")  # optional: the C book's chapters folder; unset skips real_book
sys.path.insert(0, SCRIPTS)
import us_bookfmt as bf  # noqa: E402

TMP = tempfile.mkdtemp(prefix="us-book-test-")
os.chmod(TMP, 0o755)  # programs run as an ordinary user when the tests run as root
os.environ["TMPDIR"] = tempfile.tempdir = TMP  # run folders go in TMP too, and leave with it
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TIMES = {}
TESTS = []


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def run(script, *args, stdin=None):
    """Run scripts/<script> with args; returns (exit code, output)."""
    start = time.time()
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args),
                          input=stdin, capture_output=True, text=True, env=ENV)
    TIMES[" ".join((script,) + tuple(a if len(a) < 30 else os.path.basename(a) for a in args))] = time.time() - start
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def fresh_book(name):
    """A temp copy of the fixture book."""
    path = os.path.join(TMP, name)
    shutil.copytree(FIXTURE, path)
    shutil.rmtree(os.path.join(path, "sections"))
    return path


def section(number):
    """Fixture text of a not-yet-written section."""
    return bf.read_text(os.path.join(FIXTURE, "sections", number + ".md"))


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def rejected(number):
    """Path of the saved rejected section."""
    return os.path.join(TMP, "private", "scratch", "rejected-%s.md" % number)

# ---------------------------------------------------------------- plan check


@test
def plan_check_fixture_passes():
    code, out = run("us_plan.py", "check", FIXTURE)
    check(code == 0, out)
    check(out.splitlines()[-1] == "plan ok: 2 chapters, 7 sections, 7 ideas", out)


def broken_plan(old, new):
    """Check a plan with one edit; returns (exit code, output)."""
    book = os.path.join(tempfile.mkdtemp(dir=TMP), "b")
    os.makedirs(book)
    text = bf.read_text(os.path.join(FIXTURE, "PLAN.md"))
    check(old in text, "fixture has no %r" % old)
    bf.write_text(os.path.join(book, "PLAN.md"), text.replace(old, new, 1))
    return run("us_plan.py", "check", book)


PLAN_ERRORS = [
    ("section gap", "1.3   Variables", "1.5   Variables", 1, "PLAN.md:10: 1.5 is section 3 of chapter 1; renumber it 1.3"),
    ("chapter gap", "### 2 Choices", "### 3 Choices", 1, "PLAN.md:13: chapter 3 follows chapter 1; renumber it 2"),
    ("duplicate id", "teaches: comparison", "teaches: comparison, printf", 1, "idea 'printf' already taught in 1.2"),
    ("need taught later", "level: 2\n1.4", "level: 2 | needs: comparison\n1.4", 1, "1.3 needs 'comparison', taught later in 2.1"),
    ("need taught nowhere", "needs: variable", "needs: ghost", 1, "2.1 needs 'ghost', taught nowhere"),
    ("need in same chapter", "needs: printf", "needs: comparison", 1, "2.2 needs 'comparison', taught in the same chapter (2.1)"),
    ("level out of range", "level: 2\n1.4", "level: 7\n1.4", 1, "PLAN.md:10: 1.3: level 7; use 1 to 5"),
    ("second story", "2.1 Comparing values |", "2.1 Comparing values | story |", 1, "1.2"),
    ("unknown field", "needs: printf", "nedds: printf", 1, "unknown field 'nedds: printf'"),
    ("bad idea id", "teaches: comparison", "teaches: compar!son", 1, "bad idea id 'compar!son'"),
    ("six ideas (warn)", "teaches: comparison", "teaches: comparison, c2, c3, c4, c5, c6", 0,
     "warn PLAN.md:14: 2.1 teaches 6 ideas; five at most: split the section"),
    ("three hard in a row (warn)", "2.3 Practice: choices | practice | level: 3", "2.3 Practice: choices | practice | level: 5", 0,
     "warn PLAN.md:16: 2.1, 2.2, 2.3 are level 4 or 5 in a row; put an easier section between them"),
    ("no practice at end (warn)", "2.3 Practice: choices | practice | level: 3", "", 0, "warn PLAN.md:15: chapter 2 does not end with a practice section"),
]


def make_plan_error_test(name, old, new, want_code, want):
    """A test that one broken plan is caught."""
    def fn():
        if name == "three hard in a row (warn)":
            text = bf.read_text(os.path.join(FIXTURE, "PLAN.md")).replace("needs: variable", "needs: variable | level: 4") \
                .replace("needs: printf | level: 2", "needs: printf | level: 4")
            book = os.path.join(tempfile.mkdtemp(dir=TMP), "b")
            os.makedirs(book)
            bf.write_text(os.path.join(book, "PLAN.md"), text)
            code, out = run("us_plan.py", "check", book)
            check(code == 0 and "in a row" not in out, out)
            bf.write_text(os.path.join(book, "PLAN.md"), text.replace("choices | practice | level: 3", "choices | practice | level: 5"))
            code, out = run("us_plan.py", "check", book)
            check(code == 0 and want in out, out)
            return
        if name == "second story":
            code, out = broken_plan("2.2 Making a choice with if |", "2.2 Making a choice with if | story |")
            text = out
            check(code == 0, "one story per chapter must pass: " + out)
            book = os.path.join(tempfile.mkdtemp(dir=TMP), "b")
            os.makedirs(book)
            plan = bf.read_text(os.path.join(FIXTURE, "PLAN.md"))
            plan = plan.replace("1.2 Printing a line |", "1.2 Printing a line | story |")
            bf.write_text(os.path.join(book, "PLAN.md"), plan)
            code, text = run("us_plan.py", "check", book)
            check(code == 1 and "1.2: second story in chapter 1 (first is 1.1)" in text, text)
            return
        code, out = broken_plan(old, new)
        check(code == want_code, "exit %d: %s" % (code, out))
        check(want in out, "expected %r in:\n%s" % (want, out))
    fn.__name__ = "plan_error_" + name.replace(" ", "_").replace("(", "").replace(")", "")
    return fn


for _case in PLAN_ERRORS:
    test(make_plan_error_test(*_case))


@test
def plan_warns_small_chapter():
    code, out = run("us_plan.py", "check", FIXTURE)
    check("chapter 1 has" not in out, out)                     # 4 sections: inside 4 to 12
    code, out = broken_plan("2.3 Practice: choices | practice | level: 3", "2.3 Practice: choices | practice | level: 3\n2.4 More | practice |\n" +
                            "".join("2.%d More %d | practice |\n" % (k, k) for k in range(5, 14)))
    check("chapter 2 has 13 sections (usually 5 to 9); split the chapter" in out, out)

# ---------------------------------------------------------------- brief


@test
def brief_fixture():
    book = fresh_book("brief")
    code, out = run("us_plan.py", "brief", book, "2")
    check(code == 0, out)
    check(len(out.split()) <= 1000, "%d words" % len(out.split()))
    check("- variable §1.3: A variable is a named box in memory that holds one value." in out, out)
    check("- printf §1.2: `printf` is the function that prints text on the screen." in out, out)
    check("1: printf, string literal, variable, assignment" in out, out)
    check("2.2 Making a choice with if | teaches: if-statement, else-branch | needs: printf | level: 2" in out, out)
    check("Chapter 1 closed with:" in out and "Next chapter" not in out, out)
    code, out = run("us_plan.py", "brief", book, "1")
    check("Not yet taught" in out and "2: comparison §2.1, if statement §2.2, else branch §2.2" in out, out)
    check("Next chapter: 2 Choices" in out, out)
    check("From earlier chapters" not in out, "chapter 1 has nothing before it")


@test
def brief_carries_the_book_forward():
    book = fresh_book("brief-carry")
    plan = os.path.join(book, "PLAN.md")
    bf.write_text(plan, bf.read_text(plan).replace("run: c\n", "run: c\nenv: A=1 B=2\n"))
    code, out = run("us_plan.py", "brief", book, "2")
    check(code == 0 and "run: c\nenv: A=1 B=2\n" in out, out)
    check("From earlier chapters:\n- chapter 1: no spine; look in its last section with us_find.py\n" in out, out)
    os.makedirs(os.path.join(book, "spines"))
    bf.write_text(os.path.join(book, "spines", "1.md"), "# Chapter 1 spine\n\nPicture: a variable is a labelled box.\n\n"
                  "Running example: ~/hello.c, a greeting.\n- 1.2 prints a line\n- 1.3 stores a name\n\n"
                  "Terms: printf; variable.\n\nFirst real act: 1.2. Left at end: hello.c prints the name.\n")
    code, out = run("us_plan.py", "brief", book, "2")
    check("From earlier chapters:\n- chapter 1: Picture: a variable is a labelled box. Running example: ~/hello.c, a "
          "greeting. Left at end: hello.c prints the name.\n" in out and "1.2 prints a line" not in out, out)
    bf.write_text(os.path.join(book, "spines", "1.md"), "Picture: " + "long " * 300 + "\n")
    code, out = run("us_plan.py", "brief", book, "2")
    block = out.split("From earlier chapters:\n")[1].split("\n\n")[0]
    check(len(block.split()) <= 150 and block.endswith("…"), "150 words at most: %d" % len(block.split()))
    for k in (1, 2, 3):
        bf.write_text(os.path.join(book, "spines", "%d.md" % k), "Picture: p%d %s\nRunning example: r%d\n"
                      "Left at end: left%d %s\n" % (k, "wide " * 60, k, k, "more " * 60))
    bf.write_text(plan, bf.read_text(plan).rstrip("\n") + "\n\n### 3 Loops\n3.1 Repeating with while | teaches: "
                  "while-loop\n\n### 4 Arrays\n4.1 Many values in a row | teaches: array\n")
    code, out = run("us_plan.py", "brief", book, "4")
    check(code == 0 and "From earlier chapters:\n" in out, out)
    rows = out.split("From earlier chapters:\n")[1].split("\n\n")[0].split("\n")
    check(len(rows) == 3 and len(" ".join(rows).split()) <= 150, "no chapter dropped, 150 words at most: %s" % rows)
    check("Left at end: left1" in rows[0] and "Picture" not in rows[0] and "Left at end: left2" in rows[1]
          and "Picture: p3" in rows[2] and "Left at end: left3" in rows[2], "older chapters give what they left; the last gives its picture: %s" % rows)

# ---------------------------------------------------------------- append, replace, next, status


def chapter2(book):
    """Text of chapter 2's file, or None."""
    path = bf.chapter_path(book, 2)
    return bf.read_text(path) if path else None


def expect_reject(book, text, number, want, chapter=2):
    """Append must refuse text with message `want`, leave the chapter untouched, and save the text."""
    before = chapter2(book)
    if os.path.exists(rejected(number)):
        os.remove(rejected(number))
    code, out = run("us_section.py", "append", book, str(chapter), stdin=text)
    check(code == 1, "accepted: " + out)
    check(want in out, "expected %r in:\n%s" % (want, out))
    check(chapter2(book) == before, "chapter file changed")
    check(os.path.exists(rejected(number)) and bf.read_text(rejected(number)).strip() == text.strip(), "rejected text not saved")
    check(all(l.startswith(("error line", "warn line", "rejected")) for l in out.splitlines()), out)


@test
def append_flow():
    book = fresh_book("append")
    check(run("us_plan.py", "next", book)[1] == "chapter 2, section 2.1 (0 of 3 written)", run("us_plan.py", "next", book)[1])
    out = run("us_plan.py", "status", book)[1]
    check("4/4" in out.splitlines()[1] and out.splitlines()[1].endswith("written"), out)
    check(out.splitlines()[2].endswith("planned"), out)
    code, out = run("us_section.py", "append", book, "2", stdin=section("2.1"))
    check(code == 0, out)
    check(out.splitlines()[0].startswith("ok 2.1 Comparing values  912 words  1 program  0 figures"), out)
    check(len(out.splitlines()) <= 4, out)
    path = bf.chapter_path(book, 2)
    check(path.endswith("02-choices.md") and bf.read_text(path).startswith("# Chapter 2: Choices\n\n## 2.1"), path)
    check(run("us_plan.py", "next", book)[1] == "chapter 2, section 2.2 (1 of 3 written)", "next after 2.1")
    status = json.load(open(os.path.join(book, "STATUS.json")))
    check(status["chapters"]["2"]["state"] == "writing" and status["chapters"]["2"]["sections"] == ["2.1"], status)
    check(run("us_plan.py", "status", book)[1].splitlines()[2].endswith("writing"), "status writing")


def appended_book(name, upto):
    """Fixture copy with chapter 2 sections appended up to (not including) `upto`."""
    book = fresh_book(name)
    for n in ("2.1", "2.2", "2.3"):
        if n == upto:
            break
        code, out = run("us_section.py", "append", book, "2", stdin=section(n))
        check(code == 0, out)
    return book


BAD_SECTIONS = [
    ("no hidden answer", lambda t: t.replace("<details>", "<p>"), "Check yourself has 0 hidden answers"),
    ("no check yourself", lambda t: t.replace("**Check yourself**", "**Questions**"), "no '**Check yourself**'"),
    ("missing teaches", lambda t: t.replace("<!-- teaches: else-branch = else branch, else -->\n", ""), "no marker for planned idea 'else-branch'"),
    ("wrong number", lambda t: t.replace("## 2.2 ", "## 2.3 "), "this is 2.3 but 2.2 is expected"),
    ("two sections", lambda t: t + "\n## 2.3 Practice: choices\n\nMore.\n", "a second section (2.3)"),
    ("bad reference", lambda t: t.replace("In §2.1", "In §9.9"), "§9.9 is not in the plan"),
    ("code without fence", lambda t: t.replace("```c\n", "Here:\n\n```c\n"), "error line 30: id=2-2-demo was not tried: send it to python3 scripts/us_run.py try "),
    ("fence without language", lambda t: t.replace("```c\n", "```\n"), "fence without a language tag"),
    ("unknown mode", lambda t: t.replace("<!-- code: id=2-2-demo -->", "<!-- code: id=2-2-demo mode=skip -->"), "mode 'skip' unknown"),
    ("teaches without words", lambda t: t.replace("<!-- teaches: else-branch = else branch, else -->", "<!-- teaches: else-branch -->"), "teaches 'else-branch' has no words after '='"),
    ("text before heading", lambda t: "Here is the section.\n\n" + t, "error line 1: text before the '## 2.2' heading"),
]


def make_bad_section_test(name, edit, want):
    """A test that one kind of bad section is refused."""
    def fn():
        book = appended_book("bad-" + name.replace(" ", "-"), "2.2")
        expect_reject(book, edit(section("2.2")), "2.2", want)
    fn.__name__ = "append_rejects_" + name.replace(" ", "_")
    return fn


for _case in BAD_SECTIONS:
    test(make_bad_section_test(*_case))


@test
def append_reject_line_numbers():
    book = appended_book("lines", "2.2")
    text = section("2.2").replace("In §2.1", "In §9.9")
    code, out = run("us_section.py", "append", book, "2", stdin=text)
    check("error line 5: §9.9 is not in the plan" in out, out)


@test
def append_resubmit_from_rejected_file():
    book = appended_book("resubmit", "2.2")
    bad = section("2.2").replace("**Check yourself**", "**Questions**")
    run("us_section.py", "append", book, "2", stdin=bad)
    path = rejected("2.2")
    bf.write_text(path, section("2.2"))
    code, out = run("us_section.py", "append", book, "2", "--file", path)
    check(code == 0 and out.startswith("ok 2.2 Making a choice with if"), out)
    check(not os.path.exists(path), "rejected file left behind")


@test
def append_forward_reference_and_title_warning():
    book = appended_book("forward", "2.2")
    text = section("2.2").replace("In §2.1", "In §2.1 (and §2.3 later)").replace("## 2.2 Making a choice with if", "## 2.2 Choosing with if")
    code, out = run("us_section.py", "append", book, "2", stdin=text)
    check(code == 0, out)
    lines = out.splitlines()
    check(len(lines) <= 4 and "1 figure" in lines[0], out)
    check("forward: §2.3" in out and "title differs from the plan: 'Making a choice with if'" in out, out)


@test
def helper_problems_pass_through():
    if not os.path.exists(os.path.join(SCRIPTS, "us_draw.py")):
        return
    book = appended_book("helpers", "2.2")
    code, out = run("us_section.py", "append", book, "2", stdin=section("2.2").replace("q -> big: yes", "q -> -> big"))
    check(code == 0 and out.startswith("ok 2.2"), out)
    check(any(l.startswith("us_draw: ") for l in out.splitlines()), out)
    path = bf.chapter_path(book, 2)
    check(out.splitlines()[-1].endswith("then: python3 scripts/us_draw.py --chapter %s" % (
        os.path.relpath(path) if not os.path.relpath(path).startswith("..") else path)), out)


@test
def story_and_practice_rules():
    book = fresh_book("kinds")
    long_story = "## 1.1 Where C came from\n\n" + ("C was made for Unix. " * 130) + "\n"
    code, out = run("us_section.py", "replace", book, "1.1", "--file", write_tmp(long_story))
    check(code == 1 and "a story is at most 500" in out, out)
    short = "## 1.4 Practice: first steps\n\n" + "**Exercise 1.** Why?\n\n<details>\n<summary>Answer</summary>\n\nBecause.\n\n</details>\n" * 2
    code, out = run("us_section.py", "replace", book, "1.4", "--file", write_tmp(short))
    check(code == 1 and "1.4 is practice with 2 answered tasks; give at least three that climb" in out, out)


def write_tmp(text):
    """Write text to a temp file and return its path."""
    fd, path = tempfile.mkstemp(dir=TMP, suffix=".md")
    os.write(fd, text.encode())
    os.close(fd)
    return path


@test
def cut_off_and_finish():
    book = appended_book("cutoff", "2.3")
    check(run("us_plan.py", "next", book)[1] == "chapter 2, section 2.3 (2 of 3 written)", run("us_plan.py", "next", book)[1])
    code, out = run("us_section.py", "append", book, "2", stdin=section("2.3"))
    check(code == 0 and out.startswith("ok 2.3 Practice: choices"), out)
    check(run("us_plan.py", "next", book)[1] == "all written", "next after last")
    row = run("us_plan.py", "status", book)[1].splitlines()[2]
    check("3/3" in row and row.endswith("written"), row)
    check(json.load(open(os.path.join(book, "STATUS.json")))["chapters"]["2"]["state"] == "written", "status json")
    code, out = run("us_section.py", "append", book, "2", stdin=section("2.3"))
    check(code == 1 and "fully written" in out, out)


def route(text):
    """Write the shared private/route.md (None: remove it)."""
    path = os.path.join(TMP, "private", "route.md")
    if text is None:
        os.path.exists(path) and os.remove(path)
    else:
        bf.write_text(path, text)
    return path


@test
def next_follows_the_route_and_leaves_out_skip():
    book = fresh_book("rt")
    shutil.rmtree(os.path.join(book, "chapters"))
    try:
        route(None)
        check(run("us_plan.py", "next", book)[1] == "chapter 1, section 1.1 (0 of 4 written)", "no route: plan order")
        route("# Route\n- rt-two 1 another book · skip\n- other 2 skip\n")
        check(run("us_plan.py", "next", book)[1].startswith("chapter 1,"), "a route naming only other books changes nothing")
        route("- rt 2 choices first, needed in 3 weeks\n- rt 1 basics\n")
        check(run("us_plan.py", "next", book)[1] == "chapter 2, section 2.1 (0 of 3 written)", run("us_plan.py", "next", book)[1])
        route("- rt/2 choices · skip\n")
        check(run("us_plan.py", "next", book)[1].startswith("chapter 1,"), "skip left out; unnamed chapters follow")
        route("- rt 1 skip\n- rt 2 skip\n")
        check(run("us_plan.py", "next", book)[1] == "all written (skipped on the route: 1, 2)", run("us_plan.py", "next", book)[1])
    finally:
        route(None)


@test
def place_records_skip_and_claimed_once():
    book = fresh_book("pl")
    shutil.rmtree(os.path.join(book, "chapters"))
    levels = os.path.join(TMP, "private", "levels.yaml")
    try:
        path = route("# Route\n- pl 1 basics\n\nLeft off on purpose:\n- pl-extra 3\n")
        bf.write_text(levels, "pl/1: {level: 2, state: proven, checked: 2026-01-01, next: 2026-01-04}\n")
        code, out = run("us_plan.py", "place", book, "2", "1")
        check(code == 0 and out == "placed pl: chapters 2, 1 marked skip in route.md; 1 new claimed line in levels.yaml", out)
        check(bf.read_text(path) == "# Route\n- pl 1 basics · skip\n- pl 2 Choices · skip\n\nLeft off on purpose:\n- pl-extra 3\n",
              bf.read_text(path))
        lines = bf.read_text(levels).splitlines()
        check(lines[0].endswith("state: proven, checked: 2026-01-01, next: 2026-01-04}") and len(lines) == 2 and
              re.fullmatch(r"pl/2: \{level: 1, state: claimed, checked: (\S+), next: (\S+)\}", lines[1]), lines)
        before = bf.read_text(path), bf.read_text(levels)
        code, out = run("us_plan.py", "place", book, "2", "1")
        check(code == 0 and (bf.read_text(path), bf.read_text(levels)) == before and "0 new claimed lines" in out, out)
        check(run("us_plan.py", "next", book)[1] == "all written (skipped on the route: 1, 2)", "next sees the placement")
        check(run("us_plan.py", "place", book, "9")[0] == 1, "a chapter not in the plan is refused")
        route(None)
        os.remove(levels)
        run("us_plan.py", "place", book, "2")
        check(bf.read_text(path) == "- pl 2 Choices · skip\n" and bf.read_text(levels).startswith("pl/2: {level: 1, state: claimed"),
              "no route or levels yet: both made")
    finally:
        route(None)
        os.path.exists(levels) and os.remove(levels)


@test
def replace_section():
    book = appended_book("replace", "2.3")
    before = chapter2(book)
    new = section("2.1").replace("Line 4 does the work.", "Line 4 does all the work.")
    code, out = run("us_section.py", "replace", book, "2.1", "--file", write_tmp(new))
    check(code == 0 and out.startswith("ok 2.1"), out)
    after = chapter2(book)
    check("Line 4 does all the work." in after and after.count("## 2.") == 2, after[:200])
    doc = bf.parse_chapter(after)
    check([s.number for s in doc.sections] == ["2.1", "2.2"], "order kept")
    check(section_body(after, "2.2") == section_body(before, "2.2"), "2.2 changed")
    code, out = run("us_section.py", "replace", book, "2.1", "--file", write_tmp(new.replace("**Check yourself**", "**Questions**")))
    check(code == 1 and chapter2(book) == after and os.path.exists(rejected("2.1")), out)
    code, out = run("us_section.py", "replace", book, "2.3", "--file", write_tmp(section("2.3")))
    check(code == 1 and "not written yet" in out, out)


def section_body(text, number):
    """Text of one section of a chapter."""
    doc = bf.parse_chapter(text)
    return bf.section_text(doc, doc.section(number))

# ---------------------------------------------------------------- tried programs, fix hints, mark

PROGRAM_22 = section("2.2")[section("2.2").index("<!-- code: id=2-2-demo -->"):]
PROGRAM_22 = PROGRAM_22[:PROGRAM_22.index("```\n\n") + 4]


def tried_store(book):
    """Folder of chapter 2's tried programs."""
    import us_run
    return us_run.tried_folder(os.path.join(book, "chapters", "02-choices.md"))


@test
def append_fills_tried_program():
    book = appended_book("tried", "2.2")
    code, out = run("us_run.py", "try", book, "2", stdin=PROGRAM_22)
    check(code == 0 and out.splitlines() == ["== id=2-2-demo (run)", "4", out.splitlines()[-1]], out)
    check(os.path.exists(os.path.join(tried_store(book), "2-2-demo.md")), "not stored")
    bare = section("2.2").replace(PROGRAM_22, "<!-- code: id=2-2-demo -->\n")
    full = run("us_section.py", "append", appended_book("tried-words", "2.2"), "2", stdin=section("2.2"))[1]
    code, out = run("us_section.py", "append", book, "2", stdin=bare)
    check(code == 0 and out.splitlines()[0] == full.splitlines()[0], "words or programs differ: %s | %s" % (out, full))
    text = chapter2(book)
    check(PROGRAM_22 + "```text\n4\n```\n" in text, text[text.index("### The code"):][:300])
    check(not os.path.exists(os.path.join(tried_store(book), "2-2-demo.md")), "tried program left after append")


@test
def bare_marker_adds_attributes():
    book = appended_book("tried-attrs", "2.2")
    run("us_run.py", "try", book, "2", stdin=PROGRAM_22.replace("-->", 'stdin="1 2\\n" -->'))
    bare = section("2.2").replace(PROGRAM_22, "<!-- code: id=2-2-demo varies timeout=3 -->\n")
    code, out = run("us_section.py", "append", book, "2", stdin=bare)
    check(code == 0, out)
    check('<!-- code: id=2-2-demo stdin="1 2\\n" varies timeout=3 -->\n```c\n' in chapter2(book), chapter2(book)[:0])


@test
def bare_marker_not_tried():
    book = appended_book("not-tried", "2.2")
    bare = section("2.2").replace(PROGRAM_22, "<!-- code: id=never -->\n")
    expect_reject(book, bare, "2.2", "error line 30: id=never was not tried: send it to python3 scripts/us_run.py try %s 2 first, or include the program" % book)
    check("no fenced program" not in run("us_section.py", "append", book, "2", stdin=bare)[1], "two errors for one marker")


@test
def fix_hint_after_problem():
    book = appended_book("fix-hint", "2.2")
    code, out = run("us_section.py", "append", book, "2", stdin=section("2.2").replace("int x = 4;", "int x = 4; int y;"))
    path = bf.chapter_path(book, 2)
    shown = os.path.relpath(path) if not os.path.relpath(path).startswith("..") else path
    check(code == 0 and "unused variable 'y'" in out, out)
    check(out.splitlines()[-1] == "fix the program in %s with a small edit, then: python3 scripts/us_run.py %s --only 2-2-demo" % (shown, shown), out)


@test
def line_references_filled_in():
    book = appended_book("line-refs", "2.2")
    text = section("2.2").replace("Line 4 does the work.", "Line {L:int x = 4;} does the work, and line {L:2-2-demo:return} ends it.")
    code, out = run("us_section.py", "append", book, "2", stdin=text)
    check(code == 0 and "Line 4 does the work, and line 6 ends it." in chapter2(book), out)
    for ref, want in (("{L:x}", "{L:x}: lines 4, 5 all hold it in id=2-2-demo; write a longer piece of the line"),
                      ("{L:nowhere}", "{L:nowhere}: no line holds it in id=2-2-demo; write a longer piece of the line")):
        book = appended_book("line-refs-bad" + ref[3:-1], "2.2")
        expect_reject(book, section("2.2").replace("Line 4 does", "Line %s does" % ref), "2.2", "error line 41: " + want)
    book = appended_book("line-refs-none", "2.2")
    expect_reject(book, section("2.2").replace("In §2.1", "In §2.1 ({L:main})"), "2.2", "no program above it in the section")


@test
def line_references_read_well():
    import us_section
    prog = "<!-- code: id=long -->\n```c\n" + "".join("int v%d;\n" % k for k in range(1, 41)) + "```\n"
    text, problems = us_section.fill_line_refs(prog + "{L:v3;} is first. See lines {L:v4;} and {L:v40;}; and line {L:v31;}.")
    check(not problems and text.endswith("Line 3 is first. See line 4 and line 40 (`v40;`); and line 31 (`v31;`)."), text)


@test
def line_references_exact_and_never_into_a_session():
    import us_section
    prog = "<!-- code: id=p -->\n```c\nint a = 1;\nint a = 1 + 2;\n```\n"
    text, problems = us_section.fill_line_refs(prog + "See {L:=int a = 1;} and {L:p:=int a = 1 + 2;}.")
    check(not problems and text.endswith("See line 1 and line 2."), (text, problems))
    session = "<!-- code: id=s -->\n```console\n$ git status\n```\n"
    text, problems = us_section.fill_line_refs(prog + session + "Line {L:git status} asks.\n{L:s:git}")
    check(len(problems) == 2 and all("{L:" in m and "name the command in backticks instead" in m for _, m in problems), problems)


@test
def lesson_length_is_advice():
    import us_section
    text = section("2.1").replace("### The picture\n", "### The picture\n\n" + "Words to make it longer. " * 50 + "\n", 1)
    plan = bf.load_plan(FIXTURE)
    rep = us_section.validate(text, plan, "2.1", set())[0]
    check(not rep.errors and not rep.warnings, rep.errors + rep.warnings)
    check(any("usually runs 1,200 to 3,000" in n for n in rep.notes), rep.notes)


@test
def plan_env_lines():
    code, out = broken_plan("run: c\n", "run: c\nenv: GIT_AUTHOR_DATE=2026-01-05T10:00:00 NAME='Sam Rivera'\n")
    check(code == 0 and "plan ok" in out, out)
    code, out = broken_plan("run: c\n", "run: c\nenv: GIT_AUTHOR_DATE\n")
    check(code == 1 and "error PLAN.md:4: env: takes NAME=VALUE words" in out, out)
    code, out = run("us_plan.py")
    check("env: GIT_AUTHOR_DATE=" in out, "env: is documented in the help")
    book = fresh_book("env-book")
    bf.write_text(os.path.join(book, "PLAN.md"), bf.read_text(os.path.join(book, "PLAN.md")).replace(
        "run: c\n", "run: c\nenv: A=1 B='two words'\n"))
    check(bf.plan_env(book) == {"A": "1", "B": "two words"}, bf.plan_env(book))


@test
def sections_that_teach_nothing_new():
    book = fresh_book("no-teaches")
    plan = os.path.join(book, "PLAN.md")
    bf.write_text(plan, bf.read_text(plan).replace("| teaches: if-statement, else-branch |", "|")
                  .replace("2.3 Practice: choices | practice |", "2.3 Practice: choices | practice | teaches: choice-practice |"))
    code, out = run("us_plan.py", "check", book)
    check(code == 0 and "plan ok" in out, out)
    for n in ("2.1", "2.2"):
        text = section(n).replace("<!-- teaches: if-statement = if statement, if -->\n", "") \
            .replace("<!-- teaches: else-branch = else branch, else -->\n", "")
        code, out = run("us_section.py", "append", book, "2", stdin=text)
        check(code == 0, out)
    code, out = run("us_section.py", "append", book, "2", stdin=section("2.3"))
    check(code == 0 and "no marker" not in out, "a practice needs no idea marker: " + out)
    code, out = run("us_check.py", book, "2")
    check(code == 0 and "no marker" not in out, out)


@test
def taught_lookup():
    code, out = run("us_plan.py", "taught", FIXTURE, "printf", "string literal", "variables", "comparing", "pointer")
    check(out.splitlines() == ["printf: taught in §1.2 (printf)", "string literal: taught in §1.2 (string-literal)",
                               "variables: taught in §1.3 (variable)", "comparing: taught in §2.1 (comparison)",
                               "pointer: not taught in chapters 1-2"], out)


@test
def brief_keeps_whole_lines_in_order():
    import us_plan
    book = fresh_book("brief-short")
    plan = bf.load_plan(book)
    bf.write_text(os.path.join(book, "chapters", "01-first-steps.md"), bf.read_text(os.path.join(
        book, "chapters", "01-first-steps.md")).replace("<!-- teaches: variable = variable, variables -->",
                                                         "<!-- teaches: variable -->"))
    full = us_plan.make_brief(book, plan, 2)
    check("- variable §1.3" in full and "Words already taught (use freely):\n1: printf, string literal, variable, assignment"
          in full, full)
    saved = us_plan.BRIEF_CAP
    try:
        us_plan.BRIEF_CAP = len(full.split()) - 3
        short = us_plan.make_brief(book, plan, 2)
    finally:
        us_plan.BRIEF_CAP = saved
    check(" ..." not in short and "Words already taught" not in short and "- variable §1.3" in short
          and len(short.split()) <= len(full.split()) - 3, short)


@test
def mark_reviewed():
    book = appended_book("mark", "2.3")
    code, out = run("us_plan.py", "mark", book, "2", "reviewed")
    check(code == 1 and out == "chapter 2 is not fully written (2 of 3; next 2.3); write it before marking it reviewed", out)
    run("us_section.py", "append", book, "2", stdin=section("2.3"))
    code, out = run("us_plan.py", "mark", book, "2", "reviewed")
    check(code == 0 and out == "chapter 2: reviewed", out)
    check(json.load(open(os.path.join(book, "STATUS.json")))["chapters"]["2"]["state"] == "reviewed", "STATUS.json")
    check(run("us_plan.py", "status", book)[1].splitlines()[2].endswith("reviewed"), "status")
    code, out = run("us_plan.py", "mark", book, "2", "written")
    check(code == 0 and run("us_plan.py", "status", book)[1].splitlines()[2].endswith("written"), out)
    check(run("us_plan.py", "mark", book, "2", "done")[0] != 0, "unknown state accepted")
    code, out = run("us_plan.py", "mark", book, "2", "reviewed", "--false", "3", "--stuck", "1", "--open", "12.4 wording")
    review = bf.read_text(os.path.join(book, "REVIEW.md")).splitlines()
    check(code == 0 and review[0] == "# Review log" and review[-2].endswith(" chapter 2 reviewed") and
          review[-1] == "- %s chapter 2 reviewed, false 3, stuck 1; open: 12.4 wording" % time.strftime("%Y-%m-%d"),
          review)
    check(run("us_plan.py", "mark", book, "2", "reviewed", "--false", "x")[0] != 0, "a count that is no number")

# ---------------------------------------------------------------- parser details


@test
def parser_markers_and_fences():
    text = "\n".join([
        "# Chapter 3: Things", "", "## 3.1 One", "", "<!-- teaches: a.b_c-d = thing, things -->",
        "**Thing** is defined here, see §2.1.", "", "<!-- code: id=x mode=warns stdin=\"3 4\"", "file=u.h -->",
        "````c", "```", "int x;", "````", "```text", "out", "```", "",
        "<!-- fig: id=f1", "kind: flow", "a -> b", "-->", "<!-- diagram: id=f2 shows=\"x\" -->",
        "<!-- resolves: 1.2 -->", "> **Simplified here.** Not the whole truth; §5.1 has it.", ""])
    doc = bf.parse_chapter(text)
    s = doc.sections[0]
    check(doc.number == 3 and doc.title == "Things", doc.title)
    check(s.teaches[0].id == "a.b_c-d" and s.teaches[0].words == ["thing", "things"], s.teaches)
    c = s.code[0]
    check((c.id, c.mode, c.attrs, c.lang, c.fence, c.output) == ("x", "warns", {"stdin": "3 4", "file": "u.h"}, "c", (10, 13), (14, 16)), c)
    check([(f.id, f.kind, f.span) for f in s.figures] == [("f1", "fig", (18, 21)), ("f2", "diagram", (22, 22))], s.figures)
    check(s.resolves == [("1.2", 23)] and [r for r, _ in s.refs] == ["2.1", "5.1"] and len(s.simplified) == 1, s.refs)

# ---------------------------------------------------------------- real book


def real_book():
    if not os.path.isdir(REAL):
        raise AssertionError("no real book at " + REAL)
    book = os.path.join(TMP, "jojoway")
    shutil.copytree(REAL, os.path.join(book, "chapters"))
    code, out = run("us_plan.py", "from-chapters", book, "--title", "Learn C the Jojo way", "--for", "someone who has never programmed")
    check(code == 0, out)
    code, out = run("us_plan.py", "from-chapters", book)
    check(code == 1 and "--force" in out, "overwrote PLAN.md")
    code, out = run("us_plan.py", "check", book)
    REPORT.append("check on the real book:\n" + out)
    check(code == 0 and out.splitlines()[-1] == "plan ok: 11 chapters, 145 sections, 493 ideas", out)
    code, out = run("us_plan.py", "brief", book, "8")
    REPORT.append("brief 8: %d words" % len(out.split()))
    check(code == 0 and len(out.split()) <= 1000 and "The reader already has:" in out and " ..." not in out, out)
    code, out = run("us_plan.py", "status", book)
    check(len(out.splitlines()) == 12 and all(l.endswith("written") for l in out.splitlines()[1:]), out)
    totals = [0, 0, 0]
    for path in sorted(glob.glob(os.path.join(book, "chapters", "*.md"))):
        for s in bf.parse_chapter(bf.read_text(path)).sections:
            totals[0] += len(s.teaches)
            totals[1] += len(s.code)
            totals[2] += len(s.figures)
    check(totals == [493, 786, 90], totals)


if REAL:
    test(real_book)
else:
    print("skip  real_book: JOJO_CHAPTERS not set")


REPORT = []


def main():
    """Run every test; print one line each and a total."""
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("pass  " + fn.__name__)
            passed += 1
        except Exception as exc:  # noqa: BLE001
            print("FAIL  %s: %s" % (fn.__name__, str(exc).replace("\n", " | ")[:400]))
            failed += 1
    if "-v" in sys.argv:
        print("\n".join(REPORT))
        for cmd, secs in TIMES.items():
            if "jojoway" in cmd:
                print("%6.2fs  %s" % (secs, cmd))
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
