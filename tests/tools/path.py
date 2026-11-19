#!/usr/bin/env python3
"""Tests for the curriculum loader (stages 4 and 5, second design): every command of scripts/us_path.py
(find, card, map, index, role, spine, steps, words, ready, check, status, mark), every rule of `us_path.py check`
(a failing and a passing case each, tags and notes included), and the curriculum line of `us_check.py --tokens`.
Each test builds its own small curriculum in a temp folder (UNDERSTUDY_CURRICULUM); the four example files in
the first code blocks of curriculum/FORMAT.md are part of it and must pass.
Prints one line per test and "N passed, M failed"; exit 1 on failure.

    python3 tests/tools/path.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
FORMAT = os.path.join(ROOT, "curriculum", "FORMAT.md")
TMP = tempfile.mkdtemp(prefix="us-path-test-")
TESTS = []
COUNT = [0]


def test(fn):
    TESTS.append(fn)
    return fn


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def examples():
    """The four example files of FORMAT.md, in its order: card, track map, domain index, role map."""
    blocks = re.findall(r"```text\n(.*?)```", read(FORMAT), re.S)
    check(len(blocks) >= 4, "FORMAT.md should hold the four ```text examples first, found %d blocks" % len(blocks))
    return blocks[:4]


KIND_PART = {"language": "How it runs", "tool": "State and danger", "framework": "What it owns",
             "system": "Numbers and traces", "skill": "Judged by"}


def step_block(ident, k):
    """A valid block of Step notes for step k."""
    return ("### %d\nNeed: why does `cmd%d` of %s behave this way?\nShow: run `cmd%d` twice and compare: the "
            "second run prints %d.\nExplain: The loop of %s repeats the work %d times.\nTry: predict: what `cmd%d` "
            "prints; fix: a broken `cmd%d` (finish line: it prints %d)." % (k, k, ident, k, k, ident, k, k, k, k))


def card(ident, needs="none", kind="tool", title=None, steps=None, aliases=None, belief=None, ladder=None,
         status="built 2026-11-18", sources="example.org/docs (the order)", body="", words=None, part=None,
         never=None, failures=None, practice=None, order=None, notes=True, deep="2, 3", blocks=None, numbers=None):
    """A small card that passes check without notes: third design (Step notes, Deep steps) unless notes=False.
    docker and linux-command-line get the step counts FORMAT.md's example goals name (12 and 13)."""
    steps = steps or STEP_COUNT.get(ident, 6)
    head = ["# %s: %s" % (ident, title or "%s for testers" % ident.replace("-", " ")), "kind: %s" % kind]
    if aliases:
        head.append("aliases: %s" % aliases)
    head += ["needs: %s" % needs, "status: %s" % status, "sources: %s" % sources]
    order = order or "\n".join("%d. Step %d, made and broken on purpose." % (k, k) for k in range(1, steps + 1))
    ladder = ladder or ("- Use: run it on a given file.\n- Explain: trace one run to a friend.\n"
                        "- Build: the project above.\n- Design: choose the settings for a stated load.")
    return "\n".join(head) + """

## Promise
Run and repair a small %(id)s setup.

## The one idea
One loop keeps it true.%(body)s

## In production
- Teams run it from files in Git.

## Teaching order
%(order)s

## %(kpart)s
%(part)s
%(notes)s
## Go deep, leave for later
%(deep)s- Deep: the loop. Later: the rest.

## Never omit
%(never)s

## Wrong beliefs
%(belief)s

## Failures to diagnose
%(failures)s

## Practice and project
%(practice)s

## Mastery ladder
%(ladder)s

## Words to own
%(words)s
""" % {"id": ident, "order": order, "belief": belief or '- [1] "It runs by itself" (a loop runs it).',
       "ladder": ladder, "body": body, "kpart": KIND_PART.get(kind, "State and danger"),
       "part": part or "- [1] State lives in `state.json`.\n- `wipe --all` deletes the work: use `wipe --dry-run` first.",
       "never": never or "- Break it and watch it recover.",
       "failures": failures or "- [2] It does not start: the name is wrong.\n- [3,4] It starts and stops: the command exits.",
       "practice": practice or "Guided: repeat each step. Project: the learner's own small service; finish line: five checks pass.",
       "words": words or "[1] %s loop, %s state; [2-%d] %s reconcile" % (ident, ident, max(steps, 2), ident),
       "notes": ("\n## Step notes\n%s\n" % (blocks if blocks is not None else "\n".join(
           step_block(ident, k) for k in range(1, steps + 1))) if notes else "") +
                ("\n## Believable numbers\n%s\n" % numbers if numbers else ""),
       "deep": "- Deep steps: %s (the loop and its state).\n" % deep if notes and deep else ""}


# the fixture adds a planned row 4 with hours to FORMAT.md's example map: a planned subject the tests can use
ROW4 = "| 4 | kubernetes-internals (planned) | 3 | run services on a cluster | pods, services | 40 | 2 Explain |"
STEP_COUNT = {"docker": 12, "linux-command-line": 13}
NEEDS = {"docker": "linux-command-line, networking-basics", "networking-basics": "linux-command-line"}
SUPPORT = ["docker", "networking-basics", "linux-command-line", "linux-shell", "container-internals"]


def fresh():
    """A new curriculum folder: FORMAT.md's four examples plus the cards their ids name. Returns its path."""
    COUNT[0] += 1
    cur = os.path.join(TMP, "c%d" % COUNT[0], "curriculum")
    c, m, i, r = examples()
    c = c.replace("(steps 3 to 8 follow in the same form)\n", "\n".join(step_block("kubernetes-core", k)
                                                                     for k in range(3, 9)) + "\n")
    write(os.path.join(cur, "cards", "kubernetes-core.md"), c)
    m = m.replace("\n\n## Goals", "\n" + ROW4 + "\n\n## Goals")
    write(os.path.join(cur, "devops", "containers.md"), m)
    write(os.path.join(cur, "devops", "INDEX.md"), i)
    write(os.path.join(cur, "roles", "junior-devops-engineer.md"), r)
    for ident in SUPPORT:
        write(os.path.join(cur, "cards", ident + ".md"), card(ident, needs=NEEDS.get(ident, "none")))
    return cur


def run(cur, *args, today=None, script="us_path.py"):
    """Run a script on curriculum `cur`: (exit code, output lines)."""
    env = dict(os.environ, UNDERSTUDY_CURRICULUM=cur)
    env.pop("UNDERSTUDY_TODAY", None)
    if today:
        env["UNDERSTUDY_TODAY"] = today
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args),
                          capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + proc.stderr).splitlines()


def edit(path, old, new):
    text = read(path)
    check(old in text, "test set-up: %r not in %s" % (old, path))
    write(path, text.replace(old, new, 1))


def fails(cur, *needles):
    """Check fails, its last line is 'check failed', and an ERROR line holds each needle."""
    code, out = run(cur, "check")
    check(code == 1 and out[-1] == "check failed", out)
    errs = [l for l in out if l.startswith("ERROR ")]
    for n in needles:
        check(any(n in l for l in errs), "no ERROR with %r in %s" % (n, out))
    return errs


def passes(cur):
    code, out = run(cur, "check")
    check(code == 0 and out[-1].startswith("check ok: "), out)
    return out


def cardpath(cur, ident):
    return os.path.join(cur, "cards", ident + ".md")


MAP = lambda cur: os.path.join(cur, "devops", "containers.md")       # noqa: E731
ROLE = lambda cur: os.path.join(cur, "roles", "junior-devops-engineer.md")   # noqa: E731
INDEX = lambda cur: os.path.join(cur, "devops", "INDEX.md")           # noqa: E731
K8S = "kubernetes-core"

# ---------------------------------------------------------------- an empty or missing curriculum


@test
def missing_or_empty_curriculum():
    for cur in (os.path.join(TMP, "none", "curriculum"), os.path.join(TMP, "empty", "curriculum")):
        if "empty" in cur:
            os.makedirs(cur)
            write(os.path.join(cur, "FORMAT.md"), read(FORMAT))
        code, out = run(cur, "find", "docker")
        check(code == 1 and out == ["nothing in the curriculum matches docker"], out)
        check(run(cur, "check") == (0, ["no curriculum files"]), run(cur, "check"))
        check(run(cur, "index") == (0, ["no curriculum files"]), run(cur, "index"))
        check(run(cur, "status") == (0, ["no curriculum files"]), run(cur, "status"))
        for args in (("card", "docker"), ("map", "devops/containers"), ("index", "devops"), ("role", "x"),
                     ("mark", "docker", "reviewed"), ("ready", "x")):
            code, out = run(cur, *args)
            check(code == 1 and out and "Traceback" not in "\n".join(out), (args, out))
        for args in (("spine", "docker"), ("steps", "docker:1"), ("words", "docker")):
            code, out = run(cur, *args)
            check(code == 2 and len(out) == 1 and out[0].startswith("no card"), (args, out))

# ---------------------------------------------------------------- the law: FORMAT.md's examples pass


@test
def format_examples_pass():
    out = passes(fresh())
    check(out == ["check ok: 6 cards, 1 maps, 1 roles, 1 indexes"], out)


@test
def real_curriculum_runs():
    """The real curriculum folder (whatever other helpers have written by now) is read without a crash."""
    env = {k: v for k, v in os.environ.items() if k != "UNDERSTUDY_CURRICULUM"}
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "us_path.py"), "check"], capture_output=True,
                          text=True, env=env)
    last = proc.stdout.strip().splitlines()[-1:] or [""]
    check("Traceback" not in proc.stderr and re.match(r"^(check ok: |check failed$|no curriculum files$)", last[0]),
          proc.stdout[-500:] + proc.stderr[-500:])

# ---------------------------------------------------------------- find


@test
def find_one_card_by_alias_prints_card_and_tracks():
    cur = fresh()
    code, out = run(cur, "find", "k8s")
    check(code == 0 and out[0] == "# kubernetes-core: Kubernetes for people who will run services on it", out[:2])
    check(out[-1] == "In tracks: none", out[-3:])
    code, out = run(cur, "find", "Kubernetes")
    check(code == 0 and out[0].startswith("# kubernetes-core:"), out[:3])


@test
def find_card_in_a_track_shows_its_row():
    cur = fresh()
    code, out = run(cur, "find", "docker")
    check(code == 0 and out[0] == "# docker: docker for testers", out[:2])
    i = out.index("In tracks:")
    check(out[i + 1] == "devops/containers:" and out[i + 2].startswith("| # | Subject | Needs first |"), out[i:])
    check(out[i + 3].startswith("| 3 | docker | 1, 2 |") and len(out) == i + 4, out[i:])


@test
def find_role_track_and_domain_print_that_file():
    cur = fresh()
    code, out = run(cur, "find", "junior", "devops", "engineer")
    check(code == 0 and out == read(ROLE(cur)).splitlines(), out[:3])
    code, out = run(cur, "find", "containers", "and", "orchestration")
    check(code == 0 and out == read(MAP(cur)).splitlines(), out[:3])
    code, out = run(cur, "find", "devops")
    check(code == 0 and out == read(INDEX(cur)).splitlines(), out[:3])


