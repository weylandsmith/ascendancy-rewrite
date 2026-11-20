#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t428f: K5 ORIGIN VIA RUNTIME FRAME READ (docs/re/_wip_t428f.md).

Question: the k5 blit site (paint body 0x3c7bc..0x3c832, t428e E1) fetches
17np record 5 and calls 0x5caac. WHERE does it land on screen? t428e E6 said
p3/p4/p5 were stale frame leftovers; F1b re-accounting of the banked asm
(work/t198_planwin.asm:2011-2040) shows FIVE explicit pushes ($0 y, $0 x, $5
sel, fc34 return, &struct) with `add $0x14,%esp` confirming — so at the call
[esp+0x10]=y=0, [esp+0x14]... wait, the live dump settles the exact map. The
E6 composition law (work/combat_decomp/5caac.c:58-64) then makes the RUNTIME
payload-dir entry p2+8+8*sel the decisive offset:
    x = p4 + struct[+4] + dir[+0x10],  y = p5 + struct[+8] + dir[+0x14].

LEGS (file offsets; linear = P0+off, P0=0x1BF450 deterministic base):
  k5_gate  0x3C7CD  cmpl $0xffffffff,0x35(%eax) — stops with eax = the ACTUAL
                     0x56d1c(0x7a35c,"PLANLIST" imm 0x1f06) result. Bank head
                     0x60 (magic, name@+0x20, dword@+0x34/35). Gate datum.
  k5_blit  0x3C82D  call 0x5caac — fires ONLY if the gate passed. Bank 0x18
                     bytes at esp (ret0,p1,p2,sel,y,x as the callee sees them),
                     struct head at p1, payload head at p2, dir entry
                     p2+8+8*sel + entry body; compute the E6 origin.
  blit1    0x3B9DF  blit-1 call site (t428d PORTED law) — POSITIVE CONTROL
                     that the paint body ran at all this session.

