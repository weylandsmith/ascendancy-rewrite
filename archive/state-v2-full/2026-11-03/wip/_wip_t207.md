# _wip_t207 — planet-event callers of the diplomacy-on-attack handler (0x43a4c)

Task: t207 — read 0x39fba and 0x3a255 verbatim, name the enclosing functions
and their callers, pin the victim law (esi+0x57), and decide what the -1
return at 0x3a255 drives. Windows: work/t207_w1.txt (0x39f00..0x3a010),
work/t207_w2.txt (0x3a1e0..0x3a2b0), work/t207_w3.txt (handler re-verify).

## S1 — handler return law RE-VERIFIED VERBATIM (work/t207_w3.txt, 0x43a4c..0x43b0e)
- eax = victim diplo row = ecx(=eax arg) + movsx(victim_idx si); args per t204:
  EAX=diplo row base 0x12e16 + 0x1ee*victim-race, EDX=attacker race idx,
  EBX=star record 0x13bc5 + 0x60*star (t205 identity).
- 0x43a90: if BYTE[row+0x1c0] == 2 (WAR) -> return 0 (0x43b09) — no cost.
- ... attitude word [+0x1b2] -= d, state-3 CEILING (t204 law, unchanged).
- 0x43acc: if state==3 AND new attitude > word[row+0x1cf] -> slam to line-10.
  NOTE the JLE at 0x43ae0 compares against word[row+0x1cf] = per-row
  BREAK_ALLIANCE line (t204).
- 0x43aee: victim mark set (bit = victim idx in the PER-STAR byte [0x48304+star]).
- RETURN 0xffffffff (0x43b00) iff the path through the alliance-violation
  region ran to 0x43b00, i.e. the mark-write tail. EXACT control flow:
  state==2 -> ret 0; every non-WAR path falls through 0x43aee..0x43b00 and
  returns -1. => **-1 means "a diplomatic price was paid (or at least the
  non-at-war path ran)", 0 means "already at war / skipped"**. t204's
  "branches on the -1 return" reads as: the caller only does its follow-up
  when the victim was NOT already at war with the attacker.
  (The alliance-break itself is a relation-state side effect inside this
  handler path per t204 pin; the -1 is NOT break-only — re-read carefully:
  0x43ad4 jne 0x43aee / 0x43ae0 jle 0x43aee both land on the mark tail,
  and only the WAR guard 0x43a97 je skips it. So -1 == "not at war".)

## S2 — enclosing functions (functions_full.tsv; OVERLAP caveat)
- 0x39fba lies in 0x39f00..0x3a098 (size 408).
- 0x3a255 lies in 0x3a174..0x3a4df (size 875).
(NOT the 0x38ba4 governor family — that span ends before 0x39f00.)

## S3 — 0x39f00 body reading (work/t207_w1.txt)
- EAX=ESI planet record (0x39f07 mov esi,eax); EDX saved [esp+0x14]; BX saved
  [esp+0x1c].
- 0x39f12 assert [eax+0x62] != -1.
- owner race = [esi+0x57] byte; asserts in-race-range ([0x13b96]>>16 == nraces)
  or ==0xff sentinel (0x39f1e..0x39f4a). Planet-record +0x57 == owner byte
  (aicode.md:105/654, income-law.md:353 — NOT the name-family orbit f32s:
  r1-savestate.md's +0x57 orbit note is on the planet NAME record, different
  record family; the byte-read form + 0xff sentinel + census usage agree owner).
- 0x39f85: EBX = sar([esi+0xa],16) -> handle index into per-STAR table 0x13bc5
  (stride 0x60 idiom verbatim). So the star holding this planet = star([esi+0xa]).
- 0x39fa8: ECX = sar([esp+0x1a],16) = race index of the EDX arg (attacker).
- call 0x43a4c with EAX=0x12e16+0x1ee*victim([esi+0x57]), EDX=attacker idx,
  EBX=star record. Victim = planet OWNER race.
