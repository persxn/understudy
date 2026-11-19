# Reviewing a curriculum file

For the agent that reviews a file somebody else built. A file is `reviewed` only by an agent that did not write
it. Your job is to find what is wrong, missing or unproven, repair it, and record what you did. Read `FORMAT.md`
first. You are the last check before every future learner's planner trusts this file.

## The checks, in order

1. **Sources.** Open every source the file lists. Does it say what the file uses it for? Remove a source you
   cannot open or that does not support the use; add the page that does. Anything named in the file (a problem,
   a tool, a book chapter, a page) must exist: open it or delete the name.
2. **Truth.** Read every statement as a claim. Each "wrong belief" must be a belief people really hold, and its
   bracketed truth must be exactly right, with no exception left out. Each "failure to diagnose" must be real and
   something a learner can make happen. Where a claim can be run on this machine, run it (use /tmp). A claim you
   cannot confirm is reworded to what is certain, or removed, or listed on the `unverified:` line.
3. **Order.** Would a strong practitioner teach it in this order? Does any step use something a later step
   teaches? Is anything essential to the promise missing? Is anything there that the promise does not need?
   In a track map: does every subject come after what it needs, and is the reason for each jump stated?
4. **Depth where it matters.** "Go deep" names the two or three things that separate someone who can use the
   subject from someone who understands it. If it names something minor, fix it.
5. **The ladder.** Each of the four tasks is something a learner does and a third person could judge. No
   "understands".
6. **Nothing perishable.** No version numbers, prices, defaults or install commands; no statistics without a
   source; no judgement dressed as fact (hours and practice counts are judgement: say so on `unverified:`).
7. **Agreement.** The card's `needs` match the maps; two cards do not teach the same thing; a role's levels are
   reachable from the cards' ladders.
8. **Can a planner and a writer use it?** Read `.claude/skills/us-map/references/from-a-card.md`. For three
   steps, write in your head the lesson a writer would produce from the step and the notes tagged to it. Where
   you would have to guess what is taught or how deep, the step is thin: add the missing decision.
9. **Made for this subject.** Cover the title and read the steps. Could they be the steps of another language,
   tool or field with the names swapped? A step that survives the swap ("Basics", "Core concepts", "Advanced
   features", "Best practices", "Project") is rewritten to name the real constructs, commands, problems,
   protocol messages or numbers of THIS subject, or removed. The kind's own part must hold things only this
   subject has. No card supplies a running example: the case is always the learner's own.
10. **Complete against two outlines.** Name two independent, respected outlines of the subject that you opened
   (the official documentation's contents, a standard textbook's chapter list, a well-known course or guide).
   List what they cover that the card neither teaches nor names under "leave for later". Each gap is fixed or
   recorded in `REVIEWS.md` with the reason it is left out.
11. **Prerequisites, step by step.** For each step ask: what must the learner already know to follow it? It is an
   earlier step or a `needs:` card, or the card has a hole: fix it. A step tagged on a note must be the step
   that really teaches the thing.
12. **Tags.** Every wrong belief, failure and word sits on the step that teaches it. A word nobody would teach
   in that step is moved or removed; a step with no word and no wrong belief is either trivial (merge it) or
   under-described (add what it needs).
13. **Every `Show:` is real.** Run each one again yourself, or reopen the source it names. What the card says
   happens is what you saw (a timing may differ by machine: the card must then give an order of magnitude, not
   your stopwatch). An experiment that does not reliably surprise, that needs more than a chapter can hold, or
   that would only work on the writer's machine is replaced by one that does better.
14. **Need, Explain, Try.** `Need:` is a question a learner really asks at that moment, not a syllabus heading
   with a question mark. `Explain:` is correct, is the mechanism and not a definition, and can be said in a
   breath. Each `Try:` task has a type and a finish line, cannot be done by rereading the lesson, and one of them
   grows from a real failure.
15. **Depth is decided, and decided well.** The deep steps are the ones a strong practitioner would spend the
   hours on. Step 1 is small and whole and already touches the card's deepest idea. No step owns more than five
   words (step 1: four); a word in brackets really is incidental there; every word is owned at exactly one step.
   A step line that still reads as a list of six topics is slimmed, its detail moved into the notes.
16. **Believable numbers.** A card whose chapters will invent cases with quantities carries the orders of
   magnitude that keep them believable, each run or sourced, dated where it ages.
17. **Each goal block makes a book** (track maps). Run `python3 scripts/us_path.py goal <track> <n>` and read the
   output as that learner's planner: can chapter 1 do what "Open with" says from the steps it names? Do the
   "Deep" steps deserve a chapter each for this goal? Does "Order" bring what such a learner asks for by name
   into the first half? Are the hours the Hours column scaled by steps? Could a strong, complete book be made
   from exactly these steps in this order, with nothing assumed that no step teaches?
18. **Size and form.** `python3 scripts/us_path.py check` has no ERROR for the file, and you have read its notes.
   Over a limit: cut what teaches least.

## Then record and mark

Add a block to `curriculum/REVIEWS.md`:

```text
## cards/dsa-core-techniques.md, reviewed 2026-11-18
- Sources opened: ... (each with what it confirmed)
- Outlines compared: ... (the two outlines, and each gap fixed or left with its reason)
- Run: ... (what was run and what it showed)
- Changed: ... (each change and why)
- Still unverified: ...
```

Then `python3 scripts/us_path.py mark <id or path> reviewed --by "independent agent, sources reopened"`.
If a file is too weak to repair in place, do not mark it: say so in `REVIEWS.md` and in your reply.
