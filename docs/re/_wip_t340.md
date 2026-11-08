# _wip_t340 — OQ-016 residue-(4) FINAL shield-completion witness (ONE launch)

## S0 — Task + sitting check (2026-11-08)
- STATE.md NEXT ACTION t340 verbatim: at the shield build-completion turn
  (Gridsor I pending item 26, acc=30 @ t1086, +6/turn, COST 60 runtime =>
  completion ~t1091-1092), does ANY observable dword move per turn in the item
  slot / build-queue struct. Watch WHOLE slot dword + build-queue acc, NOT
  byte+3 (t325 census law: byte+3 == 0 on all 44 pending rows, constant 15 on
  43 completed rows). Budget: ONE launch, t>=1093. Zero movers => ABSENCE-ONLY
  third time, residue stays instrumentation-class-open, capture queue EMPTY.
- Sitting check NEGATIVE: tail-scan work/r1/playcap/live-timeline.jsonl newest
  "turn": 1086 (126 identical entries in 3 MB tail). No re-sit needed.
- Production :9 alive (dosbox-x pids 136357/136359, Xvfb 1461) — NEVER
  signalled this iteration.

## S1 — WHY t325's four launches never reached completion (root cause, offline)
- work/r1/t325-shield-20261107-013553 stalled at turn 1087: log says
  "popup drain closed 0" while drain_0.png (mtime 01:38:15, the drain call
  frame) CLEARLY holds a modal popup. vision_analyze ID: "Construction of
  Industrial MegaFacility is complete on Corncob I. / Corncob I has 1 free
  population for additional projects." with buttons Go^to^Planet + OK, OK
  label centred ~(408,447) root px.
