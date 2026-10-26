# aicode.md — AI turn-loop map (W6-A3, t90)

Static decode from work/ascend_restored.bin (base-0, OQ-011 pointer-law
image). Method: rel32 call-graph census over obj0 code [0x14bb0,0x82bb0)
(tool scripts/r1_t90_callgraph.py, RC=0, work/t90_callgraph.pkl) + raw
objdump -D -b binary -M intel per function. Nothing here was run against a
device; [verified] = instruction-verified this pass, [inferred] = reasoned
from verified sites. All addresses are image offsets (add P0 at runtime).

## 1. MASTER TURN FUNCTION — FUN_00024f24 [verified]

Entry FUN_00024f24 (size 0x983), EAX = campaign-state base (EBP; per-run
heap, never hard-code). Single caller: 0x55f06 inside FUN_00055df4 (the
END-TURN dispatcher; same function also calls the end-event-queue builder
family 0x46354/0x46524 and event 0x55a60 — score.md S5 banked).

Phase order inside the turn (call sites verbatim):

  P0 random-event window 0x24f32..0x24ffc [partial]:
     gated DAT_00010ba4 == -1 AND [state] >= 0x1388 (5000); three rng
     draws (0x7824f): /21, /5 +3, /0x4c +0x19 (=> 3..7 and 25..76 bands
     [inferred usage]); calls FUN_000226e4, 0x2351c, 0x238e8, 0x23388;
     then rng%6 + FUN_000232ec(state,0,edx) at 0x24fc6; 0x56d8c event
     lookup; virtual-call [obj+0xa7 hi]+0xc at 0x25000. (Semantics of
     these four = random-event module, NOT yet mapped — W6-A3 boundary.)
  P1 INCOME  0x2501c FUN_00025400 (wrapper -> FUN_0002547c, the
     player-command-exec / gun+ability commit site of combat.md S2h; the
     income channel law income-law.md S6 runs in that chain; also zeroes
     the scored-star counter DAT_00048300 (inc WORD @0x251a2 is its only
     writer seen in the walk) [inferred identity] and [ebp+4]=0).
  P2 ORDERS  0x25023 FUN_000255a4 (per-ship order sweep -> 0x2547c per
     command with ah==2 ability 0x39c10 / ah==3 gun 0x49f28 dispatch
     re-confirmed at 0x25569/0x25579; ah>=4 -> assert 0x2a438 — the S2h
     law re-observed from the TURN side).
  P3 RESEARCH 0x2502f FUN_00046aec(state @0x74744 stride 0x4b) — §3.
  P4 GROWTH  0x2503c loop FUN_00038f68 over the 123B planet pool
     (head ebp+0x18247, count [ebp+0x27281] hi-WORD) — the t81 law.
  P5 POP-CAP 0x25056 FUN_000252fc (calls 0x40ec0 ship list + 0x40f7c
     colony count — cap/recalc plumbing of the t29/t33 law) [inferred].
  P6 PER-RACE AI 0x25062..0x25088 loop over 0x1ee-stride race rows at
     ebp+6 (count [ebp+0xd86] hi-WORD == race count), SKIP iff row index
     == DAT_0007458e (player index), call FUN_0003e6e0(row); then
     0x250a5 call FUN_0003e6e0(0x12e16 + (idx*31*8)) for the PLAYER row
     (static table base 0x12e16, stride 0x1ee — diplomacy.md §10 matrix)
     but only for diplomacy upkeep? [inferred; the call is unconditional].
  P7 SCORE/OWNERSHIP 0x250aa..0x2523e (gated DAT_00010ba0 == -1): walks
     the 0x60-stride star-owner table at 0x13bc5 (count
     DAT_00016145 hi-word... loop uses ds:0x16145), tests star owner bit
     [star+0x15] bit<<race, and incs DAT_00048300 per owned star at
     0x251a2 — SCORED-STAR PRODUCER FOUND [verified]: DAT_00048300
     (owner-scan form) and per score.md S3 the printed DAT_000482fb is
     the same dword's byte/adjacent read (0x482fb vs 0x48300: 0x48300 is
     the INC target; OQ-021 row already keys on DAT_482fb — the producer
     walk here is the first cited writer path) [verified as producer of
     0x48300; the 0x482fb alias relation NOT re-measured this pass].
  P8 (tail 0x2524a..) FUN_00024274 / 0x24a34 events; 0x2532a 0x40ec0;
     per-race command exec loop 0x2542d..0x2546f calling FUN_0002547c;
     0x2554f FUN_00041260 (race.cpp giant, size 0x2010) = the AI command
     executor reached from the TURN (second caller besides 0x16eb0) —
     callees include 0x49f28 dispatcher, 0x4a55c, 0x40178 (ship orders),
     0x3ea08, 0x38818 (build cmd), 0x439f4 ally mask, 0x55a60 events:
     the AI acts (build+fire+order) through THE SAME command primitives
     as the player [verified by callee set].
  0x257cf FUN_00046fa0 research-queue copy (§3 note).

