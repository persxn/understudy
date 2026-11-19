# computational-geometry: exact geometry on integer points, for contests
kind: skill
aliases: geometry, cross product, convex hull, segment intersection, point in polygon
needs: dsa-core-techniques
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: cses.fi/problemset Geometry, tasks 2189-2195, 1740, 3410 (limits, outputs); cses.fi/book/book.pdf
  ch. 29-30 (cross product sign, segment cases, ray parity, Pick, rotated Manhattan, closest-pair window,
  Andrew, the Fenwick sweep for Intersection Points); usaco.guide/plat/geo-pri (order, angles, Cut Length);
  cp-algorithms.com convex-hull (collinear flag, all-collinear case), check-segments-intersection,
  picks-theorem; codeforces.com 598F (two decimals, 10^-6); g++ 13 -fsanitize=undefined and Python 3.13 brute
  forces in /tmp (every Show: overflow, the double orientation, segment and ray tests, hull, Pick, closest pair)
unverified: step order and practice counts are judgement

## Promise
Solve point, segment, polygon and hull problems in integers that cannot overflow or round, decide every
degenerate case on purpose, and use floating point only where the answer is not an integer.

## The one idea
One number, the cross product, answers "left, right or on the line" and "how much area". Picture: turning a
steering wheel; its sign says which way you turn. Where it breaks: zero means "on the line", and every bug
of this subject hides in the zero case and in the size of the product.

## In production
- Contests: inputs are usually integers (CSES: |x| ≤ 10^9), so exact answers are expected.
- Work: maps, graphics and robotics use the same predicates. Book programs run: plan `run: cpp`.

## Teaching order
1. Points as integer vectors: `long long x, y`, `+`, `-`, dot and cross; bounds from the limits (|x| ≤ 10^9:
   cross products ≤ 8·10^18 < 2^63); `__int128` beyond.
2. Orientation: the sign of cross(b-a, c-a): left (+), right (-), on the line (0); the dot product's sign,
   ahead or behind; CSES Point Location Test. Everything later is built from these two signs.
3. Twice the signed area: the shoelace sum Σ cross(p_i, p_i+1), last vertex joined to the first, positive
   counter-clockwise; CSES Polygon Area (prints 2a).
4. Segment intersection, every case: proper crossing, an endpoint on the other segment, collinear overlap or
   apart; signs compared, never products; CSES Line Segment Intersection.
5. Point in polygon: boundary first, then a ray to the right with a half-open rule and an orientation; odd is
   inside; CSES Point in Polygon.
6. Lattice points: gcd(|dx|, |dy|) + 1 on a segment (`std::gcd`); Pick's theorem A = I + B/2 - 1, in integers
   I = (2A - B + 2) / 2; CSES Polygon Lattice Points.
7. Convex hull by Andrew's monotone chain: sort by (x, y), lower and upper chains, pop on `< 0` or `<= 0`;
   all-collinear input; CSES Convex Hull (prints every point on the hull).
8. Distances without roots: squared distances; Manhattan |dx| + |dy| as the larger gap in x+y or x-y; CSES
   Maximum Manhattan Distances (points added one at a time).
9. Closest pair by sweep line (dsa-core-techniques 11): sorted by x, a `set` by (y, x) (cpp-for-contests 6) of
   points less than d behind, searched for y within d; O(n log n); CSES Minimum Euclidean Distance (prints d²).
10. Angles and real answers: exact polar sort (half-plane, then cross), never `atan2` for ties; intersection
   points and lengths in `long double`, a scaled epsilon, no `==`; two-decimal inputs times 100; Codeforces
   598F Cut Length (10^-6).

## Judged by
- [1] The largest intermediate value is bounded from the limits and fits its type.
- [4] Every predicate's zero case is decided on purpose: touching, collinear, repeated points.
- [7] Collinear points are kept or dropped as the statement asks, and an all-collinear input is handled.
- [8-9] Distances are compared squared, in integers, until the output needs a root.
- [10] Floating point appears only where the output is not an integer, with its epsilon stated.

