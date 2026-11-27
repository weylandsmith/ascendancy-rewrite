# tNAME-1 (D33-L3) WIP — per-game star-name variation: where the vendor seeds the worldgen RNG

## S1 TRAP RE-HIT (banking it so nobody does it a third time)
`~/tools/revenv/bin/python scripts/t442_disasm.py START $(python3 -c ...)` /
`$((0x238e8+0x260))` — bash expands to DECIMAL, the script parses argv as HEX,
so the END silently becomes a huge address and the run floods 3.4 MB. The
STATE.md trap said EXPLICIT hex END. One more rule: always pipe disasm through
`grep`/`head` even for small ranges.

## S2 srand CENSUS [verified, scripts/tPF6b_callscan.py 0x78273]
FUN_00078273 (srand: call 0x78249 -> store seed at rng-state) has exactly FIVE
rel32 call sites in obj0 code: 0x213fc, 0x21490, 0x35800, 0x54f0d, 0x59aa9.
- 0x54f0d / 0x59aa9: save/restore path (guard `cmp dword [obj+0x48aa],0` +
  DAT_00010ba0==-1) — srand from SAVED state (already known t422).
- 0x35800: srand(0) in an audio/init prologue (xor eax,eax immediately before).
- 0x213fc and 0x21490 are BOTH inside FUN_00020fd4 (0x20fd4..0x230d8, the
  new/load-campaign entry — its ONLY call site is 0x7b817).

## S3 FUN_00020fd4 fresh-game seed law [verified disasm 0x213c0..0x214bf]
```
0x213d6 call 0x309d4 (eax=0x484f8)     ; init
0x213db call 0x78192; test; je 0x213f5 ; branch on some capability
0x213f5 xor eax, eax
0x213f7 call 0x7821c                   ; CLOCK getter (0x7b5c0/0x7b683 below)
0x213fc call 0x78273                   ; srand(clock)  <-- FRESH-RUN SEED
0x21401..0x21412: mov edx,0x8353b call 0x21a84; mov eax,0x98d call 0x77ece
        -> edi = result (0 => branch A)
BRANCH A (0x2141d, default no-record path):
  mov ebx,7 / edx,0x32 / eax,0x12e10 / ecx,0 / call 0x226e4   ; regen
  call 0x238e8                                                 ; worldgen
BRANCH B (0x21442, record path):
  8x push stack-buffers + push 0x998 + push eax; call 0x77fe1  ; record read
  0x21480 mov ebx,[esp+0x550]          ; record field 0 = SEED
  0x21489 cmp ebx,-1 / je 0x21495      ; -1 => KEEP the clock seed
  0x2148e mov eax,ebx / 0x21490 call 0x78273   ; srand(record seed)
  0x21495..: ebx=[esp+0x546] sar 0x10, edx=[esp+0x542] sar 0x10,
             eax=0x12e10 ecx=0 call 0x226e4; call 0x238e8
```
=> VENDOR LAW: a fresh program run seeds the SINGLE Borland LCG (0x7824f) from
the system CLOCK; only a scenario/record seed != -1 overrides it. Worldgen
0x238e8 draws its per-star/per-planet parameters from that stream (0x23da4
rng%5+1 planets-per-star; 0x23a86 rng%5 size; 0x23a97 rng%11 weight row;
scenario override 0x23aaa..0x23ac2) — so EVERY fresh game differs, and the
same scenario seed reproduces. This is the per-game variation D33-L3 asks
about; the NAME pool law itself is already CLOSED (OQ-004 + mapgen.md S2).
0x7821c internals: 0x7b5c0 -> value; if >= 0x1f4 inc [esp]; 0x7b683 -> returns
eax (clock-shaped accumulator); exact tick semantics NOT claimed.

## S4 PORT DEFECT [verified code]
rewrite/src/main.cpp:50 `unsigned seed = 1;` — the ONLY seed source;
main.cpp:283/287 cfg.seed = mc.seed = o.seed. The Begin handoff
(NewGameSettings menulaw.h:355) carries stars/owners/gov/species but NO seed,
so buildCampaign(o,&err,&newGame) always rebuilds with seed 1 => identical
star names ("always Phoebe") every Begin press, every game. The title wheel
galaxy uses wheelBaseSeed+gen (title.cpp:221-234) which is likewise anchored
to the built campaign's seed 1.

## S5 PORT FIX SHAPE (in progress)
Vendor-analog: a fresh interactive game draws a per-run seed from the clock;
an explicit seed stays authority (CLI --seed == the record-seed override leg;
gate matrix passes --seed explicitly and is untouched). Begin handoff gains a
seed term; main.cpp prefers apply->seed exactly like tSPEC-1 prefers
apply->species. Determinism contract preserved: same seed -> identical galaxy
(existing pin), and headless no-UI default must NOT become time-derived (gate
3l byte-identity + the headless matrix run WITHOUT --seed — CHECK FIRST which
headless paths rely on seed==1 default).

