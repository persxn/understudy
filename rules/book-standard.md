# Book standard: the format

The format of a book, which the scripts read. How to write it (voice, shape, depth, what to mark) is only in `rules/writers-guide.md`.

One subject is one book: parts, chapters and numbered sections, in the order they are taught. Nothing is used before the section that teaches it.

## Files

```text
book/<book>/PLAN.md               the contents page, approved by the learner before writing
book/<book>/BOOK.md               the book's sheet, at most 350 words (below)
book/<book>/PRACTICES.md          habits, facts that change, handle with care (below)
book/<book>/chapters/NN-name.md   one file per chapter
book/<book>/chapters/fig/NN-name/<id>.svg   figures, made by scripts/us_draw.py
book/<book>/STATUS.json           what is written and reviewed, kept by scripts
book/<book>/FACTS.md              every checked fact and how it was checked; made by scripts/us_index.py
book/<book>/MISTAKES.md           false statements a reader reported, watched for in later chapters (optional)
```

**BOOK.md**, written by the planner, kept by the writer: lines `Reader:`, `Promise:`, `Kind:`, `Running project or case:`, `Pictures:`, `Names:`, `Versions:`, then one line per written chapter, `Left at end of chapter N: ...` (files, state, where the project stands; 60 words at most; the writer of a chapter is shown the last two).

**PRACTICES.md**, three parts: habits (each with the chapter it applies from); `## Facts that change` (version-sensitive facts looked up once, each with its source and date); `## Handle with care` (commands or advice that can delete, overwrite, cost money or break a rule).

## PLAN.md

```text
# Usability testing for product teams
for: a designer who has never run a test
run: none
kind: skill

### 2 Writing the tasks
2.1 What a task is for | teaches: test-task
2.3 Leading words | short | teaches: leading-word
2.6 Practice: rewrite five tasks | practice | level: 3
```

- One line per section: `N.M Title | fields`. Fields: `teaches:` idea ids (short, lower-case, hyphenated, unique in the book); `needs:` ideas from **other chapters** this section leans on (inside a chapter, order is the dependency); `level:` 1 Use, 2 Explain, 3 Build, 4 Design, 5 Teach (default 1); a kind, `story`, `practice` or `short` (default: a lesson); `fig` when the section must contain a drawn figure. A story or practice that only applies earlier ideas needs no `teaches:`.
- A chapter usually has 5 to 9 sections (the check warns outside 4 to 12), and ends in practice.
- Header lines above the first chapter: `run:` (`none` when there is nothing to run; `console` for a terminal tool; else the language, `c`, `python`); `kind:` one of `language`, `tool`, `framework`, `system`, `skill`; a tool book may add `state: docker`, `timeout: N`, `check: COMMAND`, `mask: REGEX`, `env: NAME=VALUE ...` (`rules/tool-books.md`).
- `python3 scripts/us_plan.py check <book>` must pass before any chapter is written.

## Sections

`## N.M Title`, then headings named after the content (no fixed headings).

- **lesson** (default) and **short**: each must contain a line `**Check yourself**` followed by at least one question whose answer is hidden:

```text
<details>
<summary>Answer</summary>

The answer.

</details>
```

- **story**: history that makes the reader care; free form, at most 500 words, at most one per chapter.
- **practice**: closes a chapter; tasks rising to a small project or case, each with a hidden answer. An answer that is a program is a tagged, run program. At least one task's q tag carries `unseen="name"`: a problem, case or material that appears nowhere in the chapter before the practice heading (the check: an ERROR, a NOTE once the chapter is marked written or reviewed).

Sizes: a lesson usually 1,200 to 3,000 words, a short section 300 to 700 (NOTE lines outside these). A lesson under 900 words or a short section under 200 is an ERROR: deepen it, or mark it `short` in the plan. A practice has at least three answered tasks, one of them a `build` task with a finish line the reader can test alone (`check=`, or a checklist in a `run: none` book). In a `run: console` or `run: none` book a `<!-- checklist: -->` of 3 to 10 yes/no tests is that finish line, since a session cannot carry `check=`.

## Markers

Hidden HTML comments. Scripts read them; the reader never sees them.

