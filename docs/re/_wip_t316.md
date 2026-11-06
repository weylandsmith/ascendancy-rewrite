# t316 — MSG-EMIT-PATH HUNT (OFFLINE, ZERO capture; hand-authored)

Task (docs/STATE.md NEXT ACTION 2026-11-05T23:36): the only remaining 0x1c01
producer that picks its TARGET WINDOW DYNAMICALLY is the emit-builder at
payload 0x33374 (`bb 01 1c 00 00` = mov $0x1c01,%ebx) which emits via
fn 0x56ca4(0x7a35c, ...). Walk back to the fn prologue, objdump the span,
E8-census the entry, grid-scan entry+P0 to name the owner class; decode what
obj 0x7a35c's per-window table holds and whether FLEETWND can ever be selected.

## S0 Pre-flight
- Sitting check: live-timeline.jsonl mtime 23:41 (writer alive); 1.5GB tail
  window 60739 turn-lines, max turn 1255 == t315's value (60740 lines, same
  max — line count drift is the live writer appending restored-state lines);
  newest line turn=1086 wall=23:41:06 file=55.sav in_game=True (same restored
  state as t313/t314/t315). NO new sitting -> r1_t85g_sitting.py NOT run.
- Binding negatives honoured: t315 amendment (no sender re-sweep — census
  CLOSED at 5 sites; no key-driven shapes; LOADSCREEN dead-by-construction);
  t314 amendment (no open_fleet->digit-keys shape); t313 amendment (no
  offline censuses on fn 0x51b68/0x51cc4 targets). 0x33374/fn 0x56ca4 is a
  NEW target explicitly authorized by the assignment.
- Tools: objdump -b binary -m i386 on work/ascend_payload.bin (offline static
  law: file bytes NOT relocated); RAM via zipfile 'Memory' of saves in
  work/r1/t299-leg-20261105-212402/save; B/P0 re-derived per run via
  r315_handler_scan.py law (code-pattern hit -> B; P0 = B-0x88).

## S1 STEP 1 DONE — fn boundary + OWNER NAMED: THE EMIT-BUILDER IS CALLED
## ONLY FROM STATSHIPLST's SLOT-2 FN (objdump -b binary -m i386, verbatim)
- Site law-check: `bb 01 1c 00 00` (mov $0x1c01,%ebx) occurs EXACTLY ONCE in
  the whole payload, at 0x33374 (t315 census re-confirmed incidentally;
  `ba 01 1c 00 00` = 0x16168 + 0x35696; the t315 5-site inventory stands —
  0x1642c/0x1756b are raw-011c data/operand hits, not mov-imm sites).
- ENTRY = fn 0x33320: prologue `56 57 55 83 ec 08` (push esi/edi/ebp) at
  0x33320; frame law eax->esi (widget), edx saved +0x4, ecx->edi, ebx saved
  +0x0; epilogue `83 c4 08 5d 5f 5e c3` at 0x3344f..0x33455; next fn 0x33456
  (lea-pad `8b c0`) + tiny setters 0x33458/0x33460/0x33468. Span [0x33320,
  0x33456). (An objdump run with --adjust-vma=0x33200 mis-decodes 0x33300-
  0x33370 as a u16 table — that region is the TAIL of fn 0x33058's code, not
  data; always disassemble with default adjust-vma=0 from a known entry.)
- E8 CENSUS fn 0x33320: EXACTLY ONE caller, site 0x32778, inside fn 0x32664
  (control census same run: fn 0x56ca4 56 callers — t315's number reproduced;
  fn 0x33058 3 callers {0x32722, 0x3291d, 0x333aa}).
- fn 0x32664 IS STATSHIPLST's slot-2 fn (t314 live witness: run-2 fleet_keys
  btn_hdlr stop 'ret0 file 0x32943 inside STATSHIPLST slot-2 fn, cp 0x247c70'
  — and t315 S3 span walk [0x32664,0x3294d) matches this fn exactly). So the
  ONLY owner of the dynamic-target 0x1c01 producer is the SHIP-LIST widget
  family, NOT a map/HUD pump.
