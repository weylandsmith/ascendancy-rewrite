# t434b WIP — COMPLETE SHIPS SCREEN (leg 1 witness run; leg 2 row-art identity)

Carried premise: t434 landed ink/selection law (docs/re/_wip_t434.md F0-F6).
Leg 1 = RUN scripts/t407_fleetlist_witness.sh + scripts/t434_witness_census.py.
Leg 2 = row-art library identity via fn 0x50d12 blit arg chain (NOT filenames,
R-t434).

## F0 ENV NOTE
Census scripts need numpy+PIL: NOT in .venv nor system python3; present in
~/.hermes/hermes-agent/venv/bin/python (numpy 2.4.3, PIL 12.3.0). Run census
with that interpreter.

## F1 LEG-1 WITNESS RUN 2026-11-20 (run work: /tmp/t434_shots)
scripts/t407_fleetlist_witness.sh VERDICT PASS:
  ui screen map -> Ships (FLEET); ui fleet select row 0; ui fleet deselect
  (was row 0); ui fleet scroll down 1 / scroll up 0; zero laser01.
Census first pass (fleet-rows.png, script as-written): name_green=0
loc_green=0 cyan=0 row0_white=69 navy_frame=0 -> VERDICT FAIL.
Direct pixel census (band color histograms, off both shots):
  fleet-rows.png  row0 name band: bg(16,16,24)x4291 + WHITE(255,255,255)x69;
                  row0 loc band:  bg x6443 + WHITE x397; rows1-3: pure bg.
  fleet-final.png row0 name band: bg + (0,170,81)x69; row0 loc: bg+(0,170,81)
                  x397; rows1-3 pure bg.
  INK-YS CANON (x140..570): text ink occupies y62..72 and y76..83 — NOT the
  script's assumed y56..76 window.
FINDINGS:
  (a) INK LAW IS CORRECT ON OUR RENDER — the t434 FAIL was a CENSUS-SCRIPT
      bug x2: (1) wrong ink y-window (assumed y56..76, actual 62..83) so the
      green count sampled blank background; (2) it censused fleet-rows.png,
      shot while row 0 was SELECTED — selected ink is WHITE by law (0xf3), so
      "green on every row" was never possible there. Green (0,170,81) IS
      present on fleet-final.png row 0 after deselect == pal[24] family;
      white-on-selected + green-after-deselect + zero cyan + navy_frame=0 all
      corroborate the t434 law end-to-end on our own render.
  (b) MULTI-ROW GAP IS REAL: seed-5 sitting has exactly ONE ship in transit at
      the witness turn (~t278), so rows 1-3 are legitimately empty. The
      unselected-race-ink leg (green on rows 1..N) needs >=2 ships in transit
      simultaneously -> new witness t434b must advance to a turn where the
      census count >=2 (plan: probe select-log/ship census per turn, stop when
      two in-transit ships exist).

## F2 LEG-1 CLOSED (census fixed, VERDICT PASS on the same run)
scripts/t434_witness_census.py rewritten per F1: ink window y+10..y+32
(=y62..84), green censused on fleet-final.png (post-deselect), white on
fleet-rows.png (selected), navy-frame absent. Result on /tmp/t434_shots:
name_green=69 loc_green=397 cyan=0 row0_white=69 navy_frame=0 -> VERDICT PASS.
t434's ink/selection law is now MEASURED on our own render (green race ink ==
pal[24] family (0,170,81); white == 0xf3 selected override; zero cyan; vendor
frame/marker absence). HONEST SCOPE NOTE: seed-5 sitting holds ONE ship at the
witness turn, so green was witnessed on row 0 post-deselect only; multi-row
per-race ink needs >=2 ships in transit (carried seam, not a leg-1 failure).

## F3 LEG-2 ROUTE (static account off work/t434_fleetwin.asm, pre-live)
CALL census of fn 0x50d12: 0x1fc34 x10 (shape-cache fetch), 0x5caac x9 (blit),
0x21a20 x9 (string getter), 0x76c79 x7 (SPRINTF — banked law aicode.md:642,
NOT a blit). The t434 F2 "blit" labels on the 0x21a20/0x76c79 chains were
mislabels; the real row-art blit is the 0x50d39..0x50d49 site:
  eax=0x9f10c (shape-cache singleton, shp.md:410), dx=WORD ds:0x895c2 (slot
  global) -> call 0x1fc34 -> eax = shape struct; pushes $0x32(y=50), $0x41,
  BYTE_HI([ship+0xa7]), eax, ebp -> call 0x5caac.
NO CONTRADICTION with "0x41=65 cannot exist in a 4-record lib" (t434 F5):
per the E6 law (work/combat_decomp/5caac.c:52,58-64) param_3 indexes the
PAYLOAD DIRECTION TABLE dir=p2+8+8*sel, dir_off=u32[dir], rec=p2+dir_off —
65 is a DIR index of the payload surface, not an .shp record count. So the
open question narrows to: WHAT is p2 (the smship lib payload or a composite
surface) and WHAT are rec dims. Live legs:
  art_blit 0x50d49 (before-call map [esp]=p1 struct,[+4]=p2 payload,
           [+8]=sel,[+c]=x,[+10]=y; dump struct head, payload head magic,
           dir entry sel, rec body dims) + slot globals 0x895c2/0x895c6/0x6a14
  fc34_art 0x50d34 (cache ptr + slot word pre-call)
  sprf_ctl 0x50dd4 (sprintf inside the FIRST state-branch leg = positive
           control that the art-blit leg executed)
  orbit_blit 0x50e0e (the t434 F2 orbit site, arg law same)

