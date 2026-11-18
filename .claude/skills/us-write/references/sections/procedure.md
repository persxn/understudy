# A procedure section

**Use it** when the section teaches a job done in steps: set up a project, recover a deleted branch, run a moderated test session, migrate a schema. The reader leaves able to do the job again, on their own material, and to know at each step whether it worked.

**Order of the parts.**
1. The job and when you need it, in one real situation, and what "done" looks like (the state or result you will be able to see).
2. What must be true before you start, and how to check it (a version, a file, a signed consent form).
3. The steps, numbered. Each step has three parts: what to do, why this step exists (one sentence), and how to see that it worked (the output, the state, the observable result).
4. A full run of the procedure on the book's running project or case, with real output.
5. The points where it usually fails, each with its symptom and the way back. Say which steps can be undone and which cannot, before the reader reaches them.
6. Variations the reader will meet (a different platform, a larger team), briefly.
7. Recap as the bare list of steps, then **Check yourself** with a "this step failed with this message: what now?" question.

**Size.** 1,000 to 2,500 words. A procedure longer than about nine steps is two procedures; split it at a point where the reader can stop and check.

**Sketch** (a Git book, "Getting a deleted branch back").
- Job: you deleted `feature-login` with `git branch -D` and it had two days of work. Done looks like: the branch is back, `git log feature-login` shows the last commit.
- Before: do not run `git gc`; nothing has been pruned yet.
- Steps: 1 `git reflog` and find the last commit on the branch (why: the reflog remembers where HEAD has been; see it: a line `checkout: moving from feature-login`). 2 `git branch feature-login <hash>` (why: a branch is only a name for a commit). 3 `git log --oneline feature-login` (see it: your two days of commits).
- Fails: the reflog has expired (entries for commits no branch reaches go after 30 days by default; a default like this gets a risk note); the work was never committed (then Git cannot help).
- Check yourself: "`git reflog` shows nothing about the branch. What does that tell you about the work?"
