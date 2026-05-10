# Failure modes — boundary regions of the autonomy thermometer

> *Status: technical reference. This document catalogues four
> families of conditions under which one or more axes of an
> `AutonomyProfile` respond non-monotonically, saturate at their
> extreme by construction, or honestly drop out — for reasons that
> reflect properties of the input rather than the structural
> autonomy of the underlying system. Cross-references the per-axis
> design documents (`CBA.md`, `CONSTRAINT_CLOSURE.md`, `RAI.md`,
> `PBA.md`) and the optional diagnostic fields surfaced on
> `AutonomyProfile` since `v0.9.0a1`. Descriptive, not prescriptive:
> the document teaches the reader how to interpret a profile near
> these regions, not how to engineer around them.*

> *Spanish summary at the bottom of this file.*

## 1. Purpose

The five normalised axes that compose an `AutonomyProfile` are
designed to live in `[0, 1]` and to be comparable across substrates.
That convention buys a great deal of expressive uniformity: a
cellular automaton, a Boolean network, a periodic cycle, a
SimpleAutomaton trace and an LLM transcript can all be plotted in
the same atlas, correlated against each other, and ranked by any
single coordinate.

The convention also has a cost. Any normalised ratio admits a
**boundary region** in which the headline number stops being a
faithful summary of the underlying property. In some cases the
metric saturates at `1.0` because both the numerator and the
denominator have collapsed onto a degenerate baseline; in others it
saturates at `0.0` for symmetric reasons; in others it drops out
honestly with a `ValueError` or a `None`. A reader who consumes only
the headline can misread these regimes as "high autonomy" when the
correct reading is "the metric has nothing to measure here" or "the
metric is reporting predictability without identity".

This document collects the four families of boundary regions that
have been observed across the package's existing axes, and points
to the diagnostic field exposed in `v0.9.0a1` that disambiguates
each one when consulted alongside the headline. It does not propose
defensive scoring schemes or operational wrappers; those belong, if
anywhere, to downstream applications building on top of the
profile, not to the measurement library itself.

## 2. Conceptual frame

The general principle has a long history. Goodhart (1975) observed
that *"any observed statistical regularity will tend to collapse
once pressure is placed upon it for control purposes"*. The
formulation predates information theory's adoption in autonomy
research by three decades, and the same shape of warning has been
restated in adjacent literatures: Strathern's compact reformulation
*"when a measure becomes a target, it ceases to be a good measure"*
(Strathern, 1997); Bertschinger, Olbrich, Ay & Jost's (2008)
distinction between observational and causal versions of every
information-theoretic autonomy candidate, which arises precisely
because purely observational measures cannot disambiguate two
different data-generating processes that yield the same
distribution; Albantakis's (2021) explicit comparison across
candidate measures of structural autonomy, which documents that
agents with the same input-output behaviour can differ widely in
their internal causal organisation, and that whether a metric
notices that difference depends on whether the metric is
observational, perturbational, or graph-structural.

For a measurement library the relevant reading of the principle is
weaker than its policy reading and more concrete: when a normalised
ratio approaches its extremes, the reader cannot tell, from the
headline number alone, **which of several qualitatively distinct
configurations** produced it. Some of those configurations
correspond to genuinely high (or low) structural autonomy; others
correspond to degeneracies of the inputs. The diagnostic fields
added in `v0.9.0a1` exist to make this distinction available
without re-running the metric.

The four families below are organised by the mechanism that
produces the ambiguity, not by the axis that exhibits it. Several
axes appear in more than one family, by design.

## 3. The four families at a glance

| # | Family | Mechanism | Axes affected | Disambiguating diagnostic |
|---|---|---|---|---|
| I | Controlled indefinition | The metric raises `ValueError` (or returns `None`) on degenerate inputs rather than fabricating a number. | `closure`, `persistence` | None needed (the failure is loud). |
| II | Saturation through mutual degeneration | A ratio of two non-negative quantities approaches `1.0` because both terms collapse onto a near-zero baseline, not because the numerator dominates. | `memory`, `coherence` | `memory_e_states`, `memory_e_env`, `cba_h_d`, `cba_h_e` |
| III | Decoupling from runtime dynamics | The metric reads a static structural property (a graph, a declared topology) and is therefore insensitive to changes in runtime behaviour that do not modify the static representation. | `constraint` | None at the metric level; auditing requires comparing the declared graph against observed transitions. |
| IV | Predictability without identity | The metric scores a ratio of mutual information to entropy, which assigns `1.0` to any deterministic mapping `E = f(D)` regardless of whether `f` is the identity. | `coherence` | `cba_match_rate`, `cba_mi` |

