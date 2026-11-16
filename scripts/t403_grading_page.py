#!/usr/bin/env python3
"""t403 grading page generator: D12 sheet for the phase-11/12 screens.

Pattern owner: scripts/t397_grading_page.py (read it first; the laws below are
its laws, restated). Builds work/r1/d1page/index.html + d11/*.png crops for
docs/DECISIONS.md D12 asks. POSTs land as "USER:" lines via d1page/server.py
(generic fields handler since t397).

Readability law (t397): 640x480 frames scaled by the browser are UNREADABLE
for text; text bands ship as NATIVE-RES 2x nearest-neighbour crops.
Crop-by-measurement law (t397 pitfall): boxes come from scripts/
t403_sheet_inventory.py / the green- and cyan-ink run probes in _wip_t403,
NEVER from memory. Run with the Hermes venv python (system python3 has no PIL).

Vendor-reference images (scratchpad/*-original.png) are copied into the page
dir and served LOCAL-ONLY. Copyright Maxis/Hasbro-derived media: NEVER publish,
NEVER commit (d1page/ lives under gitignored work/).

Field list mirrors the STATE.md D11 queue items the user has NOT yet graded:
  q1 title hover highlight (the one gap left in the 11:37 title verdict)
  q2 new game (t401 art pass vs the 11:37 "rows-bad" complaint list)
  q3 galaxy map (t399 3D field + t400 rail/flags/digits vs the 11:37 FAIL list)
  q4 planets list (t402 statuslist law — NEW screen, never graded)
  q5 audio line (OQ-027 closer: paste the `audio:` startup line; the 11:37
     "seems OK at first listen" is explicitly NOT the row's closing verdict)
Idempotent: re-run after any new loop capture to refresh crops.
"""
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "work/r1/d1page")
OUT = os.path.join(PAGE, "d11")
os.makedirs(OUT, exist_ok=True)


def crop2x(src, box, name):
    im = Image.open(os.path.join(ROOT, src)).convert("RGB")
    c = im.crop(box)
    c = c.resize((c.width * 2, c.height * 2), Image.NEAREST)
    c.save(os.path.join(OUT, name))
    return name, c.size


def full(src, name):
    im = Image.open(os.path.join(ROOT, src)).convert("RGB")
    im.save(os.path.join(OUT, name))
    return name, im.size


made = []
# 1. TITLE hover (t400 law: hovered band fill (0,28,36); MEASURED in
# t400-title-hover.png — btn4 LOAD band holds ALL 9347 fill px, others 0).
made.append(full("work/r1/loop/t400-title-hover.png", "t403-title-full.png"))
made.append(crop2x("work/r1/loop/t400-title-hover.png", (159, 355, 478, 445),
                   "t403-title-hover.png"))
# 2. NEW GAME (t401). Content column runs measured: racelist/begin x 494..639,
# desc+panels x 0..370; bottom config band y 415..480.
made.append(full("work/r1/loop/t401-newgame.png", "t403-newgame-full.png"))
made.append(crop2x("work/r1/loop/t401-newgame.png", (494, 60, 640, 380),
                   "t403-newgame-race.png"))
made.append(crop2x("work/r1/loop/t401-newgame.png", (0, 415, 470, 480),
                   "t403-newgame-bottom.png"))
made.append(crop2x("work/r1/loop/t401-newgame.png", (0, 60, 250, 380),
                   "t403-newgame-desc.png"))
# 3. GALAXY MAP (t399 field + t400 rail). Sidebar split per t397 geometry.
made.append(full("work/r1/loop/t400-map.png", "t403-map-full.png"))
made.append(crop2x("work/r1/loop/t400-map.png", (430, 0, 640, 240),
                   "t403-map-side-top.png"))
made.append(crop2x("work/r1/loop/t400-map.png", (430, 240, 640, 480),
                   "t403-map-side-bot.png"))
