#!/usr/bin/env python3
"""Check books against rules/book-standard.md, and the product's own skills. Exit 1 on errors only.

    python3 scripts/us_check.py [BOOK [N]] [--tokens]     no BOOK: the skills and every book
    python3 scripts/us_check.py BOOK N --suspects [--all]  the spots a reviewer must clear, for chapter N
                                   (the top ones; --all: every one)
    python3 scripts/us_check.py BOOK N --prose [--from LINE] [--lines K]
                                   the chapter for the reviewer: numbered prose and tables, each program
                                   with its output and each figure folded to one line; K lines (150) a call
    python3 scripts/us_check.py BOOK N --show ID           one program and its output, in full, with the
                                   lines of the file and of the program numbered
    python3 scripts/us_check.py BOOK N --risks             the review's reading list for chapter N: each
                                   <!-- risk: --> note with its passage, each command that can destroy
                                   something, each dangling reference, each unrun block

One line per problem: ERROR (must fix), FLAG (look, fix if right), NOTE (for information).
--tokens   also print the rough token size of everything an agent can load, and fail (exit 1) when
           the always-loaded text is over 2,000 tokens or a skill body is 1,000 or more
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
from us_lib import ROOT, parse_front, tokens  # noqa: E402
from us_run import POSIX_RE, command_spans, shown  # noqa: E402

errors, warnings = [], []          # filled by check_skills (product checks)

# ---------------------------------------------------------------- product skills (unchanged)


def check_skills():
    folder = os.path.join(ROOT, ".claude", "skills")
    sizes = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name, "SKILL.md")
        if not os.path.exists(path):
            continue
        front, body = parse_front(path)
        if sorted(front) != ["description", "name"]:
            errors.append(f"skill {name}: header must hold exactly 'name' and 'description', found {sorted(front)}")
        skill_name = front.get("name", "")
        if skill_name != name:
            errors.append(f"skill {name}: name '{skill_name}' must match its folder")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", skill_name):
            errors.append(f"skill {name}: name must be 1-64 lowercase letters, digits, hyphens")
        if "claude" in skill_name or "anthropic" in skill_name:
            errors.append(f"skill {name}: name contains a reserved word")
        description = front.get("description", "")
        if not 1 <= len(description) <= 1024 or "<" in description or ">" in description:
            errors.append(f"skill {name}: description must be 1-1024 characters with no angle brackets")
        if body.count("\n") > 500:
            errors.append(f"skill {name}: body is over 500 lines")
        for ref in re.findall(r"`((?:rules|scripts)/[\w./-]+)`", body):
            if not os.path.exists(os.path.join(ROOT, ref)):
                errors.append(f"skill {name}: points to {ref}, which does not exist")
        sizes.append((name, tokens(description), tokens(body)))
    for name, line in (("CLAUDE.md", "@AGENTS.md"), ("GEMINI.md", "@./AGENTS.md")):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path) or line not in open(path, encoding="utf-8").read().split():
            errors.append(f"{name} must exist and import the shared prompt with the line {line}")
    prompt_text = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read()
    for name, _, _ in sizes:
        if f"`{name}`" not in prompt_text:
            errors.append(f"AGENTS.md router does not mention {name}")
    listing = sum(len(n) + d * 4 for n, d, _ in sizes)
    if listing > 8000:
        errors.append(f"skill names + descriptions are {listing} characters; keep under 8000 for small skill-list budgets")
    print(f"skills: {len(sizes)} checked")
    return sizes


ALWAYS_CAP, BODY_CAP = 2000, 1000


def token_report(sizes):
    """Print the sizes; a broken limit is an error, so --tokens exits 1."""
    prompt = tokens(open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read())
    always = prompt + sum(desc for _, desc, _ in sizes)
    print("\nRough token sizes (four characters per token)")
    print(f"  always loaded: system prompt {prompt} + skill descriptions {always - prompt} = {always}")
    for name, _, body in sizes:
        print(f"  on use: {name:<12} {body}")
    rules = os.path.join(ROOT, "rules")
    for name in sorted(os.listdir(rules)):
        size = tokens(open(os.path.join(rules, name), encoding="utf-8").read())
        print(f"  on demand: rules/{name:<22} {size}")
    if always > ALWAYS_CAP:
        errors.append(f"always-loaded text is {always} tokens; keep it at or under {ALWAYS_CAP}")
    errors.extend(f"skill {name}: body is {body} tokens; keep it under {BODY_CAP}" for name, _, body in sizes if body >= BODY_CAP)

# ---------------------------------------------------------------- report


class Report:
    """Problems of one run: (level, where, message); notes at the end come last."""

    def __init__(self):
        self.items, self.tail = [], []
        self.chapters = self.sections = 0

    def add(self, level, where, msg):
        """Record one problem; where is 'file:line' or ''."""
        item = (level, where, msg)
        if item not in self.items:
            self.items.append(item)

    def count(self, level):
        """Problems of one level, the end notes included."""
        return sum(1 for i in self.items + self.tail if i[0] == level)

    def lines(self):
        """Printable lines: errors, then flags, then notes, then the end notes."""
        order = {"ERROR": 0, "FLAG": 1, "NOTE": 2}
        items = sorted(self.items, key=lambda i: order[i[0]]) + self.tail
        return ["%s %s%s" % (lvl, where + " " if where else "", msg) for lvl, where, msg in items]


def plural(n, word):
    """'1 error', '3 errors'."""
    return "%d %s%s" % (n, word, "" if n == 1 else "s")

# ---------------------------------------------------------------- one book


class Book:
    """A book folder with its plan and its written chapters, parsed once."""

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path.rstrip(os.sep))
        self.plan = bf.load_plan(path)
        self.docs = {}                  # chapter number -> (path, ChapterDoc)
        for f in sorted(os.listdir(os.path.join(path, "chapters"))) if os.path.isdir(os.path.join(path, "chapters")) else []:
            m = re.match(r"^(\d+)-.*\.md$", f)
            if m:
                full = os.path.join(path, "chapters", f)
                self.docs.setdefault(int(m.group(1)), (full, bf.parse_chapter(bf.read_text(full))))

    def rel(self, path, line=None):
        """Book-relative 'chapters/08-x.md:12'."""
        where = os.path.relpath(path, self.path)
        return "%s:%d" % (where, line) if line else where

    def written(self):
        """Every written section in book order: (section, chapter number, path, doc)."""
        out = []
        for n in sorted(self.docs):
            path, doc = self.docs[n]
            out += [(s, n, path, doc) for s in doc.sections]
        return sorted(out, key=lambda x: bf.section_key(x[0].number))

    def docs_of(self, path):
        """The parsed chapter of a chapter file."""
        return next(doc for p, doc in self.docs.values() if p == path)

    def exists(self, number):
        """True if section 'N.M' is planned or written."""
        if self.plan and self.plan.section(number):
            return True
        return any(s.number == number for s, _, _, _ in self.written())


def check_book(bk, only, rep):
    """Every book check, for chapter `only` or the whole book."""
    if bk.plan is None:
        rep.add("ERROR", bk.rel(os.path.join(bk.path, "PLAN.md")), "missing; write it, or run python3 scripts/us_plan.py from-chapters %s" % shown(bk.path))
        return
    check_plan(bk, only, rep)
    for n in sorted(bk.docs):
        if bk.plan.chapter(n) is None and only in (None, n):
            rep.add("ERROR", bk.rel(bk.docs[n][0], 1), "chapter %d is not in PLAN.md; add '### %d Title' and its sections" % (n, n))
    targets = [n for n in sorted(bk.docs) if only in (None, n)]
    if only is not None and only not in bk.docs:
        rep.add("ERROR", "", "chapter %d is not written (no chapters/%02d-*.md)" % (only, only))
    taught = book_markers(bk, only, rep)
    for n in targets:
        path, doc = bk.docs[n]
        rep.chapters += 1
        rep.sections += len(doc.sections)
        check_chapter(bk, n, path, doc, rep)
        if only is not None and doc.sections:
            rep.add("NOTE", bk.rel(path), "words per section: %s (%s)" % (" · ".join(
                "%s %d" % (sec.number, sec.words) for sec in doc.sections), WORDS_COUNTED))
        run_helpers(bk, path, doc, rep)
    used_before_taught(bk, only, taught, rep)
    unpaid_simplified(bk, only, rep)
    if only is None:
        private_inside(bk, rep)
        stale_index(bk, rep)


def check_plan(bk, only, rep):
    """us_plan.py check: errors are ERRORs, warnings NOTEs (in chapter mode, only those of that chapter)."""
    res = bf.run_helper("us_plan.py", ["check", bk.path])
    if res is None:
        rep.add("ERROR", "", "scripts/us_plan.py is missing")
        return
    code, out, err = res
    text = bf.read_text(os.path.join(bk.path, "PLAN.md")).splitlines()
    span = None
    if only is not None and bk.plan.chapter(only):
        ch = bk.plan.chapter(only)
        later = [c.line for c in bk.plan.chapters if c.line > ch.line]
        span = (ch.line, (min(later) - 1) if later else len(text))
    for line in out + err:
        m = re.match(r"^(error|warn) PLAN\.md:(\d+): (.*)$", line)
        if not m:
            if code and not line.startswith("plan ok"):
                rep.add("ERROR", "PLAN.md", line)
            continue
        n = int(m.group(2))
        if 0 < n <= len(text) and bf.EVERYDAY_RE.match(text[n - 1]):
            continue                          # `everyday:` is read by us_check, not by the plan parser
        if m.group(1) == "error":
            rep.add("ERROR", "PLAN.md:%d" % n, m.group(3))
        elif span is None or span[0] <= n <= span[1]:
            rep.add("NOTE", "PLAN.md:%d" % n, m.group(3))


def book_markers(bk, only, rep):
    """Map idea -> (section, path, Teach) for every written teaches marker; duplicate ids are ERRORs."""
    taught = {}
    for sec, n, path, doc in bk.written():
        for t in sec.teaches:
            if t.id in taught:
                first = taught[t.id]
                if only in (None, n, bf.section_key(first[0].number)[0]):
                    rep.add("ERROR", bk.rel(path, t.line), "idea '%s' is marked again (first in %s at %s); keep one marker, rename the other id"
                            % (t.id, first[0].number, bk.rel(first[1], first[2].line)))
                continue
            taught[t.id] = (sec, path, t, doc)
    return taught


def check_chapter(bk, n, path, doc, rep):
    """Shape, beats, ideas, references, fences and links of one written chapter."""
    planned = bk.plan.chapter(n)
    if doc.number and doc.number != n:
        rep.add("ERROR", bk.rel(path, doc.title_line), "heading says chapter %d but the file is chapter %d; fix '# Chapter %d: Title'" % (doc.number, n, n))
    if not doc.title:
        rep.add("ERROR", bk.rel(path, 1), "no '# Chapter %d: Title' heading; add it as the first line" % n)
    for line, text in doc.other_headings:
        rep.add("FLAG", bk.rel(path, line), "'%s' is not a numbered section; make it '## %d.M Title' or a '###' inside one" % (text[:40], n))
    if planned:
        check_order(bk, planned, path, doc, rep)
    for sec in doc.sections:
        psec = bk.plan.section(sec.number)
        kind = plan_kind(psec) if psec else ("practice" if sec.title.lower().startswith("practice") else "lesson")
        terms = [w for t in sec.teaches for w in t.words]
        if kind in ("lesson", "short") and len(terms) > TERMS_MAX:
            rep.add("FLAG", bk.rel(path, sec.line), "%s names %d new terms (%s ...); a beginner holds about three at a "
                    "time: teach each where it is first needed, or split the section" % (sec.number, len(terms), ", ".join(terms[:4])))
        if kind == "lesson":
            check_shape(bk, path, sec, rep)
            if sec.words < LESSON_MIN:
                rep.add("ERROR", bk.rel(path, sec.line), "%s has %s words: a lesson this short has left out a move "
                        "(how it works and why, the real thing worked through, or what goes wrong). Deepen it; or, "
                        "if it truly teaches one small thing, mark it `short` in PLAN.md" % (sec.number, bf.fmt_int(sec.words)))
            elif not LESSON_WORDS[0] <= sec.words <= LESSON_WORDS[1]:
                rep.add("NOTE", bk.rel(path, sec.line), "%s has %s words; a lesson usually runs %s to %s" % (
                    sec.number, bf.fmt_int(sec.words), bf.fmt_int(LESSON_WORDS[0]), bf.fmt_int(LESSON_WORDS[1])))
        elif kind == "short":
            check_short(bk, path, sec, rep)
        elif kind == "practice":
            check_practice(bk, path, sec, rep)
        if psec and "fig" in plan_fields(psec) and not any(f.kind == "fig" for f in sec.figures):
            rep.add("ERROR", bk.rel(path, sec.line), "%s must contain a drawn figure (fig in PLAN.md); add "
                    "'<!-- fig: id=name ... -->', then run python3 scripts/us_draw.py --chapter %s" % (sec.number, shown(path)))
        check_ideas(bk, path, sec, psec, rep)
        check_refs(bk, path, sec, rep)
    refs_in_code(bk, path, doc, rep)
    if (bk.plan.run or "").strip().lower() != "none":
        not_run(bk, path, doc, rep)
    marked = sum(1 for m in scan(doc)[1] if m.kind == "risk")
    if marked:
        rep.add("NOTE", bk.rel(path), "risk: %d marked for review (python3 scripts/us_check.py %s %d --risks)"
                % (marked, shown(bk.path), n))
    for start, end, lang in bf.collect_fences(scan(doc)[0]):
        if not lang:
            rep.add("ERROR", bk.rel(path, start), "fence has no language tag; write ```c, ```text or similar")
    check_links(bk, path, doc, rep)
    repeated_sentences(bk, path, doc, rep)
    new_words(bk, n, path, rep)
    check_programs(bk, path, doc, rep)
    portability(bk, path, doc, rep)
    screen_suggests(bk, n, path, rep)
    recall_questions(bk, path, doc, rep)


def prose_lines(doc, sec):
    """(line, text) of a section's prose, headings and markers left out."""
    return [(ln, text) for ln, kind, text in scan(doc)[0][sec.line:sec.end]
            if kind == "prose" and text.strip() and not text.lstrip().startswith("#")]


