# t222 — ninth consecutive byte-identical adjudication (idle, content-free by design)

Session started 2026-10-30T23:25:13Z. Assigned task: docs/STATE.md NEXT ACTION
= t222, the TRIGGER-ARMED idle check (two axes only, ~4-call cap, no new code
path). Hand-authored file; verified at t221 that no generator writes
docs/re/_wip_*.md (scripts/r1_idle_probe.py only reads them).

## S1 — Axis 1: no sitting (TRIGGER-A all three equal, 9th running)

`python3 scripts/r214_triage.py` RC=0 at 2026-10-30T23:25Z:

- ns_mtime 1793294532100000000 == baseline: True
- size     5721578066 == baseline: True
- tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline: True
- script's own verdict line: `=> sitting delta: False`
- game process census: dosbox/ascend.exe processes: 0
- tail shape healthy: 400 rows, 0 bad json, turn 1086, 275 distinct, one key shape

Baseline age recomputed independently this iteration (not carried over from the
STATE prose): baseline ns 1793294532100000000 == 2026-10-29T17:22:12.100Z,
session clock 2026-10-30T23:25:39Z ⇒ 30.058 h. Monotone against t221's 29.94 h
at 23:18:02Z (delta ~0.12 h ≈ the 7.6 min wall gap), so the age arithmetic in
the STATE chain is self-corroborating.

r1_t85g_sitting.py correctly NOT run (t152 trap: the sitting script is only for
a NAMED sitting dir, never for an idle adjudication).

## S2 — Axis 2: save axis bit-identical (watcher-death gap stays closed)

`find /home/hrethric -xdev \( -name '*.sav' -o -name '*.gam' \) -printf '%T@ %p\n' | sort -rn`:

- population 1409 files — unchanged since t216
- #1 playcap/save/41.sav  1793294530.108
- #2 playcap/save/60.sav  1793294520.040
- #3 playcap/save/59.sav  1793294510.004

Bit-identical to t216..t221. The newest save is still OLDER than the timeline
baseline (1793294532.100), gap 1.992 s — fourth consecutive re-measurement of
that figure. The failure mode this axis exists to catch (watchers dying and
hiding a sitting behind a newer save) did not occur. Zero saves since the
2026-10-29 13:22 end series.

## S3 — Adjudication and honest negative

NINE consecutive byte-identical adjudications stand (t214..t222). Both
adjudication axes are unchanged, and the watcher population is unchanged as an
incidental read of the triage script (wrapper 27772 bash / no writer fd, child
27774, orphans 260988/290953/292085 — no new orphans, no retirements, stable
~15+ h). Nothing killed: retiring watchers is a supervised-session decision.

HONEST NEGATIVE: no ledger row moved and none could. OQ-005, OQ-016, OQ-019,
OQ-021 all stay OPEN. With no sitting there are no witnesses, so the OQ-016
multi-volley clamp witnesses and the OQ-021 mid-campaign slot comparator remain
unobservable; OQ-019 and OQ-005 wait on a user ruling, not on measurement I can
take. Under strict-close an idle reproduction cannot close anything.

Deliberate restraint (t220's idle discipline, applied for a third iteration):
no new axis, no fd census, no static hunt (corpus formally EXHAUSTED at t213
S7), no out-of-band ledger re-audit — with no sitting the open set cannot have
changed, so re-printing the audit would be the tenth instance of the same
negative rather than a finding. Gate stage 3t runs both ledger checks anyway.

The next move remains new play or a user decision, not another research
iteration. Standing user asks are unchanged (play a few mid-campaign turns
attacking a NON-AT-WAR power + save; the OQ-019 per-commit attack-pricing
ruling; retire the three orphaned watchers before the next capture). Re-arm the
harness on the r214_triage trigger against the three baselines in S1.