- 0x39fbf onwards RETURN VALUE IS DISCARDED (0x39fbf overwrites EBX without
  testing EAX). Follow-up code at 0x39fc4.. scans the planet's item slots
  ([esi+0x10] table, idx [ebp+1], stride 0x28 into 0x73e46 = planitem runtime,
  active-flag bit8 per t201) — planet slot processing, unrelated to the call.
- => caller 0x39fba: fire-and-forget attack-dip-cost on the planet-owner race.

## S4 — 0x3a174 body reading (work/t207_w2.txt, mid-function)
- ESI=planet record here too (0x3a21c reads [esi+0xa] star handle, 0x3a235
  [esi+0x57] victim). EBP = big context (reads [ebp+0x54] attacker HANDLE,
  [ebp+0x15a] loop bound).
- 0x3a1f4..0x3a215 WITNESS GATE: k = sar([ebp+0x54],16) (attacker race idx);
  cmp byte [k*2*0x1ee... form: [eax*2+0x12fb3] where eax = 0x1ee*k -> reads
  race-table byte 0x12fb3 + 0x1ee*k + 1? CAREFUL: operand [eax*2 + 0x12fb3]
  with eax = 0x1ee*k -> addr = 0x12fb3 + 2*0x1ee*k. Hmm — stride 0x3dc(2*0x1ee)?
  Resolvable against t190 species-table census (base 0x12fb3 stride 0x1ee).
  -> 0xffffffff stored when byte==0; else k stored. = third-party witness idx.
- 0x3a21c..0x3a255: EDX=k(attacker), ESI=0x12e16+0x1ee*victim([esi+0x57]),
  EDI=witness; call 0x43a4c.
- 0x3a25a: cmp eax,-1; jne 0x3a298 (skip). On -1:
  0x3a27c: di = word [0x12fdf + 2*(0x1ee*victim)];  # 0x13fdf-region matrix
  0x3a283: cmp di, word [0x12fc8 + 2*(2*(0x1ee*attacker))]  # THIRD-PARTY matrix
  0x3a28a: jge skip; on less: word [0x12fc8 + attacker-cell] = attitude(victim-row) - 10.
  (exact index algebra to be pinned in S6)

## S5 — caller census (E8 byte-pass over full ascend_restored.bin)
- callers(0x39f00) == EXACTLY {0x4c97f}
- callers(0x3a174) == EXACTLY {0x3d951, 0x42c8e}
- functions_full.tsv: 0x39f00..0x3a098 (408B), 0x3a174..0x3a4df (875B) —
  0x3a174 is its OWN function (not a 0x38ba4-family mid-function span).
- 0x4c97f lies inside tsv entry 0x4c794..0x4ca50 — the t88 gizmo-attack
  handler family; 0x4c991 (inside the same span) IS the documented
  "gizmo-0x46 build leg" (loop <=5 over target [esi+0x10] slot list, active
  bit bit0 of word+2, 0xff sentinel; combat.md S2f). The dispatch idiom at
  0x4c966 `cmp byte [esi+0x32],0` reads the DESIGN row +0x32 (category)
  exactly per combat.md — ESI inside these handlers IS the design row
  (0x7650c + 0x6a*design_idx), EBP = [ship+0x68] TARGET record pointer
  (0x4c7ea), ship = [esp+0x44].
  => THE 0x4c97f CALL SITE (work/t207_w5.txt):
     guarded by [esp+0x40]&1 (success/hit flag) AND mode==1 (0x4c94d);
     power already subtracted at 0x4c960 ([ship+0x88] -= cost);
     iff design CATEGORY == 0 (cat-0 guns fall through 0x4c966 jne):
       EAX = EBP target record, EDX = sar(target? NO: ebx=[esp+0x44]=SHIP,
       ebx=[ship+0x54] -> sar -> attacker owner idx), EBX = ship record,
       call 0x39f00.
  *** NOTE 0x4c794 = the cat-1 (shield) handler per combat.md S2f dispatch
      (0->0x4b8e4, 1->0x4c794, 2->0x4ca50, 5->0x4cd90); the cat-0 check at
      0x4c966 lives INSIDE this span which makes the tsv span boundary
      suspect OR this leg runs after a shared prologue — RE-READ the
      dispatch entry before asserting (the 0x4c966 compare of [esi+0x32]==0
      guards the call site itself, so the site pays diplo only for cat-0
      designs regardless of span bookkeeping).
- 0x3d951 inside tsv 0x3d2fe..0x3db54 (t198 module vote: race.cpp,
  _wip_t198.md S1 "race 0x3d2fe(1)"); 0x42c8e inside tsv 0x41e34..0x435fb
  (the order-resolver family, t206 W2 same nesting). Context read
  (work/t207_w6.txt): ESI=planet record; loops via 0x396cc (slot->unit
  record getter, see S6b); compares unit owner [unit+0x54]>>16 against
  occupant-losing side and [esp+0x2c4]; calls 0x3a174 with
  EDX=slot idx (and 0xffff-masked), ECX=&out; afterwards calls 0x39894
  (new-owner getter) writing [esp+0x30c] and asserts equality patterns —
  a CAPTURE/OCCUPATION transition path inside the order resolver.

## S6 — victim law + argument algebra (VERBATIM)
### 0x39f00 wrapper (fire-and-forget)
- ESI = planet record; [esi+0x62] != -1 assert.
- victim = BYTE [esi+0x57] (planet OWNER; 0xff sentinel skips the call) —
  same +0x57 owner byte as income-law.md:353/aicode.md:105 (NOT the
  name-record orbit f32 family; record-family note r1-savestate.md:155).
- star = sar(dword [esi+0xa], 16) -> EBX = 0x13bc5 + 0x60*star (t205 law).
- attacker idx EDX = sar([esp+0x1a],16) = sar(dword[EDX arg + 0x54],16) —
  the CALLER's EDX record +0x54 owner-handle (at 0x4c97f: the SHIP's +0x54).
