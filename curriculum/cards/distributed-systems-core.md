# distributed-systems-core: partial failure, time and consistency between machines
kind: system
aliases: distributed systems, partial failure, clocks, consistency models, linearizability, cap theorem
needs: networking-basics, sql-and-relational, caching-and-queues, scaling-data
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: DDIA 2nd ed. contents (system models); MIT 6.824 schedule (outline); Lamport time-clocks; Cambridge
  dist-sys-notes §4 (vector clocks), §7.2 (quorums, ABD); Spanner OSDI 2012 §3; aphyr.com/posts/299; jepsen.io
  linearizable; Gilbert-Lynch 2012 CAP; kleppmann.com 2015/05/11 (CAP); Abadi PACELC
unverified: that "strong consistency" is also used for models weaker than linearizable is the editor's judgement

## Promise
Say what a silent node, a skewed clock or a network partition does to the learner's data; name exactly the consistency each of its datastores promises, and what it costs.

## The one idea
A machine knows others only by messages that come late or never, and by clocks that disagree; a consistency model says which histories a store may show. Picture: friends arranging to meet by post, each with a different watch. Where it breaks: silence looks the same whether the letter, the friend or the reply was lost.

## In production
- Every call across the network can end in "don't know"; write paths are made safe to repeat, never assumed to have failed.
- Datastores state their guarantees in these words (linearizable, serializable, eventual); Jepsen's analyses test such claims.
- Durations come from the monotonic clock; timestamps from different machines do not decide which write wins.

