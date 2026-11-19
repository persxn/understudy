#!/usr/bin/env python3
"""The curriculum loader: hand an agent the curriculum lines it needs, and check the files.
The files and their rules are in curriculum/FORMAT.md (UNDERSTUDY_CURRICULUM=FOLDER reads another folder).

    python3 scripts/us_path.py find WORDS          the best match among cards, tracks, domains and roles;
                                                   several close ones are listed (at most eight)
    python3 scripts/us_path.py card ID             the card, then its rows in the track maps
    python3 scripts/us_path.py map DOMAIN/TRACK    the track map, its Goals included
    python3 scripts/us_path.py index [DOMAIN]      the domain index; with no domain, the domains
    python3 scripts/us_path.py spine CARD[:STEPS] ... [--track DOMAIN/TRACK]
                                                   one outline for a goal: each card's promise, idea, steps
                                                   (STEPS like 4-8 or 1,3,5-6; all when left out), ladder;
                                                   hours from that track's map when one is given
    python3 scripts/us_path.py goal DOMAIN/TRACK [N|WORDS]
                                                   one goal block of a track map (no N: the goals listed), the
                                                   track: line for the plan, then the spine of its Steps
    python3 scripts/us_path.py steps CARD:STEPS ...
                                                   the notes for one chapter: the steps and what is tagged
                                                   to them (what us_plan.py brief prints)
    python3 scripts/us_path.py words CARD|TRACK ...
                                                   the words to own, one line per card
    python3 scripts/us_path.py role ROLE [--have "id:level, id:level"]
                                                   the role map less what the learner has, and what is left
    python3 scripts/us_path.py ready ROLE [--have "id:level, ..."] [--all]
                                                   a readiness score from the books' plans and practice records
                                                   (specialist lines only with --all)
    python3 scripts/us_path.py check               every file against curriculum/FORMAT.md
    python3 scripts/us_path.py status [--stale MONTHS]
                                                   per domain: tracks, cards built / reviewed / tested,
                                                   planned subjects; files older than MONTHS (12) months
    python3 scripts/us_path.py mark ID|PATH reviewed|tested [--by "TEXT"]
                                                   today's date on the file's status line, if it passes check
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us_lib import ROOT, tokens  # noqa: E402

KINDS = ("language", "tool", "framework", "system", "skill")
LEVELS = ("1 Use", "2 Explain", "3 Build", "4 Design", "5 Teach")
CLASSES = ("essential", "desirable", "specialist")
LIMITS = {"index": 250, "map": 2000, "card": 5000, "role": 800}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUS_RE = re.compile(r"^(built|reviewed|tested) (\d{4}-\d{2}-\d{2})(?: by (\S.*))?$")
PLANNED_RE = re.compile(r"^(\S+)\s+\(planned\)$")
KEY_RE = re.compile(r"^([a-z][a-z ]*[a-z]):(?:\s(.*))?$")
KIND_PART = {"language": "How it runs", "tool": "State and danger", "framework": "What it owns",
             "system": "Numbers and traces", "skill": "Judged by"}     # the fifth part of a card, by kind:
KIND_PART_SLOT = "<the kind's part>"
OPTIONAL_PARTS = ["Step notes", "Believable numbers"]     # of a card, after the kind's part (third design)
NOTE_LABELS = ("Need", "Show", "Explain", "Try", "Picture")
NOTE_REQUIRED = ("Need", "Show", "Explain", "Try")
TRY_TYPES = re.compile(r"^(predict|explain|fix|apply|decide|build|recall):", re.I)
GOAL_LABELS = ("Steps", "Open with", "Deep", "Order", "Halfway")
GOAL_REQUIRED = ("Steps", "Open with", "Deep", "Order")
STEP_TOKENS, BLOCK_TOKENS = 80, 200          # notes above these sizes
OWNED_MAX, OWNED_FIRST = 5, 4                # owned words a step may have; step 1
GOALS = (2, 5)
TAG_TRY = re.compile(r"^\[([\d\s,-]*)\]\s*")
STEPS_RE = re.compile(r"^\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$")
STEP_RE = re.compile(r"^(\d+)\.\s+\S")
HEADERS = {   # (required, optional) header lines, in this order
    "card": (["kind", "aliases", "needs", "status", "sources"], ["aliases", "unverified"]),
    "map": (["for", "leads to", "status", "sources"], ["unverified"]),
    "index": (["status"], ["sources", "unverified"]),
    "role": (["status", "sources"], ["unverified"]),
}
PARTS = {
    "card": ["Promise", "The one idea", "In production", "Teaching order", KIND_PART_SLOT, "Go deep, leave for later",
             "Never omit", "Wrong beliefs", "Failures to diagnose", "Practice and project", "Mastery ladder",
             "Words to own"],
    "map": ["Goals", "Why this order", "Checkpoint projects", "Short on time", "Left out on purpose"],
    "index": [],
    "role": ["Order and time", "Interview checks", "Capstone", "Overlap"],
}
COLUMNS = {
    "map": ["#", "Subject", "Needs first", "After it you can", "Main topics", "Hours", "Level"],
    "index": ["Track", "For", "Start here if"],
    "role": ["Subject", "Level", "Class", "At work it looks like", "Proved by"],
}
LADDER = ["Use", "Explain", "Build", "Design"]
STEPS = (6, 14)
NAMES = {"card": "card", "map": "track", "index": "domain", "role": "role"}
STOP = set("a an the of to in and or is are what how why does do for on with it its i my me want learn learning "
           "become be get into about teach book job career start".split())
LIST_MAX = 8

# ---------------------------------------------------------------- reading the files


def curriculum_dir():
    """The curriculum folder: UNDERSTUDY_CURRICULUM, or curriculum/ in the repository."""
    return os.path.abspath(os.environ.get("UNDERSTUDY_CURRICULUM") or os.path.join(ROOT, "curriculum"))


def today():
    """Today's date; UNDERSTUDY_TODAY=YYYY-MM-DD fakes it for tests."""
    return datetime.date.fromisoformat(os.environ.get("UNDERSTUDY_TODAY") or datetime.date.today().isoformat())


def as_date(text):
    """A YYYY-MM-DD string as a date, or None."""
    try:
        return datetime.date.fromisoformat(text) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else None
    except ValueError:
        return None


