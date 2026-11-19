# contest-strategy: turning what you know into solved problems and rating
kind: skill
aliases: codeforces rounds, icpc, upsolving, virtual contests, how to practise
needs: dsa-core-techniques
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: codeforces.com/blog/entry/ 133094 (djm03178: score max(0.3x, x - ⌊120xt/(250d)⌋ - 50w); ICPC style
  t + 10w, easiest first; pretest 1, compile errors free; hacks; 12-hour open hacking),
  20762 (change = (R - r) / 2), 62865 (equal rating: 0.5; 200 below: 0.75; 400 below: 0.9), 53341 (E869120:
  virtual contests, solve times kept), 98806 (Um_nik: archives teach, contests make fast; switch when stuck);
  codeforces.com/api problemset.problems and contest.list (rounds 2271 and 2275: points, ratings, solve
  counts, read 2026-11-19); atcoder.jp/contests/abc400/rules (score, then last solve time plus 5 minutes per
  wrong answer; compile errors free); cerc25.ii.uni.wroc.pl/grules.html (an ICPC regional: three people, one
  PC, 20 minutes per rejected run, compile errors included, last hour frozen); cses.fi tasks 1094, 1621 (limits); usaco.guide/general
  contest-strategy (read first, order, partials), practicing (D. Yao, B. Qi), debugging-checklist; github.com/kth-competitive-programming/kactl
  content/contest/troubleshoot.txt ("Wrong answer" lines quoted); cses.fi/book/book.pdf 1.6 (company contests, IOI, ICPC)
unverified: time boxes, log categories, team roles, weekly load and "a month" in step 12 are judgement

## Promise
Enter a Codeforces, AtCoder or ICPC-style contest knowing its rules, spend its minutes on the right problems,
recover from wrong answers by checklist, and turn each contest into practice.

## The one idea
A contest is a budget of minutes; the result comes from where they go. Picture: an exam, read first, then
answered where you can. Where it breaks: it is marked live, by rules that differ per platform.

## In production
- Rated rounds, ICPC regionals, olympiads, and contests run by companies, some used in recruiting (CSES
  handbook 1.6; which still run is looked up).
- The same habits (read before coding, test before submitting, review every miss) carry into timed online
  assessments and on-call debugging.

## Teaching order
1. The rules, from the platform's page before each round: Codeforces standard (points fall each minute, wrong
   tries cost points), Div. 3, Div. 4, Educational (solved, then penalty minutes), AtCoder (score, then time),
   ICPC (one computer); a template tested before the clock starts.
2. The first minutes: read A to C in full, limits and samples by hand; order by the standings' solve counts;
   the idea, why it is right and its cost said before typing.
3. Test or submit: samples, your own edge cases, one max test (largest n, hardest values) for time and overflow
   (KACTL); a stress test (cpp-for-contests 9) for an unproven greedy.
4. After any verdict other than accepted, a fixed checklist (KACTL, USACO Guide): output format, debug output,
   state cleared, n = 1, overflow, statement and code reread, `-Wall -Wshadow`, stress test.
5. Pretests, system tests and hacks: "pretests passed" is provisional; `unordered_map` meets crafted tests (the
   defence: dsa-core-techniques 5); the 12-hour open hacking phase.
6. Time boxes and switching: a limit per problem set before starting it; under summed penalty (ICPC) shortest
   first; USACO and IOI subtasks and partial scores, costed first.
7. ICPC team play: three people, one computer, a printed team reference (KACTL is a model); one types while two
   solve on paper; debugging from a printout; the frozen last hour.
8. After the round: upsolve the first unsolved and every failed problem; the Codeforces editorial a step at a
   time (D. Yao), then coded with it closed (B. Qi); a strong accepted solution read.
9. The error log: per miss, what failed (reading, idea, proof, code, testing, time), its cause, its cost, and a
   rule that extends the KACTL checklist; reread before each contest.
10. Virtual contests on Codeforces: a past round on its real clock, ranked against the original standings;
   minutes per problem kept in a sheet (E869120).
11. A training week: archives for learning, a little above your level, sorted by rating; contests for speed
   (Um_nik); problem ratings read as solve chances.
