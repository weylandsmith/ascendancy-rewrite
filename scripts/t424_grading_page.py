#!/usr/bin/env python3
"""t424 grading page generator: D17-round sheet (chrome field + New Game laws).

Pattern owners: scripts/t397_grading_page.py (laws), scripts/t420_grading_page.py
(restated pattern + inventory). Builds work/r1/d1page/index.html + d11/*.png
crops. POSTs land as "USER:" lines via d1page/server.py (generic fields
handler). Server serves ROOT/index.html — no restart needed.

NOTE ON THE PAUSED SHEET (D17): the user paused the web ruling workflow and
answers freeform in chat. This sheet is the loop's shipped fallback per the
t424 assignment item (4) — it asks ONLY the two questions the round-4 (D17)
defect list maps onto after t422/t423 landed (chrome grain; New Game laws).
It re-asks NOTHING D16/D17 already asked, and carries no audio row (OQ-027
closes only on a final hearing verdict, already asked at D16).

Readability law (t397): text bands ship as NATIVE-RES 2x nearest crops.
Crop-by-measurement law: boxes come from t403_sheet_inventory runs + the
before/after diff-cluster scan run THIS row (below), never from memory.

Inventory MEASURED this row (t403_sheet_inventory + PIL diff clusters):
  t423c3-newgame    640x480 bg=(0,0,0) mass=34637 bands 420-480:9367
  t423c3-chip before/after diff 1102 px; cells cluster DESC ring (352..448,
      32..160) + header (384..448,32..96)  -> the chip-click grade crops
  t423c3-hostile vs newgame diff 3274 px; cells cluster ATMOSPHERE WHEEL
      (288..352, 384..480) + lore text (79..192, 352) -> red-orb grade crops
  map_t422          640x480 left band is the chrome-field grade zone
All six sheet shots md5-DISTINCT (verified this row).
Run with a PIL python:  ~/tools/revenv/bin/python scripts/t424_grading_page.py
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
# 1. CHROME FIELD (t422) — per-pixel Markov noise vs the old TV-static/cell
#    look. Grade zone measured: left perimeter band x0..6 + sidebar.
made.append(full("work/r1/loop/walk/map_t422.png", "t424-map-full.png"))
made.append(crop2x("work/r1/loop/walk/map_t422.png", (0, 30, 160, 300),
                   "t424-chrome-leftband.png"))
made.append(crop2x("work/r1/loop/walk/map_t422.png", (460, 30, 640, 300),
                   "t424-chrome-rightband.png"))
# 2. NEW GAME (t423 cycles 1-3) — wheels distinct + hostile orb + volume
#    preview + 2x portrait + chip-click colour reassign.
NG = "work/r1/loop/t423c3-newgame.png"
made.append(full(NG, "t424-newgame-full.png"))
made.append(crop2x(NG, (0, 350, 640, 480), "t424-newgame-bar.png"))
made.append(crop2x(NG, (300, 30, 640, 220), "t424-newgame-desc.png"))
# 3. HOSTILE atmosphere wheel (the vendor-truncated k12 record now paints).
made.append(crop2x("work/r1/loop/t423c3-hostile.png", (256, 384, 500, 480),
                   "t424-hostile-wheel.png"))
made.append(full("work/r1/loop/t423c3-hostile.png", "t424-hostile-full.png"))
# 4. CHIP CLICK before/after (DESC ring green -> pink, law FUN_000232ec).
made.append(crop2x("work/r1/loop/t423c3-chip-before.png", (330, 20, 500, 200),
                   "t424-chip-before.png"))
made.append(crop2x("work/r1/loop/t423c3-chip-after.png", (330, 20, 500, 200),
                   "t424-chip-after.png"))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>D17-round grading — chrome + New Game (t422/t423)</title>
<style>
body{background:#14161a;color:#d8dce0;font:14px/1.5 system-ui,sans-serif;margin:24px auto;max-width:1000px}
h1{font-size:20px} h2{font-size:16px;margin-top:28px;border-bottom:1px solid #333;padding-bottom:4px}
.hint{color:#9aa3ad;font-size:12px}
.row{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}
img{border:1px solid #444;background:#000;image-rendering:pixelated}
fieldset{border:1px solid #555;margin:10px 0}
label{margin-right:14px}
textarea{width:100%;height:44px;background:#1d2023;color:#d8dce0;border:1px solid #444}
button{background:#2d6cdf;color:#fff;border:0;padding:10px 22px;font-size:15px;margin-top:16px;cursor:pointer}
</style></head><body>
<h1>D17-round grading: chrome field + New Game screen (t422/t423)</h1>
<p class="hint">The ruling workflow is paused per your note — answer here only
if it's quicker than chat; freeform in chat is equally good. This sheet asks
ONLY what the round-4 defect list left open after the t422 chrome-field law
and the three t423 New Game cycles landed. Nothing D16/D17 already asked is
re-asked; no audio row. Best graded live after <code>git pull</code> (remote
main == 8525086 includes t421..t423c3); shots are the fallback.</p>

<h2>1. CHROME TEXTURE (t422) — "grainier/larger than original EVERYWHERE"</h2>
<div class="row">
<div><img src="d11/t424-map-full.png" width="640"><div class="hint">full map screen with the new field</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t424-chrome-leftband.png" width="320"><div class="hint">2x left perimeter band — per-pixel Markov noise (copy-left 5% / repeat-up 25% / per-column palette draw)</div></div>
<div><img class="zoom" src="d11/t424-chrome-rightband.png" width="360"><div class="hint">2x right band + sidebar edge</div></div>
</div>
<p class="hint">Measured: our vertical equal-neighbour rate 0.405 vs vendor
0.398 (was TV-static 1.46 lag-1); no cell grid any more. The exact vendor
generator is exhausted as a route (named seam, chrome.md SS4).</p>
<fieldset><legend>Chrome grain now close to the original?</legend>
<label><input type=radio name=q0 value="ok"> yes</label>
<label><input type=radio name=q0 value="partial"> partly (name it)</label>
<label><input type=radio name=q0 value="bad"> still wrong</label>
<label><input type=radio name=q0 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q0n placeholder="notes"></textarea>

<h2>2. NEW GAME screen (t423) — wheels, hostile orb, volume preview, 2x portrait</h2>
<div class="row">
<div><img src="d11/t424-newgame-full.png" width="640"><div class="hint">Neutral state: wheels k(idx)/k(count+2)/k10-12, volume starfield (circle r300 x depth +-300), 2x stretched portrait</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t424-newgame-bar.png" width="1280"><div class="hint">2x config bar: five density wheels distinct, species wheel, atmosphere wheels, 7 chips, Begin box (hover zone spins the field)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t424-newgame-desc.png" width="680"><div class="hint">2x DESC panel: racering ring + portrait</div></div>
</div>
<p class="hint">LIVE re-check: (a) no wheel frame repeats, none missing;
(b) the starfield fills a VOLUME and spins while the cursor is over the
Begin-button zone; (c) the portrait reads the size you remember (the vendor
stretches the 49px record 2x — cited site 0x52834).</p>
<fieldset><legend>New Game wheels + preview + portrait right now?</legend>
<label><input type=radio name=q1 value="ok"> yes all</label>
<label><input type=radio name=q1 value="partial"> partly (name which)</label>
<label><input type=radio name=q1 value="bad"> still bad</label>
<label><input type=radio name=q1 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q1n placeholder="notes"></textarea>

<h2>3. HOSTILE atmosphere orb (t423) — the truncated vendor record now paints</h2>
<div class="row">
<div><img class="zoom" src="d11/t424-hostile-wheel.png" width="488"><div class="hint">2x atmosphere wheel at Hostile: red spiked orb (3cfgnew k12 — the truncation is IN the shipped archive; our decoder now accepts the last record)</div></div>
<div><img src="d11/t424-hostile-full.png" width="640"><div class="hint">full screen, Hostile selected</div></div>
</div>
<fieldset><legend>Hostile-atmosphere art shows and looks right?</legend>
<label><input type=radio name=q2 value="ok"> yes</label>
<label><input type=radio name=q2 value="partial"> shows but wrong (name it)</label>
<label><input type=radio name=q2 value="bad"> no</label>
<label><input type=radio name=q2 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q2n placeholder="notes"></textarea>

<h2>4. PLAYER-COLOUR chip click (t423c) — re-assigns every race's colour</h2>
<div class="row">
<div><img class="zoom" src="d11/t424-chip-before.png" width="340"><div class="hint">before: DESC ring green (idx 0)</div></div>
<div><img class="zoom" src="d11/t424-chip-after.png" width="340"><div class="hint">after clicking chip 4: ring pink (idx 3), AI races re-draw distinct colours</div></div>
</div>
<p class="hint">LIVE: click any chip in the row under the panels — the DESC
ring changes to that colour and the six AI races get distinct other colours
(vendor law FUN_000232ec: your slot exact, AI rand()%7 no-collision).</p>
<fieldset><legend>Chip click behaves like the original?</legend>
<label><input type=radio name=q3 value="ok"> yes</label>
<label><input type=radio name=q3 value="partial"> partly (name it)</label>
<label><input type=radio name=q3 value="bad"> no</label>
<label><input type=radio name=q3 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q3n placeholder="notes"></textarea>

<button onclick="post()">Submit grading</button>
<script>
function post(){
  const fields=[];
  for(let i=0;i<4;i++){
    const r=document.querySelector('input[name=q'+i+']:checked');
    if(!r) continue;
    let v=r.value;
    const t=document.getElementById('q'+i+'n');
    if(t&&t.value.trim()) v+=' | notes: '+t.value.trim();
    fields.push(["D17r2 q"+i+" = ", v]);
  }
  if(!fields.length){alert('answer at least one row');return;}
  fetch('/ruling',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title:"D17-round grading (chrome + new game)", fields:fields})})
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
