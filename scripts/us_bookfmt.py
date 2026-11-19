"""Parse the book format of rules/book-standard.md: PLAN.md, chapter files, STATUS.json."""
import glob
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us_lib import ROOT, load_config  # noqa: E402

KINDS = ["lesson", "story", "practice", "short"]   # short: a lesson about one command or small idea
CODE_MODES = ["run", "fragment", "compile", "warns", "error", "compile-error"]
ID_CHARS = r"[A-Za-z0-9._-]+"
ID_RE = re.compile(r"^%s$" % ID_CHARS)

# ---------------------------------------------------------------- data


@dataclass
class PlanSection:
    """One planned section: a line `N.M Title | fields` of PLAN.md."""
    number: str
    title: str
    line: int
    raw: str
    kind: str = "lesson"
    level: int = 1
    teaches: list = field(default_factory=list)
    needs: list = field(default_factory=list)
    fig: bool = False          # `fig` field: the section must hold a drawn figure

    @property
    def chapter(self):
        """Chapter number this section belongs to."""
        return int(self.number.split(".")[0])

    @property
    def index(self):
        """Position of the section inside its chapter (the M of N.M)."""
        return int(self.number.split(".")[1])


@dataclass
class PlanChapter:
    """One planned chapter: a `### N Title` line and its sections."""
    number: int
    title: str
    line: int
    raw: str
    part: str = ""
    sections: list = field(default_factory=list)
    from_refs: list = field(default_factory=list)   # (card id, [steps] or None) of its `from:` line
    from_line: int = 0


@dataclass
class Plan:
    """A parsed PLAN.md; errors and warnings are (line, message) pairs."""
    path: str = ""
    title: str = ""
    audience: str = ""
    run: str = ""
    parts: list = field(default_factory=list)
    chapters: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)      # other header lines: key -> [(line number, value), ...]
    held: list = field(default_factory=list)      # (line, card id, [steps] or None) of the `held:` lines
    later: list = field(default_factory=list)     # (line, card id, [steps] or None) of the `later:` lines
    track: list = field(default_factory=list)     # (line, DOMAIN/TRACK, [rows] or None) of the `track:` lines
    budget: tuple = None                          # (line, hours) of the `budget: N hours` line
    later_books: set = field(default_factory=set)  # lines of the `later:` lines whose bracket starts "book N"

    def uses_curriculum(self):
        """True when the plan has a held:, later: or from: line."""
        return bool(self.held or self.later or any(c.from_line for c in self.chapters))

    def curriculum_refs(self):
        """(line, where, card id, [steps] or None) of every from:, held: and later: entry; where is 'from N',
        'held' or 'later'."""
        out = [(c.from_line, "from %d" % c.number, i, st) for c in self.chapters for i, st in c.from_refs]
        return out + [(ln, "held", i, st) for ln, i, st in self.held] + [(ln, "later", i, st) for ln, i, st in self.later]

    def chapter(self, n):
        """The planned chapter numbered n, or None."""
        return next((c for c in self.chapters if c.number == n), None)

    def sections(self):
        """Every planned section, in book order."""
        return [s for c in self.chapters for s in c.sections]

    def section(self, number):
        """The planned section 'N.M', or None."""
        return next((s for s in self.sections() if s.number == number), None)

    def teacher(self):
        """Map idea id -> the first section that teaches it."""
        found = {}
        for s in self.sections():
            for idea in s.teaches:
                found.setdefault(idea, s)
        return found


@dataclass
class Teach:
    """A `<!-- teaches: id = words -->` marker."""
    id: str
    words: list
    line: int


@dataclass
class Code:
    """A `<!-- code: ... -->` marker, its fence and the output fence below it."""
    id: str
    mode: str
    attrs: dict
    line: int
    lang: str = ""
    fence: tuple = None
    output: tuple = None


@dataclass
class Figure:
    """A `<!-- fig: -->` (or legacy `<!-- diagram: -->`) marker."""
    id: str
    kind: str
    span: tuple
    body: str = ""


@dataclass
class Marker:
    """Any hidden HTML comment: kind, body, first and last line."""
    kind: str
    body: str
    start: int
    end: int


@dataclass
class SectionDoc:
    """One written `## N.M Title` section of a chapter file."""
    number: str
    title: str
    line: int
    end: int = 0
    beats: list = field(default_factory=list)
    check_line: int = 0
    answers: int = 0
    details: int = 0
    words: int = 0
    teaches: list = field(default_factory=list)
    code: list = field(default_factory=list)
    figures: list = field(default_factory=list)
    resolves: list = field(default_factory=list)
    refs: list = field(default_factory=list)
    simplified: list = field(default_factory=list)
    markers: list = field(default_factory=list)
    bare_fences: list = field(default_factory=list)
    questions: list = field(default_factory=list)   # 1-based first line of each question/task (as us_practice finds them)
    qtags: list = field(default_factory=list)       # {'line', 'idea', 'type', 'wrong', 'question'}: q markers (question K, 0 if above none)
    untagged: list = field(default_factory=list)    # (K, line) of each question with no q marker directly above it
    checks: list = field(default_factory=list)      # (id, command) of each program block with check=
    checklists: list = field(default_factory=list)  # {'id', 'line', 'items'} of each checklist marker


@dataclass
class ChapterDoc:
    """A parsed chapter file: title, sections, and stray `##` headings."""
    number: int = 0
    title: str = ""
    title_line: int = 0
    sections: list = field(default_factory=list)
    other_headings: list = field(default_factory=list)
    bad_headings: list = field(default_factory=list)    # (line, text) of headings no rule reads, e.g. '###x' 
    lines: list = field(default_factory=list)

    def section(self, number):
        """The written section 'N.M', or None."""
        return next((s for s in self.sections if s.number == number), None)