def cells(line):
    """The cells of a Markdown table row (`\\|` inside a cell stands for |)."""
    s = line.strip()[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


class File:
    """One curriculum file, parsed: title, header lines, the table and the `## ` parts."""

    def __init__(self, path, kind, ident, domain=None):
        self.path, self.kind, self.id, self.domain = path, kind, ident, domain
        self.text = open(path, encoding="utf-8").read()
        self.lines = self.text.splitlines()
        self.title, self.title_id = "", None
        self.header = []                 # (line, key, value)
        self.bad_header = []             # lines in the header that are not `key: value`
        self.parts = []                  # (line, name, [(line, text)])
        self.table = []                  # (line, cells): the first table, header row included
        self.problems = []
        self.parse()

    def parse(self):
        first = self.lines[0] if self.lines else ""
        m = re.match(r"^# (.+)$", first)
        if m:
            self.title = m.group(1).strip()
            m2 = re.match(r"^([^\s:]+): (.+)$", self.title)
            if self.kind in ("card", "role") and m2:
                self.title_id, self.title = m2.group(1), m2.group(2).strip()
        k = 1
        while k < len(self.lines) and self.lines[k].strip():
            line = self.lines[k]
            m = KEY_RE.match(line)
            if m:
                self.header.append([k + 1, m.group(1), (m.group(2) or "").strip()])
            elif line[:1].isspace() and self.header:
                self.header[-1][2] = (self.header[-1][2] + " " + line.strip()).strip()
            else:
                self.bad_header.append(k + 1)
            k += 1
        part = None
        in_table = None
        for n in range(k, len(self.lines)):
            line = self.lines[n]
            if line.startswith("## "):
                part = (n + 1, line[3:].strip(), [])
                self.parts.append(part)
                continue
            if part:
                part[2].append((n + 1, line))
            elif line.strip().startswith("|"):
                if in_table is None:
                    in_table = not self.table
                if in_table:
                    self.table.append((n + 1, cells(line)))
            elif line.strip():
                in_table = False if self.table else None

    def get(self, key):
        """The value of a header line, or None."""
        return next((v for _, k, v in self.header if k == key), None)

    def key_line(self, key):
        return next((ln for ln, k, _ in self.header if k == key), 1)

    def rows(self):
        """Data rows of the table: (line, cells), the header and separator rows left out."""
        return [(ln, c) for ln, c in self.table[1:] if not all(re.fullmatch(r":?-+:?", x) for x in c)]

    def part(self, name):
        return next((p for p in self.parts if p[1] == name), None)

    def label(self):
        """'cards/docker.md': the path inside the curriculum folder's parent."""
        return os.path.relpath(self.path, os.path.dirname(curriculum_dir()))

    def where(self, line=None):
        return "%s:%d" % (self.label(), line) if line else self.label()

    def ref(self):
        """The id a person types for this file."""
        if self.kind == "map":
            return "%s/%s" % (self.domain, self.id)
        return self.id


# ---------------------------------------------------------------- steps and tags of a card


def parse_steps(spec):
    """[3, 5, 6] from '3,5-6' (spaces allowed); None when it cannot be read or a range runs backwards."""
    spec = re.sub(r"\s+", "", spec or "")
    if not STEPS_RE.match(spec):
        return None
    out = []
    for piece in spec.split(","):
        a, _, b = piece.partition("-")
        a, b = int(a), int(b or a)
        if b < a:
            return None
        out += [n for n in range(a, b + 1) if n not in out]
    return out


def show_steps(steps):
    """'1, 3, 5-6' for [1, 3, 5, 6]."""
    runs = []
    for n in sorted(set(steps)):
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    return ", ".join("%d" % a if a == b else "%d-%d" % (a, b) for a, b in runs)


def parse_tag(text):
    """(steps, rest, bad) of an item: steps is None when it has no tag; bad is the tag when it cannot be read."""
    m = TAG_TRY.match(text)
    if not m:
        return None, text, None
    steps = parse_steps(m.group(1))
    if not steps:
        return None, text[m.end():], m.group(0).strip()
    return steps, text[m.end():], None


def kind_part(f):
    """The name of the card's fifth part for its kind, or None when the kind is not known."""
    return KIND_PART.get(f.get("kind") or "")


def card_parts(f):
    """The parts a card has in order: the required ones, its kind's part, and the optional ones it holds."""
    out = []
    for p in PARTS["card"]:
        if p != KIND_PART_SLOT:
            out.append(p)
            continue
        out += [kind_part(f)] if kind_part(f) else []
        out += [o for o in OPTIONAL_PARTS if f.part(o)]
    return out


def labelled(body, labels):
    """{label: [line, text]} of `Label: text` lines; a line with no label goes on the label before it."""
    found, last = {}, None
    for ln, t in body:
        m = re.match(r"^(%s):\s*(.*)$" % "|".join(labels), t.strip())
        if m:
            last = m.group(1)
            found.setdefault(last, [ln, ""])
            found[last][1] = (found[last][1] + " " + m.group(2)).strip()
        elif last and t.strip():
            found[last][1] += " " + t.strip()
    return found


def step_notes(f):
    """({step: {'line', 'notes': {label: [line, text]}, 'text'}}, [(line, problem)]) of "Step notes"."""
    part = f.part("Step notes")
    blocks, bad, cur = {}, [], None
    for ln, t in part[2] if part else []:
        if t.startswith("### "):
            m = re.match(r"^###\s+(\d+)\s*$", t)
            if not m:
                bad.append((ln, "a block of Step notes is headed '### N' (the step's number); fix '%s'" % t.strip()))
                cur = None
            elif int(m.group(1)) in blocks:
                bad.append((ln, "step %s has two blocks of Step notes; keep one" % m.group(1)))
                cur = None
            else:
                cur = blocks[int(m.group(1))] = {"line": ln, "body": []}
        elif cur is not None:
            cur["body"].append((ln, t))
    for b in blocks.values():
        b["notes"] = labelled(b["body"], NOTE_LABELS)
        b["text"] = "\n".join(t for _, t in b["body"]).strip()
    return blocks, bad


def deep_steps(f):
    """The step numbers of the `- Deep steps: N, N (why)` line of "Go deep, leave for later", or None."""
    items = [t for t in part_lines(f, "Go deep, leave for later") if t.startswith("- ")]
    m = re.match(r"^- Deep steps:\s*([\d,\s-]+?)\s*(?:\(|\.|$)", items[0]) if items else None
    return parse_steps(m.group(1)) if m else None


def is_met(word):
    """True for a word in round brackets: met in passing, not owned."""
    return word.startswith("(") and word.endswith(")")


def bare(word):
    """A word without its round brackets."""
    return word[1:-1].strip() if is_met(word) else word


def card_steps(f):
    """[(number, line, [lines as written])] of "Teaching order"; an indented line goes on the step before it."""
    part = f.part("Teaching order")
    steps = []
    for ln, t in part[2] if part else []:
        m = STEP_RE.match(t)
        if m:
            steps.append((int(m.group(1)), ln, [t.rstrip()]))
        elif steps and t.strip() and t[:1].isspace():
            steps[-1][2].append(t.rstrip())
    return steps


def step_text(lines):
    """The words of a step, its number left out and its lines joined."""
    return re.sub(r"^\d+\.\s+", "", " ".join(l.strip() for l in lines))


def tagged_items(f, name):
    """[(line, steps or None, text, bad tag)] of the `- ` items of a part, the tag taken off the text."""
    part = f.part(name) if name else None
    out = []
    for ln, text in list_items(part[2]) if part else []:
        steps, rest, bad = parse_tag(text[2:] if text.startswith("- ") else text)
        out.append((ln, steps, rest.strip(), bad))
    return out


def word_groups(f):
    """[(line, steps or None, [words], bad tag)] of "Words to own": groups split at `;`, each led by a tag."""
    part = f.part("Words to own")
    groups = []
    for ln, t in part[2] if part else []:
        for k, piece in enumerate(t.split(";")):
            if k or not groups:
                groups.append([ln, ""])
            if piece.strip() and not groups[-1][1].strip():
                groups[-1][0] = ln
            groups[-1][1] += " " + piece.strip()
    out = []
    for ln, text in groups:
        if text.strip():
            steps, rest, bad = parse_tag(text.strip())
            out.append((ln, steps, [w.strip() for w in rest.split(",") if w.strip()], bad))
    return out


def part_lines(f, name):
    """The non-blank lines of a part, as written."""
    part = f.part(name)
    return [t.rstrip() for _, t in part[2] if t.strip()] if part else []


DOCS = ("FORMAT.md", "REVIEWING.md", "REVIEWS.md")      # for builders and reviewers; never printed to a planner


def subject_of(cell):
    """(id, planned) of a table's subject cell: 'docker' or 'docker (planned)'."""
    m = PLANNED_RE.match(cell.strip())
    return (m.group(1), True) if m else (cell.strip(), False)


def load():
    """(files, strays): every curriculum file of the four kinds, and paths that are none of them."""
    root = curriculum_dir()
    files, strays = [], []
    if not os.path.isdir(root):
        return files, strays
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isfile(full):
            if name.endswith(".md") and name not in DOCS:
                strays.append(full)
            continue
        if name.startswith("."):
            continue
        for sub in sorted(os.listdir(full)):
            path = os.path.join(full, sub)
            if os.path.isdir(path):
                if not sub.startswith("."):
                    strays.extend(os.path.join(d, f) for d, _, fs in os.walk(path) for f in sorted(fs) if f.endswith(".md"))
                continue
            if not sub.endswith(".md"):
                continue
            stem = sub[:-3]
            if name == "cards":
                files.append(File(path, "card", stem))
            elif name == "roles":
                files.append(File(path, "role", stem))
            elif sub == "INDEX.md":
                files.append(File(path, "index", name, name))
            else:
                files.append(File(path, "map", stem, name))
    return files, strays


class Curriculum:
    """All files, with lookups by kind and id."""

    def __init__(self):
        self.files, self.strays = load()
        self.cards = {f.id: f for f in self.files if f.kind == "card"}
        self.roles = {f.id: f for f in self.files if f.kind == "role"}
        self.maps = [f for f in self.files if f.kind == "map"]
        self.indexes = {f.domain: f for f in self.files if f.kind == "index"}
        self.planned = {subject_of(c[1])[0] for m in self.maps for _, c in m.rows() if len(c) > 1 and subject_of(c[1])[1]}

    def domains(self):
        return sorted({f.domain for f in self.files if f.domain})

    def map_rows(self, ident):
        """(map, line, cells) of every track-map row whose subject is ident."""
        return [(m, ln, c) for m in self.maps for ln, c in m.rows() if len(c) > 1 and subject_of(c[1])[0] == ident]

    def hours(self, ident):
        """The study hours of a subject from the first track map that lists it with a number, or None."""
        for _, _, c in self.map_rows(ident):
            if len(c) > 5 and re.fullmatch(r"\d+", c[5]):
                return int(c[5])
        return None

    def find_map(self, ref):
        """The map named DOMAIN/TRACK, or TRACK when only one domain has it."""
        if "/" in ref:
            d, t = ref.split("/", 1)
            return next((m for m in self.maps if m.domain == d and m.id == t), None)
        hits = [m for m in self.maps if m.id == ref]
        return hits[0] if len(hits) == 1 else None

    def by_ref(self, ref):
        """A card or role id, DOMAIN/TRACK, a domain, or a path to a curriculum file; None when none."""
        if ref in self.cards:
            return self.cards[ref]
        if ref in self.roles:
            return self.roles[ref]
        short = re.fullmatch(r"(cards|roles)/([a-z0-9-]+)(?:\.md)?", ref)
        if short:
            return (self.cards if short.group(1) == "cards" else self.roles).get(short.group(2))
        found = self.find_map(ref) or self.indexes.get(ref)
        if found:
            return found
        for cand in (ref, os.path.join(ROOT, ref), os.path.join(curriculum_dir(), ref),
                     os.path.join(os.path.dirname(curriculum_dir()), ref)):
            full = os.path.abspath(cand)
            hit = next((f for f in self.files if f.path == full), None)
            if hit:
                return hit
        return None

# ---------------------------------------------------------------- check


def check_all(cur, notes=None):
    """[(where, message)] of every problem in the curriculum; each message says the fix.
    notes, a list, gets (where, message) of what is worth a look but does not fail the check."""
    errs = []
    notes = [] if notes is None else notes

    def err(f, line, msg):
        errs.append((f.where(line) if f else line, msg))

    def note(f, line, msg):
        notes.append((f.where(line), msg))
    err.note = note

    root = curriculum_dir()
    for path in cur.strays:
        errs.append((os.path.relpath(path, os.path.dirname(root)), "not a curriculum file: put cards in cards/, "
                     "roles in roles/ and track maps and INDEX.md in a domain folder, or remove it"))
    for d in cur.domains():
        if not ID_RE.match(d):
            errs.append((os.path.relpath(os.path.join(root, d), os.path.dirname(root)),
                         "domain folder '%s' must be lower-case words joined by hyphens; rename it" % d))
        if d not in cur.indexes and any(m.domain == d for m in cur.maps):
            errs.append((os.path.relpath(os.path.join(root, d), os.path.dirname(root)),
                         "domain '%s' has track maps but no INDEX.md; write it (FORMAT.md, Domain index)" % d))
    try:
        import us_check
        mistakes = us_check.read_mistakes(us_check.MISTAKES)[0]
    except Exception as exc:  # noqa: BLE001
        mistakes, us_check = [], None
        errs.append(("rules/known-mistakes.md", "could not be read (%s); fix it" % exc))
    for f in cur.files:
        check_common(cur, f, err)
        {"card": check_card, "map": check_map, "index": check_index, "role": check_role}[f.kind](cur, f, err)
        if us_check:
            check_mistakes(f, mistakes, us_check, err)
    check_cycles(cur, err)
    check_agree(cur, err)
    shared_words(cur, note)
    return errs


def check_common(cur, f, err):
    """Title, file name, header lines in order, status, sources, `## ` parts in order, size."""
    if not f.title:
        want = "# %s: Title" % f.id if f.kind in ("card", "role") else "# Title"
        err(f, 1, "the first line must be '%s'; add it" % want)
    if f.kind in ("card", "role") and f.title and f.title_id is None:
        err(f, 1, "the first line must be '# %s: Title' (the id, a colon, the title); fix it" % f.id)
    elif f.title_id is not None and f.title_id != f.id:
        err(f, 1, "the id '%s' differs from the file name '%s.md'; make them the same" % (f.title_id, f.id))
    if f.kind != "index" and not ID_RE.match(f.id):
        err(f, None, "the file name '%s' must be an id: lower-case words joined by hyphens; rename it" % f.id)
    required, optional = HEADERS[f.kind]
    order = required + [k for k in optional if k not in required]
    for line in f.bad_header:
        err(f, line, "not a header line: write 'key: value' (a long value goes on with an indented line), "
                     "or leave a blank line before the text")
    keys = [k for _, k, _ in f.header]
    for ln, k, _ in f.header:
        if k not in order:
            err(f, ln, "'%s:' is not a header line of a %s; the lines are %s" % (k, NAMES[f.kind], ", ".join(order)))
        elif keys.count(k) > 1:
            err(f, ln, "'%s:' is written twice; keep one" % k)
    for k in required:
        if k not in keys and k not in optional:
            err(f, 1, "no '%s:' line; add it under the title (the lines in order: %s)" % (k, ", ".join(order)))
    known = [k for k in keys if k in order]
    if known != sorted(known, key=order.index):
        err(f, f.header[0][0] if f.header else 1, "header lines are out of order; the order is %s" % ", ".join(order))
    for ln, k, v in f.header:
        if k in ("for", "leads to", "kind", "needs", "sources", "status") and not v:
            err(f, ln, "'%s:' is empty; fill it in" % k)
    status = f.get("status")
    if status:
        m = STATUS_RE.match(status)
        if not m or not as_date(m.group(2)) or (m.group(1) == "built" and m.group(3)):
            err(f, f.key_line("status"), "status '%s' cannot be read; write 'built YYYY-MM-DD', or 'reviewed' or "
                                         "'tested' YYYY-MM-DD with an optional ' by WHO'" % status)
    want = card_parts(f) if f.kind == "card" else PARTS[f.kind]
    got = [p[1] for p in f.parts]
    for ln, name, body in f.parts:
        if f.kind == "card" and name in KIND_PART.values() and name not in want:
            if kind_part(f):
                err(f, ln, "'## %s' is the part of a %s card; a %s card has '## %s' (FORMAT.md, the part made for "
                           "the kind): rename it, or fix kind:" % (name, next(k for k, v in KIND_PART.items()
                                                                              if v == name), f.get("kind"), kind_part(f)))
        elif name not in want:
            err(f, ln, "'## %s' is not a part of a %s; the parts are: %s" % (
                name, NAMES[f.kind], ", ".join(want) if want else "none (a table and one line)"))
        elif got.count(name) > 1:
            err(f, ln, "'## %s' is written twice; keep one" % name)
        elif not any(t.strip() for _, t in body):
            err(f, ln, "'## %s' is empty; write it" % name)
    for name in want:
        if name not in got and f.kind == "card" and name == kind_part(f):
            err(f, None, "no '## %s' part, which a %s card must have (FORMAT.md, the part made for the kind); add it "
                         "after Teaching order" % (name, f.get("kind")))
        elif name not in got:
            err(f, None, "no '## %s' part; add it (the parts in order: %s)" % (name, ", ".join(want)))
    present = [g for g in got if g in want]
    if present != sorted(present, key=want.index):
        err(f, f.parts[0][0], "the parts are out of order; the order is: %s" % ", ".join(want))
    size = tokens(f.text)
    if size > LIMITS[f.kind]:
        err(f, None, "%d tokens; a %s may have %s: cut what teaches least, or split it in two" % (
            size, NAMES[f.kind], "{:,}".format(LIMITS[f.kind])))


def need_entries(text):
    """[[id, ...]] of a needs: line: entries split at commas, alternatives (any one will do) at `|`."""
    if not text or text.strip() == "none":
        return []
    return [[a.strip() for a in e.split("|")] for e in text.split(",") if e.strip()]


def known_subject(cur, ident):
    """True if ident is a card or a planned subject of some track map."""
    return ident in cur.cards or ident in cur.planned


def check_card(cur, f, err):
    kind = f.get("kind")
    if kind is not None and kind and kind not in KINDS:
        err(f, f.key_line("kind"), "kind '%s' is not known; use one of %s" % (kind, ", ".join(KINDS)))
    needs = f.get("needs")
    if needs and needs.strip() != "none":
        for n in [a for entry in need_entries(needs) for a in entry]:
            if not ID_RE.match(n):
                err(f, f.key_line("needs"), "needs '%s' is not an id (lower-case words joined by hyphens); fix it" % n)
            elif not known_subject(cur, n):
                err(f, f.key_line("needs"), "needs '%s', which is no card and no '(planned)' row of a track map; "
                                            "fix the id, or add it to a track map as '%s (planned)'" % (n, n))
    part = f.part("Teaching order")
    if part:
        steps = [(ln, int(m.group(1))) for ln, t in part[2] for m in [re.match(r"^(\d+)\.\s+\S", t)] if m]
        if not STEPS[0] <= len(steps) <= STEPS[1]:
            err(f, part[0], "Teaching order has %d numbered steps; give %d to %d, each about a chapter" % (
                len(steps), STEPS[0], STEPS[1]))
        if [n for _, n in steps] != list(range(1, len(steps) + 1)):
            err(f, part[0], "Teaching order steps must be numbered 1, 2, 3 ... in order; renumber them")
    part = f.part("Wrong beliefs")
    if part:
        items = tagged_items(f, "Wrong beliefs")
        if not items:
            err(f, part[0], "Wrong beliefs has no items; write each as - [3] \"the belief\" (the truth)")
        for ln, _, text, _ in items:
            if not re.match(r'^(?:"[^"]+"|“[^”]+”) \([^()]*(?:\([^()]*\)[^()]*)*\)\.?$', text):
                err(f, ln, "a wrong belief must be a quoted belief and the truth in brackets: - [3] \"the belief\" (the truth)")
    check_tags(f, err)
    part = f.part("Mastery ladder")
    if part:
        items = list_items(part[2])
        names = [re.match(r"^- (\w+):", t).group(1) if re.match(r"^- (\w+):\s*\S", t) else None for _, t in items]
        if names != LADDER:
            err(f, part[0], "Mastery ladder must be four lines in order: - Use: ..., - Explain: ..., - Build: ..., "
                            "- Design: ..., each a task the learner does")
        for ln, t in items:
            if re.search(r"\bunderstand", t, re.I):
                err(f, ln, "a rung must be a task the learner does, never 'understands X': say what they do")


TAG_HELP = "[3], [5-6], [2,8] or [1,4-6]"


def check_tags(f, err):
    """Every tag names steps the card has; required tags are there; notes on thin steps."""
    steps = card_steps(f)
    count = len(steps)

    def names(ln, tags, bad, where, required):
        if bad:
            err(f, ln, "the tag %s in %s cannot be read; write %s" % (bad, where, TAG_HELP))
        elif tags is None and required:
            err(f, ln, "every %s in %s needs a tag naming its step, such as %s; add it" % (
                "group" if where == "Words to own" else "item", where, TAG_HELP))
        elif tags and (min(tags) < 1 or max(tags) > count):
            gone = [n for n in tags if not 1 <= n <= count]
            err(f, ln, "the tag in %s names step %s, but the card has steps 1 to %d; fix the tag" % (
                where, show_steps(gone), count))

    for name, required in ((kind_part(f), False), ("Believable numbers", False), ("Never omit", False),
                           ("Wrong beliefs", True), ("Failures to diagnose", True)):
        for ln, tags, _, bad in tagged_items(f, name):
            names(ln, tags, bad, name, required)
    for ln, tags, _, bad in word_groups(f):
        names(ln, tags, bad, "Words to own", True)
    check_deepened(f, err, steps)
    if not hasattr(err, "note") or not steps:
        return
    covered = {n for _, tags, _, _ in word_groups(f) + tagged_items(f, "Wrong beliefs") for n in tags or []}
    for n, ln, lines in steps:
        text = step_text(lines)
        if not concrete(text):
            err.note(f, ln, "step %d names nothing concrete (no `code`, number or name): name the real thing that "
                            "carries it" % n)
        if n not in covered:
            err.note(f, ln, "step %d has no word and no wrong belief tagged to it: tag one, or ask whether it is a "
                            "step" % n)


def check_deepened(f, err, steps):
    """A card with Step notes: a full block for each step, a typed Try, a valid Deep steps line, at most five owned
    words a step (step 1: four); notes on long step lines and blocks. A card without: an error."""
    note = getattr(err, "note", None)
    if not f.part("Step notes"):
        err(f, None, 'not yet deepened: no "Step notes" part; add a \'### N\' block for each step with Need:, '
                     'Show:, Explain: and Try:')
        return
    blocks, bad = step_notes(f)
    for ln, msg in bad:
        err(f, ln, msg)
    have = [n for n, _, _ in steps]
    for n, ln, lines in steps:
        if n not in blocks:
            err(f, ln, "step %d has no block in Step notes; add '### %d' with Need:, Show:, Explain: and Try:" % (n, n))
        elif note and tokens(step_text(lines)) > STEP_TOKENS:
            note(f, ln, "step %d is about %d tokens; a step line is lean (about 60): move the detail into its Step "
                        "notes" % (n, tokens(step_text(lines))))
    for n, b in sorted(blocks.items()):
        if n not in have:
            err(f, b["line"], "Step notes has a block for step %d, which the card does not have; fix the number" % n)
            continue
        missing = [lab for lab in NOTE_REQUIRED if not b["notes"].get(lab, [0, ""])[1]]
        if missing:
            err(f, b["line"], "the Step notes of step %d have no %s line; add %s" % (
                n, " and no ".join(m + ":" for m in missing), ", ".join(m + ":" for m in missing)))
        need = b["notes"].get("Need")
        if need and need[1] and not need[1].rstrip().endswith("?"):
            err(f, need[0], "the Need: of step %d must be the learner's question, ending with '?'" % n)
        tries = b["notes"].get("Try")
        if tries and tries[1]:
            pieces = [x.strip() for x in tries[1].split(";")]
            if not TRY_TYPES.match(pieces[0]) or sum(1 for x in pieces if TRY_TYPES.match(x)) < 2:
                err(f, tries[0], "the Try: of step %d needs two tasks separated by ';', each beginning with predict:, "
                                 "explain:, fix:, apply:, decide:, build: or recall:" % n)
        if note and tokens(b["text"]) > BLOCK_TOKENS:
            note(f, b["line"], "the Step notes of step %d are about %d tokens (about %d at most): keep what makes it "
                               "land" % (n, tokens(b["text"]), BLOCK_TOKENS))
    deep = deep_steps(f)
    low, high = (1, 3) if len(steps) <= 7 else (2, 4)
    if not deep or not low <= len(deep) <= high or any(n not in have for n in deep):
        part = f.part("Go deep, leave for later")
        err(f, part[0] if part else None, "no valid 'Deep steps:' line: make the first item of 'Go deep, leave for "
                                          "later' '- Deep steps: N, N (why)' naming %d to %d steps the card has" % (low, high))
    owned = {}
    for ln, tags, words, _ in word_groups(f):
        for n in tags or []:
            owned.setdefault(n, [ln, 0])[1] += sum(1 for w in words if not is_met(w))
    for n, (ln, count) in sorted(owned.items()):
        cap = OWNED_FIRST if n == 1 else OWNED_MAX
        if count > cap:
            err(f, ln, "step %d owns %d words (%s at most): put the rest in brackets (met in passing) or at a later "
                       "step" % (n, count, "four" if n == 1 else "five"))


def concrete(text):
    """True when a step names something real: a backtick span, a digit, or a capitalised word after the first
    (a word with a capital inside it, such as `ConfigMap` or `DNS`, counts wherever it stands)."""
    if "`" in text or re.search(r"\d", text):
        return True
    found = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
    return any(w[0].isupper() for w in found[1:]) or any(re.search(r"[A-Z]", w[1:]) for w in found)


def list_items(body):
    """(line, text) of each `- ` item of a part; a line that is not an item goes on the item before it."""
    items = []
    for ln, t in body:
        if not t.strip():
            continue
        if t.startswith("- "):
            items.append([ln, t.strip()])
        elif items:
            items[-1][1] += " " + t.strip()
        else:
            items.append([ln, t.strip()])
    return [tuple(i) for i in items]


def check_table(f, err):
    """The table is there with the right columns: True when its rows can be read."""
    cols = COLUMNS[f.kind]
    if not f.table:
        err(f, None, "no table; add it with the columns | %s |" % " | ".join(cols))
        return False
    ln, head = f.table[0]
    if [c.lower() for c in head] != [c.lower() for c in cols]:
        err(f, ln, "the table's columns must be | %s |; fix the header row" % " | ".join(cols))
        return False
    if not f.rows():
        err(f, ln, "the table has no rows; add them")
    for rl, c in f.rows():
        if len(c) != len(cols):
            err(f, rl, "this row has %d cells; the table has %d columns" % (len(c), len(cols)))
    return True


def level_ok(text):
    return any(text.strip().lower() == lv.lower() for lv in LEVELS)


def check_map(cur, f, err):
    goals = f.part("Goals")
    if goals:
        items = [t for t in part_lines(f, "Goals") if t.startswith("- ")]
        if not f.table and any(t.strip().startswith("|") for _, t in goals[2]):
            err(f, goals[0], "'## Goals' comes before the table; put it after the table and before '## Why this order'")
        elif goal_blocks(f):
            if f.table:
                check_goal_blocks(cur, f, err, goal_blocks(f))
        elif not GOALS[0] <= len(items) <= GOALS[1]:
            err(f, goals[0], "'## Goals' has %d list items; give %d to %d, each '- a goal in the learner's words: "
                             "rows 1 to 3'" % (len(items), GOALS[0], GOALS[1]))
        if f.table and not goal_blocks(f):
            check_goal_refs(cur, f, err, goals)
    if not check_table(f, err):
        return
    rows = [(ln, c) for ln, c in f.rows() if len(c) == len(COLUMNS["map"])]
    place = {}
    ids = [subject_of(c[1])[0] for _, c in rows]
    for k, (ln, c) in enumerate(rows, 1):
        ident, planned = subject_of(c[1])
        if ID_RE.match(ident):
            place.setdefault(ident, k)
    for k, (ln, c) in enumerate(rows, 1):
        num, subject, needs, hours, level = c[0], c[1], c[2], c[5], c[6]
        if num != str(k):
            err(f, ln, "row number is '%s'; number the rows 1, 2, 3 ... in order (this is %d)" % (num, k))
        ident, planned = subject_of(subject)
        if not ID_RE.match(ident):
            err(f, ln, "subject '%s' must be an id (lower-case words joined by hyphens), or 'id (planned)'" % subject)
        elif planned and ident in cur.cards:
            err(f, ln, "'%s' has a card now; write it without '(planned)'" % ident)
        elif not planned and ident not in cur.cards:
            err(f, ln, "'%s' has no card; write '%s (planned)', or write the card" % (ident, ident))
        elif place.get(ident) != k:
            err(f, ln, "'%s' is already row %d; keep one row" % (ident, place[ident]))
        for need in [x.strip() for x in re.split(r"[,;]", needs) if x.strip()]:
            if need.lower() in ("none", "-", "—", "nothing"):
                continue
            if re.fullmatch(r"\d+", need):
                if not 1 <= int(need) < k:
                    err(f, ln, "needs row %s, which is not a row before this one; a subject comes after what it "
                               "needs: reorder the rows or fix the number" % need)
            elif not ID_RE.match(need):
                err(f, ln, "needs '%s': write row numbers or subject ids, joined by commas" % need)
            elif need in place:
                if place[need] >= k:
                    err(f, ln, "needs '%s', which is row %d, not before it; reorder the rows" % (need, place[need]))
            elif not known_subject(cur, need):
                err(f, ln, "needs '%s', which is no card and no '(planned)' row of a track map; fix the id" % need)
        if ID_RE.match(ident) and ident in cur.cards and not planned:
            check_row_needs(f, err, k, ln, ident, needs, need_entries(cur.cards[ident].get("needs")), place, ids)
        if not re.fullmatch(r"\d+", hours):
            err(f, ln, "hours '%s' must be a number (study hours, rounded to 5)" % hours)
        if not level_ok(level):
            err(f, ln, "level '%s' is not one of %s" % (level, ", ".join(LEVELS)))
    index = cur.indexes.get(f.domain)
    if index and not any(c and (c[0] == f.id or c[0].split(" (")[0] == f.id) for _, c in index.rows()):
        err(index, None, "track '%s' (%s) is not listed; add a row for it" % (f.id, f.label()))


GOAL_RANGES = r"\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*(?:\s+and\s+\d+(?:\s*-\s*\d+)?)?"
GOAL_ROW_STEPS = re.compile(r"\brow\s+(\d+)\s+steps?\s+(%s)" % GOAL_RANGES)
GOAL_ROWS_TO = re.compile(r"\brows?\s+(\d+)\s+to\s+(\d+)")
GOAL_ROWS = re.compile(r"\brows?\s+(\d+(?:\s*(?:,|and)\s*\d+)*)")
GOAL_CARD = re.compile(r"(?<![\w/-])([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\s+(%s)(?![\w-])" % GOAL_RANGES)


def goal_blocks(f):
    """[{'title', 'line', 'notes': {label: [line, text]}, 'lines'}] of the `### ` blocks of a map's Goals."""
    part = f.part("Goals")
    blocks = []
    for ln, t in part[2] if part else []:
        if t.startswith("### "):
            blocks.append({"title": t[4:].strip(), "line": ln, "body": []})
        elif blocks:
            blocks[-1]["body"].append((ln, t))
    for b in blocks:
        b["notes"] = labelled(b["body"], GOAL_LABELS)
        b["lines"] = ["### " + b["title"]] + [t.rstrip() for _, t in b["body"]]
        while b["lines"] and not b["lines"][-1].strip():
            b["lines"].pop()
    return blocks


def card_refs(text):
    """([(id, [steps] or None)], [unreadable entries]) of 'card-id 1-3, 5; card-id' (a full stop at the end)."""
    refs, bad = [], []
    for piece in [x.strip().rstrip(".") for x in text.split(";") if x.strip().rstrip(".").strip()]:
        m = re.match(r"^([a-z0-9]+(?:-[a-z0-9]+)*)(?:\s+(.+))?$", piece)
        steps = parse_steps(re.sub(r"\s+and\s+", ",", m.group(2))) if m and m.group(2) else None
        if not m or (m.group(2) and not steps):
            bad.append(piece)
        else:
            refs.append((m.group(1), steps))
    return refs, bad


def check_goal_blocks(cur, f, err, blocks):
    """Goal blocks: two to five, each with Steps, Open with, Deep and Order; steps and cards that exist; Deep
    within Steps; every card of Steps named in Order (unless the order is the rows')."""
    if not GOALS[0] <= len(blocks) <= GOALS[1]:
        err(f, f.part("Goals")[0], "'## Goals' has %d goal blocks; give %d to %d" % (len(blocks), GOALS[0], GOALS[1]))
    planned = {i for _, c in f.rows() if len(c) > 1 for i, p in [subject_of(c[1])] if p}
    for b in blocks:
        notes, name = b["notes"], "goal '%s'" % b["title"]
        missing = [lab for lab in GOAL_REQUIRED if not notes.get(lab, [0, ""])[1]]
        if missing:
            err(f, b["line"], "%s has no %s line; add it" % (name, " and no ".join(m + ":" for m in missing)))
        taken = {}
        for label in ("Steps", "Deep"):
            if label not in notes:
                continue
            ln, text = notes[label]
            refs, bad = card_refs(text)
            for piece in bad:
                err(f, ln, "%s: cannot read '%s' in %s:; write card-id N-M, N; card-id ..." % (name, piece, label))
            for ident, steps in refs:
                if ident in cur.cards:
                    have = len(card_steps(cur.cards[ident]))
                    for n in [n for n in steps or [] if not 1 <= n <= have]:
                        err(f, ln, "goal names step %d of %s, which has %d steps" % (n, ident, have))
                elif ident not in planned:
                    err(f, ln, "goal names '%s', which is no card and no planned subject of this map; fix the id" % ident)
                if label == "Steps":
                    every = taken.get(ident, set()) | set(steps if steps else range(1, 1000))
                    taken[ident] = every
                elif ident not in taken or any(n not in taken[ident] for n in steps or [0]):
                    err(f, ln, "%s: Deep: names %s %s, which is not in its Steps:" % (
                        name, ident, show_steps(steps) if steps else "(all)"))
        order = notes.get("Order", [0, ""])
        if order[1] and not re.search(r"\brows? in order\b|\brow order\b", order[1], re.I):
            for ident in [i for i in taken if i in cur.cards or i in planned]:
                if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(ident), order[1]):
                    err(f, order[0], "%s: %s is in Steps: but not in Order:; name it there, or write 'rows in order'" % (
                        name, ident))


