# Prediction-Powered Inference (PPI) — verbatim quotes for Study 2 methods

Intake note. Source-grounded: all quotations below are transcribed verbatim from
the **published Science article** (PDF pages read directly, running header
"Angelopoulos *et al.*, *Science* 382, 669-674 (2023)"). Where noted, the
abstract was cross-checked against the arXiv preprint abstract and is identical.

**Use case for our paper:** Study 2 derives bias-corrected POPULATION estimates
from many LLM-judge labels plus a small expert-coded gold sample. PPI is the
method that licenses combining a large set of (possibly biased) machine labels
with a small trusted gold sample to get valid, bias-corrected population
estimates with valid confidence intervals.

---

## 1. Full citation

Angelopoulos, A. N., Bates, S., Fannjiang, C., Jordan, M. I. & Zrnic, T. (2023),
"Prediction-powered inference," *Science* 382(6671), 669-674.
DOI: 10.1126/science.adi6000. Preprint: arXiv:2301.09633.

- **Authors:** Anastasios N. Angelopoulos, Stephen Bates, Clara Fannjiang,
  Michael I. Jordan, Tijana Zrnic (Department of Electrical Engineering and
  Computer Sciences, University of California, Berkeley). The first three are
  marked equal-contribution (†).
- **Venue:** *Science*, vol. 382, issue 6671, pp. 669-674.
- **Published:** 10 November 2023.
- **DOI (journal):** 10.1126/science.adi6000
- **arXiv id:** 2301.09633 (v1 23 Jan 2023; v4 9 Nov 2023). arXiv DOI
  10.48550/arXiv.2301.09633.
- **Code:** https://github.com/aangelopoulos/ppi_py

> Citation-key note: `references.bib` is pm-node-only per project rules. Do NOT
> add a BibTeX entry from here; flag to pm node if the key is missing.

---

## 2. What PPI does — key method sentences (verbatim)

### Abstract (verbatim; identical in Science PDF and arXiv)

> "Prediction-powered inference is a framework for performing valid statistical
> inference when an experimental dataset is supplemented with predictions from a
> machine-learning system. The framework yields simple algorithms for computing
> provably valid confidence intervals for quantities such as means, quantiles,
> and linear and logistic regression coefficients, without making any
> assumptions on the machine-learning algorithm that supplies the predictions.
> Furthermore, more accurate predictions translate to smaller confidence
> intervals. Prediction-powered inference could enable researchers to draw valid
> and more data-efficient conclusions using machine learning."

*(Location: Abstract, p. 669.)*

### Introduction — the core "best of both worlds" claim (verbatim)

> "This manuscript presents prediction-powered inference, a framework that
> achieves the best of both worlds: extracting information from the predictions
> of a high-throughput machine-learning system and guaranteeing statistical
> validity of the resulting conclusions."

*(Location: Introduction, p. 669, left column.)*

### Introduction — combining gold-standard data with predictions (verbatim)

> "Prediction-powered inference provides a protocol for combining predictions,
> which are abundant but not always trustworthy, with gold-standard data, which
> are trusted but scarce, to compute confidence intervals and *P* values. The
> resulting confidence intervals and *P* values are statistically valid, as in
> the classical approach, but also leverage the information contained in the
> predictions, as in the imputation approach, to make the confidence intervals
> smaller and the *P* values more powerful."

*(Location: Introduction, p. 669, middle/right column. This is the single best
sentence pair to quote for our Study 2 — it states the small-gold + large-
machine-prediction combination and the validity guarantee in one place.)*

### Protocol setup — the small labeled vs large unlabeled datasets (verbatim)

> "Toward this goal, they have access to a small gold-standard dataset of
> features paired with outcomes, (*X*, *Y*) = ((*X*₁, *Y*₁), ..., (*X*ₙ, *Y*ₙ)),
> as well as the features of a large unlabeled dataset, (*X*′) = (*X*′₁, ...,
> *X*′_N), where the true outcomes *Y*′₁, ..., *Y*′_N are not observed.
> Typically, *N* is much larger than *n*."

