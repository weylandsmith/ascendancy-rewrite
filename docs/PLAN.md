# Ascendancy Closeout Plan (v2 loop)

v1 plan: archive/ralph-v1/PLAN.md. Its phase list P0..P6 is COMPLETE (gate
green, binary plays seeded campaigns to victory, docs/re/ specs cited). This
file plans only what remains: converting documented defaults into lifted
constants. Do not re-plan completed phases.

Erratum carried from the v1 file (v1 text was falsified, keep this version in
mind when reading old phases): the .tsv files are NOT text renderings of the
.bin tables (FINDINGS 1b); they are per-context string pools with a numeric
area; grammar open = OQ-004.

--------------------------------------------------------------------------
EVIDENCE RULES (unchanged from v1 — the value of this repo is trust)
--------------------------------------------------------------------------
1. Every constant/formula copied into rewrite/ cites a docs/ file which cites
   a Ghidra address, an extracted-file offset, or a pointer-law-derived
   guest-physical address from a named capture.
2. Conflicting sources: record BOTH in OPEN-QUESTIONS, pick by evidence.
3. Never invent formats. Unknown = unknown.
4. game/ stays byte-identical (gate-enforced).
5. NEW for v2: check docs/REFUTED-ROUTES.md before any research action.

--------------------------------------------------------------------------
WORKSTREAMS (run strictly one action at a time; pick the STATE.md NEXT ACTION)
--------------------------------------------------------------------------
W1  PLANET FIELDS -> COMBAT (OQ-010, OQ-003)   [IN PROGRESS - see STATE.md]
    click-diff capture -> field map -> Ghidra xrefs on writers/readers ->
    lift damage application (hit prob, shield subtract-vs-absorb, overkill,
    firing order) from batmode/cosmos-attributed ranges. Upgrade
    Campaign::attackScore/defenseScore with citations; unit-test the lifted
    arithmetic against a captured real battle outcome if one can be staged.

W2  CAMPAIGN CONSTANTS (OQ-016, OQ-012, OQ-013, OQ-014, OQ-021, OQ-020)
    With planet fields known, the same live-RAM method settles: income/
    growth tables (diff stockpiles/population across turns with controlled
    planet states), new-game size options (read 3cfgnew.tmp-driven UI state
    in RAM at the new-game screen), variant-tree visibility (which research
    rows are live in a fresh campaign's RAM), end-ctrl threshold (find the
    constant in code: scan for comparisons against counts near the victory
    check; attribution gsystem/cosmos), ability charge constant (vendor %d —
    find the argument site).

W3  FILE-FACING CODECS (OQ-005, OQ-006, OQ-018, OQ-004, OQ-019)
    Via exe code located through attribution + call graph from proven entry
    points: shape loader (dims + RLE grammar — the ONLY sanctioned route;
    blind static sweeps are forbidden), audio init (rate of headerless
    files, theme selection), open-file thunk (which tables load; .tsv
    grammar), ship design screen structures.

W4  DIPLOMACY ORDERING (OQ-015)
    DA_ selection loop + full %token table via code (race module
    attributed, 20 E1 sites).

W5  HYGIENE (continuous)
    gate green every commit; STATE.md ledger + OPEN-QUESTIONS updated in the
    same commit; new refuted routes recorded immediately; capture artifacts
    stay in work/ (gitignored); docs/re/ specs are the long-term record.

W6  AI BEHAVIOR DECODE (t85g standing worklist — closes the rewrite's
    placeholder behaviors; findings bank to docs/re/aicode.md as laws, and
    UPGRADE the matching rewrite phase functions with citations)
    Motivation (user request 2026-10-23): rewrite placeholders like
    researchPhase uniform-random AI tech pick, expansionPhase nearest-
    unowned BFS, and the aggregate combatPhase are KNOWN-simpler than the
    original; the original's decision code is statically present and
    mostly unread. Queued actions (one per loop turn, cheapest first):
    A1 ship [reg+0x90] writer/init census (shield layer identity;
       combat.md S2c-1; feeds OQ-010).
    A2 finish combat loop 0x4d075..0x4d20e + death handler 0x49d2c + hit
       path 0x4b740 remainder (firing order, overkill, [edi+0x4a] build
       site = the combat-object snapshot; combat.md S2c-2).
    A3 AI turn loop map: entry via race.cpp-attributed ranges around the
       proven attitude scorer 0x3ecb8 + build selector caller 0x3ead6
       (income-law S9) -> phase order + which functions decide research,
       expansion, fleet build, ship orders (feeds aicode.md + OQ-016).
    A4 AI RESEARCH selection: within A3, the function choosing the next
       tech per race (rewrite placeholder = uniform random; original
       law = target measurement). Cross-check flash.pop gates at
       0x417aa/0x4193c (race.cpp) which restructure these loops.
    A5 ship ORDER dispatch: order-name block 0x88e60 (SOGoStar..SOGoSpace;
       only proven code ref = SONothing pool-imm at 0x1dae6, next to the
       hover gate 0x1d9fe — the order-string display path; a SOPatrol
       pool-imm at 0x27d is LE-header noise, NOT a ref). Decode 0x1dae6's
       enclosing function + find the numeric order-enum (display strings
       may index a separate enum) -> how AI assigns SOAttack/
       SODefendPlanet/SOColonize (the "system defense / offensive thrust"
       question; feeds aicode.md).
    A6 SHIP_PATIENCE (+0x1b0) readers (named key, unbound semantics).
    A7 state-byte stores of imm3 into [+0x1c0+idx] (OQ-023 static route).
    LAWFUL SOURCE: mid-turn capture frames t1244..1254 (banked) + static
    decode; NO new user sessions required for any item in this list.


--------------------------------------------------------------------------
VERIFICATION
--------------------------------------------------------------------------
bash scripts/gate.sh (exit 0 = healthy; includes build, 83 tests, boot
smokes, victory smoke, probes, R1-harness static invariants).
Launch: bash scripts/launch_ralph.sh (tmux session 'ascend', goal + gate
registered, bounded R1 capture at session start).
Definition of done for the whole loop: STATE.md ledger.open is empty, each
closure carrying evidence per STATE.md DEFINITION-OF-DONE.

--------------------------------------------------------------------------
LOOP OPERATING PROCEDURE (v2)
--------------------------------------------------------------------------
Every turn:
 1. Read docs/STATE.md (ledger, in-hand tools, NEXT ACTION).
 2. Read the relevant docs/REFUTED-ROUTES.md section for the intended action.
 3. Execute EXACTLY the NEXT ACTION. Bounded >30-min work checkpoints into
    docs/ before ending.
 4. Update STATE.md (turn note, ledger, exact next action) and
    OPEN-QUESTIONS.md in the same commit.
 5. git add -A && git commit -m "W<n>: <action>".
 6. bash scripts/gate.sh; fix before ending the turn.
Never: modify game/; invent data; close an OQ without measurement; re-run a
refuted route; run an R1 capture outside the safety-invariant scripts.
