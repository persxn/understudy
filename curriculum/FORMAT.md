# The curriculum files: what they are and how they are written

For people and agents who BUILD or REVIEW these files. A learner's agent never reads this page and never opens
`curriculum/`: it runs `python3 scripts/us_path.py ...` and is handed the few lines it needs.

## What they are for (second design, 18 November 2026)

The first design made one book from one card. Four blind judges scored those books lower than books the product
planned alone (stage 4): the books were narrower than the learner's goal, a skipped card left
holes, and the card's example was weaker than the learner's own work. So the design changed:

- **The planner plans for the learner's goal, in the learner's own setting.** It decides the book's shape, its
  running case and its depth, exactly as it does without a curriculum.
- **The curriculum is a checked bank of teaching steps.** Each subject card is a list of steps; every other note
  on the card (a wrong belief, a failure, a word, a number) hangs on the step it belongs to.
- **Scripts do the joining.** `us_path.py spine` prints the steps of every card a goal needs, as one outline.
  The plan says which steps each chapter takes (`from:`), which the learner already has (`held:`) and which wait
  (`later:`). `us_plan.py check` refuses a plan that leaves a step unaccounted for. `us_plan.py brief` hands the
  writer of a chapter only the notes of that chapter's steps. `us_check.py` flags a word the chapter should have
  taught. None of this costs instructions in a skill.

What a card is NOT: a chapter list, a case to copy, or a place for facts that go out of date.

## Four kinds of file

| File | Path | Holds | Limit (4 characters = 1 token) |
|---|---|---|---|
| Domain index | `curriculum/<domain>/INDEX.md` | the tracks inside a domain, one line each | 250 tokens |
| Track map | `curriculum/<domain>/<track>.md` | the subjects of one track in order, and for each goal its steps, its opening, its deep steps and its order of study | 2,000 tokens |
| Subject card | `curriculum/cards/<subject>.md` | the teaching steps of one subject and, for each step, how to make it land | 5,000 tokens |
| Role map | `curriculum/roles/<role>.md` | what one job needs: subjects, levels, proof | 800 tokens |

A subject has 6 to 14 steps. Fewer: it is a step inside another card. More: two cards. Too deep for the limit:
split, never squeeze.

The limits on whole files are generous on purpose, because no agent ever loads a whole file. What is loaded is
small and is what the limits really guard: the outline of a card at planning (its step lines, at most about 60
tokens each) and the notes of one step at writing (at most about 350 tokens with everything tagged to it).

## Rules that keep them true

1. **One home per fact.** The map owns order between subjects. The card owns the steps of one subject. The role
   owns levels. They refer to each other by id and never repeat each other.
2. **Teaching decisions, not perishable facts.** No version numbers, prices, default values or install commands:
   those are looked up when a learner's book is planned (`PRACTICES.md`). A card may name what must be looked up.
3. **Production is the default lens.** The steps end where the subject is really used at work, and "In production"
   says how. Never a tour of features.
4. **Every claim is one you are certain of or took from a named source.** `sources:` lists the pages actually
   read, each with what it was used for. Do not invent statistics, job requirements or problem names.
5. **Plain words.** A card is read by a planner model, but its phrases end up in a beginner's book.
6. **Status is honest.** `status: built DATE` when written; `reviewed DATE` only by a different agent that checked
   it against its sources; `tested DATE` only after a book was planned from it and passed `us_plan.py check`.
   What could not be verified is said in an `unverified:` line, not hidden.
7. **Made for this subject.** Cover the title: could the steps belong to another language, tool or field? Then the
   card is a template with a name on it, and it is wrong. Every step names the real things of this subject: its
   constructs, commands, problems, protocols, numbers. "Basics", "Advanced features" and "Best practices" are
   never steps. Each kind of subject also has a part of its own (below) that only that kind needs.
8. **No cases.** A card never supplies the book's running example. The learner's own code, stack, repository or
   target judge is the case; the card says what must happen in it.
9. **Every note hangs on a step.** A wrong belief, a failure, a word or a number is tagged with the step it
   belongs to, so that the writer of one chapter is handed only what that chapter needs.
