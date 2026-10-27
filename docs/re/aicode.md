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

*** t101 REFUTATION of the two "main leg" claims above [verified raw
objdump 0x43b50..0x43cc3 + FILE 0x43b10 jump table 16/16]: there is NO
edx==0 maintenance leg containing these loops. 0x43bd0..0x43bee
(integrity := max), 0x43bf0..0x43c3d (attitude floor) and 0x43c3f..0x43c77
(+0x88 <<= 1) are the SA_HealShips / SA_ForcePeace / SA_DoublePower
ABILITY case bodies, reachable only via the edx==1 dispatch (0x43c3d is
`jmp 0x43bf9`, no fallthrough into 0x43c3f). The t90 sentence "the t85g
boundary recharge is THESE TWO sites" is VOID — the per-turn recharge is
FUN_0004a74c [ship+0x88] := 0x4a99c result = trunc([+0x18]*(1 +
clamp((T-[+0x52])//100,0,10)/10)), T = ds:0x12e10, called from the
FUN_0003e6e0 ship loop at 0x3e7b0 and from build completion 0x49d0d
(recharge multiplier maxes at x2 by age, which is what t85g saw as an x2
recharge). +0x88 = POWER (panel law, §6.4 NOTE below). Full trail:
docs/re/_wip_t101.md F1/F4/F7 + scripts/r1_t101_field_verify.py. ***

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

## 3b. RESEARCH PICKER — W6-A4 CLOSED (t91) [verified]

FIELD IDENTITY IS THE KEY. Turn call site 0x25028: `mov eax,0x74744;
call 0x46aec` — so inside FUN_00046aec the row base ESI = 0x74744 (restree
runtime), and 0x74744+0x1d4e == **0x76492** and 0x74744+0x1d5c ==
**0x764a0**: the "race research-target word race+0x1d4e" and the
accumulator +0x1d5c ARE the SAME table DAT_00076492[race]/DAT_000764a0[race]
whose writer census t90 ran for the expansion target. One table, one picker.

WRITE CENSUS (t91, exhaustive over obj0 code [0x14bb0,0x82bb0)):
- raw-byte scan for u16 0x1d4e: 6 hits whole-file, all INSIDE aligned
  insns 0x46bbb/0x46c11/0x46c36/0x46c53 (reads) and 0x46c67 (clear to
  0xffff) in FUN_00046aec + 0x46eea (indexed read in FUN_00046e84).
- raw-byte scan for u32 disp32 0x76492: 19 insn sites. WRITERS of a VALUE:
  **0x40164** (inside FUN_00040018 — the t90 "expansion picker"),
  **0x47e34** (research-window UI tail: stores selected row word
  [esi+0x9db] -> DAT_00076492[player] + sets owned-mask bit via
  FUN_0x46d3c legality + FUN_0004fb30 — the HUMAN picker); WRITERS of
  0xffff (clears): 0x22db7 (init loop, 8 races, paired 0x764a0:=0 at
  0x22dc0), 0x43f5b (row target == completed row -> clear + delta into
  0x764a0), 0x47880/0x47985 (UI clears). READERS: 0x390c7, 0x3dc7f,
  0x3eb05, 0x43f50, 0x44155, 0x467b9/0x4683b, 0x478b4/0x478d5, 0x48137.
- disp window scan 0x1d00..0x1dff over all mem operands: no other writer
  of the 0x1d4e/+0x1d5c pair anywhere in the image.

PICK GATE (0x3eaef..0x3eb1d inside FUN_0003ea54 decision block, §2a step 3):
  if DAT_00076492[race] == 0xffff -> FUN_00040018(row). Player row is
  skipped while DAT_00010ba4 == 0 (human controls; UI writer 0x47e34 is
  the human path) UNLESS DAT_000764ae != -1.

=> THE AI RESEARCH PICKER IS FUN_00040018 — the same function t90 banked
   as the expansion-target picker. The original models research target and
   expansion target as ONE per-race slot picked by ONE law:
   (i) rows 0..DAT_00074744 (restree runtime, stride 0x4b), skip rows whose
       owned-mask word [row+0x47]>>24 has the race bit, legality =
       FUN_00046d3c (row prereq chain +0x40, five slots, 0xff terminator,
       all must be owned); collect up to 0x20 candidates;
   (ii) copy 23 static u16s from 0x67be (preferred list — NO writers found
       at 0x67be..0x67d2, i.e. static data), scan candidates in order for
       the first member of the preferred list;
   (iii) if race has bit DAT_00074902>>24 (sole reader is 0x400b4):
       rng%100 < 45 -> chosen := -2 sentinel (skips the preferred scan,
       which only accepts candidates != -1/-2);
   (iv) fallback rng % candidate_count (0x4013f);
   store -> DAT_00076492[race] (0x40164). Preferred-list raw values
   (static, t91): 1007 f56 eb02 45b 700 aa10 200 2e10 1 1007 73 1002 12e
   700 4710 200 2e10 1 1007 2f c402 13b 700 (u16 LE; entry semantics
   interpretation NOT required for the law — the scan is membership-only).

ACCUMULATOR +0x1d5c / DAT_000764a0 reset sites (the "partner" t91 asked
for): FUN_00046aec zeroes it per-race at loop edges 0x46b90 and at
completion 0x46c75; per-turn value = SUM over owned planets of planet
+0x46 (RES word) + +1/planet gated (gov 0x13bc4==2 && word<15 && owner !=
DAT_0007458e), x1.2 f64 (0x3feb3333/0x33333333 pair) when nonzero — §3.

BUILD-COMPLETION CROSS-CHECK (kills the "AI picks research when a build
finishes" hypothesis): sole caller of FUN_00046e84 is 0x39173 inside the
item-completion branch of the build engine. FUN_00046e84 (EAX=0x74744,
DX=race) builds the candidate array (same skip-owned + FUN_00046d3c
legality), then if count>0: rng%count -> **marks that row OWNED directly**
(mask bytes +0x4a/0x4b |= 1<<race) and if race == player posts event
0x55a60(code 0x16). It NEVER writes the target word. So research can be
granted by build completion (AI free-tech grant) while the PICK stays in
FUN_00040018.

rewrite DELTA (t92 candidate, NOT done t91): researchPhase uniform-random
pick should become the FUN_00040018 law (legal-candidate build -> preferred
list -> rng%100<45 sentinel -> uniform), and the completion consumer stays
§3. [verified law; no code site changed this iteration — docs task.]

## 3c. t92 MEASUREMENT PASS toward the rewrite delta (no code site yet)

Picker body FUN_00040018 fully disassembled this pass (objdump -b binary -M
intel 0x40018..0x40175 on the restored image) — law as banked in §3b, with
three pinned details the rewrite implementation needs:
- candidate loop 0x4002e..0x40083: iterate rows 0..DAT_00074744-1 in ROW
  ORDER, skip if owned-mask [0x7478b + 0x4b*r]>>24 has race bit, legality
  call FUN_00046d3c(race,row) (prereq slots +0x40..+0x44, 0xff terminator,
  ALL must be owned — body read this pass: any-unowned -> eax=0 false),
  collect into stack array cap 0x20 ([esp+edi*2]).
- preferred scan 0x400e1..0x40134: OUTER loop over candidates in ascending
  order; head guard 0x400f4/0x400fb loads the chosen word ([esp+0x72]>>16
  == WORD [esp+0x74]) and `jne 0x40134` EXITS the scan whenever chosen !=
  -1. Inner loop 0x40105..0x40127 scans the 23 preferred words with its
  own chosen!=-1 re-guard (0x4010d) — so the match store 0x4012d executes
  exactly ONCE: the FIRST candidate (lowest row index) that is a member of
  the preferred list WINS [verified]. Preferred array = 46-byte copy
  (rep movsd 0x400af x11 + movsw 0x400b1) at [esp+0x40] from static
  0x67be; scan cap edx<0x17.
- sentinel 0x400b3..0x400da PRECEDES the scan: read moffs ds:0x74902
  (sole code referrer whole-image, re-censused this pass — only
  data-region false hits at 0x74903/9/13), bit test (flag>>24) & (1<<race);
  if set: rng%100 < 45 (idiv remainder compare 0x2d) -> chosen := 0xfffe.
  With -2 set, the very first outer iteration hits the 0x400fb exit (and
  0x4013b skips the uniform fallback for negative chosen), so the
  sentinel SHORT-CIRCUITS BOTH tiers. TRUE PRECEDENCE [verified]:
  sentinel(-2) > FIRST-preferred-member > uniform rng (0x4013f). A
  surviving -2 is STORED to DAT_00076492[race] at 0x40164 — and readers
  treat it as "target set" (gate 0x3eb1d tests ==0xffff), i.e. the race
  then behaves as having an objective that never completes until cleared
  elsewhere; semantics of -2 in consumers NOT re-measured (named
  residual).

LIVE FLAG MEASUREMENT (t92, scripts/r1_sav_scan anchors + corollary member
index B+0x82bb0+X): DAT_00074902 high byte = **0x0f** in the user's live
campaign slot (work/r1/playcap/save/60.sav, t=1254, 4 AI races) and **0x00**
in both r1deep scripted slots (50/52.sav). Same probe self-validated:
rowcount DAT_00074744==66 and row-0 mask +0x47==0xff030000 in all three.
=> the sentinel is SCENARIO-DRIVEN and in the shipped 4-race scenario EVERY
AI race is flagged: 45% of pick opportunities the AI researches NOTHING.
rewrite has no scenario flag model — t93 decision banked below.

PREFERRED LIST RAW VALUES re-verified byte-exact (0x67be, 23 u16 LE):
4103 3926 60162 1115 1792 43536 512 11792 1 4103 115 4098 302 1792 18192
512 11792 1 4103 47 50178 315 1792. MEMBERSHIP MATH FOR ROWS 0..65: only
the values **1** (twice) and **47** are in range — every other entry can
never equal a candidate row index (0x40123 cmp is a raw u16 equality). So
on the 66-main-row table the "preferred list" degenerates to {1,47}
[verified membership set; WHY vendor data holds junk entries is not needed
for the law]. The rewrite pin test must therefore use rows 1 and 47.

t93 IMPLEMENTATION DECISION (banked): apply the sentinel UNCONDITIONALLY
for AI owners to mirror the shipped 4-race scenario the measured flag 0x0f
represents. MODEL NOTE: the original stores -2 into the target slot; the
completion consumer 0x46bbb guard is `cmp eax,0xffff; jge skip` with a
zero-extended load, so -2 (0xfffe) PASSES the guard and indexes tech-cost
at row 0xfffe — vendor pseudo-target semantics NOT safe to copy blindly
(named residual §3c). SAFEST REWRITE MODEL: sentinel => that AI owner does
not pick and does not progress research this turn (queuedTech stays -1),
re-evaluated next turn — cite §3c in the code comment. The player keeps
the cheapest-cost default (unchanged). This is a behaviour change to every
AI timeline — regen all seeds + PLAYTHROUGH (t89 procedure), every seed
must stay FINITE < 1200. Pin test must use preferred rows 1 and 47 only.

## 3d. t93 CODE LANDING + §3c SENTINEL CORRECTION [verified t93]

CORRECTION (found by re-verifying the banked disassembly against the raw
objdump before implementing — the disassembly is ground truth, §3c's prose
was the misread): §3c/§3b said "a surviving -2 is STORED to
DAT_00076492[race]" and "the race then behaves as having an objective that
never completes". WRONG. The uniform-leg entry test 0x40134..0x4013d is

    mov eax,[esp+0x72] ; sar eax,0x10 ; test eax,eax ; jge 0x4015b

i.e. the uniform fallback at 0x4013f runs whenever chosen < 0 — INCLUDING
chosen == -2 from the sentinel store 0x400da — and OVERWRITES it
(candidates are non-empty here: count==0 exits at 0x40096 before the
sentinel). The store 0x40164 therefore never sees -2 from this path: the
picked value is always a real candidate row. TRUE LAW [verified]:
the sentinel skips ONLY the preferred-bias scan (guard 0x400fb exits it
when chosen != -1); a flagged race then picks UNIFORMLY at 100% of pick
opportunities, an unflagged race picks preferred-first when possible and
uniform otherwise. Effective effect of flag 0x0f (all shipped AI): the
preferred rows {1,47} bias is dead in the shipped scenario — research
content is uniform-random there; the bias tier still matters for unflagged
configurations (r1deep slots measured 0x00, t92). Consequence: the §3c
"no pick this turn" rewrite model is VOID; the named -2-consumer residual
(0x46bbb row-0xfffe index) is UNREACHABLE from the picker and demoted to
a curiosity.

IMPLEMENTED (t93, OQ-016 picker sub-law CLOSED-with-code-site):
- rewrite/src/game/campaign.h — Campaign::aiResearchPreferred(cand,
  sentinelHit): pure tier decision (sentinelHit => -1 skip; else first
  member of {1,47} in candidate order, else -1 => caller runs uniform).
- rewrite/src/game/campaign.cpp researchPhase AI branch — replaces the
  UNCITED uniform pick with the FUN_00040018 tier chain: candidates =
  tree_->available(...) row-order (== 0x4002e..0x40083 build incl the
  FUN_00046d3c prereq law), cap 32 (0x40044), one rng_ draw for the
  rng%100<45 sentinel roll (0x400c4..0x400d8, applied to every AI owner =
  the flag-0x0f shipped-scenario mirror), preferred hit or uniform
  fallback 0x4013f. Player path unchanged (cheapest-cost default; the
  human picker 0x47e34 is UI).
- TEST(campaign_research_picker_law_oq016): membership + first-wins +
  sentinel-skip edges on rows 1/47 (the only values that can match a
  66-row candidate, §3c math), plus a 60-turn campaign leg proving AI
  research still completes under the law. 110 tests 0 failed.
- Timeline re-measure post-delta (finite budget prevented the full
  PLAYTHROUGH regen script; numbers below are real headless runs
  --campaign 1200): seed 2024 Control t737 (was t777), 42 Extinct t688
  (was t581), 13 Extinct t503 (unchanged), 1 Control t836 (was t842),
  2 Control t657 (was t677). All FINITE < 1200. PLAYTHROUGH.md regen
  queued as the head of the next task.

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
  (0x88e60 block) — order enum numeric law STILL OPEN (A5); t94 pass below.

## 2f-supplement. ORDER ENUM CENSUS (t94) — values/stores/dispatch measured,
## numeric->name tie NOT made (honest negative, A5 stays open)

NAME TABLE [verified, restored image]: 8 NUL-strings stride 20 at
0x88e60 SONothing / 0x88e74 SOGoStar / 0x88e88 SOColonize / 0x88e9c
SOOrbitPlanet / 0x88eb0 SOPatrol / 0x88ec4 SODefendPlanet / 0x88ed8 SOAttack
/ 0x88eec SOGoSpace; pool-rel imms (imm=str_off-0x82BB0) 0x62b0 +20k.
R12-consistent reference census (scripts/r1_t94_so_imm.py + r1_t94_so_xref.py):
EXACTLY ONE code u32-imm to any of the 8 pool-rel names: 0x1dae5 -> 0x62b0
(SONothing base) inside the ship-info display function (formats ship pos
[+0x88]/[+0x8c]/[+0x94] floats against 0x831c9 at 0x1da83..0x1daac); the
site does `mov esi,0x62b0; call 0x2fb38; mov ecx,0x32; rep movsd` = relocate
+ copy the WHOLE 200-byte block to stack — i.e. the engine indexes names at
RUNTIME base + 20*k, no per-name immediate exists (this is why 7/7 other
names have zero direct refs — presence/absence R12 law, not proof of no
consumer). No u32 anywhere in the image points into 0x88e60..0x88f00
[verified, full-image scan].

STORE SITES (mov byte [ship+0x58], imm) [verified, scripts/r1_t94_order_census.py
— complements r1_t86 op set which lacks C6 /0; boundary-checked; 56 verified
sites in obj0, ZERO outside obj0]:
  imm 1: 0x3fb3e (fn 1267)
  imm 3: 0x39859, 0x49cd6
  imm 4: 0x2202f, 0x22127, 0x49db9
  imm 5: 0x22243, 0x2228f
  (no imm-0 or imm-2 stores; §2f says kind 2 written by 0x4aa50 — reg-form)
  [t107 CORRECTION (census-audit P2/P4, fixed tool r1_t106_writers.py +
  r1_t107_writers_full.py, both boundary-checked): imm-0 EXISTS at 0x24a00
  (assert-guarded `cmp BYTE [ecx+0x58],0` @0x249e3 then kind:=0 with WORD
  [+0x56]:=0xffff — command CLEAR path) and imm-2 at 0x3ca60 (ship ptr
  [edi+0xab]: kind:=2, [+0x59]:=[0x43508], then WORD [edi+0xb0]:=0xffff —
  a SECOND move-order issuer beside 0x22243/0x2228f). The t94 tool's window
  rejected both. Kind VALUE semantics unchanged: 0 = no-order/cleared,
  2 = move order, consistent with the §exec-semantics law.]
CMP-READER clusters: 0x40186..0x401fd (the 0x40178 decider itself: kind in
{1,2,5} -> early return; kind==3 -> 0x39894 targetable then 0x2a428 assert
0x54f; kind==4 assert-else 0x553), 0x21f7a/0x22035 (kind==5 exec path),
0x220f5..0x220ff (kinds 3/1/2 downgrade), 0x39510, 0x3e928, 0x41357..0x41d0f
(command-exec fn 2010), 0x42100..0x434c7 (fn 6087, five kind==4 gates),
0x49a44/0x49c1a/0x49c20/0x49f69, 0x4a7a6, 0x4aa2c, 0x4ab0a, 0x4cf2c,
0x5115f; plain reg-reads 0x4b18a/0x4b2fb/0x4b5f0/0x4b7fc/0x4e0e3/0x50d98/
0x52059/0x55c17 (UI/tooltip candidates — none shown indexing a 20-stride
name table within this pass).

EXEC SEMANTICS MEASURED (names the VALUES functionally, [verified]):
- 0x21f58(ship): iff kind==5: reads [+0x59] as STAR record ptr, matches
  ship-star against two slots ([eax] / [eax+0x4]), copies 3 f32 offsets
  (+0x08 / +0x14), jitters each with rng%200 (0x7824f), places via 0x49aa8,
  THEN stores kind:=4 (0x2202f). kind==4: just updates [+0x59]. => 5 is a
  "go-to-star" TRAVEL order consumed into 4 on arrival-at-star processing.
- 0x220a8(ship...): sets kind:=5 (+0x59 target) via 0x22243/0x2228f then
  calls 0x21f58 — the travel-order ISSUER.
- 0x220f2: kinds {3,1,2} whose FUN_00039894 target became un-targetable ->
  kind:=4 with [+0x59] := owning STAR record (0x13bc5, idx*0x60 law
  (idx*4-idx)<<5) — the "retreat to system" downgrade.
- UI dispatcher 0x1de40: `cmp bl,0x5; ja 0x1d9ab; jmp [ebx*4+0x8c90]` —
  a SIX-slot (values 0..5) jump table at image 0x8c90 whose entries are
  LE-FIXUP-encoded (raw u32 reads are garbage: 0x8e020fc5 etc. — NOT yet
  decoded; this is the A5 closer candidate: decode fixup records -> 6 case
  bodies -> each case's pushed string names its kind).

=> A5 STATE: value set {0..5} confirmed end-to-end (stores 1/3/4/5 + reg-form
2 + zero-default; 6-way UI dispatch table); functional semantics cited for
5 (travel-to-star) and 4 (in-system/after-arrival); SONothing is block slot 0
matching the zero-default reading [inferred, NOT closed]. rewrite delta: NONE
(aggregate-only rewrite, ANALYSIS-ONLY like the t90 map — cite in OQ-016 row).
NEXT A5 step: decode the 0x8c90 fixup table (LE fixup record format — see
docs/re/loader.md §4 notes on unapplied fixups) and/or live-capture the
relocated table via the pointer law, then read the six case bodies.

## 2g. JUMP-TABLE DECODE LAW + CASE BODIES (t95) — table cracked, name
## binding ONE step short (string-getter table base unreached, budget stop)

DECODE LAW [verified, scripts/r1_t95_jumptable.py RC=0, VALIDATED_SLOTS=3:
playcap/41, r1deep-20261008-190330/41, r1deep-20261007-224831/41]:
the 0x8c90 table is NOT at member B+0x8c90 (that member index holds obj1 POOL
data — the naive pointer-law read reads pool garbage, silently). The live LE
loader relocated the DISPATCHER'S OWN jmp disp32: image 0x1de4f is
`2e ff 24 9d <disp32 @0x1de53> jmp [ebx*4+0x8c90]`; live disp32 (member
B+0x1de53) = 0x1dcc90 = 0x8c90 + 0x1d4000 on all 3 slots (delta identical).
Table ENTRIES at member (live disp + 136), six u32 runtime addrs = img +
0x1d4000 with img in the gap [0x2a50,0x14bb0) (the sub-0x14bb0 CODE region
the restore tool never reconstructed):
  kind0 0x1dcdd9 img 0x8dd9 | kind1 0x1dcf9f img 0x8f9f | kind2 0x1dd06b img 0x906b
  kind3 0x1dd14d img 0x914d | kind4 == kind5 0x1dcdfb img 0x8dfb  (SHARED body)
obj0 code-region law REFINED [verified]: runtime = img + 0x1d4000 holds for
the WHOLE obj0 code span (low gap included, via the jmp-disp delta == the
OQ-011 0x140000+0x34000 home); pool law runtime = P0 + img (P0 = B-136) is
SEPARATE. BANKED TRAP: mem.find() hits are MEMBER indices — subtract H=136
before applying either law (name block found at member 0x248338 -> runtime
0x2482b0 == P0+0x88e60 EXACTLY, self-validating the pool law on t94's block).

CASE BODIES (live disasm, objdump on member windows; batmode.cpp is the
module whose debug strings sit inside the bodies' pool immediates):
- SHARED TAIL 0x1dcdfb (the SOPatrol-class tail; every case reaches it):
  formats via 0x2360c9 (sprintf-class) fmt '%s %s' (pool 0x24260d) with
  ship+0x54 hi-word -> (idx*57)*4 table 0x2b6590 entry (star record name),
  then 'POWER %d MOVES %d INTEGRITY %d' fmt 0x242619 with ship+0x88/+0x94/
  +0x8c (moves/z/?/integrity — matches t85g field identities), blit via
  0x1eef88, second dispatcher copy at 0x1dd290 (jmp [ebx*4+0x1dcc90],
  already-relocated encoding visible LIVE at runtime img 0x929f).
- kind0 0x1dcdd9: eax=3 -> call 0x1e0e70; body reads [eax+1]+0x1c.
- kind1 0x1dcf9f: eax=4 -> call 0x1e0e70; reads [ship+0x57], ==0xff falls to
  SHARED tail, else star-record indexed (idx*57 law).
- kind2 0x1dd06b: (no 0x1e0e70 head) builds '%s %s' from [ship+0x54]>>16 star
  + [ship+0x34].
- kind3 0x1dd14d: eax=8 -> 0x1e0e70; if [ship+0x23]&1 eax=9 -> 0x1e0e70
  (SECOND string); tests owner-bitmap bit ([ship+0x17] shl race DAT_2b658e)
  against star record [ebx+0x17]; fail -> shared tail.
- kind4/kind5: entry IS the shared tail (both kinds display identically —
  consistent with t94: 5 collapses to 4 on arrival).
STRING GETTER 0x1e0e70 [verified head]: EAX = index; bounds-checks EAX
against ds:0x254e0c (count) and on failure loads ebx=0x1ea ('INVALID ORDER'
at pool 0x242636 is in the error arm's string neighborhood); init gate call
0x1e0d04 when ds:0x254e08==0. THE TABLE ITSELF (base + stride) was NOT
reached before the budget stop — that is ALL that separates kind{0,1,3(+9)}
indices from the 8 SO-name strings.

A5 STATE after t95: the named t94 blocker (fixup table unreadable) is GONE —
table decoded, six case bodies disassembled, per-kind string-index calls
(3, 4, 8, 9) cited. NOT closed (strict-close): no case body pushes a name
literal; the numeric->name tie needs the 0x1e0e70 table dump. NEXT: read
0x1e0e70's full body live (member runtime 0x1e0e70-0x1d4000+0x14bb0+... i.e.
obj0 normal law — img 0x140e70, member B+0x140e70) to find its string-table
base+stride; dump entries; match to SONothing..SOGoSpace at pool 0x88e60.
Index set observed {3,4,8,9} > 8 names — either the getter table is a DIFFERENT
(order-description) string array than the SO block, or stride/base differ;
resolve by measurement, do NOT assume.
- No ledger row closed this iteration (strict-close): findings are
  STRUCTURE (phase order + decision-site ownership), sufficient to
  de-risk A4/A5, not a constant/formula closure. OQ-016 row annotated
  with the caller-side confirmation + phase-order citation.

## 2g-correction (t96): the "low gap" was a member-index artifact; case
## bodies ARE statically disassemblable, and the 0x8c90 table holds real
## Watcom LE fixup records (NOT pre-relocated reloc entries)

ADDRESS LAW RE-STATED (all three spaces, self-checked against
r1-savestate.md CLOSED law, [verified] t96 on playcap/41 B=0x1bf4d8,
H=136, P0=B-H=0x1bf450):
  F = restored/payload FILE offset (= image offset; files same size 0x8cc83)
  R = guest RUNTIME physical; obj0: R = F + P0
  M = save member index; M = R + H
  (1) r1_sav_scan B is a MEMBER index; the banked read form mem[B+x] ==
      P0+x is the POOL law (B = P0+H), NOT the code law — for obj0 CODE at
      file F the live bytes are at member F + P0 + H.
  (2) t95's "case bodies live at img 0x8dd9 etc." and "static region unread-
      able" were BOTH wrong: t95 read member indices as image offsets. The
      bodies' REAL file offsets are kind0 0x1d989 / kind1 0x1db4f / kind2
      0x1dc1b / kind3 0x1dcfd / SHARED tail 0x1d9ab, runtime = P0+F exactly
      (banked CLOSED law; t95's "img+0x1d4000" mislabels P0+F — 0x1d4000 is
      merely the Watcom SECTION base = P0+0x14bb0 for this object).
      Gate-check proof: restored[0x1d989:0x1d9a1] == live mem[0x1dcdd9+136:
      +152] EXACT (opcodes, no fixups inside); kind1/kind2/kind3 likewise.
  (3) restored[u32 @0x8c90] = 0x8e020fc5 ... are NOT garbage — they are the
      WATCOM LE FIXUP RECORDS for the jmp's memory-reference operand (0x8e =
      142 byte record length; the LE object header + fixup subobject were
      stripped in the restore, so the table region must be read per the LE
      fixup-record format, see loader.md; the t95 "disp+136" table read was
      reading 136 bytes PAST the real table start in member space and only
      accidentally returned sensible values — re-verify before use).

## 2g-correction-2 (t96): string-getter LAW + ACT enum (+0x5d) + display
## function identity — the 0x8c90 table is NOT reachable as "img 0x8c90"
## and its case bodies display static.txt strings, NOT the SO block

STRING GETTER LAW [verified, restored-file disasm 0x21a20 (t95's "live
0x1e0e70" = file 0x21a20 region, same function family; getter body:
bounds-check EAX against ds:0x12e0c count, table load `mov eax,[ecx*4+
0x10ba8]`): the table at DATA img 0x10ba8 is a RUNTIME-built array of char*
(count u32 at img 0x12e0c, arena img 0x10ec8..0x12e08 = 0x1f40 bytes, cap
assert 200 @0x218f5). INIT FUN_000218b4 [verified disasm]: opens
pool-rel 0xa1f = file 0x835cf = "static.txt", reads 200-byte records via
0x340e8, per record: first byte must be '"' (0x22), strips quotes, unescapes
\n, NUL-terminates, appends pointer to the table, count++ — i.e.
**getter(n) == nth quoted string of game/static.txt** (the Corn debug-string
catalog; error-arm file string '..\\corn.cpp' at 0x835da confirms module).
Live slot playcap/41 showed count 0 at runtime 0x12e0c (lazy init; never
called in that sitting). work/r1/game/static.txt EXISTS on disk — the n->
string map is a FILE, not the 0x88e60 SO block.

DISPLAY FUNCTION IDENTITY [verified]: the 0x1de40-family dispatcher + case
bodies + shared tail 0x1d9ab live in module batmode.cpp (pool strings
'%s %s' 0x60d/0x613, 'POWER %d MOVES %d INTEGRITY %d' 0x619=file 0x831c9,
'INVALID ORDER' 0x638=file 0x831e8). Case bodies call getter(n) with STATIC
n for LOCATION/STATUS text, not order names: case 0x1db4f (jmp-slot 1)
= getter(4) + 'Planet %s'-style build off [+0x57] (planet idx, 0xff=sentinel
-> tail); slot-2 body 0x1dc1b builds '%s %s' from star-name (0x74590
stride-57 table, name@+0x13, owner byte@0x12e18, idx*57=(idx*32-idx)*8
verified AGAIN) + getter(5)/getter(6)/(7); slot-3 body 0x1dcfd getter(8)
'Star Lane', bit [+0x23]&1 -> getter(9), owner-bitmap test via race byte
ds:0x7458e -> getter(10); tail 0x1d9ab = '%s %s' + POWER/MOVES/INTEGRITY
via 0x76c79 (sprintf). => THE 0x8c90 JUMP TABLE IS THE SHIP-PANEL STATUS
DISPATCHER, NOT THE ORDER-NAME MAPPING. The A5 name tie does NOT run
through it (t95's premise, voided).

+0x5d ACT ENUM CENSUS (imm8 stores, verified, regex C6 4x 5d over obj0):
  0 (NO_ACT): 0x41a30 (target==self/own star reset), 0x41bff, 0x41c26
    (target kind!=4), 0x41c98 ([+0x84]&8), 0x41ced ([+0x57]!=0xff), 0x41dab,
    0x460d9, 0x499e5  — 8 sites, all in command-clear paths (fn 2010 family
    0x41b8f shared exit).
  1: 0x45e31, 0x4aa50 — 0x4aa50 site: target==[ship+0x59] guard, then
    +0x5d:=1 AND +0x5e:=esi (object) — MOVE-TO-OWNED-TARGET class (t94
    already saw +0x5e; the +0x5d half was missed).
  2: 0x40224 — after FUN_0004105c(ship,+0x59 target) returns nonzero then
    +0x5d:=2, +0x5e:=eax (result) — 0x4105c = "legal act on target?"
    decider (walks table ds:0x13b98 count).
  Companion dwords: +0x5e = ACT TARGET OBJECT POINTER (0x4aa54, 0x40228
  store pair; display reads it at 0x1deb9/0x1dee5 adding +0x1c/+0x24 =
  object NAME fields (star rec +0x1c, planet rec +0x24 — consistent with
  0x1ddd5 tail append ebx+0x1c)).
  NOTE t93's aicode claim "FUN_0004105c (+0x5d:=2 act target)" is
  CORRECTED: 0x4105c DECIDES legality; the store is at the CALLER 0x40224.

SO NAME BLOCK remains the only order-name evidence; code-side tie NOT yet
measured (exec paths use +0x58 kind numerically; display uses static.txt).

## 2h (t96 FINAL BANK). GETTER LAW CLOSED + PANEL STATUS-TEXT LAW + SO-BLOCK
## residual. Honest state of W6-A5.

STRING GETTER CLOSED SUB-LAW [verified, restored disasm FUN_00021a20 +
init FUN_000218b4 + LIVE playcap/41]:
  getter(n): bounds-check n vs count ds:0x12e0c (= P0+0x959bc runtime),
  return table[n], table at data-intra 0x10ba8 => F 0x93758 => runtime
  P0+0x93758 (live dump of 191 entries decodes to the static.txt strings IN
  FILE ORDER: 3 'Sun %s', 4 'Planet %s', 5 '\nOwned by %s', 6 '\nMoving to
  Star Lane', 7 '\nMoving to Planet', 8 'Star Lane', 9 'Red Link', 10 ' to '
  — exact match to work/r1/game/static.txt, 191 quoted strings, count live
  = 0xbf = 191). INIT reads pool-rel 0xa1f = 'static.txt' (file 0x835cf),
  200-byte records via 0x340e8, quote-strip + \n unescape, arena
  0x10ec8..0x12e08 intra (0x1f40 B, cap assert 200). So index->string is
  FILE-DRIVEN (static.txt), NOT the 0x88e60 SO block.

PANEL PANEL-STATUS DISPATCHER, law entry-0x1d4000+0x14bb0=F [verified,
clean STATIC table at F 0x1d840 = live entries - 0x1d4000 exactly; NO fixup
decoding was ever needed — t95's "fixup-encoded garbage" came from reading
member B+0x8c90 (obj1 pool data) and from forgetting the +0x14bb0 code-obj
intra base: cs-relative 0x8c90 == F 0x1d840, cs base = code obj start]:
  kind0 F 0x1d989: sprintf(getter(3) 'Sun %s', star->name [objptr+0x1c])
  kind1 F 0x1db4f: getter(4) 'Planet %s' + [+0x57] planet idx (0xff sentinel
          -> shared tail); then '\n...' append via [0x12e18+idx*57 owner byte]
  kind2 F 0x1dc1b: '%s %s' (0x60d) star-name; if star==own star (ds:0x7458e)
          && act!=0: act==1 -> getter(6) '\nMoving to Star Lane' else
          getter(7) '\nMoving to Planet'; else getter(5) '\nOwned by %s'
          (display's OWN copy of the +0x5d law, consistent w/ census)
  kind3 F 0x1dcfd: getter(8) 'Star Lane'; [+0x23]&1 -> getter(9) 'Red Link';
          owner-bitmap (race shl ds:0x7458e vs [owner+0x17]) fail -> tail
  kind4==kind5: entry IS shared tail F 0x1d9ab (panel default: name+coords+
          'POWER %d MOVES %d INTEGRITY %d' fmt 0x831c9 via sprintf 0x76c79);
          'INVALID ORDER' (0x831e8) staged at 0x1daf6 with guard cmp
          [ship+0x5d],7 (act enum valid 0..7 — display-side corroboration).
  => THE TABLE MAPS KIND -> STATUS TEMPLATE, NOT KIND -> SO NAME. t95's
  premise that this table was the A5 name tie is VOID.

SO NAME BLOCK RESIDUAL (A5 stays OPEN, strict-close): block = 10 entries
stride 20 @F 0x88e60: SONothing SOGoStar SOColonize SOOrbitPlanet SOPatrol
SODefendPlanet SOAttack SOGoSpace BAD BAD. Tension: kinds verified {0..5}
(cmp bl,5) vs 8 named entries — block indices are NOT kind indices
[inferred from entry count; NOT closed]. Only code reference: 0x1dae5
`mov esi,0x62b0; call 0x2fb38 (R12 adjust helper); rep movsd ecx=0x32`
= copy the whole 200-B block to [esp+0x10] inside the display fn; NO reader
of [esp+0x10] found in scan window 0x1c000..0x1e500 (8- and 32-bit esp-rel
patterns) — the kind->SO-name tie is made by some OTHER consumer (order
menu builder, likely adjacent batmode.cpp UI) or the block feeds a callee
by address; NOT measured this session. NEXT hammers: (1) disasm R12 helper
0x2fb38 law bank; (2) census ALL adjust-helper sites + 20-stride indexed
reads; (3) the two dispatcher twins 0x1de40/0x1dd290 region's remaining
undecoded arms. rewrite delta: NONE (ANALYSIS-ONLY).

## 2i (t97 BANK). SO-BLOCK CONSUMER PASS — honest negative, hammers (1)/(2)
## exhausted, helper 0x2fb38 identity + live block verification + tail-pool law

HELPER 0x2fb38 OBSERVED LAW [verified, restored disasm + 106 rel32 caller
census, tool scripts/r1_t97_so_consumer.py]: it is NOT an "R12 adjust" and
NOT the string-relocation mechanism. Body: saves esi/edi/ebp; EAX=arg1 ->
esi; EDX spooled; stack args [esp+0x44..0x50]; tests arg bit (al&0x80);
conditionally calls 0x5e940(esi+8, value); writes ONE byte at [[esi+4]+0xf3];
restores regs. Caller census = 106 sites across the whole string-staging
zones (0x14cf8..0x5aa5f) — it accompanies the Watcom staging idiom (5x movs
copy 20 B code->BSS @0x7d382/0x7d38a + fixed sentinel pushes), i.e. debug/
bookkeeping scaffolding around staged immediates, NOT a pointer converter.
RELOCATION IS STILL THE LOADER'S JOB (OQ-004 law stands): the imm at site
0x1dae5 (static 0x62b0) reads P0+0x88e60 in LIVE RAM — RE-VERIFIED t97 in
work/r1/playcap/save/60.sav (B=0x1bf4d8, member index B+F): block bytes at
B+0x88e60 decode SONothing/SOGoStar/SOColonize/SOOrbitPlanet/SOPatrol/
SODefendPlanet/SOAttack/SOGoSpace/BAD/BAD exactly (tool
scripts/r1_t97_pooltail.py RC=0). Harness note: playcap saves live under
work/r1/playcap/save/*.sav (not playcap/*.sav).

POOL-TAIL NOTE [verified]: pool-rel immediates in the display fn range go
past the restored image end — pool-rel 0xa0e0 -> F 0x8cc90 > image end
0x8cc83; live B+0x8cc90 reads BSS zeros/binary (NOT a string); B+0x8ccd8+
carries the .txt name table ('batfx.txt','cosmos.txt','end-capt.txt'...).
The invalid-act tail 0x1defe (mov edx,0xa0e0; mov eax,0x7a35c; call 0x55240)
takes a BSS buffer + a CODE address (0x7a35c bytes are code) = debug/assert
scaffolding; NO SO-name tie there.

DISPLAY FN FULL EXTENT [verified, objdump walk 0x1d989..0x1df18 ret, rets
at 0x1df18/0x1e695/0x1e9d9/0x1ef98 bound adjacent fns]: the fn containing
the 0x1dae5 whole-block copy ENDS at 0x1df18; across that extent NO read of
the [esp+0x10] SO staging slot exists (t94's window conclusion extends to
the whole function). The act-dispatch arms 0x1de9c (cmp [+0x5d],1/2) build
the target-name APPENDAGE from [+0x5e]+0x1c (star name) / +0x24 (planet
name) via staged-copy + call 0x2fb38, then fall to 0x1defe; names used are
static.txt + record names, NOT the SO block.

20-STRIDE INDEXED CENSUS (hammer 2) [verified, 152,831 insns obj0,
imul *,*,0x14 | lea *,...,*0x14]: exactly 6 sites — 0x22904, 0x22a60
(debug printf arg tables indexing ESP frames, fmt pool-rel 0xb42/0xb49,
NOT any string pool) and 0x36fb8/0x36fe5/0x37027/0x3705a (context = order
validation printf cluster, same esp-frame indexing class). NO indexed read
of a pool-string base exists anywhere in obj0.

VERDICT (strict-close): kind->SO-name numeric tie STILL NOT MEASURED. The
block's only code touch remains the whole-200-B copy at 0x1dae5 whose
destination slot is never read inside its function. The "internal debug
identifier" reading is PLAUSIBLE but NOT supported by any cited
debug-format/assert-name string tie, so per the t97 rule the OQ-016 row
STAYS OPEN. Named hammers for t98: (A) WATCOM DEBUG INFO in game/ascend.exe
(LE format; SO block @file 0x8b8b0; a symbol table naming the block directly
is the cleanest possible closer — first ID-Info/object-table parse attempt
this session failed on record-format assumptions TWICE, so use the
documented WLINK ID Info record layout or a known tool, not guesswork);
(B) the twin dispatcher region 0x1dd290 undecoded arms; (C) live-RAM: read
the [esp+0x10] copy at runtime is NOT possible from saves (stack transient).
rewrite delta: NONE (ANALYSIS-ONLY, unchanged).

t97 COMPLETION (same session, hammers (1)-(3) exhausted):
- POOL-REL IMM CENSUS CORRECTION [verified]: t94 scanned only the static
  file form (0x88e60+); a pool-rel form census (0x62b0..+200) yields 14
  byte-scan candidates, of which disassembly adjudicates 13 as DECODE
  ARTIFACTS (unaligned u32 windows overlapping mov-immediates: e.g.
  0x30b2d/0x41b74/0x41c33/0x41dcd `mov [reg+0x63],0`, 0x52884 `mov
  ecx,0x62`, 0x6007b/0x174f2/0x6ae7b mid-data). REAL imm into the block:
  ONLY 0x1dae6 (the display whole-block copy). Lesson banked: string-imm
  censuses must be decode-boundary-verified (scripts/r1_t97d_jmptables.py
  shows the pattern).
- LIVE-POINTER CENSUS (t97b, scripts/r1_t97b_liveptr.py, self-validated
  playcap/save/60.sav, B=0x1bf4d8, P0=0x242088): ZERO u32 anywhere in the
  full 16-MiB guest RAM (all byte phases) holds a relocated address into
  the SO block 0x2caee8..0x2cafb0. The block is never pointed at from any
  heap/BSS/stack structure at turn-boundary state.
- JUMP-TABLE FULL CENSUS (t97d, decode-verified, obj0): 9 computed-jump
  sites total; the ONLY one in the batmode display zone is 0x1de50 -> F
  0x1d840 (the t96 status-template table, entries re-dumped identical:
  0x1d989/0x1db4f/0x1dc1b/0x1dcfd/0x1d9ab/0x1d9ab). NO second kind-keyed
  table exists; hammer (3) (0x1dd290 "twin") is INSIDE the kind3 arm
  already fully disassembled at t96/t97 — no order-menu builder there.
- CONTRAST EVIDENCE [verified]: sibling pool name tables that the engine
  DOES consume are referenced per-name by immediates — dip-state cluster
  (pool-rel 0x64a4 'Peaceful'/0x64b8 'Hostile'/0x64cc 'Peace'/'War'@
  0x64e0/'Alliance') has 62 aligned imm referrers in obj0. The SO block
  has exactly ONE referrer (a whole-block copy whose slot is never read).
  Structural signature of a DEBUG symbol table, NOT a UI table — but no
  cited debug-format string ties names to kind numerics, so A5 REMAINS
  OPEN (strict-close).
- LE HEADER (t97c, scripts/r1_t97c_le_debug.py): ascend.exe delta
  exe-file = image-FILE + 0x2a50 confirmed byte-wise (block at exe
  0x8b8b0). Object-table parse at DW(le+0x30) breaks at obj 47 — format
  assumptions wrong TWICE (name-count semantics); do NOT re-guess in
  t98 — fetch the WLINK ID-Info/object-table spec FIRST (user policy:
  firecrawl pre-approved; GOAL says no network fetches — the firecrawl
  pre-approval is the standing user override, confirm with user if in
  doubt), or scan the debug region structurally: no u32==0x8b8b0/0x88e60
  exists in the whole exe (t97c), so a symbol tie, if present, encodes
  the address in object/segment-relative form — parse segment table
  (offSegTab DW(le+0x34)) before object-relative arithmetic.

## §2i — t98 WLINK DEBUG-INFO VERDICT: exe carries NO symbol table; the
## SO-name tie is UNMEASURABLE from the binary (cited negative)

Spec-first per t97 rule. Layout source: IBM OS/2 16/32-bit Linear eXecutable
Module Format (LX) Specification rev 11 (14 Jun 2001), fetched
https://archive.org/download/IBMOS2Warp4ToolkitDocuments2/lxref.htm (cached
~/.hermes/cache/web/archive.org-c9e087b277.md). Tool:
scripts/r1_t98_wlink.py (RC=0; structural seals below, verdict printed).

STRUCTURE [verified byte-wise on game/ascend.exe, 0x8f6d3 B]:
- LE header at DW(0x3c) = 0x2a50, sig 'LE'. WATCOM variant KEEPS IBM field
  positions: objtab = le+DW(le+0x40) = file 0x2b14; obj page table =
  le+DW(le+0x48) = 0x2b44; resident name table = le+DW(le+0x58) = 0x2d28
  parses CLEAN per spec §2.7 as module name 'corn'; entry table = 0x2d30
  (adjacent). TILING SEAL: objtab 2 objects x 24 B (WLINK object entry = 20
  IBM fields + 4) ends EXACTLY at the obj-page-table pointer; page table
  121 x u32 (DW(le+0x14)=121) ends EXACTLY at the resident-name-table
  pointer. Three independent header pointers tile byte-exactly -> the
  header reading is sound.
- LOADER SECTION (DW(le+0x38)=0x149b1) at le+0xb8=0x2b08 ENDS EXACTLY at
  DATA PAGES OFFSET DW(le+0x80)=0x17600. Demand pages run 0x17600..EOF.
- THE SO BLOCK (exe-file 0x8b8b0, t94/t97 pinned) lies INSIDE the demand-
  page span: it is plain loaded image data, not a table of the container.
- t97c BUG ROOT-CAUSED [verified]: it parsed "object table" at DW(le+0x30),
  which per spec fig 3-7 is FIXUP SECTION SIZE (value 0x14794 -> parse
  started in the loader-tables/file-pages border = garbage at obj 47). The
  "name-count semantics" premise was a phantom — the LE object table has NO
  name strings AT ALL (spec §2.4: 20-byte fixed numeric entries).

DEBUG INFO [verified, two independent ways]:
1. Header walk: DEBUG INFO OFF = DW(le+0x98) = 0, DEBUG INFO LEN =
   DW(le+0x9c) = 0. Per spec §2.2 note ("Table offsets ... may be set to
   zero to indicate that the table does not exist in the EXE file") the
   debug section DOES NOT EXIST in ascend.exe.
2. Brute signature scan whole file: 'NB03' 0, 'NB00' 0, 'NB02' 0, 'ODIAG'
   0, 'DWARF' 0, 'OS21001' 0 (spec §2.18 defines the NB0n signature; the
   'WATCOM' 4 hits are the DOS-stub stub-strings 0x371/0x3c7 and two
   runtime in-image strings 0x7ad76/0x7ada7 — not debug records). No
   '.obj'/'.OBJ' module-name vocabulary anywhere; 'shiporders' 0.
3. Each of the eight SO names occurs EXACTLY ONCE in the whole file — at
   its own slot in the block (0x8b8b0..0x8b93c). No second copy, no
   nonresident name table (DW(le+0x88)=0), no symbol referencing them.

VERDICT (strict-close): the kind/act -> SO-name mapping CANNOT be tied by
symbol table because ascend.exe was SHIPPED WITHOUT DEBUG INFO (cited
header fields + zero signatures). Combined with t97 (no live-RAM pointer
into the block; sole static referrer = whole-200-B copy at 0x1dae5 whose
stack slot is never read; zero pool-rel immediates to name entries beyond
that copy), NO measurement route to the association remains: the block is
a debug-leftover name array that survived into the shipping image,
consumed by nothing. A5's residual is reclassified: UNMEASURABLE-BY-ANY-
REMAINING-ROUTE, closing note per t97 rule (debug-only identifiers; the
kind->USER-visible mapping lives in game/static.txt ONLY — t96 STRING-
GETTER LAW).

SUPPORTING READING [inferred, kept for the record, NOT a closure]: the
eight names SONothing/SOGoStar/SOColonize/SOOrbitPlanet/SOPatrol/
SODefendPlanet/SOAttack/SOGoSpace index 0..7, and the ship-panel display
fn stages 'INVALID ORDER' behind guard cmp [+0x5d],7 (t96 §2h) — the ACT
field domain matches the array extent. Whether index==act value was NEVER
measured (no consumer reads the array), so per strict-close it stays an
inference. The earlier t96 note "block indices != kinds [inferred]" used
kind domain 0..5 (+0x58); the act domain 0..7 is the closer fit — either
way, unmeasured.

ROUTE STATUS: LE-debug route KILLED (REFUTED-ROUTES R14). Next named work
per assignment branch (fail): W6-A6 = 0x43b50 race-maintenance tail +
0x2ef60 jump-table case bodies (aicode.md §438 reference).

## 6. (t99) W6-A6 CLOSED: FUN_00043b50 = PER-RACE SPECIAL-ABILITY CADENCE
## ENGINE — tail, dispatch, all 16 bodies, field meanings CITED.
Tool scripts/r1_t99_maint_census.py (RC=0; table/callers/store-census;
objdump needs -D not -d on binary-format images). Full working notes:
docs/re/_wip_t99.md F1-F20.

### 6.1 Extent + shape [verified]
0x43b50..0x44029. Gate: WORD[0x6780 + 2*(row+0x19a>>24)] > row+0x19e ->
return -1 (not-due). edx==1 -> dispatch 0x441c1; ELSE return -1 IMMEDIATELY
(0x43b9c — every body is reachable ONLY through the jump table). Jump-table
operand `jmp cs:[eax*4+0x2ef60]` = restored FILE 0x43b10 (+0x14bb0 law, t96;
raw 0x2ef60 = pool garbage, pinned by tool). Key = (row+0x19d-5)&0xff,
in-range 0..15; out-of-range -> 0x4400a = counter-bump exit.
EXITS: T1 0x4400a row+0x19e := [esp+0x6c8] (0 for all bodies — counter
RESET on fire); T2 0x43fe5 (profile-13 body tail) row+0x19e := cad - cnt.

### 6.2 THE DISPATCH KEY IS THE SPECIAL ABILITY NUMBER [verified]
row+0x19d sole writer 0x4460f (raceneg.cpp loader FUN_00044290,
RACE%02d.DIP parser: 15 DIPVALUE keys -> row+0x1c7..+0x1e5 words, incl
+0x1c9=DECLARE_WAR/+0x1cb=ACCEPT_PEACE per diplomacy.md L177) stores
[row+1]; runtime law live-verified (60.sav rows 0..3: +0x19d == byte+1 ==
dword[+0x19a]>>24 = 19/2/11/0 = Chamachies/Orfa/Ungooma/eliminated).
help.txt 'abil%02d'/'abres%02d' sections (rewrite species.cpp ALREADY
parses, 21 blocks) name the ability per index; the UI caller 0x37cb1 opens
'abres%02d' with the profile. LIVE: player=19, Orfa=2, Ungooma=11.

### 6.3 CASE BODIES (profile -> cited effect; vendor text 1:1)
 5 SA_HealShips 0x43baf: every own ship +0x8c := +0x98 (integrity=max).
 6 SA_ForcePeace 0x43bf0: every other row: if [x+0x1b0]>>16 <
   ([self+0x1cb]>>16)+20 -> [x+0x1b2] := that (attitude floor toward self
   at ACCEPT_PEACE threshold + 20 — the forced-peace push).
 7 SA_DoublePower 0x43c3f: every own ship +0x88 <<= 1.
 8 SA_RepelAlienShips 0x43c79: stars with own owner-bit byte+0x14: ships
   with owner!=self && order-kind [s+0x58]==4: 0x220a8(star)+0x21f58(self,
   ship) re-place at the star (jittered).
 9 SA_SapAlienPower 0x43d33: stars byte+0x15 (lane/in-system) own: alien
   ships +0x88 := 0.
10 SA_Cornucopia 0x43de4: own planets (skip [p+0x16]==10): track MIN word
   [p+0x42]; on that planet every slot class byte in {0,1} := uniform pick
   {2,3,4} (pool 0x6838 u32 x3, rng 0x7824f %3) — "least populated colony
   into a rich world"; class values = t35 chain barren0/normal/rich.
11 SA_BumpShipsInLanes 0x43e98: live sys table 0x3a095 stride 0x162 (count
   DAT_0x43489 hi): [sys+0x58]==5 lanes with owner: ship := at lane star
   via 0x21f58 (the t85c reversal!).
12 SA_StealTech 0x43eec: research rows i (cursor edi=i*0x4b added to the
   raw data-intra 0x7478b — operand = research RUNTIME ROW byte +3 =
   per-race OWNERSHIP bitmask; live row0 dword 0x0f000000 -> mask 0x0f =
   all 4 races own it at t1254, consistent): popcount(mask)>>=2 -> own bit
   ORed INTO the mask (the steal); if row == own target (0x76492[2self]==i):
   target := 0xffff (re-pick next turn) + accumulator recompute.
13 SA_Shield 0x43fba: own planets: dword [p+0x62] := 0xffffffff
   ("invincible for one day"; T2 exit preserves phase).
15 SA_KnowStarLanes NOP (passive) | 18 SA_FastLaneTravel NOP (0x4400a).
16 SA_BlockStarLanes 0x4405f: own stars' lane entries (sub-array [star
   +0x42] words, entries [star+0x2c+4k]): byte[+0x23] |= 2 (block bit).
17 SA_Hatred 0x440b5: every other row state [r+0x1c0]==2 (AT WAR): for
   every third x (not self, not r): if [x toward self +0x1b2] >
   [r+0x1c9] (war's DECLARE_WAR threshold) -> [x+0x1b2] := [r+0x1c9]
   (make aliens dislike the enemy down to the war threshold).
19 SA_FreeResearch 0x4414e: own target t!=0xffff: 0x764a0[2self] :=
   WORD[0x74782 + 45*t] (research cost word — live 50/90/100 for rows
   0..4) = set progress to cost = "complete in one day".
   *** t105 CORRECTION [verified, byte-pinned 0x4416b..0x44189 + live
   66/66]: the index math is lea 4t / add t / shl 4 / sub = 75*t, NOT
   45*t: 0x74782 is the ROW-0 runtime COST WORD of the research-state
   table (record base 0x74744, stride 75 == the OQ-013 restree runtime
   law cost@+62). There is NO independent stride-45 table. Verify tool
   scripts/r1_t105_verify.py leg 2+3. ***
20 SA_IndustryBoost 0x4418e: own planets ([p+0x54]!=0xff): WORD [p+0x50]
   += 100 (build accumulator per income-law live measurement).

### 6.4 CADENCE LAW + TABLE (0x6780 = ABILITY CHARGE DAYS) [verified]
Counter row+0x19e: +1 per turn in FUN_0003e6e0 tail (0x3e7cf..0x3e805) iff
[[row+7]+0x14]&0x80 (AI-enable scenario bit); player row excluded; when
counter EXACTLY equals cad -> EVENT 0x18 (24) queued on game obj 0x7a35c
(0x55a60, queue depth 32, stride-10 records at +0x475e).
TABLE words (live == restored FILE 0x89330; ZERO stores image-wide):
cad[5]=60 6=100 7=62 8=77 9=90 10=150 11=70 12=63 13=66 14=72 16=92
17=100 19=89 20=68; ZERO at 0,1,2,3,4,15,18,21 -> CHARGED SET {5..14,16,
17,19,20} == rewrite chargedIdx EXACTLY (species.cpp:30) — the 14 charged
SA_ abilities. *** OQ-020 CLOSER: charge period = cad[ability] days from
this table (Baliflids 100, Nimbuloids 68 ...); rewrite default 30 is WRONG
per-ability. Delta task = t100 — LANDED t100: kCad[21] in
rewrite/src/game/species.cpp + abilityPhase count-up law, verified three-leg
(scripts/r1_t100_cad_verify.py RC=0). ***
UI leg 0x37b6c dx==1: countdown = cad - counter shown with static.txt
strings [0x1c]=''/[0x1d]='s' plural law; dx==2 opens 'abres%02d' window.
*** t103 CORRECTION [verified]: dx 1|2 = probe + countdown (that part
stood); 'abres%02d' belongs to the dx==50 FIRE leg (result text), NOT
dx==2 — full adjudication S8 below. ***
NOTE +0x88 LABEL: S2d banks +0x88=gizmo POWER sum; profile 7 doubles it,
profile 9 zeroes it (help.txt POWER texts) — t85g's '+0x88=MOVES' label is
WRONG at these sites (MOVES candidate = +0x94, panel fmt order POWER,
MOVES, INTEGRITY = +0x88,+0x94,+0x8c); re-attribution pass named, t85g
raw observations stand.
*** t101 ADJUDICATED [verified]: CONFIRMED as proposed. The panel display
arm 0x1da8a..0x1daaf pushes [eax+0x8c],[eax+0x94],[eax+0x88] R-to-L into
'POWER %d MOVES %d INTEGRITY %d' (F 0x831c9 re-dumped byte-exact; the
only 'MOVES' string image-wide). +0x88=POWER, +0x94=MOVES (re-granted
per turn = drive stat [ship+0x10], FUN_0004a658; travel fsub/fistp
0x4a30f..0x4a314), +0x8c=INTEGRITY, +0x98=MAX, +0x18=POWER capacity,
+0x52=birth day. The 16 ability bodies hit POWER only — NO moves-targeting
ability exists. Verify tool scripts/r1_t101_field_verify.py RC=0 (panel
bytes + jump table + live laws). ***
OPEN RESIDUALS (strict-close keeps OQ-016 open): event-24 CONSUMER
module (P0 random-event family); GOVOROM +0x42-vs-pop relation uncited
(vendor-text only); the 0x37b6c dx-switch full adjudication; stride-45
table 0x74782 identity beyond cost-word.
*** t102 CLOSED the first residual (S7 below): the consumer IS
FUN_00055ae8 (EVENTWIN pump, sole caller 0x54b74) and type 24 has NO
effect arm — queue = UI refresh; SA_ effects are synchronous-only per the
SPLIT LAW S7.2. Remaining residuals stand. ***
*** t105 CLOSED the LAST two residuals [verified, tools
scripts/r1_t105_verify.py RC=0 five legs + r1_t86_write_census 0x42]:
(1) GOVOROM +0x42 IS pop — SA_Cornucopia body (0x43de4..0x43e96, pinned)
min-walks WORD[planet_rec+0x42] over the static pool 0x2b057 stride 123
(owner BYTE [rec+0x57], skip [rec+0x16]==10); that exact word is the
population counter per the t24 CLOSED pop law (income-law.md §6e:
colonize :=2 / growth +1 / clamp cap +0x4a; growth-pass decompile
38f68.c:154-177 reads +0x42/+0x4a/+0x4e on the same layout) — a STORED
counter, not a derived cache, and not a race-row field (race-row +0x42 is
pointer garbage; "GOVOROM" names the ability NUMBER 10, no GOVOROM race
row exists in the shipped campaign). (2) the "stride-45 table 0x74782"
never existed — see the S6.3 correction above (index math = 75*t, word =
restree runtime cost). The F12 sub-note "planet-choice key +0x42 semantic
UNMAPPED" is likewise resolved by (1). S6.4 OPEN-RESIDUALS list: ALL FOUR
ITEMS NOW CLOSED; OQ-016 itself stays open on its own listed grounds. ***


## 7. (t102) EVENT-24 CONSUMER DECODE CLOSED: THE QUEUE IS A UI SIGNAL;
## SA_ EFFECTS ARE SYNCHRONOUS ONLY. Verify tool
## scripts/r1_t102_event24_verify.py RC=0 (5 legs). Working notes
## docs/re/_wip_t102.md F1-F8.

### 7.1 The pump and its type switch [verified 0x55ae8..0x55db1 raw]
FUN_00055ae8 (sole rel32 caller 0x54b74 inside FUN_00054650, the
EVENTWIN/message pump; gated [[obj+0x4226]>>16]==1 and ds:0x7a358!=-1)
pops the stride-10 ring on the game object 0x7a35c (write cursor = hi
word dword[+0x4758], read cursor = hi word dword[+0x475a], wrap-zero both
at 0x55d8a..0x55d9a) and dispatches on record TYPE:
  0 -> edi=0x14 | 1,2,15 -> edi=0x11, ds:0x43508:=queued obj |
  3..9,20 -> ship-availability write family (assert dl==4; row=ctx*166
  onto 0x12e16; call 0x45d4c; [0x12fff+off]:=1/0, [0x13000+off]:=[obj+0x59])
  | 16,17 -> edi=0x11, ds:0x43508:=ctx | 18,19 -> [obj+0x24d9c]:=-1
  (ctx==7 sub-arm DEAD: t[esp+8] is 0 from 0x55b74 and never rewritten) |
  23 -> ds:0x6775:=ctx byte | 10..14, 21, 22, 24, 25, >=26 -> NOTHING
  (ring maintenance only; edi stays 0 from 0x55b99 -> tail 0x55da1 je
  0x55db1 SKIPS the 0x56ad4 re-arm).
*** TYPE 24 HAS NO EFFECT ARM (0x55d02/0x55d05/0x55d10 -> 0x55d69 null).
The queued event 0x18 advances the ring and nothing else. ***

### 7.2 The SPLIT LAW (producer gate == sync-dispatch gate) [verified]
FUN_00043b50(edx=1) rel32 callers EXACTLY {0x37baf (edx=0 probe),
0x37cb1 (UI path, FUN_00037b6c dx==1), 0x3eb3c}. The 0x3eb3c gate
(0x3eb22..0x3eb33): race byte != ds:0x7458e -> CALL bodies; race ==
0x7458e -> call ONLY if ds:0x10ba4 == -1. The event-24 producer (t101 F4,
0x3e7d5..0x3e815) pushes ONLY for race == 0x7458e rows (counter==cad
exact). Both are the same equality on the same rows: AI races execute
SA_ bodies SYNCHRONOUSLY in the per-race turn tail FUN_0003e6e0 (caller
of FUN_0003ea54 at 0x3e7bb); the local race's due-ability event 24 goes
to the ring as an EVENTWIN refresh and the local ability fires through
the UI command path 0x37b6c dx==1 -> 0x37cb1 call. Live 60.sav:
ds:0x10ba4==0, ds:0x7458e==0==race0 byte, queue hi word 0 (drained).
*** CONSEQUENCE FOR THE REWRITE: no deferred-execution queue needed.
abilityPhase counter == cad => fire immediately for AI races; for the
player race, fire on the UI activate action (same body, same reset law
T1 0x4400a). The cadence gate INSIDE 0x43b50 (cad > counter -> 0x44017,
t101) is the single authority. ***

### 7.3 ds:0x7458e / ds:0x10ba4 identity [verified stores + live]
0x7458e has EXACTLY two store sites image-wide (opcode census on
8e 45 07): 0x21aa0 (idx->0x7458e, 1<<idx->0x89324 bitmask; 0xff sentinel
-> 0/0xff) and 0x52cc6 (reset both-ish to 0; also 0x12e17). Live: 0 =
race0 byte; race rows row+0x7 -> AI-controller blocks with [+0x14]&0x80
set for races 0-2 (t102 probe, pointer law H=136; member = P - 0x242000).
[inferred] 0x7458e = local player's race index; 0x10ba4 = netplay flag
(-1 = all races local; 0 = singleplayer/HOTSEAT-off).

### 7.4 F8b drain sites adjudicated (t101 residue) [verified static,
correlated live]: jump table FILE 0x41244 7/7 [0x419cf,0x41cc6,0x41bb3,
0x41ded x3, 0x41c56]; order-state dispatch 0x41e1e on BYTE [ship+0x5d].
The completion leg 0x41ded..0x41e19 ZEROS [ship+0x94] and [ship+0x88]
folding the delta into stack budget [esp+0x3a0]; arrival leg 0x41d80
decl [ship+0x88]. FUN_0003e6e0 leg (c) recharges every ship via
FUN_0004a74c, so zero POWER at save time means a post-recharge drain:
*** t104 ADJUDICATION — CAPTURE-OBSERVED, AND THE FIVE-ROWS HYPOTHESIS
REFUTED (tools scripts/r1_t104_drain_verify.py RC=0 + r1_t104c_fulllaw.py,
stream pass over playcap/live-timeline.jsonl 44,928 rows):
OBSERVED (the closure class t102 named): completion drain EXECUTING on
CONTINUOUS tracked records (same owner+design+state both sides): 4 events
day369 slot3, day678 slot14, day945 slot10, day1017 slot28 (repeats on
slot3 at 370/372); EVERY one POWER(word +0x88) > 0 -> 0 WITH order-state
+0x5d CLEARED 0x3 -> 0 in the same sample pair; MOVES net-unchanged
(zero leg + FUN_0004a658 re-grant between autosaves); POWER returns at
the NEXT boundary (678->679 P4, 945->946 P5, 1017->1018 P8) == the
FUN_0004a74c pass one End-Turn later. CONTROL: b5d-UNCHANGED same-day
P->0 burns = 126 members (travel/upkeep 0x4a2d4..0x4a314) — the b5d-clear
gate genuinely separates completion from burns.
[t107 ADDITION (census-audit): a THIRD burn path exists in the CONTROL
class — 0x41d80 `dec DWORD [ship+0x88]` in command-exec fn 2010 (block
0x41d60..0x41daf: [+0x67]:=ptr 0x12e10, DEC POWER, BYTE +0x5d:=0), a
per-order one-POWER spend invisible to every banked census (FF /1 DEC is
outside the mov/sub/add op set r1_t86/r1_t106 generate). Law unchanged
(recharge/re-grant laws intact); the burn-class enumeration was
incomplete, not wrong. Aggregate rewrite has no per-ship POWER -> no delta.]
REFUTED (the t102 mechanism for the static five zero-POWER rows): the
rows on 59.sav+60.sav (both T=1254, slots 2/4/11/12/15, own2, b5d==0,
+0x52 1257..1264 > T) are POST-DEATH FREE-RECORD REUSE, not mid-transit
completion drains: ALL FIVE slots went state->0 mid-t1253 (the t85g war
turn; r1_t85g2_slots.py had independently named them "Ungooma slots that
died"; slot4 reappears t1254 with design 2->4, xyz frozen, ETA re-stamped
1264). P=0 on a reused record simply awaits its race's NEXT recharge
(owner-2 boundary refills 4 counted); ETA-ahead = the 0x40e96 order stamp
on new orders (§7.5 stands). The "five rows = post-recharge completion
drains" reading is VOID; no recharge-law exception exists.
RESIDUAL kept honest: autosave granularity cannot order drain-vs-recharge
WITHIN one turn tick; observed events carry b5d-before == 0x3 (state
domain only partially mapped, t96). ***
NOTE leg (a) EVENT 11 pushes per item for local-race ships when
FUN_000402d8(race) < 0; leg (b) EVENT 10 race-death (row+0x3 := -1).
Both feed the SAME null-for-UI ring: types 10/11 also have no effect arm
(10..14 -> NOTHING), i.e. ALL of 0x3e6e0's queue traffic is UI refresh.

### 7.5 [+0x52] ETA OVERWRITE (context for F8b) [verified bytes, target
object identity open]: FUN_00040de0 leg 0x40e96..0x40ea6 sets
[obj+0x52] := ds:0x12e10 + (idiv quotient 0x40e91, dividend from call
0x4a41c(obj), divisor WORD [obj_arg+0x44]) + 1, plus BYTE [obj+0x58] := 1
and [obj+0x59] := ptr; FUN_00040eb4 then SUBTRACTS two +0x52 fields
(earliest-arrival compare). The birth-day field is therefore REUSED as a
transit ETA stamp — this is the provenance of [rec+0x52] > T on the t1254
reused-record rows (t104: all five slots 2/4/11/12/15 carry 1257..1264 vs
T=1254), independent of the recharge law. t104 OBSERVED the drain
executing on the user's playcap stream (§7.4 adjudication: completion =
POWER->0 with +0x5d cleared, next-boundary recharge restores) — the F8b
path is upgrade-complete from attributed to observed; the ledger residue
that remains is only the within-tick ordering granularity note.

## 8. (t103) HUMAN ABILITY ACTIVATION CLOSED: THE 0x37b6c DX-SWITCH.
## Verify tool scripts/r1_t103_dxswitch_verify.py RC=0 (5 legs). Working
## notes docs/re/_wip_t103.md P1-P14.

### 8.1 Identity: ability-window class record [verified bytes]
Zero rel32 callers image-wide; the ONLY u32 == 0x37b6c is FILE 0x8893c =
pool 0x5d84 (+0x8 slot). Class record (file 0x88934, stored by ctor
FUN_00037ac0 `mov [eax+0xa7],0x5d84` at 0x37ac5):
  +0 create FUN_00037ad0 (cl,4 -> load template 0x888f8 via 0x76cac;
     cl,2 -> 0x76cd4 loads DESCRIPTION resource 'abil%02d' file 0x8483f +
     'help.txt' 0x84848 — the window opens showing the ability description)
  +4 shared 0x30d08   +8 HANDLER FUN_00037b6c (extent 0x37b6c..0x37cf7)
  +c PAINT FUN_00037cf8: shp lib 0x9f10c sel 250 base + race ability glyph
     BYTE [race*2+0x12e18] (race row +0x2) via FUN_0001fc34/FUN_0005caac.
Dispatch: pump FUN_00056b5c (0x56c6b mov ebp,[eax+0xa7]; 0x56c74 call
[ebp+0x8]) for the TOP window (WORD [game+0x4226]>>16 into stride-0x8e table
at +0x3068); relay FUN_00056ca4 (0x56cd1/0x56cd7/0x56cda) targets a slot from
[[game+0x4]]. REGISTER LAW (relay): caller ebx = MESSAGE CODE (arrives as dx
via movsx), caller ecx arrives as handler ebx, caller edx = slot idx >>16.

### 8.2 The switch [verified bytes, leg 1]
Head: esi = 0x12e16 + ds:0x7458e * 0x1ee (LOCAL race row — the SAME
equality that gates t102 S7.2; ability [row+0x19a]>>24 == [row+0x19d]).
  dx 0 / other -> FUN_00033ff8 (base-class msg filter: passes 0-5,6/7,7,
    0xc9/0xca arms, default forwards 0x336b4).
  dx 1|2 -> PROBE: call 0x43b50(eax=row, edx=0). eax==-1 (READY) ->
    BYTE [ui+0xccb] := 2 -> tail. NOT-due -> countdown text:
    cad-counter (u16), singular iff ==1 (0x37bfb cmp edx,1) picks
    static.txt [0x1c]='' vs [0x1d]='s', formatted 0x76c79 into [ui+0xcd0],
    plus [0x1e]='OK' copied to [[ui+0x67]+4]+0x20. The child relay at
    0x37bdb is FUN_00056ca4 msg 2 (ecx=0).
  dx 50 -> gate cmp ebx,1 (0x37c9c): ebx==1 -> FIRE call 0x43b50(row, 1),
    then snprintf 'abres%02d' (pool 0x1ca1 = file 0x84851, byte-pinned)
    with the ABILITY ID, and FUN_00033f40 opens (help.txt, abres<NN>) —
    the result-text window; ebx!=1 -> base-class filter.
  Tail 0x37c78: [ui+0x35]:=[0x39]:=-1; call [class+0xc] (repaint).
CORRECTION: the S6.4-era expectation 'dx==2 opens abres%02d' is REFUTED —
abres is the dx-50 result resource; dx 1|2 is probe+countdown.
[ui+0xccb] marker: disp32 census EXACTLY one hit (the store 0x37bbb), zero
readers — dead marker (UI re-probes instead; honest negative under the
disp32 law).

### 8.3 FUN_00043b50 edx parameter law [verified bytes, leg 2]
cad = WORD[0x6780+2*ability]; gate `cad > counter` -> return 0 (charging).
Ready: sentinel := -1; `cmp edx,1 / je 0x441c1`:
  edx==0 (UI probe, 0x37baf): return eax=-1 = READY signal only.
  edx==1 (commit; UI fire 0x37cb1 AND AI sync 0x3eb3c): body dispatch
    al = BYTE[row+0x19d] - 5; >0xf -> no body; else cs:[eax*4+0x2ef60]
    (FILE 0x43b10, the 16 bodies of S6.3).
  RESET tail 0x43fe5..0x44011: row+0x19e := counter - cad (sub edx,eax at
  0x44001 — DIRECTION corrected vs t99 prose; == 0 exactly at the fire
  moment, so t100's reset-0 model stands; over-fire carries the residue).

### 8.4 Dispatch arrival [static exhausted; honest negative on positive arm]
All (pump 9 + relay 56) dispatch sites register-traced. The input relay
0x54976 pumps msg=WORD ds:0x484c4 / ebx=WORD ds:0x484c6 verbatim from the
DOSBox event record (record+0xc/+0x10, readers 0x2a875/0x2a8fe; INT 16h
scan/char pairing corroborates at 0x2a5f0/0x2a6d0). Msg-50 relays exist
(0x3b6ac, 0x3d83f..0x3daf9 family, ship-context gates) but none arms ecx==1.
Which user action POSITIVELY delivers (50,1) to this window needs a live UI
trace — carried as residual (same closure class as F8b observation); the
handler-internal law (dx==50 && ebx==1 -> fire) is cited either way.
