# Three first chapters from the final validation (18 November 2026)

Each folder is what one fresh Opus agent, following the skills from a learner's first "hi", left behind in a clean
copy of this repository: the contents page, the book's sheet, the facts card, chapter 1 and the review notes.
Nothing here was edited by hand. The learner cards and instructions are in [`tests/evals/`](../../tests/evals/).

| Book | Kind | Learner | Chapter 1 | Programs | Plan, chapter and review |
|---|---|---|---|---|---|
| [`python-sales`](python-sales/chapters/01-first-program.md) | language | a spreadsheet user who has never programmed | 7 sections, about 7,800 words | 35; 33 ran, 2 are fragments; 2 trace tables from real runs | 11.8 min, 153,280 tokens |
| [`learn-os`](learn-os/chapters/01-one-programs-life.md) | system | a student four weeks before an operating systems exam | 8 sections, about 13,400 words, 2 figures | 26 of 26 ran (C programs and terminal sessions) | 13.1 min, 188,742 tokens |
| [`usability-testing`](usability-testing/chapters/01-first-test.md) | skill, nothing to run | a design intern who must run her first test | 8 sections, about 11,200 words, 1 figure | none | 8.1 min, 139,542 tokens |

After the product's own review (risk list, then one read), an independent Opus reader scored each chapter for
its learner with [`tests/evals/RUBRIC.md`](../../tests/evals/RUBRIC.md):

| | Accuracy | Depth | Clarity | Sequencing | Practical | Exercises | Completeness | Mean |
|---|---|---|---|---|---|---|---|---|
| Python | 8 | 9 | 8 | 8 | 9 | 9 | 8 | 8.4 |
| Operating systems | 6 | 9 | 8 | 8 | 9 | 9 | 8 | 8.1 |
| Usability testing | 8 | 9 | 9 | 9 | 10 | 9 | 8 | 8.9 |

**What the readers still found, so you know what to look for:**

- *Operating systems:* a practice answer said that without `fflush` the prompt would not appear before the
  read. Nobody had run that case, and on Linux it is false. This led to a new rule (a claim about a case nobody ran
  is run or marked), and the review was run once more with it: it tried 17 such claims, found this one wrong and
  one set of timings off, and fixed both. The chapter here is the corrected one; it was not scored again.
- *Python:* two loose sentences about how many digits a decimal number prints with; a promise about chapter 6 that
  the plan does not keep; the causes of one error listed three times; too many new words in section 1.1.
- *Usability testing:* three small slips inside its own worked examples (a "free" delivery option the notes never
  show, clock times that do not fit, one prompt missing from the model notes); nothing about testing a phone
  design on a phone; more everyday pictures than it needs.

The pasted output in these chapters was produced just before the runner began showing a program's own folder as
`/home/you/...` in its error messages; a chapter written today shows the full path there.
