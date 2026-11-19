# api-design: HTTP APIs others build on and you can still change
kind: skill
aliases: rest api, api review, openapi, webhooks, api versioning
needs: networking-basics, sql-and-relational, system-design-foundations, caching-and-queues
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: RFC 9110, 9457, 6585 (reopened 2026-11-19), 6750, 7396, 8594, 9745 (meanings); datatracker idempotency-key-header -08,
  ratelimit-headers -11 (WG drafts, 2026-11-18); google.aip.dev, Microsoft Azure Guidelines.md, Zalando
  (outlines); Stripe docs and blog (idempotency, key pruning, pagination, versioning, webhooks, rate limiters); OWASP API Top 10 2023; graphql.org; grpc.io
unverified: grouping is judgement; Idempotency-Key, RateLimit are drafts: codes, names may change

## Promise
Design your service's API so clients can retry, page and survive change; defend it in review.

## The one idea
An API is a promise to strangers. Picture: a wall socket plugs are made to fit. Where it breaks: clients rely
on what you never promised (Hyrum's law).

## In production
- The contract (often OpenAPI) is reviewed before code; CI lints and diffs it for breaks.

## Teaching order
1. REST: resources (`/orders`, `/orders/{id}`) acted on by standard methods; RFC 9110: GET, HEAD safe; PUT, DELETE also idempotent, so a lost reply may be retried; POST neither; PATCH not by definition; else `POST .../{id}:cancel` (AIP-136).
2. API-first: an OpenAPI file (`paths`, `components/schemas`, `responses`) reviewed before code, live responses checked against it.
3. Shapes: one casing; opaque string IDs; RFC 3339 times with offset; money as integer minor units plus ISO 4217 currency; string enums that may grow; absent against `null` decided per field.
4. Status and errors: `200`, `201` + `Location`, `204`; `400` against `422`; `401` + `WWW-Authenticate` against `403`; `404`; `409`; what clients retry (`429`, `503`, `504`, after `Retry-After`; POST only with a key); RFC 9457 `application/problem+json`.
5. Pagination: offset, then an opaque cursor over a keyset query (sql-and-relational 10): `page_token` in, `next_page_token` out, empty at the end (AIP-158); a maximum page size; paged from release one.
6. Filtering and sorting: named filter parameters or a `filter` grammar (AIP-160); `order_by` ending in a unique tie-break; indexed fields only (sql-and-relational 8); a token bound to its filter and order; a field mask.
7. A retryable POST: one `Idempotency-Key` per operation, resent on retry; key, body hash, first response stored in the effect's transaction (caching-and-queues 8), replayed; draft codes: missing `400`, other body `422`, still running `409`; keys expire.
8. Partial updates and concurrency: PUT replaces all; PATCH as JSON Merge Patch (RFC 7396: a member sets, `null` deletes, arrays replaced whole); `ETag` on GET, `If-Match` on write, `412` if it changed, `428` (RFC 6585) if `If-Match` is missing.
9. Long-running operations: `202 Accepted` with an operation resource (`done`, then `error` or `response`, AIP-151), polled, or announced by webhook (step 12).
10. Rate limits: per API key at an API gateway, in a shared store; fixed window against sliding window or token bucket (rate plus burst); `429` + `Retry-After`; draft `RateLimit`, `RateLimit-Policy`; `429` against shedding `503` (reliability-and-observability 7).
11. Callers: API keys between servers, OAuth access tokens for a user, in `Authorization: Bearer` (RFC 6750), never in URLs; a scope per operation; `401` `invalid_token` against `403` `insufficient_scope`; object-level authorization (OWASP API1).
12. Pushing events: webhooks, at least once and unordered; HMAC-SHA256 over timestamp and raw body, compared in constant time, old timestamps refused; `2xx` at once, work queued. To apps: long polling, server-sent events (one way), WebSocket.
13. Changing safely: AIP-180's breaks (field removed, renamed, retyped; new required field; changed format, default, meaning); additions safe only for tolerant clients; Hyrum's law; `Deprecation` (RFC 9745), `Sunset` (RFC 8594); an OpenAPI diff in CI.
14. Not REST: gRPC between services (a `.proto` contract over HTTP/2, streams, deadlines, field numbers never reused); GraphQL (chosen fields, resolvers' N+1 fixed by batching, partial data with errors under `200`, depth and cost limits).

## Judged by
- [1] Methods keep their standard meaning?
- [4] Code can act on each error by status and `type`?
- [5-6] Every list paged by opaque cursor, capped, stably ordered?
- [7-8] A retried POST acts once; two editors lose nothing?
- [10-11] Every operation authenticated, scoped, ownership-checked, rate-limited?
- [12] A duplicate, late or forged webhook harmless?
- [13] Today's clients work after the change?

## Step notes
### 1
Need: My request timed out; can I just send it again, whatever the method?
Show: a 30-line `http.server`: two identical `POST /orders` give `201` `ord_1`, `201` `ord_2`; `PUT /orders/ord_1` twice leaves one order; `DELETE /orders/ord_2` twice: `204`, `404`. Many read that `404` as failure; the state is what one call left.
Explain: Idempotent is about the effect, not the reply: a repeated PUT or DELETE leaves what one left; a repeated POST makes another thing.
Try: predict: the order count after POST, PUT, DELETE are each sent thrice, then run it; decide: method and URL for five operations of theirs.
### 2
Need: Why write YAML nobody runs before the endpoint?
Show: a 20-line `openapi.yaml` (`Order`: `id` string, `total_cents` integer, `currency` `^[A-Z]{3}$`), a server written from a chat message; `jsonschema` on its response: `'total_cents' is a required property`, `17 is not of type 'string'`, `'eur' does not match`: three breaks, no client yet.
Explain: The file is the promise in a form people and machines read: disagreements surface in review and CI, not in a client.
Try: build: their endpoint in OpenAPI, and a CI check failing when a response leaves it; apply: retype a field, see it fail.
### 3
Need: Does it matter if an ID is a number, money a float?
Show: Node 22: `JSON.parse('{"id": 9007199254740993}').id` prints `9007199254740992`, another order; Python reads it exactly. `0.1 + 0.2` prints `0.30000000000000004`.
Explain: JavaScript reads JSON numbers as 64-bit floats, exact to 2^53: IDs go as opaque strings (integers also leak counts), money as integer minor units and a currency.
Try: predict: what JavaScript shows for their largest ID, then check; fix: one field of theirs whose type loses data, in OpenAPI.
### 4
Need: My API answers "Item out of stock"; what is wrong with that?
Show: `409` as `text/plain` and `application/problem+json` (`type` .../out-of-stock, `title`, `status`, `detail`, `instance`, `sku`); a Node client offers a back-order for each. Reworded "Sorry, that item is sold out": the text-matching client shows a generic error; the `type` one still offers.
Explain: Status gives the class, `type` what code switches on, `detail` is for people (RFC 9457: not parsed); `400` malformed, `422` well-formed, invalid.
Try: fix: an error of theirs into problem details with per-field `errors`; decide: retry or not for `400`, `409`, `429`, `503`.
### 5
Need: Why does page two show a row I saw on page one?
Show: seven items newest first, `limit=3`: `offset=0` gives item7, item6, item5; one `POST`; `offset=3` gives item5, item4, item3. A cursor, `WzEwNSwgNV0=` (base64 of the last row's `[105, 5]`): after the same insert, item4, item3, item2 (SQLite).
Explain: An offset counts from the top, so an insert shifts later pages; a cursor is "after this row", one index seek where `OFFSET` reads every skipped row (sql-and-relational 10): every row that keeps its sort key is seen once (one whose key changes mid-paging may be missed or repeated). Paging added later truncates old clients' lists.
Try: predict: offset paging after a page-1 row is deleted (here item4 never shown), then a cursor; build: capped cursor paging on their longest list.
### 6
Need: I sort by `created_at`; why do rows appear on two pages?
Show: PostgreSQL 16, 100,000 orders over five `created_at` values; `ORDER BY created_at LIMIT 50`, `OFFSET 0` then `50`: 42 IDs on both pages (top-N heapsort breaks ties differently per limit). `ORDER BY created_at, id`: none.
Explain: Ties have no defined order, so each query may break them differently; a unique last key makes it total. A field mask (`fields=id,total`) trims replies.
Try: fix: an `order_by` of theirs lacking a tie-break, until no ID is on two pages; decide: which filters need an index, by `EXPLAIN`.
### 7
Need: My POST timed out: was the order made? Can I retry without charging twice?
Show: a reply taking 1.5 s, `curl -m 1`: exit 28; a retry: `201` `ord_2`, two orders. With `Idempotency-Key`: the retry replays `201` `ord_3`; another body `422`; two at once: `201`, `409` (`UNIQUE constraint failed: idem.key`), one order (SQLite).
Explain: Lost on the way, died mid-work, reply lost: alike to a client, so it resends the key; unique, in the effect's transaction, it makes a retry find the first.
Try: predict: a retry once the key is pruned (Stripe: a new request); fix: their payment endpoint sent thrice, until one row, three equal bodies.
### 8
Need: Two of us edited one record and my change vanished with no error; how?
Show: A and B `GET` a profile (`ETag: "5ea161e7"`); A `PUT`s a new phone, `200`; B a new email, `200`; the record: B's email, the OLD phone. With `If-Match`, B gets `412`; without it, `428`.
Explain: PUT replaces all from a stale copy; `If-Match` makes a write conditional on the version read, so the loser re-reads (optimistic concurrency); merge patch sends less, races still.
Try: predict: B's edit as a merge patch of email alone, then run it; fix: their update endpoint, until two scripted editors get one `412` and lose nothing.
### 9
Need: The export takes two minutes; the request times out first. What do I return?
Show: `POST /reports`: `202`, `Location: /operations/op_1`, `Retry-After: 1`, `"done":false`; polls at 0 s and 1 s `done: false`; at 2 s `done: true`, `response` `{"url":"/reports/1.csv","rows":18234}`.
Explain: Work outlasting a request becomes a resource to poll, cancel or hear of by webhook; 202 is "intentionally noncommittal" (RFC 9110): store the operation.
Try: fix: restart the server mid-job, see the poll fail, store operations; decide: synchronous, 202 and poll, or webhook for three slow endpoints.
### 10
Need: I allow 5 a second; how did one client get 10 through in a fifth of a second?
Show: 5 sent at x.85 s, 5 just after the next second: a fixed window answers ten `200` in 0.16 s; a token bucket (5 tokens, 5 a second) five `200`, five `429` with `Retry-After: 1`.
Explain: A fixed window forgets at its boundary, so bursts either side double the rate; a bucket refills steadily, a burst at most its size; counted per server, each allows its share.
Try: predict: a fixed window's worst case at 100 a minute, then show it; decide: rate and burst for one endpoint, and when a client retries `429`, `503`.
### 11
Need: The token is valid, so the request is allowed?
Show: alice's bearer token on bob's `/orders/ord_2`: `200`; with an owner check, `404`. Bad token: `401`, `WWW-Authenticate: Bearer error="invalid_token"`; no scope: `403`, `insufficient_scope`. `?access_token=` is logged: `"GET /orders/ord_1?access_token=tok_alice HTTP/1.1"`.
Explain: A token says who; each handler checks this caller may touch this ID, taking the user from the token, never the body.
Try: fix: a handler of theirs loading by ID unchecked, until user B gets `404` on A's object; apply: scopes per operation in OpenAPI `security`.
### 12
Need: Every webhook fails its signature check, the secret right; why?
Show: HMAC-SHA256 over `timestamp.body`: raw bytes, `valid`; `json.dumps(json.loads(body))`, `INVALID` (`{"id":"evt_9"` became `{"id": "evt_9"`); replayed an hour later, refused (300-second tolerance).
Explain: It signs exact bytes: verify before parsing (`hmac.compare_digest`); the timestamp stops a replay attack; dedupe by event ID. Server-sent events push one way, WebSocket both.
Try: predict: whether swapping two keys breaks the signature, then run it; build: a receiver answering `2xx` at once, queueing, ignoring a repeated event ID.
### 13
Need: I only renamed a field for clarity; why do users see NaN?
Show: a Node v1 client (`o.total_cents / 100`); a Python one checking v1, `additionalProperties: false`. Rename to `amount_cents`: `Total: NaN EUR`, no error; strict: `'total_cents' is a required property`. Add a field: `Total: 25.99 EUR`; strict: `Additional properties are not allowed`.
Explain: Clients rely on each name they read, some on more (Hyrum's law): add, never rename; serve both, the old marked `Deprecation`, `Sunset`; a new version (path, media type, header) only to break.
Try: apply: rename a field over three releases, an old client's test passing; decide: which of five changes break (AIP-180).
### 14
Need: When would I not use REST, and what does GraphQL cost the server?
Show: `{ orders(first: 50) { id customer { name } } }` resolved per field over SQLite: naive resolvers, 51 queries; one batched `IN` (as DataLoader does), 2.
Explain: Clients composing resources choose fields, so a resolver runs per object: N+1 by default; gRPC fixes a `.proto` contract, field numbers never reused, for service calls.
Try: decide: REST, gRPC or GraphQL for three consumers of theirs, with reasons; predict: queries for 50 orders with customer and items, then batch.

## Believable numbers
- [7] Stripe may prune idempotency keys once 24 hours old (docs.stripe.com, 2026-11).

## Go deep, leave for later
- Deep steps: 5, 7, 8, 13 (cursors under writes, a retry acting once, two writers losing nothing, a change no client notices).
- Later: OAuth flows, hypermedia, CORS.

## Never omit
- Each step added to the learner's OpenAPI file, linted, called with `curl -i`.
- Look up when planned: OpenAPI version; the drafts' status.

## Wrong beliefs
- [1] "Idempotent means the same response every time" (it means the same effect: a second `DELETE` may answer `404`).
- [1,8] "PUT and PATCH are the same" (PUT replaces all and is idempotent; PATCH need not be).
- [4] "Return `200` with an error field" (caches, proxies and libraries act on the status).
- [5] "Offset paging is fine if sorted" (an insert before the offset shifts every later page).
- [7] "The key just drops duplicates" (it must replay the first response and refuse a changed body).
- [13] "Adding a field or enum value is always safe" (strict parsers and exhaustive switches break).

## Failures to diagnose
- [6] Pages repeat: sort on a non-unique column.
- [7] A double charge after a timeout: POST retried with no key.
- [8] A lost edit: PUT without `If-Match`.
- [11] Another user's order read by changing the ID.
- [12] Every webhook signature fails: the body was parsed and re-serialised before verifying.

## Practice and project
Guided: judge public API docs. Project: the learner's API in OpenAPI, mocked; finish line: paging
under inserts repeats nothing, a POST sent thrice acts once, two editors lose nothing, a diff shows no break.

## Mastery ladder
- Use: call an unfamiliar API correctly from its docs alone.
- Explain: show how a retried POST double-charges.
- Build: the project above.
- Design: review a proposed endpoint in writing by "Judged by".

## Words to own
[1] REST, resource, safe method, idempotent method, (collection); [2] OpenAPI, API-first; [3] opaque ID; [4] problem
details; [5] offset pagination, cursor, page token; [6] field mask; [7] idempotency key; [8] merge patch, ETag, optimistic
concurrency; [9] long-running operation, polling; [10] rate limiting, token bucket, API gateway; [11] access token, bearer token,
OAuth scope, object-level authorization; [12] webhook, signature, replay attack, server-sent events, WebSocket; [13]
breaking change, Hyrum's law, deprecation; [14] gRPC, protocol buffers, GraphQL, resolver
