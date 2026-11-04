# _wip_t98 — WLINK ID-Info parse: SO-block -> kind tie (STATIC, ANALYSIS-ONLY)

TASK (STATE.md t98): parse the WATCOM WLINK debug records of game/ascend.exe
ONCE, properly (spec-first), to tie the SO name block (image FILE 0x88e60 ==
exe-file 0x8b8b0, delta +0x2a50 pinned t97c) to kind numerics via a SYMBOL
TABLE. Target names 'SONothing'..'SOGoSpace' (8 names stride 20).

BANKED CONSTRAINTS (do not repeat):
- t97c: object-table parse at DW(le+0x30) broke at obj 47 (name-count
  semantics guessed WRONG twice). Format must come from a fetched spec.
- t97c: ZERO raw u32 == 0x8b8b0 / 0x88e60 anywhere in the exe. A symbol tie,
  if present, encodes the address object/segment-relative -> parse segment
  table (offSegTab DW(le+0x34)) arithmetic before concluding absence.
- R3: LE header field-map route is CLOSED for memory-size questions (no
  object parse sums cbObject==cbImage). This task is DIFFERENT scope: debug
  ID Info records, not the memory map. R12: no u32 scans for ties; byte-
  level name search of the debug region IS legitimate (names live in ID Info).
- Branch (3) outcome rules: if records name the block but no enum -> bank as
  SUPPORTING evidence, annotate OQ-016 (A5 component CLOSED as debug-only
  identifiers), queue A6 (0x43b50 tail) as t99. If debug info stripped ->
  cited negative (record absent per spec walk) + REFUTED-ROUTES entry
  killing LE-debug route + t99 = A6.

STATUS LOG
- [init] sitting watch re-checked: live-timeline.jsonl mtime 2026-10-26
  15:44 unchanged, no new sitting -> assignment stands.
- [spec FETCHED, cached /home/hrethric/.hermes/cache/web/archive.org-
  c9e087b277.md] IBM OS/2 16/32-bit LX Specification rev 11 (June 2001),
  archive.org/download/IBMOS2Warp4ToolkitDocuments2/lxref.htm. KEY LAYOUTS
  [verified vs spec]:
  * LE header (at DW(mz+0x3c), sig 'LE'/'LX'): OBJECT TABLE OFF = DW(le+
    0x40), # OBJECTS = DW(le+0x44) (header-relative); OBJ PAGE TBL OFF =
    DW(le+0x48); RES NAME TBL OFF = DW(le+0x58), ENTRY TBL = DW(le+0x5c);
    NON-RES NAME TBL OFF = DW(le+0x88) FILE-relative + LEN DW(le+0x8c);
    DEBUG INFO OFF = DW(le+0x98) FILE-relative (spec explicitly corrects
    an older "header-relative" claim), DEBUG INFO LEN = DW(le+0x9c);
    DATA PAGES OFFSET = DW(le+0x80) FILE-relative.
  * Object table entry = 20 B FIXED: vsize DW, reloc_base DW, flags W,
    page_tbl_idx W, #page_tbl_entries DW, reserved DW. NO NAME STRINGS IN
    OBJECT TABLE AT ALL — t97's "name-count semantics" premise was a
    phantom; its real bug: DW(le+0x30) is FIXUP SECTION SIZE per spec
    figure 3-7, NOT the object table offset. t97 parsed from garbage.
  * Debug section (§2.18): format debugger-defined; FIRST 4 BYTES = type
    signature 'NB0'+n (0=32-bit CodeView, 2=16-bit CodeView, 4=PM-debugger);
    WATCOM WLINK uses its OWN debug-block format in this section.
    Section sits at file tail (order: header, resident, non-resident, debug).
  * Resident/Non-res name table entries: LEN + ASCII + type byte (0x05
    module name, 0x08 entry point) per §2.7.
- [inferred] exe 0x8f6d3 total; SO block at exe-file 0x8b8b0 leaves
  0x3e23 past the block — enough room for a WLINK debug block at tail.
