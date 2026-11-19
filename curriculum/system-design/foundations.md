# System design: foundations
for: someone who has written small programs and can use a terminal
leads to: backend engineer, new graduate on a services team, later SRE
status: reviewed 2026-11-18 by independent agent, sources reopened
sources: DDIA contents (3, 5-7); sre-book contents (3, 4, 8); system-design-primer index (3-5, 10); MIT 6.824 (6, 7)
unverified: hours and levels are judgement

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | networking-basics | none | time one request | DNS, TCP, TLS, HTTP | 25 | 2 Explain |
| 2 | sql-and-relational | none | model and change data safely | joins, indexes, transactions | 30 | 3 Build |
| 3 | system-design-foundations | 1, 2 | defend a design with numbers | SLOs, estimates, trade-offs | 30 | 4 Design |
| 4 | caching-and-queues | 1, 2, 3 | add a cache or queue, say what breaks | caches, queues, idempotency, retries | 25 | 3 Build |
| 5 | scaling-data | 1, 2, 3 | replicate and partition, priced | replicas, failover, sharding | 30 | 4 Design |
| 6 | distributed-systems-core | 1, 2, 4, 5 | say what partitions do to data | clocks, linearizability, CAP | 20 | 2 Explain |
| 7 | consensus-and-transactions | 2, 4, 5, 6 | price consensus, leases, 2PC | Raft, fencing, 2PC, sagas | 20 | 2 Explain |
| 8 | reliability-and-observability | 1, 2, 3, 4 | watch a service, survive overload | alerts, overload, deploys | 30 | 3 Build |
| 9 | api-design | 1, 2, 3, 4 | design an API you can change later | errors, paging, versioning | 20 | 3 Build |
| 10 | system-design-interviews | 1, 2, 3, 4, 5, 9 | run a 45-minute design round aloud | scoping, estimates, deep dives | 20 | 4 Design |

## Goals
### Hold my own in design reviews as a backend developer (about 125 h)
Steps: networking-basics 2, 9-10; sql-and-relational 7-10; system-design-foundations 1-8, 10; caching-and-queues 1-3, 5-10; scaling-data 1-4, 6, 10-11; distributed-systems-core 1-2; consensus-and-transactions 6; reliability-and-observability 1, 3-4, 6-9; api-design 1, 4-5, 7-8, 10, 13.
Open with: a complaint on a service like theirs ("checkout times out at lunch") to a costed decision, one sitting; what runs out first by one division, pool size ÷ hold time (system-design-foundations 1).
Deep: system-design-foundations 4, 8; caching-and-queues 3, 8; scaling-data 3; reliability-and-observability 6.
Order: system-design-foundations 1-4; sql-and-relational 8, 10; caching-and-queues 1-3; scaling-data 1-3; caching-and-queues 5-8; networking-basics 2, 9-10; caching-and-queues 9-10; system-design-foundations 5-8; the rest in row order, system-design-foundations 10 last. With interviews within six months (about 145 h): add scaling-data 7, 9 and system-design-interviews 1-8, 14, 1-3 after system-design-foundations 4, each later one after the steps it names; a timed mock fortnightly.
Halfway: "I can say, by a number, if an index, cache, replica or queue fixes a slow page, and what it breaks."

### Pass system design interviews (about 120 h)
Steps: networking-basics 2, 8-9; sql-and-relational 5, 8-10; system-design-foundations 1-8; caching-and-queues; scaling-data 2-4, 6-7, 9-10; distributed-systems-core 1, 7; api-design 1, 4-5, 7, 10, 12; system-design-interviews.
Open with: system-design-foundations 1's decision, then aloud in 15 minutes: a round in miniature (system-design-interviews 1).
Deep: system-design-foundations 4; caching-and-queues 8; scaling-data 6; system-design-interviews 2, 6, 7.
Order: system-design-foundations 1-2; system-design-interviews 1-3; system-design-foundations 3-5; caching-and-queues 1-3; scaling-data 2-4, 6; api-design 1, 4; system-design-interviews 4-6, a first timed round; caching-and-queues 4-8; system-design-foundations 6-8; system-design-interviews 7; the rest in row order, each problem (8-13) after the steps it names; a mock (14) weekly.

### Run my own service past its first scaling problem (about 100 h)
Steps: networking-basics 2, 8-10; sql-and-relational 7-11; system-design-foundations 1-7; caching-and-queues 1-3, 5-10; scaling-data 1-4; reliability-and-observability 1-3, 5-9.
Open with: system-design-foundations 1 on their service's real complaint, the resource found by division then run out under load.
Deep: system-design-foundations 4; sql-and-relational 8; caching-and-queues 3, 8; scaling-data 3; reliability-and-observability 6.
Order: system-design-foundations 1-4; reliability-and-observability 1-3; sql-and-relational 8, 10; caching-and-queues 1-3; scaling-data 1-3; caching-and-queues 5-8; networking-basics 2, 8-10; caching-and-queues 9-10; reliability-and-observability 5-7; the rest in row order.

### Build storage or infrastructure (about 150 h)
Steps: scaling-data; distributed-systems-core; consensus-and-transactions; networking-basics 2-5, 9-10; sql-and-relational 8-9, 11; system-design-foundations 1-7; caching-and-queues 3, 5-10; reliability-and-observability 1-3, 5-8, 10.
Open with: a store like theirs ("writes stall at peak"): peak commits a second divided by what one disk sustains, a decision priced (system-design-foundations 1, scaling-data 1).
Deep: scaling-data 2, 4; distributed-systems-core 2, 5; consensus-and-transactions 2, 4.
Order: system-design-foundations 1-4; scaling-data 1-4; sql-and-relational 8-9; networking-basics 2-5, 10; distributed-systems-core 1-6, scaling-data 5 after 2; consensus-and-transactions 1-4; scaling-data 6-11; the rest in row order.

## Why this order
Rows give needs; goals interleave rows, bringing review staples (index, cache, replica, queue) early.

## Checkpoint projects
- After 3: a decision record. After 5: the design document, caches, queues and replicas in it, at 100 times the load, priced. After 8: it surviving overload.

## Short on time
Goals' steps are the floor (hours: row hours × share of steps); never skip estimates (3) or failure cases (4, 5).

## Left out on purpose
- Code-level design, pipelines, frontend: planned tracks. Security design: no card yet.
