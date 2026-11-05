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
        "batmode_dead": 0x1AEF8,  # BatModeWnd INACTIVE in system view (record
                                      # 0xfdc924 +0xac state); control only
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
        "s2_54a83": 0x54A83}

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
            self.leg_pats.append(re.compile(
                rf"(?<![0-9A-Fa-f]){lin & 0xFFFFFF:06X} [0-9A-F]", re.I))
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
            eb = self.dump_mem(esp, 8, f"{tag}_esp")
            if eb and len(eb) >= 8:
                r0, r1 = struct.unpack_from("<II", eb, 0)
                rec["ret_stack"] = {"esp": hx(esp), "ret0": hx(r0),
                                    "ret1": hx(r1),
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
        while time.time() < t_end and len(recs) < 6:
            txt = self.pty_new()
            if txt and self.leg_pats and any(p.search(txt)
                                             for p in self.leg_pats):
                time.sleep(1.5)
                self.pty_new()          # settle the code view (t302 form)
                recs.append(self.bank_stop(f"{tag}#{len(recs)}"))
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
                pat = re.compile(rf"(?<![0-9A-Fa-f]){lin & 0xFFFFFF:06X} "
                                 r"[0-9A-F]", re.I)
                pty_census[name] = len(pat.findall(whole))
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
            # SHORT baseline: the 0x3b pump guarantees a fire storm there; the
            # whole-log pty census counts them all anyway. The banked baseline
            # just names the pump msg-id for the CURRENT window set.
            census["baseline"] = s.census_click(
                None, None, "baseline", 15)
            im, d = s.open_fleet()
            if im is None:
                s.log(f"CENSUS: FLEET would not open (diff {d}) — clicking "
                      f"current screen targets only")
            else:
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
            for (cx, cy, kindlbl) in targets[:args.clicks_per_view]:
                census[kindlbl] = s.census_click(
                    cx, cy, f"{kindlbl}_{cx}x{cy}", args.window)
            # POSITIVE CONTROL inside the dispatch-site instrument: NEXTTURN's
            # dispatch is windows.txt VERBATIM msg 7 (t302 btn_hdlr witness) —
            # if msg 7 + name NEXTTURN appears at a disp site, the census
            # attribution law holds. (Advances the turn: allowed on scratch.)
            census["control_nextturn"] = s.census_click(
                R293.NEXTTURN[0], R293.NEXTTURN[1], "control_nextturn",
                args.window)
            # WHOLE-LOG pty census (catches any stop poll_stop/census_window
            # missed between cycles; same fire-pattern law as arm_all)
            whole = open(s.ptylog, "rb").read().decode("utf-8", "replace")
            pty_census = {}
            for name in s.legs:
                lin = P0 + LEGS[name]
                pat = re.compile(rf"(?<![0-9A-Fa-f]){lin & 0xFFFFFF:06X} "
                                 r"[0-9A-F]", re.I)
                pty_census[name] = len(pat.findall(whole))
            s.log(f"PTY WHOLE-LOG CENSUS {pty_census}")
            s.probes.append({"probe": "pty-whole-log-census",
                             "counts": pty_census})
            s.persist()
            with open(op.join(s.out, "census.json"), "w") as fh:
                json.dump({"window_s": args.window, "star": star,
                           "targets": census, "pty": pty_census},
                          fh, indent=1)
            measured = [k for k, v in census.items()
                        if k not in ("baseline",) and v]
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