@test
def find_several_close_lists_them_and_nothing_else():
    cur = fresh()
    for k in range(10):
        write(cardpath(cur, "linux-extra-%d" % k), card("linux-extra-%d" % k))
    code, out = run(cur, "find", "linux")
    check(code == 0 and len(out) == 8, out)
    check(all(re.match(r"^linux-\S+\s+card\s+linux .* for testers$", l) for l in out), out)
    cur = fresh()
    code, out = run(cur, "find", "linux")
    check(code == 0 and len(out) == 2 and out[0].split()[:2] == ["linux-command-line", "card"], out)
    check(out[1].split()[:2] == ["linux-shell", "card"], out)


@test
def find_nothing_and_never_format():
    cur = fresh()
    code, out = run(cur, "find", "quantum", "basket", "weaving")
    check(code == 1 and out == ["nothing in the curriculum matches quantum basket weaving"], out)
    for words in (["format"], ["four", "kinds", "of", "file"], ["curriculum", "files"]):
        code, out = run(cur, "find", *words)
        check("# The curriculum files: what they are" not in out, (words, out[:3]))

# ---------------------------------------------------------------- card, map, index, role


@test
def card_command():
    cur = fresh()
    code, out = run(cur, "card", "docker")
    check(code == 0 and out[0] == "# docker: docker for testers" and "In tracks:" in out, out)
    code, out = run(cur, "card", "nope")
    check(code == 1 and out[0].startswith("no card 'nope'"), out)


@test
def map_command_prints_goals():
    cur = fresh()
    for ref in ("devops/containers", "containers"):
        code, out = run(cur, "map", ref)
        check(code == 0 and out == read(MAP(cur)).splitlines(), (ref, out[:2]))
        i = out.index("## Goals")
        check(out[i + 1].startswith("### ") and out[i + 2].startswith("Steps: "), out[i:i + 3])
    code, out = run(cur, "map", "devops/nothing")
    check(code == 1 and out == ["no track map 'devops/nothing'; tracks: devops/containers"], out)


@test
def index_command():
    cur = fresh()
    write(os.path.join(cur, "data", "INDEX.md"), "# Data and databases\nstatus: built 2026-11-18\n\n"
          "| Track | For | Start here if |\n|---|---|---|\n| sql (planned) | anyone | you store data |\n")
    code, out = run(cur, "index")
    check(code == 0 and out == ["data  Data and databases", "devops  DevOps and infrastructure"], out)
    code, out = run(cur, "index", "devops")
    check(code == 0 and out == read(INDEX(cur)).splitlines(), out)
    code, out = run(cur, "index", "art")
    check(code == 1 and out == ["no domain 'art'; domains: data, devops"], out)


@test
def role_without_have_prints_all_and_hours():
    cur = fresh()
    code, out = run(cur, "role", "junior-devops-engineer")
    check(code == 0 and out[:-4] == read(ROLE(cur)).splitlines(), out)
    check(out[-3:] == ["left: 2 subjects, about 50 hours",
                       "Specialist lines, if you want them: 1 subject, about 40 hours", "Needed first, though not on this role's list: networking-basics (for docker)"], out)
    edit(MAP(cur), "| pods, services | 40 |", "| pods, services | many |")
    code, out = run(cur, "role", "junior-devops-engineer")
    check(out[-2] == "Specialist lines, if you want them: 1 subject, hours unknown (no track map gives them)", out)
    edit(ROLE(cur), "| docker | 3 Build |", "| networking-basics | 2 Explain | desirable | x | y |\n| docker | 3 Build |")
    code, out = run(cur, "role", "junior-devops-engineer")
    check(not any(l.startswith("Needed first") for l in out), out)


@test
def role_with_have_takes_out_lines_at_or_above_level():
    cur = fresh()
    code, out = run(cur, "role", "junior-devops-engineer", "--have",
                    "linux-command-line:3, kubernetes-internals:4, docker:2")
    rows = [l for l in out if l.startswith("| ") and not l.startswith("| Subject") and not l.startswith("|---")]
    check(code == 0 and [r.split("|")[1].strip() for r in rows] == ["docker"], out)
    check(out[-2:] == ["left: 1 subject, about 30 hours", "Needed first, though not on this role's list: networking-basics (for docker)"], out)
    code, out = run(cur, "role", "junior-devops-engineer", "--have", "docker:3, linux-command-line:5")
    check(out[-2:] == ["left: 0 subjects, about 0 hours",
                       "Specialist lines, if you want them: 1 subject, about 40 hours"], out)
    code, out = run(cur, "role", "junior-devops-engineer", "--have",
                    "docker:3, linux-command-line:3, kubernetes-internals:2")
    check(out[-1] == "left: 0 subjects, about 0 hours", out)
    check(run(cur, "role", "junior-devops-engineer", "--have", "docker=3")[0] == 2, "bad --have accepted")
    check(run(cur, "role", "nobody")[0] == 1, "unknown role accepted")
    check(run(cur, "role", "junior-devops-engineer", "--by", "x")[0] == 2, "--by with role accepted")
    check(run(cur, "role", "junior-devops-engineer", "--all")[0] == 2, "--all with role accepted")

# ---------------------------------------------------------------- check: every rule, failing and passing


@test
def check_header_lines_required_and_in_order():
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none\n", "")
    fails(cur, "cards/linux-shell.md:1 no 'needs:' line")
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "kind: tool\nneeds: none\n", "needs: none\nkind: tool\n")
    fails(cur, "header lines are out of order")
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none\n", "needs: none\nflavour: sweet\n")
    fails(cur, "'flavour:' is not a header line of a card")
    cur = fresh()
    edit(MAP(cur), "leads to:", "leeds to:")
    fails(cur, "no 'leads to:' line")
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none\n", "needs: none\nunverified: the hours\n")
    fails(cur, "header lines are out of order")
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "kind: tool\n", "kind: tool\naliases: whale, containers\n")
    edit(cardpath(cur, "linux-shell"), "(the order)\n", "(the order);\n  example.org/more (the rest)\nunverified: the hours\n")
    passes(cur)
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "(the order)\n", "(the order);\nexample.org/more (the rest)\n")
    fails(cur, "cards/linux-shell.md:6 not a header line")


@test
def check_parts_required_and_in_order():
    cur = fresh()
    edit(cardpath(cur, "docker"), "## Never omit\n- Break it and watch it recover.\n\n", "")
    fails(cur, "no '## Never omit' part")
    cur = fresh()
    edit(cardpath(cur, "docker"), "## Promise\nRun and repair a small docker setup.\n\n", "")
    edit(cardpath(cur, "docker"), "## Words to own", "## Promise\nRun it.\n\n## Words to own")
    fails(cur, "the parts are out of order")
    cur = fresh()
    edit(MAP(cur), "## Short on time", "## Extras\nMore.\n\n## Short on time")
    fails(cur, "'## Extras' is not a part of a track")
    cur = fresh()
    edit(ROLE(cur), "## Capstone\nOne project", "## Capstone\n\n## Spare\nOne project")
    fails(cur, "'## Capstone' is empty", "'## Spare' is not a part of a role")


@test
def check_kind_part_required_with_the_right_name():
    cur = fresh()
    text = read(cardpath(cur, "docker"))
    write(cardpath(cur, "docker"), re.sub(r"## State and danger\n(?:.+\n)+\n", "", text))
    fails(cur, "cards/docker.md no '## State and danger' part, which a tool card must have")
    cur = fresh()
    edit(cardpath(cur, "docker"), "## State and danger", "## How it runs")
    errs = fails(cur, "'## How it runs' is the part of a language card; a tool card has '## State and danger'",
                 "no '## State and danger' part")
    check(not any("is not a part of a card" in e for e in errs), errs)
    cur = fresh()
    edit(cardpath(cur, "docker"), "kind: tool", "kind: system")
    fails(cur, "a system card has '## Numbers and traces'")
    cur = fresh()
    edit(cardpath(cur, K8S), "## State and danger", "## Go deep, leave for later\n- x\n\n## State and danger")
    fails(cur, "the parts are out of order")


@test
def check_kind():
    cur = fresh()
    edit(cardpath(cur, "docker"), "kind: tool", "kind: gadget")
    fails(cur, "kind 'gadget' is not known")
    for kind, part in KIND_PART.items():
        cur = fresh()
        write(cardpath(cur, "docker"), card("docker", kind=kind))
        check("\n## %s\n" % part in read(cardpath(cur, "docker")), part)
        passes(cur)


@test
def check_goals_of_a_track_map():
    cur = old_goals(fresh())
    text = read(MAP(cur))
    write(MAP(cur), re.sub(r"## Goals\n(?:.+\n)+\n", "", text))
    fails(cur, "curriculum/devops/containers.md no '## Goals' part")
    cur = old_goals(fresh())
    write(MAP(cur), re.sub(r"\n- [^\n]*\n\n## Why this order", "\n\n## Why this order", read(MAP(cur))))
    fails(cur, "'## Goals' has 1 list items; give 2 to 5")
    cur = old_goals(fresh())
    edit(MAP(cur), "## Why this order", "- c: rows 1.\n- d: rows 2.\n- e: rows 3.\n- f: row 1.\n\n## Why this order")
    fails(cur, "'## Goals' has 6 list items; give 2 to 5")
    cur = old_goals(fresh())
    add_goal(cur, "- c: rows 1.\n- d: rows 2.\n- e: rows 3.")
    passes(cur)
    cur = old_goals(fresh())
    text = read(MAP(cur))
    goals = re.search(r"## Goals\n(?:.+\n)+\n", text).group(0)
    write(MAP(cur), text.replace(goals, "").replace("## Checkpoint projects", goals + "## Checkpoint projects"))
    fails(cur, "the parts are out of order; the order is: Goals, Why this order")
    cur = old_goals(fresh())
    text = read(MAP(cur))
    write(MAP(cur), text.replace(goals, "").replace("| # | Subject |", goals + "| # | Subject |"))
    fails(cur, "'## Goals' comes before the table; put it after the table")


@test
def check_sizes():
    for kind, path, limit in (("card", lambda c: cardpath(c, "docker"), 5000), ("map", MAP, 2000),
                              ("index", INDEX, 250), ("role", ROLE, 800)):
        cur = fresh()
        text = read(path(cur))
        pad = limit * 4 - len(text) - len("\n## x\n")
        tail = "\nPadding " + "x" * (pad - len("\nPadding ")) + "\n"
        if kind == "card":
            edit(path(cur), "reconcile\n", "reconcile" + tail)
        elif kind == "index":
            write(path(cur), text + "\n" + "Roles: " + "x" * (limit * 4 - len(text) - 8) + "\n")
        else:
            edit(path(cur), "## Overlap\n" if kind == "role" else "## Left out on purpose\n",
                 ("## Overlap\n" if kind == "role" else "## Left out on purpose\n") + tail.lstrip("\n"))
        text = read(path(cur)).rstrip("\n")
        text = (text + "x" * (limit * 4 - len(text) - 1))[:limit * 4 - 1] + "\n"
        write(path(cur), text)
        size = (len(read(path(cur))) + 3) // 4
        check(size == limit, (kind, size))
        passes(cur)
        write(path(cur), read(path(cur)).rstrip("\n") + "xxxx\n")
        fails(cur, "%d tokens; a %s may have %s" % (limit + 1, {"map": "track", "index": "domain"}.get(kind, kind),
                                                  "{:,}".format(limit)))


