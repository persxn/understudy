## 6.2 Two people, one row: the lost update

### Two deposits, one missing

Mia has 100 in her account. At 9:00 one morning two things happen in the same second: her employer's payroll job pays her 10, and a friend pays back 10 she owed through the app. Your code handles both, and your code is simple. It reads the balance, adds 10, and writes the new balance back:

```text
balance = SELECT balance FROM accounts WHERE id = 1     -- 100
new_balance = balance + 10                              -- 110, worked out in the program
UPDATE accounts SET balance = new_balance WHERE id = 1
```

Two copies of this code run at once, one for each deposit, each with its own connection to the database. Both finish. Both log "deposit OK". No error appears anywhere. At 9:01 Mia's balance is 110, not 120.

Every statement did exactly what it says, nothing crashed, nothing was rolled back, and still 10 has vanished. This section is about where it went: what PostgreSQL does, step by step, when two sessions touch one row, why it was built to do that, and three ways to stop it, each with its price.

### The kitchen whiteboard

Picture the whiteboard in an office kitchen where the coffee fund is kept. It says 100. Two colleagues each put 10 in the tin. Each walks to the board, reads "100", goes back to their desk to work out the sum, comes back, wipes the number and writes "110". There is one marker, so if they arrive together one waits for the other to finish writing. The wait does not help. The second person writes the 110 they worked out at their desk, from a 100 that was no longer on the board.

That is the whole bug in everyday form: the reading, the working-out somewhere else, the single marker, the useless wait. All four carry over to PostgreSQL.

The picture stops being true in three places. On the whiteboard there is one number; PostgreSQL does not change a row in place. A writer makes a new version of the row beside the old one, and until the writer commits, everyone else keeps reading the old version, so a reader never waits for the marker at all. Second, the marker is not handed back when the writer stops writing; it is held until the writer's whole transaction ends. Third, the database can be cleverer than a colleague: in one variation below it notices the board changed under you and refuses to let you write. Each difference shows up in the trace.

### The parts, and what each one knows

You need one table with one row:

<!-- code: id=lost-update-setup mode=fragment -->
```sql
CREATE TABLE accounts (id int PRIMARY KEY, owner text NOT NULL, balance int NOT NULL);
INSERT INTO accounts VALUES (1, 'Mia', 100);
SHOW transaction_isolation;
```

```text
CREATE TABLE
INSERT 0 1
 transaction_isolation 
-----------------------
 read committed
(1 row)
```

