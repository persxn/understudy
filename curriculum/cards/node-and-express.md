# node-and-express: Node.js and Express for people who will run a team's web service
kind: framework
aliases: node, nodejs, express, backend javascript
needs: javascript, networking-basics, sql-and-relational
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: nodejs.org/en/learn event loop, don't-block, backpressure (3-6), api/timers (3); expressjs.com using- and
  writing-middleware, error-handling, migrating-5, body-parser, behind-proxies, best practices,
  healthcheck-graceful-shutdown (8-14); node-postgres.com pooling, apis/pool (11); 12factor.net (7, 14); supertest
  README (13); github.com/expressjs/express lib/response.js, application.js and pillarjs/finalhandler (8);
  fullstackopen.com (outline); Shows run on Node 22; Express, `pg` from docs (not installed)
unverified: the step order is judgement

## Promise
Build, test and run an Express service over PostgreSQL that stays responsive, fails loudly and shuts down cleanly; say when Node runs each piece of your code.

## The one idea
One thread runs all your JavaScript, one callback at a time; slow work is handed off and returns as a callback. Picture: one waiter taking orders for every table while the kitchen cooks. Where it breaks: if the waiter cooks (a CPU loop, a sync call), every table waits.

## In production
- Stateless processes behind a reverse proxy; config from the environment; logs to stdout.

