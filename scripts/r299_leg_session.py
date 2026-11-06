#!/usr/bin/env python3
"""t299 — DEBUGGER LEG WITNESS: does a mouse click reach the batmode SELECT /
ORDER legs, and with what operands (OQ-016 r1, OQ-019 r1/r3).

INSTRUMENT SEMANTICS (read from work/r1/dbx-build/dosbox-x-master THIS session;
see docs/re/_wip_t299.md S1/S4 — all [verified in-tree]):
  * work/r1/bin/dosbox-x-dbg (--enable-debug=heavy). MCP DIRECTION LAW (t282):
    the emulator dials US -> bind the listener before spawn.
  * BREAK needs a pty (debug.cpp:5410 isatty x3) + a long settle, and is a
    per-attempt LOTTERY (t286 law 2) -> wrap in a relaunch loop.
  * CODE breakpoints under C_HEAVY_DEBUG write NO 0xCC (the INT-3 patch block
    is inside `#if !C_HEAVY_DEBUG`, debug.cpp:720) and are evaluated at the TOP
    of the instruction loop (core_normal.cpp:182 -> DEBUG_HeavyIsBreakpoint
    debug.cpp:6665 -> CheckBreakpoint :819, matching
    `bp->GetLocation() == GetAddress(cs, reg_eip)`). Passing the SAME selector
    as CS makes the match independent of what SegBase(cs) actually is.
  * reg_eip holds the GUEST-LINEAR code address (t286b: fire EIP 0x1f231f ==
    payload file 0x32ecf + P0 0x1bf450) => arm `BP <CS>:<P0 + file_offset>`;
    the stop lands AT the leg's first instruction, so registers show ENTRY
    state (batcon entry: eax=win, ecx=modifier, edx=pending clip).
  * ACTIVATION LAW (measured in debug_mcp.cpp:559 + debug.cpp:762): AddBreakpoint
    does NOT Activate(); only RUN/RUNWATCH call ActivateBreakpoints(). An
    `EXEC BP` issued while the guest RUNS is therefore inert. CONSEQUENCE: arm
    ALL legs once while stopped at the title, RUN once, and attribute every stop
    by its EIP. (The "one bp at a time" rule is a BPLM-fire-line rule; code
    bps report CS:EIP correctly.)

LEGS (t301 SUPERSEDED SET — window-class dispatch law, docs/re/_wip_t301.md
S4/S6; the old batmode legs below are DEAD for system-view clicks — BatModeWnd
is INACTIVE there and its class table 0x2478e8 is never consulted):
  cosmos_router 0x30d08  THE generic dispatcher: prologue 51 56 57 55; callers
                         do `mov ecx,[win+0xa7]; call [ecx+4]` (verified sites
                         img+0x26eda, img+0x30d02; zero E8 callsites — reached
                         ONLY through the per-class table slot 1)
  cosmos_entry  0x26818  COSMOSWnd class-entry (table slot 0) 53 51 56 57 89 c3
                         89 d1 f6 c1 04; its own installer `mov [eax+0xa7],
                         0x247a4c` at img+0x2683f (static imm 0x5a4c -> +P0 in
                         RAM)
  cosmos_hdlr   0x26b34  COSMOSWnd msg handler (table slot 2, mirrors the dead
                         batmode slot-2 shape 56 57 55 83 ec 3c)
  cosmos_27e80  0x27e80  table slot 3 (53 51 56 57 55 81 ec e4 00)
  cosmos_2925c  0x2925c  table slot 5 (51 56 57 55 81 ec 94 01)
  batcon        0x1b91c  [DEAD-IN-VIEW, keep armed as controls] entry eax=win
  deselect      0x1b114  [DEAD-IN-VIEW]
Shared slots 1/4 of every class table are 0x30d08/0x1f0608 — arming
0x30d08 witnesses EVERY class dispatch including the FLEET/NEXTTURN type-0
button clicks (those executed and were never armed in t299-t301).

DRIVE (r298.Sess inherited, client-rect-bounded finders): enter campaign ->
End Turn ONCE -> FLEET -> row y in (93,200,305,410). Row->ship mapping is NOT
array order (t298 refutation), so SHIP IDENTITY IS READ FROM THE CLIP at the
stop (edx -> {kind,obj} -> ship slot via the PHYSICAL value law member =
value + 0x88), never inferred from the row position.

SAFETY: scratch game-wp ONLY (asserted, never game/); OWN ring dir (two-writer
law); private Xvfb (never :9); core=normal; -time-limit; kill-by-recorded-PID;
Oct-29 md5-verified RESUME.GAM; production :9 untouched.

usage: r299_leg_session.py [--disp 97] [--port 55999] [--tl 1800]
                           [--legs batcon,select,...] [--views 4]
Exit 0 = at least one leg witnessed with operand state banked.
     1 = honest negative (no fire / BREAK lottery lost / base mismatch).
     2 = harness error.
"""
import argparse
import hashlib
import json
import os
import os.path as op
import pty
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.dirname(op.abspath(__file__)))
import r1_slot as SL                                          # noqa: E402
import r293_move_session as R293                              # noqa: E402
import r298_order_session as R298                             # noqa: E402

DBG_BIN = op.join(ROOT, "work/r1/bin/dosbox-x-dbg")
EXPECT_BASE = 0x1BF4D8      # deterministic base: t286b 4 sightings + t297 + t298
P0 = EXPECT_BASE - 0x88
CODE_END = P0 + 0x8CC83     # obj1 image end (pointer law, OQ-011)
FLEET_BTN = (553, 184)
FLEET_ROWS = (93, 200, 305, 410)


HL_STOP = "\x1b[30m\x1b[42m"   # PAIR_BLACK_GREEN = DrawCode stop-line highlight
                               # (debug.cpp:1586-87, source-read t305)


class FirePat:
    """t305 FIRE-PATTERN LAW (docs/re/_wip_t305.md S1, source + 3-run verified).
    A stop fires DrawCode; ncurses emits ONLY the CHANGED CELLS of the cursor
    line, prefixed by the PAIR_BLACK_GREEN highlight HL_STOP (its use in
    debug.cpp is exclusive to that line). The address token right after HL is
    EITHER the full '0160:0021612A' OR a SUFFIX of the 6-hex linear address
    whose length depends on what the previous screen render had at those cells:
    0x21612A -> '1612A', 0x2160C4 -> '60C4', 0x1E5F84 -> '1E5F84'. A regex per
    fixed form cannot cover this (leading zeros are STRIPPED, not present for
    0* to consume), so: regex captures the token and CODE checks
    sig6.endswith(token) with len(token) >= 4 (last-4 is unique across the
    whole leg set incl. the 24-leg census set — audited t305; tokens shorter
    than 4 are ambiguous and are NOT counted, a documented undercount risk).
    Bare (no-color) fallback = the t302 6-hex law, with a lookbehind that
    excludes renders already counted via HL. Attribution is ALWAYS EV-eip-exact
    (bank_stop); this is only a 'something stopped' trigger + census counter.
    VERIFIED vs real logs: 033648 cos_hdlr 41; 052925 s2_56cda 3; 061825
    cos_hdlr 60, s2_56cda 20, s2_56c74 1 (the '60C4' render a fixed-5 pattern
    misses)."""
    _RE = re.compile(re.escape(HL_STOP)
                     + r"((?:[0-9A-Fa-f]{4}:)?[0-9A-F]{4,8}) [0-9A-F]")
    _RE_BARE_T = r"(?<![0-9A-Fa-f]){} [0-9A-F]"

    def __init__(self, lin):
        self.sig6 = f"{lin & 0xFFFFFF:06X}"
        self.re_bare = re.compile(self._RE_BARE_T.format(self.sig6))

    def findall(self, text):
        hits = []
        hl_spans = [m.span() for m in
                    re.finditer(re.escape(HL_STOP), text)]
        for m in self._RE.finditer(text):
            tok = m.group(1).split(":")[-1].lstrip("0") or "0"
            if len(tok) >= 4 and self.sig6.endswith(tok):
                hits.append(m.group(1))
        # Bare (no-color) fallback = the t302 law. A token is EXCLUDED if an HL
        # marker START sits 1..16 bytes before it (HL is 9 bytes; full-form
        # render adds 'CS:' = 5 more -> token at start+14; a genuine bare token
        # is preceded by non-ANSI junk). Two counters mutually exclusive.
        bare = [m.group(0) for m in self.re_bare.finditer(text)
                if not any(1 <= m.start() - s <= 16
                           for s, _e in hl_spans)]
        return hits + bare

    def search(self, text):
        return bool(self.findall(text))


def fire_pats(lin):
    """Compatibility shim: one FirePat per leg (search/findall API)."""
    return [FirePat(lin)]


