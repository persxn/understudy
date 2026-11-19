# react: React for people who will build and maintain a team's user interface
kind: framework
aliases: reactjs, react hooks, jsx, single-page app
needs: javascript, html-and-css
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: react.dev/learn contents (order), render-and-commit, queueing updates, effects, you-might-not-need-an-effect;
  react.dev/reference useState, input (messages), useEffect, StrictMode, Component (error boundaries), memo;
  creating-a-react-app (14), typescript (1, 3-4); react.dev/learn state-as-a-snapshot,
  preserving-and-resetting-state, rendering-lists, refs; useContext (notes); testing-library.com queries/about (13); fullstackopen.com (outline)
unverified: step notes run on React 19.2 only, development build unless said; Testing Library from its docs; order of 12-14 is judgement

## Promise
Build and change screens of a real React app: state well placed, effects only where needed, data without races, behaviour tested; say why each re-render happened.

## The one idea
A component is a function from props and state to a description of the screen; React calls it and makes the page match. Picture: a recipe React cooks whenever an ingredient changes. Where it breaks: React decides when to cook, may cook twice, and keeps state by the dish's place on the table.

## In production
- Lint enforces Rules of React (`eslint-plugin-react-hooks`).
- Server data goes through a data library or framework loaders, not hand-written effects.

## Teaching order
1. Components and JSX: functions returning JSX, `{}` expressions, `className`, fragments, props, `children`; `.tsx` types (`React.ReactNode`).
2. Conditions and lists: `&&`, `? :`; `items.map` with a `key`, an item's name among siblings.
3. Events: `onClick={handleClick}`, not `handleClick()`; handlers as props; typed events (`React.ChangeEvent<HTMLInputElement>`).
4. State as a snapshot: `useState`; setters queue a re-render; updater `n => n + 1`; batching; replace objects and arrays, never mutate; `useState<User | null>(null)`.
5. Render and commit: what triggers a render; children render too; commit changes only differing DOM; `<StrictMode>` (opt-in) double renders; state kept by position, reset by `key`.
6. Where state lives: lifted to the nearest common parent; derived, never copied; `useReducer` when many updates touch one state.
7. Forms: controlled `value` plus `onChange`, or `defaultValue`; `onSubmit` with `e.preventDefault()`; disabled while sending; errors by field.
8. Refs: `useRef` for values that must not render (a timer id); `ref` on an element to focus it; never read `ref.current` in render.
9. Effects: syncing with an outside system (socket, timer, widget); dependencies by `Object.is`; cleanup; the development remount; stale closures; when not to use one.
10. Fetching without races: loading and error states; an `ignore` flag or `AbortController` in cleanup; waterfalls; error boundaries; data libraries, framework loaders.
11. Sharing: `createContext`, a provider, `useContext`; a new `value` object re-renders all consumers; custom hooks share logic, not state; Rules of Hooks.
12. Performance only when measured: the DevTools Profiler; `memo`, `useMemo`, `useCallback`; new object or function props defeat `memo`.
13. Testing behaviour: the project's runner (looked up); Testing Library `render`, `getByRole`, `user-event`; `findBy` for later content, `queryBy` for absence; a faked network.
14. Starting and shipping: a framework or build tool from react.dev's list (looked up), its `package.json` scripts (javascript 8); URL routes; the `build` output; client or server rendering.

