# _wip_t428d.md — PLANET-SCREEN CYCLE 4 (PORT k4 FIELD + k5 SELECTOR LAW)

Task: docs/STATE.md NEXT ACTION t428d. (a) Port the 17np k4 starfield blit at
screen (7,115) under the widget paint, pin anchor + census, witness leg;
(b) budget-permitting resolve k5 push-order/selector statically. Frame
ALREADY EXACT (t406); no grid-gate re-hunt (t428b F1); no grid re-derivation
(OQ-014 CLOSED).

Sitting check [verified]: work/r1/playcap/live-timeline.jsonl mtime
2026-11-12 06:45 — unchanged since the t428c check. No new sitting; the
t428d assignment stands.

## F1 — BLIT-1 SELECTOR IS THE IMMEDIATE $4: THE RECORD LAW FOR THE FIELD
## BLIT EXISTS AND IS TRIVIAL (t428d) [VERIFIED — CORRECTS t428 F4]

work/t198_planwin.asm 0x3b9b1..0x3b9df, read against the S12.1 arg map
(shp.md §12.1 [verified FUN_0005caac prologue]: cdecl 5 args,
[EBP+8]=shape-struct, [EBP+0xc]=payload, [EBP+0x10]=selector,
[EBP+0x14]=x, [EBP+0x18]=y; pushes are REVERSE order):

  3b9b1 mov 0x1c(%ebp),%eax ; SENDMESSAGE field
  3b9b4 sar $0x10,%eax
  3b9b7 cmp $0xffffffff,%eax
  3b9ba je  0x3ba5e          ; GATE: all three blits skipped iff SENDMESSAGE==-1
  3b9c0 push $0x73           ; arg5 = y = 115
  3b9c2 push $0x7            ; arg4 = x = 7
  3b9c4 xor %edx,%edx
  3b9c6 push $0x4            ; arg3 = SELECTOR = 4  <-- IMMEDIATE
  3b9c8 mov $0x9f10c,%eax    ; shape cache base
  3b9cd mov 0x37c(%esp),%dx  ; = esp0+0x370 = WORD[0x6fd9c] = 44 = 17np (S23.1)
  3b9d5 call 0x1fc34         ; payload = desc for slot 44
  3b9da push %eax            ; arg2 = payload
  3b9de push %esi            ; arg1 = widget+4 (desc)
  3b9df call 0x5caac

=> blit-1 = 17np RECORD 4 AT SCREEN (7,115), UNCONDITIONAL once the gate
passes (PLSQUARE SENDMESSAGE=1 -> passes). t428 F4's "selector =
[EBP+0x1c]>>16 = SENDMESSAGE = 1 for blit 1" is WRONG — it conflated the
gate test with the arg pushes; the third push (0x3b9c6) is the selector and
it is the constant 4. This CLOSES seam T428c-A's "k4's record-index law for
THIS call site": there is no selector computation — record 4 is hardcoded,
consistent with the t428c registration measurement (k4 is the ONLY 17np
record that registers at (7,115), 158/269, shuffle control 6..12).

## F2 — THE FULL PAINT-BODY HEAD BLIT LAW (three blits) + PUSH-ORDER LAW
(t428d) [VERIFIED control flow, same listing]

PUSH-ORDER LAW, resolved once from the known-good anchor (per the task
brief): FIRST push = arg5 = y, SECOND = arg4 = x. Blit-1 gives (7,115),
which is EXACTLY the t428c-registered anchor [measured], so the law is
calibrated against measurement, not assumption.

- BLIT 1 (0x3b9df): 17np k4 at (7,115) — THE FIELD STARFIELD. (F1)
- BLIT 2 (0x3ba1e), GATED by BYTE[widget+0x18b] & 4 (0x3b9e4..0x3b9f4):
  pushes $0x128,$0x198 => y=296, x=408 — CORRECTS t428 F4a, which read
  x=296,y=408 (wrong order; the calibrated law above reverses it).
  SELECTOR: 0x3ba0f reads esp+0x374 AFTER three pushes (12 bytes) =
  esp0+0x368 = the value stored at 0x3b9aa:
      WORD[widget + 0x175 + 2*WORD[planet+0x16]]
  (planet = [0x43508]; +0x16 = the TYPE word the t427 row-string also
  reads). So the cond-2 selector is a PER-WIDGET, PER-PLANET-TYPE table at
  widget+0x175 — runtime widget state, NOT extractable from windows.txt.
  k5 (416x316) at (408,296) would cover only ~32% of its px on-screen; the
  t428c exhaustive scan found its peak at (224,107) with 14.6%, and the
  scan covered (408,296) too — so k5-at-blit-2 is NOT supported by witness
  B (the peak location disagrees). k5 identity REMAINS OPEN (seam
  T428c-A narrows to k5 only); blit-2's selector LAW is banked regardless.
- BLIT 3 (0x3ba4a): pushes $0x0,$0x0,%eax where eax = [EBP+0x1c]>>16
  (= SENDMESSAGE = 1 for PLSQUARE) => 17np record 1 at (0,0). [inferred]
  purpose unclear (k1 is the 9x9 busy-pop sprite — a 9x9 mark at the
  screen corner, or the desc clip rect suppresses it). NOT ported: no
  witness support (no measured 9x9 red sprite at (0,0) in witness B), and
  strict-close discipline says don't ship unmeasured art.

## F3 — PORT: k4 FIELD BLIT (t428d)

- planetstrip.h: kFieldLib=17np record 4, kFieldBlitOrigin{7,115} +
  fieldLibraryConforms() census gate (17np: 9 records, rec4 625x357 —
  dims from shp.md S23.2, re-censused by the pin against the extracted
  file).
