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


@dataclass
class ChapterDoc:
    """A parsed chapter file: title, sections, and stray `##` headings."""
    number: int = 0
    title: str = ""
    title_line: int = 0
    sections: list = field(default_factory=list)
    other_headings: list = field(default_factory=list)
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
HEAD_BEAT = re.compile(r"^###\s+(.*?)\s*#*\s*$")
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
        if cur is not None:
            cur.beats.append((HEAD_BEAT.match(body).group(1), n))
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
        if s.startswith("#") or s.startswith("```") or (s.startswith("<!--") and out):
            break
        if s.startswith("<!--") or "-->" in s and not out:
            continue
        if not s and out and len(" ".join(out).split()) > 30:
            break
        out.append(s)
    return " ".join(x for x in out if x)


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

