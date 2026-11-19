"""Check a book's PLAN.md, brief the writer of a chapter, and track progress.

  us_plan.py check BOOK            validate PLAN.md
  us_plan.py brief BOOK N          one-page brief for the writer of chapter N
  us_plan.py taught BOOK WORD...   where each word or phrase is taught, if anywhere
  us_plan.py next BOOK             what to write next
  us_plan.py status BOOK           one row per chapter
  us_plan.py mark BOOK N reviewed [--false A] [--stuck B] [--open "text"]
                                   record that chapter N is reviewed (or: written, to undo), and add a
                                   line to the book's REVIEW.md: suspects found false, places stuck, left open;
                                   stamps h= on each <!-- checked: --> mark that has none, records the facts
  us_plan.py mark BOOK N restamp   stamp every checked mark of chapter N afresh (after a deliberate re-check)
  us_plan.py mark BOOK pass N      record that the book pass (us_check.py BOOK --digest) covered chapters 1 to N
  us_plan.py from-chapters BOOK [--force] [--title T] [--for F] [--run R]
                                   build PLAN.md from existing chapter files
  us_plan.py place BOOK N...       placement: mark chapters N... `skip` in private/route.md and claimed at
                                   level 1 in private/levels.yaml (safe to run twice)
  us_plan.py needs BOOK N.M...     the fewest sections to write so that N.M... can be read: they and, in turn,
                                   the unwritten sections teaching what they need; words and tokens to write
  us_plan.py cost BOOK [N]         per chapter: words, hours of study, minutes and tokens of writing; a total
  us_plan.py move BOOK N --to M    move chapter N to position M and renumber (only before any chapter is written)

next (and us_autopilot.py, us_resume.py) take chapters in the order of private/route.md, whose lines
name them as `BOOK N` (`- learn-git 3 why`), leaving out those marked skip; chapters the route does
not name come after, in plan order. No route for the book: plan order. Route lines:
  - BOOK N Title                     the whole chapter N (also BOOK/N)
  - BOOK N Title · skip              leave chapter N out
  - BOOK N sections N.A N.B          only those sections of chapter N (also `section`, commas allowed);
                                     us_autopilot.py, which writes whole chapters, leaves such chapters out

PLAN.md's header may hold `env:` lines: NAME=VALUE words set for every program and terminal session
of the book, so that what they print is the same on every run, e.g. fixed dates for git commits:
  env: GIT_AUTHOR_DATE=2026-01-05T10:00:00 GIT_COMMITTER_DATE=2026-01-05T10:00:00
and `run: console` (a terminal tool), a language or `none` (nothing to run), `kind: language|tool|framework|
system|skill`, `state: docker`, `timeout: N` (seconds),
`check: COMMAND` and `mask: REGEX` (both repeatable). Section fields: teaches:, needs:, level:,
story, practice, short (one command or small idea, 300 to 700 words) and fig (a figure is required).

A plan made from the curriculum (curriculum/FORMAT.md) may hold, above the first chapter,
  held: CARD STEPS; CARD STEPS        steps the learner has shown (STEPS like 1-3 or 2,5; none: all)
  later: CARD STEPS                   steps left for a later book ((a reason in brackets) is ignored,
                                      but "(book 2)" marks a later book of a series)
and, directly under a chapter's `### N Title` line, `from: CARD STEPS; CARD STEPS`: the steps it teaches.
check then accounts for every step of every card these lines touch, and for the cards those need; with a
`track:` line the plan is one book: at most 16 chapters;
brief adds the curriculum's notes for the chapter's steps.
"""
import collections
import datetime
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402

KINDS = ("language", "tool", "framework", "system", "skill")   # the PLAN.md header line `kind:`
BRIEF_CAP = 1000
WRAP = 100
CARRY_CAP = 150          # words of "From earlier chapters"
OLDER_CAP = 35           # of those, for each chapter before the last one
SPINE_LINES = ("Picture", "Running example", "Left at end")

# ---------------------------------------------------------------- check


def check_plan(plan):
    """All plan problems: (errors, warnings), each a list of (line, message)."""
    book = os.path.dirname(plan.path)
    env = bf.plan_env_words(book) if plan.path else []
    lines = bf.read_text(plan.path).splitlines() if plan.path else []
    skip = {n for n, _ in env} | {n for n, l in enumerate(lines, 1) if bf.EVERYDAY_RE.match(l)}  # read elsewhere
    errors, warnings = [e for e in plan.errors if e[0] not in skip], []
    errors += [(n, "env: takes NAME=VALUE words, such as env: TZ=UTC; '%s' is not one" % (w or "unclosed quote"))
               for n, w in env if not (w and bf.ENV_WORD.match(w))]
    check_header(plan, lines, errors)
    check_numbering(plan, errors)
    check_ideas(plan, errors)
    for ch in plan.chapters:
        check_chapter_shape(ch, errors, warnings)
    check_load(plan, warnings)
    if not plan.audience or plan.audience.upper().startswith("TODO"):
        warnings.append((1, "no 'for:' line; say who the book is for"))
    return sorted(errors), sorted(warnings)


def run_names():
    """Names `run:` may take: console and the languages (and their aliases) us_run.py knows."""
    try:
        import us_run
        return {us_run.CONSOLE} | set(us_run.LANGS) | set(us_run.ALIASES)
    except Exception:             # us_run.py cannot be loaded: its names as of this writing
        return {"console", "c", "cpp", "python", "bash", "sh", "javascript", "java",
                "c++", "cxx", "py", "python3", "js", "node", "shell"}


def check_header(plan, lines, errors):
    """The header lines: run:, state:, timeout:, check:, mask:."""
    run = plan.run.strip().lower()
    at = next((n for n, l in enumerate(lines, 1) if re.match(r"\s*run\s*:", l, re.I)), 1)
    if run and not run.startswith("todo") and run != "none" and run not in run_names():
        errors.append((at, "run: '%s' is not known; write run: none (nothing to run), run: console for a terminal tool, or one of: %s"
                       % (plan.run, ", ".join(sorted(run_names() - {"console"})))))
    for n, v in plan.meta.get("kind", []):
        if v.lower() not in KINDS:
            errors.append((n, "kind: '%s' is not known; write one of: %s" % (v, ", ".join(KINDS))))
    for n, v in plan.meta.get("state", []):
        if v.lower() != "docker":
            errors.append((n, "state: '%s' is not known; the only one is state: docker" % v))
    for n, v in plan.meta.get("timeout", []):
        if not re.fullmatch(r"\d+(\.\d+)?", v) or float(v) <= 0:
            errors.append((n, "timeout: '%s' is not a number of seconds; write timeout: 120" % v))
    for n, v in plan.meta.get("check", []):
        if not v:
            errors.append((n, "check: has no command; write check: docker version, or drop the line"))
    for n, v in plan.meta.get("mask", []):
        try:
            re.compile(v) if v else None
        except re.error as e:
            errors.append((n, "mask: '%s' is not a valid pattern (%s); fix it or drop the line" % (v, e)))
        if not v:
            errors.append((n, "mask: has no pattern; write mask: REGEX, or drop the line"))


def check_numbering(plan, errors):
    """Chapters run 1,2,3 and each chapter's sections run N.1, N.2, ..."""
    for i, ch in enumerate(plan.chapters, 1):
        if ch.number != i:
            errors.append((ch.line, "chapter %d follows chapter %d; renumber it %d" % (ch.number, i - 1, i)))
        for j, sec in enumerate(ch.sections, 1):
            want = "%d.%d" % (ch.number, j)
            if sec.number != want:
                errors.append((sec.line, "%s is section %d of chapter %d; renumber it %s" % (sec.number, j, ch.number, want)))


