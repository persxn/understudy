#!/usr/bin/env python3
"""Practise with no AI: Check yourself questions, practice exercises and key-term cards from written chapters.

    python3 scripts/us_practice.py [BOOK] [--chapter N] [--count K | --minutes M] [--due]
    python3 scripts/us_practice.py --cards [BOOK] [--count K] [--due]   flashcards of the key terms
    python3 scripts/us_practice.py --stats     your record in 25 lines at most: boxes per chapter, weak
                                               spots, each practised section (times, box, next due), cards
    python3 scripts/us_practice.py --summary [BOOK]   what you know, in 15 lines (also private/learner.md)
    python3 scripts/us_practice.py --plain [--answers]      print the next K questions, no marking
    python3 scripts/us_practice.py record BOOK N.M right|partly|no [--sure] [--note TEXT]
                                   [--type TYPE] [--idea ID] [--wrong "NAME"]
                                               log one answer given in a lesson or check: practice.json,
                                               levels.yaml (in progress, next date), weaknesses.md
    python3 scripts/us_practice.py check BOOK N.M [--in FOLDER] [--answer-file PATH]
                                               test your own project against the section's model answers
                                               (check="COMMAND" blocks) and walk its checklists

One question at a time: read it, answer it on paper or in your head, press Enter, compare, then
say honestly whether you got it (add ! when you were sure: y! or n!). Right moves the question up a
box and further into the future (box 1 tomorrow, then 3, 7, 14, 30, 60 days; right and sure: two
boxes up); wrong sends it back to box 1 for tomorrow; partly keeps its box and brings it back
tomorrow. Each run asks what is due today, most urgent first (misses, a sure answer that was wrong,
days overdue, ideas later sections need), spread over books and sections, then new questions in book
order (at most 60% due when the newest chapter has new questions). No BOOK: every book. --due: only
what is due, questions and cards together. --minutes M: about M minutes (1.5 minutes a question).
Everything is kept in <private>/practice.json and learner.md; nothing is written into the book.
--answer-file PATH reads the marks (y, p, n or q, one per line; y! n! for sure) instead of the keyboard.
"""
import datetime
import hashlib
import json
import math
import os
import re
import shlex
import signal
import subprocess
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
import us_plan  # noqa: E402

DAYS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30, 6: 60}
TOP = max(DAYS)
WIDTH = 80
SHARE = 0.6             # most of a session one book, or due items with new material waiting, may take
MINUTES_EACH = 1.5
CHECK_TIMEOUT = 10
SUMMARY_LINES = 15
START = re.compile(r"^\s*(\d+[.)]\s|\*\*([A-Za-z]+\s+)?\d+([.:)]?\*\*|[.:)]\s)|\*\*(Exercise|Question|Task)\b|#{3,6}\s+(Exercise|Question|Task)\b)")


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


def slug_of(book):
    return os.path.basename(book.rstrip(os.sep))

# ---------------------------------------------------------------- finding questions


def section_questions(lines, free_from=0, with_lines=False):
    """(question, answer) pairs: each <details> outside code fences, with the question above it.

    Before line free_from (the Check yourself line) only numbered questions and exercises count.
    with_lines: (question, answer, index of the question's first line) triples."""
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
            listed = bf.checklist_rows(chunk)
            tagged = [k for k, l in enumerate(chunk) if not fence_at[k] and k and l.strip() and bf.Q_MARK.match(chunk[k - 1])]
            starts = tagged or [k for k, l in enumerate(chunk)
                                if not fence_at[k] and k not in listed and START.match(l)]
            # a q tag opens a question; numbered steps inside a tagged task are not new questions
            question = "\n".join(chunk[starts[-1]:] if starts else chunk).strip()
            answer = "\n".join(l for l in lines[i + 1:end] if not re.match(r"\s*<summary>.*</summary>\s*$", l))
            if question and (starts or i >= free_from):
                text = [k for k, l in enumerate(chunk) if l.strip() and not bf.Q_MARK.match(l)]
                first = start + (starts[-1] if starts else (text[0] if text else 0))
                pairs.append((question, answer.strip(), first) if with_lines else (question, answer.strip()))
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


