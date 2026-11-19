# string-algorithms: matching and comparing strings for contest problems
kind: skill
aliases: string hashing, kmp, prefix function, z-function, suffix array, trie, manacher
needs: dsa-core-techniques, recursion-and-dynamic-programming, advanced-data-structures
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/book/book.pdf ch. 26 (trie, hashing, Z); cses.fi/problemset String Algorithms (names, task
  pages); usaco.guide/gold/hashing, /adv (string searching, suffix array); codeforces.com/blog/entry/60442
  (dacin21: n/p bound, Thue-Morse against 2^64, 2^61−1, pairs of primes); codeforces.com problems 126B, 1200E;
  atcoder.jp/contests/practice2/tasks/practice2_i; cp-algorithms.com string contents (outline); runs with g++ in
  /tmp (Thue-Morse at 512, 1024, 2048; birthday count; letters from 0); g++ 13 and Python 3.13 runs,
  2026-11-19 (step notes, numbers; rerun independently, reviews/VA.md)
unverified: step order past 9 and practice counts are judgement

## Promise
Match, compare and count substrings in near-linear time: hashing that survives hacks, prefix and Z-functions,
tries, palindromes, and suffix arrays with LCP.

## The one idea
Never compare the same characters twice: what one comparison learned (a border, a match length, a hash) is
reused by the next. Picture: when a search word half matches, you slide it to its next possible start. Where it
breaks: hashing reuses a fingerprint, not the characters, so equal hashes only probably mean equal strings.

## In production
- Contests: a string task is often one of these tools plus binary search or DP.
- Codeforces hacks: weak hash parameters are attacked; the risk decides the method.
- Work: the same collision arithmetic applies to any content hash.
- A skill book whose programs run: plan `run: cpp`.

## Teaching order
1. Polynomial hashing: prefix hashes and powers, any substring in O(1); CSES String Matching.
2. Hashing safely: a base drawn at run time, modulus 2^61−1 (`__int128` product) or two primes near 10^9;
   Thue-Morse strings against the free 2^64 overflow; the birthday bound (m²/2p expected collisions).
3. Hash plus binary search on length (a repeat of length L implies one of L−1; dsa-core-techniques 7); the
   longest common prefix of two substrings by the same search; Repeating Substring.
4. Prefix function: amortised O(n), KMP on `pattern + '#' + text`; Codeforces 126B Password, 1200E Compress Words.
5. Borders and periods: the π chain lists every border; border b gives period n−b; Finding Borders, Finding Periods.
6. Z-function: the matched box [l, r), O(n); String Functions (π and Z of one string).
7. KMP automaton with DP over matched length (recursion-and-dynamic-programming 5): Required Substring.
8. Trie: nodes at most total length plus one; Word Combinations (trie plus DP over positions).
9. Palindromes: Manacher with odd and even centres, O(n); Longest Palindrome, All Palindromes; forward and
   backward hashes in a Fenwick tree (advanced-data-structures 4): Palindrome Queries.
10. Suffix array: doubling over cyclic shifts with `$` appended, O(n log n) with counting sort; pattern search by
   binary search: Finding Patterns, Counting Patterns; Minimal Rotation (shifts of s itself).
11. LCP array by Kasai, O(n); distinct substrings n(n+1)/2 − ΣLCP: Distinct Substrings, AtCoder practice2 I;
   sparse table over LCP (advanced-data-structures 3) for any two suffixes; Substring Order I.

## Judged by
- [2] Is the base random at run time, the modulus 2^61−1 or a pair, and the comparison count under the birthday bound?
- [2] In a round with hacks, is an exact method used where one exists?
- Are substring bounds half-open, and tested at length 1 and the full string?
- Is it stress-tested against naive matching on random strings over two letters, where borders are dense?
- [8] Do trie nodes × alphabet × 4 bytes fit the memory limit?

