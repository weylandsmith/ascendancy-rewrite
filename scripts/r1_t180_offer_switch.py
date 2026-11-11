#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t180: resolve FUN_00044fc0's offer-kind switch table (cs:0x303dc).

    44fd3  mov al,bl ; sub al,2 ; cmp al,0xc / ja 0x45448   ; bl in 2..14
    44fe6  jmp DWORD PTR cs:[eax*4+0x303dc]

cs-relative reading uses the code-object-0 intra base +0x14bb0 (R13 law,
verified for this exact construct by scripts/r1_t180_switchtbl.py printing
15/15 in-range targets). Table image VA = 0x14bb0 + 0x303dc.

DA_ pool index meanings are from docs/re/diplomacy.md S7 (file order, t12):
  2 DA_DeclareWar, 3 DA_ProposeAlliance, 4 DA_TradeStarlanes,
  5 DA_TradeStars, 6 DA_TradeResearch, 7 DA_OfferPeaceToOtherRace,
  8 DA_BreakAlliance, 9 DA_DeclareWarOnOtherRace,
  10 DA_BreakAllianceWithOtherRace, 13 DA_OfferPeace, 14 DA_NoDipAction
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "ascend_restored.bin")
CS_BASE, CS_SLOT = 0x14BB0, 0x303DC

NAMES = {2: "DA_DeclareWar", 3: "DA_ProposeAlliance", 4: "DA_TradeStarlanes",
         5: "DA_TradeStars", 6: "DA_TradeResearch",
         7: "DA_OfferPeaceToOtherRace", 8: "DA_BreakAlliance",
         9: "DA_DeclareWarOnOtherRace", 10: "DA_BreakAllianceWithOtherRace",
         13: "DA_OfferPeace", 14: "DA_NoDipAction"}


def main():
    data = open(IMG, "rb").read()
    tbl = CS_BASE + CS_SLOT
    print(f"cs:{CS_SLOT:#x} -> image {tbl:#x}  (bodies inside FUN_00044fc0)")
    ok = 0
    for i in range(13):
        v = int.from_bytes(data[tbl + i * 4: tbl + i * 4 + 4], "little")
        inb = 0x44fc0 <= v < 0x44fc0 + 0x488
        ok += inb
        print(f"  bl={i+2:2d} {NAMES.get(i+2, '?'):28s} idx={i:2d} -> {v:#x}"
              f" {'IN-FN' if inb else 'out'}")
    print(f"in-range {ok}/13")


if __name__ == "__main__":
    main()
