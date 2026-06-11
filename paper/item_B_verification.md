# Item B — diagnostics.yaml `source:` verification (complete)

TO_VERIFY item B / F5 battery gate. Protocol (pm-tightened 2026-06-10): each row
carries the **verbatim source sentence** + **pinpoint** so the pm confirms
against quoted text, not paraphrase. Full verbatim quotes (with page/line) live
in `intake/` (cgel-diagnostic-criteria.md, maling-1983-quotes.md,
matthews_2014_quotes.md, aarts2007_verbatim_quotes.md). CGEL = Huddleston &
Pullum 2002 (line numbers in `literature/00-CGEL.md`); ch.7 lists [9] (§2,
l.18452) and [11] (§2.2, l.~18550) source most A/P rows. Aarts 2007 §8.4.4 adopts
the **same** A/P battery (explicitly "Huddleston and Pullum et al. (2002: 606)",
intake/aarts l.542), so it independently corroborates the battery.

Status: ✅ sourced (verbatim+pinpoint) · ⚠ flag (mis-/un-sourced) · ✋ pm/Matthews.

## Degree & comparison
- **very_mod** ✅ CGEL ch.7 §2.2 [11]iii: "Central adjectives accept *very* and *too* as degree modifiers… in general, prepositions do not." Corrob. Aarts §8.4.1 p3, §8.4.4.
- **too_mod** ✅ same sentence ([11]iii).
- **comparative_more** ✅ [11]iii ("…inflectional or analytic comparatives and superlatives; in general, prepositions do not").
- **inflectional_comparison** ✅ [11]iii + **Maling p.270**: "It takes a synthetic comparative and superlative…" (near/nearer/nearest as adjectival evidence; table (45) p.273). yaml's "near" cue confirmed.
- **well_mod** ⚠ **NO VALID SOURCE.** Maling has no *well worth* test (intake/maling Target 2 = NOT FOUND); CGEL [9]iii/[11]v cite *right*/*straight*, never *well*. diagnostics.yaml credits "Maling 1983; CGEL" — both wrong for *well*. **pm: drop the row, or supply a source.**
- **right_mod** ✅ CGEL ch.7 §2 [9]iii: "A subset of prepositions are distinguished by their acceptance of such adverbs as *right* and *straight* as modifiers"; [11]v. **Maling p.262**: "certain specifiers such as *right* are good" (ex.20). (*straight*: in CGEL/Aarts, not Maling.)

## Complementation
- **np_complement** ✅ CGEL ch.7 §2.2 [11]iv ("Central prepositions license NP complements; in general, adjectives do not") + §2.1 ("only four adjectives [take NP complements], namely *worth*, *due*, *like*, and *unlike*"). **Maling pp.253–254** (transitive adjectives = *like, worth, near*). NB Maling's set (3) ≠ CGEL's (4: worth/due/like/unlike) — *near* is Maling-only, *due/unlike* CGEL-only.
- **gerund_gap_complement** ⚠ **RE-SOURCE.** Mis-attributed to Maling (intake/maling Target 5 = NOT FOUND). Trace to **CGEL "hollow clauses", l.1935**: "This idea is *worth* [giving some thought to]". yaml should read CGEL, not Maling.
- **that_clause_complement** ✅ CGEL ch.7 §2 [9]i + (b): "Declarative content clauses are non-expandable if they do not permit the subordinator *that*. Almost all words that license complements of this kind are prepositions…" (note: CGEL frames this as preposition-distinguishing; reconcile with yaml's {adj:partial,prep:partial}).

## Function & position
- **attributive** ✅ **Matthews 2014 p.3**: "By the attributive position we mean that of a premodifier…"; p.23 "a modifier in the attributive position… by which adjectives are most clearly distinguished." CGEL ch.6 §2 [1] (attributive/predicative/postpositive); Aarts p1.
- **predicative_be** ✅ CGEL ch.6 §2.1 l.16113: "Predicative complements are dependents in clause structure, licensed by particular verbs, such as intransitive *be* and *seem*…" — but l.16161 caveat: "*be* allows such a wide range of complements that its value as a diagnostic is quite limited." (Worth noting in the paper.)
- **postpositive** ✅ **Matthews 2014 p.10** (the "three positions"… postpositive as a third main function, citing H&P 2002:528); pp.12–13 (postpositive-only: *elect, proper*); p.54 (*the parliamentarians present*).
- **predeterminer_position** ✅ CGEL ch.5 §2 l.9947: "A predeterminer modifier normally precedes a determiner…"; §6 l.11415 (All/Both as determiner vs predeterminer, "All/Both the students").
- **determiner_function** ✅ CGEL ch.5 §2 l.10800: "We distinguish… between the concepts of determiner, a function in the structure of the NP, and determinative, a category of words…".
- **fused_head** ✅ CGEL ch.5 §9.1 l.12393: "Fused-head NPs are those where the head is combined with a dependent function that in ordinary NPs is adjacent to the head, usually determiner or internal modifier" (ex. "Did you buy [some] yesterday?").
- **partitive_of** ✅ CGEL ch.5 §2 l.10044 (partitive fused-head, "most of the boys"); §3.3 l.10555 (of obligatory: "[Many of the delegates]" vs *"[Many of delegates]").

## Morphology
- **un_prefix** ✅ but **CGEL ch.19 §5.5.1 l.51004** (NOT ch.6): "*In·* and *un·*… attach primarily to adjectives." Aarts p5. **Update yaml source ch. ref.**
- **ly_adverb_base** ✅ CGEL ch.6 §5.2 l.17309: "A very high proportion of adverbs are formed from adjectives by suffixation of *·ly*."
- **ness_nominalization** ✅ but **CGEL ch.19 §5.1.1 l.50449** (NOT ch.6): "Adding *·ness* to an adjective… changes it into a noun…". **Update yaml source ch. ref.**

## Clause-level & other
- **seem_complement** ✅ CGEL ch.6 §2.1 l.16161: "…*become* and *make*, and to a lesser extent *seem*, appear, feel, look, sound, which take a more restricted range of complements… largely exclude PP complements" (ex. "They all seem content" / *"They all seem outside").
- **become_complement** ✅ CGEL ch.7 §2.2 [11]ii: "AdjPs, other than those restricted to attributive or postpositive function, can mostly occur as complement to *become*; in general, PPs cannot." Aarts §8.4.4.
- **coordination_with_adj** ⚠ **TO LOCATE.** yaml = "standard coordination diagnostic; locate canonical statement." Not in the CGEL ch.5/6/7/19 or Maling/Matthews/Aarts extracts pulled. Next pass: CGEL ch.15 (coordination) like-category constraint. Currently unsourced.
- **fronting_pp** ✅ CGEL ch.7 §2.2 [11]vi: "Prepositions taking NP complements can normally be fronted along with their complement in relative and interrogative constructions… in general, adjectives cannot." (info-packaging cross-ref Ch.16 still to add.)
- **stranding** ✅ [11]vi (above) + CGEL ch.7 §4.1 stranding (l.18423).

## Summary for pm
- **22 / 24 diagnostics sourced** verbatim + pinpoint (CGEL chs 5/6/7/19, Maling, Matthews; Aarts corroborates the A/P battery).
- **2 flags need a pm/executor decision:** `well_mod` (no valid source — drop or supply) and `coordination_with_adj` (locate in CGEL ch.15).
- **2 yaml `source:` corrections:** `gerund_gap_complement` → CGEL hollow clauses (not Maling); `un_prefix`/`ness_nominalization` → CGEL **ch.19** (not ch.6).
- **Candidate battery addition (Maling p.263–265; Aarts §8.4.4):** the *enough*-position test — Maling's one "purely syntactic" A/P diagnostic ("*enough* follows adjectives, but precedes prepositions"). pm decision (F5: battery expansion is pm-gated).
- Once pm confirms these rows + resolves the 2 flags, **F5 battery gate clears** → instantiation unblocks.
