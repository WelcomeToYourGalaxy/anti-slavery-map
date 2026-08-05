#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_vessels.py -- the only thing on this map that moves.

    python3 harvest_vessels.py --grid
    python3 harvest_vessels.py --named --token YOUR_GFW_TOKEN
    python3 harvest_vessels.py --all --token YOUR_GFW_TOKEN

Writes vessels.json.

TWO LAYERS, DELIBERATELY DIFFERENT COLOURS
------------------------------------------
  named   Vessels under an OFFICIAL DESIGNATION, by name and IMO: on an RFMO
          IUU list, or named in a US withhold release order. Roughly 29 of
          them. Each is a determination about an identified ship, and each one
          can be looked up, written about and asked about. Positions come from
          Global Fishing Watch.

  grid    Where the published model says at-risk fishing effort is, as a 2.5
          degree grid. NOT vessels. Nobody is identified and nobody could be:
          the PNAS authors anonymised every vessel in their release, and that
          was the right call on a method contested in the same journal.

The two must never be drawn the same. One is "this ship, by name, is on a
list"; the other is "the model puts unusual amounts of at-risk effort in this
square of ocean". Colour and shape carry that difference, because a reader who
conflates them will believe the map has identified thousands of slave ships,
which it has not and cannot.

WHAT THE GRID ACTUALLY ANSWERS
------------------------------
Your question was whether the anonymised data still gives a grasp of how many
are out there. It does, at sea rather than by hull: the model's at-risk effort
concentrates hard. Half the ocean cells carry 95% of it, and the single
heaviest square is the southwest Atlantic off Argentina -- the squid jigger
grounds, which is also the gear class the paper scored highest.
"""

import argparse
import csv
import io
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "vessels.json")
UA = "welcometoyourgalaxy-map/1.0"

GFW_SEARCH = ("https://gateway.api.globalfishingwatch.org/v3/vessels/search"
              "?query=%s&datasets[0]=public-global-vessel-identity:latest&limit=5")
GFW_EVENTS = ("https://gateway.api.globalfishingwatch.org/v3/events"
              "?datasets[0]=public-global-port-visits-events:latest"
              "&vessels[0]=%s&start-date=%s&end-date=%s&limit=1&sort=-start")


def fetch(url, token=None, timeout=90):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    h = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def find_export(*patterns):
    if not os.path.isdir(DATA_DIR):
        return None
    for f in sorted(os.listdir(DATA_DIR)):
        low = f.lower()
        if low.endswith((".csv", ".json")) and any(p in low for p in patterns):
            p = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return p
    return None


# ======================================================================= GRID
def harvest_grid(a):
    src = find_export("atrisk_grid", "pnas_grid", "atrisk")
    if not src:
        print("  No at-risk grid. Extract it from the PNAS reproduction repo: "
              "interim_data/s5_figure_3_data.csv in "
              "github.com/emlab-ucsb/slavery-in-fisheries, summed across gears, "
              "and commit as data/pnas_atrisk_grid.csv with columns lat, lng, "
              "at_risk_kwh, total_kwh, share, gears.")
        return []
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    if not rows:
        return []
    vals = sorted(float(r["at_risk_kwh"]) for r in rows)
    p90 = vals[int(len(vals) * 0.90)]
    p99 = vals[int(len(vals) * 0.99)]
    cut = vals[int(len(vals) * (1 - a.top))]

    # Every cell carrying its own paragraph came to 25 MB for a layer whose
    # whole message is "it concentrates here". Below the threshold the cells add
    # weight and no signal, so only the heaviest are drawn and the run says how
    # many were left out.
    skipped = 0
    out = []
    for r in rows:
        try:
            lat, lng = float(r["lat"]), float(r["lng"])
            v = float(r["at_risk_kwh"])
        except (KeyError, TypeError, ValueError):
            continue
        if v < cut:
            skipped += 1
            continue
        share = r.get("share") or ""
        gears = (r.get("gears") or "").replace("_", " ")
        out.append({
            "name": "At-risk fishing effort",
            "source": "atrisk", "type": "Modelled at-risk fishing effort",
            "lat": lat, "lng": lng, "precise": False, "local": True,
            "impact": 5 if v >= p99 else 4 if v >= p90 else 3,
            "status": ("%s%% of effort here" % share) if share else "Modelled",
            "state": "At sea",
            "url": "https://github.com/emlab-ucsb/slavery-in-fisheries",
            "desc": (("A 2.5\u00b0 cell of ocean in which the published model attributes "
                      "%s kW-hours of fishing effort to vessels it scored high-risk for "
                      "forced labour" % format(int(v), ","))
                     + ((", %s%% of all effort recorded in this cell" % share) if share else "")
                     + ((". Gear: %s" % gears) if gears else "") + ". "
                     + "<b>This is not a vessel and nobody here is identified.</b> The "
                       "authors anonymised every hull in their release, and on a method "
                       "contested in the same journal that was the right call. What the "
                       "cell says is where the model puts unusual amounts of at-risk "
                       "effort \u2014 useful for grasping the scale and the geography, "
                       "useless for pointing at a ship. "
                     + "McDonald et al., PNAS 2021, 2018 effort. Compare it with the "
                       "named-vessel layer, which is the opposite: few points, each an "
                       "official designation against an identified ship."),
        })
    print("  at-risk cells: %d drawn, %d below the threshold and left out "
          "(--top %.2f)" % (len(out), skipped, a.top))
    return out


# ====================================================================== NAMED
def harvest_named(a):
    """Vessels under an official designation, positioned via GFW."""
    src = find_export("iuu_vessel", "named_vessel", "wro_vessel", "iuu")
    listed = []
    if src:
        for r in csv.DictReader(open(src, encoding="utf-8-sig")):
            lo = {str(k).lower().replace(" ", "").replace("_", ""): v for k, v in r.items()}
            nm = str(lo.get("name") or lo.get("vessel") or "").strip()
            if nm:
                listed.append({"name": nm,
                               "imo": str(lo.get("imo") or "").strip(),
                               "flag": str(lo.get("flag") or "").strip(),
                               "listing": str(lo.get("listing") or lo.get("source")
                                              or lo.get("rfmo") or "").strip()})
    else:
        # bulk.json already carries the IUU vessels this map harvested
        bp = os.path.join(HERE, "bulk.json")
        if os.path.exists(bp):
            try:
                for x in json.load(open(bp, encoding="utf-8")).get("projects", []):
                    if x.get("source") == "iuu":
                        listed.append({"name": x.get("name", ""),
                                       "imo": str(x.get("imo") or ""),
                                       "flag": x.get("state", ""),
                                       "listing": "RFMO IUU list"})
                print("  read %d IUU vessels from bulk.json" % len(listed))
            except Exception as ex:
                print("  could not read bulk.json: %s" % str(ex)[:50])
    if not listed:
        print("  No named vessels. They come from bulk.json (harvest_bulk.py --iuu) "
              "or a committed CSV in data/ with columns name, imo, flag, listing.")
        return []
    if not a.token:
        print("  %d named vessels, but no Global Fishing Watch token, so no positions. "
              "Pass --token, or set GFW_TOKEN in the workflow secrets." % len(listed))
        return []

    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=a.days)
    out, found = [], 0
    for v in listed:
        q = v["imo"] or v["name"]
        if not q:
            continue
        try:
            time.sleep(0.4)
            j = json.loads(fetch(GFW_SEARCH % urllib.parse.quote(q), a.token)
                           .decode("utf-8", "replace"))
        except Exception as ex:
            if a.verbose:
                print("    %-28s search failed: %s" % (v["name"][:28], str(ex)[:36]))
            continue
        ent = (j.get("entries") or j.get("data") or [])
        if not ent:
            continue
        vid = ent[0].get("id") or ent[0].get("vesselId")
        pos = None
        if vid:
            try:
                time.sleep(0.4)
                e = json.loads(fetch(GFW_EVENTS % (vid, start.isoformat(), end.isoformat()),
                                     a.token).decode("utf-8", "replace"))
                ev = (e.get("entries") or e.get("data") or [])
                if ev:
                    p = ev[0].get("position") or {}
                    if p.get("lat") is not None:
                        pos = (float(p["lat"]), float(p["lon"]), ev[0].get("start"))
            except Exception:
                pass
        if not pos:
            continue
        found += 1
        out.append({
            "name": v["name"][:110],
            "source": "vessel", "type": "Listed vessel \u2014 last known position",
            "lat": pos[0], "lng": pos[1], "precise": True,
            "impact": 5, "status": str(pos[2] or "")[:10] or "Last seen",
            "state": v["flag"] or "",
            "url": "https://globalfishingwatch.org/",
            "desc": (("<b>%s</b>%s is under an official designation: %s. "
                      % (v["name"], (" (IMO %s)" % v["imo"]) if v["imo"] else "",
                         v["listing"] or "listed"))
                     + "The position is its last recorded port visit in Global Fishing "
                       "Watch, not a live track \u2014 a vessel that has gone dark has no "
                       "position to show, which is itself the point. "
                     + "<b>This is a named ship on a published list</b>, not a model "
                       "output. Compare it with the at-risk effort grid, which "
                       "identifies nobody."),
        })
    print("  named vessels positioned: %d of %d" % (found, len(listed)))
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("grid", "named", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--token", default=os.environ.get("GFW_TOKEN"))
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--top", type=float, default=0.10,
                    help="fraction of at-risk cells to draw, heaviest first")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.grid, a.named, a.all]):
        ap.error("choose --grid, --named or --all")

    recs = []
    if a.named or a.all:
        print("=== Named vessels under official designation ===")
        recs += harvest_named(a)
    if a.grid or a.all:
        print("=== Modelled at-risk fishing effort ===")
        recs += harvest_grid(a)

    print("total: %d" % len(recs))
    if a.dry_run or not recs:
        return 0 if recs else 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "note": ("Two layers that must not be confused: named vessels under "
                            "an official designation, and a modelled grid identifying "
                            "nobody."),
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
