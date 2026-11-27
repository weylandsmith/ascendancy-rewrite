# _wip_tPF6b — vendor PLANLIST per-cell filter site (iteration log)

Task: STATE NEXT ACTION TPF6-B — recover the list-construction function behind
the planet-screen PLANLIST popup and whether it gates rows by the ARMED CELL;
or certify its absence (honest negative, row stays open per strict-close).

## P0 — CHECKER CALL-SITE CENSUS (exhaustive rel32, obj0 code range
[0x14bb0,0x82bb0), scripts/tPF6b_callscan.py, work/ascend_restored.bin)
checker 0x3830c: 14 sites -> fn attribution (functions_full.tsv):
  0x387bd  fn 0x3875c   (queue-arm chain, t341 census)
  0x38a65  fn 0x38840   (queue-arm cmd0, t341 sole writer)
  0x3afe8 0x3b43d 0x3b786 0x3bab7 0x3c2da   fn 0x3aa0a  (PLANETALLOC/planet
      screen UI fn — same fn that fetches widget 0x1f06=PLANLIST at 0x3c7bd)
  0x3d533 0x3d579      fn 0x3d2fe   (popup composition, tPF-2d D4/D6)
  0x3f30d              fn 0x3f130   (the t406 F2b "selector" legs)
  0x3fcf0 0x3fdb8 0x3fe22 0x3fe83   fn 0x3fc4c   (4-leg helper, ONLY caller
      0x3f4d5 INSIDE fn 0x3f130 -> 0x3fc4c is private to the selector)
  0x40071              fn 0x40018   (AI candidate loop, aicode.md)
REQUIRES predicate 0x46d3c: 6 sites (0x40071 fn 0x40018, 0x474e8/0x47df5/
0x47f40/0x48298/0x48566 = research-window family) — NONE in the planet-UI or
selector fns. So the PLANLIST question is entirely about 0x3f130/0x3fc4c vs
the 0x3aa0a legs. [verified this iteration]

## P1 — CALLER GRAPH OF THE SELECTOR (function-bounded rel32 scan; the naive
linear 0xe8 scan DESYNCS and false-negatives — scan per-function, banked trap)
  fn 0x3f130: callers = 0x3eade (x2 sites) inside fn 0x3ea54
  fn 0x3fc4c: caller  = 0x3f4d5 (inside fn 0x3f130) — private helper
  fn 0x40018: callers = 0x3eb1d (x2, inside fn 0x3ea54)
  fn 0x3d2fe (popup): ZERO direct call sites AND zero u32 pointer refs image-
      wide -> reached only via a table whose entries are not plain u32 fn ptrs
      in the restored image (message-map or thunk). Not needed for TPF6-B.
Ghidra get_function_callers(0x3d2fe) = 0 too (agrees: no RESOLVED caller).
[verified this iteration]

## P2 — ARGUMENT REGISTER LAW FOR CHECKER 0x3830c (from entry bytes + sites)
Entry 0x3830c: push ecx/esi/edi/ebp; mov esi,eax; al=byte[esi+0x57];
cmp eax,0xff; jne; cmp dl,5 -> item-5 special. Sites bound dl < 0x27 at
0x38331 (jae 0x38343a else-path) => EDX = ITEM. eax = world obj ([0x43508]).
Item-table access 0x3834d 'mov al,[eax*8+0x73e45]' (stride 8 table base).
CELL register: sites show ebx (0x3d56d 'mov bx,word[eax+0xab]') and ecx
carried from caller. 0x3b42d site loads edx=byte[widget+0xab] -> in fn 0x3aa0a
[ebp-8] and in fn 0x3d2fe [ebp-0x10] are DIFFERENT locals; field +0xab read as
BYTE into the item arg at 0x3b42d vs WORD into ebx at 0x3d56d — resolve which
of {ebx, ecx} is the cell before comparing gates (next probe: read checker
body for ebx/ecx consumers).

## P3 — FIRST LOOK AT SELECTOR HELPER fn 0x3fc4c (work/r1/tPF6b_3fc4c.txt)
0x3fcd0 leg: al=byte[ecx+0x59]; cmp eax,6; jge out -> per-object loop bound 6;
edx=0x12 CONSTANT item 18; call 0x3830c; fail -> out; pass -> call 0x3958c
(item 0x12) -> if !=0xffff then out; call 0x38818(edx=0x12,ebx=0) -> return
0xffffffff. This leg is a SPECIFIC-item (18) gate, not a row loop.
=> the four legs at 0x3fcf0/0x3fdb8/0x3fe22/0x3fe83 are fixed-item checks
(item 0x12 and kin), NOT the list filter. The row loop, if any, is in the
main body of fn 0x3f130 itself (0x3f130..0x3faa3 minus the 0x3fc4c tail).