def importance(plan):
    """Section number -> 0 to 2: 2 x min(later planned sections whose needs: name an idea it teaches, 5) / 5."""
    secs = [s for ch in plan.chapters for s in ch.sections]
    out = {}
    for i, s in enumerate(secs):
        later = sum(1 for t in secs[i + 1:] if set(t.needs) & set(s.teaches))
        out[s.number] = 2 * min(later, 5) / 5
    return out


def written_chapters(book, plan):
    status = bf.read_status(book)
    return [ch for ch in plan.chapters if us_plan.chapter_state(book, ch, status)[0] in ("written", "reviewed")]


def book_questions(book, chapter=None):
    """Every question of the book's written chapters, in book order, as dicts.

    Each has idea, type and wrong from the q tag on the line above its first line; with no tag, the
    first idea the section teaches (if any) and type 'unknown'."""
    plan = bf.load_plan(book)
    if plan is None:
        return []
    slug, out, weight = slug_of(book), [], importance(plan)
    planned = {s.number: s for ch in plan.chapters for s in ch.sections}
    for ch in written_chapters(book, plan):
        if chapter and ch.number != chapter:
            continue
        doc = bf.parse_chapter(bf.read_text(bf.chapter_path(book, ch.number)))
        for sec in doc.sections:
            free = sec.check_line - sec.line if sec.check_line else len(doc.lines)
            lines = doc.lines[sec.line:sec.end]
            psec = planned.get(sec.number)
            for n, (q, a, first) in enumerate(section_questions(lines, free, True), 1):
                digest = hashlib.sha1(" ".join(q.split()).encode()).hexdigest()[:8]
                tag = bf.parse_q(lines[first - 1]) if first > 0 else None
                fallback = psec.teaches[0] if psec and psec.teaches else ""
                tag = tag or {"idea": fallback, "type": "unknown", "wrong": ""}
                out.append({"key": "%s/%s/q%d/%s" % (slug, sec.number, n, digest), "book": slug,
                            "book_title": plan.title or slug, "section": sec.number, "title": sec.title,
                            "chapter": ch.number, "question": q, "answer": a, "idea": tag["idea"] or fallback,
                            "type": tag["type"] or "unknown", "wrong": tag["wrong"],
                            "importance": weight.get(sec.number, 0)})
    return out


def book_cards(book):
    """One card per key term of the written chapters: the term, section and defining sentence of KEYTERMS.md.
    A term with no definition gets no card."""
    import us_index
    plan = bf.load_plan(book)
    if plan is None:
        return []
    bk, slug, weight, out = us_index.BookIndex(book, os.path.dirname(book.rstrip(os.sep))), slug_of(book), importance(plan), []
    for ch in written_chapters(book, plan):
        for psec in ch.sections:
            for idea in psec.teaches:
                if idea not in bk.taught:
                    continue
                term, _, sentence = bk.term(idea)
                if not sentence:
                    continue
                out.append({"key": "card/%s/%s/%s" % (slug, psec.number, idea), "book": slug,
                            "book_title": plan.title or slug, "section": psec.number, "title": psec.title,
                            "chapter": ch.number, "question": "**%s**\n\nWhat does it mean? (key term from §%s %s)"
                            % (term, psec.number, psec.title), "answer": sentence, "idea": idea, "type": "recall",
                            "wrong": "", "importance": weight.get(psec.number, 0), "card": True})
    return out


def books_of(book_arg=None):
    return [bf.resolve_book(book_arg)] if book_arg else bf.list_books()


def all_questions(book_arg=None, chapter=None):
    return [q for b in books_of(book_arg) for q in book_questions(b, chapter)]


def all_cards(book_arg=None):
    return [c for b in books_of(book_arg) for c in book_cards(b)]

# ---------------------------------------------------------------- choosing what to ask


def misses(rec, last=5):
    return sum(1 for h in rec["history"][-last:] if h.endswith(" n"))