- ROOT CAUSE: the runs executed at 01:35-01:38 used the PRE-FIX in-process
  detector (rgb:- headerless parse); the fix (ppm P6 + (80,100) origin
  conversion) was committed at 02:13 AFTER the runs ("offline-verified vs real
  popup" in commit 26b278d). RE-VERIFIED this session against the committed
  on-disk code: r325.popup_ok_center('drain_0.png') -> (406, 442) NOT None
  (same on screen_stop_and_look.png + screen_after_battery.png of run 005947).
  White-row census of drain_0.png y330..470 x170..486: rows 353-359, 392-398,
  445-454, total 1705 white px >= 120 gate. => the committed chain CAN drain
  this popup class; the t325 stall was the instrument, not the game.
- CONSEQUENCE: t340 runs the committed fixed chain verbatim; completion is
  reachable. No new drain logic needed, only the watch-target change
  (ring-diff whole slot dword + acc per turn) and a longer budget.

## S2 — Method (launch design, one shot)
- scripts/r340_shield_complete_session.py imports r325 helpers verbatim
  (drain_popups/popup_ok_center/latest_ring/read_turn/find_target + constants
  TARGET_PLANET=Gridsor I, PENDING_ITEM=26, SLOT_IDX=76,
  RESERVED=011a0000, EARLY_LIN=0x25EAF4 / member 0x25eb7c deterministic heap).
- Chain verbatim: own scratch game-wp + own ring dir, Xvfb :97, MCP out-conn,
  BREAK lottery x3 at title, MEMDUMPBIN byte-at-arm, BPLM 0x25EAF4 (byte+3 —
  a FIRE is now a bonus witness: word2 0xf01 write covers byte+3), BPLIST,
  RUN, RETURN-TO-GAME (318,333), fixed drain, ring resolve (pending item 26 +
  reserved pattern verified before trusting addresses).
- NEW observation channel: every ~15 s ring sample appended to turns.jsonl —
  turn, acc word (base+0x50), pending item (base+0x54), cap, ALL cap slot
  dwords hex (83 dwords). Completion witness = slot76 raw != 011a0000 or
  pending item != 26, with the turn number + acc at that sample and the prior
  sample (per-turn diff = the value law).
- Battery to turn >= 1093 (or 2400 s), NEXTTURN (511,67) every 10 s, popup
  drain on 2-consecutive no-advance (t245 serialization law), fire handling
  = bank regs/EIP/dump_stopped then BPDEL * + RUN (t325 shape).
- Teardown SIGKILL by recorded pids (t286 signal law); production ps-verified
  untouched post-run. Exit 0 = completion turn witnessed (ring-diff mover
  found or BPLM fire), 1 = negative, 2 = harness error.
- LAUNCHED work/r1/t340-shieldc-20261108-013812 (bg proc_3954715cdd4f):
  BREAK#0 stopped first try, byte-at-arm read, BPLM 0025EAF4 armed (00),
  EARLY RUN, RETURN-TO-GAME click, ENTER at +49 s, ZERO boot/load fires —
  t325's fixed chain reproducing exactly. Stale :97 lock from t338's dead Xvfb
  cleared pre-launch (xdpyinfo :97 failed while lock existed = Xvfb was dead,
  not alive: always xdpyinfo-check before reusing a display number).
- LAUNCH 1 (…013812, renamed .harnessbug1) DIED pre-battery: NameError
  W_ANCH — r325.latest_ring() reads r325's MODULE-GLOBAL W_ANCH; my wrapper
  set its own global. Harness bug (exit-2 class): fixed by assigning
  T325.W_ANCH. Not a scientific negative; the ring never got sampled.
  (Side observation from pty: MEMDUMPBIN 0000:LINEAR len 1 -> "Invalid memory
  dump arguments" — the byte-at-arm read never worked in t325 either;
  expect_artifact stayed False there too. BPLM arm itself was fine.)
- LAUNCH 2 (…014705, bg proc_02571d6f8da0) LIVE: BREAK#0 first try, armed
  0025EAF4, ENTER +49 s, resolve OK, battery clicking; 01:50:09 ring turn
  1088 acc=42 item=26 slot76=0x1a01 — acc law +6/turn reproducing (30@1086,
  36@1087, 42@1088); popup drain CLOSED 6+1 popups where t325 closed 0 —
  S1 root-cause confirmed live: the same popup class that stalled t325 is
  being cleared by the committed detector. Completion predicted acc>=60 @
  t1091; deadline t1093.

## S3 — MEASURED COMPLETION LAW (launch 2 rc=0, 413 s, turns 1086..1093)
Per-turn whole-array diff (83 dwords re-resolved from the ring every 15 s,
work/r1/t340-shieldc-20261108-014705/turns.jsonl, first-sample-per-turn):
    t1086 acc=30 item=26 slot76=0x00001a01  diffs vs prev: []
    t1087 acc=36 item=26 slot76=0x00001a01  diffs: []
    t1088 acc=42 ...                         diffs: []
    t1089 acc=48 ...                         diffs: []
    t1090 acc=54 ...                         diffs: []
    t1091 acc= 0 item= 0 slot76=0x0f011a01  diffs: [43, 76]  <- COMPLETION
    t1092 acc= 6 item= 0 slot76=0x0f011a01  diffs: []
    t1093 acc=12 item= 0 slot76=0x0f011a01  diffs: []
(1) THE LAW: while pending, the ONLY per-turn mover in the whole 83-dword
    slot array is the build-queue ACC word (base+0x50) += planet stored IND
    (base+0x44 = 6); slot dwords frozen. At the completion turn boundary
    (acc 54+6=60 >= COST 60, t274 law 0x390a3) EXACTLY THREE things move:
    slot76 dword 0x00001a01 -> 0x0f011a01 (byte2 0->01 BUILT, byte3 0->0x0F
    =15 COMPLETED marker — t325 census law now explained: 15 is a completion
    MARKER, written once, never a counter); acc := 0 (restarts +6/turn);
    pending item word (base+0x54) := 0 (queue empty, t271 word2-bit0 law).
(2) WRITER WITNESSED: BPLM 0x25EAF4 fired EXACTLY ONCE (00->0F) at
    EIP linear 0x1f86e0 -> payload file offset 0x1f86e0-(B-H)=0x1f86e0-
    0x1bf450 = 0x39290 — inside the same build-queue function family as the
    banked acc law sites 0x39005/0x390a3. Fire regs: eax=4c ebx=25e9c1
    ecx=1a3c edx=f00 esi=270c66 edi=0 ebp=254e10 esp=2e89d4. (MEMDUMPBIN
    code/stack dumps failed 'Invalid memory dump arguments' — the
    seg:off form rejects 8-hex linear here; regs banked via EV are the
    witness.)
(3) slot43 byte1 0xff->0x00 at the same boundary (empty cell -> byte1=0) —
    secondary mover, decode pending vs planitem.txt + fn at 0x39290.
(4) Popups: 23 OK-clicks across 7 drain calls (4/6/1/4/4/3/1) where t325
    closed 0 — the S1 instrument verdict
    confirmed live; t325's four zero-fire launches were NEVER the game.
Teardown SIGKILL recorded (dosbox 208428, Xvfb 208424 — from the bg stdout
transcript; kill_rec does not write session.log. 208042/208038 were
launch-1's pids). Exit rc=0.

## S4 — WRITER SITE + STATIC CROSS-CHECK (scripts/r340_writer_site.py exit 0)
- Fire EIP linear 0x1f86e0 -> file 0x39290; containing function span
  0x38f68..0x394d8 (functions_full.tsv) = FUN_00038f68, THE build-queue
  function (acc law 0x39005/0x3907b, completion check 0x390a3 all inside).
- Fire regs esi=0x270c66 = Gridsor I record linear VERIFIED (ring-final
  physical 0x270cee - 0x88). eax(slot idx from +0x52)=76, ebx=[esi+0x10]
  array, edx=0xf00.
- The writing instruction (work/r331_disasm.txt): 0x3928b
  `or WORD PTR [ebx+eax*4+0x2],dx` (word2 |= 0x0f00: byte2 0->01 built,
  byte3 0->0x0f=15 marker), preceded by 0x3925b `mov edx,0xf` / 0x39263
  `cmp ch,0x1b / jne` / 0x39265 `mov edx,0x23` (item 27 special: word2 |=
  0x2300 — static, unverified live); gate into the block: FLAG-table word
  bit 0x8 (`mov ax,[eax*8+0x73e46]; and al,8; je 0x39290`) and slot>=cells
  (`mov ax,[esi+0x52]; cmp ax,[esi+0x18]; jb 0x39290`; 76>=73 ORBITAL ✓).
  0x3927f `mov BYTE PTR [ebx+eax+3],0x0` also touches byte3 but writes 0
  over 0 (silent, no BPLM fire — consistent with EXACTLY ONE fire 00->0F).
- Immediately after (0x39290..0x3929a, the fire-EIP instruction itself):
  +0x52 := 0xffff, +0x54(byte) := 0xff, +0x50 acc := 0, jmp 0x392f4.
- RE-QUEUE MOVER (slot43): at the SAME boundary slot43 byte1 0xff->0x00 and
  ring-final shows +0x52=43, +0x54=0 (item 0 FACTORY), acc resumed +6/turn
  (t1092 6, t1093 12) — a Factory build was queued into empty slot 43 right
  after completion on this owner-INDEX-0 planet. WHO queues it is NOT
  decoded (selector caller law 0x3ead6 is queue-empty-only, consistent; but
  the human-planet auto-queue path is unconfirmed) — named observation, kept
  out of the closure claim.
- MEMDUMPBIN pitfall: `MEMDUMPBIN 0000:<8hex-linear> len file` ->
  "Invalid memory dump arguments" (t325's byte-at-arm and my code/stack
  dumps all failed; regs via EXEC EV work fine). BPLM/BPLIST/BPDEL/RUN/EV
  unaffected.
## S5 — VERDICT (strict-close)
residue-(4) "per-slot shield-byte consumer" CLOSED with cited measurement:
the consumer is the completion handler 0x3928b (FUN_00038f68) writing word2
|= 0x0f01 ONCE at the completion turn (bit0 built-active + byte3=15 done
marker); while pending, NO slot byte moves at all — the sole per-turn mover
in the whole 83-dword array is the acc word += stored IND (existing cited
law). t325's census (byte+3==0 pending / ==15 completed) is now EXPLAINED,
its counter-premise confirmed dead. Rewrite: buildPhase (campaign.cpp:1012)
already models acc+=IND, completion at acc>=COST, acc reset — t340 CONFIRMS
it live; comment updated to cite 0x3928b/0x39290 + this witness (no code
delta: the rewrite has no word2 slot-state model and none is required).
OQ-016 ROW STAYS OPEN (residues 1 and 5 unaddressed).
