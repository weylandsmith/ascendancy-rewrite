# t249 WIP — HEADER-PLANETS COUNTER + WRITER HUNT (running notes)

## S1 STATIC SHAPE OF THE +0x8c7 FIELD (Ghidra + objdump, this session)
- Program: work/ascend_restored.bin loaded in headless Ghidra (health OK,
  ascend_restored.bin active). Instruction search over 99,581 insns,
  operand "0x8c7": EXACTLY 20 hits. Only TWO write sites program-wide:
  * 0x32eb6 FUN_00032d1c: `MOV word ptr [EBP+0x8c7], BX` where
    BX = u16[EBP+0x8c7]+1 — the list-ADD routine increments the count.
    (0x325b5 FUN_00032548 and 0x33015 FUN_00032fdc zero it.)
  * guard at 0x32d2d: if count > 0xff -> FUN_0002a428 (overflow trap).
- THE +0x8c7 OBJECT IS A GENERIC SCROLLABLE LIST: entries at obj+0xcb
  stride 8 (add writes ptr at 0xcb+count*8, dword at 0xc7+count*8=0),
  count u16 @+0x8c7, top/scroll u16 @+0x8cb, selected u16 @+0x8cf (set by
  FUN_00032f6c), fields up to ~0x8f2. Capacity 0xff (trap).
- FUN_00051684 disasm (objdump base-0): EAX-in arg stored [ebp-0x4] at
  0x5168a; 0x51727 `MOV EAX,[EAX+0xab]`; 0x5172e `MOV AX,[EAX+0x8c7]`;
  cmp 1 -> singular/plural format word 0x1c/0x1d; format 0x97 at 0x51798.
  So the header PLANETS number == LIST ITEM COUNT of the list whose handle
  is u32 [widget+0xab]. FUN_00051b68 (sibling screen producer) reads the
  SAME shape ([local_c+0xab]+0x8c7) with format arg DAT_000856c4.
- Ghidra get_function_callers(FUN_00051684) = 0 (indirect/vtable dispatch;
  E8 census for 0x51684 pending).
- CONSEQUENCE FOR THE MEMORY HUNT: the counter lives in a HEAP object, so
  t248's fixed-member-offset intersection was structurally doomed across
  two different sessions (heap layout shifts). Correct instrument: per-slot
  pointer-chain walk: find u32 P s.t. u16[P+0x8c7]==expected count, validate
  P by list semantics (entries [P+0xcb+k*8] k<count point to NAMED planet
  records with owner==race), then anchor P's owner widget via pointer sites
  of (P-0xab) in data/BSS.

## S2..S7 MEMORY SIDE (tools r1_t249_listwalk/inspect/raw/content/sigscan/validate.py)
- NEGATIVE (instrument lesson): the list stores entries INLINE at obj+0xc7
  stride 8 (companion dword at +4), so "entries point to planet records"
  scans with base 0xcb (off-by-4) and 0xc7 both found nothing — because the
  entries are LIST-ITEM HANDLES (own 0x7b-stride run), not record pointers.
- THE FIND (r1_t249_sigscan.py): open-time signature of the planet-list obj
  per FUN_00051834 case 1 ([o+0xab]==0, byte[o+0xc5]==0, [o+0xbb]==0xffffffff,
  u16[o+0x8c9]==0x8d): EXACTLY ONE hit in bank-t1254/48.sav:
  OBJ=0xfda074 (heapoff 0xe1ab9c), u16[OBJ+0x8c7] = 102 == header EXACT.
  sel(+0x8cd)=0. Entries: 0x26f3e5, 0x26d1c8, 0x26d243, 0x26d14d, 0x26d057...
  — a 0x7b-stride item run (item base 0x26d057 = rec base 0x26d103 - 0xac).
- ZERO signature hits in ALL 20 sampled live-ring slots (t1086) => the list
  object only exists after the planet screen is opened; the live self-play
  session never opened it (the t1092 screenshot session was softlocked and
  its RAM rotated away).
- FUN_00051834 case 1 (the population loop, static law): allocs list ->
  widget+0xab; zeroes count; bound u16@dsx0x3a093 (=145 both slots); filter
  byte[rec0+0x33+k*0x7b]==race (DAT_0002b0ae = rec0+0x33, rec0 dsx 0x2b07b)
  — THE ENGINE'S OWN HEADER FILTER IS t248's OWNER BYTE.
- CONSEQUENCE (hypothesis, t1254-measured): header PLANETS == count(owner==
  race) AT SCREEN-OPEN TIME, FROZEN until reopen (no per-turn refresh in the
  population routine). At t1254 count==102==header. Explains t248's 60-vs-80
  @t1086 ONLY IF the screen was last opened when count was 60 — testable via
  the timeline owner-hist (next).
- TODO: item-handle offset of the record pointer (dump window at OBJ and
  item0); E8 caller census of 0x51684; bank-t1254 all-slot sig hist.

## S8/S9 (r1_t249_items.py, r1_t249_entry131b4.py) — OBJECT SEMANTICS PINNED
- Entries of OBJ (0xfda074) are a 0x7b-stride ITEM run: min 0x26d057, span
  0x4530 = 144*0x7b exactly, 102 distinct k-slots, and SET EQUALITY
  {entry+0xac} == {planet records with NAME+0x33==race0} EXACT (missing 0,
  extra 0). So the list object's count field u16[OBJ+0x8c7]=102 counts
  exactly the owner-filtered planets; item array = record array - 0xac.
