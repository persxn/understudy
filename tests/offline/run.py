"""Offline mode: practice with no AI, the resume note, and autopilot with a fake agent.

    python3 tests/offline/run.py

Everything runs on temp copies: the fixture book, the real 11-chapter book (if
$JOJO_CHAPTERS is set), and a temp private folder.
One line per test, then "N passed, M failed"; exit 1 on any failure.
"""
import datetime
import hashlib
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
FIXTURE = os.path.join(ROOT, "tests", "book", "fixture")
JOJO = os.environ.get("JOJO_CHAPTERS", "")
TMP = tempfile.mkdtemp(prefix="us-offline-")
os.chmod(TMP, 0o755)
os.environ["TMPDIR"] = tempfile.tempdir = TMP  # run folders go in TMP too, and leave with it
TODAY = datetime.date.today()
RESULTS = []


def env(private, **extra):
    fake = "%s %s {prompt}" % (sys.executable, os.path.join(HERE, "fake_agent.py"))
    e = dict(os.environ, UNDERSTUDY_PRIVATE=private, UNDERSTUDY_AUTOPILOT_WRITER=fake,
             UNDERSTUDY_AUTOPILOT_REVIEWER=fake, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
             GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    e.pop("UNDERSTUDY_TODAY", None)
    e.update(extra)
    return e


def run(script, *args, e=None):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + [str(a) for a in args],
                       capture_output=True, text=True, env=e)
    return p.returncode, p.stdout + p.stderr


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("pass  " if ok else "FAIL  ") + name + ("" if ok else ": " + str(detail).replace("\n", " | ")[:300]))


def snapshot(folder):
    """Hash of every file's path and bytes under folder."""
    h = hashlib.sha1()
    for d, _, files in sorted(os.walk(folder)):
        for f in sorted(files):
            h.update(os.path.join(d, f).encode() + open(os.path.join(d, f), "rb").read())
    return h.hexdigest()


def prose_too_wide(text):
    """Lines over 80 columns outside code fences."""
    bad, fence = [], False
    for line in text.splitlines():
        if re.match(r"\s*(```|~~~)", line):
            fence = not fence
        elif not fence and len(line) > 80 and not line.lstrip().startswith("|"):
            bad.append(line)
    return bad


def day(n):
    return (TODAY + datetime.timedelta(days=n)).isoformat()


def store(private):
    return json.load(open(os.path.join(private, "practice.json")))


def words(path):
    return len(open(path).read().split())


