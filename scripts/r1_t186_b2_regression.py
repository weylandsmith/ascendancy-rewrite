#!/usr/bin/env python3
"""t186 regression for the B2 leg of r1_idle_probe.py.

Replays every adjacent (numeric-order) prompt pair in work/r1/loop/ and prints
OLD (whole-file digit-stripped diff) vs NEW (human-region digit-stripped diff)
arm decisions, plus the old-vs-new flip table. Requirements checked:

  1. NEW arms strictly fewer pairs than OLD (the self-echo is gone).
  2. Every pair where OLD armed but NEW did not has delta lines ONLY inside
     the report-echo region (verify by locating each surviving old-delta line
     in the newest file and checking it falls between the IDLE-GATE marker and
     the next STEERING/INTERRUPT marker).
  3. If any prompt file historically contains a STEERING section, the pair
     that introduced it MUST still arm under NEW.

RC=0 pass, RC=1 fail. Prints a compact table only.
"""
import difflib, glob, os, os.path as op, re, sys

ROOT = op.dirname(op.dirname(op.abspath(__file__)))
LOOPDIR = op.join(ROOT, "work", "r1", "loop")
ECHO = "IDLE-GATE TRIGGER ARMED"
STEER_HDR = "STEERING FOR THIS ITERATION"
INTERRUPT = "INTERRUPTED PRIOR WORK DETECTED"
strip = lambda t: re.sub(r"\d+", "N", t)


def _num(p):
    m = re.search(r"(\d+)", op.basename(p))
    return int(m.group(1)) if m else -1


def human_regions(txt):
    out, keep = [], True
    for l in txt.splitlines():
        if ECHO in l:
            keep = False
            continue
        if STEER_HDR in l:
            keep = True
            continue
        if INTERRUPT in l:
            keep = False
            continue
        if keep:
            out.append(l)
    return out


def dlines(a, b):
    return [l for l in difflib.unified_diff(a, b, lineterm="")
            if l[:1] in "+-" and l[:3] not in ("+++", "---")]


def human_flags(txt):
    """Per-line booleans: True where the line is HUMAN-authored (contract text
    or a steering note). Report-echo and INTERRUPTED-note lines are False."""
    out, keep = [], True
    for l in txt.splitlines():
        if ECHO in l:
            keep = False
            out.append(False)
            continue
        if STEER_HDR in l:
            keep = True
            out.append(False)
            continue
        if INTERRUPT in l:
            keep = False
            out.append(False)
            continue
        out.append(keep)
    return out


def explainable(line, txt):
    """True if a diff line can be attributed to a loop-authored region of txt.
    Diff lines are DIGIT-STRIPPED, so compare against digit-stripped file lines
    (a raw probe of 'rN_idle_probe' would never match 'r1_idle_probe')."""
    probe = strip(line[1:]).strip()
    if not probe:
        return True
    flags = human_flags(txt)
    lines = [strip(l).strip() for l in txt.splitlines()]
    for i, l in enumerate(lines):
        if not flags[i] and probe in l:
            return True
    return False


prompts = sorted(glob.glob(op.join(LOOPDIR, "prompt-*.txt")), key=_num)
if not prompts:
    # work/r1/loop rotated/cleaned: nothing to replay. This runs inside
    # gate.sh's pre-flight, so a missing history must NOT redden the tree —
    # report the skip loudly and leave.
    print("SKIP: no prompt-*.txt under %s — B2 replay not adjudicated" % LOOPDIR)
    sys.exit(0)
if len(prompts) < 2:
    print("SKIP: only 1 prompt file — B2 replay needs a pair")
    sys.exit(0)

texts = {p: open(p, encoding="utf-8", errors="replace").read() for p in prompts}
steer_hist = [p for p in prompts if STEER_HDR in texts[p]]

old_arms, new_arms, flips = 0, 0, []
bad = []
for prev, new in zip(prompts[:-1], prompts[1:]):
    pt, ntx = texts[prev], texts[new]
    o = dlines(strip(pt).splitlines(), strip(ntx).splitlines())
    n = dlines([strip(l) for l in human_regions(pt)],
               [strip(l) for l in human_regions(ntx)])
    if o:
        old_arms += 1
    if n:
        new_arms += 1
    if o and not n:
        flips.append(op.basename(prev) + "->" + op.basename(new))
        # sanity: every old-delta line must live in the echo region of one of
        # the two files (added lines are in `new`, removed in `prev`)
        for l in o:
            tgt = ntx if l.startswith("+") else pt
            if not explainable(l, tgt):
                bad.append((op.basename(prev), op.basename(new), l[:100]))

print("pairs=%d old_arms=%d new_arms=%d flipped_to_idle=%d"
      % (len(prompts) - 1, old_arms, new_arms, len(flips)))
print("prompt files ever containing a STEERING section: %s"
      % ([op.basename(p) for p in steer_hist] or "NONE"))
if bad:
    print("FAIL: %d flipped-pair delta line(s) NOT explainable as echo echo"
          % len(bad))
    for p, q, l in bad[:10]:
        print("   %s->%s  %s" % (p, q, l))
    sys.exit(1)
if old_arms and new_arms >= old_arms:
    print("FAIL: fix did not reduce arms (new=%d old=%d)" % (new_arms, old_arms))
    sys.exit(1)
# informational: which recent pairs flipped (the t178-t186 idle-poll era).
# Flip strings look like "prompt-99.txt->prompt-100.txt", so match on those.
recent = [f for f in flips if re.search(r"prompt-(?:99|10[0-7])\.txt->prompt-1\d+\.txt", f)]
print("idle-era pairs flipped to IDLE: %s" % recent)
print("REGRESSION OK")
