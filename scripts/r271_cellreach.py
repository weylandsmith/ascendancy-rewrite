# SPDX-License-Identifier: GPL-3.0-or-later

# r271_cellreach.py — t271: REACHABILITY CENSUS for per-cell completion laws.
#
# QUESTION (docs/re/_wip_t271.md S3): are the rewrite-unwired T39b completion
# branches (Terraforming item 36 -> class-1 mutation; Automation item 35 ->
# word2|=2) reachable at all — in the original's OWN AI doctrine, and in
# captured play? The static bounds (read verbatim 2026-11-02 from
# work/ai_selector_disasm.txt):
#   0x3f528 cmp bl,5 / je skip            — Colony Base excluded
#   0x3f52f mov ax,[0x73e3c] (=22) / cmp ebx,eax / jge skip
#                                          — need-class SCORER candidates are
#                                            rows 0..21 ONLY (OQ-014: 22 ==
#                                            SURFACE count, RAM-verified)
#   loop bound 0x3f58f/0x3f668 cmp ebx,0x27 (39 rows walked, 22..21 skipped)
# Emergency chain FUN_0003fc4c purchase sets (ai-dossier.md S10, measured):
#   {38 dig, 18, 19, 11, template {12,13,14,15,37}} — NO 35/36.
# If items >= 22 NEVER appear in any slot of any capture (except pending/UI),
# the T39b branches are HUMAN-UI-only paths: zero-corpus-witness, and in the
# rewrite (kBuildOrder player + closed AI doctrine) structurally unreachable.
#
# Method: same anchor/locator machinery as r1_built_cell_law.py (build_anchors
# + find_base + IL.find_records; slot array = u32[rec+0x10] + 0x88, cap words
# u16[rec+0x1a]; slot word = {byte0 class, byte1 itemIdx, u16 flags}).
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMG = 0x254E10, 0x1BF450

def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    any_slots = collections.Counter()      # item id -> slot-obs (itemIdx != 0xFF)
    active_slots = collections.Counter()   # item id -> active slot-obs
    high = []                              # (run, sav, turn, name, slot, id, act)
    n22 = collections.Counter()            # per-save word [0x73e3c] census
    nsav = 0
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        runname = os.path.basename(run)
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            H = base - IMG
            nsav += 1
            try:
                n22[st.unpack_from("<H", m, 0x73E3C + H)[0]] += 1
                turn = st.unpack_from("<H", m, TURN_PHYS + H)[0]
            except Exception:
                turn = -1
            for rec in IL.find_records(m):
                rb = rec[0]
                if m[rb + 0x57] == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                for k in range(min(capw, 200)):
                    it = m[ptr + 4 * k + 1]
                    if it == 0xFF:
                        continue
                    act = st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1
                    any_slots[it] += 1
                    if act:
                        active_slots[it] += 1
                    if it >= 22:
                        high.append((runname, os.path.basename(f), turn, name, k, it, act))
    print(f"saves scanned: {nsav}")
    print("word[0x73e3c] census (expect ALL 22):", dict(n22))
    print("item census ANY slot-obs by id:", dict(sorted(any_slots.items())))
    print("item census ACTIVE slot-obs by id:", dict(sorted(active_slots.items())))
    print(f"\nOBSERVATIONS of items >= 22 in slots: {len(high)}")
    for h in high[:40]:
        print("  ", h)
    print("\nVERDICT:", "ZERO items >= 22 ever placed in captured play"
          if not high else f"{len(high)} placements of items >= 22 (inspect above)")
    for iid, label in ((35, "Automation"), (36, "Terraforming")):
        print(f"  item {iid} ({label}): any={any_slots.get(iid,0)} active={active_slots.get(iid,0)}")

if __name__ == "__main__":
    main()