def repeated_sentences(bk, path, doc, rep):
    """FLAG a sentence of six words or more written word for word in four or more sections."""
    seen = {}                                     # sentence -> {section: first line}
    for sec in doc.sections:
        for ln, text in prose_lines(doc, sec):
            if text.lstrip().startswith("|"):
                continue                              # a table row (its separator above all) is no sentence
            for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"<[^>]+>", " ", text).strip()):
                key = " ".join(sent.lower().split())
                if len(key.split()) >= 6:
                    seen.setdefault(key, {}).setdefault(sec.number, (ln, sent.strip()))
    for key, where in seen.items():
        if len(where) >= 4:
            ln, sent = min(where.values())
            rep.add("FLAG", bk.rel(path, ln), "'%s' is written word for word in %d sections (%s): say it once, "
                    "or say each its own way" % (sent, len(where), ", ".join(where)))


NEW_WORDS = 12          # most new-word flags per chapter
PATTERN = re.compile(r"[\"'()\[\]{}|]")  # quotes, brackets, a pipe: a pattern or a command, not a word
STRANGE = re.compile(r"^(?:/[\w.-]|--?[A-Za-z][\w=.+-]*$|0\d+$)")  # a path, an option, a number such as 0644


def section_words(doc, sec):
    """(candidates, words) of one section: candidates are (line, word) to be explained where they first
    appear (commands of console lines, and paths, options and 0-numbers there and in inline code), less
    those the section's prose writes in backticks in a sentence of six words or more (that sentence is
    its explanation); words are every word of its console lines, inline code and taught ideas."""
    cands, words = [], {w.lower() for t in sec.teaches for x in t.words for w in [x] + x.split()}
    explained = {w.lower().rstrip(".,;:") for _, text in prose_lines(doc, sec) for sent in re.split(r"(?<=[.!?])\s+", text)
                 if len(sent.split()) >= 6 for span in re.findall(r"`([^`]+)`", sent) for w in [span] + span.split()}
    console = [range(a + 1, b) for a, b, lang in bf.collect_fences(scan(doc)[0]) if lang == "console"]
    for ln in range(sec.line + 1, sec.end + 1):
        line = doc.lines[ln - 1]
        if any(ln in r for r in console):
            if not line.startswith("$ "):
                continue
            k = 0                                   # a quoted argument is a pattern or a text: never a candidate
            for t in re.findall(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'|[|;&]+|(?:[^\s|;&\"']|\"[^\"]*\"|'[^']*')+", line[2:]):
                if re.fullmatch(r"[|;&]+", t):
                    k = 0
                    continue
                words.add(t.strip("'\"").lower())
                if not PATTERN.search(t) and ((k == 0 and not t.startswith("./")) or STRANGE.match(t)):
                    cands.append((ln, t))
                k += 1
        elif scan(doc)[0][ln - 1][1] == "prose":
            for span in re.findall(r"`([^`]+)`", scan(doc)[0][ln - 1][2]):
                if not PATTERN.search(span):        # plainly a command or a pattern, not a word to explain
                    cands += [(ln, t) for t in span.split() if STRANGE.match(t)]
                words |= {w.lower() for w in [span] + span.split()}
    return [(ln, w.rstrip(".,;:")) for ln, w in cands if w.rstrip(".,;:").lower() not in explained
            and not re.fullmatch(r"[-:|]+", w)], words


