# Marsman et al. (2018) — verbatim quotes for §2.2 caution

**Status: FULL TEXT obtained (not partial).** Open-access (CC BY-NC-ND) final
published version from the UvA-DARE repository, identical to the Taylor &
Francis gold-OA version. Extracted with `pdftotext -layout`; PDF saved at
`intake/marsman2018.pdf`, raw text at `intake/marsman2018_extracted.txt`
(1304 lines, complete article body + references). The Taylor & Francis HTML
page itself returned **HTTP 403** to the fetcher, so the repository PDF was
used; it carries the same DOI and the explicit "Open Access article" notice.

Note on page numbers: this is a two-column journal article. Running heads in
the extracted text mark the page boundaries, so each quote below is tagged
with the journal page on which it falls (pp. 15–35). Mathematical notation
that did not survive plain-text extraction (subscripts, integral signs, the
matrix Σ) is rendered approximately; the **prose** is verbatim.

---

## 1. Full citation (confirmed from the repository title page + APA block)

> Marsman, M., Borsboom, D., Kruis, J., Epskamp, S., van Bork, R., Waldorp, L. J., van der Maas, H. L. J., & Maris, G. (2018). An introduction to network psychometrics: Relating ising network models to item response theory models. *Multivariate Behavioral Research*, 53(1), 15–35. https://doi.org/10.1080/00273171.2017.1379379

- **Complete author list, in order:** M. Marsman; D. Borsboom; J. Kruis; S. Epskamp; R. van Bork; L. J. Waldorp; H. L. J. van der Maas; G. Maris.
  (The two names **after Waldorp** are **van der Maas, H. L. J.** and **Maris, G.**)