def check_ideas(plan, errors):
    """Ids unique; needs taught in an earlier chapter; levels 1 to 5."""
    first = {}
    for sec in plan.sections():
        if not 1 <= sec.level <= 5:
            errors.append((sec.line, "%s: level %d; use 1 to 5" % (sec.number, sec.level)))
        for idea in sec.teaches:
            if idea in first:
                errors.append((sec.line, "%s: idea '%s' already taught in %s; rename it or drop it here" % (sec.number, idea, first[idea].number)))
            else:
                first[idea] = sec
    for sec in plan.sections():
        for idea in sec.needs:
            check_need(sec, idea, first.get(idea), errors)


def check_need(sec, idea, teacher, errors):
    """One `needs:` id must be taught in an earlier chapter."""
    if teacher is None:
        errors.append((sec.line, "%s needs '%s', taught nowhere; add it to a teaches: in an earlier chapter or drop it" % (sec.number, idea)))
    elif teacher.chapter == sec.chapter:
        errors.append((sec.line, "%s needs '%s', taught in the same chapter (%s); drop it, section order covers it" % (sec.number, idea, teacher.number)))
    elif teacher.chapter > sec.chapter:
        errors.append((sec.line, "%s needs '%s', taught later in %s; move that idea earlier or drop the need" % (sec.number, idea, teacher.number)))


def check_chapter_shape(ch, errors, warnings):
    """At most one story; 4 to 12 sections (usually 5 to 9) and a closing practice (warnings)."""
    stories = [s for s in ch.sections if s.kind == "story"]
    for extra in stories[1:]:
        errors.append((extra.line, "%s: second story in chapter %d (first is %s); make it a lesson" % (extra.number, ch.number, stories[0].number)))
    n = len(ch.sections)
    if n < 4 or n > 12:
        fix = "split the chapter" if n > 12 else "add sections or merge with a neighbour"
        warnings.append((ch.line, "chapter %d has %d sections (usually 5 to 9); %s" % (ch.number, n, fix)))
    if ch.sections and ch.sections[-1].kind != "practice":
        warnings.append((ch.sections[-1].line, "chapter %d does not end with a practice section; add 'N.M Practice: ... | practice'" % ch.number))


def check_load(plan, warnings):
    """Five new ideas a section at most; never three hard sections (level 4 or 5) in a row."""
    run = []
    for sec in plan.sections():
        if len(sec.teaches) > 5:
            warnings.append((sec.line, "%s teaches %d ideas; five at most: split the section" % (sec.number, len(sec.teaches))))
        run = run + [sec] if sec.level >= 4 else []
        if len(run) == 3:
            warnings.append((sec.line, "%s are level 4 or 5 in a row; put an easier section between them"
                             % ", ".join(s.number for s in run)))


def cmd_check(book):
    """Print problems, or 'plan ok: ...'; exit 1 on errors."""
    plan = need_plan(book)
    errors, warnings = check_plan(plan)
    counts = check_curriculum(book, plan, errors, warnings)
    budget = check_budget(book, plan, errors)
    series = check_one_book(book, plan, errors)
    errors, warnings = sorted(errors), sorted(warnings)
    for line, msg in errors:
        print("error PLAN.md:%d: %s" % (line, msg))
    for line, msg in warnings:
        print("warn PLAN.md:%d: %s" % (line, msg))
    if errors:
        return 1
    ideas = sum(len(s.teaches) for s in plan.sections())
    print("plan ok: %d chapters, %d sections, %d ideas" % (len(plan.chapters), len(plan.sections()), ideas) +
          (", %d curriculum steps taught, %d held, %d later" % counts if counts else "") +
          (", about %.0f of %g budget hours (%s)" % (budget, plan.budget[1], "study and practice, by the roadmap" if any(
              c.from_refs for c in plan.chapters) and curriculum() else "reading and study, as cost counts it")
           if budget is not None else "") +
          (", %d steps for later books" % series if series else ""))
    return 0

BUDGET_SLACK = 0.15       # a plan may run this far over its budget: line
BOOK_CHAPTERS = 16        # one book of a plan with a track: line


def plan_map(cur, plan):
    """The track map of the plan's first track: line, or None."""
    return next((m for m in (cur.find_map(ref) for _, ref, _ in plan.track) if m), None) if cur else None


def check_one_book(book, plan, errors):
    """A plan with a track: line is one book: at most 16 chapters. Returns how many steps later: lines leave for later books ('(book 2)')."""
    if not plan.track:
        return 0
    cur = curriculum()
    if len(plan.chapters) > BOOK_CHAPTERS:
        errors.append((plan.track[0][0], "this is more than one book (%d chapters): a book has at most %d chapters; "
                                         "group more steps in a chapter, leave what the goal can do without under "
                                         "later:, and only if the goal still does not fit make it a series with "
                                         "later: ... (book 2)" % (len(plan.chapters), BOOK_CHAPTERS)))
    return len(series_steps(cur, plan)) if cur else 0


def series_steps(cur, plan):
    """(card, step) pairs on later: lines that name a later book of the series."""
    return {(i, n) for ln, i, st in plan.later if ln in plan.later_books and i in cur.cards
            for n in (card_numbers(cur, i) if st is None else st)}


def check_budget(book, plan, errors):
    """ERROR when the plan's study hours (plan_hours) pass `budget:` by more than 15%; returns the hours, or None
    when the plan has no budget: line."""
    if not plan.budget:
        return None
    line, hours = plan.budget
    need = plan_hours(book, plan)
    if need > hours * (1 + BUDGET_SLACK):
        errors.append((line, "the plan needs about %.0f hours of study; the learner has %g (budget:): move steps to "
                             "later: or cut sections, keeping every card the goal names" % (need, hours)))
    return need


def plan_hours(book, plan):
    """Study hours of the plan. With from: lines and a curriculum: each card's track-map Hours scaled by the share
    of its steps on from: lines (as us_path.py spine counts them), plus the cost hours of the chapters with no
    from: line and of the chapters of cards no map gives hours for. Otherwise: the cost total."""
    written = all_written(book, plan)
    cur = curriculum() if any(c.from_refs for c in plan.chapters) else None
    if cur is None:
        return chapter_cost(plan.sections(), written)[2]
    import us_path
    taught, tmap = {}, plan_map(cur, plan)
    for c in plan.chapters:
        for ident, steps in c.from_refs:
            have = card_numbers(cur, ident) if ident in cur.cards else []
            taught.setdefault(ident, set()).update(n for n in (have if steps is None else steps) if n in have)
    total, costed = 0, {c.number for c in plan.chapters if not c.from_refs}
    for ident, steps in taught.items():
        hours = us_path.card_hours(cur, ident, sorted(steps), tmap)[0] if ident in cur.cards else None
        if hours is None:
            costed |= {c.number for c in plan.chapters if any(i == ident for i, _ in c.from_refs)}
        else:
            total += hours
    secs = [s for c in plan.chapters if c.number in costed for s in c.sections]
    return total + (chapter_cost(secs, written)[2] if secs else 0)

# ---------------------------------------------------------------- the curriculum's steps (from:, held:, later:)


def curriculum():
    """The curriculum (us_path.Curriculum), or None when there is no curriculum folder."""
    import us_path
    return us_path.Curriculum() if os.path.isdir(us_path.curriculum_dir()) else None


def card_numbers(cur, ident):
    """The step numbers of a card."""
    import us_path
    return [n for n, _, _ in us_path.card_steps(cur.cards[ident])]


