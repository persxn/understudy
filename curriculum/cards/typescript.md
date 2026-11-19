# typescript: TypeScript for people who will type real JavaScript code bases
kind: language
aliases: ts, tsc, tsconfig, static types for javascript
needs: javascript
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: typescriptlang.org Handbook contents (order), TSConfig reference (what `strict` turns on);
  typescript-eslint.io no-floating-promises, no-misused-promises (what a linter adds); TypeScript
  wiki FAQ (erasure, assertions, array covariance); effectivetypescript.com (outline); devblogs.microsoft.com
  announcing TypeScript 6.0 (changed defaults); traces compiled by `tsc` 6.0 and 7.0 (November 2026: same
  codes and messages), run in Node
unverified: option defaults, error codes and message wording can change by release; Node's type stripping run
  on one Node line

## Promise
Type a JavaScript code base so the checker catches bugs: read its errors, model data with unions and generics, guard every boundary, know what a passing check does not prove.

## The one idea
The types are a second program the compiler reads and then deletes: it checks, it never changes what runs. Picture: an inspector who checks the plans and leaves before anyone moves in. Where it breaks: the plans can lie (`as`, `any`, a wrong `.d.ts`), and nobody inspects the parcels delivered later (JSON, user input).

## In production
- CI runs `tsc --noEmit` as its own step: bundlers and Node strip types unchecked.
- Front end and API share request and response types; incoming data passes hand-written guards or a schema library.

## Teaching order
1. What the compiler does: `tsc` reads `.ts`, reports errors, writes `.js` with the types erased; `tsconfig.json`; the editor's checker; bundlers and `node` strip types without checking.
2. Annotations and inference: primitives, arrays, tuples; annotate parameters and exports, let the rest be inferred; `let` widens, `const` keeps a literal type; `as const`.
3. Object types and structural typing: `type` aliases, optional `?`, `readonly`; any value with the right shape fits; excess-property checks on fresh literals only; index signatures and `Record`.
4. Unions and narrowing: `string | null`, `strictNullChecks`; `typeof`, truthiness, `===`, `in`, `instanceof`; discriminated unions on `kind`; exhaustiveness with `never`; `?.`, `!`; narrowing kept across calls that undo it.
5. `any`, `unknown` and assertions: `any` spreads unchecked; `unknown` is narrowed first; `as` claims, never checks; predicates `x is User`; `satisfies`; `querySelector`'s `Element | null` narrowed by `instanceof HTMLInputElement`.
6. Functions: parameter and return types, optional and default parameters, function types for callbacks, `void`; `async` functions return `Promise<T>`; a forgotten `await` as a type error.
7. Generics: `<T>` inferred at the call, constraints with `extends`, `keyof`; `Array<T>`, `Promise<T>`; when a plain union is clearer.
8. `type` against `interface`, classes and enums: `extends` against `&`, declaration merging; `public`, `private` against `#private`; `enum` and parameter properties emit code (`erasableSyntaxOnly`).
9. Types from types: `Partial`, `Pick`, `Omit`, `Record`, `ReturnType`, `Awaited`; `typeof` a value, indexed access `User["id"]`; read mapped and conditional types before writing them.
10. Data from outside: `JSON.parse`, `response.json()`, environment variables and form input as `unknown`; a run-time guard or schema at the boundary; `catch (e)` is `unknown`.
11. Options that change correctness: what `strict` turns on (`strictNullChecks`, `noImplicitAny`, `useUnknownInCatchVariables`); `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`; `module`, `moduleResolution`, `verbatimModuleSyntax`; `skipLibCheck`.
12. Declaration files and third-party code: `.d.ts`, packages that ship types, `@types/` packages and the `types` option, error TS7016, `declare module`, `declare global`.
13. Migrating JavaScript: `allowJs`, `checkJs` or `// @ts-check` with JSDoc, then rename, leaves of the import graph first; `noImplicitAny` errors as the to-do list; `// @ts-expect-error` over `// @ts-ignore`.