def subject_command(bk):
    """The book's own subject: the first word of its most common `$` command (git in a Git book), or None."""
    firsts = collections.Counter(doc.lines[ln].split()[1] for _, (_, doc) in bk.docs.items()
                                 for a, b, lang in bf.collect_fences(scan(doc)[0]) if lang == "console"
                                 for ln in range(a, b - 1) if doc.lines[ln].startswith("$ ") and doc.lines[ln].split()[1:])
    return firsts.most_common(1)[0][0] if firsts else None


def new_words(bk, n, path, rep):
    """FLAG commands, options, paths and 0-numbers that no earlier section of the book has shown."""
    seen, found = {subject_command(bk)}, []
    for sec, k, _, doc in bk.written():
        cands, words = section_words(doc, sec)
        if k == n:
            for ln, w in cands:
                if w.lower() not in seen and w not in [x for _, _, x in found]:
                    found.append((ln, sec.number, w))
        seen |= words
    for ln, number, w in found[:NEW_WORDS]:
        rep.add("FLAG", bk.rel(path, ln), "(%s) `%s` first appears here: explain it where it appears, or remove it"
                % (number, w))


def check_programs(bk, path, doc, rep):
    """A POSIX program needs the word POSIX near it; a long program needs a shorter one before it."""
    earlier = []
    for sec in doc.sections:
        said = any("posix" in text.lower() for _, text in prose_lines(doc, sec))
        for c in sec.code:
            if not c.fence or c.lang in ("console", "text"):
                continue
            body = doc.lines[c.fence[0]:c.fence[1] - 1]
            if not said and POSIX_RE.search("\n".join(body)):
                said = True                           # once a section
                rep.add("FLAG", bk.rel(path, c.line), "id=%s includes a POSIX header: say that this is POSIX, "
                        "not standard C" % c.id)
            mine = {x.strip() for x in body if len(x.strip()) > 2}
            if len(body) > 60 and not any(len(mine & other) * 2 >= len(mine) for other in earlier):
                rep.add("NOTE", bk.rel(path, c.line), "id=%s: %d lines with no build-up: grow it from a shorter "
                        "program the reader has seen" % (c.id, len(body)))
            earlier.append(mine)


def session_lines(doc, sec):
    """(line, text) of every line inside the console fences of a section."""
    return [(ln, doc.lines[ln - 1]) for a, b, lang in bf.collect_fences(scan(doc)[0])
            if lang == "console" and sec.line < a <= sec.end for ln in range(a + 1, b)]


# Commands that work differently, or not at all, on another system: (what, pattern, the portable way).
OPT = r"\s(?:[^|;&]*\s)?-[A-Za-z]*"
UNPORTABLE = [
    ("sed -i", r"\bsed" + OPT + "i", "GNU and macOS sed differ on -i: write the file again with printf or a here-document"),
    ("grep -P", r"\bgrep" + OPT + "P", "macOS grep has no -P: use grep -E"),
    ("readlink -f", r"\breadlink" + OPT + "f", "older macOS readlink has no -f: use cd and pwd -P"),
    ("date -d", r"\bdate" + OPT + r"d\b", "macOS date has no -d: show a fixed date instead"),
    ("echo -e", r"\becho\s+-[A-Za-z]*e", "echo -e differs between shells: use printf"),
    ("stat -c", r"\bstat" + OPT + "c", "macOS stat has no -c: use ls -l or wc -c"),
    ("xargs -r", r"\bxargs" + OPT + "r", "macOS xargs has no -r: leave it out where the input is never empty"),
    ("ls --color", r"\bls\s(?:[^|;&]*\s)?--colou?r", "macOS ls has no --color: leave colour out"),
]


def portability(bk, path, doc, rep):
    """FLAG once per chapter each session command that differs between systems; NOTE python3 for Windows."""
    found = collections.OrderedDict()          # what -> [first line, count, level, message]
    linux = "linux" in (bk.plan.audience or "").lower()
    said_py = re.search(r"`py`|`python`", "\n".join(doc.lines))
    for sec in doc.sections:
        for ln, line in session_lines(doc, sec):
            if not line.startswith("$ "):
                continue
            hits = [(what, "FLAG", why) for what, pat, why in UNPORTABLE if re.search(pat, line)]
            for part in re.split(r"[|;&]+", line[2:]):
                words = part.split()
                if words[:1] == ["git"]:
                    words = words[1:]
                if len(words) == 3 and words[0] == "mv" and words[1] != words[2] and words[1].lower() == words[2].lower():
                    hits.append((" ".join(words), "FLAG", "the two names differ only in letter case: on macOS and "
                                 "Windows nothing is seen to change; rename through a third name"))
                if words[:1] == ["python3"] and not linux and not said_py:
                    hits.append(("python3", "NOTE", "on Windows this is `python` or `py`: say so once"))
            for what, level, why in hits:
                entry = found.setdefault(what, [ln, 0, level, why])
                entry[1] += 1
    for what, (ln, count, level, why) in found.items():
        rep.add(level, bk.rel(path, ln), "`%s`%s: %s" % (what, " (%d times)" % count if count > 1 else "", why))


def screen_suggests(bk, n, path, rep):
    """FLAG a command the session output suggests (git's hints) that no prose or taught word up to there explains."""
    subject = subject_command(bk)
    if not subject:
        return
    pat = re.compile(r"(?<![\w-])%s\s+[a-z][\w-]*(?:\s+--?[A-Za-z][\w-]*)*" % re.escape(subject))
    known, found = "", collections.OrderedDict()   # phrase -> [first line, count]
    for sec, k, _, doc in bk.written():
        known += "\n".join(re.sub(r"`", "", text).lower() for _, text in prose_lines(doc, sec))
        known += "\n" + "\n".join(w.lower() for t in sec.teaches for w in t.words) + "\n"
        if k != n:
            continue
        for ln, line in session_lines(doc, sec):
            if line.startswith("$ "):
                continue
            for m in pat.finditer(line):
                phrase = " ".join(m.group(0).split())
                if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(phrase.lower()).replace(r"\ ", r"\s+"), known):
                    found.setdefault(phrase, [ln, 0])[1] += 1
    for phrase, (ln, count) in found.items():
        rep.add("FLAG", bk.rel(path, ln), "the screen suggests `%s`%s and the book never explains it: teach it or "
                "point to the section that will" % (phrase, " (%d times)" % count if count > 1 else ""))


RECALL = re.compile(r"\b(?:what is|what are|name (?:the|one|two|three|four|a|an|each)|which command|how many|short form)\b", re.I)


def recall_questions(bk, path, doc, rep):
    """NOTE a Check yourself with more than one question that only asks to recall: no program, session or
    code in it (not even `inline`), and wording such as "what is" or "which command"."""
    scanned = scan(doc)[0]
    for sec in doc.sections:
        if not sec.check_line:
            continue
        questions, cur, depth = [], None, 0
        for ln in range(sec.check_line + 1, sec.end + 1):
            line = doc.lines[ln - 1]
            depth += line.count("<details>") - line.count("</details>")
            if depth or "</details>" in line:
                cur = None
                continue
            if scanned[ln - 1][1] == "prose" and re.match(r"^\s*\d+\.\s", line):
                cur = [ln, "", False]
                questions.append(cur)
            if cur is not None:
                cur[1] += " " + scanned[ln - 1][2]
                cur[2] |= scanned[ln - 1][1] != "prose" or "<!--" in line or "`" in line
        recall = [q for q in questions if not q[2] and RECALL.search(q[1])]
        if len(recall) > 1:
            rep.add("NOTE", bk.rel(path, recall[0][0]), "%s Check yourself: %d questions only ask to recall (%s): "
                    "make one predict output, find the fault or write a line" % (
                        sec.number, len(recall), ", ".join(re.match(r"\s*(\d+)", q[1]).group(1) for q in recall)))


