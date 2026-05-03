# PBA as a falsifiable hypothesis

> *Spanish version available in [`docs/PBA.es.md`](PBA.es.md).
> This English version is the canonical reference; in case of
> any discrepancy, this one wins.*

> *Status: working draft. The argument here drives the design of
> `autonometrics` and is itself testable; this document exists so
> that the test can be carried out, and so that the package does
> not pretend that the principle is proven.*

## What PBA states

The **Principio de Bordes Autodeterminados** (PBA), in its current
working form, is a structural claim about how systems determine
their own behaviour:

> The structural self-determination of a system can be read as a
> *ratio of internal magnitude over total magnitude*, where
> "magnitude" stands for some quantity (information, causal
> influence, energy, constraint, etc.) that the system's behaviour
> is sensitive to.

Concretely, PBA predicts that several classical formalisations of
autonomy and self-determination
— Bertschinger / Albantakis (information-theoretic closure),
Gershenson autopoiesis (self-production of components),
Deci & Ryan RAI (motivational regulation),
coherence-based alignment (CBA), and
Montévil & Mossio's closure of constraints —
are **five faces of one structural shape**, not five unrelated
phenomena that happen to use ratios.

If PBA is correct, the five corresponding metrics, when computed
on the same system, should not be statistically independent: they
should covary in ways that the literature on each formalism would
predict.

## What kind of unification PBA proposes

The phrase "five faces of one structural shape" is deliberately
chosen and easy to misread. Two natural misreadings sit on either
side of what PBA actually claims, and both are wrong in
informative ways. This section pins the middle.

### Three levels of unification

Different scientific unifications carry very different ontological
commitments. It helps to separate them explicitly.

**Level 1 — Extensional identity.** "These N quantities are
literally the same number, expressed in different notations." The
canonical case is entropy: thermodynamic entropy, Boltzmann's
statistical entropy and Shannon's information entropy turned out
to be one quantity up to unit conversion
(`S_thermo = k_B · S_stat`,
`H_Shannon = S_stat / ln 2`). Other examples: `E = mc²`, Maxwell's
unification of electricity and magnetism. When such a unification
holds it **reduces ontology**: N concepts collapse to one, and the
field reorganises around the reduction. These cases are rare and
are the strongest possible scientific unification.

**Level 2 — Shared structure with multiple coordinates.** "These N
quantities are coordinated views of one underlying object that is
*not itself scalar*; no single one of them captures the object,
but together they cover it, and they are constrained to move
consistently as views of the same thing." Examples:

- **Color**. Not one quantity. At least three-dimensional.
  RGB, HSV and CMYK are different coordinate systems on the same
  perceptual space, with precise transformation rules between
  them.
- **Big Five personality**. Five empirically stable dimensions
  (openness, conscientiousness, extraversion, agreeableness,
  neuroticism) recovered through factor analysis on questionnaire
  data across cultures and languages. Not reducible to one axis;
  not arbitrary either.
- **Temperature pre-kinetic-theory (1700s–1850s)**. Multiple
  operational definitions (mercury thermometer, gas thermometer,
  blackbody radiation) ranking systems consistently by "hotness"
  before any unifying theory existed for what they were jointly
  measuring. The kinetic theory of gases came almost a century
  later.
- **Spacetime in special relativity**. Space and time, until then
  treated as independent, became coordinates of a single 4D
  object whose Minkowski geometry imposes specific relations
  between them.

A Level 2 unification **does not reduce ontology**; it **describes
its structure**. The claim is that an object exists in some
coordinate-independent sense, and that its multiple operational
definitions are consistent enough to triangulate it.

**Level 3 — Arbitrary grouping under a shared label.** "These N
quantities have the same name because we put them in the same
folder; there is no underlying object." Many premature
"unifications" in theoretical work fall here when subjected to
empirical test. A Level 3 result is not unification at all; it is
a taxonomic mistake.

### PBA is Level 2, not Level 1

