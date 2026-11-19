# How understudy is built (18 November 2026)

One rule decides most of the design: **a script beats an instruction, because a script costs no tokens.** The model
writes teaching and talks to the learner. Everything mechanical is a Python script that uses only the standard library.

## The parts

| Part | Where | Loaded when | Size |
|---|---|---|---|
| System prompt: routing table and eleven standing rules | `AGENTS.md` (imported by `CLAUDE.md`, `GEMINI.md`) | always | 1,200 tokens |
| Nine skill descriptions | front matter of each `SKILL.md` | always | 792 tokens |
| One skill's steps | `.claude/skills/us-*/SKILL.md` | when a message is routed to it | 516 to 985 tokens |
| Reference pages, templates, samples | `.claude/skills/us-*/references/`, `assets/` | only at the step that names one | 150 to 500 words each; samples up to 3,700 |
| Shared rules | `rules/` | only when a skill says so | 300 to 1,800 tokens each |
| Two helper agents: writer and reviewer | `.claude/agents/` | started by `us-write` and `us-review`, so a chapter never fills the main conversation | |
| Scripts | `scripts/` | run, never read | zero tokens |
| Curriculum: 34 subject cards, 6 track maps, 5 role maps | `curriculum/` | never opened by an agent: `us_path.py` prints one goal's plan and outline when a book is planned, and the notes of a chapter's steps when it is written | about 1,500 to 11,500 tokens once per book (most goals 4,000 to 8,000); about 400 to 1,200 per chapter |

`python3 scripts/us_check.py --tokens` prints these sizes and fails when the always-loaded text passes 2,000 tokens
or a skill reaches 1,000.

## The learner's files

- `book/` is the learner's own git repository. One subject is one book: `PLAN.md` (the contents page, with what each
  section teaches and needs), `BOOK.md` (reader, promise, kind, running project, pictures, names), `PRACTICES.md`
  (habits; facts looked up once, with source and date; what to handle with care), one Markdown file per chapter,
  `REVIEW.md`, `STATUS.json`.
- `private/` holds everything about the person and is never pushed: goal, route, levels, every practice answer,
  weak spots, the machine check, the resume note.

Nothing about the learner lives only in a conversation, so a session can end at any moment.

## Who does what

| Job | Model | Script |
|---|---|---|
| Plan a book | writes the contents page | checks it, estimates hours and cost, finds the next chapter |
| Write a chapter | writes it whole, marks what it doubts | runs every program and pastes real output, draws figures, builds trace tables, checks the shape |
| Review a chapter | settles each doubt the cheapest sure way; reads the chapter once | makes the list of doubts, dangerous commands, unrun blocks and broken references; refuses "reviewed" while doubts remain |
| Teach | explains, asks, judges an answer | finds the section, records the answer, schedules the repeat |
| Practise and revise | nothing | asks the questions, hides the answers, keeps the boxes and dates |
| Come back after a month | nothing | writes the resume note from the files |
| Read the book | nothing | the reading page, the indexes, search |

## The curriculum (third design, 19 November)

A bank of teaching steps that were researched and checked once, so that the order of a subject, its real practice
problems, the wrong beliefs people hold and the words to own are not invented afresh for every learner.

- **A subject card** (`curriculum/cards/`) is 6 to 14 steps. Every wrong belief, failure and word is tagged with
  the step it belongs to, and each kind of subject has a part of its own: how a language runs, the state a tool
  keeps and the commands that destroy it, what a framework owns, the numbers and traces of a system, how a skill
  is judged. A card never supplies an example: the case is the learner's own.
- **Every step says how it lands**, in a block of step notes: `Need:` (the question the learner has just before
  it), `Show:` (the one run, trace or measurement that makes it undeniable, with the real output and whether it
  was run or comes from a named source), `Explain:` (the mechanism in a sentence the learner could say back),
  `Try:` (two typed tasks with a finish line) and, when needed, `Picture:`. Each card names its two to four deep
  steps, where a chapter spends its best pages. A word is owned at one step (taught and checked; five a step at
  most) or only met in passing, glossed once. Cards whose chapters invent cases with quantities carry believable
  numbers, each run or sourced. All 34 cards and the 6 maps were deepened by one helper and verified by a second,
  who reran every `Show:`.
- **A track map** (`curriculum/<domain>/`) orders the subjects of a route. Each common goal is a block: `Steps:`
  (what the goal cannot do without), `Open with:` (what chapter 1 does), `Deep:` (the steps that deserve a chapter
  each), `Order:` and, optionally, `Halfway:`. **A role map** (`curriculum/roles/`) lists what a job asks for,
  from dated adverts and public ladders.
- **The planner still plans.** `us_path.py goal DOMAIN/TRACK N` hands it one goal's block, a ready `track:` line
  and the outline of exactly that goal's steps (`find`, `map` and `spine` remain for goals no block fits). It
  writes one book at a time, within the learner's hours, and records in `PLAN.md` where every step went
  (`track:`, `budget:`, `held:`, `later:`, and a `from:` line under each chapter). A book is at most 16 chapters
  and carries the learner to the goal on its own; only a goal too large for that (a year of study) is a series,
  its later books' steps under `later: ... (book 2)`. The cards are a floor: the planner adds chapters from no card
  for what the learner's situation needs.
  `us_plan.py check` refuses a step left unaccounted for, a goal card left untaught, a plan over budget, and a
  plan with a `track:` line that is more than one book.
- **The writer gets only its chapter's notes** through `us_plan.py brief`, step by step in lesson order. The
  brief says the notes are a reference, not the chapter's outline: a chapter is one problem from the book's
  setting carried from first attempt to finished work, deepest at the deep step. `us_check.py` flags an owned word
  the chapter never uses, requires the practice section to hold a task tagged `unseen="..."` on something the
  chapter has not used, and notes a timing in prose that appears in no pasted output.
- **`us_path.py ready ROLE`** scores a role from the learner's books and practice records.
- The rules for writing and reviewing these files are `curriculum/FORMAT.md` and `curriculum/REVIEWING.md`
  (eighteen checks, among them rerunning every `Show:`). `python3 scripts/us_path.py check` enforces what a script
  can, including the limits (card 5,000 tokens, track map 1,800, role map 800, domain index 250) and a card
  without step notes, which is an error.

## The path of a chapter

1. `us-map`: contents page, book sheet, facts card (one lookup per book), approved by the learner.
2. `us-writer`: reads the writer's guide, the sheet, the guide for the book's kind and one sample; writes the chapter
   one section per edit; `us_run.py` pastes real output; `us_check.py` gates it.
3. `us-reviewer`: `us_check.py BOOK N --risks`, then one read, then a line of eight scores.
4. The learner reads, practises offline, and reports what is wrong; a report is repaired in place.

## Measured cost (Opus agents, 18 November)

| Step | Tokens | Time |
|---|---|---|
| First hello, a planned 6-chapter book, a first chapter of 7,800 to 13,400 words, its review | 139,542 to 188,742 | 8 to 13 minutes |
| The review alone, on an existing chapter | 98,270 to 139,237 | 2 to 5 minutes |
| An independent reader scoring a chapter | about 83,000 | under a minute |
| Planning a 17-chapter book (older measurement) | 83,187 | |

These agents each carried 60,000 to 80,000 tokens of fixed overhead from the build environment, so a learner's own
Claude Code may spend less. No tutoring session and no Pro-plan session has been measured.

## With no subscription

Reading (the page or plain Markdown), searching, practising with spaced repeats, seeing weak spots, and the resume
note all work with Python alone. Writing chapters, tutoring and level checks need the model.
