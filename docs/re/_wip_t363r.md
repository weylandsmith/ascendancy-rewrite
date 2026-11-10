# _wip_t363r.md — t363R RE-LAND progress (session 2026-11-09 ~23:15 EST)

STATE: code LANDED + builds clean + existing suite 197/0 GREEN with the new
wiring. Pins test_shipsim_t363.cpp NOT YET written (next step). CMakeLists
NOT YET updated with the new test file.

Done:
- Sitting check NEGATIVE (turn 1086, size 8,917,535,608 B unchanged).
- Raw re-reads banked to _wip_t363.md S6 (mutators 0x49698/0x496e4/0x49624,
  admission 0x499f8, completion 0x49a34, upkeep 0x4a658, recalc 0x49acc).
- shipsim.h: SimLane.closed; InvSlot/SimDesign/kCidx*/kLaneStep pool consts
  (DERIVED flag); Ship += weaponLevel/shieldLevel/cat2PowerCarry/scannerTotal/
  specialCount/targetSlot/hullBaseDrive/shields/inv[25]/invCap/invFilled/
  laneToB/orderPayloadLane/speciesLaneTravel; BoundaryReport.laned; API
  setDesigns/recalcShip/upkeep/refreshUseCounts/setSlot/clearSlot/
  fillFirstEmpty/carriesCode/firstCarrier/setDriveAddend + private
  starArrivalComplete; designs_/driveAddend_ members.
- shipsim.cpp: fromRecord imports (NO recalc on import — powerMax law);
  recalcShip (+0x18 zero restored, 0x49af5); upkeep verbatim (bit0 zeroes
  MOVES, ring scan STILL RUNS; payable gate skips ENTIRELY; charges NESTED;
  bit3 zeroes shields); refreshUseCounts (+0x42 operand); mutators verbatim
  (idx>cap REJECT / idx==cap ADMITTED phantom; fillFirstEmpty window=cap);
  starArrivalComplete (polarity target==l->a -> laneToB); laneMarch endpoint
  laneToB-driven; commitMove orderType-2 -> starArrivalComplete (scatter
  fallback SUPERSEDED for type 2); tail ORDER status->refill->refresh->march
  ->upkeep; sweep re-grant REPLACED by upkeep(); digest extended.

Named divergences recorded in-code: clearSlot idx>=25 defensive refuse
(vendor would corrupt memory — no cited law); designRow out-of-range -> zero
row; kind==3 completion leg unimplemented (unreachable from sole caller).

NEXT: pins x8 (contract item 6 a-h), CMakeLists line, mutation campaign
(item 7: burn-after-pick swap, skip-ring-on-bit0, charges-unnested, refresh
operand +0x3e, recalc window inclusive, phantom-not-inert), ships.md S62,
G9 polarity fix in place, ledger audit, gate, commit.
