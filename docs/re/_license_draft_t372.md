# _license_draft_t372.md — GPL-3.0-or-later adoption record + landing
# procedure (t372, 2026-11-11). HAND-AUTHORED; no generator names this file
# (grep 'packaging|_license_draft' scripts/* = 0 by the t371 control, re-run
# t372: see S5). Companion: docs/re/_notice_draft_t372.md (NOTICE text).

## S0. The decision being applied

User decision 2026-11-10 (STATE queue header, phase 8): license the engine
code **GPL-3.0-or-later**, plus a written unrestricted-use grant OFFERED to
the original creators at their option (the offer text lives in the NOTICE
draft; rationale: copyleft blocks closed derivatives, the side-grant gives
the people who made Ascendancy freedom to do anything with our code without
infecting their choices). D5 annotated in docs/DECISIONS.md this iteration.

## S1. License text source (verbatim, on-box, NOT fetched)

File: /usr/share/common-licenses/GPL-3 (Debian `common-licenses` package).
Measured 2026-11-11:
  - size 35,149 bytes, 674 lines
  - md5 1ebbd3e34237af26da5dc08a4e440464
  - sha256 3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986
    (MEASURED 2026-11-11; this is the anchor of record — t373 asserts it
    after `install`, and any session with URL approval may diff against
    https://www.gnu.org/licenses/gpl-3.0.txt once)
  - structure check (grep, all present): header "GNU GENERAL PUBLIC LICENSE /
    Version 3, 29 June 2007" (L1-2), FSF verbatim-copying notice (L4-6),
    "TERMS AND CONDITIONS" (L71), numbered sections 0..17 (L73 "0.
    Definitions." .. L612 "17. Interpretation of Sections 15 and 16."),
    "END OF TERMS AND CONDITIONS" (L621), "How to Apply These Terms to Your
    New Programs" appendix (L623) with the standard <one line>/<year>/<name>
    notice template.
  - HONEST NEGATIVE: a byte-diff against https://www.gnu.org/licenses/gpl-3.0.txt
    was NOT run this iteration (URL-fetch policy: the queue pre-approved
    exactly one fetch, spent on motesandbeams.com). The md5 above is the
    anchor: any future session with approval may fetch gnu.org once and
    diff; a mismatch before t373 landing would be a stop-the-line event.
  - The FSF text is itself designed for verbatim redistribution ("Everyone
    is permitted to copy and distribute verbatim copies of this license
    document, but changing it is not allowed." — L4-6 of the file).

## S2. "or later" version wording

SPDX id: `GPL-3.0-or-later`. Source files carry
`SPDX-License-Identifier: GPL-3.0-or-later` (S4). The README/NOTICE prose
says "GPL-3.0-or-later". The LICENSE file is the v3 text alone — that is the
standard shape: the "+" comes from the per-file identifier / the
"or (at your option) any later version" clause in each file's notice block,
not from bundling multiple license texts.

## S3. Landing procedure (t373 executes, atomic with README + .gitignore)

1. `install -m644 /usr/share/common-licenses/GPL-3 LICENSE` at repo root;
   immediately `md5sum LICENSE` and assert == S1 md5 (the evidence-rule
   habit: no constant without a witness).
2. `install -m644 docs/re/_notice_draft_t372.md NOTICE` (strip this
   draft-comment header line first — the NOTICE body starts at its S0).
3. Swap README.md from docs/re/_readme_draft_t371.md (its <TBD-contact-t372>
   placeholder now resolves to the contact routes banked in packaging.md S8:
   mailto contact@motesandbeams.com is the *creator* route; the repo-author
   contact stays <TBD-t373> — user's call what to publish about themselves).
4. .gitignore per packaging.md S3 incl. the 4 tracked work/ survivors
   (t371 landmine) — `git rm --cached` those before adding ignore rules.
5. Re-run `bash scripts/gate.sh` green after the swap (gate stage list is
   milestone-keyed, adding root text files cannot break stages, but the
   evidence rule says measure, not assume).

## S4. SPDX header sweep plan (measured census 2026-11-11 — list, don't
bulk-edit blind; headers land with t373 per queue)

Census method: git ls-files, extension filter {.c .cpp .h .hpp .py .sh},
first-400-bytes scan for 'SPDX-License-Identifier'. RESULT: 506 code-ish
tracked files, HAS=0, MISSING=506. Per-directory breakdown:
  rewrite  .cpp 58   .h 24          (= 82; publishable rewrite src+tests+build)
  scripts  .py 364   .sh 53  .c 1
  tools    .c 1      .cpp 2
  archive  .sh 1
  work     .py 1     .sh 1          (the t371 landmine survivors — see below)
Rules for t373:
- Insert as the FIRST comment line (comment syntax per language: // for
  c/cpp/h, # for py/sh). Never touch archive/ (historical state; one .sh —
  skip it, provenance matters more than uniformity there).
- work/ files: they are publish-excluded (packaging.md S3 landmine). Sweep
  them ONLY if they stay tracked; if t373 untracks them (recommended), they
  leave the sweep set: 504 files.
- No copyright line is auto-inserted: asserting a copyright holder on the
  user's behalf is the user's call (see S7). SPDX identifier alone is safe.
- After the sweep: `grep -rL 'SPDX-License-Identifier' <sweep set>` must
  print nothing, and `bash scripts/gate.sh` + run_tests must stay green
  (comment-only change; the pin tests compile the sources, so a broken
  comment = build break = caught).

## S5. Hand-authored-file control (re-run this iteration)

`grep -n 'packaging\|_readme_draft\|_license_draft\|_notice_draft\|LICENSE'
scripts/*.py scripts/*.sh` over all scripts: only hits are gate-stage
comments about docs/re regeneration lists, none opens any of the four
distribution files for writing. Root LICENSE/NOTICE do not exist yet
(measured `ls` — confirmed this session), so no generator can clobber a
draft that hasn't landed.

## S6. Landing anchors

LICENSE: assert md5 1ebbd3e34237af26da5dc08a4e440464 AND sha256
3972dc97...36986 (both measured 2026-11-11 on the source file; S1).
NOTICE sha256: <fill at S3 step 2, after the draft-comment strip>.

## S7. Open items deliberately NOT decided here (user-gated, not blockers)

- Repo author identity to publish in README/NOTICE copyright lines (git
  identity exists: hrethric <[REDACTED-EMAIL]> — whether
  that is what goes on a public repo is the user's decision, not ours).
- Whether artifacts/ (packaging.md S2 gray item) ships. Unchanged from t371.
- GitHub remote/org/name: stays USER-gated per queue.
