# JUDGING.md — judging protocol pre-registration (Phase 3)

Status: **pm-signed-off + FROZEN 2026-06-11 (A1–A5 applied).** The operative
sign-off (the A1–A5 message) froze the no-examples §4 prompt and authorized the
run with no further round-trip. Registered before any rating exists; git history
is the timestamp. F6 order: instantiate → gold → judge.

## 1. Purpose and principle

The LLM judge is the measurement instrument: it rates each bleached sentence for
acceptability. Its systematic error is corrected against the expert-coded gold
sample via prediction-powered inference (PPI; DSL is equivalent for the uniform
gold draw). The judge is **blind** -- it sees only sentences, never the
diagnostic, category, lexeme, or design.

## 2. Judge models (A1 — pinned)

- **Primary: `claude-fable-5`** (Anthropic). Dated snapshot string logged at run
  time. Its PPI-corrected estimates are the **headline** numbers.
- **Second (independent vendor): `GPT-5.5`** (OpenAI, shipped 2026-04-23). Dated
  snapshot logged. A **robustness check** only: inter-judge agreement + a
  parallel PPI-corrected re-estimate.
- The two are **never ensembled or averaged** (an ensemble is an unpinnable
  judge). Current-names checked 2026-06-11 (Anthropic: Fable 5, Opus 4.8;
  OpenAI: GPT-5.5; Google: Gemini 3.1 Pro). Fable 5 supersedes the earlier
  Opus-class note -- the stale-names catch working as designed.
- **Temperature 0**, but determinism is not guaranteed across infrastructure, so
  the design is **one rating per cell per judge** (gold correction absorbs judge
  noise; we do not chase it with repeats).

**Disclosure (goes in the paper's methods):** the judging model and the drafting
workflow share a vendor (and indeed a model family), which is why the design
never leans on judge authority -- PPI correction against human gold makes the
headline estimates unbiased under judge error by construction, and the
cross-vendor second judge covers family-quirk concerns.

## 3. Blinding (non-negotiable)

The judge receives **only the sentence string**: never the stratum, diagnostic
id/gloss, lexeme-under-test (not named, not highlighted), `tradition`
expectations, or any hint the items are constructed. Presentation order
randomized once (seed 26). One sentence per call (no batching) so earlier items
cannot contaminate later ones.

## 4. Prompt (A2 — FROZEN)

**No example sentences.** The operative sign-off (the A1–A5 message, temporally
second) accepted the no-examples design, overruling the earlier example-anchor
requirement: deleting examples prevents lexeme contamination more thoroughly
than auditing them, and endpoint verbal anchors preserve scale interpretability.
The plausibility guard is retained (the bleached grid is bland-to-odd by design;
without it judges discount uninformative-but-grammatical items). Frozen text,
exactly:

> You are judging the acceptability of English sentences (British English). Rate how natural and acceptable the following sentence is to a native speaker, on a scale from 1 to 7, where 1 = completely unacceptable (not a possible English sentence) and 7 = completely natural (a fully acceptable English sentence). Some sentences may be unusual or uninformative; judge only whether the sentence is possible, natural English, not whether it is likely, sensible, or informative. Reply with a single integer from 1 to 7 and nothing else.
>
> Sentence: {sentence}

Same text, reply-line adapted to the interface, is the gold-coding instruction
(A4 construct invariant). The runner stores this exact string in its manifest.

## 5. Rating scale + dichotomization (A3 — pre-registered)

- **1–7 ordinal**, endpoints anchored in the prompt.
- The Phase-1 cut (z̄ > 0) was defined over MULTIPLE human raters per cell; the
  grid has ONE deterministic rating per judge per cell, so it does not transfer.
  **Primary cut = within-judge z > 0** (each judge's ratings standardized over
  its own full 12,840-cell set, mirroring Phase 1's rater-relative logic).
  **Sensitivity arms = raw ≥ 5 and raw ≥ 4.** Verdict-invariance across arms
  applies exactly as in Phase 1. Mirrored in PLAN.md §3.

## 6. Procedure + manifest (A5)

1. Input = `results/phase3_grid_judgment.csv`, **sentence column only**.
2. Randomize order (seed 26); one call per sentence; max_tokens 1024.
3. Parse a single integer 1–7. Non-integer / refusal: **retry once, then mark
   judge-missing** -- never silently imputed, never silently dropped.
4. Manifest schema (named so absence is a test failure, not an oversight),
   **per judge**: model id, snapshot string, provider, run date, sampling params,
   randomization seed, library versions, git rev, n cells, n missing.

**Runtime deviations (logged 2026-06-11, measured pre-run).** `claude-fable-5`
is a reasoning model: (a) it DEPRECATES `temperature`, so it is not sent (model
default sampling) -- the pre-registered "temperature 0" is unattainable for this
model and is absorbed by the one-rating-per-cell design and the "determinism not
guaranteed" hedge; (b) thinking is MANDATORY and cannot be disabled, so
`max_tokens` is 1024 (8 truncated mid-thought) and output averages ~79 tokens
(~76 reasoning). The primary judge therefore DELIBERATES rather than snap-judges;
this does not break the design -- PPI anchors the headline estimates to the human
gold (the construct), debiasing whatever the judge's deliberation adds. The
GPT-5.5 second judge will run at `reasoning_effort=minimal` (settable there).
Measured full-grid budget: ~2.44 M input + ~1.02 M output tokens (~$23 mid /
~$113 premium live; ~half via Batch).

## 7. Gold coding (A4)

- **Identical instruction wording** to the §4 prompt, with only the reply-format
  line adapted to the interface -- instruction identity is the PPI construct
  invariant (judge and coder must measure the same thing).
- **Blind interface built:** `results/gold_coding_blind.csv` (randomized, seed
  26; sentence strings + a blank rating column; no lexeme/item/stratum). Rejoin
  key (`results/gold_coding_key.csv`) is executor-only during coding (cell
  mapping, not judge output).
- **Firewall (logged rule):** the gold coder views no judge output until all 600
  codes are committed; the commit hash is the evidence.
- **Variety:** British English; for any cell where variety uncertainty genuinely
  arises, the coder **flags, does not guess** (Canadian-intuition nuisance).
- **Inclusion-probability assert:** the PPI code asserts stored
  `inclusion_prob == 600 / 12840` (= 0.04673) at load -- the number changed once
  during the D1 re-draw (0.04753 → 0.04673), so the assert makes the manifest
  self-checking.
- 200-cell κ subset waits on the Pullum email (gates nothing).

## 8. Sign-off checklist

- [x] Models pinned (A1: `claude-fable-5` primary, `GPT-5.5` second).
- [x] Temperature 0, one-per-call, randomized order.
- [x] British English; identical wording to judge + gold coder (A4).
- [x] Dichotomization resolved (A3).
- [x] Gold plan: coder = pm, blind, same scale/instructions, firewall (A4).
- [x] Prompt frozen (§4; no-examples design per the operative sign-off).

**JUDGING.md FROZEN 2026-06-11.** Run authorized (no further round-trip).
Access note: primary `claude-fable-5` runs from this environment now; second
`GPT-5.5` runs when an `OPENAI_API_KEY` is present (robustness-only, non-blocking).
