# t273 WIP — LONG DRIVE WITNESS HARVEST II (2026-11-02, session 16:24Z -> )

Assigned: STATE NEXT ACTION t273. Legs (a) multi-volley vs NON-at-war owner
(OQ-016), (b) V>=25 threshold watch (OQ-021), (c) magnetron USE frames (OQ-019).
Writer-EIP leg VOID (t272).

## S1 — INTAKE / PRE-FLIGHT (measured)
- Production :9 LIVE at intake: dosbox-x pid 576895 (launch Nov 2 10:07:00,
  TL=172800 -> expiry Nov 4 10:07), single watcher pid 576910 (t267 law OK).
- Ring at intake: turn 1086 all slots, T=50, V=0, sel=0, rank=65535,
  n=4 ['Chamachies','Orfa','Ungooma','Minions'], sa=26/sf=25/pm=26, ships=30.
- No new user sitting (tail rows all 1086 through 11:30:26 EST); RESUME.GAM
  md5 5b382afbb789186c3654f3cec085b2e2 (mtime Oct 29 13:20) == STATE value.
- PRE-DRIVE BANK: work/r1/bank-t273-predrive/ (20 slots, cp -p, ~11:33 EST).

## S2 — THE LINEAGE HIJACK (drive leg died; cause reconstructed with detector math)
- Drive launched 11:35:12 (scripts/r1_t250_turndrive.py --target 1255
  --max-presses 220; hermes-venv python; log work/r1/t250_drive_20261102-113512.log).
  Its pre-drive popup drain closed 1 "popup" at 11:35:14.
- AT 11:35:16 the ring lineage FLIPPED 1086/4-power -> 645/3-power
  ['Nimbuloids','Hanshaks','Chronomyst'], ships 30->3, pm 26->3, sel 0->2,
  rank 65535->1. A DIFFERENT CAMPAIGN (the vendor TUTORIAL scenario: screen
  shows "Terpsichore / Orange Medium", Explorer I + Defender I, and modal
  "Do you wish to exit this tutorial?" — work/screens/t273/now_1156.png,
  /tmp/t273_screen1.png).
- CAUSE [inferred, strong]: the popup detector (v3 law: white-text rows in
  band y 330..470 root == game y 230..370, click = rightmost label of lowest
  row, ytop-3) MISDETECTED THE TITLE MENU as a popup. refcap.md measured title
  rows Play Introduction y=252 / Tutorial y=293 / New Game y=333 — the game
  y=237 click target lands INSIDE the Tutorial button (its row spans 240..270
  per ui.md PLAYTUTORIAL rect (159,240)-(477,270); refcap notes a y=293 click
  hit Tutorial one band low). dosbox.log later shows "Active save slot: 1
  [Empty]" (title) then tutorial autosaves. The t251 "popup chain confirmed a
  resume dialog" load is the same failure class.
- 13 presses, zero advancement (tutorial parks awaiting scripted player input;
  probes said input ALIVE — softlock never declared, correct). Driver KILLED
  ~11:49 via process_manage; ZERO further input to :9. A VNC client was
  connected during part of the window ([::1]:53822<->[::1]:53822, x11vnc pid
  1207; ss shows no owning process on this host => remote viewer) — cannot
  exclude the user clicked Tutorial themselves; both readings recorded.
- SAFETY: RESUME.GAM md5 RE-VERIFIED UNCHANGED post-incident. 1086 campaign
  preserved in bank-t273-predrive. Tutorial ring banked to
  work/r1/bank-t273-tutorial645/ (20 slots). No dosbox kill, no relaunch, no
  loadstate, game/ untouched.
- KEEPER LAW: popup drain must NEVER run when the game is at the title menu;
  recovery clicks must be band-measured, not detector-derived.

