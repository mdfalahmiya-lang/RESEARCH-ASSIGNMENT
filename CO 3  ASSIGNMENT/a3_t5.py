"""A3 Task 5 - first-order resolution: CNF + Skolemisation, binary resolution using the Task-4 unifier,
strategies (none / unit preference / set of support / both), non-entailed queries under a step cap,
comparison with the propositional prover of Task 2.   Run: python a3_t5.py"""
import itertools, heapq, time
from a3_logic import unify, apply, rename, fmt, fmt_sub, variables, is_var
import a3_prop

TAGS = {'forall', 'exists', 'and', 'or', 'imp', 'not'}
V = lambda x: '?' + x

# ---------------------------------------------------------------- formulas and CNF conversion
def pt(t): return fmt(t) if isinstance(t, tuple) else str(t)
def pf(f):
    t = f[0]
    if t == 'forall': return f'∀{f[1][1:]} ' + pf(f[2])
    if t == 'exists': return f'∃{f[1][1:]} ' + pf(f[2])
    if t == 'not': return '¬' + pf(f[1])
    if t == 'imp': return '(' + pf(f[1]) + ' ⇒ ' + pf(f[2]) + ')'
    if t in ('and', 'or'): return '(' + (' ∧ ' if t == 'and' else ' ∨ ').join(pf(x) for x in f[1:]) + ')'
    return fmt(f)

def elim(f):
    t = f[0]
    if t == 'imp': return ('or', ('not', elim(f[1])), elim(f[2]))
    if t in ('and', 'or', 'not'): return (t,) + tuple(elim(x) for x in f[1:])
    if t in ('forall', 'exists'): return (t, f[1], elim(f[2]))
    return f

def nnf(f, neg=False):
    t = f[0]
    if t == 'not': return nnf(f[1], not neg)
    if t in ('and', 'or'): return ({'and': 'or', 'or': 'and'}[t] if neg else t,) + tuple(nnf(x, neg) for x in f[1:])
    if t in ('forall', 'exists'): return ({'forall': 'exists', 'exists': 'forall'}[t] if neg else t, f[1], nnf(f[2], neg))
    return ('not', f) if neg else f

_c = itertools.count(1)
def mapt(t, env):
    if isinstance(t, tuple): return (t[0],) + tuple(mapt(a, env) for a in t[1:])
    return env.get(t, t)
def stdz(f, env):
    t = f[0]
    if t in ('forall', 'exists'):
        nv = f'{f[1]}{next(_c)}'; e2 = dict(env); e2[f[1]] = nv; return (t, nv, stdz(f[2], e2))
    if t in ('and', 'or', 'not'): return (t,) + tuple(stdz(x, env) for x in f[1:])
    return mapt(f, env)
def subst_f(f, env):
    t = f[0]
    if t in ('forall', 'exists'): return (t, f[1], subst_f(f[2], env))
    if t in ('and', 'or', 'not'): return (t,) + tuple(subst_f(x, env) for x in f[1:])
    return mapt(f, env)

_sk = itertools.count(1)
def skolem(f, univ, log):
    t = f[0]
    if t == 'forall': return ('forall', f[1], skolem(f[2], univ + [f[1]], log))
    if t == 'exists':
        name = f'Sk{next(_sk)}'; term = name if not univ else (name,) + tuple(univ)
        log.append(f'∃{f[1][1:]} is replaced by {"the Skolem CONSTANT " + name + " (no universal quantifier encloses it)" if not univ else "the Skolem FUNCTION " + pt(term) + " (depends on the enclosing universals " + ", ".join(u[1:] for u in univ) + ")"}')
        return skolem(subst_f(f[2], {f[1]: term}), univ, log)
    if t in ('and', 'or', 'not'): return (t,) + tuple(skolem(x, univ, log) for x in f[1:])
    return f

def drop_forall(f): return drop_forall(f[2]) if f[0] == 'forall' else ((f[0],) + tuple(drop_forall(x) for x in f[1:]) if f[0] in ('and', 'or', 'not') else f)

def to_clauses(f):
    t = f[0]
    if t == 'and': return [c for x in f[1:] for c in to_clauses(x)]
    if t == 'or':
        res = [[]]
        for x in f[1:]: cs = to_clauses(x); res = [r + c for r in res for c in cs]
        return res
    if t == 'not': return [[(False, f[1])]]
    return [[(True, f)]]

def cnf_with_log(name, f):
    log = []; a = elim(f); b = nnf(a); c = stdz(b, {}); d = skolem(c, [], log); e = drop_forall(d); cl = to_clauses(e)
    print(f'**{name}**\n\n1. original: `{pf(f)}`\n2. eliminate ⇒: `{pf(a)}`\n3. move ¬ inward: `{pf(b)}`\n4. standardise variables apart: `{pf(c)}`\n5. Skolemise: `{pf(d)}`' + ''.join(f'  — {l}' for l in log) + f'\n6. drop ∀ and distribute ∨ over ∧: `{pf(e)}`\n7. clauses: ' + ' ; '.join('{' + ', '.join(('' if s else '¬') + fmt(a) for s, a in c) + '}' for c in cl) + '\n')
    return cl

