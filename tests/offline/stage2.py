"""Stage 2, the learner side: question tags, choosing what to ask, cards, the learner summary, self-tests.

    python3 tests/offline/stage2.py

Small books are made in a temp folder; the private folder is a temp folder too (UNDERSTUDY_PRIVATE), and
dates are faked with UNDERSTUDY_TODAY. Scripts run as commands, except where a test needs to answer
question by question (the priority order, the 30-day simulation): there it calls us_practice's functions.
One line per test, then "N passed, M failed"; exit 1 on any failure.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
TMP = tempfile.mkdtemp(prefix="us-stage2-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP
TODAY = datetime.date(2026, 3, 2)
RESULTS = []
sys.path.insert(0, SCRIPTS)
import us_practice as up  # noqa: E402


def day(n):
    return (TODAY + datetime.timedelta(days=n)).isoformat()


def env(private, when=0, **extra):
    e = dict(os.environ, UNDERSTUDY_PRIVATE=private, UNDERSTUDY_TODAY=day(when))
    e.update(extra)
    return e


def run(script, *args, e=None, cwd=None):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + [str(a) for a in args],
                       capture_output=True, text=True, env=e, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("pass  " if ok else "FAIL  ") + name + ("" if ok else ": " + str(detail).replace("\n", " | ")[:500]))


def read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def store(private):
    path = os.path.join(private, "practice.json")
    return json.load(open(path)) if os.path.exists(path) else {}


def inproc(private, when=0):
    """Point us_practice, called in this process, at a private folder and a date."""
    os.environ["UNDERSTUDY_PRIVATE"] = private
    os.environ["UNDERSTUDY_TODAY"] = day(when)

# ---------------------------------------------------------------- making small books


def question(n, text, answer, tag=None):
    return ([tag] if tag else []) + ["%d. %s" % (n, text), "", "<details>", "<summary>Answer</summary>", "",
                                     answer, "", "</details>", ""]


def section(number, title, teaches=(), questions=(), body=()):
    """teaches: (idea, word, defined); questions: (tag or None, text, answer)."""
    out = ["## %s %s" % (number, title), ""]
    for idea, word, defined in teaches:
        out += ["<!-- teaches: %s = %s -->" % (idea, word),
                ("A **%s** is the thing called %s in this small test book." % (word, word)) if defined else
                "Some plain words about it, with nothing in bold.", ""]
    out += list(body)
    if questions:
        out += ["### Check yourself", ""]
        for k, (tag, text, answer) in enumerate(questions, 1):
            out += question(k, text, answer, tag)
    return out


def make_book(slug, title, chapters, run_line="python", head=()):
    """chapters: [(n, title, [(number, title, plan fields, section lines)])]; returns the book folder."""
    book = os.path.join(TMP, "books", slug)
    os.makedirs(os.path.join(book, "chapters"))
    plan = ["# " + title, "for: someone new", "run: " + run_line] + list(head) + [""]
    for n, ctitle, secs in chapters:
        plan += ["### %d %s" % (n, ctitle)] + ["%s %s%s" % (num, t, (" | " + f) if f else "") for num, t, f, _ in secs] + [""]
        text = ["# Chapter %d: %s" % (n, ctitle), ""]
        for _, _, _, lines in secs:
            text += lines + [""]
        open(os.path.join(book, "chapters", "%02d-c%d.md" % (n, n)), "w").write("\n".join(text) + "\n")
    open(os.path.join(book, "PLAN.md"), "w").write("\n".join(plan) + "\n")
    return book


def small_book(slug="tb", title="Test Book"):
    """Two chapters: 1.1 teaches alpha (defined) and beta (no definition); 1.2 needs alpha; 2.1 needs alpha."""
    s11 = section("1.1", "Alpha", [("alpha", "alpha", True), ("beta", "beta", False)], [
        ("<!-- q: idea=alpha type=recall -->", "What is alpha?", "The first thing."),
        ("<!-- q: idea=alpha type=predict wrong=\"alpha is beta\" -->", "What does the alpha line print?", "It prints 1."),
        (None, "Say alpha out loud.", "Alpha."),
    ])
    s12 = section("1.2", "Gamma", [("gamma", "gamma", True)], [
        ("<!-- q: idea=gamma type=explain -->", "Why gamma?", "Because."),
        ("<!-- q: idea=gamma type=apply -->", "Use gamma.", "Like so."),
    ])
    s13 = section("1.3", "Story", (), [(None, "Who wrote it?", "Someone.")])
    s21 = section("2.1", "Delta", [("delta", "delta", True)], [
        ("<!-- q: idea=delta type=fix -->", "Fix delta.", "Fixed."),
        ("<!-- q: idea=delta type=decide -->", "Choose delta.", "Chosen."),
    ])
    return make_book(slug, title, [
        (1, "Start", [("1.1", "Alpha", "teaches: alpha, beta", s11), ("1.2", "Gamma", "teaches: gamma | needs: alpha", s12),
                      ("1.3", "Story", "story", s13)]),
        (2, "More", [("2.1", "Delta", "teaches: delta | needs: alpha, gamma", s21)]),
    ])

# ---------------------------------------------------------------- B1 tags


def test_tags():
    book = small_book("tags")
    qs = up.book_questions(book)
    got = [(q["section"], q["idea"], q["type"], q["wrong"]) for q in qs]
    check("tags: idea, type and wrong read from the line above each question",
          got[:2] == [("1.1", "alpha", "recall", ""), ("1.1", "alpha", "predict", "alpha is beta")], got)
    check("tags: an untagged question gets the section's first idea and type unknown", got[2] == ("1.1", "alpha", "unknown", ""), got)
    check("tags: an untagged question in a section that teaches nothing has no idea", got[5] == ("1.3", "", "unknown", ""), got)
    check("tags: importance from later sections' needs (alpha: 2 of them)",
          qs[0]["importance"] == 2 * 2 / 5 and qs[3]["importance"] == 2 * 1 / 5 and qs[-1]["importance"] == 0,
          [q["importance"] for q in qs])
    private = os.path.join(TMP, "p-tags")
    code, out = run("us_practice.py", book, "--plain", "--count", 50, e=env(private))
    check("tags: plain output hides the tags", code == 0 and "<!--" not in out and "q: idea" not in out and "[8/8]" in out, out)

    code, out = run("us_practice.py", "record", book, "1.1", "no", "--sure", "--type", "predict", "--idea", "alpha",
                    "--wrong", "alpha is beta", e=env(private))
    rec = store(private).get("tags/1.1/lesson/alpha/predict", {})
    check("record --type --idea --wrong: kept on its own record, sure-wrong remembered",
          code == 0 and (rec.get("idea"), rec.get("type"), rec.get("wrong"), rec.get("sure")) == ("alpha", "predict", "alpha is beta", [0]),
          (out, rec))
    code, out = run("us_practice.py", "record", book, "1.1", "right", e=env(private))
    rec = store(private).get("tags/1.1/lesson", {})
    check("record without the options: the old key, idea from the plan", code == 0 and rec.get("idea") == "alpha" and "type" not in rec, rec)
    code, out = run("us_practice.py", "record", book, "1.1", "right", "--type", "guess", e=env(private))
    check("record with an unknown type: exit 2, lists the types", code == 2 and "recall, explain, predict" in out, out)
    check("record rewrites learner.md", os.path.exists(os.path.join(private, "learner.md")), os.listdir(private))

# ---------------------------------------------------------------- B2 choosing


def item(key, book="b", section="1.1", idea="", chapter=1, importance=0):
    return {"key": key, "book": book, "book_title": book, "section": section, "title": "T", "chapter": chapter,
            "question": "q", "answer": "a", "idea": idea or key, "type": "recall", "wrong": "", "importance": importance}


def rec(book="b", section="1.1", box=2, due=0, history=("y",), sure=(), idea=""):
    r = {"book": book, "section": section, "title": "T", "question": "q", "box": box, "due": day(due),
         "history": ["%s 10:00:%02d %s" % (day(-30 + i), i, m) for i, m in enumerate(history)]}
    if sure:
        r["sure"] = list(sure)
    if idea:
        r["idea"] = idea
    return r


def test_priority():
    private = os.path.join(TMP, "p-prio")
    inproc(private)
    items = [item("plain", section="1.1"), item("overdue", section="1.2"), item("box1", section="1.3"),
             item("surewrong", section="1.4"), item("missed2", section="1.5"), item("needed", section="1.6", importance=2),
             item("future", section="1.7")]
    st = {"plain": rec(due=0), "overdue": rec(due=-20), "box1": rec(box=1, due=0, history=("y", "p")),
          "surewrong": rec(box=1, due=0, history=("y", "n"), sure=(1,)), "missed2": rec(box=1, due=-7, history=("n", "n", "y", "p")),
          "needed": rec(due=-1), "future": rec(due=1)}
    got = [i["key"] for i in up.pick(items, st, 10, True)]
    # missed2: 6 + 1 + 1 = 8; surewrong: 3 + 2 + 1 = 6; needed: 1/7 + 2; overdue: 2; box1: 1; plain: 0; future: not due
    check("priority: misses, then the sure-wrong one, importance, days overdue, box 1, nothing",
          got == ["missed2", "surewrong", "needed", "overdue", "box1", "plain"], got)
    check("priority: the sure-wrong item comes before an item missed once but not sure",
          [i["key"] for i in up.pick([item("a", section="1.1"), item("b", section="1.2")],
                                     {"a": rec(box=1, history=("y", "n")), "b": rec(box=1, history=("y", "n"), sure=(1,))}, 2, True)]
          == ["b", "a"])
    ws = {"old": rec(), "fresh": rec()}
    ws["fresh"]["history"].append("%s 09:00:00 y" % day(-2))   # its idea was asked two days ago
    got = [i["key"] for i in up.pick([item("fresh", section="1.1"), item("old", section="1.2")], ws, 2, True)]
    check("equal priority: an idea not asked in the last 3 days first", got == ["old", "fresh"], got)
    again = [[i["key"] for i in up.pick(items, st, 10, True)] for _ in range(3)]
    check("same files and date, same order", again[0] == again[1] == again[2])


def test_balance_variety():
    inproc(os.path.join(TMP, "p-bal"))
    items = [item("a%d" % k, book="A", section="1.%d" % k) for k in range(8)] + \
            [item("b%d" % k, book="B", section="1.%d" % k) for k in range(2)]
    st = {i["key"]: rec(book=i["book"], section=i["section"], due=-5 if i["book"] == "A" else 0) for i in items}
    got = [i["book"] for i in up.pick(items, st, 5, True)]
    check("balance: no book over 60%% (3 of 5) while another has due items", got.count("A") == 3 and got.count("B") == 2, got)
    items = items[:9]
    got = [i["book"] for i in up.pick(items, st, 5, True)]
    check("balance: once the other book has nothing waiting, the first may take more", got.count("A") == 4 and got.count("B") == 1, got)
    items = [item("s1-%d" % k, section="1.1") for k in range(3)] + [item("s2", section="1.2"), item("s3", section="1.3")]
    st = {i["key"]: rec(section=i["section"], due=-10 if i["section"] == "1.1" else 0) for i in items}
    got = [i["section"] for i in up.pick(items, st, 3, True)]
    check("variety: no second item from a section while another due section waits", sorted(got) == ["1.1", "1.2", "1.3"], got)
    got = [i["section"] for i in up.pick(items, st, 5, True)]
    check("variety: a section repeats only when no other due section is left", got.count("1.1") == 3 and len(got) == 5, got)


def test_new_material():
    inproc(os.path.join(TMP, "p-new"))
    due = [item("d%d" % k, section="1.%d" % k) for k in range(10)]
    new = [item("n%d" % k, section="2.%d" % k, chapter=2) for k in range(10)]
    st = {i["key"]: rec(section=i["section"]) for i in due}
    got = [i["key"][0] for i in up.pick(due + new, st, 5)]
    check("60%% rule: 3 due of 5, then new questions from the newest chapter", got == list("dddnn"), got)
    got = [i["key"] for i in up.pick(due + new, st, 5)]
    check("new questions come in book order", got[3:] == ["n0", "n1"], got)
    check("--due: only due items", [i["key"][0] for i in up.pick(due + new, st, 5, True)] == list("ddddd"))
    old_new = [item("n%d" % k, section="0.%d" % k, chapter=0) for k in range(2)]
    got = [i["key"][0] for i in up.pick(due + old_new + [item("zz", chapter=1)], dict(st, zz=rec()), 5)]
    check("nothing new in the newest chapter: due items may fill it all", got == list("ddddd"), got)
    got = [i["key"][0] for i in up.pick(due + new[:1], st, 5)]
    check("only one new question: due items take the rest", got == list("ddddn"), got)


def test_minutes_and_boxes():
    book = small_book("mins")
    private = os.path.join(TMP, "p-min")
    code, out = run("us_practice.py", book, "--plain", "--minutes", 6, e=env(private))
    check("--minutes 6: 4 questions", "[4/4]" in out, out[:300])
    code, out = run("us_practice.py", book, "--plain", "--minutes", 1, e=env(private))
    check("--minutes 1: at least 3", "[3/3]" in out, out[:300])
    code, out = run("us_practice.py", book, "--plain", e=env(private))
    check("default count stays 10 (the book has 8)", "[8/8]" in out, out[:300])

    inproc(private)
    st, q = {}, item("x")
    up.mark(st, q, "y", sure=True)
    check("right and sure on a new question: box 3, due in 7 days", (st["x"]["box"], st["x"]["due"]) == (3, day(7)), st["x"])
    st["x"]["box"] = 5
    up.mark(st, q, "y")
    check("box 6 is 60 days", (st["x"]["box"], st["x"]["due"]) == (6, day(60)) and up.DAYS[6] == 60, st["x"])
    up.mark(st, q, "y", sure=True)
    check("never past box 6", st["x"]["box"] == 6, st["x"])
    st["x"]["box"] = 5
    up.mark(st, q, "y", sure=True)
    check("box 5, right and sure: box 6", st["x"]["box"] == 6)
    up.mark(st, q, "n", sure=True)
    check("wrong and sure: box 1, remembered as sure-wrong", st["x"]["box"] == 1 and up.sure_wrong(st["x"]), st["x"])
    code, out = run("us_practice.py", "record", book, "1.2", "right", "--sure", e=env(private))
    check("record right --sure: two boxes up (box 3)", store(private)["mins/1.2/lesson"]["box"] == 3, out)
    answers = os.path.join(TMP, "ans-min")
    open(answers, "w").write("y!\nn!\np\nq\n")
    run("us_practice.py", book, "--answer-file", answers, e=env(private))
    data = store(private)
    k1, k2 = sorted(k for k in data if "/q" in k)[:2]
    check("session: y! moves two boxes, n! is kept as sure-wrong",
          data[k1]["box"] == 3 and up.sure_wrong(data[k2]) and data[k2]["idea"] == "alpha", (data[k1], data[k2]))
    code, out = run("us_practice.py", "--stats", e=env(private))
    check("stats: six box columns", "box6" in out and "cards: 0 seen, 0 due" in out, out)


def test_old_store():
    book = small_book("old")
    private = os.path.join(TMP, "p-old")
    os.makedirs(private)
    keys = [q["key"] for q in up.book_questions(book)]
    old = {keys[0]: {"book": "old", "section": "1.1", "title": "Alpha", "question": "What is alpha?", "box": 5,
                     "due": day(-1), "history": ["%s 10:00:00 y" % day(-40)]},
           keys[1]: {"book": "old", "section": "1.1", "title": "Alpha", "question": "x", "box": 1,
                     "due": day(0), "history": ["%s 10:00:00 n" % day(-1)]},
           "old/1.2/lesson": {"book": "old", "section": "1.2", "title": "Gamma", "question": "answers given in a lesson or check",
                              "box": 2, "due": day(3), "history": ["%s 10:00:00 y" % day(0)]}}
    json.dump(old, open(os.path.join(private, "practice.json"), "w"))
    code, out = run("us_practice.py", book, "--due", "--plain", e=env(private))
    check("old practice.json: due items still come, the missed one first", code == 0 and "[1/2]" in out and
          out.index("What does the alpha line print?") < out.index("What is alpha?"), out)
    for args in (("--stats",), ("--summary", book), ("record", book, "1.1", "no")):
        code, out = run("us_practice.py", *args, e=env(private))
        check("old practice.json: %s works" % args[0], code == 0 and "Traceback" not in out, out)
    open(os.path.join(TMP, "ans-old"), "w").write("y\ny\n")
    code, out = run("us_practice.py", book, "--due", "--answer-file", os.path.join(TMP, "ans-old"), e=env(private))
    data = store(private)
    check("old practice.json: a session marks old records and adds idea and type", code == 0 and data[keys[0]]["box"] == 6 and
          data[keys[0]].get("idea") == "alpha" and data[keys[0]].get("type") == "recall", data[keys[0]])

# ---------------------------------------------------------------- B3 cards


def test_cards():
    book = small_book("cards")
    private = os.path.join(TMP, "p-cards")
    code, out = run("us_practice.py", "--cards", book, "--plain", "--answers", e=env(private))
    terms = re.findall(r"^(alpha|beta|gamma|delta)$", out, re.M)
    check("cards: one per defined key term, in book order", code == 0 and terms == ["alpha", "gamma", "delta"], out)
    check("cards: the front says where it is from, the back is the definition",
          "key term from §1.1 Alpha" in out and "A alpha is the thing called alpha in this small test book." in out and
          "card · Test Book · §1.1" in out, out)
    check("cards: a term with no definition is skipped", "beta" not in out)
    answers = os.path.join(TMP, "ans-cards")
    open(answers, "w").write("y\nn\np\n")
    code, out = run("us_practice.py", "--cards", book, "--answer-file", answers, e=env(private))
    data = store(private)
    check("cards: marked y/p/n into boxes, keys start card/",
          sorted(data) == ["card/cards/1.1/alpha", "card/cards/1.2/gamma", "card/cards/2.1/delta"] and
          [data[k]["box"] for k in sorted(data)] == [2, 1, 1], data)
    code, out = run("us_practice.py", "--cards", book, "--due", "--plain", e=env(private, 1))
    check("cards --due tomorrow: the two not right", "[2/2]" in out and "gamma" in out and "delta" in out, out)
    open(answers, "w").write("y\n" * 3)
    run("us_practice.py", book, "--count", 3, "--answer-file", answers, e=env(private))
    code, out = run("us_practice.py", book, "--due", "--plain", "--count", 20, e=env(private, 3))
    check("--due: due questions and due cards together (3 of each)",
          "[6/6]" in out and out.count("card · ") == 3 and "What is alpha?" in out, out)
    code, out = run("us_practice.py", "--stats", e=env(private, 1))
    check("stats: cards seen and due", "cards: 3 seen, 2 due" in out and "card/" not in out, out)
    code, out = run("us_practice.py", "--cards", book, "--plain", e=env(private, 1))
    check("--cards without --due: due cards first", out.count("card · ") == 2, out)

# ---------------------------------------------------------------- B4 summary


def hist(*marks, start=-20):
    return ["%s 10:00:00 %s" % (day(start + i), m) for i, m in enumerate(marks)]


def test_summary():
    book = small_book("sum")
    private = os.path.join(TMP, "p-sum")
    os.makedirs(private)
    keys = {(q["section"], q["type"]): q["key"] for q in up.book_questions(book)}
    st = {
        keys[("1.1", "recall")]: {"book": "sum", "section": "1.1", "title": "Alpha", "question": "q", "box": 2, "due": day(3),
                                  "history": hist("y"), "idea": "alpha", "type": "recall"},
        keys[("1.1", "predict")]: {"book": "sum", "section": "1.1", "title": "Alpha", "question": "q", "box": 1, "due": day(1),
                                   "history": hist("y", "n", "p", "n"), "idea": "alpha", "type": "predict",
                                   "wrong": "alpha is beta", "sure": [3]},
        keys[("1.2", "explain")]: {"book": "sum", "section": "1.2", "title": "Gamma", "question": "q", "box": 3, "due": day(3),
                                   "history": hist("y", "y"), "idea": "gamma", "type": "explain"},
        keys[("2.1", "fix")]: {"book": "sum", "section": "2.1", "title": "Delta", "question": "q", "box": 4, "due": day(9),
                               "history": hist("y", "y", "y"), "idea": "delta", "type": "fix"},
        "check/sum/2.1/delta-prog": {"book": "sum", "section": "2.1", "title": "Delta", "question": "self-test", "box": 2,
                                     "due": day(3), "history": [day(-1) + " 10:00:00 y"], "idea": "delta", "type": "build"},
    }
    json.dump(st, open(os.path.join(private, "practice.json"), "w"))
    code, out = run("us_practice.py", "--summary", book, e=env(private))
    lines = out.splitlines()
    path = os.path.join(private, "learner.md")
    check("summary: printed and written to learner.md, 15 lines at most", code == 0 and read(path) == out and len(lines) <= 15, out)
    body = [l for l in lines if l.startswith("- ")]
    want = ['- Wrong belief that keeps returning: "alpha is beta" (§1.1, missed 2, 1 while sure)',
            "- Weak foundation: alpha (missed 2 of the last 5); §1.2 Gamma, §2.1 Delta lean on it",
            "- Can explain, cannot yet apply: alpha (last: wrong), gamma (never tried)",
            "- Solid: 1 idea applied well (delta)",
            "- Applied alone: delta-prog (§2.1, %s)" % day(-1),
            "- Not yet practised: 1 section"]
    for k, w in enumerate(want):
        check("summary line %d: %s" % (k + 1, w.split(":")[0][2:]), body[k:k + 1] == [w], body)
    st[keys[("1.1", "predict")]]["history"] = hist("y", "n")
    st[keys[("1.1", "predict")]]["sure"] = []
    json.dump(st, open(os.path.join(private, "practice.json"), "w"))
    code, out = run("us_practice.py", "--summary", book, e=env(private))
    check("summary: one miss, not sure: no wrong-belief line, no weak foundation", "Wrong belief" not in out and
          "Weak foundation" not in out and "alpha (last: wrong)" in out, out)
    st[keys[("1.1", "predict")]]["sure"] = [1]
    json.dump(st, open(os.path.join(private, "practice.json"), "w"))
    code, out = run("us_practice.py", "--summary", book, e=env(private))
    check("summary: one miss while sure is a wrong belief", '"alpha is beta" (§1.1, missed 1, 1 while sure)' in out, out)
    code, out = run("us_resume.py", book, e=env(private))
    note = read(os.path.join(private, "RESUME.md"))
    part = note.split("## Weak spots", 1)[-1].split("\n## ", 1)[0]
    check("RESUME.md carries the summary under its weak spots", "Wrong belief that keeps returning" in part and
          "Applied alone: delta-prog" in part and len(note.split()) < 250, note)
    empty = os.path.join(TMP, "p-sum-empty")
    code, out = run("us_practice.py", "--summary", book, e=env(empty))
    check("summary with nothing practised", code == 0 and "- Not yet practised: 4 sections" in out, out)

# ---------------------------------------------------------------- B5 self-test

CHECK_BOOK_HEAD = ("mask: took \\d+ms",)


def program(bid, attrs, code, output, hidden=True):
    """A model answer: inside the hidden answer (hidden) or above it, with `answer`."""
    prog = ["<!-- code: id=%s %s -->" % (bid, attrs), "```python"] + code + ["```", ""]
    out = ["```text"] + output + ["```", ""]
    if hidden:
        return ["<details>", "<summary>Answer</summary>", ""] + prog + out + ["</details>", ""]
    return prog + ["<details>", "<summary>Answer</summary>", ""] + out + ["</details>", ""]


def test_check():
    greet = ["name = input()", "print('Hello,', name)  ", "print('took 3ms')", "print('Bye,', name)"]
    s11 = section("1.1", "Alpha", [("alpha", "alpha", True)], [("<!-- q: idea=alpha type=recall -->", "What?", "That.")])
    s12 = ["## 1.2 Practice: greet", "", "<!-- q: idea=alpha type=build -->",
           "**Exercise 1.** Write `greet.py`: read a name, greet it, say goodbye.", ""] + \
        program("greet", 'check="python3 greet.py" stdin="Ann\\n"', greet, ["Hello, Ann", "took 3ms", "Bye, Ann"]) + \
        ["<!-- q: idea=alpha type=build -->", "**Exercise 2.** Write `count.py`: print the arguments, one a line.", ""] + \
        program("count", 'answer check="python3 count.py" args="x y"', ["import sys", "for a in sys.argv[1:]:", "    print(a)"],
                ["x", "y"], hidden=False)
    s13 = ["## 1.3 Practice: slow", "", "<!-- q: idea=alpha type=build -->", "**Exercise 1.** Make it wait.", ""] + \
        program("slow", 'check="python3 slow.py" timeout=1', ["print('done')"], ["done"]) + \
        ["<!-- q: idea=alpha type=build -->", "**Exercise 2.** Clean up.", ""] + \
        program("wipe", 'check="sudo rm -rf build"', ["print('ok')"], ["ok"])
    s14 = ["## 1.4 Practice: nothing", "", "**Exercise 1.** Think.", "", "<details>", "<summary>Answer</summary>", "",
           "Done.", "", "</details>", ""]
    s15 = ["## 1.5 Practice: plan", "", "<!-- q: idea=alpha type=build -->", "**Exercise 1.** Write a first test plan.", "",
           "<details>", "<summary>Answer</summary>", "", "A plan.", "", "</details>", "",
           "<!-- checklist: id=first-test -->", "- Does every task give a goal, not steps?", "- Is there a time limit?",
           "- Did someone else read it?", ""]
    book = make_book("chk", "Check Book", [(1, "Projects", [
        ("1.1", "Alpha", "teaches: alpha", s11), ("1.2", "Practice: greet", "practice", s12),
        ("1.3", "Practice: slow", "practice", s13), ("1.4", "Practice: nothing", "practice", s14),
        ("1.5", "Practice: plan", "practice", s15)])], head=CHECK_BOOK_HEAD)
    private, mine = os.path.join(TMP, "p-chk"), os.path.join(TMP, "mine")
    os.makedirs(mine)
    open(os.path.join(mine, "greet.py"), "w").write("n = input()\nprint('Hello,', n)\nprint('took 41ms')\nprint('Bye,', n)\n")
    open(os.path.join(mine, "count.py"), "w").write("import sys\nprint('\\n'.join(sys.argv[1:]))\n")
    code, out = run("us_practice.py", "check", book, "1.2", "--in", mine, e=env(private))
    check("check PASS: own programs, same stdin and args, trailing spaces cut, mask: applied",
          code == 0 and "PASS greet" in out and "PASS count" in out and "2 of 2 passed" in out, out)
    check("check PASS: nothing of the model answer shown", "input()" not in out and "Hello, Ann" not in out, out)
    data = store(private)
    check("check PASS: recorded under check/<book>/<N.M>/<id>",
          data.get("check/chk/1.2/greet", {}).get("history", [""])[-1].endswith(" y") and "check/chk/1.2/count" in data, sorted(data))
    check("check PASS: the level line, as record right does", "levels.yaml: added the line `chk/1: {level: 1" in out and
          "chk/1:" in read(os.path.join(private, "levels.yaml")), out)
    check("check PASS: learner.md has the Applied alone line",
          "- Applied alone: count (§1.2, %s), greet (§1.2, %s)" % (day(0), day(0)) in read(os.path.join(private, "learner.md")),
          read(os.path.join(private, "learner.md")))
    open(os.path.join(mine, "greet.py"), "w").write("n = input()\nprint('Hello,', n)\nprint('took 1ms')\nprint('Bye', n)\n")
    code, out = run("us_practice.py", "check", book, "1.2", "--in", mine, e=env(private, 1))
    check("check FAIL: the first line that differs, expected and got, exit 1",
          code == 1 and "FAIL greet: line 3 differs\n  expected: Bye, Ann\n  got:      Bye Ann" in out and "PASS count" in out, out)
    check("check FAIL: recorded with its history", store(private)["check/chk/1.2/greet"]["history"][-1].endswith(" n") and
          len(store(private)["check/chk/1.2/greet"]["history"]) == 2)
    open(os.path.join(mine, "slow.py"), "w").write("while True:\n    pass\n")
    code, out = run("us_practice.py", "check", book, "1.3", "--in", mine, e=env(private))
    check("check: a program that never ends fails at the block's timeout", code == 1 and "FAIL slow: still running after 1 seconds" in out, out)
    check("check: a dangerous command is refused, not run", "REFUSED wipe: `sudo rm -rf build` looks dangerous" in out, out)
    code, out = run("us_practice.py", "check", book, "1.4", "--in", mine, e=env(private))
    check("check: a section with nothing to check says so, exit 1", code == 1 and "nothing to check" in out, out)
    answers = os.path.join(TMP, "ans-chk")
    open(answers, "w").write("y\ny\ny\n")
    code, out = run("us_practice.py", "check", book, "1.5", "--answer-file", answers, e=env(private))
    check("checklist: all yes is a PASS", code == 0 and "PASS first-test" in out and "Is there a time limit? (y/n) y" in out, out)
    open(answers, "w").write("y\nn\ny\n")
    code, out = run("us_practice.py", "check", book, "1.5", "--answer-file", answers, e=env(private))
    check("checklist: one no is a FAIL", code == 1 and "FAIL first-test" in out and
          store(private)["check/chk/1.5/first-test"]["history"][-1].endswith(" n"), out)
    proc = subprocess.Popen([sys.executable, os.path.join(SCRIPTS, "us_practice.py"), "check", book, "1.5"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            env=env(private))       # stdin a pipe left open: nobody there, it must not wait
    try:
        out, code = proc.communicate(timeout=20)[0], proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        out, code = "hung waiting for y/n", None
    check("checklist with no terminal: printed to check by hand, no waiting",
          code == 0 and "  check by hand: Is there a time limit?" in out and "(y/n)" not in out, out)
    os.makedirs(os.path.join(TMP, "cwd"))
    open(os.path.join(TMP, "cwd", "count.py"), "w").write("import sys\nprint('\\n'.join(sys.argv[1:]))\n")
    open(os.path.join(TMP, "cwd", "greet.py"), "w").write(read(os.path.join(mine, "greet.py")))
    code, out = run("us_practice.py", "check", book, "1.2", e=env(private), cwd=os.path.join(TMP, "cwd"))
    check("check: with no --in, the current folder", "PASS count" in out, out)

# ---------------------------------------------------------------- the 30-day simulation


def sim_book(slug, title):
    """Two chapters of three sections, two tagged questions each; 1.1 teaches the idea the others need."""
    chapters = []
    for c in (1, 2):
        secs = []
        for s in (1, 2, 3):
            num, idea = "%d.%d" % (c, s), "%s-i%d%d" % (slug, c, s)
            lines = section(num, "S%s" % num, [(idea, "w%s%d%d" % (slug, c, s), True)], [
                ("<!-- q: idea=%s type=recall -->" % idea, "%s %s recall?" % (slug, num), "a"),
                ("<!-- q: idea=%s type=apply -->" % idea, "%s %s apply?" % (slug, num), "b")])
            needs = "" if (c, s) == (1, 1) else " | needs: %s-i11" % slug
            secs.append((num, "S%s" % num, "teaches: %s%s" % (idea, needs), lines))
        chapters.append((c, "C%d" % c, secs))
    return make_book(slug, title, chapters)


def test_simulation():
    books = [sim_book("sa", "Book A"), sim_book("sb", "Book B"), sim_book("sc", "Book C")]
    private = os.path.join(TMP, "p-sim")
    items = [q for b in books for q in up.book_questions(b)]
    st, count, flip, asked_days, bad = {}, 6, [0], {"sa": [], "sb": [], "sc": []}, []
    sure_idea = "sc-i11"

    def answer(q):
        if q["book"] == "sa":
            return "y", False
        if q["book"] == "sb":
            flip[0] += 1
            return ("n" if flip[0] % 2 else "y"), False
        return ("n", True) if q["idea"] == sure_idea and q["type"] == "apply" else ("y", False)
    due_days = {b: [] for b in asked_days}
    for d in range(30):
        inproc(private, d)
        now = day(d)
        due = [q for q in items if q["key"] in st and st[q["key"]]["due"] <= now]
        chosen = up.pick(items, st, count)
        keys = {q["key"] for q in chosen}
        if len(chosen) > count:
            bad.append("day %d: %d asked" % (d, len(chosen)))
        for b in asked_days:
            due_days[b].append(any(q["book"] == b for q in due))
            asked_days[b].append(any(q["book"] == b for q in chosen))
        for q in due:
            if up.sure_wrong(st[q["key"]]) and st[q["key"]]["due"] == now and q["key"] not in keys:
                bad.append("day %d: sure-wrong %s due today, not asked" % (d, q["key"]))
        due_chosen = [q for q in chosen if q in due]
        secs = [(q["book"], q["section"]) for q in due_chosen]
        per_book = {b: sum(1 for q in due_chosen if q["book"] == b) for b in asked_days}
        cap = -(-count * 6 // 10)
        waiting = {(q["book"], q["section"]) for q in due if q["key"] not in keys and per_book[q["book"]] < cap}
        if len(secs) != len(set(secs)) and waiting - set(secs):
            bad.append("day %d: a section twice while %s waits" % (d, sorted(waiting - set(secs))))
        for q in chosen:
            m, sure = answer(q)
            up.mark(st, q, m, sure)
    for b in asked_days:
        run_ = 0
        for k in range(30):
            run_ = run_ + 1 if due_days[b][k] and not asked_days[b][k] else 0
            if run_ >= 7:
                bad.append("%s unasked a full week with due items (to day %d)" % (b, k))
                break
    seen = {q["key"] for q in items if q["key"] in st}
    check("simulation: 30 days, 3 books: every question met, every rule kept", not bad and len(seen) == len(items),
          (bad[:5], len(seen), len(items)))
    sure = [r for r in st.values() if r.get("idea") == sure_idea and r.get("type") == "apply"]
    every = [len(r["history"]) == (TODAY + datetime.timedelta(days=29) - datetime.date.fromisoformat(r["history"][0][:10])).days + 1
             for r in sure]
    check("simulation: the sure-wrong idea is asked every day once it has been met", sure and all(every),
          [(r["history"][0][:10], len(r["history"])) for r in sure])
    a = [r for r in st.values() if r["book"] == "sa"]
    check("simulation: book A, always right, climbs to box 4 or more", min(r["box"] for r in a) >= 4, [r["box"] for r in a])
    lines = up.summary_lines(books, st)
    check("simulation: the summary names the idea answered wrong while sure as a weak foundation",
          any(l.startswith("- Weak foundation: sc-i11") for l in lines), lines)


def main():
    test_tags()
    test_priority()
    test_balance_variety()
    test_new_material()
    test_minutes_and_boxes()
    test_old_store()
    test_cards()
    test_summary()
    test_check()
    test_simulation()
    passed = sum(RESULTS)
    print("%d passed, %d failed" % (passed, len(RESULTS) - passed))
    shutil.rmtree(TMP, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