def test_practice():
    book, private = os.path.join(TMP, "fx"), os.path.join(TMP, "p1")
    shutil.copytree(FIXTURE, book)
    e = env(private)
    before = snapshot(book)
    code, out = run("us_practice.py", book, "--plain", "--answers", "--count", 50, e=e)
    n = open(os.path.join(book, "chapters", "01-first-steps.md")).read().count("<details>")
    check("plain lists all %d fixture questions with their answers" % n,
          "[%d/%d]" % (n, n) in out and out.count("Answer:") == n, out[:200])
    check("plain output says where each question is from", "Tiny C · §1.2 Printing a line" in out, out[:200])
    check("plain output has no hidden markers or HTML", not re.search(r"<!--|<details>|<summary>|\*\*", out), out)
    check("plain output fits 80 columns", not prose_too_wide(out), prose_too_wide(out))
    check("plain writes nothing at all", not os.path.exists(private))

    answers = os.path.join(TMP, "answers")
    open(answers, "w").write("y\nn\np\ny\nn\nq\n")
    code, out = run("us_practice.py", book, "--answer-file", answers, e=e)
    data = store(private)
    check("session records 5 marks and stops at q", code == 0 and len(data) == 5 and "2 right, 1 partly, 2 missed" in out, out[-300:])
    q1, q2, q3 = (data[k] for k in sorted(data)[:3])
    check("right: box 2, due in 3 days", (q1["box"], q1["due"]) == (2, day(3)), q1)
    check("wrong: box 1, due tomorrow", (q2["box"], q2["due"]) == (1, day(1)), q2)
    check("history holds the date and the mark", q2["history"][0].startswith(TODAY.isoformat()) and q2["history"][0].endswith(" n"), q2)
    check("key is book/section/number/hash", re.match(r"^fx/1\.2/q1/[0-9a-f]{8}$", sorted(data)[0]), sorted(data)[0])
    check("session ends by writing the resume note", "resume note written:" in out and os.path.exists(os.path.join(private, "RESUME.md")), out[-200:])

    code, out = run("us_practice.py", book, "--due", e=e)
    check("nothing due today after the session", "nothing is due today" in out, out)
    later = env(private, UNDERSTUDY_TODAY=day(1))
    code, out = run("us_practice.py", book, "--due", "--plain", e=later)
    check("tomorrow: the 3 missed or partly ones are due, nothing new", out.count("[") == 3 and "[3/3]" in out and "new" not in out, out[:300])
    open(answers, "w").write("y\ny\ny\n")
    run("us_practice.py", book, "--due", "--answer-file", answers, e=later)
    data = store(private)
    check("right on a box-1 question moves it to box 2, due 3 days on", data[sorted(data)[1]]["box"] == 2 and data[sorted(data)[1]]["due"] == (TODAY + datetime.timedelta(days=4)).isoformat(), data[sorted(data)[1]])
    code, out = run("us_practice.py", book, "--due", "--plain", "--count", 10, e=env(private, UNDERSTUDY_TODAY=day(3)))
    check("three days on: the first right answer comes back", "[1/" in out and "§1.2 Printing a line · box 2" in out, out[:300])
    code, out = run("us_practice.py", book, "--plain", "--count", 3, e=later)
    check("default run fills up with new questions in book order", out.count("· new") == 3, out[:300])

    chapter = os.path.join(book, "chapters", "01-first-steps.md")
    text = open(chapter).read()
    open(chapter, "w").write(text.replace("2. What happens in step 2 of the trace?", "2. What does line 4 do?", 1))
    open(answers, "w").write("q\n")
    run("us_practice.py", book, "--answer-file", answers, e=env(private, UNDERSTUDY_TODAY=day(1)))
    data = store(private)
    check("an edited question starts fresh", not any(k.startswith("fx/1.2/q2/") for k in data) and len(data) == 4, sorted(data))
    code, out = run("us_practice.py", book, "--plain", "--count", 50, e=env(private, UNDERSTUDY_TODAY=day(1)))
    check("the edited question is offered as new", "2. What does line 4 do?" in out, out[:400])
    code, out = run("us_practice.py", "--stats", e=e)
    check("stats: a row per chapter with boxes and percent right", re.search(r"fx\s+1\s+4\s+0\s+4\s+0\s+0\s+0\s+\d+%", out), out)
    check("stats: weak spots name the sections", "weak spots:" in out and "§1.3 Variables (missed 1)" in out, out)
    rows = [l for l in out.splitlines() if re.match(r"  fx §1\.\d .* due ", l)]
    check("stats: a row per practised section with times, lowest box and next due",
          "sections practised (times, lowest box, next due):" in out and len(rows) == 2 and
          rows[0].startswith("  fx §1.2 Printing a line ") and
          re.search(r"fx §1\.3 Variables\s+3x  box 2  due %s$" % day(3), rows[1]), out)
    big = os.path.join(TMP, "p-stats")
    os.makedirs(big)
    json.dump({"b/%d.%d/q1/x" % (c, k): {"book": "b", "section": "%d.%d" % (c, k), "title": "T", "question": "q", "box": 2,
                                         "due": day(c + k), "history": ["%s 10:00:00 y" % TODAY]}
               for c in range(1, 7) for k in range(1, 11)}, open(os.path.join(big, "practice.json"), "w"))
    code, out = run("us_practice.py", "--stats", e=env(big))
    lines = out.rstrip("\n").splitlines()
    check("stats: 60 sections fit in 25 lines, soonest due first, the rest counted",
          len(lines) == 25 and lines[-1].startswith("  ... ") and lines[-1].endswith(" more") and "b §1.1 T" in out, lines)
    open(chapter, "w").write(text)
    check("practice never writes into the book", snapshot(book) == before, os.listdir(book))
    return book, private


def test_route(book, private):
    e = env(private)
    route = os.path.join(private, "route.md")
    open(route, "w").write("- printf@1\n- fx 2 choices first\n- fx 1 basics · skip\n")
    code, out = run("us_resume.py", book, e=e)
    note = open(os.path.join(private, "RESUME.md")).read()
    check("resume names the skipped chapters", "written 1, reviewed none, skipped 1; next to write: chapter 2, §2.1" in note, note)
    ap, _, ap_private = make_autopilot_book("ap-route")
    for text, want in (("- tiny 2 first\n- tiny 1 then\n", [2, 1]), ("- tiny 1 · skip\n", [2]), (None, [1, 2])):
        os.makedirs(ap_private, exist_ok=True)
        if text:
            open(os.path.join(ap_private, "route.md"), "w").write(text)
        else:
            os.remove(os.path.join(ap_private, "route.md"))
        code, out = run("us_autopilot.py", ap, "--dry-run", "--no-review", e=env(ap_private))
        got = [int(n) for n in re.findall(r"chapter (\d+)\.", out)]
        check("autopilot dry run follows the route %r: chapters %s" % (text, want), got == want, out)
    os.remove(route)


