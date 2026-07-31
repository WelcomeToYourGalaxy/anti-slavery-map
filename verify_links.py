#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_links.py -- live-check every URL that ships in the map.

This project's standard is that a dead or wrong link is a defect, not a
cosmetic issue. Run this before deploying, and again whenever
trackerdata.json grows.

    python3 verify_links.py                    # check everything
    python3 verify_links.py --only trackerdata # or: index, seed
    python3 verify_links.py --workers 12 --timeout 20
    python3 verify_links.py --csv report.csv

Exit code is 1 if anything failed, so it can gate a deploy.

Notes on interpreting the output:
  OK          2xx, or a redirect chain ending in 2xx
  REDIRECT    ends somewhere else -- check the final URL is still the thing
              you meant; government sites reorganise constantly
  403 / 405   often a bot block rather than a dead page. Re-check by hand
              before removing an entry; several national labour ministries
              refuse HEAD and non-browser user agents.
  TIMEOUT     common for .gov.in, .go.ke, .gov.pk -- retry before believing it
  DEAD        4xx/5xx that persisted on retry. Fix or drop the entry.
"""

import argparse
import csv
import io
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")


# --------------------------------------------------------------- collection
def from_trackerdata(path):
    """Every url in trackerdata.json, at country / region / sub-region level."""
    out = []
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)
    for iso, country in data.items():
        label = country.get("name") or iso

        def walk(node, where):
            for t in (node.get("trackers") or []):
                if t.get("url"):
                    out.append((t["url"], t.get("name", ""), where))
            for name, child in (node.get("sub") or {}).items():
                walk(child, where + " / " + name)

        walk(country, label)
    return out


def from_index(path):
    """URLs inside internationalBodies[] and the PJ_SEED case list."""
    with io.open(path, encoding="utf-8") as f:
        doc = f.read()
    out = []

    m = re.search(r"const internationalBodies\s*=\s*\[(.*?)\n\];", doc, re.S)
    if m:
        body = m.group(1)
        cur = "International bodies"
        for line in body.split("\n"):
            b = re.search(r'\{"name":"([^"]+)","(?:guide|lat)"', line)
            if b:
                cur = b.group(1)
            for u, n in re.findall(r'"url":"(https?://[^"]+)"', line), []:
                pass
            for u in re.findall(r'"url":"(https?://[^"]+)"', line):
                nm = re.search(r'"name":"([^"]+)","url"', line)
                out.append((u, nm.group(1) if nm else "", cur))

    m = re.search(r'var PJ_SEED=\{"projects":\[(.*?)\n\s*\]\};', doc, re.S)
    if m:
        for u in re.findall(r'"url":"(https?://[^"]+)"', m.group(1)):
            out.append((u, "", "case seed"))

    m = re.search(r"const WIRE_FEEDS\s*=\s*(\[.*?\]);", doc, re.S)
    if m:
        for name, url in re.findall(r'\["([^"]+)",\s*"(https?://[^"]+)"\]', m.group(1)):
            out.append((url, name, "wire feed"))
    return out


# --------------------------------------------------------------- checking
def check(url, timeout):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # several state sites have stale chains
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method,
                                     headers={"User-Agent": UA,
                                              "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                final = r.geturl()
                code = r.getcode()
                if final.rstrip("/") != url.rstrip("/"):
                    return ("REDIRECT", code, final)
                return ("OK", code, "")
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # some servers only answer GET
            return ("DEAD" if e.code >= 400 else "OK", e.code, "")
        except (urllib.error.URLError, ssl.SSLError, OSError) as e:
            if method == "HEAD":
                continue
            reason = getattr(e, "reason", e)
            kind = "TIMEOUT" if "timed out" in str(reason).lower() else "ERROR"
            return (kind, 0, str(reason)[:90])
    return ("ERROR", 0, "no method succeeded")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["trackerdata", "index", "seed", "all"],
                    default="all")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--csv")
    args = ap.parse_args()

    targets = []
    td = os.path.join(HERE, "trackerdata.json")
    ix = os.path.join(HERE, "index.html")
    if args.only in ("trackerdata", "all") and os.path.exists(td):
        targets += from_trackerdata(td)
    if args.only in ("index", "seed", "all") and os.path.exists(ix):
        targets += from_index(ix)

    # de-duplicate on url, keeping the first place it was seen
    seen, uniq = set(), []
    for u, n, w in targets:
        if u not in seen:
            seen.add(u)
            uniq.append((u, n, w))

    print("checking %d unique URLs (%d workers, %ds timeout)\n"
          % (len(uniq), args.workers, args.timeout))

    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = pool.map(lambda t: (t, check(t[0], args.timeout)), uniq)
        for (url, name, where), (status, code, extra) in results:
            rows.append(dict(status=status, code=code, url=url,
                             name=name, where=where, detail=extra))
            if status != "OK":
                print("%-9s %-4s %s\n          %s | %s%s"
                      % (status, code or "-", url, where, name,
                         ("\n          -> " + extra) if extra else ""))

    from collections import Counter
    tally = Counter(r["status"] for r in rows)
    print("\n" + "-" * 60)
    for k in ("OK", "REDIRECT", "TIMEOUT", "ERROR", "DEAD"):
        if tally.get(k):
            print("%-9s %d" % (k, tally[k]))

    if args.csv:
        with io.open(args.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["status", "code", "url",
                                              "name", "where", "detail"])
            w.writeheader()
            w.writerows(rows)
        print("\nwrote", args.csv)

    return 1 if (tally.get("DEAD") or tally.get("ERROR")) else 0


if __name__ == "__main__":
    sys.exit(main())