## NEXT
(1) resolve checker cell-register (read 0x3830c body fully once);
(2) read fn 0x3f130 0x3f130..0x3faa3 for an item loop appending rows + which
    cell value it passes (armed cell widget word vs constant);
(3) correlate fn 0x3ea54 gate ([p+0x54]==0xff per t406 F2b) — is 0x3f130 the
    PLANLIST fill or the AI/other selector;
(4) verdict: cell-aware -> diff vs projectOptionsFor + ship; not cell-aware ->
    honest negative, PORT-ONLY re-examination note, TPF6-B stays open.

## P4 — *** THE VENDOR PLANLIST ROW-FILL SITE, RECOVERED (CELL-AWARE) ***
fn 0x3aa0a IS the PLANLIST widget's message handler (banked: t428e E3 widget
0x1f06; t341 "UI leg fn 0x3aa0a"; entry binds eax->[ebp-8]=widget, dx->[ebp-4]
msg id; dispatch 0x3aa4c: dx==7 -> 0x3abb2, dx==0x33(51) -> 0x3b6f3).
MSG-51 HANDLER 0x3b6f3 = THE ROW FILL (work/r1/tPF6b_3aa0a.txt lines 919+):
  gate: bh=byte[0x7458e]; cmp bh, byte[[0x43508]+0x57]; jne 0x3b7f2 (skip).
  arg leg: cmp [ebp-0x14],1; je-> 0x3b70d: word[widget+0xae] := 0xffff
      (UNARMED fill: force cell = -1 BEFORE the loop).
  init: dword[[ebp-0x18=PLANLIST]+0xab] := 0; esi := [ebp-8]+0xb2; edi :=
      [ebp-8] (row array base = widget+0xb2, STRIDE 5, count [ebp-0x10]).
  LOOP 0x3b75e..0x3b7c0: ecx 0..0x26; skip cl==5; edx=item=cl;
      bx = word[widget+0xae]  <- THE ARMED CELL WORD;
      eax = [0x43508]; call 0x3830c; test eax; je -> next item;
      PASS: byte[edi+0xb2] := al(item); dword[edi+0xb3] := 0; esi+=5; edi+=5;
      count++.
  tail 0x3b7c2: if count==0 skip refresh; else 0x314e8(widget,0,6,0) +
      0x56ca4(0x7a35c, edx=[2nd-widget+0x41], ebx=1, ecx=0) repaint.
=> VENDOR PLANLIST ROWS ARE CELL-AWARE: per-item checker 0x3830c(item,
   armedCell=word[widget+0xae]); unarmed fills pass -1 (the arg==1 leg forces
   +0xae=0xffff first). The armed cell word +0xae is written by the square-
   click handler (0x3b4a4, same region that calls queue-arm 0x38840 with
   bl=byte[+0xab] item, dx=word[+0xae] — the t341 UI leg) and mirrored from
   +0xac at init 0x3ab4c; +0xab byte = the armed cell's ITEM (0xff empty;
   0x17=23 ship). [verified bytes this iteration; game-terms labels inferred
   from t341/t428e/tPF-2d banked laws]
SKIP-5 IS UNCONDITIONAL (0x3b76a cmp byte[ebp-0xc],5 / je) — item 5 (Colony
Base per tPF-6 fixture trap) is NEVER a PLANLIST row in the vendor, even with
all techs. DELTA CANDIDATE vs projectOptionsFor — check port next.
CHECKER CELL-ARG SENTINEL LAW (body 0x38718 tail): cmp ebx,0xffff je out;
cmp byte[obj+0x10 ptr + ebx*4 + 1], 0xff -> cell item lookup indexed ebx*4 —
ebx is a CELL INDEX (verified).
Popup loop (0x3d56d) passes word[widget+0xab] as the same ebx: for the empty
path byte[+0xab]=0xff is the gate; widget classes differ in layout (TYPE 10
list vs popup button host) — do not blend.

