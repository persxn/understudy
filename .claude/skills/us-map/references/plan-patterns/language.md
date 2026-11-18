# Plan pattern: a programming language

For Python, Go, Rust, C, Java, JavaScript and the like. Header: `run: python` (or the language), `kind: language`.

## The shape

- **Chapter 1** installs the toolchain, runs a program, shows the edit-run cycle and how to read an error message, and ends with a tiny program that does something useful (sums a file of numbers), not only "hello".
- **The usual order:** values and types, names, decisions, loops, functions, collections, the language's own way to make types (classes, structs, traits), errors, modules and packages, files and input, testing, then concurrency. Chapters are named after what the reader can do ("Repeating work"), never after syntax ("Operators").
- **The distinctive idea** (ownership in Rust, pointers and memory in C, goroutines and channels in Go, the event loop in JavaScript) gets its own chapter once enough is known to need it, foreshadowed in a short section earlier.
- **Tooling threads through** from chapters 1 to 3: formatter, linter, package manager and environment, debugger, test runner. A last chapter called "Tools" means the reader worked without them for weeks.
- **Carried through:** one program that grows (a budget tracker, a log analyser, a text game) and needs each chapter's feature.

## What weak plans miss

Reading tracebacks and debugging; tests before the last chapter; strings and Unicode; the memory model (what a name refers to, copy or share); idioms (what an experienced reviewer of this language would change); the standard library's everyday modules.

## Sample

Weak: `4.2 Functions | teaches: functions` (one line for a whole chapter's worth, nothing to test). Better, a whole chapter:

```text
### 4 Functions: naming a piece of work
4.1 The same five lines, three times | story
4.2 Defining and calling a function | teaches: def-statement, function-call, return-value
4.3 Parameters and arguments | teaches: parameter, positional-argument, keyword-argument
4.4 Where a name lives | teaches: local-scope, global-scope | fig
4.5 Default values, and the list that remembers | teaches: default-argument, mutable-default-trap | level: 2
4.6 The function that forgot to return | short | teaches: implicit-none | needs: none-value
4.7 Reading a traceback through several calls | teaches: call-stack, traceback-frames | fig | level: 2
4.8 Splitting the budget tracker into functions | teaches: decomposition | level: 3
4.9 Practice: from one long script to small functions | practice | level: 3
```

The mutable-default trap and the traceback are what a Python teacher checks for: the first is the most reported surprise of the language, the second is the skill that makes every later chapter cheaper.
