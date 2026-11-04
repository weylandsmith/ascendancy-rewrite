# t162 — IDLE re-check #49 + P0 checksum-grader audit

Session start 2026-10-28 05:36:18, HEAD 506d825 (t161).

## Triggers (session start, before any edit)
- (A) NEGATIVE — probe RC=0: newest playcap dir playcap-20261014-224611;
  live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B; (A6) content
  baseline reproduced an 11th time head 42a0bed0507f9052e2009ec94e9c27f1 / tail
  1529ab1ad70ac360f441d819703f943f (dd/tailc hand path, size re-stat 5691796463),
  last row still t1254; zero dosbox procs; find sweep 4 files non-loop none;
  A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
- (B) NEGATIVE — clean tracked tree at 506d825 at session start (verdict wording
  "IDLE — neither trigger" valid per t155/B5), no STEERING, B3 HEAD == journal
  sha 506d825 (journal row 83 ct 05:33:44, OK, fail_streak 0), prompt pair
  prompt-84 vs prompt-83 (58/58) digit-stripped delta 0.
- ledger_index_check: LEDGER INDEX OK (record open == index open, 19 closed ids).

## THE AUDIT TARGET (t161 SET-PAIRS law applied to the P0 grader)
gate.sh stage 1 (scripts/gate.sh:12-16) is the ONLY enforcement of the top NEVER
("never modify game/"). Ledger family audited t157..t161; checksum grader never
audited in 161 iterations. Read from source:

  MAN="$ROOT/docs/BASELINE.sha256"
  if [ ! -f "$MAN" ]; then (cd "$ROOT/game" && sha256sum * > "$MAN") && note "created baseline manifest"; fi
  (cd "$ROOT/game" && sha256sum -c "$MAN" --quiet 2>&1) | grep -v ': OK' && err "game/ files modified!"

Static reads (measured, pristine tree untouched):
- game/ is FLAT: 0 subdirs, 0 dotfiles, 0 nested files, 0 unreadable files;
  disk files = 23 == manifest lines = 23 (today the leg covers everything).
- docs/BASELINE.sha256 is git-TRACKED since seed commit 3792dc5 (so tampering is
  revertable, but revertable != detected; gate.sh verifies no hash OF the manifest).
- Manifest regen source is the shell glob `*` — a CORRUPTED game/ regenerates a
  blessed baseline (self-healing grader) if the manifest is ever absent.

Candidate blind directions (all three are the t161 "legs built from what drifted
last time" shape — this leg was built for content mutation only):
  1. listed file DELETED from game/ -> sha256sum -c behaviour unmeasured;
  2. NEW file ADDED to game/ -> never compared against a set;
  3. MANIFEST tamper/regen -> no self-integrity leg.
All three graded GREEN today would mean the P0 invariant is enforced for
modification only, not for the whole set.

## MEASURED (scratch copy under work/r1/t162-p0check, pristine never touched)
- T0 control (23/23): silent. T1 DELETE jammer.dig: ARMED ("FAILED open or
  read" -> grep -> err). T2 ADD NOTES.TXT: ZERO signal — nothing enumerates
  disk->manifest. T3 manifest absent: gate REGENERATED from the glob, blessing
  the tampered tree (24 entries incl. NOTES.TXT) — passes forever after.
- Static: game/ flat (0 dirs/dotfiles/nested/unreadable); manifest set == disk
  == 23 (comm -3 empty); manifest git-tracked since seed 3792dc5.
- FIX (scripts/gate.sh stage 1): absent manifest = hard err + restore-from-git
  instruction (regen path deleted); second direction LC_ALL=C comm -3 of
  manifest names (awk substr($0,67)) vs find -maxdepth 1 -type f, any delta ->
  err. Five branches validated by real execution on stage-1 code extracted
  VERBATIM from the patched file: F0 flag 0 silent; F1 names NOTES.TXT only;
  F2 both legs fire; F3 errs with NO regen; F4 tampered-hash errs. Fixture
  traps banked (not gate bugs): running extracted stage-1 code standalone
  needs note()/err shims
  (RC=127 near-miss), and LC_ALL=C on sort but not comm dumps ALL 23 names as
  unpaired (23x noise buries the real delta) — comm pinned to C.
- Full gate bash scripts/gate.sh GATE_EXIT=0, zero FAIL lines, "ALL CHECKS
  PASS (milestone=6)" with the new leg running; ledger_audit LEDGER AUDIT OK;
  pristine game/ re-verified clean. Fixtures deleted.
- Bank hygiene: stop-report.md zero diff vs HEAD at 2113 lines pre-append;
  §55 appended (2158 lines).

## CONCLUSION
No ledger row closed (strict-close honest negative — grader hardening, not
measurement). Trigger (A)/(B) both negative at session start. P0 invariant is
now enforced bidirectionally (content AND set AND baseline-existence) by gate
stage 1, which every loop exit traverses — enforcement, not suggestion (t158
law: the leg IS in gate.sh).

