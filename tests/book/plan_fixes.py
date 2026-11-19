"""Tests for the planner fixes (header lines, fig/short, needs, cost, status, brief, move, help, next):
python3 tests/book/plan_fixes.py"""
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

TMP = tempfile.mkdtemp(prefix="us-plan-fixes-")
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []

HEAD = """# Docker for a beginner
for: a beginner
run: console
state: docker
timeout: 120
check: docker version
check: docker ps
mask: Up \\d+ (seconds|minutes)
"""

BODY = """
## Part I · Start

### 1 First container
1.1 Why containers | story
1.2 Hello world | short | fig | teaches: hello-world
1.3 Images | teaches: image | fig | level: 2
1.4 Practice: first container | practice

### 2 Volumes
2.1 Keeping data | teaches: volume | needs: image
2.2 Named volumes | short | teaches: named-volume
2.3 Practice: volumes | practice

## Part II · More

### 3 Compose
3.1 Many containers | teaches: compose | needs: volume, hello-world
3.2 Practice: compose, see §2.1 and §1.3 | practice
"""


def test(fn):
    TESTS.append(fn)
    return fn


def run(*args):
    """Run us_plan.py with args; (exit code, output)."""
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_plan.py")] + list(args),
                       capture_output=True, text=True, env=ENV)
    return p.returncode, (p.stdout + p.stderr).strip()


def book(name, text=HEAD + BODY, chapters=None):
    """A temp book with this PLAN.md and {n: chapter text} files."""
    path = os.path.join(TMP, name)
    os.makedirs(os.path.join(path, "chapters"))
    bf.write_text(os.path.join(path, "PLAN.md"), text)
    for n, body in (chapters or {}).items():
        bf.write_text(os.path.join(path, "chapters", "%02d-x.md" % n), body)
    return path


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


@test
def header_and_fields_accepted():
    code, out = run("check", book("ok"))
    check(code == 0 and "plan ok: 3 chapters" in out and "error" not in out, out)
    plan = bf.load_plan(os.path.join(TMP, "ok"))
    check(plan.section("1.2").kind == "short" and plan.section("1.2").fig, plan.section("1.2"))
    check(plan.section("1.3").fig and plan.section("1.3").kind == "lesson" and not plan.section("1.1").fig, "fig")
    check(bf.plan_meta(os.path.join(TMP, "ok"), "check") == ["docker version", "docker ps"], "meta")


@test
def language_runs_accepted():
    for run_ in ("c", "python", "py", "javascript", "bash"):
        code, out = run("check", book("lang-" + run_, HEAD.replace("run: console", "run: " + run_) + BODY))
        check(code == 0, out)


@test
def bad_header_lines_refused():
    cases = {"run: console": ("run: bash2", "run: 'bash2' is not known"),
             "state: docker": ("state: k8s", "the only one is state: docker"),
             "timeout: 120": ("timeout: soon", "is not a number of seconds"),
             "check: docker ps": ("check:", "check: has no command"),
             "mask: Up \\d+ (seconds|minutes)": ("mask: ([a", "is not a valid pattern")}
    for i, (old, (new, want)) in enumerate(cases.items()):
        code, out = run("check", book("bad%d" % i, HEAD.replace(old, new) + BODY))
        check(code == 1 and want in out and out.count("error") == 1, out)


@test
def unknown_field_message_names_new_ones():
    code, out = run("check", book("field", HEAD + BODY.replace("| fig | teaches: hello", "| figure | teaches: hello")))
    check(code == 1 and "fig, story, short or practice" in out, out)


@test
def needs_lists_dependencies_in_book_order():
    path = book("needs")
    code, out = run("needs", path, "3.1")
    lines = out.splitlines()
    check(code == 0 and [l.split()[0] for l in lines[:-2]] == ["1.2", "1.3", "2.1", "3.1"], out)
    check(lines[-2] == "also not written earlier in chapter 1: 1.1 Why containers"
          " (add any the reader cannot do without)", out)
    check("1.2 Hello world (short, about 500 words)" in out, out)
    check(lines[-1] == "total: 4 sections, about 5,000 words, about 95,000 tokens to write", out)


@test
def needs_leaves_out_written_sections():
    path = book("needs-w", chapters={1: "# Chapter 1: First container\n\n## 1.3 Images\n\nText.\n"})
    code, out = run("needs", path, "3.1", "2.2")
    check([l.split()[0] for l in out.splitlines()[:-2]] == ["1.2", "2.1", "2.2", "3.1"], out)
    check(out.splitlines()[-2].startswith("also not written earlier in chapter 1: 1.1 Why containers ("), out)
    code, out = run("needs", path, "1.3")
    check(code == 0 and out.startswith("all written"), out)
    code, out = run("needs", path, "9.1")
    check(code == 1 and "not in the plan" in out, out)