## F4 F5-CONTRADICTION RESOLVED STATICALLY (t434 F5's 0x41 reading was wrong)
Push-order account at 0x50d39..0x50d49 (cdecl, first-pushed = LAST param):
  push 0x32 -> p5=y=50; push 0x41 -> p4=x=65; push edx -> p3=sel=
  BYTE_HI([ship+0xa7]); push eax -> p2=fc34 payload; push ebp -> p1=struct.
Matches FUN_0005caac's map (param_1 struct, param_2 table base, param_3 sel,
param_4/5 origin — work/combat_decomp/5caac.c:52,58-64). t434 F5's "record
immediate 0x41=65 cannot exist in a 4-record lib" MISREAD the x-coordinate as
the selector: the selector is DYNAMIC HI([ship+0xa7]) and smship libs hold
N=4 records [measured offline this iteration: smship19/00/01 + dkship19
headers all N=4, table_size 40]. No contradiction remains.
OFFLINE CONTAINER FACTS (extracted/ascend01/data): smship19 recs at
0x38/0x49f/0xf56/0x2136; dims per S16 law: rec0 (32,9) pair@rec, rec1 (49,15),
rec2 (49,17), rec3 (67,22) pairs @rec+0x10; recs1-3 head u16x4 =
(111,157,56,79) == slot-N-1 metadata (shape box + signed hotspot, hotspot
i32x2 = (-27,-17) — bbox-vs-anchor law the live stop settles).
t434 F3 slot witness stands: 0x895c2 == 14 -> cache name 'DATA\SMSHIP19.SHP'
32/32 fleet-open saves. REMAINING GAP = which record (sel value) + dims +
origin law produce the drawn t253 bbox x27..121 y71..112. Closure = ONE live
BPPM stop at 0x50d49 (args + table + rec dump) + 0x50d34 (slot word + cache
name). Scripts: scripts/r434b_art_session.py (adapted r428f law stack:
scratch game-wp, Oct-29 RESUME.GAM t1086, EXPECT_BASE 0x1BF4D8, poll-by-break
cold legs, delete-fired-BP resume).

## F5 LIVE WITNESS LANDED (run work/r1/dbg-t434b2-a1-20261120-035003)
Attempt-1 (dbg-t434b-a1) clicked TOGSHIPS (557,403) per windows.txt — WRONG
widget (screen diff 924px, zero stops). FLEET rail widget rect 474,169-632,199
(SENDMESSAGE 1 SENDPARAM1 18) is the screen-switch; click (553,184). LAW:
rail-screen switch = FLEET widget, not TOGSHIPS.
Attempt-2 stops (poll-by-break, cold legs):
  FC34  cache_ptr=0x2e110c slot_word=14 (== t434 F3: slot 14 = DATA\SMSHIP19)
  BLIT  p1=0x2e8974 p2=0x3be78c SEL=1 arg_x=65 arg_y=50
        struct: pixptr 0x28a4f8 W=8 H=47 (dest row surface)
        payload head "1.10" N=4 tsz=0x28; slots 0x49f/0xf56/0x2136 —
          BYTE-IDENTICAL to extracted smship19.shp header.
        dir entry sel=1 -> rec at +0x49f; rec head 6f 00 9d 00 38 00 4f 00
          (bbox 111,157,56,79) hotspot (-46,-26); dims rec+0x10 = (49,15).
        E6 origin law: x = 65 + struct[+4](8) + rec[+8](-46) = 27
                        y = 50 + struct[+8](47) + rec[+0xc](-26) = 71
        => origin (27,71) == t253 MEASURED sprite bbox top-left x27 y71.

## F6 IDENTITY CLOSED BY CONTENT (offline arbiter over the banked dump)
scripts check: MEM_ARTLIBFULL_003BE78C.BIN (16384 B) vs every
extracted/*/*/data/*.shp — EXACTLY ONE match:
extracted/ascend01/data/smship19.shp (15331 B, full containment).
=> ROW-ART LIBRARY IDENTITY [MEASURED]: the ships-screen row art is the
   cache payload of DATA\SMSHIP19.SHP (the PLAYER race's smship lib; t434 F3
   slot-14 witness and the content match now AGREE — no longer inferred).
   Record = dir entry sel=1 (sel = BYTE_HI([ship+0xa7]), live value 1),
   rec at payload +0x49f, bbox u16x4 (111,157,56,79), hotspot i32x2
   (-46,-26), dims u32 pair @rec+0x10 = (49,15), stream @rec+0x18 (S16 law).
   ORIGIN LAW [MEASURED, E6]: x = arg_x(65) + struct[+4](8) + s32[rec+8](-46)
   = 27; y = arg_y(50) + struct[+8](47) + s32[rec+0xc](-26) = 71 — EXACTLY the
   t253 measured sprite bbox top-left (x27 y71). The hotspot IS the
   anchor-offset: origin = push_origin + dest_struct_wh + hotspot.
   SIZE RESIDUAL (honest): record dims (49,15) do not equal the t253 ink
   extent (95x42); the t253 region x27..121 y71..112 likely includes the
   gizmo-icon rows (t434 F2 item iii, painted later at the same row). NOT
   claimed closed.
