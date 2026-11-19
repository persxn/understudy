# reliability-and-observability: targets, telemetry, overload and incidents
kind: skill
aliases: sre, monitoring, observability, slo, incident response, postmortems
needs: networking-basics, sql-and-relational, system-design-foundations, caching-and-queues
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: sre.google SRE book and workbook: contents; SLOs, monitoring, SLO alerts, overload, canarying, incidents, postmortems; builder.aws.com Builders' Library: timeouts and retries, health checks; learn.microsoft.com Azure Bulkhead, Noisy Neighbor; martinfowler.com BlueGreenDeployment; kubernetes.io rolling update; HotOS 2021 Metastable Failures; OpenTelemetry primer; github.com/giltene/wrk2; postmortems aws.amazon.com/message/41926, blog.cloudflare.com 2019-07-02, about.roblox.com/newsroom/2022/01

## Promise
Set user-side targets for the learner's service, page only on user harm, survive overload and bad deploys, run an incident and write its postmortem.

## The one idea
Reliability is a budget: decide how much failure users can bear, measure it where they feel it, spend the rest on change. Picture: a household budget. Where it breaks: overload feeds itself; the bill comes at once.

## In production
- Error budgets set release pace; on-call is paged by burn rate, not CPU.

## Teaching order
1. SLIs (system-design-foundations 3) as good events over valid events, for availability and latency; read at the load balancer or the client (failures before the server never reach its logs).
2. SLOs and the error budget: 99.9% over 30 days lets 0.1% of valid requests fail (43.2 minutes, system-design-foundations 7, only if all fail); a budget policy (spent: releases freeze); Google's planned Chubby outages.
3. The four golden signals: latency (failed requests apart; a slow error is worse), traffic, errors, saturation; black-box and white-box; p99 read from merged latency histograms.
4. Metrics, logs, traces: the question each answers; structured logs with a request id; OpenTelemetry spans and context propagation; cardinality.
5. Alerting on symptoms: burn rate; page at 14.4 over 1 hour or 6 over 6 hours, each confirmed by a window 1/12 as long; ticket at 1 over 3 days; every page actionable, with a runbook.
6. How a service falls over: slowdown, full queues, timeouts, retries multiplying (caching-and-queues 9), metastable failure; the learner's service made to do it.
7. Surviving overload: timeouts at the downstream's p99.9; deadlines passed down; retries at one layer, in a budget (caching-and-queues 9); bulkheads (a pool per dependency; tenant quotas against a noisy neighbour); "overloaded; don't retry"; shedding by criticality; client-side throttling.
8. Health checks: liveness (the process answers `200`), local checks (its own disk, memory), dependency checks; one that tests a shared dependency fails every server at once, so the load balancer must fail open.
9. Safe change: canary against control on the same SLIs, then staged rollout; rolling (a few servers at a time) or blue-green (a second full environment, the router switched over and back); config is change too (Cloudflare); rollback first; feature flags; expand and contract.
10. Load testing: closed loop (each client waits for its reply) against open loop (arrivals on a schedule, wrk2's `-R`); coordinated omission; the knee where p99 climbs; headroom.
11. Incidents: declare early (a second team, users affected, an hour unsolved); incident commander (IC), operations, communications, planning; mitigate (roll back, drain, shed) before root cause; a living incident document with a timed log.
12. Blameless postmortems: timeline, impact, contributing causes, actions with owners and dates; S3 2017, Cloudflare 2019 (a backtracking regex pushed worldwide at once; a CPU guard lost in a refactor), Roblox 2021 (73 hours; Consul overloaded, telemetry depending on it).

## Judged by
- [1-2] Is each SLO computed from users' requests, with a window and a budget policy?
- [3] Are latencies percentiles from merged histograms, errors included?
- [5] Would each page wake someone for user harm they can act on now, with a runbook?
- [6-7] At twice the tested peak, does the service shed load, keep admitted requests in SLO and recover alone?
- [9] Can any change, config included, be rolled back in minutes, and was that tried?
- [12] Does the postmortem have a timeline, contributing causes without blame, and actions with owners?

## Step notes
### 1
Need: Our availability graph says 99% for the week, so why are users angry about one afternoon?
Show: a generated week's log: 12.1 million requests, 3% 404s, latency log-normal around 80 ms; one hour six times slower, 5% 503s. Good: below 500 and under 300 ms; valid: not a 404. Mean latency 93 ms (91 without that hour); week SLI 99.04%, over a 99% target; the bad hour 16.3% good.
Explain: An SLI is good events over valid events, counted where users feel them; a week's ratio and a mean hide an hour that failed most users.
Try: build: availability and latency SLIs per hour from their access log; explain: which failures their server's log can never hold.
### 2
Need: "Three nines" sounds great, but what does it let us break, and what then?
Show: 50 requests a second for 30 days: 129,600,000 valid requests; at 99.9%, 129,600 may fail. Ten minutes of total outage spend 23.1%; an hour at 5% errors 6.9%; a day at 0.2%, which no graph shows, 6.7%.
Explain: The error budget is the failures the target allows in its window, counted in requests, so a slow leak spends it like an outage; the budget policy says what stops once it is spent.
Try: apply: their busiest endpoint's budget in requests, and what their worst hour spent; decide: their budget policy, agreed with whoever owns releases.
### 3
Need: Every host's p99 looks fine, so why does the fleet feel slow?
Show: log-normal latencies: host A, 90,000 requests around 50 ms, p99 100 ms; host B, 10,000 around 400 ms (a bad disk), p99 805 ms. Average of the p99s: 453 ms; true p99: 587 ms; summed bucket counts put it in 500-1000 ms.
Explain: Percentiles do not average: hosts export counts per latency bucket, the counts are summed, the percentile is read from the sum.
Try: fix: a fleet panel averaging per-host p99s; predict: their p99 with fast 500s counted as successes.
### 4
Need: We already have logs; why does everyone say we need metrics and traces too?
Show: 1,000,000 generated requests labelled method (4), route (30), status (6), 12 latency buckets: 8,508 series; add `user_id` (of 50,000): 2,021,808.
Explain: A metric counts per label set (how often); a structured log records one event's fields (what happened to this request); a trace joins one request's spans across services by a propagated context (where the time went); each label set is another series.
Try: build: a request id in every log line and on one outgoing call; predict: the series a planned label adds, then count.
### 5
Need: Our alert pages on CPU over 80% all night; what should wake someone instead?
Show: 30 simulated days, 50 requests a second: 20 lone minutes at 8% errors, a 30-minute incident at 10% (burn rate 100), a 12-hour leak at 0.7% (burn 7). "5-minute error rate over 1%": 21 pages, the incident in 1 minute, the leak (11.7% of the budget) never. Burn-rate rules: 2 pages, after 9 minutes and about 5 hours.
Explain: Burn rate is how fast the budget goes (1 spends it exactly over the window); 14.4 for an hour spends 2%, 6 for six hours 5%: real harm.
Try: build: both page rules on their SLI with a runbook link; predict: minutes to page at burn rate 1,000.
### 6
Need: The spike ended twenty minutes ago; why is the service still down?
Show: a 30-line queue: capacity 100 a second, load 80, a 10-s spike at 200, callers waiting 2 s, retrying 3 times. Answered in time per 10 s: 800, 300, then 0 for good; no retries: 0 for 40 s, then back. 1,000 clients at a server down 10 s, then serving 100 a second, retrying every 1 s: waves, 60,500 attempts, done at 109 s; jittered exponential backoff: about 6,100, 45 s.
Explain: Timed-out requests stay queued, served for nobody, while retries add more; once retries alone exceed capacity, the trigger's end no longer helps (metastable).
Try: build: their service pushed past capacity with its real retries; predict: whether it recovers when load returns.
### 7
Need: Which knob stops that: shorter timeouts, fewer retries, or turning users away?
Show: step 6 rerun: a 10% retry budget alone, 0 for 110 s (no retries: 40); requests whose caller left dropped (a deadline passed down), recovered; queue capped at 1 s of work, 800 at once. Node over HTTP, 1-s caller, server waiting 5 s on a 3-s dependency: 0 of 50 answered, about 150 request-seconds held; at 700 ms, 50 fast 504s, 36.
Explain: Bound the work: deadlines so nobody serves a caller who left, a queue that refuses early (backpressure), retries in a budget, each timeout below its caller's.
Try: build: their service through step 6's fault until it recovers alone; fix: a timeout outliving its caller's.
### 8
Need: Shouldn't a health check test the database too, to be thorough?
Show: 10 servers checked every 5 s, out after 2 failures, back after 3 passes; the shared database down 10 s; 40% of 100 requests a second need it. Liveness only: 400 failed. Checks querying the database: fleet out, 15 s with no server, 1,700 failed. Failing open: 400.
Explain: A check on a shared dependency fails everywhere at once, so the load balancer drops the fleet for longer than the blip; failing open sends to all when all fail.
Try: decide: which of their checks are liveness, local or dependency; predict: their settings against a 10-s database blip.
### 9
Need: Tests passed and the deploy still took the site down; how do others ship safely?
Show: 100 requests a second; a release lifting errors from 0.1% to 2%. All at once, paged by the 1-hour burn rule after 43 minutes, rolled back in 10: 6,039 extra failures. A 1% canary for 20 minutes, halted past 3 times control's error rate: halted in 200 of 200 runs, 23 extra; good releases halted about 1 in 100.
Explain: A canary compares a slice of real traffic with the rest on the same SLIs, so a bad release hurts few; flags and expand-and-contract let old and new run together.
Try: build: a canary stage and halt rule in their deploy; fix: a migration dropping a column the old version reads.
### 10
Need: Our load test says p99 is 1 ms, yet production is slow: is the tester lying?
Show: a server answering in 1 ms, frozen 1 s in every 10, tested 100 s. Closed loop (one client waiting each reply): 90,004 requests, p99 1.0 ms. Open loop, 1,000 a second timed from each scheduled send: p99 901 ms.
Explain: A closed-loop client stops sending while the server stalls, so a stall is one slow sample, not the thousand who would have waited (coordinated omission); headroom is from peak to the knee.
Try: apply: an open-loop run (wrk2's `-R`) of their service, stepped to the knee; predict: what their tool reports for a 1-s pause.
### 11
Need: Five people are typing fixes into one chat mid-outage: who does what?
Show: the SRE book's "Managing Incidents", unmanaged: paged at 2 p.m., a rollback that does not help, executives wanting an ETA, an engineer's unannounced change, servers restarting and dying; then managed: roles, a living document, a 6 p.m. handoff.
Explain: The commander holds the state and hands out work; only operations changes production; communications updates everyone; mitigation before root cause.
Try: build: a game day with the four roles and a timed log; decide: by the three questions, which recent outages were incidents.
### 12
Need: How do we write up an outage without hunting whoever typed the command?
Show: AWS's S3 summary as a timeline: 9:37 a.m. PST one mistyped input removes far more servers; subsystems unrestarted for years restart; the status page stuck until 11:37 (it ran on S3); GET returning from 12:26, all by 1:54 p.m. Actions: slower removal, a minimum-capacity guard, cells.
Explain: Blameless asks why the system let a reasonable act do harm; causes are several; actions are owned, dated, and change the system.
Try: build: a postmortem of their last outage passing "Judged by"; explain: why Cloudflare's kill switch sat behind a down login.

## Believable numbers
- [5] SRE workbook, Alerting on SLOs (opened 2026-11-19): at 99.9%, burn rate 1,000 empties the 30-day budget in 43 minutes; a 0.1% threshold over 10 minutes "could receive up to 144 alerts per day" yet meet the SLO.
- [7] A timeout at the downstream's p99.9 fails 0.1% of healthy calls (Builders' Library); client-side throttling starts once requests exceed twice the accepts (SRE book, Handling Overload).

## Go deep, leave for later
- Deep steps: 2, 5, 6, 7 (the budget and the alert that spends it; overload as one story: how retries hold a service down, then the timeouts, deadlines and shedding that let it recover).
- Later: toil, on-call load, backups and restore drills, capacity planning, chaos platforms, multi-region recovery.

## Never omit
- Every fix proved by its test or fault, rerun.
- Look up when planned: the learner's telemetry, alerting and deploy tools; the platform's probe names (Kubernetes liveness and readiness).

## Wrong beliefs
- [1] "Server metrics show what users get" (requests failing before the server never appear).
- [2] "99.9% means 43 minutes of downtime a month" (only for total outages; a request SLO counts failed requests).
- [3] "Average the hosts' p99s for the fleet's" (percentiles do not average; merge the buckets).
- [5] "Page on any error spike, so nothing is missed" (in step 5's simulation a 1% threshold paged 20 times for harmless minutes and missed a leak that spent 11.7% of the budget).
- [6] "When the trigger goes, the service recovers" (retries hold it down until load falls far lower: in the HotOS example, below 150 of 300 QPS capacity).
- [7] "A longer timeout is safer" (it ties up threads after the caller gave up).
- [8] "A deep health check is more thorough" (a shared database blip fails every server at once).
- [10] "Low load-test latency means fast" (a closed-loop tester sends less while the server stalls).
- [12] "A postmortem finds the root cause and the culprit" (causes are several; blame hides facts).

## Failures to diagnose
- [5] A page storm over one dead host; an outage with no page.
- [6] Still down after the spike ended: retries.
- [7] Work finishing after its caller gave up: a timeout longer than the caller's.
- [8] The whole fleet removed when the database blinks.
- [9] A rollback failing on a migration.

## Practice and project
Guided: SLIs for the learner's endpoints. Alone: each public postmortem's causes mapped onto the learner's. Project: SLOs, dashboard and burn-rate alerts on the learner's service; it falls over under retries and is fixed; a game day with roles; finish line: before and after graphs, an alert fired only by the fault, a postmortem passing "Judged by".

## Mastery ladder
- Use: write SLOs and a burn-rate alert for one service.
- Explain: show a friend, on their own graphs, how retries kept it down.
- Build: the project above.
- Design: set timeouts, retries, shedding and health checks for three chained services; defend each.

## Words to own
[1] good event, valid event; [2] error budget, budget policy; [3] golden signals, saturation, black-box monitoring, histogram; [4] (metric), structured log, trace, span, context propagation, cardinality; [5] burn rate, page, runbook; [6] cascading failure, metastable failure; [7] deadline propagation, load shedding, client-side throttling, bulkhead, noisy neighbour, (backpressure); [8] health check, liveness check, dependency check, fail open; [9] canary, staged rollout, (rolling deployment), (blue-green deployment), rollback, feature flag, expand and contract; [10] open-loop load, coordinated omission, headroom; [11] incident commander, mitigation; [12] blameless, contributing cause, action item