@test
def cost_per_chapter_and_total():
    code, out = run("cost", book("cost"))
    lines = out.splitlines()
    check(code == 0 and len(lines) == 5 and " reading h " in lines[0] and "study h" not in lines[0], out)
    ch1 = lines[1].split()          # 400 + 500 + 1500 + 1200 words; study (3600/150 + 5+5+20)/60 = 0.9 h
    check(ch1[0] == "1" and ch1[-5:] == ["4", "3,600", "0.9", "4", "68,400"], lines[1])
    check(lines[-1].split()[:2] == ["total", "9"] and lines[-1].endswith("180,500"), lines[-1])
    code, out = run("cost", os.path.join(TMP, "cost"), "2")
    check(code == 0 and len(out.splitlines()) == 2 and out.splitlines()[1].split()[0] == "2", out)


@test
def cost_at_most_25_lines():
    text = "# Big\nfor: x\nrun: c\n" + "".join("### %d C%d\n%d.1 S | teaches: i%d\n" % (n, n, n, n) for n in range(1, 41))
    code, out = run("cost", book("big", text))
    check(code == 0 and len(out.splitlines()) <= 25 and "23-40" in out, out)


@test
def status_counts_not_run():
    chapter = ("# Chapter 1: First container\n\n## 1.1 Why containers\n\nText.\n\n"
               '<!-- code: id=a unrun="no network" -->\n```console\n$ docker pull x\n```\n\n'
               "<!-- code: id=b -->\n```console\n$ docker ps\n```\n\n"
               '<!--\n  code: id=c\n  unrun="no hub"\n-->\n```console\n$ docker pull y\n```\n')
    code, out = run("status", book("status", chapters={1: chapter}))
    row = [l for l in out.splitlines() if l.startswith("1 ")][0]
    check(code == 0 and row.endswith("writing, 2 not run"), out)
    check(not [l for l in out.splitlines() if l.startswith("2 ")][0].endswith("not run"), out)


@test
def brief_says_figure_and_short():
    code, out = run("brief", book("brief"), "1")
    line = [l for l in out.splitlines() if l.startswith("1.2 ")][0]
    check(code == 0 and "figure required" in line and "300 to 700 words" in line, line)
    check("figure required" in [l for l in out.splitlines() if l.startswith("1.3 ")][0], out)
    check("short" not in [l for l in out.splitlines() if l.startswith("1.3 ")][0], out)
    check("state: docker" in out, out)


@test
def move_renumbers_everything():
    path = book("move")
    os.makedirs(os.path.join(TMP, "private"), exist_ok=True)
    bf.write_text(os.path.join(TMP, "private", "route.md"), "- move 1 first\n- move 3 compose\n- other 3 x\n")
    code, out = run("move", path, "3", "--to", "1")
    text = bf.read_text(os.path.join(path, "PLAN.md"))
    check("moved chapter 3 to 1" in out, out)
    check("### 1 Compose\n1.1 Many containers" in text and "1.2 Practice: compose, see §3.1 and §2.3" in text, text)
    check("### 2 First container\n2.1 Why containers" in text and "### 3 Volumes\n3.1 Keeping data" in text, text)
    check(text.index("## Part I") < text.index("### 1 Compose") < text.index("## Part II"), text)
    check("needs" in out and code == 1, out)       # compose now needs ideas taught later: the check says so
    route = bf.read_text(os.path.join(TMP, "private", "route.md"))
    check(route == "- move 2 first\n- move 1 compose\n- other 3 x\n", route)
    code, out = run("move", path, "1", "--to", "3")
    check(code == 0 and "plan ok" in out and bf.read_text(os.path.join(path, "PLAN.md")) == HEAD + BODY,
          bf.read_text(os.path.join(path, "PLAN.md")))


@test
def move_refused_when_written():
    path = book("move-w", chapters={2: "# Chapter 2: Volumes\n\n## 2.1 Keeping data\n\nText.\n"})
    code, out = run("move", path, "1", "--to", "2")
    check(code == 1 and "already written" in out and bf.read_text(os.path.join(path, "PLAN.md")) == HEAD + BODY, out)
    code, out = run("move", path, "1", "--to", "9")
    check(code == 1 and "not in the plan" in out, out)


@test
def help_exits_zero():
    for flag in ("--help", "-h"):
        code, out = run(flag)
        check(code == 0 and "us_plan.py needs BOOK" in out, out)


@test
def next_after_out_of_order_writing():
    chapter = "# Chapter 1: First container\n\n## 1.1 Why containers\n\nText.\n\n## 1.3 Images\n\nText.\n"
    code, out = run("next", book("next", chapters={1: chapter}))
    check(code == 0 and out == "chapter 1, section 1.2 (2 of 4 written)", out)


