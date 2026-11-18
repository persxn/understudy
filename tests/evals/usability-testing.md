You play the coding agent (for example Claude Code) that a learner has just opened inside the product "understudy". A scripted learner talks to you. Behave exactly as the product instructs. Stop when the script's last step is done, or after 20 minutes (check `date +%H:%M` now and then), whichever comes first. The work normally takes well under that: do NOT hurry, skip steps or shorten anything to save time; write at the full depth and size the product asks for.

THE PRODUCT FOLDER: FOLDER. Work only inside it (the scripts keep run folders under the system temporary folder; that is fine). Begin every shell command with `cd FOLDER &&`. Never use the shell `sleep` command. Do not install anything.

HOW TO BEHAVE:
1. A real agent has `AGENTS.md` loaded as its system prompt before the first message: read it first and treat it as your standing instructions. Skills are in `.claude/skills/<name>/SKILL.md`; a real agent sees only each skill's name and description (`head -6` of each) until the routing sends it to one. Read a skill's body only when routed to it; read a file under `rules/` or a skill's `references/` or `assets/` only when the skill tells you to, and note which ones you read.
2. Do what the skills say with the scripts they name. Do not read the scripts' source (use `--help`), nor `tests/`, `docs/`, `README.md`, `examples/` (except a sample a skill sends you to).
3. Take the learner's answers from the LEARNER CARD, in their own words. When the product hands writing or reviewing to a helper agent, play that helper yourself following its definition under `.claude/agents/`.
4. This machine is the learner's laptop. Use web search or fetch only where a skill tells you to look something up; what you read is reference only.

THE TEST'S OWN LIMITS (they override the product where they clash): plan a SHORT book (at most 6 chapters); write ONE chapter only, the first that the route names, exactly as the plan has it; then do the product's review of it; then end the session as the product says.

THE LEARNER CARD
- Ananya, final-year design student in Pune starting a product design internship at a food-delivery startup in three weeks. Laptop with a browser; she uses Figma. On the 20-dollar Claude Pro plan.
- Her manager wrote: "in your first month you will plan and run usability tests on our new checkout prototype and report what you find". She has never run one. She knows what a prototype is; she does not know how to write tasks, how many people to test with, what to say during a session, or how to turn notes into findings.
- About six hours a week. Wants to practise on a real thing; she has a clickable checkout prototype of her own from a college project.

THE SCRIPT
Message 1: "i need to learn how to run usability tests before my internship starts, i've never done one"
Then answer what the product asks, from the card. Approve the plan it proposes ("this looks right, go ahead"). When it offers to write, say "yes, the first chapter please". If it shows a first section and asks about the voice: "yes, continue".

WHAT TO REPLY (in the message, no file; under 450 words; plain language):
A. The skills you loaded, in order, and which rules, references and assets each sent you to (file names).
B. What exists now: the book folder's files; the chapter file's path, its sections and word count; how many programs or sessions it has and how many really ran; how many risk notes the writer placed and how the review settled each; the last line of the product's check for the chapter.
C. The journal, most serious first: every command that failed or did not behave as the skill said (exact text); every instruction that was unclear, contradicted another file, or assumed a different kind of subject; anything wasteful. Say "none" where there is none.
D. Minutes used and anything cut for time.
