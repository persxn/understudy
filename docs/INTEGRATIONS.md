# Outside projects: what was taken and what was not

The owner named fourteen outside projects to study. Thirteen were found; each was cloned and read on 2026-11-16 (licence, files, the main skill text, the code where there is any). Nothing was installed and no code was run. No text or code was copied: what was taken is ideas, rewritten to fit this system's rules. One project, "Hairline", could not be found under that name.

The test for taking something: does it make a learner on a Pro account learn more per token, without adding anything that loads every session?

## Engineering quality

| Project | Licence | What it is | Decision |
|---|---|---|---|
| DietrichGebert/ponytail | MIT | A style for coding agents: the smallest complete change; reuse, then the standard library, then a dependency, then new code | **Not installed.** It is for agents that write the user's code, and this system never does (rule 4). **Taken as two things:** the rule for changing this repository (below), and a line in `us-build`: the learner's own work is judged on whether it is the smallest change that fully solves the problem and whether they reused what exists first. |
| obra/superpowers | MIT | Fourteen workflow skills for coding agents, about 22,000 words | **Not installed** (size; written for agents that write code). **Taken:** evidence before claims (system prompt rule 5: "say that something passed only after opening its output"); plan before substantial work (the book's `PLAN.md` contents page, and a chapter's spine before its first section); a subagent's report is not evidence (reviews and tests are opened and counted by the main session). |
| Graphify-Labs/graphify | Apache-2.0, parts MIT | Turns a codebase into a knowledge graph with an interactive page; depends on networkx and some 25 language parsers | **Not a dependency.** It discovers structure in unstructured code. A book here already has its structure, written down: the tree, the `needs` lists, the links. `us_index.py` turns that into a graph with no model at all. **Taken:** its model of the graph (typed nodes; edges marked as stated, `needs`, or found in the prose, `mentions`; a schema number), "ask the graph, do not read the files" (`scripts/us_find.py`: search, `--explain`, `--path`, `--read`), and the explorable map as the landing page of the reader. |

**Rule for changing this repository** (ponytail and superpowers, in four lines): reuse what a script or rule file already does before adding one; a script beats an instruction, because it costs no tokens; keep the always-loaded text at or under 2,000 tokens and each skill under 1,000 (`us_check.py --tokens` enforces both); a change is done when a fresh agent or a script has shown it working, and that output has been opened.

## Teaching

| Project | Licence | What it is | Decision |
|---|---|---|---|
| derwells/learn-skill | MIT (adapted from Jane Street's socratic-tutor, MIT) | One tutor skill with a strong reference on question craft and evidence of mastery | **Taken, the most of any project,** into `rules/teaching.md` and `rules/levels.md`: one question at a time, ending the reply; told-then-tested for things that cannot be worked out; a wrong answer gets a narrower question, then a plain explanation after two failures, then a new question; "what is X?" is not a failed attempt; check yourself before correcting the learner; only something the learner produced counts as proof; "just tell me" answers the question and earns no level; no flattery. **Not taken:** its 0 to 5 scale and its `.learning/` store (this system has five levels and `private/`). |
| adityakumar68/claude-study-skills | MIT | Four skills: tutor, explain mode, lecture map, paper breakdown | **Taken** into `rules/teaching.md`: the difference between a gap and a wrong idea, and how each is repaired; asking how sure the learner is, because sure-and-wrong is the mistake they will not catch. **Not taken:** explain mode and paper breakdown (they explain in chat; here the book explains and the tutor tests). |
| GalacticQuasar/claude-study-skills | none stated, so ideas only | A course-ingest skill that mirrors PDFs page by page, and a tutor | **Taken as an idea, written from scratch:** `scripts/us_ingest.py` copies the learner's own lectures and slides into `private/sources/` one page at a time with an index, marks pages with little text for a look at the original, and `rules/writing-modes.md` says how chapters are written from them. Kept private, never pushed. |
| YUANYINGLONG-91/lecture-notes-tutor | MIT | Page-by-page explanation of slides in chat, with emoji templates | **Mostly not taken:** it conflicts with "the book explains, the tutor tests" and with the plain style. **Taken:** read the material before teaching it; questions grounded in the material; reading `.pptx` with the standard library only (own code in `us_ingest.py`). |

## Diagrams

| Project | Licence | What it is | Decision |
|---|---|---|---|
| yizhiyanhua-ai/fireworks-tech-graph | MIT | A description file in, an SVG out, with validators; about 12,000 lines, twelve styles, animated export | **Architecture taken, code not:** description → layout by calculation → SVG whose shapes carry their role → checks → PNG. Its list of checks (arrow ends, collisions, bounds, text fit) is the basis of the checks in `scripts/us_draw.py` (`--check`). One style, not twelve. |
| wheresryan22/anatomy | MIT | Hand-built isometric explainer figures; up to an hour of agent time each; needs Node and Chrome | **Not adoptable here:** the cost per figure breaks the lean rule. **Taken:** every number in a figure comes from the truth (here: the proof or a source); look at the rendered picture at reading size, in both themes, before accepting it; "every line ends on something" as a check. |

By the owner's decision (2026-11-17) the diagram engine **ships with the product** as `scripts/us_draw.py` with `scripts/fig-style.json`, and `us-draw` uses it. This reverses the decision of 2026-11-16 to build the toolkit once on the learner's machine.

## Design of the reading page

| Project | Licence | What was used |
|---|---|---|
| persxn/jojocode-ui-skill (the owner's) | MIT | The governing design language: one accent hue drives every colour; each surface has one job (aurora behind, glass for bars and sheets, recess for things you put something into, clay only for the main action and the active state); "Read" mode for chapters, where nothing pulls the eye off the text; the motion vocabulary and its durations; measured contrast; honest empty and error states; its tokens for space, radius and type. |
| emilkowalski/skills (emil-design-eng) | MIT | When not to animate (nothing on keyboard-repeated actions such as search results), ease-out for entering, press feedback at 0.96, popovers from their origin, never from scale 0, exact transition properties. Only the main skill's outline and rule tables were read. |
| jakubkrehel/make-interfaces-feel-better | MIT | Concentric radii, tabular numbers, balanced headings and pretty paragraphs, antialiasing, 44-pixel touch targets, one stroke weight for icons with `currentColor`, no `transition: all`. |
| nutlope/hallmark | MIT | Only its outline was read (ask once, pick one direction, build, sweep). Nothing specific was taken beyond what the owner's skill already requires. |
| "Hairline" | not found | Not used. If the owner sends a link, read it and run its checks over `reader/src/`. |

Bundled in `reader/index.html`, with their licences in `reader/vendor/`: marked (MIT), highlight.js (BSD-3-Clause). The page uses the reader's own system fonts; no font is bundled.
