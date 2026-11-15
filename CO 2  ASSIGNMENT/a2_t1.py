"""A2 Task 1 - UCS vs Greedy vs A* on campus-shuttle grids.
Cells: '.' road (cost 1), 'x' construction slow-zone (cost 5), '#' blocked. 4-connected moves.
Heuristic h(n) = Manhattan distance to goal (x c_min = 1).  Seeds: maps 11, trips 5."""
import heapq, random, time

def parse(rows): return [list(r) for r in rows]
def cost_of(ch): return 1 if ch == '.' else 5

def search(grid, s, g, mode):
    R, C = len(grid), len(grid[0])
    h = lambda p: abs(p[0] - g[0]) + abs(p[1] - g[1])
    f = {'UCS': lambda gg, p: gg, 'Greedy': lambda gg, p: h(p), 'A*': lambda gg, p: gg + h(p)}[mode]
    st = dict(exp=0, gen=1, maxf=1)
    best = {s: 0}; parent = {s: None}; cnt = 0
    pq = [(f(0, s), h(s), cnt, 0, s)]; done = set()
    while pq:
        _, _, _, gg, u = heapq.heappop(pq)
        if u in done: continue
        done.add(u); st['exp'] += 1
        if u == g:
            p = []; x = u
            while x is not None: p.append(x); x = parent[x]
            return gg, p[::-1], st
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v = (u[0] + dr, u[1] + dc)
            if not (0 <= v[0] < R and 0 <= v[1] < C) or grid[v[0]][v[1]] == '#': continue
            ng = gg + cost_of(grid[v[0]][v[1]])
            if mode == 'Greedy':
                if v in best: continue          # greedy: first discovery only
            elif v in best and ng >= best[v]: continue
            best[v] = ng; parent[v] = u; cnt += 1; st['gen'] += 1
            heapq.heappush(pq, (f(ng, v), h(v), cnt, ng, v))
            st['maxf'] = max(st['maxf'], len(pq))
    return None, None, st

def path_cost(grid, p): return sum(cost_of(grid[r][c]) for r, c in p[1:])

# ---------------- designed maps ----------------
def open_map(R=61, C=61, p=0.05, seed=11):
    rnd = random.Random(seed)
    g = [['.'] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            if rnd.random() < p: g[r][c] = '#'
    g[0][0] = g[R-1][C-1] = '.'; return g

def maze_map(n=30, seed=11):                      # perfect maze, (2n+1)^2 grid
    rnd = random.Random(seed); S = 2 * n + 1
    g = [['#'] * S for _ in range(S)]; stack = [(1, 1)]; g[1][1] = '.'
    while stack:
        r, c = stack[-1]
        nb = [(r+dr, c+dc, dr, dc) for dr, dc in ((2,0),(-2,0),(0,2),(0,-2)) if 0 < r+dr < S-1 and 0 < c+dc < S-1 and g[r+dr][c+dc] == '#']
        if not nb: stack.pop(); continue
        rr, cc, dr, dc = rnd.choice(nb); g[r+dr//2][c+dc//2] = '.'; g[rr][cc] = '.'; stack.append((rr, cc))
    return g

def cup_map(R=61, C=61):                          # dead-end trap: cup opens toward the start, goal behind it
    g = [['.'] * C for _ in range(R)]
    for r in range(15, 46): g[r][45] = '#'        # back wall
    for c in range(25, 46): g[15][c] = '#'; g[45][c] = '#'
    return g

def swamp_map(R=61, C=61):                        # costly band with a cheap way round
    g = [['.'] * C for _ in range(R)]
    for r in range(10, 51):
        for c in range(20, 41): g[r][c] = 'x'
    return g

MAPS = [('M1 open roads (5% obstacles)', open_map(), (0, 0), (60, 60)),
        ('M2 perfect maze (dead ends)', maze_map(), (1, 1), (59, 59)),
        ('M3 dead-end cup trap', cup_map(), (30, 2), (30, 58)),
        ('M4 swamp band (cost 5) with detour', swamp_map(), (30, 2), (30, 58))]

if __name__ == '__main__':
    print('| map | algo | expanded | generated | max frontier | path cost | optimal? | time ms |')
    print('|---|---|---|---|---|---|---|---|')
    for name, grid, s, g in MAPS:
        opt = None
        for mode in ('UCS', 'Greedy', 'A*'):
            t = time.perf_counter(); cst, p, st = search(grid, s, g, mode); ms = 1000 * (time.perf_counter() - t)
            if mode == 'UCS': opt = cst
            assert cst == path_cost(grid, p)
            print(f"| {name} | {mode} | {st['exp']:,} | {st['gen']:,} | {st['maxf']:,} | {cst} | {cst == opt} | {ms:.1f} |")
    # design decision: 95% of trips on open roads. 200 random trips on map M1-style open map
    print('\nOPEN-ROAD TRIPS: 200 random start/goal pairs on M1 (seed 5)')
    grid = open_map(); rnd = random.Random(5)
    free = [(r, c) for r in range(61) for c in range(61) if grid[r][c] == '.']
    acc = {m: dict(exp=0, opt=0, ex=0.0, n=0) for m in ('UCS', 'Greedy', 'A*')}
    n_tr = 0
    while n_tr < 200:
        s, g = rnd.sample(free, 2)
        ucs_c, _, _ = search(grid, s, g, 'UCS')
        if ucs_c is None: continue
        n_tr += 1
        for m in acc:
            c, p, st = search(grid, s, g, m)
            acc[m]['exp'] += st['exp']; acc[m]['opt'] += (c == ucs_c); acc[m]['ex'] += (c - ucs_c) / ucs_c
    print('| algo | mean expanded | % trips optimal | mean cost excess % |'); print('|---|---|---|---|')
    for m, a in acc.items():
        print(f"| {m} | {a['exp']/200:,.0f} | {100*a['opt']/200:.1f} | {100*a['ex']/200:.2f} |")