def needs_of(cur, ident):
    """The entries of a card's needs: line, each a list of alternatives (any one will do) that have cards."""
    import us_path
    entries = [[a for a in e if a in cur.cards] for e in us_path.need_entries(cur.cards[ident].get("needs"))]
    return [e for e in entries if e]


def shelf_teaches(book):
    """Card ids on a from: line of another book's PLAN.md on the same shelf (the book's folder's parent)."""
    found = set()
    for other in bf.list_books(os.path.dirname(os.path.abspath(book).rstrip(os.sep))):
        if os.path.abspath(other) == os.path.abspath(book) or not os.path.exists(os.path.join(other, "PLAN.md")):
            continue
        found |= {i for c in bf.load_plan(other).chapters for i, _ in c.from_refs}
    return found


def check_curriculum(book, plan, errors, warnings):
    """Account for every step of every card the plan touches; returns (taught, held, later) counts, or None
    when the plan has no from:, held: or later: line or there is no curriculum folder."""
    cur = curriculum() if plan.uses_curriculum() or plan.track else None
    if cur is None:
        return None
    where, sets = {}, {"from": set(), "held": set(), "later": set()}
    first = {}                                    # card -> first chapter that teaches it
    chapter_of = {}                               # (card, step) -> first chapter that teaches it
    for line, kind, ident, steps in plan.curriculum_refs():
        if ident not in cur.cards:
            errors.append((line, "no card '%s' in the curriculum; fix the id (python3 scripts/us_path.py find %s)"
                           % (ident, ident.replace("-", " "))))
            continue
        have = card_numbers(cur, ident)
        gone = [n for n in steps or [] if n not in have]
        if gone:
            errors.append((line, "%s has steps 1 to %d; step %s does not exist" % (ident, len(have),
                                                                                 ", ".join(map(str, gone)))))
        where[ident] = min(where.get(ident, line), line)
        for n in [n for n in (have if steps is None else steps) if n in have]:
            sets[kind.split()[0]].add((ident, n))
            if kind.startswith("from"):
                ch = int(kind.split()[1])
                first[ident] = min(first.get(ident, ch), ch)
                chapter_of[(ident, n)] = min(chapter_of.get((ident, n), ch), ch)
    for ident, line in sorted(where.items(), key=lambda x: (x[1], x[0])):
        have = card_numbers(cur, ident)
        taught, held, later = [{n for i, n in sets[k] if i == ident} for k in ("from", "held", "later")]
        missing = [n for n in have if n not in taught | held | later]
        if missing:
            errors.append((line, "%s: step%s %s %s in no from:, held: or later: line; add them to a chapter's from: "
                                 "line, or to held: (the learner has shown it) or later: (left for a later book)"
                           % (ident, "" if len(missing) == 1 else "s", ", ".join(map(str, missing)),
                              "is" if len(missing) == 1 else "are")))
        both = sorted((taught & (held | later)) | (held & later))
        if both:
            errors.append((line, "%s: step%s %s %s in more than one of from:, held: and later:; a step is taught, "
                                 "held or left for later: keep it in one" % (
                                     ident, "" if len(both) == 1 else "s", ", ".join(map(str, both)),
                                     "is" if len(both) == 1 else "are")))
    touched, elsewhere = set(where), None
    for ident in sorted(first, key=lambda i: (where[i], i)):
        for need in needs_of(cur, ident):
            if any(a in touched for a in need):
                continue
            elsewhere = shelf_teaches(book) if elsewhere is None else elsewhere
            if not any(a in elsewhere for a in need):
                errors.append((where[ident], "%s needs %s: teach its steps here, or list them under held: (the learner "
                                             "showed they have them) or later:" % (ident, " or ".join(need))))
    lines = {c.number: c.from_line for c in plan.chapters}
    held = {i for i, _ in sets["held"]}
    for ident in sorted(first):
        for need in needs_of(cur, ident):
            if any(a in touched and a not in first or a in held for a in need):
                continue                          # some of it held, or all left for later: the order may be meant
            taught = sorted((first[a], a) for a in need if a in first)
            if taught and taught[0][0] > first[ident]:
                warnings.append((lines[first[ident]], "note: %s is first taught in chapter %d, before %s (chapter %d), "
                                                      "which it needs: is this order meant?" % (
                                                          ident, first[ident], taught[0][1], taught[0][0])))
        order = sorted((n, c) for (i, n), c in chapter_of.items() if i == ident)
        for k, (n, c) in enumerate(order):
            low = [m for m, d in order[:k] if d > c]
            if low:
                warnings.append((lines[c], "note: %s step %d is taught in chapter %d, before step %d (chapter %d); "
                                           "the card teaches them the other way round: is this order meant?" % (
                                               ident, n, c, low[0], chapter_of[(ident, low[0])])))
                break
    check_track(book, plan, cur, touched, sets, errors, warnings, series_steps(cur, plan))
    check_deep_room(plan, cur, warnings)
    return tuple(len(sets[k]) for k in ("from", "held", "later")) if plan.uses_curriculum() else None


def check_deep_room(plan, cur, warnings):
    """A note when a chapter's from: line holds a deep step of a card with three or more other steps."""
    import us_path
    for c in plan.chapters:
        held = [(i, n) for i, steps in c.from_refs if i in cur.cards
                for n in (card_numbers(cur, i) if steps is None else steps)]
        for ident, n in held:
            if n in (us_path.deep_steps(cur.cards[ident]) or []) and len(held) - 1 >= 3:
                warnings.append((c.from_line, "note: chapter %d holds the deep step %s %d with %d other steps: give it "
                                              "room" % (c.number, ident, n, len(held) - 1)))


def check_track(book, plan, cur, touched, sets, errors, warnings, series=()):
    """The `track:` lines: the map and its rows exist; every goal row with a card is accounted for here or
    taught by another book on the shelf; a note for a goal card this book only leaves for later."""
    elsewhere = None
    for line, ref, rows in plan.track:
        tmap = cur.find_map(ref)
        if tmap is None:
            errors.append((line, "no track map '%s'; tracks: %s" % (ref, ", ".join(m.ref() for m in cur.maps) or "none")))
            continue
        import us_path
        subjects = [us_path.subject_of(c[1]) for _, c in tmap.rows() if len(c) > 1]
        gone = [n for n in rows or [] if not 1 <= n <= len(subjects)]
        if gone:
            errors.append((line, "%s has rows 1 to %d; row %s does not exist" % (ref, len(subjects),
                                                                              ", ".join(map(str, gone)))))
        for n in [n for n in (rows or range(1, len(subjects) + 1)) if 1 <= n <= len(subjects)]:
            ident, planned = subjects[n - 1]
            if planned or ident not in cur.cards:
                continue
            if ident not in touched:
                elsewhere = shelf_teaches(book) if elsewhere is None else elsewhere
                if ident not in elsewhere:
                    errors.append((line, "the goal's track names %s (row %d of %s): teach its steps in a chapter, or "
                                         "account for them under held: or later:" % (ident, n, ref)))
            elif not any(i == ident for k in ("from", "held") for i, _ in sets[k]) and \
                    any(i == ident for i, _ in sets["later"]) and \
                    not all((ident, n) in series for n in card_numbers(cur, ident)):   # left for book 2: taught there
                errors.append((line, "%s is in the goal's rows (track:) but this book teaches none of it: teach at "
                                     "least the steps the goal cannot do without" % ident))


def need_plan(book):
    """The book's plan, or exit with a one-line message."""
    plan = bf.load_plan(book)
    if plan is None:
        sys.exit("no PLAN.md in %s; write one or run: us_plan.py from-chapters %s" % (book, book))
    return plan

