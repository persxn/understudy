"""Tests for the final upgrade's script changes (section C): python3 tests/book/final_fixes.py"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
TMP = tempfile.mkdtemp(prefix="us-final-fixes-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []
COUNTER = [0]

PLAN = """# Giving feedback
for: a new team lead
run: none
kind: skill

### 1 Basics
1.1 Why feedback goes wrong | teaches: alpha
1.2 The first conversation | teaches: beta
1.3 Practice: basics | practice

### 2 Later
2.1 Hard cases | teaches: gamma
"""

ANSWER = "**Check yourself**\n\n1. What is it?\n\n<details>\n<summary>Answer</summary>\n\nThis.\n\n</details>\n"


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def lesson(number, title, idea, body="", ask=True):
    """A free-form lesson: headings of its own, one idea marker, a Check yourself with one hidden answer."""
    return ("## %s %s\n\nA story opens the section.\n\n### When people talk past each other\n\n"
            "<!-- teaches: %s = %s -->\n**%s** is said here and shown by example.\n\n%s\n\n%s" % (
                number, title, idea, idea, idea, body, ANSWER if ask else "Nothing to ask.\n"))


def practice(number, tasks=3):
    """A practice section with tasks and hidden answers."""
    return "## %s Practice: basics\n\n" % number + "".join(
        "%d. Do it.\n\n<details>\n<summary>Answer</summary>\n\nDone.\n\n</details>\n\n" % k for k in range(1, tasks + 1))


FILL = " ".join(["word"] * 1000)   # a lesson under 900 words is an ERROR


def book(chapters, plan=PLAN, sheet=None):
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


def whole(body1="", body2=""):
    """Chapter 1 written in full."""
    return {1: [lesson("1.1", "Why feedback goes wrong", "alpha", body1 + "\n\n" + FILL),
                lesson("1.2", "The first conversation", "beta", body2 + "\n\n" + FILL), practice("1.3")]}


@test
def free_form_lesson_passes_and_run_none_checks_clean():
    b = book(whole())
    code, out = run("us_check.py", b)
    check(code == 0 and not any(l.startswith("ERROR") for l in out), out)
    check(any("usually runs 1,200 to 3,000" in l and l.startswith("NOTE") for l in out), "length is a note: %s" % out)
    code, out = run("us_plan.py", "check", b)
    check(code == 0 and any(l.startswith("plan ok") for l in out), out)
    code, out = run("us_run.py", os.path.join(b, "chapters", "01-basics.md"))
    check(code == 0 and "nothing to run" in " ".join(out), out)


@test
def plan_rejects_unknown_kind():
    b = book({}, PLAN.replace("kind: skill", "kind: poetry"))
    code, out = run("us_plan.py", "check", b)
    check(code == 1 and any("kind: 'poetry' is not known" in l for l in out), out)


@test
def lesson_without_check_yourself_fails():
    secs = whole()
    secs[1][0] = lesson("1.1", "Why feedback goes wrong", "alpha", ask=False)
    code, out = run("us_check.py", book(secs))
    check(code == 1 and any(l.startswith("ERROR") and "no '**Check yourself**'" in l for l in out), out)


@test
def dangling_references():
    b = book(whole("See section 7.1 and chapter 9, and §1.2."))
    code, out = run("us_check.py", b)
    check(any(l.startswith("ERROR") and "points to 7.1, which the plan does not have" in l for l in out), out)
    check(any(l.startswith("ERROR") and "points to chapter 9, which the plan does not have" in l for l in out), out)
    b = book({1: [lesson("1.1", "Why feedback goes wrong", "alpha")], 2: [lesson("2.1", "Hard cases", "gamma", "As in §1.2.")]})
    code, out = run("us_check.py", b, "2")
    check(any(l.startswith("NOTE") and "points to 1.2, which comes earlier but is not written yet" in l for l in out), out)


RISKY = ("Most people forget within a week. <!-- risk: a number from memory -->\n\n"
         "<!-- code: id=wipe -->\n```console\n$ rm -rf ~/notes\n```\n\n"
         "<!-- code: id=srv unrun=\"needs a mail server\" -->\n```console\n$ mail -s hi team\n```\n\n"
         "See section 8.2.")


@test
def risks_list_every_kind():
    b = book(whole(RISKY))
    code, out = run("us_check.py", b, "1")
    check(any(l.startswith("NOTE") and "risk: 1 marked for review" in l for l in out), out)
    code, out = run("us_check.py", b, "1", "--risks")
    text = "\n".join(out)
    check(code == 0, text)
    check("risk chapters/01-basics.md:" in text and "a number from memory" in text
          and "    Most people forget within a week." in text, text)
    check(any(l.startswith("destroys ") and "rm -rf ~/notes" in l for l in out), text)
    check(any(l.startswith("reference ") and "8.2" in l for l in out), text)
    check(any(l.startswith("unrun ") and "needs a mail server" in l for l in out), text)
    check(out[-1] == "4 items to review in chapter 1", text)


@test
def mark_reviewed_refuses_with_risks_left():
    b = book(whole("Most people forget within a week. <!-- risk: a number from memory -->"))
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    check(code == 1 and "1 risk note" in out[0] and "--risks" in out[0], out)
    path = os.path.join(b, "chapters", "01-basics.md")
    write(path, read(path).replace(" <!-- risk: a number from memory -->", ""))
    code, out = run("us_plan.py", "mark", b, "1", "reviewed")
    check(code == 0 and out == ["chapter 1: reviewed"], out)


@test
def brief_shows_book_sheet():
    sheet = "Reader: a new team lead\nPromise: one hard talk a week\nLeft at end of chapter 1: a script\n"
    b = book(whole(), sheet=sheet)
    os.makedirs(os.path.join(b, "spines"))
    write(os.path.join(b, "spines", "1.md"), "Picture: a ladder\n")
    code, out = run("us_plan.py", "brief", b, "2")
    text = "\n".join(out)
    check(code == 0 and text.startswith("Reader: a new team lead") and "Left at end of chapter 1: a script" in text, text)
    check("From earlier chapters" not in text and "kind: skill" in text and "2.1 Hard cases" in text, text)
    os.remove(os.path.join(b, "BOOK.md"))
    code, out = run("us_plan.py", "brief", b, "2")
    check("From earlier chapters:" in out, "no sheet: the old block stays: %s" % out)


@test
def thin_lesson_and_thin_short_are_errors():
    secs = whole()
    secs[1][0] = lesson("1.1", "Why feedback goes wrong", "alpha", " ".join(["word"] * 300))
    code, out = run("us_check.py", book(secs))
    check(code == 1 and any(l.startswith("ERROR") and "1.1 has" in l and "a lesson this short has left out a move"
                            in l and "mark it `short` in PLAN.md" in l for l in out), out)
    check(not any("1.2 has" in l and l.startswith("ERROR") for l in out), "800 words is only a NOTE: %s" % out)
    plan = PLAN.replace("1.1 Why feedback goes wrong | teaches: alpha", "1.1 Why feedback goes wrong | short | teaches: alpha")
    code, out = run("us_check.py", book(secs, plan))
    check(not any("1.1 has" in l and l.startswith("ERROR") for l in out), "300 words is fine for a short: %s" % out)
    secs[1][0] = lesson("1.1", "Why feedback goes wrong", "alpha", " ".join(["word"] * 100))
    code, out = run("us_check.py", book(secs, plan))
    check(code == 1 and any(l.startswith("ERROR") and "1.1 has" in l and "too thin even for a short section" in l
                            for l in out), out)


@test
def words_per_section_note():
    b = book(whole())
    code, out = run("us_check.py", b, "1")
    notes = [l for l in out if "words per section:" in l]
    check(len(notes) == 1 and notes[0].startswith("NOTE") and " · 1.2 " in notes[0] and "1.3 12 (" in notes[0]
          and "hidden answers are counted" in notes[0], out)
    code, out = run("us_check.py", b)
    check(not any("words per section:" in l for l in out), "only for one chapter: %s" % out)


@test
def practice_needs_three_answered_tasks():
    secs = whole()
    secs[1][2] = practice("1.3", tasks=2)
    code, out = run("us_check.py", book(secs))
    check(code == 1 and any(l.startswith("ERROR") and "1.3 is practice with 2 answered tasks; give at least three "
                            "that climb" in l for l in out), out)
    secs[1][2] = practice("1.3", tasks=3)
    code, out = run("us_check.py", book(secs))
    check(not any("answered tasks" in l for l in out), out)


@test
def a_pattern_is_no_new_word():
    session = ("```console\n$ grep -E \"^(Name|Pid|PPid):\" /proc/self/status | head -n 3\n```\n\n"
               "Then try `grep -E \"(a|b)\" notes.txt` and `[0-9]+`.")
    code, out = run("us_check.py", book(whole(session)), "1")
    new = [l.split("`")[1] for l in out if "first appears here" in l]
    check(not any(re.search(r"Pid|Name|\(|\[|\"", w) for w in new) and "head" in new, new)


@test
def too_many_new_terms_in_one_section_is_flagged():
    flood = "<!-- teaches: alpha = alpha, one, two, three, four, five, six, seven, eight -->"
    secs = whole()
    secs[1][0] = secs[1][0].replace("<!-- teaches: alpha = alpha -->", flood)
    code, out = run("us_check.py", book(secs), "1")
    check(any(l.startswith("FLAG") and "1.1 names 9 new terms" in l for l in out), out)
    code, out = run("us_check.py", book(whole()), "1")
    check(not any("new terms" in l for l in out), out)


@test
def a_named_later_section_is_a_promise():
    early = "Here **beta** is used early, as sections 1.3 and 1.2 show."
    code, out = run("us_check.py", book(whole(early)), "1")
    check(not any("is used here but taught in 1.2" in l for l in out), out)
    code, out = run("us_check.py", book(whole("Here **beta** is used early.")), "1")
    check(any("is used here but taught in 1.2" in l and "plain words" in l for l in out), out)


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
