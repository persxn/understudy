"""Tests for stage 3, part A (checked marks, the facts record, known mistakes, checks across the book, the
digest): python3 tests/book/stage3.py"""
import contextlib
import datetime
import io
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
import us_check  # noqa: E402

TMP = tempfile.mkdtemp(prefix="us-stage3-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP
ENV = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
TESTS = []
COUNTER = [0]
TODAY = datetime.date.today().isoformat()

PLAN = """# Docker for beginners
for: a developer new to containers
run: none

### 1 Images
1.1 Layers | teaches: image-layer
1.2 Volumes | teaches: volume

### 2 Containers
2.1 Running | teaches: container | needs: image-layer
"""
FILL = " ".join(["word"] * 950)
NAMES = {1: "01-images.md", 2: "02-containers.md", 3: "03-more.md"}


def test(fn):
    """Register a test function."""
    TESTS.append(fn)
    return fn


def check(cond, msg):
    """Assert with a message."""
    if not cond:
        raise AssertionError(msg)


def section(number, title, idea, words, body=""):
    """A lesson: its teaches marker, a defining sentence, body, filler and a Check yourself."""
    return ("## %s %s\n\n<!-- teaches: %s = %s -->\nA **%s** is what %s names in this book.\n\n%s\n\n%s\n\n"
            "**Check yourself**\n\n1. Why?\n\n<details>\n<summary>Answer</summary>\n\nThis.\n\n</details>\n"
            % (number, title, idea, words, words.split(",")[0].strip(), title.lower(), body, FILL))


def chapters(b11="", b12="", b21="", w11="layer", w12="volume", w21="container"):
    """Chapters 1 and 2 of the plan, with extra body text per section."""
    return {1: [section("1.1", "Layers", "image-layer", w11, b11), section("1.2", "Volumes", "volume", w12, b12)],
            2: [section("2.1", "Running", "container", w21, b21 or "Each layer of the image stays read-only.")]}


def book(chs, plan=PLAN, sheet=None, mistakes=None):
    """A new book: chs is {N: [section texts]}; returns its folder."""
    COUNTER[0] += 1
    path = os.path.join(TMP, "r%d" % COUNTER[0], "bk")
    os.makedirs(os.path.join(path, "chapters"))
    write(os.path.join(path, "PLAN.md"), plan)
    if sheet:
        write(os.path.join(path, "BOOK.md"), sheet)
    if mistakes:
        write(os.path.join(path, "MISTAKES.md"), mistakes)
    for n, secs in chs.items():
        write(os.path.join(path, "chapters", NAMES[n]), "# Chapter %d: %s\n\n" % (n, NAMES[n][3:-3].title()) + "\n".join(secs))
    return path


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def run(script, *args, scripts=SCRIPTS):
    """scripts/<script> with args: (exit code, output lines)."""
    proc = subprocess.run([sys.executable, os.path.join(scripts, script)] + list(args),
                          capture_output=True, text=True, env=ENV)
    return proc.returncode, (proc.stdout + proc.stderr).splitlines()


def lines(out, level, text=""):
    """Lines of one level (ERROR, FLAG, NOTE) holding text."""
    return [l for l in out if l.startswith(level) and text in l]


def ch1(b):
    return os.path.join(b, "chapters", NAMES[1])


def stamp(path, needle):
    """Put h= (the passage hash) into the checked mark on the line holding needle."""
    text = read(path).splitlines()
    k = next(i for i, l in enumerate(text) if needle in l)
    text[k] = text[k].replace(" -->", " h=%s -->" % bf.passage_hash(text, k + 1), 1)
    write(path, "\n".join(text) + "\n")

# ---------------------------------------------------------------- A1 checked marks


@test
def malformed_marks_are_errors_with_their_fix():
    for mark, want in (("how=guess date=2026-11-18", "checked mark has how=guess: use how= one of run, practices, source, known, reworded"),
                       ("how=known", "checked mark has no date: add date=YYYY-MM-DD"),
                       ("how=known date=18/11/2026", "checked mark has date=18/11/2026: write the day as YYYY-MM-DD"),
                       ("how=known date=2026-13-40", "checked mark has date=2026-13-40"),
                       ("how=source date=2026-11-18", 'checked mark how=source has no ref: add ref="..."')):
        code, out = run("us_check.py", book(chapters(b11="Layers stack up. <!-- checked: %s -->" % mark)), "1")
        check(len(lines(out, "ERROR", want)) == 1 and code == 1, (mark, out))
    good = 'Layers stack up. <!-- checked: how=source date=2026-11-18 ref="docs.docker.com" -->'
    code, out = run("us_check.py", book(chapters(b11=good)), "1")
    check(not lines(out, "ERROR", "checked mark"), out)


@test
def a_changed_passage_is_flagged_and_a_kept_one_is_not():
    b = book(chapters(b11="Layers stack up.\n<!-- checked: how=known date=2026-11-18 -->"))
    stamp(ch1(b), "checked:")
    code, out = run("us_check.py", b, "1")
    check(not lines(out, "FLAG", "the passage changed"), out)
    write(ch1(b), read(ch1(b)).replace("Layers stack up.", "Layers  stack\nup."))     # spacing only
    code, out = run("us_check.py", b, "1")
    check(not lines(out, "FLAG", "the passage changed"), "blind to spacing: %s" % out)
    write(ch1(b), read(ch1(b)).replace("stack\nup.", "stack down."))
    code, out = run("us_check.py", b, "1")
    check(lines(out, "FLAG", "the passage changed since it was checked on 2026-11-18: check it again and restamp, "
                             "or remove the mark"), out)


@test
def one_note_counts_the_facts_of_a_chapter():
    marks = ["Fact %d. <!-- checked: how=%s date=2026-11-18%s -->" % (k, how, ' ref="x"' if how == "source" else "")
             for k, how in enumerate(["run", "run", "run", "source", "source", "practices", "practices", "known", "reworded"])]
    code, out = run("us_check.py", book(chapters(b11="\n\n".join(marks))), "1")
    notes = lines(out, "NOTE", "facts checked")
    check(len(notes) == 1 and notes[0].endswith("facts checked: 9 (run 3, source 2, practices 2, known 1, reworded 1)"), out)
    code, out = run("us_check.py", book(chapters()), "1")
    check(not lines(out, "NOTE", "facts checked"), out)


RISKY = ("Most people forget within a week. <!-- risk: a number from memory -->\n\n"
         "<!-- code: id=wipe mode=fragment -->\n```console\n$ docker volume rm -f data\n```\n\n"
         "<!-- code: id=srv unrun=\"needs a cluster\" -->\n```console\n$ kubectl get pods\n```\n\n"
         "See section 8.2.\n")


@test
def risks_leave_out_what_a_checked_mark_settles():
    code, out = run("us_check.py", book(chapters(b11=RISKY)), "1", "--risks")
    check(out[-1] == "4 items to review in chapter 1", out)
    mark = "<!-- checked: how=known date=2026-11-18 -->"
    settled = (RISKY.replace("<!-- risk: a number from memory -->", "<!-- risk: a number from memory --> " + mark)
               .replace("data\n```\n", "data\n```\n" + mark + "\n")
               .replace("pods\n```\n", "pods\n```\n" + mark + "\n")
               .replace("See section 8.2.", "See section 8.2. " + mark))
    code, out = run("us_check.py", book(chapters(b11=settled)), "1", "--risks")
    check(code == 0 and out == ["0 items to review in chapter 1"], out)
    own_line = RISKY.replace("<!-- risk: a number from memory -->", "<!-- risk: a number from memory -->\n" + mark)
    code, out = run("us_check.py", book(chapters(b11=own_line)), "1", "--risks")
    check(out[-1] == "3 items to review in chapter 1" and not any(l.startswith("risk ") for l in out), out)

# ---------------------------------------------------------------- A2 the record


FACTS = ('Layers stack up. <!-- checked: how=source date=2020-01-05 ref="docs.docker.com/layers" -->\n\n'
         'Old practice. <!-- checked: how=practices date=2020-02-01 -->\n\n'
         'Old run. <!-- checked: how=run date=2020-01-01 ref="session-7" -->\n\n'
         'Fresh source. <!-- checked: how=source date=%s ref="docs.docker.com/new" -->\n\n'
         '<!-- code: id=srv unrun="needs a cluster" -->\n```console\n$ kubectl get pods\n```\n' % TODAY)


@test
def facts_list_each_mark_then_the_unrun_blocks_then_a_count():
    b = book(chapters(b11=FACTS))
    code, out = run("us_check.py", b, "--facts")
    check(code == 0, out)
    check(out[0] == "1.1 source 2020-01-05 docs.docker.com/layers: Layers stack up.", out)
    check(out[2] == "1.1 run 2020-01-01 session-7: Old run." and len([l for l in out if l.startswith("1.1 ")]) == 4, out)
    k = out.index("shown but not run here:")
    check(out[k + 1] == "  1.1 id=srv: needs a cluster", out)
    check(out[-1] == "facts: 4 checked (run 1, source 2, practices 1), 1 shown but not run here", out)
    code, out = run("us_check.py", b, "2", "--facts")
    check(out == ["facts: 0 checked, 0 shown but not run here"], out)


@test
def facts_cut_the_passage_to_100_characters():
    long = "x" * 150 + " <!-- checked: how=known date=2026-11-18 -->"
    code, out = run("us_check.py", book(chapters(b11=long)), "1", "--facts")
    check(out[0] == "1.1 known 2026-11-18 -: " + "x" * 100, out)


@test
def stale_lists_only_old_source_and_practices_checks():
    b = book(chapters(b11=FACTS))
    code, out = run("us_check.py", b, "--facts", "--stale", "6")
    check(code == 0, out)
    got = [l.split(":")[0] for l in out[:-1]]
    check(got == ["1.1 source 2020-01-05 docs.docker.com/layers", "1.1 practices 2020-02-01 -"], out)
    check(out[-1].startswith("2 facts checked by source or practices more than 6 months ago"), out)
    code, out = run("us_check.py", b, "--facts", "--stale", "1200")
    check(code == 0 and out[-1].startswith("0 facts"), out)
    code, out = run("us_check.py", b, "9", "--facts", "--stale", "6")
    check(code == 0, "exit 0 always: %s" % out)
    check(run("us_check.py", b, "--stale", "6")[0] == 2, "--stale needs --facts")

# ---------------------------------------------------------------- A3 known mistakes

SAYS = {   # first words of the truth -> a sentence that states the mistake
    "Since Docker Engine 23": "`docker volume prune` removes all unused volumes.",
    "The top-level `version:`": "Every Compose file must start with a `version:` key.",
    "Kubernetes Secrets are stored": "Kubernetes Secrets are encrypted by default.",
    "`git pull` runs": "`git pull` is the same as `git fetch`.",
    "`git checkout` is not": "`git checkout main` is the only way to switch branches.",
    "In Python 3 `print`": 'print "Hello"',
    "Since Python 3.7": "Dictionaries are unordered.",
    "`gets` was removed": "gets(name);",
    "On a terminal glibc": "Without `fflush(stdout)` the prompt will not appear before scanf waits.",
    "401 means not": "A 401 means forbidden: you may not see this page.",
    'The "five users': "Five users find 85% of usability problems.",
    "In binary floating point": "Since 0.1 + 0.2 = 0.3 the comparison is true.",
}
FINE = [   # sentences near each mistake that are right and must not be flagged
    "`docker volume prune -a` removes all unused volumes, named ones too.",
    "A Compose file starts with `services:`; the old `version:` key is ignored.",
    "A Secret is encrypted in etcd only if you configure encryption at rest.",
    "`git pull` is the same as `git fetch` followed by `git merge`.",
    "Use `git switch main`; `git checkout main` is the only way to switch branches in old versions.",
    'print("Hello")',
    "A dict keeps the order in which keys were inserted.",
    "fgets(name, sizeof name, stdin);",
    "Call `fflush(stdout)` so the prompt also appears when output goes to a pipe.",
    "403 Forbidden means you are logged in but not allowed.",
    "If each user finds about 31% of problems, five users find about 85% by the model.",
    ">>> 0.1 + 0.2 == 0.3",
    "You might think 0.1 + 0.2 equals 0.3, but it is not.",
]


@test
def every_seeded_pattern_catches_its_mistake_and_spares_its_truth():
    rows, bad = us_check.read_mistakes(us_check.MISTAKES)
    check(not bad and len(rows) == len(SAYS) == 12, (bad, len(rows)))
    for r in rows:
        key = next(k for k in SAYS if r["truth"].startswith(k))
        check(r["re"].search(us_check.flat(SAYS[key])), "missed: %s / %s" % (r["pattern"], SAYS[key]))
        check(not r["re"].search(us_check.flat(r["truth"])), "the truth matches: %s" % r["truth"])
        check(re.search(r", \d{4}-\d{2}-\d{2}$", r["source"]), r["source"])
    for sentence in FINE:
        hits = [r["subject"] for r in rows if r["re"].search(us_check.flat(sentence))]
        check(not hits, "false alarm %s: %s" % (hits, sentence))


@test
def a_mistake_is_flagged_in_a_book_of_its_subject_only():
    body = "Run it often: `docker volume prune` removes all unused volumes."
    code, out = run("us_check.py", book(chapters(b12=body)), "1")
    flags = lines(out, "FLAG", "known mistake (docker): Since Docker Engine 23")
    check(len(flags) == 1 and "[docs.docker.com/reference/cli/docker/volume/prune, 2026-11-18]" in flags[0], out)
    k = read(ch1(book(chapters(b12=body)))).splitlines().index(body) + 1
    check(flags[0].startswith("FLAG chapters/01-images.md:%d " % k), (k, flags))
    plan = PLAN.replace("# Docker for beginners", "# Containers for beginners").replace("containers\n", "boxes\n", 1)
    code, out = run("us_check.py", book(chapters(b12=body), plan=plan), "1")
    check(not lines(out, "FLAG", "known mistake"), "not a docker book: %s" % out)
    code, out = run("us_check.py", book(chapters(b12=body), plan=plan, sheet="Reader: knows Docker a little\n"), "1")
    check(lines(out, "FLAG", "known mistake (docker)"), "BOOK.md names docker: %s" % out)


@test
def a_star_row_applies_to_every_book_and_code_lines_are_matched():
    plan = PLAN.replace("# Docker for beginners", "# Feedback")
    code, out = run("us_check.py", book(chapters(b11="So 0.1 + 0.2 = 0.3 here."), plan=plan), "1")
    check(lines(out, "FLAG", "known mistake (*): In binary floating point"), out)
    cplan = PLAN.replace("# Docker for beginners", "# Learn C")
    code, out = run("us_check.py", book(chapters(b11="<!-- code: id=g mode=fragment -->\n```c\nchar name[8];\n"
                                                      "    gets(name);\n```\n"), plan=cplan), "1")
    check(lines(out, "FLAG", "known mistake (c): `gets` was removed"), out)


@test
def a_checked_mark_within_three_lines_keeps_the_sentence():
    said = "Many think Kubernetes Secrets are encrypted by default.\nThey are not."
    for gap, flagged in ((" <!-- checked: how=reworded date=2026-11-18 -->", False),
                         ("\n<!-- checked: how=reworded date=2026-11-18 -->", False),
                         ("\n\n<!-- checked: how=reworded date=2026-11-18 -->", False),     # line 3 after
                         ("\n\n\n<!-- checked: how=reworded date=2026-11-18 -->", True),      # line 4 after
                         ("\n\n\nMore.\n\n<!-- checked: how=reworded date=2026-11-18 -->", True),
                         ("", True)):
        plan = PLAN.replace("# Docker for beginners", "# Kubernetes for beginners")
        code, out = run("us_check.py", book(chapters(b11=said + gap), plan=plan), "1")
        check(bool(lines(out, "FLAG", "known mistake (kubernetes)")) == flagged, (gap, out))


@test
def a_book_keeps_its_own_mistakes():
    own = "| subject | pattern | the truth | source, date |\n|---|---|---|---|\n| team | `\\bblue\\b\\|teal` | Our colour is green. | style guide, 2026-11-18 |\n"
    code, out = run("us_check.py", book(chapters(b11="The logo is teal."), mistakes=own), "1")
    check(lines(out, "FLAG", "known mistake (team): Our colour is green. [style guide, 2026-11-18]"), out)
    bad = own.replace("Our colour is green.", "Not blue.")
    code, out = run("us_check.py", book(chapters(), mistakes=bad), "1")
    check(code == 1 and lines(out, "ERROR MISTAKES.md:3", "the truth matches its own pattern"), out)


@test
def mistakes_prints_the_truths_for_a_subject():
    code, out = run("us_check.py", "--mistakes", "Git", "basics")
    check(code == 0 and any(l.startswith("- `git pull` runs") for l in out)
          and any(l.startswith("- In binary floating point") for l in out)
          and not any("Docker" in l for l in out), out)
    code, out = run("us_check.py", "--mistakes", "docker")
    check(len([l for l in out if l.startswith("- ")]) == 3, "docker, docker compose and *: %s" % out)


def product():
    """A copy of scripts and rules in TMP, so --learn writes there and not to the real file."""
    COUNTER[0] += 1
    home = os.path.join(TMP, "product%d" % COUNTER[0])
    shutil.copytree(SCRIPTS, os.path.join(home, "scripts"), ignore=shutil.ignore_patterns("__pycache__"))
    for name in (".claude", "rules"):
        shutil.copytree(os.path.join(ROOT, name), os.path.join(home, name))
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        shutil.copy(os.path.join(ROOT, name), home)
    return home


@test
def learn_accepts_and_refuses():
    home = product()
    scripts, data = os.path.join(home, "scripts"), os.path.join(home, "rules", "known-mistakes.md")
    before = read(data)
    code, out = run("us_check.py", "--learn", "rust", r"\bunsafe\b.{0,20}\bturns off\b|borrow checker is off",
                    "`unsafe` does not turn off the borrow checker.", "doc.rust-lang.org/book/ch20-01-unsafe-rust.html",
                    scripts=scripts)
    check(code == 0 and out[0].startswith("added to rules/known-mistakes.md: | rust |"), out)
    text = read(data)
    check(text.startswith(before) and text.count("\n") == before.count("\n") + 1, "one row appended")
    rows = us_check.read_mistakes(data)[0]
    check(rows[-1]["pattern"] == r"\bunsafe\b.{0,20}\bturns off\b|borrow checker is off"
          and rows[-1]["source"] == "doc.rust-lang.org/book/ch20-01-unsafe-rust.html, " + TODAY, rows[-1])
    for args, why in (((r"unsafe (", "Truth.", "x, 2026-11-18"), "the pattern does not compile"),
                      ((r"unsafe", "`unsafe` is fine.", "x, 2026-11-18"), "the truth matches the pattern"),
                      ((r"borrow checker is off", "No.", "y, 2026-11-18"), None)):
        code, out = run("us_check.py", "--learn", "rust", *args, scripts=scripts)
        check(code == 0 if why is None else (code == 1 and why in out[0]), (args, out))
    code, out = run("us_check.py", "--learn", "rust", r"borrow checker is off", "No.", "z", scripts=scripts)
    check(code == 1 and "already has this pattern" in out[0], out)
    code, out = run("us_check.py", "--learn", "rust", r"\bunsafe\b.{0,20}\bturns off\b|borrow checker is off",
                    "No.", "z", scripts=scripts)
    check(code == 1 and "already has this pattern" in out[0], "a duplicate with a pipe: %s" % out)
    check(run("us_check.py", "--learn", "rust", "x", scripts=scripts)[0] == 2, "usage")


@test
def learn_writes_a_book_mistakes_file():
    b = book(chapters(b11="The logo is teal."))
    code, out = run("us_check.py", "--learn", "team", "teal|navy", "Our colour is green.", "style guide", "--book", b)
    check(code == 0 and os.path.exists(os.path.join(b, "MISTAKES.md")), out)
    check("| team | `teal\\|navy` |" in read(os.path.join(b, "MISTAKES.md")), read(os.path.join(b, "MISTAKES.md")))
    code, out = run("us_check.py", b, "1")
    check(lines(out, "FLAG", "known mistake (team): Our colour is green."), out)


@test
def the_skills_check_verifies_the_table():
    home = product()
    scripts, data = os.path.join(home, "scripts"), os.path.join(home, "rules", "known-mistakes.md")
    code, out = run("us_check.py", scripts=scripts)
    check(code == 0 and not lines(out, "ERROR"), out)
    write(data, read(data) + "| x | `(unclosed` | Truth. | s, 2026-11-18 |\n| y | `truth` | The truth. | s, 2026-11-18 |\n")
    code, out = run("us_check.py", scripts=scripts)
    check(code == 1 and lines(out, "ERROR", "does not compile") and lines(out, "ERROR", "the truth matches its own pattern"), out)
    code, out = run("us_check.py", "--tokens", scripts=scripts)
    check("  script data: rules/known-mistakes.md (read by us_check.py; no agent loads it)" in out
          and not any("on demand: rules/known-mistakes.md" in l for l in out), out)

# ---------------------------------------------------------------- A4 across the whole book


@test
def a_term_claimed_by_two_ideas_is_flagged_at_the_later():
    code, out = run("us_check.py", book(chapters(w12="volume, Layer")))
    flags = lines(out, "FLAG", "term 'Layer' is already taught in 1.1 (idea image-layer): one home per idea; refer "
                               "back, or give this one its own name")
    check(len(flags) == 1 and flags[0].startswith("FLAG chapters/01-images.md:"), out)
    code, out = run("us_check.py", book(chapters(w12="volume, ly", w11="layer, ly")))
    check(not lines(out, "FLAG", "is already taught"), "two letters are ignored: %s" % out)
    code, out = run("us_check.py", book(chapters(w21="container, layer")), "1")
    check(not lines(out, "FLAG", "is already taught"), "chapter 1 only: %s" % out)
    code, out = run("us_check.py", book(chapters(w21="container, layer")), "2")
    check(lines(out, "FLAG", "term 'layer' is already taught in 1.1"), out)


@test
def a_need_never_used_is_noted():
    code, out = run("us_check.py", book(chapters(b21="Nothing from before is mentioned.")), "2")
    check(lines(out, "NOTE", "2.1 says it needs image-layer (taught in 1.1) and never uses it: drop the need, or "
                             "build on it"), out)
    code, out = run("us_check.py", book(chapters()), "2")
    check(not lines(out, "NOTE", "says it needs"), out)


@test
def a_chapter_builds_on_earlier_ones_or_is_flagged():
    code, out = run("us_check.py", book(chapters(b21="Each layer sits on a volume.")), "2")
    check(lines(out, "NOTE", "builds on 2 ideas from earlier chapters (image-layer, volume)"), out)
    code, out = run("us_check.py", book(chapters(b21="Nothing from before is mentioned.")), "2")
    check(lines(out, "FLAG", "chapter 2 uses nothing from earlier chapters: is the order right?"), out)
    code, out = run("us_check.py", book(chapters()), "1")
    check(not lines(out, "", "builds on") and not lines(out, "", "uses nothing"), "not for chapter 1: %s" % out)

# ---------------------------------------------------------------- A5 the digest

SHEET = ("Reader: a developer new to containers\nPromise: run a small app in containers\n"
         "Left at end of chapter 1: an image built from layers\nLeft at end of chapter 2: a running container\n")
PLAN3 = PLAN + "\n### 3 More\n3.1 Networks | teaches: network\n"


def digest_book():
    chs = chapters(b11='Layers are cached. <!-- checked: how=run date=2026-11-18 ref="s1" -->\n\nChapter 3 shows networks.',
                   b21="Each layer stays. See §1.2 and chapter 5.")
    chs[3] = [section("3.1", "Networks", "network", "network", "A layer again.")]
    return book(chs, plan=PLAN3.replace("### 3 More", "### 3 More\n\n### 5 Never"), sheet=SHEET)


@test
def the_digest_holds_head_ideas_facts_pointers_and_left_lines():
    b = digest_book()
    write(os.path.join(b, "PLAN.md"), PLAN3)
    code, out = run("us_check.py", b, "--digest")
    text = "\n".join(out)
    check(code == 0 and out[0] == "Reader: a developer new to containers" and "Left at end of chapter 1" not in out[:3], out[:4])
    check("## Chapter 1: Images" in out and "## Chapter 3: More" in out, text)
    check("- idea layer (image-layer, 1.1): A layer is what layers names in this book." in out, text)
    check("- fact 1.1 [run] Layers are cached." in out, text)
    check("- 1.1 points to chapter 3 (written): Chapter 3 shows networks." in out, text)
    check("- 2.1 points to §1.2 (written): See §1.2 and chapter 5." in out, text)
    check("- 2.1 points to chapter 5 (not in the plan): See §1.2 and chapter 5." in out, text)
    check("- Left at end of chapter 2: a running container" in out, text)
    words = sum(len(l.split()) for l in out[:-1])
    check(out[-1] == "3 chapters, 4 ideas, 1 checked fact, %d words" % words, (out[-1], words))


@test
def the_digest_from_a_shows_earlier_chapters_as_terms():
    b = digest_book()
    code, out = run("us_check.py", b, "--digest", "--from", "2", "--to", "2")
    check(code == 0 and "Chapter 1 terms: layer, volume" in out and "## Chapter 1: Images" not in out
          and "## Chapter 2: Containers" in out and "## Chapter 3: More" not in out, out)
    check(out[-1].startswith("1 chapter, 1 idea, 0 checked facts, "), out[-1])
    check("- 2.1 points to chapter 5 (planned, not written): See §1.2 and chapter 5." in out, out)


@test
def the_digest_drops_the_oldest_detail_to_fit():
    bk = us_check.Book(digest_book())
    old = us_check.DIGEST_WORDS
    try:
        us_check.DIGEST_WORDS = 120
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            us_check.digest(bk)
    finally:
        us_check.DIGEST_WORDS = old
    out = buf.getvalue().splitlines()
    check("## Chapter 3: More" in out and "## Chapter 1: Images" not in out and "Chapter 1 terms: layer, volume" in out, out)
    cut = [l for l in out if l.startswith("cut to fit 120 words:")]
    check(len(cut) == 1 and "chapter" in cut[0] and "terms only" in cut[0], out)
    check(int(re.search(r"(\d+) words$", out[-1]).group(1)) <= 120, out[-1])
    check(run("us_check.py", bk.path, "1", "--digest")[0] == 2, "no chapter with --digest")


@test
def a_definition_is_found_further_down_the_section_but_not_among_the_questions():
    sys.path.insert(0, SCRIPTS)
    import us_bookfmt as bf
    text = ("# Chapter 1: X\n\n## 1.1 A\n\n<!-- teaches: traceback = traceback, error message -->\n"
            "Here is a program with one small slip in it, saved as slip.py.\n\n```python\nprint(tea)\n```\n\n"
            "Everything Python printed after the heading is called a traceback: the error message, with its trail.\n\n"
            "<!-- teaches: version = version -->\nNothing here says what it is, only that you type a command.\n\n"
            "**Check yourself**\n\n1. Which version do you have, and how do you know?\n\n<details>\n<summary>Answer</summary>\n\nA.\n\n</details>\n")
    doc = bf.parse_chapter(text)
    found = {t.id: bf.definition(t, doc.lines) for t in doc.sections[0].teaches}
    check(found["traceback"].startswith("Everything Python printed after the heading is called a traceback"), found)
    check(found["version"] == "", found)


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
