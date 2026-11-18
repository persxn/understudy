# The first session

Read on a first run, before asking the learner anything. The aim is one sentence of goal and the few facts the planner needs, in as few messages as possible: a question their message already answered tells them you were not listening.

## The questions, and why each is asked

Ask only what their words have not made clear, all in one message, after saying the goal back.

| Question | Why | What to do with the answer |
|---|---|---|
| What is it for? (only when they named a subject, not a goal) | the same subject is a different book for a job, an exam or a hobby | write the use into the goal sentence |
| Deadline and hours a week ("none" is fine) | the planner fits the route to them | `deadline:` and `hours a week:` in `goal.md` |
| A whole profession, or this one thing? (only for a software-engineering goal) | only "become an engineer" switches on `rules/engineer-standard.md` | `engineer standard: on` or `off`; any other field stays `off` |
| Their machine and its limits, once: system, internet data cap, usage plan, how they learn best | blocked tools, big downloads and usage budget shape every later step | "Told by the learner" in `private/machine.md`, then `python3 scripts/us_doctor.py` |

Do not ask what they can already do: placement (`rules/levels.md`) finds it from the plan; asking now gets a guess.

## Say the goal back

One sentence that starts "I can …", concrete enough to test: a thing they will be able to do, not a topic.

- Weak: "I can understand operating systems."
- Better: "I can explain what happens from a key press to a letter on screen, and read a kernel panic message without fear."

## Example: a programming goal

> **Learner:** I want to get a backend job. I know some Python.
> **You:** Your goal as I understand it: "I can build, test and deploy a small web service the way a junior backend engineer would." Is that right? And three things: a deadline and hours a week, if you have them; your machine (system, any internet data cap, which usage plan); and do you want the whole engineer path, or this job's skills only?

"Some Python" goes under `already has`.

## Example: a non-programming goal

> **Learner:** My team wants me to start running usability tests on our app.
> **You:** Your goal as I understand it: "I can plan, run and report a small usability test of our app that my team acts on." Is that right? Is there a date for the first test, and how many hours a week can you give it? And, once: which computer you use and which usage plan.

No engineer-standard question: the goal is not a software profession. Nothing to install is normal.

## Then

Write `private/goal.md` (template in `rules/private-files.md`) and hand to `us-map`.
