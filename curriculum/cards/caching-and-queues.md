# caching-and-queues: caches, queues and retries, and how they break
kind: system
aliases: caching, message queues, retries, redis, memcached
needs: networking-basics, sql-and-relational, system-design-foundations
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: usenix.org NSDI 2013 Scaling Memcache at Facebook (look-aside, delete because idempotent, leases: 10 s,
  17K/s to 1.3K/s); builder.aws.com Builders' Library (retries with jitter; queue backlogs: 300 minutes, message
  age); sre.google/sre-book/addressing-cascading-failures (retry budgets, multiplying retries);
  aws.amazon.com/message/12721 (December 2021); gist.github.com/jboner/2841832 (Dean and Norvig, about 2012);
  Azure architecture patterns catalogue and system-design-primer cache and asynchronism parts (outlines);
  kafka.apache.org/intro (events kept after reading, order per partition); docs.confluent.io kafka/design/consumer-design (an offset per group and partition)

## Promise
Add a cache or a queue to a real service, measure the gain, show how it breaks: stale data, stampedes, duplicates, retry storms, backlogs.

## The one idea
Both buy speed or calm by letting data or work wait away from its home for a while; the bugs live in "for a while". Picture: a timetable copied to a notice board; a deli's ticket roll. Where it breaks: nobody updates the copy; the line grows while the counter looks calm.

## In production
- A look-aside cache sits before the database, which stays the truth; Facebook deletes on write, as deletes are idempotent.
- Queues take slow work out of the request; retries without backoff turn blips into outages (AWS, December 2021).