def test_resume(book, private):
    for name, text in (("now.md", "Stopped in §1.3, mid trace.\n"), ("goal.md", "goal: I can write small C programs\n"),
                       ("route.md", "- printf@1\n- variable@2\n"), ("levels.yaml", "printf: {level: 1, state: proven}\n")):
        open(os.path.join(private, name), "w").write(text)
    e = env(private)
    before = snapshot(book)
    code, out = run("us_resume.py", book, e=e)
    path = os.path.join(private, "RESUME.md")
    note = open(path).read()
    check("resume prints one line", out.strip().count("\n") == 0 and out.startswith("resume note written: "), out)
    check("resume says where you are", "Tiny C (2 chapters): written 1" in note and "next to write: chapter 2, §2.1" in note and
          "Last practised: §1.3" in note, note)
    check("resume uses now.md, goal.md and the route", "Stopped in §1.3" in note and "small C programs" in note and "variable@2" in note, note)
    check("resume gives today's work and the commands", "us_reader.py --serve" in note and "us_practice.py" in note and
          re.search(r"\d+ questions? due today, \d+ new", note), note)
    check("resume lists weak spots and the sentence to start with", "§1.3 Variables (missed 1)" in note and
          "start with this sentence:" in note and "> I'm back" in note, note)
    check("fixture note is under 250 words (%d)" % words(path), words(path) < 250)
    mtime = os.path.getmtime(path)
    run("us_resume.py", book, e=e)
    check("resume is idempotent", open(path).read() == note and os.path.getmtime(path) == mtime)
    check("resume writes nothing into the book", snapshot(book) == before)
    return note


def test_real_book():
    if not JOJO:
        print("skip  real book: JOJO_CHAPTERS not set")
        return 0
    if not os.path.isdir(JOJO):
        check("real book present at %s" % JOJO, False)
        return 0
    book, private = os.path.join(TMP, "jojo"), os.path.join(TMP, "p2")
    os.makedirs(book)
    shutil.copytree(JOJO, os.path.join(book, "chapters"))
    run("us_plan.py", "from-chapters", book)
    e = env(private)
    code, out = run("us_practice.py", book, "--plain", "--answers", "--count", 10000, e=e)
    n = len(re.findall(r"^\[\d+/\d+\] ", out, re.M))
    details = sum(open(os.path.join(book, "chapters", f)).read().count("<details>") for f in os.listdir(os.path.join(book, "chapters")) if f.endswith(".md"))
    check("real book: every hidden answer is a question (%d of %d)" % (n, details), n == details and n > 400)
    check("real book: plain prose fits 80 columns", not prose_too_wide(out), prose_too_wide(out)[:3])
    check("real book: no hidden markers shown", "<!--" not in out and "<details>" not in out)
    open(os.path.join(TMP, "a2"), "w").write("y\nn\n")
    run("us_practice.py", book, "--chapter", 8, "--answer-file", os.path.join(TMP, "a2"), e=e)
    run("us_resume.py", book, e=e)
    path = os.path.join(private, "RESUME.md")
    note = open(path).read()
    check("real book note is under 250 words (%d)" % words(path), words(path) < 250)
    check("real book note: all written, reading chapter 8 and 9", "written 1-11" in note and "all written" in note and
          "Read chapter 8, Pointers" in note and "then chapter 9" in note, note)
    check("real book note: the sentence points at §8.1", re.search(r"> I'm back.*§8\.1 ", note), note)
    return n


def make_autopilot_book(name):
    root = os.path.join(TMP, name, "books")
    book, src = os.path.join(root, "tiny"), os.path.join(TMP, name, "src")
    os.makedirs(book)
    shutil.copy(os.path.join(FIXTURE, "PLAN.md"), book)
    shutil.copytree(os.path.join(FIXTURE, "sections"), src)
    chapter = open(os.path.join(FIXTURE, "chapters", "01-first-steps.md")).read()
    for part in re.split(r"(?m)^(?=## \d)", chapter)[1:]:
        open(os.path.join(src, re.match(r"## (\d+\.\d+)", part).group(1) + ".md"), "w").write(part)
    subprocess.run(["git", "init", "-q", root])
    return book, src, os.path.join(TMP, name, "private")


