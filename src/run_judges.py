"""Phase 3 judge runner (JUDGING.md, frozen). Blind LLM acceptability ratings.

One call per sentence, temperature 0, randomized order (seed 26). The judge sees
ONLY the frozen prompt + the sentence -- never stratum/diagnostic/lexeme. Parses
a single integer 1-7; non-integer/refusal -> retry once -> mark judge-missing
(never imputed, never dropped). Resumable + crash-safe (appends per cell; skips
already-rated cell_ids on re-run). Writes ratings + an A5 manifest.

  python src/run_judges.py --judge fable [--limit N] [--workers N]
  python src/run_judges.py --judge gpt   (needs OPENAI_API_KEY; else skips)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
GRID = os.path.join(RESULTS, "phase3_grid_judgment.csv")
SEED = 26

# FROZEN prompt (JUDGING.md §4; A2 no-examples design). Must match JUDGING.md.
PROMPT = (
    "You are judging the acceptability of English sentences (British English). "
    "Rate how natural and acceptable the following sentence is to a native "
    "speaker, on a scale from 1 to 7, where 1 = completely unacceptable (not a "
    "possible English sentence) and 7 = completely natural (a fully acceptable "
    "English sentence). Some sentences may be unusual or uninformative; judge "
    "only whether the sentence is possible, natural English, not whether it is "
    "likely, sensible, or informative. Reply with a single integer from 1 to 7 "
    "and nothing else.\n\nSentence: {sentence}"
)

FABLE_MODEL = "claude-fable-5"
GPT_MODEL = "gpt-5.5"
MAX_OUT = 1024   # fable-5 is a reasoning model (mandatory thinking); 8 truncates
INT_RE = re.compile(r"[1-7]")


def git_rev():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=ROOT).decode().strip()
    except Exception:
        return "unknown"


def parse_rating(text):
    m = INT_RE.search(text or "")
    return int(m.group()) if m else None


# ---- judge backends: return (rating|None, raw_text, resolved_model) ----------
def make_fable():
    import anthropic
    client = anthropic.Anthropic(max_retries=5)

    def call(sentence):
        # NB: claude-fable-5 DEPRECATES the temperature param -> not sent;
        # the model's default sampling applies (logged deviation, JUDGING.md §6).
        r = client.messages.create(
            model=FABLE_MODEL, max_tokens=MAX_OUT,
            messages=[{"role": "user",
                       "content": PROMPT.format(sentence=sentence)}])
        txt = "".join(b.text for b in r.content if b.type == "text").strip()
        return parse_rating(txt), txt, r.model

    return call, anthropic.__version__, "anthropic"


def make_gpt():
    import openai
    key = os.environ.get("OPENAI_API_KEY")
    if not key:   # fall back to the codex login's stored key
        p = os.path.expanduser("~/.codex/auth.json")
        if os.path.exists(p):
            key = json.load(open(p)).get("OPENAI_API_KEY")
    if not key:
        return None, None, None
    client = openai.OpenAI(api_key=key, max_retries=5)

    def call(sentence):
        # gpt-5.5 is a reasoning model: no temperature; reasoning_effort='none'
        # (snap percept, no reasoning tokens); max_completion_tokens not max_tokens.
        r = client.chat.completions.create(
            model=GPT_MODEL, max_completion_tokens=MAX_OUT,
            reasoning_effort="none",
            messages=[{"role": "user",
                       "content": PROMPT.format(sentence=sentence)}])
        txt = (r.choices[0].message.content or "").strip()
        return parse_rating(txt), txt, r.model

    return call, openai.__version__, "openai"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=["fable", "gpt"], default="fable")
    ap.add_argument("--limit", type=int, default=0, help="smoke-test N cells")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    if args.judge == "fable":
        call, libver, provider = make_fable()
    else:
        call, libver, provider = make_gpt()
        if call is None:
            print("OPENAI_API_KEY unset -- skipping GPT-5.5 (robustness-only; "
                  "run later once the key is present). Logged, not a failure.")
            return

    # cell_id = row index in the grid (matches the gold sample's cell_id)
    cells = []
    with open(GRID) as f:
        for i, row in enumerate(csv.DictReader(f)):
            cells.append({"cell_id": i, "sentence": row["sentence"]})

    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(cells)).tolist()
    present = {cid: pos for pos, cid in enumerate(order, 1)}

    out = os.path.join(RESULTS, f"phase3_ratings_{args.judge}.csv")
    done = set()   # skip only OK cells; re-attempt missing on resume
    if os.path.exists(out):
        with open(out) as f:
            for r in csv.DictReader(f):
                if r.get("status") == "ok":
                    done.add(int(r["cell_id"]))
    # NB: a resumed run may append a fresh row for a previously-missing cell;
    # readers dedup by cell_id keeping status==ok (latest wins).

    todo = [cells[cid] for cid in order if cid not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"judge={args.judge} model={FABLE_MODEL if args.judge=='fable' else GPT_MODEL} "
          f"cells={len(cells)} done={len(done)} to_run={len(todo)} workers={args.workers}")

    cols = ["cell_id", "present_order", "rating", "status", "raw_response"]
    lock = threading.Lock()
    new_file = not os.path.exists(out)
    fh = open(out, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=cols)
    if new_file:
        w.writeheader()
        fh.flush()

    resolved = {"model": None}
    counts = {"ok": 0, "missing": 0}

    def work(cell):
        rating = raw = None
        status = "missing"
        for attempt in (1, 2):                      # retry once
            try:
                rating, raw, model = call(cell["sentence"])
                if resolved["model"] is None and model:
                    resolved["model"] = model
                if rating is not None:
                    status = "ok"
                    break
            except Exception as e:
                raw = f"ERR:{type(e).__name__}:{str(e)[:80]}"
        with lock:
            w.writerow({"cell_id": cell["cell_id"],
                        "present_order": present[cell["cell_id"]],
                        "rating": rating if rating is not None else "",
                        "status": status, "raw_response": raw})
            fh.flush()
            counts[status] += 1
            n = counts["ok"] + counts["missing"]
            if n % 500 == 0:
                print(f"  ...{n}/{len(todo)} (missing={counts['missing']})")

    if todo:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            list(ex.map(work, todo))
    fh.close()

    manifest = {
        "phase": 3, "step": "judging", "judge": args.judge,
        "model_requested": FABLE_MODEL if args.judge == "fable" else GPT_MODEL,
        "model_resolved": resolved["model"], "provider": provider,
        "run_date": datetime.now(timezone.utc).isoformat(),
        "temperature": ("deprecated_model_default" if args.judge == "fable"
                        else "not_sent"),
        "reasoning_effort": (None if args.judge == "fable" else "none"),
        "max_tokens": MAX_OUT, "one_call_per_cell": True,
        "randomization_seed": SEED, "library_version": libver,
        "git_rev": git_rev(), "n_cells": len(cells),
        "n_rated_this_run": counts["ok"], "n_missing_this_run": counts["missing"],
        "prompt": PROMPT, "limit": args.limit or None,
    }
    mpath = os.path.join(RESULTS, f"phase3_ratings_{args.judge}_manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"done: ok={counts['ok']} missing={counts['missing']} "
          f"resolved_model={resolved['model']} -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
