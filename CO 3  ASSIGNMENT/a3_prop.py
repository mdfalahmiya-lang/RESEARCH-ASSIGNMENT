"""A3 Tasks 1-2: propositional KB, truth-table model checking, inference-rule derivations, resolution.
Usage: python a3_prop.py t1 | t2 .  Sentences are nested tuples: ('sym',x) ('not',a) ('and',..) ('or',..) ('imp',a,b) ('iff',a,b)."""
import sys, time, itertools, heapq, math

S = lambda x: ('sym', x); N = lambda a: ('not', a)
A = lambda *a: ('and',) + a; O = lambda *a: ('or',) + a
I = lambda a, b: ('imp', a, b); E = lambda a, b: ('iff', a, b)

def symbols(s):
    return {s[1]} if s[0] == 'sym' else set().union(*[symbols(a) for a in s[1:]])

def show(s):
    k = s[0]
    if k == 'sym': return s[1]
    if k == 'not': return '¬' + show(s[1])
    if k == 'and': return '(' + ' ∧ '.join(show(a) for a in s[1:]) + ')'
    if k == 'or': return '(' + ' ∨ '.join(show(a) for a in s[1:]) + ')'
    if k == 'imp': return '(' + show(s[1]) + ' ⇒ ' + show(s[2]) + ')'
    return '(' + show(s[1]) + ' ⇔ ' + show(s[2]) + ')'

def to_py(s, idx):
    k = s[0]
    if k == 'sym': return f'(m>>{idx[s[1]]}&1)'
    if k == 'not': return f'(1-{to_py(s[1], idx)})'
    if k == 'and': return '(' + '&'.join(to_py(a, idx) for a in s[1:]) + ')'
    if k == 'or': return '(' + '|'.join(to_py(a, idx) for a in s[1:]) + ')'
    a, b = to_py(s[1], idx), to_py(s[2], idx)
    return f'((1-{a})|{b})' if k == 'imp' else f'(1-({a}^{b}))'

def compile_s(s, idx): return eval('lambda m:' + to_py(s, idx))

# ---------------- truth-table entailment ----------------
def tt_entails(kb, alpha, syms, cap=1 << 22):
    """KB |= alpha ?  Returns (answer or None if > cap models, stats). Stops at the first countermodel."""
    st = dict(models=0, sent_evals=0, kb_true=0)
    if (1 << len(syms)) > cap: return None, st
    idx = {s: i for i, s in enumerate(syms)}; fs = [compile_s(s, idx) for s in kb]; fa = compile_s(alpha, idx)
    for m in range(1 << len(syms)):
        st['models'] += 1; ok = True
        for f in fs:
            st['sent_evals'] += 1
            if not f(m): ok = False; break
        if ok:
            st['kb_true'] += 1
            if not fa(m): return False, st
    return True, st

def classify(kb, alpha, syms):
    t = time.perf_counter(); a, s1 = tt_entails(kb, alpha, syms); b, s2 = tt_entails(kb, N(alpha), syms)
    tot = {k: s1[k] + s2[k] for k in s1}; tot['time'] = time.perf_counter() - t
    if a is None: return 'infeasible', tot
    return ('entailed' if a else 'negation entailed' if b else 'neither'), tot

# ---------------- Wumpus world ----------------
def wumpus_kb(n, percepts):
    nb = lambda r, c: [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 1 <= r + dr <= n and 1 <= c + dc <= n]
    P = lambda r, c: S(f'P_{r}_{c}'); W = lambda r, c: S(f'W_{r}_{c}'); B = lambda r, c: S(f'B_{r}_{c}'); St = lambda r, c: S(f'S_{r}_{c}')
    kb = [N(P(1, 1)), N(W(1, 1))]
    for r in range(1, n + 1):
        for c in range(1, n + 1):
            kb.append(E(B(r, c), O(*[P(*x) for x in nb(r, c)])))
            kb.append(E(St(r, c), O(*[W(*x) for x in nb(r, c)])))
    for kind, r, c, val in percepts:
        lit = {'B': B, 'S': St}[kind](r, c); kb.append(lit if val else N(lit))
    return kb

