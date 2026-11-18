# Learn Git
for: someone who can use a terminal a little and has written small programs, but has never used version control
run: console
env: GIT_AUTHOR_DATE=2026-01-05T10:00:00 GIT_COMMITTER_DATE=2026-01-05T10:00:00

## Part I · Your own history

### 1 Getting started: your first repository
1.1 Life without version control | story
1.2 What version control does for you | teaches: version-control, snapshot, project-history
1.3 Installing Git and checking it works | teaches: git-command, git-version
1.4 Telling Git who you are | teaches: git-config, user-identity
1.5 Making a repository | teaches: git-init, repository, working-tree, dot-git-folder
1.6 Asking Git what it sees | teaches: git-status, untracked-file
1.7 Your first commit | teaches: git-add, staging-area, git-commit, commit, commit-message
1.8 Reading the history | teaches: git-log, commit-hash
1.9 The second commit: the everyday cycle | teaches: modified-file, edit-stage-commit-cycle
1.10 Getting help from Git itself | teaches: git-help
1.11 Three places your work can be | teaches: three-areas | level: 2
1.12 Practice: your first repository | practice | level: 3

### 2 Recording changes well
2.1 What did I change? | teaches: git-diff, diff-hunk
2.2 What am I about to commit? | teaches: diff-staged
2.3 Staging part of a file | teaches: git-add-patch, partial-staging
2.4 Removing and renaming files | teaches: git-rm, git-mv, rename-detection
2.5 Telling Git what to ignore | teaches: gitignore, ignore-pattern
2.6 Taking a file out of the staging area | teaches: restore-staged
2.7 Throwing away an edit | teaches: restore-worktree
2.8 Writing a good commit message | teaches: subject-line, message-body, imperative-mood
2.9 How big should a commit be? | teaches: atomic-commit | level: 4
2.10 Line endings and whitespace | teaches: line-endings, autocrlf, whitespace-errors | level: 2
2.11 Practice: recording changes | practice | level: 3

### 3 Exploring history
3.1 Shaping the log | teaches: log-oneline, log-graph, log-limit
3.2 Searching the log | teaches: log-author, log-grep, log-since
3.3 Seeing one commit whole | teaches: git-show
3.4 Naming commits without their hash | teaches: revision, head, ancestry-ref
3.5 Comparing two commits | teaches: diff-between-commits, diff-stat
3.6 The history of one file | teaches: log-follow, log-patch
3.7 Who wrote this line? | teaches: git-blame
3.8 Reading an old version of a file | teaches: show-at-revision
3.9 Marking versions with tags | teaches: tag, lightweight-tag, annotated-tag
3.10 Finding the commit that added a piece of code | teaches: pickaxe-search | level: 2
3.11 Practice: exploring history | practice | level: 3

## Part II · Branching

### 4 Branches
4.1 Why work on a branch? | teaches: branch
4.2 Creating and listing branches | teaches: git-branch, branch-list
4.3 Switching branches | teaches: git-switch, switch-create
4.4 What HEAD points to | teaches: head-attached | needs: head | level: 2
4.5 What switching does to your files | teaches: switch-updates-worktree, carry-uncommitted | level: 2
4.6 When Git refuses to switch | teaches: switch-blocked
4.7 Seeing branches in the graph | teaches: diverged-history | needs: log-graph
4.8 Detached HEAD | teaches: detached-head | needs: revision | level: 2
4.9 Renaming and deleting branches | teaches: branch-rename, branch-delete, unmerged-branch-warning
4.10 The default branch and naming branches | teaches: default-branch, branch-naming
4.11 Why a branch costs almost nothing | teaches: branch-as-pointer | level: 2
4.12 Practice: branches | practice | level: 3

