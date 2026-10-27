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
