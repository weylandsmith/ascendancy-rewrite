# t257 WIP — WATCHER SCHEMA + DAY FIELD

## S1 PREMISE (verified this session, 2026-11-01 ~15:05)
- Assignment: STATE.md "## NEXT ACTION" = t257, branch 1 (t249b DID pin the day
  dword). Implementation form mandated by the t249b note: `"day": turn` — pure
  alias, no second RAM read, no new scan.
- t249b law (docs/re/selfplay.md:226-252): the 7-segment readout IS the turn
  counter zero-padded to 5; dword==turn intersects to exactly three sites
  (member 0x254e98 == turn X=0x12e10 + two heap addresses); ZERO data-seg day
  scalar in both sessions; vendor gauge text equates day==turn.
- Live row shape MEASURED before any change (tail -n 3 of
  work/r1/playcap/live-timeline.jsonl): 16 keys
  {T, T_known, file, file_mtime_ns, in_game, planets_mine, rank, relation,
   score_stars, selector_byte, ship_raw, ships, systems_any, systems_full,
   turn, wall}, rows t=1255 file 43/44.sav wall 15:02:2x.

## S2 CORRECTION TO THE QUEUE TEXT (honest negative, banked before editing)
- The queue claims "r214_triage asserts ONE key shape". FALSE as stated:
  scripts/r214_triage.py tail_shape() (lines 92-121) only COUNTS keysets
  (collections.Counter) and PRINTS the top 4. There is no assertion, so the
  alias cannot break it. Branch 2 ("fold the candidate list forward") is
  therefore NOT triggered; branch 1 stands.
- The real hazard branch 2 gestured at is multiplicity, not the assertion:
  EIGHT python watcher processes are alive on the same OUT dir
  (27774, 260988, 290953, 292085, 449921, 457638, 462206, 479983 — ps
  ppid-checked this session; wrappers 27772/457636/462204/479981 bash).
  Each dedups independently, so after the relaunch the file will MIX 16-key
  rows (old in-memory code) and 17-key rows (new code) until the orphans are
  retired. Retiring them is the user's call (STATE.md:271) — NOT taken here.

## S3 CHANGE MADE
- scripts/r1_playcap_watch.py process(): d["day"] = d["turn"] immediately
  after S.read_slot, with the t249b citation; module docstring schema note
  updated 16->17 fields with the alias law (so a future mining run reading
  the docstring is not misled into thinking day is an independent counter).
- scripts/r214_triage.py: docstring claim corrected + tail_shape now flags
  shapes that differ ONLY by the "day" key as the same schema (alias law),
  and prints the day/turn agreement census for the tail window.
- No rewrite/ semantic change; no pin (pins freeze laws, not schemas — t256c
  precedent). No OQ row touched.

## S4 VERIFICATION (scratch, never the live dir for --once) — DONE
- `python3 -m py_compile` clean on both scripts. Scratch run: copied
  bank-t251-live1255/41.sav,42.sav into /tmp/t257scratch, ran
  `r1_playcap_watch.py /tmp/t257scratch --once` from repo root -> 2 rows,
  17 keys each, day==turn==1255, agree=True.
- LIVE relaunch mechanics MEASURED: first relaunch attempt via terminal
  background=true left the process tied to the session wrapper (513473/513481)
  — killed it and relaunched detached the proven way:
  `subprocess.Popen(..., start_new_session=True, stdin/stdout/stderr=DEVNULL)`
  -> pid 513605, ppid 1, own session, 98 MB steady. pid recorded in
  work/r1/playcap/watch-t257.pid. The reaped sitting pair was 479981/479983
  (the only pair owned by the current :9 dosbox, /proc cmdline-validated
  before kill per the t85b reaper law); orphans 27774/260988/290953/292085/
  449921/457638/462206 left running per STATE.md:271 (user's call).
- Startup-cost law LEARNED: a relaunch streams the whole 7.4 GB timeline to
  rebuild `seen` (~2-3 min, line-by-line, bounded RSS) BEFORE its first
  emit — "no new rows within 30 s of launch" is NOT a failure signal for the
  new watcher; check the `watch: start` line in watch.out first (appeared
  15:13:04, first day-row 15:14:01).
- POST-RLAUNCH CENSUS (r214_triage tail_shape, last 400 rows): 7x 17-key rows
  all day==turn (disagree=0), 393x 16-key rows from the still-live orphans —
  exactly the predicted MIXED-SHAPE window. Canonical (day-folded) shape is
  ONE identical 16-field shape across all 400 rows, so multiplicity math stays
  valid during the transition. New rows verbatim-checked:
  {53,54,55}.sav wall 15:14:0x, day=1255=turn.

## S5 DISPOSITION
- No rewrite/ semantic change, no pin (schema, not law — t256c precedent).
- No OQ row touched; strict-close honest negative: this iteration closed
  NOTHING (the day question was already closed-banked by t249b; t257 was
  harness plumbing). OPEN-QUESTIONS untouched (005/016/019/021 stay open).
- Files touched: scripts/r1_playcap_watch.py, scripts/r214_triage.py,
  docs/re/selfplay.md (t257 note under t249b), docs/STATE.md.
- Queue status: t257 DRAINS the queue; STATE.md carries a freshly authored
  queue (t258 OQ-021 discriminator) per the AFTER-DRAINS instruction.
