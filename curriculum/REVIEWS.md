# Review records

Each file under `curriculum/` was reviewed by an agent that did not write it, to `curriculum/REVIEWING.md`.
These are the reviewers' own records, unedited: sources reopened, outlines compared, what was run, each change
and why, what stays unverified, and a score out of ten. Second design, 18 and 19 November 2026. The records of
the first design (the pilot of 18 November) are kept at the end; the files they describe were since converted
and reviewed again.


## R1: Contest core cards and the competitive-programming map

### R1: review record (competitive-programming list), 2026-11-18

#### cards/cpp-for-contests.md, reviewed 2026-11-18 (score 8/10; 1,665 tokens)
- Sources opened: cses.fi/problemset (every named task exists: Weird Algorithm, Missing Number, Number Spiral,
  Repetitions, Increasing Array, Nested Ranges Check, Concert Tickets, Room Allocation, Coin Piles, Hidden
  Integer under Interactive Problems); codeforces.com/blog/entry/4088 (Codeforces rules, read via the .net mirror:
  "the judging result as the number of the first pretest that failed"; it does NOT say testing stops there);
  codeforces.com/blog/entry/76724 and 78321 (no statement either way about stopping; one comment says tests may
  run in parallel); cses.fi/142/text/674 (a CSES course page: "only the first error will be shown"; course,
  not the problem set); codeforces.com/blog/entry/137878 (users: on CSES "we have the option to view the full
  test cases where our solution fails"; on Codeforces tests are hidden in rounds, visible in the problemset,
  cut when long); usaco.guide/general list.
