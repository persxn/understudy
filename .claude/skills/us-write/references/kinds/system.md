# Teaching how a system works

**At the end of a chapter** the reader can take a situation they have not seen (a page fault, a packet to a new host, two transactions on one row) and say, in order, what each part does and why, and predict the outcome before checking: not a list of parts, an order of events they can replay.

**The usual arc.** A puzzle from experience (why does the second `ping` answer faster than the first? why did my update vanish?) → the parts involved and what each one *knows* at the start → the order of events, one step at a time, built up as a diagram or a table → the same trace with one thing changed (the cache is cold, the lock is taken) → the design reason: what problem this arrangement solved, and what it costs → a new situation the reader traces alone.

**The real thing** is a trace by hand, a small experiment, or a diagram built up in steps. Weak: "ARP maps IP addresses to MAC addresses. The ARP cache stores mappings." Better: Host A (192.168.1.10) wants to send to B (192.168.1.20) on the same network. Step 1: A checks its ARP cache; empty. Step 2: A broadcasts "who has .20?" to every machine. Step 3: only B answers, with its MAC address. Step 4: A stores it and sends the packet. Then the experiment: `ip neigh` before and after a `ping`; then the question: what happens when B's network card is replaced? A table, one row per step, beats a page of definitions.

**Three exercise types.**
- *Predict*: "Under READ COMMITTED, two transactions each `SELECT` balance 100, compute 110 in the program, write `SET balance = 110` and commit. What is the balance, and where did a deposit go? Would `SET balance = balance + 10` change the answer?" Reason it out, then (where possible) run it in two `psql` windows.
- *Trace it*: "Fill in the table for a lookup of `www.example.org` with an empty resolver cache: who asks whom, what each answers."
- *Decide the design*: "Your service reads a config value on every request. Cache it, or not? What breaks in each case?"

**Mark with a risk note** numbers (latencies, default buffer and page sizes, timeouts), behaviour that differs between implementations (Linux against Windows schedulers, PostgreSQL against MySQL isolation defaults), claims about what a standard (an RFC, the SQL standard) requires, and any history or attribution.

**Usual failures of generated material, and the cure.**
- *A list of parts with no order of events*: "the kernel, the scheduler, the MMU, the TLB." Every part enters the text at the moment it acts in a trace.
- *Boxes without time*: number the arrows, or use a sequence figure (`us-draw`).
- *Analogies that never break*: say where the post-office picture of routing stops being true (packets can be dropped, reordered, take different paths).
- *No experiment*: when the machine can show it (`strace`, `ip`, `EXPLAIN`, a 20-line simulation), show it.
