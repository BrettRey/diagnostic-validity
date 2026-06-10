# diagnostic-validity

*Do categorial diagnostics measure anything? A psychometric study of
English lexical categories.* Target: Language.

Phase 0 bundle, produced in chat (pm node). Start here:

1. PLAN.md   — design contract: estimands, models, go/no-go, phases
2. CLAUDE.md — executor rules: source-grounding law, golden numbers,
               house style
3. GOLDEN.md — reproducibility anchors; verify before any new analysis

Quick start (executor):

    pip install numpy scikit-learn pytest
    python -m pytest tests/ -q          # 4 tests must pass
    python src/pipeline.py --demo reflective --seed 7
    python src/pipeline.py --demo network --seed 7
    # compare output to GOLDEN.md, then begin Phase 1 (PLAN.md section 6)

Phase 1 task in one line: fetch MegaAcceptability v2 (megaattitude.io),
dichotomize per PLAN.md section 3, run src/pipeline.py --input on it,
emit results/pilot_findings.md + CSVs, post pm-update. No prose
interpretation; no new citations (use paper/TO_VERIFY.md).
