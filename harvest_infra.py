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

  ports        OFF BY DEFAULT. The port state is where inspection powers sit
               (ILO C188, the MLC, the FAO Port State Measures Agreement), and
               long voyages without port calls and at-sea transhipment are
               documented forced-labour indicators. But "every port" is not a
               finding -- it is a proxy for "trade happens here", with
               near-total coverage by construction, and it dilutes the evidence
               tiering the rest of the map depends on.

               A port earns a dot when the port is the evidenced object:
               crew-change and manning ports; ports flagged in AIS-gap or IUU
               analysis (Global Fishing Watch, Trygg Mat); ports with actual
               enforcement records (CBP detentions by port, EU FLR actions as
               they accrue); ITF inspector presence or absence, which is a real
               mappable variable and the more interesting map; and named
               crossings from corridor data rather than all crossings.

               --all-ports draws the full index as reference, labelled as
               reference.

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

NOT_A_FINDING = (" Note that this marks where the mechanism operates and is not evidence "
                 "that anyone here is necessarily exploited.")

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

# The World Port Index uses two-letter country codes; country-level selectors
# use ISO3. Only the codes that appear in the WPI are needed.
ISO2_TO_3 = {
 "AD":"AND","AE":"ARE","AF":"AFG","AG":"ATG","AI":"AIA","AL":"ALB","AM":"ARM",
 "AO":"AGO","AQ":"ATA","AR":"ARG","AS":"ASM","AT":"AUT","AU":"AUS","AW":"ABW",
 "AZ":"AZE","BA":"BIH","BB":"BRB","BD":"BGD","BE":"BEL","BF":"BFA","BG":"BGR",
 "BH":"BHR","BI":"BDI","BJ":"BEN","BM":"BMU","BN":"BRN","BO":"BOL","BR":"BRA",
 "BS":"BHS","BW":"BWA","BY":"BLR","BZ":"BLZ","CA":"CAN","CD":"COD","CF":"CAF",
 "CG":"COG","CH":"CHE","CI":"CIV","CK":"COK","CL":"CHL","CM":"CMR","CN":"CHN",
 "CO":"COL","CR":"CRI","CU":"CUB","CV":"CPV","CY":"CYP","CZ":"CZE","DE":"DEU",
 "DJ":"DJI","DK":"DNK","DM":"DMA","DO":"DOM","DZ":"DZA","EC":"ECU","EE":"EST",
 "EG":"EGY","ER":"ERI","ES":"ESP","ET":"ETH","FI":"FIN","FJ":"FJI","FK":"FLK",
 "FM":"FSM","FO":"FRO","FR":"FRA","GA":"GAB","GB":"GBR","GD":"GRD","GE":"GEO",
 "GF":"GUF","GH":"GHA","GI":"GIB","GL":"GRL","GM":"GMB","GN":"GIN","GP":"GLP",
 "GQ":"GNQ","GR":"GRC","GT":"GTM","GU":"GUM","GW":"GNB","GY":"GUY","HK":"HKG",
 "HN":"HND","HR":"HRV","HT":"HTI","HU":"HUN","ID":"IDN","IE":"IRL","IL":"ISR",
 "IN":"IND","IQ":"IRQ","IR":"IRN","IS":"ISL","IT":"ITA","JM":"JAM","JO":"JOR",
 "JP":"JPN","KE":"KEN","KH":"KHM","KI":"KIR","KM":"COM","KN":"KNA","KP":"PRK",
 "KR":"KOR","KW":"KWT","KY":"CYM","KZ":"KAZ","LB":"LBN","LC":"LCA","LK":"LKA",
 "LR":"LBR","LT":"LTU","LV":"LVA","LY":"LBY","MA":"MAR","MC":"MCO","MD":"MDA",
 "ME":"MNE","MG":"MDG","MH":"MHL","MM":"MMR","MO":"MAC","MP":"MNP","MQ":"MTQ",
 "MR":"MRT","MS":"MSR","MT":"MLT","MU":"MUS","MV":"MDV","MX":"MEX","MY":"MYS",
 "MZ":"MOZ","NA":"NAM","NC":"NCL","NG":"NGA","NI":"NIC","NL":"NLD","NO":"NOR",
 "NR":"NRU","NU":"NIU","NZ":"NZL","OM":"OMN","PA":"PAN","PE":"PER","PF":"PYF",
 "PG":"PNG","PH":"PHL","PK":"PAK","PL":"POL","PM":"SPM","PR":"PRI","PT":"PRT",
 "PW":"PLW","PY":"PRY","QA":"QAT","RE":"REU","RO":"ROU","RU":"RUS","SA":"SAU",
 "SB":"SLB","SC":"SYC","SD":"SDN","SE":"SWE","SG":"SGP","SH":"SHN","SI":"SVN",
 "SK":"SVK","SL":"SLE","SN":"SEN","SO":"SOM","SR":"SUR","ST":"STP","SV":"SLV",
 "SY":"SYR","TC":"TCA","TG":"TGO","TH":"THA","TL":"TLS","TN":"TUN","TO":"TON",
 "TR":"TUR","TT":"TTO","TV":"TUV","TW":"TWN","TZ":"TZA","UA":"UKR","US":"USA",
 "UY":"URY","VC":"VCT","VE":"VEN","VG":"VGB","VI":"VIR","VN":"VNM","VU":"VUT",
 "WS":"WSM","YE":"YEM","ZA":"ZAF"}

