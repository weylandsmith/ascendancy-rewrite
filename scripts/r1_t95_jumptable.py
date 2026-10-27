#!/usr/bin/env python3
"""t95 / W6-A5: decode the ship-order-kind JUMP TABLE via the dispatch site.

WARNING (t96): the table read below IS valid (live entries == restored FILE
0x1d840 + P0, clean pointers), but its PURPOSE was misidentified — it is the
ship-PANEL STATUS dispatcher (static.txt templates), NOT the order-name
mapping; see REFUTED-ROUTES R13 and docs/re/aicode.md §2h. Do not spend a
session "decoding fixups" here; the A5 residual is the SO-block CONSUMER.

THE MEASURED DECODE LAW (this replaces the first draft's B+TABLE read, which
this session proved WRONG — member B+0x8c90 holds the obj0 DATA pool there,
not the table):
  The static image cannot yield the table (region below 0x14bb0 keeps raw LE
  fixup bytes; payload and restored read identically garbage at 0x8c90). But
  the DISPATCHER's own jmp disp32 is fixup-relocated in the live guest: at
  image 0x1de4f `2e ff 24 9d <disp32@0x1de53> jmp [ebx*4+0x8c90]`, the live
  disp32 == 0x8c90 + 0x1d4000 (the low-region runtime home == the OQ-011 obj0
  code home). Table runtime address = live disp32; ENTRIES are u32 runtime
  addrs of the form img + 0x1d4000 (case bodies live in the img gap
  [0x2a50,0x14bb0)); member index for any runtime addr R is R + H, H = 136
  (dosbox-x 2025.02.01; re-derive per build).
  BANKED TRAP: find()-style searches return MEMBER indices, not runtime
  addrs. The name block found at member 0x248338 has runtime 0x2482B0 ==
  P0+0x88e60 EXACTLY (P0 = B - H) — only after the -H correction does the
  pool law (runtime = P0 + img offset) validate.

Self-validation gates (all must pass or the reading is VOID, not a finding):
  1. B vote >= 5 unanimous anchors (r1_sav_scan law; ambiguous windows don't
     vote). B anchors gate 2 and the P0 cross-check, not the table read.
  2. Dispatcher bytes at image 0x1de40..0x1de52 in the member equal the
     payload bytes (same program instance; opcodes are not relocated, only
     their fixup immediates are).
  3. Live disp32 == 0x8c90 + 0x1d4000 (delta law).
  4. All six entries land in img [0x2a50, 0x14bb0) under the same delta AND
     are IDENTICAL across all validated slots (deterministic load layout).

Exit 0 = table decoded and self-validated on >=1 slot. 1 = ran, negative.
2 = harness error.
"""
import argparse, os, os.path, sys, struct, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

ROOT = "/home/hrethric/projects/ascendancy"
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
H = 136
STATIC_TABLE = 0x8c90
DISP_OFF = 0x1de53          # disp32 of the jmp at 0x1de4f
LOWHOME = 0x1d4000          # measured low-region runtime home (the delta)
GAP = (0x2a50, 0x14bb0)     # img span holding the six case bodies


def slots_for(run_dir):
    for sub in ("save", "ck"):
        d = os.path.join(run_dir, sub)
        if os.path.isdir(d):
            return d, sorted(f for f in os.listdir(d) if f.endswith(".sav"))
    return None, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True,
                    help="comma-list of work/r1/* run dirs to try")
    ap.add_argument("--max-slots", type=int, default=2)
    args = ap.parse_args()

    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    disp_expect = pay[0x1de40:0x1de53]

    hits = 0
    decoded_seen = None
    for run in args.runs.split(","):
        run = run.strip()
        if not run.startswith("/"):
            run = os.path.join(ROOT, run)
        d, sl = slots_for(run)
        if not sl:
            print(f"{os.path.basename(run)}: no save/ck slots")
            continue
        for f in sl[: args.max_slots]:
            try:
                mem = zipfile.ZipFile(os.path.join(d, f)).read("Memory")
            except Exception as e:
                print(f"{os.path.basename(run)}/{f}: read failed {e!r}")
                continue
            votes, _ = find_base(mem, anch)
            if not votes or votes.most_common(1)[0][1] < 5:
                print(f"{os.path.basename(run)}/{f}: no unanimous B (gate 1)")
                continue
            B = votes.most_common(1)[0][0]
            n_votes = votes.most_common(1)[0][1]
            gate2 = mem[B + 0x1de40:B + 0x1de53] == disp_expect
            ld, = struct.unpack_from("<I", mem, B + DISP_OFF)
            gate3 = ld == STATIC_TABLE + LOWHOME
            raw = list(struct.unpack_from("<6I", mem, ld + H))
            img = [v - LOWHOME for v in raw]
            gate4 = all(GAP[0] <= v < GAP[1] for v in img)
            if decoded_seen is None:
                decoded_seen = img
                gate4b = True
            else:
                gate4b = img == decoded_seen
            print(f"\n{os.path.basename(run)}/{f}: B={B:#x} ({n_votes} votes) "
                  f"P0={B-H:#x}")
            print(f"  gate2 dispatcher bytes: {gate2}")
            print(f"  live jmp target {ld:#x} (static {STATIC_TABLE:#x}, "
                  f"delta {ld - STATIC_TABLE:#x}) gate3 {gate3}")
            print(f"  entries kind 0..5 runtime: {[hex(v) for v in raw]}")
            print(f"  entries img: {[hex(v) for v in img]} gate4 {gate4} "
                  f"identical-across-slots {gate4b}")
            if gate2 and gate3 and gate4 and gate4b:
                hits += 1
                print("  VALIDATED")
            else:
                print("  VOID")
            break  # layout is deterministic: one slot per run is enough
    print(f"\nVALIDATED_SLOTS={hits}")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
