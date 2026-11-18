# Exercises

**The ladder.** A chapter's practice climbs in three steps, and each section's **Check yourself** sits on the first rungs.
- *Guided*: one idea, familiar material, a nudge. Proves the reader followed.
- *On your own*: several ideas, new material, no nudge. Proves the reader can transfer.
- *Project or case*: the whole chapter, with choices nobody made for them. Proves the reader can do the job.

**Question types that make the reader act.** Recall ("what is a commit?") checks memory, not understanding; avoid it. Use these, one example each:
- *Predict*: "Before running it: what does this print when the list is empty?" The reader must run the model in their head; a wrong prediction is the most useful moment in the chapter.
- *Find the fault*: "This Dockerfile rebuilds every dependency on each code change. Which line causes it?" Real faults with real symptoms, not typos.
- *Change it*: "Make the endpoint return 404 instead of 500 for an unknown id. Which one line changes?" Small, precise edits show the reader where the moving parts are.
- *Decide*: "Two options for storing sessions: in memory or in Redis. Your app runs on three servers. Which, and why?" There is a better answer and a reason; say both.
- *Explain to a friend*: "A colleague says `git pull` is the same as `git fetch`. In three sentences, what would you tell them?" Forces the reader to order the idea in their own words.

**Hidden answers.** Every question has its answer in `<details>`, and the answer teaches: the result, the reason, and the most likely wrong answer with why it is tempting. Weak: "`B`." Better: "`B`. The inner loop's `break` ends only the inner loop, so the outer one carries on with the next row. If you said `A`, you pictured `break` leaving both loops; that needs a flag or a function return." An answer that is a program is tagged and run (`rules/book-standard.md`, `answer`).

**How a chapter project is set, by kind.**
- *Language*: a small complete program for a stated problem, with sample input and the expected output, so the reader can check it runs right.
- *Tool*: a job on a real set-up, ending in a state the reader can show (`git log --oneline --graph`, `docker ps`, a page that loads), plus one deliberate breakage to recover from.
- *Framework*: a feature added to the running project, with the request and response (or the screen) that proves it works and the test that pins it.
- *System*: a trace or experiment on a new situation: fill a table, predict, then check by running where the machine allows; answer gives the full table.
- *Skill*: the practice done on the reader's own material, then judged against the chapter's checklist; the answer is a model version with its reasons, since the reader's own work cannot be marked here.

Every project states what done looks like. A project with no finish line is either skipped or never ends.
