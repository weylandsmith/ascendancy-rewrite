# _wip_t214 — sitting adjudication ONLY (t213 assignment): NO SITTING, capture health measured

Task (docs/STATE.md NEXT ACTION t214, assigned by t213): run trigger-A triage on
`work/r1/playcap/live-timeline.jsonl`; if a sitting exists, run
`scripts/r1_t85g_sitting.py` and mine two named witnesses (multi-volley vs
non-at-war owner; mid-campaign slot V>1 with a nonzero `byte[star+0x15]`). If
no sitting: write the honest idle-wait line and STOP — no invented static work
(t212 law: re-running a censused instrument without new inputs is net-negative).

No steering note was prepended to this session's prompt. Tree clean at 7f0b00f
(t213) at session start; no dirt to adopt.

## S1 — TRIGGER-A: NO SITTING (scripts/r214_triage.py, RC=0)

All three frozen baselines re-verified byte-identical (measured this session):

| signal        | measured                  | baseline                  | eq  |
|---------------|---------------------------|---------------------------|-----|
| ns mtime      | 1793294532100000000       | 1793294532100000000       | yes |
| size          | 5,721,578,066             | 5,721,578,066             | yes |
| tail-64KiB md5| 9054cc6c66802e6f80431d4ffa1416ee | 9054cc6c66802e6f80431d4ffa1416ee | yes |

Corroborating negatives (same probe run / same session, all measured):
- `ps -eo comm,args`: ZERO processes whose `comm` starts with `dosbox`, zero
  `ascend.exe` in any cmdline. (An earlier `pgrep -f dosbox` "hit" was the probe's
  own shell command line matching itself — use `comm`-class matching for
  process-presence claims, not `pgrep -f`.)
- No `.sav` anywhere under `/home/hrethric` newer than 2026-10-29 14:00 outside
  `work/r1/playcap/save/` (that dir's newest = 60.sav 2026-10-29 13:22).
- `work/r1/playcap/caps/` empty. No game dir mounted (`mount` grep ascend/cifs/smb: none).
- Row count unchanged: 240,249 lines == t213's value.

=> No sitting. `scripts/r1_t85g_sitting.py` correctly NOT run (running it on the
stale shared dir is the t152 silent-wrong-input trap). Both named witnesses
remain unobservable this iteration.

## S2 — NEW, FOUND BY TRIAGE: FOUR LIVE WATCHERS ON THE SHARED CAPTURE DIR

`ps -eo pid,ppid,comm,etime` filtered on `r1_playcap_watch.py`:

```
pid 27772  ppid 1       bash     up 4-10:15   <- setsid wrapper (scripts/r1_playcap_vnc.sh:184)
pid 27774  ppid 27772   python3  up 4-10:15
pid 260988 ppid 1       python3  up 1-18:30   <- orphaned, up since 2026-10-28
pid 290953 ppid 1       python3  up 1-05:28   <- orphaned, up since 2026-10-29
pid 292085 ppid 1       python3  up 1-05:03   <- orphaned, up since 2026-10-29
```

Four distinct watcher INSTANCES (one wrapper+child pair, plus three processes
reparented to init) all pointed at the same capture dir. t115's law ("the pair is
the bash wrapper plus child, not a duplicate watcher") covers pid 27772/27774
only; 260988 / 290953 / 292085 are NOT explained by that law. They are live
(`--no-exit`, 5 s poll) and each appends to `live-timeline.jsonl`, which is why
`watch.log` shows the same `60.sav t=1086` line four times.

## S3 — WHAT THAT DOES AND DOES NOT BREAK (measured, controlled)

Measured on tail windows only (never the whole 5.7 GB file):

- tail-400: 400 raw rows collapse to **106** distinct `(file, file_mtime_ns)`
  keys -> **3.77x** inflation; 98 of 106 keys have >1 row, max reps 4 (matches
  the four-watcher count exactly). Reps differ only in `wall`
  (e.g. `44.sav` reps at 13:05:59 / 13:06:00 / 13:06:00 / 13:06:01).
- tail-1200: 436 distinct keys, 416 groups with >=2 rows, and **ZERO content
  conflicts** — every group's rows are byte-equal after dropping `wall`
  (scripts probe C method: dict-compare of all non-`wall` fields per key).

Consequences, stated precisely:
1. **Event-level mining is SAFE.** `r1_stream.build_index`
   (scripts/r1_stream.py:78-99) keys on exactly `(file, mtime_ns)` and drops
   repeats before yielding, and `observations(trust=True)` layers the stale-echo
   law on top. Since duplicate keys never disagree on payload (S3 measurement),
   first-wins is lossless for every field the miners read. So OQ-016/OQ-021
   witness mining via `r1_stream` was never corrupted by this.
2. **Raw-row arithmetic is NOT safe.** Any claim of the form "N observations",
   "68 sustained raw rows", or a rate/frequency computed from raw line counts in
   this file is inflated by up to ~4x (and non-uniformly: an autosave written
   while only two watchers were alive gets 2 reps, one after 2026-10-28 gets up
   to 4). Do not count raw rows as events for any post-t187 window.
3. **Growth-rate triage is still valid directionally but not quantitatively**:
   the file grows ~4 polls per autosave touch instead of 1; trigger-A keys on
   mtime/size/tail-md5, which only answer "did anything get appended", and the
   answer here is no.
4. **A capture-health check belongs in future trigger triage** — the cheap form
   is: distinct-`(file,mtime)` fraction of a tail window. 1.00 = single writer;
   ~0.25 = four writers. If a future sitting shows a collapse factor that CHANGES
   mid-window, key ordering across instances could interleave and the sorted-index
   order must be re-checked before trusting turn-boundary sequences.

## S4 — LEDGER DISPOSITION: no row moves, strict-close respected

Open set (scripts/ledger_index_check.py this session): OQ-005, OQ-016, OQ-019,
OQ-021 — 15 closed / 19 rows. Every residue is in exactly one of the three
classes t213 S7 declared (the classification is cited per row below, not new):
- **play-gated**: OQ-016 clamp witnesses (needs a battle vs a non-at-war owner),
  OQ-021 comparator firing (needs a real >50%-owned mid-campaign session).
- **BLOCKED-USER**: OQ-019 per-ship / per-commit attack-pricing modelling ruling,
  OQ-005 dims-location residue (80 recs / 31 files, docs/BLOCKED.md t68) and the
  index.txt eyeball decision (docs/OPEN-QUESTIONS.md:1293).
- **watchpoint-class**: OQ-021 displayed-count write site — dosbox-x binary IS
  installed (`/usr/bin/dosbox-x`), so the blocker is not tooling but the need for
  a supervised interactive session (a USER-APPROVED harness ask, not static work).

Nothing in S1-S3 closes a row: S1 is a negative about the corpus, S2/S3 are about
instrument health, not about any law. No plausible-default closure taken.

## S6 — INFLATION TIME-PROFILE (scripts/r214_inflation_profile.py, RC=0, full-file scan)

One streaming regex pass (no json.loads) over all 240,249 rows:

- rows 240,249 / distinct `(file, file_mtime_ns)` keys 56,377 -> overall
  collapse 4.26x. Per-key rep histogram:
  {1:13137, 2:9025, 3:4331, 4:6021, 5:7559, 6:3328, 7:2880, 8:2882, 9:2882,
  10:2882, 11:1152, 12:298}.
- Collapse per 4,000-row APPEND-ORDER chunk (the `wall` field is time-of-day
  with NO date — first draft binned w[-5:] and silently binned MM:SS; caught
  and fixed same session, pitfall banked): rises 1.96x (head, t37 era) ->
  plateau 4.6-4.7x -> 8.0-10.0x (chunks 37..47, up to ~12 writers) -> RESET to
  1.3-1.5x at chunk 48 (lines ~192k = new sitting start) -> back to ~3.7-5.1x
  by the tail; final chunk 3.66x.
- READING: watcher count ACCRETED through the capture's life (matching the S2
  uptimes) and at least one sitting-era had ~10-12 concurrent instances.
  Raw-row arithmetic from ANY window of this file is suspect at its own local
  factor — there is no single global correction constant.

