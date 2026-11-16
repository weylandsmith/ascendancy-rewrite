#!/usr/bin/env python3
"""t403 self-test for the ruling channel (in-process, scratch targets only).

Rules obeyed (t397/t397b): D11_DECISIONS_FILE points at a SCRATCH file, NEVER
docs/DECISIONS.md; scratch port; the real server on 8613 is not touched.
Checks: POST fields -> USER: lines; GET / serves the D12 sheet; traversal 403.
"""
import json
import os
import os.path as op
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, "/home/hrethric/projects/ascendancy/work/r1/d1page")
os.environ["D11_DECISIONS_FILE"] = "/tmp/t403_scratch_decisions.md"
if op.exists(os.environ["D11_DECISIONS_FILE"]):
    os.remove(os.environ["D11_DECISIONS_FILE"])

import server  # noqa: E402

PORT = 8699
httpd = ThreadingHTTPServer(("127.0.0.1", PORT), server.H)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

body = json.dumps({"title": "D12",
                   "fields": [["D12 selftest =", "ok"],
                              ["D12 planets list =", "usable rows look right"]]}).encode()
with urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:%d/ruling" % PORT, data=body), timeout=5) as r:
    print("POST", r.status, r.read().decode())

with urllib.request.urlopen("http://127.0.0.1:%d/" % PORT, timeout=5) as r:
    html = r.read().decode()
print("GET /", r.status, "D12-mentions:", html.count("D12"))

try:
    urllib.request.urlopen(
        "http://127.0.0.1:%d/d11/..%%2f..%%2fetc%%2fpasswd" % PORT, timeout=5)
    print("TRAVERSAL: NOT BLOCKED -- FAIL")
except urllib.error.HTTPError as e:
    print("TRAVERSAL:", e.code, "PASS" if e.code in (403, 404) else "CHECK")

written = open(os.environ["D11_DECISIONS_FILE"]).read()
print("--- scratch DECISIONS tail:")
print(written)
ok = ("USER: D12 selftest = ok" in written
      and "USER: D12 planets list = usable rows look right" in written)
httpd.shutdown()
print("SELFTEST", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
