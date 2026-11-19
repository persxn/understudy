# scaling-data: replication, partitioning and consistency, and their costs
kind: system
aliases: database scaling, replication, sharding, consistency models
needs: networking-basics, sql-and-relational, system-design-foundations
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: DDIA 2nd ed. ch. 6, 7 (order, indexes, hot spots); github.blog oct21-post-incident-analysis;
  discord.com/blog how-discord-stores-trillions-of-messages; infoq.com cap-twelve-years-later; docs.aws.amazon.com
  Aurora.Replication; hpbn.co (56 ms); a PostgreSQL 16 primary and standby run
  (steps 1-4, 10-11); hashing, hot keys, indexes, quorums simulated
unverified: replicas before sharding (In production) is judgement

## Promise
Choose how to replicate and partition data for a stated load, price each choice in latency, consistency and operations, spot its failures.

## The one idea
Copies let data survive and reads grow; splits let writes and size grow. Copies lag; splits send some questions everywhere. Picture: a library with branch copies, books split across buildings by letter. Where it breaks: branches hear of new books late; everyone wants one building.

## In production
- A read replica and a standby usually come long before sharding; failover is where data is lost or split.
- The partition key decides which queries stay cheap.

## Teaching order
1. Why one database stops being enough, measured in the learner's own: working set past memory, reads past CPU, writes past the disk's IOPS, one machine's downtime; before sharding: split by function (a database per service).
2. Leader and followers (primary and replicas): the change log (PostgreSQL's WAL, MySQL's binlog) shipped and replayed; a follower from `pg_basebackup`; synchronous or asynchronous; `pg_stat_replication`; reads sent to a replica.
3. Lag anomalies: read-your-writes, monotonic reads, consistent prefix; fixes: own data from the leader for a while, one replica per user, waiting until `pg_last_wal_replay_lsn()` passes the write.
4. Failover: heartbeats and a timeout; the freshest follower promoted (`pg_promote()`), clients redirected; RPO, RTO; an old leader still taking writes (split-brain), stopped by fencing; GitHub 2018 traced.
5. Multi-leader (several regions, offline clients) and its write conflicts; leaderless (Cassandra): n, w, r and `w + r > n`, read repair; last-write-wins silently dropping a concurrent write.
6. Partitioning (sharding): by key range (ordered scans, hot ranges) or hash of key (even spread, no range scans); `hash mod N`; the partition key chosen from the queries that must stay on one shard (a tenant, a user, a channel).
7. Hot partitions: a celebrity or a timestamp key; one key spread by a suffix, read back from all; Discord traced.
8. Secondary indexes across partitions (DynamoDB's LSI, GSI): local (scatter-gather, slow as the slowest shard) or global (partitioned by the field; a write touches several shards, so it often updates late).
9. Rebalancing and routing: many more fixed partitions than nodes, moved whole; consistent hashing with virtual nodes; automatic or operator-approved moves; routing by ZooKeeper, a routing tier or any node.
10. Consistency models and their price, per kind of data: eventual, read-your-writes, linearizable (distributed-systems-core 5); in a partition, refuse or answer stale (CAP: distributed-systems-core 7); without one, round trips.
11. Transactions across partitions: a write to two shards loses one-machine atomicity; two-phase commit (2PC) holds locks across machines (consensus-and-transactions 5); designs keeping each transaction in one partition key.

## Numbers and traces
- [2] Lag measured: `replay_lag` in `pg_stat_replication` (empty while idle); Aurora's "usually much less than 100 milliseconds", more under heavy writes.
- [4] GitHub 2018: a 43-second cut; promoted West Coast primaries took writes for nearly 40 minutes while seconds of East Coast writes (954 on one cluster) never crossed: 24 hours 11 minutes degraded.
- [2-3] A write: the leader logs, commits, answers (if asynchronous); the follower receives, replays; a read before replay sees the old row.
- [4] Failover: timeout, promotion, clients move; unshipped writes lost, or clashing with an unfenced old leader (`pg_promote()` beside a live primary: both accept `INSERT`).
- [7] Discord: keyed by channel and time bucket; one busy channel slowed quorum reads across 177 Cassandra nodes; a service in front coalesced identical reads.
- [1] One 2-CPU virtual machine, PostgreSQL 16, two days (2026-11): 28,000 to 90,000 cached primary-key reads a second, 1,600 to 4,300 small write transactions; disk flushes 200 to 8,000 a second, by disk.
- [2-3,10] On one machine (a laptop) a small commit is replayed on the standby in about 0.2 ms; a network adds its trip: New York to London 28 ms one way, so a synchronous commit waits at least 56 ms, one fibre round trip (hpbn.co); a bulk write adds WAL bytes ÷ bandwidth.

## Step notes
### 1
Need: One reviewer says "add a read replica", another says "shard it": which one fixes what?
Show: `pgbench -i -s 10`, then reads (`pgbench -S -c 8 -T 8`) and small writes (`-N`). Most guess similar rates. PostgreSQL 16, 2 CPUs, two days: 28,400 and 52,000 reads a second, 1,580 and 3,700 writes, 15-20 times fewer; `pg_test_fsync`: 200-300 flushes a second on one virtual disk, 8,000 on another.
Explain: Reads need CPU and memory, which copies multiply; every write is applied on every copy, so only a split multiplies writes.
Try: apply: both runs on their own database, then one division: which limit their peak hits first; decide: replica, split by function or bigger machine for their busiest table, with the number.
### 2
Need: What is a replica doing all day, and how far behind is it?
Show: a standby from `pg_basebackup -R`; `INSERT` there: "ERROR: cannot execute INSERT in a read-only transaction". 3 million rows in one `INSERT` on the primary: 0.13 to 0.35 s after `COMMIT` the standby counts 0 (`replay_lag` 0.13-0.3 s); at 0.45-0.7 s all 3 million appear at once. One machine: the insert wrote 459 MB of WAL, 4 s more over 1 Gbit/s.
Explain: The leader logs each change (WAL) first; followers, started from a snapshot plus the log, replay it in order, so a follower is the leader a moment ago; synchronous means the commit waits for a copy (step 10).
Try: predict: `replay_lag` during their biggest batch job, then measure; fix: an app writing to the replica URL (the error above).
### 3
Need: Users swear their comment vanished after posting, yet the row is there: what happened?
Show: a `dblink` loop, 1,000 times: `INSERT` on the primary, read that id on the standby at once. Expected on one machine: none missing; here 667 to 936 found nothing. Wait until the standby's `pg_last_wal_replay_lsn()` passes the primary's `pg_current_wal_lsn()` taken after the commit: 0 stale, mean wait 0.22 ms (taken before it: 430).
Explain: Followers apply the log late, so a read there can miss one's own post (read-your-writes), see a reply then lose it on a staler replica (monotonic reads), or an answer before its question (consistent prefix).
Try: build: read-your-writes in their app (leader for a minute, or the LSN wait); predict: two reads on two unequally lagging replicas.
### 4
Need: If the primary dies at 3 a.m., what happens to the writes it just accepted?
Show: `SELECT pg_promote()` on the standby, old primary still up: an `INSERT` to each succeeds. Made a standby of the new one, the old logs "new timeline 2 forked off current database system timeline 1"; `pg_rewind` refuses (no checksums, no `wal_log_hints`); rebuilt by `pg_basebackup`, its row is gone.
Explain: Promotion starts a new timeline; writes the old leader took after it are lost (RPO) unless fencing stopped it; a short heartbeat timeout fails over on false alarms, a long one adds downtime (RTO).
Try: build: a script killing the leader, reporting downtime and lost writes; explain: from GitHub 2018, why failing back would lose writes.
### 5
Need: Why would anyone run a database with no leader at all?
Show: a 25-line simulation, n = 3, each replica missing a write 30% of the time: w = 1, r = 1: 28% of reads after an acknowledged write are old; w = 2, r = 2: 0%, 22% of writes refused; w = 3, r = 1: 66% refused. Last-write-wins with clocks 5 ms apart keeps the earlier edit, silently.
Explain: A write acknowledged by w copies and a read of r overlap when `w + r > n`, so the read meets the newest version; read repair mends stale copies; several leaders must merge conflicts.
Try: predict: stale reads at w = 1, r = 3, then run it; decide: one leader or several for their data, naming the conflict to merge.
### 6
Need: Which column do we shard on, and what breaks if I pick wrong?
Show: 30 lines: 100,000 keys placed by `hash mod 10`, then 11. Most guess 10% move; 90.7% do. On a ring with 100 virtual nodes each: 8.0%.
Explain: The partition key picks a row's shard: a query naming it asks one shard, any other asks all, so choose it from the queries that must stay cheap (a tenant's, a user's, a channel's); hash spreads keys, loses range scans; key range keeps scans, makes hot ranges.
Try: decide: the key for their three busiest queries, naming which become scatter-gather; predict: which shard a time-ordered insert stream fills under range partitioning.
### 7
Need: Our keys are spread evenly, so why is one shard on fire?
Show: 1,000,000 messages over 100,000 channels (Zipf-like, exponent 1.2), hashed to 8 shards: channels per shard 12,400 to 12,700, messages 65,000 to 260,000; one channel carries 19.6%. The top 100 split by a suffix 0-7 onto successive shards: busiest 13.0%, their reads ask 8. Hashing the suffix let copies collide: 18.7%.
Explain: Hashing evens out keys, not traffic: a popular key lives on one shard until split by hand and read back from all pieces.
Try: build: per-key request counts from their logs, top 10 keys' share; fix: a hot key split by suffix, with its read path.
### 8
Need: Orders are sharded by user, so how do I find every order of one product?
Show: a 25-line program, 8 shards, 50,000 orders: a user's orders, one shard; a product's 33 orders, a local index asks all 8; a global index takes 2 round trips (its shard, then 8, the rows being scattered), and a write touches 1.88 shards.
Explain: A local index sits beside each shard's rows, so a query by its field asks every shard, slow as the slowest; a global index is partitioned by the field: fewer asked, more written, often late.
Try: predict: shards asked by their slowest report under each index, then count; decide: local or global for one field, from its read and write rates.
### 9
Need: Adding one more database server: must most of the data move?
Show: the step 6 program with 1,000 fixed partitions: the new node takes 9 from each of 10, 90 moved whole, 8.9% of keys move. A ring with one point per node puts 20.2% of keys on its biggest node (fair 9.1%); 100 virtual nodes: 11.4%.
Explain: Hash keys once into many more partitions than nodes; a new node takes whole partitions, and a router maps partition to node.
Try: build: rebalancing 4 to 5 nodes with moves counted; decide: automatic or operator-approved moves, given a move loads both nodes.
### 10
Need: "Strong" or "eventual": which do we need, and what does each cost?
Show: step 3's loop with `synchronous_commit = remote_apply`: stale reads 811-900 of 1,000 become 0, the loop twice as slow; with `on` (flushed there, not replayed) 74-104 stay stale. Standby stopped: the next `INSERT` hangs (`SyncRep`), `statement_timeout` does not end it; cancelled: "already committed locally, but might not have been replicated".
Explain: Each guarantee is paid in waiting: eventual answers at once, maybe stale; linearizable (as if one copy, in real time) waits for agreement and, cut off, must refuse.
Try: decide: a model per kind of data in their service (balance, feed, counter); explain: why "eventual" has no bound.
### 11
Need: Moving money between users on two shards: what replaces the transaction?
Show: two databases as shards; the debit commits, the process dies before the credit: total 170, not 200. With `PREPARE TRANSACTION` on both and no `COMMIT PREPARED`, a writer gets "canceling statement due to lock timeout"; after a restart `pg_prepared_xacts` still lists both.
Explain: Each shard commits alone; 2PC makes each promise first, and a promised shard keeps its locks until the coordinator decides, even across crashes.
Try: build: the transfer inside one shard by the key chosen; predict: who can write those rows while a prepared transaction waits.

