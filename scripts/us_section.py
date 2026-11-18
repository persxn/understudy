"""Add or repair one section of a chapter, checked against PLAN.md and the book standard.

  us_section.py append BOOK N [--file PATH]     the first unwritten section of chapter N, Markdown on stdin (or in PATH)
  us_section.py append BOOK N.M [--file PATH]   section N.M, put in its place even when earlier ones are not written
  us_section.py replace BOOK N.M --file PATH    swap a written section for a corrected one
  us_section.py patch BOOK N.M --old TEXT --new TEXT   change one exact piece of a written section

A code marker with no fence below it stands for a program tried with `us_run.py try`: the tried
program is filled in (attributes on the marker are added to the tried ones) before checking.
In prose, {L:fclose(fp)} becomes "line N", N the line holding `fclose(fp)` in the nearest program
above it, or "line N (`fclose(fp)`)" past line 30, where counting is slow; {L:ID:text} names the
program, and {L:=text} (or {L:ID:=text}) wants the whole line to be exactly text. A "line" or "Line"
written just before it is kept, not doubled. A terminal session has no line numbers a reader can
see: {L:...} pointing into a console fence is an error; name the command in backticks instead.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
import us_run  # noqa: E402

LESSON_WORDS = (700, 2600)
LESSON_TARGET = (1200, 3000)   # rules/writers-guide.md: advice, not a limit
CONSOLE_TARGET = (1200, 3000)
STORY_MAX = 500
SHORT_WORDS = (300, 700)   # kind `short`: one command or one small idea
LESSON_MIN = 900          # under it a lesson is an error: it has left out a move
SHORT_MIN = 200            # under it even a `short` section is an error
PRACTICE_MIN = 3           # tasks with a hidden answer that climb: guided, on your own, a small project
MODES = ["run", "fragment", "compile", "warns", "error", "crash"]
LINE_REF = re.compile(r"(?:\b([Ll]ines?) +)?\{L:([^{}]*)\}")  # shortcut: text holding { or } cannot be named; rare
COUNT_EASY = 30            # a line number past this is given with its text


class Report:
    """Collected errors, warnings and notes for one submitted section."""

    def __init__(self, line_map=None):
        self.errors, self.warnings, self.notes = [], [], []
        self.line_map = line_map

    def at(self, line):
        """A line of the checked text as a line of the text the writer sent."""
        if not self.line_map:
            return line
        return self.line_map[min(max(line, 1), len(self.line_map)) - 1]

    def error(self, line, msg):
        """Record a problem that stops the section."""
        self.errors.append("error line %d: %s" % (self.at(line), msg))

    def warn(self, line, msg):
        """Record a problem that does not stop the section."""
        self.warnings.append("warn line %d: %s" % (self.at(line), msg))

# ---------------------------------------------------------------- checks


def check_shape(doc, rep):
    """Exactly one `## N.M Title` section and nothing around it."""
    if doc.title:
        rep.error(doc.title_line, "remove the '# ' chapter heading; send only the section")
    for line, text in doc.other_headings:
        rep.error(line, "'%s' is not a section heading; use '## N.M Title', or '###' inside one" % text[:40])
    if not doc.sections:
        rep.error(1, "no '## N.M Title' heading; start the section with one")
        return None
    for extra in doc.sections[1:]:
        rep.error(extra.line, "a second section (%s); send one section per call" % extra.number)
    sec = doc.sections[0]
    stray = next((i for i, l in enumerate(doc.lines[:sec.line - 1], 1) if l.strip()), None)
    if stray:
        rep.error(stray, "text before the '## %s' heading; start with the heading" % sec.number)
    return sec


def check_identity(sec, planned, want, rep):
    """The section is the one expected, and its title matches the plan."""
    if sec.number != want:
        rep.error(sec.line, "this is %s but %s is expected; renumber the heading '## %s'" % (sec.number, want, want))
    elif norm(sec.title) != norm(planned.title):
        rep.warn(sec.line, "title differs from the plan: '%s'" % planned.title)


def norm(title):
    """Title reduced to lower-case letters and digits, for comparison."""
    return "".join(ch for ch in title.lower() if ch.isalnum())


def check_lesson(sec, rep, target=LESSON_TARGET, required=(), hard=LESSON_WORDS, least=1, what="a lesson"):
    """Free headings (rules/writers-guide.md); a Check yourself with a hidden answer; length is advice."""
    check_answers(sec, rep, least)
    check_words(sec, rep, hard, target, what)


def check_answers(sec, rep, least=1):
    """Check yourself present with at least `least` hidden answers."""
    if not sec.check_line:
        rep.error(sec.end, "no '**Check yourself**'; end the section with it and at least one question, its answer in <details>")
    elif sec.answers < least:
        rep.error(sec.check_line, "Check yourself has %d hidden answers; give at least %d in <details>" % (sec.answers, least))


def check_words(sec, rep, hard, soft, what="a lesson"):
    """Word count: an error under LESSON_MIN (SHORT_MIN for a short section), else a note (advice) outside
    the guide's range."""
    if what == "a lesson" and sec.words < LESSON_MIN:
        rep.error(sec.line, "%s has %s words: a lesson this short has left out a move (how it works and why, the "
                  "real thing worked through, or what goes wrong). Deepen it; or, if it truly teaches one small thing, "
                  "mark it `short` in PLAN.md" % (sec.number, bf.fmt_int(sec.words)))
    elif what == "a short section" and sec.words < SHORT_MIN:
        rep.error(sec.line, "%s has %s words: too thin even for a short section" % (sec.number, bf.fmt_int(sec.words)))
    elif sec.words < soft[0] or sec.words > soft[1]:
        rep.notes.append("note line %d: %s words; %s usually runs %s to %s" % (
            rep.at(sec.line), bf.fmt_int(sec.words), what, bf.fmt_int(soft[0]), bf.fmt_int(soft[1])))


