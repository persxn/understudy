# Reviewing a contest solution

Read before reviewing a solution the learner wrote, solved or not, and before an upsolve. The SKILL.md says to point and never rewrite; this file says what to look at, in which order, and what a good correctness argument sounds like.

## Order

1. **Correctness argument first, before you read the code.** Ask why it is right. A solution that passed with no reason will fail on the next problem that looks like it, and the reason is the part that transfers.
2. **Cost.** Time and memory in terms of the input limits, then whether that fits the limits given. "n is 2·10^5, my loop is n log n, about 4 million steps" is an answer; "it is fast" is not.
3. **Edge cases.** The smallest input, the largest, all values equal, negative numbers, overflow of 32-bit integers. Name a case, ask what the code does; never say what to change.
4. **Clarity.** Only after the above, and only what would have cost them time: a name that hid a bug, a copy of the same loop twice.

## A weak and a good argument

Problem: choose the most meetings that do not overlap.

- Weak: "I sort by end time and take what fits. It passed." Nothing says why the greedy choice cannot lose.
- Good: "Take the meeting that ends first. Any best answer can swap its first meeting for this one, because this one ends no later, so it still fits with the rest. Repeat on what is left." That is an exchange argument; once they can say it, they can reuse it.

When the argument is weak, ask for the case that would break it: "Suppose a best answer does not take the earliest-ending meeting. What can you do to it?"

## When they are stuck in an upsolve

Use the steps in the SKILL.md (a question, then the idea's name, then where their approach breaks). Reading the editorial is allowed after a real attempt; then they close it and write the solution from memory, and explain it back to you. A solution typed while reading the editorial counts as not solved.

## What to record

In `private/compete.md`, one line per recurring mistake kind (overflow, off by one at the boundary, wrong greedy without a proof), not per problem. A mistake kind seen three times is worth a short repair from the chapter that owns the idea.
