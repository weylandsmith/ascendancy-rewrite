# t305 WIP — NORMAL-CORE STOP ANOMALY: RESOLVED AS INSTRUMENT DEFECT (fire-pattern 5-hex truncation law)

## S0. Headline (cited, this session)
THE t304 "NEW ANOMALY" (normal core banks ZERO stops even for cos_hdlr) IS AN
INSTRUMENT DEFECT, NOT A GAME LAW. Under the fixed conf the breakpoints DO
stop the guest; only the pty fire-detection pattern failed to see them.

Evidence (run work/r1/t299-leg-20261105-052925/mcp-pty.log, legs
[s2_56cda=0160:0021612A, cos_hdlr=0160:001E5F84], witness0 armed RUN = REQ 14):

  off 17104 (arm echo / MEMDUMPBIN lines) — full form `21612A` appears ONLY in
    REQ echoes: "EXEC BP 0160:0021612A", "Set breakpoint at 0160:21612A",
    "01. BP 0160:21612A", "EXEC MEMDUMPBIN 0160:0021612A ...".
  off 17311, immediately after "REQ 14 EXEC RUN": the code view re-renders
    highlighted (ANSI \x1b[30m\x1b[42m on the first line = stop highlight):
      `1612A FF5608`  `call near dword [esi+0008]`
      `1612D 5F`      `pop edi`   `1612E 5E` `pop esi`
      `1612F C20400`  `ret 0004`  `16132 8BC0` `mov eax,eax-src` `16134 56` `push esi`
    then the prompt returns: `I-> _` and the data view shows
    `00FD2310 47A4C` / `00003B` / `1612A C0 Z0 S0 O0 A1` (stop-EIP line) /
    `002BC35C` / `0000003B` — a STOP AT THE LEG, guest halted.
  Same render in windows 1 and 2 (offs 20397, 23439) = 3/3 armed windows fired
  s2_56cda. cos_hdlr never got a turn (one stop per window, script never
  resumed mid-window).
  Corroboration: save/ cadence 41..50 every 10 s 05:29:37-05:31:07, then GAP
  50.sav 05:31:07 -> 51.sav 05:32:15 exactly spanning armed window
  05:31:14-05:32:14 (guest frozen at the BP; autosave is in-guest), then
  52.sav 05:32:25 after DISARM-RUN. Same pattern windows 2/3.
  Control runs: 051904 fired identically (off 22901 `1612A FF5608`).

## S1. THE RENDERING LAW (normal core vs dyn core)
- t302 law (dyn core, DrawCode): fire line `1E5F84 56 push esi...` = 6-hex EIP,
  opcode glued, run-on. Pattern `(?<![0-9A-Fa-f])<6hex> [0-9A-F]`.
- t305 law (NORMAL core): the code view is a CURSOR-POSITIONED ANSI screen
  (ESC[<row>;<col>H moves), addresses are rendered TRUNCATED TO 5 HEX DIGITS
  (low 20 bits): 0x20EF05 -> `0EF05`, 0x21612A -> `1612A`, 0x2284F5 -> `284F5`
  (all three verified verbatim in the two run logs). The 6-hex leg string NEVER
  appears in a normal-core stop render -> the t302 pattern structurally cannot
  match. Address+opcode ARE space-separated here (`1612A FF5608`), opcode and
  mnemonic are separated by a cursor-move, not a space.
- Collision safety of a last-5-hex fire pattern: leg+-0x100000 would be
  0x11612A (below code base 0x1d4000) or 0x31612A (above image end ~0x2e9114,
  segment line in the same pty) — neither is in the executed payload window
  (pointer-law code window [0x14bb0,0x82bb0)@0x1d4000 = runtime
  [0x1d4000,0x242000)). LAST-5 IS SAFE for every leg in the window.
- SECOND, RENDER-INDEPENDENT detector already in the script: the `I-> ` prompt
  reappearing after a `(Running)` render = the debugger is stopped; attribute
  via EXEC EV eip (bank_stop does this). Prefer prompt-detect + EV attribution
  as ground truth, 5-hex code-view grep as secondary.

## S2. Consequences (re-reads of prior logs)
- t304 (4) "normal core banked ZERO stops" = DEAD READING. Normal core works;
  the 22 slot-2 site legs CAN be witnessed there.
- t303's dyn-core site-zero-fires stay re-attributed as core artifact (t304
  amendment (2) stands — dynrec mid-block BPs cannot stop).
- The census runs' "0 stops banked" lines in 051904/052925 session.logs were
  stops happening unbanked; liveness=True after DISARM was consistent because
  the guest resumed fine.

## S3. Instrument patch (this session, applied)
scripts/r299_leg_session.py: NEW module-level `fire_pats(lin)` returns BOTH
patterns (t302 6-hex dyn-core DrawCode form + t305 5-hex normal-core form).
Used at all three detection sites: arm_all (leg_pats.extend), witness pty
census, census pty census. The two forms are mutually exclusive per render
(each lookbehind kills the other's longer hex run), so summing findalls never
double-counts one fire. REGRESSION-TESTED vs real logs this session:
  run 033648 (dyn core, 41 known stops): 6-hex finds 41, 5-hex finds 0.
  run 052925 (normal core, 3 known stops): 5-hex finds 3, 6-hex finds 0.
  run 051904 (normal core, 1 known stop):  5-hex finds 1, 6-hex finds 0.
COLLISION AUDIT on the 24-leg census set: no two legs share a 5-hex form; four
near-pairs (0x1d..0x3a apart) exist but fire-detect needs addr+SPACE+opcode
byte, and the code view renders one instruction per screen line — a fire line
is unambiguous. Attribution was never the grep: bank_stop names the leg by
exact EV-eip (attribute()).
RUN: scripts/r305_relaunch.sh (--witness 3 --census --window 60, out
work/r1/t305/) — witness phase re-confirms ret0=0x21612d under normal core;
census phase = the OQ-019 selection-writer probe with the FIXED detector.

## S4. RUN RESULT — work/r1/t299-leg-20261105-061825 (rc=0, attempt 2)
WITNESS PHASE (cos_hdlr only, normal core): 3/3 windows banked, EVERY stop
ret0=0x21612d -> file 0x56cdd (call site 0x56cda) — t304 caller law
re-confirmed under the CORRECT core, and the fixed detector banked stops the
t304 instrument could not see. (ret0file=None on the census stops below is the
ESP-at-slot-2-site shape: at a call-site BP the return addr is still ahead —
[esp] holds the pushed arg, not ret0. Not a defect, expected at site legs.)

PER-WINDOW PER-LEG FIRE CENSUS (whole-log, corrected FirePat attribution;
banked stops in parens = msg edx + window-record NAME):
  baseline (no click)  : s2_56cda 15, cos_hdlr 15        (0x3b COSMOSWnd)
  sprite (48,151)      : s2_56cda 2, btn_hdlr 1          (0x8 PLIND)
  planet (439,331)     : s2_56cda 1                      (0x8 PLANETALLOC)
  empty  (236,200)     : s2_56c74 1                      (NOT banked — see S5)
  control NEXTTURN     : s2_56cda 2, btn_hdlr 1          (0x8 PLSQUARE)
  all 20 other s2_* sites: 0 fires in every window.
READS: (1) the periodic pump = 0x56cda (15/60s, msg 0x3b COSMOSWnd); clicks
add msg 0x8 to the CLICKED/repainted window record via the SAME pump site
(PLIND/PLANETALLOC/PLSQUARE), btn_hdlr fires once for sprite and nextturn.
(2) THE EMPTY CLICK IS THE ONLY TARGET THAT USES A DIFFERENT SITE: s2_56c74
(file 0x56c74, `ff 55 08 call [ebp+8]`) — matches t304's planet/empty 'Cancel'
-via-0x56c74 observation, now under correct core. (3) NO slot-2 site besides
56cda/56c74 fires for ANY click — 20 sites cited zero.
OQ-019 STATUS: the selection WRITER (who sets DAT_000482fb/sel) is STILL not
named — msg 0x8 at window records is the repaint/dispatch datum, not the
selection store. Row stays OPEN (strict-close). Datum banked toward it:
click->msg-id map {sprite 0x8 PLIND + btn_hdlr, planet 0x8 PLANETALLOC,
empty ->0x56c74 site, nextturn 0x8 PLSQUARE + btn_hdlr}.

## S5. SECOND INSTRUMENT BUG FOUND AND KILLED (same session)
The first-pass t305 patch (fixed 5-hex pattern) MISSED the empty-click fire:
DrawCode/ncurses emits only CHANGED CELLS, so the address token length varies
with prior screen contents — '60C4' (4 chars) rendered where my pattern wanted
'160C4'. Fixed by SOURCE LAW: PAIR_BLACK_GREEN HL_STOP prefix is exclusive to
the stop line (debug.cpp:1586-87); FirePat captures the HL token and code-
checks sig6.endswith(token), token len>=4 (last-4 unique across all 35 legs +
24-leg census set, audited); bare t302 form kept as no-color fallback with
HL-proximity exclusion. REGRESSION (exact): 033648 cos_hdlr 41, 052925 s2_56cda
3, 061825 cos_hdlr 60 / s2_56cda 20 / s2_56c74 1 — all five match known truth.
Consequence: the S4 census above is the CORRECTED attribution of run 061825
(the run's own session.log census line used the first-pass pattern and shows
s2_56c74:0 — superseded). Future runs use FirePat natively.

