# R1 via SAVESTATE — the live-image route that replaced ptrace (2026-10-05)

Status: R1 LIVE. The tracer route (docs/BLOCKED.md) is superseded, not
repaired: dosbox-x 2025.02.01 blocks PTRACE_ATTACH/SEIZE on this box
(re-confirmed by an attempt mid-session this date, rc=1 negative), but the
emulator's OWN autosave feature hands us full guest RAM without ever
attaching to a process.

## Measured laws (all reproduced 2026-10-05, several runs)

1. `autosave=<interval> <slotlo>-<end>` + `saveremark=false` in [dosbox]
   writes slot files every <interval> s with no prompts, headless-safe
   (output=x11 under Xvfb; stdin=/dev/null; -time-limit still bounds it).
2. SLOT PATH LAW: saves land at `<dirname(captures)>/save/NN.sav` —
   dosbox-x strips the last path component of `captures` for state files.
   (Measured twice: captures=$ROOT/work/r1/r1sav-X  ->  work/r1/save/;
   captures=$RUN/caps -> $RUN/save/. Both match one rule.)
3. A slot file is a ZIP. Members of interest: `Memory` = 17,055,880 B
   uncompressed for memsize=16 (= 16 MiB + 278,664 B extra, presumed ROM/
   extra storage — unverified); `Program_Name` = `ASCEND` proves the real
   game process was captured; `CPU` = 21 MB of register/emulator state.
4. NEEDLE LAW: the payload FILE HEAD is a useless needle — at runtime the
   first 0x18000 bytes carry fixups (head 'LE\0\0' -> runtime 0710ec03...,
   ~136 differing bytes per 4 KB block, low-word-dominated). Correct law:
   high-entropy, zero-free windows at payload offset P appear at member
   offset B+P for ONE constant B.
5. BASE (this capture set): B = 0x1BF4D8, 6/6 unanimous high-entropy
   128-byte anchors, 6/6 consistent, identical in all 6 slots.
   B is per-run data, not a constant to hard-code — scripts re-derive it
   every capture (the OQ-011 lesson: never trust an unreplicated vote).
   B is a MEMBER offset. Whether member offset == guest linear address is
   NOT established (IVT reads sane at member 0x0..0x3FF; BDA at 0x400 read
   all-zero — census incomplete). The pointer law (stored u32 = linear
   address = f(B, object layout)) needs more work: three candidate delta
   laws all beat controls (D=R: 289 code-region hits; D=0x242000: 573;
   D=0x1d4000: 329 data hits; random controls <=115) — ambiguous, do NOT
   pick one yet; a per-object fixup table read from the LE header or
   Ghidra-side relocation walk will settle it.

## Tooling

* `scripts/r1_savestate.sh [boot-seconds]` — safe by construction (same
  invariants as r1_attempt.sh: scratch copy only, never mounts game/;
  pkill -x; -time-limit; bounded run dir work/r1/r1sav-<stamp>/). Exit 0
  only when `r1_sav_scan.py` finds the base unanimously.
* `scripts/r1_sav_scan.py --run-dir <dir with save/> --needle
  work/ascend_payload.bin` — unanimous-vote base finder (ambiguous windows
  do not vote; min 5 votes).
* `scripts/r1_base.py` — earlier exploration variant (kept; same vote core).
* `scripts/r1_validate.py` — pointer-density base validator (set-based, one
  pass over guest RAM; results above recorded here).

## Save-state internals — source-cited (subagent verified tag dosbox-x-v2025.02.01) + measured cross-checks

Canonical repo is joncampbell123/dosbox-x. Primary paths:
* src/misc/savestates.cpp:1113-1134 — slot path law: without `-savedir`,
  `path = dirname(capturedir) + "/save"`, entry name `<slot>.sav` (1-based).
  MATCHES the measured law exactly. `-savedir <abs>` overrides to
  `<path>/<N>.sav` — prefer it for determinism.
