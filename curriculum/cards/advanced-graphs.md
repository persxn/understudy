# advanced-graphs: connectivity, Euler tours and flows for contest problems
kind: skill
aliases: scc, strongly connected components, 2-sat, bridges, eulerian path, max flow, bipartite matching
needs: graphs-and-trees
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/book/book.pdf ch. 16.3-16.4, 17, 19, 20 (successor paths, cycle finding, Kosaraju, 2SAT,
  Euler, flows, matchings, path covers); cses.fi/problemset Graph Algorithms, Advanced Techniques (names, task
  pages); usaco.guide/adv (graphs, flows: order); cp-algorithms.com/graph/dinic.html (bounds and their
  conditions, edge pointers), /graph/2SAT.html (Kosaraju numbering, reading the assignment);
  atcoder.jp/contests/practice2 (D, G, H); cses.fi task pages 1751, 1684, 1686, 1691, 1694, 1695, 1696
  (limits, 2026-11-19); runs with g++ in /tmp (every Show, in reviews/D9.md, rerun in VA.md)
unverified: step order past 6, the contest signals and practice counts are judgement

## Promise
Recognise a functional graph, a strong-connectivity, 2-SAT, bridge, Euler-tour, flow, cut or matching problem
behind its story, and solve it within the limits.

## The one idea
Each algorithm here is a DFS or BFS that keeps one extra fact per node or edge: a finish time, a low value, an
unused edge, a residual capacity. Picture: a maze walker's chalk marks. Where it breaks: flow needs many
searches, each on a graph the last one changed.

## In production
- Contests: flows hide behind small limits (a few hundred nodes); 2-SAT behind "each item takes one of two
  choices".
- Work: dependency cycles are strong components; single points of failure are bridges and cut vertices.
- A skill book whose programs run: plan `run: cpp`.

## Teaching order
1. Functional graphs: one successor each, every walk a tail into one cycle; three colours (or tortoise and
   hare) give each node its cycle and distance to it: Planets Cycles; graphs-and-trees 10's jumps on
   successors: Planets Queries I and II.
2. Strong components: Kosaraju (finish order, then the reversed graph; components in topological order) and
   Tarjan (low-link; reverse topological order); Flight Routes Check, Planets and Kingdoms; AtCoder practice2 G.
3. The condensation DAG and DP over it in topological order (graphs-and-trees 7): Coin Collector.
4. 2-SAT: clause (a ∨ b) as ¬a → b and ¬b → a; unsatisfiable iff x and ¬x share a component; otherwise x is
   true when comp[x] comes after comp[¬x] in topological order; Giant Pizza, AtCoder practice2 H.
5. Bridges and cut vertices: DFS tree, entry time, low value; the parent skipped by edge id, not by node;
   Necessary Roads, Necessary Cities.
6. Euler paths and circuits: degree conditions plus one component holding all edges; Hierholzer, O(m), a
   next-edge pointer per node and a used mark per edge; Mail Delivery, Teleporters Path, De Bruijn Sequence.
7. Maximum flow: residual graph, reverse edges, augmenting paths; Edmonds-Karp (BFS paths), O(VE²); Download
   Speed.
8. Dinic: level graph, blocking flow, edge pointers; fewer than V phases, O(V²E) in general, O(E√V) on unit
   (matching) networks; AtCoder practice2 D.
9. Minimum cut: equal to the maximum flow; read from residual reachability; Police Chase; cutting nodes by
   splitting each into an in-node and an out-node.
10. Bipartite matching as unit flow: School Dance; edge-disjoint paths read back from the flow: Distinct Routes;
   Kőnig's theorem (minimum vertex cover = maximum matching, read from the cut); a DAG path cover is n minus a
   matching.

## Judged by
- Is the model on paper (nodes, edges, capacities or literals) with its size, and the bound times size in time?
- [4] Does each clause add both implications, and does the assignment test match the SCC code's numbering?
- [6] Are degrees and edge connectivity both checked, and all m edges used?
- [7-10] Are capacities and the flow in `long long` where sums can pass 2^31?
- [2,5,6] Is recursion depth safe for a path of 10^5 nodes, or the DFS iterative?
- Is it checked against brute force on small random graphs (delete each edge and search, for bridges; every
  assignment, for 2-SAT)?

