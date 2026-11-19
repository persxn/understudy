# advanced-data-structures: range queries with updates for contest problems
kind: skill
aliases: segment tree, fenwick tree, binary indexed tree, sparse table, monotonic stack, lazy propagation
needs: dsa-core-techniques, graphs-and-trees
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/book/book.pdf ch. 8.2-8.3 (nearest smaller, window minimum), 9 (static queries, Fenwick,
  segment tree), 18.2 (subtrees and paths), 28.1 (lazy propagation); cses.fi/problemset Range Queries, Tree
  Algorithms, Sliding Window, Advanced Techniques, Advanced Graph Problems (names; task pages of steps 5 and
  10-12 read for their limits);
  usaco.guide/gold, /plat (module order, offline sweeps); atcoder.jp/contests/practice2 (B, J, K, L);
  runs with g++ in /tmp (overlap, node index, missing push, index 0, inversion count); g++ 13 and
  Python 3.13 runs, 2026-11-19 (step notes, numbers; rerun independently, reviews/VA.md)
unverified: step order past 8, practice counts and rating bands are judgement

## Promise
Name the queries and updates a problem asks for, pick the lightest structure that supports both, write it from
memory, and stress-test it against a plain array.

## The one idea
Precompute answers for chosen blocks, so any range is a few blocks. Picture: a bank keeps monthly totals, so a
year is twelve additions. Where it breaks: blocks must combine by an associative operation, and overlapping
blocks are allowed only when counting twice changes nothing (min yes, sum no).

## In production
- Contests: the data structure is often the whole problem once the observation is made.
- Work: totals kept per block, so a range question over a time series touches few blocks.
- A skill book whose programs run: plan `run: cpp`.

## Teaching order
1. Monotonic stack: nearest smaller value to the left, each index pushed and popped once (amortised O(n),
   dsa-core-techniques 8); Nearest Smaller Values.
2. Monotonic `deque` of indices (cpp-for-contests 4): window minimum in O(n), the front expires by index;
   Sliding Window Minimum (n up to 10^7, generated input: no log factor fits).
3. Sparse table: `st[k][i]` = min of 2^k values from i, O(n log n) build, O(1) query by two overlapping blocks
   of length 2^k, k = floor(log2 length); only idempotent operations (min, max, gcd, and, or); Static Range
   Minimum Queries.
4. Fenwick tree: `i & -i`, point add, prefix sum, 1-indexed; Dynamic Range Sum Queries; range add with point
   query by storing differences: Range Update Queries.
5. Fenwick over values: inversions; compression (dsa-core-techniques 4) of every value the input will ever
   use (initial values, updates and query ends, all read first); counts in a value range: Salary Queries.
6. Segment tree: recursive on nodes 1, 2v, 2v+1, a merge function with an identity element; Dynamic Range
   Minimum Queries; nodes with several fields (sum, best prefix, best suffix, best): Subarray Sum Queries.
7. Walking the tree in O(log n): first index whose value is at least x (Hotel Queries), k-th remaining element
   from counts (List Removals), AtCoder practice2 J.
8. Lazy propagation: a pending tag per node, pushed down before descending, two tags composed into one; Range
   Updates and Sums, Polynomial Queries, AtCoder practice2 K and L.
9. Offline queries sorted by right end: Distinct Values Queries (each value counted only at its last position).
10. Trees as arrays: entry and exit times make a subtree one range; Subtree Queries, Path Queries (subtree range
   add, point query: step 4); any path via the lowest common ancestor (graphs-and-trees 10).
11. Union-find (graphs-and-trees 11) extended: data at the leader; deletions answered in reverse time (Network
   Breakdown); union by size without path compression, links labelled by day (New Roads Queries).
12. Choosing from the operations (static or changing, invertible or idempotent, online or offline) on mixed
   sets: Pizzeria Queries, Increasing Array Queries.

## Judged by
- Are the query and the update written down before a structure is chosen, and is it the lightest one?
- [6] Is the merge associative, with an identity, checked on a one-element node?
- [6] Is the array 4n for the recursive tree, and [4] the Fenwick 1-indexed?
- Do sums and counts that can pass 2^31 use `long long`?
- Does a stress test compare it with a plain array on random operations?
- [8] Does every function that descends push down first, and is tag composition tested in both orders?

