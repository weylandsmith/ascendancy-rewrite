#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# publish_public.sh — build a pushable public tree FROM A FRESH CLONE.
# Never run against the working repo: it rewrites ALL history.
#
# Excludes (user decision 2026-11-10 + t371 landmine notes):
#   game/ extracted/        vendor copyrighted distribution files
#   work/                   capture corpus + live session state (gitignored
#                           anyway; listed for defense-in-depth)
#   artifacts/ascend_restored.bin, artifacts/functions_full.tsv
#                           derivatives of the vendor EXE (t371
#                           PUBLISH-CONDITIONAL); regenerable:
#                           python3 scripts/r1_restore_sites.py + Ghidra
#                           headless (see docs/re/loader.md)
#   docs/assets|scratchpad/            ALL vendor-derived media (USER REMOVAL ORDER
#                           2026-11-12, extended same day from manual-jpg to
#                           the whole dir): 23 rasterised manual pages +
#                           decoded intro/logic movie frames + vendor font
#                           sheets + original-game screenshots (refcap).
#                           manual entered history at eb79da3 — filter must
#                           cover ALL commits, a tip delete is not enough.
#                           REGENERATE locally (own copy): scripts/flc_probe.
#                           py, fnt_probe.py, media_probe.py, refcap_gate.sh;
#                           gate stage 4f self-skips when pins absent.
#
# Usage: bash scripts/publish_public.sh <output-dir>
set -euo pipefail
OUT="${1:?usage: publish_public.sh <output-dir>}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"

[ -e "$OUT" ] && { echo "REFUSING: $OUT exists (fresh dir required)" >&2; exit 2; }

git clone -q "$SRC" "$OUT"
cd "$OUT"

# NOTE: do NOT pre-stage removals with `git rm --cached` — a dirty index makes
# filter-branch refuse ("Your index contains uncommitted changes"). The
# --index-filter below performs the removal per commit. (Verified 2026-11-11.)

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty \
    --index-filter 'git rm -r -q --cached --ignore-unmatch \
      game extracted work archive/user-saves docs/assets scratchpad \
      artifacts/ascend_restored.bin artifacts/functions_full.tsv' \
    --env-filter 'export GIT_AUTHOR_NAME="Weyland Smith" GIT_COMMITTER_NAME="Weyland Smith";
      if [ -n "${GITHUB_USER:-}" ]; then
        export GIT_AUTHOR_EMAIL="$GITHUB_USER@users.noreply.github.com" GIT_COMMITTER_EMAIL="$GITHUB_USER@users.noreply.github.com";
      fi' -- --all >/dev/null

# 1b. HISTORY SCRUB (t383; t396 GENERALIZED — see t396 notes below).
# Two passes over ALL tracked paths (SCRUB_PATHS empty = all files):
#  (P1) FULL personal-address form [REDACTED-EMAIL]*.[ISP] -> [REDACTED-EMAIL].
#       t383 scoped this to ONE path (docs/re/_license_draft_t372.md) and the
#       wip file docs/re/_wip_t383.md kept a historical blob with the full
#       address — MEASURED t396: 1 blob, present in the ALREADY-PUSHED
#       pubt391 tree too. Path-scoped privacy scrub is the bug; mask is
#       idempotent, so scope it wide.
#  (P2) BARE domain tokens (the ISP domain words, never used as contact info
#       in this repo — MEASURED t396: only gate-pattern citations in
#       STATE.md/packaging/publish_public.sh + the wip leak) -> [ISP-DOMAIN],
#       so the fail-closed gate below can exist at all. NOTE the domain
#       literals are SPLIT in-code ("ta"+"nagra", "digital"+"-oasis") so this
#       script's own blob never trips its own grep.
# PITFALLS (banked): this box's git filter-branch has NO --blob-filter (that
# belongs to git-filter-repo, not installed) — --tree-filter works; sed is
# now unscoped-by-default; the email class must eat the LOCAL PART too
# ([A-Za-z0-9._%+-]* before '@') — an earlier [[:space:][:punct]] class
# stopped at '@' and would have leaked the username.
P1="[A-Za-z0-9._%+-]*@ta""nagra[A-Za-z0-9.-]*"
P2="dig""ital-oasis|ta""nagra"
# grep -l first (text files only, NUL-safe), sed ONLY the files that actually
# contain a pattern — never rewrites binaries, never churns every file's bytes
# per commit (t383's single-path loop took 20 s; an unconditional
# find|xargs sed over ~570 commits would churn the whole tree every commit).
# t396b PITFALL (MEASURED in /tmp/tfmini): sed WITHOUT -E is BRE, where a bare
# `|` is a LITERAL — the P2 alternation matched nothing and the mask silently
# no-oped while the ERE gate (grep -aE) reported 100 hits. BOTH seds run -E.
TREE_SED="grep -rlZ -E '${P1}|${P2}' . --exclude-dir=.git 2>/dev/null | xargs -0 -r sed -i -E -e 's/${P1}/[REDACTED-EMAIL]/g' -e 's/${P2}/[ISP-DOMAIN]/g'; true;"
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --tree-filter "$TREE_SED" -- --all >/dev/null

