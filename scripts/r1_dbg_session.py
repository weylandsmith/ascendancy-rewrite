#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_dbg_session.py — t327 DEBUGGER-SESSION TOOL v2.

One command = one leg-witness capture session with declarative legs, phase
choreography, whole-log pty census, expectation verdict, and bank-on-exit.
Compresses every future DAT-writer hunt to 1-2 sessions (STATE.md t327).

This tool does NOT re-derive any instrument law. It composes the proven
machinery of scripts/r299_leg_session.py (imported as L): the FirePat
detector, the r299 launch shape (dbg binary + pty stdio + MCP out-dial +
core=normal conf), arm_census/disarm_run/census_click/census_window,
bank_stop and the t302 resume protocol, the r322 relaunch-loop semantics.

LAWS BAKED IN (all measured; do not re-litigate — docs/re/dosbox-debugger.md):
  1. t305 NORMAL-CORE RENDER LAW: a stop renders as the ONE line prefixed by
     PAIR_BLACK_GREEN (debug.cpp:1586-87); the address token is a SUFFIX of
     the 6-hex linear EIP with leading zeros STRIPPED, so detection goes
     through FirePat (capture token, sig6.endswith(tok), len>=4). Attribution
     is ALWAYS EV-eip-exact via bank_stop; the grep only triggers "something
     stopped" + feeds the whole-log census.
  2. t304 CORE-CONF LAW: core=normal MUST be under [cpu] (launch() writes the
     canonical conf; the pty 'Single-stepping...' warning is ground truth).
  3. MEMREAD IS REAL-MODE-ONLY (debug.cpp:2983-84) — for in-game values the
     RING (.sav autosaves) is the read surface, not EXEC MEMREAD; memory
     dumps at stops go through MEMDUMPBIN CS: (paging off, linear==physical;
     filenames bare+relative, length HEX, output name UPPERCASED).
  4. t290 xsend LAW: xsend's arg1 is the WINDOW TITLE ("DOSBox-X"), not the
     display; DISPLAY is an env var (inherited from Sess.send).
  5. t302 RESUME LAW: a fired code BP stays armed under C_HEAVY_DEBUG;
     resuming with it re-stops at the same EIP and FREEZES the guest. All
     resumes go through L.Sess.resume_and_rearm (BPDEL fired idx -> RUN ->
     autosave/refire liveness proof -> BREAK -> re-arm un-witnessed).
  6. t303 CENSUS-SAFETY LAW: never arm across choreography you are not
     polling; between measured clicks the guest runs LEG-FREE. Banked-stop
     cap per window stays 6; the whole-log pty census counts the rest.
  7. BANK-ON-EXIT: census.json / verdict.json / probes.json are persisted on
     every census_click, at session end, AND via atexit (SIGKILL teardown by
     RECORDED PID only — t325 SIGNAL LAW: SIGTERM pops the vendor
     quit-confirm, never use it here).
  8. t325 CENSUS LAW: slot byte +3 is NOT a progress value — watch whole
     dwords (applies to any ring oracle you add).
  9. FirePat UNIQUENESS: the last-4 hex of armed leg linear addresses must be
     pairwise unique (t305 audit law) — enforced at legset build time here.

EXIT CODES (GOAL.txt R1): 0 = every expectation met; 1 = session ran but an
expectation failed / measurement negative (relaunch loop may retry);
2 = harness error (NEVER retry — fix the tool).

