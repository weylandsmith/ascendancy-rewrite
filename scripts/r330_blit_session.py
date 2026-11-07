#!/usr/bin/env python3
"""t330: MOUSE-DIMS DRAW-CAPTURE — executes the t328 S4 design (docs/re/
_wip_t328.md S4; docs/re/shp.md S25). ATTEMPT-2 SHAPE (post attempt 1
dbg-t330-20261107-073530, findings in _wip_t330 S2):

  * blit_entry stops CONSUME the window (1 banked per panel, deref/refuse
    stayed silent after the entry BPDEL+RUN) -> legs WITHOUT entry this
    time; the guest runs through the dims gate and stops AT deref/refuse.
  * attribution must hook the Sess INSTANCE (DbgSession composes Sess).
  * cache ctx = 0x2E1194 ABSOLUTE (ck113 law; deterministic base B =
    0x1BF4D8 every run; P0+0x9F10C = 0x25E55C is NOT the ctx — corrected).
  * MOUSE.SHP verbatim copy IS in the save state (sav-linear 0x2EC0C4,
    full 10435 B match; PAY 0x2EC03C is NOT a cache-slot ptr — gsystem
    loads it outside the 200-slot cache; u32 refs cluster at 0x2e8b78+).

Question (OQ-005 residue, decision-sheet C27/C28/C29 = mouse.shp k5/k6/k7):
does the vendor blit FUN_0005caac read record dims from rec+0 (u16 pair,
46x77, walk EXACT-H — t328 S2a) or from the canonical u32@+0x10 slot (zero
component -> dims-gate -1 refuse @0x5cb2b)?

Legs (file offsets; linear = P0 + off, P0 = 0x1BF450):
  blit_refuse 0x5CB2B  dims-gate -1 return (fires ONLY on invalid dims)
  blit_minus2 0x5CB36  empty-clip -2 return (completes the error picture)
  blit_deref  0x5CB59  stream-cursor deref `mov esi,[esi]` (stop BEFORE the
     instruction: ebx = hdr = [[ebp+8]] = [pixptr][W-1][H-1]; esi = dir slot
     addr = PAY+8+8*sel; args live at [ebp+4]=shape [ebp+8]=PAY
     [ebp+0xc]=sel [ebp+0x10/0x14]=x/y — raw asm re-verified t330)
  btn_hdlr    (r299)   positive control only (attempt 1: bar-button clicks
                       land WITHOUT it — NOT an expectation)

Verdict grammar (S4, post-hoc via --offline so banked data is never
wasted): mouse-attributed blit_refuse -> canonical-slot law holds;
mouse-attributed deref with hdr dims (45,76) -> u16@+0 in force; no
mouse-attributed blit -> honest negative (k5/k6/k7 UNREACHABLE-BY-CAPTURE;
cursor-shape consumers [windows.txt CURSORSHAPE cosmos L216 + BatModeWnd
L1186] bypass FUN_0005caac entirely).

LAWS CARRIED: t325 SIGKILL recorded-PID teardown; t302 census re-arm/freeze;
t303 arm only around the measured click; t305 last-4 audit (BF7B/BFAB/BF86
new, unique vs 61 r299 legs + BEFC); t327 venv python (PIL); scratch only;
production :9 untouched. Exit 0 = banked + analyzed; 1 = negative; 2 = harness.
"""
import argparse
import glob
import json
import os
import os.path as op
import struct
import sys
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r299_leg_session as L                      # noqa: E402
import r1_dbg_session as D                         # noqa: E402

P0 = D.P0
NEW_LEGS = {"blit_refuse": 0x5CB2B, "blit_minus2": 0x5CB36,
            "blit_deref": 0x5CB59}
ALL_LEGS = ["blit_refuse", "blit_minus2", "blit_deref", "btn_hdlr"]
D.LEGS.update(NEW_LEGS)
L.LEGS.update(NEW_LEGS)

CACHE = 0x2E1194          # shape-cache ctx, ABSOLUTE (ck113 + t330 measured)

# windows.txt right-bar rects (verified t330 against extracted/ascend00):
# STATUS 474,130-632,160 | FLEET 474,169-632,199 | RESEARCH 474,208-632,238
# SPECIALAB 474,247-632,277 | RACES 474,286-632,316 | Intelligence 474,303-632,333
BTNS = {"status": (553, 145), "fleet": (553, 184), "research": (553, 223),
        "specialab": (553, 262), "races": (553, 301), "intel": (553, 318)}
