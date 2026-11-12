#!/usr/bin/env bash
# t381 mutation campaign: 9 mutants over the handler-1 charge law +
# resolveInvasion (shipsim.cpp). Serial; reverts after each.
set -u
D=$(mktemp -d)
S=/home/hrethric/projects/ascendancy/rewrite/src/game/shipsim.cpp
MUT=/home/hrethric/projects/ascendancy/scripts/r363r_mutate.py

run() { # name, old-literal, new-literal
  printf '%s' "$2" > "$D/o"; printf '%s' "$3" > "$D/n"
  python3 "$MUT" "$1" "$D/o" "$D/n"
}

run M1_dec_removed \
'        if (mode == 1) --slot.use;             // THE use-consumption site' \
'        // M1 mutant: DEC removed'

run M2_charge_mode_gate_removed \
'        if (mode != 1) return rep;             // 0x4c947 cmp 0x1: probes charge
                                               // nothing (K6 edge law)' \
'        // M2 mutant: mode gate removed'

run M3_gate_orbit_mask_dropped \
'        const int gate = (affordable && inRange && d.targetOrbitSurface) ? 1 : 0;' \
'        const int gate = (affordable && inRange) ? 1 : 0;   // M3 mutant'

run M3b_gate_range_dropped \
'        const int gate = (affordable && inRange && d.targetOrbitSurface) ? 1 : 0;' \
'        const int gate = (affordable && d.targetOrbitSurface) ? 1 : 0;   // M3b mutant'

run M3c_gate_affordable_dropped \
'        const int gate = (affordable && inRange && d.targetOrbitSurface) ? 1 : 0;' \
'        const int gate = (inRange && d.targetOrbitSurface) ? 1 : 0;   // M3c mutant'

run M4_status_doubler_removed \
'            if (s->status & 0x4) limit *= 2.0;' \
'            // M4 mutant: doubler removed'

run M5_invasion_cap_removed \
'    if (need > activeShieldUnits) need = activeShieldUnits + 1;' \
'    // M5 mutant: cap removed (need = count always)'

run M6_invasion_offbyone \
'    if (need > activeShieldUnits) need = activeShieldUnits + 1;' \
'    if (need > activeShieldUnits) need = activeShieldUnits;   // M6 mutant'

# M7 count/consume-window mutants DROPPED as vacuous (skill rule 6): need =
# min(count, shield+1) <= real in-cap module count ALWAYS, so the consume loop
# stops before any phantom slot — widening either window changes no
# observable (return == consumed clears). Banked as a law-shape note.

run M8_consume_stop_removed \
'    for (uint32_t i = 0; i < s->invCap && i < kRingSlots && consumed < need; ++i)' \
'    for (uint32_t i = 0; i < s->invCap && i < kRingSlots; ++i)   // M8 mutant'

run M9_charge_uses_power_not_design \
'        s->power -= d.power;                   // 0x4c958..0x4c960 (affordable' \
'        s->power -= s->power;                  // M9 mutant (0x4c958'

rm -rf "$D"
git -C /home/hrethric/projects/ascendancy diff --stat -- rewrite/src/game/shipsim.cpp | tail -1
