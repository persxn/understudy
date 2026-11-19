# Private files

Everything about the person lives in `private/`. It is never pushed and never copied into `book/`. Keep each file short: current state, not history. Everything the learner has done lives in these files and in `book/`, never only in a conversation, so a month away loses nothing.

| File | Holds | Size |
|---|---|---|
| `now.md` | where the last session stopped; the `Next:` line is set with `python3 scripts/us_resume.py --next "..."` | five lines |
| `RESUME.md` | written by `python3 scripts/us_resume.py`: where they are, what to do with no AI, weak spots, the sentence to start with when they are back. Never by hand | |
| `practice.json` | written by `python3 scripts/us_practice.py`: every offline answer to a Check yourself question (book, section, box, due date, history). Read it; never edit it | |
| `machine.md` | written by `python3 scripts/us_doctor.py`: the measured machine and any `- blocked:` line with its cure; under "Told by the learner", what they said (internet, usage plan, how they learn), kept when the script runs again | under 20 lines |
| `goal.md` | see the template below | under 20 lines |
| `route.md` | the current route: books and chapters in order (`learn-git 3`), the reason for each in a few words, `skip` on chapters placement showed they already have; a chapter taken by section names them (`- learn-docker 1 sections 1.2 1.5`); what was left off, at the bottom | one line per chapter |
| `levels.yaml` | `learn-git/3: {level: 2, state: proven, checked: 2026-11-16, next: 2026-12-20}` (book/chapter); `state` is `claimed`, `in progress` (answers logged by `us_practice.py record`, no check passed yet) or `proven` | one line per chapter |
| `learner.md` | written by `python3 scripts/us_practice.py`: wrong beliefs that keep returning, weak foundations, what they can explain but not yet apply, what is solid, projects passed alone. Read it at the start of a lesson; never edit it | fifteen lines |
| `weaknesses.md` | weak spots that keep returning, each with the section (`§N.M`) it belongs to | under 30 lines |
| `week.md` | this week's plan, including the share for algorithm practice that the learner chose this week | under 20 lines |
| `standard.md` | progress on the engineer standard (only if it applies) | one line per item |
| `build.md` | the project in progress: its folder, which step it is at (explore, plan, build, check, report), who writes the tests at this stage, open review points | under 15 lines |
| `autopilot.log` | written by `python3 scripts/us_autopilot.py`: one line per step | |
| `sources/` | the learner's own lectures and slides, copied by `python3 scripts/us_ingest.py` | |
| `interviews/` | one short file per mock interview: problem, what went well, what did not | |
| `compete.md` | contest handle, rating, recent contests, problems to upsolve, recurring mistakes | under 40 lines |
| `logs/` | the learner's own work log, one file per month | |

`goal.md` template (keep these labels):

```
goal: I can ...                      # one sentence
in their words: ...
deadline: none | 2027-01-10
hours a week: 4
engineer standard: off | on
progress card: off | on
already has: ...                     # what they say they can already do
```

Rules:

- Read only the file the current job needs.
- Rewrite files in place. Do not append a running history; move old detail into `logs/` only if the learner wants it kept.
- At the end of every session: `python3 scripts/us_resume.py --next "..."` once. It sets `now.md` and rebuilds `RESUME.md`, so that is true if they do not come back for a month.
- `book/progress-card.json` is public and optional. Create or update it only when the learner has switched it on in `goal.md`. It holds levels reached, projects shipped and contest rating. Nothing else.
