# number-theory-and-combinatorics: number theory and counting modulo a prime, for contests
kind: skill
aliases: contest math, modular arithmetic, combinatorics, number theory
needs: recursion-and-dynamic-programming
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/problemset Mathematics (names; task pages for limits of Exponentiation II, Counting Divisors,
  Moving Robots, Fibonacci Numbers, Throwing Dice, Grundy's Game); cses.fi/book/book.pdf ch. 21-25 (outline:
  totient, matrices, probability, game theory); usaco.guide/gold/modular (Fermat needs a prime), /gold,
  /plat, /adv (outline); atcoder.jp abc326_e, abc340_f (tasks; abc340_f samples); cses.fi task 1081 (Common
  Divisors limits, 2026-11-19); g++ and Python in /tmp (every Show, in reviews/D9.md, rerun in VA.md)
unverified: step order and practice counts and rating bands are judgement; games sit here because Nim and
  Grundy numbers are xor and counting arguments, not DP tables (judgement)

## Promise
Answer "how many" and "what is the expected value" modulo a prime, without overflow, using divisors, primes,
inverses, binomials, inclusion-exclusion and fast powers, each formula checked against brute force; and decide
two-player games by Grundy numbers.

## The one idea
A residue keeps what `+`, `-` and `*` need and forgets the rest. Picture: a clock; 3 hours after 11 is 2.
Where it breaks: division needs an inverse, which exists only for numbers coprime with the modulus, and a
clock cannot say which is bigger.

## In production
- Contests: counts printed modulo a prime the statement names; a probability as `P * Q^-1` modulo it.
- Work: hashing, cryptography. Book programs run: plan `run: cpp`.

## Teaching order
1. Modular arithmetic in C++: reduce after every `+`, `-`, `*`; products of two residues in `long long`; `%` of
   a negative number; fast exponentiation by squaring, O(log e); CSES Exponentiation.
2. Trial division to √n; divisor count Π(e+1); multiples of every d: n/1 + n/2 + ... = O(n log n);
   CSES Counting Divisors, Common Divisors.
3. The sieve of Eratosthenes with smallest prime factors; factorising in O(log x); Counting Divisors, fast.
4. gcd by Euclid, lcm without overflow, extended Euclid: `ax + by = c` is solvable iff gcd(a,b) divides c;
   AtCoder ABC340 F (S = 1: triangle (0,0),(X,Y),(A,B) has area |XB - YA| / 2).
5. Modular inverses: exist iff gcd(a,m) = 1; extended Euclid for any m; Euler's theorem a^φ(m) ≡ 1, φ from
   step 3's factorisation; Fermat's `a^(p-2)` for prime p, a not a multiple of p; exponents mod p-1; CSES
   Exponentiation II.
6. Factorial and inverse-factorial tables in O(n) (one Fermat call, then downward); C(n,k), multinomials in
   O(1) for n < p; CSES Binomial Coefficients, Creating Strings II.
7. Counting models: stars and bars C(n+k-1, k-1), CSES Distributing Apples; Catalan numbers C(2n,n)/(n+1) and
   the reflection argument, Bracket Sequences I and II.
8. Inclusion-exclusion over subsets (one bitmask each, dsa-core-techniques 2), products guarded against
   overflow; derangements, D(n) = (n-1)(D(n-1) + D(n-2)); CSES Prime Multiples, Christmas Party.
9. Expected value by linearity, no independence needed: a count is a sum of indicator probabilities; CSES
   Moving Robots (a decimal); modulo a prime, AtCoder ABC326 E.
10. Matrix exponentiation: a linear recurrence of order d as a d×d matrix, O(d³ log n); CSES Fibonacci Numbers
   (n ≤ 10^18), Throwing Dice (order 6); powers of an adjacency matrix count walks: Graph Paths I.
11. Games: a position is losing iff every move leads to a winning one; Stick Game as a DP table; Nim: lose iff
   the xor is 0, Nim Game I; Grundy number = mex of the moves' values, a sum of games takes the xor; Grundy's
   Game, a pattern found by computing.

## Judged by
- [1] Every subtraction is made non-negative and every product of two residues is formed in 64 bits.
- [5-6] Every division is an inverse whose existence is argued: prime modulus, divisor not a multiple of it.
- [7-9] The formula matches a brute force for every n up to 8 before submitting.
- [9] No residue is compared or maximised: such choices are made on exact values.