def check_story(sec, rep):
    """A story is short."""
    if sec.words > STORY_MAX:
        rep.error(sec.line, "%s words; a story is at most %d (about 250)" % (bf.fmt_int(sec.words), STORY_MAX))


def check_practice(sec, rep):
    """A practice climbs: at least PRACTICE_MIN tasks, each with a hidden answer."""
    if sec.details < PRACTICE_MIN:
        rep.error(sec.line, "%s is practice with %d answered tasks; give at least three that climb: guided, on your "
                  "own, a small project or case" % (sec.number, sec.details))


def check_ideas(sec, planned, plan, rep):
    """Every planned idea has a teaches marker; markers name planned ideas; a lesson's markers give words."""
    taught = {}
    for t in sec.teaches:
        if kind_of(planned) in ("lesson", "short") and not t.words:
            rep.error(t.line, "teaches '%s' has no words after '='; write '<!-- teaches: %s = term, terms -->'" % (t.id, t.id))
        if t.id in taught:
            rep.error(t.line, "'%s' is marked twice; keep the marker above its first teaching" % t.id)
        taught.setdefault(t.id, t)
        if t.id not in planned.teaches:
            other = plan.teacher().get(t.id)
            where = "planned for %s" % other.number if other else "not in the plan"
            rep.warn(t.line, "teaches '%s' is %s; check the id" % (t.id, where))
    for idea in planned.teaches if kind_of(planned) in ("lesson", "short") else []:
        if idea not in taught:
            rep.error(sec.line, "no marker for planned idea '%s'; add '<!-- teaches: %s = words -->' above its definition" % (idea, idea))


def check_code(sec, taken, rep):
    """Code and figure markers: ids, fences, modes; every fence has a language."""
    for code in sec.code:
        if not code.id:
            rep.error(code.line, "code marker has no id; write '<!-- code: id=some-name -->'")
        elif code.id in taken:
            rep.error(code.line, "code id '%s' is already used in this chapter; rename it" % code.id)
        taken.add(code.id)
        if code.mode not in MODES and code.mode != "compile-error":
            rep.error(code.line, "mode '%s' unknown; use %s" % (code.mode, ", ".join(MODES)))
        if not code.fence:
            rep.error(code.line, "no fenced program directly below the code marker; put the ``` block right under it")
    for fig in sec.figures:
        if not fig.id:
            rep.error(fig.span[0], "figure marker has no id; start it '<!-- fig: id=some-name'")
        elif ("fig", fig.id) in taken:
            rep.error(fig.span[0], "figure id '%s' is already used in this chapter; rename it" % fig.id)
        taken.add(("fig", fig.id))
    for line in sec.bare_fences:
        rep.error(line, "fence without a language tag; write ```c, ```text or similar")