# ---------------------------------------------------------------- books and paths


def book_root():
    """Folder that holds all books (config `book`, relative to ROOT)."""
    root = load_config().get("book", "book")
    return root if os.path.isabs(root) else os.path.join(ROOT, root)


def private_dir():
    """Private folder (env UNDERSTUDY_PRIVATE, else config `private`)."""
    path = os.environ.get("UNDERSTUDY_PRIVATE") or load_config().get("private", "private")
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def resolve_book(arg):
    """A book slug or folder path -> absolute book folder."""
    if os.path.isdir(arg) or os.sep in arg or arg.startswith("."):
        return os.path.abspath(arg)
    return os.path.join(book_root(), arg)


def slugify(title):
    """Chapter title -> file slug ('Pointers & memory' -> 'pointers-and-memory')."""
    text = title.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "chapter"


def chapter_path(book, n):
    """Existing chapters/NN-*.md for chapter n, or None."""
    hits = sorted(glob.glob(os.path.join(book, "chapters", "%02d-*.md" % n)))
    return hits[0] if hits else None


def new_chapter_path(book, n, title):
    """Path a new chapter n with this title is created at."""
    return os.path.join(book, "chapters", "%02d-%s.md" % (n, slugify(title)))


def read_text(path):
    """Whole file as text."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    """Write a file atomically, creating folders."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def read_status(book):
    """STATUS.json as a dict ({'chapters': {}} if missing)."""
    path = os.path.join(book, "STATUS.json")
    if not os.path.exists(path):
        return {"chapters": {}}
    data = json.loads(read_text(path) or "{}")
    data.setdefault("chapters", {})
    return data


def write_status(book, data):
    """Save STATUS.json, sorted and indented."""
    write_text(os.path.join(book, "STATUS.json"), json.dumps(data, indent=2, sort_keys=True) + "\n")


def fmt_int(n):
    """1742 -> '1,742'."""
    return "{:,}".format(n)


def word_count(text):
    """Words in a run of text: tokens holding a letter or digit."""
    return sum(1 for t in text.split() if re.search(r"[A-Za-z0-9]", t))


def run_helper(script, args):
    """Run scripts/<script> if present; return (exit code, stdout lines, stderr lines) or None."""
    path = os.path.join(ROOT, "scripts", script)
    if not os.path.exists(path):
        return None
    proc = subprocess.run([sys.executable, path] + list(args), capture_output=True, text=True)
    def keep(text):
        return [l for l in text.splitlines() if l.strip()]
    return proc.returncode, keep(proc.stdout), keep(proc.stderr)

# ---------------------------------------------------------------- PLAN.md

PLAN_TITLE = re.compile(r"^#\s+(.+?)\s*$")
PLAN_PART = re.compile(r"^##\s+(.+?)\s*$")
PLAN_CHAPTER = re.compile(r"^###\s+(?:Chapter\s+)?(\d+)\s*[.:]?\s+(.+?)\s*$", re.I)
PLAN_SECTION = re.compile(r"^(\d+)\s*\.\s*(\d+)\s+(.*)$")
PLAN_META = re.compile(r"^(for|run)\s*:\s*(.*?)\s*$", re.I)
META_KEYS = ("state", "timeout", "check", "mask", "kind")   # header lines above the first chapter, read with plan_meta()
PLAN_HEAD = re.compile(r"^(%s)\s*:\s*(.*?)\s*$" % "|".join(META_KEYS), re.I)
PLAN_BUDGET = re.compile(r"^budget\s*:\s*(.*?)\s*$", re.I)  # the learner's hours of study for this book
PLAN_TRACK = re.compile(r"^track\s*:\s*(.*?)\s*$", re.I)   # the goal's rows of a track map
TRACK_ENTRY = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*)(?:\s+(\S.*))?$")
PLAN_STEPS = re.compile(r"^(held|later|from)\s*:\s*(.*?)\s*$", re.I)   # curriculum steps: curriculum/FORMAT.md
CARD_ENTRY = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)(?:\s+(\S.*))?$")


def unbracket(text):
    """Text with every (round-bracketed reason) taken out, nested brackets included."""
    while True:
        new = re.sub(r"\([^()]*\)", " ", text)
        if new == text:
            return text
        text = new


def curriculum_entries(text):
    """([(card id, [steps] or None)], [bad entries]) of 'CARD STEPS; CARD STEPS (reason)'."""
    from us_path import parse_steps
    entries, bad = [], []
    for piece in [p.strip() for p in unbracket(text).split(";") if p.strip()]:
        m = CARD_ENTRY.match(piece)
        steps = parse_steps(m.group(2)) if m and m.group(2) else None
        if not m or (m.group(2) and not steps):
            bad.append(piece)
        else:
            entries.append((m.group(1), steps))
    return entries, bad


def add_budget_line(plan, chapter, m, n):
    """Read the `budget: N hours` line; misplaced, repeated or unreadable lines are errors."""
    text = unbracket(m.group(1)).strip()
    found = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:hours?|h)?", text, re.I)
    if chapter is not None:
        plan.errors.append((n, "budget: goes above the first chapter, with the other header lines; move it there"))
    elif not found or float(found.group(1)) <= 0:
        plan.errors.append((n, "budget: cannot read '%s'; write budget: N hours, such as budget: 40 hours" % text))
    elif plan.budget:
        plan.errors.append((n, "budget: is written twice; keep one"))
    else:
        plan.budget = (n, float(found.group(1)))


