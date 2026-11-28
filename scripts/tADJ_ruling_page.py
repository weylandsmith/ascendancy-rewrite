#!/usr/bin/env python3
"""tADJ-RULING-PAGE: D2/D3 adjudication page for the loop's two USER-RULING rows.

OQ-016 and OQ-019 have exhausted every capture route (cited-dead evidence is
quoted VERBATIM below, collapsed under <details>), so closure is user-ruling
work only. The user is time-poor: text asks go unanswered, the same choices
close fast on a visual page (standing pattern: scripts/t424_grading_page.py,
and DECISIONS.md:184-196 shows a ruling that landed from one).

Shape: writes work/r1/d1page/index.html (the ALREADY-RUNNING server.py on
:8613 serves ROOT/index.html with no restart; POST /ruling appends a dated
"USER:" block to docs/DECISIONS.md via ruling_block()'s fields handler — the
exact mechanism the 2026-11-09 rulings used).

Discipline:
- Do NOT answer FOR the user: no option is pre-checked, no option is marked
  recommended in the page body.
- The t329 S4 draft (docs/re/_wip_t329.md) stays DO-NOT-APPLY until an
  accept-cited-dead ruling lands; the page only says that applying it is what
  "accept" would mean.
- Every cited-dead claim carries its doc citation so the ruling is informed.
- The debugger option names the budget consequence honestly: the scripted-
  mouse class is budget-spent (REFUTED-ROUTES.md:465-467) AND the debugger
  class itself carries two binding negatives (t288, t299) — funding it buys a
  NEW instrument class, not a rerun.

Run:  python3 scripts/tADJ_ruling_page.py   (stdlib only)
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "work", "r1", "d1page")
ADJ = os.path.join(PAGE, "d11")  # server.py only serves /img/ and /d11/ (do_GET whitelist) — no restart needed
os.makedirs(ADJ, exist_ok=True)

# One witness image: the live state-16 (battle control) screen recorded by the
# t338 session — the very screen whose chain legs are cited-dead for both rows.
SHOTS = [("work/r1/dbg-t338-20261107-224027/10_state16_screen.png",
          "tadj-state16.png")]
for src, name in SHOTS:
    s = os.path.join(ROOT, src)
    if os.path.exists(s):
        shutil.copyfile(s, os.path.join(ADJ, name))

# Preserve the previous sheet the way the page dir already does (index-d1.html,
# index-d11.html).
idx = os.path.join(PAGE, "index.html")
if os.path.exists(idx):
    shutil.copyfile(idx, os.path.join(PAGE, "index-d17r2.html"))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>D2/D3 adjudication — OQ-016, OQ-019, loop lifetime (tADJ)</title>
<style>
body{background:#14161a;color:#d8dce0;font:14px/1.55 system-ui,sans-serif;margin:24px auto;max-width:980px}
h1{font-size:20px} h2{font-size:16px;margin-top:30px;border-bottom:1px solid #333;padding-bottom:4px}
.hint{color:#9aa3ad;font-size:12px}
img{border:1px solid #444;background:#000;image-rendering:pixelated}
fieldset{border:1px solid #555;margin:12px 0;padding:10px 14px}
legend{font-weight:600}
label{display:block;margin:6px 0}
details{margin:8px 0;border:1px solid #333;padding:6px 10px;background:#19181d}
summary{cursor:pointer;color:#c8ccd0}
pre{white-space:pre-wrap;font:12px/1.45 ui-monospace,monospace;color:#b8bec6}
textarea{width:100%;height:52px;background:#1d2023;color:#d8dce0;border:1px solid #444;margin-top:6px}
button{background:#2d6cdf;color:#fff;border:0;padding:10px 22px;font-size:15px;margin-top:18px;cursor:pointer}
code{background:#222127;padding:1px 4px}
</style></head><body>
<h1>D2/D3 adjudication: OQ-016, OQ-019, and how long the loop runs</h1>
<p class="hint">Three questions. The loop has run out of work it can close by
itself: strict-close means only cited measurement closes a row, and every
capture route on the two open rows is now a <em>cited-dead</em> route. Your
answer here appends a dated block to docs/DECISIONS.md and the very next loop
session acts on it. Nothing is pre-selected; there is no recommended option.</p>

<div><img src="d11/tadj-state16.png" width="640"><div class="hint">The live
battle-control screen (state 16), recorded by session t338 — the same screen
where both rows' chain legs were measured zero. The screen is real; the
selection/order message road behind it is what could not be witnessed.</div></div>

<h2>1. OQ-019 — per-ship design model: select / destination / magnetron residues</h2>
<p><strong>Question:</strong> every capture route for the remaining OQ-019
residues is cited-dead, so how should the loop dispose of the row?</p>
<details><summary>cited-dead evidence (verbatim, with paths)</summary>
<pre>OPEN-QUESTIONS.md (t324 note): "Every OQ-019 capture route is now
cited-dead: t319/t320 pump, t322 mouse, t323 activation, t324 class-table."

t319/t320 (pump):   the poster never posts msg 0xc.
t322 (mouse):       the four batcon click-road legs {0x1AEF8, 0x1B91C,
                    w43508_1b5e6, w43508_1baa7} armed live for the first
                    time over the t298 battery: ALL ZERO, instrument
                    verified (census-ctl MATCH=True). REFUTED-ROUTES.md
                    t322 amendment: "THE BATCON MOUSE ROAD IS DEAD
                    IN-CAPTURE".
t323 (activation):  BatModeWnd has NO in-session activator — the only
                    runtime switcher fn 0x31f30 is reached exclusively from
                    fn 0x32100, which is NOT in the BATMODE class table.
t324 (class table): re-open condition discharged NEGATIVE ABSOLUTE — live-
                    RAM census of the BatModeWnd class table (data payload
                    offset 0x58e8) reproduces the cited table byte-for-byte;
                    fn 0x32100 ABSENT, 10/10 saves identical
                    (scripts/r324_census.py).

Dispositions packet: docs/re/_wip_t329.md S4 — final row text DRAFTED there,
marked DO-NOT-APPLY until your ruling. Residues: (1) select + msg-0x50
destination widget = unreachable-by-capture (static law stands); (2) per-ship
build/redesign path = the D2 build decision (the flip itself landed t365; the
aggregate-oracle removal clause is unblocked but deferred on this ruling);
(3) magnetron witnessed use = witness-class limited, use-site law stands
static-cited (gizhelp.txt:1173-1181 + handler 0x21f58).</pre></details>
<fieldset><legend>OQ-019 disposition</legend>
<label><input type=radio name=q0 value="accept-cited-dead-and-close-with-residue"> accept cited-dead and close the row with the residue notes (the loop applies the t329 S4 draft verbatim)</label>
<label><input type=radio name=q0 value="fund-debugger-witness"> fund a debugger-class witness anyway — budget consequence: the scripted-mouse class is budget-spent (REFUTED-ROUTES.md:465-467) AND the debugger class carries two binding negatives itself: t288 (the dbg dosbox-x build aborts restoring bank savestates) and t299 (3 sessions, all eight static batmode legs zero). Funding this buys a brand-new instrument class (live in-session BPs, scratch tree, no guarantee), not a rerun of a dead one</label>
<label><input type=radio name=q0 value="defer"> defer</label>
</fieldset>
<textarea id=q0n placeholder="notes (e.g. which residue to keep open even if the rest closes)"></textarea>

<h2>2. OQ-016 — campaign per-turn constants: build-order / batctrl-chain residue</h2>
<p><strong>Question:</strong> the OQ-016 residue list is exhausted — accept
the cited-dead tail, or name a capture target the loop has not refuted?</p>
<details><summary>cited-dead evidence (verbatim, with paths)</summary>
<pre>OPEN-QUESTIONS.md:269: "The OQ-016 residue list is now EXHAUSTED ((1)
cited-dead x8 legs = user ruling, (2)(3)(4) CLOSED, (6) CLOSED as
misattribution) — row movement per D3 is USER ADJUDICATION; row stays open
strict-close."

The eight chain legs {0x156D4, 0x15EF1, 0x15FED, 0x1615D, 0x1616F, 0x161D1,
0x1B7DD, 0x1B180} measured ZERO twice, independently:
  t332 — full battery from the galaxy map, all 8 legs armed, all zero
         (docs/re/ships.md S52-S54).
  t338 — game driven INTO state 16 live (Icarus-pip click enters system
         view; SET-STATE witnessed with edx=0x10; 13 oracle reads
         state==16): all eight legs pty-whole-log ZERO again; mechanism
         banked — BatControlWnd is a TYPE-19 parent with rect 0,0-0,0 and
         can NEVER be a mouse hit target; entry at fn 0x156d4 requires a
         non-mouse 0x1c01 poster to registry slot 61, and no such poster
         exists in the image (docs/re/ships.md S55-S57).

Closed sub-laws already stand cited: income channel law, pop growth, build
queue + AI selector, pop-cap recalc, terrain generation, home placement
table. Residue (5) build-order minutiae is the diminishing tail.</pre></details>
<fieldset><legend>OQ-016 disposition</legend>
<label><input type=radio name=q1 value="accept-cited-dead"> accept cited-dead (close the row with the eight-leg unreachable note, like the magnetron static-citation class)</label>
<label><input type=radio name=q1 value="name-a-new-capture-target"> name a new capture target (write it in the notes box — the loop will audit it against REFUTED-ROUTES.md before spending anything)</label>
<label><input type=radio name=q1 value="defer"> defer</label>
</fieldset>
<textarea id=q1n placeholder="notes / the named capture target"></textarea>

<h2>3. D3 — how long the loop keeps running</h2>
<p><strong>Question:</strong> with the open ledger now entirely user-gated
(plus a hygiene-tail of audits), what should the harness do between now and
your rulings — and after them?</p>
<details><summary>context (verbatim)</summary>
<pre>GOAL.txt: "This loop has no completion milestone short of the empty open
ledger; under strict-close policy it may run indefinitely."

DECISIONS.md:182 (2026-11-09): "D3 = DEFERRED by user until D1/D2 work has
landed." — D1 landed (grading pages, 2026-11-09 rulings); D2 landed t365
(per-ship flip, suite green, seeds byte-identical). D3 is ripe again.

tPF5-A (2026-11-27) shipped the LAST non-user-gated, statically derivable
item in the defect queue. With no ruling, later sessions would keep the loop
green on control-plane hygiene (ledger/gate/doc audits) at <=1 audit per
session — real but thin work. Each hygiene session costs a launch and the
hardware is slow; idling loses nothing that a ruling can't restart.</pre></details>
<fieldset><legend>D3 — loop lifetime</legend>
<label><input type=radio name=q2 value="idle-until-ruling"> idle the harness now: relaunch only when a ruling lands on this page (or a new play sitting appears) — resumes immediately, no churn</label>
<label><input type=radio name=q2 value="hygiene-loop"> keep looping on control-plane hygiene at &lt;=1 audit per session until further notice</label>
<label><input type=radio name=q2 value="run-until-zero"> run literally until the open ledger is empty (risk: pressure to re-queue refuted-class routes — the loop has caught itself doing that once, tOQ19-AUDIT)</label>
<label><input type=radio name=q2 value="stop"> stop the closeout loop; ship as 18/20 closed + honest capture-limited notes</label>
<label><input type=radio name=q2 value="defer"> defer</label>
</fieldset>
<textarea id=q2n placeholder="notes"></textarea>

<button onclick="post()">Submit adjudication</button>
<script>
function post(){
  const labels=["ADJ OQ-019 disposition","ADJ OQ-016 disposition","ADJ D3 loop lifetime"];
  const fields=[];
  for(let i=0;i<3;i++){
    const r=document.querySelector('input[name=q'+i+']:checked');
    if(!r) continue;
    let v=r.value;
    const t=document.getElementById('q'+i+'n');
    if(t&&t.value.trim()) v+=' | notes: '+t.value.trim();
    fields.push([labels[i]+" = ", v]);
  }
  if(!fields.length){alert('answer at least one row');return;}
  fetch('/ruling',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title:"D2/D3 adjudication (OQ-016 + OQ-019 + loop lifetime)", fields:fields})})
   .then(r=>{document.body.innerText=r.ok?'Posted. The next loop session will act on it.':'POST failed '+r.status;});
}
</script>
</body></html>
"""

with open(idx, "w") as f:
    f.write(HTML)

print("wrote", idx, len(HTML), "bytes")
print("images copied:", [n for s, n in SHOTS
                         if os.path.exists(os.path.join(ADJ, n))])
