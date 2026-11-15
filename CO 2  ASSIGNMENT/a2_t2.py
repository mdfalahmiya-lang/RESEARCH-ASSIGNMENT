"""A2 Task 2 - online search agents in unmapped mazes: online DFS and LRTA*.
The agent senses only the 4 neighbouring cells of its current cell. Cost per move = 1.
Competitive ratio = moves / optimal path length with full map (BFS).  Seeds: maze = 1000+s."""
import random, itertools
from collections import deque
D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

def make_maze(n, braid, seed):
    """Perfect maze on (2n+1)^2 grid, then knock out a fraction `braid` of the remaining dead ends
    (removes dead ends -> more loops).  Returns grid (True = open), dead-end density."""
    rnd = random.Random(seed); S = 2 * n + 1
    g = [[False] * S for _ in range(S)]; stack = [(1, 1)]; g[1][1] = True
    while stack:
        r, c = stack[-1]
        nb = [(r+dr, c+dc, dr, dc) for dr, dc in ((2,0),(-2,0),(0,2),(0,-2)) if 0 < r+dr < S-1 and 0 < c+dc < S-1 and not g[r+dr][c+dc]]
        if not nb: stack.pop(); continue
        rr, cc, dr, dc = rnd.choice(nb); g[r+dr//2][c+dc//2] = True; g[rr][cc] = True; stack.append((rr, cc))
    def nbrs(r, c): return [(r+dr, c+dc) for dr, dc in D4 if 0 <= r+dr < S and 0 <= c+dc < S and g[r+dr][c+dc]]
    dead = [(r, c) for r in range(S) for c in range(S) if g[r][c] and len(nbrs(r, c)) == 1 and (r, c) != (1, 1)]
    rnd.shuffle(dead)
    for (r, c) in dead[:int(braid * len(dead))]:
        cand = [(r+dr, c+dc) for dr, dc in D4 if 0 < r+dr < S-1 and 0 < c+dc < S-1 and not g[r+dr][c+dc]]
        if cand: x, y = rnd.choice(cand); g[x][y] = True
    cells = sum(sum(row) for row in g)
    de = sum(1 for r in range(S) for c in range(S) if g[r][c] and len(nbrs(r, c)) == 1)
    return g, de / cells, cells

def bfs_dist(g, s):
    S = len(g); dist = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for dr, dc in D4:
            v = (u[0]+dr, u[1]+dc)
            if 0 <= v[0] < S and 0 <= v[1] < S and g[v[0]][v[1]] and v not in dist: dist[v] = dist[u] + 1; q.append(v)
    return dist

def online_dfs(g, s, target):
    """Online DFS: go to an untried neighbour if one exists, else backtrack along own path.
    Returns (moves, revisits, cells_visited, found)."""
    S = len(g); visited = {s}; stack = [s]; cur = s; moves = rev = 0
    def open_nb(p): return [(p[0]+dr, p[1]+dc) for dr, dc in D4 if 0 <= p[0]+dr < S and 0 <= p[1]+dc < S and g[p[0]+dr][p[1]+dc]]
    while cur != target:
        nxt = next((v for v in open_nb(cur) if v not in visited), None)
        if nxt is not None:
            visited.add(nxt); stack.append(nxt); cur = nxt; moves += 1
        else:
            stack.pop()
            if not stack: return moves, rev, len(visited), False       # explored everything: unreachable
            cur = stack[-1]; moves += 1; rev += 1                      # backtrack = move onto a revisited cell
    return moves, rev, len(visited), True

def lrta_trials(g, s, target, trials, seed=0, cap=500000):
    """LRTA*: H table persists across trials. Returns list of moves per trial."""
    S = len(g); H = {}; rnd = random.Random(seed); out = []
    h0 = lambda p: abs(p[0]-target[0]) + abs(p[1]-target[1])
    for _ in range(trials):
        cur = s; moves = 0
        while cur != target and moves < cap:
            nb = [(cur[0]+dr, cur[1]+dc) for dr, dc in D4 if 0 <= cur[0]+dr < S and 0 <= cur[1]+dc < S and g[cur[0]+dr][cur[1]+dc]]
            vals = [(1 + H.get(v, h0(v)), rnd.random(), v) for v in nb]
            best = min(vals)
            H[cur] = best[0]; cur = best[2]; moves += 1
        out.append(moves)
    return out

if __name__ == '__main__':
    print('Online DFS: mean over 5 mazes per cell. size = grid side, braid = fraction of dead ends removed')
    print('| grid | braid | dead-end density | open cells | target | optimal | DFS moves | revisits | competitive ratio |')
    print('|---|---|---|---|---|---|---|---|---|')
    for n in (10, 20, 40):
        for braid in (0.0, 0.5, 1.0):
            agg = {k: [] for k in ('near', 'mid', 'far')}; dd = []; cc = []
            for sd in range(5):
                g, dens, cells = make_maze(n, braid, 1000 + sd); dd.append(dens); cc.append(cells)
                dist = bfs_dist(g, (1, 1)); far = max(dist.values())
                for lab, frac in (('near', .15), ('mid', .5), ('far', 1.0)):
                    tgt = min(dist, key=lambda p: abs(dist[p] - frac * far))
                    m, rv, vis, ok = online_dfs(g, (1, 1), tgt); assert ok
                    agg[lab].append((dist[tgt], m, rv))
            for lab in agg:
                o = sum(x[0] for x in agg[lab]) / 5; m = sum(x[1] for x in agg[lab]) / 5; rv = sum(x[2] for x in agg[lab]) / 5
                print(f'| {2*n+1}x{2*n+1} | {braid} | {sum(dd)/5:.2f} | {sum(cc)/5:.0f} | {lab} | {o:.0f} | {m:.0f} | {rv:.0f} | {m/o:.2f} |')
    print('\nUnreachable target (sealed pocket), online DFS:')
    print('| grid | braid | reachable cells | moves until failure declared | moves / reachable cells |'); print('|---|---|---|---|---|')
    for n in (10, 20, 40):
        for braid in (0.0, 1.0):
            g, dens, cells = make_maze(n, braid, 1000); S = 2*n+1
            tgt = (S-3, S-3); g[tgt[0]][tgt[1]] = True            # a floor cell sealed in by 4 walls
            for dr, dc in D4: g[tgt[0]+dr][tgt[1]+dc] = False
            comp = len(bfs_dist(g, (1, 1)))                       # cells the rover can actually reach
            m, rv, vis, ok = online_dfs(g, (1, 1), tgt); assert not ok
            print(f'| {S}x{S} | {braid} | {comp} | {m} | {m/comp:.2f} |')
    print('\nLRTA* learning over repeated missions (same maze, far target), moves per trial; optimal = BFS length')
    print('| grid | braid | optimal | trial 1 | 2 | 3 | 5 | 10 | 20 | 40 | first trial with ratio<=1.05 |'); print('|---|---|---|---|---|---|---|---|---|---|---|')
    for n, braid in ((10, 0.0), (10, 0.5), (20, 0.5)):
        g, dens, cells = make_maze(n, braid, 1000); dist = bfs_dist(g, (1, 1)); far = max(dist.values())
        tgt = min(dist, key=lambda p: abs(dist[p] - far)); tr = lrta_trials(g, (1, 1), tgt, 40)
        first = next((i+1 for i, m in enumerate(tr) if m <= 1.05 * far), 'none in 40')
        print(f'| {2*n+1}x{2*n+1} | {braid} | {far} | {tr[0]} | {tr[1]} | {tr[2]} | {tr[4]} | {tr[9]} | {tr[19]} | {tr[39]} | {first} |')
    # amortisation: first mission online DFS (map stored), later missions optimal (A*/BFS on the stored map)
    print('\nAmortisation, 41x41 braid 0.5 far target: total moves over m missions')
    g, dens, cells = make_maze(20, 0.5, 1000); dist = bfs_dist(g, (1, 1)); far = max(dist.values()); tgt = min(dist, key=lambda p: abs(dist[p]-far))
    dfs_m = online_dfs(g, (1, 1), tgt)[0]; lr = lrta_trials(g, (1, 1), tgt, 40)
    print('| missions m | online DFS every time | LRTA* learning | DFS once then stored map (optimal) |'); print('|---|---|---|---|')
    for m in (1, 2, 5, 10, 40):
        print(f'| {m} | {m*dfs_m} | {sum(lr[:m])} | {dfs_m + (m-1)*far} |')
