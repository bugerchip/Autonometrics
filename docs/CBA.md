# CBA axis — design document

> *Status: design draft for the upcoming `v0.8.0a0` release.
> This document fixes the operational decisions before any code
> is written, so the implementation can be audited against an
> explicit specification rather than reverse-engineered from
> whatever the code happens to do. Same discipline applied to
> the `persistence` axis in [`docs/RAI.md`](RAI.md) and to the
> `constraint_closure` axis in
> [`docs/CONSTRAINT_CLOSURE.md`](CONSTRAINT_CLOSURE.md).*

> *Spanish summary at the bottom of this file.*

## What this axis adds to PBA

The four axes shipped so far live in four distinct mathematical
territories, all of them **synchronic or retrospective**:

- `ratio_endo_total` (Bertschinger / Albantakis) lives in
  **information-theoretic territory** at the level of the
  one-step transition `S_t → S_{t+1}`.
- `memory_endo_ratio` (Crutchfield) lives in
  **information-theoretic territory** at the level of long-run
  predictability of the trajectory.
- `constraint_closure` (Montévil & Mossio) lives in
  **graph-theoretic territory** at the level of cyclic
  dependencies among update rules.
- `rai_proxy_persistence` (Lee & McShea) lives in
  **dynamical-systems territory** at the level of how the system
  reabsorbs a perturbation.

The `v0.7.0a0` benchmark and the `v0.7.2a0` atlas-geometry
analysis together established that these four axes carry
distinct information on the current adapter zoo (pairwise
Pearson `|r| < 0.7`, no single principal direction exceeding
`λ₁ = 0.47`), and that each axis has its own documented domain
of applicability with explicit boundary regions where it
saturates by construction.

The fifth axis, **CBA** (Coherence-Based Alignment), enters from
a **fundamentally different scientific tradition** and probes a
**different temporal structure** than the previous four:

- **Different tradition.** CBA is rooted in the
  *intention–behaviour gap* literature in psychology (Festinger
  1957 on cognitive dissonance, Sheeran 2002's meta-analysis of
  intention–behaviour translation, Gollwitzer 1999 on
  implementation intentions), with deeper roots in the classical
  philosophical problem of *akrasia* (Aristotle, *Ethica
  Nicomachea* VII; Davidson 1970, *How is Weakness of the Will
  Possible?*) and in the philosophy of language (Searle 1975 on
  commissive speech acts; Anscombe 1957 on direction of fit).
  Recent AI-alignment work (Lanham et al. 2023 on CoT
  faithfulness; Turpin et al. 2023 on CoT unfaithfulness;
  PhilArchive 2024 on CBA as a unifying frame) operationalises
  the same fenomeno on language-model agents but does **not**
  invent it.
- **Different temporal structure.** Closure, memory, constraint
  and persistence all measure properties of a system **at one
  level**: the trajectory itself, the dependency graph, the
  unperturbed dynamics. CBA measures the **coupling between two
  levels**: a *declared* trajectory (what the system says it will
  do) and an *executed* trajectory (what the system actually
  does). It is the only PBA axis that explicitly requires the
  system to expose **two parallel layers** rather than one.

The reason this matters for PBA:

- The first four axes can in principle be measured on any
  substrate that produces a trajectory. CBA can only be measured
  on substrates that produce a **declarative layer** alongside
  the executive layer: agents with explicit plans, language
  models with chain-of-thought, humans reporting intentions,
  systems with predictive controllers, etc.
- This **narrowness is informative**, not a defect. It means CBA
  occupies a different stratum of the atlas: where the first
  four axes try to detect autonomy from structure alone, CBA
  asks whether the system's **own word about its future**
  predicts that future. Whether or not such a declarative layer
  is necessary for "full" autonomy is one of the open questions
  PBA was set up to make answerable.

The cross-tradition test the fifth axis offers therefore has
two parts:

1. **Structural**: does the info-theoretic operationalisation of
   CBA chosen in this document end up correlating moderately
   with the four existing axes (as PBA's atlas hypothesis would
   predict), or independently of them, or strongly redundantly
   with one of them?
2. **Geometric**: does adding a fifth axis collapse, preserve, or
   reorganise the current 4-D point-cloud geometry? In
   particular, does CBA reveal a *conditional* structure — for
   instance, do the first four axes co-vary differently in the
   regime of high CBA than in the regime of low CBA?

The first question reuses the falsification machinery already
established for axes 1–4. The second question is genuinely new
and is one of the reasons this cycle ships a **conditional
correlation analysis** alongside the standard pairwise
correlation table.

A nuance worth fixing up front: the cross-tradition test, even
in its strongest form, **does not by itself decide between
Level 2 and Level 3** of the unification taxonomy in
[`docs/PBA.md`](PBA.md). What the fifth axis can do is push the
prior between those two ontologies based on a fresh piece of
evidence. The strong behavioural validation (does our
structural CBA proxy correlate with intention–behaviour gap
measurements on real conversational or behavioural data?) is
deferred to `v0.9.0`, where the transcript adapter brings real
data into the package.

This document is therefore unusually conservative compared to
its predecessors: it does not commit to a single
operationalisation up front. It compares four structurally
distinct candidates, fixes explicit decision criteria, and
arrives at a provisional pick that the user reviews before any
code is written.

## Scientific background

### The intention–behaviour gap, distilled

The phenomenon CBA targets is older than any of its
formalisations. Stated as plainly as possible:

> *A system declares (predicts, plans, promises, intends,
> reasons aloud) that it will do X. The system then does Y. The
> question is the relation between X and Y.*

When `X = Y` consistently, the system is *coherent*: its word
predicts its act. When `X ≠ Y` systematically, the system is
*akratic* (in the philosophical sense), or *dissonant* (in the
psychological sense), or *unfaithful* (in the AI-alignment
sense), or *cheap-talking* (in the game-theoretic sense). The
vocabularies differ; the underlying gap is the same.

Crucially, the gap is **substrate-agnostic at the conceptual
level**. The same shape of question can be asked of:

- a person who says "I will exercise tomorrow" and then does or
  does not exercise (Sheeran, Webb 2016);
- a language model that produces a chain-of-thought arguing for
  answer A and then outputs answer B (Turpin 2023; Lanham 2023);
- a politician who publishes a manifesto and then governs
  (revealed-preference economics, Samuelson 1938);
- a planning agent in reinforcement learning that announces a
  policy and then executes a different one (DeepEval Plan
  Adherence, 2024–2025);
- a feedback controller whose model predicts a setpoint and
  whose actuator drifts away from it (control theory).

PBA's contribution is not to invent this question. PBA's
contribution is to **add it as a coordinate of the atlas** with
the same `[0, 1]` ratio convention used for the other four
axes, and to enforce the same independence-by-design and
falsification disciplines as the rest of the package.

### Conceptual lineage

The candidate operationalisations developed below all sit on a
recognisable lineage. The major waypoints, in chronological
order:

- **Aristotle (≈ 350 BCE), *Ethica Nicomachea* VII.** Defines
  *akrasia* as the situation in which an agent knows what is
  best, judges it correct, and yet acts against that judgement.
  This is the original formulation of the gap, framed as a
  problem of practical reasoning rather than measurement.
- **Anscombe (1957), *Intention*.** Introduces the concept of
  **direction of fit** distinguishing belief (word fits world)
  from intention (world is to fit word). Key for understanding
  why a declared trajectory is not just a prediction: it
  imposes a normative pull on the executed trajectory.
- **Festinger (1957), *A Theory of Cognitive Dissonance*.**
  Operationalises the gap psychologically as **dissonance**: a
  mismatch between cognitions (or between cognition and
  behaviour) creates psychological discomfort that drives the
  system toward consonance. Festinger's original formulation
  uses a **ratio of dissonant cognitions to total cognitions**
  — structurally identical in form to the ratio convention PBA
  adopts for every axis.
- **Davidson (1970), *How is Weakness of the Will Possible?*.**
  Reformulates akrasia analytically and identifies the
  *principle of continence*: a rational agent should act on
  their best all-things-considered judgement. Davidson does not
  resolve the paradox; he sharpens it.