@test
def check_file_name_is_id_and_ids_lower_case():
    cur = fresh()
    edit(cardpath(cur, "docker"), "# docker:", "# dockerd:")
    fails(cur, "the id 'dockerd' differs from the file name 'docker.md'")
    cur = fresh()
    write(cardpath(cur, "Docker_Two"), card("Docker_Two"))
    fails(cur, "the file name 'Docker_Two' must be an id")
    cur = fresh()
    edit(cardpath(cur, "docker"), "# docker: docker for testers", "# Docker for testers")
    fails(cur, "the first line must be '# docker: Title'")
    cur = fresh()
    os.makedirs(os.path.join(cur, "Dev_Ops"))
    os.rename(MAP(cur), os.path.join(cur, "Dev_Ops", "containers.md"))
    os.rename(INDEX(cur), os.path.join(cur, "Dev_Ops", "INDEX.md"))
    fails(cur, "domain folder 'Dev_Ops' must be lower-case")


@test
def check_needs_are_cards_or_planned():
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: container-internals, wizardry")
    fails(cur, "needs 'wizardry', which is no card and no '(planned)' row")
    edit(cardpath(cur, "linux-shell"), "needs: container-internals, wizardry", "needs: container-internals")
    edit(cardpath(cur, K8S), "needs: docker,", "needs: wizardry, docker,")
    fails(cur, "needs 'wizardry', which is no card")
    edit(MAP(cur), "\n\n## Goals", "\n| 5 | wizardry (planned) | 3 | cast | spells | 10 | 1 Use |\n\n## Goals")
    passes(cur)
    edit(cardpath(cur, "linux-shell"), "needs: container-internals", "needs: Container_Internals")
    fails(cur, "needs 'Container_Internals' is not an id")


@test
def check_needs_with_alternatives():
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: container-internals | docker, networking-basics")
    passes(cur)
    edit(cardpath(cur, "linux-shell"), "needs: container-internals | docker,", "needs: container-internals | sorcery,")
    fails(cur, "cards/linux-shell.md:3 needs 'sorcery', which is no card and no '(planned)' row")
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: container-internals | Bad_Id")
    fails(cur, "needs 'Bad_Id' is not an id")
    cur = fresh()                     # alternatives make no edge in the cycle check
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: container-internals | docker")
    edit(cardpath(cur, "container-internals"), "needs: none", "needs: linux-shell")
    passes(cur)
    cur = fresh()                     # any one alternative as an earlier row satisfies the map order
    edit(cardpath(cur, "docker"), "needs: linux-command-line, networking-basics",
         "needs: linux-command-line, networking-basics | container-internals")
    passes(cur)
    edit(cardpath(cur, "docker"), "needs: linux-command-line, networking-basics | container-internals",
         "needs: linux-command-line, networking-basics, linux-shell | container-internals")
    fails(cur, 'row 3 docker: its card needs linux-shell or container-internals, which is not an earlier row and is '
               'not named in "Needs first"')
    edit(MAP(cur), "| 3 | docker | 1, 2 |", "| 3 | docker | 1, 2, container-internals |")
    passes(cur)
    code, out = run(cur, "spine", "docker:1")
    check("## docker: docker for testers (kind tool; needs: linux-command-line, networking-basics, linux-shell | "
          "container-internals; 12 steps)" in out, out)


@test
def check_no_cycle_in_needs():
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: container-internals")
    edit(cardpath(cur, "container-internals"), "needs: none", "needs: linux-shell")
    errs = fails(cur, "needs go round in a circle: container-internals -> linux-shell -> container-internals")
    check(len(errs) == 1, errs)
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: linux-shell")
    fails(cur, "needs go round in a circle: linux-shell -> linux-shell")
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "needs: none", "needs: container-internals")
    passes(cur)


@test
def check_map_order_follows_needs():
    cur = fresh()
    edit(MAP(cur), "| 1 | linux-command-line | none |", "| 1 | linux-command-line | 2 |")
    fails(cur, "needs row 2, which is not a row before this one")
    cur = fresh()
    edit(MAP(cur), "| 1 | linux-command-line | none |", "| 1 | linux-command-line | docker |")
    fails(cur, "needs 'docker', which is row 3, not before it")
    cur = fresh()
    edit(cardpath(cur, "linux-command-line"), "needs: none", "needs: networking-basics")
    fails(cur, 'row 1 linux-command-line: its card needs networking-basics, which is not an earlier row and is not '
               'named in "Needs first"')
    cur = fresh()
    edit(cardpath(cur, "docker"), "needs: linux-command-line, networking-basics", "needs: linux-shell")
    fails(cur, 'row 3 docker: its card needs linux-shell, which is not an earlier row')
    edit(MAP(cur), "| 3 | docker | 1, 2 |", "| 3 | docker | 1, 2, linux-shell |")
    out = passes(cur)               # named in "Needs first": no error; rows 1 and 2 it does not need: notes
    check([l for l in out if l.startswith("note: ")] == [
        'note: curriculum/devops/containers.md:11: row 3: "Needs first" names row 1 (linux-command-line), which the '
        'card does not need',
        'note: curriculum/devops/containers.md:11: row 3: "Needs first" names row 2 (networking-basics), which the '
        'card does not need'], out)
    cur = fresh()
    edit(MAP(cur), "| 3 | docker |", "| 4 | docker |")
    fails(cur, "row number is '4'")


@test
def check_map_subjects_have_cards_or_planned():
    cur = fresh()
    os.remove(cardpath(cur, "networking-basics"))
    fails(cur, "'networking-basics' has no card; write 'networking-basics (planned)'")
    edit(MAP(cur), "| 2 | networking-basics |", "| 2 | networking-basics (planned) |")
    passes(cur)
    write(cardpath(cur, "networking-basics"), card("networking-basics"))
    fails(cur, "'networking-basics' has a card now; write it without '(planned)'")


@test
def check_map_hours_and_level():
    cur = fresh()
    edit(MAP(cur), "| 20 | 2 Explain |", "| about 20 | 2 Explain |")
    fails(cur, "hours 'about 20' must be a number")
    cur = fresh()
    edit(MAP(cur), "| 20 | 2 Explain |", "| 20 | 2 Expert |")
    fails(cur, "level '2 Expert' is not one of 1 Use, 2 Explain, 3 Build, 4 Design, 5 Teach")
    cur = fresh()
    edit(MAP(cur), "| 20 | 2 Explain |", "| 20 | 5 Teach |")
    passes(cur)
    cur = fresh()
    edit(MAP(cur), "| # | Subject |", "| No | Subject |")
    fails(cur, "the table's columns must be | # | Subject | Needs first |")


@test
def check_teaching_order_steps():
    for steps, ok in ((5, False), (6, True), (14, True), (15, False)):
        cur = fresh()
        write(cardpath(cur, "linux-shell"), card("linux-shell", steps=steps))
        if ok:
            passes(cur)
        else:
            fails(cur, "Teaching order has %d numbered steps; give 6 to 14" % steps)
    cur = fresh()
    edit(cardpath(cur, "linux-shell"), "3. Step 3", "4. Step 3")
    fails(cur, "Teaching order steps must be numbered 1, 2, 3")


@test
def check_wrong_beliefs():
    for belief in ('- [1] It runs by itself (a loop runs it).', '- [1] "It runs by itself" because a loop runs it.',
                   '- [1] "It runs by itself"'):
        cur = fresh()
        write(cardpath(cur, "docker"), card("docker", belief=belief))
        fails(cur, "a wrong belief must be a quoted belief and the truth in brackets")
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", belief='- [1] "It runs by itself" (a loop, the reconciler (one of\n'
                                         '  many), runs it).\n- [2] “Curly quotes” (are fine too)'))
    passes(cur)


@test
def check_mastery_ladder():
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", ladder="- Use: run it.\n- Explain: say it.\n- Build: make it."))
    fails(cur, "Mastery ladder must be four lines in order")
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", ladder="- Use: run it.\n- Build: make it.\n- Explain: say it.\n"
                                                         "- Design: plan it."))
    fails(cur, "Mastery ladder must be four lines in order")
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", ladder="- Use: run it.\n- Explain: understands the loop.\n"
                                                         "- Build: make it.\n- Design: plan it."))
    fails(cur, "never 'understands X'")

# ---------------------------------------------------------------- check: tags


@test
def tags_of_every_form_are_read():
    sys.path.insert(0, SCRIPTS)
    import us_path
    for text, want in (("[3] x", [3]), ("[5-6] x", [5, 6]), ("[2,8] x", [2, 8]), ("[1,4-6] x", [1, 4, 5, 6]),
                       ("[2, 8] x", [2, 8]), ("[ 1 , 4 - 6 ] x", [1, 4, 5, 6])):
        steps, rest, bad = us_path.parse_tag(text)
        check(steps == want and rest == "x" and bad is None, (text, steps, rest, bad))
    for text in ("[6-5] x", "[] x", "[1,] x", "[-2] x"):
        steps, rest, bad = us_path.parse_tag(text)
        check(steps is None and bad == text[:-2], (text, steps, bad))
    for text in ('"No tag" (x)', "[see] x", "plain"):
        check(us_path.parse_tag(text) == (None, text, None), text)
    check(us_path.parse_steps("1,3,5-6") == [1, 3, 5, 6] and us_path.parse_steps("4-8") == [4, 5, 6, 7, 8], "steps")
    check(us_path.show_steps([1, 3, 5, 6]) == "1, 3, 5-6", us_path.show_steps([1, 3, 5, 6]))
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", steps=8, part="- [3] a `x`.\n- [5-6] b `y`.\n- [2,8] c `z`.\n"
                                        "- [1,4-6] d `w`.\n- e `v`.", words="[1-8] loop"))
    passes(cur)


@test
def check_tags_required_where_the_format_says():
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", belief='- "It runs by itself" (a loop runs it).'))
    fails(cur, "cards/linux-shell.md:68 every item in Wrong beliefs needs a tag naming its step")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", failures="- It does not start: the name is wrong."))
    fails(cur, "every item in Failures to diagnose needs a tag naming its step")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", failures="It does not start; it starts and stops."))
    fails(cur, "every item in Failures to diagnose needs a tag")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", words="loop, state; [2-6] reconcile"))
    fails(cur, "every group in Words to own needs a tag")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", words="[1] loop, state;\n[2-6] reconcile; probe"))
    fails(cur, "cards/linux-shell.md:85 every group in Words to own needs a tag")
    cur = fresh()                     # optional where the format says so: no tag = every step
    write(cardpath(cur, "linux-shell"), card("linux-shell", part="- State lives in `state.json`.", never="- Break it."))
    passes(cur)


@test
def check_tags_name_only_steps_that_exist():
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", part="- [9] State lives in `state.json`."))
    fails(cur, "the tag in State and danger names step 9, but the card has steps 1 to 6")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", never="- [0] Break it.\n- [5-7] Fix it."))
    errs = fails(cur, "the tag in Never omit names step 0", "the tag in Never omit names step 7")
    check(len(errs) == 2, errs)
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", belief='- [7] "It runs by itself" (a loop runs it).'))
    fails(cur, "the tag in Wrong beliefs names step 7")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", words="[1] loop; [2-12] state"))
    fails(cur, "the tag in Words to own names step 7-12, but the card has steps 1 to 6")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", failures="- [3-1] It starts and stops."))
    fails(cur, "the tag [3-1] in Failures to diagnose cannot be read; write [3], [5-6], [2,8] or [1,4-6]")


