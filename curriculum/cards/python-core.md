# python-core: Python as a first language, for people who will write, test and ship it
kind: language
aliases: python, python3, pytest, heapq, bisect
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: docs.python.org/3: tutorial (coverage), reference/datamodel (identity, hashing), faq/programming
  (failures), builtins/time-complexity, library collections, heapq, bisect, stdtypes (costs); Think Python 3e
  contents (order); cards needing it (what they assume); traces, messages, costs run on 3.13 here;
  peps.python.org/pep-0686 (UTF-8 mode default from 3.15); docs.python.org/3/whatsnew/3.13 (shadowing hint);
  stdtypes note 6 and peps.python.org/pep-0008 (repeated concatenation quadratic; the in-place optimisation "fragile")
unverified: the order of steps 10-14 is judgement

## Promise
Write, test and debug programs others can run; predict what each line does to names and objects; choose structures whose cost fits.

## The one idea
A name is a label tied to an object; assignment ties a label, never copies. Picture: luggage tags; two tags can hang on one suitcase. Where it breaks: some cases never open (`int`, `str`, `tuple`); "changing" one moves the tag to a new case.

## In production
- A virtual environment per project; linter, type checker, pytest in CI; daily: reading tracebacks and failing tests.
- Interviews, judges: built-ins, `heapq`, `bisect`; CPython does roughly 10^7 simple steps a second.

## Teaching order
1. Running code: the REPL, `python3 file.py`, `print`, `input()`; `int` (never overflows), `float`, `/`, `//`, `%`, `**`; `str` (immutable) slicing `s[1:-1]`, `split`, `join`, `strip`; f-strings `f"{x:.2f}"`.
2. Names and objects: assignment binds; `is` against `==`; aliasing; mutable `list`, `dict`, `set` against immutable `int`, `str`, `tuple`; copies `a[:]`, `copy.deepcopy`.
3. Control flow: `if`/`elif`, truthiness, `while`, `for` over any iterable, `range`, `enumerate`, `zip`, `break`, `continue`.
4. Functions and calls: `return` (`None` if absent; several values as a tuple); positional and keyword arguments, `*args`, `**kwargs`; defaults evaluated once (`None` sentinel); a new frame per call; `RecursionError`.
5. Scope and closures: local, enclosing, global, built-in; `global`, `nonlocal`; `lambda`; a closure keeps the variable, not its value.
6. Lists and tuples: an array of references; `append`/`pop` as a stack, amortised constant, `a[i]` constant; `insert(0, x)`, `pop(0)`, `x in a`, a slice `a[i:j]` linear; `s += t` in a loop may copy each time, `"".join` never; tuples as records and keys.
7. Dicts and sets: hash tables, average constant `in`, get, set; hashable keys; insertion order kept; `get`, `items()`, `&`, `|`, `-`; `Counter`, `defaultdict`, `deque` (both ends constant: BFS).
8. Iteration: `iter`, `next`, `StopIteration`; list, dict and set comprehensions; generator expressions and `yield`; `itertools.permutations`, `combinations`, `product`.
9. Sorting and searching: `sorted` against `list.sort` (`None`); `key=` with a tuple, stability; `heapq` (`heapify` linear, negate for max, `(priority, count, item)`); `bisect_left`, `bisect_right`.
10. Errors: a traceback read from its last line up; `try`/`except`/`else`/`finally`, the narrowest class; `raise`, your own `Exception` subclass, `raise ... from e`.
11. The standard library by need: `with open(path, encoding="utf-8")`, `pathlib`, `json`, `argparse`, `os.environ`, `logging`, `re` with raw strings, `datetime` with time zones, `sys.stdin.readline`.
12. Classes: `__init__`, `self`, class against instance attributes, inheritance, `super()`; `__repr__`, `__len__`, `__iter__`, `__contains__`, `__eq__`, `__lt__`; `@dataclass`, `field(default_factory=list)`, `frozen=True`.
13. Modules and projects: `import` runs a module once; `if __name__ == "__main__":`; packages as folders; a virtual environment per project, dependencies pinned in a file; module name clashes.
14. Type hints and tests: `list[int]`, `str | None`, a checker in CI; pytest: `test_` functions, plain `assert`, `pytest.raises`, `parametrize`, `tmp_path`; a bug fixed test-first.