```text
<!-- teaches: test-task = task, test task -->     above the paragraph that first teaches an idea; after = the
                                                   technical terms it names
<!-- code: id=first-commit -->                    a program or terminal session: it is run, its output pasted below
<!-- code: id=star-trap mode=fragment -->         not run
<!-- fig: id=pointer-arrow                        a figure description (format: python3 scripts/us_draw.py --format);
kind: memory                                       the script draws it and writes the image line and alt text below
... -->
<!-- trace: id=boxes watch="x y" at="7 14" -->    a trace table made by us_run.py from a real run: a row each time an
                                                   `at` line finishes (rows=12, hits=all|first); `?` in a
                                                   cell means the name does not exist yet
<!-- risk: why -->                                right after a statement or block the review must check
<!-- checked: how=source date=2026-11-18 ref="..." -->   what the review turns a settled risk note into: how it was
                                                   checked (run, practices, source, known, reworded), when, and by what
<!-- q: idea=test-task type=fix wrong="names the button" -->   on the line above every Check yourself question
                                                   and practice task: the idea it tests, what it makes the reader do
                                                   (recall, explain, predict, fix, apply, decide, build), and, when
                                                   there is one, the wrong belief it catches; a
                                                   find-the-fault question is type=fix; on a practice
                                                   task, unseen="name" names the problem, case or
                                                   material the chapter has not used before it
<!-- checklist: id=first-test -->                  then a list of 3 to 10 yes/no tests the reader applies to their
                                                   own work, where nothing can be run
<!-- resolves: 1.13 -->                           where an earlier "Simplified here" is repaid
```

Code modes: `run` (default; builds with no warnings, exits 0), `compile` (must build; nothing pasted), `warns` (the warnings are pasted, then the output), `error` (must fail to build; the message is pasted), `crash` (killed by a signal: output so far, then a line such as `Segmentation fault`), `fragment` (not run).

Attributes: `stdin="3 4\n"` (input; `^C` and `^D` are key presses), `wait=N` (each stdin item typed N seconds after the last; for containers and `^C`), `unrun="why"` (could not run here; show the expected output; retried on every run; the review checks it), `args="in.txt"`, `after=ID` (reads a file program ID made), `file=util.h` (saved for later programs), `exit=N`, `timeout=N`, `varies` (output changes between runs), `stderr=hide`, `nosan` (a memory fault on purpose), `danger="why"` (a risky shell command), `answer` (the output goes in the hidden answer that follows), `check="COMMAND"` (on a model answer: the reader's own program, run by COMMAND with the same input, must print this output; `python3 scripts/us_practice.py check <book> N.M --in THEIR-FOLDER` tests it with no AI). In prose, `{L:text}` (or `{L:ID:text}`) becomes the number of the line holding that text.

## Terminal sessions

A book's `console` fences are one continuing story for a reader who types along, and the runner depends on these rules:

- The reader's home folder is shown as `/home/you` wherever a command prints it; say once that their own name stands there.
- The first chapter starts in an empty home folder; each later chapter starts with what the one before left there. Each session starts in the folder where the last ended, except a chapter's first, which starts in the home folder. Never `cd` into a folder the reader is already in; never make again what an earlier chapter made.
- `$ ` lines run in order on a terminal 80 columns wide (a here-document or a line ending in `\` continues). Every `$` line but the last must succeed; `exit=N` is for the last. The fence is rewritten with what they printed; never type output.
- `env:` in the plan fixes what changes between runs (for Git, `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE`).
- Use commands that behave the same on Linux, macOS and Git Bash: `printf` or a here-document, not `sed -i`.
- `state: docker`: its rules (names, ports, clean-up, typing into containers) are in `rules/tool-books.md`.
- `python3 scripts/us_run.py try <book> N` replays the chapter so far and tries what comes next.

## Style of the file

GitHub-flavoured Markdown. Every fence carries a language tag. No HTML except the markers and `<details>`. A figure caption starts `*Figure N.Ma:`. `> **Simplified here.** ...` names what was glossed over and the section that gives the fuller truth.

## Done

A chapter is **written** when `python3 scripts/us_check.py <book> N` prints no ERROR. It is **reviewed** after the one review (the risk list, then one read) (`us-review`) and `us_plan.py mark <book> N reviewed`. After that, the reader is the reviewer: what they report is repaired in place.
