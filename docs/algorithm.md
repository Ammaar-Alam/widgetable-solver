## 1. Closest formal puzzle class

The closest formal class is:

**Addressable directed maximal-slide removal puzzle with movable blockers.**

More concretely: each piece is an individually addressable token; when selected, it moves maximally along one fixed direction until either it exits the board or collides with the first blocking token. This puts the game closest to the **local-signal/full-step tilt** family, especially **Ricochet Robots/Lunar Lockout-like token-sliding puzzles**, but with two important changes: each pig has only one fixed direction, and the boundary is absorbing rather than a wall.

The screenshots support this interpretation: the pigs are not on a visible square grid, their headings appear sprite-oriented rather than strictly axis-aligned, and collision/exit behavior appears continuous or at least fine-quantized.

Comparison:

| Puzzle class                       |                                                                                                                                                                                                                               Similarity | Key difference                                                                                                                                                                  |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tap Away / arrow-removal games** | Very close in surface mechanics: tap pieces in their indicated direction to clear the board. Some published descriptions say obstructed pieces stop, and some variants require correct ordering or punish blocked taps. ([Plays.org][1]) | Most Tap Away variants are closer to monotone “remove only if path is clear.” Your rules allow blocked taps to physically reposition pigs, which makes the puzzle more dynamic. |
| **Ricochet Robots**                |       Very close formal primitive: select one token, it slides maximally until obstacle/contact. Ricochet Robots is described as moving a selected robot maximally in a chosen cardinal direction until a wall or robot is encountered.  | Ricochet lets the player choose direction each move; pigs have fixed headings. Ricochet has walls/targets; this game has absorbing edges and goal is remove all pigs.           |
| **Lunar Lockout**                  |                                                Similar because tokens stop only by other tokens and movement is maximal. Demaine and Hearn describe Lunar Lockout as having no walls; a token may slide only if another token stops it.  | Lunar Lockout is usually grid/cardinal and target-relocation; this is removal with fixed headings.                                                                              |
| **Ice-sliding puzzles**            |                                                                                                                                                                                                          Similar maximal sliding motion. | Usually a single avatar or several tokens choose among directions and stop on walls. Here each pig has one heading and the board edge removes it.                               |
| **Rush Hour**                      |                                                                                                  Similar blocking-order logic and vehicle-like constrained motion. Rush Hour’s generalized form is PSPACE-complete. ([ScienceDirect][2]) | Rush Hour cars can move forward/backward and can stop at chosen positions; pigs move one-way and cannot stop manually.                                                          |
| **Parking Jam-style games**        |                                                                                           Similar “move vehicles out in the right order” objective; app descriptions emphasize unblocking cars and choosing an order. ([Google Play][3]) | Parking Jam usually avoids collisions or treats them as failure/penalty; here collision is a legal repositioning operation.                                                     |
| **PushPush / Push-1**              |                                                                                    Similar “maximal slide after activation” in PushPush. Demaine et al. define PushPush as a pushed block sliding the maximal extent of its free range.  | PushPush has an agent that pushes blocks; pigs are directly tapped, and the blocker does not move.                                                                              |

A concise formal name I would use in code and writeups:

**Directed Tap-Slide Removal Puzzle, DTSR.**

---

## 2. Literature review and known complexity landscape

There does not appear to be a published complexity result for exactly this pig-removal model: fixed one-way headings, open rectangle, movable blockers, absorbing boundary, and all pieces must be removed. The closest known literature is on sliding-block, tilt, and maximal-slide puzzles.

Known relevant results:

1. **Rush Hour**: Flake and Baum proved generalized Rush Hour PSPACE-complete. Their formulation uses an (n \times n) grid, cars restricted to horizontal or vertical motion, a chosen exit, and a target car. ([ScienceDirect][2])

2. **Nondeterministic Constraint Logic, NCL**: Hearn and Demaine introduced NCL and proved it PSPACE-complete; they used it as a framework for proving PSPACE-hardness of many motion-planning and puzzle problems, including sliding-block problems. ([Erik Demaine][4])

3. **Ricochet Robots / Lunar Lockout with fixed geometry**: Balanza-Martinez et al. give a simpler proof that Ricochet Robots, equivalent to Lunar Lockout with fixed geometry in their model, is PSPACE-complete. Their model has addressable robots that move maximally in selected cardinal directions. 

4. **Lunar Lockout**: Demaine and Hearn’s survey notes that standard Lunar Lockout had partial results, while a generalization with fixed blocks is PSPACE-complete. 

5. **PushPush / pushing-block puzzles**: Demaine, Demaine, and O’Rourke proved PushPush and Push-1 NP-hard in 2D.  The broader survey also notes PSPACE-completeness for several PushPush/PUSH variants. 

6. **1×1 Rush Hour with fixed blocks**: Brunner et al. proved PSPACE-completeness for a highly restricted 1×1 Rush Hour variant with horizontal-only, vertical-only, and immovable unit blocks. ([DROPS][5])

