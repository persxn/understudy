# system-design-foundations: reasoning about a design from requirements and numbers
kind: skill
aliases: system design, back-of-the-envelope estimates, design review
needs: networking-basics, sql-and-relational
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: sre.google workbook/non-abstract-design (stages, disks, machines); sre-book service-level-objectives, availability-table;
  cacm.acm.org the-tail-at-scale (63%, hedging); wikipedia Little's_law, M/M/1_queue; HikariCP wiki About-Pool-Sizing; industrialempathy.com
  design-docs-at-google (length, alternatives, non-goals); AWS Well-Architected pillars; system-design-primer (outline);
  github.com/brettwooldridge/HikariCP and node-postgres.com/apis/pool (pool defaults, read 2026-11-19);
  postgresql.org/docs/16 runtime-config-connection (max_connections); gist.github.com/jboner/2841832 (round trips, about 2012)

## Promise
Turn a vague product into measurable requirements and numbers, find what runs out first, choose building blocks, defend trade-offs, say how it fails, read designs critically.

## The one idea
A design is choices forced by numbers: how many requests, how much data, how fast, how stale, how often down. Picture: a kitchen planned for the rush. Where it breaks: the rush can grow a hundredfold; parts fail partly, silently.

## In production
- Designs are documents reviewed before code; reviewers ask for numbers, cost, and what happens when each part fails.

## Teaching order
1. The whole practice once, small: one feature of the learner's own service in an hour: one functional and one numbered requirement, peak requests a second, a sketch, the resource that runs out first by one division (a pool of 10 held 3 s carries 3.3 a second), two options, a written decision.
2. Estimating: daily active users (DAU) × actions ÷ 86,400 = average requests per second (QPS); peak as a measured multiple; read/write ratio; bytes × records a year × replicas; monthly cost from prices looked up; every assumption written.
3. Latency as a distribution, and requirements that can be checked: p50, p99, p99.9 from a histogram, never the average; fan-out to 100 servers turns a 1% tail into 63%; hedged requests; each non-functional requirement as an SLO (SLI, target, window); an SLA adds penalties.
4. Throughput and running out: Little's law (in flight = arrival rate × time held), so N connections held T seconds serve at most N/T a second; M/M/1 time in system = service time ÷ (1 − utilisation); the bottleneck measured running out in the learner's service.
5. Building blocks: load balancer, stateless servers, database (relational, key-value, document, wide-column, chosen by access pattern), object storage, CDN, cache, queue; each one's limit and failure mode; monolith against microservices.
6. Scaling the stateless tier: vertical first, then horizontal; sessions out of process memory (database or Redis), not sticky sessions; health checks and service discovery; autoscaling on a measured signal; single points of failure; redundancy, active-passive or active-active.
7. Availability and durability: nines as downtime (99.9%: 8.76 hours a year, 43.2 minutes a month); three serial dependencies at 99.9% give 99.7%; copies help only if they fail apart: failure domains (host, availability zone, region), correlated failure, blast radius; durable against available; graceful degradation.
8. A trade-off as a decision: two or three options, each with what it carries, costs and how it fails, in numbers; the choice and what would reverse it, in a decision record (ADR).
9. Reading a design: the SRE workbook's non-abstract design (possible, better, feasible, resilient, with disk and machine counts), then a public postmortem; each read against the learner's own.
10. A design document: context and scope, goals and non-goals, the design, alternatives considered, cross-cutting concerns (security, privacy, observability); a review by the AWS Well-Architected pillars.

## Judged by
- [3] Each requirement measurable: an SLI, a target, a window, not "fast".
- [2] Every number has a written assumption and unit; peak sizes each part; the monthly cost is stated.
- [3] Latency given as percentiles; fan-out per request counted.
- [1,4] The bottleneck is named with arithmetic (size ÷ hold time), and what happens past it.
- [5-7] Each box and shared dependency: its failure, what users see, how it is noticed, its blast radius.
- [7] Every call to another service has a timeout and a retry rule.
- [8,10] Two alternatives rejected with reasons; non-goals stated.
- [8] Each piece of data has one home of truth and a stated allowed staleness.
- What changes at ten times the load is stated.

