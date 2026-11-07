# t324 — RAM CLASS-TABLE CENSUS (BatModeWnd [rec+0xa7]) — WIP

Task (STATE.md NEXT ACTION t324): test the t323 re-open condition. t323 closed
the [win+0xb1] activation route census-complete STATICALLY, but static class
tables are RAM-relocated (t303(5); t296 installer img+0x1abe6/0x1ac21 writes
imm 0x58e8 -> RAM +P0), so fn 0x32100's absence from the cited BATMODE table
[0x1abfc, 0x30d08, 0x1aef8, 0x1d858, 0x311b8, 0x1e9dc] is cited-but-indirect.
DELIVERABLE: slots MATCH cited law => negative ABSOLUTE (every OQ-019 capture
route now cited-dead); MISMATCH => t323 reopens, name the writer.

## S0. SITTING CHECK + STEP (0) ARTIFACT GREP (measured)
- Sitting check: tail-seek 400 KB of work/r1/playcap/live-timeline.jsonl ->
  newest turn = 1086 (16 lines in tail) == corpus turn. NO new sitting; t324
  stands as assigned.
- Step (0) grep: `find work/r1 -name 'MEM_*.BIN'` -> 10 files, all SMALL
  code-side control/head dumps from leg sessions (t299/t301-era
  MEM_CONTROL_001DAD6C, MEM_CTL_CENSUS_0021612A, t299
  MEM_POST-RUN-IMMEDIATE_ESI_00247ADC, t320-era *_002BC35C heads). NONE covers
  the window-registry region; and per t307 S4 the MEMDUMPBIN dumps carry
  rebased code bytes anyway. No prior RAM dump answers t324.
- ZERO-BOOT PATH TAKEN: the pointer law (OQ-011 CLOSED, STATE WHAT-IS-IN-HAND)
  makes the save-ZIP `Memory` member a full guest-RAM image: member index for
  data offset X = B + 0x82BB0 + X; member byte -> physical = member - 0x88;
  stored u32 values are guest-PHYSICAL (t298 binding). Production saves
  work/r1/playcap/save/56..60.sav (mtime Nov 6 20:28-20:29, t=1086 corpus) are
  READ-ONLY inputs — production :9 (pid 1957) untouched, no guest boot, no
  scratch copy, no capture. This supersedes steps (1)-(2) relaunch shape: the
  census is a pure offline RAM read.

## S1. ADDRESS ALGEBRA USED (all verbatim from pinned laws, cross-checked)
- data physical base DB = B - 0x88 + 0x82bb0 = P0 + 0x82bb0 (P0 = B - H, H=136).
  Cross-check vs t307 S4 measured self-relocation delta 0x242000:
  0x1bf450 (t307 run P0) + 0x82bb0 = 0x242000 EXACT.
- wmgr base = data offset 0x12e10 (fn 0x232ec/0x238e8/0x2351c arg, t323 S2);
  window records stride 0x1ee at base+0x8 (fn 0x232ec BYTE [base+0x8]=dl then
  per-record [rec+0x8]) — consistent with r284_deref RACE_X=0x12e16 stride
  0x1ee in the same data space.
- registry: count at [base+0x3333] (high half), entries stride 0x27 at
  [base+0x3337] (fn 0x2351c loop 0x23619..0x2361f, t323 S2).
- name immediates are POOL-RELATIVE = data offsets (t323 S2: imm 0x2bf7 =
  "BatModeWnd", 0x2c02 = "COSMOSWnd", 0x2c0c = "RESWIN", 0x2c13 =
  "RACECONTROLS"; full absolute addresses never appear in code).
