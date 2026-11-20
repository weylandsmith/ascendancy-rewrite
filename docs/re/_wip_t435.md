# t435 WIP — RESEARCH SCREEN CYCLE (grade t419 rebuild vs D15 spec + live re-check)

## F0 PREMISE + CONTROL PLANE
- Assignment: docs/STATE.md NEXT ACTION t435 (queue row STATE.md:2567-2571).
  Row text: grade the t419 rebuild against the D15-addendum spec (3D tree,
  right info frame, Z-rotate + scroll controls, corner popup) + the LIVE
  re-check list (spin latches per t425 law, Esc instant, no CPU peg — ps -o
  pcpu assertion); fix what fails.
- Sitting check: live-timeline.jsonl mtime 2026-11-12 06:45 predates the last
  iterations (t434/t434b 2026-11-20) -> NO new play, assignment stands.
- Tree clean at launch (HEAD 879c23b).
- INHERITED STATE: t408 researchview law (_wip_t408 S1-S7 seams) + t419 3D
  rebuild (_wip_t419 F7): ResearchLayout one-shot, researchNodeScreen 3D
  flat-XY field rest-scale-1, pressSpin latch + pump kSpinTickMs=1000 (t425
  cadence law), move pair = resPanY scroll, corner popup mouse.shp k5,
  witness 5/5 PASS, suite 421 at the time.
- t419 RE LEG was an honest negative ONLY because Ghidra's defined-strings
  table returned 0 that session. Ghidra 8089 RESPONDS this session (HTTP 0).
  datafiles.md:47 already banks the reswin.txt referrer sites 0x4712b+0x47579.
  R-t423c binds: string->paint route is NOT a data-ref census for the PAINT
  (strcmp chains); route = vtable [win+0xa7]+0xc. t423c3 banked the call-site
  shape: `mov ebx,[ebp+0xa7]; mov edx,0x1c01; mov eax,ebp; call [ebx+0xc]`.
- Carry-warnings (t434b): rail switch = RESEARCH widget (474,208-632,238),
  click centre (553,223) [ui-runtime.md:187 measured], NOT TOG*; census
  scripts need ~/.hermes/hermes-agent/venv/bin/python (numpy+PIL).

## F1 LIVE RE-CHECK RUN 1 (scripts/t419_research3d_witness.sh, /tmp/t419_shots)
BUILD current (cmake --build all targets green). Witness outcome 4 PASS / 1 FAIL:
  PASS study click (Spacetime Surfing), PASS popup shown, PASS popup hidden,
  PASS CPU delta 144 ticks/4s (~36% core, NOT pegged), FAIL esc_ms=timeout.
THE FAIL IS A WITNESS-ORDERING BUG, NOT A PRODUCT DEFECT [verified from
app.log]: t425(d) made the corner-popup CLICK fire doEscape — the script's
"X click 2 2" at the corner ALREADY exited research ("ui corner exit popup
click" then "ui screen Research -> map (esc)" BEFORE the K Escape line), so
n0 was counted on the MAP screen and the subsequent map-level Escape logs no
"ui screen" line -> poll never trips. Esc-on-research itself worked INSTANTLY
(the popup-click path IS the doEscape chain, t409/t410 law). Fix: move the
Esc-instant block BEFORE the corner-popup block.
SPIN LAW WITNESSED: pixel diff off shots (numpy): open->study 983 px (panel
+ gold ring only); spin1 27701 px bbox x7..600 y46..472 (whole-field 3D
motion); spin2 27081 px (still moving at 2 deg/s cadence); stopped == spin2
BYTE-IDENTICAL (md5 2b196245) -> after the second rotate press the pump
applied NO further motion == dialLatch stop law live. The two rotate presses
logged "ui research pan 0 0" twice (rotate dials share the pan log line —
cosmetic, law-correct: pressSpin pair).
xsend.c:128 "(window died before release)" is a MISLABELLED message: the
press loop always exits press==-1 for non-key full clicks (loop decrements
past 0); clicks DID land (log lines prove). Cosmetic tool fix, low priority.

## F2 GHIDRA STATE NOTE (t419 failure-mode root cause)
t419's RE-leg honest negative ("defined-strings table returns 0 even for
known-present strings") = NO PROGRAM LOADED on the headless server that
session. This session: server v7.0.0-headless UP (8089); work/
ascend_restored.bin loaded as Raw Binary x86:LE:32 gcc imagebase 0
(0 functions until analysis/scripted create; ships.md:546 precedent used
project work/ghp5 which carries prior analysis).

## F3 WITNESS FIXED + RE-RUN: 5/5 PASS (2026-11-20)
Ordering fix landed in scripts/t419_research3d_witness.sh (Esc block BEFORE
the corner block; popup block re-enters research via rail (553,223) first).
Result: study PASS, popup shown/hidden PASS, esc_ms=204 PASS, CPU delta 144
ticks/4s (~36% of one core) PASS. LIVE RE-CHECK LIST CLOSED: spin latch law
witnessed by md5 (stopped frame == spin2 frame BYTE-IDENTICAL after the
second dial press -> pump applies nothing when latched off); Esc instant;
no CPU peg.

## F4 NATIVE-VISION GRADE (port research-study.png vs vendor t252, side-by-side
/tmp/t419_shots/t435_grade.png):
MATCHING: header green centred top band; black tree field with thin-blue
prereq lanes; ring nodes; right panel x484..632 "Current Project:/name/(N
days)/Allows/unlock" all green centred; two arrow boxes lower-right.
DEFECTS (vendor has, port lacks) — ranked by evidence-available fix cost:
 D1 ARROW BOXES are vector glyphs; vendor paints 20res.shp SHAPEFRAME faces
    (windows.txt children carry SHAPEFRAME 0..3; t391: 20res N=6, k0 15x30).
    FIXABLE NOW (art on disk, geometry cited) -> t408 seam S4.
 D2 SPECIES CREST box top-left (0..32,0..32) absent on ours (vendor green
    crest glyph in a beveled box; t408 F6 "1starmap k3 analog slot").
 D3 PANEL ART: vendor disk-icon (~46px gizmo face, y~60) + planet art (~60x46,
    y~215) absent on ours (code draws text only). Needs gizmo/planet record
    join — larger; name as seam.
 D4 chrome frame around the tree field + margins = t433's row (EXACT memory-
    surface census), NOT this row's evidence class. Do not touch.
 D5 footer "Esc: return to galaxy" is OURS-only (vendor paints nothing there)
    — keep (affordance, D15 era), not a defect claim either way.

