# The engineer standard

Applies only when `private/goal.md` says the goal is to become an engineer. A small goal stays small; its work still counts here. Track progress in `private/standard.md`, one line per item.

| # | Requirement | Counts when |
|---|---|---|
| 1 | **Design ladder** component → module and interface → application → database and API → distributed → infrastructure → scale and reliability → production → large scale | each rung defended in a `us-design` session; a rung opens only when its foundations are at level 2 |
| 2 | **Three open-source studies** of substantial projects in the learner's field | each has: why chosen, architecture, folder tour, key modules, traced execution paths, interfaces, testing/logging/config/errors, trade-offs, one small change or contribution. Pinned to a commit. Written up in `book/projects/` |
| 3 | **Five end-to-end cloud projects**, each harder than the last, at least one with a pipeline of several AI services | planned, designed, built by the learner, tested, deployed, monitored, documented, published; architecture defended. Local-only passes show as "not yet deployed" |
| 4 | **Cloud path from foundations** virtualisation, networking, compute, storage, identity, DNS, load balancing, containers, orchestration, serverless, databases, object storage, CDNs, infrastructure as code, CI/CD, monitoring, security, high availability, disaster recovery, cost | their chapters at level 2, principles before any provider's buttons |
| 5 | **Failure drills** on things the learner owns, isolated and reversible | for each sizeable project: break it on purpose, diagnose, recover, write a postmortem |
| 6 | **Mock design interviews**, recurring | requirements, estimates, a hand-drawn design, challenges, changed requirements, failures, revision. Recorded in `private/interviews/` |
| 7 | **Case studies** of systems the learner cannot yet build | read, components named, trade-offs explained, a simplified version reproduced |
| 8 | **Outage stories** | the ten questions answered; "what would you have done"; a safe small recreation where possible |
| 9 | **Classics and papers** for the field | read with a guided plan; the learner explains the problem, the idea and its influence |
| 10 | **Vocabulary** | terms used correctly without prompting, checked by surprise questions |
| 11 | **Boring details** | in every book: investigations done from docs, logs, experiments and source |
| 12 | **Agent literacy** how language models and agents work, fail and are evaluated | a book on language models and agents at level 2 and one agent workflow built by the learner |
| 13 | **Algorithms and contests** a long-running track; first milestone a Codeforces rating of 1800 | competency shown in timed contests and upsolving, not solved-problem counts |

## Fixed rules

- **Money.** Every project runs locally first. Real deployment happens when a free tier or credit that was verified today covers it. Anything paid needs the learner's yes, with an estimate. Order is always: estimate → billing alarm → build → teardown.
- **Credits and offers.** Check live, record the date and terms, track expiry. Never recommend one from memory.
- **Outside practice sites and material.** Discover the best existing ones, link them with prerequisites and a follow-up check. Finishing a game is not a level.
- **Certifications.** Only when the learner picks one. Build practical simulations from the official objectives, label them as simulations, and report gaps before suggesting a real attempt.
- **Hand-drawn designs.** Ask for a photo where the harness accepts images; otherwise ask for boxes, arrows and labels as a text list.
- **Never** test or break anything the learner does not own or have permission to test.
