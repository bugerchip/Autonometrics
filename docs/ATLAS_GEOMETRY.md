# Atlas geometry: are the four PBA axes shadows of one object?

**Status**: pre-registration. Locked at the start of the
`v0.7.2a0` cycle, before any extended-zoo analysis is run.

**Cycle**: `v0.7.2a0` (analytical maintenance, no new metric).

**Predecessor design documents**:
[`docs/PBA.md`](PBA.md), [`docs/RAI.md`](RAI.md),
[`docs/CONSTRAINT_CLOSURE.md`](CONSTRAINT_CLOSURE.md).

---

## Why this document exists

After four releases the package ships four PBA axes:

- `ratio_endo_total` (closure)
- `memory_endo_ratio` (memory)
- `constraint_closure` (constraint)
- `rai_proxy_persistence` (persistence)

Each pairwise correlation on the `v0.7.0a0` benchmark sits below
the `|r| < 0.7` falsification gate, so the four axes carry
**distinct information** on the current zoo. That falsifies the
strong Level-1 reading of PBA ("one scalar in different
notations") but it does **not** decide between the two remaining
ontologies that
[`docs/PBA.md`](PBA.md#what-pba-actually-claims) explicitly
distinguishes:

- **Level 2 reading.** *One* multidimensional object. The four
  axes are projections of the same structure onto different
  coordinate systems. They are correlated because they are
  views of the same object; they are not redundant because each
  view sees something the others miss.
- **Level 3 reading.** *Several* objects sharing a label. Each
  axis measures a different phenomenon; the conjunction of the
  four under the name "structural self-determination" is a
  taxonomic mistake. The package accidentally bundled four
  different things together.

Both readings are *consistent* with the empirical correlation
pattern observed in `v0.7.0a0`. The benchmark, by itself, does
not decide between them.

This cycle's purpose is **partial decision** by *atlas
geometry*. Looking at the shape of the 4-D point cloud the
benchmark produces:

- if the cloud is approximately **low-dimensional** (a
  near-line, a near-plane), there is a structural reason the
  axes co-vary in the way they do, and that reason is evidence
  for **a single underlying object** with a few free parameters
  (Level 2);
- if the cloud is approximately **isotropic** (full-rank, no
  direction explains noticeably more variance than another),
  there is no privileged underlying coordinate, and that is
  evidence for **separate objects glued together by a label**
  (Level 3).

Neither outcome *proves* one reading. Both are *evidence*.
The strong validation — does the atlas predict behaviour outside
the structural domain it was built from? — is deferred to
`v0.9.0` (LLM transcript adapter + behavioural / RAI-style
validation).

---

## What this cycle is *not*

This document fixes one boundary deliberately: **the geometry
analysis can refute or weaken Level 2; it cannot confirm it.** The
strongest possible outcome here is "Level 2 is *consistent with*
the structural geometry of the four-axis cloud, with the strength
captured by the pre-registered indicators below". The strongest
possible *negative* outcome is "Level 2 is *suspect*: the cloud
geometry does not support a single-object reading on the structural
zoo".

Specifically, this cycle does **not**:

1. Validate the persistence axis against behavioural / RAI data
   (deferred to `v0.9.0`).
2. Add a fifth axis (deferred to `v0.8.0`).
3. Formalise the persistence boundary theorems (deferred to
   `v0.7.1`).
4. Decide between Level 2 and Level 3 once and for all. The
   final decision needs cross-tradition behavioural validation
   that the structural benchmark cannot supply.

What it *does* is push the **prior** between the two ontologies
based on a piece of evidence that does not require the v0.9.0
adapter to be in place.

---

## Locked decisions

The following decisions are pre-registered. Any deviation from
them in the implementation phase has to be flagged explicitly and
justified in the verdict section, otherwise the analysis is
considered non-pre-registered (i.e. exploratory) and the
conclusions cannot count as evidence for the level question.

### Decision 1 — Sample size and zoo extension

The `v0.7.0a0` benchmark produced **48** fully-valid points in
4-D from 69 swept configurations (21 dropouts due to degenerate
trajectories). PCA on `n = 48` in `d = 4` is **underpowered**:
clustering structure on adapter-class boundaries can dominate
the geometric signal, and the principal-component variance
estimates have wide confidence intervals.

The cycle therefore extends the zoo to a target of **at least
200 fully-valid points**. The extension is achieved by:

1. Increasing `n_seeds` per configuration on every existing
   adapter (typically from 5 to 20).
2. *Not* adding new adapter classes or new parameter values.
   Adding adapter classes mid-cycle would conflate "more
   sample" with "different population" and would invalidate the
   pre-registration.

The exact final `n` is whatever the extended sweep produces;
the pre-registered floor is `n_valid >= 200`.

### Decision 2 — Techniques and order

The cycle commits to a **strict order**: numerical primary,
visual secondary.

1. **PCA**, computed via `numpy.linalg.svd` on the
   centred-and-scaled data matrix, is the *primary* technique.
   PCA is linear, deterministic, and produces single-number
   summaries (variance explained per component). Its main
   limitation — that it cannot detect curved structure — is
   accepted as a known cost.
2. **K-means clustering** with the **silhouette score**
   (Rousseeuw 1987) is the *secondary* technique. K-means
   is run for `k = 1, 2, 3, 4, 5` (a fixed grid set in
   advance). The chosen `k` is the value with the highest
   silhouette score. The *strength* of the clustering is read
   from the silhouette value itself, not from how the clusters
   look.
3. **t-SNE / UMAP** plots, if produced at all, are
   **illustrative only**. They are flagged as such in the
   figure title and in the doc text. They cannot count as
   evidence for or against any level reading. (t-SNE / UMAP
   construct local-similarity preserving embeddings that
   *systematically produce* visual clusters even on isotropic
   noise, so they cannot distinguish Level 2 from Level 3.)

This order is chosen explicitly to **prevent** the typical
"saw a cluster on t-SNE → declared Level 2 confirmed" failure
mode.

### Decision 3 — Pre-registered numerical thresholds

The thresholds below are anchored in textbook practice (Jolliffe
2002, *Principal Component Analysis*; Rousseeuw 1987, *Silhouettes:
A graphical aid to the interpretation and validation of cluster
analysis*) and **not** tuned to the `v0.7.0a0` snapshot. Two
authors have access to the snapshot before this document is
locked, but the thresholds below are stated in terms of
*independent* literature conventions, not in terms of what the
snapshot would yield.

**PCA-based criteria.** Let `λ_i` be the share of total variance
explained by the `i`-th principal component (sorted decreasingly).
Then on the extended zoo:

| Indicator       | Range            | Reading                                                                 |
|-----------------|------------------|-------------------------------------------------------------------------|
| `λ_1`           | `>= 0.70`        | Strong single-axis structure. **Refuerza Nivel 2 (objeto único).**       |
| `λ_1`           | `0.50 — 0.70`    | Dominant first axis with non-trivial residual structure.                 |
| `λ_1 + λ_2`     | `>= 0.85`        | Effectively two-dimensional cloud. **Refuerza Nivel 2 plural.**         |
| `λ_1 + λ_2`     | `0.65 — 0.85`    | Partial low-dimensionality; mixed evidence.                              |
| `λ_1`           | `< 0.40` *and*   |                                                                          |
| `λ_1 + λ_2`     | `< 0.65`         | Cloud is approximately isotropic. **Sospecha Nivel 3.**                  |

These ranges intentionally allow for an *inconclusive* zone
(`0.40 ≤ λ_1 < 0.50`, `0.65 ≤ λ_1 + λ_2 < 0.85`) where the
analysis declines to take a side. *Inconclusive* is a permitted
verdict and is the honest outcome when the data does not commit.

**Clustering-based criteria.** Let `s(k)` be the average
silhouette score on `k` k-means clusters, computed on the
PCA-whitened data, and let `k* = argmax_k s(k)` over the fixed
grid `k ∈ {2, 3, 4, 5}` (Rousseeuw conventions).

| Indicator                 | Range          | Reading                                              |
|---------------------------|----------------|------------------------------------------------------|
| `s(k*)`                   | `>= 0.50`      | Strong cluster structure. Concentrated regions.       |
| `s(k*)`                   | `0.25 — 0.50`  | Reasonable cluster structure.                         |
| `s(k*)`                   | `< 0.25`       | Weak / no cluster structure. The cloud is diffuse.    |

The reading of `s(k*) >= 0.50` is **ambiguous between Level 2 and
Level 3**: strong clusters can come either from "different parts
of the same object" (Level 2) or from "different objects"
(Level 3). Clustering alone *does not* decide the level question;
it only describes whether the cloud is concentrated or diffuse.
The level reading is then resolved by **adapter-class
composition of clusters**:

- if `k*` clusters correlate with **adapter classes** (each
  cluster is dominated by one of `ECASystem`, `KauffmanNetwork`,
  `PeriodicCycle`, `SimpleAutomaton`), the clustering reflects
  *the zoo's structure*, not the autonomy structure. **Cluster
  result is non-informative for the level question.**
- if `k*` clusters cut **across** adapter classes (each cluster
  contains points from multiple adapter classes), the clustering
  reflects autonomy structure that survives substrate.
  **Refuerza Nivel 2**.

**Conditional-correlation criteria.** Let `r_ij | C` be the
within-cluster Pearson correlation of axes `i` and `j` on cluster
`C`. If the global correlation `r_ij` differs from the
within-cluster `r_ij | C` by more than `0.30` *for at least two
of the four clusters in the chosen `k*`*, then the global
correlation is partly an *artifact of the cluster structure*
(Simpson's-paradox-style). This is recorded as a *health flag*,
not as a level-question decision.

### Decision 4 — Treatment of dropouts (the 21 `n/a` points)

The `v0.7.0a0` benchmark dropped 21 of the 69 configurations
because their focal trajectories are degenerate for at least one
of the four metrics. The structural-geometry analysis runs on the
non-degenerate subset (the extended `>= 200`-point zoo).

The dropouts are **not** discarded silently:

1. The proportion of dropouts per adapter class and per
   parameter is reported in a separate table in the verdict
   section.
2. If the dropout pattern is **systematic** (e.g. every
   `coupling = 0.0` Kauffman drops, every `rule ∈ {0, 90, 184,
   250}` ECA drops, etc.), that pattern is itself reported as a
   structural finding. Systematic dropouts are *evidence* that
   the metric set has joint blind spots.
3. The verdict explicitly conditions on `non-degeneracy`. This
   is the same convention `docs/PBA.md` already uses for the
   closure-saturation theorem and the constraint-closure
   trivial-zero theorem.

### Decision 5 — Documentation structure

This document, `docs/ATLAS_GEOMETRY.md`, is the canonical record
of the cycle. It contains:

1. **Pre-registration** (this document, locked at cycle start).
2. **Implementation report** (added after the analysis is run).
3. **Verdict section** (added after the implementation report,
   explicitly comparing observed indicators against the
   thresholds locked in section "Decision 3").
4. **Rejected and deferred** (added in the verdict section if
   any deviations from the pre-registration occurred).

`docs/PBA.md` and `docs/PBA.es.md` are *updated* with the
verdict — gaining a new "Atlas geometry" subsection — but do
**not** host the pre-registration. This separation makes the
chronological audit trail explicit: PBA states the framework, the
geometry document records the cycle that subjects the framework
to a particular structural test.

---

## Predicted outcomes (worked through)

Three clean outcomes are possible. They are listed in advance
so the verdict cannot drift after the analysis runs.

### Outcome A — Level 2 reinforced

`λ_1 >= 0.70` *or* (`λ_1 + λ_2 >= 0.85` and `s(k*) >= 0.25`
with cross-adapter clusters).

Reading: the cloud has a single privileged direction or sits on
a 2-D submanifold of the 4-D space. Either is *consistent with* a
single multidimensional object whose four axes are projections.
PBA's Level 2 reading gains structural support. Documents and
README change "Level 2 plausible" to "Level 2 plausible and
geometrically supported".

This outcome **does not** confirm Level 2. It only blocks one
of its falsification routes.

### Outcome B — Inconclusive

`λ_1 ∈ [0.40, 0.70)` *and* `λ_1 + λ_2 ∈ [0.65, 0.85)` *and*
`s(k*) < 0.25`.

Reading: the cloud has no privileged direction strong enough to
support Level 2, but no clear isotropy strong enough to support
Level 3. The structural zoo, as currently shaped, is silent on
the level question. The verdict reports this honestly. The level
question gets pushed entirely to `v0.9.0`'s behavioural
validation; the structural geometry alone is not enough.

This outcome is permitted and expected with non-trivial prior
mass. The pre-registration explicitly *avoids* squeezing every
result into a yes/no answer.

### Outcome C — Level 3 suspected

`λ_1 < 0.40` *and* `λ_1 + λ_2 < 0.65`, *and* the `k*` clusters
correlate with adapter classes.

Reading: the cloud is roughly isotropic, and what little
structure exists comes from substrate (adapter type) rather
than autonomy. PBA's Level 2 reading is *suspect* on the
structural domain. The package would *not* be downgraded
unilaterally on this evidence — Level 3 still has to survive the
behavioural validation in `v0.9.0` before being accepted as the
final reading — but the documents do change tone: "Level 2
plausible and geometrically supported" gives way to "Level 2
under stress; Level 3 not yet ruled out".

The package itself does not change; the four metrics still
work and still do what their docstrings claim. Only the
*narrative around their conjunction* changes.

---

## Implementation steps (locked order)

1. **Pre-registration commit** — this document, no analysis
   code, no extended data. Establishes the locked decisions.
2. **Benchmark extension** — `examples/benchmark_demo.py`
   re-run with `n_seeds` raised to the level needed to clear
   `n_valid >= 200`. New CSV + log + scatter snapshot at
   `docs/benchmarks/v0.7.2a0.{csv,png,log.txt}`.
3. **Analysis script** —
   `examples/atlas_geometry_diagnostic.py`. Reads the
   `v0.7.2a0` CSV, drops the `n/a` rows, computes:
   - centred + scaled data matrix;
   - PCA via `numpy.linalg.svd`, reports `λ_i` and component
     loadings;
   - K-means for `k ∈ {1, …, 5}` (numpy implementation, no
     sklearn);
   - silhouette score per `k`;
   - per-cluster adapter-class composition;
   - per-cluster within-cluster correlation matrices.
   Output: stdout table + `docs/benchmarks/atlas_geometry_v0.7.2.{csv,log.txt}`.
4. **Visualisation** —
   `examples/atlas_geometry_plot.py`. Renders the PCA biplot
   (PC1 vs PC2 with axis loadings) and an *illustrative*
   t-SNE / UMAP projection if the optional dependency is
   available (degrades gracefully otherwise). The t-SNE figure
   is labelled "Illustrative; not used as evidence" in the
   title and in the figure caption.
5. **Verdict** — appended to this document, comparing the
   observed indicators against the pre-registered thresholds
   from "Decision 3". `docs/PBA.md` and `docs/PBA.es.md` gain
   their "Atlas geometry" subsection summarising the verdict.
   `README.md` updates the roadmap and the benchmark headline
   numbers.
6. **Release commit** — bump `0.7.0a0 → 0.7.2a0` (skipping
   `0.7.1a0`, which holds the persistence boundary theorems
   pending; this is documented in the CHANGELOG so the version
   gap is auditable).

The order is enforced by the commit chain: the pre-registration
commit lands *first*, and the analysis script's first line of
output cites this document's locked thresholds. Any deviation
from the locked decisions raises a deviation flag in the
verdict and is recorded as a separate sub-section.

---

## Independence-by-design (recap)

The new analysis script is a **consumer** of the package, not
an extension of it. It imports `autonometrics` only to read
the public API; it does not add a new metric, a new adapter or
a new field on `AutonomyProfile`. The release surface of the
package is therefore unchanged: the four shipped metrics, the
benchmark, the diagnostic, the plot. The geometry analysis
lives in `examples/` exactly the way the
saturation, constraint-density, and persistence diagnostics
already do.

---

## References (decision anchors)

- **Jolliffe, I. T. (2002).** *Principal Component Analysis*,
  2nd ed. Springer. Standard textbook for PCA variance-share
  thresholds.
- **Rousseeuw, P. J. (1987).** *Silhouettes: A graphical aid to
  the interpretation and validation of cluster analysis*.
  Journal of Computational and Applied Mathematics 20, 53 — 65.
  Standard reference for the silhouette interpretation table
  used in "Decision 3".
- **Simpson, E. H. (1951).** *The interpretation of interaction
  in contingency tables*. Journal of the Royal Statistical
  Society B 13, 238 — 241. Origin of the conditional-correlation
  paradox the analysis flags as a health check.
- **van der Maaten, L., & Hinton, G. (2008).** *Visualizing
  Data using t-SNE*. Journal of Machine Learning Research 9,
  2579 — 2605. Cited so the t-SNE figure can be flagged
  honestly as illustrative.
- **PBA framework.** [`docs/PBA.md`](PBA.md) /
  [`docs/PBA.es.md`](PBA.es.md). The Level 1 / 2 / 3 reading
  this analysis tries to discriminate among.
- **RAI design.** [`docs/RAI.md`](RAI.md). Sets the
  validation roadmap (`v0.9.0` for behavioural validation) the
  geometry analysis explicitly does not subsume.

---

*Locked: open of cycle `v0.7.2a0`. Subsequent edits to this
document are restricted to (a) the implementation report, (b)
the verdict section, (c) the rejected/deferred section. The
"Locked decisions" section is read-only after this commit.*

---

## Implementation report

This section is added **after** the analysis was run. The
"Locked decisions" section above is unchanged from the
pre-registration commit.

### Sample produced

- `n_total = 405` swept configurations (the same five ECA rules,
  five Kauffman couplings, three periodic periods, and two
  `SimpleAutomaton` modes as in `v0.7.0a0`; only `n_seeds` was
  raised).
- `n_valid = 247` fully-valid 4-D points after dropouts.
- `n_dropped = 158` (39%).

The valid count clears the pre-registered floor of 200 with
margin. To clear the floor with only `n_seeds` extension, the
final value used was `n_seeds = 30`, not 20 as the locked
decision text says "typically". This is **within** the
pre-registered intent (the floor is on `n_valid`, not on
`n_seeds`); the `n_seeds = 20` value yields ~163 valid points
and would have missed the floor. The CSV is at
`docs/benchmarks/v0.7.2a0.csv`; the human-readable run log is
at `docs/benchmarks/v0.7.2a0.log.txt`.

### Dropout pattern

| Adapter class      | total | dropped | rate |
|--------------------|------:|--------:|-----:|
| `ECASystem`        |   150 |      82 | 55%  |
| `KauffmanNetwork`  |   150 |      76 | 51%  |
| `PeriodicCycle`    |    45 |       0 | 0%   |
| `SimpleAutomaton`  |    60 |       0 | 0%   |

Dropouts are **not** random across the zoo. They concentrate on
`ECASystem` (rules with constant or near-constant focal
trajectories at `width = 51`) and `KauffmanNetwork` (focal
nodes that absorb into a fixed point at extreme `coupling`
values). `PeriodicCycle` and `SimpleAutomaton` produce
non-degenerate trajectories on every seed.

This is itself a structural finding: the metric set has a
**joint blind spot** that is selective for the cellular and
network adapters, not for the synthetic ones. We record this as
a health flag and condition the verdict on
`non-degeneracy`, exactly as `docs/PBA.md` already does for the
saturation theorem and `docs/CONSTRAINT_CLOSURE.md` for the
trivial-zero theorem.

### Indicators (raw)

PCA on the standardised 4-D matrix:

| Indicator         |  Value |
|-------------------|-------:|
| `λ_1`             | 0.4688 |
| `λ_2`             | 0.3402 |
| `λ_3`             | 0.1062 |
| `λ_4`             | 0.0848 |
| `λ_1 + λ_2`       | 0.8090 |
| `λ_1 + λ_2 + λ_3` | 0.9152 |

K-means + silhouette on the PCA-whitened scores
(`k ∈ {2, 3, 4, 5}`):

| `k` | silhouette `s(k)` | inertia |
|----:|------------------:|--------:|
|   2 |            +0.356 |  747.13 |
|   3 |            +0.465 |  537.79 |
|   4 |            +0.563 |  373.48 |
|   5 |            +0.642 |  240.18 |

`k* = 5` (the silhouette is monotone on this grid). Cluster
composition at `k* = 5`:

| Cluster | size | composition (count by adapter)             | dominant class    |
|--------:|-----:|--------------------------------------------|-------------------|
| 0       |   38 | ECASystem 30, KauffmanNetwork 8            | `ECASystem`       |
| 1       |   77 | KauffmanNetwork 2, PeriodicCycle 45, SimpleAutomaton 30 | `PeriodicCycle` |
| 2       |   34 | KauffmanNetwork 4, SimpleAutomaton 30      | `SimpleAutomaton` |
| 3       |   66 | ECASystem 38, KauffmanNetwork 28           | `ECASystem`       |
| 4       |   32 | KauffmanNetwork 32                         | `KauffmanNetwork` |

Four of the five clusters are **dominated** (more than 50% of
their members belong to a single adapter class). One cluster
(cluster 4) is *purely* one adapter class. Cluster 1 is the
only one that mixes more than two adapter classes; cluster 3 is
borderline between `ECASystem` and `KauffmanNetwork`.

### Conditional correlations (Simpson's-paradox check)

Selected pairs where the within-cluster or within-class
correlation differs from the global value by more than `0.30`:

- `closure–persistence`: global `−0.61`. Within `KauffmanNetwork`
  alone the correlation is `−0.07`; within `SimpleAutomaton`
  alone it is `−1.00`. The global moderate-negative correlation
  is *not* a within-substrate property — it is a between-substrate
  contrast.
- `memory–constraint`: global `−0.52`. Within cluster 3 the
  correlation is `−0.68`; within cluster 4 it is `−0.14`.
- `closure–constraint`: global `+0.04`. Within cluster 1 the
  correlation is `−1.00`; within cluster 0 it is `+0.40`.

The global correlation table from `v0.7.0a0` already showed all
six pairs below the falsification threshold of `|r| < 0.7`, and
that result is preserved on the `v0.7.2a0` extended sample. What
the conditional analysis adds is that **the magnitudes of the
global correlations are partly artefacts of the substrate
mixture**: the four adapter classes occupy different parts of
the 4-D cube, and several of the global pair-correlations would
shrink (in absolute value) if the analysis were run within a
single adapter class.

For at least three of the six pair-correlations, `|r_global -
r_within_cluster| > 0.30` for two or more of the five clusters;
per Decision 3, this raises the **Simpson's-paradox health
flag**.

The full per-cluster and per-adapter-class correlation tables
are in `docs/benchmarks/atlas_geometry_v0.7.2a0.json`. The
pretty-printed log is at
`docs/benchmarks/atlas_geometry_v0.7.2a0.log.txt`. The PCA scree
plus the PC1/PC2 biplot (with axis loadings overlaid and the
pre-registered `λ_1 = 0.70` reference line drawn on the scree)
is at `docs/benchmarks/atlas_geometry_v0.7.2a0.png`.

---

## Verdict

The pre-registered outcome bands (Decision 3 + "Predicted
outcomes" section) are evaluated against the indicators above.

**Outcome A — Level 2 reinforced.** Requires `λ_1 ≥ 0.70` *or*
(`λ_1 + λ_2 ≥ 0.85` *and* `s(k*) ≥ 0.25` *with cross-adapter
clusters*). Observed: `λ_1 = 0.47` (no), `λ_1 + λ_2 = 0.81` (no),
clusters are **not** cross-adapter (4 of 5 are dominated by one
adapter class). **Outcome A is rejected.**

**Outcome C — Level 3 suspected.** Requires `λ_1 < 0.40` *and*
`λ_1 + λ_2 < 0.65` *and* `k*` clusters that correlate with
adapter classes. Observed: `λ_1 = 0.47` (no), `λ_1 + λ_2 = 0.81`
(no), clusters do correlate with adapter classes (yes).
**Outcome C is rejected on PCA grounds**, even though its
clustering condition is met.

**Outcome B — Inconclusive.** Requires `λ_1 ∈ [0.40, 0.70)`
*and* `λ_1 + λ_2 ∈ [0.65, 0.85)` *and* `s(k*) < 0.25`. Observed:
`λ_1 = 0.47` (yes), `λ_1 + λ_2 = 0.81` (yes), `s(k*) = 0.64`
(no — clearly above 0.25). Outcome B's PCA clauses match;
its silhouette clause does **not**.

The data therefore lands in a **gap** the pre-registration did
not anticipate: PCA in the inconclusive band, silhouette
strongly above the inconclusive ceiling, but with the strong
clustering structure aligned to substrate (adapter class)
rather than to autonomy.

The honest verdict is therefore:

> **Inconclusive on the level question (PCA reading), with a
> Level-3-suggestive overlay (clustering reading).**

Specifically:

1. **PCA-only verdict: inconclusive.** The 4-D autonomy cloud is
   neither effectively one-dimensional (`λ_1 = 0.47 < 0.70`) nor
   effectively two-dimensional (`λ_1 + λ_2 = 0.81 < 0.85`). It
   carries non-trivial structure on at least three of its four
   PCA components; the fourth still accounts for `8.5%` of total
   variance. Per Decision 3, this PCA pattern alone does not
   support Level 2 and does not justify a Level-3 declaration
   either.

2. **Clustering overlay: Level-3-suggestive but
   non-decisive.** The silhouette is clearly high
   (`s(k* = 5) = 0.64`), and 4 of the 5 clusters are dominated
   by a single adapter class. Per Decision 3, when clusters
   align with adapter classes the clustering reflects the *zoo's
   structure*, not the autonomy structure. **Cluster strength
   without cross-adapter mixing therefore does not constitute
   evidence for Level 2; if anything it is mild evidence
   against**, in the sense that "the four metrics behave
   differently on different substrates" is the kind of pattern
   Level 3 predicts and Level 2 does not.

3. **Simpson's-paradox flag raised.** Several pairwise global
   correlations are partly artefacts of the substrate
   composition of the zoo. The flag is *not* a level-question
   decision (per Decision 3 it is a health flag), but it
   reinforces the overlay above: the four metrics interact with
   *each other* differently inside different adapter classes.
   This is, again, the pattern Level 3 expects.

4. **Conditional on non-degeneracy.** The verdict is conditional
   on the ECA / Kauffman dropout pattern. The 39% dropout rate
   shows the metric set is not currently defined on a substantial
   slice of the structural zoo, and that slice is not random
   across substrates. A future iteration that closes the
   degenerate zone might shift the indicators non-trivially.

The structural-geometry analysis therefore **does not** rule out
Level 2 — it cannot, by construction (see "What this cycle is
*not*"). It **does** weaken the structural-side prior on
Level 2 enough to elevate Level 3 from "considered and rejected
in v0.7.0a0" to "consistent with the cluster geometry of the
extended zoo, awaiting behavioural validation in v0.9.0".

The package's external behaviour does **not** change. The four
metrics still ship, still measure what their docstrings say,
and still preserve their pairwise `|r| < 0.7` falsification
result. What changes is the wording in `docs/PBA.md` and
`docs/PBA.es.md`: the framing moves from "Level 2 plausible"
to "Level 2 plausible **on the structural geometry, but** the
cluster overlay is Level-3-suggestive on the same data; the
question is now genuinely under-determined and is pushed to
v0.9.0".

### Where the verdict goes next

- `v0.7.2a0` (this cycle): documentation-only update. No new
  metric, no API change.
- `v0.9.0`: behavioural validation. The atlas analysis is
  re-run, this time on systems whose autonomy is *known
  externally* (LLM transcripts, RAI questionnaires).
  Cross-tradition agreement at that point is what would
  finally arbitrate Level 2 vs Level 3.

### Deviations from the pre-registration

- **Decision 1 (sample size).** Pre-registration text said
  "typically from 5 to 20"; final implementation used
  `n_seeds = 30`. The pre-registered floor was on `n_valid`, not
  `n_seeds`; `n_seeds = 30` is the smallest grid multiplier that
  cleared the 200 floor with margin under the observed ~60%
  retention rate. This is a benign deviation; recorded for
  transparency.
- **Decision 3 (verdict bands).** The data fell in a gap between
  the three pre-registered outcomes (PCA in Outcome-B band,
  silhouette in Outcome-A/C band). Pre-registration did not
  anticipate this combination. The verdict text above resolves
  the gap conservatively, treating PCA as the primary technique
  (per Decision 2's "numerical primary, visual secondary")
  and treating clustering's substrate-alignment as a
  Level-3-suggestive overlay rather than a Level-3 declaration.
  Documented here so future iterations can revise the bands if
  the same combination recurs.
- No deviations on Decisions 2, 4, or 5.

*End of v0.7.2a0 cycle. Locked decisions remain read-only;
this implementation report and verdict close the cycle.*

---

## v0.8.0a0 follow-up — five-axis geometry (atlas as a mosaic)

**Status**: implementation report. Closes Step 7 of the
Session B plan pre-registered for the `v0.8.0a0` release cycle
(see commits `4c5ab1d`, `8e66c82`, `eefce9d` and the entry in
`CHANGELOG.md` for the same release).

The pre-registered Step 7 read, in plain terms, *"rerun the
PCA + clustering + silhouette analysis above on the new
five-axis benchmark and report the verdict"*. That instruction
assumed the five-axis benchmark would produce a five-dimensional
point cloud whose geometry could be analysed with the same
machinery as the four-axis cloud of `v0.7.2a0`.

The benchmark produced a different reality. This section
documents that reality, why it is the **honest** outcome of
Step 7, and what it implies for the level question.

### The empirical fact

The full five-axis sweep ships in
`docs/benchmarks/v0.8.0a0.{csv,log.txt}`. After the standard
quality filter, the snapshot contains **645 measured systems**.
Of those, the count of systems with **all five axes
simultaneously defined** is

```
n_valid_full = 0  /  645
```

Zero. Not "small", not "underpowered" — structurally **none**.
Every row in the benchmark CSV has at least one axis missing.

### Why none, and why the pattern is structural rather than
accidental

Each shipped axis is **gated by an adapter capability**. The
gating is documented in `core.AutonomySystem` and reproduced
here for the record:

- `closure` and `memory` need only `get_state_history` /
  `get_env_history`. Every adapter ships these.
- `constraint_closure` requires `get_causal_graph`, returning
  a square boolean adjacency matrix.
- `persistence` requires `replay_from_perturbation`, returning
  the post-perturbation focal slice.
- `coherence` requires `get_declared_executed`, returning a
  parallel `(declared, executed)` pair.

The four shipped non-`PromisedCycle` adapters (`SimpleAutomaton`,
`ECASystem`, `BooleanNetwork`, `CSVTrajectory`) all expose the
first three families above and therefore fill the four `v0.7.2a0`
axes; **none of them ship a declarative layer**, so the
`coherence` column is always `None` on those rows. Conversely,
`PromisedCycle` was designed for the coherence axis and has no
exogenous causal graph to expose, so its `constraint_closure`
column is always `None`.

The intersection of "rows with `coherence` defined" and "rows
with `constraint_closure` defined" is therefore **empty by
construction**, not by chance. No additional sampling, no larger
zoo, and no different seed setting will fix it. The hole is a
property of which adapter classes ship in v0.8.0a0, not of
which subset of them was actually run.

### Why this defeats Step 7 in its pre-registered form

PCA / k-means / silhouette all need a **rectangular complete
matrix**: rows are observations, columns are axes, every cell
must contain a number. Standard practice (Jolliffe 2002,
Rousseeuw 1987) assumes complete-case input, with imputation
flagged as a separate methodological commitment.

The five-axis dataset has **no complete row**. There is therefore
no five-dimensional point cloud over which to run PCA. There is
no `λ_1` to compare with the pre-registered `λ_1 ≥ 0.65` floor
(itself adapted from the `v0.7.2a0` cycle's `λ_1 ≥ 0.70`). There
is no five-dimensional silhouette score to compute.

Three options were considered. They are recorded here in line
with the deviation-policy of Decision 2 above.

1. **Run PCA on the union with imputation.** Replace each
   missing cell with a column-mean, a regression fit, or a
   multiple-imputation draw. Rejected: imputing systematically
   missing axes (every PromisedCycle row imputes a
   `constraint_closure`, every ECA row imputes a `coherence`)
   propagates the imputation choice into the principal
   components and generates a low-dimensional artefact whose
   slope is determined by the imputer, not the data. The
   resulting `λ_1` would be uninterpretable in level-question
   terms.
2. **Run PCA per sub-cluster (per-adapter four-axis
   geometries).** For each adapter class with four valid axes,
   fit a four-dimensional PCA. This is technically sound but is
   **not Step 7** — Step 7 asked about the global five-axis
   cloud. Running it per sub-cluster reports four separate
   four-dimensional geometries, which is interesting but is a
   **different question**: it tests whether the four-axis
   structure is stable across substrates rather than whether
   the five-axis structure is one object. Recorded for v0.8.0a1
   or later as a follow-up; not promoted to Step 7's
   replacement.
3. **Report the structural infeasibility as the verdict of
   Step 7.** Adopted. The five-axis benchmark *did* answer
   Step 7's underlying question — "is the five-axis cloud one
   object?" — but with a stronger answer than PCA could give:
   *the cloud does not exist as a single object on the current
   adapter zoo*. That is a Level-3-style answer in the
   pre-registered ontology of `## What this cycle is *not*`
   (read across cycles): the four / five axes do not co-inhabit
   a shared coordinate system because no system instantiates
   all of them at once.

### What the verdict actually is

Combining the result of `v0.7.2a0` (Level 2 plausible on
structural geometry, Level-3-suggestive on the cluster overlay,
inconclusive overall) with the new structural infeasibility:

- The atlas of autonomy that the package ships is best read,
  on the current zoo, as a **mosaic / archipelago**: a small
  number of overlapping four-axis sub-charts that share most
  axes but never share all five.
- The Level 2 reading ("one multidimensional object viewed
  through several coordinate systems") becomes **harder** to
  defend purely on structural data: a single object should
  have a consistent rank, a consistent set of coordinates, and
  in particular *some* substrate where all coordinates are
  observable. None of the substrates in v0.8.0a0 is that
  substrate.
- The Level 3 reading ("several phenomena bundled under a
  shared label") becomes **easier** to defend, in the soft
  sense the v0.7.2a0 verdict already opened: the four / five
  metrics behave coherently inside their respective sub-charts
  and do not stitch into a single object across them.
- Crucially, the prediction window is **not collapsed**: it is
  pushed forward. The `v0.9.0` adapter step (LLM transcripts
  with `get_declared_executed` and an explicit causal graph
  exported alongside) is now the natural candidate for a
  substrate that closes the five-axis hole. If such a substrate
  exists and produces a non-degenerate five-axis cloud, PCA
  Step 7 can be re-run there in its pre-registered form. If it
  does not, the mosaic reading hardens.

### Independent corroboration from the diagnostic audits

Two diagnostics were run alongside Step 7 (commits `8e66c82`
and `eefce9d`) and bear on the same level question:

- **Stratified audit (correlational).** The headline pairwise
  finding `r(closure, coherence) = +0.96` on the 240
  PromisedCycle rows was decomposed by configuration. The
  per-cell correlations decay smoothly with `p_noise`
  (`+0.93 → −0.18`), and the scatter shows five `p_noise`
  islands in the (closure, coherence) plane. The visual
  signature is a textbook Simpson's paradox: a between-cluster
  correlation that disappears within clusters.
- **Causal experiment (interventional).** The PromisedCycle
  adapter was extended with an independent declared-channel
  noise `p_env`, then swept across the (`p_noise`, `p_env`)
  grid. The headline correlation falls from `+0.97` (single
  driver) to `+0.48` (two drivers); within fixed `p_noise`
  cells it oscillates around zero; `r(coherence, p_env) =
  +0.0007` confirms that Theil's U is invariant to declarative-
  side perturbations, exactly as `docs/CBA.md` predicted.

Neither diagnostic is a substitute for the pre-registered
five-axis PCA. Both reinforce the qualitative reading recorded
above: cross-axis correlations that look strong on the global
five-axis dataset are partly substrate-induced, partly
adapter-degeneracy-induced, and not partly five-dimensional
intrinsic structure — because there is no five-dimensional
intrinsic structure to point to in this release.

### Deviations from Step 7's pre-registration

- **Technique not run.** PCA / k-means / silhouette were not
  computed on the five-axis matrix. Justification: the matrix
  has no complete row (`n_valid_full = 0/645`). The relevant
  pre-registered escape clause is the deviation policy of
  Decision 2: "Any deviation from [the locked decisions] in
  the implementation phase has to be flagged explicitly and
  justified in the verdict section". This is the explicit
  flag.
- **Threshold not applied.** No `λ_1` measurement exists; the
  `λ_1 ≥ 0.65` floor is therefore not a pass/fail marker on
  this cycle. The interpretive band-table from Decision 3 is
  inapplicable. This deviation is benign in the sense that
  Step 7 was *prepared* to declare a verdict if the data
  permitted, and the data did not permit; it was *not*
  prepared for the structural-infeasibility outcome, which
  predates any threshold check.
- **Substitute analysis declined.** Two substitute analyses
  (per-adapter four-axis PCA, imputed-matrix five-axis PCA)
  were considered and rejected for the reasons recorded
  above. They are appropriate research-grade follow-ups for
  a future release, not appropriate substitutes for Step 7
  itself.

*End of v0.8.0a0 follow-up. Step 7 closes here, with the
verdict that "no five-dimensional cloud" is the empirical
answer to the geometric question the cycle posed. The
package's external behaviour is unchanged; the documentation
moves from "five-axis atlas to be analysed geometrically" to
"five-axis mosaic, with the geometry of each four-axis
sub-chart available individually and the unified five-axis
geometry deferred to whichever future adapter closes the
hole".*
