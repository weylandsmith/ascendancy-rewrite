# t341 WIP — CANDIDATE-RESIDUE-(6): FACTORY AUTO-RESERVE AT BUILD COMPLETION (ZERO CAPTURE)

Task: docs/STATE.md NEXT ACTION t341. Sitting check NEGATIVE (tail-seek,
newest live-timeline turn 1086 == corpus; files 42..47.sav rows). Production
:9 never signalled; game/ read-only.

Instruments: scripts/r341_dis.py (range dumper over work/r331_disasm.txt,
file-offset == guest offset for obj0 code), scripts/r341_queue_writers.py
(census; work/r341_queue_writers.out exit 0).

## S1 — WRITER CENSUS (queue fields +0x52 WORD cell / +0x54 BYTE item)

Whole-image store census (non-stack frame; full list work/r341_queue_writers.out):
- 0x37f8d/0x37f93 — reset 0xffff/0xff (loader/init family fn ~0x37d80 planitem init)
- 0x38a19/0x38a1f — reset (fn 0x38840, early exit path)
- 0x38af5..0x38b26 — THE RESERVE WRITER (fn 0x38840): +0x52=0xffff then
  (item flag bit1 clear -> +0x52=[esp+0x1c] cell arg; cell byte1=[item] unless
  item==0x23) then +0x54=item byte. This is the t271 reservation-pattern writer.
- 0x39290/0x39296 — completion reset (t340 law, VERIFIED live)
- 0x3a153/0x3a159 — reset (fn near 0x3a0xx)
- 0x3a655/0x3a65d — planet-record CONSTRUCT/copy (whole record field-by-field
  copy from stack frame, 0x3a596..0x3a6b9; not a queue op)
- 0x49dd2/0x49de5 — reset (gizmo-record region, different record class? check)
- obj1-region 0x4xxxx-0x6xxxx hits are esp frames or other record classes
  (gizmo stride 0x6a, window records) — none store a planet +0x52 WORD with a
  cell index.
=> The ONLY in-image site that stores a queue cell index + item into a planet
record's +0x52/+0x54 (the reserve pattern t340 observed) is fn 0x38840 at
0x38af5..0x38b26. Everything else resets or copies.

## S2 — CALL GRAPH TO THE SELECTOR

- Selector FUN_0003f130 (0x3f130..0x3f4fc, ghp5 size 0x3cd): direct in-image
  call xrefs = EXACTLY ONE: 0x3eade.
