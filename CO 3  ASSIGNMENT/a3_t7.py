"""A3 Task 7 - hospital medication-safety advisor (ILLUSTRATIVE ONLY, not clinical advice).
Design: Datalog (function-free FOL Horn clauses) + indexed backward chaining + rule-based explanations.
KB sizes 40 / 400 / 2000 rules, 50,000 patients, 31 hand-built test cases with expected answers,
oracle cross-check on 300 random queries per size, baselines: rules-unindexed BC, fully unindexed BC, per-query forward chaining.
Run: python a3_t7.py   Seeds: rules 77, patients 5, random queries 11."""
import random, time, tracemalloc, statistics, sys
from a3_logic import KB, fmt
import a3_t6

NAMED_DRUGS = ['warfarin', 'aspirin', 'ibuprofen', 'amoxicillin', 'sertraline', 'tramadol', 'metformin', 'lisinopril']
NAMED_AL = ['penicillin_allergy', 'salicylate_allergy', 'nsaid_allergy']
NAMED_CO = ['renal_failure', 'peptic_ulcer', 'bleeding_disorder', 'pregnancy', 'epilepsy', 'bipolar', 'liver_disease']
A = lambda a: ('Allergy', '?p', a); T = lambda d: ('Takes', '?p', d); C = lambda c: ('HasCondition', '?p', c); G = lambda b: ('Age', '?p', b)

def base_rules():
    R = []
    def add(kind, drug, body, tag): R.append((f'{kind}:{drug}:{tag}', drug, body))
    for d, a in [('amoxicillin', 'penicillin_allergy'), ('aspirin', 'salicylate_allergy'), ('ibuprofen', 'nsaid_allergy'), ('aspirin', 'nsaid_allergy')]: add('allergy', d, [A(a)], a)
    for d, t in [('aspirin', 'warfarin'), ('warfarin', 'aspirin'), ('warfarin', 'ibuprofen'), ('ibuprofen', 'warfarin'), ('tramadol', 'sertraline'), ('sertraline', 'tramadol'), ('ibuprofen', 'lisinopril'), ('lisinopril', 'ibuprofen')]: add('interaction', d, [T(t)], t)
    for d, c in [('ibuprofen', 'renal_failure'), ('ibuprofen', 'peptic_ulcer'), ('aspirin', 'peptic_ulcer'), ('aspirin', 'bleeding_disorder'), ('warfarin', 'bleeding_disorder'), ('warfarin', 'pregnancy'), ('lisinopril', 'pregnancy'), ('metformin', 'renal_failure'), ('tramadol', 'epilepsy'), ('sertraline', 'bipolar')]: add('condition', d, [C(c)], c)
    for d, b in [('aspirin', 'child'), ('tramadol', 'child'), ('tramadol', 'elderly'), ('ibuprofen', 'elderly')]: add('age', d, [G(b)], b)
    for d in NAMED_DRUGS: add('duplicate', d, [T(d)], 'same_drug')
    for d, tag, body in [('ibuprofen', 'nephro', [T('lisinopril'), C('renal_failure')]), ('warfarin', 'bleed_elderly', [T('aspirin'), G('elderly')]),
                         ('tramadol', 'seizure', [T('sertraline'), C('epilepsy')]), ('metformin', 'lactic', [T('lisinopril'), C('renal_failure')]),
                         ('aspirin', 'bleed_elderly', [T('warfarin'), G('elderly')]), ('amoxicillin', 'inr_liver', [T('warfarin'), C('liver_disease')])]: add('combo', d, body, tag)
    assert len(R) == 40
    return R