### 5 Merging and conflicts
5.1 Bringing work back together | teaches: git-merge, merge-into-current
5.2 Fast-forward merges | teaches: fast-forward
5.3 Three-way merges and merge commits | teaches: merge-commit, merge-base, three-way-merge | level: 2
5.4 When both sides change the same lines | teaches: merge-conflict, conflict-markers
5.5 Resolving a conflict | teaches: resolve-conflict, conclude-merge
5.6 Backing out of a merge | teaches: merge-abort
5.7 Taking one side of a file whole | teaches: checkout-ours-theirs
5.8 Seeing conflicts more clearly | teaches: diff3-style, merge-tool | level: 2
5.9 Keeping conflicts small | teaches: conflict-prevention | level: 4
5.10 Reading merges in the history | teaches: merge-parents, first-parent-log | level: 2
5.11 Fast-forward or merge commit? | teaches: no-ff, ff-only | level: 4
5.12 Practice: merging and conflicts | practice | level: 3

## Part III · Working with others

### 6 Remotes
6.1 A copy somewhere else | teaches: remote, bare-repository
6.2 Cloning a repository | teaches: git-clone, origin
6.3 Remote-tracking branches | teaches: remote-tracking-branch | needs: branch-as-pointer | level: 2
6.4 Fetching new work | teaches: git-fetch
6.5 Pulling: fetch, then merge | teaches: git-pull | needs: git-merge
6.6 Pushing your commits | teaches: git-push, upstream-branch
6.7 When a push is rejected | teaches: non-fast-forward-reject | needs: fast-forward
6.8 Ahead and behind | teaches: ahead-behind | level: 2
6.9 Adding and managing remotes | teaches: git-remote, multiple-remotes
6.10 Pushing tags and deleting remote branches | teaches: push-tags, delete-remote-branch, fetch-prune | needs: tag
6.11 Talking to a server over HTTPS and SSH | teaches: https-remote, ssh-remote, ssh-key, credential-helper
6.12 Practice: remotes | practice | level: 3

### 7 Collaborating through pull requests
7.1 Where a team keeps the shared repository | teaches: hosting-service, shared-repository
7.2 One branch per change | teaches: feature-branch | needs: branch
7.3 Opening a pull request | teaches: pull-request
7.4 Forks: contributing without write access | teaches: fork, upstream-remote | needs: multiple-remotes
7.5 Keeping your branch up to date with main | teaches: sync-with-main | needs: git-fetch, git-merge
7.6 Reviewing a pull request | teaches: code-review, review-comment
7.7 Answering a review | teaches: review-follow-up
7.8 How a pull request gets merged | teaches: merge-button, squash-merge, rebase-merge | level: 2
7.9 Automatic checks on every pull request | teaches: ci-check | level: 2
7.10 Protecting the main branch | teaches: branch-protection, required-checks
7.11 Being a good author and reviewer | teaches: review-etiquette, small-pull-request | level: 4
7.12 Practice: a pull request from start to finish | practice | level: 3

### 8 Rebasing and rewriting history
8.1 Why a tidy history helps | teaches: linear-history
8.2 Rebasing a branch | teaches: git-rebase, replayed-commits | needs: merge-base
8.3 What rebase really does to your commits | teaches: new-commit-ids | level: 2
8.4 Conflicts during a rebase | teaches: rebase-continue, rebase-abort, rebase-skip | needs: resolve-conflict
8.5 Fixing the last commit | teaches: commit-amend
8.6 Interactive rebase | teaches: interactive-rebase, todo-list
8.7 Squashing, rewording and reordering | teaches: squash, reword, reorder-commits
8.8 Splitting a commit in two | teaches: edit-stop, split-commit | needs: git-add-patch | level: 2
8.9 Fixup commits and autosquash | teaches: fixup-commit, autosquash
8.10 Pulling with rebase | teaches: pull-rebase | needs: git-pull
8.11 The golden rule: do not rewrite shared history | teaches: shared-history-rule | level: 4
8.12 Force-pushing safely | teaches: force-push, force-with-lease | level: 4
8.13 Copying single commits | teaches: cherry-pick
8.14 Merge or rebase? | teaches: merge-vs-rebase | level: 4
8.15 Practice: rebasing | practice | level: 3

