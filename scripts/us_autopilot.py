#!/usr/bin/env python3
"""Write a book chapter by chapter with no main conversation: a fresh headless agent per step.

    python3 scripts/us_autopilot.py BOOK [--chapters K] [--minutes M] [--no-review] [--dry-run]

Loop: ask the plan what is next (in the order of private/route.md, leaving out chapters marked
skip); run the writer for that chapter and wait; check that the chapter really advanced; refresh the index; commit inside the book if it is a git repository; rewrite
private/now.md and private/RESUME.md. A fully written chapter then gets one reviewer run. Stops
after K chapters, after M minutes (checked between steps), when the book is written, after two runs
in a row with no progress (probably the usage limit), or on Ctrl+C (after the current step).
Every step is one line in <private>/autopilot.log. --dry-run prints the commands and touches nothing.

Commands come from understudy.yaml (environment UNDERSTUDY_AUTOPILOT_WRITER / _REVIEWER win):

    autopilot:
      writer: claude -p {prompt} --model opus
      reviewer: claude -p {prompt} --model opus
"""
import datetime
import os
import shlex
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import us_bookfmt as bf  # noqa: E402
import us_plan  # noqa: E402
import us_resume  # noqa: E402

DEFAULT = "claude -p {prompt} --model opus"
PROMPTS = {"writer": "Use the us-writer agent for book %s chapter %d.",
           "reviewer": "Use the us-reviewer agent for book %s chapter %d."}
STOP = []


def templates():
    """{'writer': ..., 'reviewer': ...} from the autopilot: block of understudy.yaml."""
    found, inside = {}, False
    path = os.path.join(bf.ROOT, "understudy.yaml")
    for raw in (open(path, encoding="utf-8") if os.path.exists(path) else []):
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            inside = line.strip() == "autopilot:"
        elif inside:
            key, _, value = line.strip().partition(":")
            found[key.strip()] = value.strip()
    return {role: os.environ.get("UNDERSTUDY_AUTOPILOT_" + role.upper()) or found.get(role) or DEFAULT
            for role in PROMPTS}


def command(template, prompt):
    return [t.replace("{prompt}", prompt) for t in shlex.split(template)]