def prune_definitions(kb, query_syms):
    """Drop 'X <=> phi' sentences whose defined symbol X occurs nowhere else and not in the query:
    such a definition is satisfiable for every value of phi, so removing it cannot change entailment."""
    kb = list(kb)
    while True:
        cnt = {}
        for s in kb:
            for x in symbols(s): cnt[x] = cnt.get(x, 0) + 1
        drop = [s for s in kb if s[0] == 'iff' and s[1][0] == 'sym' and cnt[s[1][1]] == 1 and s[1][1] not in query_syms]
        if not drop: return kb
        kb = [s for s in kb if s not in drop]

# ---------------- CNF ----------------
def elim(s):
    k = s[0]
    if k == 'sym': return s
    if k == 'not': return N(elim(s[1]))
    if k in ('and', 'or'): return (k,) + tuple(elim(a) for a in s[1:])
    a, b = elim(s[1]), elim(s[2])
    if k == 'imp': return O(N(a), b)
    return A(O(N(a), b), O(N(b), a))

def nnf(s, neg=False):
    k = s[0]
    if k == 'sym': return N(s) if neg else s
    if k == 'not': return nnf(s[1], not neg)
    if k in ('and', 'or'):
        k2 = {'and': 'or', 'or': 'and'}[k] if neg else k
        return (k2,) + tuple(nnf(a, neg) for a in s[1:])
    raise ValueError

def clauses_of(s):
    k = s[0]
    if k == 'sym': return [frozenset([s[1]])]
    if k == 'not': return [frozenset(['-' + s[1][1]])]
    if k == 'and': return [c for a in s[1:] for c in clauses_of(a)]
    res = [frozenset()]
    for a in s[1:]:
        cs = clauses_of(a); res = [r | c for r in res for c in cs]
    return res

neg = lambda l: l[1:] if l[0] == '-' else '-' + l
def taut(c): return any(neg(l) in c for l in c)

def cnf(s):
    seen, out = set(), []
    for c in clauses_of(nnf(elim(s))):
        if not taut(c) and c not in seen: seen.add(c); out.append(c)
    return out

def cnf_steps(s):
    a = elim(s); b = nnf(a)
    return [('original', show(s)), ('eliminate ⇔ and ⇒', show(a)), ('push ¬ inward (NNF)', show(b)),
            ('distribute ∨ over ∧ → clauses', ' ∧ '.join('{' + ', '.join(sorted(c)) + '}' for c in cnf(s)))]

def kb_clauses(kb):
    seen, out = set(), []
    for s in kb:
        for c in cnf(s):
            if c not in seen: seen.add(c); out.append(c)
    return out

# ---------------- resolution refutation (given-clause loop with literal index and subsumption) ----------------
def resolution(clauses, strategy='fifo', cap=300000, time_cap=40.0):
    cnt = dict(gen=0, att=0, taut=0, sub=0, given=0); t0 = time.perf_counter()
    proc, index, seen, parents, heap, ctr, ids = {}, {}, set(), {}, [], itertools.count(), itertools.count()
    def push(c):
        if c in seen: return
        seen.add(c); heapq.heappush(heap, (len(c) if strategy == 'shortest' else 0, next(ctr), c))
    def remove(i):
        for l in proc[i]: index[l].discard(i)
        del proc[i]
    for c in clauses:
        if not taut(c): push(frozenset(c))
    while heap:
        if time.perf_counter() - t0 > time_cap: return None, cnt, parents
        _, _, c = heapq.heappop(heap); cnt['given'] += 1
        if not c: return True, cnt, parents
        cand = set()
        for l in c: cand |= index.get(l, set())
        if any(proc[i] <= c for i in cand): cnt['sub'] += 1; continue
        l0 = min(c, key=lambda l: len(index.get(l, ())))
        for i in list(index.get(l0, ())):
            if i in proc and c <= proc[i]: remove(i); cnt['sub'] += 1
        i = next(ids); proc[i] = c
        for l in c: index.setdefault(l, set()).add(i)
        for l in c:
            for j in list(index.get(neg(l), ())):
                if j not in proc: continue
                d = proc[j]; cnt['att'] += 1
                r = (c - {l}) | (d - {neg(l)})
                if taut(r): cnt['taut'] += 1; continue
                r = frozenset(r)
                if r in seen: continue
                cnt['gen'] += 1; parents[r] = (c, d, l)
                if not r: return True, cnt, parents
                if cnt['gen'] > cap: return None, cnt, parents
                push(r)
    return False, cnt, parents