- **Searle (1975, 1979), classification of illocutionary acts.**
  Identifies **commissives** as a class of speech acts in which
  the direction of fit is *world-to-word*: a promise creates an
  obligation for the world (the speaker's future actions) to
  conform to the words spoken. Mathematically, a commissive is
  the speech-act analogue of what CBA tries to score.
- **Bratman (1987), *Intention, Plans, and Practical Reason*.**
  Treats plans as *partial commitments* that filter future
  deliberation: once a plan is in place, options inconsistent
  with it are excluded by default. This connects intention to
  *constraint*, and explains why high CBA is correlated, in
  rich agents, with reduced cognitive load: the plan is doing
  some of the work.
- **Gollwitzer (1999), implementation intentions.** Shows
  empirically that the *form* of a declaration matters: "if X,
  then I will do Y" closures the intention–behaviour gap more
  than vague declarations of intent. Effect size in the
  Gollwitzer & Sheeran (2006) meta-analysis: `d = 0.65` across
  94 studies.
- **Sheeran (2002), intention–behaviour gap.** Meta-analysis of
  **422 prospective studies, n = 82,107**. Finds that intentions
  account for **≈ 28% of the variance** in behaviour and that
  experimental shifts in intention (`d = 0.66`) translate into
  shifts in behaviour of only `d = 0.36`. The gap is large,
  robust, and reproducible across health domains, environmental
  behaviour, and consumer choice.
- **Sheeran & Webb (2016)** consolidates the field into a single
  review.
- **Lanham et al. (2023), Anthropic CoT faithfulness.**
  Operationalises the same gap on language models: how much of
  the chain-of-thought is causally responsible for the final
  answer? Finds substantial **post-hoc rationalisation** in
  large models — they sometimes produce coherent reasoning that
  is *not* what determined their output.
- **Turpin et al. (2023), CoT unfaithfulness.** Shows that
  biased prompts can shift LLM answers without altering the
  expressed reasoning, demonstrating that the declared layer
  can dissociate from the executive layer in modern AI systems
  too.
- **PhilArchive (2024), Coherence-Based Alignment.** Introduces
  the term *CBA* for an integrative framework bundling
  epistemic coherence (beliefs vs observations), action
  coherence (best-policy vs executed-action) and value
  coherence (declared values vs long-run trajectory). The
  framework is conceptual and does not commit to a single
  formula; this document operationalises one slice of it (action
  coherence) for substrate-agnostic measurement.
- **DeepEval, Snowflake Agent GPA, FAITHCOT-BENCH, IDS, GTA,
  IntentScore (2023–2025).** Implementations and benchmarks of
  the same gap on agent traces, mostly using LLM-as-judge.
  Useful as references and complementary tools; not used as
  dependencies because they break the package's offline
  reproducibility constraint.

The takeaway: the question CBA asks has been continuously
refined by at least eleven distinct research traditions over
more than two millennia. Adding it to the atlas is **not
inventing a phenomenon**; it is **proposing one more
operationalisation, with explicit lineage, of a long-standing
question**.

### Why CBA fits PBA on its face

CBA, in any of its concrete operationalisations, is naturally a
**ratio of internal magnitude over total magnitude**:

- For Festinger, the ratio is `dissonant / (dissonant +
  consonant)`, or equivalently consonance = `consonant / total`.
- For Sheeran-style intention–behaviour analysis, the ratio is
  the share of the variance in behaviour attributable to
  intention.
- For Gollwitzer-style implementation intentions, the ratio is
  the share of intentions that cross into action.
- For information-theoretic coherence, the ratio is
  `I(D; E) / H(D)`, the share of declared-side uncertainty that
  is resolved by knowledge of the executed side.

The shape matches the PBA convention exactly. As with RAI in
`docs/RAI.md`, the challenge is not the shape; it is that CBA
was designed to be measured by behavioural studies on humans
and by LLM-as-judge classifiers on agent traces, and the
package's adapter zoo contains zero entities of either kind by
default. The remaining sections of this document address the
operationalisation problem.

## The translation problem

For CBA to enter the atlas, the package needs an
**operationalisation that:**

1. Produces a `[0, 1]` score from data the existing or planned
   adapters can expose, **without requiring an external LLM
   judge**, an API call, or a non-deterministic classifier.
2. Captures the **spirit** of the intention–execution gap as
   formalised across the lineage above: how much of the
   executed trajectory is predicted, constrained, or
   determined by the declared trajectory.
3. Is **structurally distinct** from the four existing axes, so
   that any cross-axis correlation observed on the
   five-axis benchmark is informative rather than engineered.
4. Treats systems **without a declarative layer** honestly: the
   metric should return `None` (drop out) rather than fabricate
   a score from a synthetic proxy that pretends every system
   has an intention.

Constraint (1) is non-trivial. It rules out the most popular
modern operationalisations of CBA in AI alignment, which all
rely on an external LLM evaluator (DeepEval Plan Adherence,
Snowflake Agent GPA, IntentScore, etc.). Those tools are
genuinely useful, and `docs/CBA.md` cites them as sister
implementations, but they are not viable as the **structural,
substrate-agnostic, offline** version of CBA that the package
is built around.

Constraint (4) is what makes the fifth axis *narrower* than the
first four. Cellular automata have no plans. Boolean networks
have no plans. Periodic cycles do not announce their period
before iterating. The honest move is to record those
configurations as `n/a` for the CBA axis and to design at least
one synthetic adapter (`PromisedCycle`, introduced below) that
*does* have a declarative layer, so the metric is not measured
purely on data the user is responsible for supplying.

The four-step shape above mirrors the structure of RAI's
translation problem, and the same three-path response applies:
information-theoretic redirection (Path I, rejected),
behavioural transcript adapter (Path II, deferred to v0.9.0),
or a structural signature defined directly on the existing
APIs (Path III, the path this document develops).

## Adjacent literatures and prior work

The translation problem is not new. Five lines of work have
each addressed neighbouring versions of it. Acknowledging them
up front avoids two failure modes: claiming as new what already
exists, and mistaking adaptation for invention. The same
discipline applied to RAI's lineage in `docs/RAI.md` is applied
here.

### Festinger (1957) — dissonance ratios as a measurement primitive

Festinger's *A Theory of Cognitive Dissonance* is the earliest
explicit **quantitative** treatment of the intention–behaviour
gap, even though it predates information theory's adoption in
psychology and uses informal counts of cognitions rather than
estimates of mutual information. Festinger's central
formalisation is:

```
dissonance = D / (D + C)
```

where `D` is the count of cognitions (or behaviours) dissonant
with a focal cognition and `C` is the count of consonant ones.
The complement, *consonance*, is `C / (D + C) ∈ [0, 1]` and
plays the same role a CBA score would play in the PBA atlas: a
number in `[0, 1]` reporting how much of the system's content
agrees with a focal commitment.

Two things in this lineage matter for the present design:

1. The **ratio shape** of the formalisation, in `[0, 1]`, with a
   numerator counting "internal" agreement and a denominator
   counting the total. PBA's atlas convention literally inherits
   this shape.
2. The recognition that **the gap is measurable from observable
   contents**, not only from introspection. Festinger's
   experimental tradition (Festinger & Carlsmith 1959; Aronson
   1969 onwards) routinely operationalises dissonance from
   behavioural data alone.

Where Festinger does **not** suffice: his framework is
domain-specific (cognition counts) and pre-information-theoretic.
The candidate operationalisations below generalise Festinger's
ratio to discrete trajectories using either match counts (C1,
C4) or mutual information (C2), so that the same machinery
applies to systems that do not produce "cognitions" in
Festinger's original sense.

### Sheeran (2002) and Sheeran & Webb (2016) — the empirical baseline

Sheeran's meta-analysis of **422 prospective studies (n =
82,107)** establishes the empirical magnitude of the
intention–behaviour gap in humans:

- Intentions explain `≈ 28%` of the variance in behaviour.
- Experimental shifts in intention of `d = 0.66` translate into
  behavioural shifts of `d = 0.36`.
- The gap is robust across health domains, environmental
  behaviour, and consumer choice.

The 2016 review with Webb consolidates these findings.

This matters for PBA in two ways:

1. **Reference distribution.** Any CBA score the package
   reports on a behaviourally meaningful adapter (e.g. the
   future transcript adapter) can be compared, in coarse terms,
   against Sheeran's empirical baseline. A CBA score
   substantially below Sheeran's `≈ 28%`-of-variance figure on
   a real-world domain would be diagnostic of either a
   particularly akratic system or a poorly-aligned
   operationalisation; either is informative.