12. Rating lags: each update moves r half the way to R, the rating your place fits (d = (R - r) / 2); judge a
   month of performances, not one round.

## Judged by
- [1] This round's scoring, penalty and hacking rules were looked up before it started.
- [2] Every statement up to the first past your level was read before any code.
- [3] Each submission passed the samples and at least one edge case of your own.
- [4] Each wrong answer went through the checklist before a resubmission.
- [6] No problem ran past its time box without a decision to stay.
- [8-9] The first unsolved problem is upsolved; each miss has a log line with a rule.

## Step notes
### 1
Need: One wrong try sank me in an Educational round and barely mattered in a Div. 2; isn't a wrong answer a
wrong answer?
Show: one record (A accepted at minute 8; B wrong on test 3 at 14, accepted at 20; C at 55) under each
published rule. A 120-minute Div. 2 with assumed values 500, 1000, 1500: 484 + 870 + 1170 = 2524; the wrong
try cost 50, as much as 12.5 minutes of B's decay. Educational (t + 10w): penalty 8 + 30 + 55 = 93, the wrong
try a tenth of it. AtCoder: 55 + 5 = 60, only the last solve's time counting.
Explain: Each rulebook turns minutes and mistakes into rank its own way (decaying points, summed minutes, the
last solve); its page says what each costs this round.
Try: apply: their last round's record rescored under the other two rules, three totals a second person
reproduces; predict: what a compile error costs on Codeforces, AtCoder and their regional, then look it up.
### 2
Need: Problems are in order of difficulty, so why not start at A and work down?
Show: Codeforces Round 2271 (Div. 1 + Div. 2, 180 minutes): G, 3500 points, rated 3100, solved by 123; H1,
3000 points, rated 2800, by 152 (solvers to November 2026): the later letter was easier, and its points said
so. In that round 5 minutes of reading cost A (500) about 7 points and D (1750) 23; a wrong try from a missed
line, 50.
Explain: Letters are only an order; points, where given, are the setters' estimate; the standings' solve
counts are the field's measurement. Reading costs less than one wrong try, and an obvious problem is coded
at once.
Try: apply: next round, every statement to the first past their level read before typing, each with idea,
proof and cost written; predict: from a virtual's standings at minute 30, the third problem.
### 3
Need: My solution passed the samples and a big random test of 2·10^5; why time limit?
Show: CSES Distinct Numbers (n ≤ 2·10^5, 1 s) with a `find` over a vector of values seen: sample 0.003 s;
2·10^5 random values in 1..10, 0.024 s; 2·10^5 distinct values, 4.1 s; random values in 1..10^9, 4.0 s.
Sorted and `unique`: 0.04 s.
Explain: A max test is the largest n with the values that make your loops work hardest; random small values let
every search stop early, so the size of n alone tested nothing.
Try: build: a max-test generator that reproduces their last time-limit verdict locally; predict: the slow
version on 10^5 distinct values (a quarter of 4.1 s), then run.
### 4
Need: Wrong answer on test 5; I changed something, resubmitted, got it again: what goes in between?
Show: CSES Increasing Array (x ≤ 10^9), moves summed in `int`: sample right. Hunch 1, `'\n'` and fast input;
hunch 2, the loop rewritten: both print -447305535 on 2·10^5 values, 10^9 then ones. The checklist's overflow
line with that max test finds it in one run (`long long`: 199998999800001; `-Wall` silent). Each hunch cost
10 penalty minutes in an Educational round, 50 points in a Div. 2.
Explain: A hunch changes code without a found cause; the checklist makes each cause a test that takes a minute,
and nothing is resubmitted until one fails.
Try: fix: their last wrong answer by the checklist on a timer, the minute of each line and the line that
found it written; apply: what their hunch resubmissions cost that round.
### 5
Need: "Pretests passed", then it failed after the round, yet my code didn't change: how?
Show: g++ 13 here, 2·10^5 keys into `unordered_map<long long,int>`: random, under 0.2 s; multiples of 107897,
0.02 s; multiples of 172933, tens of seconds (42 and 52 s in two runs). A hacker sends the last; a successful
hack test joins the system tests and all are rejudged (blog 133094).
Explain: Pretests are a sample of the tests; a hash table is fast on average over keys nobody chose, and after
the round someone chooses. So test your own worst cases before the hacker does.
Try: predict: their own accepted `unordered_map` solution on multiples of 172933, then run; decide: which of
their last five pretests-passed solutions a max test would break, and why.
### 6
Need: If I solve the same problems in the end, does the order really change my rank?
Show: Codeforces Round 1125 (Div. 3; contest 2275, ICPC rules; A to E rated 800, 800, 1000, 1300, 1500) with
assumed solve times of 5, 8, 12, 25 and 40 minutes (not from the round): easiest first, penalty 5 + 13 + 25 +
50 + 90 = 183; hardest first, 357; under AtCoder's rule, 90 either way. Round 2271 (standard, 180 minutes, A
to D 500, 1000, 1250, 1750; assumed 10, 15, 30, 45 minutes): A to D 3772, B first 3778, D to A 3667.
Explain: Summed penalty counts each minute for its own problem and every later one: shortest first. Decaying
points punish order less (the worst order here: two wrong tries). Partial scores: costed first (USACO Guide:
seconds to half an hour); when ideas stop, switch and come back.
Try: apply: their last virtual rescored in their order and shortest first; decide: a time box per problem from
its rating, and in the log, what was done when one ran out.
### 7
Need: Three of us and one keyboard: who types, and what do the other two do?
Show: a team virtual of a past regional in the Codeforces Gym under CERC 2025's rules (three people, "one
provided PC", 20 minutes per rejected run, compile errors included, ranking frozen in the last hour). A fourth
person or a screen recording logs each minute: who typed, keyboard idle, debugging at it. Judged by KACTL's
"Wrong answer" lines "Print your solution! Print debug output, as well." and "Explain your algorithm to a
teammate." Finish line: idle and debugging-at-keyboard minutes, summed from the log.
Explain: The keyboard is the scarce resource: one person types while two solve on paper, and a wrong answer is
debugged from a printout so the keyboard stays busy.
Try: build: a team reference within their contest's page limit; apply: a second logged team virtual, both
sums lower than the first's.
### 8
Need: I read the editorial and understood it; why can't I solve the next problem like it?
Show: their last round's first unsolved problem, by the USACO Guide's rules: the editorial read "step by step
until you get unstuck" (D. Yao), closed after each paragraph; then coded with it closed, since "unless you
understand the solution perfectly, you should always implement the solution afterward" (B. Qi). Finish line:
a week later, accepted again from a blank file on a timer, the minutes predicted first; the judge's submission
time is the record.
Explain: Reading checks the idea; coding it closed proves you hold it. Coaches differ on when to look (D. Yao:
15-20 minutes without progress at Bronze, 30-40 at Silver; Um_nik: "You don't read the editorial"): choose a
rule.
Try: apply: three upsolves this way, each with paragraph count and minutes; decide: their rule on when to
open an editorial, written down.
### 9
Need: My rating has been flat for months; where am I actually losing it?
Show: a month's misses, a line each, costed by the round's rules (10 penalty minutes a wrong try in Div. 3,
50 points plus decay in a Div. 2, minutes stuck), summed by cause. A round whose performance R fell below r
lost (r - R)/2: 150 for 1300 against 1600 (blog 20762).
Explain: Costs add up per cause; the largest total, not the most painful miss, is where training goes.
Try: build: their month's log sorted by total cost, each cost checked by a second person against the rules;
apply: one checklist rule from the top cause, and the next month's total for it compared.
### 10
Need: Practice goes fine at home; why am I so slow in a real round?
Show: Round 2275 as a virtual, on its real clock, no help, ranked among the original contestants. E869120's
rule: time each problem "from opening problem statement to getting AC" and "make a spreadsheet of problem,
solved and time"; here with the minute read, the idea, the first submission and accepted, beside the judge's
submission times. Untimed practice records none of it.
Explain: Only the real clock and penalty show where speed is lost: reading, idea, typing or debugging.
Try: predict: their rank before each of three virtuals; build: the sheet, which a second person matches
to the submission list.
### 11
Need: Which problems should I practise: the ones I can solve, or ones far above me?
Show: blog 62865: a problem at your rating is solved half the time, 200 below 0.75, 400 below 0.9; the Elo
curve those fit gives 0.97 at 600 below. The USACO Guide's useful problem: a struggle, then solved or just missed.
Explain: A problem teaches when solving it is uncertain; ratings say in advance where that is.
Try: decide: next week's archive band from their rating; apply: twenty archive problems logged solved or not by
rating band, compared with the curve.
### 12
Need: I lost 150 in one round; did I get worse?
Show: d = (R - r) / 2 (blog 20762): from 1400 at a steady 1600, ratings run 1500, 1550, 1575, 1588. From 1600,
one round at 1300 gives 1450; the next at 1600 gives 1525.
Explain: Each update halves the gap to the performance, so rating trails your level by rounds, and one unusual
round moves it half as far as it was unusual.
Try: predict: rounds from 1400 at a steady 1700 to pass 1650 (three); explain: their last
month's rating line beside each round's performance.

