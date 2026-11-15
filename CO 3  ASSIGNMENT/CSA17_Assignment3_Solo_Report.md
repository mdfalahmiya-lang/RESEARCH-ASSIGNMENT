# CSA17 – Artificial Intelligence | Assignment 3 (CO3) — Logical agents, propositional and first-order inference

**Submission mode: SOLO.** The assignment is written for pairs; I worked alone, so I carried out **both** the "Student A" and the "Student B" responsibilities of every task (each is labelled below) and never wrote "my partner did this". The contribution record at the end says so plainly.
**Method:** Represent → Infer → Implement → Measure → Debug → Evaluate → Defend. Operation counts (models, clauses, unifications, rule firings) are the primary evidence; times are secondary and come from one Python run on one machine.
**Files:** `a3_logic.py` (unification + backward-chaining engine), `a3_prop.py` (Tasks 1–2), `a3_t3.py … a3_t7.py`, raw outputs `t1_out.txt … t7_out.txt`. Run `python a3_prop.py t1`, `python a3_prop.py t2`, `python a3_t3.py` … `python a3_t7.py`. Seeds are in each file header.

---

## TASK 1 – Logical agents: knowledge bases, entailment and reasoning patterns

### Part A – Knowledge base and model checking in the Wumpus world
**Shared work.** For every square (r,c) of an n×n world there are four proposition symbols P (pit), W (wumpus), B (breeze), S (stench). The KB contains ¬P₁₁, ¬W₁₁, and for every square B_rc ⇔ (P of its neighbours) and S_rc ⇔ (W of its neighbours), plus the percept literals. A truth-table entailment checker (`tt_entails`) enumerates every assignment, evaluates the KB, and reports a counter-model if α is false in some model of the KB. Percepts used: ¬B₁₁, ¬S₁₁, B₂₁. Queries I designed: **α₁ = ¬P₁₂** ("(1,2) has no pit"), **α₂ = P₂₁**, **α₃ = W₂₂**.

**Student A – design and mathematical analysis**
* *Counting.* Symbols m = 4n². Sentences = 2 (the two unit facts) + 2n² (one biconditional per square for B and one for S) + percept literals, i.e. 2n² + 2 + 3: **13, 23, 37** for n = 2, 3, 4 (the program counts exactly these).
* *Models.* A model assigns T/F to every symbol: **2^m = 2^(4n²)**: 65,536; 6.9 × 10¹⁰; 1.8 × 10¹⁹.
* *Minimal relevant set for one query.* A sentence "X ⇔ φ" in which X occurs nowhere else and not in the query is satisfiable for **every** assignment of φ's symbols (set X := φ), so it constrains nothing else and can be dropped without changing any entailment; I apply this repeatedly. All B_rc/S_rc biconditionals of unvisited squares disappear. What remains for these percepts is {B₁₁, S₁₁, B₂₁, P₁₁, P₁₂, P₂₁, P₂₂, (P₃₁), W₁₁, W₁₂, W₂₁} plus the query symbol: **10–12 symbols for every n**, i.e. about 2,000 models, independent of the world size.
* *Soundness and completeness of model checking.* Sound: it answers "entailed" only if α holds in **every** model of the KB, which is the definition of KB ⊨ α. Complete: with finitely many symbols it examines all 2^m models, so it decides every entailment question. The price is the exponential 2^m.

**Student B – experimental validation** (table below). Full symbol set: n = 2 is feasible (65,671 models enumerated for an entailed query because the checker runs two checks, KB ⊨ α and KB ⊨ ¬α); **n = 3 (2³⁶ models) is infeasible**: at the measured 3.1 million models/s even the best case would need ≈ 6.1 hours, and n = 4 (2⁶⁴) ≈ 2 × 10⁵ years. With relevant-symbol restriction every n takes ≈ 2,083–2,118 models in about a millisecond. The three query types were all found: **entailed** (¬P₁₂), **negation entailed** (P₂₁: KB ⊨ ¬P₂₁), **neither** (W₂₂).

### Part B – Reasoning patterns
**Shared work.** Derivation of the safety of three squares by inference rules (n = 3; percepts ¬B₁₁, ¬S₁₁, B₂₁, then ¬B₁₂, ¬S₁₂ after visiting (1,2)). Biconditional elimination turns B₁₁ ⇔ (P₁₂ ∨ P₂₁) into the clauses (¬B₁₁ ∨ P₁₂ ∨ P₂₁), (¬P₁₂ ∨ B₁₁), (¬P₂₁ ∨ B₁₁). Then:
1. And-Elimination picks the clause (¬P₁₂ ∨ B₁₁) out of the conjunction;
2. **Unit Resolution** with the percept literal ¬B₁₁ gives **¬P₁₂**; likewise ¬P₂₁;
3. the same two steps with ¬S₁₁ give ¬W₁₂, ¬W₂₁; And-Introduction gives "(1,2) safe" = ¬P₁₂ ∧ ¬W₁₂.
Square (2,2) is safe after the second visit: ¬B₁₂ and the clause (¬P₂₂ ∨ B₁₂) give ¬P₂₂, ¬S₁₂ gives ¬W₂₂.

**Student A – experimental investigation.** Each safety conclusion needs **3 inference steps** (one unit resolution for ¬P, one for ¬W, one And-Introduction); the log in the table confirms every literal is obtained by exactly one resolution step (the whole KB saturates in 12 steps). Model checking the same query needs **65,536 models** even with relevant-symbol pruning (16 symbols), a factor of ≈ 22,000.

**Student B – soundness reasoning.** Truth tables for Modus Ponens, And-Elimination, Unit Resolution and Biconditional-Elimination are in the tables: in every row where all premises are true, the conclusion is true. **Why a derived sentence holds in every model of the KB:** by induction on the derivation: the KB sentences are true in every model of the KB, and each rule application preserves truth (the tables), so every derived sentence is too. **Why "not derived" is not "false":** failure to derive α shows only that this rule set found no proof; even for a complete system it means KB ⊭ α, i.e. α is false in *some* model, not in all. Example from the run: with these percepts neither P₂₂ nor ¬P₂₂ is derivable and the KB has models with P₂₂ true (2) and false (1).

**Cross-understanding.** (A can explain B's soundness tables and B can explain A's counting and pruning argument; both are covered above.)

### Evidence (program output, `t1_out.txt`)
## 1A. Size of the KB as a function of n (derived: symbols 4n², sentences 2 + 2n² + percepts, models 2^(4n²))

| n | symbols m = 4n² | sentences (2 + 2n² + 3 percepts) | models 2^m | counted symbols | counted sentences |
|---|---|---|---|---|---|
| 2 | 16 | 13 | 65,536 | 16 | 13 |
| 3 | 36 | 23 | 68,719,476,736 | 36 | 23 |
| 4 | 64 | 37 | 18,446,744,073,709,551,616 | 64 | 37 |

## 1B. Truth-table entailment: full symbol set vs relevant-symbol restriction
Percepts: ¬B_1_1, ¬S_1_1, B_2_1.  Each query is classified by two checks (KB |= α, KB |= ¬α).

| n | symbols used | query | verdict | models enumerated | sentence evaluations | time s |
|---|---|---|---|---|---|---|
| 2 | full (16) | ¬P_1_2  ("(1,2) has no pit") | entailed | 65,671 | 131,445 | 0.02 |
| 2 | full (16) | P_2_1  ("(2,1) has a pit") | negation entailed | 65,671 | 131,445 | 0.02 |
| 2 | full (16) | W_2_2  ("wumpus in (2,2)") | neither | 34,574 | 70,140 | 0.01 |
| 2 | relevant (10) | ¬P_1_2  ("(1,2) has no pit") | entailed | 1,059 | 2,128 | 0.001 |
| 2 | relevant (10) | P_2_1  ("(2,1) has a pit") | negation entailed | 1,059 | 2,128 | 0.001 |
| 2 | relevant (11) | W_2_2  ("wumpus in (2,2)") | neither | 1,094 | 2,230 | 0.001 |
| 3 | full (36) | ¬P_1_2  ("(1,2) has no pit") | INFEASIBLE: 2^36 = 68,719,476,736 models | - | - | - |
| 3 | full (36) | P_2_1  ("(2,1) has a pit") | INFEASIBLE: 2^36 = 68,719,476,736 models | - | - | - |
| 3 | full (36) | W_2_2  ("wumpus in (2,2)") | INFEASIBLE: 2^36 = 68,719,476,736 models | - | - | - |
| 3 | relevant (11) | ¬P_1_2  ("(1,2) has no pit") | entailed | 2,083 | 4,154 | 0.001 |
| 3 | relevant (11) | P_2_1  ("(2,1) has a pit") | negation entailed | 2,083 | 4,154 | 0.001 |
| 3 | relevant (12) | W_2_2  ("wumpus in (2,2)") | neither | 2,118 | 4,256 | 0.001 |
| 4 | full (64) | ¬P_1_2  ("(1,2) has no pit") | INFEASIBLE: 2^64 = 18,446,744,073,709,551,616 models | - | - | - |
| 4 | full (64) | P_2_1  ("(2,1) has a pit") | INFEASIBLE: 2^64 = 18,446,744,073,709,551,616 models | - | - | - |
| 4 | full (64) | W_2_2  ("wumpus in (2,2)") | INFEASIBLE: 2^64 = 18,446,744,073,709,551,616 models | - | - | - |
| 4 | relevant (11) | ¬P_1_2  ("(1,2) has no pit") | entailed | 2,083 | 4,154 | 0.001 |
| 4 | relevant (11) | P_2_1  ("(2,1) has a pit") | negation entailed | 2,083 | 4,154 | 0.001 |
| 4 | relevant (12) | W_2_2  ("wumpus in (2,2)") | neither | 2,118 | 4,256 | 0.001 |

Measured throughput ≈ 3,129,314 models/s, so the full n=3 set (2^36 = 6.9e10 models) would take ≈ 6.1 hours (best case, with early exit per model) and n=4 (2^64) ≈ 1.9e+05 years: infeasible in practice.

## 1C. Part B - derivations with inference rules instead of model checking (n = 3)