## How it runs
- [2] `a = [1, 2]; b = a; b.append(3)`: `a` is `[1, 2, 3]`. `b = b + [4]` makes a new list; `a` is unchanged.
- [2,6] `grid = [[0] * 3] * 3; grid[0][0] = 1` changes all three rows (one row object); use `[[0] * 3 for _ in range(3)]`.
- [1] `0.1 + 0.2` is `0.30000000000000004`, so `== 0.3` is False (`math.isclose`). `2 ** 100` is exact. `-7 // 2` is -4, `-7 % 2` is 1.
- [4] `def f(x): x.append(9); x = [0]`: the caller's list gains 9, never becomes `[0]`.
- [4] `def add(item, acc=[])`: `add(1)` then `add(2)` returns `[1, 2]`: one list, made when `def` ran.
- [5] `[lambda: i for i in range(3)]`, each called: 2, 2, 2 (`i` is read at call time); `lambda i=i: i` gives 0, 1, 2.
- [5] `x = 10; def h(): x += 1`: `h()` raises `UnboundLocalError` (an assignment makes `x` local).
- [8] A generator's body runs only when `next` asks, up to the next `yield`, locals kept; then `StopIteration`. `it = iter(xs); list(it); list(it)`: the second is `[]`.
- [12] A class defining `__eq__` alone is unhashable; without `__contains__`, `in` loops over `__iter__`.

