# networking-basics: how a request crosses the network, for people who will build services
kind: system
aliases: networking, computer networks, how the internet works, tcp/ip
needs: none
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: hpbn.co contents (order), /primer-on-latency-and-bandwidth (fibre, last mile),
  /transport-layer-security-tls (handshake round trips, SNI); gist.github.com/jboner/2841832 (Dean and Norvig
  latencies); developer.mozilla.org How_browsers_work; gaia.cs.umass.edu/kurose_ross/eighth.php (top-down);
  engineering.fb.com/2021/10/05 outage-details; rfc-editor.org/rfc/rfc1035 sections 4.1.3, 6.1.3 (TTL: how long
  a record may be cached, counting down); expressjs.com/en/guide/behind-proxies.html (`trust proxy`, left-most
  `X-Forwarded-For`); expressjs.com/en/5x/api/application (`etag` setting)

## Promise
Follow one HTTPS request from a typed address to the server and back, say what each step costs in round trips, find which step failed.

## The one idea
Each layer adds one promise on top of a network that may lose, delay or reorder any packet: names become addresses, packets an ordered byte stream, the stream private and proven. Picture: letters through many sorting offices. Where it breaks: TCP makes letters feel like a pipe, and distance, not bandwidth, sets how soon a reply can come.

## In production
- Small requests are limited by round trips, not bandwidth (hpbn.co): reused connections and servers near the user (a CDN) are the usual fixes.
- Services call each other over HTTP, with timeouts and connection pools the engineer sets.
- Everything depends on DNS. Facebook, 4 October 2021: a backbone command cut off the data centres, DNS servers withdrew their routes, tools needing DNS failed too.

## Teaching order
1. One request at low resolution: the network panel and `curl -v` on the learner's own service; every stage named.
2. Latency and bandwidth: round-trip time, why distance sets a floor; `ping` a near and a far host; `curl -w` timings.
3. Names: the stub resolver asks a recursive resolver, which walks root, top-level and authoritative servers; A, AAAA and CNAME records; caching and TTL; `dig +trace`; a name broken on purpose.
4. Addresses, ports, routes: IP, private ranges, NAT, a socket as address plus port; a twenty-line socket server and client in the learner's language; `127.0.0.1` against `0.0.0.0` when binding; `ss -ltn`; `traceroute`.
5. TCP: SYN, SYN-ACK, ACK captured with `tcpdump`; a byte stream, shown by two `send`s read by one `recv` in step 4's programs; retransmission, flow and congestion control (slow start), head-of-line blocking.
6. UDP: datagrams with no handshake and no retransmission; why DNS and QUIC use it.
7. TLS: the certificate chain and SNI; the handshake round trips; what stays visible; a wrong-name certificate made on purpose.
8. HTTP: a request and response written by hand to step 4's socket; methods, status codes, headers, `Cache-Control` and `ETag`, keep-alive; HTTP/1.1, HTTP/2 multiplexing and HTTP/3 over QUIC, compared by the head-of-line blocking each removes.
9. In between: reverse proxies, layer 4 (TCP) and layer 7 (HTTP) load balancers, CDNs; what the server sees; `X-Forwarded-For` and the standard `Forwarded`; TLS termination at the proxy, plain or re-encrypted behind it.
10. When the network fails: refused, timed out, not resolved, packet loss; connect and read timeouts; the Facebook 2021 outage traced.

## Numbers and traces
- [2] Light in fibre: about 200,000 km a second; New York to London at best 56 ms round trip, to Sydney 160 ms; the last mile adds 10 to 65 ms (hpbn.co).
- [2] Dean and Norvig (about 2012): memory 100 ns, a same-datacentre round trip 0.5 ms, California to the Netherlands and back 150 ms.
- [5,7] A new HTTPS connection: one round trip for TCP, one for TLS 1.3 (two for 1.2), plus an uncached lookup, before the request; a reused one costs none.
- [1-8] The trace: resolver cache or recursive lookup to an A record and its TTL; SYN, SYN-ACK, ACK; ClientHello with SNI, ServerHello and certificate, Finished; `GET` with `Host`; status, headers, body. Matched to `curl -w` `time_namelookup`, `time_connect`, `time_appconnect`, `time_starttransfer`.

