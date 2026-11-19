# Feature inventory (audit of 18 November 2026)

Counted at the level of a capability a learner or builder would name, not of files or functions. Made by reading the
repository and running its tests on this date, not from earlier progress notes.

**Status words**

- **Proven**: covered by automated tests that pass today, or exercised end to end in this cycle's trials.
- **Built, thin evidence**: the instructions exist and were followed in a few scripted scenes on 16 November, with an
  older version of the skills; not re-run since the skills changed.
- **Partial**: works in a test set-up, not yet in the real situation.
- **Proposed**: discussed and designed on paper; nothing in the repository.

## Counts

| | Capabilities | Proven | Built, thin evidence | Partial | Proposed |
|---|---|---|---|---|---|
| Original (as received 16 November, 13:00) | 13 (one more was removed as unused) | 6 | 7 | 0 | 0 |
| New (built 16 to 18 November) | 26 | 24 | 0 | 2 | 0 |
| Outstanding | 7 | 1 | 3 | 0 | 3 |
| **Total** | **46** | **31 (67%)** | **10 (22%)** | **2 (4%)** | **3 (7%)** |

Built in some form: 43 of 46 (93%). Proven: 31 of 46 (67%). The second number is the honest one.

Updated after stage 2 (18 November, 14:40): N21 to N23 were built and tested; they replace the proposals P6 and P8
and most of P9. Updated after stage 3 (15:40): N24 to N26 were built and tested; they replace P5 and the
script half of P7. Updated after stage 4 (19:35): the curriculum pilot (P1) was built and tested, and the test went
against it: books planned from cards scored lower than books planned without (stage 4). It is
switched off and counted as Partial, not Proven. P2, P3 and P4 depended on it and are stopped. Updated after stages 4 and 5
together (19 November): the curriculum was redesigned, built, reviewed and tested again. P3 (contest programming)
counts as Proven: two blind judges preferred the book planned from it. P1, P2 and P4 count as built with thin
evidence (here: reviewed by independent helpers and covered by tests, but level or untested with learners).
Updated for the third design (19 November): every step of every card now says how it lands (step notes), each card
names its deep steps, each goal of a track map is a checked block, and plans are one book of at most 16 chapters.
Third design (19 and 20 November): books planned with the curriculum beat books planned without it on the contents page in all six tested subjects (system design, contest programming, web, machine learning, coding interviews, DevOps; two blind judges each, 2 of 2, the last two after one round of fixes). First chapters: ahead in system design (8.71, 8.57 against 8.43, 8.29) and contest programming (8.86, 8.86 against 8.00, 8.43), level in web, slightly behind in the short extracts for machine learning, interviews and DevOps.

## 1. Original capabilities (in the checkpoint received on 16 November)

The checkpoint held a system prompt, eight skills, ten rule files and seven scripts (`install.py`, `us_book.py`,
`us_check.py`, `us_index.py`, `us_init.py`, `us_lib.py`, `us_log.py`). All were rewritten since; what follows is
their state today.

