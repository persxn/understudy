"""Tests for us_check.py, us_index.py, us_find.py and us_init.py: python3 tests/tools/run.py [-v]

-v also prints the real-book report (counts, timings, top messages, suspects of chapter 8).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
FIXTURE = os.path.join(ROOT, "tests", "book", "fixture")
REAL = os.path.dirname(os.environ.get("JOJO_CHAPTERS", "").rstrip("/"))  # optional: the C book; unset skips real_book
TMP = tempfile.mkdtemp(prefix="us-tools-test-")
os.chmod(TMP, 0o755)          # programs run as an ordinary user must reach their working folder
os.environ["TMPDIR"] = tempfile.tempdir = TMP  # run folders go in TMP too, and leave with it
PRIVATE = os.path.join(TMP, "private")
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=PRIVATE)
TESTS, REPORT = [], []


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def run(script, *args, env=None, scripts=SCRIPTS):
    """Run a script; returns (exit code, output lines)."""
    proc = subprocess.run([sys.executable, os.path.join(scripts, script)] + list(args),
                          capture_output=True, text=True, env=env or ENV)
    return proc.returncode, [l for l in (proc.stdout + proc.stderr).splitlines() if not l.startswith("warning: running as root")]


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ---------------------------------------------------------------- fixture book


PREPARED = os.path.join(TMP, "prepared", "fx")


def prepare():
    """The fixture with chapter 1's output pasted and chapter 2 appended section by section."""
    shutil.copytree(FIXTURE, PREPARED)
    shutil.rmtree(os.path.join(PREPARED, "sections"))
    code, out = run("us_run.py", os.path.join(PREPARED, "chapters", "01-first-steps.md"))
    check(code == 0, out)
    for n in ("2.1", "2.2", "2.3"):
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_section.py"), "append", PREPARED, "2"],
                              input=read(os.path.join(FIXTURE, "sections", n + ".md")), capture_output=True, text=True, env=ENV)
        check(proc.returncode == 0, proc.stdout + proc.stderr)


COUNTER = [0]


def book(edit=None):
    """A fresh copy of the prepared fixture in its own book root; edit(book) changes it."""
    COUNTER[0] += 1
    path = os.path.join(TMP, "b%d" % COUNTER[0], "fx")
    shutil.copytree(PREPARED, path)
    if edit:
        edit(path)
    return path


def ch(path, n):
    return os.path.join(path, "chapters", {1: "01-first-steps.md", 2: "02-choices.md"}[n])


def replace(path, n, old, new, count=1):
    """Edit chapter n of a book: old -> new (must exist)."""
    text = read(ch(path, n))
    check(old in text, "fixture has no %r" % old)
    write(ch(path, n), text.replace(old, new, count))


def last(out):
    return out[-1] if out else ""

# ---------------------------------------------------------------- check


@test
def check_fixture_passes():
    code, out = run("us_check.py", book())
    out = [l for l in out if "a lesson needs 1,300 or more" not in l]      # the fixture's lessons are short
    check(code == 0 and re.match(r"check ok: 2 chapters, 7 sections, 0 errors, \d+ flags, \d+ notes$", last(out)), out)
    check(not any(l.startswith(("ERROR", "FLAG")) for l in out), out)


@test
def check_one_chapter():
    code, out = run("us_check.py", book(), "2")
    check(code == 0 and last(out).startswith("check ok: 1 chapter, 3 sections, 0 errors"), out)
    code, out = run("us_check.py", book(), "5")
    check(code == 1 and any("chapter 5 is not written" in l for l in out), out)


