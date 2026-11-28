#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tCITE-AUDIT: check every code-address citation in durable docs/re/*.md
against instruction boundaries in work/ascend_restored.bin.

Boundary set = per-function decode from ghp5 starts (work/functions_full.tsv),
each function decoded for its own [start, start+size) with 1-byte fallback on
undecodable bytes. A cited addr inside the obj0 code span [0x14bb0,0x82bb0)
(pointer law OQ-011 CLOSED) that is NOT a boundary is a CANDIDATE.

Candidates are pre-sorted by shape of the surrounding prose so a human can
adjudicate in one pass:
  RANGE-EDGE  : token is the start/end of an `0x.. .. 0x..` range (range ends
                are exclusive/derived, not instruction sites — usually fine)
  DATA-SHAPE  : token sits in ds:/DAT_/+off/[..] idiom (a RAM/data address that
                coincidentally lands in the code byte-range, or a struct offset
                arithmetic — usually fine)
  CODE-SHAPE  : prose names a code-role word right before the address
                (fn/handler/call/site/site/caller/loop/branch/...) — THESE are
                the defect candidates: either mid-instruction citations or
                ghp5 function-map gaps.
  OTHER       : everything else — needs eyeballing.

Writes /tmp/tcite_cands.json (all candidates with pre/post context) and prints
counts + the CODE-SHAPE list. Exit 0 always (audit, not gate).
"""
import os, re, json
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = "/home/hrethric/projects/ascendancy"
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

data = open(os.path.join(ROOT, "work/ascend_restored.bin"), "rb").read()
funcs = []
with open(os.path.join(ROOT, "work/functions_full.tsv")) as f:
    f.readline()
    for line in f:
        p = line.split("\t")
        if len(p) >= 2:
            try:
                funcs.append((int(p[0], 16), int(p[1], 16)))
            except ValueError:
                pass

md = Cs(CS_ARCH_X86, CS_MODE_32)
bounds = set()
for s, sz in funcs:
    end = min(s + sz, len(data))
    a = s
    while a < end:
        bounds.add(a)
        got = False
        for ins in md.disasm(data[a:min(end, a + 16)], a):
            if ins.address != a:
                break
            a = ins.address + ins.size
            got = True
            break
        if not got:
            a += 1
print(f"funcs={len(funcs)} boundaries={len(bounds)}")

ROLE = re.compile(r"(fn|fun_?\d*|fun$|call|callee|caller|handler|entry|dispatch|writer|reader|site|block|loop|leg|arm|router|comparator|evaluator|resolver|pump|switcher|code|jmp|tail|trampoline|anchor|branch|gate|chain|path|body|hook|thunk|stub|start|ends|end|begins|begin|at|in|via|from|to|inside|inside of|reaches|first|first-call|scan)\s*[:=]?\s*[,.;)]?\s*$", re.I)
tok = re.compile(r"0x([0-9a-fA-F]{3,8})")
skip = {"_wip_", "_draft_", "_license_", "_notice_", "_readme_"}
docs = sorted(d for d in os.listdir(os.path.join(ROOT, "docs/re"))
              if d.endswith(".md") and not any(k in d for k in skip))

cands = []
total = 0
for d in docs:
    with open(os.path.join(ROOT, "docs/re", d), encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            for m in tok.finditer(line):
                v = int(m.group(1), 16)
                if not (CODE_LO <= v < CODE_HI):
                    continue
                total += 1
                if v in bounds:
                    continue
                pre = line[:m.start()]
                post = line[m.end():]
                if re.search(r"\.\.\s*$", pre) or post.startswith(".."):
                    kind = "RANGE-EDGE"
                elif re.search(r"(ds\s*:|DAT_)\s*$", pre) or post.startswith("+") or pre.rstrip().endswith("+") or pre.rstrip().endswith("["):
                    kind = "DATA-SHAPE"
                elif "ds:" in pre or "DAT_" in pre or re.search(r"\+\s*0x[0-9a-f]+\s*\]", post):
                    kind = "DATA-SHAPE"
                elif ROLE.search(pre):
                    kind = "CODE-SHAPE"
                else:
                    kind = "OTHER"
                cands.append({"doc": d, "line": i, "addr": hex(v), "kind": kind,
                              "pre": pre[-60:], "post": post[:60]})
json.dump(cands, open("/tmp/tcite_cands.json", "w"), indent=1)
from collections import Counter
print(f"code_span_tokens={total} candidates={len(cands)}")
print(Counter(c["kind"] for c in cands))
print("=== CODE-SHAPE candidates (defect candidates) ===")
seen = set()
for c in cands:
    if c["kind"] == "CODE-SHAPE":
        key = (c["doc"], c["addr"])
        if key in seen:
            continue
        seen.add(key)
        print(f"{c['doc']}:{c['line']} {c['addr']} | ...{c['pre']} << {c['post']}...")
