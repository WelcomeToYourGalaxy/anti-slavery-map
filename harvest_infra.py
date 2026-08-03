#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_infra.py -- the infrastructure layers: ports, recruiters, zones.

    python3 harvest_infra.py --ports
    python3 harvest_infra.py --recruiters
    python3 harvest_infra.py --zones
    python3 harvest_infra.py --all -v

Writes infra.json.

WHAT THESE THREE HAVE IN COMMON
-------------------------------
None of them is evidence of exploitation. All three are places where the
*mechanism* operates, and each sits at a different point in it:

  ports        where a fishing crew can be transferred between vessels without
               anyone going ashore. Transhipment is how a person stays at sea
               for years, and it is also the point where a port state could
               inspect and mostly does not.

  recruiters   the licensed agency at the ORIGIN end. This is where the fee is
               charged and the debt created, months before anyone reaches a
               workplace. It is also the only point in the whole chain where a
               single administrative act -- pulling a licence -- stops the next
               hundred people being placed.

  zones        export processing and free zones, where labour law, inspection
               or union rights are reduced by statute to attract investment.
               The exploitation there is not a failure of enforcement; it is
               the absence of law by design.

Every record says, in its own text, that it marks infrastructure and not a
finding. That distinction is enforced everywhere else on this map and it
matters most here, because these are the layers where a dot is most likely to
be read as an accusation.

WHAT IS AND IS NOT AUTOMATABLE
------------------------------
Ports:       yes. The World Port Index is public-domain US government data with
             coordinates for roughly 3,700 ports.
Recruiters:  partly. Several origin states publish licensed-agency registers,
             but as HTML tables or PDFs behind JS. Committed exports in data/
             are the reliable route and are treated as first-class.