BROKEN = [
    ("plan error", lambda b: write(os.path.join(b, "PLAN.md"), read(os.path.join(b, "PLAN.md")).replace("| level: 2\n", "| level: two\n", 1)),
     "ERROR", "PLAN.md:10 1.3: level 'two' is not a number"),
    ("unplanned section", lambda b: replace(b, 2, "## 2.3 Practice: choices", "## 2.5 Practice: choices"),
     "ERROR", "2.5 is not in chapter 2 of PLAN.md"),
    ("sections out of order", lambda b: (replace(b, 2, "## 2.1 Comparing", "## 2.9 X"), replace(b, 2, "## 2.2 Making", "## 2.1 Comparing"),
                                         replace(b, 2, "## 2.9 X", "## 2.2 Making")), "ERROR", "out of plan order"),
    ("section missing", lambda b: write(ch(b, 2), read(ch(b, 2))[:read(ch(b, 2)).index("## 2.3")]),
     "ERROR", "STATUS.json says written but 2.3 not written"),
    ("title differs", lambda b: replace(b, 1, "## 1.3 Variables", "## 1.3 Boxes"), "FLAG", "title differs from PLAN.md 'Variables'"),
    ("no hidden answer", lambda b: replace(b, 1, "<details>", "<div>", -1), "ERROR", "1.2 Check yourself has no hidden answer"),
    ("no check yourself", lambda b: replace(b, 1, "**Check yourself**", "**Questions**"), "ERROR", "1.2 has no '**Check yourself**'"),
    ("missing teaches", lambda b: replace(b, 1, "<!-- teaches: assignment = assignment -->\n", ""), "ERROR",
     "no marker for planned idea 'assignment'"),
    ("duplicate idea", lambda b: replace(b, 2, "<!-- teaches: comparison", "<!-- teaches: printf = printf -->\n<!-- teaches: comparison"),
     "ERROR", "idea 'printf' is marked again (first in 1.2"),
    ("unplanned idea", lambda b: replace(b, 1, "<!-- teaches: printf", "<!-- teaches: extra-idea = extra -->\n<!-- teaches: printf"),
     "FLAG", "idea 'extra-idea' is not in PLAN.md"),
    ("bad reference", lambda b: replace(b, 2, "In §1.3", "In §9.9"), "ERROR", "points to 9.9, which the plan does not have"),
    ("bad section word", lambda b: replace(b, 2, "In §1.3", "In section 9.9"), "ERROR", "points to 9.9, which the plan does not have"),
    ("bad chapter word", lambda b: replace(b, 2, "In §1.3", "In chapter 9"), "ERROR", "points to chapter 9, which the plan does not have"),
    ("bad resolves", lambda b: replace(b, 2, "### The idea", "<!-- resolves: 7.7 -->\n### The idea"), "ERROR", "resolves 7.7, which is not a section"),
    ("fence without language", lambda b: replace(b, 1, "Line 4 does the work.", "```\nplain\n```\n\nLine 4 does the work."),
     "ERROR", "fence has no language tag"),
    ("broken link", lambda b: replace(b, 1, "Think of a row", "See [this](missing.md). Think of a row"), "ERROR", "link to missing.md, which does not exist"),
    ("broken image", lambda b: replace(b, 1, "Think of a row", "![a box](fig/none.svg)\n\nThink of a row"), "ERROR", "link to fig/none.svg"),
    ("broken anchor", lambda b: replace(b, 1, "Think of a row", "See [it](#no-such-heading). Think of a row"), "ERROR", "link to #no-such-heading"),
    ("stale output", lambda b: replace(b, 1, "```text\n1\n```", "```text\n2\n```"), "ERROR", "id=1-2-demo pasted output differs from a fresh run"),
    ("figure fails", lambda b: write(os.path.join(b, "chapters", "fig", "02-choices", "choice-flow.svg"),
                                      read(os.path.join(b, "chapters", "fig", "02-choices", "choice-flow.svg")).replace("<text", "<txt", 1)),
     "ERROR", "figure: not well-formed XML"),
    ("figure without image line", lambda b: write(ch(b, 2), re.sub(r"\n!\[[^\n]*\]\(fig/[^\n]*\)\n", "\n", read(ch(b, 2)))),
     "ERROR", "figure 'choice-flow' has no image line below it; run python3 scripts/us_draw.py --chapter /"),
    ("used before taught", lambda b: replace(b, 1, "Think of a row of labelled boxes", "A `variable` is coming. A **variable** again. Think of a row of labelled boxes"),
     "FLAG", "chapters/01-first-steps.md:18 (1.2) 'variable' is used here but taught in 1.3; say it in plain words here instead, or, only if the reader must look ahead, add (§1.3) after the sentence"),
    ("used before taught across chapters", lambda b: replace(b, 1, "Think of a row of labelled boxes", "An else branch is near. Think of a row of labelled boxes"),
     "FLAG", "(1.2) 'else branch' is used here but taught in 2.2"),
    ("personal file", lambda b: write(os.path.join(b, "now.md"), "x\n"), "ERROR", "now.md personal record inside the book"),
    ("sentence repeated", lambda b: write(ch(b, 1), re.sub(r"^(## 1\.\d .*\n)", r"\1\nThe same sentence is said in every section.\n",
                                                          read(ch(b, 1)), flags=re.M)),
     "FLAG", "chapters/01-first-steps.md:5 'The same sentence is said in every section.' is written word for word in 4 sections "
     "(1.1, 1.2, 1.3, 1.4)"),
    ("posix unsaid", lambda b: replace(b, 1, "#include <stdio.h>\n", "#include <stdio.h>\n#include <unistd.h>\n"), "FLAG",
     "chapters/01-first-steps.md:32 id=1-2-demo includes a POSIX header: say that this is POSIX, not standard C"),
    ("long program", lambda b: replace(b, 1, "    int x = 1;\n", "".join("    // step %d\n" % k for k in range(60)) + "    int x = 1;\n"),
     "NOTE", "id=1-2-demo: 67 lines with no build-up: grow it from a shorter program the reader has seen"),
]


def make_broken_test(name, edit, level, want):
    """A test: one broken copy gives the line wanted, at the level wanted, with the right exit code."""
    def fn():
        code, out = run("us_check.py", book(edit))
        hits = [l for l in out if l.startswith(level + " ") and want in l]
        check(hits, "expected %s %r in:\n%s" % (level, want, "\n".join(out[-12:])))
        check(code == (1 if level == "ERROR" else 0), "exit %d" % code)
        check(last(out).startswith("check failed" if level == "ERROR" else "check ok"), last(out))
    fn.__name__ = "check_finds_" + name.replace(" ", "_")
    return fn


for _case in BROKEN:
    test(make_broken_test(*_case))


@test
def check_used_before_taught_every_use_and_exemptions():
    b = book(lambda b: replace(b, 1, "Think of a row of labelled boxes",
                               "A `variable` here.\n\nThink of a row of labelled boxes, a **variable** each, a variable in plain words"))
    code, out = run("us_check.py", b)
    hits = [l for l in out if "'variable' is used here" in l]
    check(len(hits) == 1 and ":20 " in hits[0], "once a section, never in inline code: %s" % hits)
    replace(b, 1, ", a **variable** each", "")
    code, out = run("us_check.py", b)
    hits = [l for l in out if "'variable' is used here" in l]
    check(not hits, "an everyday word in plain prose or inline code is not flagged: %s" % hits)
    replace(b, 1, "a variable in plain words", "a **variable** each")
    replace(b, 1, "A `variable` here.", "A `variable` here (§1.3).")
    code, out = run("us_check.py", b)
    hits = [l for l in out if "'variable' is used here" in l]
    check(len(hits) == 1 and ":20 " in hits[0], "promise on the line exempts that use only: %s" % hits)
    plan = os.path.join(b, "PLAN.md")
    write(plan, read(plan).replace("run: c\n", "run: c\neveryday: variable, variables\n"))
    code, out = run("us_check.py", b)
    check(code == 0 and not any("'variable'" in l for l in out), out)


