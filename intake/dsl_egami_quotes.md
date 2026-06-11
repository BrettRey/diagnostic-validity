# DSL (Egami, Hinck, Stewart & Wei) — intake quotes

Intake for: Study 2 methods (unbiased population estimates from LLM-judge labels +
a designed probability sample of expert codes).

Source fetched: arXiv:2306.04746, v3 (HTML, `https://arxiv.org/html/2306.04746v3`)
and the arXiv abstract page (`https://arxiv.org/abs/2306.04746`), plus the project
page (`http://naokiegami.com/dsl/`). Retrieved 2026-06-10.

Truncation note: the arXiv HTML body was read in sections via WebFetch. Quotes
below are verbatim single sentences/short fragments I could locate with their
section. I was NOT able to confirm a full continuous read of the Related Work
section, so see the PPI caveat in §3. Anything not directly quoted here should be
re-checked against the PDF before it goes into the paper as a quotation. Use
⟨VERIFY⟩ if you cannot re-confirm a quote against the source.

---

## 1. WHAT DSL DOES (verbatim, with location)

**Abstract.** "To address this, we build on debiased machine learning to propose
the design-based supervised learning (DSL) estimator. DSL employs a
doubly-robust procedure to combine surrogate labels with a smaller number of
high-quality, gold-standard labels. Our approach guarantees valid inference for
downstream statistical analyses, even when surrogates are arbitrarily biased and
without requiring stringent assumptions, by controlling the probability of
sampling documents for gold-standard labeling."

**Introduction (§1).** "Our proposed estimator, design-based supervised learning
(DSL), combines the surrogate and gold-standard labels to create a
bias-corrected pseudo-outcome, which we use in downstream statistical analyses."

**Introduction (§1).** "The proposed DSL estimator is consistent and
asymptotically normal, and its corresponding confidence interval is valid,
without any further modeling assumptions even when the surrogates are arbitrarily
biased."

### The "design-based" / known-inclusion-probability idea (verbatim, §2 Problem Setting)

- "We use π(Qi,Wi,Xi)≔Pr(Ri=1∣Qi,Wi,Xi) to denote the probability of sampling
  document i for gold-standard labeling."
- "Formally, we assume that the sampling probability for gold-standard labeling
  is known and bounded away from zero."
- "For example, if a researcher has 10000 documents and samples 100 of them to
  expert-annotate at random, π=100/10000=.01 for all documents."
- "Both conditions are straightforward to guarantee by design in many social
  science applications where the whole corpus is available in advance, which
  gives the name, design-based supervised learning."

### The estimator (verbatim, §4)

DSL pseudo-outcome (bias-corrected outcome):
`Ỹik ≔ ĝk(Qi,Wi,Xi) + Ri/π(Qi,Wi,Xi) · (Yi − ĝk(Qi,Wi,Xi))`

(Notation: `Yi` = gold-standard label; `ĝk` = surrogate/predicted label model
fit out-of-fold; `Ri` = 1 if document i was sampled for gold-standard labeling;
`π` = known sampling probability. The correction term is nonzero only on the
gold-labeled subsample, reweighted by inverse sampling probability.)

**One-line gloss for the paper (paraphrase, not a quote):** DSL takes a
*known-probability random sample* of documents to be expert ("gold") labeled,
predicts labels for the whole corpus with the LLM surrogate, then forms an
inverse-probability-weighted, doubly-robust pseudo-outcome that corrects the
surrogate's bias on the sampled subset — yielding consistent, asymptotically
normal downstream estimates with valid confidence intervals even when the LLM
labels are arbitrarily biased.

---

## 2. FULL CITATION

Egami, Naoki; Hinck, Musashi; Stewart, Brandon M. & Wei, Hanying. 2023. Using
imperfect surrogates for downstream inference: Design-based supervised learning
for social science applications of large language models. In *Advances in Neural
Information Processing Systems 36* (NeurIPS 2023).

- Venue: 37th Conference on Neural Information Processing Systems (NeurIPS 2023);
  *Advances in Neural Information Processing Systems*, vol. 36.
- arXiv: arXiv:2306.04746. DOI (arXiv): https://doi.org/10.48550/arXiv.2306.04746
- arXiv versions: v1 2023-06-07; v2 2023-10-31; v3 2024-01-14 (current; quotes
  above are from v3).
- NeurIPS proceedings page:
  https://proceedings.neurips.cc/paper_files/paper/2023/hash/d862f7f5445255090de13b825b880d59-Abstract-Conference.html
- ⟨VERIFY⟩ page range / editors for the NeurIPS proceedings volume — not captured
  here. NeurIPS proceedings typically lack continuous page numbers; pm node
  should set the canonical biblatex-APA entry in references.bib (executor must
  not edit references.bib).

Note: the authors later issued an expanded/retitled journal version, "Using
large language model annotations for the social sciences: A general framework of
using predicted variables in downstream analyses" (per naokiegami.com/dsl/).
That is a *different, later* work — do not conflate it with the NeurIPS 2023
paper cited above. Confirm separately if you intend to cite the journal version.

---

## 3. DSL vs. prediction-powered inference (PPI) — CAVEAT, not a clean quote

I could NOT find a sentence in the v3 main text (as fetched) that names
"prediction-powered inference" or "PPI" and contrasts it with DSL. The paper
*does* cite Angelopoulos et al. [2023] (the PPI paper) in Related Work and
locates DSL in the same debiased-ML / efficient-influence-function family.

Closest located sentence (Related Work, verbatim): "Like these papers, we
exploit the efficient influence function to produce estimators with reduced
bias." — this follows the cluster of citations that includes Angelopoulos et al.
[2023], but it does not single out PPI by name.

⟨VERIFY⟩ If the paper needs an explicit DSL-vs-PPI contrast, read the PDF Related
Work section directly (the HTML fetch may have dropped surrounding sentences).
The two methods share the same goal (valid inference from imperfect predicted
labels via a labeled probability sample); a substantive head-to-head contrast,
if any, must be quoted from the source, not asserted from memory.

---

## 4. WHICH SECTION IS THE LLM-judge + designed-sample application

Empirical section: **§5 Experiments**, with
- §5.1 Logistic Regression in Congressional Bills Data
- §5.2 Class Prevalence Estimation

Both apply LLM/automated surrogate labels together with a designed
(known-probability) sample of gold-standard expert codes. For a "Study 2"
analogue (population/prevalence estimation from LLM-judge labels + designed
expert subsample), §5.2 Class Prevalence Estimation is the closest match;
§5.1 is the regression-coefficient analogue. ⟨VERIFY⟩ exact §5 sub-structure and
sample sizes against the PDF before citing specifics.
