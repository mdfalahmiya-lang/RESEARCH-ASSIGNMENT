"""A2 Task 3 - how tree structure (move ordering) controls alpha-beta work.
Trees: uniform branching b, depth d, root = MAX. Leaves are distinct random integers (seed 7) so that
ordering, not ties, decides pruning; except the 'equal leaves' test. A tree is a nested list; a leaf is an int."""
import random, math, statistics

def gen(b, d, rnd, equal=False):
    if d == 0: return 0 if equal else rnd.random()
    return [gen(b, d - 1, rnd, equal) for _ in range(b)]

def value(t, maxn):
    if not isinstance(t, list): return t
    vs = [value(c, not maxn) for c in t]; return max(vs) if maxn else min(vs)

def reorder(t, maxn, mode, rnd):
    """best: strongest move first at every node (MAX: descending value, MIN: ascending); worst: reverse."""
    if not isinstance(t, list): return t
    kids = [reorder(c, not maxn, mode, rnd) for c in t]
    if mode == 'random': rnd.shuffle(kids); return kids
    key = lambda c: value(c, not maxn)
    asc = (mode == 'best') == (not maxn)          # MIN+best -> ascending ; MAX+worst -> ascending
    return sorted(kids, key=key, reverse=not asc)

def minimax(t, maxn, c):
    c['nodes'] += 1
    if not isinstance(t, list): c['leaves'] += 1; return t
    vs = [minimax(x, not maxn, c) for x in t]; return max(vs) if maxn else min(vs)

def alphabeta(t, maxn, a, b, c):
    c['nodes'] += 1
    if not isinstance(t, list): c['leaves'] += 1; return t
    if maxn:
        v = -math.inf
        for x in t:
            v = max(v, alphabeta(x, False, a, b, c)); a = max(a, v)
            if a >= b: c['cuts'] += 1; break
        return v
    v = math.inf
    for x in t:
        v = min(v, alphabeta(x, True, a, b, c)); b = min(b, v)
        if a >= b: c['cuts'] += 1; break
    return v

def run(t):
    m = dict(nodes=0, leaves=0, cuts=0); vm = minimax(t, True, m)
    a = dict(nodes=0, leaves=0, cuts=0); va = alphabeta(t, True, -math.inf, math.inf, a)
    assert vm == va                                          # correctness: same root value
    return m, a

def predicted_best(b, d):
    nodes = sum(b ** math.ceil(l / 2) + b ** (l // 2) - 1 for l in range(d + 1))
    return nodes, b ** math.ceil(d / 2) + b ** (d // 2) - 1

if __name__ == '__main__':
    print('| b | d | test | minimax nodes | PREDICTED a-b nodes | a-b nodes | a-b leaves | cutoffs | a-b/minimax |')
    print('|---|---|---|---|---|---|---|---|---|')
    for b, d in ((4, 6), (3, 8), (5, 5)):
        rnd = random.Random(7); base = gen(b, d, rnd)
        total = (b ** (d + 1) - 1) // (b - 1)
        pb, pl = predicted_best(b, d)
        rows = []
        rows.append(('1 best ordering', pb, reorder(base, True, 'best', rnd)))
        rows.append(('2 worst ordering', total, reorder(base, True, 'worst', rnd)))
        eq = gen(b, d, rnd, equal=True); rows.append(('3a all leaves equal', pb, eq))
        for name, pred, t in rows:
            m, a = run(t)
            print(f"| {b} | {d} | {name} | {m['nodes']:,} | {pred:,} | {a['nodes']:,} | {a['leaves']:,} | {a['cuts']:,} | {a['nodes']/m['nodes']:.3f} |")
        res = []
        for s in range(100):
            r2 = random.Random(1000 + s); t = reorder(base, True, 'random', r2); res.append(run(t)[1])
        ns = [x['nodes'] for x in res]; ls = [x['leaves'] for x in res]
        pr = round(b ** (0.75 * d))
        print(f"| {b} | {d} | 3b random ordering (100 shuffles): mean | {total:,} | leaves≈b^(3d/4)={pr:,} | {statistics.mean(ns):,.0f} | {statistics.mean(ls):,.0f} | {statistics.mean(x['cuts'] for x in res):,.0f} | {statistics.mean(ns)/total:.3f} |")
        print(f"| {b} | {d} | 3b random ordering: min / max nodes | | | {min(ns):,} / {max(ns):,} | | | |")
    # same b and d, wide spread: leaf evaluations only
    b, d = 4, 6; rnd = random.Random(7); base = gen(b, d, rnd)
    best = run(reorder(base, True, 'best', rnd))[1]['leaves']; worst = run(reorder(base, True, 'worst', rnd))[1]['leaves']
    print(f"\nSame b=4, d=6 (4,096 leaves): alpha-beta leaf evaluations range from {best} (best order) to {worst} (worst order): factor {worst/best:.1f}")
