# Phase 1 findings -- MegaAcceptability v2 reanalysis

Structured outputs only; interpretation and the PLAN.md §4 go/no-go call are pm-node work (Phase 2). All numbers trace to `results/pilot_*` and `results/pilot_runs/` under the manifest below.

## Provenance

- Dataset: MegaAcceptability v2 (megaattitude.io), file `data/mega-acceptability-v2/mega-acceptability-v2.tsv`
- SHA-256: `81ae0810dd7b2af230de980ff8acb0675727ae194ac82e6caabacdeb744955e4`
- Judgments: 375,000 raw; 373,440 after dropping 10 NA and non-native raters (native filter effect is negligible: see DECISIONS).
- Seed 7; git `22e50277b6`; versions {'python': '3.11.4', 'numpy': '2.1.3', 'scikit_learn': '1.6.1', 'pandas': '2.3.3'}.
- Pre-registration: DECISIONS.md 2026-06-10. Primary slice = past tense, native, participant z-scores, cell = mean z, dichotomize z-bar > 0.

## Slice composition

- Full dataset (native, non-NA): 1007 verbs, 50 frames.
- primary_past_z0: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_past_z025: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_past_raw4: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_past_raw45: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_alltense_z0: 1000 verbs x 50 frames (slice contained 1007 verbs; 7 excluded for partial missing cells; 0 absent from slice entirely).

## Model comparison by arm (Model A low-rank vs Model B network)

`diff_mean` > 0 means the network predicts held-out cells better; `network_better` is its sign. Grid arms use fixed rank 1 for a like-for-like verdict; the final row is the primary arm at its best CV rank (10).

| arm | n_verbs | base_rate | rankA | logloss_lowrank | logloss_network | diff_mean | diff_se | network_better | significant_2se | eig_dominance | eig_band | edge_density |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary_past_z0 | 1000 | 0.4122 | 1 | 0.537501 | 0.38896 | 0.148541 | 0.003874 | True | True | 1.5224 | 1.5-3 (intermediate) | 0.2526 |
| sens_past_z025 | 1000 | 0.3198 | 1 | 0.493482 | 0.344344 | 0.149138 | 0.003749 | True | True | 1.5581 | 1.5-3 (intermediate) | 0.227 |
| sens_past_raw4 | 1000 | 0.3113 | 1 | 0.500986 | 0.363142 | 0.137844 | 0.003709 | True | True | 1.5135 | 1.5-3 (intermediate) | 0.2202 |
| sens_past_raw45 | 1000 | 0.2282 | 1 | 0.435317 | 0.305896 | 0.129422 | 0.00358 | True | True | 1.4613 | <1.5 (no dominance) | 0.1879 |
| sens_alltense_z0 | 1000 | 0.3562 | 1 | 0.543716 | 0.423863 | 0.119854 | 0.003596 | True | True | 1.4648 | <1.5 (no dominance) | 0.2384 |
| primary_past_z0@bestrank | 1000 | 0.4122 | 10 | 0.433388 | 0.38896 | 0.044427 | 0.002399 | True | True | 1.5224 | 1.5-3 (intermediate) | 0.2526 |

- Pre-registered robustness criterion (DECISIONS 4): verdict sign invariant across grid = **True**; eigen-dominance band invariant = **False**. If either is False, threshold-dependence is itself the result (no arm promoted).
- Excluded verbs (any missing cell in slice) per arm: primary_past_z0=0, sens_past_z025=0, sens_past_raw4=0, sens_past_raw45=0, sens_alltense_z0=7.

## Model A rank sweep (primary arm)

Residual structure check: does held-out prediction improve past one latent dimension? (Calibration note, DECISIONS 2026-06-10.)

