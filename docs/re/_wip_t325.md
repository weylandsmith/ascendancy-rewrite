# _wip_t325 — PER-SLOT SHIELD-BYTE WRITNESS (OQ-016 residue 4)

Started 2026-11-07 (fresh session). Assignment = docs/STATE.md NEXT ACTION t325.

## S0 — SITTING CHECK (done first, per law)
`tail -c 400000 work/r1/playcap/live-timeline.jsonl` -> 16 parsed turn events,
turn min/max = 1086/1086. Newest turn == 1086 == the t319..t329 corpus: NO new
human play since the last iteration. `scripts/r1_t85g_sitting.py` NOT run
(justified: no new sitting). Production :9 (pid 1957) untouched.

## S1 — WHAT-IS-IN-HAND (carried, do not re-derive)
- Residue definition: docs/re/income-law.md T271 item 4 — per-slot shield byte
  (slot byte3) writes ARE reachable (item 18 Surface Shield 1519 obs, 26 Orbital
  Shield 2743, 27 Orbital Mega Shield 231 active; 19 Surface Mega Shield ZERO =
  chain-C never fired) but the CONSUMER is unmapped. Documented gap, NOT wired.
- Writer law (static, decompile-cited, income-law T39b): completion branch
  FUN_00038f68 — generic flag&8 items: `byte3 := 0` (@0x38fee) then
  `word2 |= (id==0x1b ? 0x23 : 0xf) << 8`. CAVEAT banked there: decompiler's
  pending-item byte sits at +0x15 while captures show pending id at record +0x54
  (runtime colony-block aliasing) — only RELATIONSHIPS claimed.
- Slot law: slot array at (stored ptr value) + 0x88 inside the Memory image
  (income-law T33, 72066/72066 corpus); slot = 4B {class, itemIdx(0xff empty),
  flags u8, shield u8} -> shield byte = slot base + 3.
- POINTER-VALUE LAW t298 (binding): RAM holds guest-PHYSICAL; BPLM target =
  member + 0x88.
- t324 note: census anchor = installer target data 0x58e8; [wmgr+0x3337] is the
  LANE POOL not a name registry; slots = P0+static.
- REFUTED / do NOT chase: item-35/36 completion witnesses (t271 zero-witness,
  AI-unreachable); corpus mining of flight class; blind sweeps (R2).

## S2 — INSTRUMENT STATE (recon)
- Ghidra headless 127.0.0.1:8089 health `{"status":"healthy",...,"program_loaded":
  false}` — must load work/ascend_restored.bin before static queries.
- Debugger build: work/r1/dbx-build/dosbox-x-master/src/dosbox-x (copy to
  work/r1/bin/dosbox-x-dbg if absent). Laws: FirePat stop-line = unique PATTERN
  (t305); MEMREAD real-mode-only (debug.cpp:2983) so the ring is the read
  surface; xsend arg1 = WINDOW TITLE (t290); resume-with-fired-BP re-freezes
  (t302 bug 2); first-BP-fire 0x00-init artifact check.

## S3 — PHASE A MEASUREMENT (offline, production ring newest slot 52.sav, t1086)
scripts/r325_shield_scan.py (reuses r1_income_law find_records/slot law verbatim).
Base B=0x1bf4d8 (matches t286 deterministic base). Item table names_ok green;
items 18/19/26/27 ALL flags=0x0008 (flag&8) at runtime.
1. 74 ACTIVE shield slots, ALL owner 0 (player). DIFFERENTIAL LAW MEASURED:
   item 26 Orbital Shield slots: word2=0x0f01 byte3=15 (0x0f) — matches T39b
   `word2 |= 0xf<<8` verbatim. item 18 Surface Shield slots (dozens, every
   planet): word2=0x0001 byte3=0 — CONTRADICTS a universal T39b reading:
   surface shields carry byte3=0. No 19/27 active in this state.
   => byte3 is orbital/ability-correlated (cf. T57: p3 in {7,8} written only for
   flag&4 ability items), NOT a universal shield-charge byte. [inferred from the
   two-population measurement above]