@test
def check_notes_do_not_fail_and_come_before_the_last_line():
    cur = fresh()
    order = "\n".join(["1. Run it with `go`.", "2. Teach the idea well.", "3. A Container and its state.",
                       "4. Read 4 logs.", "5. Wrap up the thing,", "   across two lines.", "6. Use DNS names."])
    write(cardpath(cur, "linux-shell"), card("linux-shell", order=order, words="[1] loop; [2,4-6] state"))
    out = passes(cur)
    notes = [l for l in out if l.startswith("note: ")]
    check(notes == ["note: curriculum/cards/linux-shell.md:18: step 2 names nothing concrete (no `code`, number or name): "
                    "name the real thing that carries it",
                    "note: curriculum/cards/linux-shell.md:19: step 3 has no word and no wrong belief tagged to it: tag one, "
                    "or ask whether it is a step",
                    "note: curriculum/cards/linux-shell.md:21: step 5 names nothing concrete (no `code`, number or name): "
                    "name the real thing that carries it"], notes)
    check(out[-1] == "check ok: 6 cards, 1 maps, 1 roles, 1 indexes" and out[:-1] == notes, out)
    edit(cardpath(cur, "linux-shell"), "kind: tool", "kind: gadget")
    code, out = run(cur, "check")
    check(code == 1 and out[-1] == "check failed" and out[0].startswith("ERROR ") and out[1].startswith("note: "), out)

@test
def check_notes_a_word_owned_by_two_cards():
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", words="[1] Load  Shedding, pipe; [2-6] glob"))
    write(cardpath(cur, "container-internals"), card("container-internals", words="[1] load shedding ; [2-6] cgroup"))
    ok = ["check ok: 6 cards, 1 maps, 1 roles, 1 indexes"]
    check(passes(cur) == ok, "two cards no plan can join were noted")
    write(cardpath(cur, "linux-shell"), card("linux-shell", needs="docker | container-internals",
                                             words="[1] Load  Shedding, pipe; [2-6] glob"))
    out = passes(cur)                 # linux-shell needs container-internals (one alternative): they can meet
    check([l for l in out if l.startswith("note: ")] == [
        "note: curriculum/cards/linux-shell.md:84: word 'Load  Shedding' is also owned by container-internals: one "
        "home per word"], out)
    write(cardpath(cur, "linux-shell"), card("linux-shell", words="[1] load-shedding, pipe; [2-6] glob"))
    check(passes(cur) == ok, "a different word was noted")
    write(cardpath(cur, "linux-shell"), card("linux-shell", needs="docker | container-internals",
                                             words="[1] Load  Shedding, pipe; [2-6] glob"))
    write(cardpath(cur, "docker"), card("docker", needs="linux-command-line, linux-shell | container-internals"))
    edit(MAP(cur), "| 3 | docker | 1, 2 |", "| 3 | docker | 1, 2, linux-shell |")
    out = passes(cur)                 # alternatives of one need elsewhere: a learner takes one or the other
    check([l for l in out if l.startswith("note: ")] == [
        'note: curriculum/devops/containers.md:11: row 3: "Needs first" names row 2 (networking-basics), which the '
        'card does not need'], out)
    cur = fresh()                     # a needs chain two links long
    write(cardpath(cur, "container-internals"), card("container-internals", needs="linux-shell",
                                                     words="[1] shell word; [2-6] ci"))
    write(cardpath(cur, "linux-shell"), card("linux-shell", needs="docker", words="[1] Shell Word; [2-6] ls"))
    out = passes(cur)                 # container-internals needs docker through linux-shell
    check([l for l in out if l.startswith("note: ")] == [
        "note: curriculum/cards/linux-shell.md:84: word 'Shell Word' is also owned by container-internals: one home "
        "per word"], out)
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", needs="linux-command-line", words="[1] packet; [2-12] image"))
    edit(MAP(cur), "| 3 | docker | 1, 2 |", "| 3 | docker | 1 |")     # only the track map joins them
    write(cardpath(cur, "networking-basics"), card("networking-basics", words="[1] packet; [2-6] route"))
    edit(MAP(cur), "| 2 | networking-basics | 1 |", "| 2 | networking-basics | none |")
    out = passes(cur)
    check([l for l in out if l.startswith("note: ")] == [
        "note: curriculum/cards/networking-basics.md:84: word 'packet' is also owned by docker: one home per word"], out)

OLD_GOALS = "- Ship my own service in a container: rows 1 to 3.\n- Run services on a cluster: rows 1 to 4.\n"


def old_goals(cur):
    """The fixture's map with its Goals in the old form (a list); returns cur."""
    text = read(MAP(cur))
    a, b = text.index("## Goals\n") + len("## Goals\n"), text.index("\n## Why this order")
    write(MAP(cur), text[:a] + OLD_GOALS + text[b:])
    return cur


def set_goals(cur, blocks):
    """Replace the map's Goals with these lines."""
    text = read(MAP(cur))
    a, b = text.index("## Goals\n") + len("## Goals\n"), text.index("\n## Why this order")
    write(MAP(cur), text[:a] + blocks.rstrip("\n") + "\n" + text[b:])


GOAL_A = """### Ship my own service (about 55 h)
Steps: linux-command-line 1-6; networking-basics 2-4; docker 1-12.
Open with: their own service in a container in chapter 1 (docker 1-3 in miniature).
Deep: docker 4, 6; linux-command-line 5.
Order: linux-command-line 1-4; docker 1-3; linux-command-line 5-6; networking-basics 2-4; docker 4-12.
Halfway: they rebuild the image in seconds.
"""
GOAL_B = """### Platform engineer (about 70 h)
Steps: linux-command-line; networking-basics 2-5; docker.
Open with: one real server they can reach.
Deep: linux-command-line 5, 8; docker 4, 7.
Order: rows in order.
"""


@test
def check_goal_blocks():
    passes(fresh())                   # FORMAT.md's example map: goal blocks
    for goals, msg in (
            (GOAL_A.replace("Open with: their own service in a container in chapter 1 (docker 1-3 in miniature).\n",
                            ""), "goal 'Ship my own service (about 55 h)' has no Open with: line; add it"),
            (GOAL_A.replace("Deep: docker 4, 6; linux-command-line 5.\n", "").replace("Order: ", "Ordr: "),
             "has no Deep: and no Order: line"),
            (GOAL_A.replace("docker 1-12.", "docker 1-13."), "goal names step 13 of docker, which has 12 steps"),
            (GOAL_A.replace("networking-basics 2-4; docker 1-12.", "networking-basics 2-4; docker 1-12; wizard-craft."),
             "goal names 'wizard-craft', which is no card and no planned subject of this map; fix the id"),
            (GOAL_A.replace("networking-basics 2-4; docker 1-12.", "networking-basics two; docker 1-12."),
             "cannot read 'networking-basics two' in Steps:; write card-id N-M, N; card-id"),
            (GOAL_A.replace("Deep: docker 4, 6;", "Deep: docker 4, 6; networking-basics 5;"),
             "Deep: names networking-basics 5, which is not in its Steps:"),
            (GOAL_A.replace("Deep: docker 4, 6;", "Deep: docker 4, 6; kubernetes-core 2;"),
             "Deep: names kubernetes-core 2, which is not in its Steps:"),
            (GOAL_A.replace("linux-command-line 5-6; networking-basics 2-4; docker 4-12", "linux-command-line 5-6; docker 4-12"),
             "networking-basics is in Steps: but not in Order:; name it there, or write 'rows in order'"),
            (GOAL_B.replace("Deep: linux-command-line 5, 8; docker 4, 7.", "Deep: linux-command-line 14."),
             "goal names step 14 of linux-command-line, which has 13 steps")):
        cur = fresh()
        set_goals(cur, goals + "\n" + (GOAL_B if "Platform" not in goals else GOAL_A))
        errs = fails(cur, msg)
        check(len(errs) == 1, errs)
    cur = fresh()
    set_goals(cur, GOAL_A)
    fails(cur, "'## Goals' has 1 goal blocks; give 2 to 5")
    cur = fresh()                     # wrapped lines, row order, a planned subject in Steps
    set_goals(cur, GOAL_A.replace("Order: linux", "Order: (row order, except)\n  linux") + "\n" +
              GOAL_B.replace("docker.\n", "docker;\n  kubernetes-internals.\n").replace("rows in order", "row order"))
    passes(cur)


def add_goal(cur, item):
    """Add a goal item at the end of the map's Goals; returns its line number."""
    text = read(MAP(cur))
    at = text.index("\n\n## Why this order")
    write(MAP(cur), text[:at] + "\n" + item + text[at:])
    return text[:at].count("\n") + 2


@test
def check_goals_name_rows_and_steps_that_exist():
    cur = old_goals(fresh())
    add_goal(cur, "- Hold my own (about 125 h): docker 1-2, 6; networking-basics 2 and 4; rows 1 to 3; row 3 steps "
                  "1-4, 6;\n  row 4 steps 1-9 (planned: not counted); rows 1, 2 and 4; linux-command-line 1-3 (needs "
                  "row 1 step 2).")
    passes(cur)
    for bad, msg in (("docker 1-2, 13", "goal names step 13 of docker, which has 12 steps"),
                     ("networking-basics 2 and 9", "goal names step 9 of networking-basics, which has 6 steps"),
                     ("rows 1 to 6", "goal names row 6, which the map does not have"),
                     ("rows 1, 2 and 5", "goal names row 5, which the map does not have"),
                     ("row 3 steps 1-4, 13-14", "goal names step 13 of docker, which has 12 steps"),
                     ("row 7 steps 1-2", "goal names row 7, which the map does not have"),
                     ("wizard-craft 1-3", "goal names 'wizard-craft', which is no card and no planned subject of this "
                                          "map; fix the id")):
        cur = old_goals(fresh())
        line = add_goal(cur, "- Broken goal: %s." % bad)
        errs = fails(cur, "curriculum/devops/containers.md:%d %s" % (line, msg))
        check(len(errs) == 1 if "13-14" not in bad else len(errs) == 2, errs)
    cur = fresh()                     # a planned subject of the map, and words that are no ids, pass
    add_goal(cur, "- Later: kubernetes-internals 1-3 after about 40 hours, in 2 weeks.")
    passes(cur)

def shell_card(**kw):
    """linux-shell (six steps, in no map) with these card() arguments."""
    return card("linux-shell", **kw)


def blocks_but(changes, steps=6):
    """The generated blocks of linux-shell with {step: block text or None (left out)} changed."""
    return "\n".join(changes.get(k, step_block("linux-shell", k)) for k in range(1, steps + 1)
                     if changes.get(k, "") is not None)


