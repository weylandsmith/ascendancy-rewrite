#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t344: MOUSE-CURSOR SELECTOR LIVE WITNESS (OQ-005, docs/re/_wip_t344.md S3).

STATIC LAW FOUND t344(a) (work/r331_disasm.txt verbatim):
  * 'DATA\\MOUSE.SHP' referrer IS an immediate: pool-relative imm 0x1764
    (= str_off 0x84314 - 0x82BB0) at fn 0x309d4 0x309f9 (opener, gsystem).
    t328's zero-u32 scan scanned 0x84314 — wrong value, law explained.
  * THE CURSOR REQUEST POINT: fn 0x30a60 0x30aa7 `call 0x64ea9(lib, id)`
    with lib := [eax+0x733] (eax = gsystem obj, imm 0x484f8 loader-patched),
    id = edx. Callers:
      fn 0x54650 button arm  0x546af edx=1 / release arm 0x546d6 edx=0
      mode chain 0x54741..0x547a6: mode := 0 (edx==0,   ds:0x484ec==0),
        1 (edx==0, 484ec==0x27f), 2 (edx==0x1df, 484ec==0),
        3 (edx==0x1df, 484ec==0x27f); on CHANGE edx = mode+4 -> fn 0x5a1e4
        -> gate -> fn 0x30a60.  {edx, 484ec} = cursor (y,x) at EXACT edge
        values 0 / 479 / 639 — SCREEN CORNERS (DOSBox clamps clicks that
        land outside the letterboxed content to exactly these).
      fn 0x1be10 window chooser (CURSORSHAPE path), fn 0x309d4 opener.
  * => ids 4,5,6,7 ARE the corner cursors; mouse.shp k4..k7 are ONE 78x47
    glyph with the 4 corner hotspots ((0,0),(-77,0),(0,-46),(-77,-46) i32
    bbox pairs) — t344 static measurement, scripts/r344_dimslaw.py.

THIS SESSION arms fn 0x30a60's request site (file 0x30AA7) + t330's proven
blit_deref (0x5CB59) + btn_hdlr control, clicks the four screen corners
(root coords clamped by DOSBox: (12,10),(788,10),(12,590),(788,590)), then
the right-bar STATUS button (t330-proven mouse.shp k0 drawer, positive
control) and the pip/enter-system view (windows.txt CURSORSHAPE 2 L216).
Banked per stop: eax/ebx/ecx/edx, ret0, lib=[eax+0x733], TOC entry
lib+8+8*id, record head 0x20 bytes (hex) for offline byte-match against
extracted libs (r330 machinery reused).

VERDICT:
  mouse.shp rows with id in {5,6,7}  -> CORNER SELECTOR WITNESSED LIVE.
  blit_deref row resolving to the k5/k6/k7 record offset -> DRAW WITNESS
    (C27-C29 close-class).
  ids {0,1,4} only -> mode chain live, corner ids capture-limited.
  zero cur_req -> harness negative (rc 1; attempt logic per t330).