def check_order(bk, planned, path, doc, rep):
    """Written sections are the planned ones, in plan order; titles match."""
    want = [s.number for s in planned.sections]
    got = [s.number for s in doc.sections]
    for sec in doc.sections:
        psec = bk.plan.section(sec.number)
        if psec is None or psec.chapter != planned.number:
            rep.add("ERROR", bk.rel(path, sec.line), "%s is not in chapter %d of PLAN.md; renumber it or add it to the plan" % (sec.number, planned.number))
        elif bf.anchor(psec.title).replace("-", "") != bf.anchor(sec.title).replace("-", ""):
            rep.add("FLAG", bk.rel(path, sec.line), "title differs from PLAN.md '%s'; make them match" % psec.title)
    seen = [g for g in got if g in want]
    if seen != sorted(seen, key=bf.section_key) or len(set(seen)) != len(seen):
        rep.add("ERROR", bk.rel(path, doc.sections[0].line), "sections out of plan order or repeated: %s; order is %s" % (" ".join(got), " ".join(want)))
        return
    missing = [w for w in want if w not in got]
    status = bf.read_status(bk.path)["chapters"].get(str(planned.number), {}).get("state", "")
    gaps = [w for w in missing if seen and bf.section_key(w) < bf.section_key(seen[-1])]
    if gaps:
        rep.add("NOTE", bk.rel(path, 1), "planned section%s %s not written yet, between written ones (sections written "
                "out of order): write %s when the learner needs %s" % ("s" if len(gaps) > 1 else "", ", ".join(gaps),
                "them" if len(gaps) > 1 else "it", "them" if len(gaps) > 1 else "it"))
    elif missing and status in ("written", "reviewed"):
        rep.add("ERROR", bk.rel(path, 1), "STATUS.json says %s but %s not written" % (status, ", ".join(missing)))
    elif missing:
        rep.add("NOTE", bk.rel(path, 1), "%d of %d sections written; next is %s" % (len(seen), len(want), missing[0]))


def check_shape(bk, path, sec, rep):
    """Headings are free (rules/writers-guide.md); a Check yourself with at least one hidden answer is required."""
    if not sec.check_line:
        rep.add("ERROR", bk.rel(path, sec.end), "%s has no '**Check yourself**'; end the section with it and at least "
                "one question, its answer in <details>" % sec.number)
    elif sec.answers < 1:
        rep.add("ERROR", bk.rel(path, sec.check_line), "%s Check yourself has no hidden answer; put each answer in <details>" % sec.number)


LESSON_WORDS = (1200, 3000)            # rules/writers-guide.md: advice, a NOTE outside it
SHORT_WORDS = (300, 700)
LESSON_MIN = 900                      # under it a lesson is an ERROR: it has left out a move
SHORT_MIN = 200                        # under it even a `short` section is an ERROR
TERMS_MAX = 7                          # more new terms than this in one section is a FLAG
PRACTICE_MIN = 3                       # tasks with a hidden answer: guided, on your own, a small project
WORDS_COUNTED = ("prose, programs, sessions and hidden answers are counted; headings, markers, "
                 "<summary> lines and pasted output are not")


def plan_fields(psec):
    """The `|` fields of a plan section line, lower case ('fig', 'short', 'teaches: x', ...)."""
    return [f.strip().lower() for f in psec.raw.split("|")[1:] if f.strip()]


def plan_kind(psec):
    """The section's kind; `short` read from the raw line too, in case the parser does not know it."""
    return "short" if any(re.fullmatch(r"(?:kind\s*:\s*)?short", f) for f in plan_fields(psec)) else psec.kind


def check_short(bk, path, sec, rep):
    """A short section: a Check yourself with a question; 300 to 700 words is advice."""
    if not sec.check_line or sec.answers < 1:
        rep.add("ERROR", bk.rel(path, sec.check_line or sec.end), "%s (short) needs a '**Check yourself**' with at least "
                "one question and its answer in <details>" % sec.number)
    if sec.words < SHORT_MIN:
        rep.add("ERROR", bk.rel(path, sec.line), "%s has %s words: too thin even for a short section" % (
            sec.number, bf.fmt_int(sec.words)))
    elif not SHORT_WORDS[0] <= sec.words <= SHORT_WORDS[1]:
        rep.add("NOTE", bk.rel(path, sec.line), "%s has %s words; a short section usually runs %s to %s" % (
            sec.number, bf.fmt_int(sec.words), SHORT_WORDS[0], SHORT_WORDS[1]))


def check_practice(bk, path, sec, rep):
    """A practice climbs: at least PRACTICE_MIN tasks, each with its answer in <details>."""
    if sec.details < PRACTICE_MIN:
        rep.add("ERROR", bk.rel(path, sec.line), "%s is practice with %d answered tasks; give at least three that "
                "climb: guided, on your own, a small project or case" % (sec.number, sec.details))


def refs_in_code(bk, path, doc, rep):
    """ERROR for a §N.M inside a fence or inline code: the reader would type it as part of the command."""
    for ln, kind, text in scan(doc)[0]:
        spans = [text] if kind == "code" else re.findall(r"`[^`]+`", text) if kind == "prose" else []
        for m in (m for span in spans for m in bf.REF_RE.finditer(span)):
            rep.add("ERROR", bk.rel(path, ln), "a section reference inside a command (§%s.%s): take it out of the "
                    "code and put it after the sentence" % m.groups())


def not_run(bk, path, doc, rep):
    """Count programs and sessions that were not run here (unrun=, or a console fragment with `$ ` lines)."""
    blocks, idle = 0, []
    for c in (c for s in doc.sections for c in s.code if c.fence):
        command = c.lang == "console" and any(l.startswith("$ ") for l in doc.lines[c.fence[0]:c.fence[1] - 1])
        if c.mode != "fragment" or command:
            blocks += 1
            if "unrun" in c.attrs or c.mode == "fragment":
                idle.append(c.id or "line %d" % c.line)
    if not idle:
        return
    rep.add("NOTE", bk.rel(path), "not run here: %d of %d (%s)" % (len(idle), blocks, ", ".join(idle)))
    if len(idle) > 2 and len(idle) * 4 > blocks:
        rep.add("ERROR", bk.rel(path), "too much of this chapter cannot be run on this machine: stop and ask the learner "
                "(run python3 scripts/us_doctor.py %s)" % shown(bk.path))


def check_ideas(bk, path, sec, psec, rep):
    """Every idea the plan lists for the section has its marker there."""
    ids = [t.id for t in sec.teaches]
    for idea in (psec.teaches if psec and plan_kind(psec) in ("lesson", "short") else []):
        if idea not in ids:
            rep.add("ERROR", bk.rel(path, sec.line), "%s has no marker for planned idea '%s'; add '<!-- teaches: %s = words -->' above its definition" % (sec.number, idea, idea))
    teacher = bk.plan.teacher()
    for t in sec.teaches:
        if psec and t.id not in psec.teaches:
            other = teacher.get(t.id)
            where = "planned for %s" % other.number if other else "not in PLAN.md"
            rep.add("FLAG", bk.rel(path, t.line), "idea '%s' is %s; fix the id or the plan" % (t.id, where))


SECTION_WORD_RE = re.compile(r"\bsections?\s+(\d+)\.(\d+)\b", re.I)
CHAPTER_WORD_RE = re.compile(r"\bchapters?\s+(\d+)\b(?!\.\d)", re.I)


def dangling(bk, doc, sec):
    """(level, line, message) for each §N.M, 'section N.M' or 'chapter N' in prose that the plan does not
    have (ERROR), or that is planned, not written and earlier in the book than this section (NOTE)."""
    out, seen = [], set()
    found = [(ref, line) for ref, line in sec.refs]
    for line, text in prose_lines(doc, sec):
        text = re.sub(r"`[^`]*`", "", text)
        found += [("%d.%d" % (int(a), int(b)), line) for a, b in SECTION_WORD_RE.findall(text)]
        found += [("chapter %d" % int(c), line) for c in CHAPTER_WORD_RE.findall(text)]
    written = {s.number for s, _, _, _ in bk.written()}
    for ref, line in found:
        if (ref, line) in seen:
            continue
        seen.add((ref, line))
        if ref.startswith("chapter"):
            if bk.plan.chapter(int(ref.split()[1])) is None:
                out.append(("ERROR", line, "points to %s, which the plan does not have; fix the number" % ref))
        elif not bk.plan.section(ref):
            out.append(("ERROR", line, "points to %s, which the plan does not have; fix the number" % ref))
        elif ref not in written and bf.section_key(ref) < bf.section_key(sec.number):
            out.append(("NOTE", line, "points to %s, which comes earlier but is not written yet" % ref))
    return out