2. **Validation target.** The v0.9.0 transcript adapter will be
   able to compare structural CBA proxies against
   Sheeran-tradition behavioural measurements directly,
   provided the dataset includes paired declared-intention and
   measured-behaviour entries. This is not a v0.8.0
   commitment, but it justifies investing in the structural
   proxy now.

### Gollwitzer (1999, 2006) — the form of the declaration matters

Gollwitzer's **implementation intentions** literature shows that
*how* a declaration is phrased changes whether it crosses to
action. The signature finding (Gollwitzer & Sheeran 2006
meta-analysis of 94 studies): "if X then I will do Y"
formulations close the gap with effect size `d = 0.65`,
substantially better than vague intentions of the form "I will
do Y".

The package does not currently distinguish between forms of
declaration, but the distinction is important for the v0.9.x
roadmap: a **stratified CBA**, conditional on declaration form,
is a natural extension once enough real-world declarative data
is present. This document records the lineage but defers the
extension.

### PhilArchive (2024) — the CBA frame as such

The PhilArchive 2024 paper is the contemporary work that
explicitly proposes the term *Coherence-Based Alignment* and
defines a triple decomposition:

- **Epistemic coherence** — alignment between the system's
  beliefs (model of the world) and observed evidence.
- **Action coherence** — alignment between the system's chosen
  policy / action and the policy / action it would best
  endorse.
- **Value coherence** — alignment between the system's
  long-run trajectory and its declared values.

The paper defines `C ∈ [0, 1]` as the unifying score and gives
desiderata but **does not commit to a single computational
formula**. PBA's structural CBA proxy operationalises the
**action-coherence** component using mutual-information ratios
on observed declared-vs-executed trajectories, leaving the
epistemic and value components for future cycles or for sister
LLM-judge implementations.

This document **cites PhilArchive 2024 as the framing source**
for the name and the conceptual triple, while being explicit
that the present formula is a generalisation across substrates,
not a re-implementation of any specific PhilArchive computation
(which the paper does not provide).

### CoT-faithfulness lineage and current LLM-judge tools (2022–2025)

The most active modern strand on coherence-style measurement
runs through the chain-of-thought (CoT) faithfulness work:

- **Wang et al. (2022)**, self-consistency: same problem
  resampled multiple ways, agreement is a faithfulness signal.
  Effect size `+18%` accuracy on GSM8K when used as a decoding
  strategy.
- **Turpin et al. (2023)**, *"Language Models Don't Always Say
  What They Think"*: documents systematic CoT unfaithfulness in
  GPT-3.5 and Claude 1.3, with biased prompts shifting answers
  without altering reasoning.
- **Lanham et al. (2023)**, Anthropic, CoT faithfulness:
  intervention-based methodology to detect post-hoc
  rationalisation in larger models.
- **DeepEval Plan Adherence**: open-source `pip install`-able
  metric that scores agent plans against execution traces using
  GPT-4 / Claude as judge.
- **Snowflake Agent GPA (Goal-Plan-Action)**: five-axis
  framework for agent evaluation; "Plan adherence" is
  structurally what CBA measures.
- **IntentScore (2024)**, **GTA / Reasoning-Execution Gaps
  (2024)**, **ValueActionLens (2025)**, **IDS (2024)**:
  variations on the same theme on different axes
  (intent-as-reward, separate reasoning-from-execution gaps,
  cross-cultural value-action gap, intent-drift score).
- **FAITHCOT-BENCH** (Sze et al., 2024): 1,000+ annotated
  trajectories across 4 LLMs and 4 domains; **a ready dataset**
  for the v0.9.0 validation phase, distributed under an
  acceptable open licence.

These tools share two properties that the PBA structural CBA
proxy deliberately gives up:

- They use an LLM as judge, which (a) requires API access at
  inference time, (b) costs money per measurement, (c) is not
  fully reproducible across model versions.
- They target action-coherence at the *semantic* level (does
  the plan as written predict the action as written?), which
  requires natural-language understanding.

PBA's structural CBA proxy targets action-coherence at the
**syntactic / token level** instead: given two parallel
discrete trajectories `D` and `E`, both encoded in the package's
integer-state convention, how much of `E` is predictable from
`D`? This is a strictly weaker question than the semantic one,
but it has three compensating advantages: it is offline, it is
deterministic, and it is comparable across substrates that have
nothing else in common (e.g. an LLM transcript and a planning
controller).

### Behavioural measurement in RL, world-models, and game theory

For completeness, three further sub-traditions inform but do not
drive the present design:

- **Behavioral Consistency Reward (BehR)** in reinforcement
  learning: rewards an agent for keeping its actions
  predictable from its previously stated policy. Same
  declarative-vs-executed structure, applied at training time
  rather than evaluation time.
- **Cheap talk vs costly signaling** in game theory (Crawford &
  Sobel 1982; Spence 1973, Nobel 2001): *the informational
  value of a declaration depends on its cost*. CBA scores from
  zero-cost declarations are systematically less informative
  than CBA scores from costly declarations. The present design
  does not weight by cost, but the v0.9.x roadmap has a slot
  for it.
- **Stated vs revealed preference** in economics (Samuelson
  1938 onwards): an entire methodology built around the gap
  between what people say they prefer and what their choices
  reveal. Annual Review of Resource Economics 2019 surveys the
  modern state.

### What stays unique to PBA

Three things are not covered by the adjacent literatures and
remain genuine PBA contributions:

1. **Substrate-agnostic info-theoretic operationalisation.**
   Festinger's ratio is for cognitions, Sheeran's variance
   decomposition is for human behaviour, PhilArchive defines a
   conceptual triple, and DeepEval/Snowflake/etc. use
   LLM-as-judge. None of those gives a single offline formula
   that works on cellular automata, ECAs, Kauffman networks,
   structured cycles, transcript adapters, and CSV-supplied
   trajectories interchangeably. That uniformity is the package
   contribution.
2. **Integration into a multi-axis atlas.** The CBA literature
   is not organised as part of a multi-dimensional autonomy
   profile; PBA's atlas places CBA next to closure, memory,
   constraint and persistence with explicit cross-axis
   independence audits.
3. **Conditional-correlation analysis.** The hypothesis that
   CBA acts as a *gating axis* for the others — that the four
   structural axes only stabilise into informative measurements
   on systems whose declarative-executive coupling is
   non-trivial — is original to this document and is what makes
   the v0.8.0a0 cycle worth running even if the headline atlas
   geometry stays as it was after v0.7.2a0.

## Approaches not pursued in v0.8.0

### Path I — Synthetic declarative proxy on existing zoo

One way to keep CBA measurable on the existing four-adapter zoo
(ECA, Kauffman, PeriodicCycle, SimpleAutomaton) would be to
**synthesise** a declarative layer for each: e.g. for ECA, take
the rule's local prediction at time `t` and call it the
declaration; the global state at `t + 1` is then the execution.
The CBA score becomes the consistency between local-rule
predictions and emergent global outcomes.

This is rejected for v0.8.0 for two reasons:

1. **It collapses the new axis into a re-reading of `closure`.**
   The local-rule prediction *is* what `closure` already
   measures (information from the system's previous state about
   its next state). A CBA built on top of that proxy would
   correlate with `closure` by construction, fail the
   independence-by-design audit, and provide no genuinely new
   coordinate for the atlas.
2. **It breaks the "declarative layer" promise.** A synthetic
   declarative layer is not what the lineage means by
   declaration. Festinger, Sheeran, Gollwitzer and PhilArchive
   all assume an *agent that issues* a declaration distinct
   from its execution. Forcing a declaration onto a system that
   has none would launder the metric: the score would look like
   a CBA score and would not behave like one.

The package therefore does not pursue this path. The honest
move is **dropout**: ECA, Kauffman, PeriodicCycle and
SimpleAutomaton return `None` for the CBA axis. The benchmark
records `n_valid` for the CBA column accordingly, just as it
already does for `constraint_closure` on adapters that do not
expose `get_causal_graph`.

### Path II — LLM-as-judge

