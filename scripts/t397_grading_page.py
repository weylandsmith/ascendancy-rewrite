#!/usr/bin/env python3
"""t397 grading page generator: builds work/r1/d1page/index.html + d11/*.png
crops for the D11 eyes-on asks (docs/DECISIONS.md D11).

D9 law: the user answers visual pages fast and text asks never, so every ask
ships as an image pair + radio buttons that POST a "USER:" block to
docs/DECISIONS.md (via d1page/server.py).

Readability law (t397): a 640x480 screenshot scaled down by the browser is
UNREADABLE, which is how clean screens get graded "garbled". Text bands are
shown as NATIVE-RES 2x nearest-neighbour crops next to the full frame.

Vendor-reference images (scratchpad/*-original.png) are copied into the page
dir and served LOCAL-ONLY. They are copyright Maxis/Hasbro-derived media:
NEVER publish, never commit (d1page/ is under gitignored work/).

Idempotent: re-run after any new loop capture to refresh crops.
"""
import os, shutil, sys
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
# T393 title (post-fix): hotkey hint lines + button stack. D11 item 1.
made.append(full("work/r1/loop/t393-title.png", "t393-title-full.png"))
made.append(crop2x("work/r1/loop/t393-title.png", (140, 355, 500, 435), "t393-title-hints.png"))
made.append(crop2x("work/r1/loop/t393-title.png", (180, 130, 470, 300), "t393-title-art.png"))
# T393 new game: race rows + Begin button. D11 item 2.
# Geometry MEASURED (column-brightness runs): sidebar at x 502..632, race rows
# y 258..321, Begin bottom-right. An early crop at x 0..400 caught NONE of it
# (frac_bright 0.012) — always measure before cropping.
made.append(full("work/r1/loop/t393-newgame.png", "t393-newgame-full.png"))
made.append(crop2x("work/r1/loop/t393-newgame.png", (495, 95, 640, 375), "t393-newgame-rows.png"))
made.append(crop2x("work/r1/loop/t393-newgame.png", (495, 430, 640, 478), "t393-newgame-begin.png"))
# T394 map chrome. D11 item 3. map-turn1.png deliberately EXCLUDED (black
# post-quit teardown frame — grading it would misreport a black screen).
# Chrome lives in the RIGHT SIDEBAR (ovals, arrows, menu buttons, species
# squares) — not the bottom. Gradient-band rows measured over x 440..639.
made.append(full("work/r1/loop/t394-map.png", "t394-map-full.png"))
made.append(crop2x("work/r1/loop/t394-map.png", (430, 0, 640, 240), "t394-map-side-top.png"))
made.append(crop2x("work/r1/loop/t394-map.png", (430, 240, 640, 480), "t394-map-side-bot.png"))
# Vendor reference (user-supplied screenshots; local serving only, never ship).
for p, nm in [("scratchpad/newgame-original.png", "vendor-newgame.png"),
              ("scratchpad/galaxymap-original.png", "vendor-galaxymap.png")]:
    sp = os.path.join(ROOT, p)
    if os.path.isfile(sp):
        shutil.copyfile(sp, os.path.join(OUT, nm))
        made.append((nm, Image.open(os.path.join(OUT, nm)).size))

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>Ascendancy rewrite — D11 grading</title>
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
<h1>D11 — grade the pushed rebuild (remote main == 3be7e9af6c24)</h1>
<p class="hint">One line each suffices. Radio answers + optional notes post
straight into docs/DECISIONS.md as a USER: block; the loop picks it up on its
next wake. Crops are 2x nearest-neighbour of the exact text bands — if a crop
is readable but the live window is not, say so in the note (that is a window
size problem, not a font problem). The old D1 sheet is archived at
/index-d1.html.</p>

<h2>1. TITLE screen (ours: t393, Xvfb capture)</h2>
<div class="row">
<div><img src="d11/t393-title-full.png" width="640"><div class="hint">full frame</div></div>
<div><img class="zoom" src="d11/t393-title-hints.png" width="720"><div class="hint">2x crop: hotkey hint lines</div></div>
</div>
<div><img class="zoom" src="d11/t393-title-art.png" width="580"><div class="hint">2x crop: art behind the buttons</div></div>
<fieldset><legend>Are the hint lines readable (no garble) and the art visible?</legend>
<label><input type=radio name=q1 value="ok"> readable + art OK</label>
<label><input type=radio name=q1 value="garbled"> text garbled</label>
<label><input type=radio name=q1 value="no-art"> no art behind buttons</label>
<label><input type=radio name=q1 value="saw-live"> answered from my live Athens run, not these shots</label>
</fieldset>
<textarea id=q1n placeholder="notes (optional)"></textarea>

