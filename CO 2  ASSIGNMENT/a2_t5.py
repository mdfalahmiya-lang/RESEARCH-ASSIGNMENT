"""A2 Task 5 - constraint propagation derived from the principle
 'remove v from D(x) if some neighbour y has no value compatible with v'.
Constraints: exams sharing students may not share a slot (binary 'not equal' on conflict-graph edges).
Algorithms: BT (plain chronological), AC3+BT (propagate once, then BT), MAC (propagate after every assignment).
Counters: nodes = value assignments tried, backtracks = dead ends, checks = compatibility tests, wipes = domain wipe-outs.
Seeds: random instances 3000 + 17*n + s."""
import random, sys
from collections import deque

class Cap(Exception): pass

def new_cnt(): return dict(nodes=0, backtracks=0, checks=0, wipes=0)

def compatible(cnt, a, b):
    cnt['checks'] += 1; return a != b

def revise(adj, dom, x, y, cnt):
    """Delete every value of x that has no support in D(y)."""
    removed = False
    for vx in sorted(dom[x]):
        if not any(compatible(cnt, vx, vy) for vy in dom[y]):
            dom[x].discard(vx); removed = True
    return removed

def ac3(adj, dom, cnt, queue=None, trace=None):
    q = deque(queue if queue is not None else [(x, y) for x in range(len(adj)) for y in adj[x]])
    while q:
        x, y = q.popleft()                                    # arc (x,y): revise D(x) against D(y)
        if revise(adj, dom, x, y, cnt):
            if trace is not None: trace.append((x, y, [len(d) for d in dom]))
            if not dom[x]: cnt['wipes'] += 1; return False    # wipe-out => no solution
            for z in adj[x]:                                  # x changed => neighbours z must be re-checked against x
                if z != y: q.append((z, x))
    return True

def solve(adj, dom0, mode, cap=300000):
    n = len(adj); cnt = new_cnt(); dom = [set(d) for d in dom0]; sol = [None] * n
    if mode in ('AC3+BT', 'MAC'):
        if not ac3(adj, dom, cnt): return None, cnt, 'no solution (by propagation alone)'
    def rec(i, dom):
        if i == n: return True
        for v in sorted(dom[i]):
            cnt['nodes'] += 1
            if cnt['nodes'] > cap: raise Cap
            if mode == 'MAC':
                nd = [set(d) for d in dom]; nd[i] = {v}
                if ac3(adj, nd, cnt, [(z, i) for z in adj[i] if z > i]):
                    sol[i] = v
                    if rec(i + 1, nd): return True
            else:
                ok = True
                for z in adj[i]:
                    if z < i and not compatible(cnt, sol[z], v): ok = False; break
                if ok:
                    sol[i] = v
                    if rec(i + 1, dom): return True
        cnt['backtracks'] += 1; return False
    try:
        ok = rec(0, dom)
    except Cap:
        return None, cnt, 'DNF (node cap)'
    return (sol if ok else None), cnt, ('solved' if ok else 'no solution (after search)')

def cycle(n):
    adj = [set() for _ in range(n)]
    for i in range(n): adj[i].add((i + 1) % n); adj[(i + 1) % n].add(i)
    return [sorted(a) for a in adj]

def random_graph(n, deg, seed):
    rnd = random.Random(seed); p = deg / (n - 1); adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rnd.random() < p: adj[i].add(j); adj[j].add(i)
    return [sorted(a) for a in adj]

def valid(adj, sol): return sol is not None and all(sol[i] != sol[j] for i in range(len(adj)) for j in adj[i])

if __name__ == '__main__':
    designed = [('I1 8-cycle, 2 slots, E0 pinned to slot 0', cycle(8), [{0}] + [{0, 1} for _ in range(7)]),
                ('I2 triangle, 2 slots, E0 pinned', [[1, 2], [0, 2], [0, 1]], [{0}, {0, 1}, {0, 1}]),
                ('I3 odd 9-cycle, 2 slots, nothing pinned (arc-consistent but unsolvable)', cycle(9), [{0, 1} for _ in range(9)])]
    print('| instance | algorithm | outcome | nodes | backtracks | checks | wipe-outs |'); print('|---|---|---|---|---|---|---|')
    for name, adj, dom in designed:
        for mode in ('BT', 'AC3+BT', 'MAC'):
            sol, cnt, out = solve(adj, dom, mode)
            if sol: assert valid(adj, sol)
            print(f"| {name} | {mode} | {out} | {cnt['nodes']} | {cnt['backtracks']} | {cnt['checks']} | {cnt['wipes']} |")
    # trace of shrinking domains on I1 and I2
    for name, adj, dom in designed[:2]:
        d = [set(x) for x in dom]; tr = []; cnt = new_cnt(); ok = ac3(adj, d, cnt, trace=tr)
        print(f'\nTRACE {name}: propagation {"succeeded" if ok else "hit a wipe-out"}; domain sizes after each removal step (revise x vs y):')
        print('  start:', [len(x) for x in dom])
        for k, (x, y, sz) in enumerate(tr): print(f'  step {k+1}: revise E{x} against E{y} -> sizes {sz}')
        print('  final domains:', [sorted(x) for x in d])
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        name, adj, dom = designed[0]; d = [set(x) for x in dom]; tr = []; ac3(adj, d, new_cnt(), trace=tr)
        sizes = [[len(x) for x in dom]] + [t[2] for t in tr]
        fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
        im = ax[0].imshow(list(zip(*sizes)), aspect='auto', cmap='viridis_r'); ax[0].set_xlabel('propagation step (0 = initial)'); ax[0].set_ylabel('exam'); ax[0].set_title('Domain size per exam (I1: 8-cycle, 2 slots)'); plt.colorbar(im, ax=ax[0])
        ax[1].plot([sum(s) for s in sizes], 'o-'); ax[1].set_xlabel('propagation step'); ax[1].set_ylabel('total domain values left'); ax[1].set_title('Shrinking domains: 15 values -> 8 (one per exam)'); ax[1].grid(alpha=.3)
        plt.tight_layout(); plt.savefig('fig_t5_domains.png', dpi=130)
    except Exception as e: print('plot skipped', e)
    print('\nSCALING: random timetables, 4 slots, mean degree 6; 5 instances per n; node cap 300,000 (DNF if exceeded)')
    print('| exams n | algorithm | solved / unsat / DNF | mean nodes | mean backtracks | mean checks | mean wipe-outs |'); print('|---|---|---|---|---|---|---|')
    raw = {}
    for n in (10, 15, 20, 25, 30, 35, 40):
        for mode in ('BT', 'AC3+BT', 'MAC'):
            agg = dict(nodes=0, backtracks=0, checks=0, wipes=0); s_ = u_ = f_ = 0
            for s in range(5):
                adj = random_graph(n, 6, 3000 + 17 * n + s); dom = [set(range(4)) for _ in range(n)]
                sol, cnt, out = solve(adj, dom, mode)
                if out == 'solved': s_ += 1; assert valid(adj, sol)
                elif out.startswith('DNF'): f_ += 1
                else: u_ += 1
                for k in agg: agg[k] += cnt[k]
            print(f"| {n} | {mode} | {s_} / {u_} / {f_} | {agg['nodes']/5:,.0f} | {agg['backtracks']/5:,.0f} | {agg['checks']/5:,.0f} | {agg['wipes']/5:,.1f} |")
            sys.stdout.flush()
