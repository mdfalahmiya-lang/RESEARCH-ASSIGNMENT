"""CSA17 Assignment 1 - Task 12: robot lost among k junctions (belief-state search).
8x8 hospital-junction grid with ~12% corridors walled off (connectivity kept). Actions N,S,E,W
(blocked move = stay put). Dock = junction 0. Local sensor = which of the 4 corridors are open.
Run: python ai1_belief.py > belief_out.txt     Seeds: grid 7, trials 100+t."""
import random, itertools
from collections import deque
from math import comb

R = C = 8; V = R * C; DOCK = 0
ACTS = 'NSEW'; D = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}

def make_grid(seed, wall_frac=0.12):
    rnd = random.Random(seed)
    E = []
    for r in range(R):
        for c in range(C):
            if c + 1 < C: E.append((r * C + c, r * C + c + 1))
            if r + 1 < R: E.append((r * C + c, (r + 1) * C + c))
    rnd.shuffle(E); open_ = set(E); removed = 0
    def connected(es):
        nb = {i: [] for i in range(V)}
        for a, b in es: nb[a].append(b); nb[b].append(a)
        seen = {0}; q = [0]
        while q:
            u = q.pop()
            for v in nb[u]:
                if v not in seen: seen.add(v); q.append(v)
        return len(seen) == V
    for e in E:
        if removed >= int(wall_frac * len(E)): break
        open_.discard(e)
        if connected(open_): removed += 1
        else: open_.add(e)
    move = [dict() for _ in range(V)]
    for s in range(V):
        r, c = divmod(s, C)
        for a, (dr, dc) in D.items():
            r2, c2 = r + dr, c + dc
            t = s
            if 0 <= r2 < R and 0 <= c2 < C:
                n = r2 * C + c2
                if (min(s, n), max(s, n)) in open_: t = n
            move[s][a] = t
    return move

MOVE = make_grid(7)
def percept(s): return sum(1 << i for i, a in enumerate(ACTS) if MOVE[s][a] != s)
def apply(B, a): return frozenset(MOVE[s][a] for s in B)
def split(B):
    d = {}
    for s in B: d.setdefault(percept(s), set()).add(s)
    return [frozenset(x) for x in d.values()]

# hop distance to dock (used once the robot is localised = original single-state design)
DIST = [None] * V; DIST[DOCK] = 0; q = deque([DOCK])
while q:
    u = q.popleft()
    for a in ACTS:
        v = MOVE[u][a]
        if DIST[v] is None: DIST[v] = DIST[u] + 1; q.append(v)

def blind_belief_bfs(B0, cap=400000):
    """No sensor: BFS over belief states (frozensets). Returns (plan length, belief states generated)."""
    seen = {B0: 0}; fr = deque([B0]); goal = frozenset([DOCK])
    if B0 == goal: return 0, 1
    while fr:
        B = fr.popleft()
        for a in ACTS:
            B2 = apply(B, a)
            if B2 not in seen:
                seen[B2] = seen[B] + 1
                if B2 == goal: return seen[B2], len(seen)
                fr.append(B2)
                if len(seen) > cap: return None, len(seen)
    return None, len(seen)                      # goal belief unreachable (not synchronisable)

def sensed_conditional_plan(B0, cap=400000):
    """With local sensor: AND-OR search by iterative deepening on worst-case plan length.
    After every action the percept splits the belief (AND over percepts, OR over actions).
    A singleton belief hands over to the original shortest-path design."""
    gen = set(); memo = {}
    class Cap(Exception): pass
    def solve(B, L):
        if len(B) == 1: return DIST[next(iter(B))] <= L
        if L == 0: return False
        key = (B, L)
        if key in memo: return memo[key]
        res = False
        for a in ACTS:
            B2 = apply(B, a); gen.add(B2)
            if len(gen) > cap: raise Cap
            if all(solve(c, L - 1) for c in split(B2)): res = True; break
        memo[key] = res; return res
    classes = split(B0)
    try:
        for L in range(0, 80):
            if all(solve(c, L) for c in classes): return L, len(gen) + len(classes)
    except Cap:
        return None, len(gen)
    return None, len(gen)

def blind_plan_actions(B0, cap=400000):
    seen = {B0: None}; fr = deque([B0]); goal = frozenset([DOCK])
    while fr:
        B = fr.popleft()
        for a in ACTS:
            B2 = apply(B, a)
            if B2 not in seen:
                seen[B2] = (B, a)
                if B2 == goal:
                    p = []; x = B2
                    while seen[x]: x, act = seen[x][0], seen[x][1]; p.append(act)
                    return p[::-1]
                fr.append(B2)
    return None

def naive_success(B0):
    """Original design retained naively: assume the FIRST possible location is the true one,
    follow its shortest path to the dock; count true locations for which it still works."""
    s0 = min(B0); plan = []
    s = s0
    while s != DOCK:
        a = next(a for a in ACTS if DIST[MOVE[s][a]] == DIST[s] - 1); plan.append(a); s = MOVE[s][a]
    ok = 0
    for s in B0:
        for a in plan: s = MOVE[s][a]
        ok += (s == DOCK)
    return ok / len(B0)

if __name__ == '__main__':
    print('grid 8x8, V =', V, ', max localised distance to dock =', max(DIST), 'hops')
    print('Theory: reachable belief states <= sum_{j<=k} C(64,j) (actions never grow a belief)\n')
    print('| k | trials | naive-plan success | blind: beliefs generated | blind: plan len | sensor: beliefs generated | sensor: worst-case plan len | k=1 single-state BFS len | bound sum_{j<=k}C(64,j) |')
    print('|---|---|---|---|---|---|---|---|---|')
    ex = None
    for k in (2, 4, 8):
        bg, bl, sg, sl, nv, orig = [], [], [], [], [], []
        for t in range(10):
            rnd = random.Random(100 + t * 31 + k)
            B0 = frozenset(rnd.sample(range(1, V), k))
            L1, g1 = blind_belief_bfs(B0); L2, g2 = sensed_conditional_plan(B0)
            nv.append(naive_success(B0)); orig.append(max(DIST[s] for s in B0))
            if L1 is not None: bl.append(L1); bg.append(g1)
            if L2 is not None: sl.append(L2); sg.append(g2)
            if k == 4 and t == 0: ex = (sorted(B0), blind_plan_actions(B0), L2)
        avg = lambda x: f'{sum(x)/len(x):.1f}' if x else 'n/a'
        print(f'| {k} | 10 | {100*sum(nv)/len(nv):.0f}% | {avg(bg)} ({len(bg)}/10 solvable) | {avg(bl)} | {avg(sg)} ({len(sg)}/10) | {avg(sl)} | {avg(orig)} (max single dist) | {sum(comb(V,j) for j in range(1,k+1)):,} |')
    print('\nWorked example k=4: possible junctions', ex[0])
    print('blind (no sensor) shortest conditional-free plan:', ''.join(ex[1]) if ex[1] else None, ' length', len(ex[1]) if ex[1] else None)
    print('with sensor: worst-case plan length', ex[2])