@test
def check_step_notes_of_a_deepened_card():
    cur = fresh()
    for kw, msg in (
            ({"blocks": blocks_but({6: None})}, "step 6 has no block in Step notes; add '### 6' with Need:, Show:"),
            ({"blocks": blocks_but({}) + "\n" + step_block("linux-shell", 7)},
             "Step notes has a block for step 7, which the card does not have"),
            ({"blocks": blocks_but({2: step_block("linux-shell", 2).replace("Show: run `cmd2` twice and compare: "
                                                                           "the second run prints 2.\n", "")})},
             "the Step notes of step 2 have no Show: line; add Show:"),
            ({"blocks": blocks_but({2: "### 2\nNeed: x?\nTry: predict: a; fix: b"})},
             "the Step notes of step 2 have no Show: and no Explain: line"),
            ({"blocks": blocks_but({3: step_block("linux-shell", 3).replace("behave this way?", "behave this way.")})},
             "the Need: of step 3 must be the learner's question, ending with '?'"),
            ({"blocks": blocks_but({4: step_block("linux-shell", 4).replace("; fix: a broken", "; a broken")})},
             "the Try: of step 4 needs two tasks separated by ';', each beginning with predict:"),
            ({"blocks": blocks_but({4: step_block("linux-shell", 4).replace("Try: predict: what", "Try: what")})},
             "the Try: of step 4 needs two tasks"),
            ({"blocks": blocks_but({4: step_block("linux-shell", 4).replace("### 4", "### four")})},
             "a block of Step notes is headed '### N' (the step's number); fix '### four'"),
            ({"blocks": blocks_but({}) + "\n" + step_block("linux-shell", 3)}, "step 3 has two blocks of Step notes"),
            ({"deep": None}, "no valid 'Deep steps:' line: make the first item of 'Go deep, leave for later' "
                             "'- Deep steps: N, N (why)' naming 1 to 3 steps the card has"),
            ({"deep": "1, 2, 3, 4"}, "naming 1 to 3 steps"),
            ({"deep": "2, 9"}, "naming 1 to 3 steps"),
            ({"steps": 8, "deep": "5"}, "naming 2 to 4 steps"),
            ({"words": "[1] a, b, c, d, e; [2-6] f"}, "step 1 owns 5 words (four at most): put the rest in brackets"),
            ({"words": "[1] a; [2] b, c, d, e, f, g; [3-6] h"}, "step 2 owns 6 words (five at most)"),
            ({"words": "[1] a; [2-3] b, c, d; [3] e, f, g; [4-6] h"}, "step 3 owns 6 words (five at most)")):
        write(cardpath(cur, "linux-shell"), shell_card(**kw))
        errs = fails(cur, msg)
        check(len(errs) == (2 if "'### four'" in msg else 1), (msg, errs))     # '### four' also leaves step 4 without a block
    for kw in ({"deep": "4"}, {"deep": "1-3"}, {"steps": 8, "deep": "2, 3, 5, 8"},
               {"words": "[1] a, b, c, d, (e), (f); [2] b2, c2, d2, e2, f2, (g); [3-6] h"},
               {"blocks": blocks_but({2: "### 2\nNeed: why\n  this, really?\nShow: run `x` and see 3.\n"
                                         "Explain: It loops.\nPicture: a thermostat;\n  it breaks when cold.\n"
                                         "Try: predict: a; then b; recall: c"})}):
        write(cardpath(cur, "linux-shell"), shell_card(**kw))
        out = passes(cur)
        check(not any(l.startswith("note: ") for l in out), (str(kw)[:80], out))


@test
def check_notes_on_size_and_undeepened_cards():
    cur = fresh()
    long_step = "2. Step 2 with `cmd` " + "and many more words " * 16 + "at the end."
    order = "\n".join(["1. Step 1 `a`.", long_step] + ["%d. Step %d `x`." % (k, k) for k in range(3, 7)])
    write(cardpath(cur, "linux-shell"), shell_card(order=order, blocks=blocks_but({
        3: step_block("linux-shell", 3).replace("Explain: The loop", "Explain: " + "Long words go on here. " * 30 +
                                                "The loop")})))
    out = passes(cur)
    notes = [l for l in out if l.startswith("note: ")]
    check(len(notes) == 2 and re.match(r"^note: curriculum/cards/linux-shell\.md:18: step 2 is about \d+ tokens; a "
                                       r"step line is lean \(about 60\): move the detail into its Step notes$", notes[0])
          and re.match(r"^note: curriculum/cards/linux-shell\.md:\d+: the Step notes of step 3 are about \d+ tokens "
                       r"\(about 200 at most\): keep what makes it land$", notes[1]), notes)
    write(cardpath(cur, "linux-shell"), shell_card(notes=False, words="[1] a, b, c, d, e, f; [2-6] g"))
    errs = fails(cur)                 # not yet deepened: one error, none of the others (no Deep steps line)
    check(errs == ['ERROR curriculum/cards/linux-shell.md not yet deepened: no "Step notes" part; add a \'### N\' '
                   'block for each step with Need:, Show:, Explain: and Try:'], errs)


@test
def check_shared_words_count_owned_words_only():
    cur = fresh()
    write(cardpath(cur, "linux-shell"), shell_card(needs="container-internals", words="[1] pipe, (cgroup); [2-6] glob"))
    write(cardpath(cur, "container-internals"), card("container-internals", words="[1] cgroup; [2-6] ns"))
    out = passes(cur)
    check(not any("also owned by" in l for l in out), out)
    write(cardpath(cur, "linux-shell"), shell_card(needs="container-internals", words="[1] pipe, cgroup; [2-6] glob"))
    out = passes(cur)
    check(any("word 'cgroup' is also owned by container-internals" in l for l in out), out)


@test
def goal_command():
    cur = fresh()
    code, out = run(cur, "goal", "devops/containers")
    check(code == 0 and out == ["1  Ship my own service in a container (about 55 h)",
                                "2  Move from developer to platform engineer (about 70 h)"], out)
    code, out = run(cur, "goal", "devops/containers", "1")
    i = out.index("")
    check(code == 0 and out[0] == "### Ship my own service in a container (about 55 h)" and
          out[1] == "Steps: linux-command-line 1-6; networking-basics 2-4; docker 1-12." and
          any(l.startswith("Halfway: ") for l in out[:i]) and out[i + 1] == "track: devops/containers 1-3" and
          out[i + 2] == "", out)
    check(out[i + 3] == spine_first(21, 3, 49), out[i + 3])     # 20 x 6/13 = 9, 20 x 3/6 = 10, 30
    check("Teaching order (steps 2-4 of 6):" in out and "Teaching order (steps 1-6 of 13):" in out, out)
    code, out = run(cur, "goal", "devops/containers", "platform", "engineer")
    check(code == 0 and out[0] == "### Move from developer to platform engineer (about 70 h)" and
          "Order: rows in order; networking-basics may be `held` by a working backend developer." in out, out)
    j = out.index("")
    check(out[j + 1] == "track: devops/containers 1-3" and "Teaching order (steps 1-13 of 13):" in out, out)
    for args, code_want, first in ((("3",), 2, "devops/containers has goals 1 to 2"),
                                   (("quantum",), 2, "no goal of devops/containers matches 'quantum'")):
        code, out = run(cur, "goal", "devops/containers", *args)
        check(code == code_want and out[0].startswith(first), (args, out))
    code, out = run(cur, "goal", "devops/nowhere", "1")
    check(code == 1 and out[0].startswith("no track map 'devops/nowhere'"), out)
    old_goals(cur)
    code, out = run(cur, "goal", "devops/containers", "1")
    check(code == 0 and out == ["devops/containers still has its Goals in the old form (a list), with no goal blocks; "
                                "its Goals:"] + OLD_GOALS.splitlines(), out)

# ---------------------------------------------------------------- check: the rest


@test
def check_roles():
    cur = fresh()
    edit(ROLE(cur), "| docker | 3 Build | essential |", "| docker | 3 Build | vital |")
    fails(cur, "class 'vital' is not one of essential, desirable, specialist")
    cur = fresh()
    edit(ROLE(cur), "| docker | 3 Build | essential |", "| docker | Build | essential |")
    fails(cur, "level 'Build' is not one of")
    cur = fresh()
    edit(ROLE(cur), "| docker | 3 Build |", "| dockers | 3 Build |")
    fails(cur, "'dockers' has no card; write 'dockers (planned)'")
    cur = fresh()
    text = read(ROLE(cur))
    for ident in ("linux-command-line", "docker"):
        text = text.replace("| %s |" % ident, "| %s (planned) |" % ident)
        os.remove(cardpath(cur, ident))
        edit(MAP(cur), "| %s |" % ident, "| %s (planned) |" % ident)
    write(ROLE(cur), text)
    edit(cardpath(cur, K8S), "needs: docker, networking-basics", "needs: networking-basics")
    fails(cur, "the role names no card")
    edit(ROLE(cur), "| docker (planned) |", "| docker-x |")
    write(cardpath(cur, "docker-x"), card("docker-x"))
    passes(cur)


@test
def check_status_lines():
    for status, ok in (("built 2026-11-18", True), ("reviewed 2026-11-18", True), ("tested 2026-11-18 by Ann Lee", True),
                       ("reviewed 2026-11-18 by agent 7", True), ("built 2026-11-18 by Ann", False),
                       ("done 2026-11-18", False), ("built 2026-13-01", False), ("built 18.11.2026", False),
                       ("reviewed 2026-11-18 by", False), ("built", False)):
        cur = fresh()
        write(cardpath(cur, "docker"), card("docker", status=status))
        if ok:
            passes(cur)
        else:
            fails(cur, "cards/docker.md:4 status '%s' cannot be read" % status)
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", status=""))
    fails(cur, "'status:' is empty")


@test
def check_sources_not_empty():
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", sources=""))
    fails(cur, "cards/docker.md:5 'sources:' is empty")
    for path in (MAP, ROLE):
        cur = fresh()
        text = re.sub(r"(?m)^sources: .*$", "sources:", read(path(cur)))
        write(path(cur), text)
        fails(cur, "'sources:' is empty")
    cur = fresh()
    edit(ROLE(cur), "sources: ", "")
    fails(cur, "no 'sources:' line")


@test
def check_known_mistakes_by_subject():
    wrong = "\nKubernetes Secrets are encrypted, so a password there is safe."
    cur = fresh()
    write(cardpath(cur, "kubernetes-extra"), card("kubernetes-extra", body=wrong))
    errs = fails(cur, "known mistake (kubernetes): Kubernetes Secrets are stored unencrypted")
    check(errs[0].startswith("ERROR curriculum/cards/kubernetes-extra.md:"), errs)
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", body=wrong))
    passes(cur)                                         # a shell card is not about kubernetes
    cur = fresh()
    write(cardpath(cur, "kubernetes-extra"), card("kubernetes-extra", body=wrong.replace(
        "are encrypted,", "are encrypted only if encryption at rest is on,")))
    passes(cur)
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", body="\nIn Python 0.1 + 0.2 = 0.3 exactly."))
    fails(cur, "known mistake (*)")
    cur = fresh()
    write(cardpath(cur, "linux-shell"), card("linux-shell", aliases="git", body="\n`git pull` is the same as `git fetch`."))
    fails(cur, "known mistake (git)")


