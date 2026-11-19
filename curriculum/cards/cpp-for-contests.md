# cpp-for-contests: C++ as a tool for contests and problem solving
kind: language
aliases: c++ for competitive programming, contest c++, stl for contests
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: usaco.guide/general (I/O, debugging, stress tests, data structures); CSES handbook ch. 1-4;
  cses.fi/problemset tasks (limits, flush rule); cppreference Compare; codeforces.com/blog/entry/62393
  (anti-hash); codeforces.com/blog/entry/4088 (rules: the verdict names the first failing pretest);
  codeforces.com/blog/entry/137878 (users' reports: what is shown of a failed test differs by judge and by
  mode); g++ 13 here (traps; every Show and Believable number rerun 2026-11-19)
unverified: order and counts are judgement; what a judge runs and shows after a failing test is looked up per
  judge and contest mode, never taught as fact

## Promise
Read a problem's limits, solve it in C++ with the standard library, test it yourself (edge cases, a
stress test) and get it accepted, knowing what each verdict means.

## The one idea
The judge is a silent examiner (hidden tests, hard limits, one word back), so build your own: a slow sure
solution plus random tests. Picture: an exam marked pass or fail. Where it breaks: the verdict does name the
kind of failure.

## In production
- Contests: one file from a personal template, warnings and sanitizers on. Interviews reward the same habits;
  macros and `bits/stdc++.h` stay out of work code.
- Look up per judge: compiler, flags, stack and memory limits, AI rules, and what is run and shown after a
  failing test (it differs by judge and by contest mode).

## Teaching order
1. The judge loop: CSES Maximum Subarray Sum compiled with `g++ -O2 -Wall -Wextra`, run on a file, compared
   with `diff`, submitted; wrong answer, time limit, runtime error and compile error each caused on purpose; a
   verdict names a failing test and its kind.
2. Limits to types: Weird Algorithm's values pass 5·10^10, Missing Number's sum 2·10^10, Number Spiral's
   answers 10^18; answers modulo 10^9+7, reduced after each step.
3. Input and output: untied streams, `'\n'` not `endl`, state cleared between test cases; decimals by
   `fixed << setprecision(k)`; flushing: CSES Hidden Integer (interactive).
4. `vector`, `string`, `pair`, global arrays; `stack`, `queue`, `deque` (BFS and windows use them later);
   references against copies; Repetitions, Increasing Array.
5. Sorting: `sort` with a lambda, several keys, strict weak ordering; `unique`; Nested Ranges Check.
6. `set`, `multiset`, `map`: iterators, `lower_bound`, erasing one copy; CSES Concert Tickets.
7. `priority_queue` and `unordered_map`: a heap for "next smallest"; a hash map is O(1) only on average
   (defences against crafted keys: dsa-core-techniques 5); Room Allocation.
8. Debugging: `-fsanitize=address,undefined` and its report read, `-D_GLIBCXX_DEBUG`, `assert`, `cerr`; stack
   and memory in bytes.
9. Stress testing: a brute force (the slow, sure solution), generator, compare loop, shrinking; Coin Piles's
   formula against a search.
10. A personal template; others' accepted CSES code (open once you solve) read for what to borrow.

## How it runs
- [2] `int` is 32 bits on usual judges: 2·10^9 fits, 2^31 = 2,147,483,648 does not. `int a = 123456789;
  long long b = a * a;` prints `-1757895751` (made in `int`); write `1LL * a * a`, and `1LL << 40`.
- [2] `long long` holds up to 2^63 − 1 ≈ 9.22·10^18. Coordinates up to 10^9 in absolute value: a difference
  reaches 2·10^9 (past `int`), a squared distance dx² + dy² 8·10^18 (fits, 1.2·10^18 to spare; one more such
  term would not). Doubling 1: 62 doublings fit (2^62), the 63rd overflows.
- [4] `v.size() - 1` on an empty vector is 18446744073709551615; `-1 < v.size()` is false. Write `(int)v.size()`.
- [4] `void f(vector<int> v)` copies n elements per call, `const vector<int>& v` none. `s = s + c` copies s.
- [4] A `vector` is one block: `v[i]` O(1); `push_back` amortised O(1) (a full block is copied to a larger
  one); front insert or erase O(n).