## How it runs
- [1] `s instanceof Shape` for an interface `Shape`: TS2693: types are gone at run time.
- [1,8] `enum Color { Red, Green }` compiles to a real object; a type alias to nothing. `node` runs `const n: number = "seven"` unchecked and refuses the `enum` (`ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`).
- [2] `let m = "GET"` is `string`, so `req(m)` taking `"GET" | "POST"` fails (TS2345); `const m = "GET"` passes.
- [3] `const o: Opts = { url: "/a", retrys: 3 }`: TS2353 (`'retrys' does not exist`); the same object via a variable compiles.
- [3] `const animals: Animal[] = dogs; animals.push(new Animal())` compiles; then `dogs[0].bark()` throws `is not a function`.
- [4] `if (b.v !== null) { reset(b); b.v.length }` compiles though `reset` set `b.v = null`, and throws.
- [5] `JSON.parse('{"id":"7"}') as User` compiles; at run time `typeof u.id` is "string", `u.name` `undefined`.
- [6] `const v: number = load()` with `async function load()`: TS2322 (`Promise<number>`).
- [10] `catch (e) { e.message }`: TS18046 (`'e' is of type 'unknown'`).
- [11] Under `strict`, `const n: string = names[5]` compiles and holds `undefined`; with `noUncheckedIndexedAccess`, TS2322 (`string | undefined`).
- [12] Importing an untyped package under `noImplicitAny`: TS7016 (no declaration file); a `declare module` silences it and is never checked.