The most direct translation of contemporary AI-alignment CBA
work would be to use a language model to score
declared-vs-executed alignment on transcript-style inputs. This
is exactly what DeepEval Plan Adherence and Snowflake Agent GPA
do.

This is rejected as the primary v0.8.0 operationalisation for
three reasons:

1. **It violates the offline-and-deterministic contract.** The
   four shipped axes all run on `numpy` alone; introducing an
   LLM dependency for the fifth axis breaks symmetry and makes
   `pip install autonometrics` non-self-contained.
2. **It is not reproducible across model versions.** A CBA
   score produced by GPT-4-2024-08 differs from one produced
   by GPT-4-2025-03; benchmarks would silently drift with model
   updates, contradicting the package's reproducibility
   commitments.
3. **It costs money per measurement.** Benchmarks would become
   pay-to-run, pricing out any user without API budget.

Path II is therefore deferred to a possible **optional extra**
in a future release: `pip install "autonometrics[llm-judge]"`
might one day expose a wrapper around an LLM-judge backend,
clearly marked as non-default and as not subject to the
reproducibility commitments of the core. v0.8.0 makes no such
addition.

### Path III — A structural info-theoretic signature on parallel trajectories

The remaining option, and the one this document develops, is to
**define a structural signature** that:

- Runs on any system that exposes two parallel discrete
  trajectories `D` (declared) and `E` (executed) with the same
  length and a comparable alphabet.
- Captures the intention–execution gap in the sense formalised
  by Festinger, Sheeran, Bratman and PhilArchive: how much of
  the executed trajectory is determined by the declared one.
- Is mathematically independent of the four existing axes by
  design and verifiable by static import audit.

The word *invent* would be overstated here. The candidate
operationalisations below all exist as standard
information-theoretic or distance-based measurements; the
contribution is the **synthesis** that brings one of them into
PBA under the same `[0, 1]` ratio convention used for the other
axes, and the **decision discipline** that picks one over the
others on stated criteria.

The next section compares four structurally distinct candidates
within Path III.

## Candidate structural signatures

All four candidates assume the same minimal interface from the
adapter:

```python
class AutonomySystem(Protocol):
    ...
    def get_declared_executed(self) -> tuple[np.ndarray, np.ndarray] | None:
        """Return parallel (declared, executed) discrete trajectories.

        Both arrays must have shape (T,) over the same integer
        alphabet. Returning None signals 'no declarative layer'
        and the CBA axis returns None for this system.
        """
```

The intent is to keep the protocol extension as small as
possible (one method, optional, returning a tuple of arrays of
identical shape). The five-axis benchmark then drops adapters
that return `None` from the CBA column and reports `n_valid`
honestly, identically to how it currently handles
`constraint_closure` dropout.

The four candidates below differ only in **how the score is
computed** from the same `(D, E)` pair.

### C1 — Match rate (Festinger-style, simplest)

The most direct translation of Festinger's consonance ratio:

```
cba_match = (1 / T) * Σ_t  𝟙[D_t == E_t]
```

i.e. the fraction of timesteps at which declaration and
execution coincide.

- **Strengths.** Zero free parameters, transparent, trivially
  reproducible, identical in spirit to Festinger's original
  ratio.
- **Weaknesses.** Confounded by alphabet sparsity: if the
  alphabet is very large and the system happens to repeat any
  symbol frequently, baseline match rate is non-zero. Cannot
  detect *systematic* substitutions (e.g. "the system always
  declares A and always does B" yields `cba_match = 0` even
  though the declaration is in some sense informative — but
  inversely so).

### C2 — Theil's U (asymmetric MI ratio, info-theoretic)

The information-theoretic operationalisation closest in spirit
to PhilArchive 2024 and to the closure-axis convention:

```
cba_theil = I(D; E) / H(D)
```

where `H(D)` is Shannon entropy of the declared distribution
and `I(D; E) = H(D) - H(D | E)` is mutual information.

- **Strengths.** Bounded in `[0, 1]` by construction, asymmetric
  (the coefficient `H(D)` matches the **declared-side**
  uncertainty being resolved), invariant under any
  permutation of the alphabet, robust to baseline match rate,
  detects systematic substitutions correctly. Same shape as the
  closure axis (`I(S_t; S_{t+1}) / H(S_{t+1})`-style ratios),
  enabling apples-to-apples comparison.
- **Weaknesses.** Returns `1.0` for any deterministic
  `E = f(D)` even when `f` is the constant or a non-identity
  bijection. This is in fact the standard Theil's U semantics
  — *predictability of E from D* — and is a feature for CBA
  (a system whose declaration deterministically predicts its
  execution is maximally coherent in the relevant sense), but
  must be documented carefully so it is not confused with
  **identity** (which would require `D == E` pointwise).
- **Estimator caveat.** Plug-in entropy estimators are biased
  upward at finite `T`; the implementation will use the
  Miller-Madow correction (already used by `closure` and
  `memory` axes) and will surface a low-N warning for `T <
  T_min` where `T_min` is set per-experiment but defaults to
  `100`.

### C3 — Normalised distance (transcript-friendly)

For substrates where `D` and `E` are sequence-valued and the
natural notion of agreement is *edit distance* rather than
pointwise equality:

```
cba_dist = 1 - (Levenshtein(D, E) / max(|D|, |E|))
```

- **Strengths.** Native to transcript-style data; insensitive
  to small reorderings; widely used in NLP and bioinformatics.
- **Weaknesses.** Heavy dependency (a Levenshtein implementation
  in core), confounded by sequence length, not directly
  comparable across alphabets of very different sizes. The
  package would need to add a Levenshtein implementation or
  pull a dependency for a metric only one adapter (the future
  transcript adapter) actually needs.

### C4 — Festinger-style ratio with explicit consonant / dissonant counts

The most literal translation of Festinger 1957 to a
trajectory:

```
consonant   = #{t : D_t == E_t}
dissonant   = #{t : D_t != E_t}
cba_festinger = consonant / (consonant + dissonant)
```

This collapses to C1 mathematically (since `consonant +
dissonant = T`), but is included explicitly so the document can
record the historical lineage and explain why C1 and C4 are
*the same number under different names*. Naming matters in PBA:
calling the metric `cba_festinger_ratio` or `cba_match_rate`
shapes how readers situate it in the literature.

### Comparison table

| Aspect | C1 (match) | C2 (Theil's U) | C3 (distance) | C4 (Festinger) |
|---|---|---|---|---|
| Range | `[0, 1]` | `[0, 1]` | `[0, 1]` | `[0, 1]` |
| Lineage | Festinger 1957 | Theil 1970, PhilArchive 2024 | NLP, bioinformatics | Festinger 1957 |
| Shape match with PBA atlas | partial (count ratio) | full (info-theoretic ratio) | partial (distance ratio) | partial (count ratio) |
| Dependencies | numpy only | numpy only | adds Levenshtein | numpy only |
| Detects systematic substitution | no | yes | partial | no |
| Detects simple drift | yes | yes | yes | yes |
| Sensitive to alphabet size | yes | no | yes | yes |
| Estimator bias at low N | none | yes (Miller-Madow fixable) | none | none |
| Comparable across substrates | partial | yes | poor | partial |
| Independence-by-design from `closure` | yes | yes (different decomposition) | yes | yes |
| Independence-by-design from `memory` | yes | yes | yes | yes |
| Naming clarity | high | medium-high | high | medium |

The table makes the decision criteria visible at a glance.

## Decision criteria

A candidate is selected by the conjunction of:

- **Atlas shape match.** The numerator must be an internal /
  declarative magnitude; the denominator must be a total or
  declarative-side magnitude. The score must lie in `[0, 1]`
  with the same orientation as the other axes (higher = more
  coherent / more autonomous in the CBA sense).
- **Substrate-agnosticism.** The metric must be definable on any
  pair of discrete-state trajectories of the same length over
  any finite alphabet, without bespoke hyperparameters per
  substrate.
- **Independence-by-design from the other four axes.** The
  formula must use no quantity that closure / memory /
  constraint / persistence already use, in the same way they
  use it. Verifiable by static import audit and confirmed
  empirically by `|r| < 0.7` on the five-axis benchmark.
- **Sensitivity to systematic mismatch.** A system that always
  declares `A` and always executes `B` should score *very low*
  on CBA (modulo the careful caveat that Theil's U treats
  bijections specially — see below). A system whose execution
  is statistically independent of its declaration should score
  near zero. A system whose declaration deterministically
  predicts its execution should score `1.0`.
- **Reproducibility.** No external services, no
  non-deterministic estimators. Single-seed, single-machine
  reproducibility down to floating-point identity, modulo
  documented numerical tolerances.
- **Estimator behaviour at low N.** The implementation must
  either be exact at all `T` (C1, C3, C4) or come with an
  explicit bias correction and a low-N warning (C2).
- **Lineage transparency.** The formula must be traceable to a
  cited source; PBA's structural variant must be documented as
  an adaptation, not as the original.

C1 and C4 are mathematically identical and satisfy most
criteria except *sensitivity to systematic mismatch* (they
score zero for any non-identity deterministic mapping, which
collapses informative substitutions and uninformative drifts
into the same number). C3 satisfies the criteria but at the
cost of a dependency that is justified only on transcript-style
data, which v0.8.0 does not yet ship. C2 satisfies all criteria
with the documented Theil's-U-on-bijection caveat and is the
information-theoretic operationalisation that fits the closest
into the existing atlas geometry.

## Provisional pick — Theil's U with C1 as a sanity-check companion

The v0.8.0a0 axis ships **C2 — Theil's U**, computed as

```
cba_theil = I(D; E) / H(D)
```

with the Miller-Madow bias correction and a low-N warning at
`T < 100`.

Two clarifications make the choice non-arbitrary and avoid
common misreadings:

1. **Why not C1 alone?** C1 is intuitively appealing and
   trivial to compute, but it confounds the case "the
   declaration is informative but expressed in a different
   alphabet from the execution" (e.g. the declaration is the
   action class and the execution is the concrete action) with
   the case "the declaration is uninformative". C2 separates
   them.
