# Routing check (a small, cheap model is enough)

Give a fresh agent only `AGENTS.md` and the first five lines of each `.claude/skills/*/SKILL.md`, then these
messages; it names the one skill it would load first. `book/` and `private/` exist unless said.

| # | Message | Expected |
|---|---|---|
| 1 | "hi! i want to learn python" (no `book/`, no `private/`) | us-start |
| 2 | "can you write me the chapter on negotiation tactics for salary talks" | us-write |
| 3 | "what order should I learn accounting topics in? give me a syllabus" | us-map |
| 4 | "i don't get why a page fault happens, explain it" | us-teach |
| 5 | "quiz me on chapter 2 of my usability testing book" | us-teach |
| 6 | "draw me a diagram of how a TCP handshake goes" | us-draw |
| 7 | "section 3.2 says five users find 85% of problems, I think that's wrong" | us-review |
| 8 | "I'm writing the test plan for my internship's checkout prototype and I'm stuck on the tasks, can you look at it" | us-build |
| 9 | "can you just write my Dockerfile for me" | us-build |
| 10 | "let's do a mock system design interview" | us-design |
| 11 | "what's the capital of Australia?" | none |
| 12 | "i have 2 weeks left before my exam now, not 4, change the plan" | us-start |
| 13 | "make me a one page cheat sheet for git" | us-write |
| 14 | "give me a codeforces style problem on binary search" | us-compete |
| 15 | "what should i do next?" | us-start |
| 16 | "I need to learn how to read a balance sheet for my new job" (no book on it) | us-start or us-map |
| 17 | "review chapter 4 of my docker book" | us-review |
| 18 | "here are my lecture slides on thermodynamics, turn them into notes" | us-write |

Last run, 18 November 2026 (Haiku): 18 of 18.