## Step notes
### 1
Need: `string::find` is in the library and fast; why would String Matching need a hash?
Show: count occurrences by repeated `find`, n = 10^6. Random two-letter text: `find` under 0.01 s, prefix
hashes mod 2^61−1 a few hundredths. Text a^(10^6), pattern a^(5·10^5): `find` about 6 s on a laptop or a judge
(5·10^5 starts, each comparing 5·10^5 letters: 2.5·10^11, even at 4·10^10 a second), hashing still hundredths;
both count 500,001.
Explain: With prefix hashes, any substring's hash is h[r] − h[l]·B^(r−l): one O(1) comparison instead of up to
m letters; equal hashes then mean probably equal strings.
Try: predict: `find`'s time on the a^n test at n = 2·10^5, then run; fix: a hash set of all substrings with
letters mapped from 0 (failure [1]), until it agrees with a `set<string>`.
### 2
Need: My hash with unsigned overflow and base 131 passed every test; how did it get hacked?
Show: a Thue-Morse string of length 1024 and its complement, unsigned 64-bit: equal for 1000 of 1000 random odd
bases (about a quarter at length 512); mod 2^61−1, random base: 0 of 1000. Birthday: 300,000 random strings mod
10^9+7, four runs: 37 to 55 colliding pairs; m²/2p predicts 45.
Explain: The two hashes differ by a product of ten factors B^(2^i) − 1, together divisible by 2^64 for every
odd B. Mod a prime one fixed pair collides with chance at most n/p, but m hashes make m²/2 pairs.
Try: predict: colliding pairs for 10^6 hashes mod 10^9+7, then with two primes (500; 5·10^−7); build: a hash,
base from the clock, mod 2^61−1 by `__int128`, surviving their own Thue-Morse test.
### 3
Need: My Repeating Substring with hash and binary search passes small tests; why does it answer 70,000?
Show: a random 26-letter string, n = 10^5, true answer 6 (by sorting suffixes). One hash mod 10^9+7 in a set,
eight random bases: 37,059 to 73,680, every one in the tens of thousands. Mod 2^61−1: 6 each time.
Explain: Each check puts 10^5 hashes in one set, about n²/2p = 5 false pairs, so every length seems to repeat
and the search climbs. The search itself is sound: a repeat of length L contains one of L−1.
Try: predict: the same at n = 2·10^4 (0.2 false pairs a check), then run with six bases (here 6, 39, 82, 1250,
1406, 3984 for a true 6: sometimes right, never trustworthy); apply: the longest common prefix of two substrings
by the same search, against a loop on random strings.
### 4
Need: One character can fall back through π many times; why is the prefix function still linear?
Show: count the falls (`j = pi[j-1]`) at n = 10^6: a^(n−1)b, 999,998, all at its last letter; "a b aa b aaa
b …", 997,175; random over a, b, about a third of n; a Fibonacci string, 26. Never above n.
Explain: π rises by at most 1 per character and every fall lowers it by at least 1, so all falls together are
at most n, however many land on one character.
Try: build: KMP on `pattern + '#' + text` for String Matching, against `find`'s count on random two-letter
strings; fix: a separator the text can contain (failure [4]): pattern "a" in "a#a" counts 1, not 2.
### 5
Need: Finding Periods: are the periods just the multiples of the shortest one?
Show: over all a/b strings, shortest first, "multiples of the shortest period, plus n" first fails on "aabaa":
periods 3, 4, 5, the multiples 3, 5. Its π chain gives borders 2, 1, so periods 3, 4, 5; the chain matched
brute force on every string up to length 8.
Explain: p is a period exactly when the prefix of length n−p is also a suffix, a border; the borders are
π[n−1], then π of that, down to 0.
Try: predict: the periods of "abacaba" from its borders (4, 6, 7), then print; build: Finding Borders and
Finding Periods, against brute force on every string up to length 10.
### 6
Need: My Z-function passes the stress test; can it still time out?
Show: a Z that moves the box at every i (l = i, r = i + z[i]), not only when r grows: equal to naive Z on
10^5 random strings, fast on random text and on a^n, but 2.5·10^9 comparisons on abab… at n = 10^5: seconds,
where the box shrinks after every odd i. The right box: under 2n comparisons on all three.
Explain: [l, r) is the match reaching furthest right; inside it z[i] starts free at min(r − i, z[i − l]), and
only pushing r right costs comparisons, so the total is O(n).
Try: predict: naive Z's comparisons on a^n at n = 10^5 (5·10^9), then run; build: String Functions, π and Z
checked against each other (a border of length k exists exactly when z[n−k] = k).
### 7
Need: Required Substring: when the next letter breaks a partial match, can I restart at state 0?
Show: over {a, b}, DP on matched length against brute force. Restart (state 1 if the letter starts the
pattern, else 0) is right for "ab", "aba", "abb", "abab"; for "aab" at n = 4: 3 against 4 (it misses "aaab");
at n = 10: 583 against 792. The KMP automaton: right on all.
Explain: After a mismatch, the longest text suffix still a prefix of the pattern is a border, so the next state
is go(π[j−1], c): an m × 26 table built once, then DP over (length, state).
Try: predict: restart's count for "abaa" at n = 10 (334 against 393); build: Required Substring (n ≤ 1000,
m ≤ 100), accepted.
### 8
Need: Word Combinations has 10^5 dictionary words; how do I find the words starting at each position in time?
Show: a 5000-letter text over a, b and 10^5 random words of length 5 to 20: every word at every position is
5·10^8 checks, over a second; trie walks from each position: about 8·10^4 steps in all, same count. Random words
of total length 10^6: 739,355 nodes, 77 MB as `int[26]`.
Explain: Words sharing a prefix share a path, so one walk from position i reads the text once and meets every
word starting there; nodes are at most total length plus one.
Try: decide: 10^6 nodes of `int[26]` against a 256 MB limit, and the remedy (failure [8]); build: Word
Combinations, trie plus DP over positions, accepted.
### 9
Need: A palindrome of length L contains one of length L−2; can I binary-search its length as in step 3?
Show: brute force over all a/b strings, shortest first: binary search over all lengths first fails on "aba"
(it tests 2, finds none, answers 1); Manacher with odd centres only first fails on "aa" (answers 1).
Explain: Trimming both ends keeps a palindrome, so lengths are monotone only within one parity. Manacher keeps
the palindrome reaching furthest right and starts each centre from its mirror, like the Z box.
Try: fix: the binary search, odd and even lengths apart, against brute force; build: Longest Palindrome with
Manacher on both centres, accepted.
### 10
Need: Sorting suffixes with `std::sort` and a string comparison passes random tests; is that n log n?
Show: suffixes as `string_view`, `std::sort`: n = 10^5, random hundredths, a^n and (ab)^(n/2) one to two
seconds; n = 3·10^5, random still hundredths, a^n about 15 s (n log n comparisons, each reading up to n
letters). Doubling with counting sort on a^n at 3·10^5: hundredths.
Explain: Random suffixes differ within a few letters, but on a^n one comparison reads up to n. Doubling sorts
by the first 2^k letters as pairs of ranks from the round before: O(n) a round, log n rounds.
Try: predict: the comparator sort on a^n at 2·10^5, then run; fix: doubling without `$` (failure [10]): on
"baa" it prints 1 2 0 (cyclic shifts aab, aba, baa), the suffix order is 2 1 0; done when they agree.
### 11
Need: The LCP array is only n−1 numbers; what can it answer, and why is Kasai linear?
Show: "abab": sorted suffixes ab, abab, b, bab; LCP 2 0 1; distinct substrings 10 − 3 = 7, as a brute-force set
says (and on 20,000 random strings). Random 26 letters, n = 10^5: about 5·10^9 distinct (4,999,757,432 on one
string); in `int` it printed 704,790,136, positive and plausible.
Explain: Each suffix adds its prefixes not shared with its sorted predecessor. Kasai takes suffixes in text
order, and the match drops by at most 1 from one to the next, so total work is O(n).
Try: build: Distinct Substrings and practice2 I in `long long`, against the set; apply: the LCP of any two
suffixes as a minimum over their ranks by a sparse table, then Substring Order I.