* savestates.cpp:1078-1084 + hardware.cpp:2145/2166-2173 — autosave never
  prompts (dialog only when `!auto_save_state && !noremark`); remark entry
  = literal "Auto-save"; interval is HOST wall-clock seconds checked at
  vblank, first save just after t=interval; slot range walks A-B then wraps.
  REQUIRES video timer activity — must run with real output (x11 under
  Xvfb), NOT `output=dummy` for the *game* run (dummy smoke tests still
  saved here because dosbox-x reset dummy->default; do not rely on it).
* src/hardware/memory.cpp:2803-2853 (`SerializeMemory::getBytes`) — the
  `Memory` entry layout: [0] MemoryBlock struct header, then MemBase =
  COMPLETE guest RAM contiguous from guest PHYSICAL 0 (pages*4096), then
  mhandles (pages*4), then pagehandler_idx (262,144 B; 1=ram 2=rom
  3-16=VGA). MEASURED: header = 136 B EXACT (136 + 16 MiB + 16,384 +
  262,144 = 17,055,880 = member size, zero slack). The subagent's compiled
  estimate of 104 was 32 B short — trust the census AND the BDA scan below,
  and DERIVE H per build rather than hard-coding.
* dosbox.cpp:1708 — `savefile` replaces the slot name for ALL saves
  INCLUDING autosave (savestates.cpp:1134 ternary): must stay EMPTY or the
  slot rotation dies.

### Derived law (2026-10-05, slot 46 of r1sav-20261005-151634)
MEMBER OFFSET = GUEST PHYSICAL + H, H = 136 for this build. Two independent
confirmations: (1) size census above; (2) BDA signature scan — the unique
h in [0,0x2000) with u16@h+0x413 == 0x280 (640 KB) AND u16@h+0x44A == 80
returns h=0x88 exactly; with that offset the IVT reads coherently
(INT0 f000:ca60, INT10 c000:00ee video BIOS, INT21 f000:d0e0, INT33
c402:0010 mouse). The earlier "BDA all-zero" oddity was MY misalignment
(reading at member 0x400, not 0x488) — recorded so nobody re-chases it.
Consequence: this capture's image base in GUEST PHYSICAL = B - 136 =
0x1BF450 (B=0x1BF4D8 member-offset, per-run data as always).

### POINTER LAW — delta clusters measured, interpretation OPEN
MEASURED FACT: the two dominant runtime-vs-file u32 deltas differ by
exactly 0x6E000 (0x242000 - 0x1d4000). HYPOTHESIS [unverified, do not cite
as fact]: 0x6E000 is the page-rounded CODE object size, i.e. the two clusters
are per-object linear bases of ONE law (stored u32 = file u32 + object
linear base). The object-size figure needed to confirm this was NOT found
in the repo: a header parse attempted here with a recalled field map
produced impossible object entries — the same failure `scripts/
le_header_dump.py`'s docstring documents ("that judgement was made against a
RECALLED field map"). The repo-anchored facts stand: 121-page table stepping
+0x100 (loader.md §1), page size 0x1000, image size 0xa7710. FIRST step of
the next action: extract object boundaries with a field map validated
against those anchors (or empirically, where the delta census shifts),
THEN the 31,514 disp-only operands resolve. The 0x2420/0x24 secondary
clusters are byte-shift artefacts of unaligned u32 reads, not extra laws.

## What this unlocks (per BLOCKED.md upgrade branch)

The captured Memory member contains the RUNTIME image AND the game's loaded
data structures (e.g. the strings 'Xerxes' at 0x255f69, 'Knowledge' at
0x2535fd — golden-save vocabulary present in live RAM). Route from here:
resolve the pointer law (law #5 open point), then correlate the 31,514
disp-only operands against extracted-file structures to lift exact combat
arithmetic (OQ-010), AI orderings (OQ-015/016), .shp codec (OQ-005).
Capture deeper saves (click into a real game first — ref_capture.sh proves
the click coordinates) for post-load data richness.
