"""A3 Task 3 - knowledge engineering for exam eligibility: FOL encoding vs propositional encoding.
Run: python a3_t3.py   Seeds: instance generator seed = 100*s + c, query seed = 5."""
import random, time, itertools
from a3_logic import KB, fmt

V = lambda x: '?' + x

# ---------------- FOL encoding (executable Horn/Datalog form of the regulations) ----------------
def rules_v1():
    s, c, p, r, d, l = V('s'), V('c'), V('p'), V('r'), V('d'), V('l')
    return [(('FeesPaid', s), [('PaidBy', r, s), ('Receipt', r)]),                                    # A5  exists r: receipt paid by s
            (('Barred', s), [('Disciplinary', d, s), ('Active', d)]),                                 # A6  exists d: active case
            (('ApprovedLeave', s, c), [('Leave', l, s, c), ('Approved', l)]),                         # A7  exists l: approved leave covering c
            (('AttOK', s, c), [('Attendance', s, c, 'ok')]),                                          # A3
            (('AttOK', s, c), [('Attendance', s, c, 'short'), ('ApprovedLeave', s, c)]),              # A4  condonation
            (('MissingPrereq', s, c), [('Enrolled', s, c), ('Prereq', p, c), ('not', ('Passed', s, p))]),  # A8  forall p ... as 'no failed p' (s,c bound BEFORE the negation)
            (('PrereqsCleared', s, c), [('not', ('MissingPrereq', s, c))]),                           # A8'
            (('Eligible', s, c), [('Enrolled', s, c), ('AttOK', s, c), ('PrereqsCleared', s, c), ('FeesPaid', s), ('not', ('Barred', s))]),   # A1/A2
            (('HallTicket', s, c), [('Eligible', s, c)])]                                             # A11

def rules_v0():
    """First draft of the KB, kept so the defect log is reproducible: three omissions."""
    s, c, p, r, d, l = V('s'), V('c'), V('p'), V('r'), V('d'), V('l')
    rs = rules_v1()
    rs[2] = (('ApprovedLeave', s, c), [('Leave', l, s, c)])                                            # D2: forgot Approved(l)
    rs[7] = (('Eligible', s, c), [('AttOK', s, c), ('PrereqsCleared', s, c), ('FeesPaid', s)])         # D1: forgot not Barred ; D3: forgot Enrolled
    rs[5] = (('MissingPrereq', s, c), [('Prereq', p, c), ('not', ('Passed', s, p))])                   # D4: negation before s is bound (floundering)
    return rs

def toy_facts():
    F = []
    def student(n, courses, att, paid=True, barred=False, passed=(), leave=None):
        nonlocal F
        for cc in courses: F.append(('Enrolled', n, cc))
        for cc, a in zip(courses, att): F.append(('Attendance', n, cc, a))
        if paid: F += [('Receipt', 'r_' + n), ('PaidBy', 'r_' + n, n)]
        if barred: F += [('Disciplinary', 'd_' + n, n), ('Active', 'd_' + n)]
        for pc in passed: F.append(('Passed', n, pc))
        if leave: F += [('Leave', 'l_' + n, n, leave[0])] + ([('Approved', 'l_' + n)] if leave[1] else [])
    student('ann', ['CS101'], ['ok'])
    student('bob', ['CS101'], ['short'])
    student('cat', ['CS101'], ['short'], leave=('CS101', True))
    student('dan', ['CS101'], ['ok'], paid=False)
    student('eve', ['CS101'], ['ok'], barred=True)
    student('fay', ['CS201'], ['ok'])
    student('hal', ['CS101'], ['short'], leave=('CS101', False))      # leave application still pending
    student('ivy', ['CS201'], ['ok'], passed=['CS101'])
    F += [('Attendance', 'gus', 'MA101', 'ok'), ('Receipt', 'r_gus'), ('PaidBy', 'r_gus', 'gus')]   # gus dropped MA101 (not enrolled)
    F += [('Prereq', 'CS101', 'CS201')]
    return F

