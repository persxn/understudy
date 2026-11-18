# Review log

- 2026-11-17 chapter 1 reviewed
- ch1 false fixed (15): 10 "line N" notes counted commands, not fence lines (1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9); config case rule (1.4); "three places at once" (1.7); init hint is 11 lines (1.4); hash length scoped (1.8); unbacked ch7 promise softened (1.4).
- ch1 stuck fixed (2): 1.3 Windows/macOS version strings carry extra words; 1.4 Check Q2 fix fails with "multiple values" if a name was already set, so the question now says no name is set yet.
- ch1 suspects: 38 shown (of 100) cleared or fixed; the 18 FLAGs are noise (commands explained in place, or used in a story or as a promise).
- ch1 open: 1.12 exercise 6 (likely 3 and 5 too) shows their output above the hidden answer, giving it away (the `answer` attribute did not move it); left for the script, not the prose.
- 2026-11-17 chapter 2 reviewed
- ch2 false fixed (3): 2.10 core.autocrlf does not make CRLF-committed files look modified (tried on 2.43; rewritten); 2.6 "every git status ... printed restore --staged" false before the first commit (§1.7 showed rm --cached); 2.11 ex 8 file is nine lines, not ten.
- ch2 stuck fixed (2): "exit code" used undefined (2.5); the skip-`cd tipcalc` advice came after the session that first needs it (2.1).
- ch2 suspects: 35 shown, all cleared (3 fixes above came from reading, not the list); the 12 FLAGs are noise ('git restore --staged' is 2.6's own term, matched as 2.7's 'git restore').
- ch2 open: none in the prose; us_index reports PLAN.md problems (not this chapter's).
- 2026-11-17 chapter 3 reviewed
- 2026-11-17 chapter 3 reviewed
- ch3 false fixed (6): 3.7 blame reads the working tree, not HEAD; 3.4 HEAD~1's diff does not end with the line Jo's began from (the shared blob ID 2097295 is the link); 3.4 macOS terminals start zsh, not Bash; 3.1 short-hash length grows with repository size, not only on a clash; 3.9 HEAD moves by itself, not "you move" it; 3.11 every practice answer showed the previous exercise's output (`answer` on markers already inside <details>): attribute dropped, stale blocks removed, rerun.
- ch3 stuck fixed (3): 3.2 and ex 9 `--author=Sam` now say to type your own name; 3.2 tip count now says to add Jo's commit to §3.1's page; 10 empty ```text boxes removed from Check-yourself answers.
- ch3 suspects: 31 shown, all cleared (blame -L/HEAD~n claims, ex 12 "prints nothing" and the 09d5c13~1 blame step re-run with us_run try); the 4 FLAGs are noise (--since/--grep taught in 3.2's idea).
- ch3 open: no commit made: book/ is ignored by the outer repo and has no repository of its own.
