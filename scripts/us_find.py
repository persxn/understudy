#!/usr/bin/env python3
"""Find where something is taught without reading a chapter.

    python3 scripts/us_find.py WORDS [--book BOOK] [--read]
    python3 scripts/us_find.py [BOOK] 12.3 [--read]      a section by its number

Matches idea terms first, then section titles, then the prose; prints at most five lines:
    book 8.2 Title  chapters/08-x.md:120-214  (taught: pointer)
--read prints the best match's section (at most 120 lines; a note says what was cut).
Reads search.json at the book root (run us_index.py first); prose is searched in the chapter files.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402

CAP = 120
STOP = set("a an the of to in and or is are what how why does do for on with it its i my".split())


def words(text):
    """Lower-case words of a text, without stop words."""
    return [w for w in re.findall(r"[a-z0-9_#+&*%-]+", text.lower()) if w not in STOP]


def stem(w):
    """Crude stem: 'dereferencing' and 'dereferences' -> 'dereferenc'."""
    for end in ("ing", "es", "ed", "s"):
        if w.endswith(end) and len(w) - len(end) >= 4:
            return w[:-len(end)]
    return w


def load(root):
    """search.json sections, or exit with the fix."""
    path = os.path.join(root, "search.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        sys.exit("no index at %s: run python3 scripts/us_index.py" % root)
    if data.get("schema") != 3:
        sys.exit("the index is from an older version: run python3 scripts/us_index.py")
    return data["sections"]


def score_terms(want, entry):
    """(share of query words found in one idea term, all found?, that term)."""
    best = (0, False, 0, "")
    for term in entry["terms"]:
        tw = {stem(w) for w in words(term)}
        hit = sum(1 for w in want if stem(w) in tw)
        if hit:
            best = max(best, (hit / len(want), hit == len(want), -len(term), term))
    return best[0], best[1], best[-1]


def score_title(want, entry):
    """Share of query words in the section title."""
    tw = {stem(w) for w in words(entry["title"])}
    return sum(1 for w in want if stem(w) in tw) / len(want)


def prose_hits(want, root, entries):
    """Count query-word hits per written section, reading each chapter file once."""
    counts, files = {}, {}
    for e in entries:
        if e["file"]:
            files.setdefault(e["file"], []).append(e)
    pats = [re.compile(r"\b%s\w*" % re.escape(stem(w)), re.I) for w in want]
    for file, secs in files.items():
        path = os.path.join(root, file)
        if not os.path.exists(path):
            continue
        lines = bf.read_text(path).splitlines()
        for e in secs:
            text = "\n".join(lines[e["lines"][0] - 1:e["lines"][1]])
            found = [len(p.findall(text)) for p in pats]
            if all(found):
                counts[(e["book"], e["id"])] = sum(found)
    return counts


def rank(query, root, entries):
    """Best sections for the query, idea terms first, then titles, then prose: list of (score, entry, why)."""
    want = words(query) or query.lower().split()
    hits = prose_hits(want, root, entries)
    out = []
    for e in entries:
        frac, full, term = score_terms(want, e)
        title = score_title(want, e)
        prose = hits.get((e["book"], e["id"]), 0)
        score = 1000 * full + 200 * (title == 1) + 100 * title + 80 * frac + min(prose, 50)
        if full:
            why = "taught: %s" % term
        elif title >= 0.5:
            why = "title"
        elif frac >= 0.5:
            why = "taught: %s" % term
        elif prose:
            why = "prose: %d hit%s" % (prose, "" if prose == 1 else "s")
        else:
            continue
        out.append((score, e, why))
    return sorted(out, key=lambda x: (-x[0], bf.section_key(x[1]["id"])))


def show(hit):
    """One result line."""
    _, e, why = hit
    where = "%s:%d-%d" % (e["file"].split("/", 1)[1], e["lines"][0], e["lines"][1]) if e["file"] else "planned"
    return "%s %s %s  %s" % (e["book"], e["id"], e["title"], where) + ("  (%s)" % why if why else "")


def read(root, e):
    """Print one section, capped at CAP lines, with a note of what was cut."""
    if not e["file"]:
        print("%s %s is planned, not written" % (e["book"], e["id"]))
        return
    lines = bf.read_text(os.path.join(root, e["file"])).splitlines()[e["lines"][0] - 1:e["lines"][1]]
    while lines and not lines[-1].strip():
        lines.pop()
    print("\n".join(lines[:CAP]))
    if len(lines) > CAP:
        rest = lines[CAP:]
        heads = [l.lstrip("# ").strip() for l in rest if re.match(r"^#{3,4}\s", l)]
        tail = ("; still to come: " + ", ".join(heads)) if heads else ""
        print("[cut: lines %d-%d of %s (%d lines)%s]" % (e["lines"][0] + CAP, e["lines"][0] + len(lines) - 1,
                                                       e["file"], len(rest), tail))


def main(argv):
    if not argv or "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    args = list(argv)
    book = None
    if "--book" in args:
        i = args.index("--book")
        if i + 1 >= len(args):
            print("--book needs a book name")
            return 2
        book = args[i + 1]
        del args[i:i + 2]
    do_read = "--read" in args
    given = [a for a in args if not a.startswith("--")]
    number = re.fullmatch(r"§?(\d+\.\d+)", given[-1]) if given and len(given) <= 2 else None
    if number and len(given) == 2:
        if book or not os.path.isdir(bf.resolve_book(given[0])):
            number = None
        else:
            book = given[0]
    query = " ".join(given)
    if not query:
        print("give words to look for")
        return 2
    if book:
        path = bf.resolve_book(book)
        root, name = os.path.dirname(path.rstrip(os.sep)), os.path.basename(path.rstrip(os.sep))
    else:
        root, name = bf.book_root(), None
    if not any(glob.glob(os.path.join(b, "chapters", "*.md")) for b in ([path] if book else bf.list_books(root))):
        print("nothing is written yet: no chapter of %s exists, so there is nothing to search; the plan is in PLAN.md"
              % (name or "any book"))
        return 0
    entries = [e for e in load(root) if name is None or e["book"] == name]
    if number:
        hits = [(0, e, "") for e in entries if e["id"] == number.group(1)]
        if not hits:
            print("no section %s" % number.group(1))
            return 1
        if do_read and len(hits) > 1:
            print("\n".join(show(h) for h in hits) + "\nseveral books have §%s: name one, us_find.py BOOK %s --read"
                  % ((number.group(1),) * 2))
            return 2
    else:
        hits = rank(query, root, entries)
    if not hits:
        print("nothing matches '%s'" % query)
        return 1
    if do_read:
        print(show(hits[0]))
        read(root, hits[0][1])
        return 0
    for h in hits if number else hits[:5]:
        print(show(h))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
