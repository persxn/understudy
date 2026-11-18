# Contributing to understudy

The most useful help is a reader's report: read a chapter and say where it lost you or what is wrong. Open an
issue with the section number. That is the review this system depends on.

To change the system itself, read on.

## How the pieces fit

- **One system prompt.** `AGENTS.md` is the text the agent always loads. `CLAUDE.md` and `GEMINI.md` only point
  to it. It routes every message to one skill and holds the rules that always apply. `understudy.yaml` names
  the learner's two folders, `book/` and `private/`.
- **Nine skills** in `.claude/skills/`: `us-start`, `us-map`, `us-write`, `us-draw`, `us-review`, `us-teach`,
  `us-build`, `us-design`, `us-compete`. Each one is a short list of steps in `SKILL.md`, plus a `references/`
  folder with one small file per topic. The agent reads a reference file only at the step that needs it. Each
  `references/README.md` is that folder's index. `us-map`, `us-write` and `us-review` also have an `assets/`
  folder of templates.
- **Two agents** in `.claude/agents/`: a writer and a reviewer. Writing and reviewing run there, so a chapter
  never fills the main conversation.
- **Scripts** in `scripts/` do the mechanical jobs: running code and pasting its output, drawing figures,
  numbering, checking, indexing, practice. A script costs no tokens.
- **Rules** in `rules/` are short files a skill reads only when it says so. `rules/writers-guide.md` is the
  whole writing method; anything a learner reads follows it.

## The rule for changing this repository

Reuse what a script or rule file already does before adding one. A script beats an instruction, because it
costs no tokens. Keep the always-loaded text small. A change is done when a fresh agent or a script has shown
it working and you have opened that output.

## Size limits

The always-loaded text must be at or under 2,000 tokens, and each skill body under 1,000. Check both with:

```
python3 scripts/us_check.py --tokens
```

## Changing a skill or a reference page

- Keep `SKILL.md` to steps. Move detail into a file under that skill's `references/`, and have the step say
  when to read it.
- When you add, rename or remove a reference file, update the table in that folder's `README.md`, which says
  when each file is read.
- If the change alters which skill a message should reach, update the routing table in `AGENTS.md`.
- Run `python3 scripts/us_check.py --tokens` afterwards.

## Adding a kind of subject

A book's `PLAN.md` names its kind (`kind:`). Today there are five: `language`, `tool`, `framework`, `system`,
`skill`. Each kind has its own files, so a new kind touches all of them:

- the list `KINDS` in `scripts/us_plan.py`, which refuses an unknown kind;
- a plan pattern in `.claude/skills/us-map/references/plan-patterns/`;
- a writing guide in `.claude/skills/us-write/references/kinds/`;
- one finished sample section in `.claude/skills/us-write/references/samples/`, which sets the voice and depth;
- the "shape follows the subject" table in `rules/writers-guide.md`;
- the by-kind pages that exist in other skills, such as `verify-by-kind.md` (`us-review`),
  `lesson-by-kind.md` (`us-teach`) and `project-by-kind.md` (`us-build`);
- the index `README.md` of every folder you touched.

## After a change to a script

Run the tests before and after the change:

```
python3 tests/book/run.py
python3 tests/run/run.py
python3 tests/draw/run.py
python3 tests/tools/run.py
python3 tests/offline/run.py
```

Each prints one line per test and a total, and exits 1 on any failure. Some tests use an optional real book
(the author's C book). They read it from `JOJO_CHAPTERS` and are skipped when it is not set.

## After a change to a skill or a rule

Re-run the three learner cases in `tests/evals/`. `tests/evals/README.md` has the full steps:

1. `git clone` this repository to a scratch folder. Start one fresh agent per case (`python.md`,
   `operating-systems.md`, `usability-testing.md`) with the case file as its task, replacing `FOLDER` with the
   scratch path. Cap each one at 20 minutes.
2. Give each finished chapter to a fresh reader with `reader.md`, which names `RUBRIC.md` and the learner card.
3. A change is good when no line of the last run falls and nothing in the journals blocks.

`tests/evals/routing.md` is a separate, cheap check that messages reach the right skill. The last measured
results and their chapters are in `examples/final-validation/`.