## Step notes
### 1
Need: The editor shows red, yet the app runs; so what does TypeScript do?
Show: `total(prices: number[])` summing with `reduce`, called `total([5, "3"])`. `tsc --strict total.ts`:
`error TS2322: Type 'string' is not assignable to type 'number'.`, yet `total.js` is written, types gone
(default options here). `node total.ts` (Node 22 here strips types) and `node total.js` print `53`.
Explain: `tsc` checks, then emits JavaScript with types erased; the check blocks nothing unless CI fails.
Try: apply: `tsc --noEmit` as a CI step of theirs, red on a planted error; predict: what `noEmitOnError`
changes for `node total.ts` (nothing: Node strips types and never runs `tsc`).
### 2
Need: I wrote `const req = { method: "GET" }`; why is `method` a `string`?
Show: `const req = { method: "GET", url: "/a" }; send(req.method, req.url)`, `send` taking `"GET" | "POST"`:
`TS2345: Argument of type 'string' is not assignable to parameter of type '"GET" | "POST"'`. `as const` or
`satisfies` a shape: clean (`let`: How it runs [2]).
Explain: Inference picks the widest type later code could need; properties stay writable, so `method` widens to
`string`.
Try: predict: the types of `[1, "a"]` and `["GET", "POST"] as const`; fix: a function of theirs annotated only
at its edges, still clean.
### 3
Need: I passed an order id as a user id; why did nothing complain?
Show: `type UserId = string; type OrderId = string;` `deleteUser(order.id)` compiles. With `class
Point { x = 0; y = 0 }`, `const p: Point = { x: 1, y: 2 }` compiles, and `p instanceof Point` is false.
Explain: Types are compared by shape, not name; an alias is only a second name.
Try: predict: an extra `z` via a variable (compiles), then in place (TS2353); explain: why `instanceof`
disagrees with the checker.
### 4
Need: We added a payment kind; totals went wrong with no compiler error; how?
Show: `Payment` is card, cash or the new refund, by `kind`; `net(p)` has `case "card"`, `case "cash"`,
`default: return 0`. A refund of 40 compiles and nets 0. Default replaced by `const unhandled: never = p`:
`TS2322: Type '{ kind: "refund"; amount: number; }' is not assignable to type 'never'`. Hover `p` per branch:
card, cash, then the rest.
Explain: Each check removes union members, so each branch knows which remain; only `never` should be left.
Try: predict: `if (typeof v === "object") v.length` for `string[] | null` (TS18047); fix: a `switch` of theirs
made exhaustive, until adding a member breaks the build at that `switch`.
### 5
Need: All typed, `tsc` clean; how does `user.name.toUpperCase()` crash?
Show: `load(): any` returns `JSON.parse('{"nme": "Ann"}')`; `const u: User = load()`, then
`u.name.toUpperCase()`. Strict, clean; run: `Cannot read properties of undefined (reading 'toUpperCase')`. As
`unknown`: `TS2322: Type 'unknown' is not assignable to type 'User'`. `load() as User`: clean, same crash. A
guard `x is User` testing only `"name" in x` passes `{"name": 42}`.
Explain: `any` fits every type and switches checking off where it flows; `unknown` allows nothing until
narrowed; `as` and `x is T` are believed.
Try: decide: each `any` and `as` in a file of theirs, kept with a reason or replaced; build: a guard
rejecting `{"name": 42}`, tested on three bad inputs.
### 6
Need: I forgot an `await` and it shipped; when does the compiler catch that?
Show: `if (isAdmin(7)) grant()`, async `isAdmin`: `TS2801: This condition will always return true since this
'Promise<boolean>' is always defined.` A bare `save(7);` or `forEach(async id => { await save(id) })`: clean.
Explain: A `void` callback type ignores its result, so an async one fits, and a dropped promise is legal: a
linter's job (typescript-eslint `no-floating-promises`, `no-misused-promises`).
Try: predict: `const ok: boolean = isAdmin(7)`; apply: those lint rules on their project, one finding fixed.
### 7
Need: My helper takes `any[]` and a key name; why bother with `<T>`?
Show: `pluckAny(users, "emial")` compiles to `any[]`; `.toLowerCase()` on an item throws. `pluck<T, K extends
keyof T>(rows: T[], key: K): T[K][]`: `"emial"` gives `TS2345: ... not assignable to parameter of type 'keyof
User'`; `"email"` gives `string[]`.
Explain: A type parameter is filled in from each call's arguments, so the result keeps the caller's type.
Try: build: `groupBy<T, K extends keyof T>` for their data; decide: generic or union for a `string | number`
parameter.
### 8
Need: I marked the field `private`; why is it in our API's JSON?
Show: `class Account { private pinHash = "9f86d0"; #secret = "s3cr3t"; ... }`: `JSON.stringify` gives
`{"owner":"ann","pinHash":"9f86d0"}`. `acct["pinHash"]` compiles (dot: TS2341). Two `interface Req`
merge; two `type Req`: TS2300.
Explain: `private` is a check, erased; `#` fields are private at run time. Interfaces of one name merge.
Try: fix: a class of theirs whose JSON shows a secret; predict: `--erasableSyntaxOnly` on
`constructor(public owner: string)`.
### 9
Need: I used `Omit` to drop the password hash; how did it leak?
Show: `type PublicUser = Omit<User, "passwrodHash">` (a typo) compiles, and `PublicUser` still requires
`passwordHash`. `Pick<User, "passwrodHash">`: `TS2344: Type '"passwrodHash"' does not satisfy the constraint
'keyof User'`.
Explain: Utility types are type functions: `Pick` limits keys to `keyof T`, `Omit` takes any key, so a typo
removes nothing.
Try: explain: `Omit`'s definition (go to definition); build: `Partial<Omit<User, "id">>` as their
update function's input.
### 10
Need: It compiles, so how can `user.name` be undefined?
Show: `const res = new Response('[{"id": 7, "fullName": "Ann Lee"}]')` (the API renamed `name`); `const users:
User[] = await res.json()`, no `as` or `any` written: clean; then `.name.split(" ")` in Node:
`Cannot read properties of undefined (reading 'split')`: `json()` is declared `Promise<any>`. As `unknown`,
through a guard testing each field's `typeof`: `Error: users[0]: bad shape {"id":7,"fullName":"Ann Lee"}`.
Explain: The checker knows only declarations; outside data is `unknown` until a check that runs makes it `User`.
Try: build: a guard or schema for an API response of theirs, tested with a renamed field; predict:
`process.env.PORT`'s type with Node's types.
### 11
Need: `strict` catches `users.find(...).name`; how did `users[i].name` crash in production?
Show: one-user array, `strict`: `users.find(x => x.id === 9).name` gives `TS2532: Object is possibly
'undefined'`; `users[9].name` is clean, then `Cannot read properties of undefined (reading 'name')`. With
`noUncheckedIndexedAccess`: TS2532 on both. `exactOptionalPropertyTypes` refuses `{ retries: undefined }` for
`retries?: number` (TS2375).
Explain: Each flag decides which run-time values a type admits; `strict` leaves out `noUncheckedIndexedAccess`
and `exactOptionalPropertyTypes`, so it trusts every index to hit.
Try: apply: `noUncheckedIndexedAccess` to their project, three errors fixed; decide: their CI's flags.
### 12
Need: I wrote a `.d.ts` to silence TS7016; is the library checked now?
Show: a local JavaScript package `slugger` returning a string: TS7016. Add `declare module "slugger" { export
default function slug(s: string): number; }`: clean, and `slug("Hi").toFixed(0)` throws `toFixed is not a
function`. The bare `declare module "slugger";` compiles too: all `any`.
Explain: A `.d.ts` describes JavaScript the checker never reads; it is believed, not compared.
Try: decide: shipped types, `@types/` or a small `.d.ts` for a dependency of theirs; explain: what
`skipLibCheck` skips.
### 13
Need: Our code is all JavaScript; must we rename every file first?
Show: `cart.js` with `// @ts-check` and JSDoc `@param {number} discount`, called with an input's `value`:
`TS2345` in a `.js` file. Over a line with no error, `// @ts-expect-error` gives `TS2578: Unused
'@ts-expect-error' directive`; `// @ts-ignore` stays silent.
Explain: The checker reads JavaScript, typed by JSDoc; `@ts-expect-error` complains once it is not needed.
Try: apply: `// @ts-check` on a leaf file of their import graph, each error fixed or marked with a reason;
predict: which of their errors `noImplicitAny` adds.