@test
def check_new_words_and_show():
    def edit(b):
        replace(b, 1, "Line 4 does the work.", "Line 4 does the work. Try `-Wall`. Then `rm -f`. See `0644`.")
        replace(b, 2, "In §1.3", "Use `-Wall`. See `/dev/null`. In §1.3")
    b = book(edit)
    code, out = run("us_check.py", b)
    new = [l for l in out if "first appears here" in l]
    check(new == ["FLAG chapters/01-first-steps.md:46 (1.2) `%s` first appears here: explain it where it appears, or remove it" % w
                  for w in ("-Wall", "-f", "0644")] + [l for l in new if "/dev/null" in l] and len(new) == 4 and
          "(2.1) `/dev/null`" in new[-1], new)
    code, out = run("us_check.py", book(lambda b: replace(b, 2, "In §1.3", " ".join("Try `-o%d`." % k for k in range(15)) + " In §1.3")), "2")
    check(len([l for l in out if "first appears here" in l]) == 12, out)
    code, out = run("us_check.py", b, "1", "--show", "1-2-demo")
    check(out[:4] == ["32       <!-- code: id=1-2-demo -->", "33       ```c", "34    1  #include <stdio.h>", "35    2"]
          and "40    7  }" in out and out[-1] == "44       ```", out)


@test
def check_new_words_explained_or_the_subject():
    session = ("Line 4 does the work.\n\n```console\n$ zork --frob x\n$ zork --frob y\n$ tar -xzf a.tgz\n```\n\n"
               "The option `-xzf` tells tar to unpack the archive here.")
    code, out = run("us_check.py", book(lambda b: replace(b, 1, "Line 4 does the work.", session)), "1")
    new = [l.split("`")[1] for l in out if "first appears here" in l]
    check(new == ["--frob", "tar"], "only what no long sentence explains, never the book's own command (zork): %s" % new)
    table = "\n\n| Step | What happens to the file |\n| --- | --- | --- | --- | --- | --- |\n| 1 | made |\n\n### The code"
    code, out = run("us_check.py", book(lambda b: [replace(b, n, "### The code", table, 2) for n in (1, 2)]))
    check(not any("written word for word" in l for l in out), "a table row is no repeated sentence: %s" % out)


@test
def prose_pages_of_150_and_sessions_folded():
    session = ("Line 4 does the work.\n\n<!-- code: id=hello-session -->\n```console\n$ printf 'one\\n\\ntwo\\nthree\\n'\n"
               "$ true\n```\n\n" + "\n\n".join("Filler line %d." % k for k in range(200)))
    b = book(lambda b: replace(b, 1, "Line 4 does the work.", session))
    check(run("us_run.py", ch(b, 1))[0] == 0, "session ran")
    code, out = run("us_check.py", b, "1", "--prose")
    check(len(out) == 151 and out[-1].startswith("next: --from "), "a page is 150 lines: %d, %s" % (len(out), out[-1]))
    fold = [l for l in out if "hello-session" in l]
    check(fold and fold[0].endswith("[session id=hello-session: $ printf 'one\\n\\ntwo\\nthree\\n' ; $ true; "
                                    "output 4 lines: \"one\" / \"two\"]"), fold)


@test
def prose_here_document_is_typed_not_output():
    session = ("Line 4 does the work.\n\n<!-- code: id=note-session -->\n```console\n$ cat > note.txt <<'EOF'\n"
               "first line\n> quoted\nEOF\n$ wc -l < note.txt\n```\n")
    b = book(lambda b: replace(b, 1, "Line 4 does the work.", session))
    check(run("us_run.py", ch(b, 1))[0] == 0, "session ran")
    fold = [l for l in run("us_check.py", b, "1", "--prose")[1] if "note-session" in l]
    check(fold and fold[0].endswith("[session id=note-session: $ cat > note.txt <<'EOF' … ; $ wc -l < note.txt; "
                                    "output 1 line: \"2\"]"), fold)


@test
def check_simplified_note_and_resolves():
    box = "> **Simplified here.** A box can hold more; §2.2 gives the fuller truth.\n\n### The code"
    b = book(lambda b: replace(b, 1, "### The code", box))
    code, out = run("us_check.py", b)
    notes = [l for l in out if "'Simplified here' is not repaid" in l]
    check(code == 0 and len(notes) == 1 and out[-2] == notes[0] and "resolves: 1.2" in notes[0], out)
    replace(b, 2, "### The idea", "<!-- resolves: 1.2 -->\n### The idea")
    code, out = run("us_check.py", b)
    check(not any("Simplified" in l for l in out), out)


@test
def check_forward_reference_is_a_note():
    code, out = run("us_check.py", book(lambda b: replace(b, 1, "Think of a row", "§2.2 comes later. Think of a row")))
    check(code == 0 and any(l.startswith("NOTE") and "1.2 refers forward to §2.2" in l for l in out), out)


SESSION = """Line 4 does the work.

```console
$ git status
  (use "git frob --hard <file>..." to discard changes)
$ git status
  (use "git frob --hard <file>..." to discard changes)
$ git log
$ sed -i 's/a/b/' f.txt
$ sed -i 's/b/c/' f.txt
$ echo -e 'x'
$ git mv README.md readme.md
$ python3 hello.py
```
"""