## Step notes
### 1
Need: I called `name.strip()` and the spaces are still there; did it not work?
Show: `name = "  Ada  "`, then `name.strip()` on its own line, then `print(f"[{name}]")`: most expect `[Ada]`;
it prints `[  Ada  ]`. `clean = name.strip()` then `print(f"[{clean}]")`: `[Ada]`. Then `print(input("age? ") + 1)`
with 30 typed: `TypeError: can only concatenate str (not "int") to str`: `input()` always gives text.
Explain: A `str` object never changes: its methods return a new one, and only `=` ties a name to it.
Try: predict: `int("3.5")` (`ValueError`); build: the mean of two typed numbers as `f"{m:.2f}"` (1, 2: `1.50`).
### 2
Need: I saved `backup = scores` before changing `scores`; why did my backup change too?
Show: `scores = [90, 85]; backup = scores; scores += [70]`: `backup` is `[90, 85, 70]`, `backup is scores`
True. The same lines with numbers, `count = 1; saved = count; count += 1`: `saved` is still 1, `saved is
count` False. `id()` before and after `+=`: the list's stays, the number's changes. Draw the tags.
Explain: `=` ties a second name to the same object, never a copy; `+=` changes a mutable object in place but
makes a new immutable one, so only the list shows through both names.
Try: predict: `b = a[:]; b[0].append(9)` for `a = [[1], [2]]` (`a` changes: shallow), then `copy.deepcopy`;
fix: `grid = [[0] * 3] * 3`, where one move fills a column, until `grid[0] is grid[1]` is False.
### 3
Need: My `if answer == "y" or "Y":` says yes when I type n; why?
Show: `answer = "n"` prints `yes`; in the REPL `answer == "y" or "Y"` is `'Y'`; `bool("0")` is True.
Explain: `or` returns its first truthy operand (else the last); a non-empty string is always truthy.
Try: predict: removing each 2 from `[1, 2, 2, 3]` inside `for x in xs` (`[1, 2, 3]`: an item is skipped);
predict: `rec = {}` above `for n in range(3): rec["n"] = n; rows.append(rec)` (three `{'n': 2}`: one
dict), then fix it by moving one line.
### 4
Need: My function prints the right answer; why is its result `None`?
Show: `def area(w, h): print(w * h)`; `a = area(3, 4)` prints 12, then `a + 1`: `TypeError: unsupported
operand type(s) for +: 'NoneType' and 'int'`. `def f(x): x = x + [1]` leaves the caller's list alone; `x +=
[1]` extends it. (Mutable default: How it runs.)
Explain: A call makes a frame whose parameters are new names for the caller's objects; with no `return`, `None`.
Try: predict: recursive `total(xs[1:])` on 10,000 items (`RecursionError`); fix: their function whose results
leak between calls, until two calls agree.
### 5
Need: `print(x)` worked until I added `x = 5` below it; how can a later line break an earlier one?
Show: `x = 10`; `def h(): print(x); x = 5` on two lines. Most predict 10; `h()`: `UnboundLocalError: cannot
access local variable 'x' where it is not associated with a value`. `h.__code__.co_varnames` is `('x',)`.
(The `+=` form: How it runs.)
Explain: An assignment anywhere in a body makes the name local throughout (unless `global`, `nonlocal`).
Try: predict: two `make_counter()` closures called a, a, b, a (1 2 1 3); fix: their loop-made callbacks that
all see the last `i`.
### 6
Need: Why does `insert(0, x)` in my loop take a second when `append` takes nothing?
Show: a million appends, counting how often `sys.getsizeof(a)` changes: under a hundred times (at lengths
that vary by version); every other append used spare room. For 10^5 items:
`insert(0, i)` about a second; `append`, then `reverse()`, a few milliseconds.
Explain: A list is an array of references with spare room at the end: `append` fills a slot, copying now and
then; `insert(0)` and `pop(0)` shift every reference; a slice copies its own.
Try: predict: `pop(0)` to empty on twice the items (4 times the time), then `deque.popleft`; predict:
10^5 then 2x10^5 `s += "x"` in a function also keeping `prev = s` each pass (about 4 times: each `+=`
copies), then `"".join`. Without `prev`, CPython may extend in place (PEP 8: never rely on it).
### 7
Need: Why is `x in my_set` instant at a million items, and why can't a list be a key?
Show: predict the size of `{1: "a", 1.0: "b", True: "c"}`: `{1: 'c'}` (equal keys, one hash). `{[1, 2]: 0}`:
`TypeError: unhashable type: 'list'`. A set's `in`: tens of nanoseconds at 10^3 items and at 10^6.
Explain: A dict files each key under its hash and confirms with `==`, so `in` goes to one slot at any size.
Try: fix: `d[k].append(v)` raising `KeyError`; build: a `Counter` of a file's words, checked by hand.
### 8
Need: My script loads a big log into a list and runs out of memory; how do I avoid that?
Show: `tracemalloc` peak of `sum([x * x for x in range(10**6)])`: 40 MB; of `sum(x * x for x in
range(10**6))`: under 1 KB, same answer. (When a body runs: How it runs.)
Explain: Each `next` runs a generator to its next `yield`, so a pipeline holds one item at a time.
Try: build: a generator of their log's error lines into `Counter`, peak checked; predict: the count of
`combinations(range(20), 3)` (1140).
### 9
Need: `heapq` pops the smallest first, yet the printed heap is unsorted; is it broken?
Show: `h = [5, 1, 4, 2, 3]; heapify(h)`: `[1, 2, 4, 5, 3]`; each `h[i]` ≤ `h[2*i+1]`, `h[2*i+2]`. Two
`heappush(q, (1, {...}))`: `'<' not supported between instances of 'dict' and 'dict'`.
Explain: A heap keeps only parent ≤ children, so a push or pop moves one item along log2 n slots; tuples
compare field by field.
Try: fix: `scores = scores.sort()` (`None`); apply: score descending then name, by `key=lambda p: (-p[1],
p[0])`, then by two stable sorts.
### 10
Need: The traceback is forty lines; where do I look?
Show: `int(cfg["port"])` on `port=`, two calls deep. Last line: `ValueError: invalid literal for int() with
base 10: ''`; above, where. `raise RuntimeError(...) from e` prints both.
Explain: Frames run outermost to innermost; the last line says what failed, the frame above it where.
Try: fix: `prnt("saving")` under a bare `except:` printing "could not open the file" (it does), narrowed to
`OSError`; build: their own exception class, caught by name.
### 11
Need: My script reads its file fine; why does a colleague get odd characters?
Show: `"naïve café\n"` written as UTF-8, read with `encoding="cp1252"`: `'naÃ¯ve cafÃ©\n'`, no error; with
`"ascii"`: `can't decode byte 0xc3`. With no `encoding`, `open` uses the locale's (Windows before 3.15; PEP 686).
Explain: A file holds bytes; text is bytes decoded by a named encoding: name it in every `with open`.
Try: fix: `datetime.now() < datetime.now(timezone.utc)` (`can't compare offset-naive and offset-aware
datetimes`); apply: `argparse` in their script, `--help` listing its options.
### 12
Need: I added an item to one cart; why does every cart have it?
Show: `class Cart: items = []`; after `a.add("tea")`, `b.items` is `['tea']`, `a.__dict__` `{}`. A dataclass
refuses `items: list = []`: `ValueError: mutable default <class 'list'> for field items is not allowed: use
default_factory`.
Explain: `a.items` is sought in the instance, then the class, so a list made in the class body is shared.
Try: fix: a subclass skipping `super().__init__()` (`'Tea' object has no attribute 'name'`); build: `__repr__`
and `__lt__` on their class, until `sorted` works.
### 13
Need: I named my file `random.py` and now `random.randint` does not exist; why?
Show: `random.py` (one `print`) beside `game.py` importing `random` twice: one print, then `module 'random'
has no attribute 'randint' (consider renaming ...)`, a hint new in 3.13.
Explain: `import` searches the script's folder first, runs a module once, keeps it in `sys.modules`;
`__name__` is `"__main__"` only when run.
Try: apply: `python3 -m venv .venv`, activated, `sys.prefix` ending in `.venv`; build: a module that runs as a
script, imports silently.
### 14
Need: `def add(a: int, b: int)` and `add("2", "3")` still ran; what are hints for?
Show: it prints `23`; `mypy`: `Argument 1 to "add" has incompatible type "str"; expected "int"`. Test first:
`parse_cents` that reads the digits after the point as cents, parametrized over `"3"`, `"3.50"`, `"3.5"`:
`assert 305 == 350` fails.
Explain: The interpreter ignores hints, a checker reads them; a test pins chosen behaviour.
Try: fix: `parse_cents`, until its cases and a `pytest.raises(ValueError)` pass; apply: `str | None` on their
function, the checker clean once callers handle `None`.