## Teaching order
1. The runtime: `node app.js`; what Node adds (`process`, `fs`, `http`); a bare `http.createServer`; `node --inspect`.
2. Packages in production (on javascript 8): `"type"` in `package.json` picks ES modules or CommonJS; `^` ranges and semantic versioning against the lock file; `npm ci`; `npm audit`.
3. Node's event loop (on javascript 10): timers, poll, check and close phases; `process.nextTick`; promise callbacks; inside an I/O callback.
4. What blocks it: a CPU loop, `readFileSync`, `pbkdf2Sync`, a huge `JSON.parse`, ReDoS; `perf_hooks.monitorEventLoopDelay`; the worker pool behind `fs`, `dns.lookup`, `crypto.pbkdf2`, zlib; worker threads.
5. Async errors in Node (on javascript 9, 11-12): error-first callbacks, `util.promisify`, `fs/promises`; an unhandled rejection ending the process; `uncaughtException` only to log and exit.
6. Streams and backpressure: `write()` returning `false`, `'drain'`, `highWaterMark`; `pipeline()`.
7. Configuration: `process.env` read and validated once at startup, failing fast; secrets outside the repository.
8. Express requests: `app.get`, `req.params`, `req.query`, `req.body`; `res.status(201).json(...)`; one response per request, `return` after it; status codes (networking-basics 8).
9. The middleware chain: `app.use`, `next()`, order (logger, parsers, auth, routes, 404, error handler); `express.json()` and its `limit`; `express.Router()`; CORS (`cors`) for a page served from another origin.
10. Errors: the four-argument `(err, req, res, next)` handler, registered last; `res.headersSent`; how `async` errors reach it (changed between majors: look up); no stack traces to clients.
11. Input and PostgreSQL: a schema validator answering `400`; `pg` `Pool`, `pool.query` with `$1` parameters; a transaction on one `pool.connect()` client, `release()` in `finally`; pool size against the server's connection limit.
12. Authentication and hardening: a session cookie (`httpOnly`, `secure`, a shared store) or bearer token; middleware setting `req.user` or answering `401`; ownership checked in the handler; Helmet, rate limits on login.
13. Testing routes without a network: `app` exported without `listen`; supertest `request(app).post(...).expect(201)`; a disposable test database.
14. Production: a process per core (cluster or the platform's replicas); `trust proxy`; request logs with an id to stdout; a health endpoint; `SIGTERM` and `server.close()`.

## What it owns
- [3] Node runs your top module once, then loops: due timers, I/O callbacks (connections and request data), `setImmediate`, close callbacks; after each callback, `nextTick` then promise callbacks.
- [8-10] Per request: Node parses the head and emits `request`; Express walks middleware and routes in registration order, by method and path; each calls `next()` or responds; no match: Express's 404; `next(err)` or a caught throw jumps to the next four-argument handler, else the default one.
- Yours: validation, authentication, the pool, timeouts, logs, process count, shutdown.
- Look up when planned: Node's LTS line, `--unhandled-rejections` mode, `server.close()` and idle keep-alive connections; the Express major (async errors, path syntax, unparsed `req.body`); the team's validator, logger, session store.

## Step notes
### 1
Need: Node has one thread; does my server serve one user at a time?
Show: a 9-line `http.createServer`: `/wait` answers after `setTimeout` 1 s, `/spin` loops 1 s. Ten `curl`s at
once: `/wait` 1.05 s in all, `/spin` 10.04 s (Node 22 here). Most predict the same.
Explain: One thread runs your JavaScript a callback at a time; waiting is handed off, computing holds it.
Try: build: their bare server answering JSON on two routes; predict: ten 0.3 s `/spin`s, then run.
### 2
Need: Same `package.json`; why does it work on my laptop and break in CI?
Show: npm's `semver`: `^1.2.3` takes 1.9.0, not 2.0.0; `^0.2.1` refuses 0.3.0. A dependency added, lock not
updated: `npm ci` exits 1, "... are in sync" (npm 10 here).
Explain: The range says what may be installed, the lock what was; `npm ci` installs the lock or fails.
Try: predict: what `^0.4.2` accepts of 0.4.9, 0.5.0, 1.0.0; fix: CI moved to `npm ci` (done when a stale lock
fails it).
### 3
Need: My logs print in an order I didn't write; why?
Show: `setTimeout 0`, `setImmediate`, a resolved promise, `nextTick`, then the same four inside an `fs.readFile`
callback; run it five times. Always `tick, promise` first; then timeout and immediate in either order (once
the timeout came after `readFile`): from the main module no order is defined. Inside the callback, every
run: `tick, promise, immediate, timeout` (Node 22 here; nodejs.org event-loop guide).
Explain: After each callback Node empties `nextTick`, then promises; the loop turns timers, poll (I/O), check
(`setImmediate`), close. A 0 ms timer waits 1 ms, so may miss the first turn; after I/O, check precedes timers.
Try: predict: a `then` that schedules a `nextTick`; explain: a self-rescheduling `nextTick` starving a timer.
### 4
Need: One endpoint gets slow and every request times out; why all of them?
Show: a route testing `/^(a+)+$/` on its input: 27 `a`s and `!`, 28 bytes, hold the loop for seconds (1.3 to
5 s on the machines here), `monitorEventLoopDelay`'s max the same, `/health` stuck behind; each extra `a`
doubles it. Eight `crypto.pbkdf2`: two waves of four, the second done at twice the first; `UV_THREADPOOL_SIZE=8`:
one wave, finished no sooner on two cores (Node 22 here).
Explain: Your own code (regex, loop, `*Sync`, `JSON.parse`) holds the one thread; only built-in work goes to the
pool, and cores cap it.
Try: fix: their heaviest route moved off the thread (done when `/health` answers in 10 ms meanwhile); predict:
eight hashes' waves on their machine.
### 5
Need: The service exited with code 1 and no request logged it; where did the error go?
Show: `/user` calls a rejecting `async` loader with no `catch`: curl exit 52, Node exits 1, the next curl is
refused (7). `--unhandled-rejections=warn`: alive, the request hanging forever (Node 22 here).
Explain: An error goes to whoever waits for it (caller, `await`, `.catch`, a callback's first argument); with
nobody, Node exits: the safe outcome.
Try: fix: their floating promises (done when the crash above answers 500); decide: who restarts their process.
### 6
Need: Saving a 2 GB upload ran the container out of memory; don't streams stop that?
Show: a 300 MB file into a slow writer (1 ms a chunk). `on('data', c => w.write(c))`: peak RSS 328 MB, 4,578
ignored `false`s. `pipeline(src, w, cb)`: 72 MB. Both about 5 s (Node 22 here).
Explain: `false` means the buffer passed `highWaterMark`: stop until `'drain'`; `pipeline` does it and destroys
every stream on error.
Try: fix: a route reading a whole file, rewritten with `pipeline` (done when RSS stays flat for a file bigger
than their memory limit); predict: the peak at `highWaterMark` 1 MB.
### 7
Need: Staging crashed on the first request, not at start; why not earlier?
Show: `PORT=3000 DEBUG=false`: `PORT + 1` is `"30001"`, `DEBUG` truthy; `listen(process.env.PORT)` with `PORT`
unset took random port 42119, silently (Node 22 here).
Explain: Environment values are strings or `undefined`: convert and check them all at start-up; fail at once.
Try: build: their config module (done when `env -i node app.js` names every missing variable, exit 1); fix: a
committed secret, found by `git log -S`, rotated.
### 8
Need: "Cannot set headers after they are sent to the client"; I answered once, didn't I?
Show: in their Express app, a route answering 404 for an unknown id with no `return`, then `res.json(user)`:
the client gets the 404; the terminal prints `ERR_HTTP_HEADERS_SENT` (`res.json` calls Node's `setHeader`);
the process lives, as Express catches the throw, logs it, closes the socket (express lib/response.js,
application.js; finalhandler). Run here on plain `http` (no Express): the same 404, then Node exits 1.
Explain: One response per request; `res.json` doesn't end your function, so the code after it runs.
Try: fix: `return` on every early answer (done when an unknown-id test logs nothing); apply: a route reading
`req.params` and `req.body`, answering 201.
### 9
Need: The logger misses some requests and one route hangs; does order matter?
Show: in their Express app, a logger registered after `app.get('/')` never logs `/`; auth calling `next()` only
when a token is sent: a tokenless request hangs until curl gives up; a body over `express.json()`'s `limit`: 413
(expressjs.com writing- and using-middleware, body-parser). Run here on a 20-line copy of the chain on plain
`http`, not Express: the first two alike.
Explain: A request walks one list in registration order until something answers or the list ends.
Try: build: logger, parser with `limit`, auth, routes, 404, errors (done when 200 KB gets 413); fix: their page
blocked by CORS, allowed for its origin only.
### 10
Need: My async route throws, my error handler never runs, the process dies; why?
Show: in their project, an `async` route awaiting a rejection: Express 5 passes it to `next`, 500; Express 4
didn't: exit 1 on Node 22 (expressjs.com error-handling, migrating-5). On step 9's copy (not Express),
4-style: curl 52, then 7, the process gone; with `r.catch(next)`: 500, then 200.
Explain: Express catches a synchronous throw and, in 5, a returned rejection; a throw in a timer reaches nobody
unless given to `next`.
Try: predict: a throw inside `setTimeout` in an Express 5 route; fix: a handler sending stacks (done when clients
get `{"error":"internal"}`).
### 11
Need: Under load requests hang, the database idle; a restart helps an hour. What leaks?
Show: (no `pg` here: a pool of 10 simulated by a semaphore; for real, system-design-foundations 1) a 5 ms query
took 2,008 ms behind ten 2 s reports; after 10 throws before `release()`, the next waited past 5 s. PostgreSQL
16, `max_connections=20`, two `pgbench -c 10`: "remaining connection slots are reserved".
Explain: A connection held T seconds serves 1/T queries a second, a leaked one none; all pools share one limit.
Try: fix: `release()` in `finally` (done when 20 failures leave queries working); decide: pool size for their
processes against `SHOW max_connections`.
### 12
Need: If my page has an XSS hole, can the attacker read the session cookie?
Show: a `sid` cookie read in headless Chromium (here): without `HttpOnly`, `document.cookie` is `"sid=abc123"`;
with it, `""`, still sent.
Explain: `HttpOnly` hides it from scripts, `Secure` from plain HTTP, `SameSite` from other sites.
Try: fix: `/orders/:id` serving any logged-in user (done when a two-user test gets 404); apply: a login rate
limit (sixth try a minute: 429).
### 13
Need: My route tests pass alone, but `npm test` hangs; why?
Show: two test files importing an `app.js` that calls `listen(47109)`: one `ok`, then `node --test` hung.
`app` exported, `listen(0)` in the test: `# pass 2` in well under a second (Node 22 here); supertest does
that (README).
Explain: A listening server keeps its process alive; a test that binds a free port and closes it sends real
HTTP through every middleware, then lets the process end.
Try: build: supertest for one route's 201, 400, 401 on a throwaway database (done when two runs pass); fix: a
test passing only after another.
### 14
Need: Every deploy brings a burst of 502s; what cuts requests?
Show: five 2 s requests in flight, `kill -TERM`: no handler, all five cut (curl 52), status 143; `server.close()`
in a `SIGTERM` handler: new connections refused, all five 200, exit 0 (Node 22 here).
Explain: The platform sends SIGTERM, waits, then SIGKILL; close, finish, `pool.end()`, exit before then.
Try: build: their shutdown, proved by the five-request test; decide: processes and pools per machine.

## Believable numbers
- [1,4] Bare `http` server, JSON: 20,000 to 30,000 requests a second, one process, two-core container, client on
  the same machine (here, three runs, Nov 2026).
- [4] Loop stopped (here): `pbkdf2Sync` 200,000 rounds about 0.1 s; `JSON.parse` of 13 to 21 MB about 0.15 s.

## Go deep, leave for later
- Deep steps: 4, 5, 6, 10 (what blocks the one thread, where an async error goes in Node and in Express, and
  backpressure: what takes down a service that worked on a laptop). Next in depth: the pool and shutdown (11, 14).
- Later: WebSockets, other frameworks (Fastify, NestJS), serverless.

## Never omit
- [3-6] Every ordering or blocking claim shown by a script whose output the learner predicts first.

## Wrong beliefs
- [6] "Streams are for speed" (a slow reader sets the pace; backpressure saves memory).
- [4] "The worker pool runs my slow JavaScript" (it runs only built-in work such as `fs`, `dns.lookup`, `crypto.pbkdf2`, zlib; your own CPU work blocks unless split up or moved to a worker thread).
- [2] "A `^` range only brings safe updates" (semver is a promise authors break; `npm ci` installs the locked tree).
- [10] "Any `throw` reaches the error handler" (a throw in a timer or `fs` callback crashes the process; older majors also miss `async` rejections; use `next`).
- [11] "A bigger pool is faster" (each process has its own pool; together they can exceed PostgreSQL's connection limit).
- [5,14] "Catching `uncaughtException` keeps the service up" (its state is unreliable; log, exit, restart).

## Failures to diagnose
- [4] Every request slow while one is served: a CPU loop.
- [4] Eight `crypto.pbkdf2` calls finishing in waves: the worker pool's size (look up) caps them.
- [5] The process exits with code 1 printing the error: a rejected promise nobody handled.
- [6] Memory climbing while copying a big file: `on('data')` writes ignore `false`.
- [8] "Cannot set headers after they are sent to the client": a second response, a `return` missing.
- [9] A request that hangs: a middleware neither called `next()` nor responded.
- [9] `req.body` missing: no `express.json()` before the route, or another `Content-Type`.
- [9] The browser blocks a call that `curl` answers: no `Access-Control-Allow-Origin` header.
- [11] Under load requests hang: clients checked out, never released.
- [14] Each deploy cuts requests: no `SIGTERM` handler.
- [14] Rare 502s from the load balancer: Node's keep-alive timeout below its idle timeout.

## Practice and project
Guided: predict each trace, then run it. Alone: find what blocks a service. Project: the learner's own JSON API over PostgreSQL with login, validation, logs, tests; done when: supertest covers each route and error, a slow route delays no other, a test shows a leaked client exhausting the pool, `SIGTERM` lets a running request finish.

## Mastery ladder
- Use: add a validated, tested route to an existing Express service.
- Explain: walk a friend through one request, naming each middleware and loop phase.
- Build: the project above.
- Design: choose process count, pool size, timeouts and shutdown order for a stated load; defend them.

## Words to own
[1] runtime; [2] semantic versioning; [3] poll phase, check phase, nextTick;
[4] blocking, worker pool, event loop delay, worker thread, ReDoS; [5] error-first callback, uncaughtException;
[6] stream, highWaterMark, drain event; [7] fail fast; [8] request object, response object, route
parameter; [9] middleware, router, body parser, CORS; [10] error-handling middleware; [11] input validation, client
release; [12] session cookie, security headers; [13] supertest; [14] cluster, graceful shutdown
