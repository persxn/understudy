# AI: engineering products on language models
for: a developer building product features on models
leads to: AI engineer; owner of an LLM feature
status: reviewed 2026-11-19 by independent agent, every Show rerun, goals run as planner
sources: the cards' needs and steps; hamel.dev evals, applied-llms.org (prompting and evaluation before fine-tuning: 2, 12)
unverified: hours, levels, goal steps and planned rows are judgement

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | python-core | none | write, test and ship Python | objects, classes, tests | 40 | 3 Build |
| 2 | llm-application-engineering | 1 | ship a measured model-backed feature | evaluation, retrieval, tools | 50 | 3 Build |
| 3 | sql-and-relational | none | store a feature's data and traces | joins, transactions | 30 | 3 Build |
| 4 | api-design | networking-basics, 3, system-design-foundations, caching-and-queues | serve it by a retry-safe API | errors, idempotency | 20 | 3 Build |
| 5 | reliability-and-observability | networking-basics, 3, system-design-foundations, caching-and-queues | watch it, survive overload | SLOs, traces | 30 | 3 Build |
| 6 | docker | linux-command-line, networking-basics | ship the service as an image | images, compose | 30 | 3 Build |
| 7 | machine-learning-fundamentals | 1 | train and honestly measure a tabular model | splits, leakage | 50 | 3 Build |
| 8 | python-for-data (planned) | 1 | work with arrays and tables | NumPy, pandas | 25 | 3 Build |
| 9 | retrieval-systems (planned) | 2 | tune search at scale | ranking | 30 | 3 Build |
| 10 | deep-learning-with-pytorch (planned) | 7, 8 | train and read a network | autograd | 60 | 3 Build |
| 11 | model-serving-and-mlops (planned) | 5, 6, 7 | deploy and watch models | serving, drift | 30 | 3 Build |
| 12 | llm-fine-tuning (planned) | 2, 10 | fine-tune when it pays | adapters | 30 | 3 Build |

## Goals
### Ship an LLM feature in the product I build (about 50 h)
Steps: llm-application-engineering.
Open with: one real call from their own code on a question their feature must answer, its reply scored by a
short script against five cases they wrote by hand, then run again and recounted (llm-application-engineering
2, with 5 in miniature).
Deep: llm-application-engineering 5, 6, 8, 9.
Order: llm-application-engineering 1-6, the evaluation set built before any retrieval or tool; 7-8 if it answers
from documents and 9-10 if it acts, else `later:` (about 35 h); 11; 12. python-core is `held` by a developer who
writes Python; if Python is new, python-core 1-4, 6-8, 10-14 first (about 35 h more). Row 7 waits.
Halfway: "Every change I make prints passes per failure mode before it ships."

### Make our LLM feature cheap and dependable (about 85 h)
Steps: llm-application-engineering 1-2, 4-6, 11-12; reliability-and-observability 1-7, 9; api-design 7, 10; system-design-foundations 1, 3-4, 7; caching-and-queues 8-9; sql-and-relational 7, 9; networking-basics 4-5, 8-10.
Open with: a day of their feature's traces turned into cost per request and p99 (llm-application-engineering 12),
then one saving, the prompt's stable part first so the cache can read it, rerun on 20 cases they labelled to
show quality held (5 in miniature).
Deep: llm-application-engineering 5; system-design-foundations 4; reliability-and-observability 2, 6, 7; caching-and-queues 9.
Order: llm-application-engineering 1-2 (often held), 5-6, 12, 4, 11; system-design-foundations 1, 3-4, 7;
reliability-and-observability 1-3; networking-basics 4-5, 8-10; caching-and-queues 9; reliability-and-observability
4-7; sql-and-relational 7, 9; caching-and-queues 8; api-design 7, 10; reliability-and-observability 9.
Halfway: "I know what one request costs and its p99, and no saving ships unless the set still passes."

### My first job as an AI engineer (about 270 h)
Steps: python-core; llm-application-engineering; git 1-7, 10; sql-and-relational 1-5, 7-10; networking-basics 1, 3-5, 8-10; system-design-foundations 1, 3-4, 7; caching-and-queues 8-9; api-design 1, 4, 7, 9-12; reliability-and-observability 1-4, 6-7, 9; linux-command-line 1-8, 12; docker 1-4, 6-12; machine-learning-fundamentals 1-9, 12-13.
Open with: as the first goal: one real call from their own code, scored against five hand-written cases
(llm-application-engineering 2, with 5 in miniature); if Python is new, after python-core, whose step 1 opens.
Deep: llm-application-engineering 5, 6, 8, 9; machine-learning-fundamentals 3, 9.
Order: python-core 1-8, 10-14 unless held (a first call needs `json`, `os.environ`, exceptions, a class and a
virtual environment); llm-application-engineering 1-6; git 1-7, 10; python-core 9; llm-application-engineering
7-12; sql-and-relational 1-5, 7-10; networking-basics 1, 3-5, 8-10; linux-command-line 1-8, 12; docker 1-4, 6-12;
system-design-foundations 1, 3-4, 7; caching-and-queues 8-9; api-design 1, 4, 7, 9-12; reliability-and-observability
1-4, 6-7, 9; machine-learning-fundamentals 1-9, 12-13 last; rows 9 and 11 when written.
Halfway: "I have shipped a feature with retrieval or a tool, gated by an evaluation set, from a repository others review."

### Work beside our data scientists (about 65 h)
Steps: machine-learning-fundamentals; llm-application-engineering 1-2, 5-6.
Open with: a baseline scored honestly on their own table: their team's model, `DummyClassifier` and a one-column
rule on the same held-out rows, in what an error costs (machine-learning-fundamentals 1, 4).
Deep: machine-learning-fundamentals 3, 9, 12; llm-application-engineering 5.
Order: machine-learning-fundamentals 1-13; llm-application-engineering 1-2, 5-6 last, the same evaluation habit
applied to model calls. python-core first unless held (about 40 h more).
Halfway: "Given a reported score, I can say whether it will hold on next month's data, and which split proves it."

## Why this order
Row 2 needs only Python and holds its own evaluation: ship first; training (7) waits: product work needs measurement more. Rows 3 to 6 make the feature a service; Goals take only the steps of their outside needs that they use.

## Checkpoint projects
- After 2: the learner's feature with an eval report. After 6: a containerised service with traces and an SLO. After 7: a tabular model beating its baseline.

## Short on time
Goals' steps are the floor. Rows 8 to 12 wait.

## Left out on purpose
- Research and training large models (another job); vendor courses (cards name what to look up); front-end (the learner's web stack).
