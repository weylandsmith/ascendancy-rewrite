# t377 WIP — MAGNETRON USE-SITE INTO SHIPSIM (queue row t377)

## S0 steering check (session start, 2026-11-11 ~21:15 EST)
- Ring-first sitting probe `python3 scripts/t368_ring_turn.py`: parsed=20/20
  max_turn=1254 min_turn=1254. 1254 > 1086 => standing rule says run
  `scripts/r1_t85g_sitting.py` before the assignment.
- Production :9 HEALTHY: dosbox-x pid 107664 (timeout wrapper 107662),
  watcher pid 107679 (`r1_playcap_watch.py --no-exit`), ring 49.sav age 4 s,
  TL expiry 2026-11-17 11:24:41. Untouched throughout.
- live-timeline.jsonl 9,274,572,989 B mtime Nov 11 21:14 — LIVE feed (the
  t368 dead-feed condition is NOT present this session).
- `scripts/r369_playwindow.py` exit 0: first turn!=1086 row turn=1254
  wall=15:33:07 file=42.sav mtime_ns=1794429182264000000. NOTE this lo_ns is
  NEWER than t370's window (1794373326560000000): the user resumed playing
  TODAY ~15:33 wall. Ring turn still 1254 => the user is placing orders WITHIN
  turn 1254 (the t1253->1254 boundary already ended before 02:19 per t372).
  => A NEW PLAY SPAN EXISTS (15:33 -> 21:1x) never witnessed by any census.
- Sitting adjudication `r1_t85g_sitting.py work/r1/playcap` launched
  background -> work/r1/t377_sitting.out (pid 178014).

## S0b sitting adjudication result + FEED LAW FINDING
- `scripts/r377_feedcheck.py` (new, reuses r370_slot_events.stream): the NEW
  span lo_ns 1794429182264000000 -> EOF is frames=2236 wall 15:33:07->21:35:57,
  ALL turn 1254, and first-frame-vs-last-frame ship_raw diff = 0 of 40 slots.
  The user resumed the session today but produced ZERO ship-record events —
  no magnetron use, no order writes, no turn end. => No new witness exists;
  the t370 M1-M6 witnesses remain the complete evidence base. t377 stands.
- INSTRUMENT LAW (banked, affects every future sitting check): the r1_stream
  trust law filters turns BELOW the watermark only. The accumulating
  live-timeline.jsonl contains the OLD game that reached turn 1335 (mtime_ns
  1793245641..., Oct-28 rows, line 239178) — turns ABOVE today's watermark
  1254 PASS the filter and pollute a sitting census: t377_sitting.out's
  "t=1255..1335" relation snapshots + t1335 presence events are Oct-28 echoes,
  NOT today's play. A sitting census must floor at the playwindow mtime_ns
  (t369 trap, now generalized: floor applies to the sitting tool too, not just
  r369_playwindow).
- Ring banked: work/r1/bank-play-20261111-t377/ (20 slots, t1254).

## S1 task contract (STATE.md queue row t377, verbatim intent)
Witness M1 (docs/re/ships.md S64): s28 Guandagnini Vernunft->Atropos INSTANT
jump d=(+2464,-3104,+2528), POWER 90->80 = gizmos.txt Lane Magnetron 'Power
10' EXACT, ring slot (cidx 60) REMOVED same event = single-use consumption.
Carriage side exists (t363R carriesCode/firstCarrier); the USE event is not
modelled. Land useMagnetron (or executor seam) on the cited carrier law.
Pins: burn-exact, slot consumed-once, no second use, zero-carried never fires.
Landing-on-grid reconciliation stays an honest negative (S64 neg-(a)); pin
FLAGS/DELTA CLASS, never invented coordinates.

## S2 FRESH raw re-reads (work/r331_disasm.txt, this session) + CORRECTIONS
Windows re-read verbatim: FUN_0004a360 prologue (64672-), FUN_0004ca50 whole
body (67439-), case tree 0x4cd51..0x4cd66 + 0x4cd0d..0x4cd43 magnetron leg,
FUN_000220a8 entry+lane-check tail, FUN_00021f58 whole body, FUN_00049aa8,
FUN_000533e0 quantizer, FUN_000496e4 clear-slot. RAM corroboration:
scripts/r377_design_rows.py (new) on work/r1/bank-play-20261111 (B=0x1bf4d8
3/3): row 60 cat=5 flags=0x0002(TARGETLANE) power=10 range=50 level=0
numUses=1 ind=50; row 9 cat=0 flags=0x000f power=6 range=50 numUses=3;
row 73 cat=5 flags=0x0080(PASSIVE) power=10 range=0 numUses=0.
LOADED ROW == FILE ROW confirmed again for the three witness keys.