def check_refs(sec, plan, number, rep):
    """Every § points into the plan; later sections are listed as forward notes."""
    here = key(number)
    forward = []
    for ref, line in sec.refs:
        if plan.section(ref) is None:
            rep.error(line, "§%s is not in the plan; fix the number" % ref)
        elif key(ref) > here and "§" + ref not in forward:
            forward.append("§" + ref)
    for value, line in sec.resolves:
        ref = value.strip().lstrip("§")
        if ref[:1].isdigit() and plan.section(ref) is None:
            rep.error(line, "resolves %s, which is not in the plan; fix the number" % ref)
    if forward:
        rep.notes.append("forward: " + ", ".join(sorted(forward, key=lambda r: key(r[1:]))))


def kind_of(planned):
    """Kind of a planned section; `short` is read from the plan line too, should the parser not know it."""
    fields = [f.strip().lower() for f in planned.raw.split("|")[1:]]
    return "short" if "short" in fields or "kind: short" in fields else planned.kind


def key(number):
    """'8.12' -> (8, 12) for ordering."""
    return tuple(int(x) for x in number.split("."))


def validate(text, plan, want, taken, line_map=None):
    """Check one submitted section; returns (Report, SectionDoc or None)."""
    rep = Report(line_map)
    doc = bf.parse_chapter(text)
    sec = check_shape(doc, rep)
    planned = plan.section(want)
    if sec is None or planned is None:
        return rep, sec
    check_identity(sec, planned, want, rep)
    kind = kind_of(planned)
    if kind == "lesson":
        check_lesson(sec, rep, CONSOLE_TARGET if plan.run.strip().lower() == us_run.CONSOLE else LESSON_TARGET)
    elif kind == "short":
        check_lesson(sec, rep, SHORT_WORDS, (), SHORT_WORDS, 1, "a short section")
    else:
        {"story": check_story, "practice": check_practice}[kind](sec, rep)
    check_ideas(sec, planned, plan, rep)
    check_code(sec, taken, rep)
    check_refs(sec, plan, want, rep)
    return rep, sec

# ---------------------------------------------------------------- tried programs


def chapter_programs(path):
    """{id: (marker line, fence text)} of the programs already in a chapter file."""
    if not path or not os.path.isfile(path):
        return {}
    lines = [l if l.endswith("\n") else l + "\n" for l in bf.read_text(path).splitlines(keepends=True)]
    blocks, _ = us_run.parse_chapter(lines, answers=False)
    return {b.id: (lines[b.marker - 1].strip(), "".join(lines[b.open:b.close + 1])) for b in blocks}


def merged_marker(stored, given):
    """The tried marker line, with attributes the section's marker adds or overrides."""
    try:
        extra = us_run.parse_attrs(us_run.MARKER.match(given).group(1))
        attrs = us_run.parse_attrs(us_run.MARKER.match(stored).group(1))
    except (ValueError, AttributeError):
        return given
    if set(extra) <= {"id"}:
        return stored
    attrs.update(extra)
    words = []
    for key, value in attrs.items():
        if value == "" and key in ("varies", "answer"):
            words.append(key)
        elif value == "" or re.search(r"[\s\"']", value):
            words.append('%s="%s"' % (key, value.replace('"', '\\"')))
        else:
            words.append("%s=%s" % (key, value))
    return "<!-- code: %s -->" % " ".join(words)


def fill_programs(text, path):
    """Put the tried program (or the chapter's own) under each code marker that has no fence.
    Returns (text, map from its lines to the lines sent, problems as (line, message), ids from tried/)."""
    lines = text.splitlines()
    out, line_map, problems, used = [], [], [], []
    known = None
    i = 0
    while i < len(lines):
        line = lines[i]
        fm = us_run.FENCE_OPEN.match(line)
        if fm:
            close = us_run.find_fence_close(lines, i + 1, fm.group(2)[0], len(fm.group(2)))
            end = len(lines) - 1 if close < 0 else close
            out += lines[i:end + 1]
            line_map += range(i + 1, end + 2)
            i = end + 1
            continue
        m = us_run.MARKER.match(line)
        j = i + 1
        while m and j < len(lines) and not lines[j].strip():
            j += 1
        if m and not (j < len(lines) and us_run.FENCE_OPEN.match(lines[j])):
            try:
                bid = us_run.parse_attrs(m.group(1)).get("id", "")
            except ValueError:
                bid = ""
            found = us_run.tried_program(path, bid) if bid else None
            if found:
                used.append(bid)
            elif bid:
                known = chapter_programs(path) if known is None else known
                found = known.get(bid)
            if found:
                program = [merged_marker(found[0], line)] + found[1].rstrip("\n").split("\n")
                out += program
                line_map += [i + 1] * len(program)
                i += 1
                continue
            if bid:
                problems.append((i + 1, "id=%s was not tried: send it to python3 scripts/us_run.py try %s %d first, "
                                 "or include the program" % (bid, us_run.shown(os.path.dirname(os.path.dirname(path))),
                                                             int(os.path.basename(path)[:2]))))
        out.append(line)
        line_map.append(i + 1)
        i += 1
    return "\n".join(out) + "\n", line_map, problems, used


