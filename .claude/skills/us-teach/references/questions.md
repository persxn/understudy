# Questions that show understanding

Read when you are unsure what to ask next, or how to answer a reply that is wrong, half right or "don't know". `rules/teaching.md` gives the moves; this file gives patterns and examples to copy.

## Patterns

Each makes the learner produce something. Pick the one that fits the idea, not the same one every time.

- **Predict, then check.** "What happens if…?" before they see it. Works for any kind: output, a tool's state, a network event, a participant's reaction.
- **Find the fault.** Show a short example with one mistake. "What is wrong, and what would it cause?"
- **Change one condition.** Take a case they got right and alter one thing. "Same query, but the table has no index."
- **Decide and defend.** Two options, a situation. "Which, and what would make you choose the other?"
- **Explain to a friend.** "Tell a colleague who missed the lesson why this exists, in three sentences." Listen for the reason, not the words.
- **Transfer.** A case from the learner's own field that the section did not show.

Avoid questions answered by yes or no, by picking from a list, or by repeating a sentence of the section: they prove nothing (`rules/levels.md`).

## A wrong answer

Find the belief behind it before correcting. Ask for the reasoning: "How did you get that?"

- Learner (operating systems): "Each thread gets its own copy of the global variables."
- Weak reply: "No, threads share globals." (They now hold two facts and no reason.)
- Better reply: "Two threads both run `count = count + 1` once, starting from 0. With your idea, what is `count` at the end, and what does each thread see?" Their idea predicts 1 in each copy; then show that the program prints 2, or sometimes 1, and ask why.

## "Don't know"

Record it as `no`. Do not fill the silence with the answer. Make the question smaller: "Leave the whole thing aside. When the program starts, where does `count` live?" If the smaller one is also "don't know", it is a gap: send them to the section (`§N.M`) and ask again after.

## A half-right answer

Say exactly which half is right, then ask about the other half only.

- Learner (usability testing): "Five users are enough because you find most problems."
- Reply: "Right that a small group finds most of the big problems. Most of the problems of which kind of user? What would five users from one team miss?"

Record `partly` with a note naming the missing half, so the next surprise question goes there.

## A right answer

Now and then push: argue the other side, or change a condition. A right answer that falls over under one change was a guess.
