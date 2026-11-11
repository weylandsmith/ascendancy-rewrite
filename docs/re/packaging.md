# packaging.md — distribution split for the public tree (t371, 2026-11-11)

HAND-AUTHORED (t371). No generator writes this file: verified 2026-11-11 by
`grep -ln "docs/re/" scripts/*.py | xargs grep -l "open(.*'w'"` — no script
names `packaging.md` (grep "packaging" over scripts/ = 0 hits), and gate.sh
regenerates only the attribution/census docs listed in BLOCKED.md traps
(attribution.tsv, gizmos/economy/modules/ships/planets censuses), never this
one. If a future gate ever rewrites this file, that is a bug: git diff it.

## 1. Why a split exists

User decision 2026-11-10 (STATE queue header): **ship WITHOUT vendor data**.
The repo today mixes three classes of content that a public tree must treat
differently: (a) our own code + evidence, (b) the vendor's copyrighted
distribution files, (c) capture corpus / live session state. The split below
is a *content* plan — no git history surgery yet (that is t373, and the push
itself stays USER-gated).

## 2. Publishable tree inventory (measured 2026-11-11, `git ls-files` = 1362
tracked files, 182.0 MB total)

| top dir | files | MB | verdict |
|---|---|---|---|
| rewrite/ | 84 | 1.03 | PUBLISH (src/game 10+ units, src/formats, src/ui, tests 36 files; CMakeLists C++17) |
| docs/ | 178 | 8.11 | PUBLISH (docs/re 115 evidence specs + control plane + PLAYTHROUGH + BASELINE.sha256→see §4) |
| scripts/ | 425 | 2.55 | PUBLISH (gate.sh, ledger audits, probes, capture stack — capture stack ships but is inert without work/) |
| artifacts/ | 6 | 0.62 | PUBLISH-CONDITIONAL: ascend_restored.bin + functions_full.tsv are DERIVATIVES of ascend.exe (fixups rewritten on the vendor payload). Ghidra-space exe derivative — include only if the license stance (§6) covers exe derivatives; otherwise publish artifacts/README.md (provenance+validation record) and let users rebuild via scripts/r1_restore_sites.py. RECOMMEND: publish README only. |
| archive/ | 166 | 2.03 | PUBLISH (state-v2-full 159 + ralph-v1 7: loop working memory, no vendor bytes — verified: no game files under archive/) |
| tools/ | 3 | 0.02 | PUBLISH (xsend.c etc.) |
| (root) | 2 | ~0 | PUBLISH (README.md rewritten this task, .gitignore) |
| LICENSE, NOTICE | 0 | — | TO ADD at t372 (GPL-3.0-or-later text + creator-grant notice) |

Publishable total ≈ 864 files, ~14.3 MB (measured: sum of tracked sizes for
rewrite+docs+artifacts+scripts+archive+tools+root).

## 3. Excluded set (never publish)

| path | MB | why | regenerable by user? |
|---|---|---|---|
| game/ | 23 files, 94.2 | vendor distribution: ascend.exe, .cob archives, resume.gam, drivers, manual PDF. Copyrighted; gate checksums it vs docs/BASELINE.sha256 | NO — user must supply their own install |
| extracted/ | 471 files, 73.5 | vendor content unpacked from the .cob archives (tables, text, audio, FLC). Copyrighted derivative | YES from a supplied install: `python3 scripts/cob.py extract game/ascend00.cob extracted/ascend00` (control-verified this iteration: `cob.py list game/ascend00.cob` → "54 entries … table=ok"). ascend01/02 + the .bin/.tsv side: see docs/re/datafiles.md (RAM name-table route) — full one-command importer is a t373 follow-up item |
| work/ | 17 GB | capture corpus: save rings, timeline (9.1 GB live-timeline.jsonl), scratch sessions. Private + enormous | partially (re-capture); nothing in a public tree needs it |
| work/r1/playcap/live-timeline.jsonl | 9.1 | called out separately because it is the single largest file in the tree and is LIVE (production watcher pid 107679 appends continuously) | no |
| rewrite/build/, build*/, .venv, __pycache__ | — | build artifacts; already .gitignore'd | yes (cmake) |

