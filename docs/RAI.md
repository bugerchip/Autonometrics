# RAI axis — design document

> *Status: design draft for the upcoming `v0.7.0a0` release.
> This document fixes the operational decisions before any code
> is written, so the implementation can be audited against an
> explicit specification rather than reverse-engineered from
> whatever the code happens to do. This is the same discipline
> applied to the constraint-closure axis in `docs/CONSTRAINT_CLOSURE.md`.*

> *Spanish summary at the bottom of this file.*

## What this axis adds to PBA

The three axes shipped so far live in three distinct
mathematical territories:

- `ratio_endo_total` (Bertschinger / Albantakis) lives in
  **information-theoretic territory** at the level of states.
- `memory_endo_ratio` (Crutchfield) lives in
  **information-theoretic territory** at the level of statistical
  predictability.
- `constraint_closure` (Montévil & Mossio) lives in
  **graph-theoretic territory** at the level of dependencies among
  update rules.

The `v0.6.0a0` benchmark and the `v0.6.1a0` domain-of-applicability
diagnostic together established that these three axes carry
distinct information on the current adapter zoo (pairwise Pearson
`|r| < 0.7`) and that each has explicit boundary regions where it
saturates by construction.

The fourth axis, **RAI** (Relative Autonomy Index, drawn from
Deci & Ryan's Self-Determination Theory), enters from a
**fundamentally different scientific tradition**: motivational
psychology of human behaviour. The reason this matters for PBA:

- The first three axes were all developed for physical /
  computational / biological systems. A correlation among them
  could in principle still be explained by some shared structural
  bias of those traditions.
- RAI was developed for **humans completing tasks**. If a metric
  built in that universe ends up sharing the "ratio internal /
  total" signature with the previous three when applied to
  comparable systems, the convergence is much harder to dismiss
  as discipline-specific bias.

RAI therefore acts as a **cross-tradition test of the atlas
hypothesis**. If it survives the audit and shows moderate
correlation with the existing axes (without redundancy), the
"atlas of autonomy" framing introduced in `v0.6.0a0` gains
genuine interdisciplinary support. If it fails to behave like a
sibling of the other three, the atlas claim weakens specifically
on the cross-tradition dimension and we learn that the unifying
shape is narrower than hoped.

A nuance worth fixing up front: the cross-tradition test has
**two strengths**, not one. The structural proxy that this
document develops draws on philosophy-of-biology work
(Lee & McShea 2020 on persistence and plasticity; see the
"Adjacent literatures" section below), a tradition that is
closer to the existing PBA axes than SDT itself is. The
**strong** cross-tradition test — against SDT's behavioural
definition with regulation-type self-reports — is therefore
deferred to the v0.9.0 transcript adapter, where the structural
proxy can be compared directly with regulation-coded human or
agent action sequences. This document is honest about that
distinction throughout.

This document is therefore unusually conservative compared to
its predecessors: it does not commit to a single
operationalisation up front. It compares three structurally
distinct candidates, fixes explicit decision criteria, and
arrives at a provisional pick that the user reviews before any
code is written.

## Scientific background

### Self-Determination Theory (Deci & Ryan)

Self-Determination Theory (SDT) places human motivation on a
spectrum from **fully external regulation** to **fully internal
regulation**. The classical decomposition uses four to six
regulation types, ordered by degree of internalisation:

1. **External regulation.** The behaviour is performed because of
   external contingencies: rewards, punishments, deadlines,
   social pressure. The "locus of causality" is external.
2. **Introjected regulation.** The pressure has been internalised
   but not owned: the person acts to avoid guilt, to protect
   self-esteem, to comply with an internal voice that itself
   came from outside. The locus is internal but the regulation
   feels imposed.
3. **Identified regulation.** The person recognises the value of
   the behaviour and accepts it as personally important. The
   locus is internal and the regulation is endorsed.
4. **Integrated / intrinsic regulation.** The behaviour is fully
   coherent with the self. It is performed because it is
   inherently meaningful or enjoyable, not because of any
   instrumental reason.

The **Relative Autonomy Index** (RAI) collapses this spectrum
into a single number by giving the autonomous regulations
positive weight and the controlled regulations negative weight:

```
RAI = -2 * external - 1 * introjected + 1 * identified + 2 * intrinsic
```

(Several variants exist; the weights and the normalisation
differ across SDT papers, but the shape is constant: a weighted
ratio of internal-vs-external motivation.)

### Why RAI fits PBA on its face

RAI is, by construction, a **ratio internal / total** quantity:

- Numerator weights track autonomous regulations (positively
  signed) net of controlled ones (negatively signed).
- The denominator (in normalised variants) sums over all
  regulation types, making the score sit in `[-1, +1]` or, after
  affine rescaling, in `[0, 1]`.

The shape matches the PBA convention exactly. The challenge is
not the shape; it is that RAI was designed to be measured by
**self-report questionnaires** on humans, and the package's
adapter zoo contains zero entities capable of completing a
questionnaire.

### The translation problem

For RAI to enter the atlas, the package needs an
**operationalisation that:**

1. Produces a `[0, 1]` score from data the existing adapters
   already expose (state and environment trajectories, or
   causal graphs).
2. Captures the **spirit** of the autonomous-vs-controlled
   distinction in SDT, even if it can no longer use the SDT
   classification directly.
3. Is **structurally distinct** from the three existing axes,
   so that a cross-tradition correlation, if observed, is
   informative rather than engineered.

Three families of approaches exist and are evaluated below. The
candidates within the surviving family are compared in detail
in the next section.

## Adjacent literatures and prior work

The translation problem is not new. Three lines of work have
addressed neighbouring versions of it, and each one reshapes
how this document positions its own contribution. Acknowledging
them up front avoids two failure modes: claiming as new what
already exists, and mistaking adaptation for invention.

### Lee & McShea (2020) — operationalising goal-directedness

In *"Operationalizing Goal Directedness"* (Philosophy, Theory, and
Practice in Biology, 2020), Lee and McShea introduce two
quantitative metrics for systems that are intuitively
goal-directed:

- **Persistence** — "the tendency for an entity on a trajectory
  toward a goal to return to that trajectory following
  perturbations". Formalised as

  ```
  P = (G/N − R) / (1 − R)
  ```

  where `G` is the number of "good moves" (those that reduce
  distance to the goal), `N` the total number of moves, and
  `R` the chance probability of a good move under random
  movement.

- **Plasticity** — "the tendency for an entity to find a particular
  trajectory toward a goal from a variety of different starting
  points". Formalised as `Q = 1/S` where `S` is the slope of
  trajectory-length versus starting-distance for a population
  of trials.

Their argument that goal-directedness is **continuous and
multidimensional** rather than discrete and unitary is, in
essence, the same argument PBA's atlas framing makes for
autonomy in general. Their two metrics map directly onto
Candidates 1 and 2 below. The present document acknowledges
this lineage: **Candidate 1 is a generalisation of Lee & McShea's
persistence**, not an independent invention.

The differences are concrete. Lee & McShea's framework requires
an externally specified goal (chemoattractant gradient, target
ship, lecture hall) and a low-dimensional Euclidean state space
(1D or 2D). PBA's adapter zoo has neither: ECA cells do not
"pursue" anything, Kauffman networks merely iterate, and the
state spaces are high-dimensional discrete vectors. The genuine
contribution of this document, on top of Lee & McShea's
foundation, is the adaptation that lets the same conceptual
core run on systems without external goals (see "Differences
from the original Lee & McShea formulation" inside Candidate 1).

### Albantakis (2021) — comparing autonomy measures across families

In *"Quantifying the Autonomy of Structurally Diverse Automata: A
Comparison of Candidate Measures"* (Entropy, 2021), Larissa
Albantakis (whose information-theoretic measures already
underpin the closure axis in this package) compares four
families of autonomy measures on evolved Markov Brain agents:
graph-theoretical, information-theoretical, causal, and
**dynamical** (the family Candidate 1 belongs to).

Two findings from that paper are directly relevant here:

1. **Different measure families capture different aspects.**
   Albantakis explicitly identifies three aspects of autonomy
   that the measures cluster around: **self-determination**
   (how much the system determines its own internal states),
   **closure** (whether the system is independent of the
   environment), and **agency** (whether actions are
   determined by internal mechanisms). The atlas framing PBA
   adopted in `v0.6.0a0` is consistent with this.
2. **Perturbation-based measures carry information that
   observation-based ones do not.** Specifically, Albantakis
   shows that the ordering of normalised Lempel-Ziv complexity
   across task conditions is **reversed** when computed under
   perturbation versus under natural activity. This is direct
   empirical support, on a different zoo, for the independence
   prediction this document makes for Candidate 1.

The companion `autonomy` Python toolbox is at
`github.com/Albantakis/autonomy`. PBA does not depend on it,
but the cross-package comparison is a natural extension for a
future release.

### Goal-directedness in LLM agents (2025 — 2026)

Recent work has begun to operationalise goal-directedness in
language-model agents directly, not via SDT but via
behavioural signatures over agent traces. Two strands matter
for the v0.9.0 validation plan:

- **MAGELLAN** (Gaven et al., 2025) measures intrinsic
  motivation through **learning-progress prediction** in
  autotelic LLM agents.
- **Goal-directedness as an LLM property** (2026) defines it as
  "an LLM's propensity to use available resources and
  capabilities to achieve a given goal", finds that it is
  consistent across tasks, distinct from task performance, and
  only moderately sensitive to motivational prompts.

Both strands provide **ready-made validation methodology** for
the v0.9.0 transcript phase: the structural proxy this document
specifies can be correlated directly against goal-directedness
scores produced by such methods on LLM transcripts, without the
package having to invent its own behavioural classifier.

### What stays unique to PBA

Three things are not covered by the adjacent literatures and
remain genuine PBA contributions:

1. **Adaptation to systems without external goals.** Lee & McShea
   require an externally specified goal; PBA's zoo does not
   have one. The adaptation (treating the unperturbed natural
   trajectory as the implicit goal, using Hamming distance in
   high-dimensional discrete state) is new.
2. **Integration into a multi-axis atlas.** Albantakis compares
   measures on a single zoo; she does not claim a multi-axis
   atlas with cross-axis falsification thresholds. PBA does.
3. **Pre-registered cross-tradition test.** Neither Lee & McShea
   nor Albantakis pre-register the comparison against SDT's
   behavioural RAI on transcript data. PBA's v0.9.0 plan does,
   with a fixed correlation threshold for promotion of the
   structural proxy.

The package therefore positions itself as a **synthesiser**:
it integrates Lee & McShea's persistence-and-plasticity
framework, Albantakis's comparative methodology, and SDT's
motivational vocabulary, into a single multi-axis instrument
with explicit falsification rules. The contribution is in the
synthesis and the discipline, not in inventing the underlying
metrics from scratch.

## Approaches not pursued in v0.7.0

### Path I — Reuse the information-theoretic split

The most direct translation would be to reinterpret the SDT
external-vs-internal contrast as an information-theoretic
decomposition: how much of `S_{t+1}` is explained by `S_t` (the
"internal" component) versus by `E_t` (the "external"
component).

This is rejected as a candidate for the same reason `ratio_endo_total`
was already implemented: an information-theoretic version of
"internal vs external" already exists as the closure axis. A
second metric built on the same machinery would correlate by
construction with `closure` and fail the independence-by-design
audit. PBA would gain a label without gaining a dimension.

The package therefore does not pursue this path.

### Path II — Wait for transcript adapters

The most honest translation would be to keep RAI tied to its
original behavioural meaning and only measure it on systems
whose actions come with declared reasons: LLM transcripts, agent
reasoning traces, conversational logs. A behavioural classifier
would tag each action by its regulation type; the RAI score
would be a weighted aggregate over the tagged actions.

This is rejected as the **sole** approach for v0.7.0 for two
reasons:

1. **It defers the release.** The transcript adapter is
   currently scheduled for `v0.9.0`. Making RAI depend on it
   reorders the roadmap so that v0.7.0 ships without a benchmark,
   which breaks the package's discipline of pairing every new
   axis with a benchmark snapshot.
2. **It removes the controllable-systems baseline.** Without a
   structural operationalisation that runs on the existing zoo,
   when transcripts arrive there is no reference distribution
   to compare against. "Is RAI = 0.43 on this conversation
   high or low?" becomes impossible to answer honestly.

Path II is therefore deferred to **v0.9.0** as the **validation
phase**, not as the primary operationalisation. The structural
proxy chosen below in v0.7.0 is the proxy whose correspondence
with transcript-based RAI is the test the v0.9.0 benchmark will
run.

### Path III — Invent a structural signature on the existing zoo

The remaining option, and the one this document develops, is to
**invent a structural signature** that:

- Runs on any system implementing the existing `AutonomySystem`
  protocol.
- Captures the SDT distinction between "the system pursues
  something of its own" and "the system is pulled around by
  external forces".
- Is mathematically independent of the three existing axes.

The word *invent* is used here in the **measurement sense**, not
in the **ontological sense**: the same kind of invention as
inventing a thermometer to quantify heat, or as Spearman
inventing IQ tests to quantify cognitive ability. The goal is
not to invent a new entity called "structural autonomous
motivation". The goal is to invent a **measurement procedure**
that, if validated against the behavioural definition in v0.9.0,
turns out to track what RAI was meant to track.

The next section compares three structurally distinct candidates
within Path III.

## Three candidate structural signatures

Each candidate is evaluated on the same five criteria (mapping
to SDT, expected independence, applicability to the zoo,
computational cost, robustness to parameters). The evaluations
are pre-committed: they are written before any code is run, so
the choice cannot be retrofitted to convenient empirical
results.

### Candidate 1 — Perturbation persistence (Lee & McShea-style)

**Provenance.** This candidate is a generalisation of Lee &
McShea's (2020) persistence metric to systems without
externally specified goals. The conceptual core
(persistence as the tendency to return to a preferred
trajectory after perturbation) is theirs; the adaptation to
PBA's adapter zoo is new and is documented in a dedicated
subsection below.

**Definition.** At a randomly chosen step `t*` in the system's
trajectory, inject a small bounded perturbation to the state
`s_{t*}` (for binary states, flip a single bit; for discrete
states, advance by one). Run the system forward from the
perturbed state under the same environment. Compare the
perturbed trajectory `s'_{t*+k}` to the unperturbed baseline
`s_{t*+k}` over the next `K` steps.

A system that absorbs the perturbation has the two trajectories
re-converging quickly. A system that propagates the perturbation
has the trajectories diverging and staying apart. In Lee &
McShea's vocabulary, the unperturbed trajectory plays the role
of the **goal**, and a "good move" is any step that reduces
distance to that goal trajectory.

**Score.** Two equivalent presentations are useful.

The Lee & McShea form, adapted to the PBA setting, is:

```
RAI_proxy_1 = (G/N − R) / (1 − R)
```

where `G` is the number of post-perturbation steps that reduce
Hamming distance to the unperturbed trajectory, `N` is the
total number of post-perturbation steps over all perturbation
trials, and `R` is the chance baseline computed per adapter (see
the adaptations subsection below).

The equivalent distance-based form, more convenient for
implementation, is:

```
RAI_proxy_1 = clip( 1 − d̄ / d_ref , 0, 1 )
```

where `d̄` is the mean Hamming distance between perturbed and
unperturbed trajectories over `K` lookahead steps, averaged
over `M` perturbation times and several seeds, and `d_ref` is
the reference scale corresponding to two independent random
trajectories of the same alphabet (for binary states with
balanced distribution, `d_ref ≈ 0.5`).

`RAI_proxy_1 = 1` means perturbations are absorbed perfectly
(the system returns to its natural trajectory); `RAI_proxy_1 = 0`
means perturbations propagate as much as random noise (no
internal pull).

**Mapping to SDT.** A person in autonomous regulation has a
preferred course of action that they return to when an external
pressure pushes them off it. A person in controlled regulation
has no such preferred course; whatever pushes them defines what
they do next. Perturbation persistence is a structural analogue:
the system has *something to defend* against external
disturbance.

**Differences from the original Lee & McShea formulation.**

The PBA adaptation differs from the published persistence
metric on four points. They are listed here so that any later
reviewer can audit the gap between the published method and
this package's variant.

1. **Implicit goal versus explicit goal.** Lee & McShea require
   an externally specified goal (a chemical gradient, a target
   ship, a destination). The PBA zoo has no such goal: ECA
   cells do not pursue, Kauffman networks merely iterate. The
   adaptation treats the **system's own unperturbed
   trajectory** as the implicit goal. A good move is one that
   brings the perturbed trajectory closer to the unperturbed
   one.
2. **Hamming distance versus Euclidean distance.** Lee & McShea
   work in 1D or 2D Euclidean physical space. The PBA zoo
   works in high-dimensional discrete state vectors (51-bit
   ECA rows, 10-node Kauffman states, etc.). The adaptation
   uses Hamming distance, which is the natural metric for
   discrete-state trajectories.
3. **Computed baseline `R` versus geometric baseline.** Lee &
   McShea use `R = 0.5` for unbounded 1D space because
   chance-of-good-move is geometrically determined. The
   adaptation **computes `R` per adapter** by sampling
   independent random trajectories of the same length and
   alphabet; this is necessary because the discrete-state
   geometry varies across adapters and can be far from 0.5
   for sparsely-occupied state spaces.
4. **Multi-perturbation averaging.** Lee & McShea apply their
   metric to a single trial trajectory of a single entity. The
   adaptation averages over many perturbation times and seeds,
   producing a population-level estimate that is robust to the
   specific time at which the perturbation lands.

The intuition and the formula structure are Lee & McShea's. The
discrete-state, no-external-goal extension is the PBA
contribution. Both halves should be cited explicitly when the
metric is reported.

**Expected behaviour:**

- Strong attractors (point fixed-points, short cycles) → high.
- Chaotic regimes (perturbations grow exponentially) → low.
- Periodic systems with full state coverage → high.
- Stochastic systems with no internal structure → low.

**Pros.**

- Operationally simple; one perturbation experiment per
  configuration.
- Independent of `closure` (which measures information flow,
  not dynamical resilience).
- Independent of `constraint_closure` (which measures graph
  topology, not perturbation behaviour).
- Universal: any adapter exposing `get_state_history` and
  `get_env_history` is measurable.

**Cons.**

- Sensitive to the choice of perturbation magnitude (a single
  bit-flip vs a larger jump may give different scores).
- For deterministic systems whose state space is tiny (e.g.
  `PeriodicCycle` with `n = 1`), the perturbation may cycle
  the system through its only other state and back, giving
  trivial high scores.
- Captures resilience but not the "goal pull" facet that
  Candidate 2 captures more directly.

### Candidate 2 — Plasticity / attractor convergence (Lee & McShea-style)

**Provenance.** This candidate is a generalisation of Lee &
McShea's (2020) plasticity metric. Their formulation defines
plasticity as the tendency of a system to find a particular
trajectory toward a goal from a variety of starting points,
formalised as `Q = 1/S` with `S` the slope of trajectory-length
versus starting-distance. The adaptation here keeps the
"many-initial-conditions" core but reframes the count toward
attractor convergence (since the PBA zoo has no externally
defined goals to measure trajectory length to).

**Definition.** Run the system from `M` distinct random initial
conditions, each for `K` steps, under the same environment
schedule. Record the final state (or short cycle of states) of
each run. Cluster the final states; count the number of
**distinct attractors** found.

A system that pulls many initial conditions to the same
attractor has *something to converge towards*. A system whose
final state depends entirely on the initial condition has no
such common pull.

**Score.** Let `A` be the number of distinct attractors found
among `M` runs. Define:

```
RAI_proxy_2 = 1 - (A - 1) / (M - 1)
```

`RAI_proxy_2 = 1` means all runs converge to the same attractor
(`A = 1`); `RAI_proxy_2 = 0` means every run finds its own
attractor (`A = M`).

**Mapping to SDT.** A person with strong autonomous regulation
exhibits **consistent goal-directed behaviour across contexts**;
the behaviour is identifiable as "this person, doing what they
do" regardless of the starting situation. A person whose
behaviour is fully reactive does whatever the local situation
demands; there is no consistent direction across contexts.
Attractor convergence is the structural analogue.

**Expected behaviour:**

- Single fixed-point attractor → 1.
- Multiple disjoint attractors → low.
- Frozen Kauffman regime (`K = 1`) → typically high.
- Chaotic Kauffman regime (`K = 9`) → typically low.

**Pros.**

- Captures the "goal pull" facet of SDT directly.
- Easy to interpret (`A = 1` versus `A = M` is intuitive).
- Independent of `closure` (which does not measure
  initial-condition dependence) and of `constraint_closure`
  (graph-topological).

**Cons.**

- Computationally heavier: requires `M` independent runs per
  configuration.
- The clustering step (deciding what counts as the same
  attractor) introduces a free parameter.
- For periodic systems with full state coverage, can
  trivially saturate (all runs end on the same cycle).
- Sensitive to the run length `K`; transients may look like
  separate attractors for short `K`.

### Candidate 3 — Auto-generation of structure

**Definition.** Run the system **twice** under the same initial
condition, with two different environment schedules:

- **Natural environment**: the original `E_t`.
- **Flat environment**: `E_t = 0` (or a constant baseline) for
  all `t`.

Measure the **Shannon entropy** of the resulting state
trajectory in each case. The intuition: a system that produces
rich behaviour from itself has high entropy under flat
environment; a system that depends on the environment for its
variability has low entropy under flat environment.

**Score.** Let `H_flat` and `H_natural` be the state-trajectory
entropies under the two schedules. Define:

```
RAI_proxy_3 = clip( H_flat / H_natural , 0, 1 )
```

`RAI_proxy_3 = 1` means the system is as rich without
environment as with it; `RAI_proxy_3 = 0` means the system is
inert without environmental input.

**Mapping to SDT.** A person with strong autonomous regulation
continues to act, create, and engage even in low-stimulus
environments. A person with strong external regulation becomes
inert without external prompts. The ratio of internal-vs-natural
state entropy is the structural analogue.

**Expected behaviour:**

- Self-generated dynamics with rich trajectories → high.
- Environment-driven systems (e.g. the `external` mode of
  `SimpleAutomaton`) → low.
- Periodic-cycle adapters (no real environment dependence) →
  trivially high (a known degenerate case).

**Pros.**

- Conceptually elegant; directly captures the
  "produce-from-within" intuition.
- Cheap to compute (one extra trajectory per configuration).

**Cons.**

- **Independence risk.** Closure is essentially `I(S_{t+1}; S_t |
  E_t)`. Auto-generation under fixed `E` is a closely related
  measurement: it asks "how much state structure remains when
  we flatten the environment", which is operationally not far
  from "how much of the next state is determined by the
  current state given the environment". Empirically this is
  expected to correlate with `closure` more strongly than the
  other two candidates would.
- Requires the system to have a meaningful "no-environment"
  mode. Some adapters (especially `ECASystem` whose environment
  *is* part of the dynamics) may not admit a clean `E = 0`
  setting.
- Sensitive to entropy estimation choices on short trajectories.

## Comparative table

The three candidates are scored on the five criteria fixed in
the design discussion. Scores are tentative and pre-committed:
the empirical phase will revise them.

| Criterion | Candidate 1 (perturbation) | Candidate 2 (attractors) | Candidate 3 (auto-generation) |
|---|---|---|---|
| Mapping to SDT | clear (defends the trajectory) | clear (pursues a goal) | clear (produces from within) |
| Expected independence from `closure` | high | high | **low — primary risk** |
| Expected independence from `constraint_closure` | high | high | high |
| Applicability across the existing zoo | universal | universal but expensive | **partial — needs flat-env mode** |
| Computational cost | low (one extra run per cfg) | medium (`M` runs per cfg) | low (one extra run per cfg) |
| Robustness to free parameters | medium (perturbation size) | low (clustering rule, `K`) | medium (entropy estimator) |
| Compactness of statement | one number, one experiment | one number, `M` runs | one number, two runs |

## Decision criteria

The design fixes three rules, ordered by priority, for choosing
the operationalisation. Ordering matters: a candidate that fails
a higher-priority rule is rejected even if it scores best on
lower-priority rules.

1. **Independence first.** If a candidate is **structurally
   close** to one of the existing axes (especially `closure`),
   it is rejected regardless of conceptual elegance. The
   independence-by-design audit (no imports of the other
   metric modules) and the empirical correlation threshold
   (`|r| < 0.7` on the benchmark zoo) both apply.
2. **Conceptual mapping second.** Among candidates that pass
   the independence test, the one whose definition maps most
   directly to the SDT distinction wins.
3. **Simplicity as tie-break.** If two candidates remain
   indistinguishable after the first two rules, the simpler
   one wins. Simpler here means fewer free parameters and
   fewer adapter-specific assumptions.

## Provisional pick: Candidate 1 (perturbation resistance)

Applying the criteria in order:

- **Rule 1 (independence).**
  - Candidate 3 fails: auto-generation under flat `E` is
    operationally close to `closure` and the audit is expected
    to surface a high empirical correlation. Rejected.
  - Candidates 1 and 2 pass: perturbation resistance and
    attractor convergence both measure dynamical properties
    that closure (information flow) and constraint
    (graph topology) do not directly capture.
- **Rule 2 (conceptual mapping).** Both surviving candidates
  map cleanly to SDT, but on different facets:
  - Candidate 1 maps the **autonomy-vs-control** facet: does
    the system *defend* its course against external pressure?
  - Candidate 2 maps the **goal-directedness** facet: does
    the system *pursue* a particular target?
  SDT actually distinguishes both, but RAI itself is a single
  number that the SDT literature treats as primarily about
  autonomy-vs-control. Candidate 1 is therefore the closer
  conceptual match to the original RAI score.
- **Rule 3 (simplicity).** Candidate 1 has one free parameter
  (perturbation magnitude) and one experiment per configuration.
  Candidate 2 has the clustering rule plus the run length plus
  the number of initial conditions. Candidate 1 is simpler.

The design therefore picks **Candidate 1 (perturbation
resistance)** as the structural proxy for v0.7.0.

### Why Candidate 2 is documented but deferred

Candidate 2 is not discarded permanently. It captures a facet
of SDT that Candidate 1 does not (goal pull rather than
trajectory defence). A future release may add it as a
**second component** of RAI — a vector-valued
extension — once Candidate 1 has been validated against
transcript-based RAI in v0.9.0. This document records the
reasoning so that a later contributor sees the deferred option
explicitly rather than independently rediscovering it.

### Why Candidate 3 is rejected

Candidate 3 is rejected on independence grounds: the empirical
correlation with `closure` is expected to exceed the threshold,
and the structural relationship to `closure` is too direct for
the safeguard of pre-registration to absorb it. The conceptual
elegance does not save it from the redundancy risk that the
package is explicitly designed to prevent.

## Per-adapter predictions (Candidate 1)

The predictions are written before any code is run. If the
empirical scores diverge from these predictions in a systematic
way, the operationalisation is judged inadequate and the
implementation does not ship.

| Adapter / configuration | Expected `RAI_proxy_1` | Reasoning |
|---|---:|---|
| `PeriodicCycle` (period 2) | 0.7 — 1.0 | A bit-flip on a period-2 cycle either lands on the next cycle state (no divergence) or breaks the cycle (a few-step transient before re-convergence). Expected to score high. |
| `PeriodicCycle` (period 3+) | 0.7 — 1.0 | Same logic; longer transient possible but absorbed by the closed cycle. |
| `ECASystem` rule 110 | 0.3 — 0.6 | Rule 110 is universal-computation; perturbations propagate but are constrained by the rule's structured patterns. Mid-range expected. |
| `ECASystem` rule 30 | 0.0 — 0.2 | Rule 30 is chaotic; perturbations grow exponentially. Low expected. |
| `ECASystem` rule 90 | 0.1 — 0.3 | Rule 90 is fractal (XOR of neighbours); perturbations spread linearly with structured shape. Low-mid expected. |
| `ECASystem` rule 184 | 0.4 — 0.7 | Rule 184 has stable density (traffic-flow analogue); perturbations partially absorbed. Mid expected. |
| `KauffmanNetwork` `K = 1` | 0.6 — 0.9 | Frozen regime; typically converges to point fixed-points that absorb perturbations. High expected. |
| `KauffmanNetwork` `K = 3` | 0.3 — 0.6 | Edge of chaos; mixed absorption / propagation. Mid expected. |
| `KauffmanNetwork` `K = 9` | 0.0 — 0.2 | Chaotic regime on `n = 10`; perturbations propagate to most of the network. Low expected. |
| `SimpleAutomaton.self_generated` | 0.5 — 0.9 | Depends on the self-rule; a stable rule absorbs, a noisy rule does not. Wide expected band. |
| `SimpleAutomaton.external` | 0.0 — 0.2 | By construction, the state is environment-driven. A perturbation to the state is overwritten on the next step. Low expected. |

The most discriminating predictions are the two that the
existing axes cannot separate:

- `ECASystem` rule 30 vs rule 110 (both saturate `closure = 1.0`
  and `constraint = 1.0`; predicted RAI_proxy gap: 0.3 — 0.6).
- `SimpleAutomaton.self_generated` vs `SimpleAutomaton.external`
  (both have `constraint = 0.0`; predicted RAI_proxy gap:
  0.5 — 0.9).

If RAI_proxy_1 fails to separate either of these pairs in the
empirical run, the operationalisation has not earned its place
in the atlas.

## Falsification thresholds

The implementation does not ship unless **all three** of the
following pass:

1. **Discrimination on saturated pairs.** The two pairs above
   must show a mean RAI_proxy_1 difference of at least 0.25
   on the benchmark seeds.
2. **Independence by design (static).** The metric module
   `src/autonometrics/metrics/rai.py` (or chosen filename) must
   not import any function from `metrics.albantakis`,
   `metrics.memory_ratio` or `metrics.constraint_closure`. A
   test asserts the import graph.
3. **Independence by design (empirical).** On the four-axis
   benchmark, the Pearson correlation between `RAI_proxy_1`
   and each of the three existing axes must satisfy `|r| < 0.7`.
   Spearman correlations are reported alongside but do not gate
   the release on their own.

If any of the three fails, the design returns to the comparison
table and the next-best surviving candidate is considered.

## Independence-by-design guarantees

Two layers of safeguard, mirroring the constraint-closure axis:

- **Static layer.** The metric module imports only `numpy` and
  the project's own protocol types. A unit test asserts the
  import graph does not touch the modules listed under
  threshold 2. This makes any future "engineered correlation"
  visible at code-review time, before it can show up in a
  benchmark.
- **Empirical layer.** The four-axis benchmark reports the
  pairwise correlations. A correlation that drifts above the
  threshold across releases triggers a domain-of-applicability
  diagnostic, mirroring the v0.5.1a0 saturation diagnostic and
  the v0.6.1a0 density diagnostic.

The two layers are deliberately redundant: the static layer
catches construction-driven correlations; the empirical layer
catches data-driven ones.

## Provisional status and validation plan

`RAI_proxy_1` is a **structural proxy** for the autonomous-vs-
controlled motivation distinction in SDT. It is **not** the
behavioural RAI score that Deci & Ryan defined for human
self-reports. The package documents this gap explicitly:

- README and CHANGELOG entries refer to the metric as
  *"structural autonomous-motivation proxy (RAI-style)"*, never
  as *"RAI"* unqualified.
- The metric's docstring in code repeats the disclaimer.
- `docs/PBA.md` notes that the four-axis atlas's fourth
  dimension is currently a structural proxy whose **strong
  validation** is deferred to v0.9.0.

The validation plan is concrete and uses **two complementary
references**, since the SDT literature itself has moved on from
the original weighted RAI formula:

1. **v0.9.0 ships the LLM transcript adapter.** That adapter
   exposes per-action regulation labels (external,
   introjected, identified, intrinsic) either via human
   annotation or via a behavioural classifier.
2. **Reference 1 — Comprehensive RAI (C-RAI), unweighted form.**
   The 2017 work by Sheldon et al. (and follow-ups,
   including the 2024 CRAI-Drinking validation) finds that the
   **unweighted aggregate** of regulation subscales is the
   most unbiased indicator of motivation quality in a
   behavioural domain — outperforming the original
   `(2 × intrinsic + identified) − (2 × external + introjected)`
   weighting. The v0.9.x diagnostic therefore correlates
   `RAI_proxy_1` against the unweighted C-RAI score, not the
   classical RAI score.
3. **Reference 2 — Goal-directedness scoring on LLM transcripts.**
   The 2025 — 2026 LLM agency literature (MAGELLAN; the 2026
   goal-directedness paper) provides an alternative
   behavioural reference that is closer to PBA's structural
   proxy in mechanism: it scores behavioural goal-pursuit
   directly. The v0.9.x diagnostic correlates `RAI_proxy_1`
   against goal-directedness scores on transcript adapters in
   parallel.
4. **Validation criterion.** A Pearson correlation of at least
   `+0.5` between `RAI_proxy_1` and **either** of the two
   behavioural references on a held-out conversation corpus is
   the threshold for promoting the proxy from *structural
   proxy* to *validated structural correlate*. Two references
   give two independent chances to pass; failure on both is
   meaningful evidence of disconnection.
5. **Negative outcome handled.** If both correlations fall
   below the threshold, the package documents that the
   structural proxy and the behavioural references measure
   distinct facets of motivation. The proxy is not removed; it
   is reframed as "structural autonomy", and a separate
   transcript-based metric is added as a fifth axis if
   warranted by the data.

This plan keeps the package honest in two directions: the
v0.7.0 release does not claim what it has not earned, and the
v0.9.0 release has a pre-committed test (against two
references) that can fail.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Perturbation magnitude is the wrong size for a given adapter (too small to affect anything, too large to be a perturbation). | Run a magnitude sweep in the v0.7.x diagnostic; fix one canonical magnitude per adapter type. |
| Some adapters have tiny state spaces (e.g. `PeriodicCycle` with `n = 1`); the perturbation forces a known false-positive zone. | Document this as a Theorem in the eventual `v0.7.1a0` domain-of-applicability section, mirroring Theorems A and B for constraint-closure. |
| The empirical correlation with `closure` is borderline (around `|r| ≈ 0.6 — 0.7`). | Pre-commit the threshold and abide by it. If the metric falls just above the threshold, return to Candidate 2 in the next minor release rather than relax the threshold. |
| Validation in v0.9.0 yields `r < 0.5`. | Reframe the proxy as a structural-only axis; do not fold it back into "RAI" terminology. |

## Implementation sketch (non-binding)

The following is a **non-binding** sketch of how the metric
would be implemented under the v0.7.0 locked naming
(`rai_proxy_persistence` in code, `persistence` as the axis
label). The exact API is fixed in the v0.7.0 implementation
phase.

```python
def compute_rai_proxy_persistence(
    states: np.ndarray,
    env: np.ndarray,
    transition_fn: Callable[[int, int], int],
    *,
    n_perturbations: int = 32,
    horizon: int = 64,
    rng: np.random.Generator | None = None,
) -> float:
    """Structural autonomous-motivation proxy
    (Lee & McShea-style persistence) via single-bit perturbation.

    Parameters
    ----------
    states : 1-D array of recorded system states (alphabet inferred).
    env    : 1-D array of recorded environment states (same length).
    transition_fn : callable that, given (state, env), returns the
        next state under the system's own rule. Adapters expose
        this as a method or via a stored rule table.
    n_perturbations : how many random (time, magnitude=1) bit-flips
        to apply.
    horizon : how many steps to follow the perturbed trajectory.
    rng : optional numpy RNG.

    Returns
    -------
    score : float in [0, 1]. 1 = perturbations fully absorbed,
        0 = perturbations behave like noise.
    """
```

The metric depends on `transition_fn`. This is the one new piece
of API every adapter has to expose, alongside
`get_state_history`, `get_env_history` and `get_causal_graph`.
The implementation phase fixes the protocol extension explicitly.

## Why this design is conservative

This document differs from `docs/CONSTRAINT_CLOSURE.md` in that
it does **not** ship a single fixed operationalisation. It
records three candidates, applies pre-committed criteria, and
arrives at a provisional pick. The reasons:

- The conceptual leap to motivational psychology is larger than
  any earlier leap in the package. The protection against
  picking a poor operationalisation is correspondingly larger.
- Recording the rejected candidates leaves a trail. If the
  picked operationalisation fails in implementation or in
  validation, the package can pivot to Candidate 2 without
  re-discovering the comparison.
- The atlas framing established in v0.6.0a0 places higher
  evidential demands on the fourth axis: it is the first
  cross-tradition test, and the scrutiny it will face from
  any reader is heavier than the scrutiny faced by the
  third axis.

The conservatism is the package's discipline showing up at the
moment that most needs it.

## Design decisions (locked v0.7.0)

The following four decisions were open during the design phase
of this document. They were resolved by explicit user
confirmation before any code was written. Each entry records
the question that was open, the decision taken, and the reason.
This audit trail is preserved here (rather than in chat logs
or a separate notes file) so that any future reviewer can trace
why the implementation looks the way it does.

1. **Final pick — locked: Candidate 1.**
   - **Open question.** Accept Candidate 1 (perturbation
     persistence, Lee & McShea-style) as the v0.7.0
     operationalisation, with Candidate 2 deferred and
     Candidate 3 rejected?
   - **Decision.** Yes. Candidate 1 ships in v0.7.0;
     Candidate 2 is documented as a possible future
     vector-valued extension; Candidate 3 is rejected
     definitively.
   - **Reason.** Candidate 1 wins the three decision criteria
     in order (independence, conceptual mapping, simplicity)
     and has direct lineage to Lee & McShea's published
     persistence metric, which strengthens defensibility.

2. **Perturbation magnitude — locked: single bit-flip default,
   no sweep in v0.7.0.**
   - **Open question.** Default to a single bit-flip on binary
     adapters, or build a magnitude sweep into v0.7.0 from the
     start?
   - **Decision.** Single bit-flip is the v0.7.0 default. A
     magnitude sweep ships **separately** in a `v0.7.1`
     maintenance cycle, mirroring the pattern established by
     `v0.5.1` (saturation diagnostic) and `v0.6.1` (constraint
     density diagnostic). The diagnostic file will be
     `examples/perturbation_magnitude_diagnostic.py`.
   - **Reason.** Keeps v0.7.0 minimal and shippable, preserves
     the project's "release minimal core, then ship a domain-
     of-applicability diagnostic" cadence, and avoids
     conflating "what is the metric?" with "how does it
     behave under different perturbation regimes?" — those
     are two distinct questions and deserve two releases.

3. **Adapter API extension — locked: `transition_fn` as
   `Optional`.**
   - **Open question.** Add `transition_fn` to the
     `AutonomySystem` protocol (cleaner, requires every
     adapter to expose it), or use a perturbation hook on
     `get_state_history` (uglier but adapter-agnostic)?
   - **Decision.** Add `transition_fn` as an **optional**
     method on the protocol. Adapters that expose it (ECA,
     Kauffman, SimpleAutomaton, PeriodicCycle) become
     measurable on this axis. Adapters that cannot expose it
     (CSVTrajectory replay-only) return `None` for
     `rai_proxy_persistence`, and the benchmark CSV records
     `n_valid` accordingly.
   - **Reason.** Mirrors the pattern already established in
     `v0.6.0a0` for `get_causal_graph()`, which is also
     `Optional`. Honours the "fail loudly, return None"
     principle: replay-only adapters cannot answer
     counterfactual questions and the package says so
     explicitly instead of fabricating a score.

4. **Naming — locked: `rai_proxy_persistence` (code), Lee &
   McShea-style persistence (prose), `persistence` (axis
   label).**
   - **Open question.** Use `rai_proxy_resistance` in code and
     *"structural autonomous-motivation proxy (RAI-style)"* in
     prose, or revise?
   - **Decision (revised default).**
     - Code identifier: `rai_proxy_persistence` (function name
       and dict key in `Autonometer` results).
     - Long-form prose label: *"structural autonomous-motivation
       proxy (Lee & McShea-style persistence)"*.
     - Short PBA atlas axis label: `persistence` (one word,
       symmetric with `closure`, `memory`, `constraint`).
   - **Reason.** Once the doc commits explicitly to Lee &
     McShea's lineage, the canonical term in their paper is
     **persistence**, not "resistance". Using their vocabulary
     in code makes the citation traceable from the source
     itself; using "resistance" would silently obscure the
     lineage and look like an independent invention. The
     short axis label `persistence` keeps the atlas readable
     in tables and plots.

These four decisions are now binding for the v0.7.0
implementation cycle. Any deviation during coding requires an
explicit doc edit (and a note in `CHANGELOG.md`), not a silent
divergence.

## References

### Self-Determination Theory and the original RAI

- Deci, E. L., & Ryan, R. M. (2000). *The "what" and "why" of
  goal pursuits: Human needs and the self-determination of
  behavior*. Psychological Inquiry 11(4), 227 — 268.
- Ryan, R. M., & Deci, E. L. (2017). *Self-Determination Theory:
  Basic Psychological Needs in Motivation, Development, and
  Wellness*. The Guilford Press.
- Grolnick, W. S., & Ryan, R. M. (1989). *Parent styles
  associated with children's self-regulation and competence in
  school*. Journal of Educational Psychology 81(2), 143 — 154.
  (Original weighted RAI scoring formula.)
- Sheldon, K. M., Osin, E. N., Gordeeva, T. O., Suchkov, D. D.,
  & Sychev, O. A. (2017). *Evaluating the Dimensionality of
  Self-Determination Theory's Relative Autonomy Continuum*.
  Personality and Social Psychology Bulletin 43(9), 1215 — 1238.
  (Comprehensive RAI / C-RAI; finds unweighted aggregate
  outperforms the classical weighted formula.)

### Goal-directedness and structural autonomy

- Lee, J. G., & McShea, D. W. (2020). *Operationalizing Goal
  Directedness: An Empirical Route to Advancing a Philosophical
  Discussion*. Philosophy, Theory, and Practice in Biology
  12(5). (Foundational paper for **persistence** and
  **plasticity** as quantitative measures of goal-directedness;
  direct conceptual ancestor of Candidate 1 and Candidate 2 in
  this document.)
- Albantakis, L. (2021). *Quantifying the Autonomy of
  Structurally Diverse Automata: A Comparison of Candidate
  Measures*. Entropy 23(11), 1415. (Cross-family comparison
  of structural, information-theoretic, causal, and dynamical
  autonomy measures, including perturbation-based metrics.
  Empirical evidence that perturbation-based measures carry
  information distinct from observation-based ones, on
  evolved Markov Brain agents. Companion toolbox at
  `github.com/Albantakis/autonomy`.)
- Bertschinger, N., Olbrich, E., Ay, N., & Jost, J. (2008).
  *Autonomy: an information theoretic perspective*. BioSystems
  91(2), 331 — 345. (Foundational paper for the closure axis
  and the `A_m` measure; cited here for the comparative
  framing used in Candidate 3's rejection.)

### Adjacent measures and validation references

- Ashby, W. R. (1947). *Principles of the Self-Organizing
  Dynamic System*. Journal of General Psychology 37(2),
  125 — 128. (Background on perturbation resistance and
  homeostasis as a structural signature of agency.)
- Crutchfield, J. P., & Young, K. (1989). *Inferring statistical
  complexity*. Physical Review Letters 63(2), 105 — 108.
  (Background on attractor convergence in dynamical systems.)
- Kauffman, S. A. (1969). *Metabolic stability and epigenesis in
  randomly constructed genetic nets*. Journal of Theoretical
  Biology 22(3), 437 — 467. (Background on K-regime transitions
  used in the per-adapter predictions.)
- Gaven et al. (2025). *MAGELLAN: Metacognitive predictions of
  learning progress guide autotelic LLM agents in large goal
  spaces*. ICML / RLC 2025. (Reference for the v0.9.0 LLM
  validation phase; intrinsic motivation via learning-progress
  prediction.)
- Goal-directedness as an LLM property (2026). Recent paper
  defining goal-directedness as "an LLM's propensity to use
  available resources and capabilities to achieve a given
  goal"; finds it consistent across tasks and distinct from
  task performance. (Reference for the v0.9.0 LLM validation
  phase; behavioural reference for the structural proxy.)

---

## Resumen en español

Este documento fija las decisiones de diseño para el cuarto eje
de PBA, **RAI** (Relative Autonomy Index, de la Self-Determination
Theory de Deci & Ryan), antes de escribir cualquier código. La
lógica del documento, en orden:

1. **Por qué este eje.** Los tres ejes existentes vienen de
   física, biología e información. RAI viene de psicología
   motivacional humana, una tradición distinta. Si encaja en
   PBA con la firma "ratio interno / total", el atlas gana
   apoyo interdisciplinario real. Matiz: el test cross-tradicion
   fuerte (contra SDT conductual) queda diferido a v0.9.0; lo
   que se hace en v0.7.0 es construir un proxy estructural
   sobre la base de literatura adyacente (Lee & McShea 2020,
   Albantakis 2021).
2. **El problema de traducción.** RAI se mide originalmente con
   cuestionarios. Las redes Kauffman no llenan cuestionarios.
   Hay que operacionalizarlo de otra forma sin perder su
   significado.
3. **Literaturas adyacentes que reconocemos.** Tres líneas de
   trabajo previo enmarcan lo que hacemos:
   - **Lee & McShea (2020)** ya operacionalizaron persistencia
     y plasticidad como métricas cuantitativas de
     goal-directedness en sistemas con objetivo externo. Sus
     dos métricas son los ancestros directos de Candidatos 1 y
     2 en este documento.
   - **Albantakis (2021)** ya comparó cuatro familias de
     medidas de autonomía sobre Markov Brains evolucionados,
     incluyendo análisis bajo perturbación. Encontró que las
     medidas basadas en perturbación cargan información
     distinta de las basadas en observación — evidencia
     empírica directa para nuestra predicción de
     independencia.
   - **Goal-directedness en LLMs (2025–2026)** provee
     metodología lista para la fase de validación v0.9.0.
4. **Tres caminos posibles, dos descartados:**
   - **Camino I** (rehacer la separación info-teórica) se
     descarta porque colapsaría con `closure`.
   - **Camino II** (esperar al adapter de transcripts) se
     difiere a v0.9.0 como **fase de validación**.
   - **Camino III** (firma estructural en el zoológico actual)
     es el que se desarrolla aquí. No es invento puro: es
     **adaptación** del marco Lee & McShea a sistemas sin
     objetivo externo.
5. **Tres candidatos para la firma estructural:**
   - **Candidato 1 — persistencia a perturbaciones (estilo
     Lee & McShea).** Empuja al sistema y mide cuánto vuelve a
     su rumbo. Generalización de su fórmula
     `P = (G/N − R)/(1 − R)` a estado discreto sin objetivo
     externo.
   - **Candidato 2 — plasticidad / convergencia a atractores
     (estilo Lee & McShea).** Arranca desde muchas condiciones
     iniciales y cuenta cuántas terminan en el mismo lugar.
   - **Candidato 3 — auto-generación de estructura.** Aplana el
     ambiente y mide cuánta riqueza queda en la trayectoria.
     Sin precedente claro en la literatura adyacente; rechazado
     por riesgo de redundancia con `closure`.
6. **Criterios de decisión ordenados:** primero independencia,
   segundo mapeo conceptual, tercero simplicidad.
7. **Pick provisional: Candidato 1.** Pasa independencia,
   mapea directamente a la dimensión autonomía-vs-control de
   SDT, es la más simple, y tiene linaje canónico (Lee &
   McShea 2020). Candidato 2 queda documentado para un posible
   eje vector-valuado en futuras versiones. Candidato 3 se
   rechaza.
8. **Predicciones por adapter** escritas antes de codear,
   incluyendo dos pares discriminantes (rule 30 vs rule 110;
   self_generated vs external) que los otros tres ejes no
   separan.
9. **Umbrales de falsificación** triples: discriminación en
   pares saturados, audit estático de imports, audit empírico
   `|r| < 0.7`.
10. **Status provisional y plan de validación.** En v0.7.0 se
    reporta como **proxy estructural**, no como "RAI" sin
    más. La validación fuerte en v0.9.0 corre contra **dos
    referencias** independientes: C-RAI sin pesos (Sheldon
    2017) y goal-directedness conductual sobre transcripts
    (literatura LLM 2025–2026). Pasar **cualquiera** de las
    dos con `r ≥ +0.5` promueve el proxy.
11. **Decisiones de diseño cerradas (locked v0.7.0).** Las
    cuatro preguntas que estaban abiertas se resolvieron por
    confirmación explícita del usuario:
    - **Pick final:** Candidato 1.
    - **Magnitud de perturbación:** single bit-flip por
      defecto; sweep de magnitudes ship en `v0.7.1` como ciclo
      de mantenimiento separado (mismo patrón que `v0.5.1` y
      `v0.6.1`).
    - **Extensión del protocolo:** `transition_fn` como
      `Optional`. Adapters que la expongan se miden; los que
      no, devuelven `None` (mismo patrón que
      `get_causal_graph()` en `v0.6.0a0`).
    - **Nomenclatura:** `rai_proxy_persistence` en código,
      *"structural autonomous-motivation proxy (Lee &
      McShea-style persistence)"* en prosa, `persistence` como
      etiqueta corta del eje. Se eligió "persistence" sobre
      "resistance" para alinear vocabulario con Lee & McShea
      (2020) y hacer trazable la cita desde el código mismo.

El espíritu del documento es el mismo de los anteriores:
**pre-registrar lo que se va a hacer**, declarar lo que cuenta
como falsación, y dejar trazable el porqué de cada decisión.
La diferencia es que esta vez el espacio de operacionalizaciones
posibles era mayor, y el proyecto eligió compararlas en
papel antes de comprometerse en código.
