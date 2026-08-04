#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_sites.py -- more located sites, in the IPIS mould.

    python3 harvest_sites.py --delve
    python3 harvest_sites.py --sherloc
    python3 harvest_sites.py --ejatlas
    python3 harvest_sites.py --all -v

Writes sites.json.

WHAT COUNTS AS "IN THE IPIS MOULD"
----------------------------------
IPIS is the strongest layer on this map because of what its records are: a
person went to a specific pit, wrote down the coordinates, and recorded whether
children were working there. Observation, at a place, by someone who went.

Very little else in this field meets that bar. The sources below are ordered by
how close they come, and each record says which rung it is on:

  sherloc   PROSECUTED CASES. UNODC's case-law database: trafficking
            prosecutions with the court, the country, the facts and the
            outcome. Not an observation of a site, but a finding by a court
            about events at a place -- the highest evidentiary standing of
            anything here, and past tense, which matters for the reason set out
            under --sexual below.

  delve     ARTISANAL MINING SITES -- AND A CORRECTION. I described Delve as
            the obvious extension of the IPIS layer. It is not. Delve is a
            knowledge platform: country profiles, narrative, and partner
            uploads of whatever shape the partner had. There is no bulk
            site-level download, and the files attached to country pages are
            often surveys of people rather than registers of places -- one
            Burkina Faso upload turned out to be a 376-respondent gender survey
            with site names, no coordinates, and three respondents under 18.
            That is a real dataset and a poor map layer.

            The parser stays because some partner uploads DO carry site
            coordinates, and reading one costs nothing. But Delve is not an
            IPIS equivalent and should not be waited on as though it were.

  ejatlas   ENVIRONMENTAL JUSTICE ATLAS. Roughly 4,000 geolocated conflicts,
            each with a case narrative. A subset name forced labour, debt
            bondage or child labour among the impacts. Community-reported
            rather than field-verified, and every record says so.

ON SUB-NATIONAL SEX TRAFFICKING
-------------------------------
You asked for it and this is what I have built: --sherloc includes sexual
exploitation cases, placed at the court and the location the judgment names.
Prosecuted, adjudicated, public record, past tense.

What I have not built is a layer of suspected commercial-sex venues, and the
reason is narrow enough to state once. Every other point layer here is inert if
misused -- a brick kiln location helps nobody exploit anyone. A venue list is
directly usable by buyers, and by police for raids that in this sector
overwhelmingly end with the women arrested, deported or moved on rather than
assisted. It is the one dataset shape where publishing the points predictably
harms the people the map exists for. Court cases give you the same geography
with none of that, because the events have already happened and the venue is
named by a judgment rather than by rumour.