## 2. PER-RACE AI DECISION CHAIN — FUN_0003e6e0 [verified]

FUN_0003e6e0(EAX = 0x1ee-stride race row; row+0 == race byte, row+3 ==
status dword, 0xffffffff == eliminated/absent):

  0x3e6f0 status<0 -> eliminated branch:
     0x402d8 (§2c); if it returns <0: FUN_00040ec0 collects the race's
     ships (sort §2b) and the loop 0x3e71f calls FUN_00049d2c per ship =
     DEATH handler (combat.md S2g) — eliminated race's whole fleet is
     destroyed [verified]; event 0x55a60(code 0xb, race) per ship for the
     player race only.
  0x3e7a1 branch: if 0x40ec0 count==0 AND FUN_00040f7c==0 (no ships, no
     colonies): race EXTINCT — event 0x55a60(code 0xa), row+3 :=
     0xffffffff [verified: the elimination WRITER].
  0x3e7aa: for each of the race's ships: FUN_0004a74c (ship upkeep /
     at-reach, banked t85g range family) [inferred label].
  0x3ea54 FUN_0003ea54(EAX=row) — the per-turn decision block, §2a.
  0x3eae5 tail: counter row+0x19e++ (skip player row and row 0); if
     word table 0x6780[race+0x19a hi] <= counter: event 0x55a60(0x18) —
     the race timer cadence table (0x6780 stride 2, key row+0x19a) —
     W6-A6 SHIP_PATIENCE adjacent [verified structure, semantics open].

FUN_0003ea54(EAX=row) decision block [verified], in order:
  1. diplomacy update (skipped for the player row unless
     DAT_00010ba4 != -1, i.e. AI-controlling mode):
     0x3ecb8 ATTITUDE SCORER (t76 law) -> 0x3ef2c (relation-state
     propagation: reads [row+0x1c0+rel], gates on [state+0x12e19],
     0x77556 string ops — proposal/peace bookkeeping [inferred]) ->
     0x44690 PROPOSAL EMITTER (0x44fc0/0x454a4 proposal builders;
     relation tests [edi+eax+0x1c0]==0/1/2/3 ladder 0x4492c..0x44a0e;
     adjacency 0x44634; escalation 0x44a44) -> 0x3eb88 ally-bitmask
     rebuild via 0x439f4. [verified call order; each leg's internals
     cited in diplomacy.md where banked]
  2. BUILD: loop over the 123B planet pool base 0x2b057 (count
     DAT_0003a093 hi-word) [verified strides]; call FUN_0003f130 (the
     t28 build selector) IFF planet owner byte [+0x57]==race AND
     (player-row special cases) AND planet build-queue word [+0x5a]==0
     AND queue-slot byte [+0x54]==0xff — CONFIRMS the t28 "selector runs
     only on queue-empty planets" law from the caller side [verified].
  3. EXPANSION: if the race's target word DAT_00076492[race] == 0xffff
     -> FUN_00040018(row) (§2d picks + WRITES the target). Table census
     (objdump full-code scan): writers 0x22db7, 0x40164, 0x47880,
     0x47985, 0x47e34; clearers-to-0xffff 0x467d3, 0x46848, 0x47901;
     readers incl. ship-order path 0x3dc7f, 0x43f50, build cmd 0x390c7 —
     DAT_00076492 = per-race EXPANSION TARGET STAR (u16, 0xffff=none)
     [verified table; star-vs-other payload of the value inferred,
     0x40018's candidate loop is star-index based (0x46d3c tech-avail,
     restree rows) which makes star/star-record the reading].
  4. 0x43b50(row, 0) — race-level upkeep/maintenance (§2e).
  5. FLEET ORDERS: FUN_00040ec0 ship list (sort by design power), then
     per ship FUN_00040178(row, ship) (§2f).

## 2b. SHIP LIST FUN_00040ec0(EAX race byte, EDX out-array, EBX out-count)

Scans the LIVE owner table from 0x3a095 stride 0x162 (101 cap, bound
0x6b) — note t74 law: the static table at 0x3a095 keeps owner 0xFFFF;
0x3a095 here indexes the runtime array the t74 scan found live copies of
at heap corollary X — the AI uses [rec+0x54] hi-word as owner dword
[verified instruction: sar 0x10; cmp == race]. Collects ship ptrs,
sums ship counts [rec+0xa7 hi]+1 into *EBX, then SORTS the pointer array
with comparator 0x40eb4: `[[a]+0x52] - [[b]+0x52]` = DESCENDING design
design-power (design[+0x52] = weapon Level per t87 gizmo map — the AI
moves its strongest ships first) [verified].

