# t328 WIP — OQ-005 DRAW-WITNESS FEASIBILITY (offline-first)

Assigned: docs/STATE.md NEXT ACTION t328 (queue row 1). Closes NOTHING
(strict-close). Deliverable: per-record feasibility table for the 80-record
OQ-005 residue + updated DECISIONS.md D1 text so the human ask shrinks to
what is actually adjudicable.

## S0 INPUTS (located this session)
- Sitting check NEGATIVE: playcap newest turn 1086 (tail-seek
  '"turn": N' over 3 MB tail); production :9 dosbox-x pids 136357/136359 +
  watcher 136372/136374 alive since Nov06 — UNTOUCHED this session (offline
  task, zero launches).
- Decision sheet: work/r1/shp_png/decision-sheet.md (88 rows A1..A15,
  B1..B29, C1..C44; hand-safe twin of index.txt). Raw dumper census banked:
  work/r1/shp_png/index_t278pristine.txt.
- C-row record list (grep of decision-sheet): C1 3cfgnew--12; C2..C13
  cos_star--40..51; C14 1starmap--1; C15 destroy--14; C16 expl00--9;
  C17/C18 expl01--8/--9; C19/C20 expl03--0/--9; C21/C22 expl04--0/--9;
  C23 expl05--9; C24 expl07--0; C25/C26 expl08--0/--9; C27/C28/C29
  mouse--5/--6/--7; C30/C31 orbex00--8/--9; C32..C44 sg{37,45,47,49,50,64,
  66,70}expl--0/--9 (sg50 only --9, sg64 only --0, sg70 only --9).
  25 zero-byte ladder slots = C15..C26 + C30,C31 + C32..C39 + C42..C44
  (=12+2+8+3=25, exact match to the t278 S24.2 decomposition).
- shp.md sections: S9 grammar FUN_0005caac; S12/S14 blit law; S16 unified
  stream law; S17 runtime table uniform (4 libs x 43 selectors live-RAM,
  scripts/r1_shp_ramtable.py); S20.3 16-record dims-unknown remainder;
  S21 span-bound removal; S23 pop-slot lib; S24 decision sheet. S25 = MINE.
- Carried law (task text): dims-zero blit = error -1 @0x5cb2b => a record
  with zero dims CANNOT be drawn by the vendor => no witness is possible.
- t323 amendment: combat explosions = UNREACHABLE-BY-CAPTURE (cite, no probe).
- TOOL NOTE: any future capture/debugger work = scripts/r1_dbg_session.py via
  ~/.hermes/hermes-agent/venv/bin/python (system python3 has NO PIL).

