# Web: full-stack developer
for: someone who wants to build web apps for a living
leads to: junior front-end, back-end or full-stack developer
status: reviewed 2026-11-19 by independent agent, goal blocks written and read as planner
sources: the cards' needs lines; react.dev/learn/creating-a-react-app (row 13);
  expressjs.com best-practice-security (row 10)
unverified: hours, levels, goal steps and planned rows are judgement

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | html-and-css | none | build pages usable by keyboard, at any width | semantic HTML, forms, flex, grid | 40 | 3 Build |
| 2 | javascript | none | make pages fetch data and respond | closures, async, the DOM, npm | 60 | 3 Build |
| 3 | git | none | work by pull requests | branches, merging, undo | 15 | 3 Build |
| 4 | typescript | 2 | type a real code base | narrowing, generics, boundaries | 30 | 3 Build |
| 5 | react | 1, 2 | build screens, state well placed | state, effects, fetching, testing | 50 | 3 Build |
| 6 | networking-basics | none | follow a request to a server | DNS, TCP, TLS, HTTP | 25 | 2 Explain |
| 7 | sql-and-relational | none | model and query an app's data | joins, indexes, transactions | 30 | 3 Build |
| 8 | node-and-express | 2, 6, 7 | run a service that stays responsive | event loop, middleware, pool | 45 | 3 Build |
| 9 | api-design | 6, 7, system-design-foundations, caching-and-queues | design an API clients can retry and page | errors, paging, idempotency | 20 | 3 Build |
| 10 | web-auth-and-security (planned) | 6, 8, python-core | log users in and stop common attacks | sessions, OAuth, CSRF, XSS | 25 | 3 Build |
| 11 | software-testing (planned) | 2, python-core | prove a change works | unit, integration, end-to-end | 25 | 3 Build |
| 12 | docker | 6, linux-command-line | ship the app in containers | images, compose | 30 | 3 Build |
| 13 | next-js (planned) | 5, 6 | build a server-rendered React app | routing, server rendering | 30 | 3 Build |
| 14 | ai-assisted-development (planned) | 3, 11 | ship changes made with coding agents, checked | diff review, permissions | 15 | 3 Build |

## Goals
### My first front-end job (about 210 h)
Steps: html-and-css; javascript; react; git 1-10, 12; typescript 1-12; networking-basics 1-5, 7-8.
Open with: a page of their own (the app they mean to build, or their portfolio) typed as a document, opened in
the browser and committed (html-and-css 1, git 1); then broken once on purpose: a `div` inside a `p`, the
repaired tree read in Elements.
Deep: html-and-css 4, 5; javascript 3, 10; react 4, 9.
Order: html-and-css 1-2 with git 1-2; javascript 1-4; html-and-css 3-5; javascript 5-9, 13; git 3-6;
html-and-css 6-9; typescript 1-4; react 1-5; javascript 10-12, 14; networking-basics 1-5, 7-8; typescript 5-6,
10; react 6-10; git 7-10, 12; html-and-css 10-13; typescript 7-9, 11-12; react 11-14; next-js (row 13) once
written.
Halfway: "My page works by keyboard, and my first React screen keeps its state where I can say why."

### My first full-stack job (about 345 h)
Steps: html-and-css; javascript; react; sql-and-relational; node-and-express; git 1-10, 12; typescript 1-12;
networking-basics 1-5, 7-10; api-design 1-8; caching-and-queues 8; linux-command-line 1-8, 12; docker.
Open with: the first page of the app they will build end to end, typed and committed (html-and-css 1, git 1),
then broken once on purpose: a `div` inside a `p`, the repaired tree read in Elements.
Deep: html-and-css 5; javascript 10; react 4; sql-and-relational 8; node-and-express 4, 10.
Order: html-and-css 1-2 with git 1-2; javascript 1-4; html-and-css 3-5; javascript 5-9, 13; html-and-css 6-9;
git 3-6; typescript 1-4; react 1-5; javascript 10-12, 14; networking-basics 1-5, 7-8; sql-and-relational 1-4;
node-and-express 1-5, 7-9; typescript 5-6, 10; react 6-10 against their own API; sql-and-relational 5-11;
node-and-express 6, 10-14; networking-basics 9-10; api-design 1-6, caching-and-queues 8, api-design 7-8 (the rest
of both, and system-design-foundations, `later:`); git 7-10, 12; linux-command-line 1-8, 12; docker;
html-and-css 10-13; typescript 7-9, 11-12; react 11-14; rows 10 and 11 once written.
Halfway: "My React screen and my own Express route both run, in git, and I can say when each line runs."

### I build back ends and must now build a UI (about 145 h)
Steps: html-and-css; javascript; react 1-11, 13-14.
Open with: one resource of their own API as a hand-written page, read in Elements and the Accessibility pane
(html-and-css 1-2); then broken once on purpose: a bold `div` as a heading, which no screen reader finds.
Deep: html-and-css 5, 8; react 4, 5, 9.
Order: html-and-css 1-2; javascript 1-9, 13 (a Node developer holds 1-12: about 95 h); react 1-5;
html-and-css 3-9; javascript 10-12, 14; react 6-11; html-and-css 10-13; react 13-14. Types only if their
code is TypeScript.
Halfway: "I can build a React screen from my API's JSON and say why typing in it re-renders what it does."

### Add TypeScript to my team's JavaScript (about 40 h)
Steps: typescript; react 1, 3-4.
Open with: `// @ts-check` on one file of their team's code, `tsc` run, one real error read; then broken once on
purpose: a string passed as a number, the error printed and the JavaScript still written (typescript 1, 13).
Deep: typescript 4, 5, 10, 13.
Order: typescript 1, 13 in miniature, 2-4, 6; react 1, 3-4 on React code (else `later:`); typescript 5, 10-11,
7-9, 12, 13 in full; javascript `held`.
Halfway: "Our first files pass `tsc`, and I can type our components' props, events and state."

## Why this order
HTML and CSS first: DOM steps need a page. TypeScript before React, whose steps then type props, events and state. SQL before Node: a request ends in the pool. docker needs linux-command-line (DevOps map). Rows 10 and 11 need one language: row 8 (2 for 11) or python-core.

## Checkpoint projects
- After 5: a screen of the learner's app on a public API, tested. After 8: on its own Express API and database. After 12: started by `docker compose up`.

## Short on time
Goals' steps are the floor: less depth, never fewer steps. Rows 4 and 13 may wait for a team without them.

## Left out on purpose
- Vue, Angular, Django, Rails: one stack learnt deeply transfers.
