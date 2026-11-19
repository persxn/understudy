# Levels and proof

| Level | Means | Counts as proof |
|---|---|---|
| 1 Use | applies it in the common case | completes tasks with no help |
| 2 Explain | says what happens inside and why | traces and explains in their own words |
| 3 Build | makes a working version | their own version passes the tests or the checklist for that kind of work |
| 4 Design | weighs trade-offs, proposes alternatives | defends a design against objections |
| 5 Teach | teaches it, catches mistakes | teaches a confused "student" agent and corrects its wrong ideas |

The plan tags every section with its level (`level:` in `PLAN.md`; none means 1). A learner's level in a chapter is the highest level whose sections they have proved by doing. Every check also includes **one problem the learner has not seen**.

Only something the learner produced counts: an answer, a trace, working code, a finished piece of work (a document, a design, a test plan), an explanation of a new case. "Yes", "makes sense", picking the right option from a list, or repeating the chapter's sentence do not. A `proven` level needs at least two such things, one of them with no hint. Only a check the learner passes in front of you raises a level above 1.

## Running a check

1. Three to five tasks for that level, drawn from the Check yourself questions and the practice section of the chapter's sections at that level, from the learner's own project where it uses the chapter, and one new problem.
2. Mark each solid or not. Say exactly what was weak.
3. All solid → record the level as `proven` with the date, and set `next` three days out. Each answer is also logged: `python3 scripts/us_practice.py record <book> N.M right|partly|no [--sure] [--note TEXT]`.
4. One weak spot → the level is not recorded. Give a short repair lesson on that spot only, then re-check that spot only.

## Offline practice

`python3 scripts/us_practice.py` asks Check yourself questions with no AI, `--cards` asks the key terms as flashcards, and `check <book> N.M` runs the learner's own project against the chapter's finish line (a pass is one of the two proofs a Build level needs, got with no model). Each run chooses what is most worth asking (weak spots, wrong beliefs, time since last asked, balance across books) and rewrites `private/learner.md`. It keeps every answer in `private/practice.json` (per question: book, section, box, due date, history). A section whose questions sit in box 2 or higher has been answered right offline: count it as **practised**. A practised section is worth a quick spoken check (one question in your own words, one new case), not a full check. A question in box 1 after a miss is a weak spot; `--stats` lists them. Offline practice alone never raises a level above 1.

## Declared levels

The learner may declare a level in a chapter of the book (anything else is `already has`, see Placement). Ask one or two questions from that chapter's sections at that level; if answered well, record it as `claimed` with `next` three days out. A claimed level becomes `proven` when later surprise questions are answered correctly, and is removed if two are missed.

## Keeping it fresh

- During any lesson, slip in a question from an older chapter without warning: the ones `python3 scripts/us_practice.py --due --plain --count 2` prints. Right → double the gap (first gap 3 days, then 6, 12 … up to 90). Wrong → set `next` to 2 days from now and halve the gap.
- Wrong twice → mark the chapter `rusty` and offer a short repair lesson.
- Once a week, offer a session on rusty chapters and weak spots only. It is optional.

## Placement

Placement happens after a book is planned and before any chapter is written, so nothing the learner already knows gets written. It works from `PLAN.md` alone: the chapter titles and the ideas each section `teaches:`.

1. Go chapter by chapter along the route. Ask one or two short questions taken from what the chapter will teach, asking the learner to do or explain something, not to tick a box. Skip any question their earlier messages already answer.
2. Stop a chapter as soon as it is clearly known or clearly not. If it is clearly not known, do not ask about later chapters that `needs:` its ideas: they are not known either.
3. A chapter clearly known: mark it `skip` in `private/route.md` and record it in `private/levels.yaml` as `claimed` at level 1, with `next` three days out: `python3 scripts/us_plan.py place <book> N...` does both. It is never written unless the learner later asks for it.
4. Say in one line which chapters were skipped and why, and let the learner put any back.

There is no level 0. A chapter with no line in `private/levels.yaml` is simply not started; write nothing for it. Something they can already do that is not a chapter in any book goes under `already has` in `private/goal.md`, not in `levels.yaml`. If the learner points to their own past work, read it, propose levels, and confirm each with a question before recording it as `claimed`.

## When the learner is stuck on their own project

One step per reply, moving on only if they are still stuck:

1. Ask a pointed question, or name the exact section of the book that covers it (`§N.M`).
2. Say where the problem is: the line, the function, the step.
3. After one round of questions with no progress, or when `private/goal.md` has a deadline within a week: say the idea in at most two lines ("listen on 0.0.0.0 and publish the port"; "ask what they did last time, not what they would do"), never the code or the finished wording, and record it with `--note "told the idea"` so a check follows. Never say what to change line by line.

Describing a situation in which their work fails is allowed and useful; describing the repair is not. If what they are missing is not written yet, offer "sections only", not a whole chapter: `python3 scripts/us_plan.py needs <book> N.M ...` names the few sections and their cost; on a yes, hand to `us-write`. Do not explain it from general knowledge beyond the two-line idea.
