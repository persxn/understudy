# graphs-and-trees: graph and tree algorithms for contest problems
kind: skill
aliases: graph algorithms, bfs, dfs, dijkstra, shortest paths, lca, minimum spanning tree
needs: dsa-core-techniques, recursion-and-dynamic-programming
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/book/book.pdf ch. 11-16, 18 (order; ch. 18 ancestors and LCA); cses.fi/problemset and task pages (names,
  limits); usaco.guide silver and gold lists (order, functional graphs); cp-algorithms.com dijkstra_sparse,
  disjoint_set_union, lca_binary_lifting
unverified: readiness bands, counts and times are judgement

## Promise
Turn a problem into nodes and edges, then choose the traversal, shortest-path, ordering, tree, union-find or
spanning-tree algorithm its shape and weights call for.

## The one idea
Most of the work is modelling: what a node is (a cell, a town, a town-with-coupon-used) and what an edge is; the
algorithm then follows from weights and shape. Picture: towns and roads. Where it breaks: nodes are often
states, not places, and edges are made while searching.

## In production
- Contests: grids, dependencies and states are graphs in disguise.
- Work: build and package order is a topological sort; a cycle in it is a bug.
- Interviews: BFS on grids, prerequisites.
- A skill book whose programs run: plan `run: cpp` (`run: python` on the coding-interviews track:
  `collections.deque` for BFS, `heapq` for Dijkstra, an explicit stack for DFS, since deep recursion fails).

## Teaching order
1. Modelling and storing: adjacency lists, matrices, edge lists, grids as implicit graphs; Building Roads'
   and Counting Rooms' inputs read in.
