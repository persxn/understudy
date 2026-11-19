# Core CS: competitive programming
for: someone who writes small programs (loops, functions, arrays) in any language
leads to: rated contests (Codeforces, AtCoder, USACO), algorithmic engineering, interviews
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: usaco.guide bronze to platinum module lists (order, why C++); cses.fi/book/book.pdf
  (chapter order); cses.fi/problemset (categories); the cards' steps
unverified: hours, goals and row 7's place are judgement

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | cpp-for-contests | none | write, test and debug judged C++ fast | I/O, overflow, STL, sanitizers, stress tests | 25 | 3 Build |
| 2 | dsa-core-techniques | 1 | solve one-idea problems at the right complexity | complete search, binary search, two pointers, prefix sums, greedy | 60 | 3 Build |
| 3 | recursion-and-dynamic-programming | 2 | turn a search into states and transitions | recursive search, memoisation, DP families | 60 | 3 Build |
| 4 | graphs-and-trees | 2, 3 | model a problem as a graph | BFS, DFS, shortest paths, trees, LCA, union-find, MST | 60 | 3 Build |
| 5 | contest-strategy | 2 | turn knowledge into rating | rules, checklist, upsolving, virtuals | 20 | 3 Build |
| 6 | advanced-data-structures | 2, 4 | answer range queries with updates | sparse table, Fenwick and segment trees, lazy tags | 50 | 3 Build |
| 7 | number-theory-and-combinatorics | 3 | count modulo a prime, decide games | inverses, binomials, expectation, matrices, games | 40 | 3 Build |
| 8 | string-algorithms | 2, 3, 6 | match strings in near-linear time | hashing, prefix and Z-functions, trie, suffix array | 35 | 3 Build |
| 9 | advanced-graphs | 4 | solve connectivity and flow problems | functional graphs, SCC, 2-SAT, bridges, Euler paths, flows | 40 | 3 Build |
| 10 | computational-geometry | 2 | handle points and polygons exactly | cross product, segments, polygons, hull | 30 | 3 Build |

## Goals
### Enter my first rated contests: Codeforces Div. 3 or 4, AtCoder Beginner (about 135 h)
Steps: cpp-for-contests; dsa-core-techniques; recursion-and-dynamic-programming 1-6; graphs-and-trees 1-3; contest-strategy 1-4, 8.
Open with: CSES Maximum Subarray Sum from statement to accepted: limits read first; the brute force, right on the sample, ruled out by counting n(n+1)/2 ≈ 2·10^10 additions; what it repeats, as an observation proved; the linear scan checked against the brute force with `diff`, then submitted; then the same, alone, on a problem not shown (cpp-for-contests 1; dsa-core-techniques 1).
Deep: dsa-core-techniques 1, 7, 12; cpp-for-contests 9; recursion-and-dynamic-programming 5.
Order: cpp-for-contests 1; dsa-core-techniques 1; cpp-for-contests 2-3; dsa-core-techniques 2; cpp-for-contests 9; cpp-for-contests 4-5; dsa-core-techniques 3-4; contest-strategy 1-2, then a rated round weekly; cpp-for-contests 6-8; dsa-core-techniques 5-7; contest-strategy 3-4, 8; dsa-core-techniques 8-13; the rest, rows in order.
Halfway: "I solve A and B in rated rounds, upsolve C, and size ideas by their limits."