- fn 0x32664 msg dispatch verbatim: dx<8 ->0x328da; dx==8 ->0x32720 (calls fn
  0x33058 — the t314 run-2 msg-3 family sibling); 0x191 -> 0x328be; 0x192 ->
  0x32827; 0x193 -> 0x32786; else -> forwarded to fn 0x336b4 (btn_hdlr) at
  0x326af. In-rect click branch 0x32730: checks ebp(click y? arg ebx) against
  [esi+0x8/+0x10] and [esi+0xc/+0x14], then msg 0xc special (byte [esi+0x4f])
  else calls fn 0x33320(esi=widget, edx=arg, ecx, ebx) at 0x32778.
- fn 0x33320 VERBATIM KEY PATH: guard [w+0xbf] (width?) vs arg; branch on
  cmpl $0x0,0x9f100 (a GLOBAL — runtime abs P0+0x9f100); 0x1c01 road
  (0x33374): ebx=0x1c01, ecx=[[w+0x8cd]>>16], edx=[w+0x63] <- THE TARGET
  INDEX COMES FROM WIDGET FIELD +0x63; 0x1c02 road (0x3338b) identical with
  ebx=0x1c02; both then `mov $0x7a35c,%eax; call fn 0x56ca4` (0x3339c) and
  post-call fn 0x33058(widget). => 0x1c01/0x1c02 are a PAIRED message (prev/
  next page arrows of the ship list) dispatched through the global table.
- fn 0x56ca4 TABLE LAW now EXACT (verbatim 0x56ca4..0x56cdf): esi=obj
  (0x7a35c), bails ret0 if [[obj+0x4226]>>16] < 0 (mode4226 law); eax =
  edx*3 (lea (,edx,4); sub); WINNER = `mov 0x4(%esi,%eax,4),%eax` = [obj +
  edx*12 + 4]; then esi=[win+0xa7] (cp) and `call *0x8(%esi)` = DISPATCH
  SLOT-2 with msg edi->dx. Companion fn 0x56d1c (0x56d1c..): walks idx 0..
  min(0x400, [obj+0x3000]) over the SAME 12-stride table, entry valid iff
  [e+4]!=0, matches a NAME string at [e+4]+0x20 via fn 0x7892a (mode 0xa).
  => THE TABLE AT 0x7a35c IS THE WINDOW REGISTRY: stride 12, entry =
  {? , WINDOW(rec), ?}; indexed by a per-widget field +0x63 or by name.

## S2 STEP 2 — RAM MEASUREMENT: THE REGISTRY IS EMPTY IN EVERY SAVE; THE
## DYNAMIC EMIT PATH IS DEAD BY MEASUREMENT (scripts/r316_registry_dump.py +
## r316_registry_probe.py; base law FIXED again: magic recs are RAW guest
## addrs 0xfe7b48 etc., NOT P0-relative — an early probe this session made the
## t315-known base mistake and read garbage)
- Patched data base DB: code imm `mov $0x7a35c` (file 0x33397) reads
  0x2bc35c in RAM => DB=0x242000 (obj1). cmpl disp32 (0x33359) -> global
  0x9f100 runtime abs 0x2e1100.
