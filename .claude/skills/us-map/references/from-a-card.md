# Planning with the curriculum

Read when `python3 scripts/us_path.py find <subject or job words>` printed a track, a card or a role. The curriculum is a bank of teaching steps that were researched and checked once. It does not plan the book: you do, for this learner's goal and in this learner's own setting. The scripts hand you only what you need: never open `curriculum/` yourself.

## The order of work

1. **The goal.** `python3 scripts/us_path.py map <domain>/<track>` (`index <domain>` lists the tracks), then `python3 scripts/us_path.py goal <domain>/<track> <n>` for the goal nearest the learner's. It prints a checked plan for that goal: the steps it cannot do without, how the book opens, which steps go deep, the order of study, a ready `track:` line, and the outline of exactly those steps (each card's promise, one idea, steps, deep steps, ladder, project, hours). No goal fits? `spine <card>[:steps] ...` prints the same outline for steps you choose.
2. **Take its shape, fit it to this learner.** "Open with" is chapter 1. Each "Deep" step gets a chapter of its own or most of one. "Order" is the order of the parts; whatever THIS learner named comes in the first half even if the goal's order says later. Their hours decide how much beyond the goal's steps the book takes.
3. **What they already have.** A step goes under `held:` only on evidence, said in the brackets. When the plan is drawn, before placement (`rules/levels.md`), the only evidence is what they do at work or have built, every week. Placement may add to it later: move the steps to `held:` and run the check again. Their own guess ("my C++ is fine") is not evidence: teach the step, briefly if it proves easy.
4. **Plan as you always do** (`syllabus.md`, the plan pattern for the kind, `sizing.md`), with these rules:
   - **The book is the goal, not one card.** "One subject is one book" yields here: a goal usually draws on several cards, and the book carries the learner to the goal on its own, by their deadline. Work out their hours first (hours a week times the weeks to their deadline) and write them in the header: `budget: 150 hours`. A book has at most 16 chapters. To fit: take every card the goal needs and from each the steps the goal cannot do without (the goal's "Steps"); inside a step, plan sections only for what this goal uses (a contest trick has no place in an interview book); put rarer and deeper steps under `later:` with the reason. Only when the goal still cannot fit (a year of study, sixty steps or more) is it a series: book 1 is then a first complete version of the goal (the nearest smaller goal on the map is usually exactly that), never the first cards in full, and the rest is `later: ... (book 2)`; `private/route.md` names each later book, its hours and what it adds. `us_plan.py check` refuses more than 16 chapters, a plan over budget, and a card of the goal neither taught nor later.
   - **The cards are a floor, not a fence.** Read the finished plan as this learner's senior colleague: what will they meet in the first month of the goal that no chapter teaches? Add chapters for it, with no `from:` line (the goal's "Order" may name some; their codebase and deadline name others).
   - **The kind's plan pattern still shapes the book** (`plan-patterns/<kind>.md`). For a skill, chapter 1 does the whole practice once, small, in the learner's setting, taking a step from several cards if it must; for a tool, chapter 1 gets something real working. A card's order then rules the order of its own steps.
   - Group steps into chapters: two or three steps usually make one chapter of five to nine sections; a deep step fills a chapter alone, or with one step that serves it, with `level: 2` or higher (`us_plan.py check` notes a deep step crowded by three others). A chapter is one problem or case carried from first attempt to finished work, not a tour of its steps. Every chapter ends in practice on something the chapter has not used: a new problem, case or material the reader works alone. A step the learner half has (they use it every week, the goal leans on one part of it) gets a section in the chapter that first needs it, not a chapter. A chapter of three sections means two steps should share it. One step is never split across distant chapters.
   - Keep each card's step order unless this learner's goal gives a reason. A card that needs another comes after it, unless the learner holds what it needs or the needed steps are woven in where they are first used. The plan's chapter order is the order of study: start where the learner starts. Whatever the learner named (the words they cannot yet use, the failure they keep meeting) comes in the first half of their time, each as soon as what it needs has been taught; a card's remaining steps can follow.
   - **The case is set in the learner's own world**: their stack, their scale, their tools, their judge, with invented names and data (nothing personal goes into `book/`). The card's "In production" says what must happen in it. Never take an example from a card, and never invent a toy where the learner has the real thing.
   - "The one idea" goes to `BOOK.md` "Pictures" with where it breaks. The ladder's four tasks are the checks for levels 1 to 4. The card's project, moved to the learner's material, is the book's final project.
5. **Say where every step went**, in `PLAN.md`:

```text
track: core-cs/competitive-programming 1-4
budget: 150 hours
held: cpp-for-contests 1-3 (writes and runs C++ like this every week at work)
later: graphs-and-trees 9-12 (after the first rated contests)
later: advanced-data-structures (book 2)

### 4 Sorting as a tool
from: dsa-core-techniques 3; cpp-for-contests 5
4.1 Sort, then scan | teaches: sort-then-scan
```

   `python3 scripts/us_plan.py check <book>` refuses a plan that leaves a step of a card it touches, or of a card those cards need, neither taught, held nor later. A step you would drop is `later:` with its reason in `private/route.md`: never silently gone.
6. **Do not copy the notes.** Wrong beliefs, failures, words and the kind's own part reach each chapter's writer through `us_plan.py brief`, for that chapter's steps only. Facts with versions are still looked up once for `PRACTICES.md` (`facts.md`): a card names what to look up, never the values.

## A role: a job

`python3 scripts/us_path.py role <role> --have "git:3, python:2"` prints what is left for this learner: essential lines first, desirable when time allows, specialist only if asked. Each line's level is the level to reach and "Proved by" is the real test. Record the role in `private/goal.md`. Later, `python3 scripts/us_path.py ready <role>` scores it from their books and practice records.

## Weak and better

Weak: the outline has twelve steps, so the plan has twelve chapters with the steps' names, and its example is a made-up shop.

Better: the learner runs an Express service with PostgreSQL and wants to hold their own in design reviews, where they hear "read replica" and "backpressure". One book: it opens on a service like theirs under load, takes the foundations steps in its first part, holds the SQL steps they use every week, has a part on caches and queues and a part on replicas because the goal names them, and leaves sharding `later:` with the reason.
