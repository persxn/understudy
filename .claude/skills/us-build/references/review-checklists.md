# Review checklists

Read when reviewing any piece of the learner's work. Use the list for its kind, and the habits list for every kind. Point at each problem with where it is and what it would cause; never repair it. Report the two or three that matter most first: a review of twenty small points teaches nothing.

## Habits (every kind)

- Did they read what exists before making something new?
- Is it the smallest change or piece that fully does the job?
- Did they check it, and show the result, not just say it passed?
- Did they say honestly what they did not check?

## Code

- Does it do what the brief asked, including the empty, the largest and the wrong input?
- Do the tests fail when the code is broken? (Break one line and run them.)
- Did they reuse their own code and the standard library before adding a dependency?
- Can someone else read it: names, one job per function, no dead code?
- Errors: handled or reported, never silently swallowed.

## Deployment or set-up

- Does it come up from nothing, with only the documented steps?
- Secrets kept out of files that are shared; ports and permissions no wider than needed.
- What happens when it restarts, or the disk fills?
- Is there a teardown, and does it leave nothing paid for running?

## Document

- Who reads it, and what do they do after? Is that clear on the first page?
- Is every claim backed by something the reader can check?
- Does each section earn its place, or repeat another?
- Would the intended reader understand every term?

## Design

- Walked through the main case, a rare case and a failure?
- Every choice with its reason and what was given up.
- What it costs to change later, and where it is hardest to change.

## Study

- A question that the method can actually answer.
- Participants or data that fit the question, with how they were chosen.
- Each finding tied to evidence; anything that contradicts it reported, not dropped.
- Limits said plainly.

## Plan

- Every step has an owner and a date, and the dependencies between steps are visible.
- The riskiest step is named and has a fallback.
- One realistic delay: does the end date still hold?

## Example (a study)

Weak review: "Looks good, maybe add more participants." Better: "Finding 3 says users trust the price. In two of your five sessions, users asked whether shipping was included. What does that do to finding 3?"
