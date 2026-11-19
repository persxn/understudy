# dsa-core-techniques: core algorithmic techniques for contest problems
kind: skill
aliases: dsa, algorithms, complete search, binary search, two pointers, prefix sums, greedy
needs: cpp-for-contests | python-core
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/book/book.pdf ch. 2-3, 5-6, 8 (speed table, complete search, greedy, two pointers);
  cses.fi/problemset (task names, categories); usaco.guide module lists (Bronze puts complete search
  before greedy; /bronze/rect-geo), /silver/binary-search-sorted-array, /general/practicing (editorials);
  codeforces.com/problemset/problem/1201/C, 1915/F (limits); codeforces.com/blog/entry/62865;
  run here: every Show and number, rerun 2026-11-19
unverified: practice and readiness bands, counts and times are judgement

## Promise
Meet an unseen problem, read the needed complexity from its limits, find the work the brute force repeats,
choose the technique that removes it, argue it is correct, and get it accepted in C++ or Python.

## The one idea
Ask what work the brute force repeats; each technique keeps something so it is never redone. Picture: a bank
statement's running balance; spending between two dates is one subtraction. Where it breaks: only what can be
undone; a running maximum cannot be subtracted.

## In production
- Contests: a round's early problems often need only these and one observation.
- Interviews, code review: a search in a loop replaced by sorting, hashing or prefix sums.
- A skill book whose programs run (`run: cpp`, or `run: python` after python-core); C++ names first,
  Python's where they differ.

## Teaching order
1. Limits to a target complexity: the operation budget (about 10^8 simple steps a second in C++, 10^7 in
   CPython); CSES Maximum Subarray Sum by every start and end, counted before it runs, then the linear scan.
2. Complete search by loops: every subset as a bitmask (`&`, `|`, `^`, `<<`, `>>`, and how they bind), every
   order by `next_permutation` (Python `itertools`); CSES Apple Division.
3. Arrays and strings: counting arrays, off-by-one, simulation and casework; Palindrome Reorder; rectangles'
   overlap, per axis max(0, least right end − greatest left end).
4. Sorting as a tool: sort then scan, sort by key, coordinate compression; Distinct Numbers, Stick Lengths.
5. Hashing: a seen-before set or a count map (`unordered_set`, `unordered_map` from cpp-for-contests 6-7;
   Python `set`, `dict`) replaces an inner search; Sum of Two Values; crafted keys slow both.
6. Binary search on a sorted array: the invariant, the first-true template, `lower_bound`, `upper_bound`
   (Python `bisect_left`, `bisect_right`); USACO Silver Counting Haybales.
7. Binary search on the answer: a monotone yes/no check; Factory Machines, Array Division, Codeforces 1201C
   Maximum Median.
8. Two pointers: Ferris Wheel, Apartments; pointers only move forward, so the work is linear, amortised
   (at most 2n moves).
9. Sliding window: grow right, shrink left, counts in a map; Playlist.
10. Prefix sums: 1D (prefix xors too: `(x ^ y) ^ y` is `x`), 2D, and a map of earlier sums; Forest Queries,
    Subarray Sums II, Subarray Divisibility.
11. Difference arrays and a sweep line over sorted events: range additions, arrivals and leavings; Restaurant
    Customers.
12. Greedy: the exchange argument; a stress test against step 2's complete search finds counterexamples
    (cpp-for-contests 9; in Python the same loop); Movie Festival, Tasks and Deadlines; a greedy over a
    `multiset` (cpp-for-contests 6): Movie Festival II.
13. Mixed sets, tags hidden: unseen CSES Sorting and Searching problems (Missing Coin Sum, Collecting Numbers);
    CSES Construction Problems, starting with Inverse Inversions (an answer built, not searched for).

## Judged by
- [1] The target complexity was written from the limits before code (n = 2·10^5: n² is 4·10^10, too slow).
- [2] Before a complete search was coded, 2^n·n (subsets) or n!·n (orders) was counted against the budget.
- [1,13] A brute force agreed with the solution on random small inputs.
- [6-7] The yes/no predicate is written, shown monotone, its range's ends justified; the loop keeps "lo is no,
  hi is yes".
- [8-9] It is said why no pointer moves back and why no better window is skipped.
- [10-11] Index 0 of the prefix array is 0; in C++, sums that can exceed `int` are `long long`.
- [12] Each greedy has an exchange argument written, or was stress-tested and is marked unproved.
- [13] Each miss is logged with its cause and the rule that would have caught it, then upsolved.