def log(line):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("autopilot: " + line)
    path = os.path.join(bf.private_dir(), "autopilot.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write("%s  %s\n" % (stamp, line))


def progress(book, n):
    """(sections written, state) of chapter n, as us_plan.py status counts them."""
    plan = bf.load_plan(book)
    state, done, _ = us_plan.chapter_state(book, plan.chapter(n), bf.read_status(book))
    return len(done), state


def git_commit(book, message):
    """Commit when the book folder, or the folder of books above it, is the repository's top."""
    top = subprocess.run(["git", "-C", book, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    top = top.stdout.strip()
    if top not in (os.path.realpath(book), os.path.realpath(os.path.dirname(book))):
        return "no commit (not a book repository)"
    subprocess.run(["git", "-C", top, "add", "-A"], capture_output=True)
    done = subprocess.run(["git", "-C", top, "commit", "-q", "-m", message], capture_output=True, text=True)
    return "committed" if done.returncode == 0 else "nothing to commit"


def after_step(book, arg, what):
    """Index, commit, now.md, RESUME.md: the bookkeeping after every agent run."""
    index = subprocess.run([sys.executable, os.path.join(bf.ROOT, "scripts", "us_index.py"), book],
                           capture_output=True, text=True)
    log("us_index.py: " + ((index.stdout + index.stderr).strip().splitlines() or ["(no output)"])[-1])
    log(git_commit(book, "autopilot: " + what))
    plan = bf.load_plan(book)
    nxt = us_plan.next_to_write(book, plan)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    bf.write_text(os.path.join(bf.private_dir(), "now.md"), "\n".join([
        "%s autopilot: %s." % (stamp, what),
        "book: %s (%s)" % (plan.title, arg),
        "next to write: " + ("chapter %d, §%s %s" % (nxt[0].number, nxt[1].number, nxt[1].title) if nxt else "nothing, all written"),
        "next step: read and practise (private/RESUME.md), or run `python3 scripts/us_autopilot.py %s` again" % arg]) + "\n")
    with open(os.devnull, "w") as quiet:
        sys.stdout, out = quiet, sys.stdout
        try:
            us_resume.main([book])
        finally:
            sys.stdout = out


def run_agent(role, template, arg, book, n):
    """Run one agent; returns (progress before, progress after, exit code)."""
    cmd = command(template, PROMPTS[role] % (arg, n))
    before, start = progress(book, n), time.time()
    log("%s chapter %d: %s" % (role, n, shlex.join(cmd)))
    try:  # its own session, so Ctrl+C reaches only us and the step finishes
        code = subprocess.run(cmd, cwd=bf.ROOT, start_new_session=True).returncode
    except FileNotFoundError:
        log("%s command not found: %s; set autopilot.%s in understudy.yaml" % (role, cmd[0], role))
        return before, before, None
    after = progress(book, n)
    log("%s chapter %d: exit %d, %ds, sections %d -> %d, %s" % (role, n, code, time.time() - start, before[0], after[0], after[1]))
    return before, after, code


def plan_steps(book, plan, count, review):
    """For --dry-run: (role, chapter) steps for the next count unfinished chapters, in route order."""
    status, steps = bf.read_status(book), []
    for ch in us_plan.route_chapters(book, plan):
        if us_plan.route_sections(book, ch.number) is not None:
            continue
        state = us_plan.chapter_state(book, ch, status)[0]
        if state == "reviewed" or (state == "written" and not review):
            continue
        steps += ([("writer", ch.number)] if state != "written" else []) + ([("reviewer", ch.number)] if review else [])
        if len({n for _, n in steps}) >= count:
            break
    return steps


def option(args, name, default):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default


def on_ctrl_c(*_):
    if STOP:
        raise KeyboardInterrupt
    STOP.append(1)
    print("\nautopilot: stopping after the current step (Ctrl+C again to stop now)")


def main(argv):
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--chapters", "--minutes"))]
    if "--help" in argv or "-h" in argv or not args:
        print(__doc__.strip())
        return 0 if args else 2
    book = bf.resolve_book(args[0])
    arg = os.path.basename(book) if os.path.dirname(book) == bf.book_root() else book
    plan = bf.load_plan(book)
    if plan is None:
        print("no PLAN.md in %s" % book)
        return 1
    count, minutes = int(option(argv, "--chapters", 10 ** 6)), float(option(argv, "--minutes", 0))
    review, tpl = "--no-review" not in argv, templates()
    by_section = [c.number for c in us_plan.route_chapters(book, plan) if us_plan.route_sections(book, c.number) is not None]
    if by_section:
        print("autopilot: leaving out chapter%s %s: the route names sections of %s and autopilot writes whole chapters" % (
            "" if len(by_section) == 1 else "s", ", ".join(map(str, by_section)), "it" if len(by_section) == 1 else "them"))
    if "--dry-run" in argv:
        for role, n in plan_steps(book, plan, count, review):
            print("cd %s && %s" % (shlex.quote(bf.ROOT), shlex.join(command(tpl[role], PROMPTS[role] % (arg, n)))))
            print("%s %s %s" % (sys.executable, os.path.join(bf.ROOT, "scripts", "us_index.py"), book))
            print("git commit (only if %s is a book repository)" % book)
        return 0
    signal.signal(signal.SIGINT, on_ctrl_c)
    start, done, misses, to_review = time.time(), 0, 0, None
    log("start %s: chapters %s, minutes %s, review %s" % (arg, option(argv, "--chapters", "all"), minutes or "no limit", review))
    while True:
        nxt = us_plan.next_to_write(book, bf.load_plan(book), whole_only=True)
        if STOP:
            reason, code = "stopped by Ctrl+C", 0
        elif done >= count:
            reason, code = "%d chapter%s done" % (done, "" if done == 1 else "s"), 0
        elif minutes and time.time() - start >= minutes * 60:
            reason, code = "time limit of %g minutes reached" % minutes, 0
        elif misses >= 2:
            reason, code = "two runs in a row made no progress: probably the usage limit; try again later", 1
        elif not nxt and not to_review:
            reason, code = "the book is written", 0
        else:
            role, n = ("reviewer", to_review) if to_review else ("writer", nxt[0].number)
            before, after, exit_code = run_agent(role, tpl[role], arg, book, n)
            if exit_code is None:
                reason, code = "%s command not found" % role, 1
                break
            moved = after[1] == "reviewed" if role == "reviewer" else after[0] > before[0]
            misses = 0 if moved else misses + 1
            if not moved:
                log("%s chapter %d: no progress" % (role, n))
                continue
            finished = after[1] in ("written", "reviewed")
            total = len(bf.load_plan(book).chapter(n).sections)
            after_step(book, arg, "chapter %d %s" % (n, "reviewed" if role == "reviewer" else
                                                       "written" if finished else "%d of %d sections written" % (after[0], total)))
            to_review = n if after[1] == "written" and review else None
            done += finished and not to_review
            continue
        break
    log("stop: " + reason)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