2. **Why not C2 alone?** Reporting only Theil's U risks
   silently scoring a non-identity bijection as `1.0`. The
   v0.8.0a0 implementation therefore **also computes C1
   internally** and surfaces it as a diagnostic
   (`cba_diagnostics["match_rate"]`) in the
   `AutonomyProfile.diagnostics` dictionary. This is parallel
   to how `persistence` already exposes `d_bar` and `d_ref` as
   diagnostics for interpretive purposes.

The headline number that enters the autonomy profile, the
benchmark CSV and the atlas geometry analysis is
`cba_theil_u`. The diagnostic match rate is reported alongside
but never replaces it.

This pick is **provisional** in the strict sense used in
[`docs/RAI.md`](RAI.md): the candidate may be revised before
v0.8.0a0 ships if the user objects to any of the trade-offs
this document makes explicit. After v0.8.0a0 ships, the choice
is locked unless the v0.7.2a0-style geometry rerun (now
five-axis) produces evidence that one of C1, C3 or C4 fits the
atlas better. Any such revision would itself be pre-registered
in a follow-up section of this document, in the same way the
RAI design recorded its updates after Lee-McShea differential
analysis.

## Per-adapter predictions

The `v0.8.0a0` implementation extends `tests/benchmarks` with a
five-axis sweep across the existing four adapter families plus
one new family introduced for CBA. The expected behaviour, in
qualitative terms, is documented here so the benchmark is not
asked open-endedly "what does CBA look like?"; it is asked the
falsifiable question "does CBA conform to the predictions
below, on which adapters, and where does it fail?"

Predictions are stated in coarse bands (`high ≥ 0.8`,
`mid ∈ [0.4, 0.8)`, `low < 0.4`, `n/a` if `get_declared_executed`
returns `None`) so they are testable without overcommitting
to numerical thresholds the v0.7.2a0 geometry analysis showed
are noisy at `n = 10`.

### `PromisedCycle` — the canonical CBA-positive adapter

A new adapter introduced in `v0.8.0a0`. Internally it is a
periodic cycle of length `k` over an alphabet of size `m`, but
it exposes **two trajectories**:

- **Declared.** The cycle's *announced* schedule for the next
  `T` steps, generated at construction time.
- **Executed.** The cycle's actual states, with optional
  **noise probability** `p_noise` per step that flips the
  current state to a random alternative.

Predictions:

- `p_noise = 0.0` → `cba_theil ≈ 1.0`. Declared schedule
  perfectly predicts execution. **Sanity check**: this is the
  "zero akrasia" boundary case and the metric must hit the
  upper boundary on it. If it does not, the implementation is
  buggy.
- `p_noise = 0.1` → `cba_theil` in the high band, slightly
  below `1.0`. Most of the executed entropy is still resolved
  by the declared schedule.
- `p_noise = 0.5` → `cba_theil` in the mid band. Half the
  execution is independent of the declaration.
- `p_noise = 1.0` → `cba_theil ≈ 0.0`. **Sanity check**: this
  is the "maximal akrasia" boundary case and the metric must
  hit the lower boundary on it.

The two boundary predictions (`p_noise = 0.0` and `p_noise =
1.0`) are pre-registered as **hard sanity checks** for v0.8.0a0:
the release is gated on both holding.

### `PromisedCycle` with adversarial noise

A second variant of `PromisedCycle` swaps random noise for
**systematic substitution**: every declared symbol `s` is
executed as `(s + 1) mod m`. This is the case Theil's U handles
correctly and C1 / C4 do not.

Prediction:

- C2 (`cba_theil`) ≈ `1.0` (deterministic bijection: declared
  side perfectly predicts executed side, even though the
  symbols never match).
- C1 / C4 (`cba_match`) ≈ `0.0` (no pointwise matches).

The benchmark records both numbers and the doc explicitly
documents the divergence as the **textbook illustrative case**
for why the headline number is C2 rather than C1.

### `ECA`, `Kauffman`, `PeriodicCycle`, `SimpleAutomaton`

None of these adapters expose `get_declared_executed`. The
expected outcome is `cba_theil = None` and the benchmark CSV
records dropout for the CBA column on every system in these
families.

This is the expected and *correct* behaviour. CBA is the
narrowest axis in the atlas precisely because not every
substrate has a declarative layer; the package's job is to
report that honestly rather than fabricate a score.

### Future: `TranscriptAdapter`

Deferred to v0.9.0. The transcript adapter ingests CSV files
with `(timestamp, declared_intent, executed_action)` rows, maps
them to the integer-alphabet convention, and exposes
`get_declared_executed`. Predictions for this adapter cannot be
pre-registered before v0.9.0 because they depend on the
specific datasets ingested.

## Falsification thresholds

In the same spirit as `docs/RAI.md` and
`docs/ATLAS_GEOMETRY.md`, the v0.8.0a0 benchmark is **gated on
explicit numerical thresholds set before the metric runs.**
Two layers of thresholds apply: per-adapter sanity checks and
cross-axis independence checks.

### Sanity-check thresholds (per-adapter, hard gates)

- `PromisedCycle(p_noise=0.0)` → `cba_theil ≥ 0.95`.
- `PromisedCycle(p_noise=1.0)` → `cba_theil ≤ 0.10`.
- `PromisedCycle(adversarial substitution)` → `cba_theil ≥ 0.90`
  **and** `cba_match ≤ 0.10`.

If any of these fails on the release benchmark, **the release
does not ship** and the implementation is investigated.

### Independence-by-design thresholds (cross-axis, soft gates)

For the five-axis benchmark across all valid systems
(`n ≥ 30` excluding CBA dropouts):

- Pairwise Pearson `|r| < 0.7` between `cba_theil` and each of
  `closure`, `memory`, `constraint_closure`,
  `rai_proxy_persistence`. **Hard gate**: a release with any
  pair `|r| ≥ 0.9` is blocked, on the grounds that such a pair
  is functionally redundant. **Soft gate**: a release with any
  pair in `[0.7, 0.9)` ships with a mandatory note in the
  changelog flagging the partial overlap and naming the pair.
- Static import audit: `metrics/coherence.py` must not import
  any function or class from `metrics/closure.py`,
  `metrics/memory.py`, `metrics/constraint_closure.py` or
  `metrics/persistence.py`. Verified by an automated test that
  fails CI on violation. Same machinery used since v0.6.1.