## Believable numbers
- [1,6] Read 2026-11. Codeforces standard: x/250 a minute in 120 minutes (500: 2), never below 0.3x once
  accepted, 50 a wrong try; Div. 3, 4, Educational: t + 10w, unsolved free. AtCoder ABC: last solve plus 5
  minutes a wrong answer. CERC 2025: 20 minutes a rejection, compile errors included.
- [3] C++: some hundreds of millions of simple steps a second (CSES book 2.3); a quadratic `find` on 2·10^5
  values, 4.1 s here.

## Go deep, leave for later
- Deep steps: 2, 4, 8, 9 (reading the set first, the checklist, upsolving with the editorial closed and the
  costed log are what move a stuck rating).
- Later: IOI subtask strategy in depth; coaching a team; hacking others' solutions as a skill.

## Never omit
- Rules, penalties and AI-tool rules are looked up per contest, never quoted from memory.

## Wrong beliefs
- [1] "A wrong submission costs the same everywhere" (Codeforces skips pretest 1 and compile errors, AtCoder
  compile errors; each ICPC regional sets its own; only solved problems pay).
- [2] "Problems are sorted by difficulty" (not always, says the USACO Guide; see the standings).
- [3] "A big random test is a max test" (random small values let searches stop early: 0.024 s against 4.1 s).
- [4] "Change a line and resubmit to find the bug" (two hunches cost 20 minutes and found nothing; one max
  test did).
