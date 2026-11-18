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
2. **Run it.** A program or session can answer for itself: `python3 scripts/us_run.py <chapter file> --only ID`. A quoted message, a default, an exit code: the run is the proof.
3. **One look at the official source.** The maker's documentation for the book's version, the man page, the standard: one page. If the fact will matter again, add it to "Facts that change" with source and date, so the next chapter's review settles it at step 1.
   What you know for certain without looking settles a routine item at once; a number, a limit, a default or a rule you could not swear to gets the look.
4. **Reword as uncertain.** If one look does not settle it, do not open a second tab. Make the text say what varies and how the reader can see it for themselves.

Then delete the `<!-- risk: ... -->` note.

The other kinds of item:

- **A destructive line** stays listed for good; judge it once. It must be what the reader means to run, on something the book made, with what it destroys said beside it. If it could touch more than that, make it `mode=fragment` or narrow it.
- **A dangling reference**: point it at the section that really teaches the idea (`python3 scripts/us_find.py WORDS`), or replace it with one plain sentence.
- **An `unrun` block**: judge the shown output by what the tool does on a normal machine. Wrong output is worse than none; when unsure, cut it to the lines you are sure of.

## Example

Item: `l.212 risk: default changed in 2.0` after "By default, `pip install` puts packages in your user folder."

Weak: open five documentation pages, re-read the section around line 212, rewrite it for flow. Twenty minutes, two voices.

Better: PRACTICES.md is silent; one look at pip's guide for the book's version settles it; fix the sentence, add the fact to PRACTICES.md with URL and date, delete the note. Two minutes.

## When to stop

Stop when `--risks` shows no marked risk and no dangling reference, and each destructive line and `unrun` block has been judged once. Then make the one read (the SKILL.md pass, step 4; `one-read.md`) and finish.
