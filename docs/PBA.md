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

The remaining ratios (`memory_endo_ratio` and the three planned
axes) will receive analogous diagnostics as they ship: each
metric's domain of applicability has to be stated before that
metric counts as evidence for or against PBA.

## Current evidence status

As of `v0.5.1a0`:

- Two of the five ratios are implemented (`ratio_endo_total`,
  `memory_endo_ratio`).
- Internal sanity tests show the two ratios behave as the
  literature predicts on canonical cases (constant series,
  i.i.d. noise, deterministic cycles, mixed self-rule plus
  environment-driven dynamics).
- A first cross-system mini-benchmark was run in `v0.5.0a0`
  (snapshot under `docs/benchmarks/v0.5.0a0.{csv,png,log.txt}`).
  On 48 valid points out of 69 configurations,
  `Pearson r(closure, memory) = +0.32` and
  `Spearman r(closure, memory) = +0.56`, both below the
  `|r| < 0.7` threshold this document uses as a falsification
  cue. The two axes therefore carry distinct information on the
  current adapter zoo.
- The `v0.5.1a0` saturation diagnostic confirms that the
  vertical wall at `closure = 1.0` observed in that benchmark is
  the closure-saturation theorem above, not a flaw of the metric:
  injecting Bernoulli bit-flip noise pulls closure off the wall
  monotonically.

PBA is therefore at the stage of *plausible working hypothesis
with one diagnostic-grade limitation explicitly mapped*, not
*empirical claim*. Documents and demos in the package phrase it
accordingly.

## Next decision points

- `v0.6.0a0` ships the third axis — RAI-style relative autonomy
  ratio (Deci & Ryan); first opportunity to check whether a
  ratio drawn from a different research tradition (psychology
  of motivation) co-discriminates with the two
  information-theoretic ratios on a shared system.
- `v0.7.0a0` and `v0.8.0a0` add CBA and the Montévil–Mossio
  constraint-closure ratio respectively; completing the five
  lets the prediction above be evaluated for the first time.
- A dedicated benchmarks track (provisionally `v0.9.0a0` in the
  README roadmap) is the formal home of the falsification
  test, building on the `v0.5.x` baseline.

If at any of these checkpoints the prediction starts failing,
this document is updated honestly: PBA's status is downgraded
and the package's marketing follows.
