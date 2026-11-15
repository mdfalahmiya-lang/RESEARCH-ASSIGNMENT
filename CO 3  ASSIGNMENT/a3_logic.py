"""Shared FOL toolkit for Assignment 3 (Tasks 3-7).
Terms/atoms: a constant is a str, a variable is a str starting with '?', a compound term or atom is a tuple
(functor, arg1, ...).  A substitution is a dict {var: term}."""
import itertools

def is_var(t): return isinstance(t, str) and t.startswith('?')

def walk(t, th):
    while is_var(t) and t in th: t = th[t]
    return t

def occurs(v, t, th):
    t = walk(t, th)
    if t == v: return True
    return isinstance(t, tuple) and any(occurs(v, a, th) for a in t[1:])

def _bind(v, t, th, occ):
    if occ and occurs(v, t, th): return None
    th = dict(th); th[v] = t; return th

def _unify(x, y, th, occ):
    if th is None: return None
    x, y = walk(x, th), walk(y, th)
    if x == y: return th
    if is_var(x): return _bind(x, y, th, occ)
    if is_var(y): return _bind(y, x, th, occ)
    if isinstance(x, tuple) and isinstance(y, tuple) and len(x) == len(y) and x[0] == y[0]:
        for a, b in zip(x[1:], y[1:]):
            th = _unify(a, b, th, occ)
            if th is None: return None
        return th
    return None

def apply(t, th):
    t = walk(t, th)
    if isinstance(t, tuple): return (t[0],) + tuple(apply(a, th) for a in t[1:])
    return t

def unify(x, y, th=None, occurs_check=True, cnt=None):
    """Most general unifier as an idempotent substitution, or None."""
    if cnt is not None: cnt['unif'] = cnt.get('unif', 0) + 1
    r = _unify(x, y, dict(th or {}), occurs_check)
    return None if r is None else {v: apply(v, r) for v in r}

def compose(s1, s2):
    """(s1 then s2): applying the result equals applying s1 and then s2."""
    r = {v: apply(t, s2) for v, t in s1.items()}
    for v, t in s2.items(): r.setdefault(v, t)
    return {v: t for v, t in r.items() if v != t}

def variables(t):
    if is_var(t): return {t}
    if isinstance(t, tuple): return set().union(*[variables(a) for a in t[1:]]) if len(t) > 1 else set()
    return set()

_ctr = itertools.count(1)
def rename(clause_terms, tag=None):
    """Standardise apart: give every variable in the given list of terms a fresh name."""
    tag = tag if tag is not None else next(_ctr)
    vs = set().union(*[variables(t) for t in clause_terms]) if clause_terms else set()
    m = {v: f'{v}_{tag}' for v in vs}
    return [apply(t, m) for t in clause_terms]

def fmt(t):
    if isinstance(t, tuple): return f'{t[0]}(' + ','.join(fmt(a) for a in t[1:]) + ')'
    return str(t)

def fmt_sub(th):
    return '{' + ', '.join(f'{v}/{fmt(t)}' for v, t in sorted(th.items())) + '}' if th is not None else 'FAIL'

# ---------------------------------------------------------------------------------------------
# Datalog-style knowledge base with backward chaining (used by Tasks 3, 6, 7)
# Facts are ground atoms.  Rules are (head, [body literals]); a body literal is an atom or ('not', atom)
# (negation as failure, evaluated when ground).  Counters are kept in self.stats.
# ---------------------------------------------------------------------------------------------
def variant_key(atom):
    m = {}
    def go(t):
        if is_var(t): return m.setdefault(t, f'_{len(m)}')
        if isinstance(t, tuple): return (t[0],) + tuple(go(a) for a in t[1:])
        return t
    return go(atom)

class KB:
    def __init__(self, index=True):
        self.index = index; self.index_rules = index; self.index_facts = index; self.facts = set(); self.by_pred = {}; self.by_arg0 = {}
        self.rules = {}; self.rule_idx = None; self.limit = None; self.reset()
    def reset(self):
        self.stats = dict(unif=0, goals=0, maxdepth=0, cut=0, repeat=0, rules_tried=0); self.seen = set()
    def add_fact(self, a):
        if a in self.facts: return
        self.facts.add(a); self.by_pred.setdefault(a[0], []).append(a); self.by_arg0.setdefault((a[0], a[1] if len(a) > 1 else None), []).append(a)
    def add_rule(self, head, body):
        self.rules.setdefault(head[0], []).append((head, body)); self.rule_idx = None
    def finalize(self):
        """Index rules by the first head argument position holding a constant (per predicate)."""
        self.rule_idx = {}
        for p, rs in self.rules.items():
            pos = next((i for i in range(1, len(rs[0][0])) if any(not is_var(h[i]) and not isinstance(h[i], tuple) for h, _ in rs)), None)
            keyed, other = {}, []
            for h, b in rs:
                if pos is not None and not is_var(h[pos]): keyed.setdefault(h[pos], []).append((h, b))
                else: other.append((h, b))
            self.rule_idx[p] = (pos, keyed, other, rs)
    def _rules_for(self, g):
        if self.rule_idx is None: self.finalize()
        pos, keyed, other, allr = self.rule_idx.get(g[0], (None, {}, [], []))
        if self.index_rules and pos is not None and not is_var(g[pos]): return keyed.get(g[pos], []) + other
        return allr
    def _facts_for(self, g):
        if self.index_facts and len(g) > 1 and not is_var(g[1]) and not isinstance(g[1], tuple): return self.by_arg0.get((g[0], g[1]), [])
        return self.by_pred.get(g[0], [])
    def solve(self, goals, th, depth, max_depth):
        if not goals: yield th; return
        g, rest = goals[0], goals[1:]
        if g[0] == 'not':
            atom = apply(g[1], th); self.stats['goals'] += 1
            if not any(True for _ in self.solve([atom], {}, depth + 1, max_depth)): yield from self.solve(rest, th, depth, max_depth)
            return
        gs = apply(g, th); self.stats['goals'] += 1
        if self.limit and self.stats['goals'] > self.limit: raise RuntimeError('goal budget exceeded')
        self.stats['maxdepth'] = max(self.stats['maxdepth'], depth)
        k = variant_key(gs)
        if k in self.seen: self.stats['repeat'] += 1
        self.seen.add(k)
        if depth > max_depth: self.stats['cut'] += 1; return
        for f in self._facts_for(gs):
            th2 = unify(gs, f, None, False, self.stats)
            if th2 is not None: yield from self.solve(rest, compose(th, th2) if th else th2, depth, max_depth)
        for h, b in self._rules_for(gs):
            self.stats['rules_tried'] += 1
            ren = rename([h] + list(b)); h2, b2 = ren[0], ren[1:]
            th2 = unify(gs, h2, None, False, self.stats)
            if th2 is not None: yield from self.solve(list(b2) + rest, compose(th, th2) if th else th2, depth + 1, max_depth)
    def ask(self, goal, max_depth=60, limit=None):
        """All answers: list of dicts for the variables of `goal`. Returns (answers, stats)."""
        self.reset(); vs = sorted(variables(goal)); out = []
        for th in self.solve([goal], {}, 0, max_depth):
            ans = tuple(apply(v, th) for v in vs)
            if ans not in out: out.append(ans)
            if limit and len(out) >= limit: break
        return out, dict(self.stats)