# ---------------------------------------------------------------- brief


def book_ideas(book, plan):
    """Map idea id -> {'term', 'words', 'definition', 'section'}: the marker's words, else the id in words."""
    ideas = {i: {"term": bf.humanise(i), "words": [], "definition": "", "section": sec.number}
             for i, sec in plan.teacher().items()}
    for ch in plan.chapters:
        path = bf.chapter_path(book, ch.number)
        doc = bf.parse_chapter(bf.read_text(path)) if path else None
        for t in [t for sec in doc.sections for t in sec.teaches] if doc else []:
            if t.id in ideas and not ideas[t.id]["words"]:
                ideas[t.id].update(words=t.words, term=(t.words or [ideas[t.id]["term"]])[0],
                                   definition=bf.definition(t, doc.lines, cap=10 ** 6))
    return ideas


def chapter_terms(ideas, ch, where=False):
    """'N: a, b, c' for the ideas chapter ch teaches (with where: 'a §N.M'), or None."""
    terms = list(dict.fromkeys(ideas[i]["term"] + (" §" + ideas[i]["section"] if where else "")
                               for sec in ch.sections for i in sec.teaches))
    return "%d: %s" % (ch.number, ", ".join(terms)) if terms else None


def carried(book, n):
    """'From earlier chapters': the chapter before n gives its picture, the first line of its running
    example and what it left; the two before that give only what they left (OLDER_CAP words each).
    CARRY_CAP words in all, near enough; a long line is cut with an ellipsis, no chapter is dropped."""
    out, room = [], CARRY_CAP
    for k in range(n - 1, max(0, n - 4), -1):        # nearest first: it gets the room it needs
        path = os.path.join(book, "spines", "%d.md" % k)
        if not os.path.exists(path):
            if bf.chapter_path(book, k):
                out.append("- chapter %d: no spine; look in its last section with us_find.py" % k)
                room -= len(out[-1].split())
            continue
        text = bf.read_text(path)
        labels = SPINE_LINES if k == n - 1 else SPINE_LINES[-1:]
        found = [re.search(r"(?:^|\s)%s:[ \t]*(.*)" % label, text, re.M) for label in labels]
        parts = [(label + ":").split() + m.group(1).split() for label, m in zip(labels, found) if m]
        cap = max(12, room - OLDER_CAP * (k - max(1, n - 3))) if k == n - 1 else max(12, min(OLDER_CAP, room))
        for part in parts:                           # too long: the picture gives way first, what was left last
            over = 3 + sum(len(x) for x in parts) - cap
            if over > 0 and len(part) > 6:
                del part[max(5, len(part) - over - 1):]
                part.append("…")
        words = ["-", "chapter", "%d:" % k] + [w for part in parts for w in part]
        out.append(" ".join(words))
        room -= len(words)
    return ["", "From earlier chapters:"] + out[::-1] if out else []


def make_brief(book, plan, n):
    """The brief, at most BRIEF_CAP words. Kept first: the ideas this chapter needs, then the words of the
    chapters those come from, then the nearest earlier chapters, then the next later ones."""
    ideas = book_ideas(book, plan)
    ch = plan.chapter(n)
    env = ["env: " + e.strip() for e in bf.ENV_RE.findall(bf.read_text(plan.path))] if plan.path else []
    sheet = os.path.join(book, "BOOK.md")
    sheet = bf.read_text(sheet).strip().splitlines() if os.path.exists(sheet) else []
    left = [l for l in sheet if l.startswith("Left at end of chapter")]
    sheet = [l for l in sheet if l not in left[:-2]] + [""] if sheet else []      # the last two chapters' state is enough
    meta = ["%s: %s" % (k, v) for k in ("kind", "state", "timeout") for _, v in plan.meta.get(k, [])]
    head = sheet + ["# %s" % plan.title, "for: %s" % plan.audience, "run: %s" % plan.run] + meta + env + ["", ch.raw] + \
        [s.raw + section_notes(s) for s in ch.sections] + ([] if sheet else carried(book, n))
    needed = list(dict.fromkeys(i for sec in ch.sections for i in sec.needs if i in ideas))
    prev = bf.chapter_path(book, n - 1) if n > 1 else None
    nxt = plan.chapter(n + 1)
    tail = (["", "Chapter %d closed with:" % (n - 1)] + textwrap.wrap(bf.closing_paragraph(bf.read_text(prev)), WRAP)
            if prev else []) + ["", "Next chapter: %d %s" % (nxt.number, nxt.title) if nxt else "This is the last chapter."]
    has = {i: "- %s §%s" % (ideas[i]["term"], ideas[i]["section"]) for i in needed}
    earlier = [c for c in plan.chapters if c.number < n]
    sources = {int(ideas[i]["section"].split(".")[0]) for i in needed}
    order = sorted(earlier, key=lambda c: (c.number not in sources, -c.number))
    later = [c for c in plan.chapters if c.number > n]
    taught, coming = {}, {}

    def text():
        out = head + (["", "The reader already has:"] + list(has.values()) if has else [])
        lines = [taught[c.number] for c in earlier if c.number in taught]
        left = [c.number for c in earlier if c.number not in taught and chapter_terms(ideas, c)]
        if lines:
            out += ["", "Words already taught (use freely):"] + [l for x in lines for l in wrap(x)]
            out += ["(chapters %s left out)" % ", ".join(map(str, left))] if left else []
        lines = [coming[c.number] for c in later if c.number in coming]
        out += ["", "Not yet taught (avoid, or promise the section):"] + [l for x in lines for l in wrap(x)] if lines else []
        return "\n".join(out + tail)

    def fits(where, key, value):
        where[key] = value
        if len(text().split()) > BRIEF_CAP:
            del where[key]
    for i in needed:
        if ideas[i]["definition"]:
            fits(has, i, has[i] + ": " + ideas[i]["definition"])
    for c in order:
        if chapter_terms(ideas, c):
            fits(taught, c.number, chapter_terms(ideas, c))
    for c in later:
        if chapter_terms(ideas, c):
            fits(coming, c.number, chapter_terms(ideas, c, where=True))
    return text()


def section_notes(sec):
    """What the writer must know beyond the plan line: a required figure, a short lesson."""
    notes = (["short: one command or one small idea, 300 to 700 words, ending in Check yourself"]
             if sec.kind == "short" else []) + (["figure required (<!-- fig: ... -->)"] if sec.fig else [])
    return "  (%s)" % "; ".join(notes) if notes else ""


def wrap(line):
    return textwrap.wrap(line, WRAP, subsequent_indent="   ")


def cmd_taught(book, words):
    """One line per word or phrase: the first section that teaches it (by idea id, its words, or a title)."""
    plan = need_plan(book)
    ideas = book_ideas(book, plan)
    last = plan.chapters[-1].number if plan.chapters else 0
    for word in words:
        low = word.lower()
        want = {low, low + "s", low[:-1] if low.endswith("s") else low}
        hits = [(bf.section_key(v["section"]), v["section"], i) for i, v in ideas.items()
                if want & ({i.lower(), bf.humanise(i)} | {w.lower() for w in v["words"]})]
        hits += [(bf.section_key(sec.number), sec.number, sec.teaches[0] if sec.teaches else 'title "%s"' % sec.title)
                 for sec in plan.sections()
                 if any(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(w), sec.title.lower()) for w in want)]
        if hits:
            _, number, why = min(hits)
            print("%s: taught in §%s (%s)" % (word, number, why))
        else:
            print("%s: not taught in chapters 1-%d" % (word, last))
    return 0


