# _wip_t204 — DIPLOMACY-ON-ATTACK (0x43a4c) code + pins (gap row 13)

Task per STATE.md NEXT: transcribe 0x43a4c verbatim, find call sites, map
onto rewrite diplomacy model, wire into combatPhase, pin, doc. Law banked
in combat.md S2f-b + ai-dossier §2; this file holds THIS session's
re-verification + the rewrite mapping decisions.

## S0 — intake triage
- live-timeline.jsonl size 5,721,578,066 == frozen baseline exactly;
  dosbox down; tree clean at 38f728c -> no sitting, STATE NEXT stood.

## S1 — 0x43a4c verbatim re-verification (capstone ~/tools/revenv)
Listing banked 2026-10-30 (0x43a4c..0x43b0e, restored image obj0):
- entry ecx=obj(relations row), esi=target idx(EDX), edi=EDI (must be !=0 —
  assert 0x43a7a line 0xdcf msg 0x84d94); bounds 0<=dx<word[0x13b98]
  (assert 0x43a5c line 0x21d8 msg 0x2a428 target).
- 0x43a90: state=byte[obj+dx+0x1c0]; ==2 (WAR) -> return 0 (0x43b09 path).
- 0x43a99 CORRECTION vs combat.md S2f-b / ai-dossier §2: the subtrahend key
  is `MOVSX DX, BYTE PTR [0x13bc4]` — a BYTE read, sign-extended into DX
  (upper EDX preserved = caller's edx upper bits; all three live call sites
  set edx via `SAR edx,0x10` of a small positive dword -> upper 0, verified
  at 0x4b852/0x39fb1/0x4b855 context). d = 10*(byte[0x13bc4]+1) (inc/imul
  0x43aa1/0x43aa2). Live byte measured ==2 (t202 census via STATE) -> d=30.
- 0x43aa5: if byte[obj+dx+0x1c0]==3 (ALLIANCE) -> add edx,edx (d doubled=60).
- 0x43abc: att=WORD[obj+2*dx+0x1b2]; att-=d; store 0x43ac5.
- CLAMP 0x43acc..0x43ae7 is a CEILING not a floor: iff state==3,
  `cmp si,bx; jle skip` — if att > word[obj+0x1cf] then att=word[obj+0x1cf]-10,
  else LEAVE AS IS. word[+0x1cf]=BREAK_ALLIANCE threshold (diplomacy.md
  S-threshold map :178). Semantics: after an alliance-violation shot, if the
  victim's attitude toward you is STILL above its own break-alliance line,
  slam it to line-10 (guarantees the alliance dies).