## P5 — DECOMPILE CORROBORATION + MSG MAP (Ghidra FUN_0003aa0a, 0x3aa0a)
__regparm3 (eax, dx=msgid, ecx=param); [ebp-0x14]=ebx=param_3 high-view.
Dispatch (decompile + 0x3aa4c bytes agree):
  msg 0   = widget init: 5x 0x56ce4 loop, +0x35/+0x39=-1, +0xab=0xff,
            +0xac=-1, +0xae=+0xac.
  msg 3   = key handler (DAT_00010ba0 gates; 0x14 -> +0x42+=2 etc).
  msg 4   = square click: +0xac := 0x3a880(hit-test); ship-owner vetoes.
  msg 5   = ROW PICK/ARM: +0xae := +0xac; if row item != 0xff -> checker
            0x3830c(item, +0xae) must be -1 -> 0x38840 queue-arm; then
            +0xab=0xff,+0xac=-1,+0xae=+0xac. (t341 UI leg VERBATIM.)
  msg 0x32= 50 scroll: +0xac := 10/10/b/4 legs (arrows/row-count).
  msg 0x33= 51 ROW FILL 0x3b6f3: GATE DAT_0007458e == byte[DAT_00043508+0x57]
            (viewer race == world owner byte — fill runs ONLY for the owner);
            param_3==1 -> +0xae := 0xffff FIRST (PLBUILD SENDPARAM1 1,
            windows.txt ln1615 VERBATIM => every PLBUILD click opens the list
            UNARMED, cell=-1); loop ecx 0..0x26, skip 5,
            FUN_0003830c(item=cl, cell=+0xae) nonzero -> append row
            (byte+0xb2=item, u32+0xb3=0, stride 5); repaint iff count>0.
  msg 0x34= 52: +0xb0 := [PLSQUARE+0xab] (ship-design leg).
  msg 0x1c01/0x1c02 = row hover/select highlight (rows +0xb2 read by ebx*5).
*** THE CHECKER 0x3830c IS NOT PLACEMENT-ONLY — IT IS THE FULL ORDERABILITY
PREDICATE (body audit this iteration):
  LEG-A REQUIRES  0x3835d: req=byte item+5 (0x73e45 stride 8); if !=0xff:
          idx = req*5*8 (0x7478b base, sar 0x18 = UPOP byte of req row);
          pass-leg iff race mask word[0x74744] > req AND
          (1<<byte[obj+0x57]) & tech-bits -> else FAIL 0x38430.
          = the OQ-014 REQUIRES law inside the checker [verified].
  LEG-B FREE-POP  0x383b3: acc = word[obj+0x42] - word[obj+0x4c]; if
          byte[obj+0x54] != 0xff: acc += SBYTE UPOP(pending item) [0x73e44];
          pass iff acc >= UPOP(item) [0x73e41 sar 0x18] -> ebp; else FAIL
          unless item==0x17 -> 0x39a9c result replaces ebp.
          SAME UPOP WORD as cmd0 gate 0x388f7 (t406 F2b) — VERBATIM.
  item==5 at 0x38430: ebp := -1 (CB exempt from the pop leg).
  LEG-C CELL  0x3843a: if cell(word ebx) >= word[obj+0x1a] FAIL; flags bit0
          (0x73e46) OR race-table byte[0x12fb3+r*40]==2 -> edi; cell occupied
          -> edi; flags bit2 + item!=0xff -> edi; XOR surface/ring legs
          0x384db.. (0x18 = surface-cell count boundary; 0x395c4/0x3965c
          neighbour legs); final 0x386fe: return (ebp AND edi) ? -1 : 0.
=> return is -1 (0xffffffff, truthy) on PASS. 0x3b6f3 tests nonzero, 0x3b43d
   tests ==-1: consistent. [verified bytes]
CONSEQUENCE FOR THE PORT: the vendor PLANLIST row set =
   item in [0,0x27) AND item!=5 AND REQUIRES AND FREEPOP(acc incl. pending)
   AND PLACEMENT(cell)  — armed OR unarmed (cell=-1 still runs LEG-B/A).
Port projectOptionsFor = REQUIRES AND (armed? placementBlock) — MISSING:
   (D1) skip-5 unconditional; (D2) the FREE-POP leg AT LIST TIME (port banked
   'free-pop is an ORDER gate, not a list filter' — REFUTED: the same acc
   expression sits inside the checker the fill loop calls); (D3) unarmed
   (-1) path runs no leg at all in the port while vendor runs A+B.
PLBUILD param law answers the 'does the popup ever show an armed-filtered
list' half of TPF6-A: NO — SENDPARAM1=1 forces cell -1 on every open; the
armed value in +0xae only matters between an arm (msg 5 writes) and the next
PLBUILD click.