def check_refs(bk, path, sec, rep):
    """References point into the plan (see dangling); later sections are one NOTE per section."""
    forward = []
    for level, line, msg in dangling(bk, bk.docs_of(path), sec):
        rep.add(level, bk.rel(path, line), "%s %s" % (sec.number, msg))
    for ref, line in sec.refs:
        if bk.plan.section(ref) and bf.section_key(ref) > bf.section_key(sec.number) and "§" + ref not in forward:
            forward.append("§" + ref)
    for value, line in sec.resolves:
        ref = value.strip().lstrip("§")
        if re.match(r"^\d+\.\d+$", ref) and not bk.exists(ref):
            rep.add("ERROR", bk.rel(path, line), "resolves %s, which is not a section; fix the number" % ref)
    if forward:
        line = next(l for r, l in sec.refs if "§" + r == forward[0])
        rep.add("NOTE", bk.rel(path, line), "%s refers forward to %s; %s" % (sec.number, ", ".join(forward), (
            "more than two forward references: teach what the section needs, and promise less")
            if len(forward) > 2 else "fine if it is a promise"))


LINK_RE = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
ANCHORS = {}


def anchors_of(path):
    """Heading anchors of a Markdown file, cached."""
    if path not in ANCHORS:
        ANCHORS[path] = bf.heading_anchors(bf.read_text(path).splitlines()) if os.path.exists(path) else set()
    return ANCHORS[path]


def check_links(bk, path, doc, rep):
    """Relative links and images resolve; #anchors name a heading."""
    scanned, _ = scan(doc)
    here = os.path.dirname(path)
    for n, kind, body in scanned:
        if kind != "prose":
            continue
        for target in LINK_RE.findall(re.sub(r"`[^`]*`", "", body)):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            file, _, frag = target.partition("#")
            full = os.path.normpath(os.path.join(here, file)) if file else path
            if file and not os.path.exists(full):
                rep.add("ERROR", bk.rel(path, n), "link to %s, which does not exist; fix the path" % target)
            elif frag and full.endswith(".md") and frag not in anchors_of(full):
                rep.add("ERROR", bk.rel(path, n), "link to #%s, which names no heading; run python3 scripts/us_index.py %s or fix it" % (frag, shown(bk.path)))


def run_helpers(bk, path, doc, rep):
    """us_run.py --check once per chapter; us_draw.py --check on every figure; image lines present."""
    if any(c.mode != "fragment" for s in doc.sections for c in s.code) or any("```console" in l for l in doc.lines):
        res = bf.run_helper("us_run.py", [path, "--check"])
        if res is None:
            rep.add("ERROR", "", "scripts/us_run.py is missing")
        elif res[0] != 0:
            hits = 0
            for line in res[1] + res[2]:
                m = re.match(r"^\S+?:(\d+)\s+(.*?)\s*(?:\((run [^)]*)\))?$", line)
                if m and not line.startswith("warning:"):
                    hits += 1
                    msg = re.sub(r"\s{2,}", " ", m.group(2))
                    rep.add("ERROR", bk.rel(path, int(m.group(1))), msg + ("; " + m.group(3) if m.group(3) else ""))
            if not hits:
                rep.add("ERROR", bk.rel(path), "us_run.py --check failed (exit %d): %s" % (res[0], " ".join(res[1] + res[2])[-200:]))
    svgs = []
    for sec in doc.sections:
        for fig in sec.figures:
            svg = figure_image(bk, path, doc, fig, rep)
            if svg:
                svgs.append((svg, fig))
    if svgs:
        res = bf.run_helper("us_draw.py", ["--check"] + [s for s, _ in svgs])
        if res and res[0] != 0:
            for line in res[1] + res[2]:
                if line.startswith("ok "):
                    continue
                fig = next((f for s, f in svgs if os.path.basename(s) in line), None)
                where = bk.rel(path, fig.span[0]) if fig else bk.rel(path)
                rep.add("ERROR", where, "figure: %s; fix the description, then: python3 scripts/us_draw.py --chapter %s" % (line.split(" ", 1)[-1].strip(), shown(path)))


def figure_image(bk, path, doc, fig, rep):
    """Check a figure's image line; return its SVG path when it is a drawn fig: figure."""
    if not fig.id:
        rep.add("ERROR", bk.rel(path, fig.span[0]), "figure marker has no id; start it '<!-- %s: id=name'" % fig.kind)
        return None
    after = [l.strip() for l in doc.lines[fig.span[1]:fig.span[1] + 3]]
    img = next((l for l in after if l), "")
    m = re.match(r"^!\[.*\]\(([^)\s]+)\)\s*$", img)
    if not m:
        rep.add("ERROR", bk.rel(path, fig.span[1]), "figure '%s' has no image line below it; run python3 scripts/us_draw.py --chapter %s" % (fig.id, shown(path)))
        return None
    if fig.kind != "fig" or not m.group(1).endswith(".svg"):
        return None
    svg = os.path.normpath(os.path.join(os.path.dirname(path), m.group(1)))
    return svg if os.path.exists(svg) else None      # a missing file is reported by the link check


def used_before_taught(bk, only, taught, rep):
    """FLAG the first use of an idea's words in a section before the one that teaches it."""
    everyday = bf.everyday_words(bk.path)
    text, spans = prose_index(bk, only)
    if not text:
        return
    ideas = []
    for idea, (sec, path, t, doc) in taught.items():
        words, guessed = bf.idea_words(t, doc.lines)
        ideas.append((idea, sec.number, words, guessed))
    for idea, psec in bk.plan.teacher().items():
        if idea not in taught and re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", idea):
            ideas.append((idea, psec.number, [bf.humanise(idea)], True))
    terms = [(re.sub(r"\s+", " ", w.lower()), number) for _, number, words, _ in ideas for w in words]
    earlier, found = [], []                             # words of ideas taught before (lower case); flags
    for idea, number, words, guessed in sorted(ideas, key=lambda i: bf.section_key(i[1])):
        keep = [w for w in words if w.lower() not in everyday and len(w) > 1 and w.lower() not in earlier
                and not (guessed and any(re.search(r"(?<!\w)%s(?!\w)" % re.escape(w.lower()), e) for e in earlier))]
        earlier += [w.lower() for w in words]
        words = keep
        if not words:
            continue
        limit = next((s[0] for s in spans if bf.section_key(s[2]) >= bf.section_key(number)), len(text))
        pat = re.compile(r"(?<![\w-])(?:%s)(?![\w-])" % "|".join(
            (r"(?i:%s)" if not re.search(r"[A-Z]", w[1:]) else "%s") % re.escape(w).replace(r"\ ", r"\s+")
            for w in sorted(words, key=len, reverse=True)))
        # everyday English ('variable', or a guessed 'depends on'): flagged only in bold
        plain = {w.lower() for w in words if re.fullmatch(r"[a-z]+" if not guessed else r"[a-z]+(?: [a-z]+)*", w)}
        flagged = set()                                    # sections where this idea is flagged already
        for m in pat.finditer(text, 0, limit):
            start, end, sec_no, path, line_of = span_at(spans, m.start())
            line_no, line_text = line_of(m.start())
            if sec_no in flagged or "§" + number in line_text or re.search(
                    r"(?i)\bsections?\b(?:[^.;:]|(?<=\d)\.(?=\d))*?(?<![\d.])%s(?!\d)" % re.escape(number), line_text):
                continue                                   # once a section; a forward promise, as the standard asks
            if inside_taught(text, m, sec_no, terms):
                continue                                   # part of a longer term taught by now
            said = re.sub(r"\s+", " ", m.group(0))
            if said.lower() in plain and not any(re.search(r"(?i)(?<!\w)%s(?!\w)" % re.escape(said).replace(r"\ ", r"\s+"), span)
                                                 for span in re.findall(r"\*\*.+?\*\*", re.sub(r"`[^`]*`", "", line_text))):
                continue
            flagged.add(sec_no)
            found.append((path, line_no, "(%s) '%s' is used here but taught in %s; say it in plain words here instead, or, only if "
                          "the reader must look ahead, add (§%s) after the sentence" % (sec_no, said, number, number)))
    for path, line_no, msg in sorted(found):
        rep.add("FLAG", bk.rel(path, line_no), msg)