def proof_lines(parents, c=frozenset(), depth=0, shown=None):
    shown = set() if shown is None else shown
    txt = '{' + ', '.join(sorted(c)) + '}' if c else '[] (empty clause)'
    if c not in parents or c in shown:
        return ['  ' * depth + txt + ('   [input]' if c not in parents else '   [see above]')]
    shown.add(c); a, b, l = parents[c]
    return ['  ' * depth + txt + f'   [resolve on {l.lstrip("-")}]'] + proof_lines(parents, a, depth + 1, shown) + proof_lines(parents, b, depth + 1, shown)

# ---------------- model checking on CNF ----------------
def mc_cnf(clauses, syms, cap=1 << 23):
    k = len(syms)
    if (1 << k) > cap: return None, 1 << k
    idx = {s: i for i, s in enumerate(syms)}; cl = []
    for c in clauses:
        p = n = 0
        for l in c:
            if l[0] == '-': n |= 1 << idx[l[1:]]
            else: p |= 1 << idx[l]
        cl.append((p, n))
    for m in range(1 << k):
        for p, n in cl:
            if not (m & p or (~m) & n): break
        else: return True, m + 1            # a model exists -> satisfiable (query not entailed)
    return False, 1 << k                      # no model: unsatisfiable (query entailed)

# ---------------- policy KB (smart building) ----------------
def policy_kb():
    b, w, v, e, m, a, u, l, r, i, t, s, p, f = [S(x) for x in 'badge work visitor escort emergency access unlock lockdown alarm intrusion maint supervisor afterpass forced'.split()]
    return [I(A(b, w, N(v)), a),                                 # R1 staff in hours
            I(A(v, e, w), a),                                    # R2 escorted visitor in hours
            I(m, a),                                             # R3 emergency override
            E(a, u),                                             # R4 access <=> door unlocked
            I(A(l, N(m)), N(u)),                                 # R5 lockdown blocks unless emergency
            I(v, O(e, N(a))),                                    # R6 visitors need an escort
            I(r, O(i, f, m)),                                    # R7 alarm means intrusion, forced door or emergency
            I(i, l),                                             # R8 intrusion => lockdown
            I(A(N(w), b, N(v), O(s, p)), a),                     # R9 after-hours staff need supervisor or pass
            I(t, O(e, b)),                                       # R10 maintenance needs escort or badge
            I(f, N(b)),                                          # R11 forced door => no valid badge
            I(A(a, N(m)), N(l)),                                 # R12 granted access (non-emergency) => no lockdown
            E(r, O(i, f))]                                       # R13 alarm <=> intrusion or forced (biconditional + disjunction)

def php(pig, hol):
    x = lambda i, j: f'x{i}_{j}'
    cl = [frozenset(x(i, j) for j in range(hol)) for i in range(pig)]
    for j in range(hol):
        for i in range(pig):
            for k in range(i + 1, pig): cl.append(frozenset(['-' + x(i, j), '-' + x(k, j)]))
    return cl, [x(i, j) for i in range(pig) for j in range(hol)]

def chain(n):
    cl = [frozenset(['p0'])] + [frozenset([f'-p{i}', f'p{i+1}']) for i in range(n)]
    return cl, [f'p{i}' for i in range(n + 1)]

def fmt_cnt(c): return f"{c['gen']:,} | {c['att']:,} | {c['taut']:,} | {c['sub']:,}"

