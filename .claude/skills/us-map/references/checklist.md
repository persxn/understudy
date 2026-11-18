# Before showing the plan

Run through this once, after `us_plan.py check` passes and before the learner sees the destination. Each line is a thing planners forget; fix the plan rather than explaining it away.

**Coverage**
- Every core idea from the sources in `syllabus.md` has a `teaches:` line somewhere, or is in a book this plan `needs:`.
- The ideas the promise needs silently are there (configuration, reading errors, undo, testing, deployment, ethics: whichever apply).
- What was cut is listed as left out on purpose at the bottom of `private/route.md` (never in `PLAN.md`: the check rejects lines it does not know), so the learner can ask for it.

**Order**
- Read the chapter titles alone, top to bottom: each is something the reader can do, and each makes sense after the one before.
- Every `needs:` points to an earlier chapter or another book, never a later one.
- Chapter 1 gives a real result by its second or third section.
- Internals come after use; the hardest idea of the book is met simply before it is met fully.

**Size**
- Chapters have 5 to 9 sections; a chapter outside 4 to 12 is split or merged.
- One-command or one-term sections are `short`.
- `us_plan.py cost` fits the reader's hours and usage, or the route says what was left off (`sizing.md`).

**Practice**
- Every chapter ends in a `practice` section that climbs to a small project or case.
- The running project or case appears in the practice of every chapter that can hold it.
- Each chapter has a "when it goes wrong" section or the errors sit beside their ideas.

**Files**
- `PLAN.md` header has `for:`, `run:` (`none` when nothing runs) and `kind:`.
- `BOOK.md` is written from `assets/BOOK.template.md`, under 350 words, with the same running project the plan uses.
- `PRACTICES.md` has its three parts, each fact with source and date (`facts.md`).
- `us_index.py` and `us_doctor.py` have run; no `- blocked:` line is left unspoken.