def sure_wrong(rec):
    """True when the last answer was wrong and given as sure."""
    h = rec.get("history") or []
    return bool(h) and h[-1].endswith(" n") and len(h) - 1 in rec.get("sure", [])


def priority(item, rec, now):
    """3 x misses in the last 5 + 2 if last wrong while sure + min(days overdue, 14) / 7 + 1 in box 1 + importance."""
    overdue = (now - datetime.date.fromisoformat(rec["due"])).days if rec.get("due") else 0
    return (3 * misses(rec) + (2 if sure_wrong(rec) else 0) + min(max(overdue, 0), 14) / 7
            + (1 if rec.get("box", 1) == 1 else 0) + item.get("importance", 0))


def recent_ideas(store, items, now, days=3):
    """(book, idea) pairs asked in the last `days` days."""
    idea_of = {i["key"]: i.get("idea", "") for i in items}
    cut = (now - datetime.timedelta(days=days)).isoformat()
    out = set()
    for key, rec in store.items():
        idea = rec.get("idea") or idea_of.get(key, "")
        if idea and any(h[:10] >= cut for h in rec.get("history", [])):
            out.add((rec.get("book", ""), idea))
    return out


def ordered_due(items, store, now):
    """Due items, most urgent first; equal priorities: an idea not asked in the last 3 days, then due date, book order."""
    recent = recent_ideas(store, items, now)
    due = [(n, i) for n, i in enumerate(items) if i["key"] in store and store[i["key"]].get("due", "") <= now.isoformat()]
    return [i for _, i in sorted(due, key=lambda p: (-round(priority(p[1], store[p[1]["key"]], now), 6),
                                                     (p[1]["book"], p[1].get("idea", "")) in recent,
                                                     store[p[1]["key"]]["due"], p[0]))]


def spread(due, count):
    """Take up to count of the ordered due items: no book over 60% of the session (rounded up) while another
    book has due items waiting; no second item from a section while another due section waits."""
    cap, chosen, books, secs, rest = math.ceil(SHARE * count), [], {}, set(), list(due)

    def book_ok(it):
        return books.get(it["book"], 0) < cap or not any(r["book"] != it["book"] for r in rest)

    def section_ok(it):
        where = (it["book"], it["section"])
        return where not in secs or not any((r["book"], r["section"]) not in secs and book_ok(r) for r in rest)
    while rest and len(chosen) < count:
        it = next((r for r in rest if book_ok(r) and section_ok(r)), None) or \
            next((r for r in rest if book_ok(r)), None) or rest[0]
        rest.remove(it)
        chosen.append(it)
        books[it["book"]] = books.get(it["book"], 0) + 1
        secs.add((it["book"], it["section"]))
    return chosen


def pick(questions, store, count, due_only=False):
    """What to ask now, at most count: due items by priority, spread over books and sections, then new ones
    in book order. Without due_only, due items take at most 60% (rounded up) while the most recently written
    chapter of a book has new questions; with nothing new they may take it all."""
    now = today()
    due = ordered_due(questions, store, now)
    new = [] if due_only else [q for q in questions if q["key"] not in store]
    latest = {}
    for q in questions:
        latest[q["book"]] = max(latest.get(q["book"], 0), q["chapter"])
    if new and any(q["chapter"] == latest[q["book"]] for q in new):
        room = max(math.ceil(SHARE * count), count - len(new))
    else:
        room = count
    chosen = spread(due, min(room, count))
    return (chosen + new)[:count]

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
    kind = "card · " if q.get("card") else ""
    return "-" * WIDTH + "\n" + textwrap.shorten("[%d/%d] %s%s · §%s %s · %s" % (
        i, total, kind, q["book_title"], q["section"], q["title"], tag), WIDTH, placeholder="...") + "\n"

# ---------------------------------------------------------------- marking