LEGS = {"router": 0x30D08,     # GENERIC msg dispatcher (shared table slot 1 of
                                      # EVERY class incl. type-0 FLEET/NEXTTURN);
                                      # reached via mov ecx,[win+0xa7]; call [ecx+4]
        "cos_entry": 0x26818,   # COSMOSWnd class-entry (table phys 0x247a4c slot 0)
        "cos_hdlr": 0x26B34,    # COSMOSWnd msg handler (slot 2)
        "cos_s3": 0x27E80,      # COSMOS table slot 3
        "cos_s5": 0x2925C,      # COSMOS table slot 5
        "btn_entry": 0x30AD8,   # type-0 button class-entry (FLEET/NEXTTURN table
                                      # phys 0x247cb8 slot 0) — the clicks that
                                      # WORKED never had this armed
        "btn_hdlr": 0x336B4,    # type-0 button handler (slot 2)
        "batmode_dead": 0x1AEF8,  # BatModeWnd msg-handler ENTRY (t299 zero-fires
                                      # were DYN-core: entry is block-top but the
                                      # t302 fire-pattern was dyn-blind; t306
                                      # RE-ARMS under normal core + FirePat)
        # t306 SELECTION-EFFECT LEGS (ships.md S24 static law, do NOT re-derive;
        # mid-block instructions — CAN fire under normal core, could NOT under
        # dynrec: core_dynrec.cpp:268 heavy-BP only at run-loop top):
        #   0x1b71f = c6 85 b7 00 00 00 02  mov BYTE [ebp+0xb7],2  (msg-0x53
        #     leg: G2 kind==2 / G3 owner / G4 moves>0 all passed; at stop
        #     ebp=BatModeWnd record (magic+NAME), eax=ship record phys)
        #   0x1ba39 = c6 86 b7 00 00 00 02  mov BYTE [esi+0xb7],2  (mouse msg-4
        #     leg via router 0x1b070 -> 0x1b91c; at stop esi=BatModeWnd record,
        #     eax=ship record, ebp=0xffffffff (bank_stop magic-guards it))
        "bat_s53": 0x1B71F,
        "bat_mouse": 0x1BA39,
        # msg-4 router INSIDE the BatModeWnd family (ships.md S24: "MOUSE
        # ROUTE IS MSG 4 (0x1b070)"). t299 run-4 armed it but under DYN core
        # (unreliable per t305 REFUTED amendment) — t306 re-arms under normal.
        # entry-fires-without-effects = gate rejected; nothing-fires = msg
        # layer never reached by map clicks.
        "bat_router": 0x1B070,
        # t303 CENSUS legs: the FIVE `call [ecx+4]` dispatch sites (ff 51 04
        # occurs EXACTLY 5x in the payload — verified this session vs t301
        # S6.1). Stopping at the SITE (before the call) keeps the caller's
        # window-record reg live: 0x26eda/0x30d02 are preceded by
        # `mov ecx,[eax+0xa7]` (8b 88 a7 00 00 00) so eax = window record.
        "disp_26eda": 0x26EDA,
        "disp_30d02": 0x30D02,
        "disp_7a7eb": 0x7A7EB,
        "disp_7aa3e": 0x7AA3E,
        "disp_7b020": 0x7B020,
        # t304 SLOT-2 CALL SITES: cos_hdlr/btn_hdlr are class-table SLOT 2
        # (+0x8). STATIC (docs/re/_wip_t304.md S1): `call [ecx+8]` does NOT
        # EXIST in the payload (zero sites) — the slot-2 call is always
        # ff /2 mod=01 disp8=08 through esi (13x), edi (2x), ebx (1x), each
        # preceded by a class-table load `mov r32,[r32+0xa7]` (or, at 0x809fe,
        # a global object-table index). t303 armed only slot-1 ff5104 sites,
        # which is why cos_hdlr fired 15x "unwitnessed". These 16 are the
        # candidate callers; the whole-log pty census names the one(s) that
        # actually fire. Lead: 0x15b0f (msg id via `sar ebx,0x18` = generic).
        # t304 STATIC RE-VERIFY (whole-image ff/2 decode, not a mod=01 grep):
        # 22 slot-2 sites total. The 6 below are the DISP32 form the WIP scan
        # missed: `8b a8 a7 00 00 00` mov r32,[r32+0xa7] (disp32) then ff 55 08
        # call [ebp+8]; 0x26c43/0x27082 sit INSIDE cos_hdlr's span, 0x333ef/
        # 0x3340c inside the button-handler span -> handler-to-handler chains.
        "s2_26c43": 0x26C43, "s2_27082": 0x27082, "s2_31550": 0x31550,
        "s2_333ef": 0x333EF, "s2_3340c": 0x3340C, "s2_56c74": 0x56C74,
        "s2_15b0f": 0x15B0F, "s2_356a5": 0x356A5, "s2_3afc3": 0x3AFC3,
        "s2_3b38b": 0x3B38B, "s2_3b3a9": 0x3B3A9, "s2_3b4e9": 0x3B4E9,
        "s2_3b584": 0x3B584, "s2_3b5be": 0x3B5BE, "s2_3b607": 0x3B607,
        "s2_553cb": 0x553CB, "s2_553e5": 0x553E5, "s2_55406": 0x55406,
        "s2_56cda": 0x56CDA, "s2_809fe": 0x809FE, "s2_4e2cb": 0x4E2CB,
        "s2_54a83": 0x54A83,
        # t307 SELECTION/ORDER-WRITER LEGS — the non-batmode members of the
        # t296 store census (ships.md S24/S32; REFUTED-ROUTES t306 amendment
        # keeps the four batmode sites DEAD). EVERY byte verified this session
        # vs work/ascend_payload.bin + t91_code_disasm.txt; the signature is
        # the store itself `a3 04/08 35 04 00 = mov ds:0x435XX,eax`, so eax at
        # the stop IS the stored value (star_name_at(eax) names a star record
        # per T298-A when eax is a star pointer). Follow-on ring posts
        # (0x56ad4, code 0x10/0x11) sit 5-15 bytes downstream at 6 of 8.
        "w43504_28ec2": 0x28EC2,   # cosmos family (disasm 23094; ebx=0x10)
        "w43504_28ef6": 0x28ef6,   # cosmos family, eax=[[..]] (23111)
        "w43504_36b01": 0x36B01,   # diplomacy row, eax=[ebx+0x13000] (40724)
        "w43504_52003": 0x52003,   # ship order-target, eax=[esi+0x59] (73824)
        "w43504_55d35": 0x55D35,   # gate cmp [esp+8],1 at 0x55d25 (78663)
        "w43508_51a8e": 0x51A8E,   # turn-gated ds:0x484ec>0x96, ring 0x11
        "w43508_51fc2": 0x51FC2,   # eax=[edx+0x59], ring 0x11 (73808)
        "w43508_55bbd": 0x55BBD,   # edi=0x11 leg into 0x55d6f (78564)
        # t309 TWO-RING MAP (docs/re/_wip_t309.md S1.8/S1.11 — the t308
        # 'star click posts ring 0x10' reading CONFLATED THE TWO RINGS:
        # 0x28ed8 posts RING-A {code=edx=1, param=ebx=0x10}; the DAT-writing
        # consumer dispatches on the CODE field of RING-B). Bytes verified
        # this session vs work/ascend_payload.bin:
        "cons_entry": 0x55AE8,      # RING-B CONSUMER fn entry (53 51 52 56
                                    # 57 55 83ec10; sole E8 caller = pump site
                                    # 0x54b74 in main-loop fn 0x54650; gates
                                    # ds:0x7a358!=-1, count [core+0x4758]>>16
                                    # !=0, mode [core+0x4226]>>16==1)
        "ringB_post": 0x55A60,      # RING-B POST fn entry (56 57 89d6 89df;
                                    # 19 E8 sites, codes 1..0x19) — any ring-B
                                    # activity at all is a fire here
        "ringB_w10_41c17": 0x41C17, # ring-B code-0x10 post #1 (edx=0x10,
                                    # ebx=esi, ecx=[esi+0x5e]) fn 0x41260
        "ringB_w10_499e0": 0x499E0, # ring-B code-0x10 post #2, same shape,
                                    # fn 0x49880 — the ONLY two 0x10 posters
        "ringA_resolver": 0x55DF4,  # RING-A shadow-copy+resolver fn entry
                                    # (called from 0x54b4a gated ([core+
                                    # 0x44aa]>>16)>0; jmp-table 0x55e86 on
                                    # code<=8) — POSITIVE CONTROL: the star
                                    # ENTER posts ring-A code 1, so a fire
                                    # here after the click proves the pump
                                    # ran while armed
        # t310 (docs/re/_wip_t310.md S1b): fn 0x51834 is a msg PRE-DISPATCHER
        # (dx=msg id): <2 -> 0x51AF3, ==2 -> 0x51A2A, ==0x1c01 -> 0x51A67
        # (the DESTINATION path: gate ds:0x484ec>0x96 -> DAT_43508=eax + ring-A
        # 0x11 at 0x51A8E; else star-addr k=0x13bc5+k*96 -> DAT_43504 + ring-A
        # 0x10 at 0x51AC9), default -> TAIL-CALL btn_hdlr 0x336b4. The ONLY
        # senders of msg 0x1c01 in the image (cmp-family + mov edx,0x1c01
        # census, both 0 other forms):
        "w51ac9": 0x51AC9,          # DAT_43504=edx star-record addr store,
                                    # bytes 89 15 04 35 04 00 (payload-verified
                                    # t310); gate ds:0x484ec<=0x96 branch
        "s2_1616f": 0x1616F,        # RELAY site: mov edx,0x1c01 at 0x16168,
                                    # call [ebx+0xc] at 0x1616f (bytes verified
                                    # ff 53 0c); eax=ebp=window rec — a stop
                                    # HERE = msg-0x1c01 WAS sent (fn 0x160xx).
                                    # (Relay site #2 = s2_356a5, already in the
                                    # t304 set at its line above — digit-key
                                    # gated 0x30..0x39, NOT in this legset.)
        # t311 STATUSWND MSG-ENTRY LEG (docs/re/_wip_t311.md S1; class grid
        # RAM 0x248040 slot 4 named 'STATUSWND' per t310 S5). ENTRY of fn
        # 0x51834 fires for EVERY msg delivered to the class; dx = msg id,
        # ret0 = the dispatch site, magic window rec names the window. This
        # leg separates 'class never messaged' from '0x1c01 never sent' — the
        # t310 store legs alone could not. Entry bytes verified this session
        # vs work/ascend_payload.bin: 56 57 55 83 ec 0c 89 c5 66 89 54 24.
        "fn51834_entry": 0x51834,
        # t319 PUMP CALLER/GATE SEPARATION LEGS (docs/re/_wip_t319.md S1;
        # REFUTED-ROUTES t318 amendment (3) shape spec). Bytes verified this
        # session vs work/ascend_payload.bin:
        #   pump_entry_56b5c = fn 0x56b5c ENTRY (56 57 55 83 ec 10 89 c7 66 89
        #     54 24 08). At the stop: edx=msg id, esi=core obj (eax=esi only
        #     past 0x56b63), ret0 = which of the NINE E8 callers fired
        #     (0x53fa3 d / 0x54976 3 / 0x54ac5 4|0xc / 0x54b36 5 / 0x5531e f /
        #     0x5548c e / 0x55f82 d / 0x56f0f 2 / 0x57003 1; call site =
        #     ret0_file_off-5 for E8).
        #   p54a47 = 8b 1d f0 84 04 00, first insn of the ds:0x484a4-EQUAL road
        #     (only reached past cmp edi,ds:0x484a4 @0x54a3f jne 0x54a88).
        #   p54a88 = 3b be a4 4d 02 00, the cmp edi,[esi+0x24da4]. At the stop
        #     edi=msg id candidate, esi=core obj; equal AND [esi+0x489e]==0 ->
        #     msg 0xc poster, else msg 4 — both fall into call 0x56b5c @0x54ac5.
        #     Static NOTE (t91_code_disasm 77184-77215): the only in-function
        #     entry to 0x54a3f is je@0x549e7 ([esi+0x24da8]==-1) arriving with
        #     [esi+0x489e]==0, so on THAT path the discriminating datum is
        #     edi vs [core+0x24da4], not +0x489e.
        "pump_entry_56b5c": 0x56B5C,
        "p54a47": 0x54A47,
        "p54a88": 0x54A88,
        # t322 BATCON CLICK-ROAD LEGS — the two DAT_43508 stores that were
        # NEVER ARMED in ANY capture t307..t321 (REFUTED-ROUTES t321 amendment
        # (3): the whole "writer zero" negative series never tested the mouse
        # road). Bytes verified this session vs work/ascend_payload.bin:
        #   w43508_1b5e6 = a3 08 35 04 00 (mov ds:0x43508,eax) inside fn 0x1aef8
        #     (BatModeWnd msg handler), the msg-0x50 publish leg (t296 S4).
        #   w43508_1baa7 = a3 08 35 04 00, same store inside fn 0x1b91c @0x1baa7
        #     = THE per-ship destination/selection store (t296 S5 / t321 S4:
        #     kind-1 clip, ch==[win+0xb7]==0, clicked-obj == [win+0xb3] stored).
        #   fn1b91c_entry = 56 57 55 89 c6 83 b8 af 00 00 00 00 (push esi/edi/
        #     ebp; mov esi,eax; cmp DWORD [eax+0xaf],0). At the stop eax=esi=
        #     BatModeWnd record (bank_stop magic-dumps its +0x90..+0xcf grid =
        #     the recorder-first [win+0xaf]/[+0xb3]/[+0xb7] reads); ecx=1 from
        #     router 0x1b0cc / 0 from 0x1b1de; edx=clip ptr (bank_stop clip
        #     block reads kind=u8[[edx]] + obj=u32[[edx]+1]).
        "w43508_1b5e6": 0x1B5E6,
        "w43508_1baa7": 0x1BAA7,
        "fn1b91c_entry": 0x1B91C,
        # t314 FLEETWND MSG-HANDLER ENTRY LEG (docs/re/_wip_t314.md S1; class
        # named FLEETWND t313 S5 via magic rec 0xfe7a90, cp 0x247fa8). Entry of
        # fn 0x51cc4 (vtable slot 2 of FLEETWND) fires for EVERY msg delivered
        # to the FLEET window; prologue `66 89 94 24 b4 01 00 00` = mov
        # [esp+0x1b4],dx so edx AT THE STOP is the msg id; ret0 names the
        # dispatch site. Own 0x1c01 path: je@0x51cfa -> 0x51f3b -> state table
        # (RAM 0x211188) -> writer blocks {0x51fb5 DAT_43508, 0x51ff6
        # DAT_43504}. Entry bytes verified this session vs
        # work/ascend_payload.bin: 56 57 55 81 ec bc 01 00 00 89 c7 66 89 94 24.
        "fn51cc4_entry": 0x51CC4}

EVENTS = []
hx = lambda v: hex(v) if isinstance(v, int) else None


# ---------------- MCP plumbing (r1_wp_session.py proven form) ----------------
def read_until_end(f, end_marker, budget):
    lines, header = [], None
    t0 = time.time()
    while time.time() - t0 < budget:
        try:
            raw = f.readline()
        except (socket.timeout, OSError):
            continue
        if not raw:
            return lines, False, header
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if line == end_marker:
            return lines, True, header
        if line.startswith("BEGIN event"):
            ev, _, _ = read_until_end(f, "END event", 2.0)
            EVENTS.extend(ev)
            continue
        if line.startswith("BEGIN "):
            header = line
            continue
        if line:
            lines.append(line)
    return lines, True, header


