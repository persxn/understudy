---
name: us-start
description: Entry point and guide. Use first in any session where the learner greets, starts or resumes, states or changes what they want to learn or become, asks about their progress, asks what to learn next, plans their week, or when book/ or private/ is missing. Not for studying a topic (us-teach) or ordering a subject's topics (us-map).
---

# us-start

## First run (no `book/` or `private/`)

1. Run `python3 scripts/us_init.py`. It creates `book/` as its own git repository, `private/now.md` and `private/machine.md`. Do not create these by hand. Other private files are created by the step that first needs them.
2. Read `references/first-session.md` first. Find out what brings them here, unless their message says: **a goal** ("become a backend engineer", "run usability tests for my team"), **a subject** ("teach me Docker": ask in one line what it is for), or **a piece of software** to understand and rebuild (after the goal is recorded, hand to `us-build`).
3. Sharpen the goal into one sentence that starts "I can …" and say it back once. In that same message ask only what their words have not made clear: a deadline and hours a week (accept "none"); for a software-engineering goal, whether the aim is the whole profession or this one thing; and, once, their machine and its limits.
4. Only "become an engineer" switches on the engineer standard (`rules/engineer-standard.md`). Never add it to a small goal or another field.
5. Write `private/goal.md` (template: `rules/private-files.md`); what they say they can already do goes under `already has` in their words; do not ask for it. The progress card stays off until they ask. Write the machine answers under "Told by the learner" in `private/machine.md`, then run `python3 scripts/us_doctor.py`; tell them any `- blocked:` line it prints.
6. Hand to `us-map`. It maps what the goal needs, places the learner on that map, builds the route and gets their approval of the destination. Nothing more for this skill to do in the first run.

## Returning

Everything they did offline is in local files, so a month away loses nothing. After a break, read `references/coming-back.md` (index of references: `references/README.md`).

1. Run `python3 scripts/us_resume.py`, then read `private/RESUME.md`. Run `python3 scripts/us_practice.py --stats`: weak spots, and each section practised offline with its box (2 or higher: answered right offline).
2. Say in two lines where they are and what is next.
3. List their weak spots first, then the sections practised offline: each is worth a quick spoken check, not a full test (`rules/levels.md`, "Offline practice"). Then wait.

## Progress page

Read `private/levels.yaml` (and `private/standard.md` if the standard applies). Show one line per chapter on the route: title, level, state (`proven`, `claimed`, `rusty`, `skip`), next revision date. Add sections practised offline from `python3 scripts/us_practice.py --stats`. Then the goal's percentage and, if it applies, the standard's counts. Nothing else.

## What next

From `private/route.md` and `private/levels.yaml`, offer two or three steps. For each: time, and one of **needed** (something later depends on it), **can run alongside** (different kind of work, shares nothing), or **not yet** (say what it waits for). End with what was left off the route on purpose. Works offline. Check the job market only if asked, and say it needs the internet.

## Weekly plan

If the engineer standard applies, ask how much of this week goes to algorithm practice. Then write `private/week.md`. If a deadline exists, say honestly which level is reachable by then.

## Before a subscription ends

When the learner says their subscription is ending, offer once to stock up: write the next chapters on the route now (`us-write`, "Many chapters"), so they can read and practise them offline. Tell them how: the reading page, `python3 scripts/us_reader.py --serve`, and practice, `python3 scripts/us_practice.py`.

## Goal changes or falling behind

Hand to `us-map` to rebuild the route. Everything already proven is kept.

## Progress card

Only if `private/goal.md` has it switched on: write `book/progress-card.json` with levels reached, projects shipped, contest rating. Never anything from `weaknesses.md`, `interviews/` or `logs/`.