## F5 20res.shp FACE LAW [MEASURED via tools/shp_pngdump + game.pal + ASCII census]
Records decode 6/6 via the rewrite's own decoder: k0 15x30, k1 14x30, k2 30x15,
k3 30x14 (k4/k5 = 30x15/30x14 duplicates of the vertical pair — no windows.txt
record consumes them; the t408 F6 "third arrow pair at (600,442)" candidate,
NOT blitted without a record). Glyph reading (luminance ASCII, exact):
k0 LEFT double-arrow (apex left, diamond knob above), k1 RIGHT mirror,
k2 vertical pair w/ top diamond (MOVEUP face), k3 DOWN arrow w/ diamond
(MOVEDOWN face). BG (12,32,48) == the port's existing box fill — the faces
CARRY their own panel background. Rect-vs-record dims match per child
(RESROTLEFT 524,442-539,472 == 15x30 k0; RESROTRIGHT 540..554 == 14x30 k1;
RESMOVEUP 563,442-593,457 == 30x15 k2; RESMOVEDOWN 563,458-593,472 == 30x14 k3).
=> SHAPEFRAME n indexes 20res.shp record n DIRECTLY (TYPE-100 binds
DATA\20RES.SHP; statuslaw.cpp kScreenResearch->"20res.shp" agrees).

## F6 D1 + D2 FIXES LANDED (measured on our render)
D1: ui.cpp research painter blits 20res.shp records 0..3 at the verbatim rects
    (libFor(kScreenResearch) == the 20res slot; vector fallback ONLY if the lib
    refused). Our-render census off the witness shot: rotleft box
    {(12,32,48)x220,(190,255,255)x29,(48,81,138)x24} == decoded k0 histogram
    EXACTLY; rotright +18 (255,121,48) == k1; moveup 243 == k2; movedown 171 ==
    k3. RECT LAW correction [measured]: these child rects are HALF-OPEN
    (539-524=15==k0.w etc — the inclusive +1 reading fails 4/4).
D2: player PLAQUE on the research header (t426 map law reused verbatim: frame
    15x25 idx19 outline + navy fill at (10,10) + raceflag k<species>). Census
    of 38 banked vendor *_game.png: crest green bbox x10..24 y10..34 on EVERY
    screen (fleet_row1_leftclick is the one 0-px exception — a modal covers
    it); our post-fix render bbox x10..24 y10..34 EXACT (green px count
    differs by species record, expected: seed-5 species != Chamachies).
PINS tests/test_resface_t435.cpp x2 (record==rect dims half-open for all four
faces + decode sizes; fill index (12,32,48) is the PLURALITY colour of every
face, >1/4 of pixels). Suite 460/0 (458+2).
WITNESS re-run 5/5 PASS incl esc_ms=204.
CLOSE GRADE: live re-check list PASS x3 (latch md5-equality, Esc 204 ms, CPU
36% core); D1 CLOSED with art; D2 CLOSED with plaque; D3 (panel disk-icon +
planet art join) and D4 (chrome frame = t433's row) remain NAMED SEAMS;
D5 footer = port affordance, kept. Row t435 closes per the close law: no
fixable-with-available-evidence defect remains (D3 needs the gizmo/planet
record->panel join law which is NOT available offline — the vendor panel art
chain was never in a captured window, t419 F6 precedent; naming it again with
the closure witness: BPPM stop inside the reswin panel paint once the vtable
chain [win+0xa7]+0xc for STATE 20 is identified live).
LEDGER: closes NOTHING (strict-close — the research-screen complaints have no
OQ owner; t408/t419 precedent; OQ-016/019/027 untouched).