LAWS: r1_dbg_session v2 composes r299 Sess; INSTANCE-patch bank_stop;
census only inside armed windows (t303); storm cap; scratch scratch/ only
(preflight refuses game/); private Xvfb :97, port 55999; production :9
never signalled; teardown SIGKILL recorded PIDs; VENV python (PIL).
Exit 0 = banked+analyzed; 1 = negative; 2 = harness (never retry).
"""
import argparse
import json
import os
import os.path as op
import struct
import sys
import sys
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r299_leg_session as L                                   # noqa: E402
import r1_dbg_session as D                                     # noqa: E402
import r330_blit_session as T330                               # noqa: E402

P0 = D.P0
CUR_LEGS = {"cur_req": 0x30AA7, "mode_upd": 0x547A6}
L.LEGS.update(CUR_LEGS)                     # single source of truth (r330 law)
ALL_LEGS = ["cur_req", "mode_upd", "blit_deref", "btn_hdlr"]

# t344 launch-2 CALIBRATION (replaces launch-1 letterbox assumption):
# DOSBox maps guest 640x480 -> root 800x600 at scale 1.25, offset 0
# (launch 1: root 788 -> guest ~630, ids 4..7 never evaluated). Exact
# corner guest {0,639}x{0,479} = root {0,799}x{0,599}.
CORNERS = {"c_tl": (0, 0), "c_tr": (799, 0), "c_bl": (0, 599),
           "c_br": (799, 599), "c_br2": (798, 598), "c_top_r": (799, 300),
           "c_bot_l": (0, 300)}
STATUS_BTN = (553, 145)
PHASES = ["baseline"] + list(CORNERS) + ["control_status"]


class CursorSess(T330.BlitSess):
    """BlitSess + cur_req attribution + corner-click phase plan."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.cur_attrib = []
        self.cur_left = {}
        s = self.s
        orig330 = s.bank_stop                    # already instance-patched

        def bank344(tag):
            eip = s.read_reg("eip")
            leg = s.attribute(eip) if eip else None
            if leg in ("cur_req", "mode_upd"):
                return self._bank_cur(tag, eip, leg)
            return orig330(tag)

        s.bank_stop = bank344                    # re-patch (compose)

    def bank_on_exit(self):
        super().bank_on_exit()
        try:
            with open(op.join(self.s.out, "cur_attrib.json"), "w") as fh:
                json.dump(self.cur_attrib, fh, indent=1)
        except Exception:
            pass

    def _bank_cur(self, tag, eip=None, leg="cur_req"):
        s = self.s
        regs = {"eip": eip}
        for r in ("eax", "ebx", "ecx", "edx", "esp"):
            v = s.read_reg(r)
            if v is None:
                break
            regs[r] = v
        rec = {"tag": tag, "wall": time.strftime("%H:%M:%S"),
               "leg": leg, "window": self.window_no,
               "eip_file_off": f"{(eip - P0):#x}" if eip else None}
        esp = regs.get("esp")
        if esp and 0x1000 < esp < 0x10000000:
            eb = s.dump_mem(esp, 8, f"cur344esp{self.window_no}")
            if eb and len(eb) >= 4:
                r0 = struct.unpack_from("<I", eb, 0)[0]
                rec["ret0_file_off"] = ((r0 & 0xFFFFFF) - P0) \
                    if P0 <= (r0 & 0xFFFFFF) < P0 + 0x8CC83 else None
        sid = struct.unpack("<i", struct.pack("<I", regs.get("edx", 0)))[0]
        rec["sel_id"] = sid
        info = {}
        lib = None
        eax, ebx = regs.get("eax"), regs.get("ebx")
        if leg == "mode_upd":
            # AT 0x547a6: eax = core obj (mode clobbered at 0x547a0),
            # edx = id = mode+4 (0x5479d lea). Gate state read directly:
            # [core+0x24da4] mouse-active !=0 AND ecx==0 -> fn 0x5a1e4
            # SUPPRESSES the request. Bank the flag so zero cur_req after
            # a mode_upd is ATTRIBUTABLE, not a mystery.
            info["mode"] = sid - 4
            if eax and 0x1000 < eax < 0x10000000:
                fb = s.dump_mem(eax + 0x24DA4, 4,
                                f"cur344flag{self.window_no}")
                if fb and len(fb) >= 4:
                    info["mouse_active"] = struct.unpack_from("<i", fb, 0)[0]
        else:
            # AT 0x30aa7 fn 0x30a60 has ALREADY resolved: eax = lib, edx = id
            # (0x30aa3 mov edx,esi / 0x30aa5 mov eax,ecx). ebx = caller's ebx.
            lib = eax
            info["lib_ptr"] = f"{lib:#x}" if lib else None
            info["caller_ebx"] = f"{ebx:#x}" if ebx is not None else None
        if leg == "cur_req" and lib and 0x10000 <= lib < 0x800000 \
                and 0 <= sid < 64:
            tb = s.dump_mem(lib + 8 + 8 * sid, 8,
                            f"cur344toc{self.window_no}")
            if tb and len(tb) >= 4:
                off = struct.unpack_from("<I", tb, 0)[0]
                info["rec_rel"] = f"{off:#x}"
                if 0 < off < 0x400000:
                    rb = s.dump_mem(lib + off, 0x20,
                                    f"cur344rec{self.window_no}")
                    if rb and len(rb) >= 0x18:
                        info["rec_head"] = rb.hex(" ")
        key = self.window_no
        if self.cur_left.get(key, 8) <= 0:
            rec["dump_capped"] = True
        else:
            self.cur_left[key] = self.cur_left.get(key, 8) - 1
            rec.update(info)
            self.cur_attrib.append({"phase_tag": tag, "window": self.window_no,
                                    "sel_id": sid, **info})
        s.log(f"CUR344 STOP {tag} id={sid} lib={rec.get('lib_ptr') or info.get('lib_ptr')} "
              f"rec={info.get('rec_rel')}")
        s.hits.append(rec)
        with open(op.join(s.out, "hits.json"), "w") as fh:
            json.dump(s.hits, fh, indent=1)
        s.resume_and_rearm("cur_req")
        return rec

    def run_phases(self):
        s = self.s
        results = {}
        map_im = s.grab("map0")
        for ph in PHASES:
            if ph == "baseline":
                results[ph] = s.census_click(None, None, ph, 12)
            elif ph in CORNERS:
                x, y = CORNERS[ph]
                results[ph] = s.census_click(x, y, ph, 8)
                im = s.grab(ph + "_png")
                if im is not None and map_im is not None:
                    results[ph + "_diff"] = s.diff_px(map_im, im)
            elif ph == "control_status":
                results[ph] = s.census_click(*STATUS_BTN, ph, 15)
                im = s.grab("scr_status")
                if im is not None and map_im is not None:
                    results[ph + "_diff"] = s.diff_px(map_im, im)
                if not s.escape_to_map(map_im):
                    s.log(f"B344: escape_to_map failed after {ph}")
            elif ph == "pip":
                im = s.enter_system(map_im)
                results["pip_entered"] = im is not None
                if im is not None:
                    results[ph] = s.census_click(788, 10, ph, 8)
                    s.escape_to_map(map_im)
            s.persist()
        return results