C1 GATE POLARITY CORRECTION (t185 T3 prose was inverted). Raw 0x4cb76..95:
  fild(Range<<5); fcomp dist; jae pass -> fail leg writes -1 ONLY when
  dist < Range*32. The gate rejects targets that are TOO CLOSE, not too far
  (t185 wrote "Range*32 < lane-d -> fails"). Corroborated by witness M1:
  d=(+2464,-3104,+2528) -> |d| ~4700 >> 1600 and the use COMMITTED.
  Also Range==0 skips the check entirely (je 0x4cb99).
  NOTE: with dist measured from the TARGET TRIPLE the M1 commit would need
  dist>=1600 PASS = fine under the corrected polarity (4700 >= 1600 -> pass).
  The t185 inverted reading would have REFUSED M1 — the correction is
  witness-verified, not just byte-verified.
C2 ACTIVATION = three conjuncts (0x4cb99..0x4cbbd + 0x4cbd4):
  bit0 = affordable(cost<=power, 0x4ca90) AND rangeOK(0x4cb95 leg);
  bit1 = design[+0x33] TARGETLANE flag (0x4cba7 and al,0x2). The COMMIT test
  is `test BYTE [esp+0x5c],0x1` (0x4cbd4) — bit0 ONLY. bit1 (TARGETLANE) is
  OR-ed into the return word but NOT tested on this path (t185 called it
  "GATE 2" — it is a RETURN FLAG here, not a gate; the flag's consumers are
  elsewhere). The handler returns eax=1 on commit (0x4cbb4).
C3 CHARGE 0x4cbe3: [+0x88] -= min(Power, power) computed at ENTRY (0x4ca89,
  before any placement) — cost 10, M1 power 90->80 EXACT.
C4 ORDER-KIND GATE at 0x4cbfd/0x4cd51 tail: cat==0 rows with [row+0x52]>1
  clear target[+0x23] bit 2; cidx==0x20 set bit; cidx 0x34..0x3b ret;
  cidx==0x3e OR target[+0x17] 1<<(ship+0x56); cidx==0x3c MAGNETRON leg:
  FUN_000220a8(ship,star) -> BYTE[+0x58]:=5 -> DWORD[+0x59]:=esi (the STAR
  BLOCK PTR — 0x4cd1c `mov [edi+0x59],esi`; t185 wrote it right) ->
  FUN_00021f58 -> slot rebuild: idx = ([+0x63]-(rec+0xab))/7 (0x4cd24..0x4cd39)
  -> FUN_000496e4 clear-slot. SINGLE-USE CONSUMPTION IS EXPLICIT LAW.