2. DFS: components, flood fill, recursion against an explicit stack; Counting Rooms, Building Roads.
3. BFS: unweighted distances, parents to rebuild a path, many sources; Labyrinth, Message Route, Monsters.
4. Two-colouring and cycles (a colour clash means an odd cycle): Building Teams, Round Trip.
5. Dijkstra with a min-heap (cpp-for-contests 7; Python's `heapq` is one): why weights must be non-negative; skipping stale entries;
   0-1 BFS; Shortest Routes I, Investigation.
6. Negative weights, all pairs: Bellman-Ford, Floyd-Warshall; Shortest Routes II, High Score, Cycle Finding.
7. DAGs: topological order, cycle detection, DP in that order; Course Schedule, Longest Flight Route, Game Routes.
8. Trees: rooting, depth, subtree sizes, diameter by two searches; Subordinates, Tree Diameter.
9. DP on trees, then for every root: Tree Matching, Tree Distances I.
10. Binary lifting: `up[j][v]`, the 2^j-th ancestor; the k-th ancestor from k's bits; the lowest common
    ancestor by lifting to equal depth, then both while they differ; distance by depths; Company Queries I and
    II, Distance Queries. Successor graphs: advanced-graphs 1.
11. Union-find: one leader per set, path compression, union by size; Road Construction.
12. Minimum spanning trees: Kruskal with union-find, Prim, the cut property; Road Reparation.
13. States as nodes, then unseen problems: Flight Discount (town, coupon used); nodes, edges, then the algorithm.

## Judged by
- [1,13] The model is written before code: what nodes and edges are, and how many (a 1000 by 1000 grid is
  10^6 nodes); a matrix only for small n.
- [3,5-6] The algorithm matches the weights, and the choice is said: BFS for equal weights, 0-1 BFS, Dijkstra
  for non-negative, Bellman-Ford when negative.
- [5-6] Distances are `long long`, and "infinity" exceeds every real distance.
- [2,8-9] Recursion depth is bounded, or an explicit stack is used, when a path of 2·10^5 nodes is possible.
- [7] A topological order is checked to hold all n nodes.
- [5,10-12] Library code matched a brute force on small random graphs.
- [12] Kruskal's choice is argued by the cut property.

## Step notes
### 1
Need: The input is a grid of `#` and `.`, not a list of edges; where is the graph?
Show: a 1000 by 1000 open grid as adjacency lists: 3,996,000 directed edges, 54 MB. Kept implicit (the grid
plus four moves): 1 MB. A matrix for Building Roads' 10^5 towns would be 10^10 cells.
Explain: A node is a cell, an edge a legal move; neighbours are computed when needed, and you count nodes and
edges from the limits before choosing how to store them.
Try: decide: nodes, edges and their counts for Counting Rooms and Building Roads, from the limits; build: read
Building Roads into adjacency lists and print each town's degree.
### 2
Need: My Counting Rooms passed the samples; why does it crash on a big open grid?
Show: recursive flood fill on open n by n grids: 400 by 400 works, 160,000 calls deep; 1000 by 1000 dies with a
segfault (8 MB stack). The same search with a `vector` as stack finds 1 room, holding at most 499,501 cells.
Explain: DFS goes as deep as it can before backing up; on an open grid that path snakes through every cell, so
depth is the number of cells, a stack frame each.
Try: predict: the depth on a 300 by 300 open grid (90,000), then run; fix: their Counting Rooms with an
explicit stack, accepted.
### 3
Need: My DFS gives every node a distance; why does the judge say my route is not the shortest?
Show: Message Route on links 1-2, 2-3, 3-4, 4-5, 5-1, node 1 listing 2 first. DFS records distance 4, route
1 2 3 4 5; BFS records 1, route 1 5. Print both from the parent arrays.
Explain: The queue holds every node at distance d before any at d+1, so BFS reaches a node first by a shortest
route; DFS reaches it first by whichever route it tried first.
Try: predict: queue pushes on an open 1000 by 1000 grid when marking on pop instead of push (1,998,001 against
1,000,000), then run; build: Monsters as one BFS from all monsters at once.
### 4
Need: How can I tell two teams are possible without trying all 2^n splits?
Show: BFS colouring a 4-cycle gives teams 1 2 1 2; a 5-cycle stops at "edge 3-4 joins two of team 1".
Explain: Colours alternate with BFS distance; two same-coloured neighbours close a cycle of odd length, and no
split can colour an odd cycle.
Try: explain: rebuild the odd cycle from the clash edge and the parents; build: Building Teams on a graph with
several components, each started.
### 5
Need: My Dijkstra is right on small tests; why does it time out without the `continue` line I copied?
Show: 3000 nodes, 4.5·10^6 edges, built so nodes collect many heap entries (i to i+1 weight 1, i to j weight
2n−2i). With the line: 4,498,500 edge scans, under a second. Without: 4,495,503,999 scans, a thousand times
more, several seconds (a scan is cheap), same distances.
Explain: An improved distance leaves the old entry in the heap; with weights ≥ 0 a node's first pop is final,
and every later pop is stale: skip it, or its edges are scanned again.
Try: predict: the extra scans on a simple path (none), and why; apply: Shortest Routes I in `long long`
(distances here reached 9.2·10^9).
### 6
Need: My Dijkstra re-pushes improved nodes; why would a negative edge break it?
Show: edges 1→2 (1), 1→3 (3), 3→2 (−3), 2→4 (1). With a processed array (the CSES book's): dist 2 = 0 but
dist 4 = 2; the truth, from Bellman-Ford, is 1. Skipping only stale entries gets 1 by expanding 2 again, but
on a chain of k triangles h_i→h_{i+1} (0), h_i→m_i (4^(k−i)), m_i→h_{i+1} (−4^(k−i) − 2^(k−i)) it makes
3·2^k − 2 expansions: 3,145,726 for k = 20 (41 nodes, 60 edges).
Explain: Dijkstra relies on nothing found later being shorter. Bellman-Ford relaxes every edge n−1 times; an
improvement in round n proves a negative cycle.
Try: explain: on nodes 1, 2, 3, why 2 is final too early; build: Cycle Finding, printing the cycle.
### 7
Need: How do I know a valid order exists, and how do I run a DP over a graph?
Show: Kahn's algorithm on Course Schedule's sample: 3 4 1 5 2. Add 2→3: the queue empties after 4 5, and 1, 2, 3
keep in-degree 1: exactly the cycle. Code that never checks the length prints "4 5" as an order.
Explain: A node joins the order only when all its predecessors have; no node of a cycle ever does, so an order
shorter than n proves a cycle, and in a full order every dp[v] reads finished predecessors.
Try: fix: a solution printing a short order (failure [7]); build: Longest Flight Route, rebuilding the route
from parents.
### 8
Need: My tree DFS works on random trees; why does it crash on a chain of 2·10^5?
Show: Subordinates where v's boss is v−1. Recursive DFS: segfault at 2·10^5 with an 8 MB stack (here the limit
was near 174,000). Iterative: a preorder from a stack, then walked in reverse: 199,999. Python 3.13 here:
`RecursionError`, but with `sys.setrecursionlimit(10**6)` it finished.
Explain: Rooted, a node's answer reads only its children's; reversed preorder puts children first, with no
recursion.
Try: predict: whether a balanced tree of 2·10^5 nodes is safe recursively; build: Tree Diameter by two
searches, saying why the first ends at a diameter's end.
### 9
Need: Tree Distances I wants the farthest node from every node; are n searches really too slow?
Show: random trees. A BFS from every node: seconds at 2·10^4 nodes (4·10^8 steps), four times that at 4·10^4,
a hundred times at 2·10^5. Rerooting: 2·10^5 nodes in hundredths of a second, the same answers at 2·10^4.
Explain: Root once; keep each node's two longest branches down, through different children; then top-down,
up[c] = 1 + max(up[v], the best branch of v not through c). The answer is max(down, up).
Try: predict: what keeping one branch gets wrong on a star; build: Tree Matching, the state "dp[v][v matched?]"
written first.
### 10
Need: How do I jump k bosses up quickly, and how many levels does the table need?
Show: a chain of 2·10^5 (v's boss v−1), k = 150,000 from node 200,000: 17 levels (2^0 to 2^16) answer 181,072,
silently wrong; 18 levels give 50,000 in 8 jumps.
Explain: `up[j][v] = up[j-1][up[j-1][v]]`, built in O(n log n); k's bits say which jumps to take, so the levels
must cover the largest k: 18 for 2·10^5.
Try: predict: which k break 17 levels (all from 131,072); build: Distance Queries, checked against BFS on small
random trees.
### 11
Need: Road Construction asks for components after every road; why not rerun a DFS each time?
Show: 10^6 operations: 5·10^5 unions `p[find(i)] = find(i+1)` joining a chain, then 5·10^5 finds from its far end. Both tricks, or either
alone: milliseconds; neither: 10^5 operations took seconds (2.5·10^9 steps), 10^6 still ran after two
minutes.
Explain: Each set is a tree with its leader at the root; union links roots. Union by size keeps trees shallow;
path compression points every node it walks at the root.
Try: predict: the time of 2·10^5 operations with neither trick (quadratic: about 4 times 10^5's); build: Road
Construction, stress-tested against DFS.
### 12
Need: Does the cheapest set of roads joining every town also give the shortest routes?
Show: triangle 1-2 (2), 2-3 (2), 1-3 (3). Kruskal keeps 1-2 and 2-3, total 4; inside it 1 to 3 costs 4, while
the shortest route is the road 1-3: 3.
Explain: Cut property: for any split of the towns, the cheapest road across it belongs to a minimum spanning
tree; Kruskal takes roads cheapest first, skipping any whose ends union-find already joined.
Try: explain: why Kruskal's first road is safe, by the cut property; build: Road Reparation, IMPOSSIBLE when
fewer than n−1 roads are taken.
### 13
Need: In Flight Discount I find the cheapest route and halve its dearest flight; why is that wrong?
Show: flights 1→2 (30), 2→3 (30), 1→3 (80). Cheapest route 60, one 30 halved: 45. Nodes as (town, coupon
used): 6 nodes, edge (a,0)→(b,1) costing c/2; Dijkstra finds 40, the 80 halved.
Explain: When the best way on depends on more than the place (coupon used, keys held, time mod k), that joins
the node, and the graph grows by its number of values.
Try: decide: nodes and edges for a 1000 by 1000 grid where up to 10 walls may be broken, before code; build:
Flight Discount, compared with the halving idea on random small graphs.

## Believable numbers
- Run here (g++ -O2, Python 3.13, a shared two-core machine, November 2026; a laptop is as fast or faster): BFS
  on an open 1000 by 1000 grid and Dijkstra on 10^5 nodes and 2·10^5 edges: hundredths of a second in C++,
  about a second in Python.
- [2,8] An 8 MB stack held about 174,000 frames of a small recursive function here; judges' stacks differ:
  look them up.
- [5-6] Weights up to 10^9 on 10^5 nodes gave distances of 9.2·10^9: past `int`.

## Go deep, leave for later
- Deep steps: 3, 5, 7, 13 (choosing the traversal: why BFS and Dijkstra give true distances; DP in
  topological order; modelling with states as nodes).
- Later: strong components, 2-SAT, flows, bridges, Euler paths (advanced-graphs); Euler tours of trees,
  union-find extensions (advanced-data-structures).

## Never omit
- Every solution starts from a model on paper.

## Wrong beliefs
- [5-6] "Dijkstra works with negative edges if there is no negative cycle" (with a processed array a node is
  final too early; the stale-skipping version stays right but can expand nodes exponentially often).
- [2-3] "DFS finds shortest paths" (BFS does, in unweighted graphs; DFS only in a tree, where paths are unique).
- [3] "In BFS, mark a node when it leaves the queue" (mark it on entry, or it is queued many times).
- [2,8] "Recursive DFS is fine on any tree" (a long path can overflow the stack; know the limit or use a stack).
- [12] "A minimum spanning tree holds the shortest paths" (it minimises total weight, not distances).

## Failures to diagnose
- [5] Time limit with Dijkstra: no `if (d > dist[u]) continue;`, so stale entries are expanded again.
- [5-6] Wrong on big weights: distances overflow `int`.
- [1,3] Runtime error on grids: a neighbour outside the grid.
- [7] A "topological order" printed for a graph with a cycle: the order was never checked for n nodes.
- [10] Wrong far jumps: too few levels (depths up to 2·10^5 need 18).
- [11] Time limit on a long chain: union-find without path compression or union by size.

## Practice and project
Per technique: the chapter's problems, then about ten Codeforces problems tagged graphs or trees, your rating
to 300 above. Stuck: the editorial a step at a time, then code it closed. Log each miss: wrong model,
wrong algorithm, or bug. Project: a personal library (BFS, Dijkstra, topological sort, LCA, union-find), each
stress-tested.

## Mastery ladder
- Use: solve the chapter's problems from a given model.
- Explain: show on three nodes why Dijkstra fails on a negative edge.
- Build: solve three of four unseen, untagged Codeforces graph problems rated 1500 to 1800, an hour each.
- Design: model a new problem two ways (places or states as nodes), compare sizes, pick one.

## Words to own
[1] adjacency list, implicit graph; [2] connected component, DFS; [3] BFS, multi-source; [4] bipartite;
[5] relaxation; [6] negative cycle; [7] topological order, DAG; [8] rooted tree, diameter;
[9] rerooting; [10] binary lifting, lowest common ancestor; [11] union-find; [12] minimum
spanning tree, cut property; [13] state graph
