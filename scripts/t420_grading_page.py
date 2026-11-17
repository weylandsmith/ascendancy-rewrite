#!/usr/bin/env python3
"""t420 grading page generator: D16 sheet for the phase-15 screens.

Pattern owners: scripts/t397_grading_page.py (laws), scripts/t413_grading_page.py
(restated pattern + crop inventory run). Builds work/r1/d1page/index.html +
d11/*.png crops for the docs/DECISIONS.md D16 asks. POSTs land as "USER:"
lines via d1page/server.py (generic fields handler since t397). Server serves
ROOT/index.html — no restart needed.

Readability law (t397): 640x480 frames scaled by the browser are UNREADABLE
for text; text bands ship as NATIVE-RES 2x nearest-neighbour crops.
Crop-by-measurement law (t397 pitfall): boxes come from
scripts/t403_sheet_inventory.py runs, NEVER from memory. Run with a PIL python:
  ~/tools/revenv/bin/python scripts/t420_grading_page.py

Inventory MEASURED this row (t403_sheet_inventory run, 2026-11-17):
  walk/t414-newgame2  bg=(0,0,0)     mass=34186 bands 420-480,360-420,0-60
  walk/t415_intro     bg=(0,0,0)     mass=34184 bands 420-480,360-420,0-60
  t417b-status        bg=(0,0,0)     mass=9529  bands 0-60,420-480,60-120
  t418b-planet-open   bg=(16,16,24)  mass=24550 bands 0-60,60-120,300-360
  t418b-planet-tile   bg=(16,16,24)  mass=24550 bands 0-60,60-120,300-360
  research-open       bg=(16,16,24)  mass=6441  bands 60-120,120-180,420-480
  research-spin1      bg=(16,16,24)  mass=4711  bands 420-480,0-60,120-180
  corner-topleft      bg=(16,16,24)  mass=4870  bands 0-60,420-480,120-180
All nine phase-15 shots md5-DISTINCT (checked this row — no dead/duplicate
frames). The t419 shots were banked from /tmp/t419_shots into work/r1/loop.

NO vendor-reference images this sheet (phase 15 asks are look/function vs the
user's live memory of the original, same as t413/D14).
"""
import os

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
# 1. NEW GAME round 3 (t414) — frame, spinning preview, wheels, chips,
#    circular portraits, planet image.
made.append(full("work/r1/loop/walk/t414-newgame2.png", "t416-newgame-full.png"))
made.append(crop2x("work/r1/loop/walk/t414-newgame2.png", (0, 0, 500, 120),
                   "t416-newgame-top.png"))
made.append(crop2x("work/r1/loop/walk/t414-newgame2.png", (0, 350, 640, 480),
                   "t416-newgame-bar.png"))
made.append(crop2x("work/r1/loop/walk/t414-newgame2.png", (300, 60, 640, 340),
                   "t416-newgame-desc.png"))
# 2. RACE INTRO framed (t415).
made.append(full("work/r1/loop/walk/t415_intro.png", "t416-intro-full.png"))
made.append(crop2x("work/r1/loop/walk/t415_intro.png", (0, 0, 640, 120),
                   "t416-intro-head.png"))
made.append(crop2x("work/r1/loop/walk/t415_intro.png", (0, 40, 320, 260),
                   "t416-intro-portrait.png"))
# 3. PLANETS LIST background (t417b) — black interior, texture bands, red marker.
made.append(full("work/r1/loop/t417b-status.png", "t416-status-full.png"))
made.append(crop2x("work/r1/loop/t417b-status.png", (0, 0, 640, 120),
                   "t416-status-head.png"))
made.append(crop2x("work/r1/loop/t417b-status.png", (0, 40, 140, 340),
                   "t416-status-marker.png"))
# 4. PLANET VIEW (t418b) — the planet disc + isometric tile grid + selection.
made.append(full("work/r1/loop/t418b-planet-open.png", "t416-planet-full.png"))
made.append(full("work/r1/loop/t418b-planet-tile.png", "t416-planet-tile.png"))
made.append(crop2x("work/r1/loop/t418b-planet-open.png", (60, 60, 470, 400),
                   "t416-planet-grid.png"))