## Teaching order
1. A slow endpoint made fast: p50, p99 and database queries measured, cache-aside added, measured again; hit ratio; then one update read back stale.
2. Where caches live: browser and CDN (`Cache-Control`, networking-basics 8), in-process (fastest, one copy per server, each stale in its own way), shared (Redis, Memcached: one network round trip, one copy).
3. Keeping a cache honest: expiry (a TTL), delete on write, write-through, write-back, the race that leaves a stale value; leases.
4. Eviction and sizing: what goes when memory is full (LRU, LFU, the store's eviction policy setting, looked up); the working set; hit ratio plotted against cache size, flat once the working set fits.
5. When caches hurt: a stampede on a hot key, a cold start after `FLUSHALL`, the cache as a hard dependency; request coalescing, leases, warming.
6. Queues: producer, broker, consumer; load levelling; competing consumers; publish-subscribe (pub/sub: every subscriber gets each message). A queue (RabbitMQ, SQS) deletes a message once acknowledged; a log (Kafka) keeps it, ordered only within a partition, each consumer group at its own offset.
7. Delivery promises: at-most-once (`ack` before work), at-least-once (`ack` after work); unacknowledged messages redelivered (SQS after the visibility timeout); duplicates, ordering; exactly-once as end-to-end work.
8. Idempotency (done twice, the effect of once): an idempotency key under a `UNIQUE` constraint (sql-and-relational 9), stored in the same transaction as the effect; a payment or email made safe to repeat.
9. Retries: a timeout on every call; capped exponential backoff with jitter; retries at one layer only; a retry budget (the SRE book's example: 60 retries a minute per process); circuit breakers that stop calling a failing service; after a set number of attempts, poison messages moved to a dead-letter queue (DLQ).
10. Overload: arrivals beating service (Little's law, system-design-foundations 4); a backlog drains only at spare capacity; consumer lag and alarms on message age; backpressure; rate limits at the entrance (api-design 10); AWS's 2021 event traced.

## Numbers and traces
- [2] Memory 100 ns against a same-datacentre round trip 0.5 ms (Dean and Norvig, about 2012; today's looked up): a shared cache costs a network call, thousands of times an in-process read. Measured here: a Python dict `get` 30-130 ns, a Redis `GET` over loopback 8-20 µs.
- [10] A spike unnoticed for about 30 minutes that queues 10 times what consumers can do takes about 300 minutes to work through (Builders' Library); a one-hour outage needs double capacity for another hour. Simulated here: at 90% busy, a 10-minute consumer stop takes 90 minutes to drain.
- [1,3] Hit: `get` returns it. Miss: `get` empty, read the database, `set` with expiry. Write: update the database, delete the key.
- [5] Stampede: a hot key expires and every request queries the database; with a lease (one token per key per 10 seconds) one fetches and the rest wait: Facebook's peak fell from 17K to 1.3K queries a second (NSDI 2013).
- [7-8] Delivery: publish, store, process, `ack`; a crash before `ack` redelivers; a stored idempotency key stops the second effect.

## Step notes
### 1
Need: The page takes 50 ms and the database is busy; if I put a cache in front, what do I win and what do I lose?
Show: 25 lines with Python's `sqlite3`: a report scanning 1M rows, 300 requests over 23 customers. No cache: p50 41 ms, p99 109 ms, 300 queries. Cache-aside, 30 s expiry: p50 0.2 µs, but p99 still 78 ms (a miss), 23 queries, hit ratio 92%. Then update one customer: the database says 1,066,265, the cache still 52,265.
Explain: Cache-aside reads the cache, on a miss reads the database and stores the answer with an expiry; the median collapses, the p99 stays a miss until hits pass 99%, and every hit may be stale.
Try: build: cache-aside on their slowest read, hit ratio, p50, p99 and queries before and after; predict: the p99 at their hit ratio, then explain the run.
### 2
Need: Why run Redis when a dict in my process is faster?
Show: the same `GET` 20,000 times: a Python dict 30-130 ns; Redis on the same machine over a raw socket (15 lines) 8-20 µs: hundreds of times slower (three runs), before any datacentre hop (0.5 ms, Dean and Norvig).
Explain: An in-process cache is a memory read but one copy per server, each stale in its own way; a shared cache is one copy everyone sees, paid for with a round trip.
Try: predict: how many copies of one value 8 servers with in-process caches hold, and how long until all agree after a write; apply: `Cache-Control` on one response, seen served from the browser's cache in its network tab.
### 3
Need: I delete the key after every update; how can users still see the old price?
Show: every interleaving (38 lines) of a reader (miss, read database, set) and a writer (write database, fix cache): update leaves a stale value in 1 of 10, delete also 1 of 10 (read before the write, set after the delete); delete with a lease (token given on the miss, revoked by the delete, a set with a revoked token refused, as at Facebook): 0. Two writers, no reader: update 2 of 6, delete 0.
Explain: Delete beats update because two writers' sets can land out of order and deletes cannot; a lease refuses the set of a reader whose miss came before the delete.
Try: predict: which interleaving is stale, then check with the program; fix: their cache-aside with a lease or a version checked on set, rerun to 0.
### 4
Need: How big should the cache be, and why did doubling it change nothing?
Show: an LRU (`OrderedDict`, 20 lines), 300,000 requests. 10,000 equally hot keys: 10%, 49%, 88% at 1k, 5k, 9k slots, then flat at 97% from 10k (the rest are first reads). 100,000 Zipf keys (key r asked in proportion to 1/r): 1k slots give 50%, 50k only 84%.
Explain: Hit ratio climbs until the working set fits, then stops; under skew a small cache takes most hits and the long tail costs memory for little.
Try: apply: their own logged keys replayed against 4 sizes, plotted; decide: their store's eviction policy, from the curve.
### 5
Need: Our hit ratio is 99%; why did the database fall over at midnight?
Show: a hot key expires; 200 threads want it; loading takes 50 ms (25 lines). All at once: 200 database queries; 1 ms apart: 46-53; 5 ms apart: 10-12; one fetch per key (a lock, look again inside): 1. Duplicates ≈ arrival rate × load time. Facebook's leases: peak 17K to 1.3K queries a second (NSDI 2013).
Explain: Each request that misses during the refill refills too; coalescing lets one fetch while the rest wait.
Try: predict: queries when their hottest key expires at peak rate, by multiplication, then measure; fix: a `FLUSHALL` on a test copy that swamps their database, until warming or coalescing survives it.
### 6
Need: Is a queue just a list, and how do RabbitMQ and Kafka differ?
Show: a queue in PostgreSQL 16: `DELETE ... WHERE id = (SELECT id ... FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING`, 4 `pgbench` clients: 2,000 jobs split 498/500/496/506, none taken twice. Without `SKIP LOCKED` none is taken twice either, but consumers queue on one row: 2,100 against 3,400 tries a second. A log keeps messages: Kafka's "events are not deleted after consumption", order only within a partition (kafka.apache.org/intro); each group keeps its own offset (Confluent, consumer design).
Explain: A queue gives each message to one competing consumer and forgets it once acknowledged; a log keeps every message and lets each group keep its own place.
Try: build: the `SKIP LOCKED` queue for their slowest side effect, no job run twice or lost; decide: queue or log for one stream of theirs (a second reader later? replay?).
### 7
Need: If the consumer dies halfway, is the message lost or done twice?
Show: PostgreSQL 16, a message table with a 1 s visibility timeout, an 11-line `psql` consumer: take message 7, insert the payment, crash before the `DELETE` that acknowledges. 1.1 s later another consumer takes message 7 and finishes: 2 payment rows for one message.
Explain: The broker knows a message is done only when acknowledged: after the work, a crash means redelivery (at-least-once); before it, loss (at-most-once).
Try: predict: rows after a crash before the `ack` and after a crash before the insert, then run both; explain: why a visibility timeout shorter than the slowest work duplicates with no crash at all.
### 8
Need: Then how does a payment that may arrive twice happen once?
Show: step 7 rerun with `INSERT ... ON CONFLICT DO NOTHING` into a table whose message id is `UNIQUE`: 1 row. The usual first try, `INSERT ... WHERE NOT EXISTS (SELECT ...)`, from 8 `pgbench` clients over 5,000 keys: 12 keys charged twice in 16,000 attempts; with `UNIQUE`: 0.
Explain: An idempotency key is a unique record of "done", written in the effect's transaction, so the database refuses a second effect; a check before inserting races.
Try: fix: their consumer until a twice-delivered message has one effect; decide: for an effect outside the database (an email), where the key lives and what a crash between send and record does.
### 9
Need: Retries should make calls more reliable; why did adding them make the outage worse?
Show: a counting program (36 lines): web, service and data access each try 4 times against a database that is down: 64 database calls for one request; retries at the top only: 4; a 10% retry budget over 1,000 requests: 1,100 calls, not 4,000. 1,000 clients failing together, backing off 100, 200, 400 ms without jitter: all 1,000 retry in the same 10 ms; with full jitter, 161-165 at most.
Explain: Retries at each layer multiply and synchronised ones arrive as a wave: retry at one layer, within a budget, with jitter.
Try: apply: attempts per layer in their stack (client defaults looked up), multiplied; fix: a poison message looping until moved to a dead-letter queue after N tries.
### 10
Need: The outage lasted ten minutes; why are we still behind an hour later?
Show: simulated (25 lines): consumers do 100 a second, 90 arrive; consumers stop 10 minutes: 54,000 waiting, caught up 90 minutes later (spare: 10 a second). Clients resend any message not done in 60 s: arrivals double, the backlog passes 1.7 million, not caught up in 6 hours.
Explain: A backlog drains at the spare capacity, not the full one, and clients that give up and resend add load just when none is spare, so overload outlives its trigger (AWS, December 2021).
Try: predict: their catch-up time after a 15-minute consumer stop, from arrival rate and capacity, then check against lag; build: an alarm on the oldest message's age, its threshold from their clients' timeout.

## Go deep, leave for later
- Deep steps: 3, 8, 9, 10 (invalidation races; at-least-once made safe by idempotency; retries and backlogs as feedback loops: where caches and queues cause outages).
- Later: load shedding, cascading failure (reliability-and-observability); outbox, sagas (consensus-and-transactions); stream processing, event sourcing, CQRS (data-intensive-systems, planned).

## Never omit
- [7-8] Every consumer fed one message twice.
- [9] Every retry loop limited in attempts, with backoff and jitter.
- Look up when planned: the broker's delivery guarantees.

## Wrong beliefs
- [1,5] "A cache only makes things faster" (it adds stale reads, a failure, a spike when emptied).
- [3] "Updating the cache on each write keeps it right" (racing writers can leave the older value; deleting narrows the race; leases or versions close it).
- [8] "Checking first whether it was done makes a consumer idempotent" (two can pass the check together: 12 keys charged twice in 16,000 concurrent attempts on PostgreSQL 16 here; a `UNIQUE` constraint refuses the second).
- [7] "The queue processes each message exactly once" (a message can arrive twice, or vanish if acknowledged early; consumers must be idempotent).
- [9] "Retrying makes calls more reliable" (it rides out brief faults; many retrying clients keep an overloaded service down).
- [10] "A growing queue is fine because nothing is lost" (old work may be useless when it finally runs).

## Failures to diagnose
- [3] A stale value after an update: a reader that missed before the write set the old value after its delete.
- [5] A database swamped after a cache flush: every miss reaches it at once.
- [7-8] A duplicate email: the consumer crashed after sending, before acknowledging.
- [9] A poison message: it fails every time, looping until moved to a dead-letter queue.
- [9] A retry storm: three layers making four attempts each: one request becomes 64 database calls (SRE book).

## Practice and project
Guided: predict hit ratio and database load; measure. On your own: find the feedback loop in an incident. Project: in the learner's own service, a cache on its hottest read and a queue for its slowest side effect; finish line: the gain measured, a flush survived, a twice-delivered message with one effect.

## Mastery ladder
- Use: put cache-aside with expiry on an endpoint; report its hit ratio.
- Explain: show a friend how one hot key expiring sinks a database, and two fixes.
- Build: the project above.
- Design: decide, with numbers, whether a stated service needs a cache, a queue, both or neither.

## Words to own
[1] cache-aside, hit ratio; [2] in-process cache; [3] expiry, invalidation, stale read, write-through,
write-back; [4] eviction, LRU, eviction policy, working set; [5] cache stampede, thundering herd, hot key, request
coalescing, lease token; [6] message broker, competing consumers, publish-subscribe, consumer group, offset,
(producer), (consumer), (pub/sub), (log-based broker); [7] at-most-once, at-least-once, acknowledgement,
redelivery, visibility timeout; [8] idempotency, idempotent consumer, deduplication; [9] exponential backoff,
jitter, retry budget, retry storm, dead-letter queue, (circuit breaker), (poison message); [10] backlog,
backpressure, consumer lag
