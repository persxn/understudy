# Setting up and running understudy

## What you need

| Need | For | Notes |
|---|---|---|
| Linux, macOS or WSL | everything | plain Windows is not supported |
| Python 3 | every script | standard library only, nothing to install; tested on Python 3.13 only |
| git | the book is its own repository | |
| Claude Code, logged in | planning, writing, tutoring | reading and practising need no AI |
| The tools of your subject | running a book's programs | a C compiler for a C book, Docker for a Docker book, and so on; the machine check tells you what is missing |

Optional: `gdb` (trace tables for C), `rsvg-convert` or Chrome (PNG copies of figures), `pdftotext` or the `pypdf`
module (notes from your own PDF slides).

## First run

```bash
unzip understudy-skills.zip          # or: git clone <your repository address>
cd skills/understudy                 # the folder that holds AGENTS.md
claude
```

Then say what you want in your own words, for example `I want to learn Git.` The agent creates `book/` (your books,
their own git repository) and `private/` (your records, never pushed), asks a few questions, plans a book and shows
you the contents page before anything is written.

## Every day

| You want to | Do |
|---|---|
| read your books in a browser | `python3 scripts/us_reader.py --serve`, then open http://localhost:8765 |
| practise what is due, with no AI | `python3 scripts/us_practice.py --due` |
| revise key terms as flashcards | `python3 scripts/us_practice.py --cards` |
| test your own project against a chapter's finish line | `python3 scripts/us_practice.py check BOOK N.M --in YOUR-FOLDER` |
| see what you know, in fifteen lines | `python3 scripts/us_practice.py --summary` |
| see your record and weak spots | `python3 scripts/us_practice.py --stats` |
| check this machine can run a book's programs | `python3 scripts/us_doctor.py BOOK` |
| see what a book will cost to write and study | `python3 scripts/us_plan.py cost BOOK` |
| find where something is taught | `python3 scripts/us_find.py WORDS --read` |
| see which facts in a book were checked, and how | open the book's `FACTS.md`, or `python3 scripts/us_check.py BOOK --facts` |
| see the routes the curriculum knows | `python3 scripts/us_path.py index`, then `python3 scripts/us_path.py map DOMAIN/TRACK` |
| see the checked plan for one goal of a route: its steps, how the book opens, the deep steps, the order, then the outline of those steps | `python3 scripts/us_path.py goal DOMAIN/TRACK N` (no N: the goals listed) |
| see what the writer of a chapter is handed: the plan's lines for it, then the curriculum's notes for each of its steps in lesson order | `python3 scripts/us_plan.py brief BOOK N` |
| see what a job asks for and what you still lack | `python3 scripts/us_path.py role ROLE --have "git:3, python-core:2"` |
| score your readiness for a job from your books and practice | `python3 scripts/us_path.py ready ROLE` |
| pick up after a break | open `private/RESUME.md`; it holds the sentence to say to the agent |

## Other agents

`python3 scripts/install.py` makes the same skills and system prompt visible to Codex and Gemini CLI. Their format
was checked against those tools' documentation; the skills have not been run there.

## Checking the install

```bash
python3 scripts/us_check.py --tokens     # must end "check ok"
python3 tests/book/run.py                # each prints "N passed, 0 failed"
python3 tests/tools/run.py
python3 tests/tools/path.py              # the curriculum loader
python3 tests/tools/stage5.py            # plans that draw on the curriculum
python3 scripts/us_path.py check         # the curriculum itself (sizes, step notes, goal blocks): must end "check ok"
python3 tests/offline/run.py
python3 tests/draw/run.py
python3 tests/run/run.py                 # about three minutes
python3 tests/run/state.py               # needs Docker running; skip without it
```

All suites together (23 files under `tests/`, among them the `stage2.py`, `stage3.py`, `path.py` and `stage5.py` files):
758 tests with a Docker daemon running (a few fewer without one: those tests skip). The full list and what each covers is in `docs/FEATURES.md`.

## After you change something

- A script: run the suites above.
- A skill, a rule or a reference page: also re-run the three learner cases in `tests/evals/` and have a fresh reader
  score the chapters (`tests/evals/README.md`).

## If something goes wrong

- `- blocked:` in `private/machine.md`: the machine check found something the book needs and cannot reach; the line
  says what to do. The chapter can still be written; what cannot run is shown as expected output and labelled.
- A script prints an error: the agent is told to show it and stop. Read the message; most name the file, the line
  and the fix.
- Docker's service must be running before a Docker book's sessions can run.
