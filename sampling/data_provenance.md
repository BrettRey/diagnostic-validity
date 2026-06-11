# Phase 3 data provenance (F2)

Frame + determinative matrix for the Phase 3 sampler. Hashes are SHA-256.
The eventual F4 sampler manifest references these.

## SUBTLEX-UK frequency frame (F2)
- Source URL: https://psychology.nottingham.ac.uk/subtlex-uk/SUBTLEX-UK.txt.zip
  (the cleaned, text/TSV file the database designates as standard).
- Fetched: 2026-06-11 (UTC).
- zip SHA-256:  e40d83af55eb85e9e2bc0d72e1022b10e47e31ff2086ad2edcc18292d6bd6616
- .txt SHA-256: 9cc02e83efce5c606606578122b792e364dcee52799115218f2cfd596e0fe0f3
- Integrity: Content-Length 3,488,497 bytes matched; `unzip -t` OK (not
  truncated). Extracted SUBTLEX-UK.txt = 18,218,234 bytes; 160,024 types
  (160,025 lines incl. header). Tab-separated. This is the CLEANED ~160k-type
  file, NOT the 332,988 uncleaned one (which includes numbers/junk).
- Columns verified present (F2 requirement): **LogFreq(Zipf)** (col 6) = the
  Zipf banding variable; **DomPoS** (col 16) = dominant PoS. (Also Freq, CD,
  Cbeebies/CBBC/BNC Zipf variants, DomPoSLemma/Freq, AllPoS.) No Zipf
  recompute needed; the F2 fallback is not triggered.
- Cite: vanheuven2014 (in references.bib).
- Repo policy: GITIGNORED (18 MB); reproducible by re-download from the URL +
  SHA-256 verify (same model as the 36 MB MegaAcceptability). Flag to pm if a
  committed copy is wanted instead.

## Reynolds 2021 determinative/pronoun feature matrix (F1c)
- Source: LingBuzz 005747 (reynolds2021matrix); pm's local copy
  (`~/Downloads/reynolds_21_Full-matrix-o.file`) -- LingBuzz robots-blocks
  automated fetch, so the local copy is authoritative.
- Copied to: data/reynolds2021_determinative_matrix.csv (COMMITTED; 47 KB; not
  re-downloadable).
- SHA-256: a15af082a6bc5dbe24bcf57475c35cad1b00c2dc7e17af584db1841bf7abddf7
- Format: CSV; 137 word-forms (rows) x 155 features (cols) + a `names` label
  column (the 155-feature filtered version). Row labels are word-forms, with
  `_det`/`_pron` disambiguation only for ambiguous forms (one_det/one_pron,
  we_det/we_pron, you_det/you_pron_sing, what_det/what_pron, which_*_det/pron,
  …). Features are distributional/morphological binary codes; there is NO
  det/pron category column.
- **F1c TODO (gates the determinative draw, not the rest):** the stratum = the
  73 determinatives. Only 14 rows are `_det`-suffixed and 8 `_pron`-suffixed;
  the ~115 bare rows carry no category label, so the 73/65 split is Reynolds'
  a-priori classification and must be SOURCED (read Reynolds 2021, Cadernos
  10.25189/2675-4916.2021.V2.N3.ID399) or pm-confirmed -- not inferred from
  memory -- before the F4 determinative draw.
