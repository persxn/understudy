# new-graduate-software-engineer: a first software-engineering job
status: reviewed 2026-11-18 by independent agent, sources reopened
sources: read 2026-11-18: dropbox.github.io/dbx-career-framework IC1; handbook.gitlab.com backend engineer; adverts
  (posted): Google Early Career Campus 2026-08-14 (anitab.org), Stripe New Grad 2026-09-02, Cohesity
  2026-08-12, Airtable (closed 2026-03-06), Benchling (removed 2026-01-30), D2L Spring 2026 (communitech.ca),
  Suade 2026-05-21 (workable.com); metacareers.com/swe-prep-techscreen;
  missing.csail.mit.edu (tools degrees skip)
unverified: classes of the DP and graphs lines are judgement

| Subject | Level | Class | At work it looks like | Proved by |
|---|---|---|---|---|
| python-core | 3 Build | essential | features in the team's language (all 7 adverts) | code others can read, run, test |
| dsa-core-techniques | 3 Build | essential | DS/algorithms (4 of 7 adverts) | unseen problems, cost stated |
| interview-problem-solving | 3 Build | essential | the coding screen (Meta: 45 minutes) | three recorded mocks, scored |
| git | 3 Build | essential | code review (4 of 7 adverts, Dropbox, GitLab) | reviewed PR, conflict resolved, commit recovered |
| software-testing (planned) | 3 Build | essential | tests with each change (Dropbox, Suade, GitLab) | a bug fixed test-first |
| sql-and-relational | 3 Build | desirable | queries, schema changes (Suade SQL, D2L databases) | indexed schema, race-safe update |
| networking-basics | 2 Explain | desirable | service calls (Google preferred) | a request traced, timed |
| linux-command-line | 2 Explain | desirable | Linux (Google preferred) | a crash explained from its logs |
| system-design-foundations | 2 Explain | desirable | system design (Cohesity, Airtable, D2L, Google) | a one-page design with numbers |
| recursion-and-dynamic-programming | 3 Build | desirable | harder interview problems | unseen DP problems |
| graphs-and-trees | 3 Build | desirable | dependencies, routes | unseen BFS, shortest-path problems |
| ai-assisted-development (planned) | 3 Build | desirable | AI tools, checked (Google, Stripe, D2L) | a flawed AI change caught |
| caching-and-queues | 2 Explain | specialist | backend specialism (Stripe preferred) | a cache stampede explained |

## Order and time
Table order; dsa-core-techniques needs python-core or cpp-for-contests (25 h). Essential 190 h, desirable 240 h (`role`; maps' judgement).

## Interview checks
- A coding problem solved aloud with its complexity (interview-problem-solving, dsa-core-techniques).
- Your project: a bug found, its fix tested (python-core, software-testing).
- Reviewing a pull request or answering review (git).
- A small design: tables, endpoints, what breaks at 10x load (sql-and-relational, system-design-foundations).

## Capstone
A team-built web service with a database: pull requests, CI tests, indexed schema, one race-safe operation, a one-page design. Finish: a stranger clones it; one command passes all tests.

## Overlap
Backend: SQL, networking, design. core-cs/coding-interviews: interview lines. SRE, platform: git, networking, Linux.
