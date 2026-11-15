"""T7 second adversary: 'paired cities' - city 2k and 2k+1 are 1 apart (so every city's cheapest edge is 1),
all other distances uniform in [50,100]. The bound minout[] then says ~1 per city although a tour must
pay ~n/2 expensive edges -> weak bound. Seeds 123+s."""
import random, time, math
from a2_t6_t7 import exhaustive, bnb
print('| n | method | complete tours | search nodes | time ms | same optimum? | tours pruned away |'); print('|---|---|---|---|---|---|---|')
for n in (8, 9, 10, 11, 12):
    agg = {'EX': [0, 0, 0], 'BB': [0, 0, 0]}; same = True; runs = 5 if n <= 10 else 2
    for s in range(runs):
        r = random.Random(123 + s); D = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                D[i][j] = D[j][i] = 1.0 if (i // 2 == j // 2) else r.uniform(50, 100)
        if n <= 11:
            t = time.perf_counter(); b, _, gen, ev = exhaustive(D); te = time.perf_counter() - t
            for k, v in zip(range(3), (ev, gen, 1000 * te)): agg['EX'][k] += v
        t = time.perf_counter(); b2, _, st = bnb(D); tb = time.perf_counter() - t
        if n <= 11: same &= abs(b - b2) < 1e-9
        for k, v in zip(range(3), (st['tours'], st['nodes'], 1000 * tb)): agg['BB'][k] += v
    if n <= 11:
        a = agg['EX']; print(f'| {n} | exhaustive | {a[0]/runs:,.0f} | {a[1]/runs:,.0f} | {a[2]/runs:,.1f} | {same} | |')
    a = agg['BB']; pr = f"{100*(1-a[0]/agg['EX'][0]):.1f} %" if n <= 11 else 'n/a (exhaustive too slow)'
    print(f'| {n} | branch&bound | {a[0]/runs:,.0f} | {a[1]/runs:,.0f} | {a[2]/runs:,.1f} | {same if n<=11 else "not checked"} | {pr} |')
