#!/usr/bin/env python3
"""r363_gizmo_census.py — t363 SAVE-SIDE gizmo-ring census (residue HOME + law corroboration).

Laws reused verbatim (see scripts/r360_save_shipcensus.py header): slot ZIP
'Memory' == guest RAM, base B via unanimous anchor vote, ship array
B+0x82bb0+0x3a095 stride 0x162, dead row == u32@+0x54 == 0xffffffff, turn
gate 1..4000. Ring: 25 slots stride 7 at +0xab {cidx u8, use u16, payload
u32}; cap dword +0x15a.

Census goals (docs/re/pership-spec.md §3/§4, _wip_t363 S2f):
  1. RESIDUE HOME: which cidx codes appear on which ships — magnetron 0x3c,
     Phase Bomb 0x46, Invasion Module 0x49, Colonizer 0x47, Lane Drive 0x2b,
     Hyperdrive 0x2c, Replenisher 0x41. Counts per code + distinct ships.
  2. TURN-TAIL REFRESH corroboration: for every non-empty slot at REAL
     inventory (0..cap-1), does slot-use-word == design[+0x42] (NumUses col,
     file work/r363_gizmo_rows.json)? Autosave lands after the turn tail
     (S22 IDENTITY TIE reasoning), so the refresh law predicts a HIGH match
     rate; mid-turn consumption would show as word < design.
  3. UPKEEP payload gate: payload dword == 0xFFFFFFFF rate on upkeep-gate
     rows (codes 10..15) vs other rows — the 0x4a658 burn requires -1.
Exit 0 measured, 2 harness error. Honest-negative outcomes print and still
exit 0 (measurement, not assertion).
"""
import json, os, struct, struct as S, sys, zipfile, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan as SS
import r1_slot as RS

OFF = 0x82BB0
SHIP_X = 0x3A095
TURN_X = 0x12E10
STRIDE = 0x162
CAP_SLOTS = 0x6B
RING_OFF = 0xAB
KEYS = {0x2a: "Cloaker", 0x2b: "StarLaneDrive", 0x2c: "StarLaneHyperdrive",
        0x3c: "LaneMagnetron", 0x3f: "ToroidalBlaster", 0x41: "Replenisher",
        0x46: "PhaseBomb", 0x47: "Colonizer", 0x49: "InvasionModule"}


def payload_class(v):
    """Burn-eligibility class: the FUN_0004a658 gate is `cmp DWORD[slot+3],-1`."""
    if v == 0xFFFFFFFF:
        return "ff_burn_eligible"
    if v == 0:
        return "zero"
    return "other"


def class_name(v):
    """Value-shape class of the slot payload dword (identity is UNMEASURED)."""
    if v == 0xFFFFFFFF:
        return "0xffffffff"
    if v == 0:
        return "0x0"
    if v >= 0x100000:
        return "ge_1M(pointer-like)"
    return "small_nonzero"


def main():
    rows = json.load(open(os.path.join(ROOT, "work", "r363_gizmo_rows.json")))
    numuses = {r["idx"]: r["cols"][4] for r in rows}   # +0x42 col
    cats = {r["idx"]: r["cols"][0] for r in rows}
    pay = RS.load_payload(ROOT)
    anch = RS.anchors_cached(ROOT, pay)
    savedir = os.path.join(ROOT, "work", "r1", "playcap", "save")
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))

    code_count = collections.Counter()          # cidx -> slot count
    code_ships = collections.defaultdict(set)   # cidx -> distinct (save,row)
    refresh = collections.Counter()             # match / below / above / design0
    refresh_ex = []
    upkeep_pay = collections.Counter()          # payload classes on gate rows
    other_pay = collections.Counter()
    pay_hist = collections.Counter()
    n_ok = n_rej = live_rows = ring_slots_seen = 0
    dup_rows = 0
    for f in slots:
        try:
            mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
        except Exception as e:
            print(f"{f}: read failed {e!r}")
            continue
        B = RS.base_of(mem, anch)
        if B is None:
            print(f"{f}: no base vote")
            n_rej += 1
            continue
        turn = struct.unpack_from("<I", mem, B + OFF + TURN_X)[0]
        if not (1 <= turn <= 4000):
            print(f"{f}: turn {turn} out of gate — rejected")
            n_rej += 1
            continue
        n_ok += 1
        base = B + OFF + SHIP_X
        for k in range(CAP_SLOTS):
            r = base + k * STRIDE
            if struct.unpack_from("<I", mem, r + 0x54)[0] == 0xFFFFFFFF:
                continue
            live_rows += 1
            cap = struct.unpack_from("<I", mem, r + 0x15A)[0]
            if cap > 64:
                continue
            seen_here = collections.Counter()
            for i in range(cap):                # REAL inventory only (i<cap)
                p = r + RING_OFF + 7 * i
                cidx = mem[p]
                if cidx == 0xFF:
                    continue
                ring_slots_seen += 1
                code_count[cidx] += 1
                code_ships[cidx].add((f, k))
                seen_here[cidx] += 1
                use = struct.unpack_from("<H", mem, p + 1)[0]
                payload = struct.unpack_from("<I", mem, p + 3)[0]
                d = numuses.get(cidx)
                if d is None:
                    refresh["cidx_out_of_table"] += 1
                elif d == 0:
                    refresh["design0"] += 1
                    if use != 0 and len(refresh_ex) < 8:
                        refresh_ex.append((f, k, i, hex(cidx), use, d))
                elif use == d:
                    refresh["match"] += 1
                elif use < d:
                    refresh["below"] += 1
                    if len(refresh_ex) < 8:
                        refresh_ex.append((f, k, i, hex(cidx), use, d))
                else:
                    refresh["above"] += 1
                if 10 <= cidx <= 15:
                    upkeep_pay[payload_class(payload)] += 1
                else:
                    other_pay[payload_class(payload)] += 1
                pay_hist[class_name(payload)] += 1
            if any(v > 1 for v in seen_here.values()):
                dup_rows += 1

    print(f"slots_ok={n_ok} rejected={n_rej} live_rows={live_rows} ring_slots_seen={ring_slots_seen}")
    print("cidx_census (code count distinct_ships name):")
    for c, n in sorted(code_count.items()):
        print(f"  0x{c:02x} {n:6d} {len(code_ships[c]):5d} {KEYS.get(c, rows[c]['name'] if c < len(rows) else '?')}")
    print(f"refresh_law (slot use-word vs design[+0x42]): {dict(refresh)}")
    print(f"  examples (save row slot cidx use design): {refresh_ex}")
    print(f"upkeep_gate_rows_10..15 payload: {dict(upkeep_pay)}")
    print(f"other_rows payload: {dict(other_pay)}")
    print(f"slot_payload_value_classes(all slots)={dict(pay_hist)}")
    print(f"rows_with_duplicate_cidx_in_ring={dup_rows}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