def analyze(run):
    ap = op.join(run, "cur_attrib.json")
    bp = op.join(run, "blit_attrib.json")
    if not op.exists(ap):
        print(f"NO cur_attrib.json in {run}")
        return 2
    cur = json.load(open(ap))
    blit = json.load(open(bp)) if op.exists(bp) else []
    libs = T330._ALL_LIBS()

    def resolve(rb_hex):
        if not rb_hex:
            return None, None
        rb = bytes.fromhex(rb_hex.replace(" ", ""))
        for p, d in libs.items():
            off = d.find(rb)
            if off >= 0:
                return op.basename(p), off
        return None, None

    ids_by_lib = {}
    for a in cur:
        nm, off = resolve(a.get("rec_head"))
        a["lib_file"], a["rec_off"] = nm, (hex(off) if off is not None else None)
        ids_by_lib.setdefault(nm or "?", []).append(a.get("sel_id"))
        print("CUR ROW:", json.dumps({k: a.get(k) for k in
              ("phase_tag", "sel_id", "lib_file", "rec_off", "ret0_file_off")}))
    mouse_rows = [a for a in cur if a.get("lib_file") == "mouse.shp"]
    mode_rows = [a for a in cur if a.get("mode") is not None]
    corner_ids = sorted({a["sel_id"] for a in mouse_rows
                         if a.get("sel_id") in (4, 5, 6, 7)})
    mode_vals = sorted({a.get("mode") for a in mode_rows})
    # TOC offsets of mouse.shp k4..k7 (file-measured t344)
    mtoc = {}
    if "mouse.shp" in libs:
        d = libs["mouse.shp"]
        for k in range(8):
            mtoc[struct.unpack_from("<I", d, 8 + 8 * k)[0]] = k
    draw_rows = []
    for r in blit:
        nm, off = resolve(r.get("rec_head"))
        if nm == "mouse.shp" and off in mtoc and mtoc[off] in (5, 6, 7):
            draw_rows.append({"phase_tag": r.get("phase_tag"), "k": mtoc[off],
                              "hdr": r.get("hdr")})
    census = {}
    cp = op.join(run, "census.json")
    if op.exists(cp):
        census = json.load(open(cp)).get("pty_census", {})
    if draw_rows:
        v = (f"DRAW WITNESS: blit_deref banked mouse.shp records "
             f"{draw_rows} — k5/k6/k7 pixels drawn through FUN_0005caac")
    elif corner_ids:
        v = (f"SELECTOR WITNESSED: cursor requests selected mouse.shp corner "
             f"ids {corner_ids} live (mode-chain corner law confirmed); "
             f"pixel draw still unwitnessed")
    elif mode_rows:
        v = (f"MODE CHAIN LIVE: mode_upd fired with modes {mode_vals} "
             f"(gate mouse_active values "
             f"{sorted({a.get('mouse_active') for a in mode_rows})}); cur_req "
             f"corner ids absent — request gate or corner-value miss")
    elif mouse_rows:
        v = ("mode chain/button requests witnessed with ids "
             f"{sorted({a['sel_id'] for a in mouse_rows})} only — corner ids "
             "5..7 NOT fired this session (capture-limited)")
    else:
        v = "HONEST NEGATIVE: zero cur_req stops attributed to any library"
    verdict = {"census": census, "cur_rows": len(cur),
               "mouse_rows": len(mouse_rows), "corner_ids": corner_ids,
               "mode_rows": len(mode_rows), "modes_seen": mode_vals,
               "draw_rows": draw_rows, "verdict": v}
    print("VERDICT:", v)
    with open(op.join(run, "verdict.json"), "w") as fh:
        json.dump(verdict, fh, indent=1)
    return 0


def live_attempt(tag, window, disp, port, tl, settle):
    ds = CursorSess(tag, ALL_LEGS, PHASES, window, disp, port, tl, settle, 0)
    s = ds.s
    try:
        s.log(f"t344 start out={s.out} legs={ALL_LEGS} window={window}")
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
        B = L.SL.base_of(mem, s.anch) if mem else None
        s.log(f"ring base B={hex(B) if B else None} (expect "
              f"{hex(L.EXPECT_BASE)})")
        if B != L.EXPECT_BASE:
            s.log("NEGATIVE: base mismatch — armed addresses invalid")
            return 1
        s.legs = ALL_LEGS
        s.census = True
        s.pay = open(L.R293.PAYLOAD, "rb").read()
        ph_res = ds.run_phases()
        if ph_res is None:
            return 2
        ds.whole_log_census()
        ds.bank_on_exit()          # t330 ordering fix: bank before analyze
        with open(op.join(s.out, "phases.json"), "w") as fh:
            json.dump({k: (v if isinstance(v, (dict, int, float, bool))
                           else (0 if v is None else len(v)))
                       for k, v in ph_res.items()}, fh, indent=1)
        return 0
    finally:
        ds.teardown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="t344")
    ap.add_argument("--window", type=int, default=12)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55999)
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
