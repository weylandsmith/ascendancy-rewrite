#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t434b: FLEET ROW-ART IDENTITY VIA LIVE BLIT ARGS (docs/re/_wip_t434b.md F3/F4).

Question (t434 F5 residual): fn 0x50d12 paints each ships-screen row and
blits a per-ship render at the row left. WHICH library/record is it, and what
is the origin law? Static account (F4, cited): push order 0x50d39..0x50d49 =
cdecl (y=0x32, x=0x41, sel=BYTE_HI([ship+0xa7]), p2=FUN_0001fc34(cache
0x9f10c, slot WORD ds:0x895c2), p1=ebp). t434's "0x41=65 cannot exist in a
4-record lib" was an x-coordinate misread — the selector is DYNAMIC.

LEGS (file offsets; linear = P0+off, P0=0x1BF450 deterministic base):
  fc34_art  0x50D34  cache-fetch pre-call: eax (cache ptr), edx (slot word).
  art_blit  0x50D49  call 0x5caac pre-call map [esp]=p1 struct,[+4]=p2
                     payload,[+8]=sel,[+c]=x,[+10]=y (t330 law). Dump struct
                     head, payload head ("1.10" magic), dir entry p2+8+8*sel,
                     record body (dims law shp.md S16/S17), and ONCE a full
                     0x4000-byte payload copy for OFFLINE byte-identity match
                     against extracted/*/*/smship??.shp (identity by CONTENT,
                     never by filename — R-t434 premise honored).
                     E6 origin law (5caac.c:58-64):
                       x = arg_x + struct[+4] + s32[rec+8]
                       y = arg_y + struct[+8] + s32[rec+0xc]
  sprf_ctl  0x50DD4  sprintf inside the same first paint leg (0x21a20 name
                     getter chain): positive control that the leg executed.

