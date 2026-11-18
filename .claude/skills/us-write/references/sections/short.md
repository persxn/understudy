# A short section

**Use it** (plan kind `short`) for one small thing that needs no picture and no mechanism: one command, one term, one rule, one keyword, one convention. If you find yourself writing a picture and a trace, it was not short: tell the planner, or write a full lesson.

**Order of the parts.**
1. The need, in one or two sentences: the moment the reader will want this.
2. The real thing: the smallest example, run, with its result.
3. What it means, in two or three sentences, connected to an idea the reader already has.
4. One mistake, with its symptom.
5. **Check yourself** with one or two questions that make the reader use it.

No recap: the section is its own recap.

**Size.** 300 to 700 words. Resist padding: a short section that grows to 900 words of "it is important to note" is worse than one of 400.

**Sketch** (a Python book, "Leaving a loop early with `break`").
- Need: you are searching a list of orders for the first one over £100; once you find it, looking at the rest wastes time.
- Real thing: a six-line loop over `orders` that prints the match and `break`s; the output shows only one line, and a counter shows the loop ran three times, not ten.
- Meaning: `break` ends the innermost loop at once; the program continues after the loop. It ends one loop only, which matters in the next chapter's nested loops.
- Mistake: putting `break` after the `if` instead of inside it, so the loop always stops after the first order; the symptom is "not found" for data that has a match.
- Check yourself: "In a loop inside a loop, the inner one hits `break`. Which loop ends, and what runs next?"

Weak version of the same section: a paragraph defining `break`, `continue` and `pass` together, no running example. Three ideas, no need, no symptom; the reader will remember none of them at the moment they need one.
