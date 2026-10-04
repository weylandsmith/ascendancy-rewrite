# BLOCKED — one question for the user

Date: 2026-10-04. One question. Everything else proceeds under the stated
default; this file records the fork, not a halt to all work.

## Question

The shipped `ascend.exe` (OS/2 LE, Watcom) has been proven to expose its
**control flow** statically (269 functions bootstrapped, file order == memory
order) but NOT its **data identities**: no static constant base maps code-side
addresses to the data the code actually reads (four independent tests, all
refuted — `docs/re/loader.md` §4, scripts named there). The rule formulas and
constants for combat/economy/A therefore have two extraction routes, and they
imply different risk/fidelity/effort profiles for the rest of the project:

  A. **Runtime dump (R1)**: drive the original game in dosbox-x (pty, bounded
     logs), dump memory after data load, correlate pointers against extracted
     files to recover the live base, then re-run Ghidra fixed-base and lift
     formulas the conventional way. Exact fidelity to the original formulas.
     Cost: significant dosbox forensics (the previous dosbox session caused a
     12 GB log incident — the guardrails exist but the route is untested here;
     no gdb stub in this dosbox-x build, dumping means INT hook tricks or an
     external tracer). Could consume many turns before producing anything.

  B. **Data-first (R2)**: implement systems from what IS verified — extracted
     plaintext tables (race*.dip DIPVALUES weights, restree.txt tech tree,
     ship/item tables), the manual's rule prose (23 pp rasterised in
     docs/assets/manual-jpg/), targeted narrow disassembly of the 269 bootstrapped
     functions where control flow alone constrains behaviour, and seeded
     deterministic choices documented as choices. Constants cite extracted-file
     offsets (explicitly allowed by the goal contract: "cites Ghidra addresses
     OR extracted-file offsets"). Behaviour where formulas remain ambiguous is
     labelled OPEN-QUESTIONS with the admissible range, never silently invented.
     Cost: faster, lower risk, but exact combat/economy formula fidelity is
     NOT guaranteed — a replay-faithfulness purist would object; a "playable
     game of Ascendancy" reader would not.

  C. Hybrid: B for everything, plus R1 attempts interleaved once per session,
     upgrading formulas to exact whenever the dump succeeds.

## Best default I can proceed under

**C (hybrid), B-priority.** Rationale: the verification target is a seeded
campaign turning to victory with gate-green evidence, not bit-exact replay;
route A's preconditions (memory dump from this dosbox-x build) are themselves
unproven, and betting the critical path on them risks turns with no output;
the contract explicitly admits extracted-file-offset citations, so B is
compliant, and interleaved A attempts can only improve fidelity for free.
Ambiguities go to OPEN-QUESTIONS as required; nothing is invented.

If the user instead requires formula-exact parity (A-only), say so — the
project COMPLETED under default C (gate green, victory playthroughs,
checklist closed at 5ac604d), and retrofitting exact formulas into the
working systems stays cheap: they are constants and small arithmetic in
Campaign::attackScore/defenseScore/economy phases, each cited to its
OQ entry. Residual R1-blocked items after completion: OQ-003 (.gam save
map), OQ-005 (.shp pixel codec), OQ-006 (headerless sample rate),
OQ-010 (combat arithmetic), OQ-017 (vendor .fnt font), OQ-019 (ship
design screen). Pursuing any of them needs a runtime-capture capability
this box lacks: dosbox-x here has no gdb stub, and the safe capture
routes (INT-hook memory dump inside dosbox, or an external tracer under a
custom emulator) each change how the original binary is EXECUTED — that
environmental commitment is the user's call, not a step to take
unilaterally.