| # | Capability | Where | Depends on | Evidence today | Status |
|---|---|---|---|---|---|
| O1 | Every message is routed to the right skill without the learner naming one | `AGENTS.md`, skill descriptions | nothing | `tests/evals/routing.md`: 18 of 18 with the smallest model, six of them not about programming | Proven |
| O2 | Goal intake and private learner records | `us-start`, `rules/private-files.md`, `us_init.py` | O1 | three trial learners: `private/goal.md`, `machine.md`, `route.md`, `now.md`, `RESUME.md` were all written | Proven |
| O3 | Planning a subject as a book and a personal route | `us-map`, `rules/route-variations.md`, `rules/levels.md` | N1 | three trials planned 6-chapter books that passed the plan check | Proven |
| O4 | Writing chapters of the learner's book | `us-write`, `.claude/agents/us-writer.md` | N1, N2, N5, N14 | three trials: 7,800 to 13,400 words, every program run | Proven |
| O5 | One review of each chapter | `us-review`, `.claude/agents/us-reviewer.md` | N5, N16 | rounds 2 and 3 of the validation | Proven |
| O6 | Checking and indexing a book with no model | `us_check.py`, `us_index.py` | N1 | tests: tools 58, check 9, final 13 | Proven |
| O7 | Tutoring with five levels proved by doing | `us-teach`, `rules/levels.md`, `rules/teaching.md` | N8 | one scripted scene on 16 November | Built, thin evidence |
| O8 | Coaching the learner's own project without doing it | `us-build` | O1 | two scripted scenes on 16 November (refused to write the script; refused an unauthorised scan) | Built, thin evidence |
| O9 | Design practice, mock interviews, the engineer standard (design ladder, open-source studies, cloud projects, failure drills, case studies, outage stories) | `us-design`, `rules/engineer-standard.md` | O1 | scripted scenes on 16 November | Built, thin evidence |
| O10 | Algorithm and contest coaching | `us-compete` | O1 | scripted scenes on 16 November | Built, thin evidence |
| O11 | Security learning restricted to targets the learner owns | `rules/track-security.md`, rule 8 of `AGENTS.md` | O1 | scene build-2 on 16 November | Built, thin evidence |
| O12 | Cheat sheets, printable copies, notes from the learner's lectures | `rules/writing-modes.md`, `us_ingest.py` | O4 | none this cycle | Built, thin evidence |
| O13 | The same skills in Codex and Gemini CLI | `scripts/install.py`, `CLAUDE.md`, `GEMINI.md` | nothing | format checked against those tools' documentation; never run there | Built, thin evidence |
| (O14) | A cost log (`us_log.py`) | removed on 18 November | | no skill ever called it | Removed |

## 2. New capabilities (built since 16 November)

| # | Capability | Where | Depends on | Evidence | Status |
|---|---|---|---|---|---|
| N1 | The book model: a contents page with what each section teaches and needs; check, brief, next, status, mark, cost, needs, move, place | `us_plan.py`, `us_bookfmt.py`, `rules/book-standard.md` | nothing | tests: book 53, plan 17, e2e 20 | Proven |
| N2 | Every program and terminal session is run and its real output pasted; keys typed; time limits; "not run" labels; Docker clean-up; dangerous commands refused | `us_run.py`, `us_state.py`, `us_term.py` | N1 | tests: run 137, state 33, term 20 | Proven |
| N3 | Step-by-step trace tables made from a real run | `us_trace.py` (called by `us_run.py`) | N2, gcc and gdb for C | tests: trace 11; two tables in the Python trial chapter | Proven |
| N4 | Figures drawn from about ten lines of text, light and dark, with a description for screen readers | `us_draw.py`, `us-draw` | nothing | tests: draw 22 | Proven |
| N5 | The chapter gate: a Check yourself in every lesson, depth floors, a practice that climbs to a task on something the chapter has not used (`unseen=`), a note on a timing in prose that no pasted output shows, no pointer to a missing section, nothing used before it is taught, too many new terms flagged, size budget for skills | `us_check.py` | N1 | tests: check 9, final 13, tools 58 | Proven |
| N6 | Adding, replacing or patching one section | `us_section.py` | N1, N5 | tests: section 7 | Proven |
| N7 | A machine check before any usage is spent | `us_doctor.py` | nothing | tests: doctor 10 | Proven |
| N8 | Practice with no AI, with growing gaps between repeats, and a record of every answer | `us_practice.py` | written chapters | tests: offline 55, records 30 | Proven |
| N9 | A "where you left off" note for a month with no AI | `us_resume.py` | N8 | tests: offline; written in all three trials | Proven |
| N10 | Finding where something is taught without reading a chapter; key terms and index pages | `us_find.py`, `us_index.py` | N1 | tests: tools | Proven |
| N11 | A reading page in the browser: contents, search, map of the book, hidden answers, "not run" notes | `reader/index.html`, `us_reader.py` | N10 | tests: reader 24, map 20 | Proven |
| N12 | One writing method for any subject, shaped by five kinds of subject, with per-skill reference pages, templates and one sample section per kind | `rules/writers-guide.md`, `.claude/skills/*/references/`, `assets/` | nothing | three trials on unlike subjects, scored by independent readers: 8.4, 8.1, 8.9 | Proven |
| N13 | The book's one-page sheet and its facts card, looked up once | `BOOK.md`, `PRACTICES.md`, `plans/SOURCES.md`, `us-map` templates | N1 | written and used in all three trials | Proven |
| N14 | Review by risk, then one read, then a scored line with one repair | `us_check.py --risks`, `us-review/references/` | N5 | round 3: the read caught the slips the outside readers had named; 17 untested claims tried, one found false | Proven |
| N15 | Ready-made contents pages | `plans/learn-git` (17 chapters), `plans/learn-docker` (11 chapters) | N1 | both pass the plan check | Proven |
| N16 | Writing only the few sections a learner needs now | `us_plan.py needs`, route lines naming sections | N1, N6 | one trial session on 18 November | Proven |
| N17 | A re-test kit: three learner cases, an eight-line rubric, an independent reader, a routing check | `tests/evals/` | nothing | used for all three validation rounds | Proven |
| N18 | Example chapters as they came out | `examples/` | nothing | files present; scores recorded beside them | Proven |
| N19 | Writing chapters unattended | `us_autopilot.py` | a logged-in `claude` command | tests run it with a stand-in for the agent; it has never written a real chapter | Partial |
| N20 | Books about tools that keep things outside a folder (Docker) | `rules/tool-books.md`, `us_state.py` | Docker, downloads | proven on small home-made images; no chapter with real downloads (the build machine cannot reach Docker Hub) | Partial |