2. PENDING BUILDS: 92 pending; ONE is a shield: Gridsor I item=26 acc=30, and
   ITS RESERVED SLOT exists: Gridsor I idx=76 class=1 item=26 word2=0x0000
   byte3=0 (t271 reservation law verbatim, word2 bit0 CLEAR). Slot byte3
   member-addr 0x25EB7C == the arr+4*i+3 arithmetic of find_records (arr indexes
   the Memory member directly, so that value IS the BPLM operand class t286b
   used, no further conversion -- verify live before believing).
3. RESUME.GAM.user-oct29 is RAW VENDOR SAVE (file=data, 87663 B), NOT a zip --
   analyzers cannot read it; scratch-session state must be inspected via the
   session's OWN ring dir. (Banked so nobody re-tries the zip read.)

## S4 — PHASE A2 (scripts/r325b_oct29_check.py) + RUN DESIGN
1. SAVE-AXIS CORROBORATION (t215 law): newest production ring slots all turn
   1086 (46/47/47.sav + re-check 48.sav @00:47). Production (pid 136359,
   work/r1/vnc/session.conf, TL 172800) IDLE — autosaves fresh, turn frozen.
   Sitting check FINAL: no new play; r1_t85g_sitting.py not run.
2. OCT29 RAW VENDOR SAVE WALK (145/145 records, 123-stride): the scratch-boot
   campaign (RESUME.GAM.user-oct29, md5 OK) HAS A PENDING SHIELD BUILD:
   Gridsor I item=26 acc=30. Same pending visible in production ring52 RAM
   (item 26 acc=30) WITH ITS RESERVED SLOT: slot 76 raw=011a0000 (class=1,
   byte1=0x1a=26, word2=0x0000 bit0 CLEAR, byte3=0) — t271 law verbatim.
3. ITEM ROWS (runtime RAM): 18 Surface Shield cost=100 ind=0; 19 Mega cost=180;
   26 Orbital Shield cost=60 ind=0; 27 Orbital Mega cost=120; ALL flags=0x0008.
   Build law acc += stored IND (record word+0x44 = 6 for Gridsor I) ->
   completion at acc>=60 = 5 NEXTTURN clicks after load (cadence law: each map
   click +1 turn). Fire expected t1091.
4. HEAP ADDRESS LAW FOR THE ARM: production ring52 Gridsor I arr(member)=
   0x25ea49 -> slot76 byte3 member 0x25EB7C -> BPLM LINEAR = member - 0x88 =
   0x25EAF4 (t286b off-by-H law; my r325_shield_scan.py "BPLM=" printout was
   UN-CONVERTED member index — corrected here, script prints member idx as
   evidence only). Vendor-file ptr (oct29 Gridsor I +0x10 = 0x25EA61) DIFFERS
   from live-RAM ptr (0x25e9c1): loader re-allocates heap on resume, stored
   pointer values are dead addresses — scratch session MUST resolve its own
   arr from its OWN ring post-entry (verify slot76 == 011a0000 before arming).
5. RUN DESIGN (scratch debugger session, one): boot game-wp from oct29 ->
   ENTER (Return to Current Game 318,333) -> ring resolve arr -> verify
   reserved pattern -> BREAK (lottery loop) -> BPLM 0x(arr+0x133-0x88) -> RUN
   -> NEXTTURN clicks (window-rel 511,67) -> fire watch. Baseline 0 at arm =>
   NO artifact rejection (t286b law: first fire IS first write). Bank per-fire
   EIP+value, then RUN again (max 3 fires). After-phase ring diff of slot 76
   gives the completion VALUE law. Writer identification = last storing insn
   before reported EIP touching the offset (t286 law 7), mapped through
   work/ascend_restored.bin (VA==file offset) + functions_full.tsv.