## Step notes
### 1
Need: My brute force is right on every test I made; can I tell before submitting that it is too slow?
Show: Maximum Subarray Sum over every start and end: right on the sample. Count first: n(n+1)/2 ≈ 2·10^10
additions at n = 2·10^5; at about 10^9 a second, 10 to 20 s against a limit of 1. Then the largest test,
`(echo 200000; seq 200000) > big.in`, timed: over ten seconds on any machine (12.8 s here); the linear scan:
hundredths, the same 20000100000.
Explain: Count the innermost line's runs as a power of n against a budget of 10^8 a second (a running sum
manages 10^9; most steps are heavier), and you know whether a plan fits before writing it.
Try: decide: the largest complexity for n = 20, 5000, 2·10^5, 10^6, then submit the brute force and the scan;
fix: a scan whose `best` starts at 0, on `3 / -5 -2 -8` (answer −2), accepted.
### 2
Need: Apple Division allows n = 20: 2^20 ways to split the apples; isn't trying them all far too slow?
Show: count first: 2^20 subsets × 20 items ≈ 2·10^7 steps, a fifth of the C++ budget. Every mask m from 0 to
2^n − 1, item i in the first group when `m >> i & 1`: 20 weights up to 10^9 take hundredths of a second in C++
(0.07 s here), about two seconds in Python. At n = 30 the count is 3·10^10: out.
Explain: An n-bit number is a subset, bit i saying whether item i is in, so counting from 0 to 2^n − 1 visits
every subset once; 2^n·n (n!·n for orders) against the budget says whether it fits.
Try: predict: the orders `next_permutation` visits from 3 1 2, then run it (2, not 6); fix: `if (m & 1 << i
== 0)`, which never fires in C++ (right in Python), naming the operators that bind looser than `==`.
### 3
Need: I subtract the corners and multiply; why is my overlap area positive for rectangles that do not touch?
Show: width = least right end − greatest left end, height likewise: (0,0)-(2,2) against (5,5)-(7,7) gives
area 9, from −3 × −3; side by side, (5,0)-(7,2), −6. With `max(0, ·)` per axis: 0 and 0.
Explain: An axis "overlap" below zero is a gap; two gaps multiply to a positive area, so clamp each axis first.
Try: predict: the overlap of (0,0)-(4,4) and (4,0)-(6,4), then run it; build: Palindrome Reorder with a counting
array of 26 (accepted).
### 4
Need: Stick Lengths wants every stick one length at least cost; isn't the best length the average?
Show: target = rounded mean, stressed against trying every target: [6, 9, 1]: the mean, 5, costs 9; the best,
6, the middle of the sorted list, costs 8.
Explain: Raising the target by one costs one per stick below and saves one per stick above; it pays until as many
are below as above.
Try: build: Distinct Numbers by sorting, then counting changes between neighbours (accepted); apply: compress
values up to 10^9 to ranks with sort, `unique`, `lower_bound`.
### 5
Need: A hash set makes Sum of Two Values linear; can a test really make it slow?
Show: 10^5 multiples of 172933 into `unordered_map`: seconds; with a splitmix64 hash seeded at run time:
hundredths. Python: 2·10^4 multiples of 2^61 − 1 into a `set`: seconds; each xored with one random number:
hundredths.
Explain: A fixed, public hash lets a hacker choose keys that share a bucket; a seed drawn at run time takes the
choice away. `map` or sorting avoid hashing.
Try: build: Sum of Two Values with a map from value to index (accepted); fix: the slow `unordered_map` with a
seeded hash, on the same keys.
### 6
Need: I wrote binary search from memory and it hangs on some inputs; which line is wrong?
Show: "last a[i] ≤ x" on [1, 3, 5, 7], x = 5, as `if (a[mid] <= x) lo = mid; else hi = mid - 1;`, mid rounded
down: lo 0 hi 3, lo 1 hi 3, then lo 2 hi 3 mid 2 for ever.
Explain: Keep "lo is no, hi is yes" (first-true), loop while hi − lo > 1: mid lies strictly between, so every
step shrinks the range and the answer is hi.
Try: apply: Counting Haybales as `upper_bound(B) − lower_bound(A)`; positions 1 3 3 3 8 10 give 3 for [3, 3], 4
for [2, 9], 0 for [4, 7]; fix: the hanging search with the template, tested on two elements.
### 7
Need: Factory Machines wants a least time, not an array element; where is the sorted thing to search?
Show: made(T) = Σ T / k_i grows with T: search the first T with made(T) ≥ t. Plausible hi = (t / n) · max k, t / n
rounded down, against trying T = 0, 1, 2, ...: n = 3, t = 1, k = 4 3 1: search 0, brute 1 (one random small test
in six fails). Rounded up, or hi = min k · t (the fastest machine alone), it agreed on 2·10^4 tests.
Explain: Binary search needs a yes/no question that flips once as the candidate grows, and ends proved no and
yes; an unproved end caps the answer silently.
Try: build: Array Division, check "at most k parts of sum ≤ S", both ends justified (accepted); fix: the check's
sum overflowing at k_i = 1, t = 10^9 (stop adding at t).
### 8
Need: Apartments has two nested loops; isn't that O(n²) at n = 2·10^5?
Show: sorted applicants and apartments, a `for` over applicants, an inner `while` moving the apartment pointer,
its moves counted: with 2·10^5 of each, 200000 moves in all.
Explain: The inner pointer never moves back, so it moves at most m times in the whole run; cost is counted over
all iterations together (amortised).
Try: predict: the inner moves when every apartment is too small; build: Ferris Wheel with a pointer at each end
of the sorted weights, saying why pairing the heaviest with the lightest loses nothing.
### 9
Need: My Playlist window is right on the sample; why does it count a window with a song twice?
Show: shrinking with `if (count[s] > 1)`, one step, not `while`; every list of up to four songs checked: [1, 2,
2, 1] gives 3, true 2 ([2, 2] still repeats after one step). `while` agreed on 10^5 random tests.
Explain: Shrink until the window is valid again; each song enters once and leaves once, so the `while` costs 2n
moves in all.
Try: predict: the `if` version on 2 1 1 2, then run; build: Playlist with a map of counts, the window's
invariant written above the loop (accepted).
### 10
Need: Subarray Sums II has negatives, so two pointers fail; how can a map of earlier sums count subarrays?
Show: add count[prefix − x], then store the prefix, forgetting the empty prefix; stressed against all pairs (i, j):
a = [−2], x = −2: map 0, brute 1. Starting the map at {0: 1} fixes it.
Explain: (i, j] sums to x exactly when prefix[j] − prefix[i] = x; the empty prefix, 0, is one of the earlier
ones.
Try: build: Forest Queries with a 2D prefix array shifted by one (accepted); predict: `-7 % 5` in C++ and in
Python, then key Subarray Divisibility by `((s % n) + n) % n`.
### 11
Need: Each of q updates adds v to a range of cells; must I touch every cell of every range?
Show: `d[l] += v; d[r + 1] -= v;`, then one running sum. Plausible `d[r] -= v` against adding cell by cell fails at
once: n = 1, add 2 to [1, 1]: [0] against [2].
Explain: d marks where the value changes, up where a range starts and down just after it ends; one running sum
rebuilds every cell: O(n + q).
Try: build: Restaurant Customers by sorting 2n events (+1 arrive, −1 leave) with a running count (accepted);
explain: why times up to 10^9 rule out an array indexed by time.
### 12
Need: My Movie Festival greedy is plainly right and passes the samples; how can I be sure?
Show: "shortest movie first" against a complete search over every subset (`m >> i & 1`; three movies, times
1..10): (1,5), (4,7), (6,10): the shortest, (4,7), clashes with both: greedy 1, best 2. "Earliest end first"
agreed on 2·10^4 tests.
Explain: Swap a best schedule's first movie for the earliest-ending one: nothing clashes, the count stays. A
stress test breaks a greedy; this exchange argument proves one.
Try: explain: Tasks and Deadlines' exchange argument in four sentences; build: Movie Festival II with a `multiset`
(Python: `sortedcontainers` if the judge has it, else C++), stress-tested first.
### 13
Need: Without a tag on the problem, how do I know which technique it wants?
Show: Missing Coin Sum's rule ("next coin > reachable + 1: answer reachable + 1") unsorted, against every
subset's sum: coins 3 3 1: rule 1, brute 2.
Explain: A technique shows in limits and wording (n ≤ 20, "least x such that", sums over ranges); a rule holds
only under its premise, here sorted coins.
Try: apply: five unseen CSES Sorting and Searching problems, technique named before coding, misses logged;
build: Inverse Inversions, checked by a brute that counts inversions for n ≤ 8.