def goal_numbers(text):
    """[3, 5, 6, 11] of '3, 5-6 and 11'."""
    return parse_steps(re.sub(r"\s+and\s+", ",", text)) or []


def check_goal_refs(cur, f, err, goals):
    """Every row and step a goal names exists: 'rows 1 to 5', 'row 3 steps 1-6', 'scaling-data 1-4, 6';
    a hyphenated id (or a card id) followed by steps must be a card or a planned subject of this map."""
    subjects = [subject_of(c[1]) for _, c in f.rows() if len(c) == len(COLUMNS["map"])]
    planned = {i for i, p in subjects if p}

    def row(ln, n):
        if not 1 <= n <= len(subjects):
            err(f, ln, "goal names row %d, which the map does not have" % n)
            return None
        return subjects[n - 1]

    def steps(ln, ident, numbers):
        have = len(card_steps(cur.cards[ident]))
        for n in numbers:
            if not 1 <= n <= have:
                err(f, ln, "goal names step %d of %s, which has %d steps" % (n, ident, have))

    for ln, text in list_items(goals[2]):
        taken = []
        for m in GOAL_ROW_STEPS.finditer(text):
            taken.append(m.span())
            got = row(ln, int(m.group(1)))
            if got and not got[1] and got[0] in cur.cards:
                steps(ln, got[0], goal_numbers(m.group(2)))
        for m in GOAL_ROWS_TO.finditer(text):
            taken.append(m.span())
            for n in (int(m.group(1)), int(m.group(2))):
                row(ln, n)
        for m in GOAL_ROWS.finditer(text):
            if not any(a <= m.start() < b for a, b in taken):
                taken.append(m.span())
                for n in goal_numbers(m.group(1)):
                    row(ln, n)
        for m in GOAL_CARD.finditer(text):
            ident = m.group(1)
            if any(a <= m.start() < b for a, b in taken) or ("-" not in ident and ident not in cur.cards):
                continue
            if ident in cur.cards:
                steps(ln, ident, goal_numbers(m.group(2)))
            elif ident not in planned:
                err(f, ln, "goal names '%s', which is no card and no planned subject of this map; fix the id" % ident)