C5 FUN_00021f58 placement body: requires BYTE[+0x58]==5; target=[+0x59];
  triple := target[+0x08..+0x10] if EDI==target[+0x00] else target[+0x14..+0x1c]
  if EDI==target[+0x04] else assert; y += f32 ds:0xaee (LIVE -200.0);
  TWO LCG draws: x += draw % JITTER, z += draw % JITTER (idiv ebx; the
  magnetron caller passes ebx=0? NO — 0x4cd12 `xor ebx,ebx` BEFORE 0x21f58,
  and inside 0x21f58 ebx is RE-SET at 0x21ff2 `mov ebx,0xc8`=200 AFTER the
  first idiv?? — RE-READ carefully: 0x21ff2 mov ebx,0xc8 sits between the
  first idiv (0x21ffa) and the second (0x22016); the FIRST idiv uses the
  INHERITED ebx. Inherited ebx on the magnetron path = 0 (0x4cd12) -> idiv 0
  = divide fault?? NO: 0x21ff7 sar edx,0x1f; 0x21ffa f7 fb idiv ebx — with
  ebx==0 this would fault. Resolution: the vendor call 0x21f58 is NOT called
  with ebx=0 in practice... re-check: 0x4cd12 xor ebx,ebx happens AFTER
  0x4cd0d (the 0x220a8 call) and BEFORE 0x4cd1f (the 0x21f58 call), so ebx=0
  IS live at the call. Inside 0x21f58, ebx is only READ at 0x21f62 (`test
  ebx,ebx` — the assert-arg, je 0x21f77 skips the assert when ebx==0) and at
  0x21ff2 it is OVERWRITTEN with 200 BEFORE the first idiv?? — the first
  idiv is at 0x21ffa, AFTER 0x21ff2. ORDER: 0x21feb call 0x7824f (draw 1);
  0x21ff2 mov ebx,0xc8; 0x21ffa idiv ebx -> BOTH idivs use 200. The
  0x4cd12 xor ebx,ebx feeds only the assert-skip test at 0x21f62. NO FAULT,
  JITTER = 200 BOTH AXES. (This paragraph is the audit trail of the check.)
  pos := triple (+jitter) via FUN_00049aa8 (store +0x9e then CALL 0x533e0
  quantizer) -> BYTE[+0x58]:=4 (0x2202f).
C6 QUANTIZER FUN_000533e0 RAW (g = ds:0x895dc = 32): per axis
  x := (float)( ((int)x + (x>=0 ? +g : -g) - sign(x)/2...  exact sequence:
  edx = x>=0 ? g : -g; eax = same; edx := (eax - (edx sar 31)) sar 1  =
  (g - (-1))/2 = 16 for g=32 BOTH signs (eax=+-32; sar(edx,31) = -1 when
  edx=-32 -> eax-edx = 32-(-1)?? — NO: eax and edx hold the SAME signed g;
  for x<0: eax=-32, edx=-32 sar31 = -1, eax-edx = -32-(-1) = -31, sar 1 =
  -15 (floor(-31/2) = -16? sar = arithmetic: -31>>1 = -16). So offset = +16
  for x>=0 (32-0=32>>1=16) and -16 for x<0 (-31>>1 = -16). Then
  (float)(x + offset) -> round-fistp -> idiv g (trunc) -> *g stored.
  NET: x' = trunc((round(x + sgn*16))/32)*32 = ROUND-HALF-AWAY-FROM-ZERO
  snapping at the half-cell, i.e. the CURRENT rewrite snapGrid
  (round(|x|/32)*32 sign-directed) AGREES at ties away from zero and both
  round-half-even differences are sub-half only at EXACT .5 cells:
  vendor round() = x87 round-half-EVEN on (x+16); rewrite std::round = half-
  AWAY. They differ ONLY when x+16 lands exactly on an odd multiple of 32
  + 0.5?? — at integer-valued coordinates +16 the argument is an integer,
  NO tie exists. All witnessed coordinates are integers (f32-exact), so the
  two laws AGREE on every reachable value; the divergence class is named,
  not pinned. [verified-by-bytes; tie-class divergence UNWITNESSED]
C7 USE-ACCOUNTING GUARD 0x4a373..0x4a397 (dispatcher prologue, re-read):
  numUses(row +0x42)==0 -> unlimited, no DEC, proceed; else use-word==0 ->
  BLOCK (esi=0 -> 0x4a3cb return 0, handler NEVER runs); else DEC use-word
  ONLY when mode==1, then handler runs in BOTH modes. DEC PRECEDES the
  handler and is UNGATED by any handler-side gate: a range/affordability
  FAILURE STILL CONSUMES A USE. (M1 corroboration: use 1 -> slot removed;
  no witness of a failed-use DEC.)
C8 clear-slot FUN_000496e4 (re-read): idx-bound-free; cidx==0xFF -> no-op;
  filled dec; recalc. The rewrite's clearSlot is already verbatim.

## S3 SIM LANDING DESIGN (in progress)
Seam: public `MagnetronReport useMagnetron(int shipId, int mode)` =
dispatcher-entry composition for the kind-2 handler with the ACTIVE slot
(+0x63 surrogate = activeSlot, C4's slot-rebuild math keys on it):
  gate dispatcherGate? — the 0x4a360 entry does NOT test [+0x62] (that gate
  lives in FUN_00049f28 callers); the entry derefs [+0x63] directly. Sim:
  activeSlot<0 -> refuse (no law for a null deref; named divergence like the
  gun path).
  C7 ammo law -> C1 range gate (dist from the ACTIVE target triple — sim
  holds targetPos explicitly) -> C2 bit0 -> C3 charge -> kind-2 tail case
  tree: cidx 0x3c leg only (0x20/0x33/0x3e legs = planet/star visibility
  bookkeeping OUTSIDE the ship model — named non-goals, return flag words
  only) -> 0x220a8 order-kind gate (kind in {1,2,2-ish}: sim models the
  {3,1,2}-else-assert shape as: kind 4 with target==star handled; kinds not
  in the cited set -> refuse, named) -> +0x58:=5 -> +0x59:=star id ->
  placement C5 (+jitter 200 BOTH axes, y -200) -> quantizer snap -> +0x58:=4
  -> clearSlot(activeSlot) [C4].
  mode-0: everything computed, NOTHING lands except... C7: the DEC is
  mode-1-only, and 0x4cbcd jne exits BEFORE any store on mode 0 -> pure probe
  (flags + hypothetical values in the report).
  HONEST NEGATIVES kept: which star (S64 neg-a) stays unreconciled — pins
  assert the placement FORM (star+jitter snapped) and delta class (instant,
  no walk, power cost exact, slot gone), never vendor coordinates.
  rng law: exactly 2 draws per committed magnetron use on the sim's isolated
  stream (0x21feb/0x2200c).