Sections 4–7 expand each family with a worked example and the
relevant diagnostic.

## 4. Family I — Controlled indefinition

### 4.1 Description

Some normalised ratios are mathematically undefined in regions of
the input space. The package's policy is to raise `ValueError`
rather than substitute a fabricated value. The two axes that
exhibit this behaviour are `closure` and `persistence`.

For `closure` (`compute_albantakis`), the headline is

```
closure = I(S_{t+1}; S_t | E_t) / H(S_{t+1} | E_t)
```

When `H(S_{t+1} | E_t) = 0` — for example, when the environment
is a constant trajectory and the system is perfectly determined by
its own past — the denominator vanishes and the ratio is
ill-defined. The same condition arises whenever the conditioning
strips away every degree of freedom in the next state.

For `persistence` (`compute_rai_proxy_persistence`), the headline is

```
persistence = 1 - mean_hamming(perturbed, unperturbed) / d_ref
```

When the chance baseline `d_ref` is zero — for example, when the
focal marginal distribution puts all its mass on a single state —
the ratio is ill-defined.

### 4.2 Worked example

```python
import numpy as np
from autonometrics.metrics.closure import compute_albantakis

states = np.zeros(500, dtype=np.int64)
env = np.zeros(500, dtype=np.int64)

# Both trajectories are constant. H(S_{t+1} | E_t) = 0.
# compute_albantakis raises ValueError.
compute_albantakis(states, env)
```

### 4.3 Why this is the simplest family

This failure mode is "loud": the package signals the ambiguity at
the call site and the caller is forced to handle it. The orchestrator
in `Autonometer.measure` catches these errors per axis and records
the affected axis as `None` in the resulting `AutonomyProfile`,
preserving the mosaic-dropout convention used everywhere else in
the package.

No additional diagnostic field is necessary: the `None` value in
the profile, combined with the `metadata` carrying the per-axis
status, is sufficient. The reader who sees `profile.closure is
None` and `profile.persistence is None` on a system whose other
axes saturate to extreme values should suspect a degenerate input
before suspecting a genuinely autonomous system.

### 4.4 References

- `docs/PBA.md`, sections on dropout policy and mosaic-atlas
  reporting.
- `src/autonometrics/metrics/closure.py` — docstring of
  `compute_albantakis`.
- `src/autonometrics/metrics/persistence.py` — docstring of
  `compute_rai_proxy_persistence`.

## 5. Family II — Saturation through mutual degeneration

### 5.1 Description

`memory` (`compute_memory_endo_ratio`) and `coherence`
(`compute_cba_theil_u`) are both ratios of non-negative
information-theoretic quantities. Both have the property that the
ratio approaches `1.0` not only when the numerator dominates the
denominator (the intended reading) but also when both terms
collapse onto a near-zero baseline.

For `memory`:

```
memory_endo_ratio = E(states) / (E(states) + E(env))
```

with `E(.)` the Crutchfield excess entropy of the trajectory. Two
qualitatively distinct configurations both yield `≈ 1.0`:

- **(a) System-dominant memory.** `E(states)` is large; `E(env)`
  is small but non-trivial. The system carries the joint memory.
  This is the intended high-autonomy reading.
- **(b) Mutually trivial trajectories.** Both `E(states)` and
  `E(env)` are near zero, so the ratio's numerator and denominator
  share the same near-zero baseline and the limit `0/0` is resolved
  to `1.0` by the conventional definition. The system has no memory;
  the environment has no memory; the ratio nonetheless reads `1.0`.

For `coherence`, the same shape recurs at the level of mutual
information rather than excess entropy: a Theil-U ratio
`I(D; E) / H(D)` saturates whenever `H(D)` is near zero, regardless
of whether the executed trajectory is genuinely tracking the
declared one (see Family IV for the related but distinct
"deterministic non-identity" sub-case).

### 5.2 Worked examples

For `memory`:

```python
import numpy as np
from autonometrics.metrics.memory_ratio import compute_memory_endo_ratio

# Configuration (a): system-dominant memory.
rng = np.random.default_rng(0)
period = 7
states_a = np.tile(np.arange(period, dtype=np.int64), 200)[:1000]
env_a = rng.integers(0, 4, size=1000, dtype=np.int64)

score_a, diag_a = compute_memory_endo_ratio(
    states_a, env_a, return_diagnostics=True,
)
# score_a              ≈ high (system has structured memory, env does not).
# diag_a["e_states"]   > 0
# diag_a["e_env"]      ≈ 0  (random env carries no excess entropy)

# Configuration (b): mutually trivial trajectories.
states_b = np.zeros(1000, dtype=np.int64)
env_b = np.zeros(1000, dtype=np.int64)

score_b, diag_b = compute_memory_endo_ratio(
    states_b, env_b, return_diagnostics=True,
)
# score_b              ≈ 1.0 by the 0/0 convention.
# diag_b["e_states"]   ≈ 0
# diag_b["e_env"]      ≈ 0
```

The headline numbers are not the same for arbitrary configurations,
but both regimes are reachable and both can converge to the same
high band on profile plots if only the headline is consumed. The
diagnostic fields `memory_e_states` and `memory_e_env`, exposed as
`Optional[float]` on `AutonomyProfile` since `v0.9.0a1`, allow the
reader to tell them apart.

### 5.3 Diagnostic available

For `memory`:

- `profile.memory_e_states` — Crutchfield excess entropy of the
  system trajectory in bits.
- `profile.memory_e_env` — Crutchfield excess entropy of the
  environment trajectory in bits.

A reading of `profile.memory ≈ 1.0` with `profile.memory_e_env ≈ 0`
**and** `profile.memory_e_states ≈ 0` is the degenerate regime.
A reading of `profile.memory ≈ 1.0` with
`profile.memory_e_states > 0` is the intended high-memory regime.

For `coherence`:

- `profile.cba_h_d` — Miller-Madow Shannon entropy of the declared
  marginal in bits.
- `profile.cba_h_e` — Miller-Madow Shannon entropy of the executed
  marginal in bits.
- `profile.cba_mi` — mutual information `I(D; E)` in bits.

A reading of `profile.coherence ≈ 1.0` with `profile.cba_h_d ≈ 0`
indicates a trivial declared trajectory: there is no declared-side
uncertainty for the executed trajectory to resolve, and the
headline reflects that absence rather than genuine alignment.

### 5.4 References

- `docs/CBA.md`, *Risks and mitigations* — section R2 (estimator
  bias at low `T`) and the *Provisional pick* discussion of why
  Theil's U was chosen as the headline.
- `src/autonometrics/metrics/memory_ratio.py` — docstring noting
  the `0/0` convention.
- The `v0.9.0a1` `CHANGELOG` entry, which lists the diagnostic
  fields.

## 6. Family III — Decoupling from runtime dynamics

### 6.1 Description

`constraint` (`compute_constraint_closure`) reads the **graph of
update functions** of the system, not its runtime trajectory. The
headline counts the fraction of update functions that participate
in short mutually-sustaining cycles in the dependency graph
(Montévil & Mossio, 2015; see `docs/CONSTRAINT_CLOSURE.md` for the
full operationalisation).

The metric is therefore insensitive, by design, to changes in
runtime behaviour that do not modify the declared graph. Two
qualitatively distinct situations produce identical
`constraint_closure` readings:

- **(a) Faithful representation.** The system's actual transitions
  match the declared update functions. The graph reading is a
  faithful summary of runtime structure.
- **(b) Drifted representation.** The system's actual transitions
  diverge from the declared update functions, but the declared
  graph itself has not been updated. The metric still reads the
  declared graph and reports the closure that would obtain *if*
  the system behaved as declared.

This is not an estimator bug; it is the consequence of the
Montévil-Mossio operationalisation choosing the static topology
over the runtime dynamics for principled reasons (rationale in
`docs/CONSTRAINT_CLOSURE.md`, sections on why structural rather
than informational dependency was chosen). It is documented here
so that consumers comparing `constraint_closure` against axes that
*do* read the runtime trajectory can interpret the divergence
correctly.

### 6.2 Worked example

