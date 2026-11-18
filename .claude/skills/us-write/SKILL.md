---
name: us-write
description: Writes chapters of the learner's book. Use when the learner asks for a chapter, a book, notes or a written explanation to keep, wants several chapters or a whole book written, wants a section added or a chapter updated, wants a cheat sheet, a printable copy, or notes made from their own lectures or slides, or when a lesson needs a chapter that is not written yet. Not for explaining in conversation (us-teach).
---

# us-write

You write the teaching the way `rules/writers-guide.md` says: one writer, one voice, whole chapters, written first and checked after. Scripts paste real output, draw figures and check.

## What to write

1. `python3 scripts/us_plan.py next <book>` names the next chapter (no `PLAN.md`: hand to `us-map`).
2. `python3 scripts/us_doctor.py <book>`, unless it ran for this book earlier in this session or the book is `run: none`. A blocked line is told to the learner with its cure, and the chapter is still written: what cannot run here is shown as expected output and marked `unrun="why"`.
3. Say which chapter and how long (`us_plan.py cost <book> N`). Straight after planning, ask first ("chapter 1 now? about N minutes") unless the learner asked for it or the autopilot runs.

**Sections only.** When a project or a question needs a few sections, not a chapter: `python3 scripts/us_plan.py needs <book> N.M ...` lists them and what they lean on. Say the cost; on a yes write those the same way, each in its place in the chapter file.

## One writer per book

Start the `us-writer` agent with the book and the chapters to write; it writes them one after another, keeping the book in mind. Never write a chapter in the main conversation. With no agents, write here; the learner clears the conversation between books, not chapters.

## The writer's steps, per chapter

1. `python3 scripts/us_plan.py brief <book> N` (it prints `BOOK.md`); read it, `rules/writers-guide.md`, `book/<book>/PRACTICES.md`, the kind file `references/kinds/<kind>.md` for the book's `kind:`, and the ONE sample `references/samples/<kind>.md`, in full: it sets the depth. The plan's sections are the list of what to teach; keep their numbers and titles. Unsure of a section's shape: `references/sections/` (concept, mechanism, procedure, worked-case, short, practice). Other references, and when to read each: `references/README.md`.
2. Copy `assets/chapter-start.md` to `book/<book>/chapters/NN-name.md`. First chapter of a new book only: write section 1 in full, show the learner a few lines and ask whether the voice is right (not when they already said to go on, or the autopilot runs).
3. Write the rest, one section per edit, each at full depth, running nothing in between and never shortening to save time. Format: `rules/book-standard.md`, "Sections" and "Markers" (and "Terminal sessions" when the book has them); `python3 scripts/us_draw.py --format` once for a figure.
4. `python3 scripts/us_run.py <chapter file>` once: real output is pasted where this machine can run the code (`python3 scripts/us_draw.py --chapter <chapter file>` when it has figures). Fix what was wrong in your text; delete a risk note whose only doubt was an output the run has now pasted; mark what cannot run `unrun="why"` with the output you expect; this machine's faults never go into the prose.
5. `python3 scripts/us_check.py <book> N`: fix each ERROR; NOTE lines are advice. A lesson it calls too short is deepened with the move it lacks (`references/depth.md`), never padded. One pass, then stop. Then run through `references/checklist.md` once.
6. Add `Left at end of chapter N: ...` to `BOOK.md`. `python3 scripts/us_index.py <book>`, commit inside `book/` (one line), `python3 scripts/us_resume.py --next "..."`. Reply in two lines: sections, words, not run, risk notes left. Then the review (`us-review`).

A small fix later: `python3 scripts/us_section.py patch <book> N.M --old TEXT --new TEXT`.

## Many chapters

Loop without asking, in route order, leaving out chapters marked `skip` in `private/route.md`: `us-writer` → `us-reviewer` (see `us-review`) → the next. Stop at the chapters or time given, or the book's end. With no conversation at all: `python3 scripts/us_autopilot.py <book>`.

## Other jobs

A cheat sheet, a printable copy, or notes from the learner's lectures or slides: `rules/writing-modes.md`.
