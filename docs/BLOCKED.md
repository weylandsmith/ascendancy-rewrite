# BLOCKED.md — machine block register + runbook (slimmed 2026-11-03)

Full decision history + every superseded block (t44..t277: the OQ-021 threshold
saga incl. the t75 fabrication post-mortems, the t258/t259 play-gate and dead-
process addenda, the t273 tutorial-hijack hold, the t187 player-ask list,
t48/t49/t51/t52/t55/t57/t70/t82/t89a/t186):
archive/state-v2-full/2026-11-03/BLOCKED.md (md5 2e7c0940e11e839390abb7c9ebf4c1a6).
THE USER-FACING ASK SURFACE IS docs/DECISIONS.md — read that to see what needs a
human. This file is what the loop itself cannot close, plus the safety runbook.

## Standing decision (NOT re-openable)
Option C hybrid, B-priority, chosen by the user 2026-10-04: data-first work plus
R1 runtime capture via dosbox-x save states, no cadence limit (abolished
2026-10-05). Rationale + the refuted A/B fork: archive/ralph-v1/BLOCKED.md.

## Current blocks (research the loop cannot close alone)

### OQ-005 — .shp dims-field location, 80 records (BLOCKED-USER-LEVEL)
Grammar/blit/runtime-table laws CLOSED with citations (shp.md S9/S12/S14/S16/
S17); W3 sanctioned route EXECUTED negative (all 75 decoder sites read dims
ONLY from the record-start header; cache load = verbatim copy). Residual: 80
records / 31 files whose in-record dims location is unknown (.tmp/1starmap
cached heads non-verbatim, so file-space inference unsound there). Decomposed
t278 (shp.md S24.2): 25 zero-byte ladder slots (batch-rulable) + 12 cos_star
k40..k51 (addressable-but-blit-refused per t200 selector law) + 4 invalid-dims
+ 2 t197 dims-gate demotions (mouse k5, sg64expl k0) + 3cfgnew k12 (vendor EOF
truncation). Closure class = human-verifiable drawn frame (R13 forbids self-
grading) OR user ruling on the shipped DECISION SHEET:
work/r1/shp_png/decision-sheet.md (88 rows; t347 REBUILD adds a cited
DISPOSITION per C-row — 40 no-ask + 1 junk-certain + 3 adjudicable — asserted by
the generator). PITFALL (t347 amendment): scripts/r1_t182_pngdump.py still
REWRITES index.txt on every run, but scripts/r1_t278_decision_sheet.py now
writes index.txt too (pointer header + the identical sheet bytes), so recovery
is "re-run the generator", not hand-editing. Hand-author only in
decision-sheet.md (and even there, prefer editing the generator's tables so the
next rebuild keeps the text). Blind sweeps FORBIDDEN (R2). Default in force: decode per
S16 V/A law (dims at rec / rec+0x10); residual class skip-and-warn in tooling,
never game-visible (rewrite renders its own vector art; codec = validation
asset). Details: docs/DECISIONS.md D1.

### Nuke law (Phase Bomb gizmo 70) — capture-gated; default: NOT modelled
Static died: device effects are DATA-DISPATCHED (no in-code caller; same shape
as event-24 dispatch 0x4402a); every CMP-imm70 site resolves to ASCII parsing
(0x796ad/0x7a49a), the AI 70-turn reject (0x3f6eb), message ids, or data
(income-law.md T39e). 13 scripted AI runs never built one;
r1_destruction_census.py finds ZERO device-destruction events corpus-wide.
Default: not modelled in rewrite combat (documented abstraction, ships.md) — no
silent stub; OQ-016 names it. Closing route (one R1 run): scripted campaign
forcing Phase Bomb (restree prereqs, build at Shipyard, launch at an owned
planet with >=3 surface items); identify the dispatch entry by which code first
writes FF into a mid-record slot byte at launch (3-save diff + static sweep of
the launch handler — whole-image watch not needed).