def mark(store, q, answer, sure=False):
    """Record y, p or n for a question and move it between boxes (right and sure: two boxes up)."""
    rec = store.setdefault(q["key"], {"book": q["book"], "section": q["section"], "title": q["title"],
                                      "question": textwrap.shorten(q["question"], 70), "box": 1,
                                      "due": "", "history": []})
    for f in ("idea", "type", "wrong"):
        if q.get(f):
            rec[f] = q[f]
    now = today()
    if answer == "y":
        rec["box"] = min(rec["box"] + (2 if sure else 1), TOP)
    elif answer == "n":
        rec["box"] = 1
    rec["due"] = (now + datetime.timedelta(days=DAYS[rec["box"]] if answer == "y" else 1)).isoformat()
    if sure:
        rec.setdefault("sure", []).append(len(rec["history"]))
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


def read_answers(path):
    """Marks from an answer file: one per line, y p n q, with ! after y or n when sure."""
    return [l.strip().lower() for l in open(path, encoding="utf-8") if l.strip()] if path else None


def session(chosen, store, answers):
    """Ask each question; returns how many of y, p, n were given."""
    got = {"y": 0, "p": 0, "n": 0}
    ask = "Did you get it? (y)es (p)artly (n)o (q)uit, ! if you were sure "
    for i, q in enumerate(chosen, 1):
        print(header(q, i, len(chosen), store))
        print(render(q["question"]) + "\n")
        try:
            if answers is None:
                input("[Enter] to see the answer ")
                print()
            print("Answer:\n" + render(q["answer"]) + "\n")
            reply = ""
            while reply[:1] not in ("y", "p", "n", "q") or not reply:
                if answers is None:
                    reply = input(ask).strip().lower()
                else:
                    reply = answers.pop(0) if answers else "q"
                    print(ask + reply)
        except (EOFError, KeyboardInterrupt):
            reply = "q"
        if reply[:1] == "q":
            break
        mark(store, q, reply[:1], reply.endswith("!") and reply[:1] in "yn")
        save_store(store)  # after every answer: a cut-off session loses nothing
        got[reply[:1]] += 1
    return got

# ---------------------------------------------------------------- stats


def is_card(key):
    return key.startswith("card/")


def weak_spots(store, n=3):
    """The n sections with the most misses (n marks) as ((book, section, title), misses)."""
    misses_ = {}
    for rec in store.values():
        k = sum(1 for h in rec["history"] if h.endswith(" n"))
        if k:
            spot = (rec["book"], rec["section"], rec["title"])
            misses_[spot] = misses_.get(spot, 0) + k
    return sorted(misses_.items(), key=lambda kv: -kv[1])[:n]


def stats(store, cap=25):
    """Per chapter: boxes and percent right; then weak spots; then practised sections (times practised,
    lowest box, next due date), soonest due first; then cards seen and due, all in at most cap lines."""
    since = (today() - datetime.timedelta(days=14)).isoformat()
    rows, secs = {}, {}
    cards = [r for k, r in store.items() if is_card(k)]
    for key, rec in store.items():
        if is_card(key):
            continue
        row = rows.setdefault((rec["book"], int(rec["section"].split(".")[0])), [0, [0] * TOP, 0, 0])
        row[0] += 1
        row[1][rec["box"] - 1] += 1
        recent = [h for h in rec["history"] if h[:10] >= since]
        row[2] += sum(1 for h in recent if h.endswith(" y"))
        row[3] += len(recent)
        sec = secs.setdefault((rec["book"], rec["section"], rec["title"]), [0, TOP, "9999"])
        sec[0] += len(rec["history"])
        sec[1], sec[2] = min(sec[1], rec["box"]), min(sec[2], rec["due"])
    out = [("%-20s %4s %5s" + " %4s" * TOP + " %9s") % (("book", "ch", "seen") + tuple("box%d" % b for b in range(1, TOP + 1))
                                                        + ("right 14d",))]
    for (book, ch), (seen, boxes, right, total) in sorted(rows.items()):
        pct = "%d%%" % round(100 * right / total) if total else "-"
        out.append(("%-20s %4d %5d" + " %4d" * TOP + " %9s") % ((book[:20], ch, seen) + tuple(boxes) + (pct,)))
    if not rows:
        out.append("nothing practised yet")
    spots = weak_spots(store)
    if spots:
        out.append("\nweak spots:")
        for (book, sec, title), k in spots:
            out.append("  %s (missed %d)" % (textwrap.shorten("%s §%s %s" % (book, sec, title), WIDTH - 16, placeholder="..."), k))
    out.append("cards: %d seen, %d due" % (len(cards), sum(1 for r in cards if r["due"] <= today().isoformat())))
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


