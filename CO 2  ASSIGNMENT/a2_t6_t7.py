"""A2 Task 6 (exhaustive + local search for a courier tour) and Task 7 (redesign = branch & bound).
Instances: n cities uniform in a 100x100 square, seed 4000+10n+s.  Local-search seeds: 9000+run."""
import itertools, math, random, time, sys

def inst(n, s):
    r = random.Random(4000 + 10 * n + s); P = [(r.uniform(0, 100), r.uniform(0, 100)) for _ in range(n)]
    return [[math.dist(a, b) for b in P] for a in P]

def tour_len(D, t): return sum(D[t[i]][t[(i + 1) % len(t)]] for i in range(len(t)))

# ------------- Task 6: exhaustive enumeration -------------
def exhaustive(D):
    """Representation: tour = permutation of cities 1..n-1 after fixed depot 0. Generation: itertools.permutations.
    Symmetry: a tour and its reverse have equal length, keep only perm[0] < perm[-1]. Evaluation: closed-tour length.
    Retention: running best (length, tour)."""
    n = len(D); best = math.inf; bt = None; gen = ev = 0
    for p in itertools.permutations(range(1, n)):
        gen += 1
        if n > 2 and p[0] > p[-1]: continue
        ev += 1
        c = D[0][p[0]]
        for i in range(n - 2): c += D[p[i]][p[i + 1]]
        c += D[p[-1]][0]
        if c < best: best, bt = c, (0,) + p
    return best, bt, gen, ev

def held_karp(D):                                           # independent exact method used only to verify
    n = len(D); INF = math.inf; dp = {(1 << i, i): D[0][i] for i in range(1, n)}
    for mask in range(1, 1 << n):
        if mask & 1: continue
        for j in range(1, n):
            if not mask & (1 << j) or (mask, j) in dp: continue
            pm = mask ^ (1 << j)
            if pm == 0: continue
            v = min((dp[(pm, k)] + D[k][j] for k in range(1, n) if (pm, k) in dp), default=INF)
            if v < INF: dp[(mask, j)] = v
    full = (1 << n) - 2
    return min(dp[(full, j)] + D[j][0] for j in range(1, n))

def two_opt(D, rnd, restarts):
    n = len(D); best = math.inf; moves = 0
    for _ in range(restarts):
        t = list(range(n)); rnd.shuffle(t); imp = True
        while imp:
            imp = False
            for i in range(n - 1):
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1: continue
                    a, b, c, d = t[i], t[i + 1], t[j], t[(j + 1) % n]
                    if D[a][c] + D[b][d] < D[a][b] + D[c][d] - 1e-12:
                        t[i + 1:j + 1] = reversed(t[i + 1:j + 1]); imp = True; moves += 1
        best = min(best, tour_len(D, t))
    return best, moves

# ------------- Task 7: branch & bound redesign -------------
def bnb(D):
    """DFS over partial tours. Incumbent = nearest-neighbour tour. Prune when
       cost_so_far + minout[cur] + sum_{unvisited u} minout[u] >= best   (each of those cities must still be left by one edge,
       each such edge costs >= that city's cheapest outgoing edge, so the bound never exceeds the true completion cost).
       Children visited nearest-first; cost is carried incrementally (no re-summing of prefixes)."""
    n = len(D); minout = [min(D[i][j] for j in range(n) if j != i) for i in range(n)]
    cur, seen, nn = 0, {0}, [0]
    while len(nn) < n:
        nx = min((j for j in range(n) if j not in seen), key=lambda j: D[cur][j]); nn.append(nx); seen.add(nx); cur = nx
    st = dict(best=tour_len(D, nn), tour=nn, nodes=0, tours=0, lookups=n, pruned=0)
    order = [sorted(range(n), key=lambda j: D[i][j]) for i in range(n)]
    def rec(cur, mask, cost, depth, rest, path):
        st['nodes'] += 1
        if depth == n:
            st['tours'] += 1; st['lookups'] += 1; c = cost + D[cur][0]
            if c < st['best']: st['best'], st['tour'] = c, path[:]
            return
        for j in order[cur]:
            if mask >> j & 1: continue
            st['lookups'] += 1; nc = cost + D[cur][j]; nrest = rest - minout[j]
            if nc + minout[j] + nrest >= st['best']: st['pruned'] += 1; continue
            path.append(j); rec(j, mask | 1 << j, nc, depth + 1, nrest, path); path.pop()
    rec(0, 1, 0.0, 1, sum(minout[1:]), [0])
    return st['best'], st['tour'], st