USAGE
  live : python3 scripts/r1_dbg_session.py --tag tNNN \
           --legs w43504_28ec2,btn_hdlr --phases baseline,star6,hold \
           --expect 'w43504_28ec2>=1' --expect 'btn_hdlr>=1' \
           --expect-ret0 'btn_hdlr@0x3177d' [--attempts 2] [--window 60]
         (phases: baseline | starN | hold | preturn ; leg names come from
          the LEGSPEC below or any name in r299_leg_session.LEGS)
  offline: python3 scripts/r1_dbg_session.py --offline RUN_DIR \
           [--expect 's2_56cda==106' ...]
         replays the whole-log FirePat census against a RECORDED run's
         mcp-pty.log (legs auto-taken from that run's census line) and
         validates expectations. Also the mutation-test surface: a bogus leg
         must classify 0 fires and exit cleanly (rc 1 with FAIL, no crash).

VERIFIED POSITIVES (t327, this session):
  offline t308 run work/r1/t299-leg-20261105-140250 -> 9/9 counts reproduce
  (w43504_28ec2 1, btn_hdlr 8, six zero-legs 0); run 143815 -> 1/3.
  offline t319 run work/r1/t299-leg-20261106-030727 -> 5/5 counts reproduce
  (pump_entry_56b5c 1, p54a47 0, p54a88 1, s2_56c74 1, s2_56cda 106) and the
  poster callsite ret0=0x54aca (= post call 0x54ac5 + 5) is found in hits.
  mutation: legs at 0xDEAD0/0xABCDEF/0x123456 -> 0 fires, clean exit.
  live: see docs/re/dosbox-debugger.md §TOOL v2 for the live launch result.
"""
import argparse
import atexit
import json
import os
import os.path as op
import re
import signal
import signal as SIG
import struct
import socket
import sys
import time

HERE = op.dirname(op.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = op.dirname(HERE)

import r1_slot as SL                                          # noqa: E402
import r299_leg_session as L                                  # noqa: E402

P0 = L.P0
LEGS = L.LEGS

# --------------------------------------------------------------------------
# LEGSPEC: declarative leg metadata {addr (file offset), expect-callsite,
# hot}. Addresses ARE the r299 LEGS table (single source of truth); this map
# only adds per-leg session metadata. `callsite` = the file offset of the
# call/post whose return address lands at [esp] when this leg stops
# (bank_stop stores ret0_file_off = callsite + 5 for E8 calls).
# --------------------------------------------------------------------------
LEGSPEC = {
    "w43504_28ec2":  {"hot": False, "why": "DAT_43504 star-select store "
                     "(t308 CLOSED: fn 0x28e70 publisher, fires 3/3 on an "
                     "ENTERED galaxy-map star click)"},
    "btn_hdlr":      {"hot": False, "callsite": 0x31778,
                      "why": "type-0 button handler 0x336b4; banked stops "
                     "ret0=0x3177d (star clicks) / 0x56cdd (NEXTTURN) "
                     "[t308 runs 140250/143815 hits.json]"},
    "pump_entry_56b5c": {"hot": False, "callsite": 0x54ac5,
                         "why": "broadcast-pump entry; msg-4 road caller "
                     "0x54ac5 -> banked ret0_file_off 0x54aca, edx=4 "
                     "[t319 run 030727 hits.json]"},
    "p54a47":        {"hot": False, "why": "ds:0x484a4-EQUAL road (t319)"},
    "p54a88":        {"hot": False, "why": "cmp edi,[esi+0x24da4] gate (t319)"},
    "s2_56c74":      {"hot": False, "why": "pump dispatch dispatch-site "
                     "(COLD 2x-confirmed t318/t319)"},
    "s2_56cda":      {"hot": True,  "why": "HOT pump leg (~1/s msg 0x3b "
                     "family; storm-capped at 6 banked stops)"},
    "cos_hdlr":      {"hot": True,  "why": "COSMOSWnd msg handler, hot"},
    # t346 INPUT-PUMP WRITER legs (docs/re/_wip_t346.md S1 static census;
    # closes the t288 honest negative "writer EIP still unwitnessed"):
    "w484c4_2a91d":  {"hot": False, "why": "DOSBox event-record demux "
                      "keyboard arm fn 0x2a838: mov WORD ds:0x484c4,dx "
                      "(dx=WORD[rec+0xc]); char store 0x2a911 precedes"},
    "w484c4_2a72a":  {"hot": False, "why": "INT16h AH=0 drain arm fn "
                      "0x2a5f0: mov ds:0x484c4,ax (ax=scan code, sar 8); "
                      "fires only when the DOS key buffer is non-empty"},
    "c484c4_54928":  {"hot": False, "why": "pump CLEAR fn 0x54650: mov "
                      "ds:0x484c4,0 gated msg==0x19 + [esi+0x48aa]==-1 "
                      "(consumption witness)"},
}


def spec(name):
    return LEGSPEC.get(name, {"hot": False})


# --------------------------------------------------------------------------
# expectation grammar:  "LEG==N" | "LEG>=N" | "LEG@0xRET0FILEOFF"
# --------------------------------------------------------------------------
def parse_expects(pats):
    out = []
    for p in pats or []:
        m = re.match(r"^([A-Za-z0-9_]+)\s*(==|>=)\s*(\d+)$", p)
        if m:
            out.append({"kind": "count", "leg": m.group(1), "op": m.group(2),
                        "n": int(m.group(3)), "text": p})
            continue
        m = re.match(r"^([A-Za-z0-9_]+)@\s*(0[xX][0-9A-Fa-f]+)$", p)
        if m:
            out.append({"kind": "ret0", "leg": m.group(1),
                        "addr": int(m.group(2), 16), "text": p})
            continue
        print(f"HARNESS ERROR: unparsable expectation {p!r}")
        sys.exit(2)
    return out


# --------------------------------------------------------------------------
# Session class: r299 machinery + generic phases + verdict + bank-on-exit.
# --------------------------------------------------------------------------
class Args:
    disp: str
    port: int
    tl: int
    settle: int
    boot: int


class DbgSession:
    def __init__(self, tag, legs, phases, window, disp, port, tl, settle,
                 star_max, out_prefix="dbg"):
        self.tag = tag
        self.legs = legs
        self.phases = phases
        self.window = window
        self.star_max = star_max
        a = Args()
        a.disp, a.port, a.tl, a.settle = disp, port, tl, settle
        a.boot = 170
        self.s = L.Sess(a)
        # re-home the run dir under the tool's own name
        new_out = op.join(ROOT, "work/r1",
                          f"{out_prefix}-{tag}-{time.strftime('%Y%m%d-%H%M%S')}")
        if op.isdir(self.s.out):
            os.rmdir(op.join(self.s.out, "save"))
            os.rmdir(self.s.out)
        self.s.out = new_out
        os.makedirs(op.join(new_out, "save"), exist_ok=True)
        self.s.savedir = op.join(new_out, "save")
        self.s.logp = op.join(new_out, "session.log")
        self.s.dbl = op.join(new_out, "dosbox.out")
        self.s.ptylog = op.join(new_out, "mcp-pty.log")
        self.s.transcript = op.join(new_out, "mcp-transcript.txt")
        self.census = {}
        self.oracle = {}
        self.verdict = None
        self.keys = ["c", "1"]          # t346 keys-phase key list
        atexit.register(self.bank_on_exit)

    def bank_on_exit(self):
        try:
            self.s.persist()
            with open(op.join(self.s.out, "census.json"), "w") as fh:
                json.dump({"tag": self.tag, "pty_census": self.census,
                           "phases": list(self.census)}, fh, indent=1)
            if self.verdict is not None:
                with open(op.join(self.s.out, "verdict.json"), "w") as fh:
                    json.dump(self.verdict, fh, indent=1)
        except Exception:
            pass

    # ---- oracle: ring-surface reads ONLY (law 3) ----
    def sel_oracle(self, tag):
        s = self.s
        try:
            p = s.newest_sav()
            if not p:
                return None
            mm = s.read_mem(p)
            bb = SL.base_of(mm, s.anch) if mm else None
            if not bb:
                return None
            rd = lambda X: struct.unpack_from("<I", mm, bb + SL.OFF + X)[0]
            v = rd(0x43504)
            o = {"tag": tag, "sav": op.basename(p), "turn": rd(0x12e10),
                 "DAT_43504": hex(v), "DAT_43504_name": s.star_name_at(mm, v),
                 "DAT_43508": hex(rd(0x43508))}
            s.log(f"ORACLE {tag} {o}")
            return o
        except Exception as e:
            s.log(f"ORACLE {tag} error {e!r}")
            return None

    # ---- phase: green-annulus star battery (t308 pip law, verbatim) ----
    def star_candidates(self, map_im0):
        px = map_im0.load()
        GREENS = {(0, 85, 40), (0, 113, 56), (0, 142, 69)}
        gp = [(x, y) for y in range(60, 440)
              for x in range(40, 456) if px[x, y] in GREENS]
        gpset = set(gp)
        seen, cands = set(), []
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
            if d_ic < 50:          # exclude Icarus's own pip (t308b law)
                continue
            cands.append((d_ic, mx, my))
        cands.sort()
        return cands

    def phase_star(self, n):
        s = self.s
        map_im0 = s.grab("map_pre_star")
        cands = self.star_candidates(map_im0) if map_im0 is not None else []
        s.log(f"STAR-PHASE: {len(cands)} candidates nearest={cands[:3]}")
        tried, out = [], {}
        for i in range(min(n, self.star_max)):
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
            ob = self.sel_oracle(f"star{i}_before")
            recs = s.census_click(xx, yy, f"star{i}_{xx}x{yy}", self.window)
            im_a = s.grab(f"star{i}_screen")
            dv = s.diff_px(map_im0, im_a) if im_a is not None else -1
            entered = dv > 15000
            oa = self.sel_oracle(f"star{i}_after")
            delta = bool(entered and ob and oa
                         and ob.get("DAT_43504") != oa.get("DAT_43504"))
            out[f"star{i}"] = {"click": [xx, yy], "screen_diff": dv,
                               "entered": entered, "dat43504_delta": delta,
                               "stops": 0 if recs is None else len(recs)}
            s.log(f"STAR-PHASE {i}: ({xx},{yy}) diff={dv} entered={entered} "
                  f"delta={delta}")
            if entered:
                if not s.escape_to_map(map_im0):
                    s.log("STAR-PHASE: escape_to_map FAILED — skipping rest")
                    break
                if delta:
                    s.log(f"WITNESS DELTA at star{i}: {ob['DAT_43504']}"
                          f"({ob['DAT_43504_name']}) -> {oa['DAT_43504']}"
                          f"({oa['DAT_43504_name']}) — pip loop stopped")
                    break
        return out

    def run_phases(self):
        s = self.s
        results = {}
        for ph in self.phases:
            if ph == "baseline":
                results["baseline"] = s.census_click(
                    None, None, "baseline", 15)
            elif ph == "hold":
                results["hold"] = s.census_click(None, None, "hold",
                                                 self.window)
            elif ph == "preturn":
                ob = self.sel_oracle("preturn_before")
                s.click(L.R293.NEXTTURN[0], L.R293.NEXTTURN[1], "preturn",
                        wait=6.0)
                self.sel_oracle("preturn_after")
                results["preturn"] = {"turn_before":
                                      (ob or {}).get("turn")}
            elif ph == "keys":
                # t346 INPUT-PUMP WITNESS (t311 digit-phase shape verbatim:
                # close_eventwin -> bare-map assert -> arm -> RUN -> popup
                # re-guard -> send keys -> census window -> disarm). NO
                # Escape (t285 self-harm law: Escape at the bare map exits
                # the campaign).
                keys = getattr(self, "keys", ["c", "1"])
                if not s.close_eventwin():
                    s.log("KEYS: close_eventwin failed — skipped")
                    results["keys"] = {"skipped": "close_eventwin"}
                    continue
                if not s.assert_on_map("keys_prearm"):
                    s.log("KEYS: not on bare map — skipped (title guard)")
                    results["keys"] = {"skipped": "not_on_map"}
                    continue
                if not s.arm_census(self.legs):
                    s.log("KEYS: ARM FAILED — keys not measured")
                    results["keys"] = {"skipped": "arm"}
                    continue
                lines, ok, hdr = s.req("EXEC RUN", 20.0)
                s.log(f"KEYS: armed RUN hdr={hdr} keys={keys}")
                im_rg = s.grab("keys_reguard")
                if im_rg is not None and s.eventwin_open(im_rg):
                    s.log("KEYS: POPUP REGUARD — popup open at arm; RUN "
                          "resumed, keys NOT pressed")
                    s.req("EXEC RUN", 20.0)
                    results["keys"] = {"skipped": "reguard"}
                else:
                    for k in keys:
                        s.send(["key", k])
                        time.sleep(0.4)
                    results["keys"] = s.census_window("keys", self.window)
                s.disarm_run("keys")
                s.persist()
            elif re.match(r"^star\d+$", ph):
                results[ph] = self.phase_star(int(ph[4:]))
            else:
                self.s.log(f"HARNESS ERROR: unknown phase {ph!r}")
                return None
        return results

    # ---- whole-log pty census (the authoritative fire counter) ----
    def whole_log_census(self):
        whole = open(self.s.ptylog, "rb").read().decode("utf-8", "replace")
        self.census = {name: len([m for pt in L.fire_pats(P0 + LEGS[name])
                                  for m in pt.findall(whole)])
                       for name in self.legs}
        self.s.log(f"PTY WHOLE-LOG CENSUS {self.census}")
        self.s.probes.append({"probe": "pty-whole-log-census",
                              "counts": self.census})
        with open(op.join(self.s.out, "census.json"), "w") as fh:
            json.dump({"tag": self.tag, "pty_census": self.census}, fh,
                      indent=1)
        return self.census

    # ---- verdict ----
    def grade(self, expects):
        hits = self.s.hits
        checks = []
        for e in expects:
            if e["kind"] == "count":
                got = self.census.get(e["leg"])
                ok = got is not None and (got == e["n"] if e["op"] == "=="
                                          else got >= e["n"])
                checks.append({**e, "got": got, "ok": bool(ok)})
            else:
                want = e["addr"]
                got = None
                for h in hits:
                    if h.get("leg") != e["leg"]:
                        continue
                    r0 = (h.get("ret_stack") or {}).get("ret0_file_off")
                    if r0 and int(r0, 16) == want:
                        got = {"tag": h.get("tag"), "ret0": r0}
                        break
                checks.append({**e, "got": got, "ok": got is not None})
        all_ok = bool(checks) and all(c["ok"] for c in checks)
        self.verdict = {"tag": self.tag, "pass": all_ok, "checks": checks,
                        "census": self.census,
                        "banked_stops": len(hits)}
        with open(op.join(self.s.out, "verdict.json"), "w") as fh:
            json.dump(self.verdict, fh, indent=1)
        self.s.log("VERDICT " + ("PASS" if all_ok else "FAIL") + " "
                   + json.dumps(checks))
        return all_ok

    # ---- teardown: SIGKILL RECORDED PIDs only (law 7) ----
    def teardown(self):
        for who, p in (("dosbox", getattr(self.s, "child", None)),
                       ("xvfb", getattr(self.s, "xv", None))):
            if p is None:
                continue
            try:
                os.kill(p.pid, SIG.SIGKILL)
                self.s.log(f"[teardown] SIGKILL {who} pid={p.pid}")
            except Exception:
                pass
            # t344 FIX: a SIGKILLed Xvfb leaves /tmp/.X<disp>-lock + socket
            # behind, and every later attempt on the same display dies with
            # "Server is already active for display" (t344c att2). Remove
            # ONLY when the lock contents == the pid we just killed.
            if who == "xvfb":
                disp = getattr(self.s, "disp", None)
                if disp is not None:
                    disp = str(disp).lstrip(":")
                    lock = f"/tmp/.X{disp}-lock"
                    try:
                        with open(lock) as fh:
                            owner = int(fh.read().strip())
                        if owner == p.pid:
                            os.remove(lock)
                            sock = f"/tmp/.X11-unix/X{disp}"
                            if op.exists(sock):
                                os.remove(sock)
                            self.s.log(f"[teardown] removed stale X{disp} "
                                       f"lock+socket (owner==killed pid)")
                    except Exception:
                        pass
        try:
            self.s.ls.close()
        except Exception:
            pass


def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk:
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sk.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def preflight(legs):
    """rc=2 conditions: unknown leg, last-4 collision (law 9), missing
    artifacts, game/ mount."""
    for l in legs:
        if l not in LEGS:
            print(f"HARNESS ERROR: unknown leg {l!r}")
            return 2
    tok = {}
    for l in legs:
        t = f"{(P0 + LEGS[l]) & 0xFFFFFF:06X}"[-4:]
        if t in tok:
            print(f"HARNESS ERROR: last-4 FirePat collision {l} vs "
                  f"{tok[t]} (t305 audit law)")
            return 2
        tok[t] = l
    for p, why in ((L.DBG_BIN, "debugger binary"),
                   (L.R293.SCRATCH, "scratch"), (L.R293.PAYLOAD, "payload"),
                   (L.R293.OCT29, "Oct-29 backup")):
        if not op.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if op.abspath(L.R293.SCRATCH).startswith(op.join(ROOT, "game") + op.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    import hashlib
    if (hashlib.md5(open(L.R293.OCT29, "rb").read()).hexdigest()
            != L.R293.OCT29_MD5):
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2
    pay = open(L.R293.PAYLOAD, "rb").read()
    for l in legs:
        off = LEGS[l]
        print(f"LEG {l:16s} file {off:#07x} linear {P0+off:#08x} "
              f"bytes {pay[off:off+10].hex(' ')}")
    return 0


def live_attempt(tag, legs, phases, window, disp, port, tl, settle, star_max,
                 keys=None):
    ds = DbgSession(tag, legs, phases, window, disp, port, tl, settle,
                    star_max)
    if keys:
        ds.keys = keys
    s = ds.s
    rc = 1
    try:
        s.log(f"t327 dbg-session v2 start out={s.out} legs={legs} "
              f"phases={phases} window={window}")
        s.launch()
        conn = s.connect()
        if conn is None:
            s.log("NEGATIVE: no MCP connection")
            return 1
        lines, ok, hdr = s.req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            s.log("NEGATIVE: no PONG")
            return 1
        s.log(f"settling {settle}s before BREAK")
        time.sleep(settle)
        if not s.do_break():
            s.log("NEGATIVE: BREAK lottery lost — relaunch")
            return 1
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"post-lottery RUN hdr={hdr}")
        s.pty_new()
        if not s.wait_title():
            s.log("NEGATIVE: title never appeared")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed")
            return 1
        time.sleep(settle)
        closed = s.drain_popups()
        s.log(f"post-load drain closed {closed}")
        rows = s.ring_mem_rows()
        if not rows or not rows[-1].get("recs"):
            s.log("NEGATIVE: ring has no ship records")
            return 1
        mem = s.read_mem(rows[-1]["path"])
        B = SL.base_of(mem, s.anch)
        s.log(f"ring base B={hex(B) if B else None} "
              f"(expect {hex(L.EXPECT_BASE)})")
        if B != L.EXPECT_BASE:
            s.log("NEGATIVE: base mismatch — armed addresses invalid")
            return 1
        s.legs = legs
        s.census = True
        s.pay = open(L.R293.PAYLOAD, "rb").read()
        ph_res = ds.run_phases()
        if ph_res is None:
            return 2
        s.probes.append({"probe": "phases", "result": {
            k: (v if isinstance(v, dict) else
                (0 if v is None else len(v))) for k, v in ph_res.items()}})
        ds.whole_log_census()
        return 0
    finally:
        ds.teardown()


def offline_run(run_dir, expects, extra_legs):
    """Replay the whole-log census against a RECORDED run (no launch)."""
    pty = op.join(run_dir, "mcp-pty.log")
    logp = op.join(run_dir, "session.log")
    if not op.exists(pty):
        print(f"HARNESS ERROR: no mcp-pty.log in {run_dir}")
        return 2
    legs = list(extra_legs)
    recorded = None
    if op.exists(logp):
        m = re.search(r"PTY WHOLE-LOG CENSUS (\{.*\})",
                      open(logp).read())
        if m:
            recorded = eval(m.group(1), {"__builtins__": {}})
            legs = list(dict.fromkeys(legs + list(recorded)))
    if not legs:
        print("HARNESS ERROR: no legs (census line absent and no --legs)")
        return 2
    whole = open(pty, "rb").read().decode("utf-8", "replace")
    counts = {}
    for name in legs:
        if name not in LEGS:
            print(f"LEG {name}: UNKNOWN NAME (not in r299 LEGS) — counting "
                  f"by raw address is not supported; classify as 0")
            counts[name] = 0
            continue
        counts[name] = len([m for pt in L.fire_pats(P0 + LEGS[name])
                            for m in pt.findall(whole)])
    print("OFFLINE CENSUS " + json.dumps(counts))
    if recorded is not None:
        drift = {k: (recorded.get(k), counts.get(k)) for k in recorded
                 if recorded.get(k) != counts.get(k)}
        print("REPLAY vs RECORDED: "
              + ("EXACT (0 drift)" if not drift else f"DRIFT {drift}"))
    # ret0 expectations read the recorded hits.json
    hits_p = op.join(run_dir, "hits.json")
    hits = json.load(open(hits_p)) if op.exists(hits_p) else []
    checks = []
    for e in expects:
        if e["kind"] == "count":
            got = counts.get(e["leg"])
            ok = got is not None and (got == e["n"] if e["op"] == "=="
                                      else got >= e["n"])
            checks.append({**e, "got": got, "ok": bool(ok)})
        else:
            got = None
            for h in hits:
                if h.get("leg") != e["leg"]:
                    continue
                r0 = (h.get("ret_stack") or {}).get("ret0_file_off")
                if r0 and int(r0, 16) == e["addr"]:
                    got = {"tag": h.get("tag"), "ret0": r0}
                    break
            checks.append({**e, "got": got, "ok": got is not None})
    ok_all = all(c["ok"] for c in checks) if checks else False
    for c in checks:
        print(f"  {'PASS' if c['ok'] else 'FAIL'} {c['text']} got={c['got']}")
    print("OFFLINE VERDICT " + ("PASS" if ok_all else "FAIL"))
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="t327")
    ap.add_argument("--legs", default="")
    ap.add_argument("--phases", default="baseline,star6,hold")
    ap.add_argument("--expect", action="append")
    ap.add_argument("--expect-ret0", action="append")
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--window", type=int, default=60)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55999)
    ap.add_argument("--tl", type=int, default=7200)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--star-max", type=int, default=6)
    ap.add_argument("--keys", default="c,1")  # t346 keys-phase key list
    ap.add_argument("--offline", default=None, metavar="RUN_DIR")
    args = ap.parse_args()

    expects = parse_expects(args.expect) + [
        {"kind": "ret0", "leg": m.group(1), "addr": int(m.group(2), 16),
         "text": p}
        for p in (args.expect_ret0 or [])
        for m in [re.match(r"^([A-Za-z0-9_]+)@\s*(0[xX][0-9A-Fa-f]+)$", p)]
        if m]

    if args.offline:
        extra = [l.strip() for l in args.legs.split(",") if l.strip()]
        return offline_run(op.abspath(args.offline), expects, extra)

    legs = [l.strip() for l in args.legs.split(",") if l.strip()]
    if not legs:
        print("HARNESS ERROR: live mode needs --legs")
        return 2
    rc = preflight(legs)
    if rc:
        return rc
    if not port_free(args.port):
        print(f"HARNESS ERROR: MCP port {args.port} busy")
        return 2
    phases = [p.strip() for p in args.phases.split(",") if p.strip()]

    # r322 relaunch law: rc=0 + census measured => stop; rc=2 => NEVER retry;
    # rc=1 => retry up to --attempts (BREAK lottery is per-attempt, t286 law).
    final = 1
    for i in range(1, args.attempts + 1):
        print(f"=== ATTEMPT {i} {time.strftime('%H:%M:%S')} ===", flush=True)
        rc = live_attempt(args.tag, legs, phases, args.window, args.disp,
                          args.port, args.tl, args.settle, args.star_max,
                          keys=[k.strip() for k in args.keys.split(",")
                                if k.strip()])
        run = None
        # find the newest dbg-<tag>- dir for this attempt
        cands = sorted((d for d in os.listdir(op.join(ROOT, "work/r1"))
                        if d.startswith(f"dbg-{args.tag}-")), reverse=True)
        run = op.join(ROOT, "work/r1", cands[0]) if cands else None
        print(f"attempt {i} rc={rc} run={run}", flush=True)
        if rc == 2:
            print("ATTEMPT harness error — NOT retrying (fix the tool)")
            return 2
        if rc == 0 and run:
            vp = op.join(run, "verdict.json")
            # live_attempt leaves verdict grading to grade(); do it here so
            # the loop owns the expectation check
            ds_grade = grade_from_run(run, expects)
            print(f"attempt {i} verdict pass={ds_grade}")
            if ds_grade:
                final = 0
                break
        final = 1
    return final


def grade_from_run(run, expects):
    hits_p = op.join(run, "hits.json")
    cen_p = op.join(run, "census.json")
    if not op.exists(cen_p):
        return False
    census = json.load(open(cen_p))["pty_census"]
    hits = json.load(open(hits_p)) if op.exists(hits_p) else []
    checks = []
    for e in expects:
        if e["kind"] == "count":
            got = census.get(e["leg"])
            ok = got is not None and (got == e["n"] if e["op"] == "=="
                                      else got >= e["n"])
            checks.append({**e, "got": got, "ok": bool(ok)})
        else:
            got = None
            for h in hits:
                if h.get("leg") != e["leg"]:
                    continue
                r0 = (h.get("ret_stack") or {}).get("ret0_file_off")
                if r0 and int(r0, 16) == e["addr"]:
                    got = {"tag": h.get("tag"), "ret0": r0}
                    break
            checks.append({**e, "got": got, "ok": got is not None})
    ok_all = bool(checks) and all(c["ok"] for c in checks)
    with open(op.join(run, "verdict.json"), "w") as fh:
        json.dump({"pass": ok_all, "checks": checks, "census": census,
                   "banked_stops": len(hits)}, fh, indent=1)
    for c in checks:
        print(f"  {'PASS' if c['ok'] else 'FAIL'} {c['text']} got={c['got']}")
    return ok_all


if __name__ == "__main__":
    sys.exit(main())