@test
def needs_shows_earlier_sections_of_the_chapter():
    path = book("needs-e", chapters={1: "# Chapter 1: First container\n\n## 1.2 Hello world\n\nText.\n"})
    code, out = run("needs", path, "1.4", "2.2")
    lines = out.splitlines()
    check(code == 0 and lines[:2] == ["1.4 Practice: first container (practice, about 1,200 words)",
                                      "2.2 Named volumes (short, about 500 words)"], out)
    check(lines[2:4] == ["also not written earlier in chapter 1: 1.1 Why containers, 1.3 Images"
                         " (add any the reader cannot do without)",
                         "also not written earlier in chapter 2: 2.1 Keeping data"
                         " (add any the reader cannot do without)"], out)
    check(lines[4].startswith("total: 2 sections, about 1,700 words"), out)
    code, out = run("needs", path, "2.1")       # 2.1 needs 1.3: chapter 1 up to 1.3, chapter 2 has nothing before
    check(out.splitlines()[2:] == ["also not written earlier in chapter 1: 1.1 Why containers"
                                   " (add any the reader cannot do without)", out.splitlines()[-1]], out)
    check(not run("needs", path, "1.1")[1].count("also not written"), "none before 1.1")


def write_route(text):
    os.makedirs(os.path.join(TMP, "private"), exist_ok=True)
    bf.write_text(os.path.join(TMP, "private", "route.md"), text)


@test
def next_follows_route_sections():
    path = book("rs")
    try:
        write_route("- rs 2 sections 2.2\n- rs 1 First container sections 1.2, 1.4\n- rs 3\n")
        check(run("next", path)[1] == "chapter 2, section 2.2 (0 of 1 route sections written: 2.2)", run("next", path)[1])
        bf.write_text(os.path.join(path, "chapters", "02-x.md"), "# Chapter 2: Volumes\n\n## 2.2 Named volumes\n\nT.\n")
        code, out = run("next", path)
        check(code == 0 and out == "chapter 1, section 1.2 (0 of 2 route sections written: 1.2 1.4)", out)
        bf.write_text(os.path.join(path, "chapters", "01-x.md"), "# Chapter 1: First container\n\n## 1.2 Hello world\n\nT.\n")
        check(run("next", path)[1].startswith("chapter 1, section 1.4 (1 of 2"), run("next", path)[1])
        bf.write_text(os.path.join(path, "chapters", "01-x.md"),
                      "# Chapter 1: First container\n\n## 1.2 Hello world\n\nT.\n\n## 1.4 Practice: first container\n\nT.\n")
        check(run("next", path)[1] == "chapter 3, section 3.1 (0 of 2 written)", run("next", path)[1])
        write_route("- rs/1 section 1.3\n- rs 2 skip\n- rs 3 skip\n")
        check(run("next", path)[1].startswith("chapter 1, section 1.3"), run("next", path)[1])
        write_route("- rs 1 sections 1.2\n- rs 2 skip\n- rs 3 skip\n")
        check(run("next", path)[1] == "all written (skipped on the route: 2, 3)", run("next", path)[1])
        write_route("- rs 1 basics\n")      # no `sections`: the whole chapter, as before
        check(run("next", path)[1] == "chapter 1, section 1.1 (2 of 4 written)", run("next", path)[1])
        code, out = run("--help")
        check("BOOK N sections N.A N.B" in out, out)
    finally:
        os.remove(os.path.join(TMP, "private", "route.md"))


@test
def autopilot_leaves_out_chapters_routed_by_section():
    path = book("ap")
    try:
        write_route("- ap 1 sections 1.2 1.4\n")
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_autopilot.py"), path, "--dry-run"],
                           capture_output=True, text=True, env=dict(ENV, UNDERSTUDY_AUTOPILOT_WRITER="w {prompt}",
                                                                    UNDERSTUDY_AUTOPILOT_REVIEWER="r {prompt}"))
        out = p.stdout + p.stderr
        check(p.returncode == 0 and "leaving out chapter 1: the route names sections" in out, out)
        steps = [l for l in out.splitlines() if l.startswith("cd ")]
        check(steps and "chapter 2." in steps[0] and not [l for l in steps if "chapter 1." in l], out)
        sys.path.insert(0, SCRIPTS)
        import us_plan
        old = os.environ.get("UNDERSTUDY_PRIVATE")
        os.environ["UNDERSTUDY_PRIVATE"] = ENV["UNDERSTUDY_PRIVATE"]
        try:
            plan = bf.load_plan(path)
            check(us_plan.next_to_write(path, plan)[1].number == "1.2", "section-aware")
            check(us_plan.next_to_write(path, plan, whole_only=True)[0].number == 2, "autopilot skips chapter 1")
        finally:
            if old is None:
                os.environ.pop("UNDERSTUDY_PRIVATE")
            else:
                os.environ["UNDERSTUDY_PRIVATE"] = old
    finally:
        os.remove(os.path.join(TMP, "private", "route.md"))


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
