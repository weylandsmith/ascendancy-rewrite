# t323 WIP — OFFLINE ACTIVATION DECODE: WHO SHOWS/ARMS BatModeWnd

Task (STATE.md NEXT ACTION t323): zero-capture decode deciding whether
BatModeWnd (the batcon/fleet UI window, OQ-019 select/destination residue
host) has ANY in-session activation trigger. If yes: name the writer + the
in-game action. If no: honest negative -> OQ-019 select/destination residues
get UNREACHABLE-BY-CAPTURE disposition (law stays t296/t321 static, cited).

Preconditions checked: sitting check — playcap 200MB tail max turn 1086 ==
t319/t320/t321/t322's (no new play; r1_t85g_sitting.py NOT run). Production
:9 (pid 1957) untouched. Fixed laws carried: t322 amendment (1)-(3); t321
amendment (1)-(4); t320 (1)-(4); t319 (1)-(4); msg-0x50 no external sender;
fn 0x1b91c decode verbatim stands (t296 S5 + t321 S4); t298 picker/rect laws.

## S0 — Static inputs
- work/t91_code_disasm.txt (140902 lines), work/ascend_payload.bin.
- windows.txt BatModeWnd block: extracted/ascend00/windows.txt lines
  1176-1188: TYPE 4 / NAME BatModeWnd / PARENT NONE / STATE 1 16 /
  X0 7 Y0 7 X1 465 Y1 472 / BACKGRNDCOLOR 0 / CURSORSHAPE 2 /
  HELPINDEX batmode. TOGGRID (TYPE 25) child at 1190+ also STATE 1 16.
- STATE field forms in windows.txt: "STATE 1 0" (most windows),
  "STATE 1 1", "STATE 4 1 3 7 13", "STATE 3 1 7 13" (variable-length list).

## S1a — Sitting check (done)
- 200MB tail max turn 1086 (== t319..t322). No new play; sitting script not run.

## S1b — windows.txt parse chain located (BM block)
- windows.txt is loaded into RAM and the parser scans it with sscanf-style
  format literals taken from the obj1 data pool: fn @0x58b40..0x58c65 (inside
  the winmgr windows.txt loader; "windows.txt" literal payload 0x85bac -> imm
  0x2ffc site 0x575c2) parses BM-block fields via fn 0x77fe1 (scan helper,
  args: stream esi, format imm, out ptrs). Formats pool run at payload
  0x85e48..0x85f58 ("%s %d", "%s %s", "NONE", block tags "BM"@0x85ecf,
  "SW"@0x85f44 etc). Immediates like 0x331f/0x32f9 at push sites 0x589bd/
  0x589e2 are FILE-OFFSET-into-the-loaded-file-buffer anchors (offsets into
  extracted/ascend00/windows.txt land on real field text: 0x331f =
  'HAPEFRAME -1\r\nSOUNDCHANNEL', 0x3347 = 'MESSAGE    0\r\nSENDPARAM1' — the
  BM block region). STATE keyword is NOT a NUL string anywhere in the payload
  (only "STATE%02d"@0x8598b) -> the STATE line is consumed by the same
  scan-chain anchored by these format runs; STATE value lands in a per-window
  record field consumed at 0x5898e..0x58ae6 + 0x58aff..0x58b3e loop via
  helper fn 0x31d58 (window eax, value di, out ebx): iterates table
  [win+0xab] stride 14 (count u16 high half of [win+0xad]), on match writes
  dx -> rec[+0xa] (0x31dd0) and copies 14B record out (ecx path). fn 0x32000
  (0x32000..0x32047) loops count ds:0x13b98 writing WORD [i*14 + [win+0xab] +
  0xc] = BYTE[i*0x1ee + 0x12e18]*5 + 0x14 — per-state shape-frame sizing.

## S2 — Name-lookup law + BatModeWnd's ONLY code-level name reference
- OQ-004 pool-relative immediate law applies to code immediates: `mov
  edx,0x2bf7` at 0x52a71 = payload 0x82bb0+0x2bf7 = string "BatModeWnd"
  (status.cpp pool). Verified 0x2c02="COSMOSWnd", 0x2c0c="RESWIN",
  0x2c13="RACECONTROLS". (Shell grep for "a7 57 08 00" = 0 hits was RIGHT:
  full absolute addresses never appear; only pool imms.)
