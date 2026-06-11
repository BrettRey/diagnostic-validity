"""Phase 3 instantiation (F5) + gold draw (F6). Seed 26.

Turns the 526-lexeme sample x the 24 CONFIRMED judgment diagnostics into bleached
test sentences, via a template-exception table (never silent hand-edits). Then,
in the rigid F6 order, draws the 600-cell gold sample BEFORE any rating exists.
well_mod + that_clause_complement instantiate LATE (appended columns, per the gate
ruling), so they are excluded here.

Outputs (results/):
  phase3_grid_judgment.csv      every (lexeme, diagnostic) cell + sentence + flags
  phase3_template_exceptions.md  the documented exception table (built, not silent)
  phase3_eyeball_50.csv          50 random cells for the pm eyeball
  phase3_gold_sample.csv         600 cells, uniform, inclusion prob stored (F6)
  phase3_instantiate_manifest.json

Run from repo root:  python src/instantiate_phase3.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(__file__))
import pipeline  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
SEED = 26
GOLD_N = 600
EYEBALL_N = 50

SAMPLE = os.path.join(RESULTS, "phase3_sample.csv")
DIAG = os.path.join(ROOT, "diagnostics.yaml")

# Instantiate-late (not gates): appended after their resolution.
DEFER = {"well_mod", "that_clause_complement"}

# Decision 2 (2026-06-11): charitable realization. The instantiator makes
# SPELLING decisions, never acceptability decisions: realize every cell with
# the lexeme's most charitable well-formed candidate and let raters judge
# (worther/beautifuller being rated bad IS the datum). Suppletive lookups +
# orthographic rules are logged dictionary facts (template-exception file).
SUPPLETIVE_COMPARATIVE = {"good": "better", "bad": "worse", "far": "further",
                          "little": "less", "well": "better"}
IRREGULAR_LY = {"true": "truly", "due": "duly", "whole": "wholly",
                "full": "fully"}


def _syllables(w):
    return len(re.findall(r"[aeiouy]+", w))


def reg_er(w):
    """Regular synthetic comparative orthography."""
    if " " in w:
        return w + "er"                          # multiword: garbage-is-data
    if w.endswith("e"):
        return w + "r"                           # nice->nicer, large->larger
    if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
        return w[:-1] + "ier"                    # happy->happier
    if w.endswith("l") and len(w) > 2 and w[-2] in "aeiou" and w[-3] not in "aeiou":
        return w + "ler"                         # British -l doubling: cruel->crueller
    if (len(w) >= 3 and w[-1] not in "aeiouwxy" and w[-2] in "aeiou"
            and w[-3] not in "aeiou" and _syllables(w) == 1):
        return w + w[-1] + "er"                  # big->bigger (CVC monosyll)
    return w + "er"                              # worth->worther (badness=datum)


def comparative(w):
    return SUPPLETIVE_COMPARATIVE.get(w, reg_er(w))


def reg_ly(w):
    if w in IRREGULAR_LY:
        return IRREGULAR_LY[w]
    if w.endswith("ic"):
        return w + "ally"                        # basic->basically
    if w.endswith("le") and len(w) > 2 and w[-3] not in "aeiou":
        return w[:-1] + "y"                      # gentle->gently, able->ably
    if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
        return w[:-1] + "ily"                    # happy->happily
    if w.endswith("ll"):
        return w + "y"                           # dull->dully
    return w + "ly"                              # worth->worthly (datum)


def reg_ness(w):
    if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
        return w[:-1] + "iness"                  # happy->happiness
    return w + "ness"


def reg_un(w):
    return "un" + w                              # un+stem; unnear (datum)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git_rev():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=ROOT).decode().strip()
    except Exception:
        return "unknown"


def drop_optional(frame):
    """Remove optional ' (something)'-type parentheticals; tidy spaces."""
    s = re.sub(r"\s*\([^)]*\)", "", frame)
    return re.sub(r"\s+", " ", s).strip()


def instantiate(diag, surface):
    """Return (sentence, flag, needs_realization) for one cell."""
    did = diag["id"]
    frame = diag["frame"]

    # morphology: realize the charitable well-formed candidate (spelling only,
    # never acceptability). Suppletive where attested, else orthographic rules.
    if did == "inflectional_comparison":
        return (frame.replace("LEX-er", comparative(surface)),
                "realized:comparative", "")
    if did == "ly_adverb_base":
        return frame.replace("LEXly", reg_ly(surface)), "realized:ly", ""
    if did == "ness_nominalization":
        return frame.replace("LEXness", reg_ness(surface)), "realized:ness", ""
    if did == "un_prefix":
        return frame.replace("unLEX", reg_un(surface)), "realized:un", ""

    # postpositive: pm note-form ('the something LEX')
    if did == "postpositive":
        return f"The something {surface} happened.", "note_postpositive", ""

    # enough items: collide when the lexeme under test IS 'enough'
    if did in ("enough_postposed", "enough_preposed"):
        sent = drop_optional(frame).replace("LEX", surface)
        flag = "collision_enough" if surface.lower() == "enough" else ""
        return sent, flag, ""

    # standard: drop optional complement, substitute the surface form
    return drop_optional(frame).replace("LEX", surface), "", ""


def main():
    diags = [d for d in yaml.safe_load(open(DIAG))["diagnostics"]
             if d["id"] not in DEFER]
    assert len(diags) == 24, f"expected 24 confirmed items, got {len(diags)}"

    lexemes = list(csv.DictReader(open(SAMPLE)))
    cells = []
    for lx in lexemes:
        surface = lx["lexeme"]
        for d in diags:
            sent, flag, need = instantiate(d, surface)
            sent = sent[0].upper() + sent[1:] if sent else sent  # sentence case
            cells.append({
                "lexeme": surface, "stratum": lx["stratum"],
                "det_flag": lx.get("det_flag", ""), "diagnostic": d["id"],
                "op": d["op"], "sentence": sent, "flag": flag,
                "needs_realization": need,
            })

    os.makedirs(RESULTS, exist_ok=True)
    cols = ["lexeme", "stratum", "det_flag", "diagnostic", "op",
            "sentence", "flag", "needs_realization"]
    with open(os.path.join(RESULTS, "phase3_grid_judgment.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(cells)

    # tallies
    n = len(cells)
    by_flag, by_need, by_diag = {}, {}, {}
    for c in cells:
        if c["flag"]:
            by_flag[c["flag"]] = by_flag.get(c["flag"], 0) + 1
        if c["needs_realization"]:
            by_need[c["needs_realization"]] = \
                by_need.get(c["needs_realization"], 0) + 1

    # ---- F6: gold BEFORE any rating. Uniform; inclusion prob stored. -----
    rng = np.random.default_rng(SEED)
    gold_idx = sorted(rng.choice(n, size=GOLD_N, replace=False).tolist())
    incl_p = GOLD_N / n
    gcols = ["cell_id"] + cols + ["inclusion_prob"]
    with open(os.path.join(RESULTS, "phase3_gold_sample.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=gcols)
        w.writeheader()
        for i in gold_idx:
            w.writerow({"cell_id": i, **cells[i],
                        "inclusion_prob": round(incl_p, 6)})

    # eyeball: a second independent draw (same rng stream), for pm inspection
    eye_idx = sorted(rng.choice(n, size=EYEBALL_N, replace=False).tolist())
    with open(os.path.join(RESULTS, "phase3_eyeball_50.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=["cell_id"] + cols)
        w.writeheader()
        for i in eye_idx:
            w.writerow({"cell_id": i, **cells[i]})

    # ---- template-exception table (documented, not silent) --------------
    smani = json.load(open(os.path.join(RESULTS,
                      "phase3_sample_manifest.json")))
    conv = smani.get("determinative_surface_conversions", {})
    multiword = {k: v for k, v in conv.items() if " " in v}
    ex = os.path.join(RESULTS, "phase3_template_exceptions.md")
    with open(ex, "w") as f:
        f.write("# Phase 3 template-exception table (instantiation)\n\n")
        f.write("Built per diagnostics.yaml `notes` -- every non-trivial "
                "transformation is documented here, never silently hand-edited. "
                f"Grid = {len(lexemes)} lexemes x {len(diags)} confirmed "
                f"judgment diagnostics = {n} cells. well_mod + "
                "that_clause_complement instantiate late (appended), not here.\n\n")
        f.write("## Morphology realization (spelling, never acceptability)\n")
        f.write("Every cell is realized with the lexeme's most charitable "
                "well-formed candidate; raters judge it. *worther*/*beautifuller* "
                "rated bad IS the datum (that the base fails synthetic comparison; "
                "the periphrastic escape is the separate comparative_more item). "
                "The instantiator makes spelling decisions only -- it never marks "
                "a cell non-applicable (that would smuggle the verdict into the "
                "template). Counts: "
                f"comparative {by_flag.get('realized:comparative',0)}, "
                f"-ly {by_flag.get('realized:ly',0)}, "
                f"-ness {by_flag.get('realized:ness',0)}, "
                f"un- {by_flag.get('realized:un',0)} cells (all lexemes).\n\n")
        f.write("Logged dictionary facts + orthographic rules:\n")
        f.write(f"- Suppletive comparatives: {SUPPLETIVE_COMPARATIVE} "
                "(e.g. good->better, never *gooder).\n")
        f.write("- Regular comparative: e->+r (nice->nicer); y->ier "
                "(happy->happier); CVC monosyllable doubles (big->bigger); "
                "else +er (worth->worther).\n")
        f.write(f"- Irregular -ly: {IRREGULAR_LY}; -ic->-ically; -le->-ly "
                "(gentle->gently); y->ily (happy->happily); else +ly.\n")
        f.write("- -ness: y->iness (happy->happiness); else +ness.\n")
        f.write("- un-: un+stem, no stem change (unhappy, unnear). Hyphenation "
                "(un-X vs unX) and off-category strings (*unnear*, *una few*) "
                "stand as garbage-is-data.\n")
        f.write("\n## enough collision\n")
        f.write(f"`enough_postposed`/`enough_preposed` x lexeme *enough*: "
                f"{by_flag.get('collision_enough',0)} cells ('enough enough'), "
                "flagged not hand-edited (pm ruling).\n")
        f.write("\n## postpositive note-form\n")
        f.write(f"`postpositive`: {sum(1 for c in cells if c['diagnostic']=='postpositive')} "
                "cells instantiated as 'The something LEX happened.' per the "
                "diagnostics.yaml note (not the bare frame).\n")
        f.write("\n## optional complements\n")
        f.write("Frames with '(something)' optional complements (very_mod, "
                "too_mod, comparative_more, right_mod, enough_preposed, "
                "seem_complement, become_complement, coordination_with_adj) are "
                "instantiated WITHOUT the optional, to test the target operator "
                "cleanly (avoids confounding with np_complement).\n")
        f.write("\n## determinative underscore->space (from the sample stage)\n")
        f.write("Multiword determinative labels convert underscore->space at the "
                "sample stage (logged in phase3_sample_manifest.json); they "
                "instantiate as multiword surfaces, and morphological frames over "
                "them produce garbage-is-data:\n")
        for k, v in sorted(multiword.items()):
            f.write(f"- `{k}` -> *{v}*\n")

    manifest = {
        "phase": 3, "step": "F5 instantiation + F6 gold",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "git_rev": git_rev(), "versions": pipeline._versions(),
        "frames": {"sample": {"path": os.path.relpath(SAMPLE, ROOT),
                              "sha256": sha256(SAMPLE)},
                   "diagnostics": {"path": os.path.relpath(DIAG, ROOT),
                                   "sha256": sha256(DIAG)}},
        "n_lexemes": len(lexemes), "n_diagnostics": len(diags),
        "deferred_diagnostics": sorted(DEFER),
        "n_cells": n, "cells_by_flag": by_flag,
        "gold": {"n": GOLD_N, "pool": n, "inclusion_prob": incl_p,
                 "seed": SEED, "uniform": True,
                 "note": "Drawn BEFORE any rating (F6). All cells are realized "
                         "strings (charity = spelling, not acceptability); "
                         "gold-before-judge preserved (no judging yet)."},
        "eyeball": {"n": EYEBALL_N, "seed": SEED,
                    "note": "second draw from the seed-26 stream after gold"},
    }
    with open(os.path.join(RESULTS, "phase3_instantiate_manifest.json"),
              "w") as f:
        json.dump(manifest, f, indent=2)

    print("Instantiated %d cells (%d lexemes x %d diagnostics)."
          % (n, len(lexemes), len(diags)))
    print("Flags:", by_flag)
    print("Gold: %d cells, uniform, inclusion_prob %.5f (seed %d)."
          % (GOLD_N, incl_p, SEED))
    print("Eyeball: %d cells -> results/phase3_eyeball_50.csv" % EYEBALL_N)


if __name__ == "__main__":
    main()