## Step notes
### 1
Need: My feature works on my laptop; what gives out first in production, and at how many orders?
Show: asyncio, 28 lines: a semaphore of 10 "connections"; an order arrives every 0.2 s for 60 s, holds one for 20 ms of SQL and a 3 s payment call; completions counted from second 10. Most predict "fine". Measured: 3.30 a second (10 ÷ 3.02 = 3.31); at 60 s, 100 orders wait for a connection, 1.7 more each second, so the next waits 30 s. Provider at 6 s: 1.6, 200 waiting. PostgreSQL 16, `pgbench` of `SELECT pg_sleep(0.3)`, 10 and 20 clients: 33.2 and 66.4 a second.
Explain: A connection held T seconds serves 1/T requests a second; a pool of N, N/T, whatever the CPU does; beyond, requests queue.
Try: apply: each pool in their service (database, HTTP client, workers), size ÷ hold time, the first to run out named; fix: a connection held across an outside call, divided before and after.
### 2
Need: Product says "a million users"; how many requests a second is that, and is it a lot?
Show: 1,000,000 DAU × 20 actions ÷ 86,400 = 231 a second; peak at 3×, 700. Most expect "a cluster". One PostgreSQL 16 on 2 vCPUs (`pgbench -S`): 30,000 to 90,000 primary-key reads a second; a 1M-row scan 50-100 ms, 10 to 20 a second a core.
Explain: Load is users × actions ÷ seconds in a day × a measured peak factor; whether it is a lot depends on what one request costs the busiest part.
Try: apply: their peak QPS and yearly storage, one assumption a line; predict: how many of their slowest query a core carries, from `EXPLAIN ANALYZE`, then load-test it.
### 3
Need: The dashboard says 63 ms on average, yet users say pages hang; which is true?
Show: 100,000 generated latencies, 98% near 40 ms, 2% at 0.8-1.5 s. Mean 63, p50 40, p99 1,154 ms: almost no request takes the mean. Pages calling 1, 10, 100 servers: 1.0%, 9.4%, 63.3% wait past the p99. SLO "99% under 300 ms": SLI 97.97%, missed, while the mean looks fine.
Explain: Users meet the slowest call behind each page; a requirement is checkable only as a share of good requests (SLI) against a target over a window (SLO).
Try: build: p50, p99, p99.9 and the SLI from their own access log; apply: each non-functional requirement (latency, throughput, availability, durability, consistency, cost) as SLI, target, window.
### 4
Need: The database sits at 5% CPU, yet requests time out waiting for a connection; what is full?
Show: step 1's `pgbench -c 10` (ceiling 33 a second), arrivals random (`-R`): 20 a second, mean 321 ms; 30, 465 ms; 40, about 2 s and climbing, the machine 2% busy. A simulated server (14 lines, 10 ms, random arrivals): busy 50%, 2.0× service time in the system; 80%, 5.0×; 90%, 9.5-10.8× (formula 2, 5, 10); 99%: 68× to 122× by seed (formula 100): it never settles.
Explain: What is held while waiting fills first: in flight = arrival rate × hold time (100 a second held 10 s: 1,000); past the pool the queue grows without bound, and before it waiting grows as 1 ÷ (1 − utilisation).
Try: predict: their pool's wait at 80% and 95% busy, then load-test; fix: time-outs while the database idles, until the pool's wait is near zero.
### 5
Need: Ten app servers and one PostgreSQL: which box refuses first, and with what message?
Show: PostgreSQL 16: `max_connections` 100, 3 kept for superusers. 98 `pgbench` clients as an ordinary role: `FATAL: remaining connection slots are reserved for roles with the SUPERUSER attribute`; as superuser, the 101st: `FATAL: sorry, too many clients already`. Ten app servers with pools of 10 fill it.
Explain: Every block (balancer, server, database, object store, cache, queue) has a number that ends it and a way it fails; read a design by finding both.
Try: build: their service's blocks with limit, failure and how it is noticed; decide: monolith or services for their team, for deploys, not scale.
### 6
Need: I added a second server and users keep getting logged out; why?
Show: two copies of a 25-line `http.server` app, sessions in a dict, round robin: after login, 50 of 100 requests saw "LOGGED OUT". Sessions in a store both share (a dict standing in for Redis): 0 of 100.
Explain: Copies can be added freely only if they keep nothing between requests; the state moves to a shared store: a new part to size, a new single point of failure.
Try: fix: their service as two copies behind a balancer until a login survives every request; predict: what limits at ten copies (step 5's arithmetic).
### 7
Need: Two copies of everything gives four nines, surely?
Show: a year of minutes, simulated: three dependencies at 99.9%, all needed: 99.70% (26 h down). Two copies at 99% in separate zones: 99.99% (52 min); the same copies sharing a zone up 99.5%: 99.49% (44 h).
Explain: Dependencies in series multiply; copies add nines only if they fail apart, so what they share (zone, deploy, config) sets the real figure.
Try: apply: their call chain's availabilities multiplied; decide: what users see when one shared dependency is down, and how it is noticed.
### 8
Need: Both options work; how do I choose so the review is not about taste?
Show: step 1, provider at 6 s, 5 orders a second: pool 10 carries 1.6. A, pool 30: 4.98, exactly its limit (30 ÷ 6.02), so 6.1 s breaks it, and three instances fill PostgreSQL's 97. B, connection released before the call: 4.98 with the pool 1% busy, but 30 calls open at the provider (5 × 6); a crash leaves orders "pending" for a sweeper.
Explain: A decision states each option's numbers, cost and way of failing, the choice, and the measurement that would reverse it.
Try: build: an ADR for one choice in their service, two options rejected with numbers; decide: A or B if the provider allows 20 open calls.
### 9
Need: What does a real design review look like, numbers and all?
Show: the SRE workbook's non-abstract design: 500,000 searches and 10,000 clicks a second; one machine would need about 2,500 disks; the end, 64 machines a datacentre. Most call the naive pass wasted; the author: "this step hasn't been a waste of time".
Explain: A design is read by redoing its arithmetic: each stage fits the numbers or is ruled out by one.
Try: explain: one workbook number redone, with the requirement it serves; apply: a public postmortem's cause looked for in their own design.
### 10
Need: How much do I write before coding, and what will reviewers look for?
Show: "Design docs at Google": 10-20 pages for a larger project, 1-3 for small work; "alternatives considered" among the most important parts; a non-goal is a reasonable goal not pursued (ACID compliance), never "shouldn't crash".
Explain: The doc makes trade-offs reviewable while changing course costs only paper; alternatives and non-goals carry it.
Try: build: their service's design document, every Judged-by line checkable in it; apply: a review pillar by pillar (Well-Architected), each finding with a number.

## Believable numbers
- PostgreSQL 16, 2 vCPUs, runs on two days (2026-11): a primary-key read in 1M rows 0.06-0.09 ms; 30,000 to 90,000 a second (`pgbench -S`); 1,600 to 4,300 small write transactions (`pgbench -N`, 8 clients); a scan of the 1M rows (130 MB, cached) 50-100 ms. Machines differ threefold: give orders, not digits.
- [1,4-5] Look up for the learner's stack: the pool's default size (HikariCP and node-postgres: 10; a wait for a free one: HikariCP 30 s, node-postgres forever; read 2026-11-19) and the server's `max_connections` (100 on PostgreSQL 16 here, 3 reserved for superusers).
- [2-3] Round trips: same datacentre 0.5 ms, California to the Netherlands and back 150 ms (Dean and Norvig, about 2012; today's looked up); loopback to Redis here 8-20 µs.

## Go deep, leave for later
- Deep steps: 3, 4, 8 (measurable requirements and the tail users feel; what runs out first, by Little's law; a trade-off defended with measured numbers).
- Later: caching-and-queues, scaling-data, reliability-and-observability, api-design; security design.

## Never omit
- [1,4] A resource seen to run out in the learner's own system: its limit predicted by arithmetic, then measured before any fix.
- A real public design or postmortem in every chapter, beside the learner's own.
- Look up when planned: today's latency orders of magnitude; the learner's cloud prices.

## Wrong beliefs
- [1] "Our traffic is small, so capacity can wait" (a pool of 10 held through a 3 s outside call carries 3.3 orders a second).
- [3] "Average latency shows how users feel" (users meet the tail, and fan-out makes it common).
- [4] "A bigger connection pool fixes pool exhaustion" (it moves the queue into the database; shorten the hold: HikariCP cites Oracle cutting 2,048 connections to 96, response time from about 100 ms to 2 ms).
- [4] "At 80% busy there is 20% to spare" (in the simplest queue a request already takes five times its service time; near 100% the wait has no bound).
- [4,6] "More servers always add capacity" (only while the work splits; then a shared database or lock is the limit).
- [5] "Microservices make a system scale" (a stateless monolith scales out too; services let teams deploy apart, and add network calls).
- [7] "Redundancy makes failure impossible" (a bad deploy or shared dependency takes out every copy).
- [8] "A design has one right answer" (it has trade-offs fitting requirements).

## Failures to diagnose
- [2-3] A target with no SLI, a design with no numbers: nothing can be checked or sized.
- [1,4] Requests timing out while the database idles: connections held across a slow outside call.
- [5] `FATAL: sorry, too many clients already`: app instances × pool size passed `max_connections`.
- [6] Users logged out at random after scaling out: sessions kept in one server's memory.
- [6-7] A single point of failure in a shared dependency: one database, zone or region.
- [7] One slow dependency stopping everything: no timeout, every worker waits on it.

## Practice and project
Guided: three estimates against worked answers; alone: a public design's numbers on a page. Project: a design document for the learner's service; finish line: the first resource to run out found by a load test, matching the arithmetic; every Judged-by test passed.

## Mastery ladder
- Use: estimate peak requests a second and yearly storage for a stated product.
- Explain: tell a friend why the slowest 1% of calls rules a page calling 100 services.
- Build: the design document above.
- Design: defend it in a review against hard questions on load, failure, cost.

## Words to own
[1] functional requirement, non-functional requirement, bottleneck, (connection pool); [2] DAU, QPS, peak load,
read/write ratio, back-of-the-envelope estimate; [3] latency percentile, tail latency, fan-out, SLI, SLO,
(hedged request), (SLA); [4] throughput, Little's law, utilisation, pool exhaustion; [5] stateless service,
key-value store, failure mode, monolith, microservice, (object storage), (document store), (wide-column store);
[6] horizontal scaling, vertical scaling, sticky session, single point of failure, redundancy, (service
discovery), (autoscaling), (active-passive), (active-active); [7] availability, nines, durability, failure
domain, correlated failure, (availability zone), (blast radius), (graceful degradation); [8] trade-off, decision
record; [9] postmortem; [10] design document, non-goal
