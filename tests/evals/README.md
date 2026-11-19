# End-to-end test cases

Three learners, three kinds of subject. Each case is one prompt for a fresh agent that plays the coding agent in a
clean copy of this repository, with a scripted learner; `RUBRIC.md` is what an independent reader scores the result
against. Run them after any change to the skills or the rules:

1. `git clone` this repository to a scratch folder; start one fresh agent per case with the case file as its task
   (replace `FOLDER` with the scratch path); cap each at 20 minutes. A run takes 8 to 14 minutes and 140,000 to 190,000 tokens; a reader about 83,000.
2. Give each finished chapter to a fresh reader with `reader.md` (it names `RUBRIC.md` and the learner card).
   `routing.md` is a separate, cheap check that messages reach the right skill.
3. A change is good when no line of the last run falls and nothing in the journals blocks.

Last run, 18 November 2026 (independent readers, seven lines): Python 8.4, operating systems 8.1 (accuracy 6: one
claim about a case nobody ran; since fixed and made a rule), usability testing 8.9. The measured results and the
chapters are in [`examples/final-validation/`](../../examples/final-validation/README.md).

| Case | Kind | Learner |
|---|---|---|
| `python.md` | language | a first-year student with no programming |
| `operating-systems.md` | system | a third-year student before an exam and interviews |
| `usability-testing.md` | skill (not programming) | a design intern who must run a usability test |
| `dsa.md` | language and technique (the curriculum cards) | a student who wants to get good at contests |
| `system-design.md` | system (the curriculum cards) | a backend developer with one year of experience |
