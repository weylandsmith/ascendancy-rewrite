#!/usr/bin/env python3
"""t413 grading page generator: D14 sheet for the phase-13/14 screens.

Pattern owners: scripts/t397_grading_page.py (laws), scripts/t403_grading_page.py
(restated pattern). Builds work/r1/d1page/index.html + d11/*.png crops for the
docs/DECISIONS.md D14 asks. POSTs land as "USER:" lines via d1page/server.py
(generic fields handler since t397). Server serves ROOT/index.html — no
restart needed (t403 fact, re-verified GET 200 this row).

Readability law (t397): 640x480 frames scaled by the browser are UNREADABLE
for text; text bands ship as NATIVE-RES 2x nearest-neighbour crops.
Crop-by-measurement law (t397 pitfall): boxes come from
scripts/t403_sheet_inventory.py runs, NEVER from memory. Run with a PIL python:
  ~/tools/revenv/bin/python scripts/t413_grading_page.py
  (or the Hermes venv python — system python3 has no PIL)

Idempotent: re-run after any new loop capture to refresh crops.
NO vendor-reference images this sheet (phase 13/4 asks are function+look vs
the user's live memory of the original; scratchpad originals only exist for
newgame/galaxymap and the t411 map is already graded against them).
"""
import os
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
# Inventory MEASURED this row (t403_sheet_inventory run, 2026-11-16):
#   t411-map        bg=(0,0,0)   bands 240-300/360-480 bright (field+sidebar)
#   t412-raceintro  bg=(0,0,0)   bands 120-240 bright (body text), 0-60 heading
#   planet-view     bg=pale sage bands 0-180 (info column), 420-480 (project row)
#   fleet-rows      bg=(16,16,24) bands 0-180 (header + rows)
#   species-menu    bg=(16,16,24) band 300-360 (menu rows)
#   sys-open        bg=(16,16,24) bands 60-180 (orbit grid), 420-480 (consoles)
#   research-study  bg=(16,16,24) bands 60-180 (tech list), 420-480 (study row)

# 1. GALAXY MAP after t411 (blend fix, mottle, bevel, digits, depth dim).
made.append(full("work/r1/loop/t411-map.png", "t414-map-full.png"))
made.append(crop2x("work/r1/loop/t411-map.png", (430, 0, 640, 240),
                   "t414-map-side-top.png"))
made.append(crop2x("work/r1/loop/t411-map.png", (430, 240, 640, 480),
                   "t414-map-side-bot.png"))
# 2. RACE INTRO (t412) — new screen between New Game and the map.
made.append(full("work/r1/loop/t412-raceintro.png", "t414-intro-full.png"))
made.append(crop2x("work/r1/loop/t412-raceintro.png", (0, 0, 640, 120),
                   "t414-intro-head.png"))
made.append(crop2x("work/r1/loop/t412-raceintro.png", (0, 120, 640, 300),
                   "t414-intro-body.png"))
# 3. SYSTEM VIEW (t410) — map star click -> orbit grid + consoles.
made.append(full("work/r1/loop/sys-open.png", "t414-sys-full.png"))
made.append(crop2x("work/r1/loop/sys-open.png", (0, 40, 470, 200),
                   "t414-sys-orbits.png"))
made.append(crop2x("work/r1/loop/sys-open.png", (460, 40, 640, 460),
                   "t414-sys-consoles.png"))
# 4. PLANET VIEW + PROJECT SET (t406) — colonised dot click.
made.append(full("work/r1/loop/planet-view.png", "t414-planet-full.png"))
made.append(crop2x("work/r1/loop/planet-view.png", (0, 0, 470, 190),
                   "t414-planet-info.png"))
made.append(crop2x("work/r1/loop/project-list.png", (0, 380, 640, 480),
                   "t414-planet-project.png"))
# 5. SHIPS screen (t407) — fleet rows were EMPTY per D13.
made.append(full("work/r1/loop/fleet-rows.png", "t414-ships-full.png"))
made.append(crop2x("work/r1/loop/fleet-rows.png", (20, 46, 470, 200),
                   "t414-ships-rows.png"))
# 6. RESEARCH screen (t408) — was EMPTY; set-study law.
made.append(full("work/r1/loop/t408-research-study.png", "t414-res-full.png"))
made.append(crop2x("work/r1/loop/t408-research-study.png", (20, 46, 470, 200),
                   "t414-res-rows.png"))
made.append(crop2x("work/r1/loop/t408-research-study.png", (0, 400, 640, 480),
                   "t414-res-study.png"))
# 7. SPECIES screen + ability dialog (t409).
made.append(full("work/r1/loop/species-menu.png", "t414-species-full.png"))
made.append(crop2x("work/r1/loop/species-menu.png", (0, 280, 470, 380),
                   "t414-species-menu.png"))