## 2c. FUN_000402d8 "systems held +1" [verified]

Counts stars owned by the race in the 0x60-stride table 0x13bc5 (owner
[star+0x14], race bit <<[row+0]) then adds 1 iff the race holds its home
(bit [row+[7]+0x14]) — returns owned-system score; negative return feeds
the eliminated-race fleet-death branch. [semantics of the sign in the
caller: gate, open].

## 2d. EXPANSION PICKER FUN_00040018 [verified body, law below]

Candidate build: loop restree-runtime rows (count DAT_00074744, stride
0x4b at 0x7478b — research runtime array; the row's OWNED-mask dword
+0x47>>24 bit<<race gates: skip rows ALREADY owned... [verified test]);
legality via FUN_00046d3c(race, row) — tech-gate check: row prereq chain
(+0x40 5 slots, 0xff term) all owned in the mask [verified, mirrors
OQ-014 REQUIRES law]; collect up to 0x20 candidates.
SELECTION LAW (three tiers) [verified]:
  (i) copy 11 u32s from runtime 0x67be (45 halfword entries — the
     scenario-template PREFERRED list, same family as the OQ-016 preset
     preset residue) and scan candidates in candidate order for the
     first one present in the preferred list (inner loop 0x40105..0x40127
     caps the preferred scan at 0x17 pairs [verified]);
  (ii) if the race has bit in DAT_00074902 (a tech/race flag
     [inferred: Internet-style bonus]) rng%100 < 45 -> target := -2
     (a "free/skip" sentinel [verified store at 0x400da, meaning open]);
  (iii) fallback: rng % candidate-count uniform pick (0x4013f).
  Result -> DAT_00076492[race] [verified store 0x40164].
=> rewrite expansionPhase "nearest unowned BFS" is NOT the original law:
original = preferred-list-then-uniform-random over TECH-LEGAL candidates
[verified; note: this is research-row based (restree) — the expansion
target is a research/unlocked-location concept in this leg [inferred],
and the star-travel side (0x3dc7f reader) consumes it].

## 2e. FUN_00043b50(row, edx) race maintenance [verified skeleton]

Gate: word 0x6780[row+0x19a hi] > row+0x19e counter -> early return
(same cadence table as §2 tail). With edx==1: jump table [eax*4+0x2ef60]
on (row+0x19d - 5) & 0xff, cases 5..0xf (0x441c1..0x441d2) [decoded
range only]. Main leg (edx==0): per-ship integrity reset loop 0x43bd0
(ship+0x8c := ship+0x98 — integrity restored to MAX INTEGRITY, the t85c
+0x98 law, invoked at the race level) [verified]; attitude floor push
0x43c0a..: for every OTHER race row: other[row+0x1cb hi]+20 > other
attitude[row+0x1b2 hi] -> set other's attitude-toward-self word
[ecx+0x1b2] := that value (a global ATTITUDE FLOOR keyed to enemy
strength+20) [verified]; per-ship moves DOUBLING loop 0x43c5b
(ship+0x88 <<= 1) [verified instruction — ties to the t85g boundary
recharge: the recharge is x2, race-gated]. Star-table walk tail
0x43c79.. [not fully decoded this pass — W6-A3 residual].

## 2f. SHIP ORDER DECIDER FUN_00040178(race row, ship) [verified]

ship+0x58 = ORDER KIND byte; ship+0x59 = ORDER TARGET ptr; ship+0x5d =
AI-act flag; ship+0x5e = act-payload [field map verified from stores].
  - order kind in {1,2,5} -> RETURN (orders already assigned: kind 1 set
    by 0x4aa10 colonize-target, 2 by 0x4aa50, 5 = hold [inferred kind
    names, values verified]).
  - player-owned ship while DAT_00010ba4==0: clear +0x5d/+0x5e.
  - kind==3 -> ability-use: FUN_00039894(ship,+0x59) targetable? -> the
    0x39c10 chain handles activation (S2h ability commit path) [verified
    call].
  - kind==4 check follows: 0x2a428 assert-id 0x553 on fallthrough.
  - NO TARGET (+0x28==-1... tested [+0x28]; banked note: this field
    groups with +0x59 [verified store adjacency]) AND
    FUN_0004105c(race, ship)==0 -> +0x5d:=2, +0x5e:=target [verified].
  - Else if race HAS a current research target word (row+0x19b != 0)
    and ship empty (+0x8<=0 or +0xc>0, i.e. no cargo/capacity pressure
    [inferred]): scan the race ship list; FUN_0004aa10(ship, other)
    returns path-cost via table 0x45beb stride 25 formula
    ((idx*4-idx)<<3)*4 + target — the STARLANE distance law table
    (0x45beb, same table as the t28 threat-period lookup [verified base])
    -> pick MIN-distance owned ship; then FUN_0004aa10(ship, pick) sets
    +0x5d:=1, +0x5e:=pick [verified] = AI ships CONGREGATE toward the
    nearest friendly ship when the race has a research objective.
  - FUN_0004105c(race,ship) [decoded earlier leg 0x4105c, size 0x419 —
    not fully read; the +0x5d:=2 path = colonize/expansion act
    [inferred]].