def inside_taught(text, m, sec_no, terms):
    """True if match m of text lies inside a longer term taught at or before section sec_no."""
    word = re.sub(r"\s+", " ", m.group(0).lower())
    for term, number in terms:
        if word in term and term != word and bf.section_key(number) <= bf.section_key(sec_no):
            start = max(0, m.start() - len(term))
            pat = re.compile(re.escape(term).replace(r"\ ", r"\s+"), re.I)
            if any(o.start() <= m.start() and o.end() >= m.end() for o in pat.finditer(text, start, m.end() + len(term))):
                return True
    return False


SCANS = {}


def scan(doc):
    """bf.scan_lines of a chapter, cached."""
    if id(doc) not in SCANS:
        SCANS[id(doc)] = bf.scan_lines(doc.lines)
    return SCANS[id(doc)]


def prose_index(bk, only):
    """One string of all section prose in book order; spans of (start, end, section, path, line lookup)."""
    parts, spans, pos = [], [], 0
    for sec, n, path, doc in bk.written():
        if only is not None and n != only:
            continue
        scanned, _ = scan(doc)
        lines, offs = [], []
        for ln, kind, body in scanned[sec.line - 1:sec.end]:
            if kind != "prose" or re.match(r"^\s*#{3,}\s", body) or "<summary>" in body:
                continue
            clean = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), re.sub(r"\]\([^)]*\)", "]", body)).replace("`", "")
            offs.append((pos + sum(len(x) + 1 for x in lines), ln, body))
            lines.append(clean)
        chunk = "\n".join(lines) + "\n"
        spans.append((pos, pos + len(chunk), sec.number, path, offs))
        parts.append(chunk)
        pos += len(chunk)
    return "".join(parts), spans


def span_at(spans, at):
    """The section span holding text offset `at`, with a function from offset to (line, raw text)."""
    for start, end, number, path, offs in spans:
        if start <= at < end:
            def line_of(p, offs=offs):
                best = offs[0]
                for o in offs:
                    if o[0] > p:
                        break
                    best = o
                return best[1], best[2]
            return start, end, number, path, line_of
    raise ValueError(at)


def unpaid_simplified(bk, only, rep):
    """'Simplified here' boxes no later `resolves` marker repays: notes at the end."""
    written = bk.written()
    for i, (sec, n, path, doc) in enumerate(written):
        if not sec.simplified or only not in (None, n):
            continue
        later = {v.strip().lstrip("§") for s, _, _, _ in written[i:] for v, _ in s.resolves}
        if sec.number not in later:
            for line, _ in sec.simplified:
                rep.tail.append(("NOTE", bk.rel(path, line), "'Simplified here' is not repaid yet; add '<!-- resolves: %s -->' where a later section does" % sec.number))


PERSONAL = {"now.md", "goal.md", "route.md", "levels.yaml", "weaknesses.md", "week.md", "build.md",
            "compete.md", "costs.md", "interviews", "logs", "scratch"}


def private_inside(bk, rep):
    """Personal records must never sit inside the book."""
    for folder, dirs, files in os.walk(bk.path):
        dirs[:] = [d for d in dirs if d != ".git"]
        for item in sorted(set(dirs + files) & PERSONAL):
            rep.add("ERROR", bk.rel(os.path.join(folder, item)), "personal record inside the book; move it to the private folder")


def stale_index(bk, rep):
    """NOTE when README.md, KEYTERMS.md or INDEX.md is older than a chapter and would change if rebuilt."""
    if not bk.docs:
        return                                    # nothing written: nothing to index
    newest = max([os.path.getmtime(p) for p, _ in bk.docs.values()] + [os.path.getmtime(os.path.join(bk.path, "PLAN.md"))])
    made = [os.path.join(bk.path, f) for f in ("README.md", "KEYTERMS.md", "INDEX.md")]
    if all(os.path.exists(p) and os.path.getmtime(p) >= newest for p in made):
        return
    try:                                          # us_index leaves a file alone when its text is unchanged
        import us_index
        ix = us_index.BookIndex(bk.path, os.path.dirname(bk.path.rstrip(os.sep)))
        if all(os.path.exists(p) and bf.read_text(p) == text for p, text in zip(made, (ix.readme(), ix.keyterms(), ix.index_md()))):
            return
    except Exception:                             # noqa: BLE001 - an index that cannot be built is reported as stale
        pass
    rep.add("NOTE", "", "the book's index is older than its chapters; run python3 scripts/us_index.py %s" % shown(bk.path))

# ---------------------------------------------------------------- suspects

SWEEP = {"impossible": 15, "guaranteed": 15, "never": 12, "always": 12, "cannot": 10, "none": 8,
         "must": 6, "exactly": 8, "every": 4, "all": 3, "only": 4}
SWEEP_RE = re.compile(r"\b(%s)\b" % "|".join(SWEEP), re.I)
UNIT = r"(?:bytes?|bits?|KB|MB|GB|TB|KiB|MiB|GiB|kB|ms|ns|µs|seconds?|milliseconds?|nanoseconds?|Hz|MHz|GHz)"
NUM_RE = re.compile(r"(?<![\w.§-])(\d[\d,]*(?:\.\d+)?)(\s?%s\b|-bit\b|%%)?" % UNIT)
SKIP_NUM = re.compile(r"(?:§|\b(?:line|lines|step|steps|exercise|question|figure|chapter|section|part|level|beat)s?\s+"
                      r"|\blines?\s+\d+\s*(?:to|and|-|–)\s*)$", re.I)
MACHINE_RE = re.compile(r"\b\d+\s?(?:bytes?|bits?|-bit|KB|MB|GB|KiB|MiB|GiB)\b|\b0x[0-9a-f]{4,}\b"
                        r"|\baddress(?:es)?\s+(?:is\s+|of\s+\S+\s+is\s+)?\d{3,}|sizeof\s*\(?[\w *]*\)?\s+(?:is|gives|returns|==?)\s+\d+"
                        r"|\b\d+(?:\.\d+)?\s?(?:ms|ns|µs|seconds?|milliseconds?|nanoseconds?|GHz|MHz)\b", re.I)
HERE_RE = re.compile(r"on (?:this|your|my|a typical|most|the test|a) (?:machine|computer|system|laptop)|made-up|imagin|pretend"
                     r"|suppose|for example|typical", re.I)
PRINTS_RE = re.compile(r"\b(?:prints?|printed|outputs?|displays?|shows on the screen)\b", re.I)
RISK = ["answer", "ref", "trace", "number", "machine", "sweeping", "forward"]      # most risky first
CAP = {"answer": 10, "ref": 8, "trace": 16, "number": 14, "machine": 6, "sweeping": 4, "forward": 2}
SHOWN = 38                                    # with the two closing lines, never more than 40 lines
CLEARING = "clear each line shown: true as written, or scoped to this system or machine, or fixed."
UNSHOWN = " The %d not shown rank lower: sample them only if time allows."
CLAIMLESS = ("The question", "The picture", "Remember")   # beats that set a scene, not claims about code


def suspects(bk, n, every=False):
    """Print the reviewer's list for chapter n: line, kind, excerpt; most suspicious first (every: no cap)."""
    if n not in bk.docs:
        print("chapter %d is not written" % n)
        return 1
    path, doc = bk.docs[n]
    found = {}                          # line -> [kinds, excerpt]

    def hit(line, kind, excerpt):
        entry = found.setdefault(line, [[], excerpt])
        if kind not in entry[0]:
            entry[0].append(kind)
    scanned, markers = bf.scan_lines(doc.lines)
    kinds = {ln: kind for ln, kind, _ in scanned}
    terms = [w for s, _, _, _ in bk.written() for t in s.teaches for w in t.words or [bf.humanise(t.id)]
             if not re.fullmatch(r"[a-z]+", w)]    # everyday words are no sign of a claim about code
    taught_in = {}                                 # term (lower case) -> first section teaching it
    for s, _, _, _ in bk.written():
        for t in s.teaches:
            for w in t.words or [bf.humanise(t.id)]:
                taught_in.setdefault(w.lower(), s.number)
    terms = re.compile(r"(?<![\w-])(?:%s)(?![\w-])" % "|".join(map(re.escape, sorted(set(terms), key=len, reverse=True))),
                       re.I) if terms else None
    for sec in doc.sections:
        sec_suspects(bk, doc, sec, scanned, kinds, markers, hit, terms)
        ref_suspects(bk, doc, sec, hit, terms, taught_in)
    counts = {k: sum(1 for ks, _ in found.values() if k in ks) for k in RISK}
    digits = lambda ln: max([len(x) for x in re.findall(r"\d+", doc.lines[ln - 1])] + [0])
    ranked = sorted(found.items(), key=lambda kv: (min(RISK.index(k) for k in kv[1][0]), -digits(kv[0]),
                                                  -len(kv[1][0]), kv[0]))   # in a kind: longer numbers, more signs
    shown, per = [], {k: 0 for k in RISK}
    for line, (ks, excerpt) in ranked:
        first = min(ks, key=RISK.index)
        if every or (per[first] < CAP[first] and len(shown) < SHOWN):
            per[first] += 1
            shown.append("%d %s %s" % (line, "+".join(sorted(ks, key=RISK.index)), excerpt))
    print("\n".join(shown + ["suspects %s ch %d: %d lines%s; %s" % (
        bk.name, n, len(found), " (%d shown)" % len(shown) if len(shown) < len(found) else "",
        ", ".join("%s %d" % (k, counts[k]) for k in RISK)),
        CLEARING + (UNSHOWN % (len(found) - len(shown)) if len(shown) < len(found) else "")] if found else ["suspects %s ch %d: none" % (bk.name, n)]))
    return 0


