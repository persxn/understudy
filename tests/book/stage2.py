"""Tests for stage 2, part A (question tags, check=, checklists): python3 tests/book/stage2.py"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
import us_bookfmt as bf  # noqa: E402
import us_practice as up  # noqa: E402

TMP = tempfile.mkdtemp(prefix="us-stage2-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []
COUNTER = [0]

PLAN = """# Giving feedback
for: a new team lead
run: none

### 1 Basics
1.1 Why feedback goes wrong | teaches: alpha
1.2 The first conversation | teaches: beta
1.3 Practice: basics | practice

### 2 Later
2.1 Hard cases | teaches: gamma
"""
SHEET = "Reader: a new team lead\nPromise: one hard talk a week\n"
FILL = " ".join(["word"] * 1000)   # a lesson under 900 words is an ERROR
CHECKLIST = "<!-- checklist: id=talk -->\n%s\n"


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def tag(idea, kind="predict", wrong="", unseen=""):
    """A q marker line."""
    return "<!-- q: idea=%s type=%s%s%s -->\n" % (idea, kind, ' wrong="%s"' % wrong if wrong else "",
                                                 ' unseen="%s"' % unseen if unseen else "")


def ask(text, q_tag=""):
    """One numbered question with its hidden answer, its tag (if any) on the line above."""
    return "%s%s\n\n<details>\n<summary>Answer</summary>\n\nThis.\n\n</details>\n\n" % (q_tag, text)


def lesson(number, title, idea, tags=("predict",), body=""):
    """A lesson with one idea and a Check yourself of len(tags) questions; a tag of None is left out."""
    qs = "".join(ask("%d. What happens here?" % k, tag(idea, t) if t else "") for k, t in enumerate(tags, 1))
    return ("## %s %s\n\nA story opens the section.\n\n<!-- teaches: %s = %s -->\n**%s** is said here.\n\n%s\n\n%s\n\n"
            "**Check yourself**\n\n%s" % (number, title, idea, idea, idea, body, FILL, qs))


UNSEEN = "a bakery order form"          # the practice's new case: the chapter never names it before


def practice(number="1.3", tags=("apply", "decide", "build"), items=3, idea="alpha"):
    """A practice: tasks with hidden answers, then a checklist of `items` yes/no tests (none if items is 0)."""
    out = "## %s Practice: basics\n\n" % number
    out += "".join(ask("%d. Do it." % k, tag(idea, t, unseen=UNSEEN if t == "build" else "") if t else "")
                   for k, t in enumerate(tags, 1))
    if items:
        out += CHECKLIST % "\n".join("- Is test %d met?" % k for k in range(1, items + 1))
    return out


def whole(t11=("recall", "predict"), t12=("explain",), prac=None, idea11="alpha"):
    """Chapter 1 in full, every question tagged unless asked otherwise."""
    return {1: [lesson("1.1", "Why feedback goes wrong", "alpha", t11).replace("idea=alpha", "idea=%s" % idea11),
                lesson("1.2", "The first conversation", "beta", t12), prac if prac is not None else practice()]}


def book(chapters, plan=PLAN, sheet=SHEET):
    """A new book: chapters is {N: [section texts]}; returns its folder."""
    COUNTER[0] += 1
    path = os.path.join(TMP, "r%d" % COUNTER[0], "bk")
    os.makedirs(os.path.join(path, "chapters"))
    write(os.path.join(path, "PLAN.md"), plan)
    if sheet:
        write(os.path.join(path, "BOOK.md"), sheet)
    for n, secs in chapters.items():
        name = {1: "01-basics.md", 2: "02-later.md"}[n]
        write(os.path.join(path, "chapters", name), "# Chapter %d: %s\n\n" % (n, name[3:-3].title()) + "\n".join(secs))
    return path


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def run(script, *args):
    """scripts/<script> with args: (exit code, output lines)."""
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args),
                          capture_output=True, text=True, env=ENV)
    return proc.returncode, (proc.stdout + proc.stderr).splitlines()


def errors(out, text=""):
    """ERROR lines holding text."""
    return [l for l in out if l.startswith("ERROR") and text in l]


STAGE2 = ("has no tag", "q tag", "asks only for recall", "no build task", "finish line", "checklist", "questions by kind")

# ---------------------------------------------------------------- us_bookfmt (A2)


@test
def parser_records_tags_untagged_checks_and_checklists():
    text = ("# Chapter 1: Basics\n\n## 1.1 Why\n\n**Check yourself**\n\n"
            + ask("1. First?", tag("alpha", "recall", "equals means the same"))
            + ask("2. Second?")
            + "<!-- code: id=receipt answer check=\"python3 receipt.py\" stdin=\"3\\n\" -->\n```python\nprint(3)\n```\n\n"
            + CHECKLIST % "- One?\n- Two?\n\n- Three?" + "\nAfter the list.\n")
    sec = bf.parse_chapter(text).sections[0]
    check(len(sec.questions) == 2, sec.questions)
    check(sec.qtags == [{"idea": "alpha", "type": "recall", "wrong": "equals means the same", "unseen": "", "line": 7,
                         "question": 1}], sec.qtags)
    check(sec.untagged == [(2, sec.questions[1])], sec.untagged)
    check(sec.checks == [("receipt", "python3 receipt.py")], sec.checks)
    check(len(sec.checklists) == 1 and sec.checklists[0]["id"] == "talk"
          and sec.checklists[0]["items"] == ["One?", "Two?", "Three?"], sec.checklists)


@test
def parser_finds_the_questions_us_practice_finds():
    import us_practice
    for text in (lesson("1.1", "Why", "alpha", ("recall", None, "predict")), practice(tags=("build", None)),
                 "## 1.1 Why\n\nExercise first.\n\n" + ask("1. Before?") + "**Check yourself**\n\nNo number here?\n\n"
                 "<details>\nIt.\n</details>\n\n```python\n# 9. not a question\n```\n\n" + ask("2. Last?")):
        doc = bf.parse_chapter("# Chapter 1: Basics\n\n" + text)
        sec = doc.sections[0]
        free = sec.check_line - sec.line if sec.check_line else len(doc.lines)
        theirs = us_practice.section_questions(doc.lines[sec.line:sec.end], free)
        check(len(theirs) == len(sec.questions), (theirs, sec.questions))
        for q, ln in zip(theirs, sec.questions):
            check(q[0].splitlines()[0].strip() == doc.lines[ln - 1].strip(), (q[0], doc.lines[ln - 1]))

# ---------------------------------------------------------------- us_check (A3)


@test
def a_book_without_book_md_is_untouched():
    secs = whole(t11=(None, None), t12=(None,), prac=practice(tags=(None, None, None), items=0))
    code, out = run("us_check.py", book(secs, sheet=None), "1")
    check(code == 0 and not errors(out), out)
    check(not any(w in l for l in out for w in STAGE2), out)


@test
def a_fully_tagged_book_passes():
    b = book(whole())
    code, out = run("us_check.py", b)
    check(code == 0 and not errors(out), out)
    check(not any(w in l for l in out for w in STAGE2 if w != "questions by kind"), out)


@test
def an_untagged_question_is_an_error():
    code, out = run("us_check.py", book(whole(t11=("recall", None))))
    check(code == 1 and errors(out, "1.1 question 2 has no tag: put `<!-- q: idea=ID type=TYPE -->` on the line "
                                    "above it"), out)
    code, out = run("us_check.py", book(whole(prac=practice(tags=("apply", "build", None)))))
    check(code == 1 and errors(out, "1.3 question 3 has no tag"), out)
    secs = whole()
    secs[1][1] = secs[1][1].replace(tag("beta", "explain"), tag("beta", "explain") + "\n")   # a blank line between
    code, out = run("us_check.py", book(secs))
    check(errors(out, "1.2 question 1 has no tag"), "the tag must be directly above: %s" % out)


@test
def a_tag_must_name_an_idea_taught_at_or_before():
    code, out = run("us_check.py", book(whole(idea11="gamma")))
    check(code == 1 and errors(out, "idea 'gamma', which is taught later (in 2.1)"), out)
    code, out = run("us_check.py", book(whole(idea11="zeta")))
    check(code == 1 and errors(out, "idea 'zeta', which PLAN.md does not teach"), out)
    secs = whole()
    secs[1][1] = secs[1][1].replace("idea=beta", "idea=alpha")          # taught earlier: fine
    code, out = run("us_check.py", book(secs))
    check(code == 0 and not errors(out), out)


@test
def an_unknown_type_is_an_error_listing_the_types():
    code, out = run("us_check.py", book(whole(t12=("guess",))))
    check(code == 1 and errors(out, "type 'guess'; types: recall, explain, predict, fix, apply, decide, build "
                                    "(a find-the-fault question is type=fix)"), out)


@test
def a_lesson_of_only_recall_is_flagged():
    code, out = run("us_check.py", book(whole(t11=("recall", "recall"))))
    flags = [l for l in out if l.startswith("FLAG") and "asks only for recall" in l]
    check(code == 0 and len(flags) == 1 and "1.1 asks only for recall; make one question predict, fix, apply or decide"
          in flags[0], out)
    code, out = run("us_check.py", book(whole(t11=("recall", "fix"))))
    check(not any("asks only for recall" in l for l in out), out)


@test
def numbered_steps_inside_a_tagged_task_are_not_questions():
    steps = "Build the thing in three steps:\n\n1. Read the input.\n2. Sort it.\n3. Print the middle.\n"
    prac = practice().replace("3. Do it.", "**Task 3.** " + steps)
    check("1. Read the input." in prac, prac)
    b = book(whole(prac=prac))
    code, out = run("us_check.py", b)
    check(code == 0 and not errors(out, "has no tag"), out)
    lines = prac.splitlines()
    qs = up.section_questions(lines)
    check(len(qs) == 3 and qs[2][0].startswith("**Task 3.**") and "3. Print the middle." in qs[2][0], qs)
    starts = bf.question_starts(lines)
    check(len(starts) == 3 and lines[starts[2]].startswith("**Task 3.**"), starts)


@test
def a_numbered_checklist_is_not_a_run_of_questions():
    prac = practice()
    for k in range(1, 4):
        prac = prac.replace("- Is test %d met?" % k, "%d. Is test %d met?" % (k, k))
    prac += "\n<details>\n<summary>A model answer</summary>\n\nOne way to do it.\n\n</details>\n"
    check("3. Is test 3 met?" in prac, prac)
    code, out = run("us_check.py", book(whole(prac=prac)))
    check(code == 0 and not errors(out, "has no tag"), out)
    rows = prac.splitlines()
    check(len(up.section_questions(rows, len(rows))) == 3, up.section_questions(rows, len(rows)))


@test
def practice_needs_a_build_task():
    code, out = run("us_check.py", book(whole(prac=practice(tags=("apply", "decide", "fix")))))
    check(code == 1 and errors(out, "1.3 has no build task"), out)


@test
def practice_in_a_run_none_book_needs_a_checklist():
    code, out = run("us_check.py", book(whole(prac=practice(items=0))))
    check(code == 1 and errors(out, "1.3 has no finish line the reader can test alone: add `<!-- checklist:"), out)
    code, out = run("us_check.py", book(whole(prac=practice(items=10))))
    check(code == 0 and not errors(out), out)


@test
def a_checklist_may_have_one_lead_in_paragraph():
    lead = "<!-- checklist: id=talk -->\nAnswer each about your own talk.\n\n"
    prac = practice(items=0) + lead + "\n".join("- Is test %d met?" % k for k in range(1, 4)) + "\n"
    code, out = run("us_check.py", book(whole(prac=prac)))
    check(code == 0 and not errors(out), out)
    doc = bf.parse_chapter(prac)
    check(doc.sections[0].checklists[0]["items"] == ["Is test %d met?" % k for k in range(1, 4)], doc.sections[0].checklists)


@test
def practice_in_a_console_book_may_finish_on_a_checklist():
    console = PLAN.replace("run: none", "run: console")
    code, out = run("us_check.py", book(whole(prac=practice(items=3)), plan=console))
    check(not errors(out, "finish line"), out)
    code, out = run("us_check.py", book(whole(prac=practice(items=0)), plan=console))
    check(code == 1 and errors(out, "1.3 has no finish line the reader can test alone: add `<!-- checklist:"), out)


@test
def a_checklist_holds_three_to_ten_items():
    for n in (2, 11):
        code, out = run("us_check.py", book(whole(prac=practice(items=n))))
        check(code == 1 and errors(out, "1.3 checklist id=talk has %d items; give 3 to 10" % n), out)
        check(errors(out, "1.3 has no finish line"), "a bad checklist is no finish line: %s" % out)
    secs = whole()
    secs[1][0] += CHECKLIST % "- Only one?"             # anywhere, not only in a practice
    code, out = run("us_check.py", book(secs))
    check(code == 1 and errors(out, "1.1 checklist id=talk has 1 items"), out)


RUN_PLAN = PLAN.replace("run: none", "run: python")
MODEL = ('<!-- code: id=receipt check="python3 receipt.py" stdin="3\\n" -->\n```python\nn = int(input())\n'
         'print("total", n * 2)\n```\n\n')


def run_book(model):
    """A run: python book whose practice may hold a model answer; its output pasted by us_run."""
    prac = practice(items=0) + ("\n" + model if model else "")
    b = book(whole(prac=prac), plan=RUN_PLAN)
    code, out = run("us_run.py", os.path.join(b, "chapters", "01-basics.md"))
    check(code == 0, out)
    return b


@test
def practice_in_a_run_book_needs_a_check_block():
    code, out = run("us_check.py", run_book(""))
    check(code == 1 and errors(out, "1.3 has no finish line the reader can test alone: add check=\"COMMAND\""), out)
    b = run_book(MODEL)
    check("```text\ntotal 6\n```" in read(os.path.join(b, "chapters", "01-basics.md")), "output pasted")
    code, out = run("us_check.py", b)
    check(code == 0 and not errors(out), out)


@test
def chapter_check_counts_questions_by_kind():
    secs = whole(t11=("recall", "predict"), t12=("explain", None))
    code, out = run("us_check.py", book(secs), "1")
    notes = [l for l in out if "questions by kind" in l]
    check(len(notes) == 1 and notes[0].startswith("NOTE") and notes[0].endswith(
        "questions by kind: recall 1 · explain 1 · predict 1 · apply 1 · decide 1 · build 1 · untagged 1"), out)
    code, out = run("us_check.py", book(secs))
    check(not any("questions by kind" in l for l in out), "only for one chapter: %s" % out)

# ---------------------------------------------------------------- us_run (A1)


def chapter(marker, body='print("hi")', lang="python"):
    """A one-block chapter file; returns its path."""
    COUNTER[0] += 1
    path = os.path.join(TMP, "ch%d.md" % COUNTER[0])
    write(path, "# Chapter 1: X\n\n## 1.1 A\n\n<!-- code: %s -->\n```%s\n%s\n```\n" % (marker, lang, body))
    return path


@test
def us_run_accepts_check_on_a_run_program():
    path = chapter('id=ok check="python3 ok.py" stdin="3\\n"', "print(int(input()) * 2)")
    code, out = run("us_run.py", path)
    check(code == 0 and "```text\n6\n```" in read(path), (out, read(path)))
    code, out = run("us_run.py", path, "--check")
    check(code == 0, out)


@test
def us_run_refuses_check_elsewhere():
    for marker, why, lang in (('id=f mode=fragment check="python3 f.py"', "mode=fragment", "python"),
                              ('id=c mode=compile check="./c"', "mode=compile", "c"),
                              ('id=e mode=error check="./e"', "mode=error", "c"),
                              ('id=v varies check="python3 v.py"', "varies", "python"),
                              ('id=s check="ls"', "a console session", "console"),
                              ('id=n check=""', "an empty command", "python")):
        body = "$ echo hi" if lang == "console" else "int main(void) { return 0; }" if lang == "c" else 'print("hi")'
        path = chapter(marker, body, lang)
        code, out = run("us_run.py", path)
        hit = [l for l in out if "check= needs a mode=run program whose output is pasted, not %s: remove check= or "
               "make it such a program" % why in l]
        check(code == 1 and len(hit) == 1, (marker, out))
        check("```text" not in read(path), "nothing run or pasted: %s" % read(path))


@test
def a_tag_opens_a_task_whatever_its_first_line_looks_like():
    prac = "## 1.3 Practice: basics\n\n" + "".join(
        ask(first, tag("alpha", t)) for first, t in (("**1. Predict.** What happens?", "predict"),
                                                     ("### Task 2, on your own", "decide"),
                                                     ("Build the whole thing.", "build")))
    prac = prac.replace("type=build", 'type=build unseen="%s"' % UNSEEN)
    prac += CHECKLIST % "\n".join("- Test %d?" % k for k in range(1, 4))
    b = book(whole(prac=prac))
    code, out = run("us_check.py", b)
    check(code == 0 and not errors(out, "has no tag") and not errors(out, "no build task"), out)
    import us_practice
    lines = prac.splitlines()
    qs = us_practice.section_questions(lines, len(lines))
    check(len(qs) == 3 and qs[0][0].startswith("**1. Predict.**") and qs[2][0].startswith("Build the whole"), qs)


@test
def practice_must_reach_something_unseen():
    plain = practice().replace(' unseen="%s"' % UNSEEN, "")
    code, out = run("us_check.py", book(whole(prac=plain)))
    check(code == 1 and errors(out) == ['ERROR chapters/01-basics.md:61 the practice section has no task on something '
                                        'new: tag one task unseen="<its name>" (a problem, case or material the '
                                        'chapter has not used)'], out)
    secs = whole()
    secs[1][1] = secs[1][1].replace("A story opens the section.", "A story opens the section, about A Bakery\nOrder form.")
    b = book(secs)
    code, out = run("us_check.py", b)                  # case and line breaks do not hide it
    text = read(os.path.join(b, "chapters", "01-basics.md")).splitlines()
    used = 1 + next(k for k, l in enumerate(text) if "A Bakery" in l)
    at = 1 + next(k for k, l in enumerate(text) if "unseen=" in l)
    check(code == 1 and errors(out) == ['ERROR chapters/01-basics.md:%d unseen="a bakery order form" is already used '
                                        'earlier in this chapter (line %d): the reader must meet it first in the '
                                        'practice' % (at, used)], out)
    write(os.path.join(b, "STATUS.json"), '{"chapters": {"1": {"state": "written"}}}')
    code, out = run("us_check.py", b)                  # a finished chapter: a NOTE, so it still passes
    check(code == 0 and any(l.startswith("NOTE ") and "is already used earlier" in l for l in out), out)
    import us_practice
    qs = [q for q in us_practice.book_questions(b) if q["type"] == "build"]
    check(len(qs) == 1 and "unseen" not in qs[0]["question"], qs)


@test
def python_error_mode_shows_what_the_reader_sees():
    path = chapter("id=bad-indent mode=error", "if True:\nprint(1)")
    code, out = run("us_run.py", path)
    text = read(path)
    check("IndentationError" in text and "Sorry:" not in text and 'File "' in text, (out, text))


@test
def a_term_written_with_a_capital_is_matched_exactly():
    secs = whole()
    secs[1][0] = secs[1][0].replace("A story opens the section.", "It is true that a story opens the section.")
    secs[1][1] = secs[1][1].replace("<!-- teaches: beta = beta -->", "<!-- teaches: beta = beta, True -->")
    code, out = run("us_check.py", book(secs), "1")
    check(not any("'true' is used here" in l.lower() for l in out), out)


@test
def the_sheet_is_noted_when_overgrown_and_the_brief_keeps_two_left_lines():
    sheet = SHEET + "".join("Left at end of chapter %d: state %d.\n" % (k, k) for k in range(1, 5))
    b = book(whole(), sheet=sheet)
    code, out = run("us_plan.py", "brief", b, "1")
    text = "\n".join(out)
    check("chapter 4: state 4" in text and "chapter 3: state 3" in text and "chapter 1: state 1" not in text, out)
    b = book(whole(), sheet=SHEET + "Promise: " + "word " * 400 + "\nLeft at end of chapter 1: " + "word " * 70 + "\n")
    code, out = run("us_check.py", b)
    check(any(l.startswith("NOTE") and "the sheet's own lines have" in l
                     and "'Left at end of chapter N:' lines are not counted): shorten the other lines" in l for l in out)
          and any(l.startswith("NOTE") and "this line has 7" in l for l in out), out)


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