def test_autopilot():
    book, src, private = make_autopilot_book("ap-dry")
    before = snapshot(os.path.dirname(book))
    code, out = run("us_autopilot.py", book, "--dry-run", e=env(private, FAKE_SOURCE=src))
    check("dry run prints writer and reviewer for both chapters", code == 0 and out.count("us-writer agent") == 2 and
          out.count("us-reviewer agent") == 2 and "us_index.py" in out, out)
    check("dry run touches nothing", snapshot(os.path.dirname(book)) == before and not os.path.exists(private))
    code, out = run("us_autopilot.py", book, "--dry-run", "--no-review", "--chapters", 1, e=env(private))
    check("dry run with --chapters 1 --no-review: one writer only", out.count("us-writer") == 1 and "reviewer" not in out, out)

    book, src, private = make_autopilot_book("ap-two")
    code, out = run("us_autopilot.py", book, "--chapters", 2, e=env(private, FAKE_SOURCE=src))
    status = json.load(open(os.path.join(book, "STATUS.json")))["chapters"]
    check("two-chapter fake run: both written and reviewed", code == 0 and
          [status.get(k, {}).get("state") for k in ("1", "2")] == ["reviewed", "reviewed"], out[-400:])
    log = open(os.path.join(private, "autopilot.log")).read().splitlines()
    check("every log line starts with date and time", log and all(re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d  ", l) for l in log), log[:2])
    check("log has 7 writer runs, 2 reviews, and the stop", sum("writer chapter" in l and "exit 0" in l for l in log) == 7 and
          sum("reviewer chapter" in l and "exit 0" in l for l in log) == 2 and "stop: 2 chapters done" in log[-1], log[-1])
    commits = subprocess.run(["git", "-C", book, "log", "--oneline"], capture_output=True, text=True).stdout
    check("one commit per step inside the book repository", commits.count("autopilot:") == 9, commits)
    check("index refreshed", os.path.exists(os.path.join(book, "README.md")) and os.path.exists(os.path.join(os.path.dirname(book), "manifest.json")))
    now = open(os.path.join(private, "now.md")).read()
    check("now.md rewritten, five lines or fewer", "chapter 2 reviewed" in now and "all written" in now and now.count("\n") <= 5, now)
    check("RESUME.md written by autopilot", "written 1-2, reviewed 1-2" in open(os.path.join(private, "RESUME.md")).read())

    book, src, private = make_autopilot_book("ap-one")
    code, out = run("us_autopilot.py", book, "--chapters", 1, "--no-review", e=env(private, FAKE_SOURCE=src))
    check("--chapters 1 --no-review stops after chapter 1", "stop: 1 chapter done" in out and
          not os.path.exists(os.path.join(book, "chapters", "02-choices.md")), out[-300:])

    book, src, private = make_autopilot_book("ap-stuck")
    code, out = run("us_autopilot.py", book, e=env(private, FAKE_SOURCE=src, FAKE_MODE="noop"))
    check("no progress twice: stops, says usage limit, exit 1", code == 1 and out.count("chapter 1: no progress") == 2 and "usage limit" in out, out[-400:])

    book, src, private = make_autopilot_book("ap-time")
    code, out = run("us_autopilot.py", book, "--minutes", 0.02, e=env(private, FAKE_SOURCE=src, FAKE_SLEEP="1.5"))
    written = open(os.path.join(book, "chapters", "01-first-steps.md")).read().count("\n## ")
    check("minutes limit: stops after the step in progress", code == 0 and "time limit" in out and written == 1, out[-300:])

    code, out = run("us_autopilot.py", book, e=env(private, UNDERSTUDY_AUTOPILOT_WRITER="no-such-agent-xyz {prompt}"))
    check("missing agent command: stops with a clear line", code == 1 and "command not found: no-such-agent-xyz" in out, out[-300:])


def main():
    book, private = test_practice()
    test_route(book, private)
    test_resume(book, private)
    n = test_real_book()
    test_autopilot()
    passed = sum(RESULTS)
    print("real book: %d questions" % n)
    print("%d passed, %d failed" % (passed, len(RESULTS) - passed))
    shutil.rmtree(TMP, ignore_errors=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