=> rewrite has NO ship-order model (aggregate only); the original law is
   per-ship kind/target + congregation-to-nearest-friend [verified core].

## 3. RESEARCH PHASE FUN_00046aec(@0x74744 stride 0x4b) [verified]

Per race r (count DAT_00013b96 hi-word):
  PROGRESS[r] := 0
  for every PLANET p (123B pool 0x2b057, count DAT_0003a091):
     if owner(p)==r:
        if NOT (gov-type byte DAT_00013bc4 == 2 AND progress_word(p) <
           15): PROGRESS[r] += 1     [the growth-style +1 channel —
           same shape as the t81 population growth gate]
        PROGRESS[r] += RES-word p[+0x46]   [the research channel word —
        income-law S6 channel; stored u16]
  Then per race: pending tech word race[+0x1d4e] (0xffff = none);
  delta = PROGRESS[r]+1 (0 if 0); rounded f64 mul 1.2
  (0x3feb3333/0x33333333 push pair — 1.2x multiplier via mul_100-style
  idiom, fistp round) [verified constants]; race[+0x1d5c] += delta;
  if race[+0x1d5c] >= techCost(tech)[+0x3e]: SET owned mask bit
  race-tech-record +0x4a AND +0x4b (two mask dwords — tech bits for
  local + shared scopes [inferred]); clear pending (+0x1d4e := 0xffff,
  +0x1d5c := 0); player race -> event 0x55a60(0,0) + FUN_00046cac
  (post-completion hook, OQ-013 restree runtime) [verified].
=> the RESEARCH COMPLETION law is now cited. The PICK law (which tech
   becomes pending +0x1d4e) is NOT here: FUN_00046fa0 (0x257cf) is a
   QUEUE COPY (0x1d72-byte restree buffer copy, 0x46870 loader fallback)
   — the picker is elsewhere (W6-A4 target; candidate site census:
   0x46fa0 caller 0x257cf only; 0x20c48 = copy primitive). rewrite's
   uniform-random pick remains UNCITED (do not believe it).

## 4. Census numbers / tools

- call-graph edges: obj0 full E8 scan; 0x3f130 callers EXACTLY {0x3eade};
  0x3ecb8 {0x3ea75}; 0x3e6e0 {0x25083, 0x250a5}; 0x24f24 {0x55f06};
  0x41260 {0x16eb0, 0x2554f}. [verified via scripts/r1_t90_callgraph.py,
  exit 0 on the pinned expectations]
- DAT_00076492 writer/reader census: 19 sites (§2d list) [verified,
  full-code objdump grep — the R12 amendment file law: restored image].
- Jump table 0x2ef60 (11-case, keys row+0x19d-5) and 0x6780 cadence
  table: located, NOT decoded — named residual.

## 5. Residuals (what A3 did NOT close)

- P0 random-event module (0x226e4/0x2351c/0x238e8/0x23388/0x232ec)
  semantics — event CONTENT mapping, feeds nothing open directly.
- Research PICKER (which tech goes into race+0x1d4e) = W6-A4 proper;
  this pass narrowed it: picker runs before 0x257cf queue copy or in
  the AI command executor 0x41260 (its 0x38818/0x39894 callee set).
- FUN_0004105c (+0x5d:=2 act target) full body = W6-A5 adjacent.
- 0x43b50 star-table tail + 0x2ef60 jump-table case bodies = W6-A6/A7.
- ORDER KIND names {1,2,4,3,5} mapping to SOGoStar../SOAttack strings
  (0x88e60 block) — order enum numeric law STILL OPEN (A5).
- No ledger row closed this iteration (strict-close): findings are
  STRUCTURE (phase order + decision-site ownership), sufficient to
  de-risk A4/A5, not a constant/formula closure. OQ-016 row annotated
  with the caller-side confirmation + phase-order citation.