@test
def check_strays_and_index_listing():
    cur = fresh()
    write(os.path.join(cur, "notes.md"), "# Notes\n")
    fails(cur, "curriculum/notes.md not a curriculum file")
    cur = fresh()
    write(os.path.join(cur, "cards", "old", "x.md"), "# x\n")
    fails(cur, "curriculum/cards/old/x.md not a curriculum file")
    cur = fresh()
    edit(INDEX(cur), "| containers |", "| boxes |")
    fails(cur, "curriculum/devops/INDEX.md track 'containers' (curriculum/devops/containers.md) is not listed")
    cur = fresh()
    os.remove(INDEX(cur))
    fails(cur, "domain 'devops' has track maps but no INDEX.md")
    cur = fresh()
    write(os.path.join(cur, "cards", "notes.txt"), "not markdown\n")
    passes(cur)


@test
def check_error_lines_name_file_and_fix():
    cur = fresh()
    edit(cardpath(cur, "docker"), "kind: tool", "kind: gadget")
    edit(MAP(cur), "| 20 | 2 Explain |", "| x | 2 Explain |")
    errs = fails(cur)
    check(len(errs) == 2, errs)
    check(any(e.startswith("ERROR curriculum/cards/docker.md:2 ") and "use one of" in e for e in errs), errs)
    check(any(re.match(r"^ERROR curriculum/devops/containers\.md:\d+ hours 'x' must be a number", e) for e in errs), errs)

# ---------------------------------------------------------------- spine, steps, words


def spine_first(steps, cards, hours, unknown=""):
    """The outline's first line."""
    return ("Outline for the plan (%d steps from %d cards). Plan for the learner's goal and in the learner's own "
            "setting; group steps into chapters; account for every step with from:, held: or later:. All of it at "
            "full depth is about %d hours%s: fit the learner's budget by leaving depth for later, never a card the "
            "goal names." % (steps, cards, hours, " (left out, no hours known: %s)" % unknown if unknown else ""))


@test
def spine_whole_card():
    cur = fresh()
    code, out = run(cur, "spine", K8S)
    check(code == 0 and out[0] == spine_first(8, 1, 0, K8S) and out[1] == "", out[:3])
    check(out[2] == "## kubernetes-core: Kubernetes for people who will run services on it (kind tool; needs: docker, "
                    "networking-basics; 8 steps)", out[2])
    check(out[3] == "Promise: Deploy, expose, update and debug a small service on a cluster, and explain what each part "
                    "of the cluster did.", out[3])
    check(out[4].startswith("The one idea: You state what you want; loops keep making it true. Picture: a thermostat. "
                            "Where it breaks: there are many loops,") and out[4].endswith("what you asked for."), out[4])
    check(out[5] == "In production:" and out[6].startswith("- Clusters are usually managed"), out[5:7])
    i = out.index("Teaching order:")
    check([l[:2] for l in out[i + 1:i + 9]] == ["%d." % k for k in range(1, 9)], out[i:i + 10])
    check(out[i + 9] == "Go deep, leave for later:" and "Mastery ladder:" in out, out[i + 9:])
    check(out[-1] == "Project: the learner's own small web service with a database, deployed from files, surviving the "
                     "loss of a pod; finish line: a script of five checks all pass.", out[-1])
    joined = "\n".join(out)
    for gone in ("State and danger", "Never omit", "Pods are restarted", "CrashLoopBackOff", "Words to own",
                 "pod, node", "Guided:", "[3]"):
        check(gone not in joined, gone)


@test
def spine_with_step_ranges_and_several_cards():
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", steps=6, practice="Guided: build three images and compare their sizes."))
    code, out = run(cur, "spine", K8S + ":4-6", "docker:1,3")
    check(code == 0 and out[0] == spine_first(5, 2, 10, K8S), out[:1])
    i = out.index("## docker: docker for testers (kind tool; needs: none; 6 steps)")
    check(out[i + 1] == "About 10 hours at full depth (track devops/containers)." and out[i + 2].startswith("Promise:"),
          out[i:i + 3])
    check(not any(l.startswith("About") for l in out[:i]), out)
    i = out.index("Teaching order (steps 4-6 of 8):")
    check(out[i + 1:i + 4] == ["4. Services and cluster DNS: one stable name for pods whose addresses keep changing.",
                               "5. ConfigMaps and Secrets: configuration outside the image.",
                               "6. Probes, rolling updates and `kubectl rollout undo`."], out[i:i + 5])
    check(out[i + 4] == "Go deep, leave for later:", out[i + 4])
    i = out.index("Teaching order (steps 1, 3 of 6):")
    check(out[i + 1:i + 3] == ["1. Step 1, made and broken on purpose.", "3. Step 3, made and broken on purpose."], out[i:])
    check("## docker: docker for testers (kind tool; needs: none; 6 steps)" in out, out)
    check(out[-1] == "Practice and project: Guided: build three images and compare their sizes.", out[-1])
    cur2 = fresh()                   # a step that wraps onto an indented line is printed as written
    write(cardpath(cur2, "docker"), card("docker", steps=6, order="1. One `x`.\n2. Two `y`,\n   and more.\n3. Three 3.\n"
                                         "4. Four 4.\n5. Five 5.\n6. Six 6."))
    code, out = run(cur2, "spine", "docker:2")
    i = out.index("Teaching order (steps 2 of 6):")
    check(out[i + 1:i + 3] == ["2. Two `y`,", "   and more."] and out[0] == spine_first(1, 1, 5), out)


@test
def spine_unknown_card_step_or_planned_subject():
    cur = fresh()
    for args, want in ((("nope",), "no card 'nope'; try: python3 scripts/us_path.py find nope"),
                       ((K8S + ":9",), "kubernetes-core has steps 1 to 8; step 9 does not exist"),
                       ((K8S + ":2-x",), "steps '2-x' of kubernetes-core cannot be read; write them like 4-8 or 1,3,5-6"),
                       ((K8S, "docker:0,13"), "docker has steps 1 to 12; step 0, 13 does not exist")):
        code, out = run(cur, "spine", *args)
        check(code == 2 and out == [want], (args, out))
    edit(MAP(cur), "\n\n## Goals", "\n| 5 | helm (planned) | 3 | charts | charts | 10 | 1 Use |\n\n## Goals")
    code, out = run(cur, "spine", "helm", "docker:1")
    check(code == 0 and out[0] == spine_first(1, 1, 3, "helm"), out)      # 30 h x 1/12, rounded
    check(out[2] == "## helm: no card yet (a planned subject of a track map); plan its steps from the learner's goal "
                    "and sources you read", out[2])


@test
def spine_gives_hours_from_the_track_map():
    cur = fresh()
    code, out = run(cur, "spine", "docker", "networking-basics")
    check(code == 0 and out[0] == spine_first(18, 2, 50), out[0])
    check("About 30 hours at full depth (track devops/containers)." in out and
          "About 20 hours at full depth (track devops/containers)." in out, out)
    code, out = run(cur, "spine", "networking-basics:1-2", "linux-command-line:1-9")   # 20 x 2/6 = 6.7, 20 x 9/13 = 13.8
    check(out[0] == spine_first(11, 2, 21) and "About 7 hours at full depth (track devops/containers)." in out
          and "About 14 hours at full depth (track devops/containers)." in out, out)
    write(os.path.join(cur, "devops", "zeta.md"), read(MAP(cur)).replace("| 30 | 3 Build |", "| 60 | 3 Build |"))
    code, out = run(cur, "spine", "docker", "--track", "devops/zeta")    # the given track's hours, not the first map's
    check(code == 0 and "About 60 hours at full depth (track devops/zeta)." in out, out)
    code, out = run(cur, "goal", "devops/zeta", "1")
    check(code == 0 and spine_first(21, 3, 79) in out and "About 60 hours at full depth (track devops/zeta)." in out,
          out)
    code, out = run(cur, "spine", "docker")
    check(code == 0 and "About 30 hours at full depth (track devops/containers)." in out, out)
    os.remove(os.path.join(cur, "devops", "zeta.md"))
    edit(MAP(cur), "| 30 | 3 Build |", "| many | 3 Build |")
    code, out = run(cur, "spine", "docker", "linux-command-line")
    check(out[0] == spine_first(25, 2, 20, "docker") and not any("About 30" in l for l in out), out)


def block_of(ident, k, deep=False):
    """What `steps` prints for the generated step k up to its words (Need, Show, Explain)."""
    return ["  Need: why does `cmd%d` of %s behave this way?" % (k, ident),
            "  Show: run `cmd%d` twice and compare: the second run prints %d." % (k, k),
            "  Explain: The loop of %s repeats the work %d times." % (ident, k)]


def try_of(k):
    return "  Try: predict: what `cmd%d` prints; fix: a broken `cmd%d` (finish line: it prints %d)." % (k, k, k)


@test
def steps_prints_each_step_with_its_own_notes():
    cur = fresh()
    code, out = run(cur, "steps", K8S + ":5-6")
    want = (["kubernetes-core, steps 5-6 of 8", "5. ConfigMaps and Secrets: configuration outside the image."] +
            block_of(K8S, 5) +
            ["  Teach against:",
             '  - "Secrets are encrypted" (only base64-encoded unless encryption at rest is switched on).',
             "  Words to own: configmap, secret", try_of(5),
             "6. Probes, rolling updates and `kubectl rollout undo`."] + block_of(K8S, 6) +
            ["  Goes wrong:", "  - A rollout stuck on a failing readiness probe.", "  Words to own: probe, rollout",
             try_of(6),
             "State and danger:",
             "- `kubectl delete namespace` removes everything in it without asking: never on a shared cluster.",
             "Never omit:", "- Delete things and watch them recover, in every step.",
             "- Memory limits and what `OOMKilled` means.",
             "Practice: Guided: repeat each step's experiment with one thing changed. On your own: given a manifest, "
             "predict what the cluster will do, then check."])
    check(code == 0 and out == want, out)
    code, out = run(cur, "steps", K8S + ":1,8")         # FORMAT.md's own block 1, a deep step, met words
    check(out[1:6] == [
        "1. One pod by hand: `kubectl run`, then delete it; nothing brings it back.",
        "  Need: I can run a container on my laptop; why does a cluster need a new word, \"pod\", for the same thing?",
        "  Show: `kubectl run web --image=<your image>`, then `kubectl delete pod web`, then `kubectl get pods`. The "
        "learner expects it to come back; nothing does. (From kubernetes.io \"Pods\": a bare pod is not rescheduled.)",
        "  Explain: A pod is one run of your containers on one node; nothing owns it, so nothing replaces it.",
        "  Words to own: pod"], out)
    check(out[6] == "  Met in passing: node" and out[7].startswith("  Try: predict: what `kubectl get pods` shows"), out)
    i = out.index("8. Debugging with `kubectl describe`, events and logs: the failures below, each made on purpose and "
                  "repaired. (a deep step: give it the chapter's best pages)")
    check(out[i + 4:i + 9] == ["  Goes wrong:", "  - `Pending`: no node has the requested memory or processor.",
                               "  - `CrashLoopBackOff`: the container starts and exits; the reason is in `kubectl logs "
                               "--previous`.", "  - `ImagePullBackOff`: a wrong image name or missing registry secret.",
                               "  - A Service with no endpoints: its selector matches no pod's labels."], out[i:])
    check("  Words to own: event" in out and "  Met in passing: namespace" in out, out)
    code, out = run(cur, "steps", K8S + ":2,8")          # an item tagged [2,8] goes under step 2 only
    check(sum(1 for l in out if "`Pending`" in l) == 1 and out.index("  - `Pending`: no node has the requested memory "
          "or processor.") < out.index("8. Debugging with `kubectl describe`, events and logs: the failures below, each "
                                       "made on purpose and repaired. (a deep step: give it the chapter's best pages)"), out)
    check("2. A Deployment: delete its pod; a new one appears. The loop is the lesson. (a deep step: give it the "
          "chapter's best pages)" in out, out)