10. **A step says how it lands, not only what it covers** (third design, 19 November 2026). Blind judges found
   chapters written from topic lists broad and shallow. So every step carries its own notes: the question that
   opens it, the one experiment that makes it undeniable with what really happens, the explanation in a sentence
   the learner can say, and two tasks to try. Each card marks its few deep steps; a word is either owned at a
   step (five at most) or only met in passing. Depth is a decision the card makes, not one the writer guesses.
11. **Shown, not asserted.** Every `Show:` was run on a real machine or is quoted from a named source, and says
   which. Numbers in it are real output. A writer will run it again in the learner's setting; the card's job is
   to be certain the experiment exists, works, and surprises.

## Subject card

File name = id, lower-case with hyphens. Every `## ` part below is required, in this order; the fifth part's
name depends on `kind:`.

```text
# kubernetes-core: Kubernetes for people who will run services on it
kind: tool
aliases: kubernetes, k8s
needs: docker, networking-basics
status: built 2026-11-18
sources: kubernetes.io/docs/concepts (the objects and how they relate); kubernetes.io/docs/tasks/debug (the failures)

## Promise
Deploy, expose, update and debug a small service on a cluster, and explain what each part of the cluster did.

## The one idea
You state what you want; loops keep making it true. Picture: a thermostat. Where it breaks: there are many loops,
each a little behind the others, so the cluster is usually almost, not exactly, what you asked for.

## In production
- Clusters are usually managed by a cloud; teams own namespaces, not machines.
- Everything is a file in Git that a pipeline applies; nobody types changes by hand.
- The daily work is reading events and logs to find why a pod is not running.

## Teaching order
1. One pod by hand: `kubectl run`, then delete it; nothing brings it back.
2. A Deployment: delete its pod; a new one appears. The loop is the lesson.
3. One `kubectl apply` traced through the API server, etcd, the controllers, the scheduler and the kubelet.
4. Services and cluster DNS: one stable name for pods whose addresses keep changing.
5. ConfigMaps and Secrets: configuration outside the image.
6. Probes, rolling updates and `kubectl rollout undo`.
7. PersistentVolumeClaims: storage that outlives a pod.
8. Debugging with `kubectl describe`, events and logs: the failures below, each made on purpose and repaired.

## State and danger
- [3] Desired state lives in etcd behind the API server; the files in Git are its only safe copy.
- [7] `kubectl delete pvc` can delete the data with the claim (reclaim policy `Delete`): check the policy first.
- `kubectl delete namespace` removes everything in it without asking: never on a shared cluster.

## Step notes
### 1
Need: I can run a container on my laptop; why does a cluster need a new word, "pod", for the same thing?
Show: `kubectl run web --image=<your image>`, then `kubectl delete pod web`, then `kubectl get pods`. The learner
expects it to come back; nothing does. (From kubernetes.io "Pods": a bare pod is not rescheduled.)
Explain: A pod is one run of your containers on one node; nothing owns it, so nothing replaces it.
Try: predict: what `kubectl get pods` shows a minute after the node is drained, then check; build: a pod from a
manifest file whose `kubectl describe` shows the image and port you chose.
### 2
Need: If a pod that dies stays dead, how does anything stay up?
Show: create a Deployment with `replicas: 2`, delete one pod, watch `kubectl get pods -w`: a new pod with a new
name and a new IP appears within seconds, while the old name never returns.
Explain: You wrote down "two of these"; a controller keeps comparing that with what exists and creates or deletes
pods until they match.
Try: predict: the pod count after `kubectl scale --replicas=5` and after deleting three at once; fix: a
Deployment whose selector matches no pod template label (finish line: `kubectl rollout status` succeeds).
(steps 3 to 8 follow in the same form)

## Go deep, leave for later
- Deep steps: 2, 3, 8 (the loop, the path of one `apply`, and debugging are what separate use from understanding).
- Later: operators, service mesh, Helm (its own card).

## Never omit
- Delete things and watch them recover, in every step.
- [6] Memory limits and what `OOMKilled` means.

## Wrong beliefs
- [2] "Pods are restarted" (they are replaced by new pods with new addresses).
- [3] "`kubectl apply` does the work" (it only records what you want; controllers do the work later).
- [4] "A Service is a load balancer program" (it is a stable address plus forwarding rules on every node).
- [5] "Secrets are encrypted" (only base64-encoded unless encryption at rest is switched on).

## Failures to diagnose
- [2,8] `Pending`: no node has the requested memory or processor.
- [8] `CrashLoopBackOff`: the container starts and exits; the reason is in `kubectl logs --previous`.
- [8] `ImagePullBackOff`: a wrong image name or missing registry secret.
- [4,8] A Service with no endpoints: its selector matches no pod's labels.
- [6] A rollout stuck on a failing readiness probe.

## Practice and project
Guided: repeat each step's experiment with one thing changed. On your own: given a manifest, predict what the
cluster will do, then check. Project: the learner's own small web service with a database, deployed from files,
surviving the loss of a pod; finish line: a script of five checks all pass.

## Mastery ladder
- Use: deploy and expose a given image from a written manifest.
- Explain: trace `kubectl apply` to a running container, to a friend, without notes.
- Build: the project above.
- Design: choose requests, limits and replica counts for a stated load, and defend them.

## Words to own
[1] pod, (node); [2] deployment, replica, desired state, reconcile; [3] control plane, scheduler, kubelet,
(etcd); [4] service, selector, label, (endpoint); [5] configmap, secret; [6] probe, rollout; [7] volume, claim;
[8] event, (namespace)
```