## Step notes
### 1
Need: My cross product came out negative for an obvious left turn; I stored the result in `long long`, so how?
Show: a=(-10^9,-10^9), b=(10^9,-10^9), c=(-10^9,10^9), a left turn. In `int`: -1651507200, and
`-fsanitize=undefined` names "2000000000 * 2000000000 cannot be represented in type 'int'". In `long long`
from the start: 4000000000000000000.
Explain: The type of a product is the type of its operands, decided before assignment; bound every intermediate
from the limits (differences 2·10^9, products 4·10^18, a cross up to 8·10^18 < 9.2·10^18).
Try: predict: the largest |cross| when |x| ≤ 10^9 and whether `long long` holds a sum of two, then check;
fix: their own vector struct so no `int` reaches a product, clean under `-fsanitize=undefined`.
### 2
Need: Coordinates are integers below 10^9 and a `double` has 15 digits; why not compute orientation in `double`?
Show: a=(-701999243, 326986382), b=(-376030054, 282263757), c=(-280747491, 269191091). Exact `long long`: +1,
a left turn. `double` with differences first: 0.0, "collinear". `double` expanded as ax(by-cy)+bx(cy-ay)+
cx(ay-by): -2.0, a right turn. Python floats agree.
Explain: Products pass 2^53 (9·10^15) and are rounded. The differences are exact and rounding never reverses
two products' order, so the first form can only collapse to 0 (3 million triples here: never a flip); a sum of
three rounded terms can land on the wrong side.
Try: predict: what `long double` gives on the expanded form (+1 here), then run; build: CSES Point Location
Test in `long long`, checked against a Python brute force.
### 3
Need: The shoelace formula gave me a negative area, or twice the right one; which is the bug?
Show: square (0,0),(0,4),(4,4),(4,0), clockwise: sum -32. Arrow (0,0),(4,0),(4,4),(2,1),(0,4), triangles
fanned from vertex 0: terms 16, -4, 8; sum 20 (area 10, confirmed by sampling); the absolute value of each
triangle, a common "fix": 28 (area 14).
Explain: Each term is twice a signed triangle; on a concave polygon the negative ones cancel the area counted
twice, so the absolute value is taken once, at the end.
Try: predict: the sum for the arrow listed clockwise (-20); apply: CSES Polygon Area, printing 2a.
### 4
Need: My segment test passes the samples and fails on the judge; which case did I miss?
Show: against a Python `Fraction` brute force on 200,000 random pairs in -3..3 (counts vary with the seed), the
strict test (signs opposite on both sides): 25,955 wrong (NO for touching (0,0)-(2,0), (2,0)-(3,1)); with `<= 0`: 488 wrong (YES
for collinear apart (0,0)-(1,0), (2,0)-(3,0)); signs plus bounding boxes: 0. Crosses multiplied: AB
(-10^9,-10^9)-(10^9,-10^9) and CD (-10^9,10^9)-(0,-10^9+1) never meet, yet 4·10^18 · 2·10^9 wraps negative: YES.
Explain: Opposite signs on both sides is the proper crossing; every zero is a point on a line, which counts
only inside the segment's bounding box.
Try: build: the four cases as four test pairs that each fail one wrong version; fix: a product test
(failure [4]) to compare signs, clean under `-fsanitize=undefined`.
### 5
Need: My ray test says a point in the middle of a diamond is outside; how?
Show: diamond (2,0),(4,2),(2,4),(0,2). Counting an edge when min y ≤ py ≤ max y: (2,2) and (1,2) OUTSIDE
(the ray meets vertex (4,2): two edges), (3,1) on an edge OUTSIDE. The card's rule: INSIDE, INSIDE, BOUNDARY.
Against a winding-number brute force on 90,013 queries in random star polygons: 13,424 wrong off the boundary,
against 0.
Explain: An edge counts only if exactly one end is strictly above the point (a vertex on the ray counts once)
and the point is on the edge's left as it goes up: an orientation, no division.
Try: predict: the closed-range answer for (0,0) in the diamond (5,0),(0,5),(-5,0),(0,-5) (OUTSIDE), then run; fix: failure [5]
in their own code, checked by the brute force.
### 6
Need: Pick's theorem gives me three times as many interior points as I can count; what did I pass it?
Show: triangle (0,0),(4,0),(0,3): 2A = 12, B = 4 + 1 + 3 = 8, I = (12 - 8 + 2)/2 = 3, as counting the grid
finds. Passing the shoelace sum 12 as A: I = 12 - 4 + 1 = 9.
Explain: Boundary points of an edge are gcd(|dx|, |dy|) + 1 counting both ends, so B is the sum of gcds; Pick
holds in A, and integers stay exact if written with 2A.
Try: predict: B and I for the square (0,0)-(5,5), then count; apply: CSES Polygon Lattice Points.
### 7
Need: My hull prints duplicated points on some tests, or misses points on an edge; what decides that?
Show: square corners plus (2,0): popping on `<= 0` gives 4 points, on `< 0` 5. Collinear (0,0),(1,1),(2,2),
(3,3) with `< 0`: 6 points, (2,2) and (1,1) twice. Against a brute force on 2,974 random sets in -3..3: all 23
mismatches were all-collinear inputs.
Explain: Built counter-clockwise, a chain pops while its last turn is clockwise; `<= 0` also pops a point on
the line, `< 0` keeps it; on a line both chains walk the same points, so that case is answered alone.
Try: fix: the all-collinear case (each point once); apply: CSES Convex Hull with every point on an edge.
### 8
Need: Isn't the farthest pair by Manhattan distance the farthest pair by ordinary distance?
Show: (0,0),(10,0),(6,6). Squared: (0,0)-(10,0) wins, 100 against 72. Manhattan: (0,0)-(6,6) wins, 12 against
10. The larger gap in x+y or x-y gives 12; against brute force on 2,000 random sets: no mismatch.
Explain: |dx| + |dy| is the larger of |du| and |dv| with u = x+y, v = x-y, so the farthest pair is decided by
two extremes of u and two of v.
Try: predict: the answer after each point of CSES Maximum Manhattan Distances' sample; apply: that problem.
### 9
Need: In the sweep, could the box above and below the point hold so many points that it is quadratic again?
Show: 2·10^5 random points with |x| ≤ 10^9: 17 distances computed in all, under 0.1 s here. A 447 by 447 grid,
the worst kind: 796,556 distances, never more than 4 in a box, under 0.1 s. All pairs: 2·10^4 points took 0.2 s in
C++; 2·10^5 means 100 times as many pairs.
Explain: Points already seen are pairwise at least d apart, so only a few fit in the d by 2d box; the `set`
finds them in O(log n), with d the square root of the best d² so far, rounded up.
Try: predict: what a `map` from y to x returns for (1,1),(3,1),(4,2) (4, not 2: failure [9]), then run;
build: CSES Minimum Euclidean Distance against brute force on 300 small sets.
### 10
Need: Why not sort points around the origin by `atan2` and be done?
Show: (10^9, 999999999) and (999999999, 999999998): cross -1, different directions; `atan2` in `double`
returns 0.78539816289744834865 for both (Python too); `atan2l` told them apart here.
Explain: Close directions differ by about 10^-18 radians, below a `double`'s step; the half-plane, then the
cross product, compares directions exactly.
Try: build: an exact polar comparator, checked against `atan2` on -3..3 where no ties are close; apply:
Codeforces 598F with two-decimal inputs times 100 for every predicate.

