# interview-problem-solving: solving coding problems aloud in a job interview
kind: skill
aliases: coding interview, technical interview, leetcode
needs: dsa-core-techniques
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: techinterviewhandbook.org: coding-interview-rubrics (dimensions, signals, bands), -cheatsheet (the
  conversation; 2-3 questions; approach "up to 5-10" minutes), -study-plan (priorities, Grind 75, mocks from
  60%), algorithms/ linked-list, stack, heap, interval, tree (corner cases), behavioral-interview (STAR(R), 3-5
  projects); metacareers.com blog preparing-for-your-software-engineering-interview-at-meta (45 minutes, no
  compiler, approach scored); interviewing.io guides/hiring-process ("how" and "what"
  companies; five interviews "doubles your chances"), blog
  does-communication-matter-...-100k-interviews (Code, Solve over Communicate); crackingthecodinginterview.com
  contents (BUD, best conceivable runtime); every bug shown run in Python 3.13 in /tmp
unverified: step order, counts and times are judgement; "I, not we" is common coaching, unsourced

## Promise
Take an unseen problem from a vague statement to tested code in 45 minutes, aloud, with the structures
interviews use.

## The one idea
You are scored on what the interviewer saw and wrote down. Picture: a driving test marks the mirror checks, not
only arriving. Where it breaks: arriving still matters most; code and problem solving outweigh talk.

## In production
- Often 45 minutes (Meta: 5 introductions, 35 coding, 5 questions) in a shared editor, often without running
  the code. Look up per company: languages, running code, AI rules, problem count.
- Notes are written per dimension; unsaid reasoning is unseen. "How" companies weigh the thinking, "what"
  companies a fast optimum (interviewing.io).

## Teaching order
1. The rubric (communication, problem solving, technical competency, testing); one whole round on Two Sum,
   whose idea is held (dsa-core-techniques 5) so attention stays on the conversation: restate, clarify,
   example, nested loops and their cost, hash map, a green light, code, trace, complexity.
2. Clarifying: size (10 or 10^5 items?), range, negatives, empty, duplicates, sorted, may input change; a hand
   example kept as a test.
3. Brute force to better, aloud: the brute force and its cost in a minute, the best conceivable runtime, CtCI's
   BUD (bottlenecks, unnecessary and duplicated work), structures tried in turn; Product of Array Except Self
   (no division).
4. Coding while narrating, in your interview language: real code, telling names, a helper named with its
   contract and written last if the interviewer agrees (`in_bounds(r, c)`), so the main idea lands first.
5. Verifying by hand, without running: read as another's code; a typical case traced line by line in a table
   of variables, then `[]` and one item; fixed; time and space restated.
6. Linked lists: reversal, dummy head, fast and slow pointers; Reverse Linked List, Linked List Cycle, Merge Two
   Sorted Lists, Remove Nth Node From End Of List.
7. Stacks and queues: Valid Parentheses, Min Stack, Implement Queue using Stacks (two stacks, amortised O(1)); a monotonic
   stack for the next greater element: Daily Temperatures, Largest Rectangle in Histogram.
8. Heaps: keep k, pop the worst kept: a min-heap for the k largest (Top K Frequent Elements), a max-heap for the
   k smallest (K Closest Points to Origin; `heapq` is a min-heap: push negated keys); Merge K Sorted Lists; two heaps, Find
   Median from Data Stream.
9. Hash maps in a class design, each operation costed: LRU Cache (map to nodes of a doubly linked list; ask
   before `OrderedDict`), Time Based Key-Value Store (binary search on time, dsa-core-techniques 6).
10. Intervals: sort by start, overlap test (`a.start <= b.end and b.start <= a.end`; ask if touching counts),
   merge; Merge Intervals, Insert Interval.