- [6] `set`, `map`, `multiset` are balanced trees: O(log n) each. `std::lower_bound(s.begin(), s.end(),
  x)` on a set walks linearly; `s.lower_bound(x)` does not. `ms.erase(x)` removes every copy,
  `ms.erase(ms.find(x))` one. `if (m[k] == 0)` inserts k; `m.count(k)` does not.
- [6,8] After `s.erase(it)` the loop's `++it` is undefined: write `it = s.erase(it)`. `push_back` may move the
  block, leaving an earlier `int& r = v[0]` dangling.
- [7] `priority_queue<int>` is a heap in a vector: `top()` the largest in O(1), push and pop O(log n), no
  middle erase; `priority_queue<int, vector<int>, greater<int>>` tops with the smallest.
- [8] `vector<int> a(n); a[n] = 0;` at `-O2` printed the right sum for n = 1000 and aborted inside `malloc`
  for n = 10; `-fsanitize=address` reports `heap-buffer-overflow` for both. A local `int a[1000000]` can
  overflow the stack; a global one does not.

## Step notes
### 1
Need: My program prints the sample's answer; why "wrong answer on test 2", and what about the tests after it?
Show: the linear scan for Maximum Subarray Sum (sums in `long long`: step 2), `best` started at 0. Sample in
`1.in`, answer in `1.ans`; `3` / `-5 -2 -8` in `2.in`, `-2` in `2.ans`. `g++ -O2 -Wall -Wextra s.cpp -o s`,
`./s < 1.in > 1.out`, `diff 1.out 1.ans`: silent, the same. On `2.in`: `< 0`, `> -2`. `best` from the first
value: both silent; submitted: accepted.
Explain: A verdict names a failing test and how it failed, never why: the count (dsa-core-techniques 1), the
type (step 2) or a `diff` on your own file finds why. Whether later tests ran or are shown differs by judge and
mode: look yours up.
Try: predict: the verdicts of every start and end and of a local `long long a[1000]`, then submit both; fix:
`cin >> a` on a `vector` (hundreds of lines from g++) from its first `error:` line alone.
### 2
Need: n ≤ 10^6 fits in `int` and my Weird Algorithm passes 999999, the biggest test; why wrong answer?
Show: steps and largest value, `int n` against `long long n`, `-O2`: 999999 agrees (258 steps); 704511 gives
211 steps against 242, largest value 56991483520. No crash, no warning; 432 inputs up to 10^6 pass 2^31 − 1.
Step 1's scan with `int` sums: the same bug (on `seq 200000` it printed 2147474694 here, not 20000100000).
Explain: The type must hold the largest value reached, not the input; signed overflow is undefined, so the run
carries on with garbage and looks normal.
Try: predict: Missing Number's 1 + ... + n at n = 2·10^5 in `int`, then fix with `1LL *`; decide: each value's
type in Number Spiral at y = x = 10^9, and where a product modulo 10^9+7 is reduced.
### 3
Need: My algorithm is linear and I added `sync_with_stdio(false)` as the blogs say; why is reading and
printing 10^6 numbers still slow?
Show: read 10^6 numbers, print each doubled, to a file: defaults about 0.6 s; `sync_with_stdio(false)` alone
about half that; plus `cin.tie(nullptr)` about 0.1 s; untied with `endl` 0.4 s again. A laptop gives other
seconds, the same ratios.
Explain: A tied `cin` flushes `cout` before each read, `endl` after each line; each flush is a call into the
operating system. An interactive judge needs exactly that flush, once per question.
Try: fix: a CSES Hidden Integer client that hangs for want of a flush (accepted); fix: a second test case wrong
because a global count was not cleared.
### 4
Need: My solution is O(n); why the time limit since I moved the check into a helper function?
Show: `long long at(vector<long long> v, int i)` called 10^4 times on 2·10^5 elements: over a second on any
machine (2·10^9 elements, 16 GB, copied); with `const vector<long long>& v`: milliseconds. Same answer.
Explain: Without `&` each call copies every element (here 2·10^9 copies); a reference passes only the address.
Try: predict: `v.size() - 1` for an empty `v`, and whether `for (int i = 0; i < v.size() - 1; i++)` runs, then
run it; fix: an Increasing Array helper that copies the vector (under 0.1 s at n = 2·10^5).
### 5
Need: My comparator sorts by value and ties do not matter; why does `sort` crash or invent numbers?
Show: `vector<int> a(n, 7)` sorted with `return x <= y;`: n = 16 fine; n = 17 starts with 0, a seven lost
(n = 10^5: two lost; g++'s library, others fail differently). `-fsanitize=address`: heap-buffer-overflow in
`std::__introsort_loop`; `-D_GLIBCXX_DEBUG`: "comparison doesn't meet irreflexive requirements".
Explain: `sort` trusts `comp(x, x)` to be false and, above 16 elements here, loops with no bounds check until the
comparator says stop; `<=` never does on equal items.
Try: build: Nested Ranges Check's order, run under `-D_GLIBCXX_DEBUG` (accepted); fix: a two-key comparator with
`<=` on the second key.
### 6
Need: A `set` is O(log n); why does `lower_bound` on mine take seconds?
Show: a `set<int>` of 2·10^5: 2,000 calls of `std::lower_bound(s.begin(), s.end(), x)` take seconds (about
2·10^8 node steps); 2·10^5 of `s.lower_bound(x)`, building included, a tenth of a second. Same answers.
Explain: A set's iterator steps one node at a time, so `std::lower_bound` walks; the member function goes down the
tree in O(log n).
Try: predict: {5, 5, 5, 8} after `ms.erase(5)`, and after `ms.erase(ms.find(5))`, then run; build: Concert
Tickets with a `multiset`, `upper_bound` then one step back (accepted).
### 7
Need: `unordered_map` is O(1); why did my hash solution get hacked?
Show: 10^5 keys, multiples of 172933 (a bucket count of this library): `unordered_map` seconds (5·10^9 key
comparisons), `map` hundredths; keys 1 to 10^5: hundredths. `bucket_size(0)` is 100000. (g++ 13 here; bucket
counts vary by version.)
Explain: A key goes to bucket hash mod bucket count, and `std::hash` of an integer is the integer, so multiples
share one bucket and each insert scans every earlier key.
Try: build: Room Allocation with a `priority_queue` of (leaving day, room) under `greater` (accepted); decide: for
an open-hacking round, `map`, a seeded hash (dsa-core-techniques 5) or sorting.
### 8
Need: `-fsanitize=address,undefined` was silent; is my indexing safe?
Show: `v.reserve(100); v.push_back(1); v[5] = 42;` prints "size 1, v[5] = 42" with or without the sanitizers;
`-D_GLIBCXX_DEBUG` stops: "out-of-bounds index 5, but container only holds 1 elements". Without `reserve` the
sanitizer reports "heap-buffer-overflow ... WRITE of size 4" and the line.
Explain: The sanitizer guards memory the program does not own; spare capacity is owned, so only debug mode,
checking each `[]` against `size()`, sees it.
Try: fix: a solution with runtime error on the judge only: make it fail here under both checks, read the line
naming your file; explain: why `a[n] = 0` gave a right sum at n = 1000.
### 9
Need: My Coin Piles formula passes the samples and my hand cases; how do I find the input that breaks it first?
Show: plausible `(a + b) % 3 == 0`; a brute force trying both moves recursively; a generator (Python
`random.seed(s)`, two `randint(0, 10)`); a compare loop. Seed 3 fails: "3 9", formula YES, brute NO (16 of the
121 pairs fail). Shrunk by hand: "0 3".
Explain: The brute force is too slow but plainly right; small random tests try cases you never thought of, and
the first disagreement is small enough to trace.
Try: build: a stress loop for your own CSES solution, printing the failing test; apply: plant an off-by-one in an
accepted solution and count the tests the loop needs.
### 10
Need: Do I need a long template like top coders, and why does mine compile slowly?
Show: a ten-line solution with `bits/stdc++.h` builds in about a second (`-O2 -Wall -Wextra`), with
`<iostream>` a few tenths; precompiled (`g++ -x c++-header` into a `bits/` folder on `-I`) a few tenths, but
`g++ -H` marks it `x`, unused, once the flags differ (add `-fsanitize`).
Explain: Everything the template includes is compiled every time; a precompiled header serves only its own flags.
Try: build: a template under 30 lines you can explain, with a `-DLOCAL` `cerr` macro; decide: from two accepted
solutions by others, one habit to borrow and one to refuse, with the reason.

## Believable numbers
Run here (g++ 13 `-O2`, a shared two-core virtual machine, November 2026; processor time). A recent laptop is
about as fast or a few times faster, a judge often slower: trust the powers of ten and the ratios.
- [3] Reading 10^6 numbers with `cin`: a quarter second synced, a few hundredths untied; 10^7 untied about
  half a second, so 10^8 never fits in one second.
- [3] 10^6 lines written to a file: `'\n'` a few hundredths of a second, `endl` ten times that.
- [6-7] 10^6 random keys inserted, then 10^6 lookups: `map` about 2 s, `unordered_map` and a sorted `vector`
  (`sort`, `unique`, `binary_search`) a few tenths: each tree step is a pointer to memory not in cache.
- [5] `sort` of 10^6 `int`: under a tenth of a second.
- [7] 10^5 crafted keys: `unordered_map` seconds, with a seeded splitmix64 hash hundredths.
- [10] Building one solution with `bits/stdc++.h`: about a second, the sanitizers adding a little.

## Go deep, leave for later
- Deep steps: 2, 8, 9 (overflow, undefined behaviour and stress tests are where a program that works here
  fails on the judge, and where a contestant learns to find out why).
- Later: `pb_ds` trees, `bitset` tricks.

## Never omit
- A real judge in every chapter; limits before code; a brute force kept for stress tests.

## Wrong beliefs
- [2] "`int` is fine when every input fits" (sums and products need not: Missing Number).
- [1] "Wrong answer on test 3 means tests 4 onwards passed" (the verdict says nothing about them: whether they
  ran, and whether their results are shown, differs by judge and contest mode).
- [3] "`endl` is just a newline" (it also flushes: slow over 10^5 lines).
- [7] "`unordered_map` is always faster than `map`" (on average only; crafted tests make it slow).
- [5] "A comparator may return `a <= b`" (it must be false for equal items, or `sort` can crash).
- [8] "Undefined behaviour always crashes" (it can pass locally and fail on the judge).
- [9] "A stress test needs big random tests" (values up to 10 broke Coin Piles's formula at the third test and left
  a case small enough to trace).
- [8] "With the sanitizers on, every bad index is caught" (not one inside a `vector`'s spare capacity: after
  `reserve(100)`, `v[5]` on a one-element vector runs silently under `-fsanitize=address`; `-D_GLIBCXX_DEBUG`
  stops it).

## Failures to diagnose
- [2] Wrong answer on big tests only: `int` overflow.
- [3,4] Time limit, right algorithm: `endl` on big output, or a vector passed by value.
- [3] Second test case wrong: state not cleared. Interactive run hangs: no flush.
- [8] Runtime error on the judge only: an index out of range, named by `-fsanitize=address`.
- [8] Runtime error on a long path: recursion deeper than the stack.

## Practice and project
Guided: the chapter's CSES problems, then two unseen. Project: a template and stress harness that finds
three planted bugs (overflow, off-by-one, uncleared state) and prints the smallest failing input.

## Mastery ladder
- Use: ten CSES Introductory problems accepted, each tested locally first.
- Explain: from a verdict and the limits, name a failed submission's cause and show it.
- Build: the template and stress harness.
- Design: pick types and containers for a new problem from its limits; defend them.

## Words to own
[1] verdict, time limit exceeded, runtime error; [2] constraints, overflow, modulo;
[3] flush, interactive problem; [4] reference, unsigned; [5] comparator, strict weak ordering; [6] multiset,
iterator; [7] heap, hash table; [8] sanitizer, undefined behaviour, stack overflow; [9] stress test; [10] template