## P6 — CELL-SENTINEL FLOW CORRECTED (supersedes P2/P5 wording on 0x38718)
The 0x38718 snippet is NOT inside the checker (checker ends ret 0x38716;
0x38718 is a stub wrapper calling 0x38840). CELL-SENTINEL LAW VERIFIED:
0x3843a `cmp bx, word[esi+0x1a]; jae 0x386fe` — bx=0xffff (cell -1) is ABOVE
any cell count so the jae BYPASSES every cell leg (0x3843a..0x386fc) and
lands on the final `test ebp / test edi` AND. edi was pre-granted -1 by
LEG-A pass (0x383ad je 0x383b3 path keeps edi=-1 from 0x3831f). => checker
(item, -1) == REQUIRES AND FREEPOP, cell legs inert. The `cmp dl,0xff` legs
(0x384af, 0x384db) test ITEM==0xff (demolish selector), NOT the cell.
FULL CHECKER SEMANTICS (final):
  PASS(-1) iff REQUIRES-OK (req==0xFF or race-mask>req & tech bit)
         AND ( freePopAcc >= UPOP(item)  [acc = +0x42 - +0x4c +
               SBYTE UPOP(pending@+0x54) when pending!=0xff]
               OR (item==0x17 AND 0x39a9c != 0) )
         AND cell-edi (item-cell geometry; inert for cell=-1).
0x39a9c (ship pop-exemption, 137 bytes, read this iteration): if world race
byte in [0,[0x13b96].hi) -> edx = FIRST EMPTY CELL (0x3958c scan over +0x1a);
0xffff -> 0; cell word+2 bit0 == 0 -> 0; else ebx=-1 iff 0x402d8(race*80*2 +
0x12e16) > 0. Semantics of 0x402d8 UNRESOLVED (ship-design table census?) ->
SEAM TPF6-SHIP: ship-row membership beyond pop-short stays unrecovered; do
NOT claim the ship law closed.
FREE-POP-AT-LIST-TIME LAW (the iteration's port delta, cited):
0x383b3..0x38416 is INSIDE the checker that 0x3b6f3 calls per row, so the
vendor PLANLIST HIDES rows whose UPOP exceeds current free pop (incl. the
pending item's own UPOP addback). Port bank 'free-pop is an ORDER gate, not
a list filter' (_wip_tPF6 P3-adjacent comment in planetview.cpp:47-49) is
REFUTED BY BYTES. Vendor-visible consequence: with queue pending, rows the
pending item's UPOP pushes over threshold disappear from the list.
FREE-POP ADDBACK ARITHMETIC (port mapping, verified against usedPopFor):
+0x4c is the recalc-maintained used-pop (0x38f68 writer block 0x38ee3..f58;
port cited analog campaign.h:396 usedPopFor = ACTIVE-item UPOP sum + gov
Automation). Vendor acc = pop - used + (pending!=0xff ? SBYTE UPOP(pending)
: 0); with used including pending that nets to pop - active_sum, which is
EXACTLY the port's pop - usedPopFor(star). No pending term needed port-side.

## P7 — VERDICT (TPF6-B CLOSED AT MECHANISM)
1. THE SITE EXISTS AND IS CELL-AWARE IN CODE: 0x3b6f3 (fn 0x3aa0a, msg 0x33)
   passes word[widget+0xae] as the checker's cell (ebx). [verified]
2. BUT FOR HUMAN PLAY THE CELL IS ALWAYS -1: the ONLY msg-51 producer in the
   planet window is PLBUILD (windows.txt; msg-id space per-window per tPF-7a
   law — ROTRIGHT/WEAPONS/BATROTRIGHT/RESROTRIGHT msg-51s are OTHER windows),
   and its SENDPARAM1 is 1 (ln1615 verbatim), which the handler consumes as
   'force +0xae := 0xffff BEFORE the loop'. The armed value written by row
   pick (0x3b4a4-region msg 5) never reaches a fill. => vendor PLANLIST
   membership for every witnessed AND reachable open =
     item in [0,0x27) AND item != 5 AND REQUIRES AND FREEPOP(pop-active)
   with cell legs inert (0x3843a jae bypass). TPF6-A first half ANSWERED:
   the vendor NEVER shows a per-cell-filtered build list; a Build whose list
   has no buildable row would show an EMPTY list (count==0 -> no repaint at
   0x3b7c2; rows stale from the previous fill remain on screen — note for
   TPF6-A second half, needs a witness).
3. PORT DELTAS (shipping): projectOptionsFor must (D1) skip item 5 always
   (0x3b76a unconditional) and (D2) apply the FREE-POP leg ALWAYS (armed and
   unarmed alike), item 23 exempt via the 0x38422 ship replacement whose full
   condition (0x39a9c -> empty-active-cell + race leg 0x402d8) stays SEAM
   TPF6-SHIP (0x402d8 semantics unrecovered — honest negative). The tPF-6
   armed placementBlock filter stays (it guards the PORT tile-first flow,
   justified by the popup D6 law, not by this fill law).
4. The port bank 'free-pop is an ORDER gate, not a list filter' is REFUTED —
   R-tPF6b candidate for REFUTED-ROUTES.md.




