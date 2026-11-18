# Coming back

Read when a learner returns after a break of more than a few days, or says they forgot where they were. Everything they did is in local files, so nothing is lost; the job is to make the first minutes back easy and true.

## Order of the first reply

1. Run `python3 scripts/us_resume.py`, read `private/RESUME.md`, run `python3 scripts/us_practice.py --stats`. Trust the files over your memory of earlier sessions and over `now.md` if they disagree.
2. Two lines: where they stopped and what is next. Name the section (`§N.M`), not "the next topic".
3. Weak spots first, then sections practised offline. Offer one quick spoken check on each practised section (one question in their words, one new case), not a full test: they earned it, and a full test after a break feels like punishment.
4. Stop and wait. The learner chooses.

Do not re-teach anything before they ask; rusty is not lost, and one surprise question tells you more than a summary.

## After a long break (a month or more)

- Ask once whether the goal or deadline changed. A changed goal goes to `us-map` to rebuild the route; everything proven is kept.
- Expect several chapters past their `next` date. Offer one short session on those, weakest first, instead of continuing the route as if nothing happened.
- Check that the machine still works: run `python3 scripts/us_doctor.py` and say any `- blocked:` line.

## Example

> **You:** You stopped in §4.3, writing interview questions for your study, and the next step is §4.4, running a pilot session. Offline you answered §3.2 and §3.5 right; §4.1 (choosing participants) is a weak spot. Shall we start with one question on §4.1, or go straight to the pilot?

Weak version: "Welcome back! Last time we covered a lot. Ready to continue?" It says nothing they can act on and hides the weak spot.