PBA does **not** claim that the five metrics it integrates
(`closure`, `memory`, `constraint_closure`, `rai_proxy_persistence`,
the planned CBA axis) are the same scalar quantity in different
notations. That stronger claim, if made, would be falsified by
any pairwise correlation noticeably below `|r| ≈ 1.0`. Empirically,
the v0.5.0a0, v0.6.0a0 and v0.7.0a0 benchmarks already show
pairwise Pearson correlations between the four shipped axes of
`+0.32` (closure-memory), `-0.04` (closure-constraint), `-0.57`
(memory-constraint), `-0.44` (closure-persistence), `-0.38`
(memory-persistence) and `+0.05` (constraint-persistence). A
Level 1 reading of PBA is therefore already falsified — by six
pairs of correlations sitting below the saturating `|r| ≈ 1.0` —
and was never the intended reading.

What PBA does claim is the Level 2 reading:

> Structural self-determination is a real but multidimensional
> phenomenon. Each of the five formalisms shipped with the package
> operationalises a different coordinate of that phenomenon. The
> five coordinates are not independent — they are constrained by
> being views of the same underlying object — but neither are they
> identical. The shape of their joint distribution across
> meaningful systems is what PBA predicts and what
> `autonometrics` measures.

The prediction this enables is sharp: pairwise correlations should
sit in a "sweet spot" — non-zero (otherwise no shared object) and
sub-saturating (otherwise redundant), with signs interpretable
from each formalism's underlying theory. The benchmark snapshot
described in "Current evidence status" lives inside that sweet
spot for two of three current pairs and gives a known-cause
explanation for the third (Albantakis closure saturates on the
current zoo, which compresses any linear relation involving it
toward zero by construction).

### `autonometrics` as an atlas of autonomy

The most accurate one-line description of what the package
proposes is therefore:

> `autonometrics` is an *atlas* of autonomy: a small set of
> charts (metrics) that cover the same multidimensional territory
> from different operational angles and remain comparable to each
> other through a shared `[0, 1]` ratio normalisation.

Three properties this framing preserves and three it gives up
deserve to be stated explicitly.

**Preserved.**

- Falsifiability. The atlas can fail (correlations randomise,
  signs go against theory, classes refuse to co-discriminate),
  and that failure is publishable.
- Cross-tradition comparability. Five metrics on the same plane
  is a real instrument regardless of whether the unifying claim
  holds.
- Operational utility. Atlas-style measurement is already used
  in fields where the underlying object is genuinely
  multidimensional (color, personality, anatomy under homology);
  the precedent is mature.

**Given up.**

- The dramatic single-quantity reduction of Level 1. We are not
  doing entropy.
- The promise that one number can stand for autonomy. It cannot,
  and pretending otherwise would be a category error.
- The expectation that all five metrics will eventually agree on
  a single ranking of systems. They will not, and *should* not
  if the underlying object really is multidimensional.

This section is the canonical statement of the level at which PBA
operates. The rest of the document — falsification criteria,
domain-of-applicability theorems, evidence status — should be read
under it. References to "five faces of one structural shape"
elsewhere in the codebase and the README are shorthand for the
Level 2 reading defined here.

## Why this is a hypothesis and not a definition

The temptation is to read PBA as a *convention* — "we choose to
call this ratio shape autonomy". That is a coherent move, but it
is not the move taken here. `autonometrics` treats PBA as an
**empirical conjecture about the structure of an existing
literature**, not as a stipulative definition.

The difference matters because:

- A definition cannot be wrong; it can only be useful or useless.
- A conjecture about how five distinct research traditions relate
  *can* be wrong, and is therefore informative when it survives
  contact with data.

`autonometrics` is the instrument that exposes the conjecture to
that contact.

## The falsifiable prediction

Once the package has all five ratio-shaped metrics implemented
(roadmap targets `v0.5.0a0` through `v0.7.0a0`), the prediction
takes a concrete form:

> **Prediction.** Across a curated benchmark of systems with
> independently-known degrees of structural self-determination
> (e.g. period-`p` cycles, coupled boolean networks at varying
> coupling strengths, RL agents at varying degrees of policy
> grounding, Likert responses from population studies of
> autonomous vs heteronomous motivation), the five PBA ratios
> should:
>
> 1. Be **non-trivially correlated** across systems where the
>    underlying literature predicts a shared autonomy gradient.
> 2. **Co-discriminate** between qualitatively different classes
>    that the literature predicts should differ on autonomy
>    (e.g. self-rule-driven vs noise-driven automata, intrinsic
>    vs extrinsic motivation profiles).
> 3. **Converge** on the same canonical region of the joint
>    `[0, 1]^5` hypercube for a given class, rather than scatter
>    across it.

## What would falsify PBA

The prediction is informative because it can fail in concrete,
publishable ways:

- **Independence outcome.** If across the benchmark the five
  ratios end up empirically independent (pairwise correlations
  centred at zero, no shared principal component above noise),
  PBA collapses to a *common functional form* without a *common
  underlying construct*. The package would still be useful as a
  five-axis dashboard, but the unifying argument would be wrong.

- **Anti-correlation outcome.** If the ratios systematically
  pull in opposite directions on systems the literature
  considers paradigmatically autonomous, PBA mis-identifies what
  the five traditions are measuring; the unifying argument
  would be not just wrong but actively misleading.

- **Class-mixing outcome.** If the five-dimensional point cloud
  fails to separate self-determined from heteronomous classes
  better than chance, the principle has no discriminative
  power and should be retired.

Any of these outcomes is a valid scientific result. PBA is
designed to be discardable.

## What would *not* falsify PBA

To keep the test honest, two near-misses must be ruled out
explicitly:

- **Trivial agreement on degenerate cases.** If all five ratios
  return the same number on a constant sequence and on uniform
  i.i.d. noise, that is not evidence for PBA; it is evidence
  that any reasonable normaliser collapses on degenerate
  inputs. The benchmark must include non-degenerate systems
  where the ratios are forced to disagree if PBA is wrong.

- **Engineered correlation.** If the five metrics are
  implemented in a way that mathematically forces them to
  share most of their variance (e.g. all of them ultimately
  reading off the same conditional entropy), apparent
  correlation is a coding artefact, not evidence. Each metric
  must therefore be implemented from its primary source and
  audited for hidden algebraic overlap.

## Why the project survives a falsification of PBA

The package's operational value is **independent of the
unifying argument**. If PBA is falsified, `autonometrics`
remains useful as:

- a cross-platform, dependency-light reimplementation of five
  reference metrics that are otherwise scattered across
  papers, languages and ecosystems,
- a standardised `AutonomyProfile` data container with
  measurement metadata,
- a small ecosystem of adapters for distinct substrates
  (synthetic automata, CSV trajectories, future LLM
  transcripts and surveys),
- a canonical `[0, 1] × [0, 1]` plane for two-axis readings
  that does not require the five-axis claim to be true.

Tying the project's survival to the truth of PBA would have
been a fragile design choice. Tying its survival to the
correctness of the underlying classical metrics — each of
which is independently published, cited and defended — is
much sturdier.

## Domain of applicability

PBA is a claim about *self-determined boundaries*; the metrics it
relies on therefore have **regions where they are mathematically
trivial**, not because the metric is broken but because in those
regions the system itself is degenerate from the metric's point of
view. Acknowledging those regions explicitly is part of the
honest formulation of the principle.

The first such region was identified empirically in `v0.5.0a0` and
characterised formally in `v0.5.1a0`:

> **Closure saturation theorem (informal).** For a system whose
> dynamics is deterministic and whose observed pair `(S_t, E_t)`
> contains all the variables the transition rule depends on,
> Albantakis closure satisfies `A = 1` by construction.
>
> *Proof sketch.* Under those conditions
> `H(S_{t+1} | S_t, E_t) = 0`. By the chain rule,
> `H(S_{t+1} | E_t) = I(S_{t+1}; S_t | E_t) + H(S_{t+1} | S_t, E_t)`.
> The second term vanishes, so the numerator and the denominator
> of the closure ratio are equal.

