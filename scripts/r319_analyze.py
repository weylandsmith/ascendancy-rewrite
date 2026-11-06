#!/usr/bin/env python3
"""t319: analyse the pump caller/gate separation capture (offline).

Reads <run>/hits.json + <run>/probes.json, prints a SMALL census answering
the three-way question (docs/re/_wip_t319.md S0):
  (A) caller-never      : pump_entry stops exist but NONE with call-site
                          0x54ac5 (ret0_file_off == 0x54aca)
  (B) gate-never-equal  : p54a88 fires with edi != [core+0x24da4] (offline
                          read of the sav decides; here we print edi per stop)
  (C) pump-entry-never  : pump_entry zero whole-log (pty census)
Usage: r319_analyze.py <run-dir>
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

CALLERS = {  # return-address file offsets for the NINE E8 calls into fn
    # 0x56b5c (call site + 5; sites from the t318 amendment), msg id family.
    "0x53fa8": "0x53fa3 msg d", "0x5497b": "0x54976 msg 3",
    "0x54aca": "0x54ac5 msg 4|0xc POSTER", "0x54b3b": "0x54b36 msg 5",
    "0x55323": "0x5531e msg f", "0x55491": "0x5548c msg e",
    "0x55f87": "0x55f82 msg d", "0x56f14": "0x56f0f msg 2",
    "0x57008": "0x57003 msg 1",
}

def cs(h):
    rs = h.get("ret_stack", {})
    return rs.get("ret0_file_off")

print("\n== pump_entry_56b5c stops (entry of fn 0x56b5c) ==")
n = poster = 0
caller_ct = collections.Counter()
for h in hits:
    if h.get("leg") != "pump_entry_56b5c":
        continue
    n += 1
    r = h.get("regs", {})
    rs = h.get("ret_stack", {})
    c = cs(h)
    lbl = CALLERS.get(c, f"UNKNOWN cs={c}")
    caller_ct[lbl] += 1
    if "POSTER" in lbl:
        poster += 1
    print(f"#{n} {h.get('wall')} tag={h.get('tag')} edx(msg)={r.get('edx')} "
          f"esi={r.get('esi')} edi={r.get('edi')} eax={r.get('eax')} "
          f"ret0={rs.get('ret0')} cs={lbl} esp_p8={rs.get('esp_p8')}")
print(f"(pump_entry banked total {n}, POSTER-caller {poster})")
print("caller histogram:", dict(caller_ct))

print("\n== p54a47 stops (ds:0x484a4-EQUAL road) ==")
rows = [h for h in hits if h.get("leg") == "p54a47"]
for i, h in enumerate(rows[:20], 1):
    r = h.get("regs", {})
    print(f"#{i} {h.get('wall')} tag={h.get('tag')} edi={r.get('edi')} esi={r.get('esi')}")
print(f"(p54a47 banked total {len(rows)})")

print("\n== p54a88 stops (cmp edi,[esi+0x24da4]) ==")
rows = [h for h in hits if h.get("leg") == "p54a88"]
edi_ct = collections.Counter()
for i, h in enumerate(rows[:40], 1):
    r = h.get("regs", {})
    edi_ct[r.get("edi")] += 1
    print(f"#{i} {h.get('wall')} tag={h.get('tag')} edi(msg cand)={r.get('edi')} esi={r.get('esi')}")
print(f"(p54a88 banked total {len(rows)}); edi histogram: {dict(edi_ct)}")

print("\n== s2_56c74 (pump dispatch) / s2_56cda stops ==")
for leg in ("s2_56c74", "s2_56cda"):
    rows = [h for h in hits if h.get("leg") == leg]
    ed_ct = collections.Counter()
    for h in rows:
        r = h.get("regs", {})
        ed_ct[(r.get("edi") or r.get("edx"), h.get("wrec_eax", {}).get("name")
              or h.get("wrec_esi", {}).get("name"))] += 1
    print(f"{leg}: {len(rows)} by (msg,name): {dict(ed_ct)}")

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
