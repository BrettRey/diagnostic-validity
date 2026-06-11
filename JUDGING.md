# JUDGING.md — judging protocol pre-registration (Phase 3)

Status: **DRAFT for pm sign-off.** Registered before any rating exists; the git
history of this file is the timestamp. This is the last document between here and
data. Nothing is rated until this is signed off and the gold sample is drawn
(F6 order: instantiate -> gold -> judge).

## 1. Purpose and principle

The LLM judge is the measurement instrument: it rates each bleached sentence in
the grid for acceptability. It stands in for human raters; its systematic error
is corrected against the expert-coded gold sample via prediction-powered
inference (PPI; the DSL framing is equivalent for the uniform gold draw). The
judge must be **blind**: it sees only sentences, never what is being tested.
Everything that could leak the diagnostic, the category, or the design is
withheld.

## 2. Judge model(s)

- **Pin the exact model ID and release date at run time.** Model names go stale
  fast; verify current names when judging starts, do not trust a name written
  here weeks earlier. ⟨PIN-AT-RUN-TIME⟩
- As of 2026-06-11 the strongest Claude option is Opus-class (`claude-opus-4-8`).
  Recommendation for pm: one **primary** judge (a strong current model) plus one
  **independent-vendor second** judge (a current OpenAI or Google model) so that
  inter-judge agreement is a robustness check and no single vendor's quirks drive
  the result. Each judge's bias is separately gold-corrected.
- **Temperature 0** (deterministic, reproducible) for the primary run. One rating
  per cell per judge.
- Log model id, version/release date, provider, temperature, and all sampling
  params to a run manifest (per-call if they can drift).

## 3. Blinding (non-negotiable)

The judge receives **only the sentence string**. It never sees: the stratum
label, the diagnostic id or gloss, the lexeme-under-test (not highlighted, not
named), the `tradition` expectations, or any indication that the items are
constructed tests. Presentation order is randomized once (seed 26) so adjacent
items do not cue a pattern. Cells are sent one per call (no batching) so earlier
items cannot contaminate later judgments.

## 4. Prompt template (exact, to be frozen at sign-off)

> You are judging the acceptability of English sentences (British English).
> Rate how natural and acceptable the following sentence is to a native speaker,
> on a scale from 1 to 7, where 1 = completely unacceptable (not a possible
> English sentence) and 7 = completely natural (a fully acceptable English
> sentence). Reply with a single integer from 1 to 7 and nothing else.
>
> Sentence: {sentence}

No examples are given (calibration examples would anchor and bias). The scale
wording is fixed; only `{sentence}` varies.

## 5. Rating scale and anchoring

- **1–7 ordinal** (matches MegaAcceptability v2 and PLAN.md). Endpoints anchored
  in the prompt (1 = completely unacceptable, 7 = completely natural).
- Dichotomization for the binary measurement models follows the pre-registered
  PLAN.md threshold; the raw 1–7 is retained for sensitivity.

## 6. Procedure

1. Input = `results/phase3_grid_judgment.csv`, **sentence column only**.
2. Randomize order (seed 26); one sentence per API call; temperature 0.
3. Parse a single integer 1–7. On a non-integer or refusal, retry once; if still
   invalid, record the cell as missing (handled in analysis, not silently
   dropped) and log it.
4. Write ratings + a manifest (model id/version/date, params, git rev, library
   versions, n cells, n missing) to `results/`.
5. Morphology cells (comparative/-ly/-ness/un-) are already realized strings
   (Decision 2); the judge rates them like any other sentence. Their badness,
   where the form is non-existent, is the datum.

## 7. Gold coding (the correction's other half)

- The 600-cell gold sample (`results/phase3_gold_sample.csv`, drawn before any
  rating) is **expert-coded blind** on the same 1–7 scale, by a human coder who
  also does not see stratum/diagnostic labels — only sentences.
- The judge's ratings on the gold cells are compared to the expert codes; the
  PPI estimator uses the gold residuals to debias every population estimate. The
  stored uniform inclusion probability (0.04673) feeds the estimator.

## 8. Sign-off checklist (pm)

- [ ] Pin primary (and any second) model id + release date.
- [ ] Confirm temperature, one-per-call, randomized order.
- [ ] Freeze the prompt wording (section 4).
- [ ] Confirm British English as the rating variety (matches SUBTLEX-UK frame).
- [ ] Confirm the gold-coding plan (who codes; blind; same scale).
- [ ] Confirm dichotomization threshold reference (PLAN.md).

Once signed off: draw nothing new, run the judge, and the ordering invariant
(gold-before-judge) is satisfied because the gold already exists.