| rank | n_params_lowrank | logloss_lowrank | logloss_network | diff_mean | diff_se |
|---|---|---|---|---|---|
| 1 | 1098 | 0.537501 | 0.388962 | 0.148539 | 0.003874 |
| 2 | 2147 | 0.480097 | 0.38896 | 0.091137 | 0.003188 |
| 3 | 3196 | 0.472137 | 0.38896 | 0.083177 | 0.003019 |
| 4 | 4245 | 0.460293 | 0.388962 | 0.071331 | 0.002841 |
| 5 | 5294 | 0.448223 | 0.38896 | 0.059263 | 0.002662 |
| 6 | 6343 | 0.441633 | 0.38896 | 0.052673 | 0.002585 |
| 7 | 7392 | 0.445465 | 0.388962 | 0.056503 | 0.002628 |
| 8 | 8441 | 0.438497 | 0.38896 | 0.049537 | 0.00253 |
| 9 | 9490 | 0.437268 | 0.38896 | 0.048308 | 0.002477 |
| 10 | 10539 | 0.433388 | 0.38896 | 0.044428 | 0.002399 |

- Network (primary): n_params = 346 (BIC node fits), held-out log-loss ~ 0.388962. Lowest low-rank rank reaching that log-loss within 1..10: **none in range**. Matched-complexity reading (parsimony at equal prediction) is pm-node work.

## Eigenvalue spectra (primary arm)

Pre-reg 5 continuous check + residual-structure spectrum. First 10 eigenvalues of the cell correlation matrix.

- Undichotomized z-bar matrix: 12.869, 9.585, 3.632, 2.415, 1.995, 1.479, 0.959, 0.918, 0.859, 0.708
- Dichotomized 0/1 matrix:    10.671, 7.009, 3.082, 1.880, 1.830, 1.389, 1.039, 0.922, 0.892, 0.857

## Principal-component loadings (primary arm, continuous z-bar)

Frame loadings on the first two PCs of the continuous z-bar frame correlation matrix (eigenvalues 12.87, 9.58). Sign is arbitrary; no labels (pm-node interprets). Full table: `results/pilot_pc_loadings.csv`.

- PC1 highest: NP be V about NP (+0.188); NP be V about whether S (+0.174); NP be V that S (+0.172); NP be V (+0.168); NP be V that S[+future] (+0.164); NP be V that S[-tense] (+0.161)
- PC1 lowest:  NP V that S[+future] (-0.212); NP V that S (-0.209); NP V whether S[+future] (-0.194); NP V S (-0.191); NP V to NP that S[+future] (-0.190); NP V whether S (-0.190)
- PC2 highest: NP V NP that S[+future] (+0.229); NP V NP whether S[+future] (+0.217); NP V NP whether S (+0.216); NP V NP that S (+0.214); NP be V whichNP to VP (+0.212); NP V NP whichNP S (+0.204)
- PC2 lowest:  NP V (+0.013); NP V VPing (+0.026); NP V to VP[+eventive] (+0.027); NP V NP (+0.039); NP V to VP[-eventive] (+0.040); NP V about NP (+0.059)

## Projectibility (primary arm)

- Frames with projectibility > 0.01 (point estimate): 48 of 49.
- Nonparametric bootstrap over verbs (200 resamples): **49 of 49 frames have a 95% CI lower bound > 0** (PLAN §4 T2 reference is ≥ 10). Per-frame point/SE/CI in `results/pilot_projectibility_bootstrap.csv`.
- Top frames (point; CI_lo): NP V that S 0.058; 0.043; NP V that S[+future] 0.054; 0.041; NP V to NP that S[+future] 0.050; 0.038; NP V to NP whether S[+future] 0.049; 0.037; NP be V about whether S 0.048; 0.037; NP V whichNP S 0.047; 0.030; NP be V that S[+future] 0.047; 0.036; NP V whether to VP 0.047; 0.027
- Bottom frames (point; CI_lo; sig>0): NP V NP VP 0.010; 0.005; True; NP V NP that S[-tense] 0.011; 0.004; True; NP V NP whichNP S 0.012; 0.006; True; NP V NP 0.012; 0.007; True; NP V NP whether S[+future] 0.015; 0.011; True

## Per-verb misfit (primary arm)

Standardized network misfit; full ranking in `results/pilot_misfit.csv`.
- Highest-misfit verbs: admonish (2.72); counsel (2.14); quote (2.07); trouble (1.98); rebuke (1.97); offer (1.76); compliment (1.55); relish (1.53); hanker (1.52); delude (1.51); prejudge (1.49); fight (1.49); pressure (1.45); confuse (1.34); enlighten (1.34)

## Frame flags

No frame has a primary-arm base rate outside [0.02, 0.98].