def showc(c): return '{' + ', '.join(('' if s else '¬') + fmt(a) for s, a in c) + '}' if c else '[] (empty clause)'

# ---------------------------------------------------------------- resolution
def canon(c):
    m = {}
    def go(t):
        if is_var(t): return m.setdefault(t, f'_{len(m)}')
        if isinstance(t, tuple): return (t[0],) + tuple(go(a) for a in t[1:])
        return t
    return tuple(sorted(((s, go(a)) for s, a in c), key=repr))

def is_taut(c): return any(s1 != s2 and a1 == a2 for (s1, a1), (s2, a2) in itertools.combinations(c, 2))

def resolve_clauses(c, d, cnt):
    """All binary resolvents of c and d (d renamed apart)."""
    atoms = [a for _, a in d]; ren = rename([a for _, a in d] + [a for _, a in c], tag=next(_c))
    d2 = [(s, ren[i]) for i, (s, _) in enumerate(d)]; c2 = [(s, ren[len(d) + i]) for i, (s, _) in enumerate(c)]
    out = []
    for i, (s1, a1) in enumerate(c2):
        for j, (s2, a2) in enumerate(d2):
            if s1 != s2 and a1[0] == a2[0] and len(a1) == len(a2):
                th = unify(a1, a2, None, True, cnt)
                if th is None: continue
                cnt['steps'] += 1
                r = [(s, apply(a, th)) for k, (s, a) in enumerate(c2) if k != i] + [(s, apply(a, th)) for k, (s, a) in enumerate(d2) if k != j]
                seen = []; [seen.append(l) for l in r if l not in seen]
                out.append((seen, th))
    return out

def prove(kb_clauses, query_clauses, strategy='none', max_gen=5000, tcap=12.0):
    """strategy: 'none' | 'unit' | 'sos' | 'sos+unit'.  Returns (outcome, counters, proof_steps)."""
    cnt = dict(gen=0, steps=0, unif=0, given=0); t0 = time.perf_counter()
    sos_only = strategy.startswith('sos'); unit_pref = strategy.endswith('unit') or strategy == 'unit'
    usable, queue, seen, parent, ctr = [], [], set(), {}, itertools.count()
    def push(c, par=None):
        k = canon(c)
        if k in seen: return False
        seen.add(k); parent[k] = par
        heapq.heappush(queue, (len(c) if unit_pref else 0, next(ctr), c)); return True
    if sos_only:
        for c in kb_clauses: seen.add(canon(c)); parent[canon(c)] = None; usable.append(c)
        for c in query_clauses: push(c)
    else:
        for c in kb_clauses + query_clauses: push(c)
    while queue:
        _, _, g = heapq.heappop(queue); cnt['given'] += 1
        if not g:
            return 'PROVED', cnt, parent, time.perf_counter() - t0
        for d in list(usable):
            for r, th in resolve_clauses(g, d, cnt):
                if is_taut(r): continue
                k = canon(r)
                if k in seen: continue
                cnt['gen'] += 1
                if push(r, (canon(g), canon(d), th)) and not r: return 'PROVED', cnt, parent, time.perf_counter() - t0
                if cnt['gen'] >= max_gen or time.perf_counter() - t0 > tcap: return 'CAP HIT (gave up)', cnt, parent, time.perf_counter() - t0
        usable.append(g)
    return 'SATURATED (no proof exists)', cnt, parent, time.perf_counter() - t0

def proof_steps(parent):
    """Collect the derivation of the empty clause as an ordered list."""
    out, seen = [], set()
    def go(k):
        p = parent.get(k)
        if p is None or k in seen: return
        seen.add(k); go(p[0]); go(p[1]); out.append((k, p))
    go(())
    return out

def kshow(k): return '{' + ', '.join(('' if s else '¬') + fmt(a) for s, a in k) + '}' if k else '[] (empty clause)'

# ---------------------------------------------------------------- the four statements
def statements():
    e, d = V('e'), V('d')
    S1 = ('forall', e, ('forall', d, ('imp', ('and', ('Employee', e), ('Document', d), ('Restricted', d), ('Handled', e, d)), ('Authorised', e))))
    S2 = ('forall', d, ('imp', ('and', ('Document', d), ('ContainsPatientData', d)), ('Restricted', d)))
    S3 = ('exists', e, ('and', ('Employee', e), ('forall', d, ('imp', ('and', ('Document', d), ('Audited', d)), ('Handled', e, d)))))
    S4 = ('and', ('Document', 'R1'), ('ContainsPatientData', 'R1'), ('Audited', 'R1'))
    return [('S1 every employee who handled a restricted document is authorised', S1), ('S2 every document containing patient data is restricted', S2),
            ('S3 some employee handled every audited document', S3), ('S4 R1 contains patient data and R1 was audited', S4)]

