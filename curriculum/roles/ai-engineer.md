# ai-engineer: mid-level applied AI engineer: product features on models, not research
status: reviewed 2026-11-19 by independent agent, sources reopened
sources: read 2026-11-19: handbook.gitlab.com ML engineer; AWS GenAI Developer Pro guide (no training);
  adverts: GitLab 2026-05-29*, Glean Evals 10-23, Atomicwork, Distyl 06-18*, Fieldguide, Ro, Rillet 08-25,
  Onit, Employ, Version 1 05-19, SAI, Impiricus 01-09 (*closed); 3 reopened 11-19; Capco (open 11-18), Jolera
unverified: 6 of 12 senior, 3 evals roles; essential 7+, desirable 3-6 or an essential line's need; levels

| Subject | Level | Class | At work it looks like | Proved by |
|---|---|---|---|---|
| python-core | 3 Build | essential | Python (12 of 12) | tested service |
| llm-application-engineering | 3 Build | essential | evals, agents (11 of 12) | eval report |
| retrieval-systems (planned) | 2 Explain | essential | RAG (10), vector stores (7) | recall@k measured |
| api-design | 3 Build | essential | backend APIs (10 of 12) | retry-safe API |
| reliability-and-observability | 3 Build | essential | tracing (9 of 12) | cost traced, alert |
| system-design-foundations | 2 Explain | essential | system design (7 of 12) | costed design |
| github-actions-ci-cd | 3 Build | desirable | CI/CD (6 of 12) | evals gate merges |
| git | 3 Build | desirable | Git (Capco, Atomicwork) | PRs reviewed |
| llm-fine-tuning (planned) | 2 Explain | desirable | fine-tuning (5, a plus) | choice defended |
| cloud-core-services (planned) | 1 Use | desirable | a cloud (5 of 12) | managed deploy |
| typescript | 3 Build | desirable | TypeScript (5 of 12) | typed client |
| sql-and-relational | 3 Build | desirable | SQL (4 of 12) | traces queried |
| docker | 3 Build | desirable | containers (3 of 12) | service image |
| model-serving-and-mlops (planned) | 1 Use | desirable | serving (3 of 12) | open model served |
| machine-learning-fundamentals | 2 Explain | desirable | classical ML (2 of 12; Jolera) | baseline beaten |
| networking-basics | 2 Explain | desirable | api-design needs it | call traced |
| caching-and-queues | 2 Explain | desirable | queues (2); api-design needs it | retry-safe worker |
| deep-learning-with-pytorch (planned) | 1 Use | specialist | PyTorch (2 of 12) | network trained |

## Order and time
python-core, llm-application-engineering, retrieval-systems, networking-basics, sql-and-relational,
system-design-foundations, caching-and-queues, api-design, reliability-and-observability; the rest by needs,
some off this list (linux-command-line 20 h, javascript 60 h). Essential 200 h, desirable 320 h.

## Interview checks
- Design an LLM feature (system-design-foundations; Jolera).
- Did it get better? (llm-application-engineering; Distyl, Glean).
- RAG or fine-tuning? (retrieval-systems, llm-fine-tuning; GitLab).
- Prompt injection (llm-application-engineering; GitLab, Onit).

## Capstone
The learner's product answers from its documents with citations, behind a traced API. Finish: one command
prints pass rate per category against a baseline; a worse change fails CI; an injected document triggers no tool.

## Overlap
backend-engineer: most essential lines; ML engineer: PyTorch, serving.
