# Writing modes

## Writing many at once

When asked for several chapters, or stocking up before a subscription ends: follow "Many chapters" in `us-write`, taking chapters in the order of `private/route.md` and leaving out those marked `skip`. To run with no conversation at all: `python3 scripts/us_autopilot.py <book> --chapters K` (or `--minutes M`); try `--dry-run` first. Stop at the number of chapters or the time you were given; never run past it. Finish with `python3 scripts/us_index.py`, `python3 scripts/us_check.py`, a commit in `book/`, and `python3 scripts/us_resume.py --next "..."`.

## From the learner's own lectures, slides or PDFs

Their course decides the order and the emphasis; the book still explains in its own words and runs what it shows.

1. `python3 scripts/us_ingest.py <file or folder> [name]` copies the text into `private/sources/<name>/`: `pages.md`, every page or slide under its own heading, and `index.md` (page, first line, word count, a mark on pages with almost no text, which may be pictures). Nothing there is pushed or copied into `book/`.
2. Read `index.md`, then only the pages a chapter needs. A marked page must be looked at, or listed as not read.
3. Map the course's parts onto chapters of a plan by title (hand to `us-map` if the subject has no `PLAN.md`) and write chapters as usual. Where the book follows the course, name the lecture and page. Where the course and a first-hand source disagree, say so in the text and follow the source.
4. Anything the course states that a run or a source cannot confirm is labelled as the course's claim, not the book's.

## Other formats, only when asked

- **Cheat sheet:** one page from a written chapter, saved as `book/<book>/cheatsheets/NN-name.md`.
- **Printable copy:** each chapter is already one Markdown file, `book/<book>/chapters/NN-name.md`: give its path. Never regenerate text to make one.
