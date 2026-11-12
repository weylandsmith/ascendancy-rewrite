# _wip_t378 — DESTINATION-TRIPLE ATOMICITY INTO SHIPSIM (WIP, in-progress)

Assignment: docs/STATE.md NEXT ACTION t378 (queue row verbatim): witness M3
(ships.md S64) — every empty-space order writes order TYPE ->3 + [+0x6c]
destination triple ATOMICALLY in one frame (5 ships); object moves write
type 1/2 + ptr. Verify the issue seam in shipsim writes kind AND destination
in one step; pin the atomic pair + the 0xFFFF no-target sentinel. Two-click
sub-gap stays CADENCE-BLIND (adjacent XY->Z census = 0) — do NOT invent a
two-step internal model; UI choreography stays non-goal (pership-spec N8).

## S1 Evidence re-read (this session, 2026-11-12)

Witness stream work/r1/t370_slot_events_all.txt (frames=546, wall 00:02:09 ->
01:31:32 — covers the full playtest window; r370 run predates the 02:11
end-turn frame, the end-turn resolution witnesses are in
docs/re/_wip_playtest_t369.md "END-TURN RESOLUTION CAPTURED").

Empty-space destination orders (type ->3 + trip written SAME FRAME):
  1. s16 Erchamion  00:15:29  trip (0,0,0)->(-1664,-1568,64)   type 2->3, act 0->7
  2. s38 Ilmarinen  00:20:19  trip (0,0,0)->(-672,32,-2112)    type 0->3, act 0->7
  3. s25 Ipshitz    00:22:29  trip (0,0,0)->(-192,1504,-1280)  type 1->3, act 0->7
  4. s18 Sparrowhawk 00:24:49 trip (0,0,0)->(608,32,-416)      type 1->3, act 0->7
  5. s14 Stainer    (trip present pre-window; 00:24:02 shows trip
     (352,-672,800)->(0,0,0) type 3->0 = the ORDER-END leg, see S2)
  NB: the 4 in-window ISSUE events are 4 distinct ships; s14's issue happened
  before 00:02:09 (its trip was already live). The S64 "5 ships" count counts
  ships whose type==3 state was witnessed, not 5 in-window issue frames.

FIELD DISCIPLINE at every type->3 issue frame (all 4):
  - kind (+0x58) STAYS 4 (InSystem) — the empty-space order does NOT write
    kind; it writes TYPE (+0x67) and TRIPLE (+0x6c). The queue's "writes kind
    AND destination in one step" phrasing maps to the CITED fields as
    type+triple; kind is not part of this pair (kind 0 only on dead slots,
    spec A4).
  - act (+0x5d) goes 0 -> 7 at all four issues (7 is OUTSIDE the cited act
    enum {0,1,2} — MEASURED value, uncited meaning; bank as observation, do
    NOT wire an act model on it).
  - atgt (+0x5e) untouched; pos moves in the same frame = real-time glide
    (M4 law), not order state.

ORDER-END / REPLACE legs (same census):
  - s14 Stainer 00:24:02: trip ->(0,0,0), type 3->0 = replacing/clearing an
    empty-space order zeroes BOTH the type and the triple (trip := 0 is the
    sim-visible no-destination value).
  - Object-target orders swap type+payload in ONE frame too but never write
    +0x6c: s28 00:13:08 type 2->1 pay swap; s34 00:26:48 / 00:27:40 /
    00:27:51 same shape; s22 Ignatz 00:28:22 kind 4->3 + tgt + type 2->1 +
    pay (the ENGAGE issue writes kind+tgt+type together).

## S2 The 0xFFFF no-target sentinel — WHAT IS ACTUALLY CITED

Candidate citations checked (grep corpus):
  - aicode.md:505 / ai-dossier §5: imm-0 store 0x24a00 = command CLEAR path:
    kind := 0 AND WORD [+0x56] := 0xffff. ships.md S2809 L3: dead/free marker
    u32@+0x54 == 0xffff0000 (NOT 0xffffffff; low u16 stays).
    => the vendor's no-order state pairs kind 0 with the OWNER-HALF sentinel
    0xffff. This is the death/clear finalizer family (0x249b4/0x24a00).
  - The ship-order target field +0x59 NEVER reads 0xffff in the corpus
    (kind_hi values witnessed: 0x45/0x85/0xa1/0x1e/... all star-ptr bytes).
    There is NO cited 0xffff sentinel INSIDE the order-target field.
  - aicode.md:117/122: DAT_00076492[race] == 0xffff = per-race EXPANSION
    target "none" (race row, not ship record).
  - shipsim.h:102 inv payload u32 measured 0xFFFFFFFF on 80 slots (ring
    payload zone, not order fields).
DISPOSITION: the queue's "0xFFFF no-target sentinel" is honoured as the CITED
0x24a00 pair (kind:=0 + owner-word:=0xffff) where it exists, and as the
sim-level refusal sentinel otherwise: issueDestination returns FALSE and
writes NOTHING when the ship cannot hold the order (no half-written type 3).
No new vendor sentinel is invented. [all cited above]

## S3 Landing contract (drafted before code)

Seam in shipsim (the sim-level stand-in for the player command issuer that
writes the +0x6c triple — the vendor issuer itself was never disassembled for
this leg; S64 neg-(a) stands):
  bool issueDestination(int shipId, float x, float y, float z);
    - requires kind == InSystem (all 4 witness issues fired on kind 4;
      kinds 1/2/5 are sticky in the decider, ai-dossier §5);
    - on accept writes orderType := 3 AND targetPos := (x,y,z) in ONE call
      (atomic pair — no early-return between the two stores);
    - on refusal changes NOTHING (no type-3-with-zero-triple state reachable
      through the seam); returns false.
  bool clearDestination(int shipId):
    - the S1 order-END leg: iff orderType == 3, orderType := 0 AND
      targetPos := (0,0,0) in one call; false otherwise (state untouched).
    - NOT wired to the 0x24a00 death clear (that finalizer family is
      commitShot C4, already landed) — this is the order-replacement leg.
Existing walk seam (commitMove) already reads orderType==3 -> targetPos; the
atomicity law means the executor can NEVER observe type 3 with a stale triple
through the issue API — pin that.

Pins (test_shipsim_t378.cpp):
  T1 atomic pair: fresh InSystem ship type 0 trip 0 -> issueDestination ->
     type==3 && trip==exact values in one step; witness-valued regression:
     the 4 M3 triples round-trip exactly (floats are exact: all integers).
  T2 refusal writes nothing: kind Engage/Move/Placement ship -> false,
     type/trip unchanged (no half-write).
  T3 order-end leg: clearDestination on type 3 -> type 0 + trip (0,0,0)
     atomically; on type 1/2 -> false, state untouched (object orders are
     NOT the +0x6c store, S1).
  T4 executor can never see a torn order: after issueDestination, commitMove
     walks toward the exact triple (proves the sim's type-3 arm consumes the
     pair the seam wrote); after clearDestination, commitMove reports 0
     (no walk) — the Stainer 00:24:02 shape.
  T5 no-target sentinel: an id not in the sim -> false; and the cited 0xffff
     owner-half law is pinned where it already lands (dead ship owner -1 ->
     handle high half 0xffff semantics live in shipsave/destroy — check site;
     if already pinned elsewhere, reference the pin, do not duplicate).
MUTATION campaign per skill after pins green.