## Go deep, leave for later
- Deep steps: 4, 5, 10 (narrowing; what the checker is made to believe; checking data from outside).
- Later: conditional and mapped types, template literal types, decorators, project references, writing a library's types.

## Never omit
- Every lesson compiles under `strict` and runs; beside each rule, a case that passes the checker and fails when run.
- Look up when planned: the release and its defaults (`strict`, `types`, `module` have changed), the project's `tsconfig.json` and build, the validation library.

## Wrong beliefs
- [1] "TypeScript checks types while the program runs" (they are erased; nothing is checked at run time).
- [3] "Extra properties are always errors" (only on an object literal written in place).
- [5] "`as User` checks the data" (it tells the compiler to believe you; so does an `x is User` guard whose body checks nothing).
- [5] "`unknown` is just a stricter `any`" (`any` permits everything; `unknown` nothing until narrowed).
- [8] "An `enum` is only a type" (it emits a run-time object; a union of string literals emits nothing).
- [11] "`strict` makes the types sound" (index access, assertions, `any`, array assignment and narrowing across calls still let wrong values through).

## Failures to diagnose
- [4] A new union member silently taken by `default`.
- [5,10] A production crash on a typed field: the API changed shape and the code cast the JSON with `as`.
- [13] A real bug hidden for months by `// @ts-ignore` or a cast to `any`.

## Practice and project
Guided: fix each error from its message alone. Project: migrate one feature of the learner's own JavaScript code base under `strict`, with guards on every value from outside; finish line: `tsc --noEmit` clean in CI, no `any` added, malformed API data rejected with a clear error.

## Mastery ladder
- Use: type a module so `tsc --strict` passes without `any` or `as`.
- Explain: show in code three ways a program passes the checker and still crashes, and each fix.
- Build: the migration above.
- Design: choose compiler options and boundary validation for a stated project, defended.

## Words to own
[1] type checker, type erasure, tsconfig; [2] type annotation, type inference, literal type; [3] structural typing,
excess property check, index signature; [4] union type, narrowing, discriminated union, exhaustiveness check;
[5] any, unknown, type assertion, type predicate; [6] function type; [7] generic, type parameter, generic constraint;
[8] interface, intersection type, declaration merging; [9] utility type; [10] run-time validation;
[11] strict mode flags; [12] declaration file; [13] gradual migration
