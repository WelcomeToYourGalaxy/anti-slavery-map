#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_points.py -- the sub-national and point-level layers.

    python3 harvest_points.py --ipis          # DRC artisanal mining sites (GPS)
    python3 harvest_points.py --kilns         # South Asian brick kilns (GPS)
    python3 harvest_points.py --osh --token X # Open Supply Hub facilities (GPS)
    python3 harvest_points.py --hotlines      # State Dept national helpline index
    python3 harvest_points.py --all -v

READ THIS BEFORE USING THE POINT LAYERS
---------------------------------------
Everything here is SECTOR INFRASTRUCTURE, not confirmed exploitation. A brick
kiln is not proof of bonded labour. A mining pit is not proof of child labour. A
garment factory is not proof of anything.

What these layers give you is the thing that genuinely did not exist before: the
physical locations, at coordinate precision, of the sectors where forced and
child labour are *documented to concentrate*. Combined with the country-and-
commodity determinations already on the map, that is the closest honest thing to
"where to look" that open data supports.

Each record says this in its own description. The layer is drawn as its own
source family so it can never be mistaken for a case or a determination. And
this is the one place where a dot IS precise, so these draw as solid pins --
which is exactly why the wording matters.

THE THREE SOURCES
-----------------
1. IPIS (International Peace Information Service). Since 2009, field-visited
   artisanal and small-scale mining sites in eastern DRC -- roughly 2,800 sites,
   with per-site flags for CHILD LABOUR, armed-group interference, worker
   numbers and minerals. This is the strongest dataset in this whole field: real
   coordinates, real field visits, and an explicit child-labour observation
   rather than an inference. Published as open data on their GeoServer.

2. SentinelKilnDB. 62,671 hand-validated brick kilns across the Indo-Gangetic
   Plain -- India, Pakistan, Bangladesh, Afghanistan -- detected from Sentinel-2
   imagery. Brick kilns are the most consistently documented bonded-labour
   sector in South Asia, and this is the first open, comprehensive map of where
   they physically are. CC-BY-NC-4.0, so check the licence against your use.

3. Open Supply Hub. Millions of production facilities with GPS, contributed by
   brands, unions and NGOs. Free API key. Filter by country and sector to pull
   the facilities in the sectors your determinations already flag.