Zones:       no authoritative global boundary set exists that I can verify. The
             ILO and UNCTAD publish counts and country lists rather than
             geometry. This reads a committed file and does not pretend
             otherwise.
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
OUT = os.path.join(HERE, "infra.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

NOT_A_FINDING = (" <b>This marks infrastructure, not a finding.</b> It is a place where the "
                 "mechanism operates, not evidence that anyone here is exploited. Read it as "
                 "context for the determinations and cases on the other layers.")

WPI_SOURCES = [
    "https://msi.nga.mil/api/publications/download?key=16694622/SFH00000/UpdatedPub150.csv&type=view",
    "https://raw.githubusercontent.com/datasets/world-port-index/main/data/wpi.csv",
]


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
        if low.endswith((".csv", ".json", ".geojson", ".xlsx", ".zip", ".dbf")) and any(p in low for p in patterns):
            p = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return p
    return None


def num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None



def read_dbf(path, encoding="latin-1"):
    """Minimal DBF reader.

    The World Port Index ships as an Access database or a shapefile. Neither is
    a format you can read with the standard library alone -- except that a
    shapefile's attributes are a DBF, and DBF is simple enough to parse
    directly: fixed-width records behind a field descriptor table. That avoids
    making anyone install GDAL or pyshp to put ports on a map.

    The .shp holds the geometry, but WPI's DBF carries latitude and longitude
    as fields too, so the attributes alone are enough.
    """
    with open(path, "rb") as f:
        raw = f.read()
    if len(raw) < 32:
        return []
    nrec = int.from_bytes(raw[4:8], "little")
    hdr = int.from_bytes(raw[8:10], "little")
    rlen = int.from_bytes(raw[10:12], "little")
    fields, pos = [], 32
    while pos < hdr - 1 and raw[pos] != 0x0D:
        name = raw[pos:pos + 11].split(b"\x00")[0].decode(encoding, "replace").strip()
        ftype = chr(raw[pos + 11])
        flen = raw[pos + 16]
        fields.append((name, ftype, flen))
        pos += 32
    rows = []
    for i in range(nrec):
        off = hdr + i * rlen
        rec = raw[off:off + rlen]
        if not rec or rec[:1] == b"*":          # deleted
            continue
        cur, out = 1, {}
        for name, ftype, flen in fields:
            val = rec[cur:cur + flen].decode(encoding, "replace").strip()
            out[name] = val
            cur += flen
        rows.append(out)
    return rows


def wpi_rows(fp):
    """Accept the shapefile bundle, the .dbf on its own, or a CSV export."""
    import zipfile
    if fp.lower().endswith(".zip"):
        with zipfile.ZipFile(fp) as z:
            names = z.namelist()
            dbf = next((n for n in names if n.lower().endswith(".dbf")), None)
            csvn = next((n for n in names if n.lower().endswith(".csv")), None)
            if dbf:
                tmp = os.path.join(HERE, "_wpi_tmp.dbf")
                with open(tmp, "wb") as out:
                    out.write(z.read(dbf))
                try:
                    return read_dbf(tmp)
                finally:
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
            if csvn:
                return list(csv.DictReader(io.StringIO(
                    z.read(csvn).decode("utf-8", "replace"))))
        return []
    if fp.lower().endswith(".dbf"):
        return read_dbf(fp)
    return list(csv.DictReader(open(fp, encoding="utf-8-sig")))


# ====================================================================== PORTS
FISHING_HINT = ("fish", "seafood", "trawl", "cannery", "processing")


def harvest_ports(a):
    raw = None
    fp = find_export("port", "wpi", "pub150")
    rows = None
    if fp:
        rows = wpi_rows(fp)
        print("  %s: %d rows" % (os.path.basename(fp), len(rows)))
    if rows is None:
        for u in WPI_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s (%d bytes)" % (u[:70], len(raw)))
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-64s %s" % (u[:64], str(ex)[:40]))
    if rows is None and not raw:
        print("  World Port Index unreachable. It is public-domain US government "
              "data; download Pub 150 from msi.nga.mil and commit it to data/ "
              "with 'port' in the filename.")
        return []

    if rows is None:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))
    if not rows:
        print("  no rows parsed")
        return []

    def col(r, *keys):
        for k in r:
            kl = k.lower().replace(" ", "").replace("_", "")
            if any(x in kl for x in keys):
                return r[k]
        return None

    out = []
    for r in rows:
        lat, lng = num(col(r, "latitude", "ycoord")), num(col(r, "longitude", "xcoord"))
        if lat is None or lng is None:
            continue
        name = (col(r, "portname", "mainportname", "name") or "Port").strip()
        country = (col(r, "country") or "").strip()
        # The WPI encodes harbour size as a single letter -- V(ery small), S,
        # M(edium), L(arge) -- and has no fishing flag at all. The previous
        # version looked for the word "fish" in the row, found it 5 times in
        # 3,630, and silently dropped 3,100 ports on a test that could not work.
        harbour = str(col(r, "harborsize", "harboursize") or "").strip().upper()[:1]
        SIZE = {"L": ("large", 3), "M": ("medium", 3), "S": ("small", 2),
                "V": ("very small", 2)}
        size_word, impact = SIZE.get(harbour, ("unclassified", 2))
        name_l = name.lower()
        fishing = any(w in name_l for w in FISHING_HINT)
        if a.big_only and harbour not in ("L", "M"):
            continue
        out.append({
            "name": name[:100],
            "source": "ports",
            "type": "Port \u2014 %s harbour" % size_word,
            "lat": lat, "lng": lng, "precise": True,
            "impact": impact + (1 if fishing else 0),
            "status": "Port",
            "state": country,
            "url": "https://msi.nga.mil/Publications/WPI",
            "desc": (("Port listed in the World Port Index"
                      + (" (%s)" % country if country else "")
                      + ", %s harbour. " % size_word)
                     + "Ports matter here for one specific reason: <b>transhipment</b>. "
                       "Catch and crew transferred between vessels at sea, or in port without "
                       "anyone going ashore, is how a fisher stays offshore for months or "
                       "years \u2014 and the port state is the authority that could inspect and "
                       "usually does not. A vessel that never lands its crew is the documented "
                       "forced-labour signature at sea."
                     + NOT_A_FINDING),
        })
    print("  ports kept: %d of %d" % (len(out), len(rows)))
    return out


# ================================================================ RECRUITERS
# Origin states that license overseas recruitment. Each publishes a register;
# most are HTML tables or PDFs behind JS, so a committed export is the reliable
# route. The country entry on the map already links each register.
RECRUIT_REGISTERS = [
    ("PHL", "Department of Migrant Workers", "https://dmw.gov.ph/"),
    ("NPL", "Foreign Employment Board", "https://fepb.gov.np/"),
    ("BGD", "BMET", "https://bmet.gov.bd/"),
    ("LKA", "Sri Lanka Bureau of Foreign Employment", "https://www.slbfe.lk/"),
    ("IDN", "BP2MI", "https://bp2mi.go.id/"),
    ("IND", "eMigrate", "https://emigrate.gov.in/"),
    ("ETH", "Ministry of Labour and Skills", "https://mols.gov.et/"),
]


