# The writer's guide: how learning material is written

This is the whole method, for any subject: a language, a tool, a framework, how a system works, or a professional skill. Read it once, then the book's sheet (`BOOK.md`) and the guide for its kind of subject and one sample (both under `.claude/skills/us-write/references/`). Then write.

## The reader and the voice

One capable beginner, addressed as "you", in plain English, like a story told by someone who has done the work. Never talk down, never show off. One writer writes a book's chapters one after another and keeps the book in mind: the same running project or case, the same pictures, the same names for things. `BOOK.md` holds them; keep to it. Fix the facts of a case before you tell it (who, what was on the screen, times, amounts) and never let them drift: a reader notices when the session that took fifteen minutes ends at 7:00.

## What every section does

Six moves. They are jobs to do, not headings to fill; name your headings after the content.

1. **Need.** Open with a question or a problem the reader already has, or one the last section left open.
2. **Intuition.** A picture from everyday life, and where the picture stops being true. Reuse the book's pictures (`BOOK.md`); a new one only for an idea that is hard to see without it, never one per section.
3. **Mechanism.** How it really works and why it exists: what problem it solved, what happens step by step, what it is built from. This is where the depth lives; take the room it needs and no more.
4. **The real thing.** A worked example the reader does with you, then a walk through what just happened, step by step.
5. **When it goes wrong.** The usual mistakes with their real symptoms, and how to get out.
6. **Keep it.** A short recap, then `**Check yourself**`: questions that make the reader do something (predict, fix a fault, change it, decide), each answer hidden in `<details>`.

A move that would only repeat another is merged or dropped. A section about one small thing (one command, one term) is short: need, the real thing, one mistake, a question.

## The shape follows the subject

| Kind of subject | "The real thing" is | Practice is | The mechanism to show |
|---|---|---|---|
| A language | a program the reader types and runs | change it, break it, write one | what the machine does with each line |
| A tool or service | a terminal session on a small real job | find and fix a broken set-up | what the tool keeps where, and what each command changes |
| A framework or library | a small project that grows chapter by chapter | add a feature, read an error | who calls your code, when, and what the framework does for you |
| How a system works (operating systems, networks, databases, architecture) | a trace by hand, a small experiment, a diagram built up in steps | predict what happens, then reason it out | the parts, what each one knows, the order things happen in |
| A professional skill (writing, design, testing, managing work, interviewing) | a worked case: a weak version, then a better one, with the reasons | do it on the reader's own material, then judge it against a checklist | why the practice exists: what goes wrong without it |

If a subject is of two kinds, each chapter takes the shape of what it teaches. Never force a program into a chapter that has no use for one, and never leave one out where it would show the idea.

## Order and size

Nothing is used before it is explained, inside a chapter as well as across chapters. If a later section owns an idea, give one plain sentence and its number; never point to a section the plan does not have. At most three new terms before the reader has used the first. The reader does something real early in every chapter.

A chapter is as long as its ideas need: usually 5 to 9 sections; a section usually 1,200 to 3,000 words (programs and answers count, pasted output does not), a short one 300 to 700. Thorough, never exhaustive: leave out what this reader will not need for the book's promise.

**Depth is shown, not told.** A lesson that comes out short has nearly always *told* the mechanism in a list of facts. Show it instead: walk one concrete case step by step, saying what each part holds before and after; change one thing and walk it again; make the usual mistake really happen and read its real message; say why it was built this way and what that costs. Stay with one idea until the reader could explain it to a friend, then move on. Never pad: no second recap, no list of extras. The check refuses a lesson under 900 words; if the idea truly is that small, it is a `short` section in the plan. Every chapter ends with practice that climbs: guided, then on your own, then a small project or a case that uses the whole chapter.

## Truth, and what to mark

Write what you know to be true of the current version, and say which version. Follow the habits and facts in the book's `PRACTICES.md`. Never invent a fact to fill a gap.

Do not stop to verify routine things. Put a hidden note `<!-- risk: why -->` right after any statement or example that is one of these, and only these: it differs between versions or systems; it deletes, overwrites or costs money; it is a number, limit, default or quoted message you are not sure of; it is a rule from a standard, a law or a vendor; it says what would happen in a case you did not run ("without the `fflush` the prompt would not appear"): run that case as a second program, or mark it; you are unsure. The review checks exactly those. Numbers and messages in your prose come from the pasted output of the run, word for word, never from memory of what such a run usually prints.

## Write first, check after

Write the whole chapter in one sitting, straight into its file, one section at a time (the first section starts the file; each next one is added with its own edit), every section at full depth, running nothing in between. Do not hurry and do not shorten a section to save time or usage: a thin chapter is the costly one, because it has to be written again. Put `<!-- code: id=NAME -->` above each program or terminal session. Then run `python3 scripts/us_run.py <chapter file>` once: it pastes real output wherever this machine can run the code. Where it cannot, mark the block `unrun="short reason"` and show the output you expect; the reading page labels it. The fence right after a program is its output: the script replaces it. Then `python3 scripts/us_check.py <book> N` and fix what it calls an ERROR. A blocked machine never stops a chapter from being written.