def excerpt(text, at=0, size=12):
    """At most `size` words of text around offset `at`, markup stripped."""
    words = text[:at].split()[-3:] + text[at:].split()
    out = re.sub(r"[*_`]|<[^>]+>", "", " ".join(words[:size])).strip()
    return out


def sec_suspects(bk, doc, sec, scanned, kinds, markers, hit, terms=None):
    """Find every kind of suspect in one section."""
    lines = doc.lines
    traced = {mk.end + 1 for mk in markers if mk.kind == "trace"}     # tables a script made from a real run
    scene = [r for r in (bf.beat_range(doc, sec, b) for b in CLAIMLESS) if r]
    psec = bk.plan.section(sec.number) if bk.plan else None
    practice = bool(psec and psec.kind == "practice")
    body = [(ln, kind, text) for ln, kind, text in scanned if sec.line < ln <= sec.end]
    evidence = set()
    for ln, kind, text in body:
        if kind == "code" or (kind == "prose" and text.lstrip().startswith("|")):
            evidence |= set(re.findall(r"\d[\d,]*(?:\.\d+)?", text.replace(",", "")))
    trace = bf.beat_range(doc, sec, "The trace")
    if trace:
        start = None
        for ln in range(trace[0], trace[1] + 2):
            row = ln <= trace[1] and kinds.get(ln) == "prose" and lines[ln - 1].lstrip().startswith("|")
            if row and start is None:
                start = ln
            elif not row and start is not None and start in traced:
                start = None
            elif not row and start is not None:
                hit(start, "trace", "lines %d-%d: %s" % (start, ln - 1, excerpt(lines[start - 1], 0, 10)))
                start = None
    for ref, ln in sec.refs:
        if bf.section_key(ref) > bf.section_key(sec.number):
            text = lines[ln - 1]
            at = next((m.start() for m in bf.REF_RE.finditer(text) if "%d.%d" % tuple(map(int, m.groups())) == ref), 0)
            hit(ln, "forward", excerpt(text[at:]))               # from this reference, not an earlier one on the line
    answer_suspects(doc, sec, markers, hit)
    in_details = 0
    for idx, (ln, kind, text) in enumerate(body):
        in_details += lines[ln - 1].count("<details>") - lines[ln - 1].count("</details>")
        if kind != "prose" or not text.strip() or text.lstrip().startswith(("#", "|", "![")):
            continue
        if not in_details and (practice or 0 < sec.check_line < ln):
            continue                                          # a question sets up a case; it claims nothing
        prose = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), text)
        for sent in re.finditer(r"[^.!?]+[.!?]?", prose) if not in_details and not any(
                a <= ln <= b for a, b in scene) else []:
            found = list(SWEEP_RE.finditer(sent.group(0)))
            raw = text[sent.start():sent.end()]
            if found and ("`" in raw or re.search(r"\d", raw) or (terms and terms.search(raw))):
                strongest = max(found, key=lambda m: SWEEP[m.group(1).lower()])
                hit(ln, "sweeping", excerpt(text, sent.start() + strongest.start()))
        near = " ".join(lines[max(0, ln - 2):ln + 1])
        for m in NUM_RE.finditer(prose):
            value, unit = m.group(1).replace(",", ""), m.group(2)
            if SKIP_NUM.search(prose[:m.start()]) or re.match(r"^\d+\.\d+$", value) and "§" in prose[max(0, m.start() - 2):m.start()]:
                continue
            if re.match(r"^\s*\d+\.\s", prose) and m.start() == len(prose) - len(prose.lstrip()):
                continue                                      # a numbered list item
            if (len(value.replace(".", "")) >= 2 or unit) and value not in evidence:
                hit(ln, "number", excerpt(text, m.start()))
                break
        if MACHINE_RE.search(prose) and not HERE_RE.search(near):
            hit(ln, "machine", excerpt(text, MACHINE_RE.search(prose).start()))


def ref_suspects(bk, doc, sec, hit, terms, taught_in):
    """A sentence naming earlier-taught terms beside a § reference to an earlier section that teaches
    none of them: the reference may point at the wrong section."""
    teaches = {s.number for s, _, _, _ in bk.written() if s.teaches}
    here = bf.section_key(sec.number)
    for ln, text in prose_lines(doc, sec) if terms else []:
        for sent in re.split(r"(?<=[.!?])\s+", text):
            refs = {"%d.%d" % (int(a), int(b)) for a, b in bf.REF_RE.findall(sent)}
            refs = {r for r in refs if bf.section_key(r) < here and r in teaches}
            used = {m.group(0).lower(): taught_in.get(m.group(0).lower()) for m in terms.finditer(sent)}
            used = {w: s for w, s in used.items() if s and bf.section_key(s) < here}
            if refs and used and not refs & set(used.values()):
                w, s = sorted(used.items())[0]
                hit(ln, "ref", "%s; '%s' is taught in §%s" % (excerpt(sent, 0, 10).rstrip(".,;:"), w, s))


def answer_suspects(doc, sec, markers, hit):
    """Answers that say what a program prints with no run program in the question or the answer."""
    lines = doc.lines
    run_lines = [mk.start for mk in markers if mk.kind == "code" and sec.line < mk.start <= sec.end
                 and bf.parse_attrs(mk.body).get("mode", "run") in ("run", "warns")]
    start_q = sec.check_line or (sec.line if any(s for s in [sec.details]) else 0)
    if not start_q:
        return
    prev, open_at = start_q, None
    for ln in range(start_q, sec.end + 1):
        text = lines[ln - 1]
        if "<details>" in text:
            open_at = ln
        elif "</details>" in text and open_at:
            answer = " ".join(lines[open_at:ln - 1])
            backed = any(prev <= r <= ln for r in run_lines)
            m = PRINTS_RE.search(re.sub(r"<[^>]+>", "", answer))
            if m and not backed:
                first = next((i for i in range(open_at, ln) if PRINTS_RE.search(lines[i - 1])), open_at)
                hit(first, "answer", excerpt(lines[first - 1], PRINTS_RE.search(lines[first - 1]).start()))
            prev, open_at = ln, None

# ---------------------------------------------------------------- prose view for the reviewer


def folds(doc):
    """Map first line -> (last line, one-line summary) for each program (with its output) and figure."""
    out = {}
    for sec in doc.sections:
        for c in sec.code:
            if not c.fence:
                continue
            body = doc.lines[c.fence[0]:c.fence[1] - 1]
            what = "fragment" if c.mode == "fragment" else "program"
            text = "%s id=%s: %s, %s" % (what, c.id, c.lang or "untagged", plural(len(body), "line"))
            if c.lang == "console":           # a session: its commands, and the first of what they print
                starts = dict(command_spans(body))   # a here-document's lines belong to its command
                inside = {i for a, b in starts.items() for i in range(a, b + 1)}
                cmds = [l + (" …" if starts.get(i, i) > i else "") for i, l in enumerate(body)
                        if i in starts or (i not in inside and l.startswith("> "))]
                got = [l for i, l in enumerate(body) if i not in inside and not l.startswith("> ")]
                text = "session id=%s: %s; %s" % (c.id, " ; ".join(cmds), "output %s: %s" % (plural(len(got), "line"), " / ".join(
                    '"%s"' % (l if len(l) <= 40 else l[:40] + "…") for l in [x for x in got if x.strip()][:2])) if got else "no output")
                out[c.line] = (c.fence[1], "[%s]" % text)
                continue
            if what == "program":
                text += "; " + {"run": "ran", "compile": "compiled"}.get(c.mode, c.mode)
            if c.output:
                got = doc.lines[c.output[0]:c.output[1] - 1]
                shown = " / ".join('"%s"' % (l if len(l) <= 40 else l[:40] + "…") for l in got[:2])
                text += "; output %s: %s" % (plural(len(got), "line"), shown) if got else "; no output"
            elif what == "program" and c.mode in ("run", "warns", "error") and "answer" not in c.attrs:
                text += "; no output"
            out[c.line] = ((c.output or c.fence)[1], "[%s]" % text)
        for f in sec.figures:
            end, alt = f.span[1], ""
            nxt = next((i for i in range(end, min(end + 3, len(doc.lines))) if doc.lines[i].strip()), None)
            m = re.match(r"^!\[(.*)\]\([^)]*\)\s*$", doc.lines[nxt]) if nxt is not None else None
            if m:
                end, alt = nxt + 1, m.group(1)
            out[f.span[0]] = (end, "[figure id=%s: %s]" % (f.id, alt or "no image yet"))
    return out


