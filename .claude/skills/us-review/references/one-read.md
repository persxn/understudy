# The one read: what the risk list cannot see

Read at step 4 of the pass, after the risk list is settled. The writer marks doubtful facts; a script finds dangerous commands and broken references. Neither can see a chapter disagreeing with itself. So read the chapter file once, from top to bottom (this is the one place a whole chapter is read), as the reader on `BOOK.md` would, and hunt for five things only. Fix each where it stands with the smallest edit that makes it true. Do not restyle, reorder or rewrite; do not read it a second time.

**1. The case or running program disagrees with itself.** Names, times, amounts, counts, what was on the screen, what a file is called.

> §1.1: "the session took fifteen minutes". §1.5: the timeline ends at 7:00. Fix: one of them, wherever the smaller change is.
> §1.4 promises the participant "I won't use your name"; the notes in §1.6 are headed "Ravi (support desk)". Fix: the notes say P1.

**2. Something is used before the reader has it.** A term before its explanation; a file the reader was never told to save ("change `day_total_labels.py`" when only `day_total.py` was saved); a line number, button or screen no example shows; a promise of a later chapter that the plan does not keep (check the plan line before leaving the promise in).

**3. The reader would not see what the page shows.** A figure described as "left to right" that is drawn top to bottom; an output or message that cannot be what the command prints; an answer that quotes a number no example produced; prose that restates a run's numbers differently from the pasted output; a claim about a case nobody ran ("without this line it would..."): run it (`python3 scripts/us_run.py try <book> N` takes a block on stdin) or make the sentence say only what the shown run proves. If a program is at fault, edit it and run `python3 scripts/us_run.py <chapter file> --only ID`; never edit a pasted output by hand.

**4. Too many new words at once.** More than about three new terms before the reader has used the first, or a term the chapter never needs. Move a term to where it is first needed, or cut it.

**5. It says it twice, or wanders.** A recap of the recap; a second picture for an idea that already has one; a side fact the book's promise does not need. Cut it; the chapter gets better and shorter.

Keep a tally as you go (case, order, page, words, repeats) for the `REVIEW.md` line. What is wrong but too big for a small edit (a missing explanation, a section in the wrong place) is not fixed here: it is the one repair the rubric allows, or it is written as open.

**Not this read's job:** style, word choice, a better example, anything that was merely not how you would have written it. The writer's voice stays.