- EAX = 0x12e16 + 0x1ee*victim. RETURN DISCARDED at 0x39fbf.
- After the call: slot-scan tail (min-REQUIRES-demolition shape: builds a
  candidate list of ACTIVE items (word+2 bit0) with cost word
  [0x73e46+0x28*item], picks min-cost (0x3a05a..0x3a066 skip [esi+0x52],
  rng tie-break 0x3a07b) and zeroes slot byte+3 0x3a068 — an item-loss
  path, NOT diplo. (Consistent with a planet taking an attack hit.)

### 0x3a174 (capture-path payer, return matters)
- EAX=ESI planet record, EDX=DI slot idx (< [esi+0x1a] assert; slot item
  byte+1 MUST == 0x17 assert 0x3a1a6), ECX=BX out-param.
- EBP = 0x396cc(planet, slot) = the UNIT/ship record slotted at +0x17 (the
  occupying transport/invasion unit); gate 0x3a1d1..0x3a1e1: if owner !=
  0xff then ASSERT unit_owner([ebp+0x54]>>16) == owner byte (the unit sits
  on an owned planet of the same race — or owner 0xff).
- EDX = attacker = sar([ebp+0x54],16) = OWNER RACE OF THE SLOTTED UNIT (the
  invader).
- WITNESS (edi): k=EDX; if BYTE [0x12fb3 + 2*0x1ee*k] == 0 -> EDI =
  0xffffffff else EDI = k. (INDEX-STRIDE QUESTION: t202 banked the per-race
  ability byte at 0x12fb3 + 0x1ee*owner (BuildOnBlack +0x19d, census
  {0:19,1:2,2:11,3:0,4:8} 60.sav); this site's algebra is 0x3dc*k — either
  a DIFFERENT column at stride 0x3dc or a compiler 2x form of the same
  table; CENSUS r207 decides which reads true against the live saves.)
- EAX = 0x12e16 + 0x1ee*victim (victim = [esi+0x57]); EBX = star record
  0x13bc5+0x60*star([esi+0xa]). call 0x43a4c.
- 0x3a25a cmp eax,-1 / jne skip: FOLLOW-UP RUNS ONLY ON THE -1 RETURN, i.e.
  iff victim was NOT already at war with the attacker (handler: 0x43a97 je
  -> ret 0 iff state==2 WAR; every non-WAR path falls through the mark tail
  0x43aee and rets -1). => -1 is the "price actually paid (or first
  violation)" sentinel; 0 = already-at-war, no reputation consequence.