EDGE_PX = [(12, 240), (460, 240), (236, 12), (236, 468)]
PHASES = ["baseline", "status", "fleet", "research", "specialab", "races",
          "intel", "pip", "edges"]


class BlitSess(D.DbgSession):
    """DbgSession + instance-level bank_stop attribution + storm cap."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.attrib = []
        self.window_no = 0
        self.storm_cap = 3
        self.dump_budget = {"blit_refuse": 8, "blit_minus2": 4,
                            "blit_deref": 8}
        self.dump_left = {}
        s = self.s
        orig = s.bank_stop

        def bank330(tag):
            eip = s.read_reg("eip")
            leg = s.attribute(eip) if eip else None
            if leg in NEW_LEGS:
                return self._bank_blit(tag, eip, leg, orig)
            return orig(tag)

        s.bank_stop = bank330                    # INSTANCE patch (t330 law)

    def bank_on_exit(self):
        super().bank_on_exit()
        try:
            with open(op.join(self.s.out, "blit_attrib.json"), "w") as fh:
                json.dump(self.attrib, fh, indent=1)
        except Exception:
            pass

    # ---- helpers ----
    def _u32(self, blob, off):
        try:
            return struct.unpack_from("<I", blob, off)[0]
        except Exception:
            return None

    def _hx(self, v):
        return f"{v:#x}" if isinstance(v, int) else None

    def _bank_blit(self, tag, eip, leg, orig_fallback):
        """Bank regs + args + hdr dims + dir/record + lib for a blit-leg stop,
        then hand the standard resume/rearm choreography to the Sess."""
        s = self.s
        rec = {"tag": tag, "wall": time.strftime("%H:%M:%S"), "leg": leg,
               "window": self.window_no,
               "eip_file_off": self._hx(eip - P0) if eip else None}
        regs = {}
        for r in ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp"):
            v = s.read_reg(r)
            if v is None:
                break
            regs[r] = v
        rec["regs"] = {k: self._hx(v) for k, v in regs.items()}
        # ret0 from [esp] (Sess law)
        esp = regs.get("esp")
        if esp and 0x1000 < esp < 0x10000000:
            eb = s.dump_mem(esp, 16, f"b330esp{self.window_no}")
            if eb and len(eb) >= 8:
                r0 = self._u32(eb, 0)
                rec["ret_stack"] = {
                    "ret0": self._hx(r0),
                    "ret0_file_off": (self._hx((r0 & 0xFFFFFF) - P0)
                                      if r0 and P0 <= (r0 & 0xFFFFFF)
                                      < P0 + 0x8CC83 else None)}
        ebp, ebx, esi = regs.get("ebp"), regs.get("ebx"), regs.get("esi")
        info = {}
        if ebp and 0x1000 < ebp < 0x10000000:
            ab = s.dump_mem(ebp + 4, 0x18, f"b330arg{self.window_no}")
            if ab and len(ab) >= 0x18:
                shape, pay = self._u32(ab, 4), self._u32(ab, 8)
                info["shape_struct"] = self._hx(shape)
                info["PAY"] = self._hx(pay)
                info["sel"] = self._u32(ab, 0xc)
                info["x"], info["y"] = self._u32(ab, 0x10), self._u32(ab, 0x14)
        # hdr = ebx (prologue ebx=[[ebp+8]]; untouched 0x5cb41..0x5cb59)
        if ebx and 0x10000 < ebx < 0x800000:
            hb = s.dump_mem(ebx, 0x10, f"b330hdr{self.window_no}")
            if hb and len(hb) >= 0x10:
                info["hdr"] = {"pixptr": self._hx(self._u32(hb, 0)),
                               "Wm1": struct.unpack_from("<i", hb, 4)[0],
                               "Hm1": struct.unpack_from("<i", hb, 8)[0]}
        # dir slot + record base ONLY at deref (esi = PAY+8+8*sel pre-move)
        pay = None
        if info.get("PAY"):
            pay = int(info["PAY"], 16)
        if leg == "blit_deref" and esi and pay and P0 < esi < 0x800000:
            db = s.dump_mem(esi, 4, f"b330dir{self.window_no}")
            erel = self._u32(db, 0) if db else None
            info["dir_rel"] = self._hx(erel)
            if erel is not None and pay + erel < 0x800000:
                rb = s.dump_mem(pay + erel, 0x20, f"b330rec{self.window_no}")
                if rb and len(rb) >= 0x18:
                    info["rec_base"] = self._hx(pay + erel)
                    info["rec_head"] = rb.hex(" ")
                    info["dims_u16_at0"] = struct.unpack_from("<HH", rb, 0)
                    info["dims_u32_at0x10"] = struct.unpack_from(
                        "<II", rb, 0x10)
        # library attribution: PAY inside cache slot ptr array, OR verbatim
        # copy at PAY+0x88 matching a known lib head (mouse is OUTSIDE the
        # cache — t330 finding — so match by file bytes too)
        if pay and CACHE <= pay < CACHE + 4 * 200:
            idx = (pay - CACHE) // 4
            info["slot"] = idx
            nb = s.dump_mem(CACHE + 0x7D0 + idx * 0x32, 0x32,
                            f"b330name{self.window_no}")
            if nb:
                info["lib"] = nb.split(b"\x00")[0].decode("latin1",
                                                          "replace")
        if pay and "lib" not in info:
            hb2 = s.dump_mem(pay + 0x88, 0x40, f"b330vb{self.window_no}")
            if hb2 and hb2[:4] == b"1.10":
                info["copy_head"] = hb2.hex(" ")
                nm = match_lib(hb2)
                if nm:
                    info["lib"] = nm
                    info["lib_via"] = "bytes"
        key = (self.window_no, leg)
        if self.dump_left.get(key, self.dump_budget.get(leg, 0)) <= 0:
            rec["dump_capped"] = True
        else:
            self.dump_left[key] = self.dump_left.get(
                key, self.dump_budget.get(leg, 0)) - 1
            rec.update(info)
            self.attrib.append({"leg": leg, "phase_tag": tag, "window": self.window_no,
                                "ret0_file_off": (rec.get("ret_stack") or
                                                  {}).get("ret0_file_off"),
                                **info})
        s.log(f"B330 STOP {tag} leg={leg} lib={rec.get('lib')} "
              f"sel={rec.get('sel')} hdr={rec.get('hdr')} "
              f"u16@0={rec.get('dims_u16_at0')}")
        s.hits.append(rec)
        with open(op.join(s.out, "hits.json"), "w") as fh:
            json.dump(s.hits, fh, indent=1)
        s.resume_and_rearm(leg)
        return rec

    def census_window(self, tag, seconds):
        """r299 census_window with a bounded storm cap, calling the INSTANCE-
        patched bank_stop via s.bank_stop."""
        self.window_no += 1
        s = self.s
        t_end = time.time() + seconds
        recs = []
        while time.time() < t_end and len(recs) < self.storm_cap:
            txt = s.pty_new()
            if txt and s.leg_pats and any(p.search(txt) for p in s.leg_pats):
                time.sleep(1.5)
                s.pty_new()
                recs.append(s.bank_stop(f"{tag}#{len(recs)}"))
                continue
            time.sleep(1.0)
        s.log(f"B330 CENSUS-WINDOW {tag}: {len(recs)} stops banked")
        return recs

    def run_phases(self):
        s = self.s
        results = {}
        map_im = s.grab("map0")
        for ph in PHASES:
            if ph == "baseline":
                results[ph] = s.census_click(None, None, ph, 15)
            elif ph == "edges":
                # cursor-change hunt: real Button clicks at screen edges
                # (t320: xsend has NO motion verb; Button is the sanctioned
                # activator), leg-free, then a watch window.
                for (x, y) in EDGE_PX:
                    s.send(["click", str(x), str(y)])
                    time.sleep(1.2)
                results[ph] = s.census_click(None, None, ph, 15)
            elif ph == "pip":
                # enter a system/planet view (r293 enter_system): the cosmos
                # CURSORSHAPE 2 consumer (windows.txt L216) is the lead
                # mouse.shp suspect.
                im = s.enter_system(map_im)
                results["pip_entered"] = im is not None
                results[ph] = s.census_click(None, None, ph, self.window)
                if im is not None and not s.escape_to_map(map_im):
                    s.log("B330: escape_to_map failed after pip")
            else:
                x, y = BTNS[ph]
                results[ph] = s.census_click(x, y, ph, self.window)
                im = s.grab(f"scr_{ph}")
                if im is not None and map_im is not None:
                    results[ph + "_diff"] = s.diff_px(map_im, im)
                if not s.escape_to_map(map_im):
                    s.log(f"B330: escape_to_map failed after {ph}")
            s.persist()
        return results


_LIB_CACHE = None


def match_lib(head40):
    """Identify a library by its verbatim-copy head bytes (first 0x20 of the
    1.10 copy) against extracted files."""
    global _LIB_CACHE
    import glob
    if _LIB_CACHE is None:
        _LIB_CACHE = {}
        for p in (glob.glob(op.join(ROOT, "extracted/**/*.shp"),
                            recursive=True)
                  + glob.glob(op.join(ROOT, "extracted/**/*.tmp"),
                              recursive=True)):
            try:
                with open(p, "rb") as fh:
                    d = fh.read(0x40)
                if d[:4] == b"1.10":
                    _LIB_CACHE.setdefault(d, []).append(op.basename(p))
            except Exception:
                pass
    hits = _LIB_CACHE.get(head40, [])
    return hits[0] if len(set(hits)) >= 1 else None


def rec_lib_and_truth(a):
    """Attribute an attribution row: lib via cache name, else via rec_head
    bytes matched against extracted libraries (mouse PAY is OUTSIDE the
    200-slot cache — t330 finding). Returns (lib, record_index, dims_truth)
    where dims_truth checks the runtime hdr against BOTH candidate file
    slots: hdr == (u16@+2, u16@+0) [the +0 pair as (W-1,H-1)] vs
    hdr == (u32@+0x10, u32@+0x14)."""
    lib = (a.get("lib") or "").strip()
    rh = a.get("rec_head")
    if not rh:
        return lib or "?", None, None
    rb = bytes.fromhex(rh.replace(" ", ""))
    hits = []
    for p in _ALL_LIBS():
        d = _ALL_LIBS()[p]
        off = d.find(rb)
        if off >= 0:
            hits.append((op.basename(p), off, d))
    if not hits:
        return lib or "?", None, None
    nm, off, d = hits[0]
    lib = lib or nm
    k = None
    try:
        cnt = struct.unpack_from("<I", d, 4)[0]
        for kk in range(cnt):
            if struct.unpack_from("<Q", d, 8 + 8 * kk)[0] == off:
                k = kk
                break
    except Exception:
        pass
    truth = None
    hdr = a.get("hdr") or {}
    wm1, hm1 = hdr.get("Wm1"), hdr.get("Hm1")
    if wm1 is not None and hm1 is not None and off + 0x18 <= len(d):
        u0, u2 = struct.unpack_from("<HH", d, off)
        c, dd = struct.unpack_from("<II", d, off + 0x10)
        truth = {"file_u16_at0": [u0, u2], "file_u32_at0x10": [c, dd],
                 "hdr_at_stop": [wm1, hm1],
                 "plus0_pair_match": (wm1 == u2 and hm1 == u0),
                 "plus0x10_pair_match": (wm1 == c and hm1 == dd)}
    return lib, k, truth


_LIBS_ALL = None


def _ALL_LIBS():
    global _LIBS_ALL
    if _LIBS_ALL is None:
        _LIBS_ALL = {}
        for p in (glob.glob(op.join(ROOT, "extracted/**/*.shp"),
                            recursive=True)
                  + glob.glob(op.join(ROOT, "extracted/**/*.tmp"),
                              recursive=True)):
            try:
                _LIBS_ALL[p] = open(p, "rb").read()
            except Exception:
                pass
    return _LIBS_ALL


def analyze(run):
    """Post-hoc S4 verdict from banked attribution (no launch)."""
    ap = op.join(run, "blit_attrib.json")
    cp = op.join(run, "census.json")
    if not op.exists(ap):
        print(f"NO blit_attrib.json in {run}")
        return 2
    attrib = json.load(open(ap))
    census = json.load(open(cp))["pty_census"] if op.exists(cp) else {}
    rows = []
    for a in attrib:
        if "leg" not in a:                       # banked pre-fix rows
            a["leg"] = "blit_deref" if a.get("dir_rel") else "blit_entry"
        lib, k, truth = rec_lib_and_truth(a)
        rows.append({**a, "lib_resolved": lib, "rec_k": k, "dims_truth":
                     truth})
    libs = {}
    for r in rows:
        libs.setdefault(r["lib_resolved"], []).append(r)
    print(f"attribution rows: {len(attrib)}  libs: "
          f"{ {k: len(v) for k, v in libs.items()} }")
    print(f"census: {census}")
    mouse = [r for r in libs.get("mouse.shp", [])
             if "post-rearm" not in (r.get("phase_tag") or "")]
    for r in mouse:
        print("MOUSE ROW:", json.dumps({x: r.get(x) for x in
              ("phase_tag", "sel", "rec_k", "hdr", "dims_truth")}))
    refuses = [r for r in mouse if r.get("leg") == "blit_refuse"]
    derefs = [r for r in mouse if r.get("leg") == "blit_deref"]
    p0m = [r for r in derefs if (r["dims_truth"] or {}).get(
        "plus0_pair_match")]
    p10m = [r for r in derefs if (r["dims_truth"] or {}).get(
        "plus0x10_pair_match")]
    if refuses:
        v = ("CANONICAL-SLOT: vendor REFUSED mouse records at the dims gate "
             "(blit_refuse attributed to MOUSE lib)")
    elif derefs and p0m and not p10m:
        v = ("DRAW-TIME DIMS = u16 PAIR AT rec+0: every mouse deref stop "
             f"({len(p0m)}/{len(derefs)}) has hdr (W-1,H-1) == "
             "(u16@+2, u16@+0) of the MATCHED record file bytes and NONE "
             "match the u32@+0x10 pair — slot-location dispute DECIDED "
             "for +0 (order: H-1 stored first at +0). Never-selected "
             "k5/k6/k7 (windows.txt requests CURSORSHAPE 2 only) stay "
             "drawn-frame UNWITNESSED but inherit the measured +0 law: "
             "their u16@+0 (46,77) = 78x47 VALID dims -> the 'invalid "
             "dims' C-row classification is REFUTED for C27-C29.")
    elif derefs:
        v = ("MOUSE DREW — hdr/dims correspondence MIXED, inspect rows "
             "(no clean +0 vs +0x10 verdict)")
    else:
        v = ("HONEST NEGATIVE: no mouse-attributed deref banked this run")
    verdict = {"census": census, "libs": {k: len(v) for k, v in libs.items()},
               "mouse_hits": len(mouse),
               "mouse_sels": sorted({r.get("sel") for r in mouse}),
               "plus0_matches": len(p0m), "plus0x10_matches": len(p10m),
               "verdict": v}
    print("VERDICT:", v)
    with open(op.join(run, "verdict.json"), "w") as fh:
        json.dump(verdict, fh, indent=1)
    return 0


def live_attempt(tag, window, disp, port, tl, settle):
    ds = BlitSess(tag, ALL_LEGS, PHASES, window, disp, port, tl, settle, 0)
    s = ds.s
    try:
        s.log(f"t330 attempt2 start out={s.out} legs={ALL_LEGS} "
              f"cache={hex(CACHE)} window={window}")
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
        # t330 ORDERING FIX: blit_attrib.json was atexit-only, so the
        # in-process analyze() saw no file and returned 2 on a GOOD run
        # (both t330 attempts exited 1 despite rc=0 banking). Write the
        # artifacts before analyze() runs; bank_on_exit stays idempotent.
        ds.bank_on_exit()
        with open(op.join(s.out, "phases.json"), "w") as fh:
            json.dump({k: (v if isinstance(v, (dict, int, float, bool))
                           else (0 if v is None else len(v)))
                       for k, v in ph_res.items()}, fh, indent=1)
        return 0
    finally:
        ds.teardown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="t330b")
    ap.add_argument("--window", type=int, default=18)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55999)
    ap.add_argument("--tl", type=int, default=7200)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--offline", default=None, metavar="RUN_DIR")
    args = ap.parse_args()

    if args.offline:
        rc = D.offline_run(op.abspath(args.offline), [], ALL_LEGS)
        return analyze(op.abspath(args.offline)) or rc

    rc = D.preflight(ALL_LEGS)
    if rc:
        return rc
    if not D.port_free(args.port):
        print(f"HARNESS ERROR: MCP port {args.port} busy")
        return 2
    last = 1
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
        last = 1
    return last


if __name__ == "__main__":
    sys.exit(main())