The `v0.5.0a0` benchmark made this saturation visible: every
elementary cellular automaton, every period-`p` cycle and every
self-generated `SimpleAutomaton` in the zoo collapsed onto the
vertical line `closure = 1.0`. The theoretical statement above
explains *why*. The diagnostic shipped in `v0.5.1a0`
(`examples/saturation_diagnostic.py`,
`docs/benchmarks/saturation_v0.5.1.csv`,
`docs/benchmarks/saturation_v0.5.1.png`) verifies it empirically:
when bit-flip noise is injected into the focal trajectory of a
saturating ECA at probability `p`, the closure score falls
monotonically from `1.000` at `p = 0` to `≈ 0.001` at `p = 0.5`,
with a sharp drop already visible at `p = 0.01` (closure ≈ 0.81).
The wall is therefore a **fragile theoretical point**, not a
robust regime, and any closure value below 1.0 is informative
about partial observation, stochastic dynamics, or measurement
noise — exactly the three failure modes the metric is designed
to detect.

Three practical consequences for PBA:

1. **The metrics have trivial regions, and that is fine.**
   Reading `closure = 1.0` as "maximally autonomous" is wrong; it
   reads as "the metric saturated because the system is fully
   determined and fully observed". A determinist clockwork hits
   the same point as a maximally self-organising system.

2. **Where you cut "system" vs "environment" moves the metric.**
   The Albantakis ratio is relative to the chosen pair
   `(S, E)`. Changing what counts as the system or what counts
   as the environment can shift closure between 0 and 1 without
   changing the underlying physical process. Adapter design is
   not a neutral act of plumbing; it is part of the measurement.

3. **PBA cannot promise universality across degenerate regions.**
   The principle is informative *outside* the trivial regions of
   each metric. Any claim about empirical correlation among the
   five ratios is therefore a claim *conditional on* avoiding
   those regions in the benchmark systems used for the test.

### Constraint-closure complements the wall, not replaces it

The third axis shipped in `v0.6.0a0`,
`constraint_closure`, was added in part to *probe* the saturation
wall identified above. Its design (see
[`docs/CONSTRAINT_CLOSURE.md`](CONSTRAINT_CLOSURE.md)) is
deliberately information-theory-free: the metric reads only the
topology of the system's causal-dependency graph and counts the
fraction of constraints that lie on a simple directed cycle of
length 2 or 3. Two consequences for the domain-of-applicability
discussion:

1. **Constraint-closure does not saturate where Albantakis closure
   does.** A deterministic single-node periodic cycle hits
   `closure = 1.0` and `constraint = 0.0`; a deterministic ECA
   ring hits `closure = 1.0` and `constraint = 1.0`. The third
   axis therefore *separates* systems that the first axis is
   forced to identify, but it has saturating regions of its own:
   any single-constraint system scores `0.0` and any
   periodic-ring whose every cell sits next to a neighbour that
   reads it back scores `1.0`. PBA never escapes the need to
   state a domain of applicability per axis; it only changes
   which axis is informative on which system.
2. **Independence is now testable on a third pair.** With three
   axes, three pairwise correlations exist (`closure-memory`,
   `closure-constraint`, `memory-constraint`); the
   engineered-correlation safeguard in the previous section
   applies to each of them. The fourth axis added in
   `v0.7.0a0` raises the count to six pairwise correlations,
   and all six stay below `|r| < 0.7` on the v0.7.0a0 zoo (see
   "Current evidence status" below).

