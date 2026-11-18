# Teaching a tool or service

**At the end of a chapter** the reader can do a real job with the tool on their own (put a change under version control and undo a bad one; run a service with its data kept safe) and, before pressing Enter, say what the command will change and where. That is what lets them recover.

**The usual arc.** A job, or a small disaster the reader recognises ("you removed the container and the data went with it") → a picture of what the tool keeps where (Git's working folder, staging area and repository; Docker's image layers, container layer and volumes) → one terminal session that does the job, with a look at the state after each step → what each command changed, in the picture → the commands that undo, and the ones that cannot be undone → a broken set-up to fix.

**The real thing** is a terminal session on a small real job, with a command that *shows the state* after each command that changes it. Weak:

```text
$ git add notes.txt
$ git commit -m "Add notes"
```

followed by "add stages the file, commit saves it". Better: the same session with `git status --short` after each step, so the reader sees `?? notes.txt`, then `A  notes.txt`, then nothing; and the prose says which of the three areas held the change at each line. The state commands (`git status`, `docker ps -a`, `docker diff`, `kubectl get`) are the reader's eyes; teach them first, use them always.

**Three exercise types.**
- *Predict the state*: "After `git commit --amend`, how many commits does `git log --oneline` show, and has the hash of the last one changed?"
- *Fix a broken set-up*: give a session that ends in `fatal: refusing to merge unrelated histories` or a container that exits at once; the reader finds the cause with the state commands and repairs it.
- *Do the job*: "Put the `site/` folder under version control, with `build/` ignored, in three commits that each make sense", checked against a given `git log` shape.

**Mark with a risk note** every command that deletes, overwrites or rewrites shared state (`git reset --hard`, `docker volume rm`, `terraform apply`), anything that costs money in a cloud service, flags and defaults that changed between versions (`docker-compose` against `docker compose`, Git's default branch), and output you show without having run it.

**Usual failures of generated material, and the cure.**
- *Commands with no picture of what they change*: a cheat sheet in paragraphs. Every changing command is followed by a look at the state and one sentence placing the change in the picture.
- *Flag catalogues*: teach the three options this job needs; say where the rest are (`git log --help`).
- *Happy path only*: show the real error message and the way out; a tool is learned when it refuses.
- *State that does not carry over*: the sessions are one story (`rules/book-standard.md`, "Terminal sessions"); never make again what an earlier chapter made.