## S6 CORPUS MEASUREMENT [verified, scripts/tname1_homename_census.py + ad-hoc twin probe]
25 fresh vendor lineages (r1ad-/r1deep- capture dirs, earliest save each,
turn<=38, owner-0 owned planets via pointer law): owner-0 home star BASES are
25 DISTINCT strings — Sophia, Byzantium, Masticon, Flammifer, Pendulon,
Chippendale, Pindentry, Hope, Rhovid, Phoebe, Hurble, Wattsenfax, Sirverei,
Philadelphia, Vishnu, Smorgasbord, Millitrin, Sentril, Gravitus, Xerxes(x5,
template-galaxy dirs)... The STATE.md NEXT note's "tpld1_spechome shows home
names varying" referred exactly to this corpus: tpld1 L1 shows home CELLS are
CONSTANT per spec across all lineages (73/45/23), while the BASE NAME varies
per game. => USER CLAIM D33-L3 CONFIRMED AGAINST THE VENDOR: type per species
(table law, tPL-D1 CLOSED), name per game (fresh RNG). Phoebe appearing in
one lineage is one draw out of 100 bases, not a law.

## S7 VENDOR NAME LAW (full shape) [verified disasm + closed priors]
Names come from the names.txt pool (OQ-004 loading, mapgen.md S2: 100 unique
bases, Roman numerals only on planets). The per-game variation lives ENTIRELY
in the worldgen RNG stream: FUN_00020fd4 (the game's main(); only caller
0x7b817) does srand(FUN_0007821c()) at 0x213fc on the fresh path, where
0x7821c wraps 0x7b5c0/0x7b683 (clock-shaped accumulator; tick semantics not
claimed); the record/scenario leg (0x21442..0x21490) overrides with a stored
seed when != -1. Worldgen 0x238e8 then draws per-star rng%5+1 planet counts
(0x23da4) and per-planet rng%5 / rng%11 params (0x23a86/0x23a97) from that
ONE Borland LCG. Star slot k's name comes from the loaded star table order
(NAME-0x1C record law, income-law.md), so a clock seed re-draws the whole
name/position/type layout each fresh game. THERE IS NO SEPARATE NAME RNG —
"vary the seed" IS the vendor name law.

## S8 SHIPPED + VERIFIED (this iteration)
PORT: menulaw.h NewGameSettings.seed (default 1); title.cpp Begin feeds
wheelBaseSeed+1 (chains across eject re-entries via wheelBaseSeed re-read of
the LIVE campaign seed) + 'seed %u' in the apply line; main.cpp
buildCampaign prefers apply->seed on the Begin leg; interactive UI boot with
no --seed draws a clock seed ('main: fresh-run seed %u'), --seed is
authority everywhere (vendor cmp -1 leg), headless default stays 1.
PINS test_name_seed_tname1.cpp x4 (identity; title feeds wheelBaseSeed expr;
main prefers apply + guard present + default 1; behavior: same seed same
name, neighbour seeds vary, Chamachies 45/row7 for EVERY seed).
MUTATIONS tNAME1_mutate.sh M1-M4 ALL CAUGHT (each with the right pin line),
restore md5-ok x4. TRAP: a foreground tool-timeout mid-round left the M4
mutant on disk — restore from /tmp backups and cmp-verify before rerunning;
the tSPEC-1 script's exit-trap line has an unescaped `$?` inside single
quotes + em-dash (bash trap parse error at exit only — cosmetic, fixed in
the tNAME1 copy).
WITNESS tNAME1_name_witness.sh rc=0: A seed 9309524 home Mira 73/5; B seed
3531809547 home Xerxes 73/5 (DIFFERENT names, same TYPE); C/C2 --seed 7 ->
handoff seed 8, BOTH home Zoroaster 73/5 (reproduces). Suite 621->625/0/0;
gate 0; ledger OK (open=[016,019]).
RESIDUES (documented): (1) the clock getter's tick semantics (0x7821c ->
0x7b5c0/0x7b683) are not claimed — the port uses a chrono hash, the LAW is
'time-varies + explicit-seed-authority', not 'same value as the vendor
clock'; (2) the vendor's between-game stream advance is modelled as +1 per
Begin (wheelBaseSeed chain) — the vendor LCG advances by many draws, but
only 'never the same seed twice in a run' is observable; (3) the port's
name->slot assignment (shuffle order) differs from the vendor's table order
— both are seed-permutations of the same pool (mapgen.md S2 pool law holds;
slot-level name identity was never a closed law).