Everything below was run on PostgreSQL 16, in a database called `bank`, with two `psql` windows side by side: window A (the payroll deposit) and window B (the friend's deposit). Each window is its own *session*, with its own connection and its own server process. Neither knows what the other is doing except through the table.

Both sessions work in transactions. `BEGIN` starts one, `COMMIT` ends it, and everything in between happens completely or not at all. While a transaction is open, `psql` shows a star in its prompt, `bank=*#`. Other sessions cannot see a transaction's changes until it commits.

<!-- teaches: read-committed = isolation level, READ COMMITTED -->
The last part is the rule that decides what each statement sees. It is called the *isolation level*, and `read committed` above is PostgreSQL's default. READ COMMITTED means: each statement sees the data that was committed at the moment that statement started. Not when the transaction started; each statement takes a fresh look.

### Walking the lost update, one step at a time

Type these into the two windows in the order of the step numbers in the comments. The steps go back and forth between the windows.

<!-- code: id=lost-update-a mode=fragment -->
```sql
-- window A
BEGIN;                                            -- step 1
SELECT balance FROM accounts WHERE id = 1;        -- step 3
UPDATE accounts SET balance = 110 WHERE id = 1;   -- step 5 (the program worked out 100 + 10)
COMMIT;                                           -- step 7
```

<!-- code: id=lost-update-b mode=fragment -->
```sql
-- window B
BEGIN;                                            -- step 2
SELECT balance FROM accounts WHERE id = 1;        -- step 4
UPDATE accounts SET balance = 110 WHERE id = 1;   -- step 6 (it also worked out 100 + 10)
COMMIT;                                           -- step 8
```

Here is what window B showed, complete:

```text
bank=# BEGIN;
BEGIN
bank=*# SELECT balance FROM accounts WHERE id = 1;
 balance 
---------
     100
(1 row)

bank=*# UPDATE accounts SET balance = 110 WHERE id = 1;
UPDATE 1
bank=*# COMMIT;
COMMIT
bank=# 
```

On paper it looks like nothing happened. What the transcript cannot show is time: after step 6, window B printed nothing and gave no prompt back. It sat there. Only when you typed `COMMIT;` in window A did `UPDATE 1` appear in window B. The table puts the time back:

| Step | Window A | Window B | The row, and who waits |
|---|---|---|---|
| 1 | `BEGIN` | | committed balance 100 |
| 2 | | `BEGIN` | committed balance 100 |
| 3 | `SELECT` gives 100 | | 100; reading takes no lock |
| 4 | | `SELECT` gives 100 | 100; both programs now hold the number 100 |
| 5 | `UPDATE ... 110` gives `UPDATE 1` | | committed version still 100; A's new version 110 exists but is uncommitted; A holds the row's lock |
| 6 | | `UPDATE ... 110`: no answer | B finds A's uncommitted version and waits for A to finish |
| 7 | `COMMIT` | `UPDATE 1` appears | 110 is committed; B wakes, takes the newest version and writes its 110 over it |
| 8 | | `COMMIT` | committed balance 110; one deposit is gone |

<!-- teaches: row-lock = row lock, waiting for a transaction -->
Step 6 is the interesting one. Session B goes to update row 1 and finds that another transaction has already written a newer version of it and has not finished. B cannot know yet whether A will commit (then the newer version is the truth) or roll back (then 100 is still the truth). So it does the only safe thing: it waits for A's transaction to end. This waiting is what a *row lock* is in practice: not a padlock you can see, but "a transaction that changes a row makes every other writer of that row wait until it commits or rolls back". That is the second difference from the whiteboard: the marker is held until the transaction ends, not until the statement ends.

You can watch the wait from a third window while B is stuck:

<!-- code: id=lost-update-watch mode=fragment -->
```sql
SELECT pid, state, wait_event_type, pg_blocking_pids(pid) AS blocked_by
FROM pg_stat_activity
WHERE datname = 'bank' AND pid <> pg_backend_pid();
```

```text
  pid  |        state        | wait_event_type | blocked_by 
-------+---------------------+-----------------+------------
 32169 | idle in transaction | Client          | {}
 32312 | active              | Lock            | {32169}
(2 rows)
```

Session 32169 (window A) is "idle in transaction": its transaction is open and it is waiting for you to type. Session 32312 (window B) is waiting on a lock, blocked by 32169. Your numbers will differ.

In the same third window, a plain `SELECT balance FROM accounts WHERE id = 1;` answered `100` at once, without waiting. That is the first difference from the whiteboard, live: A's 110 is not committed, so other sessions read the old version, and reading does not queue behind the writer.

Step 7 is where the deposit is lost. A commits; its version, 110, becomes the committed one. B wakes up. Under READ COMMITTED, B now looks at the newest committed version of the row, checks that it still matches `WHERE id = 1` (it does), and applies its `SET`. Its `SET` says `balance = 110`. The number 110 was worked out in B's program from the 100 it read at step 4, which stopped being true at step 7. The database has no way to know where that 110 came from; to the database it is a constant, and B is entitled to write a constant.

<!-- teaches: lost-update = lost update -->
This is called a *lost update*: two transactions read the same value, each computes a new value from it, and the second write wipes out the first. Notice what it is not. It is not a crash, a deadlock or an error. Every message was a success. That is why it is so expensive to find in a real system.

Now run the same statements without `BEGIN` and `COMMIT`. Each statement is then its own transaction, committed at once, so at step 6 there is nothing to wait for: B prints `UPDATE 1` immediately, and the balance is still 110. The wait was never the cure. It only made sure B did not write on top of something that might be rolled back.

### Change one thing: let the database do the sum

Reset the balance to 100 and do the same walk with one change in both windows:

<!-- code: id=lost-update-plus mode=fragment -->
```sql
UPDATE accounts SET balance = balance + 10 WHERE id = 1;   -- steps 5 and 6
```

Window B looks the same as before until step 7, when A commits. Then:

```text
bank=*# UPDATE accounts SET balance = balance + 10 WHERE id = 1;
UPDATE 1
bank=*# SELECT balance FROM accounts WHERE id = 1;
 balance 
---------
     120
(1 row)

bank=*# COMMIT;
COMMIT
```

| Step | Window A | Window B | The row, and who waits |
|---|---|---|---|
| 1 to 4 | `BEGIN`, `SELECT` gives 100 | `BEGIN`, `SELECT` gives 100 | 100 |
| 5 | `UPDATE ... balance + 10` | | A's uncommitted version: 100 + 10 = 110 |
| 6 | | `UPDATE ... balance + 10`: no answer | B waits for A |
| 7 | `COMMIT` | `UPDATE 1` appears | B takes the newest version, 110, and works out 110 + 10 = 120 |
| 8 | | `COMMIT` | committed balance 120 |

Exactly the same machinery ran: B waited, then took the newest committed version. The only difference is when the arithmetic happens. In the first walk the sum was done in the program, at step 4, before the wait. Here `balance + 10` is part of the statement, and the statement finishes its work after the wait, on the row as it is then. The stale number never enters the picture.

There is one stale number left, though. B's SELECT at step 4 still said 100. If B's program printed "your new balance is 110" from that, the receipt is wrong even though the account is right. The database protected the row, not your program's variables.

This cure is free, and you should use it whenever the new value can be written as an expression of the old one: counters, stock levels, totals. It stops working the moment your program has to *decide* something with the value before writing, such as "refuse the withdrawal if the balance would go below zero" or "ask the fraud service". Then the program needs the value in hand, and you are back to read, think, write.

### Change another thing: REPEATABLE READ refuses

Reset to 100 and walk the original, buggy version (`SET balance = 110`, worked out in the program) again, but start both transactions with a stricter isolation level:

<!-- code: id=lost-update-rr mode=fragment -->
```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;            -- steps 1 and 2, instead of BEGIN
```

<!-- teaches: repeatable-read = REPEATABLE READ, snapshot -->
Under REPEATABLE READ, a transaction does not take a fresh look with each statement. At its first statement it takes a *snapshot*: a fixed view of what was committed at that moment, and every later statement in the transaction sees that same view. Steps 1 to 6 go as before, including the wait at step 6. At step 7, A commits, and window B says:

```text
bank=*# UPDATE accounts SET balance = 110 WHERE id = 1;
ERROR:  could not serialize access due to concurrent update
bank=!# SELECT balance FROM accounts WHERE id = 1;
ERROR:  current transaction is aborted, commands ignored until end of transaction block
bank=!# ROLLBACK;
ROLLBACK
```

Follow the reasoning from B's side. B's snapshot says the balance is 100, but the row was changed by a transaction that committed after that snapshot was taken. Under READ COMMITTED, B would quietly move on to the newest version. Under REPEATABLE READ it cannot: the newest version is outside its snapshot, and writing on top of a value it is not allowed to see would break the promise of one fixed view. So PostgreSQL refuses, and the whole transaction is now dead. The prompt changes to `bank=!#`, every further statement is refused, and only `ROLLBACK` gets you out.

The deposit is not lost; it has not happened yet. B's program must start the transaction again from `BEGIN`:

```text
bank=# BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN
bank=*# SELECT balance FROM accounts WHERE id = 1;
 balance 
---------
     110
(1 row)

bank=*# UPDATE accounts SET balance = 120 WHERE id = 1;
UPDATE 1
bank=*# COMMIT;
COMMIT
```

The new snapshot sees 110, the program works out 120, and nothing is lost. Notice the order: the retry goes back to the SELECT, not just to the UPDATE, because the number read the first time was the problem.

The same error appears if both windows write `balance = balance + 10` under REPEATABLE READ: this level does not look at what your SET says, only at whether someone else changed the row after your snapshot.

### Saying it out loud: SELECT ... FOR UPDATE

The last cure takes the lock at the read instead of at the write. Reset to 100 and change the SELECT in both windows, at steps 3 and 4, under the default READ COMMITTED:

<!-- code: id=lost-update-for-update mode=fragment -->
```sql
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
```

| Step | Window A | Window B | The row, and who waits |
|---|---|---|---|
| 1, 2 | `BEGIN` | `BEGIN` | 100 |
| 3 | `SELECT ... FOR UPDATE` gives 100 | | A holds the row's lock from now on |
| 4 | | `SELECT ... FOR UPDATE`: no answer | B waits for A, before it has read anything |
| 5 | `UPDATE ... SET balance = 110` | | A's uncommitted version 110 |
| 6 | `COMMIT` | the SELECT returns 110 | lock released; B reads the newest version |
| 7 | | `UPDATE ... SET balance = 120` | B's program worked out 110 + 10 |
| 8 | | `COMMIT` | committed balance 120 |

`FOR UPDATE` tells PostgreSQL: "I am reading this row because I am going to change it." It takes the same row lock an UPDATE would take, at the moment of reading. The second reader of that kind now waits before it has a number in hand, so the number it finally gets is the committed one.

### Why not lock every read?

You might ask why PostgreSQL does not simply do this for every SELECT. The reason is the first place the whiteboard picture broke: PostgreSQL keeps versions of rows precisely so that reading and writing do not block each other. A report that reads a million rows for ten minutes does not stop any deposit, and a deposit does not stop the report. If every read took a lock that writers had to wait for, that report would freeze every account it touched for ten minutes. Most reads never lead to a write, and only you know which of your reads your program is about to use for one. So the default is fast and safe for each single statement, and you mark the reads that matter.

The same thinking explains why READ COMMITTED quietly re-reads at step 7 instead of raising an error. That choice makes one-statement changes like `balance = balance + 10` correct with no extra code and no retries, which covers a great many real updates. The price is the case you saw: when the value was worked out outside the statement, the re-read cannot help, and the database cannot tell.

Each cure, then, buys correctness with something:

| Cure | What it costs |
|---|---|
| `SET balance = balance + 10` | Nothing, but only fits when the new value is an expression of the old one |
| `SELECT ... FOR UPDATE` | Other writers wait for as long as your transaction stays open; every code path that writes the row must use it |
| `REPEATABLE READ` | Your program must catch the error (its code is `40001`) and redo the whole transaction |

### How these failures look in your own work

**Totals that come out slightly low, only in production.** No errors, no crashes, and every test passes, because tests run one request at a time. Look for a SELECT, then a computation in the program, then an UPDATE with the result as a constant. Reproduce it the way you did here, with two `psql` windows and the steps in order.

**Requests that hang.** You added `FOR UPDATE` and now some requests never finish. Run the `pg_stat_activity` query above: you will find a waiting session whose `blocked_by` points at a session that is `idle in transaction`. Some code opened a transaction, took the lock, and then went off to do something slow (call another service, wait for a user) before committing. The lock is held all that time. Keep transactions that hold locks short, and do the slow work before `BEGIN` or after `COMMIT`.

**Users see `could not serialize access`.** Someone switched to REPEATABLE READ and did not add the retry. The error is not a fault to report; it is the database asking you to try again.

### In one line each

1. Each session reads the committed balance; under READ COMMITTED reading takes no lock and never waits.
2. The first UPDATE writes a new, uncommitted version and holds the row's lock until its transaction ends.
3. A second writer of the same row waits for that transaction to commit or roll back.
4. Under READ COMMITTED it then works on the newest committed version: right if the SET computes from the row, wrong if the SET is a number your program computed earlier.
5. Under REPEATABLE READ it refuses instead, and your program retries from `BEGIN`.
6. `SELECT ... FOR UPDATE` moves the wait to the read, so the program's number is never stale.

**Check yourself**

1. Reset to 100. Both windows run the original walk under READ COMMITTED, but each UPDATE is written as `UPDATE accounts SET balance = 110 WHERE id = 1 AND balance = 100;`. Predict what window B prints after A commits, what the final balance is, and what B's program must do next.

<details>
<summary>Answer</summary>

B waits at its UPDATE as before. When A commits, B takes the newest committed version (110) and checks its WHERE again: `balance = 100` is now false, so nothing is changed and B prints `UPDATE 0`. The balance is 110, and B's deposit has not been made. The program must notice that zero rows were updated, read the balance again and try again. This is a fourth cure ("compare and set"); it only works if the program checks the row count every time.

</details>

2. Under REPEATABLE READ, window B has run `BEGIN` and its SELECT (100). Window A then runs its UPDATE and its COMMIT. Only after that does B send its UPDATE. Does B wait? What does it print?

<details>
<summary>Answer</summary>

It does not wait: there is no open transaction to wait for, because A has already committed. It prints `ERROR:  could not serialize access due to concurrent update` at once, because the row was changed by a transaction that committed after B's snapshot (taken at B's SELECT). If B had not run any statement before A committed, its snapshot would start later, it would read 110, and there would be no error.