- 4-axis-vs-5-axis geometry comparison: rerun
  `docs/ATLAS_GEOMETRY.md`'s PCA and clustering on the
  five-axis cloud restricted to systems where CBA is defined
  (i.e. `PromisedCycle` family for v0.8.0). The release is
  **not** gated on the geometry result, but the result is
  reported in the v0.8.0a0 changelog as new evidence on the
  Level-2 vs Level-3 unification question.

### Conditional-correlation analysis (new in v0.8.0a0)

Even if all pairwise correlations stay below `0.7`, the
v0.8.0a0 cycle adds a **conditional correlation** report: split
the (transcript-style or PromisedCycle) sample into
`high CBA` (`cba_theil ≥ 0.7`) and `low CBA` (`cba_theil <
0.3`) and compute the four pairwise correlations of the other
axes within each subset. If the conditional correlations differ
substantially between the two subsets, this is recorded as
**Level-3-suggestive evidence**: the four axes might be co-
varying differently in different *coherence regimes*, hinting
at substrate-dependent geometry. The Simpson's-paradox flag
documented in `docs/ATLAS_GEOMETRY.md` would apply here too.

This analysis is **not gated**: it produces a report, not a
release decision. It exists so the geometry conversation
keeps moving forward in v0.8.0a0 rather than being deferred to
v0.9.0.

## Independence-by-design guarantees

Independence-by-design is the same discipline used for
`persistence` in [`docs/RAI.md`](RAI.md). Restated for CBA:

- **Code-level independence.** `metrics/coherence.py` (the
  module that ships C2 and the C1 diagnostic) imports only
  `numpy` and standard library. It does not import from any of
  `metrics/closure.py`, `metrics/memory.py`,
  `metrics/constraint_closure.py`, `metrics/persistence.py`. A
  CI test enforces this constraint statically.
- **Quantity-level independence.** The coherence module computes
  Shannon entropy on the **declared** trajectory `D` and mutual
  information between `D` and the **executed** trajectory `E`.
  Neither quantity is the same as the closure axis's
  `I(S_t; S_{t+1}) / H(S_{t+1})` (which compares the system to
  itself across time, not declaration to execution), nor as
  the memory axis's excess entropy (which integrates over many
  past steps), nor as constraint_closure (which is structural
  on a graph), nor as persistence (which depends on
  perturbation experiments). The four axes therefore use
  numerator and denominator data the CBA axis does not, and
  vice versa.
- **Empirical independence.** Pairwise `|r| < 0.7` on the
  five-axis benchmark across all valid systems is a **soft
  gate**; `|r| < 0.9` is a **hard gate**. Same thresholds used
  for the four-axis benchmark in v0.7.0a0 onwards, applied
  consistently.
- **Geometric independence.** The `v0.7.2a0`-style PCA report,
  rerun on the five-axis cloud, must not collapse the new axis
  onto an existing principal direction (`λ_max < 0.65` is the
  pre-registered threshold from `docs/ATLAS_GEOMETRY.md`,
  carried over).

If any of the independence guarantees fails, the release does
**not** ship. Specifically:

- Static import violation → CI fails, blocked.
- `|r| ≥ 0.9` between CBA and any of the four other axes →
  release blocked, axis revisited.
- `|r| ∈ [0.7, 0.9)` → release ships with a changelog note
  flagging the partial overlap and explaining it.
- PCA `λ_max ≥ 0.65` → release ships, but the
  `docs/ATLAS_GEOMETRY.md` document is updated with the new
  result and the PBA hypothesis status is reviewed accordingly
  in `docs/PBA.md`.

## Provisional status and validation plan

The structural CBA proxy proposed here is, like the persistence
axis, **provisional in the strict sense**: it captures one
information-theoretic operationalisation of the
intention–execution gap, with explicit lineage and explicit
limits. It does not yet have direct empirical validation
against the behavioural intention–behaviour gap measurements
the lineage was originally built around.

The validation plan splits across three milestones:

### v0.8.0a0 — internal validation

- Sanity checks on `PromisedCycle` (boundary cases at
  `p_noise = 0.0` and `p_noise = 1.0`).
- Adversarial-substitution test that pulls C1 and C2 apart, as
  pre-registered above.
- Independence-by-design audits (static + empirical + PCA).
- Conditional correlation report for the existing four axes
  within high-CBA and low-CBA subsets.

### v0.9.0a0 — external behavioural validation

The transcript adapter (planned for v0.9.0a0) will ingest
real-data zoo entries with paired declared and executed
trajectories. Two validation pathways open up:

1. **FAITHCOT-BENCH** (Sze et al., 2024). 1,000+ annotated CoT
   trajectories; the human-annotated faithfulness label can be
   regressed against the structural CBA score from this
   document. Effect-size target: rank correlation `ρ > 0.5`
   between the two on the test split. Effect size below `0.3`
   would falsify the structural proxy *as a faithfulness
   measure on LLM CoT*, and the `docs/CBA.md` document would be
   updated to either restrict the proxy's scope or revise the
   formula.
2. **Sheeran-style behavioural data.** Datasets pairing
   declared intentions with measured behaviour (health,
   environmental, consumer choice). Effect-size target:
   variance explained by structural CBA score within
   `[15%, 40%]`, comparable to Sheeran's `≈ 28%` reference
   figure. Outside this range would not falsify the structural
   proxy outright but would prompt a reanalysis of which
   sub-component of the intention–behaviour gap the structural
   proxy is actually capturing.

Both are explicitly **deferred validation**, with thresholds
pre-registered now to constrain post-hoc rationalisation later.

### v0.9.x and beyond — community validation

The `pip install autonometrics`-able structural CBA proxy is
made available to the community **before** behavioural
validation is complete, with the explicit invitation, mirrored
in [`docs/PBA.md`](PBA.md):

> *We have built the instrument. We invite the community to
> validate it against external behavioural measurements that we
> as a coder-philosopher project cannot ourselves carry out.*

This invitation is sincere and resourced: the v0.9.0a0
transcript adapter will accept CSV inputs in a documented
schema, the package will publish a registered preprint of this
design document on PhilArchive (mirror of the source paper that
introduced the CBA term), and the GitHub issues template will
include a *behavioural validation* category for community
results to be filed against.

## Risks and mitigations

The following are the risks the design tries to mitigate
explicitly. Risks left unmitigated are listed last so the
reader sees what the design does *not* claim.

### R1 — Theil's U scoring bijections as `1.0`

A non-identity bijection `E = π(D)` with `π` a fixed
permutation of the alphabet scores `cba_theil = 1.0`. This is
mathematically correct (declaration deterministically predicts
execution) but counter-intuitive (the system never does what it
says).

**Mitigation.** The diagnostic match-rate `cba_match` is
reported alongside; the divergence between `cba_theil ≈ 1.0`
and `cba_match ≈ 0.0` is the textbook flag for "informative
declaration, systematic substitution". The README, this
document, and the docstring of `compute_cba_theil_u` all
describe the case explicitly.

### R2 — Estimator bias at low `T`

Plug-in entropy estimators are biased at finite `T`; the bias
shrinks as `O(1/T)`.

**Mitigation.** The implementation uses Miller-Madow
correction (already used by `closure` and `memory`). A low-N
warning is raised at `T < 100`. The benchmark is configured
with `T = 256` for `PromisedCycle` to comfortably exceed the
warning threshold.

### R3 — Alphabet inflation

If the declared alphabet is much larger than the executed
alphabet (or vice versa), MI estimates can degrade.

**Mitigation.** The implementation pre-aligns the alphabets
(unique-symbol mapping) before computing MI, and the docstring
warns against passing trajectories where the alphabets diverge
by more than a factor of `10×`. A future release can add an
adaptive alphabet-binning helper.

### R4 — Substrate narrowness

Most existing adapters return `None` for CBA; the v0.8.0a0
benchmark therefore has many CBA dropouts.

**Mitigation.** This is *expected* given the lineage; CBA is
the narrowest axis in the atlas by design. The benchmark
reports `n_valid` per axis and the changelog states explicitly
that the five-axis cloud has fewer CBA-defined points than
the four-axis cloud has of the others.

### R5 — Conditional correlations being noisy

The conditional-correlation report partitions the sample into
two subsets (`high CBA`, `low CBA`); each subset will have
fewer points than the whole, raising statistical-noise
concerns.

