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
- **gpt**: low-rank PCA rank 3 held-out MSE 0.3001 vs GGM MSE 0.2978 -> ggm; continuous eigen-dominance 2.99, GGM edge density 0.264.

## RQ2 -- projectibility (decoration check; PLAN T2 >=10)
- **fable**: 24/24 diagnostics project > 0. See phase3_fig_projectibility.png.
- **gpt**: 21/24 diagnostics project > 0. See phase3_fig_projectibility.png.

## RQ3 -- lexeme misfit (boundary set; TYPE-M CAVEAT)
**Underpowered: 24 judgment items < the pre-registered 40-item floor. The ranking is reported; individual-lexeme misfit claims are not made (Type-M: even a high-ranking boundary item is a noisy estimate).** Corpus columns would lift p toward ~42.
- **fable**: boundary-in-top-decile hit-rate 0.231 (3 of 13): ['worth', 'less', 'such']. Top-misfit lexemes: ['chicky', 'now', 'long', 'taliban', 'kyle', 'thenceforth', 'second', 'beyond'].
- **gpt**: boundary-in-top-decile hit-rate 0.154 (2 of 13): ['worth', 'more']. Top-misfit lexemes: ['next', 'comedy', 'beyond', 'heavenward', 'whatever', 'ploppy', 'following', 'somewhat'].

## Lexeme communities + P1 (more/less)
Unsupervised k-means of lexeme profiles; strata used only to READ clusters (F3), never to fit them. P1 (pre-registered): Reynolds predicts the more/less profiles cluster with the determinative community.
- **fable**: ARI(clusters vs a-priori strata) = 0.303; cluster->dominant-stratum {'2': 'preposition', '3': 'adjective', '0': 'preposition', '1': 'adjective', '4': 'determinative'}. P1: more in determinative cluster = True, less = True (more->determinative, less->determinative).
- **gpt**: ARI(clusters vs a-priori strata) = 0.325; cluster->dominant-stratum {'2': 'preposition', '4': 'adjective', '1': 'adjective', '3': 'determinative', '0': 'preposition'}. P1: more in determinative cluster = True, less = True (more->determinative, less->determinative).

## Posterior-predictive checks
- **fable**: observed eigen-dominance 3.46 (sim 95% [5.22, 6.05]); observed edge density 0.272 (sim [0.236, 0.312]).
- **gpt**: observed eigen-dominance 3.47 (sim 95% [4.58, 5.37]); observed edge density 0.236 (sim [0.176, 0.239]).

## Figures
- phase3_fig_verdict.png (RQ1 verdict-invariance across arms)
- phase3_fig_misfit.png (RQ3 lexeme misfit, boundary marked)
- phase3_fig_projectibility.png (RQ2)

## Estimand architecture
PPI-corrected per-item acceptance rates (EB-shrunk, CIs) in phase3_headline.json `ppi_item_rates`. The structural verdict is fit on the judge matrix with the instrument characterization (stage 2a) and the arms behind it.