## Believable numbers
Run here (g++ 13 `-O2`, Python 3.13, a shared two-core machine, November 2026; processor time).
- [1] A tight loop (one addition, one comparison) runs about 10^9 steps a second on a recent laptop (1.6·10^9
  here); a step reading memory at random or taking `%` costs 3 to 10 times more; Python about 2·10^7. CSES
  handbook: "some hundreds of millions of operations in a second" (its n² at n = 10^5: 5.3 s). Budget 10^8
  in C++, 10^7 in Python.
- [1-2] The handbook's table for one second: n ≤ 20 allows 2^n, n ≤ 5000 n², n ≤ 10^6 n log n. With many
  test cases the limits often bound the sum of n over all tests: that sum is the budget (Codeforces 1915F).
- [4] Sorting 10^6 numbers: C++ 0.07 s, Python 0.2 s.

## Go deep, leave for later
- Deep steps: 1, 7, 12 (reading limits into a target complexity; binary search on the answer;
  proving a greedy and breaking a wrong one).
- Later: monotonic stacks, sliding-window minimum, range trees (advanced-data-structures); ternary search.

## Never omit
- Each technique starts from the brute force it improves.
- Edge cases: one element, all equal, negatives, largest values.

## Wrong beliefs
- [1] "About 10^9 operations a second, so n² at n = 10^5 passes" (that is 10^10; budget 10^8 in C++, 10^7 in
  CPython).
