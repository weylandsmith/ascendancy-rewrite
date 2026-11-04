# _wip_t231 — idle adjudication, eighteenth consecutive (2026-10-31T00:46Z)

Generator safety (t226 rule): nothing regenerates this file. Verified again by the
grep recorded at t228/t230 — `gate.sh:373` mentions `_wip_` only inside a comment,
and `scripts/r1_idle_probe.py` L50 / L361 / L373 / L389 treat `docs/re/_wip_*.md`
as informational / the loop's own untracked files (reads only). This file is
hand-authored and committed as-is.

## S1 — Axis 1: TRIGGER-A baselines unchanged (eighteenth iteration)

`python3 scripts/r214_triage.py` RC=0 at 2026-10-31T00:45:58Z:

    ns_mtime 1793294532100000000 == 1793294532100000000: True
    size     5721578066          == 5721578066          : True
    tail md5 9054cc6c66802e6f80431d4ffa1416ee (64 KiB)  : True
    => sitting delta: False

Zero comm-class dosbox/ascend.exe processes. Tail healthy: 400 rows, 0 bad json,
turn 1086, 275 distinct, a single 16-field key shape
(T,T_known,file,file_mtime_ns,in_game,planets_mine,rank,relation,score_stars,
selector_byte,ship_raw,ships,systems_any,systems_full,turn,wall).

Per the t152 trap the sitting script (`r1_t85g_sitting.py`) was NOT run — with no
delta there is nothing to adjudicate and running it manufactures a capture.

Baseline age independently recomputed (not copied from STATE): baseline ns
1793294532100000000 == 2026-10-29T17:22:12.100 UTC → 113026 s = **31.396 h** old at
00:45:58Z. Monotone against t230's 31.2489 h at 00:37:08Z: Δ = 0.147 h against an
8 m 50 s (0.1472 h) wall gap ✓ — the age series is self-consistent, so the baseline
is genuinely static rather than being silently rewritten.

## S2 — Axis 2: save axis bit-identical (thirteenth time)

    find /home/hrethric -xdev \( -name '*.sav' -o -name '*.gam' \) -printf '%T@ %p\n' | sort -rn | head
    (+ a separate count pass)

Population **1409** files (unchanged since t216).

    1793294530.108  playcap/save/41.sav   <- newest (t216 ns-precision law: by ns, never wall-minute)
    1793294520.040  playcap/save/60.sav   (10.07 s older — NOT the newest)
    1793294510.004  59.sav   1793294500.004  58.sav   1793294489.988  57.sav
    1793294479.980  56.sav   1793294469.964  55.sav   1793294459.956  54.sav
    1793294449.944  53.sav   1793294439.952  52.sav

Newest save remains OLDER than the timeline baseline → the watcher-death gap stays
closed (a save newer than an unchanged timeline would mean the writers died).
Gap baseline−newest = **1.992 s**, re-measured the thirteenth consecutive time.

## S3 — Honest negative: nothing closed, nothing new manufactured

No sitting → the four open witness classes are unobservable. Under strict-close
**no row moved**: OQ-005 / OQ-016 / OQ-019 / OQ-021 stay OPEN;
`docs/OPEN-QUESTIONS.md` untouched. `ledger_audit.py` was NOT re-run out-of-band
(no sitting ⇒ the open set cannot have changed); it ran only as a gate stage,
together with `ledger_index_check.py`.

The ~4-call cap held: exactly the 2 assigned axis calls before the finish
sequence. No new code path, no fd census (writer population stable at exactly
FOUR open fds on live-timeline.jsonl t215..t230 per t215's fd-level law), no
static hunt (corpus formally EXHAUSTED at t213 S7), and no re-print of the same
negative dressed as a finding.

Watcher population unchanged: wrapper 27772 (bash, ppid 1, holds no writer fd) +
child 27774 (python3, ppid 27772) + orphans 260988 / 290953 / 292085
(all python3, ppid 1, `--no-exit`). No new orphans since t215, no retirements.
Nothing was killed — retiring them is a supervised-session decision.

CONCLUSION (unchanged from t218..t230): an idle iteration cannot move the ledger.
The next move is new play (USER ASKS in STATE.md) or a user decision, not another
research iteration.
