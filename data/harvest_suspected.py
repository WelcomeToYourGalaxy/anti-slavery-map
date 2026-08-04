#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_suspected.py -- subnational geography of where it is thought to be,
not where it was found.

    python3 harvest_suspected.py --ncrb
    python3 harvest_suspected.py --polaris
    python3 harvest_suspected.py --hotspots
    python3 harvest_suspected.py --all

Writes suspected.json.

THE PROBLEM THIS ANSWERS
------------------------
Roughly 50 million people are estimated to be in modern slavery. Every case
record on this map, from every source combined, describes about 270,000 of them.
The other 99% has never been detected, recorded or counted by anyone, so there
is no detection dataset that can show it.

What exists instead is a smaller, stranger class of data: subnational estimates,
signals and programme geographies that say *this is where it is thought to be*.
None of it is a finding. All of it is more honest about being an estimate than
the detection data is about being a fraction.

  ncrb        India's National Crime Records Bureau publishes human trafficking
              and bonded labour cases by STATE and district. Official, annual,
              and subnational -- rare anywhere and almost unique at this scale.

  polaris     The US National Human Trafficking Hotline publishes signals by
              state. A signal is a contact, not a case: the same person may
              contact twice and most contacts are not victims. It maps where
              people know the number and are able to call, which is a real thing
              to know and not the thing it looks like.

  hotspots    Freedom Fund hotspot programmes. Not an estimate at all -- these
              are the subnational geographies where a funder concentrated after
              its own assessment. Bihar and Uttar Pradesh kilns, Tamil Nadu
              spinning mills, the Nepal Terai, Ethiopian domestic work
              corridors, Thai seafood. Someone looked hard and decided this is
              where to work.

WHY THESE THREE AND NOT A MODEL
-------------------------------
There are vulnerability indices that would produce a smooth global surface at
subnational level. They are built from proxies -- poverty, conflict,
governance -- and they would give this map a confident-looking heat layer whose
colour was decided by a regression rather than by anyone observing anything.

The map already has one honest measure of what is not seen: prevalence estimates
against detection counts, and the two disagreeing about a country being the
finding. Adding an inferred surface on top would blur that, which is the
opposite of the point. Everything here is something a named body published about
a named place, and each record says which of the three kinds it is.
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "suspected.json")

# Freedom Fund and comparable programme geographies. These are transcribed from
# published programme descriptions, not modelled, and each is a place a funder
# committed to after its own assessment.
HOTSPOTS = [
    ("Bihar and eastern Uttar Pradesh", "IND", 25.6, 85.1,
     "Brick kilns, stone quarries and agricultural bonded labour. One of the "
     "longest-running hotspot programmes anywhere."),
    ("Tamil Nadu \u2014 Erode, Tiruppur, Dindigul", "IND", 11.1, 77.3,
     "Spinning mills and hostel-based garment work, the sector behind the "
     "Dindigul Agreement."),
    ("Nepal Terai \u2014 Central and Eastern", "NPL", 26.8, 86.0,
     "Origin districts for cross-border and Gulf migration, and the recruitment "
     "end of several corridors on this map."),
    ("Thailand \u2014 Samut Sakhon and the Gulf coast", "THA", 13.5, 100.3,
     "Seafood processing and fishing crews, the sector behind the EU yellow card "
     "and the 2015 investigations."),
    ("Ethiopia \u2014 Amhara and Oromia origin areas", "ETH", 10.5, 38.5,
     "Domestic work migration to the Gulf, and the origin end of the kafala "
     "corridors."),
    ("Myanmar\u2013Thailand border \u2014 Mae Sot and the Moei strip", "MMR", 16.7, 98.6,
     "Garment work, agricultural labour and, since 2021, the scam compounds."),
    ("Brazil \u2014 Par\u00e1 and Maranh\u00e3o frontier", "BRA", -5.0, -48.0,
     "Cattle, charcoal and deforestation frontier; the states with the densest "
     "entries on Brazil's own employer register."),
    ("Eastern DRC \u2014 North and South Kivu", "COD", -2.0, 28.5,
     "Artisanal mining under armed-group interference, the geography the IPIS "
     "layer covers site by site."),
]


def find_export(*patterns):
    if not os.path.isdir(DATA_DIR):
        return None
    for f in sorted(os.listdir(DATA_DIR)):
        low = f.lower()
        if low.endswith((".csv", ".json", ".xlsx")) and any(p in low for p in patterns):
            p = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return p
    return None


def rows(src):
    raw = open(src, "rb").read()
    txt = raw.decode("utf-8", "replace").lstrip()
    if txt[:1] in "[{":
        j = json.loads(txt)
        if isinstance(j, list):
            return j
        for k in ("data", "results", "rows", "records"):
            if isinstance(j.get(k), list):
                return j[k]
        return []
    return list(csv.DictReader(io.StringIO(txt)))


def lk(r):
    return {str(k).lower().replace(" ", "").replace("_", ""): v for k, v in r.items()}


def num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


DETECTION_CAVEAT = (
    " Every number on this layer is a count of <b>what an institution recorded</b>, "
    "not of what happened. Read it against the prevalence estimate for the same "
    "country: where a place reports a lot, someone is looking; where it reports "
    "little, that may mean little is happening or that nobody is looking, and the "
    "number itself cannot tell you which.")