## Step notes
### 1
Need: My nearest-smaller loop passed random tests; why does it time out, and isn't a `while` inside a `for`
just as quadratic?
Show: n = 2·10^5, scan left from each index as the brute. Random values: about 2.5·10^6 steps; decreasing:
2·10^10, several seconds on any laptop or judge (at best a few 10^9 comparisons a second) against a 1 s limit;
the stack: 4·10^5 pushes and pops either way. A stack popping only on `>`, stressed on values 1 to 3: caught
within a few tests, e.g. 2 2 3 gives 0 1 2, truth 0 0 2.
Explain: An index not smaller than a later one can never again be an answer, so it is popped for good: each
index is pushed once and popped at most once.
Try: predict: the brute's steps on increasing, then decreasing input, then run; fix: the `>` pop, by their
own stress test.
### 2
Need: Sliding Window Minimum has n = 10^7; my `multiset` window is only O(n log n), so why is it too slow?
Show: CSES's generator, 10^7 values. Window 1000: multiset over a second (2·10^7 tree operations), deque
about a tenth; window 10^6: multiset tens of seconds (each step walks a million-node tree that misses the
cache), deque unchanged; a heap that pops expired tops, a few tenths either way.
Explain: The deque holds indices with values rising front to back; a newcomer pops every larger value at the
back, and the front leaves when its index leaves the window.
Try: fix: a deque of values (failure [2]), the failing window found by stress test; apply: window maximum by
one changed comparison, matching a brute on 10^4 random cases.
### 3
Need: xor is associative, even invertible; why does a sparse table give min in O(1) but not xor or sum?
Show: random arrays of length ≤ 20, values 1 to 100, 10^4 queries from two blocks of length 2^k, against a
loop: min, gcd, or, lcm: 0 wrong; sum: 10,000 wrong; xor: about 98% wrong.
Explain: The two blocks overlap (they are one block at a power-of-two length), so the middle is taken twice:
harmless when x op x = x, fatal for sum and xor.
Try: decide: max, product, lcm, count of distinct values: O(1) by sparse table or not, then stress each;
build: Static Range Minimum Queries with `__lg`, stating its memory at n = 2·10^5.
### 4
Need: I copied `i += i & -i`; what does `t[i]` hold, and why must the index start at 1?
Show: at n = 16, add(5) visits 5 6 8 16; sum(7) reads 7 6 4, the blocks (6,7], (4,6], (0,4]; add(0) prints
0 0 0 0 … forever.
Explain: `t[i]` holds the sum of (i − lowbit(i), i]; a prefix sum peels off lowbit to 0, an update climbs to
every block covering i; lowbit(0) is 0, so index 0 never moves.
Try: predict: the indices of add(11) and sum(13) at n = 16, then print them; build: Range Update Queries, +x at
a and −x at b+1, checked against an array on random operations.
### 5
Need: Salary Queries has values to 10^9; I compressed them, so why are some counts off by one?
Show: stress test against a counting loop at test 10: salaries 6 4 10, `! 3 5`, `? 1 5`: brute 2, compressed
from initial values 1 (`lower_bound` filed the new 5 under 6). Compressing updates and query ends: 0 wrong.
Explain: Compression lists every value ever looked up, so read all input first; a Fenwick tree over those
indices then counts values in a range.
Try: build: inversions by a Fenwick tree over values, against O(n²), then 2·10^5 reversed (`int` printed
−1,474,936,480 here); fix: their own compression from initial values.
### 6
Need: My segment tree passes my small stress tests; why a runtime error on the judge?
Show: recursive min tree in a global `long long t[2*MAXN]`, MAXN = 2·10^5, against a loop: n = 6 (top node
13), 1000 and 10^5 answer right, the array being sized by MAXN. n = 1.5·10^5 reaches node 524,273: a segfault
when the tree is the last global; with the input array declared first (g++ put it after the tree), no crash,
17,898 inputs overwritten. `-fsanitize=address` names the write either way.
Explain: Node v merges its children 2v and 2v+1; unless n is a power of two the numbering skips, so leaves
reach near 4n. The identity answers ranges outside the query.
Try: build: Subarray Sum Queries, four fields, merge and identity on paper first, stressed against O(n²);
predict: the top node for n = 5 to 8 (9, 13, 13, 15).
### 7
Need: Hotel Queries wants the first hotel with x free rooms; binary search over range maxima works, so why walk?
Show: n = m = 2·10^5: binary search visits 7.3·10^7 nodes, a few tenths of a second; walking from the root
(left if its max ≥ x) visits 7.4·10^6, a few hundredths; same answers. Ten times fewer visits: log n, not log² n.
Explain: The left child's max already says whether the answer lies left, so one root-to-leaf path decides:
O(log n), not O(log² n).
Try: build: List Removals walking on counts, against `vector::erase`; apply: AtCoder practice2 J with
`max_right`, accepted.
### 8
Need: I can do lazy "add"; Range Updates and Sums mixes "add" and "set": what does a node keep?
Show: a node's tag is (set, then add), pushed in that order; stress test against an array. A "set" that keeps
the node's pending add failed: add 5 to [1,2], set [1,2] to 1, set [1,2] to 4, sum [1,1] = 9, brute 4.
Shrunk by hand: add 5, set 1 already reads 6 for 1. The fixed version: 0 wrong in 20,000 tests.
Explain: A tag is an update the children have not seen; a second one composes with it: set after add erases
the add, add after set raises the set value; push down before any descent.
Try: decide: for practice2 K (x → bx + c), two tags composed and the new sum, before code; build: Polynomial
Queries, the tag a first term and step, saying what the right child receives.
### 9
Need: Distinct Values Queries: 2·10^5 queries, each maybe the whole array; can anything beat counting each?
Show: n = q = 2·10^5, random. Counting each range: 1.3·10^10 steps, about a minute on a laptop or a judge
(scattered reads, a few 10^8 a second). Sorted by right end with a Fenwick tree of last-occurrence marks:
6·10^6 steps, hundredths. On 1 2 1 3 2 at r = 5 the marks sit at 3, 4, 5: [2,5] has 3.
Explain: With r fixed, only each value's last occurrence up to r matters; moving its mark there keeps "marks
in [l, r]" equal to the distinct count.
Try: explain: why this fails when each query is xored with the last answer; build: Distinct Values Queries,
stress-tested against the counting loop.
### 10
Need: Subtree Queries changes values and sums subtrees; my DFS per query is right, so why so slow?
Show: a chain of 2·10^5, half updates, half subtree sums: a walk per query, 10^10 steps, over a minute; entry
times and a Fenwick tree, hundredths. Iterative DFS: a recursive one crashed on this chain here (8 MB stack).
Exit time stored one too far: values 8 6 8 7, edges 1-2, 2-3, 1-4 in that order: subtree of 2 = 21, brute 14.
Explain: DFS numbers a node, then all its descendants, before leaving it, so a subtree is the range
[tin, tout].
Try: build: Path Queries, a change at s added to s's subtree range, the root sum read at one point; predict:
tin and tout of a 7-node tree they draw, then print them.
### 11
Need: Union-find only joins; how do I handle deleted cables, or "from which day are a and b joined"?
Show: New Roads Queries by union by size, links labelled with their day, the answer the largest label on the
path: matches a brute force. Add path compression: roads 2-1, 4-3, 1-4, 3-2 on days 1 to 4; 2 and 3 joined from
day 3, compressed answers 2 or 1 (by which root wins a tie), never 3: day 4's find relinked 3 or 2.
Explain: Run time backwards, adding deleted cables as unions; keep size, sums or the component count at the
leader. Compression relinks a node past the day that mattered.
Try: build: Network Breakdown in reverse, against BFS on random small cases; explain: why union by size alone
keeps paths O(log n) (done: a node's set at least doubles whenever its root changes).
### 12
Need: For a new problem, how do I choose a structure without trying each?
Show: n = q = 2·10^5, half point updates, half range sums: Fenwick about 0.01 s, bottom-up tree of 2n 0.02,
recursive tree of 4n 0.06 (call overhead), a plain array summing each range 2 s (6.7·10^9 additions, even
vectorised). Same answers; a laptop or a judge is within a factor of two or three.
Explain: List the operations: static or changing, invertible (Fenwick), idempotent (sparse table), neither
(segment tree), online or offline; take the lightest that supports all.
Try: decide: Pizzeria Queries as trees of p − i and p + i, and why min needs a segment tree; decide: Increasing
Array Queries: what the right-to-left sweep, the monotonic stack and the range assignment each hold.

## Believable numbers
- Run here (g++ -O2, Python 3.13, shared two-core machine, November 2026; a laptop or judge is the same order):
  2·10^5 Fenwick operations, hundredths of a second in C++, a second in Python; a recursive segment tree about
  3 times a Fenwick tree. A tight C++ loop adds about 3·10^9 numbers a second; scattered access, about 3·10^8.
- [2,3] Memory: a sparse table is n log n values (n = 2·10^5: about 14 MB of `int`; n = 10^7: about 1 GB).
- [5] Counts pass 2^31 fast: inversions reach n²/2, 2·10^10 at n = 2·10^5.

## Go deep, leave for later
- Deep steps: 6, 8, 9, 12 (what a node stores and how it merges; how two tags compose; reordering queries
  offline; choosing from the operations: where adapting, not copying, is learned).
- Later: persistent trees (Range Queries and Copies), Mo's algorithm and square root decomposition,
  small-to-large merging (Distinct Colors), sparse segment trees, treaps (Cut and Paste), 2D trees (Forest
  Queries II), segment tree beats.

## Never omit
- Every structure starts from the brute force it replaces, kept for the stress test.
- Cost per operation times operations, checked against the limits.

## Wrong beliefs
- [1-2] "The inner `while` makes it quadratic" (each index enters and leaves once: O(n) in all).
- [3] "A sparse table answers sums in O(1)" (overlap counts twice: run, 1 2 3 4 5 gives 24 for 15; xor fails
  too; sums need disjoint blocks, O(log n), or plain prefix sums).
- [4] "A Fenwick tree does range minimum with updates" (prefix minima only, and only while values only fall:
  min cannot be undone).
- [6] "2n is enough for a segment tree" (for the iterative bottom-up one; the recursive 1, 2v, 2v+1 numbering
  reaches nearly 4n: run, n = 6 uses node 13).
- [8] "Tags can be applied in any order" (they compose: an assignment arriving at a node discards that node's
  pending addition, while an addition arriving after an assignment adds to the assigned value).
- [9] "Queries must be answered in input order" (read all, sort, answer in stored order, unless forced online).
- [11] "Union-find can remove an edge" (it cannot; reverse time so removals become unions).
- [12] "A segment tree is always the safe choice" (run: about 3 times a Fenwick tree's time; at n = 10^7 only
  O(n) fits).

## Failures to diagnose
- [6] Array of 2n: out of bounds; a `vector` of 2n crashed here from n = 6 (a glibc abort or a segfault), a
  global one may corrupt its neighbour silently; found by `-D_GLIBCXX_DEBUG` or the sanitizer.
- [8] Missing push down: run, add 5 to [0,3], then the sum of [1,2] is 0 where 10 was due.
- [4] Fenwick called at index 0: `i += i & -i` stays 0, an endless loop, time limit.
- [5] Inversions in `int`: a reversed array of 2·10^5 has 19,999,900,000.
- [5] Salary Queries compressed from initial values only: an updated salary has no index.
- [2] A deque of values that pops equal values too: when the leaving value equals the front, it is a newer copy
  that goes (values 1 1 2, window 2: 1 2, truth 1 1). Indices never need the question.
- [10] Exit time off by one: a subtree range that misses its last node, or takes in the next one.
- [11] Path compression in New Roads Queries: the labelled links are rewritten and the days lost (run: roads
  2-1, 4-3, 1-4, 3-2, query 2 3 answers 2 or 1, not 3).

## Practice and project
Per step: its CSES problems, then about ten Codeforces problems tagged data structures from your rating to 300
above. Project: a library (sparse table, Fenwick, lazy segment tree, union-find), each stress-tested; finish line:
AtCoder Library Practice Contest B, J, K and L accepted with it.

## Mastery ladder
- Use: solve the chapter's CSES problems with a given structure.
- Explain: show on paper why a sparse table may overlap for minimum but not for sum.
- Build: the library and its finish line above.
- Design: for a new problem, list its operations and defend the lightest structure that supports them.

## Words to own
[1] monotonic stack; [2] monotonic deque; [3] sparse table, idempotent; [4] Fenwick tree, lowbit;
[5] inversion; [6] segment tree, merge function, identity element; [7] tree
walk, order statistic; [8] lazy propagation, lazy tag, push down; [9] offline query; [10] Euler tour, entry
time, exit time; [11] reverse time; [12] online query