def fill_line_refs(text):
    """Replace each {L:text} in prose by its line number in the nearest program above; returns (text, problems)."""
    lines = text.split("\n")
    blocks = us_run.parse_chapter([l + "\n" for l in lines], answers=False)[0]
    by_id, problems = {b.id: b for b in blocks}, []

    def number(i, m):
        ident, sep, rest = m.group(2).partition(":")
        prog = by_id.get(ident) if sep else None
        want = rest if prog else m.group(2)
        prog = prog or max((b for b in blocks if b.close < i), key=lambda b: b.close, default=None)
        if prog is None:
            problems.append((i + 1, "{L:%s}: no program above it in the section; name one: {L:ID:text}" % m.group(2)))
            return m.group(0)
        if prog.lang == us_run.CONSOLE:
            problems.append((i + 1, "{L:%s} points into the session id=%s, which has no line numbers a reader can "
                             "see: name the command in backticks instead" % (m.group(2), prog.id)))
            return m.group(0)
        exact = want.startswith("=")
        want = want[1:] if exact else want
        hits = [k for k, l in enumerate(prog.code.splitlines(), 1) if (l.strip() == want.strip() if exact else want in l)]
        if len(hits) == 1:
            start = not m.group(1) and re.search(r"(^|[.!?]\s+)$", m.string[:m.start()])
            word = (m.group(1) or ("Line" if start else "line")).rstrip("s")
            return "%s %d" % (word, hits[0]) + (" (`%s`)" % want if hits[0] > COUNT_EASY else "")
        problems.append((i + 1, "%s: %s in id=%s; write a longer piece of the line" % (
            "{L:%s}" % m.group(2), "lines %s all hold it" % ", ".join(map(str, hits)) if hits else "no line holds it",
            prog.id)))
        return m.group(0)
    for i, line in enumerate(lines):
        if "{L:" in line and not any(b.open <= i <= b.close for b in blocks):
            lines[i] = LINE_REF.sub(lambda m: number(i, m), line)
    return "\n".join(lines), problems


def forget_tried(path, ids):
    """Remove tried programs that are now in the chapter (the chapter holds the newest copy)."""
    for bid in ids:
        try:
            os.remove(os.path.join(us_run.tried_folder(path), bid + ".md"))
        except OSError:
            pass

# ---------------------------------------------------------------- chapter file and status


def chapter_ids(doc, skip=None):
    """Code ids and ('fig', id) pairs already used in a chapter, except in section skip."""
    taken = set()
    for s in doc.sections:
        if s.number != skip:
            taken |= {c.id for c in s.code} | {("fig", f.id) for f in s.figures}
    return taken


def save_rejected(text, number):
    """Save a rejected section where the writer can fix it; returns the path."""
    path = os.path.join(bf.private_dir(), "scratch", "rejected-%s.md" % number)
    bf.write_text(path, text if text.endswith("\n") else text + "\n")
    return path


def run_helpers(path):
    """Run us_run.py and us_draw.py on the chapter; return their problem lines (none on success)."""
    out = []
    for script, args in (("us_run.py", [path]), ("us_draw.py", ["--chapter", path])):
        res = bf.run_helper(script, args)
        if res is None or res[0] == 0:
            continue
        code, lines, errs = res
        name = script[:-3]
        lines = [l for l in lines if not l.startswith(("ok ", "reads:")) and not re.search(r"\b0 problems\b", l)]
        out += ["%s: %s" % (name, l) for l in (lines or errs)] or ["%s: failed (exit %d)" % (name, code)]
    return out