- On -1: cmp WORD [0x12fdf + 2*(0x1ee*attacker)] < WORD [0x12fc8 +
  2*(2*0x1ee*attacker)]  -> if less: WORD [0x12fc8 + attacker-cell] :=
  WORD [0x12fdf + attacker-row] - 10.  # THIRD-PARTY OPINION PENALTY
  - 0x12fc8 = third-party opinion matrix PER t180/t99 banked form
    (0x447a0 writes it directly: mov [ebx+0x12fc8],dx; debugflags.md:21
    "copies template word [edx+0x12feb] into third-party matrix [0x12fc8]";
    _wip_t99.md:75 lists [0x12fc8] readers 0x49a17/0x4a867/0x50f89,
    dispatcher 0x441c1).
  - 0x12fdf = word at diplo-row offset +0x1c9 IF the row base is
    0x12e16+0x1ee*r (0x12e16+0x1c9=0x12fdf EXACT; 0x1c9 = the documented
    threshold-word family +0x1c9/1cd/1cf/1d3, diplomacy.md:131 —
    +0x1cf=DECLARE line used by the t204 ceiling). 0x12fd6 = row offset
    +0x1c0 = the RELATION-STATE matrix base (t180: writes
    [edx+eax+0x12fd6], bl=1 state set). => 0x12fc8 (state base -0xe) and
    0x12fdf sit INSIDE the same packed table cluster [0x12e10..]; exact
    column semantics of the COMPARED cell pair pending census (C-W).
- Post-penalty tail (work/t207_w8/w11/w14 — the REST of 0x3a174, the event
  itself): counts gizmo-design 0x49 items on the invader unit
  ([ebp+0xab]+7i, count loop 0x3a2a6, cmp 0x49); counts planet slots
  item==0x12 (+2 if word+2 bit0) and item==0x13 active; writes out-param
  [ecx] = count (forced 1 if witness==-1); 0x3a362.. loop: for each gizmo
  0x49 slot on the unit, call 0x496e4 (slot rebuild) — the unit CONSUMES
  its 0x49 items; then loop over planet item==0x13 active slots calling
  0x38840(planet, slot, 1, 0xff) (item deactivate/removal — the Orbital
  Mega Shield 0x1d? check index identity! planitem ORDER: 0x12=? 0x13=? —
  NAME PIN PENDING); owner==current player [0x7458e] -> event announce
  0x55a60(0x7a35c, EDX=0xd, EBX=planet) code 0xd unless [0x7e582]>>16==0x10;
  vision 0x21da4(ship owner... star record); [planet+0x67] := [0x12e10]
  (owner record stamp); tail: call 0x38ba4 (the t45 governor/item
  activator) on the planet; return [esp+0xc].

### S6b — 0x396cc slot->unit getter VERBATIM (work/t207_w9.txt)
returns EAX = 0x3a095 + 0x162*unit_idx where unit_idx =
  word [[planet+0x10] + 4*slot + 2] >> 8 & 0x7f. Asserts slot < [planet+0x1a],
  slot idx < 0x6b, unit handle != -1. So the +0x17 slots hold HANDLES into a
  0x162-stride unit table at 0x3a095.