def check_row_needs(f, err, k, ln, ident, cell, entries, place, ids):
    """Row k's card needs: each entry (any one alternative) an earlier row or named in "Needs first";
    a note for a row number in "Needs first" whose subject the card does not need."""
    named = [x.strip() for x in re.split(r"[,;]", cell) if x.strip()]
    for entry in entries:
        if not any((a in place and place[a] < k) or a in named for a in entry):
            err(f, ln, 'row %d %s: its card needs %s, which is not an earlier row and is not named in "Needs first"'
                % (k, ident, " or ".join(entry)))
    wanted = {a for entry in entries for a in entry}
    for x in named:
        if re.fullmatch(r"\d+", x) and 1 <= int(x) < k and ids[int(x) - 1] not in wanted and hasattr(err, "note"):
            err.note(f, ln, 'row %d: "Needs first" names row %s (%s), which the card does not need' % (k, x, ids[int(x) - 1]))


def check_index(cur, f, err):
    check_table(f, err)
    for ln, c in f.rows():
        if c:
            track = subject_of(c[0])[0]
            if not ID_RE.match(track):
                err(f, ln, "track '%s' must be an id (the track map's file name), or 'id (planned)'" % c[0])


def check_role(cur, f, err):
    if not check_table(f, err):
        return
    cards = 0
    for ln, c in f.rows():
        if len(c) != len(COLUMNS["role"]):
            continue
        ident, planned = subject_of(c[0])
        if not ID_RE.match(ident):
            err(f, ln, "subject '%s' must be an id (lower-case words joined by hyphens), or 'id (planned)'" % c[0])
        elif planned and ident in cur.cards:
            err(f, ln, "'%s' has a card now; write it without '(planned)'" % ident)
        elif not planned and ident not in cur.cards:
            err(f, ln, "'%s' has no card; write '%s (planned)', or write the card" % (ident, ident))
        else:
            cards += not planned
        if not level_ok(c[1]):
            err(f, ln, "level '%s' is not one of %s" % (c[1], ", ".join(LEVELS)))
        if c[2].strip().lower() not in CLASSES:
            err(f, ln, "class '%s' is not one of %s" % (c[2], ", ".join(CLASSES)))
    if f.rows() and not cards:
        err(f, None, "the role names no card; at least one subject must have a card")


