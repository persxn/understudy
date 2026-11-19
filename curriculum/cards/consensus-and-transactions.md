# consensus-and-transactions: agreement, leases and transactions across machines
kind: system
aliases: consensus, raft, distributed locks, two-phase commit, sagas, transactional outbox
needs: sql-and-relational, caching-and-queues, scaling-data, distributed-systems-core
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: raft.pdf §5, 8 (votes, timing, commit rule, serial numbers, reads); MIT 6.824 schedule (outline), l-2pc
  notes (what is logged, blocking, Raft-replicated parties); kleppmann.com 2016/02/08 (pauses, fencing tokens, zxid);
  jepsen.io etcd-3.4.3 (1-3 s leases, revision as fencing token); Cambridge dist-sys-notes (in-doubt
  transactions); microservices.io saga, transactional-outbox (duplicates, idempotent consumers);
  postgresql.org/docs/16 sql-prepare-transaction (a prepared transaction keeps its locks; meant for a transaction manager)

## Promise
Choose and test the agreement a design needs: a consensus store for one ordered log, a fenced lease for one holder, and for work across databases one database, 2PC or a saga with an outbox.

## The one idea
Agreement is a majority voting on one ordered log; leases, locks and commits across machines are built on it or chosen instead of it. Picture: a committee voting by post. Where it breaks: a member who slept through a vote thinks he still chairs.

## In production
- Consensus comes from etcd, ZooKeeper, Consul or a database's own Raft, never home-made.
- A lock is a lease; only storage that checks a fencing token makes it safe.
- 2PC is used inside one database system; across services, an outbox and sagas.

## Teaching order
1. Consensus as a tool: a replicated state machine (one log, one order, every replica applying it) behind a Raft leader; a majority (distributed-systems-core 6) for any progress; safety never depends on timing, liveness does: broadcast time ≪ election timeout ≪ time between failures.
2. One write through Raft: AppendEntries (previous index and term checked), a majority, commit index, apply; the leader stops; terms; randomized timeouts against split votes; RequestVote (one vote per term, only to a log at least as up-to-date); only own-term entries counted (Figure 8); serial numbers stop a second apply.
3. Reads: a deposed leader still answering gives stale reads; Raft's fix: a no-op entry per term and a heartbeat round with a majority before answering (linearizable, distributed-systems-core 5), or a lease, which trusts bounded clock skew (distributed-systems-core 3).
4. Locks and leases: a lock from a consensus store is a lease that expires; a holder paused (garbage collection, `kill -STOP`) past its lease acts after another took over; a fencing token (etcd's lock revision, ZooKeeper's zxid) checked by the storage; scaling-data 4's fencing made exact.
5. Two-phase commit (named in scaling-data 11): PREPARE; a participant logs its changes, keeps its locks, votes; the coordinator logs COMMIT, then sends it; if it dies after PREPARE, YES-voters wait in doubt, locks held; atomic, not available, unless each party is a Raft group.
6. Instead of 2PC: the dual-write bug (commit, then crash before publishing); the transactional outbox: the message in the same local transaction, a relay publishing at least once, consumers idempotent (caching-and-queues 8); sagas: local transactions and compensations, without isolation.

## Numbers and traces
- [1] Raft: election timeout 150-300 ms, against 0.5-20 ms to send to all servers and hear back. On one laptop, a commit on 2 of 3 processes over loopback UDP took 0.1-1 ms (run 2026-11-19).
- [4] etcd locks on 1-3 s leases had two holders within minutes, in healthy clusters (Jepsen).
- [2] A write at term T, index i; the leader dies before commit (kept if the new leader holds it, else overwritten), then after commit, before replying (the serial number stops a second apply).
- [5] The coordinator dies after PREPARE, before and after logging COMMIT; what each YES-voter holds.
- [6] Order row and outbox row in one transaction; the relay publishes, crashes before marking it sent, publishes again; the consumer's stored key drops the second.