SAFETY (r428f stack verbatim): scratch game-wp only (preflight asserts); OWN
ring dir; private Xvfb (:97, NEVER production :9); Oct-29 md5-verified
RESUME.GAM; NEVER loadstate; base assert; teardown SIGKILL by RECORDED PID.
Exit 0 = verdict produced (identity or cited negative); 1 = negative; 2 =
harness error (never retry).
"""
import argparse
import json
import os
import os.path as op
import struct
import sys
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r1_slot as SL                                         # noqa: E402
import r299_leg_session as L                                 # noqa: E402
import r1_dbg_session as D                                   # noqa: E402

P0 = D.P0
CODE_END = L.CODE_END
ART_LEGS = {"fc34_art": 0x50D34, "art_blit": 0x50D49, "sprf_ctl": 0x50DD4}
L.LEGS.update(ART_LEGS)          # single source of truth (r330 law)
ALL_LEGS = ["fc34_art", "art_blit", "sprf_ctl"]

SHIPS_BTN = (553, 184)           # FLEET windows.txt rect 474,169-632,199
                                 # (SENDMESSAGE 1 SENDPARAM1 18; TOGSHIPS
                                 # 557,403 is a DIFFERENT widget — attempt-1
                                 # clicked it, screen never changed, 0 stops)


def hx(v):
    return f"{v:#x}" if isinstance(v, int) else None


def s32(b, o):
    try:
        return struct.unpack_from("<i", b, o)[0]
    except Exception:
        return None


def u32(b, o):
    try:
        return struct.unpack_from("<I", b, o)[0]
    except Exception:
        return None


class ArtSess(D.DbgSession):
    """DbgSession + art-leg attribution + hand-rolled ships-screen census."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.art = []
        self.dump_left = {"fc34_art": 3, "art_blit": 6, "sprf_ctl": 2}
        self.full_dumped = False
        s = self.s
        orig = s.bank_stop

        def bank434b(tag):
            eip = s.read_reg("eip")
            leg = s.attribute(eip) if eip else None
            if leg in ART_LEGS:
                return self._bank_art(tag, eip, leg)
            return orig(tag)

        s.bank_stop = bank434b                    # INSTANCE patch (t330 law)

        # t428f POLL-BY-BREAK law: stock resume_and_rearm's BPDEL * releases a
        # pending halt at the NEXT cold leg unbanked. Break, attribute, bank;
        # legs here are cold (paint-only), no hot-storm risk.
        def census434b(tag, seconds):
            t_end = time.time() + seconds
            recs = []
            while time.time() < t_end and len(recs) < 8:
                if not s.do_break():
                    s.log(f"CENSUS434B {tag}: BREAK lost — ending window")
                    break
                eip = s.read_reg("eip")
                leg = s.attribute(eip) if eip else None
                if leg:
                    recs.append(s.bank_stop(f"{tag}#{len(recs)}"))
                    continue          # bank_stop resumed + re-armed
                lines, ok, hdr = s.req("EXEC RUN", 15.0)
                time.sleep(1.5)
            s.log(f"CENSUS434B {tag}: {len(recs)} stops banked ({seconds:.0f}s)")
            return recs

        s.census_window = census434b

    def bank_on_exit(self):
        super().bank_on_exit()
        try:
            with open(op.join(self.s.out, "art_attrib.json"), "w") as fh:
                json.dump(self.art, fh, indent=1)
        except Exception:
            pass

    def _bank_art(self, tag, eip, leg):
        s = self.s
        regs = {"eip": eip}
        for r in ("eax", "ebx", "ecx", "edx", "esp"):
            v = s.read_reg(r)
            if v is None:
                break
            regs[r] = v
        rec = {"tag": tag, "wall": time.strftime("%H:%M:%S"), "leg": leg,
               "eip_file_off": hx(eip - P0) if eip and eip > P0 else None,
               "regs": {k: hx(v) for k, v in regs.items()}}
        info = {}
        if self.dump_left.get(leg, 0) > 0:
            self.dump_left[leg] -= 1
            if leg == "fc34_art":
                info["cache_ptr"] = hx(regs.get("eax"))
                info["slot_word"] = regs.get("edx")
            elif leg == "art_blit":
                esp = regs.get("esp")
                if esp and 0x1000 < esp < 0x10000000:
                    eb = s.dump_mem(esp, 0x14, f"artes{tag}")
                    if eb and len(eb) >= 0x14:
                        p1, p2, sel, px, py = struct.unpack_from("<5I", eb, 0)
                        info["esp"] = hx(esp)
                        info["p1"], info["p2"], info["sel"] = hx(p1), hx(p2), sel
                        info["arg_x"], info["arg_y"] = s32(eb, 0xc), s32(eb, 0x10)
                        sb = s.dump_mem(p1, 0x18, f"arts{tag}") if p1 and \
                            0x10000 <= p1 < 0x10000000 else None
                        if sb and len(sb) >= 0x10:
                            info["s_pixptr"] = hx(u32(sb, 0))
                            info["s_w"] = s32(sb, 4)
                            info["s_h"] = s32(sb, 8)
                        if p2 and 0x10000 <= p2 < 0x10000000:
                            ph = s.dump_mem(p2, 0x20, f"artpay{tag}")
                            if ph and len(ph) >= 0x10:
                                info["pay_magic"] = ph[:4].decode(
                                    "latin1", "replace")
                                info["pay_head"] = ph.hex(" ")
                            tb = s.dump_mem(p2 + 8 + 8 * sel, 8,
                                            f"artdir{tag}") \
                                if 0 <= sel < 64 else None
                            if tb and len(tb) >= 8:
                                off = u32(tb, 0)
                                info["dir_off"] = hx(off)
                                eb2 = s.dump_mem(p2 + off, 0x28, f"artrec{tag}") \
                                    if off and 0 < off < 0x800000 else None
                                if eb2 and len(eb2) >= 0x18:
                                    info["rec_head"] = eb2.hex(" ")
                                    info["rec8"] = s32(eb2, 8)
                                    info["recC"] = s32(eb2, 0xC)
                                    info["rec10"] = s32(eb2, 0x10)
                                    info["rec14"] = s32(eb2, 0x14)
                                # ONE full payload copy for offline identity
                                if not self.full_dumped:
                                    fb = s.dump_mem(p2, 0x4000, "artlibfull")
                                    if fb:
                                        self.full_dumped = True
                                        info["full_lib_bytes"] = len(fb)
                    # E6 origin law
                    ax, ay = info.get("arg_x"), info.get("arg_y")
                    s4, s8 = info.get("s_w"), info.get("s_h")
                    r8, rC = info.get("rec8"), info.get("recC")
                    if None not in (ax, ay, s4, s8, r8, rC):
                        info["origin_x"] = ax + s4 + r8
                        info["origin_y"] = ay + s8 + rC
            # sprf_ctl: control leg, regs suffice
        else:
            rec["dump_capped"] = True
        rec["info"] = info
        s.log(f"ART STOP {tag} leg={leg} " + json.dumps(info)[:400])
        self.art.append(rec)
        s.hits.append(rec)
        with open(op.join(s.out, "hits.json"), "w") as fh:
            json.dump(s.hits, fh, indent=1)
        # t428f resume law: delete ONLY the fired BP, RUN; census re-breaks.
        idx = s.bp_index_of(P0 + L.LEGS[leg]) if leg else None
        if idx is not None:
            s.req(f"EXEC BPDEL {idx:X}", 10.0)
        else:
            s.log("RESUME434B: fired BP index not found — RUN leg-touched")
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"RESUME434B {leg} hdr={hdr}")
        return rec

    # ---- one hand-rolled census: ships screen must survive the clicks ----
    def run_phases(self):
        s = self.s
        out = {}
        if not s.close_eventwin():
            s.log("DRIVE: close_eventwin failed (title guard?)")
            return None
        if not s.assert_on_map("drive_prearm"):
            s.log("DRIVE: not on bare map — abort")
            return None
        base_im = s.grab("map_baseline")
        if not s.arm_census(ALL_LEGS):
            s.log("DRIVE: ARM FAILED")
            return None
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"DRIVE: armed RUN hdr={hdr}")
        time.sleep(0.5)
        s.send(["click", str(SHIPS_BTN[0]), str(SHIPS_BTN[1])])
        out["ships"] = s.census_window("ships", 20)
        im_sh = s.grab("ships_screen")
        out["ships_diff"] = s.diff_px(base_im, im_sh) \
            if im_sh and base_im else -1
        # second paint: click row 0 (selection repaint re-enters 0x50d12)
        s.send(["click", "300", "105"])
        out["row"] = s.census_window("row", 12)
        s.disarm_run("drive")
        s.persist()
        out["stops"] = {k: (0 if v is None else len(v))
                        for k, v in out.items() if isinstance(v, list)}
        return out


