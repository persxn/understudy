# Outstanding work and the way forward (audit of 18 November 2026)

Read with `docs/FEATURES.md` (what exists, with evidence). Figures marked **measured** come from runs in this
repository's record (`examples/final-validation/`); figures marked **estimate** do not.

## 1. Does the learning system deliver what was asked?

| Asked for | Verdict | What exists | What is missing |
|---|---|---|---|
| Reliable progress tracking | Mostly yes | Levels per chapter (`claimed`, `in progress`, `proven`), every practice answer with date and confidence, weak spots, a resume note; all in plain files | The tutoring side has thin evidence since the skills were rewritten |
| Job-readiness scoring mapped to professional competencies | Yes, untested with learners (since 19 November) | Five role maps built from dated adverts and public ladders; `us_path.py ready ROLE` scores each line from books and practice records and names what to start next | The score counts practice answers, not the "Proved by" task of each line; adverts go stale and need re-sampling |
| Deep DSA and a serious competitive-programming pathway | Yes (since 19 November) | Ten reviewed cards from contest C++ to geometry and strategy, every step tied to a real public problem; goal lines by contest level; an interviews track; two blind judges preferred the book planned from it | Only a first chapter was judged; no person has trained from it |
| System design and distributed-systems fundamentals | Yes, level with no curriculum in a blind test (since 19 November) | Ten reviewed cards (networking to consensus, reliability, API design, interviews); vocabulary tagged to the step that teaches it and checked by script in each chapter | In the last blind test one judge preferred the book planned without it; chapters come out thinner |
| Adaptive spaced repetition | Yes (since stage 2) | Offline revision ordered by misses, sure-but-wrong answers, time overdue and what later sections lean on; balanced across books; daily cap; flashcards | Self-marked, so only as honest as the learner |
| Misconception tracking | Yes for new chapters (since stage 2) | Questions tagged with the wrong belief they catch; a script-made summary names beliefs that return and tells "can explain" from "can apply" | Chapters written before 18 November have no tags and fall back to the section's idea |
| Cumulative assessment and cross-subject revision | Little | Surprise questions from older chapters are an instruction to the tutor | No exercises that join subjects; nothing tested (P9) |
| Competence proved, not chapters completed | Yes | A level counts only on work the learner produced; since stage 2 each chapter project has a finish line the learner tests alone | Design and teach levels still need the model; the tutor's own checks have thin evidence |
| High-quality, technology-specific textbooks | Yes for first chapters | Three unlike subjects scored 8.4, 8.1, 8.9 of 10 (**measured**, AI readers) | Teaching decisions per technology are made afresh each time (P1); chapters deep in a book untested (P7) |

**How it fits together today:** the book and its questions are the single source; practice, levels and the resume
note all read from it, so nothing is generated twice. That spine is sound. What is thin is everything that should
sit on top of it: role-level readiness, long-term retention across subjects, and proof that the teaching skills
behave as written.

## 2. Cheapest architecture that keeps the quality

| Question | Recommendation | Why |
|---|---|---|
| Precompute once or generate each time? | Precompute contents pages, facts cards and teaching decisions for common subjects; generate only the chapter text for the learner | Planning a 17-chapter book cost 83,187 tokens (**measured**); a ready-made plan costs none |
| Where should assessments come from? | From the chapter, written once with it: tagged questions, a project with a finish line a script can test | Practice already reuses chapter questions at zero tokens; extend that, never regenerate |
| What can scripts take over next? | Revision order and balance, flashcards from each book's key terms, the learner summary, re-checks of known mistakes, clashes between chapters over one term | All are rule-following work on files that already exist |
| Which agent calls can go? | None of the two (writer, reviewer). Do not add a verifier agent. | The independent review found real faults the writer missed (**measured**: 3 to 8 slips a chapter, one false statement). A third agent would add about one review's cost per chapter for little gain |
| Is the reviewer too dear? | Keep it; measure its fixed overhead on a learner's machine | It cost 98,270 to 139,237 tokens here (**measured**), most of it the build environment's start-up load, which may not apply to a learner |
| Whole-book checks | Scripts for structure; one read per part of a book over a script-made digest, not a read per chapter | **Estimate:** 10,000 to 20,000 tokens a chapter, averaged |
| What to remove | The older review commands `--suspects` and `--prose` and the `spines/` format (no skill uses them); the fixed `19 tokens a word` in `us_plan.py cost` should be re-derived from a learner's real run | Less to maintain; honest estimates |
| With no subscription | Already: reading, search, practice, records, resume note. Add: smarter revision, flashcards, project tests | All script work |

## 3. Plan, in order

**Essential (closes gaps in what is already claimed)**

1. Write and review chapters 2 and 3 of one test book with the current method, and score them: nothing yet shows
   that a later chapter builds well on an earlier one.
2. Re-run the scripted scenes for tutoring, project coaching, design and contests against the rewritten skills.
3. The owner's own checks: one chapter on a 20-dollar plan with the meter read; one unattended run; one Docker or
   Spring Boot chapter on a machine with downloads; a person reading a chapter.

**High value (mostly scripts)** (items 4, 5 and 7 were built and tested in stage 2, item 6 and the whole-book checks in stage 3, both on 18 November)

4. Revision that orders by importance and weakness, balances subjects, caps the daily load, and makes flashcards.
5. Question tags written with the chapter, and a ten-line learner summary built by script.
6. A lasting "checked, how, when" mark on settled facts and a list of known mistakes re-checked on every chapter.
7. A testable finish line for each chapter project.
8. Pilot of the curriculum layer: about ten subject cards, two track maps, one role map, and a with-and-without test
   on real chapters. Scale up only if the cards raise the score. DONE 18 November, 19:35: the cards did NOT
   raise the score (contents page 6 to 7 of 10 with a card against 8 without; chapters level). The pilot is
   switched off and item 9 is stopped.
   REDONE 19 November with a second design (see item 9).