- 0x3eade is inside fn 0x3ea54 (0x3ea54..0x3eb86, size 0x133). Verbatim loop:
    3ea8f  dx = ds:0x3a093 (planet count, WORD)
    3ea9f  next planet: ebx++; ebx>=count -> exit 0x3eae5
    3eaac  edx = &record[ebx]; base ds 0x2b057, stride 0x7b  (PLANET RECORDS)
    3eab8  al = [edx+0x57]                      (planet OWNER-RACE byte)
    3eabb  al != [ecx]        -> next           (ecx = fn arg record, byte0)
    3eabf  al == ds:0x7458e?  (0x7458e = current-race-in-process global)
    3eac5    != (not current race) -> goto 0x3ead6 (queue check)
    3eac7    == : [edx+0x5a]!=0 -> goto 0x3ead6 ; else 0x10ba4==0 -> SKIP planet
    3ead6  [edx+0x54]==0xff? NO -> next          (queue must be EMPTY)
    3eadc  eax = ecx ; 0x3eade call 0x3f130      (arg = the fn's record)
  => QUEUE-EMPTY-ONLY caller law (banked) REPRODUCED verbatim + the owner gate:
     current-race planets are skipped iff [planet+0x5a]==0 AND ds:0x10ba4==0.
     Non-current-race planets always reach the queue-empty test.
- fn 0x3ea54 direct xrefs: EXACTLY ONE: 0x3e7bb (inside fn 0x3e6e0,
  0x3e6e0..0x3e826, size 0x147). Entry guards on arg record:
    3ea60  al=[arg byte0]; al==0x7458e && ds:0x10ba4 != 0xffffffff -> SKIP the
           four sub-calls (0x3ecb8, 0x3ef2c, 0x44690, 0x3eb88) but STILL run
           the planet loop (0x3ea8f is reached from 0x3ea8f fallthrough —
           verify edge: 0x3ea71 jne 0x3ea8f jumps PAST the four calls INTO the
           loop preamble at 0x3ea8f).
  (interpretation of arg record: race-vs-planet decided in S3)

## S3 — CALL CHAIN CLOSED STATICALLY (zero capture)

- fn 0x3e6e0 callers: EXACTLY TWO, both in fn 0x24f24 (0x24f24 size 0x3d7):
  0x25083 (eax=esi) and 0x250a5 (eax = race-row: `add eax,0x12e16` at 0x250a0 —
  the race-row static base neighbourhood, cf. aicode.md S7.3 "Head: esi =
  0x12e16 + ds:0x7458e*0x1ee (LOCAL race row)"). => fn 0x3e6e0 IS the per-race
  turn tail (aicode.md S7.2 banked law REPRODUCED: AI races run SA_ bodies
  there; caller 0x3ea54 at 0x3e7bb).
- fn 0x3ea54 ARG RECORD = race record (byte0 = race index; loop matches
  planet [p+0x57] owner byte against it).
- *** THE OWNER GATE IS [p+0x5a]-CONDITIONED, NOT OWNER-0-EXCLUDED ***
  Verbatim 0x3eabf..0x3eade:
    cmp al, ds:0x7458e ; jne 0x3ead6        (non-local race -> queue test)
    cmp DWORD [edx+0x5a],0x0 ; jne 0x3ead6  (LOCAL planet w/ [p+0x5a]!=0 ->
                                            queue test TOO)
    cmp DWORD ds:0x10ba4,0x0 ; je 0x3ea9f   (singleplayer -> skip local planet)
    cmp BYTE [edx+0x54],0xff ; jne 0x3ea9f  (queue must be empty)
    0x3eade call 0x3f130
  => the AI turn tail DOES run the selector on HUMAN planets iff
  [planet+0x5a] != 0. The STATE.md hypothesis "owner-gated away from 0" is
  WRONG as stated — the gate is a per-planet DWORD flag at +0x5a, not owner.
- +0x5a WRITER CENSUS (scripts inline census, 19 stores whole-image):
  planet-record-relevant: 0x3a681 (record copy ctor 0x3a596..0x3a6b9),
  0x3adb7 (TOGGLE: not edx from [eax+0x5a]; inside fn 0x3aa0a, gated
  ds:0x484ac!=0 && ds:0x10ba0!=0 — a debug-flag-gated branch region
  0x3ad62..0x3addb all gated on ds:0x10ba0 [0x10ba0 = nougat.lf per
  debugflags.md]); 0x3dc0d/3dcb5/3dd6b/3dde3 (ebp-based, identity TBD);
  0x266b1 zero-store; the rest are other record classes (gizmo 0x4924a,
  esp frames). NO site stores a constant nonzero into a planet +0x5a.
- COMPLETION-HANDLER SIDE-EVENT (fn 0x38f68 0x3934e..0x393a4, VERBATIM):
  owner==ds:0x7458e && [0x7e582 hi]!=0x11 && pop(+0x42)==used(+0x4c) &&
  edi==0 && [esi+0x5a]==0 && (queue empty [+0x54]==0xff OR item flag bit0x20)
  -> push EVENT 15 via 0x55a60(eax=0x7a35c, edx=0xf, ebx=planet). The t340
  run's completion turn hit exactly this (queue just reset to 0xff):
  EVENT-15 IS PRODUCED AT THE OBSERVED BOUNDARY. Consumer TBD (dispatcher
  arm for type 15 — aicode.md S7.1 arm list covers 0..14,16..26 arms; 15
  needs its arm located).

## S4 — SELECTOR 0x3f130 INTERNALS vs OBSERVED PICK (item 0 on Gridsor I)
(t28 banked law docs/re/income-law.md S9 re-verified verbatim this iteration:
0x3f146 [+0x44]==0 -> return; 0x3f159 gate FUN_0003f758==1 -> return;
over-cap demolish 0x3f1e9; tubes 0x3f2ff; min-requires sweep 0x3f403;
random-cell picker 0x3f481 FUN_00038818(0xffff); MAIN PICK 0x3f4d5 call
0x3fc4c (score) + 0x3f4ec call 0x3fec4, candidate array built 0x3f528..0x3f66d
(0x27=39 items, stride 0x28 item-table records; per-item score words at
[esp+edx]), RANDOM-BIASED SELECT 0x3f672: if ebp(candidate count)==0 return;
rng call 0x7824f % 100 -> [esp+0xd8]; scan candidates 0x3f6a7..0x3f72b:
skip if slot occupied (0x3958c != 0xffff) AND pick-percent>rng ... FINAL
0x3f745/0x3f747 FUN_00038818(dl=item, ebx=0, cell=0xffff->auto) = THE RESERVE
-> fn 0x38840 writes +0x52/+0x54 (S1 writer). 0x38818 verbatim:
0x38825 call 0x3875c (picker when cell==?) then 0x38832 call 0x38718
(store) — chain to the S1 writer CONFIRMED.)

## S5 — VERDICT: RESIDUE-(6) RESOLVED — THE "HUMAN PLANET" WAS AN AI PLANET
## (t340 MISATTRIBUTION), AND THE AUTO-RESERVE IS THE ALREADY-BANKED AI
## SELECTOR PATH. MEASURED LAW: THE VENDOR NEVER AUTO-QUEUES FOR THE HUMAN.

### S5.1 Owner correction (decisive, cited measurement + banked law)
- t248 LAW (docs/re/selfplay.md S t248 PROOF 1, structural, 50 systems x 2
  timestamps zero violations): the 0x7b planet record holds the OWNER RACE
  INDEX at NAME+0x33; sample_ring() reads [base+0x57] with base = name-0x24
  -> +0x57 == NAME+0x33 — same field.
- MEASURED (ring-final of the t340 ground-truth run, scripts inline census
  via IL.find_records — heap-record law: name at base+0x24, so the read
  [base+0x57] IS NAME+0x33): Gridsor I owner byte = **1** (an AI race) in
  ALL 20 ring saves; named-planet owner histogram over the static pool
  {0:80, 1:11, 2:13, 255:41} (owner-0 count 80 == t248 PROOF 2's t1086
  count EXACT); ds:0x7458e (local player) = 0; ds:0x10ba4 (netplay) = 0.
  (A star-record bitmask corroboration was ATTEMPTED via static base
  0x13bc5 and returned garbage — heap-moved save; claim NOT claimed, the
  pool census + t248 law stand alone.)
- => t340 LANDED clause (5) "item 0 FACTORY auto-reserved on the HUMAN
  planet" is FALSE as stated: the planet was AI-owned all along. The
  "no UI click" observation is explained: AI planets are machine-driven.

### S5.2 Static chain (who wrote cell 43 / item 0) — fully closed, zero capture
Per-turn turn tail (fn 0x24f24, VERBATIM 0x2503c..0x250a5):
  loop A 0x2503c: for every planet (stride 0x7b, bound hi16): call FUN_00038f68
  loop B 0x25060: for every race row (stride 0x1ee base ebp+6): SKIP iff
    row-index == ds:0x7458e; call FUN_0003e6e0(row)
  after-loop 0x250a5: call FUN_0003e6e0(0x12e16 + idx*0x1ee) FOR THE LOCAL row.
=> completion handler FUN_00038f68 runs BEFORE the AI/selector tail EVERY turn
   (loop A precedes loop B) — exactly the observed ordering (reset then
   re-queue in one turn boundary).
FUN_0003e6e0 -> 0x3e7bb FUN_0003ea54(race rec) -> planet loop 0x3ea9f:
  owner match [p+NAME+0x33]==race byte; local-race gate (0x3eabf..0x3eacd):
  local planet skipped iff [p+0x5a]==0 AND ds:0x10ba4==0 (all 104 owned
  planets have [p+0x5a]=0 MEASURED, so the human is gated out; the local
  call at 0x250a5 also runs the selector for the LOCAL race iff some owned
  planet has [p+0x5a]!=0 — none in this capture);
  QUEUE-EMPTY test 0x3ead6 [p+0x54]==0xff -> 0x3eade FUN_0003f130(ctx,planet).
FUN_0003f130 PICK LAW (t28 banked, income-law.md S9; re-verified verbatim):
  candidate scan 0x3f528..0x3f66d (39 rows, stride 0x28) -> random-biased
  select 0x3f672 (rng%100; absent-item wins first pass; COST/IND>=70 abort)
  -> 0x3f747 FUN_0003818(dl=item, ebx=0, cell=0xffff) -> 0x3875c legal-cell
  picker -> 0x38832 FUN_00038718 -> 0x38753 FUN_00038840(cmd2) -> THE S1
  WRITER 0x38b12/0x38b26 (+0x52=cell, +0x54=item) + slot byte1:=item.
  Slot43 byte1 0xff->0x00 == byte1:=item 0 verbatim (t340 S4 store list).
Writer census (scripts/r341_queue_writers.py exit 0): the ONLY in-image
stores of a planet-record +0x52 WORD cell + +0x54 BYTE item pair are fn
0x38840 (0x38af5..0x38b26, via callers 0x38718/0x38753 chain, 17 direct +
19 indirect-caller-of-0x38818 sites) — everything else resets (0x37f8d,
0x3a153, 0x39290) or copies whole records (0x3a655 ctor). UI paths use the
SAME chain (0x3ae99 in the planet-window command fn = the human click leg).

### S5.3 MEASURED LAW (the closure-grade statement) — human planets NEVER
auto-queue; AI planets do at every empty-queue turn:
- 13 human (owner-0) planets with empty queues at t1086 (Vega II/IV, Atropos
  I, Delphinius V, Phoebe III/V, Corncob I, Hope II, Oslo II/IV, Icarus
  II/IV, Willy II) -> STILL EMPTY at t1093 (13/13, seven turns).
- The AI selector ran for owners 1/2 in the SAME turn window (Gridsor I
  re-queued in the boundary itself).
- Positive control honesty: the 4 AI empty-queue planets at t1086 (Shlupp
  II/III, Sarsaparilla I, Feculon I) also stayed empty — CONSISTENT with the
  t28 law: all four are at pop==cap with IND 6-7 (measured: 20/20, 20/20,
  26/26, 21/21; IND 7,6,7,7) -> over-cap path with no MPOP==0/UPOP>0
  demolish candidate or COST/IND>=70 abort -> return without queueing.
  (Per-planet pick adjudication stays in residue-(5) minutiae; the closure
  claim does not rest on it.)
=> Rewrite buildPhase claim "Player planets: the original is UI-driven (no
   auto selector)" is SUPPORTED by cited measurement (13/13 empty over 7
   turns + the 0x3eabf..0x3eacd local-race gate static law). No rewrite code
   delta. Comment upgraded to cite this witness.

