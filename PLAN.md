# PLAN.md — Do categorial diagnostics measure anything?

Target venue: *Language*. Working title: *Do categorial diagnostics measure
anything? A psychometric study of English lexical categories.*

This file is the single source of truth for design decisions. Claude Code
(executor) follows it; deviations require a pm-update entry and a reason.
Brett + Claude (chat) = pm node. Decisions made here override conversational
memory on either side.

## 1. Research questions and estimands

RQ1 (structure). For a lexeme × diagnostic acceptability matrix, which
measurement model best characterizes the data: a low-rank reflective model
(diagnostics as items measuring few latent dimensions) or a sparse pairwise
network (diagnostics mutually constraining with no common cause)?

RQ2 (item validity). For each diagnostic: discrimination, dimensional
loading pattern, and projectibility score = improvement in held-out
prediction of the remaining diagnostics when this diagnostic is observed.
A diagnostic that predicts nothing beyond itself is decoration.

RQ3 (person/lexeme misfit). Which lexemes show quantified misfit under the
winning model? Pre-named candidates (boundary set): *worth*, *near*, *fun*,
*like*, *due*, *galore*, *ablaze*, *asleep*, *more*, *less*, *enough*,
*such*, *own*. Prediction: boundary items show top-decile misfit. If they
don't, the informal boundary-item literature is miscalibrated — also a
finding.

RQ4 (theory adjudication). Map results onto named positions:
- discrete-essence tradition → expect clean low-rank, one dominant
  dimension per category, low misfit;
- Croft 2001 (methodological opportunism) → expect fragmentation: no
  stable structure, diagnostics fail to cohere;
- Aarts 2007 (subsective gradience) → expect low-rank with graded scores;
- maintained-cluster view (Reynolds) → expect structured sparse network
  with identifiable communities and high-misfit boundary items.

## 2. Known technical hazard (read before modeling)

Low-rank Ising/pairwise models and multidimensional IRT models are closely
related; in limiting cases they are statistically equivalent (Marsman et
al., network-psychometrics literature — VERIFY exact citation before any
draft text relies on it). Therefore the comparison is NOT "factor vs
network" as raw fit. It is a comparison of structural commitments under
matched complexity:

- Model A (reflective): low-rank logistic model, rank r ∈ {1..5}.
- Model B (network): sparse pairwise model, node-wise ℓ1 logistic
  (eLasso-style), λ by EBIC or CV.
- Comparison: (i) cross-validated held-out log-loss with cell-wise CV;
  (ii) parameter parsimony (effective df); (iii) structure diagnostics —
  eigenvalue spectrum of the estimated association matrix, edge density,
  community structure. Report all three; do not collapse to a single
  winner statistic without argument.

## 3. Data plan

Phase 1 (pilot, existing data, no collection):
- MegaAcceptability v2 (megaattitude.io): 1,000 clause-embedding verbs ×
  50 frames, normalized ratings. Treat frames as items, verbs as
  respondents. Dichotomize at pre-registered threshold AND run ordinal
  sensitivity check; report both.
- Purpose: de-risk RQ1/RQ2 machinery on dense human data; establish that
  the model comparison discriminates on real judgments.

Phase 3 (new grid, category boundary):
- Lexeme sample: frequency-stratified adjectives + prepositions +
  determinatives (sampling frame: CGEL category lists ∪ a COCA/BNC
  frequency band sample; exact frame to be fixed in a pm-update before
  collection), plus the boundary set (forced inclusion, analyzed with and
  without).
- Items: diagnostics.yaml battery, instantiated as bleached sentences
  (White & Rawlins bleaching method: someone/something/happened).
- Ratings: LLM judge over all cells; designed random gold sample
  (inclusion probabilities stored) expert-coded blind; DSL/PPI-style
  bias correction for all population estimates (VERIFY citations:
  Angelopoulos et al. prediction-powered inference; Egami et al.
  design-based supervised learning).
- Judge validation (separate from correction): agreement with (a) CGEL
  starred/unstarred examples, (b) Sprouse–Almeida collected ratings —
  these are the HARD region, report agreement there separately.

## 4. Go/no-go thresholds (pre-registered, Phase 1 → Phase 2)

GO if, on MegaAcceptability:
- T1: CV log-loss difference between Model A and Model B exceeds 2× the
  cell-wise CV standard error in either direction, OR structure
  diagnostics cleanly dissociate (first-eigenvalue dominance ratio > 3
  vs < 1.5 across category subsets); AND
- T2: ≥ 10 frames show projectibility scores significantly above zero
  (a battery where nothing projects is not a measurement instrument); AND
- T3: synthetic-recovery tests (tests/) pass on matrices matched to the
  empirical n, p, and base rates.

NO-GO (mush): neither model separates, projectibility flat, misfit
uncorrelated with anything. Action: write up as a short methods caution
elsewhere; do not proceed to Phase 3 collection.


Power note (from tests/test_recovery.py): person-fit detection of
partially deviant profiles is weak below ~25 items (planted half-profile
scrambles separate in expectation but not reliably per-item). Phase 3
battery floor: >= 40 items per lexeme (judgment + corpus columns
combined) before RQ3 misfit claims are made about individual lexemes.

## 5. Falsification criteria for the framework claim

The maintained-cluster framing is DISCONFIRMED in this study if the data
are well described by a clean one-dimension-per-category reflective model
with boundary items showing unremarkable misfit. Pre-commit: if that
happens, the paper reports it and the discussion concedes it. The intro
(paper/main.tex §1–2) is written outcome-neutral on purpose; do not edit
it to lean toward a result after results exist.

## 6. Phase plan and division of labour

- Phase 0 (chat, DONE = this bundle): plan, battery, tested pipeline,
  outcome-neutral §1–2, verified references only.
- Phase 1 (Claude Code): fetch MegaAcceptability; run src/pipeline on it;
  emit results/pilot_findings.md + CSVs. No prose interpretation.
- Phase 2 (chat): go/no-go call against §4; citing-papers sweep on
  MegaAttitude (novelty check); freeze Phase 3 sampling frame.
- Phase 3 (Claude Code): build grid, LLM judging, gold sample draw,
  correction stats.
- Phase 4 (chat): results/discussion drafting; adversarial reviews
  (Croftian; White–Rawlins-adjacent; traditional descriptivist); then
  submission package.

## 7. Standing rules for the executor

1. No fabricated numbers anywhere. Unknown values are ⟨RESULT⟩.
2. No new citations. Citation candidates go in paper/TO_VERIFY.md for the
   pm node; only the pm node moves entries into references.bib.
3. Every analysis run writes a manifest (data hash, code commit, seed,
   parameters) to results/.
4. Golden numbers in GOLDEN.md must reproduce before any new analysis is
   trusted; if they drift, stop and post a pm-update.
5. Log pm-updates per the LLM-CLI-projects protocol; identify as
   claude-code:diagnostic-validity.
