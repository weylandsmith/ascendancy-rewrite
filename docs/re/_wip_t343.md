# _wip_t343 — PORTABILITY AUDIT + ARTIFACT CLOSURE (working notes, stream-as-I-go)

## Clone gate test (item 2)
- Tool: scripts/r343_clone_gate.sh (file:// clone, zero network, saves verbatim
  gate output to work/r343/clone-<label>-gate.out).
- RUN1 (pre-fix gate.sh, 2026-11-08 ~14:05): /tmp/ascend-t343-a, exit 0.
  Verbatim skips in the clone:
    * "note: no R1 save-state captures present (work/r1/r1sav-*); pointer-law battery skipped"
    * "note: no R1 save-state captures present; star-table battery skipped"
    * "note: work/ascend_restored.bin absent ...; attribution skipped"
    * "[gate] Xvfb/ImageMagick/revenv unavailable: skipped intro pixel check"   <- MISATTRIBUTED, see below
    * "[gate] xvfb-run unavailable: skipped UI smoke"                            <- MISATTRIBUTED
    * "[gate] xvfb-run unavailable: skipped audio smoke"                          <- MISATTRIBUTED
  Binary WAS built from scratch in the clone (ascendancy + run_tests, 14:06) but
  only at stage '4-5' (gate.sh:519), AFTER smokes 4e/4c/4d.
- BUG MEASURED (confirms pairing-session finding): the smoke guards are
  `[ -x binary ] && command -v xvfb-run` with a single else-note naming only
  xvfb-run. On a fresh clone the FIRST conjunct fails, so the note blames the
  wrong cause AND the stage self-skips. Three stages affected: 4e (~361),
  4c (~405), 4d (~471).
- FIX: hoist the milestone-gated build block before the first build-dependent
  stage; split the else-notes to name the actual missing prerequisite.
- RUN2 (post-fix): fresh clone, SINGLE run must execute UI/audio/pixel smokes.

## Artifact closure (item 1)
- artifacts/ascend_restored.bin (md5 b3cc18929cfe4bb86700164efb2bc143, 576643 B)
- artifacts/functions_full.tsv (md5 706a25c1dd21f0496e3a73dec0319b97, 10901 B,
  header 'file_off\tsize' + 1144 rows, sizes HEX per planets-ui.md pitfall)
- validation tool: scripts/r343_artifact_validate.py (V1 rebuild determinism vs
  captures, V2 Watcom start density of restored pointer runs vs control,
  V3 tsv structural parse). Results appended below when run.

## Provenance (verified on disk / archive)
- ascend_restored.bin: scripts/r1_restore_sites.py (STATE archive L220:
  "validation: pointer runs >=8 hit Watcom starts 60% vs 15% control").
- functions_full.tsv: ghp5/ascend5 full-analysis Ghidra export
  (docs/re/r1-savestate.md ~L437: 1,144 functions, base 0x100000 import,
  postScript ExportFunctions.java).

## Session-continuation notes (banked after items 1-3, ~15:20)
- RUN2 (working-tree gate.sh on clone /tmp/ascend-t343-b): exit 0, binary built
  EARLY, and the diff run1-vs-run2 of skip-notes is EXACTLY the three
  misattributed lines disappearing (UI smoke, audio smoke, intro pixel check
  all RAN — xsend click line present in run2 output). work/r343/clone-run2-gate.out.
- ARTIFACTS COMMITTED as a tracked COPY under artifacts/ (not git add -f on
  work/ paths — cleaner; README states the supersession). Validation tool
  scripts/r343_artifact_validate.py exit 0:
  V1 code-window byte-identical vs rebuild from r1sav-20261011-213606 slot
  46.sav; 9 bytes/3 groups differ in DATA region (0x8bed0/0x8bedc/0x8bee4,
  capture-dependent class drift — documented, not a failure).
  V2 restored-link-time-sites population: 575/1039 = 55.3% start-byte vs
  15.6% control (3.55x). NOTE the naive "aligned self-pointer" population
  measures 21.6% and CANNOT pass the 2x bar — population definition matters.
  V3 tsv OK (1144 fns, hex sizes, 904 overlaps known).
- PAYLOAD DERIVATION MEASURED: game/ascend.exe[0x2a50:0x2a50+0x8cc83] ==
  work/ascend_payload.bin EXACT (576,643 B). attribution_scan.py now derives
  it when the work copy is absent, prefers artifacts/ascend_restored.bin, and
  mkdir -p's work/ for its tsv; gate 3r guard widened. Fresh clones with the
  game dir now RUN the attribution stage (was: skip).
- RETRACTIONS: docs/re/retractions.md, 24 entries, each verified against the
  citing doc this session (file:line given, anchors named). The t31/t32 pair
  found at archive OPEN-QUESTIONS ~L1106 ("old t31 numbers RETRACTED",
  income-law T33); t47 labels at ships.md t101 block L346 + archive OQ ~L1588.
  combat.md ~L467 still prints the narrow ah>=4 form — flagged in entry #15.
- PORTABILITY: docs/re/portability.md reading order formats->tables->worldgen
  ->economy->combat->dip->victory->AI, each step law-file + gate/pin, plus
  NOT-portably-known section (open rows, capture-limited class, box-limited
  gates).
- Ledger: NO row closes (audit task per assignment). audits green.
- RUN3 PENDING: clone the COMMITTED tree (artifacts/ tracked) and verify a
  SINGLE gate run runs everything runnable (the assignment's third-clone bar).