Search algorithms relevant to an implementation:

* **A*** is the standard optimal heuristic graph-search method introduced by Hart, Nilsson, and Raphael. ([IEEE Xplore][6])
* **IDA*** and iterative deepening are useful when memory is the limiting resource; Korf showed depth-first iterative deepening has strong optimality properties for exponential tree search. ([ScienceDirect][7])
* **SAT-based planning** originated with Kautz and Selman’s planning-as-satisfiability formulation. ([Cornell Computer Science][8])
* **Bounded model checking** is relevant for SAT/SMT encodings of bounded-length plans. It uses SAT/SMT to reason over traces up to a bound. ([cs.cmu.edu][9])
* **MCTS** is useful for stochastic or adversarial domains, but is less naturally suited to deterministic sparse-reward puzzles; Browne et al. survey the method and its applications. ([IEEE Xplore][10])

Important caution: PSPACE-completeness of Rush Hour or Ricochet Robots does **not** automatically imply PSPACE-completeness of this pig game. The pig game has a strong monotonicity property: each pig moves only forward along its fixed heading and never reverses. That removes the reversible gadget structure used by many PSPACE-hardness proofs. For an explicitly discretized board, useful solution length is bounded by the total number of forward position increments plus removals, so the bounded-move decision version is naturally in NP under ordinary explicit-grid assumptions. I would not claim a PSPACE result for this exact rule set without a separate proof.

---

## 3. Formal model

### 3.1 Continuous geometric model

Let the board be a closed rectangle

[
B = [0,W] \times [0,H] \subset \mathbb{R}^2.
]

There are (n) pigs. Pig (i) has:

[
(K_i, x_i, u_i, a_i)
]

where:

* (K_i \subset \mathbb{R}^2) is its fixed local collision shape, usually an ellipse or capsule.
* (x_i \in \mathbb{R}^2) is its center/reference point.
* (u_i \in \mathbb{S}^1) is its fixed heading vector.
* (a_i \in {0,1}) indicates whether it is active.

The occupied region of active pig (i) is:

[
P_i(x_i) = x_i + K_i.
]

A state is:

[
S = (A, x_1,\dots,x_n)
]

where (A \subseteq {1,\dots,n}) is the active set. Removed pigs have (i \notin A).

### 3.2 Legal actions

An action is a tap:

[
\text{tap}(i), \quad i \in A.
]

In implementation, a tap that produces zero displacement and no removal should be treated as dominated and pruned, even if the game UI technically accepts it.

### 3.3 Collision raycast

When pig (i) is tapped, it moves along:

[
x_i(t) = x_i + t u_i,\quad t \ge 0.
]

Define the exit time as the first time the pig’s center leaves the eroded board:

[
\tau_{\text{exit}}(i)
= \inf {t \ge 0 : x_i + t u_i \notin B \ominus K_i }.
]

For another active pig (j), define the first collision time:

[
\tau_{ij}
= \inf {t \ge 0 : (x_i+t u_i+K_i) \cap (x_j+K_j) \neq \varnothing }.
]

Using configuration-space notation:

[
\tau_{ij}
= \inf {t \ge 0 : x_i - x_j + t u_i \in K_j \oplus (-K_i) }.
]

So continuous collision detection is a ray-intersection query against the Minkowski sum (K_j \oplus (-K_i)). Minkowski sums and configuration-space obstacles are standard in robot motion planning and collision detection. ([ScienceDirect][11])

Let:

[
\tau_i^* = \min_{j \in A, j \ne i} \tau_{ij}.
]

If:

[
\tau_{\text{exit}}(i) < \tau_i^*
]

then pig (i) exits and is removed.

Otherwise let:

[
j^* = \arg\min_{j \ne i} \tau_{ij}.
]

The pig moves to the contact position:

[
x_i' = x_i + \tau_{ij^*}u_i.
]

In a numerical engine, store:

[
x_i' = x_i + \max(0,\tau_{ij^*}-\varepsilon)u_i
]

or store exact contact but use non-overlap tolerance in later raycasts.

### 3.4 Transition function