### OQ-CARGO AI landing-site chooser (BLOCKED-static, default in force)
Chain CLOSED except the picker (income-law.md S13.5): cargo placement = EVENT 4
with +0xae from EVENT 8's FUN_0003a880 converter, legality re-gated FUN_0003830c
(rule G). Missing: who picks the AI's landing COORDS. get_xrefs_to(0x3aa0a)=0,
byte scan '0a aa 03 00'=0, operand scan=0 — handler reached ONLY via a
data-resident table (t44, 2 rounds, stopped per no-spiral rule). Closing needs
a whole-image DATA scan for table-shaped dword runs + call-shape validation —
beyond a bounded recipe. Default: rewrite places arrival CBs by the uniform
non-rock picker draw (campaign.cpp seedColonyBaseColony; consistent with
rule-G-exempt CB + 26% barren + ranks 4/40).

### Per-ship build/redesign path (BOUNDARY by decision, t209/t210/t256c law)
The rewrite models fleets as aggregate vectors; the vendor's per-ship order
states (kind 1..5, Invasion-Module carriers in 480 ships, per-ship gizmo
inventory) are observable in the ORIGINAL and NONE is representable without a
per-ship sim (t256c census, 62,762 trusted rows). AI dossier row 16 relabelled
GAP->BOUNDARY PERMANENTLY. This is a BUILD decision, not an RE unknown:
docs/DECISIONS.md D3.

### Scripted-move capture (t48/t49 route) — LIVE, t298 owns the next launch
Historical: the corpus CANNOT supply flight (t49: 484 saves, zero state-4, zero
movement, zero item-23 landings; t58 scripted-fresh null too), and st4 is a
DWELL state invisible at 10 s ring cadence (t265 law). The route that closes
OQ-019's sugar-cube residue is ONE scripted session: click own ship, click
lane-adjacent destination, End-Turn x2, read per-autosave coords from the ring.
Capability proven end-to-end t297 (drive plumbing clean; session died at its
own picker bug — owner==0 filter, fixed). The live choreography authority is
docs/re/_wip_t297.md S1 (msg-4 router re-read) + ships.md S24/S25; the driver
is scripts/r297_order_session.py (venv python!). GATE: End Turn ONCE before
picking (owner-0 fleet has no kind-4 ship at t=1086; slot 8 lands at t=1087).
Do NOT re-run corpus mining for this — t49/t58/t265 closed that class three
times.

## Sentinel park log (t349+; one line per parked iteration — checks per STATE.md NEXT)
- 2026-11-09 t349: parked, no trigger. Sitting check NEGATIVE (400 KB tail-seek,
  16 lines, newest turn 1086; ring rotation only — newest save 51.sav
  2026-11-09T04:52:29.856 ns, game pid 1555 HEALTHY, TL expiry 2026-11-11 01:07).
  No D1/D2/D3 ruling: DECISIONS.md mtime 03:31 (pre-t348-commit), no USER:/RULING
  markers, post-commit find -newermt shows only capture/loop artifacts.
  decision-sheet.md 03:40 = t347 generator output, not an annotation. NEXT stays
  the WAIT-TRIGGER sentinel verbatim; no research task invented (t178).
