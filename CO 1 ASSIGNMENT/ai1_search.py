"""CSA17 Assignment 1 - Hospital medicine-delivery robot.
Algorithms: BFS (iterative, FIFO), UCS (iterative, priority queue), IDDFS (recursive).
Run: python ai1_search.py   -> results.json, results.md, plots png.  Seeds are fixed below."""
import random, time, heapq, json, sys, itertools, math
from collections import deque
sys.setrecursionlimit(20000)

SEED_BASE = 2026                 # graph seed = SEED_BASE + N ; goal seed = SEED_BASE
SIZES = [1000, 10000, 100000, 1000000]
RUNS = 5                         # timing runs per (algorithm, case)
BUDGET = 1_000_000               # IDDFS generation budget -> "DNF" beyond this

class BudgetExceeded(Exception):
    pass

# ---------------- preprocessing: graph generation + adjacency lists -------------
def build_graph(N, seed, extra_frac=0.10, island=5):
    """Hospital graph: random recursive tree (corridor backbone, hubs = lift lobbies)
    + 10% extra cross-corridor edges, weights 1..9 min. Plus an isolated 'island'
    ward block (nodes N..N+4) used as the unreachable goal. Simple graph (no parallels)."""
    rnd = random.Random(seed)
    t = time.perf_counter()
    V = N + island
    seen, edges = set(), []
    for i in range(1, N):
        p = rnd.randrange(i)
        seen.add(p * V + i); edges.append((i, p, rnd.randint(1, 9)))
    for _ in range(int(extra_frac * N)):
        a, b = rnd.randrange(N), rnd.randrange(N)
        if a == b: continue
        lo, hi = (a, b) if a < b else (b, a)
        if lo * V + hi in seen: continue
        seen.add(lo * V + hi); edges.append((a, b, rnd.randint(1, 9)))
    for i in range(N + 1, N + island):
        edges.append((i, i - 1, rnd.randint(1, 9)))
    adj = [[] for _ in range(V)]
    for a, b, w in edges:
        adj[a].append((b, w)); adj[b].append((a, w))
    return adj, time.perf_counter() - t, len(edges)

def rebuild(parent, v):
    p = []
    while v is not None:
        p.append(v); v = parent[v]
    return p[::-1]

# ---------------- Algorithm 1: BFS (iterative, queue) ---------------------------
def bfs(adj, s, g):
    st = dict(gen=1, exp=0, maxf=1)
    if s == g: return [s], st
    parent = {s: None}; fr = deque([s])
    while fr:
        u = fr.popleft(); st['exp'] += 1
        for v, _ in adj[u]:
            if v not in parent:
                parent[v] = u; st['gen'] += 1
                if v == g: return rebuild(parent, v), st      # goal test at generation
                fr.append(v)
                if len(fr) > st['maxf']: st['maxf'] = len(fr)
    return None, st

# ---------------- Algorithm 2: Uniform-cost search (iterative, heap) ------------
def ucs(adj, s, g):
    st = dict(gen=1, exp=0, maxf=1)
    dist = {s: 0}; parent = {s: None}; pq = [(0, s)]; done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done: continue                                 # stale entry
        done.add(u); st['exp'] += 1
        if u == g: return rebuild(parent, u), st               # goal test at expansion
        for v, w in adj[u]:
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd; parent[v] = u
                heapq.heappush(pq, (nd, v)); st['gen'] += 1
                if len(pq) > st['maxf']: st['maxf'] = len(pq)
    return None, st

# ---------------- Algorithm 3: Iterative deepening DFS (recursive) --------------
def iddfs(adj, s, g, budget=BUDGET):
    """Depth-limited recursive DFS, limit 0,1,2,...; only an on-path check (no global
    explored set) so memory is O(b*d). 'maxf' = pending siblings along the current path."""
    st = dict(gen=0, exp=0, maxf=0, iters=0)
    onpath = {s}
    cut = False
    def dls(u, limit, pend):
        nonlocal cut
        st['exp'] += 1
        if u == g: return [u]
        pend += len(adj[u])
        if pend > st['maxf']: st['maxf'] = pend
        if limit == 0:
            if any(v not in onpath for v, _ in adj[u]): cut = True
            return None
        for v, _ in adj[u]:
            if v in onpath: continue
            st['gen'] += 1
            if st['gen'] > budget: raise BudgetExceeded
            onpath.add(v)
            r = dls(v, limit - 1, pend)
            onpath.discard(v)
            if r is not None: return [u] + r
        return None
    try:
        for L in itertools.count():
            st['iters'] += 1; st['gen'] += 1; cut = False
            r = dls(s, L, 0)
            if r is not None: return r, st
            if not cut: return None, st      # whole component exhausted -> unreachable
    except BudgetExceeded:
        return 'DNF', st

ALGOS = {'BFS': bfs, 'UCS': ucs, 'IDDFS': iddfs}

def path_cost(adj, p):
    c = 0
    for u, v in zip(p, p[1:]):
        c += next(w for x, w in adj[u] if x == v)              # raises if edge missing
    return c

def farthest(adj, s):
    seen = {s: 0}; q = deque([s]); last = s
    while q:
        u = q.popleft(); last = u
        for v, _ in adj[u]:
            if v not in seen: seen[v] = seen[u] + 1; q.append(v)
    return last, seen[last]

NGOALS = 5

