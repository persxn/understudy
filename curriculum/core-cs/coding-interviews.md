# Core CS: coding interviews
for: someone who writes small programs in one language and wants to pass coding interviews
leads to: internship and new-graduate offers, experienced engineer loops (with system design)
status: reviewed 2026-11-19 by independent agent, goal blocks rebuilt
sources: techinterviewhandbook.org/coding-interview-study-plan (topic priorities: trees and graphs high, DP low;
  about 11 hours a week for 3 months; mocks from 60%); interviewing.io/guides/hiring-process (about five
  interviews before the real ones); crackingthecodinginterview.com contents (topics; OO design and threads)
unverified: hours and the step ranges per goal are judgement

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | python-core | none | write interview code in Python without looking things up | lists, dicts, sets, strings, classes, heapq, bisect | 40 | 3 Build |
| 2 | cpp-for-contests | none | write and test C++ fast | STL, overflow, stress tests | 25 | 3 Build |
| 3 | dsa-core-techniques | 1, 2 | pick the technique an array or string problem needs | complexity, complete search, hashing, binary search, two pointers, windows, prefix sums, greedy | 60 | 3 Build |
| 4 | interview-problem-solving | 3 | solve an unseen problem aloud to the rubric | the conversation, lists, stacks, heaps, LRU, intervals, trees, tries, mocks | 50 | 3 Build |
| 5 | recursion-and-dynamic-programming | 3 | turn a search into a DP | backtracking, memoisation, DP families | 60 | 3 Build |
| 6 | graphs-and-trees | 3, 5 | model a problem as a graph | BFS, DFS, topological order, Dijkstra, union-find | 60 | 3 Build |
| 7 | system-design-foundations | networking-basics, sql-and-relational | defend a design with numbers | requirements, estimates, building blocks, trade-offs | 30 | 4 Design |

## Goals
### My first internship coding interview (about 150 h)
Steps: python-core 2, 4, 6-9, 12; dsa-core-techniques 1-10; interview-problem-solving 1-11, 13-14; recursion-and-dynamic-programming 1-5; graphs-and-trees 1-3.
Open with: Two Sum aloud on a 35-minute timer, recorded, in their interview language: restated; "may one element be used twice?" asked and the hand example [3,2,4] kept as a test; the nested loops and their cost said before typing; a dict of values seen so far as the fix; code; a hand trace of [3,2,4] in a table; complexity said; marked against the four rubric dimensions (interview-problem-solving 1-2).
Deep: interview-problem-solving 3, 5, 14; dsa-core-techniques 1; graphs-and-trees 3.
Order: interview-problem-solving 1-2; dsa-core-techniques 1 with python-core 6-7 (what `in` costs); interview-problem-solving 3; python-core 2, 4; interview-problem-solving 4-5, then a first timed mock (14) and one every two weeks after; dsa-core-techniques 2-6 with python-core 8-9; python-core 12; interview-problem-solving 6-8; dsa-core-techniques 7-10; interview-problem-solving 9-11; recursion-and-dynamic-programming 1-5; graphs-and-trees 1-3; interview-problem-solving 13. python-core 2 and 4 are a section each where a bug first shows them; leave out contest-only topics (bitmask subsets, coordinate compression, anti-hash tests) and Python she will not be asked (generators, dataclasses). From no card: one timed online assessment (silent, hidden tests) before the first mock.
Halfway: "I can take an unseen easy array problem from my first question to hand-traced code, aloud, in 35 minutes, and say its cost before I type."

### A new-graduate offer at a large company (about 205 h)
Steps: python-core 2, 4, 6-9, 12; dsa-core-techniques 1-12; interview-problem-solving; recursion-and-dynamic-programming 1-9; graphs-and-trees 1-5, 7, 11, 13.
Open with: the internship goal's Two Sum round (interview-problem-solving 1-2).
Deep: interview-problem-solving 3, 5, 14; dsa-core-techniques 1; recursion-and-dynamic-programming 4; graphs-and-trees 3.
Order: the internship order (python-core woven in as there) to interview-problem-solving 11, then 12; recursion-and-dynamic-programming 1-5; graphs-and-trees 1-5, 7, 11, 13; recursion-and-dynamic-programming 6-9 (TIH ranks DP low); dsa-core-techniques 11-12; interview-problem-solving 13. Mocks every two weeks from interview-problem-solving 5, weekly in the last month.
Halfway: "In a mock on an unseen list, stack, heap or interval problem I clarify, state a brute force, improve it and trace it, without long silences."

### A senior engineer loop (about 260 h)
Steps: python-core; dsa-core-techniques 1-12; interview-problem-solving; recursion-and-dynamic-programming 1-9, 13; graphs-and-trees 1-5, 7, 11, 13; system-design-foundations.
Open with: Merge Intervals aloud, 35 minutes, in their working language: "do touching intervals overlap?" asked and turned into `<=`, sort by start, merge, a hand trace of [[1,4],[4,5]], the cost said, marked against the rubric (interview-problem-solving 2, 10).
Deep: interview-problem-solving 3, 14; recursion-and-dynamic-programming 4; graphs-and-trees 3; system-design-foundations 4, 8.
Order: interview-problem-solving 1-5, a first timed mock; system-design-foundations 1-4 (networking-basics, sql-and-relational held or first); interview-problem-solving 6-12 with recursion-and-dynamic-programming 1-9, 13 and graphs-and-trees 1-5, 7, 11, 13 (python-core, dsa-core-techniques mostly held: revise where a mock shows a gap); system-design-foundations 5-10, then the system-design/foundations goal "Pass system design interviews"; interview-problem-solving 13. Mocks fortnightly, coding and design alternating.

### I compete already and now want interviews (about 50 h)
Steps: interview-problem-solving.
Open with: Product of Array Except Self recorded twice in their contest language, silent as in a round, then aloud from the brute force and its cost to prefix and suffix products, traced by hand on [2,3] before any run; both marked against the rubric's phrases (interview-problem-solving 3, 5).
Deep: interview-problem-solving 3, 5, 14.
Order: interview-problem-solving 3, 5, 1-2, 4, then a timed mock (14) every week; 6-12 at a problem or two each; 13 short. Rows 2, 3, 5, 6 `held` after placement; a step it fails is taught where first used.
Halfway: "I say my brute force and its cost before I type, use names an interviewer can read, and find my bugs by hand before I run anything."

## Why this order
Interview in the language you know best: row 1 or row 2, not both (row 3 needs either); goals name python-core; in C++, cpp-for-contests replaces it. dsa-core-techniques
gives Python's names beside C++'s, so a Python learner needs no row 2. Row 4 precedes 5 and 6: the conversation is then practised on every later problem, and its
structures are asked more than DP; its step 11 is the first recursion, so row 5 step 1 goes fast.

## Checkpoint projects
- After 4: the card's three recorded mocks.
- After 6: five timed mocks on unseen problems, one a graph and one a DP, each with a miss log entry.

## Short on time
Never skip interview-problem-solving 1-5 and 14, or mocks. The new-graduate line in three months (TIH: about
11 hours a week), take dsa-core-techniques 11, recursion-and-dynamic-programming 6-9 (DP ranks low) and
graphs-and-trees 13 short.

## Left out on purpose
- Contest-only rows (segment trees, flows, geometry): competitive-programming.
- A company's recent questions: they change; looked up per book.
- Object-oriented design and concurrency rounds: no card yet.
