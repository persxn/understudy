# Running and scoring a mock interview

Read before a mock interview of any kind. The SKILL.md gives the steps of a design session; this file gives the interviewer's behaviour, what each scored line means, and how to interview on a subject that is not system design.

## Behaviour

- Fix the time at the start (45 minutes is usual) and keep it: pacing is part of what is tested.
- Answer questions briefly and truthfully; volunteer nothing. A real interviewer does not rescue, and a rescued answer cannot be scored.
- Take notes as you go, quoting the learner's words. The score at the end must point at moments, not impressions.
- Never show your own answer during the interview. After it, the two strongest and two weakest moves, each with the section (`§N.M`) that would have helped.

## The scored lines (system design)

Score each 1 to 4 in one line, with the moment that earned it.

| Line | 4 looks like | 1 looks like |
|---|---|---|
| requirements | asks who uses it, how much, what must never fail, before drawing | starts drawing boxes |
| assumptions | states numbers and says which would change the design | hides them, or has none |
| reasoning | each box exists because a requirement needs it | boxes from a familiar diagram |
| trade-offs | names what each choice gives up | "this is the best way" |
| scale | rough arithmetic leads to where the bottleneck is | "we can add servers" |
| reliability | says what fails first and what the user sees | assumes nothing fails |
| security | who may do what, where data is exposed | not mentioned |
| communication | the interviewer could redraw the design from their words | the interviewer had to guess |
| depth | goes deep on one part when asked | stays at boxes |

Weak line: "communication: good". Better: "communication 2: at minute 20 the queue appeared without saying what it was for; I had to ask."

## Interviews on other subjects

"Interview mode for other topics" uses the same behaviour with the questions that field's interviews really ask, drawn only from chapters the learner has at level 2 or above. Score the lines that fit the field, replacing those that do not.

- A usability researcher: a portfolio walk-through ("why five participants? what did you drop and why?") and a case ("the team wants to test a redesign next week; plan it aloud"). Lines: framing the question, method choice, participants, avoiding leading, turning findings into decisions, communication.
- An operating-systems or networking interview: "walk me through what happens when…" questions. Lines: order of events, which part knows what, failure cases, precision of terms, communication.

## After the interview

Write the file in `private/interviews/` as the SKILL.md says, with the scored lines. A line scored 1 or 2 twice across interviews goes in `private/weaknesses.md` with its section.
