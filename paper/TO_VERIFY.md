# TO_VERIFY.md — citation/claim quarantine (pm-node work, Phase 2)

Rule (CLAUDE.md 1-2): nothing moves from here into references.bib or
unmarked prose until the source has been read. Executor may ADD items
here; only the pm node RESOLVES them.

## Citations to verify and complete

1. White & Rawlins 2016 — MegaAcceptability release paper. Believed:
   SALT 26 proceedings, "A computational model of S-selection". Need:
   venue confirmation, volume, pages, DOI.
   - [READ 2026-06-10 — pm to promote] Confirmed via the W&R 2020
     reference list (lingbuzz 004596) and megaattitude.io: White, Aaron
     Steven & Kyle Rawlins. 2016. "A computational model of S-selection."
     *Semantics and Linguistic Theory* (SALT) 26, 641–663. CLC
     Publications, Ithaca, NY. DOI 10.3765/salt.v26i0.3819. Ready for key
     whiterawlins2016 (@inproceedings). **PROMOTED to references.bib
     2026-06-10 (pm).**
2. White & Rawlins 2020 — "Frequency, acceptability, and selection: A
   case study of clause-embedding", Glossa. Need: volume, article no.
   - [READ 2026-06-10 — pm to promote] PDF read (lingbuzz 004596);
     published version confirmed via publisher metadata
     (doi.org/10.5334/gjgl.1001): *Glossa: a journal of general
     linguistics* 5(1), published 2020-11-04, DOI 10.5334/gjgl.1001.
     Glossa uses continuous article numbering; the article id was not
     captured from the metadata, but the DOI is sufficient for a
     biblatex-APA @article. **PROMOTED to references.bib 2026-06-10 (pm)**
     as Glossa 5(1), article 105 (pm verified the article number).
3. Marsman et al. — Ising/IRT equivalence result (network psychometrics).
   Believed: Marsman et al., Multivariate Behavioral Research, ~2018,
   "An introduction to network psychometrics...". Need: full citation
   AND the exact scope of the equivalence claim before §2.2 relies on it.
   - [pm 2026-06-10] marsman2018 PROMOTED to references.bib (citation
     verified). STILL OPEN: the executor must read the paper to (a)
     confirm the author list past Waldorp (reconstructed from the journal
     listing), and (b) record the EXACT scope of the Ising/IRT equivalence
     before §2.2's ⟨VERIFY⟩ resolves.
4. Borsboom-school network psychometrics overview for §2.2 (psychology
   restructuring claim). Candidate: Borsboom & Cramer, Annual Review of
   Clinical Psychology. Need: exact cite.
   - [pm 2026-06-10] borsboomcramer2013 PROMOTED to references.bib
     (Annual Review of Clinical Psychology 9(1), 91–121).
5. Sprouse & Almeida replication work. Believed: Sprouse & Almeida 2012
   (J. Linguistics, Adger textbook data); Sprouse, Schütze & Almeida
   2013 (Lingua, LI 2001-2010 random sample). Need: full cites + the
   actual replication rate (do NOT write "95%" from memory).
   - [pm novelty sweep 2026-06-10 — READ before use] Sprouse 2018 handbook
     chapter reports ~3% sign-reversal for the Linguistic Inquiry
     replication data, with subsequent replications at 0–6%. Use these
     real numbers (never "95%") once the chapter is read; see item 13.
6. Prediction-powered inference — Angelopoulos et al., Science, ~2023.
7. Design-based supervised learning — Egami et al. (NeurIPS?). Items 6-7
   gate the Study 2 methods text.
8. CoLA — Warstadt, Singh & Bowman, TACL ~2019, "Neural Network
   Acceptability Judgments". Need: full cite + corpus size as published.
9. Reynolds 2021, "Quantifying determinatives..." (Cadernos de
   Linguística) — own paper; need volume/pages/DOI for the bib.
10. Boyd HPC citation IF the discussion needs it (PLAN: not headlined).
    Candidate: Boyd 1991, Philosophical Studies. Verify before use.