- 2026-11-09 t350: parked, no trigger. Sitting check NEGATIVE (400 KB tail-SEEK,
  16 lines, newest 54.sav, turn field 1086 on 16/16 records == corpus floor;
  timeline 8,808,297,699 B, growth = ring rotation only). Production :9 HEALTHY
  (pid 1555 up 03:53, TL expiry 2026-11-11 01:07, watcher 1575, saves at
  05:00:30). No ruling: DECISIONS.md 03:31 / decision-sheet.md 03:40 both pre-date
  the t349 commit 04:56:55, `grep -i USER:` in DECISIONS.md = zero hits, and the
  post-commit find -newermt sweep (22 files) is only docs/re/* regeneration
  timestamps + work/r1/loop + dosbox.log — no hand-edited file anywhere. NEXT
  stays the WAIT-TRIGGER sentinel verbatim; +0x0a hunt not re-opened (t348(1)-(3)
  binding); no research task invented (t178).
- 2026-11-09 t351: parked, no trigger. Sitting check NEGATIVE (400 KB tail-SEEK,
  16 lines parsed, turn field 1086 on 16/16 records == corpus floor; timeline
  8,809,340,543 B, newest ring saves 59.sav 05:07:10 / 60.sav 05:04:00 — growth
  = ring rotation only). Production :9 HEALTHY (GAME_HEALTH_LIVE: game pid 1555
  up 04:00, TL expiry 2026-11-11 01:07:10, watcher 1575, ring 46.sav age 4s).
  No ruling: DECISIONS.md mtime 03:31:41 and decision-sheet.md 03:40:49 both
  pre-date the t350 commit 05:03:50; grep -i 'USER:' DECISIONS.md = 0 hits;
  per the t350 guardrail the post-commit find sweep (STATE.md/BLOCKED.md = t350's
  own writes, docs/re/* + attribution.tsv + loop logs = gate regeneration) is
  interpreted ONLY via `git status --porcelain` = EMPTY, so no hand edit exists.
  NEXT stays the WAIT-TRIGGER sentinel verbatim; +0x0a hunt not re-opened
  (t348(1)-(3) binding); no research task invented (t178).
- 2026-11-09 t352: parked, no trigger. Sitting check NEGATIVE (400 KB tail-SEEK,
  17 records parsed with json, turn field 1086 on 17/17 == corpus floor; timeline
  8,810,407,088 B, newest tail record file=60.sav; ring saves rotating at the
  10 s cadence — 60.sav mtime 05:14:00). Production :9 HEALTHY (game pid 1555,
  TL expiry 2026-11-11 01:07:10, watcher 1575, ring age 5s). No ruling:
  DECISIONS.md mtime 03:31:41 and decision-sheet.md 03:40:49 both pre-date the
  t351 commit 05:10:33; grep USER:/ANSWER:/RULING/RULED over DECISIONS.md hits
  only the author's own ask-text (lines 13/80/85/94), decision-sheet hits are the
  generator's disposition column; post-commit sweep = gate-regenerated docs/re/*
  only and `git status --porcelain` EMPTY per the t350 guardrail — no hand edit.
  NEXT stays the WAIT-TRIGGER sentinel verbatim; +0x0a hunt not re-opened
  (t348(1)-(3) binding); no research task invented (t178).

- 2026-11-09 t353: parked, no trigger. Sitting check NEGATIVE (400 KB tail-SEEK,
  16 records parsed with json, turn==day==1086 on 16/16 == corpus floor; timeline
  8,811,378,829 B, newest tail record field file=58.sav; on-disk ring 58/59/60.sav
  05:20:21/:31/:41 = 10 s rotation, not play). Production :9 HEALTHY: dosbox-x pid
  1555 up 04:13:36 (-time-limit 172800, TL expiry 2026-11-11 01:07), watcher pid
  1575 r1_playcap_watch.py --no-exit, health 'ring 45.sav age 0s'. PATH NOTE: the
  health file is work/r1/loop/GAME_HEALTH_LIVE.txt, NOT work/r1/GAME_HEALTH_LIVE.txt
  (t351/t352 LANDED blocks cite the latter path; the file there does not exist).
  No ruling: DECISIONS.md mtime 03:31:41 and decision-sheet.md mtime 03:40:49 both
  pre-date the t352 commit 5af066b 05:17:00; grep -i -E 'USER:|ANSWER:|RULING|RULED|
  user replied' DECISIONS.md = 4 hits, all the author's own ask-text (D1 header L13,
  'if undecided' L58, status lines L80/85/94); the 59 sheet hits are the t347
  generator's own disposition column. git status --porcelain EMPTY (t350 guardrail);
  post-commit find -newermt sweep = gate-regenerated docs/re/{gizmos,economy,modules,
  fnt,text}.md only. NEXT stays the WAIT-TRIGGER sentinel verbatim; no research task
  invented (t178); +0x0a hunt not re-opened (REFUTED t348(1)-(3)); game/ untouched.
- 2026-11-09 t354: PATH FACT banked (the only deliverable this iteration — see
  the t354 LANDED block in STATE.md for the full account). Short form: the
  decision sheet lives at work/r1/shp_png/decision-sheet.md and has NEVER
  existed at docs/decision-sheet.md (t354 stat: no such file; git ls-files =
  zero hits under docs/). Prior sentinel scripts t348-t353 are untracked and
  gone, so what they actually watched is unrecoverable — their park lines
  report sheet mtime 03:40:49 which matches the REAL file, but trigger
  fidelity is UNVERIFIABLE. (STATE.md NEXT has always named the real path
  work/r1/shp_png/decision-sheet.md — do NOT assume the old sentinels
  watched docs/; t354 briefly did and was wrong.) t354 sentinel (work/r1/sentinel_t354.sh,
  untracked — logic restated here so it survives): watches the REAL path,
  trigger = mtime > 03:40:49 baseline OR git-diff-vs-HEAD OR any
  *ruling*/*reply* file in git status --porcelain; 60 s poll, 45 min cap.
  LESSON: stat a watched path at authoring time — a sentinel on a missing
  file reads 'no change' forever, silently. CORRECTION after the run: the
  STATE.md NEXT text always named the RIGHT path (work/r1/shp_png/...); the
  phantom docs/ path was t354's own misreading of the park lines, which cite
  the sheet by bare filename. The t354 sentinel therefore watched the real
  file and its negative IS valid ruling evidence.
