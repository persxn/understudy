---
name: us-review
description: Flaw-finder and repairer for the learner's book. Use when the learner asks to review, audit, proofread or check chapters, reports a mistake in the book or a place where it lost them, or when a chapter has just been written. Not for writing new chapters (us-write).
---

# us-review

One pass per chapter, straight after it is written, by a fresh reader that did not write it: the risk list is settled, then the chapter is read once. It costs under a third of the writing. Never a second pass: after it, the learner is the reviewer.

## The pass

Run it as the `us-reviewer` agent, one chapter per run. `references/README.md` lists the references; read each only at its step.

1. `python3 scripts/us_check.py <book> N` must show no ERROR. If it does, fix those first.
2. `python3 scripts/us_check.py <book> N --risks` is the whole reading list: marked risks with the passage each follows, destructive commands, dangling references, `unrun` blocks.
3. For each item, decide by the cheapest sure way: what `book/<book>/PRACTICES.md` already states is settled (never looked up again); what can run is run (`python3 scripts/us_run.py <chapter file> --only ID`); otherwise one look at the official source. Fix the text, or make it say what is uncertain, then delete the `<!-- risk: ... -->` note. Read `references/risk-review.md` first: the order of settling, each kind of item, when to stop. Unsure what counts as checked for this book's `Kind:`? Read that kind's part of `references/verify-by-kind.md`. A destructive command must be what the reader means to run, with its effect said beside it. An `unrun` block is judged by what the tool really does on a normal machine.
4. Read the chapter file once, top to bottom, hunting only for the five things in `references/one-read.md` (the case disagreeing with itself, something used before the reader has it, what the page shows wrongly, too many new words at once, repeats). Fix each with a small edit. Never restyle, never read it twice.
5. Never edit a pasted output. To change a program, edit it and run `us_run.py <chapter file> --only ID`.
6. `python3 scripts/us_check.py <book> N` again, with no ERROR. Add the lines of `assets/REVIEW.template.md` to `book/<book>/REVIEW.md`: risks checked and how, what was fixed, what was left open and why, and the one-line score from `references/rubric.md` (scored from that one read; a line under 8 gets its one repair of one section, as that file says). Then `python3 scripts/us_plan.py mark <book> N reviewed` (it refuses while risk notes remain), `python3 scripts/us_index.py <book>`, commit inside `book/`, and `python3 scripts/us_resume.py --next "..."`.

## When the reader reports something

"This is wrong", "this answer does not work", "I got lost at §8.3". Read `references/reader-reports.md`. Find the passage with `python3 scripts/us_find.py`, read that section only, repair that passage only, rerun its programs if one changed, and add a line to `REVIEW.md`. If the repair changes a definition, look the term up and check the sections that reuse it. Confirm the fix in a line, then carry on with what they were doing.

## Several chapters

Take the chapters marked `written` in `python3 scripts/us_plan.py status <book>`, in book order, one `us-reviewer` run each. Say how many are waiting, then start.
