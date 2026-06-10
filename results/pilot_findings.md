# Phase 1 findings -- MegaAcceptability v2 reanalysis

Structured outputs only; interpretation and the PLAN.md §4 go/no-go call are pm-node work (Phase 2). All numbers trace to `results/pilot_*` and `results/pilot_runs/` under the manifest below.

## Provenance

- Dataset: MegaAcceptability v2 (megaattitude.io), file `data/mega-acceptability-v2/mega-acceptability-v2.tsv`
- SHA-256: `81ae0810dd7b2af230de980ff8acb0675727ae194ac82e6caabacdeb744955e4`
- Judgments: 375,000 raw; 373,440 after dropping 10 NA and non-native raters (native filter effect is negligible: see DECISIONS).
- Seed 7; git `cbe53738bb`; versions {'python': '3.11.4', 'numpy': '2.1.3', 'scikit_learn': '1.6.1', 'pandas': '2.3.3'}.
- Pre-registration: DECISIONS.md 2026-06-10. Primary slice = past tense, native, participant z-scores, cell = mean z, dichotomize z-bar > 0.

## Slice composition

- Full dataset (native, non-NA): 1007 verbs, 50 frames.
- primary_past_z0: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_past_z025: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_past_raw4: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_past_raw45: 1000 verbs x 49 frames (slice contained 1000 verbs; 0 excluded for partial missing cells; 7 absent from slice entirely). Frames absent from this slice: ['S, I V'].
- sens_alltense_z0: 1000 verbs x 50 frames (slice contained 1007 verbs; 7 excluded for partial missing cells; 0 absent from slice entirely).

## Model comparison by arm (Model A low-rank vs Model B network)

`diff_mean` > 0 means the network predicts held-out cells better; `network_better` is its sign. Grid arms use fixed rank 1 for a like-for-like verdict; the final row is the primary arm at its best CV rank (5).

| arm | n_verbs | base_rate | rankA | logloss_lowrank | logloss_network | diff_mean | diff_se | network_better | significant_2se | eig_dominance | eig_band | edge_density |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary_past_z0 | 1000 | 0.4122 | 1 | 0.537501 | 0.388961 | 0.148541 | 0.003874 | True | True | 1.5224 | 1.5-3 (intermediate) | 0.2517 |
| sens_past_z025 | 1000 | 0.3198 | 1 | 0.493482 | 0.344344 | 0.149137 | 0.003749 | True | True | 1.5581 | 1.5-3 (intermediate) | 0.227 |
| sens_past_raw4 | 1000 | 0.3113 | 1 | 0.500986 | 0.363141 | 0.137845 | 0.003709 | True | True | 1.5135 | 1.5-3 (intermediate) | 0.2194 |
| sens_past_raw45 | 1000 | 0.2282 | 1 | 0.435317 | 0.305896 | 0.129422 | 0.00358 | True | True | 1.4613 | <1.5 (no dominance) | 0.1879 |
| sens_alltense_z0 | 1000 | 0.3562 | 1 | 0.543716 | 0.423861 | 0.119855 | 0.003596 | True | True | 1.4648 | <1.5 (no dominance) | 0.2384 |
| primary_past_z0@bestrank | 1000 | 0.4122 | 5 | 0.448223 | 0.388961 | 0.059262 | 0.002662 | True | True | 1.5224 | 1.5-3 (intermediate) | 0.2526 |

- Pre-registered robustness criterion (DECISIONS 4): verdict sign invariant across grid = **True**; eigen-dominance band invariant = **False**. If either is False, threshold-dependence is itself the result (no arm promoted).
- Excluded verbs (any missing cell in slice) per arm: primary_past_z0=0, sens_past_z025=0, sens_past_raw4=0, sens_past_raw45=0, sens_alltense_z0=7.

## Model A rank sweep (primary arm)

Residual structure check: does held-out prediction improve past one latent dimension? (Calibration note, DECISIONS 2026-06-10.)

| rank | logloss_lowrank | logloss_network | diff_mean | diff_se |
|---|---|---|---|---|
| 1 | 0.537501 | 0.38896 | 0.148541 | 0.003874 |
| 2 | 0.480097 | 0.388959 | 0.091139 | 0.003188 |
| 3 | 0.472137 | 0.388961 | 0.083176 | 0.003019 |
| 4 | 0.460293 | 0.388959 | 0.071334 | 0.002841 |
| 5 | 0.448223 | 0.388961 | 0.059262 | 0.002662 |

## Eigenvalue spectra (primary arm)

Pre-reg 5 continuous check + residual-structure spectrum. First 10 eigenvalues of the cell correlation matrix.

- Undichotomized z-bar matrix: 12.869, 9.585, 3.632, 2.415, 1.995, 1.479, 0.959, 0.918, 0.859, 0.708
- Dichotomized 0/1 matrix:    10.671, 7.009, 3.082, 1.880, 1.830, 1.389, 1.039, 0.922, 0.892, 0.857

## Projectibility (primary arm)

- Frames with projectibility > 0.01: 48 of 49 (PLAN §4 T2 reference is ≥ 10; formal significance/bootstrap deferred to pm-node). Full ranking: `results/pilot_projectibility.csv`.
- Top frames: NP V that S (0.058); NP V that S[+future] (0.054); NP V to NP that S[+future] (0.050); NP V to NP whether S[+future] (0.049); NP be V about whether S (0.048); NP V whichNP S (0.047); NP be V that S[+future] (0.047); NP V whether to VP (0.047)
- Bottom frames: NP V NP VP (0.010); NP V NP that S[-tense] (0.011); NP V NP whichNP S (0.012); NP V NP (0.012); NP V NP whether S[+future] (0.015)

## Per-verb misfit (primary arm)

Standardized network misfit; full ranking in `results/pilot_misfit.csv`.
- Highest-misfit verbs: admonish (2.72); counsel (2.14); quote (2.07); trouble (1.98); rebuke (1.96); offer (1.76); compliment (1.55); relish (1.53); hanker (1.52); delude (1.51); prejudge (1.49); fight (1.49); pressure (1.45); confuse (1.34); enlighten (1.34)

## Frame flags

No frame has a primary-arm base rate outside [0.02, 0.98].
