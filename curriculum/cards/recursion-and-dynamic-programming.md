# recursion-and-dynamic-programming: from complete search to dynamic programming
kind: skill
aliases: dynamic programming, dp, recursion, backtracking, bitmask dp
needs: dsa-core-techniques
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/book/book.pdf ch. 5, 7, 10 (complete search, DP families, bitmasks); cses.fi/problemset, task
  pages and atcoder.jp/contests/dp/tasks (names, limits); usaco.guide bronze and gold lists (order),
  /gold/intro-dp (push, pull); cp-algorithms.com contents; g++ here (memoised Dice Combinations at n = 10^6
  crashed an 8 MB stack)
unverified: readiness bands and times are judgement

## Promise
Solve a problem by complete search, see the subproblems it repeats, turn it into a DP with a stated state,
transition, base case and order, and recognise the standard families in unseen problems.

## The one idea
A DP state is all the rest of the work needs to know, and no more. Picture: a hiker's note at each crossroads,
"best way from here": no path is walked twice. Where it breaks: if the best way from here depends on how you
arrived, the state is missing something; add it, and the table grows.

## In production
- Contests: classic DP problems are rarely set as is (USACO Guide); the work is the state.
- Interviews: brute force, memoised, then a table.
- A skill book whose programs run: plan `run: cpp` (`run: python` on the coding-interviews track: memoise
  with `functools.cache`; Python stops deep recursion with `RecursionError`, so long chains go bottom-up).

## Teaching order
1. Recursion: the call stack, base case, trust the smaller call; CSES Tower of Hanoi.
2. Complete search by recursion: choose or skip each item, a `used` array to build orders; count the leaves
   (2^n, n!) first; Apple Division again, Creating Strings.
3. Backtracking and pruning: cut a branch once it cannot succeed; Chessboard and Queens, Grid Path Description.
4. Memoisation: a recursion's repeated subproblems cached; AtCoder Frog 1, CSES Dice Combinations (answers
   modulo 10^9+7, cpp-for-contests 2).
5. Bottom-up tables: state, transition, base case, order, push and pull; Minimizing Coins, where greedy fails.
6. Counting with loop order: Coin Combinations I and II, same table, loops swapped, different answer.
7. Knapsack: Book Shop, Money Sums; AtCoder Knapsack 1 and 2 (swap what the table is indexed by).
8. Grids and two sequences: Grid Paths I, AtCoder LCS, Edit Distance; recovering the choices, not only the value.
9. Longest increasing subsequence: quadratic, then n log n with `lower_bound` (dsa-core-techniques 6);
   Increasing Subsequence.
10. Intervals and games: Removal Game, AtCoder Deque and Slimes.
11. Bitmask DP: a set as an integer index (the bitmasks of dsa-core-techniques 2); AtCoder Matching, Elevator
    Rides; why n stays near 20.
12. Digit DP (a tight flag per position) and probability DP: AtCoder Digit Sum and Coins, CSES Counting
    Numbers.