**Tracked-file landmine (measured):** despite `work/` being in .gitignore,
4 files ARE tracked (added with -f historically): work/r1/sentinel_t369.sh,
work/r1/t368_ring_turn.py, work/r363_gizmo_census.out,
work/r363_gizmo_rows.json. t373 must decide: move the two .py to scripts/
(they are tools) and `git rm --cached` the .out/.json (or move under docs/
as evidence). A publish filter that only drops `work/` would MISS these.

## 4. Evidence-rule file: docs/BASELINE.sha256

Stays in the public tree: it is our checksum manifest of the vendor install
(hashes only, no vendor bytes), and gate.sh P0 refuses to run without it
(gate.sh:18-23 — "NEVER regenerate the baseline from disk"). Shipping hashes
of vendor files is standard practice and does not redistribute content.

## 5. Case-sensitivity audit for Windows (checklist + this iteration's result)

Checked mechanically 2026-11-11 over all 1362 tracked paths:
- [x] two files differing only in case (same lowercase path, >1 spelling): **0**
- [x] file vs directory case collision (a file whose lowercase equals an
      existing dir path): **0**
- [x] non-ASCII paths: **0**
- [x] paths containing spaces: **0**
Still to check at t373 (can't be seen from git ls-files alone):
- [ ] case-stable #include lines: two includes that resolve case-insensitively
      to different headers (grep all `#include "` targets vs actual file case)
- [ ] runtime-constructed paths in C++/Python that hardcode vendor file case
      (the vendor tables are lowercase on disk; any code opening "Gizmos.txt"
      works on ext4-only-by-accident? reverse: opens lowercase — verify)
- [ ] .bat/.ps1 helpers (none exist yet; if CI adds them, keep extensions
      .BAT-insensitive-safe i.e. lowercase)
- [ ] git core.ignorecase hygiene on contributor clones (document in README)

## 6. CI matrix draft (build + run_tests; tests measured 226, 0 failed, 2026-11-11)

| os | compiler | deps | notes |
|---|---|---|---|
| ubuntu-latest | gcc 13 | apt: libsdl2-dev libsdl2-mixer-dev | reference path (this box: SDL2 2.32, SDL2_mixer 2.8 per README) |
| windows-latest | msvc (cl) | vcpkg: sdl2 sdl2-mixer | MSVC needs /W3 parity with gate warnings; vendor path reads must use the §5 checklist result |
| macos-latest | clang (apple) | brew: sdl2 sdl2_mixer | arm64; watch for x86 assumptions in formats/ (byte-order is little-endian-explicit via struct unpack — python side fine; C++ side uses fixed-width LE reads, verify) |

CI scope: `cmake -S rewrite -B build && cmake --build && ./build/run_tests`
(226 tests, no display needed — README). Gate.sh stages needing the capture
stack (dosbox-x, work/, game/) are OUT of CI scope; the --portable gate mode
(t373) is the bridge. xvfb smoke stays linux-only if ported at all.

## 7. README.md draft for the public repo

Draft landed at docs/re/_readme_draft_t371.md (hand-authored this iteration;
the current root README.md is intentionally UNTOUCHED — replacing it is part
of the t373 repo-hygiene execution so README, LICENSE, NOTICE, and .gitignore
land atomically).

## 8. Abandonware status note — cited sources (for README/NOTICE prose)

- Internet Archive hosts the item and states the status verbatim:
  https://archive.org/details/msdos_ascendancy — "Ascendancy is currently
  abandonware." (item: The Logic Factory, 1995, 39.5 MB). [verified 2026-11-11]
- The Logic Factory: founded 1993 by Jason and Todd Templeman; shipped
  Ascendancy (1995), The Tone Rebellion (1997), iOS Ascendancy (2011);
  "In June 2014, The Logic Factory ceased maintaining its website" —
  https://en.wikipedia.org/wiki/The_Logic_Factory [verified 2026-11-11].
  Note: publishers listed on https://en.wikipedia.org/wiki/Ascendancy_(video_game):
  Virgin Interactive / Broderbund / Softgold — publisher-side rights may sit
  elsewhere than the developer; NOTICE prose must not assert the dev grant
  covers publisher rights.
- motesandbeams.com about page FETCHED 2026-11-11 (t372 — the queue row
  pre-approved exactly this one fetch). Verbatim quote: "Mobe, short for
  Motes and Beams, was created by Todd Templeman, author of Space Pilot
  Connor Grant and co-Founder of The Logic Factory, developer of the
  original Space Strategy game, Ascendancy." Page contact routes: mailto
  contact@motesandbeams.com, X @motesandbeams (the page says the company is
  in public testing of "Mobe", hiring C++/3D/open-source people — i.e. the
  site is live and maintained). [verified
  https://www.motesandbeams.com/about.html 2026-11-11]
  HONEST SCOPE: the page establishes Todd Templeman's TLF co-founder
  identity and a live contact channel ONLY. It contains NO licensing or
  rights statement. The creator grant in the NOTICE draft is therefore an
  OFFER addressed to him (and the other creators/rights holders), not a
  grant received — nothing here closes anything.
- Legal caveat for the README: "abandonware" is a distribution norm, not a
  license. Our tree ships NO vendor data (§3), so our copyright exposure is
  code + prose only; the artifacts/ conditional (§2) is the one gray item.

## 9. Honest negatives / open items this audit could not close

(a) The vendor-text files under extracted/ascend00/*.txt (gizmos.txt,
    help.txt…) are the files docs/re/*.md quote from. Publishing docs/re with
    short quotes is fine (fair-use-ish, and quotes are our measurement
    records); publishing extracted/ is not. A quote-audit of docs/re (longest
    verbatim vendor block per file) was NOT run this iteration — add to t373
    checklist: `longest quoted vendor span per docs/re/*.md`.
(b) cob.py extract covers ascend00 (54 entries, table=ok). ascend01/02
    extraction path (compressed entries? per cob.py docstring "entries may be
    compressed") and the ascend02 .bin/.tsv side are NOT verified end-to-end
    as a user-runnable importer. The public "supply your own data" flow is
    therefore INCOMPLETE until t373 lands scripts/r_extract_all.py or README
    states the limitation honestly.
(c) SDL2_mixer on vcpkg: availability/versions as of 2026-11 NOT checked
    (no vcpkg here); the CI row is a DRAFT, not a verified matrix.

## 10. t372 LICENSE DRAFT (appended 2026-11-11; S1-S9 above unchanged)

Deliverables (all drafts; root swap stays atomic at t373 per S7):
- docs/re/_license_draft_t372.md — GPL-3.0-or-later adoption record: text
  source /usr/share/common-licenses/GPL-3 (md5 1ebbd3e3..., sha256
  3972dc97...36986, 674 L, structure greps pass); landing procedure;
  SPDX sweep census MEASURED 506 code-ish tracked files, 0 with headers
  (rewrite 82, scripts 418, tools 3, archive 1, work 2 — work survivors
  leave the set if t373 untracks them: 504).
- docs/re/_notice_draft_t372.md — NOTICE body: GPL header block, dual-grant
  offer to the creators (OFFER, not grant; publisher-rights caveat honored —
  says explicitly the offer covers OUR code only), vendor-exclusion
  statement, abandonware-is-not-a-license note.
- docs/re/_readme_draft_t371.md: <TBD-t372> contact placeholder RESOLVED
  with the cited motesandbeams.com route (S8).
- docs/DECISIONS.md: D5 added, APPLIED 2026-11-10 user decision.
Honest negatives: no byte-diff vs gnu.org (URL budget spent on S8 fetch;
md5/sha256 anchored instead); author identity, artifacts/, remote stay
user-gated. No OQ row touched (license is not a measurement; strict-close
trivially satisfied — nothing closable and nothing closed).
