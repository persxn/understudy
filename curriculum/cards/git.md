# git: Git for people who will work on a team's code
kind: tool
aliases: version control, branching and merging, pull requests, github
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: plans/learn-git/PLAN.md (steps follow its chapters); git-scm.com/book/en/v2 (Pro Git);
  missing.csail.mit.edu (Git as a skill); State and danger run with git 2.43 in /tmp; git-scm.com/docs/git-init
  (ref formats); git-scm.com/docs/reftable (refs in `.git/reftable`); docs.github.com
  about-pull-request-merges (squash, rebase merges)

## Promise
Keep a project's history, work with others through branches and pull requests, and recover from any mistake, knowing what each command changes.

## The one idea
A commit is a snapshot of the whole project pointing to its parent; a branch is a movable label on one commit. Picture: a photo album, each photo knowing the one before; sticky notes for branches. Where it breaks: unchanged files are stored once; "rewriting" makes new photos while the old stay until cleaned away.

## In production
- Changes go through reviewed pull requests with automatic checks; main is protected.
- Undo under pressure: revert shared commits, the reflog for lost work, rotate a leaked secret.

## Teaching order
1. A first repository: `git init`, `add`, `commit`; the three places work lives, read with `git status`.
2. Recording changes: `git diff` against `git diff --staged`, `git add -p`, `.gitignore`, `git restore`; one logical change per commit, a subject line and a body that says why.
3. Exploring history: `git log --graph --oneline`, `git show`, one file's history (`git log -- path`), `HEAD~2` and hashes, `git blame`, tags.
4. Branches as pointers: `git branch`, `git switch`, HEAD, detached HEAD.
5. Merging: fast-forward and three-way (the merge base, a merge commit with two parents), a conflict made on purpose, its markers resolved, `git merge --abort`.
6. Remotes: `clone`, `fetch`, `pull`, `push`, remote-tracking branches, a rejected push, SSH keys or HTTPS with a credential helper.
7. Pull requests: a small change on a branch or fork; review given and answered; required checks, branch protection, `CODEOWNERS`; merge commit, squash or rebase, and the history each leaves.
8. Rebasing and rewriting: `git rebase main` (new ids); `--amend`, `rebase -i` (squash, reword, `fixup` with `--autosquash`); `pull --rebase`; `cherry-pick`; force-push with lease; shared history; merge or rebase.
9. Team workflows and releases: trunk-based with short-lived branches, or release and hotfix branches; a commit-message convention; version numbers as `git tag -a`; signed tags.
10. Undoing: an undo per place (working tree, index, local or shared commits); `reset` soft, mixed, hard; `revert` (`-m 1`); `restore --source`; reflog, `ORIG_HEAD`, `git fsck`; a leaked secret; what cannot return.
11. Inside Git: blobs, trees, commits named by hash, read with `cat-file -p`, built by hand (`hash-object -w`, `update-index`, `write-tree`, `commit-tree`); a branch as a file, `HEAD` symbolic; packfiles, `git gc`.
12. Daily tools: `git stash` (and `-u`), `git worktree add` for a second checkout; `git bisect` by hand, then `git bisect run` with a test script; `git log -S` and `git grep` to find when code appeared.
13. Configuration and hooks: `git config` levels (system, global, local), `--show-origin`; aliases; `.gitattributes` (line endings, binaries); a pre-commit hook, shared by `core.hooksPath`, skipped by `--no-verify`.
14. Large repositories: `git clone --depth 1` (shallow), partial clone (`--filter=blob:none`), sparse checkout; LFS for large binaries; submodules and their pinned commits.

## State and danger
- [1,11] The working tree (files on disk); the index (`.git/index`: the next commit); objects (`.git/objects`); refs (`.git/refs`, `HEAD`).
- [6] Remote-tracking refs (`refs/remotes/origin/...`): your last view of the remote, moved by fetch, pull, push.
- [10] The reflog (`.git/logs`): where `HEAD` and each branch pointed; local, and it expires.
- [10] `git reset --hard` discards staged and unstaged edits to tracked files (untracked files stay). Safe: `git stash` first, or `git reset --keep`, which refuses to drop local changes.
- [2,10] `git checkout -- file` and `git restore file` overwrite it with its staged copy (not the last commit): unstaged edits gone. Safe: `git stash` first.
- [2] `git clean -fd` deletes untracked files and folders for good. Safe: `git clean -nd` (the same, as a dry run) first.
- [6,8] `git push --force` replaces the remote branch, dropping others' commits. `--force-with-lease` refuses ("stale info") if the remote moved since your last fetch, but any fetch (an editor's too) renews the lease: add `--force-if-includes`.
- [4] `git branch -D` forces what `-d` refuses ("not fully merged").