- fn 0x2351c(eax=wmgr base, edx=name-imm): checks [base+0x32dcf] high half
  ==1, iterates registry [base+0x3333] (count high half), name-compares,
  returns window-record ptr (registry stride 0x27 at [base+0x3337] per
  0x23619..0x2361f loop). CALLERS (exhaustive, 3): 0x21530 (gated by fn
  0x78283("NOINTRO"-region string 0x8355d) — boot path), 0x24f96 (rnd-heavy
  path), 0x52a76 = THE ONLY BatModeWnd lookup in the image.
- Block @0x52a44..0x52b37 verbatim: fn 0x52678(ebp) must return -1 (else
  jne 0x52f97 skips everything); then fn 0x232ec(0x12e10, edx=0); fn
  0x238e8(0x12e10); fn 0x2351c(0x12e10, "BatModeWnd"); then fn 0x56d1c
  (0x7a35c, "COSMOSWnd"@0x2c02) + clear loop [rec+4..0x197a] stride; fn
  0x56d1c(0x7a35c,"RESWIN"@0x2c0c) + clear; fn 0x56d1c(...,"RACECONTROLS")
  + float-init; then fn 0x56d1c(0x7a35c, edx=0x2c20) -> **fn 0x32000(eax,
  edx=1)** @0x52b37. fn 0x32000 = per-state-STATE-table writer: for i <
  ds:0x13b98: WORD [i*14 + [rec+0xab] + 0xc] = BYTE[i*0x1ee + 0x12e18]*5 +
  0x14 (shape-frame sizing per state id).
- fn 0x232ec(eax=base,edx): BYTE [base+0x8]=dl then for all [base+0xd88]
  window records (stride 0x1ee) BYTE [rec+0x8] = dl — GLOBAL show/hide-ish
  switch byte at window-record +0x8, set with edx=0 in this block.
- fn 0x2bf23 (inside fn 0x2bee0): reads DAT_43510 bl, if ==1 reads ds:0x7458e
  -> score idx -> fn 0x4f86c(0x78638); then fn 0x336b4 — the t321
  default-handler tail. fn 0x2bee0 is a msg wrapper (cmp dx,0x1).

## S3 — fn 0x528ec: the RIGHT-PANEL msg handler holding the only in-session
## BatModeWnd name-lookup; RESULT DISCARDED (not an activation path)
- fn 0x528ec(ebp=window rec; template copy from ds:0x895c8) dispatches
  0x5290d..0x52945 verbatim: jb 0x1f5 -> 0x52f59; ==0x1f5 -> 0x52db9;
  0x1f6..0x1f8 -> 0x52f49; 0x1f9/0x1fa -> 0x52eec; >0x1fa: cmp dx,0x1c01
  je 0x52d6c else fn 0x336b4 default (t321 law shape).
- fn 0x52678 = hotspot test on MOUSE WORDS ds:0x484ec (x) / ds:0x484f0 (y):
  returns -1 iff x in [0x1f7..0x277]=[503..631] AND y in
  [0x17e..0x1d7]=[382..471].
- Block 0x52962 (rect [0x17b..0x1ed]x[0x1a4..0x1d8] = [379..493]x[420..472]
  hit): ring post fn 0x56ad4(0x7a35c, ebx=0x69b8, code 5) -> return -1.
  0x529a4 (miss + hotspot -1): ring post 0x69c4 code 5.
- Block 0x529d2: rect HIT -> fn 0x4fb30(0x78638,0); WORD[ebp+0xb5] =
  (x-0x17b)>>4 (13-col cell index); fn 0x232ec(0x12e10, [ebp+0xb3]>>16);
  virtual call [rec+0xa7 class-table]+0xc(ebp, edx=0); return -1.
- Block 0x52a44 (rect MISS): requires hotspot -1 (mouse NOT in
  503..631x382..471 else jne 0x52f97); then fn 0x4fb30(0x78638,0); fn
  0x238e8(0x12e10); **fn 0x2351c(0x12e10,"BatModeWnd")@0x52a76 RESULT
  UNUSED** (next insn overwrites eax); then registry clears:
  fn 0x56d1c(0x7a35c,"COSMOSWnd") + zero [rec+4..+0x197a];
  fn 0x56d1c(0x7a35c,"RESWIN") + zero [rec+0x11f..+0x126];
  fn 0x56d1c(0x7a35c,"RACECONTROLS") + float-init;
  fn 0x56d1c(0x7a35c, edx=0x2c20="..\status.cpp") -> fn 0x32000(rec,1).
  => This is a DESELECT/CLEAR path on right-panel clicks OUTSIDE the two
  hot rects — it WRITES NOTHING to any BatModeWnd record and never calls
  through BatModeWnd's class table. NOT an activator.