## Go deep, leave for later
- Deep steps: 2, 3, 4, 6 (what a replica is and how late it is, the anomalies lag makes, failover's lost writes and split-brain, and the partition key decide every later choice).
- Later: exact CAP, PACELC (distributed-systems-core); consensus, 2PC (consensus-and-transactions); storage engines (LSM trees), change data capture, CRDTs.

## Never omit
- [3] Each anomaly made to happen before it is named.
- [4] The leader killed on purpose; downtime and lost writes measured.
- Look up when planned: the database's replication and failover settings.

## Wrong beliefs
- [1] "Sharding is the first way to scale" (indexes, caches, replicas, a bigger machine usually come first).
- [2] "A replica is a backup" (it copies mistakes and deletes within seconds; only a backup goes back).
- [2] "A read replica takes load off writes" (every write is still applied on every copy).
- [3] "On a fast network the replica is up to date" (here, on one machine, most immediate reads of one's own write missed it).
- [4] "Automatic failover loses nothing" (with asynchronous replication, unreplicated writes are lost or clash).
- [6] "Adding a shard moves a fair share of the data" (under `hash mod N`, 10 to 11 nodes moves about 91%; fixed partitions or a ring move about 1 in 11).
- [7] "Hashing keys spreads the load" (it spreads keys, not traffic).
- [10] "Eventual consistency means correct soon" (replicas agree once writes stop, with no bound on when).

## Failures to diagnose
- [2] "cannot execute INSERT in a read-only transaction": writes sent to a follower.
- [3] A user not seeing their own post: the read hit a lagging follower.
- [4] Two leaders taking writes: failover in a network split, unfenced.
- [6,9] Most data moving when a node is added: `hash mod N` placement.
- [7] A hot partition: one key (a celebrity, a huge channel) takes most traffic.
- [8] A query hitting every shard: its filter lacks the partition key.
- [10] Commits hanging on `SyncRep`: the only synchronous standby is down.
- [11] Rows locked by a prepared transaction nobody finished: `pg_prepared_xacts`.

## Practice and project
Guided: predict a read sequence's anomaly; run it. Alone: price three designs for one workload. Project: the learner's own database with a leader, two followers, a table partitioned by a key from its queries; finish line: a script kills the leader, reports downtime and lost writes; read-your-writes holds after failover.

## Mastery ladder
- Use: add a read replica; route reads so writers see their writes.
- Explain: tell a friend why GitHub could not fail back.
- Build: the project above.
- Design: choose replication, partition key and consistency for a chat service with a few huge channels.

## Words to own
[1] IOPS; [2] leader, follower, read replica, write-ahead log, asynchronous replication; [3] replication lag, read-your-writes, monotonic reads, consistent prefix;
[4] failover, (heartbeat), RPO, RTO, split-brain, fencing; [5] multi-leader, leaderless, replication
factor, quorum, (read repair), last-write-wins; [6] partition key, shard, key-range partitioning, hash partitioning;
[7] hot partition; [8] secondary index, local index, global index, scatter-gather; [9] rebalancing,
consistent hashing, virtual node; [10] eventual consistency, synchronous replication;
[11] distributed transaction