def positional(argv, valued):
    return [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in valued)]

# ---------------------------------------------------------------- the learner summary


def answers_of(records):
    """Every (time, mark) of these records, oldest first."""
    return sorted((h[:-2], h[-1]) for r in records for h in r["history"])


def summary_lines(books, store=None):
    """The learner summary for these books: plain Markdown list lines, most important first, 13 at most."""
    store = load_store() if store is None else store
    plans = {slug_of(b): bf.load_plan(b) for b in books}
    plans = {s: p for s, p in plans.items() if p is not None}
    recs = {k: r for k, r in store.items() if r.get("book") in plans}
    out = []
    # wrong beliefs that keep returning
    beliefs = {}
    for r in recs.values():
        if r.get("wrong"):
            b = beliefs.setdefault((r["book"], r["wrong"]), [0, 0, set()])
            b[0] += sum(1 for h in r["history"] if h.endswith(" n"))
            b[1] += sum(1 for i in r.get("sure", []) if i < len(r["history"]) and r["history"][i].endswith(" n"))
            b[2].add(r["section"])
    for (book, name), (n, sure, secs) in sorted(beliefs.items(), key=lambda kv: (-kv[1][1], -kv[1][0], kv[0]))[:3]:
        if n >= 2 or sure:
            out.append("- Wrong belief that keeps returning: \"%s\" (%s, missed %d%s)" % (
                name, ", ".join("§" + s for s in sorted(secs, key=bf.section_key)), n,
                ", %d while sure" % sure if sure else ""))
    # per idea
    ideas = {}
    for r in recs.values():
        if r.get("idea"):
            ideas.setdefault((r["book"], r["idea"]), []).append(r)
    weak = []
    for (book, idea), rs in sorted(ideas.items()):
        last = [m for _, m in answers_of(rs)][-5:]
        if last.count("n") >= 2:
            plan = plans[book]
            teacher = plan.teacher().get(idea)
            secs = [s for ch in plan.chapters for s in ch.sections]
            after = secs[secs.index(teacher) + 1:] if teacher in secs else secs
            lean = [s for s in after if idea in s.needs]
            if lean:
                weak.append("- Weak foundation: %s (missed %d of the last %d); %s lean%s on it" % (
                    idea, last.count("n"), len(last), ", ".join("§%s %s" % (s.number, s.title) for s in lean[:3]),
                    "s" if len(lean) == 1 else ""))
    out += weak[:3]
    gap, solid = [], []
    for (book, idea), rs in sorted(ideas.items()):
        said = [r for r in rs if r.get("type") in ("recall", "explain") and r["box"] >= 2]
        done = [r for r in rs if r.get("type") in bf.Q_APPLY]
        if any(r["box"] >= 3 for r in done):
            solid.append(idea)
        if said:
            last = answers_of(done)
            if not done or not last:
                gap.append("%s (never tried)" % idea)
            elif last[-1][1] in "np":
                gap.append("%s (last: %s)" % (idea, {"n": "wrong", "p": "partly"}[last[-1][1]]))
    if gap:
        out.append("- Can explain, cannot yet apply: " + ", ".join(gap[:5]) + (" and %d more" % (len(gap) - 5) if len(gap) > 5 else ""))
    if solid:
        out.append("- Solid: %d idea%s applied well (%s%s)" % (len(solid), "" if len(solid) == 1 else "s",
                                                              ", ".join(solid[:5]), ", ..." if len(solid) > 5 else ""))
    passed = sorted((k, r) for k, r in recs.items() if k.startswith("check/") and r["history"] and r["history"][-1].endswith(" y"))
    if passed:
        out.append("- Applied alone: " + ", ".join("%s (§%s, %s)" % (k.rsplit("/", 1)[1], r["section"], r["history"][-1][:10])
                                                    for k, r in passed[:5]))
    practised = {(r["book"], r["section"]) for r in recs.values()}
    left = 0
    for b in books:
        if slug_of(b) in plans:
            for q in {(q["book"], q["section"]) for q in book_questions(b)}:
                left += q not in practised
    if left:
        out.append("- Not yet practised: %d section%s" % (left, "" if left == 1 else "s"))
    return out[:SUMMARY_LINES - 2]


