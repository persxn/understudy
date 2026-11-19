# sql-and-relational: SQL and relational databases for people who build applications
kind: language
aliases: sql, relational databases, postgresql, mysql, data modelling
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: postgresql.org/docs: contents (order), sql-select (processing order), transaction-iso (anomalies), glossary (ACID),
  docs/18 indexes-multicolumn (skip scan);
  use-the-index-luke.com/sql/table-of-contents; DDIA ch. 7 (lost update, write skew);
  dbi-services.com/blog/oracle-serializable-is-not-serializable; postgresql.org/docs/16/app-pgdump.html (roles not in
  a single-database dump); postgresql.org/docs/16/pgbench.html (custom scripts, `--max-tries`)
unverified: How it runs was run on PostgreSQL 16 only, not MySQL; skip scan read in the 18 docs, not run

## Promise
Model a real application's data, query it, speed slow queries from the plan, change it safely while others write.

## The one idea
You describe the rows you want; the database decides how to fetch them and keeps them true under many writers. Picture: a librarian with card indexes. Where it breaks: fast only with the right index; safe from other writers only as far as the isolation level says.

## In production
- The usual slowness: a missing index, N+1 queries from an ORM, deep `OFFSET` paging.
- Races (double bookings, lost updates) show under load, never in one-user tests.