- BITMAP 0x43aee: eax=dword[edi+2] sar 0x10 (edi = per-run base handle);
  cl=byte[obj+0] (=row owner's race idx — the VICTIM, see S2 direction);
  byte[base+0x48304] |= 1<<cl. Return -1 (bitmap path) / 0 (at-war path).

## S2 — call-site census + direction (E8 byte-pass 0x14bb0..0x8cc83)
EXACTLY 3 callers: 0x39fba, 0x3a255, 0x4b875 (zero packed-u32 sites — R12
consistent). Row = diplo table 0x12e16 stride 494 (0x1ee) at all three:
- 0x4b875 COMBAT DAMAGE-APPLY: esi=damaged ship ([esi+0x90] shield /
  [esi+0x8c] hull decremented immediately AFTER at 0x4b87a/0x4b888, t86 law);
  obj=0x12e16+494*([esi+0x54]>>16) = VICTIM's row; EDX=[esp+0xe]>>16 =
  attacker race. Fires PER SHOT/PER-HIT, BEFORE damage lands. Rewrite mapping
  = once per (attacker,victim) engagement resolution (no per-ship model —
  documented divergence; original volley can stack -30 repeatedly).
- 0x39fba / 0x3a255 PLANET-EVENT module (esi object: byte[+0x57] victim
  race, 0xff sentinel skips; obj=0x12e16+494*([esi+0xa]>>16)); 0x3a255
  branches on ret==-1 (hostility written). NO rewrite analogue (no planet
  attack-event model) — banked as original-call-site inventory, unwired.
DIRECTION LAW: row=VICTIM, dx=attacker -> att[cell]=victim's attitude toward
attacker DECREASED; bitmap bit = victim race. Matches ai-dossier §2 prose.
THIRD ARG (EBX->edi): at 0x39fba/0x4b875 EBX = 0x13bc5 + 96*(same row-owner
idx as obj) = the SPECIES-RECORD table (stride 0x60, cf. income-law S6(a)
"species table DAT_00013bc4 stride 0x60"); handler 0x43aee uses
[dword[edi+2]] sar 16 as the run-base paragraph for the bitmap OR — every
record stores the same per-run handle at +2 (Watcom handle pattern), so the
bitmap base is per-run global, not per-species. Byte written =
1 << byte[obj+0] (row-owner = victim race; 0x43af3 mov cl,[ecx]).

## S5 — CODE PLAN (executing)
1. diplomacy.{h,cpp}: bool applyAttackDipCost(const DipValues& v, bool
   victimAtWar, bool allied, int govByte, int* attitude) + constexpr
   kAttackDipGovByte=1 (S3 live census; pins cover 0/1/2).
2. campaign.h: unsigned attackedMarks(); DipPolicyState dipStateFor(ai);
   void setDipAttitudeFor(ai,att) (pins); member unsigned char attacked_=0.
3. combatPhase: after absorbSplit, BEFORE SuperMarines/hull continue:
   iff a==kPlayer && first pair this phase: law on dipState_[b-1]; true ->
   attacked_ |= 1<<b. AI-attacker: skip (no cell; banked residue).
4. pins test_diponattack_t204.cpp: T1 pure battery (at-war gate, govByte
   0/1/2, alliance double, ceiling edges 240/241, JLE-skip 190/170),
   T2 e2e per-AI expected-equality via decideDipAction replay (no-attack vs
   attack expectation; >=1 AI attacked-expected match + bit), T3 permanence
   20 turns, T4 alliance-violation kills alliance (950 -> allied -> shot ->
   att < breakAlliance -> BreakAlliance in same turn).

## S3 — operand identities (MEASURED this session, pointer law)
- byte[0x13bc4] LIVE CENSUS scripts inline over work/r1/playcap/save/*.sav
  (20 saves, base via r1_slot.base_of vote): value 1 in 20/20. race count
  word[0x13b98]==4 20/20. => subtrahend d = 10*(1+1) = 20, doubled 40.
  CORRECTION: the STATE t204 assignment text claimed "==2 t202 census => 30"
  — WRONG operand or WRONG value; the playcap ring measures 1. The law takes
  the byte as PARAMETER (pins cover govbyte 1 AND 2).
  [identity of the table itself: income-law.md S6-caveat(a)/aicode §3 read
  DAT_00013bc4 as a species/gov-type table stride 0x60 — the BYTE READ at
  0x43a99 is base+0, no stride, so whatever it indexes, the live value 1 is
  what shipped combat used. Row-identity question banked as residue.]
- word[obj+0x1cf] = BREAK_ALLIANCE (diplomacy.md §8 t13 positional loader map
  [verified]) — so the clamp ceiling is victim's own break-alliance line.
- global byte[0x48304] (relocated-image index B+0x82BB0+0x48304): value 0 in
  20/20 saves. HONEST NEGATIVE: zero attacked-mark witnesses in the corpus
  (ring = new-game/t1254-era saves; either nobody fired at a non-at-war power
  or readers/writers never ran). Writer site 0x43afa is cited statically.

## S4 — rewrite mapping decisions (decided BEFORE coding)
D1. PURE LAW home: diplomacy.{h,cpp} `bool applyAttackDipCost(const DipValues&
    victimValues, bool victimAtWar, bool victimAllied, int govByte,
    int* attitude)` — verbatim 0x43a4c: at-war -> return false untouched;
    d=10*(govByte+1), doubled iff allied (allied == state-3 proxy per the
    t189b identity); att-=d; CEILING iff allied: att = breakAlliance-10 ONLY
    when att-after-d > breakAlliance (0x43ade JLE keeps values at/below line);
    return true (= the -1 bitmap path). i16 wrap semantics documented.
D2. TWO-PARTY PROJECTION (documented, do NOT invent a ladder): the original
    row is the VICTIM's row, cell idx = attacker (victim's attitude toward
    attacker). dipState_ rows are AI->PLAYER only (gap row 12), so the cell
    EXISTS ONLY WHEN THE ATTACKER IS THE PLAYER. Call site fires the law iff
    a==kPlayer && b!=kPlayer: attitude lands on dipState_[b-1] (= victim ->
    player = victim -> attacker exactly). AI-attacker engagements: NO attitude
    mapping (residue, consistent with gap row 16 no-ship-model + row 12).
D3. ATTACKED BITMAP: Campaign member `std::vector<unsigned char> attacked_`
    (size Nowner_, per-race bit 0 semantics == original byte bits), set at
    the call site iff applyAttackDipCost returns TRUE (never on the at-war
    path — cites 0x43a90->0x4b09), PERMANENT (no clear anywhere incl. peace),
    public readback `unsigned attackedBitmap() const` (bit r = 1<<r).
D4. WIRING POINT: combatPhase capture loop, immediately AFTER attackScore/
    absorbSplit and BEFORE the SuperMarines/hull-check continues — cites
    0x4b875 ordering (call precedes [esi+0x90]/[esi+0x8c] subtraction at
    0x4b87a/0x4b888). Fires per attack RESOLUTION per pair per turn (rewrite
    aggregate fires once per star pair; original fires per shot -> stacking
    -20s — aggregate divergence DOCUMENTED, S2i pattern). Original fires even
    when the attack FAILS (damage lands regardless) -> law call must precede
    the hullHit<=defenseScore continue.
D5. cadence/rng: the law draws NO rng (0x43a4c body has zero calls except
    asserts) and no rng stream side effects. Rewrite adds none.
D6. STATE-PROXY CAVEAT: dipState_.allied is the player-AI alliance (t189b
    identity 3==ALLIANCE); dipState_.atWar vs war_[] CAN DESYNC (SA_ForcePeace
    1639 clears war_ but not st.atWar) — the law guard reads dipState_.atWar
    (the row's own state == the original's byte[obj+dx+0x1c0]); banked.

## S5 — code + pins LANDED
CODE: diplomacy.h/.cpp applyAttackDipCost + kAttackDipGovByte=1;
campaign.h attacked_ byte + attackedMarks()/dipStateAt() readbacks +
setStarOwnerForTest/setWarForTest pin surface; combatPhase call at the
0x4b875-position (after absorbSplit, before SuperMarines/hull continues),
gated a==kPlayer (D2).
PINS rewrite/tests/test_diponattack_t204.cpp x4, 128 tests 0 failed:
T1 battery (at-war guard, gov 0/1/2 ladder, alliance double, CEILING engage
at line-10 + EXACT-boundary JLE-skip + below-line skip + no-ceiling-without-
alliance, d==0 still marks, kAttackDipGovByte==1);
T2 e2e: 340->320 EXACT one-pair-per-combat, mark bit1, cascade 20/turn ->
declare at 280 (<DECLARE_WAR 290) -> at-war freeze at 256 through 2 more
turns, peace keeps the mark, at-war state sticks through peace+war;
T3 alliance violation 340-40=300 <510 -> BreakAlliance same turn (-24 ->276);
T4 ceiling e2e 560-40=520 >510 -> slammed 500 -> break (476) — without the
ceiling the break would NOT fire: the handler guarantees alliance death.
PITFALLS CAUGHT: (1) first-draft A3 used breakAlliance=-500 thinking low
line = skip; the CEILING engages when att > line (low line ENGAGES) — the
skip side needs a HIGH line; (2) a 1-AI alliance fixture trips end-unit
Unification at t1 -> over() -> every later advance() no-ops; fix = second
AI (race02 Orfa, PROPOSE_ALLIANCE 760 never reached, att 420 stable over
the window) owning s2..s4.
BLAST RADIUS: MEASURED UNCHANGED — seed 2024 Control t1255 FINITE, seed 42
Extinct t979 FINITE (CLI this session). MECHANISM note (corrects a too-
cozy first claim): under the FFA default war_[] bits are ON but
dipState_.atWar starts FALSE (only DecideDipAction's DeclareWar latches it,
diplomacy.cpp:243), so player attacks DO pay -20/engagement in FFA runs —
attitude just never crossed a threshold that altered an outcome on the two
checked seeds (falling attitude makes ProposePeace strictly rarer; the
already-at-war DeclareWar branch is a no-op).

## AMENDMENT t210 (stacking residue line, S2:44 + D4:117 "per shot -> stacking")
RESOLVED by cited measurement (docs/re/_wip_t210.md S1..S6): the original
stacks the -20 per COMMITTED WEAPON / per VICTIM — NOT per shot. The 0x43a4c
leg inside 0x4b740 is mode==1-gated (@0x4b7f1 `cmp [esp+8],1`), and the
generic volley loop 0x4a5c1 calls 0x49f28 with edx=0 (@0x4a5ec) -> volley is
cost-free (t88a dry-run law holds). Multipliers: commit loop 0x2550c..0x25527
(one mode-1 arm-activation per matched gizmo — 0x25560 gun / 0x25570 ability)
and cat-5 splash loops 0x4d0a5..0x4d1a4 (per other entity) / 0x4d2ab..0x4d2fd
(per hostile alive-power victim, owner!=victim @0x4d2be, race-alive
byte[0x12fd6+494*owner]==2 @0x4d2ca). The D4 aggregate divergence stands
(DOCUMENTED, OQ-019 per-ship boundary — no semantic change), but its stated
mechanism is corrected: per-engagement charge under-fires once per EXTRA
committed weapon of the same order at the same victim, and once per splash
victim beyond the first.