| N21 | Revision that chooses for the learner: what was missed, what they were sure of and got wrong, what later sections lean on, spread across books and sections, with a daily cap and a sixth box at 60 days; flashcards of each book's key terms | `us_practice.py` (`--due`, `--minutes`, `--cards`) | N8, N10 | tests: offline stage2 74 (one of them a 30-day run with three books); tried by hand on a real chapter | Proven |
| N22 | Question tags written with the chapter (idea, kind of task, the wrong belief caught) and a fifteen-line learner summary made by script: wrong beliefs that return, weak foundations and what leans on them, what can be explained but not yet applied, what is solid | `<!-- q: -->` in `rules/book-standard.md`; `us_bookfmt.py`, `us_check.py`; `us_practice.py --summary`, `private/learner.md`; `us-teach` reads it | N5, N8 | tests: book stage2 19, offline stage2; a trial chapter with 30 tags (`examples/stage2-trial/`) | Proven |
| N23 | A chapter project the learner can test alone: their own program run against the model answer's real output, or a checklist where nothing can be run | `check="COMMAND"`, `<!-- checklist: -->`; `us_practice.py check BOOK N.M` | N2, N22 | tests: both suites above; on the trial chapter a faulty program failed with the one differing line and the corrected one passed | Proven |

| N24 | A lasting record of what was checked: each settled doubt becomes a hidden mark saying how (a run, the facts card, a named source, certain knowledge, reworded), when and by what; the script stamps the passage, notices a later change to it, and writes the book's `FACTS.md` | `<!-- checked: -->`; `us_plan.py mark ... reviewed` and `restamp`; `us_check.py --facts [--stale M]`; `us_index.py` | N14 | tests: book stage3 23, tools stage3 13; trial: ten doubts in a real chapter became ten stamped marks (8 by run, 1 by source, 1 reworded) | Proven |
| N25 | Known mistakes are re-checked by script on every chapter: a list per subject of statements that have been wrong before, each with the truth and its source; a book keeps its own list of what readers reported; the planner prints the truths for a new book's facts card | `rules/known-mistakes.md` (read by the script, never loaded by an agent), `book/<book>/MISTAKES.md`; `us_check.py`, `--mistakes`, `--learn` | N5 | tests: every seeded row against a sentence stating the mistake and against its truth | Proven |
| N26 | Checks across a whole book: a term two ideas claim, a section that says it needs an idea and never uses it, a chapter that builds on nothing earlier; a digest of at most 3,500 words for one read across chapters at the end of each part (the book pass) | `us_check.py BOOK`, `--digest`; `us_plan.py status`, `mark BOOK pass N`; `us-review/references/book-pass.md` | N1, N10 | tests as above; trial on a two-chapter book: the pass read 1,736 words, opened one passage and fixed one promise chapter 1 made about chapter 2 | Proven |