## Teaching order
1. Partial failure: a lost request, a lost reply and a paused server look alike to the caller; crash-stop, crash-recovery, Byzantine faults; a timeout only guesses (a failure detector); a network partition; `kill -STOP` and `kill -CONT` on the learner's own server.
2. Unknown outcomes: a timed-out `COMMIT` may have happened; the idempotency key (caching-and-queues 8) stored in the effect's own transaction (sql-and-relational 9); exactly-once processing as at-least-once delivery plus that check.
3. Physical clocks: time-of-day (`CLOCK_REALTIME`) against monotonic (`CLOCK_MONOTONIC`, durations only); drift and skew; NTP stepping a clock back; last-write-wins (scaling-data 5) dropping a later write from a node whose clock is behind.
4. Logical clocks: happened-before; Lamport's IR1 and IR2 on three processes, ties broken by process id; a smaller Lamport timestamp does not mean earlier; vector clocks tell concurrent events apart; version vectors do it for replicas' copies.
5. Consistency as histories (Jepsen's way): each operation an interval from call to return; linearizable: one instant inside each interval, one object, real time; "strong consistency" used loosely: ask which; causal consistency; serializable (sql-and-relational 9) against strict serializable.
6. Majorities: any two majorities of n overlap; 2f+1 nodes survive f crashes; scaling-data 5's `w + r > n` gives overlap, not linearizability; ABD: a read writes the newest value back to a quorum before returning; sloppy quorums lose the overlap.
7. CAP as proved: with messages lost or delayed, no read/write store is both linearizable and answering every request at every non-failed node; partitions are not optional; many systems are neither "CP" nor "AP"; PACELC: else, latency against consistency.

## Numbers and traces
- [1] `kill -STOP` mid-request: the caller's read timeout fires and it reports failure; after `kill -CONT` the server commits: the caller was wrong. The stopped server's kernel still completes the TCP handshake, so even `connect()` succeeds (Linux, run 2026-11-19).
- [3] Spanner polls time every 30 s, assumes drift up to 200 µs/s; uncertainty a sawtooth of about 1-7 ms.
- [6] n = 3, w = 2, r = 2: a write in progress has reached only A; a read of {A,B} returns the new value, a later read of {B,C} the old one; with ABD's write-back the second read sees it.
- [7] {A} cut off from {B,C}: a client at A gets a refusal or a wait from a linearizable store, a possibly stale answer from an available one.

## Step notes
### 1
Need: My request timed out, yet the server's log says it ran; how did it fail and succeed?
Show: a 38-line Python `bank.py` (TCP server, balance 100; client, 1 s timeout): request dropped, reply dropped,
server `kill -STOP`ped then `kill -CONT`. Learners expect three errors; the client prints `no reply after 1.0 s`
each time, the balance ends 100, 90, 90 (run here).
Explain: The caller cannot tell these silences apart and delay has no bound, so a timeout is a guess; a
partition is that silence between groups of nodes that all keep running.
Try: predict: the client's output with a 0.5 s pause, then run it; explain: which of the three faults their own
service's logs could tell apart.
### 2
Need: So after a timeout I retry; what could go wrong?
Show: `bank.py`, server paused, client retrying three times: learners predict one debit or none; after `kill
-CONT`, balance 70. With id `r-17` inserted under a primary key in the debit's own SQLite transaction: 90, and
`r-17 already done, not applied again` twice (run here).
Explain: A retry makes "maybe once" "maybe twice"; the key, committed with the effect, lets a repeat find it.
Try: fix: store the id in a second transaction, `kill -9` between the two, show the duplicate; decide: which
write in their own service a retry could repeat, and where its key lives.
### 3
Need: Every server runs NTP; why can't timestamps say which write came last?
Show: a 21-line `lww.py`: A saves `draft`, B `final` 0.5 s later, into last-write-wins; B's clock 2 s behind (an
offset; stepping the real clock needs root). Learners expect `final`: `store keeps: draft`. Clock stepped
back 2 s during 0.5 s: time-of-day `-1.50 s elapsed`, monotonic `0.50 s` (run here).
Explain: Writes closer together than the skew can be ordered backwards; the monotonic clock is never stepped
back (NTP only bends its rate), so it alone measures durations.
Try: predict: the largest skew at which `final` wins, then run it; apply: move a duration their own code times
with `time.time()` or `Date.now()` to the monotonic clock.
### 4
Need: If wall clocks lie, how can machines agree on what happened first?
Show: a 30-line `clocks.py`, three threads on queues: P0 does a, b sends to P1; P1 does c, d receives, e sends
to P2; P2 does f, g receives. Lamport stamps (IR1, IR2) and vectors on every event. Real orders change run to run
(`f c a b d e g`, `a f c b d e g`); the (Lamport, pid) order is `a c f b d e g` every time. `f` L=1, `e` L=4,
yet `[0,0,1]`, `[2,3,0]`: concurrent (run here).
Explain: Happened-before: order in a process, a send before its receipt, chains of these. Lamport's Clock
Condition: a before b implies L(a) < L(b), not the converse (1978); V(a) < V(b) exactly when a happened before b.
Try: predict: the vectors once P2 also sends to P0, then run it; explain: what last-write-wins on Lamport stamps
does to two concurrent writes, and what a version vector shows.
### 5
Need: Our database says "strongly consistent"; what would prove it isn't?
Show: a 31-line `history.py`: primary and replica; W writes x=1, acked once the replica has it 0.2 s later. R1
reads the primary at 0.05 s: 1; R2 the replica at 0.10 s: 0; R3 at 0.30 s: 1. Learners say "synchronous, so
fresh". A 12-line checker tries every order (b first if b ended before a began): `NOT linearizable`; without
R1, `R2 -> W -> R3` is legal (run here).
Explain: Each operation takes effect at one instant inside its interval, so a read starting after another
returned a value returns it or newer; R1 ended before R2 began. Jepsen's checkers also let a timed-out write
take effect or not.
Try: build: call and return times recorded against their own datastore, then checked; predict: a PostgreSQL 16
synchronous standby's read after `COMMIT`, apply delayed 2 s (old value here: `synchronous_commit = on` awaits
a flush, not an apply).
### 6
Need: Two of three replicas take each write and each read asks two; how can a read be old?
Show: the trace under "Numbers and traces" in a 24-line `quorum.py`, replicas holding (timestamp, value), a read
returning the newest of two replies: the write reaches A at once, B and C after 1 s. At 0.10 s client 2 reads
{A,B}: `returns v1`; at 0.20 s client 3 reads {B,C}: `returns v0`; at 1.00 s the write is acknowledged. With
write-back, client 3 gets v1 (run here; Kleppmann's notes §7.2).
Explain: `w + r > n` meets every completed write; during one, a later read can go back in time. ABD's read then
writes the newest value to a quorum and waits for its acks; the program's write-back is instant.
Try: predict: client 3's answer reading {A,C}, then run it; explain: how a sloppy quorum misses a completed write.
### 7
Need: Everyone says "pick two of three"; which did our database pick, and when does it matter?
Show: a 23-line `cap.py`, the cut a rule of which node reaches which: A cut off from {B,C}. Majority store:
write at B `ok`; read and write at A `refused after 0.5 s: no majority reachable`. Local store: A reads `x=1`,
writes 3, copies `{'A': 3, 'B': 2, 'C': 2}`: two truths to merge (run here).
Explain: While messages are lost or delayed, a store must refuse or give up linearizability (Gilbert and Lynch);
otherwise it pays latency (PACELC). Real nodes do not see the cut; they time out (step 1) and refuse on a guess.
Try: decide: per datastore of theirs, from its documentation, what a client with the minority gets, and its
PACELC place (PA/EL, PC/EC); explain: why refusing without a majority is not enough for linearizable (step 6).

## Go deep, leave for later
- Deep steps: 2, 5, 7 (an outcome the caller cannot know, consistency as a history a client can check, and what CAP does and does not say are where understanding is made).
- Later: consensus, leases, 2PC (consensus-and-transactions); Spanner's TrueTime, CRDTs, gossip membership, Byzantine fault tolerance, TLA+.

## Never omit
- Every claim shown by a fault injected into a running system: kill, pause, cut off, clock stepped.
- Look up when planned: the consistency each of the learner's datastores documents, and any Jepsen analysis of it.

## Wrong beliefs
- [1] "A timeout means the other side failed" (no reply came in time; the work may have run, or may yet).
- [2] "A request that timed out is safe to send again" (only if the server can recognise the repeat; otherwise the effect may happen twice).
- [3] "NTP keeps clocks right, so timestamps order events" (clocks drift and step back; last-write-wins drops the later write).
- [4] "A higher Lamport timestamp means the event came later" (concurrent events get ordered timestamps too; vector clocks tell them apart).
- [5] "Serializable means up to date" (some serial order, not real-time; strict serializable is both).
- [6] "`w + r > n` gives linearizable reads" (an unfinished write can be seen by one read and missed by a later one, unless reads write back).
- [7] "CAP means pick two of three" (only during a network partition must a store choose between answering and staying linearizable; otherwise consistency still costs latency).
- [7] "CAP's C is ACID's C" (it is linearizability; ACID's C, sql-and-relational 9, is the application's invariants).

## Failures to diagnose
- [1-2] A payment applied twice after a retried timeout.
- [3] A later edit lost: written on a node whose clock was behind, under last-write-wins.
- [6] A read older than an earlier read: quorum reads without write-back.

## Practice and project
Guided: predict each trace, then run it. Alone: redraw a Jepsen anomaly as a history. Project: the learner's service with a payment-like write and a three-replica datastore; a fault script pauses the server, drops replies, steps a clock and cuts one replica off; finish line: each run's history written down, no effect applied twice, the cut-off replica's behaviour (refused or stale) matched to the store's documentation.

## Mastery ladder
- Use: pause the learner's server with `kill -STOP` mid-request; report what the caller and the database each recorded.
- Explain: draw for a friend, as a history, how quorum reads can go back in time.
- Build: the project above.
- Design: for each datastore in a design, state its consistency model, its PACELC place and what users see during a partition; defend each.

## Words to own
[1] partial failure, network partition, failure detector, crash-recovery; [2] exactly-once processing; [3] time-of-day clock, monotonic clock, clock drift, clock skew; [4] happened-before, Lamport clock, vector clock, version vector; [5] history, linearizability, strong consistency, causal consistency, strict serializability; [6] majority quorum, sloppy quorum; [7] CAP theorem, PACELC
