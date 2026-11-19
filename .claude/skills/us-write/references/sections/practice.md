# A practice section

**Use it** to close every chapter (plan kind `practice`). It turns what the reader followed into what the reader can do alone. The question types and how to hide answers are in `../exercises.md`; this file is the section's shape.

**Order of the parts.**
1. One paragraph: what the reader can now do, and what this practice will prove.
2. Guided tasks (two or three): the reader works on something already in the chapter, with a nudge. A change to an example, a prediction, a fault to find.
3. On-your-own tasks (two or three): new material, no nudge, using several of the chapter's ideas together. At least one asks the reader to decide or explain, not just to produce.
4. The chapter project or case: one larger task that uses the whole chapter, on the book's running project or on the reader's own material. State what done looks like so the reader knows when to stop, as a finish line they can test alone: `check=` on the model answer, or a checklist (`../exercises.md`).
5. Every task has its answer hidden in `<details>`: a run program, an expected terminal state, or a model answer with the reasons and the most likely mistake.

**Size.** As long as the tasks need: usually 600 to 1,500 words including answers. Six to eight tasks. Fewer, harder tasks beat many easy ones.

**The climb must be real.** Each step on the ladder needs more of the reader than the last: first apply one idea to a familiar thing, then combine ideas on a new thing, then make choices nobody gave them. A practice where task 5 is as easy as task 1 is a quiz, not a ladder.

**Sketch** (a Docker chapter on volumes).
- Guided: "Run the guestbook with the named volume, sign it, remove the container, run it again. Predict: are the entries there? Check with the page."
- Guided: "`docker volume ls` shows two volumes; which one is the guestbook's, and how can you tell without guessing?"
- On your own: "Start PostgreSQL 16 with its data in a volume called `pgdata`, create a table, recreate the container, and show the table survived."
- On your own: "A colleague used a bind mount to `./data` and the app cannot write to it. Find out why (hint withheld)."
- Project: "Write the commands that upgrade the guestbook from `guestbook:1` to `guestbook:2` without losing an entry, and prove it." Answer: the command list, the proof, and the mistake of forgetting `-v` on the new container.
