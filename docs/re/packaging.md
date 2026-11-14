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
work/r363_gizmo_rows.json. A publish filter that only drops `work/` would
MISS these.
**DISPOSITIONED t373 (2026-11-11):** `git mv` -> scripts/t368_ring_turn.py
(path math patched, re-run verified parsed=20/20) and
scripts/sentinel_t369.sh (absolute REPO path, no edit needed);
`git rm --cached` the .out/.json (evidence stays on disk + regenerable by
scripts/r363_gizmo_census.py). `git ls-files work/` now prints NOTHING, and
gate.sh carries a recurrence check (fails the gate if any work/ file is ever
tracked again).

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

(a) QUOTE AUDIT RUN t373 — CLOSED as measured. Tool
    scripts/r373_quote_audit.py (corpus: every .txt/.dip/.gam under
    extracted/, cp437, distinct stripped lines >= 12 chars = 5297; longest
    run of consecutive verbatim lines per docs/re/*.md). RESULT: 1 doc with
    any span at all — ui.md, 4 lines (vendor table rows like
    "SMALLSEED      1"); everything else 0. Positive control: pasting 6 consecutive
    gizmos.txt lines into a probe md reports 6, so the audit is not blind.
    No wholesale paste exists in docs/re; the NOTICE fair-use-length claim
    holds.
(b) CLOSED t373 by measurement: cob.py extract IS the complete importer.
    ascend01 -> 328 files, ascend02 -> 89 files (incl. the compressed
    entries); `diff -r` vs the loop's reference extracted/ trees = 0
    differing lines for BOTH archives (ascend00 54 files, gate-checked).
    README now states the three-command flow as fact, and gate --portable
    with ASCENDANCY_DATA=<vendor install dir> runs the extraction
    automatically (verified on a vendor-stripped clone: exit 0, full
    vendor stages). The ascend02 .bin/.tsv side was already covered by
    this: those live in extracted/ascend02/data/ (flc/voc/fnt/raw), which
    the same command produces.
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


## 11. t373 LANDING (2026-11-11) — root swap executed, hygiene verified

- LICENSE: `install -m644 /usr/share/common-licenses/GPL-3 LICENSE`;
  post-install ASSERT PASS on both anchors (md5 1ebbd3e34237af26da5dc08a4e440464,
  sha256 3972dc97...36986). Byte-diff vs gnu.org still NOT run (URL budget;
  hashes are the anchor of record — S1 honest negative unchanged).
- NOTICE: from _notice_draft_t372.md minus its 4-line draft header
  (`tail -n +5`): 2417 B, sha256
  2e5f4153f90632b448bab4761f064867a18be6cb35645c1794ee9ee98a5dd3bf.
  Copyright holder line intentionally still `<TBD-t373: repo author name>` —
  author identity is USER-gated (license draft S7). Landing the file with the
  placeholder is safe: the grant text needs no holder to be an offer.
- README.md replaced by the t371 draft + t373 edits: ascend01/02 importer now
  stated as a VERIFIED three-command flow (S9b); Windows vcpkg downgraded to
  honest "expected-to-work, not tested" (negative (c) unchanged — no vcpkg on
  this box); gate section documents --portable + ASCENDANCY_DATA; the
  authentic-vs-defaults section from the old README kept (it is the public
  honesty statement) with OQ-003/OQ-005 residues as-is.
- SPDX sweep EXECUTED: scripts/r373_spdx_sweep.py, 505 files inserted
  (rewrite 82, scripts 420 incl. the 2 moved survivors, tools 3; archive/
  SKIPPED per S4; idempotent --check mode exits 0 = 0 missing). Placement
  law: after shebang; after shebang+coding-cookie (4 files carry PEP-263
  cookies on L2 — pushing them to L3 would void them). No copyright lines
  inserted (S7). Post-sweep: all 365 .py py_compile-clean EXCEPT
  scripts/r1_shp_streamlaw_variants.py, which is broken at HEAD since t67
  (literal `...[truncated]` paste artifact — verified identical failure on
  the pre-sweep HEAD blob; NOT a t373 regression; gate never runs it).
- gate.sh: `--portable` flag + `ASCENDANCY_DATA=<dir>` env (symlink game/ +
  auto-extract extracted/ once); 25 stages wrapped in `[ "$VENDOR" = 1 ]`
  skip-with-note guards (VENDOR = ascend.exe present AND ascend00 >= 54
  files); default no-flag behaviour unchanged (missing game/ = FAIL);
  recurrence invariant wired: gate FAILS if `git ls-files work/` is ever
  non-empty again; 3r gained the missing revenv guard (t343 fresh-clone
  gap); 4f vendor-gated (pub-clone test caught it reading
  extracted/ascend02/data/intro65a.flc).
- CLONE VERIFICATION (the queue's "verify" bar), all exit 0 on this box:
  (A) raw clone --portable; (B) PUBLISHED SHAPE (clone minus game/ and
  extracted/ = the actual distribution) --portable, 28 skip-notes;
  (C) published shape + ASCENDANCY_DATA=<real vendor install dir>
  --portable: auto-extraction ran (ascend00 54 confirmed) and the FULL
  vendor stage set executed — only work/-capture stages noted-skipped.
- GitHub push: NOT done — USER-gated (remote/org/name = user's call).


## 12. t383 RE-EXPORT (2026-11-12) — verified pushable tree + history scrub

- Fresh export `GITHUB_USER=weylandsmith bash scripts/publish_public.sh
  /tmp/pubpush-t383b` exit 0: "vendor-free history, 6149 objects, 11M .git,
  tree intact." (first export of the session, /tmp/pubpush-t383, predated the
  scrub: 6143 objects; superseded and deleted.)
- HISTORY: 568 commits, author+committer UNIFORM "Weyland Smith
  <weylandsmith@users.noreply.github.com>"; refs/original 0.
- PRIVACY FINDING (the iteration's real one): a tip-only redaction is NOT
  enough — docs/re/_license_draft_t372.md held the personal git-identity
  address ([ISP-DOMAIN] domain, withheld) in 25 historical blobs; pushing without a
  history scrub would have leaked it. publish_public.sh 1b now rewrites every
  blob via --tree-filter sed scoped to that path, and a fail-closed gate
  batch-scans ALL blobs (rev-list --objects | cat-file --batch | grep -a) for
  SCRUB_PATTERN=[ISP-DOMAIN] — exit 5 on any hit. Post-scrub scan: 0 hits
  for "[ISP-DOMAIN]" AND 0 for "hrethric@" across every blob.
- TOOL PITFALLS banked: (1) this box's git filter-branch has NO --blob-filter
  (git-filter-repo only; not installed) — first attempt exit 1; (2) a
  [^[:space:][:punct:]] email class stops at '@' and leaks the local part —
  use [A-Za-z0-9._%+-]*domain[A-Za-z0-9.-]*; (3) per-commit `git grep
  $(git rev-list --all)` over 568 commits timed out at 300 s — the batch
  cat-file scan is the shape that works; (4) no generator writes
  packaging.md/_license_draft_t372.md (scripts/ grep = comment citations
  only) — both safe to hand-edit.
- VERIFIED ON THE CLONE (no vendor data): cmake Debug + build -j4 exit 0;
  run_tests exit 0 "270 tests, 192 skipped, 0 failed" (observer pins: 5 SKIP
  no-vendor, 2 ok incl. synthetic terminator + render map). Keep-checks pass;
  NOTICE "Copyright (C) Weyland Smith". origin set to
  https://github.com/weylandsmith/ascendancy-rewrite.git on the verified tree
  (set-url only — push is USER-gated, NOT run).
- OPEN DISPOSITION (user's call, not a blocker): 160 tracked files carry the
  plain username "hrethric" inside /home/hrethric paths (scripts, docs). It
  is a username, not an email/credential; scrubbing it would rewrite hundreds
  of path strings across history. Left as-is for the push.

## t389 RE-EXPORT + VERIFY + PUSH LANDED (2026-11-14)

- Export: `GITHUB_USER=weylandsmith bash scripts/publish_public.sh
  /tmp/pubpush-t389` exit 0 — "vendor-free history, 6298 objects, 5.6M .git,
  tree intact." game/ extracted/ work/ archive/user-saves docs/assets all
  absent from the tree; artifacts/ holds only README+tsv stubs (vendor
  derivatives filtered); identity uniform across ALL history: single email
  weylandsmith@users.noreply.github.com (`git log --all --format=%ae | sort -u`).
- VERIFIED ON THE CLONE (no vendor data): cmake (empty build type) + build -j4
  exit 0, ZERO warnings, ascend_ui BUILDS on the export (t389 key-fact 1 — the
  CMakeLists run_tests->ascend_ui link + SDL2_mixer headers survived the
  filter); run_tests exit 0 "293 tests, 196 skipped, 0 failed";
  ASCENDANCY_DATA=<working repo> gate.sh --portable exit 0.
- PUSH: fetch-FIRST law respected. Trap hit + banked: publish_public.sh clones
  from the local SRC, so the export's `origin` is the WORKING REPO path — a
  naive fetch/ls-remote grades against the wrong remote. Fix: `git remote
  set-url origin https://github.com/weylandsmith/ascendancy-rewrite.git`
  BEFORE fetch. Remote tip was b2539b3; `merge-base --is-ancestor` confirmed
  FAST_FORWARD_OK; push landed `b2539b3..36bf92d main -> main`;
  ls-remote origin main == 36bf92dbb4bdf12d2a76bb0ff88fbdc26980621c (the
  exported t388b tip). 7 commits shipped: D9 records, t385+t385b, t386, t387,
  t388, t388b (49 files, +4690/-195). No force needed; askpass helper
  /tmp/t389_askpass.sh deleted after use (verified absent).
- SEED REGRESSION (engine-untouched proof, pre-push): baseline worktree
  /tmp/t389-baseline @ c7a3fda (last commit before phase 10); `--headless
  --campaign 1600` seeds 1/2024/23 byte-IDENTICAL base vs HEAD
  (md5 7e794a6d.../332a8cf3.../0a6b7876...), victories Extinct t266 / Extinct
  t285 / Control t1406 == the t365 banked record (docs/re/engine-flip-t365.md
  L28-30). Match the working repo's EMPTY CMAKE_BUILD_TYPE when byte-comparing
  builds. Baseline worktree removed after (`git worktree list` clean).
