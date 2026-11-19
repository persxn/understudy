# javascript: JavaScript for people who will ship code to browsers and servers
kind: language
aliases: js, ecmascript, npm, promises, async await, event loop, dom
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: javascript.info, MDN JavaScript Guide contents (order); MDN Using promises (floating promises); MDN
  Microtask guide, In depth (queues); jakearchibald.com tasks-microtasks (puzzle); html.spec.whatwg.org timers (4 ms
  clamp); traces and npm run in Node, Chromium
unverified: messages are V8's (Node, Chrome); other engines differ

## Promise
Write and debug JavaScript for browser and Node: predict what a line does to values, `this` and the queues; handle every async error; drive a page from fetched data.

## The one idea
One thread runs your code, one task at a time, each to the end; whatever arrives meanwhile waits in queues. Picture: a cook finishes the plate in hand, then every sticky note (microtasks), then the next ticket (task). Where it breaks: the host fetches, times and draws in parallel; Workers add cooks.

## In production
- Runs in browsers and Node, shipped through a bundler and linter, often typed.
- Costly bugs: unhandled rejections, out-of-order responses, shared objects mutated elsewhere.

## Teaching order
1. Values, types, control flow: primitives and objects, `typeof`; `if`, `for`, `while`, `switch`; coercion and `NaN`, `===` over `==`; truthy and falsy, `??` against `||`, `?.`; the console.
2. Functions and scope: declarations, expressions, arrows, default and rest parameters, callbacks; `const`, `let`, blocks, the temporal dead zone, `var` only to read; closures and the loop-closure trap.
3. Objects and arrays as references: aliasing and mutation; spread is shallow, `structuredClone` deep; `const` fixes the name only.
4. `this` set by the call site: method call, plain call (`undefined` in strict code), `call`/`bind`, `new`; arrows take the enclosing `this`.
5. Prototypes and what `class` builds: the prototype chain; methods on `prototype`; `extends`, `super`, `#private`, `instanceof`.
6. Collections and iteration: `map`, `filter`, `find`, `reduce`, `sort` with a comparator; `Map`, `Set`; `for...of` against `for...in`; iterables; destructuring.
7. Text, numbers, dates, JSON: template literals; doubles (`0.1 + 0.2`, `Number.MAX_SAFE_INTEGER`, money in cents, `BigInt`); a `Date` is a UTC instant shown in local time; ISO strings, `Intl`; what JSON drops.
8. Modules and packages: `import`/`export`, named and default; a module runs once, strict; `<script type="module">`; CommonJS `require`; `package.json` (`dependencies`, `devDependencies`, `scripts`); `npm install`, the committed lock file; `npm run build`, `npm test`; bare names (`"lodash"`) found in `node_modules`.
9. Errors and debugging: `throw`, `Error` subclasses, `cause`, `stack`, `try`/`catch`/`finally`; a callback's error never reaches your `try`; stack traces, breakpoints, `debugger`.
10. The event loop: call stack, run-to-completion, tasks (timers, I/O, events), microtasks drained after each task, then rendering.
11. Promises: pending, fulfilled, rejected; `then` returns a new promise; return in a chain, `catch`, `finally`; unhandled rejections; wrapping a callback API.
12. `async`/`await`: always returns a promise; `await` resumes in a microtask; `try` around `await`; `Promise.all`, `allSettled`, `race`; `AbortController`.
13. The DOM and events (its HTML too unless html-and-css is held): `querySelector`, `textContent` against `innerHTML`, `<script defer>`; `addEventListener`, bubbling, `target` against `currentTarget`, delegation with `closest`, `preventDefault`.
14. `fetch`: `response.ok`, `status`, `response.json()`, a JSON body with `Content-Type`; loading, error and empty states; ignoring a stale response.