## Step notes
### 1
Need: Our etcd has three nodes; how many can stop before writes fail, and do they fail or go wrong?
Show: a 29-line `majority.py`: a leader and two follower processes on UDP; commit when 2 of 3 hold an entry. One
follower `kill -STOP`ped: `x=2 committed (2 of 3)`. Both: `x=3 NOT committed: held by 1 of 3 after 500 ms`;
it just stops. After `kill -CONT` both store x=3 from their socket buffers: "NOT committed" is not
"gone" (run here).
Explain: Two majorities always share a node, so no decision is contradicted; without one, none is made. Raft's
leader retries forever (§5.3): x=3 commits when a follower returns, unless a leader without it wins first.
Try: predict: how many of five can stop with writes still committing, then change the program; decide: an
election timeout for a 20 ms broadcast time, and what 10 ms would cause.
### 2
Need: The leader died in the middle of my write; is the write in or out, and who decides?
Show: a 55-line `raft1.py`, one process, RequestVote, AppendEntries and the commit rule on S1-S3 (a paused node
answers nothing). S1's `debit` reaches only S2; S1 is paused. S3 times out first: `S2 refuses: my log (1, 1) is
more up-to-date than yours (0, 0)`; S2 wins term 3. On 3 of 3, still `commit index 0` until a term-3 no-op
commits. The retry applies again: 80; with serial numbers 90. Entry only on S1: `overwritten` (run here).
Explain: Voters refuse a less up-to-date log (later last term, else longer), so a winner holds every committed
entry; it counts only own-term entries, older ones commit with them. On all three the rule only waits; Figure 8
shows why: on five, an older entry on a majority overwritten (§5.4.2).
Try: predict: who can win had S3 stored it too, then run it; build: Figure 8, five servers, counting any entry on
3 of 5: S1 commits (2, a) in term 4; S5 wins term 5 and overwrites it (run here).
### 3
Need: Reads change nothing; why can't the leader answer them from memory?
Show: `raft1.py`: S1, paused since term 1, resumes while S2 leads term 3 with 90 committed. Asked first, S1
answers 100. With a heartbeat round first (empty AppendEntries), S2 and S3 reply term 3; S1 steps down and
refuses (run here; §8).
Explain: A leader can be deposed unawares; it answers after a no-op of its term and a majority's heartbeat replies.
A lease skips the round, making safety depend on bounded clock skew.
Try: predict: what S2 answers before its no-op commits, had S1 heard S2's ack and replied `ok` (100: an
acknowledged debit missed, run here); decide: which documented read option of their datastore each read needs.
### 4
Need: I take a lock in etcd or Redis before writing; how can two clients both write?
Show: a 42-line `lease.py`: 1 s leases, tokens from 33, storage, two client processes. Client 1 gets 33, prints
`lease has 0.8 s left, writing`, is `kill -STOP`ped 2 s; client 2 gets 34, writes. After `kill -CONT` client 1
overwrites it. Storage keeping the highest token: `REFUSED: token 33 < 34` (run here; Kleppmann 2016).
Explain: A pause can fall between any check and the write; only storage sees every write, so it refuses old tokens.
Try: fix: fence a lock in their own service (etcd's revision or a counter), pause the holder, show the refusal;
predict: what breaks if storage checks the token and writes in two statements.
### 5
Need: 2PC makes two databases commit together; what if the coordinator crashes halfway?
Show: two PostgreSQL 16 servers (`max_prepared_transactions = 5`) each `PREPARE TRANSACTION 'tx42'` after
an `UPDATE`; no coordinator returns. `pg_locks`: locks with no `pid`. A read gets 100; an `UPDATE` under
`lock_timeout = '2s'`: `ERROR: canceling statement due to lock timeout`, even after a restart. Only
`COMMIT PREPARED 'tx42'` or `ROLLBACK PREPARED` frees it (run here).
Explain: A YES-voter promised to commit if told, so it cannot decide alone; the outcome is in the coordinator's log.
Try: decide: whether `ROLLBACK PREPARED` on one participant is safe with the coordinator's log lost (run
here, the other committed: 100 and 110, ten created); build: an alert on any `pg_prepared_xacts` row older
than a minute.
### 6
Need: I save the order, then publish "order placed"; what is wrong with that?
Show: a 35-line `outbox.py`, SQLite: order and outbox rows in one transaction; the relay publishes, then
`SIGKILL`s itself before marking. Restarted, it publishes again: two `order 7 confirmed`, two emails; a consumer
storing the message id with the effect prints `message 1 already processed, dropped` (run here).
Explain: The outbox makes "commit and publish" one local commit plus a retry loop: never lost, sometimes repeated.
Try: fix: kill their own service between a commit and its publish, show the lost message, move it to an outbox;
decide: the compensation for each step of one of their sagas, and what users see in between.

## Go deep, leave for later
- Deep steps: 2, 4, 5 (one entry through a leader failure, a fenced lease, and a prepared transaction left in doubt are where understanding is made).
- Later: Paxos, membership changes, chain replication, Spanner's TrueTime, Byzantine faults, TLA+.

## Never omit
- Every claim shown by a fault injected into a running system: kill, pause, cut off.
- Look up when planned: the read and lock options of the learner's datastores.

## Wrong beliefs
- [2] "An entry on a majority is committed" (an old-term entry on a majority can still be overwritten).
- [4] "A lock service guarantees one holder" (a paused holder acts after its lease; storage must refuse old tokens).
- [5] "Two-phase commit survives a coordinator crash" (YES-voters block with locks held until it returns).
- [6] "A saga is a transaction" (no isolation; undo is business code).

## Failures to diagnose
- [1] Writes refused after two of three nodes are stopped: no majority, no leader.
- [4] Two lock holders after a pause longer than the lease.
- [6] A relay publishing twice; a message sent for a rolled-back write.

## Practice and project
Guided: predict each trace, then run it. Alone: read one Jepsen analysis and name the step whose guarantee broke. Project: a fault script against a three-node consensus store under the learner's service; finish line: per run, a history with no acknowledged write lost, a stale holder refused, the minority refusing writes.

## Mastery ladder
- Use: kill a three-node store's leader; report the election time and lost writes.
- Explain: walk a friend through one Raft write and a leader crash.
- Build: the project above.
- Design: for a cross-service operation, choose one database, 2PC or a saga with an outbox; defend it.

## Words to own
[1] consensus, replicated state machine, election timeout, liveness; [2] log entry, AppendEntries, commit index, term, leader election; [3] linearizable read, safety; [4] distributed lock, lease, process pause, fencing token; [5] two-phase commit, coordinator, prepare, in-doubt transaction; [6] dual write, transactional outbox, saga, compensating transaction