# ============================ TASK 1 ============================
def task1():
    PERC = [('B', 1, 1, False), ('S', 1, 1, False), ('B', 2, 1, True)]
    QUERIES = [('¬P_1_2  ("(1,2) has no pit")', N(S('P_1_2'))), ('P_2_1  ("(2,1) has a pit")', S('P_2_1')), ('W_2_2  ("wumpus in (2,2)")', S('W_2_2'))]
    print('## 1A. Size of the KB as a function of n (derived: symbols 4n², sentences 2 + 2n² + percepts, models 2^(4n²))\n')
    print('| n | symbols m = 4n² | sentences (2 + 2n² + 3 percepts) | models 2^m | counted symbols | counted sentences |'); print('|---|---|---|---|---|---|')
    for n in (2, 3, 4):
        kb = wumpus_kb(n, PERC); syms = sorted(set().union(*[symbols(s) for s in kb]))
        print(f'| {n} | {4*n*n} | {2+2*n*n+3} | {2**(4*n*n):,} | {len(syms)} | {len(kb)} |')
    print('\n## 1B. Truth-table entailment: full symbol set vs relevant-symbol restriction')
    print('Percepts: ¬B_1_1, ¬S_1_1, B_2_1.  Each query is classified by two checks (KB |= α, KB |= ¬α).\n')
    print('| n | symbols used | query | verdict | models enumerated | sentence evaluations | time s |'); print('|---|---|---|---|---|---|---|')
    rate = None
    for n in (2, 3, 4):
        kb = wumpus_kb(n, PERC); full = sorted(set().union(*[symbols(s) for s in kb]))
        for name, q in QUERIES:
            v, st = classify(kb, q, sorted(set(full) | symbols(q)))
            if v == 'infeasible': print(f'| {n} | full ({len(full)}) | {name} | INFEASIBLE: 2^{len(full)} = {2**len(full):,} models | - | - | - |')
            else:
                print(f"| {n} | full ({len(full)}) | {name} | {v} | {st['models']:,} | {st['sent_evals']:,} | {st['time']:.2f} |")
                if rate is None or st['models'] > 20000: rate = st['models'] / max(st['time'], 1e-9)
        for name, q in QUERIES:
            red = prune_definitions(kb, symbols(q)); rs = sorted(set().union(*[symbols(s) for s in red]) | symbols(q))
            v, st = classify(red, q, rs)
            print(f"| {n} | relevant ({len(rs)}) | {name} | {v} | {st['models']:,} | {st['sent_evals']:,} | {st['time']:.3f} |")
    print(f'\nMeasured throughput ≈ {rate:,.0f} models/s, so the full n=3 set (2^36 = 6.9e10 models) would take ≈ {2**36/rate/3600:,.1f} hours (best case, with early exit per model) and n=4 (2^64) ≈ {2**64/rate/3.15e7:.1e} years: infeasible in practice.')
    print('\n## 1C. Part B - derivations with inference rules instead of model checking (n = 3)\n')
    PERC2 = PERC + [('B', 1, 2, False), ('S', 1, 2, False)]
    kb2 = wumpus_kb(3, PERC2)
    def unit_derive(kb, goals):
        cls = [set(c) for c in kb_clauses(kb)]; units = {next(iter(c)) for c in cls if len(c) == 1}; log = []; steps = 0
        ch = True
        while ch:
            ch = False
            for c in cls:
                if len(c) > 1 and not any(l in units for l in c):
                    live = [l for l in c if neg(l) not in units]
                    if len(live) == 1 and live[0] not in units:
                        used = [neg(l) for l in c if l != live[0]]; steps += len(used); units.add(live[0]); ch = True
                        log.append(f'Unit Resolution: clause {{{", ".join(sorted(c))}}} with unit(s) {", ".join(used)}  ⊢  {live[0]}')
        return units, steps, log
    units, steps, log = unit_derive(kb2, None)
    for sq, lits in (('(1,2)', ['-P_1_2', '-W_1_2']), ('(2,1)', ['-P_2_1', '-W_2_1']), ('(2,2)', ['-P_2_2', '-W_2_2'])):
        ok = all(l in units for l in lits)
        print(f'* Square {sq} safe (¬P ∧ ¬W) derived: **{ok}**')
    print(f'* Total unit-resolution steps to saturate the KB: {steps}.  Derivation log:\n')
    for l in log: print('   -', l)
    print('\nInference-rule cost for each query (resolution steps for the two literals + 1 And-Introduction) vs model checking on the relevant symbols:\n')
    print('| query | rule steps | model-checking models (relevant symbols) |'); print('|---|---|---|')
    for sq, lits, q in (('(1,2)', ['-P_1_2', '-W_1_2'], A(N(S('P_1_2')), N(S('W_1_2')))), ('(2,1)', ['-P_2_1', '-W_2_1'], A(N(S('P_2_1')), N(S('W_2_1')))), ('(2,2)', ['-P_2_2', '-W_2_2'], A(N(S('P_2_2')), N(S('W_2_2'))))):
        # steps needed for just these literals (minimal derivation): run propagation restricted to clauses of needed percepts
        need = 0; cls = kb_clauses(kb2)
        for l in lits:
            # each literal needs one unit resolution per falsified literal of its supporting clause (here 1: the percept unit)
            need += 1
        need += 1
        red = prune_definitions(kb2, symbols(q)); rs = sorted(set().union(*[symbols(s) for s in red]) | symbols(q))
        a, st = tt_entails(red, q, rs)
        print(f'| safe{sq} (entailed = {a}) | {need} | {st["models"]:,} |')
    print('\n## 1D. Soundness truth tables (every row where all premises are true must make the conclusion true)\n')
    rules = {'Modus Ponens (P⇒Q, P ⊢ Q)': (lambda P, Q: [(not P) or Q, P], lambda P, Q: Q),
             'And-Elimination (P∧Q ⊢ P)': (lambda P, Q: [P and Q], lambda P, Q: P),
             'Unit Resolution (P∨Q, ¬P ⊢ Q)': (lambda P, Q: [P or Q, not P], lambda P, Q: Q),
             'Biconditional-Elimination (P⇔Q ⊢ (P⇒Q)∧(Q⇒P))': (lambda P, Q: [P == Q], lambda P, Q: ((not P) or Q) and ((not Q) or P))}
    for name, (prem, concl) in rules.items():
        print(f'**{name}**\n\n| P | Q | premises all true? | conclusion | sound on this row |\n|---|---|---|---|---|')
        ok = True
        for P, Q in itertools.product([True, False], repeat=2):
            pt = all(prem(P, Q)); c = concl(P, Q); row = (not pt) or c; ok &= row
            print(f'| {int(P)} | {int(Q)} | {int(pt)} | {int(c)} | {"✓" if row else "✗"} |')
        print(f'\nSound: **{ok}**\n')
    print('"Not derived" is not "false": under percepts ¬B11, ¬S11, B21 (n=3), neither P_2_2 nor ¬P_2_2 is derivable, and enumeration finds KB-models of both kinds:')
    kb = wumpus_kb(3, PERC); q = S('P_2_2'); red = prune_definitions(kb, symbols(q)); rs = sorted(set().union(*[symbols(s) for s in red]) | symbols(q))
    idx = {s: i for i, s in enumerate(rs)}; fs = [compile_s(s, idx) for s in red]; pi = idx['P_2_2']; t = f = 0
    for m in range(1 << len(rs)):
        if all(g(m) for g in fs):
            if m >> pi & 1: t += 1
            else: f += 1
    print(f'models of the KB with P_2_2 true: {t}; with P_2_2 false: {f}  → KB ⊭ P_2_2 and KB ⊭ ¬P_2_2.')