def cmd_brief(book, n):
    """Print the brief for chapter n."""
    plan = need_plan(book)
    if plan.chapter(n) is None:
        sys.exit("chapter %d is not in the plan" % n)
    print(make_brief(book, plan, n))
    refs = plan.chapter(n).from_refs
    if refs:
        import us_path
        cur = curriculum()
        print("\n" + us_path.NOTES_HEAD)
        print("\n".join(us_path.chapter_notes(refs, cur) if cur else ["(no curriculum folder: no notes)"]))
    return 0

# ---------------------------------------------------------------- progress


def written_sections(book, ch):
    """Section numbers already in chapter ch's file."""
    path = bf.chapter_path(book, ch.number)
    if not path:
        return [], 0
    doc = bf.parse_chapter(bf.read_text(path))
    return [s.number for s in doc.sections], sum(s.words for s in doc.sections)


def route_path():
    return os.path.join(bf.private_dir(), "route.md")


def route_chapter(book, line):
    """The chapter number a route.md line names for this book (`learn-git 3` or `learn-git/3`), or None."""
    m = re.search(r"(?<![\w-])%s[ /](\d+)\b" % re.escape(os.path.basename(book.rstrip(os.sep))), line)
    return int(m.group(1)) if m else None


def is_skip(line):
    return re.search(r"\bskip\b", line, re.I) is not None


def route_chapters(book, plan):
    """The plan's chapters in the order to take them: the route's order without its `skip` chapters,
    then the chapters it does not name, in plan order. No route for this book: plan.chapters."""
    lines = bf.read_text(route_path()).splitlines() if os.path.exists(route_path()) else []
    named = [(route_chapter(book, l), is_skip(l)) for l in lines if route_chapter(book, l)]
    rank, skip = {}, {n for n, s in named if s}
    for n, _ in named:
        rank.setdefault(n, len(rank))
    return sorted((c for c in plan.chapters if c.number not in skip), key=lambda c: rank.get(c.number, len(rank)))


SECTIONS_RE = re.compile(r"\bsections?\b\s*((?:\d+\.\d+\s*,?\s*)+)", re.I)


def route_sections(book, n):
    """The section numbers the first non-skip route.md line for chapter n names after `sections`
    (`- learn-docker 1 sections 1.2 1.5`, commas allowed), or None: the whole chapter."""
    lines = bf.read_text(route_path()).splitlines() if os.path.exists(route_path()) else []
    for line in lines:
        if route_chapter(book, line) == n and not is_skip(line):
            m = SECTIONS_RE.search(line)
            return re.findall(r"\d+\.\d+", m.group(1)) if m else None
    return None


def next_to_write(book, plan, whole_only=False):
    """(chapter, planned section, written count) of the next unwritten section on the route, or None.
    A chapter whose route line names sections offers only those; whole_only leaves such chapters out."""
    for ch in route_chapters(book, plan):
        picked = route_sections(book, ch.number)
        if picked is not None and whole_only:
            continue
        done = set(written_sections(book, ch)[0])
        todo = [s for s in ch.sections if s.number not in done and (picked is None or s.number in picked)]
        if todo:
            return ch, todo[0], len([s for s in ch.sections if s.number in done])
    return None


def cmd_next(book):
    """Print the next section to write."""
    plan = need_plan(book)
    found = next_to_write(book, plan)
    if not found:
        taken = {c.number for c in route_chapters(book, plan)}
        left = [c.number for c in plan.chapters if c.number not in taken and len(written_sections(book, c)[0]) < len(c.sections)]
        print("all written" + (" (skipped on the route: %s)" % ", ".join(map(str, left)) if left else ""))
        print_pass_due(book, plan)
        return 0
    ch, sec, done = found
    picked = route_sections(book, ch.number)
    if picked is not None:
        have = set(written_sections(book, ch)[0])
        print("chapter %d, section %s (%d of %d route sections written: %s)" % (
            ch.number, sec.number, len([p for p in picked if p in have]), len(picked), " ".join(picked)))
    else:
        print("chapter %d, section %s (%d of %d written)" % (ch.number, sec.number, done, len(ch.sections)))
    print_pass_due(book, plan)
    return 0


def pass_ends(plan):
    """Chapters that close a stretch for the book pass: the last chapter of each part (PLAN.md `## Part`);
    a book with no parts: every fourth chapter and the last one."""
    chs = plan.chapters
    if plan.parts:
        return [c.number for i, c in enumerate(chs) if i + 1 == len(chs) or chs[i + 1].part != c.part]
    return [c.number for i, c in enumerate(chs, 1) if i % 4 == 0 or i == len(chs)]


def pass_due(book, plan, status=None):
    """(A, B) when a reviewed chapter B closes a stretch the book pass has not covered (it covered 1 to A-1),
    else None."""
    status = status or bf.read_status(book)
    done = int(status.get("book_pass", 0) or 0)
    reviewed = {int(k) for k, v in status["chapters"].items() if k.isdigit() and v.get("state") == "reviewed"}
    ends = [b for b in pass_ends(plan) if b > done and b in reviewed]
    return (done + 1, max(ends)) if ends else None


def print_pass_due(book, plan, status=None):
    """One line when a book pass is due."""
    due = pass_due(book, plan, status)
    if due:
        print("book pass due: chapters %d to %d (python3 scripts/us_check.py %s --digest --from %d --to %d; then "
              "us_plan.py mark %s pass %d)" % (due[0], due[1], book, due[0], due[1], book, due[1]))


def chapter_state(book, ch, status):
    """planned, writing, written or reviewed."""
    done, words = written_sections(book, ch)
    planned = {s.number for s in ch.sections}
    if status.get("chapters", {}).get(str(ch.number), {}).get("state") == "reviewed":
        return "reviewed", done, words
    if not done:
        return "planned", done, words
    return ("written" if planned <= set(done) else "writing"), done, words


def cmd_status(book):
    """Print one row per chapter."""
    plan = need_plan(book)
    status = bf.read_status(book)
    print("%-3s %-40s %9s %8s  %s" % ("ch", "title", "sections", "words", "state"))
    for ch in plan.chapters:
        state, done, words = chapter_state(book, ch, status)
        title = ch.title if len(ch.title) <= 40 else ch.title[:37] + "..."
        unrun = not_run(book, ch.number)
        state += ", %d not run" % unrun if unrun else ""
        path = bf.chapter_path(book, ch.number)
        facts = sum(fact_counts(bf.read_text(path).split("\n")).values()) if path else 0
        state += ", facts %d" % facts if facts else ""
        print("%-3d %-40s %4d/%-4d %8s  %s" % (ch.number, title, len(done), len(ch.sections), bf.fmt_int(words), state))
    print_pass_due(book, plan, status)
    return 0


RISK_RE = re.compile(r"<!--\s*risk:")
UNRUN_RE = re.compile(r"<!--\s*code:[^>]*?\bunrun=", re.S)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def not_run(book, n):
    """How many programs and sessions of chapter n's file carry unrun= (could not run on this machine)."""
    path = bf.chapter_path(book, n)
    return len(UNRUN_RE.findall(bf.read_text(path))) if path else 0


def checked_marks(lines):
    """(line number, {'how', 'date', 'ref', 'h'}) of each <!-- checked: --> mark outside code fences."""
    scanned, _ = bf.scan_lines(lines)
    return [(n, bf.parse_checked(lines[n - 1])) for n, kind, _ in scanned
            if kind == "prose" and bf.CHECKED_MARK.search(lines[n - 1])]


