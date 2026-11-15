# Predictions written BEFORE any Assignment-2 code was executed

**T1 (grids, h = Manhattan × c_min).** Open map: A* expands ≫ fewer nodes than UCS (≈10× or more), Greedy the fewest; A* and UCS optimal, Greedy optimal or within a few %. Maze (single corridor tree): all three find the same unique route, cost identical; UCS expands most. Cup-trap map: Greedy dives into the cup and expands most of the cup interior before escaping (expansions ≫ A*), path suboptimal. Swamp map (cost-5 band with cheap detour): Greedy walks straight through the swamp (cost ≈ 140 vs optimum ≈ 102) → not optimal; A* optimal with fewer expansions than UCS.

**T2 (online).** Online DFS moves ≈ 2 × (cells explored before target) in a perfect maze, so competitive ratio grows with maze size and dead-end density and is worst for far targets; unreachable target ⇒ explores the whole component (≈ 2·cells moves). LRTA* trial 1 costs more than DFS-like exploration but the cost over repeated trials falls toward the optimal path (ratio → 1) within ~10–20 trials.

**T3 (b = 4, d = 6, 4,096 leaves).** Minimax visits (4⁷−1)/3 = 5,461 nodes. Alpha-beta, best ordering: Σ_ℓ (b^⌈ℓ/2⌉ + b^⌊ℓ/2⌋ − 1) = 1+4+7+19+31+79+127 = **268 nodes**, 127 leaf evaluations. Worst ordering: **5,461 nodes, 0 useful cutoffs**. Random ordering: ≈ b^{3d/4} = 4^{4.5} = 512 leaves (≈ 1,000 nodes, wide variance). All-equal leaves: pruning triggers on ties (α ≥ β), so every sibling is cut after its first child: close to the best-case count (≈ 268).

**T4 (Connect-k, b = 7).** Nodes = Σ_{i≤d} 7^i: d=4: 2,801; d=5: 19,608; d=6: 137,257; d=7: 960,800 (terminal positions make observed slightly lower). Evaluation calls ≈ 7^d. Win rate vs random rises with depth and saturates near 100 % by d ≈ 3–4. With a 1 s per-move criterion, plain minimax becomes impractical at about d = 6 in Python.

**T5 (CSP).** AC-3 alone solves the pinned even cycle (0 search nodes) and detects the pinned triangle's failure (domain wipe-out). Odd cycle with 2 slots is arc-consistent but unsolvable, so AC-3 finds nothing and search is unavoidable. Plain backtracking nodes grow exponentially with the number of exams near the hard density; MAC reduces nodes by one to several orders of magnitude, but costs more constraint checks per node.

**T6 (TSP).** Distinct tours = (n−1)!/2: n=8: 2,520; 9: 20,160; 10: 181,440; 11: 1,814,400; time grows ×(n−1) per added customer. 2-opt with a single start gets stuck in local minima (mean excess a few %, some runs optimal); 10 restarts reach the optimum in most runs.

**T7 (branch & bound redesign).** On random Euclidean instances at n = 10 it should examine ≥ 95 % fewer complete tours and ≥ 90 % fewer distance evaluations while returning the identical optimum. Adversarial near-equal distances (all in [0.99, 1.01]) should defeat the bound: pruning < 30 %, and the overhead may make it slower than plain enumeration.