- fn 0x4fb30(eax=0x78638 table, edx=dx): early-outs unless [tbl+0x213]!=-1
  && [tbl+0x20b]!=0; fn 0x500e0(dx) lookup — a selection/registry accessor.
- Boot-path BatModeWnd lookup 0x21530: gated by fn 0x78283("resume.gam")
  != 0 (@0x21522, string payload 0x8355d VERIFIED "resume.gam") — runs once
  at startup iff resume.gam exists; caller 0x24f96 sits in a random-draw
  (fn 0x7824f x5) setup path. fn 0x2351c body = name->record lookup +
  occupancy-map byte writes at [wmgr+0x32dda..] (imul x100 grid) — layout
  bookkeeping, NOT a state/visibility store.
- STATE-line semantics (loader): fn 0x31d58(win eax, di) walks 14-byte
  records at [win+0xab] (count [win+0xad]>>16) comparing di == record low
  WORD; on match writes BYTE 1 -> [matched+0xa] (0x31dd0) / copies 14B out
  (0x31db3 path); callers 0x58ac5/0x58b19 pass di = 1<<i built in a loop
  over i < ds:0x13b98 — the STATE list is a BITMASK TABLE consumed at
  windows.txt load time (fn 0x32000 sizes per-entry shape frames at +0xc).

- Payload string pool (winmgr.cpp region) carries the windows.txt field
  literals + per-type parse chains; BatModeWnd string sits adjacent to
  COSMOSWnd/RESWIN/RACECONTROLS/RACELIST (status.cpp->winmgr.cpp pool), and
  the BM block parse chain is bracketed by literal "BM" ... "%s %s %s NONE"
  ... run of "%s %d" scan strings (visible via strings -a dump of
  work/ascend_payload.bin).

## S4 — State-record semantics + COMPLETE writer census of the STATE fields
- Window-record STATE machinery layout (verified from fn 0x31e74/0x31f30/
  0x32048/0x31d58 reads/stores): [win+0xab] = state-record table ptr,
  [win+0xad]>>16 = record count, [win+0xaf] = single-record index (>>16,
  -1 = none), [win+0xb1] = WORD CURRENT STATE id, [win+0xb3]/[win+0xb5]
  aux words, [win+0xb7] cursor/kind byte. Records stride 14: rect u16s at
  +0..+6 (x0,y0,x1,y1 read via dword high halves), flags u16 at +0xa
  (bit0 present, bit1 current, bit2 toggled by fn 0x32048), size WORD at
  +0xc (fn 0x32000: frame*5+0x14).
- fn 0x31e74(win, ecx, edx, ebx): rect-contains hit over state records;
  returns record idx or -1; fast path checks the [win+0xaf] record and
  returns CURRENT [win+0xb1] on hit.
- fn 0x31f30(win, si) = THE state-setter: rejects si==[win+0xb1]; bounds
  assert vs [win+0xaf]; clears bit1 on old record (0x31f7b); sets bit1 on
  new record iff bit0 (0x31fab); **WORD[win+0xb1]=si @0x31faf**. CALLERS
  (exhaustive grep): ONLY 0x321ad and 0x3221b — both INSIDE fn 0x32100.
- fn 0x32100(win, dx, ecx->edi, ebx) = a msg handler with jump table
  cs:[0x1d524] over msgs 0..8 (0x3210b cmp ax,8 ja -> fn 0x336b4 default
  @0x322e7). Case @0x321ca: point-in-window-rect ([+8..+0x14]) -> fn
  0x31e74 hit -> fn 0x4fb30(0x78638) + fn 0x31f30 (SET STATE) + fn 0x32048
  + virtual repaint [[win+0xa7]+0xc] + registry dispatch fn 0x56ca4. Case
  @0x32196: fn 0x31e74 [win+0xb1]-changed -> fn 0x31f30 + repaint.
  fn 0x32100 is NOT in the BATMODE class table (t296: BATMODE =
  [0x1abfc,0x30d08,0x1aef8,0x1d858,0x311b8,0x1e9dc]). Its class-table
  reference sits at payload 0x603ea (dword scan, sole occurrence).
- fn 0x32048(win, edx): bounds-checks edx vs [win+0xaf]; flags bit0 must
  be set else returns 0; flips bit2 (0x320bf/0x320c5); returns masked
  WORD[rec+0xa].
