# tPF-5 WITNESS — INDUSTRY TILE ANCHOR (D28 item 10) [run after build]

Law: ui::stripGaugeBlitPos adds the record bbox (L,T) to the windows.txt rect
origin (vendor FUN_0005caac 0x5cb61/0x5cb6a add [entry+8]/[entry+0xc] to the
pushed x/y). planind rec T ladder {23,20,11,5,1}.

PLAN (port witness, seed 5 --species 0, port window 640x480 :99 — same rig as
scripts/tplb2_port_witness.sh; build BOTH run_tests AND ascendancy FIRST):
 1. open planet view for star 0 (Amoroso I); shot rest.png
 2. LOG LINE: extend the strip paint with one printf
    "ui strip planind rec <k> anchor (L,T) at (x,y)" (law line, t428d
    precedent) OR compute offline from the campaign's gauge selector —
    the selector for Amoroso I industry is small (rec 0..1 -> T=23).
 3. PIXEL DIFFERENTIAL (anti-vacuity, tplb2_census shape):
    - band ABOVE the content: rect rows y0..y0+T-1 must show the FIELD/
      backdrop (NOT the industry art) -> sample row y0+2 inside the PLIND
      rect (x 123..230) and compare vs the same row in the PLRES rect
      (both should be backdrop-ish, NOT industry-art colours);
    - the content must reach the rect BOTTOM: row y1 (106) inside PLIND must
      DIFFER from row y1 inside PLPOP (different art) and must NOT be the
      uniform backdrop;
    - MUTATION CONTROL: rebuild with stripGaugeBlitPos -> {x0, y0} and rerun
      the same census; the band rows must flip to industry art (that is the
      user's "too high, top cut off" shape). If the census cannot tell the
      two builds apart, the witness is VACUOUS — say so, do not PASS it.
