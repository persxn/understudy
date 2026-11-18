# A mechanism section

**Use it** when the reader already knows *what* the thing is and now needs *how it happens*: the order of events between parts, what each part knows, and why it was built that way. Examples: how a request reaches a controller; how a shell finds a program; how a lookup goes through a B-tree; how a review comment travels from a reader to an author. This is where a book's depth lives.

**Order of the parts.**
1. The need: a puzzle the concept alone cannot answer ("so why was the second request fast?").
2. The cast: the parts involved and what each one knows or holds at the start. Keep it to the parts that act.
3. The events, in order, one step per paragraph or per table row, each naming who acts, on what, and what changes. Build the figure up step by step rather than showing a finished diagram first.
4. The same run with one thing changed (cache cold, lock taken, permission missing), so the reader sees which step depends on which.
5. Why it is built this way: the problem the design solved and what it costs.
6. What goes wrong, with the symptom the reader will actually see, traced back to the step that failed.
7. Recap as the list of steps in one line each, then **Check yourself** with at least one "predict what happens when..." question.

**Size.** 1,500 to 3,000 words. A trace table or a sequence figure is almost always worth its space here; a paragraph of five arrows is not.

**Sketch** (a shell book, "How the shell finds a program").
- Need: you typed `python` and got a version you did not install.
- Cast: the shell, the `PATH` variable, the folders it lists, the program files in them.
- Events: the shell splits the line; checks aliases and built-ins; walks `PATH` left to right; runs the first match; remembers it in its hash table.
- One thing changed: install a new Python earlier in `PATH` while the shell is open; it still runs the old one, because of the hash table, until `hash -r`.
- Why: searching every folder every time was slow; the cost is stale answers.
- Symptom traced: `command not found` means no folder in `PATH` had it; `type -a python` shows every match in order.
- Check yourself: "`PATH` is `/usr/local/bin:/usr/bin`. Both hold `python3`. Which runs, and how do you make the other one run?"