def harvest_recruiters(a):
    fp = find_export("recruit", "agenc", "agency")
    if not fp:
        print("  No committed register found. Licensed-recruiter lists are published by:")
        for iso, name, url in RECRUIT_REGISTERS:
            print("    %-4s %-42s %s" % (iso, name, url))
        print("  Most are HTML tables or PDFs behind JS. Export one, commit it to "
              "data/ with 'recruit' or 'agency' in the filename, and it is read on "
              "every run. Expected columns: agency name, licence number, address or "
              "city, country; latitude and longitude if the source has them.")
        return []

    rows = list(csv.DictReader(open(fp, encoding="utf-8-sig")))
    out, nogeo = [], 0
    for r in rows:
        low = {k.lower().replace(" ", "").replace("_", ""): v for k, v in r.items()}
        lat = num(low.get("latitude") or low.get("lat"))
        lng = num(low.get("longitude") or low.get("lon") or low.get("lng"))
        name = (low.get("name") or low.get("agency") or low.get("agencyname") or "").strip()
        if not name:
            continue
        if lat is None or lng is None:
            nogeo += 1
            continue
        lic = (low.get("licence") or low.get("license") or low.get("licenseno") or "").strip()
        out.append({
            "name": name[:110],
            "source": "recruiters",
            "type": "Licensed recruitment agency",
            "lat": lat, "lng": lng, "precise": True,
            "impact": 3, "status": "Licensed",
            "state": (low.get("city") or low.get("country") or "").strip(),
            "url": (low.get("url") or "").strip() or "https://www.ilo.org/fair-recruitment",
            "desc": (("Licensed overseas recruitment agency"
                      + ((", licence %s" % lic) if lic else "") + ". ")
                     + "The origin end of the chain, and the point most worth watching: "
                       "<b>this is where the fee is charged and the debt created</b>, months "
                       "before anyone reaches a workplace. It is also the only place where a "
                       "single administrative act \u2014 pulling a licence \u2014 stops the next "
                       "hundred people being placed. Check a worker's agency against the "
                       "register before any money changes hands; an unlicensed recruiter is "
                       "itself an offence and a far faster case than proving exploitation "
                       "afterwards."
                     + NOT_A_FINDING),
        })
    if nogeo:
        print("  %d agency row(s) had no coordinates and were dropped rather than "
              "placed at a country centre \u2014 an agency is an address, and a "
              "centroid would say something the register does not" % nogeo)
    print("  recruitment agencies: %d" % len(out))
    return out


# ====================================================================== ZONES
def harvest_zones(a):
    fp = find_export("zone", "epz", "sez", "freezone")
    if not fp:
        print("  No committed zone file. There is no authoritative global boundary "
              "set for export processing and free zones that I can verify \u2014 the ILO "
              "and UNCTAD publish counts and country lists, not geometry, and the "
              "commercial datasets are not open.")
        print("  If you have one (a national SEZ authority's shapefile, or UNCTAD's "
              "World Investment Report annex), commit it to data/ with 'zone', "
              "'epz' or 'sez' in the filename. Expected columns: name, country, "
              "latitude, longitude.")
        print("  Until then the zones stay off the map rather than being approximated, "
              "because a zone drawn in the wrong place is worse than no zone.")
        return []

    rows = list(csv.DictReader(open(fp, encoding="utf-8-sig")))
    out = []
    for r in rows:
        low = {k.lower().replace(" ", "").replace("_", ""): v for k, v in r.items()}
        lat = num(low.get("latitude") or low.get("lat"))
        lng = num(low.get("longitude") or low.get("lon") or low.get("lng"))
        name = (low.get("name") or low.get("zone") or low.get("zonename") or "").strip()
        if not name or lat is None or lng is None:
            continue
        out.append({
            "name": name[:110],
            "source": "zones",
            "type": "Export processing / free zone",
            "lat": lat, "lng": lng, "precise": True,
            "impact": 3, "status": "Zone",
            "state": (low.get("country") or "").strip(),
            "url": (low.get("url") or "").strip() or "https://www.ilo.org/",
            "desc": ("Export processing or free zone. These are areas where labour law, "
                     "inspection or the right to organise is reduced or suspended by statute "
                     "to attract investment. That is the point worth holding on to: where "
                     "exploitation occurs in a zone it is often <b>not a failure of "
                     "enforcement but the absence of law by design</b>, which means the remedy "
                     "is legislative rather than a complaint to an inspector who has no "
                     "jurisdiction."
                     + NOT_A_FINDING),
        })
    print("  zones: %d" % len(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("ports", "recruiters", "zones", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--big-only", action="store_true",
                    help="keep only large and medium harbours")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.ports, a.recruiters, a.zones, a.all]):
        ap.error("choose --ports, --recruiters, --zones or --all")

    recs = []
    if a.ports or a.all:
        print("=== Ports and transhipment points ===")
        recs += harvest_ports(a)
    if a.recruiters or a.all:
        print("=== Licensed recruitment agencies ===")
        recs += harvest_recruiters(a)
    if a.zones or a.all:
        print("=== Export processing and free zones ===")
        recs += harvest_zones(a)

    print("total: %d record(s)" % len(recs))
    if a.dry_run or not recs:
        for r in recs[:15]:
            print("  %-40s %8.3f %9.3f  %s" % (r["name"][:40], r["lat"], r["lng"], r["type"]))
        return 0 if recs else 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "note": ("Infrastructure, not findings: ports where crews can be "
                            "transferred, agencies where debt is created, zones where "
                            "labour law is reduced by statute."),
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
