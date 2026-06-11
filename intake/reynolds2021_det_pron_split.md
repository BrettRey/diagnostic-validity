# Reynolds (2021): determinative vs pronoun split

**Source:** Reynolds, Brett (2021). "Quantifying the Differences Between
Lexical Categories: The Case of Pronouns and Determinatives in English."
*Cadernos de Linguística* 2(3), e399. DOI 10.25189/2675-4916.2021.V2.N3.ID399.
Open access.

- Landing page: https://cadernos.abralin.org/index.php/cadernos/article/view/399
- Full-text PDF (read in full, 16 pp.): https://cadernos.abralin.org/index.php/cadernos/article/view/399/488
- XML galley: https://cadernos.abralin.org/index.php/cadernos/article/view/399/483
- Supplementary matrix (the real data): Reynolds (2021), *LingBuzz* 005747,
  file `73-65full.csv` -- https://ling.auf.net/lingbuzz/005747

## Headline answer

The paper does **NOT** print an explicit in-text list/table/appendix that
names which word-forms are determinatives and which are pronouns. It gives:

1. The **counts** in prose (§2.2, p. 8): "138 rows for word forms
   (73 determinatives and 65 pronouns) and 232 columns for features."
2. A **dendrogram** (Figure 1, p. 10) with the pronouns boxed in red and the
   determinatives boxed in blue -- a figure, not a transcribable list.
3. A **data-availability** pointer to the supplementary CSV `73-65full.csv`
   on LingBuzz (§2.2: "I have made my data available...").
4. An **appendix of R code** (p. 16) that reveals how the split is encoded.

**The classification is encoded by ROW ORDER in `73-65full.csv`, not by any
"category" column.** The appendix R code is decisive:

```r
WordListM <- read_csv("73-65full.csv")
...
# Run DISCO for 73 determinatives & 65 pronouns
eqdist.etest(WordListM, sizes=c(73, 65), R=999, method="discoF")
# Rerun DISCO on 73 determinatives split in half
eqdist.etest(WordListM[c(1:73),], sizes=c(35,38), R=999, method="discoF")
```

`sizes=c(73, 65)` means the first 73 data rows are determinatives and the
next 65 are pronouns. `WordListM[c(1:73),]` again treats rows 1-73 as the
determinatives. So the split is positional.

## The local matrix IS the paper's data

`data/reynolds2021_determinative_matrix.csv` has exactly **138 data rows**
(plus a header) -- matching the paper's 73 + 65. Row 73 (data index) is
`various_det`; row 74 is `each_other`. The boundary is clean and matches the
filename `73-65full.csv`. There is no `category`/`class` column in the file;
the assignment is recoverable from row order, with certainty, per the
appendix.

(The matrix has 232 feature columns in the paper's count; the local header
lists fewer named feature columns because the paper groups morphological
"appears-in-word" columns etc. The 138-row form list is what matters here and
it is complete.)

## DETERMINATIVES -- 73 forms (rows 1-73 of the matrix)

a, a_certain, a_few, a_great_many, a_little, all, another, any, anybody,
anyone, anything, anywhere, both, certain, each, either, enough, every,
everybody, everyone, everything, everywhere, few, fewer, fewest, little,
less, least, many, many_a, more, most, much, neither, last, next, no, none,
nobody, no_one, nothing, nowhere, one_det, two_det, three_det, once, twice,
thrice, several, some, somebody, someone, something, somewhere, somewhat,
such, sufficient, that, these, this, those, the, us_det, we_det, you_det,
what_det, whatever_det, which_rel_det, which_int_det, whichever_rel_det,
whichever_int_det, zero_det, various_det

(count = 73)

## PRONOUNS -- 65 forms (rows 74-138 of the matrix)

each_other, one_another, he, him, himself, his, she, her_acc, her_dep, hers,
herself, it_plain, it_dum, its, itself, I, me, mine, my, myself, one_pron,
one_s, oneself, their_sing, theirs_sing, their_plur, theirs_plur, them_sing,
them_plur, themself, themselves, they_sing, they_plur, we_pron, us_pron, our,
ours, ourselves, what_pron, whatever_pron, which_rel_pron, who_int, who_rel,
whom_int, whom_rel, whose_int, whose_rel, whoever, whoever_s, whosever,
whosoever, whosoever_s, you_pron_sing, you_pron_plur, your_sing, yours_sing,
your_plur, yours_plur, yourself, yourselves, today, tomorrow, tonight,
yesterday, there

(count = 65)

## Caveats / notes for the pm

- **Provenance of the local CSV is consistent but not formally verified**
  against the LingBuzz `73-65full.csv` byte-for-byte. The 138-row count, the
  73/65 boundary, the `_det`/`_pron` disambiguation tags, and the appendix
  `sizes=c(73,65)` all line up, so the split above is the paper's split. If
  the pm wants belt-and-suspenders certainty, download `73-65full.csv` from
  https://ling.auf.net/lingbuzz/005747 (LingBuzz "current.file" link;
  WebFetch could not pull the binary directly) and diff its row order against
  the local file.
- These tagged forms reflect Reynolds's deliberate splitting of
  case-syncretic / categorially-ambiguous items into separate rows
  (e.g. `you_det` vs `you_pron_sing`/`you_pron_plur`; `one_det` vs
  `one_pron`; `which_rel_det` vs `which_rel_pron`; `it_plain` vs `it_dum`).
  CGEL's `you`, `we`, `us` are determinatives in this scheme (the personal
  determinatives, as in *you kids*); their pronoun uses are the `_pron` rows.
- The 73/65 labels are the paper's **a priori CGEL categorization**, not the
  clustering result. The k-groups clustering (§3.1) agreed on 129/138 forms
  (93.48%); three determinatives (you, we, us) landed in the pronoun cluster
  and six pronouns (one_another, it, there, what, whatever, which_rel) landed
  in the determinative cluster. For a Phase 3 study using "the 73
  determinatives," use the a priori list above, not the cluster output.

## Verbatim location anchors

- Counts: §2.2 "Preparing the data matrix", p. 8.
- Feature grouping (139 morph / 3 phon / 36 sem / 54 syn = 232), p. 8.
- Data availability: §2.2, p. 8; full reference p. 15 (Reynolds 2021, LingBuzz
  005747).
- Split encoding: Appendix "R Code", p. 16, `sizes=c(73, 65)`.
- Dendrogram (boxed pron/det): Figure 1, p. 10.
- DISCO full-set result (F = 11.670, p = 0.001): Table 2, p. 11.
