# Depth: when a lesson came out thin

Read when `us_check.py` says a lesson is too short, or when a section reads like a list of facts. A thin lesson is rarely missing words; it is missing a move. Find which, and add that. Never pad.

**The four usual gaps, and what to add.**

1. **The mechanism was told, not shown.** "fork copies the process" is a fact. Depth is the walk: before the call there is one process with this memory and these open files; the kernel makes a second entry with a new number and the same contents; both continue from the same line, and the only difference is the number the call hands back. Then the proof the reader can run, and what its output shows line by line.
2. **One example, no variation.** One case teaches the case. Change one thing and walk it again: the file is empty; the second user arrives first; the cache is cold. The second walk is where the rule becomes visible.
3. **Mistakes named, not lived.** "Be careful to close the file" is advice. Make it happen: the program that forgets, its real output or message, how the reader would notice in their own work, and the way out.
4. **No "why this way".** What problem did this design solve, what did people do before, what does it cost? Two honest paragraphs turn a rule into something the reader can reason from, and explain to someone else.

**A test for each section.** Could the reader now (a) predict what happens in a case the text did not show, (b) say why, in terms of the parts, and (c) recognise the usual failure when they meet it? If any answer is no, that is the move to add.

**Weak (about 60 words).**

> A zombie is a process that has finished but whose parent has not called `wait`. It shows as `Z` in `ps`. Zombies use no memory but fill the process table. Always call `wait`.

**Better (the same idea at depth, in outline).** Start a child that exits at once while the parent sleeps for thirty seconds; run `ps` and show the `Z` line. Ask why the kernel keeps anything at all: the parent has not yet collected the exit status, and that number has to live somewhere. Show what is kept (the entry and the status) and what is gone (memory, open files). Change one thing: the parent exits first; who collects the child now? Show it. Then the real failure: a server that forks per request and never waits, what its `ps` looks like after an hour, and the two cures. Then a question that needs the model, not the definition.

**Not depth:** a second recap, a history lesson nobody asked for, every option of a command, a list of "other things to know", longer sentences. If a section teaches one small thing and is complete, it is a `short` section: say so in the plan instead of stretching it.