13. A DP for an unseen problem: what must be remembered (AtCoder Vacation: yesterday's choice).

## Judged by
- [2-3] The number of candidates (2^n, n!) was computed against the limits before coding.
- [4-13] The state is one written sentence naming every index ("best pages from the first i books, price ≤ w").
- [5-13] Transition, base case, order and the answer's cell are written before code; states times
  transitions, and the table's bytes, checked against the limits.
- [5] Impossible states hold infinity or −1, never a 0 that looks like an answer.
- [4,6,12] Each addition in a counting DP is reduced modulo the prime.
- [6-7] The loop order is justified: is order counted; may an item repeat.
- [8] The choices can be rebuilt, not only the value.
- [13] The DP matched its brute force on random small inputs.

## Step notes
### 1
Need: `hanoi` calls `hanoi(n-1, ...)`, which is not finished yet; how can I trust it?
Show: print each call indented by its depth. For n = 2, `hanoi(1,1->2)` stays open while its two
`hanoi(0,...)` calls run under it; n = 3 prints 7 moves from 15 calls; n = 20, 1,048,575 moves.
Explain: Each call has its own frame, fully described by its arguments `(n, from, to)`; if the smaller call is
right for any pegs, this one is. Those arguments are the first state you meet.
Try: predict: the depth where a recursion with no base case dies (here `-O0`: past 260,000; `-O2` made it a
loop that never died); build: CSES Tower of Hanoi, accepted.
### 2
Need: Creating Strings wants orders, and the next letter depends on the letters used; how do I loop over that?
Show: a `used` array over "aaaaabbbbb" reaches 3,628,800 leaves for 252 distinct strings; sorting and
skipping a letter equal to the last tried there leaves 252. 11 distinct letters: 4·10^7 leaves, one to a few
seconds; 12: 4.8·10^8, twelve times that.
Explain: Unlike the loops of dsa-core-techniques 2, a choice may depend on earlier ones, so recursion builds a
search tree; count its leaves against the limits before coding.
Try: predict: leaves for "aabac" with and without the skip (120, 20); decide: whether 2^n or n! fits a second at
n = 8, 12, 20.
### 3
Need: My Chessboard and Queens search is right; how can it finish with 8^8 placements?
Show: one queen per row. Checking only complete boards visits 19,173,961 nodes; checking each new queen against
the earlier ones and abandoning at once visits 2,057. Both print 92.
Explain: A cut abandons the whole subtree under a bad partial placement; the cost is the nodes visited, not the
leaves, so a test made early can save a factor of 10^4.
Try: predict: the node count when the test waits until row 4, then measure; build: Grid Path Description,
adding one cut at a time and logging nodes after each; done under one second on 48 `?`.
### 4
Need: I see the recurrence once it is shown; how was I supposed to find the state?
Show: Frog 1 as plain recursion, `cost(i)` = cheapest way to stone i, calls counted by argument. With 7
stones `cost(1)` runs 8 times, `cost(0)` 13: 33 calls for 7 arguments. At 30 stones: 2,178,308 calls, about a
second in Python; a dict on `i`: 58 calls, same answer.
Explain: The arguments that come back are the state; cache an answer per argument and the cost is states times
work per state.
Try: predict: calls at 32 stones without the cache (5,702,886); fix: memoised Dice Combinations
dies at n = 10^6: find the depth (here near 174,000), rewrite it bottom-up.
### 5
Need: The memo works; how do I turn it into loops, and in what order do I fill the table?
Show: Minimizing Coins, coins {1,3,4}, x = 6, printing `dp` per sum: `[0,1,2,1,1,2,2]`: two coins (3+3), where
greedy takes 4+1+1. Start the table at 0, not infinity, with coins {2}, x = 3: it prints 1, not −1.
Explain: Say "dp[s] is the fewest coins with sum exactly s" before coding, then the transition (last coin c:
dp[s−c]+1), the base (dp[0] = 0), and an order filling dp[s−c] first. Pull reads earlier cells; push writes later.
Try: build: the four lines written, then Minimizing Coins accepted; predict: dp[0..7] for coins {2,5}.
### 6
Need: Coin Combinations I and II have the same two loops; why are the answers different?
Show: coins {2,3,5}, x = 9. Sums outer, coins inner: 8. Coins outer: 3. Print both tables: they first differ at
5 (3 against 2: 2+3, 3+2, 5 against {2,3}, {5}).
Explain: With sums outer, any coin can be the last at every sum, so orders count; with coins outer, coins enter
one at a time, so each multiset is built in one order only.
Try: explain: list the 8 and the 3 by hand; fix: their version without `% MOD` passes the samples; find the
smallest x where it fails.
### 7
Need: Book Shop is Coin Combinations II with prices; why does my one-row table promise more pages than exist?
Show: the Book Shop sample (x = 10, answer 13), one row: `w` looped down gives 13, looped up 16: the book of
price 5 bought twice.
Explain: "dp[w] is the most pages with total price at most w using the books so far"; looping down reads only
cells from before this book. Knapsack 2 has weights to 10^9: index by value, store the least weight.
Try: predict: what the upward loop buys on a three-item case, then run; decide: cells for Knapsack 1 and 2 under
each indexing, from their limits.
### 8
Need: I have the edit distance; the judge wants the edits. Do I store a path in every cell?
Show: LOVE to MOVIE: print the 5 by 6 table, value 2. From the last cell, step to the neighbour whose value plus
its cost equals the cell: replace L by M, insert I.
Explain: Each cell equals one of its transitions applied to a neighbour, so walking back from the answer cell
recovers the choices; the full table is what makes that possible.
Try: build: AtCoder LCS printing the string; decide: when two rows save memory, what you lose (the walk back).
### 9
Need: The fast LIS keeps an array with `lower_bound`; is that array the subsequence?
Show: 3 1 4 1 5 9 2 6, printing the array after each value: it ends `[1,2,5,6]`, length 4, right, but 2 comes
after 5 in the input. The quadratic DP takes seconds at n = 5·10^4 in C++ (1.25·10^9 pairs), minutes at 2·10^5; this one
hundredths of a second at 2·10^5.
Explain: `tails[k]` is the smallest end of an increasing subsequence of length k+1 seen so far; a smaller end
never hurts, so only the length means anything.
Try: predict: the array for 2 2 2 with `lower_bound` and with `upper_bound`; build: Increasing Subsequence, then
print one real LIS from a parent per element.
### 10
Need: In Removal Game, why not take the bigger end each turn?
Show: the CSES sample 4 5 1 3: perfect play gives the first player 8, bigger-end greedy 7. A search over arrays of
four values 1..9 finds (1,1,3,2) first: 4 against 3.
Explain: dp[l][r] is the best (mine minus yours) for the mover on a[l..r]; each move hands the other player a
shorter interval, so fill by length.
Try: predict: both values on 1 1 3 2, then trace the table; build: AtCoder Slimes, writing first why its state
is an interval.
### 11
Need: Matching counts pairings for n ≤ 21, and orders are 21!. What is small enough to index?
Show: on random compatibilities, brute force over all 10! orders and dp[mask] agree; at n = 21 the 2,097,152
masks take a fifth of a second in C++, where orders would be 5·10^19.
Explain: Which women are taken is a set, and the order they were taken in does not matter; man i is the count
of bits in the mask, so the set alone is the state.
Try: decide: masks and memory at n = 20, 25, 30; build: Elevator Rides with dp[mask] = (rides, weight of the
last ride), the sentence written first.
### 12
Need: Digit Sum gives K with 10,000 digits; how do I count numbers I cannot loop over?
Show: the sample K = 30, D = 4: brute force 6; states (sum mod D, tight) give 6; with the tight flag dropped, 24
(the count for 1..99). With 10,000 digits and D = 100: 1.5 s in Python.
Explain: Build the number digit by digit; while its prefix equals K's (tight) the next digit is at most K's,
afterwards any. A probability DP is the same table holding probabilities.
Try: predict: the answer for K = 30 if tight is forgotten; build: AtCoder Coins, "dp[i][j] is the probability of
j heads among the first i coins" written first.
### 13
Need: Facing a new problem, how do I decide what the state must remember?
Show: Vacation, three states. The day only (a best total per day; next day, the best activity unlike the one
used): 210 on the sample, right; days (10, 0, 0), (100, 1, 1): 11, not 100; one random test in four of up to 5
days fails. (day, yesterday's activity): right on 3000. The whole history: right, by 3^n tries (531,441 at 12).
Explain: A state is enough when the best future from it does not depend on how you got there: start from the whole
history and drop what the future never reads.
Try: decide: a one-sentence state for an unseen problem from their judge, and why it is enough, before code;
fix: a DP failing hidden tests, found by a brute force on random small inputs.

## Believable numbers
- Run here (g++ -O2, Python 3.13, a shared two-core machine, November 2026; a laptop is as fast or faster):
  Dice Combinations bottom-up at n = 10^6, hundredths of a second in C++, half a second in Python; a one-row
  knapsack of 10^8 cell updates (1000 items by 10^5 weights) under a tenth in C++, while Python manages about
  10^7 updates a second. About 10^8 to 10^9 simple steps a second in C++, 10^7 in Python.
- [1,4] Stack: 8 MB here (`ulimit -s`); a small recursive function died near depth 174,000. Python 3.13 raises
  `RecursionError` at its default limit of 1000.
- [5-7] A table of 10^8 `int` is 400 MB.

## Go deep, leave for later
- Deep steps: 4, 5, 6, 13 (finding the state in a recursion's arguments, saying state and transition
  before code, what loop order counts, and choosing a state alone; reconstruction, step 8, rides on 5).
- Later: DP on trees and DAGs (graphs-and-trees 7, 9); meet in the middle; broken profiles (Counting
  Tilings); a DP sped up by a Fenwick tree (Increasing Subsequence II); sum over subsets (CSES SOS Bit
  Problem); divide-and-conquer and Knuth optimisations.

## Never omit
- Every DP starts as a recursive brute force.

## Wrong beliefs
- [1] "Recursive calls share the local variables" (each call has its own, on the stack, until it returns).
- [4-5] "Memoisation and tables are different algorithms" (same states and transitions; memo skips unreached
  states, uses the stack).
- [5] "Greedy works for making change" (coins {1,3,4}, sum 6: greedy uses 3 coins, the best 2).
- [6-7] "Loop order does not matter" (it decides whether order counts, and whether knapsack items repeat).
- [9] "The `lower_bound` array is a longest increasing subsequence" (only its length is; 3 1 4 1 5 9 2 6 ends
  with [1,2,5,6]).
- [13] "DP is a formula to memorise per problem" (it is a chosen state; the families are patterns of states).

## Failures to diagnose
- [4-5] Wrong on the smallest inputs: the base case.
- [5] 0 printed where no answer exists: an unreachable state left at 0.
- [7] 0/1 knapsack answer too large: a one-row table looped upward reuses items.
- [4,6] Wrong only on big tests: a missing modulo.
- [7-8] Memory limit: a full table where two rows do.
- [1,4] Runtime error: memoised recursion 10^6 calls deep overflows the stack (in Python, `RecursionError`).
- [13] Samples pass, hidden tests fail: the state forgets something (Vacation by day only).

## Practice and project
Per family: the chapter's tasks, then about ten Codeforces problems tagged dp, from your rating to 300 above.
Stuck: the editorial a step at a time, then code it closed. Log each miss: state, transition, order or bug.
Project: a DP notebook, a page per family (state, transition, trap).

## Mastery ladder
- Use: solve the chapter's tasks given the state.
- Explain: for a solved problem, say why the state is enough and why the order works.
- Build: solve three of four unseen, untagged Codeforces DP problems rated 1500 to 1700, an hour each.
- Design: for a new problem, compare two states by size and correctness, and pick one.

## Words to own
[1] base case, call stack; [2] search tree; [3] backtracking, pruning;
[4] overlapping subproblems, memoisation; [5] state, transition, bottom-up, push and pull; [6] loop order;
[7] knapsack; [8] reconstruction; [9] longest increasing subsequence; [10] interval DP; [11] bitmask DP;
[12] digit DP, probability DP; [13] state design