[
T(S,i)=
\begin{cases}
(A \setminus {i}, x_1,\dots,x_n), & \text{if } i \text{ exits}, \
(A, x_1,\dots,x_i',\dots,x_n), & \text{if } i \text{ collides}.
\end{cases}
]

Other pigs never move during the transition.

### 3.5 Goal test

[
G(S) \iff A = \varnothing.
]

### 3.6 Cost function

Each tap costs 1.

However, every pig must eventually exit exactly once, so every solution has exactly (n) exit taps. Therefore:

[
\text{total taps} = n + #\text{collision taps}.
]

This is a key simplification. Optimizing fewest taps is equivalent to minimizing the number of non-removing collision taps.

If a move limit (L) exists, the meaningful slack is:

[
k = L - n.
]

If (k=0), the puzzle must be solvable by pure exit taps only.

### 3.7 Discretized / quantized model

For a game implementation, assume a finite set of center positions and heading bins.

Let pig (i)’s center lie on a fixed ray parameter:

[
s_i \in {0,1,\dots,L_i}.
]

The position is:

[
x_i(s_i)=x_i^0+s_i \Delta_i u_i.
]

A state is:

[
S = (A, s_1,\dots,s_n).
]

A tap increments (s_i) until the next increment would overlap another active pig mask or leave the board. If it leaves first, remove the pig. If overlap would occur first, stop at the last non-overlapping value.

The discretized transition is finite and deterministic. Since (s_i) never decreases, the useful state graph is acyclic after zero-displacement taps are pruned.

---

## 4. Is greedy edge peeling always correct?

### 4.1 Under the stated rules: no

A pure greedy edge-peeling strategy is **not complete** under your rules because collision taps can be necessary to break cycles.

Counterexample using four small disks in a square board:

Board:

[
B=[0,6]\times[0,6].
]

Let all pigs be disks of radius (r < 0.25).

Initial pigs:

| Pig |  Center | Heading | Initially blocked by |
| --- | ------: | ------: | -------------------- |
| (A) | ((2,2)) |    East | (B)                  |
| (B) | ((4,2)) |   North | (C)                  |
| (C) | ((4,4)) |    West | (D)                  |
| (D) | ((2,4)) |   South | (A)                  |

No pig initially has a clear exit ray:

[
A \to B,\quad B \to C,\quad C \to D,\quad D \to A.
]

A pure edge-peeling solver sees no removable pig and fails.

But the level is solvable:

1. Tap (A). It moves east until it touches (B), vacating the vertical line (x=2).
2. Tap (D). It now exits south.
3. Tap (C). It exits west.
4. Tap (B). It exits north.
5. Tap (A). It exits east.

So the blocker cycle can be broken by one collision move. This directly invalidates “only tap pigs with clear exit rays.”

### 4.2 When greedy edge peeling is correct

Greedy edge peeling is correct under a stricter monotone model:

* blocked taps are illegal, ignored, or losing moves;
* pieces never move except by being removed;
* removing a piece only deletes blockers and never changes any remaining piece’s position.

Define a directed dependency graph (G) with edge:

[
i \to j
]

when (j) is the first blocker along (i)’s exit ray. An exit-ray pig has outdegree 0.

In this static model, solvability is equivalent to (G) being acyclic after considering induced subgraphs during removal. Any sink-removal order works.

Proof sketch:

1. A legal removal can only remove a vertex of outdegree 0.
2. Removing a vertex deletes incident edges but creates no new edges.
3. If the graph is acyclic, every nonempty induced subgraph has a sink.
4. Therefore repeated removal of any available sink empties the graph.
5. If a directed cycle remains, no vertex in the cycle can ever become a sink until some cycle vertex is removed, which is impossible in the static model.

This theorem applies to many Tap Away-like variants, but not to the collision-repositioning model in your rules.

---

## 5. Complexity analysis

### 5.1 Fixed phone level

A single finite level is just a finite deterministic planning problem. Exhaustive search is always possible in principle.

### 5.2 Discretized generalized version

Assume:

* board size (W \times H) is explicit;
* each pig has finitely many quantized positions along its heading ray;
* each useful collision tap advances at least one quantization step;
* zero-displacement taps are ignored.

Then each pig’s scalar coordinate (s_i) is monotone nondecreasing. A useful solution has length at most:

[
n + \sum_i L_i.
]

So the bounded-move decision problem is in NP for explicit finite boards: the certificate is the tap sequence, and each transition can be checked in polynomial time.

This is a major difference from Rush Hour and Ricochet Robots, where reversible motion can create exponentially long state-space traversals and PSPACE-complete behavior.

### 5.3 Continuous model

For continuous ellipses/capsules with real coordinates, the exact complexity depends on the numeric representation and collision model.

* For a fixed tap sequence of length (k), validation is straightforward using continuous collision detection.
* If shapes and coordinates are algebraic, a bounded-(k) formulation can be encoded as SMT over real arithmetic, although ellipses/capsules introduce nonlinear constraints.
* Unbounded continuous reachability is more delicate because contact positions are real-valued and may not belong to a finite pre-enumerated set.

### 5.4 Known vs unknown

Known:

* Closely related maximal-slide and sliding-block puzzles have PSPACE-complete generalized versions: Rush Hour, Ricochet Robots/Lunar Lockout with fixed geometry, and several sliding-block variants. ([ScienceDirect][2])
* PushPush and Push-1 are NP-hard in 2D. 

Not known from the literature search:

* A published complexity classification for exactly this fixed-heading, all-removal, collision-repositioning pig model.

My assessment:

* The exact DTSR model is likely easier than Ricochet Robots/Rush Hour because of one-way monotonic motion.
* A generalized discretized version with obstacles, move limits, and engineered gadgets is plausibly NP-hard, but I would label that as conjectural unless a reduction is written.

---

## 6. Best exact solver for optimal fewest-tap solutions

The best exact formulation is not plain BFS over tap count. Use the fact that every solution needs exactly (n) exit taps.

Optimize:

[
#\text{collision taps}
]

instead of total taps.

Recommended exact solver:

## **Peel-Aware 0-1 A***

abbreviated **PA01-A***.

Action cost:

[
c(i,S)=
\begin{cases}
0, & \text{if tap } i \text{ exits},\
1, & \text{if tap } i \text{ collides}.
\end{cases}
]

Final answer:

[
\text{optimal taps} = n + \text{optimal collision cost}.
]

This gives a much shallower search objective. If a level has 50 pigs and needs 3 setup collisions, the meaningful optimal cost is 3, not 53.

### Solver comparison

| Method                                 |                                                                                                      Usefulness | Verdict                                      |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------: | -------------------------------------------- |
| BFS over tap count                     |                                     Optimal but expands all orders of removals and setup taps. Memory explodes. | Poor default.                                |
| 0-1 BFS / Dijkstra over collision cost |                                                                            Stronger because exits cost 0 extra. | Good baseline.                               |
| A* over collision cost                 |                                       Best exact default with admissible lower bounds and strong move ordering. | Recommended.                                 |
| IDA*                                   |        Lower memory; good when optimal extra collisions are small. Re-expands states heavily unless TT is used. | Good fallback.                               |
| Bidirectional search                   |                            Hard because removals are irreversible and inverse transitions are highly nonunique. | Usually poor.                                |
| SAT/SMT                                | Good for bounded-depth proofs or small discretized levels. Continuous collision makes formulas large/nonlinear. | Useful secondary tool.                       |
| Dynamic programming                    |                                      Works only for static edge-peel variants or small finite product lattices. | Not general enough.                          |
| MCTS                                   |                                                       Non-optimal, weak on deterministic sparse-reward puzzles. | Use only for finding an initial upper bound. |

---

## 7. Heuristics and reductions

### 7.1 Exit-ray detection

For each active pig (i), compute:

[
\tau_{\text{exit}}(i), \quad \min_j \tau_{ij}.
]

If:

[
\tau_{\text{exit}}(i) < \min_j \tau_{ij},
]

then (i) is an exit-ray pig.

Implementation:

```text
raycast(i):
    t_exit = distance_to_board_exit(i)
    best_t = +inf
    best_blocker = None

    for j in active_pigs_except_i:
        t = swept_collision_time(i, j)
        if 0 <= t < best_t:
            best_t = t
            best_blocker = j

    if t_exit < best_t:
        return EXIT(t_exit)
    else:
        return HIT(best_t, best_blocker)
```

Use a spatial index, such as a uniform grid or R-tree, to avoid testing every pair on every raycast.

### 7.2 Blocker graph

Build two graphs:

1. **Immediate blocker graph**:

[
i \to b(i)
]

where (b(i)) is the first blocker hit by (i), if any.

2. **All-blockers graph**:

[
i \to j
]

if (j)’s shape intersects (i)’s swept exit tube before the board edge.

The immediate graph predicts the next transition. The all-blockers graph predicts stopper usefulness and future dependencies.

### 7.3 SCC analysis

After removing all currently obvious exit-ray pigs in a hypothetical static peel, remaining SCCs identify collision-required regions.

Use SCCs for:

* detecting blocker cycles;
* selecting which pig to tap when no exit exists;
* estimating lower bounds;
* move ordering.

A conservative admissible lower bound is:

[
h(S)=
\begin{cases}
0, & \text{if static zero-peel empties the board},\
1, & \text{otherwise}.
\end{cases}
]

A stronger but more delicate lower bound counts independent SCC cycles whose breaker sets are disjoint. For each cycle (C), define a breaker set (B(C)): pigs whose next collision move can change at least one immediate blocker relation inside (C). A set of cycles with pairwise disjoint breaker sets requires at least that many collision taps. This is admissible.

A raw “number of blocker cycles” heuristic is useful for ordering, but should not be used for optimal pruning unless the implementation proves that one collision cannot break multiple counted cycles.

### 7.4 Deadlock detection

Safe deadlocks:

* No pig has an exit ray.
* Every tap has zero displacement because the pig is already in contact with its blocker.
* No active pig can move by more than tolerance (\varepsilon).

Then the state is dead.

Move-limit deadlocks:

[
\text{taps used} + |A| > L
]

is impossible because every active pig needs one exit tap.

Collision-budget deadlock:

[
g_{\text{collision}} + h_{\text{admissible}} > k
]

where (k=L-n).

Heuristic deadlocks, not safe for optimal pruning unless proven:

* dense mutual-contact SCCs;
* cycles whose members all point into each other with no external release line;
* states where every cycle-breaking tap increases blocker count.

Use those for move ordering or beam pruning, not for exact proof unless validated.

### 7.5 Safe-peel reductions

An exit pig (e) is **provably safe to remove immediately** if no other active pig can ever use it as a stopper.

Because every pig moves only along its fixed heading, pig (j)’s future centers lie on the same forward ray:

[
R_j = {x_j + \alpha u_j : \alpha \ge 0}.
]

If (e)’s shape is not intersected by the swept tube of any other pig’s future forward ray, then (e) can never be a blocker for any future move.

Safe-peel theorem:

If (e) has a clear exit ray and no other pig can ever collide with (e), then removing (e) now preserves solvability and optimal collision cost.

Reason: removing (e) cannot alter any other current or future transition. It contributes one unavoidable exit tap, so commuting it to the front is harmless.

### 7.6 Move ordering

Order candidate actions by:

1. safe exits;
2. exits that unblock many immediate blockers;
3. exits with low stopper value;
4. collision moves inside SCC cycles;
5. collision moves maximizing newly available exit rays;
6. collision moves maximizing static peel closure;
7. collision moves with large positive displacement;
8. avoid zero-displacement taps.

Useful score:

[
\text{score}(i)
===============

10 \cdot \Delta \text{removed_by_peel}

* 5 \cdot \Delta \text{exit_rays}

- 4 \cdot \Delta \text{cycle_count}
- 2 \cdot \text{stopper_value}(i)
- \text{collision_cost}.
  ]

For exact A*, this score affects only ordering, not pruning.

### 7.7 Canonicalization of equivalent pigs

If pigs are indistinguishable except for position, heading, and shape:

[
\text{canonical}(S)
===================

\text{sorted}{(\text{shape_id},\text{heading_id},q(x_i),q(y_i)) : i \in A}.
]

Here (q) is fixed-point quantization.

This collapses symmetric states. Store a mapping back to actual screen objects for output reconstruction.

### 7.8 Transposition table hashing

For labeled pigs:

[
H(S) = \bigoplus_{i \in A} Z[i,\text{heading}_i,q(x_i),q(y_i)].
]

For unlabeled canonical states, hash the sorted canonical tuple.

Use:

* 64-bit hash for speed;
* 128-bit hash or tuple verification for exact solving;
* store best known collision cost (g);
* optionally store predecessor and action for solution reconstruction.

Zobrist hashing is standard in board-game transposition tables. ([Chess Programming Wiki][12])

---

## 8. Exact solver pseudocode: PA01-A*

```python
def solve_exact(initial_state, move_limit=None):
    n0 = initial_state.num_active()

    if move_limit is not None and move_limit < n0:
        return UNSAT

    collision_budget = None
    if move_limit is not None:
        collision_budget = move_limit - n0

    # Fast non-optimal solver gives an incumbent upper bound.
    incumbent_plan = solve_fast(initial_state, move_limit=move_limit)
    incumbent_extra = INF
    if incumbent_plan is not None:
        incumbent_extra = count_collision_taps(incumbent_plan)

    start = safe_peel_closure(initial_state)

    open_heap = PriorityQueue()
    dist = {}
    parent = {}

    h0 = admissible_extra_lower_bound(start)

    push(
        open_heap,
        priority=(h0, 0),
        state=start,
        g_extra=0
    )

    dist[hash_state(start)] = 0

    while open_heap:
        state, g_extra = pop_min(open_heap)

        key = hash_state(state)
        if g_extra != dist.get(key, INF):
            continue

        if state.is_goal():
            plan = reconstruct(parent, key)
            return expand_safe_peel_macros(plan)

        if g_extra + admissible_extra_lower_bound(state) >= incumbent_extra:
            continue

        if collision_budget is not None:
            if g_extra + admissible_extra_lower_bound(state) > collision_budget:
                continue

        actions = ordered_actions(state)

        for action in actions:
            event = raycast(state, action.pig_id)

            if event.is_zero_displacement():
                continue

            if event.kind == "EXIT":
                next_state = apply_exit(state, action.pig_id)
                step_extra = 0
            else:
                next_state = apply_collision(state, action.pig_id, event)
                step_extra = 1

            next_state = canonicalize(next_state)
            next_state = safe_peel_closure(next_state)

            new_g = g_extra + step_extra

            if new_g >= incumbent_extra:
                continue

            if collision_budget is not None and new_g > collision_budget:
                continue

            next_key = hash_state(next_state)

            if new_g < dist.get(next_key, INF):
                dist[next_key] = new_g
                parent[next_key] = (key, action, event)

                h = admissible_extra_lower_bound(next_state)
                f = new_g + h

                push(
                    open_heap,
                    priority=(f, tie_breaker(next_state)),
                    state=next_state,
                    g_extra=new_g
                )

    return UNSAT
```

Admissible lower bound:

```python
def admissible_extra_lower_bound(state):
    residual = static_zero_peel_residual(state)

    if residual.is_empty():
        return 0

    # Always safe:
    lb = 1

    # Optional stronger safe bound:
    cycles = blocker_cycles(residual)
    independent = disjoint_breaker_cycle_packing(cycles, residual)
    lb = max(lb, len(independent))

    return lb
```

Safe peel closure:

```python
def safe_peel_closure(state):
    plan_macro = []

    changed = True
    while changed:
        changed = False

        for pig in list(state.active_pigs()):
            event = raycast(state, pig)

            if event.kind != "EXIT":
                continue

            if can_never_be_stopper(state, pig):
                state = apply_exit(state, pig)
                plan_macro.append(pig)
                changed = True
                break

    state.attach_macro(plan_macro)
    return canonicalize(state)
```

---

## 9. Fast practical solver for phone-sized levels

For 30–80 pigs, exact optimal search may still be too expensive. The best practical solver is a deterministic hybrid:

## **PAWS: Peel-Aware Weighted Search**

Architecture:

1. Use safe-peel reductions.
2. Greedily remove low-risk exit pigs.
3. When stuck in blocker cycles, use SCC-guided collision moves.
4. Run beam search over collision moves, not over every tap.
5. Replan after every real tap if extracting from a live phone screen.

Fast solver loop:

```python
def solve_fast(initial_state, move_limit=None, beam_width=256, lookahead_hits=4):
    state = canonicalize(initial_state)
    plan = []

    while not state.is_goal():
        # 1. Forced safe exits.
        safe_exits = find_safe_exit_pigs(state)
        if safe_exits:
            pig = best_safe_exit(state, safe_exits)
            plan.append(tap(pig))
            state = apply_exit(state, pig)
            continue

        # 2. Ordinary exits.
        exits = find_exit_pigs(state)
        if exits:
            pig = best_exit_by_stopper_aware_score(state, exits)
            plan.append(tap(pig))
            state = apply_exit(state, pig)
            continue

        # 3. No exits: break a blocker SCC.
        candidates = cycle_breaking_candidates(state)

        best = None
        best_score = -INF

        for pig in candidates:
            event = raycast(state, pig)
            if event.kind != "HIT" or event.is_zero_displacement():
                continue

            s2 = apply_collision(state, pig, event)
            score = evaluate_after_greedy_rollout(s2)

            if score > best_score:
                best_score = score
                best = (pig, event, s2)

        if best is None:
            # Escalate to beam search.
            subplan = beam_breakout(state, beam_width, lookahead_hits)
            if subplan is None:
                return None
            for action in subplan:
                plan.append(action)
                state = simulate(state, action)
            continue

        pig, event, state = best
        plan.append(tap(pig))

        if move_limit is not None and len(plan) > move_limit:
            return None

    return plan
```

Beam search over collision moves:

```python
def beam_breakout(state, beam_width, max_hit_depth):
    beam = [(state, [])]
    seen = set()

    for depth in range(max_hit_depth + 1):
        next_beam = []

        for s, p in beam:
            s = greedy_low_risk_peel(s, p)

            if has_exit(s):
                return p

            for pig in cycle_breaking_candidates(s):
                event = raycast(s, pig)

                if event.kind != "HIT" or event.is_zero_displacement():
                    continue

                s2 = apply_collision(s, pig, event)
                s2 = canonicalize(s2)
                key = hash_state(s2)

                if key in seen:
                    continue
                seen.add(key)

                p2 = p + [tap(pig)]
                score = heuristic_state_score(s2)
                next_beam.append((score, s2, p2))

        next_beam.sort(reverse=True, key=lambda x: x[0])
        beam = [(s, p) for _, s, p in next_beam[:beam_width]]

    return None
```

This is not guaranteed optimal. It is designed to solve phone-scale levels quickly and provide a good incumbent for PA01-A*.

---

## 10. Screenshot-to-state extraction

### 10.1 Board bounds

The screenshots show a mostly open green play area with UI overlays at the top and bottom. The solver should not assume the full screenshot is playable board.

Pipeline:

1. Remove iOS status/header and bottom power-up UI by cropping to the green play region.
2. Detect the board rectangle by background-color segmentation.
3. Estimate left/right bounds as the visible play-area edges.
4. Estimate top bound below the score/progress UI.
5. Estimate bottom bound above the power-up buttons.
6. Refine bounds using observed exits: when a pig disappears, fit the boundary crossing location to the predicted ray.

### 10.2 Pig center detection

Options:

1. **HSV color segmentation**: pigs are pink against green background.
2. Threshold pink regions.
3. Clean with morphological open/close.
4. Use connected components or contours.
5. Split touching blobs with watershed or template matching.

OpenCV contour detection is designed for finding object boundaries in binary images; OpenCV’s documentation recommends thresholding or edge detection before contour extraction. ([OpenCV-Python Tutorials][13])

For higher accuracy, use rotated template matching. OpenCV template matching searches for a smaller template inside a larger image by sliding the template and comparing patches. ([OpenCV-Python Tutorials][14])

Recommended robust approach:

* manually crop one clean pig sprite from the screenshot;
* generate rotated templates every (5^\circ) or every likely engine heading bin;
* run normalized cross-correlation;
* apply non-maximum suppression;
* refine centers with contour centroid or ellipse fit.

### 10.3 Heading estimation

The head direction is visually encoded by the snout/ears, not by an arrow.

Use a two-stage estimator:

1. Fit the major axis of the pink blob.
2. Disambiguate head vs tail using template scoring:

   * head side has snout/ear dark features;
   * tail side has a small curl/dot.

For each candidate angle (\theta), compute:

[
\text{score}(\theta)=\text{NCC}(\text{rotated pig template at }\theta,\text{image patch}).
]

Take the maximum. Then cluster headings with circular (k)-means to infer the game’s quantization bins.

### 10.4 Collision shape approximation

Use a capsule or ellipse, not a rectangle.

For pig (i):

* center (x_i): template-match center;
* heading (u_i): estimated angle;
* major radius (a): half body length plus margin;
* minor radius (b): half body width plus margin.

A capsule is often more stable than an ellipse for collision:

[
\text{capsule} = \text{line segment along body axis} \oplus \text{disk radius } r.
]

Add a safety margin of 2–5 pixels until simulated transitions match observed frames.

### 10.5 Transition validation from observed frames

Use consecutive screenshots from the same level:

1. Detect all pigs in frame (t) and (t+1).
2. Match unchanged pigs by nearest neighbor plus heading.
3. Identify the missing or moved pig.
4. Infer which pig was tapped.
5. Simulate that tap using current collider parameters.
6. Minimize endpoint error between predicted and observed moved pig.
7. Fit:

   * board bounds;
   * capsule length;
   * capsule radius;
   * contact tolerance;
   * heading quantization.

This is essential because the rendered sprite and the physics collider may not be identical.

### 10.6 Solvable-state extraction

After detection:

1. Build candidate state.
2. Check for overlaps; if overlaps exist, shrink or re-fit colliders.
3. Run raycasts for all pigs.
4. Compare predicted exit rays to obvious visible edge pigs.
5. Run fast solver.
6. If solver fails, try:

   * smaller collider radius;
   * larger collider radius;
   * alternate heading bin assignment;
   * manual correction UI.

For a real phone bot, re-detect after every tap and replan. Do not assume perfect physics.

---

## 11. Known results vs novel proposals

Known / cited:

* Rush Hour PSPACE-completeness. ([ScienceDirect][2])
* NCL PSPACE-completeness framework. ([Erik Demaine][4])
* Ricochet Robots / Lunar Lockout with fixed geometry PSPACE-completeness. 
* Lunar Lockout partial and generalized complexity results. 
* PushPush / Push-1 NP-hardness in 2D. 
* A*, IDA*, SAT planning, bounded model checking, MCTS as standard algorithmic frameworks. ([IEEE Xplore][6])

Novel / proposed here:

* The **DTSR** formalization for this pig game.
* Optimizing by collision taps:

[
\text{total taps}=n+#\text{collision taps}.
]

* **PA01-A*** as a 0-1-cost exact solver over collision cost.
* Safe-peel theorem based on “can never be a future stopper.”
* SCC-guided cycle-breaking heuristic.
* PAWS fast solver architecture.
* Screenshot-to-state calibration loop for this specific visual style.

Conjectural:

* Generalized DTSR is plausibly NP-hard, but I am not claiming a formal proof here.
* PSPACE-hardness is not justified for the exact fixed-heading monotone model; related PSPACE results should be treated as context, not as a theorem about this game.

---

## 12. Recommended implementation architecture in Python

Final recommended algorithm name:

# **PAWS: Peel-Aware 0-1 Search**

Use two modes:

1. **PAWS-Exact**: PA01-A* over collision cost.
2. **PAWS-Fast**: SCC-guided beam/greedy solver for phone-sized levels.

Module layout:

```text
paws/
  vision/
    detect_board.py
    detect_pigs.py
    estimate_heading.py
    calibrate_physics.py

  geometry/
    shapes.py          # ellipse/capsule/mask
    raycast.py         # continuous and quantized raycasts
    spatial_index.py

  model/
    state.py
    transition.py
    canonical.py
    hashing.py

  graph/
    blockers.py
    scc.py
    peel.py
    deadlocks.py

  solvers/
    exact_pa01_astar.py
    fast_paws_beam.py
    sat_encode.py      # optional
    validator.py

  app/
    solve_from_screenshot.py
    replay_plan.py
```

Core data structures:

```python
@dataclass(frozen=True)
class Pig:
    id: int
    shape_id: int
    heading: Vec2
    center: Vec2
    active: bool = True

@dataclass(frozen=True)
class State:
    pigs: tuple[Pig, ...]
    board: Board
    hash: int

@dataclass
class RaycastEvent:
    kind: Literal["EXIT", "HIT", "ZERO"]
    distance: float
    blocker_id: int | None
    new_center: Vec2 | None
```

For the screenshots you attached, I would start with a continuous capsule model and then fit a quantized approximation only if the observed transitions reveal snapping.

---

## 13. Failure cases and handling

### Vision failures

Problem: pigs overlap visually or touch.

Handling:

* use rotated template matching, not only connected components;
* use non-maximum suppression;
* use previous frame tracking if solving live;
* allow manual correction of centers/headings.

### Heading ambiguity

Problem: body axis is clear, but head/tail direction is ambiguous.

Handling:

* score head-specific template features;
* classify snout/ear side versus tail side;
* use observed motion after one tap to confirm heading;
* cluster headings into discrete bins.

### Collider mismatch

Problem: sprite outline does not equal physics collider.

Handling:

* fit capsule radius and length from observed collision endpoints;
* maintain tolerance bands;
* re-detect after each tap and replan;
* prefer conservative collision margins for exact planning, then validate.

### Greedy dead ends

Problem: removing an exit pig too early deletes a useful stopper.

Handling:

* exact solver should not force unsafe exits;
* fast solver should assign high stopper value to pigs lying in many future swept rays;
* use safe-peel only when the pig can never be a stopper.

### State explosion

Problem: 50+ pigs produce too many action orders.

Handling:

* optimize collision taps, not total taps;
* safe-peel forced removals;
* canonicalize identical pigs;
* use transposition table;
* use SCC move ordering;
* get an incumbent from PAWS-Fast before PAWS-Exact.

### Continuous numerical instability

Problem: repeated contact states cause tiny overlaps or zero moves.

Handling:

* fixed-point coordinates after each transition;
* (\varepsilon)-separated contact placement;
* prune moves below displacement tolerance;
* deterministic tie-breaking when two blockers have near-equal collision times.

### Move limit

Problem: level has a hidden or displayed tap limit.

Handling:

* compute (k=L-n);
* exact search only needs to prove whether collision cost (\le k);
* if (k=0), solve by static exit-peeling only;
* if PAWS-Fast exceeds (L), escalate to PAWS-Exact with the collision budget.

---

## Final recommendation

Implement **PAWS-Exact** first using a quantized or fixed-point capsule model:

1. detect pigs and headings;
2. build deterministic raycast transitions;
3. canonicalize states;
4. optimize collision taps with 0-1 A*;
5. use safe-peel and SCC move ordering;
6. validate against screenshots or live frames;
7. add PAWS-Fast as an incumbent generator and phone-scale solver.

This gives you an exact optimal solver when the extracted model is accurate, while still scaling to practical mobile-game levels through the fast SCC-guided fallback.

[1]: https://plays.org/tap-away/ "️ Play Tap Away Game: Free Online Block Clearing Spatial Logic Puzzle Video Game for Kids & Adults "
[2]: https://www.sciencedirect.com/science/article/pii/S0304397501001736 "Rush Hour is PSPACE-complete, or “Why you should generously tip parking lot attendants” - ScienceDirect"
[3]: https://play.google.com/store/apps/details?hl=en_US&id=park.car.parking.games.master.mania "Parking Games: Parking Jam - Apps on Google Play"
[4]: https://erikdemaine.org/papers/NCL_TCS/ " Robert A. Hearn and Erik D. Demaine: {PSPACE}-Completeness of Sliding-Block Puzzles and Other                   Problems through the Nondeterministic Constraint Logic Model                   of Computation "
[5]: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2021.7 "1 X 1 Rush Hour with Fixed Blocks Is PSPACE-Complete"
[6]: https://ieeexplore.ieee.org/document/4082128/?utm_source=chatgpt.com "A Formal Basis for the Heuristic Determination of Minimum ..."
[7]: https://www.sciencedirect.com/science/article/pii/0004370285900840?utm_source=chatgpt.com "Depth-first iterative-deepening: An optimal admissible tree ..."
[8]: https://www.cs.cornell.edu/selman/papers/pdf/92.ecai.satplan.pdf?utm_source=chatgpt.com "Planning as Satisfiability"
[9]: https://www.cs.cmu.edu/~emc/papers/Books%20and%20Edited%20Volumes/Bounded%20Model%20Checking.pdf?utm_source=chatgpt.com "Bounded Model Checking - CMU School of Computer Science"
[10]: https://ieeexplore.ieee.org/document/6145622?utm_source=chatgpt.com "A Survey of Monte Carlo Tree Search Methods"
[11]: https://www.sciencedirect.com/science/article/abs/pii/S0010448507001492?utm_source=chatgpt.com "Exact and efficient construction of Minkowski sums ..."
[12]: https://www.chessprogramming.org/Zobrist_Hashing?utm_source=chatgpt.com "Zobrist Hashing"
[13]: https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.html?utm_source=chatgpt.com "Contours : Getting Started — OpenCV-Python Tutorials beta ..."
[14]: https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html?utm_source=chatgpt.com "Template Matching - OpenCV-Python Tutorials's documentation!"