## What it owns
- React calls your component, never you, when it chooses, maybe twice: rendering is pure (same inputs, same JSX; no fetches, timers or mutations).
- [3-5] One update: the handler ends, setters queued; React calls the component, then those it returns; commits differing DOM; the browser paints.
- [9] Then, per effect whose dependencies changed: old cleanup, new setup (usually after paint; after a click possibly before). Unmount runs every cleanup, drops state.
- [5,8] Kept between renders: state and refs (by type, position, `key`); rebuilt: locals and functions.
- Yours: server data and its cache, routing, state placement, styling, build.
- Look up when planned: the version (batching outside handlers, Strict Mode's checks), framework, build tool, Compiler; Server Components, Actions, `useEffectEvent`.

## Step notes
### 1
Need: I wrote `<Greeting name="Ada" />`; when does my function run, and who calls it?
Show: log `<Greeting name="Ada" />` as a value: an object whose `type` is your function; the body has not run; `root.render` runs it once; under `<StrictMode>`, twice in development, once in production. Both logs print since React 18 (React DevTools greys the second; 17 hid it) (react.dev/learn/render-and-commit, reference/react/StrictMode).
Explain: JSX only describes the screen; React decides when to call your component, so its body computes JSX, nothing else.
Try: build: a screen of theirs split into two typed components; predict: how often a body's `console.log` prints at start-up in development.
### 2
Need: I typed in a row, added an item on top, and my text jumped rows; why?
Show: rows holding an `<input>`, keyed by index; type in Milk, insert Bread on top: Bread holds the text; keyed by `id`, Milk keeps it (react.dev/learn/rendering-lists).
Explain: A key names an item among siblings; state and DOM follow the key, so index keys hand row 1's state to whatever is now first.
Try: fix: a list of theirs keyed by index until typed text survives an insert; predict: `{items.length && <List />}` with no items (`0`).
### 3
Need: I wrote `onClick={handleClick()}` and got "Too many re-renders" before clicking; why?
Show: `onClick={handleClick()}`, `handleClick` calling `setN(n + 1)`: before any click, "Too many re-renders. React limits the number of renders…" and an empty root (development build; production says "Minified React error #301") (react.dev/reference/react/useState).
Explain: Braces run during render, so `handleClick()` sets state while rendering, which renders again; a passed function runs on the click.
Try: fix: a handler of theirs needing an `id`, passed without calling it; build: a child button calling an `onSave` prop, event typed (inline handlers infer it).
### 4
Need: I set the state and logged it on the next line; why is it the old value?
Show: one handler: `setCount(count + 1)` three times, then `console.log(count)`. Most predict 3 and 3; React 19.2 logs 0, shows 1. Three `setCount(c => c + 1)`: 1 to 4. `setCount(count + 5)`, then a timeout logging `count`: 9 shown, 4 logged (react.dev/learn/state-as-a-snapshot).
Explain: Each render is a call with its own fixed `count`; a setter queues a value or an updater for the next call; updaters run in order.
Try: fix: a mutated object of theirs passed back to its setter (`Object.is` ignores it); predict: `setN(n + 5)`, `setN(n => n + 1)`, `setN(42)` from 0 (42).
### 5
Need: The parent re-rendered; why did one input lose my text and its neighbour keep it?
Show: `Form` has a counter and renders `<InnerField />`, defined inside it, and `<OuterField />`, outside. Type in both, click the counter: the inner input is empty, a new DOM node; the outer keeps both (React 19.2; react.dev/learn/preserving-and-resetting-state).
Explain: A state update (or the first mount) renders that component and all below it; commit changes only differing DOM; state belongs to a type at a position, and each `Form` render makes a new `InnerField` type.
Try: apply: reset a form for a new record with `key={record.id}`; predict: does a `Counter` survive its `<div>` wrapper turning `<section>` (no)?
### 6
Need: I copied a prop into state; why doesn't the child update when the parent's list changes?
Show: a parent adds items; children count open ones. `useState(items.filter(…))`: stuck at "1 open"; set by an effect: two renders per change, the first stale; computed in the body: one (React 19.2, Strict Mode off; on, each render is called twice in development) (react.dev/learn/you-might-not-need-an-effect).
Explain: State is what only this component knows; anything computable is computed in render; shared state lives in the nearest common parent.
Try: decide: state, derived, prop or URL for each datum of one screen of theirs; build: two siblings synced by lifted state, then a reducer.
### 7
Need: A customer was charged twice; how did one Pay button send two POSTs?
Show: `onSubmit` counts a POST, waits 500 ms; double-click Pay: 2 POSTs; `disabled={sending}` after `setSending(true)`: 1, as React "does not batch across multiple intentional events like clicks" (react.dev/learn/queueing-a-series-of-state-updates).
Explain: The first click's update is committed before the second click, so state that disables the form stops a resubmit.
Try: fix: a form of theirs that submits twice, double-clicked with Network open; build: errors shown by field after `onSubmit`.
### 8
Need: I kept a click count in a ref; why does the button still say 0?
Show: `useRef(0)`, button text `{ref.current}`, handler `ref.current++`. Three clicks: the console logs 1, 2, 3, the button says 0; after an unrelated state change, 3 (react.dev/learn/referencing-values-with-refs).
Explain: A ref is a box React keeps across renders and never watches: for what the screen does not show (a timer id, a DOM node).
Try: build: a search box focused on mount by a `ref`; fix: a timer id of theirs in a local variable, lost on re-render, so Stop fails.
### 9
Need: Why does my chat connect twice in development, and my interval stop at 1?
Show: under `<StrictMode>` an effect logs connect, disconnect, connect in development (since React 18), connect once in production (react.dev/learn/synchronizing-with-effects). `setInterval(() => setCount(count + 1), 100)` with `[]`: 1 after 1.3 s; `c => c + 1`: about 13. Plain JavaScript in Node 22: a closure from `render(0)` reads 0 after `render(1)`.
Explain: An effect starts syncing after commit, its cleanup stops it; it sees its render's values, so each value it reads is a dependency, compared by `Object.is`.
Try: fix: an effect of theirs missing a dependency, as lint says; decide: per effect of one component: keep, derive, handler, or `key`.
### 10
Need: I typed "hello" fast and got results for "hell"; how can an older request win?
Show: "hell" answering in 400 ms, "hello" in 100: "hello" shown at 200 ms, "hell" at 700; with an `ignore` flag set in cleanup, "hello" stays (React 19.2; Node 22 alike; react.dev/learn/you-might-not-need-an-effect).
Explain: Responses come in any order and nothing cancels a promise; cleanup marks the old one stale. Error boundaries catch render errors, not handler or async ones.
Try: fix: a search of theirs, network throttled, until fast typing ends right; build: an error boundary (a class or `react-error-boundary`) round one widget, made to throw.
### 11
Need: I put the user in context; why does every consumer re-render on any change?
Show: `value={{ user }}`, a `memo` consumer, 10 clicks on an unrelated counter: 11 consumer renders; `useMemo(() => ({ user }), [user])` as the value: 1 (react.dev/reference/react/useContext).
Explain: Consumers re-render when the value differs by `Object.is`, and an object literal is new each render; context passes a value; it manages no state.
Try: fix: a context value of theirs rebuilt each render, profiled before and after; build: a custom hook in two components, whose states stay separate.
### 12
Need: Typing lags; should I wrap everything in `memo`?
Show: production React 19.2 in Chromium: 1,000 simple rows re-render and commit in a few ms (development several times slower), 10,000 in tens of ms. A `memo` card given `person={{ name }}`: 11 renders in 10 parent updates; given `name`: 1 (react.dev/reference/react/memo).
Explain: `memo` skips a render only when every prop is `Object.is`-equal: it pays only for costly components whose props really stay the same.
Try: decide: for their slowest interaction, profiled: `memo`, state moved down, or nothing; predict: does `memo` stop renders from its own state (no)?
### 13
Need: It works when I click by hand; why can't my test find "Saved"?
Show: (Testing Library docs, not run here) for text arriving after a fetch, `getByText` right after `render` throws; `await findByText` retries until found, 1000 ms by default; `queryBy` returns `null` (testing-library.com/docs/queries/about).
Explain: Queries read the DOM as a user would, when called; later content needs `findBy`; a faked network decides when.
Try: build: a test per behaviour of a screen of theirs (`getByRole`, `user-event`, a faked API); fix: a test of state, rewritten to check what the user sees.
### 14
Need: It works under `npm run dev`; what does the server send when I deploy?
Show: a client-rendered app sends an empty `<div id="root"></div>` and a script; `renderToString` (React 19.2, Node 22) turns the same component into `<main><h1>Orders</h1>…` (react.dev/learn/creating-a-react-app).
Explain: Client rendering sends a shell filled in the browser; server rendering sends HTML, then React attaches; the `build` output ships.
Try: apply: build their app and open the output's `index.html`; decide: client or server rendering for two of their routes.

## Go deep, leave for later
- Deep steps: 4, 5, 6, 9 (state as a snapshot; render, commit and identity by position; where state lives; effects as synchronisation and when to remove one).
- Later: Server Components (next-js), React Native, state libraries, transitions, Suspense, portals.

## Never omit
- Each step on the learner's screens, React DevTools open.
- [9-10] Each effect's cleanup written and checked by the development double run.

## Wrong beliefs
- [4] "After `setCount(count + 1)`, `count` is the new value" (it holds this render's snapshot).
- [6] "State copied from a prop follows the prop" (`useState` reads its argument only on the first render).
- [2] "Keys only speed things up; the index is fine" (a key is identity: index keys move typed input on insert).
- [9] "`useEffect(fn, [])` runs once" (once per mount; Strict Mode in development runs setup, cleanup, setup).
- [9] "I choose the dependencies" (every reactive value the effect reads is listed; change the code, not the list).
- [11] "Context is a state manager" (it passes a value down; each consumer re-renders when it changes).
- [12] "`memo` everywhere makes it fast" (it pays only for costly renders with props unchanged).

## Failures to diagnose
- [3,4] "Too many re-renders": `onClick={handleClick()}` sets state during render.
- [4] TypeScript refuses `setUser(user)`: `useState(null)` inferred the type `null`.
- [4] The screen does not update: a mutated state object passed back; `Object.is` sees no change.
- [7] "A component is changing an uncontrolled input to be controlled" (development warning): `value` started `undefined`.
- [9] An interval stuck at 1: an effect with `[]` reads a stale `count`; use the updater.
- [10] Results for an older query: no cleanup ignored or aborted its slower response.
- [10] A blank page after one bad record: a render threw; no error boundary.
- [13] A `getBy` query misses text that arrives after a fetch: use `findBy`.

## Practice and project
Project: a screen of the learner's own app listing, filtering, creating and editing records from a real API; done when: no stale result when typing fast, input survives reordering, a test per behaviour passes, no derivable effect.

## Mastery ladder
- Use: build a list-and-form screen from a design and an API.
- Explain: walk a friend from a click to the new screen, naming render, commit and each effect run.
- Build: the project above.
- Design: place a stated screen's state (local, lifted, context, URL, server cache), defended.

## Words to own
[1] component, JSX, props, fragment; [2] key; [3] event handler; [4] state variable, state setter, updater function,
batching; [5] render, commit phase, Strict Mode; [6] lifting state up, derived state, reducer; [7] controlled input,
uncontrolled input; [8] ref object; [9] effect, dependency array, cleanup function, stale closure;
[10] request waterfall, error boundary; [11] context, provider, custom hook, Rules of Hooks; [12] memoization, React Profiler;
[13] user-event, query priority; [14] server-side rendering
