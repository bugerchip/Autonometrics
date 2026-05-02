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

## Current evidence status

As of `v0.4.0a0`:

- Two of the five ratios are implemented (`ratio_endo_total`,
  `memory_endo_ratio`).
- Internal sanity tests show the two ratios behave as the
  literature predicts on canonical cases (constant series,
  i.i.d. noise, deterministic cycles, mixed self-rule plus
  environment-driven dynamics).
- No cross-system validation against an independently-curated
  benchmark has been run yet.

PBA is therefore at the stage of *plausible working hypothesis*,
not *empirical claim*. Documents and demos in the package phrase
it accordingly.

## Next decision points

- `v0.5.0a0` adds RAI; first opportunity to check whether a
  ratio drawn from a different research tradition (psychology of
  motivation) co-discriminates with the two information-theoretic
  ratios on a shared system.
- `v0.6.0a0` and `v0.7.0a0` add CBA and the Montévil–Mossio
  constraint-closure ratio respectively; completing the five lets
  the prediction above be evaluated for the first time.
- A dedicated benchmarks track (provisionally `v0.9.0a0` in the
  README roadmap) is the formal home of the falsification test.

If at any of these checkpoints the prediction starts failing,
this document is updated honestly: PBA's status is downgraded
and the package's marketing follows.