def prose(bk, n, start=1, k=150):
    """Print chapter n for the reviewer: prose and tables numbered, programs and figures folded to a line."""
    if n not in bk.docs:
        print("chapter %d is not written" % n)
        return 1
    doc = bk.docs[n][1]
    fold, ln, shown = folds(doc), 1, 0
    while ln <= len(doc.lines):
        end, text = fold.get(ln, (ln, doc.lines[ln - 1]))
        if end >= start and text.strip():
            if shown == k:
                print("next: --from %d" % ln)
                return 0
            print("%s  %s" % (ln if end == ln else "%d-%d" % (ln, end), text))
            shown += 1
        ln = end + 1
    print("end of chapter")
    return 0


def show(bk, n, ident):
    """Print one program of chapter n with its output, in full, numbered."""
    doc = bk.docs[n][1] if n in bk.docs else None
    code = next((c for s in doc.sections for c in s.code if c.id == ident), None) if doc else None
    if code is None or not code.fence:
        print("no program id=%s in chapter %d" % (ident, n))
        return 1
    for ln in range(code.line, (code.output or code.fence)[1] + 1):
        own = ln - code.fence[0] if code.fence[0] < ln < code.fence[1] else ""
        print(("%d %4s  %s" % (ln, own, doc.lines[ln - 1])).rstrip())
    return 0

# ---------------------------------------------------------------- risks: the review's reading list

DESTROYS = re.compile("|".join([
    r"\brm\s+(?:-\w*[rRf]|--recursive|--force)", r"\bprune\b", r"\bdrop\s+(?:table|database|schema)\b",
    r"\bdelete\s+from\b(?!.*\bwhere\b)", r"\btruncate\b", r"\bformat\s+[a-z]:", r"\bmkfs", r"\bdd\b.*\bof=",
    r"\bgit\s+push\b.*(?:--force|\s-f\b)", r"\bgit\s+reset\s+--hard", r"\bgit\s+clean\s+-\w*f",
    r"\bgit\s+branch\s+-D\b", r"\bchmod\s+-R\s+777", r"\bkill\s+-(?:9|KILL)\b", r"\bshred\b",
    r"\brmdir\s+/s\b", r"\bdel\s+/[fsq]\b", r"\bdocker\s+(?:rm|rmi|volume\s+rm)\s+-f\b"]), re.I)


def passage_above(lines, at, cap=12):
    """The paragraph or fenced block that ends just above line `at` (1-based), or the one holding text
    before a marker on the same line; at most `cap` lines, the last ones."""
    i = at - 1
    if lines[i].split("<!--")[0].strip():
        end = i + 1
    else:
        while i > 0 and not lines[i - 1].strip():
            i -= 1
        end = i
    if end == 0:
        return []
    start = end - 1
    fence = re.match(r"^\s*(`{3,}|~{3,})", lines[start])
    if fence:
        start -= 1
        while start > 0 and not lines[start].lstrip().startswith(fence.group(1)):
            start -= 1
    else:
        while start > 0 and lines[start - 1].strip() and not lines[start - 1].lstrip().startswith(("#", "<!--")):
            start -= 1
    return lines[max(start, end - cap):end]


def risks(bk, n):
    """Print the reading list of chapter n; the last line counts the items."""
    if n not in bk.docs:
        print("chapter %d is not written" % n)
        return 1
    path, doc = bk.docs[n]
    scanned, markers = scan(doc)
    items = []
    for m in (m for m in markers if m.kind == "risk"):
        body = "\n".join("    " + l for l in passage_above(doc.lines, m.start))
        items.append((m.start, "risk %s: %s\n%s" % (bk.rel(path, m.start), m.body or "(no reason given)", body)))
    for ln, kind, text in scanned:
        if kind == "code" and DESTROYS.search(text):
            items.append((ln, "destroys %s: %s" % (bk.rel(path, ln), text.strip())))
    for sec in doc.sections if bk.plan else []:
        items += [(line, "reference %s: %s %s" % (bk.rel(path, line), sec.number, msg))
                  for level, line, msg in dangling(bk, doc, sec)]
    for c in (c for s in doc.sections for c in s.code if "unrun" in c.attrs):
        items.append((c.line, "unrun %s: id=%s, %s" % (bk.rel(path, c.line), c.id or "?", c.attrs["unrun"] or "no reason")))
    for _, text in sorted(items, key=lambda x: x[0]):
        print(text)
    print("%s to review in chapter %d" % (plural(len(items), "item"), n))
    return 0

# ---------------------------------------------------------------- main


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    values = {}
    for name in ("--from", "--lines", "--show"):
        if name in argv:
            i = argv.index(name)
            if i + 1 == len(argv) or (name != "--show" and not argv[i + 1].isdigit()):
                print("%s needs a %s" % (name, "program id" if name == "--show" else "number"))
                return 2
            values[name] = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
    flags = {a for a in argv if a.startswith("--")}
    unknown = flags - {"--tokens", "--suspects", "--prose", "--all", "--risks"}
    if unknown:
        print("unknown option %s; use --risks, --suspects [--all], --prose, --show or --tokens" % ", ".join(sorted(unknown)))
        return 2
    if "--all" in flags and "--suspects" not in flags:
        print("--all goes with --suspects: us_check.py BOOK N --suspects --all")
        return 2
    args = [a for a in argv if not a.startswith("--")]
    only = None
    if len(args) > 1:
        if not args[1].isdigit():
            print("chapter must be a number: us_check.py BOOK N")
            return 2
        only = int(args[1])
    if "--suspects" in flags:
        if not args or only is None:
            print("usage: us_check.py BOOK N --suspects [--all]")
            return 2
        return suspects(Book(bf.resolve_book(args[0])), only, "--all" in flags)
    if "--risks" in flags:
        if not args or only is None:
            print("usage: us_check.py BOOK N --risks")
            return 2
        return risks(Book(bf.resolve_book(args[0])), only)
    if "--prose" in flags or "--show" in values:
        if not args or only is None:
            print("usage: us_check.py BOOK N --prose [--from LINE] [--lines K] | --show ID")
            return 2
        bk = Book(bf.resolve_book(args[0]))
        if "--show" in values:
            return show(bk, only, values["--show"])
        return prose(bk, only, int(values.get("--from", 1)), int(values.get("--lines", 150)))
    rep = Report()
    if not args:
        sizes = check_skills()
        if "--tokens" in flags:
            token_report(sizes)
        for e in errors:
            rep.add("ERROR", "", e)
        books = bf.list_books()
        if not books:
            rep.add("NOTE", "", "no books under %s yet" % os.path.relpath(bf.book_root(), ROOT))
    else:
        books = [bf.resolve_book(args[0])]
        if not os.path.isdir(books[0]):
            print("no book at %s" % books[0])
            return 2
    for path in books:
        bk = Book(path)
        sub = Report()
        check_book(bk, only, sub)
        if len(books) > 1:
            sub.items = [(l, bk.name + "/" + w if w else bk.name, m) for l, w, m in sub.items]
            sub.tail = [(l, bk.name + "/" + w if w else bk.name, m) for l, w, m in sub.tail]
        rep.items += sub.items
        rep.tail += sub.tail
        rep.chapters += sub.chapters
        rep.sections += sub.sections
    for line in rep.lines():
        print(line)
    n_err = rep.count("ERROR")
    print("check %s: %s, %s, %s, %s, %s" % ("ok" if not n_err else "failed", plural(rep.chapters, "chapter"),
          plural(rep.sections, "section"), plural(n_err, "error"), plural(rep.count("FLAG"), "flag"), plural(rep.count("NOTE"), "note")))
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