# 5. RESEARCH 3D (t419) — spin, scroll, panel, and the corner Exit popup.
made.append(full("work/r1/loop/research-open.png", "t416-res-open.png"))
made.append(full("work/r1/loop/research-spin1.png", "t416-res-spin.png"))
made.append(full("work/r1/loop/research-scrolldn.png", "t416-res-scroll.png"))
made.append(crop2x("work/r1/loop/research-open.png", (476, 40, 640, 300),
                   "t416-res-panel.png"))
made.append(crop2x("work/r1/loop/corner-topleft.png", (0, 0, 160, 120),
                   "t416-res-corner.png"))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>Ascendancy rewrite — D16 grading</title>
<style>
body{background:#111;color:#ddd;font-family:sans-serif;max-width:1000px;margin:1em auto;padding:0 1em}
h1{font-size:1.3em} h2{font-size:1.1em;margin-top:1.4em;border-bottom:1px solid #444}
img{border:1px solid #555;image-rendering:pixelated;max-width:100%}
.zoom{image-rendering:pixelated}
fieldset{border:1px solid #666;margin:.6em 0;padding:.6em}
label{margin-right:1.2em}
textarea{width:100%;height:3.2em;background:#1c1b1a;color:#ddd;border:1px solid #555}
button{font-size:1.15em;padding:.5em 1.6em;background:#2c5b8a;color:#fff;border:0;cursor:pointer}
.hint{color:#9a9a9a;font-size:.9em}
.row{display:flex;gap:1em;flex-wrap:wrap;align-items:flex-start}
</style></head><body>
<h1>D16 — phase 15 (your D15 round-3 list), item by item (main == t419, pushed this iteration)</h1>
<p class="hint">Everything below answers your D15 message (new game framing /
wheels / player colors / race images / planet image; intro framing; rotation
axis; planets-list background; the planet itself; the research CPU stall and
the corner Exit popup). The loop fixed t414-t419 and self-graded with its own
vision; this sheet asks YOU to confirm. Best graded from your live run after
`git pull` — shots are the fallback. One line each suffices; radio + notes
post straight into docs/DECISIONS.md as a USER: block.</p>

<h2>0. RESEARCH SCREEN STALL — CPU pegging and trapped-Esc are gone (t419)</h2>
<p class="hint">This was your worst defect: opening Research pinned a core and
Esc took minutes. Measured now: 2 us/frame layout (was 2160 us for ONE frame),
Esc closes in 204 ms, CPU ~35% of one core while the screen is open. Please
re-check LIVE: open Research, leave it a minute, press Esc — it should close
promptly and your machine stay responsive.</p>
<fieldset><legend>Research no longer pegs the CPU; Escape returns to the galaxy promptly?</legend>
<label><input type=radio name=q0 value="ok"> yes</label>
<label><input type=radio name=q0 value="partial"> partly (name it)</label>
<label><input type=radio name=q0 value="no"> still stalls</label>
<label><input type=radio name=q0 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q0n placeholder="notes"></textarea>

<h2>1. RESEARCH 3D (t419) — rotating tree, right info panel, spin + scroll controls</h2>
<div class="row">
<div><img src="d11/t416-res-open.png" width="640"><div class="hint">at rest: the tech tree laid out flat, right-hand info panel live</div></div>
</div>
<div class="row">
<div><img src="d11/t416-res-spin.png" width="640"><div class="hint">mid-spin: perspective appears, rings scale with depth</div></div>
<div><img src="d11/t416-res-scroll.png" width="640"><div class="hint">after the scroll pair (up/down)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t416-res-panel.png" width="656"><div class="hint">2x: Current Project panel</div></div>
</div>
<fieldset><legend>Research is now a 3D rotating dealie with the info frame at right and working rotation + scroll?</legend>
<label><input type=radio name=q1 value="ok"> yes</label>
<label><input type=radio name=q1 value="partial"> partly (name it)</label>
<label><input type=radio name=q1 value="bad"> no</label>
<label><input type=radio name=q1 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q1n placeholder="notes"></textarea>

<h2>2. CORNER EXIT POPUP (t419) — mouse in a corner pops 'Exit &lt;ESC&gt;'</h2>
<div class="row">
<div><img class="zoom" src="d11/t416-res-corner.png" width="320"><div class="hint">2x: the popup tucked into the top-left corner (mouse.shp art — the image you remembered)</div></div>
</div>
<p class="hint">LIVE re-check: move the mouse into any screen corner during the
campaign and the box should pop out, tucking away when you leave. It is
campaign-wide (you confirmed the original has none on the title screen).</p>
<fieldset><legend>Corner Exit popup appears/disappears like the original?</legend>
<label><input type=radio name=q2 value="ok"> yes</label>
<label><input type=radio name=q2 value="partial"> partly (name it)</label>
<label><input type=radio name=q2 value="bad"> no</label>
<label><input type=radio name=q2 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q2n placeholder="notes"></textarea>

<h2>3. NEW GAME round 3 (t414) — framing, spinning preview, wheels, colors, portraits, planet</h2>
<div class="row">
<div><img src="d11/t416-newgame-full.png" width="640"><div class="hint">full screen now: texture chrome page, cosmos preview, framed panels</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t416-newgame-bar.png" width="1280"><div class="hint">2x config bar: wheels (5 density / species / 3 atmosphere), 7 player-colour chips, Begin box</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t416-newgame-desc.png" width="680"><div class="hint">2x: circular portrait, planet image, lore well</div></div>
<div><img class="zoom" src="d11/t416-newgame-top.png" width="1000"><div class="hint">2x: species name header</div></div>
</div>
<p class="hint">LIVE re-check: the preview field should SPIN and change star
count with Star Density; no wheel frame repeats or is missing (Hostile's red
orb is a known vendor-truncated record — it prints a refusal instead); race
portraits are clipped to circles, not squares.</p>
<fieldset><legend>New Game screen fixed: framing + spinning preview + wheels + player colors + circular portraits + planet image?</legend>
<label><input type=radio name=q3 value="ok"> yes all</label>
<label><input type=radio name=q3 value="partial"> partly (name which)</label>
<label><input type=radio name=q3 value="bad"> still bad</label>
<label><input type=radio name=q3 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q3n placeholder="notes"></textarea>

<h2>4. RACE INTRO (t415) — framed screen with portrait + emblem</h2>
<div class="row">
<div><img src="d11/t416-intro-full.png" width="640"><div class="hint">appears after Begin: frame + dividers, portrait top-left, emblem, header, intro well right, body well below</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t416-intro-head.png" width="1280"><div class="hint">2x: header + emblem</div></div>
<div><img class="zoom" src="d11/t416-intro-portrait.png" width="640"><div class="hint">2x: lgrace portrait</div></div>
</div>
<p class="hint">Known seam, do not hold it against the screen: body-well ink
colour comes from a runtime race-colour table we have not captured — Minions
show red where your screenshot memory says green.</p>
<fieldset><legend>Intro screen framing/art right (ignoring the ink-colour seam)?</legend>
<label><input type=radio name=q4 value="ok"> yes</label>
<label><input type=radio name=q4 value="partial"> partly (name it)</label>
<label><input type=radio name=q4 value="bad"> no</label>
<label><input type=radio name=q4 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q4n placeholder="notes"></textarea>

<h2>5. GALAXY MAP ROTATION (t416) — dials now latch: click = keeps spinning</h2>
<p class="hint">No art to grade — behaviour only. Vendor law recovered: one
click starts CONTINUOUS motion, clicking the same dial stops it, the opposite
dial flips direction. Spin = world-Y (looks like in-plane rotation at rest),
tilt = world-X, no clamp. LIVE: click ROTLEFT once and watch; re-click stops.</p>
<fieldset><legend>Rotation dials behave like the original (continuous, stop, flip)?</legend>
<label><input type=radio name=q5 value="ok"> yes</label>
<label><input type=radio name=q5 value="partial"> partly (name it)</label>
<label><input type=radio name=q5 value="bad"> no</label>
<label><input type=radio name=q5 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q5n placeholder="notes"></textarea>

<h2>6. PLANETS LIST background (t417/t417b) — the "unused image" is gone</h2>
<div class="row">
<div><img src="d11/t416-status-full.png" width="640"><div class="hint">black interior, perimeter texture bands, speckled header + green title, divider ramp, RED selection marker, no row separator lines</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t416-status-head.png" width="1280"><div class="hint">2x header</div></div>
<div><img class="zoom" src="d11/t416-status-marker.png" width="280"><div class="hint">2x marker + sphere well</div></div>
</div>
<fieldset><legend>Planets list background looks right now?</legend>
<label><input type=radio name=q6 value="ok"> yes</label>
<label><input type=radio name=q6 value="partial"> partly (name it)</label>
<label><input type=radio name=q6 value="bad"> no</label>
<label><input type=radio name=q6 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q6n placeholder="notes"></textarea>

<h2>7. THE PLANET ITSELF (t418b) — disc + isometric tile grid + tile select</h2>
<div class="row">
<div><img src="d11/t416-planet-full.png" width="640"><div class="hint">planet disc + isometric diamond grid + structures on tiles</div></div>
<div><img src="d11/t416-planet-tile.png" width="640"><div class="hint">a tile selected (white outline) — build order via the project list</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t416-planet-grid.png" width="820"><div class="hint">2x: the diamond lattice; clicking a gap point between tiles honestly refuses</div></div>
</div>
<p class="hint">LIVE re-check: click a tile adjacent to an existing structure
and order a build — the adjacency law (an ACTIVE neighbour refuses an inactive
new item) is the vendor's four-probe rule, cited in code.</p>
<fieldset><legend>Planet view shows the planet with selectable isometric tiles and adjacency-gated build orders?</legend>
<label><input type=radio name=q7 value="ok"> yes</label>
<label><input type=radio name=q7 value="partial"> partly (name it)</label>
<label><input type=radio name=q7 value="bad"> no</label>
<label><input type=radio name=q7 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q7n placeholder="notes"></textarea>

<h2>8. AUDIO (carried, OQ-027) — still waiting on your ears</h2>
<p class="hint">Only two narrow questions remain: at the title screen is the
menu tune intro00-or-intro01 ordering right, and do button clicks sound like
the original's? If you never want to answer this, say "skip audio" and the
row stays a documented port choice.</p>
<fieldset><legend>Audio: title tune + click sounds acceptable?</legend>
<label><input type=radio name=q8 value="ok"> acceptable</label>
<label><input type=radio name=q8 value="wrong"> wrong (describe)</label>
<label><input type=radio name=q8 value="skip"> skip audio — port choice stands</label>
<label><input type=radio name=q8 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q8n placeholder="notes"></textarea>

<button onclick="post()">Submit grading</button>
<script>
function post(){
  const fields=[];
  for(let i=0;i<9;i++){
    const r=document.querySelector('input[name=q'+i+']:checked');
    if(!r) continue;
    let v=r.value;
    const t=document.getElementById('q'+i+'n');
    if(t&&t.value.trim()) v+=' | notes: '+t.value.trim();
    fields.push(["D16 q"+i+" = ", v]);
  }
  if(!fields.length){alert('answer at least one row');return;}
  fetch('/ruling',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title:"D16 phase-15 grading", fields:fields})})
   .then(r=>{document.body.innerText=r.ok?'Posted. Thank you.':'POST failed '+r.status;});
}
</script>
</body></html>
"""

with open(os.path.join(PAGE, "index.html"), "w") as f:
    f.write(HTML)

print("crops:", len(made))
for n, sz in made:
    print(" ", n, sz)