## S1 MEASURED CLASSIFICATION [verified this session, work/r1/shp_png/_t328_dims.json]
File-space dims + span for all 44 C-rows (parsed from extracted/ascend0*/data/*.shp
with the S1 container law: magic 1.10, tsz=8*(count+1), u64 directory):

  GROUP A cos_star k40..k51 (12): span 27 (3 stream bytes past the 24-byte
    header); dims words ZERO at BOTH candidate slots (rec+0 u16-pair = 0,0;
    rec+0x10 u32-pair = 0,0). => blit -1 gate fires (see S1b). CITED-NO-WITNESS.
  GROUP B 25 zero-STREAM ladder slots: destroy k14, expl00 k9, expl01 k8/9,
    expl03 k0/9, expl04 k0/9, expl05 k9, expl07 k0, expl08 k0/9, orbex00 k8/9,
    sg37/45/47/49expl k0+9, sg66expl k0/9, sg70expl k9 (count = 25; matches
    t278 S24.2 decomposition). span 8 (k0-variant libs) or 24 (k>=1) = ZERO
    stream bytes at the canonical slot. NOT dims-zero: the k>=1 records carry
    plausible u16 dims at rec+0 (139,139 / 199,199) and the variant word
    0x7FFFFFBB at rec+0x10; the k0-variant headers (S3 class bb ff ff 7f)
    carry 0x7FFFFFBB at rec+0 then u16s 139,139,70,70. The task text's
    "dims-zero blit = error -1" premise applies ONLY to group A — for group B
    the structural fact is zero-STREAM, not zero-dims. [correction banked]
  GROUP C sg50expl k9 (span 27, EOF): near-empty + truncated; t323 amendment
    names it combat-explosion UNREACHABLE-BY-CAPTURE.
  GROUP D sg64expl k0 (span 1162): the '12 00 00 00 fb ff ff ff' header variant
    (S3); t323 amendment names it UNREACHABLE-BY-CAPTURE.
  GROUP E mouse k5/k6/k7 (span 2062 each, REAL art bytes; dims u16 at rec+0 =
    46x77 all three). Selection probe = S2.
  GROUP F 1starmap k1 (span 24 = zero stream bytes; u16 dims at rec+0 30x50;
    variant word 0x7FFFFFBB at rec+0x10). windows.txt SHAPEITEM selects
    1starmap k3,k4,k5,k7 — NOT k1 (cited lines 456/477/498/517).
  GROUP G 3cfgnew k12 (span 2391 AT FILE EOF, u32 dims at rec+0x10 = 84x79,
    walk short 55/79 rows at EOF per S20): broken vendor data outright.

## S1b BLIT -1 GATE, re-verified from raw asm THIS SESSION (objdump -D -b
binary -mi386 -M addr32,intel --start-address 0x5caac --stop-address 0x5cb60
work/ascend_restored.bin): FUN_0005caac prologue loads esi=[ebp+8],
ebx=[esi]; 0x5cabe eax=[ebx+4]; inc eax; 0x5cac5 jle 0x5cb2b; 0x5cac7
eax=[ebx+8]; inc eax; 0x5cacd jle 0x5cb2b. 0x5cb2b mov eax,-1; ret.
=> gate = shape[+4]+1 <= 0 || shape[+8]+1 <= 0 (W-1/H-1 fields must be >= 0).
A record whose W and H read 0 in EVERY candidate slot CANNOT be drawn —
independent of selector. Then rect clamp + 0x5cb14..0x5cb22 -2 empty-clip;
error set {-1 @0x5cb2b, -2 @0x5cb36} re-confirmed; no stream-overrun error
(S20 law re-confirmed on this disassembly).

## S2 SELECTOR-SITE PROBE + FEASIBILITY VERDICTS [verified this session]

S2a MOUSE (k5/k6/k7, decision-sheet C27/C28/C29): REAL ART — span 2062 each,
2038 stream bytes at the canonical stream slot (rec+0x18, S16/S17 law).
measured this session (scripts/r328_hdr.py + inline S9 walk):
  - u16 dims at rec+0 = 46x77 for ALL THREE; S9 walk from rec+0x18 with
    those dims completes EXACT-H 77/77 rows for k5, k6, k7 (same result for
    passing k4). NOTE t196 S20.1 claimed "mouse k6/k7 not walkable" — that
    walk used the CANONICAL A dims (u32@+0x10); with the u16@+0 pair all
    three walk EXACT-H. [banked correction]
  - canonical A dims u32@rec+0x10: k5 (0,46), k6 (77,0), k7 (0,0) — each
    has a zero component -> pinned dims-gate (t197, both sides, (0,4096])
    rejects -> validator FAIL class. THE MOUSE CASE IS A DIMS-SLOT-LOCATION
    DISPUTE, not junk: valid bytes exist at +0, plausible-invalid at +0x10.
  - windows.txt: NO SHAPEITEM line references mouse.shp (census: the 7
    SHAPEITEM lines are 4x 1starmap + 3x 3cfgnew); name string
    'DATA\MOUSE.SHP' @0x84314 (gsystem.cpp string neighbourhood) has ZERO
    u32 references in code range [0x14bb0,0x82bb0) AND zero in obj1 (honest
    negative; calibration: same-scan DOES find refs for planets/LGRACE/planal
    names, so absence is informative but the reference form for MOUSE.SHP is
    simply not located). CURSORSHAPE 2 exists (2 windows: TYPE 100 cosmos
    @line 216, BatModeWnd @1186). WHO SELECTS k5/k6/k7 = UNKNOWN.
  => FEASIBLE-BY-CAPTURE (the only 3 records where a witness can decide):
    runtime shape-struct dims (blit [ebx+4]/[ebx+8]) measured live + screen
    compare vs our u16@+0 decode. DESIGN queued as t330 (S4).

S2b 1starmap k1 (C14): zero stream bytes (span 24 = header only); u16@+0
dims 30x50 valid; canonical A dims u32@+0x10 = 0x7FFFFFDB/0x7FFFFFA6
variant words (invalid). windows.txt SHAPEITEM selects 1starmap k3,k4,k5,k7
(lines 456/477/498/517) — NOT k1; SHAPEFILE 1STARMAP.SHP @178 binds the lib
to TYPE 100 (star-map window). No citable selector for k1. Zero-stream means
a draw would paint 50 rows of NEXT-RECORD BYTES (no-overrun-error law) —
garbage, not art. => CITED-NO-WITNESS for art purposes; the t330 star-map
phase blit census settles code-side selection for free (if sel==1 never
fires, the no-selector claim is live-witnessed too).

S2c COMBAT FAMILY (25 zero-stream ladder slots, group B): every lib named in
extracted/ascend00/batfx.txt (battle-effects list, "// here are the names",
81 entries: destroy.shp line 10, expl00..08 lines 24-32, sgNNexpl lines
~50-66, orbex00..02 lines 75-77). MEASURED zero-stream 25/25 (span==header:
8 for the k0-variant variant-header libs, 24 for k>=1). NOT dims-zero
(task-text correction, S1 GROUP B): u16@+0 dims are plausible (139x139,
199x199). Verdict = combat-effect class => UNREACHABLE-BY-CAPTURE per t323
amendment (cited), zero probes. CITED-NO-WITNESS (draws nothing meaningful:
zero stream bytes at the only law-cited stream slot).

S2d cos_star k40..k51 (C2..C13): MEASURED all-zero 24-byte headers 12/12
(every candidate dims slot is 0) + 3 stream bytes each. Blit -1 gate
re-verified from raw asm (S1b): W-1/H-1 read from shape struct; an all-zero
struct: eax=[ebx+4] (=W-1), inc eax (=W), jle -> -1 when W<=0; same for H at
[ebx+8]. cos_star k40..51 have ZERO at every candidate dims slot, so W==0
whichever slot the loader used -> -1 @0x5cb2b is drawn-nothing independent of
selector. t200 selector law (SEL=4*star_type+cls,
types 0..12, planets-ui.md S6) additionally bounds addressability. =>
CITED-NO-WITNESS, 12 records, exactly as the task text predicted.

S2e sg50expl k9 (C40): span 27 AT FILE EOF, header 8b 00 8b 00 46 00 46 00
fc ff ff ff 08 00 00 00 fc ff ff ff 08 00 00 00 — near-empty (3 stream
bytes) + truncated; batfx.txt line 58 = combat. UNREACHABLE-BY-CAPTURE
(t323) + zero-stream corroboration. CITED-NO-WITNESS.
S2f sg64expl k0 (C41): span 1162, header variant '12 00 00 00 fb ff ff ff'
(S3 class); batfx.txt line 63 = combat. UNREACHABLE-BY-CAPTURE (t323).
S2g 3cfgnew k12 (C1): span 2391 AT FILE EOF; walk short 55/79 rows at EOF
(S20/S21: fails even the UNBOUNDED walk — broken vendor data outright);
SHAPEITEM selects 3cfgnew k0 only (lines 612/631/650). JUNK-CERTAIN (cite).

## S3 FEASIBILITY TABLE (44 C-rows) — summary
  CITED-NO-WITNESS (vendor draws nothing / nothing meaningful): 12 cos_star
    (zero dims every slot + blit -1 gate, t200 law) + 25 ladder slots
    (zero stream bytes + batfx.txt combat attribution) + 1starmap k1 (zero
    stream + no citable selector) + sg50expl k9 (near-empty+EOF, combat) = 39.
  UNREACHABLE-BY-CAPTURE cited (t323): sg64expl k0 (+ sg50expl k9 dual-class).
  JUNK-CERTAIN: 3cfgnew k12 (EOF truncation) = 1.
  FEASIBLE-BY-CAPTURE: mouse k5/k6/k7 = 3 (dims-slot dispute; design t330).
  Total 44 = exact C-row count. 41/44 leave the human ask; 3 remain.

## S4 t330 DESIGN — ONE-LAUNCH MOUSE-DIMS DRAW-CAPTURE (DESIGNED, NOT RUN)
Tool: scripts/r1_dbg_session.py via ~/.hermes/hermes-agent/venv/bin/python.
Scratch copy of the Oct-29 save (NEVER mount game/); own ring; r322
relaunch loop; SIGKILL teardown by recorded PID.
Legs (LEGSPEC additions):
  blit_entry  0x5caac hot=True   — total draw census baseline per phase.
  blit_refuse 0x5cb2b hot=True   — dims-gate -1 census (fires ONLY on
                                   invalid runtime dims).
  blit_deref  0x5cb59 hot=False-if-feasible — ESI=[ESI] entry deref; capture
                                   payload base -> map to cache slot via
                                   S17 anchor CACHE=0x2e1194 (slot PAY ptrs)
                                   -> LIBRARY attribution of every blit.
Phases: ENTER game; visit cosmos map, planet screen, research, fleet, fleet
orders, intel, ship design, diplomacy; hover UI edges (cursor-change hunt);
one scripted battle IF reachable (t323: magnetron road dead — battle phase
OPTIONAL, not a blocker). Screenshot per phase (convert ppm:- law, t325).
Verdict grammar: if ANY phase shows blit_refuse count > baseline AND the
deref census attributes a mouse.shp slot payload to that blit -> the vendor
REFUSES k5/k6/k7 (canonical-slot law holds; records = never-drawable,
CITED-NO-WITNESS). If a screen visibly contains a 46x77 mouse panel
(vision-by-context, t193 law) AND our u16@+0 decode matches it -> vendor
draws it with +0 dims; slot-location question CLOSED by measurement.
Budget: 1-2 attempts; if mouse.shp is never loaded (no cache slot matches
mouse content in any phase), honest negative banked: library loaded only by
gsystem.cpp path we cannot trigger -> mouse k5/k6/k7 join UNREACHABLE class.
