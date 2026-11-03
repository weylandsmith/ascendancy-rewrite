# Driver self-harm via the title menu — THE campaign-swap root cause (t285, 2026-11-03)

Hand-authored (docs/re/* is never regenerated; keeper tools named inline).
WIP working log: docs/re/_wip_t285.md. Witness banks: work/r1/bank-t285-predrive,
bank-t285-flip1255 (incl. the two decisive screenshots), bank-t285-loaded1255,
bank-t285-restored-t1086. Keeper tools: scripts/r285_fp.py, patched
scripts/r1_t261_drive.py.

## 1. THE LAW (witnessed in reproduction, screenshots + fingerprints)

ESCAPE AT THE BARE GALAXY MAP EXITS THE CAMPAIGN TO THE TITLE MENU. The game
keeps autosaving the RAM campaign while sitting at the title menu, so the ring
(and any ring-based watcher/guard) still reports in_game=True — the title menu is
INVISIBLE to RAM-side state. Only the screen distinguishes the two.

Consequence chain when an automated driver probes with Escape during an
input-dead window ("softlock class"):
1. Escape -> title menu (campaign still resident, ring still autosaving it).
2. The probe's pixel-diff reports "ALIVE" — the starfield-animation false
   positive already banked in selfplay.md t266 — so the driver believes input
   works and continues clicking.
3. drain_popups() at the title menu sees the white menu rows as a popup band
   (threshold px>190 grey-white text on dark panel) and clicks them.
4. A click on "Load Game" + a save-row click makes THE GAME'S OWN loader replace
   the RAM campaign with a DIFFERENT campaign from work/r1/game/*.SAV.
5. The next NEXTTURN click advances the LOADED campaign; the ring (still the
   same dir, still single-writer) now holds a MIXED LINEAGE and any
   "TARGET REACHED" verdict is false.

## 2. TODAY'S WITNESS (2026-11-03, production :9, drive 04:33:53)

- Presses 1-6 advanced 1086->1092 (genuine production lineage; rows banked).
- Presses 7-8 (04:37-04:39): NEXTTURN at measured (511,67) did NOT advance;
  drained=0 (no popup) — softlock-class struck after only 6 presses.
- 04:38:11 probe_a screenshot: CAMPAIGN t1092. Driver sent Escape (old
  input_alive). 04:38:13 probe_b screenshot: TITLE MENU, rows verbatim
  "Play Introduction / Tutorial / New Game / Return to Current Game / Load Game
  Alt-L / Save Game Alt-S / Exit to DOS". Escape is NOT inert at the map.
- Press 9 drained=2 (two title-menu row clicks => Load Game + save row).
- 04:39:45 flip bank: ALL 20 slots turn=1255 V=14 owned=124 fp=39614c7c
  (pre-drive bank: ALL 20 slots turn=1086 V=0 owned=104 fp=3a189896). One clean
  swap, no interleave, no oscillation this time.
- Press 10 advanced the loaded campaign -> driver printed "TARGET REACHED at
  ring turn 1255" on 10 presses — FALSE SUCCESS on mixed lineage.

## 3. THE NOV-1 21:38 PRODUCTION INCIDENT IS THE SAME MECHANISM (corroborated)

work/r1/playcap/drive_20261101-213051.log (read this session, n=38 presses):
presses 17-18 t1111 no-advance drained=0 (softlock), 21:37:14 "probe: input
ALIVE (changed_px=306624 — IDENTICAL tell to today)", press 19 drained=2, press
20 "ring turn 1255 (moved)". The flip slots of that incident
(work/r1/bank-t261-t1255 slots 54-60) carry fp=39614c7c — THE SAME loaded
campaign as today's swap. t266's two-writer analysis stands for RING-content
corruption (a stray dosbox writing playcap/save), but the RAM CAMPAIGN SWAP in
both incidents is driver self-harm via Escape+drain at the title menu, clicking
the game's own Load Game. The "oscillation" t266 measured (t1254<->t1255 every
~150 s) is the same loop: Escape -> title -> drain -> Load -> advance -> stall.
The t261 "input-dead ON LOAD" law (t1255 save captures a frozen state) remains
separate and unrefuted — what changed is WHO loads it and WHY.

## 4. FINGERPRINT TOOL LAW (scripts/r285_fp.py, keeper)

fp = md5[:8] over sorted (planet-name, owner-byte) pairs from
r1_income_law.find_records on the ZIP member "Memory" (NOT namelist()[0] —
CMOS sorts first; trap hit and fixed in-session).
- fp EQUALITY across slots of the SAME session/run is a valid campaign-identity
  test (1086-slots vs 1255-slots separated cleanly, 20/20 each side).
- fp equality ACROSS a load/restore is NOT layout-stable: after
  Return-to-Current-Game the locator chain found recs=156 vs 152 and fp changed
  (179af5f4 vs 3a189896) while the campaign was provably intact (see 5). The
  name-anchor walk picks a different mod-class when the heap reshuffles.
- Layout-INDEPENDENT restore check that worked: watcher-level ship census —
  sorted tuple list of (owner,state,design,x,z) over live slots via
  r1_slot.ship_records. pre-drive shipfp f4e5e715 (26 live) == restored
  shipfp f4e5e715 (26 live); loaded-1255 = 0272c480 (35 live). Use THIS to
  verify a restore; use planet fp only within one run.

## 5. RECOVERY EXECUTED (production restored to t1086, SOP-grade)

- RESUME.GAM survived untouched throughout (md5 5b382afbb789186c3654f3cec085b2e2
  before and after — the game only writes it on an in-game Save, never clicked).
- Return-to-Current-Game click at the title menu did NOT dislodge the loaded
  t1255 campaign (it keeps the LAST-loaded state; verified by screenshot +
  watcher rows). So the restore lever is: bank -> SIGKILL recorded pid ->
  r1_playcap_vnc.sh start (TL=172800 default) -> ONE click (318,333) at the
  title menu -> resume from RESUME.GAM. Executed 05:26-05:28: watcher back to
  t=1086 V=0 26 systems; shipfp verified equal to pre-drive (f4e5e715).
- New production pid 660167, TL expiry 2026-11-05 05:26:51. The loop's drive
  target (t1250+) was NOT reached; the ~30 genuine rows 1087-1092 survive in
  bank-t285-predrive + the timeline.

## 6. DRIVER PATCHES SHIPPED (scripts/r1_t261_drive.py)

1. drain_popups() gated by ring_in_game() — cheap first line; INSUFFICIENT
   ALONE (the ring keeps saying in_game at the title menu — law 1). Kept because
   it catches the full-death class.
2. input_alive() rewritten: 'c'-overlay FIRST (self-reverting, title-menu
   no-op), Escape demoted to last resort AND gated by ring_in_game(). The
   starfield false-positive threshold remains PIXEL_ALIVE=50 — t266's warning
   stands: pixel-ALIVE is NOT evidence a NEXTTURN click landed; only ring
   turn-moved is.
3. RECOMMENDED FURTHER HARDENING (not yet shipped, next drive-class task):
   screen-based title-menu detector before ANY click (e.g. the orange title
   background dominates rows y<100 of the game area, or the white menu box at
   rows ~330-565 window-rel; probe_b is the fixture), and treat 2 consecutive
   no-advance presses as STOP-AND-LOOK (bank + screenshot + human flag) rather
   than probe-and-click.

## 7. HARVEST LEGS ON THE 6 GENUINE TURNS (r273_harvest.py window
04:33:00-04:39:41, 42 rows / 40 pairs) — all honest negatives, no OQ moved:
- Leg A: ZERO damage applications (hull/shield decrease), zero destructions,
  zero owner flips; 11 attitude deltas ALL -1 drift class, none <= -2, none
  co-occurring with a WAR flip. (OQ-016 damage-vs-non-war witness: still zero
  in the whole corpus; the only price witnesses remain the t1253 -40/-28 pair.)
- Leg B: V census {0:7, 14:2, 23:33}; ZERO V>=25; selector all-zero; rank all
  65535. V=23 reached at t1087 (first end-turn pass) and HELD 1087-1092 —
  consistent with the t284 flood law (no lanes newly admitted).
- Leg C: ZERO magnetron USE-frame candidates (806 st5 control rows).
- MINE-CHECK per the t284 law: r284_vreplay.py on bank-t285-flip1255: 20/20
  EXACT (V=14 pred=14, vis=mk=13) — the replay law holds on the loaded campaign
  too (a DIFFERENT campaign seed, 4 races, 58 lanes).