def about(f):
    """The words that say what a file is about, for the subjects of rules/known-mistakes.md."""
    words = [f.id.replace("-", " "), f.title, f.get("aliases") or "", f.get("for") or ""]
    if f.kind == "map":
        words += [subject_of(c[1])[0].replace("-", " ") for _, c in f.rows() if len(c) > 1]
    return "\n".join(words)


def check_mistakes(f, rows, us_check, err):
    """ERROR for each text that matches a known mistake whose subject is about this file."""
    subject = about(f)
    rows = [r for r in rows if us_check.subject_applies(r["subject"], subject)]
    if not rows:
        return
    for line, text in text_units(f.lines):
        for r in rows:
            if r["re"].search(text):
                err(f, line, "known mistake (%s): %s [%s]; reword it" % (r["subject"], r["truth"], r["source"]))


def text_units(lines):
    """(first line, text) of each paragraph, list item and table row, whitespace runs collapsed."""
    units, cur = [], None
    for k, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("```"):
            cur = None
            continue
        if cur is None or re.match(r"^(?:[-*] |\d+\. |\||#)", s):
            cur = [k, s]
            units.append(cur)
        else:
            cur[1] += " " + s
    return [(k, " ".join(t.split())) for k, t in units]


def shared_words(cur, note):
    """A note on the later card (by id) for each word of "Words to own" that an earlier card also owns, when the two
    can meet in one learner's plan: a track map lists both, or one needs the other (any alternative, any depth)."""
    owners = {}
    either = {frozenset((a, b)) for f in cur.cards.values() for e in need_entries(f.get("needs"))
              for a in e for b in e if a != b}               # alternatives of one need: a learner takes one
    for ident in sorted(cur.cards):
        f = cur.cards[ident]
        for ln, _, words, _ in word_groups(f):
            for w in [w for w in words if not is_met(w)]:
                key = " ".join(w.lower().split())
                first = next((o for o in owners.get(key, []) if o != ident and frozenset((o, ident)) not in either
                              and can_meet(cur, o, ident)), None)
                owners.setdefault(key, []).append(ident)
                if first:
                    note(f, ln, "word '%s' is also owned by %s: one home per word" % (w.strip(), first))


def needed_by(cur, ident):
    """Every card id a card needs, directly or through the needs of what it needs (all alternatives)."""
    seen, todo = set(), [ident]
    while todo:
        f = cur.cards.get(todo.pop())
        for a in [a for e in need_entries(f.get("needs") if f else None) for a in e]:
            if a not in seen:
                seen.add(a)
                todo.append(a)
    return seen


def can_meet(cur, a, b):
    """True when cards a and b can be in one learner's plan: a track map lists both, or one needs the other."""
    for m in cur.maps:
        ids = {subject_of(c[1])[0] for _, c in m.rows() if len(c) > 1}
        if a in ids and b in ids:
            return True
    return b in needed_by(cur, a) or a in needed_by(cur, b)


def check_agree(cur, err):
    """ERROR when one card has different Hours or a different Level in two track maps."""
    seen = {}
    for m in cur.maps:
        for ln, c in m.rows():
            if len(c) != len(COLUMNS["map"]):
                continue
            ident, planned = subject_of(c[1])
            if planned or ident not in cur.cards:
                continue
            hours, level = c[5].strip(), " ".join(c[6].split())
            if ident not in seen:
                seen[ident] = (m, hours, level)
                continue
            first, h0, l0 = seen[ident]
            if hours != h0:
                err(m, ln, "%s is %s hours in %s and %s in %s: one home per fact, make them agree" % (
                    ident, h0, first.ref(), hours, m.ref()))
            if level.lower() != l0.lower():
                err(m, ln, "%s is level %s in %s and %s in %s: one home per fact, make them agree" % (
                    ident, l0, first.ref(), level, m.ref()))


def check_cycles(cur, err):
    """ERROR once for each circle in what subjects need (cards' needs and track-map rows)."""
    graph, owner = {}, {}
    for f in cur.cards.values():
        # an entry with alternatives (a | b) is no edge: any one of them will do, so it alone cannot force a circle;
        # only single-id entries are followed
        graph.setdefault(f.id, set()).update(e[0] for e in need_entries(f.get("needs")) if len(e) == 1)
        owner[f.id] = f
    for m in cur.maps:
        rows = [c for _, c in m.rows() if len(c) == len(COLUMNS["map"])]
        ids = [subject_of(c[1])[0] for c in rows]
        for c, ident in zip(rows, ids):
            for need in [x.strip() for x in re.split(r"[,;]", c[2]) if x.strip()]:
                if re.fullmatch(r"\d+", need):
                    need = ids[int(need) - 1] if 1 <= int(need) <= len(ids) else None
                if need and ID_RE.match(need):
                    graph.setdefault(ident, set()).add(need)
                    owner.setdefault(ident, m)
    seen, done, found = set(), set(), set()

    def visit(node, path):
        if node in path:
            ring = path[path.index(node):] + [node]
            key = frozenset(ring)
            if key not in found:
                found.add(key)
                err(owner.get(ring[0]), None, "needs go round in a circle: %s; remove one of these needs"
                    % " -> ".join(ring))
            return
        if node in done:
            return
        path.append(node)
        for nxt in sorted(graph.get(node, ())):
            visit(nxt, path)
        path.pop()
        done.add(node)

    for node in sorted(graph):
        if node not in seen:
            visit(node, [])
            seen.add(node)


def counts_line(cur):
    return "check ok: %d cards, %d maps, %d roles, %d indexes" % (
        len(cur.cards), len(cur.maps), len(cur.roles), len(cur.indexes))


def cmd_check(cur):
    if not cur.files and not cur.strays:
        print("no curriculum files")
        return 0
    notes = []
    errs = check_all(cur, notes)
    for where, msg in errs:
        print("ERROR %s %s" % (where, msg))
    for where, msg in notes:
        print("note: %s: %s" % (where, msg))
    print("check failed" if errs else counts_line(cur))
    return 1 if errs else 0

# ---------------------------------------------------------------- printing


def show(f):
    sys.stdout.write(f.text if f.text.endswith("\n") else f.text + "\n")