@test
def steps_of_two_cards_every_tag_form_and_the_old_form():
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", steps=8, part="- [3] three `x`.\n- [5-6] fivesix `y`.\n"
                                        "- [2,8] twoeight `z`.\n- [1,4-6] onefoursix `w`.\n- untagged `v`.",
                                        words="[1] loop; [2-8] reconcile, (glob); [5] probe", never="- [7] seven only.",
                                        belief='- [6] "Belief six" (truth).', failures="- [1,5] Fails one or five.",
                                        numbers="- [5] 5 ms a call (run here).\n- 1 GB of memory (run here)."))
    code, out = run(cur, "steps", "docker:5", K8S + ":1")
    k = out.index("kubernetes-core, step 1 of 8")
    check(code == 0 and out[:k] == ["docker, step 5 of 8", "5. Step 5, made and broken on purpose."] +
          block_of("docker", 5) + ["  Goes wrong:", "  - Fails one or five.", "  State and danger:",
                                   "  - fivesix `y`.", "  - onefoursix `w`.", "  Believable numbers:",
                                   "  - 5 ms a call (run here).", "  Words to own: reconcile, probe",
                                   "  Met in passing: glob", try_of(5), "State and danger:", "- untagged `v`.",
                                   "Believable numbers:", "- 1 GB of memory (run here).",
                                   "Practice: Guided: repeat each step."], out)
    code, out = run(cur, "steps", "docker:2,3")
    check("  - three `x`." in out and "  - twoeight `z`." in out and "  - fivesix `y`." not in out, out)
    check(out.index("  - twoeight `z`.") < out.index("3. Step 3, made and broken on purpose. (a deep step: give it the "
                                                    "chapter's best pages)"), out)
    check("2. Step 2, made and broken on purpose. (a deep step: give it the chapter's best pages)" in out, out)
    code, out = run(cur, "steps", "docker:5-7")
    check(out[-3:-1] == ["Never omit:", "- seven only."], out)
    write(cardpath(cur, "linux-shell"), card("linux-shell", notes=False))       # the old form: no step notes
    code, out = run(cur, "steps", "linux-shell:2")
    check(code == 0 and out == ["linux-shell, step 2 of 6", "2. Step 2, made and broken on purpose.", "  Goes wrong:",
                                "  - It does not start: the name is wrong.", "  Words to own: linux-shell reconcile",
                                "State and danger:", "- `wipe --all` deletes the work: use `wipe --dry-run` first.",
                                "Never omit:", "- Break it and watch it recover.", "Practice: Guided: repeat each step."],
          out)
    code, out = run(cur, "steps", "docker")
    check(code == 2 and out == ["give the steps: docker:STEPS, such as docker:1-3 or docker:2,5"], out)
    code, out = run(cur, "steps", "docker:9")
    check(code == 2 and out == ["docker has steps 1 to 8; step 9 does not exist"], out)


@test
def words_of_a_card_and_a_track():
    cur = fresh()
    code, out = run(cur, "words", K8S)
    check(code == 0 and out == ["kubernetes-core: pod, (node), deployment, replica, desired state, reconcile, control "
                                "plane, scheduler, kubelet, (etcd), service, selector, label, (endpoint), configmap, "
                                "secret, probe, rollout, volume, claim, event, (namespace)"], out)       # met in brackets
    edit(MAP(cur), "| 2 | networking-basics |", "| 2 | networking-basics (planned) |")
    os.remove(cardpath(cur, "networking-basics"))
    code, out = run(cur, "words", "devops/containers", "docker")
    check(code == 0 and out == ["linux-command-line: linux-command-line loop, linux-command-line state, "
                                "linux-command-line reconcile", "networking-basics: (planned: no card yet)",
                                "docker: docker loop, docker state, docker reconcile",
                                "kubernetes-internals: (planned: no card yet)",
                                "docker: docker loop, docker state, docker reconcile"], out)
    code, out = run(cur, "words", "nothing")
    check(code == 2 and out[0].startswith("no card or track 'nothing'"), out)

# ---------------------------------------------------------------- ready


def product():
    """A copy of the scripts and rules in TMP, so that understudy.yaml can point at a test shelf."""
    home = os.path.join(TMP, "product")
    if not os.path.isdir(home):
        for name in ("scripts", "rules"):
            shutil.copytree(os.path.join(ROOT, name), os.path.join(home, name),
                            ignore=shutil.ignore_patterns("__pycache__"))
        write(os.path.join(home, "AGENTS.md"), read(os.path.join(ROOT, "AGENTS.md")))
    return home


def ready(cur, shelf, *args):
    """Run `us_path.py ready junior-devops-engineer` with the books under shelf/book and records in shelf/private."""
    home = product()
    write(os.path.join(home, "understudy.yaml"), "book: %s\nprivate: %s\n" % (os.path.join(shelf, "book"),
                                                                          os.path.join(shelf, "private")))
    env = dict(os.environ, UNDERSTUDY_CURRICULUM=cur)
    env.pop("UNDERSTUDY_PRIVATE", None)
    proc = subprocess.run([sys.executable, os.path.join(home, "scripts", "us_path.py"), "ready",
                           "junior-devops-engineer"] + list(args), capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + proc.stderr).splitlines()


CHAPTER = """# Chapter 1: Shell

## 1.1 Thing

Some text about the thing.

**Check yourself**

1. What is a thing?

<details><summary>Answer</summary>

A thing.

</details>

2. What is another thing?

<details><summary>Answer</summary>

Another.

</details>
"""


def shelf_book(shelf, plan_head, written=False):
    """A book `shell` on a shelf: PLAN.md with its header lines; chapter 1 teaches linux-command-line 1-3."""
    book = os.path.join(shelf, "book", "shell")
    write(os.path.join(book, "PLAN.md"), "# Shell\nfor: testers\nrun: none\n%s\n### 1 Shell\n"
          "from: linux-command-line 1-3\n1.1 Thing | teaches: thing\n" % plan_head)
    if written:
        write(os.path.join(book, "chapters", "01-shell.md"), CHAPTER)
    return book


def answer(shelf, book, marks):
    """Record the latest answers to chapter 1's questions in practice.json, as us_practice.py keeps them."""
    sys.path.insert(0, SCRIPTS)
    import us_practice
    keys = [q["key"] for q in us_practice.book_questions(book, 1)]
    check(len(keys) == 2, keys)
    store = {k: {"book": "shell", "section": "1.1", "title": "Thing", "question": "q", "box": 1, "due": "",
                 "history": ["2026-11-1%d 10:00:00 %s" % (i, m) for i, m in enumerate(ms)]}
             for k, ms in zip(keys, marks) if ms}
    write(os.path.join(shelf, "private", "practice.json"), __import__("json").dumps(store))


HONEST = 'This counts what your books and practice records show. The "Proved by" task of each line is the real test.'


@test
def ready_with_no_books():
    cur = fresh()
    code, out = ready(cur, os.path.join(TMP, "shelf-empty"))
    check(code == 0 and out == [
        "junior-devops-engineer: 0% ready (essential lines weigh 3, desirable 2; specialist lines with --all); "
        "0 books on the shelf",
        "linux-command-line  needs 3 Build  essential  0% ready (0% declared)  weakest step: 1 Step 1, made and broken "
        "on purpose",
        "docker              needs 3 Build  essential  0% ready (0% declared)  weakest step: 1 Step 1, made and broken "
        "on purpose",
        "Essential: 0%   Essential and desirable: 0%",
        "Needed first, though not on this role's list: networking-basics (for docker)",
        "Next: linux-command-line (0%)",       # docker waits for linux-command-line, a line of the role
        HONEST], out)
    code, out = ready(cur, os.path.join(TMP, "shelf-empty"), "--all")
    check(code == 0 and "kubernetes-internals  needs 2 Explain  specialist  0% ready  no card yet" in out
          and out[0].startswith("junior-devops-engineer: 0% ready (essential lines weigh 3, desirable 2, specialist 1)"),
          out)
    check(ready(cur, os.path.join(TMP, "shelf-empty"), "--have", "x")[0] == 2, "bad --have accepted")
    check(run(cur, "ready", "nobody")[0] == 1, "unknown role accepted")


@test
def ready_with_a_held_card_and_have():
    cur = fresh()
    shelf = os.path.join(TMP, "shelf-held")
    shelf_book(shelf, "held: docker (placement test)\nlater: linux-command-line 4-6")
    code, out = ready(cur, shelf)
    check(code == 0 and out[0].startswith("junior-devops-engineer: 50% ready") and out[0].endswith("1 book on the shelf"),
          out)
    check(out[2] == "docker              needs 3 Build  essential  100% ready (100% declared)  weakest step: none "
                    "(all declared)", out)
    check(out[1].startswith("linux-command-line  needs 3 Build  essential  0% ready (0% declared)"), out)
    check(out[3] == "Essential: 50%   Essential and desirable: 50%" and out[4] == "Needed first, though not on this role's list: networking-basics (for docker)"
          and out[5] == "Next: linux-command-line (0%)", out)
    code, out = ready(cur, shelf, "--have", "linux-command-line:3")
    check(out[1] == "linux-command-line  needs 3 Build  essential  100% ready (100% declared)  weakest step: none "
                    "(all declared)" and out[3] == "Essential: 100%   Essential and desirable: 100%"
          and out[5] == "Next: nothing left", out)
    code, out = ready(cur, shelf, "--have", "linux-command-line:2")
    check(out[1].startswith("linux-command-line  needs 3 Build  essential  0% ready (0% declared)"), out)


@test
def ready_with_a_written_chapter_and_answers():
    cur = fresh()
    shelf = os.path.join(TMP, "shelf-written")
    write(cardpath(cur, "linux-command-line"), card("linux-command-line", steps=6))    # six steps: the sums below
    book = shelf_book(shelf, "held: linux-command-line 6", written=True)
    answer(shelf, book, [["y"], ["n"]])            # half right: steps 1-3 at 0.25 + 0.75 x 1/2, step 6 held
    code, out = ready(cur, shelf)
    check(code == 0 and out[1] == "linux-command-line  needs 3 Build  essential  48% ready (17% declared)  weakest "
                                  "step: 4 Step 4, made and broken on purpose", out)
    answer(shelf, book, [["y"], ["n", "y"]])       # the latest answer counts
    code, out = ready(cur, shelf)
    check(out[1].startswith("linux-command-line  needs 3 Build  essential  67% ready (17% declared)"), out)
    answer(shelf, book, [["n"], ["y", "n"]])       # all wrong: only the written chapter counts
    code, out = ready(cur, shelf)
    check(out[1].startswith("linux-command-line  needs 3 Build  essential  29% ready (17% declared)"), out)
    check(out[3] == "Essential: 15%   Essential and desirable: 15%", out)
    check(out[5] == "Next: linux-command-line (29%)" and out[-1] == HONEST and len(out) == 7, out)