## S5 — ATTEMPT 1 (run work/r1/t325-shield-20261107-005947): NEGATIVE, TWO CAUSES
scripts/r325_shield_session.py. GOOD: scratch boot clean; ENTER reacted; target
resolved from the session's OWN ring (Gridsor I pending 26 acc=30 slot76
raw=011a0000, member 0x25eb7c — IDENTICAL member addr to production ring52,
so the scratch heap layout matches at B=0x1bf4d8); BREAK survived attempt 0;
BPLM 0025EAF4 armed 1/1 (byte-at-arm MEMDUMPBIN failed -> val None -> no
artifact rejection). Turn advanced 1086->1087 early.
CAUSE 1 (mine, harness): I sent SIGTERM to the scratch dosbox mid-battery
(thinking it hung) — per law SIGTERM pops the quit-confirm with (Yes) DEFAULT.
The confirm swallowed every later click. Retract: NEVER SIGTERM; teardown is
SIGKILL by recorded PID (the script does it correctly).
CAUSE 2 (game): a CONSTRUCTION-COMPLETE popup ("Industrial Megafacility ...
Corncob I", t1087) was modal from ~01:04 onward; per selfplay.md:329 Escape
does NOT close it, only the OK click does. My battery never clicked OK, so
turn froze at 1087 for the remaining ~13 min (only 1 of ~45 clicks counted).
Zero fires is therefore NOT evidence about the shield byte: the completion
turn (~t1092 = acc 30 + 6*5) was never reached. Attempt 1 = instrument bug
class (t306-t323 lineage), not a law.
ATTEMPT 2 FIXES: (a) popup-drain loop BEFORE + DURING the battery: grab
screen, detect white-dialog band (y 250-350 white-span > 400 px, measured
fingerprint this session), click the game popup OK (locate per t261 drive laws
or vision), re-verify by turn advance; (b) NEVER SIGTERM; (c) click cadence
8 s; (d) budget to t>=1093.

## S6 — ATTEMPT 2 (run t325-shield-20261107-013015): BREAK LOTTERY DEATH
Target resolved perfectly again (member 0x25eb7c IDENTICAL across independent
sessions — deterministic heap re-confirmed 2/2); post-entry drain found no
popup; BREAK#0 hdr=None + no PONG = the lethal-BREAK class (t286 law 2,
~50%/attempt). Script exits 1 without retry — needs the r322-style relaunch
wrapper. ATTEMPT 3 = third and last launch of the 3-launch budget.
Static banked while waiting: writer-site disasm VERBATIM (objdump on
work/ascend_restored.bin, VA==file):
  0x38fe2 call 0x39b6c (out-params @esp+0x28/0x2c/0x30)
  0x38fe7 cmpl $0x0,0x28(%esp) / 0x38fec je 0x38f95   (p3==0 -> NO write)
  0x38fee movb $0x0,0x3(%edi)                          (byte3 := 0)
  0x38ffa shl $0x8,%eax; 0x38ffd or %eax,%edx;
  0x38fff mov %dx,0x2(%edi)                            (word2 |= p3<<8)
  0x39003 jmp 0x38f95
If the fire EIP maps near these (fire = first access AFTER the store, t286
law 7; writer = last storing insn before EIP touching +3), the writer law is
CLOSED live. item 26 p3 expected 7 or 8 (T57: p3 in {7,8} for flag&4 ability
items; 26 is NOT in the T57 enumerated table -> p3 value for 26 is itself a
NEW measurement; the byte3=0x0f corpus reading suggests p3=0x0f for 26).

## S7 — ATTEMPT 3 (run t325-shield-20261107-013553): EARLY-ARM SHAPE VALIDATED, DRAIN BUG KILLED IT
GOOD (all banked as instrument law): title BREAK#0 survived (3/3 class per
t282); BPLM 0025EAF4 armed at TITLE, SURVIVED campaign load with ZERO
boot/load fires (blind-free-heap baseline 0 confirmed live — the exact t286b
law); target re-resolved from session ring: member 0x25eb7c IDENTICAL 3/3
sessions (deterministic heap law now 3 independent confirmations + production);
turn advanced 1086->1087 with bp armed.
BUGS (mine, instrument class):
 (a) popup_ok_center parsed `convert img rgb:-` as PPM — rgb: output is
     HEADERLESS raw RGB, so the header parse always failed -> detector blind
     (returned None forever; "popup drain closed 0" while a Corncob I popup
     was MODAL on screen). Fixed: ppm:- (has P6 header) + re.match.
 (b) COORDINATE LAW RE-VERIFIED THE HARD WAY: content bbox of the Xvfb root
     grab == (80,100)-(716,576) — the dosbox window origin is (80,100) HERE
     TOO (same as t245 production). Detector works in ROOT px; xsend takes
     WINDOW-REL. My drain sent root coords as window-rel (would have clicked
     80,100 off-target even with a working detector). Fixed: subtract (80,100).
 MEASURED POPUP GEOMETRY (drain_0.png, root px): white text rows 350..454;
 bottom label-row groups [(217,226),(235,279),(402,414)] -> OK label center
 root (408,442); hit y = label-top-3 = 442 -> window-rel click (328,342).
 BUDGET ACCOUNTING (honest): 3 launches spent, ZERO reached the completion
 phase (t293 accounting: only runs reaching build/launch count; none witnessed
 the shield turn). Attempts 2/3 died to documented instrument classes (BREAK
 lottery; my two drain bugs). ONE more launch with the fully-fixed chain, then
 HARD STOP regardless: negative if no fire.
 CONTEXT INCIDENT: piping `convert ... rgb:-` into python without slicing
 dumped ~1 MB of raw bytes into my context. Never echo raw pixel streams.

