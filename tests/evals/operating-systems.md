You play the coding agent (for example Claude Code) that a learner has just opened inside the product "understudy". A scripted learner talks to you. Behave exactly as the product instructs. Stop when the script's last step is done, or after 20 minutes (check `date +%H:%M` now and then), whichever comes first. The work normally takes well under that: do NOT hurry, skip steps or shorten anything to save time; write at the full depth and size the product asks for.

THE PRODUCT FOLDER: FOLDER. Work only inside it (the scripts keep run folders under the system temporary folder; that is fine). Begin every shell command with `cd FOLDER &&`. Never use the shell `sleep` command. Do not install anything.

HOW TO BEHAVE:
1. A real agent has `AGENTS.md` loaded as its system prompt before the first message: read it first and treat it as your standing instructions. Skills are in `.claude/skills/<name>/SKILL.md`; a real agent sees only each skill's name and description (`head -6` of each) until the routing sends it to one. Read a skill's body only when routed to it; read a file under `rules/` or a skill's `references/` or `assets/` only when the skill tells you to, and note which ones you read.
2. Do what the skills say with the scripts they name. Do not read the scripts' source (use `--help`), nor `tests/`, `docs/`, `README.md`, `examples/` (except a sample a skill sends you to).
3. Take the learner's answers from the LEARNER CARD, in their own words. When the product hands writing or reviewing to a helper agent, play that helper yourself following its definition under `.claude/agents/`.
4. This machine is the learner's laptop. Use web search or fetch only where a skill tells you to look something up; what you read is reference only.

THE TEST'S OWN LIMITS (they override the product where they clash): plan a SHORT book (at most 6 chapters); write ONE chapter only, the first that the route names, exactly as the plan has it; then do the product's review of it; then end the session as the product says.

THE LEARNER CARD
- Kabir, third-year computer science student in Chennai. Laptop: Ubuntu, 8 GB RAM, gcc and Python 3 installed. On the 20-dollar Claude Pro plan.
- Knows C at college level (loops, functions, pointers a little), has used the terminal. Has an operating systems exam in four weeks and placement interviews after it. The syllabus: processes and threads, CPU scheduling, synchronisation, memory management, file systems. He has attended the lectures but "nothing stuck"; he can recite definitions and cannot explain what really happens.
- About eight hours a week. Wants to understand how it really works, with things he can try on his laptop.

THE SCRIPT
Message 1: "i have my operating systems exam in 4 weeks and i don't actually understand any of it. can you teach me OS properly"
Then answer what the product asks, from the card. Approve the plan it proposes ("yes, this covers my syllabus, go ahead"). When it offers to write, say "yes, start with the first chapter". If it shows a first section and asks about the voice: "yes, continue".

WHAT TO REPLY (in the message, no file; under 450 words; plain language):
A. The skills you loaded, in order, and which rules, references and assets each sent you to (file names).
B. What exists now: the book folder's files; the chapter file's path, its sections and word count; how many programs or sessions it has and how many really ran; how many risk notes the writer placed and how the review settled each; the last line of the product's check for the chapter.
C. The journal, most serious first: every command that failed or did not behave as the skill said (exact text); every instruction that was unclear, contradicted another file, or assumed a different kind of subject; anything wasteful. Say "none" where there is none.
D. Minutes used and anything cut for time.
