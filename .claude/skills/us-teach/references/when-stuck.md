# When the learner is stuck

Read when the learner has tried and is not moving, in a lesson or at a check. The ladder below is the one in `rules/levels.md` ("When the learner is stuck on their own project") and `rules/teaching.md`, worked through. Climb one rung per reply, and only if they are still stuck: each rung gives away a little more, and what they work out themselves is what they keep.

## The ladder

1. **A pointed question**, or the exact section that covers it (`§N.M`). The question should cut the problem in half: "Does the request reach the server at all?"
2. **Where the problem is.** The line, the step, the paragraph, the moment in the session. Not what is wrong with it.
3. **The idea in two lines.** After one round of questions with no progress, or with a deadline inside a week. Two lines name the idea; they never contain the finished answer (no code, no rewritten sentence). Record it with `--note "told the idea"` so a check follows.

Describing a case in which their answer fails is always allowed; describing the repair is not.

## A worked example (networks)

The learner's container serves a page, but the browser on their machine cannot reach it.

- Rung 1: "From inside the container, does `curl localhost:8000` work? What does that tell you?" They try: it works.
- Still stuck. Rung 2: "So the server runs. The problem is between your machine and the container: look at how the port was published and what address the server listens on."
- Still stuck after one more question. Rung 3: "A server listening on 127.0.0.1 inside a container only hears the container itself. Listen on 0.0.0.0 and publish the port." They make the change themselves.

## The same ladder, for a skill (writing a research plan)

The learner cannot see why their interview questions get thin answers.

- Rung 1: "Read your third question aloud. What is the shortest honest answer to it?" ("Yes.")
- Rung 2: "Look at how questions two to five begin."
- Rung 3: "Questions that start 'Do you' or 'Would you' invite yes or no, and guesses about the future. Ask about the last time it happened." They rewrite the questions; you do not.

## The idea in two lines

Two lines is a limit, not a target. Write the idea, not the steps: "the index is only used when the query starts with its first column" is an idea; "add `CREATE INDEX ... (a, b)`" is the answer. If you cannot say it without giving the answer, stay on rung 2 and ask another question.

## When the book is the problem

If they are stuck because the section never explained what they need, the ladder is the wrong tool: note the section in `private/now.md` and offer the `us-review` repair at the end of the session (the SKILL.md says how).
