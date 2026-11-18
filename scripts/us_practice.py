#!/usr/bin/env python3
"""Practise with no AI: Check yourself questions and practice exercises from written chapters.

    python3 scripts/us_practice.py [BOOK] [--chapter N] [--count K] [--due]
    python3 scripts/us_practice.py --stats     your record in 25 lines at most: boxes per chapter, weak
                                               spots, each practised section (times, box, next due)
    python3 scripts/us_practice.py --plain [--answers]      print the next K questions, no marking
    python3 scripts/us_practice.py record BOOK N.M right|partly|no [--sure] [--note TEXT]
                                               log one answer given in a lesson or check: practice.json,
                                               levels.yaml (in progress, next date), weaknesses.md

One question at a time: read it, answer it on paper or in your head, press Enter, compare, then
say honestly whether you got it. Right moves the question up a box and further into the future
(box 1 tomorrow, then 3, 7, 14, 30 days); wrong sends it back to box 1 for tomorrow; partly
keeps its box and brings it back tomorrow. Each run asks what is due today, oldest first, then
new questions in book order. No BOOK: every book. --due: only what is due.
Everything is kept in <private>/practice.json; nothing is written into the book.
--answer-file PATH reads the marks (y, p, n or q, one per line) instead of the keyboard.
"""
import datetime
import hashlib
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
import us_plan  # noqa: E402

DAYS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
WIDTH = 80
START = re.compile(r"^\s*(\d+[.)]\s|\*\*([A-Za-z]+\s+)?\d+[.:)]?\*\*|\*\*(Exercise|Question)\b|#{3,6}\s+(Exercise|Question)\b)")


def today():
    """Today's date; UNDERSTUDY_TODAY=YYYY-MM-DD fakes it for tests."""
    return datetime.date.fromisoformat(os.environ.get("UNDERSTUDY_TODAY") or datetime.date.today().isoformat())


def store_path():
    return os.path.join(bf.private_dir(), "practice.json")


def load_store():
    path = store_path()
    return json.loads(bf.read_text(path)) if os.path.exists(path) else {}