def add_track_line(plan, chapter, m, n):
    """Read one `track: DOMAIN/TRACK ROWS` line (no rows: all of them); misplaced or unreadable lines are errors."""
    from us_path import parse_steps
    text = unbracket(m.group(1)).strip()
    found = TRACK_ENTRY.match(text)
    rows = parse_steps(found.group(2)) if found and found.group(2) else None
    if chapter is not None:
        plan.errors.append((n, "track: lines go above the first chapter, with the other header lines; move it there"))
    elif not found or (found.group(2) and not rows):
        plan.errors.append((n, "track: cannot read '%s'; write track: DOMAIN/TRACK ROWS, such as "
                               "system-design/foundations 1-5, 7 (no rows: all of them)" % text))
    else:
        plan.track.append((n, found.group(1), rows))


def add_steps_line(plan, chapter, m, n):
    """Read one held:, later: or from: line into the plan; misplaced or unreadable lines are errors."""
    key = m.group(1).lower()
    entries, bad = curriculum_entries(m.group(2))
    for piece in bad:
        plan.errors.append((n, "%s: cannot read '%s'; write CARD STEPS, such as cpp-for-contests 1-3 or "
                               "dsa-core-techniques 2,5 (no steps: all of them), entries joined by ';'" % (key, piece)))
    if not entries and not bad:
        plan.errors.append((n, "%s: names no card; write %s: CARD STEPS, or drop the line" % (key, key)))
    if key == "from":
        if chapter is None or chapter.sections or chapter.from_line:
            plan.errors.append((n, "a from: line goes directly under its chapter's '### N Title' line, before the "
                                   "first section, once a chapter; move it there"))
            return
        chapter.from_line, chapter.from_refs = n, entries
    elif chapter is not None:
        plan.errors.append((n, "%s: lines go above the first chapter, with the other header lines; move it there" % key))
    else:
        getattr(plan, key).extend((n, i, st) for i, st in entries)
        if key == "later" and re.search(r"\(\s*book\s+\d", m.group(2), re.I):
            plan.later_books.add(n)              # a later book of a series: (book 2)


def split_ids(text):
    """'a, b c' -> ['a', 'b', 'c']."""
    return [t for t in re.split(r"[,\s]+", text.strip()) if t]


def parse_fields(sec, fields, n, errors):
    """Fill kind, level, teaches, needs of a plan section from its `|` fields."""
    for raw in fields:
        f = raw.strip()
        if not f:
            continue
        key, sep, value = f.partition(":")
        key = key.strip().lower()
        if not sep and key in KINDS:
            sec.kind = key
        elif not sep and key == "fig":
            sec.fig = True
        elif sep and key in ("teaches", "needs"):
            ids = split_ids(value)
            for i in ids:
                if not ID_RE.match(i):
                    errors.append((n, "%s: bad idea id '%s'; use letters, digits, '.', '_', '-'" % (sec.number, i)))
            getattr(sec, key).extend(i for i in ids if ID_RE.match(i))
        elif sep and key == "level":
            v = value.strip()
            if not v.isdigit():
                errors.append((n, "%s: level '%s' is not a number; write level: 1 to 5" % (sec.number, v)))
            else:
                sec.level = int(v)
        elif sep and key == "kind" and value.strip().lower() in KINDS:
            sec.kind = value.strip().lower()
        else:
            errors.append((n, "%s: unknown field '%s'; use teaches:, needs:, level:, fig, story, short or practice" % (sec.number, f)))


def parse_plan_text(text, path=""):
    """Parse PLAN.md text into a Plan; problems go to plan.errors as (line, message)."""
    plan = Plan(path=path)
    part, chapter, in_comment = "", None, False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if in_comment or line.startswith("<!--"):
            in_comment = "-->" not in line
            continue
        if not line:
            continue
        m_sec, m_ch = PLAN_SECTION.match(line), PLAN_CHAPTER.match(line)
        m_meta = PLAN_META.match(line)
        if m_ch:
            chapter = PlanChapter(int(m_ch.group(1)), m_ch.group(2), n, line, part)
            plan.chapters.append(chapter)
        elif line.startswith("###"):
            plan.errors.append((n, "chapter line needs a number: '### N Title'"))
        elif line.startswith("##") and PLAN_PART.match(line):
            part = PLAN_PART.match(line).group(1)
            plan.parts.append(part)
        elif line.startswith("#") and PLAN_TITLE.match(line):
            if plan.title:
                plan.errors.append((n, "second book title; use '## ' for a part or '### N' for a chapter"))
            plan.title = PLAN_TITLE.match(line).group(1)
        elif m_meta and not chapter:
            setattr(plan, "audience" if m_meta.group(1).lower() == "for" else "run", m_meta.group(2))
        elif PLAN_BUDGET.match(line):
            add_budget_line(plan, chapter, PLAN_BUDGET.match(line), n)
        elif PLAN_TRACK.match(line):
            add_track_line(plan, chapter, PLAN_TRACK.match(line), n)
        elif PLAN_STEPS.match(line):
            add_steps_line(plan, chapter, PLAN_STEPS.match(line), n)
        elif PLAN_HEAD.match(line) and not chapter:
            m_head = PLAN_HEAD.match(line)
            plan.meta.setdefault(m_head.group(1).lower(), []).append((n, m_head.group(2)))
        elif m_sec:
            add_plan_section(plan, chapter, m_sec, n, line)
        else:
            plan.errors.append((n, "unrecognised line; expected 'N.M Title | fields'"))
    if not plan.title:
        plan.errors.append((1, "no book title; add '# Title' as the first line"))
    if not plan.chapters:
        plan.errors.append((1, "no chapters; add '### 1 Title' and its sections"))
    return plan


