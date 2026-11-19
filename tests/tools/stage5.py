#!/usr/bin/env python3
"""Tests for stage 5 (the plan and chapter side of the curriculum, second design): the held:, later: and from:
lines of PLAN.md (us_bookfmt.py), every message `us_plan.py check` gives about them, the curriculum block of
`us_plan.py brief`, `move` carrying a from: line, the other commands with the new lines, the curriculum-word FLAG
of `us_check.py`, and that a plan without these lines gives the same output as before.
Each test builds its own curriculum (UNDERSTUDY_CURRICULUM) and books in a temp folder.
Prints one line per test and "N passed, M failed"; exit 1 on failure.

    python3 tests/tools/stage5.py
"""
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
import us_path  # noqa: E402

TMP = tempfile.mkdtemp(prefix="us-stage5-test-")
TESTS = []
COUNT = [0]


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


def card(ident, needs="none", words=None, steps=6, notes=True, deep="2, 3"):
    """A card with `steps` steps: in the third design (Step notes, Deep steps) unless notes=False."""
    blocks = "\n".join("### %d\nNeed: why does `cmd%d` of %s do that?\nShow: run `cmd%d`: it prints %d.\nExplain: "
                       "%s loops %d times.\nTry: predict: the output; fix: a broken `cmd%d`." % (
                           k, k, ident, k, k, ident.capitalize(), k, k) for k in range(1, steps + 1))
    notes_part = "\n## Step notes\n%s\n" % blocks if notes else ""
    deep_line = "- Deep steps: %s (the loop).\n" % deep if notes else ""
    order = "\n".join("%d. %s step %d with `cmd%d`." % (k, ident.capitalize(), k, k) for k in range(1, steps + 1))
    return """# %(id)s: %(id)s for testers
kind: tool
needs: %(needs)s
status: built 2026-11-18
sources: example.org (the order)

## Promise
Run %(id)s.

## The one idea
One loop.

## In production
- Files in Git.

## Teaching order
%(order)s

## State and danger
- [1] State in `%(id)s.json`.
- [3] `%(id)s wipe` deletes the work.
- Untagged danger of %(id)s.

%(notes)s
## Go deep, leave for later
%(deep)s- Deep: the loop.

## Never omit
- Always back up %(id)s.
- [2] Only for step two of %(id)s.

## Wrong beliefs
- [1] "%(id)s is magic" (it is a loop).
- [4] "%(id)s never fails" (it does).

## Failures to diagnose
- [2] %(id)s will not start: a wrong name.

## Practice and project
Guided: repeat each %(id)s step. Project: your own %(id)s; finish line: it runs.

## Mastery ladder
- Use: run it.
- Explain: trace it.
- Build: the project.
- Design: size it.

## Words to own
%(words)s
""" % {"id": ident, "needs": needs, "order": order, "words": words or "[1] %s loop; [2-6] %s state" % (ident, ident),
       "notes": notes_part, "deep": deep_line}


def curriculum(cards=None):
    """A curriculum folder with cards alpha, beta (needs alpha) and gamma, or the given {id: text}."""
    COUNT[0] += 1
    cur = os.path.join(TMP, "cur%d" % COUNT[0], "curriculum")
    cards = cards or {"alpha": card("alpha", words="[1] exchange argument, pod, (met thing); [2] desired-state; [3] loop; "
                                                   "[4] reconcile; [5-6] alpha state"),
                      "beta": card("beta", needs="alpha"), "gamma": card("gamma")}
    for ident, text in cards.items():
        write(os.path.join(cur, "cards", ident + ".md"), text)
    return cur


def book(name, plan, chapters=None, shelf=None):
    """A book folder with PLAN.md and chapter files {n: text}; returns its path."""
    COUNT[0] += 1
    path = os.path.join(shelf or os.path.join(TMP, "shelf%d" % COUNT[0]), name)
    write(os.path.join(path, "PLAN.md"), plan)
    for n, text in (chapters or {}).items():
        write(os.path.join(path, "chapters", "%02d-chapter-%d.md" % (n, n)), text)
    return path


def run(cur, script, *args):
    """Run a script with curriculum `cur` (None: a folder that does not exist): (exit code, output lines)."""
    env = dict(os.environ, UNDERSTUDY_CURRICULUM=cur or os.path.join(TMP, "no-curriculum"),
               UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args), capture_output=True, text=True,
                          env=env)
    return proc.returncode, [l for l in (proc.stdout + proc.stderr).splitlines() if not l.startswith("warning:")]


def plan_text(head="", chapters=(("One", "", "a"), ("Two", "", "b"))):
    """PLAN.md: header lines, then chapters (title, from: line or '', idea) of one section each."""
    out = ["# Book", "for: testers", "run: none"] + ([head] if head else []) + [""]
    for n, (title, src, idea) in enumerate(chapters, 1):
        out += ["### %d %s" % (n, title)] + ([src] if src else []) + ["%d.1 %s | teaches: %s" % (n, title, idea), ""]
    return "\n".join(out)


