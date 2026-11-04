# t297 WIP — LIVE move-order witness (OQ-019 r1/r3, OQ-016 r1 gate)

Session start 2026-11-04 ~14:45 EST. Fresh session; resumed from STATE.md alone.

## Pre-flight (verified this session)
- Production :9 alive (dosbox pid 1957, r1_playcap_watch pid 1979), ring rows
  PINNED turn 1086 through wall 14:44 => NO new sitting => r1_t85g_sitting.py
  NOT required (tail-BYTES read only; file 8.00 GB).
- scripts/r296_selection_note.py -> ANCHORS OK 11/11 (payload 576,643 B).
- Scratch copy work/r1/game-wp present; r293 drive class reusable.

## T297-S1. CORRECTION TO THE t296 POINTER LAW (re-dumped 0x1b070..0x1b150 +
0x1b91c..0x1bb1f verbatim from work/t91_code_disasm.txt). The batcon window
holds TWO distinct selection fields:
  [win+0xaf] = SELECTED OBJECT (clip ptr)  — msg-4 ROUTER gate
  [win+0xb3] = hover/selected clip copy    — order-issue leg gate
MSG 4 (0x1b070, BatModeWnd): mode==4 -> ignore; bounds [win+0x8..0x14];
  call 0x4fb30(0x78638) (hit-test);
  IF [ebp+0xaf] != 0 -> call 0x1b91c with ecx=1 (0x1b0bf mov ecx,0x1)   <<<<
  ELSE mode==2 -> WORD [ebp+0xbc]: >=0xffff -> mode:=0 (0x1b114); <0xffff ->
    mode:=3 + call 0x1bd80(win, x-[win+0xc], y-[win+0x8]) (0x1b103..0x1b10a);
  mode==3 (0x1b11d): relay 0x326 ecx=5 over [ebp+0x1d0a], mode:=0.
BATCON HANDLER 0x1b91c (eax=win, ecx=modifier, edx=[ebp+0xab] pending-hit,
dl=pending kind):
  [win+0xaf]==0 -> assert 0x3d7@0x82ffe (0x1b936) — requires a selection;
  ecx==0 -> call 0x1ca38 DESELECT + return (0x1b949);
  mode==1 (ARMED, 0x1b953..0x1b9ab): action from selected clip kind
    (2->3, kind==mode->2, 3->4) -> relay 0x322; if result == -1 -> mode:=0 +
    relay 0x326 + [win+0xb3]:=0;
  mode NOT 1 (0x1b9ee): pending kind dl==2 (SHIP clip) + [win+0xb7]==0 +
    owner [ship+0x54]>>16==ds:0x7458e + MOVES [+0x88]>0 -> [win+0xb3]:=clip,
    [win+0xb7]:=2 (SELECT, the t296 gates);
  dl==1 (0x1ba45): mode==2|3 -> mode:=0 + relay 0x326 (ship,ecx=[clip+1],
    edx=[pending+0x41]); ELSE (mode 0): [win+0xb3]:=[win+0xaf] re-copy;
  dl==3 (0x1bad3): mode==2 or bh==3 -> relay 0x326 ecx=4 + mode:=0;
  ORDER-ISSUE LEG (0x1ba8c, dl==1, mode==0, gate [win+0xb3]==eax clicked clip):
    ecx=1; eax=[[ebx+0x1]] (clicked object); ebx=0x11;
    ds:0x43508 := eax @0x1baa7; [win+0xaf]:=0; call 0x56ad4(0x7a35c,
    edx=1, edi=param) = COMMAND RING {u16 0x11,u32 dest}.
  TAIL 0x1bb1f: ebp==-1 path -> reads [win+0xb3] kind, cmp 2 @0x1bb2e (more).
>>> LIVE-ROUTE CONSEQUENCE: the t296 note's "verification is ds:0x43504" and
"plain click after selection always deselects" are BOTH about the WRONG field
or the wrong leg. Selection state for the ROUTER is [win+0xaf] (window-object
RAM, NOT reachable by the pointer-law scalar table); ds:0x43504 is a separate
global with its own writers. The destination-entry route t296 thought needed
the unidentified msg-0x50 widget EXISTS in the mouse path: click ship (select,
mode 2) -> click DESTINATION CLIP (routes to 0x1b91c ecx=1; pending kind 1 or
3 legs relay 0x326 = order; kind-1 leg at mode 0 publishes ds:0x43508 + ring
code 0x11 directly @0x1baa7). Whether the mode-2 plain-click leg (WORD
[win+0xbc]) intercepts first is the open sub-question -> measure where +0xbc
is written.

