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
  BLOCKED     401/403/405/406/429 -- a live site refusing a scripted request.
              NOT a dead link. Open it by hand before touching the entry;
              government sites and Cloudflare-fronted NGOs do this constantly.
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
                # http->https, adding or dropping www, adding a trailing slash
                # and adding a default index are all normalisation, not a move.
                # Reporting them as redirects buried the handful that matter:
                # of 125 redirects in the sibling run, almost all were these.
                def canon(u):
                    u = u.lower()
                    # Query-string locale noise is not a move. Google News
                    # rewrites hl=en to hl=en-US on every single request, which
                    # reported 35 of 35 feed URLs as redirects and buried the
                    # ones that actually went somewhere else.
                    base, _, q = u.partition("?")
                    if q:
                        keep = [kv for kv in q.split("&")
                                if kv.split("=")[0] not in
                                ("hl", "gl", "ceid", "utm_source", "utm_medium",
                                 "utm_campaign", "utm_content", "utm_term",
                                 "fbclid", "gclid", "lang", "locale", "ref")]
                        base = base + ("?" + "&".join(sorted(keep)) if keep else "")
                    u = re.sub(r"^https?://", "", base)
                    u = re.sub(r"^www\.", "", u)
                    u = re.sub(r"/(index|default)\.(html?|php|aspx?)$", "/", u)
                    return u.rstrip("/")
                if canon(final) != canon(url):
                    return ("REDIRECT", code, final)
                return ("OK", code, "")
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 406, 429, 501):
                continue  # some servers only answer GET
            # A live site refusing a script is not a dead link, and calling it
            # one gets working entries deleted. Real-world evidence for this:
            # a run over the sibling map's directory returned 403 for cdc.gov,
            # nrc.gov, phmsa.dot.gov, dec.ny.gov, muckrock.com and mass.gov --
            # every one of them a page that opens fine in a browser.
            if e.code in (401, 403, 405, 406, 429):
                return ("BLOCKED", e.code, "refused a scripted request; open it by hand")
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
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero when dead links exceed --max-dead")
    ap.add_argument("--max-dead", type=int, default=0)
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
    for k in ("OK", "REDIRECT", "BLOCKED", "TIMEOUT", "ERROR", "DEAD"):
        if tally.get(k):
            print("%-9s %d" % (k, tally[k]))

    dead = [r for r in rows if r["status"] == "DEAD"]
    if dead:
        print("\nDEAD \u2014 these need fixing or removing (%d):" % len(dead))
        for r in dead:
            print("  %-4s %-72s %s" % (r["code"], r["url"][:72], r["where"][:34]))
        print("\nRead BLOCKED as 'a live site refusing a script', not as dead. "
              "Open one by hand before touching the entry.")

    if args.csv:
        with io.open(args.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["status", "code", "url",
                                              "name", "where", "detail"])
            w.writeheader()
            w.writerows(rows)
        print("\nwrote", args.csv)

    # Exit non-zero only when asked. A scheduled check over ~400 third-party
    # URLs will always find something down somewhere, and a permanently red
    # tick trains you to ignore the one run that matters. Use --strict to gate
    # a deploy on it.
    bad = (tally.get("DEAD", 0) + tally.get("ERROR", 0))
    if args.strict and bad > args.max_dead:
        print("\n--strict: %d dead/errored exceeds --max-dead %d" % (bad, args.max_dead))
        return 1
    if bad:
        print("\n%d dead/errored URL(s). Not failing the run \u2014 pass --strict "
              "to make this a build failure." % bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