- class table = [rec+0xa7]; virtual repaint [[win+0xa7]+0xc], hide-call
  [[rec+0xa7]+0x8] (t323 S3/S3'). Converting a stored pointer p to a
  Ghidra/payload code offset: file_off = p - P0; to a data offset:
  p - (P0 + 0x82bb0).
- CORRECTION to the STATE.md task text: `[wmgr+0x3337] stride 0x27` is NOT
  the window-name registry. Reading [wmgr+0x3333]>>16 = count 50 and the
  50 entries at +0x3337 (stride 0x27, data payload offset 0x16147) reproduces
  the LANE POOL EXACTLY (r284_deref: LANE_X=0x16147 stride 0x27; entry dwords
  are star-record pointers 0x255xxx — entry[0] = 0x255bc5, 0x256825 = the
  Icarus star record). The fn 0x2351c pair-matrix/occupancy code at +0x3333/
  +0x3337 is a LANE-bookkeeping routine, not the BatModeWnd name registry the
  task assumed. So the census must anchor on the CLASS TABLE directly (the
  installer's target offset), which is what S2 does.

## S2. MEASURED — LIVE RAM CLASS TABLE AT THE BATMODEWND INSTALLER TARGET
Read surface = a production save's `Memory` ZIP member (pointer law: full
guest-RAM image). Zero guest boot, zero scratch copy, production :9 (pid 1957)
untouched. 10/10 saves 50..59.sav (t=1086 corpus, mtime Nov 6 20:28-20:29) give
IDENTICAL results.
- Base (save 54): B=0x1bf4d8, P0=B-0x88=0x1bf450, DB=P0+0x82bb0=0x242000,
  memlen=0x1044088. Data payload offset X -> member idx B+0x82bb0+X.
- MODEL VALIDATION (same-save internal cross-check): the Icarus star record
  pointer 0x256825 (a stored guest-physical u32) read at member idx 0x256825+0x88,
  +0x1c = b"Icarus\x00" — the pointer law / rebase math is confirmed on THIS
  save, so the table read below rests on validated address arithmetic.
- The BatModeWnd class table: fn 0x1ac21 (payload, the ONE installer that
  writes [rec+0xa7]=0x58e8; a full image census of all `[reg+0xa7]` stores —
  62 sites — shows 0x58e8 appears ONLY at 0x1ac21, the sibling window uses
  0x88498 @0x1abe6) points the table base at DATA payload offset 0x58e8.
  Reading live RAM at member idx B+0x82bb0+0x58e8 (phys DB+0x58e8=0x2478e8),
  6 dwords:
    RAM slots (guest-physical fn ptrs):
      0x1da04c 0x1f0158 0x1da348 0x1dcca8 0x1f0608 0x1dde2c
    minus P0 (-> Ghidra/code offsets):
      0x1abfc  0x30d08  0x1aef8  0x1d858  0x311b8  0x1e9dc   in-code 6/6
  = the CITED BATMODE table EXACTLY (t296/t323: [0x1abfc, 0x30d08, 0x1aef8,
  0x1d858, 0x311b8, 0x1e9dc]).
- fn 0x32100 (the [win+0xb1] state-rect click switcher): present in this
  table = FALSE. Also absent of the other flagged writers fn 0x31f30 /
  fn 0x339a4. Verified on all 10 saves (50..59), each with a live "Icarus"
  star-name cross-check.
- REBASE MODEL (clean): [rec+0xa7] holds a DATA payload offset (0x58e8) — NOT
  rebased (data offsets don't take +P0). Each table SLOT holds a runtime fn
  pointer = P0 + <static fn offset>. So live-RAM table slot k = P0 + cited[k],
  which is EXACTLY what was observed. The t307 self-relocation law (code
  immediates referencing DAT scalars rebased by +P0) does NOT apply to class-
  table bases or slot fn pointers the way I first feared — the table is a
  stable data-segment block whose slots are physical code pointers.

## S3. VERDICT + RESIDUAL (honest, strict-close)
VERDICT: The BatModeWnd class table, read from LIVE RAM at its sole
installer's target offset (data payload 0x58e8), reproduces the cited static
table BYTE-FOR-BYTE (6/6 slots = P0 + cited), and fn 0x32100 is ABSENT. The
t323 caveat (b) — "static class tables are RAM-relocated, so the cited table
is cited-but-indirect; re-open if a RAM census finds fn 0x32100 installed in
BatModeWnd's table" — is DISCHARGED on exactly the axis it named: the runtime
table is not drifted (it is P0 + static), and the flagged writer is not in it.
Every OQ-019 capture route is now cited-dead: t319/t320 pump (never posts
0xc), t322 mouse (BatModeWnd zero msgs in-view), t323 activation (census-
complete, no in-session trigger), t324 class-table (verified live, no 0x32100).
Per the task's own deliverable: slots MATCH cited law => the negative is
ABSOLUTE; the OQ-019 select/destination residue disposition is FINAL on every
capture axis. ROW STAYS OPEN per strict-close (no live store of the SELECT
widget was ever witnessed — the class-table negative is a cited-dead-route
closure, not a positive witness).

RESIDUAL (stated, NOT overclaimed): I verified the table via its UNIQUE
installer + the table at that installer's target offset. I did NOT physically
locate BatModeWnd's window RECORD and dump [rec+0xa7] from it, because the
record is not resident in the t=1086 campaign save: a scan for a stored u32
pointing at the "BatModeWnd" name pool (phys 0x244c7f, the in-data copy; the
code-side pool copy at data offset 0x82bb0+0x2bf7 = b"BatModeWnd" is present)
found NO resident record. Window records are allocated lazily on screen-open,
and t=1086 is a campaign/system-map state where BatModeWnd is never composed
in-view — consistent with t322's "composition-shielded BY DESIGN" finding
(BatModeWnd receives ZERO msgs in-view). This residual is the same wall the
row already sits against (the batcon UI screen is precisely the
UNREACHABLE-BY-CAPTURE class t323 established), so it does not reopen t323.
If a future session ever reaches a screen state with the BatModeWnd record
resident, a one-shot [rec+0xa7] dump is the belt-and-suspenders confirmation —
but reaching that state is itself the closed class.

## S4. NEXT
- Ledger: OQ-019 row — add the t324 class-table line (cited-dead route, row
  stays open per strict-close). No row CLOSED (no positive SELECT witness).
- STATE.md: NEXT ACTION -> the queue row after t324 = t325 (per-slot
  shield-byte witness), OR if t324's absolute negative unlocks t329 (OQ-019
  disposition packet, CONDITIONAL on t324 negative-absolute). Ordering: t329
  is now satisfiable (t324 landed NEGATIVE-ABSOLUTE), and it is the natural
  consequence of this iteration — name it NEXT with the rationale that it
  packages the row for the USER's ruling (D2/D1), while t325-t328 remain in
  queue. (t329 drafts only; it does not move the ledger.)
