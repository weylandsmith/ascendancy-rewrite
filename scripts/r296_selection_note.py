#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r296 — SHIP-SELECTION CHOREOGRAPHY NOTE (t296 deliverable, static-cited).

NOT a capture driver. This is the machine-readable pin sheet a t297 live
session builds on, plus a self-check that every cited anchor is still present
VERBATIM in work/ascend_payload.bin (run it before any launch: if the payload
drifted, the choreography is void).

Full law: docs/re/ships.md S24 + docs/re/_wip_t296.md S1..S9.

SELECTION (BatModeWnd handler 0x1aef8; mouse path is MSG 4, not 0x53):
  G1 clip exists iff BYTE [ship+0x58] == 4 (in-system)   builder 0x1d6bb
  G2 clip kind byte == 2 (ship)                           0x1b6fc / 0x1b9f6
  G3 owner [ship+0x54]>>16 == BYTE ds:0x7458e             0x1b709 / 0x1ba16
  G4 MOVES DWORD [ship+0x88] > 0                          0x1b716 / 0x1ba2c
  effect BYTE [batwin+0xb7] := 2                          0x1b71f / 0x1ba39

CLICK GEOMETRY (live session):
  BatModeWnd client rect (windows.txt VERBATIM): X0 7 Y0 7 X1 465 Y1 472.
  Message-4 bounds check 0x1b085..0x1b0a3 rejects clicks outside
  [win+0x8..0x14] (the runtime rect), so aim INSIDE it. The ship's on-screen
  position is computed by the clip DRAW call 0x1a270 (site 0x1d707); the
  screen->world camera fields are UNMAPPED (honest negative, _wip_t296 S6.2),
  so locate the ship SPRITE visually, not by arithmetic.
  DO NOT click star dots: they are kind-3 PLANET clips -> G2 skips (this is
  exactly why t293's three launches never selected anything).
  DO NOT plain-click again after selecting: in mode 2 with WORD [win+0xbc]
  == 0xffff the click sets mode := 0 (DESELECT) at 0x1b114.

VERIFICATION AFTER THE CLICK (ring-readable, no debugger):
  ds:0x43504 (SELECTED OBJECT POINTER) is plain RAM at guest-phys
  B + 0x82bb0 + 0x43504 — the r1_slot.OFF data-segment base, like every other
  DAT scalar. [t297 CORRECTION, measured: the earlier note here said
  "B + 0x43504", which is off by 0x82bb0 and reads garbage (constant
  0x1de8c031).] t297 ALSO measured production idle idle t=1086: ds:0x43504 =
  0x256825 NON-NULL while nothing is selected and ds:0x43508 changes WITHOUT
  INPUT — both globals have non-order writers (0x51a8e/0x51fc2), so use them
  ONLY as baseline-vs-delta pairs around a click, never as absolute
  witnesses. BYTE [batwin+0xb7] is a window-object field; the batwin INSTANCE
  is not yet pinned in guest RAM (handler-pointer scan dead, t297-B).

ORDER PUBLICATION (the still-open half):
  msg 0x50 leg 0x1b5ba: gate param ebx >= 1 and [sel+0x58]>>16 >= ebx, then
  ds:0x43508 := [sel + 0x42 + ebx*4]  (the SELECTED object's own target
  table) @0x1b5dd/0x1b5e6, plus command-ring post 0x56ad4(0x7a35c, code 0x11)
  writing 6-byte {u16 code, u32 param} at [game+0x422c] + slot*6.
  THE WIDGET THAT POSTS msg 0x50 IS NOT IDENTIFIED (image-wide immediate
  census: 0x53 loads = {0x15f3c batmode relay, 0x1f971, 0x3df34, 0x4b83a};
  0x52 = {0x1724a, 0x1762c, 0x3decc}; no cosmos-map poster). t297's job is to
  find it (candidates: BatListWnd row interaction, right-click contents menu)
  or to prove the mouse route cannot reach it and switch to the debugger-poke
  class (t290/t291 precedent: poke the selection, then post msg 0x50).

WITNESS INSTRUMENT (unchanged, t293): owner-0 ship kind census; kind 2 ==
issued move order. Baseline kinds {3,4,5}; kind 2 never observed -> clean.

Usage:  python3 scripts/r296_selection_note.py            # anchor self-check
        python3 scripts/r296_selection_note.py --print    # dump this pin sheet
Exit: 0 all anchors present, 1 payload drifted, 2 no payload.
"""
import os, sys

# (address, byte pattern hex, meaning) — every one VERBATIM from
# work/ascend_payload.bin via work/t91_code_disasm.txt (t296 verification pass).
ANCHORS = [
    (0x1d6bb, "807d5804",            "G1 clip-build kind-4 gate"),
    (0x1b6fc, "803802",              "G2 msg0x53 clip kind==2"),
    (0x1b709, "8a158e4507 00".replace(" ", ""), "G3 viewer index ds:0x7458e"),
    (0x1b716, "83b888000000 00".replace(" ", ""), "G4 MOVES>0"),
    (0x1b71f, "c685b70000000 2".replace(" ", ""), "mode:=2 (msg 0x53 leg)"),
    (0x1b9f6, "80fa02",              "G2 mouse leg clip kind==2"),
    (0x1ba39, "c686b70000000 2".replace(" ", ""), "mode:=2 (mouse leg)"),
    (0x1b5e6, "a308350400",          "ds:0x43508 publish (msg 0x50)"),
    (0x1b114, "c685b70000000 0".replace(" ", ""), "mode:=0 deselect on plain click"),
    (0x1d6e6, "c60602",              "clip kind := 2 store"),
    (0x17654, "e8435d0000",          "clip rebuild 0x1d39c call site"),
]

PAY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "work", "ascend_payload.bin")


def check(pay):
    bad = []
    for a, pat, what in ANCHORS:
        want = bytes.fromhex(pat)
        got = pay[a:a + len(want)]
        if got != want:
            bad.append((a, what, want.hex(), got.hex()))
    return bad


def main():
    if "--print" in sys.argv:
        print(__doc__)
    if not os.path.isfile(PAY):
        print("NO PAYLOAD", PAY)
        return 2
    pay = open(PAY, "rb").read()
    bad = check(pay)
    if bad:
        print("ANCHOR DRIFT — choreography VOID:")
        for a, what, w, got in bad:
            print(f"  {hex(a)} {what}: want {w} got {got}")
        return 1
    print(f"ANCHORS OK {len(ANCHORS)}/{len(ANCHORS)} present verbatim "
          f"(payload {len(pay)} B) — t296 choreography valid for t297")
    return 0


if __name__ == "__main__":
    sys.exit(main())