## C-W census questions (r207_witness_census.py)
1. Which stride makes [0x12fb3 + S*k] a per-race CONTACT/known flag:
   S=0x1ee vs S=0x3dc, judged by per-race variation across k=0..3 in saves
   vs the KNOWN BuildOnBlack row (t202 values 60.sav {r0:0,r1:2,r2:2,r3:0,r4:0}??
   re-measure) at 0x12fb3+0x1ee*owner.
2. [0x12fc8] 4x4 word submatrix (2*0x1ee stride cells) vs the DIPLO state
   matrix [0x12fd6]: read both for race pairs in 20 saves; predict state
   cells from relation states (t189b).
3. word [0x12fdf + 2*0x1ee*k] per k — compare against the race template
   row words (restree-independent): is it DECLARE_WAR threshold (+0x1c9)?
4. gizmo 0x49 + planitem 0x12/0x13/0x17 NAME PIN (count rows in the vendor
   txt files in order).
5. planitem count: rows list from extracted/ascend00/planitem.txt after '#'.

## S7 — VERDICT + CENSUS RESULTS (tools r207_disp_cluster.py,
r207_opinion_census.py RC=0; work/t207_disp.txt, work/t207_opinion.txt)

### S7a — scale-2 ALGEBRA CORRECTION (supersedes my S4/S6 draft)
The compiler splits 494 as 247x read with scale 2 (`[eax*2+0x12fb3]`,
eax = k*247): 0x12fb3 = diplo-row0 + 0x19d. So the "witness byte" at
0x3a20b is the t202 ABILITY byte row(k)+0x19d (distribution measured
{0:20, 2:20, 11:20, 19:20} = one race per value across 20 saves —
matches the t202 ability census EXACTLY). Likewise:
  [eax+0x12fdf], eax = 494*v  -> row(v)+0x1c9 = DECLARE_WAR threshold.
  [edx+0x12fc8], edx = 494*v + 2*a -> row(v)+0x1b2+2*a = the ATTITUDE
      CELL a->v (diplomacy.md S7 law). NO third-party matrix at this
      site — my S4 draft was WRONG; it is the same cell the handler just
      penalized, read back. (0x12fc8 remains the banked third-party
      matrix elsewhere: 0x447a0/0x274d3/0x45f52 write sites unchanged.)
All eight 0x12fb3 sites are scale-2 (r207_disp_cluster) — one table,
consistent.

### S7b — THE GUARANTEE-WAR LAW (NEW, cited): 0x3a25a..0x3a291 VERBATIM
0x3a174 (invasion resolution, see S7d) pays the handler at 0x3a255.
On the -1 return (handler 0x43a97: return 0 iff state==2 WAR, so -1 ==
victim NOT already at war):
  di = WORD row(v)+0x1c9 (DECLARE_WAR);
  cmp di, WORD[row(v)+0x1b2+2a]; jge skip;
  WORD[...] := DECLARE_WAR - 10.
=> AN INVASION ATTEMPT AGAINST A NOT-AT-WAR OWNER SLAMS THE VICTIM'S
ATTITUDE cell below the DECLARE_WAR line (if still above it — measured
200/200 non-war pairs sit at START_ATTITUDE 600 > DECL 210, so it always
fires in fresh campaigns). The t180 chooser (state==1: att < row+0x1c9 ->
DA_DeclareWar) then fires. INVADING GUARANTEES WAR. This is the invasion
sibling of the t204 BREAK_ALLIANCE ceiling — SAME clamp shape (+0x1cf
there, +0x1c9 here), same line-10 offset.
REWRITE VISIBLE -> WIRED (combatPhase player-capture path, see code).