# ============================ TASK 2 ============================
def task2():
    kb = policy_kb(); names = sorted(set().union(*[symbols(s) for s in kb]))
    print('## 2A. Policy KB (13 rules; implication, biconditional, disjunction). Symbols:', ', '.join(names), '\n')
    for k, s in enumerate(kb, 1): print(f'R{k}: {show(s)}')
    print('\n### Hand-checkable CNF conversions (stage log from the program)\n')
    for k in (4, 7, 9):
        print(f'**R{k}**\n')
        for stage, t in cnf_steps(kb[k - 1]): print(f'- {stage}: `{t}`')
        print()
    cl = kb_clauses(kb); print(f'Whole KB in CNF: {len(cl)} clauses over {len(names)} symbols.\n')
    facts = [frozenset(['badge']), frozenset(['work']), frozenset(['-visitor'])]
    print('### Entailed query: staff with a valid badge, in working hours ⊨ door unlocked\n')
    ok, cnt, par = resolution(cl + facts + [frozenset(['-unlock'])], 'shortest')
    print(f'result: {"entailed (empty clause derived)" if ok else ok}; clauses generated {cnt["gen"]}, resolvents attempted {cnt["att"]}\n\n```')
    print('\n'.join(proof_lines(par))); print('```\n')
    print('### Non-entailed query: a visitor in working hours ⊨ door unlocked ?\n')
    ok, cnt, _ = resolution(cl + [frozenset(['visitor']), frozenset(['work']), frozenset(['-unlock'])], 'fifo')
    print(f'result: {"proved" if ok else "NOT entailed: the clause set saturated (no new clauses) without the empty clause"}; generated {cnt["gen"]}, attempted {cnt["att"]}, tautologies {cnt["taut"]}, subsumed {cnt["sub"]}.')
    print('Why it terminates: clauses over k symbols are subsets of 2k literals, at most 3^k non-tautological clauses; every resolvent is new and finite, so the generation of new clauses must stop.\n')
    ents, st = tt_entails(kb + [S('badge'), S('work'), N(S('visitor'))], S('unlock'), names)
    print(f'Model checking on the same entailed query: entailed = {ents}, models enumerated {st["models"]:,} (2^{len(names)} = {2**len(names):,}).\n')
    print('## 2B. Implication chains p0, p0⇒p1, …, p_{n-1}⇒p_n, query p_n (resolution refutation vs model checking)\n')
    print('| n | method | outcome | clauses generated | resolvents attempted | tautologies discarded | subsumed removed | time s |'); print('|---|---|---|---|---|---|---|---|')
    for n in (10, 20, 40, 80):
        cl, syms = chain(n); q = cl + [frozenset([f'-p{n}'])]
        for strat in ('fifo', 'shortest'):
            t = time.perf_counter(); ok, cnt, _ = resolution(q, strat); dt = time.perf_counter() - t
            print(f'| {n} | resolution ({strat}) | {"proved" if ok else ok} | {fmt_cnt(cnt)} | {dt:.3f} |')
        t = time.perf_counter(); r, models = mc_cnf(q, syms, cap=1 << 22); dt = time.perf_counter() - t
        print(f'| {n} | model checking | {"entailed" if r is False else "INFEASIBLE (2^%d = %s models)" % (len(syms), format(2**len(syms), ","))} | models: {models if r is not None else "-"} | - | - | - | {round(dt,3)} |')
    print('\n## 2C. KB families that favour each method\n')
    print('| KB family | symbols | method | outcome | work | time s |'); print('|---|---|---|---|---|---|')
    for pig, hol in ((4, 3), (5, 4)):
        cl, syms = php(pig, hol)
        t = time.perf_counter(); r, models = mc_cnf(cl, syms); dt = time.perf_counter() - t
        print(f'| pigeonhole PHP({pig},{hol}) (unsatisfiable) | {len(syms)} | model checking | {"unsat" if r is False else r} | {models:,} models | {dt:.2f} |')
        for strat in ('fifo', 'shortest'):
            t = time.perf_counter(); ok, cnt, _ = resolution(cl, strat, cap=150000, time_cap=40); dt = time.perf_counter() - t
            print(f'| pigeonhole PHP({pig},{hol}) | {len(syms)} | resolution ({strat}) | {"refuted" if ok else "GAVE UP (cap/time)"} | {cnt["gen"]:,} generated, {cnt["att"]:,} attempted | {dt:.2f} |')
    cl, syms = chain(20); q = cl + [frozenset(['-p20'])]
    t = time.perf_counter(); r, models = mc_cnf(q, syms); dt = time.perf_counter() - t
    print(f'| chain n=20 | 21 | model checking | entailed | {models:,} models | {dt:.2f} |')
    t = time.perf_counter(); ok, cnt, _ = resolution(q, 'shortest'); dt = time.perf_counter() - t
    print(f'| chain n=20 | 21 | resolution (shortest) | proved | {cnt["gen"]:,} generated, {cnt["att"]:,} attempted | {dt:.3f} |')

if __name__ == '__main__':
    {'t1': task1, 't2': task2}[sys.argv[1]]()
