#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_facilities.py -- courthouses, consulates and border posts from OSM.

    python3 harvest_facilities.py --all
    python3 harvest_facilities.py --courthouse --dry-run -v

Writes facilities.json.

WHY THIS EXISTS
---------------
The facility layer is fed by a dataset built for a sibling map, and that dataset
carries police stations, town halls and government offices but not the three
types that are actually useful here -- which is why courthouse, embassy and
border post all showed a count of zero. It is not a tag mismatch; the records
are not in the source.

WHY THESE THREE AND NOT THE OTHERS
----------------------------------
Every one of these has a function relevant to this subject at EVERY instance:

  courthouse       any courthouse hears a case, takes a wage claim, issues a
                   judgment. The physical venue for the courts lens.
  embassy /        for a worker whose passport is held, the sending country's
  consulate        consulate is often the only body that can issue replacement
                   documents or arrange repatriation.
  border /         where import bans are enforced and goods detained, and a
  customs post     named point on corridor data.

Police stations stay in the layer for the same reason: a report can be made at
any of them. That is the test -- the function is universal, so plotting all of
them asserts nothing about which ones are special.

Town halls and generic government offices failed that test and were removed.
256,000 civic buildings filtered by nothing is a proxy for "a town is here", and
the description was doing work the data could not support.

ON POLICE STATIONS SPECIFICALLY
-------------------------------
Worth stating plainly because the map cuts both ways on this. A police station
is where a member of the public reports a crime, and for a third party who
discovers forced labour it is usually the right call. For the worker, in several
jurisdictions, walking into one without status means being treated as an
immigration case rather than a victim -- which is why the survivor lens lists
specialist hotlines first and the police-station record says so.
"""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "facilities.json")
UA = "welcometoyourgalaxy-map/1.0 (civic research; contact via github)"

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
]

KINDS = {
    "courthouse": {
        "k": "ch",
        "q": 'node["amenity"="courthouse"];way["amenity"="courthouse"];',
        "label": "Courthouse",
        "desc": ("Courthouse. Where prosecutions for trafficking and forced labour are "
                 "heard, where wage and damages claims are filed, and where judgments "
                 "are collected \u2014 the physical venue for the courts lens. Check "
                 "which court has jurisdiction before travelling: labour claims and "
                 "criminal trafficking cases are often heard in different buildings."),
    },
    "embassy": {
        "k": "dp",
        "q": ('node["amenity"="embassy"];way["amenity"="embassy"];'
              'node["office"="diplomatic"];way["office"="diplomatic"];'),
        "label": "Embassy / consulate",
        "desc": ("Embassy or consulate \u2014 the sending country's presence in the "
                 "destination country. For a migrant worker whose passport is held by "
                 "an employer or agent, the consulate is often the only body that can "
                 "issue replacement documents or arrange repatriation, and it can do so "
                 "without the employer's consent. Several also run their own welfare "
                 "funds for nationals abroad."),
    },
    "border": {
        "k": "bd",
        "q": ('node["barrier"="border_control"];way["barrier"="border_control"];'
              'node["amenity"="customs"];way["amenity"="customs"];'),
        "label": "Border / customs post",
        "desc": ("Border or customs post. Where import bans are actually enforced and "
                 "goods detained, and a named point on many documented corridors. The "
                 "customs authority here is the body that acts on a withhold release "
                 "order or an equivalent measure."),
    },
}


def fetch(url, data, timeout=300):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url, data=urllib.parse.urlencode({"data": data}).encode(),
        headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def run_query(body, verbose=False):
    q = "[out:json][timeout:280];(%s);out center tags;" % body
    for ep in ENDPOINTS:
        try:
            raw = fetch(ep, q)
            j = json.loads(raw.decode("utf-8", "replace"))
            els = j.get("elements") or []
            print("  %-42s %d elements" % (ep.split("/")[2], len(els)))
            return els
        except Exception as ex:
            print("  %-42s %s" % (ep.split("/")[2], str(ex)[:44]))
            time.sleep(3)
    return []


def to_records(els, spec):
    out = []
    for e in els:
        lat = e.get("lat") or (e.get("center") or {}).get("lat")
        lon = e.get("lon") or (e.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        t = e.get("tags") or {}
        name = t.get("name") or t.get("name:en") or spec["label"]
        out.append({
            "name": str(name)[:120],
            "k": spec["k"],
            "type": spec["label"],
            "lat": float(lat), "lng": float(lon),
            "country": t.get("country") or t.get("addr:country") or "",
            "url": ("https://www.openstreetmap.org/%s/%s"
                    % (e.get("type", "node"), e.get("id", ""))),
            "desc": spec["desc"],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("courthouse", "embassy", "border", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.courthouse, a.embassy, a.border, a.all]):
        ap.error("choose --courthouse, --embassy, --border or --all")

    recs = []
    for key, spec in KINDS.items():
        if not (a.all or getattr(a, key)):
            continue
        print("=== %s ===" % spec["label"])
        # Global queries for these three are small enough to run whole: there
        # are tens of thousands of courthouses worldwide, not millions. That is
        # exactly why they are worth plotting and town halls are not.
        recs += to_records(run_query(spec["q"], a.verbose), spec)

    print("total: %d" % len(recs))
    if a.dry_run or not recs:
        for r in recs[:12]:
            print("  %-38s %8.3f %9.3f" % (r["name"][:38], r["lat"], r["lng"]))
        if not recs:
            print("Nothing harvested. Overpass rate-limits hard; try again in a few "
                  "minutes, or run one --flag at a time rather than --all.")
        return 0 if recs else 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "source": "OpenStreetMap via Overpass",
                   "note": ("Courthouses, consulates and border posts. Each has a "
                            "function relevant to this subject at every instance, "
                            "which is why all of them are plotted."),
                   "facilities": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