def add_plan_section(plan, chapter, m, n, line):
    """Turn one matched `N.M Title | fields` line into a PlanSection."""
    number = "%d.%d" % (int(m.group(1)), int(m.group(2)))
    parts = m.group(3).split("|")
    sec = PlanSection(number, parts[0].strip(), n, line)
    if not sec.title:
        plan.errors.append((n, "%s has no title; write '%s Title'" % (number, number)))
    parse_fields(sec, parts[1:], n, plan.errors)
    if chapter is None:
        plan.errors.append((n, "%s comes before any chapter; add '### %s Title' above it" % (number, m.group(1))))
        return
    chapter.sections.append(sec)


def parse_plan(path):
    """Parse a PLAN.md file (see parse_plan_text)."""
    return parse_plan_text(read_text(path), path)


def load_plan(book):
    """Plan of a book folder, or None if it has no PLAN.md."""
    path = os.path.join(book, "PLAN.md")
    return parse_plan(path) if os.path.exists(path) else None

# ---------------------------------------------------------------- chapter files

FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})\s*([^`\s]*)")
HEAD_CHAPTER = re.compile(r"^#\s+(?:Chapter\s+(\d+)\s*[:.]\s*)?(.*?)\s*$")
HEAD_SECTION = re.compile(r"^##\s+(\d+)\.(\d+)\s+(.*?)\s*$")
HEAD_BEAT = re.compile(r"^#{3,6}\s+(.*?)\s*#*\s*$")    # ### to ###### inside a section
CHECK_RE = re.compile(r"^\s*(\*\*Check yourself\*\*|#+\s*Check yourself)", re.I)
REF_RE = re.compile(r"§\s?(\d+)\.(\d+)")
ATTR_RE = re.compile(r'([A-Za-z][\w-]*)=("(?:[^"\\]|\\.)*"|\S+)')
SIMPLIFIED_RE = re.compile(r"^\s*>\s*\*\*Simplified here\.?\*\*", re.I)


def fence_close(line, opener):
    """True if line closes a fence opened with `opener` (``` or ~~~ run)."""
    s = line.strip()
    return len(s) >= len(opener) and set(s) == {opener[0]}


def scan_lines(lines):
    """Classify lines: yields (n, kind, text) with kind prose/fence_open/code/fence_close; comments split out."""
    out, markers = [], []
    opener, comment = None, None
    for n, line in enumerate(lines, 1):
        if opener:
            if fence_close(line, opener):
                out.append((n, "fence_close", line))
                opener = None
            else:
                out.append((n, "code", line))
            continue
        if comment is None:
            m = FENCE_OPEN.match(line)
            if m and "<!--" not in line:
                opener = m.group(1)
                out.append((n, "fence_open", m.group(2)))
                continue
        prose, comment = strip_comments(line, n, comment, markers)
        out.append((n, "prose", prose))
    return out, markers


def strip_comments(line, n, comment, markers):
    """Remove HTML comments from a line, collecting finished ones into markers."""
    prose, rest = "", line
    while rest:
        if comment is not None:
            end = rest.find("-->")
            if end < 0:
                comment[1].append(rest)
                return prose, comment
            comment[1].append(rest[:end])
            markers.append(make_marker("\n".join(comment[1]), comment[0], n))
            comment, rest = None, rest[end + 3:]
        else:
            start = rest.find("<!--")
            if start < 0:
                return prose + rest, None
            prose += rest[:start]
            comment, rest = [n, []], rest[start + 4:]
    return prose, comment


def make_marker(body, start, end):
    """A Marker from a comment body: kind is the word before the first colon."""
    m = re.match(r"\s*([A-Za-z][\w-]*)\s*:(.*)", body, re.S)
    if not m:
        return Marker("", body.strip(), start, end)
    return Marker(m.group(1).lower(), m.group(2).strip(), start, end)


def parse_attrs(text):
    """'id=x mode=y stdin="3 4"' -> dict (quotes removed)."""
    attrs = {}
    for key, value in ATTR_RE.findall(text):
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        attrs[key] = value
    return attrs


# The fact record (stage 3). The writer marks what it doubts with <!-- risk: why -->. The review settles each and
# turns it into a lasting mark on the same line:
#   <!-- checked: how=source date=2026-11-18 ref="packages.ubuntu.com/noble/python3" h=1a2b3c4d -->
# how: run (a program or session proved it), practices (the book's PRACTICES.md states it), source (one look at
# an official source, named in ref), known (certain without looking), reworded (the text now says only what is
# sure). h: a short hash of the passage above the mark, stamped by `us_plan.py mark ... reviewed`; when the
# passage later changes, the hash no longer fits and the check says so.
CHECK_HOWS = ("run", "practices", "source", "known", "reworded")
CHECKED_MARK = re.compile(r"<!--\s*checked:(.*?)-->")
RISK_MARK = re.compile(r"<!--\s*risk:(.*?)-->")


def parse_checked(line):
    """{'how', 'date', 'ref', 'h'} from a line holding a checked mark, or None."""
    m = CHECKED_MARK.search(line)
    if not m:
        return None
    attrs = parse_attrs(m.group(1))
    return {k: attrs.get(k, "") for k in ("how", "date", "ref", "h")}


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


def passage_hash(lines, at):
    """Eight hex digits for the passage above line `at` (1-based), blind to spacing and to hidden marks."""
    import hashlib
    text = " ".join(" ".join(re.sub(r"<!--.*?-->", "", l).split()) for l in passage_above(lines, at, cap=40))
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:8]


# Question tags (stage 2): one hidden line directly above a numbered question or practice task:
#   <!-- q: idea=variable type=predict wrong="equals means the same" -->
# idea: an idea id the book teaches; type: what the question makes the reader do; wrong: a short name for the
# wrong belief this question catches (optional); unseen: on a practice task, the name of the problem, case or
# material the chapter has not used before its practice (optional).
Q_TYPES = ("recall", "explain", "predict", "fix", "apply", "decide", "build")
Q_APPLY = ("predict", "fix", "apply", "decide", "build")     # doing, as against saying
Q_MARK = re.compile(r"^\s*<!--\s*q:(.*?)-->\s*$")
CHECKLIST_MARK = re.compile(r"^\s*<!--\s*checklist:(.*?)-->\s*$")   # then a Markdown list of yes/no tests


def parse_q(line):
    """{'idea', 'type', 'wrong', 'unseen'} from a q marker line, or None when the line is not one."""
    m = Q_MARK.match(line)
    if not m:
        return None
    attrs = parse_attrs(m.group(1))
    return {"idea": attrs.get("idea", ""), "type": attrs.get("type", ""), "wrong": attrs.get("wrong", ""),
            "unseen": attrs.get("unseen", "")}


QUESTION_START = re.compile(r"^\s*(\d+[.)]\s|\*\*([A-Za-z]+\s+)?\d+([.:)]?\*\*|[.:)]\s)|\*\*(Exercise|Question|Task)\b|#{3,6}\s+(Exercise|Question|Task)\b)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")


def list_start(lines, k, end=None):
    """0-based index where the list under a checklist marker on index k may start: past blank lines and at most one
    paragraph (a lead-in sentence) before the list."""
    end = len(lines) if end is None else end
    j = k + 1
    while j < end and not lines[j].strip():
        j += 1
    if j < end and not LIST_ITEM.match(lines[j]) and not lines[j].lstrip().startswith(("#", "<!--", "```", "~~~", "<details")):
        while j < end and lines[j].strip() and not LIST_ITEM.match(lines[j]):
            j += 1
    return j


def checklist_rows(lines):
    """0-based indexes of the list items that belong to a checklist (a numbered one is not a run of questions)."""
    rows = set()
    for k, line in enumerate(lines):
        if CHECKLIST_MARK.match(line):
            seen = False
            for j in range(list_start(lines, k), len(lines)):
                if LIST_ITEM.match(lines[j]):
                    rows.add(j)
                    seen = True
                elif lines[j].strip() and not (seen and lines[j].startswith((" ", "\t"))):
                    break
    return rows


def question_starts(lines, free_from=0):
    """0-based index of the first line of each question in lines: the same questions us_practice.py's
    section_questions finds (each <details> outside fences, with the question above it; before index
    free_from, the Check yourself line, only numbered questions and exercises count)."""
    out, fence, start, i = [], None, 0, 0
    while i < len(lines):
        s = lines[i].strip()
        if fence:
            fence = None if fence_close(lines[i], fence) else fence
        elif FENCE_OPEN.match(lines[i]):
            fence = FENCE_OPEN.match(lines[i]).group(1)
        elif s.startswith("<details>"):
            end, depth = i, 0
            for end in range(i, len(lines)):
                depth += lines[end].count("<details>") - lines[end].count("</details>")
                if depth <= 0:
                    break
            inside, opener, starts, tagged = [], None, [], []
            listed = checklist_rows(lines[start:i])
            for k in range(start, i):
                if k - start in listed:
                    continue
                if opener:
                    opener = None if fence_close(lines[k], opener) else opener
                    continue
                m = FENCE_OPEN.match(lines[k])
                if m:
                    opener = m.group(1)
                elif k > start and Q_MARK.match(lines[k - 1]) and lines[k].strip():
                    tagged.append(k)                 # a q tag opens a question, whatever its first line looks like
                elif QUESTION_START.match(lines[k]):
                    starts.append(k)
            starts = tagged or starts                # numbered steps inside a tagged task are not new questions
            text = [k for k in range(start, i) if lines[k].strip() and not Q_MARK.match(lines[k])]
            if starts:
                out.append(starts[-1])
            elif text and i >= free_from:
                out.append(text[0])
            start = i = end + 1
            continue
        i += 1
    return out


def read_questions(doc, sec):
    """Fill a section's questions, q tags, untagged questions, check= blocks and checklists."""
    lines = doc.lines[sec.line:sec.end]
    free = sec.check_line - sec.line if sec.check_line else len(lines)
    firsts = [sec.line + 1 + k for k in question_starts(lines, free)]
    sec.questions = firsts
    for k, ln in enumerate(firsts, 1):
        if ln < 2 or parse_q(doc.lines[ln - 2]) is None:
            sec.untagged.append((k, ln))
    for ln in range(sec.line + 1, sec.end + 1):
        tag = parse_q(doc.lines[ln - 1])
        if tag is not None:
            tag.update(line=ln, question=firsts.index(ln + 1) + 1 if ln + 1 in firsts else 0)
            sec.qtags.append(tag)
        m = CHECKLIST_MARK.match(doc.lines[ln - 1])
        if m:
            sec.checklists.append({"id": parse_attrs(m.group(1)).get("id", ""), "line": ln,
                                   "items": checklist_items(doc.lines, ln, sec.end)})
    sec.checks = [(c.id, c.attrs["check"]) for c in sec.code if "check" in c.attrs]


def checklist_items(lines, line, end):
    """The list items after a checklist marker on 1-based line `line` (blank lines and one lead-in paragraph
    between allowed)."""
    items = []
    for raw in lines[list_start(lines, line - 1, end):end]:
        if LIST_ITEM.match(raw):
            items.append(re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", raw).strip())
        elif raw.strip() and not (items and raw.startswith((" ", "\t"))):
            break
    return items


def parse_teach(marker):
    """Teach from a teaches marker body 'id = words, words'."""
    ident, _, words = marker.body.partition("=")
    ws = [w.strip() for w in words.split(",") if w.strip()]
    return Teach(ident.strip(), ws, marker.start)


def parse_chapter(text):
    """Parse a chapter file (or one submitted section) into a ChapterDoc."""
    lines = text.splitlines()
    doc = ChapterDoc(lines=lines)
    scanned, markers = scan_lines(lines)
    fences = collect_fences(scanned)
    cur = None
    for n, kind, body in scanned:
        if kind != "prose":
            continue
        cur = read_heading(doc, cur, n, body) if body.startswith("#") else cur
        if cur is not None and not body.startswith("#"):
            read_prose(cur, n, body)
    if cur is not None:
        cur.end = len(lines)
    attach(doc, markers, fences, scanned)
    for sec in doc.sections:
        read_questions(doc, sec)
    return doc


def collect_fences(scanned):
    """List of (start, end, lang) for every fenced block."""
    fences, start = [], None
    for n, kind, body in scanned:
        if kind == "fence_open":
            start = (n, body)
        elif kind == "fence_close" and start:
            fences.append((start[0], n, start[1]))
            start = None
    if start:
        fences.append((start[0], len(scanned), start[1]))
    return fences


def read_heading(doc, cur, n, body):
    """Handle a heading line; returns the current section afterwards."""
    m = HEAD_SECTION.match(body)
    if m:
        if cur is not None:
            cur.end = n - 1
        sec = SectionDoc("%d.%d" % (int(m.group(1)), int(m.group(2))), m.group(3), n)
        doc.sections.append(sec)
        return sec
    if body.startswith("###"):
        m = HEAD_BEAT.match(body)
        if m is None:
            doc.bad_headings.append((n, body.strip()))
        elif cur is not None:
            cur.beats.append((m.group(1), n))
        return cur
    if body.startswith("## ") or body.startswith("# "):
        if cur is not None:
            cur.end = n - 1
        if body.startswith("# ") and not doc.title:
            m = HEAD_CHAPTER.match(body)
            doc.number, doc.title, doc.title_line = int(m.group(1) or 0), m.group(2), n
        else:
            doc.other_headings.append((n, body))
        return None
    return cur


def read_prose(sec, n, body):
    """Record check-yourself, details, refs and Simplified boxes of a prose line."""
    if CHECK_RE.match(body) and not sec.check_line:
        sec.check_line = n
    count = body.count("<details>")
    sec.details += count
    if sec.check_line:
        sec.answers += count
    for m in REF_RE.finditer(body):
        sec.refs.append(("%d.%d" % (int(m.group(1)), int(m.group(2))), n))
    if SIMPLIFIED_RE.match(body):
        sec.simplified.append((n, body.strip()))


def section_at(doc, n):
    """The section containing line n, or None."""
    for sec in doc.sections:
        if sec.line <= n <= (sec.end or len(doc.lines)):
            return sec
    return None


def attach(doc, markers, fences, scanned):
    """Hand markers, fences and word counts to the sections they sit in."""
    outputs = attach_markers(doc, markers, fences)
    for start, end, lang in fences:
        sec = section_at(doc, start)
        if sec is not None and not lang:
            sec.bare_fences.append(start)
    for n, kind, body in scanned:
        sec = section_at(doc, n)
        if sec is None or n == sec.line or any(a <= n <= b for a, b in outputs):
            continue
        if kind == "code" or (kind == "prose" and not body.lstrip().startswith("#")):
            sec.words += word_count(clean_prose(body) if kind == "prose" else body)


def clean_prose(body):
    """Prose line without HTML tags and table rules."""
    body = re.sub(r"<summary>.*?</summary>", " ", body)
    return re.sub(r"</?details>", " ", body)


def attach_markers(doc, markers, fences):
    """Turn raw markers into Teach/Code/Figure/resolves; returns output fence spans."""
    outputs = []
    for mk in markers:
        sec = section_at(doc, mk.start)
        if sec is None:
            continue
        sec.markers.append(mk)
        if mk.kind == "teaches":
            sec.teaches.append(parse_teach(mk))
        elif mk.kind == "code":
            code = make_code(mk, fences, doc.lines)
            sec.code.append(code)
            if code.output:
                outputs.append(code.output)
        elif mk.kind in ("fig", "diagram"):
            attrs = parse_attrs(mk.body.splitlines()[0] if mk.body else "")
            sec.figures.append(Figure(attrs.get("id", ""), mk.kind, (mk.start, mk.end), mk.body))
        elif mk.kind == "resolves":
            sec.resolves.append((mk.body, mk.start))
    return outputs


def next_fence(fences, lines, after):
    """The fence starting after line `after` with only blank lines between, or None."""
    for start, end, lang in fences:
        if start > after:
            gap = lines[after:start - 1]
            return (start, end, lang) if all(not g.strip() for g in gap) else None
    return None


def make_code(mk, fences, lines):
    """Code marker -> Code with its program fence and the output fence below it."""
    attrs = parse_attrs(mk.body)
    code = Code(attrs.pop("id", ""), attrs.pop("mode", "run"), attrs, mk.start)
    fence = next_fence(fences, lines, mk.end)
    if fence:
        code.fence, code.lang = (fence[0], fence[1]), fence[2]
        out = next_fence(fences, lines, fence[1])
        if out and out[2] == "text":
            code.output = (out[0], out[1])
    return code


def section_text(doc, sec):
    """The raw lines of one section, joined."""
    return "\n".join(doc.lines[sec.line - 1:sec.end])

# ---------------------------------------------------------------- terms and definitions

SENTENCE_END = re.compile(r"(?<=[.!?]\*\*)\s+|(?<=[.!?])\s+(?=[A-Z`*§(\"])")


def paragraph_after(lines, line, limit=12):
    """Prose after a marker line: up to the next heading, marker or fence."""
    out = []
    for raw in lines[line:line + limit]:
        s = raw.strip()
        if s.startswith(("#", "```", "**Check yourself**")) or (s.startswith("<!--") and out):
            break
        if s.startswith("<!--") or "-->" in s and not out:
            continue
        if not s and out and len(" ".join(out).split()) > 30:
            break
        out.append(s)
    return " ".join(x for x in out if x)


def section_prose(lines, line, limit=400):
    """The prose from a marker line to the end of its section (the next `## ` heading): fences, markers,
    headings, tables and hidden answers left out."""
    out, fence, hidden = [], None, 0
    for raw in lines[line:line + limit]:
        s = raw.strip()
        if fence:
            fence = None if fence_close(raw, fence) else fence
            continue
        m = FENCE_OPEN.match(raw)
        if m:
            fence = m.group(1)
            continue
        if s.startswith(("## ", "**Check yourself**")):          # the questions are not where an idea is defined
            break
        hidden += s.count("<details>") - s.count("</details>")
        if hidden > 0 or not s or s.startswith(("#", "<", "|")):
            continue
        out.append(s)
    return " ".join(out)


def bold_spans(text):
    """Every **bold** span in text."""
    return re.findall(r"\*\*(.+?)\*\*", text)


DEFINES = re.compile(r"^(?:An?|The)\s+(.{1,30}?)\s+(?:is|are)\b")


def idea_term(teach, lines):
    """The word an idea goes by: marker words, else a bold term near the marker, else the id."""
    if teach.words:
        return teach.words[0]
    spans = [b.strip().replace("`", "") for b in bold_spans(paragraph_after(lines, teach.line))]
    if spans and DEFINES.match(spans[0]):
        return DEFINES.match(spans[0]).group(1)
    id_words = set(humanise(teach.id).split())
    short = [b.rstrip(".?!:") for b in spans if len(b.split()) <= 4]
    pick = next((b for b in short if id_words & set(b.lower().split())), short[0] if short else "")
    pick = re.sub(r"^(?:The|A|An)\s+", "", pick)
    return pick or humanise(teach.id)


def humanise(ident):
    """Idea id -> words ('C8.NULL_POINTER' -> 'null pointer', 'memory-box' -> 'memory box')."""
    ident = re.sub(r"^[A-Za-z]\d+\.", "", ident)
    return re.sub(r"[-_.]+", " ", ident).strip().lower()


def definition(teach, lines, cap=25):
    """The sentence that defines an idea: the bold sentence after its marker, at most cap words."""
    para = paragraph_after(lines, teach.line)
    sentences = [s for s in SENTENCE_END.split(para) if s and s.strip()]
    wanted = {w.lower() for w in teach.words} | {idea_term(teach, lines).lower()}
    bolded = [s for s in sentences if "**" in s]
    pick = next((s for s in bolded if any(b.lower().replace("`", "") in wanted for b in bold_spans(s))), None)
    pick = pick or next((s for s in bolded if len(s.split()) > 6), bolded[0] if bolded else "")
    if not pick:                                 # not under the marker: look through the rest of the section
        term = idea_term(teach, lines).lower()                      # only the idea's own name counts here
        names = lambda s: len(term) > 2 and re.search(r"(?<!\w)%s(?!\w)" % re.escape(term), s.replace("`", "").lower())
        rest = [s for s in SENTENCE_END.split(section_prose(lines, teach.line)) if s and len(s.split()) > 4]
        pick = next((s for s in rest if any(b.lower().replace("`", "") in wanted for b in bold_spans(s))), "") or \
            next((s for s in rest if names(s) and re.search(r"\b(is|are|means|called)\b|:", s)), "") or \
            next((s for s in sentences if len(s.split()) > 4 and names(s)), "")
    if pick and len(pick.split()) <= 5 and pick in sentences[:-1]:
        pick += " " + sentences[sentences.index(pick) + 1]
    words = pick.replace("**", "").split()
    return " ".join(words[:cap]) + (" ..." if len(words) > cap else "")


def book_ideas(book, plan):
    """Map idea id -> {'term', 'definition', 'section'} for every idea, written or planned."""
    ideas = {}
    for idea, sec in plan.teacher().items():
        ideas[idea] = {"term": humanise(idea), "definition": "", "section": sec.number}
    for ch in plan.chapters:
        path = chapter_path(book, ch.number)
        if not path:
            continue
        doc = parse_chapter(read_text(path))
        for sec in doc.sections:
            for t in sec.teaches:
                if t.id in ideas and not ideas[t.id]["definition"]:
                    ideas[t.id]["term"] = idea_term(t, doc.lines)
                    ideas[t.id]["definition"] = definition(t, doc.lines)
    return ideas


def closing_paragraph(text):
    """The last prose paragraph of a chapter (outside fences, comments and <details>)."""
    scanned, _ = scan_lines(text.splitlines())
    paras, cur, depth = [], [], 0
    for n, kind, body in scanned:
        s = body.strip() if kind == "prose" else ""
        depth += s.count("<details>") - s.count("</details>")
        if kind == "prose" and s and depth == 0 and not s.startswith(("#", "<", "|", ">")):
            cur.append(s)
            continue
        if cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return paras[-1] if paras else ""

# ---------------------------------------------------------------- shared by us_check, us_index, us_find


def list_books(root=None):
    """Every book folder (holding PLAN.md or chapters/) directly under the book root, sorted."""
    root = root or book_root()
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not name.startswith(".") and (os.path.exists(os.path.join(path, "PLAN.md"))
                                         or os.path.isdir(os.path.join(path, "chapters"))):
            out.append(path)
    return out


def section_key(number):
    """'8.12' -> (8, 12), for ordering sections."""
    a, _, b = str(number).partition(".")
    return (int(a) if a.isdigit() else 0, int(b) if b.isdigit() else 0)


def anchor(title):
    """GitHub heading slug: '8.2 Pointers & `p`' -> '82-pointers--p'."""
    text = re.sub(r"<[^>]+>", "", title).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_anchors(lines):
    """Every heading anchor in a Markdown file (outside fences), with GitHub's -1, -2 suffixes."""
    seen, out = {}, set()
    scanned, _ = scan_lines(lines)
    for n, kind, body in scanned:
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", body) if kind == "prose" else None
        if not m:
            continue
        slug = anchor(m.group(1))
        k = seen.get(slug, 0)
        out.add(slug if k == 0 else "%s-%d" % (slug, k))
        seen[slug] = k + 1
    return out


EVERYDAY_RE = re.compile(r"^\s*everyday\s*:\s*(.*)$", re.I | re.M)


def everyday_words(book):
    """Lower-case words listed on PLAN.md `everyday:` lines (too common to flag as used early)."""
    path = os.path.join(book, "PLAN.md")
    if not os.path.exists(path):
        return set()
    words = set()
    for m in EVERYDAY_RE.finditer(read_text(path)):
        words |= {w.strip().lower() for w in m.group(1).split(",") if w.strip()}
    return words


def idea_words(teach, lines):
    """(words an idea goes by, guessed?): the marker's `= words`, else a short bold term near the marker.

    A guess is dropped (empty list) when no bold term names the idea: an id turned into words is no evidence."""
    if teach.words:
        return list(teach.words), False
    spans = [b.strip().replace("`", "") for b in bold_spans(paragraph_after(lines, teach.line))]
    term = idea_term(teach, lines)
    if not spans or term.lower() == humanise(teach.id) and term.lower() not in {s.lower() for s in spans}:
        return [], True
    term = term.strip().rstrip(".:?!")
    if (not term or len(term.split()) > 3 or re.search(r"[\d:;()<>=]", term)
            or re.match(r"^[A-Z][a-z]+ing\b", term) or len(term) < 3):
        return [], True
    stems = {w[:4] for w in humanise(teach.id).split() if len(w) > 2}
    if not stems & {w[:4] for w in re.findall(r"[a-z]+", term.lower()) if len(w) > 2}:
        return [], True                      # the bold text does not name this idea
    low = term if re.search(r"[A-Z].*[A-Z]|[A-Z]{2}", term) else term.lower()
    words = [low]
    if re.search(r"[a-rt-z]$", low) and len(low) > 3:
        words.append(low[:-1] + "ies" if re.search(r"[^aeiou]y$", low)
                     else low + ("es" if low.endswith(("x", "ch", "sh")) else "s"))
    return words, True


def contents_span(lines):
    """(start, end) 0-based indices of the `<!-- contents -->` and `<!-- /contents -->` lines, or None."""
    start = next((i for i, l in enumerate(lines) if l.strip() == "<!-- contents -->"), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "<!-- /contents -->"), None)
    return (start, end) if end is not None else None


def beat_range(doc, sec, beat):
    """(first, last) line numbers of a beat's body inside a section, or None."""
    names = [(name, line) for name, line in sec.beats]
    for i, (name, line) in enumerate(names):
        if name == beat:
            end = names[i + 1][1] - 1 if i + 1 < len(names) else (sec.check_line - 1 if sec.check_line > line else sec.end)
            return line + 1, end
    return None


ENV_RE = re.compile(r"^\s*env\s*:\s*(.*)$", re.I | re.M)


def plan_env_words(book):
    """(line, word) for each word of the PLAN.md `env:` lines; a line shlex cannot read gives (line, None)."""
    import shlex
    path = os.path.join(book, "PLAN.md")
    out = []
    for n, line in enumerate(read_text(path).splitlines() if os.path.exists(path) else [], 1):
        m = ENV_RE.match(line)
        try:
            out += [(n, w) for w in shlex.split(m.group(1))] if m else []
        except ValueError:
            out.append((n, None))
    return out


def plan_env(book):
    """{NAME: value} from PLAN.md `env:` lines: set for every program and session of the book."""
    return dict(w.split("=", 1) for _, w in plan_env_words(book) if w and ENV_WORD.match(w))


ENV_WORD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def plan_meta(book, key):
    """Every value of the PLAN.md header line `key: value` (one of META_KEYS, above the first chapter), in order.
    `book` is the book folder. No plan or no such line gives []."""
    path = os.path.join(book, "PLAN.md")
    if not os.path.exists(path):
        return []
    return [value for _, value in parse_plan(path).meta.get(key.lower(), [])]

