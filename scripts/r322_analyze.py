#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t322: analyse the batcon two-click order-witness capture (offline).

Reads <run>/hits.json + census.json + probes.json + session.log, prints a
SMALL census answering the decision-tree question (docs/re/_wip_t322.md S4):
  (a) fn 0x1aef8 stops > 0  -> BatModeWnd DOES receive msgs in-view: learn the
      two-click choreography from the live [win+0xaf]/[+0xb3]/[+0xb7] grid +
      clip kind/obj per stop.
  (b) fn 0x1aef8 stops == 0 AND btn_hdlr alive -> composition-shielded: the
      blocker moves to window activation (offline probe next).
Also: store-leg fires (w43508_1b5e6 / w43508_1baa7) = WITNESSED DAT_43508
store (delta-only oracle law t297-A prints the before/after pairs).
Usage: r322_analyze.py <run-dir>
"""
import json, os, sys, collections

run = sys.argv[1]
hits = json.load(open(os.path.join(run, "hits.json")))
print(f"run={run} hits={len(hits)}")
by_leg = collections.Counter(h.get("leg") for h in hits)
print("per-leg (banked):", dict(by_leg))

try:
    probes = json.load(open(os.path.join(run, "probes.json")))
    for e in probes:
        if e.get("probe") == "pty-whole-log-census":
            print("pty-whole-log-census:", e.get("counts"))
except FileNotFoundError:
    print("(no probes.json)")

BAT_LEGS = ("batmode_dead", "fn1b91c_entry")
STORE_LEGS = ("w43508_1b5e6", "w43508_1baa7")

def grid(h):
    for k in ("win_from_eax", "win_from_esi", "win_from_ebp"):
        if k in h:
            return k, h[k]
    return None, None

print("\n== BATCON stops (entry legs) ==")
n = 0
for h in hits:
    if h.get("leg") not in BAT_LEGS:
        continue
    n += 1
    r = h.get("regs", {})
    rs = h.get("ret_stack", {})
    wk, w = grid(h)
    name = ""
    for k in ("wrec_eax", "wrec_esi", "wrec_ebp"):
        if h.get(k, {}).get("magic_ok"):
            name = h[k]["name"]
            break
    f = lambda o: (w or {}).get(f"+{hex(o)}")
    clip = h.get("clip", {})
    print(f"#{n} {h.get('wall')} tag={h.get('tag')} leg={h.get('leg')} "
          f"win={name!r}({wk}) ecx={r.get('ecx')} edx={r.get('edx')} "
          f"[+0xaf]={f(0xaf)} [+0xb3]={f(0xb3)} [+0xb7]={f(0xb7)} "
          f"[+0xbb]={f(0xbb)} ret0={rs.get('ret0_file_off')} "
          f"clip={ {k2: clip.get(k2) for k2 in ('kind','obj','ship_slot')} if clip else None}")
print(f"(batcon entry banked total {n})")

print("\n== STORE LEG stops (WITNESSED DAT_43508 writes) ==")
m = 0
for h in hits:
    if h.get("leg") not in STORE_LEGS:
        continue
    m += 1
    r = h.get("regs", {})
    rs = h.get("ret_stack", {})
    print(f"#{m} {h.get('wall')} tag={h.get('tag')} leg={h.get('leg')} "
          f"eax(stored value)={r.get('eax')} ret0={rs.get('ret0_file_off')}")
print(f"(store banked total {m})")

print("\n== other legs (control/context) ==")
for leg in sorted({h.get("leg") for h in hits} - set(BAT_LEGS) - set(STORE_LEGS)):
    rows = [h for h in hits if h.get("leg") == leg]
    ct = collections.Counter()
    for h in rows:
        name = ""
        for k in ("wrec_eax", "wrec_esi", "wrec_ebp"):
            if h.get(k, {}).get("magic_ok"):
                name = h[k]["name"]
                break
        ct[(h.get("regs", {}).get("edx"), name)] += 1
    print(f"  {leg}: {len(rows)} by (edx,name): {dict(ct)}")

print("\n== DAT oracle pairs (delta-only law t297-A) ==")
cen = None
try:
    cen = json.load(open(os.path.join(run, "census.json")))
    orc = cen.get("oracles", {})
    for tag in sorted(orc):
        o = orc[tag] or {}
        print(f"  {tag:24s} turn={o.get('turn')} sel43510={o.get('sel43510')} "
              f"DAT_43508={o.get('DAT_43508')} DAT_43504={o.get('DAT_43504')}"
              f"({o.get('DAT_43504_name')})")
except FileNotFoundError:
    print("(no census.json)")

print("\n== verdict ==")
pty = (cen.get("pty") or {}) if cen else {}
if not pty:
    try:
        for e in json.load(open(os.path.join(run, "probes.json"))):
            if e.get("probe") == "pty-whole-log-census":
                pty = e.get("counts", {})
    except FileNotFoundError:
        pty = {}
entry_pty = pty.get("batmode_dead", 0)
ctl_alive = by_leg.get("btn_hdlr", 0) > 0 or pty.get("btn_hdlr", 0) > 0
if m:
    print("STORE WITNESSED — close the OQ-019 select leg on this evidence")
elif n or entry_pty:
    print(f"(a) BatModeWnd RECEIVES msgs in-view (banked {n}, pty {entry_pty}) "
          "— choreography readable from grids above")
elif ctl_alive:
    print("(b) entry zero whole-log, control alive — COMPOSITION-SHIELDED, "
          "blocker = window activation")
else:
    print("CONTROL DEAD — instrument invalid, run not attributable")