def analyze(run):
    kp = op.join(run, "art_attrib.json")
    art = json.load(open(kp)) if op.exists(kp) else []
    blits = [r for r in art if r.get("leg") == "art_blit"]
    fc = [r for r in art if r.get("leg") == "fc34_art"]
    ctl = [r for r in art if r.get("leg") == "sprf_ctl"]
    cen = {}
    cp = op.join(run, "census.json")
    if op.exists(cp):
        cen = json.load(open(cp)).get("pty_census", {})
    print("CENSUS", cen)
    print(f"art_blit stops={len(blits)} fc34={len(fc)} ctl={len(ctl)}")
    for f in fc:
        print("  FC34", json.dumps(f.get("info")))
    for b in blits:
        print("  BLIT", json.dumps(b.get("info")))
    for c in ctl:
        print("  CTL", json.dumps(c.get("info")))
    with_d = [b for b in blits if b["info"].get("rec_head")]
    if with_d:
        sels = sorted({b["info"].get("sel") for b in with_d})
        v = (f"ROW-ART BLIT WITNESSED LIVE x{len(with_d)}; sels {sels}; "
             f"payload magic {[b['info'].get('pay_magic') for b in with_d]}; "
             f"origins {[(b['info'].get('origin_x'), b['info'].get('origin_y')) for b in with_d]}; "
             f"run identity match offline vs extracted smship??/dkship??")
        rc = 0
    elif blits:
        v = ("art_blit fired but arg dump failed (see BLIT lines) — rerun "
             "only if harness-clean")
        rc = 1
    elif ctl:
        v = ("HONEST NEGATIVE: paint leg ran (sprintf control fired) but "
             "0x50d49 never stopped — art blit gated off on this build/state")
        rc = 1
    else:
        v = ("HONEST NEGATIVE: zero stops — ships-screen paint never executed "
             "while armed (check phases diffs)")
        rc = 1
    print("VERDICT:", v)
    with open(op.join(run, "verdict.json"), "w") as fh:
        json.dump({"census": cen, "blits": len(blits), "fc34": len(fc),
                   "ctl": len(ctl), "verdict": v}, fh, indent=1)
    return rc


def live_attempt(tag, window, disp, port, tl, settle):
    ds = ArtSess(tag, ALL_LEGS, ["drive"], window, disp, port, tl, settle, 0)
    s = ds.s
    try:
        s.log(f"t434b start out={s.out} legs={ALL_LEGS} window={window}")
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
        mem = s.read_mem(rows[-1]["path"]) if rows else None
        B = SL.base_of(mem, s.anch) if mem else None
        s.log(f"ring base B={hx(B)} (expect {hx(L.EXPECT_BASE)})")
        if B != L.EXPECT_BASE:
            s.log("NEGATIVE: base mismatch — armed addresses invalid")
            return 1
        s.legs = ALL_LEGS
        s.census = True
        s.pay = open(L.R293.PAYLOAD, "rb").read()
        ph_res = ds.run_phases()
        if ph_res is None:
            return 2
        s.probes.append({"probe": "phases", "result": ph_res})
        ds.whole_log_census()
        ds.bank_on_exit()
        with open(op.join(s.out, "phases.json"), "w") as fh:
            json.dump(ph_res, fh, indent=1)
        return 0
    finally:
        ds.teardown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="t434b")
    ap.add_argument("--window", type=int, default=15)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55998)
    ap.add_argument("--tl", type=int, default=3600)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--offline", default=None, metavar="RUN_DIR")
    args = ap.parse_args()

    if args.offline:
        return analyze(op.abspath(args.offline))

    rc = D.preflight(ALL_LEGS)
    if rc:
        print(f"PREFLIGHT RC={rc}")
        return rc
    if not D.port_free(args.port):
        print(f"HARNESS ERROR: MCP port {args.port} busy")
        return 2
    for attempt in range(1, args.attempts + 1):
        print(f"=== attempt {attempt}/{args.attempts} ===")
        rc = live_attempt(f"{args.tag}-a{attempt}", args.window, args.disp,
                          args.port, args.tl, args.settle)
        print(f"live_attempt rc={rc}")
        if rc == 0:
            runs = sorted(os.listdir(op.join(ROOT, "work/r1")))
            cand = [r for r in runs if r.startswith(f"dbg-{args.tag}-a{attempt}")]
            if cand:
                return analyze(op.join(ROOT, "work/r1", cand[-1]))
            return 0
        if rc == 2:
            print("HARNESS ERROR — not retrying")
            return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