@test
def check_portable_commands_and_what_the_screen_suggests():
    code, out = run("us_check.py", book(lambda b: replace(b, 1, "Line 4 does the work.", SESSION)), "1")
    mine = [l for l in out if "differ" in l or "Windows" in l or "screen suggests" in l]
    check(mine == [
        "FLAG chapters/01-first-steps.md:54 `sed -i` (2 times): GNU and macOS sed differ on -i: write the file again "
        "with printf or a here-document",
        "FLAG chapters/01-first-steps.md:56 `echo -e`: echo -e differs between shells: use printf",
        "FLAG chapters/01-first-steps.md:57 `mv README.md readme.md`: the two names differ only in letter case: on "
        "macOS and Windows nothing is seen to change; rename through a third name",
        "FLAG chapters/01-first-steps.md:50 the screen suggests `git frob --hard` (2 times) and the book never explains "
        "it: teach it or point to the section that will",
        "NOTE chapters/01-first-steps.md:58 `python3`: on Windows this is `python` or `py`: say so once"], mine)

    def edit(b):
        replace(b, 1, "Line 4 does the work.", SESSION + "\n`git frob --hard` throws an edit away (§1.3).\n")
        write(os.path.join(b, "PLAN.md"), read(os.path.join(b, "PLAN.md")).replace("never programmed", "never programmed, on Linux"))
    code, out = run("us_check.py", book(edit), "1")
    check(not any("screen suggests `git frob" in l or "`python3`:" in l for l in out),
          "explained in prose, and a Linux book: %s" % out)


@test
def check_recall_questions_and_many_forward_references():
    def edit(b):
        replace(b, 1, "1. What happens in step 1 of the trace?", "1. What is a string literal?")
        replace(b, 1, "2. What happens in step 2 of the trace?", "2. Which command prints a line?")
        replace(b, 1, "Think of a row", "§1.3, §1.4 and §2.1 come later. Think of a row")
    code, out = run("us_check.py", book(edit), "1")
    check(any(l.startswith("NOTE chapters/01-first-steps.md:73 1.2 Check yourself: 2 questions only ask to recall "
                           "(1, 2)") for l in out), out)
    check(any(l.startswith("NOTE") and "1.2 refers forward to §1.3, §1.4, §2.1; more than two forward references" in l
              for l in out), out)
    code, out = run("us_check.py", book(lambda b: [edit(b), replace(b, 1, "Which command prints a line?",
                                                                       "Which command prints `hi`?")]), "1")
    check(not any("only ask to recall" in l for l in out), "a question with code in it is not pure recall: %s" % out)


@test
def check_inside_a_longer_term_is_no_early_use():
    def edit(b):
        replace(b, 1, "<!-- teaches: printf = printf -->", "<!-- teaches: printf = printf, printf variable -->")
        replace(b, 1, "Line 4 does the work.", "Line 4 does the work. A `printf variable` here.")
    code, out = run("us_check.py", book(edit))
    check(not any("'variable' is used here" in l for l in out), out)
    code, out = run("us_check.py", book(lambda b: [edit(b), replace(b, 1, "A `printf variable` here.",
                                                                       "A `printf variable` and a **variable** here.")]))
    check(len([l for l in out if "'variable' is used here" in l]) == 1, out)


@test
def check_no_book_and_tokens():
    code, out = run("us_check.py", "--tokens")
    check(out[0].startswith("skills: ") and "Rough token sizes (four characters per token)" in out, out[:3])
    check(any(l.startswith("  on demand: rules/book-standard.md") for l in out), "token table")
    check(re.match(r"check (ok|failed): \d+ chapters?, \d+ sections?, \d+ errors?, \d+ flags?, \d+ notes?$", last(out)), last(out))
    check(code == (1 if last(out).startswith("check failed") else 0), code)


@test
def tokens_fail_on_a_broken_limit():
    home = product()
    scripts = os.path.join(home, "scripts")
    code, out = run("us_check.py", "--tokens", scripts=scripts)
    check(code == 0 and not any(l.startswith("ERROR") for l in out), out)
    skill = os.path.join(home, ".claude", "skills", "us-start", "SKILL.md")
    body = int(next(l.split()[-1] for l in out if l.startswith("  on use: us-start ")))
    write(skill, read(skill) + "x" * 4 * (1000 - body))
    code, out = run("us_check.py", "--tokens", scripts=scripts)
    check(code == 1 and "ERROR skill us-start: body is 1000 tokens; keep it under 1000" in out, out[-3:])
    write(skill, read(skill)[:-4])
    always = int(re.search(r"= (\d+)$", next(l for l in run("us_check.py", "--tokens", scripts=scripts)[1] if "always loaded" in l)).group(1))
    prompt = os.path.join(home, "AGENTS.md")
    write(prompt, read(prompt) + "x" * 4 * (2000 - always))
    code, out = run("us_check.py", "--tokens", scripts=scripts)
    check(code == 0, "2,000 exactly is allowed: %s" % out[-2:])
    write(prompt, read(prompt) + "xxxx")
    code, out = run("us_check.py", "--tokens", scripts=scripts)
    check(code == 1 and "ERROR always-loaded text is 2001 tokens; keep it at or under 2000" in out, out[-3:])


@test
def check_rejects_bad_usage():
    check(run("us_check.py", book(), "x")[0] == 2, "chapter must be a number")
    check(run("us_check.py", "--bogus")[0] == 2, "unknown option")
    check(run("us_check.py", book(), "--suspects")[0] == 2, "suspects needs N")

# ---------------------------------------------------------------- suspects


