# Literature-intake HANDOFF (2026-06-10, pre-reset)

Resume point for the next session. Five source extracts (verbatim quotes +
pinpoints) are saved in this `intake/` dir; the assembly into item B +
TO_VERIFY is NOT yet done — that is the first task on resume.

## Source extracts saved (verbatim, in intake/)
- `maling-1983-quotes.md` — Maling 1983 (scanned PDF, read visually)
- `matthews_2014_quotes.md` — Matthews 2014
- `aarts2007_verbatim_quotes.md` — Aarts 2007 (local .md, Chs 7-8 only)
- `cgel-diagnostic-criteria.md` — CGEL ch.5/6 (+ ch.19) criteria
- `sprouse_replication_rates.md` — Sprouse&Almeida 2012 / SS&A 2013

## KEY FINDINGS (do not lose — these are the value of the pass)

1. **Two mis-attributed `source:` fields in diagnostics.yaml** (firewall catch):
   - `well_mod`: Maling has NO "well worth" test; CGEL cites *right*/*straight*,
     never *well*. The *well* degree test currently has **no valid source** —
     pm decision: drop it or find a source.
   - `gerund_gap_complement`: not in Maling; traces to CGEL "hollow clauses"
     (00-CGEL.md l.1935, "This idea is worth [giving some thought to]"), not
     Maling. Re-source to CGEL.

2. **worth/near contradiction (citable; strengthens §2.1):**
   - Maling 1983: *worth* = completed reanalysis to **preposition** (p.269,
     "well-behaved preposition"); *near* = **adjective** ("the only surviving
     relic of the class of transitive adjectives", p.266). Her transitive
     adjectives = *like, worth, near* only (p.254).
   - CGEL ch.7 §2.2: *worth* = **adjective** ("the case… is strong"); *near*
     = **preposition** (list [27]).
   - i.e. Maling and CGEL invert each other on both items.

3. **⚠ §1 mischaracterizes Aarts (pm to fix, outcome-neutral intro):** §1 says
   Aarts "defends graded membership." Aarts EXPLICITLY REJECTS fuzzy/graded
   class *membership* (Zadeh, aarts2007.md line 350); his view = subsective
   gradience (graded prototypicality within SHARP boundaries) + intersective
   gradience (property-set overlap). Change "graded membership" →
   "subsective gradience / graded prototypicality". The RQ4 prediction
   mapping (subsective → low-rank graded scores) is fine.

4. **⚠ Item C: §2.1 "diagnostics have drifted" NOT supported by Matthews 2014
   (pm to soften/re-attribute):** Matthews's "drift" = Sapir's drift of the
   *language* (attributive vs predicative uses diverging, p.173), NOT linguists
   reweighting diagnostics. Milder claims he DOES support: one-time retreat
   from necessary-and-sufficient to "cluster of syntactic properties" (p.21);
   positional criteria give fuzzy boundaries, "evidence may be less than
   decisive" (p.24).

5. **Item 5 resolved (exact, for bib promotion):**
   - Sprouse & Almeida 2012, *J. Linguistics* 48(3):609-652, DOI
     10.1017/S0022226712000011 — **98% min replication**, 0 sign-reversals
     (Adger Core Syntax; 469 pts/365 phenomena).
   - Sprouse, Schütze & Almeida 2013, *Lingua* 134:219-248, DOI
     10.1016/j.lingua.2013.07.002 — **95% convergence** (86-99%) (LI 2001-2010
     random sample; 296 pts/148 phenomena). Different construct from the 98%;
     don't merge.

6. **CGEL ch.5/6 rows: all 9 found verbatim** (see cgel-diagnostic-criteria.md).
   Chapter flags: `un_prefix` + `ness_nominalization` are CGEL **ch.19**
   §5.5.1 (l.51004) / §5.1.1 (l.50449), NOT ch.6; `ly_adverb_base` = ch.6 §5.2
   (l.17309). predeterminer/determiner/fused-head/partitive (ch.5),
   predicative/seem (ch.6) all sourced.

7. **`attributive` + `postpositive` sourced** from Matthews 2014 (pp.2-3, 10,
   12-13, 23-24).

8. **`enough`-position test**: Maling's one "purely syntactic" A/P diagnostic
   (pp.263, 265); also in Aarts/CGEL battery. Candidate battery addition (pm).

## NEXT STEPS (on resume)
1. Read the 5 intake/ files; assemble `paper/item_B_cgel_verification.md`
   into the full item-B table (rename to item_B_verification.md — multi-source
   now), every diagnostic row with verbatim + pinpoint.
2. Update TO_VERIFY: resolve item B (incl. the two mis-attribution flags),
   item C (Matthews softening), item 5 (Sprouse numbers + cites); cross-ref
   item A (worth/near both sides now sourced); add the §1-Aarts flag.
3. pm decisions queued: §1 Aarts wording; §2.1 Matthews + worth/near; `well_mod`
   source; `enough`-test addition; promote Sprouse/Maling/Matthews/Aarts cites
   to references.bib (Maling/Matthews/Aarts already in central? check).
4. STILL PENDING from before this intake:
   - Two data files for the F4 sampler → `data/`: SUBTLEX-UK (Zipf+PoS) and the
     Reynolds 2021 determinative matrix CSV (73 dets). Both must be dropped by
     pm (not scriptable). Then run `src/run_phase1.py`-style F4 sampler.
   - Web methods intake cluster (NOT in Mendeley): Marsman 2018 (§2.2
     equivalence scope, item 3), Angelopoulos/PPI (item 6), Egami/DSL (item 7),
     Warstadt/CoLA (item 8), van der Maas 2006 (item 12), Borsboom&Cramer 2013
     (item 4). Dispatch as web-subagent fan-out.

## Build status recap (committed)
Phase 1 pilot done + GO; Phase 3 frame frozen (DECISIONS F1-F7 + amendments);
prepositions stratum done (sampling/prepositions_cgel_ch7.csv, 168);
item A (worth) resolved; item-B CGEL rows partly drafted in
paper/item_B_cgel_verification.md. Latest commit before this handoff: b6361c5.