def drain(master_fd, path):
    with open(path, "wb") as fh:
        while True:
            try:
                data = os.read(master_fd, 65536)
            except OSError:
                return
            if not data:
                return
            fh.write(data)
            fh.flush()


class Sess(R298.Sess):
    """r298 drive class + debugger control."""

    def __init__(self, args):
        super().__init__(args)
        self.out = op.join(ROOT, "work/r1",
                           f"t299-leg-{time.strftime('%Y%m%d-%H%M%S')}")
        os.makedirs(op.join(self.out, "save"), exist_ok=True)
        self.savedir = op.join(self.out, "save")
        self.logp = op.join(self.out, "session.log")
        self.dbl = op.join(self.out, "dosbox.out")
        self.ptylog = op.join(self.out, "mcp-pty.log")
        self.transcript = op.join(self.out, "mcp-transcript.txt")
        self.pty_off = 0
        self.hits = []
        self.probes = []
        self.csseg = 0x160
        self.leg_lines = {}
        self.legs = list(LEGS)   # armed set (main overwrites); used by
                                 # resume_and_rearm
        self.witnessed = set()   # legs banked once: DROP after first witness
                                 # (t302 law: msg 0x3b pump re-fires cos/router
                                 # legs on every resume; keeping them armed
                                 # floods stops and starves the click battery)
        self.census = False      # t303: main() sets True in census mode —
        self.pulse_clicks = 0    # t320: extra Button1 pulses per armed window
        self.pulse_xy = None     # t320: set per-window by census_click
                                 # re-arm ALL legs per stop (every msg id is
                                 # data) and run choreography LEG-FREE

    # ---------- launch (dbg build, pty stdio, MCP out-dial) ----------
    def launch(self):
        shutil.copy2(R293.OCT29, op.join(R293.SCRATCH, "RESUME.GAM"))
        low = op.join(R293.SCRATCH, "resume.gam")
        if op.exists(low):
            os.rename(low, low + ".vendor-t299")
        conf = op.join(self.out, "session.conf")
        with open(conf, "w") as fh:
            fh.write(f"""[dosbox]
machine=svga_s3
memsize=16
[cpu]
core=normal
[dosbox]
mcp_server={self.a.port}
captures={self.out}/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C {R293.SCRATCH}
C:
ASCEND.EXE
""")
        self.xv = subprocess.Popen(
            ["Xvfb", self.disp, "-screen", "0", "800x600x24"],
            stdout=open(op.join(self.out, "xvfb.out"), "wb"),
            stderr=subprocess.STDOUT)
        time.sleep(1.5)
        self.ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ls.bind(("127.0.0.1", self.a.port))
        self.ls.listen(1)
        self.ls.settimeout(2.0)
        master, slave = pty.openpty()
        threading.Thread(target=drain, args=(master, self.ptylog),
                         daemon=True).start()
        env = dict(os.environ, DISPLAY=self.disp, TERM="xterm")
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env.pop(k, None)
        self.child = subprocess.Popen(
            [DBG_BIN, "-conf", conf, "-nogui", "-savedir", self.savedir,
             "-time-limit", str(self.a.tl)],
            stdin=slave, stdout=slave, stderr=slave, cwd=self.out, env=env,
            close_fds=True)
        os.close(slave)
        self.log(f"spawned dosbox-x-dbg pid={self.child.pid} "
                 f"display={self.disp} out={self.out} tl={self.a.tl}")

    def connect(self):
        t0 = time.time()
        while time.time() - t0 < self.a.boot:
            try:
                conn, addr = self.ls.accept()
                self.log(f"MCP connected OUT from {addr} "
                         f"after {time.time()-t0:.1f}s")
                conn.settimeout(0.5)
                self.mf = conn.makefile("rwb")
                self.seq = [0]
                return conn
            except socket.timeout:
                if self.child.poll() is not None:
                    self.log(f"child exited early rc={self.child.returncode}")
                    return None
        return None

    def req(self, verb, budget=30.0):
        self.seq[0] += 1
        rid = str(self.seq[0])
        try:
            self.mf.write(f"REQ {rid} {verb}\n".encode())
            self.mf.flush()
        except OSError as e:
            self.log(f"channel dead ({e}) at {verb!r}")
            return [], False, None
        lines, ok, hdr = read_until_end(self.mf, f"END {rid}", budget)
        with open(self.transcript, "a") as fh:
            fh.write(f"REQ {rid} {verb}\nHDR {hdr}\n")
            for l in lines:
                fh.write("  " + l + "\n")
            fh.flush()
        return lines, ok, hdr

    # ---------- persistence ----------
    def persist(self):
        with open(op.join(self.out, "hits.json"), "w") as fh:
            json.dump(self.hits, fh, indent=1)
        with open(op.join(self.out, "probes.json"), "w") as fh:
            json.dump(self.probes, fh, indent=1)

    # ---------- debugger control ----------
    def pty_new(self):
        try:
            with open(self.ptylog, "rb") as fh:
                fh.seek(self.pty_off)
                data = fh.read()
                self.pty_off = fh.tell()
        except OSError:
            return ""
        return data.decode("utf-8", "replace")

    def pty_peek(self):
        """Same as pty_new but does NOT advance pty_off (t303: liveness checks
        must not swallow a stop's code-view line — t302 S4 law)."""
        try:
            with open(self.ptylog, "rb") as fh:
                fh.seek(self.pty_off)
                data = fh.read()
        except OSError:
            return ""
        return data.decode("utf-8", "replace")

    def read_reg(self, name):
        """EXEC EV <reg> -> int, or None if unanswered. Response shape is
        MEASURED (t286 stopped-state.txt): ['EV of 'EIP' is:', '1f231f']."""
        lines, ok, hdr = self.req(f"EXEC EV {name}", 10.0)
        if hdr is None:
            return None
        for l in reversed(lines):
            s = l.strip()
            if not s or s.lower().startswith("ev of"):
                continue
            try:
                return int(s, 16)
            except ValueError:
                return None
        return None

    def do_break(self):
        for attempt in range(3):
            lines, ok, hdr = self.req("BREAK", 60.0)
            self.log(f"BREAK#{attempt} hdr={hdr} frame_ok={ok} "
                     f"lines={lines[:3]}")
            if hdr is not None and not hdr.rstrip().endswith("ERR"):
                chk, _, h2 = self.req("EXEC BPLIST", 15.0)
                self.log(f"post-BREAK BPLIST hdr={h2} lines={chk}")
                if h2 is not None:
                    return True
            lines, ok, _ = self.req("PING", 15.0)
            if "PONG" not in " ".join(lines):
                self.log(f"BREAK#{attempt}: channel dead (no PONG) — lottery "
                         f"LOST, relaunch")
                return False
            time.sleep(10.0)
        return False

    def arm_all(self, legs):
        """Arm every leg while STOPPED; BPLIST must list exactly len(legs).
        Also precompiles the pty fire-detection patterns (self.leg_pats) from
        the SAME values, so poll_stop can never see a type mismatch."""
        self.req("EXEC BPDEL *", 15.0)
        self.leg_lines = {}
        self.leg_pats = []
        ok_all = True
        for name in legs:
            lin = P0 + LEGS[name]
            self.leg_lines[name] = f"{self.csseg:04X}:{lin:08X}"
            # t302 FIX: the MEASURED fire line on this build is the DrawCode
            # render "1E5F84 56 push esi..." — 6-hex EIP (no CS prefix, no
            # 8-digit padding), opcode-hex glued to the mnemonic, run-on lines
            # ("push esi1E5F85 57 ..."). The old full-form pattern
            # 0160:001E5F84 NEVER matched -> attempt t302-1 banked a real stop
            # (cos_hdlr) as NOFIRE and let the game freeze at the BP. Pattern:
            # 6-hex leg EIP NOT preceded by a hex char, then space + >=1 hex
            # (kills "Set breakpoint at 0160:1F0158" and BPLIST lines: they end
            # at the address; kills REQ-echo full forms 001F0158: the 6-hex run
            # there is preceded by '0').
            # t302 pattern kept + t305 NORMAL-CORE 5-hex pattern (fire_pats:
            # normal core renders '1612A FF5608', the 6-hex form never appears).
            self.leg_pats.extend(fire_pats(lin))
            lines, ok, hdr = self.req(f"EXEC BP {self.csseg:04X}:{lin:08X}",
                                      15.0)
            self.log(f"ARM {name:9s} {self.leg_lines[name]} hdr={hdr} "
                     f"lines={lines}")
            if hdr is None or hdr.rstrip().endswith("ERR"):
                ok_all = False
        lines, ok, hdr = self.req("EXEC BPLIST", 15.0)
        listed = [l for l in lines if re.search(r"BP\s+[0-9A-Fa-f]{4}:", l)]
        self.log(f"BPLIST {len(listed)} entries: {listed}")
        return ok_all and len(listed) == len(legs)

    def dump_mem(self, addr, n, tag):
        """Binary dump of guest memory at LINEAR==PHYSICAL `addr`.
        PARSING LAWS (source this session): the command line runs through
        GetHexValue's expression parser, so (a) a '/' in the FILENAME is
        division -> whole command rejected 'Invalid memory dump arguments'
        (attempt-1 measured) — filenames MUST be bare relative names; the
        emulator's cwd is the run dir (launch cwd=self.out); (b) the length is
        parsed as HEX. Addressing: MEMREAD is real-mode-only (debug.cpp:2984)
        and `0000:` hits LinMakeProt's selector<8 rejection (debug.cpp:460),
        so the usable selector mid-game is CS (paging off, EIP carries the full
        linear). Try CS: first, fall back to 0000:."""
        fname = f"mem_{tag}_{addr:08x}".replace("/", "-") + ".bin"
        # ParseCommand uppercases the ENTIRE line including the filename
        # (debug.cpp:2197-2198 `for (auto &c : copy_str) c = toupper(c)`), so
        # the emulator writes MEM_TAG_....BIN while Python asked for lowercase.
        # t299 attempt-2 proved this (MEM_CONTROL_001DAD6C.BIN appeared).
        out_f = op.join(self.out, fname.upper())
        for seg in (self.csseg,):
            lines, ok, hdr = self.req(
                f"EXEC MEMDUMPBIN {seg:04X}:{addr:08X} {n:X} {fname}", 20.0)
            if op.exists(out_f):
                return open(out_f, "rb").read()
            if hdr is not None:
                self.log(f"MEMDUMPBIN {hex(addr)} no file hdr={hdr} "
                         f"lines={lines}")
        return None

    def attribute(self, eip):
        for name, lin in self.leg_lines.items():
            if eip == P0 + LEGS[name]:
                return name
        return None

    def bank_stop(self, tag):
        """Bank registers + window block + clip for the CURRENT stop, then RUN."""
        rec = {"tag": tag, "wall": time.strftime("%H:%M:%S")}
        regs = {}
        for r in ("eip", "eax", "ebx", "ecx", "edx", "esi", "edi", "ebp",
                  "esp"):
            v = self.read_reg(r)
            regs[r] = v
            if v is None:
                self.log(f"STOP {tag}: EV {r} unanswered — bank partial")
                break
        ip16 = self.read_reg("IP")   # 16-bit mirror: cross-check for the P0 law
        rec["regs"] = {k: hx(v) for k, v in regs.items() if v is not None}
        rec["ip16"] = hx(ip16)
        eip = regs.get("eip")
        rec["leg"] = self.attribute(eip) if eip else None
        rec["eip_file_off"] = hx(eip - P0) if eip and eip > P0 else None
        # t304 CALLER WITNESS: t303 REFUTED the slot-1 router law (cos_hdlr
        # fired 15x with all five ff5104 sites armed+silent). The return
        # address at [esp] at a handler stop names the TRUE dispatch caller
        # verbatim. Dump 8 bytes at esp; ret0 = [esp] (call pushed it).
        esp = regs.get("esp")
        if esp and 0x1000 < esp < 0x10000000:
            # t318 EXTENSION: dump 16 bytes (was 8). The broadcast-pump
            # dispatch s2_56c74 carries msg = [esp+8] AT THE CALL INSTRUCTION
            # (return addr not yet pushed), so an 8-byte window CANNOT see it.
            # esp_p8/esp_p12 are the raw words at [esp+8]/[esp+12]; ret0/ret1
            # semantics unchanged.
            eb = self.dump_mem(esp, 16, f"{tag}_esp")
            if eb and len(eb) >= 8:
                r0, r1 = struct.unpack_from("<II", eb, 0)
                rec["ret_stack"] = {"esp": hx(esp), "ret0": hx(r0),
                                    "ret1": hx(r1),
                                    "esp_p8": hx(struct.unpack_from("<I", eb, 8)[0]) if len(eb) >= 12 else None,
                                    "esp_p12": hx(struct.unpack_from("<I", eb, 12)[0]) if len(eb) >= 16 else None,
                                    # t304 GUARD FIX: bound must be the image
                                    # END (P0+size), not the size — comparing
                                    # linear vs 0x8CC83 rejected every real
                                    # ret0 (logged file=None at 03:38:55).
                                    "ret0_file_off": (hx((r0 & 0xFFFFFF) - P0)
                                                      if P0 <= (r0 & 0xFFFFFF) < CODE_END else None),
                                    "ret0_call_site": (hx((r0 & 0xFFFFFF) - P0 - 3)
                                                       if P0 <= (r0 & 0xFFFFFF) < CODE_END else None)}
                self.log(f"STOP {tag} ret0={hx(r0)} "
                         f"file={rec['ret_stack']['ret0_file_off']}")
        self.log(f"STOP {tag} leg={rec['leg']} eip={hx(eip)} "
                 f"file={rec['eip_file_off']} "
                 f"eax={hx(regs.get('eax'))} ecx={hx(regs.get('ecx'))} "
                 f"edx={hx(regs.get('edx'))} ebp={hx(regs.get('ebp'))}")
        # window block covering the leg fields: +0xa4 clip, +0xac pending-clip-2,
        # +0xb4 mode, +0xbc pending kind (u32 grid aligned down from 0x90).
        # t302 FIX: dump the head of EVERY candidate reg (magic-check each) —
        # at cos_hdlr stops esi=CLASS TABLE (no magic), eax=WINDOW RECORD
        # (magic + NAME@+0x20); the old break-on-first-blob never named the
        # window. The magic-bearing reg gets the +0x90 field grid.
        magic_w = None
        for wkey in ("esi", "eax", "ebp"):
            w = regs.get(wkey)
            if not (w and P0 < w < 0x10000000):
                continue
            head = self.dump_mem(w, 48, f"{tag}_{wkey}_head")
            if head and len(head) >= 48:
                magic = struct.unpack_from("<I", head, 0)[0]
                nm = head[0x20:0x2c].split(b"\x00")[0].decode("latin1", "replace")
                rec[f"wrec_{wkey}"] = {"magic_ok": magic == 0x12345678,
                                       "name": nm}
                if magic == 0x12345678:
                    magic_w = (wkey, w)
            if magic_w and magic_w[0] == wkey:
                break
        wsrc = magic_w if magic_w else (("esi", regs.get("esi"))
                                        if regs.get("esi") else None)
        if wsrc:
            wkey, w = wsrc
            blob = self.dump_mem(w + 0x90, 64, f"{tag}_{wkey}")
            if blob and len(blob) >= 0x40:
                g = lambda o: struct.unpack_from("<I", blob, o - 0x90)[0]
                rec[f"win_from_{wkey}"] = {
                    "win": hx(w), **{f"+{o:#x}": hx(g(o))
                                     for o in range(0x90, 0xD0, 4)}}
                self.log(f"STOP {tag} win[{wkey}] name="
                         f"{rec.get(f'wrec_{wkey}', {}).get('name')!r} "
                         f"{rec[f'win_from_{wkey}']}")
        # pending clip from the hit-test: edx at batcon entry, [[clip]]=object
        clip = regs.get("edx")
        if clip and P0 < clip < 0x10000000:
            blob = self.dump_mem(clip, 16, f"{tag}_clip")
            if blob and len(blob) >= 8:
                kind = blob[0]
                obj = struct.unpack_from("<I", blob, 1)[0]
                rec["clip"] = {"ptr": hx(clip), "kind": kind, "obj": hx(obj),
                               "ship_slot": None}
                # t303 CENSUS: the .sav scan per stop is the expensive part;
                # a census banks dozens of stops — msg-id+name is the data.
                if not self.census:
                    try:
                        p = self.newest_sav()
                        mem = self.read_mem(p) if p else None
                        B = SL.base_of(mem, self.anch) if mem else None
                        if B:
                            base, n = SL.ship_array_law(mem, B)
                            for k in range(n):
                                r = base + k * SL.SHIP["stride"]
                                if r == obj + 0x88:
                                    rec["clip"]["ship_slot"] = k
                                    rec["clip_ship"] = dict(
                                        slot=k,
                                        owner=struct.unpack_from("<I", mem,
                                                                 r + 0x54)[0] >> 16,
                                        kind=mem[r + 0x58],
                                        moves=struct.unpack_from("<H", mem,
                                                                 r + 0x94)[0])
                                    break
                    except Exception as e:
                        rec["clip_ship_error"] = repr(e)[:120]
                self.log(f"STOP {tag} clip={rec['clip']}")
        self.hits.append(rec)
        with open(op.join(self.out, "hits.json"), "w") as fh:
            json.dump(self.hits, fh, indent=1)
        self.resume_and_rearm(rec.get("leg"))
        return rec

    def bp_index_of(self, lin):
        """Index of the armed code-BP whose offset matches lin (BPLIST prints
        'NN. BP 0160:1DA348' — 6-hex, GetAddress-evaluated)."""
        lines, ok, hdr = self.req("EXEC BPLIST", 15.0)
        if hdr is None:
            return None
        for l in lines:
            m = re.match(r"\s*(\d+)\.\s+BP\s+([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4,8})", l)
            if m and (int(m.group(3), 16) & 0xFFFFFF) == (lin & 0xFFFFFF):
                return int(m.group(1))
        return None

    def resume_and_rearm(self, fired):
        """t302 LAW (source-pinned, docs/re/_wip_t302.md S3): a code BP under
        C_HEAVY_DEBUG is NOT 0xCC-patched and NOT once-only, and the
        heavy-check runs at the TOP of the core loop (core_normal.cpp:182) —
        resuming with the FIRED bp still armed re-stops at the same EIP on the
        very next dispatch (msg 0x3b is periodic), freezing the guest (measured
        t302-1/-2: '(Running)' ACK then debugger prompt, autosave cadence dead).
        Protocol: BPDEL the fired index -> RUN -> PROVE liveness by autosave
        growth -> BREAK (stopped re-arm window) -> re-arm all legs -> RUN."""
        t_res = time.time()
        if fired:
            idx = self.bp_index_of(P0 + LEGS[fired])
            if idx is not None:
                lines, ok, hdr = self.req(f"EXEC BPDEL {idx:X}", 10.0)
                self.log(f"BPDEL {fired} idx={idx} hdr={hdr} lines={lines}")
            else:
                self.log(f"BPDEL {fired}: index not found in BPLIST")
            if not self.census:   # t303: census mode re-arms EVERY leg every
                self.witnessed.add(fired)   # stop — every msg id is data
        lines, ok, hdr = self.req("EXEC RUN", 20.0)
        self.log(f"resume RUN hdr={hdr} lines={lines}")
        alive = False
        while time.time() - t_res < 40:
            try:
                mt = max((os.path.getmtime(op.join(self.savedir, f))
                          for f in os.listdir(self.savedir)
                          if f.endswith(".sav")), default=0.0)
            except OSError:
                mt = 0.0
            if mt > t_res + 1:
                alive = True
                break
            # t303 CENSUS: on a HOT leg set (0x3b pump ~1/s) the guest RE-FIRES
            # within ~2 s of RUN — long before the autosave cadence. A pending
            # fire line PROVES the guest ran (and it must be banked by
            # poll_stop, not mistaken for a freeze).
            if self.census:
                txt = self.pty_peek()
                if txt and self.leg_pats and any(p.search(txt)
                                                 for p in self.leg_pats):
                    self.log("resume liveness via RE-FIRE (hot census leg; "
                             "line PEEKED not consumed — poll_stop banks it)")
                    alive = True
                    break
            time.sleep(2.0)
        self.probes.append({"probe": "resume-liveness", "alive": alive,
                            "fired": fired})
        self.log(f"resume liveness={alive} (autosave growth within 40s)")
        if not alive:
            return False
        time.sleep(1.0)
        if not self.do_break():
            self.probes.append({"probe": "rearm-break", "ok": False})
            self.log("REARM: BREAK lost — legs stay DELETED, continuing "
                     "leg-free (guest alive)")
            return True
        # t302 LAW: re-arm only UN-witnessed legs. The msg-0x3b pump re-fires
        # router/cos_hdlr every ~1-2 s; re-arming a witnessed hot leg just
        # re-freezes the guest on the next RUN and starves the click battery.
        legs = [l for l in getattr(self, "legs", list(LEGS))
                if l not in self.witnessed]
        if not legs:
            self.log("rearm: all legs witnessed — staying leg-free, guest "
                     "runs clean for the battery")
            lines, ok, hdr = self.req("EXEC RUN", 20.0)
            self.log(f"leg-free RUN hdr={hdr}")
            return True
        okc = self.arm_all(legs)
        self.log(f"re-armed {len(legs)} legs ok={okc}")
        lines, ok, hdr = self.req("EXEC RUN", 20.0)
        self.log(f"rearm RUN hdr={hdr}")
        # t302 S4 LAW: do NOT pty_new() here — a HOT leg (one that catches the
        # periodic msg 0x3b pump: router slot1, cos_hdlr slot2) re-stops within
        # ~1-2 s of the rearm RUN and pty_new SWALLOWS that stop's code view
        # (attempt 3: guest frozen at 1E5F84 through the whole press loop).
        # poll_stop banks it (recursion depth-capped).
        self._rr_depth = getattr(self, "_rr_depth", 0) + 1
        try:
            if self._rr_depth <= 3:
                self.poll_stop("post-rearm", budget=8.0)
            else:
                self.log("post-rearm: recursion cap hit, RUN stays clean")
        finally:
            self._rr_depth -= 1
        return True

    def poll_stop(self, tag, budget=20.0):
        """Scan the pty for an armed leg's code-view line; bank EVERY stop that
        follows the trigger (a click can walk several legs: batcon -> select ->
        relay) until the pty goes quiet. MEASURED pty format (t286 runs):
        '0160:00214141 8B35...' — CS:%04X and the linear EIP as %08X. Patterns
        are precompiled in arm_all (leg_lines holds display STRINGS — formatting
        them with :08X was attempt-1's crash)."""
        pats = self.leg_pats
        t0 = time.time()
        recs = []
        while time.time() - t0 < budget:
            txt = self.pty_new()
            if txt and any(p.search(txt) for p in pats):
                self.log(f"FIRE-CANDIDATE {tag} after {time.time()-t0:.1f}s")
                time.sleep(1.5)
                self.pty_new()
                recs.append(self.bank_stop(tag))
                # chain: give the game a beat, then check for a second stop
                time.sleep(1.0)
                txt2 = self.pty_new()
                if txt2 and any(p.search(txt2) for p in pats):
                    self.log(f"CHAIN fire {tag}")
                    time.sleep(1.5)
                    self.pty_new()
                    recs.append(self.bank_stop(tag + "+chain"))
                    continue
                return recs
            time.sleep(1.0)
        return recs or None

    def check_stopped_oracle(self, tag):
        """If EXEC answered-while-running was NEGATIVE (probe), a responding
        EXEC eip means the guest is STOPPED — recovers chain stops the pty scan
        may have consumed. No-op when the oracle is invalid."""
        if getattr(self, "exec_free", True):
            return None
        e = self.read_reg("eip")
        if e is not None and self.attribute(e):
            self.log(f"ORACLE {tag}: EXEC answered mid-run and EIP is leg "
                     f"{self.attribute(e)} — banking the missed stop")
            return [self.bank_stop(tag + "_oracle")]
        return None

    # ---------- t303 CENSUS machinery ----------
    def arm_census(self, legs):
        """BREAK -> pmode arm-time gate -> arm_all. Up to 3 tries (GetAddress
        is evaluated AT ARM TIME — arming under the wrong mode bakes a wrong
        location, t299 law 2). On failure the guest is left RUNNING leg-free
        (BPDEL * ran inside arm_all only after a stop was won; if BREAK was
        lost nothing was armed)."""
        for att in range(3):
            if att:
                r = self.req("EXEC RUN", 15.0)
                self.log(f"census-arm {att}: RUN hdr={r[2]}")
                time.sleep(4.0)
            if not self.do_break():
                self.log(f"census-arm {att}: BREAK lottery lost")
                continue
            cs = self.read_reg("cs")
            eip0 = self.read_reg("eip")
            self.log(f"census-arm {att}: cs={hx(cs)} eip={hx(eip0)}")
            if not (cs and eip0 and P0 <= eip0 < CODE_END):
                continue
            self.csseg = cs
            if self.arm_all(legs):
                # MEMDUMPBIN control vs payload bytes at the FIRST leg (P0 law
                # + dump path in one shot; honest log either way)
                if getattr(self, "pay", None):
                    first = legs[0]
                    ctl = self.dump_mem(P0 + LEGS[first], 16, "ctl_census")
                    if ctl:
                        want = self.pay[LEGS[first]:LEGS[first] + 16]
                        self.log(f"census control MATCH={ctl == want}")
                        self.probes.append({"probe": "census-ctl",
                                            "match": ctl == want})
                self.probes.append({"probe": "census-arm", "ok": True,
                                    "att": att})
                return True
        self.probes.append({"probe": "census-arm", "ok": False})
        # FAILURE PATH SAFETY (t302 law): arm_all may have armed SOME legs
        # before the BPLIST gate failed, with the guest STOPPED — a bare RUN
        # would re-freeze on the 0x3b pump. BPDEL * (EXEC answers even while
        # running) then RUN (no-op if already running).
        self.req("EXEC BPDEL *", 15.0)
        self.req("EXEC RUN", 15.0)
        return False

    def disarm_run(self, tag):
        """End a census window: BREAK (whatever state), BPDEL *, BPLIST-empty
        confirm, RUN, liveness by autosave growth. The guest MUST end the
        choreography leg-free and alive (t302 freeze laws)."""
        self.do_break()
        lines, ok, hdr = self.req("EXEC BPDEL *", 15.0)
        lines2, ok2, hdr2 = self.req("EXEC BPLIST", 15.0)
        listed = [l for l in lines2
                  if re.search(r"BP\s+[0-9A-Fa-f]{4}:", l)]
        self.log(f"DISARM {tag}: BPDEL hdr={hdr} BPLIST left={len(listed)}")
        lines, ok, hdr = self.req("EXEC RUN", 20.0)
        t_res = time.time()
        alive = False
        while time.time() - t_res < 60:
            try:
                mt = max((os.path.getmtime(op.join(self.savedir, f))
                          for f in os.listdir(self.savedir)
                          if f.endswith(".sav")), default=0.0)
            except OSError:
                mt = 0.0
            if mt > t_res + 1:
                alive = True
                break
            time.sleep(2.0)
        self.probes.append({"probe": "disarm-liveness", "tag": tag,
                            "alive": alive, "bplists_left": len(listed)})
        self.log(f"DISARM {tag} liveness={alive}")
        return alive

    def census_window(self, tag, seconds):
        """Bank EVERY leg stop for `seconds` of wall time (NOT until quiet —
        with the hot 0x3b pump armed, quiet never comes; the msg-id SET is the
        datum). bank_stop re-arms all legs and RUNs (census mode never drops),
        and the cascade inside resume_and_rearm banks 1-3 stops per call, so
        the per-window cap is SMALL (6): each banked stop costs ~20-90 s of
        MCP round-trips (BREAK lottery dominates). The whole-log pty census
        counts EVERY fire regardless. Storm cap 6."""
        t_end = time.time() + seconds
        recs = []
        # t320 pulse train: keep ds:0x484ac (mouse-active word) re-set through
        # the poster pass. Sent ONLY in quiet iterations (never mid bank_stop
        # cascade), and NOT in baseline windows (x is None there). xsend has
        # NO motion verb and SDL rejects synthetic MotionNotify (xsend.c
        # header law) — a real Button click is the sanctioned activator.
        px = getattr(self, "pulse_xy", None)
        n_left = getattr(self, "pulse_clicks", 0) if px is not None else 0
        t_pulse = time.time() + 1.5
        while time.time() < t_end and len(recs) < 6:
            txt = self.pty_new()
            if txt and self.leg_pats and any(p.search(txt)
                                             for p in self.leg_pats):
                time.sleep(1.5)
                self.pty_new()          # settle the code view (t302 form)
                recs.append(self.bank_stop(f"{tag}#{len(recs)}"))
                continue
            if px is not None and n_left and time.time() >= t_pulse:
                self.pulse_count = getattr(self, "pulse_count", 0) + 1
                self.log(f"PULSE {tag}#{self.pulse_count} at {px}")
                self.send(["click", str(int(px[0])), str(int(px[1]))])
                n_left -= 1
                t_pulse = time.time() + 1.5
                continue
            time.sleep(1.0)
        self.log(f"CENSUS-WINDOW {tag}: {len(recs)} stops banked "
                 f"({seconds:.0f}s)")
        return recs

    def census_click(self, x, y, tag, seconds):
        """THE t303 unit: arm ONLY around the measured click. Choreography
        between clicks runs leg-free — a hot armed leg + an un-polled click =
        the guest frozen mid-sequence (t302 law, the reason t302 could not
        census map clicks). x=None = BASELINE window (no click)."""
        if x is not None:
            # t298 LAW re-confirmed (t303 defect 4a): an open modal SWALLOWS
            # map clicks (225/207 px diffs = screen repaint only). Close first,
            # BEFORE the arm, so the armed window is not spent on dead clicks.
            if not self.close_eventwin():
                self.log(f"CENSUS {tag}: close_eventwin failed — click "
                         f"skipped (modal law)")
                return None
        # t320: pulse train is per-window — armed ONLY around a real click
        # window (baseline windows must measure the unperturbed fire rate).
        self.pulse_xy = ((x, y) if x is not None
                         and getattr(self, "pulse_clicks", 0) else None)
        if not self.assert_on_map(f"pre_{tag}"):
            return None
        if not self.arm_census(self.legs):
            self.log(f"CENSUS {tag}: ARM FAILED — click not measured")
            return None
        lines, ok, hdr = self.req("EXEC RUN", 20.0)
        self.log(f"CENSUS {tag}: armed RUN hdr={hdr}")
        time.sleep(0.5)
        if x is not None:
            self.send(["click", str(int(x)), str(int(y))])
        recs = self.census_window(tag, seconds)
        self.disarm_run(tag)
        self.persist()
        return recs

    # ---------- drive helpers ----------
    def click(self, x, y, tag, wait=2.5):
        if not self.assert_on_map(f"pre_{tag}"):
            return False
        self.send(["click", str(int(x)), str(int(y))])
        time.sleep(wait)
        return True

    def open_fleet(self):
        map_im = self.grab("map")
        if map_im is None:
            return None, 0
        if not self.close_eventwin():
            self.log("EVENTWIN would not close before FLEET")
            return None, 0
        if not self.click(*FLEET_BTN, "fleet", wait=2.5):
            return None, 0
        im = self.grab("fleet")
        d = self.diff_px(map_im, im)
        if d < 30000:
            self.close_eventwin()
            self.click(*FLEET_BTN, "fleet_retry", wait=2.5)
            im = self.grab("fleet2")
            d = self.diff_px(map_im, im) if im is not None else 0
        self.log(f"FLEET diff={d} "
                 f"rails={self.fleet_open(im) if im else 0}")
        return (im, d) if d >= 30000 else (None, d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55999)
    ap.add_argument("--tl", type=int, default=1800)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--boot", type=int, default=170)
    ap.add_argument("--legs", default="router,cos_entry,cos_hdlr,cos_s3,"
                                      "cos_s5,btn_entry,btn_hdlr,batmode_dead")
    ap.add_argument("--views", type=int, default=4)
    ap.add_argument("--clicks-per-view", type=int, default=4)
    ap.add_argument("--control-click", type=int, default=0)  # t301: black rect, REFUTED
    ap.add_argument("--census", action="store_true")   # t303 msg-census mode
    ap.add_argument("--witness", type=int, default=0)  # t304 A: bank N stops, no clicks
    ap.add_argument("--window", type=int, default=30)  # census bank-window s
    ap.add_argument("--target-kinds", default="sprite,planet,empty")
    ap.add_argument("--star-click", type=int, default=0)  # t307 N cosmos pips
    ap.add_argument("--pre-turn", type=int, default=0)    # t310 End Turn ONCE
                                                          # before the fleet
                                                          # battery (t298 gate)
    ap.add_argument("--digit-keys", type=int, default=0)  # t310 N digit keys
    ap.add_argument("--fleet-keys", type=int, default=0)  # t314 N digit keys
                                                          #    with FLEET open
                                                          # '1'.. in ONE armed
                                                          # window (msg-0x1c01
                                                          # sender 0x35696)
    ap.add_argument("--shipclick", type=int, default=0)   # t317 N gutter clicks
    ap.add_argument("--pulse-clicks", type=int, default=0)  # t320: N extra
    # Button1 pulses at the click coord INSIDE each armed window (keeps
    # ds:0x484ac mouse-active through the poster pass; xsend has no motion
    # verb and SDL rejects synthetic motion — click is the activator)
                                                          #    at x=620 inside
                                                          #    STATSHIPLST rect
                                                          #    (emit road, fn
                                                          #    0x33320 strip law)
    args = ap.parse_args()

    if args.witness and args.legs == ap.get_default("legs"):
        # t304 WITNESS default: cos_hdlr ONLY (hot pump leg -> stops ~2 s;
        # leg-light = the t302 freeze law respected by construction).
        args.legs = "cos_hdlr"
    if args.census and args.legs == ap.get_default("legs"):
        # t304 CENSUS default set (t303 slot-1 set DEAD per REFUTED-ROUTES
        # t303 amendment): every slot-2 call site in the payload (22, static
        # whole-image ff/2 decode) + both handlers. The pty census attributes
        # the true dispatch site; btn_hdlr makes the NEXTTURN control
        # witnessable (t303 defect 4b).
        args.legs = ",".join([f"s2_{o:05x}" for o in sorted(
            v for k, v in LEGS.items() if k.startswith("s2_"))]
            + ["cos_hdlr", "btn_hdlr"])
    legs = [l.strip() for l in args.legs.split(",") if l.strip()]
    for l in legs:
        if l not in LEGS:
            print(f"HARNESS ERROR: unknown leg {l!r}")
            return 2
    for p, why in [(DBG_BIN, "debugger binary"), (R293.SCRATCH, "scratch"),
                   (R293.PAYLOAD, "payload"), (R293.OCT29, "Oct-29 backup")]:
        if not op.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if op.abspath(R293.SCRATCH).startswith(op.join(ROOT, "game") + op.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    if hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest() != R293.OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2
    pay = open(R293.PAYLOAD, "rb").read()
    for l in legs:
        off = LEGS[l]
        print(f"LEG {l:9s} file {off:#07x} linear {P0+off:#08x} "
              f"bytes {pay[off:off+10].hex(' ')}")

    s = Sess(args)
    s.legs = legs   # resume_and_rearm re-arms exactly this set
    s.pulse_clicks = args.pulse_clicks   # t320 (consumed in census_window)
    s.log(f"t299 leg-witness session start out={s.out} legs={legs}")
    s.launch()
    rc = 1
    try:
        conn = s.connect()
        if conn is None:
            s.log("NEGATIVE: no MCP connection")
            return 1
        lines, ok, hdr = s.req("PING", 10.0)
        s.log(f"PING hdr={hdr} lines={lines}")
        if "PONG" not in " ".join(lines):
            s.log("NEGATIVE: no PONG")
            return 1
        s.log(f"settling {args.settle}s before BREAK")
        time.sleep(args.settle)
        if not s.do_break():
            s.log("NEGATIVE: BREAK lottery lost — relaunch loop should retry")
            return 1
        # ARMING LAW (source-measured): BP location = GetAddress(seg,off),
        # which for seg==CS returns SegPhys(cs)+off — computed AT ARM TIME with
        # the mode AT ARM TIME. Arming at the real-mode title would bake the
        # wrong base. Therefore: BREAK only to WIN the lottery and prove the
        # channel; arm AFTER the campaign load (guaranteed pmode, CS=0160) with
        # a base-verified P0. Losing this second BREAK is survivable: arm/RUN
        # go through EXEC, and the STOP path only needs the debugger to exist
        # when a leg hits (t282: fires land via the debugCallback trampoline).
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"post-lottery RUN hdr={hdr} lines={lines}")
        s.pty_new()

        if not s.wait_title():
            s.log("NEGATIVE: title never appeared after RUN")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed")
            return 1
        time.sleep(args.settle)
        closed = s.drain_popups()
        s.log(f"post-load drain closed {closed}")

        rows = s.ring_mem_rows()
        if not rows or not rows[-1].get("recs"):
            s.log("NEGATIVE: ring has no ship records")
            return 1
        mem = s.read_mem(rows[-1]["path"])
        B = SL.base_of(mem, s.anch)
        s.log(f"ring base B={hx(B)} (expect {hx(EXPECT_BASE)})")
        if B != EXPECT_BASE:
            s.log("NEGATIVE: base mismatch — the armed leg addresses would be "
                  "wrong for this session; aborting interpretation")
            return 1

        # ---- t304 WITNESS MODE: no clicks, no choreography. Arm cos_hdlr
        # ONLY; the 0x3b pump fires it ~1/s, and every bank_stop dumps [esp]
        # -> ret0 = the CALLER EIP verbatim (the datum t303 could not name).
        if args.witness:
            s.census = True          # light bank_stop + hot-leg liveness law
            s.pay = pay
            allrecs = []
            for att in range(3):
                allrecs += (s.census_click(None, None, f"witness{att}",
                                           args.window) or [])
                if len([r for r in allrecs
                        if r.get("ret_stack", {}).get("ret0_file_off")]) >= 3:
                    break
            rets = [r["ret_stack"] for r in allrecs
                    if r.get("ret_stack", {}).get("ret0_file_off")]
            s.log(f"WITNESS: {len(allrecs)} stops, {len(rets)} with ret0: "
                  + " | ".join(f"{r['ret0']}->{r['ret0_file_off']}"
                               for r in rets[:8]))
            whole = open(s.ptylog, "rb").read().decode("utf-8", "replace")
            pty_census = {}
            for name in s.legs:
                lin = P0 + LEGS[name]
                # t305: dual-core patterns (fire_pats). The two forms are
                # MUTUALLY EXCLUSIVE per render (5-hex lookbehind kills the
                # 6-hex run and vice versa), so summing findalls never
                # double-counts one fire.
                pty_census[name] = len([m for pt in fire_pats(lin)
                                        for m in pt.findall(whole)])
            s.probes.append({"probe": "witness-ret0", "stops": len(allrecs),
                             "ret0": [r["ret0_file_off"] for r in rets]})
            s.persist()
            with open(op.join(s.out, "witness.json"), "w") as fh:
                json.dump({"stops": allrecs, "pty": pty_census}, fh, indent=1)
            rc = 0 if rets else 1
            s.log(f"SESSION END rc={rc} witness-ret0={len(rets)}"
                  + (" CONTINUING to census (combined mode)"
                     if args.census else ""))
            if args.census:
                # combined single-boot session: re-target legs to the census
                # set (slot-2 call sites + both handlers) and fall through.
                args.legs = ",".join([f"s2_{o:05x}" for o in sorted(
                    v for k, v in LEGS.items() if k.startswith("s2_"))]
                    + ["cos_hdlr", "btn_hdlr"])
                legs = args.legs.split(",")
                s.legs = legs
                rc = 1   # census result decides the session rc
            else:
                return rc

        # ---- t303 CENSUS MODE: never arm across choreography. Every
        # measurement is an arm -> click -> bank-window -> disarm cycle;
        # between cycles the guest runs leg-free and alive (t302 freeze laws).
        if args.census:
            s.census = True
            s.pay = pay
            census = {}
            oracles = {}
            # t306 SELECTION ORACLE (delta-pair law, ships.md S25 t297-A: the
            # DAT scalars at B+OFF+X churn WITHOUT input — only before/after
            # pairs around a click mean anything; sel43510 = the watch.log
            # sel= field, DAT_43504 = current-system/star/sel-object ptr).
            # t307: MOVED above the baseline so the star phase shares it.
            def sel_oracle(tag):
                try:
                    p = s.newest_sav()
                    if not p:
                        return None
                    mm = s.read_mem(p)
                    if not mm:
                        s.log(f"ORACLE {tag}: Memory unreadable in {op.basename(p)}")
                        return None
                    bb = SL.base_of(mm, s.anch)
                    if not bb:
                        s.log(f"ORACLE {tag}: no base vote in {op.basename(p)}")
                        return None
                    rd = lambda X: struct.unpack_from("<I", mm, bb + SL.OFF + X)[0]
                    v43504 = rd(0x43504)
                    # t309 CORE READS (docs/re/_wip_t309.md S1.13): core
                    # struct base = the 0x7a35c immediate (t307 self-
                    # relocation law: RAM immem = +0x242000 rebased, member
                    # index = linear - mem_base, so member bb+SL.OFF+0x7a35c).
                    # mode/pump-gates decide whether the RING-B consumer CAN
                    # run; ring counters decide whether it HAS work.
                    core = bb + SL.OFF + 0x7a35c
                    rdc = lambda D: struct.unpack_from("<I", mm, core + D)[0]
                    # t308 S1 LAW: the sav Memory member is +0x88 off guest
                    # LINEAR, so bb+SL.OFF+X == linear mem_base(obj1)+X — the
                    # oracle address IS the rebased store target (t307 fire
                    # decoded [00285504] == member 0x28558c). alt_285504 =
                    # member B+OFF-0x88+0x43504 (linear 0x28547c, a DIFFERENT
                    # variable — the void t307 datum, kept for disambiguation).
                    o = {"tag": tag, "sav": op.basename(p), "turn": rd(0x12e10),
                         "sel43510": mm[bb + SL.OFF + 0x43510],
                         "DAT_43504": hx(v43504),
                         "DAT_43504_name": s.star_name_at(mm, v43504),
                         "alt_285504": hx(struct.unpack_from(
                             "<I", mm, bb + SL.OFF - 0x88 + 0x43504)[0]),
                         "DAT_43508": hx(rd(0x43508)),
                         # t309 gate/ring snapshot (S1.13): mode==1 required
                         # by BOTH consumer and pump; ringB widx!=0 required
                         # by the pump; ringA count>0 required by the
                         # resolver; pump_gate ds:0x660c==-1 required by the
                         # fn-0x20fd4 path to 0x54650; guard ds:0x7a358.
                         "mode4226": hex(rdc(0x4226) >> 16),
                         "ringB_count": hex(rdc(0x4758) >> 16),
                         "ringB_widx": hex(struct.unpack_from(
                             "<H", mm, core + 0x475a)[0]),
                         "ringA_count": hex(rdc(0x44aa) >> 16),
                         "ringA_idx": hex(struct.unpack_from(
                             "<H", mm, core + 0x44ac)[0]),
                         "pump_gate_660c": hx(rd(0x660c)),
                         # t310 (task-mandated + the fn-0x51834 gate):
                         # 0x7e5aa = core member +0x44aa (ringA count, the
                         # t309 lesson: read it DIRECT, not via rdc offsets),
                         # 0x7e89e = core member +0x489e, 0x484ec = the
                         # turn-gate scalar of the msg-0x1c01 destination
                         # path (publishes iff > 0x96).
                         "gate_7e5aa": hx(rd(0x7e5aa)),
                         "gate_7e89e": hx(rd(0x7e89e)),
                         "gate_484ec": hx(rd(0x484ec)),
                         "guard_7a358": hx(rdc(-4))}
                    s.log(f"ORACLE {tag} {o}")
                    return o
                except Exception as e:
                    s.log(f"ORACLE {tag} error {e!r}")
                    return None
            # SHORT baseline: the 0x3b pump guarantees a fire storm there; the
            # whole-log pty census counts them all anyway. The banked baseline
            # just names the pump msg-id for the CURRENT window set.
            census["baseline"] = s.census_click(
                None, None, "baseline", 15)
            # ---- t307 COSMOS STAR-CLICK PHASE (galaxy map; campaign-load
            # view IS the map — do NOT open_fleet, t306 lands system view).
            # Candidate law VERBATIM from r293 enter_system (bright pips,
            # sum(r+g+b)>380, x 40..455 y 60..440, nearest MAP_CENTER first);
            # dedupe >=20px apart. A hit = screen diff vs map baseline >15000
            # = entered system view -> escape ladder BEFORE the next click
            # (t285: never Escape blind; ladder checks orange each press).
            star_results = {}
            if args.star_click:
                map_im0 = s.grab("map_pre_star")
                cands = []
                if map_im0 is not None:
                    # t308b GREEN-ANNULUS PIP LAW (offline census of run
                    # 140250's own map shot, MEASURED): system pips are rings
                    # of the green family {(0,85,40),(0,113,56),(0,142,69)}
                    # (20-70 px each); the old sum>380 rule picked purple UI
                    # text fragments and field dots (5 of 6 clicks were
                    # repaints, the one ENTER was Icarus again). Cluster the
                    # green family (8px link), centroid each >=10-px cluster;
                    # EXCLUDE centroids within 40px of the KNOWN Icarus pip
                    # (238,282, measured twice: t307+t308 ENTER at that px)
                    # so every click targets a DIFFERENT system by
                    # construction (idle DAT_43504 = Icarus ptr -> same-value
                    # stores are invisible; only starA->starB is a datum).
                    px = map_im0.load()
                    GREENS = {(0, 85, 40), (0, 113, 56), (0, 142, 69)}
                    gp = [(x, y) for y in range(60, 440)
                          for x in range(40, 456) if px[x, y] in GREENS]
                    gpset = set(gp)
                    seen = set()
                    from collections import deque as _dq
                    for p in gp:
                        if p in seen:
                            continue
                        q = _dq([p]); seen.add(p); pts = []
                        while q:
                            cx0, cy0 = q.popleft(); pts.append((cx0, cy0))
                            for nx in range(cx0 - 8, cx0 + 9):
                                for ny in range(cy0 - 8, cy0 + 9):
                                    if (nx, ny) in gpset and (nx, ny) not in seen:
                                        seen.add((nx, ny)); q.append((nx, ny))
                        if len(pts) < 10:
                            continue
                        mx = sum(a for a, _ in pts) // len(pts)
                        my = sum(b for _, b in pts) // len(pts)
                        d_ic = ((mx - 238) ** 2 + (my - 282) ** 2) ** 0.5
                        # 50px not 40: Icarus's OWN annulus centroid lands
                        # ~6px off the pip centre (measured (237,288)); a
                        # click there = a third same-value store.
                        if d_ic < 50:
                            continue
                        cands.append((d_ic, mx, my))
                    cands.sort()
                s.log(f"STAR-PHASE: {len(cands)} bright candidates, "
                      f"nearest={cands[:3]}")
                tried = []
                for i in range(args.star_click):
                    pick = None
                    for cd, xx, yy in cands:
                        if all(abs(xx - tx) + abs(yy - ty) > 20
                               for _, tx, ty in tried):
                            pick = (cd, xx, yy)
                            break
                    if pick is None:
                        s.log(f"STAR-PHASE {i}: no fresh candidate — stop")
                        break
                    cd, xx, yy = pick
                    tried.append(pick)
                    oracles[f"star{i}_before"] = sel_oracle(f"star{i}_before")
                    recs = s.census_click(xx, yy, f"star{i}_{xx}x{yy}",
                                          args.window)
                    im_a = s.grab(f"star{i}_screen")
                    dv = (s.diff_px(map_im0, im_a)
                          if im_a is not None else -1)
                    entered = dv > 15000
                    oracles[f"star{i}_after"] = sel_oracle(f"star{i}_after")
                    # t308 WITNESS BREAK: the close-condition datum is a REAL
                    # DAT_43504 delta (t307 proved same-value stores are
                    # invisible to pairs). Idle scalar = current star ptr, so
                    # an ENTERED click on a DIFFERENT star must flip it
                    # (starA->starB). On a flip, bank and stop the pip loop.
                    delta = False
                    ob4 = oracles.get(f"star{i}_before")
                    oa4 = oracles.get(f"star{i}_after")
                    if entered and ob4 and oa4:
                        delta = ob4.get("DAT_43504") != oa4.get("DAT_43504")
                    star_results[f"star{i}"] = {
                        "click": [xx, yy], "cand_dist": cd,
                        "screen_diff_vs_map": dv, "entered_system": entered,
                        "dat43504_delta": delta,
                        "stops": recs}
                    s.log(f"STAR-PHASE {i}: click ({xx},{yy}) diff={dv} "
                          f"entered={entered} stops={0 if recs is None else len(recs)}")
                    if entered:
                        if not s.escape_to_map(map_im0):
                            s.log("STAR-PHASE: escape_to_map FAILED — "
                                  "remaining star windows skipped")
                            break
                        if delta and ob4 and oa4:
                            s.log(f"WITNESS DELTA at star{i}: DAT_43504 "
                                  f"{ob4.get('DAT_43504')}"
                                  f"({ob4.get('DAT_43504_name')}) -> "
                                  f"{oa4.get('DAT_43504')}"
                                  f"({oa4.get('DAT_43504_name')}) — pip loop "
                                  "stopped early (datum banked)")
                            break
                census.update({k: v["stops"] for k, v in star_results.items()})
            # t309 HOT HOLD after the star phase (the t308 blind-spot fix,
            # S1.7/S1.13): census_click(None) RE-ARMS THE FULL LEG SET and
            # banks 60 s leg-hot with NO click — consumer/resolver fires that
            # happen after the click's window disarms are INVISIBLE to the
            # pty whole-log census (a stop requires an armed BP), so this
            # window is the only instrument that can see them.
            census["hold_post_star"] = s.census_click(
                None, None, "hold_post_star", args.window)
            oracles["hold_post_star"] = sel_oracle("hold_post_star")
            # t310 --pre-turn (t298 GATE LAW: at t=1086 the owner-0 fleet has
            # NO kind-4 (moves>0) ship; the sprite picker needs one, so End
            # Turn ONCE before the fleet battery. Clicked on the bare map with
            # the orange title guard inside click(); NOT inside an armed window.
            if args.pre_turn:
                oracles["preturn_before"] = sel_oracle("preturn_before")
                s.click(R293.NEXTTURN[0], R293.NEXTTURN[1], "preturn",
                        wait=6.0)
                oracles["preturn_after"] = sel_oracle("preturn_after")
                s.log(f"PRE-TURN turn {oracles['preturn_before'].get('turn') if oracles['preturn_before'] else '?'}"
                      f" -> {oracles['preturn_after'].get('turn') if oracles['preturn_after'] else '?'}")
            # t311 --digit-keys PHASE MOVED ABOVE THE FLEET OPEN (the t310
            # focus defect: t310 pressed keys after the planet window with a
            # 'Cancel' popup holding focus, so 0x1c01 (if sent) went to a
            # BUTTON class, not STATUSWND). Bare map = STATUSWND-focus
            # candidate; the entry leg's win-name names the focused window
            # verbatim either way. The ONLY in-image senders of msg 0x1c01
            # are fn-0x160xx (0x16168) and the DIGIT-KEY handler (0x35696,
            # gate cmp ebx,0x31/0x39 = ASCII '1'..'9').
            if args.digit_keys:
                keys = [str(k) for k in range(1, min(9, args.digit_keys) + 1)]
                if not s.close_eventwin():
                    s.log("DIGIT-PHASE: close_eventwin failed — skipped")
                elif not s.assert_on_map("digit_prearm"):
                    s.log("DIGIT-PHASE: not on bare map — skipped "
                          "(title guard)")
                elif s.arm_census(s.legs):
                    # POST-ARM POPUP REGUARD (t311): a popup that opens
                    # between close_eventwin and the arm would steal focus
                    # again mid-window — re-check and bail rather than press
                    # into the wrong window.
                    im_pg = s.grab("digit_reguard")
                    if im_pg is not None and s.eventwin_open(im_pg):
                        s.log("DIGIT-PHASE: POPUP REGUARD — popup open at "
                              "arm; RUN resumed, keys NOT pressed")
                        s.req("EXEC RUN", 20.0)
                    else:
                        lines, ok, hdr = s.req("EXEC RUN", 20.0)
                        s.log(f"DIGIT-PHASE: armed RUN hdr={hdr} keys={keys}")
                        time.sleep(0.5)
                        for k in keys:
                            s.send(["key", k])
                            time.sleep(1.2)
                        census["digit_keys"] = s.census_window(
                            "digit_keys", args.window)
                        s.disarm_run("digit_keys")
                        s.persist()
                else:
                    s.log("DIGIT-PHASE: ARM FAILED — keys not measured")
                oracles["digit_after"] = sel_oracle("digit_after")
            im, d = (None, 0) if args.star_click else s.open_fleet()
            if im is None:
                s.log(f"CENSUS: FLEET would not open (diff {d}) — clicking "
                      f"current screen targets only")
            # t314 --fleet-keys PHASE (docs/re/_wip_t314.md): the digit sender
            # 0x356a5 `call [esi+8]` edx=0x1c01 dispatches on the KEY-FOCUSED
            # window. t311/t312 measured bare-map focus = btn class (NEXTTURN-
            # CONT), msg never reached STATUSWND; t313 named FLEETWND (cp
            # 0x247fa8) with its OWN 0x1c01 path je@0x51cfa->0x51f3b->state
            # table RAM 0x211188 -> writer blocks. THE UNTESTED CARRIER: keys
            # pressed with the FLEET window open. FOCUS DEFECT FIX (run
            # t299-leg-20261105-210255, MEASURED): the rowjump click (200,93)
            # CLOSES the fleet window (rails 188 -> 0 at the reguard grab), so
            # those keys went to 'PLBUILD' (btn class) — NOT FLEETWND. The
            # phase therefore runs BEFORE rowjump0, and the reguard asserts
            # fleet_open(rails)>0 as well as no-popup: keys are pressed only
            # with the FLEET window verifiably still open.
            if args.fleet_keys:
                if im is None or not s.fleet_open(im):
                    s.log("FLEET-KEYS: FLEET window not open — skipped")
                else:
                    fkeys = [str(k) for k in
                             range(1, min(9, args.fleet_keys) + 1)]
                    oracles["fleetkeys_before"] = sel_oracle(
                        "fleetkeys_before")
                    if s.arm_census(s.legs):
                        im_pg = s.grab("fleetkeys_reguard")
                        if im_pg is None or s.eventwin_open(im_pg) \
                                or not s.fleet_open(im_pg):
                            s.log("FLEET-KEYS: REGUARD FAIL — popup open or "
                                  f"rails={s.fleet_open(im_pg) if im_pg is not None else '?'}"
                                  " — RUN resumed, keys NOT pressed")
                            s.req("EXEC RUN", 20.0)
                        else:
                            lines, ok, hdr = s.req("EXEC RUN", 20.0)
                            s.log(f"FLEET-KEYS: armed RUN hdr={hdr} "
                                  f"keys={fkeys} rails={s.fleet_open(im_pg)}")
                            time.sleep(0.5)
                            for k in fkeys:
                                s.send(["key", k])
                                time.sleep(1.2)
                            popup_after = s.grab("fleetkeys_popup")
                            s.log("FLEET-KEYS: popup open after keys = "
                                  f"{s.eventwin_open(popup_after) if popup_after is not None else '?'}")
                            census["fleet_keys"] = s.census_window(
                                "fleet_keys", args.window)
                            s.disarm_run("fleet_keys")
                            s.persist()
                            if popup_after is not None and \
                                    s.eventwin_open(popup_after):
                                s.close_eventwin()
                    else:
                        s.log("FLEET-KEYS: ARM FAILED — keys not measured")
                    oracles["fleetkeys_after"] = sel_oracle(
                        "fleetkeys_after")
            # t317 --shipclick PHASE (docs/re/_wip_t317.md S3): fn 0x33320's
            # strip law (VERBATIM 0x33331..0x33342: emit iff click-X >
            # [w+0x10]-[w+0xbf] = 632-28) says the 0x1c01 EMIT ROAD fires for a
            # click in the RIGHT 28-px GUTTER of STATSHIPLST (x in (604,632],
            # y in [46,472]), msg 4/5 family (msg 0xc needs [w+0x4f]==0x30;
            # MEASURED 0x66 — scripts/r317_gate_probe.py). Target = [w+0x63]=95
            # = FLEETWND slot (t316). Witness leg s2_56cda = the dispatch call
            # site inside fn 0x56ca4: at the stop eax=registry win rec,
            # esi=cp, edi=MSG — edi==0x1c01 names the whole chain in one reg
            # set. NO rowjump before this phase (closes FLEET, t314 law).
            if args.shipclick:
                if im is None or not s.fleet_open(im):
                    s.log("SHIPCLICK: FLEET window not open — skipped")
                else:
                    # baseline armed window (no click): the s2_56cda background
                    # fire rate makes the click-window counts attributable.
                    oracles["shipclick_baseline"] = sel_oracle(
                        "shipclick_baseline")
                    census["shipclick_baseline"] = s.census_click(
                        None, None, "shipclick_baseline", args.window)
                    ys = [250, 120, 453, 300][:args.shipclick]
                    for cy in ys:
                        oracles[f"shipclick{cy}_before"] = sel_oracle(
                            f"shipclick{cy}_before")
                        census[f"shipclick{cy}"] = s.census_click(
                            620, cy, f"shipclick_620x{cy}", args.window)
                        oracles[f"shipclick{cy}_after"] = sel_oracle(
                            f"shipclick{cy}_after")
                        # RAW gate datum (guest 0x600058 indexes the sav Memory
                        # member DIRECTLY — t316 S2 base law, probe-verified).
                        gp = s.newest_sav()
                        gm = s.read_mem(gp) if gp else None
                        if gm and len(gm) > 0x60005d:
                            s.probes.append({
                                "probe": "gate600058", "after": cy,
                                "gate": gm[0x600058],
                                "datum59c": gm[0x600059:0x60005d].hex()})
                        popup_sc = s.grab(f"shipclick{cy}_post")
                        if popup_sc is not None and s.eventwin_open(popup_sc):
                            s.close_eventwin()
                        if popup_sc is not None and not s.fleet_open(popup_sc):
                            s.log(f"SHIPCLICK: FLEET closed after click y={cy}"
                                  " — phase stopping (rails reguard)")
                            break
            if im is not None:
                if not s.click(200, FLEET_ROWS[0], "rowjump0", wait=3.0):
                    s.log("CENSUS: rowjump failed")
            sys_im = s.grab("census_view")
            star = ""
            p = s.newest_sav()
            if p:
                m2 = s.read_mem(p)
                B2 = SL.base_of(m2, s.anch) if m2 else None
                if B2:
                    star = s.star_name_at(
                        m2, struct.unpack_from(
                            "<I", m2, B2 + SL.OFF + 0x43504)[0])
            sprites = s.ship_sprites(sys_im) if sys_im is not None else []
            planet = s.planet_point(sys_im) if sys_im is not None else None
            emp = (s.empty_point(sys_im, [(x, y) for x, y, _ in sprites] +
                                 ([planet] if planet else []))
                   if sys_im is not None else None)
            s.log(f"CENSUS view star={star!r} sprites={sprites[:4]} "
                  f"planet={planet} empty={emp}")
            targets = [(x, y, "sprite") for x, y, _ in sprites[:2]]
            if planet:
                targets.append((planet[0], planet[1], "planet"))
            if emp:
                targets.append((emp[0], emp[1], "empty"))
            # t306: --target-kinds filters WHICH targets get a window (task
            # scope: sprite + control_nextturn only; planet/empty datum done
            # t305, don't re-measure).
            want = {k.strip() for k in args.target_kinds.split(",")}
            # t307: sel_oracle MOVED above the baseline (shared with the star
            # phase); the t306 duplicate definition + `oracles = {}` reset
            # deleted here (it would have wiped the star oracle pairs).
            for (cx, cy, kindlbl) in [t for t in targets
                                      if t[2] in want][:args.clicks_per_view]:
                oracles[f"{kindlbl}_before"] = sel_oracle(f"{kindlbl}_before")
                census[kindlbl] = s.census_click(
                    cx, cy, f"{kindlbl}_{cx}x{cy}", args.window)
                oracles[f"{kindlbl}_after"] = sel_oracle(f"{kindlbl}_after")
            # (t311: the t310 digit-keys block that used to sit HERE — after
            # the fleet/planet windows — MOVED above open_fleet to the bare
            # map; a second press-block here would overwrite census["digit_keys"]
            # and re-press into whatever popup the planet click opened.)
            # POSITIVE CONTROL inside the dispatch-site instrument: NEXTTURN's
            # dispatch is windows.txt VERBATIM msg 7 (t302 btn_hdlr witness) —
            # if msg 7 + name NEXTTURN appears at a disp site, the census
            # attribution law holds. (Advances the turn: allowed on scratch.)
            # t309: oracle PAIR around it settles the t308 branch-(b) question
            # (turn delta via rd(0x12e10): did the turn actually advance?),
            # and the post-turn HOT HOLD catches a consumer that only runs
            # after the turn-advance pump.
            oracles["nextturn_before"] = sel_oracle("nextturn_before")
            census["control_nextturn"] = s.census_click(
                R293.NEXTTURN[0], R293.NEXTTURN[1], "control_nextturn",
                args.window)
            census["hold_post_turn"] = s.census_click(
                None, None, "hold_post_turn", args.window)
            oracles["nextturn_after"] = sel_oracle("nextturn_after")
            # WHOLE-LOG pty census (catches any stop poll_stop/census_window
            # missed between cycles; same fire-pattern law as arm_all)
            whole = open(s.ptylog, "rb").read().decode("utf-8", "replace")
            pty_census = {}
            for name in s.legs:
                lin = P0 + LEGS[name]
                # t305 dual-core fire law (see witness block above).
                pty_census[name] = len([m for pt in fire_pats(lin)
                                        for m in pt.findall(whole)])
            s.log(f"PTY WHOLE-LOG CENSUS {pty_census}")
            s.probes.append({"probe": "pty-whole-log-census",
                             "counts": pty_census})
            s.persist()
            with open(op.join(s.out, "census.json"), "w") as fh:
                json.dump({"window_s": args.window, "star": star,
                           "targets": census, "pty": pty_census,
                           "oracles": oracles},
                          fh, indent=1)
            # t307: in --star-click mode a completed bank-window with ZERO
            # stops IS the datum (task close-condition: "zero fires at ALL 8
            # sites is ALSO a datum"), so measured = windows that RAN
            # (recs is not None), not windows that banked. Non-star mode
            # keeps the t303 semantics (back-compat with runs 033648/061825).
            measured = [k for k, v in census.items()
                        if k not in ("baseline",)
                        and (v if not args.star_click else v is not None)]
            rc = 0 if measured else 1
            s.log(f"SESSION END rc={rc} census-measured={measured} "
                  f"hits={len(s.hits)}")
            return rc

        # ---- arm in pmode, base verified ----
        # The BREAK may land on a real-mode DOS moment (wrong CS, EIP below the
        # image). Retry: RUN, wait, BREAK again (max 4) before declaring a
        # negative. Arming under the wrong mode would bake a wrong location
        # (GetAddress is evaluated AT ARM TIME), so this gate is not optional.
        p0_ok = False
        cs = eip0 = None
        for att in range(4):
            if att:
                self_r = s.req("EXEC RUN", 15.0)
                s.log(f"arm-retry {att}: RUN hdr={self_r[2]}")
                time.sleep(4.0)
            if not s.do_break():
                s.log(f"arm-retry {att}: BREAK lottery lost at arm time")
                continue
            cs = s.read_reg("cs")
            eip0 = s.read_reg("eip")
            s.log(f"arm attempt {att}: cs={hx(cs)} eip={hx(eip0)}")
            p0_ok = bool(cs and eip0 and P0 <= eip0 < CODE_END)
            if p0_ok:
                s.csseg = cs
                break
        s.probes.append({"probe": "armtime-eip-in-payload-image",
                         "eip": hx(eip0), "cs": hx(cs), "p0": hx(P0),
                         "code_end": hx(CODE_END), "ok": p0_ok})
        if not p0_ok:
            s.log("NEGATIVE: never caught a pmode arm-time window — arming "
                  "would be blind; aborting (honest)")
            return 1
        if not s.arm_all(legs):
            s.log("NEGATIVE: BPLIST did not confirm the armed leg set")
            return 1
        s.log("armed: " + ", ".join(s.leg_lines.values()))
        # MEMDUMPBIN addressing control: bytes at the armed batcon linear must
        # equal payload file bytes at 0x1b91c (proves the dump path AND the P0
        # law in one shot; honest log either way — dump failures are known at
        # title-arm, untested mid-game).
        ctl = s.dump_mem(P0 + LEGS["router"], 16, "control")
        if ctl:
            want = pay[LEGS["router"]:LEGS["router"] + len(ctl)]
            s.log(f"MEMDUMPBIN control MATCH={ctl == want} "
                  f"got={ctl.hex(' ')} want={want.hex(' ')}")
            s.probes.append({"probe": "memdumpbin-control",
                             "match": ctl == want})
        else:
            s.probes.append({"probe": "memdumpbin-control", "match": None,
                             "note": "no file"})
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"armed RUN hdr={hdr} lines={lines}")
        t0 = time.time()
        e1 = s.read_reg("eip")
        s.probes.append({"probe": "exec-while-running",
                         "eip": hx(e1), "answered": e1 is not None,
                         "rtt_s": round(time.time() - t0, 2)})
        s.exec_free = e1 is not None
        s.log(f"EXEC-while-running probe: eip={hx(e1)} "
              f"answered={e1 is not None} rtt={s.probes[-1]['rtt_s']}s "
              f"-> stopped-oracle {'INVALID (EXEC answers while running)' if s.exec_free else 'VALID (a reply means STOPPED)'}")
        s.persist()
        # t302 FIX: was s.pty_new() — which SWALLOWED the first fire line
        # (attempt 1: cos_hdlr fired seconds after RUN and its line was
        # consumed here, never banked). poll_stop scans incrementally and
        # banks anything already pending.
        s.poll_stop("post-run-immediate", budget=6.0)

        # End Turn ONCE (kind-4 gating fact, t297/t298)
        turn0 = max(d["turn"] for d in rows)
        presses, advanced = 0, False
        while presses < 3 and not advanced:
            if not s.assert_on_map(f"endturn{presses}"):
                return 1
            s.send(["click", str(R293.NEXTTURN[0]), str(R293.NEXTTURN[1])])
            presses += 1
            t0 = time.time()
            while time.time() - t0 < 150:
                st = s.poll_stop(f"endturn-p{presses}", budget=5.0)
                if st:
                    continue
                rows = s.ring_mem_rows()
                if rows and max(d["turn"] for d in rows) > turn0:
                    advanced = True
                    break
            s.log(f"press {presses}: advanced={advanced}")
            if not advanced:
                s.close_eventwin()
        if not advanced:
            s.log("NEGATIVE: could not advance one turn")
            return 1
        s.drain_popups()
        if not s.close_eventwin():
            s.log("NEGATIVE: post-turn EVENTWIN would not close")
            return 1

        rows = s.ring_mem_rows()
        recs0 = rows[-1]["recs"]
        cand = [int(k) for k, v in recs0.items()
                if v["owner"] == 0 and v["kind"] == 4 and v["moves"] > 0]
        s.log(f"post-turn t={rows[-1]['turn']} owner0 n={len(recs0)} "
              f"kinds={sorted(set(v['kind'] for v in recs0.values()))} "
              f"cand(kind4,moves>0)={cand}")

        # ---- battery over fleet-row system views ----
        seen_systems = set()
        for vi in range(args.views):
            page = 1 + vi // 4
            ry = FLEET_ROWS[vi % 4]
            im, d = s.open_fleet()
            if im is None:
                s.log(f"view {vi}: FLEET would not open (diff {d})")
                continue
            for _pg in range(page - 1):
                s.click(620, 453, f"page{vi}_{_pg}", wait=2.0)
            if not s.click(200, ry, f"rowjump{vi}", wait=3.0):
                continue
            sys_im = s.grab(f"view{vi}_r{ry}")
            star = ""
            p = s.newest_sav()
            if p:
                m2 = s.read_mem(p)
                B2 = SL.base_of(m2, s.anch) if m2 else None
                if B2:
                    star = s.star_name_at(
                        m2, struct.unpack_from(
                            "<I", m2, B2 + SL.OFF + 0x43504)[0])
            sprites = s.ship_sprites(sys_im) if sys_im is not None else []
            planet = s.planet_point(sys_im) if sys_im is not None else None
            emp = (s.empty_point(sys_im, [(x, y) for x, y, _ in sprites] +
                                 ([planet] if planet else []))
                   if sys_im is not None else None)
            s.log(f"view {vi} page{page} row{ry}: star={star!r} "
                  f"sprites={sprites[:4]} planet={planet} empty={emp}")
            targets = [(x, y, "sprite") for x, y, _ in sprites[:2]]
            if planet:
                targets.append((planet[0], planet[1], "planet"))
            if emp:
                targets.append((emp[0], emp[1], "empty"))
            for (cx, cy, kindlbl) in targets[:args.clicks_per_view]:
                tag = f"r{ry}/{kindlbl}_{cx}x{cy}"
                s.pty_new()
                if not s.click(cx, cy, tag):
                    break
                st = s.poll_stop(tag, budget=22.0)
                if st is None:
                    st = s.check_stopped_oracle(tag)
                if st is None:
                    s.log(f"NOFIRE {tag}")
                    s.probes.append({"tag": tag, "nofire": True})
            # t301 AUDIT: the old TOGGRID "control click" at (572,418) was
            # INVALID — pixel census of 23_view0_r93.png shows rect
            # 557,403-587,433 is BLACK (uniq=2, mean~0) in the Icarus view;
            # windows.txt child rects belong to BOTH sibling windows
            # (COSMOSWnd TOGSHIPS and BatModeWnd TOGGRID share the rect) and
            # neither is painted there. DEFAULT IS NOW 0. The session carries
            # a BUILT-IN positive control instead: the End-Turn and FLEET
            # clicks happen while btn_entry/btn_hdlr (type-0 class 0x247cb8)
            # + router 0x30d08 are armed, and those clicks are PROVEN to work
            # (t300) — if they don't fire, the instrument is dead, full stop.
            if vi == 0 and args.control_click:
                s.pty_new()
                if s.click(572, 418, "TOGGRID_control"):
                    st = s.poll_stop("TOGGRID_control", budget=22.0)
                    if st is None:
                        s.log("NOFIRE TOGGRID_control")
                        s.probes.append({"tag": "TOGGRID_control",
                                         "nofire": True})
                    s.persist()
            s.persist()
            if star in seen_systems:
                s.log(f"view {vi}: system {star!r} already covered — stop loop")
                break
            seen_systems.add(star)
            for k in range(3):
                imx = s.grab(f"esc{vi}_{k}")
                if imx is None:
                    break
                if s.orange_frac(imx) > 0.20:
                    s.log("TITLE visible during escape — STOP (t285)")
                    s.persist()
                    return 1 if not s.hits else 0
                rails = s.fleet_open(imx)
                if rails == 0:
                    break
                s.send(["key", "Escape"])
                time.sleep(2.0)
        s.persist()
        rc = 0 if s.hits else 1
        s.log(f"SESSION END rc={rc} hits={len(s.hits)} "
              f"legs={sorted(set(h['leg'] for h in s.hits))}")
        return rc
    finally:
        try:
            s.req("EXEC BPDEL *", 5.0)
        except Exception:
            pass
        try:
            os.kill(s.child.pid, signal.SIGKILL)
            s.log(f"[teardown] SIGKILL dosbox pid={s.child.pid}")
        except Exception:
            pass
        time.sleep(1.0)
        if getattr(s, "xv", None):
            try:
                os.kill(s.xv.pid, signal.SIGKILL)
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