made.append(full("work/r1/loop/ability-open.png", "t414-ability-full.png"))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>Ascendancy rewrite — D14 grading</title>
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
<h1>D14 — the D13 bug list, item by item (local main == t412, pushed this iteration)</h1>
<p class="hint">Every item below was on your D13 list ("step through all the
screens until they look and work right"). The loop fixed them t404-t412 and
self-graded with its own vision; this sheet asks YOU to confirm. Best graded
from your live run after `git pull` — shots are the fallback. One line each
suffices; radio + notes post straight into docs/DECISIONS.md as a USER: block.</p>

<h2>0. MAP CLICKS — laser sound gone (t404) + screens reachable (t405-t410)</h2>
<p class="hint">Regression fix: clicking the map no longer plays laser-fire.
Rail buttons now navigate. Escape backs out ONE level per press.</p>
<fieldset><legend>Map clicks silent; rail buttons open their screens; Escape steps back one level at a time?</legend>
<label><input type=radio name=q0 value="ok"> yes all three</label>
<label><input type=radio name=q0 value="partial"> partly (name it)</label>
<label><input type=radio name=q0 value="no"> no</label>
<label><input type=radio name=q0 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q0n placeholder="notes"></textarea>

<h2>1. GALAXY MAP look pass 2 (t411) — day digits, sidebar, recessed field</h2>
<div class="row">
<div><img src="d11/t414-map-full.png" width="640"><div class="hint">ours now: no pale wash (blend-mode bug fixed), outline-ring zero digits, mottled sidebar, recessed field, far pips dimmer</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t414-map-side-top.png" width="840"><div class="hint">2x: day counter digits + rail</div></div>
<div><img class="zoom" src="d11/t414-map-side-bot.png" width="840"><div class="hint">2x: spin/zoom cluster + flags</div></div>
</div>
<fieldset><legend>Map looks right now (digits, sidebar texture, frame recess, depth dimming)?</legend>
<label><input type=radio name=q1 value="ok"> yes</label>
<label><input type=radio name=q1 value="partial"> better, still wrong somewhere (name it)</label>
<label><input type=radio name=q1 value="bad"> still bad</label>
<label><input type=radio name=q1 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q1n placeholder="notes"></textarea>

<h2>2. RACE INTRO (t412) — NEW screen between New Game and the map</h2>
<div class="row">
<div><img src="d11/t414-intro-full.png" width="640"><div class="hint">Begin -> intro -> click -> map (your race's history.txt text, race-coloured ink)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t414-intro-head.png" width="940"><div class="hint">2x: heading + first lines</div></div>
</div>
<div><img class="zoom" src="d11/t414-intro-body.png" width="940"><div class="hint">2x: body text</div></div>
<fieldset><legend>Intro appears after Begin, text is right for your species, click continues to the map, mapgen delay hidden behind it?</legend>
<label><input type=radio name=q2 value="ok"> yes</label>
<label><input type=radio name=q2 value="partial"> appears, but wrong (name it)</label>
<label><input type=radio name=q2 value="bad"> missing/wrong screen</label>
<label><input type=radio name=q2 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q2n placeholder="notes"></textarea>

<h2>3. SYSTEM VIEW (t410) — click a STAR on the map</h2>
<div class="row">
<div><img src="d11/t414-sys-full.png" width="640"><div class="hint">orbit grid is code-drawn (vendor chrome has no full-screen backdrop — measured)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t414-sys-orbits.png" width="940"><div class="hint">2x: orbit rings + body dots</div></div>
<div><img class="zoom" src="d11/t414-sys-consoles.png" width="560"><div class="hint">2x: right-column consoles (17 buttons, verbatim windows.txt)</div></div>
</div>
<fieldset><legend>Star click opens the system display; it reads as a system display?</legend>
<label><input type=radio name=q3 value="ok"> yes</label>
<label><input type=radio name=q3 value="partial"> opens, look wrong (name it)</label>
<label><input type=radio name=q3 value="bad"> no</label>
<label><input type=radio name=q3 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q3n placeholder="notes"></textarea>

<h2>4. PLANET VIEW + set a PROJECT (t406) — colonised dot click inside system view</h2>
<div class="row">
<div><img src="d11/t414-planet-full.png" width="640"><div class="hint">planet info (planet.txt route one)</div></div>
</div>
<div><img class="zoom" src="d11/t414-planet-project.png" width="940"><div class="hint">2x: project list row — click sets the planet's project</div></div>
<fieldset><legend>Colonised dot opens the planet view; you can set a project; bare planets stay silent (not fabricated)?</legend>
<label><input type=radio name=q4 value="ok"> yes</label>
<label><input type=radio name=q4 value="partial"> partly (name it)</label>
<label><input type=radio name=q4 value="bad"> no</label>
<label><input type=radio name=q4 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q4n placeholder="notes"></textarea>

<h2>5. SHIPS screen (t407) — was EMPTY</h2>
<div class="row">
<div><img src="d11/t414-ships-full.png" width="640"><div class="hint">fleet rows: name, location, orders</div></div>
<div><img class="zoom" src="d11/t414-ships-rows.png" width="900"><div class="hint">2x: header + rows</div></div>
</div>
<fieldset><legend>Ships screen lists your fleet correctly?</legend>
<label><input type=radio name=q5 value="ok"> yes</label>
<label><input type=radio name=q5 value="partial"> rows present, wrong (name it)</label>
<label><input type=radio name=q5 value="bad"> still empty/wrong</label>
<label><input type=radio name=q5 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q5n placeholder="notes"></textarea>

<h2>6. RESEARCH screen (t408) — was EMPTY; select a technology</h2>
<div class="row">
<div><img src="d11/t414-res-full.png" width="640"><div class="hint">tech list + current study row</div></div>
<div><img class="zoom" src="d11/t414-res-rows.png" width="900"><div class="hint">2x: rows</div></div>
</div>
<div><img class="zoom" src="d11/t414-res-study.png" width="940"><div class="hint">2x: study-selection row</div></div>
<fieldset><legend>Research screen lists techs and you can pick what to study?</legend>
<label><input type=radio name=q6 value="ok"> yes</label>
<label><input type=radio name=q6 value="partial"> partly (name it)</label>
<label><input type=radio name=q6 value="bad"> no</label>
<label><input type=radio name=q6 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q6n placeholder="notes"></textarea>

<h2>7. SPECIES screen + special ability (t409)</h2>
<div class="row">
<div><img src="d11/t414-species-full.png" width="640"><div class="hint">species menu rows</div></div>
<div><img class="zoom" src="d11/t414-species-menu.png" width="900"><div class="hint">2x: menu</div></div>
</div>
<div><img src="d11/t414-ability-full.png" width="640"><div class="hint">ability dialog (vendor path 0x55ffb -> 'ability')</div></div>
<fieldset><legend>Species screen reads correctly; the special-ability button opens a dialog?</legend>
<label><input type=radio name=q7 value="ok"> yes</label>
<label><input type=radio name=q7 value="partial"> partly (name it)</label>
<label><input type=radio name=q7 value="bad"> no</label>
<label><input type=radio name=q7 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q7n placeholder="notes"></textarea>

<h2>8. AUDIO line (OQ-027 closer — still open)</h2>
<p class="hint">Your "seems OK at first listen" is recorded but per the row's
own bar is NOT the closer. The closer is: paste the `audio: driver=... sfx=...
tunes=... vol=...` startup line from your run + a match/differ verdict vs the
original's feel.</p>
<textarea id=q8 placeholder="paste the audio: line here (this field alone closes OQ-027 when it carries a verdict)"></textarea>

<button onclick="post()">Post ruling</button>
<script>
function post(){
  const fields=[["D14 q0 map-clicks/rail/escape",q0v()],
    ["D14 q1 map-look",q1v()],["D14 q2 race-intro",q2v()],
    ["D14 q3 system-view",q3v()],["D14 q4 planet-view+project",q4v()],
    ["D14 q5 ships",q5v()],["D14 q6 research",q6v()],
    ["D14 q7 species+ability",q7v()],
    ["D14 q8 audio-line",document.getElementById('q8').value.trim()]];
  fields.forEach(f=>{const n=f[0].split(' ')[1];  // "D14 q3 ..." -> "q3"
    const t=document.getElementById(n+'n'); if(t&&t.value.trim())f[1]=(f[1]||'')+' | notes: '+t.value.trim();});
  fetch('/ruling',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title:"D14 phase-13/14 grading",
      fields:fields.filter(f=>f[1])})})
   .then(r=>{document.body.innerText=r.ok?'Posted. Thank you.':'POST failed '+r.status;});
}
function q0v(){const r=document.querySelector('input[name=q0]:checked');return r?r.value:''}
function q1v(){const r=document.querySelector('input[name=q1]:checked');return r?r.value:''}
function q2v(){const r=document.querySelector('input[name=q2]:checked');return r?r.value:''}
function q3v(){const r=document.querySelector('input[name=q3]:checked');return r?r.value:''}
function q4v(){const r=document.querySelector('input[name=q4]:checked');return r?r.value:''}
function q5v(){const r=document.querySelector('input[name=q5]:checked');return r?r.value:''}
function q6v(){const r=document.querySelector('input[name=q6]:checked');return r?r.value:''}
function q7v(){const r=document.querySelector('input[name=q7]:checked');return r?r.value:''}
</script>
</body></html>
"""

with open(os.path.join(PAGE, "index.html"), "w") as fh:
    fh.write(HTML)
for n, sz in made:
    im = Image.open(os.path.join(OUT, n))
    cols = len(im.getcolors(1 << 20) or [])
    print("%-28s %s %d colours %s" % (n, sz, cols, "OK" if cols >= 4 else "FLAT!"))
print("wrote index.html + %d crops" % len(made))
