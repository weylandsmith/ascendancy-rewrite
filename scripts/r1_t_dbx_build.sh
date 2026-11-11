#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# r1_t_dbx_build.sh — build a debugger-enabled dosbox-x (OQ-021 watchpoint
# instrument; see docs/re/dosbox-debugger.md for WHY and the operating rules).
#
# STATUS: STAGED, NEVER YET RUN (authored 2026-11-02; the user's build approval
# was requested and the question timed out — do not run without an explicit yes,
# the standing no-unapproved-fetch policy applies to apt-get source too).
#
# Route 1 (this script): rebuild the Debian source with debug+heavy.
#   Gives BPLM/BPPM/BPM memory-change watchpoints. No MCP control protocol
#   (master-only).
# Route 2 (not scripted): clone upstream master for watchpoints + MCP control.
#
# Guarantees this script must preserve when run:
#   - installs ONLY to work/r1/bin/ ; /usr/bin/dosbox-x is never touched
#     (production :9 + the launch harness assume it)
#   - build tree lives under work/ (gitignored); NEVER the repo root
#   - no capture, no game dir mount, no ring writes — pure compile
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
BT="$ROOT/work/r1/dbx-build"
BIN="$ROOT/work/r1/bin"
mkdir -p "$BT" "$BIN"

command -v dpkg-buildpackage >/dev/null || {
  echo "needs dpkg-dev (sudo apt-get install -y dpkg-dev build-essential) — STOP"; exit 2; }

cd "$BT"
[ -d dosbox-x-* ] || apt-get source dosbox-x || { echo "apt-get source failed"; exit 2; }
SRC="$(ls -d dosbox-x-*/ | head -1)"
[ -n "$SRC" ] || { echo "no source dir"; exit 2; }
cd "$SRC"

# Inject debug+heavy into the build. Debian uses dh/autoconf; patch configure
# invocation in debian/rules rather than the generated configure script.
if ! grep -q enable-debug debian/rules; then
  cp debian/rules debian/rules.orig
  # dh $@ style rules: add an override_dh_auto_configure target.
  if grep -qE "dh \$@|dh sequencer" debian/rules; then
    cat >> debian/rules <<'EOF'

override_dh_auto_configure:
	dh_auto_configure -- --enable-debug=heavy
EOF
  else
    sed -i 's|\./configure|./configure --enable-debug=heavy|' debian/rules
  fi
fi

# Build deps may still be missing; report rather than sudo-install silently.
if ! dpkg-buildpackage -us -uc -b > "$BT/build.log" 2>&1; then
  echo "BUILD FAILED — tail of $BT/build.log:"; tail -20 "$BT/build.log"; exit 1
fi

DEB="$(ls -t ../dosbox-x-dbgsym*.deb ../dosbox-x_*deb 2>/dev/null | head -1)"
[ -n "$DEB" ] || { echo "no .deb produced"; exit 1; }
cd "$BT" && ar x "$DEB"
if [ -f data.tar.* ]; then
  mkdir -p extract && tar xf "data.tar."* -C extract
  FOUND="$(find extract -type f -name dosbox-x | head -1)"
  [ -n "$FOUND" ] || { echo "binary not found in deb"; exit 1; }
  cp "$FOUND" "$BIN/dosbox-x-dbg"
  chmod +x "$BIN/dosbox-x-dbg"
  echo "INSTALLED: $BIN/dosbox-x-dbg"
  echo "-- verification (must show debugger strings the dfsg build lacks):"
  strings "$BIN/dosbox-x-dbg" | grep -icE "BPLM|BPPM|breakpoint" || true
  echo "-- then run HELP against the live build per README before use:"
  echo "   core=normal conf, scratch game copy, own ring dir (see docs/re/dosbox-debugger.md)"
else
  echo "no data.tar in deb"; exit 1
fi