- The two `unverified:` statements: "CSES runs every test and shows each verdict" found no source (CSES's own
  course page says only the first error is shown) and "Codeforces stops at the first failing test" is not in
  the rules (only that the first failed test is the one named). Both REMOVED. Step 1 now says what is certain:
  a verdict names only the first failing test; CSES lets you open that test's input, Codeforces shows tests
  only outside a live round, cut when long (users' reports, on `unverified:`). The wrong belief's truth is now
  "the verdict names only the first failing test".
- Outlines compared: USACO Guide General (I/O, debugging, stress testing, data structures incl. stack, queue,
  deque) and CSES handbook ch. 1-4 (language features, floating-point output). Gaps fixed: `stack`, `queue`,
  `deque` added to step 4 (BFS in graphs-and-trees 3 and windows used them with no home); decimal output with
  `fixed << setprecision` added to step 3 (geometry and probability need it). Left: `pb_ds`, `bitset` (already
  later); `__int128` (taught where needed, computational-geometry 1).
- Run (g++ 13, /tmp/r1): `a*a` gives -1757895751; `v.size()-1` = 18446744073709551615 and `-1 < v.size()` false;
  `ms.erase(1)` removes both copies; `m[5]==0` inserts; comparator `a<=b` on 100 equal items: ASan
  heap-buffer-overflow and `_GLIBCXX_DEBUG` abort; Weird Algorithm peak for n ≤ 10^6 is 56,991,483,520 (> 5·10^10);
  10^7 numbers read untied 0.48 s; 10^6 `endl` lines 0.51 s against 0.04 s with `'\n'`. `a[n] = 0`: right sum
  for n = 1000, glibc `malloc` abort for n = 10; ASan reports both.
- Changed: step 1 (above); step 3 (decimals); step 4 (stack/queue/deque); the [8] "How it runs" item now says
  what really happened (right for n = 1000, abort for n = 10) instead of "gave the right answer"; sources gain
  the two Codeforces pages and the timings.
- Still unverified: what each judge shows of a failed test (users' reports); order and counts (judgement).
- Holds it back: step 1's judge facts rest on users' reports, not a help page of either judge.

#### cards/dsa-core-techniques.md, reviewed 2026-11-18 (score 8/10; 1,831 tokens)
- Sources opened: cses.fi/problemset (all named tasks exist); usaco.guide/bronze, /silver (module lists),
  /silver/binary-search-sorted-array (Counting Haybales is its example); codeforces 1201C name; CSES handbook
  complexity table (n ≤ 20: 2^n; ≤ 5000: n²; ≤ 10^6: n log n).
- Outlines compared: USACO Bronze + Silver, CSES handbook ch. 2-6, 8. Gap that mattered: complete search
  (Bronze, handbook ch. 5) comes before greedy in both, and step 11's stress test needs it, but its only home
  was recursion-and-dynamic-programming 2, which comes AFTER this card (and the blind test's learner lost it).
  Fixed: complete search by loops (bitmask subsets, `next_permutation`/`itertools`, Apple Division, 2^20) is now
  in step 1, with the words complete search and bitmask and the two wrong beliefs that belong to it (moved here
  from the DP card). Left: Bronze rectangle geometry and ad hoc (no step; minor), monotonic stack and sliding
  minimum (already later, advanced-data-structures 1-2), ternary search (later).
- Python check (needs `cpp-for-contests | python-core`): before, step 1's budget (10^8/s) was wrong for Python,
  step 4 sent the learner to cpp-for-contests 7, step 5 named only `lower_bound`, step 11 required a `multiset`
  and the C++ stress harness, and the Promise said "accepted in C++". Now: budget "about ten times fewer in
  CPython" (run: 10^7 additions 0.8 s); step 4 names both languages' hash containers and both fallbacks against
  crafted keys (run: 2·10^4 Python set keys that are multiples of 2^61−1 took 3.2 s, plain keys 0.03 s); step 5
  gives `bisect_left`/`bisect_right` (run); step 11 says the stress loop is the same in Python and that Python's
  standard library has no ordered multiset (look up `sortedcontainers` on the judge, else C++); `run: python`
  allowed; Judged-by and the overflow failure say "C++" where only C++ overflows.
- Homes now: sets/maps cpp-for-contests 6 (hash ones 7) or python-core; heaps cpp-for-contests 7 or python-core;
  complete search here, step 1. Every step that uses them names where they come from (4, 11).
- Still unverified: rating bands, counts and times (judgement, on the line).
- Holds it back: Python's home card (python-core) does not exist yet, so the Python route's sets and heaps
  rest on a planned row.

#### cards/recursion-and-dynamic-programming.md, reviewed 2026-11-18 (score 8/10; 1,568 tokens)
- Sources opened: cses.fi/problemset (all named tasks exist; Counting Tilings and Increasing Subsequence II
  checked for "later"); usaco.guide/gold (DP modules: intro, knapsack, grids, LIS, bitmask, range, digit: all
  present) and /gold/intro-dp ("problemsetters rarely set direct applications"; push and pull DP confirmed);
  AtCoder DP contest task names (Frog 1, Vacation, Knapsack 1/2, LCS, Coins, Deque, Slimes, Matching, Digit Sum).
- Outlines compared: USACO Gold DP list and CSES handbook ch. 5, 7, 10. Gaps: broken-profile DP and DP sped up
  by a Fenwick tree added to "later"; meet in the middle already there.
- Run: memoised Dice Combinations at n = 10^6 segfaults at an 8 MB stack (confirms the [1,4] failure).
- Changed: step 2 rewritten as complete search BY RECURSION (choose/skip, `used` array, search tree), building
  on dsa-core-techniques 1, so complete search has one home; its words and two beliefs moved to that card.
  Word "expected value" removed from step 12 (AtCoder Coins is a probability, and expected value is taught by
  number-theory-and-combinatorics 9; the check note is gone): now "probability DP". Step 12 names the tight flag
  of digit DP. Python line for the coding-interviews track (`functools.cache`, `RecursionError`, bottom-up).
- Still unverified: readiness bands and times.
- Holds it back: step 2 now has no wrong belief of its own (I would not invent one).

#### cards/graphs-and-trees.md, reviewed 2026-11-18 (score 8/10; 1,581 tokens)
- Sources opened: cses.fi/problemset (all named tasks exist); usaco.guide/silver and /gold (traversal, flood
  fill, trees, functional graphs in Silver; DSU, topological sort, Dijkstra, MST, tree DP, rerooting, LCA in
  Gold); cp-algorithms lca_binary_lifting.
- Outlines compared: USACO Silver/Gold graph modules and CSES handbook ch. 11-16, 18. Gaps: none essential;
  successor graphs and cycle finding live in advanced-graphs 1.
- Overlap found: step 10 taught binary lifting on Planets Queries I (successor graph, k ≤ 10^9), and
  advanced-graphs 1 teaches the same on the same problem. Fixed my side: step 10 is now binary lifting on
  ancestors (`up[j][v]`, k-th ancestor, LCA, distance by depths) with a pointer to advanced-graphs 1 for
  successor graphs; the failure is now "depths up to 2·10^5 need 18 levels"; the word "successor graph" dropped.
- Changed: step 5 names Python `heapq`; Python line for the coding-interviews track (`deque`, `heapq`, explicit
  DFS stack); sources line.
- Still unverified: readiness bands, counts, times.
- Holds it back: Planets Queries I still appears in advanced-graphs 1 with its own lifting (not my file).

#### core-cs/competitive-programming.md, reviewed 2026-11-18 (score 7/10; 893 tokens of 900)
- Read the six row 5-10 cards' headers, steps, projects and ladders. "Needs first" agrees with every card's
  `needs:` (5: 2; 6: 2, 4; 7: 3; 8: 3, 6; 9: 4; 10: 2). The "first cut" note removed.
- Changed: Main topics of rows 5-10 now name what the cards teach (row 5 platform rules, checklist, virtuals;
  row 7 expectation and games, which the old row lacked; row 8 drops trie as a main topic in favour of the
  card's spine; row 9 bridges and Euler paths; row 10 segments and polygons); row 1 names sets and heaps; row 2
  names complete search. Goals: first rated contests now include contest-strategy 1-4 and 8 (rules, reading
  the set, testing, checklist, upsolving; the old goal had none of row 5 while its checkpoint demanded
  upsolving); USACO line corrected against the USACO Guide lists (Silver graphs = row 4 steps 1-4, 8: the old
  "step 10" was binary lifting, which is not Silver; Gold = rows 3, 4, row 6 steps 1-6 and 10, row 7 steps
  1-6, row 8 steps 1-3, matching Gold's math, data-structure, Euler-tour and hashing modules, not "row 6" whole,
  which includes lazy propagation); 1500-1800 goal adds row 7 steps 1-6. Why this order: complete search
  before greedy; row 5 needs only 2; why 8 needs 6. Checkpoints after 6, 8, 9 from the cards' finish lines.
  Left out: Platinum topics now point to the cards' "later" lists.
- Still unverified: hours; that row 7 steps 1-6 are needed early (judgement).
- Holds it back: 893 of 900 tokens, so "Why this order" is terse (no reason given for 7 needing 3).

#### Conflicts with files outside my list
- cards/advanced-graphs.md step 1 re-teaches binary lifting on Planets Queries I; it should build on
  graphs-and-trees 10 (now ancestors only) and keep functional-graph cycles as its own.
- roles/new-graduate-software-engineer.md line 26 says "dsa-core-techniques needs cpp-for-contests (25 h)
  first"; it now needs cpp-for-contests OR python-core.
- core-cs/coding-interviews.md "Why this order" says dsa-core-techniques "is written in C++" and the Python
  learner must translate; the card now gives Python names itself. Its step ranges still hold (no step was
  renumbered in any of my cards).
- Word notes not mine to resolve: "brute force" (cpp-for-contests 9 and interview-problem-solving),
  "lowest common ancestor" (graphs-and-trees 10 by binary lifting, interview-problem-solving 11 by recursion on a
  binary tree: two mechanisms), "state" (recursion-and-dynamic-programming 5 and react: two meanings).
- `us_path.py check` fails on react.md, api-design.md, interview-problem-solving.md, javascript.md,
  node-and-express.md (sizes, missing needs); none on my files.


## R2: Advanced contest cards

### Review record R2: advanced-data-structures, string-algorithms, advanced-graphs, number-theory-and-combinatorics

Reviewer: independent agent. I did not write these files. I edited only these four cards. Not run: any git command.
The CSES pages were reached through WebFetch (curl to cses.fi and codeforces.com is refused by the proxy). The
whole problemset list was read, and so were the task pages named below. The Download Speed page showed the
maintenance notice, but the task is in the list. Programs are in /tmp/r2/src (g++ 13 -O2).

#### cards/advanced-data-structures.md, reviewed 2026-11-18
- Sources opened: cses.fi/book/book.pdf contents (ch. 8.2-8.3 nearest smaller and window minimum, 9 range
  queries, 18.2 subtrees and paths, 28.1 lazy propagation; 8 and 28 were missing from `sources:`, so I added them).
  The cses.fi/problemset list: every named task exists. Task pages read: Sliding Window Minimum (n ≤ 10^7,
  generated), Salary Queries (values to 10^9 with updates), Path Queries (root-to-node sum), Network Breakdown,
  New Roads Queries, Pizzeria Queries, Increasing Array Queries. Also atcoder.jp/contests/practice2 task list
  (B Fenwick, J Segment Tree, K Range Affine Range Sum, L Lazy Segment Tree) and usaco.guide/gold and /plat
  module lists.
- Outlines compared: the CSES handbook chapters 8, 9, 18 and 28, and the USACO Guide Gold and Platinum Range
  Queries and Trees modules. Gaps: small-to-large merging (Distinct Colors), sparse segment trees and Mo's or
  square root decomposition were not named. All three now sit under Later. Divide-and-conquer static range
  queries and the Kruskal reconstruction tree are left out: Platinum, rare.
- Run: overlap on 1 2 3 4 5 gives 24 for 15. For n = 6 the highest node is 13, and over n ≤ 10^5 the highest
  node divided by n is 3.977. Without push down, add 5 to [0,3] and the sum of [1,2] is 0, not 10. A Fenwick
  update from index 0 stays at 0. A reversed array of 2·10^5 has 19,999,900,000 inversions.
- Changed:
  - The "run, 28 for 23" overlap example could not be reproduced. I replaced it with an example anyone can
    rerun.
  - The sparse-table belief now gives the true alternatives (disjoint blocks in O(log n), or prefix sums).
  - The Fenwick-minimum truth was missing a condition: it holds only while values only fall.
  - The lazy-composition truth was wrong ("wipe the additions below it"). It now says what happens at the node
    itself, in both orders.
  - Step 3 now gives the table, the choice of k and the idempotent operations.
  - Step 5 now says the compression must include updates and query ends, and has a new failure for it.
  - Step 7 now says which walk each problem needs, and "order statistic" moved to 7, where the k-th element is
    taught.
  - Step 8 now names what the tags are for practice2 K and Polynomial Queries.
  - Step 10 was thin. It now says how Path Queries becomes subtree range add plus point query, with a path
    through the LCA.
  - Step 11 was thin (union-find "with data per set" on a problem that needs only a count). It now covers data
    at the leader, reverse time, and New Roads Queries (union by size without compression, links labelled by
    day). I added a failure for path compression there.
  - Step 12 now says what each mixed problem combines.
  - Words: tag, push and merge became "lazy tag", "push down" and "merge function". This ends the clash with
    git, where the words mean other things.
- Placement: Euler-tour subtree and path queries and the union-find extensions are right here. Both are a
  Fenwick or segment tree, or a union-find, over a structure that graphs-and-trees already built (DFS order,
  plain union-find in its step 11). Binary lifting rightly stays in graphs-and-trees.
- Still unverified: step order past 8; practice counts.
- Score 8/10. What most holds it back: step 12 ends on Increasing Array Queries, which is much harder than
  everything before it. A planner may need to put it `later:`.

#### cards/string-algorithms.md, reviewed 2026-11-18
- Sources opened: cses.fi/book contents (ch. 26) and the problemset list: every named task exists. Task pages
  read: Repeating Substring, Required Substring (n ≤ 1000, m ≤ 100), Minimal Rotation, Palindrome Queries,
  Substring Order I, String Functions. Also codeforces.com/blog/entry/60442 (dacin21: the n/p bound, the
  Thue-Morse table at 2^10, 2^61−1, pairs of primes), Codeforces 1200E "Compress Words" (API name) and 126B
  Password, and AtCoder practice2 I (Number of Substrings).
- Outlines compared: the cp-algorithms string section (prefix function, Z, hashing, Rabin-Karp, suffix array,
  Aho-Corasick, suffix tree, suffix automaton, Lyndon, Manacher, Main-Lorentz) and the USACO Guide Advanced
  Strings modules. Main-Lorentz and suffix trees were missing; I added them to Later. Expression parsing is left
  out: it is not string matching.
- Run:
  - A Thue-Morse string and its complement collide under unsigned 2^64 for 1000 of 1000 odd bases at length
    1024, and for 269 of 1000 at length 512. Even bases never collide this way.
  - 300,000 random strings modulo 10^9+7 give 48 colliding pairs; m²/2p predicts 45.
  - With letters mapped from 0, h("b") = h("ab") = 1.
- Changed:
  - The Thue-Morse length was 2048. It is now 1024, which is enough (run, and the blog's table). The card now
    says what goes wrong with an even base.
  - Step 2 now gives the concrete safe choices and the m²/2p figure.
  - Step 3 now gives the monotonicity that makes the binary search valid.
  - The unreproducible "−1000000001" was replaced by the actual symptom (equal substrings compare unequal).
  - "Chance about n/p" became "at most n/p".
  - Word "anti-hash test" (owned by contest-strategy 5, earlier in the same track) was replaced by "double
    hashing".
  - The sources now say what each was used for.
- Note left standing: "trie" is also tagged by interview-problem-solving 12. The two cards are on different
  tracks with no `needs:` link between them. A contest learner meets the trie only here, an interview learner
  only there, so each card must teach it.
- Still unverified: step order past 9; practice counts.
- Score 8.5/10. What most holds it back: Aho-Corasick sits under Later, though many coaches teach it before
  suffix arrays. That is defensible, but not proven by any source.

#### cards/advanced-graphs.md, reviewed 2026-11-18
- Sources opened:
  - cp-algorithms 2SAT: Kosaraju, components in topological order, `assignment = comp[x] > comp[¬x]`.
  - cp-algorithms Dinic: fewer than V phases; O(VE) blocking flow with edge pointers; O(V²E); O(E√V) on unit
    networks, meaning every vertex except s and t has one entering or one leaving edge of capacity 1;
    O(E√E) when all capacities are 1.
  - CSES handbook contents (16.3-16.4, 17, 19, 20) and the problemset: every named task exists. Planets
    Queries II page read.
  - AtCoder practice2 D, G, H; usaco.guide/adv module list.
- Outlines compared: the CSES handbook ch. 16-20 and the USACO Guide Advanced Graphs and Flows modules. Gaps:
  flows with lower bounds, Hall's and Dilworth's theorems (handbook 20.3-20.4), and Hamiltonian paths
  (handbook 19.2). All are now under Later. Block-cut trees were already there.
- Run:
  - 2-SAT on 20,000 random formulas against brute force. Kosaraju with comp[x] > comp[¬x] and Tarjan with
    comp[x] < comp[¬x] both had 0 failures. The wrong direction broke a clause in 13,131 of 15,927
    satisfiable formulas.
  - Dinic phases on random matching networks: 6, 7 and 8 at V = 2,002, 10,002 and 40,002, all within 2√V.
  - Edges 0-1, 0-1, 1-2: skipping the parent node reports 0-1 as a bridge; skipping the parent edge does not.
- Changed:
  - Step 1 repeated graphs-and-trees 10 (binary lifting on a successor graph, Planets Queries I), and so did
    its belief "binary lifting is for trees". Step 1 now teaches the tail-and-cycle structure, three-colour
    walking or tortoise and hare, Planets Cycles, and Planets Queries II using the jumps from graphs-and-trees
    10. The belief was replaced.
  - Step 2 now says in which order each algorithm numbers its components.
  - Step 4 now states the rule as "after in topological order". The wrong belief is rewritten with the run's
    numbers.
  - Step 8 now gives each bound with its exact condition, and I added the wrong belief "Dinic is always
    O(E√V)".
  - Step 5 now says to skip the parent by edge id.
  - Step 6 now gives the exact degree conditions (directed included) and a used mark per edge.
  - Step 10 now states Kőnig's theorem and says how to read the paths back.
  - The two sources the writer had not run (2-SAT direction, flow bounds) are now run or quoted with their
    conditions.
- Still unverified: step order past 6; "a few hundred nodes" as the flow signal; practice counts. The cost of
  Dinic without edge pointers comes from cp-algorithms; I did not time it.
- Score 8.5/10. What most holds it back: no step teaches recovering a minimum vertex cover or a path cover as
  output, only its size.

#### cards/number-theory-and-combinatorics.md, reviewed 2026-11-18
- Sources opened: the CSES problemset list (every named task exists) and these task pages: Exponentiation II,
  Counting Divisors, Moving Robots (a decimal answer, not modular), Fibonacci Numbers, Throwing Dice, Graph
  Paths I, Stick Game, Grundy's Game (n ≤ 10^6, t ≤ 10^5). Also the CSES handbook contents (21-25),
  usaco.guide/gold/modular (Fermat for a prime p and a not divisible by p; it does not cover the totient),
  AtCoder ABC326 E (modulo 998244353) and ABC340 F (S = 1).
- Outlines compared: the CSES handbook ch. 21-25 and the USACO Guide Gold Math, Platinum Misc. and Advanced
  Misc. modules.
  - Gap fixed: Euler's totient and Euler's theorem (handbook 21.2) were missing, though Exponentiation II
    rests on them. They are now in step 5.
  - Gap fixed: graphs and matrices (handbook 23.3) are now in step 10 with Graph Paths I.
  - Already under Later: Möbius, CRT, Lucas, Burnside, Gaussian elimination, Miller-Rabin and FFT.
  - Left out: Cayley's formula and Markov chains (rare). XOR basis is an Advanced module.
- Run:
  - 3^8 ≡ 1 modulo 10, while 3·7 ≡ 1. (2p)^(p−2) ≡ 0. -7 % 3 = -1. 46341² > INT_MAX.
  - Ten products of residues near 10^9+7 overflow signed 64-bit; nine do not.
  - Grundy's Game values up to 10^5 have 41 zeros, the last at 1222.
- Changed:
  - Grundy's Game, as named, could not be solved by the step's method (the n ≤ 10^6 table is quadratic). The
    step now says the solution is a pattern found by computing, with the numbers from the run.
  - The matrix overflow failure now gives the exact threshold.
  - Step 9 now says what Moving Robots and ABC326 E compute.
  - Step 11 now teaches the losing-position rule and Nim's xor test explicitly.
  - The promise now covers games.
  - I added a project finish line; the card had none.
  - Word "expected value" is left to recursion-and-dynamic-programming 12, which comes earlier in the track.
  - "Euler's totient" was added.
  - The sources now say what each was used for.
- Placement: games stay here. Nim and Sprague-Grundy are xor and mex arguments (handbook ch. 25 sits in the
  maths part). recursion-and-dynamic-programming 10 teaches minimax DP (Removal Game), which is a different
  idea, and that card already has 13 steps. This is judgement, and is said on `unverified:`.
- Still unverified: step order; practice counts; whether Grundy's Game has no losing heap above 10^5 (I did not
  prove it).
- Score 8/10. What most holds it back: there is no probability step beyond linearity (conditional
  probability, probability DP), so "expected value" problems needing states lean on the DP card.

#### Conflicts outside my list
- interview-problem-solving tags "trie", "monotonic stack" and "amortised" that these cards also teach. They
  are separate tracks; someone should decide the checker's rule for cross-track words.
- The competitive-programming map, row 7: its "Main topics" omits games and matrices, which the card teaches.
- `check` fails on react.md, api-design.md, distributed-systems-core.md and javascript.md (size, needs), which
  are not mine.


## R3: Geometry, contest strategy, interviews

### R3 review record (independent agent, sources reopened), 2026-11-18

Files: cards/computational-geometry.md, cards/contest-strategy.md, cards/interview-problem-solving.md,
core-cs/coding-interviews.md, core-cs/INDEX.md. All five are marked reviewed. `us_path.py check` shows no ERROR
for any of them. The ERRORs it prints are all in web/ files that other reviewers own.
Network: curl is refused by the proxy for every source host, so every page was opened with WebFetch.

#### cards/computational-geometry.md, reviewed 2026-11-18 (1,927 tokens; score 8.5/10)
- Sources opened: cses.fi/problemset (the Geometry ids 2189-2195, 3410, 1740, 1741 all exist); the task pages
  2191 (prints 2a, |x| <= 1e9, n <= 1000), 2192 (INSIDE/OUTSIDE/BOUNDARY), 2194 (prints d², distinct points),
  2195 ("print all points that lie on the convex hull", area > 0), 3410 (points added one at a time);
  cses.fi/book/book.pdf ch. 29-30 (the sign of the cross product, the three segment cases, ray parity, Pick,
  the rotation (x+y, y-x), the closest-pair window [x-d, x] x [y-d, y+d], Andrew's sort by (x, y), and
  Intersection Points needing a binary indexed tree or segment tree); usaco.guide/plat/geo-pri (the order;
  its Angles section; CF Cut Length); cp-algorithms convex-hull (the include_collinear flag and the
  all-collinear special case), check-segments-intersection (projections on both axes, sgn tests),
  picks-theorem; codeforces 598F (at most two decimals, |coord| <= 1e5, error 1e-6).
- Outlines compared: (1) CSES book ch. 29-30. Complex numbers as the representation are left out: a coding
  choice, not a concept. Intersection Points was already under "later". (2) USACO Guide Geometry Primitives,
  then Sweep Line. Gap: Angles (sorting by argument). Fixed: step 10 now teaches the exact polar sort (half-plane,
  then cross product, not atan2), with the word "polar angle".
- Run (g++ 13, -fsanitize=undefined, /tmp/r3geo/g.cpp):
  - The segment test as the card states it agrees with an exact rational brute force on 200k random pairs in
    -3..3 (0 mismatches). My first brute force was wrong and was replaced.
  - Point in polygon, with the card's rule plus the orientation condition, agrees with a perturbed-ray brute
    force on 20k random star polygons (0 mismatches).
  - Monotone chain: popping on `< 0` keeps collinear points (a square with an edge midpoint gives 5) and on
    `<= 0` drops them (4). An all-collinear input of 4 points gives 6 points when collinear points are kept,
    which confirms the failure the card lists.
  - Pick on the 2x2 square: 2A=8, B=8, I=1. Using 2A as A gives 5, which confirms that failure.
  - The bound 2·(2e9)² = 8e18 < 2^63-1.
  - 4e9·4e9 in `long long` is reported by UBSan and wraps to a negative value.
- Changed:
  - Step 5: the ray rule was incomplete. Counting "exactly one end strictly above" without the side test counts
    edges to the left of the point. Added the orientation condition and "odd is inside".
  - Steps 3, 4, 6, 7, 8, 9 now state the exact decision each one carries: the shoelace sum and its sign; the four
    segment cases; B as the sum of the edges' gcds and I = (2A - B + 2)/2 in integers; the hull's popping turn
    and its orientation; why only the extremes of x+y and x-y matter; d rounded up from d².
  - Step 10: polar sort added; inputs with two decimals scaled by 100; the 1e-6 tolerance.
  - Added the wrong belief "the shoelace sum is the area". Both failures now carry the results of my runs.
  - "Later": I judge the Fenwick deferral right. Intersection Points is exactly a sweep that counts active
    horizontals in a y range (CSES book 30.1), and this card does not need advanced-data-structures. It now
    names advanced-data-structures 4-8 and says these are good first problems after that card.
  - Mastery "Use" now names the steps' problems, not list positions.
  - The sources line now records what each source confirmed.
- Still unverified: step order and practice counts (judgement). Not run: whether the shoelace running sum can
  pass 2^63 when 2a fits. A spiral polygon argues that it can; this is not on the card.
- Holds it back: the card does not cover a point's distance to a segment or line, beyond step 10's mention of
  floating point.

#### cards/contest-strategy.md, reviewed 2026-11-18 (1,972 tokens; score 7.5/10)
- Sources opened:
  - CF blog 133094: standard rounds against extended ICPC rounds; points fall every minute; pretest 1 and
    compile errors cost nothing; +100/-50 room hacks; a 12-hour open hacking phase.
  - CF blog 20762: d = (R - r)/2, where R is fitted to the geometric mean of seed and place.
  - CF blog 62865 (MikeMirzayanov): equal rating means 0.5; 200 below means 0.75.
  - CF blog 53341 (E869120): virtual contests; keep solve times in a spreadsheet.
  - CF blog 98806 (Um_nik): archives teach, contests make you fast; problems a little above your level; switch
    problems when stuck; avoid editorials.
  - atcoder abc400 rules: score, then time, 5 minutes per wrong answer, compile errors free.
  - cerc25 rules: three people, one PC, the last hour frozen, 20 minutes per rejection. Its compile-error rule
    contradicts itself, which supports the card's "each regional sets its own".
  - usaco.guide contest-strategy: read all problems first; difficulty may be out of order; do not spend "too
    long" on one; partial scores take from 30 seconds to 30 minutes.
  - usaco.guide practicing: D. Yao reads the editorial step by step, after 15-20 minutes at Bronze and 30-40 at
    Silver; B. Qi says implement unless you understand it perfectly.
  - usaco.guide debugging-checklist.
  - KACTL troubleshoot.txt on github.com: "generate max cases" when the time limit is close; print your code.
  - CSES book 1.6: companies use contests for recruiting; the IOI and ICPC formats.
- Outlines compared: (1) the USACO Guide general modules (contest strategy, practicing, debugging checklist):
  all covered. (2) The E869120 and Um_nik training guides. Gap: the editorial question, where the coaches
  disagree. Fixed: step 8 now gives both views and tells the learner to pick a rule. Gap: tracking solve times.
  Fixed in step 10.
- Changed:
  - Check 9: step 6 was the generic step. It now carries a real rule: under ICPC-style penalty, which sums solve
    times, shortest first minimises the sum. It also carries the USACO Guide's warning about partial-score cost.
  - Step 7 now says who types and who thinks, and that you debug from a printout. The page limit of the team
    reference is looked up per contest.
  - Step 1 says what each format rewards (points fall each minute, wrong tries cost points) and adds "template
    compiled before the clock starts".
  - Step 11 now gives the source's test of a useful problem in place of a free-floating band.
  - Step 12 now gives the real formula in place of "about half to your performance".
  - The wrong belief on step 6 is reworded to what the USACO Guide actually says. It never says "return".
  - "In production": the CSES list of company contests is partly out of date (Code Jam has ended), so it now says
    which contests still run must be looked up. Added a line on how the habits transfer.
  - Words: "edge case" was owned twice (here and in interview-problem-solving). Step 3 now owns "max test", which
    the step really teaches (KACTL).
  - Each source in the sources line now records what it confirmed.
- Still unverified: time boxes, log categories, team roles, weekly load and "a month" (judgement, on the line).
- Holds it back: the time-box and team-role decisions are coaching judgement with no source a learner can open.

#### cards/interview-problem-solving.md, reviewed 2026-11-18 (1,994 tokens; score 7.5/10)
- Sources opened:
  - techinterviewhandbook.org coding-interview-rubrics: four dimensions; "announced they are done" untested is
    the lowest testing band; silence is the lowest communication band. The page does NOT rank coding over
    communication.
  - cheatsheet: restate; 2-3 clarifying questions; code after a green light; do not announce done.
  - study-plan: priorities; 11 hours a week for 3 months; mocks from 60%; the Grind 75 week lists. These
    confirmed every problem title on the card except Daily Temperatures and Remove Nth Node, which the TIH stack
    and linked-list pages list.
  - algorithms/ stack, linked-list, heap ("use a Min Heap of size k" for the top k; Python heapq is a min-heap),
    interval (the overlap test; touching intervals as a corner case), tree (recursion is the most common
    approach; iterative traversals; in-order of a BST is sorted; level order by BFS).
  - behavioral-interview: STAR plus Reflection; 3-5 projects.
  - metacareers.com blog "preparing for your software engineering interview at Meta" (updated 2022-10-06): 45
    minutes split 5/35/5; a shared editor; practise without a compiler; the approach "can be as important as"
    the answer.
  - interviewing.io hiring-process guide: "how" and "what" companies; five interviews double your chances.
  - interviewing.io blog "does communication matter... 100k interviews": a 4-4-2 candidate does far better than
    a 3-3-4 one; one point lost in Code or Solve raises rejection about 6x.
  - crackingthecodinginterview.com contents: "Look for BUD"; BCR.
- Google PDF: the "Google Interview Prep Guide" is a recruiter handout reposted on third-party sites
  (hbcuconnect, a GitHub Pages copy). I opened one copy. It says "google.com/careers" in the footer but carries
  no issuer and no date. Google's own pages (how-we-hire, interview-tips) hold no coding-interview details. I
  could not establish it as official, so I REMOVED it and replaced it with Meta's own blog post, which supports
  the same claims (45 minutes, shared editor, no compiler, approach scored). metacareers swe-prep-techscreen
  only confirms 45 minutes and was dropped in favour of that post.
- Outlines compared: (1) CtCI table of contents. Gaps: bit manipulation, math puzzles, OO design, threads.
  Bit manipulation and OO design/concurrency are now named under "later" with reasons; math puzzles are left out
  as rare in current loops (judgement). (2) The TIH study-plan topics. Gaps: Matrix (covered by
  dsa-core-techniques 2 and graphs-and-trees grids); Recursion (now step 11, below); level-order and iterative
  traversal (added to step 11).
- Changed:
  - Step 8 was WRONG. It said "a size-k min-heap for top k (K Closest Points to Origin)". The k closest need a
    max-heap of size k; a min-heap keeps the farthest. Fixed, with Top K Frequent Elements as the min-heap case
    and the negated-key trick for heapq. Added a failure for this mistake.
  - Recursion (decision): a learner on the coding-interviews track meets row 4 before
    recursion-and-dynamic-programming, and trees are "High" priority in TIH. So step 11 stays here and now
    teaches recursion explicitly: null base case, trust the calls on both children, call depth equals height,
    a skewed tree; plus level order with step 7's queue and Kth Smallest by in-order. Words: the
    recursion-and-dynamic-programming card owns base case and call stack; this card uses them untagged. The map
    now says recursion-and-dynamic-programming step 1 goes fast after this step.
  - Monotonic stack: a learner on this track never reaches advanced-data-structures, so step 7 keeps the
    technique (Daily Temperatures, Largest Rectangle), with "each index pushed and popped once". One home per
    word: the words "monotonic stack" and "amortised" are untagged here (advanced-data-structures step 1 owns
    them); step 7 owns "next greater element".
  - Other words untagged here because their mechanism has a home elsewhere: "brute force" (cpp-for-contests 9;
    the learner has it from dsa-core-techniques 1); "eviction" (caching-and-queues, replaced by "doubly linked
    list"); "lowest common ancestor" (graphs-and-trees 10, replaced by "level order"). "max-heap" was added.
  - Step 1 says why it uses Two Sum: the idea is already held, so attention stays on the conversation.
  - Step 3 spells out BUD and BCR.
  - Step 4: the unclear "helpers like `min` skipped with leave" became a helper named with its contract and
    written last.
  - Step 5: a trace table, no running.
  - Step 9: the cost of each operation in the LRU cache; ask before using `OrderedDict`; Time Based Key-Value
    Store by binary search on time.
  - Step 10: the overlap test, and ask whether touching intervals count.
  - Step 13: Grind 75 problems, topics hidden.
  - Wrong beliefs on steps 1, 3 and 5 now quote what the sources actually say. The [3] truth no longer claims a
    brute force always earns credit, given the "what" companies.
  - "In production" now has Meta's split and the how/what difference.
  - "Practice" now says mocks from 60% (TIH) and about five (interviewing.io).
  - Words moved into step order.
- Still unverified: counts and times (judgement); "I, not we" in story answers (common coaching, unsourced, on the
  line). LeetCode and neetcode pages were not opened; the titles were confirmed through TIH lists.
- Holds it back: the card is at the token limit. A Python-specific line per structure (deque, heapq,
  OrderedDict) would help Python learners, but there is no room for it.

#### core-cs/coding-interviews.md, reviewed 2026-11-18 (896 tokens; score 8/10)
- Sources opened: TIH study plan (trees and graphs High, DP Low, 11 hours a week for 3 months, mocks at 60%);
  interviewing.io guide (five interviews); CtCI contents. The source note was corrected: CtCI has an
  "Experienced Candidates" section, OO design and threads, but no system design chapter.
- Ranges checked against the cards as they stand now. All step numbers exist.
  - Internship: dsa-core-techniques 1-9, interview-problem-solving 1-11 and 13-14,
    recursion-and-dynamic-programming 1-5, graphs-and-trees 1-3. Right as it was.
  - New graduate: unchanged in substance, but written as "rows 3, 4 all"; graphs-and-trees 13 added for state
    graphs (Word Ladder in Grind 75 week 12).
  - Senior: was WRONG in its emphasis. It had Bellman-Ford/Floyd, trees 8, MST 12 and interval DP 10,
    which are contest topics, and no design round beyond foundations. It is now the new-graduate line plus DP 13
    (an unseen DP), row 7, then the system-design/foundations goal "Pass system design interviews". That goal
    reaches system-design-interviews with its needs, and those needs are the senior loop's real difference.
  - Row 3 "Needs first" was 2. The card now needs cpp-for-contests | python-core, so it is now "1, 2", and "Why
    this order" says either one, not both. The format cannot express "or", and the check accepts this.
- Still unverified: hours and ranges (judgement, on the line).
- Holds it back: python-core is still planned, though it is the language most learners on this track will use.

#### core-cs/INDEX.md, reviewed 2026-11-18 (250 tokens, at the limit; score 8/10)
- Both built tracks are listed; the planned rows are honest; the role exists. I tried a sharper coding-interviews
  row, but it went over the limit, so I reverted it. No change.
- Holds it back: it is at the token limit, so the planned tracks cannot say more.

#### For others to resolve (outside my list)
- string-algorithms owns "trie" too, and the check notes it on that card. I kept the tag in
  interview-problem-solving because learners on the interview track never reach string-algorithms. The
  string-algorithms reviewer should untag it there, or tell me to.
- roles/new-graduate-software-engineer.md "Order and time" still says "dsa-core-techniques needs cpp-for-contests
  (25 h) first". The card now needs cpp-for-contests | python-core.
- advanced-data-structures keeps "monotonic stack" and "amortised". cpp-for-contests also owns "amortised cost",
  so those two cards should settle it between them.


## INTEGRATION-CS: Editor's pass over core-cs

### Integration record: competitive-programming and coding-interviews tracks, 2026-11-18

Editor-in-chief pass over the eleven cards and two maps (plus INDEX.md) after R1, R2 and R3. I read every card and
both maps end to end. I ran no git command that changes anything. Programs went in /tmp/integ.

#### 1. One home per idea and per word

| Idea or word | Before | Now | Why |
|---|---|---|---|
| amortised | cpp-for-contests [7] "amortised cost" and advanced-data-structures [1] "amortised" | dsa-core-techniques [7] "amortised" (step 7 says it: all moves counted together, at most 2n). Untagged in the other two; advanced-data-structures 1 now points to dsa-core-techniques 7 | Handbook ch. 8 (amortized analysis) opens with two pointers. dsa-core-techniques is the one card on every route: C++, Python and interview. The interview card uses the word in step 7 untagged, and its learner never reaches advanced-data-structures |
| brute force | cpp-for-contests [9] (interview-problem-solving was already untagged by R3) | dsa-core-techniques [1], whose step is "Brute force and complexity". cpp-for-contests 9 says "a brute force (the slow, sure solution)" untagged | A Python interview learner never has cpp-for-contests, so the word had no home on that route |
| sweep / sweep line | dsa-core-techniques [10] "sweep" and computational-geometry [9] "sweep line" | dsa-core-techniques [10] "sweep line" (step 10 reworded to say it). Geometry 9 untags it and points to dsa-core-techniques 10 | The same idea (sorted events) |
| collision | dsa-core-techniques [4] "hash collision" and string-algorithms [1] "collision" | dsa-core-techniques only; string-algorithms [1] keeps "polynomial hash" | The same word, met earlier on the same route |
| priority queue | cpp-for-contests [7] "heap" and graphs-and-trees [5] "priority queue" | graphs-and-trees [5] keeps "relaxation" only | Dijkstra uses the heap that cpp-for-contests 7 (or python-core, or interview 8) teaches |
| crafted hash keys | taught in cpp-for-contests 7, dsa-core-techniques 4 and contest-strategy 5 | Defence taught in dsa-core-techniques 4. cpp-for-contests 7 says "O(1) only on average (defences: dsa-core-techniques 4)". contest-strategy 5 says "(the defence: dsa-core-techniques 4)" | One home, both languages |
| complete search | dsa-core-techniques 1 (loops), recursion-and-dynamic-programming 2 (recursion) | Unchanged in substance. Checked: step 2 says "unlike the loops of dsa-core-techniques 1, a choice may depend on earlier ones", reuses Apple Division on purpose, and owns only "search tree". Alias "complete search" moved from the DP card to dsa-core-techniques. DP step 11 points to the bitmasks of dsa-core-techniques 1 | The two steps read as one progression with no repeat |
| binary lifting | graphs-and-trees 10 (ancestors) and advanced-graphs 1 | advanced-graphs 1 now says that the jump table of graphs-and-trees 10, built on successors instead of parents, gives the k-th successor (Planets Queries I). With the cycle structure it gives the distance a to b (Planets Queries II). graphs-and-trees 10 already points there | The home of successor jumps was implied, not stated. Planets Queries I had no step |
| trie | interview-problem-solving [12], string-algorithms [8] | Left. No route holds both cards (the instruction allows it) | |
| tortoise and hare / fast and slow pointers | advanced-graphs [1], interview-problem-solving [6] | Left. These are different cards on different tracks, the same case as trie | Noted: a contest learner who later takes interview-problem-solving meets both names |

`us_path.py check` printed no note for any of my files, before or after.

#### 2. Completeness against outlines
Outlines opened: usaco.guide/bronze, /silver, /gold, /plat (module lists), cses.fi/problemset (all 19 categories;
the Bitwise, Construction, Interactive, Sliding Window, Advanced Techniques and Counting task lists), and
techinterviewhandbook.org coding-interview-study-plan and algorithms/study-cheatsheet (18 topics with
priorities; Grind 75 weeks 5-12).

Contest gaps up to about Codeforces Expert:
- Bitwise operators (USACO Silver "Intro to Bitwise Operators"; CSES Bitwise Operations). Before, the only
  mention was `m >> i & 1`. FIXED: dsa-core-techniques 1 names `&`, `|`, `^`, `<<`, `>>`; step 9 adds prefix
  xors (`x ^ y ^ y == x`).
- Many test cases with a bound on the sum of n (every Codeforces Div. 3/4 round). There was no home. FIXED:
  dsa-core-techniques 1 (the sum is the budget) plus a failure [1] (clearing the whole array in each test).
- Rectangle geometry (USACO Bronze). It had no home and was not "later". FIXED: dsa-core-techniques 2 (per-axis
  overlap).
- Construction problems (CSES category; the Codeforces "constructive" tag). FIXED: named in
  dsa-core-techniques 12, and in the map's "Left out" as having no technique of their own.
- SOS DP (USACO Plat; CSES SOS Bit Problem): added to recursion-and-dynamic-programming "later".
- Xor basis (CSES Maximum Xor Subset): added to number-theory-and-combinatorics "later", beside Gaussian
  elimination.
- Trie over bits (CSES Maximum Xor Subarray): added to string-algorithms "later".
- Silver functional graphs: advanced-graphs 1 is now in the USACO goal line.
- Already named "later", so left: ternary search, meet in the middle, Mo's and square root decomposition,
  small-to-large, HLD, centroid, convex hull trick, bitset, divide-and-conquer DP.
- Left out, beyond Expert: virtual tree, Kruskal reconstruction tree, divide-and-conquer static range queries,
  dynamic connectivity.
- Covered another way: LCA by Euler tour (USACO Gold, optional) is covered by binary lifting in graphs-and-trees 10.

Interview gaps against TIH: every High and Mid topic has a home: Array, String, Hash table, Recursion, Sorting
and searching, Matrix (dsa-core-techniques 2, graphs-and-trees 3), Linked list, Queue, Stack, Tree, Graph, Heap,
Trie, Interval. DP (Low) is in recursion-and-dynamic-programming. Binary and Math (Low): interview "later" now
reads "bit manipulation and math (TIH: low)", and the operators are in dsa-core-techniques 1. Geometry (Low;
only K Closest Points) is covered by interview 8.

#### 3. Prerequisites
- Every `needs:` is unchanged and correct: no card relies on a card it does not need.
  - number-theory-and-combinatorics 10 used "the adjacency matrix" (graphs-and-trees 1, not a need). It now
    defines it inline ("a[i][j] the number of edges from i to j").
  - computational-geometry 6 uses `std::gcd` (a library call; Euclid stays in number-theory).
- New cross-card pointers, each to a card in `needs`:
  - recursion-and-dynamic-programming 9 → dsa-core-techniques 5
  - recursion-and-dynamic-programming 11 → dsa-core-techniques 1
  - advanced-data-structures 1 → dsa-core-techniques 7
  - advanced-data-structures 2 → cpp-for-contests 4
  - advanced-data-structures 5 → dsa-core-techniques 3
  - advanced-data-structures 11 → graphs-and-trees 11
  - string-algorithms 3 → dsa-core-techniques 6
  - string-algorithms 7 → recursion-and-dynamic-programming 5
  - string-algorithms 9 → advanced-data-structures 4
  - string-algorithms 11 → advanced-data-structures 3
  - advanced-graphs 1 → graphs-and-trees 10
  - advanced-graphs 3 → graphs-and-trees 7
  - number-theory-and-combinatorics 8 → dsa-core-techniques 1
  - computational-geometry 9 → dsa-core-techniques 10 and cpp-for-contests 6
  - interview-problem-solving 9 → dsa-core-techniques 5
- Map "Needs first":
  - competitive-programming row 8 is now "2, 3, 6", exactly the card's needs; it was "3, 6".
  - All other rows of both maps agree with their cards.
- Main topics, checked against the cards:
  - Row 2 now names complete search.
  - Row 3 says "recursive search".
  - Row 4 adds union-find.
  - Row 7 is now "inverses, binomials, expectation, matrices, games", with "decide games" in "After it" (R2's
    point).
  - Row 8 adds trie.
  - Row 9 adds functional graphs.
  - coding-interviews row 3 adds complete search and greedy.

#### 4. Goals
competitive-programming:
- First rated contests: verified as it stands.
- NEW, for learner (a): "Get properly good in a year at ten hours a week (towards Codeforces Expert),
  interview-ready on the way: this book rows 1 to 4; next row 5 and interview-problem-solving; then rows 6, 7;
  then 8 to 10." The rows' hours come to about 470, which is about a year at 10 h/week (judgement, on the
  unverified line). Placement decides which of row 1 is held.
- USACO line:
  - Bronze adds row 4 step 1 (USACO Bronze "Introduction to Graphs").
  - Silver functional graphs moved into the line as row 9 step 1, placed under Gold because it uses row 4
    step 10 (binary lifting is Platinum in USACO, so Silver cannot include it).
- 1500-1800: verified.

coding-interviews:
- New graduate: now "dsa-core-techniques 1-11; row 4 all; …". Step 12 is now CSES mixed and construction sets,
  which are contest work; interview 13 does the unseen practice.
- For learner (b) (Python, three months): "Short on time" now says how to fit the new-graduate line into TIH's
  roughly 11 hours a week for three months. Take dsa-core-techniques 10, DP 6-9 (TIH ranks DP low) and
  graphs-and-trees 13 short.
- Internship, senior and "compete already": verified against the cards.

Sizes: competitive-programming 900 tokens and coding-interviews 897. To fit, I shortened the sources,
checkpoints, "Why this order" and "Left out" wording.

#### 5. Other conflicts
- coding-interviews "Why this order" no longer says the DSA card is C++-only. It now says the card gives
  Python's names beside C++'s, so a Python learner needs no row 2.
- interview-problem-solving 11 against the DP card: they agree. Both say null/base case, "trust the call(s)",
  and call depth = height. The DP card's Python note (`RecursionError`, go bottom-up) and the graphs-and-trees
  explicit-stack note are consistent with interview 11's skewed-tree warning. The DP card owns "base case" and
  "call stack"; interview 11 uses them untagged.

#### 6. Statuses and new claims
dsa-core-techniques gained new technical claims, so its status is now `built 2026-11-18` and it needs one more
independent review. The claims, each checked:
- "Clearing a whole 2·10^5 array in each of 10^4 tests: 0.7 s before any work": g++ -O2 here, 0.68 s with a
  `long long` and an `int` array, 0.70 s with fresh vectors.
- Codeforces limits often bound the sum of n over tests: codeforces.com/problemset/problem/1915/F, "t ≤ 10^4 …
  The sum of n over all test cases does not exceed 2·10^5".
- `x ^ y ^ y == x`, and the operators: run in Python and C++.
- Rectangle overlap per axis max(0, least right end − greatest left end): 20,000 random pairs against a cell
  count in Python, 0 mismatches.
- USACO Bronze has "Rectangle Geometry", and CSES has "Construction Problems": both pages opened.

The other twelve files had integration edits only (untagging, pointers, moving, wording, map rows), so they keep
`reviewed`. The "later" names I added are CSES task names read from the problem-set list: SOS Bit Problem,
Maximum Xor Subset, Maximum Xor Subarray. `std::gcd` was compiled here (it gives 2 for (−6, 4)).

#### Not resolved (outside my files or my reach)
- python-core is still planned, so learner (b)'s row 1 has no card. dsa-core-techniques' `needs` alternative
  and the Python lines rest on it.
- roles/new-graduate-software-engineer.md still says dsa-core-techniques needs cpp-for-contests (R1, R3).
- Three cards sit at the token limit: interview-problem-solving (2,000), dsa-core-techniques (2,000) and the
  competitive-programming map (900). Any future addition needs a cut.
- `us_path.py check` fails, but only on other teams' files: reliability-and-observability size, web/full-stack,
  and system-design-interviews word notes. Nothing names my files.
- cpp-for-contests: coordinator added one wrong belief on [1,8] after two blind judges caught chapters overclaiming what the sanitizers catch; run with g++ 13 here: v.reserve(100); v.push_back(1); v[5]=7 prints 7 under -fsanitize=address,undefined and aborts under -D_GLIBCXX_DEBUG.
- Coordinator, 19 November: hours made equal across maps (one home per fact): python-core 40 h in core-cs/coding-interviews.md (was 30; the AI map and the card's 14 steps say 40), docker 30 h in web/full-stack.md and ai/ai-engineering.md (was 20; the DevOps map, its home track, says 30).

## R4: Networking, SQL, git, API design, the new-graduate role

### R4: review record (stages 4 and 5, second design), 2026-11-18

Files: cards/networking-basics.md, cards/sql-and-relational.md, cards/git.md, cards/api-design.md,
roles/new-graduate-software-engineer.md. All five marked `reviewed`. `us_path.py check` has no ERROR and no note for
any of them (the run as a whole fails on other reviewers' files: interview-problem-solving, node-and-express, react).

#### cards/networking-basics.md, reviewed 2026-11-18 (score 8/10; 1,695 tokens)
- Sources opened: hpbn.co contents (Networking 101 then HTTP then browser APIs: the card's order) and
  /primer-on-latency-and-bandwidth (quoted: 200,000,000 m/s in fibre; New York to London 56 ms and to Sydney 160 ms
  round trip; "10-65 ms" last mile: all match); gaia.cs.umass.edu/kurose_ross/eighth.php (top-down kept; chapters
  4-5 network layer, 7 mobile). Dean and Norvig gist, MDN and the Facebook 2021 post were not reopened (unchanged
  claims, confirmed by the previous review).
- Outlines compared: HPBN contents; Kurose and Ross 8th ed. Gaps: wireless and mobile networks (HPBN part II,
  K&R ch. 7), WebRTC, WebSocket and SSE (HPBN part IV): added to "Later" (WebSocket and SSE pointed at api-design,
  which teaches them). Routing and link layer were already under "Later".
- Compared with HEAD~1: the lost "Project" step was only a heading (the project lives in "Practice and project").
  Lost in conversion and restored: the hand-written socket server and client (step 4), without which the [5]
  byte-stream belief had nothing to show it. "Proxies hide the client address" and "refused / timed out / not
  resolved told apart" survive as step 9 and the failures.
- Run: curl exit 6 (`.invalid` name), 7 (closed port), 60 (openssl s_server certificate for other.test, trusted
  with --cacert, asked as localhost: "no alternative certificate subject name matches"), and **exit 28 produced
  both ways**: a connect timeout to a listener whose backlog was full (`--connect-timeout 2`: "Failed to connect
  ... Timeout was reached") and a read timeout from a server that accepts and never answers (`-m 2`: "Operation
  timed out ... 0 bytes received"). `curl -w` dns/connect/appconnect/starttransfer fields printed. Two `send`s
  read by one `recv` (b'hello world'). Not runnable here: ping, dig +trace, traceroute to remote hosts.
- Changed: step 3 names the resolution walk (stub, recursive, root, TLD, authoritative) and AAAA; step 4 adds the
  socket programs and 127.0.0.1 against 0.0.0.0 binding (the cause of the refused-connection failure); step 5
  shows the byte stream with step 4's programs; step 8 adds an HTTP request written by hand, HTTP/2 multiplexing
  and HTTP/3 over QUIC; step 9 adds the standard `Forwarded` header and where TLS ends; the exit-28 failure adds
  the read timeout; "In production" regains the round-trip line (sourced to hpbn, not "mostly"); words
  `multiplexing`, `QUIC` on [8].
- Still unverified: the Dean and Norvig figures are a 2012 list (the card says so).
- Holds it back: steps 2, 3 and 4 depend on outside hosts the learner's network may block (ICMP); the card
  should say what to do then, and has no room-free way to.

#### cards/sql-and-relational.md, reviewed 2026-11-18 (score 8.5/10; 1,962 tokens)
- Sources opened: postgresql.org/docs/18 indexes-multicolumn (skip scan, quoted); use-the-index-luke.com table of
  contents (anatomy, where clause, functions, bind variables, LIKE, partial indexes, joins, top-N and paging,
  DML cost). PostgreSQL contents, transaction-iso, DDIA ch. 7 and dbi-services were confirmed by the previous
  review and every claim drawn from them was re-run (below).
- Outlines compared: PostgreSQL documentation contents (SQL language, then administration); Use the Index, Luke.
  Gaps fixed: join methods in a plan (nested loop, hash, merge) into step 8; types for time and money into 5;
  `RETURNING`, `MERGE` and a batched backfill into 7; backups restored and `pg_stat_statements` named in 11.
  Left under "Later" with reason (not needed for the promise): MVCC and VACUUM, views, roles and GRANT, jsonb,
  full-text search, table partitioning, partial indexes.
- Run (PostgreSQL 16.15, own cluster in /tmp as user postgres, three psql sessions driven by a script): every
  "How it runs" line. Alias in WHERE: `column "dd" does not exist`; works in ORDER BY; aggregate in WHERE: "aggregate
  functions are not allowed in WHERE"; `NULL = NULL` null; `g <> 'a'` dropped the NULL row; `NOT IN` with a NULL
  returned 0 rows, `NOT EXISTS` 3; count(*) 4, count(v) 3, avg over three, sum of no rows NULL; two items and two
  payments: 4 rows, both sums 60 instead of 30, pre-aggregated 30/30; 200,000 rows: email index scan, lower(email)
  parallel seq scan then index scan once indexed, country = 'US' (90%) seq scan, created alone on (country,
  created) seq scan; lost update at read committed (10 to 9 twice); `n = n - 1` and `FOR UPDATE` correct;
  repeatable read: "could not serialize access due to concurrent update" (SQLSTATE 40001 shown with VERBOSITY
  verbose); write skew commits at repeatable read, serializable aborts one ("read/write dependencies"); "deadlock
  detected"; ALTER TABLE waiting behind an open transaction makes a later SELECT wait too; `lock_timeout` cancels
  it; ON CONFLICT upsert; MERGE; RETURNING; keyset row comparison uses an index on (created, id) only once it
  exists (seq scan before); default isolation "read committed".
- Changed: the composite-index claim was version-bound: now "on 16 ... (18's skip scan may, when `country` has few
  values)" with the 18 docs as source and the version on "Look up"; step 9 retries 40P01 (deadlock) as well as
  40001 and names a UNIQUE constraint as the cheapest lock; step 10 names the keyset query and its index (without
  it the "fix" is still a scan), and "no transaction open across a network call"; steps 1, 5, 6, 7, 8, 11 given
  the concrete thing each teaches; a failure for the multiplying join ([4]).
- Still unverified: MySQL not run (said on `unverified:`); the skip-scan clause read, not run (no PostgreSQL 18).
- Holds it back: eleven steps and "How it runs" leave no room for one PostgreSQL-against-MySQL difference table,
  which a learner on MySQL needs.

#### cards/git.md, reviewed 2026-11-18 (score 8/10; 1,909 tokens)
- Sources opened: plans/learn-git/PLAN.md (all 17 chapters and their sections read against the steps);
  git-scm.com/book/en/v2 contents (known chapter list: basics, branching, server, distributed, GitHub, tools,
  customizing, internals) used as the second outline.
- Outlines compared: the plan; Pro Git. Compared with HEAD~1: the conversion merged "Configuration and hooks" and
  "Large repositories" into one grab-bag step, and dropped from the steps: merge-or-rebase (a "Go deep" item with
  no step), cherry-pick, `pull --rebase`, amend, autosquash, reverting a merge, `restore --source`, ORIG_HEAD,
  CODEOWNERS, commit conventions, `bisect run`, aliases, partial clone and sparse checkout. All restored; the
  merged step split back into 13 (config and hooks) and 14 (large repositories). Pro Git items left under
  "Later": rerere, bundles, migration, servers.
- Run (git 2.43, /tmp): layout of .git; `reset --hard` drops staged and unstaged edits, keeps untracked;
  `reset --keep` refuses ("Entry 'f' not uptodate") and keeps the edit; `checkout -- g` and `restore g` both
  restore the staged copy; `git clean -n` does NOT list directories, `-nd` does; `branch -d` "not fully merged",
  `-D` deletes; plain push rejected; `--force-with-lease` "stale info" before a fetch, succeeds after any fetch
  (dropping the other clone's commit); `--force-with-lease --force-if-includes` refused ("remote ref updated since
  checkout"); hard reset leaves dangling blobs found by `fsck`; also every command added: `revert -m 1`,
  `config --show-origin`, `rebase -i --autosquash` of a `fixup!` commit, `bisect run` finding the first bad
  commit, `stash -u`, `worktree add`, a failing pre-commit hook via `core.hooksPath` and `--no-verify`, partial
  clone (needs `uploadpack.allowFilter` on the server), `sparse-checkout set`, `--depth 1`, a commit built with
  hash-object/update-index/write-tree/commit-tree, `gc` to a packfile.
- Changed: the steps above; State and danger's safe form for `git clean -fd` was `git clean -n`, which hides the
  folders `-fd` deletes: now `git clean -nd`; steps 2, 3, 5, 7, 10, 11 name what is taught; words: `tag` became
  `annotated tag` and `merge` became `three-way merge, merge commit, merge base` (the bare words collided with
  advanced-data-structures' lazy-propagation `tag` and segment-tree `merge`, different meanings); `cherry-pick`,
  `sparse checkout` added; [14] words split from [13].
- Still unverified: nothing material.
- Holds it back: no step on reviewing other people's diffs as a skill (only "review comments given and
  answered"); the plan has it (7.6-7.11) but the card is near the limit.

#### cards/api-design.md, reviewed 2026-11-18 (score 7.5/10; 1,998 tokens)
- Sources opened: datatracker draft-ietf-httpapi-idempotency-key-header (-08, 2026-10-22, WG Document, not an RFC;
  400 missing, 422 same key other payload, 409 still processing: matches the card) and
  draft-ietf-httpapi-ratelimit-headers (-11, 2026-05-23, WG Document; defines `RateLimit` and `RateLimit-Policy`);
  RFC 9457 (members type, status, title, detail, instance; `type` is the primary identifier; about:blank);
  RFC 9745 (`Deprecation`, March 2025, Sunset from RFC 8594, which the card cited without listing: added);
  google.aip.dev/180 (breaking changes: removal, rename, type, new required field, default, format, semantics;
  enum values in responses need caution). RFC 9110, 6585, 6750, 7396 meanings checked from knowledge of the texts
  (201 + Location, 401 MUST send WWW-Authenticate, 422 in 9110, 428/429 in 6585, invalid_token 401 and
  insufficient_scope 403, merge patch null deletes, arrays replaced).
- Outlines compared: Google AIP index; Microsoft Azure REST guidelines and Zalando guidelines (the card's own
  outline sources, not reopened). Gaps left under "Later": OAuth flows, hypermedia, CORS (unchanged).
- Changed (the limit rose to 2,000, so every terse step now carries its decision): 1 PATCH neither safe nor
  idempotent, custom methods; 3 why IDs are strings, offset in times, minor units plus ISO 4217; 4 which failures
  a client retries and the 9457 members including `instance`; 5 cursor contents, AIP-158 token fields, why paging
  must ship in release one; 6 token bound to filter and order; 7 the three failure points, what the server stores
  and in which transaction (pointing at caching-and-queues 8, where the mechanism is taught), the draft's three
  codes; 8 merge-patch rules, 412 against 428; 9 the AIP-151 operation; 10 **a factual fix**: the card said a
  token bucket does not admit twice the limit across a boundary; a bucket admits burst plus rate x time, so it
  can, unless the burst is sized: now "a sliding window or token bucket (rate plus chosen burst) bounds it"; the
  RateLimit headers named as an IETF draft; 11 invalid_token against insufficient_scope; 12 HMAC over timestamp
  and raw body, constant-time compare; 13 AIP-180 list, Deprecation and Sunset by RFC; 14 gRPC field numbers,
  GraphQL N+1 and cost limits. Load shedding: the word stays owned and taught by reliability-and-observability
  (step 7); api-design uses it untagged and points there. `scope` renamed `OAuth scope` (collided with
  javascript's lexical scope). Failure added: webhook signatures failing because the body was re-serialised.
- Still unverified: Idempotency-Key and RateLimit are drafts whose codes and names may change (on `unverified:`
  and "Look up").
- Holds it back: 14 steps at exactly the limit; "Judged by" has no test for steps 3, 9 or 14. It is a candidate to
  split (core contract 1-8; events, change and alternatives 9-14) when maps can absorb a second id.

#### roles/new-graduate-software-engineer.md, reviewed 2026-11-18 (score 7/10; 798 tokens)
- Sources reopened: Stripe New Grad (jobs.generalcatalyst.com copy, posted 2026-09-02: AI tools minimum, code
  review and safe production changes preferred, backend/infra specialism preferred, no SQL, git or testing);
  Google Early Career Campus (jobs.anitab.org, posted 2026-08-14: DS/algorithms and AI tools minimum, Linux,
  networking, distributed systems preferred, "test" among duties); Dropbox IC1 (code reviews, well tested,
  on-call); metacareers.com/swe-prep-techscreen (a 45-minute technical screen; added as the source for the
  interview line). Google's how-we-hire page says nothing about coding interviews, so it was not used.
- Changed: added interview-problem-solving (3 Build, essential; proof: the card's three recorded, scored mocks)
  and pointed the first interview check at it; dsa-core-techniques' cell no longer claims "interviews (4 of 7)"
  (the adverts name DS/algorithms, not interviews) and its proof is no longer the interview card's;
  first-programming-language (planned) became python-core (planned), the id the curriculum already plans and
  that dsa-core-techniques needs; scaling-data removed (its "data-heavy teams" cell had no source);
  caching-and-queues' specialist class now rests on Stripe's preferred backend specialism; hours recomputed from
  the maps: 345 for essential and desirable lines (python-core 30, dsa 60, interview 50, SQL 30, networking 25,
  design 30, DP 60, graphs 60), marked as the maps' judgement; Overlap points at core-cs/coding-interviews.
- No line is `(planned)` that has a card now (checked against `ls curriculum/cards`; software-testing,
  operating-systems-core and ai-assisted-development still have none).
- Still unverified: classes of the DP and graphs lines (no advert names them).
- Holds it back: at 800 tokens it cannot say which roles' adverts ask for API design (none sampled do), so
  api-design is absent although the full-stack map's first-job goal uses it.

#### Conflicts for someone else
- system-design/foundations.md row 8: "Needs first 3, 4" while api-design needs networking-basics and
  sql-and-relational too (rows 1 and 2); rows 4 and 5 list them explicitly. Harmless transitively, inconsistent.
- web/full-stack.md "My first full-stack job" takes api-design 1-8 with caching-and-queues `later:`; api-design 7
  now points at caching-and-queues 8 for the stored-key mechanism, so that chapter's writer must teach the
  UNIQUE-constraint store in place (one paragraph), or the map should take caching-and-queues 8.
- Not checked: remote ping/dig/traceroute (sandbox network); PostgreSQL 18 skip scan (docs only); MySQL.


## R5: System design foundations, caches and queues, scaling data, the map

### R5: system design foundations track (stage 4-5 review, second design)

Reviewer: independent agent (did not write these files). Repository:
/home/claude/ckpt/understudy-checkpoint/understudy/curriculum. No git command run.
Read first: FORMAT.md, REVIEWING.md, us-map from-a-card.md, writers-guide.md, and the neighbouring cards
networking-basics, sql-and-relational, distributed-systems-core, reliability-and-observability, api-design,
system-design-interviews.

#### cards/system-design-foundations.md, reviewed 2026-11-18 (marked; 1,998 tokens; score 8/10)
- Sources opened: sre.google workbook/non-abstract-design (the four questions; AdWords CTR numbers: 100 TB/day,
  ~2,500 disks, ~1,563 machines); sre-book service-level-objectives (SLI, SLO, SLA "consequences");
  availability-table (99.9% = 8.76 h a year, 43.2 min a month); cacm the-tail-at-scale (1 in 100 slow, 100 servers
  gives 63%; hedged requests after p95, ~5% extra load); builder.aws.com avoiding-insurmountable-queue-backlogs
  (100 a second at 100 ms is 10 threads, at 10 s 1,000); HikariCP About-Pool-Sizing (2,048 to 96 connections,
  ~100 ms to ~2 ms, "over 50x"); wikipedia Little's law and M/M/1 queue (time in system 1/(μ−λ));
  industrialempathy design-docs-at-google (context and scope, goals and non-goals, design, alternatives,
  cross-cutting concerns).
- Outlines compared: system-design-primer index; SRE workbook NALSD + Google design-doc structure. Gaps fixed:
  SQL or NoSQL data models (key-value, document, wide-column) now in step 5; active-passive / active-active,
  service discovery, sticky sessions, autoscaling in step 6; failure domains / availability zones in step 7;
  microservices and monolith as words; utilisation and queueing delay in step 4 (absent before, the most-used
  argument in a capacity review); cost as a requirement (step 1-2, Judged by). Left: graph databases, federation
  (federation is now scaling-data step 1), security design (Later and map "Left out").
- Run: python3: 0.999^3 = 0.997; 1 − 0.99^100 = 0.634; 8,760 × 0.001 = 8.76 h; 86,400 s/day.
- Changed: "In production" now says what must happen in the learner's own system (peak traffic counted, first
  resource to run out predicted by arithmetic, then exhausted by a load test, the two compared). Step 4 given
  real arithmetic (Little's law worked example from the Builders' Library; M/M/1 1/(1−ρ): 2x at 50%, 10x at 90%).
  New wrong belief "at 80% busy there is 20% to spare" (M/M/1: already 5x). HikariCP belief made traceable: the old
  text said "50 times faster" without whose demo; the page credits Oracle and reports ~100 ms to ~2 ms, now said. Step 1
  lists the non-functional families; step 2 gives the 86,400 formula, QPS, replicas in storage, cost looked up;
  step 3 adds p99.9 from histograms and hedged requests; step 7 separates durability from availability (the word
  was tagged but never taught) and adds the 43.2-minute month. Step 9 trimmed of the AdWords name: it is reading
  material read beside the learner's design, not a case (rule 8). New failure: random logouts after scaling out
  (in-memory sessions). Words added: QPS, hedged request, utilisation, key-value/document/wide-column store,
  failure mode, monolith, microservice, sticky session, service discovery, autoscaling, active-passive,
  active-active, failure domain, availability zone.
- Still unverified: none beyond judgement of order. Holds it back: the step list is dense; a writer gets the
  decisions but the card is at its limit, so steps 5 and 6 cannot carry more.

#### cards/caching-and-queues.md, reviewed 2026-11-18 (marked; 1,825 tokens; score 8/10)
- Sources opened: NSDI 2013 Scaling Memcache (delete because idempotent; token once every 10 s per key; peak
  17K/s to 1.3K/s, all quoted); builder.aws.com queue backlogs ("300 minutes" after a ~30-minute unthrottled spike
  at 10x consumer capacity; a one-hour outage needs double capacity for another hour; message age; DLQ "too
  late"); sre-book addressing-cascading-failures (limit retries per request; 60 retries a minute per process;
  three layers x 4 attempts = 64; randomized exponential backoff); aws.amazon.com/message/12721 (7 December 2021,
  clients not "adequately backing off"); gist jboner/2841832 ("~2012": 100 ns, 500 µs); kafka.apache.org/intro
  (events kept after consumption, order per partition).
- Outlines compared: system-design-primer cache and asynchronism parts; Azure patterns catalogue. Gaps fixed:
  log-based brokers (Kafka: retention, per-partition order, consumer groups, offsets, consumer lag) were missing
  though they are the broker most heard in reviews: step 6. Left: refresh-ahead, priority queue, claim check
  (minor); stream processing, event sourcing, CQRS now named under Later (data-intensive-systems, planned).
- Changed: Numbers [2] now dated (Dean and Norvig, about 2012; today's looked up) and states the ratio;
  [10] reworded to what the Builders' Library actually says (it does not say "queues 300 minutes"; it says
  draining takes 300 minutes) plus the one-hour-outage figure. Step 2 says what each cache place costs; step 4
  names the eviction-policy setting to look up and the hit-ratio curve; step 7 defines at-most-once/at-least-once
  by when `ack` happens and names SQS redelivery after the visibility timeout; step 9 now carries decisions (one
  retrying layer, the SRE book's retry budget example, circuit breaker meaning, DLQ after N attempts). The retry
  storm failure now uses the SRE book's own number (3 layers x 4 attempts = 64) instead of an unsourced 27.
- Still unverified: consumer groups and offsets are certain Kafka terms but are not on the intro page opened.
- Holds it back: step 10 (overload) overlaps reliability-and-observability step 6-7; the split is stated in
  Later but a writer could teach the retry multiplication twice.

#### cards/scaling-data.md, reviewed 2026-11-18 (marked; 1,994 tokens; score 8.5/10)
- Sources opened: DDIA 2nd ed. ch. 6 and 7 contents (setting up followers; replication-lag solutions; leaderless;
  sharding by key range / hash; skew and hot spots; rebalancing; request routing; local and global secondary
  indexes; sharding for multitenancy); github.blog oct21 (43 s; West Coast took writes "for nearly 40 minutes";
  954 writes on one busy cluster; 24 h 11 min); discord.com trillions-of-messages (channel + static time bucket;
  hot partition affected latency across the cluster through quorum reads; data services coalesce; 177 Cassandra
  nodes in 2022); infoq CAP twelve years later; AWS Aurora.Replication ("usually much less than 100
  milliseconds", more under heavy writes); hpbn.co (New York-London 56 ms RTT in fibre).
- Outlines compared: DDIA 2nd ed. ch. 6-7; system-design-primer database part. Gaps fixed: new followers from a
  snapshot plus the log; federation (split by function) in step 1; replication factor, read repair; multitenant
  key; local/global indexes (2nd-ed words) with DynamoDB LSI/GSI as the concrete carrier; RPO/RTO. Left: storage
  engines (LSM trees), change data capture, CRDTs (Later); multi-region sync engines (DDIA 2nd ed.) left out as
  too specialised.
- Run: PostgreSQL 16 primary + standby in /tmp (`pg_basebackup -R`): `pg_stat_replication` shows the walreceiver,
  `replay_lag` empty while idle; INSERT on the standby gives "cannot execute INSERT in a read-only transaction";
  `pg_last_wal_replay_lsn()` works; `pg_promote()` on the standby, then INSERT succeeds on both standby and old
  primary (split-brain made to happen). Python: `hash mod N` from 10 to 11 nodes moves 90.9% of keys; a
  consistent-hash ring with 100 virtual nodes moves 8% (≈1/11).
- Changed: every step rewritten to name its mechanism, setting or number (the thin steps were 1, 5, 6, 7, 8, 9,
  11): step 1 the four measurable limits; step 3 each anomaly with its symptom and three fixes; step 4 heartbeat
  timeout trade-off, `pg_promote()`, RPO/RTO, fencing; step 5 n/w/r with read repair; step 6 range vs hash
  trade-off and the key chosen from the queries that must stay on one shard; step 7 key splitting by suffix;
  step 8 local (scatter-gather, slowest shard) vs global (late updates); step 9 fixed partitions, virtual nodes,
  routing choices; step 11 the design that keeps transactions inside one key. New Numbers: hash mod N vs ring
  (simulated), Discord trace, the split-brain run. GitHub line corrected to the post's words (it was "nearly 40
  minutes of writes on the other coast", kept; added 954). Wrong belief "a read replica takes load off writes"
  said writes "run" on every copy: now "applied" (replicas replay WAL, they do not re-execute). New failure:
  most data moving when a node is added. Words added: IOPS, consistent prefix, heartbeat, RPO, RTO, replication
  factor, read repair, key-range/hash partitioning, local/global index, virtual node.
- Still unverified: "replicas before sharding" (judgement, on the line).
- Holds it back: CAP is taught both here (step 10) and in distributed-systems-core step 12 (see conflicts).

#### system-design/foundations.md (track map), reviewed 2026-11-18 (marked; 900 tokens; score 8/10)
- Checked every row's "Needs first" against the cards' `needs:` and made them exact: row 6 was "4, 5" (card needs
  networking, sql, caching, scaling: now 1, 2, 4, 5); row 8 was "3, 4" (now 1, 2, 3, 4); row 9 was "4, 5, 8"
  (card needs system-design-foundations too: now 3, 4, 5, 8).
- Removed every trace of the dropped row 10: "Why this order" ("outages (10)"), "Checkpoint projects" ("After 10"
  replaced by "After 7": burn-rate alerts and a survived overload test), `sources:` ("sre-book ... 10"). "Left
  out on purpose" now says outages are read inside 7, and that security design has no card. Sources now name
  system-design-primer (opened) instead of the Azure catalogue.
- Goals checked against the cards' real steps (spine run for every step range): the design-review line now adds
  row 8 (APIs are reviewed in every design review) and distributed-systems-core 1-2 and 11 (unknown outcomes after
  a timeout, the dual-write bug and outbox: questions a backend reviewer meets weekly); the interviews line now
  takes sql-and-relational 5 (modelling: core entities) and networking-basics 10 (timeouts) and drops 7 (TLS); a
  new line for the blind-test learner ("design reviews now, interviews within months: the first line, row 9
  last"). Her planner would previously have picked one of two lines and missed either api-design or
  interviews; now one line covers both.
- Still unverified: hours and levels (judgement, on the line). Holds it back: at exactly 900 tokens nothing more
  can be said about why 7 precedes 8.

#### system-design/INDEX.md, reviewed 2026-11-18 (marked; 164 tokens; score 9/10)
- Checked: `foundations` exists; planned tracks agree with the map's "Left out" (data-intensive-systems now also
  named in caching-and-queues Later); role new-graduate-software-engineer exists. No change beyond the status.

#### Vocabulary of the track as a whole (`us_path.py words system-design/foundations`)
Added to my cards (see above). Still with no home in any card of the track, for other reviewers:
- ACID (sql-and-relational step 9 teaches it but owns no word "ACID"; distributed-systems-core uses it).
- bulkhead, blue-green deployment (reliability-and-observability steps 7 and 9).
- noisy neighbour / multi-tenancy (could go to reliability 7 or scaling-data 6; left: card at limit).
Double ownership to resolve on the other side (my cards keep the word where the mechanism is taught):
- system-design-interviews owns QPS, bottleneck, failure mode (taught in system-design-foundations 2, 4, 5) and
  pub/sub (= publish-subscribe, caching-and-queues 6) and visibility timeout (now taught in caching-and-queues 7,
  untagged there): drop them from its words. A learner on the design-review path never takes that card, so the
  words must live in foundations.
- node-and-express (new card) owns pool exhaustion and backpressure: the general mechanism is
  system-design-foundations 4 (Little's law, N/T) and caching-and-queues 10; node-and-express should use them
  untagged, or own only the Node-specific terms (stream backpressure is a different, Node-streams sense: if that
  is what it teaches, it may keep a distinct word such as "stream backpressure").
- CAP: one home in scaling-data 10 (the design-review learner stops before row 6). distributed-systems-core 12
  should take CAP as known and teach only its exact terms against ACID and PACELC.
- Retry multiplication: caching-and-queues 9 owns "retry storm" (64 = 4^3, SRE book); reliability step 6 repeats
  it with 243x: it should refer to caching-and-queues rather than reteach.


## R6: Distributed systems, reliability, design interviews

### R6: review record (distributed-systems-core, reliability-and-observability, system-design-interviews)

Reviewer: independent agent, principal-engineer lens. Date 2026-11-18. Read in full: FORMAT.md, REVIEWING.md,
from-a-card.md, writers-guide.md, and the neighbouring cards system-design-foundations, caching-and-queues,
scaling-data, api-design, and the track map system-design/foundations.md. curl was blocked by the proxy (403 on
every host), so every source was opened with web fetch.

#### cards/distributed-systems-core.md, reviewed 2026-11-18
- Sources opened:
  - raft.pdf: the 150-300 ms timeout, the 0.5-20 ms broadcast time, the timing inequality, the vote rule (later
    last term, else longer), the commit rule and Figure 8 (an entry is never committed by counting replicas from
    an earlier term), §8 serial numbers, §8 reads (no-op, heartbeat with a majority, a lease that "assumes bounded
    clock skew"), §9.3.
  - Lamport time-clocks: the three rules of happened-before, IR1 and IR2, and that the converse of the clock
    condition does not hold.
  - Spanner §3 (not §5): 30 s poll, 200 µs/s, sawtooth of about 1-7 ms.
  - aphyr 299: last-write-wins timestamps lose writes; NTP does not fix it.
  - Kleppmann 2016: pause past the lease, fencing token, zxid.
  - Jepsen etcd-3.4.3: 1-3 s TTLs failed within minutes in healthy clusters; the lock revision used as a fencing token.
  - Jepsen linearizable page: real time, one object, not totally available.
  - MIT 6.824 2PC notes: log before YES, COMMIT logged before it is sent, blocking with locks held, Raft-replicated
    participants.
  - microservices.io saga: no isolation; outbox.
  - Abadi PACELC: definition, PA/EL, PC/EC.
  - CAP: Gilbert-Lynch 2012 "Perspectives" (atomic memory, a response to every request, lost or delayed messages),
    Kleppmann 2015 "stop calling databases CP or AP" (every non-failing node; neither CP nor AP), Brewer 2012
    (C is single-copy consistency).
  - The quorum claim, which was written from memory, now has a source: Kleppmann's Cambridge "Concurrent and
    Distributed Systems" notes §7.2, slide "Not linearizable, despite quorum reads/writes", and the ABD fix.
- Outlines compared:
  - MIT 6.824 schedule. Covered: Raft, linearizability, ZooKeeper, distributed transactions. Added to "later":
    chain replication, Byzantine faults (already there), Spanner's TrueTime, verification (TLA+). Left out:
    FaRM, Bitcoin and SUNDR, which are research topics beyond the promise.
  - DDIA 2nd ed. chapters 9-10. System models (crash-stop, crash-recovery, Byzantine; no bound on delay) were
    missing: added to step 1. Safety against liveness was missing: added to step 7. Linearizable ID generators
    are left to scaling-data and to "later".
- Run: arithmetic only (nothing here runs locally). `us_path.py check`: no ERROR, no note.
- Changed:
  - Step 6 now carries the sourced counter-example ({A,B} then {B,C}), the ABD fix and sloppy quorums. The wrong
    belief on w + r > n was reworded to match.
  - Step 7: the vote rule exactly as the paper states it; safety never depends on timing.
  - Step 8: Figure 8's commit rule. New wrong belief: "an entry on a majority is committed".
  - Step 9: Raft's own read fixes, and that a lease trusts clock skew.
  - Step 10: what is logged, and when. The wrong belief now reads "survives a coordinator crash"; "always finishes"
    was a straw man.
  - Step 12: CAP stated as proved (lost or delayed messages; linearizable; every request at every non-failed node
    answered; partitions are not a choice; "neither CP nor AP"), plus PACELC. This card now owns the exact
    statement.
  - Step 2: builds on caching-and-queues 8 and no longer re-teaches the idempotency key.
  - Step 3: `CLOCK_REALTIME` and `CLOCK_MONOTONIC`.
  - Step 4: the three rules of happened-before, and ties broken by process id.
  - The Spanner number is attributed to §3.
  - In production: 2PC is used inside one database system and should not be dismissed outright.
  - New words: crash-recovery, sloppy quorum, safety, liveness.
- Still unverified: none of the card's facts. The 40 hours on the map are judgement (the map is not mine).
- Score 8/10. Most holds it back: at 2,000 tokens, steps 6-10 are dense lists that a writer must unpack. The card
  would read better split into "time, order and consistency" (steps 1-6) and "agreement" (steps 7-12).

#### cards/reliability-and-observability.md, reviewed 2026-11-18
- Sources opened:
  - SRE workbook "Alerting on SLOs": 14.4 over 1 h with a 5 min window (2% of the budget); 6 over 6 h with a 30 min
    window (5%); 1 over 3 d with a 6 h window (10%, ticket); short window 1/12 of the long one.
  - SRE book SLO chapter: Chubby planned outages; client-side SLIs.
  - SRE book monitoring chapter: the four golden signals; slow errors; histogram buckets; "every page should be
    actionable".
  - SRE book "Handling overload": K = 2, criticalities, "overloaded; don't retry", retry budgets.
  - SRE book "Managing incidents": the four roles (planning was missing), the living document, when to declare
    an incident.
  - Builders' Library (now at builder.aws.com): timeouts at p99.9 for 0.1% false timeouts; "243x" over five layers
    of three tries; health-check kinds and fail-open.
  - HotOS 2021 paper: 300 QPS capacity, 280 normal, 560 with retries, recovery only below 150.
  - wrk2 README: `-R`, coordinated omission, latency timed from the scheduled send.
  - OpenTelemetry primer.
  - Three postmortems, each checked against what the card says it teaches:
    - S3 2017: a mistyped input; subsystems not restarted in years; the status dashboard depended on S3.
    - Cloudflare 2019: a backtracking regex in a WAF rule pushed globally; the CPU guard removed in a refactor
      weeks earlier; the internal panel unreachable because Access was down.
    - Roblox: 73 h; the Consul streaming feature and BoltDB; a circular dependency between telemetry and Consul.
      The listed URL was wrong: fixed to the newsroom post dated January 2022.
- Arithmetic: 30 × 1,440 × 0.001 = 43.2 is correct, but only for a total outage. Under the card's own request-based
  SLI the budget is 0.1% of requests. Step 2 now says so (pointing to foundations 7, which owns nines-as-downtime),
  and a new wrong belief covers it. 3^5 = 243 is correct.
- Outlines compared: SRE book contents and SRE workbook contents. Data integrity (backups, restore drills) and
  capacity planning were missing: both added to "later". Toil and on-call were already there. Release
  engineering is covered in step 9. Load balancing belongs to foundations.
- Run: `python3 -c` for 43.2 and 243. Check: clean.
- Changed:
  - Step 5: the full alert table and the meaning of burn rate.
  - Step 6: the metastable mechanism (trigger, then a sustaining effect).
  - Step 7: client-side throttling stated as the book has it (probabilistic, above 2× accepts).
  - Step 8: rewritten in the Builders' Library terms. The old "readiness never tests a shared dependency" was not
    the source's claim. Kubernetes names are now looked up when the book is planned. The word "readiness check" is
    replaced by "dependency check".
  - Step 9: staged rollout, config treated as a change, expand-and-contract migrations.
  - Step 10: open and closed loop defined.
  - Step 11: when to declare an incident, and the planning role.
  - In production: each postmortem's actual lesson.
  - Wrong belief [6]: the HotOS numbers.
- Still unverified: nothing factual. The term "expand and contract" comes from practice, not from a listed source.
- Score 8/10. Most holds it back: twelve steps cover two subjects (observability and overload/incident work). A
  writer gets the "what" but must find the depth for steps 4 and 10 alone.

#### cards/system-design-interviews.md, reviewed 2026-11-18
- Sources opened:
  - Meta careers blog: 45 minutes. Its signals are "identify your focus", "holistic and the details", "explore
    tradeoffs", "make it a conversation". The labels "technical excellence" and "problem navigation" are Hello
    Interview's, not Meta's: re-attributed.
  - Added primary sources on grading. Amazon's SDE II prep page: practicality, accuracy, efficiency, reliability,
    optimization, scalability. SRE workbook NALSD: "sound reasoning ... more important than any final values".
    Google's hiring pages render empty and re:Work's structured-interviewing guide is a 404: not used.
  - Hello Interview pages: the delivery budget (5 / 2 / 5 / 10-15 / 10); the four areas; the levels blog ("around
    2" deep dives for senior; staff leads almost everything; nothing on how heavily the round weighs); the
    news-feed, WhatsApp and Dropbox breakdowns (each detail in steps 8, 11 and 12 confirmed).
  - Pragmatic Engineer review of Xu: case-study list, 4-step budget, the memorised-design anecdote.
  - SQS visibility timeout.
- Outlines compared:
  - Xu's contents. The web crawler (and search) has no family: added to "later". The key-value store and
    consistent hashing are owned by scaling-data and distributed-systems-core. The unique ID generator is in step 10.
  - system-design-primer. Security is left to api-design 11.
- Check 9:
  - Every step now names the foundation it applies (foundations 1, 2, 4; scaling-data 6; caching-and-queues 10;
    api-design 10), so each step reads as the foundations under a clock, not a trick.
  - The families stay grouped by the constraint that dominates them, each with what it tests.
  - Step 7 (flagged as naming nothing) now names the concrete failure questions: cache gone, queue age, replica
    lag. It also names a priced rejected option.
  - Step 13 now names the race itself.
  - Step 10 adds 62^7 ≈ 3.5 trillion (run).
- Removed unsupported claims: "weighs heavily" (no source says it). "From senior level up the round is the norm"
  is now attributed to one interviewer's account, and the company's own pages are named.
- Word notes resolved: "bottleneck", "QPS" and "failure mode" are owned by system-design-foundations and removed
  here. Step 7 now carries a sourced wrong belief instead. "race condition" was added for step 13.
- Never omit: "every claim defensible from a foundations card".
- Still unverified (on the card): the families and their grouping; level expectations come from one interviewer.
- Score 7/10. Most holds it back: what "graded" means rests on two company pages and one commercial site. No
  company publishes its actual design rubric, and I could not open one.

#### Conflicts outside my list (not touched)
- system-design/foundations.md (map) refers to "outages (10)" and "After 10", but there is no row 10. The planned
  "learning from public outages" subject now lives in reliability-and-observability 12. The map should say "7 (12)".
- scaling-data owns the words "CAP theorem" and "linearizability" and teaches "CAP as Brewer states it" (step 10).
  This card now owns the exact statement (step 12), so scaling-data 10 should keep only the price and point here.
  I did not tag "CAP theorem" here, to avoid a double home.
- system-design-foundations 7 now states "43.2 minutes a month". It is correct for a 30-day month and full
  downtime. reliability step 2 refers to it.


## INTEGRATION-SD: Editor's pass over system-design

### Integration of the system-design track (editor-in-chief), 2026-11-18

Read in full: FORMAT.md, REVIEWING.md, STAGE45-REVIEW.md, R4, R5, R6; the map, the index and all nine cards as one
book. Ran `us_path.py words system-design/foundations`, `check` (before: no note and no ERROR for my files),
`spine` for every goal line after the edits. No git command run.

#### Decision: distributed-systems-core split in two
At 1,998 tokens it had twelve dense steps on two subjects (DDIA 2nd ed. puts them in two chapters: 9 "The trouble
with distributed systems" and 10 "Consistency and consensus"), and the integration needed room it did not have:
the homes of "CAP theorem" and "linearizability", vector clocks, "strong consistency", "distributed lock". Split:
- `distributed-systems-core` (kept id; 7 steps, 1,877 tokens): 1 partial failure, 2 unknown outcomes, 3 physical
  clocks, 4 logical clocks, 5 histories and linearizability, 6 majorities and quorums, 7 CAP and PACELC (old 1-6, 12).
- `consensus-and-transactions` (new; 6 steps, 1,565 tokens): 1 Raft as a tool, 2 one write, 3 reads, 4 locks,
  leases and fencing (old 9 split into reads and locks), 5 2PC, 6 outbox and sagas (old 7-11).
Every verified statement kept (Raft numbers and rules, Figure 8, §8 reads and serial numbers, Spanner §3, etcd
1-3 s leases, fencing tokens, 2PC logging and blocking, ABD counter-example, CAP as proved, PACELC, all wrong
beliefs and failures). Each card has its own header, sources (only the pages it uses), parts, tags, traces,
project and ladder. Old step numbers were referenced only by the map's Goals (now rewritten); no file outside my
list names them.

#### Per file
**distributed-systems-core.md** (stays reviewed; integration plus verified additions). Rewritten as above. Now
owns `linearizability` (step 5) and `CAP theorem` (step 7); the "pick two of three" belief moved here from
scaling-data. Step 3 points at scaling-data 5 for last-write-wins, step 6 at scaling-data 5 for `w + r > n`, step 5
at sql-and-relational 9 for serializable. New: vector clocks, "strong consistency", three traces made from the
old step text ([1] pause, [6] quorum, [7] partition), a [4] wrong belief, two failures ([3], [6]), a project and
ladder for this half. `unverified:` line added (usage of "strong consistency").
**consensus-and-transactions.md** (new). Built from old steps 7-11; marked reviewed after the check below.
**scaling-data.md** (stays reviewed). Step 10 keeps the price (per kind of data; refuse or answer stale in a
partition; round trips otherwise) and points to distributed-systems-core 5 and 7; words `linearizability`,
`CAP theorem` and the CAP belief moved out. Step 2 names the synonyms primary/replicas; step 11 points at
consensus-and-transactions 5; Later updated to the two new ids.
**sql-and-relational.md** (stays reviewed). Step 9 teaches ACID letter by letter (PostgreSQL glossary) and names the
race condition; words `ACID`, `race condition`; source "glossary (ACID)". Small wording cuts to stay under 2,000.
**networking-basics.md** (stays reviewed). Step 9: TLS termination; word added.
**system-design-foundations.md** (stays reviewed). Step 2: DAU; word added; three "own" cuts for size.
**caching-and-queues.md** (stays reviewed). Step 2 points at networking-basics 8; step 6 pub/sub defined, word added
(interviews gave it up); step 7 owns `visibility timeout` (taught there, untagged before); step 8 defines
idempotency, points at sql-and-relational 9 and now says the key is stored in the effect's transaction (what
api-design 7 and distributed-systems-core 2 already said it teaches); word `idempotency`; step 10 points at
system-design-foundations 4 and api-design 10, and gives up `rate limiting` to api-design 10, where windows and
buckets are taught; Later: outbox and sagas now consensus-and-transactions.
**reliability-and-observability.md** (stays reviewed). needs adds networking-basics, sql-and-relational (load
balancer and timeouts in 1 and 7; migrations in 9). Step 6 no longer reteaches retry multiplication (243x
removed; points at caching-and-queues 9); step 7 points there for one-layer retries and budgets; step 1 and 2
name system-design-foundations 1 and 7. Added: bulkhead and noisy neighbour (7), rolling and blue-green
deployment (9), `health check` (8), `expand and contract` as a word (9). Postmortem lessons moved from "In
production" into step 12 (kept, compressed); Kubernetes probe names moved to "Look up"; step 8 names `200`.
**api-design.md** (stays reviewed). Step 1 names REST; words `REST`, `rate limiting`; source and wording cuts.
**system-design-interviews.md** (stays reviewed). needs adds networking-basics and sql-and-relational (301/302 and
CDN; core entities, joins and transactions). Every borrowed idea names card and step (foundations 1, 2, 4;
scaling-data 10; caching-and-queues 6, 7; api-design 12; sql-and-relational 9). Words `pub/sub`, `visibility
timeout`, `race condition` given up to their teaching steps; step 13 owns `atomic counter`. Later: proximity.
**system-design/foundations.md** (stays reviewed). New row 7; rows renumbered; Needs first exact against every
card (6: 1,2,4,5; 7: 2,4,5,6; 8: 1-4; 9: 1-4; 10: 1-5, 9). Goals rewritten from the cards as they now are (below).
Why/Checkpoints/Short on time renumbered and cut to 899 tokens. Row 8 (old api-design) already listed 1-4 (R5).
**system-design/INDEX.md**: unchanged (the track row still holds).

#### Goals, checked with `spine`
- Design reviews: rows 1-5, 8, 9 plus distributed-systems-core 1-2, 5, 7 (CAP and linearizability now live
  there) and consensus-and-transactions 4 (distributed locks: proposed in reviews weekly) and 6 (outbox).
- Interviews: rows 3-5, 9, 10; networking 2-3, 8-10; sql 4-5, 8-9; distributed-systems-core 1, 5, 7 (CAP).
- The named learner (Express and PostgreSQL, 6 h a week): one self-contained line, about 190 beginner-hours less
  what placement finds held: networking 2-3, 8-10; sql 5, 7-10; rows 3-5 whole; dsc 1-2, 5, 7; consensus 4, 6;
  reliability 1-9 (load testing, incident roles and postmortem writing can wait); api-design 1, 3-8, 10-14 (OpenAPI
  workflow and long-running operations can wait); interviews last. Design-review readiness after rows 3-5.
- Scaling my service: reliability is row 8 now. Infrastructure: rows 1 to 8.

#### New technical claims and how each was verified
- ACID four properties, "constraints hold at commit", durability after a crash: postgresql.org/docs/current/glossary.
- Vector clocks: V(a) < V(b) iff a happened before b; incomparable iff concurrent: Cambridge dist-sys-notes §4.
- Linearizable reads ("a later-starting read returns that value or newer"): kleppmann.com 2015/05/11.
- Partition behaviour of a linearizable store: jepsen.io linearizable ("some or all nodes unable to make progress").
- Bulkhead (pool per dependency) and noisy neighbour (quota enforcement): learn.microsoft.com Azure pages.
- Blue-green (two environments, router switched, switched back; schema change first): martinfowler.com.
- Rolling update (incremental replacement, zero downtime, `rollout undo`): kubernetes.io update tutorial.
- Raft rules and numbers, 2PC logging and blocking, fencing tokens and zxid, etcd leases, outbox duplicates:
  raft.pdf, MIT 6.824 l-2pc, kleppmann.com 2016/02/08, jepsen etcd-3.4.3, microservices.io saga and outbox (reopened
  for the new card); MIT 6.824 schedule and DDIA 2nd ed. contents (O'Reilly) as its two outlines: Paxos, chain
  replication, Spanner, verification, Byzantine faults under Later; FaRM and Bitcoin left out (research).
- Certain without a page: DAU, REST's resources and methods, TLS termination with plain or re-encrypted traffic
  behind the proxy, pub/sub delivering to every subscriber, idempotent = twice has the effect of once.
- Not verified, on the line: "strong consistency" also used for weaker models (judgement).

#### Vocabulary: words added, and left out with reasons
Added: ACID, race condition, TLS termination, DAU, pub/sub, visibility timeout, idempotency, rate limiting (moved),
REST, bulkhead, noisy neighbour, health check, rolling deployment, blue-green deployment, expand and contract,
vector clock, strong consistency, linearizability and CAP theorem (moved), distributed lock, atomic counter.
Left out: MTTR/MTTD and severity levels (reliability at its limit; no source opened; incident step names
mitigation); service mesh, sidecar, serverless (platform choices, kubernetes-core's Later); gossip (dsc Later);
Bloom filters and LSM trees (scaling-data Later, storage engines); geohash/quadtree (interviews Later);
OLTP/OLAP, CDC, CQRS, event sourcing (data-intensive-systems, planned); MVCC and snapshot isolation (sql Later);
pessimistic locking (sql at its limit; `FOR UPDATE` is taught, the label is not); on-call, toil, chaos (reliability
Later); authentication/JWT (security design has no card).

#### Not resolved
- `check` fails only on curriculum/web/full-stack.md:22 ('docker' still "(planned)"): not my file.
- R4's conflict stands: web/full-stack takes api-design 1-8 with caching-and-queues `later:`, while api-design 7
  points at caching-and-queues 8 for the stored key.
- Two pointers go forward to cards not needed: caching-and-queues 10 to api-design 10 (rate limits) and
  api-design 10 to reliability-and-observability 7 (shedding). Each step teaches what it uses; the pointer only
  says where the depth lives. Making them needs would put a new ERROR in web/full-stack (not mine).
- reliability-and-observability, api-design, system-design-foundations, sql-and-relational and scaling-data sit
  at 1,999-2,000 tokens. reliability (observability vs overload and incidents) and api-design (contract vs events
  and change) are the next split candidates.

Final check line: `check failed`, from one ERROR in curriculum/web/full-stack.md:22 (docker "(planned)"); no ERROR
and no note names any of my files.

#### Second pass (coordinator's request): Goals re-cut to an hours budget
Why: a blind test showed that the learner's line (rows 3-5 whole plus parts of six cards, about 80 steps) led to a
22-chapter first book that never reached reliability, APIs or interviews before her deadline. Each line now names
only the steps its goal cannot do without, with the hours of that set (row hours x share of steps; `spine` gives
the same total). Whole rows appear only where every step is needed. Each range was read with `spine` for what
it assumes:
- Design reviews (about 125 h), with interviews in about six months (about 145 h; `spine`: 144): networking-basics 2,
  9-10; sql-and-relational 7-10 (7 because reliability 9's expand and contract builds on its migrations);
  system-design-foundations 1-8, 10; caching-and-queues 1-3, 5-10; scaling-data 1-4, 6, 10-11 (11 because
  consensus 6 starts from 2PC); distributed-systems-core 1-2; consensus-and-transactions 6; reliability 1, 3-4,
  6-9 (SLIs, golden signals, telemetry, how a service falls over, timeouts, retries and overload, health checks,
  safe change; 2 and 5 left out, since 5 needs 2's budget); api-design 1, 4-5, 7-8, 10, 13. For interviews, add
  scaling-data 7, 9 and system-design-interviews 1-8, 14 inside the same line. I merged the old first and third
  lines (they differed only by the interview steps) to stay within 900 tokens.
- Interviews (about 120 h): networking-basics 2, 8-9 (8 for interviews 10's 301/302); sql-and-relational 5, 8-10
  (10 for api-design 5's keyset); system-design-foundations 1-8; caching-and-queues whole (every step is asked:
  eviction, stampedes, queues, retries, backpressure); scaling-data 2-4, 6-7, 9-10; distributed-systems-core 1, 7
  (7 leans on scaling-data 10's definition of linearizable); api-design 1, 4-5, 7, 10, 12; interviews whole.
- Own service past its first scaling problem (about 100 h). Storage or infrastructure (about 150 h): rows 5 to 7
  whole plus named steps.
To make room, I cut the map elsewhere: shorter sources, shorter "After it you can" cells, Why, Checkpoints, Short on
time (now: the Goals' steps are the floor) and Left out. The map is 888 tokens.

system-design-foundations.md (stays reviewed; wording only): step 1 now opens with the whole practice once, small,
as the book's first chapter: one feature of the learner's own service, taken in an hour from two requirements to
one estimate, a sketch, two options and a written decision. The step numbers are unchanged, so no reference
breaks. I dropped the second "In production" line to stay within the limit: it said the same as Never omit [4].
Card at 1,995 tokens.

`check`: `check ok: 34 cards, 6 maps, 1 roles, 5 indexes` (the full-stack ERROR is gone; no note names my files).

## R7: HTML and CSS, JavaScript, TypeScript

### R7: html-and-css, javascript, typescript (stage 4/5 second-design review)

Reviewer: independent agent (did not write these cards). Repository files edited: only the three cards. Originals
kept at /tmp/r7/*.orig.md. All three marked `reviewed 2026-11-18`. Each card is now at exactly 2,000 tokens with the
status line; every addition was paid for by a cut (listed).

Machine facts that matter to all three:
- `tsc` on PATH (/home/claude/.npm-global/bin/tsc -> /opt/native-tsc) is TypeScript **7.0.2, the native (Go)
  compiler**. A second compiler, TypeScript **6.0.3** (the last JavaScript-based one), is at
  /opt/npm-tools/node_modules/.bin/tsc. I ran every TypeScript trace on both: error codes and messages were identical.
- Node is v22.23.4; it strips TypeScript types by default and refuses `enum`.
- Chromium is Playwright's headless build 153.0.8010.12 under /opt/pw-browsers (PLAYWRIGHT_BROWSERS_PATH), driven
  with /opt/npm-tools/node_modules/playwright. Nothing installed.
- `us_path.py check` fails at the moment only because of files outside my list (full-stack.md docker row,
  coding-interviews/new-graduate python-core rows, docker.md size; others are working on those). To see notes I ran
  it on a temp copy with those fixed: the one note on my files ("breakpoint" owned by both html-and-css and
  javascript) is resolved. No ERROR names my files.

#### cards/html-and-css.md, reviewed 2026-11-18
- Sources opened: MDN Learn Core modules (order; outline 1); web.dev Learn HTML and Learn CSS contents (outline 2);
  MDN Cascade (cascade steps; layers inside origin and importance; unlayered beats layered; inline `style` above
  author rules); MDN Stacking context (the 14 conditions; positioned with z-index, fixed, sticky, opacity, transform,
  isolation confirmed); MDN Ordering flex items (order and row-reverse change only painting; Tab and speech follow
  source); MDN reading-flow (changes Tab and speech order; limited availability, experimental); WCAG 2.2
  Understanding 1.4.3 (4.5:1, 3:1 for large text; 18pt/14pt bold); WebAIM Million 2026 (missing labels 51%, low
  contrast 83.9%; I replaced the card's "about half" with the figures).
- Outlines compared: MDN Core modules; web.dev Learn HTML + Learn CSS. Gaps: tables (both outlines; a first-month
  thing in any admin screen) FIXED in step 2 (`<caption>`, `<th scope>`); pseudo-classes and pseudo-elements
  FIXED in step 5; inline `style` in the cascade FIXED; layer precedence FIXED in step 12. Left: floats and legacy
  layout (legacy), web fonts, backgrounds/borders/shadows (no mechanism beyond the cascade), logical properties,
  anchor positioning, nesting, view transitions, details/summary; `<dialog>`/popover and container queries were
  already under Later.
- Run (Chromium, /tmp/r7/pw): specificity (#main p beats .note.warn and p.note; one id beats eleven classes);
  button font 13.3333px under 20px body; nested 2em = 80px; 250 vs 200 box; margins collapse to 30; two `flex: 1`
  items in 300px: the long-word one grew to 417px, 150 with `min-width: 0`; z-index 9999 child under parent's
  z-index 2 sibling; accessibility names via CDP (unlabelled input "", icon button "", image link without alt "",
  placeholder DOES give a name); div tabIndex -1, button 0; unlayered rule beats a layered #x.a.b.
- Changed: the flex trace's "376px" was a content-dependent number: replaced by the setup that was run (two `flex: 1`
  items) and "grows past 150"; "13.33px here" -> "in Chromium"; unverified line now says traces ran in Chromium only
  and form-control fonts differ by engine; "unlabelled input" -> "no label or placeholder" (placeholder supplies a
  name in Chromium); step 11 now names the commonest stacking-context makers in real bugs (a positioned box with
  z-index, `fixed`, `sticky`); wrong belief [8] gained the `reading-flow` exception (its truth was no longer
  timeless); "a script without defer" -> "a classic `<script>`" (modules defer). Cuts to pay: guided practice line,
  failure [8] (duplicated the trace), "an id beats even eleven classes" (duplicated wrong belief [5]), wording.
- Order (check 3): sound; HTML meaning and access before CSS, cascade before box model before layout. DevTools are
  used from step 1 (Elements) and 5 (Styles); step 13 consolidates with audits. Go deep (check 4) names the cascade,
  box/flex/grid sizing, and keyboard/screen-reader access: right.
- Engine differences: specificity, inheritance, box sizing, margin collapsing, flex `min-width: auto` and stacking
  are specified behaviour; form-control default fonts are UA-stylesheet values and are flagged; accessible-name
  results were seen in Chromium only.
- Still unverified: results in Firefox and WebKit; whether `reading-flow` has spread.
- Score: 8/10. Held back by: it is one card for two languages at the token limit, so forms, tables and
  accessibility get one step each; a writer gets the decision but little on images/media.

#### cards/javascript.md, reviewed 2026-11-18
- Sources opened: javascript.info contents (outline 1); MDN JavaScript Guide contents (outline 2); MDN Using promises
  (floating promises, `unhandledrejection`); MDN Microtask guide In depth (queue drained including new microtasks,
  then rendering); jakearchibald.com tasks-microtasks (the ordering puzzle). Dropped nodejs.org event-loop guide
  from sources: the card no longer teaches Node's phases (node-and-express 3 owns them).
- Outlines compared: gaps FIXED: control flow (`if`/`for`/`while`/`switch`; the card says needs: none), optional
  chaining `?.`, strings/template literals, number precision and safe integers, `BigInt`, dates and time zones,
  JSON as a topic (both outlines have "Date and time" and "JSON"), custom errors and `cause`, debugging (javascript.info
  "Debugging in the browser"), `<script type="module">` and bare specifiers (tooling boundary). Left: generators,
  Proxy, regular expressions, `Intl` beyond display, `Temporal`, typed arrays, resource management, property
  descriptors (all under Later or below the promise).
- Run (Node 22, Chromium): every trace in How it runs, output as stated: coercion line; var/let closures 3,3,3 /
  0,1,2; spread shallow; unbound method TypeError message; `[1,10,2].sort()`; `0.1 + 0.2`, `2 ** 53 + 1`;
  TZ=America/New_York `new Date("2026-03-01").getDate()` 28, `new Date(2026, 1, 30)` 2 March; JSON drops
  `undefined`, `NaN` -> null, Map -> {}; the ordering puzzle printed A B B2 C1 C3 C4 C2 E; 200 ms busy loop delays
  the timer 200 ms; sequential 301 ms, `Promise.all` 101 ms, `forEach(async)` waits for none; in Chromium a 404
  fetch resolves with ok false and `.json()` throws `Unexpected token '<', "<!DOCTYPE "... is not valid JSON`;
  `Cannot read properties of null (reading 'addEventListener')`; uncaught async throw in a page logs
  `Uncaught (in promise)`, fires `unhandledrejection`, page keeps running; `Cannot use import statement outside a
  module` and `Failed to resolve module specifier "lodash"...` confirmed.
- Changed: restructured steps 1-9 (old 2 and 3 merged into "Functions and scope"; new step 7 "Text, numbers, dates,
  JSON"; step 8 adds the tooling boundary; step 9 adds `Error` subclasses, `cause`, debugging). Steps 10, 13, 14 kept
  their numbers because full-stack.md ("javascript 13-14") and node-and-express ("on javascript 10") cite them.
  Step 13 says it teaches the HTML it uses when html-and-css is not held (needs stays none, as the map says).
  Overlap with node-and-express removed: Node's phases and `nextTick` out of step 10; the "Node exits with code 1"
  trace replaced by the browser's behaviour (Node's is node-and-express failure [5]). Go deep reordered to put
  references first. Removed "node-and-express, typescript, react" from Later (rule 1: the map owns order between
  subjects). Word "breakpoint" (also html-and-css's, other meaning) replaced by "debugger"; "AbortController"
  moved to step 12 where it is taught; [14] owns "HTTP status code". Cuts to pay: three failures that repeated
  traces ([2], [4], [12]), the `bind`/`typeof K` tail of a trace, guided practice line, wording.
- Order (check 3): now the order I would teach for production: values and control flow, functions/closures,
  references, `this`, prototypes, collections, real-world data (numbers, dates, JSON), modules, errors/debugging,
  then the async block and the DOM. Go deep (check 4): references and mutation; closures and `this`; the event
  loop with promises and `await`: right.
- Still unverified: messages in non-V8 engines.
- Score: 8/10. Held back by: fourteen steps at the token limit; the DOM and fetch would be stronger as their own
  card, but splitting would break the map's "javascript 13-14" goal line, which is not mine.

#### cards/typescript.md, reviewed 2026-11-18
- Sources opened: typescriptlang.org Handbook contents (outline 1, incl. Type Manipulation, Modules reference,
  JavaScript section); TypeScript wiki FAQ (no runtime checks; "type assertions, not type casts"; Dog[] -> Animal[]
  unsoundness; excess property checks only on direct literals); effectivetypescript.com 2nd edition contents
  (outline 2); devblogs.microsoft.com "Announcing TypeScript 6.0" (strict now true by default; module esnext;
  target latest; `types` defaults to []; rootDir; deprecated node10, baseUrl, es5, outFile removed; removed
  entirely in 7.0). TSConfig reference kept for what `strict` turns on (consistent with what both compilers did).
- Outlines compared: gaps FIXED: the limits of narrowing (narrowing kept across a call that undoes it; Effective TS
  "Understand type narrowing", "Avoid soundness traps") as a step-4 decision and a run trace; DOM types
  (`querySelector` -> `Element | null`, narrowed by `instanceof`; Effective TS "Understand the DOM hierarchy"),
  a junior's first front-end TS error; type predicates are trusted (wrong belief); migration "leaves of the import
  graph first" (Effective TS item 82); the `types` option beside `@types/`. Left: overloads, brands, testing types,
  template literal types, namespaces, source maps, compiler performance (Later or below the promise).
- Run (/tmp/r7/ts, both compilers, strict): TS2693, TS2353, TS2345, TS2322 (Promise<number>), TS18046, TS7016
  (only under noImplicitAny; with strict false it is silent: the trace now says so), TS2322 under
  noUncheckedIndexedAccess for array and Record; TS1294 for enum and parameter properties under
  erasableSyntaxOnly; TS2578 unused @ts-expect-error; `// @ts-check` + JSDoc error in a .js file; emitted JS run:
  enum object printed, `dogs[0].bark is not a function`, `typeof u.id` "string"; narrowing-across-call program
  compiles and throws `Cannot read properties of null`; `node run.ts` executes a type error and refuses `enum` with
  `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`; with no `strict` key both compilers behave as strict (the 6.0 default).
- Version-bound facts: the card did not state the old default of `strict`, but its migration step and Never omit
  assumed nothing; now Never omit tells the planner to look up the release's defaults (`strict`, `types`,
  `module` changed). No error code in the card differs between 6.0.3 and 7.0.2. Node's type stripping is noted as
  checked on one Node line (it is on by default only in recent lines).
- Changed: step 1 now teaches that bundlers and `node` strip types unchecked (In production says why CI runs
  `tsc --noEmit`); steps 4, 5, 12, 13 as above; wrong belief [3] "assigned directly" -> "written in place" (it also
  applies to arguments and returns); [11] belief adds narrowing across calls; How it runs sorted by step. Cuts:
  failures [1], [11], [12] (each repeated a trace), long messages where the code suffices, wording.
- Overlap with javascript: none taught twice (JSON, async and `catch` appear in TypeScript only as types).
- Order and depth: right; Go deep names narrowing, the boundary and what the checker proves.
- Still unverified: TypeScript releases before 6.0 (codes are old and stable, but not run here).
- Score: 8.5/10. Held back by: the token limit leaves the DOM and React typing to one clause; a front-end learner
  will need `React` prop typing from the react card, which does not teach it.

#### Conflicts outside my list (not touched)
- node-and-express wrong beliefs [3] "`async` code runs on other threads" and [4] "Marking a function `async` stops it
  blocking" repeat javascript [12] "`async` runs code in parallel". The mechanism is taught at javascript 12;
  node-and-express should keep only the worker-pool part (its truth "only waiting and pool tasks overlap").
- full-stack.md: "Goals" line 3 "javascript 13-14" still right after my renumbering (13 DOM, 14 fetch).
  node-and-express "on javascript 10" still right (event loop). The map's Goal "My first front-end job" reaches no
  card that teaches npm/`package.json` (node-and-express 2 owns it; react 14 only names build tools): javascript 8
  now names the bundler boundary, but someone should decide where npm lives for front-end-only learners.
- full-stack.md and others currently fail check (docker and python-core rows still "(planned)", docker.md over
  size): owners of those files.
- react.md teaches no TypeScript for components while the map says "TypeScript before React so a typed team's
  components can be read".


## R8: React, Node and Express, the web track

### R8: react, node-and-express, web/full-stack, web/INDEX (reviewed 2026-11-18)

#### cards/react.md, reviewed 2026-11-18 (score 8/10; 1,989 tokens)
- Sources opened: react.dev/learn/render-and-commit (the two triggers; the component's children render too; commit
  changes only the DOM nodes that differ; Strict Mode calls components twice); learn/queueing-a-series-of-state-updates
  (batching inside handlers, no batching across separate clicks, three `setNumber(number + 1)` add one, updater);
  learn/synchronizing-with-effects (effects run after commit; cleanup runs before the next run and at unmount; mount,
  unmount, mount in development only; an `ignore` flag); reference/useEffect caveats (one extra setup and cleanup in
  Strict Mode; usually after paint, possibly before paint when a click caused it; `Object.is`; client only;
  `useEffectEvent`); reference/StrictMode (opt-in, four development-only checks, not on by default); reference/useState
  troubleshooting (the "Too many re-renders..." message and its cause; a mutated object is ignored by `Object.is`);
  react-dom input (the uncontrolled-to-controlled error, `value` starting `undefined`); learn/you-might-not-need-an-effect
  (reset with `key`, races, framework fetching); reference/Component (error boundaries: by default a render error
  removes the UI; boundaries catch neither handler nor async errors; class only, or `react-error-boundary`);
  creating-a-react-app (the frameworks and build tools change, so the card now points to the list instead of naming
  them); testing-library.com queries/about (getBy, queryBy, findBy; `getByRole` first).
- Outlines compared: (1) react.dev Learn contents and Reference; (2) fullstackopen.com parts 1, 2, 5, 6, 7. Gaps:
  error boundaries (in both, missing): FIXED (step 10, a failure, the word). Client routing (FSO part 5): it was
  only a word in step 14; now "routes in the URL" is named there, and the framework is looked up. Global state
  libraries (FSO 6): already under Later. `useTransition`, Suspense and portals (react.dev reference): ADDED to Later.
  `useLayoutEffect`: left out (it is a single caveat; the writer gets "usually after paint" on step 9).
- Run: nothing, because React is not installed and nothing may be installed. Every behaviour was taken from the
  react.dev pages above.
- Changed:
  - "What it owns": the effect order was tagged [3-5], so the writers of steps 3 to 5 would have been handed effect
    order before effects are taught. It is now split: [3-5] covers the handler, the render, the commit and the paint;
    [9] says that, for each changed effect, the old cleanup runs and then the new setup, usually after paint and
    possibly before it after a click. The old "often after paint" is gone.
  - Step 5: Strict Mode is now described as opt-in (`<StrictMode>`). The card read as if it were always on, but
    react.dev says you opt in.
  - Removed the duplicate Strict Mode item from "What it owns" (step 5 and the [9] wrong belief carry it).
  - Look up: the major-version items are now named (batching outside handlers, Strict Mode's checks), as rule 2
    requires.
  - Step 10: error boundaries added, with a failure ("a blank page after one bad record") and the word.
  - Step 7: a double click sending two POSTs is now the reason the button is disabled while sending. This links to
    the map's idempotency step.
  - Step 14: the framework and build-tool names were removed (perishable). The step now names the URL routes and
    the `build` output, which clears check's "names nothing concrete" note.
  - Sources: rewritten to the pages actually reopened.
  - Cut to fit the limit: "never call a component as a function" and the [5] wrong belief "a re-render rebuilds
    the page" (step 5 and "What it owns" teach it).
- Still unverified: no React was run here, so the messages are quoted from react.dev; the order of steps 12-14 is
  judgement.
- Holds it back: no run, so every behaviour rests on documentation.

#### cards/node-and-express.md, reviewed 2026-11-18 (score 8/10; 1,997 tokens)
- Sources opened: expressjs.com guide/error-handling (Express catches synchronous throws; under v5 a returned
  promise that rejects calls `next(value)`; callback and timer errors must go to `next` by hand; the default handler
  sends the stack unless `NODE_ENV=production`; `res.headersSent` delegation; four arguments, registered last);
  guide/migrating-5 (rejected promises forwarded; `req.body` is `undefined` when unparsed where v4 gave `{}`; path
  syntax `/*splat`, braces for optional parts, no regexp characters; `req.query` getter with the "simple" parser;
  `urlencoded` `extended: false`; `app.listen` errors go to its callback); advanced/healthcheck-graceful-shutdown
  (on SIGTERM stop accepting, finish, release, exit; liveness against readiness). nodejs.org http API: the page was
  too long to read in full, so `server.close()` was confirmed by a run instead. fullstackopen.com parts 3 and 4.
- Outlines compared: (1) the expressjs.com guide contents (routing, middleware, error handling, debugging, behind
  proxies, database integration, security and performance best practice); (2) fullstackopen.com parts 3 and 4
  (Express, CORS, deployment, supertest, token login). Gaps:
  - CORS (FSO part 3; it is the first wall a React-plus-Express learner hits): FIXED in step 9, with a failure and
    the word.
  - Debugging with `node --inspect`: ADDED to step 1.
  - Keep-alive and proxy timeouts (behind proxies): ADDED as a [14] failure and to Look up.
  - Template engines: left out, because this is a JSON API card.
  - Password hashing: left to web-auth-and-security (planned).
- Run (Node 22, /tmp/r8):
  - Step 3's order: `sync, nextTick, promise, timeout, immediate`; inside the fs callback `io-tick, io-promise,
    io-immediate` before `io-timeout`; `t1` then `t1-micro` then `t2` (microtasks run after each timer callback).
  - A blocked loop: `/fast` took 1.997 s while `/slow` spun for 2 s, and 0.0007 s alone.
  - Eight `pbkdf2` calls finished in two waves of four (318-370 ms, then 634-713 ms).
  - An unhandled rejection printed the error and exited with code 1.
  - `write()` returned `false` once `highWaterMark` was reached, then `'drain'` fired.
  - `server.close()` with an idle keep-alive connection closed in 1 ms on Node 22. Older lines did not close idle
    connections, so this is now a look-up item.
- Changed:
  - Step 8 referred to api-design 4, a card that is not in its `needs` and comes later in the map. It now points to
    networking-basics 8, which is a need.
  - The [10] wrong belief now says that older Express majors also miss `async` rejections, without naming a version.
  - Look up: `server.close()` and idle keep-alive connections added.
  - Removed: the "Express parses no body" line (it is covered by the step 9 failure and the Look-up item on unparsed
    `req.body`), the second "In production" bullet (it repeated the failures), and "Never omit [11]" (sql-and-
    relational 10 owns bind parameters).
  - Sources: rewritten to say what was run.
- Still unverified: Express itself was not run (from its docs); the step order is judgement.
- Holds it back: Express behaviour is not traced by a run.

#### web/full-stack.md, reviewed 2026-11-18 (score 7/10; 895 tokens)
- Sources opened: every card it names (needs lines and steps); react.dev creating-a-react-app.
- Run: `us_path.py check` (the docker ERROR is fixed and no notes remain for this file); `us_path.py map` and
  `spine api-design:1-8 caching-and-queues:8` (it prints 9 steps from 2 cards).
- Changed:
  - Row 12 docker: `(planned)` removed. Needs first is now `6, linux-command-line`, matching the card's needs; the
    old `8` was not a need.
  - Full-stack goal: api-design 7 stores its key "in the effect's transaction (caching-and-queues 8)". The goal now
    TAKES caching-and-queues 8, because a double-submitted form makes idempotency central to a first full-stack job.
    Both cards' other steps and system-design-foundations go under `later:`. caching-and-queues 8 relies only on
    sql-and-relational 9, which is in rows 1-8.
  - Full-stack goal: "then 10 to 12" named two planned rows that a planner cannot spine. It now reads "then
    linux-command-line and row 12".
  - Front-end goal: "networking-basics 1-3, 8" broke the card, because step 8 writes HTTP on step 4's socket and
    compares versions by step 5's head-of-line blocking. It is now 1-5, 7-8.
  - Back-end-to-UI goal: rows 6-8 "held" were dropped, because react does not need them.
  - TypeScript goal: now says the React or Express steps are `held` on evidence.
  - Why this order: now gives the reason for the caching step and for linux-command-line.
  - Checkpoint 12: it no longer promises a login and an end-to-end test from planned rows.
  - Trimmed to fit the 900-token limit.
- Still unverified: hours, levels and step ranges (judgement, as the file says).
- Holds it back: rows 10, 11 and 13 are still planned, so the full-stack goal has no card for security or
  end-to-end testing beyond node-and-express 12-13.

#### web/INDEX.md, reviewed 2026-11-18 (score 8/10; 171 tokens)
- Changed: the roles line now names role ids marked `(planned)` (junior-front-end-developer, junior-backend-developer,
  junior-full-stack-developer). The existing new-graduate-software-engineer role holds neither react nor
  node-and-express, so it is not named.
- Holds it back: no role map exists yet.


## R9: Linux command line, Docker, dsa-core-techniques again

### R9: review record (linux-command-line, docker, dsa-core-techniques re-review), 2026-11-18

All three marked `reviewed`. All three were at or over the 2,000-token limit before review. Every addition below
was paid for by a cut elsewhere, and the status line added about 11 tokens. `us_path.py check` shows no ERROR and
no note for these files. The ERRORs it still prints belong to other teams (see Conflicts).

#### cards/linux-command-line.md, reviewed 2026-11-18 (score 8/10; 2,000 tokens)
- Sources opened:
  - missing.csail.mit.edu/2020/command-line (job control, `nohup`, `disown`, tmux, `ssh -L`, ssh config).
  - nostarch.com TLCL 3rd edition contents (36 chapters).
  - man7.org pages:
    - crontab(5): `SHELL=/bin/sh`, `%` becomes a newline, five fields.
    - manpages.debian.org crontab(5): HOME, LOGNAME and MAILTO. Neither page gives cron's PATH value, so the
      card names no value.
    - ss(8): `-l`, `-t`, `-n`, `-p`.
    - ip-address(8): `show` may be omitted.
    - ssh(1): key and config modes. A private key that is accessible by others is ignored.
    - ssh-keygen(1).
    - sshd_config(5): `StrictModes` defaults to yes.
    - journalctl(1): `-u`, `-f`, `--since`, `-p err`. The groups `systemd-journal`, `adm` and `wheel` read
      all journals.
    - systemd.service(5): ExecStart= is not run through a shell, so `|` and `>` are not interpreted.
      `Restart=` values.
    - systemd.timer(5): `OnCalendar=`; the timer activates the service of the same name.
  - The rsync manual: `-a` = `-rlptgoD`; `--dry-run`; a trailing `/` on the source copies its contents.
  - bind9 dig manual: `@server name type`, `+short`, `+trace`.
  - steam-for-linux issue 3671: it exists and is about deleted user files. The page does not name the line.
  - Checked locally: `systemctl --help` (systemd 255 binary present, not running), `journalctl --help`,
    `tar --help` and `rm --help` (`--preserve-root` refuses only `/`).
- Outlines compared:
  - TLCL. Gaps fixed:
    - "Advanced keyboard tricks": Tab completion, `history` and Ctrl-R added to step 1.
    - Package management: `apt`/`dnf` under `sudo`, in step 5.
    - Reading input: `while read -r`, in step 8.
  - Left as "later": arrays (now named), storage media (now "mounts and LVM").
  - Left out as not server work: printing, prompt customising, compiling programs.
  - Missing Semester. Gaps fixed:
    - `nohup` beside `tmux` (step 6, and the failure).
    - `ssh -L` (step 9, with the word "port forwarding").
  - Already present: `disown`-free job control, aliases, dotfiles. `mosh` and `sshfs` are left out (optional).
- First-day check (the brief's list):
  - `tail -f` was there; `-F` was added after a run showed that `-f` loses a rotated log.
  - `less`, `tar czf`/`xzf`, `chmod u+x`, `man` and `--help` were there. `history`, Tab, `nohup` and `tmux` are
    now there.
- Ordinary user against root (I ran as root, and as `nobody` with `setpriv`):
  - The card now says where `sudo` or a group is needed: system journal (`systemd-journal`), `ss -p` for other
    users' processes (as `nobody`, `ls /proc/1/fd` is refused), editing `/etc`.
  - It says "root skips read and write checks". This is not "ignores the bits": as root, `./x.sh` with mode
    000 or 644 still gives exit 126.
- Run (bash 5.2.21, /tmp/r9/lx):
  - Shell and pipes:
    - An unmatched glob stays literal.
    - `2>&1 > f` sends the error to the terminal; `> f 2>&1` sends it to the file.
    - `sort f > f` gives 0 bytes; noclobber gives "cannot overwrite existing file".
    - Exit statuses: 127 and 126.
    - `uniq -c` on `a b a` counts three runs.
    - An unquoted `$f` with a space becomes two names; `-print0 | xargs -0` keeps it as one.
  - Processes and signals:
    - `kill` gives 143 and `kill -9` gives 137.
    - The EXIT trap runs on TERM, not on KILL.
    - On a pty: a background job survives a plain `exit` but dies on SIGHUP. So the failure now says "when the
      connection drops", not "at logout".
  - Scripts and environment:
    - `set -e` holes: `local x=$(false)`, `if`, `&&`, and a pipeline without `pipefail`.
    - `${DIR:?}` and `set -u` both stop the script.
    - `export` in a child script does not reach the parent; `source` does.
  - Permissions, as `nobody`:
    - A directory with `r` and no `x`: names are listed, but `cat` is denied.
    - A directory with `x` and no `r`: `cat` works, `ls` is denied.
    - With `w`+`x` on the directory, `nobody` deleted a root-owned file of mode 444.
    - The sticky bit gives "Operation not permitted".
  - Files and disks:
    - A deleted file held open shows `(deleted)` in `/proc/PID/fd` and in `lsof +L1`; `du` no longer counts it.
    - `du -sh * | sort -h`.
- Changed:
  - Step 1: completion and history.
  - Step 3: `tail -F`.
  - Step 5: "`w` with `x`" (exact); root wording; packages.
  - Step 6: `nohup`.
  - Step 8: `while read -r`.
  - Step 9: `ssh -L`.
  - Step 10: ExecStart has no shell; journal access.
  - Step 11: `lsof +L1`.
  - Step 12: `sudo` for `ss -p`.
  - New wrong belief [4]: `uniq`. New failure [9]: `StrictModes` key refusal.
  - Failure [6]: corrected as above.
  - Word "port forwarding" [9].
  - `unverified` now includes step 13 (no cron binary here).
  - Sources rewritten to the pages really read.
  - Cut to pay for these: the processes item of "State and danger" (it was minor); duplicate phrasing.
- Still unverified: steps 9, 10, 12 and 13 come from man pages only (no ssh, ss, dig, cron or running systemd).
  Step 7's start-up file order is from memory of bash(1); it is well known, but I did not run a login shell.
- Holds it back: at 2,000 tokens, step 10 (systemd) is dense. A unit file's full anatomy (`Type=`,
  `WorkingDirectory=`, `Environment=`) is left to the writer and the look-up.

#### cards/docker.md, reviewed 2026-11-18 (score 8/10; 2,000 tokens)
- Run setup: Docker 29.9.3. I started my own `dockerd` with `--data-root`, `--exec-root`, the socket and the
  pidfile under /tmp/r9/dx (containerd image store). I pulled nothing. The images were FROM scratch, with static
  test programs (signals, unlink/read, getaddrinfo, a TCP server) and, for the shell form, Ubuntu's `dash` (and,
  separately, `bash`) with their libraries. Compose v5.7.0. I stopped the daemon when done.
- Run, with results:
  - Stopping and shells:
    - Shell form `CMD /sig` under dash: `/bin/sh -c /sig` is PID 1 and `/sig` is its child. `docker stop -t 3`
      took 3.1 s and gave 137. A two-command shell form gave the same.
    - Exec form with no handler: the program is PID 1, ignores TERM, and also gives 137.
    - Exec form with a handler: 0.1 s, exit 0.
    - `--init`: `docker-init` is PID 1; 0.1 s, exit 143.
    - **With `bash` as `/bin/sh`, a one-command shell-form CMD `exec`s: the program is PID 1.** The Dockerfile
      reference's "does not pass signals" therefore holds for dash (Debian and Ubuntu images), not for every
      shell. The card now says "`/bin/sh -c`, Debian's `dash`, stays PID 1".
  - Exit codes and kills:
    - Missing command: 127. A directory as the command: 126. Unknown flag: 125.
    - `-m 8m` with a growing string: 137 and `OOMKilled=true`.
    - `docker rm -f`: the events show `kill` with signal 9.
  - Secrets and history:
    - COPY a secret, then RUN unlink: the secret is absent in the container, but `docker save` gives a layer
      tarball that contains it.
    - `docker history` shows `ARG TOKEN=<value>` and `RUN |1 TOKEN=<value>` even on a RUN that never uses it.
      `ENV` shows in `docker image inspect`.
    - `RUN --mount=type=secret` read 19 bytes during the build; nothing in history, and no file in the image.
  - Volumes and prunes:
    - `docker rm` without `-v` leaves the anonymous volume. `volume prune` removes only the anonymous one;
      `volume prune -a` removes the named ones too.
    - `system prune -a --volumes` removed every image no container used, the build cache, the unused user
      network and the anonymous volume. Named volumes survived.
    - Compose `down` keeps the named and anonymous volumes. `down -v` removes the declared named volume and the
      attached anonymous one; a volume outside the file survives.
  - Networks and ports:
    - A user-defined network resolves `db1` (embedded DNS 127.0.0.11). The default bridge gives "Name or
      service not known".
    - `depends_on: condition: service_healthy` waited for "Healthy".
    - `-p 18080:80` answered on 127.0.0.1 and on the host address. `-p 127.0.0.1:18081:80` refused the host
      address (curl 7).
    - An app bound to the container's 127.0.0.1 gives "Connection reset by peer" (curl 56). The failure now
      quotes this message.
  - Images and cache:
    - `latest` stayed on the older build after `app:v2`.
    - `docker diff` shows `D /sig`.
    - Changing one COPY rebuilt that layer and the ones after it; the earlier layers were CACHED.
- Sources opened:
  - Dockerfile reference:
    - The shell form "does not pass signals".
    - EXPOSE "doesn't actually publish".
    - WORKDIR is created if it is missing.
    - Build args are visible in `docker history`, and are not recommended for secrets. ENV persists.
    - CMD gives the default arguments to ENTRYPOINT. USER.
  - CLI pages:
    - compose down: `-v` removes named and anonymous volumes.
    - system prune: `--volumes` removes anonymous volumes only.
    - run: the `--restart` values; `unless-stopped` against `always`.
  - get-started concepts list.
  - OWASP Docker Security Cheat Sheet: rule titles 0 to 13 and 5a.
  - All other listed docs pages are as before, used for what the card says.
- Outlines compared:
  - Docker get-started concepts (basics, building images, running containers). All covered.
    - "Overriding container defaults" now has a home: step 1, "words after the image replace `CMD`".
  - OWASP. Gaps fixed:
    - Rule 3 (capabilities): `--cap-drop ALL`, step 11.
    - Rule 5a (published ports bypass UFW): step 7.
    - Rule 7 (restarts and limits): `--restart unless-stopped`, Compose `restart:`.
  - Left: rule 4 no-new-privileges, rule 6 seccomp/AppArmor (seccomp is already "later"), rule 11 rootless
    ("later"), rule 12 Docker secrets (Swarm).
- Changed:
  - Step 3: the dash qualification.
  - Step 7: the UFW bypass.
  - Step 8: ENV against ARG made exact. The old text said both "stay in the image"; ARG values are not in the
    container's environment, only in history.
  - Step 11: restart policy and `--cap-drop ALL`; "one concern per container" cut for room.
  - "State and danger":
    - The `docker` group is root on the host.
    - System prune also removes unused networks.
  - "kubernetes-core" (no such card) became "Kubernetes".
  - Look-ups: Compose and BuildKit versions, log rotation.
  - The word "health check" [9] became "health status": the concept is owned by reliability-and-observability
    [8], and the check's note is now gone.
  - `unverified` is now push and UFW only.
- Still unverified: `docker push`/`login` (no registry); the UFW bypass (from OWASP only; no UFW here).
- Holds it back: a card at the limit. Image logging, `docker compose watch` and per-language base-image choice
  are look-ups or left to the writer.

#### cards/dsa-core-techniques.md, re-reviewed 2026-11-18 (score 8/10; 1,999 tokens)
- Read R1's block and INTEGRATION-CS.md section 6. I re-read the card in full.
- Sources opened:
  - cses.fi/problemset:
    - The 19 category headings.
    - The Construction Problems list: Inverse Inversions, Monotone Subsequences, Third Permutation, Permutation
      Prime Sums, Chess Tournament, Distinct Sums Grid, Filling Trominos, Grid Path Construction.
    - The Bitwise Operations list.
    - All 20 named tasks exist, in the categories the card implies.
  - usaco.guide/bronze/rect-geo: "Rectangle Geometry"; width = smaller right x − larger left x.
  - codeforces.com/problemset/problem/1915/F: t ≤ 10^4, n ≤ 2·10^5, "The sum of n over all test cases does not
    exceed 2·10^5".
- Run (g++ 13.3, Python 3.13.18, /tmp/r9/dsa):
  - **`x ^ y ^ y == x` is wrong as C++.** `==` binds tighter than `^`, so it printed 6 for x=5, y=3, and g++
    `-Wall` warns. Python prints True. The card's text read like a C++ identity.
    - Fixed: step 9 now says "`(x ^ y) ^ y` is `x`".
    - New failure [1]: "`m & 1 == 0` is `m & (1 == 0)` in C++, always 0". Run: C++ counted 0 evens out of 8;
      Python counted 4.
  - `m >> i & 1`: correct in both (shifts bind tighter than `&`).
  - Clearing 2·10^5 entries 10^4 times: 0.74 s (static arrays) and 0.67 s (fresh vectors) in C++. Python
    `[0]*n` per test: 1.6 s. The failure now gives both.
  - Rectangle overlap: 5,000 random pairs against a cell count, 0 mismatches.
- New material judged:
  - The bitwise operators, the sum-of-n budget, prefix xor and rectangle overlap are correct and sit on the right
    steps.
  - The three words have one home each with no check note:
    - "brute force" [1] is the name of step 1.
    - "amortised" [7] is defined in the step.
    - "sweep line" [10] is named in the step.
  - Step 12 named the whole Construction category, whose later tasks (Distinct Sums Grid, Grid Path Construction)
    are hard. It now names a starting point, Inverse Inversions.
  - Step 1 now holds complexity, the sum-of-n budget, bitmask complete search and operators, which is close to
    four sections. Splitting it would renumber every step, and other cards and both maps cite step numbers, so
    I left it and note it here.
- Changed: step 9; step 12; two [1] failures (one new, one with the Python time added). Cut for room: sources and
  phrasing. R1's "3.2 s against 0.03 s" crafted-key figure is now only "crafted keys" in sources; the run is in
  R1.
- python-core now exists as a card, so R1's "holds it back" is resolved on the card's side.
- Still unverified: bands, counts and times (judgement).
- Holds it back: step 1 is overloaded (see above); at the limit, with no room to add sliding-window minimum or
  monotonic stack (they are "later", in advanced-data-structures).

#### Conflicts with files outside my list
- web/full-stack.md row 12 still says `docker (planned)` (check ERROR). Its "Needs first: 8" disagrees with the
  card's `needs: linux-command-line, networking-basics`. linux-command-line is not on any track map.
- core-cs/coding-interviews.md:12 and roles/new-graduate-software-engineer.md:12 still say `python-core
  (planned)` (check ERROR).
- reliability-and-observability [8] and docker shared "health check". I resolved this on my side.
- The python-core word notes (hash table, iterator, heap against cpp-for-contests) are not mine.


## R10: Kubernetes, GitHub Actions, the DevOps track

### R10: review record (kubernetes-core, github-actions-ci-cd, devops/containers-and-delivery, devops/INDEX), 2026-11-19

I marked all four files `reviewed`. `us_path.py check` ends "check ok" and gives no note for these files.
Nothing was run. There is no cluster or GitHub runner here, and the proxy blocks curl to kubernetes.io and
raw.githubusercontent.com. So every behavioural claim below was checked against the documentation, read through
WebFetch (for kubernetes.io the body sits past offset 90,000-100,000 of each page). Originals are kept in
/tmp/r10orig for diffing.

#### cards/kubernetes-core.md, reviewed 2026-11-19 (score 8/10; 1,993 tokens)
- Sources opened (kubernetes.io unless stated):
  - pod-lifecycle:
    - A failing liveness probe makes the kubelet restart the container.
    - A failing readiness probe makes the EndpointSlice controller remove the Pod's IP from the EndpointSlices.
      Readiness runs "during its whole lifecycle".
    - A startup probe disables the other two until it succeeds. If it fails, the container is killed and the
      restart policy applies.
    - A Pod is "never rescheduled to a different node".
  - pod-termination:
    - The order is preStop, then SIGTERM, then SIGKILL when the grace period ends.
    - EndpointSlice removal runs "at the same time as the kubelet is starting graceful shutdown". Terminating
      endpoints show ready=false.
  - manage-resources-containers:
    - The scheduler compares the sum of requests with capacity, "although actual memory or CPU resource usage on
      nodes is very low".
    - CPU limits are enforced by throttling.
    - Memory limits: "the kernel may terminate it ... only when the kernel detects memory pressure".
    - A container over its memory request on a node short of memory is "likely" to be evicted.
    - A limit with no request: the limit is copied as the request.
  - secret:
    - Secrets are unencrypted in etcd by default.
    - Anyone who may create a Pod in the namespace can read its Secrets, including indirectly through a
      Deployment.
    - base64 "does NOT provide any useful level of confidentiality".
    - A `subPath` mount gets no updates.
  - configmap: values used as env are "not updated automatically and require a pod restart". Mounted values
    update eventually; `subPath` mounts do not.
  - ingress:
    - "The Ingress API has been frozen."
    - "The Kubernetes project recommends using Gateway instead of Ingress."
    - "Only creating an Ingress resource has no effect."
    - TLS from a `kubernetes.io/tls` Secret ends at the Ingress.
  - deployment:
    - The selector is immutable.
    - "Kubernetes takes no action on a stalled Deployment other than to report ... ProgressDeadlineExceeded."
    - A rollout happens "if and only if" `.spec.template` changes.
  - persistent-volumes:
    - Dynamic volumes "inherit the reclaim policy of their StorageClass, which defaults to `Delete`".
    - `Recycle` is deprecated.
    - RWO means one node and may serve several pods; RWOP means one pod.
    - A claim still in use is not removed until no pod uses it.
  - debug-running-pod: `kubectl debug -it POD --image=busybox:1.28 --target=...` (`--target` joins the target's
    process namespace); `logs --previous`.
  - Blog post 2026-01-29 (Steering and Security Response Committees): ingress-nginx was retired in March 2026,
    with no further releases or security fixes. They advise moving to Gateway API or another controller.
  - Not reopened as pages, but correct on long knowledge, and the original writer cites them: debug-service,
    force-delete-stateful-set-pod, RBAC (additive, no deny) and `kubectl auth can-i`.
- Outlines compared:
  - The CKAD domains (training.linuxfoundation.org):
    - Already covered: probes, Deployments, ConfigMaps, Secrets, ServiceAccounts, requests and limits,
      Services, Ingress, volumes, logs and debugging.
    - Added to "later": Jobs, CronJobs, init and sidecar containers, quotas.
    - Already in "later": Helm, Kustomize, NetworkPolicy, securityContext, CRDs and operators, autoscaling.
    - Left out because they are cluster or exam matter: admission control and API deprecations. Blue/green and
      canary are in reliability-and-observability step 9.
  - The CKA domains:
    - The Gateway API for ingress traffic is now in step 6.
    - kubeadm, control-plane HA and the CNI/CSI/CRI interfaces belong to kubernetes-internals (planned, row 10).
    - DaemonSets were dropped from "later" for space. They are a cluster-operator object.
- Changed:
  - Step 9 now teaches graceful shutdown. Pod deletion races the EndpointSlice update, so the app must keep
    serving briefly (a `preStop` delay), drain, and exit within the grace period. The project's finish line ("a
    pod killed mid-traffic unnoticed") could not be met without this. Added the failure "errors at every
    rollout" and the word "grace period".
  - Step 8 was overstated. "Past the memory limit the kernel kills" became "may kill", and eviction for use over
    the memory request was added. The scheduler sums requests, "never real use". This is the scheduler wrong
    belief the writer had cut; it now lives in the step.
  - Step 6: Gateway API is now named as the project's recommendation. The look-up list now asks whether the edge
    controller is still maintained, because ingress-nginx is retired.
  - Step 7: removed "(never through `subPath`)" for space. The docs confirm it; it is minor.
  - Wrong belief [5]: "kube-proxy" became "kube-proxy, or a replacement", since some clusters run without
    kube-proxy.
  - Wrong belief [8]: the memory kill is now "may".
  - Wrong belief [6] (Ingress) was not restored. Step 6 states its truth ("inert without an ingress
    controller").
  - The startup-probe failure was folded into the `CrashLoopBackOff` failure.
  - The ConfigMap-in-env failure was removed. Step 7 states it.
  - The dead-node advice in State and danger was removed. Most teams' RBAC on a managed cluster does not let
    them delete Nodes.
  - Sources now list the pages that were really used.
- On size: the writer cut wrong beliefs about Ingress and the scheduler. Both truths stay in steps 6 and 8, so
  the cut cost little. The card holds its subject at 13 steps.
- What it cannot hold is the next layer, which a team that runs its own services meets in its first months:
  - Jobs and CronJobs (migrations), init and sidecar containers;
  - HorizontalPodAutoscaler, ResourceQuota and LimitRange;
  - securityContext and Pod Security Standards, NetworkPolicy;
  - Helm or Kustomize packaging.
  I would not squeeze these in. They should become a second card, for example `kubernetes-workloads-and-policy`
  (needs: kubernetes-core), and a row between 6 and 7 of the map once it exists. Nothing needs to move out of
  kubernetes-core.
- Still unverified:
  - The `preStop` delay and "liveness must not check the database" are common practice, not quoted rules. They
    are on the `unverified:` line.
  - Nothing was run.
- Holds it back: no step was run on a real cluster, and the card is at its limit. Each further fix costs a cut.

#### cards/github-actions-ci-cd.md, reviewed 2026-11-19 (score 8/10; 1,997 tokens)
- Sources opened (docs.github.com unless stated):
  - secure-use:
    - Today it recommends a lockfile that "records the exact commit for every action ... including transitive
      dependencies". It calls it "the strongest protection available", and says it "supersedes SHA pinning for
      repositories that adopt it". Full-SHA pinning is the fallback.
    - CODEOWNERS on `.github/workflows`.
    - Read-only token by default.
    - No JSON blobs as secrets; `::add-mask::`.
    - Untrusted input passed through `env:`.
  - workflow-dependency-lockfiles: `.github/workflows/actions.lock`, made by the `gh actions-lock` extension.
    It covers transitive actions but not the dependencies of reusable workflows. It is marked public preview and
    "subject to change". The changelog of 2026-10-14 says public preview on the Free, Team and Enterprise Cloud
    plans. A headline dated 2026-10-28 says GA, which I could not open. The card therefore says "where offered"
    and makes availability a look-up. **The writer's correction stands.**
  - dependency-caching:
    - A run restores from its own branch or the default branch. A pull request, forks included, can also restore
      from its base branch. A pull request's caches are scoped to `refs/pull/.../merge`.
    - Caches are "not signed or verified". Anyone who can open a pull request can read them.
    - Only `push`, `workflow_dispatch`, `repository_dispatch`, `schedule` and a few others may write the default
      branch's scope. `pull_request_target`, `issue_comment` and `workflow_run` get read-only access unless a
      workflow raises the `cache-mode` key.
  - github_token concept:
    - Events made with the token start no runs, except `workflow_dispatch` and `repository_dispatch`.
    - Pull requests the token opens wait for approval.
    - The token expires at the end of the job.
  - workflow-syntax:
    - "all of those that are not specified are set to none".
    - The defaults come from the enterprise, organization or repository setting.
    - Forks get a read-only token.
    - Concurrency: a pending job in the group is cancelled and replaced by the new one.
  - events-that-trigger-workflows:
    - `pull_request` runs on the merge commit, and not at all while the pull request has a conflict.
    - `pull_request_target` runs "in the context of the default branch of the base repository". Its warning
      names cache poisoning and write privileges.
    - Secrets are not passed to fork runs.
    - First-time contributors may need approval.
  - oidc: the `sub` formats. The environment form takes precedence. `iss` is token.actions.githubusercontent.com,
    and `id-token: write` is required.
  - troubleshooting-required-status-checks: a workflow skipped by path or branch filters leaves its check
    "Pending" and blocks merging. A job skipped by `if:` reports success.
  - deployments-and-environments:
    - Environment secrets are withheld until a reviewer approves.
    - Plan limits apply: required reviewers on private repositories need a paid plan or Enterprise.
  - github.blog changelog 2023-02-02: new enterprises, organizations and personal repositories get a read-only
    token. Existing ones were not changed. **So the default token permission is a look-up.**
  - securitylab preventing-pwn-requests: `pull_request_target` plus a checkout of the pull request's head; the
    `pull_request` then `workflow_run` split.
  - osv.dev GHSA-mrrh-fwg8-r2c3: tj-actions/changed-files, tags retargeted on 14-15 March 2025, secrets printed
    to logs, CVE-2025-30066.
  - dora.dev/guides/dora-metrics: **five** measures. Change lead time, deployment frequency and failed
    deployment recovery time measure throughput; change fail rate and deployment rework rate measure
    instability. The page says "speed and stability are not tradeoffs", the measures are per application or
    service, and they are not targets. **The writer's correction stands.**
  - martinfowler.com continuousIntegration: practices list.
- Outlines compared:
  - Fowler's CI practices:
    - Mainline, self-testing build, daily commits, fix broken builds at once, keep the build fast, automate
      deployment: all present.
    - "Test in a clone of production" is left to the docker and kubernetes cards.
  - The docs.github.com Actions how-to contents:
    - Gaps fixed: `if:` conditions and passing values between jobs (`$GITHUB_OUTPUT`, job `outputs`) were
      missing. Step 10's "pushed only from `main`" cannot be written without them. Both added to steps 2 and 5.
    - Rulesets beside branch protection added to step 7.
    - Already "later": artifact attestations, self-hosted runners, merge queues.
    - Left out: publishing actions and the Marketplace (not this learner's job), status badges.
- Changed:
  - Step 9 now teaches the workflow lockfile first and the full SHA as the fallback. Wrong belief [9] now says a
    SHA fixes only that action, not the actions it calls, which is why the lockfile exists. "Never omit" now
    says "locked or pinned".
  - State and danger [5,9] was rewritten to today's rules: who may write the default branch's cache, and
    `cache-mode`. The old text implied any untrusted trigger could write it.
  - Step 5 now says what a pull request (forks too) may read and write, and that caches are readable by anyone
    who can open a pull request.
  - "Package lockfile" in step 5, so it is not confused with the workflow lockfile.
  - CODEOWNERS (the detail the writer cut) is restored where it matters: it protects nothing unless code-owner
    review is required.
  - The required-check pending case is reworded as "path-skipped workflow". The docs pend a skipped workflow; a
    job skipped by `if:` passes.
  - Concurrency: "a newer one replaces any waiting" deploy.
  - The look-up list now includes the token's default permissions and workflow lockfiles.
  - Cut for space:
    - wrong belief "masking makes leaks impossible" (State and danger [8,11] keeps the fact);
    - the failures "fork secret empty" (step 8 states it) and "cache never hits";
    - `docker/metadata-action`, `paths-ignore`, `act`;
    - the duplicate "In production" line;
    - the adnanthekhan source (the docs now cover poisoning).
- On size: the cut wrong belief about runner files is covered by step 4 ("nothing kept"). It mattered less than
  what stayed. The card is at 14 steps and at its token limit. If it must grow, I would split off step 1 and step
  14 (CI and delivery as practice: trunk-based work, small batches, release toggles, rollback, DORA). They would
  join a future `continuous-delivery` skill card, with reliability-and-observability 9's deployment strategies
  as its neighbour. That leaves this card as the tool.
- Still unverified:
  - Nothing was run.
  - Whether lockfiles are GA today. The card treats it as a look-up.
  - Steps 12 (never cancel a deploy) and 14 (rehearsed rollback) are judgement, as the card says.
- Holds it back: nothing run on a runner. The security rules (cache scope, lockfiles, `pull_request_target`
  context) changed within the last year, so this card needs recheck soonest.

#### devops/containers-and-delivery.md, reviewed 2026-11-19 (score 7/10; 897 tokens)
- Sources opened:
  - CKAD and CKA domains (rows 6 and 10; CKA confirms kubeadm, HA and the plugin interfaces as internals).
  - The Terraform Associate (004) objectives (row 9 topics: providers, workflow, state, modules).
  - Every card named in Goals, step by step: linux-command-line, git, networking-basics, docker,
    reliability-and-observability, system-design-foundations, sql-and-relational, caching-and-queues.
  - system-design/foundations.md for the goal-line form.
- Agreement: every row's "Needs first" equals its card's `needs:`. That includes row 7's three ids outside the
  track, kept because the card needs them.
- Changed. Goals rewritten: each now names the steps it cannot do without, plus hours as "(about N h)". Hours are
  row hours × share of steps, rounded.
  - Ship my service in a container with a pipeline (about 90 h):
    - linux 1-8, 12. Docker's signals, env, users and ports use them; ssh, systemd and cron are not needed.
    - git 1-7, 9-10. Pull requests and branch rules feed github-actions 7; tags and trunk-based work feed 14.
    - networking-basics 1, 3-4, 8-9.
    - all of docker.
    - github-actions 1-5, 7-14 (the matrix is not needed).
  - Deploy and debug on my team's cluster (about 125 h; 75 h when linux, git and docker are held):
    - kubernetes-core 1-10, 12-13. Storage is left for a stateless service.
    - github-actions 1-5, 7-11, 13.
    - networking-basics 1, 3-4, 7-10 (TLS for step 6, proxies, failures).
  - Run services on a cluster and keep them up (about 165 h). The real fix for the unread needs:
    - reliability 1-5, 8-9, 11-12. Step 12, postmortems, was missing before. Steps 6-7 (overload) and 10 (load
      testing) are what pull in caching-and-queues 9 and system-design-foundations 4, so they wait.
    - system-design-foundations 1, 3, 7, used by reliability 1-3 (the SLI, percentiles from histograms, the
      43.2-minute nines).
    - sql-and-relational 7, the migrations used by reliability 9's expand and contract.
    - caching-and-queues `later:` in full.
  - Developer to platform engineer (about 205 h): rows 1-7 in full; system-design-foundations 1, 3-4, 7;
    caching-and-queues 6, 9; sql-and-relational 7; rows 8-10 when written.
- Also changed:
  - "Why this order" now says why reliability's outside needs are taken only in part.
  - "Short on time" now says the goals' steps are the floor. Its old "never skip" list repeated the goal lines.
  - "Left out" no longer claims service mesh is a kubernetes-core "later" item. It was not on that card's list.
  - Several cells shortened to fit 900.
- Row 1 linux-command-line stays. No other track lists it, and web/full-stack.md and ai/ai-engineering.md point
  at it and at docker by id.
- Still unverified: hours, levels and goal step choices (judgement, on the `unverified:` line). "75 h held"
  assumes placement evidence.
- Holds it back: goal 3 says "the line above" rather than repeating it, to fit the limit. A planner must read two
  lines to build one spine call.

#### devops/INDEX.md, reviewed 2026-11-19 (score 8/10; 157 tokens)
- Changed: "Roles this domain feeds" said no role map existed, but roles/backend-engineer.md exists. It lists
  github-actions-ci-cd and kubernetes-core. The line now names `backend-engineer` by id. Platform engineer and SRE
  are still without a role map.
- Planned tracks stay planned: none has a map. The reliability card sits in this track and in
  system-design/foundations.
- Holds it back: two of its three tracks are planned.

#### Conflicts outside my list
- The docker card's hours differ between maps:
  - 30 h here at 3 Build;
  - 20 h at 3 Build in web/full-stack.md row 12;
  - 20 h at 3 Build in ai/ai-engineering.md row 6.
  `spine` prints the hours from this track. Someone who owns the maps should decide whether the other tracks
  take a subset of steps, and say so in their Goals.
- reliability-and-observability step 8 teaches "liveness check" in load-balancer terms, and kubernetes-core 9
  teaches the Kubernetes probes. The words differ, so there is no clash. Both cards tell the writer to keep
  liveness shallow.

#### Could not check
- No run of anything.
- Lockfile GA status.
- The full text of debug-service and force-delete-stateful-set-pod (not reopened; claims unchanged from the
  writer's).


## R11: Python, machine-learning fundamentals

### R11: python-core, machine-learning-fundamentals (reviewed 2026-11-19)

#### cards/python-core.md, reviewed 2026-11-19
- Sources opened: docs.python.org/3/tutorial index (chapter list, used for check 10); tutorial/datastructures (lists
  as queues are slow, use `deque`; dict keys must be immutable); library/collections (deque "approximately the same
  O(1)" at either end; list `pop(0)`/`insert(0, v)` O(n); Counter/defaultdict behaviour); library/heapq (min-heap;
  `heapify` linear; `[priority, count, task]` tie-break; `_max` functions are new in 3.14, so "negate for max" stays
  the portable teaching); library/bisect (O(log n) search, O(n) insort); library/stdtypes (repeated concatenation
  of immutable sequences is quadratic, use `str.join`; `sort` returns None; stability guaranteed);
  docs.python.org/3/builtins/time-complexity.html (the old wiki page moved here: confirms every cost the card
  states: append O(1) amortised, pop(i)/insert O(n-i), `x in list` O(n), dict/set O(1) average and O(n) worst).
  The writer's blocked wiki page is now an official docs page; added to sources.
- Outlines compared: (1) the Python tutorial's contents; (2) Think Python 3e chapter list (opened). Gaps:
  recursion and the call (Think Python 5, 6) -> added frames per call and the recursion limit to step 4, recursion in
  depth left to recursion-and-dynamic-programming (one home for "base case", "call stack"); inheritance (tutorial 9.5,
  TP 17) -> named in step 12; command-line arguments, logging (tutorial 10.3, 11.5) -> `argparse`, `logging` in step 11
  (the card's own project is a command-line tool); performance measurement (10.10) -> `timeit` in Never omit;
  `input()`/`print` (tutorial 3, 7) -> step 1; regular expressions (TP 8) -> `re.search` in step 11, the rest later.
  Left: `match`, `for/else`, decimal, weak references, threads/async (later, named).
- Route check (`spine dsa-core-techniques interview-problem-solving`, coding-interviews.md, ai-engineering.md,
  llm-application-engineering): they assume reading large input fast on a judge (added `sys.stdin.readline`; timed
  10^6 ints: `input()` 0.68 s, `readline` 0.17 s), heap entries with ties (added `(priority, count, item)` and its
  real `TypeError`), `itertools`, `bisect`, `deque`, costs (kept), `os.environ` for API keys and `re.search`
  (llm-application-engineering 2, 5: added), concurrency (llm-application-engineering 12: named under later).
- Run (Python 3.13 here, /tmp/r11): every "How it runs" trace and every quoted message reproduced exactly
  (aliasing, grid, floats/ints, mutate-not-rebind, mutable default, late-binding lambdas, `UnboundLocalError`,
  tuple `+=` TypeError, generator laziness, exhausted iterator, bisect 1/4, `__eq__` sets `__hash__` to None, `in`
  falls back to `__iter__`, `KeyError`, unhashable list, `RecursionError`, the `random.py` shadowing message (3.13
  appends a hint naming the file; the card quotes the prefix), bare `except:` catching a real SIGINT. Timings:
  10^5 `pop(0)` 0.89 s vs `popleft` 0.004 s; 10^7-step loop 0.34-0.58 s (so "roughly 10^7 a second" holds);
  `s += "x"` 10^6 times: 14.9 s at module level, 0.04 s inside a function (CPython's in-place trick is not
  promised: the card says "may copy each time").
- Changed: step 4 split into "functions and calls" (frames, recursion limit) and 5 "scope and closures" (14 steps);
  step 1 gains `print`, `input()`, `str` immutable; step 6 gains the quadratic `+=` and `"".join`; step 9 gains
  heapify's cost and the tie-break; step 11 gains `argparse`, `os.environ`, `logging`, `re.search`,
  `sys.stdin.readline` (dropped `subprocess`); step 12 names inheritance. New wrong belief "a heapq list is
  sorted"; new failure: `TypeError: '<' not supported` from `heappush`. Removed (to fit, each taught elsewhere):
  the `RecursionError` failure (recursion-and-dynamic-programming [1,4] owns it), the tuple `+=` trace, the bisect
  trace, `int(-3.5)`, `round(2.5)`. Words: "base case", "call stack" not tagged here; "frame", "inheritance" added.
  Kept "hash table", "iterator", "heap" (shared with cpp-for-contests, an alternative card: allowed).
- Still unverified: order of steps 10-14 (judgement).
- Score: 8/10. Most holds it back: the 2,000-token limit; it is the right beginner card and enough for the routes,
  but each step is now dense and a writer must expand `How it runs` from one-line traces. A split (core language
  1-9; "Python for work": errors, stdlib, classes, projects, tests) would let both breathe; not needed to be usable.

#### cards/machine-learning-fundamentals.md, reviewed 2026-11-19
- Sources opened: scikit-learn user_guide contents (coverage), common_pitfalls (preprocessing and feature-selection
  leakage, fit only on train), classification_threshold (0.5 default "most certainly not ideal"; never tune the
  threshold on training data), calibration (forests: peaks near 0.2 and 0.9, 0 and 1 "very rare"; logistic
  regression usually well calibrated), permutation_importance (impurity importance "strongly biased", favours
  high-cardinality features; correlated features mislead permutation), model_persistence (never load an untrusted
  pickle/joblib file; no supported loading across versions); Google Rules of ML (titles of rules 1, 3, 26, 29
  confirmed); reproducible.cs.princeton.edu (8 leakage types, 648 papers affected); arXiv 2207.08815 (tree models
  "remain state-of-the-art on medium-sized data"). Dropped rules 8, 10, 37 from sources: not used by any line.
- Outlines compared: (1) scikit-learn user guide contents; (2) Google ML Crash Course outline (12 modules);
  (3) ISLP chapter list. Gaps: categorical data and missing values (MLCC 4-5; sklearn 8.3.4, 8.4) -> already in
  step 7, step 2 now finds missing values and duplicates in pandas; decision threshold tuning (sklearn 3.3) ->
  step 9 "chosen on validation data"; class imbalance -> `class_weight`, and the oversampling leak as a wrong belief;
  fairness (MLCC 12) and data rights -> step 1 "may this data be used", step 12 per-group metrics, a Judged-by test;
  neural networks, embeddings, LLMs (MLCC 7-9, ISLP 9) -> "In production" says when (images, text, audio), later
  names deep-learning-with-pytorch (planned); model persistence (sklearn 11) -> untrusted-file rule in step 13;
  how a tree picks a split (ISLP 8) -> step 11. Left as later: unsupervised (ISLP 12, sklearn 2), SVMs (ISLP 9),
  survival, multiple testing beyond best-of-many, multiclass detail, kNN.
- Run (numpy, pandas, scikit-learn here; seeds 11, 23, 57 my own; /tmp/r11/ml): feature selection before CV on
  pure noise 0.84-0.93 vs 0.49-0.63 inside the pipeline; groups shuffled 0.97-0.98 vs GroupKFold 0.49-0.55;
  duplicates x3 0.93-0.98 vs 0.42-0.54 deduplicated; random walk shuffled R² 1.00 vs TimeSeriesSplit -1.4 to -2.6;
  majority at 1% positives accuracy 0.989-0.991, recall 0; full tree on random labels train 1.00, test 0.46-0.53;
  best of 50 models by test score 0.57-0.65, fresh data 0.49-0.50; label-derived feature 1.00 vs 0.49-0.52;
  scaling before split changed CV accuracy by 0.000-0.002. Added: oversampling before CV on noise (5% positives),
  seeds 3, 8, 19: recall 1.00 and AP 1.00 vs honest AP 0.06-0.07. `OneHotEncoder` message reproduced exactly.
  All reproduce reliably; no version-bound number is in the card.
- Changed: step 1 adds who bears each error and data permission; step 2 adds `isna().sum()`, `duplicated()`,
  `groupby`, ids are not features (pandas is otherwise not taught: python-core leaves it later); step 9 adds the 0.5
  default replaced on validation data, `class_weight`, no copying rows before a split; step 11 adds how a split is
  chosen; step 12 per-group; step 13 trusted files only. New wrong beliefs: oversampling then CV; impurity
  `feature_importances_`. New Judged-by: data use cleared, errors compared across affected groups. Mathematics line
  rewritten honestly (mean and variance, logarithms for log loss and log-odds, probability as a share of cases,
  derivative only as slope). Removed to fit: the duplicates failure (Judged-by [3] and step 3 carry it), the
  coefficient belief (step 5 says it), the unsourced "most failures" line, "feature stores".
- Still unverified: order of steps 11-13 and depth (judgement).
- Score: 8/10. Most holds it back: no step on feature engineering (dates, ratios, log transforms, target encoding)
  beyond "fixes as features"; there was no room under the limit.

#### Conflicts outside my list
- cards/llm-application-engineering.md "Later: ... how transformers work (machine-learning-fundamentals)":
  machine-learning-fundamentals does not teach transformers or neural networks; point it at
  deep-learning-with-pytorch (planned).
- llm-application-engineering 12 (concurrent calls) needs `async` or threads, which python-core leaves for later:
  its writer should teach them there or a planner must add them.


## R12: LLM application engineering, the AI track

### R12: review record (llm-application-engineering card, ai/ai-engineering map, ai/INDEX)

Reviewer: independent agent, principal-engineer lens on LLM evaluation and safety. Date 2026-11-19.
Final `python3 scripts/us_path.py check`: "check ok: 34 cards, 6 maps, 5 roles, 5 indexes". All three files marked reviewed.

#### cards/llm-application-engineering.md, reviewed 2026-11-19 (1,998 tokens; score 7.5/10)

- Sources opened (each with what it confirmed):
  - platform.claude.com/docs glossary: temperature 0 is "not fully deterministic, and identical inputs might produce different outputs" (step 1, wrong belief 1); the context window is working memory, separate from training data (1).
  - platform.claude.com/docs handling stop reasons: end_turn, max_tokens, stop_sequence, tool_use, refusal (and others); a refusal comes back as HTTP 200 and must be checked in normal handling; a max_tokens cut can leave an incomplete tool call (2, 4, failure [2,4]).
  - platform.claude.com/docs errors: 429 rate limit, 500, 529 overloaded; the SDK itself retries 429/5xx with exponential backoff and honours `retry-after`; the page does NOT mention jitter (2; why "whether its SDK retries" is now a look-up).
  - platform.claude.com/docs prompting best practices: role in the system prompt, context and purpose, XML tags to separate material, 3-5 varied relevant examples, long documents at the top and the query at the end, chaining to inspect intermediate outputs (3). Reduce hallucinations: permission to say "I don't know", quotes, citations (3, 8).
  - platform.claude.com/docs develop tests: success criteria first, task-specific evals with edge cases, grading order code > human > LLM, judge with clear rubric, specific output, reasoning before the verdict (5-6).
  - platform.claude.com/docs prompt caching: an exact identical prefix (tools, system, messages, in order) is reused; any change before the breakpoint misses (12).
  - developers.openai.com structured outputs: JSON mode gives valid JSON, only Structured Outputs gives schema adherence; refusals are detectable; apps must still handle refusals, incomplete responses and "validate any business rules that the schema does not express" (4, wrong belief 4). Function calling: the five-step loop with a call id; clear names and descriptions, enums so invalid states cannot be written, the "intern test", "if your code already knows a value ... don't make the model supply it" (9). Embeddings: examples use cosine similarity; the page does not state "same model for queries and documents" (kept as a certain fact: vectors from different models are not comparable).
  - anthropic.com Building effective agents: workflows = predefined code paths, agents = LLMs directing their own process; the five workflow patterns; "potential for compounding errors"; stopping conditions such as a maximum number of iterations; pause for human feedback; tool docs "like a great docstring for a junior developer", poka-yoke, absolute file paths; start with the simplest solution (9-10).
  - anthropic.com Contextual Retrieval: a knowledge base under a stated size goes whole into the prompt; chunk-specific context prepended before embedding and BM25; BM25 for exact identifiers; results combined by "rank fusion techniques" (RRF is NOT named there); reranking; 1 minus recall@20 as the metric; chunk size/boundary/overlap tuned with evals (7-8).
  - elastic.co reciprocal rank fusion reference: RRF definition and 1/(k + rank) formula, combining BM25 and vector lists (8). Added because the card named RRF with no source.
  - genai.owasp.org Top 10 2025 list (LLM01, 02, 05, 06, 07, 08, 09, 10 all map to step 11 or 7); LLM01: "unclear if there are fool-proof methods of prevention", direct vs indirect, least privilege, human approval for high-risk actions, segregate external content, adversarial testing; LLM07: credentials must not be in the system prompt and authorisation "must not be delegated to the LLM" (11).
  - simonwillison.net lethal trifecta: private data, untrusted content, ability to communicate externally; exfiltration by API call, image load or a link; "95% is very much a failing grade" (11).
  - hamel.dev evals: assertion unit tests run on every code change, regex for leaked UUIDs, look at data, judge tracked against human labels (5-6). hamel.dev llm-judge: binary pass/fail with critiques, one principal domain expert, report TPR and TNR separately because raw agreement misleads; ~100 labelled examples per failure mode for a judge (6). hamel.dev evals-faq: error analysis "the most important activity", done before writing evals; open then axial coding into a failure taxonomy, counted; code-based eval when an objective rule identifies the failure, judge otherwise; generic metrics "create false confidence"; review at least 100 traces until no new failure modes; synthetic data to start or probe rare failures; guardrails are inline (redact, refuse, regenerate), evaluators are not; retrieval and generation evaluated separately with recall@k (5-8, 11).
  - applied-llms.org: judge position and length bias, CoT before verdict, ties; pin model versions; "don't assume that plugging in the same prompt will lead to similar or better results"; assertions from production samples; read a sample of logs daily; RAG beats fine-tuning for knowledge; fine-tune only when prompting cannot reach the bar (6, 12, Later).
  - eugeneyan.com llm-patterns: the "Mission Impossible 2" vs "3" semantic-cache error and keying caches on ids instead (12); position, verbosity and self-enhancement bias, "not using the same LLM to evaluate its own outputs" (6); hybrid retrieval beats either alone; guardrail types (8, 11).
  - builder.aws.com "Timeouts, retries and backoff with jitter": "Jitter adds some amount of randomness to the backoff to spread the retries around in time", because retries that back off to the same time overload again (2). This is the source the writer lacked.
  - americanbar.org on Moffatt v. Air Canada: chatbot gave bereavement-fare information contrary to the policy page (no post-travel requests); Air Canada argued the chatbot was a separate legal entity; tribunal found negligent misrepresentation, the airline responsible for all information on its site (11). Card's "invented a refund rule" reworded to "liable for its chatbot's wrong refund rule" (the write-up says it misstated the policy, not that it invented one).
- Outlines compared: (1) Chip Huyen, AI Engineering (O'Reilly), table of contents opened on oreilly.com; (2) the platform.claude.com docs navigation tree (Building with Claude, Model capabilities, Tools, Context management, Working with files, Test and evaluate, Strengthen guardrails, OpenTelemetry). Gaps and what was done:
  - Conversation state and context management (Huyen 5 "context length and efficiency"; docs "Context management", compaction, token counting): missing. FIXED in step 2 (a chat is history your code resends, trimmed or summarised before it fills the window); wrong belief "It remembers our chat" moved from [1] to [2], where it is taught.
  - Long documents (docs: long material first, query last): FIXED in step 3.
  - Multimodal input: FIXED as "image, PDF, audio input" under Later (exists; look up).
  - Latency budgets and streaming UX: step 12 had streaming and TTFT; added "a latency budget (time to first token, output length)" (applied-llms: latency is mostly output length).
  - Human review loops / user feedback (Huyen 10 "User feedback"; applied-llms HITL): FIXED: step 10 review queue whose verdicts become labels; second "In production" line (traces and feedback read weekly, each failure a case).
  - Guardrails as checks in code (Huyen 10 architecture; hamel FAQ): FIXED in step 11, "word" guardrail added.
  - Logging and privacy: the writer's single clause in step 11 kept (retention terms; redaction before sending AND logging) and step 12 traces marked access-limited because they hold users' text. Judgement: enough for this card; a data-protection card does not exist.
  - System prompt leakage (OWASP LLM07): FIXED in step 11.
  - Model selection (Huyen 4): FIXED in step 12 ("a new one tried on the set") and "In production".
  - Fine-tuning as later and when it is the wrong tool (Huyen 7): FIXED in Later: for style and format once prompting fails on the set; facts come from retrieval.
  - Dataset engineering / synthetic data (Huyen 8): step 5 now says synthetic inputs only for rare cases.
  - Inference optimisation, open-weight serving (Huyen 9): left in Later; this card is for API users.
  - MCP (docs tree): named in Later; batches and reasoning settings fall under "the provider's name for each feature used".
  - api-design as a need: JUDGED RIGHT to leave out. The promise is a feature inside a product the learner already serves; making api-design a need would pull in networking-basics, system-design-foundations and caching-and-queues before a learner may call a model. The map puts api-design 7 and 10 (idempotency, rate limits) in the goals that need them.
- Run: nothing could call a model. Ran `us_path.py check`, `steps llm-application-engineering:5-6` (what a writer of the eval chapter is handed), `words`, `find`. Token counts measured with scripts/us_lib.tokens.
- Changed (each with why):
  - Evaluation rebuilt as practitioners do it (hamel FAQ, Anthropic tests): step 5 now "Look before measuring": success criteria, real inputs (synthetic only for rare cases), outputs read until no new fault appears (100 or more), faults grouped into failure modes and counted (error analysis), labelled set, baseline. Step 6 "Checks per failure mode": code checks first, a judge only where code cannot, one failure mode per judge, PASS/FAIL, reasoning first, not the model judged (self-preference), trusted once its true positive and true negative rates on held-out human labels are known (was "precision and recall": the sources say TPR/TNR and warn against raw agreement), position and length bias, every change alone reruns the set per mode. Previously error analysis came last in step 6, after building the judge: the wrong order.
  - Step 2: jitter now sourced (AWS); `Retry-After` added; words jitter added.
  - Step 1: "nothing known ... past its cutoff" kept; nothing perishable found. Read every line for model names, prices, context sizes, vendor feature names, library defaults: none remain. "XML-style tags" stays as a mechanism (both providers document delimiters); Pydantic stays as the named validator in Python.
  - Step 9: what code already knows (the user's id) is never asked of the model (OpenAI function calling; also a security property).
  - Step 12: concurrency now names `asyncio` with a semaphore: python-core leaves `async` for later and points to this step, so this step must teach it (prerequisite hole closed).
  - Later: "how transformers work (machine-learning-fundamentals)" was wrong: that card is tabular supervised learning with no transformers; now points to the deep-learning track (planned).
  - Wrong beliefs: added [5] generic score belief (hamel FAQ). Removed [6] (repeated step 6's text) and [12] (step 12 now teaches it) to fit the limit; "OWASP: no fool-proof prevention" made exact ("no known").
  - Failures: unchanged in substance.
  - Words: "error analysis" was also owned by machine-learning-fundamentals (check note); the mechanism there is the same practice, and that card is another reviewer's, so this card uses the phrase untagged and owns "failure mode" instead. Added jitter, guardrail; "pass rate" dropped.
  - Step 5 had a check note "names nothing concrete": now carries the 100-trace number from hamel FAQ.
  - Sources line: per-source uses moved into this record to stay under 2,000 tokens.
- Still unverified: nothing was run against a model; the step order, "one retry", "one judge per failure mode" and "synthetic only for rare cases" are judgement (written on the card's unverified line in short). The SDK-retry behaviour is a look-up, not a claim.
- What most holds it back: it is at 1,998 of 2,000 tokens, so steps are compressed to clauses a writer must expand; the sources line no longer carries what each source was used for. A split is not natural (retrieval alone would be two steps), so the honest fix is a higher limit or a planned retrieval-systems card taking some of 7-8.

#### ai/ai-engineering.md, reviewed 2026-11-19 (about 899 tokens; score 7/10)

- Sources opened: the seven cards' headers and steps (python-core 14 steps, machine-learning-fundamentals 13, llm-application-engineering 12, api-design 14, sql-and-relational 11, reliability-and-observability 12, docker 12); system-design/foundations.md Goals (form); hamel.dev evals and applied-llms.org (evaluation and prompting before fine-tuning, rows 2 and 12).
- Outlines compared: Huyen's contents (evaluation, prompting, RAG and agents, fine-tuning, dataset engineering, inference optimisation, architecture and feedback) against the rows: fine-tuning, retrieval at scale, serving are planned rows; dataset engineering and inference optimisation fall under planned rows 11-12. No row missing that a developer shipping a feature needs.
- Checked: every row's "Needs first" equals its card's `needs:` (api-design and reliability: networking-basics, sql-and-relational, system-design-foundations, caching-and-queues; docker: linux-command-line, networking-basics; llm and ML: python-core). Planned rows marked.
- Changed:
  - Row order: sql-and-relational moved from row 2 to row 3 so the LLM card is row 2 and a web developer is not routed through SQL first; all row references renumbered.
  - Goals rewritten in the foundations form, each with its hours "(about N h)" (row hours × share of steps) and the exact steps that goal cannot do without, checked against the cards' real steps: ship a feature (about 50 h; 75 h if Python is new; retrieval 7-8 and tools 9-10 only if the feature needs them; a developer in another language puts python-core `later:`); cheap and dependable (about 50 h; reliability 1-7, 9, api-design 7, 10; docker removed: it does not make a feature cheaper or more dependable); first job (about 185 h); work beside data scientists (about 55 h). The old first goal pulled reliability without its steps' purpose and the old fourth goal pulled docker for no reason.
  - Honest order for the next-month web developer: no machine-learning-fundamentals and no SQL before shipping; "Why this order" says so with the reason.
  - "Left out on purpose" now says what the track is not: not research/training large models, not a vendor course, not front-end.
  - Checkpoints merged to one line to fit the limit.
- Still unverified: hours, levels, which steps each goal keeps, and the planned rows' contents are judgement (on the file's unverified line).
- What most holds it back: Goals cite machine-learning-fundamentals step numbers (1-4, 6-10, 12-13) while another reviewer is editing that card; if its steps are renumbered, goals 3 and 4 must be rechecked. Also python-core `later:` for a non-Python developer is allowed by the planner rules but the card's step 2 and ladder still say Python.

#### ai/INDEX.md, reviewed 2026-11-19 (198 tokens; score 8/10)

- Checked: tracks match the map title and planned tracks; under 250 tokens.
- Changed: ai-engineering "Start here if" now says no machine learning is needed first; roles line now names the two role maps that use llm-application-engineering (backend-engineer specialist, full-stack-developer desirable), checked in roles/.
- What most holds it back: no AI engineer role map exists yet.

#### Conflicts outside my list
- machine-learning-fundamentals.md also owns the word "error analysis" (step 12). Resolved on my side (untagged here). If its steps renumber, ai-engineering Goals 3-4 need rechecking.
- python-core.md "Later: `async`, threads (llm-application-engineering 12)": still valid; step 12 now names `asyncio` with a semaphore.


## R13: Four role maps

### R13: role maps backend-engineer, full-stack-developer, devops-engineer, ai-engineer (reviewed 2026-11-19)

Reviewer: independent agent (director-of-engineering lens). Files edited: only the four role maps. Backups of
the writers' versions: /tmp/r13-{backend,fs,devops,ai}.orig. All four now pass `check`, are 797-799 tokens and
are marked `reviewed 2026-11-19`. Caveat for every block: job boards repost adverts under new ids, so a page
re-opened under the same company and title is not always the exact posting the writer counted (noted per file).

#### roles/backend-engineer.md, reviewed 2026-11-19
- Sources opened: dropbox.github.io/dbx-career-framework/ic2_software_engineer.html (code review, "well tested",
  debugging others' code, decompose a simple problem: supports git-by-ladder, testing, design at Build);
  handbook.gitlab.com backend family (well-tested, security, performance, Tier 2/3 on-call; no SQL or Git named).
  Adverts: Stripe Backend Engineer Core Technology (stripe.com 7182617: 2-12+ years, algorithms and data
  structures, distributed systems, any language, "interview process is language agnostic"); BitGo Backend E2
  Ecosystem (greenhouse 8644530002: TypeScript/Node/Express, PostgreSQL, REST, unit/functional tests, Git and
  code review, algorithms and complexity); Affirm SWE II Backend, Capital Orchestration (greenhouse 7749755003:
  tested code, code review, design, on-call, "Proficiency with agentic coding", Python/SQL a plus); PlayStation
  SWE II Backend (careers.playstation.com 6145793004: Node/TS, PostgreSQL with indexing and transactions,
  GraphQL/REST, caching and queues, CI/CD, IaC, AWS); Robinhood Software Engineer 1, Backend (greenhouse 7263578:
  Python/Django or Go, transaction-safe relational design; a 0.5-2-year posting, possibly not the writer's).
  DoorDash: page would not load.
- Counts: on the five re-opened, databases 4/5, tests 4/5, design 3-4/5, algorithms 2-3/5, API 2/5, git/review
  2/5, Python named only 2/5 (Node/TS 2, Go 1, any 1). The cells agree in direction with the writer's 8-sample.
  The python-core line is "a server language (8 of 8; Python 3)": honest, but it is a choice of one language,
  not evidence for Python; the Overlap now says Node (2) maps to node-and-express (it said "Node: no card",
  which was wrong: the card exists).
- Classes against count: git essential on 4 of 8 (reason in file: ladders; Dropbox IC2 and Affirm confirm
  review); networking-basics desirable on 1 of 8 (reason: prerequisite of system-design-foundations, api-design).
  Both stand. dsa-core-techniques desirable (3 of 8) left, but its interview check now names
  interview-problem-solving too (Stripe's language-agnostic coding round).
- Run: `role backend-engineer --have "git:3"` -> 16 subjects, about 475 h; `ready` lists 17 lines.
  Hours: the file said essential 180 h, desirable 310 h; `role` computes 190 / 300 (python-core 40 h from
  ai/ai-engineering, docker 20 h). Fixed to 190 / 300.
- Changed: hours; python cell wording; interview check adds interview-problem-solving; capstone set in "the
  learner's own Python service"; Overlap fixed (Node -> node-and-express); "five reopened 11-19" in sources;
  interview checks added to `unverified:` (they are read from adverts' requirements, not interview guides);
  dropped the redundant "scaling-data before distributed-systems-core" (the card's needs enforce it) for room.
- Left: Affirm's required "agentic coding" (1 of 8) is not a line (record only; ai-assisted-development is
  desirable in new-graduate and full-stack). Two adverts first published in 2024 (writer's note): the classes
  they touch (cloud, Kafka) are desirable either way, so no class rests on them alone.
- Still unverified: DoorDash, LaunchDarkly, Wealthfront not reopened; levels; interview checks.
- Score 7/10. Most holds it back: python-core stands in for "a server language"; a Go or Java learner gets an
  essential line in a language their target job may not use, and the format has no "one of" for role lines.

#### roles/full-stack-developer.md, reviewed 2026-11-19
- Sources opened: handbook.gitlab.com fullstack family ("JavaScript and associated web technologies (CSS,
  semantic HTML)", well-tested, code review, security, on-call; company-wide "expected to incorporate AI into
  their daily workflows"); Dropbox IC2 (above). Adverts: Momence Full-stack (React/Node) (greenhouse 4147556005:
  TS, Node, React, PostgreSQL, unit and end-to-end tests, 7+ years and Czech-based: a senior advert inside a
  "junior to mid" sample); Figma SWE Growth & Monetization (greenhouse 5552560004: 4+ years, React/TS, Ruby/
  Python/Go, PostgreSQL, code review); Pendo Sr. SWE Full Stack (greenhouse 8224073002: 5+ years, API design,
  unit/integration/e2e, AWS/GCP, Docker/K8s, LLM features a plus); StackAdapt Full Stack Engineer (marsdd,
  posted 2026-06-04, closed: GraphQL/REST design, test-driven, code review, DS&A, SQL); SpaceX Full Stack
  (Starlink Operations) (greenhouse 7973714002: git, automated tests, Linux, Docker/K8s/Helm, React, auth);
  Loenbro Full Stack SWE (builtincolorado, removed 2026-11-11: React, Node/Python, cloud, SQL, Git, code review,
  automated testing, CI/CD; "AI coding agents are utilized", "processes for AI-assisted development"); Breeze
  Fullstack AI Native (builtin, removed 2026-03-24: React/Node/TS, LLM features). Automox: no page loaded.
  Added: Softeta Junior Full-stack Engineer (AI-Native Development), workable, 2026-07-22 (Claude Code/Cursor
  practice, specs, directing and reviewing agent code, knowing when to stop an agent); Digital Turbine Fullstack
  JS/TS (2025-11-20; only as a check on HTML/CSS and AI tools: neither named).
- ai-assisted-development "essential on 6 of 8 ask for AI coding tools": not reproduced. Of seven re-opened
  pages, none requires an AI coding tool; one (Loenbro) describes AI coding agents in the team's process; four
  ask for LLM *product* features (Pendo, Loenbro, Breeze, Figma "iterating with AI"), which belong to
  llm-application-engineering (already a desirable line, 3 of 8). The skill is real and teachable (Softeta's
  junior advert spells it out: plan-first specs, review of agent diffs, re-planning; Affirm's backend advert
  requires "agentic coding"), so the line stays, demoted to desirable, cell "coding agents (Loenbro, Softeta)".
  This matches new-graduate-software-engineer, where it is desirable. The interview check "Reviewing AI-written
  code (Automox)" was removed: unverifiable.
- Classes against count: html-and-css essential on 2 of 8: kept; reason now in the cell (GitLab ladder, react
  needs it; adverts assume it). networking-basics desirable on 0 of 8: kept; reason in the cell (node needs it).
- Missing line added: caching-and-queues (2 Explain, desirable): api-design (essential) needs it; the old file
  only mentioned it in "Order", so `role` and `ready` never counted it.
- Order fixed: the old text ("api-design 1-8, then system-design-foundations, caching-and-queues") put
  api-design before two of its needs (its step 7 uses caching-and-queues 8). Now rows 1-8 of web/full-stack,
  then system-design-foundations, caching-and-queues, api-design, software-testing, the rest; linux before docker.
- Run: `role full-stack-developer --have "git:3"` -> 18 subjects, about 560 h (ai-assisted-development no
  hours). Hours fixed: essential 345, desirable 230 (was 205; caching-and-queues added).
- Other changes: interview checks re-sourced to pages that say it (Momence/StackAdapt testing; StackAdapt/Pendo
  API); Overlap "Front-end: rows 1 to 5" (rows 4-5 of this table are node and SQL) replaced by the card ids;
  "Next.js: no card" -> next-js (planned) (it is a planned row of web/full-stack); unverified notes Momence's
  7+ years; Proved-by cells shortened for room.
- Still unverified: Automox; whether the writer's Pendo/Figma/StackAdapt postings are the ones re-opened
  (newer or senior variants were found); levels.
- Score 7/10. Most holds it back: the sample leans mid/senior (Momence 7+, Pendo 5+, Figma 4+) for a
  "junior to mid" title; a junior learner is scored against a slightly heavier map than junior adverts ask.

#### roles/devops-engineer.md, reviewed 2026-11-19
- Sources opened: handbook.gitlab.com SRE family (Associate and SRE: Linux troubleshooting, VPCs/proxies/CDNs,
  Kubernetes basics, Terraform basics and GitLab CI, Ansible and Chef basics, Prometheus/Grafana, on-call, RCA:
  every GitLab citation in the file holds; there is no "Intermediate" level, so "(Associate, mid)");
  training.linuxfoundation.org CKA (Troubleshooting 30%, as cited). Adverts: Bayer Junior DevOps (justjoin.it,
  published 2026-01-20, not 01-16: Bash/Python, Linux, Git, any cloud, IaC exposure, GitHub Actions, containers,
  monitoring; also Kafka/Kinesis); Kforce DevOps II (wearedevelopers: Python, Kubernetes with Helm, Terraform
  required, Ansible nice, AWS, Prometheus/Grafana); Sitecore Platform Engineer (ziprecruiter, posted 2026-07-13,
  3-5 years: Azure, Kubernetes/Helm, Terraform modules, Linux, Prometheus/Grafana, Git, CI/CD; GitOps nice; a
  later or different posting from the writer's 05-12). Settling the weak sample (4 of 9 closed, 3 unnamed):
  Miratech Junior DevOps (arc.dev: AWS, Terraform/CloudFormation, Linux, GitHub Actions, Docker, Bash/Python,
  Git; Kubernetes, monitoring, networking nice) and an unnamed Junior DevOps via tealhq (cloud, CI/CD,
  Bash/Python, Linux, Docker, DNS/TCP/load balancing; IaC, Kubernetes nice).
- Counts: in the two newer adverts git is required in one (Miratech) and "version control" in the other; with
  Bayer and Sitecore that supports git essential beyond the file's 4 of 9 (reason in file stands). "AWS (9 of
  9)" was wrong as worded: Sitecore requires Azure, Bayer and the unnamed accept any cloud -> "a cloud (9 of 9;
  most AWS)". "scripting (9 of 9)" -> "scripting, Python or Bash": most adverts accept either; python-core stays
  essential (Kforce requires Python; the linux card carries the shell). Kubernetes is often "nice to have" for
  juniors (Miratech, unnamed) but 8 of 9 and the CKA keep it essential.
- Terraform, Helm, Ansible, cloud: each a planned line with its count; none bent onto an existing card. Good.
- Order: table order respects every needs (docker after linux and networking; CI after git and docker; k8s
  after docker; terraform after CI and cloud per the map). reliability-and-observability needs
  system-design-foundations and caching-and-queues, which are not lines; the file says they wait as `later:`.
- Run: `role devops-engineer --have "git:3"` -> 10 subjects, about 255 h (helm unknown). `role` takes docker
  as 20 h (ai map) while this track's map says 30 h: hours now "270 h (`role`; 280 by this map's docker)".
- Changed: sources (Bayer date, Miratech added, "3 reopened"); git, cloud, scripting cells; hours; Proved-by
  cells shortened for room.
- Still unverified: Career Team, commercetools, Greenhouse, institutedata, recruitee, joindevops adverts not
  reopened; interview checks are inferred from requirements and the CKA weights, not from interview guides.
- Score 7/10. Most holds it back: two of its ten essential lines (cloud, Terraform), the core of the job, are
  planned with no card, so the essential score cannot pass 80% today and the planner has no steps for them.

#### roles/ai-engineer.md, reviewed 2026-11-19
- Sources opened: AWS Certified Generative AI Developer - Professional exam guide (docs.aws.amazon.com
  ai-professional-01: domains 31/26/20/12/11%; out of scope "Model development and training", "Advanced ML";
  AI safety and security 20%: supports the prompt-injection check); GitLab ML engineering family
  (handbook.gitlab.com job-description-library/.../machine-learning: Python, secure and well-tested, on-call; the
  file's old path no longer loads). Adverts: Rillet Applied AI (builtin: mid, Python, agentic systems, offline
  and online evals, ML or backend foundation, APIs, cloud); Atomicwork Applied AI (builtin, removed 2026-11-01:
  Python, PyTorch/TensorFlow familiarity, RAG, vector search, evaluation pipelines, fine-tuning, Git, testing);
  Glean LLM Evals & Observability (greenhouse 4669417005: an evals-specialist role, as the writers said).
  Impiricus: index page only. Added to settle the senior and evals bias: Capco Mid Level AI Engineer
  (pitchmeai, confirmed open 2026-11-18: Python REST APIs, RAG with vector databases, Git, CI/CD, testing, code
  review, cloud; evaluation platforms, Docker/K8s, TypeScript nice) and Jolera AI Engineer (2026-02-09, mid:
  Python with NumPy/pandas/scikit-learn, RAG and vector databases, APIs, SQL, Docker, CI/CD; interview includes
  "System design and architecture discussion").
- Evaluation inflation: in the three mid-level adverts evals appear in two as required (Rillet, Jolera) and
  one as nice (Capco); llm-application-engineering stays essential (LLM features are in every advert anyway).
  retrieval-systems essential holds (RAG in Capco, Jolera, Atomicwork).
- machine-learning-fundamentals desirable on 2 of 12: Jolera requires scikit-learn, Rillet asks for an ML or
  backend foundation; with Jolera it is 3 of 14, the bottom of the desirable band: kept, cell says "(2 of 12;
  Jolera)".
- Missing lines added: git (desirable; Capco, Atomicwork; and github-actions-ci-cd needs it); networking-basics
  (desirable; api-design, system-design-foundations, reliability-and-observability need it: it was only in
  "Order"). caching-and-queues specialist -> desirable: api-design and reliability-and-observability (both
  essential) need it, so as specialist it was invisible to `role` and to `ready` without --all.
- Order fixed: the old text put caching-and-queues before system-design-foundations (which it needs) and left
  sql-and-relational in "the rest", after three essential lines that need it. Now python-core,
  llm-application-engineering, retrieval-systems, networking-basics, sql-and-relational,
  system-design-foundations, caching-and-queues, api-design, reliability-and-observability, then the rest by
  their needs.
- Run: `role ai-engineer --have "git:3"` -> 16 subjects, about 495 h; hours stated as essential 200 h,
  desirable 310 h (was "445 h" for both, before the three lines were added or moved).
- Other changes: design interview check re-sourced to Jolera (its stated interview); "Backend coding" check
  dropped for room (python-core and api-design remain covered by the capstone); sources compressed, closed
  adverts starred; Proved-by cells shortened.
- Still unverified: Distyl, GitLab (closed), Fieldguide, Ro, Onit, Employ, Version 1, SAI, Impiricus not
  reopened; levels; "fine-tuning (5, a plus)".
- Score 7/10. Most holds it back: retrieval-systems (essential) and llm-fine-tuning, model-serving-and-mlops
  (desirable) have no card; and llm-fine-tuning's map row needs deep-learning-with-pytorch, a specialist line,
  so a desirable line's own prerequisite is outside the default score.

#### Conflicts with files outside my list (not edited)
- Hours: python-core 40 h (ai/ai-engineering) against 30 h (core-cs/coding-interviews); docker 30 h
  (devops/containers-and-delivery) against 20 h (ai/ai-engineering, web/full-stack). `us_path.py` takes the first
  map loaded, so every role's totals depend on map file order. The map owners should agree one figure.
- software-testing (planned) is a row of web/full-stack whose needs are react and node-and-express ("from browser
  to database"), yet backend-engineer and new-graduate-software-engineer use it as an essential line for Python
  services. Its future card must not need react, or the backend roles need a different planned id.
- ai-assisted-development (planned) is in three roles but in no track map, so it has no hours and no needs.

#### Script behaviour (reported, not edited)
- `role` and `ready` see only the role's own lines: a card an essential line needs but the role omits is never
  listed, counted in hours or scored (before this review: caching-and-queues in full-stack and AI,
  networking-basics in AI; still: linux-command-line for docker in three roles; system-design-foundations and
  caching-and-queues for reliability-and-observability in devops).
- Hours are the full card's hours whatever the level asked (cloud-core-services at 1 Use counts 30 h).
- `ready` prints at most 18 lines: full-stack has 19 non-specialist lines, so docker is hidden behind "... and 1
  more line" while still counted.
- "Next": during this session it first proposed planned subjects with no card (retrieval-systems,
  llm-fine-tuning) ahead of essential cards; later (script apparently changed meanwhile) it proposes desirable
  git and typescript ahead of essential llm-application-engineering because the latter waits for python-core.
  A learner reading "Next" as "most important next" is misled either way.
- Planned subjects' "Needs first" from the track maps are ignored by "Next".
- `mark roles/<id>` is refused ("no curriculum file"); the bare role id works.


## INTEGRATION-WDA: Editor's pass over web, DevOps, AI and the role maps

### Integration of the web, DevOps and AI tracks and five roles (editor-in-chief), 2026-11-19

Read in full: FORMAT.md, REVIEWING.md, STAGE45-REVIEW.md; R7, R8 in full; R9-R13 conflicts and "could not check"
parts (and the per-file blocks where they touch my files); my 12 cards, 3 maps, 3 indexes, 5 roles; the steps of
git, networking-basics, sql-and-relational, api-design, caching-and-queues, system-design-foundations,
reliability-and-observability. No git command run; nothing installed; scripts/ and tests/ untouched. Originals of
the whole curriculum kept at /tmp/wda/orig-curriculum (diff shows only my 16 files changed).

`us_path.py check` before: "check ok", no note. After: "check ok: 34 cards, 6 maps, 5 roles, 5 indexes", no note.
Holes were also searched by a script (/tmp/wda/xref.py) that, for each goal's spine, lists every "card N" or
"step N" a chosen step points at that the goal does not take.

#### 1. One home per idea and per word
- node-and-express: wrong beliefs [3] "`async` code runs on other threads" and [4] "Marking a function `async`
  stops it blocking" removed (javascript [12] owns them). Replaced by the Node-only belief [4] "The worker pool
  runs my slow JavaScript" (truth from nodejs.org "Don't block the event loop", reopened: the pool runs only
  built-in work such as `fs`, `dns.lookup`, `crypto.pbkdf2`, zlib; your CPU work blocks unless split up or moved
  to a worker thread). Step 5 now reads "Async errors in Node (on javascript 9, 11-12): error-first callbacks,
  `util.promisify`, `fs/promises`; ..." instead of re-teaching promises and `await`.
- npm moved to its first meeting (below); node-and-express 2 keeps only what is Node's: `"type"` picking ES
  modules or CommonJS, `^` ranges against the lock file, `npm ci`, `npm audit`. Words `package.json`,
  `lock file` go to javascript [8]; `devDependency` dropped as a word; alias `npm` moved from node to javascript.
- javascript vs react: the stale-response race is taught at javascript 14, so the word `stale response` moved
  there (react [10] gives it up) and javascript [14] gives up `HTTP status code` (networking-basics 8 owns
  `status code`, same idea). react's [10] failure now names React's own cause (no cleanup ignored or aborted the
  older response). react [14] gives up `build tool` (javascript 8 owns `bundler`).
- javascript vs typescript: no idea taught twice (TypeScript types `async`, JSON and `catch`; javascript runs
  them). Nothing changed.
- Words left in two homes that one learner now meets: node [7] `environment variable` -> `fail fast`
  (linux-command-line 7 owns the mechanism, web goal 2 now takes linux 7); node [14] gives up `SIGTERM`
  (linux-command-line 6); docker [10] gives up `exit code` (linux-command-line 1 `exit status`; docker 10 now says
  "128 + signal (linux-command-line 6)"); llm [2] gives up `exponential backoff, jitter` (caching-and-queues 9,
  taken by AI goals 2-3) and `rate limit` (api-design `rate limiting`), takes `system prompt` (taught in step 2).
- docker "Later" said Kubernetes had no card: removed (kubernetes-core exists; the map owns order).
- llm-application-engineering 12 now says it teaches `asyncio` (`gather`, a `Semaphore`), the home python-core's
  "Later" points at (R11's conflict); "transformers (deep-learning)" -> deep-learning-with-pytorch (R11).
- Left, with reason: github-actions [10] `image tag` beside docker [12] `tag` (no other word fits step 10; a
  failure would need a run I cannot do); llm [5] `failure mode` beside system-design-foundations (other meaning;
  no goal takes sdf 5 with llm 5).

#### 2. Holes between cards
- npm, `package.json`, a build: home javascript 8 ("Modules and packages"), because every web learner and
  every later card (typescript, react, node-and-express) passes it. Taught as mechanism: `dependencies`,
  `devDependencies`, `scripts`; `npm install` filling `node_modules` and the committed lock file; Node or a bundler
  resolving bare names there; `npm run build`, `npm test`. No versions; the package manager is a look-up item.
  react 13 now runs tests in "the project's runner (`npm test`, looked up)" and react 14 runs the framework or
  build tool "by its `package.json` scripts (javascript 8)".
- React typing: home react, steps 1 (`.tsx`, props inline or as a `type`, `children: React.ReactNode`), 3
  (inline handlers infer the event, extracted ones name it, `React.ChangeEvent<HTMLInputElement>`), 4 (typed
  from the initial value, so `useState<User | null>(null)`), each "typed (typescript held)", plus failure [4]
  "TypeScript refuses `setUser(user)`: `useState(null)` inferred the type `null`". Not typescript 12: typescript
  needs only javascript and comes before react, so it cannot use React. Web goal 4 takes react 1, 3-4.
- linux-command-line: web row 12 and ai row 6 already named it in Needs first; now every goal using docker names
  its steps (linux-command-line 1-8, 12, the DevOps map's choice), and Why says where its row lives.
- Holes found by reading the outlines (all fixed in the goal lines):
  - DevOps goals 1-2: networking-basics 8 writes HTTP on step 4's socket and compares versions by step 5's
    head-of-line blocking (R8's reason), and linux 12 points at the refused/timed-out distinction (step 10):
    now 1, 3-5, 8, 10 and 1, 3-5, 7-10.
  - AI goal 1: python-core lacked 13 (virtual environment and dependencies, needed to install the SDK and
    Pydantic of llm 2, 4) and 6, 8 (lists, comprehensions); now 1-4, 6-8, 10-14. "Another language:
    python-core later" removed: the card teaches in Python.
  - AI goal 2: reliability and api-design steps leaned on system-design-foundations 1, 3-4, 7, caching-and-queues
    8-9, sql-and-relational 7, 9 and networking-basics 4-5, 8-10, none named; now named. llm 1 (tokens set cost)
    added to a "cheap" goal.
  - AI goal 3: no git, no networking-basics, no linux-command-line for docker, no system-design or
    caching-and-queues steps for api-design 7 and reliability 1-7; ML 8-9 used models (5-6) and a pipeline (7) it
    skipped; docker skipped step 8 (secrets) for a service holding an API key; sql skipped modelling (5);
    api-design 9 points at 12. All added: about 270 h, not 185.
  - AI goal 4: llm 5-6 judge with a model called in step 2 (added); ML 8 uses 5's regression (whole row taken).
  - Web goal 3 "javascript 13-14, its other steps usually held" held only for a Node developer: now rows 1, 2,
    react 1-11, 13-14, with the Node case stated (145 h, 95 h).
  - Web goal 2 named no steps for git, typescript, networking or linux, and left out rows 10-11 (planned):
    named; testing and auth "when written".
- Every goal re-run with `spine` and the cross-reference script: no remaining pointer to an untaken step.

#### 3. Goal lines (hours = `spine` scaling of the maps' Hours)
- web: front-end job 210 h; full-stack job 345 h (before rows 10-11); back end to UI 145 h (95 h); add
  TypeScript 40 h. DevOps: 90 h; 130 h (75 h held); 170 h; 205 h. AI: 35 h (50 with 7-10; 70 with Python);
  85 h; 270 h; 65 h (105 h with Python). Maps: 900, 896, 899 tokens (cells, Why, Checkpoints, Short on time cut;
  the "never skip" lists replaced by "Goals' steps are the floor").

#### 4. Planned subjects
- software-testing: stays web row 11; Needs first "2, python-core" (one language, not both, said in Why), no
  longer react and node-and-express, so the backend and new-graduate essential lines rest on a subject whose
  needs a Python learner meets. web-auth-and-security (row 10) the same: "6, 8, python-core".
- ai-assisted-development (found in two roles, new-graduate and full-stack, not three): a teachable subject
  (agent context, diff review, tests first, agent permissions); new web row 14, Needs first 3, 11, 15 h.
- operating-systems-core (new-graduate): no map plans it and core-cs is not mine; the line's evidence is "Linux
  (Google preferred)", which linux-command-line teaches: line replaced by linux-command-line (2 Explain, same
  evidence and proof). Overlap "OS" -> "Linux".
- helm-and-gitops (devops desirable): new DevOps row 11, needs 2, 6, 20 h. configuration-management-with-ansible
  (devops specialist): row 12, needs 1, 15 h, 2 Explain. DevOps goal 4 takes rows 8 to 11 when written.
- Other planned ids in roles all have map rows.

#### 5. Roles (orders against needs; hours = `role`)
- new-graduate: table order holds; Essential 190 h, desirable 240 h (role prints 430).
- backend: the old "the rest" put distributed-systems-core before scaling-data and cloud before docker; now
  "then table order, each after its needs (linux-command-line 20 h, docker, then cloud, CI)"; 190 + 310 (500).
- full-stack: "the rest" put CI and cloud before docker and llm before python-core; now "the rest after their
  needs (off this list: python-core 40 h; linux-command-line 20 h)"; 345 + 255 (600). Overlap front-end now
  points at web rows 1-5.
- devops: reliability's needs taken as steps (DevOps goal 3), the rest later; 280 + 20 (300).
- ai-engineer: off-list needs named (linux-command-line 20 h, javascript 60 h); 200 + 320 (520).
- Advert counts and sources untouched in all five. All at or under 800 tokens.
- Indexes: web, devops, ai "Roles this domain feeds" now name the role maps that exist.

#### 6. Statuses and new claims (all verified; files keep `reviewed`)
- javascript 8 npm mechanics: run with Node v22.23.4, npm 10.9.9 offline, local `file:` packages in /tmp/wda/npm:
  `npm install` wrote `dependencies`, `--save-dev` `devDependencies`, created `node_modules` and
  `package-lock.json`; `npm run build` found a dependency's binary via `node_modules/.bin`; `npm test` ran the
  `test` script; Node resolved bare `import "dep"` from `node_modules`; `npm ci` rebuilt `node_modules` from the lock.
- react typing: react.dev/learn/typescript (opened): `.tsx`, props inline or `type`/`interface`,
  `React.ReactNode`, `useState` inferred from the initial value or given a type argument, handlers inferred
  inline and typed `React.ChangeEvent<HTMLInputElement>` when extracted, `@types/react`. tsc (/home/claude/
  .npm-global/bin/tsc, strict) on useState's declared signature as a stub: `useState("idle")` is `string`,
  `useState<Status>` refuses other strings, `useState(null)` refuses an object (the new failure), a
  `User | null` state needs narrowing (TS18047). @types/react itself is not installed: not compiled against it.
- node: `util.promisify(fs.stat)`, `fs/promises` and an error-first `ENOENT` callback run on Node 22;
  `worker_threads` exists; worker-pool list from nodejs.org don't-block page.
- llm 12: `asyncio.gather` with `asyncio.Semaphore(2)`: six 0.1 s calls took 0.3 s (Python 3.13).
- Planned rows' hours and needs: judgement, under the maps' `unverified:` lines.

#### Not resolved
- `image tag` / `tag` (above). The `role` script still counts only a role's own lines (R13): off-list needs are
  stated in the roles' text. No React or Express was run (as R8).

## First design (pilot of 18 November): superseded records


##### system-design/foundations.md, reviewed 2026-11-18
- Sources opened: oreilly.com DDIA 2nd ed. contents (ch. 2 nonfunctional requirements first, 6 replication, 7 sharding, 10 consensus: supports rows 3, 5, 6); pdos.csail.mit.edu/6.824 schedule (Raft, linearizability, distributed transactions/2PC: row 6; it has no clocks lecture, clocks rest on DDIA ch. 9 "trouble with distributed systems"); sre.google/sre-book addressing-cascading-failures and contents (rows 7, 10).
- Changed: sources line rewritten to say what each source supports (the old line cited DDIA for rows 3 to 6, but DDIA has no caching-and-queues chapter); "Why this order" now states the reason for 6, 7, 9 and 10, not only 1 to 5; "Left out" merged into one line to stay within 800.
- Still unverified: hours and levels (judgement, already on the line).

##### system-design/INDEX.md, reviewed 2026-11-18
- Checked: every track named, `foundations` exists, planned tracks agree with the map's "Left out"; role new-graduate-software-engineer exists. No change.

##### cards/system-design-foundations.md, reviewed 2026-11-18
- Sources opened: sre.google/workbook/non-abstract-design (AdWords CTR worked example; "Is it possible? Can we do better? Is it feasible? Is it resilient?"; calculations of storage, IOPS, machines: confirms step 9 and estimating); cacm.acm.org/research/the-tail-at-scale (10 ms typical, 1 s p99, fan-out to 100 servers gives 63% slow: confirms step 4 and the Explain task); oreilly.com DDIA 2nd ed. contents (ch. 2 Defining Nonfunctional Requirements); docs.aws.amazon.com/wellarchitected pillars (six pillars: step 10); learn.microsoft.com/azure/architecture/patterns (Cache-Aside, Queue-Based Load Leveling, Retry, Circuit Breaker, Sharding: pattern names only, not load balancers or CDNs, so its use is narrowed).
- Run: python3 in /tmp: 1 - 0.99^100 = 0.634 (the 63%); 99.9% = 8.77 h down per year; three serial 99.9% dependencies = 99.7%.
- Changed: "More servers always add capacity" truth said "only for stateless parts", false for sharded stores: now "only while the work splits; then a shared database or lock is the limit". "Microservices make a system scale" truth left out that a stateless monolith scales out too: added. Removed the unsourced "Engineers read more designs than they write". Step 3 gains read/write ratio (a word to own that no step taught). Step 9 names the AdWords example.
- Still unverified: none beyond judgement of order.

##### cards/caching-and-queues.md, reviewed 2026-11-18
- Sources opened: usenix.org NSDI '13 Nishtala et al., Scaling Memcache at Facebook (look-aside; delete instead of update because deletes are idempotent; leases for stale sets and thundering herds, known from the paper); Builders' Library "Timeouts, retries, and backoff with jitter" (now served at builder.aws.com; retry at a single point in the stack, token-bucket retry limit, jitter, capped backoff alone keeps everyone retrying at the cap) and "Avoiding insurmountable queue backlogs" (measure message age, multi-hour recovery from short spikes, results too late to be useful, DLQ alarm, producers reject work); sre.google/sre-book/addressing-cascading-failures (retry budget, retries at multiple levels multiply, randomized exponential backoff, load shedding); aws.amazon.com/message/12721 (7 Dec 2021, us-east-1: surge of connections and retries, "a latent issue prevented these clients from adequately backing off", persistent congestion).
- Run: /tmp/sdrev/race.py, two deterministic interleavings: update-on-write leaves cache 1 while the database holds 2; delete-on-write with a slow reader also leaves cache 1. So "deleting is safer" was incomplete.
- Changed: wrong belief on updating the cache now says deleting narrows the race and leases or versions close it; "exactly once" truth adds loss when acknowledged early; "Retrying makes calls more reliable" truth admits retries do ride out brief faults; step 9 adds circuit breakers; step 2 points to networking-basics for HTTP caching headers instead of reteaching them; "Go deep" cut from five items to three sharper ones; "Never omit" says retries are limited in attempts (a cap on delay alone is what the Builders' Library warns against); dropped a duplicate production bullet and "cold cache" (taught as cold start) to stay within 1,200.
- Still unverified: none.

##### cards/scaling-data.md, reviewed 2026-11-18
- Sources opened: github.blog oct21-post-incident-analysis (43 s cut, Orchestrator promoted West Coast primaries, both sites held writes the other lacked, 954 unreplicated writes on one cluster, failed forward, 24 h 11 min degraded: confirms bullet, step 4 and the Explain task); discord.com/blog/how-discord-stores-trillions-of-messages (partitioned by channel and a static time-window bucket; hot partitions raised latency across the cluster; data services coalesce requests); infoq.com cap-twelve-years-later (Brewer: "2 of 3" misleading; choose C or A only during a partition); oreilly.com DDIA 1st ed. ch. 5, 6, 9 and 2nd ed. contents (ch. 7 is now titled Sharding).
- Changed: CAP truth now adds that outside a partition consistency still costs latency (the price step 10 teaches); "a replica is a backup" truth says "in seconds", not "at once"; step 6 gives the 2nd-edition word sharding; GitHub bullet shortened and kept exact; small cuts to stay within 1,200 (dropped "read replica" from words, kept "follower").
- Still unverified: "the usual first step is a read replica and a standby" is practitioner judgement, not sourced.
- Addendum (all four files above): to fit the longer `reviewed` status line I also removed the Azure patterns source from cards/system-design-foundations.md (it named patterns, not the building blocks the card uses it for), a duplicate "consumers must survive duplicates" bullet and the word "load levelling" from cards/caching-and-queues.md, the "Never omit" line that repeated the Promise in cards/scaling-data.md, and a few words in the map.

##### cards/networking-basics.md, reviewed 2026-11-18
- Sources opened: hpbn.co contents (latency, TCP, UDP, TLS, then HTTP: matches); MDN How_browsers_work (DNS, TCP 3-way, TLS 1.3 one round trip / 1.2 two); gaia.cs.umass.edu/kurose_ross/eighth.php (book keeps its top-down approach; the order DNS before IP follows it); engineering.fb.com 2021/10/05 outage-details (backbone command, DNS servers withdrew BGP routes, tools broke).
- Run: curl refused ("Connection refused" in -v), not resolved (curl 6), wrong-name certificate on a local openssl s_server (curl 60), `curl -w` dns/connect/tls/first-byte fields; a connect timeout made with a full listen backlog; two sends arriving as one recv (byte stream). Remote ping/dig/traceroute not runnable here (sandbox network).
- Changed: "mostly round trips" to "often" (unsourced proportion); trimmed for size.
- Still unverified: none beyond the order being a choice (top-down).

##### cards/sql-and-relational.md, reviewed 2026-11-18
- Sources opened: postgresql.org/docs/current contents; transaction-iso.html (phenomena table, default Read Committed, retry on 40001); use-the-index-luke ToC (functions, concatenated keys, N+1, offset vs seek, DML cost); DDIA ch. 7 headings (Preventing Lost Updates, Write Skew); added dbi-services.com Oracle "serializable is not serializable" (snapshot isolation, write skew shown).
- Run (PostgreSQL 16, /tmp): NULL = NULL gives null; default read committed; `lower(email)` seq scan vs index scan on 200k rows; row order changes after an UPDATE without ORDER BY; join doubles a sum; lost update at read committed; repeatable read aborts the second updater; write skew commits at repeatable read and is aborted at serializable; deadlock detected; ALTER TABLE queued behind an open transaction blocks a later SELECT; two inserts for one seat, one fails on the key.
- Changed: index belief "slows every write" to "adds cost to writes" (updates of other columns can skip it); transaction belief adds Oracle's serializable allowing write skew; injection belief adds that names (sort column) cannot be parameters, use a fixed list; step 5 adds types; removed the unsourced "most application data" line; ORM folded into the N+1 line.
- Still unverified: nothing material.

##### cards/git.md, reviewed 2026-11-18
- Sources opened: plans/learn-git/PLAN.md (all 17 chapters checked against the 14 steps: 10 = ch. 10-11, 11 = ch. 12-13, 12 = ch. 14-15, others 1:1); git-scm.com/book/en/v2 contents; missing.csail.mit.edu (2026 "Version Control and Git" lecture; tools classes skip).
- Run (git 2.43, /tmp): tree of a commit lists every file; branch ref is a 41-byte file; switch refused over local changes; deleted branch found in HEAD's reflog; a never-checked-out deleted branch found only by fsck; hard reset: staged edit survives as a dangling blob, unstaged edit gone; reset undone via HEAD@{1}; rebase gives new ids; detached-HEAD warning; secret found by `log -S` after deletion; non-fast-forward push rejected; merge conflict.
- Changed: says which steps are two chapters; hard-reset truth now names staged edits recoverable as nameless blobs; the project was "step 9's" but its finish line needs step 10 (recovery): now finished after step 10; secret line merged into undo line.
- Still unverified: stash comes late (step 12) by the plan's choice; defensible since step 4 solves a refused switch by commit or restore.

##### roles/new-graduate-software-engineer.md, reviewed 2026-11-18
- Sources opened: Dropbox IC1 (code reviews, well tested); GitLab backend engineer (well-tested, code review); Google Early Career Campus (google.com page taken down; anitab.org copy, posted 2026-08-14: DS/algorithms, AI tools minimum; Unix/Linux, networking, distributed systems preferred); Stripe New Grad (2026-09-02: AI tools with review minimum, code review preferred); Cohesity New Grad 2026 (2026-08-12: DS, algorithms, systems design, code reviews); Airtable New Grad 2026 (apply by 2026-03-06: DS, algorithms, software design, code reviews); Benchling New Grad 2026 (builtin.com, removed 2026-01-30: design, end-to-end ownership); D2L Spring 2026 New Grad (communitech.ca copy, not AI-marked: DS, algorithms, databases, distributed systems, automated tests, AI tools); Suade (workable.com original, 2026-05-21: SQL, Git, TDD, code reviews).
- Dropped: D2L and Suade aggregator copies marked AI-written (replaced by the copies above); "a UK remote graduate role (undated)", which cannot be opened by name.
- Changed: counts recomputed over 7 adverts (programming in all 7; DS/algorithms in 4); git evidence is code review (4 adverts, Dropbox, GitLab) and its proof raised to the git card's Build level; SQL evidence Suade and D2L; design evidence no longer "design docs" (no advert says so); AI tools adds D2L; Order notes dsa-core-techniques needs cpp-for-contests (25 h), which the table omits; hours 265 re-added from the maps (60+60+60+30+25+30).
- Still unverified: classes of the DP, graphs and specialist lines are judgement (no advert names them).

##### core-cs/competitive-programming.md, reviewed 2026-11-18
- Sources opened: cses.fi/book/book.pdf table of contents (ch. 17 Strong connectivity, 19 Paths and circuits, 20 Flows and cuts, 29 Geometry, 30 Sweep line); usaco.guide/general/choosing-lang (C++ advised so solutions are not a constant factor too slow); usaco.guide/silver, /gold, /plat module lists (centroid decomposition and convex hull trick are Platinum); cses.fi/problemset (categories).
- Changed: first rated contests moved from "after 4" to "after 2" (Div. 3/4 and AtCoder Beginner rounds need only rows 1-2; waiting ~200 hours wastes upsolving practice); row 9 needs "4" not "4, 6" (SCC, 2-SAT, Euler paths, flows need no range structures); row 6 "full DSU" became "DSU extensions" (basic DSU with both optimisations is taught in graphs-and-trees); the build note on rows 9-10 replaced by the reason row 8 needs 6.
- Still unverified: hours; topics of the planned rows.

##### core-cs/INDEX.md, reviewed 2026-11-18
- Checked: every track id and the role named exist or are marked planned; within limit. No change.

##### cards/cpp-for-contests.md, reviewed 2026-11-18
- Sources opened: usaco.guide choosing-lang, fast-io (sync_with_stdio, cin.tie; it does not discuss endl), debugging-cpp (warning flags, sanitizers, _GLIBCXX_DEBUG), debugging-general (stress test against a slow solution; causes per verdict); handbook ch. 1-4; cppreference Compare (irreflexivity, transitivity); codeforces blog 62393 (neal, anti-hash); blog 133941 (AI banned for solution logic in rated rounds); CSES Weird Algorithm exists.
- Run (g++ 13, /tmp): int*int into long long gives 1410065408, UBSan reports it; `1<<s` with s=40 gives 0 at -O2 and 256 at -O0 (UB differs by build); 5e6 lines with endl 2.46 s vs '\n' 0.24 s; sort with `a<=b` on 1001 items aborts ("malloc(): invalid next size"), ASan reports heap-buffer-overflow, _GLIBCXX_DEBUG flags it; unordered_map, 2e5 multiples of 172933: 42.9 s vs 0.01 s (107897 from the blog no longer bites at this size); std::lower_bound on a set 44 s vs s.lower_bound 0.01 s; empty v.size()-1 = 18446744073709551615; out-of-range read on a vector runs silently at -O2, ASan and debug mode catch it; recursive DFS on a 1e6 path segfaults with 8 MB stack (1e5 fine); vector passed by copy in recursion 1.42 s vs 0 by reference.
- Changed: compile command with warnings and sanitizers moved into step 1; step 2 no longer teaches complexity (dsa-core-techniques owns it: was taught twice); comparator truth now "strict weak ordering"; overflow belief states the types; unverified line names real judgement.
- Still unverified: practice counts and order are judgement.

##### cards/dsa-core-techniques.md, reviewed 2026-11-18
- Sources opened: handbook ch. 2 (input size table), 3, 6 (greedy, tasks and deadlines), 8.1 (two pointers); usaco.guide/silver/binary-search (firstTrue/lastTrue, round the midpoint up, overflow), /general/practicing (editorial step by step, implement afterwards); codeforces blog 62865 (rating R solves with probability 0.5); every CSES name checked on the problemset; Codeforces 1201C "Maximum Median" exists.
- Run: binary search with lo = mid and mid rounded down never ends (stopped at 100 iterations, lo=3 hi=4); rounded up ends in 4; `s = s + 'x'` 2e5 times 0.80 s vs `+=` 0.00 s; erasing the front 2e5 times 0.70 s.
- Changed: hash belief removed (duplicated cpp-for-contests) and replaced by "two nested loops mean O(n²)"; two-pointer truth now states the monotone condition; prefix-sum truth adds "on an unchanging array"; greedy truth: a stress test only finds counterexamples, it does not prove; binary-search failure states the cause exactly.
- Still unverified: rating bands, counts, times.

##### cards/recursion-and-dynamic-programming.md, reviewed 2026-11-18
- Sources opened: handbook ch. 5, 7, 10; atcoder.jp/contests/dp/tasks (Frog 1, Knapsack 1/2, LCS, Coins, Deque, Slimes, Matching, Digit Sum all exist); usaco.guide/gold (DP module order), /gold/intro-dp (push and pull, slow solution first, classics rarely set directly); every CSES name checked.
- Run: Coin Combinations sample (2,3,5; 9): sums-outer 8, coins-outer 3, matching CSES I and II; 0/1 knapsack upward loop takes one item three times (15 vs 5); unreachable state left at 0 gives a false answer; greedy on {1,3,4} for 6 uses 3 coins, best 2.
- Changed: memo belief adds that memo visits only reachable states; greedy-change truth gives a counterexample; small cuts.
- Still unverified: rating bands and times.

##### cards/graphs-and-trees.md, reviewed 2026-11-18
- Sources opened: handbook ch. 11-16, 18; cp-algorithms dijkstra_sparse (without the check up to O(nm)), disjoint_set_union, lca_binary_lifting (ceil(log2 n) levels); usaco.guide/silver/graph-traversal (Building Roads, Building Teams), silver and gold lists; every CSES name checked.
- Run: Dijkstra without the stale check: same distances, 5.0e9 edge scans and 5.9 s vs 2e5 scans and 0.03 s; BFS on a 1000x1000 grid marking on pop: 1,998,001 pushes vs 1,000,000, same distances.
- Changed: Counting Rooms moved from step 1 to step 2 (it needs DFS); 0-1 BFS moved from the negative-weights step to Dijkstra's; "Go deep" now three things (states as nodes, why BFS and Dijkstra give true distances, DP in topological order), not binary lifting; DFS belief notes trees as the exception; BFS belief scoped to BFS (Dijkstra finalises on pop); stale-entry failure marked "slow, not wrong".
- Still unverified: rating bands and times; recursion depth on each judge.

## Third design, 19 November: where the records are

The records of deepening (D1 to D17), of verification with every `Show:` rerun (V1 to V4, VA to VF) and of the editor's pass (E1) are 570 KB and are kept whole in `curriculum-records/reviews/` of the checkpoint archive, beside the `understudy` folder. Every card's status line says `reviewed` only after its verification record was written.