# 1c. COMMIT-MESSAGE SCRUB (t396): the scan covers commit OBJECTS too
# (rev-list --objects lists them) and MEASURED 1 hit: commit c953fc8 (t383)
# carries the bare ISP domain IN ITS MESSAGE. A tree-filter never touches
# messages; --msg-filter does (same ERE sed, same -E law).
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter \
  "sed -E -e 's/${P1}/[REDACTED-EMAIL]/g' -e 's/${P2}/[ISP-DOMAIN]/g'" -- --all >/dev/null

# filter-branch keeps refs/original backups; without this the vendor blobs
# survive gc and the strip is cosmetic (VERIFIED 2026-11-11: 100M->9.7M).
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now -q

# ---- verification gates (fail closed) -------------------------------------
V=$(git rev-list --objects --all | grep -cE '^.* (game/|extracted/|work/|archive/user-saves/|docs/assets|scratchpad/|artifacts/ascend_restored\.bin)' || true)
[ "$V" = "0" ] || { echo "FAIL: $V vendor-path objects remain in history" >&2; exit 3; }
# t383 gate: NO blob in the rewritten history may contain the scrub pattern
# (batch cat-file; per-commit git grep over rev-list timed out at 300 s).
# t396 FIX — THE GATE WAS VACUOUS (MEASURED 2026-11-15): `xargs git cat-file
# --batch` appends the ids as ARGUMENTS and git dies "fatal: batch modes take
# no arguments"; with 2>/dev/null and `|| true` that produced a 0-byte scan
# file, so the pattern grep could never hit and exit 5 was unreachable.
# Batch mode reads ids from STDIN. Fail CLOSED on an empty/short scan file,
# plus a positive control proving the scan sees real blob content.
SCAN=/tmp/pubpush_blobscan.$$
SCAN_PATTERN="${SCAN_PATTERN:-dig""ital-oasis|ta""nagra}"
git rev-list --objects --all | cut -d' ' -f1 | sort -u | \
  git cat-file --batch 2>/dev/null > "$SCAN" || true
SCAN_BYTES=$(stat -c %s "$SCAN" 2>/dev/null || echo 0)
[ "$SCAN_BYTES" -gt 1000000 ] || { rm -f "$SCAN"; echo "FAIL(t396): blob scan vacuous — only $SCAN_BYTES bytes scanned (must be >1MB; a short scan means cat-file died)" >&2; exit 6; }
# Positive control (t396): a string that has been in THIS script's blob since
# inception MUST appear in the scan file itself — proves the scan holds real
# blob content, not just cat-file headers.
grep -aq "usage: publish_public.sh" "$SCAN" || { rm -f "$SCAN"; echo "FAIL(t396): positive control absent from scan — scan cannot see scripts/ blob content" >&2; exit 6; }
if grep -aE "$SCAN_PATTERN" "$SCAN" > /dev/null; then
    # NEVER print matching lines: the leak IS an address, and stdout of this
    # script lands in logs (t396 rule). Count only.
    HITS=$(grep -acE "$SCAN_PATTERN" "$SCAN")
    rm -f "$SCAN"
    echo "FAIL: scrub pattern still present ($HITS scan hits)" >&2; exit 5
fi
rm -f "$SCAN"
git checkout -q . 2>/dev/null || true
for keep in rewrite/src/game/campaign.cpp docs/re LICENSE NOTICE README.md; do
    [ -e "$keep" ] || { echo "FAIL: $keep missing from stripped tree" >&2; exit 4; }
done
echo "OK: vendor-free history, $(git rev-list --objects --all | wc -l) objects, $(du -sh .git | cut -f1) .git, tree intact."
echo "Next (USER-gated): git remote remove origin; git remote add origin <your-github-url>; git push -u origin main"