If you want the venue-level version anyway, it is your project and your call --
but I would want it behind an access control rather than in a public bundle,
and I would rather you decide that deliberately than have me quietly ship it.
"""

import argparse
import csv
import io
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "sites.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

SHERLOC_PAGES = [
    "https://sherloc.unodc.org/cld/v3/sherloc/cldb/index.html",
    "https://sherloc.unodc.org/cld/en/v3/sherloc/cldb/index.html",
]
DELVE_SOURCES = [
    "https://delvedatabase.org/api/sites",
    "https://raw.githubusercontent.com/worldbank/delve/main/data/sites.csv",
]
EJATLAS_SOURCES = [
    "https://ejatlas.org/backoffice/api/cases",
    "https://ejatlas.org/api/v1/cases",
]

# Terms that mark an EJAtlas case as belonging on this map at all.
# A bare "trafficking" matched drug and arms trafficking, which is how a
# US-Colombia coca fumigation case ended up on a forced-labour map. The term
# list now requires a human-trafficking phrasing or a labour term, and a case
# that matched ONLY on a trafficking word is dropped if the surrounding text is
# about drugs, arms or wildlife.
EJ_TERMS = ["forced labour", "forced labor", "modern slavery", "slave labour",
            "slave labor", "slavery", "bonded labour", "bonded labor",
            "debt bondage", "child labour", "child labor", "human trafficking",
            "trafficking in persons", "trafficking of women",
            "trafficking of children", "sex trafficking", "trafficked",
            "indentured", "servitude", "forced work", "peonage"]
EJ_EXCLUDE = re.compile(
    r"drug[- ]traffick|arms traffick|wildlife traffick|"
    r"traffick\w* of (?:drugs|cocaine|timber|wildlife)", re.I)


def fetch(url, timeout=120):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def find_export(*patterns):
    if not os.path.isdir(DATA_DIR):
        return None
    for f in sorted(os.listdir(DATA_DIR)):
        low = f.lower()
        if low.endswith((".csv", ".json", ".geojson")) and any(p in low for p in patterns):
            p = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return p
    return None


def num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def rows_from(path_or_bytes):
    """CSV, JSON array, or GeoJSON FeatureCollection."""
    if isinstance(path_or_bytes, str):
        raw = open(path_or_bytes, "rb").read()
    else:
        raw = path_or_bytes
    txt = raw.decode("utf-8", "replace").lstrip()
    if txt[:1] in "[{":
        try:
            j = json.loads(txt)
        except Exception:
            return []
        if isinstance(j, dict):
            if j.get("type") == "FeatureCollection":
                out = []
                for f in j.get("features", []):
                    g = (f.get("geometry") or {}).get("coordinates")
                    p = dict(f.get("properties") or {})
                    if g and len(g) >= 2:
                        p["_lat"], p["_lng"] = g[1], g[0]
                    out.append(p)
                return out
            for k in ("data", "results", "sites", "cases", "items"):
                if isinstance(j.get(k), list):
                    return j[k]
            return []
        return j if isinstance(j, list) else []
    return list(csv.DictReader(io.StringIO(txt)))


def latlng(r):
    low = {str(k).lower().replace(" ", "").replace("_", ""): v for k, v in r.items()}
    lat = num(low.get("_lat") or low.get("lat") or low.get("latitude") or low.get("y"))
    lng = num(low.get("_lng") or low.get("lng") or low.get("lon") or
              low.get("longitude") or low.get("x"))
    return lat, lng, low


# ==================================================================== DELVE
def harvest_delve(a):
    src = find_export("delve", "asm", "mining")
    raw = None
    if src:
        raw = src
    else:
        for u in DELVE_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s" % u)
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-58s %s" % (u[:58], str(ex)[:36]))
    if not raw:
        print("  No Delve export found, and there is no bulk site download to fetch \u2014 "
              "delvedatabase.org is a knowledge platform of country profiles, with "
              "partner uploads of varying shape attached to some of them. Several are "
              "surveys of people rather than registers of places and carry no "
              "coordinates at all.")
        print("  If you find one that does carry latitude and longitude, commit it to "
              "data/ with 'delve' or 'asm' in the filename and this reads it. Do not "
              "wait on Delve for the IPIS extension; it is not that.")
        return []

    out = []
    for r in rows_from(raw):
        lat, lng, low = latlng(r)
        if lat is None or lng is None:
            continue
        blob = " ".join(str(v) for v in r.values()).lower()
        child = any(w in blob for w in ("child", "enfant", "minor"))
        out.append({
            "name": str(low.get("name") or low.get("sitename") or "Artisanal mining site")[:110],
            "source": "delve", "type": "Artisanal mining site",
            "lat": lat, "lng": lng, "precise": True,
            "impact": 4 if child else 3,
            "status": "Child labour recorded" if child else "Site recorded",
            "state": str(low.get("country") or ""),
            "url": "https://delvedatabase.org/",
            "desc": ("Artisanal or small-scale mining site recorded in the World Bank's "
                     "Delve platform"
                     + ((" \u2014 <b>child labour recorded at this site</b>." ) if child
                        else ".")
                     + " ASM is the sector where the strongest located evidence in this "
                       "whole field exists, because it is the one where people go and "
                       "count. Where a record came from a field visit it says so; where "
                       "it is a register entry it does not, and that difference is worth "
                       "checking before citing a single site."),
        })
    print("  Delve sites: %d" % len(out))
    return out


# ================================================================== SHERLOC
def harvest_sherloc(a):
    src = find_export("sherloc", "caselaw", "case_law")
    if not src:
        print("  SHERLOC has no open bulk endpoint \u2014 the case-law database is a "
              "search interface. Two ways in:")
        print("    1. sherloc.unodc.org/cld \u2192 filter to Trafficking in persons, "
              "export the result set, commit it to data/ with 'sherloc' in the name.")
        print("    2. Send me the network request the search page makes and I will "
              "wire it directly.")
        print("  Expected columns: case title, country, date, crime type, summary, "
              "and latitude/longitude if the export carries them; otherwise the "
              "country field is used and the record is placed imprecisely.")
        return []

    out = []
    for r in rows_from(src):
        lat, lng, low = latlng(r)
        title = str(low.get("title") or low.get("casename") or low.get("name") or "").strip()
        if not title:
            continue
        country = str(low.get("country") or low.get("countryname") or "").strip()
        summary = str(low.get("summary") or low.get("facts") or low.get("description") or "")
        blob = (title + " " + summary).lower()
        sexual = any(w in blob for w in ("sexual", "prostitution", "commercial sex"))
        rec = {
            "name": title[:130],
            "source": "sherloc",
            "type": ("Prosecuted case \u2014 sexual exploitation" if sexual
                     else "Prosecuted case"),
            "precise": lat is not None and lng is not None,
            "impact": 4,
            "status": "Adjudicated",
            "state": country,
            "url": low.get("url") or "https://sherloc.unodc.org/cld/",
            "desc": (("Trafficking prosecution recorded in UNODC's SHERLOC case-law "
                      "database" + ((", %s" % country) if country else "") + ". ")
                     + (summary.strip()[:600] + " " if summary.strip() else "")
                     + "<b>A court finding, not an allegation and not an estimate</b> "
                       "\u2014 the highest evidentiary standing of anything on this map, "
                       "and past tense. What it establishes is what a court found about "
                       "events that have already happened; it says nothing about what is "
                       "happening at that place now."),
        }
        if rec["precise"]:
            rec["lat"], rec["lng"] = lat, lng
        else:
            rec["country_name"] = country
        out.append(rec)
    print("  SHERLOC cases: %d (%d with coordinates)"
          % (len(out), sum(1 for r in out if r.get("precise"))))
    return out


# ================================================================== EJATLAS
def harvest_ejatlas(a):
    src = find_export("ejatlas", "ejolt", "conflict")
    raw = src
    if not raw:
        for u in EJATLAS_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s" % u)
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-52s %s" % (u[:52], str(ex)[:36]))
    if not raw:
        print("  EJAtlas unreachable. It maps roughly 4,000 geolocated conflicts "
              "with case narratives; a subset name forced labour, bonded labour or "
              "child labour among the impacts. Export from ejatlas.org and commit "
              "it to data/ with 'ejatlas' in the filename.")
        return []

    out, seen = [], 0
    for r in rows_from(raw):
        seen += 1
        lat, lng, low = latlng(r)
        if lat is None or lng is None:
            continue
        blob_raw = " ".join(str(v) for v in r.values())
        blob = blob_raw.lower()
        hits = [t for t in EJ_TERMS if t in blob]
        if not hits:
            continue
        if all("traffick" in t for t in hits) and EJ_EXCLUDE.search(blob_raw):
            continue
        # EJAtlas publishes an accuracy grade per case. Honour it: a HIGH local
        # case is a pin, anything coarser is a ring, because the dataset is
        # telling you how well it knows where this is and overriding that would
        # be inventing precision it does not claim.
        acc = str(low.get("accuracyoflocation") or low.get("accuracy") or "").upper()
        exact = acc.startswith("HIGH")
        out.append({
            "name": str(low.get("name") or low.get("case") or low.get("title")
                        or "Conflict")[:130],
            "source": "ejatlas", "type": "Reported conflict \u2014 labour impacts",
            "lat": lat, "lng": lng, "precise": exact, "local": not exact,
            "impact": 3, "status": "Reported",
            "state": str(low.get("country") or ""),
            "url": low.get("url") or "https://ejatlas.org/",
            "desc": (((str(low.get("impacts") or "")[:300] + " ")
                       if low.get("impacts") else "")
                     + ("Case from the Environmental Justice Atlas. Its record names: "
                        "<b>%s</b>. " % (str(low.get("matchedterms")) or "; ".join(hits)))
                     + ("" if exact else
                        ("EJAtlas grades this location %s, so it is drawn as an area "
                         "rather than a point. "
                         % (acc.split()[0].lower() if acc else "coarse")))
                     + "<b>Community-reported, not field-verified</b> \u2014 EJAtlas is "
                       "compiled with and by the people affected, which is its strength "
                       "for reaching places no inspectorate goes and its limit as "
                       "evidence. Open the case for the sources the contributors cited."),
        })
    print("  EJAtlas: %d of %d cases name forced, bonded or child labour" % (len(out), seen))
    return out



ITSCI_SOURCES = [
    "https://www.itsci.org/wp-content/uploads/itsci-sites.csv",
    "https://www.itsci.org/data/sites.json",
]
GFW_TRANSHIP = ("https://gateway.api.globalfishingwatch.org/v3/events"
                "?datasets[0]=public-global-encounters-events:latest"
                "&start-date=%s&end-date=%s&limit=%d&offset=0")


# ==================================================================== ITSCI
def harvest_itsci(a):
    """Tagged mine sites in the Great Lakes region.

    ITSCi tags bags of tin, tantalum and tungsten at the mine and follows them
    to the exporter, so its site list is one of the very few in this field that
    names the cooperative working a pit. That is what makes it useful here: a
    named operator is something you can write to, ask about, and hold to an
    answer, which a coordinate on its own is not.

    It is an industry-run scheme and has been criticised for exactly the reason
    you would expect -- the people audited pay for the audit. Every record says
    so."""
    src = find_export("itsci", "itsci_sites", "3t")
    raw = src
    if not raw:
        for u in ITSCI_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s" % u)
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-52s %s" % (u[:52], str(ex)[:36]))
    if not raw:
        print("  ITSCi publishes its site list through its own portal rather than an "
              "open endpoint. Export it and commit it to data/ with 'itsci' in the "
              "filename. Expected columns: site name, cooperative, mineral, country, "
              "latitude, longitude.")
        return []

    out = []
    for r in rows_from(raw):
        lat, lng, low = latlng(r)
        if lat is None or lng is None:
            continue
        coop = str(low.get("cooperative") or low.get("coop") or low.get("operator") or "")
        mineral = str(low.get("mineral") or low.get("commodity") or "")
        out.append({
            "name": str(low.get("name") or low.get("sitename") or "Tagged mine site")[:110],
            "source": "itsci", "type": "Tagged mine site (3T)",
            "lat": lat, "lng": lng, "precise": True,
            "impact": 3, "status": "Tagged",
            "state": str(low.get("country") or ""),
            "url": "https://www.itsci.org/",
            "desc": (("Mine site in the ITSCi traceability scheme"
                      + ((", %s" % mineral) if mineral else "")
                      + ((", worked by %s" % coop) if coop else "") + ". ")
                     + "ITSCi tags bags of tin, tantalum and tungsten at the mine and "
                       "follows them to the exporter, which makes this one of the very "
                       "few site lists in this field that <b>names the cooperative "
                       "working the pit</b> \u2014 something you can write to and hold to "
                       "an answer, which a coordinate alone is not. "
                       "<b>It is an industry-run scheme</b>, funded by the companies whose "
                       "supply chains it certifies, and has been criticised on exactly "
                       "that ground. Tagged does not mean clean; it means traced."),
        })
    print("  ITSCi sites: %d" % len(out))
    return out


# ====================================================================== GFW
def harvest_gfw(a):
    """Transhipment encounters at sea.

    Two vessels meeting at sea for long enough to transfer catch is the closest
    thing to a located event that exists in fishing. It is how a person stays
    offshore for months without a port call -- and unlike almost everything else
    here, it has a timestamp and a position."""
    if not a.token:
        print("  Global Fishing Watch needs a free API token \u2014 register at "
              "globalfishingwatch.org/our-apis and pass --token. Encounter events "
              "carry a position and a timestamp, which is as close to a located "
              "event as this field gets at sea.")
        return []
    from datetime import timedelta
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=a.days or 90)
    url = GFW_TRANSHIP % (start.isoformat(), end.isoformat(), a.max or 500)
    try:
        j = json.loads(fetch(url, timeout=180).decode("utf-8", "replace"))
    except Exception as ex:
        print("  GFW request failed: %s" % str(ex)[:70])
        return []
    ent = j.get("entries") or j.get("data") or []
    out = []
    for e in ent:
        pos = e.get("position") or {}
        lat, lng = num(pos.get("lat")), num(pos.get("lon"))
        if lat is None or lng is None:
            continue
        out.append({
            "name": "Transhipment encounter at sea",
            "source": "gfw", "type": "Transhipment encounter",
            "lat": lat, "lng": lng, "precise": True,
            "impact": 3, "status": str(e.get("start") or "")[:10] or "Recorded",
            "state": "At sea",
            "url": "https://globalfishingwatch.org/",
            "desc": ("Two vessels recorded meeting at sea long enough to transfer catch, "
                     "from Global Fishing Watch's AIS analysis. "
                     "<b>An encounter is not a finding.</b> Transhipment is legal and "
                     "routine in most fisheries. It is on this map because it is the "
                     "mechanism by which a crew can stay offshore for months or years "
                     "without a port call, which is a documented forced-labour indicator "
                     "\u2014 and because, unlike almost everything else in this field, it "
                     "carries a position and a timestamp."),
        })
    print("  GFW encounters: %d" % len(out))
    return out


# =============================================================== RIGHTS LAB
RIGHTSLAB_NOTE = (
    "  Rights Lab satellite datasets beyond the brick kilns \u2014 charcoal in Brazil, "
    "fish processing in the Sundarbans, mica in Jharkhand \u2014 are published with the "
    "papers rather than as a standing feed. Commit any of them to data/ with "
    "'rightslab', 'kiln', 'charcoal', 'mica' or 'sundarban' in the filename and this "
    "reads them. Expected columns: latitude, longitude, and a type or site name.")


def harvest_rightslab(a):
    src = find_export("rightslab", "charcoal", "sundarban", "mica", "slaveryfromspace")
    if not src:
        print(RIGHTSLAB_NOTE)
        return []
    out = []
    for r in rows_from(src):
        lat, lng, low = latlng(r)
        if lat is None or lng is None:
            continue
        kind = str(low.get("type") or low.get("kind") or low.get("class") or "site")
        out.append({
            "name": str(low.get("name") or kind)[:110],
            "source": "rightslab", "type": "Detected site \u2014 %s" % kind,
            "lat": lat, "lng": lng, "precise": True,
            "impact": 3, "status": "Site detected",
            "state": str(low.get("country") or ""),
            "url": "https://www.nottingham.ac.uk/research/beacons-of-excellence/rights-lab/",
            "desc": ("Site detected from satellite imagery by the Rights Lab's remote "
                     "sensing work, in a sector where forced or child labour is "
                     "documented to concentrate. <b>A detection is not a finding about "
                     "this site</b> \u2014 it says a facility of this kind is here, which "
                     "is where to look rather than what was found."),
        })
    print("  Rights Lab sites: %d" % len(out))
    return out




GEOCACHE = os.path.join(DATA_DIR, "geocache.json")
_GEO = None


def geocode(place, country, a):
    """Resolve an address to real coordinates, cached forever.

    Not an approximation: Nominatim returns the coordinates of the address it
    matched. When only a city is on the case record, that is what gets
    resolved -- and the record is then marked imprecise so it draws as a ring
    rather than a pin, which is the honest way to show "this town" as against
    "this door".

    The cache is committed to data/, so a case geocoded once is never looked up
    again. Nominatim asks for one request a second and that is respected."""
    global _GEO
    if _GEO is None:
        _GEO = {}
        try:
            _GEO = json.loads(open(GEOCACHE, encoding="utf-8").read())
            print("  geocode cache: %d entries" % len(_GEO))
        except Exception:
            pass
    q = ", ".join([x for x in (place, country) if x]).strip(", ")
    if not q:
        return None, None, False
    if q in _GEO:
        c = _GEO[q]
        return (c[0], c[1], bool(c[2])) if c else (None, None, False)

    import time
    url = ("https://nominatim.openstreetmap.org/search?format=json&limit=1&q="
           + urllib.parse.quote(q))
    try:
        time.sleep(1.1)
        j = json.loads(fetch(url, timeout=30).decode("utf-8", "replace"))
    except Exception as ex:
        if a.verbose:
            print("    geocode failed for %r: %s" % (q[:44], str(ex)[:34]))
        j = []
    if not j:
        _GEO[q] = None
    else:
        # A house-number match is a street address; anything coarser is a place.
        cls = (j[0].get("addresstype") or j[0].get("type") or "")
        exact = cls in ("house", "building", "yes", "commercial", "industrial", "retail")
        _GEO[q] = [float(j[0]["lat"]), float(j[0]["lon"]), exact]
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        open(GEOCACHE, "w", encoding="utf-8").write(json.dumps(_GEO))
    except Exception:
        pass
    c = _GEO[q]
    return (c[0], c[1], bool(c[2])) if c else (None, None, False)


# ============================================================== DEFENDANTS
# Ordered by what you can actually get today, not by how good the data is.
DEFENDANT_SOURCES = [
    ("CourtListener / RECAP \u2014 free API, US federal dockets",
     "https://www.courtlistener.com/help/api/rest/"),
    ("US DOJ \u2014 human trafficking prosecutions and press releases",
     "https://www.justice.gov/humantrafficking"),
    ("US Attorneys' Offices \u2014 district press releases naming defendants",
     "https://www.justice.gov/usao"),
    ("Human Trafficking Legal Center \u2014 federal civil cases (BY REQUEST)",
     "https://htlegalcenter.org/"),
    ("Business & Human Rights Resource Centre \u2014 lawsuit profiles",
     "https://www.business-humanrights.org/en/from-us/lawsuits-database/"),
]


def harvest_defendants(a):
    """Businesses and premises NAMED IN CONCLUDED PROCEEDINGS.

    This is the middle ground between a court summary and a venue list, and the
    distinction that makes it publishable is that the naming has already been
    done, by a court, at an address on a public record.

    A suspicion-based venue layer says "exploitation may be happening here" and
    is wrong about most of its points by construction. This says "a court found
    that it happened here", which is the same sentence the judgment already
    says. It covers sexual exploitation, because those cases name hotels,
    massage businesses, bars and residences -- and it covers them the same way
    it covers a car wash or a farm.

    Two disciplines carried in every record:

      * PAST TENSE. A business named in a 2019 judgment is not a claim about
        that address today. Ownership changes, premises close, and a map that
        implies otherwise defames the current occupant.
      * THE DEFENDANT, NOT THE WORKERS. The record names who was prosecuted.
        It never characterises the people who were there.
    """
    src = find_export("defendant", "htlc", "civilcase", "prosecution", "doj",
                      "courtlistener", "recap")
    if not src:
        print("  No committed case file. Sources that name defendants:")
        for name, url in DEFENDANT_SOURCES:
            print("    %-58s %s" % (name, url))
        print()
        print("  The Human Trafficking Legal Center's civil database is the richest, but "
              "it is no longer a public download \u2014 it is <b>obtained by request</b> "
              "through the Center. Ask for the federal civil trafficking case data; say "
              "what it is for. Expect that to take a while and possibly to come with "
              "conditions on republication, which are worth agreeing before building on "
              "it rather than after.".replace("<b>", "").replace("</b>", ""))
        print()
        print("  Available without asking anyone, today:")
        print("    CourtListener has a free REST API over US federal dockets. Search for "
              "18 U.S.C. 1589 (forced labor), 1590 (trafficking), 1591 (sex trafficking) "
              "and 1595 (civil remedy), and the case captions give you the defendant "
              "names. It will not give you addresses; those come from the complaint "
              "documents or from geocoding the business name and city.")
        print("    DOJ and US Attorney press releases name the defendant, the business "
              "and usually the town, and are the fastest way to a first hundred records.")
        print()
        print("  Commit whatever you get to data/ with 'htlc', 'defendant', 'courtlistener' "
              "or 'doj' in the filename. Expected columns: defendant or business name, "
              "address or city, country, year, outcome, case citation, summary, and "
              "latitude/longitude if they are in there. Only the name plus an address or "
              "a city is required \u2014 the rest enriches the record, and the address is "
              "geocoded if no coordinates are given.")
        return []

    out, nogeo = [], 0
    for r in rows_from(src):
        lat, lng, low = latlng(r)
        name = str(low.get("defendant") or low.get("business") or low.get("name") or "").strip()
        if not name:
            continue
        outcome = str(low.get("outcome") or low.get("disposition") or low.get("result") or "")
        year = str(low.get("year") or low.get("date") or "")[:4]
        cite = str(low.get("citation") or low.get("case") or low.get("docket") or "")
        place = str(low.get("address") or low.get("city") or low.get("country") or "")
        blob = (name + " " + outcome + " " + str(low.get("summary") or "")).lower()
        sexual = any(w in blob for w in ("sexual", "prostitution", "commercial sex"))

        # Pending cases are kept and LABELLED. The distinction that matters is
        # not whether to show them but whether the reader can tell them apart:
        # a concluded case is a finding, a pending one is an allegation on a
        # public court record, and both are worth knowing as long as the record
        # says which it is.
        pending = bool(outcome) and any(
            w in outcome.lower() for w in ("pending", "filed", "ongoing",
                                           "indicted", "charged", "alleged"))

        if lat is None or lng is None:
            # Geocode rather than drop. Not an approximation: the address is
            # resolved to its actual coordinates, and where only a city is on
            # record the point is marked imprecise so it draws as a ring.
            lat, lng, exact = geocode(place, str(low.get("country") or ""), a)
            if lat is None:
                nogeo += 1
                continue
        else:
            exact = True

        out.append({
            "name": name[:130],
            "source": "defendants",
            "type": (("Named in a pending case" if pending else "Named in a concluded case")
                     + (" \u2014 sexual exploitation" if sexual else "")),
            "lat": lat, "lng": lng, "precise": exact, "local": not exact,
            "impact": 3 if pending else 4,
            "status": (outcome[:40] or ("Pending" if pending else "Concluded")),
            "state": place,
            "url": str(low.get("url") or "https://htlegalcenter.org/case-database/"),
            "desc": (("<b>%s</b> was named as a defendant in a %s trafficking "
                      "case%s%s. " % (name, "pending" if pending else "concluded",
                                      (" (%s)" % year) if year else "",
                                      (", %s" % cite) if cite else ""))
                     + ("<b>This case has not concluded.</b> It is an allegation on a "
                        "public court record, not a finding, and nothing here should be "
                        "read as though a court had decided it. "
                        if pending else "")
                     + ("" if exact else
                        "Located to the city on the case record rather than to a street "
                        "address, and drawn as a ring for that reason. ")
                     + ((("Outcome: %s. " % outcome) if outcome else ""))
                     + "This is the location the case record gives. "
                       "<b>Read it in the past tense.</b> A business named in a judgment "
                       "years ago is not a claim about that address today \u2014 "
                       "ownership changes and premises close, and treating an old "
                       "finding as a current one is unfair to whoever is there now. "
                       "The record names the party that was prosecuted; it says nothing "
                       "about the people who were working there, who were the injured "
                       "party and are not identified here."),
        })
    if nogeo:
        print("  %d case(s) could not be geocoded at all (no address, no city) and were "
              "left out" % nogeo)
    print("  named defendants: %d" % len(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("delve", "sherloc", "ejatlas", "itsci", "gfw", "rightslab",
              "defendants", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--token", help="Global Fishing Watch API token")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--max", type=int, default=500)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.delve, a.sherloc, a.ejatlas, a.itsci, a.gfw, a.rightslab,
                a.defendants, a.all]):
        ap.error("choose one or more of --sherloc --defendants --delve --ejatlas "
                 "--itsci --gfw --rightslab, or --all")

    recs = []
    if a.sherloc or a.all:
        print("=== SHERLOC: prosecuted trafficking cases ===")
        recs += harvest_sherloc(a)
    if a.defendants or a.all:
        print("=== Named defendants in concluded cases ===")
        recs += harvest_defendants(a)
    if a.delve or a.all:
        print("=== Delve: artisanal mining sites ===")
        recs += harvest_delve(a)
    if a.ejatlas or a.all:
        print("=== EJAtlas: conflicts naming labour impacts ===")
        recs += harvest_ejatlas(a)
    if a.itsci or a.all:
        print("=== ITSCi: tagged mine sites (3T) ===")
        recs += harvest_itsci(a)
    if a.rightslab or a.all:
        print("=== Rights Lab: satellite-detected sites ===")
        recs += harvest_rightslab(a)
    if a.gfw or a.all:
        print("=== Global Fishing Watch: transhipment encounters ===")
        recs += harvest_gfw(a)

    print("total: %d" % len(recs))
    if a.dry_run:
        for r in recs[:15]:
            print("  %-46s %s" % (r["name"][:46], r["type"]))
        return 0
    if not recs:
        print("nothing harvested; sites.json left alone")
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "note": ("Located sites and cases. Court findings, recorded mining "
                            "sites, and community-reported conflicts \u2014 three "
                            "different evidentiary standings, each stated in the record."),
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