def errors(out):
    return [l for l in out if l.startswith("error ")]


def warns(out):
    """The warn lines of check, the chapter-shape ones and the deep-step room notes left out."""
    return [l for l in out if l.startswith("warn ") and "sections (usually" not in l and "practice section" not in l
            and "holds the deep step" not in l]


def room(out):
    return [l for l in out if "holds the deep step" in l]

# ---------------------------------------------------------------- parsing the lines


@test
def plan_parses_held_later_and_from():
    text = ("# B\nfor: t\nrun: none\nheld: alpha 1-3 (shown in placement; quiz 2); beta\n"
            "held: gamma 2,4 (the reason (nested) is ignored)\nlater: beta 5 ; gamma 1, 3\n\n"
            "### 1 One\nfrom: alpha 4-6; gamma 5-6 (here)\n1.1 A | teaches: a\n\n### 2 Two\n2.1 B\n")
    plan = bf.parse_plan_text(text)
    check(plan.errors == [], plan.errors)
    check(plan.held == [(4, "alpha", [1, 2, 3]), (4, "beta", None), (5, "gamma", [2, 4])], plan.held)
    check(plan.later == [(6, "beta", [5]), (6, "gamma", [1, 3])], plan.later)
    check(plan.chapter(1).from_refs == [("alpha", [4, 5, 6]), ("gamma", [5, 6])] and plan.chapter(1).from_line == 9,
          plan.chapter(1))
    check(plan.chapter(2).from_refs == [] and plan.chapter(2).from_line == 0 and plan.uses_curriculum(), plan.chapter(2))
    check([s.number for s in plan.sections()] == ["1.1", "2.1"], plan.sections())
    check(not bf.parse_plan_text("# B\n\n### 1 One\n1.1 A\n").uses_curriculum(), "a plain plan uses the curriculum")


@test
def plan_lines_in_the_wrong_place_or_unreadable_are_errors():
    text = ("# B\nfor: t\nfrom: alpha 1\nheld: alpha x-y; Alpha_1\nlater:\n\n### 1 One\n1.1 A\nfrom: alpha 2\n\n"
            "### 2 Two\nfrom: beta 1\nfrom: beta 2\nheld: gamma\n2.1 B\n")
    plan = bf.parse_plan_text(text)
    got = dict((n, m) for n, m in plan.errors)
    check(got[3].startswith("a from: line goes directly under its chapter's '### N Title' line"), plan.errors)
    check(any(n == 4 and "held: cannot read 'alpha x-y'; write CARD STEPS" in m for n, m in plan.errors), plan.errors)
    check(any(n == 4 and "cannot read 'Alpha_1'" in m for n, m in plan.errors), plan.errors)
    check(got[5] == "later: names no card; write later: CARD STEPS, or drop the line", plan.errors)
    check(got[9].startswith("a from: line goes directly under") and got[13].startswith("a from: line goes"), plan.errors)
    check(got[14] == "held: lines go above the first chapter, with the other header lines; move it there", plan.errors)
    check(plan.chapter(2).from_refs == [("beta", [1])], plan.chapter(2).from_refs)

# ---------------------------------------------------------------- us_plan.py check