def update_status(book, plan, number):
    """Record sections written, words and state of chapter number in STATUS.json."""
    ch = plan.chapter(number)
    doc = bf.parse_chapter(bf.read_text(bf.chapter_path(book, number)))
    done = [s.number for s in doc.sections]
    status = bf.read_status(book)
    entry = status["chapters"].setdefault(str(number), {})
    complete = {s.number for s in ch.sections} <= set(done)
    if entry.get("state") != "reviewed":
        entry["state"] = "written" if complete else "writing"
    entry["sections"] = done
    entry["planned"] = len(ch.sections)
    entry["words"] = sum(s.words for s in doc.sections)
    bf.write_status(book, status)


def fix_hints(problems, sec, path):
    """One line per program of this section that us_run.py reports a problem for: how to fix it cheaply."""
    ids = {c.id for c in sec.code}
    hints = []
    for line in problems:
        m = re.match(r"us_run: .*?\bid=(\S+)", line)
        if m and m.group(1) in ids and m.group(1) not in hints:
            hints.append(m.group(1))
    shown = us_run.shown(path)
    out = ["fix the program in %s with a small edit, then: python3 scripts/us_run.py %s --only %s" % (shown, shown, bid)
           for bid in hints]
    if any(line.startswith("us_draw: ") for line in problems):
        out.append("fix the figure description in %s, then: python3 scripts/us_draw.py --chapter %s" % (shown, shown))
    return out


def finish(book, plan, chapter, sec, rep, path, source, used=()):
    """After a section lands: helpers, status, the ok line."""
    forget_tried(path, used)
    problems = run_helpers(path)
    problems += fix_hints(problems, sec, path)
    update_status(book, plan, chapter)
    if source and os.path.abspath(source).startswith(os.path.join(bf.private_dir(), "scratch")):
        os.remove(source)
    progs, figs = len(sec.code), len(sec.figures)
    print("ok %s %s  %s words  %d program%s  %d figure%s" % (
        sec.number, sec.title, bf.fmt_int(sec.words), progs, "" if progs == 1 else "s", figs, "" if figs == 1 else "s"))
    for line in rep.warnings + rep.notes + problems:
        print(line)
    return 0


def reject(rep, text, number):
    """Print problems and save the text; returns exit code 1."""
    for line in rep.errors + rep.warnings:
        print(line)
    path = save_rejected(text, number)
    print("rejected, nothing appended; fix %s and resubmit with --file %s" % (path, path))
    return 1

# ---------------------------------------------------------------- commands


def cmd_append(book, plan, chapter, text, source, want=None):
    """Add section `want` of chapter `chapter` in its place, or else the first one not written yet."""
    ch = plan.chapter(chapter)
    if ch is None:
        return fail("chapter %d is not in the plan" % chapter)
    path = bf.chapter_path(book, chapter)
    doc = bf.parse_chapter(bf.read_text(path)) if path else bf.ChapterDoc()
    done = {s.number for s in doc.sections}
    todo = [s for s in ch.sections if s.number not in done]
    if want and plan.section(want) is None:
        return fail("%s is not in the plan; see python3 scripts/us_plan.py brief %s %d" % (want, us_run.shown(book), chapter))
    if want in done:
        return fail("%s is already written; use replace or patch to change it" % want)
    if not todo:
        return fail("chapter %d is fully written; use replace to repair a section" % chapter)
    want = want or todo[0].number
    full, rep, sec, used = check_and_fill(text, plan, want, chapter_ids(doc), path or bf.new_chapter_path(book, chapter, ch.title))
    if rep.errors:
        return reject(rep, text, want)
    after = next((s for s in doc.sections if key(s.number) > key(want)), None)
    if after:
        lines = doc.lines[:after.line - 1] + full.strip("\n").splitlines() + [""] + doc.lines[after.line - 1:]
        bf.write_text(path, "\n".join(lines).rstrip("\n") + "\n")
    elif path:
        bf.write_text(path, bf.read_text(path).rstrip("\n") + "\n\n" + full.strip("\n") + "\n")
    else:
        path = bf.new_chapter_path(book, chapter, ch.title)
        bf.write_text(path, "# Chapter %d: %s\n\n%s\n" % (chapter, ch.title, full.strip("\n")))
    return finish(book, plan, chapter, sec, rep, path, source, used)