- PROBE PLAN: (1) header per spec: object table (20B fixed entries) ->
  reloc bases of obj0/obj1 -> cross-check vs live P0 law (obj0 code
  [0x14bb0,0x82bb0)@P0code etc.); (2) DW(le+0x98/0x9c): debug off/len —
  ZERO => STRIPPED => cited negative branch; nonzero => dump first 4
  bytes signature + scan region for 'SON' name occurrences + object-
  relative arithmetic (block intra-obj offset = 0x8b8b0 - obj1-file-base).

## t98 probe findings (streaming)

P1 [verified] DEBUG INFO OFF = DW(le+0x98) = 0, LEN = DW(le+0x9c) = 0 ->
  per spec §2.18/§2.2 NO DEBUG SECTION EXISTS at all (loader-legal: "table
  offsets may be set to zero to indicate the table does not exist").
P2 [verified] Whole-file signature scan: 'NB03' 0, 'NB00' 0, 'ODIAG' 0,
  'DWARF' 0, 'OS21001' 0, 'watcom' 0, 'B32' 0, '.obj'/'.OBJ' 0,
  'shiporders' 0. ('WATCOM' 4 hits: 0x371/0x3c7 = stub/DOS-string area,
  0x7ad76/0x7ada7 = in-image runtime strings, not debug records.) The ONLY
  occurrence of each SO name in the whole exe is the block itself
  (0x8b8b0 / 0x8b93c). No object/module name table vocabulary exists.
P3 [verified] Structural fit: loader section at le+0xb8 = file 0x2b08
  (DW(le+0x38)=size 0x149b1), OBJECT TABLE OFF DW(le+0x40)=0xc4 (header-
  relative -> file 0x2b14), #OBJECTS DW(le+0x44)=2, OBJ PAGE TBL DW(le+0x48)
  =0xf4 (file 0x2b44), RESIDENT NAME TBL DW(le+0x58)=0x2d8 (file 0x2d28)
  parses CLEAN per §2.7: len=4 'corn' type=0x00 (module name — the game's
  internal module name), ENTRY TABLE file 0x2d30 (adjacent). objtab->optab
  span = 48 B / 2 objects = 24-B entries (WLINK variant, 4 B larger than
  spec's 20 — the 20-B read yields implausible obj2 vsize=0).
P4 [inferred, from npages arithmetic] datapages=0x17600, npages=121 ->
  demand-page end 0x90600 > exe len 0x8f6d3 (short by 0xf2d). Page table
  head u32s = 0x10000,0x20000,0x30000... = raw FILE offsets at face value
  (no <<shift despite shift=211/0xd3 field) — code pages start at file
  0x10000. Image bytes 0x17600.. carry the demand pages; exe tail = last
  partial page (0x3d3 within page 121).
NEXT: (a) parse 24-B object entries properly + entry table; (b) adjudicate
whether the two objects' file spans cover 0x8b8b0 (they must — the names
are IN the demand pages = obj2/data); (c) verdict hinges on P1+P2: cited
negative = debug section ABSENT per spec header walk + zero debug
signatures + zero name duplicates => NO symbol table can tie the block;
then REFUTED-ROUTES entry + t99 = A6 per assignment branch (fail).

## CONCLUSION (task complete)
Verdict = FAIL-BRANCH of the assignment: debug info STRIPPED at ship time
(cited: DEBUG INFO OFF/LEN=0/0 + zero signatures + each name unique).
Executed per assignment: (a) honest negative banked aicode.md §2i; (b)
REFUTED-ROUTES R14 kills the LE-debug route; (c) OQ-016 annotated — A5
component CLOSED as debug-only identifiers per t97 rule, row STAYS OPEN
(A6/A7 remain); (d) t99 = W6-A6 (0x43b50 tail + 0x2ef60 cases) assigned
in STATE.md with ordering rationale. Bonus closure of a harness bug:
t97c's root cause (DW(le+0x30) = FIXUP SECTION SIZE, not objtab) written
into R14 + §2i so no third parse attempt is ever needed. Tool
scripts/r1_t98_wlink.py RC=0. Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT
OK (open set unchanged {003,005,016,019,020,021,023}). Spec source cached:
~/.hermes/cache/web/archive.org-c9e087b277.md (IBM LX spec rev 11).
This wip file is now the full working record; aicode.md §2i is the bank.