if __name__ == '__main__':
    print('## T6 correctness: 5 cities, ALL 12 distinct tours listed (hand-checkable)')
    P5 = [(0, 0), (4, 0), (4, 3), (0, 3), (2, 5)]; D5 = [[math.dist(a, b) for b in P5] for a in P5]
    allt = sorted((tour_len(D5, (0,) + p), (0,) + p) for p in itertools.permutations(range(1, 5)) if p[0] < p[-1])
    for L, t in allt: print(f'  tour {t} length {L:.3f}')
    b5 = exhaustive(D5)
    print(f'  exhaustive optimum {b5[0]:.3f} tour {b5[1]}; independent minimum of the list above {allt[0][0]:.3f}; Held-Karp {held_karp(D5):.3f}')
    ang = [0, 3, 1, 5, 2, 4]   # 6 cities on a circle, indices scrambled: optimum must be the convex polygon
    Pc = [(10 * math.cos(2 * math.pi * a / 6), 10 * math.sin(2 * math.pi * a / 6)) for a in ang]
    Dc = [[math.dist(a, b) for b in Pc] for a in Pc]; bc = exhaustive(Dc)
    print(f'  circle test: exhaustive {bc[0]:.4f} vs regular-hexagon perimeter 6*10 = 60.0000 -> {"PASS" if abs(bc[0]-60)<1e-9 else "FAIL"}')

    print('\n## T6 growth: exhaustive search, one random instance per n')
    print('| n | permutations generated | (n-1)! | tours evaluated | PREDICTED (n-1)!/2 | optimum | equals Held-Karp? | time s | time ratio to n-1 |'); print('|---|---|---|---|---|---|---|---|---|')
    prev = None; times = {}
    for n in range(5, 12):
        D = inst(n, 0); t = time.perf_counter(); b, bt, gen, ev = exhaustive(D); dt = time.perf_counter() - t; times[n] = dt
        hk = held_karp(D)
        print(f'| {n} | {gen:,} | {math.factorial(n-1):,} | {ev:,} | {math.factorial(n-1)//2:,} | {b:.3f} | {abs(b-hk)<1e-9} | {dt:.3f} | {"" if prev is None else f"{dt/prev:.1f}"} |')
        prev = dt; sys.stdout.flush()

    print('\n## T6 local search: 2-opt hill climbing, 20 runs per setting (seeds 9000+run), excess over exhaustive optimum')
    print('| n | restarts | runs reaching optimum | mean excess % | max excess % | mean time ms | mean improving moves |'); print('|---|---|---|---|---|---|---|')
    for n in (8, 9, 10, 11):
        D = inst(n, 0); opt = exhaustive(D)[0]
        for R in (1, 10):
            ex = []; tt = []; mv = []
            for run in range(20):
                rnd = random.Random(9000 + run); t = time.perf_counter(); b, m = two_opt(D, rnd, R); tt.append(time.perf_counter() - t); ex.append(100 * (b - opt) / opt); mv.append(m)
            print(f'| {n} | {R} | {sum(e < 1e-9 for e in ex)}/20 | {sum(ex)/20:.2f} | {max(ex):.2f} | {1000*sum(tt)/20:.2f} | {sum(mv)/20:.1f} |')
    for n in (50, 100):
        D = inst(n, 0); t = time.perf_counter(); b, m = two_opt(D, random.Random(9000), 10); print(f'\n  n={n}: 2-opt, 10 restarts: length {b:.1f}, {time.perf_counter()-t:.2f} s (exhaustive would need {math.factorial(n-1)//2:.2e} tours)')
    print('\n  deployment extrapolation from measured exhaustive times (time grows x(n-1)):')
    for n in (9, 10, 11, 12, 13): 
        est = times.get(n) or times[11] * math.prod(range(11, n))
        print(f'   n={n}: {"measured" if n in times else "estimated"} {est:.2f} s')

    print('\n## T7 redesign: branch & bound vs exhaustive (same instances, 5 seeds each, optimum compared)')
    print('| n | method | complete tours evaluated | search nodes | distance lookups | time ms | same optimum? |'); print('|---|---|---|---|---|---|---|')
    for n in (8, 9, 10):
        agg = {'EX': [0, 0, 0, 0], 'BB': [0, 0, 0, 0]}; same = True
        for s in range(5):
            D = inst(n, s); t = time.perf_counter(); b, _, gen, ev = exhaustive(D); te = time.perf_counter() - t
            t = time.perf_counter(); b2, _, st = bnb(D); tb = time.perf_counter() - t; same &= abs(b - b2) < 1e-9
            for k, v in zip(range(4), (ev, gen, ev * n, 1000 * te)): agg['EX'][k] += v
            for k, v in zip(range(4), (st['tours'], st['nodes'], st['lookups'], 1000 * tb)): agg['BB'][k] += v
        for m, name in (('EX', 'exhaustive'), ('BB', 'branch&bound')):
            a = agg[m]; print(f'| {n} | {name} | {a[0]/5:,.0f} | {a[1]/5:,.0f} | {a[2]/5:,.0f} | {a[3]/5:,.1f} | {same} |')
        red = lambda k: 100 * (1 - agg['BB'][k] / agg['EX'][k]); print(f'| {n} | reduction by B&B | {red(0):.2f} % | {red(1):.2f} % | {red(2):.2f} % | {red(3):.1f} % | |')
    print('\n## T7 how B&B scales alone (3 seeds, verified against Held-Karp where n<=14)')
    print('| n | mean search nodes | mean complete tours | mean time s | optimum = Held-Karp? |'); print('|---|---|---|---|---|')
    for n in (11, 12, 13, 14, 16, 18):
        nd = tr = tm = 0; ok = []
        for s in range(3):
            D = inst(n, s); t = time.perf_counter(); b, _, st = bnb(D); tm += time.perf_counter() - t; nd += st['nodes']; tr += st['tours']
            if n <= 14: ok.append(abs(b - held_karp(D)) < 1e-9)
        print(f'| {n} | {nd/3:,.0f} | {tr/3:,.0f} | {tm/3:.2f} | {all(ok) if ok else "not checked"} |'); sys.stdout.flush()
    print('\n## T7 adversarial: near-equal distances (uniform in [0.99, 1.01], symmetric, non-Euclidean), 5 seeds')
    print('| n | method | complete tours | search nodes | time ms | same optimum? | tours pruned away |'); print('|---|---|---|---|---|---|---|')
    for n in (9, 10):
        agg = {'EX': [0, 0, 0], 'BB': [0, 0, 0]}; same = True
        for s in range(5):
            r = random.Random(77 + s); D = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n): D[i][j] = D[j][i] = r.uniform(0.99, 1.01)
            t = time.perf_counter(); b, _, gen, ev = exhaustive(D); te = time.perf_counter() - t
            t = time.perf_counter(); b2, _, st = bnb(D); tb = time.perf_counter() - t; same &= abs(b - b2) < 1e-9
            for k, v in zip(range(3), (ev, gen, 1000 * te)): agg['EX'][k] += v
            for k, v in zip(range(3), (st['tours'], st['nodes'], 1000 * tb)): agg['BB'][k] += v
        for m, name in (('EX', 'exhaustive'), ('BB', 'branch&bound')):
            a = agg[m]; print(f'| {n} | {name} | {a[0]/5:,.0f} | {a[1]/5:,.0f} | {a[2]/5:,.1f} | {same} | {"" if m=="EX" else f"{100*(1-agg[m][0]/agg[chr(69)+chr(88)][0]):.1f} %"} |')
