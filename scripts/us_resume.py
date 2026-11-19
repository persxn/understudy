#!/usr/bin/env python3
"""Write <private>/RESUME.md: where you are, what to do with no AI, and the sentence to start with when you're back.

    python3 scripts/us_resume.py [BOOK ...]      no BOOK: every book under the book root
    python3 scripts/us_resume.py --next "TEXT" [BOOK ...]   set the "Next:" line of private/now.md, then rebuild

Made from files only (each book's PLAN.md and STATUS.json, private/now.md, goal.md, route.md, levels.yaml,
practice.json, weaknesses.md, build.md and machine.md), so it is safe to run at the end of every job.
Under the weak spots: the first six lines of the learner summary (us_practice.py --summary).
Same files, same note.
"""
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
import us_plan  # noqa: E402
import us_practice  # noqa: E402


def private_file(name):
    path = os.path.join(bf.private_dir(), name)
    return bf.read_text(path) if os.path.exists(path) else ""


def short(path):
    """A path relative to the control folder when it is inside it."""
    rel = os.path.relpath(path, bf.ROOT)
    return path if rel.startswith("..") else rel


def ranges(numbers):
    """[1, 2, 3, 5] -> '1-3, 5'."""
    out = []
    for n in numbers:
        if out and out[-1][1] == n - 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(str(a) if a == b else "%d-%d" % (a, b) for a, b in out) or "none"


def next_stop():
    """First `name@level` on the route not yet proven in levels.yaml, or ''."""
    proven = {}
    for m in re.finditer(r"^([\w.-]+):\s*\{[^}]*level:\s*(\d)[^}]*state:\s*proven", private_file("levels.yaml"), re.M):
        proven[m.group(1)] = int(m.group(2))
    for name, level in re.findall(r"([a-z0-9][\w.-]*)@(\d)", private_file("route.md")):
        if proven.get(name, 0) < int(level):
            return "%s@%s" % (name, level)
    return ""


def blocked_lines():
    """Each `- blocked:` entry of machine.md, with its indented continuation lines."""
    out = []
    for line in private_file("machine.md").splitlines():
        if line.startswith("- blocked:"):
            out.append(line.rstrip())
        elif out and out[-1] is not None and line.startswith((" ", "\t")) and line.strip():
            out[-1] += " " + line.strip()
        elif out:
            out.append(None)
    return [l for l in out if l]


def section(title, text, cap=None):
    """A '## title' block holding the file's lines (headings left out), or nothing for an empty file."""
    lines = [l.rstrip() for l in text.splitlines() if l.strip() and not l.startswith("#")][:cap]
    return ["", "## " + title] + [l if l.lstrip().startswith(("-", "*")) else "- " + l.strip() for l in lines] if lines else []


FIRST_NOTE = "First session. No goal recorded yet."      # what us_init.py puts in a new private/now.md


def set_next(text):
    """Replace (or add) the line starting 'Next:' in private/now.md."""
    path = os.path.join(bf.private_dir(), "now.md")
    lines = [l for l in private_file("now.md").splitlines() if l.strip() != FIRST_NOTE]   # us_init's placeholder
    line = "Next: " + " ".join(text.split())
    at = [(i, m.group(1)) for i, m in enumerate(re.match(r"(\s*(?:[-*]\s*)?)next:", l, re.I) for l in lines) if m]
    if at:
        lines[at[0][0]] = at[0][1] + line
    else:
        lines.append(line)
    bf.write_text(path, "\n".join(lines) + "\n")


def book_line(book, plan):
    status, states = bf.read_status(book), {}
    for ch in plan.chapters:
        states[ch.number] = us_plan.chapter_state(book, ch, status)[0]
    done = [n for n, s in states.items() if s in ("written", "reviewed")]
    nxt = us_plan.next_to_write(book, plan)
    todo = "next to write: chapter %d, §%s %s" % (nxt[0].number, nxt[1].number, nxt[1].title) if nxt else "all written"
    taken = {c.number for c in us_plan.route_chapters(book, plan)}
    skipped = [c.number for c in plan.chapters if c.number not in taken]
    part = [n for n, s in states.items() if s == "writing"]
    return "- %s (%d chapters): written %s, reviewed %s%s%s; %s." % (
        plan.title, len(plan.chapters), ranges(done), ranges([n for n, s in states.items() if s == "reviewed"]),
        ", some sections of %s" % ranges(part) if part else "",
        ", skipped %s" % ranges(skipped) if skipped else "", todo), done