PHASE: one hand-rolled census (the planet list must SURVIVE the clicks —
census_click's close_eventwin would eat it): close popups -> arm -> RUN ->
click Planets (553,145) -> window -> grab -> click detail row (200,105, t254
Vega-IV recipe) -> window -> disarm.

Offline pre-read (F1): bank-t251-live1255 PLANLIST magic-record +0x35 == 0 in
20/20 slots — if 0x56d1c returns that record and state is representative, the
gate FAILS and k5 is never painted (honest negative closes the origin question
as "gated off"). The live stop is the arbiter.

SAFETY: scratch game-wp only (preflight asserts); OWN ring dir; private Xvfb
(:97, NEVER production :9); core=normal; -time-limit; teardown SIGKILL by
RECORDED PID; Oct-29 md5-verified RESUME.GAM; NEVER loadstate; base assert.
Exit 0 = session ran + data banked (verdict in run dir); 1 = negative;
2 = harness error (never retry).
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
K5_LEGS = {"k5_gate": 0x3C7CD, "k5_blit": 0x3C82D, "blit1": 0x3B9DF}
L.LEGS.update(K5_LEGS)          # single source of truth (r330 law)
ALL_LEGS = ["k5_gate", "k5_blit", "blit1"]

PLANETS_BTN = (553, 145)        # windows.txt NAME PLANETS rect 474,130-632,160
DETAIL_ROW = (200, 105)         # t254 Vega-IV recipe (STATE archive t254)
PEAK = (224, 107)               # t428c measured registration peak (screen law)


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


class K5Sess(D.DbgSession):
    """DbgSession + k5-leg attribution + hand-rolled planet-screen census."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.k5 = []
        self.dump_left = {"k5_gate": 4, "k5_blit": 4, "blit1": 3}
        s = self.s
        orig = s.bank_stop

        def bank428f(tag):
            eip = s.read_reg("eip")
            leg = s.attribute(eip) if eip else None
            if leg in K5_LEGS:
                return self._bank_k5(tag, eip, leg, orig)
            return orig(tag)

        s.bank_stop = bank428f                    # INSTANCE patch (t330 law)

        # t428f POLL-BY-BREAK census (instance patch). t428f attempt-1 post-mortem:
        # the k5_gate COLD leg fired during resume_and_rearm's RUN; its fire
        # line + I-> register line surfaced in the pty, but the stock
        # census_window pty_new() consumed them and the re-arm cycle (BPDEL * +
        # RUN) destroyed the stopped state — a cold leg renders ONCE, so the
        # stop was lost. Poll instead: BREAK (whatever the state), EV eip, and
        # if eip is a leg, bank NOW (registers valid, CPU parked at the BP);
        # otherwise RUN and poll again. Legs here are cold (paint-only), so the
        # t302 hot-storm law does not apply.
        orig_cw = s.census_window

        def census428f(tag, seconds):
            t_end = time.time() + seconds
            recs = []
            while time.time() < t_end and len(recs) < 6:
                if not s.do_break():
                    s.log(f"CENSUS428F {tag}: BREAK lost — ending window")
                    break
                eip = s.read_reg("eip")
                leg = s.attribute(eip) if eip else None
                if leg:
                    recs.append(s.bank_stop(f"{tag}#{len(recs)}"))
                    continue          # bank_stop resumed + re-armed
                lines, ok, hdr = s.req("EXEC RUN", 15.0)
                time.sleep(1.5)
            s.log(f"CENSUS428F {tag}: {len(recs)} stops banked ({seconds:.0f}s)")
            return recs

        s.census_window = census428f              # (used by run_phases via s.)
        self._orig_cw = orig_cw

    def bank_on_exit(self):
        super().bank_on_exit()
        try:
            with open(op.join(self.s.out, "k5_attrib.json"), "w") as fh:
                json.dump(self.k5, fh, indent=1)
        except Exception:
            pass

    def _bank_k5(self, tag, eip, leg, orig_fallback):
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
            if leg == "k5_gate":
                w = regs.get("eax")
                info["widget_ptr"] = hx(w)
                if w and 0x10000 <= w < 0x1000000:
                    hb = s.dump_mem(w, 0x60, f"k5gate{tag}")
                    if hb and len(hb) >= 0x40:
                        info["magic_ok"] = u32(hb, 0) == 0x12345678
                        info["name"] = hb[0x20:0x2c].split(b"\x00")[0].decode(
                            "latin1", "replace")
                        info["d34"] = hx(u32(hb, 0x34))
                        info["gate_val"] = s32(hb, 0x35)
                        rec["gate_pass"] = s32(hb, 0x35) == -1
            elif leg == "k5_blit":
                # t330 LAW: the heavy-debug BP stops BEFORE the call executes
                # -> esp points at the FIRST pushed arg: [esp]=p1 &struct,
                # [esp+4]=p2 payload, [esp+8]=p3 sel, [esp+0xc]=p4 x,
                # [esp+0x10]=p5 y (arg map shp.md S12.1; ret0 is static
                # 0x3c832, not yet on the stack).
                esp = regs.get("esp")
                if esp and 0x1000 < esp < 0x10000000:
                    eb = s.dump_mem(esp, 0x18, f"k5esp{tag}")
                    if eb and len(eb) >= 0x14:
                        p1, p2, sel, px, py = struct.unpack_from("<5I", eb, 0)
                        info["esp"] = hx(esp)
                        info["p1"], info["p2"], info["sel"] = hx(p1), hx(p2), sel
                        info["arg_x"], info["arg_y"] = s32(eb, 0xc), s32(eb, 0x10)
                        sb = s.dump_mem(p1, 0x18, f"k5s{tag}") if p1 and \
                            0x10000 <= p1 < 0x10000000 else None
                        if sb and len(sb) >= 0x10:
                            info["s0"] = hx(u32(sb, 0))
                            info["s4"] = s32(sb, 4)
                            info["s8"] = s32(sb, 8)
                        if p2 and 0x10000 <= p2 < 0x10000000:
                            ph = s.dump_mem(p2, 0x20, f"k5pay{tag}")
                            if ph and len(ph) >= 0x10:
                                info["pay_head"] = ph.hex(" ")
                            v110 = s.dump_mem(p2 + 0x88, 4, f"k5v110{tag}")
                            if v110:
                                info["pay110"] = v110 == b"1.10"
                            tb = s.dump_mem(p2 + 8 + 8 * sel, 8,
                                            f"k5dir{tag}") \
                                if 0 <= sel < 64 else None
                            if tb and len(tb) >= 8:
                                off = u32(tb, 0)
                                info["dir_off"] = hx(off)
                                info["dir10"] = s32(tb, 4)
                                eb2 = s.dump_mem(p2 + off, 0x20, f"k5rec{tag}") \
                                    if off and 0 < off < 0x800000 else None
                                if eb2 and len(eb2) >= 0x18:
                                    info["rec_head"] = eb2.hex(" ")
                                    info["rec8"] = s32(eb2, 8)
                                    info["recC"] = s32(eb2, 0xC)
                                    info["rec10"] = s32(eb2, 0x10)
                                    info["rec14"] = s32(eb2, 0x14)
                # E6 law (work/combat_decomp/5caac.c:58-64): param_2 is
                # RE-ASSIGNED to p2 + u32[p2+8+8*sel] (the dir entry), then
                # x = arg_x + struct[+4] + entry[+0x10],
                # y = arg_y + struct[+8] + entry[+0x14].
                ax, ay = info.get("arg_x"), info.get("arg_y")
                s4, s8 = info.get("s4"), info.get("s8")
                r10, r14 = info.get("rec10"), info.get("rec14")
                if None not in (ax, ay, s4, s8, r10, r14):
                    info["origin_x"] = ax + s4 + r10
                    info["origin_y"] = ay + s8 + r14
                    info["hits_peak"] = (info["origin_x"],
                                         info["origin_y"]) == PEAK
            else:  # blit1 positive control (same before-call layout: [esp]=p1)
                esp = regs.get("esp")
                if esp and 0x1000 < esp < 0x10000000:
                    eb = s.dump_mem(esp, 8, f"b1esp{tag}")
                    if eb and len(eb) >= 8:
                        info["p1"] = hx(u32(eb, 0))
                        info["p2"] = hx(u32(eb, 4))
        else:
            rec["dump_capped"] = True
        rec["info"] = info
        s.log(f"K5F STOP {tag} leg={leg} eax={hx(regs.get('eax'))} "
              + json.dumps(info)[:400])
        self.k5.append(rec)
        s.hits.append(rec)
        with open(op.join(s.out, "hits.json"), "w") as fh:
            json.dump(s.hits, fh, indent=1)
        # t428f: NOT s.resume_and_rearm — its internal do_break+arm_all
        # (BPDEL * + RUN) destroys a PENDING halt at the next cold leg
        # (attempt 1: CPU parked at 0x1FBC1D, BPDEL * let it fall through
        # unbanked). Delete ONLY the fired BP and RUN; the census loop
        # re-breaks and attributes the next stop.
        idx = s.bp_index_of(P0 + L.LEGS[leg]) if leg else None
        if idx is not None:
            s.req(f"EXEC BPDEL {idx:X}", 10.0)
        else:
            s.log("RESUME428F: fired BP index not found — RUN leg-touched")
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"RESUME428F {leg} hdr={hdr}")
        return rec

    # ---- one hand-rolled census: the planet list must survive clicks ----
    def run_phases(self):
        s = self.s
        out = {}
        results = {}
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
        s.send(["click", str(PLANETS_BTN[0]), str(PLANETS_BTN[1])])
        results["planets"] = s.census_window("planets", 15)
        im_pl = s.grab("planets_screen")
        out["planets_diff"] = s.diff_px(base_im, im_pl) \
            if im_pl and base_im else -1
        s.send(["click", str(DETAIL_ROW[0]), str(DETAIL_ROW[1])])
        results["row"] = s.census_window("row", 15)
        im_row = s.grab("row_screen")
        out["row_diff"] = s.diff_px(im_pl, im_row) if im_row and im_pl else -1
        s.disarm_run("drive")
        s.persist()
        out["stops"] = {k: (0 if v is None else len(v))
                        for k, v in results.items()}
        return out


def analyze(run):
    kp = op.join(run, "k5_attrib.json")
    k5 = json.load(open(kp)) if op.exists(kp) else []
    gates = [r for r in k5 if r.get("leg") == "k5_gate"]
    blits = [r for r in k5 if r.get("leg") == "k5_blit"]
    b1 = [r for r in k5 if r.get("leg") == "blit1"]
    cen = {}
    cp = op.join(run, "census.json")
    if op.exists(cp):
        cen = json.load(open(cp)).get("pty_census", {})
    print("CENSUS", cen)
    print(f"gate stops={len(gates)} blit stops={len(blits)} blit1={len(b1)}")
    for g in gates:
        print("  GATE", json.dumps(g.get("info")))
    for b in blits:
        print("  BLIT", json.dumps(b.get("info")))
    for b in b1:
        print("  BLIT1", json.dumps(b.get("info")))
    if blits:
        origins = [(b["info"].get("origin_x"), b["info"].get("origin_y"))
                   for b in blits if b["info"].get("origin_x") is not None]
        v = (f"K5 BLIT WITNESSED LIVE; E6-law origins {origins}; "
             f"peak-hit {any(o == PEAK for o in origins)}")
        rc = 0
    elif gates and all(g.get("gate_pass") is False for g in gates):
        v = ("GATE WITNESSED FAILING LIVE (widget+0x35 != -1): k5 NOT painted "
             "on this screen — origin question answered as gated-off")
        rc = 0
    elif b1:
        v = ("paint body RAN (blit1 control fired) but the k5 gate site never "
             "stopped — k5 region not executed this session (honest negative)")
        rc = 1
    else:
        v = ("HONEST NEGATIVE: zero k5/blit1 stops — planet-screen paint body "
             "never executed while armed (check phases diffs)")
        rc = 1
    print("VERDICT:", v)
    with open(op.join(run, "verdict.json"), "w") as fh:
        json.dump({"census": cen, "gates": len(gates), "blits": len(blits),
                   "blit1": len(b1), "verdict": v}, fh, indent=1)
    return rc


def live_attempt(tag, window, disp, port, tl, settle):
    ds = K5Sess(tag, ALL_LEGS, ["drive"], window, disp, port, tl, settle, 0)
    s = ds.s
    try:
        s.log(f"t428f start out={s.out} legs={ALL_LEGS} window={window}")
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
    ap.add_argument("--tag", default="t428f")
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
        return rc
    if not D.port_free(args.port):
        print(f"HARNESS ERROR: MCP port {args.port} busy")
        return 2
    for i in range(1, args.attempts + 1):
        print(f"=== ATTEMPT {i} {time.strftime('%H:%M:%S')} ===", flush=True)
        rc = live_attempt(args.tag, args.window, args.disp, args.port,
                          args.tl, args.settle)
        cands = sorted((d for d in os.listdir(op.join(ROOT, "work/r1"))
                        if d.startswith(f"dbg-{args.tag}-")), reverse=True)
        run = op.join(ROOT, "work/r1", cands[0]) if cands else None
        print(f"attempt {i} rc={rc} run={run}", flush=True)
        if rc == 2:
            print("ATTEMPT harness error — NOT retrying")
            return 2
        if rc == 0 and run:
            ar = analyze(run)
            print(f"analyze rc={ar}")
            return 0 if ar == 0 else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