- 2026-11-09 t354: parked, no trigger. Sitting check NEGATIVE (400 KB
  tail-SEEK, 16 records parsed with json, turn field 1086 on 16/16 == corpus
  floor; timeline 8,819,223,860 B, growth = ring rotation only — tail field
  files 53/54/55.sav are ring slots, not play). Production :9 HEALTHY:
  dosbox-x pid 1555 up 04:22+ (-time-limit 172800, TL expiry 2026-11-11
  01:07:10), watcher 1575, health 'ring 47.sav age 4s' (health readout path
  confirmed: work/r1/loop/GAME_HEALTH_LIVE.txt). Ruling check via the t354
  sentinel (45 min, 60 s poll, watched the REAL sheet path
  work/r1/shp_png/decision-sheet.md + *ruling*/*reply* files + git diff vs
  HEAD): TIMEOUT, no trigger; re-confirmed after exit — sheet mtime still
  03:40:49.800 (t347 generator output), git status = own docs/BLOCKED.md
  edit only. No row moved strict-close; ledger stays 16/3 (OQ-005/016/019
  all user-gated). NEXT stays the WAIT-TRIGGER sentinel verbatim; +0x0a hunt
  not re-opened (t348(1)-(3) binding); no research task invented (t178);
  game/ untouched.
- 2026-11-09 t355: parked, no trigger. Sitting check NEGATIVE (400 KB
  tail-SEEK, 16 records, turn 1086 on 16/16, newest tail file=50.sav; timeline
  8,820,053,395 B — growth vs t354 baseline is ring rotation only). Ruling
  check NEGATIVE pre-launch (DECISIONS.md 03:31:41.300 + sheet 03:40:49.800
  unchanged, porcelain empty, no *ruling*/*reply*, grep USER: = 0). Ran the
  t355 poller (sentinel_t355.sh, 60 s poll, 45 min cap, launched via
  terminal(background=true) — nohup is rejected by the tool harness): TIMEOUT,
  no trigger; post-exit re-confirm mtime unchanged, pid 1555 alive. Production
  :9 HEALTHY (pid 1555 up 05:12+, TL expiry 2026-11-11 01:07:10, watcher 1575).
  No row moved strict-close; ledger stays 16/3. NEXT stays the WAIT-TRIGGER
  sentinel verbatim.
