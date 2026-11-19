# Plan pattern: how a system works

For operating systems, networks, database internals, architecture and theory, and for algorithms studied for how and why they work (training to solve contest or interview problems is `plan-patterns/skill.md`). Header: `run: console` when experiments are typed at a terminal, `run: c` or `python` when the reader writes small programs, else `run: none`; `kind: system`.

## The shape

- **Chapter 1** follows one event through the whole system at low resolution: what happens when you type a URL and press Enter; what happens between `./a.out` and the first line printed; a query from `SELECT` to rows. Every later chapter zooms into one stage of that trace.
- **Choose a direction and say why**: top-down (application to wire, as Kurose and Ross teach networks, because the reader already uses applications) or bottom-up (bits to processes, when each layer is built from the one below).
- **Each chapter follows an order of events**, not a list of parts: who acts first, what each part knows, what happens when a step fails (a lost packet, a power cut mid-write, a page fault).
- **Numbers are content**: latencies, sizes, costs. A back-of-envelope estimate is a skill to practise.
- **Carried through:** one trace or scenario, revisited at more depth each chapter.
- **Practice:** predict, then observe with a real instrument (`strace`, `tcpdump`, `EXPLAIN ANALYZE`, a timer), or trace by hand; then a design question at level 4.

## What weak plans miss

Order of events; failure cases; numbers; experiments the reader can run; trade-offs (why this design and not the other); the history that explains a strange design.

## Sample

Weak: `6.1 ACID`, `6.2 Isolation levels`, `6.3 Locks` (definitions, nothing happens). Better:

```text
### 6 Transactions: many users, one truth
6.1 Two clerks sell the last seat | story
6.2 What a transaction promises | teaches: transaction, atomicity, durability
6.3 Following one commit to the disk: the write-ahead log | teaches: write-ahead-log, fsync | needs: buffer-pool | fig
6.4 Dirty reads, lost updates and write skew | teaches: dirty-read, lost-update, write-skew | fig | level: 2
6.5 Isolation levels and what each allows | teaches: isolation-level, read-committed, serializable | level: 2
6.6 How MVCC lets readers not block writers | teaches: mvcc, row-version | level: 2
6.7 Locks and deadlocks | teaches: row-lock, deadlock | fig
6.8 An experiment: two sessions racing | teaches: concurrent-sessions | level: 3
6.9 Practice: predict the anomaly, then run it | practice | level: 3
```

Anomalies come before isolation levels, because a level is only the list of anomalies it allows.
