#!/usr/bin/env python3
"""t318: analyse the broadcast-pump capture (offline).

Reads <run>/hits.json + <run>/session.log and prints a SMALL census:
  - per-leg stop counts
  - s2_56c74 stops: eax target rec + NAME (from wrec_* magic fields),
    msg word [esp+8] (banked esp_p8; fall back ret0 semantics), ebx/ecx
  - s2_56cda stops: edi (msg), eax NAME  (edi==0x1c01 = chain witness)
  - fn51cc4_entry stops: edx (msg id)
  - writer stops w43508_51fc2 / w43504_52003: eax (stored value)
  - any stop with 0x1c01 anywhere in regs/stack  -> the destination witness
Usage: r318_analyze.py <run-dir>
"""
import json, os, sys, collections

run = sys.argv[1]
hits = json.load(open(os.path.join(run, "hits.json")))
print(f"run={run} hits={len(hits)}")
by_leg = collections.Counter(h.get("leg") for h in hits)
print("per-leg:", dict(by_leg))

def name_of(h):
    names = []
    for k in ("wrec_eax", "wrec_esi", "wrec_ebp"):
        w = h.get(k)
        if w and w.get("magic_ok"):
            names.append(f"{k.split('_')[1]}={w.get('name')!r}")
    return " ".join(names)

print("\n== s2_56c74 (pump dispatch) stops ==")
n = 0
for h in hits:
    if h.get("leg") != "s2_56c74":
        continue
    n += 1
    rs = h.get("ret_stack", {})
    r = h.get("regs", {})
    print(f"#{n} {h.get('wall')} tag={h.get('tag')} eax={r.get('eax')} "
          f"msg[esp+8]={rs.get('esp_p8')} esp_p12={rs.get('esp_p12')} "
          f"ebx={r.get('ebx')} ecx={r.get('ecx')} ebp={r.get('ebp')} {name_of(h)}")
if not n:
    print("(none)")

print("\n== s2_56cda (fn 0x56ca4 call site) stops ==")
n = 0
for h in hits:
    if h.get("leg") != "s2_56cda":
        continue
    n += 1
    r = h.get("regs", {})
    if n <= 40 or r.get("edi") in ("0x1c01", "0x1c02"):
        print(f"#{n} {h.get('wall')} tag={h.get('tag')} edi={r.get('edi')} "
              f"edx={r.get('edx')} eax={r.get('eax')} {name_of(h)}")
if not n:
    print("(none)")
print(f"(s2_56cda total {by_leg.get('s2_56cda', 0)})")

print("\n== fn51cc4_entry (FLEETWND msg entry) stops ==")
n = 0
for h in hits:
    if h.get("leg") != "fn51cc4_entry":
        continue
    n += 1
    r = h.get("regs", {})
    print(f"#{n} {h.get('wall')} tag={h.get('tag')} edx={r.get('edx')} eax={r.get('eax')}")
if not n:
    print("(none)")

print("\n== writer stops ==")
for leg in ("w43508_51fc2", "w43504_52003"):
    rows = [h for h in hits if h.get("leg") == leg]
    print(f"{leg}: {len(rows)}", [(h.get('wall'), h.get('regs', {}).get('eax')) for h in rows[:10]])

print("\n== 0x1c01/0x1c02 anywhere witness ==")
found = 0
for h in hits:
    blob = json.dumps(h)
    if "0x1c01" in blob or "0x1c02" in blob:
        found += 1
        print(f"HIT {h.get('wall')} leg={h.get('leg')} tag={h.get('tag')}")
print(f"total {found}")

print("\n== per-phase leg coverage (tag -> legs) ==")
cov = collections.defaultdict(set)
for h in hits:
    cov[h.get("tag", "?").split("#")[0]].add(h.get("leg"))
for t, legs in sorted(cov.items()):
    print(f"  {t:28s} {sorted(l for l in legs if l)}")