## How it runs
- [1] `0 == ''` true; `[] == false` true; `NaN === NaN` false (`Number.isNaN`); `typeof null` "object"; `'2' + 1` "21"; `0 || 'd'` "d", `0 ?? 'd'` 0.
- [2] `for (var i = 0; i < 3; i++) fs.push(() => i)`: calls give 3, 3, 3; with `let`, 0, 1, 2 (a binding per pass).
- [4-5] `const m = k.m; m()` on a class method throws `TypeError: Cannot read properties of undefined (reading 'v')`.
- [6] `[1, 10, 2].sort()` stays `[1, 10, 2]` (compared as strings): pass `(a, b) => a - b`.
- [7] `0.1 + 0.2` is `0.30000000000000004`; `2 ** 53 + 1` is 9007199254740992. In New York `new Date("2026-03-01").getDate()` is 28; `new Date(2026, 1, 30)` is 2 March. JSON turns a `Date` into a string, `NaN` into `null`, drops `undefined`, empties a `Map`.
- [10-12] Log A; `setTimeout(E, 0)`; `Promise.resolve().then(C1).then(C2)`; `queueMicrotask(C3)`; an `async` function logging B, `await null`, then C4; log B2. Prints A B B2 C1 C3 C4 C2 E: sync code, microtasks in queue order (C2 queued when C1 ends), then the timer.
- [10] A 200 ms busy loop delays a `setTimeout(f, 0)` by 200 ms; clicks and paint wait.
- [12] Three `await sleep(100)` in a loop: about 300 ms; `Promise.all` of them: about 100. `forEach(async ...)` waits for none.
- [14] `fetch` of a 404 resolves, `ok` false; `.json()` of an HTML error page throws `SyntaxError: Unexpected token '<'`.