```python
import numpy as np
from autonometrics.metrics.constraint_closure import (
    compute_constraint_closure,
)

# A causal graph with three nodes that mutually update each other.
# Adjacency representation: row i lists the inputs of node i.
graph = np.array(
    [
        [0, 1, 1],  # node 0 reads nodes 1 and 2
        [1, 0, 1],  # node 1 reads nodes 0 and 2
        [1, 1, 0],  # node 2 reads nodes 0 and 1
    ],
    dtype=np.int64,
)

# constraint_closure depends only on `graph`, not on observed
# states or transitions. Identical for any system that publishes
# this graph, regardless of how the system actually transitions
# at runtime.
score = compute_constraint_closure(graph)
```

### 6.3 Diagnostic available

No metric-level diagnostic disambiguates configurations (a) and (b)
because the metric never reads the runtime trajectory in the first
place. The disambiguation is the consumer's responsibility: a
profile with high `constraint_closure` and low `closure` (or low
`coherence` on adapters that expose a declarative layer) is the
reading that flags the drift. `closure` is sensitive to runtime
information flow; `constraint_closure` is not. Consistent disagreement
between the two on systems whose declared graph claims tight
self-sustenance is informative.

The recommended reading procedure is documented in `docs/PBA.md`
under cross-axis interpretation; this guide adds the concrete
pattern: when consumers need confidence that the declared graph
remains a faithful representation of runtime dynamics, the
appropriate move is to monitor `closure` and `constraint_closure`
jointly on the same system over time and to investigate any
sustained divergence as either a data-quality issue or a genuine
structural drift.

### 6.4 References

- `docs/CONSTRAINT_CLOSURE.md` — sections on why structural rather
  than informational dependency was chosen, and on the boundary
  regions of the metric.
- `docs/PBA.md` — cross-axis interpretation table.

## 7. Family IV — Predictability without identity

### 7.1 Description

`coherence` (`compute_cba_theil_u`) is implemented as Theil's U:

```
cba_theil_u = I(D; E) / H(D)
```

with `H(D)` the Shannon entropy of the declared marginal and
`I(D; E)` the mutual information between declared and executed
trajectories.

Theil's U is a measure of **predictability**, not of **identity**.
Any deterministic mapping `E = f(D)` with non-zero entropy on `D`
yields `cba_theil_u = 1.0`, because knowing `D` is sufficient to
predict `E`. This is the standard semantics of the uncertainty
coefficient (Theil, 1970) and is in fact desirable for a measure
that aims to capture "how much of the executed trajectory is
determined by the declared one". It is also the source of a
boundary region: when `f` is a non-identity bijection of the
alphabet, the headline reads `1.0` even though the declared and
executed sequences never coincide pointwise.