def write_summary(books, store=None):
    """Write <private>/learner.md (15 lines at most); returns its text."""
    lines = summary_lines(books, store)
    text = "# What you know so far\n\n" + ("\n".join(lines) if lines else "- Nothing practised yet.") + "\n"
    path = os.path.join(bf.private_dir(), "learner.md")
    if not os.path.exists(path) or bf.read_text(path) != text:
        bf.write_text(path, text)
    return text

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


RECORD_USAGE = ("usage: python3 scripts/us_practice.py record BOOK N.M right|partly|no [--sure] [--note TEXT] "
                "[--type TYPE] [--idea ID] [--wrong NAME]")


def plan_section(book, number):
    """(plan, chapter, section) of N.M, or a message."""
    plan = bf.load_plan(book)
    if plan is None:
        return "no plan at %s: give the book's name or folder" % book
    ch = plan.chapter(int(number.split(".")[0]))
    sec = next((s for s in ch.sections if s.number == number), None) if ch else None
    if sec is None:
        return "no section %s in the plan of %s: give a section number from PLAN.md" % (number, slug_of(book))
    return plan, ch, sec


def record(argv):
    """us_practice.py record BOOK N.M right|partly|no [--sure] [--note TEXT] [--type T] [--idea ID] [--wrong NAME]:
    log one answer given in a lesson."""
    note, qtype, idea, wrong = (option(argv, o, "") for o in ("--note", "--type", "--idea", "--wrong"))
    args = positional(argv, {"--note", "--type", "--idea", "--wrong"})
    if len(args) != 3 or args[2] not in MARKS or not re.fullmatch(r"§?\d+\.\d+", args[1]):
        print(RECORD_USAGE)
        return 2
    if qtype and qtype not in bf.Q_TYPES:
        print("unknown --type %s; types: %s" % (qtype, ", ".join(bf.Q_TYPES)))
        return 2
    book, number, word = bf.resolve_book(args[0]), args[1].lstrip("§"), args[2]
    found = plan_section(book, number)
    if isinstance(found, str):
        print(found)
        return 1
    _, ch, sec = found
    slug, mark_, sure = slug_of(book), MARKS[word], "--sure" in argv
    key = "%s/%s/lesson" % (slug, number) + ("/%s/%s" % (idea or "-", qtype or "-") if idea or qtype else "")
    store = load_store()
    mark(store, {"key": key, "book": slug, "section": number, "title": sec.title,
                 "question": "answers given in a lesson or check", "idea": idea or (sec.teaches[:1] or [""])[0],
                 "type": qtype, "wrong": " ".join(wrong.split())}, mark_, sure and mark_ in "yn")
    save_store(store)
    rec = store[key]
    said = ["recorded: %s §%s %s: %s (box %d, comes back %s)" % (slug, number, sec.title, word, rec["box"], rec["due"])]
    said.append(levels_line(slug, ch.number, mark_))
    if mark_ != "y":
        path = os.path.join(bf.private_dir(), "weaknesses.md")
        text = bf.read_text(path) if os.path.exists(path) else ""
        line = "- %s §%s %s (%s): %s%s%s" % (today(), number, sec.title, slug, word, ", sure" if sure else "",
                                             ": " + " ".join(note.split()) if note.strip() else "")
        if line not in text.splitlines():
            bf.write_text(path, text + ("\n" if text and not text.endswith("\n") else "") + line + "\n")
            said.append("weaknesses.md: added the line `%s`" % line)
    print("\n".join(s for s in said if s))
    write_summary([book], store)
    import us_resume
    us_resume.main([book])
    return 0

# ---------------------------------------------------------------- testing your own work