## Step notes
### 1
Need: Planets Cycles has 2·10^5 planets; why not teleport from each until a planet repeats?
Show: successors 1→2→3→4→5→3 give 5 4 3 3 3; the walk from 1 never returns to 1. A chain into a self-loop,
walked from every planet: 2·10^8 steps at n = 2·10^4 (under half a second), 2·10^10 at 2·10^5 (most of a
minute anywhere: a few 10^8 steps a second). Three colours (new, on this walk, done): 2·10^5
steps, milliseconds.
Explain: A walk that meets its own trail has found a cycle, whose nodes all answer its length; a tail node
answers one more than its successor, so each node is walked once.
Try: predict: the answers for successors 2 1 1 4, then run; build: Planets Queries II (k-th successors from
graphs-and-trees 10's table on successors; distance a to b from the cycle structure).
### 2
Need: Flight Routes Check: my DFS from city 1 reaches every city; can every city then reach every other?
Show: flights 1→2, 2→1, 2→3. DFS from 1 reaches all, but reversed, 1 never reaches 3: NO, 3 1. Kosaraju's
finish order is 3 2 1; a second pass on the same graph returns one component {1,2,3}; on the reversed graph,
{1,2} and {3}.
Explain: The last node to finish lies in a component nothing outside enters; reversed, a search from it reaches
exactly the nodes that reach it: its component. Repeat down the finish order.
Try: fix: a second pass on the same graph (belief [2]) until Planets and Kingdoms matches a both-ways BFS on
random 8-node graphs; build: Tarjan's low-link version, compared with Kosaraju's.
### 3
Need: Coin Collector's tunnels have cycles; can't I just memoise a DFS for the richest path?
Show: tunnels 1→2, 2→1, 2→3, 3→4, 4→3, 3→5, 1→6; room i holds i coins. Condensation: C0 {1,2} 3 coins → C1,
C2; C1 {6} 6; C2 {3,4} 7 → C3; C3 {5} 5. DP over it: 15 (1 2 3 4 3 5). Memoised DFS, an open room counting 0:
11, as room 4 was cached at 4 while 3 was open.
Explain: In a component every room reaches every other, so it is collected whole; the components form a DAG,
which Kosaraju lists in topological order.
Try: predict: the answer after adding 6→1 (21), then run; build: Coin Collector in `long long`, checked against
a search over (room, rooms visited) on random 8-room graphs.
### 4
Need: Giant Pizza: each person wants "this topping or that one"; how does a graph choose the toppings?
Show: (a∨b)(a∨¬b)(¬a∨b)(¬a∨¬b), both implications: one component {a, ¬a, b, ¬b}: impossible. One implication
per clause: four components, so "satisfiable", and whatever it reads breaks a clause (a = b = 1 here). On
20,000 random formulas, Kosaraju with comp[x] > comp[¬x] and Tarjan with < never broke a clause; flipped,
13,131 of 15,927 satisfiable ones broke.
Explain: "a or b" is "not a forces b, not b forces a"; x and ¬x in one component force each other. Else take the
literal later in topological order: no true literal then implies a false one.
Try: fix: the one-implication version (failure [4]) on those four clauses; build: Giant Pizza, the program
checking its own assignment, then accepted.
### 5
Need: Necessary Roads: deleting each road and searching again is 10^10 steps; what does one DFS know?
Show: roads 0-1, 0-1, 1-2. Skipping the parent node reports 0-1 and 1-2; skipping the parent edge's id, only
1-2. Against delete-and-search on 10,000 random multigraphs of up to 7 nodes: skipping the node was wrong on
3,489, three in four of the 4,612 with a doubled road and none without; skipping the edge, on none.
Explain: low[v] is the earliest entry time v's subtree reaches by one back edge; tree edge p-v is a bridge iff
low[v] > tin[p]. A second road to the parent is a real way up.
Try: predict: bridges and cut vertices of two triangles sharing a vertex (belief [5]), then run; build:
Necessary Cities by low[v] ≥ tin[p] (root: two children), stress-tested the same way.
### 6
Need: Mail Delivery's degrees are even, so I walk any unused street; why am I home with streets left?
Show: streets 1-2, 2-3, 3-1, 2-4, 4-5, 5-2. First unused street from 1: 1 2 3 1, stuck after 3 of 6.
Hierholzer backs up to 2, walks 2 4 5 2, splices it in: 1 3 2 5 4 2 1. 49,999 triangles sharing crossing 1
(n < 10^5): 4.5·10^5 scans with a next-edge pointer, milliseconds; without, each of crossing 1's 5·10^4
visits rescans its 10^5 streets: 7.5·10^9, seconds.
Explain: Undirected: 0 odd nodes (circuit) or 2 (path). A walk sticks only at its end; a node emitted only when
bare lets each detour close on itself and land in place.
Try: decide: Teleporters Path's tests (in = out but 1 one extra out, n one extra in; edges connected) and why
the output is reversed; fix: a rescanning Hierholzer (failure [6]) on the triangles.
### 7
Need: Download Speed: I push along any path with spare capacity; why is my answer too small?
Show: 1→2, 1→3, 2→3, 2→4, 3→4, capacity 1, 1 to 4, a DFS taking edges in that order. No reverse edges:
1 2 3 4, then stuck at 1. With them: 1 3 (back) 2 4 cancels 2→3: flow 2. On random graphs (capacities 1 to 5,
edges shuffled), 10,000 each, the greedy fell short on 10 at 6 nodes and 10 edges, on 14% at 10 and 40, and on
15% to 23% from 20 and 100 up to 200 and 1000: samples pass, test files fail.
Explain: Pushing f along u→v adds f to v→u, so a later path can reroute flow already sent; stopping when no
residual path remains is then optimal (step 9).
Try: predict: the result when 2 lists 4 first, then run; build: Download Speed with flow in `long long`
(failure [7]: 1000 pipes of 10^9).
### 8
Need: Edmonds-Karp passed Download Speed; why does it crawl on a matching network of 20,000 nodes?
Show: 10^4 + 10^4 nodes, 5 random edges each, unit capacities: flow about 9,920. Edmonds-Karp: one BFS per
path, 5·10^8 edge scans, seconds. Dinic: 8 phases, 2.2·10^6 scans, hundredths; without edge pointers 1.4·10^8,
most of a second. At 10^5 + 10^5: still 8 phases, about half a second.
Explain: A phase saturates every shortest path at once, so paths lengthen: under V phases, at most about 2√V on
unit networks (inner nodes have one entering or one leaving edge, capacity 1). The pointer skips dead edges for
good.
Try: predict: phases at 4·10^4 + 4·10^4, then run; fix: Dinic without pointers (failure [8]), scans counted.
### 9
Need: Police Chase wants the fewest streets to close; are they the streets the flow saturated?
Show: streets 1-2, 1-3, 2-4, 3-4, 4-5, 5-6, from 1 to 6. One path 1 2 4 5 6: flow 1, four streets saturated.
Reachable from 1 in the residual graph: 1 2 3 4; the one street leaving that side, 4-5, is the cut.
Explain: With no augmenting path left, edges out of the reachable side are full and edges into it empty, so the
flow equals that cut; no flow exceeds any cut, so both are optimal.
Try: build: Police Chase, the streets read from reachability, checked by deleting them; apply: the fewest
crossings to close, by node splitting, checked by brute force on 8 nodes.
### 10
Need: School Dance: if each boy takes the first free girl he likes, why are pairs missing?
Show: boy 1 likes girls 1 and 2, boy 2 only girl 1. First-free: 1 pair. Kuhn's augmenting path moves boy 1 to
girl 2: 2 pairs. On 2,000 random bipartite graphs up to 5 + 5, the smallest vertex cover (all subsets) equalled
the matching, and the cover read from the search was right each time.
Explain: A matching is unit flow; an augmenting path swaps pairs along it. Kőnig: boys not reached plus girls
reached from free boys cover every edge, one end per pair.
Try: build: Distinct Routes, paths read back along used edges; decide: a DAG path cover as n minus a matching of
out-copies to in-copies, checked by brute force on 7 nodes.

## Believable numbers
- Run here (g++ -O2, a shared two-core machine, November 2026; a laptop is as fast or faster): Kosaraju on 10^5
  nodes and 2·10^5 edges, hundredths of a second; 2·10^5 and 4·10^5, about a fifth.
- [2,4-6] Recursive Kosaraju on a path died near depth 130,000 with an 8 MB stack: Giant Pizza's 2·10^5 literal
  nodes can exceed it; judges' stacks differ: look them up.
- [7-10] Flow limits are small: Download Speed and Police Chase n ≤ 500, m ≤ 1000; School Dance 500 + 500.

## Go deep, leave for later
- Deep steps: 4, 5, 7, 9 (modelling choices as implications, low values, why reverse edges make flow
  correct, max-flow min-cut).
- Later: heavy-light decomposition (Path Queries II), centroid decomposition (Finding a Centroid, Fixed-Length
  Paths I), min-cost flow (AtCoder practice2 E), flows with lower bounds, Hall's and Dilworth's theorems,
  block-cut trees, general matching; Hamiltonian paths are bitmask DP (Hamiltonian Flights).

## Never omit
- Every model drawn by hand on the sample before code.

## Wrong beliefs
- [1] "A walk from any node comes back to it" (only nodes on a cycle; the others hang on tails into one).
- [2] "Kosaraju's second pass runs on the same graph" (on the reversed graph, by decreasing finish time).
- [4] "2-SAT is hard like SAT" (two literals per clause: linear; 3-SAT is NP-complete).
- [4] "`comp[x] > comp[¬x]` means x is true, whatever the SCC code" (only with Kosaraju's topological numbering;
  Tarjan numbers in reverse, so the test flips: run, the wrong direction broke a clause in 13,131 of 15,927
  satisfiable random formulas).
- [5] "A cut vertex always touches a bridge" (two triangles sharing one vertex: a cut vertex, no bridge).
- [6] "All degrees even means an Euler circuit" (the edges must also be connected).
- [7] "Augment greedily, no reverse edges" (later paths must be able to undo earlier ones).
- [8] "Dinic is always O(E√V)" (only on unit networks like matching; O(V²E) in general).
- [9] "The saturated edges are the cut" (the cut is the edges from the residual-reachable side to the rest).

## Failures to diagnose
- [5] Skipping the parent node, not the parent edge: run, edges 0-1, 0-1, 1-2 report 0-1 as a bridge.
- [6] No next-edge pointer: adjacency rescanned, time limit; a path printed backwards.
- [4] One implication per clause: "satisfiable" for unsatisfiable input.
- [8] Dinic without edge pointers: dead edges rescanned, a phase no longer O(VE), time limit.
- [7] Flow summed in `int`: overflow.

## Practice and project
Per step: its CSES problems, then about ten Codeforces problems tagged graphs or flows from your rating to 300
above. Project: a library (SCC, 2-SAT, bridges, Hierholzer, Dinic) stress-tested on small graphs; finish line:
AtCoder practice2 D, G and H accepted with it.

## Mastery ladder
- Use: solve the chapter's CSES problems from a given model.
- Explain: show on a three-node graph why flow without reverse edges stops short.
- Build: the library and its finish line above.
- Design: model a new problem as flow or 2-SAT, state the graph's size, and defend the algorithm.

## Words to own
[1] functional graph, tortoise and hare; [2] strongly connected component, low-link; [3] condensation;
[4] literal, clause, implication graph; [5] bridge, articulation point, back edge, low value; [6] Eulerian
path, Eulerian circuit, Hierholzer; [7] residual graph, augmenting path, capacity; [8] level graph, blocking
flow, unit network; [9] minimum cut, node splitting; [10] matching, vertex cover, path cover