CRAFTED = ("A `variable` always holds exactly one value, and it never forgets. "
           "It takes 37 steps to finish. An int takes 4 bytes. §2.2 shows more.\n\n### The code")


def crafted():
    return book(lambda b: replace(b, 1, "### The code", CRAFTED, 2))


CLEARING = "clear each line shown: true as written, or scoped to this system or machine, or fixed."


def suspects(b, n):
    """us_check.py --suspects, its closing line checked and dropped."""
    code, out = run("us_check.py", b, n, "--suspects")
    m = re.search(r"(\d+) lines(?: \((\d+) shown\))?;", out[-2]) if len(out) > 1 else None
    unshown = int(m.group(1)) - int(m.group(2)) if m and m.group(2) else 0
    want = CLEARING + (" The %d not shown rank lower: sample them only if time allows." % unshown if unshown else "")
    check(out[-1] == want or last(out).endswith(": none"), out[-2:])
    return code, out[:-1] if out[-1] == want else out


@test
def suspects_find_every_kind():
    code, out = suspects(crafted(), "1")
    check(code == 0, out)
    kinds = Counter(k for l in out[:-1] for k in l.split()[1].split("+"))
    for kind in ("sweeping", "number", "trace", "answer", "forward", "machine"):
        check(kinds[kind] > 0, "no %s in:\n%s" % (kind, "\n".join(out)))
    check(all(len(l.split(" ", 2)[2].split()) <= 12 for l in out[:-1] if l.split()[1] not in ("trace", "ref")), "excerpt over 12 words")
    trace = [l for l in out[:-1] if " trace " in l]
    check(len(trace) == 2 and all(re.search(r"lines \d+-\d+", l) for l in trace), trace)
    summary = last(out)
    check(summary.startswith("suspects fx ch 1:") and all(k in summary for k in ("answer", "ref", "trace", "number", "machine", "sweeping", "forward")), summary)
    crafted_lines = [l for l in out[:-1] if "forward" in l.split()[1]]
    check(len(crafted_lines) == 2 and all(set(l.split()[1].split("+")) == {"forward", "sweeping", "number", "machine"}
                                          for l in crafted_lines), crafted_lines)


@test
def suspects_cap_and_order():
    many = "\n\n".join("Rule %d: this always works, and never fails." % i for i in range(120))
    b = book(lambda b: replace(b, 1, "### The code", many + "\n\n### The code", 1))
    code, out = suspects(b, "1")
    check(len(out) <= 39 and re.search(r"\(\d+ shown\)", last(out)), "%d lines, %s" % (len(out), last(out)))
    kinds = Counter(min(l.split()[1].split("+"), key=["answer", "ref", "trace", "number", "machine", "sweeping", "forward"].index)
                    for l in out[:-1])
    check(kinds["number"] <= 14 and kinds["sweeping"] <= 6, kinds)
    order = ["answer", "ref", "trace", "number", "machine", "sweeping", "forward"]
    ranks = [min(order.index(k) for k in l.split()[1].split("+")) for l in out[:-1]]
    check(ranks == sorted(ranks), "not most suspicious first: %s" % ranks)
    check(out[0].split()[1].startswith("answer"), out[0])


@test
def suspects_skip_scene_answers_and_script_traces():
    def edit(b):
        replace(b, 1, "### The code", "This always works for `x`, and never fails.\n\n### The code", 1)
        replace(b, 1, "### The picture\n", "### The picture\n\nIt always takes `x` and every 4 bytes.\n", 1)
    code, out = suspects(book(edit), "1")
    sweeping = [l for l in out[:-1] if "sweeping" in l.split()[1]]
    check(any("always works" in l for l in sweeping), out)
    check(not any("always takes" in l for l in sweeping), "sweeping in The picture: %s" % sweeping)
    text = read(ch(book(), 1))
    first = text.index("\n|")
    traced = text[:first + 1] + "<!-- trace: id=x watch=\"y\" at=\"1\" -->\n" + text[first + 1:]
    b = book(lambda b: write(ch(b, 1), traced))
    code, out2 = suspects(b, "1")
    check(len([l for l in out2 if " trace " in l]) == len([l for l in out if " trace " in l]) - 1, (out, out2))


@test
def suspects_ref_to_a_section_that_does_not_teach_the_term():
    edit = lambda b: replace(b, 2, "### The code", "A string literal goes to `printf`, as in §2.1. "
                             "A comparison gives 0 or 1 (§2.1).\n\n### The code", 2)
    code, out = suspects(book(edit), "2")
    refs = [l for l in out if l.split()[1].startswith("ref")]
    check(len(refs) == 1 and refs[0].endswith("as in §2.1; 'string literal' is taught in §1.2"), out)
    check(out.index(refs[0]) == 0 or out[out.index(refs[0]) - 1].split()[1].startswith(("answer", "ref")), out)


@test
def suspects_quiet_chapter():
    code, out = suspects(book(), "2")
    check(code == 0 and len(out) <= 81 and last(out).startswith("suspects fx ch 2"), out)

# ---------------------------------------------------------------- index


def snapshot(root):
    """{path: (bytes, mtime)} of every file under root."""
    out = {}
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            p = os.path.join(folder, f)
            with open(p, "rb") as h:
                out[p] = (h.read(), os.path.getmtime(p))
    return out


