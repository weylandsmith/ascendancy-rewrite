# t251 — LONG UNATTENDED DRIVE + WITNESS MINING (working log)

## S1 — Setup, corpus state at session start (2026-11-01 ~08:05)
- Live :9 dosbox pid 479966/479968 started 07:44 (post-OOM relaunch from the
  user's RESUME.GAM, turn 1086; in_game confirmed, V=score_stars=0,
  systems_any 26 / systems_full 24 at ring tail wall 08:03).
- Timeline work/r1/playcap/live-timeline.jsonl 6.78 GB / 282,132 rows,
  max turn 1335. Turns >1086 are PRIOR self-play/user-session rows (frozen-echo
  spikes at 1096/1131/1175/1208/1213/1253/1254; steady 60-300-row turns
  1097..1254; t1335 x139 = t189b alliance observation turn).
- WATERMARK LAW CONSEQUENCE (measured): trust=True drops every row with
  turn < running max => the NEW post-rewind session (turns 1087..1150) is
  INVISIBLE to trust=True (watermark already 1335). r1_stream's own caveat
  ("if you LOADED an older save mid-run that IS a real rewind — rerun with
  trust=False and pair rows by wall-clock") is the sanctioned instrument for
  the new-session window. Mining runs BOTH: trust=True over the assigned
  corpus, trust=False windowed on the new session.
- OOM law honored: scalar-only scans (r1_stream._scan_scalars pattern),
  never json.loads over the whole file.
- Pre-drive ring banked: work/r1/bank-t251-predrive (20 slots, turn 1086).
- Drive launched: scripts/r1_t250_turndrive.py (HERMES venv python — PIL)
  --target 1150 --max-presses 75 --max-softlocks 2, background, run log
  work/r1/t250_drive_<ts>.log.

## S2 — Drive outcome (MEASURED, work/r1/t250_drive_20261101-081121.log)
- Presses 1-10 advanced 1086->1096 (34 popups drained); presses 11-13 no
  advance at 1096 (probe input ALIVE 306,624 px; drain 0,0,2); press 14
  ring JUMPED 1096->1255 (V 23->14, systems_any 26->36) and the drive
  exited TARGET REACHED (target 1150).
- HYPOTHESIS for the jump (flagged [inferred]): the 07:44 relaunch loaded
  RESUME.GAM == the user's t1254 state (the STATE pairing note says resumed
  at 1086, but the t1254 bank exists and the live state at 08:17 matches
  t1254-era V/systems). Pressing NEXTTURN while a mid-turn modal sat open
  may have completed the user's queued turn cascade. NOT pinned; the
  honest fact is: ring 1086->1255, 14 presses, zero softlocks, no recovery.
- Post-jump ring is FROZEN at 1255 (57/58/59/60/41... all turn 1255 at
  08:18) — campaign likely over (Control-win screen) or softlocked. Drive
  process exited 0; SELFPLAY.marker removed (clean exit).
- Ring banked: work/r1/bank-t251-live1255 (20 slots). Pre-drive bank:
  bank-t251-predrive (20 slots @1086). User RESUME.GAM md5 check pending.

## S3 — WITNESS (b) ARRIVED (first real one in the corpus hunt)
- t212's roots (r1sav-*/r1deep-*/playcap ring) MISSED the bank-* dirs. With
  --banks bank-t1254,bank-t251-live1255,bank-t1096,bank-t250-predrive:
  mid-campaign slots WITH V>1 AND byte[star+0x15] nonzero EXIST:
  * bank-t1254 (turn 1254): ALL 20 slots V=23, nine +0x15 rows, ownP=9.
  * bank-t251-live1255 (turn 1255): all slots V=14, ten +0x15 rows, ownP=9.
- SEMANTIC NON-JOIN MEASURED: V != ownP (23 vs 9; 14 vs 9) and V != occ
  (14 vs 10 at t1255). The displayed count is NOT the +0x15 bitset count.
- P7-LABEL FORENSICS: star row 2 holds +0x15=0x3 (two races set) at both
  turns — co-ownership breaks single-owner-bit; +0x14 nonzero 50/50 (the
  t248 owner bitset). +0x15 semantics still unnamed (vision-adjacent).

## S4 — Shield-aggregate law applied to witness (a) (MEASURED)
- Offset census over 45,227 trusted points (coords+state+day skipped):
  high-frequency churn offsets are 0xa8,0x5a,0x88,0x7a,0x82,0x7e,0x5e,0x84,
  0x68,0x5c,0x60 — bookkeeping/pathing class. +0x4 (shield agg, t85 law)
  DECREASES only 10 times corpus-wide, INCREASES 26.
- Most decrease rows carry garbage owners (0xffff0000-class) = slot remap /
  pointer-move artifacts (t29b aliasing class), NOT damage.
- CLEAN named-owner shield-decrease candidates: (turn 780 slot23
  Chamachies->Orfa rel=0(untouched) dist2 9216) and (turn 1215 slot3
  Chamachies->Ungooma rel=1(PEACE) dist2 317696, shield 12->5). These are
  the witness-(a) class candidates; verifying via the DIPLOMACY channel
  (t204 law: firing slams attitude -20 / -40) before claiming.

## S5 — Attack-price cascade witness (t887) forensics
- Stream facts: att[3][0] (Minions row, Chamachies col) 324->284 == -40;
  states[3][0] 1->2 same window (wall 15:12:56 -> 15:18:03); NO other
  state/attitude transition in that trusted pair (full 4x4 diff).
- t204 law: row = VICTIM; -20 per committed weapon (gov byte 1), state-1
  pair; t208 chooser: DECL word 290 -> 284 < 290 flips WAR. Cascade
  matches EXACTLY except direction attribution is stream-ambiguous
  (self-declare slam cannot be excluded) and the clamp target 280 was
  NOT hit (price, not clamp).
- Mark window 0x48304..+0x3f census across banks: bank-t1254 20/20 slots
  byte[+38]==0x1 ONLY (contact latch bit0, t206 — never attack-written);
  live1255 + predrive all-zero. First nonzero byte ever in this window.
  => victim-bit side still zero corpus-wide; the t887 event left no mark.
  Either the fire used a path outside {0x39fba,0x3a255,0x4b875} caller
  set (impossible per t207/t210 census — so more likely: event was NOT
  0x43a4c at all, e.g. a diplomacy-AI declare whose price path writes
  attitude directly), or an unmapped clear. BOTH readings banked; the
  honest label on the witness is "attack-class price+WAR cascade", not
  "0x43a4c fire witness".
- t1253->1254 shield-drop pair: owner high-u16 0xffff->2 on ALL five rows
  = slot remap class, refutes the "AI multi-volley at t1254" hypothesis.

## S6 — Honest ledger outcome
- OQ-016 ANNOTATED STATUS t251 (first positive attack-class witness +
  sharpened damage-channel negative); STAYS OPEN (clamp witness absent).
- OQ-021 ANNOTATED STATUS t251 (witness (b) lands; non-join measured on
  real slots; P7 label killed); STAYS OPEN (writer = watchpoint class).
- No row CLOSED: strict-close — no single measurement settles either
  residue. OQ-005/OQ-019 untouched (need user rulings).
- NEXT = t252 verbatim (live screen sweep 1; :9 healthy at 1255 — sweep
  is safe: no war-starting/end-turn clicks; the game sits on the galaxy
  screen, Escape-backed).
