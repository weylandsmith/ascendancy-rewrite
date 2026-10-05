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

## What this unlocks (per BLOCKED.md upgrade branch)

The captured Memory member contains the RUNTIME image AND the game's loaded
data structures (e.g. the strings 'Xerxes' at 0x255f69, 'Knowledge' at
0x2535fd — golden-save vocabulary present in live RAM). Route from here:
resolve the pointer law (law #5 open point), then correlate the 31,514
disp-only operands against extracted-file structures to lift exact combat
arithmetic (OQ-010), AI orderings (OQ-015/016), .shp codec (OQ-005).
Capture deeper saves (click into a real game first — ref_capture.sh proves
the click coordinates) for post-load data richness.