**Optional**

9. The full curriculum layer (about 80 cards, 20 track maps, 12 roles), role-readiness scoring, the
   competitive-programming and system-design pathways built on it. BUILT 19 November at a smaller, reviewed size:
   34 cards, 6 track maps, 5 roles (quality before number, on the owner's instruction). Still planned and named
   as such in the maps: software-testing, web-auth-and-security, a React framework, terraform, a cloud's core
   services, kubernetes-internals, python-for-data, deep-learning-with-pytorch, retrieval-systems, model serving,
   operating-systems-core.
10. Cross-subject exercises, written once per pair of related books.
11. Learning by reconstructing existing software (a narrow version inside the project skill).

## 4. Cost

| | Figure | Kind |
|---|---|---|
| One planned book, one first chapter, its review | 139,542 to 188,742 tokens, 8 to 13 minutes | measured |
| Tokens per word of finished chapter, planning and review included | 12 to 20 | measured |
| This cycle's build and validation | about 2.8 million tokens of Opus agents | measured, from the agents' own reports |
| Items 1 and 2 | about one five-hour session | estimate |
| Items 4 to 7 | about two sessions | estimate |
| Item 8 | one to two sessions | estimate |
| Item 9 | five to six sessions | estimate |
| Added cost to a learner of items 4 to 7 | about 10 to 15 percent per chapter written; near zero for tutoring; zero for revision | estimate |
| A tutoring session; the share of a 20-dollar plan one chapter uses | unknown | not measured |

**Usage by kind of learner (estimates, in chapters and sessions, not rupees):** the plan's price is flat and its
allowance is not a published token count, so rupees per activity cannot be computed honestly until one chapter is
written on such a plan and the meter is read. Until then: a light learner (reads, practises offline, a little
tutoring) spends almost nothing beyond the chapters they ask for; a moderate learner's main cost is one chapter at a
time, at the measured figure above; an intensive learner writing many chapters is limited by that same figure, and
the recommended additions would cost them about one chapter in ten.

**Savings expected from the recommendations (estimates):** a ready-made plan saves the planning of a book
(83,187 tokens measured for a large one); offline revision replaces tutor-run revision entirely; local project
tests replace a model-run check for "build" tasks; nothing recommended adds a recurring model call.

## 5. Quality on 18 November

- **Tests (after stages 4 and 5, 19 November):** 758 automated tests in 23 suites, all passing (new: tools path 61, tools stage5 24; three suites need a Docker daemon running for their full count). **After stage 3:** 668 automated tests in 21 suites, all passing (new since the audit: book stage2 19, offline stage2 74, book stage3 23, tools stage3 13). At the audit: 539 automated tests in 17 suites, all passing when this was written (book 53, e2e 20, plan 17,
  section 7, check 9, final 13, run 137, trace 11, state 33, term 20, tools 58, doctor 10, offline 55, records 30,
  draw 22, reader 24, map 20). They cover the scripts, not the judgement in the skills.
- **Skills:** validated by three end-to-end trials and independent AI readers; the routing check passed 18 of 18.
- **Known limits:** accuracy is the weakest line (6 to 8 of 10): expect a small slip or two a chapter. Scores vary
  by reader. Only first chapters were scored. No person has read one.
- **Known rough edges:** `us_plan.py cost` over- or under-states until re-derived; the pasted output in the three
  example chapters predates the `/home/you/...` path change; four test files look for an optional folder from the
  build machine and skip that part without it; examples from before 18 November use the retired fixed headings.
- **Security:** chapter programs run on the learner's machine as an ordinary user with time and memory limits, a
  private home folder and a refusal list for destructive commands. That is care, not a sandbox: the network and
  the user's other files stay reachable. Material read from the web is treated as reading matter only, by
  instruction, which a model can fail to follow. The unattended writer starts `claude -p` with the learner's own
  permissions. Nothing personal is written into `book/`; `private/` is ignored by git.
- **Technical debt:** three long scripts (`us_draw.py` 2,379 lines, `us_run.py` 1,897, `us_check.py` 1,273);
  unused older commands still present.
- **Rating:** as a tool that writes and teaches from a good textbook: 8 of 10. Against the full learning system
  described in the latest briefs (role readiness, long-term retention, proven competence): about 6.5, because
  those parts are proposed, not built. After items 1 to 8, if their tests hold: 8.5 to 9.

## 20 November, 00:30: the third design of the curriculum is finished

All 34 cards and six roadmaps are deepened and verified; the planner and writer rules and four script checks were changed after blind tests; books planned with the curriculum now beat books planned without it on the contents page in all six tested subjects, and on the first chapter in system design and contest programming.

Still open, most useful first:
1. Write again and judge the first chapters for machine learning, interviews and DevOps (their extracts scored 0.1 to 0.4 below, before the last fixes).
2. Chapter output must look like the learner's machine: a writer pasted the test machine's PATH and Python path into a Linux chapter. A check or a rule for console books.
3. A first section must not use shell syntax it has not explained (`&`, `wait`, `$(...)`): a rule for the writer, or the runner should let a session be typed as a person would.
4. A card for running a Linux server (load, memory, log rotation, firewall, reverse proxy, handover) and a step on online assessments in the interview card.
5. Test the LLM-feature route on a machine that can call a model; test one chapter deep inside a book; a person's read.
6. Small: a `|` in a section title is read as a field separator by the plan check; the deep-step "give it room" note fires when the 16-chapter cap forces sharing; `goal` prints 42 KB for the year-long contest goal.
