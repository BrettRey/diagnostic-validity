# CLAUDE.md — diagnostic-validity

You are the executor (claude-code:diagnostic-validity). The pm node is
Brett + Claude chat. PLAN.md governs; this file governs how you work.

## Non-negotiable rules

1. SOURCE-GROUNDING LAW. If a fact should come from a source, read the
   source first. Never generate citations, page numbers, statistics,
   linguistic data, or attributed claims from memory. If you cannot read
   the source, write the claim with a ⟨VERIFY⟩ marker and add it to
   paper/TO_VERIFY.md. Never invent BibTeX entries; references.bib is
   pm-node-only.
2. NO FABRICATED NUMBERS. Every empirical number in any draft text must
   be traceable to a file in results/ with a manifest. Unknown = ⟨RESULT⟩.
3. GOLDEN NUMBERS. Run `python -m pytest tests/ -q` before and after any
   change to src/. If GOLDEN.md values stop reproducing, stop work and
   post a pm-update; do not "fix" tests to match new output.
4. OUTCOME NEUTRALITY. Do not edit paper/main.tex §1–2 to favour a result
   after results exist (PLAN.md §5).
5. Truncated fetches: if any download or URL fetch is truncated, flag it
   immediately; never analyze partial data silently.

## House style (paper text)

- LaTeX; biblatex-APA. Linguistic objects in \textit{}; single quotes
  only for meanings ('definite'); \enquote{} otherwise.
- En-dash with spaces for parentheticals (~-- like this~--), never
  em-dash. Oxford spelling (-ize). Contractions fine. Metric units.
- Paragraphs ~60 words, max 100. No throat-clearing. Concrete before
  abstract. Parentheses for asides; dashes only for emphasis.
- CGEL terminology strictly: determinative = category, determiner =
  function; no movement metaphors; generative accounts mentioned briefly
  for contrast only.
- Unpack PROJECTIBILITY on first use; do not headline HPC theory — the
  paper's frame is category stability and inference.

## Workflow protocol

- Check shared-memory at session start; log completions/blockers/decisions
  with "pm-update" tag; post a session summary before closing; auto-act
  on PM directives.
- Each phase emits structured outputs (CSV + a short findings .md), not
  interpretive prose. Interpretation is pm-node work.
- Commit small; manifest every run (data hash, seed, params, git rev) to
  results/manifest_*.json.

## Repo map

- PLAN.md           design contract (read first, every session)
- diagnostics.yaml  the diagnostic battery (items for the Phase 3 grid)
- src/synth.py      synthetic matrices with planted structure
- src/models.py     low-rank logistic model; sparse pairwise network;
                    CV comparison; projectibility; misfit
- src/pipeline.py   end-to-end runner (synthetic now; point at real data
                    in Phase 1)
- tests/            recovery tests backing GOLDEN.md
- paper/            main.tex (§1–2 drafted), references.bib (verified
                    entries only), TO_VERIFY.md
- results/          run outputs + manifests (gitignored except findings)
