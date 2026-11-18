"""End to end: try a section's programs, write the section with bare markers, run it all again.

    python3 tests/book/e2e.py

On a temp copy of the fixture book: try two programs for 2.1 (one shown under itself, one whose
output is the hidden answer of a Check yourself question), append 2.1 with only their marker
lines and one inline figure, check the chapter file, run us_run.py and us_draw.py again and see
nothing change, finish the chapter and mark it reviewed. One line per check, then a total.
"""
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
TMP = tempfile.mkdtemp(prefix="us-e2e-")
os.chmod(TMP, 0o755)  # programs run as an ordinary user when this runs as root
os.environ["TMPDIR"] = tempfile.tempdir = TMP  # run folders go in TMP too, and leave with it
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
RESULTS = []

DEMO = """<!-- code: id=cmp-demo -->
```c
#include <stdio.h>

int main(void) {
    int a = 3, b = 4;
    printf("%d %d\\n", a < b, a == b);
    return 0;
}
```
"""
QUIZ = """<!-- code: id=cmp-quiz -->
```c
#include <stdio.h>

int main(void) {
    printf("%d\\n", 7 > 2);
    return 0;
}
```
"""
FIGURE = """<!-- fig: id=overview
kind: flow
box a: a < b
box r: 1 or 0
a -> r
-->
"""


def run(script, *args, stdin=None):
    """Run scripts/<script>; returns (exit code, stdout and stderr)."""
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args), input=stdin,
                       capture_output=True, text=True, env=ENV)
    return p.returncode, (p.stdout + p.stderr).strip()


def check(name, ok, detail=""):
    """Record and print one check."""
    RESULTS.append(bool(ok))
    print(("pass  " if ok else "FAIL  ") + name + ("" if ok else ": " + str(detail).replace("\n", " | ")[:400]))


def read(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


def section_21():
    """Fixture 2.1 with bare markers for the two tried programs, an inline figure, and a
    Check yourself question whose answer is the quiz program's output."""
    text = read(os.path.join(FIXTURE, "sections", "2.1.md"))
    start = text.index("<!-- code: id=2-1-demo -->")
    end = text.index("```\n\n", start) + 4
    text = text[:start] + "<!-- code: id=cmp-demo -->\n" + text[end:]
    text = text.replace("The picture stops being true when a box holds more than one thing.\n",
                        "The picture stops being true when a box holds more than one thing.\n\n" + FIGURE)
    question = "1. What does this program print?\n\n<!-- code: id=cmp-quiz answer -->\n"
    return text.replace("1. What happens in step 1 of the trace?\n", question)


def main():
    book = os.path.join(TMP, "tiny")
    shutil.copytree(FIXTURE, book)
    shutil.rmtree(os.path.join(book, "sections"))

    # 1. try the programs
    code, out = run("us_run.py", "try", book, "2", stdin="Two programs for 2.1:\n\n" + DEMO + "\n" + QUIZ)
    check("try prints each program's real output under its header",
          code == 0 and out.splitlines()[:4] == ["== id=cmp-demo (run)", "1 0", "== id=cmp-quiz (run)", "1"], out)
    check("try ends with one summary line and nothing else", len(out.splitlines()) == 5
          and out.splitlines()[-1].startswith("ran 2  "), out)
    code, out = run("us_plan.py", "next", book)
    check("next is 2.1 before writing", out == "chapter 2, section 2.1 (0 of 3 written)", out)

    # 2. the section, with only marker lines where the programs go
    code, out = run("us_section.py", "append", book, "2", stdin=section_21())
    check("append accepts the section with bare markers", code == 0 and
          out.splitlines()[0].startswith("ok 2.1 Comparing values") and "2 programs  1 figure" in out, out)
    chapter = os.path.join(book, "chapters", "02-choices.md")
    text = read(chapter)
    check("the normal program is filled in, its output right under it",
          DEMO + "```text\n1 0\n```\n" in text, text[text.find("cmp-demo") - 20:][:300])
    want = QUIZ.replace("<!-- code: id=cmp-quiz -->", "<!-- code: id=cmp-quiz answer -->")
    after = text[text.find(want) + len(want):] if want in text else ""
    check("the answer program is filled in with its marker's answer added", want in text, text[text.find("cmp-quiz"):][:300])
    check("nothing is pasted under the answer program", after.startswith("\n<details>\n"), after[:80])
    check("its output is the first thing in the hidden answer",
          after.startswith("\n<details>\n<summary>Answer</summary>\n\n```text\n1\n```\n\nStep 1 runs line 3."), after[:200])
    svg = os.path.join(book, "chapters", "fig", "02-choices", "overview.svg")
    check("the figure is drawn at fig/<chapter>/<id>.svg", os.path.isfile(svg) and read(svg).startswith("<svg"), svg)
    check("the image line sits under the figure description",
          FIGURE + "![" in text and "](fig/02-choices/overview.svg)\n" in text, text[text.find("id=overview"):][:300])
    sys.path.insert(0, SCRIPTS)
    import us_run
    check("no trace of the tried programs is left", not os.listdir(us_run.tried_folder(chapter)), "tried/ not empty")
    code, out = run("us_plan.py", "next", book)
    check("next moves on to 2.2", out == "chapter 2, section 2.2 (1 of 3 written)", out)

    # 3. everything again: nothing changes
    before, before_svg = read(chapter, "rb"), read(svg, "rb")
    code1, out1 = run("us_run.py", chapter)
    code2, out2 = run("us_draw.py", "--chapter", chapter)
    code3, out3 = run("us_run.py", chapter, "--check")
    check("us_run.py on the chapter again: no problems, nothing changes",
          code1 == 0 and read(chapter, "rb") == before, out1)
    check("us_draw.py --chapter again: nothing changes",
          code2 == 0 and read(chapter, "rb") == before and read(svg, "rb") == before_svg, out2)
    check("us_run.py --check passes", code3 == 0, out3)

    # 4. finish the chapter and mark it reviewed
    code, out = run("us_plan.py", "mark", book, "2", "reviewed")
    check("mark refuses a chapter that is not fully written", code == 1 and "not fully written" in out, out)
    for number in ("2.2", "2.3"):
        code, out = run("us_section.py", "append", book, "2", stdin=read(os.path.join(FIXTURE, "sections", number + ".md")))
        check("append %s" % number, code == 0 and out.startswith("ok " + number), out)
    code, out = run("us_plan.py", "mark", book, "2", "reviewed")
    state = json.loads(read(os.path.join(book, "STATUS.json")))["chapters"]["2"]["state"]
    check("mark reviewed once all sections are in", code == 0 and out == "chapter 2: reviewed" and state == "reviewed", out)
    code, out = run("us_plan.py", "status", book)
    check("status shows it", out.splitlines()[2].endswith("reviewed"), out)

    shutil.rmtree(TMP, ignore_errors=True)
    passed = sum(RESULTS)
    print("%d passed, %d failed" % (passed, len(RESULTS) - passed))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
