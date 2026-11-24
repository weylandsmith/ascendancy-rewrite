# tPL-B1c — mutation-prove the new placement pins (LANDED 2026-11-23)

Task: run scripts/t418b_mutate.py M8..M17 against rewrite/src/ui/planetview.cpp;
CAUGHT required for every mutant (MISSED => pin weak, fix pin + re-run).

Pre-flight [verified 2026-11-23]:
- git clean at 0925966 (tPL-B1b shipped).
- /tmp/t418b_planetview.orig.cpp md5 == rewrite/src/ui/planetview.cpp md5
  (91932a9704d412c91c476183bc344b07) — snapshot is the CORRECT post-tPL-B1b
  file, not poisoned. Restore law: script copies snapshot back + os.utime;
  NEVER git checkout mid-campaign.
- Script keys build at WORKING path, reads anchors from SNAP (rule 8c safe
  since SNAP==working verified).
- Sitting check ran FIRST this iteration (r1_t85g_sitting exit 0; playcap tail
  rows all turn=1086, newest wall 20:34 — no new trusted turn-change; stale
  assignment stood). Production dosbox-x still alive (pid 1470999).

## Verdicts — MUTATION 10/10 CAUGHT (suite 501; failing pin every time =
planetgrid_placement_t418b; AFTER-RESTORE 501 tests, 0 failed)
- M8 rock veto deleted (0x38519)        CAUGHT 3 failed (L233 dig@0, L281 normal@rock)
- M9 exempt set {5,35}->{6,39} (0x385f6/ff) CAUGHT 2 (L229 item5, L230 item35)
- M10 row-1 probe lost                  CAUGHT 2 (L316 kNbr0 neighbour, L369)
- M11 POLARITY INVERSION active->refuse CAUGHT 2 (L316, L369) — the t418b bug
  re-introduced is caught by the re-derived pin: pin encodes the RAW law.
- M12 all-inactive -> pass (0x386fc)    CAUGHT 4 (L225, L302 terraform@surf-2)
- M13 XOR polarity flipped              CAUGHT 15 (L225, L229, ...)
- M14 XOR bound 31->22 (0x384e0)        CAUGHT 1 (L244 item22@0 == SurfaceVsRing)
- M15 ring domain lost                  CAUGHT 3 (L237, L239)
- M16 terraform barren arm lost         CAUGHT 2 (L295 ring, L300 surface)
- M17 own-skip deleted (0x385ee)        CAUGHT 1 (L263 own@0 == None)

Conclusion: the tPL-B1b pins (planetgrid_placement_t418b +
orders_cellless_bit1_t418b) encode every cited branch of the corrected
placement chain FUN_0003830c — grant-accumulator vetoes (XOR surface-vs-ring
item<31, rock/dig XOR, terraform barren leg), the ADJACENCY POLARITY
(active = legal, all-inactive = refuse), the ring-domain gate, the exempt set,
and the own-active skip. No pin is vacuous; no separator missing.

## Notes / triage
- HAZARD RECORDED (skill-consistent, new variant): a background launch with a
  typo'd argument list (duplicate M12/M15) was killed mid-M8 via
  process_manage kill; SIGTERM left the MUTANT ON DISK (md5 differed from
  snapshot). Recovery per skill rule 8b(i): diff vs /tmp snapshot, restore by
  copy + touch, rebuild green BEFORE relaunching. md5-compare-then-copy is the
  cheap catcher — do it after ANY killed campaign.
- Sweep cost ~13 min for 10 mutants (rebuild+suite ~78s each) in ONE background
  session with notify; no foreground timeout touched (skill rule 8).
- No OQ row touched (tPL tracks none). Honest negative under strict-close:
  open=[016,019] unchanged.