</details>

3. Find the fault. Deposits use `SELECT ... FOR UPDATE`, then `UPDATE ... SET balance = <new value>`. Refunds of 5 use a plain `SELECT`, then `UPDATE ... SET balance = <new value>`. A deposit of 10 and a refund arrive together on a balance of 100. Give an order of steps that ends with the wrong balance, and say what it is.

<details>
<summary>Answer</summary>

Deposit: `SELECT ... FOR UPDATE` gives 100 and takes the lock. Refund: plain `SELECT` gives 100 at once, because a plain read does not wait for locks. Deposit: `UPDATE ... 110`, `COMMIT`. Refund: `UPDATE ... SET balance = 95`; the lock is free, so it writes at once, and commits. The balance is 95 instead of 105: the deposit is lost. Fix: the refund path must use `FOR UPDATE` too, or write `balance = balance - 5`.

</details>

4. Decide. A concert has a row `events(id, seats_left)`. Booking must refuse when `seats_left` is 0. Which cure would you choose, and what would you write?

<details>
<summary>Answer</summary>

The decision ("is there a seat?") can go inside the statement: `UPDATE events SET seats_left = seats_left - 1 WHERE id = 7 AND seats_left > 0;`. A second booker waits, then re-checks the WHERE on the newest version, so two people can never take the last seat. The program reads the result: `UPDATE 1` means booked, `UPDATE 0` means sold out. If booking needs more than one statement (say, also inserting a ticket row and charging a card), use `SELECT ... FOR UPDATE` on the event row inside a short transaction, and charge the card outside it.

</details>
