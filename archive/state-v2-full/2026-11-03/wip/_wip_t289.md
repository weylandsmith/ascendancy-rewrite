# t289 WIP — RAM liveness needle wired into the driver, V>=25 re-drive

Session: fresh 2026-11-03 ~12:25 EST. Assignment: STATE.md NEXT t289.

## S0 SESSION-START VERIFICATION (t287 law)
- pid 660167 alive (structured argv match: `dosbox-x -conf .../vnc/session.conf
  -nogui -time-limit 172800`, wrapper `timeout -s KILL 172830` pid 660165).
  NOTE first ps attempt with substring match printed nothing (self-match
  avoidance worked); ps -eo pid=,args= + basename match lists it.
- Ring work/r1/playcap/save FRESH: 10 s cadence, newest slot age <15 s
  (56/57.sav), turn 1086, in_game True, score_stars(DAT_482fb)=0/50,
  selector 0, rank 65535, systems_full 25, planets 26.
- Screen (:9 import /tmp/t289_start_screen.png, vision): IN-CAMPAIGN galaxy
  map, turn readout 01086, panel Planets/Ships/Research/Special Ability/
  Species. NOT title menu. Safe to drive.
- live-timeline.jsonl 7.85 GB mtime 12:24 (watcher alive); tail-scan only per
  OOM law.

## S1 DRIVER PATCH (scripts/r1_t261_drive.py) — all four STATE.md steps
1. NEEDLE (t288 S3b SOP) implemented as input_globals()/needle_census()/
   needle_probe():
   - read WORD pair (msg,char) = (ds:0x484c4, ds:0x484c6) from every ring
     slot's Memory member: member-index law mem[B + 0x82bb0 + off], B by
     r1_sav_scan.find_base anchor vote (>=5 votes). No debugger. ~0.16 s/slot.
   - needle_probe(): snapshot newest slot's pair, inject xsend key 'c', wait
     for >=2 fresh slots (mtime-gated, 10 s cadence), compare.
   - Verdicts: ALIVE = pair delta. DEAD = (1,0x1b) death signature survived,
     OR pre != 0x63 and no delta. AMBIGUOUS = pre char already 0x63 (NEEDLE
     EXHAUSTION: globals hold last-written event, not zeroed on consumption —
     healthy idle production demonstrably sits at (0x2e,0x63) forever), so a
     'c' re-inject cannot produce a delta even with a live pump.
   - NEW LAW (banked): a single-shot 'c' needle is only decisive when the pre
     char != 0x63; production's parked state IS (0x2e,0x63), so for the
     parked-campaign baseline the conjunction (pixel toggle + ring liveness)
     is the fallback — coded as the AMBIGUOUS branch.
   - OFFLINE VALIDATION (hermes venv python, has PIL; t285 law):
     bank-t261-soft1255 -> 20/20 slots (1,0x1b) distinct={1/1b}  [matches t288
     census verbatim]; bank-t261-prod-titlesoft -> distinct {(0x48,0x0)}
     [matches]; live playcap/save -> (0x2e,0x63) constant [matches t288's
     healthy-post-'c' row]. title_menu_on_screen(): t285 fixture
     probe_b_043813.png -> True frac 0.4685; live galaxy map -> False frac
     0.0016. Clean separation (>250x).
2. t285 PRECONDITIONS verbatim: assert_on_map() screen gate (orange-title
   detector, frac>0.20 over rows 0..330+MENUBAR, sampled 3x4) runs BEFORE any
   click at start, at stall2 (STOP-AND-LOOK: screenshot + bank + gate, never
   probe-then-click), and after every recovery. Escape last-resort branch in
   input_alive() DELETED (its ring_in_game guard is blind off-campaign — the
   branch could fire exactly where Escape is fatal, t285). drain_popups() now
   screen-gated too (t273 guard upgraded from ring-blind to screen).
3. V-WATCH: ring_v() reads score_stars/selector_byte/turn from newest
   in-game ring row every loop top; fires (bank + screenshot + exit 0) on
   score_stars >= 25 OR selector != 0. Absolute-level only, never deltas
   (t284 mid-recompute caveat: slots in the ~3 s window read low).
4. Softlock policy: needle DEAD -> ram_frozen confirm -> softlocks++ ->
   recover (RECOVER_MODE=resume) -> screen gate. max_softlocks 0 for THIS run
   = first softlock stops the loop, no retry spiral. alive_stalls>=4 with
   ALIVE pump = STOP-AND-LOOK exit 3 (engine stuck downstream — a NEW class
   the needle can now distinguish; the pixel probe conflated it with death).
5. recover(resume) REWRITTEN per t287 law: no more blind xsend click on
   (318,333) (stale-hover law — that click opened Tutorial Select). Now
   r287_title_nav.status() highlight read + Down-walk until cyan highlight is
   measured on R4 ReturnToCurrentGame, then key Return, then screen gate +
   ring in_game confirm.
6. --v-target and --max-secs flags added (deadline default 3300 s).

