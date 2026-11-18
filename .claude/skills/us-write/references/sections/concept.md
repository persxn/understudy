# A concept section

**Use it** when the section introduces one idea the rest of the chapter stands on, and the reader's difficulty is *what it is* and *why it exists*, not yet the steps of using it: a pointer, a commit, a transaction, a usability task, a bean. If the hard part is the order of events inside it, write a mechanism section instead; if it is the steps of doing a job, a procedure.

**Order of the parts.**
1. The need: the problem the reader cannot yet name or solve, in one concrete situation.
2. The picture, and where it stops being true.
3. The definition in one bold sentence, then each term in it unpacked once, with the picture beside it.
4. The real thing: the smallest example in which the idea does work, and a walk through it.
5. The boundaries: what it is *not* (the neighbouring idea it is confused with), shown with a contrasting example.
6. The usual misconceptions, each with how it shows up.
7. A short recap and **Check yourself**.

**Size.** 1,200 to 2,000 words. If the definition needs more than three new terms, split it: one section for the idea, a later one for its variations.

**Sketch** (a version-control book, "What a commit is").
- Need: you broke a file that worked an hour ago and want the hour-old version back.
- Picture: a photo album of the whole project; each photo is the project at one moment, with a note saying why it was taken. Breaks: Git does not store a full copy of unchanged files each time; it reuses them.
- Definition: **a commit is a saved snapshot of the whole project, with a message, an author, a time and a link to the commit before it.** Unpack "snapshot", "link to the commit before".
- Real thing: make two commits, then `git log --oneline` and `git show` the first; walk through each line of the output.
- Boundaries: a commit is not a diff, though `git show` displays one; a commit is not the same as saving a file.
- Misconception: "a commit sends my work to the server" (it does not; that is a push, chapter 4).
- Check yourself: "You edit two files and commit. How many snapshots does the repository now hold, and what does the newest one link to?"