def show_card(cur, f):
    show(f)
    rows = cur.map_rows(f.id)
    print("\nIn tracks:%s" % ("" if rows else " none"))
    for m, ln, c in rows:
        head = m.table[0][1]
        print("%s/%s:\n| %s |\n| %s |" % (m.domain, m.id, " | ".join(head), " | ".join(c)))
    return 0


def words(text):
    return [stem(w) for w in re.findall(r"[a-z0-9+#]+", text.lower()) if w not in STOP]


def stem(w):
    for end in ("ing", "es", "ed", "s"):
        if w.endswith(end) and len(w) - len(end) >= 4:
            return w[:-len(end)]
    return w


def candidates(cur):
    """(kind word, id, title, exact names, words) of every card, track, domain and role."""
    out = []
    for f in cur.files:
        exact = {f.id, f.title.lower()}
        text = [f.id, f.title]
        if f.kind == "card":
            aliases = [a.strip().lower() for a in (f.get("aliases") or "").split(",") if a.strip()]
            exact |= set(aliases)
            text += aliases
        if f.kind == "map":
            exact |= {f.ref()}
            text += [f.domain]
        out.append((f, exact, set(words(" ".join(text)))))
    return out


def score(query, exact, have):
    """2 for an exact id, alias or title; else the share of the query's words the file has."""
    joined = " ".join(query.lower().split())
    if joined in exact or joined.replace(" ", "-") in exact:
        return 2.0
    q = words(query)
    return (sum(1 for w in q if w in have) / len(q)) if q else 0.0


def cmd_find(cur, query):
    scored = sorted(((score(query, ex, have), f) for f, ex, have in candidates(cur)),
                    key=lambda x: (-x[0], x[1].kind != "card", x[1].ref()))
    scored = [(s, f) for s, f in scored if s > 0]
    if not scored:
        print("nothing in the curriculum matches %s" % query)
        return 1
    top = scored[0][0]
    close = [(s, f) for s, f in scored if s == top or (top < 2 and s >= top - 0.2)]
    if len(close) == 1:
        f = close[0][1]
        return show_card(cur, f) if f.kind == "card" else show(f) or 0
    width = max(len(f.ref()) for _, f in close[:LIST_MAX])
    for _, f in close[:LIST_MAX]:
        print("%-*s  %-6s  %s" % (width, f.ref(), NAMES[f.kind], f.title))
    return 0


def parse_have(text):
    """{id: level} from 'git:3, python:2'; None when it cannot be read."""
    have = {}
    for part in [p.strip() for p in text.split(",") if p.strip()]:
        m = re.fullmatch(r"([a-z0-9-]+)\s*:\s*([1-5])(?:\s+\w+)?", part)
        if not m:
            return None
        have[m.group(1)] = int(m.group(2))
    return have


def cmd_role(cur, ident, have):
    f = cur.roles.get(ident)
    if not f:
        print("no role '%s'; roles: %s" % (ident, ", ".join(sorted(cur.roles)) or "none yet"))
        return 1
    drop, left, extra = set(), [], []
    for ln, c in f.rows():
        if len(c) < 2:
            continue
        sid = subject_of(c[0])[0]
        need = re.match(r"\s*(\d)", c[1])
        if need and sid in have and have[sid] >= int(need.group(1)):
            drop.add(ln)
        elif len(c) > 2 and c[2].strip().lower() == "specialist":
            extra.append(sid)
        else:
            left.append(sid)
    for k, line in enumerate(f.lines, 1):
        if k not in drop:
            print(line)
    print("\nleft: " + hours_left(cur, left))
    if extra:
        print("Specialist lines, if you want them: " + hours_left(cur, extra))
    first = needed_first(cur, [subject_of(c[0])[0] for _, c in f.rows() if c], left + extra, have)
    if first:
        print(first)
    return 0


def hours_left(cur, subjects):
    """'2 subjects, about 50 hours (hours unknown for: x)' for these subjects."""
    hours = {s: cur.hours(s) for s in subjects}
    known = sum(h for h in hours.values() if h is not None)
    unknown = [s for s in subjects if hours[s] is None]
    count = "%d subject%s" % (len(subjects), "" if len(subjects) == 1 else "s")
    if not subjects:
        return "0 subjects, about 0 hours"
    if len(unknown) == len(subjects):
        return count + ", hours unknown (no track map gives them)"
    return count + ", about %d hours%s" % (known, " (hours unknown for: %s)" % ", ".join(unknown) if unknown else "")


def cmd_index(cur, domain):
    if domain:
        f = cur.indexes.get(domain)
        if not f:
            print("no domain '%s'; domains: %s" % (domain, ", ".join(cur.domains()) or "none yet"))
            return 1
        show(f)
        return 0
    if not cur.domains():
        print("no curriculum files")
        return 0
    for d in cur.domains():
        f = cur.indexes.get(d)
        print("%s  %s" % (d, f.title if f else "(no INDEX.md)"))
    return 0


def status_of(f):
    m = STATUS_RE.match(f.get("status") or "")
    return (m.group(1), as_date(m.group(2))) if m else (None, None)


def cmd_status(cur, months):
    if not cur.files:
        print("no curriculum files")
        return 0
    from us_check import months_before
    for d in cur.domains():
        maps = [m for m in cur.maps if m.domain == d]
        subjects = [subject_of(c[1]) for m in maps for _, c in m.rows() if len(c) > 1]
        cards = {i for i, p in subjects if not p and i in cur.cards}
        planned = {i for i, p in subjects if p}
        st = [status_of(cur.cards[i])[0] for i in cards]
        print("%s: %d track%s, cards %d built / %d reviewed / %d tested, %d planned subject%s" % (
            d, len(maps), "" if len(maps) == 1 else "s", st.count("built"), st.count("reviewed"), st.count("tested"),
            len(planned), "" if len(planned) == 1 else "s"))
    listed = {subject_of(c[1])[0] for m in cur.maps for _, c in m.rows() if len(c) > 1}
    loose = sorted(set(cur.cards) - listed)
    if loose:
        print("cards in no track: %s" % ", ".join(loose))
    if cur.roles:
        st = [status_of(r)[0] for r in cur.roles.values()]
        print("roles: %d (%d built / %d reviewed / %d tested)" % (len(st), st.count("built"), st.count("reviewed"),
                                                                 st.count("tested")))
    limit = months_before(today(), months)
    old = [(f, d) for f in cur.files for _, d in [status_of(f)] if d and d < limit]
    unread = [f for f in cur.files if status_of(f)[1] is None]
    print("older than %d months (status before %s): %s" % (months, limit.isoformat(), "none" if not old else len(old)))
    for f, d in old:
        print("  %s  %s" % (f.label(), f.get("status")))
    if unread:
        print("status cannot be read (run python3 scripts/us_path.py check): %s" % ", ".join(f.label() for f in unread))
    return 0


def cmd_mark(cur, ref, state, by):
    f = cur.by_ref(ref)
    if not f:
        print("no curriculum file '%s': give a card or role id, DOMAIN/TRACK, a domain, or a path" % ref)
        return 1
    mine = [(w, m) for w, m in check_all(cur) if w == f.label() or w.startswith(f.label() + ":")]
    if mine:
        print("%s does not pass check; fix it first:" % f.label())
        for where, msg in mine:
            print("ERROR %s %s" % (where, msg))
        return 1
    value = "%s %s%s" % (state, today().isoformat(), " by " + by if by else "")
    ln = f.key_line("status")
    old = f.text
    lines = old.split("\n")
    lines[ln - 1] = "status: " + value
    with open(f.path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))
    again = Curriculum()
    mine = [(w, m) for w, m in check_all(again) if w == f.label() or w.startswith(f.label() + ":")]
    if mine:
        with open(f.path, "w", encoding="utf-8") as out:
            out.write(old)
        print("%s would not pass check with the new status line; left as it was:" % f.label())
        for where, msg in mine:
            print("ERROR %s %s" % (where, msg))
        return 1
    print("%s: status: %s" % (f.label(), value))
    return 0

# ---------------------------------------------------------------- spine, steps, words


SPINE_HEAD = ("Outline for the plan (%d steps from %d cards). Plan for the learner's goal and in the learner's own "
              "setting; group steps into chapters; account for every step with from:, held: or later:.")
NOTES_HEAD = ("From the curriculum: checked notes for this chapter's steps. They are a reference, not the chapter's "
              "outline. Build the chapter on ONE real problem or case from this book's setting, carried from the first "
              "attempt to finished, checked work; go deep on the deep step (prove its claim, walk one case by hand) and "
              "let the other steps serve it. Take from the notes the order, the question the reader must end up able to "
              "answer (Need), the experiment worth staging (Show), what goes wrong, and the beliefs to teach against. A "
              "fact or number here was run or sourced: keep it as written, or replace it only with output this book's "
              "own run pastes. Never state a result, a count, or a comparison of two numbers that you did not run or "
              "work out on the page. Try tasks are the least practice: the chapter's practice climbs past them to a "
              "problem the reader has not met in the chapter and solves alone. A word \"met in passing\" is glossed "
              "once, not taught. None of this wording is copied:")

def read_ref(cur, ref, need_steps=False):
    """(id, steps or None) of 'CARD' or 'CARD:STEPS', or a one-line error message (a string)."""
    ident, sep, spec = ref.partition(":")
    if ident not in cur.cards:
        if ident in cur.planned:
            return ident, "planned"
        return "no card '%s'; try: python3 scripts/us_path.py find %s" % (ident, ident.replace("-", " "))
    if need_steps and not sep:
        return "give the steps: %s:STEPS, such as %s:1-3 or %s:2,5" % (ident, ident, ident)
    if not sep:
        return ident, None
    steps = parse_steps(spec)
    if not steps:
        return "steps '%s' of %s cannot be read; write them like 4-8 or 1,3,5-6" % (spec, ident)
    have = len(card_steps(cur.cards[ident]))
    gone = [n for n in steps if not 1 <= n <= have]
    if gone:
        return "%s has steps 1 to %d; step %s does not exist" % (ident, have, show_steps(gone))
    return ident, steps


def picked(f, steps):
    """The card's steps, only those numbered in steps (all when steps is None)."""
    return [s for s in card_steps(f) if steps is None or s[0] in steps]


def keeps(tags, steps, untagged_ok):
    """True when an item tagged `tags` belongs to these steps."""
    if tags is None:
        return untagged_ok
    return steps is None or bool(set(tags) & set(steps))


