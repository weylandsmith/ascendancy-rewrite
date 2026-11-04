# t149 — IDLE re-check #36 (2026-10-28 01:48 EDT) — WIP

## Verdict (banked FIRST, before any further probe)
`python3 scripts/r1_idle_probe.py` @ 01:47:58 -> **RC=0, IDLE**, both triggers
negative. Session-start cutoff 2026-10-28 01:47:06 (from iter-20261028-014706-71.log).

(A) NEW CAPTURE — NEGATIVE, fully adjudicated:
  - newest playcap dir playcap-20261014-224611 (unchanged)
  - live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B
    == frozen baseline (r1_idle_probe.py:54-56). 39th consecutive
    byte-identical reading t111..t149.
  - INDEPENDENT RE-STAT (t147 law, run outside the probe):
    `stat -c 'mtime_ns=%y size=%s'` -> 2026-10-26 15:44:01.304000000 -0400 /
    5691796463 — exact match, zero divergence.
  - dosbox procs none; find sweep work/r1 -newermt cutoff -> 4 files, non-loop none.
  - A4 watcher ALIVE pid 27774; deeper liveness read outside the probe:
    /proc/27774 wchan=hrtimer_nanosleep, State S (sleeping) — i.e. parked in the
    5 s poll sleep, not wedged in I/O; fd table: 1,2->watch.out 3->live-timeline.jsonl
    4->watch.log (all four capture artifacts open for append).
(B) USER DECISION — NEGATIVE:
  - clean tracked tree at 082866b; git diff HEAD --name-only empty; status
    --porcelain (tracked) empty; untracked none; delta outside loop-owned none.
  - STEERING file none.
  - B3 HEAD == journal sha 082866b (journal row 70 tail verified independently:
    "2026-10-28 01:46:12 | 70 | OK | 0 | (re-check | 082866b t148: ...").
  - prompt pair prompt-71.txt vs prompt-70.txt (58/58 lines): digit-stripped
    delta 0 -> no prepended steering note.
=> No ledger row closed (strict-close: an idle turn produces no cited
   measurement). §3 answer outstanding after thirty-six idle turns.
   t113 LOOP-END PROPOSAL stands.

## VALUE-ADD 1 — the collector is FUNCTIONAL, not merely alive (measured)
t147's A4 leg proves the watcher PROCESS is up. It cannot prove the process
would still record a sitting. Direct functional test, scratch-only, live
timeline untouched:
  rm -rf /tmp/t149-watch && mkdir -p /tmp/t149-watch/save
  cp work/r1/playcap/save/41.sav work/r1/playcap/save/42.sav /tmp/t149-watch/save/
  python3 scripts/r1_playcap_watch.py /tmp/t149-watch --once      # cwd = repo root
Result (real execution 01:53:38, RC=0):
  `41.sav t=1254 SYSTEMS mine_any=36 full=32 planets=36 | DAT_482fb=14/50 sel=0 ships=38 rel_nonzero_cells=12`
  `42.sav ...` identical values; /tmp/t149-watch/live-timeline.jsonl = 2 rows,
  both valid JSON with file/turn/T/score_stars/in_game=true/systems_any/
  planets_mine/ships(38)/file_mtime_ns populated.
Second `--once` pass over the same dir: "start ... (2 prior observations
deduped)", 0 new rows, file still 2 lines => the t85b jsonl-derived `seen` dedup
law HOLDS (no 73k-dup regression).
Post-run re-stat of the LIVE timeline: unchanged (15:44:01.304 / 5691796463).
Conclusion: trigger (A)'s reporting path is live AND working end to end
(payload load -> anchor cache -> base vote -> slot parse -> JSONL append), so a
new sitting really would be captured. This is the strongest (A)-negative
position since the loop went idle: t147 fixed falsifiability, t149 demonstrates
function.

## VALUE-ADD 2 — a real asymmetry in the watcher's slot glob (measured)
`r1_playcap_watch.py:161` polls `glob(out/save/*.sav)` — LOWERCASE only.
  - All 20 ring slots under work/r1/playcap/save are lowercase `NN.sav` and all
    20 are valid dosbox save-state ZIPs (`zipfile.is_zipfile` 20/20), so the
    game's own writes match the glob: NO live blind spot for game-produced
    evidence today [verified].
  - But a hand-placed copy with an uppercase extension is invisible to the
    collector: `work/r1/playcap/evidence_slot04_t1254.SAV` is uppercase AND
    outside save/, and `zipfile.is_zipfile` on it returns False (raw memory
    dump, first bytes 346 004 \0 \0 ...), so it is a different artifact shape
    entirely (referenced by scripts/r1_t87_gizmo_table.py), not a ring slot.
  - Blast radius if a user ever copies a `.SAV` into playcap/save/: the watcher
    would never ingest it (leg 2 of (A) wouldn't grow) and leg 1 wouldn't fire
    (no new playcap-<ts> dir); only the find sweep would see it, and only if it
 landed after session start. Declined to change the glob in the LIVE watcher:
 making it case-insensitive requires killing pid 27774 and relaunching via
 scripts/r1_playcap_vnc.sh, which trades a provably-inert asymmetry for a
 live risk of an un-adjudicated watcher (the exact t147 failure shape). The
 cheap fix lands instead as a probe leg that notices un-ingestable save files.

 ## FIX LANDED (post-verdict, same iteration)
 The functional run armed trigger (A) by itself: it refreshed
 work/r1/.anch-cache.json (r1_slot.anchors_cached, r1_slot.py:49) and the
 find-sweep reported `non-loop: ['work/r1/.anch-cache.json']` -> VERDICT RE-ARM,
 RC=1. That is a pre-existing self-inflicted false positive for ANY analyzer run,
 which STATE.md had declared an artifact but the code never encoded. Fixed with a
 TOOL_ARTIFACTS exclusion in trigger_a()'s sweep.

 A5 leg landed in scripts/r1_idle_probe.py (walk playcap, skip caps/ and loop/,
 report save-looking files the watcher glob cannot read; CAUTION not trigger).
 Guard: only valid save-state ZIPs with a "Memory" member count, so the raw
 memory excerpt evidence_slot04_t1254.SAV is not permanent noise.

 VALIDATION (real executions; /tmp fixtures deleted after):
 C1 all-lowercase valid slot      -> "none (save/*.sav = 1, all match...)"
 C2 + uppercase VALID-zip .SAV    -> flagged (real blind spot)
 C3 + non-zip .SAV at root        -> correctly NOT listed (only 42.SAV shown)
 C4 uppercase removed             -> back to "none"
 real state (after patch)         -> RC=0, "A5 ... none (save/*.sav = 20,
                                   all match the watcher glob)", VERDICT IDLE
 One self-inflicted patch bug caught by running the tool: dropped closing quote in
 the find-sweep line -> SyntaxError line 112; repaired and re-verified with
 `python3 -m py_compile` plus the full matrix.

 GATES: bash scripts/gate.sh -> GATE_EXIT=0. python3 scripts/ledger_audit.py ->
 rows=18 open=['OQ-003','OQ-005','OQ-016','OQ-019','OQ-021','OQ-023'] closed=12,
 LEDGER AUDIT OK. Post-gate re-run of the probe: FINAL_RC=0, IDLE. NO ledger row
 closed (strict-close honest negative).