* Square (1,2) safe (¬P ∧ ¬W) derived: **True**
* Square (2,1) safe (¬P ∧ ¬W) derived: **True**
* Square (2,2) safe (¬P ∧ ¬W) derived: **True**
* Total unit-resolution steps to saturate the KB: 12.  Derivation log:

   - Unit Resolution: clause {-P_2_1, B_1_1} with unit(s) -B_1_1  ⊢  -P_2_1
   - Unit Resolution: clause {-P_1_2, B_1_1} with unit(s) -B_1_1  ⊢  -P_1_2
   - Unit Resolution: clause {-W_2_1, S_1_1} with unit(s) -S_1_1  ⊢  -W_2_1
   - Unit Resolution: clause {-W_1_2, S_1_1} with unit(s) -S_1_1  ⊢  -W_1_2
   - Unit Resolution: clause {-P_2_2, B_1_2} with unit(s) -B_1_2  ⊢  -P_2_2
   - Unit Resolution: clause {-P_1_3, B_1_2} with unit(s) -B_1_2  ⊢  -P_1_3
   - Unit Resolution: clause {-W_2_2, S_1_2} with unit(s) -S_1_2  ⊢  -W_2_2
   - Unit Resolution: clause {-W_1_3, S_1_2} with unit(s) -S_1_2  ⊢  -W_1_3
   - Unit Resolution: clause {-B_2_1, P_1_1, P_2_2, P_3_1} with unit(s) -P_1_1, -P_2_2, B_2_1  ⊢  P_3_1
   - Unit Resolution: clause {-P_3_1, B_3_2} with unit(s) P_3_1  ⊢  B_3_2

Inference-rule cost for each query (resolution steps for the two literals + 1 And-Introduction) vs model checking on the relevant symbols:

| query | rule steps | model-checking models (relevant symbols) |
|---|---|---|
| safe(1,2) (entailed = True) | 3 | 65,536 |
| safe(2,1) (entailed = True) | 3 | 65,536 |
| safe(2,2) (entailed = True) | 3 | 65,536 |

## 1D. Soundness truth tables (every row where all premises are true must make the conclusion true)

**Modus Ponens (P⇒Q, P ⊢ Q)**

| P | Q | premises all true? | conclusion | sound on this row |
|---|---|---|---|---|
| 1 | 1 | 1 | 1 | ✓ |
| 1 | 0 | 0 | 0 | ✓ |
| 0 | 1 | 0 | 1 | ✓ |
| 0 | 0 | 0 | 0 | ✓ |

Sound: **True**

**And-Elimination (P∧Q ⊢ P)**

| P | Q | premises all true? | conclusion | sound on this row |
|---|---|---|---|---|
| 1 | 1 | 1 | 1 | ✓ |
| 1 | 0 | 0 | 1 | ✓ |
| 0 | 1 | 0 | 0 | ✓ |
| 0 | 0 | 0 | 0 | ✓ |

Sound: **True**

**Unit Resolution (P∨Q, ¬P ⊢ Q)**

| P | Q | premises all true? | conclusion | sound on this row |
|---|---|---|---|---|
| 1 | 1 | 0 | 1 | ✓ |
| 1 | 0 | 0 | 0 | ✓ |
| 0 | 1 | 1 | 1 | ✓ |
| 0 | 0 | 0 | 0 | ✓ |

Sound: **True**

**Biconditional-Elimination (P⇔Q ⊢ (P⇒Q)∧(Q⇒P))**

| P | Q | premises all true? | conclusion | sound on this row |
|---|---|---|---|---|
| 1 | 1 | 1 | 1 | ✓ |
| 1 | 0 | 0 | 0 | ✓ |
| 0 | 1 | 0 | 0 | ✓ |
| 0 | 0 | 1 | 1 | ✓ |

Sound: **True**

"Not derived" is not "false": under percepts ¬B11, ¬S11, B21 (n=3), neither P_2_2 nor ¬P_2_2 is derivable, and enumeration finds KB-models of both kinds:
models of the KB with P_2_2 true: 2; with P_2_2 false: 1  → KB ⊭ P_2_2 and KB ⊭ ¬P_2_2.

---

## TASK 2 – Model checking versus resolution