## Believable numbers
- Limits: `int` to 2.1·10^9, `double` exact integers to 9.0·10^15 (2^53), `long long` to 9.2·10^18; |x| ≤ 10^9
  gives crosses to 8·10^18.
- [9] Run here (g++ 13 -O2, Python 3.13, shared two-core machine, November 2026): all pairs of 2·10^4 points
  0.2 s in C++, of 4,000 points 1.35 s in Python; the sweep on 2·10^5 points under 0.1 s.
- [10] Codeforces 598F: coordinates to 10^5 with two decimals, answers within 10^-6.

## Go deep, leave for later
- Deep steps: 2, 4, 9 (the zero case and the size of a product decide every predicate; the window's bound is the
  card's one proof of running time).
- Later: counting intersections (CSES Intersection Points: a sweep that counts active horizontals in a y range)
  and Area of Rectangles need a Fenwick or segment tree (advanced-data-structures 4-8), a card this one does not
  need; they make good first problems after it. Also later: rotating calipers, half-plane intersection, convex
  hull trick, circles, 3D.

## Never omit
- A brute force on random points with coordinates in -3..3, where degenerate cases are common.

## Wrong beliefs
- [1] "`long long` always holds a cross product" (only to about 10^9 inputs; the sum or product of two
  such values overflows; use `__int128`).
- [2] "`double` is exact for integer points below 10^9" (products pass 2^53: a left turn computed as 0, or as a
  right turn when three products are summed; run here).
- [4-5] "Collinear means on the segment" (it may lie outside it; check the bounding box).
- [4] "Segments meet only where their lines cross" (an endpoint touching and a collinear overlap count too).
- [7] "The hull code handles collinear points by itself" (the comparison decides; test points on an edge).
- [9] "The sweep's box can fill up and make it quadratic" (compared points are d apart: at most 4 in a box on a
  full grid here).
- [10] "`double` with a small epsilon is enough" (a fixed epsilon fails at 10^9 magnitudes; prefer integers,
  or scale the error to the values).
- [3] "The shoelace sum is the area" (it is twice the signed area: negative for clockwise order).

## Failures to diagnose
- [1] `int` differences multiplied: 2·10^9 · 2·10^9 overflows `int`.
- [4] `c1 * c2 < 0` on two cross products overflows `long long` (run: 4·10^18 times 2·10^9, two positive
  crosses, wraps negative, so two positive signs look opposite; `-fsanitize=undefined` names it).
- [5] A ray through a vertex counted twice.
- [6] Pick's theorem given the doubled shoelace sum as A.
- [7] Keeping collinear points, an all-collinear input prints points twice (run: 4 points gave 6).
- [9] A `set` keyed by y alone silently drops points that share a y.

## Practice and project
Per step: its CSES problem, then about five Codeforces problems tagged geometry. Project: a header (vector,
orientation, segment test, point in polygon, hull, closest pair), each part stress-tested on small coordinates.

## Mastery ladder
- Use: get the CSES problems of steps 2 to 9 accepted.
- Explain: list the cases of segment intersection and show a pair of segments for each.
- Build: the project's header, passing its stress tests.
- Design: for a new problem, bound every intermediate value and choose integer or floating arithmetic, with
  the reason.

## Words to own
[1] vector, dot product, cross product; [2] orientation, collinear; [3] signed area, shoelace formula;
[4] degenerate case, bounding box; [5] ray casting; [6] lattice point, Pick's theorem; [7] convex hull, monotone
chain; [8] squared distance, Manhattan distance; [9] closest pair; [10] polar angle, epsilon, `long double`
