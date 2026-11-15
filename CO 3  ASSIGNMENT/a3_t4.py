"""A3 Task 4 - unification, lifted inference and propositionalisation.  Run: python a3_t4.py"""
import itertools, time, math
from a3_logic import unify, compose, apply, rename, fmt, fmt_sub, KB, variables, _unify

V = lambda x: '?' + x

def lifted_modus_ponens(rule, atoms):
    """rule = (body list, head); atoms = known atoms. Standardise the rule apart, unify each body literal with some atom
    (one substitution threaded through) and return head(theta) for every way of doing so."""
    ren = rename(list(rule[0]) + [rule[1]]); body, head = ren[:-1], ren[-1]
    out = []
    def go(i, th):
        if i == len(body): out.append(apply(head, th)); return
        for a in atoms:
            t2 = unify(body[i], a, th, True)
            if t2 is not None: go(i + 1, t2)
    go(0, {})
    return out

def ground_clauses(rules, consts):
    """Propositionalisation: instantiate every universal rule with every tuple of constants."""
    n = 0
    for body, head in rules:
        vs = sorted(set().union(*[variables(t) for t in body + [head]]))
        for tup in itertools.product(consts, repeat=len(vs)): n += 1
    return n

def terms_upto(consts, funcs, d):
    """Number of ground terms of depth <= d. funcs = {name: arity}."""
    cur = set(consts)
    for _ in range(d):
        new = set(cur)
        for f, ar in funcs.items():
            for args in itertools.product(sorted(cur, key=str), repeat=ar): new.add((f,) + args)
        cur = new
    return len(cur)