11. Binary trees, often the first recursion: null base case, trust the calls on both children, combine; call
   depth is the height; pre-, in-, post- and level order (step 7's queue); Maximum Depth of Binary Tree,
   Validate Binary Search Tree, Kth Smallest Element in a BST, Lowest Common Ancestor of a Binary Tree.
12. Tries for prefix search: children and an end mark; Implement Trie (Prefix Tree).
13. Reading what is tested: limits and words ("sorted", "top k", "all combinations", "next greater") to a
   pattern, named aloud, on unseen Grind 75 problems, topics hidden.
14. Behavioural answers and mocks: three to five project stories in STAR(R); timed mocks with a person or a
   recording; a miss log.

## Judged by
- [1-2] Restated the problem; asked about size, edge inputs, changing the input?
- [3] An approach with time and space agreed before code; then the repeated work removed?
- [4] Real code, readable names, each part explained as written?
- [5] Traced a typical and an edge case by hand, found your own bugs, gave the code's real time and space?
- Never long silent; said when stuck; took hints?
- [14] Each story: a real situation, your actions ("I", not "we"), a result, a lesson?

## Step notes
### 1
Need: I can write Two Sum in two minutes; what is there to grade in 45?
Show: Two Sum aloud in 35 timed minutes, recorded, marked against the four rubric dimensions. Say the cost and
mean it: nested loops on 10^4 numbers took about 2 s in Python here, a hash map about a millisecond (10^5:
about 0.015 s).
Explain: The interviewer writes notes per dimension from what they see and hear; silent correct code gives
communication and testing nothing to record, and problem solving only the result.
Try: build: the recording with each dimension's moments timestamped; predict: nested loops on 10^5 (about a
hundred times 10^4), then say it aloud as a reason.
### 2
Need: The problem looks clear; why spend minutes on questions?
Show: Two Sum with the map built first, then scanned: [2,7,11,15], 9 gives [0,1], right; [3,2,4], 6 gives
[0,0], one element used twice. "May I use one element twice?" plus the hand example [3,2,4] finds it first.
Explain: Each question fixes an input the code must handle; its answer becomes a test (TIH: at least 2-3).
Try: apply: five questions for Merge Intervals, each with the input it rules in or out; fix: their own Two Sum
on [3,2,4].
### 3
Need: At home I solve it in silence; in the room I froze until I had the optimum. Why is that marked down?
Show: Product of Array Except Self, recorded twice on a 15-minute timer: silent until the optimum, then aloud
("nested loops, O(n²); reading n items is O(n); the repeated work is the left products": prefix and suffix,
traced on [2,3]). A second person marks each with TIH's rubric phrases, timestamped: the silent one meets "jumped into coding without explaining" (communication, leaning no hire) and
"without much explanation of their thought process" (problem solving, strong no hire); the spoken one shows
"Communicates approach, rationale and tradeoffs" and "Determined time and space complexity accurately".
Explain: The approach is scored (Meta: it "can be as important as having the right answer"); a brute force
said aloud is a fallback and shows the repeated work to remove.
Try: apply: an unseen problem aloud, brute force and cost in 2 minutes; explain: which BUD letter the prefix
products removed.
### 4
Need: Talking slows my typing; can't I code silently and explain after?
Show: islands on a grid with the bounds inline as `0 <= r <= R`: on rows "110", "000": 1, right; on "000",
"010", "011": `IndexError`. As `in_bounds(r, c)`, said once ("true when 0 <= r < R"), the contract is heard and
checked once.
Explain: Narration lets the interviewer follow and catch errors; a helper with a stated contract moves one
fiddly check into one place.
Try: build: a narrated flood fill recording, every line explained as written; fix: the `<= R` bound and say
why it failed only where land touches the last row or column.
### 5
Need: I read my code twice and it looked right; why trace it?
Show: Product of Array Except Self with the suffix loop `range(n - 1, 0, -1)`. [5,1] gives [1,5], right by
luck; [2,3] gives [1,2], not [3,2]; LeetCode's [1,2,3,4] gives [1,12,8,6]. In the trace table, `i` never
takes 0.
Explain: A test finds a bug only if wrong code gives a different answer; a table of variables shows a loop's
first and last index, which reading skims (TIH's testing signal: "stepping through each line, updating the
program's state at each step").
Try: predict: what [2,3] gives, by table, before running; apply: trace their last solution on a typical input
and `[]`, a bug found or none, said aloud.
### 6
Need: My reversal works on an empty list and one node; isn't that enough edge cases?
Show: reversal with `cur.next = prev` before saving `next`: [] gives [], [7] gives [7], [1,2,3] gives [1].
Saving `nxt = cur.next` first: [3,2,1].
Explain: Each pointer write destroys the only path to the rest unless it was saved; [] and [7] have no rest to
lose, so the smallest catching test has two nodes.
Try: predict: the bug's output on [1,2,3,4]; build: Remove Nth Node From End with a dummy head, traced for n
equal to the length.
### 7
Need: Isn't a stack in a loop still quadratic when it pops in a while loop?
Show: Daily Temperatures on 10^4 falling values: nested loops 2.52 s, monotonic stack 0.0018 s (10^5: 0.028 s).
Explain: Each index is pushed once and popped at most once, so the inner while loop runs n times in total.
Try: fix: Valid Parentheses returning true for "(" (failure [7]); predict: pushes and pops on 10^5 rising values.
### 8
Need: Top k means a heap; which kind?
Show: K Closest Points with a min-heap of size k: [(3,3),(5,-1),(-2,4)], k = 2 gives (-2,4),(5,-1), the two
farthest; LeetCode's [[1,3],[-2,2]], k = 1 gives [1,3]. Negated keys (a max-heap): (3,3),(-2,4).
Explain: A size-k heap pops its top; to keep the k smallest the top must be the largest kept.
Try: predict: which heap Top K Frequent needs and what it pops; fix: failure [8] in their code.
### 9
Need: Why not keep the usage order of an LRU cache in a list?
Show: 10^5 random gets and puts on 20,000 keys, capacity 10^4: usage order in a list with `remove`, 2 to 3 s;
`OrderedDict`, a few hundredths of a second.
Explain: The map finds a key in O(1); only a doubly linked list moves it to the front and drops the oldest in
O(1) too.
Try: build: LRU Cache with their own linked list, every operation costed aloud; explain: what `OrderedDict` hides.
### 10
Need: Do touching intervals overlap?
Show: [[1,4],[4,5]] (LeetCode's second example, expected [[1,5]]): with `<=` merged to [[1,5]]; with `<`
left as two.
Explain: The answer is the problem's choice; ask it and turn it into the comparison.
Try: apply: Insert Interval with touching intervals as a test; decide: `<` or `<=` for meeting rooms.
### 11
Need: Each node is bigger than its left child and smaller than its right; isn't that a BST?
Show: 5 with children 4 and 6; 6 with children 3 and 7: checking children says true; bounds passed down say
false (3 sits right of 5). A 3,000-node chain: `RecursionError` (limit 1000).
Explain: The rule binds whole subtrees, so each call needs its ancestors' bounds (and in-order visits a BST
sorted); call depth is the height, so a skewed tree is a list.
Try: fix: the children-only check to pass bounds down, false on that tree; predict: recursive Maximum Depth on
a 2,000-node chain (`RecursionError`), then run.
### 12
Need: After inserting "apple", why does my trie say "app" is a word?
Show: no end mark: `search("app")` true; with an end mark `"$"`: false, while `startsWith("app")` stays true.
Explain: A path proves a prefix; only the mark proves a word ended there.
Try: build: Implement Trie with `search` and `startsWith`; predict: `search("")` in both versions.
### 13
Need: How do I know which technique a new problem wants?
Show: limits to cost, as measured here: Python did 10^7 loop additions in 0.3 to 1 s (quiet or loaded
machine), so n ≤ 10^5 at O(n²) is about 5·10^9 steps, minutes: the limit rules it out before any idea.
Explain: The limits and words ("sorted", "top k", "next greater") point to a pattern; naming it aloud invites
the interviewer to agree.
Try: decide: the pattern for five unseen Grind 75 problems, topics hidden, in 2 minutes each; apply: one solved.
### 14
Need: I solve mediums at home in 25 minutes; why does a clock and someone watching wreck it?
Show: two recorded 45-minute mocks a week apart, an unseen problem each, set by someone else; a second person
scores each against "Judged by" and TIH's rubric bands, a timestamp for each miss; a story told in STAR(R) on
the same recording, its "we" sentences counted. Finish line: the second mock's misses fewer, none repeated.
Explain: The room adds a clock, a listener and an unseen problem; only mocks practise those (TIH: start them
"when you are 60% through" the plan; interviewing.io: five interviews, mock or real, "doubles your chances").
Try: build: three mocks, finish line: no miss of the first in the third; apply: one story retold with each "we"
made "I".

## Believable numbers
- [1] Meta: 45 minutes: 5 introductions, 35 coding, 5 questions. TIH: approach talk "a few minutes to up to 5-10".
- [1,13] Python 3.13 here (November 2026): 10^7 loop additions 0.3 to 1 s; nested loops on 10^4 items 2 s.

## Go deep, leave for later
- Deep steps: 3, 5, 14 (the brute force aloud, the trace, and the room itself make the difference).
- Later: grids and graphs (graphs-and-trees 1-3, 7; ask about diagonals); backtracking and DP
  (recursion-and-dynamic-programming); bit manipulation and math (TIH: low); object-oriented design and
  concurrency (no card); design rounds (system-design-interviews).

## Never omit
- Every problem aloud, timed, traced before running.
- Structures drawn first; corner cases: empty, one, two items.

## Wrong beliefs
- [3] "The goal is the optimal solution; stay quiet till you have it" (the approach is scored, at Meta it "can be
  as important as having the right answer"; silence is the lowest band; state the brute force briefly, then improve).
- [1] "Talking well makes up for not solving" (in interviewing.io's 100k interviews a point lost in Code or
  Solve cost far more than one in Communicate).
- [5] "Code written means done" (TIH's lowest testing band: "Did not even test code against typical cases"
  and "announced they are done").
- [6] "Empty and one-item tests cover the edge cases" (a reversal that loses the list passes both).
- [14] "Solving problems alone prepares me for the room" (the room adds a clock, a listener and an unseen
  problem; TIH and interviewing.io both prescribe mocks).
- [13] "Memorising solutions is preparation" (a changed condition breaks a recalled answer; name the pattern).
- [9] "An LRU cache is a hash map" (the map finds a key in O(1); the list in use order moves it and drops the
  oldest in O(1)).
- [11] "A BST has each node between its two children" (all the left subtree is smaller: pass bounds down).

## Failures to diagnose
- [6] The rest of a list lost: `next` overwritten before it was saved.
- [6] A crash on `fast.next.next` when `fast.next` is null.
- [7] Valid Parentheses accepting "(": the stack not checked empty at the end.
- [10] Touching intervals not merged: `<` where the rule needs `<=`.
- [8] K closest points kept in a min-heap of size k: it pops the closest and keeps the farthest.

## Practice and project
Mocks from about 60% through the plan (TIH), about five before real interviews (interviewing.io). Project:
three recorded 45-minute mocks scored by a second person against "Judged by"; finish line: no miss of the first in the third.

## Mastery ladder
- Use: solve a listed problem aloud in 45 minutes by steps 1-5.
- Explain: in your recording, mark where each rubric dimension shows.
- Build: pass every "Judged by" test in two of three mocks on unseen problems set by someone else.
- Design: interview a peer with a problem you chose; write a scored note per dimension.

## Words to own
[1] rubric; [2] clarifying question; [3] best conceivable runtime; [4] helper; [5] dry run, edge case;
[6] dummy head, fast and slow pointers; [7] next greater element; [8] min-heap, max-heap, top k; [9] doubly
linked list; [10] overlap; [11] traversal, level order, BST invariant; [12] trie; [13] pattern; [14] STAR, mock
interview, miss log