def mark_problem(mark):
    """What is wrong with a checked mark, or '' when it is well formed."""
    if mark["how"] not in bf.CHECK_HOWS:
        return "how=%s is not known; write how= one of %s" % (mark["how"] or "(none)", ", ".join(bf.CHECK_HOWS))
    if not mark["date"]:
        return "no date; add date=YYYY-MM-DD (the day it was checked)"
    if not DATE_RE.match(mark["date"]):
        return "date=%s is not YYYY-MM-DD" % mark["date"]
    if mark["how"] == "source" and not mark["ref"]:
        return 'how=source has no ref; add ref="the page or document that proved it"'
    return ""


def fact_counts(lines):
    """{how: count} of the well-formed checked marks, in CHECK_HOWS order."""
    found = collections.Counter(m["how"] for _, m in checked_marks(lines) if not mark_problem(m))
    return {how: found[how] for how in bf.CHECK_HOWS if found[how]}


def stamp_marks(lines, fresh=False):
    """Stamp h= on checked marks that have none (fresh: on every mark), in place; returns how many changed."""
    changed = 0
    for n, mark in checked_marks(lines):
        if mark["h"] and not fresh:
            continue
        h = bf.passage_hash(lines, n)
        if h == mark["h"]:
            continue
        m = bf.CHECKED_MARK.search(lines[n - 1])
        inner = re.sub(r'(^|\s)h=("[^"]*"|\S+)', "", m.group(1)).rstrip()
        lines[n - 1] = lines[n - 1][:m.start(1)] + inner + " h=%s " % h + lines[n - 1][m.end(1):]
        changed += 1
    return changed


def malformed(book, n, lines):
    """Refusal lines for chapter n's malformed checked marks, or []."""
    bad = [(k, mark_problem(m)) for k, m in checked_marks(lines) if mark_problem(m)]
    if not bad:
        return []
    name = os.path.relpath(bf.chapter_path(book, n), book)
    return ["chapter %d has %d malformed checked mark%s; fix %s:" % (n, len(bad), "" if len(bad) == 1 else "s",
                                                                   "it" if len(bad) == 1 else "them")] + \
        ["  %s:%d: %s" % (name, k, why) for k, why in bad]


def record_facts(book, n, lines, entry):
    """Put the chapter's fact counts ({how: n}) and unrun count in its STATUS.json entry."""
    entry.update(facts=fact_counts(lines), unrun=not_run(book, n))


def cmd_restamp(book, n):
    """Stamp every checked mark of chapter n afresh; refuse malformed marks."""
    plan = need_plan(book)
    path = bf.chapter_path(book, n) if plan.chapter(n) else None
    if path is None:
        print("chapter %d is not in the plan or not written" % n)
        return 1
    text = bf.read_text(path)
    lines = text.split("\n")
    bad = malformed(book, n, lines)
    if bad:
        print("\n".join(bad))
        return 1
    changed = stamp_marks(lines, fresh=True)
    if changed:
        bf.write_text(path, "\n".join(lines))
    status = bf.read_status(book)
    entry = status["chapters"].setdefault(str(n), {})
    record_facts(book, n, lines, entry)
    bf.write_status(book, status)
    print("chapter %d: restamped %d of %d checked marks" % (n, changed, len(checked_marks(lines))))
    return 0


def cmd_mark_pass(book, n):
    """Record that the book pass covered chapters 1 to n."""
    plan = need_plan(book)
    if plan.chapter(n) is None:
        print("chapter %d is not in the plan" % n)
        return 1
    status = bf.read_status(book)
    status["book_pass"] = n
    bf.write_status(book, status)
    print("book pass: chapters 1 to %d covered" % n)
    return 0


def cmd_mark(book, n, state, notes=None):
    """Set chapter n's state in STATUS.json; only a fully written chapter can be marked."""
    plan = need_plan(book)
    ch = plan.chapter(n)
    if ch is None:
        print("chapter %d is not in the plan" % n)
        return 1
    done, words = written_sections(book, ch)
    missing = [s.number for s in ch.sections if s.number not in done]
    if missing:
        print("chapter %d is not fully written (%d of %d; next %s); write it before marking it %s" % (
            n, len(ch.sections) - len(missing), len(ch.sections), missing[0], state))
        return 1
    path = bf.chapter_path(book, n)
    text = bf.read_text(path)
    lines = text.split("\n")
    risks = len(RISK_RE.findall(text))
    if state == "reviewed" and risks:
        print("chapter %d still has %d risk note%s (<!-- risk: -->); settle each and turn it into a "
              "<!-- checked: how=... date=... --> mark: python3 scripts/us_check.py %s %d --risks"
              % (n, risks, "" if risks == 1 else "s", book, n))
        return 1
    stamped = 0
    if state == "reviewed":
        bad = malformed(book, n, lines)
        if bad:
            print("\n".join(bad))
            return 1
        stamped = stamp_marks(lines)
        if stamped:
            bf.write_text(path, "\n".join(lines))
    status = bf.read_status(book)
    entry = status["chapters"].setdefault(str(n), {})
    entry.update(state=state, sections=done, planned=len(ch.sections), words=words)
    if state == "reviewed":
        record_facts(book, n, lines, entry)
    bf.write_status(book, status)
    if state == "reviewed":
        path = os.path.join(book, "REVIEW.md")
        line = "- %s chapter %d reviewed" % (datetime.date.today().isoformat(), n) + "".join(
            ", %s %s" % (k, v) for k, v in (("false", (notes or {}).get("--false")), ("stuck", (notes or {}).get("--stuck"))) if v)
        line += "; open: %s" % notes["--open"] if (notes or {}).get("--open") else ""
        old = bf.read_text(path) if os.path.exists(path) else "# Review log\n\n"
        bf.write_text(path, old + line + "\n")
    print("chapter %d: %s" % (n, state) + ("; stamped %d checked mark%s" % (stamped, "" if stamped == 1 else "s")
                                           if stamped else ""))
    return 0


def cmd_place(book, numbers):
    """Record a placement: chapters `skip` in route.md, `claimed` at level 1 in levels.yaml; idempotent."""
    plan = need_plan(book)
    bad = [n for n in numbers if plan.chapter(n) is None]
    if bad:
        print("chapter %s is not in the plan" % ", ".join(map(str, bad)))
        return 1
    slug = os.path.basename(book.rstrip(os.sep))
    lines = bf.read_text(route_path()).splitlines() if os.path.exists(route_path()) else []
    for n in numbers:
        at = [i for i, l in enumerate(lines) if route_chapter(book, l) == n]
        if at and not is_skip(lines[at[0]]):
            lines[at[0]] = lines[at[0]].rstrip() + " · skip"
        elif not at:   # before this book's next chapter, else after its last, else above "left off"
            mine = [(route_chapter(book, l), i) for i, l in enumerate(lines) if route_chapter(book, l)]
            later = [i for k, i in mine if k > n]
            left = [i for i, l in enumerate(lines) if re.search(r"(?i)\bleft off\b", l)]
            i = later[0] if later else mine[-1][1] + 1 if mine else left[0] if left else len(lines)
            lines.insert(i, "- %s %d %s · skip" % (slug, n, plan.chapter(n).title))
    bf.write_text(route_path(), "\n".join(lines) + "\n")
    path = os.path.join(bf.private_dir(), "levels.yaml")
    text = bf.read_text(path) if os.path.exists(path) else ""
    day = datetime.date.fromisoformat(os.environ.get("UNDERSTUDY_TODAY") or datetime.date.today().isoformat())
    new = ["%s/%d: {level: 1, state: claimed, checked: %s, next: %s}" % (slug, n, day, day + datetime.timedelta(days=3))
           for n in numbers if not re.search(r"(?m)^%s/%d:" % (re.escape(slug), n), text)]
    if new:
        bf.write_text(path, text + ("\n" if text and not text.endswith("\n") else "") + "\n".join(new) + "\n")
    print("placed %s: chapter%s %s marked skip in route.md; %d new claimed line%s in levels.yaml" % (
        slug, "" if len(numbers) == 1 else "s", ", ".join(map(str, numbers)), len(new), "" if len(new) == 1 else "s"))
    return 0