## Step notes
### 1
Need: My endpoint "takes a while": what happens between Enter and the JSON?
Show: `curl -v` with their service's URL twice, each line labelled: "resolved" (name), "Connected" (TCP), `>`
(the request, four text lines), `<` (the answer). Here, on Node, the second URL had no "Trying", only
"Re-using existing connection"; Python's `http.server` said "Closing connection".
Explain: A request is stages in order (address, connection, text, wait); each network crossing costs a round
trip; reuse skips two.
Try: predict: which lines vanish on the second URL; explain: the slowest stage in `curl -w '%{time_connect}
%{time_starttransfer}'` on their deployed service.
### 2
Need: Our API answers in 5 ms on my laptop; why a second abroad, and would more bandwidth help?
Show: 100 ms of round trip before their HTTPS service (deploy far away, or a 25-line asyncio relay holding each
chunk 50 ms each way, as here; a self-signed certificate from `openssl req -x509`), timed by `curl -w`. New TLS
1.3 connection: first byte 0.22 s (two round trips); TLS 1.2: 0.31 s (three); reused: 0.10 s (one). Ten
requests: 2.30 s on new connections, 1.17 s on one. The relay sets these, so they hold on any laptop. (A real
link adds a TCP round trip.)
Explain: Each exchange waits a full round trip, set by distance; bandwidth only shortens pushing the bytes.
Try: predict: first byte at 150 ms round trip, then measure; decide: reuse against doubled bandwidth for 12 API
calls a page, by arithmetic.
### 3
Need: I changed the A record an hour ago; why do some users still reach the old server?
Show: a ten-line Python UDP server on port 5300 (not 5353: laptops' mDNS holds it) answering any A question
with 10.0.0.7, TTL 60, asked with `dig @127.0.0.1 -p 5300 shop.test` (here, without `dig`, a ten-line Python
client: 27 bytes out, 43 back, one round trip; `dig`'s query is longer). That TTL lets every
resolver keep the answer 60 s, counting down (RFC 1035, 4.1.3, 6.1.3).
Explain: The stub asks a recursive resolver, which walks root, top-level and authoritative servers only on a
cache miss, then keeps the answer for its TTL.
Try: predict: the TTL `dig` (Windows: `nslookup -debug`) shows for their domain twice, 20 s apart; fix: a name failing with curl exit 6,
found along `dig +trace`'s path.
### 4
Need: My server answers curl on the machine, but my phone or a container's mapped port gets nothing; why?
Show: a twelve-line Python server on port 7000 and a client. Bound to `127.0.0.1`, reached at the machine's
network address (here 192.0.2.2): `ConnectionRefusedError`. Bound to `0.0.0.0`: both answer. The listener table
says why, `127.0.0.1:7000` against `0.0.0.0:7000` or `*:7000`: `ss -ltn` (Linux), `lsof -nP -iTCP
-sTCP:LISTEN` (macOS), `netstat -an` (any); here, without `ss`, read from `/proc/net/tcp`.
Explain: A listener gets only connections to the address it bound; for others the kernel answers the SYN with a
reset: refused.
Try: predict: what a phone on their network gets from their dev server, then `ss -ltn`; fix: a container app
bound to `127.0.0.1` behind `-p` (done when curl from the host answers).
### 5
Need: I `send` one JSON message and the other side's `recv` gets half, or two glued; is TCP broken?
Show: Python: `sendall(b"hello ")`, `sendall(b"world")`; the client waits 0.1 s, one `recv(1024)`: `b'hello
world'`. One `sendall` of 1,000,000 bytes: here 3 or 4 `recv` calls of 64 KB to 800 KB, different each run.
Explain: TCP numbers bytes, not messages: `recv` returns what has arrived, so the program marks message ends (a
length, a newline, `Content-Length`); the numbers let a lost segment be resent while later bytes wait.
Try: build: length-prefixed framing that passes the 1 MB test; explain: with sequence numbers drawn, why one lost
segment stalls bytes already here.
### 6
Need: If TCP does all that work, why do DNS and video calls use something that promises nothing?
Show: two `sendto` arrive as two `recv` (`b'hello '`, `b'world'`); 100 bytes read by `recv(10)` give 10, the
rest gone; `send` to a closed port returns 7, and only the next `recv` raises `ConnectionRefusedError` (Windows reports a
reset).
Explain: UDP hands each datagram to IP whole and forgets it: one round trip a question, loss left to the
application (DNS asks again; QUIC builds its own streams).
Try: predict: `recv(10)` on the second of two 100-byte datagrams; build: a client for step 3's server that asks
again after 1 s of silence, three times.
### 7
Need: HTTPS is encrypted, so can the office network still see which sites I visit?
Show: a seven-line Python listener printing what arrives; `curl --resolve clinic.test:8444:127.0.0.1
'https://clinic.test:8444/results?patient=42'`. Here: 517 bytes (ClientHello; the size varies by TLS library); `clinic.test` readable,
`/results` and `patient=42` absent.
Explain: The name goes first, unencrypted (SNI), to pick a certificate (unless both sides use Encrypted Client
Hello); the server proves it holds its key,
chained to a root the client trusts; then the request goes, encrypted.
Try: predict: curl's error for a certificate for `other.test` asked as `localhost` (`openssl req -x509`; exit
60); explain: each certificate `openssl s_client` shows for their host, and its signer.
### 8
Need: The browser shows "304 Not Modified"; was that the cache, and did it save time?
Show: a server sending `ETag` (Node's `http-server` here; in Express, its `etag` setting) behind step 2's relay.
With `If-None-Match`: `304`, 0 bytes, first byte after one round trip (0.11 to 0.13 s), as for the 200: the
body saved, not the round trip.
Explain: HTTP is text (method, path, headers, blank line; status, headers, body); cache headers let the client
ask "still this version?" or, until `max-age` ends, not ask.
Try: predict: what Node does with a hand-written request lacking the final blank line (here, Node 22: silent for 61.6 s, then `408 Request Timeout`, its headers
timeout: look yours up);
decide: `max-age`, `no-cache` or `ETag` for their list endpoint, with the staleness each allows.
### 9
Need: Behind our load balancer, why does my Express log show one 10.x address for everyone?
Show: a 15-line Python proxy routing by `Host`, appending the client to `X-Forwarded-For`, before their Express
app logging the socket's peer, the header and `req.ip` (here plain Node; no Express). From 192.0.2.2: peer
`127.0.0.1`, header `"192.0.2.2"`. Sent `X-Forwarded-For: 203.0.113.9`: `"203.0.113.9, 192.0.2.2"`; `trust
proxy` `true` takes the left-most, the forgery; `1` takes the entry its one proxy added (expressjs.com).
Explain: A layer-7 proxy ends the client's connection and opens its own; believe only entries your proxies added.
Try: fix: `trust proxy` set to their proxy count (done when a forged header leaves `req.ip` alone); decide: where
TLS ends for their service, and what tells the app it was HTTPS.
### 10
Need: The payment provider hung and took our API down; how long does my code wait, and is refused like slow?
Show: curl to local ports: nothing listening, exit 7 in 0 ms; a listener that never accepts, its `listen(0)`
queue filled (SYNs unanswered, as behind a dropping firewall), exit 28 at `--connect-timeout 3`; one that accepts
and never answers, exit 28 at `-m 3`. With no timeout, a default decides: here Python's `create_connection` gave
up after 134.9 s (Linux's SYN retries), Node 22's `fetch` after 300 s (its headers timeout), `urlopen` never
(still waiting at 400 s): look up the learner's libraries.
Explain: Refused is an instant answer; silence lasts your limit, or the library's or kernel's, holding a
connection throughout.
Try: apply: connect and response timeouts on every outgoing call, proved on the silent server; predict: requests
a second when 10 pooled connections each wait 30 s.

## Go deep, leave for later
- Deep steps: 2, 5, 7, 10 (round trips per stage, TCP's byte stream and loss, TLS trust, and what silence costs: where a request's time and its failures really come from).
- Later: routing protocols, link layers, wireless and mobile networks, IPv6 details, congestion-control algorithms, WebRTC; WebSocket and server-sent events (api-design).

## Never omit
- Every stage measured with a real tool, never only drawn.
- [10] A timeout on every network call the learner writes.
- Look up when planned: the HTTP and TLS versions the learner's tools use.

## Wrong beliefs
- [2] "More bandwidth makes every page faster" (small requests are limited by round trips).
- [5] "TCP delivers messages" (it delivers a byte stream; the program marks where messages end).
- [3] "A DNS change takes effect at once" (resolvers keep the old answer until its TTL runs out).
- [7] "HTTPS hides which site you visit" (it hides content and path; the address and usually the server name still show).
- [10] "No reply to ping means the server is down" (many networks drop ping; test the real port).

## Failures to diagnose
- [3,10] A name that does not resolve: a typo, a missing record, an old answer cached until its TTL ends (curl exit 6).
- [4,10] Connection refused: nothing listens on that address and port (often a server bound to 127.0.0.1 only; curl exit 7).
- [10] A connect timeout: a firewall drops the packets without answering (curl exit 28); a server that accepts and never answers hits the read timeout, also exit 28.
- [5] A message parser that works on localhost and breaks over a slow link or under load: it took one `recv` for one message.
- [7] A wrong-name certificate: it does not list the host name asked for (curl exit 60).
- [2,8] A slow page from a fast server: each request opens a new connection and pays every round trip again.
- [9] Every client logged with one address, the proxy's: read the forwarded header, only from a proxy you trust.

## Practice and project
Guided: predict the round trips before the first byte, then measure with `curl -w`. On your own: read a given capture. Project: the learner's own service behind a reverse proxy, one request traced in writing; finish line: its DNS, connect, TLS and first-byte times match `curl -w`, gaps explained.

## Mastery ladder
- Use: find which stage of a failing request broke, with `dig` and `curl -v`.
- Explain: walk a friend through pressing Enter on an address, round trip by round trip.
- Build: the project above.
- Design: place servers and a CDN for users on two continents, defended with round-trip numbers.

## Words to own
[1] time to first byte; [2] latency, bandwidth, round-trip time; [3] DNS resolver, DNS record, TTL;
[4] IP address, port, socket, packet, NAT; [5] TCP handshake, retransmission, congestion control,
head-of-line blocking; [6] UDP, datagram; [7] TLS certificate, certificate chain, SNI; [8] status code,
keep-alive, connection reuse, multiplexing, QUIC; [9] reverse proxy, load balancer, CDN, TLS termination; [10] timeout, connection refused
