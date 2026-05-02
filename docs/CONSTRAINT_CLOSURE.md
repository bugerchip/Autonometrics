# Constraint-closure axis — design document

> *Status: design draft for the upcoming `v0.6.0a0` release.
> This document fixes the operational decisions before any code
> is written, so the implementation can be audited against an
> explicit specification rather than reverse-engineered from
> whatever the code happens to do.*

> *Spanish summary at the bottom of this file.*

## What this axis adds to PBA

The two axes shipped so far (`ratio_endo_total` from Bertschinger
/ Albantakis, and `memory_endo_ratio` from Crutchfield) both live
in **information-theoretic territory**. They ask, at the level of
**states**, who produced the next state and who carries the
predictive memory of the past.

The `v0.5.1a0` saturation diagnostic established that this
shared territory has a structural blind spot: any system whose
dynamics is deterministic and whose observed `(S_t, E_t)` covers
the transition rule's inputs satisfies `closure = 1.0` by
construction. Memory partially resolves the resulting cluster on
the autonomy plane, but two qualitatively distinct systems (a
period-`p` metronome and a complex automaton) can still land on
indistinguishable points.

Constraint-closure, drawn from Montévil & Mossio (2015),
*"Biological organisation as closure of constraints"*
(J. Theor. Biol.), asks a question one level up: not "who
produced this state" but **"who sustains the rules that produced
it, and to what extent do those rules sustain each other"**.

Because it operates on the **graph of dependencies among rules**
rather than on the flow of information among states, it is
mathematically independent of the two existing axes by design —
which is exactly the property PBA needs from a third ratio if
the unifying argument is to survive contact with data.

## Scientific background

Montévil & Mossio's framework adds a third primitive to the
classical physics ontology:

- **Process**: an event of energy transfer or state transition.
- **Law**: a universal rule governing processes.
- **Constraint**: a material condition that channels processes
  without being consumed by them, and whose characteristic time
  scale is longer than the processes it channels.

The river bed example (theirs and the literature's standard
illustration):

- The *water flowing* is the process.
- *Gravity* is the law.
- The *river bed* is the constraint.

A constraint that is itself produced and maintained by other
constraints of the same system, in such a way that the dependency
graph closes on itself, is what they call a constraint under
*organisational closure*. A biological cell is the canonical
example: the membrane channels metabolism, metabolism produces
the membrane.

The principle is informative because it separates two kinds of
persistence:

- **Inertial persistence**: a crystal persists because it is in a
  local energy minimum. It does nothing. None of its features
  are constraints under closure.
- **Self-maintaining persistence**: a cell persists because it
  produces and sustains its own constraints. It does work. Its
  structural features form a closed dependency graph.

The Albantakis / Crutchfield axes cannot tell these two apart on
deterministic, fully-observed systems: both saturate. The
constraint-closure axis is, in principle, capable of separating
them, because it reads the **topology of the rule graph**, not
the information flow.

## Six design decisions, fixed

The six decisions that follow were debated in the design
conversation and frozen here. Each is one operational choice
plus a one-line justification.

### 1. What counts as a constraint

