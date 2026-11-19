# full-stack-developer: junior to mid-level developer building a web product end to end
status: reviewed 2026-11-19 by independent agent, sources reopened
sources: read 2026-11-18/19: handbook.gitlab.com fullstack; dropbox.github.io/dbx-career-framework IC2; adverts
  (updated): Momence 2026-10-01, Figma 09-24, Pendo 11-03, Automox 09-30, SpaceX Starlink 09-29, Loenbro 09-03,
  StackAdapt 10-29, Breeze Junior 09-01; 7 reopened 11-19; Softeta Junior AI-Native 07-22
unverified: essential 5+ of 8, desirable 2-4, or needed by such a line; Momence asks 7+ years; levels:
  judgement

| Subject | Level | Class | At work it looks like | Proved by |
|---|---|---|---|---|
| javascript | 3 Build | essential | JS or TS (8 of 8) | page fetching data |
| typescript | 3 Build | essential | TypeScript (7 of 8) | typed feature |
| react | 3 Build | essential | React (7 of 8; Vue 1) | tested screen |
| node-and-express | 3 Build | essential | a server side (8 of 8; Node 4) | API on a pool |
| sql-and-relational | 3 Build | essential | SQL (6 of 8) | indexed schema |
| software-testing (planned) | 3 Build | essential | tests (6 of 8) | end-to-end test |
| git | 3 Build | essential | code review (6 of 8) | PRs reviewed |
| api-design | 3 Build | essential | REST, GraphQL (6 of 8) | paged, retry-safe API |
| system-design-foundations | 2 Explain | essential | design, architecture (7 of 8) | one-page design |
| html-and-css | 3 Build | essential | HTML, CSS (2 of 8, GitLab; react needs it) | keyboard-usable page |
| networking-basics | 2 Explain | desirable | none named; node needs it | request traced |
| caching-and-queues | 2 Explain | desirable | api-design needs it | retried job made safe |
| web-auth-and-security (planned) | 3 Build | desirable | security (4 of 8, GitLab) | login, XSS blocked |
| llm-application-engineering | 3 Build | desirable | LLM features (3 of 8) | evaluated feature |
| github-actions-ci-cd | 3 Build | desirable | CI/CD (3 of 8) | every PR tested |
| ai-assisted-development (planned) | 3 Build | desirable | coding agents (Loenbro, Softeta) | flawed AI change caught |
| cloud-core-services (planned) | 1 Use | desirable | a cloud (3 of 8) | deployed to a cloud |
| reliability-and-observability | 2 Explain | desirable | on-call (2 of 8, GitLab) | alert traced |
| docker | 3 Build | desirable | Docker (2 of 8) | compose up |

## Order and time
web/full-stack rows 1-8; system-design-foundations, caching-and-queues, api-design, software-testing;
the rest after their needs (off this list: python-core, 40 h; linux-command-line, 20 h). Essential 345 h,
desirable 255 h.

## Interview checks
- A feature, screen to database (Momence, Loenbro): react, node-and-express, sql-and-relational.
- How you test it (Momence, StackAdapt): software-testing.
- An API for it (StackAdapt, Pendo): api-design.

## Capstone
A React and TypeScript app on its Express API and PostgreSQL, with login. Finish: `docker compose up` starts
it; a stranger signs up and edits data; one command runs unit and end-to-end tests, all pass.

## Overlap
backend-engineer: SQL, APIs, tests. Front-end: web/full-stack rows 1-5. Ruby, Go,
Java, .NET, PHP, Vue: no card; next-js (planned).
