# Before handing a chapter to review

Run through this once, after `us_check.py` has no ERROR and before you add the line to `BOOK.md`. Each item is here because it is the one usually forgotten; the script cannot see most of them.

1. **Order.** Read only the first paragraph of each section in order. Does each one start from something the reader already has (the last section, or a need from the running project)? Is any term used in a section before the paragraph that defines it? Move the definition up, or the use down.
2. **Terms.** Every new term is named once, after the thing, and then never renamed. Compare with `BOOK.md` `Names:`; add any new name the next chapter will use.
3. **Pictures.** Each picture says where it stops being true, and the book's pictures (`BOOK.md` `Pictures:`) are used, not replaced by new ones for the same idea.
4. **Dangling references.** Every "§N.M", "section N.M" and "chapter N" names a section the plan has; a promise of a later section is one plain sentence, not a gap the reader needs filled now. (`us_check.py BOOK N --risks` lists the ones it can find.)
5. **The real thing is real.** Every program or session is tagged and was run once by `us_run.py`; what could not run is marked `unrun="why"` with expected output; nothing in prose describes output that the block does not show, and no answer claims what a changed program would do unless that program was run too. For `run: none` books, every principle appears inside a worked case.
6. **Check yourself** in every lesson and short section, with questions that make the reader do something; every answer hidden and explained.
7. **Tags and a finish line.** Every question and task has its `q` tag with a real idea id and an honest type (few `recall`); the project can be tested by the reader alone (`check=` or a checklist).
8. **Practice climbs.** Guided, then on your own, then a project or case with a stated finish line. Task 5 is harder than task 1.
9. **Risk notes placed.** Every version claim, default, number, quoted message, standard or vendor rule, and command that deletes or costs money carries `<!-- risk: why -->` with a specific reason; nothing carries one that the run has since settled (a doubt about an output the script then pasted) or that `PRACTICES.md` states.
10. **The case agrees with itself.** Skim only the worked case or running program through the chapter: names, times, amounts, counts and what was on the screen are the same everywhere, and nothing the text promises ("I won't use your name") is broken by a later example. Text about a figure names its boxes, never "on the left" or "left to right" (the script may turn a wide figure).
11. **Sheet updated.** Add `Left at end of chapter N:` to `BOOK.md`: the files and state the reader now has, where the running project stands, any name or picture introduced. The next chapter's writer starts from this line.
