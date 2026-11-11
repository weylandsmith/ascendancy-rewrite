# _wip_t373.md — t373 REPO HYGIENE EXECUTION working record (2026-11-11)
Hand-authored; no generator names this file (S5 control re-run PASS this
session: grep over scripts/*.py|*.sh = 0 writers of LICENSE/NOTICE/README/
packaging; root LICENSE/NOTICE did not exist at session start).

## Steering check (pre-task, per NEXT)
- r369_playwindow exit 0, lo_ns UNCHANGED 1794373326560000000 (t370 window).
- Ring: t368_ring_turn parsed=20/20 max_turn=1254 (same turn as
  bank-play-20261111-t372 taken 03:58:40). Post-bank span via
  r370_slot_events (lo=1794387520560000000): frames=94 wall 03:58:48->04:13:52,
  events=0 — user idle since ~02:22, nothing new to witness. t373 stands.

## DONE this iteration
1. LICENSE installed: install -m644 /usr/share/common-licenses/GPL-3 LICENSE;
   ASSERT PASS both anchors (md5 1ebbd3e34237af26da5dc08a4e440464, sha256
   3972dc97...36986) measured on LICENSE itself post-install.
2. NOTICE installed from _notice_draft_t372.md via tail -n +5 (strip 4-line
   draft-comment header): 2417 B, sha256
   2e5f4153f90632b448bab4761f064867a18be6cb35645c1794ee9ee98a5dd3bf.
   Copyright line keeps <TBD-t373: repo author name> — author identity is
   USER-gated (license draft S7); GitHub push stays user-gated.
3. MEASUREMENT resolving packaging.md S9(b): cob.py extract IS a complete
   one-command importer for all three archives (the "compressed side" works):
   ascend01 -> 328 files, ascend02 -> 89 files (to /tmp/t373x_*), and
   `diff -r /tmp/t373x_ascendNN extracted/ascendNN` = 0 differing lines
   (ascend00 tree = 54 files, gate-checked). README TBD becomes cited fact.
4. Landmine defuse (decision per packaging.md S3 discretion):
   - git mv work/r1/t368_ring_turn.py -> scripts/t368_ring_turn.py (HERE-relative
     sys.path/ROOT patched for new depth)
   - git mv work/r1/sentinel_t369.sh -> scripts/sentinel_t369.sh (absolute
     REPO= path inside; no change needed)
   - git rm --cached work/r363_gizmo_census.out work/r363_gizmo_rows.json
     (evidence stays ON DISK; regenerable by scripts/r363_gizmo_census.py;
     r363_gizmo_census.py reads work/r363_gizmo_rows.json at runtime and is
     inert on fresh clones anyway — it needs work/r1/playcap saves)
   - target invariant: `git ls-files work/` prints NOTHING.
   - no running process held either moved file (ps checked); loop harness
     references them only in comments.
   - prose refs to update: STATE.md sitting-check line, docs/BLOCKED.md:207,
     docs/re/packaging.md S3, docs/re/ships.md:2916 (census.out path stays
     valid as a path-on-disk; annotate only if cheap).

## PENDING (rest of checklist)
5. SPDX sweep 504 files (rewrite 82, scripts 418+2 moved=420, tools 3;
   archive SKIPPED; work leaves set via untrack). Scripted insert: after
   shebang if line1 starts '#!', else line 1; '//' for c/cpp/h(pp), '#' for
   py/sh. Verify grep -L empty + gate green.
6. gate.sh --portable: PORTABLE flag; vendor stages skip-with-note when
   game/ absent; ASCENDANCY_DATA=DIR -> ln -sfn $ASCENDANCY_DATA/game
   $ROOT/game (only when absent; probes hardcode ROOT-relative game/ paths,
   symlink is the only uniform mechanism — documented side effect on clone);
   guard 3r attribution with command -v revenv (t343 fresh-clone gap:
   ungated $HOME/tools/revenv/bin/python would hard-fail a clone lacking it).
   VERIFY on this box: fresh clone /tmp + --portable exit 0 (with AND without
   ASCENDANCY_DATA).
7. Quote audit S9a: scripts/r373_quote_audit.py — longest consecutive-line
   verbatim vendor span per docs/re/*.md vs extracted text corpus; results
   into packaging.md.
8. README swap from _readme_draft_t371.md (strip draft header), TBD edits:
   ascend01/02 -> cited working flow (item 3); Windows vcpkg stays an honest
   limitation (no vcpkg on box, negative (c) unchanged); author contact TBD
   stays user-gated.
9. packaging.md landing notes; STATE.md NEXT -> WAIT-USER-RULING sentinel
   (queue: after t373 the OQ rows close ONLY on user ruling); LANDED block;
   gate + ledger audits + commit.