11. Goodman 1955 page reference for 'projectible' if a pinpoint cite is
    wanted in §1.
12. van der Maas et al. 2006 — positive-manifold-from-network result (a
    g-like factor can emerge from a densely connected network with no
    common cause). Relevant to reading the two large eigenvalues without
    conceding the reflective story. [pm novelty sweep 2026-06-10 — READ
    before use.] Need: full cite (Psychological Review?) + exact claim.
13. Sprouse 2018 — handbook chapter with acceptability-replication-rate
    numbers (feeds item 5). [pm novelty sweep 2026-06-10 — READ before
    use.] Need: full cite (handbook title, editors, pages, publisher).
14. SUBTLEX-UK — Phase 3 frequency frame (F2). van Heuven, Mandera,
    Keuleers & Brysbaert ~2014, Quarterly Journal of Experimental
    Psychology, "SUBTLEX-UK: A new and improved word frequency database
    for British English". [pm 2026-06-10 — frame citation; verify before
    bib.] Need: full cite (volume, issue, pages, DOI). Frame file URL +
    SHA-256 logged to the Phase 3 sampling manifest.

## Claims to verify against sources

A. CGEL's actual classification of *worth* (adjective with exceptional
   NP complement vs preposition), with chapter/section — gates a clause
   in §2.1 currently marked ⟨VERIFY⟩. Chat-session prior: ~0.6 adjective.
B. Every `source:` field in diagnostics.yaml — confirm each diagnostic's
   canonical statement and location before the battery is frozen.
C. Matthews 2014 "diagnostics have drifted" characterization in §2.1 —
   re-read the relevant chapters and either support with specifics or
   soften.
D. MegaAcceptability v2 normalization procedure details (gates the
   dichotomization step in Phase 1).
   - [READ 2026-06-10 — W&R 2020 §3, §4.3, App. B] W&R normalize with an
     ORDINAL (linked/cumulative-logit) MIXED-EFFECTS model fit to the 1–7
     ratings: fixed effects for verb, frame, and their interaction; random
     unconstrained cutpoints per participant. The fitted model yields a
     real-valued normalized acceptability per verb-frame pair (§4.3 uses
     "a slightly modified form"). They explicitly contrast this with
     simple z-scoring. The v2 release ships RAW ordinal 1–7 responses, not
     normalized scores. The Phase 1 pilot DELIBERATELY uses participant-
     level z-scoring (pre-reg 2026-06-10, DECISIONS.md), a simpler
     approximation; reproducing W&R's ordinal-model normalizer is not
     required to de-risk the model-comparison machinery, and is deferred
     unless a Study 1 paper claim needs it.

E. W&R 2020 factorization section — what was factorized and how it
   performed (gates any §5 corroboration claim that W&R found low-rank
   weak on this grid).
   - [READ 2026-06-10 — W&R 2020 §6, §1 claim (i), Abstract] W&R's
     factorization models (LDA; logistic factor analysis with U ∈
     R^{NV×K}, A ∈ R^{K×NF}; GloVe trained on VALEX verb–frame counts;
     pretrained GloVe/NBoW; BERT) are proof-of-concept ACQUISITION models
     that predict acceptability from frequency/cooccurrence input. Claim
     (i): shallow factorization yields "minuscule improvements" over the
     direct frequency models of §5; (ii) deep abstraction (BERT) predicts
     acceptability quite well. The "factorization fares only marginally
     better" result is RELATIVE TO FREQUENCY BASELINES on the
     frequency→acceptability acquisition question — NOT a reflective
     (low-rank)-vs-network comparison of the acceptability matrix itself.
     CONCLUSION: does NOT support the stronger corroboration reading; the
     claim that W&R found "low-rank weak on this grid" stays OUT of §5 (pm
     self-correction confirmed). The LFA model does factorize a verb×frame
     Π, but its evaluation target and baseline differ from ours.
