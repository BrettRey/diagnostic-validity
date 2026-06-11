"""Generate the external acceptability-rating app: one self-contained HTML file.

Runs by double-click (file://) or hosted on the web -- identical. No server, no
Python for the rater. Each rater types their initials (responses stay distinct,
saved under that id + downloaded as a distinctly-named JSON). Blind, one sentence
at a time, no back button, keystroke/click rating, dialect + unsure flags,
resumable (localStorage), seeded per-rater shuffle. Instruction = the frozen §4
prompt verbatim, reply-line adapted to the interface (A4 construct invariant).

Default build = the 200-cell kappa subset of the gold (so external raters overlap
Brett's gold -> kappa vs Brett + the external check on the compression) + warm-up
(non-gold, discarded) + repeats (intra-rater test-retest).

  python src/build_rater_app.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import run_judges  # frozen PROMPT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
OUTDIR = os.path.join(ROOT, "rater_app")
SEED = 26
N_KAPPA, N_WARMUP, N_REPEAT = 200, 10, 20
SETNAME = "kappa200"

INSTR = (run_judges.PROMPT.split("\n\nSentence:")[0].replace(
    "Reply with a single integer from 1 to 7 and nothing else.",
    "For each sentence, give a single rating from 1 to 7."))

TEMPLATE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acceptability rating</title>
<style>
 body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;max-width:720px;margin:0 auto;padding:24px;color:#222;line-height:1.45}
 h2{font-weight:600}
 .sentence{font-size:1.55em;text-align:center;margin:46px 0;min-height:2.2em;display:flex;align-items:center;justify-content:center}
 .scale{display:flex;justify-content:space-between;gap:6px;margin:18px 0}
 .scale button{flex:1;padding:16px 0;font-size:1.2em;border:1px solid #aaa;background:#f7f7f7;border-radius:8px;cursor:pointer}
 .scale button:hover{background:#e6f0ff}
 .scale button.sel{background:#3a7bd5;color:#fff;border-color:#3a7bd5}
 .ends{display:flex;justify-content:space-between;font-size:.82em;color:#666}
 .flags{margin:18px 0;color:#444}.flags label{margin-right:20px;cursor:pointer}
 .bar{height:6px;background:#eee;border-radius:3px;overflow:hidden;margin:8px 0 18px}
 .bar>div{height:100%;background:#3a7bd5}
 button.primary{padding:12px 26px;font-size:1em;background:#3a7bd5;color:#fff;border:none;border-radius:8px;cursor:pointer}
 button.primary:disabled{background:#bbb;cursor:default}
 input[type=text]{padding:10px;font-size:1em;width:260px}
 .instr{white-space:pre-wrap;background:#f7f7f7;padding:18px;border-radius:8px}
 .muted{color:#888;font-size:.9em}
 a.link{color:#3a7bd5;font-size:.85em;cursor:pointer}
</style></head><body><div id="app"></div>
<script>
const WARMUP=__WARMUP__, SCORED=__SCORED__, INSTR=__INSTR__, SETNAME=__SET__, NWARM=WARMUP.length;
const app=document.getElementById('app'), $=id=>document.getElementById(id);
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function mb32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function shuffle(arr,seed){const r=mb32(seed||1),a=arr.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
let rater='',seq=[],idx=0,resp={},cur={};
const lskey=()=>'acc_'+SETNAME+'_'+rater;
function persist(){try{localStorage.setItem(lskey(),JSON.stringify({idx,resp}))}catch(e){}}
function restore(){try{const d=localStorage.getItem(lskey());if(d){const o=JSON.parse(d);idx=o.idx;resp=o.resp;return true}}catch(e){}return false}
function buildSeq(){seq=WARMUP.concat(shuffle(SCORED,hash(rater)))}

function nameScreen(){app.innerHTML=`<h2>Acceptability rating</h2>
 <p>Please enter your name or initials, so your answers stay separate from anyone else's using this app:</p>
 <p><input type="text" id="rid" placeholder="e.g. GKP" autofocus></p>
 <p><button class="primary" id="go">Begin</button></p>
 <p class="muted">Your answers are saved in this browser as you go (you can close and come back), and you download them at the end.</p>`;
 $('go').onclick=begin; $('rid').onkeydown=e=>{if(e.key==='Enter')begin()};}
function begin(){const v=$('rid').value.trim();if(!v)return;rater=v;buildSeq();restore();instrScreen();}

function instrScreen(){app.innerHTML=`<h2>Instructions</h2><div class="instr">${INSTR}</div>
 <ul><li>Go with your <b>first reaction</b> — about 5–10 seconds per sentence.</li>
 <li>Rate whether it's <b>possible, natural English</b>, not whether it's likely or sensible.</li>
 <li>Please don't look anything up. There's <b>no back button</b>; give one number for every sentence.</li></ul>
 <p><button class="primary" id="start">${idx>NWARM?'Resume':'Start'} (${seq.length-idx} left)</button></p>`;
 $('start').onclick=rateScreen;}

function rateScreen(){document.onkeydown=null;
 if(idx>=seq.length)return doneScreen();
 const it=seq[idx];cur={rating:null,v:0,u:0};const warm=it.type==='warmup';
 app.innerHTML=`<div class="muted">${warm?'Warm-up (not scored)':'Sentence '+(idx-NWARM+1)+' of '+(seq.length-NWARM)}</div>
  <div class="bar"><div style="width:${100*idx/seq.length}%"></div></div>
  <div class="sentence"></div>
  <div class="scale">${[1,2,3,4,5,6,7].map(n=>`<button data-n="${n}">${n}</button>`).join('')}</div>
  <div class="ends"><span>1 = completely unacceptable</span><span>7 = completely natural</span></div>
  <div class="flags"><label><input type="checkbox" id="fv"> doesn't match my dialect</label>
   <label><input type="checkbox" id="fu"> unsure</label></div>
  <p><button class="primary" id="next" disabled>Next &rarr;</button>
   &nbsp;&nbsp;<a class="link" id="save">save &amp; download progress</a></p>`;
 document.querySelector('.sentence').textContent=it.s;
 document.querySelectorAll('.scale button').forEach(b=>b.onclick=()=>pick(+b.dataset.n));
 $('fv').onchange=e=>cur.v=e.target.checked?1:0;
 $('fu').onchange=e=>cur.u=e.target.checked?1:0;
 $('next').onclick=advance; $('save').onclick=download;
 document.onkeydown=e=>{
   if(e.key>='1'&&e.key<='7'){pick(+e.key)}
   else if(e.key==='v'){$('fv').checked=!$('fv').checked;cur.v=$('fv').checked?1:0}
   else if(e.key==='u'){$('fu').checked=!$('fu').checked;cur.u=$('fu').checked?1:0}
   else if((e.key==='Enter'||e.key===' ')&&!$('next').disabled){e.preventDefault();advance()}};}
function pick(n){cur.rating=n;document.querySelectorAll('.scale button').forEach(b=>b.classList.toggle('sel',+b.dataset.n===n));$('next').disabled=false;}

function advance(){const it=seq[idx];
 resp[idx]={cell_id:it.id,type:it.type,presented_index:idx,rating:cur.rating,variety:cur.v,unsure:cur.u,ts:new Date().toISOString()};
 idx++;persist();rateScreen();}

function doneScreen(){document.onkeydown=null;app.innerHTML=`<h2>Done — thank you!</h2>
 <p>Please download your responses and email the file to Brett.</p>
 <p><button class="primary" id="dl">Download my responses</button></p>
 <p class="muted">If the download didn't start, your answers are still saved here; reopen and click Download.</p>`;
 $('dl').onclick=download;}

function download(){const out={rater,set:SETNAME,saved:new Date().toISOString(),n_done:Object.keys(resp).length,responses:Object.values(resp)};
 const blob=new Blob([JSON.stringify(out,null,1)],{type:'application/json'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);
 a.download='acceptability_'+SETNAME+'_'+rater.replace(/[^A-Za-z0-9]/g,'')+'_'+new Date().toISOString().slice(0,10)+'.json';
 document.body.appendChild(a);a.click();a.remove();}

nameScreen();
</script></body></html>"""


