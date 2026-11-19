# system-design-interviews: the design round, reasoned aloud under a clock
kind: skill
aliases: system design interview, design round
needs: networking-basics, sql-and-relational, system-design-foundations, caching-and-queues, scaling-data, api-design
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: metacareers.com blog preparing-for-your-software-engineering-interview-at-meta (45 minutes; what
  is looked for); amazon.jobs how-we-hire sde-ii-interview-prep (design objectives);
  sre.google/workbook/non-abstract-design (four questions; reasoning over final values); hellointerview.com
  delivery, introduction, levels blog, news-feed, dropbox, whatsapp breakdowns (budget, four areas, one
  interviewer's level expectations, families); pragmaticengineer.com review of Xu's book (contents, budget,
  memorised answers); system-design-primer (outline); AWS SQS visibility timeout
unverified: the families and their grouping are judgement; level expectations are one interviewer's account

## Promise
Run a 45-minute design round aloud: scope, estimate to decide, design simply, go deep at the bottleneck, say
trade-offs and failures unasked.

## The one idea
The interviewer scores the reasoning they hear, not the picture. Picture: an annotated chess game. Where it
breaks: notes cannot save a lost game.

## In production
- Meta's and Amazon's own pages put a design round in software engineer loops; one interviewer's account: rare at entry
  level, the norm from senior up.

## Teaching order
1. The round: 45 minutes, the last five yours (Meta); what Meta, Amazon, the SRE workbook grade; a budget: about 5 minutes requirements, 7 entities and API, 10-15 a working design, 10 deep dives (Hello Interview; Xu similar); levels.
2. Scoping (system-design-foundations 1, 3): the top three functional requirements, the rest out of scope aloud; three to five non-functional ones as numbers: p99 latency, nines, each data's allowed staleness (scaling-data 10).
3. Estimating aloud (system-design-foundations 2) only where a number decides: peak QPS from daily users, a peak factor, 86,400 seconds; storage a year; does the hot set fit one machine's memory.
4. Before boxes: core entities, the API (api-design), access patterns choosing store and partition key (scaling-data 6).
5. A first high-level design that works: each API call traced through the parts; caches and queues only noted.
6. The bottleneck by arithmetic (system-design-foundations 4): load per part against one node's capacity; deep dives where numbers break; the SRE workbook's possible, better, feasible, resilient.
7. Unasked, per part: down, slow, overloaded, what users see (cache gone; queue backed up: message age; replica lagging: read-your-writes); per choice, the rejected option and its price (SQL's joins and transactions against a wide-column store's writes).
8. Read-heavy fan-out (feeds), testing read/write asymmetry: fan-out on write (capped ID lists, filled by queue workers) against on read; the celebrity problem: big accounts merged at read.
9. Write-heavy ingestion (metrics, logs), testing absorption: a log (caching-and-queues 6) takes spikes; batched writes; rollups; storage split by time; sampling where loss is allowed; backpressure (caching-and-queues 10).
10. Low-latency lookup (shorteners, typeahead), testing key design: base62 counters (62^7, about 3.5 trillion) against hashes and collisions; time-ordered IDs; `301` cached against `302` counted; top results per prefix precomputed, in memory.
11. Real-time delivery (chat, notifications), testing connection state: WebSocket servers (api-design 12); who is on which server (a registry, or publish-subscribe: caching-and-queues 6); store, then deliver; an inbox acknowledged on reconnect.
12. Large objects (files, video), testing bytes apart from metadata: bytes to object storage by pre-signed URL; metadata in a database; multipart, resumable upload; content hashes; async transcoding; CDN.
13. Coordination (rate limiter, job scheduler), testing races: check-then-write (sql-and-relational 9); atomic counters in one store (Redis `INCR`); token buckets (api-design 10) local or central; jobs claimed by expiring lease (caching-and-queues 7), so idempotent.
14. Pressure and practice: a follow-up you cannot answer (what you know, your assumption, how to check); a changed requirement; timed mocks with a second person or a recording, each reviewed against "Judged by".

## Judged by
- [2] Requirements agreed, ranked and quantified before any box?
- [3] Did each estimate change a decision?
- [4-5] API and data first; working design by midway?
- [6] Deep where the numbers break?
- [7] Each choice with its rejected option; each failure said unasked?
- Each technology named with what it does here and why?
- [14] Gaps reasoned aloud, never bluffed; did you lead?

## Step notes
### 1
Need: Is my diagram compared with a right answer, and how long is each part?
Show: a prompt from their own list, system-design-foundations 1's whole practice in 45 minutes, aloud and recorded, against the budget (5, 2, 5, 10-15, 10: 32 to 37 minutes, then questions); each phase's end marked from the recording, not memory.
Explain: They grade reasoning heard: Meta, hard parts, whole and details, trade-offs, a conversation; Amazon, practicality, accuracy, efficiency, reliability, optimisation, scalability; SRE workbook, reasoning over final values.
Try: build: the run, phase times a second person confirms within a minute; explain: its level (one interviewer: mid covers basics, senior deep in about two places, staff leads).
### 2
Need: Given a one-line prompt, shouldn't I start drawing to show I can?
Show: on a prompt from their own list, twice on a clock (system-design-foundations 1, SLOs from 3), as here on a URL shortener. Boxes first: servers, Cassandra, Redis, `301`; minute 25, "we need click counts": redesign. Four questions first: custom aliases? (a uniqueness check); links and clicks a day? (100 million, a billion: reads rule); analytics? (`302`, a click stream); how soon live everywhere? (seconds: cached replicas). Three moved a box.
Explain: A question earns its minute if its answer moves a box; agreed scope, out-of-scope said aloud, judges every later choice.
Try: build: four questions on a new prompt in 5 timed minutes, a listener naming what each changed; fix: a mock that designed another system, rescoped.
### 3
Need: Must I do all the maths first?
Show: on their prompt, as here on the shortener (system-design-foundations 2): "a billion redirects a day over 86,400 is 11,600 a second, 35,000 at three times peak; one PostgreSQL node, tens of thousands of indexed reads: no headroom, so a cache." "Ten million profiles at 1 KB: 10 GB": none (Hello Interview: only what changes the design).
Explain: An estimate earns its minute if it ends in "so": a cache, a shard, "one machine will do".
Try: apply: three estimates for a prompt in 3 minutes, each ending in its decision; decide: which of five estimates change nothing.
### 4
Need: What goes on the board before server boxes?
Show: on their prompt, as here on the shortener: entities Link (code, URL, owner), Click; `POST /links`, `GET /{code}`, `GET /links?owner=` paged (api-design 1, 5). By code: a point lookup; by owner: a list a code-keyed store needs an index for (scaling-data 8).
Explain: Store and partition key follow from the queries that must stay cheap (scaling-data 6).
Try: build: entities, three endpoints, patterns in 7 timed minutes, each pattern with its key; fix: a design naming Cassandra before any pattern.
### 5
Need: Shouldn't v1 have caches, queues, shards to look senior?
Show: on their prompt, as here on the shortener, from system-design-foundations 5's blocks: load balancer, stateless servers, PostgreSQL primary and replica. `POST /links`: server, primary, `201`; `GET /{code}`: server, replica, `302`; cache and click queue only noted.
Explain: A working end-to-end design is what step 6's arithmetic tests; a part before its number costs minutes and a defence.
Try: build: a design traced call by call in 12 timed minutes, each call heard on the recording; explain: the number a wanted part needs.
### 6
Need: How do I pick the deep dive, if not the part I know best?
Show: on their v1, as here on the shortener's (system-design-foundations 4): reads, 35,000 a second against 30,000-55,000: a cache. The write nobody checked, an `INSERT` per click: 35,000 against 4,000-12,000: three to nine times over; 100-row batches carry 250,000 rows: a log and rollups (step 9). `pgbench`'s default transaction (1,300-1,900) said twenty: measure the design's own operation.
Explain: Each part's load over one node's measured capacity for that operation: dive where it is worst.
Try: apply: a load-against-capacity line per part of their v1 in 5 minutes, worst named; predict: where the bottleneck moves if clicks double.
### 7
Need: I said "add Redis"; why did they ask what happens when it goes down?
Show: on their design, as here on the shortener: weak: "Redis, for speed." Strong: "Redis, not in-process (a stale copy per server, caching-and-queues 2). If Redis dies, 35,000 reads a second land on a node good for 30,000-55,000: no headroom, waits climb (caching-and-queues 5): a second replica. Users see slow redirects."
Explain: Each choice with its price, each part with its failure and what users see (system-design-foundations 8, 7).
Try: build: per box, "down or slow, users see..." in 5 timed minutes, a listener listing them; decide: SQL or wide-column for a prompt, with prices.
### 8
Need: Why not build each follower's feed at posting?
Show: an account with 10 million followers posts: 10 million inbox inserts; at an assumed 50,000 a second the last follower waits 200 s (scaling-data 7). Merged at read: one lookup.
Explain: Write fan-out costs per follower; past some count, merging at read is cheaper: feeds mix both.
Try: apply: the follower count past which they merge at read, from stated rates, in 3 minutes; explain: failure [8] aloud.
### 9
Need: A million metric points a second: just a bigger database?
Show: a million 100-byte points a second: 100 MB/s, 8.64 TB a day; a log takes it (caching-and-queues 6), consumers batch, roll up by minute. A 30-minute spike at ten times capacity: about 300 minutes to clear (caching-and-queues 10); alarm on message age.
Explain: Absorb in a log, then shrink: batches, rollups, time-split storage, sampling where loss is allowed, backpressure.
Try: apply: raw and rolled-up bytes a day for a prompt in 2 minutes; decide: which data may be sampled.
### 10
Need: Counter or hash for short codes: does it matter?
Show: 62^7 = 3,521,614,606,208 codes, 96 years at 100 million a day. Random 7-character codes: about 142,000 colliding pairs in a billion (birthday bound): every write checks. Browsers may cache `301` (RFC 9110; networking-basics 8); `302` counts every click.
Explain: A counter or time-ordered ID never collides but needs coordination, is guessable; a hash needs a collision check.
Try: predict: collisions in 10 million random 6-character codes, then compute; decide: `301` or `302` with analytics.
### 11
Need: Sent over a WebSocket; why do offline users lose it?
Show: weak: published to the recipient's server (caching-and-queues 6); offline, nobody subscribed: gone. Strong: stored, then delivered; on reconnect the client acknowledges its inbox's last ID, gets the rest (caching-and-queues 7).
Explain: Publish-subscribe forgets absent subscribers, so a message is stored before it is delivered.
Try: build: "send offline, reconnect" as a sequence in 4 minutes, no arrow losing a message; explain: its server dying mid-delivery.
### 12
Need: Why not upload video through my API servers?
Show: 1 GB at 10 MB a second holds a connection 100 s; 1,000 uploads a minute by Little's law (system-design-foundations 4): about 1,670 in flight on app servers. A pre-signed URL sends bytes to object storage.
Explain: Bytes and metadata load differently: bytes to storage and CDN, metadata via the API, transcoding queued; multipart resumes a part.
Try: apply: in-flight uploads by Little's law in 2 minutes; decide: what is resent after a drop at 70%.
### 13
Need: Two gateways count to 100; how do both admit the 101st?
Show: both read 99, write 100, admit (sql-and-relational 9); Redis `INCR` returns each its own count: 100, 101. A 30-second lease on a 45-second job: a second worker runs it too, as an SQS message reappears after its visibility timeout (caching-and-queues 7).
Explain: A race is a read, then a write, not one atomic step; a lease bounds a dead worker's hold, at the price of duplicates.
Try: predict: what three gateways' local buckets of 100 a minute admit (api-design 10); fix: failure [13] with an idempotency key.
### 14
Need: Asked how Cassandra settles concurrent writes, I froze: bluff?
Show: bad: "it locks the row on every replica" (false, checkable). Good: "I don't know its internals; last-write-wins drops one concurrent write (scaling-data 5); I'll assume it, give each row one writer, check the docs."
Explain: Known, assumed, how to check is reasoning, what Meta and the SRE workbook grade; a bluff is a testable claim.
Try: build: a recorded mock, three follow-ups past their knowledge, each answered in three parts; apply: "now global" at minute 30, rescoped in 3.

## Believable numbers
- [3] A million a day is about 12 a second (86,400 seconds).
- [3,6] PostgreSQL 16, 2 cores, `pgbench`, 8 clients, shared machine (2026-11), a second: indexed reads 30,000-55,000; one-row `INSERT`s 4,000-12,000; in 100-row batches, 270,000-440,000 rows; the default transaction, 1,300-1,900.

## Go deep, leave for later
- Deep steps: 2, 6, 7 (where the foundations are used under a clock).
- Later: consensus (consensus-and-transactions); crawler, search and proximity (geohash) questions; ML and frontend rounds.

## Never omit
- Every question timed, aloud.
- Every claim one the learner can defend from a foundations card; no recalled diagram without its numbers.
- Look up: the company's format; one node's capacities.

## Wrong beliefs
- [1] "Naming Kafka or Cassandra shows seniority" (it draws "what does it do, why here?"; seniors give reasons).
- [1] "My diagram is compared with a reference answer" (companies say they judge focus, trade-offs, reasoning,
  conversation).
- [3] "Estimate everything first" (only what changes a decision; say so).
- [5] "A strong first design has caches, queues and shards" (complexity before a bottleneck is shown costs time).
- [7] "Naming the best option is enough" (Meta's page: a good solution compares and contrasts approaches).
- [8-13] "Memorising classic designs is preparation" (a changed constraint breaks the recalled diagram).

## Failures to diagnose
- [1] Minute 30, no design: no time budget.
- [2] A design for another question: no agreed scope.
- [6] Deep dive on a comfortable part, another far past capacity: no load line per part.
- [8] One huge account's post stalls: pure fan-out on write.
- [11] Messages lost while offline: published, never stored.
- [13] A job run twice after a lease expired: not idempotent.

## Practice and project
Guided: per family, a question of the learner's own aloud, then a published breakdown compared.
Project: six recorded 45-minute mocks, one per family, scored by a second person; finish line: the last two pass
every "Judged by" test.

## Mastery ladder
- Use: do steps 2-5 on an unseen question in 25 minutes.
- Explain: mark where each graded area showed on your recording.
- Build: the project above.
- Design: interview a peer on a question you scoped; write notes by area.

## Words to own
[1] level, time budget; [2] out of scope; [4] core entity, access pattern; [5] high-level design; [6]
deep dive; [8] fan-out on write, celebrity problem; [9] ingestion, rollup, sampling;
[10] base62, time-ordered ID; [11] inbox; [12] pre-signed URL, multipart upload, transcoding; [13]
atomic counter; [14] follow-up