## T297-S2. [win+0xbc] writer census (batmode zone 0x14bc0..0x1e000, MEASURED)
WORD [reg+0xbc] stores: 0x1ad59 (init := 0xffff, inside the same init block
that zeroes [win+0xaf] @0x1ad37 and [win+0xb7] @0x1ad41) and 0x1c9a0
(`mov ax,WORD [ecx+0x4e42]; dec eax; mov WORD [ecx+0xbc],ax` — guarded by
`cmp BYTE [esi],0x6` @0x1c993, i.e. a clip-kind-6 context inside the route
builder 0x1a8e8 family). => [win+0xbc] is NOT written by ordinary selection;
it becomes <0xffff only through the kind-6 route-edit leg. Therefore the
msg-4 mode-2 branch at 0x1b0e3 normally takes 0xffff -> mode:=0 (t296 C4
confirmed as the DEFAULT path), and destination entry in mode 2 must go
through the batcon handler BEFORE the mode-2 branch — which it does whenever
[ebp+0xaf] != 0 (0x1b0b5 router: selection non-null => call 0x1b91c ecx=1,
0x1b0cc, and the mode-2 branch at 0x1b0d6 is only reached when [win+0xaf]==0).
KEY RE-READ: msg-4 router order is (1) mode==4 ignore, (2) bounds,
(3) call 0x4fb30(0x78638) hit-test, (4) IF [win+0xaf] != 0 -> 0x1b91c(ecx=1),
(5) ELSE mode-2 plain-click branch. So t296's "plain click after selection
deselects" holds ONLY when the router's [win+0xaf] is null — i.e. after the
kind-2 SELECT leg (which sets [win+0xb3], not [win+0xaf]) the router still
sees [win+0xaf]==0 and falls to the mode-2 branch -> DESELECT at 0x1b114
because mode==2. CONSEQUENCE FOR THE LIVE ROUTE: after selecting a ship the
NEXT plain click DESELECTS unless it is routed by a non-null [win+0xaf]. The
arms that set [win+0xaf] are the 0x1ba8c publish leg (sets it to 0 AFTER
publishing — no) and ... 0x1bdb4 (t296 S5: three-tier clip lookup writes
[win+0xaf]). WHICH msg/writer path calls 0x1bdb4 is the remaining live
question the session instruments (W2 full-RAM diff watches the window object
once its address is pinned by the W3 pointer scan).

## TOOL TRAP (bank, t297): r293/r297 drive scripts import PIL at module scope;
system python3 (3.13) has NO PIL. Run drive sessions with
~/.hermes/hermes-agent/venv/bin/python (PIL 12.3.0). First launch died at
import with ModuleNotFoundError BEFORE any spawn (clean, no orphans,
production untouched).

## T297-S3. LIVE SESSION RESULT (run work/r1/t297-order-20261104-152048,
scratch game-wp, Xvfb :97, production :9 untouched — verified before/after).
Drive script scripts/r297_order_session.py (r293 class + full-RAM XOR diff
witness W2 + cluster flood-finder + ptr scan W3). rc=1 HONEST NEGATIVE.
FACTS (all from the run log / ringsamples):
1. Campaign entered, FLEET route opened a system view, turns advanced
   1086->1088 (presses 1 and 3; press 2 swallowed by an EVENTWIN, closed by
   Escape per law). Drive plumbing GOOD.
2. TARGET-PICKER BUG (mine, fixed same session): rows0[-1]["recs"] from
   r293.ring_mem_rows is the FULL all-owners census keyed by TRUE ship-array
   index; my candidate filter tested kind==4 & moves>0 but NOT owner==0 (G3),
   so "slot 1" was an OWNER-1 ship — selection impossible by law, which
   fully explains the dead battery (the fleet row-1 jump may even have gone
   to a different ship entirely). FIX LANDED t297: owner==0 added to both
   candidate filters in r297_order_session.py (+ an idx=k field added to
   ring_mem_rows recs for explicitness; keys were already true indices).