<h2>2. NEW GAME screen</h2>
<div class="row">
<div><img src="d11/t393-newgame-full.png" width="640"><div class="hint">ours, full frame</div></div>
<div><img src="d11/vendor-newgame.png" width="640"><div class="hint">your original screenshot (reference)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t393-newgame-rows.png" width="580"><div class="hint">2x crop: race rows (right panel)</div></div>
<div><img class="zoom" src="d11/t393-newgame-begin.png" width="580"><div class="hint">2x crop: Begin New Game (bottom-right)</div></div>
</div>
<fieldset><legend>Full-screen starfield, race rows readable, Begin works bottom-right?</legend>
<label><input type=radio name=q2 value="ok"> all good</label>
<label><input type=radio name=q2 value="clipped"> still clipped (paste the `ui window WxH (logical 640x480)` startup line in notes)</label>
<label><input type=radio name=q2 value="rows-bad"> rows unreadable/wrong</label>
<label><input type=radio name=q2 value="begin-bad"> Begin button wrong</label>
</fieldset>
<textarea id=q2n placeholder="notes / the ui window line"></textarea>

<h2>3. GALAXY MAP + rail buttons</h2>
<div class="row">
<div><img src="d11/t394-map-full.png" width="640"><div class="hint">ours, full frame</div></div>
<div><img src="d11/vendor-galaxymap.png" width="640"><div class="hint">your original screenshot (reference)</div></div>
</div>
<div class="row">
<div><img class="zoom" src="d11/t394-map-side-top.png" width="840"><div class="hint">2x crop: sidebar top — turn-counter ovals, NEXT TURN arrow, menu buttons</div></div>
<div><img class="zoom" src="d11/t394-map-side-bot.png" width="840"><div class="hint">2x crop: sidebar bottom — spin/zoom cluster, species squares</div></div>
</div>
<fieldset><legend>Turn-counter ovals, NEXT TURN, spin/zoom cluster, species squares — any still wonky?</legend>
<label><input type=radio name=q3 value="ok"> all good</label>
<label><input type=radio name=q3 value="wonky"> something still wonky (name it in notes)</label>
<label><input type=radio name=q3 value="saw-live"> answered from my live run</label>
</fieldset>
<textarea id=q3n placeholder="notes"></textarea>

<h2>4. SOUND — the one line that closes OQ-027 by itself</h2>
<p>Boot <code>./build/ascendancy --data DIR --ui</code> once and paste the
startup line that starts <code>audio:</code> (looks like
<code>audio: driver=... sfx=86 tunes=3 vol=127</code>) — or the
<code>degraded: silent ...</code> line if you see one instead. Its text alone
decides dead-card vs code-gap.</p>
<textarea id=q4 placeholder="paste the audio: / degraded: line here"></textarea>

<h2>5. D11b — privacy disposition (your call)</h2>
<p>GitHub GC may still serve the OLD commit lineage (tip 5373c66aa637) which
contained your personal ISP address — it is public until they sweep. Optional:
email support.github.com citing <code>weylandsmith/ascendancy-rewrite</code> +
old tip <code>5373c66aa637</code> (also covers the manual-pages eb79da3
lineage). The loop will not act without your word.</p>
<fieldset><legend>Send the GC request?</legend>
<label><input type=radio name=q5 value="send"> send it</label>
<label><input type=radio name=q5 value="drop"> drop it</label>
</fieldset>
<textarea id=q5n placeholder="notes (optional)"></textarea>

<p><button onclick="submitRuling()">Submit ruling</button>
<span id=out class="hint"></span></p>
<script>
function submitRuling(){
  const g=id=>{const e=document.getElementById(id);return e?e.value.trim():""};
  const r=id=>{const e=document.querySelector('input[name='+id+']:checked');return e?e.value:"(no answer)"};
  const body={title:"D11",fields:[
    ["D11 title screen =",r("q1")+" "+g("q1n")],
    ["D11 new game =",r("q2")+" "+g("q2n")],
    ["D11 galaxy map =",r("q3")+" "+g("q3n")],
    ["D11 audio line =",g("q4")||"(no answer)"],
    ["D11b privacy =",r("q5")+" "+g("q5n")]]};
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