**Header.** `kind` is one of language, tool, framework, system, skill (it becomes the book's `kind:`). `needs`
are card ids, or `none`: what a learner must hold before step 1.

**Teaching order.** 6 to 14 numbered steps, in the order a strong practitioner would teach them to someone who
will use the subject at work. A step line is lean (about 60 tokens at most): its name, then the real things
that carry it. Step 1 is small and whole: it gets something real working, or does the whole practice once in
miniature, and it already touches the card's deepest idea in its simplest form. A step is a unit of teaching (one to four sections of a book), not a chapter: the
planner groups steps into chapters. Each step names what is taught and the real thing that carries it (a command,
a construct, a named public problem, a protocol message, a number). A step may need only earlier steps and the
`needs:` cards.

**The part made for the kind** (fifth part; list items, each may carry a tag):

| kind | Part | Holds |
|---|---|---|
| language | `## How it runs` | what the reader must be able to trace by hand (what a name is, what a call does, where values live and when they die), and the idioms and traps that follow, each as real code in backticks |
| tool | `## State and danger` | where the tool keeps its state (named files or objects), and each command that destroys work, with the safe form |
| framework | `## What it owns` | the loop or lifecycle the framework runs for you: what calls your code, when, and in what order; what you still own; which facts change with versions (names only, to be looked up) |
| system | `## Numbers and traces` | the orders of magnitude a practitioner carries in their head (each with its source), and the end-to-end traces the book must walk |
| skill | `## Judged by` | the criteria a strong practitioner uses to judge a piece of this work, as yes/no tests a learner can apply to their own |

**Step notes** (the part after the kind's part): one block per step, headed `### N`, with four lines that may wrap.
- `Need:` the question a learner really has just before this step, in their words, ending with a question mark.
  It is the lesson's opening; "Why learn X?" is never a Need.
- `Show:` the one run, trace, measurement or worked case that makes the idea undeniable: what to set up, what the
  learner will predict, and what really happens, with the real output or number, and where it comes from (run
  here, or the named source). The best ones contradict the prediction.
- `Explain:` the mechanism in one or two sentences a learner could say back; never a definition copied from
  documentation.
- `Try:` two tasks separated by `;`, each beginning with its type (`predict:`, `explain:`, `fix:`, `apply:`,
  `decide:` or `build:`) and saying what counts as done. One of them should grow out of a failure tagged to the
  step.
- `Picture:` (optional) an everyday picture for this step and where it breaks, when the card's one idea is not
  enough.
A block is at most about 200 tokens. Nothing in it is a case for the book: it says what must happen in the
learner's own setting.

**Deep steps.** The first line of "Go deep, leave for later" is `- Deep steps: N, N, N (why)`: the two to four
steps (one to three in a card of seven steps or fewer) where understanding is made. A planner gives a deep step
a chapter of its own or most of one; a writer spends the chapter's best pages there.

**Believable numbers** (optional part, after "Step notes"; list items, each may carry a tag): the orders of
magnitude an invented case in this subject must respect, each run here or taken from a named source, with its
date where it ages. Required in spirit for any card whose chapters will stage cases with quantities (a design, a
load test, a contest limit); a `system` card keeps them in "Numbers and traces".

**Tags.** An item starts with a tag in square brackets naming the step or steps it belongs to: `[3]`, `[5-6]`,
`[2,8]`. Required on every item of "Wrong beliefs" and "Failures to diagnose" and on every group of "Words to
own" (groups are separated by `;`). Optional in the kind's part, in "Believable numbers" and in "Never omit": an
item with no tag belongs to every step. A tag names only steps that exist.

**Words: owned or met.** In "Words to own" a word in round brackets is only met at that step: the chapter uses it
once with a plain gloss and does not teach it. Every other word is owned there: taught with its mechanism and
checked by script in the chapter. A step owns five words at most; step 1 owns four at most. A word a step would
own beyond that belongs to a later step, or in brackets.

**Other parts.** "Wrong beliefs" items are a quoted belief people really hold and the exact truth in brackets.
"Failures to diagnose" are real failures a learner can make happen, with the cause. "Mastery ladder" has the four
lines Use, Explain, Build, Design, each a task the learner does and a third person could judge, never
"understands X". "Words to own" are the terms a practitioner uses without thinking; every one must be taught in
the step it is tagged with.

## Track map

```text
# DevOps: containers and orchestration
for: someone who can use a Linux terminal and Git
leads to: platform engineer, SRE, cloud engineer, a backend engineer who deploys their own service
status: built 2026-11-18
sources: ...

| # | Subject | Needs first | After it you can | Main topics | Hours | Level |
|---|---|---|---|---|---|---|
| 1 | linux-command-line | none | work on a remote machine without a mouse | files, processes, permissions, services | 20 | 3 Build |
| 2 | networking-basics | 1 | follow a request from one machine to another | addresses, ports, DNS, NAT | 20 | 2 Explain |
| 3 | docker | 1, 2 | ship your own app as an image | images, containers, volumes, networks | 30 | 3 Build |

## Goals
### Ship my own service in a container (about 55 h)
Steps: linux-command-line 1-6; networking-basics 2-4; docker 1-12.
Open with: their own service running in a container by the end of chapter 1, built from a five-line Dockerfile
they wrote, however crude (docker 1-3 in miniature), then broken once on purpose.
Deep: docker 4, 6; linux-command-line 5.
Order: linux-command-line 1-4; docker 1-3; linux-command-line 5-6; networking-basics 2-4; docker 4-12.
Halfway: they can rebuild the image after a code change in seconds and say why it was fast.

### Move from developer to platform engineer (about 70 h)
Steps: linux-command-line 1-13; networking-basics 2-5; docker 1-12.
Open with: one real server they can reach, a process started, killed and found again (linux-command-line 1, 5).
Deep: linux-command-line 5, 8; docker 4, 7.
Order: rows in order; networking-basics may be `held` by a working backend developer.

## Why this order
One or two sentences per jump that is not obvious.

## Checkpoint projects
- After 3: ...

## Short on time
What can wait and what must never be skipped.

## Left out on purpose
What a reader might expect here, and why it is not (one line each).
```

A subject with no card yet is written `name (planned)`. "Needs first" uses row numbers or ids of subjects in
other tracks, and covers everything the card's `needs:` names. Hours are study hours for a beginner to the stated
level, practice included, rounded to 5.

**Goals** has two to five blocks. Each is a checked plan for one common goal, so that a planner does not have to
invent the shape of the book (every failed blind test traced back to that invention):
- `### <the goal in a learner's words> (about N h)`: the hours of the steps below, from the Hours column scaled
  by steps.
- `Steps:` for each card, the steps this goal CANNOT do without (a whole card only when every step is needed),
  as `card-id N-M, N; card-id ...`. A planner cutting to a learner's hours keeps these and leaves the rest for
  later.
- `Open with:` what the first chapter does for this goal and the steps it draws on: something real working, or
  the whole practice once in miniature, in the learner's own setting, already touching the deepest idea.
- `Deep:` the three to six steps that deserve a chapter of their own FOR THIS GOAL (usually deep steps of their
  cards).
- `Order:` the order of study across cards when it is not simply row order: whatever such a learner asks for by
  name comes in the first half; a card's remaining steps may follow.
- `Halfway:` (optional) what they can do at the halfway mark, in their words.
A goal block is checked the way a card is: run `python3 scripts/us_path.py goal <track> <n>` and ask whether a
strong, complete book can be made from exactly those steps in that order.

## Domain index

```text
# DevOps and infrastructure
status: built 2026-11-18

| Track | For | Start here if |
|---|---|---|
| foundations | anyone new to servers | you have never used a terminal on a remote machine |
| containers | after foundations | you can use Linux and Git and want to ship software |

Roles this domain feeds: junior-devops-engineer, sre.
```

## Role map

```text
# junior-devops-engineer: junior DevOps or platform engineer
status: built 2026-11-18
sources: (public career ladders, exam guides and the job adverts sampled, each with its date)

| Subject | Level | Class | At work it looks like | Proved by |
|---|---|---|---|---|
| linux-command-line | 3 Build | essential | scripts that others rely on | a script that backs up and rotates logs |
| docker | 3 Build | essential | every service ships as an image | a small, safe image of a real app |
| kubernetes-internals (planned) | 2 Explain | specialist | platform teams | explain scheduling of one pod |

## Order and time
The order to study in (ids), and total hours for someone starting from the stated beginning.

## Interview checks
Three to six things an interviewer really asks at this level, each tied to a subject above.

## Capstone
One project that uses most of the essential lines, with its finish line.

## Overlap
Which other roles share most of this, so a learner who changes direction keeps what they proved.
```

Class is essential, desirable or specialist. Level is one of 1 Use, 2 Explain, 3 Build, 4 Design, 5 Teach. The
"At work" and "Proved by" cells come from the sources (adverts, ladders), not from imagination.

## How a learner's plan uses them

The planner is told how in `.claude/skills/us-map/references/from-a-card.md`. In short:

```text
python3 scripts/us_path.py find competitive programming        the tracks, cards and roles that match
python3 scripts/us_path.py map core-cs/competitive-programming  the track: rows, goals, order, checkpoints
python3 scripts/us_path.py goal core-cs/competitive-programming 1  one goal: its opening, deep steps and order,
                                                                 then the outline of exactly its steps
python3 scripts/us_path.py spine cpp-for-contests:4-8 dsa-core-techniques recursion-and-dynamic-programming
                                                                 the same outline for steps chosen by hand
```

and writes into the book's `PLAN.md`:

```text
track: core-cs/competitive-programming 1-4       the rows of the goal line: the goal, not this book's size
budget: 150 hours                                hours a week times the weeks to the learner's deadline
held: cpp-for-contests 1-3                       steps the learner showed they have (evidence in brackets)
later: graphs-and-trees 9-12                     steps left for a later book, with the reason in route.md

### 4 Sorting as a tool
from: dsa-core-techniques 4; cpp-for-contests 5  the steps this chapter teaches
4.1 ...
```

A plan with a `track:` line is one book of at most 16 chapters: group more steps in a chapter, leave what the goal can do without under `later:`, and only if the goal still does not fit make it a series with `later: ... (book 2)`; steps left for a later book do not count as untaught.

`us_plan.py check` then accounts for every step of every card the plan touches (taught, held or later) and for
every card those cards need; it refuses a plan that teaches nothing from a card the goal names, and one whose
taught steps cost more hours (by the maps) than the budget. `us_plan.py brief BOOK N` prints, for the writer of chapter N, each step named on
its `from:` line with its own notes in the order a lesson is written (need, show, explain, what goes wrong, words
owned and met, tasks to try), deep steps marked. `us_check.py BOOK N` flags an owned word the chapter never uses.
`us_path.py ready ROLE` scores a role from what the learner's books and practice records show.

## Checking

`python3 scripts/us_path.py check` must end "check ok". It refuses a missing part, a file over its limit, an id
that does not exist, a tag naming a step that does not exist, an untagged item where a tag is required, a subject
placed before something it needs, a map row whose "Needs first" leaves out something its card needs, a goal line
naming a row or a step that does not exist, a role that names no card, a status it cannot read, and a card whose
text matches a known mistake (`rules/known-mistakes.md`). It also refuses a step with no step notes or with one of the four
lines missing, a `Need:` that is not a question, a `Try:` without two typed tasks, a step that owns more than five
words (step 1: four), a card without a valid `Deep steps:` line, and a goal block missing a line or naming a
step that does not exist. It notes (without failing) a step that names nothing concrete, a step line or a step's
notes over their size, a step with no word and no wrong belief tagged to it, and a word owned by two cards that
one learner can meet (cards in one track, or one needing the other). A card with no "Step notes" part is an error.