## Believable numbers
- Run here (g++ -O2, Python 3.13, shared two-core machine, November 2026; a laptop or judge is the same order):
  hashing 10^6 letters mod 2^61−1, or their prefix function, hundredths of a second in C++; the prefix
  function of 10^6 letters under a second in Python.
- [1,10] Library comparisons read about 4·10^10 letters a second here (`find`: 2.5·10^11 in 6 s), so quadratic
  work on a^n hides at n = 10^5 (`find` 0.05 s, a suffix sort 1.3 s) and shows by 3·10^5 to 10^6 (15 s, 6 s).
- [2-3] Collisions: m hashes in one set mod p give about m²/2p pairs; 10^5 mod 10^9+7, about 5.
- [8,11] Memory: trie nodes × alphabet × 4 bytes; counts of substrings reach n²/2, past `int` at n = 10^5.

## Go deep, leave for later
- Deep steps: 2, 4, 5, 11 (what makes a hash safe; why π is linear; borders and periods; what the LCP array
  answers: where tools stop being copied and start being adapted).
- Later: Aho-Corasick (Pattern Positions), suffix automaton (Substring Order II, Substring Distribution),
  palindromic tree, Lyndon words and Booth's algorithm, Burrows-Wheeler (String Transform), repetitions by
  Main-Lorentz, suffix trees; a trie over the bits of numbers (CSES Maximum Xor Subarray).

