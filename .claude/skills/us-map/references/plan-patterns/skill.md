# Plan pattern: a professional skill

For writing, design, testing, research, managing work, interviewing, analysis: practice that is not programming. Header: `kind: skill`, and `run: none` unless the skill is practised with a computer (solving contest or interview problems, estimates for a system design): then `run:` names the language and the cases are carried by real programs. A skill trained on problems (contests, interviews) has no cycle to walk: its chapters are techniques, each going from the slow sure solution to the technique that beats it, and chapter 1 takes one whole problem from statement to accepted.

## The shape

- **Chapter 1 does the whole practice once, small**, on one case from start to end: one usability test with one person and one task; one how-to guide of one page tested on one colleague. The reader sees the cycle before any phase is deepened.
- **Then one chapter per phase of the practice's own cycle**, in the order it is done (plan, prepare, do, analyse, report, improve), then the hard situations (a hostile stakeholder, no budget, a team of ten) and the practice in an organisation.
- **Every chapter has a worked case**: a weak version, a better one, and the reasons. Theory and history come only where they explain why the practice exists.
- **Carried through:** one fictional case (a product, a team, a client) used in the lessons, and the reader's own material in practice.
- **Practice:** do it on your own material, then judge it against a checklist the chapter built; the project is a real piece of work.
- **Judgement is the level-4 content:** when to break the rule, which of two good options fits.

## What weak plans miss

A cycle (tips in no order instead); worked cases; criteria to judge the result; failure modes and how they show; ethics, consent and law where they apply (recording a participant, quoting a source); working with others, since most of these skills are exercised in a team.

## Sample

Weak: `3.1 Tips for clear writing` (a list, nothing to do, nothing to judge). Better:

```text
### 3 Writing a how-to guide
3.1 The guide nobody could follow | story
3.2 Who is reading, and what they are trying to do | teaches: reader-goal, task-orientation
3.3 Tutorial, how-to, reference or explanation? | teaches: documentation-types | level: 2
3.4 Prerequisites and the starting state | teaches: prerequisites-block
3.5 Steps: one action each, with the result to expect | teaches: numbered-step, expected-result
3.6 Warnings where the danger is | short | teaches: inline-warning
3.7 When a step fails: a troubleshooting note | short | teaches: troubleshooting-note
3.8 Testing a guide on someone new | teaches: guide-usability-test | level: 3
3.9 Practice: rewrite a real how-to from your own team | practice | level: 3
```

It follows the order the work is done in, and ends by testing the guide on a reader, the one step that tells the writer the truth.