## S7 — CLAIM-SAFETY AUDIT: banked counts were NOT inflated (verified)

Checked HOW every raw-count claim banked from this file was produced:
- t187 flight census (ships.md S20 "state4 x1115" etc) —
  scripts/r1_t187_delta.py:30 uses `r1_stream.observations(RUN, trust=True)`.
- t189 state-3 arbiter ("68 sustained") — scripts/r1_t188_state3_arbiter.py:20
  same trusted path.
- diplomacy.md S11 28k trusted observations, score.md S6 28k — same.
`build_index` (scripts/r1_stream.py:78-99) dedupes on exactly `(file, mtime_ns)`
before yielding, and S3 (tail-1200) measured ZERO content conflicts inside
duplicate groups (rows differ only in `wall`), so first-wins is lossless.
=> NO banked number needs restatement. The exposure is FUTURE: any new miner
that reads raw lines instead of `r1_stream.observations` will silently inflate
event counts ~4x (more if writers accrete again).
MINING LAW (banked here, canonical home for future reference):
  counts from live-timeline.jsonl come ONLY from r1_stream.observations;
  raw `wc -l` / grep-c numbers are writer-multiplicity artefacts; before mining
  a fresh sitting, run scripts/r214_triage.py (watcher census + tail collapse)
  and if the collapse factor STEPS mid-window, verify `r1_stream` sorted-index
  order before trusting turn-boundary SEQUENCES (dedup makes counts safe; it
  does not reorder writer-interleaved appends — the sort key is
  (file_mtime_ns, file), which is writer-independent, so order is in fact
  restored; the step check is belt-and-suspenders for the next capture).

## S8 — VERDICT / WHAT NEXT SESSION MUST DO

- t214 produced: (i) a re-verified NO-SITTING adjudication on three independent
  signals, and (ii) a NEW capture-health finding (multi-watcher multiplicity)
  with its blast radius measured and bounded — mining law banked, no ledger move.
- The only inputs that move the ledger are: a new sitting, or one of the two
  standing user rulings. Idle-wait is the honest state; inventing a census is the
  known failure mode (t212 law, t186 self-arming-trigger lesson).
- Do NOT kill the orphaned watchers as a side effect of research — that mutates
  the capture rig and belongs to a supervised session decision (a stray kill also
  cannot recover the lost distinct-event detail, only stop further duplication).