### Policy KB, CNF and proof
A smart-building access policy of **13 rules** (implications, a biconditional R4 and R13, disjunctions in R6, R7, R9, R10) over 14 symbols is listed in the evidence. **Hand CNF conversions** (the program's stage log agrees):
* R4: access ⇔ unlock → (¬access ∨ unlock) ∧ (¬unlock ∨ access).
* R7: alarm ⇒ (intrusion ∨ forced ∨ emergency) → the single clause (¬alarm ∨ intrusion ∨ forced ∨ emergency).
* R9: ((¬work ∧ badge ∧ ¬visitor ∧ (supervisor ∨ afterpass)) ⇒ access) → work ∨ ¬badge ∨ visitor ∨ (¬supervisor ∧ ¬afterpass) ∨ access → distribute: **(work ∨ ¬badge ∨ visitor ∨ access ∨ ¬supervisor) ∧ (work ∨ ¬badge ∨ visitor ∨ access ∨ ¬afterpass)**.

**Student A – resolution investigation.** Proof of "badge ∧ work ∧ ¬visitor ⊨ unlock" by refutation: negate the query (¬unlock) and derive the empty clause; the proof tree is in the evidence (17 clauses generated, 22 resolvents attempted). **Non-entailed query** (a visitor in working hours does not entail unlock): the clause set **saturated** (391 generated, 158 tautologies discarded, 393 subsumed) and the prover stopped without the empty clause. *Why it terminates:* over k symbols a clause is a subset of 2k literals, so there are at most 3ᵏ non-tautological clauses; every resolvent is stored only if new, so the process must run out of new clauses. **Growth with KB size** (implication chains p₀, p_i ⇒ p_{i+1}, query p_n, n = 10, 20, 40, 80): with plain first-in-first-out saturation the clauses generated were 66, 231, 861, 3,321 (≈ ×3.7 per doubling, i.e. Θ(n²)) and the resolvents attempted 153, 908, 6,180, 45,368 (≈ ×6–7, ≈ n^2.7); with **unit-preference** (shortest clause first) only **12, 22, 42, 82** clauses (n + 2, linear).

**Student B – model-checking comparison.** Same KBs: model checking needs 2^(n+1) models: 2,048 (n = 10), 2,097,152 (n = 20, 0.22 s), and is **infeasible** for n = 40 (2⁴¹) and n = 80 (2⁸¹). **Family where model checking is faster:** unsatisfiable *pigeonhole* KBs PHP(5,4) (20 symbols): 1,048,576 models in 0.26 s, whereas resolution gave up after 150,001 generated clauses (both strategies); on PHP(4,3) plain saturation generated 60,322 clauses (3.5 s) against 4,096 models. **Family where model checking is far slower:** the implication chains (n ≥ 40). **Structural reason:** model-checking cost depends only on the **number of symbols** (2^k), whatever the shape of the sentences; resolution cost depends on the **size of the proof the search finds**, which is linear for Horn/chain structure (each step has a unit clause) but exponential for counting-style constraints like the pigeonhole principle (a known exponential lower bound for resolution).

**Joint design question.** Before choosing I would want: (1) the number of symbols k now and expected growth (k ≲ 20–25: ≈ 10⁶–10⁷ models, cheap); (2) the structure: share of Horn clauses and implication chains (resolution with unit preference, or forward chaining, is linear), and whether there are "at most one / exactly k" counting constraints (resolution can blow up); (3) the number of queries per KB: model checking can enumerate the models once and reuse them, resolution restarts per query; (4) whether a time guarantee is needed. My measurements give the rule: small k → model checking; chain-like/Horn at any size → resolution with unit preference; large k and non-Horn → neither; use a SAT solver.

### Evidence (program output, `t2_out.txt`)
## 2A. Policy KB (13 rules; implication, biconditional, disjunction). Symbols: access, afterpass, alarm, badge, emergency, escort, forced, intrusion, lockdown, maint, supervisor, unlock, visitor, work 

R1: ((badge ∧ work ∧ ¬visitor) ⇒ access)
R2: ((visitor ∧ escort ∧ work) ⇒ access)
R3: (emergency ⇒ access)
R4: (access ⇔ unlock)
R5: ((lockdown ∧ ¬emergency) ⇒ ¬unlock)
R6: (visitor ⇒ (escort ∨ ¬access))
R7: (alarm ⇒ (intrusion ∨ forced ∨ emergency))
R8: (intrusion ⇒ lockdown)
R9: ((¬work ∧ badge ∧ ¬visitor ∧ (supervisor ∨ afterpass)) ⇒ access)
R10: (maint ⇒ (escort ∨ badge))
R11: (forced ⇒ ¬badge)
R12: ((access ∧ ¬emergency) ⇒ ¬lockdown)
R13: (alarm ⇔ (intrusion ∨ forced))

### Hand-checkable CNF conversions (stage log from the program)

**R4**

- original: `(access ⇔ unlock)`
- eliminate ⇔ and ⇒: `((¬access ∨ unlock) ∧ (¬unlock ∨ access))`
- push ¬ inward (NNF): `((¬access ∨ unlock) ∧ (¬unlock ∨ access))`
- distribute ∨ over ∧ → clauses: `{-access, unlock} ∧ {-unlock, access}`

**R7**

- original: `(alarm ⇒ (intrusion ∨ forced ∨ emergency))`
- eliminate ⇔ and ⇒: `(¬alarm ∨ (intrusion ∨ forced ∨ emergency))`
- push ¬ inward (NNF): `(¬alarm ∨ (intrusion ∨ forced ∨ emergency))`
- distribute ∨ over ∧ → clauses: `{-alarm, emergency, forced, intrusion}`

**R9**

- original: `((¬work ∧ badge ∧ ¬visitor ∧ (supervisor ∨ afterpass)) ⇒ access)`
- eliminate ⇔ and ⇒: `(¬(¬work ∧ badge ∧ ¬visitor ∧ (supervisor ∨ afterpass)) ∨ access)`
- push ¬ inward (NNF): `((work ∨ ¬badge ∨ visitor ∨ (¬supervisor ∧ ¬afterpass)) ∨ access)`
- distribute ∨ over ∧ → clauses: `{-badge, -supervisor, access, visitor, work} ∧ {-afterpass, -badge, access, visitor, work}`

Whole KB in CNF: 17 clauses over 14 symbols.

### Entailed query: staff with a valid badge, in working hours ⊨ door unlocked

result: entailed (empty clause derived); clauses generated 17, resolvents attempted 22

```
[] (empty clause)   [resolve on visitor]
  {visitor}   [resolve on work]
    {-work, visitor}   [resolve on badge]
      {-badge, -work, visitor}   [resolve on access]
        {-badge, -work, access, visitor}   [input]
        {-access}   [resolve on unlock]
          {-access, unlock}   [input]
          {-unlock}   [input]
      {badge}   [input]
    {work}   [input]
  {-visitor}   [input]
```

### Non-entailed query: a visitor in working hours ⊨ door unlocked ?

result: NOT entailed: the clause set saturated (no new clauses) without the empty clause; generated 391, attempted 939, tautologies 158, subsumed 393.
Why it terminates: clauses over k symbols are subsets of 2k literals, at most 3^k non-tautological clauses; every resolvent is new and finite, so the generation of new clauses must stop.

Model checking on the same entailed query: entailed = True, models enumerated 16,384 (2^14 = 16,384).

## 2B. Implication chains p0, p0⇒p1, …, p_{n-1}⇒p_n, query p_n (resolution refutation vs model checking)

| n | method | outcome | clauses generated | resolvents attempted | tautologies discarded | subsumed removed | time s |
|---|---|---|---|---|---|---|---|
| 10 | resolution (fifo) | proved | 66 | 153 | 0 | 34 | 0.002 |
| 10 | resolution (shortest) | proved | 12 | 12 | 0 | 10 | 0.000 |
| 10 | model checking | entailed | models: 2048 | - | - | - | 0.0 |
| 20 | resolution (fifo) | proved | 231 | 908 | 0 | 119 | 0.002 |
| 20 | resolution (shortest) | proved | 22 | 22 | 0 | 20 | 0.000 |
| 20 | model checking | entailed | models: 2097152 | - | - | - | 0.217 |
| 40 | resolution (fifo) | proved | 861 | 6,180 | 0 | 445 | 0.014 |
| 40 | resolution (shortest) | proved | 42 | 42 | 0 | 40 | 0.001 |
| 40 | model checking | INFEASIBLE (2^41 = 2,199,023,255,552 models) | models: - | - | - | - | 0.0 |
| 80 | resolution (fifo) | proved | 3,321 | 45,368 | 0 | 1,721 | 0.098 |
| 80 | resolution (shortest) | proved | 82 | 82 | 0 | 80 | 0.001 |
| 80 | model checking | INFEASIBLE (2^81 = 2,417,851,639,229,258,349,412,352 models) | models: - | - | - | - | 0.0 |

## 2C. KB families that favour each method

| KB family | symbols | method | outcome | work | time s |
|---|---|---|---|---|---|
| pigeonhole PHP(4,3) (unsatisfiable) | 12 | model checking | unsat | 4,096 models | 0.00 |
| pigeonhole PHP(4,3) | 12 | resolution (fifo) | refuted | 60,322 generated, 824,543 attempted | 3.50 |
| pigeonhole PHP(4,3) | 12 | resolution (shortest) | refuted | 2,140 generated, 6,235 attempted | 0.02 |
| pigeonhole PHP(5,4) (unsatisfiable) | 20 | model checking | unsat | 1,048,576 models | 0.26 |
| pigeonhole PHP(5,4) | 20 | resolution (fifo) | GAVE UP (cap/time) | 150,001 generated, 373,958 attempted | 1.36 |
| pigeonhole PHP(5,4) | 20 | resolution (shortest) | GAVE UP (cap/time) | 150,001 generated, 633,195 attempted | 2.25 |
| chain n=20 | 21 | model checking | entailed | 2,097,152 models | 0.22 |
| chain n=20 | 21 | resolution (shortest) | proved | 22 generated, 22 attempted | 0.033 |

---

## TASK 3 – Knowledge engineering for exam eligibility (propositional vs first-order)

### Knowledge-engineering process
*Task:* decide whether a student may write the examination of a course. *Knowledge:* attendance, prerequisites, fees, discipline, approved leave. *Vocabulary:* Student, Course, Enrolled(s,c), Attendance(s,c,level∈{ok,short}), AttOK(s,c), Leave(l,s,c), Approved(l), ApprovedLeave(s,c), Prereq(p,c), Passed(s,p), PrereqsCleared(s,c), MissingPrereq(s,c), Receipt(r), PaidBy(r,s), FeesPaid(s), Disciplinary(d,s), Active(d), Barred(s), Eligible(s,c), HallTicket(s,c).

**Student A – FOL axioms (13; A5, A6, A7, A12 contain existential quantifiers)**
* A1 ∀s,c Enrolled(s,c) ∧ AttOK(s,c) ∧ PrereqsCleared(s,c) ∧ FeesPaid(s) ∧ ¬Barred(s) ⇒ Eligible(s,c)
* A2 ∀s,c Eligible(s,c) ⇒ Enrolled(s,c) ∧ FeesPaid(s) ∧ ¬Barred(s)
* A3 ∀s,c Attendance(s,c,ok) ⇒ AttOK(s,c)
* A4 ∀s,c Attendance(s,c,short) ∧ ApprovedLeave(s,c) ⇒ AttOK(s,c)
* A5 ∀s FeesPaid(s) ⇔ ∃r (Receipt(r) ∧ PaidBy(r,s))
* A6 ∀s Barred(s) ⇔ ∃d (Disciplinary(d,s) ∧ Active(d))
* A7 ∀s,c ApprovedLeave(s,c) ⇔ ∃l (Leave(l,s,c) ∧ Approved(l))
* A8 ∀s,c PrereqsCleared(s,c) ⇔ ∀p (Prereq(p,c) ⇒ Passed(s,p))
* A9 ∀s,c MissingPrereq(s,c) ⇔ Enrolled(s,c) ∧ ¬PrereqsCleared(s,c)
* A10 ∀s Barred(s) ⇒ ∀c ¬Eligible(s,c)
* A11 ∀s,c HallTicket(s,c) ⇔ Eligible(s,c)
* A12 ∀c Course(c) ⇒ ∃s Enrolled(s,c) (integrity constraint)
* A13 ∀s,c ¬Enrolled(s,c) ⇒ ¬Eligible(s,c)
The **executable form** is nine Horn rules (A1, A3, A4, A5–A9 as bodies with negation as failure, A11); A2, A10, A13 are consequences of A1 under the closed-world reading (checked by queries 6–11), A12 is an integrity check.
* **Growth derivation.** Propositional encoding: for every (student, course) pair five rule schemas are needed (AttOK from "ok", AttOK via leave, PrereqsOK, Eligible, HallTicket): **5·s·c rules**, plus the instance facts F(s,c) = Θ(s·c). So N_prop(s,c) = 5sc + F(s,c) = Θ(sc). FOL: **9 rules (constant)** + the same F(s,c). Measured rule counts: 20, 125, 500, 2,000, 8,000, 32,000 against 9; total sentences ratio 1.5 → 3.6, tending to 1 + 5sc/F with F ≈ 1.9sc, i.e. ≈ 3.6.

**Student B – crossover investigation**
* **Query suite and defects.** 16 competency queries (5 that succeed, 6 that fail, 5 returning bindings), each with its expected answer written beforehand. My first draft (v0) failed **6 of 16** queries; four KB defects were found and fixed (v1: 16/16): (1) no `¬Barred` condition in Eligible (eve eligible although barred); (2) ApprovedLeave ignored `Approved(l)` (a pending leave condoned short attendance, hal); (3) Eligible lacked `Enrolled(s,c)` (gus, who dropped the course, eligible); (4) **floundering negation**: `MissingPrereq` evaluated `not Passed(s,p)` while s was still unbound, so the query returned no answers; fixed by putting `Enrolled(s,c)` first so that s and c are bound before the negation. (Two further failures were symptoms of the first three, and one expected-answer ordering slip in my test harness was a harness bug, not a KB defect.)
* **Size and time as s and c grow** (table below, s = c, answers of both encodings agree in every run): the FOL KB is 3.6× smaller at 80×80 and builds ≈ 8× faster (8 ms vs 67 ms), **but each query is ≈ 145× slower** (≈ 0.65 ms vs ≈ 4.5 µs) because FOL spends 190 unifications per query against 4.7 table look-ups. Because grounding is paid on every KB change, the FOL encoding is cheaper overall when fewer than the **break-even number of queries** occur between changes: 0 (2×2), 3, 3, 15, 20 and **≈ 91 queries at 80×80**.

**Joint conclusion.** More expressive language does not automatically give faster reasoning: lifting adds substitution and unification work to every step (≈ 40× more steps per query here, each costlier), and unrelated data still has to be scanned (`Passed(s,·)` has ≈ 64 facts per student under a first-argument index). What expressiveness buys is a **constant-size, general, maintainable rule base** (9 rules instead of 32,000, rules unchanged when students or courses are added) and cheaper rebuilds. FOL is preferable from roughly 20×20 pairs upward when the knowledge changes or the number of queries per change is below ≈ 20–100, and propositional wins for small, static KBs with many queries. (Timings are single runs; the break-even values are indicative.)

### Evidence (program output, `t3_out.txt`)
## 3A. Defect log: query suite on draft v0 and on corrected v1


**Query suite on KB v0 (first draft)** (16 queries: 5 succeed, 6 fail, 5 bindings; binding tuples list variables in alphabetical order, e.g. (?c, ?s))

| # | kind | query | expected | actual | ok |
|---|---|---|---|---|---|
| 1 | succeed | Eligible(ann,CS101) | True | True | ✓ |
| 2 | succeed | Eligible(cat,CS101) | True | True | ✓ |
| 3 | succeed | Eligible(ivy,CS201) | True | True | ✓ |
| 4 | succeed | FeesPaid(ann) | True | True | ✓ |
| 5 | succeed | HallTicket(ann,CS101) | True | True | ✓ |
| 6 | fail | Eligible(bob,CS101) | False | False | ✓ |
| 7 | fail | Eligible(dan,CS101) | False | False | ✓ |
| 8 | fail | Eligible(eve,CS101) | False | True | ✗ DEFECT |
| 9 | fail | Eligible(fay,CS201) | False | False | ✓ |
| 10 | fail | Eligible(hal,CS101) | False | True | ✗ DEFECT |
| 11 | fail | Eligible(gus,MA101) | False | True | ✗ DEFECT |
| 12 | bindings | Eligible(?s,CS101) | {ann, cat} | {ann, cat, eve, hal} | ✗ DEFECT |
| 13 | bindings | Barred(?s) | {eve} | {eve} | ✓ |
| 14 | bindings | MissingPrereq(?s,?c) | {CS201/fay} | {} | ✗ DEFECT |
| 15 | bindings | ApprovedLeave(?s,?c) | {CS101/cat} | {CS101/cat, CS101/hal} | ✗ DEFECT |
| 16 | bindings | Eligible(ivy,?c) | {CS201} | {CS201} | ✓ |

6 of 16 queries wrong.

**Query suite on KB v1 (after fixes)** (16 queries: 5 succeed, 6 fail, 5 bindings; binding tuples list variables in alphabetical order, e.g. (?c, ?s))

| # | kind | query | expected | actual | ok |
|---|---|---|---|---|---|
| 1 | succeed | Eligible(ann,CS101) | True | True | ✓ |
| 2 | succeed | Eligible(cat,CS101) | True | True | ✓ |
| 3 | succeed | Eligible(ivy,CS201) | True | True | ✓ |
| 4 | succeed | FeesPaid(ann) | True | True | ✓ |
| 5 | succeed | HallTicket(ann,CS101) | True | True | ✓ |
| 6 | fail | Eligible(bob,CS101) | False | False | ✓ |
| 7 | fail | Eligible(dan,CS101) | False | False | ✓ |
| 8 | fail | Eligible(eve,CS101) | False | False | ✓ |
| 9 | fail | Eligible(fay,CS201) | False | False | ✓ |
| 10 | fail | Eligible(hal,CS101) | False | False | ✓ |
| 11 | fail | Eligible(gus,MA101) | False | False | ✓ |
| 12 | bindings | Eligible(?s,CS101) | {ann, cat} | {ann, cat} | ✓ |
| 13 | bindings | Barred(?s) | {eve} | {eve} | ✓ |
| 14 | bindings | MissingPrereq(?s,?c) | {CS201/fay} | {CS201/fay} | ✓ |
| 15 | bindings | ApprovedLeave(?s,?c) | {CS101/cat} | {CS101/cat} | ✓ |
| 16 | bindings | Eligible(ivy,?c) | {CS201} | {CS201} | ✓ |

0 of 16 queries wrong.

Defects found by v0 (queries 8, 10, 11, 12, 14, 15) and their fixes:

1. Query 8 `Eligible(eve,CS101)` succeeded: the Eligible rule had no `not Barred(s)` condition → added.
2. Query 10 `Eligible(hal,CS101)` succeeded: ApprovedLeave ignored `Approved(l)`, so a pending leave condoned short attendance → added `Approved(l)` to the rule body.
3. Query 11 `Eligible(gus,MA101)` succeeded: a student with an attendance record but no `Enrolled` fact was eligible → added `Enrolled(s,c)` to the Eligible rule.
4. Query 14 `MissingPrereq(?s,?c)` returned no answers although fay lacks CS101: the negated literal `not Passed(s,p)` was evaluated while ?s was still unbound (negation as failure needs bound variables, "floundering"): Passed(?s,CS101) succeeds for ivy, so the negation failed for every s. Fix: put `Enrolled(s,c)` before the negation so s and c are bound.
(Queries 12 and 15 failed in v0 as symptoms of defects 1-3.)

## 3B. KB size and inference cost as students s and courses c grow (s = c)

| s = c | pairs s·c | propositional sentences (rules + facts) | FOL sentences (axioms + facts) | prop. rules only | FOL rules only | build time prop ms | build time FOL ms | 200 queries: prop ms | 200 queries: FOL ms | prop steps/query | FOL unifications/query | answers agree | break-even number of queries |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 4 | 29 | 19 | 20 | 9 | 0.0 | 0.1 | 0.2 | 15.0 | 2.9 | 3.9 | True | 0 |
| 5 | 25 | 173 | 61 | 125 | 9 | 0.3 | 0.0 | 0.3 | 16.3 | 3.5 | 8.3 | True | 3 |
| 10 | 100 | 705 | 230 | 500 | 9 | 0.5 | 0.1 | 0.4 | 31.0 | 5.1 | 29.7 | True | 3 |
| 20 | 400 | 2759 | 795 | 2000 | 9 | 2.8 | 0.5 | 0.5 | 32.3 | 4.5 | 40.9 | True | 15 |
| 40 | 1600 | 11027 | 3151 | 8000 | 9 | 10.6 | 1.9 | 0.8 | 89.1 | 4.9 | 101.1 | True | 20 |
| 80 | 6400 | 43789 | 12122 | 32000 | 9 | 67.3 | 8.0 | 0.9 | 130.6 | 4.7 | 189.8 | True | 91 |

---

## TASK 4 – Unification and lifted inference
*(Responsibilities reversed: **Student B** = logical design and correctness; **Student A** = experiments.)*

### Student B – hand derivations (the code in `a3_t4.py` checks each one)
1. **P(x,F(y)) ~ P(A,F(B))**: x/A; F(y) ~ F(B) gives y/B → **{x/A, y/B}**.
2. **Knows(John,x) ~ Knows(y,Mother(y))**: John ~ y gives y/John; x ~ Mother(y), after applying y/John: x/Mother(John) → **{y/John, x/Mother(John)}**.
3. **Occurs check: P(x) ~ P(F(x))**: x ~ F(x) requires x to equal a term containing x, so with the occurs check the answer is **FAIL**. Without it x/F(x) is accepted: an infinite term, and unsound conclusions. This is the only one of my five pairs that gives a wrong answer if the check is removed.
4. **Standardising apart: Knows(John,x) ~ Knows(x,Elizabeth)**: the two x belong to different sentences. Treated as the same variable: x/John, then John ~ Elizabeth fails (**FAIL**, although the sentences are compatible). After renaming the second sentence's variable to x₁: x₁/John, x/Elizabeth → **{x₁/John, x/Elizabeth}**.
5. **Q(F(x),y,G(y)) ~ Q(F(z),H(z),G(H(w)))**: F(x)~F(z) gives x/z; y ~ H(z) gives y/H(z); G(y) ~ G(H(w)) becomes G(H(z)) ~ G(H(w)), so z/w; composing: **{x/w, z/w, y/H(w)}** (substitution composition verified by code).

**Why lifted inference is sound.** Lifted Modus Ponens = *universal instantiation* with a substitution θ (sound: a ∀-sentence holds for every instance) followed by ordinary Modus Ponens on the ground instances. θ is a **most general** unifier, so the conclusion qθ is the most general conclusion, and every conclusion obtainable from any ground instantiation is an instance of it. **Why it can avoid ground instances:** only the instantiations actually needed for the proof are formed (King(x) ∧ Greedy(x) ⇒ Evil(x) with King(John), Greedy(y) yields Evil(John) without ever instantiating the rule over the whole domain).

### Student A – experimental and engineering analysis
* **Ground clauses vs number of constants** (propositionalisation instantiates every universal rule with all constants): a rule with v variables over k constants gives exactly **kᵛ** instances (verified by generation); a predicate of arity a gives kᵃ ground atoms. At k = 30: 30, 900, 27,000, 810,000 clauses for v = 1…4.
* **Function symbols.** With one constant and a unary function F there are d + 1 ground terms of depth ≤ d (linear); with 2 constants and a binary function the count obeys **T(d) = 2 + T(d−1)²**: 2, 6, 38, 1,446, 2,090,918 (doubly exponential; the first four counted by generation); without a depth bound the set is infinite.
* **Lifted vs propositional inference** on the same query (Path(c₁,c_k) over a chain of k nodes): at k = 30 lifted backward chaining needs **118 unifications (indexed) in 2.0 ms**; propositional inference needs **27,900 ground clauses, 809,100 rule checks and 167.5 ms** (grounding + inference), an 80× time gap that widens with k (k³ clauses).

**Joint engineering decision.** I would propositionalise a KB despite lifted inference only when: the domain is **finite and function-free**; k and the variables per rule are small (kᵛ manageable: ≤ about 3 variables and ≤ 30 constants gave ≤ 27,000 clauses); the KB is **static and queried many times** (ground once, then use a propositional or SAT engine); or a propositional tool is required. I would not propositionalise with function symbols (infinite), with many variables or constants (kᵛ), or for a single query (my 4C table: lifted is faster). This conclusion about the many-queries case is reasoning from the grounding cost; I did not measure a multi-query regime.

### Evidence (program output, `t4_out.txt`)
## 4A. Most general unifiers (five designed pairs; hand derivation in the report, computed here as a check)

| pair | unifier |
|---|---|
| 1 plain: `P(?x,F(?y))` ~ `P(A,F(B))` | {?x/A, ?y/B} |
| 2 variable bound to a term containing a variable: `Knows(John,?x)` ~ `Knows(?y,Mother(?y))` | {?x/Mother(John), ?y/John} |
| 3 occurs check matters: P(x) vs P(F(x)): `P(?x)` ~ `P(F(?x))` | FAIL |
| 3b same pair WITHOUT occurs check: `P(?x)` ~ `P(F(?x))` | (no occurs check) ACCEPTED: x would be bound to F(x), an infinite term (wrong) |
| 4 standardising apart is essential: Knows(John,x) vs Knows(x,Elizabeth): `Knows(John,?x)` ~ `Knows(?x,Elizabeth)` | FAIL |
| 4b after renaming x -> x1 in the second atom: `Knows(John,?x)` ~ `Knows(?x1,Elizabeth)` | {?x/Elizabeth, ?x1/John} |
| 5 composition: Q(F(x),y,G(y)) vs Q(F(z),H(z),G(H(w))): `Q(F(?x),?y,G(?y))` ~ `Q(F(?z),H(?z),G(H(?w)))` | {?x/?w, ?y/H(?w), ?z/?w} |

Substitution composition check: s1 = {x/F(y), y/z}, s2 = {y/A, z/B}: compose(s1,s2) = {?x/F(A), ?y/B, ?z/B} ; apply(apply(x,s1),s2) = F(B)

Which of my test pairs gives a WRONG answer if the occurs check is removed? Pair 3 (P(x) ~ P(F(x))): it is wrongly "unified"; all other pairs behave identically.

### Lifted Modus Ponens demonstration

rule  King(x) ∧ Greedy(x) ⇒ Evil(x);  atoms: King(John), Greedy(y), King(Richard)  ⊢  ['Evil(John)', 'Evil(Richard)']   (first: θ = {x/John, y/John}; second: θ = {x/Richard, y/Richard} because Greedy(y) with a free y says everybody is greedy)

## 4B. Ground-clause growth (propositionalisation)

Ground instances of ONE rule with v variables over k constants (counted by generating them for k ≤ 12 or v ≤ 3; formula k^v beyond):

| k | v=1 | v=2 | v=3 | v=4 | predicate arity a=1 ground atoms | a=2 | a=3 | a=4 |
|---|---|---|---|---|---|---|---|---|
| 3 | 3 | 9 | 27 | 81 | 3 | 9 | 27 | 81 |
| 5 | 5 | 25 | 125 | 625 | 5 | 25 | 125 | 625 |
| 10 | 10 | 100 | 1,000 | 10,000 | 10 | 100 | 1,000 | 10,000 |
| 20 | 20 | 400 | 8,000 | 160,000 | 20 | 400 | 8,000 | 160,000 |
| 30 | 30 | 900 | 27,000 | 810,000 | 30 | 900 | 27,000 | 810,000 |

With function symbols the number of ground terms is infinite; with a depth bound d (k constants):

| depth bound d | 1 constant + unary F | 2 constants + unary F | 2 constants + binary G (counted) | binary recurrence T(d) = 2 + T(d-1)² |
|---|---|---|---|---|
| 0 | 1 | 2 | 2 | 2 |
| 1 | 2 | 4 | 6 | 6 |
| 2 | 3 | 6 | 38 | 38 |
| 3 | 4 | 8 | 1446 | 1,446 |
| 4 | 5 | 10 | not generated (too many) | 2,090,918 |

## 4C. Lifted vs propositional inference on the same query (Path(c1, ck) over a chain of k nodes)

KB: Edge(ci,ci+1) for i<k; Path(x,y) ⇐ Edge(x,y);  Path(x,z) ⇐ Edge(x,y) ∧ Path(y,z).

| k | lifted: unifications (no index) | lifted: unifications (indexed) | lifted time ms (indexed) | propositional: ground clauses | prop: rule checks to fixed point | prop: rule firings | prop time ms (grounding + inference) | both derive Path(c1,ck) |
|---|---|---|---|---|---|---|---|---|
| 5 | 50 | 18 | 0.3 | 150 | 600 | 10 | 0.2 | True |
| 10 | 200 | 38 | 0.5 | 1,100 | 9,900 | 45 | 3.8 | True |
| 20 | 800 | 78 | 1.5 | 8,400 | 159,600 | 190 | 46.0 | True |
| 30 | 1,800 | 118 | 2.4 | 27,900 | 809,100 | 435 | 215.5 | True |

---

## TASK 5 – First-order resolution

### Student A – conversion and proof design
All conversion steps (eliminate ⇒, move ¬ inward, standardise variables apart, Skolemise, drop ∀, distribute) are printed for S1–S4 in the evidence. **Skolem justification:** in S3 "some employee handled every audited document" the quantifier ∃e is not inside the scope of any ∀, so it is replaced by a Skolem **constant Sk1** (not a function); had it been ∀x ∃y …, y would become a function Sk(x). The query ∃x Authorised(x) is negated to ∀x ¬Authorised(x), the clause {¬Authorised(x)}. The proof (8 resolution steps, shown in the evidence with each unifier) goes: {¬Authorised(x)} with S1 → conditions on Employee, Document, Restricted, Handled; Employee(Sk1) fixes x/Sk1; S2 turns Restricted into ContainsPatientData and Document; S4 supplies R1; S3 supplies Handled(Sk1,R1) from Audited(R1); the empty clause results: **Authorised(Sk1)**, "the employee who handled every audited document is authorised". Implemented strategy: **set of support + unit preference**.

### Student B – comparative evidence
| strategy | clauses generated | unification attempts | proof length |
|---|---|---|---|
| none (breadth-first saturation) | 90 | 422 | 9 |
| unit preference | 39 | 49 | 9 |
| set of support | 42 | 103 | 7 |
| **sos + unit** | **21** | **24** | 8 |
(the evidence also lists steps, given clauses and times). The combined strategy needs 4.3× fewer clauses and 17.6× fewer unification attempts than uncontrolled resolution.
**Non-entailed second query** ∃x (Authorised(x) ∧ Audited(x)): on the original KB, which has only a Skolem constant, the prover **saturates and stops** (98 / 50 clauses for none / sos). After adding one axiom with a **function symbol** (Employee(m) ⇒ Employee(Mgr(m))) the same non-entailed query makes both strategies **run until the step cap** (715 and 574 generated clauses; the Herbrand universe is now infinite: Mgr(Sk1), Mgr(Mgr(Sk1)), …), while the entailed query is still proved in 23 clauses. **Comparison with Task 2:** on the equivalent small domain {Sk1, R1} grounding gives 14 ground clauses over 16 atoms; propositional resolution proves the goal with 21 clauses generated, the first-order prover with 21 as well (24 unifications, ≈ 10× the time per proof because unification is costly). With 4 constants the propositional KB has 32 clauses and needs 56 generated clauses, while the first-order proof stays at 21: **lifting pays off as the domain grows**, and costs a constant factor at small sizes.

### Cross-understanding
* **Student B – why Skolemisation preserves satisfiability but not logical equivalence.** ∃x P(x) and P(c) use different vocabularies. Every model of ∃x P(x) can be extended to a model of P(c) by interpreting c as a witness, so satisfiability is preserved; but P(c) ⊨ ∃x P(x) and not conversely (a model where P is true only of a, with c interpreted as b, satisfies the original and falsifies P(c)), so they are not equivalent. Resolution needs only the former: KB ∧ ¬Q is unsatisfiable iff its Skolemised form is.
* **Student A – cost of lifting and decidability.** The evidence shows unification as the added cost (24 unifications for a 21-clause proof) but fewer clauses as the domain grows. The non-entailed query shows that first-order entailment is only **semi-decidable**: if KB ⊨ α, resolution will find a proof; if KB ⊭ α, a KB with function symbols can make the search run forever (we had to stop it with a cap), and no algorithm decides every case.

### Evidence (program output, `t5_out.txt`)
## 5A. Conversion to CNF with Skolemisation (every step)

**S1 every employee who handled a restricted document is authorised**

1. original: `∀e ∀d ((Employee(?e) ∧ Document(?d) ∧ Restricted(?d) ∧ Handled(?e,?d)) ⇒ Authorised(?e))`
2. eliminate ⇒: `∀e ∀d (¬(Employee(?e) ∧ Document(?d) ∧ Restricted(?d) ∧ Handled(?e,?d)) ∨ Authorised(?e))`
3. move ¬ inward: `∀e ∀d ((¬Employee(?e) ∨ ¬Document(?d) ∨ ¬Restricted(?d) ∨ ¬Handled(?e,?d)) ∨ Authorised(?e))`
4. standardise variables apart: `∀e1 ∀d2 ((¬Employee(?e1) ∨ ¬Document(?d2) ∨ ¬Restricted(?d2) ∨ ¬Handled(?e1,?d2)) ∨ Authorised(?e1))`
5. Skolemise: `∀e1 ∀d2 ((¬Employee(?e1) ∨ ¬Document(?d2) ∨ ¬Restricted(?d2) ∨ ¬Handled(?e1,?d2)) ∨ Authorised(?e1))`
6. drop ∀ and distribute ∨ over ∧: `((¬Employee(?e1) ∨ ¬Document(?d2) ∨ ¬Restricted(?d2) ∨ ¬Handled(?e1,?d2)) ∨ Authorised(?e1))`
7. clauses: {¬Employee(?e1), ¬Document(?d2), ¬Restricted(?d2), ¬Handled(?e1,?d2), Authorised(?e1)}

**S2 every document containing patient data is restricted**

1. original: `∀d ((Document(?d) ∧ ContainsPatientData(?d)) ⇒ Restricted(?d))`
2. eliminate ⇒: `∀d (¬(Document(?d) ∧ ContainsPatientData(?d)) ∨ Restricted(?d))`
3. move ¬ inward: `∀d ((¬Document(?d) ∨ ¬ContainsPatientData(?d)) ∨ Restricted(?d))`
4. standardise variables apart: `∀d3 ((¬Document(?d3) ∨ ¬ContainsPatientData(?d3)) ∨ Restricted(?d3))`
5. Skolemise: `∀d3 ((¬Document(?d3) ∨ ¬ContainsPatientData(?d3)) ∨ Restricted(?d3))`
6. drop ∀ and distribute ∨ over ∧: `((¬Document(?d3) ∨ ¬ContainsPatientData(?d3)) ∨ Restricted(?d3))`
7. clauses: {¬Document(?d3), ¬ContainsPatientData(?d3), Restricted(?d3)}

**S3 some employee handled every audited document**

1. original: `∃e (Employee(?e) ∧ ∀d ((Document(?d) ∧ Audited(?d)) ⇒ Handled(?e,?d)))`
2. eliminate ⇒: `∃e (Employee(?e) ∧ ∀d (¬(Document(?d) ∧ Audited(?d)) ∨ Handled(?e,?d)))`
3. move ¬ inward: `∃e (Employee(?e) ∧ ∀d ((¬Document(?d) ∨ ¬Audited(?d)) ∨ Handled(?e,?d)))`
4. standardise variables apart: `∃e4 (Employee(?e4) ∧ ∀d5 ((¬Document(?d5) ∨ ¬Audited(?d5)) ∨ Handled(?e4,?d5)))`
5. Skolemise: `(Employee(Sk1) ∧ ∀d5 ((¬Document(?d5) ∨ ¬Audited(?d5)) ∨ Handled(Sk1,?d5)))`  — ∃e4 is replaced by the Skolem CONSTANT Sk1 (no universal quantifier encloses it)
6. drop ∀ and distribute ∨ over ∧: `(Employee(Sk1) ∧ ((¬Document(?d5) ∨ ¬Audited(?d5)) ∨ Handled(Sk1,?d5)))`
7. clauses: {Employee(Sk1)} ; {¬Document(?d5), ¬Audited(?d5), Handled(Sk1,?d5)}

**S4 R1 contains patient data and R1 was audited**

1. original: `(Document(R1) ∧ ContainsPatientData(R1) ∧ Audited(R1))`
2. eliminate ⇒: `(Document(R1) ∧ ContainsPatientData(R1) ∧ Audited(R1))`
3. move ¬ inward: `(Document(R1) ∧ ContainsPatientData(R1) ∧ Audited(R1))`
4. standardise variables apart: `(Document(R1) ∧ ContainsPatientData(R1) ∧ Audited(R1))`
5. Skolemise: `(Document(R1) ∧ ContainsPatientData(R1) ∧ Audited(R1))`
6. drop ∀ and distribute ∨ over ∧: `(Document(R1) ∧ ContainsPatientData(R1) ∧ Audited(R1))`
7. clauses: {Document(R1)} ; {ContainsPatientData(R1)} ; {Audited(R1)}

**Negated query** (query: ∃x Authorised(x)); its negation ∀x ¬Authorised(x) gives the clause {¬Authorised(x)}.

KB clauses: {¬Employee(?e1), ¬Document(?d2), ¬Restricted(?d2), ¬Handled(?e1,?d2), Authorised(?e1)} ; {¬Document(?d3), ¬ContainsPatientData(?d3), Restricted(?d3)} ; {Employee(Sk1)} ; {¬Document(?d5), ¬Audited(?d5), Handled(Sk1,?d5)} ; {Document(R1)} ; {ContainsPatientData(R1)} ; {Audited(R1)} 

## 5B. Proof that an authorised employee exists (strategy: set of support + unit preference)

Result: **PROVED**; proof steps (resolution steps in the proof tree): 8

```
{¬Document(_1), ¬Employee(_0), ¬Handled(_0,_1), ¬Restricted(_1)} <- resolve {¬Authorised(_0)}  with  {¬Document(_1), ¬Employee(_0), ¬Handled(_0,_1), ¬Restricted(_1), Authorised(_0)}   θ = {?x_6/?e1_6}
{¬Document(_0), ¬Handled(Sk1,_0), ¬Restricted(_0)}      <- resolve {¬Document(_1), ¬Employee(_0), ¬Handled(_0,_1), ¬Restricted(_1)}  with  {Employee(Sk1)}   θ = {?e1_6_15/Sk1}
{¬ContainsPatientData(_0), ¬Document(_0), ¬Handled(Sk1,_0)} <- resolve {¬Document(_0), ¬Handled(Sk1,_0), ¬Restricted(_0)}  with  {¬ContainsPatientData(_0), ¬Document(_0), Restricted(_0)}   θ = {?d2_6_15_22/?d3_22}
{¬ContainsPatientData(R1), ¬Handled(Sk1,R1)}            <- resolve {¬ContainsPatientData(_0), ¬Document(_0), ¬Handled(Sk1,_0)}  with  {Document(R1)}   θ = {?d3_22_55/R1}
{¬Handled(Sk1,R1)}                                      <- resolve {¬ContainsPatientData(R1), ¬Handled(Sk1,R1)}  with  {ContainsPatientData(R1)}   θ = {}
{¬Audited(R1), ¬Document(R1)}                           <- resolve {¬Handled(Sk1,R1)}  with  {¬Audited(_0), ¬Document(_0), Handled(Sk1,_0)}   θ = {?d5_79/R1}
{¬Audited(R1)}                                          <- resolve {¬Audited(R1), ¬Document(R1)}  with  {Document(R1)}   θ = {}
[] (empty clause)                                       <- resolve {¬Audited(R1)}  with  {Audited(R1)}   θ = {}
```

## 5C. Strategy comparison on the same query (kb clauses = 7)

| strategy | outcome | clauses generated | successful resolution steps | unification attempts | given clauses processed | proof length | time ms |
|---|---|---|---|---|---|---|---|
| none | PROVED | 90 | 422 | 422 | 89 | 9 | 56.2 |
| unit | PROVED | 39 | 49 | 49 | 18 | 9 | 2.8 |
| sos | PROVED | 42 | 103 | 103 | 39 | 7 | 12.9 |
| sos+unit | PROVED | 21 | 24 | 24 | 11 | 8 | 2.1 |

## 5D. A second query that is NOT entailed: ∃x (Authorised(x) ∧ Audited(x))  (clause {¬Authorised(x), ¬Audited(x)})

| KB | strategy | outcome | generated | steps | unification attempts | given |
|---|---|---|---|---|---|---|
| original (function-free apart from Skolem constant) | none | SATURATED (no proof exists) | 98 | 466 | 571 | 106 |
| original (function-free apart from Skolem constant) | sos | SATURATED (no proof exists) | 50 | 124 | 173 | 51 |
| + axiom Employee(m) ⇒ Employee(Mgr(m)) (a function symbol) | none | CAP HIT (gave up) | 715 | 5444 | 8900 | 681 |
| + axiom Employee(m) ⇒ Employee(Mgr(m)) (a function symbol) | sos | CAP HIT (gave up) | 574 | 1307 | 2397 | 562 |
| + Mgr axiom, ENTAILED query of 5B | sos+unit | PROVED | 23 | 26 | 26 | 11 |

## 5E. Comparison with the propositional prover of Task 2 on the equivalent small domain {Sk1, R1}

Grounding over 2 constants gives 14 distinct ground clauses over 16 atoms (vs 8 first-order clauses).
Propositional resolution (shortest-first): proved = True; clauses generated 21, resolvents attempted 21, subsumed 10, time 0.2 ms.
First-order resolution (sos+unit): proved = True; clauses generated 21, resolution steps 24, unification attempts 24, time 2.0 ms.
With 4 constants the propositional KB has 32 ground clauses and needs 56 clauses generated / 58 attempts; the first-order proof is unchanged (21 generated).

---

## TASK 6 – Forward and backward chaining
KB: organisation hierarchy (4-ary management tree), **10 definite-clause rules** (Manages, SameDept, Senior, CanApprove, Escalate, Approved, Peer, Conflict), about 100 / 1,000 / 10,000 facts (102 / 1,001 / 10,001 generated). Query: CanApprove(?m, r) for one request.

### Student A – forward chaining
Implemented to a fixed point (synchronous rounds). Results (evidence below): facts inferred **718 / 10,803 / 108,115**; rule firings 4,185 / 73,034 / 922,141; **redundant derivations 3,467 / 62,231 / 814,026 (83–88 % of firings)** because every round re-derives everything; iterations 6 / 7 / 9 (including the final no-change round). **Derived facts irrelevant to the query: 83.9–88.6 % by predicate (SameDept, Peer, Conflict, Escalate, Approved are not needed) and 98.6 / 99.87 / 99.98 % at fine grain** (only 10–25 derived facts lie on the chain of managers of the request). **When the query concerns a very small part of the KB** forward chaining's work does not shrink: it is proportional to the **whole KB** (the work grew ×17.4 and ×12.6 per ten-fold growth in facts) however little of it the query touches.

### Student B – backward chaining
Implemented with substitutions (renaming apart, unification, depth counter). For the same query: **23 / 29 / 41 goals expanded and 28 / 36 / 52 unifications**, max depth 5 / 6 / 8, 4 / 5 / 7 repeated subgoals: it grows with the **depth** of the hierarchy (log n), not with the number of facts. Without any indexing the same proofs need 448 / 5,429 / 77,817 unifications (the facts scanned grow with the KB). Compared with forward chaining (4,185 / 73,034 firings vs 28 / 36 unifications) this is a factor of ≈ 150 to 2,000.
**Left recursion.** Replacing the second Manages rule by the left-recursive form Manages(m,e) ⇐ Manages(m,x) ∧ ReportsTo(e,x) makes the first subgoal a *variant* of the goal being solved, so naive backward chaining loops: at 102 facts it spent its whole 5,000-goal budget (4,936 repeated subgoals) and at 1,001 facts likewise (4,404 repeated), returning no answer. (At 10,001 facts the 1,500-goal budget was exhausted *before* the recursion deepened because the unbound subgoal enumerates thousands of ReportsTo facts: that row shows the cost explosion but **does not by itself demonstrate non-termination**.) **Remedies and their cost:** a depth bound of 14 terminates and returns the same answers as the baseline but needs 843 goals (vs 12) at 102 facts and 12,539 (vs 15) at 1,001; **tabling** (memoising answers per variant subgoal and iterating to a fixpoint) terminates with identical answers, using 5,173 unifications at 102 facts and 846,164 at 1,001 (not run at 10,001: > 10⁷ expected). Both remedies cure non-termination but not the inefficiency: the left-recursive form forces the whole Manages relation to be computed. The best remedy is to **rewrite the rule right-recursively**.

### Verification questions
* **Student B – why is inference direction central here?** The KB has many facts and rules irrelevant to any one query (predicates irrelevant to the query, SameDept, Peer, Conflict, Escalate and Approved, account for 84–89 % of the derived facts), and each query names a specific request: goal-directed backward chaining touches only the chain of managers of that request, whereas forward chaining derives everything.
* **Student A – why does backward chaining stay efficient with many irrelevant facts?** Subgoals are unified only with facts that can match them (first-argument index), so facts about other employees are never examined: 10,001 facts needed 41 goals, only 18 more than 102 facts needed. (In the opposite situation, a KB with many queries over the same facts and few distinct derivations needed, forward chaining or tabling amortises better.)

### Evidence (program output, `t6_out.txt`)
## 6A. Student A - forward chaining to a fixed point (all 10 rules)

| facts | employees | facts inferred | rule firings | redundant derivations | iterations (incl. final no-change round) | irrelevant derived facts, predicate-level | irrelevant, fine-grained | time s |
|---|---|---|---|---|---|---|---|---|
| 102 | 31 | 718 (Approved 2, CanApprove 13, Conflict 28, Escalate 7, Manages 66, Peer 116, SameDept 481, Senior 5) | 4,185 | 3,467 | 6 | 88.3 % | 98.61 % (10 relevant) | 0.01 |
| 1,001 | 297 | 10,803 (Approved 2, CanApprove 147, Conflict 296, Escalate 74, Manages 1,076, Peer 1,184, SameDept 8,019, Senior 5) | 73,034 | 62,231 | 7 | 88.6 % | 99.87 % (14 relevant) | 0.22 |
| 10,001 | 2,964 | 108,115 (Approved 2, CanApprove 1,479, Conflict 2,960, Escalate 740, Manages 15,966, Peer 11,849, SameDept 75,114, Senior 5) | 922,141 | 814,026 | 9 | 83.9 % | 99.98 % (25 relevant) | 3.03 |

## 6B. Student B - backward chaining on the same KB, query CanApprove(?m, r) for one request r (deep in the tree)

| facts | request | answers | goals expanded | unifications | max depth | repeated subgoals | time ms | FC firings for comparison |
|---|---|---|---|---|---|---|---|---|
| 102 | r28 | ['e0', 'e1'] | 23 | 28 | 5 | 4 | 0.74 | 4185 |
| 1,001 | r296 | ['e0', 'e4'] | 29 | 36 | 6 | 5 | 0.52 | 73034 |
| 10,001 | r2960 | ['e0', 'e2'] | 41 | 52 | 8 | 7 | 0.79 | (6A) |

Same query with NO indexing of facts (shows what indexing saves):

| facts | goals expanded | unifications | time ms |
|---|---|---|---|
| 102 | 23 | 448 | 1.0 |
| 1,001 | 29 | 5,429 | 7.3 |
| 10,001 | 41 | 77,817 | 95.2 |

## 6C. A left-recursive rule on which naive backward chaining never terminates

Replace R2 by the left-recursive  Manages(m,e) ⇐ Manages(m,x) ∧ ReportsTo(e,x).  Query: Manages(?m, e) for the owner e of the request.

| facts | method | outcome | answers | goals expanded | unifications | max depth | repeated subgoals | time ms |
|---|---|---|---|---|---|---|---|---|
| 102 | right-recursive baseline (R2 as before) | terminates | 3 | 12 | 14 | 4 | 4 | - |
| 102 | naive BC, left-recursive | NEVER TERMINATES: stopped by the 5,000-goal budget | 0 | 5001 | 145873 | 76 | 4936 | 434 |
| 102 | remedy 1: depth bound 14 | terminates (depth bound 14); answers = baseline: True | 3 | 843 | 22867 | 15 | 779 | 50 |
| 102 | remedy 2: tabling (memoised answers) | terminates; answers = baseline: True | 3 | 6 table evaluations, 2 passes | 5,173 | - | - | 11 |
| 1,001 | right-recursive baseline (R2 as before) | terminates | 4 | 15 | 18 | 5 | 5 | - |
| 1,001 | naive BC, left-recursive | NEVER TERMINATES: stopped by the 5,000-goal budget | 0 | 5001 | 1158865 | 8 | 4404 | 2094 |
| 1,001 | remedy 1: depth bound 14 | terminates (depth bound 14); answers = baseline: True | 4 | 12539 | 3388827 | 15 | 11943 | 5679 |
| 1,001 | remedy 2: tabling (memoised answers) | terminates; answers = baseline: True | 4 | 8 table evaluations, 3 passes | 846,164 | - | - | 1147 |
| 10,001 | right-recursive baseline (R2 as before) | terminates | 6 | 21 | 26 | 7 | 7 | - |
| 10,001 | naive BC, left-recursive | NEVER TERMINATES: stopped by the 1,500-goal budget | 0 | 1501 | 2997 | 2 | 0 | 13 |
| 10,001 | remedy 1: depth bound 14 | budget (1,500 goals) exceeded; answers = baseline: None | 0 | 1501 | 2997 | 2 | 0 | 35 |
| 10,001 | remedy 2: tabling | NOT RUN at this size: cost grew x164 from 102 to 1,001 facts (5,173 -> 846,164 unifications), i.e. > 10^7 unifications here | - | - | - | - | - | - |

---

# DAY-4 DESIGN CHALLENGE
## TASK 7 – A knowledge-based reasoning component from first principles: Hospital Medication-Safety Advisor
**Safety notice:** the 40 base rules use eight real drug names purely for readability and are **illustrative, not clinical advice**; larger KBs add synthetic drugs (D0001…) with no medical content only to scale the rule count.

### Stage 1 – two independent design proposals (both written by me, from different starting assumptions)
* **Proposal 1 (propositional + resolution).** Symbols such as `allergic_penicillin_patient17`, one symbol per patient × fact, rules as ground implications, inference by resolution refutation; explanation = the clauses of the resolution proof. Rationale: simplest logic, complete for any propositional rule.
* **Proposal 2 (FOL Horn clauses + backward chaining).** Vocabulary Age(p,band), Allergy(p,a), Takes(p,d), HasCondition(p,c), Unsafe(p,d,reason); rules are lifted over patients; inference by backward chaining from the goal Unsafe(p, newdrug, ?r); explanation = the rule(s) that fired and the patient facts they used.

### Stage 2 – comparison
| aspect | Proposal 1 | Proposal 2 |
|---|---|---|
| agrees | rules are definite implications; goal-directed query; explanation from derivation | same |
| rule base size | ground rules × 50,000 patients (≈ 10⁸ clauses for 2,000 rules) | 2,000 rules, patient data as facts |
| inference cost (Task 2 evidence) | resolution can blow up on non-Horn structure; needs a KB per patient | Horn: linear-time behaviour, indexed lookups |
| explanation | proof tree of clauses (hard to read) | "rule X fired because facts Y, Z" |
| retained | **FOL rules + data as facts (2)**, completeness check and the "unknown" handling from the careful reading of (1) | |

### Stage 3 – joint final design
**Representation:** function-free FOL Horn clauses (Datalog). **Vocabulary:** Age, Allergy, Takes, HasCondition (patient facts), Covered(d), Unsafe(p,d,reason). **Rules:** each safety rule is `Unsafe(?p, D, rid) ⇐ body` (body = Allergy / Takes / HasCondition / Age atoms, ≤ 2 atoms), covering six kinds: allergy, interaction, condition, age band, duplicate therapy, two-factor combination. **Inference:** backward chaining with **rule index on the drug argument** and **fact index on the patient argument**. **Scale:** an indexing strategy rather than an agenda: only the ≈ 10 rules for the prescribed drug are tried and patient facts are fetched by hash. **Explanation:** for each reason, instantiate the rule that proved it and list the supporting patient facts. **Completeness of data:** verdicts INSUFFICIENT DATA (no Age fact), UNKNOWN DRUG (no rule covers it), UNSAFE, NO KNOWN CONTRAINDICATION (never "safe").
```
advise(p, d):
   if not ask(Age(p,?a)):      return INSUFFICIENT DATA
   if not ask(Covered(d)):     return UNKNOWN DRUG
   reasons = { r : ask(Unsafe(p, d, ?r)) }            # rules fetched by index on d, facts by index on p
   explanation = [ (rule r, instantiated body facts) for r in reasons ]
   return UNSAFE(reasons, explanation) if reasons else NO KNOWN CONTRAINDICATION
```

### Stage 4 – validation
**Student A – theoretical validation.**
* *Soundness.* Each backward-chaining step is lifted Modus Ponens (universal instantiation + Modus Ponens), which is sound (Task 4), so every reported reason is entailed by the rules and the patient record.
* *Completeness.* The safety rules are non-recursive (all heads are `Unsafe`, all bodies use only data predicates) and function-free, so the Herbrand base is finite and backward chaining always terminates; for definite clauses it finds every answer (the KB has a least model).
* *Complexity of a query as a function of KB size.* With the rule index: O(r_d · b), where r_d is the number of rules for the prescribed drug (≈ R/#drugs, ≈ 10 here) and b ≤ 2 the body size, each patient-fact lookup being O(1): **independent of the total number of rules R and patients**. Without the rule index: O(R) head unifications; forward chaining per query: O(R·b) rule applications plus the derivation of unsafe-reasons for **all** drugs.
* *Effect of restricting to definite clauses.* Entailment of Horn clauses is linear-time (propositional) / polynomial in the data (Datalog) while general propositional entailment is co-NP-complete and first-order entailment only semi-decidable (Task 5). The restriction costs expressiveness: no disjunction ("allergic to A *or* B"), no genuine negation (only negation as failure, hence the closed-world risk handled by INSUFFICIENT DATA).

**Student B – experimental validation** (`a3_t7.py`; 50,000 synthetic patients with 208,441 facts; **31 hand-built test cases** with expected answers written beforehand: 12 dangerous combinations, 10 safe, 9 edge cases (no record, unknown drug, polypharmacy, age bands, duplicates); KB sizes 40, 400, 2,000 rules; **300 random patient-drug queries per size compared with an independent oracle**).
* **Correctness:** 31/31 cases and 300/300 oracle checks at every size, and forward chaining also returned the right reason sets in 30/30 cases.
* **Latency:** indexed backward chaining **0.14 → 0.14 → 0.16 ms** for 40 → 400 → 2,000 rules (flat); the same program with the rule index switched off: 0.45 → 3.44 → **20.7 ms** (linear in R); per-query forward chaining 0.1 → 1.0 → 5.0 ms (linear in R); no indexing at all ≈ **1,047 ms** per query (≈ 650,000 unifications).
* **Inference steps:** a constant **12.4 unifications and 8.5 goals per query** at all three sizes (unindexed: 44 → 381 → 1,878).
* **Memory:** about 35–36 MB for the patient data and rules (dominated by the 208,441 patient facts, so it barely grows with the rules); build time 0.5–0.7 s.
* **Explanation length:** mean 3.8 lines per unsafe verdict (2 per reason), at most 15 (the polypharmacy patient, 7 reasons).
* **Baseline comparison** is in the table; the chosen design is the only one whose cost does not grow with the KB.

### Stage 5 – cross-defence
* **Student A explains the experimental evidence:** flat 0.14–0.16 ms latency and a constant 12.4 unifications per query across a 50× increase in rules, against linear growth without the rule index, show that indexing makes the query cost depend on the rules for **one drug**, not on R.
* **Student B explains why the theoretical result applies:** the O(r_d·b) bound assumes that the rules for the queried drug are found directly and that patient facts are hash-indexed; the engine's `Unsafe` rules are keyed on the drug argument (position 2) and facts on the patient argument, so the measured count (≈ 10 rules × 1–2 lookups) is that bound; the 400→2,000 growth in r_d is small because the generator adds drugs, not rules per drug.

### Stage 6 – joint evaluation
*Why a logical agent suits the problem:* the knowledge is rule-like and exists as written guidelines, **explanations are mandatory** in a clinical setting (the proof is the explanation), rules change often and must be auditable, and correctness of each rule can be tested. *Limits:* **uncertainty** (probabilities, dose-dependence, severity grades are not represented), **incomplete data** (negation as failure treats "not recorded" as "absent": reduced here by INSUFFICIENT DATA/UNKNOWN DRUG verdicts, but a missing allergy record is still a risk), knowledge acquisition effort (2,000 rules must be curated), and conflicts between rules. *Before choosing a knowledge-based approach an AI designer should check:* whether the domain knowledge is explicit and stable enough to write down; whether queries are mostly specific and goal-directed (favouring backward chaining) or bulk; whether explanations or guarantees are required; how much data is missing or uncertain; the size of the KB and the number of queries (indexing and direction); and whether a hybrid with statistical methods is needed for the uncertain part.

### Evidence (program output, `t7_out.txt`)
## 7B. Experimental validation. 50,000 patients, 208,441 patient facts (seed 5), built in 0.4 s

### 7B-1. The 31 hand-built test cases on the 2,000-rule KB (expected vs actual; all three sizes are summarised below)

| case | expected verdict | actual verdict | expected reasons | actual reasons | explanation lines | pass | latency ms |
|---|---|---|---|---|---|---|---|
| D01 warfarin + new aspirin | UNSAFE | UNSAFE | interaction:aspirin:warfarin | interaction:aspirin:warfarin | 2 | ✓ | 0.32 |
| D02 sertraline + new tramadol | UNSAFE | UNSAFE | interaction:tramadol:sertraline | interaction:tramadol:sertraline | 2 | ✓ | 0.26 |
| D03 penicillin allergy + amoxicillin | UNSAFE | UNSAFE | allergy:amoxicillin:penicillin_allergy | allergy:amoxicillin:penicillin_allergy | 2 | ✓ | 0.12 |
| D04 renal failure + ibuprofen | UNSAFE | UNSAFE | condition:ibuprofen:renal_failure | condition:ibuprofen:renal_failure | 2 | ✓ | 0.19 |
| D05 child + aspirin | UNSAFE | UNSAFE | age:aspirin:child | age:aspirin:child | 2 | ✓ | 0.22 |
| D06 elderly on warfarin + aspirin | UNSAFE | UNSAFE | combo:aspirin:bleed_elderly, interaction:aspirin:warfarin | combo:aspirin:bleed_elderly, interaction:aspirin:warfarin | 5 | ✓ | 0.19 |
| D07 bleeding disorder + warfarin | UNSAFE | UNSAFE | condition:warfarin:bleeding_disorder | condition:warfarin:bleeding_disorder | 2 | ✓ | 0.14 |
| D08 pregnancy + lisinopril | UNSAFE | UNSAFE | condition:lisinopril:pregnancy | condition:lisinopril:pregnancy | 2 | ✓ | 0.09 |
| D09 epilepsy + tramadol | UNSAFE | UNSAFE | condition:tramadol:epilepsy | condition:tramadol:epilepsy | 2 | ✓ | 0.14 |
| D10 already on ibuprofen + ibuprofen | UNSAFE | UNSAFE | duplicate:ibuprofen:same_drug | duplicate:ibuprofen:same_drug | 2 | ✓ | 0.22 |
| D11 lisinopril + renal failure + ibuprofen | UNSAFE | UNSAFE | combo:ibuprofen:nephro, condition:ibuprofen:renal_failure, interaction:ibuprofen:lisinopril | combo:ibuprofen:nephro, condition:ibuprofen:renal_failure, interaction:ibuprofen:lisinopril | 7 | ✓ | 0.20 |
| D12 ulcer + warfarin + NSAID allergy + ibuprofen | UNSAFE | UNSAFE | allergy:ibuprofen:nsaid_allergy, condition:ibuprofen:peptic_ulcer, interaction:ibuprofen:warfarin | allergy:ibuprofen:nsaid_allergy, condition:ibuprofen:peptic_ulcer, interaction:ibuprofen:warfarin | 6 | ✓ | 0.28 |
| S01 healthy adult + metformin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.13 |
| S02 on lisinopril + amoxicillin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.11 |
| S03 penicillin allergy + aspirin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.22 |
| S04 on sertraline + metformin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.12 |
| S05 elderly + lisinopril | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.09 |
| S06 child + amoxicillin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.09 |
| S07 on aspirin + sertraline | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.08 |
| S08 epilepsy + aspirin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.17 |
| S09 on metformin + ibuprofen | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.22 |
| S10 pregnancy + amoxicillin | NO KNOWN CONTRAINDICATION | NO KNOWN CONTRAINDICATION | - | - | 0 | ✓ | 0.10 |
| E01 no record at all + aspirin | INSUFFICIENT DATA | INSUFFICIENT DATA | - | - | 0 | ✓ | 0.01 |
| E02 elderly on aspirin + warfarin | UNSAFE | UNSAFE | combo:warfarin:bleed_elderly, interaction:warfarin:aspirin | combo:warfarin:bleed_elderly, interaction:warfarin:aspirin | 5 | ✓ | 0.15 |
| E03 drug without any rule | UNKNOWN DRUG | UNKNOWN DRUG | - | - | 0 | ✓ | 0.02 |
| E04 NSAID allergy + aspirin | UNSAFE | UNSAFE | allergy:aspirin:nsaid_allergy | allergy:aspirin:nsaid_allergy | 2 | ✓ | 0.18 |
| E05 polypharmacy elderly + ibuprofen | UNSAFE | UNSAFE | age:ibuprofen:elderly, allergy:ibuprofen:nsaid_allergy, combo:ibuprofen:nephro, condition:ibuprofen:peptic_ulcer, condition:ibuprofen:renal_failure, interaction:ibuprofen:lisinopril, interaction:ibuprofen:warfarin | age:ibuprofen:elderly, allergy:ibuprofen:nsaid_allergy, combo:ibuprofen:nephro, condition:ibuprofen:peptic_ulcer, condition:ibuprofen:renal_failure, interaction:ibuprofen:lisinopril, interaction:ibuprofen:warfarin | 15 | ✓ | 0.33 |
| E06 elderly on sertraline + tramadol | UNSAFE | UNSAFE | age:tramadol:elderly, interaction:tramadol:sertraline | age:tramadol:elderly, interaction:tramadol:sertraline | 4 | ✓ | 0.19 |
| E07 child + tramadol | UNSAFE | UNSAFE | age:tramadol:child | age:tramadol:child | 2 | ✓ | 0.13 |
| E08 renal failure on lisinopril + metformin | UNSAFE | UNSAFE | combo:metformin:lactic, condition:metformin:renal_failure | combo:metformin:lactic, condition:metformin:renal_failure | 5 | ✓ | 0.10 |
| E09 adult on warfarin + amoxicillin + liver disease | UNSAFE | UNSAFE | combo:amoxicillin:inr_liver | combo:amoxicillin:inr_liver | 3 | ✓ | 0.12 |

Example explanation (case D11, 2,000-rule KB):

```
Unsafe(T10,ibuprofen) because rule combo:ibuprofen:nephro fires:
    Takes(T10,lisinopril)  [fact in record]
    HasCondition(T10,renal_failure)  [fact in record]
Unsafe(T10,ibuprofen) because rule condition:ibuprofen:renal_failure fires:
    HasCondition(T10,renal_failure)  [fact in record]
Unsafe(T10,ibuprofen) because rule interaction:ibuprofen:lisinopril fires:
    Takes(T10,lisinopril)  [fact in record]
```

### 7B-2. Metrics by KB size

| rules | drugs covered | build time s | memory MB (patients + rules) | test cases passed | mean latency ms (indexed BC) | max latency ms | mean unifications / query | mean goals / query | mean explanation lines (cases with reasons) | oracle agreement (300 random) |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 8 | 0.53 | 35 | 31/31 | 0.14 | 0.33 | 12.4 | 8.5 | 3.8 | 300/300 |
| 400 | 44 | 0.72 | 35 | 31/31 | 0.14 | 0.34 | 12.4 | 8.5 | 3.8 | 300/300 |
| 2,000 | 204 | 0.68 | 36 | 31/31 | 0.16 | 0.33 | 12.4 | 8.5 | 3.8 | 300/300 |

### 7B-3. Baseline comparison (mean per query over the same test cases)

| rules | design: indexed BC ms | baseline 1: rules not indexed ms (unifications) | baseline 2: nothing indexed, one case, ms (unifications) | baseline 3: forward chaining per query ms (rule firings) | FC answers correct |
|---|---|---|---|---|---|
| 40 | 0.14 | 0.45 (44) | 1049 (648,980) | 0.1 (7) | 30/30 |
| 400 | 0.14 | 3.44 (381) | 1047 (649,376) | 1.0 (24) | 30/30 |
| 2,000 | 0.16 | 20.72 (1878) | 1047 (651,136) | 5.0 (70) | 30/30 |

---

## CONTRIBUTION RECORD (solo submission)
| Task | Student A – primary contribution | Student B – primary contribution | Joint work |
|---|---|---|---|
| 1–7 | Done by the single author | Done by the single author | There is no partner; all shared work was done by the author |

*(I confirmed with my instructor that a solo submission is acceptable.)* — **delete this line unless it is true.**

## Limitations
Single machine, single run for timings (break-even values in Task 3 are indicative); one random graph/KB per size; the Task 7 rules are illustrative and synthetic beyond the first 40; the Task 3 draft KB v0 is my own first draft kept for the defect log; non-termination in Task 6 is established at 102 and 1,001 facts only (see the note on the 10,001 row).