## Step notes
### 1
Need: The form says quantity 2 and my total says 21; isn't JavaScript doing maths?
Show: fields `"2"`, `""`, `"two"`, `"0"`: `qty + 1` gives `21`, `1`, `two1`, `01`; `Number(qty)` 2, 0,
NaN, 0: a blank field becomes 0, no error. `||` against `??`: How it runs [1].
Explain: `+` with a string joins text; `Number()` and `-` convert, blank text to 0.
Try: fix: a sum of theirs from `<input>` values: `""` and `"two"` give a message; predict: `a.qty` after
`const b = a; b.qty = 2`, with `a = { qty: 1 }` (2: one object, two names).
### 2
Need: My handler logs the last loop pass's value; doesn't a function keep the value it saw?
Show: `makeCounter()` returns `() => ++n` over its own `let n = 0`; after `a(); a()`, `a(), b()` give `3 1`.
`let s = "draft"; const f = () => s; s = "sent"; f()`: "sent". `let x` read before its line: `Cannot access 'x'
before initialization`.
Explain: A function keeps a live link to its scope's variables, not their values; each call makes new ones.
Try: predict: handlers made in a `for (var ...)` loop, then fix; build: `once(fn)`, checked by three calls.
### 3
Need: I copied the default cart with `{ ...emptyCart }`; why does Bob's new cart hold Ann's book?
Show: `const emptyCart = { items: [], coupon: null }; const newCart = () => ({ ...emptyCart })`. Ann's cart
pushes "book", sets a coupon; Bob's new cart: items `['book']`, coupon null; the `const` `emptyCart.items`:
`['book']`. With `structuredClone`: `[]`. Draw three carts, one array.
Explain: A variable holds a reference; spread copies one level, so nested arrays stay shared; `const` fixes
only the name.
Try: predict: `board` after `top2(board)` that calls `list.sort` (reordered); fix: a function of theirs
mutating its argument, caught by a test.
### 4
Need: `c.inc()` works; given to `addEventListener` it counts nothing; where did `this` go?
Show: `class Counter { count = 0; inc() { this.count++; } }`; predict `c.count`. As a click listener: 0
(`button.count` NaN); `setTimeout(c.inc)`: 0 (`this`: Node's timer, Chromium's `window`); `[1].forEach(c.inc)`:
`Cannot read properties of undefined (reading 'count')`; `() => c.inc()`: 1.
Explain: The call decides `this`: `c.inc()` passes `c`, an event its element, a plain call `undefined`; arrows
keep the outer `this`.
Try: fix: a handler of theirs passed as `obj.method`, until a click changes the object's own count; predict:
`this` logged by a `function` listener, then an arrow listener (the element; the enclosing `this`).
### 5
Need: If `class` is like Java's, how can I change a method of existing objects?
Show: `const d = new Dog()`; then `Dog.prototype.bark = () => "WOOF"`: `d.bark()` "WOOF"; `typeof Dog`
"function"; `Object.hasOwn(d, "bark")` false. Methods are shared (`x.hover === y.hover`), arrow fields not.
Explain: `class` builds a function and a prototype object; a property missing on an object is looked up along
its prototype chain at each call.
Try: predict: `d instanceof Dog` after `Object.setPrototypeOf(d, null)`; decide: method or arrow field for
10,000 objects.
### 6
Need: I keyed visit counts by user object; why does every user get the same count?
Show: `visits[ann] = 3; visits[bob] = 5`: keys `['[object Object]']`, `visits[ann]` 5; a `Map`: 3, size 2.
`new Set([{ id: 1 }, { id: 1 }]).size` 2.
Explain: Plain-object keys become strings; `Map` and `Set` compare objects by identity.
Try: build: their records grouped into a `Map` by `reduce`; predict:
`new Set(["1", 1]).size` (2: no coercion).
### 7
Need: Why is a price a cent off, and my date a string after the API?
Show: `(1.005).toFixed(2)` is "1.00" (stored as 1.00499999999999989...). A `Date` back from JSON is a
string: `.getTime()` throws `getTime is not a function`.
Explain: Numbers are binary doubles, most decimals near misses: count money in cents; JSON has no dates, so
they travel as ISO strings, revived by `new Date(s)`.
Try: fix: a total of theirs into cents, checked with 1.005; build: a `JSON.parse` reviver giving `Date`s.
### 8
Need: Two files import my config module; does each get a copy?
Show: `counter.mjs` logs "runs", exports `let n`, `inc()`, `settings`; `a.mjs` calls `inc()`, sets
`settings.theme = "dark"`; `main.mjs` imports both: one "runs", `1 dark`; `n = 5` there: `TypeError:
Assignment to constant variable.`
Explain: A module runs once; importers share its live, read-only bindings.
Try: predict: a module-level `Map` cache on their server's second request; apply: `npm install` on a fresh
clone leaves the lock file unchanged.
### 9
Need: I wrapped the call in `try`/`catch`; why did the error still crash it?
Show: `try { setTimeout(() => { throw new Error("boom") }, 0) } catch { log("caught") }; log("after try")`:
"after try", then Node exits 1; the trace starts at `Timeout._onTimeout`, no frame of the `try`.
Explain: `catch` sees only throws while its `try` is on the call stack; a callback runs later on a fresh
stack.
Try: explain: a trace from their app, frame by frame; fix: a `catch` that logs and goes on, to rethrow with
`{ cause: e }`, until Node's trace shows both errors, the first under `[cause]:`.
### 10
Need: I `await` every thousand items so the page stays responsive; why does it still freeze?
Show: 50M `Math.sqrt`s, `await Promise.resolve()` every 500,000, `setTimeout(click)` set first. Node and
Chromium: the work finishes (a few hundred ms), and only then the click. Yield by `await new Promise(r =>
setTimeout(r))`: click within a few ms, the work done later and slower. Draw the stack and both queues.
Explain: After each task, microtasks run until none remain, new ones too, before any task or paint; `await`
resumes as a microtask, so no click gets in.
Try: predict: their own mix of timers, `then` and `await`; fix: a long loop of theirs, split by timers until a
click answers within 50 ms.
### 11
Need: I put `.catch` on the promise; why is there still an "Uncaught (in promise)"?
Show: `const p = loadUser()` (rejects); `p.then(u => log(u.name)); p.catch(e => log("handled"))`. Most expect one
line: "handled"; then Node exits 1 on the same error.
Explain: Every `then` returns a new promise that passes an unhandled rejection on; a `catch` handles only its
own chain.
Try: fix: `.then(ids => { ids.forEach(save) })`, logging "all saved" though save 2 failed, till `catch` gets it;
build: `wait(ms)`, `await wait(100)` resuming about 100 ms later.
### 12
Need: My `await` is inside a `forEach`; why does the next line run first, and my `try` miss its error?
Show: `try { ids.forEach(async id => { await sleep(10 * id); if (id === 2) throw ...; log(id) }); log("done")
} catch ...`, then `log("next")`: done, next, 1, then the throw ends Node. With `await Promise.all(ids.map(...))`:
1, caught, next, 3: id 3 still ran.
Explain: An `async` callback returns its promise at the first `await`; `forEach` drops it, so nobody waits or
catches.
Try: predict: the same with `await ids.forEach(...)`; fix: a `forEach(async` in their code, test first.
### 13
Need: Clicking my delete button's icon gives an `undefined` id, and new rows do nothing; why?
Show: in Chromium, `<button data-id="1"><span>x</span></button>` with a listener; row 2 added later. Icon
click: `e.target.dataset.id` undefined, `currentTarget`'s "1"; row 2 silent. One `<ul>` listener using
`e.target.closest("button")`: 1, 2.
Explain: A click bubbles up from the innermost element; `target` is where it began, `currentTarget` the
listener's element.
Try: fix: a list of theirs, one listener; predict: a name `<img src=x onerror=...>` by `innerHTML`,
then `textContent` (the script runs; then shown as text).
### 14
Need: Search shows results for "re" though I typed "react"; how can an older request win?
Show: a local server answers `?q=re` in 300 ms, `?q=react` in 50; `search("re")`, `search("react")` 20 ms
later: "render react", "render re", screen "re". Each search aborting the last one's `AbortController`: "re ->
AbortError", screen "react".
Explain: Responses come as the server finishes them; render only the latest.
Try: fix: their search box, throttled, till the last query wins; build: its error state, shown on a forced 500.

