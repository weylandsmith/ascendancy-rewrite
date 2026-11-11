#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t364 mutation campaign: 6 mutants, serial, driver = scripts/r363r_mutate.py
set -u
cd /home/hrethric/projects/ascendancy
D=/tmp/t364mut; mkdir -p $D

# M1 stance map: restore the SUPERSEDED arg2->0 reading
cat > $D/m1.old <<'EOF'
    if (arg == 0)      s->orderType = 2;
    else if (arg <= 2) s->orderType = 1;
EOF
cat > $D/m1.new <<'EOF'
    if (arg == 0)      s->orderType = 2;
    else if (arg < 2)  s->orderType = 1;
EOF

# M2 volley [+0x63]: store only on a hit (kills the last-scanned quirk)
cat > $D/m2.old <<'EOF'
        s.activeSlot = static_cast<int>(i);                    // 0x4a5ee
EOF
cat > $D/m2.new <<'EOF'
        const bool ammoM = (d.numUses == 0) || (slot.use != 0);
        if (ammoM && s.orderType == 0 && gunEngageFlag(s, d))
            s.activeSlot = static_cast<int>(i);   // MUTANT M2 store-on-hit
EOF

# M3 mode law: apply regardless of mode (kill the 0x4b7f1 gate)
cat > $D/m3.old <<'EOF'
    if (mode != 1) return rep;

    // APPLY 0x4b87a..0x4b890 (sub then store, shield layer first).
EOF
cat > $D/m3.new <<'EOF'
    // MUTANT M3: apply regardless of mode

    // APPLY 0x4b87a..0x4b890 (sub then store, shield layer first).
EOF

# M4 charge law: charge only when damage lands (kill the fall-through)
cat > $D/m4.old <<'EOF'
    if (mode == 1) s->power -= cost;           // 0x4c614..0x4c62a
    // Damage 0x4bb2a..0x4bb43: ebx = cat0 ? design[+0x52] : 0; cidx 0x2f ->
    // design[+0x4a]. The sim's rowWeapon IS the derived +0x52 for cat-0 rows
    // (recalc law) and 0 for every other category — a non-gun active slot
    // under a gun stance lands here as damage 0, verbatim.
    int32_t dmg = d.rowWeapon;
    if (slot.cidx == 0x2f) dmg = d.special1;   // Myrmidonic Carbonizer 20
    if (dmg == 0) { rep.flags |= 0x10; return rep; }   // 0x4bb64 skip, no hit
EOF
cat > $D/m4.new <<'EOF'
    // Damage 0x4bb2a..0x4bb43: ebx = cat0 ? design[+0x52] : 0; cidx 0x2f ->
    // design[+0x4a]. The sim's rowWeapon IS the derived +0x52 for cat-0 rows
    // (recalc law) and 0 for every other category — a non-gun active slot
    // under a gun stance lands here as damage 0, verbatim.
    int32_t dmg = d.rowWeapon;
    if (slot.cidx == 0x2f) dmg = d.special1;   // Myrmidonic Carbonizer 20
    if (dmg == 0) { rep.flags |= 0x10; return rep; }   // 0x4bb64 skip, no hit
    if (mode == 1) s->power -= cost;           // MUTANT M4 charge-after-damage
EOF

# M5 ammo law: DEC on every mode (kill the 0x4a38b mode gate)
cat > $D/m5.old <<'EOF'
        if (mode == 1) --slot.use;             // THE use-consumption site
EOF
cat > $D/m5.new <<'EOF'
        --slot.use;                            // MUTANT M5 DEC on any mode
EOF

# M6 Leg A exclusivity: carrier commits then FALLS THROUGH to gunfire
cat > $D/m6.old <<'EOF'
            carrier->fireTarget = targetShipId;// [+0x68] := objective
            return rep;
        }
        // C7: no carrier. The objective-IS-local-player branch (jne 0x437ee,
        // outside the banked region) is UNMODELLED; the not-local fall-
        // through returns 2 ("nothing picked") — the sim mirrors it as an
        // empty report.
        return rep;
    }
EOF
cat > $D/m6.new <<'EOF'
            carrier->fireTarget = targetShipId;// [+0x68] := objective
            objectivePlanetShielded = true;    // MUTANT M6: fall through to B
            break;
        }
        if (!objectivePlanetShielded) return rep;
    }
EOF

for m in m1 m2 m2 m3 m3 m4 m4 m5 m5 m6 m6; do :; done
for i in 1 2 3 3 4 5 6; do :; done
for m in 1 2 3 3 4 5 6; do
  if [ -f $D/m$m.verdict ]; then continue; fi
  python3 scripts/r363r_mutate.py "M$m" $D/m$m.old $D/m$m.new | tee $D/m$m.verdict
done
