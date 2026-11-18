# Which figure shows which idea

Name the kind of idea first, then pick the figure. A wrong kind looks finished and teaches nothing: a flow chart of memory hides the addresses. Every sketch below draws cleanly.

| The idea is | Figure | Why this one |
|---|---|---|
| a sequence of events between parties | `sequence` | time runs down; who sends what to whom |
| steps with decisions | `flow`, `dir: down` | diamonds show where paths split |
| a structure of parts | `layers` (stacked), `tree` (each part has one parent) | position shows what sits on or belongs to what |
| a state that changes | `flow`, `dir: right`, `round` states, `hot` on the current one (or two `memory` figures, before and after) | arrows are the events |
| a flow of data | `flow`, `dir: right`, `store` for where it rests | arrows carry the data, labelled with its form |
| a layout in memory | `memory` | only it shows addresses and cells |
| a comparison, or a timeline | a table, not a figure | see below |

## Sketches

Sequence (a system):

```text
actor c: client
actor s: server
c -> s: SYN
s ..> c: SYN-ACK
c -> s: ACK
```

Steps with a decision (a skill: preparing a change for review):

```text
round pr: change ready
diamond small: under 400 lines?
box split: split it
pr -> small
small -> review: yes
small -> split: no
split ..> small: resubmit
```

Structure, layers, then tree:

```text
layer app: Application @ your program
in app: http = HTTP request
layer tr: Transport @ kernel
in tr: tcp = TCP segment
http -> tcp
```

```text
kind: tree
box c: commit
box t: tree
box s: src/
c -> t
t -> s
```

State that changes:

```text
dir: right
round ready: Ready
round run: Running
round wait: Blocked
ready -> run: scheduled
run -> wait: waits for I/O
wait -> ready: I/O done
hot: run
```

Flow of data:

```text
dir: right
box api: `POST /users`
store db: users table
form -> api: JSON
api -> db: insert row
```

Layout in memory:

```text
vars: p=1008@2000
row arr: 10 20 30 40 | at=1000 step=4 | hot=2
ptr p -> arr[2]
```

## When not to draw

- **A comparison** of options by their properties is a table: the reader reads across and down.
- **A timeline** of dates is a table or list: no figure type spaces events by time, so a drawing implies proportions it lacks.
- **What the reader will see as text** (a directory listing, `git log --graph`) is a text block from a real run, so they recognise it on their screen.
- **One relation between two things** is a sentence.

Weak: a `flow` of five boxes "Install, Configure, Run, Test, Deploy" in a line. A numbered list wearing boxes: nothing branches. Write the list.