def harvest_ncrb(a):
    src = find_export("ncrb", "india_traffick", "bonded")
    if not src:
        print("  India's National Crime Records Bureau publishes Crime in India "
              "annually with human trafficking and bonded labour cases by state and "
              "district \u2014 subnational official data, which is rare anywhere and "
              "almost unique at this scale. Tables are at ncrb.gov.in; commit one to "
              "data/ with 'ncrb' in the filename.")
        print("  Expected columns: state (or district), year, cases registered, "
              "victims, and latitude/longitude if you have them; otherwise the state "
              "name is matched against the map's Indian subnational geography.")
        return []
    out = []
    for r in rows(src):
        low = lk(r)
        place = str(low.get("state") or low.get("district") or low.get("stateut") or "").strip()
        if not place:
            continue
        cases = num(low.get("cases") or low.get("casesregistered") or low.get("total"))
        victims = num(low.get("victims") or low.get("victimsrescued"))
        year = str(low.get("year") or "")[:4]
        lat, lng = num(low.get("latitude") or low.get("lat")), num(low.get("longitude") or low.get("lng"))
        rec = {
            "name": ("%s \u2014 %s case%s registered"
                     % (place, format(int(cases), ",") if cases else "?",
                        "" if cases == 1 else "s")),
            "source": "ncrb", "type": "Cases registered (India, NCRB)",
            "precise": False, "local": True,
            "impact": 4 if (cases or 0) >= 100 else 3,
            "status": ("NCRB %s" % year) if year else "NCRB",
            "state": place,
            "url": "https://www.ncrb.gov.in/",
            "desc": (("Human trafficking and bonded labour cases registered in %s%s."
                      % (place, (" in %s" % year) if year else ""))
                     + ((" Victims recorded: %s." % format(int(victims), ",")) if victims else "")
                     + " From India's National Crime Records Bureau, one of the very few "
                       "official sources anywhere that publishes this <b>below national "
                       "level</b>." + DETECTION_CAVEAT),
        }
        if lat is not None and lng is not None:
            rec["lat"], rec["lng"] = lat, lng
        else:
            rec["subnational"] = place
            rec["country_name"] = "India"
        out.append(rec)
    print("  NCRB units: %d" % len(out))
    return out


def harvest_polaris(a):
    src = find_export("polaris", "nhth", "hotline")
    if not src:
        print("  Polaris publishes National Human Trafficking Hotline statistics by US "
              "state at polarisproject.org. Commit an export to data/ with 'polaris' "
              "or 'nhth' in the filename. Expected columns: state, year, signals or "
              "contacts, cases.")
        return []
    out = []
    for r in rows(src):
        low = lk(r)
        place = str(low.get("state") or low.get("name") or "").strip()
        if not place:
            continue
        sig = num(low.get("signals") or low.get("contacts") or low.get("substantivesignals"))
        cases = num(low.get("cases") or low.get("situations"))
        year = str(low.get("year") or "")[:4]
        out.append({
            "name": "%s \u2014 %s hotline signal%s" % (
                place, format(int(sig), ",") if sig else "?", "" if sig == 1 else "s"),
            "source": "polaris", "type": "Hotline signals (US)",
            "precise": False, "local": True,
            "impact": 3,
            "status": ("NHTH %s" % year) if year else "NHTH",
            "state": place, "subnational": place, "country_name": "United States",
            "url": "https://polarisproject.org/",
            "desc": (("Contacts to the US National Human Trafficking Hotline from %s%s."
                      % (place, (" in %s" % year) if year else ""))
                     + ((" Situations identified: %s." % format(int(cases), ",")) if cases else "")
                     + " <b>A signal is a contact, not a case.</b> The same person may "
                       "contact more than once, most contacts are not victims, and many "
                       "are from professionals asking about someone else. What this maps "
                       "is <b>where people know the number and are able to call</b> "
                       "\u2014 a real thing to know, and not the thing it looks like."),
        })
    print("  Polaris units: %d" % len(out))
    return out


def harvest_hotspots(a):
    out = []
    for name, iso, lat, lng, why in HOTSPOTS:
        out.append({
            "name": name,
            "source": "hotspots", "type": "Programme hotspot",
            "lat": lat, "lng": lng, "precise": False, "local": True,
            "impact": 3, "status": "Concentrated programme",
            "state": name, "iso": iso,
            "url": "https://freedomfund.org/our-programs/",
            "desc": (why + " <b>This is not an estimate and not a finding.</b> It is a "
                     "geography where a funder concentrated after its own assessment "
                     "\u2014 someone looked hard and decided this is where to work. That "
                     "makes it useful in a specific way: it marks places thought to "
                     "matter enough to spend years on, which is different from places "
                     "where something was recorded. The coordinate is the centre of a "
                     "region, not a site."),
        })
    print("  hotspots: %d" % len(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("ncrb", "polaris", "hotspots", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.ncrb, a.polaris, a.hotspots, a.all]):
        ap.error("choose --ncrb, --polaris, --hotspots or --all")

    recs = []
    if a.hotspots or a.all:
        print("=== Programme hotspots ===")
        recs += harvest_hotspots(a)
    if a.ncrb or a.all:
        print("=== India NCRB: cases by state ===")
        recs += harvest_ncrb(a)
    if a.polaris or a.all:
        print("=== Polaris: US hotline signals by state ===")
        recs += harvest_polaris(a)

    print("total: %d" % len(recs))
    if a.dry_run:
        for r in recs[:20]:
            print("  %-46s %s" % (r["name"][:46], r["type"]))
        return 0
    if not recs:
        print("nothing harvested; suspected.json left alone")
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "note": ("Subnational geography of where it is thought to be. "
                            "Estimates, signals and programme geographies \u2014 none "
                            "of it a finding, all of it about places rather than "
                            "countries."),
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