- ui.cpp kScreenPlanet branch: blitShape(kLibs[5], 4, 7, 115) BEFORE the
  strip/grid art (vendor order: paint-body blit-1 precedes the grid loop
  and child panels).
- Pins tests/test_planetfield_t428d.cpp: (1) constant law record==4 /
  origin==(7,115) + conform gate accepts 17np, declines the gauge libs;
  (2) BYTE CENSUS on the decoded rec 4: dims 625x357, idx0 fraction
  >=99%, lit px in [200,400] (vendor 269) — binds the SPECIFIC record so
  changing kFieldRecord to k1/k5 fails on dims, k0 fails on speckle stats.
- Witness leg: t428_witness_census.py gains a FIELD check on OUR render
  crop: decode rec 4, compare its lit px at screen (7,115) against the
  render; MATCHED-set census with overpaint tolerance (bright mismatch =
  overpaint, dark mismatch allowed <N) — threshold >=50% matched vs the
  vendor's measured 58.7%.

## F3 LANDED — PORT + PINS + WITNESS (t428d) [MEASURED]

- planetstrip.{h,cpp}: kFieldRecord=4, kFieldBlitOrigin{7,115},
  kFieldRecordW/H 625x357 + fieldLibraryConforms() (9 recs, rec4 dims).
- ui.cpp kScreenPlanet branch: blitShape(kLibs[5], kFieldRecord, 7, 115)
  FIRST in the branch (under strip panels + lattice, vendor order).
- tests/test_planetfield_t428d.cpp x3: blit-law constants + on-screen span;
  library census (17np conforms, gauge libs decline); DECODED rec4 byte
  census: lit=269 bbox x26..620 y2..353 (matches the t428c register script
  exactly), scatter test, rec0 control (49558 lit px = 16.2% of 639x479 —
  measured this iteration, frame class vs speckle class). SUITE: 450/0/0.
- Witness scripts/t428_witness_census.py FIELD leg on OUR render crop:
  "lit=269 matched=246 bright(overpaint)=22 dark=1" -> VERDICT PASS.
  (Our own pipeline matches 246/269 = 91.4% — higher than the vendor's
  58.7% because our lattice/strip overpaint covers fewer star px than the
  vendor's state-17 composition on witness B. dark=1: one star px lands on
  a greyscale-ramp index edge [inferred]; well inside tolerance.)

## F4 — BLIT-2 SELECTOR = SIZE CLASS; BLIT-3 = k1 AT (0,0) (t428d)
[VERIFIED stack arithmetic — supersedes BOTH t428 F4a and this file's first
F4 draft, which mis-counted pending pushes]

esp0 := stack state at 0x3b984..0x3b9aa (zero pending pushes; the three
stores 0x3b984 esp+0x340 := u16[planet+0x14] (SIZE CLASS), 0x3b996
esp+0x370 := WORD[0x6fd9c] (=44=17np), 0x3b9aa esp+0x368 :=
WORD[widget+0x175+2*WORD[planet+0x16]] are all esp0-relative).

BLIT 1 (0x3b9c0..0x3b9df): pushes $0x73,$0x7,$0x4 (12B); read at 0x3b9cd
`mov 0x37c(%esp)` = esp0-12+0x37c = esp0+0x370 = 44 -> 17np. Selector
immediate 4. Anchor (7,115) [measured t428c]. (Consistency check PASSES:
the slot read resolves to exactly the store banked at 0x3b996.)

BLIT 2 (0x3b9f6..0x3ba1e), gate BYTE[widget+0x18b]&4:
  push $0x128 (y=296), push $0x198 (x=408)          [2 pushes, 8B]
  0x3ba00 `mov 0x348(%esp),%edx` = esp0-8+0x348 = esp0+0x340 = SIZE CLASS
      -> push %edx                                   [3 pushes, 12B]
  0x3ba0f `mov 0x374(%esp),%dx` = esp0-12+0x374 = esp0+0x368 =
      WORD[widget+0x175+2*WORD[planet+0x16]]  (the lib-slot table, t428 F4)
=> BLIT-2 LAW: lib = the per-widget-type slot table entry, RECORD = THE
   PLANET SIZE CLASS, at screen (408,296). No stale-frame state (the earlier
   draft's esp arithmetic was wrong; 0x348/0x374 with 2/3 pushes pending
   land exactly on the two esp0 stores — clean law).

BLIT 3 (0x3ba26..0x3ba4a): pushes $0x0,$0x0,(SENDMESSAGE>>16 = 1) ->
   slot esp0+0x370=44 again (0x3ba33 `0x37c(%esp)` with 12B pending),
   record 1 = the 9x9 busy-pop sprite, at (0,0). NOT ported: no witness
   support on B for a 9x9 red sprite at the screen corner; strict-close.

k5 CONSEQUENCE [measured + inferred]: blit-2 with slot 44 would blit 17np
k[size] (size 0..4) at (408,296) — record 5 is NOT reachable from the size
class, and the t428c exhaustive scan covered (408,296) with its peak at
(224,107) at 14.6%. So k5 is NOT any of the three paint-body blits under
slot 44. k5 either belongs to a widget whose +0x175-table entry resolves to
a DIFFERENT lib (the table is runtime widget state — windows.txt binds no
SHAPEFRAME for it), or to a paint body outside work/t198_planwin.asm. Seam
T428c-A narrows to: k5 widget identity OPEN; blit-2 law CLOSED (size-class
record, slot-table lib, (408,296), gate &4); blit-3 law CLOSED (k1@0,0,
unported for lack of witness).

## LEDGER (t428d)
Closes NOTHING (strict-close honest negative — planet-screen visuals have
no OQ owner; t414..t428c precedent). OQ-016/019/027 untouched.