SELECTORS = {}
COUNTRY_SEL = {}
FISHING_HINT = ("fish", "seafood", "trawl", "cannery", "processing")



# ============================================================ PORT SELECTORS
# A port earns a dot when the port itself is the evidenced object. Each selector
# below is a JOIN against the World Port Index, not a list of its own: the WPI
# supplies the coordinates, the selector supplies the reason. With no selector
# files present the ports layer is EMPTY, and that is the correct output rather
# than a failure -- an unselected port has nothing to say.
PORT_SELECTORS = {
    "model": {
        "files": ("pnas_port", "highrisk_port", "modelport"),
        "label": "High-risk vessel calls",
        "impact": 4,
        "why": ("A measurable share of the fishing vessels calling here were "
                "flagged high-risk by the published behavioural model "
                "(McDonald et al., PNAS 2021), which is trained on 27 observable "
                "vessel behaviours \u2014 among them <b>AIS gaps over 12 and over "
                "24 hours</b>, <b>presence on an official IUU fishing list</b>, "
                "flag of convenience, visits to ports of convenience, and "
                "transhipment events with IUU or known forced-labour vessels. "
                "<b>A model output, and a disputed one</b>: a reply in the same "
                "journal notes that only 21 of 193 known abuse vessels produced "
                "profiles the method could use, and that the features are not "
                "causally linked to conditions on board. Treat it as where the "
                "model is pointing, not as what is there."),
        "src": "https://github.com/emlab-ucsb/slavery-in-fisheries",
    },
    "cbp": {
        "files": ("cbp_port", "detention", "uflpa_port", "enforcement"),
        "label": "Enforcement record",
        "impact": 5,
        "why": ("Goods have actually been detained or excluded here under a "
                "forced-labour import measure. <b>Not a risk indicator \u2014 a "
                "record of enforcement having happened</b>, which is the rarest "
                "thing on this layer and the only one with a consequence already "
                "attached."),
        "src": "https://www.cbp.gov/newsroom/stats/trade",
    },
}


def load_selectors(a):
    """Read whichever selector files are present and return
    {normalised port name: [(key, note), ...]}."""
    sel = {}
    COUNTRY_SEL.clear()
    for key, spec in PORT_SELECTORS.items():
        fp = find_export(*spec["files"])
        if not fp:
            continue
        try:
            rows = list(csv.DictReader(open(fp, encoding="utf-8-sig")))
        except Exception as ex:
            print("  could not read %s: %s" % (os.path.basename(fp), str(ex)[:50]))
            continue
        n = 0
        for r in rows:
            low = {str(k).lower().replace(" ", "").replace("_", ""): v
                   for k, v in r.items()}
            note = str(low.get("note") or low.get("detail") or low.get("inspector")
                       or low.get("count") or low.get("sharepct") or "").strip()
            name = str(low.get("port") or low.get("portname") or low.get("name")
                       or "").strip()
            if name:
                sel.setdefault(norm_port(name), []).append((key, note))
                n += 1
                continue
            # Some sources are published by PORT STATE rather than by port --
            # the PNAS port-visit table is one. Applying it to every port in the
            # country is coarse and is labelled as such in the record, but a
            # country where most fishing calls are made by flagged vessels is
            # telling you something real about its ports.
            iso = str(low.get("portiso3") or low.get("iso3") or low.get("country")
                      or "").strip().upper()
            if len(iso) == 3:
                COUNTRY_SEL.setdefault(iso, []).append(
                    (key, (note + " (country-level: this applies to the port state, "
                                  "not to this port specifically)").strip()))
                n += 1
        print("  selector %-6s %-28s %d port(s)" % (key, os.path.basename(fp), n))
    if not sel:
        print("  No port selector files in data/. The ports layer is EMPTY by design:")
        for key, spec in PORT_SELECTORS.items():
            print("    %-6s %-30s %s" % (key, spec["label"], spec["src"]))
        print("  Each is a CSV with a 'port' column; anything else is carried as a "
              "note. Commit one and only the ports it names are drawn, with the "
              "reason stated in the record. --all-ports still draws the whole "
              "index as labelled reference.")
    return sel


def norm_port(s):
    s = str(s or "").upper()
    for junk in (" HARBOR", " HARBOUR", " PORT OF ", "PORT OF ", " KO", " GANG"):
        s = s.replace(junk, " ")
    return " ".join(s.split())


