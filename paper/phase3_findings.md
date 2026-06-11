# Phase 3 findings (PROVISIONAL -- pending external-panel ingestion)
Numbers + figures only; the reading (RQ1 verdict, RQ3 ranking, RQ4 mapping, more/less) is pm-node work. Gold anchor = Brett's 600 (n=1 rater); the file is provisional until the colleague panel lands (human-ceiling, gold-6 external test, panel-calibrated arm).
- Grid: 535 lexemes x 24 judgment diagnostics. git f81b8019.
## RQ1 -- structure (binary, PLAN §4 thresholds as written)
CV diff sign: + network better, - low-rank better; |diff| > 2*SE = separated. Eigen-dominance > 3 reflective / < 3 network.

**fable** (missing 23):
| arm | rank | CV diff | SE units | CV call | eig-dom | struct call | edge |
|---|---|---|---|---|---|---|---|
| primary_z0 | 5 | +0.0355 | +12.8 | network | 3.46 | reflective(>3) | 0.272 |
| ge5 | 4 | +0.0375 | +15.3 | network | 3.52 | reflective(>3) | 0.149 |
| ge4 | 5 | +0.0411 | +15.8 | network | 3.62 | reflective(>3) | 0.207 |
| morph_out | 5 | +0.0366 | +14.2 | network | 2.89 | network(<3) | 0.284 |
| core96 | 4 | +0.0355 | +12.8 | network | 3.34 | reflective(>3) | 0.275 |
| calibrated | 5 | +0.0355 | +12.8 | network | 3.46 | reflective(>3) | 0.272 |

**gpt** (missing 0):
| arm | rank | CV diff | SE units | CV call | eig-dom | struct call | edge |
|---|---|---|---|---|---|---|---|
| primary_z0 | 5 | +0.0244 | +9.9 | network | 3.47 | reflective(>3) | 0.236 |
| ge5 | 4 | +0.0243 | +11.8 | network | 3.26 | reflective(>3) | 0.196 |
| ge4 | 5 | +0.0249 | +10.4 | network | 3.28 | reflective(>3) | 0.243 |
| morph_out | 4 | +0.0228 | +9.1 | network | 2.92 | network(<3) | 0.216 |
| core96 | 4 | +0.0249 | +9.8 | network | 3.53 | reflective(>3) | 0.232 |
| calibrated | 5 | +0.0244 | +9.9 | network | 3.47 | reflective(>3) | 0.236 |

## RQ1 (continuous, CO-EQUAL) -- GGM vs low-rank factor on z-scores
The gold-6 compression (the only region of real instrument nonlinearity) sits ABOVE every binary cut, so it is minimal for the binary models and carried entirely by this continuous check.
- **fable**: low-rank PCA rank 5 held-out MSE 0.2783 vs GGM MSE 0.2693 -> ggm; continuous eigen-dominance 3.21, GGM edge density 0.297.
- **gpt**: low-rank PCA rank 3 held-out MSE 0.3001 vs GGM MSE 0.2978 -> ggm; continuous eigen-dominance 2.99, GGM edge density 0.264. THIN margin (0.2978 vs 0.3001): report as directionally consistent with the binary verdict, NOT as independent confirmation.

## RQ2 -- projectibility (decoration check; PLAN T2 >=10)
- **fable**: 24/24 diagnostics project > 0. See phase3_fig_projectibility.png.
- **gpt**: 21/24 diagnostics project > 0. The three non-projecting items all sit marginally below zero -- *postpositive* (-0.003), *gerund_gap_complement* (-0.0002), *stranding* (-0.0002); *predeterminer_position* is on the line (~0, counted in the 21). At-or-near-zero, not strongly negative. See phase3_fig_projectibility.png.

## RQ3 -- lexeme misfit (boundary set; TYPE-M CAVEAT)
**Underpowered: 24 judgment items < the pre-registered 40-item floor. The ranking is reported; individual-lexeme misfit claims are not made (Type-M: even a high-ranking boundary item is a noisy estimate).** Corpus columns would lift p toward ~42.
- **fable**: boundary-in-top-decile hit-rate 0.231 (3 of 13): ['worth', 'less', 'such']. Top-misfit lexemes: ['chicky', 'now', 'long', 'taliban', 'kyle', 'thenceforth', 'second', 'beyond'].
- **gpt**: boundary-in-top-decile hit-rate 0.154 (2 of 13): ['worth', 'more']. Top-misfit lexemes: ['next', 'comedy', 'beyond', 'heavenward', 'whatever', 'ploppy', 'following', 'somewhat'].

## Lexeme communities + P1 (more/less)
Unsupervised k-means of lexeme profiles; strata used only to READ clusters (F3), never to fit them. P1 (pre-registered): Reynolds predicts the more/less profiles cluster with the determinative community.
- **fable**: ARI(clusters vs a-priori strata) = 0.303; cluster->dominant-stratum {'2': 'preposition', '3': 'adjective', '0': 'preposition', '1': 'adjective', '4': 'determinative'}. P1: more in determinative cluster = True, less = True (more->determinative, less->determinative).
- **gpt**: ARI(clusters vs a-priori strata) = 0.325; cluster->dominant-stratum {'2': 'preposition', '4': 'adjective', '1': 'adjective', '3': 'determinative', '0': 'preposition'}. P1: more in determinative cluster = True, less = True (more->determinative, less->determinative).

