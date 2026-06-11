# CoLA (Warstadt, Singh & Bowman 2019) — source-grounded quotes

Source-grounded intake note. All numbers and citation details below are quoted
verbatim from primary sources. Retrieved 2026-06-10.

## Sources consulted

- **arXiv full text (primary for numbers):** https://arxiv.org/pdf/1805.12471
  (extracted with `pdftotext -layout`; full body text, not just abstract)
- **ACL Anthology landing page (primary for citation):** https://aclanthology.org/Q19-1040/
- **arXiv abstract page:** https://arxiv.org/abs/1805.12471
- **MIT Press / TACL article page:** https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00290/43528/

Note: WebFetch on both PDFs returned unparsed binary; the saved arXiv PDF was
extracted locally with `pdftotext`. The MIT Press and Anthology HTML pages
returned only the abstract via WebFetch, so the split numbers below come from the
arXiv full-text extraction. Abstract wording matches across arXiv and Anthology.

---

## 1. Corpus size

### Total (verbatim, from the abstract; identical on arXiv and ACL Anthology)

> "We introduce the Corpus of Linguistic Acceptability (CoLA), a set of 10,657
> English sentences labeled as grammatical or ungrammatical from published
> linguistics literature."

Location: Abstract.

### Train / dev / test split (verbatim, from §2 "The Corpus of Linguistic Acceptability", subsection "Splitting the Data")

> "The in-domain set is split three ways into training (8551 examples),
> development (527), and test sets (530), all drawn from the same 17 sources.
> The out-of-domain set is split into development (516) and a test sets (533),
> drawn from another 6 sources."

(The "a test sets" wording is verbatim as printed; apparent typo in the original.)

Location: §2, paragraph headed "Splitting the Data".

### Table 2 totals (verbatim values, from the "by source" table)

From Table 2 ("The contents of CoLA by source. N is the number of sentences in a
source."), the summary rows give:

- In-Domain: N = 9515
- Out-of-Domain: N = 1049
- Total: N = 10657

Table 2 caption (verbatim):

> "Table 2: The contents of CoLA by source. N is the number of sentences in a
> source. % is the percent of sentences labeled acceptable. Sources listed above
> In-Domain are included in the training, development, and test sets, while those
> above Out-of-Domain appear only in the development and test sets."

### ⟨VERIFY⟩ internal discrepancy in the paper (flagged, not resolved)

The two in-domain figures in the paper do not reconcile exactly:
- Table 2 reports In-Domain N = **9515**.
- The "Splitting the Data" text sums to **9608** (8551 + 527 + 530).

The out-of-domain figures do reconcile: 516 + 533 = **1049** = Table 2's
Out-of-Domain N. The stated grand total is **10,657** (matches the abstract).
The 9515 vs. 9608 mismatch (Δ = 93) is internal to the published paper; this note
does not "fix" it. If a precise per-split count is needed for the diagnostic-validity
paper, use the publicly released CoLA split files (nyu-mll/CoLA-baselines) and
manifest them in results/, rather than relying on either printed figure.
Added to paper/TO_VERIFY.md.

**Headline number for citation:** 10,657 sentences total (abstract).

---

## 2. Full citation (verbatim from ACL Anthology Q19-1040)

Alex Warstadt, Amanpreet Singh, and Samuel R. Bowman. 2019. Neural Network
Acceptability Judgments. *Transactions of the Association for Computational
Linguistics*, Volume 7, pages 625–641. DOI: 10.1162/tacl_a_00290.

- Authors: Alex Warstadt; Amanpreet Singh; Samuel R. Bowman
- Venue: Transactions of the Association for Computational Linguistics (TACL)
- Year: 2019
- Volume: 7
- Pages: 625–641
- DOI: 10.1162/tacl_a_00290
- ACL Anthology ID: Q19-1040
- Open-access PDF (MIT Press): https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00290/43528/
- Preprint: arXiv:1805.12471