## S2 DRIVE RUN — RESULT (proc_2a5bc8e5d134, exit 0)
env T261_DISPLAY=:9 T261_BASE=work/r1/playcap T261_MENUBAR=0 T261_RECOVER=resume
args --target 1150 --max-presses 70 --max-softlocks 0 --max-secs 2700
(from t1086; log work/r1/playcap/drive_20261103-125013.log)
- TARGET REACHED t1150 at 13:11:12, 69 presses, ZERO softlocks, ZERO
  title-menu misfires (screen gate frac 0.0016 whole run). 64 genuine turns
  1086->1150 — the longest unbroken drive the drive class has achieved
  (t285: 6 turns before self-harm).
  Banks: t261-t1116, t261-t1146, t261-final-1150 (20 slots each).
- V WATCH (r273_harvest window 12:40-13:35, RC=0, 229 trusted rows, single
  lineage Chamachies/Orfa/Ungooma/Minions): V census {0:62, 23:167},
  selector {0: ALL 229}, rank {65535: ALL}. V>=25 rows: ZERO. V first lands
  23 at t1087 (first end-turn pass, t285 S-law reproduced on a third
  occasion) and HOLDS 23 for 64 turns while systems_full stays 25.
- REPLAY MINE-CHECK r284_vreplay on bank-t261-final-1150: TOTALS EXACT 20/20
  (stored V=23 == flood-replay pred 23, vis=mk=22 every slot). The decoded
  producer law holds on the NEW 64-turn data; V=23 < 25 because the flood
  prunes 2 lanes/claims — the threshold question stays about the COMPARATOR,
  and still no row in the corpus (now ~72.5k+) has V>=25 or a nonzero
  selector. OQ-021 THRESHOLD RESIDUE: honest negative again, row stays open.
- SIDE HARVEST: 149 attitude decreases (147x -1 drift + 2x -2 Orfa->Chamachies
  t1101/t1111, states 1/1 — no WAR co-occurrence); zero damage/destruction/
  owner-flip rows (peaceful drive); magnetron st5 control rows 3990, zero USE
  candidates.
- Production after run: pid 660167 alive (grep dosbo[x]), ring fresh at
  t1150, HEALTHY (DAT_482fb=23/50, sel 0). RESUME.GAM untouched (still the
  Oct-29 t1086 save; production RAM has MOVED to t1150 — the next resume-from-
  title would regress to t1086; drive continues from RAM, not RESUME).

## S3 NEEDLE INSTRUMENT SCIENCE (the real product of this iteration)
LIVE MEASUREMENTS on the running drive (pump alive by turn-advancement):
1. char GLOBAL == injected key VERBATIM: mid-drive pre (0x50,0x0), inject 'z'
   -> next 3 slots (0x2c,0x7a). msg code = stamping event class (0x2c key,
   0x2e mouse-move, 0x1 last-quit-event, 0x48/0x50 title/menu classes).
2. SINGLE-'c' NEEDLE IS BROKEN BY CONSTRUCTION when pre char == 0x63:
   witnessed pre (0x2e,0x63), one 'c', mouse re-stamping restored
   (0x2e,0x63) in every fresh slot — a DEAD pump frozen at (0x2e,0x63) reads
   IDENTICALLY. t288's SOP text ('inject c, expect 0x63') only works when the
   pre char differs from 0x63; the parked/idle baseline IS (0x2e,0x63) after
   t288's own probe. The run's one stall2 event (press 11, t1095) correctly
   printed AMBIGUOUS 'needle exhausted' under the first-cut code.
3. FIX (patched, verified live): needle char = 'c' unless pre char already
   0x63, then 'z' (single inject; 'c' path keeps its revert). Verdict rules:
   post char == needle -> ALIVE (dead pump CANNOT stamp — no false-ALIVE
   path); death-sig survived -> DEAD; constant pair across all 20 slots ->
   DEAD. LIVE POST-DRIVE VALIDATION: gate (False,0.0016); NEEDLE ALIVE
   'needle char 0x63 stamped: (44,122) -> (46,99)' — pre carried 0x7a (the
   'z' from measurement 1), 'c' stamped cleanly.
4. HONEST RESIDUES: 'z' map-side behaviour UNVERIFIED (observed benign once;
   fires only in-campaign behind assert_on_map, only in the exhausted-pre
   case); DEAD path validated only by OFFLINE census (soft banks 20/20
   (1,0x1b) — a live soft session was not available to inject into); msg
   codes 0x48/0x50 identity [unverified]; the in-run stall2 bank
   (bank-t289-stall2-t1095-press11) shows the OLD single-'c' verdicts — the
   fixed code ships for the next session.
5. The t288 death signature (1,0x1b) did NOT recur anywhere in this 64-turn
   drive (census distinct = {(0x2e,0x63)} style pairs throughout; zero
   softlocks) — consistent with the t288 class being restore-related rather
   than turn-count-related [inferred from one clean long drive].