### S5.4 Event-15 side (t340 completion-tail producer 0x3939b): consumer
arm adjudicated from BANKED law (aicode.md S7.1, t102 verified raw): types
{0,1,2,15} -> edi=0x11 + ds:0x43508:=obj = EVENTWIN refresh ONLY (type 15
shares the arm with 0/1/2; no effect arm, cf. type 24 S7.1 conclusion).
Event 15 CANNOT queue a build. Honest status: [verified-banked] not
re-derived this iteration; consistent with the S5.2/S5.3 verdict.

### S5.5 Pick-law consistency check (measured, closes the loop end-to-end)
Runtime item table (DS+0x73e46, 40B/item law): item 0 flag=0x0 COST=30;
item 26 flag=0x8 COST=60 (t340 gate-word measurement reproduced). Gridsor I
IND=6: item 0 COST/IND = 5 < 70 (no t27 70-law abort). Gridsor I slotted
item census (ring-final slot dwords, byte1): {1,2,5,7,8,18,22,26} — item 0
ABSENT -> absent-item-wins-first-pass in TABLE ORDER (t28 pick law 0x3f6a7)
-> row 0 (Factory) is the DETERMINISTIC first pick, exactly what was
observed queued (cell 43 = the random-legal-cell picker's answer, rng).
The observed auto-reserve is fully explained by the banked AI selector law.

## LEDGER DISPOSITION
- Candidate residue-(6): CLOSED as a NON-PHENOMENON with cited measurement
  (owner correction + 13/13 human empty-queue persistence + full static
  writer chain to 0x38840). OQ-016 ROW STAYS OPEN (residues 1, 5 unchanged);
  ledger count 16/3 unchanged.
- REFUTED-ROUTES amendment: (1) Gridsor I is owner-1 — do not treat it as a
  human planet in any future witness; (2) do not re-census queue writers —
  census closed (only 0x38840 reserves); (3) event-15 is a UI-refresh signal
  (banked S7.1) — do not hunt an effect arm.