The two saturating regions of the third axis are themselves
formal theorems, documented and verified in
[`docs/CONSTRAINT_CLOSURE.md` (Domain of applicability section)](CONSTRAINT_CLOSURE.md#domain-of-applicability-added-in-v061a0):

- **Theorem A (single-constraint trivial-zero).** Any system
  with `n = 1` update function returns `constraint = 0.0` by
  construction (a simple cycle of length 2 or 3 requires at
  least two distinct nodes).
- **Theorem B (symmetric-neighbour saturation).** Any graph in
  which every node reads at least one node that reads it back
  returns `constraint = 1.0` by construction (every node sits
  on a length-2 cycle).

The `v0.6.1a0` diagnostic
(`docs/benchmarks/constraint_density_v0.6.1.{csv,png,log.txt}`)
verifies both jointly by sweeping connection density on a
Kauffman zoo and observing the curve walk monotonically from
`constraint ≈ 0.14` at `K = 1` (lower boundary, sparse) to
`constraint = 1.00 ± 0.00` for `K ≥ 6` at `n = 10` (upper
boundary, dense). Single-node adapters and dense periodic rings
are correctly identified as **outside the metric's
discriminative domain** rather than as low- or high-autonomy.

### Persistence saturates at both extremes of focal coupling

The fourth axis shipped in `v0.7.0a0`,
`rai_proxy_persistence`, was added in part to *cross-traditions
test* the atlas claim: closure / memory / constraint are
information-theoretic and graph-theoretic; persistence is a
**dynamical** structural proxy drawn from the
goal-directedness literature (Lee & McShea 2020) and adapted to
systems without an externally specified goal. Its design is
documented in [`docs/RAI.md`](RAI.md). Like the previous three
axes, persistence has saturating regions of its own that have to
be stated explicitly:

1. **Persistence saturates differently on different boundaries.**
   On a `KauffmanNetwork` swept across focal coupling, the
   `v0.7.0a0` diagnostic
   (`docs/benchmarks/persistence_v0.7.0.{csv,png,log.txt}`)
   observes a **U-shape**: the metric sits near `1.0` at both
   ends of the coupling axis (left end: focal trajectory
   collapses to a fixed point so any perturbation is absorbed
   trivially; right end: the focal flip never enters the rule
   that computes the focal at `t_star + 1`, so the perturbation
   is invisible by construction), and dips in the middle, where
   actual perturbation propagation is observed. The non-trivial
   useful range of the metric on Boolean-network adapters is the
   intermediate-coupling regime; both tails are
   trivial-absorption regions of different kinds.
2. **Independence is now testable on six pairs.** With four
   axes, six pairwise correlations exist; the engineered-
   correlation safeguard applies to each. On the v0.7.0a0
   benchmark all six pass the `|r| < 0.7` gate.

The two saturation regimes for persistence are noted as
provisional findings in this release. Formalising them as named
theorems (analogous to Theorem A / Theorem B for
`constraint_closure`) is the planned content of the `v0.7.1`
maintenance cycle, jointly with the perturbation-magnitude sweep
already deferred there in `docs/RAI.md`.

The remaining axis (the coherence-based ratio planned for
`v0.8.x`) will receive an analogous diagnostic as it ships: each
metric's domain of applicability has to be stated before that
metric counts as evidence for or against PBA.

### Atlas geometry: do the four axes share a single object?

The four-axis benchmark passes the pairwise `|r| < 0.7`
falsification gate on every release. That result rules out the
strong **Level 1** reading of PBA (one scalar in different
notations) but does **not** decide between **Level 2** (one
multidimensional object, four projections) and **Level 3**
(several objects sharing a label). Both readings are consistent
with the same correlation table.

The `v0.7.2a0` cycle subjects the Level-2 reading to a *partial*
structural test by analysing the geometry of the 4-D point cloud
produced by the extended benchmark. The pre-registration is at
[`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md); the analyser is
`examples/atlas_geometry.py`; snapshots are at
`docs/benchmarks/atlas_geometry_v0.7.2a0.{json,log.txt,png}`.

The pre-registered indicators are anchored in textbook
conventions (Jolliffe 2002 for PCA variance shares, Rousseeuw
1987 for silhouette ranges) and were locked before the extended
analysis was run. On the `n_valid = 247` (out of 405) extended
zoo:

| Indicator         |   Value | Pre-registered band                                |
|-------------------|--------:|----------------------------------------------------|
| `λ_1`             | `0.469` | `[0.40, 0.70)` — inconclusive PCA                  |
| `λ_1 + λ_2`       | `0.809` | `[0.65, 0.85)` — partial low-dimensionality        |
| `s(k* = 5)`       | `0.642` | `≥ 0.50` — strong cluster structure                |
| Cluster alignment |       — | 4 of 5 clusters dominated by one adapter class     |

The combination is not a clean fit to any of the three
pre-registered outcomes. PCA lands in Outcome B's *inconclusive*
band; silhouette lands in Outcome A's *strong-cluster* band; the
clusters are *not* cross-adapter, so the Outcome A path is
blocked. The honest verdict, written up in
[`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md), is

> **Inconclusive on the level question (PCA reading), with a
> Level-3-suggestive overlay (clustering reading).**

Three concrete consequences for the framework:

1. **Level 2 is no longer "supported by structural geometry".**
   The 4-D cloud is neither effectively 1-D nor effectively 2-D.
   It carries non-trivial structure on at least three of its
   four PCA components.
2. **Level 3 cannot be declared on this evidence either.** The
   isotropy thresholds (`λ_1 < 0.40`, `λ_1 + λ_2 < 0.65`) are
   not crossed, even though the cluster geometry tracks
   substrate.
3. **The level question is pushed to v0.9.0.** Behavioural
   validation against transcript-based RAI is now the only path
   that can arbitrate Level 2 vs Level 3 cleanly. Structural
   geometry alone, on the current zoo, is genuinely
   under-determined.

A Simpson's-paradox health flag is also raised: several of the
six global pairwise correlations differ from their within-cluster
or within-adapter counterparts by more than `0.30`. The most
extreme case is `closure–persistence`: global `−0.61`, within
`KauffmanNetwork` `−0.07`, within `SimpleAutomaton` `−1.00`. The
falsification result (`|r_global| < 0.7` on every pair) survives
on the extended sample, but the magnitudes of the global
correlations are partly artefacts of the substrate mixture in
the zoo.

The verdict is conditional on the `non-degeneracy` clause: the
extended sweep produces dropouts in 39% of configurations,
concentrated on `ECASystem` and `KauffmanNetwork` (51 — 55%
adapter-internal dropout) and zero on `PeriodicCycle` and
`SimpleAutomaton`. This is itself a structural finding — the
metric set has a joint blind spot selective for the cellular and
network adapters — and is documented as such in
[`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md).

## Current evidence status

As of `v0.7.2a0`:

- Four of the five ratios are implemented (`ratio_endo_total`,
  `memory_endo_ratio`, `constraint_closure`,
  `rai_proxy_persistence`).
- Internal sanity tests show the four ratios behave as the
  literature predicts on canonical cases (constant series,
  i.i.d. noise, deterministic cycles, mixed self-rule plus
  environment-driven dynamics, isolated constraints versus
  mutually-sustaining ones, perturbation propagation under
  determinism, perturbation absorption under fixed-point
  collapse, perturbation invisibility under full external
  coupling).
- A first cross-system mini-benchmark with two axes was run in
  `v0.5.0a0`
  (snapshot under `docs/benchmarks/v0.5.0a0.{csv,png,log.txt}`):
  on 48 valid points out of 69 configurations,
  `Pearson r(closure, memory) = +0.32` and
  `Spearman r(closure, memory) = +0.56`, both below the
  `|r| < 0.7` threshold this document uses as a falsification
  cue.
- The `v0.5.1a0` saturation diagnostic confirms that the
  vertical wall at `closure = 1.0` observed in that benchmark is
  the closure-saturation theorem above, not a flaw of the metric:
  injecting Bernoulli bit-flip noise pulls closure off the wall
  monotonically.
- The `v0.6.0a0` benchmark adds the third axis to the same zoo
  (snapshot under `docs/benchmarks/v0.6.0a0.{csv,png,log.txt}`):
  on 48 valid points out of 69 configurations the three
  Pearson correlations are
  `r(closure, memory) = +0.32`,
  `r(closure, constraint) = -0.04`,
  `r(memory, constraint) = -0.57`,
  all below the `|r| < 0.7` threshold.
- The `v0.7.0a0` benchmark adds the fourth axis to the same zoo
  (snapshot under `docs/benchmarks/v0.7.0a0.{csv,png,log.txt}`):
  on 48 valid points out of 69 configurations the six
  Pearson correlations are
  `r(closure, memory) = +0.32`,
  `r(closure, constraint) = -0.04`,
  `r(closure, persistence) = -0.44`,
  `r(memory, constraint) = -0.57`,
  `r(memory, persistence) = -0.38`,
  `r(constraint, persistence) = +0.05`,
  all below the `|r| < 0.7` threshold. The aggregate diagnostic
  flag (`max` over the six pairs) is `OK`.
- The `v0.7.2a0` extended benchmark scales `n_seeds` from 5 to
  30 on the same zoo (snapshot under
  `docs/benchmarks/v0.7.2a0.{csv,png,log.txt}`). On `247` valid
  points (out of `405` configurations, with the dropout pattern
  documented in [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md))
  the six Pearson correlations are
  `r(closure, memory) = +0.27`,
  `r(closure, constraint) = +0.04`,
  `r(closure, persistence) = -0.61`,
  `r(memory, constraint) = -0.52`,
  `r(memory, persistence) = -0.33`,
  `r(constraint, persistence) = -0.07`,
  again all below the `|r| < 0.7` threshold. The fourth axis
  therefore carries information not already encoded by the
  first three on the extended adapter zoo as well. The
  cross-tradition test of the atlas hypothesis is partial at
  this point: the structural proxy passes the structural audit,
  but the strong validation against transcript-based RAI is
  deferred to `v0.9.0`.
- The `v0.7.2a0` atlas-geometry analysis (PCA + k-means +
  silhouette + conditional correlations on the same extended
  zoo) lands the level question in an honestly *inconclusive*
  state with a *Level-3-suggestive overlay*; details and
  pre-registered thresholds are in
  [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md) and summarised
  in the *Atlas geometry* subsection above.

PBA is therefore at the stage of *plausible working hypothesis
with diagnostic-grade limitations mapped on three of the four
shipped axes (saturation under determinism, single-constraint
trivial-zero, symmetric-neighbour saturation; the persistence
boundaries are recorded as provisional findings to be formalised
in v0.7.1), four of the five axes empirically distinguishable
on the current zoo, and the Level 2 vs Level 3 question
genuinely under-determined on the structural domain pending
v0.9.0's behavioural validation*, not *empirical claim*.
Documents and demos in the package phrase it accordingly.

## Next decision points

- `v0.7.1a0` formalises the two persistence boundary regimes
  (low-coupling collapse and high-coupling invisibility) as named
  theorems analogous to Theorem A / Theorem B for
  `constraint_closure`, and ships the perturbation-magnitude
  sweep deferred from `v0.7.0a0` in `docs/RAI.md`.
- `v0.7.2a0` (this release) ships the atlas-geometry analysis
  pre-registered in [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md).
  Verdict above.
- `v0.8.0a0` adds the coherence-based axis (CBA); completing
  the five lets the prediction above be evaluated for the first
  time.
- `v0.9.0a0` adds the LLM transcript adapter and the strong
  validation pass against behavioural / RAI-style data, the
  formal home of the falsification test that builds on the
  `v0.5.x`, `v0.6.x` and `v0.7.x` baselines. **The Level 2 vs
  Level 3 question, currently under-determined on the
  structural domain, is decided here or stays open.**

If at any of these checkpoints the prediction starts failing,
this document is updated honestly: PBA's status is downgraded
and the package's marketing follows.