def project_text(f):
    """(before, project) of "Practice and project": the text split where `Project:` begins."""
    text = " ".join(t.strip() for t in part_lines(f, "Practice and project"))
    at = text.find("Project:")
    return (text, "") if at < 0 else (text[:at].strip(), text[at:].strip())


def card_head(f, count):
    needs = f.get("needs") or "none"
    return "## %s: %s (kind %s; needs: %s; %d steps)" % (f.id, f.title, f.get("kind") or "?", needs, count)


def cmd_spine(cur, refs, tmap=None):
    found = []
    for ref in refs:
        got = read_ref(cur, ref)
        if isinstance(got, str):
            print(got)
            return 2
        found.append(got)
    cards = [(i, s) for i, s in found if s != "planned"]
    total = sum(len(picked(cur.cards[i], s)) for i, s in cards)
    hours = {i: card_hours(cur, i, s, tmap) for i, s in cards}
    known = sum(h for h, _ in hours.values() if h is not None)
    unknown = [i for i, s in found if s == "planned" or hours[i][0] is None]
    print(SPINE_HEAD % (total, len(cards)) + " All of it at full depth is about %d hours%s: fit the learner's budget "
          "by leaving depth for later, never a card the goal names." % (
              known, " (left out, no hours known: %s)" % ", ".join(unknown) if unknown else ""))
    for ident, steps in found:
        print("")
        if steps == "planned":
            print("## %s: no card yet (a planned subject of a track map); plan its steps from the learner's goal and "
                  "sources you read" % ident)
            continue
        f = cur.cards[ident]
        every = card_steps(f)
        print(card_head(f, len(every)))
        if hours[ident][0] is not None:
            print("About %d hours at full depth (track %s)." % hours[ident])
        print("Promise: " + " ".join(part_lines(f, "Promise")))
        print("The one idea: " + " ".join(t.strip() for t in part_lines(f, "The one idea")))
        print("In production:")
        print("\n".join(part_lines(f, "In production")))
        print("Teaching order%s:" % ("" if steps is None else " (steps %s of %d)" % (show_steps(steps), len(every))))
        print("\n".join(l for _, _, lines in picked(f, steps) for l in lines))
        print("Go deep, leave for later:")
        print("\n".join(part_lines(f, "Go deep, leave for later")))
        print("Mastery ladder:")
        print("\n".join(part_lines(f, "Mastery ladder")))
        before, project = project_text(f)
        print(project or "Practice and project: " + before)
    return 0


def card_hours(cur, ident, steps, tmap=None):
    """(hours, 'domain/track') from the Hours cell of track map tmap when it lists the card with a number, else of
    the first track map that does, scaled by the share of its steps requested and rounded; (None, None) when no
    map gives a number."""
    rows = cur.map_rows(ident)
    for m, _, c in [r for r in rows if r[0] is tmap] + [r for r in rows if r[0] is not tmap]:
        if len(c) > 5 and re.fullmatch(r"\d+", c[5].strip()):
            every = len(card_steps(cur.cards[ident])) or 1
            share = 1.0 if steps is None else len(steps) / every
            return int(int(c[5]) * share + 0.5), m.ref()
    return None, None


def chapter_notes(refs, cur=None):
    """The lines a chapter's writer is handed for refs [(card id, steps or None)], step by step in lesson order:
    the step line (deep steps marked), then its Need, Show, Explain, Picture, what goes wrong, wrong beliefs, the
    kind's part and believable numbers tagged to it, its owned and met words and its Try; after the steps, once,
    the untagged items, Never omit and Practice. An item tagged with several of the steps goes under the first."""
    cur = cur or Curriculum()
    out = []
    for ident, steps in refs:
        f = cur.cards.get(ident)
        if f is None:
            out.append("%s: no card in the curriculum" % ident)
            continue
        every = card_steps(f)
        mine = picked(f, steps)
        nums = [n for n, _, _ in mine]
        blocks, deep, kpart = step_notes(f)[0], deep_steps(f) or [], kind_part(f)

        def home(tags):
            return next((n for n in nums if n in tags), None) if tags else None
        out.append("%s, step%s %s of %d" % (ident, "" if len(nums) == 1 else "s", show_steps(nums), len(every)))
        for n, _, lines in mine:
            lines = list(lines)
            if n in deep:
                lines[-1] += " (a deep step: give it the chapter's best pages)"
            out += lines
            notes = blocks.get(n, {}).get("notes", {})
            out += ["  %s: %s" % (lab, notes[lab][1]) for lab in ("Need", "Show", "Explain", "Picture")
                    if notes.get(lab, [0, ""])[1]]
            for label, name in (("Goes wrong", "Failures to diagnose"), ("Teach against", "Wrong beliefs"),
                                (kpart, kpart), ("Believable numbers", "Believable numbers")):
                items = [t for _, tags, t, _ in tagged_items(f, name) if home(tags) == n] if name else []
                if items:
                    out.append("  %s:" % label)
                    out += ["  - " + t for t in items]
            words = [w for _, tags, ws, _ in word_groups(f) if home(tags) == n for w in ws]
            if [w for w in words if not is_met(w)]:
                out.append("  Words to own: " + ", ".join(w for w in words if not is_met(w)))
            if [w for w in words if is_met(w)]:
                out.append("  Met in passing: " + ", ".join(bare(w) for w in words if is_met(w)))
            if notes.get("Try", [0, ""])[1]:
                out.append("  Try: " + notes["Try"][1])
        for label, name, tagged in ((kpart, kpart, False), ("Believable numbers", "Believable numbers", False),
                                    ("Never omit", "Never omit", True)):
            items = [t for _, tags, t, _ in tagged_items(f, name) if tags is None or (tagged and home(tags))] \
                if name else []
            if items:
                out.append(label + ":")
                out += ["- " + t for t in items]
        before, _ = project_text(f)
        if before:
            out.append("Practice: " + before)
    return out


def cmd_steps(cur, refs):
    found = []
    for ref in refs:
        got = read_ref(cur, ref, need_steps=True)
        if isinstance(got, str) or got[1] == "planned":
            print(got if isinstance(got, str) else "%s is planned: it has no card yet, so no steps" % got[0])
            return 2
        found.append(got)
    print("\n".join(chapter_notes(found, cur)))
    return 0


def cmd_goal(cur, ref, pick):
    """A goal block of a track map, the `track:` line for the plan, then the spine of its Steps; no pick: the list."""
    f = cur.find_map(ref)
    if not f:
        print("no track map '%s'; tracks: %s" % (ref, ", ".join(m.ref() for m in cur.maps) or "none yet"))
        return 1
    blocks = goal_blocks(f)
    if not blocks:
        print("%s still has its Goals in the old form (a list), with no goal blocks; its Goals:" % f.ref())
        print("\n".join(part_lines(f, "Goals")))
        return 0
    if not pick:
        for k, b in enumerate(blocks, 1):
            print("%d  %s" % (k, b["title"]))
        return 0
    if len(pick) == 1 and pick[0].isdigit():
        k = int(pick[0])
        if not 1 <= k <= len(blocks):
            print("%s has goals 1 to %d" % (f.ref(), len(blocks)))
            return 2
        block = blocks[k - 1]
    else:
        want = set(words(" ".join(pick)))
        scored = sorted(((len(want & set(words(b["title"]))), -k, b) for k, b in enumerate(blocks)),
                        key=lambda x: (x[0], x[1]), reverse=True)
        if not scored or scored[0][0] == 0:
            print("no goal of %s matches '%s'; goals: %s" % (f.ref(), " ".join(pick),
                                                             "; ".join(b["title"] for b in blocks)))
            return 2
        block = scored[0][2]
    print("\n".join(block["lines"]))
    refs = card_refs(block["notes"].get("Steps", [0, ""])[1])[0]
    rows = [k for k, (_, c) in enumerate([r for r in f.rows() if len(r[1]) > 1], 1)
            if any(subject_of(c[1])[0] == i for i, _ in refs)]
    print("\ntrack: %s %s" % (f.ref(), show_steps(rows).replace(" ", "")) if rows else "\ntrack: %s" % f.ref())
    print("")
    return cmd_spine(cur, ["%s:%s" % (i, ",".join(map(str, st))) if st else i for i, st in refs], f)


def cmd_words(cur, refs):
    out = []
    for ref in refs:
        if ref in cur.cards:
            ids = [ref]
        elif cur.find_map(ref):
            ids = [subject_of(c[1])[0] for _, c in cur.find_map(ref).rows() if len(c) > 1]
        elif ref in cur.planned:
            ids = [ref]
        else:
            print("no card or track '%s'; try: python3 scripts/us_path.py find %s" % (ref, ref.replace("-", " ")))
            return 2
        for ident in ids:
            f = cur.cards.get(ident)
            out.append("%s: %s" % (ident, ", ".join(w for _, _, ws, _ in word_groups(f) for w in ws)
                                   if f else "(planned: no card yet)"))
    print("\n".join(out))
    return 0

# ---------------------------------------------------------------- ready

WEIGHTS = {"essential": 3, "desirable": 2, "specialist": 1}
HONEST = 'This counts what your books and practice records show. The "Proved by" task of each line is the real test.'


def shelf():
    """[(book, plan)] of every book on the shelf that has a PLAN.md, in name order."""
    import us_bookfmt as bf
    return [(b, p) for b in bf.list_books() for p in [bf.load_plan(b)] if p is not None]


def expand(cur, ident, steps):
    """The step numbers an entry names: all of the card's when steps is None."""
    f = cur.cards.get(ident)
    every = [n for n, _, _ in card_steps(f)] if f else []
    return every if steps is None else [n for n in steps if n in every]


def chapter_evidence(book, plan, store):
    """{(card, step): best evidence} from the chapters of one book whose from: line names the step."""
    import us_bookfmt as bf
    import us_plan
    import us_practice
    status, out = bf.read_status(book), {}
    for ch in plan.chapters:
        if not ch.from_refs:
            continue
        score = 0.0
        if us_plan.chapter_state(book, ch, status)[0] in ("written", "reviewed"):
            keys = [q["key"] for q in us_practice.book_questions(book, ch.number)]
            right = sum(1 for k in keys if (store.get(k) or {}).get("history") and store[k]["history"][-1].endswith(" y"))
            score = 0.25 + 0.75 * (right / len(keys) if keys else 0)
        for ident, steps in ch.from_refs:
            for n in steps if steps is not None else [None]:
                key = (ident, n)
                out[key] = max(out.get(key, 0.0), score)
    return out


