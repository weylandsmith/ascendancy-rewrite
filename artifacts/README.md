# artifacts/ — committed RE artifacts (t343, 2026-11-08)

Why these are committed while `work/` is gitignored wholesale: both files are
the durable inputs to static probes that run for months (function spans, the
Ghidra-space image every `work/ascend_restored.bin` consumer in scripts/
reads). They are small (~590 KB total), capture-independent in the parts that
matter, and losing them means re-running a multi-hour Ghidra full analysis.
They were COPIED out of gitignored work/ into this tracked directory (no
`git add -f` needed here; the t343 assignment's add -f route was superseded
by the cleaner copy). This README is the provenance+validation record the
commit demands.

## ascend_restored.bin (576,643 B, md5 b3cc18929cfe4bb86700164efb2bc143)
The ascend.exe payload image with every IMAGE-CLASS fixup site rewritten from
Watcom intra-object offsets to d = rv - P0 (payload-file offset; pointer law
docs/re/r1-savestate.md, CLOSED 2026-10-05i). Builder:
scripts/r1_restore_sites.py (needs a work/r1/r1sav-* capture + the raw payload
work/ascend_payload.bin, neither committed). Ghidra loads it at base 0
(seed3_run.sh imports it x86:LE:32:default cspec gcc). Address space == file
offset (base-0 image), code window [0x14bb0,0x82bb0), data 0x82bb0+.

## functions_full.tsv (10,901 B, md5 706a25c1dd21f0496e3a73dec0319b97)
Ghidra FULL-analysis function table exported from ghp5/ascend5
(docs/re/r1-savestate.md "ATTEMPT 3": import ascend_restored.bin, full
analysis, postScript ExportFunctions.java): header `file_off\tsize` + 1,144
rows. PITFALLS (banked, planets-ui.md t200 + STATE archive): sizes are HEX
(int(x,16)), and spans OVERLAP (nested/thunk functions) — pick the tightest
enclosing row. 1,143/1,144 starts in the code window; the 1 outlier is the
data-container container-not-in-any-seeded-function case documented in
r1-savestate.md ~L428.

## Validation (measured 2026-11-08, exit 0)
Command: `python3 scripts/r343_artifact_validate.py`
  V1 rebuild-determinism vs newest capture (work/r1/r1sav-20261011-213606,
     slot 46.sav, H=0x88 B=0x1bf4d8 P0=0x1bf450): CODE WINDOW BYTE-IDENTICAL;
     9 differing bytes in 3 u32-groups, all in the data region (0x8bed0/
     0x8bedc/0x8bee4: committed capture held zeros, the production capture
     decodes image-class values there) — capture-dependent class drift, known
     and expected; the link-time code content is capture-invariant as it must
     be.
  V2 Watcom start density on the restored link-time sites (the population the
     banked law measured): 575/1039 in-code targets = 55.3% start-byte vs
     uniform control 15.6% (3.55x). Banked pairing figure was 60%/15%; this
     artifact re-confirms the law on the committed bytes.
  V3 tsv structure: header exact, 1,144 rows hex-parse, all spans within the
     image, 904 overlapping spans reported (known, not a failure).
