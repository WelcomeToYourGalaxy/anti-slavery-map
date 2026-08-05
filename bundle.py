#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bundle.py -- fold every data layer into one self-contained index.html.

    python3 bundle.py                 # writes index.bundle.html
    python3 bundle.py --inplace       # overwrites index.html
    python3 bundle.py --report        # sizes only, writes nothing

WHY
---
The map loads seven optional side files at runtime. That is the right shape for
a repository that harvests on a schedule, and the wrong shape for a person who
has to upload files by hand: eight uploads to change one thing, and a map that
silently loses a layer if one of them does not land.

This produces a single file with everything already inside it. Nothing to keep
in sync, nothing to forget, and it matches how the rest of this project ships --
one HTML file you can drop anywhere.

The runtime is unchanged: the loader still fetches the side files first, and
only falls back to the embedded copy when a fetch misses. So a bundled file
deployed next to freshly harvested JSON uses the fresh JSON, and the same file
deployed alone still works. Bundling adds a floor; it does not freeze anything.

COMPACTION
----------
Most of the bulk is repeated prose: 3,128 mining sites share 62 distinct
description endings, and those endings are 1.7 MB of the 2.8 MB. Each unique
tail is stored once and referenced by index. Purely mechanical -- no text is
dropped, and the map reassembles the full string before displaying it.
"""

import argparse
import io
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LAYERS = ["projects.json", "cases.json", "prevalence.json", "points.json",
          "bulk.json", "directory.json", "wire.json", "hotlines.json",
          "routes.json", "infra.json", "facilities.json", "sites.json", "companies.json", "law.json", "suspected.json"]

# Layers deliberately left OUT of the bundle and fetched at runtime instead.
# infra.json is 3,630 ports at 2.1 MB embedded -- a quarter of the file for the
# layer that is least likely to be why anyone opened the map. Kept as a separate
# fetch so the single-file build stays around 5 MB and the ports still appear
# whenever infra.json is deployed alongside it.
DEFAULT_EXTERNAL = ["infra.json", "facilities.json"]
MARK = "\u0001"          # never appears in the source text


def compact(obj):
    """Factor repeated description tails into a table. Reversible, lossless."""
    recs = obj.get("projects") if isinstance(obj, dict) else None
    if not isinstance(recs, list) or len(recs) < 50:
        return obj, 0
    tails = Counter()
    for r in recs:
        d = r.get("desc")
        if isinstance(d, str) and len(d) > 160:
            tails[d[-260:]] += 1
    common = [t for t, n in tails.most_common(120) if n >= 3]
    if not common:
        return obj, 0
    idx = {t: i for i, t in enumerate(common)}
    saved = 0
    for r in recs:
        d = r.get("desc")
        if not isinstance(d, str) or len(d) <= 160:
            continue
        t = d[-260:]
        if t in idx:
            r["desc"] = d[:-260] + MARK + str(idx[t]) + MARK
            saved += len(t) - 4
    obj["_tails"] = common
    return obj, saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inplace", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--no-compact", action="store_true")
    ap.add_argument("--external", action="append", metavar="FILE",
                    help="fetch this layer at runtime instead of embedding it")
    ap.add_argument("--embed", action="append", metavar="FILE",
                    help="embed a layer that is external by default (e.g. infra.json)")
    a = ap.parse_args()

    src = os.path.join(HERE, "index.html")
    if not os.path.exists(src):
        print("index.html not found next to this script. cd into the repo first.")
        return 1
    with io.open(src, encoding="utf-8") as f:
        html = f.read()

    if "window.__BUNDLED" in html:
        # strip a previous bundle so re-running does not stack copies
        html = re.sub(r"<script id=\"bundled-data\">.*?</script>\n?", "", html, flags=re.S)
        print("removed a previous bundle before rebuilding")

    bundle, rows = {}, []
    external = set(DEFAULT_EXTERNAL)
    for fn in (a.embed or []):
        external.discard(fn)
    for fn in (a.external or []):
        external.add(fn)

    for fn in LAYERS:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            rows.append((fn, 0, 0, "not present"))
            continue
        if fn in external:
            rows.append((fn, 0, 0, "loaded separately (deploy it alongside)"))
            continue
        try:
            with io.open(p, encoding="utf-8") as f:
                obj = json.load(f)
        except Exception as ex:
            rows.append((fn, 0, 0, "unreadable: " + str(ex)[:40]))
            continue
        raw = os.path.getsize(p)
        if not a.no_compact:
            obj, _ = compact(obj)
        blob = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        bundle[fn] = obj
        n = len(obj.get("projects", obj.get("providers", obj.get("hotlines", [])))) \
            if isinstance(obj, dict) else 0
        rows.append((fn, n, len(blob), "%.0f%% of %d KB" % (100.0 * len(blob) / max(raw, 1), raw // 1024)))

    print("%-18s %8s %10s   %s" % ("layer", "records", "embedded", "note"))
    for fn, n, b, note in rows:
        print("%-18s %8s %9dK   %s" % (fn, n or "-", b // 1024, note))

    if a.report:
        return 0
    if not bundle:
        print("\nNo data layers present to bundle. Run the harvesters first.")
        return 1

    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")      # cannot end the script element

    script = (
        '<script id="bundled-data">\n'
        '/* Every data layer, embedded. Written by bundle.py.\n'
        '   The loader still prefers a real file on disk \u2014 this is the floor it\n'
        '   falls back to, so one file works alone and also picks up fresh\n'
        '   harvest output when that is deployed beside it. */\n'
        'window.__BUNDLED = ' + payload + ';\n'
        '(function(){\n'
        '  /* Repeated description endings are stored once per layer and referenced\n'
        '     by index; put them back before anything reads them. */\n'
        '  var M="\\u0001";\n'
        '  Object.keys(window.__BUNDLED).forEach(function(k){\n'
        '    var o=window.__BUNDLED[k], t=o&&o._tails;\n'
        '    if(!t||!o.projects) return;\n'
        '    o.projects.forEach(function(r){\n'
        '      if(typeof r.desc!=="string") return;\n'
        '      var i=r.desc.indexOf(M);\n'
        '      if(i<0) return;\n'
        '      var j=r.desc.indexOf(M,i+1);\n'
        '      var n=parseInt(r.desc.slice(i+1,j),10);\n'
        '      if(!isNaN(n)&&t[n]!=null) r.desc=r.desc.slice(0,i)+t[n];\n'
        '    });\n'
        '    delete o._tails;\n'
        '  });\n'
        '})();\n'
        '</script>\n')

    out_html = html.replace("</head>", script + "</head>", 1)
    dest = src if a.inplace else os.path.join(HERE, "index.bundle.html")
    with io.open(dest, "w", encoding="utf-8") as f:
        f.write(out_html)
    print("\nwrote %s \u2014 %.1f MB, %d layer(s) embedded"
          % (os.path.basename(dest), os.path.getsize(dest) / 1048576.0, len(bundle)))
    if external:
        print("Deploy alongside it: %s \u2014 %s"
              % (", ".join(sorted(external)),
                 "fetched at runtime rather than embedded, to keep the single "
                 "file a sensible size. Use --embed to fold one back in."))
    print("The side JSON files stay in the repo for the harvesters to keep "
          "refreshing; they are used in preference when present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