def build(books):
    books = [b for b in books if bf.load_plan(b)]
    slugs = {os.path.basename(b.rstrip(os.sep)) for b in books}
    store = {k: r for k, r in us_practice.load_store().items() if r["book"] in slugs}
    last = max(((h, r) for r in store.values() for h in r["history"]), default=None,
               key=lambda x: (x[0][:-2], bf.section_key(x[1]["section"])))  # same second: the later section
    slug = last[1]["book"] if last else None
    cur = next((b for b in books if os.path.basename(b.rstrip(os.sep)) == slug), books[0] if books else None)
    blocked = blocked_lines()
    out = ["# Where you left off", ""] + (["## Blocked on this machine"] + blocked + [""] if blocked else []) + [
        "Made from your files on %s. All of it works with no AI." % us_practice.today(), "", "## Where you are"]
    written = [] if books else out.append("- No book yet.")
    for b in books:
        line, done = book_line(b, bf.load_plan(b))
        out.append(line)
        written = done if b == cur else written
    if last:
        out.append("- Last practised: §%s %s, on %s." % (last[1]["section"], last[1]["title"], last[0][:10]))
    goal = re.search(r"^goal:\s*(.+)$", private_file("goal.md"), re.M)
    stop = next_stop()
    out += ["- Goal: %s" % goal.group(1).strip()] if goal else []
    out += ["- Next on your route: %s." % stop] if stop else []
    out += section("Last note (private/now.md)", private_file("now.md"))
    out += section("Your project (private/build.md, first lines)", private_file("build.md"), 5)
    out += ["", "## Today, with no AI"]
    if cur is None:
        out.append("- No book yet. When you are back, ask for your first book.")
    elif not written:
        plan, arg = bf.load_plan(cur), cur if short(cur) == cur else os.path.basename(cur.rstrip(os.sep))
        first = (us_plan.route_chapters(cur, plan) or plan.chapters)[:1]
        out.append("- Nothing is written yet, so there is nothing to read or practise.")
        for c in first:
            out.append("- Look up what chapter %d, %s, is about: %s." % (
                c.number, c.title, "; ".join(s.title for s in c.sections[:6])))
        out.append("- Read the contents page and the habits card of your book: `%s` and `PRACTICES.md` beside it."
                   % os.path.join(os.path.relpath(cur), "PLAN.md"))
        out.append("- Check this machine: `python3 scripts/us_doctor.py %s`" % arg)
    else:
        plan, arg = bf.load_plan(cur), cur if short(cur) == cur else os.path.basename(cur.rstrip(os.sep))
        reading = int(last[1]["section"].split(".")[0]) if last else (written[0] if written else 0)
        chs = [plan.chapter(n) for n in (reading, reading + 1) if n in written]
        if chs:
            out.append("- Read " + ", then ".join("chapter %d, %s" % (c.number, c.title) for c in chs) + ".")
        qs = us_practice.all_questions(cur)
        due = len(us_practice.pick(qs, store, len(qs), True))
        out.append("- Practice: %d question%s due today, %d new waiting." % (
            due, "" if due == 1 else "s", sum(1 for q in qs if q["key"] not in store)))
        out.append("- Reading page: `python3 scripts/us_reader.py --serve`, then open http://localhost:8765")
        out.append("- Practise: `python3 scripts/us_practice.py %s` (your record: `--stats`)" % arg)
    spots = us_practice.weak_spots(store)
    noted = [l.strip() for l in private_file("weaknesses.md").splitlines() if l.strip().startswith(("-", "*"))][-5:]
    learner = [textwrap.shorten(l, 160, placeholder=" ...") for l in us_practice.summary_lines(books, store)[:6]]
    out += ["", "## Weak spots"] + (["- §%s %s (missed %d)" % (sec, title, k) for (_, sec, title), k in spots] + noted
                                    + learner or ["- none yet"])
    where = "my book %s" % bf.load_plan(cur).title if cur else "the start"
    if last:
        where += ", chapter %s, §%s %s" % (last[1]["section"].split(".")[0], last[1]["section"], last[1]["title"])
    out += ["", "## When your subscription is back, start with this sentence:", "",
            "> I'm back after a break. I was at %s. Read private/RESUME.md and private/practice.json, "
            "update my levels from my offline practice%s, and pick up from there." % (
                where, ", then go over " + ", ".join("§" + s[0][1] for s in spots) if spots else "")]
    return "\n".join(out) + "\n"


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    if "--next" in argv:
        i = argv.index("--next")
        if i + 1 >= len(argv) or not argv[i + 1].strip():
            print('--next needs the text of the next step: us_resume.py --next "write chapter 2"')
            return 2
        set_next(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    books = [bf.resolve_book(a) for a in argv] or bf.list_books()
    path = os.path.join(bf.private_dir(), "RESUME.md")
    text = build(books)
    if not os.path.exists(path) or bf.read_text(path) != text:
        bf.write_text(path, text)
    print("resume note written: %s" % short(path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
