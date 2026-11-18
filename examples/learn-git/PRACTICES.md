# Git practices worth teaching

Sources read 2026-11-17 as reading material only:
- [Pro Git] the official book, git-scm.com/book/en/v2 ("Contributing to a Project", "Rebasing")
- [git-push] the official reference page, git-scm.com/docs/git-push
- [CC] Conventional Commits 1.0.0, conventionalcommits.org (CC BY 3.0)

1. Make each commit one logically separate change; use `git add --patch` to split edits that share a file. [Pro Git, 2026-11-17]
2. Run `git diff --check` before committing, so no whitespace errors go in. [Pro Git, 2026-11-17]
3. Write a summary line of about 50 characters or fewer, then a blank line, then a body that says why the change was made and how it differs from before. [Pro Git, 2026-11-17]
4. Write the summary in the imperative: "Fix bug", not "Fixed bug" or "Fixes bug". [Pro Git, 2026-11-17]
5. Do not rebase commits that exist outside your repository and that people may have based work on. [Pro Git, 2026-11-17]
6. When you must replace history you already pushed, use `git push --force-with-lease`, not `--force`: it refuses if someone else has pushed in the meantime. Fetches running in the background weaken that protection. [git-push, 2026-11-17]
7. In a team that adopts a convention, write `<type>[optional scope]: <description>`; `fix` patches a bug, `feat` adds a feature, and `BREAKING CHANGE:` in a footer, or `!` after the type, marks an incompatible change. [CC, 2026-11-17]
8. Tie version numbers to those types: `fix` is a patch release, `feat` a minor one, a breaking change a major one. [CC, 2026-11-17]
