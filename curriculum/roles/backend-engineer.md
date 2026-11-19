# backend-engineer: backend engineer, one to three years in
status: reviewed 2026-11-19 by independent agent, sources reopened
sources: read 2026-11-18/19: dropbox.github.io/dbx-career-framework IC2; handbook.gitlab.com backend; adverts
  (updated): Stripe Core Tech 2026-09-10, DoorDash 08-17, Affirm SWE II 10-16, PlayStation SWE II 11-02,
  Robinhood 08-25, BitGo E2 11-16; LaunchDarkly, Wealthfront (undated); five reopened 11-19
unverified: essential 5+ of 8, desirable 2-4; git (ladders), networking-basics (prerequisite), levels,
  interview checks: judgement

| Subject | Level | Class | At work it looks like | Proved by |
|---|---|---|---|---|
| python-core | 3 Build | essential | a server language (8 of 8; Python 3) | tested service |
| sql-and-relational | 3 Build | essential | databases (7 of 8) | race-safe update |
| software-testing (planned) | 3 Build | essential | tests (7 of 8) | bug fixed test-first |
| system-design-foundations | 3 Build | essential | design (7 of 8, Dropbox) | one-page design |
| reliability-and-observability | 3 Build | essential | runs it (6 of 8; on-call 3) | alert, rollback |
| api-design | 3 Build | essential | REST, GraphQL (5 of 8) | paged, retry-safe API |
| git | 3 Build | essential | review (4 of 8; ladders) | PRs reviewed |
| distributed-systems-core | 2 Explain | desirable | named (4 of 8) | partition explained |
| cloud-core-services (planned) | 1 Use | desirable | AWS (4 of 8) | deployed to a cloud |
| caching-and-queues | 3 Build | desirable | Kafka, queues (3 of 8) | retry-safe consumer |
| scaling-data | 2 Explain | desirable | scalability (3 of 8) | failover costed |
| docker | 3 Build | desirable | containers (3 of 8) | small, safe image |
| github-actions-ci-cd | 3 Build | desirable | CI (3 of 8) | every PR tested |
| dsa-core-techniques | 3 Build | desirable | algorithms (3 of 8) | unseen problems |
| kubernetes-core | 1 Use | desirable | Kubernetes (2 of 8) | bad deploy undone |
| web-auth-and-security (planned) | 2 Explain | desirable | security (2 of 8) | injection blocked |
| networking-basics | 2 Explain | desirable | HTTP (1 of 8) | slow request traced |
| llm-application-engineering | 3 Build | specialist | AI services (1 of 8) | evaluated feature |

## Order and time
git, python-core, networking-basics, sql-and-relational, system-design-foundations, caching-and-queues; then
table order, each after its needs (linux-command-line, 20 h, docker, then cloud, CI). Essential 190 h, desirable 310 h.

## Interview checks
- Algorithms (Stripe, BitGo): dsa-core-techniques, interview-problem-solving.
- Design (Robinhood, Affirm, Dropbox): system-design-foundations.
- An API, its schema (DoorDash, PlayStation): api-design, sql-and-relational.
- An outage you owned (Wealthfront, Affirm): reliability-and-observability.

## Capstone
The learner's own Python service: PostgreSQL, queue worker, CI, SLO alert. Finish: one command passes all tests; a repeated POST with one idempotency key makes one row; stopping the database fires the alert.

## Overlap
new-graduate-software-engineer: language, git, SQL, DSA; full-stack-developer: SQL, APIs. Go, Java (3
of 8 each): no card; Node (2): node-and-express.