## Step notes
### 1
Need: I edited the file after `git add`, then committed; which version did Git save?
Show: `echo one > a.txt; git add a.txt; echo two > a.txt; git commit -m first`. Most predict two; `git show
HEAD:a.txt` prints `one`, and `git status --short` still shows ` M a.txt`. `git cat-file -p HEAD`: `tree
20e50a0...`, author, committer, message.
Explain: `add` copies the file into the index; `commit` snapshots the index, not the folder.
Try: predict: `git status --short` after a second `git add a.txt` (`M` moves to the first column); build: their
project's first commit, `git status` clean after.
### 2
Need: `git diff` shows nothing, but I know I changed things; where did my changes go?
Show: after `git add`, `git diff` is empty; `git diff --staged` shows `-one`, `+two`. A committed `.env` added
to `.gitignore` still shows ` M .env`; `git check-ignore -v .env` stays silent until `git rm --cached .env`.
Explain: `git diff` compares files with the index, `--staged` the index with the last commit; `.gitignore` only
hides files not yet tracked.
Try: apply: `git add -p` splitting two edits in one file into two commits, `git log -p` showing one each; fix: a
tracked build folder of theirs, until `git check-ignore -v` names the rule and its files are still on disk.
### 3
Need: I renamed a file and its `git log` now starts at the rename; where did its history go?
Show: `calc.py` committed twice, `git mv` to `money.py`, one more commit: `git log --oneline -- money.py` lists
2 commits, `--follow` 4; `git blame` names the old `calc.py`. `git cat-file -t` gives `commit` for `git tag
v1`, `tag` for `git tag -a v1.1`.
Explain: Git stores snapshots, not renames; `--follow` and `blame` detect one by similar content.
Try: predict: what `HEAD~2` names, then check with `git log --oneline -1 HEAD~2`; apply: the commit that last
changed a line of theirs, found by `git blame`, its message and diff read with `git show`.
### 4
Need: If a branch is not a copy of my files, what is it, and where did my detached commit go?
Show: `wc -c .git/refs/heads/main`: 41 bytes, a hash and a newline; `.git/HEAD` holds `ref: refs/heads/main`
(after `git gc`, a line in `packed-refs`; with `--ref-format=reftable`, refs live in `.git/reftable`). Commit
on `git switch --detach HEAD~1`, switch back: "you are leaving 1 commit behind"; not in `git log --all`, but in
`git reflog`; `git branch rescue <hash>`.
Explain: A branch names one commit and moves when you commit; HEAD names the branch, or when detached a commit.
Try: predict: what `git branch feature` adds under `.git/refs/heads` (one 41-byte file, main's hash), then
check; fix: a switch refused over local changes, until the switch is done and the edits are still there.
### 5
Need: We edited different lines; why did Git call it a conflict?
Show: lines `a` to `f`. Branches change lines 1 and 6: a clean merge, two `parent` lines in `git cat-file -p
HEAD`. Lines 2 and 3: `CONFLICT (content): Merge conflict in f.txt`, one hunk between `<<<<<<< HEAD`,
`=======`, `>>>>>>> feature`; `git merge --abort` restores it.
Explain: A three-way merge compares each side with the merge base; changes to the same or adjoining lines
conflict.
Try: apply: the same conflict with `-c merge.conflictStyle=diff3`, the base shown after `|||||||`; build: a
conflict in their repository resolved, tests run, committed.
### 6
Need: `git status` said I was up to date; why was my push rejected?
Show: clones `ann` and `cy` of a bare repository. Ann pushes; cy's `git status`: "Your branch is up to date
with 'origin/main'". After `git fetch`: "behind 'origin/main' by 1 commit". A third clone that committed
instead reads "ahead of 'origin/main' by 1 commit", and its push: `! [rejected] main -> main (fetch first)`.
Explain: `origin/main` is your last copy of the remote's branch, moved only by fetch, pull and push; status
reads that copy.
Try: predict: `git log --graph --oneline --all` after both commit and fetch (a fork at the base); apply: `git pull
--rebase`, then push, from their second clone, until the push is accepted and the graph is one line.
### 7
Need: The pull request was squash-merged; why does `git branch -d` say my branch is not merged?
Show: `git merge --squash feature` of two commits, committed as "Add g (#12)": `git branch -d feature`:
`error: the branch 'feature' is not fully merged`, though `git diff main feature` is empty. GitHub: squash
"works best for short-lived branches"; rebase merge "creates new commit SHAs".
Explain: Squash and rebase merges write new commits, so the branch's commits never become ancestors of main.
Try: decide: merge commit, squash or rebase for their team, by the `git log --graph` each leaves; apply: one
reviewed pull request of theirs, comments answered, checks green.
### 8
Need: I rebased onto main and changed no code; why is my push rejected now?
Show: `feature` pushed, main moves on; `git rev-parse --short HEAD` before and after `git rebase main`: two
hashes for the same code, and `git cat-file -t` on the old one: still `commit`. `git push`: `[rejected]
(non-fast-forward)`; `--force-with-lease`: `+ <old>...<new> (forced update)`. (A fetch renews the lease:
State and danger.)
Explain: A hash covers the parent; replayed on a new parent, each commit is new, and the remote's old ones can
only be replaced.
Try: apply: `git commit --fixup <commit>`, then `git rebase -i --autosquash main`, until `git log --oneline
main..` lists only the original commits, the fix inside one; decide: merge or rebase, by the history their
team reads.
### 9
Need: Which commit runs in production, and how do we name a release?
Show: `git tag -a v1.1 -m "release 1.1"`, two commits on: `git describe` gives `v1.1-2-g` and a short hash
(tag, commits since, commit). A lightweight `git tag v1.2`: `describe` still says `v1.1-2-...`; `--tags` gives `v1.2`.
Explain: An annotated tag is an object with tagger, date and message; `describe` uses only those by default.
Try: build: a release tag of theirs, until `git ls-remote --tags origin` lists it (a plain `git push` says
"Everything up-to-date" and sends no tag; `git push origin <tag>` does); decide: trunk-based or release
branches for their team's deploys.
### 10
Need: I ran `git reset --hard` and my last two commits vanished; are they gone?
Show: c1, c2, c3; `git reset --hard HEAD~2`: `git log` shows c1. `git reflog`: `HEAD@{1}: commit: c3`. `git
reset --hard HEAD@{1}`: `HEAD is now at ... c3`. Once pushed, `git revert` adds `Revert "c3"` instead. (What
`--hard` destroys: State and danger.)
Explain: Reset moves the branch (soft: only that; mixed: and the index; hard: and the files); the reflog
remembers where it was, so commits come back and uncommitted edits may not.
Try: predict: `git status` after `reset --soft HEAD~1` and `--mixed` (staged; modified); fix: a merge pushed by
mistake, by `git revert -m 1`, until the merged files are gone and the merge is still in `git log`.
### 11
Need: If every commit is a whole snapshot, why isn't `.git` huge?
Show: commit `a.txt` (`hi`) and `b.txt`, then a change to `b.txt` only. `git rev-parse HEAD~1:a.txt HEAD:a.txt`:
`45b983b...` twice; 7 objects in all. `printf 'hi\n' | git hash-object --stdin` and Python's
`hashlib.sha1(b"blob 3\0hi\n")` print that hash, on any machine (a SHA-1 repository; one made with
`--object-format=sha256` names objects by SHA-256).
Explain: An object is named by its content's hash, so an unchanged file is one blob in every tree.
Try: build: a commit by hand (`hash-object -w`, `update-index`, `write-tree`, `commit-tree`) shown by `git
log`; predict: objects added by a commit of one new file (3: blob, tree, commit).
### 12
Need: The test passed 300 commits ago; must I read them all?
Show: 300 commits, one breaking `price(150) == 1.5`. `git bisect start HEAD HEAD~299`, then `git bisect run`
with that assert as a `python3 -c` test: 8 runs, the right commit. A test that failed everywhere
(an import broken by `-I`) named the second commit.
Explain: Each test halves the range (log2 n runs); the exit code is the verdict (0 good, 125 skip, else bad).
Try: apply: `git bisect run` on a regression of theirs, until it names the commit and `git bisect reset`
returns them to their branch; apply: `git stash -u`, switch, `git stash pop`, the untracked file back.
### 13
Need: I added a pre-commit hook; why did my teammate's commit skip it?
Show: a `.git/hooks/pre-commit` refusing staged `print(` blocks the commit; `--no-verify` passes. A clone gets
only `.sample` files. `git config --show-origin user.email` names the file the value came from.
Explain: `.git/hooks` is never cloned: teams commit hooks and set `core.hooksPath`, and CI checks again.
Try: apply: `.githooks/pre-commit` and `core.hooksPath` in a fresh clone, the hook firing; fix: a file saved
with Windows line endings that `git diff --stat` shows as every line changed, by `* text=auto` in
`.gitattributes`, until it counts only the lines really edited.
### 14
Need: Our clone takes ten minutes; do I need the whole history?
Show: 51 commits of a 200 KB random file, `.git` 11 MB. `git clone --depth 1 big shallow`: `warning: --depth is
ignored in local clones; use file:// instead.`, 11 MB. From `file:///.../big`: 1 commit, 384 KB.
Explain: Shallow fetches recent commits only; partial (`--filter=blob:none`) fetches contents on demand; sparse
checkout writes fewer files.
Try: predict: `git log` in the shallow clone (one commit); decide: LFS, a submodule or a package for their
large asset.

## Go deep, leave for later
- Deep steps: 4, 8, 10, 11 (a branch is a 41-byte pointer; rebasing makes new commits and pushing them can drop a colleague's; every undo moves pointers that the reflog remembers; content-named objects explain all of it).
- Later: Git servers, mailed patches, transfer protocols, `rerere`, bundles, migrating from other systems.

## Never omit
- `git status` and `git log --graph` after each new command; a break-it-and-fix-it task in every chapter.
- [8,10] Never rewrite shared history unless the team agreed.
- Look up when planned: the Git version, the hosting service.

## Wrong beliefs
- [1,11] "A commit stores my changes" (it stores a snapshot; diffs are computed on display).
- [4] "A branch is a copy of the files" (it is a pointer to one commit).
- [4,10] "Deleting a branch deletes its work" (its commits stay a while, found via the reflog or `git fsck`).
- [10] "A hard reset can always be undone" (commits return via the reflog, staged edits only as blobs via `git fsck`; unstaged edits are gone).
- [10] "Removing a committed secret in a new commit makes it safe" (it stays in history; rotate it).
- [8] "Rebase is only a tidier merge" (it makes new commits with new ids).

## Failures to diagnose
- [6] A rejected push ("fetch first"): the remote has commits you lack.
- [5] A conflict: both sides changed the same lines.
- [4] A switch refused over local changes: commit, stash or restore them.
- [4] Commits on a detached HEAD, lost from view after switching away: make a branch at them.
- [10] A leaked secret: in every clone's history; rotate it.

## Practice and project
Guided: on the learner's own repository. On your own: repair a broken repo. Project: a team project begun at step 9 and finished after step 10, two clones; finish line: a protected main, a reviewed pull request, a resolved conflict, a release tag, one recovered "lost" commit.

## Mastery ladder
- Use: the daily team cycle: branch, commit, pull request, update, merge.
- Explain: draw what commit, merge, rebase and reset do to commits and pointers.
- Build: recover unaided from a lost branch, a bad reset, a bad rebase, a leaked secret.
- Design: choose and defend a workflow, merge style and branch protection for a stated team.

## Words to own
[1] repository, working tree, staging area, commit; [2] hunk; [3] commit hash, annotated tag; [4] branch, HEAD,
detached HEAD; [5] three-way merge, merge commit, merge base, fast-forward, conflict; [6] remote, remote-tracking branch, fetch, pull, push;
[7] pull request, squash merge, branch protection; [8] rebase, cherry-pick, force-with-lease; [9] trunk-based development;
[10] revert, reset, reflog; [11] blob, tree, ref; [12] stash, bisect; [13] hook; [14] shallow clone, sparse checkout, submodule
