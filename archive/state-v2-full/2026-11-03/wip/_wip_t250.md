# t250 WIP — turn-driver robustness pass (2026-11-01)

## Mission (STATE.md NEXT ACTION)
scripts/r1_t245_turndrive.py (v3) advances turns + drains popups but is
softlock-blind. Add: (a) softlock detect (ring tail frozen except wall/file
fields + input probe zero-pixel-change) -> SIGKILL -> relaunch via
r1_playcap_vnc.sh start -> Return-to-game click window-rel (318,333) -> resume
drive; write work/r1/SELFPLAY.marker. (b) run log under work/r1/ (every press
+ drain count). Then ONE bounded validation: --target +10 on live :9.

## Session-start facts (measured 01:30Z-block)
- dosbox-x pid 462191 alive on :9 (session.conf, TL=28800); watcher banking;
  ring turn 1086 (idle idle game, healthy — zero clicks since t249b).
- Ring slots 41..60 in work/r1/playcap/save (29 MB). Bank dirs exist:
  bank-t1254, bank-t249-live-open.
- No playcap-* dir newer than Oct 14 => NOT a user sitting (t247 law).
- Timeline scalars per row: T T_known file file_mtime_ns in_game planets_mine
  rank rank relation score_stars selector_byte ship_raw ships systems_any
  systems_full turn wall. => "wall/file fields" = wall, file, file_mtime_ns.

## Design decisions
- New script scripts/r1_t250_turndrive.py (v4); v3 kept for history.
- DEVIATION from task text (documented): t247 law says the softlock signature
  recurred WITHOUT any popup, so popup-presence is LOGGED but not REQUIRED for
  the declaration. Safety guard replaces it: the check only runs after TWO
  consecutive non-advancing NEXTTURN presses with drain_popups()==0, so a
  healthy game merely waiting behind a popup is never SIGKILLed.
- Input probe = 'c' overlay toggle (galaxy-screen law, selfplay.md S2): press
  c, diff full-root screenshot; >50 changed pixels => alive (press c again to
  restore). Zero => candidate softlock; then 20 s ring re-sample; any changed
  field outside {wall,file,file_mtime_ns} => alive.
- Recovery banks save/*.sav to work/r1/bank-t250-recovery-<ts>/ BEFORE
  SIGKILL (t247 law; the t1092 frames were lost this way).
- SIGKILL only the pidfile pid (never pattern-kill; SIGTERM pops the game's
  own quit-confirm with Yes default — t247 law).
- Resume loads RESUME.GAM (t1086), NOT the ring turn — "resume the drive from
  the ring turn" means re-read ring after relaunch and keep driving toward the
  absolute target; turns beyond RESUME.GAM that were only in the ring are
  re-played by the game from 1086 (lossless for evidence: banked).
- SELFPLAY.marker (1 byte): created at drive start, REMOVED on clean exit 0;
  presence brackets self-play growth intervals (watcher rows carry wall ts).
- max-softlocks 2: second consecutive softlock exits 3 (t251 boundary law).

## Probe-law discovery (measured, decisive for detector design)
- 'c'-only input probe is BLIND on modal sub-screens: live :9 healthy session
  sitting on the planet LIST (t249 left it open) => press c changed 0 px;
  Escape changed 153,672 px; after backing to the galaxy screen, c changed
  1,152 px. Corroborates selfplay.md S2 (overlay is galaxy-screen-only) and
  KILLS the task text's literal "c-key toggle" probe: it would false-positive
  softlock on any healthy session parked on a modal screen. Detector now
  probes Escape FIRST (backs out of modals; no-op on galaxy), then c.
- Game alive-check at session start: dosbox 100% CPU (idle-hot caveat), ring
  rows banking, Escape reacts => healthy, not softlocked.
- PIL exists ONLY in the hermes venv python
  (/home/hrethric/.hermes/hermes-agent/venv/bin/python, PIL 12.3.0); the
  project .venv and system python3 have none. v3 runs must have used the
  hermes venv. Run v4 with the same interpreter.
- Ring tail parse: tail -c 400000 yields ~16 whole rows + partial head line;
  json.loads per line with skip-on-partial is correct (16 rows, newest
  59.sav wall 01:38:22 t=1086).
- Pre-drive ring banked: work/r1/bank-t250-predrive (20 slots, cp -p).

## Validation (running; results appended below)
Command: hermes-venv python scripts/r1_t250_turndrive.py --target 1096
--max-presses 25 (background, notify on exit). Started 01:4x.