## Believable numbers
- CPython 3.13 here (November 2026): 10^7 additions in a loop, 0.3 s; `sorted` on 10^6 floats, 0.23 s; `in` on
  a 10^6 list, 5 to 10 ms; `list(range(10**6))`, 40 MB; [11] 10^6 numbers by `input()`, about 1 s.

## Go deep, leave for later
- Deep steps: 2, 4, 6, 8 (a name is a reference to an object; a call passes references into a new frame; a structure's cost follows from its layout in memory; a generator holds one item at a time).
- Later: writing decorators; `async`, threads (llm-application-engineering 12); `match`; regular expressions; packaging; numpy, pandas.

## Never omit
- Predict on paper, then run, in every step.
- [6-9] Each operation's cost, said aloud and timed once with `timeit` on a large input.
- Look up when planned: Python version, dependency tool, type checker.

## Wrong beliefs
- [2] "`b = a` copies the list" (both names tie to one list).
- [4] "A function can replace the caller's variable" (it can mutate the object, never rebind the caller's name).
- [2] "`is` is a stricter `==`" (it compares identity: use it for `None` only).
- [6] "`x in my_list` is fast" (it scans; a `set` hashes).
- [9] "A `heapq` list is sorted" (only `h[0]` is sure to be the smallest).
- [14] "Type hints make Python check types" (the interpreter ignores them).
- [10] "A bare `except:` makes code safe" (it hides bugs and even catches `KeyboardInterrupt`).
- [8] "A generator expression is a list comprehension in other brackets" (the list builds every result now; the generator makes one each time `next` asks).

## Failures to diagnose
- [4] Results from one call leak into the next: a mutable default argument.
- [6,7] A queue crawls at 10^5 items: `list.pop(0)`; use `deque.popleft`.
- [7] `KeyError` on `d[k].append(v)`: the key was never set.
- [7,12] `TypeError: unhashable type: 'list'`: a list as a dict key or set item; use a tuple.
- [9] `TypeError: '<' not supported between instances` from `heappush`: equal priorities compared the items.
- [13] `AttributeError: module 'random' has no attribute 'randint'`: your own `random.py` shadows the module.

## Practice and project
Guided: change one line of a trace, predict again. On your own: short problems, cost stated. Project: a command-line tool in the learner's own setting that reads files or JSON into dataclasses and rejects bad input with clear errors; finish line: pytest and the checker pass; a stranger runs it from the README in a fresh environment.

## Mastery ladder
- Use: a script that reads a file, counts with `Counter` and prints a sorted report.
- Explain: trace the aliasing, default, frame, closure and generator programs on paper, correct when run.
- Build: the project above.
- Design: choose structures for a stated workload, state each operation's cost, confirm it by timing.

## Words to own
[1] REPL, integer division, f-string, immutable, (slice); [2] name, object, identity, aliasing,
mutable; [3] truthiness, iterable; [4] parameter, default argument, frame;
[5] scope, closure, late binding; [6] amortised cost, slice; [7] hash table, hashable; [8] iterator, comprehension,
generator; [9] sort key, stable sort, heap; [10] exception, traceback; [11] context manager; [12] special
method, inheritance, dataclass; [13] module, package, virtual environment; [14] type hint, type checker, fixture