- CORPUS MEASUREMENT (685 saves: all work/r1/t299-leg-*/save/*.sav +
  work/r1/playcap/save/*.sav, zero read failures): u32 [obj+0x4226] == 0 in
  685/685 AND u32 [obj+0x3000] == 0 in 685/685. (u16 re-read of +0x4226/
  +0x3000/+0x4228 on 60.sav: all 0.) fn 0x56ca4's FIRST instruction path
  bails ret0 whenever [[obj+0x4226]>>16] < 0 — word 0 is NOT < 0, but with
  count [obj+0x3000]==0 the name-lookup fn 0x56d1c (loop 0..min(0x400,count))
  returns 0 and every index lands on a zero entry -> win=0 -> call [0+0xa7+8]
  would fault; the fn is never reached with a live target in any captured
  state. THE 0x1c01 EMIT VIA fn 0x56ca4 NEVER DELIVERS in any save we hold.
- WHY: registration fn (fn 0x57130 region, sole 0x12345678-magic writer at
  file 0x57173 verbatim: finds free 12-stride entry ([e]!=0 skip), `movl $1,
  (e); mov %esi,0x4(e); incw 0x3000(obj); movl $0x12345678,(esi)`) is
  VIEW-GATED: the mode4226 law (t312) means the whole registry subsystem
  populates only once a view exists; [obj+0x4226]==0 across the corpus says
  NO VIEW WAS EVER REGISTERED in these saved sessions.
- CONTRADICTION BANKED HONESTLY: t315 S6 recorded `[[obj+0x4226]] =
  0x23c7969f` on 212402/58 — WRONG (mis-parsed `cmpl $0x0,disp32` at
  0x33356: took bytes +3..+6 as a u32; the value 0x23c7969f is not at
  obj+0x4226; re-measured 0x0). t315's other S6 numbers stand.
- WIDGET FIELDS MEASURED (60.sav, raw recs): FLEETWND rec 0xfe7a90 [+0x41]=
  0x5f(95) [+0x63]=0; STATSHIPLST rec 0xfe7b48 [+0x41]=0x60(96) [+0x63]=
  0x5f(95). fn 0x33320 emits with edx=[w+0x63]=95; 95==FLEETWND's [+0x41] —
  the ship-list's paired 0x1c01/0x1c02 messages are ADDRESSED AT FLEETWND's
  registry slot (structurally), but the registry is empty, so nothing is
  delivered. A stride-12 populated region exists at [0x2bc3f0,0x2bc9cc) (125
  entries, d0 in {2,4,5}) — NOT the magic registry (no rec pointers; entry0
  points into 0x19d8xx map-ish data; entries 106/107 point at 0xfe7a08/
  0xfe7ac0 with d2 not d1 layout — different table, owner unnamed).
- WHOLE-RAM POINTER CENSUS (60.sav): 126 magic recs; u32 hits pointing at any
  rec or rec+4 = 3 total (TOGGRID 1, 'I' 2) — NO pointer to FLEETWND rec
  0xfe7a90 exists anywhere in RAM (4 hits at 0xfe7ac0 = instance block, known).
  => even the window-rec side of the registry law has no FLEETWND witness.
- fn 0x33320 road selector MEASURED: global 0x9f100 (runtime 0x2e1100) == 0
  on 212402/58, 192246/58, playcap/60 -> the 0x1c01 road (else 0x1c02).

## S3 STEP 3 — THE EMIT TARGET IS FLEETWND'S SLOT ID: PAIRING LAW MEASURED
## 685/685 (the assignment's FLEETWND question ANSWERED at the addressing level)
- CORPUS (all 685 saves, rec via magic-back-walk from every 'STATSHIPLST'
  string hit): STATSHIPLST rec [+0x63] == 0x5f (95) in 685/685;
  [+0x8cd] == 0xffff0000 and [+0x57] == 0 in 685/685.
- 60.sav: FLEETWND rec [+0x41] == 0x5f (95); STATSHIPLST [+0x41] == 0x60 (96).
  => FIELD LAW (inferred from measured pairing): rec+0x41 = the window's OWN
  slot-id, rec+0x63 = the id of its PARTNER window. The ship list's
  0x1c01/0x1c02 pair-addressed emit (edx=[w+0x63]=95) is ADDRESSED AT
  FLEETWND. This is the first measurement-based link between an in-game
  0x1c01 producer and FLEETWND: t316 resolves the assignment branch "if the
  emit owner is a map/HUD pump ... else every caller's window table excludes
  FLEETWND" — NEITHER: the owner is STATSHIPLST and its target id IS FLEETWND.
- WHY DELIVERY STILL FAILS (measured): the registry itself ([obj+0x3000]
  count, [obj+0x4226] mode, the 12-stride table, and the 0x8e-stride mode
  table at obj+0x3064 with count at +0x4226 — fn 0x57130/0x57194 registration
  writers verbatim) is ZERO across 685/685 saves while 126 magic recs (the
  registration fn's own output, sole writer 0x57173) persist at 0xfe7bxx.
  => THE WINDOW REGISTRY IS RUNTIME-REBUILT / NOT PERSISTED IN SAVES — the
  same class of blindness as t313's runtime jump table (file blind) and t314's
  computed-offset stores: SAVE-TIME CENSUS CANNOT SEE THE REGISTRY, in-save
  or file. Any future witness must be LIVE (hook fn 0x56ca4 / watchpoint),
  not a save scan.
- HONEST SCOPE: fn 0x33320 runs on in-rect clicks over the ship list (msg
  0xc family, t314 run-2 witnessed msg-3 stops in this fn) — the in-game
  0x1c01 trigger shape is a CLICK on the ship-list widget with the fleet
  window open, target FLEETWND slot 95. Whether the click road is reachable
  live (registry populated in-session) is UNVERIFIED — no capture this
  iteration (assignment forbade it).

## S4 THE SLOT-ID LAW IS PROVEN STATICALLY (fn 0x3264c, verbatim)
- fn 0x3264c (STATSHIPLST-family ctor): `mov $0x7a35c,%eax; mov eax,%edx;
  call fn 0x5712c(fn obj=0x7a35c, rec)` then `mov %eax,0x41(%ebx)` — THE
  RETURNED REGISTRY SLOT-ID IS WRITTEN TO rec+0x41. This is the ONLY writer
  shape of +0x41 among the four fn 0x5712c callers (0x30c13, 0x31d03,
  0x32657, 0x5a573 all pass obj=0x7a35c). So rec+0x41 = registry slot-id
  (law, static-cited) and STATSHIPLST's rec+0x63=95 = FLEETWND's slot-id ->
  THE 0x1c01/0x1c02 PAIR EMIT TARGETS FLEETWND BY ID. fn 0x56ca4 win =
  [obj+95*12+4] which registration made == FLEETWND's magic rec, then
  `call [rec+0xa7 + 0x8]` = FLEETWND class DISPATCH SLOT-2 = fn 0x51cc4 —
  the exact handler whose 0x1c01 path (0x51f3b -> gate 0x600058 -> writers
  DAT_43508/43504) is fully mapped (t313/t315). The chain is now continuous
  end-to-end STATICALLY: ship-list click (msg 0xc in-rect) -> fn 0x33320 ->
  fn 0x56ca4(0x7a35c, edx=95, msg 0x1c01) -> [slot95].win -> FLEETWND
  dispatch -> gate byte 0x600058 -> state table -> WRITER PAIR.
- RECONCILIATION (inferred, stated as such): 126 magic recs persist in saves
  because ctors run at window construction incl. RESTORE; the registry TABLE
  (obj 0x2bc35c area) reads zero in 685/685 saves, so either the table lives
  outside the captured Memory image class or it is rebuilt post-load — the
  ctor law says registration happens in-session, so the LIVE registry is
  PRESUMED populated while playing (NOT measured — strict-close stands; the
  t317 capture settles it either way).
- t317 SHAPE (designed, not run): scratch run, open_fleet (rails=188 reguard
  per t314 drive law), arm legs {fn 0x56ca4 entry 0x56CA4, fn51cc4_entry,
  w43508_51fc2, w43504_52003}, click INSIDE the STATSHIPLST rect (rec
  geometry fields +0x8/+0xc/+0x10/+0x14 readable from a save BEFORE the run:
  read them at design time, do not guess), NO rowjump (closes FLEET). If
  fn 0x56ca4 fires with edx=95 and fn51cc4_entry fires, OQ-019's live edge
  closes at the gate byte; watchpoint 0x600058 stays the follow-up for WHO
  writes the gate to nonzero (const 0 in all saves = the datum, t315).
- RECT MEASURED NOW (60.sav, so t317 designs without a lookup): STATSHIPLST
  rect x0=7 y0=46 x1=632 y1=472 (+0xbf=28); FLEETWND rect 7,7,632,472
  (+0xbf=1792). NB fn 0x33320's own guard is [w+0xbf] vs the msg arg (see
  0x33342 jbe 0x3344f = silent ret when arg <= [w+0xbf]) — the click road
  into the emit needs the arg PAST 28; read fn 0x33058 + arg semantics at
  t317 design time before picking coordinates.

## S5 VERDICT (strict-close: NO row closed)
- Proved this iteration (static-cited + 685-save corpus): the dynamic
  0x1c01 emit owner = fn 0x33320 (sole E8 caller 0x32778 in STATSHIPLST slot-2
  fn 0x32664); target = registry slot [w+0x63]=95 = FLEETWND's slot-id
  (rec+0x41 law, ctor fn 0x3264c); chain continuous to fn 0x51cc4.
- NOT closed: no LIVE witness of fn 0x56ca4 delivering 0x1c01 to FLEETWND,
  and no witnessed store to DAT_43508/43504 — OQ-019 stays open; the honest
  negative stands: registry table zero in 685/685 saves (save-time blindness
  re-confirmed for a third mechanism class).


