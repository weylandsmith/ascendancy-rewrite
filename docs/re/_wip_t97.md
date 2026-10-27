# t97 WIP (SO-name block consumer hunt)
- No new sitting (live-timeline mtime 2026-10-26 15:44 unchanged) -> t97 stands.
- (H) helper 0x2fb38 disasm: NOT an "R12 adjust" blob: takes EAX=src pool-rel-imm,
  EDX/format-varargs; adjusts EAX by code-obj base (returns adjusted src used by the
  following rep movsd at 0x1daf4: EDI stays [esp+0x10] from lea @0x1dae1, ESI=0x62b0
  staged, after call ESI = P0+0x88e60 == FILE 0x88e60). LAW: helper converts the
  staged pool-rel immediate to linear IN PLACE for the subsequent rep movsd copy.
  => the 200-B copy at 0x1dae5..0x1daf4 is a REAL copy of the SO block to [esp+0x10].
- 106 callers of 0x2fb38 (whole-string-relocation pattern = every string push zone).
- (I) 20-stride indexed census (imul *,*,0x14 / lea *0x14, obj0, 152831 insns):
  ONLY 6 sites: 0x22904, 0x22a60 (both = debug printf arg tables over esp frames,
  fmt strings 0xb42/0xb49 pool-rel -> NOT the SO block: they index esp+frame arrays)
  and 0x36fb8/0x36fe5/0x37027/0x3705a (context TBD, next probe). NO indexed read
  of a pool string base anywhere.
- ascend.exe is WATCOM LE (PE sig @0x2a50 is LE magic 'LE\0\0'): 32-bit LE with
  sections; debug info likely embedded (WATCOM string present). LE object names in
  the non-resident debug info could name the module owning the SO table DIRECTLY.
  NEXT: parse LE header objects (ObjectTable) + DBINFO records.