This case is documented in `docs/CBA.md` under *Risks and
mitigations*, section R1 ("Theil's U scoring bijections as
`1.0`"), and is the reason `compute_cba_theil_u` ships its
`return_diagnostics=True` companion path that computes
`cba_match_rate = (1 / T) * Σ_t 𝟙[D_t == E_t]` alongside the
headline.

### 7.2 Worked example

```python
import numpy as np
from autonometrics.metrics.coherence import compute_cba_theil_u

rng = np.random.default_rng(0)
declared = rng.integers(0, 4, size=200, dtype=np.int64)
executed = (declared + 1) % 4  # non-identity bijection

score, diag = compute_cba_theil_u(
    declared, executed, return_diagnostics=True,
)
# score                  ≈ 1.000   (knowing D fully determines E)
# diag["match_rate"]     ≈ 0.000   (D and E never coincide pointwise)
```

### 7.3 Diagnostic available

Since `v0.9.0a1`:

- `profile.cba_match_rate` — fraction of timesteps with
  `D_t == E_t`.
- `profile.cba_mi` — mutual information `I(D; E)` in bits.
- `profile.cba_h_d`, `profile.cba_h_e` — declared and executed
  marginal entropies.

A reading of `profile.coherence ≈ 1.0` with
`profile.cba_match_rate ≈ 0.0` is the bijection regime. A reading
of `profile.coherence ≈ 1.0` with `profile.cba_match_rate ≈ 1.0`
is the identity regime. The two are mathematically distinct
configurations of the same `(declared, executed)` pair, and the
choice of which one to consume in downstream tooling is left to
the consumer's domain.

### 7.4 References

- `docs/CBA.md`, *Risks and mitigations*, section R1.
- `docs/CBA.md`, *Provisional pick — Theil's U with C1 as a
  sanity-check companion* — explains why the package ships C1
  internally as a diagnostic rather than as the headline.
- Theil, H. (1970). "On the Estimation of Relationships
  Involving Qualitative Variables".

## 8. Diagnosing in practice

The `v0.9.0a1` release added eight optional `Optional[float]`
fields on `AutonomyProfile`. The matching between failure modes
and diagnostic fields is summarised below.

| Family | Diagnostic to consult | Reading procedure |
|---|---|---|
| I — Controlled indefinition | None at the metric level | The axis is `None`. Check `metadata` for the per-axis status string. |
| II — Saturation through mutual degeneration (memory) | `memory_e_states`, `memory_e_env` | If both are near zero, the headline `≈ 1.0` is the degenerate regime, not the high-memory regime. |
| II — Saturation through mutual degeneration (coherence) | `cba_h_d` | If `cba_h_d ≈ 0`, the headline reflects a trivial declared trajectory rather than alignment. |
| III — Decoupling from runtime dynamics | None at the metric level | Compare `constraint_closure` against `closure` on the same system over time; sustained divergence is the flag. |
| IV — Predictability without identity | `cba_match_rate` | If `cba_match_rate` is materially below `cba_theil_u`, the headline reflects predictability without pointwise identity. |

The procedure is the same in every case: read the diagnostic
alongside the headline, not in place of it. The headline remains
the authoritative summary the atlas is built around; the
diagnostic enables the consumer to recognise when the headline is
sitting on a boundary region.

## 9. What this guide does NOT cover

The catalogue is descriptive. It does not propose:

- Operational scoring schemes that combine the headline with the
  diagnostic (consumers building on top of `AutonomyProfile` are
  free to design their own; this is out of scope for the
  measurement library).
- Mitigation strategies for any individual failure mode beyond
  pointing at the diagnostic field that disambiguates it. The
  question of how downstream systems should respond to a
  diagnostic-flagged boundary region is application-specific.
- Falsification procedures for the metrics themselves. Each axis
  has its own pre-registered falsification thresholds in its design
  document (`CBA.md`, `RAI.md`, `CONSTRAINT_CLOSURE.md`,
  `ATLAS_GEOMETRY.md`); this guide does not duplicate them.
- Substrate-specific failure modes that are properties of a
  particular adapter rather than of the axis itself (covered in
  the relevant adapter documentation when present).
- External validation of the axes against behavioural data; that
  is deferred to studies built on top of the package, in line with
  the validation plan in `docs/CBA.md` *Provisional status and
  validation plan* and in `docs/PBA.md`.

The guide is also explicitly **not a security document**. The
families catalogued here are properties of the measurement
machinery, not of any adversarial use of it. Threat models that
treat the metric as a target — Goodhart-style scenarios in the
strong sense of Strathern (1997) — are out of scope.

## 10. Cross-references

- `docs/PBA.md` — top-level atlas document; mosaic-dropout policy
  and cross-axis interpretation table.
- `docs/CBA.md` — design and post-mortem for the coherence axis;
  sections R1 (bijection) and R2 (estimator bias) overlap with
  Families II and IV here.
- `docs/CONSTRAINT_CLOSURE.md` — design for the constraint axis;
  the choice of static rather than informational dependency
  motivates Family III.
- `docs/RAI.md` — design for the persistence axis; the chance
  baseline `d_ref` is the source of the indefinition case in
  Family I.
- `docs/ATLAS_GEOMETRY.md` — pre-registered geometry analyses
  across releases; the `v0.8.0a0` follow-up records the override
  of a hard-gate trip on diagnostic grounds.
- `CHANGELOG.md` — `v0.9.0a1` entry lists the eight diagnostic
  fields added on `AutonomyProfile`.

## 11. References

- Goodhart, C. A. E. (1975). "Problems of Monetary Management:
  The U.K. Experience". *Papers in Monetary Economics*, Reserve
  Bank of Australia.
- Strathern, M. (1997). "Improving ratings: audit in the British
  University system". *European Review*, 5(3), 305–321.
- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  "Autonomy: An information theoretic perspective". *BioSystems*,
  91(2), 331–345.
- Theil, H. (1970). "On the Estimation of Relationships
  Involving Qualitative Variables". *American Journal of
  Sociology*, 76(1), 103–154.
- Montévil, M., & Mossio, M. (2015). "Biological organisation as
  closure of constraints". *Journal of Theoretical Biology*, 372,
  179–191.
- Albantakis, L. (2021). "Quantifying the Autonomy of Structurally
  Diverse Automata: A Comparison of Candidate Measures". *Entropy*,
  23(11), 1415.

## Resumen en español

> *Esta sección reproduce, de forma compacta y en español neutro,
> las decisiones del documento. La autoridad sobre el contenido
> técnico la tiene el texto en inglés.*

### Qué documenta esta guía

Las cinco aristas normalizadas de un `AutonomyProfile` viven en
`[0, 1]` y son comparables entre sustancias. Esa convención tiene
un costo: cualquier ratio normalizado admite **regiones de
frontera** en las que el número headline deja de ser un resumen
fiel de la propiedad subyacente. Esta guía cataloga cuatro familias
de tales regiones, observadas a lo largo de las aristas
existentes, y para cada una indica el campo diagnóstico expuesto
en `v0.9.0a1` que permite distinguir el régimen degenerado del
régimen genuinamente alto (o bajo).

La guía es **descriptiva, no prescriptiva**: enseña a leer el
termómetro cerca de estas regiones, no propone esquemas de
puntuación defensivos ni envoltorios operacionales. Esos son
problemas de las aplicaciones que se construyen sobre el perfil,
no de la biblioteca de medición.

### Las cuatro familias

| # | Familia | Mecanismo | Aristas | Diagnóstico |
|---|---|---|---|---|
| I | Indefinición controlada | El cálculo lanza `ValueError` o devuelve `None` ante entradas degeneradas. | `closure`, `persistence` | No requiere diagnóstico (la falla es ruidosa). |
| II | Saturación por degradación mutua | El ratio se aproxima a `1.0` porque numerador y denominador colapsan a una misma línea base cercana a cero. | `memory`, `coherence` | `memory_e_states`, `memory_e_env`, `cba_h_d`, `cba_h_e` |
| III | Desacople de la dinámica de ejecución | La métrica lee una propiedad estructural estática y es insensible a cambios de ejecución que no modifican esa estructura declarada. | `constraint` | Ninguno a nivel de métrica; auditar comparando `constraint_closure` contra `closure` a lo largo del tiempo. |
| IV | Predictibilidad sin identidad | El ratio asigna `1.0` a cualquier mapeo determinístico `E = f(D)` aunque `f` no sea la identidad. | `coherence` | `cba_match_rate`, `cba_mi` |

### Cómo usar la guía

Para cada perfil que se acerque a un valor extremo en alguna
arista, consultar el campo diagnóstico correspondiente **junto al
headline**, no en su lugar. El headline sigue siendo el resumen
autoritativo sobre el que se construye el atlas; el diagnóstico
permite reconocer cuándo el headline está sentado en una región
de frontera y, por lo tanto, cuándo conviene auditar la lectura
en lugar de consumirla directamente.

### Lo que la guía **no** cubre

- Esquemas de puntuación operacionales que combinen headline y
  diagnóstico.
- Estrategias de mitigación específicas más allá de señalar el
  diagnóstico que desambigua cada caso.
- Procedimientos de falsación de las propias métricas (cubiertos
  en los documentos de diseño por arista).
- Modos de falla específicos de adaptadores particulares
  (cubiertos en la documentación del adaptador correspondiente).
- Validación externa contra datos conductuales (diferida a
  estudios externos al paquete).
- Modelos de amenaza que traten la métrica como objetivo
  (Goodhart en sentido fuerte de Strathern 1997). Fuera de
  alcance.

### Cómo encaja con el resto de la documentación

Esta guía no inventa contenido nuevo: consolida en un solo
documento patrones que ya están señalados, individualmente, en las
docs por arista (`CBA.md` R1, `CONSTRAINT_CLOSURE.md` sección de
boundary regions, `RAI.md` sección de risks, etc.) y los cruza con
los campos diagnósticos añadidos en `v0.9.0a1`. Un lector que
quiera el detalle por arista debe ir al documento de diseño
correspondiente; un lector que quiera el panorama transversal
encuentra aquí el catálogo unificado.

Todos los detalles, excepciones, cita de literatura y referencias
cruzadas adicionales están en el texto en inglés más arriba.