def main():
    gold = [(int(r["cell_id"]), r["sentence"])
            for r in csv.DictReader(open(os.path.join(RESULTS, "phase3_gold_sample.csv")))]
    grid = [r["sentence"] for r in csv.DictReader(
        open(os.path.join(RESULTS, "phase3_grid_judgment.csv")))]
    gold_ids = {c for c, _ in gold}
    rng = np.random.default_rng(SEED)
    kidx = sorted(rng.choice(len(gold), N_KAPPA, replace=False).tolist())
    kappa = [gold[i] for i in kidx]
    ridx = rng.choice(len(kappa), N_REPEAT, replace=False).tolist()
    nongold = [i for i in range(len(grid)) if i not in gold_ids]
    widx = rng.choice(nongold, N_WARMUP, replace=False).tolist()

    warmup = [{"id": int(i), "s": grid[i], "type": "warmup"} for i in widx]
    scored = ([{"id": c, "s": s, "type": "scored"} for c, s in kappa]
              + [{"id": kappa[i][0], "s": kappa[i][1], "type": "repeat"}
                 for i in ridx])

    html = (TEMPLATE
            .replace("__WARMUP__", json.dumps(warmup))
            .replace("__SCORED__", json.dumps(scored))
            .replace("__INSTR__", json.dumps(INSTR))
            .replace("__SET__", json.dumps(SETNAME)))

    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"acceptability_{SETNAME}.html")
    with open(out, "w") as f:
        f.write(html)
    # provenance key (executor-only): cell_id set for the rejoin / kappa
    with open(os.path.join(OUTDIR, f"{SETNAME}_cellids.json"), "w") as f:
        json.dump({"kappa_cell_ids": [c for c, _ in kappa],
                   "warmup_cell_ids": [int(i) for i in widx],
                   "repeat_cell_ids": [kappa[i][0] for i in ridx],
                   "seed": SEED}, f, indent=1)
    print("wrote %s  (%d scored + %d repeats + %d warm-up)"
          % (os.path.relpath(out, ROOT), N_KAPPA, N_REPEAT, N_WARMUP))


if __name__ == "__main__":
    main()