**Preposition split (both judges; the two preposition-dominant clusters, 0 and 2).** The split tracks SEMANTICS, not sampling scope -- both clusters mix core96/extended:
- **cluster 0 = locative/spatial**: *above, below, between, under, over, inside, outside, beneath, underneath, across, around, beyond, through, behind, past, in, on, up, down* ... (fable n=66, scope 48 core / 18 extended; gpt n=61, 47/14). Core-heavy.
- **cluster 2 = grammatical + temporal + deverbal**: *of, to, by, for, with, as, at, from, into, onto, upon, since, until, after, against, throughout, without* + participial preps *according, allowing, barring, excepting, including, notwithstanding* (fable n=61, 33/28; gpt n=56, 29/27). Scope-balanced.
The preposition category is recoverable but internally structured (spatial vs grammatical), consistent across judges -- this is the ARI~0.3 texture (categories real, with sub-structure). [Per-lexeme cluster labels are not stored in the JSON; regenerable via the seed-26 k-means in src/verdict_null-style reconstruction.]

## Posterior-predictive checks
Reading (pm): the reflective fit OVER-PREDICTS its own eigenvalue signature -- observed dominance falls BELOW the simulated interval for both judges (the common-cause model cannot generate the observed spectrum) -- while the network reproduces edge density. This breaks the dominance-threshold straddle cleanly toward network.
- **fable**: observed eigen-dominance 3.46 BELOW sim 95% [5.22, 6.05]; observed edge density 0.272 INSIDE sim [0.236, 0.312].
- **gpt**: observed eigen-dominance 3.47 BELOW sim 95% [4.58, 5.37]; observed edge density 0.236 AT THE UPPER BOUND of sim [0.176, 0.239] (report as "at the upper bound," not "inside").

## Figures
- phase3_fig_verdict.png (RQ1 verdict-invariance across arms; arm labels humanized 2026-06-11)
- phase3_fig_misfit.png (RQ3 lexeme misfit, boundary marked)
- phase3_fig_projectibility.png (RQ2)
- phase3_fig_verdict_null.png (EXPLORATORY structureless null for the verdict)

## Estimand architecture
PPI-corrected per-item acceptance rates (EB-shrunk, CIs) in phase3_headline.json `ppi_item_rates`. The structural verdict is fit on the judge matrix with the instrument characterization (stage 2a) and the arms behind it.

## Emergent worst-fits (EXPLORATORY -- for a caveated Discussion table, not the figure)
Decision 2026-06-11: the misfit figure stays the pre-registered boundary test (non-circular). The data-driven worst-fitting lexemes are reported here, REAL WORDS ONLY -- blind-stratum nonce/proper-noun items (fable: chicky, taliban, kyle; gpt: comedy, ploppy) are excluded from naming. TYPE-M CAVEAT travels with the table: 24 judgment items < the 40-item floor, so per-lexeme misfit is a noisy estimate; this is descriptive, not a validated ranking. Source: results/phase3_headline.json `_misfit` (network misfit z), git f81b8019.
- **fable** real-word top misfits: *now* +3.54, *long* +3.39, *thenceforth* +2.94, *second* +2.92, *beyond* +2.53.
- **gpt** real-word top misfits: *next* +3.56, *beyond* +2.75, *heavenward* +2.66, *whatever* +2.55, *following* +2.30, *somewhat* +2.20.
- Cross-judge: *beyond* is the worst real-word misfit common to both judges. The set splits into adverb/preposition straddlers (*now, thenceforth, heavenward, beyond, following*) and determinative/degree straddlers (*next, whatever, somewhat*) -- a data-driven echo of the boundary phenomena, surfaced from OUTSIDE the pre-registered boundary set.
- ANTI-CROFT note (for §7): the detector, pointed at the A/P/Det boundary we instrumented, surfaced a DIFFERENT frayed edge (adverb/preposition straddlers) than the one pre-registered -- from a stratum sampled with NO category labels. That the data find a real boundary the analysts did not ask about is the strongest anti-opportunism (anti-Croft) evidence in the paper. Two readings must travel together: partly instrument coverage (no adverb-targeted items, so adverb-ish lexemes misfit everything) and partly real boundary phenomena.

## Structureless null for the verdict (EXPLORATORY robustness -- src/verdict_null.py; NOT pre-registered, see DECISIONS 2026-06-11)
Gelman negative control: destroy the grid's cross-diagnostic structure (column permutation preserving each diagnostic's acceptance rate, plus random Bernoulli matched to rates), re-run the identical headline pipeline, report the observed verdict as EXCESS over the null. Primary arm; reflective rank fixed at observed best for null draws (conservative for "network wins"). All three signatures sit at the 100th percentile of the shuffle null, both judges (the random-Bernoulli null agrees throughout):
| stat | fable obs | fable shuffle-null [95%] | gpt obs | gpt shuffle-null [95%] |
|---|---|---|---|---|
| eigen-dominance | 3.46 | 1.05 [1.01, 1.12] | 3.47 | 1.05 [1.01, 1.12] |
| CV gap (SE units) | 10.3 | 2.25 [0.23, 4.26] | 7.9 | 2.46 [0.49, 4.62] |
| edge density | 0.272 | 0.005 [0.00, 0.014] | 0.236 | 0.007 [0.00, 0.018] |
- **eigen-dominance** obs ~3.46 vs null ~1.05: the dominance is REAL shared variance, not an artifact of base rates/sparsity/the binary cut; the >3 threshold is not mis-calibrated (noise reads ~1). The network-wins-WITH-real-dominance tension is genuine and EARNS the van der Maas reading.
- **CV gap**: the null is NOT centred at 0 -- it sits ~2.3 SE (the network's flexibility buys a baseline edge even on noise, via the CV scaffold's documented predictor-imputation). Observed (10.3/7.9) is 4-5x the null's 97.5%ile (~4.3/4.6), so report the network advantage as EXCESS over ~2.3 SE -- emphatic, real, and it pre-empts the "scaffold favours the network" objection.
- **edge density** obs ~27%/24% vs the lasso's false-edge floor ~0.6%: the network's edges are real, not lasso noise.
Figure: phase3_fig_verdict_null.png.