- 2026-11-09 t356: parked, no trigger (EIGHTH consecutive park). Sitting check
  NEGATIVE (400 KB tail-SEEK, 16 records, turn 1086 on 16/16, newest tail
  files 44/45/46.sav; timeline 8,827,874,725 B — +7.8 MB vs t355 baseline is
  ring rotation only). Ruling check NEGATIVE pre-launch (DECISIONS.md
  03:31:41.300 + sheet 03:40:49.800 unchanged, porcelain empty, no
  *ruling*/*reply*, grep USER: = 0 on both docs). Ran the t356 poller
  (sentinel_t356.sh, 60 s poll, 45 min cap, terminal(background=true,
  notify=true), session proc_9913cfae18a0): TIMEOUT:no ruling after 45min;
  post-exit re-confirm both mtimes unchanged, porcelain showed only the
  session's own _wip_t356.md. Production :9 HEALTHY (pid 1555 up 06:54:39,
  watcher 1575, TL expiry 2026-11-11 01:07:10, ring 56.sav age 4s). No row
  moved strict-close; ledger stays 16/3. NEXT stays the WAIT-TRIGGER sentinel.
- 2026-11-10 t368: parked, no trigger. BRANCH 1 (sitting) NEGATIVE on the LIVE
  RING, not the feed: the timeline watcher (pid 1575) DIED ~2026-11-09 17:26
  (GAME_HEALTH_LIVE.txt 'UNHEALTHY | W:NOWATCHER(feed not banking)', feed mtime
  17:26 with ZERO bytes growth vs baseline) while the game kept autosaving — so
  the tail-seek law was BLIND for ~14 h. New primitive scripts/t368_ring_turn.py (moved from work/r1/ at t373)
  (read-only; unzips each ring .sav, cached-anchor base, r1_slot turn scalar):
  20/20 slots turn=1086 at 07:2x AND again at 08:0x (turn monotonic => no play
  crossed a turn boundary in the dead window). BRANCH 2 (ruling) NEGATIVE
  pre-launch, mid-poll, post-exit: DECISIONS.md mtime 2026-11-10 06:23:41.040 ==
  baseline exactly, git diff empty, porcelain = only this session's own files,
  no *ruling*/*reply* (three vendored dosbox-x clock_reply.h hits are tracked
  macOS headers, cannot fire the porcelain-based grep). Poller
  sentinel_t368.sh (proc_6d442daa5692, pid 102048) exit 0
  'TIMEOUT:no ruling after 45min'. BRANCH 3 taken: this line. Production :9
  ALIVE (pid 1555 etime 1-06:50, TL expiry 2026-11-11 01:07:10) but WATCHER
  STAYS DOWN — relaunch deliberately NOT done (F6: not the task; two-writer
  law; harness/user call). Ledger 17/2 unchanged, strict-close honest negative.
  NEXT = same sentinel (RING-FIRST), TAG FIXED: 'NEXT WAIT-USER-RULING t369 —'
  (field 2 must match WAIT* — see WIP F8: written 'NEXT t368 —', the scheduler's
  field-2 tag read as a QUEUE TASK and TRIGGER C armed this very session,
  loop.log:289885 'queue drain (t366 -> t368)' — the t243 self-arm class reborn
  via 'rewrite verbatim' keeping words but incrementing the number; validated
  with the scheduler's exact awk => never arms; wake routes dirty/LOOPSTEER/
  FORCE_RUN/IDLE_GATE=1 are tag-independent, none lost). work/r1/
  sentinel_t369.sh pre-staged (copy, baselines unchanged).
## R1 runbook (mandatory safety invariants — a run without them is a bug)
Route: scripts/r1_savestate.sh (+ r1_sav_scan.py per-run base B; NEVER hard-code
B; member = physical + H, H=136 for dfsg 2025.02.01, re-derive per build — the
off-by-H class cost t286 a whole thread). Deep capture: r1_deepcapture.sh.
Scratch debugger sessions: docs/re/dosbox-debugger.md operating rules.
Enforced statically by gate 3n/3n3.
- dosbox NEVER mounts pristine game/ — scratch copy under work/r1/ only.
- ONE dosbox-x per ring dir (two-writer law t266: a second writer corrupts
  evidence AND freezes the game). Scratch ALWAYS gets its own ring dir.
- HEADLESS: output=x11 under Xvfb for anything needing vblank autosave (the
  host-clock autosave is checked at vblank — dummy video = no saves);
  nosound=true; stdin=/dev/null. Background shells need DISPLAY=:9 injected
  explicitly (xsend fails SILENTLY otherwise; xsend arg1 = WINDOW TITLE, not
  display — t290).
- TL: launch TL=172800 (r1_playcap_vnc.sh default; NEVER 28800 — the runaway
  guard killed 18 of 33 logged sessions at 28810-28820 s with exactly 2880
  autosaves, and dosbox-x emits NO farewell line, so poll /proc, t277). Before
  any unattended leg > ~40 h: bank ring -> confirm no human VNC client -> TERM
  the recorded pid -> start -> health check shows the new expiry (SOP:
  docs/re/selfplay.md t277). A dead session with ~2880 saves per 8 h of life
  died of TL expiry; do NOT open a crash investigation for it.
- KILL BY RECORDED PID ONLY. `pkill -f` / `pgrep -f` match the searching
  shell's OWN command line (killed this project's shell twice); `pkill -x
  dosbox-x` does not discriminate INSTANCES (froze production once, t267) — the
  pre-t267 advice "kill ONLY pkill -x dosbox-x" is RETRACTED. Structured
  matching instead: parse `ps -eo pid=,args=` in Python, compare
  basename(argv[0]) == 'dosbox-x'. SIGKILL a softlocked dosbox (SIGTERM pops
  its own quit-confirm with (Yes) as the DEFAULT — a stray Enter kills it).
