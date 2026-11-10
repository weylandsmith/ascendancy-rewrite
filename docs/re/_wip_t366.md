# _wip_t366 — SAVE-WRITE SIDE (emit ship records back into RESUME.GAM layout)

Assignment (STATE.md NEXT, queue row verbatim): emit ship records back into
RESUME.GAM layout; byte-compare vs vendor-written save if one can be produced
headlessly, else round-trip-through-rewrite tests + honest note.

## S0 Framing (written BEFORE first probe)
- "Vendor-written save" question: dosbox-x savestate ZIPs (the production ring
  work/r1/playcap/save/*.sav) ARE headlessly-produced artifacts containing the
  full guest RAM 'Memory' member — but the ship array bytes in them are
  game-RAM snapshots, not game-emitted serializations. The game's OWN save
  format (RESUME.GAM / .gam slot files) is UI-driven; the click path is
  cited-broken ("window died before release", REFUTED-ROUTES t261/N8) and a
  second long-running capture is forbidden by the task contract. Expect:
  honest negative on the byte-compare leg, round-trip tests as the deliverable.
- Writer contract (pership-spec §6 S7 verbatim): emit records at member index
  B+0x82bb0+0x3a095 + slot*0x162; pointer-valued fields (+0x59, +0x63, +0x68)
  are guest-PHYSICAL values — rebasing to a target run means adding the
  per-run delta (new_B - old_B), NOT re-deriving targets.
- Durable-vs-transient: STATE t365 note says engagement-transient fields
  (stance/gate/activeSlot) are NOT durable save state. Measure which record
  bytes actually churn across adjacent autosaves (same turn and boundary) to
  ground the honest note in corpus data instead of assertion.

## S1 CHURN CENSUS (scripts/r366_churn_census.py RC=0, output
work/r366_churn.out; MEASURED 2026-11-10). Corpora: production ring
work/r1/playcap/save (same-turn adjacent pairs, t273 mtime<=120s guard) and
the t340 scratch drive ring-final work/r1/t340-shieldc-20261108-014705/ring-final
(turns 1089..1093, 19 adjacent pairs x 107 window rows).
- RING same-turn pairs: EVERY named field churns ZERO (whole stride-0x162
  window frozen while idle — corroborates t360's byte-identical-window finding
  at field granularity).
- DRIVE advancing pairs: churn ONLY at +0x58 (orderKind) / +0x59..+0x5c
  (orderTarget) / +0x5d (actEnum) / +0x5e..+0x60 (actTarget) and
  +0x9e..+0xa9 (pos). RAW counts: kind 3/19, pos-x 59, pos-z 86 pairs.
  ALL identity/design/inventory fields (weaponLevel..targetSlot, ownerHandle,
  resolverFlag+gate +0x62, activeSlot/slotPtr +0x63, orderType +0x67,
  orderPayload +0x68, absTriple, power/integrity/shields/moves/maxIntegrity,
  statusFlags, hullKind, ring+tail, invCap, filled) churn ZERO across the
  observed pairs.
- HONEST SCOPE: zero-churn is OBSERVATION, not a vendor promise — the captured
  saves hold no in-combat-at-boundary ships, so engagement-transience of
  +0x62/+0x63 (t365's stance/gate/activeSlot claim) is NOT testable here; the
  writer treats them as ordinary durable bytes round-tripped verbatim, and the
  note says the transience claim rests on the t364/t365 law reading, not on
  this census.

## S2 VENDOR-SAVE QUESTION (honest negative framing for the byte-compare leg)
The only headlessly-produced saves on disk are DOSBox-X savestate ZIPs
('Memory' member == full guest RAM) — RAM snapshots taken by the EMULATOR, not
serializations emitted by the GAME. The game's own save (RESUME.GAM) is
UI-driven; the click path is cited-broken ("window died before release",
REFUTED-ROUTES t261 input-dead law / N8 N8 t293 budget) and a second
long-running capture is forbidden by the task contract. t260's
bank-t260-roundtrip-1255 is a loadstate re-save (REFUTED-ROUTES L273:
"structural decode of a round-trip re-save cannot see [input-deadness]") —
also an emulator snapshot, and the bank state class is input-dead.
=> NO game-emitted vendor save with ship records can be produced headlessly
here. The honest substitute shipped: WRITE-BACK IDEMPOTENCE byte-compare —
parse 20/20 ring saves, write the records back through the new writer, and
assert the 17,055,880-byte Memory member is BYTE-IDENTICAL. That is a real
byte-compare against vendor-written (emulator-snapshotted) save bytes.