## S8 — ATTEMPT 4 + HARD STOP: t325 ENDS NEGATIVE (OQ-016 residue 4 stays open)
ATTEMPT 4 (run t325-shield-20261107-015339): died instantly — TITLE BREAK#0
hdr=None frame_ok=False = channel dead (BREAK lottery again, t286 law 2 class).
Instrument chain was fully fixed by then (detector verified offline against the
real attempt-3 popup: popup_ok_center(drain_0.png) -> (406,442), expected
(408,442)); the loss was pure debugger-channel luck, no new law.
FINAL BUDGET ACCOUNT (t293 accounting: only runs reaching the witnessed phase
count): 4 launches, ZERO reached the shield-completion turn.
 - att1: click battery without popup drain (drain not yet written) — stale shape
 - att2: BREAK lottery death at title
 - att3: my two instrument bugs (rgb:- headerless parse; root-vs-window-rel
   coords) -> drain clicked nothing while Corncob I popup was MODAL
 - att4: BREAK lottery death at title (0 s)
WITNESS VERDICT: NO FIRE OBSERVED on the shield build. This is an ABSENCE-ONLY
negative — it does NOT prove the writer doesn't touch slot byte +3; it proves
only that the t325 instrument chain (BPLM at record-slot stride-4, early-arm
shape) failed to capture it in 4 launches, 2 of them killed by documented
luck-classes. Row stays OPEN per strict-close.
PRODUCTION CENSUS (measured this session, ring52.sav, B=0x1bf4d8, turn 1086 —
the ONE ledger-relevant measurement t325 produced):
 item 18 word2=0x1  byte3=0  : 30 slots
 item 26 word2=0x0  byte3=0  :  1 slot   (the Gridsor I PENDING row)
 item 26 word2=0xf01 byte3=15 : 43 slots
 => across ALL 74 shield-item slots in production, byte +3 is NEVER a shield
 progress counter: it is 0 on pending rows and 15 (0xf) on completed rows.
 [inferred from the above] the per-slot shield progress law, if it exists,
 lives OUTSIDE slot dword +3 — the t325 assignment premise (witness byte +3
 as progress) is contradicted by census for every slot EXCEPT the pending one,
 where +3==0 across 44 pending-class observations. NEXT witness design must
 watch the whole slot dword (or the build-queue struct), not byte +3.
DETERMINISTIC-HEAP LAW (3/3 + production): scratch session member address
0x25eb7c resolved IDENTICALLY in attempts 1/2/3 and BPLM armed at TITLE
survived campaign load with ZERO boot fires (blind-free-heap baseline 0, t286b
law re-confirmed live). This is the reusable asset t327 should bake.
INSTRUMENT ASSETS (fixed, committed): scripts/r325_shield_session.py carries
the corrected drain (ppm:- P6 parse; root->window-rel (80,100) subtract;
verified), early-arm-at-title shape, fire-drain in the resolve loop.
PRODUCTION UNTOUCHED: post-run ps == Xvfb :9 (pid 1461) + production dosbox-x
(pid 136359) only; ring52 still turn 1086.