- [2] "Exponential search is always too slow" (with n near 20 it is often what is intended: 2^20 ≈ 10^6).
- [2] "`next_permutation` lists every permutation" (only those after the current order: sort first).
- [2] "Bit operators bind looser than comparisons" (in C++ only `&`, `^`, `|` do: `6 & 1 == 0` is
  `6 & (1 == 0)`, 0; `<<` and `>>` bind tighter, `1 << 3 == 8` is 1, and looser than `+` and `-`, `1 << n - 1`
  is `1 << (n - 1)`; in Python every bitwise operator binds tighter than a comparison: `6 & 1 == 0` is True).
- [6-7] "Binary search needs a sorted array" (it needs a monotone yes/no question, perhaps about the answer).
- [12] "A greedy that passes the samples is correct" (it needs a proof; a stress test only finds counterexamples).
- [8-9] "Two pointers works on any array" (only if shrinking a valid window keeps it valid; negatives break sums).
- [8] "Two nested loops mean O(n²)" (not if the inner pointer never moves back: at most 2n moves in all).
- [10] "Prefix sums answer any range question" (only ones that can be undone, like sum or xor, on a fixed array).

## Failures to diagnose
- [6-7] A binary search looping forever: `lo = mid` with the midpoint rounded down.
- [7] Wrong answer on a tiny test: an upper end below the answer (Factory Machines: t / n rounded down).
- [7] Wrong answer on big tests: the check's sum overflows even `long long` (Factory Machines: stop at t;
  Python does not overflow but slows).
- [12] A greedy wrong on hidden tests: unproved; a stress test finds the counterexample.
- [10] Off by one in every range sum: prefix array not shifted by one.
- [5] Time limit on one hidden test: `unordered_map` or a Python `set` or `dict` against crafted keys.
- [1] Time limit with 10^4 small tests: each clears a whole array of 2·10^5 (C++ tenths of a second,
  Python over one, before any work); clear only n.
- [1] Maximum Subarray Sum wrong exactly when every value is negative: `best` started at 0, or the running sum
  clamped to 0 before `best` reads it, lets the empty subarray win; resetting a negative running sum to 0
  before adding x is right, with `best` started at the first value.
- [2] `m & 1 == 0` is `m & (1 == 0)` in C++, always 0: parenthesise `&`, `^`, `|` inside a comparison (`-Wall`
  warns "suggest parentheses").

## Practice and project
Per technique: the chapter's CSES problems, then about ten Codeforces problems by tag, from your rating to 300
above (800 if unrated). Stuck: read the editorial a step at a time, then code it closed.
Project: a notebook page per technique (template, proof sketch, bugs) and the error log.

## Mastery ladder
- Use: the chapter's CSES problems accepted.
- Explain: argue a greedy or two-pointer solution correct, or break it with a counterexample.
- Build: solve four of five unseen, untagged Codeforces problems rated 1200 to 1400, about 45 minutes each.
- Design: from limits alone, name two techniques for a new problem and defend one.

## Words to own
[1] brute force, complexity, operation budget; [2] complete search, bitmask, (permutation); [3] counting array,
off-by-one; [4] coordinate compression; [5] hash collision; [6] invariant, monotone predicate; [7] binary search
on the answer; [8] two pointers, amortised; [9] sliding window; [10] prefix sum; [11] difference array, sweep
line; [12] greedy, exchange argument, counterexample, (complete search); [13] upsolving