**Mitigation.** The conditional-correlation report is
explicitly **not gated**. It is a descriptive analysis with
honest uncertainty bands; conclusions drawn from it are
labelled "Level-3-suggestive" rather than "Level-3-confirmed".
v0.9.0a0 will rerun the analysis on the larger transcript
zoo, where statistical power is greater.

### R6 — Lineage misappropriation

PBA's structural CBA proxy is not what Festinger, Sheeran, or
PhilArchive 2024 originally proposed. Calling our number
"Festinger's ratio" or "PhilArchive's CBA" would be
misleading.

**Mitigation.** The headline metric is named **`cba_theil_u`**
in code and **"information-theoretic CBA proxy (Theil-U style)
on declared / executed trajectories"** in prose. The PhilArchive
2024 paper is cited as the **framing source** for the *name*,
not as the source of the formula. Festinger and Sheeran are
cited as *lineage*, not as authors of the present formula.

### R7 — Risks left unmitigated

The design does not attempt to mitigate the following:

- **Semantic misalignment.** A system whose declaration is
  syntactically distinct from its execution but semantically
  equivalent (e.g. "I'll go to the store" vs "I'll buy
  groceries") will look incoherent to the structural proxy.
  Resolving this requires natural-language understanding,
  which the offline structural design deliberately renounces.
  The LLM-judge sister implementations (DeepEval, Snowflake)
  cover this case.
- **Strategic declaration.** A system that learns to declare
  whatever its execution will be (post-hoc rationalisation)
  scores high on the structural proxy even though it is, in
  the AI-alignment sense, *unfaithful*. Detecting this requires
  intervention experiments (Lanham 2023's methodology), not
  observational data. The structural proxy is descriptive, not
  diagnostic of strategic behaviour.

These limits are acknowledged here so the reader knows the
ground the proxy does **not** cover, in addition to the ground
it does.

## Implementation sketch

The implementation footprint for v0.8.0a0:

### New files

- `src/autonometrics/metrics/coherence.py` — implements
  `compute_cba_theil_u(declared, executed, *, low_n_threshold=100)`
  and the diagnostic `_cba_match_rate(declared, executed)`.
- `src/autonometrics/adapters/promised_cycle.py` — implements
  the `PromisedCycle` adapter with the `get_declared_executed`
  method and parameters `length`, `period`, `alphabet`,
  `p_noise`, `mode ∈ {"random_noise", "adversarial_shift"}`.
- `tests/unit/test_coherence.py` — boundary-case unit tests.
- `tests/unit/test_promised_cycle.py` — adapter invariants and
  reproducibility tests.
- `tests/integration/test_five_axis_benchmark.py` — extends the
  existing four-axis benchmark with the CBA column.
- `tests/integration/test_cba_independence.py` — static-import
  audit + empirical `|r| < 0.9` check.

### Modified files

- `src/autonometrics/core.py` — extends the `AutonomySystem`
  protocol with the optional `get_declared_executed` method;
  registers `cba_theil_u` in the `_METRIC_REGISTRY`,
  `_METRIC_INPUT`, `_PROFILE_FIELD` tables; bumps version to
  `0.8.0a0`.
- `src/autonometrics/profile.py` — adds `cba_theil_u: float |
  None` and `cba_diagnostics: dict[str, float] | None` fields
  to `AutonomyProfile`.
- `src/autonometrics/__init__.py` — exports
  `compute_cba_theil_u` and `PromisedCycle` in `__all__`.
- `docs/PBA.md` — adds the fifth axis to the atlas figure and
  records the v0.8.0a0 release with its findings on
  cross-axis correlation and conditional correlation.
- `docs/ATLAS_GEOMETRY.md` — appends the v0.8.0a0
  five-axis-cloud rerun results.
- `README.md` and `README.es.md` — adds CBA to the four-axis
  table with the same row format as the others.
- `CHANGELOG.md` (or release notes) — records the v0.8.0a0
  release.

### Pseudocode for the headline metric

```python
import numpy as np

def compute_cba_theil_u(
    declared: np.ndarray,
    executed: np.ndarray,
    *,
    low_n_threshold: int = 100,
) -> float:
    """Information-theoretic CBA proxy (Theil's U) on declared /
    executed trajectories.

    Returns I(D; E) / H(D) in [0, 1], with Miller-Madow bias
    correction.  Returns 0.0 when H(D) == 0 (no declared-side
    uncertainty to resolve).
    """
    if declared.shape != executed.shape:
        raise ValueError("declared and executed must have the same shape")
    T = declared.shape[0]
    if T < low_n_threshold:
        warnings.warn(
            f"CBA computed at T={T} < {low_n_threshold}; "
            "estimator bias may be substantial",
            RuntimeWarning,
        )

    H_D = _shannon_entropy_mm(declared)
    if H_D == 0.0:
        return 0.0
    H_DE = _joint_entropy_mm(declared, executed)
    H_E = _shannon_entropy_mm(executed)
    I_DE = H_D + H_E - H_DE
    return float(np.clip(I_DE / H_D, 0.0, 1.0))
```

Diagnostics (`cba_match_rate`) are computed inline by the
metric runner and attached to `AutonomyProfile.diagnostics`.

The `PromisedCycle` adapter is the simplest non-trivial
substrate the package can offer for the new axis. Its
implementation is a few dozen lines on top of the existing
adapter machinery.

### Implementation order

1. `coherence.py` with full unit-test coverage of boundary
   cases.
2. `PromisedCycle` adapter with `get_declared_executed`.
3. Protocol extension in `core.py`; registry entries; profile
   field.
4. Five-axis benchmark integration test.
5. Independence audit (static + empirical).
6. Conditional-correlation report.
7. Five-axis geometry rerun (PCA + clustering, scripts already
   in `tests/benchmarks/atlas_geometry.py`).
8. Documentation updates (`PBA.md`, `ATLAS_GEOMETRY.md`,
   `README.md`, `README.es.md`).
9. Release: tag, build, twine upload, changelog.

## Why this design is conservative

The design is conservative on three axes that PBA has
historically been bitten by:

- **It does not claim a universal CBA**. The metric scores only
  systems with a declarative layer, returns `None` otherwise,
  and the package documents the dropout instead of fabricating
  a synthetic declaration.
- **It does not claim mathematical novelty.** Theil's U dates
  to 1970, Festinger to 1957. The package contribution is
  *integration* (one more axis, same atlas convention,
  cross-axis independence audited), *not* invention.
- **It defers behavioural validation explicitly.** The
  structural proxy is named, lineage-traced, and bounded by
  effect-size targets a future cycle can apply. The
  intention–behaviour gap literature has spent half a century
  on this question and the package does not pretend a single
  release closes it.

The conservatism is the point. The ratio of *statements made*
to *statements that have been independently audited or
empirically tested* should stay close to one. v0.8.0a0 keeps
that ratio in line.

## Design decisions (locked for v0.8.0a0)

The following decisions are pre-registered and locked for the
v0.8.0a0 release. Any deviation requires an updated section
appended to this document, dated and signed.

1. **Headline metric.** `cba_theil_u = I(D; E) / H(D)` with
   Miller-Madow correction. Diagnostic companion:
   `cba_match_rate`.
2. **Default low-N threshold.** `T_min = 100`. Below this,
   the metric still runs but a `RuntimeWarning` is raised.
3. **Adapter protocol extension.** Single optional method
   `get_declared_executed() -> tuple[np.ndarray, np.ndarray]
   | None`. Returning `None` triggers CBA dropout for that
   system.
4. **Naming convention.**
   - In code: `cba_theil_u` (axis), `cba_match_rate`
     (diagnostic).
   - In prose: "information-theoretic CBA proxy (Theil-U style)".
   - Lineage tags: PhilArchive 2024 (frame name), Theil 1970
     (formula), Festinger 1957 / Sheeran 2002 (phenomenon).
5. **Reference adapter.** `PromisedCycle` with
   `mode ∈ {"random_noise", "adversarial_shift"}`. Boundary
   sanity checks at `p_noise ∈ {0.0, 1.0}` are hard gates.
6. **Independence audit.** Static import audit (hard gate) +
   pairwise `|r| < 0.9` (hard gate) + pairwise `|r| < 0.7`
   (soft gate, ships with note).
7. **Conditional-correlation report.** Mandatory in v0.8.0a0
   release, ungated, recorded in `docs/ATLAS_GEOMETRY.md` and
   `docs/PBA.md`.

These decisions can be revisited only after v0.8.0a0 ships and
only with a written update to this document.

## References

The reference list is organised in three buckets.

### Core lineage (the phenomenon)

- Aristotle (≈ 350 BCE). *Ethica Nicomachea*, Book VII.
- Anscombe, G. E. M. (1957). *Intention*. Harvard University
  Press.
- Festinger, L. (1957). *A Theory of Cognitive Dissonance*.
  Stanford University Press.
- Davidson, D. (1970). "How is Weakness of the Will Possible?"
  In *Moral Concepts*, ed. Joel Feinberg.
- Searle, J. (1979). *Expression and Meaning: Studies in the
  Theory of Speech Acts*. Cambridge University Press.
- Bratman, M. (1987). *Intention, Plans, and Practical Reason*.
  Harvard University Press.
- Gollwitzer, P. M. (1999). "Implementation intentions: Strong
  effects of simple plans". *American Psychologist*, 54(7),
  493–503.
- Sheeran, P. (2002). "Intention–Behavior Relations: A
  Conceptual and Empirical Review". *European Review of Social
  Psychology*, 12(1), 1–36.
- Gollwitzer, P. M., & Sheeran, P. (2006). "Implementation
  intentions and goal achievement: A meta-analysis of effects
  and processes". *Advances in Experimental Social Psychology*,
  38, 69–119.
- Sheeran, P., & Webb, T. L. (2016). "The Intention-Behavior
  Gap". *Social and Personality Psychology Compass*, 10(9),
  503–518.

### Operational lineage (the formula machinery)

- Theil, H. (1970). "On the Estimation of Relationships
  Involving Qualitative Variables". *American Journal of
  Sociology*, 76(1), 103–154. (Source of Theil's U / uncertainty
  coefficient.)
- Cover, T. M., & Thomas, J. A. (2006). *Elements of
  Information Theory* (2nd ed.). Wiley. (Reference for entropy
  and mutual information conventions.)
- Miller, G. A. (1955). "Note on the bias of information
  estimates". In *Information Theory in Psychology*, ed.
  H. Quastler. (Origin of Miller-Madow bias correction.)
- Madow, W. G. (1948). "Note on the consistency of certain
  estimates of entropy". *Annals of Mathematical Statistics*,
  19(2), 240–243.
- Crawford, V. P., & Sobel, J. (1982). "Strategic Information
  Transmission". *Econometrica*, 50(6), 1431–1451.

### Modern AI-alignment & evaluation (sister implementations)

- Wang, X. et al. (2022). "Self-Consistency Improves Chain of
  Thought Reasoning in Language Models". *NeurIPS 2022*.
- Turpin, M. et al. (2023). "Language Models Don't Always Say
  What They Think: Unfaithful Explanations in Chain-of-Thought
  Prompting". *NeurIPS 2023*.
- Lanham, T. et al. (2023). *Measuring Faithfulness in Chain-of-
  Thought Reasoning*. Anthropic.
- Sze, S. et al. (2024). *FAITHCOT-BENCH: A Benchmark for
  Faithful Chain-of-Thought Reasoning*. Preprint.
- PhilArchive (2024). *Coherence-Based Alignment*. Preprint.
  https://philarchive.org/archive/AAA-CBA-2024 (placeholder for
  the actual archive ID; to be confirmed before publication).
- DeepEval (2024–2025). *Plan Adherence Metric*.
  https://github.com/confident-ai/deepeval (open-source LLM
  evaluator; sister implementation).