- NEVER loadstate a bank to resume work (input-dead-on-load, t261: the softlock
  class lives INSIDE the save; loadstate GUI path itself works, t260).
  Production resumes via title 'Return to Current Game' (318,333) — and the
  live state lives in the RING, not RESUME.GAM (t259 law).
- CADENCE LAW (19 runs): autosave period CONSTANT 10 s; turn advance NEVER
  automatic (14 idle runs hold turn constant); each NEXTTURN click landing ON
  THE STRATEGIC MAP advances exactly +1 (modal views SWALLOW clicks). Schedule
  by TIME, verify by TURN number; a turn straddles 1-3 slots, slots rotate
  41..60 cyclically. Ring holds ~200 s — bank before restarts + every ~30 turns.
- DRIVE-CLASS LAW (t285, docs/re/driver-selfharm-t285.md): detect the title menu
  FROM THE SCREEN before any click (orange-frac gate, assert_on_map); 2
  consecutive no-advance presses = STOP-AND-LOOK; NEVER Escape at the bare map
  (it exits the campaign to title while the ring keeps autosaving — RAM guards
  go blind). All three implemented in r1_t261_drive.py, verified 64 clean turns.
- OOM LAW: live-timeline.jsonl ~6.4 GB — read ONLY via r1_stream.py, a <=400 KB
  tail-scan, or r214_triage.py. json.loads over the file OOM-killed a whole tmux
  scope at 13.4 GB RSS (t251).
- TIMELINE-MINING LAW (t214): event COUNTS come only from
  r1_stream.observations(trust=True) — the capture dir accumulates watcher
  instances (4 live at t214, 12 historically), raw counts are writer-
  multiplicity garbage (4.26x overall, ~12x locally). Run r214_triage.py before
  mining any fresh sitting. t273 adds: owner INDEX byte +0x56 (NOT handle
  u16+0x54), and stale-echo pairs mint phantom deltas — per-segment trust only.
- WRITER CENSUS (t215): presence != writerhood — count /proc/<pid>/fd symlinks
  resolving to the capture file. Retiring orphans is a supervised decision.
- NO-SITTING CORROBORATION (t215/t216): also check the save axis (find ...
  -name '*.sav' -o -name '*.gam' with %T@ sorted desc); name the newest save by
  full ns, never wall-minute (10 s error bar).
- exit codes: 0 = base derived / formulas upgraded; 1 = normal negative, record
  ONE line, no in-turn retry; 2 = harness bug, fix it.

## Closed-as-dead capture routes (full trail: docs/REFUTED-ROUTES.md)
- external ptrace tracer: dosbox-x makes itself untraceable (ATTACH/SEIZE EPERM
  within 2 s) — dead on this box. SUPERSEDED for watchpoint work by the
  debugger build (docs/re/dosbox-debugger.md); do NOT re-probe ptrace.
- dfsg dosbox-x debugger: no command set at all (t272, every route measured).
  Superseded by the master build — verify the NEW binary, don't re-litigate.
- static absolute-base schemes: four refuted, fifth forbidden — the runtime
  pointer law (OQ-011 CLOSED) is the answer.
- title-menu glyph readouts (t57): the only density readout is glyph-rendered
  (R13), no needle exists — closed to default stars=50, do not re-probe.