## 3. Outstanding capabilities (asked for or proposed; not in the repository)

| # | Capability | Asked in | State | Nearest thing that exists |
|---|---|---|---|---|
| P1 | Curriculum layer: domain indexes, track maps, subject cards | proposal of 18 November, 13:18 | BUILT (stages 4 and 5, deepened in the third design): 34 cards, 6 track maps, 5 indexes, each reviewed by a different helper; every step with step notes (`Need:`, `Show:`, `Explain:`, `Try:`), deep steps named, words owned or only met, every goal a block (`us_path.py goal`), all deepened by one helper and verified by a second who reran every `Show:`; goal-wide outline, step accounting, per-chapter notes in lesson order (`us_plan.py brief`), budget, one book of at most 16 chapters that reaches the goal on its own; 58 + 24 tests. Blind tests (second design): better than no curriculum for contest programming (2 of 2 judges), level for system design. Third design (19 and 20 November): books planned with the curriculum beat books planned without it on the contents page in all six tested subjects (system design, contest programming, web, machine learning, coding interviews, DevOps; two blind judges each, 2 of 2, the last two after one round of fixes). First chapters: ahead in system design (8.71, 8.57 against 8.43, 8.29) and contest programming (8.86, 8.86 against 8.00, 8.43), level in web, slightly behind in the short extracts for machine learning, interviews and DevOps. Web, DevOps and AI tracks reviewed but not blind-tested | two ready-made plans, the sources list |
| P2 | Job-readiness scoring mapped to professional roles | same, and this audit | BUILT: five role maps from dated adverts and public ladders; `us_path.py role` (what is left) and `us_path.py ready` (a score from books and practice records); tested by script; no learner has used it | the engineer standard (eight requirements, tracked in `private/standard.md`) |
| P3 | A serious competitive-programming pathway (ordered topics, problem ladder) | same | BUILT: ten cards from C++ for contests to geometry and contest strategy, every step tied to a real public problem, a goal block for each contest level; two blind judges preferred the book planned from it (second design; third design under P1) | the contest coach skill and its record file |
| P4 | A system-design and distributed-systems curriculum with working vocabulary | same | BUILT: ten cards from networking to consensus, reliability, API design and interviews, with the vocabulary tagged step by step (owned or only met) and checked in each chapter; blind tests under P1 | the design skill, mock interviews, the engineer standard |
| P7 | Chapters deep inside a book scored by an outside reader (the saved stage 1) | proposal of 13:31 | one chapter 2 written and reviewed in trials; not scored by an independent reader | whole-book checks and the book pass (N26) |
| P9 | Exercises that join two or more subjects the learner has studied | same | nothing built (planned for the closing stage) | revision already mixes and balances all books (N21) |
| P10 | Learning by reconstructing existing software | proposal of 13:18 | deferred on my advice | the project skill accepts "an app or repository to understand" |

## 4. Validation that only a person can still do

A person reading a whole chapter; one chapter on a 20-dollar plan with the usage meter read; a real unattended run;
a Docker or Spring Boot chapter on a machine with downloads; the skills running in Codex or Gemini CLI; Windows
(the scripts need Linux, macOS or WSL); choosing a licence.