- Snowflake (2024–2025). *Agent GPA: Goal-Plan-Action
  Evaluation Framework*. (Industry sister implementation.)

The reference list is not exhaustive; it covers the works
cited inline. The v0.9.0a0 transcript adapter will ship with
its own data-source bibliography.

## Resumen en español

> *Esta sección reproduce, de forma compacta y en español
> neutro, las decisiones del documento. La autoridad sobre el
> diseño la tiene el texto en inglés.*

### Qué es CBA

CBA (Coherence-Based Alignment) es la quinta arista del atlas
PBA. Mide cuánto de lo que un sistema **declara que va a hacer**
predice lo que el sistema **efectivamente hace**. Viene de una
tradición distinta a las cuatro aristas anteriores: la del
*intention–behaviour gap* (Festinger 1957, Sheeran 2002,
Gollwitzer 1999) con raíces en Aristóteles (akrasia) y
Anscombe (dirección de ajuste), y operacionalizada
recientemente en el espacio de alineamiento de IA (Lanham 2023,
Turpin 2023, PhilArchive 2024).

### Por qué es distinta a las otras

Las cuatro aristas previas miden propiedades de **una sola
trayectoria** (clausura, memoria, restricciones, persistencia).
CBA mide el **acoplamiento entre dos trayectorias paralelas**
(la declarada y la ejecutada). Es la única arista que necesita
que el sistema tenga una **capa declarativa** además de una
capa ejecutiva. Esto la hace **más estrecha** (no toda
sustancia tiene capa declarativa) pero **informativamente
distinta**.

### Operacionalización elegida

Se ship el indicador `cba_theil_u = I(D; E) / H(D)` (U de
Theil), con corrección de sesgo Miller-Madow y advertencia
para `T < 100`. En paralelo se reporta como diagnóstico
`cba_match_rate` (fracción de pasos en que `D` y `E`
coinciden), porque permite distinguir el caso "sustitución
sistemática informativa" del caso "declaración inútil".

### Adaptador de referencia: `PromisedCycle`

Un ciclo periódico de longitud `k` que expone una **agenda
declarada** y una **ejecución** con ruido `p_noise`. Casos
límite (verificaciones obligatorias antes del release):

- `p_noise = 0.0` → `cba_theil ≥ 0.95`.
- `p_noise = 1.0` → `cba_theil ≤ 0.10`.
- modo `adversarial_shift` (sustitución sistemática) →
  `cba_theil ≥ 0.90` **y** `cba_match ≤ 0.10`.

### Adaptadores existentes

ECA, Kauffman, PeriodicCycle y SimpleAutomaton **no exponen**
capa declarativa. CBA devuelve `None` para ellos. El
benchmark reporta `n_valid` honestamente y no fabrica
declaraciones sintéticas.

### Independencia respecto de las otras aristas

- Auditoría estática de imports (hard gate): `coherence.py` no
  importa de los módulos de las otras aristas.
- Correlación par a par `|r| < 0.7` (soft gate); `|r| < 0.9`
  (hard gate).
- Rerun de PCA del análisis `ATLAS_GEOMETRY.md` extendido a
  5 ejes; `λ_max < 0.65` se mantiene como umbral.
- Análisis de **correlaciones condicionales** (nuevo): se
  separa la muestra en `cba_theil ≥ 0.7` y `cba_theil < 0.3`
  y se comparan las correlaciones de las otras aristas en
  cada subconjunto. Diferencias sustanciales se reportan
  como evidencia *Level-3-suggestive*.

### Validación externa (diferida)

- v0.8.0a0: validación interna (sanity, independencia,
  geometría).
- v0.9.0a0: validación contra **FAITHCOT-BENCH** (`ρ > 0.5`
  contra etiqueta humana de fidelidad) y contra datos
  conductuales tipo Sheeran (varianza explicada en
  `[15%, 40%]`, ≈ 28% de referencia).
- v0.9.x y posterior: validación abierta a la comunidad,
  con plantilla de issue dedicada y schema CSV documentado.

### Lo que el diseño **no** afirma

- No mide CBA semántico (frases distintas con el mismo
  significado quedan fuera).
- No detecta racionalización post-hoc estratégica
  observacionalmente; eso requiere experimentos de
  intervención (Lanham 2023).
- No reemplaza a las herramientas LLM-as-judge (DeepEval,
  Snowflake); las complementa con una versión offline,
  determinista y comparable entre sustancias.

Todos los detalles, criterios de falsación, advertencias del
estimador, alternativas rechazadas y decisiones bloqueadas
están en el texto en inglés más arriba. Esta sección es solo
un mapa rápido para lectoras y lectores que llegan primero al
español.