## Believable numbers
- Node 22 here (2 shared cores, November 2026): 1e8 loop additions 0.05 to 0.2 s; `JSON.parse` a few ms per
  MB; a local `fetch` under 1 ms; `setTimeout(f, 0)` about 1 ms (browsers: nested timers at least 4 ms, HTML
  spec).

## Go deep, leave for later
- Deep steps: 3, 4, 10, 12 (references and mutation; `this`; the event loop; dropped promises: most junior production bugs).
- Later: generators, `Proxy`, Workers, regular expressions, `Temporal`, test runners.

## Never omit
- Predict the output, then run it; every async lesson prints an order.
- [11-14] Every promise ends in a `catch` or an `await` in `try`.
- Look up when planned: browser support (`Temporal`), the Node line, module system, package manager, bundler.

## Wrong beliefs
- [3] "`const` makes the object unchangeable" (only the name is fixed).
- [4] "`this` is the object the function was written in" (the call site sets it; arrows excepted).
- [5] "JavaScript classes are like Java's" (a function plus a prototype object, looked up at run time).
- [10] "`setTimeout(f, 0)` runs `f` now" (after this task, all microtasks and the tasks ahead).
- [11] "A final `catch` catches everything" (not a promise a handler started and did not return).
- [12] "`async` runs code in parallel" (one thread; `await` only yields; heavy work still blocks).
- [14] "`fetch` rejects on an HTTP error" (only on network failure; check `response.ok`).

## Failures to diagnose
- [3] One user's data shows in another's: each new object was spread from a shared template, and the nested array went with it.
- [4] A method passed as a callback: `Cannot read properties of undefined` when called plainly; as a listener or timer, no error, a `NaN` on the wrong object.
- [10] A page frozen though the loop `await`s: it yields only to microtasks; split the work with timers.
- [12] "done" logged before the saves, and their error escapes the `try` as an unhandled rejection: `forEach(async ...)`.
- [8] `Cannot use import statement outside a module` (no `type="module"`); `Failed to resolve module specifier` (a bare name, no bundler).
- [13] `Cannot read properties of null (reading 'addEventListener')`: script ran before the element existed, or a wrong selector.
- [13] Script injected through user text put in `innerHTML`.
- [14] Old results shown: an earlier, slower response arrived last.

## Practice and project
Project: a page of the learner's app on their own API with loading, error and empty states, delegated events, stale responses ignored; finish line: on a throttled network and an API 500, the console stays clean and the page says what failed.

## Mastery ladder
- Use: a script that fetches JSON and renders a list whose delete buttons work.
- Explain: predict on paper the print order of mixed sync code, timers, promises and `await`, all correct when run.
- Build: the project above.
- Design: decide where a small app's state lives and how async errors reach the user, defended.

## Words to own
[1] type coercion, strict equality, truthy, falsy; [2] first-class function, callback, block scope,
closure, temporal dead zone; [3] primitive, object reference, mutation, shallow copy; [4] call site; [5] prototype chain;
[6] iterable, destructuring; [7] floating point, time zone, JSON; [8] named export, default export, package.json, lock file, bundler;
[9] exception, stack trace, debugger; [10] event loop, task queue, microtask; [11] promise, settled, unhandled
rejection; [12] async function, await, AbortController; [13] DOM node, event bubbling, event delegation;
[14] stale response
