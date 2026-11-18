# Deriving a complete syllabus

Read before drawing the contents page of a new book. A plan written from memory covers what the planner knows well and silently drops the rest.

## Where coverage comes from

Use three sources, each for one job. Work from what you already know of them; planning needs no web search. Look one up (one page: a contents list or an exam syllabus) only when you cannot name the subject's main parts with confidence, or the learner named a syllabus of their own (then theirs is the checklist):

- **The official documentation's own contents** sets the facts and the surface. The tutorial's chapter list shows what the makers think comes first; the reference index shows everything there is. (Python's tutorial, Pro Git's contents, the PostgreSQL manual's parts.)
- **A recognised curriculum or exam syllabus** sets completeness: committees wrote it to leave nothing out. ACM/IEEE CS2023 for systems, the ISTQB Foundation syllabus for testing, the CKA curriculum for Kubernetes, an AWS exam guide for a cloud service. Use it as a checklist, never as an order: exam objectives are grouped by domain, not by learning.
- **What jobs ask for** sets the cut. Read five to ten job ads for the reader's target role: what most name is in; what one names is out unless the promise needs it.

## List, link, order

1. **List ideas, not features.** One line each, phrased so it could be tested: "a commit records a snapshot of the staged files", not "commits". Group sibling commands under the idea they serve. A full book has 150 to 300.
2. **Mark each** core (the promise fails without it), common (met within a month of real work) or rare.
3. **Find direct dependencies.** Ask of each idea: what must the reader already picture or do to follow its first example? Hidden ones cause most bad orders: a remote-tracking branch needs "a branch is a pointer"; `useEffect` needs "a component runs again when state changes".
4. **Order** so nothing is used before it is taught, then choose among the valid orders: a real result in chapter 1; each chapter adds what the running project needs next; use before internals; meet a hard idea simply, return deeper later at level 2. Errors sit beside the idea that causes them, never in a last chapter.
5. **Cut for the promise.** Keep core, keep common that serves the promise, list the rest as left out on purpose (the list goes at the bottom of `private/route.md`). Watch what the promise needs silently: "deploy a Flask app" needs environment variables and reading logs though nobody says so.

## Worked example: SQL for a data analyst

Sources: the PostgreSQL tutorial's contents; analyst job ads (joins, CTEs and window functions in most; indexes and table design in few). Dependencies found: `GROUP BY` needs aggregates; `LEFT JOIN` needs NULL; `HAVING` needs groups; window functions need groups, to see how they differ. Cut: creating tables, indexes, transactions (not in the promise); kept: reading a schema, because joins need keys.

Chapters: 1 Asking one table questions (select, filter, sort, limit) · 2 Missing values and types (NULL, dates, CASE) · 3 Summaries (aggregates, groups, HAVING) · 4 Joining tables (keys, inner, left) · 5 Queries inside queries (subqueries, CTEs) · 6 Window functions (ranking, running totals) · 7 A real analysis from question to report.