- [5] "Pretests passed means accepted" (system tests and hacks follow).
- [6] "A started problem must be finished" (the USACO Guide warns against "too long" on one; read the rest,
  come back with new ideas).
- [6] "Order does not matter if I solve the same problems" (summed penalty: 183 against 357 minutes above).
- [8] "Reading the editorial is learning it" (code it unless you understand it perfectly: B. Qi).
- [9] "My worst miss costs me the most" (costs add up per cause: sum them).
- [12] "One bad round means I got worse" (rating moves part of the way each round; one round is noise).

## Failures to diagnose
- [2] A condition in a statement's last paragraph missed until a wrong answer.
- [4] Resubmitting a random change, not a found cause.
- [5] A solution hacked by an anti-hash test on `unordered_map`.
- [6] An hour on C while D, solved by more, stayed unread.

## Practice and project
Weekly: a rated round and a virtual contest, each upsolved. Project: ten virtual contests, each with a written
review and log lines; finish line: no mistake logged twice in the last five.

## Mastery ladder
- Use: a rated round with rules looked up, the set read first, the checklist used.
- Explain: from your submission times, show where a contest's minutes went and the costliest decision.
- Build: the ten reviewed virtual contests above.
- Design: a four-week plan for a stated rating and goal (archive band, contests, upsolving), defended.

## Words to own
[1] pretest, system test, penalty; [2] standings, solve count; [3] max test; [4] troubleshooting checklist;
[5] hack, anti-hash test, open hacking phase; [6] time box, subtask, partial score; [7] team reference document,
frozen scoreboard; [8] editorial; [9] error log; [10] virtual contest; [11] archive, problem rating;
[12] performance