### 9 Team workflows and releases
9.1 Why a team agrees on a workflow | teaches: workflow
9.2 Trunk-based development | teaches: trunk-based, short-lived-branch | needs: feature-branch
9.3 Release and hotfix branches | teaches: release-branch, hotfix-branch
9.4 A shared commit-message convention | teaches: conventional-commits, commit-type | needs: subject-line
9.5 Version numbers and release tags | teaches: semver, release-tag | needs: annotated-tag
9.6 Release notes from history | teaches: git-shortlog, changelog
9.7 Signing commits and tags | teaches: signed-commit, signed-tag | level: 2
9.8 Who must review what | teaches: codeowners | needs: code-review
9.9 Choosing a workflow for your team | teaches: workflow-tradeoffs | level: 4
9.10 Practice: running a small team project | practice | level: 3

## Part IV · Undoing and recovering

### 10 Undoing changes
10.1 Which undo do you need? | teaches: undo-map | needs: three-areas
10.2 Moving a branch back with reset | teaches: git-reset, reset-target
10.3 Soft, mixed and hard reset | teaches: reset-soft, reset-mixed, reset-hard | level: 2
10.4 Undoing a commit others already have | teaches: git-revert
10.5 Reverting a merge | teaches: revert-merge, mainline-parent | needs: merge-parents | level: 2
10.6 Restoring a file from any commit | teaches: restore-source | needs: restore-worktree
10.7 A secret was committed | teaches: secret-leak, rotate-credential | level: 4
10.8 Removing untracked files | teaches: git-clean, clean-dry-run
10.9 Reset, revert or restore? | teaches: undo-choice | level: 4
10.10 Practice: undoing changes | practice | level: 3

### 11 Recovering what seems lost
11.1 Where did my commits go? | teaches: unreachable-commit
11.2 The reflog | teaches: reflog, reflog-entry | level: 2
11.3 Undoing a bad reset | teaches: reset-recovery | needs: reset-hard
11.4 Getting a deleted branch back | teaches: branch-recovery | needs: branch-delete
11.5 Undoing a rebase | teaches: orig-head, rebase-recovery | needs: git-rebase
11.6 Saving work made on a detached HEAD | teaches: detached-recovery | needs: detached-head
11.7 What Git cannot bring back | teaches: uncommitted-loss, reflog-expiry | level: 4
11.8 Dangling commits and git fsck | teaches: git-fsck, dangling-commit | level: 2
11.9 Practice: recovering | practice | level: 3

## Part V · How Git works inside

### 12 Objects
12.1 A walk through the .git folder | teaches: git-directory-layout | needs: dot-git-folder | level: 2
12.2 Storing content by its hash | teaches: content-addressing, object-id, hash-object | level: 2
12.3 Blobs: file contents | teaches: blob, cat-file | level: 2
12.4 Trees: folders and names | teaches: tree-object, file-mode | level: 2
12.5 Commit objects | teaches: commit-object, parent-pointer | level: 2
12.6 Building a commit by hand | teaches: write-tree, commit-tree | level: 3
12.7 Annotated tag objects | teaches: tag-object | needs: annotated-tag | level: 2
12.8 Why an unchanged file costs nothing | teaches: deduplication | level: 2
12.9 SHA-1, SHA-256 and trust | teaches: sha1, sha256-transition, hash-collision | level: 4
12.10 Packfiles and deltas | teaches: loose-object, packfile, delta-compression, git-gc | level: 2
12.11 Practice: objects | practice | level: 3

### 13 Refs, HEAD and the index
13.1 What a branch is on disk | teaches: ref-file, refs-heads | needs: branch-as-pointer | level: 2
13.2 HEAD as a symbolic ref | teaches: symbolic-ref | needs: head-attached | level: 2
13.3 Remote refs and tags on disk | teaches: refs-remotes, refs-tags | level: 2
13.4 Packed refs | teaches: packed-refs | level: 2
13.5 Commands that read and write refs | teaches: rev-parse, update-ref | level: 2
13.6 Refspecs: how fetch and push map refs | teaches: refspec | needs: git-fetch | level: 2
13.7 The index file | teaches: index-file, ls-files-stage | needs: staging-area | level: 2
13.8 The index during a conflict | teaches: index-stages | needs: merge-conflict | level: 2
13.9 How status decides what changed | teaches: stat-cache | level: 2
13.10 Reset, restore and switch through the three trees | teaches: three-trees-model | needs: reset-soft | level: 3
13.11 Practice: refs and the index | practice | level: 3

