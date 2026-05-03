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