- COMPLETE +0xb1 write census (image-wide grep, 14 sites): fn 0x31f30
  (THE setter), fn 0x31c79 (=0xffff), fn 0x33787 (=0), fn 0x339a4 (=ax),
  fn 0x33c73 (=cx), fn 0x33d1b (=0xf3), fn 0x364d2 (=ax), and
  BATCTRL-family 0x1568c/0x15ae3/0x15b68/0x15e9b/0x1607d/0x16122/0x161c3
  (mostly =0; the =reg sites belong to the BATCTRL class window's OWN
  state field — class table [0x15630,...] per t296 — not BatModeWnd).
- fn 0x1d7dc (BatModeWnd class slot-4, exit of fn 0x1aef8): PURE
  repaint/teardown helper — fn 0x1a338 over sub-structs
  +0x1d36/+0x253a/+0x2d3e, fn 0x1a8dc(+0x3542), fn 0x1bfa4(this),
  fn 0x1a39c x2, and esi==0 -> virtual [[rec+0xa7]+0xc](rec,0) hide-call.
  NO state write. NOT an activator.
- fn 0x1be10 (same family): CURSOR chooser — if [win+0x41]==ds:0x7d35e
  picks cursor code from [win+0xb8] + {+8 if [win+0xb7]==1, +6 if 2/3, +1
  if [win+0xaf]!=0} and calls fn 0x5a1e4(0x7a35c). NO state write. NOT an
  activator.
- fn 0x2351c FULL BODY RE-READ: edx name-arg is used ONLY as an assert
  message arg; body = n*(n-1) pair-matrix init at ds:0x48c44 + 10000B
  clear at [wmgr+0x32ddb] (fn 0x76e30, arg [wmgr+0x32ddb], 0xff>>1=127) +
  per-registry-entry grid byte writes [wmgr + BYTE[a+4]*100 + BYTE[b+4]]
  = 1 @0x23657/0x23665. LAYOUT BOOKKEEPING ONLY — the "BatModeWnd" string
  at 0x52a71 never influences control flow (dead assert-name arg).

## S5 — Remaining +0xb1 writers classified; visibility path closed
- fn 0x364d2: edx = [esi+0xaf] (state-TABLE ptr), so the store hits the
  TABLE at +0xb1, NOT a window current-state field -> excluded from census.
- fn 0x33c73 (fn 0x33c34, sole caller 0x5597f = registry-add path):
  sets [win+0xab]=edi, [win+0xaf]=cx, [win+0xb1]=strlen(edi)-1 (repnz scas
  @0x33c6e), [win+0xb3]=[win+0xb1] — CONSTRUCTION-TIME bookkeeping keyed on
  the name string length (asserts 0x91b/0x921). Not runtime.
- fn 0x33d1b (fn 0x33d08, sole caller 0x33cba adjacent to 0x33c73):
  constants +0xab=0, +0xaf=3, +0xb1=0xf3. Constructor-shape. Not runtime.
- fn 0x33787 (fn 0x3377c, sole caller 0x3372e): constructor-shape init
  (+0xb7=0xf2 cursor, +0xb9=0x7d3a2, +0xbd=-1, +0xb5=ds:0x6610). Not
  runtime state switching.
- fn 0x339a4 (in fn 0x3377c+0x1e8 region — CHAR-INPUT handler: gates on
  bl in [0x30..0x39]|[0x41..0x5A]|[0x61..0x7A]|0x20|0x2D @0x33964..0x3398a,
  then [esi+0xb1]=[esi+0xb3]=0 + BYTE[[esi+0xab]]=0, or fn 0x33b88 +
  inc [esi+0xb3] + repaint while [win+0xb1] < [win+0xaf]): a TEXT/EDIT
  state-cycling handler. BatModeWnd's msg tree (t296 S5 + t321) contains
  NO char handler -> unreachable for BatModeWnd.
- fn 0x31f30 callers EXHAUSTIVE = {0x321ad, 0x3221b} both inside fn 0x32100
  (msg 0..8 handler, jump table cs:[0x1d524], default -> fn 0x336b4).
  fn 0x32100 = generic STATE-RECT CLICK SWITCHER: fn 0x31e74 hit-test ->
  fn 0x31f30(new id) -> repaint [[win+0xa7]+0xc]. fn 0x32100 appears
  NOWHERE in the static image except a misaligned jump-table byte (0x603ea
  FALSE POSITIVE — bytes of 0x21000003|0xae at 0x603e8/0x603ec); class
  tables are RAM-relocated (t303 (5): static image holds no plaintext
  tables). Per t296 S? the cited BATMODE table is
  [0x1abfc,0x30d08,0x1aef8,0x1d858,0x311b8,0x1e9dc] — fn 0x32100 NOT in it.