### S7c — 0x39f00 = the GUN-BOMBARDMENT planet path (fire-and-forget)
Sole caller 0x4c97f sits in the gizmo-attack SHARED TAIL (span bookkeeping
0x4c794..0x4ca50; tsv overlap pitfall) gated VERBATIM by
`test byte [esp+0x40],1` (success) AND `cmp [esp+0x2c],1` (mode==1 commit)
AND `cmp byte [esi+0x32],0` (design category == 0 guns), AFTER the power
subtraction 0x4c960. Inside 0x39f00: BX (saved [esp+0x1c] word; read back
as dword [esp+0x1a]>>16 — compiler trick, bytes 0x1a/0x1b shifted out) =
attacker race idx, validated < word[0x13b98]; victim = planet owner byte
[esi+0x57], 0xff skips (asserts in-range else); EBX for the handler =
star record 0x13bc5+0x60*star([esi+0xa]) (t205 law); EAX = row base.
RETURN DISCARDED (0x39fbf overwrites). Tail (w1/w13): candidate scan over
ACTIVE planet items (word+2 bit0) with costs from 0x73e40-table
([0x73e46+0x28*item] cost word; also 0x3a0f8 planitem runtime stride-40
identity check 0x3a102 asserts UPOP byte==0), rng tie-break 0x3a07b, then
zeroes one slot byte+3 = DESTROYS/DEACTIVATES one item (shape; not fully
decoded). => ship-fires-gun-at-planet pays the dip price once, fire-and-
forget, plus a planet item-loss channel. Rewrite aggregate combat charges
the player per engagement (t204) and has no per-ship bombard channel ->
HONEST NO-DELTA for this caller; item-loss channel BANKED (no rewrite
per-item combat model; OQ-019 family).
*** t204's 0x4b875 lives in 0x4b740..0x4b8e3 (damage-apply, 6 callers,
t88a census re-run identical this session) — a DIFFERENT site in the same
module; the caller census of 0x43a4c is EXACTLY {0x39f00 via... no: the
three DIRECT E8 edges are {0x39fba, 0x3a255, 0x4b875} (re-verified this
session, full-image byte pass). Thread CLOSED: all three accounted.

### S7d — 0x3a174 = INVASION/CAPTURE RESOLUTION (t179 Leg A body)
Callers EXACTLY {0x3d951 (race.cpp-family span 0x3d2fe; context passes
word [rec+0xab] as slot idx — CONTEXT AMBIGUITY, [unverified], possibly
UI/cheat path), 0x42c8e (order-resolver engagement selection, the t179
invasion leg: owner-compare loop via 0x396cc + 0x39894 targetability)} .
Body: slot item MUST be type 0x17 'Ship' (planitem row 23) — 0x396cc maps
the slot handle to the ship record 0x3a095+0x162*idx; attacker EDX =
ship owner idx [ship+0x54]>>16; gate: owner 0xff OR ship-owner==owner.
ABILITY GATE 0x3a20b/0x3a349: ability byte row(attacker)+0x19d == 0 ->
witness -1 -> out param FORCED 1 (semantics open, [unverified]).
Then guarantee-war clamp (S7b). Then DEFENSE LAW (new, cited):
invmod = # of gizmo slots byte 0x49 (Invasion^Module, gizmos.txt row 73
of 76 — NAME PIN from file order; row byte0) on the ship (loop
[ebp+0xab]+7i, bound [ebp+0x15a]); shieldscore = #{ACTIVE item 0x12}
+ 2*#{ACTIVE item 0x13} over planet slots (0x3a2c9..0x3a325; active =
word+2 bit0); result = invmod>shields ? shields+1 : invmod (0x3a327..
0x3a33e). Then STRIP: every 0x49 slot rebuilt via 0x496e4 (0x3a362..
0x3a38d), 0x49acc full recompute; deactivate up to `result` ACTIVE item
0x13 slots via 0x38840(planet,slot,1,0xff) (0x3a3f7..0x3a45a); owner ==
current player [0x7458e] -> announce event code 0xd via 0x55a60 unless
[0x7e582]>>16==0x10; vision call 0x21da4(ship-owner star); planet+0x67
:= dword[0x12e10]; tail call 0x38ba4 (t45 activator); return local
[esp+0xc].
CORPUS WITNESS: r207_opinion_census A4 found >=1 record with gizmo byte
0x49 in EVERY save (20/20, count 13 constant) — [unverified] filter
(loose owner/slot-count bounds); mark window still ALL-ZERO t205/t206 =>
no invasion against a non-at-war owned planet was EXECUTED in captured
play: guarantee-war clamp has ZERO in-corpus witnesses (honest negative).