## Part VI · Tools of daily professional use

### 14 Stash and worktrees
14.1 Interrupted in the middle of a change | teaches: git-stash, stash-pop
14.2 Several stashes | teaches: stash-list, stash-apply, stash-drop
14.3 Stashing untracked files and parts of files | teaches: stash-untracked, stash-patch
14.4 Conflicts when a stash comes back | teaches: stash-conflict
14.5 Turning a stash into a branch | teaches: stash-branch
14.6 What a stash is inside | teaches: stash-commit | needs: commit-object | level: 2
14.7 Getting a dropped stash back | teaches: dropped-stash-recovery | needs: git-fsck | level: 2
14.8 Two branches checked out at once | teaches: git-worktree, linked-worktree
14.9 Stash, worktree or a work-in-progress commit? | teaches: wip-commit | level: 4
14.10 Practice: stash and worktrees | practice | level: 3

### 15 Finding bugs and changes
15.1 Which commit broke it? | teaches: git-bisect, good-bad-commit
15.2 Commits you cannot test | teaches: bisect-skip, bisect-log
15.3 Letting a script do the bisecting | teaches: bisect-run, bisect-exit-codes | level: 2
15.4 Bisecting across merges | teaches: bisect-first-parent | needs: first-parent-log | level: 2
15.5 Searching the code in any commit | teaches: git-grep
15.6 Blame that sees past noise | teaches: blame-ignore-revs, blame-move-detection | needs: git-blame
15.7 The history of a few lines | teaches: log-line-range | needs: log-follow
15.8 Making history easy to bisect | teaches: bisectable-history | needs: atomic-commit | level: 4
15.9 Practice: finding bugs and changes | practice | level: 3

### 16 Configuring Git and automating with hooks
16.1 Where settings live | teaches: config-scope, config-file | needs: git-config
16.2 Settings worth changing | teaches: core-editor, pull-rebase-config, push-default
16.3 Aliases | teaches: git-alias
16.4 Different settings for work and personal projects | teaches: include-if
16.5 Per-file rules with .gitattributes | teaches: gitattributes, diff-driver | needs: line-endings | level: 2
16.6 What hooks are | teaches: git-hook, hooks-folder
16.7 A pre-commit hook | teaches: pre-commit-hook, hook-exit-code
16.8 Checking messages with a commit-msg hook | teaches: commit-msg-hook | needs: conventional-commits
16.9 Sharing hooks with a team | teaches: core-hookspath, hook-framework | level: 2
16.10 Server-side hooks and the limits of client hooks | teaches: pre-receive-hook, client-hook-limits | level: 4
16.11 Practice: configuration and hooks | practice | level: 3

### 17 Large repositories
17.1 Why big repositories get slow | teaches: repo-scale-costs | level: 2
17.2 Shallow clones | teaches: shallow-clone
17.3 Partial clones | teaches: partial-clone, blob-filter | level: 2
17.4 Checking out only part of a repository | teaches: sparse-checkout, cone-mode
17.5 Large files with Git LFS | teaches: git-lfs, lfs-pointer
17.6 Submodules | teaches: submodule, gitlink | level: 2
17.7 Working with submodules day to day | teaches: submodule-update, recursive-clone
17.8 Subtrees and monorepos | teaches: subtree, monorepo | level: 4
17.9 Keeping a big repository fast | teaches: git-maintenance, commit-graph, fsmonitor | level: 2
17.10 Removing a large file from all history | teaches: filter-repo | needs: shared-history-rule | level: 4
17.11 Practice: large repositories | practice | level: 3