## Step notes
### 1
Need: My answer is right on every small n I tried; why does the judge see a negative number?
Show: subsets of n items with at least two, modulo 10^9+7: `(pw(2, n) - n - 1) % MOD` is right for every n
below 56,460; there 2^n mod p is 9,921 and it prints −46,540 (truth 999,953,467); to 10^6, 479 times. The
power: 3^(10^9) by a loop, 10^9 multiplications, seconds on any laptop or judge (each waits for the last,
a few nanoseconds); by squaring, 43.
Explain: A residue has forgotten the size of the number, so subtracting a true value can go below zero, and C++'s
`%` keeps the sign: add MOD first. Squaring halves the exponent each step: about 2 log2 e multiplications.
Try: predict: `(5 - 7) % MOD` in C++ and in Python, then run; build: CSES Exponentiation, the loop version
timed beside it.
### 2
Need: Counting Divisors has 10^5 queries up to 10^6; how many divisors can a number even have?
Show: all divisor counts to 10^6, adding 1 at every multiple of every d: 13,970,034 steps, hundredths of a
second; testing every d ≤ x for every x: 5·10^11. Most divisors: 720720 =
2^4·3^2·5·7·11·13, (4+1)(2+1)(1+1)^4 = 240. Trial division of the prime 999,999,999,989: 999,998 divisions.
Explain: d has n/d multiples, and n/1 + n/2 + ... ≈ n ln n; a divisor d pairs with x/d, so trial division stops
at √x; the count multiplies each prime's choices of exponent.
Try: predict: the loop's steps at 10^7 (162,725,364), then run; decide: √x per query, one table or a sieve
(step 3) for Counting Divisors and Common Divisors (2·10^5 values to 10^6).
### 3
Need: My sieve works to 10^4; why does it crash at 10^6?
Show: the outer loop over every i ≤ n, the inner `for (int j = i * i; j <= n; j += i)`: fine at n = 46,000,
segfault at 46,400, the first prime past 46,340 being 46,349; `-fsanitize=undefined`
says "46349 * 46349 cannot be represented in type 'int'". In `long long`: 78,498 primes to 10^6 in hundredths
of a second, 664,579 to 10^7 in under half a second; with smallest prime factors any x ≤ 10^6 factorises in at
most 19 divisions (2^19).
Explain: p starts at p², since smaller multiples have a smaller factor already; spf[x] is the first prime to
cross x off, and dividing by it at least halves x.
Try: predict: the most divisions for x ≤ 10^7 (23), then run; build: Counting Divisors from spf, timed against
step 2's table.
### 4
Need: ABC340 F wants integers A, B with |XB − YA| = 2; how do I solve an equation in integers?
Show: extended Euclid gives Xx + Yy = g. X = 3, Y = 5: 3·2 + 5·(−1) = 1, so B = 4, A = 2: |12 − 10| = 2. The
third sample has g = 998,244,353, which does not divide 2: −1. And lcm(4·10^9, 6·10^9) as `a * b / g` prints
2,776,627,963; `a / g * b` prints 12,000,000,000.
Explain: gcd(a, b) = gcd(b, a mod b), and each line hands back an (x, y); every aX + bY is a multiple of g, so c
is reachable exactly when g divides it: scale (x, y) by c/g.
Try: predict: Euclid's steps on consecutive Fibonacci numbers below 10^18 (85), then count; fix: an lcm of
2·10^5 numbers that overflows (belief [4]), the answer checked with `__int128`.
### 5
Need: Everyone divides with `pw(a, MOD - 2)`; when does that print a wrong number?
Show: modulo 10, `pw(3, 8)` = 1, but 3·1 = 3; the inverse is 7 (extended Euclid; Python `pow(3, -1, 10)`).
Modulo 7, `pw(14, 5)` = 0. Exponentiation II, 3^(b^c), b = 10^9, c = 2: exponent reduced mod p, 236,701,429;
mod p−1, 246,336,683, as Python's `pow(3, 10**18, p)` confirms.
Explain: For prime p and a not a multiple of p, a^(p−1) ≡ 1, so a^(p−2) inverts a and exponents repeat every
p−1; Euler: the same with φ(m) when gcd(a, m) = 1. Outside that, no inverse is promised.
Try: predict: 3^4 and 2^4 modulo 10 (φ(10) = 4) and why only one is 1; fix: Exponentiation II reduced by p
(failure [5]) until it matches Python's `pow` on random small cases.
### 6
Need: Binomial Coefficients has 10^5 queries with n up to 10^6; can I compute each C(n, k) fresh?
Show: Python's exact `math.comb(10**6, 5*10**5)`: a million bits, seconds, for one query. Tables of n! and
1/n! to 10^6, one Fermat call then downward: a quarter second in Python, hundredths in C++; C(10^6, 5·10^5) =
996,692,777, the exact number mod p. Modulo 7, C(8,1) by factorials gives 0; the truth is 1.
Explain: 1/(i−1)! = i · 1/i!, so one inverse feeds all; C(n, k) = n!/(k!(n−k)!) holds only while n < p, since
past it n! ≡ 0 (Lucas).
Try: build: Creating Strings II from the tables, checked against `itertools.permutations` on 8 letters;
predict: the time of 10^6 separate Fermat calls instead, then run (over a second in Python).
### 7
Need: Distributing Apples and Bracket Sequences look nothing alike; how do I find a formula I can trust?
Show: brute force in Python. Apples, n ≤ 5 children, m ≤ 6: C(n+m−1, n−1) matches all 35; C(m−1, n−1) says
0 for 3 children and 2 apples, where there are 6. Brackets, n of each: balanced 1 2 5 14 42 132 429 1430 for
n = 1..8 (11% at 8, not half); unbalanced exactly C(2n, n+1).
Explain: Bars: m stars and n−1 bars in a row, choose the bars' places. Reflection: flip every bracket after the
first prefix at −1; that gives n+1 ')' and is undone the same way, so Catalan = C(2n,n) − C(2n,n+1).
Try: explain: the reflection of `())(` and how it is undone; fix: Distributing Apples by C(m−1, n−1) (failure
[7]), found by brute force first.
### 8
Need: Prime Multiples has up to 20 primes and n = 10^18; 2^20 terms is fine, so what can go wrong?
Show: 2,000 random sets of 3 to 6 primes below 10^9, n = 10^18: dividing by wrapped products, about half
(1,088) wrong. Primes 448057 673036937 998748809 552115259 104829379
289322279: unguarded 2,249,152,789,440; with `if (q > n / a[i])` (term 0) 2,249,152,789,387, the exact
sum. With 2, 3, 10^9+7, 998244353, 999999937, four products overflow and
the answer survives: a passing test proves nothing. Derangements: the recurrence matches brute force to 8.
Explain: Add each prime's multiples, subtract each pair's, add triples back; a product above n has no
multiples, so stop before it overflows.
Try: explain: the derangement recurrence, by where person n's gift goes; build: Prime Multiples with the guard
(failure [8]), checked against Python's exact sum.
### 9
Need: An expected value sounds like a sum over every outcome; how is that ever fast?
Show: fixed points of a random permutation, averaged over all n! by brute force: exactly 1 for every n from 1 to
8, though "i stays" and "j stays" are dependent; E[X²] is 2 (n ≥ 2), not E[X]² = 1. Distinct faces in 4 die rolls:
671/216 over all 1,296 outcomes and by indicators, 6(1 − (5/6)^4); mod 998244353, 633,145,727.
Explain: X = X_1 + ... + X_n, X_i = 1 when item i counts; E[X] = ΣP(X_i = 1), dependent or not. Moving Robots:
per square, P(empty) is a product over independent robots. Products need independence.
Try: apply: expected empty boxes for m balls in n boxes, by indicators, then brute force to 5 and 5; build:
ABC326 E, each payment's probability summed, checked by enumerating rolls for small N.
### 10
Need: Fibonacci Numbers has n up to 10^18; how slow is a loop really?
Show: a loop computes F(10^9) mod p in about a second with a subtraction per step, about four with a `%`
(each step waits for the last); 10^18 steps are a billion times that: decades to a century. The 2×2
matrix [[1,1],[1,0]] to the power 10^18 by squaring: 209,783,453 in a microsecond or two, and Python's fast
doubling agrees; both give 21 for F(10^9).
Explain: One step of a linear recurrence is a matrix times the last d values; products associate, so M^n comes
from about 2 log2 n products of d³ each. Entry (i, j) of a^k counts walks of length k.
Try: build: Throwing Dice as a 6×6 matrix, matched against the O(n) DP for n ≤ 1000; fix: a 10×10 product
summing before `%` (failure [10]), found by comparing with Python.
### 11
Need: Nim has heaps of any size; how can one xor decide every position?
Show: a full search of all 120 positions of three heaps up to 7 (lost iff every move leads to a won one)
agrees with "lost iff a xor b xor c = 0"; (1,2,3) is lost for the mover. Grundy's Game (n ≤ 10^6, a
quadratic table too slow): mex values to 10^5, 2.5·10^9 splits, about a second in C++: 41 zeros, the last at
1222.
Explain: From xor 0 every move changes the xor; from xor ≠ 0 a move to 0 exists (shrink a heap holding the
xor's top bit). A game's Grundy number plays as a Nim heap of that size, so sums of games xor.
Try: build: Stick Game's table, after predicting n = 1..10 for moves {1,3,4}; predict: Grundy numbers of a heap
where you take 1 or 2, and explain their period 3.

## Believable numbers
- Run here (g++ -O2, Python 3.13, a shared two-core machine, November 2026; a laptop is as fast or faster): about
  2.5·10^8 modular multiplications a second in C++, 10^7 in a Python loop.
- [1,5,10] A power with an exponent near 10^18: about 90 multiplications, a fifth of a microsecond; a 2×2 matrix
  power, about a microsecond.
- [3] Sieve with smallest prime factors: 10^6 in hundredths of a second, 10^7 in under half a second (40 MB of
  `int`).
- [6] Factorial tables to 10^6: hundredths in C++, a quarter second in Python.

## Go deep, leave for later
- Deep steps: 5, 7, 9 (when inverses fail; a bijection to a known model; linearity of expectation).
- Later: Möbius inversion, Chinese remainder theorem, Lucas's theorem, Burnside's lemma, Gaussian elimination,
  xor basis (CSES Maximum Xor Subset), Miller-Rabin, FFT and NTT.

## Never omit
- Limits pick the method: one n up to 10^12, trial division; 10^5 queries up to 10^6, a sieve.

## Wrong beliefs
- [1] "`x % m` is never negative" (in C++ it takes the sign of x: `-7 % 3 == -1`; add m, then reduce).
- [4] "`a * b / gcd(a, b)` is a safe lcm" (`a * b` overflows first; write `a / gcd(a, b) * b`).
- [5] "`a^(p-2)` is the inverse of a" (only for prime p and a not a multiple of p: a = 2p gives 0;
  modulo 10, 3^8 ≡ 1, but 3's inverse is 7).
- [6] "The factorial formula for C(n,k) works for any n" (for n ≥ p, n! ≡ 0 mod p and has no inverse; Lucas).
- [9] "Linearity of expectation needs independence" (it holds for any variables; products need independence).
- [9] "The larger residue is the larger answer" (residues forget order: 10^9+12 leaves 5).

## Failures to diagnose
- [1] A negative answer from `(a - b) % MOD`.
- [1] `int * int` before `%`: 10^9 · 10^9 overflows.
- [3] The sieve's `j = i * i` in `int` overflows once i passes 46340.
- [5] Exponentiation II: the exponent reduced mod p, not p-1.
- [7] Distributing Apples by C(m−1, n−1), the count when every child gets one: 0 for 3 children and 2
  apples, where brute force finds 6.
- [8] Prime Multiples: a product of primes past 10^18.
- [10] A matrix product that sums residue products before reducing: each is near 10^18, so ten of them
  overflow `long long` (run); reduce after each.

## Practice and project
Per step: its CSES problems, then about ten Codeforces problems tagged math or combinatorics from your rating
to 300 above. Project: a library (power, inverse, sieve, binomials, matrix power), each part checked against
brute force; finish line: Exponentiation II, Binomial Coefficients, Prime Multiples and Throwing Dice accepted
with it.

## Mastery ladder
- Use: solve the CSES problems of the steps from a stated formula.
- Explain: show with numbers why Fermat's inverse fails modulo 10 and for multiples of p.
- Build: solve three of four unseen, untagged Codeforces counting problems rated 1500-1800, an hour each.
- Design: derive a new count two ways (bijection, inclusion-exclusion); check both by brute force.

## Words to own
[1] modulus, residue, binary exponentiation; [2] divisor, prime factorisation, harmonic sum; [3] sieve, smallest
prime factor; [4] gcd, extended Euclidean algorithm, coprime; [5] modular inverse, Euler's totient, Fermat's little theorem;
[6] binomial coefficient, factorial table; [7] stars and bars, Catalan number, bijection; [8] inclusion-exclusion,
derangement; [9] indicator variable, linearity of expectation; [10] linear recurrence, matrix
power; [11] winning position, Nim sum, Grundy number, mex
