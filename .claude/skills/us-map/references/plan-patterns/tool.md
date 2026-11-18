# Plan pattern: a tool

For Git, Docker, a shell, Terraform, kubectl, Make. Header: `run: console`, `kind: tool`; the other header lines (`state:`, `timeout:`, `check:`, `mask:`, `env:`) are in `rules/tool-books.md`, read it too.

## The shape

- **Chapter 1** installs the tool from its maker's own source, gets a first success by the second section, and meets the day-one failures (permissions, a service not running, no network).
- **Chapters 2 to 4: the everyday cycle**, the 20% of commands used 80% of the time, on the running project.
- **Then the model of state**: what the tool keeps where and what each command changes (Git's three areas, Docker's images and containers, Terraform's state file). Placed after first use, so the picture explains something the reader has already seen.
- **Then working with others**, configuration, automation, and **undo and recovery** (a whole chapter: it is what people search for in a panic). Internals last, at level 2.
- **Carried through:** one small real project the tool acts on. Fix the downloads (images, providers, versions) in chapter 1 and reuse them.
- **Practice:** one break-it-and-fix-it task per chapter, on the project.

## What weak plans miss

A picture of state (commands become spells); undo; what costs money or deletes (Terraform `destroy`, `docker system prune`); configuration files; reading the tool's own error messages. Weak plans also follow the manual page: one section per flag, alphabetically.

## Sample

Weak: `3.4 terraform state commands | teaches: state-commands`. Better:

```text
### 3 State: what Terraform remembers
3.1 Why plan knew what already existed | teaches: state-file, resource-address | fig
3.2 Reading state with list and show | short | teaches: state-list, state-show
3.3 Drift: someone changed it by hand | teaches: drift, refresh-only-plan
3.4 Remote state and locking for a team | teaches: remote-backend, state-lock | level: 2
3.5 Renaming without destroying | teaches: moved-block | needs: resource-block | level: 2
3.6 Bringing existing resources under Terraform | teaches: import-block
3.7 Secrets end up in state | short | teaches: sensitive-in-state | level: 4
3.8 When it goes wrong: a stuck lock, a state that will not load | teaches: force-unlock, state-errors | needs: terraform-plan
3.9 Practice: break it and fix it, a plan that wants to destroy the bucket | practice | level: 3
```

The chapter is about what the tool remembers, not about the `state` subcommand: renaming without destroying and secrets in state are the two things that hurt teams in production.