def main():
    rows, prep = [], []
    for N in SIZES:
        adj, tb, E = build_graph(N, SEED_BASE + N)
        V = len(adj)
        far, fdepth = farthest(adj, 0)
        prep.append(dict(N=N, V=V, E=E, build_s=tb, farthest_hops=fdepth))
        rg = random.Random(SEED_BASE)
        goals = [rg.randrange(N // 2, N) for _ in range(NGOALS)]       # 'newer wing' wards
        cases = {'best (goal adjacent to pharmacy)': [(0, adj[0][0][0])],
                 'average (5 random wards)': [(0, g) for g in goals],
                 'worst-reachable (farthest ward)': [(0, far)],
                 'unreachable (isolated ward block)': [(0, N + 3)],
                 'start==goal': [(0, 0)]}
        for cname, pairs in cases.items():
            acc = {a: [] for a in ALGOS}
            for (s, g) in pairs:
                ref_p, _ = ucs(adj, s, g)
                ref_cost = path_cost(adj, ref_p) if ref_p else None
                bfs_p, _ = bfs(adj, s, g)
                ref_hops = len(bfs_p) - 1 if bfs_p else None
                for name, f in ALGOS.items():
                    ts = []
                    for _ in range(RUNS):
                        t = time.perf_counter(); p, st = f(adj, s, g); ts.append(time.perf_counter() - t)
                    o = dict(st=st, t=1000 * sum(ts) / RUNS)
                    if p == 'DNF': o['res'] = 'DNF(budget)'
                    elif p is None: o['res'] = 'no route'
                    else:
                        assert p[0] == s and p[-1] == g
                        c = path_cost(adj, p)
                        o.update(res='route', depth=len(p) - 1, cost=c, copt=(c == ref_cost), hopt=(len(p) - 1 == ref_hops))
                    acc[name].append(o)
            for name, os_ in acc.items():
                m = lambda k: sum(o['st'][k] for o in os_) / len(os_)
                res = os_[0]['res'] if all(o['res'] == os_[0]['res'] for o in os_) else 'mixed'
                row = dict(N=N, case=cname, algo=name, result=res, gen=m('gen'), exp=m('exp'), maxf=m('maxf'),
                           time_ms=sum(o['t'] for o in os_) / len(os_), npairs=len(os_))
                if res == 'route':
                    row.update(depth=sum(o['depth'] for o in os_) / len(os_), cost=sum(o['cost'] for o in os_) / len(os_),
                               cost_opt=all(o['copt'] for o in os_), hop_opt=all(o['hopt'] for o in os_))
                else: row.update(depth=None, cost=None, cost_opt=None, hop_opt=None)
                rows.append(row)
                print(N, cname, name, res, round(row['gen']), round(row['time_ms'], 1), flush=True)
        del adj
    json.dump(dict(rows=rows, prep=prep, seeds=dict(base=SEED_BASE, runs=RUNS, budget=BUDGET, ngoals=NGOALS)),
              open('results.json', 'w'), indent=1)
    write_outputs(rows, prep)

def fmt(x, d=0):
    return '-' if x is None else (f'{x:,.{d}f}' if isinstance(x, (int, float)) else str(x))

def write_outputs(rows, prep):
    L = ['### Preprocessing (adjacency-list construction; graph seed = 2026+N)\n',
         '| N | states V | edges E | build time (s) | farthest ward (hops) |', '|---|---|---|---|---|']
    for p in prep: L.append(f"| {p['N']:,} | {p['V']:,} | {p['E']:,} | {p['build_s']:.2f} | {p['farthest_hops']} |")
    cases = []
    for r in rows:
        if r['case'] not in cases: cases.append(r['case'])
    for case in cases:
        L += [f'\n### Case: {case}\n',
              '| N | algo | result | generated | expanded | max frontier | depth | cost | cost-optimal | hop-optimal | time ms |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
        for r in rows:
            if r['case'] != case: continue
            L.append(f"| {r['N']:,} | {r['algo']} | {r['result']} | {fmt(r['gen'])} | {fmt(r['exp'])} | {fmt(r['maxf'])} | "
                     f"{fmt(r['depth'],1)} | {fmt(r['cost'],1)} | {r['cost_opt']} | {r['hop_opt']} | {r['time_ms']:.1f} |")
    L.append('\n### Empirical growth exponent alpha in metric ~ N^alpha (average case, 1k -> 1M)\n')
    L += ['| algo | alpha (generated) | alpha (max frontier) | alpha (time) |', '|---|---|---|---|']
    for a in ALGOS:
        rr = [r for r in rows if r['case'].startswith('average') and r['algo'] == a and r['result'] == 'route']
        if len(rr) >= 2:
            x0, x1 = rr[0], rr[-1]; d = math.log(x1['N'] / x0['N'])
            f = lambda k: math.log(max(x1[k], 1e-9) / max(x0[k], 1e-9)) / d
            L.append(f"| {a} | {f('gen'):.2f} | {f('maxf'):.2f} | {f('time_ms'):.2f} |")
    open('results.md', 'w').write('\n'.join(L))
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 3, figsize=(15, 4))
        for a in ALGOS:
            rr = [r for r in rows if r['case'].startswith('average') and r['algo'] == a and r['result'] == 'route']
            xs = [r['N'] for r in rr]
            for i, (k, t) in enumerate([('gen', 'Nodes generated (avg of 5 goals)'), ('maxf', 'Max frontier (memory proxy)'), ('time_ms', 'Time (ms)')]):
                ax[i].loglog(xs, [r[k] for r in rr], 'o-', label=a); ax[i].set_title(t)
        for i in range(3): ax[i].set_xlabel('states N'); ax[i].grid(True, which='both', alpha=.3)
        xs = [p['N'] for p in prep]; ax[2].loglog(xs, [1000 * p['build_s'] for p in prep], 's--', label='preprocessing (build)')
        ax[0].loglog(xs, xs, 'k:', label='y = N'); ax[0].legend(); ax[2].legend()
        plt.tight_layout(); plt.savefig('fig_scaling.png', dpi=130)
    except Exception as e:
        print('plot skipped', e)

if __name__ == '__main__':
    main()