QUERIES = [  # (kind, goal, expected)
    ('succeed', ('Eligible', 'ann', 'CS101'), True), ('succeed', ('Eligible', 'cat', 'CS101'), True), ('succeed', ('Eligible', 'ivy', 'CS201'), True),
    ('succeed', ('FeesPaid', 'ann'), True), ('succeed', ('HallTicket', 'ann', 'CS101'), True),
    ('fail', ('Eligible', 'bob', 'CS101'), False), ('fail', ('Eligible', 'dan', 'CS101'), False), ('fail', ('Eligible', 'eve', 'CS101'), False),
    ('fail', ('Eligible', 'fay', 'CS201'), False), ('fail', ('Eligible', 'hal', 'CS101'), False), ('fail', ('Eligible', 'gus', 'MA101'), False),
    ('bindings', ('Eligible', V('s'), 'CS101'), {('ann',), ('cat',)}), ('bindings', ('Barred', V('s')), {('eve',)}),
    ('bindings', ('MissingPrereq', V('s'), V('c')), {('CS201', 'fay')}), ('bindings', ('ApprovedLeave', V('s'), V('c')), {('CS101', 'cat')}),
    ('bindings', ('Eligible', 'ivy', V('c')), {('CS201',)})]

def run_suite(rules, label):
    kb = KB()
    for f in toy_facts(): kb.add_fact(f)
    for h, b in rules: kb.add_rule(h, b)
    bad = []; print(f'\n**Query suite on {label}** (16 queries: 5 succeed, 6 fail, 5 bindings; binding tuples list variables in alphabetical order, e.g. (?c, ?s))\n')
    print('| # | kind | query | expected | actual | ok |'); print('|---|---|---|---|---|---|')
    for i, (kind, g, exp) in enumerate(QUERIES, 1):
        ans, _ = kb.ask(g)
        act = (len(ans) > 0) if kind != 'bindings' else set(ans)
        ok = act == exp; bad.append(not ok)
        fe = lambda x: ('{' + ', '.join(sorted('/'.join(t) for t in x)) + '}') if isinstance(x, set) else str(x)
        print(f'| {i} | {kind} | {fmt(g)} | {fe(exp)} | {fe(act)} | {"✓" if ok else "✗ DEFECT"} |')
    print(f'\n{sum(bad)} of 16 queries wrong.')
    return bad

# ---------------- generators for scaling ----------------
def make_instance(s, c, seed):
    rnd = random.Random(seed); F = []; prereq = {}
    for j in range(c):
        prereq[j] = [rnd.randrange(j) for _ in range(rnd.choice([0, 1, 2]))] if j > 0 else []
        for p in set(prereq[j]): F.append(('Prereq', f'c{p}', f'c{j}'))
    info = {}
    for i in range(s):
        F += [('Receipt', f'r{i}'), ('PaidBy', f'r{i}', f's{i}')] if rnd.random() < .9 else []
        if rnd.random() < .05: F += [('Disciplinary', f'd{i}', f's{i}'), ('Active', f'd{i}')]
        for j in range(c):
            if rnd.random() < .8: F.append(('Passed', f's{i}', f'c{j}'))
            if rnd.random() < .5:
                F.append(('Enrolled', f's{i}', f'c{j}')); short = rnd.random() < .15
                F.append(('Attendance', f's{i}', f'c{j}', 'short' if short else 'ok'))
                if short and rnd.random() < .5:
                    F.append(('Leave', f'l{i}_{j}', f's{i}', f'c{j}'))
                    if rnd.random() < .6: F.append(('Approved', f'l{i}_{j}'))
    return F, prereq

def ground_prop(F, s, c, prereq):
    """Propositional encoding: one set of Horn rules per student and course (atoms are strings)."""
    fs = set(F); atoms = lambda *a: '_'.join(a)
    facts = set(); rules = []
    for f in F:
        if f[0] == 'Enrolled': facts.add(atoms('En', f[1], f[2]))
        elif f[0] == 'Attendance': facts.add(atoms('Att' + f[3], f[1], f[2]))
        elif f[0] == 'Passed': facts.add(atoms('Passed', f[1], f[2]))
    paid = {f[2] for f in F if f[0] == 'PaidBy'}; bar = {f[2] for f in F if f[0] == 'Disciplinary'}
    appr = {f[1] for f in F if f[0] == 'Approved'}
    for f in F:
        if f[0] == 'Leave' and f[1] in appr: facts.add(atoms('Leave', f[2], f[3]))
    for i in range(s):
        if f's{i}' in paid: facts.add(atoms('Fees', f's{i}'))
        if f's{i}' not in bar: facts.add(atoms('NoDisc', f's{i}'))
        for j in range(c):
            S_, C_ = f's{i}', f'c{j}'
            rules.append((atoms('AttOK', S_, C_), [atoms('Attok', S_, C_)]))
            rules.append((atoms('AttOK', S_, C_), [atoms('Attshort', S_, C_), atoms('Leave', S_, C_)]))
            rules.append((atoms('PrereqsOK', S_, C_), [atoms('Passed', S_, f'c{p}') for p in sorted(set(prereq[j]))]))
            rules.append((atoms('Elig', S_, C_), [atoms('En', S_, C_), atoms('AttOK', S_, C_), atoms('PrereqsOK', S_, C_), atoms('Fees', S_), atoms('NoDisc', S_)]))
            rules.append((atoms('Hall', S_, C_), [atoms('Elig', S_, C_)]))
    return facts, rules