def validate_manifest(m):
    """Raise if manifest.json is not schema 3 as specified."""
    def need(obj, keys, where):
        check(isinstance(obj, dict) and all(k in obj for k in keys), "%s lacks %s" % (where, [k for k in keys if k not in obj]))
    need(m, ["schema", "books", "edges", "chapter_edges"], "manifest")
    check(m["schema"] == 3, "schema")
    ids = set()
    for b in m["books"]:
        need(b, ["name", "title", "for", "parts"], "book")
        for p in b["parts"]:
            need(p, ["title", "chapters"], "part")
            for c in p["chapters"]:
                need(c, ["n", "title", "file", "state", "words", "sections"], "chapter")
                check(isinstance(c["n"], int) and c["state"] in ("planned", "writing", "written", "reviewed"), c["state"])
                check(c["file"] is None or c["file"].startswith(b["name"] + "/chapters/"), c["file"])
                for s in c["sections"]:
                    need(s, ["id", "title", "kind", "level", "state", "words", "teaches", "anchor"], "section")
                    check(re.match(r"^\d+\.\d+$", s["id"]) and s["state"] in ("planned", "written"), s)
                    check(s["kind"] in ("lesson", "story", "practice") and isinstance(s["level"], int), s)
                    check(isinstance(s["teaches"], list) and re.match(r"^[\w-]+$", s["anchor"]), s)
                    ids.add("%s:%s" % (b["name"], s["id"]))
    for e in m["edges"]:
        need(e, ["from", "to", "idea"], "edge")
        check(e["from"] in ids and e["to"] in ids, e)
    for e in m["chapter_edges"]:
        need(e, ["from", "to", "ideas"], "chapter edge")


@test
def index_fixture():
    b = book()
    code, out = run("us_index.py", b)
    check(code == 0 and out == ["indexed 1 book: 2 chapters, 7 sections, 7 terms, 2 edges"], out)
    text = read(ch(b, 2))
    check(text.startswith("# Chapter 2: Choices\n\n<!-- contents -->\n- [2.1 Comparing values](#21-comparing-values)\n"), text[:200])
    check("- [2.3 Practice: choices](#23-practice-choices)\n<!-- /contents -->\n\n## 2.1 Comparing values" in text, "block end")
    root = os.path.dirname(b)
    m = json.load(open(os.path.join(root, "manifest.json")))
    validate_manifest(m)
    check(m["edges"] == [{"from": "fx:2.1", "to": "fx:1.3", "idea": "variable"}, {"from": "fx:2.2", "to": "fx:1.2", "idea": "printf"}], m["edges"])
    check(m["chapter_edges"] == [{"from": "fx:2", "to": "fx:1", "ideas": 2}], m["chapter_edges"])
    chapters = m["books"][0]["parts"][0]["chapters"]
    check([c["state"] for c in chapters] == ["written", "written"] and chapters[0]["sections"][1]["teaches"] == ["printf", "string-literal"], chapters[0])
    s = json.load(open(os.path.join(root, "search.json")))
    check(s["schema"] == 3 and len(s["sections"]) == 7, "search size")
    one = next(x for x in s["sections"] if x["id"] == "1.3")
    check(one["terms"][:2] == ["variable", "variables"] and one["idea"].startswith("A variable is a named box") and len(one["idea"].split()) == 40, one)
    for name in ("README.md", "KEYTERMS.md", "INDEX.md"):
        check(os.path.exists(os.path.join(b, name)), name)
    check("[1 First steps](chapters/01-first-steps.md) · written · 4 of 4 sections" in read(os.path.join(b, "README.md")), "readme")
    check("- **variable** ([§1.3](chapters/01-first-steps.md#13-variables)): A variable is a named box in memory that holds one value." in read(os.path.join(b, "KEYTERMS.md")), "keyterms")
    check("## V\n\n- variable: [1.3](chapters/01-first-steps.md#13-variables)" in read(os.path.join(b, "INDEX.md")), "index")
    code, out = run("us_check.py", b)
    check(code == 0 and not any("index is older" in l or "link to" in l for l in out), out)


@test
def index_agrees_with_plan_check():
    b = book()
    plan = os.path.join(b, "PLAN.md")
    write(plan, read(plan).replace("run: c\n", "run: c\nenv: GIT_AUTHOR_DATE=2026-01-05T10:00:00\neveryday: box\n"))
    code, out = run("us_plan.py", "check", b)
    check(code == 0, out)
    code, out = run("us_index.py", b)
    check(code == 0 and not any("has problems" in l for l in out), out)
    write(plan, read(plan).replace("1.3   Variables", "1.5 Variables"))
    check(run("us_plan.py", "check", b)[0] == 1 and any("has problems" in l for l in run("us_index.py", b)[1]), "a real error")


@test
def index_is_idempotent():
    b = book()
    run("us_index.py", b)
    before = snapshot(os.path.dirname(b))
    time.sleep(0.05)
    code, out = run("us_index.py", b)
    after = snapshot(os.path.dirname(b))
    check(code == 0 and before == after, [p for p in after if before.get(p) != after[p]])


@test
def index_changes_nothing_else_and_replaces_old_contents():
    b = book()
    old = read(ch(b, 1))
    write(ch(b, 1), old.replace("# Chapter 1: First steps\n\n", "# Chapter 1: First steps\n\n**Contents**\n\n- [1.1 Old](#11-old)\n\n", 1))
    run("us_index.py", b)
    new = read(ch(b, 1))
    check("**Contents**" not in new and "(#11-old)" not in new, new[:300])
    start, end = new.index("<!-- contents -->"), new.index("<!-- /contents -->") + len("<!-- /contents -->\n")
    check((new[:start] + new[end:]).replace("\n\n\n", "\n\n", 1) == old, "text outside the block changed")
    write(ch(b, 1), new.replace("- [1.2 Printing a line]", "- [1.2 Stale]"))
    run("us_index.py", b)
    check(read(ch(b, 1)) == new, "stale block not refreshed")