def pools(n_syn_drugs):
    drugs = [f'D{k:04d}' for k in range(1, n_syn_drugs + 1)]
    return drugs, NAMED_AL + [f'AL{k:03d}' for k in range(1, n_syn_drugs // 2 + 3)], NAMED_CO + [f'CO{k:03d}' for k in range(1, n_syn_drugs // 2 + 3)]

def synth_rules(n_extra, seed=77):
    """SYNTHETIC drugs D0001.. (no medical content) only to scale the rule count; their heads never involve the 8 named drugs."""
    rnd = random.Random(seed); ns = max(1, n_extra // 10); sd, al, co = pools(ns); alld = NAMED_DRUGS + sd
    types = ['allergy', 'allergy', 'interaction', 'interaction', 'interaction', 'condition', 'condition', 'age', 'duplicate', 'combo']
    R, seen, j = [], set(), 0
    while len(R) < n_extra:
        d = sd[(j // 10) % ns]; t = types[j % 10]; j += 1
        if t == 'allergy': a = rnd.choice(al); body, tag = [A(a)], a
        elif t == 'interaction': x = rnd.choice(alld); body, tag = [T(x)], x
        elif t == 'condition': c = rnd.choice(co); body, tag = [C(c)], c
        elif t == 'age': b = rnd.choice(['child', 'elderly']); body, tag = [G(b)], b
        elif t == 'duplicate': body, tag = [T(d)], 'same_drug'
        else: x, c = rnd.choice(alld), rnd.choice(co); body, tag = [T(x), C(c)], f'{x}_{c}'
        rid = f'{t}:{d}:{tag}'
        if rid in seen: continue
        seen.add(rid); R.append((rid, d, body))
    return R

def gen_patients(P, seed=5):
    rnd = random.Random(seed); sd, al, co = pools(196); alld = NAMED_DRUGS + sd; recs = {}; facts = []
    for i in range(P):
        p = f'P{i}'; age = rnd.choices(['child', 'adult', 'elderly'], [.1, .65, .25])[0]
        rec = dict(age=age, al=set(), takes=set(), co=set()); facts.append(('Age', p, age))
        if rnd.random() < .3: a = rnd.choice(NAMED_AL if rnd.random() < .5 else al); rec['al'].add(a)
        for _ in range(rnd.choice([0, 1, 2, 2, 3, 3, 4])): rec['takes'].add(rnd.choice(NAMED_DRUGS if rnd.random() < .5 else alld))
        for _ in range(rnd.choice([0, 0, 1, 1, 2])): rec['co'].add(rnd.choice(NAMED_CO if rnd.random() < .5 else co))
        for a in rec['al']: facts.append(('Allergy', p, a))
        for d in rec['takes']: facts.append(('Takes', p, d))
        for c in rec['co']: facts.append(('HasCondition', p, c))
        recs[p] = rec
    return recs, facts

# ---- hand-built test cases: (name, record, new drug, expected reason set, expected verdict)
def rec(age='adult', al=(), takes=(), co=()): return dict(age=age, al=set(al), takes=set(takes), co=set(co))
CASES = [
 ('D01 warfarin + new aspirin', rec(takes=['warfarin']), 'aspirin', {'interaction:aspirin:warfarin'}),
 ('D02 sertraline + new tramadol', rec(takes=['sertraline']), 'tramadol', {'interaction:tramadol:sertraline'}),
 ('D03 penicillin allergy + amoxicillin', rec(al=['penicillin_allergy']), 'amoxicillin', {'allergy:amoxicillin:penicillin_allergy'}),
 ('D04 renal failure + ibuprofen', rec(co=['renal_failure']), 'ibuprofen', {'condition:ibuprofen:renal_failure'}),
 ('D05 child + aspirin', rec(age='child'), 'aspirin', {'age:aspirin:child'}),
 ('D06 elderly on warfarin + aspirin', rec(age='elderly', takes=['warfarin']), 'aspirin', {'interaction:aspirin:warfarin', 'combo:aspirin:bleed_elderly'}),
 ('D07 bleeding disorder + warfarin', rec(co=['bleeding_disorder']), 'warfarin', {'condition:warfarin:bleeding_disorder'}),
 ('D08 pregnancy + lisinopril', rec(co=['pregnancy']), 'lisinopril', {'condition:lisinopril:pregnancy'}),
 ('D09 epilepsy + tramadol', rec(co=['epilepsy']), 'tramadol', {'condition:tramadol:epilepsy'}),
 ('D10 already on ibuprofen + ibuprofen', rec(takes=['ibuprofen']), 'ibuprofen', {'duplicate:ibuprofen:same_drug'}),
 ('D11 lisinopril + renal failure + ibuprofen', rec(takes=['lisinopril'], co=['renal_failure']), 'ibuprofen', {'interaction:ibuprofen:lisinopril', 'condition:ibuprofen:renal_failure', 'combo:ibuprofen:nephro'}),
 ('D12 ulcer + warfarin + NSAID allergy + ibuprofen', rec(takes=['warfarin'], co=['peptic_ulcer'], al=['nsaid_allergy']), 'ibuprofen', {'condition:ibuprofen:peptic_ulcer', 'interaction:ibuprofen:warfarin', 'allergy:ibuprofen:nsaid_allergy'}),
 ('S01 healthy adult + metformin', rec(), 'metformin', set()),
 ('S02 on lisinopril + amoxicillin', rec(takes=['lisinopril']), 'amoxicillin', set()),
 ('S03 penicillin allergy + aspirin', rec(al=['penicillin_allergy']), 'aspirin', set()),
 ('S04 on sertraline + metformin', rec(takes=['sertraline']), 'metformin', set()),
 ('S05 elderly + lisinopril', rec(age='elderly'), 'lisinopril', set()),
 ('S06 child + amoxicillin', rec(age='child'), 'amoxicillin', set()),
 ('S07 on aspirin + sertraline', rec(takes=['aspirin']), 'sertraline', set()),
 ('S08 epilepsy + aspirin', rec(co=['epilepsy']), 'aspirin', set()),
 ('S09 on metformin + ibuprofen', rec(takes=['metformin']), 'ibuprofen', set()),
 ('S10 pregnancy + amoxicillin', rec(co=['pregnancy']), 'amoxicillin', set()),
 ('E01 no record at all + aspirin', None, 'aspirin', set()),
 ('E02 elderly on aspirin + warfarin', rec(age='elderly', takes=['aspirin']), 'warfarin', {'interaction:warfarin:aspirin', 'combo:warfarin:bleed_elderly'}),
 ('E03 drug without any rule', rec(takes=['warfarin']), 'drugZ', set()),
 ('E04 NSAID allergy + aspirin', rec(al=['nsaid_allergy']), 'aspirin', {'allergy:aspirin:nsaid_allergy'}),
 ('E05 polypharmacy elderly + ibuprofen', rec(age='elderly', takes=['warfarin', 'aspirin', 'sertraline', 'lisinopril', 'metformin'] + [f'D{k:04d}' for k in range(1, 10)], co=['renal_failure', 'peptic_ulcer', 'epilepsy', 'liver_disease', 'bipolar'], al=['nsaid_allergy']), 'ibuprofen',
  {'allergy:ibuprofen:nsaid_allergy', 'condition:ibuprofen:renal_failure', 'condition:ibuprofen:peptic_ulcer', 'interaction:ibuprofen:warfarin', 'interaction:ibuprofen:lisinopril', 'combo:ibuprofen:nephro', 'age:ibuprofen:elderly'}),
 ('E06 elderly on sertraline + tramadol', rec(age='elderly', takes=['sertraline']), 'tramadol', {'interaction:tramadol:sertraline', 'age:tramadol:elderly'}),
 ('E07 child + tramadol', rec(age='child'), 'tramadol', {'age:tramadol:child'}),
 ('E08 renal failure on lisinopril + metformin', rec(takes=['lisinopril'], co=['renal_failure']), 'metformin', {'condition:metformin:renal_failure', 'combo:metformin:lactic'}),
 ('E09 adult on warfarin + amoxicillin + liver disease', rec(takes=['warfarin'], co=['liver_disease']), 'amoxicillin', {'combo:amoxicillin:inr_liver'}),
]

def verdict_expected(r, d, exp):
    if r is None: return 'INSUFFICIENT DATA'
    if d == 'drugZ': return 'UNKNOWN DRUG'
    return 'UNSAFE' if exp else 'NO KNOWN CONTRAINDICATION'

def build_kb(rules, patient_facts, index=True):
    kb = KB(index=index)
    for f in patient_facts: kb.add_fact(f)
    for rid, d, body in rules: kb.add_rule(('Unsafe', '?p', d, rid), list(body))
    for d in {d for _, d, _ in rules}: kb.add_fact(('Covered', d))
    kb.finalize(); return kb

def advise(kb, p, d):
    st = dict(unif=0, goals=0)
    def q(g):
        ans, s = kb.ask(g); st['unif'] += s['unif']; st['goals'] += s['goals']; return ans
    if not q(('Age', p, '?a')): return 'INSUFFICIENT DATA', set(), st, []
    if not q(('Covered', d)): return 'UNKNOWN DRUG', set(), st, []
    reasons = {a[0] for a in q(('Unsafe', p, d, '?r'))}
    return ('UNSAFE' if reasons else 'NO KNOWN CONTRAINDICATION'), reasons, st, sorted(reasons)

def explain(kb, p, d, rid, table):
    body = table[rid][1]
    lines = [f'Unsafe({p},{d}) because rule {rid} fires:'] + [f'    {fmt(tuple(p if x == "?p" else x for x in a))}  [{"fact in record" if tuple(p if x == "?p" else x for x in a) in kb.facts else "MISSING"}]' for a in body]
    return lines

def oracle(r, d, by_drug):
    return {rid for rid, body in by_drug.get(d, []) if all((a[2] in r['al'] if a[0] == 'Allergy' else a[2] in r['takes'] if a[0] == 'Takes' else a[2] in r['co'] if a[0] == 'HasCondition' else a[2] == r['age']) for a in body)}

if __name__ == '__main__':
    t0 = time.perf_counter(); recs, pfacts = gen_patients(50000)
    print(f'## 7B. Experimental validation. {len(recs):,} patients, {len(pfacts):,} patient facts (seed 5), built in {time.perf_counter()-t0:.1f} s\n')
    summary = []; detail = None
    for S in (40, 400, 2000):
        rules = base_rules() + synth_rules(S - 40); table = {rid: (d, body) for rid, d, body in rules}
        by_drug = {}
        for rid, d, body in rules: by_drug.setdefault(d, []).append((rid, body))
        tracemalloc.start(); tb = time.perf_counter(); kb = build_kb(rules, pfacts); build = time.perf_counter() - tb; cur, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        tp = {}
        for i, (name, r, d, exp) in enumerate(CASES):
            if r is None: continue
            p = f'T{i:02d}'; tp[i] = p
            kb.add_fact(('Age', p, r['age']))
            for a in r['al']: kb.add_fact(('Allergy', p, a))
            for x in r['takes']: kb.add_fact(('Takes', p, x))
            for c in r['co']: kb.add_fact(('HasCondition', p, c))
        rows = []; ok = 0; lat = []; unifs = []; goals = []; exlen = []
        for i, (name, r, d, exp) in enumerate(CASES):
            p = tp.get(i, 'T_NONE'); ve = verdict_expected(r, d, exp)
            verd, reasons, st, rs = advise(kb, p, d)
            good = (verd == ve and reasons == exp); ok += good
            t = time.perf_counter()
            for _ in range(20): advise(kb, p, d)
            lat.append(1000 * (time.perf_counter() - t) / 20); unifs.append(st['unif']); goals.append(st['goals'])
            ex = [explain(kb, p, d, rid, table) for rid in rs]; el = sum(len(x) for x in ex); exlen.append(el)
            rows.append((name, ve, verd, sorted(exp), sorted(reasons), el, good, 1000 * 0 + lat[-1]))
            if S == 2000 and i == 10: sample_expl = ex
        # oracle cross-check on random queries
        rnd = random.Random(11); agree = 0; N = 300; keys = list(recs)
        sd, _, _ = pools(max(1, (S - 40) // 10)); alld = NAMED_DRUGS + sd
        for _ in range(N):
            p = rnd.choice(keys); d = rnd.choice(alld); _, reasons, _, _ = advise(kb, p, d); agree += reasons == oracle(recs[p], d, by_drug) if d in by_drug else reasons == set()
        # baselines
        kb.index_rules = False; lat_b = []; unif_b = []
        for i, (name, r, d, exp) in enumerate(CASES):
            p = tp.get(i, 'T_NONE'); t = time.perf_counter(); _, _, st, _ = advise(kb, p, d); lat_b.append(1000 * (time.perf_counter() - t)); unif_b.append(st['unif'])
        kb.index_facts = False; i = 10; p = tp[i]; t = time.perf_counter(); _, _, st_c, _ = advise(kb, p, CASES[i][2]); lat_c = 1000 * (time.perf_counter() - t)
        kb.index_rules = True; kb.index_facts = True
        rls = [(('Unsafe', '?p', d, rid), list(body)) for rid, d, body in rules]; lat_f = []; fir = []; fc_ok = 0
        for i, (name, r, d, exp) in enumerate(CASES):
            if r is None: continue
            p = tp[i]; pf = [('Age', p, r['age'])] + [('Allergy', p, a) for a in r['al']] + [('Takes', p, x) for x in r['takes']] + [('HasCondition', p, c) for c in r['co']]
            t = time.perf_counter(); known, st, per = a3_t6.forward_chain(pf, rls); lat_f.append(1000 * (time.perf_counter() - t)); fir.append(st['firings'])
            fc_ok += {f[3] for f in known if f[0] == 'Unsafe' and f[2] == d} == exp
        summary.append(dict(S=S, drugs=len({d for _, d, _ in rules}), build=build, mem=peak / 1e6, ok=ok, lat=statistics.mean(lat), latmax=max(lat), unif=statistics.mean(unifs), goals=statistics.mean(goals), exl=statistics.mean(e for e in exlen if e), exmax=max(exlen),
                            agree=agree, N=N, lat_b=statistics.mean(lat_b), unif_b=statistics.mean(unif_b), lat_c=lat_c, unif_c=st_c['unif'], lat_f=statistics.mean(lat_f), fir=statistics.mean(fir), fc_ok=fc_ok, nfc=len(lat_f)))
        if S == 2000: detail = rows
        print(f'(size {S} done)', file=sys.stderr, flush=True)
    print('### 7B-1. The 31 hand-built test cases on the 2,000-rule KB (expected vs actual; all three sizes are summarised below)\n')
    print('| case | expected verdict | actual verdict | expected reasons | actual reasons | explanation lines | pass | latency ms |'); print('|---|---|---|---|---|---|---|---|')
    for name, ve, va, ee, aa, el, good, l in detail: print(f"| {name} | {ve} | {va} | {', '.join(ee) or '-'} | {', '.join(aa) or '-'} | {el} | {'✓' if good else '✗'} | {l:.2f} |")
    print('\nExample explanation (case D11, 2,000-rule KB):\n\n```'); [print('\n'.join(x)) for x in sample_expl]; print('```\n')
    print('### 7B-2. Metrics by KB size\n')
    print('| rules | drugs covered | build time s | memory MB (patients + rules) | test cases passed | mean latency ms (indexed BC) | max latency ms | mean unifications / query | mean goals / query | mean explanation lines (cases with reasons) | oracle agreement (300 random) |'); print('|---|---|---|---|---|---|---|---|---|---|---|')
    for s in summary: print(f"| {s['S']:,} | {s['drugs']} | {s['build']:.2f} | {s['mem']:.0f} | {s['ok']}/{len(CASES)} | {s['lat']:.2f} | {s['latmax']:.2f} | {s['unif']:.1f} | {s['goals']:.1f} | {s['exl']:.1f} | {s['agree']}/{s['N']} |")
    print('\n### 7B-3. Baseline comparison (mean per query over the same test cases)\n')
    print('| rules | design: indexed BC ms | baseline 1: rules not indexed ms (unifications) | baseline 2: nothing indexed, one case, ms (unifications) | baseline 3: forward chaining per query ms (rule firings) | FC answers correct |'); print('|---|---|---|---|---|---|')
    for s in summary: print(f"| {s['S']:,} | {s['lat']:.2f} | {s['lat_b']:.2f} ({s['unif_b']:.0f}) | {s['lat_c']:.0f} ({s['unif_c']:,}) | {s['lat_f']:.1f} ({s['fir']:.0f}) | {s['fc_ok']}/{s['nfc']} |")