## S3 — HARNESS BUGS FOUND IN THE t251 MINE (both confirmed by measurement)
1. OWNER HANDLE vs RACE INDEX: t251's mine_stream reads owner as u16 pair at
   +0x54 => prints handles (att=196608/131072); relation lookups need the race
   INDEX byte at +0x56 (r265 law; MEASURED this session at t1253: byte56 maps
   0/1/1/2 -> names exactly, and the watcher's own ships[].owner == byte56).
   Consequence: t251's `if relv != 2` filter NEVER filtered (rel always None)
   — its "252 non-war candidate events" are meaningless, NOT witnesses.
2. STALE-ECHO PAIRS: rows of an old session's turn (e.g. 692) land between
   live turns; pairing "adjacent rows" without requiring prev_turn in
   {turn, turn-1} produced phantom deltas (-38/-34/-52 "Ungooma->Orfa" drops
   across a load boundary). Guard added in r273_harvest.
3. Nearest-other-owner ship != attacker: r273_vet.py added — per hit, min
   distance to a WAR power vs a PEACE power. All 6 flagged hull-decrease rows:
   NEITHER class within engagement scale (min distances 363..1854 u vs the
   60u reach) => UNATTRIBUTED, no non-war-damage witness.

## S4 — LEG RESULTS (r273_harvest.py over the FULL corpus, 72,327 deduped rows,
## 72,128 guarded same-lineage pairs; work/r1/t273_harvest_full4.out + t273_legA.json)
LEG A (OQ-016):
- 50 guarded damage hits: 32 hull-decrease {hist -13:5 -12:1 -11:1 -10:1 -8:10
  -7:1 -4:10 -2:3}, 18 shield-only {-10:1 -6:1 -5:8 -2:5 -1:3}. Classes:
  hull 26 AT_WAR / 3 PEACE_both / 3 unknown-state0; all PEACE/unattributed
  rows fail the vet (S3.3). NO damage-vs-non-at-war-owner witness. Honest
  negative; OQ-016 leg (a) NOT closed.
- MULTI-VOLLEY: 12 (turn,slot) pairs with >=2 damage hits across consecutive
  rows — ALL inside the t1253 Chamachies-vs-Ungooma (states==2, AT WAR) battle
  window (+1 at t908 state-0). Filter VALIDATED on this known battle (slot 14:
  6 hits; slot 23 hull steps -4,-4,-8; slot 21 -13,-4). t251's "cascade was
  the first" stands; multi-volley-vs-NON-at-war still zero corpus-wide.
- ATTITUDE PRICE CHANNEL (guarded): hist {-40:3 -28:2 -5:3 -3:31 -2:45 -1:890}.
  The -1 class = per-turn drift. -40 events: 3 rows = t887 (the t251 witness,
  now re-confirmed with ADJACENT pair 887->887) + t1253 '00:35:35' + its bank
  duplicate '08:22:52' => SECOND INDEPENDENT -40+WAR-FLIP EVENT:
  Ungooma->Chamachies 477->437 EXACTLY -40 with state 1->2 in the same row
  pair. -28 events: Chamachies->Orfa 618->590 state 1->1 (no flip). Clamp
  target DECL-10=280 still NEVER hit. OQ-016 ANNOTATED (2nd price+cascade
  witness; direction ambiguity caveat identical to t251's), STAYS OPEN.
LEG B (OQ-021):
- V>=25 rows: ZERO over the entire corpus. V census max 23 (20,703 rows);
  selector {0: 71,679}; rank {65535: 71,679} outside the tutorial lineage.
  NO threshold witness. OQ-021 leg (b) honest negative, STAYS OPEN.
- NEW SIGNAL: the tutorial lineage (648 rows) is the FIRST corpus segment with
  selector_byte=2 AND rank=1 (verified in guest RAM at the RELOCATED data base:
  P+0x43510 byte==2, P+0x4350c dword==1; player=DAT_0007458e==0 owns 3/50
  systems, V=0, 3 live ships). Selector semantics: presenter arms at payload
  file 0x2c03a(DEFAULT)/0x2c04d(end-xtnc)/0x2c064(end-dest)/0x2c07a(end-capt)/
  0x2c092(end-unit)/0x2c0a9(end-ctrl) (MEASURED by push-imm scan; score.md S3
  missed end-capt); the dispatch table itself (jmp dword[0x10173e0+eax*4]) is
  NOT locatable in the payload by arm-dword search (only 3 stray dwords in
  range) => selector->arm MAPPING [unverified] (arm-order reading would say
  2=end-dest, contradicted by the tutorial state; a control-victory reading is
  also possible). No end-screen window evidence: the five end-*.txt strings sit
  at IDENTICAL static addresses in every slot checked (image content, not an
  event trace). NOTE: watcher's relocated-address reads are correct for the
  DATA segment (turn/V/T validated); score.md's "code reads relocated
  0x285510" is the code-segment relocation of the operand — do not confuse.
LEG C (OQ-019): magnetron USE-frame candidates 0 (st5 control-class rows
160,747, other 0). Honest negative; STAYS OPEN.

## S5 — STATE OF THE BOX AT SESSION END
- :9 runs the TUTORIAL campaign (turn 645, parked, exit-dialog was on screen);
  watcher still healthy on it. Production 4-power campaign lives in
  bank-t273-predrive (t1086) + RESUME.GAM (user's, untouched).
- Relaunch-vs-leave is a USER DECISION (BLOCKED.md t273 block); research
  proceeds on offline corpus + pure-code tasks meanwhile.
- Tools added: scripts/r273_harvest.py (3-leg harvester, session-guarded),
  scripts/r273_vet.py (damage attribution vet). Outputs:
  work/r1/t273_harvest{,2,2,3,full,full2,full3,full4}.out, t273_legA.json.
