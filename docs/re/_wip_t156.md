# t156 WIP — IDLE re-check #43 + enact the timeline CONTENT baseline in the probe

## Session-start adjudication (RUN BEFORE EDITING, 2026-10-28 03:39:49, RC=0)
Trigger (A) NEGATIVE: newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns=1793043841304000000 size=5691796463 (== probe's own
BASE_MTIME_NS/BASE_SIZE at scripts/r1_idle_probe.py:70-71); zero dosbox procs;
find sweep (cutoff 03:38:08 session start) 4 files, non-loop none; A4 watcher
ALIVE pid 27774; A5 none (save/*.sav = 20, all match the watcher glob).
Trigger (B) NEGATIVE: clean tracked tree at 1767c28, no STEERING file, untracked
none inside and outside LOOP_OWNED, B3 HEAD == journal sha 1767c28 (journal row
77 ct 03:37:15, last tab field first token re-extracted by hand with
cat -A|cut outside the probe), prompt pair prompt-78 vs prompt-77 (58/58)
digit-stripped delta 0.
VERDICT printed "IDLE — neither trigger" => valid (clean tree at session start,
so the t155/B5 CAUTION path had nothing to demote).

## Independent re-verification (t147 near-miss law, all reproduced)
- stat -c '%Y %y %s' outside the probe: 1793043841 / 2026-10-26 15:44:01.304 /
  5691796463 — 46th consecutive byte-identical reading (t111..t156).
- t151 CONTENT baseline reproduced a FIFTH time: head 64 KiB md5
  42a0bed0507f9052e2009ec94e9c27f1, tail 64 KiB md5
  1529ab1ad70ac360f441d819703f943f; last row still the t1254 one
  (systems_any 36 / systems_full 32 / planets_mine 36 / T_known 50,
  file_mtime_ns 1793043836296000000, wall 15:44:01).
- Bank hygiene fresh: `grep -rln stop-report scripts/` -> only
  r1_idle_probe.py + its .pyc; gate.sh only ever `-s`/`grep -q` docs/re/*.md
  (lines 93-231), never writes stop-report.md; stop-report.md 1727 lines, zero
  diff vs HEAD before appending §49. Hand-authoring safe.

## THE FINDING — hole (B6): the t151 content baseline is documented, not enacted
Method (t145, generalised t155): ask what the leg DOES with its input, and
whether its adjudication reaches the line the caller reads.
- trigger_a's timeline leg (scripts/r1_idle_probe.py:92-98) compares ONLY
  st_mtime_ns and st_size against BASE_MTIME_NS/BASE_SIZE.
- `grep -c 'md5|hashlib' scripts/r1_idle_probe.py` -> 0. The two hex strings and
  the rule "tail-md5 match + moved mtime = a touch, not a sitting; differing
  tail-md5 = real ingest" live ONLY in STATE.md prose (added t151, quoted
  forwards t152/t153/t154/t155).
- CONSEQUENCE: a fresh session that arms on (A) and forgets the prose runs
  r1_t85g_sitting.py on the SHARED work/r1/playcap and prints the stale
  t1253/1254 sitting WITH alliance/ship/damage snapshots as if it were the
  user's new game — the exact t152 hazard, and there is no error and no dir
  echo on that path when the default is used.
- FIX: enact the baseline inside the growth leg — when mtime/size differ,
  compute the head/tail 64 KiB md5s and classify: content-identical (same size)
  => TOUCH, do not arm, print the verification; md5 differs => REAL growth, arm;
  unreadable => adjudicated=False, RC=2 (t147 law: absence of signal is not
  absence of event).
- SAFETY ARGUMENT FROM SOURCE (why the touch branch can never suppress a real
  sitting): the watcher appends — `jl = open(jlp, "a")`
  (scripts/r1_playcap_watch.py:146) — so a real ingest strictly GROWS the file.
  The demotion branch requires size == BASE_SIZE AND both md5s == the measured
  baselines, which an append cannot satisfy. Cost: head/tail 64 KiB md5 only on
  the arm path (dd/tail are seek-based; measured instant), never a full 5.7 GB
  hash, so the t151 "never md5 the whole file" law holds.
STATUS: patch pending; fixture matrix planned (classify on synthetic pair +
end-to-end sparse-file arm via R1_TIMELINE override + real-state control).