@test
def ready_next_suggests_what_can_start_now():
    cur = fresh()
    role = read(ROLE(cur)).replace(
        "| kubernetes-internals (planned) |",
        "| container-internals | 2 Explain | essential | x | y |\n| linux-shell | 2 Explain | desirable | x | y |\n"
        "| networking-basics | 2 Explain | desirable | x | y |\n| kubernetes-internals (planned) |")
    write(ROLE(cur), role)
    write(cardpath(cur, "container-internals"), card("container-internals", needs="docker | linux-shell"))
    shelf = os.path.join(TMP, "shelf-next")
    code, out = ready(cur, shelf)
    # can start now: linux-command-line (essential), then the desirable linux-shell; docker waits for
    # linux-command-line and networking-basics, container-internals for docker or linux-shell
    check(out[-2] == "Next: linux-command-line (0%), linux-shell (0%)", out)      # essential first, then desirable
    check(not any(l.startswith("Needed first") for l in out), out)
    code, out = ready(cur, shelf, "--have", "linux-shell:2")          # one alternative is ready: it can start
    check(out[-2] == "Next: linux-command-line (0%), container-internals (0%)", out)
    code, out = ready(cur, shelf, "--have", "linux-command-line:3")
    check(out[-2] == "Next: linux-shell (0%), networking-basics (0%)", out)       # no essential can start yet
    code, out = ready(cur, shelf, "--have", "linux-command-line:3, networking-basics:2")
    check(out[-2] == "Next: docker (0%), linux-shell (0%)", out)
    code, out = ready(cur, shelf, "--have", "linux-command-line:3, networking-basics:2, linux-shell:2")
    check(out[-2] == "Next: docker (0%), container-internals (0%)", out)

@test
def ready_next_names_only_subjects_with_a_card():
    cur = fresh()
    edit(ROLE(cur), "| kubernetes-internals (planned) | 2 Explain | specialist |",
         "| kubernetes-internals (planned) | 2 Explain | essential |")
    code, out = ready(cur, os.path.join(TMP, "shelf-planned"))
    check(code == 0 and "kubernetes-internals  needs 2 Explain  essential  0% ready  no card yet" in out, out)
    check(out[-2] == "Next: linux-command-line (0%)", out)
    code, out = ready(cur, os.path.join(TMP, "shelf-planned"), "--have", "linux-command-line:3, docker:3")
    check(out[-2] == "Next: nothing left", out)

@test
def ready_shows_every_line_and_what_is_needed_first():
    cur = fresh()
    extra = "".join("| linux-extra-%d | 1 Use | %s | x | y |\n" % (k, "desirable" if k % 2 else "essential")
                    for k in range(22))
    for k in range(22):
        write(cardpath(cur, "linux-extra-%d" % k), card("linux-extra-%d" % k, needs="container-internals | linux-shell"
                                                        if k == 0 else "none"))
    edit(ROLE(cur), "| kubernetes-internals (planned) |", extra + "| kubernetes-internals (planned) |")
    code, out = ready(cur, os.path.join(TMP, "shelf-every"))
    lines = [l.split()[0] for l in out[1:25]]
    check(len(out) == 29 and lines == ["linux-command-line", "docker"] + ["linux-extra-%d" % k for k in range(0, 22, 2)]
          + ["linux-extra-%d" % k for k in range(1, 22, 2)], (len(out), out[24:]))
    check(out[26] == "Needed first, though not on this role's list: networking-basics (for docker), container-internals "
                     "(for linux-extra-0)", out)
    code, out = ready(cur, os.path.join(TMP, "shelf-every"), "--have", "linux-shell:1, networking-basics:2")
    check(not any(l.startswith("Needed first") for l in out), out)
    code, out = run(cur, "role", "junior-devops-engineer", "--have", "linux-shell:1")
    check(out[-1] == "Needed first, though not on this role's list: networking-basics (for docker)", out)


@test
def check_hours_and_level_agree_across_maps():
    cur = fresh()
    other = read(MAP(cur)).replace("# DevOps: containers and orchestration", "# DevOps: another track")
    write(os.path.join(cur, "devops", "other.md"), other)
    edit(INDEX(cur), "| containers |", "| other | anyone | you want it |\n| containers |")
    passes(cur)
    edit(os.path.join(cur, "devops", "other.md"), "| 30 | 3 Build |", "| 40 | 2 Explain |")
    errs = fails(cur, "curriculum/devops/other.md:11 docker is 30 hours in devops/containers and 40 in devops/other: one "
                      "home per fact, make them agree",
                 "docker is level 3 Build in devops/containers and 2 Explain in devops/other: one home per fact")
    check(len(errs) == 2, errs)
    edit(os.path.join(cur, "devops", "other.md"), "| 40 | 2 Explain |", "| 30 | 3 build |")
    passes(cur)


@test
def mark_takes_roles_and_cards_paths_without_md():
    cur = fresh()
    code, out = run(cur, "mark", "roles/junior-devops-engineer", "reviewed", today="2027-01-07")
    check(code == 0 and "\nstatus: reviewed 2027-01-07\n" in read(ROLE(cur)), out)
    code, out = run(cur, "mark", "cards/docker", "tested", today="2027-01-08")
    check(code == 0 and "\nstatus: tested 2027-01-08\n" in read(cardpath(cur, "docker")), out)
    code, out = run(cur, "mark", "roles/nobody", "reviewed")
    check(code == 1 and out[0].startswith("no curriculum file 'roles/nobody'"), out)

# ---------------------------------------------------------------- status and mark


@test
def status_counts_and_stale():
    cur = fresh()
    write(cardpath(cur, "docker"), card("docker", status="reviewed 2026-01-10 by Ann"))
    write(cardpath(cur, "linux-command-line"), card("linux-command-line", status="tested 2025-06-01"))
    code, out = run(cur, "status", today="2026-11-18")
    check(code == 0 and out[0] == "devops: 1 track, cards 1 built / 1 reviewed / 1 tested, 1 planned subject", out)
    check("cards in no track: container-internals, kubernetes-core, linux-shell" in out, out)
    check("roles: 1 (1 built / 0 reviewed / 0 tested)" in out, out)
    i = out.index("older than 12 months (status before 2025-11-18): 1")
    check(out[i + 1] == "  curriculum/cards/linux-command-line.md  tested 2025-06-01" and len(out) == i + 2, out)
    code, out = run(cur, "status", "--stale", "6", today="2026-11-18")
    i = [k for k, l in enumerate(out) if l.startswith("older than 6 months (status before 2026-05-18): 2")]
    check(code == 0 and i and len(out) == i[0] + 3, out)
    code, out = run(cur, "status", "--stale", "24", today="2026-11-18")
    check(out[-1] == "older than 24 months (status before 2024-11-18): none", out)
    check(run(cur, "status", "--stale", "x")[0] == 2, "bad --stale accepted")


@test
def mark_rewrites_status_when_check_passes():
    cur = fresh()
    code, out = run(cur, "mark", "docker", "reviewed", "--by", "agent two", today="2027-01-05")
    check(code == 0 and out == ["curriculum/cards/docker.md: status: reviewed 2027-01-05 by agent two"], out)
    check("\nstatus: reviewed 2027-01-05 by agent two\n" in read(cardpath(cur, "docker")), read(cardpath(cur, "docker")))
    passes(cur)
    code, out = run(cur, "mark", "devops/containers", "tested", today="2027-01-06")
    check(code == 0 and "\nstatus: tested 2027-01-06\n" in read(MAP(cur)), out)
    code, out = run(cur, "mark", os.path.join(cur, "roles", "junior-devops-engineer.md"), "reviewed", today="2027-01-07")
    check(code == 0 and "\nstatus: reviewed 2027-01-07\n" in read(ROLE(cur)), out)
    code, out = run(cur, "mark", "devops", "reviewed", today="2027-01-07")
    check(code == 0 and "\nstatus: reviewed 2027-01-07\n" in read(INDEX(cur)), out)


@test
def mark_refuses_a_failing_file_and_bad_input():
    cur = fresh()
    edit(cardpath(cur, "docker"), "kind: tool", "kind: gadget")
    before = read(cardpath(cur, "docker"))
    code, out = run(cur, "mark", "docker", "reviewed", today="2027-01-05")
    check(code == 1 and out[0] == "curriculum/cards/docker.md does not pass check; fix it first:", out)
    check(out[1].startswith("ERROR curriculum/cards/docker.md:2 kind 'gadget'") and read(cardpath(cur, "docker")) == before, out)
    check(run(cur, "mark", "linux-shell", "reviewed")[0] == 0, "another file's error blocked the mark")
    check(run(cur, "mark", "docker", "built")[0] == 2, "mark built accepted")
    check(run(cur, "mark", "docker", "reviewed", "--by", " ")[0] == 2, "empty --by accepted")
    code, out = run(cur, "mark", "FORMAT.md", "reviewed")
    check(code == 1 and out[0].startswith("no curriculum file 'FORMAT.md'"), out)
    cur = fresh()
    text = read(cardpath(cur, "docker"))
    write(cardpath(cur, "docker"), text + "x" * (20000 - len(text) - 9) + "\n")
    before = read(cardpath(cur, "docker"))
    passes(cur)
    code, out = run(cur, "mark", "docker", "reviewed", "--by", "someone with a long name", today="2027-01-05")
    check(code == 1 and "would not pass check" in out[0] and read(cardpath(cur, "docker")) == before, out)

# ---------------------------------------------------------------- us_check.py --tokens


@test
def tokens_report_counts_curriculum():
    cur = fresh()
    code, out = run(cur, "--tokens", script="us_check.py")
    line = [l for l in out if l.strip().startswith("curriculum:")]
    biggest = max((len(read(cardpath(cur, i))) + 3) // 4 for i in SUPPORT + [K8S])
    check(line == ["  curriculum: 9 files; the planner is handed an outline (us_path.py spine) and each chapter's "
                   "writer the notes of its steps (largest card %d tokens)" % biggest], line)
    always = [l for l in out if "always loaded" in l]
    code2, out2 = run(os.path.join(TMP, "none", "curriculum"), "--tokens", script="us_check.py")
    check([l for l in out2 if "always loaded" in l] == always, "curriculum counted as loaded text")
    check("  curriculum: 0 files; the planner is handed an outline (us_path.py spine) and each chapter's writer the "
          "notes of its steps (largest card none yet)" in out2, out2)


@test
def usage_errors():
    cur = fresh()
    for args in ((), ("bogus",), ("find",), ("card",), ("check", "x"), ("status", "--have", "a:1"),
                 ("find", "x", "--wild"), ("spine",), ("steps",), ("words",), ("ready",), ("spine", "x", "--all"),
                 ("ready", "a", "b")):
        code, out = run(cur, *args)
        check(code == 2 and "Traceback" not in "\n".join(out), (args, out))
    check(run(cur, "--help")[0] == 0, "--help")
    code, out = run(cur, "--help")
    for word in ("spine CARD[:STEPS]", "steps CARD:STEPS", "words CARD|TRACK", "ready ROLE"):
        check(any(word in l for l in out), word)


def main():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok    " + fn.__name__)
            passed += 1
        except Exception as exc:  # noqa: BLE001
            print("FAIL  %s: %s" % (fn.__name__, str(exc).replace("\n", " | ")[:600]))
            failed += 1
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d passed, %d failed" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
