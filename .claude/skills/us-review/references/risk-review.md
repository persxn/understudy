# The review by risk, step by step

The writer marked what might be wrong; the script found what is dangerous or broken. Settle that list first, without reading the chapter; the one read comes after (`one-read.md`).

## 1. Get the list

```text
python3 scripts/us_check.py <book> N            no ERROR first; fix those before anything else
python3 scripts/us_check.py <book> N --risks    the reading list, with line numbers and passages
```

Open the chapter file only at an item's line, and only when the printed passage is not enough.

## 2. Settle each item by the cheapest sure way

Stop at the first that settles it.

1. **PRACTICES.md states it.** Read `book/<book>/PRACTICES.md` once at the start. If "Facts that change" or "Handle with care" already says it, the text agrees or is made to agree. Never look it up again: the book chose that source once.
2. **Run it.** A program or session can answer for itself: `python3 scripts/us_run.py <chapter file> --only ID`. `--only` runs that block alone: a session that leans on what earlier sessions made is rerun with the whole chapter (`us_run.py <chapter file>`; unchanged blocks come from the cache). A quoted message, a default, an exit code: the run is the proof.
3. **One look at the official source.** The maker's documentation for the book's version, the man page, the standard: one page. If the fact will matter again, add it to "Facts that change" with source and date, so the next chapter's review settles it at step 1.
   What you know for certain without looking settles a routine item at once; a number, a limit, a default or a rule you could not swear to gets the look.
4. **Reword as uncertain.** If one look does not settle it, do not open a second tab. Make the text say what varies and how the reader can see it for themselves.

Then turn the `<!-- risk: ... -->` note into a lasting mark, in the same place:

```text
<!-- checked: how=source date=2026-11-18 ref="docs.python.org/3/library/csv.html" -->
```

`how` is the step that settled it: `practices`, `run` (ref: the program's id), `source` (ref: the page; required), `known`, or `reworded`. Do not write the `h=` part: `us_plan.py mark ... reviewed` stamps it, and from then on the check says when someone changes a checked passage. The marks are the book's record of what was verified and how: `python3 scripts/us_check.py <book> --facts` lists them, and the reader sees them in the book's `FACTS.md`.

The other kinds of item:

- **A destructive line** stays listed for good; judge it once. It must be what the reader means to run, on something the book made, with what it destroys said beside it. If it could touch more than that, make it `mode=fragment` or narrow it.
- **A known mistake** (`FLAG ... known mistake`): the script matched a statement that has been wrong before, and prints the truth with its source. Make the text agree; if the text is right and the match is a false alarm, put a checked mark under it and the flag goes.
- **A dangling reference**: point it at the section that really teaches the idea (`python3 scripts/us_find.py WORDS`), or replace it with one plain sentence.
- **An `unrun` block**: judge the shown output by what the tool does on a normal machine. Wrong output is worse than none; when unsure, cut it to the lines you are sure of.

## Example

Item: `l.212 risk: default changed in 2.0` after "By default, `pip install` puts packages in your user folder."

Weak: open five documentation pages, re-read the section around line 212, rewrite it for flow. Twenty minutes, two voices.

Better: PRACTICES.md is silent; one look at pip's guide for the book's version settles it; fix the sentence, add the fact to PRACTICES.md with URL and date, turn the note into `<!-- checked: how=source date=... ref="pip.pypa.io/en/stable/user_guide" -->`. Two minutes.

## When to stop

Stop when `--risks` shows no marked risk and no dangling reference, and each destructive line and `unrun` block has been judged once. Then make the one read (the SKILL.md pass, step 4; `one-read.md`) and finish.