def ground(clauses, consts):
    out = []
    for c in clauses:
        vs = sorted(set().union(*[variables(a) for _, a in c])) if c else []
        for tup in itertools.product(consts, repeat=len(vs)):
            th = dict(zip(vs, tup))
            out.append(frozenset(('' if s else '-') + '_'.join(str(x) for x in flat(apply(a, th))) for s, a in c))
    return list(set(out))
def flat(a):
    r = []
    for x in a:
        r += flat(x) if isinstance(x, tuple) else [x]
    return r

if __name__ == '__main__':
    print('## 5A. Conversion to CNF with Skolemisation (every step)\n')
    kb = []
    for name, f in statements(): kb += cnf_with_log(name, f)
    q = [[(False, ('Authorised', V('x')))]]
    print('**Negated query** (query: ∃x Authorised(x)); its negation ∀x ¬Authorised(x) gives the clause {¬Authorised(x)}.\n')
    print('KB clauses:', ' ; '.join(showc(c) for c in kb), '\n')
    print('## 5B. Proof that an authorised employee exists (strategy: set of support + unit preference)\n')
    res, cnt, par, dt = prove(kb, q, 'sos+unit')
    print(f'Result: **{res}**; proof steps (resolution steps in the proof tree): {len(proof_steps(par))}\n\n```')
    for k, (a, b, th) in proof_steps(par): print(f'{kshow(k):55s} <- resolve {kshow(a)}  with  {kshow(b)}   θ = {fmt_sub(th)}')
    print('```\n')
    print('## 5C. Strategy comparison on the same query (kb clauses = %d)\n' % len(kb))
    print('| strategy | outcome | clauses generated | successful resolution steps | unification attempts | given clauses processed | proof length | time ms |'); print('|---|---|---|---|---|---|---|---|')
    for st in ('none', 'unit', 'sos', 'sos+unit'):
        r, c, p, dt = prove(kb, q, st)
        print(f"| {st} | {r} | {c['gen']} | {c['steps']} | {c['unif']} | {c['given']} | {len(proof_steps(p)) if r == 'PROVED' else '-'} | {1000*dt:.1f} |")
    print('\n## 5D. A second query that is NOT entailed: ∃x (Authorised(x) ∧ Audited(x))  (clause {¬Authorised(x), ¬Audited(x)})\n')
    q2 = [[(False, ('Authorised', V('x'))), (False, ('Audited', V('x')))]]
    print('| KB | strategy | outcome | generated | steps | unification attempts | given |'); print('|---|---|---|---|---|---|---|')
    for st in ('none', 'sos'):
        r, c, p, dt = prove(kb, q2, st, 3000); print(f"| original (function-free apart from Skolem constant) | {st} | {r} | {c['gen']} | {c['steps']} | {c['unif']} | {c['given']} |")
    mgr = [[(False, ('Employee', V('m'))), (True, ('Employee', ('Mgr', V('m'))))]]
    for st in ('none', 'sos'):
        r, c, p, dt = prove(kb + mgr, q2, st, 800); print(f"| + axiom Employee(m) ⇒ Employee(Mgr(m)) (a function symbol) | {st} | {r} | {c['gen']} | {c['steps']} | {c['unif']} | {c['given']} |")
    r, c, p, dt = prove(kb + mgr, q, 'sos+unit'); print(f"| + Mgr axiom, ENTAILED query of 5B | sos+unit | {r} | {c['gen']} | {c['steps']} | {c['unif']} | {c['given']} |")
    print('\n## 5E. Comparison with the propositional prover of Task 2 on the equivalent small domain {Sk1, R1}\n')
    gk = ground(kb, ['Sk1', 'R1']) + ground(q, ['Sk1', 'R1'])
    atoms = {l.lstrip('-') for c in gk for l in c}
    t = time.perf_counter(); ok, cn, _ = a3_prop.resolution([frozenset(c) for c in gk], 'shortest'); dp = time.perf_counter() - t
    print(f'Grounding over 2 constants gives {len(gk)} distinct ground clauses over {len(atoms)} atoms (vs {len(kb)+len(q)} first-order clauses).')
    print(f'Propositional resolution (shortest-first): proved = {ok}; clauses generated {cn["gen"]}, resolvents attempted {cn["att"]}, subsumed {cn["sub"]}, time {1000*dp:.1f} ms.')
    r, c, p, dt = prove(kb, q, 'sos+unit')
    print(f'First-order resolution (sos+unit): proved = {r == "PROVED"}; clauses generated {c["gen"]}, resolution steps {c["steps"]}, unification attempts {c["unif"]}, time {1000*dt:.1f} ms.')
    gk3 = ground(kb, ['Sk1', 'R1', 'R2', 'R3']) + ground(q, ['Sk1', 'R1', 'R2', 'R3'])
    ok3, cn3, _ = a3_prop.resolution([frozenset(c) for c in gk3], 'shortest')
    print(f'With 4 constants the propositional KB has {len(gk3)} ground clauses and needs {cn3["gen"]} clauses generated / {cn3["att"]} attempts; the first-order proof is unchanged ({c["gen"]} generated).')
