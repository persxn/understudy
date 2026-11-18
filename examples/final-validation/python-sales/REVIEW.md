## Chapter 1: Running your first program

- Risks: 7 items (7 marked, 0 destructive, 0 unrun, 0 dangling). Settled: 1 by PRACTICES.md (Ctrl+D), 1 run (NameError "Did you mean" and ^ underline, seen in day_total_typo on 3.13), 1 one look (Ubuntu 24.04 python3 is 3.12.3, packages.ubuntu.com/noble/python3), 3 known for certain (Ctrl+Alt+T, Text Editor on 24.04, missing `python` command, already worded "something like"), 1 reworded (1.5: "every spreadsheet" narrowed to Excel and LibreOffice Calc).
- Fixed: 1.5 the floating-point claim now names Excel and LibreOffice Calc instead of "every spreadsheet"; PRACTICES.md Ubuntu Python fact now has its source and date instead of [unchecked].
- Open: 1.6 teaches SyntaxError, which the plan does not list for 1.6 (useful, kept; plan may add the id). 1.2 to 1.5 sit just under 1,200 words (NOTE only).
- Score 9: accuracy 9, depth 8, clarity 9, sequencing 9, practical 9, exercises 9, completeness 9, efficiency 8. Lowest: 1.2 and 1.5 slightly thin on change-one-thing walks.
- 2026-11-18 chapter 1 reviewed; open: 1.6 SyntaxError taught outside the plan

## Chapter 1: Running your first program (second full pass)

- Risks: 0 items (0 marked, 0 destructive, 0 unrun, 0 dangling); us_check showed no ERROR before and after.
- One read: 3 case, 3 order, 2 page, 0 words, 0 repeats fixed.
- Fixed: 1.3 the reader was never told to save `day_total_labels.py`, which 1.3's Check yourself and 1.4 then use; it now says to save it under that name. 1.4 opening said `day_total.py` printed the total and the average (only `day_total_labels.py` does); it now names `day_total_labels.py`. 1.4 `names_first.py` and `no_recalc.py` are used by name later (1.4 When it goes wrong, 1.7 Task 3) but were never named; the text now names them where they appear. 1.6 "Here is `day_total.py` with one small slip" named a file that is not the program shown (the traceback says `day_total_typo.py`); it now names `day_total_typo.py`. 1.6 prose quoted `File "...day_total_typo.py"`, which the shown traceback does not print; the `...` is gone. 1.6 When it goes wrong said "line 5 is fine" for a name used too early, but no such example has line 5; it now says "the line it points at". 1.5 Check yourself 3 quoted `65.30000000000001`, a number no example produced; it now quotes `30.299999999999997` from float_surprise.
- Open: 1.6 teaches SyntaxError outside the plan (as before). 1.5 Check yourself 2 (`45075`) and 1.7 Task 5 (`45012075`) are the same exercise, and the `shop = Sharma` NameError appears in both 1.5 and 1.6; left, as 1.7 and 1.6 build on them. 1.1 prompt example is `riya@laptop` while shown paths say `/home/you/`; left, both are framed as examples. 1.2 and 1.5 just under 1,200 words (NOTE only).
- Score 9: accuracy 9, depth 9, clarity 9, sequencing 8, practical 9, exercises 9, completeness 9, efficiency 8. Lowest: 1.3/1.4 programs used by file name before the reader was told to save them (fixed in this pass).
- 2026-11-18 chapter 1 reviewed; open: 1.6 SyntaxError taught outside the plan; 1.5/1.7 repeated strings-joined exercise