- fn 0x314e8(win, dx, ecx, ebx) = CHILD PROPAGATOR: iterates [win+0x67]
  child array (<=0x14), calls [[child+0xa7]+0x8](child, dx) per child
  (gate: child [child+0x35]==0 unless dx>>16==1). fn 0x314e8 callers
  include fn 0x156d4 (BATCTRL slot-2 handler, t296 table BATCTRL=
  [0x15630,0x30d08,0x156d4,0x16420,...]) @0x15882.
- fn 0x156d4 BatModeWnd touch (0x15758..0x15769): fn 0x56d1c(0x7a35c,
  edx=0x5e -> pool 0x82c0e "BatModeWnd" VERIFIED) result stored
  [ebp+0xbb], NEVER READ in the decoded span; then BatListWnd (imm 0x77 ->
  pool 0x82c19 "BatListWnd" VERIFIED): [BatListWnd+0xab]=0 + fn 0x32c5c +
  BYTE[BatListWnd+0xc5]=0 + fn 0x32fdc — BATCTRL RESETS BatListWnd's state
  table, not BatModeWnd's. fn 0x32c5c = viewport surface (re)allocation
  (fn 0x1fc34(0x9f10c,...)+fn 0x61058 -> [win+0xbf]), not deactivation.
- fn 0x32048 sole caller = 0x32224 (inside fn 0x32100). fn 0x232ec callers
  5x all wmgr-glob
</think>

<tool_call>
<function=terminal>
<parameter=command>
cd /home/hrethric/projects/ascendancy && cat >> docs/re/_wip_t323.md <<'EOF'

## S6 — CONCLUSION (honest negative): BatModeWnd activation has NO
## in-session trigger
Census-complete argument:
1. STATE 1 16 is NOT a visibility/activation flag. The STATE line is the
   per-window state-RECORD table parsed at windows.txt load (14B records,
   rect+flags+size; loader fn 0x31d58 builds it, fn 0x32000 sizes frames
   value*5+0x14). Runtime state = WORD [win+0xb1] (current record id),
   [win+0xaf] = count.
2. Runtime writers of [win+0xb1] (image-wide, 14 sites, all classified in
   S4/S5): constructors (fn 0x31c54=0xffff, fn 0x3377c, fn 0x33d08,
   fn 0x33c34 — construction-time), the char-input state cycler fn 0x339a4
   (unreachable for BatModeWnd: no char handler in its msg tree, t296/t321),
   fn 0x364d2 (writes the TABLE not a window field — excluded), and THE
   ONLY runtime switcher fn 0x31f30 <- exclusively fn 0x32100 (generic
   state-rect-click msg handler), which is NOT in the cited BATMODE class
   table (t296: [0x1abfc,0x30d08,0x1aef8,0x1d858,0x311b8,0x1e9dc]).
3. Every code path that names BatModeWnd at runtime is inert or foreign:
   fn 0x2351c (sole image-wide lookup @0x52a76 + boot @0x21530 +
   @0x24f96) — the name immediate is a DEAD assert/debug-string arg
   (overwritten @0x23558 before use); body = layout bookkeeping at
   ds:0x48c44 + [wmgr+0x32dda]. fn 0x156d4 (BATCTRL) stores the lookup
   result unread and resets BatListWnd instead. fn 0x528ec block 0x52a44
   (right-panel deselect) same dead-arg pattern.
4. Therefore BatModeWnd's state is PINNED at construction; no mouse click,
   key, or message reachable from the campaign/system-map session can
   switch/activate it. Fully consistent with t322 branch (b): with legs
   {batmode_dead, fn1b91c_entry, w43508_1b5e6, w43508_1baa7} armed and the
   instrument MATCH=True, BatModeWnd received ZERO msgs — the window is
   composition-shielded BY DESIGN of its state table, not by an untried
   activator.
DISPOSITION (per t323 task spec): OQ-019 select/destination residues
= UNREACHABLE-BY-CAPTURE. Static law stands cited (t296 S5 four gates +
t321 S1-S4 msg decode + t322 armed-zero). NO future capture can close the
select leg. No ledger row closed this iteration (strict-close: the negative
IS the datum; the row stays open with narrowed scope).
Caveats (honest): (a) dispatch internals below the class-table indirection
are not fully enumerated (t303 refuted the universal-slot-1 law); the
conclusion rests on the cited class tables + t322's armed-zero, not on a
complete dispatcher enumeration. (b) fn 0x32100's class-table owner is
UNNAMED statically (RAM-relocated tables); if a future RAM census ever
found fn 0x32100 installed in BatModeWnd's table, this conclusion reopens
— re-open check: enumerate BatModeWnd RAM table slots at [rec+0xa7].