*(Location: "Protocol for prediction-powered inference," p. 669, right column.
Both datasets carry machine-learning predictions of the outcomes, denoted
Ŷ₁,...,Ŷₙ and Ŷ′₁,...,Ŷ′_N respectively.)*

### The three-step protocol + the rectifier (bias correction) (verbatim)

The published article frames the method as a three-step protocol "outlined below
and visualized in Fig. 1":

> "1) **Estimand.** The first step is to select an estimand θ*. The estimand is
> the quantity the scientist is interested in knowing — for example, the mean
> outcome *E*[*Y*ᵢ], median outcome median(*Y*ᵢ), a linear regression coefficient
> obtained by regressing *Y* onto *X*, etc."

> "2) **Measure of fit and rectifier.** The key step is to identify the measure
> of fit *m*_θ and rectifier Δ_θ for the selected estimand. For every candidate
> value of the estimand θ, the measure of fit *m*_θ is computed on the unlabeled
> dataset imputed with predictions, (*X*′, Ŷ′), and quantifies how likely θ* is
> to be equal to θ on the basis of the imputed data. The closer *m*_θ is to zero,
> the more plausible it is for θ* to be equal to θ."

> "The rectifier Δ_θ is a notion of prediction error that is relevant for the
> estimand of interest. It is defined as the difference of the measure of fit
> computed on the labeled data, (*X*, *Y*), and the labeled data when the true
> outcomes are replaced with predicted ones, (*X*, Ŷ). If the predictions are
> perfect, the rectifier is equal to zero."

> "3) **Prediction-powered confidence interval.** Finally, the measure of fit
> and rectifier are carefully combined to form a prediction-powered confidence
> interval for θ*. This process is called rectifying the confidence interval."

*(Location: "Protocol for prediction-powered inference" → three-step list,
p. 669, right column.)*

### One-line gloss of the rectifier role (verbatim, from "Properties" section)

> "Prediction-powered inference uses the gold-standard dataset to quantify and
> correct the errors made by the machine-learning algorithm on the unlabeled
> dataset, thereby enabling researchers to reliably incorporate predictions when
> constructing confidence intervals."

*(Location: "Properties of prediction-powered inference"/Fig. 1 lead-in,
p. 669-670. This is the cleanest single-sentence statement of the bias-
correction idea for a methods paragraph.)*

---

## 3. Suggested short quotation for our Study 2 methods (2-3 sentences)

For the bias-correction framing, the most economical verbatim block is:

> "Prediction-powered inference provides a protocol for combining predictions,
> which are abundant but not always trustworthy, with gold-standard data, which
> are trusted but scarce, to compute confidence intervals and *P* values. The
> resulting confidence intervals and *P* values are statistically valid, as in
> the classical approach, but also leverage the information contained in the
> predictions ... to make the confidence intervals smaller and the *P* values
> more powerful." (Angelopoulos et al. 2023: 669)

Optionally pair with the rectifier gloss:

> "Prediction-powered inference uses the gold-standard dataset to quantify and
> correct the errors made by the machine-learning algorithm on the unlabeled
> dataset ..." (Angelopoulos et al. 2023: 669-670)

---

## 4. Provenance / truncation check

- Quotes transcribed from the **published Science PDF**, pages 1-2 (= journal
  pp. 669-670), read directly via PDF rendering. Both pages rendered in full;
  no truncated or partial fetches. Sentences are complete end to end.
- Abstract cross-checked against arXiv:2301.09633 abstract — identical wording.
- The arXiv HTML render (/html/2301.09633v4) returned HTTP 404; not needed, as
  the published PDF supplied the full method text.
- Page numbers above are inferred from the running header "Science 382, 669-674
  (2023)": PDF page 1 = journal p. 669, PDF page 2 = journal p. 670. The abstract
  and the entire three-step protocol fall on p. 669; the Fig. 1 / "Properties"
  material spans p. 669-670. If a precise page is needed for a single sentence
  near the column break, ⟨VERIFY⟩ against the journal PDF pagination.