### S7e — rewrite delta (IMPLEMENTED + PINNED this session)
diplomacy.{h,cpp}: guaranteeWarOnInvasion(v, victimAtWar, attitude) —
no-op on at-war; clamp iff att > declareWar -> att = declareWar-10.
Wired in combatPhase capture branch (immediately after the repel test,
BEFORE owner_ flips): the one site where an invasion resolution is KNOWN
to have run. DOCUMENTED DIVERGENCE (honest): the original's 0x3a174 clamp
position relative to repel is UNDETERMINED statically (0x3a25a follows
the handler call directly, before any repel logic visible in this
function — arguably attempt-time faithful), and its gun-bombard caller
0x39f00 pays WITHOUT clamping; the rewrite conflates gunnery+invasion in
one aggregate engagement, so clamping at the capture branch UNDER-fires
vs an attempt-time reading. RESIDUES BANKED (keep row open):
(a) [CLOSED t208] positive end-to-end pin LANDED:
    invasion_capture_war_e2e_t208 — player gets SA_SuperMarines via
    CampaignConfig::playerSpecies -> ability_[kPlayer], industry cleared over
    the ship-cost gate via new setIndustryForTest; asserts capture ran +
    atWar flipped + att == 280 - negPlayerTurns/4 exactly. See
    docs/re/_wip_t208.md. (b) [CLOSED t209 — OUT-PARAM LAW MEASURED: callee
    0x3a35e `mov [ecx],eax` is the sole writer (full-body operand pass, no
    early ret, assert arms 0x2a428 don't return; ecx never rewritten before
    the store); value = defense-result, FORCED 1 iff ability byte==0 witness;
    neither caller pre-inits its slot; 0x42c8e DISCARDS out param AND return,
    0x3d951 (UI message family — context now MEASURED, closes (c)) reads
    [ebp-0x24] ==1 to pick message 0x1c vs 0x1d. docs/re/_wip_t209.md S1..S4.]; (c) [CLOSED t209
    via (b): 0x3d951 block = UI announcement family (0x56ca4/0x56d1c message
    ids 0x1fc5/0x1fd3, format call 0x76c79, UI words [ecx+0xcb1..0xccc])]
    (d) invasion DEFENSE LAW measured but unmodelled (invmod vs 0x12 +
2*0x13 shields, strip via 0x496e4/0x38840, event code 0xd) — per-ship
family, OQ-019 boundary; (e) ZERO in-corpus clamp witnesses (mark window
all-zero 20/20 — no invasion-vs-non-war-owner executed in captured play).
[DIVERGENCE NOTE CLOSED t209: clamp-vs-repel position MEASURED — clamp is
ATTEMPT-TIME (0x3a25a precedes defense-score loop; outcome branches only at
0x3a45c; caller 0x42c8e return discarded, outcome-independent control flow).
Rewrite capture-branch wiring = documented UNDER-MODEL, not divergence-by-
ignorance; per-attempt wiring stays OQ-019. docs/re/_wip_t209.md S5.]
Tests: invasion_guarantee_war_battery_t207 (6 arms incl JLE boundary,
idempotence, ceiling-not-floor), invasion_declare_war_cascade_t207
(340 -> -20 -> clamp 280 < DECL 290 -> chooser DeclareWar),
invasion_combat_phase_clamp_t207 (NEGATIVE side: engagement w/o capture
pays -20 only, 320). 133 tests 0 failed. BLAST RADIUS MEASURED: seed
2024 Control t1255 FINITE, seed 42 Extinct t979 FINITE — UNCHANGED (no
capture-by-player crossed the clamp in seeded autoplay).