# ---------------------------------------------------------------- needs, cost, move

WORDS = {"lesson": 1500, "short": 500, "story": 400, "practice": 1200}   # estimated words a section
STUDY = {"lesson": 5, "short": 5, "story": 0, "practice": 20}            # minutes of study besides reading
TOKENS_A_WORD = 19
READ_RATE = 150       # words a minute, reading to learn
WRITE_RATE = 1000     # words a minute, writing


def all_written(book, plan):
    """Every section number written in the book's chapter files."""
    return {n for ch in plan.chapters for n in written_sections(book, ch)[0]}


def cmd_needs(book, numbers):
    """The named sections plus, transitively, the unwritten sections teaching what they need; book order."""
    plan = need_plan(book)
    bad = [n for n in numbers if plan.section(n) is None]
    if bad:
        print("section %s is not in the plan; name sections as N.M (see us_plan.py status %s)" % (", ".join(bad), book))
        return 1
    written, teacher, want = all_written(book, plan), plan.teacher(), set()
    todo = [plan.section(n) for n in numbers]
    while todo:
        sec = todo.pop()
        if sec.number in want or sec.number in written:
            continue
        want.add(sec.number)
        todo += [teacher[i] for i in sec.needs if i in teacher]
    secs = [s for s in plan.sections() if s.number in want]
    for s in secs:
        print("%s %s (%s, about %s words)" % (s.number, s.title, s.kind, bf.fmt_int(WORDS[s.kind])))
    if secs:
        for line in earlier_in_chapter(plan, want | set(numbers), want, written):
            print(line)
    words = sum(WORDS[s.kind] for s in secs)
    if not secs:
        print("all written: %s and what they need" % ", ".join(numbers))
    else:
        print("total: %d section%s, about %s words, about %s tokens to write" % (
            len(secs), "" if len(secs) == 1 else "s", bf.fmt_int(words), bf.fmt_int(words * TOKENS_A_WORD)))
    return 0


def earlier_in_chapter(plan, involved, want, written):
    """For each chapter of the involved sections: a line listing its unwritten sections before the last
    involved one that are not in want (the plan records only links between chapters, not within one)."""
    out = []
    for ch in plan.chapters:
        mine = [i for i, s in enumerate(ch.sections) if s.number in involved]
        if not mine:
            continue
        left = [s for s in ch.sections[:max(mine)] if s.number not in want and s.number not in written]
        if left:
            out.append("also not written earlier in chapter %d: %s (add any the reader cannot do without)" % (
                ch.number, ", ".join("%s %s" % (s.number, s.title) for s in left)))
    return out


def chapter_cost(secs, written):
    """(sections, words, study hours, writing minutes, writing tokens); writing counts only unwritten sections."""
    words = sum(WORDS[s.kind] for s in secs)
    left = sum(WORDS[s.kind] for s in secs if s.number not in written)
    study = (words / READ_RATE + sum(STUDY[s.kind] for s in secs)) / 60
    return len(secs), words, study, left / WRITE_RATE, left * TOKENS_A_WORD


def cmd_cost(book, n=None):
    """Per chapter: sections, words, hours of study, minutes and tokens of writing; a total; at most 25 lines."""
    plan = need_plan(book)
    chapters = [plan.chapter(n)] if n else plan.chapters
    if None in chapters:
        print("chapter %d is not in the plan" % n)
        return 1
    written = all_written(book, plan)
    rows = [("%d" % c.number, c.title, chapter_cost(c.sections, written)) for c in chapters]
    if len(rows) > 23:          # keep it to 25 lines: the last chapters on one line
        rest = chapters[22:]
        rows = rows[:22] + [("%d-%d" % (rest[0].number, rest[-1].number), "(together)",
                             chapter_cost([s for c in rest for s in c.sections], written))]
    fmt = "%-5s %-32s %8s %8s %9s %9s %11s"
    print(fmt % ("ch", "title", "sections", "words", "reading h", "write min", "tokens"))
    for num, title, (k, words, study, mins, toks) in rows:
        title = title if len(title) <= 32 else title[:29] + "..."
        print(fmt % (num, title, k, bf.fmt_int(words), "%.1f" % study, "%.0f" % mins, bf.fmt_int(int(toks))))
    if not n:
        k, words, study, mins, toks = chapter_cost(plan.sections(), written)
        print(fmt % ("total", "(%d written: no writing cost)" % len(written) if written else "", k, bf.fmt_int(words),
                     "%.1f" % study, "%.0f" % mins, bf.fmt_int(int(toks))))
    return 0


def chapter_blocks(lines):
    """(head, [(start, end)]) for each `### N` chapter of PLAN.md lines; a block ends before the blank and
    `## Part` lines that lead into the next chapter, so parts stay where they are."""
    starts = [i for i, l in enumerate(lines) if bf.PLAN_CHAPTER.match(l.strip())]
    blocks = []
    for k, a in enumerate(starts):
        b = starts[k + 1] if k + 1 < len(starts) else len(lines)
        while b > a + 1 and (not lines[b - 1].strip() or bf.PLAN_PART.match(lines[b - 1].strip())):
            b -= 1
        blocks.append((a, b))
    return blocks


def cmd_move(book, n, to):
    """Move chapter n to position `to`, renumber chapters, sections and § references; refuse once written."""
    plan = need_plan(book)
    count = len(plan.chapters)
    if plan.chapter(n) is None or not 1 <= to <= count:
        print("chapter %d or position %d is not in the plan (chapters 1 to %d)" % (n, to, count))
        return 1
    done = [c.number for c in plan.chapters if bf.chapter_path(book, c.number)]
    if done:
        print("chapter %s already written; moving chapters would break its numbers: move before writing, "
              "or edit PLAN.md and the chapter files by hand" % ", ".join(map(str, done)))
        return 1
    if [c.number for c in plan.chapters] != list(range(1, count + 1)):
        print("chapters are not numbered 1 to %d; fix the numbering first (us_plan.py check %s)" % (count, book))
        return 1
    order = list(range(1, count + 1))
    order.remove(n)
    order.insert(to - 1, n)
    new = {old: i for i, old in enumerate(order, 1)}
    lines = bf.read_text(plan.path).splitlines()
    blocks = chapter_blocks(lines)
    out, prev = [], 0
    for slot, (a, b) in enumerate(blocks):
        src = blocks[order[slot] - 1]
        out += lines[prev:a] + [renumber(l, new) for l in lines[src[0]:src[1]]]
        prev = b
    out += lines[prev:]
    out = [re.sub(r"§\s?(\d+)\.(\d+)", lambda m: "§%d.%s" % (new.get(int(m.group(1)), int(m.group(1))), m.group(2)), l)
           for l in out]
    bf.write_text(plan.path, "\n".join(out) + "\n")
    move_route(book, new)
    print("moved chapter %d to %d; chapters renumbered" % (n, to))
    return cmd_check(book)


def renumber(line, new):
    """A chapter heading or section line with its chapter number mapped through new."""
    m = re.match(r"^(\s*###\s+(?:Chapter\s+)?)(\d+)", line, re.I) or re.match(r"^(\s*)(\d+)(?=\s*\.\s*\d+\s)", line)
    return m.group(1) + str(new.get(int(m.group(2)), int(m.group(2)))) + line[m.end():] if m else line