def readiness(cur, books, have, ident, level):
    """(ready, declared share, weakest (step, words) or None) of one subject with a card."""
    import us_practice
    store = us_practice.load_store()
    every = card_steps(cur.cards[ident])
    held = set()
    for _, plan in books:
        for entry in plan.held:
            if entry[1] == ident:
                held |= set(expand(cur, ident, entry[2]))
    if have.get(ident, 0) >= level:
        held = {n for n, _, _ in every}
    evidence = {}
    for book, plan in books:
        for (card, n), score in chapter_evidence(book, plan, store).items():
            if card == ident:
                for k in ([n] if n is not None else [s for s, _, _ in every]):
                    evidence[k] = max(evidence.get(k, 0.0), score)
    scores = [(1.0 if n in held else evidence.get(n, 0.0), n, lines) for n, _, lines in every]
    ready = sum(s for s, _, _ in scores) / len(scores) if scores else 0.0
    open_ = [(s, n, lines) for s, n, lines in scores if n not in held]
    weakest = min(open_, key=lambda x: (x[0], x[1])) if open_ else None
    words = re.split(r"[:.;]", step_text(weakest[2]))[0].strip() if weakest else ""
    return ready, len(held) / len(scores) if scores else 0.0, (weakest[1], words[:48]) if weakest else None


def next_order(cur, rows):
    """The essential and desirable lines not yet ready, what the learner can start now first: a line whose needs
    (any one alternative of each entry) include role lines none of which is half ready waits behind them; then
    essential before desirable, lowest readiness, the role table's order."""
    ready = {r[0]: r[3] for r in rows}
    depth, busy = {}, set()

    def wait(sid):
        if sid in depth:
            return depth[sid]
        if sid in busy or sid not in cur.cards:
            return 0
        busy.add(sid)
        d = 0
        for entry in need_entries(cur.cards[sid].get("needs")):
            mine = [a for a in entry if a in ready]
            if mine and not any(ready[a] >= 0.5 for a in mine):
                d = max(d, 1 + min(wait(a) for a in mine))
        busy.discard(sid)
        depth[sid] = d
        return d

    rank = {"essential": 0, "desirable": 1}
    todo = [(k, r) for k, r in enumerate(rows) if r[2] in rank and r[3] < 1]
    return [r for k, r in sorted(todo, key=lambda kr: (wait(kr[1][0]), rank[kr[1][2]], kr[1][3], kr[0]))]


def start_now(cur, rows):
    """Up to three subjects with a card to take next: the essential ones that can start now (nothing they need
    among the role's lines is short of half ready), lowest readiness first, then table order; fewer than three:
    desirable ones that can start now. When none can start: the waiting ones, in next_order."""
    order = [r for r in next_order(cur, rows) if r[4] is not None]
    ready = {r[0]: r[3] for r in rows}

    def free(sid):
        return all(not [a for a in e if a in ready] or any(ready[a] >= 0.5 for a in e if a in ready)
                   for e in need_entries(cur.cards[sid].get("needs")))

    pick = []
    for cls in ("essential", "desirable"):
        if len(pick) < 3:
            pick += sorted([(r[3], k, r) for k, r in enumerate(rows) if r[2] == cls and r[4] is not None and r[3] < 1
                            and free(r[0])], key=lambda x: (x[0], x[1]))[:3 - len(pick)]
    return [r for _, _, r in pick] or order


def needed_first(cur, listed, needers, have):
    """'Needed first, though not on this role's list: x (for a, b), ...', or '' when every need of the needers
    (direct needs: only; an entry is met by any alternative on the list or in --have) is met."""
    found = {}
    for sid in needers:
        f = cur.cards.get(sid)
        for entry in need_entries(f.get("needs") if f else None):
            if not any(a in listed or a in have for a in entry):
                found.setdefault(entry[0], []).append(sid)
    if not found:
        return ""
    return "Needed first, though not on this role's list: " + ", ".join(
        "%s (for %s)" % (k, ", ".join(v)) for k, v in found.items())


def cmd_ready(cur, ident, have, everything):
    f = cur.roles.get(ident)
    if not f:
        print("no role '%s'; roles: %s" % (ident, ", ".join(sorted(cur.roles)) or "none yet"))
        return 1
    books = shelf()
    rows = []
    for _, c in f.rows():
        if len(c) < 3:
            continue
        sid, planned = subject_of(c[0])
        cls = c[2].strip().lower()
        if cls not in WEIGHTS or (cls == "specialist" and not everything):
            continue
        need = re.match(r"\s*(\d)", c[1])
        level = int(need.group(1)) if need else 1
        if planned or sid not in cur.cards:
            rows.append((sid, c[1].strip(), cls, 0.0, None, None))
        else:
            rows.append((sid, c[1].strip(), cls) + readiness(cur, books, have, sid, level))
    rows = [r for cls in WEIGHTS for r in rows if r[2] == cls]          # essential, desirable, specialist

    def mean(classes):
        picked_rows = [r for r in rows if r[2] in classes]
        weight = sum(WEIGHTS[r[2]] for r in picked_rows)
        return sum(WEIGHTS[r[2]] * r[3] for r in picked_rows) / weight if weight else 0.0

    print("%s: %d%% ready (%s); %d book%s on the shelf" % (
        ident, round(100 * mean(WEIGHTS)), "essential lines weigh 3, desirable 2, specialist 1" if everything
        else "essential lines weigh 3, desirable 2; specialist lines with --all", len(books),
        "" if len(books) == 1 else "s"))
    width = max([len(r[0]) for r in rows] + [1])
    for sid, level, cls, ready, declared, weakest in rows:
        if declared is None:
            print("%-*s  needs %s  %s  0%% ready  no card yet" % (width, sid, level, cls))
            continue
        print("%-*s  needs %s  %s  %d%% ready (%d%% declared)  weakest step: %s" % (
            width, sid, level, cls, round(100 * ready), round(100 * declared),
            "%d %s" % weakest if weakest else "none (all declared)"))
    print("Essential: %d%%   Essential and desirable: %d%%" % (round(100 * mean(["essential"])),
                                                              round(100 * mean(["essential", "desirable"]))))
    order = start_now(cur, rows)
    first = needed_first(cur, [subject_of(c[0])[0] for _, c in f.rows() if c], [r[0] for r in rows], have)
    if first:
        print(first)
    print("Next: " + (", ".join("%s (%d%%)" % (r[0], round(100 * r[3])) for r in order[:3]) or "nothing left"))
    print(HONEST)
    return 0

# ---------------------------------------------------------------- main


USAGE = ("usage: us_path.py find WORDS | card ID | map DOMAIN/TRACK | index [DOMAIN] | spine CARD[:STEPS] ..."
         " | goal DOMAIN/TRACK [N|WORDS] | steps CARD:STEPS ... | words CARD|TRACK ... | role ROLE [--have \"id:level, ...\"]"
         " | ready ROLE [--have \"id:level, ...\"] [--all] | check | status [--stale MONTHS]"
         " | mark ID|PATH reviewed|tested [--by \"TEXT\"]")


def option(argv, name):
    """(value, rest) of `--name VALUE`; value is False when the option has no value, None when absent."""
    if name not in argv:
        return None, argv
    i = argv.index(name)
    if i + 1 == len(argv) or argv[i + 1].startswith("--"):
        return False, argv
    return argv[i + 1], argv[:i] + argv[i + 2:]


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2
    cmd, rest = argv[0], argv[1:]
    values = {}
    for name in ("--have", "--stale", "--by", "--track"):
        values[name], rest = option(rest, name)
        if values[name] is False:
            print("%s needs a value" % name)
            return 2
    everything = "--all" in rest
    rest = [a for a in rest if a != "--all"]
    if everything and cmd != "ready":
        print("--all does not go with %s; %s" % (cmd, USAGE))
        return 2
    allowed = {"role": ("--have",), "ready": ("--have",), "status": ("--stale",), "mark": ("--by",),
               "spine": ("--track",)}
    for name, value in values.items():
        if value is not None and name not in allowed.get(cmd, ()):
            print("%s does not go with %s; %s" % (name, cmd, USAGE))
            return 2
    if [a for a in rest if a.startswith("--")]:
        print("unknown option %s; %s" % (" ".join(a for a in rest if a.startswith("--")), USAGE))
        return 2
    cur = Curriculum()
    if cmd == "find" and rest:
        return cmd_find(cur, " ".join(rest))
    if cmd == "card" and len(rest) == 1:
        f = cur.cards.get(rest[0])
        if not f:
            print("no card '%s'; try: python3 scripts/us_path.py find %s" % (rest[0], rest[0]))
            return 1
        return show_card(cur, f)
    if cmd == "map" and len(rest) == 1:
        f = cur.find_map(rest[0])
        if not f:
            print("no track map '%s'; tracks: %s" % (rest[0], ", ".join(m.ref() for m in cur.maps) or "none yet"))
            return 1
        show(f)
        return 0
    if cmd == "index" and len(rest) <= 1:
        return cmd_index(cur, rest[0] if rest else None)
    if cmd in ("role", "ready") and len(rest) == 1:
        have = parse_have(values["--have"]) if values["--have"] else {}
        if have is None:
            print('--have must read "id:level, id:level" with levels 1 to 5, for example "git:3, python:2"')
            return 2
        return cmd_role(cur, rest[0], have) if cmd == "role" else cmd_ready(cur, rest[0], have, everything)
    if cmd == "spine" and rest:
        tmap = cur.find_map(values["--track"]) if values["--track"] else None
        if values["--track"] and tmap is None:
            print("no track map '%s'; tracks: %s" % (values["--track"], ", ".join(m.ref() for m in cur.maps) or "none yet"))
            return 1
        return cmd_spine(cur, rest, tmap)
    if cmd == "steps" and rest:
        return cmd_steps(cur, rest)
    if cmd == "goal" and rest:
        return cmd_goal(cur, rest[0], rest[1:])
    if cmd == "words" and rest:
        return cmd_words(cur, rest)
    if cmd == "check" and not rest:
        return cmd_check(cur)
    if cmd == "status" and not rest:
        stale = values["--stale"]
        if stale is not None and not stale.isdigit():
            print("--stale needs a number of months")
            return 2
        return cmd_status(cur, int(stale) if stale else 12)
    if cmd == "mark" and len(rest) == 2 and rest[1] in ("reviewed", "tested"):
        by = values["--by"]
        if by is not None and (not by.strip() or "\n" in by):
            print("--by needs a name on one line")
            return 2
        return cmd_mark(cur, rest[0], rest[1], by.strip() if by else None)
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