# 4. PLANETS LIST (t402). Text is cyan-white (190,255,255) over panel
# (40,40,56) — census MEASURED; crop covers the three visible rows + header.
made.append(full("work/r1/loop/t402-status-open.png", "t403-planets-full.png"))
made.append(crop2x("work/r1/loop/t402-status-open.png", (20, 46, 470, 372),
                   "t403-planets-rows.png"))
made.append(full("work/r1/loop/t402-status-select.png", "t403-planets-sel.png"))
# Vendor references (user-supplied originals; local serving only, never ship).
for p, nm in [("scratchpad/newgame-original.png", "vendor-newgame.png"),
              ("scratchpad/galaxymap-original.png", "vendor-galaxymap.png")]:
    sp = os.path.join(ROOT, p)
    if os.path.isfile(sp):
        shutil.copyfile(sp, os.path.join(OUT, nm))
        made.append((nm, Image.open(os.path.join(OUT, nm)).size))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>Ascendancy rewrite — D12 grading</title>
<style>
body{background:#111;color:#ddd;font-family:sans-serif;max-width:1000px;margin:1em auto;padding:0 1em}
h1{font-size:1.3em} h2{font-size:1.1em;margin-top:1.4em;border-bottom:1px solid #444}
img{border:1px solid #555;image-rendering:pixelated;max-width:100%%}
.zoom{image-rendering:pixelated}
fieldset{border:1px solid #666;margin:.6em 0;padding:.6em}
label{margin-right:1.2em}
textarea{width:100%%;height:3.2em;background:#1c1b1a;color:#ddd;border:1px solid #555}
button{font-size:1.15em;padding:.5em 1.6em;background:#2c5b8a;color:#fff;border:0;cursor:pointer}
.hint{color:#9a9a9a;font-size:.9em}
.row{display:flex;gap:1em;flex-wrap:wrap;align-items:flex-start}
</style></head><body>
<h1>D12 — grade the phase-11/12 rebuild (local main == t402, about to push)</h1>
<p class="hint">Your 11:37 ruling already moved everything below — these are
the fixes it asked for. One line each suffices; radio + notes post straight
into docs/DECISIONS.md as a USER: block. 2x crops are native-res text bands.
Best graded from your live Athens run after this iteration's push (git pull);
shots are the fallback. Live playtest law: rotate/zoom the map with the
bottom-right buttons, scroll + click rows in the Planets screen.</p>

<h2>1. TITLE — hover highlight (the one gap from your title verdict)</h2>
<div class="row">
<div><img src="d11/t403-title-full.png" width="640"><div class="hint">ours, full frame (LOAD GAME captured hovered)</div></div>
<div><img class="zoom" src="d11/t403-title-hover.png" width="638"><div class="hint">2x crop: hovered button band fill vs neighbours</div></div>
</div>
<fieldset><legend>Does the rewrite now highlight the button under the mouse?</legend>
<label><input type=radio name=q1 value="ok"> yes, highlights like the original</label>
<label><input type=radio name=q1 value="wrong"> highlights but looks wrong (notes)</label>
<label><input type=radio name=q1 value="no"> still no highlight live</label>
</fieldset>
<textarea id=q1n placeholder="notes (optional)"></textarea>

<h2>2. NEW GAME — t401 art pass (framing, race portraits, desc panel, Begin, bottom row)</h2>
<div class="row">
<div><img src="d11/t403-newgame-full.png" width="640"><div class="hint">ours now, full frame</div></div>
<div><img src="d11/vendor-newgame.png" width="640"><div class="hint">your original (reference)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t403-newgame-race.png" width="580"><div class="hint">2x: Player Species column (portrait + crest)</div></div>
<div><img class="zoom" src="d11/t403-newgame-bottom.png" width="940"><div class="hint">2x: bottom row wheels</div></div>
</div>
<div><img class="zoom" src="d11/t403-newgame-desc.png" width="500"><div class="hint">2x: description panel (should be solid black)</div></div>
<fieldset><legend>All five 11:37 complaints fixed: framing, bottom-row art, species-column art, Begin box, solid desc panel?</legend>
<label><input type=radio name=q2 value="ok"> all fixed</label>
<label><input type=radio name=q2 value="partial"> better, still wrong somewhere (name it)</label>
<label><input type=radio name=q2 value="bad"> still bad</label>
<label><input type=radio name=q2 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q2n placeholder="notes"></textarea>

<h2>3. GALAXY MAP — 3D field + rail art + big green digits (t399/t400)</h2>
<div class="row">
<div><img src="d11/t403-map-full.png" width="640"><div class="hint">ours now (turn 1: home-system lanes only)</div></div>
<div><img src="d11/vendor-galaxymap.png" width="640"><div class="hint">your original (reference)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t403-map-side-top.png" width="840"><div class="hint">2x: day digits (vendor faces), rail icons RIGHT of labels</div></div>
<div><img class="zoom" src="d11/t403-map-side-bot.png" width="840"><div class="hint">2x: spin/zoom cluster, species flags</div></div>
</div>
<fieldset><legend>3D-coloured-point map rotatable/zoomable, day counter big green numbers, rail icons coloured/right-side/right-size, species icons present?</legend>
<label><input type=radio name=q3 value="ok"> all good</label>
<label><input type=radio name=q3 value="partial"> better, still wrong somewhere (name it)</label>
<label><input type=radio name=q3 value="bad"> still bad</label>
<label><input type=radio name=q3 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q3n placeholder="notes"></textarea>

<h2>4. PLANETS LIST — new screen (t402): rows, header, scroll, click-select</h2>
<div class="row">
<div><img src="d11/t403-planets-full.png" width="640"><div class="hint">ours, STATUS rail -> Planets</div></div>
<div><img class="zoom" src="d11/t403-planets-rows.png" width="900"><div class="hint">2x: row text + header line</div></div>
</div>
<div><img src="d11/t403-planets-sel.png" width="640"><div class="hint">after clicking a row (selection lands)</div></div>
<fieldset><legend>Is the planets list usable now (readable rows, correct counts, click works)?</legend>
<label><input type=radio name=q4 value="ok"> usable</label>
<label><input type=radio name=q4 value="partial"> usable-ish, wrong details (name them)</label>
<label><input type=radio name=q4 value="bad"> still wrong and unusable</label>
<label><input type=radio name=q4 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q4n placeholder="notes"></textarea>

<h2>5. SOUND — the line that closes OQ-027 outright</h2>
<p>Boot <code>./build/ascendancy --data DIR --ui</code> once and paste the
startup line starting <code>audio:</code> (shape:
<code>audio: driver=... sfx=86 tunes=3 vol=127</code>) or the
<code>degraded: silent ...</code> line. Your 11:37 note ("seems OK at first
listen") is recorded but is NOT the closer — a final verdict on whether the
music/click behaviour matches the original is what closes the row.</p>
<textarea id=q5 placeholder="paste the audio: line + verdict (matches original / what differs)\"></textarea>

<p><button onclick="submitRuling()">Submit ruling</button>
<span id=out class="hint"></span></p>
<script>
function submitRuling(){
  const g=id=>{const e=document.getElementById(id);return e?e.value.trim():""};
  const r=id=>{const e=document.querySelector('input[name='+id+']:checked');return e?e.value:"(no answer)"};
  const body={title:"D12",fields:[
    ["D12 title hover =",r("q1")+" "+g("q1n")],
    ["D12 new game =",r("q2")+" "+g("q2n")],
    ["D12 galaxy map =",r("q3")+" "+g("q3n")],
    ["D12 planets list =",r("q4")+" "+g("q4n")],
    ["D12 audio =",g("q5")||"(no answer)"]]};
  fetch("/ruling",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(body)})
   .then(x=>x.text()).then(t=>{document.getElementById("out").textContent=t})
   .catch(e=>{document.getElementById("out").textContent="FAILED: "+e});
}
</script></body></html>
"""

with open(os.path.join(PAGE, "index.html"), "w") as f:
    f.write(HTML)
for n, s in made:
    print("made", n, s)
print("wrote", os.path.join(PAGE, "index.html"), len(HTML), "bytes")
