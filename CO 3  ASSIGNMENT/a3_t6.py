"""A3 Task 6 - forward vs backward chaining on an organisation-hierarchy KB (10 definite-clause rules,
about 100 / 1,000 / 10,000 facts).  Run: python a3_t6.py"""
import random, time
from collections import defaultdict
from a3_logic import KB, unify, apply, rename, walk, is_var, variant_key, fmt

V = lambda x: '?' + x

# ----------------------------------------------------------------- the organisation KB
def build_org(target):
    """4-ary management tree. Per employee: ReportsTo, InDept, Level (+ a Request for every 4th, a Signed for every 8th)."""
    facts, i = [], 0; D = max(2, target // 85)
    depth = lambda k: 0 if k == 0 else depth((k - 1) // 4) + 1
    while len(facts) < target:
        e = f'e{i}'
        if i > 0: facts.append(('ReportsTo', e, f'e{(i-1)//4}'))
        facts.append(('InDept', e, f'd{i % D}')); facts.append(('Level', e, {0: 'L4', 1: 'L3', 2: 'L2'}.get(depth(i), 'L1')))
        if i > 0 and i % 4 == 0: facts.append(('Request', f'r{i}', e))
        if i > 0 and i % 8 == 0: facts.append(('Signed', f'r{i}', f'e{(i-1)//4}'))
        i += 1
    return facts, i

def rules(left_recursive=False):
    m, e, x, a, b, d, r, k = V('m'), V('e'), V('x'), V('a'), V('b'), V('d'), V('r'), V('k')
    manages2 = (('Manages', m, e), [('Manages', m, x), ('ReportsTo', e, x)]) if left_recursive else (('Manages', m, e), [('ReportsTo', e, x), ('Manages', m, x)])
    return [(('Manages', m, e), [('ReportsTo', e, m)]),                                    # R1
            manages2,                                                                     # R2 (right- or left-recursive)
            (('SameDept', a, b), [('InDept', a, d), ('InDept', b, d)]),                    # R3
            (('Senior', m), [('Level', m, 'L4')]),                                         # R4
            (('Senior', m), [('Level', m, 'L3')]),                                         # R5
            (('CanApprove', m, r), [('Request', r, e), ('Manages', m, e), ('Senior', m)]), # R6
            (('Escalate', r, m), [('CanApprove', m, r), ('Level', m, 'L4')]),              # R7
            (('Approved', r), [('CanApprove', m, r), ('Signed', r, m)]),                   # R8
            (('Peer', a, b), [('ReportsTo', a, m), ('ReportsTo', b, m)]),                  # R9
            (('Conflict', r, m), [('Request', r, e), ('Peer', e, m)])]                     # R10

# ----------------------------------------------------------------- forward chaining (naive, synchronous rounds)
def forward_chain(facts, rls):
    known = set(facts); by_pred = defaultdict(list); idx = defaultdict(list)
    def add(f):
        by_pred[f[0]].append(f)
        for p, v in enumerate(f[1:], 1): idx[(f[0], p, v)].append(f)
    for f in facts: add(f)
    st = dict(derived=0, firings=0, redundant=0, iters=0); per = defaultdict(int)
    def match(body, i, th):
        if i == len(body): yield th; return
        lit = body[i]; best = by_pred.get(lit[0], [])
        for p, a in enumerate(lit[1:], 1):
            a = walk(a, th)
            if not is_var(a):
                c = idx.get((lit[0], p, a), []); best = c if len(c) < len(best) or best is by_pred.get(lit[0], []) else best
        for f in best:
            t2 = dict(th); ok = True
            for a, b in zip(lit[1:], f[1:]):
                a = walk(a, t2)
                if is_var(a): t2[a] = b
                elif a != b: ok = False; break
            if ok: yield from match(body, i + 1, t2)
    while True:
        st['iters'] += 1; new = set()
        for head, body in rls:
            for th in match(body, 0, {}):
                st['firings'] += 1; h = apply(head, th)
                if h in known or h in new: st['redundant'] += 1
                else: new.add(h)
        if not new: break
        for h in new: known.add(h); add(h); st['derived'] += 1; per[h[0]] += 1
    return known, st, dict(per)

# ----------------------------------------------------------------- backward chaining helpers
def make_kb(facts, rls, index=True):
    kb = KB(index=index)
    for f in facts: kb.add_fact(f)
    for h, b in rls: kb.add_rule(h, b)
    return kb

def tabled_ask(kb, goal):
    """Naive tabling (answer tables + iteration to fixpoint) so that left-recursive rules terminate."""
    tables, goals = {}, {}; st = dict(unif=0, evals=0, passes=0)
    edb = lambda p: p not in kb.rules
    def solve_goal(g):
        k = variant_key(g)
        if k not in tables: tables[k] = set(); goals[k] = g; evaluate(g, k)
        return list(tables[k])
    def conj(body, i, th):
        if i == len(body): yield th; return
        lit = apply(body[i], th)
        cands = kb._facts_for(lit) if edb(lit[0]) else solve_goal(lit)
        for f in cands:
            th2 = unify(lit, f, None, False, st)
            if th2 is not None:
                from a3_logic import compose
                yield from conj(body, i + 1, compose(th, th2) if th else th2)
    def evaluate(g, k):
        st['evals'] += 1
        for f in kb._facts_for(g):
            if unify(g, f, None, False, st) is not None: tables[k].add(f)
        for h, b in kb.rules.get(g[0], []):
            ren = rename([h] + list(b)); h2, b2 = ren[0], ren[1:]
            th = unify(g, h2, None, False, st)
            if th is None: continue
            for th2 in conj(list(b2), 0, th): tables[k].add(apply(h2, th2))
    solve_goal(goal)
    while True:
        st['passes'] += 1; before = sum(len(t) for t in tables.values())
        for k in list(goals): evaluate(goals[k], k)
        if sum(len(t) for t in tables.values()) == before: break
    ans = sorted({tuple(apply(v, unify(goal, f, None, False)) for v in sorted({a for a in goal[1:] if is_var(a)})) for f in tables[variant_key(goal)]})
    return ans, st

if __name__ == '__main__':
    print('## 6A. Student A - forward chaining to a fixed point (all 10 rules)\n')
    print('| facts | employees | facts inferred | rule firings | redundant derivations | iterations (incl. final no-change round) | irrelevant derived facts, predicate-level | irrelevant, fine-grained | time s |')
    print('|---|---|---|---|---|---|---|---|---|')
    rls = rules(); relevant_preds = {'CanApprove', 'Manages', 'Senior'}
    store = {}
    for target in (100, 1000, 10000):
        facts, n = build_org(target); t = time.perf_counter(); known, st, per = forward_chain(facts, rls); dt = time.perf_counter() - t
        irr = sum(c for p, c in per.items() if p not in relevant_preds)
        rq = f'r{max(i for i in range(4, n, 4))}'; owner = f'e{max(i for i in range(4, n, 4))}'
        chain = [owner]
        while chain[-1] != 'e0': chain.append(f'e{(int(chain[-1][1:])-1)//4}')
        rel = {('Manages', m, y) for y in chain for m in chain if m != y and chain.index(m) > chain.index(y)}
        seniors = {('Senior', m) for m in chain[1:] if ('Senior', m) in known}; ca = {f for f in known if f[0] == 'CanApprove' and f[2] == rq}
        relevant = {f for f in rel | seniors | ca if f in known}
        derived_total = st['derived']; fine = 100 * (derived_total - len(relevant)) / derived_total
        print(f"| {len(facts):,} | {n:,} | {st['derived']:,} ({', '.join(f'{p} {c:,}' for p, c in sorted(per.items()))}) | {st['firings']:,} | {st['redundant']:,} | {st['iters']} | {100*irr/derived_total:.1f} % | {fine:.2f} % ({len(relevant)} relevant) | {dt:.2f} |")
        store[target] = (facts, n, rq, ca)
    print('\n## 6B. Student B - backward chaining on the same KB, query CanApprove(?m, r) for one request r (deep in the tree)\n')
    print('| facts | request | answers | goals expanded | unifications | max depth | repeated subgoals | time ms | FC firings for comparison |')
    print('|---|---|---|---|---|---|---|---|---|')
    for target in (100, 1000, 10000):
        facts, n, rq, ca = store[target]; kb = make_kb(facts, rls)
        t = time.perf_counter(); ans, st = kb.ask(('CanApprove', V('m'), rq)); dt = 1000 * (time.perf_counter() - t)
        _, fst, _ = forward_chain(facts, rls) if target < 10000 else (None, dict(firings='see 6A'), None)
        print(f"| {len(facts):,} | {rq} | {sorted(a[0] for a in ans)} | {st['goals']} | {st['unif']} | {st['maxdepth']} | {st['repeat']} | {dt:.2f} | {fst['firings'] if target < 10000 else '(6A)'} |")
    print('\nSame query with NO indexing of facts (shows what indexing saves):\n')
    print('| facts | goals expanded | unifications | time ms |'); print('|---|---|---|---|')
    for target in (100, 1000, 10000):
        facts, n, rq, ca = store[target]; kb = make_kb(facts, rls, index=False); t = time.perf_counter(); ans, st = kb.ask(('CanApprove', V('m'), rq)); print(f"| {len(facts):,} | {st['goals']} | {st['unif']:,} | {1000*(time.perf_counter()-t):.1f} |")
    print('\n## 6C. A left-recursive rule on which naive backward chaining never terminates\n')
    print('Replace R2 by the left-recursive  Manages(m,e) ⇐ Manages(m,x) ∧ ReportsTo(e,x).  Query: Manages(?m, e) for the owner e of the request.\n')
    print('| facts | method | outcome | answers | goals expanded | unifications | max depth | repeated subgoals | time ms |'); print('|---|---|---|---|---|---|---|---|---|')
    rl = rules(True)
    for target in (100, 1000, 10000):
        facts, n, rq, ca = store[target]; owner = [f for f in facts if f[0] == 'Request' and f[1] == rq][0][2]
        goal = ('Manages', V('m'), owner)
        right = make_kb(facts, rls); ans0, st0 = right.ask(goal); base = sorted(a[0] for a in ans0)
        print(f"| {len(facts):,} | right-recursive baseline (R2 as before) | terminates | {len(base)} | {st0['goals']} | {st0['unif']} | {st0['maxdepth']} | {st0['repeat']} | - |")
        NB = 5000 if target < 10000 else 1500
        kb = make_kb(facts, rl); kb.limit = NB; t = time.perf_counter()
        try: ans, st = kb.ask(goal, max_depth=10**6); out = 'terminates'
        except RuntimeError: ans, st, out = [], dict(kb.stats), f'NEVER TERMINATES: stopped by the {NB:,}-goal budget'
        print(f"| {len(facts):,} | naive BC, left-recursive | {out} | {len(ans)} | {st['goals']} | {st['unif']} | {st['maxdepth']} | {st['repeat']} | {1000*(time.perf_counter()-t):.0f} |")
        D = 14
        DB = 400000 if target < 10000 else 1500
        kb = make_kb(facts, rl); kb.limit = DB; t = time.perf_counter()
        try: ans, st = kb.ask(goal, max_depth=D); out = f'terminates (depth bound {D})'
        except RuntimeError: ans, st, out = [], dict(kb.stats), f'budget ({DB:,} goals) exceeded'
        ok = sorted(a[0] for a in ans) == base if ans else None
        print(f"| {len(facts):,} | remedy 1: depth bound {D} | {out}; answers = baseline: {ok} | {len(ans)} | {st['goals']} | {st['unif']} | {st['maxdepth']} | {st['repeat']} | {1000*(time.perf_counter()-t):.0f} |")
        if target >= 10000:
            print(f"| {len(facts):,} | remedy 2: tabling | NOT RUN at this size: cost grew x{846164/5173:.0f} from 102 to 1,001 facts (5,173 -> 846,164 unifications), i.e. > 10^7 unifications here | - | - | - | - | - | - |"); continue
        kb = make_kb(facts, rl); t = time.perf_counter(); ans, st = tabled_ask(kb, goal); dt = 1000 * (time.perf_counter() - t)
        print(f"| {len(facts):,} | remedy 2: tabling (memoised answers) | terminates; answers = baseline: {sorted(a[0] for a in ans) == base} | {len(ans)} | {st['evals']} table evaluations, {st['passes']} passes | {st['unif']:,} | - | - | {dt:.0f} |")
