# Sizing the plan and the route

Read after the contents page passes its check, before showing it, and whenever time or usage is short.

## What the numbers mean

`python3 scripts/us_plan.py cost <book>` prints, per chapter, sections, words, hours of study, minutes of writing and tokens of writing. It estimates each section by its kind:

| Kind | Words | Study (reading at 150 words a minute, plus doing) | Tokens to write |
|---|---|---|---|
| lesson | 1,500 | about 15 minutes | about 28,500 |
| short | 500 | about 8 minutes | about 9,500 |
| story | 400 | about 3 minutes | about 7,600 |
| practice | 1,200 | about 28 minutes | about 22,800 |

So a usual chapter of five lessons, one short and a practice is about 9,200 words, two hours of study and 175,000 tokens. Real study takes longer than reading: tell the reader to double the hours for the practice they do on their own project.

## Fit to the reader

Compare the total with two budgets: hours a week times weeks to the deadline (`private/goal.md`), and the usage plan the learner told you about (`private/machine.md`, under "Told by the learner"). Measured on this product: planning a book, writing one chapter and reviewing it took 100,000 to 250,000 tokens. Nobody has measured how many chapters a 20-dollar plan's session holds, so do not promise a number: on such a plan write one chapter, let the learner look at their usage meter, and set the pace from that; say this when you show the cost. When the plan is too big, cut in this order, because each step loses less than the next:

1. Level 4 and 5 sections the promise does not need (they stay in the plan, left off the route).
2. Rare ideas (see `syllabus.md`): move them to the "left out on purpose" list.
3. Merge two thin lessons into one, or turn a one-command lesson into a `short`.
4. Route by section instead of by chapter (below).

Never cut the practice at a chapter's end or the "when it goes wrong" sections: they are where the ability comes from.

Example. The learner has 4 hours a week for 5 weeks (20 hours) and the plan costs 31 hours over 14 chapters. Weak: drop chapters 11 to 14 (the reader never gets to deployment, which was the goal). Better: keep the chapters the goal needs, take level-4 sections off the route, and route chapters 9 and 10 by section.

## Routing by section

When only part of a chapter is needed, ask the script for the fewest sections:

```text
python3 scripts/us_plan.py needs <book> 7.3 7.5
```

It prints those sections and, in turn, the unwritten sections that teach what they need, with words and tokens; a line "also not written earlier in chapter N" lists sections the plan does not link but that come before. Add from that line what a beginner cannot do without (judge by reading their titles), then write the route line as `- <book> 7 sections 7.1 7.3 7.5`. `us_autopilot.py` leaves such chapters out, so say the writer must take them one at a time.