def checklist_items(lines, line, end):
    """The list items straight after a checklist marker on 1-based line `line` (us_bookfmt's reader if it has one)."""
    if hasattr(bf, "checklist_items"):
        return bf.checklist_items(lines, line, end)
    items = []
    for raw in lines[line:end]:
        m = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", raw)
        if m:
            items.append(m.group(1).strip())
        elif raw.strip():
            break
    return items


def tidy(text, masks):
    """Trailing spaces and blank lines cut, the plan's mask: patterns blanked: lines to compare."""
    for pattern in masks:
        text = pattern.sub("~", text)
    lines = [l.rstrip() for l in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def run_check(block, command, folder, masks, expected):
    """Run the reader's program; (passed, what to print)."""
    import us_run
    if any(re.search(p, command) for p in us_run.DANGER):
        return False, "REFUSED %s: `%s` looks dangerous; not run" % (block.id, command)
    stdin = us_run.unescape(block.attrs.get("stdin", "")).encode()
    try:
        limit = float(block.attrs.get("timeout") or CHECK_TIMEOUT)
    except ValueError:
        limit = CHECK_TIMEOUT
    argv = ["sh", "-c", command + ' "$@"', "sh"] + shlex.split(us_run.unescape(block.attrs.get("args", "")))
    hide = block.attrs.get("stderr") == "hide"
    try:
        p = subprocess.Popen(argv, cwd=folder, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL if hide else subprocess.STDOUT, start_new_session=True)
    except OSError as e:
        return False, "FAIL %s: cannot run `%s` in %s: %s" % (block.id, command, folder, e)
    try:
        out, _ = p.communicate(stdin, timeout=limit)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.communicate()
        return False, "FAIL %s: still running after %g seconds (timed out); does it wait for input it never gets?" % (
            block.id, limit)
    got = tidy(out.decode("utf-8", "replace"), masks)
    want = tidy(expected, masks)
    if got == want:
        return True, "PASS %s" % block.id
    k = next((i for i in range(max(len(got), len(want))) if i >= len(got) or i >= len(want) or got[i] != want[i]))
    return False, "FAIL %s: line %d differs\n  expected: %s\n  got:      %s" % (
        block.id, k + 1, want[k] if k < len(want) else "(no more lines)", got[k] if k < len(got) else "(no more lines)")


def pasted_output(lines, block):
    """The text inside the ```text fence us_run.py pasted for a block, or None."""
    region = [l.rstrip("\r\n") for l in lines[block.out_start:block.out_end]]
    while region and not region[0].strip():
        region.pop(0)
    if len(region) < 2 or not bf.FENCE_OPEN.match(region[0]):
        return None
    return "\n".join(region[1:-1])


def check(argv):
    """us_practice.py check BOOK N.M [--in FOLDER] [--answer-file PATH]."""
    import us_run
    args = positional(argv, {"--in", "--answer-file"})
    if len(args) != 2 or not re.fullmatch(r"§?\d+\.\d+", args[1]):
        print("usage: python3 scripts/us_practice.py check BOOK N.M [--in FOLDER] [--answer-file PATH]")
        return 2
    book, number = bf.resolve_book(args[0]), args[1].lstrip("§")
    found = plan_section(book, number)
    if isinstance(found, str):
        print(found)
        return 1
    _, ch, psec = found
    path = bf.chapter_path(book, ch.number)
    doc = bf.parse_chapter(bf.read_text(path)) if path else None
    sec = doc.section(number) if doc else None
    if sec is None:
        print("§%s is not written yet: nothing to check" % number)
        return 1
    folder = os.path.abspath(option(argv, "--in", "."))
    masks = []
    for pattern in bf.plan_meta(book, "mask"):
        try:
            masks.append(re.compile(pattern))
        except re.error:
            pass
    blocks, _ = us_run.parse_chapter(doc.lines)
    blocks = [b for b in blocks if sec.line < b.marker <= sec.end and b.attrs.get("check")]
    lists = [(ln, bf.CHECKLIST_MARK.match(doc.lines[ln - 1])) for ln in range(sec.line + 1, sec.end + 1)]
    lists = [(ln, bf.parse_attrs(m.group(1)).get("id", "") or "checklist-%d" % ln) for ln, m in lists if m]
    if not blocks and not lists:
        print("§%s %s has nothing to check: no program with check= and no checklist" % (number, sec.title))
        return 1
    results, answers = [], read_answers(option(argv, "--answer-file"))
    for b in blocks:
        expected = pasted_output(doc.lines, b)
        if expected is None:
            ok, said = False, "FAIL %s: the book has no pasted output for this program yet (run us_run.py on the chapter)" % b.id
        elif b.lang == us_run.CONSOLE:
            ok, said = False, "FAIL %s: a terminal session cannot be checked this way" % b.id
        else:
            ok, said = run_check(b, b.attrs["check"], folder, masks, expected)
        print(said)
        results.append((b.id, ok))
    unattended = answers is None and not sys.stdin.isatty()     # nobody to answer: never wait for y/n
    for ln, cid in lists:
        items = checklist_items(doc.lines, ln, sec.end)
        if unattended:
            print("Checklist %s: no one to answer here (stdin is not a terminal)" % cid)
            print("\n".join("  check by hand: %s" % item for item in items))
            continue
        print("Checklist %s: answer each about your own work, y or n" % cid)
        yes = True
        for item in items:
            try:
                reply = (answers.pop(0) if answers else "n") if answers is not None else input("  %s (y/n) " % item).strip().lower()
            except (EOFError, KeyboardInterrupt):
                reply = "n"
            if answers is not None:
                print("  %s (y/n) %s" % (item, reply))
            yes = yes and reply[:1] == "y"
        print(("PASS %s" if yes and items else "FAIL %s") % cid)
        results.append((cid, yes and bool(items)))
    store, slug = load_store(), slug_of(book)
    for cid, ok in results:
        mark(store, {"key": "check/%s/%s/%s" % (slug, number, cid), "book": slug, "section": number,
                     "title": sec.title, "question": "self-test %s" % cid, "idea": (psec.teaches[:1] or [""])[0],
                     "type": "build"}, "y" if ok else "n")
    save_store(store)
    if any(ok for _, ok in results):
        said = levels_line(slug, ch.number, "y")
        if said:
            print(said)
    passed = sum(ok for _, ok in results)
    print("%d of %d passed" % (passed, len(results)) + ("; the checklist%s: check by hand" % ("s" if len(lists) > 1 else "")
                                                        if unattended and lists else ""))
    write_summary([book], store)
    import us_resume
    us_resume.main([book])
    return 0 if passed == len(results) else 1

# ---------------------------------------------------------------- main


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    if argv and argv[0] == "record":
        return record(argv[1:])
    if argv and argv[0] == "check":
        return check(argv[1:])
    store = load_store()
    if "--stats" in argv:
        return stats(store)
    valued = {"--chapter", "--count", "--answer-file", "--minutes"}
    rest = positional(argv, valued)
    if "--summary" in argv:
        print(write_summary(books_of(rest[0] if rest else None), store), end="")
        return 0
    chapter = int(option(argv, "--chapter", 0))
    cards, due_only = "--cards" in argv, "--due" in argv
    items = [] if cards else all_questions(rest[0] if rest else None, chapter)
    if cards or due_only:
        items += all_cards(rest[0] if rest else None)
    if not items:
        print("no cards yet: no written chapter has a key term with a definition" if cards else
              "no questions yet: no written chapter has a Check yourself or practice section")
        return 1
    count = int(option(argv, "--count", 10))
    if option(argv, "--minutes"):
        count = max(3, round(float(option(argv, "--minutes")) / MINUTES_EACH))
    chosen = pick(items, store, count, due_only)
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
    answers = read_answers(option(argv, "--answer-file"))
    prune(store, items)
    got = session(chosen, store, answers)
    print("-" * WIDTH + "\n%d right, %d partly, %d missed. Saved in %s" % (got["y"], got["p"], got["n"], store_path()))
    write_summary(books_of(rest[0] if rest else None), store)
    import us_resume
    us_resume.main(rest[:1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