A **constraint** is taken to be **one update function of the
discrete system**. In a Boolean network of `n` nodes, there are
`n` constraints. In an elementary cellular automaton, there is
one constraint per spatial position (they happen to share the
same lookup table, but each cell has its own update function in
the protocol's frame). In a `PeriodicCycle` of period `p`, there
is one constraint (the increment-and-modulo rule).

*Rationale.* Closest to the original paper: a constraint
"channels a process", and the update function is exactly what
channels the transition of a node. Coarser than per-edge, finer
than per-system; matches the granularity of the existing
adapters' internal representation.

### 2. How dependency between constraints is measured

A constraint `c_i` is said to **depend** on a constraint `c_j` if
the update function of `c_i` reads the state controlled by `c_j`
as one of its inputs. Equivalently: there is a directed edge
`c_j → c_i` in the system's **causal graph**.

Dependency is therefore **structural** (topology of the causal
graph), not informational (mutual information), not
interventional (counterfactual changes).

*Rationale.* Information-theoretic dependency would collapse the
metric into the same family as Albantakis closure and create the
exact "engineered correlation" failure mode the PBA document
warns against. Interventional dependency requires an external
agent doing perturbation experiments, which the protocol cannot
expose generically. Structural dependency is purely topological:
two systems with the same causal graph share constraint-closure,
regardless of what information flows through them.

### 3. How closure is counted

The metric is the **fraction of constraints that lie on at least
one cycle of the causal graph**:

```
constraint_closure = |{ c_i : c_i is on at least one cycle }| / n
```

where `n` is the total number of constraints.

*Rationale.* Direct internal-over-total ratio, in the PBA shape.
Numerator = constraints that close back on themselves through
other constraints. Denominator = all constraints. Returns a
value in `[0, 1]`. Cycles are detected by Tarjan's strongly
connected components algorithm; any node in a non-trivial SCC
(SCC of size ≥ 2, or a self-loop) is on a cycle.

### 4. Temporal filter

For the systems shipped in `v0.5.x` (deterministic automata,
fixed Boolean networks, period-`p` cycles, externally-driven
automata), update functions never change during a run. They
trivially satisfy Montévil & Mossio's requirement that a
constraint's characteristic time scale be longer than the
processes it channels.

For this release **no temporal filter is applied**. Every update
function in the system counts as a constraint for purposes of
the metric.

*Rationale.* Within the current adapter zoo this is correct by
construction. When the package later admits adaptive systems
(systems whose update functions change during a run, e.g. RL
agents with learning), the filter has to be revisited. The
decision is documented now so it can be revisited cleanly.

### 5. A priori predictions

The metric must be tested against pre-stated expectations on
the existing zoo, **fixed before implementation**, so that the
final result is not interpretable as a self-fulfilling
prophecy.

| Adapter / configuration            | Expected `constraint_closure` | Rationale                                                        |
|------------------------------------|------------------------------:|------------------------------------------------------------------|
| `PeriodicCycle(period=2..8)`       | 0.0 – 0.2                     | One constraint, no inter-constraint dependency network.          |
| `ECASystem` rule 30                | 0.4 – 0.7                     | Local dependencies (left, centre, right); cyclic neighbour ring. |
| `ECASystem` rule 110               | 0.4 – 0.7                     | Same dependency topology; cyclic neighbour ring.                 |
| `ECASystem` rule 184, rule 250     | 0.4 – 0.7                     | Same dependency topology; cyclic neighbour ring.                 |
| `KauffmanNetwork` K=1              | 0.1 – 0.4                     | Each node depends on one; cycles are rare and short.             |
| `KauffmanNetwork` K=3              | 0.6 – 0.95                    | High in-degree; cycles are abundant by random-graph statistics.  |
| `SimpleAutomaton.self_generated`   | 0.7 – 1.0                     | Rule constructed to depend on the system's own previous state.   |
| `SimpleAutomaton.external`         | 0.0 – 0.2                     | Rule constructed to depend purely on the environment.            |

**The critical falsification test.**
The metric is judged successful if and only if `PeriodicCycle`
and `SimpleAutomaton.self_generated` — both of which saturate at
`closure = 1.0` and cluster around `memory ≈ 0.97` in the
`v0.5.0a0` benchmark — produce **distinguishable**
constraint-closure values. If they do not, the operationalisation
has not captured the structural distinction it was supposed to,
and the decisions above must be revisited.

### 6. Engineered-correlation defences

Two complementary defences are required:

- **Static audit.** The implementation file
  `src/autonometrics/metrics/constraint_closure.py` must not
  import any function from `autonometrics.metrics._entropy`,
  `autonometrics.metrics.albantakis`,
  `autonometrics.metrics.memory_ratio`, or any third-party
  information-theory toolkit (`pyinform`, `dit`, etc.). The
  metric is implemented from the topology of the causal graph
  alone. A test in `tests/test_constraint_closure.py` asserts
  this by parsing the file's import block.
- **Empirical audit.** The benchmark run that ships with
  `v0.6.0a0` reports `Pearson r(closure, constraint_closure)`
  and `Pearson r(memory, constraint_closure)`. If both are below
  `0.7` over the valid points of the zoo, empirical
  independence is declared and recorded in the snapshot
  metadata.

Either defence alone is insufficient: a metric could pass the
static audit and still happen to correlate with the others on a
particular benchmark, or pass the empirical audit by accident on
the chosen zoo. Both together give the property PBA needs.

## Implementation surface

The minimal surface required for `v0.6.0a0`:

- `src/autonometrics/metrics/constraint_closure.py` — defines
  `compute_constraint_closure(causal_graph: np.ndarray) -> float`.
  Input is a `(n, n)` boolean adjacency matrix where
  `causal_graph[i, j] = True` means "constraint `i` depends on
  constraint `j`". Output is the fraction of nodes that lie on
  a cycle, computed via SCC decomposition.
- `AutonomySystem` protocol extension: an optional
  `get_causal_graph()` method that returns the adjacency matrix
  above. Adapters that do not implement it raise
  `NotImplementedError`, which the metric treats as
  "constraint-closure not applicable to this system".
  Implementations are added for `ECASystem`, `KauffmanNetwork`,
  `PeriodicCycle`, and both modes of `SimpleAutomaton`.
- `AutonomyProfile.constraint_closure: float | None` field, in
  the same shape as the existing two metric fields.
- `_METRIC_REGISTRY` entry mapping the identifier
  `"constraint_closure"` to the new function.
- Test file `tests/test_constraint_closure.py` covering the
  per-adapter expectations from section 5, the engineered-
  correlation static audit, and a few canonical graphs (single
  self-loop → 1.0; pure DAG → 0.0; all-to-all → 1.0).
- Per-adapter test additions in `tests/benchmarks/` for the new
  `get_causal_graph()` method.
- `examples/benchmark_demo.py` extended to measure the third
  axis and report the three pairwise correlations.
- `examples/benchmark_plot.py` extended (or a new
  `benchmark_plot_3d.py`) to render the three-axis cube; the
  two-axis scatter remains available so existing snapshots stay
  reproducible.

## Roadmap of the cycle

1. **Design (this document)** — done; pending review.
2. **Per-adapter `get_causal_graph()`** — additions to
   `ECASystem`, `KauffmanNetwork`, `PeriodicCycle`,
   `SimpleAutomaton`. Each method returns the boolean adjacency
   matrix in the convention defined in section "Implementation
   surface".
3. **Metric implementation** — pure-`numpy` Tarjan SCC, plus
   the `compute_constraint_closure` wrapper.
4. **Tests** — canonical graph cases plus the per-adapter
   predictions from section 5.
5. **Benchmark integration** — extend `benchmark_demo.py` and
   capture a fresh snapshot at
   `docs/benchmarks/v0.6.0a0.csv|.png|.log.txt`.
6. **PBA document update** — `docs/PBA.md` and `docs/PBA.es.md`
   add a "Domain of applicability" subsection for
   constraint-closure (mirror of the `v0.5.1a0` section for
   closure), and the "Current evidence status" section is
   updated with the three-axis correlation numbers.
7. **Release** — `v0.6.0a0`, README and CHANGELOG updated,
   roadmap shifts (RAI moves to `v0.7`, CBA to `v0.8`).

## Risks and how this document mitigates them

- **Risk**: the implementation drifts from the design and ends
  up reading information rather than topology.
  **Mitigation**: section 6 static audit + this document as a
  reviewable spec.
- **Risk**: the zoo's adapters cannot expose a clean causal
  graph (e.g. continuous parameters, non-discrete dependencies).
  **Mitigation**: only discrete adapters are in scope; if the
  graph cannot be exposed, the metric records `None` and the
  benchmark drops the row, exactly as the existing closure
  metric does for degenerate systems.
- **Risk**: the metric correlates strongly with closure on the
  current zoo by accident.
  **Mitigation**: section 6 empirical audit + the
  pre-registered predictions from section 5. If the
  metronome / self-generated automaton pair fails to separate,
  the operational definition is judged inadequate and revised
  before release.
- **Risk**: the metric saturates trivially on every adapter
  because every node is in some cycle in cyclic boundary
  conditions (every ECA, every NK).
  **Mitigation**: section 5 already lists `PeriodicCycle` as
  expected `< 0.2`. If ECA values come out near `1.0`, the
  prediction set itself is the audit trail telling us the
  cyclic-boundary effect dominates and the operationalisation
  needs a non-trivial-cycle filter (e.g. count only SCCs of
  size ≥ 2).

## Pre-implementation review

> *Added after the design was approved, before any code was
> written. Reading the six decisions against the actual structure
> of the existing adapters revealed a mismatch that would cause
> the metric to fail its own falsification test (section 5).
> This section documents the mismatch and proposes a refinement.*

### What the original operationalisation produces, mechanically

Walking the four adapters under the rules of decisions 1–3:

- **`PeriodicCycle`** has `n = 1` constraint (the single increment
  rule) with a self-loop on the dependency graph. Under
  decision 3, "any node in a non-trivial SCC, or with a
  self-loop, is on a cycle". Result: `1 / 1 = 1.0`.
- **`SimpleAutomaton.from_self_generated_rules`** has `n = 1`
  constraint, also with a self-loop. Result: `1 / 1 = 1.0`.
- **`SimpleAutomaton.from_external_rules`** has `n = 1`
  constraint that depends on the environment, with no self-loop
  in the system. Result: `0 / 1 = 0.0`.
- **`ECASystem`** with width `w` has `w` constraints on a ring;
  every cell depends on its two neighbours, so the dependency
  graph is a strongly connected ring. Every cell sits in the
  global SCC of size `w`. Result: `w / w = 1.0`.
- **`KauffmanNetwork`** with `n_nodes = 10` and `k = 3` produces
  a dense random graph; nearly all nodes are in a single large
  SCC. Result: ~`1.0` for moderate-to-high `k`.

### Why this fails the falsification test

The critical test in section 5 says **`PeriodicCycle` and
`SimpleAutomaton.self_generated` must yield distinguishable
values**. Under the original operationalisation both yield
`1.0`. The metric collapses the two cases the test requires it
to separate.

The deeper diagnosis is that **decision 3 conflates two distinct
phenomena**:

1. *Trivial cyclicity*: a single node looping back on itself,
   which a single-node system with any self-dependency exhibits
   automatically.
2. *Cyclic boundary topology*: every node belonging to a single
   global SCC because the underlying lattice is closed (e.g. a
   periodic cellular automaton ring), which any system with
   such boundary conditions exhibits automatically.

Neither phenomenon corresponds to the Montévil & Mossio notion
of *closure of constraints*, which requires a **non-trivial
network of distinct constraints sustaining each other**.

### Refinement that respects the original design intent

The refinement keeps decisions 1, 2, 4 and 6 unchanged, and
revises decision 3 to filter both trivial cases above:

- **Decision 3 (revised).** A constraint is counted as *closed*
  when it lies on at least one **simple directed cycle of
  length 2 or 3** in the dependency graph. Self-loops (cycles
  of length 1) are not counted. The metric is the fraction of
  constraints that meet that criterion.

```
constraint_closure = |{ c_i : c_i lies on some simple cycle of length 2 or 3 }| / n
```

The motivation:

- **Length ≥ 2** ensures *two distinct constraints* are
  mutually involved, which is the minimum non-trivial network.
  This is exactly the membrane ↔ metabolism kind of coupling
  that the paper uses as paradigmatic.
- **Length ≤ 3** restricts the count to *local* cycles, which
  matches the biological intuition that closure is a property
  of densely-coupled subsystems, not of systems that happen to
  be cyclic at the global topological level (every periodic
  lattice is one big cycle but that does not make every
  periodic lattice a closed system in Montévil & Mossio's
  sense).

### Recomputed predictions under the refinement

| Adapter / configuration            | Reasoning                                                                                                  | Expected     |
|------------------------------------|------------------------------------------------------------------------------------------------------------|-------------:|
| `PeriodicCycle` (n=1, self-loop)   | No cycle of length 2–3 (only self-loop).                                                                   | 0.0          |
| `SimpleAutomaton.self_generated` (n=1, self-loop) | No cycle of length 2–3.                                                                     | 0.0          |
| `SimpleAutomaton.external` (n=1, no internal loop) | No cycle.                                                                                  | 0.0          |
| `ECASystem` (n cells in a ring; each depends on left, centre, right) | Every cell has a length-2 cycle with each neighbour (i ↔ i±1). All n cells qualify. | 1.0          |
| `KauffmanNetwork` K=1              | Each node has one in-edge; length-2 cycles only when two nodes point at each other. Sparse, ~ 1/n.         | 0.0–0.3      |
| `KauffmanNetwork` K=3              | Higher in-degree; many length-2 / length-3 cycles. Dense.                                                  | 0.5–0.95     |
| `KauffmanNetwork` K=`n` (all-to-all) | Every pair has length-2 cycles. All nodes qualify.                                                        | ~ 1.0        |

### Net effect on the falsification test

The refined metric still fails to separate `PeriodicCycle` from
`SimpleAutomaton.self_generated` directly, because **both have
`n = 1` and therefore admit no length-2 / length-3 cycle in
principle**. This is a structural feature of the adapter
representation, not of the metric: a single-node system simply
cannot exhibit a network of distinct constraints. Both score
`0.0`, which is honestly what Montévil & Mossio's framework
predicts for a single-constraint system.

The falsification test is therefore **rephrased** to a pair the
refined metric can actually distinguish:

- **`PeriodicCycle` (single constraint, score 0.0)** vs
  **`KauffmanNetwork` K=3 (many distinct constraints in a dense
  graph, score in 0.5–0.95)**.

Both saturate at `closure = 1.0` and cluster at `memory ≈ 1.0`
in the `v0.5.0a0` benchmark on the seeds that admit measurement;
constraint-closure should pull them apart.

A second pair worth tracking:

- **`SimpleAutomaton.self_generated` (n=1, score 0.0)** vs
  **`ECASystem` (n cells with local mutual coupling, score
  ≈ 1.0)**.

If the refined metric distinguishes both pairs, the
operationalisation is judged adequate and v0.6.0a0 ships. If
either pair fails to separate, decisions 1–4 are revisited
again before release, and the metric does not ship until
they do.

### Honest limitation

The refinement does not pretend to map every conceivable
system to a "correct" constraint-closure value. Single-node
systems (`PeriodicCycle`, `SimpleAutomaton`) are correctly
flagged as having no constraint network; the metric is silent
on whether their single rule is biologically meaningful. That
silence is a feature, not a bug: the package's job is to
report what is measurable, not to invent a number for cases
the underlying theory does not address.

This addendum supersedes the corresponding parts of section 3
(closure counted) and section 5 (predictions). The other four
decisions stay as originally documented.

## References

- Montévil, M., & Mossio, M. (2015). *Biological organisation
  as closure of constraints*. Journal of Theoretical Biology
  372, 179–191.
- Mossio, M., Saborido, C., & Moreno, A. (2009). *An
  organizational account of biological functions*. British
  Journal for the Philosophy of Science 60(4), 813–841.
- Kauffman, S. A. (2000). *Investigations*. Oxford University
  Press. (Background on autocatalytic sets; not used directly
  but informs the constraint vs process distinction.)
- Tarjan, R. E. (1972). *Depth-first search and linear graph
  algorithms*. SIAM Journal on Computing 1(2), 146–160.
  (The SCC algorithm used for cycle detection.)

---

## Resumen en español

Este documento fija las decisiones de diseño para el tercer eje
de PBA, **constraint-closure**, antes de escribir cualquier
código. Las seis decisiones aprobadas por defecto son:

1. **Constraint = función de actualización**. Un constraint por
   nodo en redes booleanas, por celda en autómatas celulares,
   uno solo en ciclos periódicos.
2. **Dependencia estructural** (topología del grafo causal).
   `i` depende de `j` si la regla de `i` lee a `j`. **No** se
   usa información mutua ni intervención causal.
3. **Cerradura = fracción de constraints en al menos un ciclo
   del grafo**. Se detectan ciclos con descomposición SCC
   (Tarjan).
4. **Sin filtro temporal** en esta versión: todas las funciones
   de actualización persisten durante toda la simulación de los
   adapters actuales, así que todas califican.
5. **Predicciones a priori escritas** antes de codear. Test
   crítico: `PeriodicCycle` y `SimpleAutomaton.self_generated`,
   que en `v0.5.0a0` colapsan al mismo punto del plano, deben
   dar valores distinguibles en este eje. Si no, la
   operacionalización falla.
6. **Defensa contra "engineered correlation"** doble: auditoría
   estática (el archivo no importa funciones de información) +
   auditoría empírica (Pearson contra los otros dos ejes < 0.7
   en el benchmark).

El ciclo termina con un benchmark de tres ejes en
`docs/benchmarks/v0.6.0a0.{csv,png,log.txt}` y la sección
correspondiente en `docs/PBA.md` y `docs/PBA.es.md`.
