# t438 — FINAL VERIFY + HANDOFF (2026-11-20, zero capture)

Assignment: docs/STATE.md NEXT ACTION t438 (sitting check, ruling check, full
gate + audits, handoff summary, push-if-remote). No OQ closed — none was
closable this iteration (strict-close; each open row's gate-owner is named in
the STATE.md handoff block).

## F1 — Sitting check NEGATIVE
work/r1/playcap/ newest mtimes: live-timeline.jsonl / watch.out / watch.log
ALL 2026-11-12 06:45; save/ dir dir-mtime 2026-11-14 12:33 (rotation touch,
no new slots — see F5). No new sitting => scripts/r1_t85g_sitting.py NOT run
(header rule only fires on timeline growth).

## F2 — Ruling check NEGATIVE (channel alive, nothing answered)
- docs/DECISIONS.md mtime 2026-11-18 13:05:23 < last commit 2026-11-20 11:28:28.
- work/r1/shp_png/decision-sheet.md 2026-11-09 14:06 (D1 long applied, t367).
- Ruling-page server IS live: LISTEN 0.0.0.0:8613 pid 646702
  (`python3 server.py`, cwd work/r1/d1page). Newest file in d1page:
  index.html 2026-11-18 04:26; find -newermt '2026-11-20 11:28' -> EMPTY
  (no submission/answer store written since HEAD).
- Therefore D2 (acceptance, explicitly deferred — do NOT re-ask) and D12
  item-5 (audio match/differ verdict, the OQ-027(a) closer) are BOTH PENDING.
  Recorded as status only; nothing interpreted FOR the user.

## F3 — Full verify REAL (all fresh runs this iteration)
- bash scripts/gate.sh -> GATE_EXIT=0, tail '[gate] ALL CHECKS PASS
  (milestone=6)'. Log /tmp/gate_t438.log.
- Unit suite (gate runs run_tests under VENDOR=1, gate.sh:124-129):
  /tmp/gate_tests.log tail = "466 tests, 0 skipped, 0 failed".
- scripts/ledger_audit.py -> "rows=20 open=['OQ-016','OQ-019','OQ-027']
  closed=17 / LEDGER AUDIT OK".
- scripts/ledger_index_check.py -> "LEDGER INDEX OK" (STATE index mirrors
  the record file exactly).

## F4 — t437 artifact spot-verification (on-disk, cited)
- Pin: rewrite/tests/test_sfxpress_t404.cpp:35 TEST(sfx_press_buttons_button_t437).
- Code site: rewrite/src/ui/audio.cpp:30-38 sfxForPress — MapClick nullptr
  (COSMOSWnd -1 silent), RailButton/NextTurn/TitleButton "button".
- scripts/t437_soundchannel_store_census.py present (5040 B, 2026-11-20 10:59).
- R-t433 present at docs/REFUTED-ROUTES.md:1495.
(Note: grepping docs/re/audio.md for the literal "S6.9" returns nothing —
the section heading is written differently; the t437 update text is verbatim
in OPEN-QUESTIONS.md:334-355. Not a defect, just a search trap for future
sessions.)

## F5 — NEW ENVIRONMENT FACT: production game is DEAD (outranks ledger)
- work/r1/loop/GAME_DEAD.txt (written 2026-11-20 11:31:10): "game death
  detected ... pid None; reasons: G:DEATH(pid 107664 gone, zero harness
  dosbox-x in /proc); W:NOWATCHER(feed not banking); F:FEED-STALE(newest
  slot 60.sav 514658s old > 60s)" + instruction "bank the ring NOW (cp save/
  bank-tNNN-*), then relaunch per SOP."
- scripts/r1_game_health.py writes the flag but does NOT relaunch BY DESIGN;
  scripts/loop_one_task.sh:205 comment: "relaunching the game is
  research-schedule policy" — i.e. loop work. No bank-t439*/bank-* dir exists
  yet (ls bank-t* matched only doc references), so the ring was NOT banked by
  the harness.
- Consequence for the ledger: OQ-016 Phase-Bomb capture, OQ-019 sugar-cube
  scripted session (scripts/r297_order_session.py), and OQ-027(a) heap
  tune-table capture ALL need a live game; the corpus route is refuted
  (t49/t58/t265). => t439 = GAME-RING RECOVERY queued with
  bank-the-ring-FIRST discipline and the BLOCKED.md SOP constraints
  (one-writer-per-ring t266, TL=172800, Xvfb x11 headless, resume via title
  (318,333), kill-by-recorded-pid only, no loadstate-resume t261, no crash
  investigation on TL-expiry-shaped deaths t277).
- NOTE: the death is NOT TL-expiry-shaped in the t277 signature sense
  (514658 s ~ 6 days of slot age; the session's own TL expiry was
  2026-11-11 01:07 per the t349 sentinel line — so TL expiry IS the leading
  explanation for the 2026-11-12 06:45 feed stop; t277 law: do not open a
  crash investigation for it).

## F5b — RING BANKED THIS ITERATION (t439 step (1) PRE-COMPLETED)
cp -a work/r1/playcap/save -> work/r1/bank-t438-ring-2200: 20 slots, 43M,
newest 60.sav mtime Nov 14 12:33 (matches the FEED-STALE finding — no slot
newer than 2026-11-14 exists). t439 therefore starts at step (2) (relaunch
decision), NOT at banking.

## F6 — NO GIT REMOTE
git remote -v -> empty; .git/config has only [core] sections. The "push"
step in the t438 assignment closed as N/A with evidence. Older LANDED blocks
mentioning github.com/weylandsmith/ascendancy-rewrite (D14) refer to the
pre-sanitization state; deliverables here are local commits unless the user
configures a remote.

## Ledger disposition
- OQ-016: untouched this iteration (residue list EXHAUSTED per t3xx notes;
  row movement = USER ADJUDICATION per D3; Phase-Bomb sub-capture needs live
  game). STAYS OPEN.
- OQ-019: untouched (per-ship select writer unnamed; scripted-session route
  needs live game). STAYS OPEN.
- OQ-027: item (b) closed with measurement+code site at t437; item (a)
  gated on user hearing / heap capture. STAYS OPEN.
Honest negative: zero rows moved this iteration; the productive output is the
verified-green state, the dead-game discovery, and the t439 queue entry.