## Never omit
- Every fast method keeps a naive version beside it for stress tests.

## Wrong beliefs
- [1] "Equal hashes mean equal strings" (only probably; a collision is a wrong answer).
- [2] "A random base mod 10^9+7 is safe" (one comparison fails with chance at most n/p; m hashes in one set give
  about m²/2p collisions: run, 300,000 random strings, 37 to 55 colliding pairs in four runs, 45 expected).
- [2] "Unsigned overflow is a free 2^64 modulus" (a Thue-Morse string of length 1024 and its complement collide
  for every odd base: run, 1000 of 1000; an even base forgets all but the last 64 characters).
- [4] "Computing π is quadratic" (π rises by at most 1 per character, so all the falls total at most n).
- [5] "A period must divide the length" (abcab has period 3; only a full repetition needs it).
- [9] "Palindrome length can be binary-searched like a repeat" (only within one parity: run, "aba").
- [10] "`sort` on suffix strings is n log n" (a comparison can cost n; aaaa…a makes it quadratic times log n).
- [11] "Kasai re-matches each suffix from scratch" (the match drops by at most 1 a step: run, 99,974 matching
  steps in all at n = 10^5).

## Failures to diagnose
- [1] Letters mapped from 0: run, "b" and "ab" hash equal; map from 1. It bites when lengths differ in one set:
  "abbaa" has 12 distinct substrings, the set held 7.
- [1] `(h[r] - h[l] * p[r-l]) % M` negative in C++, so equal substrings compare unequal; add M, then reduce.
- [2] The 2^61−1 product in 64 bits: silent overflow. A fixed seed, or `random_device` on MinGW: hackable.
- [3] One hash mod 10^9+7 inside a binary search on n = 10^5: false repeats at every length.
- [4] A separator that can occur in the text.
- [6] The box moved at every i: right answers, quadratic on abab….
- [7] Restarting at state 0 on a mismatch: right for "abab", wrong for "aab".
- [9] Odd centres only: even palindromes missed.
- [10] No `$`: cyclic shifts sorted, not suffixes ("baa": 1 2 0 for 2 1 0).
- [8] A trie of 10^6 nodes × 26 `int`s: about 104 MB.
- [11] Distinct substrings counted in `int`.

## Practice and project
Per step: its CSES problems, then about ten Codeforces problems tagged strings or hashing from your rating to 300
above. Project: a string library (safe hash, π, Z, Manacher, suffix array with LCP); finish line: it gets
String Functions, Distinct Substrings and AtCoder practice2 I accepted, and survives the stress test.

## Mastery ladder
- Use: solve the chapter's CSES problems with a named method.
- Explain: show why π is linear, and compute the collision chance for a stated number of hashes.
- Build: the library and its finish line above.
- Design: for a new problem, choose hashing or an exact method and defend it against hacks and limits.

## Words to own
[1] polynomial hash; [2] birthday paradox, double hashing; [3] longest common prefix; [4] prefix
function, KMP; [5] border, period; [6] Z-function; [7] automaton; [8] trie; [9] palindrome, Manacher; [10] suffix
array, cyclic shift; [11] LCP array, Kasai