@test
def check_passes_and_counts_the_steps():
    cur = curriculum()
    path = book("b", plan_text("held: alpha 4-6 (shown in placement; quiz)\nlater: gamma (next book)",
                               (("One", "from: alpha 1-3", "a"), ("Two", "from: beta; alpha 2", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and out[-1] == "plan ok: 2 chapters, 2 sections, 2 ideas, 9 curriculum steps taught, 3 held, 6 later",
          out)
    check(warns(out) == [], out)


@test
def check_unknown_card_and_step():
    cur = curriculum()
    path = book("b", plan_text("held: nope 1", (("One", "from: alpha 1-6; beta 1-6 (all); alpha 9", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and "error PLAN.md:4: no card 'nope' in the curriculum; fix the id (python3 scripts/us_path.py find "
                        "nope)" in out, out)
    check("error PLAN.md:7: alpha has steps 1 to 6; step 9 does not exist" in out and len(errors(out)) == 2, out)


@test
def check_every_step_accounted_for():
    cur = curriculum()
    path = book("b", plan_text("", (("One", "from: alpha 1-3", "a"), ("Two", "from: alpha 2; gamma 1", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == [
        "error PLAN.md:6: alpha: steps 4, 5, 6 are in no from:, held: or later: line; add them to a chapter's from: "
        "line, or to held: (the learner has shown it) or later: (left for a later book)",
        "error PLAN.md:10: gamma: steps 2, 3, 4, 5, 6 are in no from:, held: or later: line; add them to a chapter's "
        "from: line, or to held: (the learner has shown it) or later: (left for a later book)"], out)
    path = book("b", plan_text("held: alpha 3-6\nlater: alpha 6; gamma",
                               (("One", "from: alpha 1-3", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == [
        "error PLAN.md:4: alpha: steps 3, 6 are in more than one of from:, held: and later:; a step is taught, held or "
        "left for later: keep it in one"], out)


@test
def check_needs_of_a_taught_card():
    cur = curriculum()
    path = book("b", plan_text("", (("One", "from: beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:6: beta needs alpha: teach its steps here, or list them under "
                                        "held: (the learner showed they have them) or later:"], out)
    for head in ("held: alpha", "later: alpha (next book)"):
        path = book("b", plan_text(head, (("One", "from: beta", "a"),)))
        code, out = run(cur, "us_plan.py", "check", path)
        check(code == 0 and out[-1].startswith("plan ok:"), (head, out))
    shelf = os.path.join(TMP, "shelf-needs")
    book("first", plan_text("", (("One", "from: alpha", "x"),)), shelf=shelf)
    path = book("second", plan_text("", (("One", "from: beta", "a"),)), shelf=shelf)
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and out[-1] == "plan ok: 1 chapters, 1 sections, 1 ideas, 6 curriculum steps taught, 0 held, 0 later",
          out)
    path = book("b", plan_text("held: beta", (("One", "from: gamma", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0, out)                          # a held card's needs are not asked for


@test
def check_notes_a_deep_step_without_room():
    cur = curriculum()
    path = book("b", plan_text("held: alpha 5-6", (("One", "from: alpha 1-4", "a"), ("Two", "from: beta", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)       # alpha's deep steps 2 and 3 with 3 others each
    check(code == 0 and room(out) == [
        "warn PLAN.md:7: note: chapter 1 holds the deep step alpha 2 with 3 other steps: give it room",
        "warn PLAN.md:7: note: chapter 1 holds the deep step alpha 3 with 3 other steps: give it room",
        "warn PLAN.md:11: note: chapter 2 holds the deep step beta 2 with 5 other steps: give it room",
        "warn PLAN.md:11: note: chapter 2 holds the deep step beta 3 with 5 other steps: give it room"], out)
    path = book("b", plan_text("held: alpha 5-6\nlater: beta 4-6", (("One", "from: alpha 1-2; beta 1", "a"),
                                                                    ("Two", "from: alpha 3-4; beta 2", "b"),
                                                                    ("Three", "from: beta 3", "c"))))
    code, out = run(cur, "us_plan.py", "check", path)       # a deep step with two others: room enough
    check(code == 0 and room(out) == [], out)
    old = curriculum({"alpha": card("alpha", notes=False), "beta": card("beta", needs="alpha", notes=False)})
    path = book("b", plan_text("held: alpha 5-6", (("One", "from: alpha 1-4", "a"), ("Two", "from: beta", "b"))))
    code, out = run(old, "us_plan.py", "check", path)       # old-form cards have no deep steps
    check(code == 0 and room(out) == [], out)


@test
def check_needs_with_alternatives():
    cards = {"alpha": card("alpha"), "gamma": card("gamma"), "delta": card("delta", needs="alpha | gamma")}
    cur = curriculum(cards)
    path = book("b", plan_text("", (("One", "from: delta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:6: delta needs alpha or gamma: teach its steps here, or list them "
                                        "under held: (the learner showed they have them) or later:"], out)
    for head in ("held: gamma", "later: alpha"):
        path = book("b", plan_text(head, (("One", "from: delta", "a"),)))
        code, out = run(cur, "us_plan.py", "check", path)
        check(code == 0 and warns(out) == [], (head, out))
    shelf = os.path.join(TMP, "shelf-alt")
    book("first", plan_text("", (("One", "from: gamma", "x"),)), shelf=shelf)
    path = book("second", plan_text("", (("One", "from: delta", "a"),)), shelf=shelf)
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0, out)
    path = book("b", plan_text("", (("One", "from: delta", "a"), ("Two", "from: gamma", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and warns(out) == ["warn PLAN.md:6: note: delta is first taught in chapter 1, before gamma "
                                       "(chapter 2), which it needs: is this order meant?"], out)
    path = book("b", plan_text("", (("One", "from: alpha", "a"), ("Two", "from: delta", "b"), ("Three", "from: gamma", "c"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and warns(out) == [], out)    # alpha, taught first, satisfies the need


@test
def check_flags_a_card_taught_before_what_it_needs():
    cur = curriculum()
    path = book("b", plan_text("", (("One", "from: beta", "a"), ("Two", "from: alpha", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and warns(out) == ["warn PLAN.md:6: note: beta is first taught in chapter 1, before alpha "
                                       "(chapter 2), which it needs: is this order meant?"], out)
    path = book("b", plan_text("later: alpha 4-6", (("One", "from: beta", "a"), ("Two", "from: alpha 1-3", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and len(warns(out)) == 1 and "note: beta is first taught in chapter 1" in warns(out)[0], out)
    # a sound plan: one step of alpha woven into a later chapter, the rest held or deferred
    path = book("b", plan_text("held: alpha 1-2\nlater: alpha 4-6", (("One", "from: beta", "a"),
                                                                     ("Two", "from: alpha 3", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and warns(out) == [], out)


@test
def check_notes_steps_taught_out_of_the_cards_order():
    cur = curriculum()
    path = book("b", plan_text("", (("One", "from: gamma 4-6; alpha 2-6", "a"), ("Two", "from: gamma 1-3; alpha 1", "b"))))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and warns(out) == [
        "warn PLAN.md:6: note: alpha step 2 is taught in chapter 1, before step 1 (chapter 2); the card teaches them "
        "the other way round: is this order meant?",
        "warn PLAN.md:6: note: gamma step 4 is taught in chapter 1, before step 1 (chapter 2); the card teaches them "
        "the other way round: is this order meant?"], out)


@test
def check_without_a_curriculum_folder_reads_the_lines_only():
    path = book("b", plan_text("held: nope 1", (("One", "from: alpha 1", "a"),)))
    code, out = run(None, "us_plan.py", "check", path)
    check(code == 0 and out[-1] == "plan ok: 1 chapters, 1 sections, 1 ideas", out)
    path = book("b", plan_text("held: alpha one", (("One", "from: alpha 1", "a"),)))
    code, out = run(None, "us_plan.py", "check", path)
    check(code == 1 and errors(out)[0].startswith("error PLAN.md:4: held: cannot read 'alpha one'"), out)

MAP = """# Testing: a track
for: testers
leads to: tests
status: built 2026-11-18
sources: example.org

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | alpha | none | a | a | 10 | 1 Use |
| 2 | beta | 1 | b | b | 10 | 1 Use |
| 3 | omega (planned) | 2 | o | o | 10 | 1 Use |
| 4 | gamma | none | g | g | 10 | 1 Use |
"""


def track_curriculum():
    cur = curriculum()
    write(os.path.join(cur, "testing", "track.md"), MAP)
    return cur


@test
def track_line_parses_and_misplaced_or_unreadable_is_an_error():
    plan = bf.parse_plan_text("# B\ntrack: testing/track 1-2, 4 (the goal; from the map)\ntrack: testing/other\n"
                              "track: nonsense here\n\n### 1 One\ntrack: testing/track\n1.1 A\n")
    check(plan.track == [(2, "testing/track", [1, 2, 4]), (3, "testing/other", None)], plan.track)
    check(plan.errors == [(4, "track: cannot read 'nonsense here'; write track: DOMAIN/TRACK ROWS, such as "
                              "system-design/foundations 1-5, 7 (no rows: all of them)"),
                          (7, "track: lines go above the first chapter, with the other header lines; move it there")],
          plan.errors)


@test
def track_map_and_rows_must_exist():
    cur = track_curriculum()
    path = book("b", plan_text("track: testing/nothing\ntrack: testing/track 2, 5-6",
                               (("One", "from: alpha; beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:4: no track map 'testing/nothing'; tracks: testing/track",
                                        "error PLAN.md:5: testing/track has rows 1 to 4; row 5, 6 does not exist"], out)


@test
def track_rows_with_cards_must_be_accounted_for():
    cur = track_curriculum()
    path = book("b", plan_text("track: testing/track (my goal)", (("One", "from: alpha; beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:4: the goal's track names gamma (row 4 of testing/track): teach "
                                        "its steps in a chapter, or account for them under held: or later:"], out)
    path = book("b", plan_text("track: testing/track 1-3", (("One", "from: alpha; beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)       # row 3 is planned: skipped
    check(code == 0 and out[-1] == "plan ok: 1 chapters, 1 sections, 1 ideas, 12 curriculum steps taught, 0 held, "
                                   "0 later" and warns(out) == [], out)
    path = book("b", plan_text("track: testing/track\nheld: gamma", (("One", "from: alpha; beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0, out)
    shelf = os.path.join(TMP, "shelf-track")
    book("first", plan_text("", (("One", "from: gamma", "x"),)), shelf=shelf)
    path = book("second", plan_text("track: testing/track", (("One", "from: alpha; beta", "a"),)), shelf=shelf)
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0, out)
    path = book("b", plan_text("track: testing/track 4", (("One", "", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and out[-1] != "plan ok" and len(errors(out)) == 1, out)
    path = book("b", plan_text("track: testing/track 4", (("One", "", "a"),)))
    code, out = run(None, "us_plan.py", "check", path)    # no curriculum folder: not checked, summary as before
    check(code == 0 and out[-1] == "plan ok: 1 chapters, 1 sections, 1 ideas", out)


@test
def track_refuses_a_goal_card_only_left_for_later():
    cur = track_curriculum()
    path = book("b", plan_text("track: testing/track 1-2, 4\nlater: gamma (second book)",
                               (("One", "from: alpha; beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:4: gamma is in the goal's rows (track:) but this book teaches none "
                                        "of it: teach at least the steps the goal cannot do without"], out)
    for head, src in (("later: gamma 2-6", "from: alpha; beta; gamma 1"), ("held: gamma 1-2\nlater: gamma 3-6",
                                                                          "from: alpha; beta"),
                      ("held: gamma", "from: alpha; beta")):
        path = book("b", plan_text("track: testing/track 1-2, 4\n" + head, (("One", src, "a"),)))
        code, out = run(cur, "us_plan.py", "check", path)
        check(code == 0 and warns(out) == [], (head, out))


@test
def one_book_at_a_time_and_later_books_of_a_series():
    cur = track_curriculum()
    many = tuple(("C%d" % k, "from: alpha" if k == 1 else "", "i%d" % k) for k in range(1, 18))
    path = book("b", plan_text("track: testing/track 1", many))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:4: this is more than one book (17 chapters): a book has at most "
                                        "16 chapters; group more steps in a chapter, leave what the goal can do without "
                                        "under later:, and only if the goal still does not fit make it a series with "
                                        "later: ... (book 2)"], out)
    path = book("b", plan_text("", many))                          # no track: line: nothing changes
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0, out)
    write(os.path.join(cur, "testing", "big.md"), MAP.replace("| alpha | none | a | a | 10 |", "| alpha | none | a | a | 300 |"))
    path = book("b", plan_text("track: testing/big 1\nbudget: 400 hours", (("One", "from: alpha", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)              # no hour cap: budget: alone decides
    check(code == 0, out)
    path = book("b", plan_text("track: testing/track 1-2, 4\nlater: gamma (book 2)", (("One", "from: alpha; beta", "a"),)))
    code, out = run(cur, "us_plan.py", "check", path)              # gamma, left for book 2, is not "untaught"
    check(code == 0 and out[-1] == "plan ok: 1 chapters, 1 sections, 1 ideas, 12 curriculum steps taught, 0 held, "
                                   "6 later, 6 steps for later books", out)


def lessons(n, head):
    """PLAN.md of one chapter with n lesson sections (0.25 study hours each, as cost counts them)."""
    return "# Book\nfor: testers\nrun: none\n%s\n\n### 1 One\n%s\n" % (
        head, "\n".join("1.%d Part %d | teaches: p%d" % (k, k, k) for k in range(1, n + 1)))


@test
def budget_refuses_a_plan_far_over_the_learners_hours():
    path = book("b", lessons(8, "budget: 1.7 hours (two evenings)"))
    code, out = run(None, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:4: the plan needs about 2 hours of study; the learner has 1.7 "
                                        "(budget:): move steps to later: or cut sections, keeping every card the goal "
                                        "names"], out)
    code, cost = run(None, "us_plan.py", "cost", path)
    check(cost[-1].split()[3] == "2.0", cost)          # no from: lines: the same hours as cost
    for head, n in (("budget: 1.74 hours", "1.74"), ("budget: 2 hours", "2"), ("budget: 40", "40"), ("budget: 30h", "30")):
        path = book("b", lessons(8, head))
        code, out = run(None, "us_plan.py", "check", path)
        check(code == 0 and out[-1] == "plan ok: 1 chapters, 8 sections, 8 ideas, about 2 of %s budget hours (reading and "
                                   "study, as cost counts it)" % n,
              (head, out))
    for head, msg in (("budget: lots", "budget: cannot read 'lots'; write budget: N hours"),
                      ("budget: 4 hours\nbudget: 5 hours", "budget: is written twice; keep one")):
        path = book("b", lessons(8, head))
        code, out = run(None, "us_plan.py", "check", path)
        check(code == 1 and any(msg in l for l in errors(out)), (head, out))
    plan = bf.parse_plan_text("# B\n\n### 1 One\nbudget: 3 hours\n1.1 A\n")
    check(plan.errors == [(4, "budget: goes above the first chapter, with the other header lines; move it there")],
          plan.errors)


@test
def budget_counts_track_map_hours_for_curriculum_steps():
    cards = {"alpha": card("alpha"), "beta": card("beta", needs="alpha"), "delta": card("delta")}
    cur = curriculum(cards)
    write(os.path.join(cur, "testing", "track.md"), MAP)       # alpha, beta and gamma: 10 hours each
    lessons4 = "\n".join("%%d.%d Part %d | teaches: %%s%d" % (k, k, k) for k in range(1, 5))

    def plan(head):
        return ("# Book\nfor: t\nrun: none\n%s\nlater: alpha 4-6\n\n### 1 One\nfrom: alpha 1-3\n1.1 A | teaches: a\n\n"
                "### 2 Two\nfrom: beta; alpha 2\n2.1 B | teaches: b\n\n### 3 Own\n%s\n\n### 4 Delta\nfrom: delta\n%s\n"
                % (head, lessons4 % ((3, "c") * 4), lessons4 % ((4, "d") * 4)))
    # alpha 3 of 6 steps = 5 h, beta 10 h, chapter 3 (no from:) 4 lessons = 1 h, delta (no hours in a map): its
    # chapter's cost, 1 h: 17 hours, where cost counts reading time only (2.5 h)
    path = book("b", plan("budget: 14 hours"))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 1 and errors(out) == ["error PLAN.md:4: the plan needs about 17 hours of study; the learner has 14 "
                                        "(budget:): move steps to later: or cut sections, keeping every card the goal "
                                        "names"], out)
    path = book("b", plan("budget: 15 hours"))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and out[-1] == "plan ok: 4 chapters, 10 sections, 10 ideas, 15 curriculum steps taught, 0 held, "
                                   "3 later, about 17 of 15 budget hours (study and practice, by the roadmap)", out)
    path = book("b", plan("budget: 15 hours").replace("budget: 15 hours\n", ""))
    code, out = run(cur, "us_plan.py", "check", path)
    check(code == 0 and "budget hours" not in out[-1], out)


@test
def budget_line_kept_by_the_other_commands():
    path = book("b", "# Book\nfor: t\nrun: none\nbudget: 9 hours\n\n### 1 One\n1.1 A | teaches: a\n\n"
                     "### 2 Two\n2.1 B | teaches: b\n")
    code, out = run(None, "us_plan.py", "move", path, "2", "--to", "1")
    check(code == 0 and "budget: 9 hours" in read(os.path.join(path, "PLAN.md")), out)
    for args in (("status", path), ("next", path), ("cost", path)):
        code, out = run(None, "us_plan.py", *args)
        check(code == 0 and "Traceback" not in "\n".join(out), (args, out))
    write(os.path.join(path, "chapters", "01-b.md"), "# Chapter 1: B\n\n## 1.1 B\n\nText.\n")
    code, out = run(None, "us_plan.py", "from-chapters", path, "--force")
    check(code == 0 and out == ["wrote PLAN.md: 1 chapters, 1 sections"], out)


@test
def track_line_kept_by_the_other_commands():
    cur = track_curriculum()
    text = plan_text("track: testing/track 1-2", (("One", "from: alpha", "a"), ("Two", "from: beta", "b")))
    path = book("b", text)
    code, out = run(cur, "us_plan.py", "move", path, "2", "--to", "1")
    check(code == 0 and "track: testing/track 1-2" in read(os.path.join(path, "PLAN.md")), out)
    for args in (("status", path), ("next", path), ("cost", path)):
        code, out = run(cur, "us_plan.py", *args)
        check(code == 0 and "Traceback" not in "\n".join(out), (args, out))
    write(os.path.join(path, "chapters", "01-two.md"), "# Chapter 1: Two\n\n## 1.1 Two\n\nText.\n")
    code, out = run(cur, "us_plan.py", "from-chapters", path, "--force")
    check(code == 0 and out == ["wrote PLAN.md: 1 chapters, 1 sections"], out)

# ---------------------------------------------------------------- brief, move and the other commands


@test
def brief_appends_the_notes_of_the_chapters_steps():
    cur = curriculum()
    plain = book("b", plan_text("", (("One", "", "a"), ("Two", "", "b"))))
    path = book("b", plan_text("held: alpha 1-2, 5-6; gamma 1-2", (("One", "from: alpha 3-4", "a"),
                                                                   ("Two", "", "b"))))
    code, before = run(cur, "us_plan.py", "brief", plain, "1")
    code, out = run(cur, "us_plan.py", "brief", path, "1")
    check(code == 0 and out[:len(before)] == before, (before, out))
    import us_path
    def block(k, deep=""):
        return ["%d. Alpha step %d with `cmd%d`.%s" % (k, k, k, deep), "  Need: why does `cmd%d` of alpha do that?" % k,
                "  Show: run `cmd%d`: it prints %d." % (k, k), "  Explain: Alpha loops %d times." % k]
    check(out[len(before):] == ["", us_path.NOTES_HEAD, "alpha, steps 3-4 of 6"] +
          block(3, " (a deep step: give it the chapter's best pages)") +
          ["  State and danger:", "  - `alpha wipe` deletes the work.", "  Words to own: loop",
           "  Try: predict: the output; fix: a broken `cmd3`."] + block(4) +
          ["  Teach against:", '  - "alpha never fails" (it does).', "  Words to own: reconcile",
           "  Try: predict: the output; fix: a broken `cmd4`.",
           "State and danger:", "- Untagged danger of alpha.", "Never omit:", "- Always back up alpha.",
           "Practice: Guided: repeat each alpha step."], out[len(before):])
    check(us_path.NOTES_HEAD == (
        "From the curriculum: checked notes for this chapter's steps. They are a reference, not the chapter's outline. "
        "Build the chapter on ONE real problem or case from this book's setting, carried from the first attempt to "
        "finished, checked work; go deep on the deep step (prove its claim, walk one case by hand) and let the other "
        "steps serve it. Take from the notes the order, the question the reader must end up able to answer (Need), "
        "the experiment worth staging (Show), what goes wrong, and the beliefs to teach against. A fact or number here "
        "was run or sourced: keep it as written, or replace it only with output this book's own run pastes. Never "
        "state a result, a count, or a comparison of two numbers that you did not run or work out on the page. Try "
        "tasks are the least practice: the chapter's practice climbs past them to a problem the reader has not met "
        "in the chapter and solves alone. A word \"met in passing\" is glossed once, not taught. None of this "
        "wording is copied:"), us_path.NOTES_HEAD)
    old = curriculum({"alpha": card("alpha", notes=False), "gamma": card("gamma", notes=False)})   # old form
    code, out = run(old, "us_plan.py", "brief", path, "1")
    check(out[len(before) + 2:] == ["alpha, steps 3-4 of 6", "3. Alpha step 3 with `cmd3`.", "  State and danger:",
                                    "  - `alpha wipe` deletes the work.", "  Words to own: alpha state",
                                    "4. Alpha step 4 with `cmd4`.", "  Teach against:",
                                    '  - "alpha never fails" (it does).', "State and danger:", "- Untagged danger of alpha.",
                                    "Never omit:", "- Always back up alpha.",
                                    "Practice: Guided: repeat each alpha step."], out[len(before):])
    code, out2 = run(cur, "us_plan.py", "brief", path, "2")
    code, before2 = run(cur, "us_plan.py", "brief", plain, "2")
    check(out2 == before2 and not any("From the curriculum" in l for l in out2), out2)


@test
def move_carries_the_from_line():
    cur = curriculum()
    path = book("b", plan_text("", (("One", "from: alpha 1-2", "a"), ("Two", "from: alpha 3-4", "b"),
                                    ("Three", "from: alpha 5-6", "c"))))
    code, out = run(cur, "us_plan.py", "move", path, "1", "--to", "3")
    check(code == 0 and out[0] == "moved chapter 1 to 3; chapters renumbered", out)
    lines = read(os.path.join(path, "PLAN.md")).splitlines()
    for n, title, src in ((1, "Two", "from: alpha 3-4"), (2, "Three", "from: alpha 5-6"), (3, "One", "from: alpha 1-2")):
        i = lines.index("### %d %s" % (n, title))
        check(lines[i + 1] == src and lines[i + 2].startswith("%d.1 %s" % (n, title)), lines)
    check(out[-1].startswith("plan ok: 3 chapters") and "18 curriculum" not in out[-1], out)
    check(any("note: alpha step 3 is taught in chapter 1, before step 1 (chapter 3)" in l for l in out), out)
    plan = bf.load_plan(path)
    check([c.from_refs for c in plan.chapters] == [[("alpha", [3, 4])], [("alpha", [5, 6])], [("alpha", [1, 2])]], plan)


@test
def other_commands_work_with_the_lines():
    cur = curriculum()
    text = plan_text("held: alpha 4-6\nlater: gamma", (("One", "from: alpha 1-3", "a"), ("Two", "from: beta", "b")))
    path = book("b", text, {1: "# Chapter 1: One\n\n## 1.1 One\n\nText about a.\n"})
    for args, want in ((("status", path), r"^1\s+One\s+1/1 .*written$"), (("next", path), r"^chapter 2, section 2\.1"),
                       (("cost", path), r"^total"), (("needs", path, "2.1"), r"^2\.1 Two"),
                       (("taught", path, "a"), r"^a: taught in §1\.1")):
        code, out = run(cur, "us_plan.py", *args)
        check(code == 0 and any(re.match(want, l) for l in out), (args, out))
    code, out = run(cur, "us_plan.py", "from-chapters", path, "--force")
    check(code == 0 and out == ["wrote PLAN.md: 1 chapters, 1 sections"], out)

# ---------------------------------------------------------------- a plan without the lines: as before


def old_scripts():
    """The scripts as they were before this stage (git HEAD), in a temp folder; None when git cannot give them."""
    home = os.path.join(TMP, "before")
    if os.path.isdir(home):
        return home
    for name in os.listdir(SCRIPTS):
        if name.endswith(".py"):
            proc = subprocess.run(["git", "show", "HEAD:scripts/" + name], cwd=ROOT, capture_output=True, text=True)
            if proc.returncode:
                return None
            write(os.path.join(home, "scripts", name), proc.stdout)
    for name in ("rules", "AGENTS.md", "understudy.yaml"):
        src = os.path.join(ROOT, name)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(home, name))
    return home


@test
def a_plan_without_the_lines_gives_the_same_output_as_before():
    home = old_scripts()
    path = book("b", plan_text("", (("One", "", "a"), ("Two", "", "b"))) + "2.2 More | needs: a\n",
                {1: "# Chapter 1: One\n\n## 1.1 One\n\nAn a is a thing.\n"})
    bad = book("c", "# B\nfor: t\n\n### 1 One\n1.1 A | needs: zz\nheld alpha\n")
    for args in (("check", path), ("brief", path, "2"), ("status", path), ("next", path), ("cost", path),
                 ("needs", path, "2.2"), ("check", bad)):
        new = run(curriculum(), "us_plan.py", *args)
        check("Traceback" not in "\n".join(new[1]), new)
        if home is None:                       # no git: the existing suites are the proof
            continue
        env = dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private"))
        proc = subprocess.run([sys.executable, os.path.join(home, "scripts", "us_plan.py")] + list(args),
                              capture_output=True, text=True, env=env)
        old = (proc.returncode, [l for l in (proc.stdout + proc.stderr).splitlines() if not l.startswith("warning:")])
        if args[0] == "cost":                  # its column is now named "reading h" (was "study h")
            new, old = (new[0], [l.split() for l in new[1][1:]]), (old[0], [l.split() for l in old[1][1:]])
        check(new == old, (args, old, new))
    if home is not None:
        code, out = run(curriculum(), "us_check.py", path, "1")
        proc = subprocess.run([sys.executable, os.path.join(home, "scripts", "us_check.py"), path, "1"],
                              capture_output=True, text=True,
                              env=dict(os.environ, UNDERSTUDY_PRIVATE=os.path.join(TMP, "private")))
        check(out == proc.stdout.splitlines(), (out, proc.stdout))

# ---------------------------------------------------------------- us_check.py: curriculum words


def chapter(n, title, body):
    return "# Chapter %d: %s\n\n## %d.1 %s\n\n%s\n" % (n, title, n, title, body)


def word_flags(out):
    return [l for l in out if "curriculum word" in l]


@test
def check_flags_a_tagged_word_the_chapter_never_writes():
    cur = curriculum()
    text = plan_text("later: alpha 5-6", (("One", "from: alpha 1-2", "loop"), ("Two", "from: alpha 3-4", "b")))
    body1 = "A pod runs. Two Pods run. The Desired State is kept. <!-- teaches: loop = exchange argument -->"
    path = book("b", text, {1: chapter(1, "One", body1), 2: chapter(2, "Two", "Nothing named here.")})
    code, out = run(cur, "us_check.py", path, "1")
    check(word_flags(out) == ["FLAG chapters/01-chapter-1.md curriculum word 'exchange argument' (alpha step 1) is not "
                              "in this chapter: teach it where the step is taught"], out)     # '(met thing)': met only
    code, out = run(cur, "us_check.py", path, "2")
    check(word_flags(out) == ["FLAG chapters/02-chapter-2.md curriculum word 'reconcile' (alpha step 4) is not in this "
                              "chapter: teach it where the step is taught"], out)   # 'loop' was taught in chapter 1
    write(os.path.join(path, "chapters", "02-chapter-2.md"), chapter(2, "Two", "We reconcile; reconciles; Exchange "
                                                                              "Arguments."))
    code, out = run(cur, "us_check.py", path, "2")
    check(word_flags(out) == [], out)
    code, out = run(cur, "us_check.py", path)
    check(len(word_flags(out)) == 1 and "'exchange argument'" in word_flags(out)[0], out)


@test
def check_flags_each_word_once_and_only_with_a_from_line():
    cur = curriculum({"alpha": card("alpha", words="[1] shared word; [2-6] a1"),
                      "gamma": card("gamma", words="[1] shared word, other; [2-6] g1")})
    text = plan_text("later: alpha 2-6; gamma 2-6", (("One", "from: alpha 1; gamma 1", "a"),))
    path = book("b", text, {1: chapter(1, "One", "Some other text, and others.")})
    code, out = run(cur, "us_check.py", path, "1")
    check(word_flags(out) == ["FLAG chapters/01-chapter-1.md curriculum word 'shared word' (alpha step 1) is not in "
                              "this chapter: teach it where the step is taught"], out)
    path = book("b", plan_text("", (("One", "", "a"),)), {1: chapter(1, "One", "Nothing.")})
    code, out = run(cur, "us_check.py", path, "1")
    check(word_flags(out) == [], out)
    path = book("b", text, {1: chapter(1, "One", "Nothing.")})
    code, out = run(None, "us_check.py", path, "1")
    check(word_flags(out) == [], out)


def main():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok    " + fn.__name__)
            passed += 1
        except Exception as exc:  # noqa: BLE001
            print("FAIL  %s: %s" % (fn.__name__, str(exc).replace("\n", " | ")[:900]))
            failed += 1
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