3. NO kind-2 EVER appeared (kind2=[] at every WITNESS incl. post-turn;
   kind2_post=[]). ds:0x43504/0x43508 (correct address B+OFF+X, see 5) never
   changed across the whole battery. NO order was issued. The A2 "issued"
   flag was a FALSE POSITIVE: check_issue() reads rec['dst43508'] which the
   witness computed from the WRONG address (see 5) and compared !=0, not
   against baseline.
4. SELECTION NEVER HAPPENED: A1 ship-cluster click (442,294) produced NO
   RAM run anywhere near the batwin fields (runs=3340 but all are the
   animation/timer band 0x4f4/0x57a + terrain rows 0xa4xx + palette ramp
   0xa6xx — identical set as A2; the click changed nothing beyond the
   animation baseline). Either the click missed the ship clip (cluster
   centroid = largest blob, likely the PLANET: the fleet row-1 ship may not
   be in-system, so no kind-4 clip exists at all — G1) or selection state is
   invisible to the instruments (window-object RAM not yet pinned, see 6).
5. POINTER-LAW CORRECTION (MEASURED, production ring 52-54.sav + scratch run):
   ds:0x43504/ds:0x43508 live at guest-phys B + SL.OFF(0x82bb0) + X — the
   SAME data-segment base as every other DAT scalar (r1_slot.read_slot law).
   The r296 note's "plain RAM at B + 0x43504" is WRONG (off by 0x82bb0);
   reading B+0x43504 returns garbage (0x1de8c031, constant). Correct values,
   production t=1086: ds:0x43504 = 0x256825 (NON-NULL while idle at the map —
   so it is NOT "selected object == null when idle"; it points at
   0x256825 whose bytes are zeros — possibly a stale/sticky selection or a
   different role than t296 assumed), ds:0x43508 = 0x26fe77 -> 0x26f00d after
   an autosave transition (CHANGES WITHOUT ANY INPUT — so 0x43508 is written
   outside the order path too; the 0x51a8e/0x51fc2 non-order writers t296
   cited). NEITHER global is a clean selection/order witness by itself.
6. WINDOW-OBJECT PIN ATTEMPT (static+RAM, MEASURED): handler 0x1aef8 has ZERO
   u32 occurrences in BOTH payload and guest RAM; 0x1b91c appears in RAM ONLY
   at 0x22cac1 and 0x22eb3b, whose B-relative offsets (0x6d5e9, 0x6f663) are
   EXACTLY the payload file offsets of the same u32s — i.e. that RAM region
   is a verbatim payload image copy (the window-class TEMPLATE table), not
   the live instance. The batwin INSTANCE fields ([+0xaf],[+0xb3],[+0xb7],
   [+0xbc]) are therefore reachable only by finding the instance allocation
   (heap) — candidate method for t298: the template-table entries at
   0x22cac1/0x22eb3b likely sit inside per-class records that also hold an
   instance pointer field; scan the template record neighbourhood for u32s
   pointing into heap (outside the payload-image region), or watch for the
   NEW heap object between title (no campaign) and in-system frames.
7. CLUSTER INVENTORY (system view screenshot 11-ish, flood-found): biggest
   blobs (442,294,400px) and (376,284,341px) = planet + city overlay region
   (matches the vision read: globe centre ~(390,290)); small blobs at
   (46,350),(46,420) = the two green iso tiles; ship sprites per vision at
   ~(48,148),(122,362),(140,432) — the flood finder merged/missed them
   (thr=380 too high for the tan hull; (62,56,219) is top-strip chrome). A
   t298 ship-sprite finder should use per-pixel colour classes (tan/gold hull
   R>150,G>110,B<90) NOT generic luminance, and must exclude the top strip
   y<112 (icon panels) — chrome was in the candidate list 3 times.
NEXT (t298): (a) fix r293.ring_mem_rows idx leak + r297 check_issue baseline
compare; (b) pin batwin instance address from the template-table neighbourhood
(static scan of RAM region around 0x22cac1: stride + instance-ptr field);
(c) re-run battery clicking COLOUR-CLASSIFIED ship sprites of a RING-VERIFIED
owner-0 kind-4 MOVES>0 ship (jump-to via the fleet row that lists THAT slot —
match fleet row content to the ship name/design first), witness via batwin
[+0xb7] once pinned + kind census + ds globals at the CORRECT address.