def save_store(data):
    bf.write_text(store_path(), json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- finding questions


def section_questions(lines, free_from=0):
    """(question, answer) pairs: each <details> outside code fences, with the question above it.

    Before line free_from (the Check yourself line) only numbered questions and exercises count."""
    pairs, fence, start, i = [], None, 0, 0
    while i < len(lines):
        s = lines[i].strip()
        if fence:
            fence = None if bf.fence_close(lines[i], fence) else fence
        elif bf.FENCE_OPEN.match(lines[i]):
            fence = bf.FENCE_OPEN.match(lines[i]).group(1)
        elif s.startswith("<details>"):
            end, depth = i, 0
            for end in range(i, len(lines)):
                depth += lines[end].count("<details>") - lines[end].count("</details>")
                if depth <= 0:
                    break
            chunk = lines[start:i]
            fence_at = in_fence(chunk)
            starts = [k for k, l in enumerate(chunk) if START.match(l) and not fence_at[k]]
            question = "\n".join(chunk[starts[-1]:] if starts else chunk).strip()
            answer = "\n".join(l for l in lines[i + 1:end] if not re.match(r"\s*<summary>.*</summary>\s*$", l))
            if question and (starts or i >= free_from):
                pairs.append((question, answer.strip()))
            start = i = end + 1
            continue
        i += 1
    return pairs


def in_fence(lines):
    """For each line, True if it is inside (or opens/closes) a code fence."""
    out, fence = [], None
    for line in lines:
        if fence:
            out.append(True)
            fence = None if bf.fence_close(line, fence) else fence
        else:
            m = bf.FENCE_OPEN.match(line)
            fence = m.group(1) if m else None
            out.append(bool(m))
    return out


def book_questions(book, chapter=None):
    """Every question of the book's written chapters, in book order, as dicts."""
    plan = bf.load_plan(book)
    if plan is None:
        return []
    status, slug, out = bf.read_status(book), os.path.basename(book.rstrip(os.sep)), []
    for ch in plan.chapters:
        if chapter and ch.number != chapter:
            continue
        if us_plan.chapter_state(book, ch, status)[0] not in ("written", "reviewed"):
            continue
        doc = bf.parse_chapter(bf.read_text(bf.chapter_path(book, ch.number)))
        for sec in doc.sections:
            free = sec.check_line - sec.line if sec.check_line else len(doc.lines)
            for n, (q, a) in enumerate(section_questions(doc.lines[sec.line:sec.end], free), 1):
                digest = hashlib.sha1(" ".join(q.split()).encode()).hexdigest()[:8]
                out.append({"key": "%s/%s/q%d/%s" % (slug, sec.number, n, digest), "book": slug,
                            "book_title": plan.title or slug, "section": sec.number, "title": sec.title,
                            "chapter": ch.number, "question": q, "answer": a})
    return out


def all_questions(book_arg=None, chapter=None):
    books = [bf.resolve_book(book_arg)] if book_arg else bf.list_books()
    return [q for b in books for q in book_questions(b, chapter)]


def pick(questions, store, count, due_only=False):
    """Due questions (oldest due first), then new ones in book order, at most count."""
    now = today().isoformat()
    due = sorted((q for q in questions if q["key"] in store and store[q["key"]]["due"] <= now),
                 key=lambda q: store[q["key"]]["due"])
    new = [] if due_only else [q for q in questions if q["key"] not in store]
    return (due + new)[:count]

# ---------------------------------------------------------------- showing


def render(text, width=WIDTH):
    """Markdown as terminal text: markers and HTML gone, prose wrapped, code as it is."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out, para, fence = [], [], None

    def flush():
        if para:
            first = para[0]
            m = re.match(r"(\s*(?:[-*]|\d+[.)])\s+)", first)
            indent = " " * len(m.group(1)) if m else ""
            out.extend(textwrap.wrap(" ".join(p.strip() for p in para).replace("**", ""), width,
                                     subsequent_indent=indent, break_on_hyphens=False) or [""])
            para.clear()
    for line in text.splitlines():
        if fence:
            out.append(line)
            fence = None if bf.fence_close(line, fence) else fence
            continue
        m = bf.FENCE_OPEN.match(line)
        s = line.strip()
        if m or not s or s.startswith(("|", "#", "<")) or re.match(r"([-*]|\d+[.)])\s", s):
            flush()
            if m:
                fence = m.group(1)
                out.append(line)
            elif s.startswith("<"):
                continue
            elif s.startswith(("|", "#")):
                out.append(line.replace("**", ""))
            elif s:
                para.append(line)
            elif out and out[-1]:
                out.append("")
            continue
        para.append(line)
    flush()
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


def header(q, i, total, store):
    rec = store.get(q["key"])
    tag = "new" if rec is None else "box %d" % rec["box"]
    return "-" * WIDTH + "\n" + textwrap.shorten("[%d/%d] %s · §%s %s · %s" % (
        i, total, q["book_title"], q["section"], q["title"], tag), WIDTH, placeholder="...") + "\n"

# ---------------------------------------------------------------- marking


def mark(store, q, answer):
    """Record y, p or n for a question and move it between boxes."""
    rec = store.setdefault(q["key"], {"book": q["book"], "section": q["section"], "title": q["title"],
                                      "question": textwrap.shorten(q["question"], 70), "box": 1,
                                      "due": "", "history": []})
    now = today()
    if answer == "y":
        rec["box"] = min(rec["box"] + 1, 5) if rec["history"] else 2
    elif answer == "n":
        rec["box"] = 1
    rec["due"] = (now + datetime.timedelta(days=DAYS[rec["box"]] if answer == "y" else 1)).isoformat()
    rec["history"].append("%s %s %s" % (now.isoformat(), datetime.datetime.now().strftime("%H:%M:%S"), answer))


def prune(store, questions):
    """Drop records of questions whose text changed: an edited question starts fresh."""
    current = {q["key"] for q in questions}
    slots = {k.rsplit("/", 1)[0] for k in current}
    stale = [k for k in store if k not in current and k.rsplit("/", 1)[0] in slots]
    for key in stale:
        del store[key]
    if stale:
        save_store(store)


def session(chosen, store, answers):
    """Ask each question; returns how many of y, p, n were given."""
    got = {"y": 0, "p": 0, "n": 0}
    for i, q in enumerate(chosen, 1):
        print(header(q, i, len(chosen), store))
        print(render(q["question"]) + "\n")
        try:
            if answers is None:
                input("[Enter] to see the answer ")
                print()
            print("Answer:\n" + render(q["answer"]) + "\n")
            reply = ""
            while reply not in ("y", "p", "n", "q"):
                if answers is None:
                    reply = input("Did you get it? (y)es (p)artly (n)o (q)uit ").strip().lower()[:1]
                else:
                    reply = answers.pop(0) if answers else "q"
                    print("Did you get it? (y)es (p)artly (n)o (q)uit " + reply)
        except (EOFError, KeyboardInterrupt):
            reply = "q"
        if reply == "q":
            break
        mark(store, q, reply)
        save_store(store)  # after every answer: a cut-off session loses nothing
        got[reply] += 1
    return got

# ---------------------------------------------------------------- stats


def weak_spots(store, n=3):
    """The n sections with the most misses (n marks) as ((book, section, title), misses)."""
    misses = {}
    for rec in store.values():
        k = sum(1 for h in rec["history"] if h.endswith(" n"))
        if k:
            spot = (rec["book"], rec["section"], rec["title"])
            misses[spot] = misses.get(spot, 0) + k
    return sorted(misses.items(), key=lambda kv: -kv[1])[:n]


def stats(store, cap=25):
    """Per chapter: boxes and percent right; then weak spots; then practised sections (times practised,
    lowest box, next due date), soonest due first, all in at most cap lines."""
    since = (today() - datetime.timedelta(days=14)).isoformat()
    rows, secs = {}, {}
    for rec in store.values():
        row = rows.setdefault((rec["book"], int(rec["section"].split(".")[0])), [0, [0] * 5, 0, 0])
        row[0] += 1
        row[1][rec["box"] - 1] += 1
        recent = [h for h in rec["history"] if h[:10] >= since]
        row[2] += sum(1 for h in recent if h.endswith(" y"))
        row[3] += len(recent)
        sec = secs.setdefault((rec["book"], rec["section"], rec["title"]), [0, 5, "9999"])
        sec[0] += len(rec["history"])
        sec[1], sec[2] = min(sec[1], rec["box"]), min(sec[2], rec["due"])
    out = ["%-20s %4s %5s %4s %4s %4s %4s %4s %9s" % ("book", "ch", "seen", "box1", "box2", "box3", "box4", "box5", "right 14d")]
    for (book, ch), (seen, boxes, right, total) in sorted(rows.items()):
        pct = "%d%%" % round(100 * right / total) if total else "-"
        out.append("%-20s %4d %5d %4d %4d %4d %4d %4d %9s" % ((book[:20], ch, seen) + tuple(boxes) + (pct,)))
    if not rows:
        out.append("nothing practised yet")
    spots = weak_spots(store)
    if spots:
        out.append("\nweak spots:")
        for (book, sec, title), k in spots:
            out.append("  %s (missed %d)" % (textwrap.shorten("%s §%s %s" % (book, sec, title), WIDTH - 16, placeholder="..."), k))
    done = sorted((v[2], k[0], bf.section_key(k[1]), k, v) for k, v in secs.items() if v[0])
    room = max(cap - "\n".join(out).count("\n") - 4, 1)  # header (2 lines), rows, "... more"
    if done:
        out.append("\nsections practised (times, lowest box, next due):")
        for _, _, _, (book, sec, title), (times, box, due) in done[:room]:
            out.append("  %-52s %3dx  box %d  due %s" % (textwrap.shorten("%s §%s %s" % (book, sec, title), 52, placeholder="..."),
                                                         times, box, due))
        if len(done) > room:
            out.append("  ... %d more" % (len(done) - room))
    print("\n".join(out))
    return 0


def option(args, name, default=None):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default

# ---------------------------------------------------------------- answers given in a lesson


MARKS = {"right": "y", "partly": "p", "no": "n"}


def levels_line(slug, chapter, mark):
    """Make sure levels.yaml shows the chapter in progress with a `next` date; never lowers a level.

    Returns what was added or changed, in words ('' when nothing)."""
    path = os.path.join(bf.private_dir(), "levels.yaml")
    text = bf.read_text(path) if os.path.exists(path) else ""
    nxt = today() + datetime.timedelta(days=3 if mark == "y" else 2)
    key = "%s/%d" % (slug, chapter)
    m = re.search(r"(?m)^%s:.*$" % re.escape(key), text)
    if not m:
        line = "%s: {level: 1, state: in progress, checked: %s, next: %s}" % (key, today(), nxt)
        bf.write_text(path, text + ("\n" if text and not text.endswith("\n") else "") + line + "\n")
        return "levels.yaml: added the line `%s`" % line
    old = m.group(0)
    have = re.search(r"\bnext:\s*(\d{4}-\d\d-\d\d)", old)
    if have and (mark == "y" or have.group(1) <= nxt.isoformat()):
        return ""
    if have:
        new = old[:have.start(1)] + nxt.isoformat() + old[have.end(1):]
        said = "levels.yaml: %s next moved to %s" % (key, nxt)
    else:
        new = re.sub(r"\s*\}\s*$", ", next: %s}" % nxt, old) if old.rstrip().endswith("}") else old + "  # next: %s" % nxt
        said = "levels.yaml: added `next: %s` to %s" % (nxt, key)
    bf.write_text(path, text[:m.start()] + new + text[m.end():])
    return said


def record(argv):
    """us_practice.py record BOOK N.M right|partly|no [--sure] [--note TEXT]: log one answer given in a lesson."""
    note = option(argv, "--note", "")
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--note")]
    if len(args) != 3 or args[2] not in MARKS or not re.fullmatch(r"§?\d+\.\d+", args[1]):
        print("usage: python3 scripts/us_practice.py record BOOK N.M right|partly|no [--sure] [--note TEXT]")
        return 2
    book, number, word = bf.resolve_book(args[0]), args[1].lstrip("§"), args[2]
    plan = bf.load_plan(book)
    if plan is None:
        print("no plan at %s: give the book's name or folder" % book)
        return 1
    ch = plan.chapter(int(number.split(".")[0]))
    sec = next((s for s in ch.sections if s.number == number), None) if ch else None
    if sec is None:
        print("no section %s in the plan of %s: give a section number from PLAN.md" % (number, os.path.basename(book)))
        return 1
    slug, mark_ = os.path.basename(book.rstrip(os.sep)), MARKS[word]
    store = load_store()
    mark(store, {"key": "%s/%s/lesson" % (slug, number), "book": slug, "section": number, "title": sec.title,
                 "question": "answers given in a lesson or check"}, mark_)
    save_store(store)
    rec = store["%s/%s/lesson" % (slug, number)]
    said = ["recorded: %s §%s %s: %s (box %d, comes back %s)" % (slug, number, sec.title, word, rec["box"], rec["due"])]
    said.append(levels_line(slug, ch.number, mark_))
    if mark_ != "y":
        path = os.path.join(bf.private_dir(), "weaknesses.md")
        text = bf.read_text(path) if os.path.exists(path) else ""
        line = "- %s §%s %s (%s): %s%s%s" % (today(), number, sec.title, slug, word, ", sure" if "--sure" in argv else "",
                                             ": " + " ".join(note.split()) if note.strip() else "")
        if line not in text.splitlines():
            bf.write_text(path, text + ("\n" if text and not text.endswith("\n") else "") + line + "\n")
            said.append("weaknesses.md: added the line `%s`" % line)
    print("\n".join(s for s in said if s))
    import us_resume
    us_resume.main([book])
    return 0


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    if argv and argv[0] == "record":
        return record(argv[1:])
    store = load_store()
    if "--stats" in argv:
        return stats(store)
    valued = {"--chapter", "--count", "--answer-file"}
    rest = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in valued)]
    chapter = int(option(argv, "--chapter", 0))
    questions = all_questions(rest[0] if rest else None, chapter)
    if not questions:
        print("no questions yet: no written chapter has a Check yourself or practice section")
        return 1
    chosen = pick(questions, store, int(option(argv, "--count", 10)), "--due" in argv)
    if not chosen:
        print("nothing is due today. Come back tomorrow, or leave out --due for new questions.")
        return 0
    if "--plain" in argv:
        for i, q in enumerate(chosen, 1):
            print(header(q, i, len(chosen), store))
            print(render(q["question"]) + "\n")
            if "--answers" in argv:
                print("Answer:\n" + render(q["answer"]) + "\n")
        return 0
    path = option(argv, "--answer-file")
    answers = [l.strip().lower()[:1] for l in open(path, encoding="utf-8") if l.strip()] if path else None
    prune(store, questions)
    got = session(chosen, store, answers)
    print("-" * WIDTH + "\n%d right, %d partly, %d missed. Saved in %s" % (got["y"], got["p"], got["n"], store_path()))
    import us_resume
    us_resume.main(rest[:1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
