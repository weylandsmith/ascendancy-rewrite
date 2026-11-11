#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t97d: enumerate ALL computed-jump tables (ff 24 9d disp32 = jmp [ebx*4+d])
in obj0 with a decode-boundary-aware filter (disassemble window, keep sites
whose insn actually decodes at that offset), then for the tables whose
handler bodies cluster in the batmode display module (0x1c000..0x1f000)
dump the entries. The 0x8c90 table (kind->status templates) is known-good
(t96). Question: is there a SECOND table keyed by order kind/act whose
bodies reference the SO block or index 20-stride names? RC=0 always."""
import re, subprocess

D = open('/home/hrethric/projects/ascendancy/work/ascend_restored.bin', 'rb').read()
CODE = (0x14bb0, 0x82bb0)

def disasm_window(s, e):
    r = subprocess.run(['objdump', '-D', '-b', 'binary', '-m', 'i386', '-M', 'intel',
                        f'--start-address=0x{s:x}', f'--stop-address=0x{e:x}',
                        '/home/hrethric/projects/ascendancy/work/ascend_restored.bin'],
                       capture_output=True, text=True)
    out = []
    for ln in r.stdout.splitlines():
        m = re.match(r'\s+([0-9a-f]+):\t(?:[0-9a-f]{2} )+\t?(.*)$', ln)
        if m: out.append((int(m.group(1), 16), m.group(2).strip()))
    return out

cands = []
i = CODE[0]
while True:
    j = D.find(b'\xff\x24\x9d', i)
    if j < 0 or j >= CODE[1]: break
    cands.append(j); i = j + 1
# also ff 24 85 (jmp [eax*4+d]), ff 24 8d (ecx*4), ff 24 95 (edx*4)
for sib in (b'\xff\x24\x85', b'\xff\x24\x8d', b'\xff\x24\x95'):
    i = CODE[0]
    while True:
        j = D.find(sib, i)
        if j < 0 or j >= CODE[1]: break
        cands.append(j); i = j + 1
cands.sort()
print('raw ff24?? candidates:', len(cands))

tables = []
for c in cands:
    disp = int.from_bytes(D[c+3:c+7], 'little')
    # verify decode boundary: disasm small window ending after c; ensure an insn starts at c
    win = disasm_window(max(c-8, CODE[0]), c+8)
    starts = {a for a, t in win}
    if c in starts:
        insn = [t for a, t in win if a == c][0]
        tables.append((c, disp, insn))
print('decode-verified jmp-table sites:')
for c, disp, insn in tables:
    print(' ', hex(c), 'table disp32', hex(disp), '|', insn)

# dump entries for tables plausibly in the display/batmode zone (site 0x1c000..0x23000)
print('--- entry dumps for batmode-zone tables ---')
# t96 trap: jmp disp32 is code-object INTRA (FILE = disp + 0x14bb0), not raw.
for c, disp, insn in tables:
    if not (0x1c000 <= c <= 0x23000): continue
    for base, tag in ((0x14bb0, 'code-obj'), (0x82bb0, 'data-obj'), (0, 'raw')):
        F = disp + base
        if F + 40 > len(D): continue
        ents = [int.from_bytes(D[F+4*k: F+4*k+4], 'little') for k in range(10)]
        plausible = sum(1 for e in ents if CODE[0] <= e < CODE[1])
        print('site', hex(c), tag, 'table F', hex(F), [hex(e) for e in ents[:8]], 'plausible', plausible)
print('RC 0')