## Teaching order
1. A first database: `psql` (or the learner's client) on a local server; `CREATE TABLE` for the learner's own data, `INSERT`, `SELECT`; an error read to its line and caret (`column "x" does not exist`, a type mismatch).
2. Asking questions: `WHERE`, `ORDER BY`, `LIMIT`; NULL and three-valued logic, `IS NULL`.
3. Summaries: `GROUP BY`, aggregates, `HAVING`; `count(*)` against `count(column)`.
4. Several tables: primary and foreign keys, inner and `LEFT JOIN`; the join that multiplies rows.
5. Modelling: entities and relationships (one-to-many by a foreign key, many-to-many by a join table); normal forms to third by the update anomaly each prevents; denormalising on purpose; types for meaning (`numeric` money, `timestamptz` moments, `text`); `NOT NULL`, `UNIQUE`, `CHECK`.
6. Harder questions: subqueries, `EXISTS`, `WITH` (CTEs), window functions (`row_number()`, a running total `OVER (PARTITION BY ... ORDER BY ...)`) against `GROUP BY`, which collapses rows.
7. Changing data: `UPDATE` and `DELETE` with `RETURNING`, the `WHERE` tried as a `SELECT` first; upsert (`ON CONFLICT`; the standard's `MERGE`); a migration on a live table: add the column, backfill in batches, then `NOT NULL`.
8. Indexes: the B-tree as sorted keys pointing at rows; `EXPLAIN ANALYZE` node by node, estimated against actual rows; nested loop, hash and merge joins; selectivity; composite indexes and the leftmost prefix; expression indexes; the cost to every insert.
9. Transactions: `BEGIN`, `COMMIT`, `ROLLBACK`; ACID letter by letter; two sessions racing: lost update and write skew, then isolation levels by what each allows; `FOR UPDATE`; a `UNIQUE` constraint as the cheapest lock; deadlocks; the whole transaction retried on 40001 or 40P01.
10. SQL from code: bind parameters (`$1`) and the injection they stop; a connection pool and its size; no transaction open across a network call; N+1 loops found in the query log, fixed by a join or `IN`; keyset paging over an index on `(created, id)` instead of `OFFSET`.
11. Operating it: `pg_dump` restored into a scratch server (a backup never restored is not one); slow statements found by `log_min_duration_statement` or `pg_stat_statements`; `lock_timeout` on every migration.

## How it runs
- [2-3] Logical order: `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`: a `SELECT` alias fails in `WHERE` (`column "d" does not exist`) but works in `ORDER BY`; an aggregate in `WHERE` fails: use `HAVING`.
- [2] `NULL = NULL` is NULL; `g <> 'a'` drops rows where `g` is NULL; `NOT IN (SELECT v ...)` matches nothing if `v` has a NULL: use `NOT EXISTS`.
- [3] Four rows, one `v` NULL: `count(*)` 4, `count(v)` 3, `avg` over three; `sum` of no rows is NULL.
- [4] An order with two items and two payments, joined to both: four rows, both sums doubled; sum each child first.
- [9] ACID: atomic (a failure midway leaves nothing), consistent (constraints hold at commit), isolated (as the level allows), durable (a commit survives a crash).
- [9] At `READ COMMITTED` two sessions read 10 seats and each write back 9: a sale lost. `SET n = n - 1` or `FOR UPDATE` fixes it; `REPEATABLE READ` aborts the second ("could not serialize access").
- [9] Write skew: two doctors each see two on call and go off; both commit under `REPEATABLE READ`; `SERIALIZABLE` aborts one for retry.
- [8] 200,000 rows: `email = '...'` uses its index; `lower(email) = '...'` scans until an index on `lower(email)` exists; `country = 'US'` (90% of rows) rightly scans; on 16, `(country, created)` cannot seek on `created` alone (18's skip scan may, when `country` has few values).

## Step notes
### 1
Need: My app created the table, yet psql says it does not exist; how do I read what the database tells me?
Show: `CREATE TABLE "Users" (...)`, as ORMs often write it, then `SELECT * FROM Users;`: on PostgreSQL 16 here,
`relation "users" does not exist`, caret under `Users` (unquoted names fold to lower case). `EXPLAIN` of a
lookup by `id` prints `Index Scan using "Users_pkey"`: the database chose how.
Explain: You state which rows; the server parses, plans and runs it, and an error names what failed and where.
Try: predict: the error for `'two'` into an integer column; build: their own first table, three rows, one
`SELECT` with `WHERE`.
### 2
Need: The list came back in insert order every time I tested; why did production shuffle it?
Show: rows 1 to 5 inserted; `SELECT id` gives 1, 2, 3, 4, 5. After `UPDATE ... WHERE id = 2`, the same query
gives 1, 3, 4, 5, 2, and `LIMIT 2` returns 1 and 3 (PostgreSQL 16 here): the update wrote a new row version
where there was room.
Explain: A table is a heap with no order; only `ORDER BY`, ending in a unique column, promises one.
Try: fix: `WHERE status <> 'done'` silently dropping rows whose status is NULL (`IS DISTINCT FROM`); predict:
the order after row 1 is deleted and inserted again.
### 3
Need: I want each customer's total and their order ids; why does PostgreSQL refuse?
Show: `SELECT customer, id, sum(total) FROM orders GROUP BY customer`: `column "orders.id" must appear in the
GROUP BY clause or be used in an aggregate function`, caret under `id`. With `count(*), sum(total), max(id)`:
ann 2, 30, 2; bob 1, 5, 3.
Explain: `GROUP BY` folds each group into one row, so each output column needs one value per group: a grouping
column or an aggregate; `WHERE` filters rows before, `HAVING` groups after.
Try: predict: `count(*)`, `count(v)` and `avg(v)` over four rows, one `v` NULL; apply: `array_agg(id)` to list
each customer's orders.
### 4
Need: Each total is right alone; why are both too big once I join the two tables?
Show: order 1: items 20 and 30, payments 10, 15 and 25. `ord JOIN item JOIN payment`: 6 rows; `sum(price)` 150,
`sum(amount)` 100, not 50 and 50. Each child summed in a subquery, then joined: 50 and 50.
Explain: A join emits a row per matching pair, so two children give items × payments rows; the aggregate then
runs over the multiplied rows.
Try: predict: `count(*)` against `count(i.ord_id)` under `LEFT JOIN` for an order with no items (here 1 and 0);
fix: a report in their schema joining two child tables, checked by counting rows before `GROUP BY`.
### 5
Need: The ORM let me store money as a float; what is the harm?
Show: `SELECT sum(0.10::float8), sum(0.10::numeric) FROM generate_series(1,10)`: `0.9999999999999999` against
`1.00`. With `CHECK (balance >= 0)`, an overdraft is refused: `violates check constraint
"account_balance_check"`.
Explain: Types and constraints are checked on every write from every program, so one forgetful code path cannot
let a bad row in.
Try: decide: types and constraints for their two core tables, one line each; explain: the update anomaly from
copying a customer's address onto every order, and the normal form that removes it.
### 6
Need: `max(at)` gives each customer's latest date; how do I get that whole order row?
Show: `WHERE row_number() OVER (...) = 1` fails: `window functions are not allowed in WHERE`. Computed in a CTE as `rn` (`PARTITION BY customer ORDER BY at DESC`), then `WHERE rn = 1`: ann's order 5, bob's
4. `sum(amount) OVER (PARTITION BY customer ORDER BY at)`: running 10, 40, 60 and 5, 12, every row kept.
Explain: A window function computes over related rows without folding them, after `WHERE`; to filter on it,
compute it in a CTE first.
Try: build: their top three per group; predict: `rank()` against `row_number()` for two orders at the same time.
### 7
Need: Adding a column to our biggest table took the site down for a minute; isn't `ALTER TABLE` instant?
Show: 1M orders. A's open transaction has read the table; B runs `ALTER TABLE ... ADD
COLUMN note text`; C, a 0.1 ms key lookup, waits until A commits (4.0 s here; `pg_blocking_pids`: C behind B, B behind A). With
`SET lock_timeout = '200ms'`, B fails `canceling statement due to lock timeout`; C takes 1 to 3 ms.
Explain: `ALTER` needs the table's exclusive lock, and every later query queues behind it while it waits.
Try: apply: their next migration with `lock_timeout` and a retry; predict: `ADD COLUMN ... DEFAULT 'EUR'`
against `DEFAULT clock_timestamp()` on 1M rows (here 1.8 ms; 1.4 to 3.2 s, a rewrite).
### 8
Need: Fast in development, seconds in production: what did the database actually do?
Show: 1M orders. `EXPLAIN (ANALYZE, BUFFERS) ... WHERE customer_id = 4242`:
Parallel Seq Scan, about 10,000 buffers, 35 to 40 ms; after `CREATE INDEX`, 11 buffers, 0.1 ms. By `status`: 5% of rows use the index, 25 to 55 ms; 95% scan, 140 to 330; forced onto the index, no faster (170 to 420).
Explain: A B-tree keeps values sorted, pointing at rows, so a rare value costs a few pages; the planner
estimates rows from statistics, and for most of a table reading it all is cheaper.
Try: predict: `lower(email) = ...` with an index on `email` only (here 239 against 0.06 ms); explain:
their slowest query's plan node by node, estimated against actual rows.
### 9
Need: Two customers bought the last seat at once and both got tickets; I used a transaction, so how?
Show: pgbench, 8 clients × 1,000 sales, 10,000 seats. A script reads (`\gset`), then writes `:left_n - 1`: about 8,850 left, some 6,850 sales lost silently. `SET left_n = left_n - 1`, or the read `FOR UPDATE`: 2,000. Under `REPEATABLE READ`, about 6,500 fail with 40001, `could not serialize access`.
Explain: Under READ COMMITTED two transactions read the same value and both write back; arithmetic in the
`UPDATE`, or a row lock on read, makes the second wait for the first.
Try: predict: sessions updating rows 1 then 2 and 2 then 1 (here after `deadlock_timeout`, 1 s: `deadlock detected`); fix: their
own race, run in parallel by a script, exactly one winner.
### 10
Need: Page 1 of our feed is instant and page 5,000 crawls; why, with the same query?
Show: 1M orders, index on `(created, id)`. `ORDER BY created DESC, id DESC LIMIT 20 OFFSET
20`: 0.06 ms; `OFFSET 900000`: 114 to 271 ms, 900,020 index entries read. `WHERE (created, id) < ($1, $2)` with the
last row's values: 0.07 ms, 4 buffers.
Explain: `OFFSET n` finds and discards n rows; a keyset condition seeks straight past the last row seen.
Try: fix: an N+1 endpoint of theirs, counted in the query log before and after; predict: requests a second
when 10 pooled connections each stay in a transaction across a 2 s call to another service (pgbench with `\sleep 2 s` inside: 5.0, ten `idle in transaction`).
### 11
Need: We take a nightly `pg_dump`; are we safe if the server dies?
Show: database `shop` owned by role `app`, with a `GRANT` to `reporting`; `pg_dump -Fc`, `pg_restore` into a
fresh `initdb` cluster: `role "app" does not exist` (and `reporting`), exit 1; rows back,
owned by `postgres`, grant gone. Roles belong to the cluster (`pg_dumpall --globals-only`; PostgreSQL docs).
Explain: A backup is proved by a timed restore into an empty server with the application working on it.
Try: build: a restore drill for their database with a check query; apply: `log_min_duration_statement` for a
day, the slowest statement explained.

## Believable numbers
- [7-10] PostgreSQL 16 here (2 cores, data in memory, November 2026): 1M orders (`id` key, `customer_id` of 100,000, `email`, `status` 95% one value, `created`, `total`) fill 81 MB, their primary key 21 MB; 5,000 rows scan in 0.3 ms: seconds on a few thousand rows is never a missing index.
- [8] Writes: 1M rows in one `INSERT`, 3.1 s with a primary key, 10.2 s with four more indexes; one index built
  in 0.5 to 1.4 s.
- [9] One hot row, 8 pgbench clients: commits take turns, 350 to 3,600 a second here on two days.

## Go deep, leave for later
- Deep steps: 4, 7, 8, 9 (a join multiplies rows before the aggregate sums them; a migration's lock queues every reader; indexes judged by plans; transactions racing).
- Later: optimiser internals, MVCC and `VACUUM`, replication and sharding (scaling-data), stored procedures, views, roles and `GRANT`, `jsonb`, full-text search, table partitioning, partial indexes.

## Never omit
- [8] Data big enough for a missing index to show in the plan.
- [9] Two sessions racing in every transaction lesson.
- Look up when planned: the database and version (skip scan, `MERGE`), the default isolation level, the migration tool.

## Wrong beliefs
- [2] "NULL = NULL is true" (it is unknown; test with IS NULL).
- [2] "Rows come back in the order they were inserted" (no order is promised without ORDER BY).
- [8] "An index always makes queries faster" (it speeds some reads, adds cost to writes, may rightly go unused).
- [9] "A transaction protects me from every race" (below serializable, lost updates or write skew can happen; Oracle's "serializable" allows write skew).
- [10] "Escaping quotes prevents injection" (parameters do; a column name cannot be one: pick it from a fixed list).

## Failures to diagnose
- [8] A slow query: the plan shows a sequential scan of a big table.
- [9] A lost update: two users at once; the application reads, computes, writes back.
- [9] A deadlock: two transactions lock the same rows in opposite order; one is aborted ("deadlock detected").
- [7,11] A migration that stalls a busy table: `ALTER TABLE` waits behind an open transaction; every later query queues behind it.
- [10] A deep page that gets slower with its number: `OFFSET` reads and discards every earlier row.
- [10] An N+1 page: one query for the list, then one per row from an ORM loop that hides the SQL.
- [4] Totals too large after adding a second join: each child multiplied the other's rows.

## Practice and project
Guided: predict a plan, then run `EXPLAIN ANALYZE`. Alone: business questions. Project: the operation in the learner's application where two users race for one row; finish line: a script runs the race and exactly one wins; five slow queries' plans saved before and after.

## Mastery ladder
- Use: answer ten business questions in correct SQL.
- Explain: show a friend, with the plan, why `lower(email) = ...` skips an index on `email`.
- Build: the project above.
- Design: choose and defend schema, constraints and indexes for a stated workload.

## Words to own
[1] table, schema; [2] NULL, three-valued logic; [3] aggregate; [4] primary key, foreign key, join;
[5] constraint, normalisation, denormalisation; [6] CTE, window function; [7] upsert, migration;
[8] index, B-tree, query plan, selectivity; [9] transaction, isolation level, lost update, deadlock, serialization failure, (ACID), (race condition),
(write skew); [10] SQL injection, bind parameter, connection pool, N+1 query,
keyset pagination; [11] slow-query log
