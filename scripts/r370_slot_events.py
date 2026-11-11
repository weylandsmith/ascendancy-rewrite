#!/usr/bin/env python3
"""t370 — per-slot ORDER-EVENT stream over the playtest window.

Why this exists: r369_order_diff tl mode can only build a destination vector
from type-3 inline triples (+0x6c) or a derefed type-1 payload (needs the
Memory image, unavailable in tl mode). The playtest ring banked AFTER the
session, so the interesting frames live only in live-timeline.jsonl, which
carries ship_raw (verbatim 177 u16 per slot, scripts/r1_playcap_watch.py:103).
This tool therefore reports RAW WORD EVENTS, not interpreted destinations:
for every consecutive deduped frame pair it prints which ship-record words
changed, decoded for the cited field map (docs/re/pership-spec.md §1):

  +0x34 name | +0x54 owner(race=>>16) | +0x58 ORDER KIND (low byte)
  +0x59 ORDER TARGET ptr | +0x5d ACT | +0x5e ACT TARGET
  +0x67 order TYPE | +0x68 order PAYLOAD ptr | +0x6c f32[3] kind-3 triple
  +0x88 u32 POWER | +0x8c u32 CHARGES | +0x9e f32[3] pos
  +0xab gizmo ring 25 slots stride 7 (cidx u8, u16 use, u32 arg)

No field meaning is invented here: only offsets and the cited decode.

OOM LAW: bounded tail-seek (default 200 MB), one json.loads per kept line.
Usage: r370_slot_events.py LO_NS [HI_NS|-1] [--slot N ...] [--grep word]
"""
import json
import os
import struct
import sys

JSONL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "work", "r1", "playcap", "live-timeline.jsonl")

# cited offsets (word index = byte offset / 2)
W_NAME = 0x34 // 2
W_OWNER = 0x54 // 2
W_KIND = 0x58            # byte 0x58 -> word 0x2C low byte
F_TRIP = 0x6c            # f32[3]
F_POS = 0x9e             # f32[3]


def fields(w):
    """Decode the cited fields of one 177-word ship record."""
    b = struct.pack("<%dH" % len(w), *w)
    d = {
        "kind": b[0x58],
        "kind_hi": b[0x59],
        "tgt": struct.unpack_from("<I", b, 0x59)[0],
        "act": b[0x5d],
        "atgt": struct.unpack_from("<I", b, 0x5e)[0],
        "type": b[0x67],
        "pay": struct.unpack_from("<I", b, 0x68)[0],
        "trip": tuple(round(v, 2) for v in struct.unpack_from("<3f", b, 0x6c)),
        "power": struct.unpack_from("<I", b, 0x88)[0],
        "charges": struct.unpack_from("<I", b, 0x8c)[0],
        "pos": tuple(round(v, 1) for v in struct.unpack_from("<3f", b, 0x9e)),
        "own": struct.unpack_from("<I", b, 0x54)[0] >> 16,
        "ring": {},
    }
    for i in range(min(struct.unpack_from("<I", b, 0x15a)[0] & 0xFFFF, 25)):
        c = b[0xab + 7 * i]
        if c != 0xFF:
            d["ring"][i] = (c, struct.unpack_from("<H", b, 0xab + 7 * i + 1)[0],
                            struct.unpack_from("<I", b, 0xab + 7 * i + 3)[0])
    try:
        d["name"] = b[0x34:0x34 + 20].split(b"\x00")[0].decode("latin-1")
    except Exception:
        d["name"] = "?"
    return d


def sig(d):
    return (d["kind"], d["kind_hi"], d["tgt"], d["act"], d["atgt"], d["type"],
            d["pay"], d["trip"], d["pos"], d["power"], d["charges"],
            tuple(sorted(d["ring"].items())))


def stream(lo_ns, hi_ns, seek=200_000_000):
    size = os.path.getsize(JSONL)
    seen, out = set(), []
    with open(JSONL, "r", errors="replace") as fh:
        fh.seek(max(0, size - seek))
        fh.readline()
        for line in fh:
            if not line.endswith("\n"):
                continue
            i = line.find('"file_mtime_ns": ')
            if i < 0:
                continue
            mt = int(line[i + 17:line.find(",", i)])
            if not (lo_ns <= mt <= (hi_ns if hi_ns and hi_ns > 0 else 1 << 62)):
                continue
            key = mt
            if key in seen:
                continue
            seen.add(key)
            if '"in_game": true' not in line:
                continue
            try:
                ob = json.loads(line)
            except Exception:
                continue
            if ob.get("turn", 0) <= 0 or not ob.get("ship_raw"):
                continue
            out.append((ob.get("wall", "?"), ob["turn"],
                        {int(k): w for k, w in ob["ship_raw"].items()}))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    slots = [int(a) for a in sys.argv[3:] if a.isdigit()]
    frames = stream(lo, hi)
    print(f"frames={len(frames)} wall {frames[0][0] if frames else '?'}"
          f" -> {frames[-1][0] if frames else '?'}")
    prev = None
    nev = 0
    for wall, turn, raw in frames:
        cur = {k: fields(w) for k, w in raw.items() if len(w) == 177}
        if prev is not None:
            for sl, d in sorted(cur.items()):
                if slots and sl not in slots:
                    continue
                pd = prev.get(sl)
                if pd is None:
                    continue
                s0, s1 = sig(pd), sig(d)
                if s0 == s1:
                    continue
                nev += 1
                ch = []
                if pd["pos"] != d["pos"]:
                    ch.append(f"pos {pd['pos']}->{d['pos']}")
                if pd["trip"] != d["trip"]:
                    ch.append(f"trip {pd['trip']}->{d['trip']}")
                if (pd["kind"], pd["kind_hi"]) != (d["kind"], d["kind_hi"]):
                    ch.append(f"kind {pd['kind']}/{hex(pd['kind_hi'])}->"
                              f"{d['kind']}/{hex(d['kind_hi'])}")
                if pd["tgt"] != d["tgt"]:
                    ch.append(f"tgt {hex(pd['tgt'])}->{hex(d['tgt'])}")
                if pd["type"] != d["type"]:
                    ch.append(f"type {pd['type']}->{d['type']}")
                if pd["pay"] != d["pay"]:
                    ch.append(f"pay {hex(pd['pay'])}->{hex(d['pay'])}")
                if pd["power"] != d["power"]:
                    ch.append(f"power {pd['power']}->{d['power']}")
                if pd["charges"] != d["charges"]:
                    ch.append(f"charges {pd['charges']}->{d['charges']}")
                if pd["ring"] != d["ring"]:
                    ch.append(f"ring {pd['ring']}->{d['ring']}")
                if pd["act"] != d["act"] or pd["atgt"] != d["atgt"]:
                    ch.append(f"act {pd['act']}/{hex(pd['atgt'])}->"
                              f"{d['act']}/{hex(d['atgt'])}")
                print(f"{wall} s{sl:<3} {d['name'][:12]:<12} own{d['own']} "
                      + " | ".join(ch))
        prev = cur
    print(f"events={nev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
