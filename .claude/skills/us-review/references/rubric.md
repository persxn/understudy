# The rubric: scoring a chapter out of ten

This is the owner's rubric. Score after the risk list is settled and the one read is done, from what you saw there. Do not read the chapter again to score it.

| Line | 9 looks like | 6 looks like |
|---|---|---|
| Accuracy | every risk item settled by a run, PRACTICES.md or one source; versions named | claims that sound right but were never marked or checked; a version left vague |
| Depth | each section shows the mechanism: why it exists, what happens step by step | names and steps without the why; the reader can repeat it but not reason about it |
| Clarity | each opening states a need the reader has; terms used once they are explained | openings that announce the topic ("In this section we will"); a term used before it is explained |
| Sequencing | nothing used before it is taught; each section starts where the last left off | a forward reference with no plain sentence; a section that needs a later one |
| Practical relevance | the real thing is the subject's own (a run, a session, a trace, a worked case) and serves the book's promise | toy examples unrelated to the running project; material this reader will not use |
| Exercises | questions make the reader predict, fix, change or decide; practice climbs to a small project or case | recall questions whose answer is a sentence copied from the text; practice that stays at one level |
| Completeness | every planned idea taught; the usual mistakes shown with real symptoms | a planned idea mentioned but not taught; no "when it goes wrong" where it was needed |
| Efficiency | sizes in the guide's ranges; small ideas are short sections; nothing said twice | padding, a recap of the recap, a long section for one command |

## The line in REVIEW.md

One line, the eight numbers in this order, then the lowest line's reason in a few words:

```text
Score 8: accuracy 9, depth 8, clarity 8, sequencing 9, practical 8, exercises 7, completeness 9, efficiency 8. Lowest: 9.6 practice stays guided.
```

The overall score is the mean, rounded to the nearest whole number; a mean ending in .5 rounds down.

## One repair, when a line is under 8

The lowest line under 8 names its weakest section. Repair that ONE section now, once: read it in full (again, this section only), add the move it lacks as `.claude/skills/us-write/references/depth.md` shows (for efficiency, cut what repeats instead), run `us_run.py <chapter file>` if a program changed and `us_check.py <book> N` again, then score that line again. Anything else under 8 is written as open with its section number. It is never a reason to rewrite the chapter, and never a second repair.
