# Repairing one passage when the reader reports a mistake

The reader found something; the chapter is already reviewed. Repair the passage they hit, keep the rest as it is, and get them back to what they were doing. A report is evidence about one place, not a reason to review the chapter again.

## Steps

1. **Find it.** `python3 scripts/us_find.py <book> 8.3 --read` for a section number, or `python3 scripts/us_find.py WORDS --book <book> --read` for a phrase they quoted. Read that section only.
2. **Reproduce it.** Before changing anything, see the fault yourself: run the program (`python3 scripts/us_run.py <chapter file> --only ID`), work the answer, follow the steps as written. If you cannot reproduce it, ask the reader one question (what they typed, which version) instead of guessing.
3. **Name the cause.** Most reports are one of four:
   - *wrong*: the text or an answer is false. Settle it as in risk-review.md (PRACTICES.md, a run, one look).
   - *lost*: something was used before it was taught. Add one plain sentence, or a pointer to the section that teaches it.
   - *different here*: their version or system behaves otherwise. Say which versions differ, and add the fact to PRACTICES.md "Facts that change".
   - *unclear*: true but too compressed. Add the missing step, not a new paragraph of everything.
4. **Repair that passage only.** Never edit pasted output; change the program and rerun it. If the repair changes a definition, find the sections that reuse the term (`python3 scripts/us_find.py TERM --book <book>`) and check only those sentences.
5. If the cause was *wrong* and the same false statement could come back in a later chapter, teach the script to watch for it: `python3 scripts/us_check.py --learn "SUBJECT" "PATTERN" "THE TRUTH" "SOURCE, DATE" --book <book>` (a short regular expression that matches the false wording and not the truth). Put a checked mark under the repaired statement.
6. `python3 scripts/us_check.py <book> N`: no ERROR. Add one line to REVIEW.md (the template's "Reader report" line). Tell the reader what changed in one line, and carry on.

## Example

Report: "§4.2 says `git switch -c` needs Git 2.23, but my answer to question 2 fails."

Weak: rewrite §4.2 in a clearer style, add a box about Git history, reorder the questions. The reader waits, the fault may still be there, and other chapters that reuse the wording now disagree.

Better: run the question's answer; it fails because the answer uses `git checkout -b` and a branch name the text never created. Fix the answer's branch name, rerun, one REVIEW.md line: "4.2 Q2 answer used an uncreated branch; fixed (reader report)". Reply: "Fixed: the answer now uses the branch `feature` from step 3."