### Get good in a year at ten hours a week (towards Expert, interview-ready) (about 470 h)
Steps: cpp-for-contests; dsa-core-techniques; recursion-and-dynamic-programming; graphs-and-trees; contest-strategy; interview-problem-solving; advanced-data-structures; number-theory-and-combinatorics; string-algorithms; advanced-graphs; computational-geometry.
Open with: CSES Maximum Subarray Sum from statement to accepted: limits read first; the brute force, right on the sample, ruled out by counting n(n+1)/2 ≈ 2·10^10 additions; what it repeats, as an observation proved; the linear scan checked against the brute force with `diff`, then submitted; then the same, alone, on a problem not shown (cpp-for-contests 1; dsa-core-techniques 1).
Deep: dsa-core-techniques 1, 12; recursion-and-dynamic-programming 13; graphs-and-trees 13; advanced-data-structures 8.
Order: cpp-for-contests 1; dsa-core-techniques 1; cpp-for-contests 2-3; dsa-core-techniques 2; cpp-for-contests 9; then rows in order, C++ where first needed; contest-strategy 1-4 after dsa-core-techniques 4, then a rated round a week; interview-problem-solving after row 4.

### Climb USACO Bronze to Gold (about 270 h)
Steps: cpp-for-contests; dsa-core-techniques; recursion-and-dynamic-programming; graphs-and-trees; advanced-data-structures 1-6, 10; number-theory-and-combinatorics 1-6; string-algorithms 1-3; advanced-graphs 1.
Open with: a past USACO Bronze problem to all official tests passed: the most direct loops, counted against the limits before coding (they fit), then the same count at Silver-sized n foretelling a time limit (cpp-for-contests 1; dsa-core-techniques 1).
Deep: dsa-core-techniques 1, 7, 10; graphs-and-trees 2; recursion-and-dynamic-programming 5, 13.
Order: Bronze: cpp-for-contests 1; dsa-core-techniques 1; cpp-for-contests 2-3; dsa-core-techniques 2; cpp-for-contests 9; then cpp-for-contests 4-8, 10 and dsa-core-techniques 3-5, 12 interleaved; recursion-and-dynamic-programming 1-3; graphs-and-trees 1. Silver: dsa-core-techniques 6-11, 13; graphs-and-trees 2-4, 8. Gold: the rest, rows in order. A timed past contest ends each part.

### Solve unseen Codeforces problems rated about 1500 to 1800 (about 245 h)
Steps: cpp-for-contests; dsa-core-techniques; recursion-and-dynamic-programming; graphs-and-trees; contest-strategy; number-theory-and-combinatorics 1-6.
Open with: an unseen problem rated about 1500 to accepted: limits read first; the brute force, right on the samples, ruled out by its count; the observation proved; the fast idea checked against the brute force with `diff`, then submitted; then the same, alone, on a second problem (dsa-core-techniques 1; cpp-for-contests 1).
Deep: dsa-core-techniques 7, 12; recursion-and-dynamic-programming 13; graphs-and-trees 13; number-theory-and-combinatorics 5.
Order: cpp-for-contests 1; dsa-core-techniques 1; cpp-for-contests 2-3; dsa-core-techniques 2; cpp-for-contests 9; contest-strategy 1-4, then a rated round a week; dsa-core-techniques 3-13; contest-strategy 5-9; the rest in row order, C++ where first needed.

## Why this order
C++ first (USACO Guide). Overflow, fast input and the habit of brute force, observation, argument and stress
test (cpp-for-contests 2-3, 9 with dsa-core-techniques 2's complete search as the sure brute force) come in the
first three or four chapters, because every technique chapter tests with them. Complete search by loops is row 2
step 2; row 3 step 2 adds recursion. Graphs follow DP: DFS is recursion; trees and DAGs hold DPs. 8 needs 6
(Fenwick, sparse table).

## Checkpoint projects
- After 2: a template, an error log, rounds upsolved.
- After 4: unseen CSES graph and DP tasks, timed.
- After 5: ten reviewed virtuals; no mistake logged twice in the last five.

## Short on time
Never skip 1 to 4, stress tests, upsolving. Row 7 steps 1-6 early; 8 to 10 when needed.

## Left out on purpose
- Platinum topics (centroids, FFT, SOS DP, xor basis): "later" on rows 3, 6 to 10.
- Constructive and ad hoc problems: row 2 step 13, then rated rounds.