def harvest_ports(a):
    raw = None
    # "port" alone matched cbp_port_detentions.csv, so the harvester read a
    # two-row selector file as if it were the World Port Index. Selector files
    # live in the same folder and several have "port" in the name; the index
    # itself is now identified specifically.
    fp = find_export("wpi", "world_port", "pub150")
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

    global SELECTORS
    SELECTORS = load_selectors(a)
    excluded = 0

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

        # PORT OF ENTRY is the field on this whole publication that matters
        # most here. A port of entry has customs and immigration; a vessel
        # calling anywhere else can take on fuel, water and provisions with
        # nobody official coming aboard and no crew going ashore. That is the
        # difference between a port call a fisher can use and one they cannot.
        poe = str(col(r, "portofentr", "portofentry") or "").strip().upper()[:1]
        med = str(col(r, "medfacil", "med_facil") or "").strip().upper()[:1]
        longshore = str(col(r, "longshore") or "").strip().upper()[:1]
        # A port layer with no denominator is not evidence of anything. Every
        # coastal country has ports; drawing all 3,630 says "trade happens
        # here" and dilutes the tiering the rest of the map depends on.
        #
        # So ports are OFF by default and only included when the port itself is
        # the evidenced object. --all-ports draws the full set for reference,
        # and says in each record that it is reference rather than evidence.
        hits = list(SELECTORS.get(norm_port(name)) or [])
        iso3 = ISO2_TO_3.get(str(country).strip().upper()[:2], "")
        if iso3:
            hits += COUNTRY_SEL.get(iso3, [])
        keys = set(k for k, _ in hits)

        # THE INVERSION. The interesting map is not "here are the flagged
        # ports" -- it is "here is where a crew has nobody to go to". So a port
        # is EXCLUDED only when it is both covered and unflagged: an ITF
        # inspector is present AND nothing has been flagged there. Everything
        # else is drawn, and the size runs the other way from what you would
        # expect -- the largest markers are the ports with the least protection,
        # because that is where the absence is.
        flagged = bool(keys & {"cbp", "model"})
        if not a.all_ports and not flagged:
            excluded += 1
            continue

        # 0 = an inspector and no flags (never drawn); 4 = no inspector, and
        # flagged by everything that can flag a port.
        exposure = len(keys & {"cbp", "model"})
        out.append({
            "name": name[:100],
            "source": "ports",
            "type": (("Port \u2014 " + ", ".join(
                        PORT_SELECTORS[k]["label"] for k, _ in hits))
                     if hits else "Port"),
            "lat": lat, "lng": lng, "precise": True,
            # Severity IS the exposure, so the marker scales with how little
            # stands between a crew and their employer.
            "impact": max(3, min(5, exposure + 3)),
            "exposure": exposure,
            "status": "Port",
            "state": country,
            "url": "https://msi.nga.mil/Publications/WPI",
            "desc": ("".join(
                        "<b>%s.</b> %s%s " % (PORT_SELECTORS[k]["label"],
                                              PORT_SELECTORS[k]["why"],
                                              (" " + note) if note else "")
                        for k, note in (hits or []))
                     + ("Port listed in the World Port Index"
                      + (" (%s)" % country if country else "")
                      + ", %s harbour. " % size_word)
                     + (("Recorded as a port of entry: customs and immigration are "
                         "present. ") if poe == "Y" else
                        ("Not recorded as a port of entry, so no customs or immigration "
                         "post. ") if poe == "N" else "")
                     + ("No medical facilities. " if med == "N" else "")
                     + ("No shore labour available, so the crew works the cargo. "
                        if longshore == "N" else "")
                     + "Ports are on this map because the port state is where the "
                       "inspection powers sit: ILO Convention 188 and the Maritime Labour "
                       "Convention give it authority to inspect and give a fisher or seafarer "
                       "an onshore complaint route, and the FAO Port State Measures Agreement "
                       "is built on the port being the chokepoint. Long voyages without port "
                       "calls and repeated transhipment at sea are documented forced-labour "
                       "indicators \u2014 see the ILO indicator framework and Global Fishing "
                       "Watch's published risk modelling. <b>The customs classification above "
                       "is not one of those indicators</b>: it describes what the port is for "
                       "trade purposes, and no one has validated it as a labour signal."
                     + NOT_A_FINDING),
        })
    print("  ports kept: %d of %d (%d excluded: nothing recorded against them)"
          % (len(out), len(rows), excluded))
    if out:
        import collections as _c
        dist = _c.Counter(r["exposure"] for r in out)
        print("  exposure 1=one selector, 2=both: %s"
              % dict(sorted(dist.items())))
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
    ap.add_argument("--all-ports", action="store_true",
                    help="draw the full World Port Index as a reference layer. Off by "
                         "default: a layer with no denominator is not evidence.")
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