- **Volume(issue):pages:** 53(1):15–35. **Year:** 2018 (online 07 Nov 2017).
- **DOI:** 10.1080/00273171.2017.1379379
- **Licence:** CC BY-NC-ND (the title page reads "License / CC BY-NC-ND";
  the article footer on p. 15 reads "This is an Open Access article distributed
  under the terms of the Creative Commons Attribution-NonCommercial-NoDerivatives
  License").

---

## 2. SCOPE / CONDITIONS of the Ising–IRT relation (verbatim)

### 2a. The headline scope claim — "broad equivalence", hedged

Abstract (p. 15):

> "Despite the divergent backgrounds of the models, we show a broad equivalence between them and also illustrate several opportunities that arise from this connection."

Introduction (p. 16) — note the hedge "in certain cases":

> "As will become apparent, even though the conceptual framework that motivates the statistical representation in a psychometric model may be strikingly different for network models and latent variable models, the network models and latent variable models turn out to be strongly related; so strongly, in fact, that we are able to establish a general correspondence between the model representations and, in certain cases, full statistical equivalence."

So the top-level claim is: **a general correspondence between representations, with *full statistical equivalence* only "in certain cases."** Not an unconditional equivalence.

### 2b. The Curie-Weiss (fully connected Ising) ↔ Rasch leg, with explicit constraints

(i) Curie-Weiss = Extended Rasch model **subject to a constraint** (pp. 19–20):

> "Comparing the expression for the Curie-Weiss model in Equation (2) and that for the E-RM in Equation (3), we see that they are equivalent subject to the constraints:"
> [constraints: log βi = μi ; log λ_{x+} = σ x+²]
> "That is, whenever a quadratic relation holds between the total scores x+ and the log of the λ_{x+} parameters in the E-RM, the E-RM is equivalent to the Curie-Weiss model."

(ii) Extended Rasch model → marginal Rasch (latent-variable) model **iff** a moment condition (p. 20):

> "Importantly, the E-RM simplifies to an M-RM if and only if the λs constitute a sequence of moments (Cressie & Holland, 1983; see Theorem 3 in Hessen, 2011, for the moment sequence of a normal structural model)."

(iii) The statistical-equivalence statement for this leg (p. 20):

> "We then only need a bit of algebra to obtain the M-RM in Equation (4), with δi = −μi. This is an important result as it implies the statistical equivalence of the network approach in Figure 5 and the latent variable approach in Figure 6."

(iv) **Crucial caveat — the implied latent-variable distribution is NOT the usual normal** (p. 20):

> "The structural model that results from the derivation is not the typically used normal distribution, but the slightly peculiar:"
> [g(θ) = mixture of n+1 normal posteriors]

and (p. 20):

> "Some instances of the structural model are shown in Figure 7, which reveals a close resemblance to a mixture of two normal distributions with equal variances and their respective means placed symmetrically about zero. For an interaction effect σ that is sufficiently small, Figure 7 reveals that g(θ) is close to the typically used normal model."

### 2c. The general Ising ↔ multidimensional IRT (MD-2PL) leg, via eigendecomposition

The mechanism (pp. 23–24): eigenvalue decomposition of the connectivity
matrix Σ, then Kac's Gaussian-integral representation applied to each
eigen-component, yields the MD-2PL.

> "Applying Kac's integral representation to each of the factors exp(Σ a_ir x_i)² reveals a multivariate latent variable expression for the Ising model, for which the latent variable model p(x | θ) is known as the multidimensional two-parameter logistic model (MD-2PL; Reckase, 2009)."

> "This formal connection between Ising network models and multidimensional IRT models proves the assertion of Molenaar (2003), who was the first to note [...]"

Summary sentence for this leg (p. 23):

> "[...] this correspondence, and shows that to each Ising model we have a statistically equivalent IRT model."

**Identification caveat baked into the equivalence** (p. 23): because the
diagonal of the connectivity matrix Σ cancels in the Ising model, the
decomposition (and hence the loadings A / latent dimensions) is **not unique**:

> "Since we use the ±1 notation for the spin random variables x_i, we observe that the terms σ_ii x_i² = σ_ii cancel in the expression for the Ising model [...] the diagonal elements of the connectivity matrix are undetermined. This indeterminacy implies that we have some degrees of freedom regarding the eigenvalue decomposition of the connectivity matrix."

> "[...] for every diagonal matrix C, the matrix Σ** = Σ + C characterizes the same marginal distribution p(x). [...] Even though these eigenvectors, and the latent variable models that are characterized by them, are strikingly different, both characterize the same marginal distribution."

### 2d. Low-rank approximation = a PRACTICAL estimation device, not the equivalence condition

The low-rank piece is introduced for *estimating* the connectivity matrix,
citing Eckart–Young — it is not what makes the models equivalent (p. 24):

> "Using a well-known result from Eckart and Young (1936), who proved that the best rank R approximation to the full (connectivity) matrix is one where all but the R largest eigenvalues are equated to zero, we have suggested a low-rank approximation to the full-connectivity matrix. However, this low-rank approximation is not uniquely determined."

(The exact Ising = MD-2PL correspondence in 2c uses the **full** rank;
low rank is a downstream approximation for tractable estimation.)

---

## 3. What the equivalence does NOT establish (the §2.2 caution proper)

These are the load-bearing hedge sentences for a caution.

(i) Only statistical, not theoretical/causal — and only for a given dataset (p. 27):

> "Thus, the equivalence shown here is not a full-blown equivalence of theoretical models, but only of statistical models that describe a given data set."

(ii) Multiple conceptual models map to one statistical model; fit licenses no inference (p. 26):

> "Because multiple conceptual models map to the same statistical model, the fit of a statistical model [...] does not license a definitive inference to a conceptual model [...] even though a conceptual model may unambiguously imply a particular statistical model."

(iii) Statistical equivalence is ineradicable (p. 27):

> "It is important to observe that statistical equivalence can never be fully eradicated."

(iv) The equivalence is between two *interpretations* of binary associations (pp. 31):

> "That the network models of Lenz and Ising directly relate to the IRT models of Rasch and Reckase implies that every observed association (of binary random variables) can be given two interpretations: The associations can be interpreted to arise from a direct influence between variables or due to an underlying and unobserved (set of) common cause(s)."

(v) **Boundary condition — equivalence/fit holds only at low interaction strength** (pp. 27–28):

> "This suggests that an M-RM with the typically used normal latent variable model f(θ) will fit to data that comes from a Curie-Weiss model with a sufficiently low interaction strength σ, but it will not fit when the interaction strength is too high."

> "The first illustration confirms our intuition that the M-RM with the typically used normal latent variable model f(θ) will fit to data that is generated from a Curie-Weiss model when the interaction strength is sufficiently low, but not when the interaction strength is too high."

---

## Plain-words scope (for §2.2 wording)

- The equivalence is **statistical**, not causal/theoretical: same probability
  distribution over the binary data, two interpretations (direct-interaction
  network vs. common-cause latent variable). It does not say which is "real,"
  and fit cannot adjudicate (p. 27).
- It is **conditional**, and the hedge words are the authors' own: a "general
  correspondence" with "full statistical equivalence" only "in certain cases"
  (p. 16). The Curie-Weiss↔Rasch leg holds **subject to constraints** (a
  quadratic moment relation) and is exact only with a **non-normal**,
  data-derived latent distribution g(θ), not the usual normal prior (p. 20).
- The general Ising↔multidimensional-IRT (MD-2PL) leg is an **exact full-rank**
  correspondence via Kac's integral, but the latent dimensions are **not
  uniquely identified** (diagonal of Σ is free); **low-rank** is a separate,
  downstream *approximation* for estimation (Eckart–Young), not the equivalence
  itself (pp. 23–24).
- Practical boundary: the standard normal-prior IRT model only **fits**
  Curie-Weiss/Ising data when **interaction strength is sufficiently low**; it
  breaks down when interactions are strong (pp. 27–28).