VOLUME
------
62,671 kilns will destroy an in-browser map. --decimate keeps one point per
grid cell so the layer stays usable, and reports how many it dropped. The full
set is always available from the source; this is a display decision, stated,
not a claim about what exists.
"""

import argparse
import json
import math
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

CAVEAT = (" <b>This is a site in a sector where forced or child labour is documented "
          "to concentrate. It is not evidence that this particular site uses it.</b> "
          "Treat it as where to look, not as a finding. Do not approach a site on the "
          "strength of a dot on a map \u2014 the organisations under Allies and Legal "
          "Help have done this before in this jurisdiction.")



DATA_DIR = os.path.join(HERE, "data")


def find_export(path, *patterns):
    """Repo-only workflow: an export committed to data/ is found automatically,
    so a GitHub Action can use it without anyone passing a path. --file still
    wins when given."""
    if path:
        return path
    if not os.path.isdir(DATA_DIR):
        return None
    for f in sorted(os.listdir(DATA_DIR)):
        low = f.lower()
        if low.endswith((".csv", ".xlsx", ".json", ".geojson")) and any(p in low for p in patterns):
            found = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return found
    return None


def read_file(path, what):
    """A missing input should say what to do, not throw a stack trace at you."""
    if not path:
        return None
    if not os.path.exists(path):
        here = os.path.abspath(os.getcwd())
        print("\n  File not found: %s" % path)
        print("  You are in: %s" % here)
        print("  %s" % what)
        near = [f for f in os.listdir(here) if f.lower().endswith((".csv", ".json", ".xlsx"))]
        if near:
            print("  Data files in this directory: %s" % ", ".join(sorted(near)[:12]))
        else:
            print("  No .csv/.json/.xlsx files in this directory at all \u2014 you are "
                  "probably not in the repo folder, or the export has not been made yet.")
        return None
    return path


def fetch(url, timeout=90, headers=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def decimate(points, cell_deg):
    """One point per grid cell -- except that a site where forced labour or child
    labour was actually observed is never thinned away.

    Thinning by geography alone would delete exactly the records that matter:
    of ~8,000 IPIS sites, roughly a thousand carry a direct observation, and a
    grid that keeps one point per cell would discard most of them in favour of
    whichever unremarkable pit happened to be first. So flagged sites are all
    kept, and the grid is applied only to the rest."""
    if not cell_deg:
        return points, 0
    keep_all = [p for p in points if (p.get("impact") or 0) >= 4]
    rest = [p for p in points if (p.get("impact") or 0) < 4]
    seen = {(round(p["lat"] / cell_deg), round(p["lng"] / cell_deg)) for p in keep_all}
    out = list(keep_all)
    for p in rest:
        k = (round(p["lat"] / cell_deg), round(p["lng"] / cell_deg))
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    if keep_all:
        print("  kept all %d site(s) with an observation of forced or child labour, "
              "regardless of the grid" % len(keep_all))
    return out, len(points) - len(out)


# ======================================================================= IPIS
IPIS_BASE = "https://geo.ipisresearch.be/geoserver/public/ows"
IPIS_CAPS = IPIS_BASE + "?service=WFS&version=1.1.0&request=GetCapabilities"
# Tried in order if capability discovery fails. Layer names change between
# releases, which is why discovery comes first.
IPIS_FALLBACK_LAYERS = [
    "public:cod_mines_curated_all_opendata_p_ipis",
    "public:cod_mines_curated_all_opendata_ipis",
    "public:caf_mines_curated_all_opendata_p_ipis",
]


def ipis_layers():
    """Ask GeoServer what it actually has, instead of hard-coding a name that
    changes every release. Returns candidate mine layers, DRC first."""
    try:
        caps = fetch(IPIS_CAPS, timeout=120).decode("utf-8", "replace")
    except Exception as ex:
        print("  GetCapabilities failed (%s); trying known layer names" % str(ex)[:44])
        return list(IPIS_FALLBACK_LAYERS)
    names = re.findall(r"<Name>([^<]+)</Name>", caps)
    mines = [n for n in names if "mine" in n.lower()]
    # DRC (cod) first, then CAR (caf), then anything else with mines in the name
    mines.sort(key=lambda n: (0 if "cod" in n.lower() else 1 if "caf" in n.lower() else 2,
                              0 if "curated" in n.lower() else 1, len(n)))
    if mines:
        print("  GeoServer advertises %d layer(s); %d mention mines. Trying: %s"
              % (len(names), len(mines), ", ".join(mines[:3])))
    else:
        print("  GetCapabilities returned %d layers, none mentioning mines \u2014 "
              "the dataset may have moved" % len(names))
    return mines[:4] + [n for n in IPIS_FALLBACK_LAYERS if n not in mines]


def ipis_url(layer):
    return (IPIS_BASE + "?service=WFS&version=1.0.0&request=GetFeature"
            "&typeName=" + urllib.parse.quote(layer) +
            "&outputFormat=application%2Fjson&maxFeatures=6000")


def harvest_ipis(a):
    gj = None

    # GitHub runners could not reach geo.ipisresearch.be at all -- connection
    # timed out on every attempt including GetCapabilities, which is the
    # cloud-IP block, not a slow query. So the same data/ escape hatch the other
    # sources use applies here: download the GeoJSON once and commit it.
    # IPIS publishes CSV as well as GeoJSON, and the CSV is what their download
    # page actually offers. Both are accepted; more than one file is read, so
    # DRC and CAR can be committed side by side.
    exports = []
    if a.file:
        exports = [a.file]
    elif os.path.isdir(DATA_DIR):
        exports = [os.path.join(DATA_DIR, f) for f in sorted(os.listdir(DATA_DIR))
                   if any(k in f.lower() for k in ("ipis", "mines"))
                   and f.lower().endswith((".csv", ".json", ".geojson"))]
    if exports:
        feats = []
        for fp in exports:
            try:
                if fp.lower().endswith(".csv"):
                    import csv as _csv
                    n0 = len(feats)
                    with open(fp, encoding="utf-8-sig") as fh:
                        for r in _csv.DictReader(fh):
                            try:
                                lat = float(r.get("latitude") or r.get("lat"))
                                lng = float(r.get("longitude") or r.get("lon") or r.get("lng"))
                            except (TypeError, ValueError):
                                continue
                            feats.append({"geometry": {"coordinates": [lng, lat]},
                                          "properties": r})
                    print("  %s: %d sites" % (os.path.basename(fp), len(feats) - n0))
                else:
                    j = json.loads(open(fp, encoding="utf-8").read())
                    feats.extend(j.get("features", []))
                    print("  %s: %d features" % (os.path.basename(fp),
                                                 len(j.get("features", []))))
            except Exception as ex:
                print("  could not read %s: %s" % (os.path.basename(fp), str(ex)[:60]))
        if feats:
            gj = {"features": feats}

    if gj is None:
        for layer in ipis_layers():
            try:
                raw = fetch(ipis_url(layer), timeout=240)
                gj = json.loads(raw.decode("utf-8", "replace"))
                if gj.get("features"):
                    print("  layer %s: %d features" % (layer, len(gj["features"])))
                    break
                gj = None
            except Exception as ex:
                print("  %-52s %s" % (layer, str(ex)[:40]))
                gj = None
    if not gj:
        print("  IPIS unreachable. A connection timeout on every attempt, including "
              "GetCapabilities, is the host refusing cloud IP ranges rather than a "
              "slow query \u2014 GitHub runners come from those ranges.")
        print("  Fix it once, by hand:")
        print("    1. open https://ipisresearch.be/home/maps-data/open-data/")
        print("    2. download the DRC mining sites layer as GeoJSON")
        print("    3. commit it to data/ipis_mines.geojson")
        print("  It is then used on every run without any network call.")
        return []
    feats = gj.get("features", [])
    print("  IPIS features: %d" % len(feats))
    out = []
    for f in feats:
        g = (f.get("geometry") or {}).get("coordinates")
        p = f.get("properties") or {}
        if not g or len(g) < 2:
            continue
        child = str(p.get("childunder15") or p.get("child_labor")
                    or p.get("child_labour") or p.get("presence_enfants") or "")
        childwork = str(p.get("childunder15work") or "").strip()
        forced = any(str(p.get("forced_labour_armed_group%d" % i) or "").strip() == "1"
                     for i in (1, 2, 3))
        armed = str(p.get("armed_group1") or p.get("interference") or "")
        workers = p.get("workers_numb") or p.get("workers") or ""
        mineral = p.get("mineral1") or p.get("mineral") or ""
        name = p.get("name") or p.get("mine") or "Artisanal mining site"
        # "1" is a yes/no flag in the DRC file; the CAR file records a count.
        try:
            flagged = float(child) > 0
        except ValueError:
            flagged = child.strip().lower() in ("true", "yes", "oui")
        out.append({
            "name": str(name)[:120],
            "source": "ipis",
            "type": ("Artisanal mining site"
                     + (" \u2014 forced labour observed" if forced else
                        " \u2014 child labour observed" if flagged else "")),
            "lat": float(g[1]), "lng": float(g[0]),
            "precise": True,
            "impact": 5 if forced else 4 if flagged else 3,
            "status": ("Forced labour observed" if forced else
                       "Child labour observed" if flagged else "Site visited"),
            "state": "eastern DR Congo",
            "url": "https://ipisresearch.be/home/maps-data/maps-of-drc/",
            "desc": ("Field-visited by IPIS."
                     + (" Mineral: %s." % mineral if mineral else "")
                     + (" Reported workers: %s." % workers if workers else "")
                     + (" <b>Forced labour by an armed group recorded at this site.</b>" if forced else "")
                     + (" <b>Children under 15 observed working at this site.</b>" if flagged else "")
                     + ((" Tasks recorded for them: %s." % childwork) if childwork else "")
                     + (" Armed interference recorded: %s." % armed if armed and armed.lower() not in ("none", "0") else "")
                     + " IPIS has mapped roughly 2,800 sites in eastern DRC since 2009 through "
                       "repeat field visits, recording child labour, armed-group interference, "
                       "worker numbers and minerals per site. Unusually for this field, the "
                       "child-labour flag is a direct field observation rather than an inference."
                     + ("" if (flagged or forced) else CAVEAT)),
        })
    return out


# ====================================================================== KILNS
KILN_SOURCES = [
    "https://huggingface.co/api/datasets/SustainabilityLabIITGN/SentinelKilnDB",
]


def harvest_kilns(a):
    """SentinelKilnDB ships as parquet on HuggingFace. The label files carry the
    geometry; --file takes a CSV/GeoJSON you have already extracted, which is the
    realistic path until they publish a flat coordinate export."""
    if not a.file:
        print("  SentinelKilnDB (62,671 kilns) is published as parquet tiles on "
              "HuggingFace rather than a flat coordinate file, so it needs one "
              "extraction step:\n"
              "      pip3 install datasets pandas\n"
              "      python3 -c \"from datasets import load_dataset; "
              "d=load_dataset('SustainabilityLabIITGN/SentinelKilnDB',split='train'); "
              "d.to_pandas()[['lat','lon','kiln_type']].to_csv('kilns.csv',index=False)\"\n"
              "      python3 harvest_points.py --kilns --file kilns.csv\n"
              "  Licence is CC-BY-NC-4.0 \u2014 check it against your use before publishing.")
        return []
    import csv as _csv
    fp = read_file(find_export(a.file, "kiln"), "Run the extraction command printed above to create kilns.csv, "
                           "then pass it with --file.")
    if not fp:
        return []
    rows = list(_csv.DictReader(open(fp, encoding="utf-8")))
    out = []
    for r in rows:
        try:
            lat = float(r.get("lat") or r.get("latitude"))
            lng = float(r.get("lon") or r.get("lng") or r.get("longitude"))
        except Exception:
            continue
        kt = r.get("kiln_type") or r.get("type") or ""
        out.append({
            "name": "Brick kiln" + (" (%s)" % kt if kt else ""),
            "source": "kilns",
            "type": "Brick kiln",
            "lat": lat, "lng": lng, "precise": True,
            "impact": 3, "status": "Site detected",
            "state": "Indo-Gangetic Plain",
            "url": "https://huggingface.co/datasets/SustainabilityLabIITGN/SentinelKilnDB",
            "desc": ("Brick kiln detected from Sentinel-2 satellite imagery and hand-validated, "
                     "from SentinelKilnDB \u2014 62,671 kilns across the Indo-Gangetic Plain "
                     "covering India, Pakistan, Bangladesh and Afghanistan. Brick kilns are the "
                     "most consistently documented bonded-labour sector in South Asia: the "
                     "mechanism is the peshgi advance, worked off across a whole family at a rate "
                     "that never clears." + CAVEAT),
        })
    print("  kilns parsed: %d" % len(out))
    return out


# ========================================================== OPEN SUPPLY HUB
def harvest_osh(a):
    # A committed Data Download is a first-class input, not a fallback: it is
    # now the only route that does not require a subscription.
    fp = find_export(None, "osh", "supply", "facilit")
    if fp and fp.lower().endswith(".csv"):
        import csv as _csv
        out = []
        with open(fp, encoding="utf-8-sig") as fh:
            for r in _csv.DictReader(fh):
                try:
                    lat = float(r.get("lat") or r.get("latitude"))
                    lng = float(r.get("lng") or r.get("lon") or r.get("longitude"))
                except (TypeError, ValueError):
                    continue
                out.append({
                    "name": str(r.get("name") or "Production facility")[:120],
                    "source": "osh", "type": "Production facility",
                    "lat": lat, "lng": lng, "precise": True,
                    "impact": 2, "status": "Facility",
                    "state": r.get("country_name") or r.get("country") or "",
                    "url": ("https://opensupplyhub.org/facilities/"
                            + str(r.get("os_id") or r.get("id") or "")),
                    "desc": ("Production facility listed on Open Supply Hub. Open the "
                             "record for who disclosed it and which buyers are connected "
                             "to it \u2014 that link from a site to a buyer is the leverage "
                             "a country-level determination does not give you." + CAVEAT),
                })
        print("  %s: %d facilities" % (os.path.basename(fp), len(out)))
        return out

    if not a.token:
        print("  Open Supply Hub API access is no longer free on signup. As of 2026 it "
              "is a paid subscription with a 14-day trial, and the old "
              "My Account > Settings > API > Generate token path is gone.")
        print("  Two routes that do not cost money:")
        print("    1. Free/discounted access policy for non-profits, civil society "
              "organisations and research institutions \u2014 application form, "
              "reviewed within two weeks. See info.opensupplyhub.org/api.")
        print("    2. Data Downloads: the same data as CSV or Excel, no API needed. "
              "Commit the file to data/ with 'osh' or 'supply' in the filename.")
        print("  Worth weighing before either: this layer maps FACILITIES, not "
              "exploitation. It is the weakest of the point layers on its own, and "
              "its real value is the link from a site to a named buyer.")
        return []
    out, page = [], 1
    countries = (a.countries or "BD,IN,PK,KH,MM,VN,CN,ET,TR").split(",")
    _ = countries
    for cc in countries:
        page = 1
        while page <= (a.pages or 3):
            url = ("https://opensupplyhub.org/api/facilities/?countries=%s&page=%d&pageSize=50"
                   % (urllib.parse.quote(cc.strip()), page))
            try:
                gj = json.loads(fetch(url, headers={"Authorization": "Token " + a.token})
                                .decode("utf-8", "replace"))
            except Exception as ex:
                print("  OSH %s page %d failed: %s" % (cc, page, str(ex)[:60]))
                break
            feats = gj.get("features") or []
            if not feats:
                break
            for f in feats:
                g = (f.get("geometry") or {}).get("coordinates")
                p = f.get("properties") or {}
                if not g:
                    continue
                out.append({
                    "name": str(p.get("name") or "Production facility")[:120],
                    "source": "osh",
                    "type": "Production facility",
                    "lat": float(g[1]), "lng": float(g[0]), "precise": True,
                    "impact": 2, "status": "Facility",
                    "state": p.get("country_name") or cc,
                    "url": "https://opensupplyhub.org/facilities/" + str(p.get("os_id") or ""),
                    "desc": ("Production facility listed on Open Supply Hub, contributed by "
                             "brands, unions and NGOs and deduplicated against a shared "
                             "identifier. Open the record for who disclosed it and which "
                             "buyers are connected to it \u2014 that link from a site to a "
                             "buyer is the leverage a determination on its own does not give "
                             "you." + CAVEAT),
                })
            page += 1
    print("  OSH facilities: %d" % len(out))
    return out


# ==================================================================== HOTLINES
def harvest_hotlines(a):
    """The State Department's country-by-country helpline index, parsed into
    per-country entries for trackerdata.json rather than left as a single link."""
    try:
        html = fetch("https://www.state.gov/human-trafficking-hotlines/").decode("utf-8", "replace")
    except Exception as ex:
        print("  hotline page fetch failed: %s" % str(ex)[:80])
        return {}
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    out = {}

    # 1. proper tables
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
        cells = [re.sub(r"<[^>]+>", " ", c)
                 for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(cells) < 2:
            continue
        country = " ".join(cells[0].split())
        number = " ".join(" ".join(cells[1:]).split())
        if country and number and len(country) <= 60 and re.search(r"\d", number):
            out[country] = number

    # 2. the page is actually paragraphs and list items in the form
    #    "Country: +00 000 0000" or "Country — 116 000". The table parser found
    #    nothing on the live page, which is what "0 countries" meant.
    if not out:
        blocks = re.findall(r"<(?:li|p|h[3-5])[^>]*>(.*?)</(?:li|p|h[3-5])>", text, re.S)
        for b in blocks:
            line = " ".join(re.sub(r"<[^>]+>", " ", b).split())
            m = re.match(r"^([A-Z][A-Za-z .'\u2019()\-]{2,45}?)\s*[:\u2013\u2014-]\s*(.+)$", line)
            if not m:
                continue
            country, number = m.group(1).strip(), m.group(2).strip()
            if not re.search(r"\d{3}", number) or len(number) > 200:
                continue
            out[country] = number

    if not out:
        plain = " ".join(re.sub(r"<[^>]+>", " ", text).split())
        print("  hotlines parsed: 0 countries \u2014 neither a table nor "
              "'Country: number' lines matched in %d bytes (%d words of visible "
              "text). The page layout has changed; re-run with --dump and send "
              "the file." % (len(html), len(plain.split())))
        if a.dump:
            fn = os.path.join(HERE, "hotlines_page.html")
            open(fn, "w", encoding="utf-8").write(html)
            print("       dumped to %s" % os.path.basename(fn))
    else:
        print("  hotlines parsed: %d countries" % len(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("ipis", "kilns", "osh", "hotlines", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--token")
    ap.add_argument("--countries")
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--decimate", type=float, default=0.05,
                    help="degrees per grid cell; 0 disables thinning")
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.ipis, a.kilns, a.osh, a.hotlines, a.all]):
        ap.error("choose --ipis, --kilns, --osh, --hotlines or --all")

    pts = []
    if a.ipis or a.all:
        print("=== IPIS: eastern DRC artisanal mining sites ===")
        pts += harvest_ipis(a)
    if a.kilns or a.all:
        print("=== SentinelKilnDB: South Asian brick kilns ===")
        pts += harvest_kilns(a)
    if a.osh or a.all:
        print("=== Open Supply Hub: production facilities ===")
        pts += harvest_osh(a)

    if pts:
        kept, dropped = decimate(pts, a.decimate)
        if dropped:
            print("decimated: %d kept, %d dropped at %.3f\u00b0 per cell "
                  "(a display decision, not a claim about what exists \u2014 "
                  "use --decimate 0 for the full set)" % (len(kept), dropped, a.decimate))
        by = defaultdict(int)
        for p in kept:
            by[p["source"]] += 1
        print("points: %d  %s" % (len(kept), dict(by)))
        if not a.dry_run:
            out = os.path.join(HERE, "points.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                           "note": ("Sector infrastructure at coordinate precision. "
                                    "NOT confirmed exploitation \u2014 sites in sectors "
                                    "where forced and child labour are documented to "
                                    "concentrate."),
                           "projects": kept}, f, ensure_ascii=False, indent=1)
            print("wrote", out, "-", os.path.getsize(out), "bytes")

    if a.hotlines or a.all:
        print("=== State Department: national helpline index ===")
        h = harvest_hotlines(a)
        if h and not a.dry_run:
            out = os.path.join(HERE, "hotlines.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                           "source": "US Department of State",
                           "hotlines": h}, f, ensure_ascii=False, indent=1)
            print("wrote", out, "-", os.path.getsize(out), "bytes")
        elif h:
            for k in list(h)[:12]:
                print("  %-28s %s" % (k, h[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
