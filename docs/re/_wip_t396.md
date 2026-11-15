# _wip_t396 — PHASE-11 VERIFY + RE-EXPORT + PUSH

Assignment source: docs/STATE.md:231 NEXT ACTION + queue row docs/STATE.md:530.

## Sitting check
- work/r1/playcap/live-timeline.jsonl mtime 2026-11-12 06:45:50 — OLDER than
  t393/t394/t395 (2026-11-15). Ring check t368_ring_turn parsed=20/20
  max_turn=1254 — same sitting as t380..t383. No new play; assignment stood.

## Verification (all PASS)
- Full gate.sh: "ALL CHECKS PASS (milestone=6)", zero FAIL lines, exit 0.
- run_tests: 318 tests, 0 skipped, 0 failed.
- SEED REGRESSION (t389 procedure, packaging.md:283-289): baseline worktree
  @ c7a3fda built Release (same build type as working tree) vs HEAD,
  `--headless --campaign 1600` seeds 1/2024/23 byte-IDENTICAL
  (md5 7e794a6d.../332a8cf3.../0a6b7876... EXACTLY the t389-recorded md5s);
  victories Extinct t266 / Extinct t285 / Control t1406 == t365 record.
  Engine untouched by t393-t395 CONFIRMED. Worktree removed, `git worktree
  list` clean.

## THE ITERATION'S REAL FINDING — the t383 privacy gate was VACUOUS
MEASURED 2026-11-15, discovered while exporting /tmp/pubpush-t396:
1. `xargs -r git cat-file --batch` appends ids as ARGUMENTS; git dies
   "fatal: batch modes take no arguments". With 2>/dev/null + `|| true` the
   scan file was 0 BYTES -> the t383 exit-5 grep could never hit. Batch mode
   reads ids from STDIN. So t383's "post-scrub scan: 0 hits [ISP-DOMAIN],
   0 hits hrethric@ across every blob" was measured on nothing.
2. Independent REAL scan of /tmp/pubpush-t396 (blob-only, 3399 blobs,
   122 MB content, positive control "usage: publish_public.sh" present):
   - 39 blobs carry "hrethric@"/"[ISP-DOMAIN]"/"[ISP-DOMAIN]" markers;
   - exactly ONE blob holds the FULL personal address
     (8-char local-part @ [ISP-DOMAIN].[ISP].org — address NOT written here per
     privacy law): blob 41fd2f61cd03..., path docs/re/_wip_t383.md (a
     pre-t383-redaction historical version; working-tree tip is clean —
     7 bare-pattern mentions only);
   - t383's SCRUB_PATHS covered ONLY docs/re/_license_draft_t372.md — the
     wip file was never in scope. t383's own S3 note even says "no blob may
     hold [the bare domain]" while packaging.md/STATE.md/_wip_t383.md cite
     the bare domain: the gate AS DESIGNED would have failed on its own docs.
3. WORSE: the ALREADY-PUSHED export /tmp/pubt391 (remote main=5373c66)
   contains the SAME full address in 1 blob — it is ALREADY PUBLIC.
   Server-side removal needs the rewrite + force-push, and GitHub GC may keep
   old objects until a support sweep (same open item as the manual pages).
4. hrethric@motesandbeams.com appears in 41 pushed blobs / 48 new blobs —
   disposition below (intentional-public vs leak) checked against README/
   NOTICE.

## Fix shipped in scripts/publish_public.sh (t396)
- (a) scan reads ids on STDIN; FAIL-CLOSED exit 6 if scan < 1 MB;
  positive control: scan must contain a known string ("usage: publish_public.sh").
- (b) mask pass generalized (see script comments): full-address form AND bare
  domain masked across ALL paths; domain literal split in-script so the gate's
  own grep cannot trip on the script blob.

## Push mechanics
- No gh CLI, no ~/.gitconfig, no ~/.netrc, no known_hosts; t389's askpass
  helper /tmp/t389_askpass.sh deleted after use per policy. Credentials
  status: (filled in below)
- Post-rewrite history DIVERGES from remote tip 5373c66+ => fast-forward is
  IMPOSSIBLE for the fixed export; the push is force-with-lease-or-nothing.
