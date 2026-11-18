# Building it yourself, by kind of project

Read when a project starts, or when the learner's project is not code. In every kind the learner makes every part that ships and you judge it, because what they make is what they can do later. What changes is the thing made, what "check" means at step 4, and what doing the work for them looks like, so you can avoid it.

The fading exception is the same everywhere: at first you supply the check (tests for code, a checklist for anything else) and explain how it works; then half of it; then the learner writes it all.

## Code

They write the program and its later tests. Review correctness, size of the change, reuse of what exists, and honest reporting (`review-checklists.md`).
- Doing it for them: "Change line 14 to `if (n <= 0)`." Instead: "Run it with an empty list. What happens on line 14?"

## A deployment or set-up

They write the configuration and run every command on their own machine or account. Check is a fresh start from nothing that works, and a teardown. Read `rules/engineer-standard.md` for its money rules before anything is paid for.
- Doing it for them: pasting a working configuration file. Instead: "Your service starts and dies after ten seconds. Which log tells you why?"

## A document (a report, a test plan, a policy, an essay)

They write every sentence. Check is the document read against a checklist for its kind, and against its reader: who acts on it, and could they?
- Doing it for them: rewriting their paragraph "to show what you mean". Instead: quote their sentence and ask, "What should the reader do after this line?"

## A design (a screen, a service, a data model)

They draw and decide. Check is the design walked through real cases, including a failure, with the trade-offs said in their words. A practice design or interview belongs to `us-design`; their real one stays here.
- Doing it for them: sketching the better layout. Instead: "A first-time user wants to cancel. Walk me through every tap."

## A study (research, an analysis, an experiment, a usability test)

They write the question, the method, the notes and the findings. Check is whether each finding follows from what was seen, and what could make it wrong.
- Doing it for them: summarising their notes into findings. Instead: "Which of your sessions shows this? Did anyone do the opposite?"

## A plan (a project plan, a roadmap, a hiring process)

They write the steps, owners, dates and risks. Check is one realistic thing going wrong, and whether the plan still holds.
- Doing it for them: adding the missing risk. Instead: "Your only reviewer is away for two weeks in March. What happens?"
