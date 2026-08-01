#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_determinations.py -- build projects.json, the determinations layer.

    python3 harvest_determinations.py            # write projects.json
    python3 harvest_determinations.py --dry-run -v
    python3 harvest_determinations.py --keep-seed-only   # rebuild from the seed

WHAT GOES IN
------------
Only findings a government has published. Not allegations, not prevalence
estimates, not press reports -- those are the wire's job and are drawn
differently on the map.

  1. US CBP Withhold Release Orders and Findings, via OpenSanctions, which
     republishes the CBP list as structured data and refreshes it daily. CBP
     itself publishes an HTML table with no API, so the choice is a documented
     third-party mirror or a brittle scraper; the mirror wins, and the source
     of record is named in every entry so nobody mistakes the mirror for the
     authority.
  2. The US DOL TVPRA List of Goods, at country-and-commodity level.

NO COORDINATES ARE INVENTED HERE
--------------------------------
Records carry an ISO3 country code and no lat/lng. The map already computes a
country centroid from the boundary geometry it loads anyway, and fills them in
at runtime, marking each as imprecise so it draws as a hollow ring. A customs
order names a company, not a place, and this file will not pretend otherwise.

IF THE FEED IS UNREACHABLE
--------------------------
The hand-entered seed inside index.html is not replaced -- it is the floor. A
failed harvest leaves the map exactly as it was rather than emptying it.
"""

import argparse
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "projects.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

# OpenSanctions publishes each dataset at a stable path. Confirm this resolves
# before trusting a run: --dry-run prints the row count it got.
OS_BASE = "https://data.opensanctions.org/datasets/latest/us_cbp_forced_labor/"
OS_FILES = ["targets.nested.json", "entities.ftm.json", "targets.simple.csv"]

# Country names as they appear in these sources -> ISO3. Only what the sources
# actually use; this is not meant to be a world list.
ISO3 = {
    "china": "CHN", "people's republic of china": "CHN", "xinjiang": "CHN",
    "malaysia": "MYS", "taiwan": "TWN", "thailand": "THA", "vietnam": "VNM",
    "turkmenistan": "TKM", "uzbekistan": "UZB", "zimbabwe": "ZWE",
    "democratic republic of the congo": "COD", "dr congo": "COD", "congo": "COD",
    "brazil": "BRA", "india": "IND", "pakistan": "PAK", "bangladesh": "BGD",
    "japan": "JPN", "south korea": "KOR", "korea": "KOR", "serbia": "SRB",
    "russia": "RUS", "myanmar": "MMR", "burma": "MMR", "indonesia": "IDN",
    "philippines": "PHL", "mexico": "MEX", "peru": "PER", "bolivia": "BOL",
    "ghana": "GHA", "cote d'ivoire": "CIV", "ivory coast": "CIV",
    "nepal": "NPL", "sri lanka": "LKA", "cambodia": "KHM", "laos": "LAO",
    "turkey": "TUR", "ethiopia": "ETH", "kenya": "KEN", "nigeria": "NGA",
    "egypt": "EGY", "argentina": "ARG", "mongolia": "MNG", "mauritius": "MUS",
    "netherlands": "NLD", "belarus": "BLR", "united states": "USA",
    "taiwan, province of china": "TWN",
}

# Commodity -> the map's own type keys, so the sector filter works on these.
COMMODITY = [
    (("glove", "rubber"), "palm"),
    (("palm",), "palm"),
    (("cotton", "textile", "garment", "apparel", "yarn"), "cotton"),
    (("seafood", "fish", "squid", "tuna", "vessel", "shrimp"), "fishing"),
    (("gold", "diamond"), "gold"),
    (("cobalt", "lithium", "nickel", "polysilicon", "battery"), "battery_min"),
    (("mica",), "mica"),
    (("brick", "kiln"), "bricks"),
    (("cocoa", "chocolate"), "cocoa"),
    (("sugar", "sugarcane"), "agri_other"),
    (("coal", "coke"), "mining_other"),
    (("salt",), "agri_other"),
    (("tyre", "tire", "bicycle", "electronic", "component"), "mfg_other"),
    (("timber", "wood", "charcoal"), "logging"),
    (("tomato", "melon", "produce", "agricultur"), "agri_other"),
]


def fetch(url, timeout=45):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


# Matched BEFORE the country list, because each of these contains a country
# name that means something else. "Inner Mongolia" is in China; a run without
# this put a Xinjiang-adjacent producer in Mongolia.
OVERRIDE = [
    ("inner mongolia", "CHN"), ("nei mongol", "CHN"), ("xinjiang", "CHN"),
    ("xuar", "CHN"), ("uyghur", "CHN"), ("uighur", "CHN"), ("hotan", "CHN"),
    ("kashgar", "CHN"), ("aksu", "CHN"), ("urumqi", "CHN"), ("xizang", "CHN"),
    ("tibet", "CHN"), ("qinghai", "CHN"), ("gansu", "CHN"), ("tianjin", "CHN"),
    ("xuzhou", "CHN"), ("yunnan", "CHN"), ("shandong", "CHN"),
    ("hong kong", "HKG"), ("macau", "MAC"),
    ("north korea", "PRK"), ("democratic people's republic of korea", "PRK"),
    ("south korea", "KOR"), ("republic of korea", "KOR"),
]

# OpenSanctions gives ISO2 in its country property more often than a name.
A2 = {
    "cn": "CHN", "my": "MYS", "tw": "TWN", "th": "THA", "vn": "VNM",
    "tm": "TKM", "uz": "UZB", "zw": "ZWE", "cd": "COD", "br": "BRA",
    "in": "IND", "pk": "PAK", "bd": "BGD", "jp": "JPN", "kr": "KOR",
    "rs": "SRB", "ru": "RUS", "mm": "MMR", "id": "IDN", "ph": "PHL",
    "mx": "MEX", "pe": "PER", "bo": "BOL", "gh": "GHA", "ci": "CIV",
    "np": "NPL", "lk": "LKA", "kh": "KHM", "la": "LAO", "tr": "TUR",
    "et": "ETH", "ke": "KEN", "ng": "NGA", "eg": "EGY", "ar": "ARG",
    "mn": "MNG", "mu": "MUS", "nl": "NLD", "by": "BLR", "us": "USA",
    "mw": "MWI", "kp": "PRK", "hk": "HKG", "sg": "SGP", "ae": "ARE",
    "sa": "SAU", "qa": "QAT", "lb": "LBN", "jo": "JOR", "za": "ZAF",
    "it": "ITA", "es": "ESP", "ie": "IRL", "fr": "FRA", "de": "DEU",
    "gb": "GBR", "uk": "GBR", "ca": "CAN", "au": "AUS", "no": "NOR",
}


def iso_of(text, country_prop=""):
    """Overrides first, then the country property (ISO2, ISO3 or a name), then
    a longest-name scan of the free text. Names are matched on word boundaries
    so 'Guinea' cannot claim 'Papua New Guinea' and 'Mongolia' cannot claim
    'Inner Mongolia'."""
    t = " " + re.sub(r"[^a-z0-9' ]+", " ", (text or "").lower()) + " "
    for phrase, iso in OVERRIDE:
        if " " + phrase + " " in t:
            return iso

    c = (country_prop or "").strip().lower()
    if len(c) == 2 and c in A2:
        return A2[c]
    if len(c) == 3 and c.isalpha():
        return c.upper()
    if c in ISO3:
        return ISO3[c]

    best, n = None, 0
    for name, iso in ISO3.items():
        if " " + name + " " in t and len(name) > n:
            best, n = iso, len(name)
    return best


def type_of(text):
    t = (text or "").lower()
    for words, key in COMMODITY:
        if any(w in t for w in words):
            return key
    return "other"


def parse_opensanctions(raw):
    """One JSON object per line (FtM), or a single JSON array. Handles both."""
    rows = []
    txt = raw.decode("utf-8", "replace").strip()
    if txt.startswith("["):
        try:
            rows = json.loads(txt)
        except Exception:
            rows = []
    else:
        for line in txt.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


_UNRESOLVED = []


def first(props, *keys):
    for k in keys:
        v = props.get(k)
        if isinstance(v, list) and v:
            return str(v[0])
        if isinstance(v, str) and v:
            return v
    return ""


def record_from_entity(e):
    props = e.get("properties") or {}
    name = first(props, "name", "alias") or e.get("caption") or ""
    if not name:
        return None
    country = first(props, "country", "jurisdiction", "mainCountry")
    program = first(props, "program", "topics", "sourceUrl")
    note = first(props, "notes", "summary", "description", "reason")
    listed = first(props, "listingDate", "createdAt", "modifiedAt")
    blob = " ".join([name, country, program, note])

    iso = iso_of(blob, country)
    if not iso:
        _UNRESOLVED.append(name.strip()[:70] + ("  [country=" + country + "]" if country else ""))
        return None

    finding = "finding" in blob.lower()
    return {
        "name": name.strip()[:160],
        "source": "cbp",
        "type": type_of(blob),
        "iso": iso,
        "state": country or iso,
        "impact": 4 if finding else 3,
        "precise": False,
        "status": "Finding in force" if finding else "Import ban in force",
        "date": listed[:10] if listed else "",
        "company": name.strip()[:120],
        "url": first(props, "sourceUrl") or "https://www.cbp.gov/trade/forced-labor/withhold-release-orders-and-findings",
        "desc": ("Named in a US customs forced-labour action. Goods from this "
                 "producer are barred from entry unless the importer rebuts the "
                 "finding; a Finding additionally allows seizure rather than only "
                 "detention. Source of record is US Customs and Border Protection "
                 "\u2014 this entry is harvested from the OpenSanctions mirror of "
                 "that list, so check the CBP page before citing it. "
                 + (note.strip()[:400] if note else "")).strip(),
    }


def harvest_cbp(verbose=False):
    for fn in OS_FILES:
        url = OS_BASE + fn
        try:
            raw = fetch(url)
        except Exception as ex:
            if verbose:
                print("  %-24s %s" % (fn, str(ex)[:70]))
            continue
        if fn.endswith(".csv"):
            continue  # only used as a reachability probe
        rows = parse_opensanctions(raw)
        del _UNRESOLVED[:]
        recs = [r for r in (record_from_entity(e) for e in rows) if r]
        print("  %-24s %d entities -> %d records" % (fn, len(rows), len(recs)))
        if _UNRESOLVED:
            print("  %d entity(ies) had no resolvable country and were dropped "
                  "rather than guessed:" % len(_UNRESOLVED))
            for u in (_UNRESOLVED if verbose else _UNRESOLVED[:8]):
                print("      " + u)
            if not verbose and len(_UNRESOLVED) > 8:
                print("      ... run with -v for the rest")
        if recs:
            return recs
    return []


# A finding can name more than one country. Where it does, the map draws a dot
# in each -- otherwise a person opening Madagascar is told nothing is documented
# there when the same listing covers it. Harvested records are single-country by
# construction (a customs order names one producer), but keep the shape general
# so a future source that spans countries does not need a schema change.
def expand_multi(rec):
    isos = rec.pop("isos", None)
    if not isos:
        return [rec]
    out = []
    for iso in isos:
        c = dict(rec)
        c["iso"] = iso
        c.pop("lat", None)
        c.pop("lng", None)
        c["precise"] = False
        c["_group"] = rec.get("name", "")
        out.append(c)
    return out


def seed_from_index():
    """The hand-entered set inside index.html, so a failed harvest still leaves
    a populated layer rather than an empty map."""
    p = os.path.join(HERE, "index.html")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        doc = f.read()
    m = re.search(r'var PJ_SEED=\{"projects":\[(.*?)\n  \]\};', doc, re.S)
    if not m:
        return []
    try:
        return json.loads("[" + m.group(1) + "]")
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-seed-only", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    seed = seed_from_index()
    print("hand-entered seed: %d records" % len(seed))
    if not seed:
        print("  index.html was not found next to this script \u2014 you are probably "
              "running from the wrong directory. cd into the repo folder first, or "
              "the seed floor is lost and only harvested records will ship.")

    harvested = [] if args.keep_seed_only else harvest_cbp(args.verbose)
    print("harvested from customs list: %d records" % len(harvested))
    if not harvested and not args.keep_seed_only:
        print("  (nothing harvested \u2014 the seed is the floor, so the map is "
              "unchanged rather than emptied)")

    seen, merged = set(), []
    for r0 in seed + harvested:
        for r in expand_multi(dict(r0)):
            # de-duplicate on name AND country, so a multi-country finding keeps
            # one dot per country instead of collapsing to the first
            k = (re.sub(r"[^a-z0-9]", "", str(r.get("name", "")).lower())[:60]
                 + "|" + str(r.get("iso") or r.get("lat") or ""))
            if k and k not in seen:
                seen.add(k)
                merged.append(r)

    withiso = sum(1 for r in merged if r.get("iso") and "lat" not in r)
    print("merged: %d records (%d placed by ISO at runtime, %d with explicit "
          "coordinates)" % (len(merged), withiso, len(merged) - withiso))

    if args.dry_run:
        for r in merged[:20]:
            print("  [%s] %-42s %s" % (r.get("iso") or "--",
                                       str(r.get("name"))[:42], r.get("status", "")))
        return 0

    out = {"generated": datetime.now(timezone.utc).isoformat(),
           "note": ("Determinations only: published government findings. "
                    "Records without lat/lng carry an ISO3 code and are placed "
                    "at a country centroid by the map at load time."),
           "projects": merged}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
