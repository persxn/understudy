# The book pass: one read across chapters

Do it when `python3 scripts/us_plan.py status <book>` says "book pass due" (the last chapter of a part has been reviewed), and at the end of a book. Each chapter was reviewed alone; nobody has yet looked at whether the chapters agree with each other. Scripts check what can be checked by rule. This pass is for what needs a reader, and it reads a digest, never the chapters.

## 1. Let the script go first

```text
python3 scripts/us_check.py <book>             every chapter: fix each ERROR; read each FLAG
```

Across chapters it flags a term that two ideas claim, a chapter that uses nothing from earlier ones, a checked passage that has since changed, and a statement that matches a known mistake. It notes a section that says it needs an idea and never uses it. Settle these first; most need one small edit.

## 2. Read the digest, once

```text
python3 scripts/us_check.py <book> --digest --from A --to B
```

At most 3,500 words: the book's sheet; for each chapter its ideas with the sentence that defines each, its checked facts, every sentence that points to another chapter, and what it left behind. Hunt for five things:

1. **Two definitions that disagree.** "A branch is a pointer to a commit" in chapter 3; "a branch is a copy of your files" in chapter 6. Keep the true one; make the other refer back.
2. **One fact stated two ways.** A default, a limit or a version that differs between chapters. `PRACTICES.md` decides; if it is silent, settle it as in `risk-review.md` and add it there.
3. **A promise not kept.** "Chapter 6 shows how" when chapter 6 does not. Either the later chapter gains one honest paragraph, or the promise becomes one plain sentence.
4. **A name that drifted.** The project folder, a file, a person or a picture that `BOOK.md` fixes and a later chapter calls something else.
5. **A later chapter teaching again** what an earlier one taught, instead of building on it.

## 3. Repair only what you found

Open a chapter only at the passage a finding names (`python3 scripts/us_find.py <book> N.M --read`). Make the smallest edit that makes the chapters agree; rerun a program if one changed (`us_run.py <chapter file> --only ID`). Do not restyle and do not read further.

## 4. Record it

One block in `REVIEW.md` headed `## Book pass: chapters A to B`, a line per finding and what changed (or "none found"). Then `python3 scripts/us_check.py <book>` with no ERROR, `python3 scripts/us_plan.py mark <book> pass B`, `python3 scripts/us_index.py <book>`, commit inside `book/`.

**Weak pass:** re-reading every chapter "to be sure". That is five reviews for the price of the book again, and the differences between chapters are exactly what a chapter-by-chapter read misses.

**Better:** the digest puts chapter 2's definition of a list beside chapter 5's; they disagree on whether a list can change; one sentence in chapter 5 is fixed. Ten minutes for a part.