def prop_ask(goal, facts, byhead, st):
    st['calls'] = st.get('calls', 0) + 1
    if goal in facts: return True
    for body in byhead.get(goal, ()):
        st['rules'] = st.get('rules', 0) + 1
        if all(prop_ask(b, facts, byhead, st) for b in body): return True
    return False

if __name__ == '__main__':
    print('## 3A. Defect log: query suite on draft v0 and on corrected v1\n')
    bad0 = run_suite(rules_v0(), 'KB v0 (first draft)')
    bad1 = run_suite(rules_v1(), 'KB v1 (after fixes)')
    print('\nDefects found by v0 (queries 8, 10, 11, 12, 14, 15) and their fixes:\n')
    print('1. Query 8 `Eligible(eve,CS101)` succeeded: the Eligible rule had no `not Barred(s)` condition → added.')
    print('2. Query 10 `Eligible(hal,CS101)` succeeded: ApprovedLeave ignored `Approved(l)`, so a pending leave condoned short attendance → added `Approved(l)` to the rule body.')
    print('3. Query 11 `Eligible(gus,MA101)` succeeded: a student with an attendance record but no `Enrolled` fact was eligible → added `Enrolled(s,c)` to the Eligible rule.')
    print('4. Query 14 `MissingPrereq(?s,?c)` returned no answers although fay lacks CS101: the negated literal `not Passed(s,p)` was evaluated while ?s was still unbound (negation as failure needs bound variables, "floundering"): Passed(?s,CS101) succeeds for ivy, so the negation failed for every s. Fix: put `Enrolled(s,c)` before the negation so s and c are bound.')
    print('(Queries 12 and 15 failed in v0 as symptoms of defects 1-3.)')
    print('\n## 3B. KB size and inference cost as students s and courses c grow (s = c)\n')
    print('| s = c | pairs s·c | propositional sentences (rules + facts) | FOL sentences (axioms + facts) | prop. rules only | FOL rules only | build time prop ms | build time FOL ms | 200 queries: prop ms | 200 queries: FOL ms | prop steps/query | FOL unifications/query | answers agree | break-even number of queries |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for n in (2, 5, 10, 20, 40, 80):
        F, prereq = make_instance(n, n, 100 * n + n)
        t = time.perf_counter(); facts, rules = ground_prop(F, n, n, prereq); byhead = {}
        for h, b in rules: byhead.setdefault(h, []).append(b)
        tb_p = 1000 * (time.perf_counter() - t)
        t = time.perf_counter(); kb = KB()
        for f in F: kb.add_fact(f)
        for h, b in rules_v1(): kb.add_rule(h, b)
        kb.finalize(); tb_f = 1000 * (time.perf_counter() - t)
        rnd = random.Random(5); qs = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(200)]
        st = {}; t = time.perf_counter(); pa = [prop_ask(f'Elig_s{i}_c{j}', facts, byhead, st) for i, j in qs]; tp = 1000 * (time.perf_counter() - t)
        fa = []; unif = 0; t = time.perf_counter()
        for i, j in qs:
            ans, s2 = kb.ask(('Eligible', f's{i}', f'c{j}')); fa.append(len(ans) > 0); unif += s2['unif']
        tf = 1000 * (time.perf_counter() - t)
        print(f'| {n} | {n*n} | {len(rules)+len(facts)} | {len(F)+len(rules_v1())} | {len(rules)} | {len(rules_v1())} | {tb_p:.1f} | {tb_f:.1f} | {tp:.1f} | {tf:.1f} | {(st["calls"])/200:.1f} | {unif/200:.1f} | {pa == fa} | {((tb_p - tb_f) / ((tf - tp) / 200)) if tb_p > tb_f else 0:.0f} |')