@test
def index_planned_sections_and_append_after_index():
    COUNTER[0] += 1
    b = os.path.join(TMP, "b%d" % COUNTER[0], "fx")
    shutil.copytree(FIXTURE, b)
    shutil.rmtree(os.path.join(b, "sections"))
    code, out = run("us_index.py", b)
    m = json.load(open(os.path.join(os.path.dirname(b), "manifest.json")))
    validate_manifest(m)
    c2 = m["books"][0]["parts"][0]["chapters"][1]
    check(c2["state"] == "planned" and c2["file"] is None and all(s["state"] == "planned" for s in c2["sections"]), c2)
    check(len(m["edges"]) == 2, m["edges"])
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_section.py"), "append", b, "2"],
                          input=read(os.path.join(FIXTURE, "sections", "2.1.md")), capture_output=True, text=True, env=ENV)
    check(proc.returncode == 0, proc.stdout + proc.stderr)
    run("us_index.py", b)
    c2 = json.load(open(os.path.join(os.path.dirname(b), "manifest.json")))["books"][0]["parts"][0]["chapters"][1]
    check(c2["state"] == "writing" and [s["state"] for s in c2["sections"]] == ["written", "planned", "planned"], c2)
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_section.py"), "append", b, "2"],
                          input=read(os.path.join(FIXTURE, "sections", "2.2.md")), capture_output=True, text=True, env=ENV)
    check(proc.returncode == 0, "append after a contents block: " + proc.stdout + proc.stderr)


@test
def index_never_leaks_private():
    secret = "PRIVATE-SECRET-4711"
    write(os.path.join(PRIVATE, "now.md"), secret + "\n")
    write(os.path.join(PRIVATE, "scratch", "rejected-1.2.md"), "## 1.2 " + secret + "\n")
    b = book()
    run("us_index.py", b)
    for path, (data, _) in snapshot(os.path.dirname(b)).items():
        check(secret.encode() not in data, "private text in " + path)
    env = dict(ENV, UNDERSTUDY_PRIVATE=os.path.join(os.path.dirname(b), "private"))
    code, out = run("us_index.py", b, env=env)
    check(code == 1 and "overlap" in last(out), out)

# ---------------------------------------------------------------- find


def indexed():
    b = book()
    run("us_index.py", b)
    return b


@test
def find_term_title_prose():
    b = indexed()
    code, out = run("us_find.py", "string", "literal", "--book", b)
    check(code == 0 and out[0].startswith("fx 1.2 Printing a line  chapters/01-first-steps.md:") and out[0].endswith("(taught: string literal)"), out)
    check(len(out) <= 5, out)
    code, out = run("us_find.py", "comparing values", "--book", b)
    check(out[0].startswith("fx 2.1 Comparing values") and out[0].endswith("(title)"), out)
    code, out = run("us_find.py", "shelf", "--book", b)
    check(code == 0 and "(prose: " in out[0] and len(out) <= 5, out)
    code, out = run("us_find.py", "zebra", "--book", b)
    check(code == 1 and out == ["nothing matches 'zebra'"], out)
    m = re.search(r":(\d+)-(\d+)", run("us_find.py", "string literal", "--book", b)[1][0])
    lines = read(ch(b, 1)).splitlines()
    check(lines[int(m.group(1)) - 1].startswith("## 1.2"), "line range start")


@test
def find_read_cap():
    b = book(lambda b: replace(b, 1, "### The code", "### The code\n\n" + "\n".join("Filler line %d." % i for i in range(150)), 2))
    run("us_index.py", b)
    code, out = run("us_find.py", "variable", "--book", b, "--read")
    check(code == 0 and out[1] == "## 1.3 Variables", out[:2])
    check(len(out) == 122, "%d lines: %s" % (len(out), out[-3:]))
    check(out[-1].startswith("[cut: lines ") and "still to come: The trace, What goes wrong, Remember" in out[-1], out[-1])
    code, out = run("us_find.py", "comparing values", "--book", b, "--read")
    check(out[1] == "## 2.1 Comparing values" and not out[-1].startswith("[cut") and len(out) < 122, out[-1])


def product(book_root=None):
    """A copy of the product (scripts, skills, prompt, rules) in TMP; book_root goes in its understudy.yaml."""
    COUNTER[0] += 1
    home = os.path.join(TMP, "product%d" % COUNTER[0])
    shutil.copytree(SCRIPTS, os.path.join(home, "scripts"), ignore=shutil.ignore_patterns("__pycache__"))
    for name in (".claude", "rules"):
        shutil.copytree(os.path.join(ROOT, name), os.path.join(home, name))
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        shutil.copy(os.path.join(ROOT, name), home)
    write(os.path.join(home, "understudy.yaml"), "book: %s\n" % (book_root or "book"))
    return home