- entry+0x33 is garbage (ASCII) — items are NOT records; the record pointer
  relation is entry+0xac == rec (verified set-equal, 102/102).
- Companion dwords (entry+4) nonzero (101/102) — values 0x170..0x1e6 (system
  ids?) — list is mutated after add (selection/bookkeeping), fine.
- POINTER SITE OF OBJ: ZERO u32 == 0xfda074 anywhere in the 16.8 MB Memory
  member; ditto widget guess. [inferred] the widget that held it was freed /
  its slot zeroed by screen close; OBJ survives in heap as the last-open
  snapshot. Open subitem: exact widget chain (needs live watchpoint, t250+).
  CLOSED t286b: the zero-u32 law re-reads correctly once the off-by-H is
  fixed — pointers are PHYSICAL, so the widget holds 0xfd9fec (= member
  0xfda074 - 0x88), and a scan for 0xfda074 was searching for a value 0x88
  off (slot 59 of a fresh session RAM holds u32 0xfd9fec AT member 0xfda067,
  witnessed). Live blind watchpoint fired on the refill's first add
  (writer file 0x32eb6, FUN_00032d1c list-ADD); candidate dispatch chain
  FUN_00051834 -> FUN_00055df4 -> FUN_00056e10 -> FUN_00056890 ->
  FUN_00056ca4 (vtable slot 8) -> FUN_00032d1c, honestly graded in
  docs/re/_wip_t286b.md S4 + dosbox-debugger.md t286b block.
- LEG (c) CLOSED-ISH: disp32 scan of code range [0x14bb0,0x82bb0) of
  work/ascend_restored.bin for 0x131b4: ZERO sites. 0x131b4 sits INSIDE the
  race-block array region (race blk1 intra-offset 0x1ac) — a per-race stat
  field accessed base-relative, static 60 at t1092+t1254, NOT a header
  counter (consistent with t247's refutation; no writer to pin).

## S10 (r1_t249_freeze.py) — DISPATCH + WRITER CENSUS
- FUN_00051684/0x51b68: ZERO E8 callers, ZERO u32 refs — pure indirect
  (vtable/handler-table) dispatch; the header producers are event handlers.
- FUN_00051834 (the list POPULATOR, case 1): referenced by exactly ONE u32
  at file 0x88b78 (data-seg handler table). Case 1 = screen-open path
  (allocs list iff widget+0xab==0, zeroes count via FUN_00032fdc, refills);
  case 2 reads [widget+0xab]+0x8cd (selection); case 3 and 0x1c01 = selection
  events. NO per-turn refill case exists => count is FROZEN between opens.
- u16[reg+0x8c9]=0x8d write sites: ONLY 0x325b5 and 0x33015 (the two list
  RESET routines, both also zero +0x8c7) — signature is reset-time stamped,
  i.e. the sig-hit object is the LAST-RESET/LAST-OPENED list instance.
- 24 sites write dword 0 to [reg+0xab] (widget teardown paths) — the widget
  that held OBJ was torn down (explains zero pointer sites of OBJ).
- LEG (c) FINAL: no instruction anywhere references absolute 0x131b4; it is
  a race-block-relative field (blk stride 0x1ee, intra 0x1ac). Static 60 at
  both timestamps; identity unresolved but NOT a counter (t247) and not a
  static immediate target.

## S11 LIVE EXPERIMENT (the decisive one) — HEADER LAW MEASURED AT A THIRD
## TIMESTAMP, IN OUR OWN SESSION
- windows.txt: sidebar button "Planets" rect X0 474 Y0 130 X1 632 Y1 160
  (SENDPARAM1 10) -> window-rel click (553,145) via tools/xsend (needs
  DISPLAY=:9 in env; without it: "no display").
- PRE-CLICK CONTROL: sig-scan over 20 ring slots (00:26Z sweep) = ZERO
  sig-objects (list never opened in this session).
- CLICK at 00:35:37Z. POST: every sampled ring slot 52-59 carries
  sig-obj 0xfda074 count=80; set {ent+0xac} == {owner==race0 recs} EXACT
  (80/80). u16@0x131b4 STILL 60 (third timestamp; definitively not it).
- SCREENSHOT work/screens/t3/planets_header_t1086_after_open.png: header
  reads "Chamachies (80 Planets Occupied, 26 Systems Controlled)" —
  vision-read of OUR capture: 80 == sig count == owner-count EXACT.
- LAW (measured 3x): header PLANETS = u16[list+0x8c7] of the planet-list
  object; list rebuilt (reset+refill, owner==race filter) on EVERY screen
  open; between opens the number is FROZEN (no per-turn refresh path exists:
  FUN_00051834 has no turn-driven case; the only +0x8c7 writers program-wide
  are the list add/reset routines 0x32eb6/0x325b5/0x33015).
- THE t248 60-vs-80 ANOMALY: resolved as a STALE SNAPSHOT — the user's
  t1092 header 60 was a list populated at an earlier open. WHY that open
  saw 60 while turn-1086 owner-count is 80: UNRESOLVED (that session's RAM
  rotated away). Candidates: list populated mid-turn before AI colonization
  updates landed; or the t244-lineage session opened with a different table
  state. [unverified] "occupied==populated" hypothesis: REFUTED by this
  experiment — at t1086 all 80 owner-flag planets are counted; no
  population filter.
- NOTE: the live :9 session now HAS the stamped object (count 80) — do not
  re-run this experiment to "confirm"; it is banked in
  work/r1/bank-t249-live-open/ (59/60.sav).
