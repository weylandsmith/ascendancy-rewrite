# _wip_t266 — SOFTLOCK-CLASS FORENSICS (scratch, session 2026-11-02)

Pre-flight: git clean; dosbox-x :9 PID 535172 ALIVE (production, resumed
t1086, last ring bank t1236 23:37). No new user sitting (timeline growth =
watcher cadence), so t266 stands.

Incident inventory (from selfplay.md §7, t261 block, STATE.md):
  I1 t1089 popup-dead (Oct 31 13:14Z) — evidence work/r1/softlock_evidence.png
     + softlock-note.txt. Input-dead, RAM frozen, dosbox alive, recovery via
     RESUME.GAM t1086.
  I2 t1254 planet-list-dead (Oct 31 ~19:39) — bank-t1254,
     evidence_slot04_t1254.SAV.
  I3 15:45 process-death — went unnoticed ~1.5h (t267 context).
  I4 t261 production :9 (Nov 1 21:38) — t1111 healthy -> t1255/V=14 profile
     in ONE 10 s slot -> TITLE MENU -> input-dead; ring OSCILLATES
     t1254<->t1255 while dead; dosbox.log zero loadstate lines; bank
     bank-t261-prod-titlesoft/.
  I5 t261 :8 loadstate-of-t1255 input-dead ON LOAD (REFUTED t261 route) —
     proves the softlock is a SAVEABLE state carried by the save.

t265 FEED to test: softlock window is TURN-FROZEN-BUT-TAIL-RUNNING — slot 30
moved 32/64/160 units while turn readout stayed 1255; t1254<->t1255
oscillation repeats identical (dx,dy,dz) triples 3x. Commit site suspect.

H0 (RING-SHARING ARTIFACT, formed from harness forensics, UNVERIFIED):
 - r1_playcap_vnc.sh launches dosbox WITHOUT -savedir (autosave=10 41-60);
   r1_t261_session.sh launches WITH -savedir $BASE/save.
 - drive log work/r1/playcap/drive_20261101-213051.log (target 1405, the
   :8 RESTORED-t1255 session) shows presses 2-16 advancing ring 1096->1111
   then press 20 @21:38:41 JUMPS to 1255, then "no advance" forever while
   its own probe says "input ALIVE (changed_px=306544)" every 90 s.
 - t261 banked "t1111 healthy V=23 -> t1255/V=14 in ONE slot" — V=14 is the
   :8 RESTORED campaign profile, not production's (V=23, mine_any=26).
 - THREE r1_playcap_watch.py instances alive right now (524207, 524532,
   535187), all arg'd playcap.
 If playcap/watch.out rows at walls 21:38..23:06 carry mine_any != 26 (the
 :8 campaign), the t261 "production softlock" I4 is a WATCHER CONFUSION, not
 an engine event, and the t265 softlock window is the :8 softlock seen
 through the shared lens. DECISIVE TEST NEXT.

MEASURED SO FAR (pass 1, bounded watch.out scan, 311k lines):
 M1. watch.out t=1254/1255 fingerprint: EVERY t1254/t1255 row in the whole
     accumulating file has mine_any=36 (the t1254-era campaign). V varies:
     V14 (t1255 rows, and t1254 rows in 08:xx-13:xx + 21:xx-23:xx windows)
     and V23 (t1254 rows 14:xx-19:xx + one t1255 V23 row 18:42). NOTE
     day-mixing hazard: watch.out wall strings carry NO date — hour buckets
     mix Oct-31 and Nov-1 rows (t265 lesson re-encountered; mtime_ns needed).
 M2. Production dosbox.log VERBATIM shows states written to
     .../work/r1/playcap/save/ (cwd-resolved savedir; session.conf has NO
     savedir=, only autosave=10 41-60). t261_session.sh launches :8 with an
     EXPLICIT -savedir $BASE/save (t261-drive/save) + its own watcher.
 M3. Drive log playcap/drive_20261101-213051.log (the I4 incident drive):
     presses 2-16 advance ring 1096->1111 (21:32-21:35, healthy), presses
     17-19 "no advance" 1111, press 20 @21:38:41 "1255 (moved)", then
     pressed 21-38 all "no advance 1255" to 21:59. Its own input probe says
     "input ALIVE (changed_px=306544)" every ~90 s THROUGHOUT the stuck
     window — changed_px ~full-screen: that probe measures ANIMATION
     (starfield), not input response. HARNESS LESSON: the v4 pixel probe is
     always-true on an animating screen; t261's "input ALIVE" mid-softlock
     was a false positive (the arrows-probe later read 0 px = dead).
 M4. Row-rate math: 22:xx hour t1255 rows n=733 ~ 10 s cadence x 2 watcher
     processes -> the playcap ring WAS being rewritten at normal cadence
     during 21:38-23:06 (not frozen-disk); ~2900/hr rows at 08:xx-15:xx =
     ~8 watchers alive then (matches the 12-stale-watcher purge era).
 OPEN: which PROCESS wrote playcap/save during the window (production
 524517 vs a stray), and what campaign its RAM held. Reading banks next:
 bank-t261-final-1096 (21:29), bank-t261-soft1255 (21:22, the :8 ring),
 bank-t261-prod-titlesoft (22:50, mid-window).

FINAL (session complete): conclusion banked to docs/re/selfplay.md t266 block
+ docs/REFUTED-ROUTES.md t266 block + STATE.md LANDED t266. Headline: t261
"production softlock" = two-writer ring collision (campaign-fingerprint law);
I3 = -time-limit expiry; oscillation quantified (~150 s cycle, constant t1254
probe-row + fresh-hash t1255 runs); mid-window "input ALIVE" = starfield
animation artifact. This scratch file is now redundant with those; keep for
the probe trail.
