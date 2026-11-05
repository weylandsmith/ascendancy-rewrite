# t301 — TOGGRID control-click disambiguation (RESULTS)

## S0. Session battery (r299_relaunch.sh, runs t299-leg-20261104-{213540,214042})
- attempt-1 (213540): full good choreography (t1086->1087, FLEET diff 122756,
  row-93 -> star='Icarus', sprites [(48,151,296)], planet (439,331), empty
  (236,200)); 8 legs armed incl. handler 0x1aef8 + router 0x1b070.
  NOFIRE x3 map clicks + NOFIRE TOGGRID_control. rc=1 hits=0.
- attempt-2 (213954 dir? console attempt-2): BREAK lottery LOST (channel dead).
- attempt-3 (214042): identical battery, identical NOFIRE x4 (session.log
  lines 45-51: clicks delivered rc=0, NOFIRE sprite/planet/empty/TOGGRID).
=> CONTROL CLICK ZERO-FIRED IN BOTH FULL SESSIONS.

## S1. CONTROL-CLICK VALIDITY AUDIT — THE CONTROL WAS INVALID (pixel-proven)
Pixel census of 23_view0_r93.png (both runs byte-similar):
  - rect 557,403-587,433 (the "TOGGRID" rect): uniq colors = 2, mean RGB
    (0.1,0.1,0.1), max 113 -> BLACK. No button was there.
  - rect 479,403-630,433 (whole child-button strip): uniq=5, mean ~(0,0,0).
  - BatModeWnd rect 7,7-465,472: uniq=222 (rich content: planet, ships, bases).
  - _raw_*_map.png grabs: same region solid black (uniq=1, max=0).
windows.txt VERBATIM (game-wp copy) shows WHY the pixel test is decisive:
BOTH windows.txt name spaces overlap at that rect:
  TOGGRID   type 25 PARENT BatModeWnd rect 557,403-587,433 SENDMESSAGE 74
  TOGSHIPS  type 25 PARENT COSMOSWnd  rect 557,403-587,433 SENDMESSAGE 58
and the two parent windows are SIBLINGS with IDENTICAL rects:
  COSMOSWnd type 2 rect 7,7-465,472   BatModeWnd type 4 rect 7,7-465,472
(the t300 note "children all x>=479" inherited this ambiguity: those children
belong to BOTH windows alternately).
CONSEQUENCE: the t301 disjunction (FIRES=>bypass / ZERO=>attribution dead) is
VOID as executed — the control click hit black pixels of whichever window is
NOT showing its sidebar (or a not-painted button). ZERO fires on an invisible,
possibly-inactive target proves nothing. The t300 negative for the MAP clicks
(inside 7,7-465,472, rich content, same sessions state-changed) STANDS.

## S2. Static/ram laws banked this session (run 59.sav, B=0x1bf4d8, P0=0x1bf450)
1. Handler phys P0+0x1aef8=0x1da348: exactly ONE aligned u32 hit in RAM:
   member 0x247978 = SLOT 2 of a 6-slot dispatch table at member 0x247970
   (phys 0x2478e8). Slots (phys): [img+0x1abfc, img+0x30d08, img+0x1aef8,
   img+0x1d858, img+0x311b8, img+0x1e9dc] — all convert to sane file offsets
   under the PER-SLOT law phys = P0 + file_off.
2. WHO WRITES THE TABLE POINTER: two code sites store imm32 0x2478e8 into
   window-record field +0xa7:
   - RAM member 0x1da0be: `mov dword [edx+0xa7], 0x2478e8` (static img+0x1abe6
     holds the SAME opcode form with placeholder imm 0x58: c7 82 a7 00 00 00
     58 00 00 00) — RELOCATED IN RAM (imm patched static+P0).
   - RAM member 0x1da0fa: `mov dword [eax+0xa7], 0x2478e8` (static img+0x1ac22,
     same placeholder-0x58 form).
   => the batmode msg layer IS wired to a window record via field +0xa7 at
   runtime; router 0x1b070's read of [win+0xaf] is the neighbouring byte.
3. ALIGNED full-RAM scan: u32==0x2478e8 has exactly ONE hit (the code imm at
   0x1da0c4); the only other byte-sequence hit is member 0xfdc9cb — UNALIGNED,
   inside the live BatModeWnd window RECORD (see 4). => no second window
   record holds the batmode table (aligned), consistent with one class.