if __name__ == '__main__':
    print('## 4A. Most general unifiers (five designed pairs; hand derivation in the report, computed here as a check)\n')
    cases = [
        ('1 plain', ('P', V('x'), ('F', V('y'))), ('P', 'A', ('F', 'B')), True),
        ('2 variable bound to a term containing a variable', ('Knows', 'John', V('x')), ('Knows', V('y'), ('Mother', V('y'))), True),
        ('3 occurs check matters: P(x) vs P(F(x))', ('P', V('x')), ('P', ('F', V('x'))), True),
        ('3b same pair WITHOUT occurs check', ('P', V('x')), ('P', ('F', V('x'))), False),
        ('4 standardising apart is essential: Knows(John,x) vs Knows(x,Elizabeth)', ('Knows', 'John', V('x')), ('Knows', V('x'), 'Elizabeth'), True),
        ('4b after renaming x -> x1 in the second atom', ('Knows', 'John', V('x')), ('Knows', V('x1'), 'Elizabeth'), True),
        ('5 composition: Q(F(x),y,G(y)) vs Q(F(z),H(z),G(H(w)))', ('Q', ('F', V('x')), V('y'), ('G', V('y'))), ('Q', ('F', V('z')), V('y2' if False else 'y'), ('G', ('H', V('w')))), True)]
    cases[-1] = ('5 composition: Q(F(x),y,G(y)) vs Q(F(z),H(z),G(H(w)))', ('Q', ('F', V('x')), V('y'), ('G', V('y'))), ('Q', ('F', V('z')), ('H', V('z')), ('G', ('H', V('w')))), True)
    print('| pair | unifier |\n|---|---|')
    for name, a, b, occ in cases:
        if occ: res = fmt_sub(unify(a, b, None, True))
        else: res = '(no occurs check) ' + ('ACCEPTED: x would be bound to F(x), an infinite term (wrong)' if _unify(a, b, {}, False) is not None else 'FAIL')
        print(f'| {name}: `{fmt(a)}` ~ `{fmt(b)}` | {res} |')
    print('\nSubstitution composition check: s1 = {x/F(y), y/z}, s2 = {y/A, z/B}: compose(s1,s2) =', fmt_sub(compose({V('x'): ('F', V('y')), V('y'): V('z')}, {V('y'): 'A', V('z'): 'B'})),
          '; apply(apply(x,s1),s2) =', fmt(apply(apply(V('x'), {V('x'): ('F', V('y')), V('y'): V('z')}), {V('y'): 'A', V('z'): 'B'})))
    print('\nWhich of my test pairs gives a WRONG answer if the occurs check is removed? Pair 3 (P(x) ~ P(F(x))): it is wrongly "unified"; all other pairs behave identically.')
    print('\n### Lifted Modus Ponens demonstration\n')
    rule = ([('King', V('x')), ('Greedy', V('x'))], ('Evil', V('x')))
    atoms = [('King', 'John'), ('Greedy', V('y')), ('King', 'Richard')]
    print('rule  King(x) ∧ Greedy(x) ⇒ Evil(x);  atoms: King(John), Greedy(y), King(Richard)  ⊢ ', [fmt(a) for a in lifted_modus_ponens(rule, atoms)], '  (first: θ = {x/John, y/John}; second: θ = {x/Richard, y/Richard} because Greedy(y) with a free y says everybody is greedy)')
    print('\n## 4B. Ground-clause growth (propositionalisation)\n')
    rules_by_vars = {1: ([('P', V('x'))], ('Q', V('x'))),
                     2: ([('P', V('x')), ('R', V('x'), V('y'))], ('S', V('x'), V('y'))),
                     3: ([('R', V('x'), V('y')), ('R', V('y'), V('z'))], ('T', V('x'), V('z'))),
                     4: ([('R', V('x'), V('y')), ('R', V('z'), V('w'))], ('U', V('x'), V('y'), V('z'), V('w')))}
    print('Ground instances of ONE rule with v variables over k constants (counted by generating them for k ≤ 12 or v ≤ 3; formula k^v beyond):\n')
    print('| k | v=1 | v=2 | v=3 | v=4 | predicate arity a=1 ground atoms | a=2 | a=3 | a=4 |'); print('|---|---|---|---|---|---|---|---|---|')
    for k in (3, 5, 10, 20, 30):
        consts = [f'c{i}' for i in range(k)]; row = []
        for v in (1, 2, 3, 4):
            if v <= 3 or k <= 12: cnt = ground_clauses([rules_by_vars[v]], consts)
            else: cnt = k ** v
            assert cnt == k ** v; row.append(f'{cnt:,}')
        print(f'| {k} | ' + ' | '.join(row) + ' | ' + ' | '.join(f'{k**a:,}' for a in (1, 2, 3, 4)) + ' |')
    print('\nWith function symbols the number of ground terms is infinite; with a depth bound d (k constants):\n')
    print('| depth bound d | 1 constant + unary F | 2 constants + unary F | 2 constants + binary G (counted) | binary recurrence T(d) = 2 + T(d-1)² |'); print('|---|---|---|---|---|')
    T = 2
    for d in range(0, 5):
        if d > 0: T = 2 + T * T
        cnt = terms_upto(['A', 'B'], {'G': 2}, d) if d <= 3 else 'not generated (too many)'
        print(f'| {d} | {terms_upto(["A"], {"F": 1}, d)} | {terms_upto(["A","B"], {"F": 1}, d)} | {cnt if d <= 3 else cnt} | {T:,} |')
    print('\n## 4C. Lifted vs propositional inference on the same query (Path(c1, ck) over a chain of k nodes)\n')
    print('KB: Edge(ci,ci+1) for i<k; Path(x,y) ⇐ Edge(x,y);  Path(x,z) ⇐ Edge(x,y) ∧ Path(y,z).\n')
    print('| k | lifted: unifications (no index) | lifted: unifications (indexed) | lifted time ms (indexed) | propositional: ground clauses | prop: rule checks to fixed point | prop: rule firings | prop time ms (grounding + inference) | both derive Path(c1,ck) |')
    print('|---|---|---|---|---|---|---|---|---|')
    for k in (5, 10, 20, 30):
        cs = [f'c{i}' for i in range(1, k + 1)]; edges = [('Edge', cs[i], cs[i + 1]) for i in range(k - 1)]
        res = {}
        for idx in (False, True):
            kb = KB(index=idx)
            for e in edges: kb.add_fact(e)
            kb.add_rule(('Path', V('x'), V('y')), [('Edge', V('x'), V('y'))])
            kb.add_rule(('Path', V('x'), V('z')), [('Edge', V('x'), V('y')), ('Path', V('y'), V('z'))])
            t = time.perf_counter(); ans, st = kb.ask(('Path', cs[0], cs[-1]), max_depth=500); res[idx] = (len(ans) > 0, st['unif'], 1000 * (time.perf_counter() - t))
        t = time.perf_counter()
        gr = []
        for x in cs:
            for y in cs: gr.append(([('Edge', x, y)], ('Path', x, y)))
        for x in cs:
            for y in cs:
                for z in cs: gr.append(([('Edge', x, y), ('Path', y, z)], ('Path', x, z)))
        known = set(edges); checks = fires = 0; changed = True
        while changed:
            changed = False
            for body, head in gr:
                checks += 1
                if head not in known and all(b in known for b in body): known.add(head); fires += 1; changed = True
        tp = 1000 * (time.perf_counter() - t)
        print(f'| {k} | {res[False][1]:,} | {res[True][1]:,} | {res[True][2]:.1f} | {len(gr):,} | {checks:,} | {fires} | {tp:.1f} | {res[True][0] and (("Path", cs[0], cs[-1]) in known)} |')