@test
def find_section_by_number():
    b = indexed()
    lines = read(ch(b, 1)).splitlines()
    for args in ((b, "1.3"), ("§1.3", "--book", b)):
        code, out = run("us_find.py", *args)
        m = re.fullmatch(r"fx 1\.3 Variables  chapters/01-first-steps\.md:(\d+)-(\d+)", out[0] if out else "")
        check(code == 0 and len(out) == 1 and m and lines[int(m.group(1)) - 1] == "## 1.3 Variables", out)
    code, out = run("us_find.py", b, "1.3", "--read")
    check(code == 0 and out[1] == "## 1.3 Variables", out[:2])
    check(run("us_find.py", b, "9.9") == (1, ["no section 9.9"]), "a missing number")
    root = os.path.join(TMP, "shelf")
    for name in ("fx", "fy"):
        shutil.copytree(PREPARED, os.path.join(root, name))
    home = product(root)
    check(run("us_index.py", scripts=os.path.join(home, "scripts"))[0] == 0, "index two books")
    code, out = run("us_find.py", "2.1", scripts=os.path.join(home, "scripts"))
    check(code == 0 and [l.split()[0] for l in out] == ["fx", "fy"] and all(" 2.1 Comparing values  chapters/02-" in l for l in out), out)
    code, out = run("us_find.py", "fy", "2.1", scripts=os.path.join(home, "scripts"))
    check(code == 0 and len(out) == 1 and out[0].startswith("fy 2.1 Comparing values  chapters/02-choices.md:"), out)
    code, out = run("us_find.py", "2.1", "--read", scripts=os.path.join(home, "scripts"))
    check(code == 2 and "several books have §2.1: name one, us_find.py BOOK 2.1 --read" in out[-1], out)
    code, out = run("us_find.py", "comparing", "2.1", scripts=os.path.join(home, "scripts"))
    check(code == 0 and "(" in out[0], "words that are not a book: an ordinary search: %s" % out)

# ---------------------------------------------------------------- init


@test
def init_creates_root_repo_and_private():
    home = os.path.join(TMP, "product")
    os.makedirs(os.path.join(home, "reader"))
    shutil.copytree(SCRIPTS, os.path.join(home, "scripts"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(os.path.join(ROOT, "understudy.yaml"), home)
    write(os.path.join(home, "reader", "index.html"), "<!DOCTYPE html><title>reader</title>\n")
    env = {k: v for k, v in ENV.items() if k != "UNDERSTUDY_PRIVATE"}
    code, out = run("us_init.py", env=env, scripts=os.path.join(home, "scripts"))
    check(code == 0, out)
    root = os.path.join(home, "book")
    for p in (".nojekyll", "index.html", ".git"):
        check(os.path.exists(os.path.join(root, p)), "missing book/" + p + ": " + " | ".join(out))
    check(os.path.exists(os.path.join(home, "private", "now.md")), "now.md")
    check(not any(os.path.exists(os.path.join(root, d)) for d in ("archive", "library", "projects", "routes")), "old tree")
    check(sorted(os.listdir(root)) == [".git", ".nojekyll", "index.html"], os.listdir(root))
    write(os.path.join(home, "private", "now.md"), "kept\n")
    code, out = run("us_init.py", env=env, scripts=os.path.join(home, "scripts"))
    check(code == 0 and read(os.path.join(home, "private", "now.md")) == "kept\n" and not any(l.startswith("created") for l in out), out)

# ---------------------------------------------------------------- real book


def timed(*args):
    start = time.time()
    code, out = run(*args)
    return code, out, time.time() - start


def real_book():
    check(os.path.isdir(REAL), "no real book at " + REAL)
    b = os.path.join(TMP, "real", "jojoway")
    shutil.copytree(os.path.join(REAL, "chapters"), os.path.join(b, "chapters"))
    if os.path.isdir(os.path.join(REAL, "diagrams")):
        shutil.copytree(os.path.join(REAL, "diagrams"), os.path.join(b, "diagrams"))
    code, out = run("us_plan.py", "from-chapters", b, "--title", "Learn C the Jojo way", "--for", "someone who has never programmed")
    check(code == 0, out)
    code, out, secs = timed("us_index.py", b)
    REPORT.append("index: %s  (%.2fs)" % (last(out), secs))
    check(code == 0 and last(out).startswith("indexed 1 book: 11 chapters, 145 sections, 493 terms, "), out)
    validate_manifest(json.load(open(os.path.join(os.path.dirname(b), "manifest.json"))))
    code, out, secs = timed("us_check.py", b, "8")
    REPORT.append("check 8: %s  (%.1fs)" % (last(out), secs))
    check(re.match(r"check (ok|failed): 1 chapter, 12 sections, ", last(out)), last(out))
    code, out, secs = timed("us_check.py", b)
    REPORT.append("check all: %s  (%.1fs)" % (last(out), secs))
    check(re.match(r"check (ok|failed): 11 chapters, 145 sections, ", last(out)), last(out))
    shapes = Counter(re.sub(r"'[^']*'", "'X'", re.sub(r"\d+", "N", re.sub(r"^(\w+) \S+ ", r"\1 ", re.sub(r"id=\S+|link to \S+|§[\d.]+(, §[\d.]+)*", "X", l))))
                     for l in out[:-1])
    REPORT.append("most common:\n" + "\n".join("  %4d  %s" % (n, s[:150]) for s, n in shapes.most_common(5)))
    code, out, secs = timed("us_check.py", b, "8", "--suspects")
    check(code == 0 and len(out) <= 81, len(out))
    REPORT.append("suspects 8: %s  (%.1fs)\nfirst 15:\n%s" % (last(out), secs, "\n".join("  " + l for l in out[:15])))
    code, out, secs = timed("us_find.py", "dereference", "--book", b)
    REPORT.append("find dereference (%.2fs):\n%s" % (secs, "\n".join("  " + l for l in out)))
    check(code == 0 and out[0].startswith("jojoway 8.3 "), out)
    code, out = run("us_find.py", "dereference", "--book", b, "--read")
    check(len(out) <= 122 and out[-1].startswith("[cut: "), out[-1])


if REAL:
    test(real_book)
else:
    print("skip  real_book: JOJO_CHAPTERS not set")


def main():
    """Run every test; print one line each and a total."""
    passed = failed = 0
    try:
        prepare()
    except Exception as exc:  # noqa: BLE001
        print("FAIL  prepare fixture: %s" % str(exc)[:400])
        shutil.rmtree(TMP, ignore_errors=True)
        return 1
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
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