4. WINDOW RECORD LAW (pointer-value law confirmed): live window record for
   "BatModeWnd" at member 0xfdc924 (phys 0xfdc9ac): +0x00 magic 0x12345678,
   +0x04 ptr->mem0x28a470, +0x08..0x14 = 7,7,0x1d1(465),0x1d8(472) == windows.txt
   rect VERBATIM, +0x20 ASCII "BatModeWnd", +0x50 ASCII "atmode" tail (name
   copy #2), +0xa7 (unaligned) = 0x2478e8 dispatch table. The record is a
   runtime heap object with magic 0x12345678 — ENUMERABLE: scan RAM for the
   magic to enumerate all live window instances + their +0xa7 tables.
5. BatModeWnd-name-string ref in CODE: member 0x1d4c31 img+0x15759 region —
   `mov edx,0x24205e / mov eax,0x2b2c5c / xor ebx,ebx / call ...` (class-record
   construction call; string phys refs relocate static 0x5e/0x69/0x77 immediates
   by +0x242000 in RAM — a SECOND relocation base for data-page imms).

## S4. WINDOW-RECORD + CLASS-TABLE LAWS (run 59.sav; phys->member = +0x88)
1. MAGIC ENUMERATION: u32 0x12345678 finds the LIVE window records (126 hits,
   2 false positives: 0x1a9374, 0x21664d — data noise). Record layout:
   +0x00 magic, +0x04 shared ptr 0x28a4f8(all), +0x08..+0x14 rect x0,y0,x1,y1
   (matches windows.txt VERBATIM: COSMOSWnd & BatModeWnd both 7,7,465,472),
   +0x20 name[8..], +0x50 name tail copy, +0xa7 DISPATCH TABLE PTR (phys),
   +0xac.. window-state (COSMOS populated, BatMode zero/0xffff => BatMode
   INACTIVE in the system view).
2. KEY INSTANCES: COSMOSWnd record 0xfd2398 (table phys 0x247a4c), BatModeWnd
   record 0xfdc924 (table phys 0x2478e8), BatControlWnd record 0xfdbebc
   (rect 0,0-0,0 — closed; table 0x247850), TOGGRID child 0xfe5b00 table
   0x247ca0 (type-25 button class), FLEET 0xfd5f54 / NEXTTURN 0xfd6218 table
   0x247cb8 (type-0 button class — THE class whose legs the WORKING clicks
   executed; never armed in t299/t300/t301!).
3. COSMOS TABLE (phys 0x247a4c, member 0x247ad4):
   [img+0x26818, img+0x30d08, img+0x26b34, img+0x27e80, img+0x1f0608, img+0x2925c]
   — SAME SHAPE as BatMode table (slots 1,4 shared). Prologues verified code:
   0x26818 `53 51 56 57 89 c3 89 d1 f6 c1 04` (class-entry shape, mirrors
   batmode slot0 img+0x1abfc), 0x26b34 `56 57 55 83 ec 3c` (handler shape,
   mirrors batmode slot2 0x1aef8 `56 57 55 83 ec 14`).
4. INSTALLERS: batmode table imm 0x2478e8 at code members 0x1da0c4/0x1da0e0
   (S2.2). COSMOS table byte-scan hits: 0x1e5c2d + 0x1e5d1d (INSIDE the COSMOS
   class functions img+0x2679x/0x268ax region — same install pattern at
   unaligned offsets) and 0xfd243f (= record 0xfd2398 + 0xa7, self). => both
   classes are wired at runtime; t299's zero-fires are explained if dispatch
   went to the ACTIVE window's table (COSMOS) while all armed legs sat in the
   INACTIVE BatMode class.
5. STRING REFS: 'BatModeWnd' phys ref only at code member 0x1d4c31; 'COSMOSWnd'
   phys ref only at member 0x1f5943 (one class-registration site each).
6. OPEN (next): what does msg dispatch actually CALL — grep the image for E8
   rel32 call sites to COSMOS slot2 img+0x26b34 and for the generic dispatcher
   `mov *(rec+0xa7)`; then the WITNESS SET for system-view clicks = {COSMOS
   class-entry 0x26818, COSMOS handler 0x26b34, type-0 button table 0x247cb8
   legs}. The batmode layer (0x1aef8 family) is NOT it.
   CAVEAT (self-audit): ALL 126 records exist at all times (built at startup),
   so +0xac state fields are NOT proof of which window is VISIBLE/dispatching —
   the "BatMode INACTIVE in system view" line above is INFERRED, and the
   Icarus-view screenshot (5 top icon panels incl. 'Scientist Takeover') is not
   plainly any single windows.txt window. THE LIVE ADJUDICATOR is the router
   stop: bank_stop now dumps the window-record head (magic+NAME) from eax/ecx
   at every stop, which names the dispatching window directly.
   SHARPENING: vision on 23_view0_r93.png — the view shows FIVE top icon
   panels incl. a 'Scientist Takeover' text panel over a starfield (tactical
   chrome). 'Scientist Takeover' is a BATTLE action (BatControlWnd family,
   record 0xfdbebc table 0x247850), and the harness's FLEET-row-jump may put
   the game in the ORBITAL/COMBAT screen rather than a plain COSMOS system
   view. So the dispatching window of the battery clicks is one of
   {BatControlWnd, BatModeWnd, COSMOSWnd} — NOT yet pinned; the router stop's
   record-NAME is the decisive measurement. BatControl table 0x247850 was
   never armed either.

## S6. DISPATCH LAW CLOSED STATICALLY (payload byte-patterns, this session)
1. CALL MECHANISM: `mov ecx,[win+0xa7]` (8b 88/8a/... a7 00 00 00 — 20 sites)
   then `call [ecx+4]` (ff 51 04 — 5 sites: img+0x26eda, img+0x30d02,
   img+0x7a7eb, img+0x7aa3e, img+0x7b020). Table slot 1 IS the dispatcher.
2. UNIVERSALITY MEASURED (RAM, run 59.sav): slot 1 == phys 0x1f0158 == P0 +
   file 0x30d08 for ALL sampled class tables (batmode 0x2478e8, cosmos 0x247a4c,
   type-0 button 0x247cb8, type-25 toggle 0x247ca0, list 0x247c70). File
   file 0x30d08 prologue 51 56 57 55 0f b6 f2 8b 48 08 (function entered ONLY
   through slot 1; the caller-side pair `mov ecx,[eax+0xa7]; movzx edx,dl;
   call [ecx+4]` sits verbatim at img+0x30cf9..0x30d07, immediately before it).
   => t299/t300 armed ZERO of these; every click (working or not) walks
   slot1 0x30d08. The zero-fires were 100% an attribution failure, not a
   bypass law.
3. TYPE-0 BUTTON TABLE (FLEET/NEXTTURN, phys 0x247cb8):
   [0x30ad8, 0x30d08, 0x336b4, 0x30fb4, 0x311b8, 0x316f0] — entry 53 51 83 ec
   04, handler 56 57 55 83 ec 04. These legs fire on the clicks t300 proved
   work; NEVER ARMED. COSMOS table = [0x26818,0x30d08,0x26b34,0x27e80,0x1f0608,
   0x2925c].
4. SCRIPT RE-ARMED: scripts/r299_leg_session.py LEGS = {router 0x30d08,
   cos_entry 0x26818, cos_hdlr 0x26b34, cos_s3 0x27e80, cos_s5 0x2925c,
   btn_entry 0x30ad8, btn_hdlr 0x336b4, batmode_dead 0x1aef8}; --legs default
   updated; MEMDUMPBIN control moved to router (bytes-checkable vs payload);
   bank_stop now dumps 48-byte window-record head per register window (magic
   0x12345678 + NAME at +0x20) so every stop NAMES the dispatching window;
   --control-click default flipped to 0 (S1 invalid-control audit). The
   End-Turn/FLEET clicks are now the BUILT-IN positive control: with btn_* +
   router armed, a session where they change state but fire nothing means the
   INSTRUMENT is dead — attribute to harness, not game.
   py_compile OK. NOT RUN this iteration (session budget: 3 debugger sittings
   already consumed by t301's control-click runs).

## S7. Verdict on the t301 assignment
The STATE.md disjunction was executed as assigned and is VOID-AS-RUN (control
invalid, S1) but the same evidence + offline static work resolves the
underlying question with higher confidence: system-view clicks DO walk msg
dispatch (slot1 thunk 0x30d08 is universal), and the t299/t300 zero-fires are
explained BY MEASUREMENT as arming the wrong class table (BatModeWnd is
INACTIVE in the system view: its record 0xfdc924 state fields +0xac.. are
zero/0xffff while COSMOSWnd 0xfd2398 is fully populated). No ledger row
closes (strict-close: OQ-016 r1, OQ-019 r1/r3 need the actual selection/order
witness). Next = ONE debugger run with the re-armed LEGS (this script), no new
instruments needed.