def move_route(book, new):
    """Renumber this book's chapters in private/route.md, if it names them."""
    path = route_path()
    if not os.path.exists(path):
        return
    slug = re.escape(os.path.basename(book.rstrip(os.sep)))
    text = bf.read_text(path)
    moved = re.sub(r"(?<![\w-])(%s[ /])(\d+)\b" % slug, lambda m: m.group(1) + str(new.get(int(m.group(2)), int(m.group(2)))), text)
    if moved != text:
        bf.write_text(path, moved)

# ---------------------------------------------------------------- from-chapters


def section_kind(sec, index):
    """Guess story/practice/lesson for an existing section."""
    title = sec.title.lower()
    if title.startswith("practice") or (not sec.beats and sec.details >= 5):
        return "practice"
    if index == 1 and "histor" in title and not sec.beats:
        return "story"
    return "lesson"


def first_ideas(docs):
    """Map 'N.M' -> first idea id taught there."""
    return {s.number: s.teaches[0].id for d in docs.values() for s in d.sections if s.teaches}


def plan_from_docs(docs, title, audience, run):
    """PLAN.md text for parsed chapter files {number: ChapterDoc}."""
    first = first_ideas(docs)
    practice = {s.number for d in docs.values() for i, s in enumerate(d.sections, 1) if section_kind(s, i) == "practice"}
    first = {k: v for k, v in first.items() if k not in practice}
    out = ["# %s" % title, "for: %s" % audience, "run: %s" % run, ""]
    for n in sorted(docs):
        out += ["### %d %s" % (n, docs[n].title)]
        used = set()
        for i, sec in enumerate(docs[n].sections, 1):
            out.append(plan_line(sec, i, n, first, used))
        out.append("")
    return "\n".join(out)


def plan_line(sec, index, n, first, used):
    """One `N.M Title | fields` line; needs come from § references to earlier chapters."""
    fields = []
    kind = section_kind(sec, index)
    if kind != "lesson":
        fields.append(kind)
    if sec.teaches:
        fields.append("teaches: " + ", ".join(dict.fromkeys(t.id for t in sec.teaches)))
    needs = []
    for ref, _ in question_refs(sec):
        idea = first.get(ref)
        if idea and int(ref.split(".")[0]) < n and idea not in used:
            used.add(idea)
            needs.append(idea)
    if needs:
        fields.append("needs: " + ", ".join(needs))
    return " | ".join(["%s %s" % (sec.number, sec.title.replace("|", "/"))] + fields)


def question_refs(sec):
    """§ references made in a lesson's 'The question' beat (where it names what it builds on)."""
    beats = [(name, line) for name, line in sec.beats]
    start = next((line for name, line in beats if name == "The question"), None)
    if start is None:
        return []
    end = next((line for name, line in beats if line > start), sec.end)
    return [(ref, line) for ref, line in sec.refs if start < line < end]


def guess_run(docs):
    """Most common language among tagged programs."""
    langs = collections.Counter(c.lang for d in docs.values() for s in d.sections for c in s.code if c.lang)
    return langs.most_common(1)[0][0] if langs else "TODO"


def cmd_from_chapters(book, args):
    """Write PLAN.md from the chapter files."""
    path = os.path.join(book, "PLAN.md")
    if os.path.exists(path) and "--force" not in args:
        print("PLAN.md exists; add --force to overwrite it")
        return 1
    docs = {}
    for name in sorted(os.listdir(os.path.join(book, "chapters"))):
        if name.endswith(".md") and name[:2].isdigit():
            doc = bf.parse_chapter(bf.read_text(os.path.join(book, "chapters", name)))
            docs[doc.number or int(name[:2])] = doc
    title = option(args, "--title", os.path.basename(os.path.abspath(book)).replace("-", " ").capitalize())
    text = plan_from_docs(docs, title, option(args, "--for", "TODO who the book is for"), option(args, "--run", guess_run(docs)))
    bf.write_text(path, text)
    n = sum(len(d.sections) for d in docs.values())
    print("wrote PLAN.md: %d chapters, %d sections" % (len(docs), n))
    return 0


def option(args, name, default):
    """Value after --name in args, or default."""
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default

# ---------------------------------------------------------------- main


def main(argv):
    """Dispatch a subcommand."""
    if argv[:1] in (["-h"], ["--help"], ["help"]):
        print(__doc__.strip())
        return 0
    if len(argv) < 2 or argv[0] not in ("check", "brief", "taught", "next", "status", "mark", "from-chapters", "place",
                                        "needs", "cost", "move"):
        print(__doc__.strip())
        return 2
    cmd, book = argv[0], bf.resolve_book(argv[1])
    if cmd == "needs":
        if len(argv) < 3 or not all(re.fullmatch(r"\d+\.\d+", a) for a in argv[2:]):
            sys.exit("usage: us_plan.py needs BOOK N.M [N.M ...]")
        return cmd_needs(book, ["%d.%d" % tuple(map(int, a.split("."))) for a in argv[2:]])
    if cmd == "cost":
        if len(argv) > 3 or (len(argv) == 3 and not argv[2].isdigit()):
            sys.exit("usage: us_plan.py cost BOOK [N]")
        return cmd_cost(book, int(argv[2]) if len(argv) == 3 else None)
    if cmd == "move":
        if len(argv) != 5 or not argv[2].isdigit() or argv[3] != "--to" or not argv[4].isdigit():
            sys.exit("usage: us_plan.py move BOOK N --to M")
        return cmd_move(book, int(argv[2]), int(argv[4]))
    if cmd == "check":
        return cmd_check(book)
    if cmd == "brief":
        if len(argv) < 3 or not argv[2].isdigit():
            sys.exit("usage: us_plan.py brief BOOK N")
        return cmd_brief(book, int(argv[2]))
    if cmd == "taught":
        if len(argv) < 3:
            sys.exit("usage: us_plan.py taught BOOK WORD [WORD...]")
        return cmd_taught(book, argv[2:])
    if cmd == "next":
        return cmd_next(book)
    if cmd == "status":
        return cmd_status(book)
    if cmd == "mark" and argv[2:3] == ["pass"]:
        if len(argv) != 4 or not argv[3].isdigit():
            sys.exit("usage: us_plan.py mark BOOK pass N")
        return cmd_mark_pass(book, int(argv[3]))
    if cmd == "mark" and argv[3:4] == ["restamp"]:
        if len(argv) != 4 or not argv[2].isdigit():
            sys.exit("usage: us_plan.py mark BOOK N restamp")
        return cmd_restamp(book, int(argv[2]))
    if cmd == "mark":
        notes = dict(zip(argv[4::2], argv[5::2]))
        if (len(argv) < 4 or not argv[2].isdigit() or argv[3] not in ("reviewed", "written") or len(argv) % 2
                or set(notes) - {"--false", "--stuck", "--open"}
                or not all(notes.get(k, "0").isdigit() for k in ("--false", "--stuck"))):
            sys.exit('usage: us_plan.py mark BOOK N reviewed|written [--false A] [--stuck B] [--open "text"]'
                     " | mark BOOK N restamp | mark BOOK pass N")
        return cmd_mark(book, int(argv[2]), argv[3], notes)
    if cmd == "place":
        if len(argv) < 3 or not all(a.isdigit() for a in argv[2:]):
            sys.exit("usage: us_plan.py place BOOK N [N...]")
        return cmd_place(book, list(dict.fromkeys(int(a) for a in argv[2:])))
    return cmd_from_chapters(book, argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