def cmd_replace(book, plan, number, text, source):
    """Replace written section `number` with a corrected one."""
    chapter = int(number.split(".")[0])
    path = bf.chapter_path(book, chapter)
    doc = bf.parse_chapter(bf.read_text(path)) if path else None
    old = doc.section(number) if doc else None
    if old is None:
        return fail("%s is not written yet; use append" % number)
    if plan.section(number) is None:
        return fail("%s is not in the plan" % number)
    full, rep, sec, used = check_and_fill(text, plan, number, chapter_ids(doc, skip=number), path)
    if rep.errors:
        return reject(rep, text, number)
    lines = doc.lines[:old.line - 1] + full.strip("\n").splitlines() + [""] + doc.lines[old.end:]
    while lines and not lines[-1].strip():
        lines.pop()
    bf.write_text(path, "\n".join(lines) + "\n")
    return finish(book, plan, chapter, sec, rep, path, source, used)


def cmd_patch(book, plan, number, old, new):
    """Replace one exact piece of text in written section `number`, then check and re-run it as replace does."""
    path = bf.chapter_path(book, int(number.split(".")[0]))
    doc = bf.parse_chapter(bf.read_text(path)) if path else None
    sec = doc.section(number) if doc else None
    if sec is None:
        return fail("%s is not written yet; use append" % number)
    body = "\n".join(doc.lines[sec.line - 1:sec.end])
    found = body.count(old)
    if found != 1:
        return fail("the --old text is found %d times in %s; it must be found exactly once: %s" % (
            found, number, "copy it exactly from the chapter file" if not found else "give a longer piece"))
    return cmd_replace(book, plan, number, body.replace(old, new) + "\n", None)


def check_and_fill(text, plan, want, taken, path):
    """Fill in tried programs, then validate; returns (filled text, Report, SectionDoc, ids taken from tried/)."""
    full, line_map, missing, used = fill_programs(text, path)
    full, refs = fill_line_refs(full)
    rep, sec = validate(full, plan, want, taken, line_map)
    for line, msg in refs:
        rep.error(line, msg)
    if missing:
        lines = {"error line %d: no fenced program" % line for line, _ in missing}
        rep.errors = ["error line %d: %s" % m for m in missing] + [e for e in rep.errors if not e.startswith(tuple(lines))]
    return full, rep, sec, used


def fail(msg):
    """Print one line and return exit code 1."""
    print(msg)
    return 1


def read_input(args):
    """Section text from --file PATH or stdin; returns (text, path or None)."""
    if "--file" in args:
        i = args.index("--file")
        if i + 1 >= len(args):
            sys.exit("--file needs a path")
        return bf.read_text(args[i + 1]), args[i + 1]
    return sys.stdin.read(), None


def main(argv):
    """Dispatch append, replace or patch."""
    if len(argv) < 3 or argv[0] not in ("append", "replace", "patch"):
        print(__doc__.strip())
        return 2
    cmd, book, target = argv[0], bf.resolve_book(argv[1]), argv[2]
    plan = bf.load_plan(book)
    if plan is None:
        return fail("no PLAN.md in %s" % book)
    if cmd != "append" and not re.match(r"^\d+\.\d+$", target):
        return fail("%s takes a section number, e.g. %s BOOK 8.2" % (cmd, cmd))
    if cmd == "patch":
        opts = argv[3:]
        if "--old" not in opts or "--new" not in opts or opts.index("--old") + 1 >= len(opts) \
                or opts.index("--new") + 1 >= len(opts):
            return fail("patch needs --old TEXT --new TEXT")
        old, new = opts[opts.index("--old") + 1], opts[opts.index("--new") + 1]
        if not old:
            return fail("--old is empty; give the exact text to replace")
        return cmd_patch(book, plan, target, old, new)
    if cmd == "replace" and "--file" not in argv:
        return fail("replace needs --file PATH")
    text, source = read_input(argv[3:])
    if not text.strip():
        return fail("empty section; send the Markdown on stdin or with --file")
    if cmd == "append":
        m = re.match(r"^(\d+)(?:\.(\d+))?$", target)
        if not m:
            return fail("append takes a chapter or section number, e.g. append BOOK 8 or append BOOK 8.2")
        return cmd_append(book, plan, int(m.group(1)), text, source, target if m.group(2) else None)
    return cmd_replace(book, plan, target, text, source)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
