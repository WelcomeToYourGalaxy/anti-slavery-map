#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_companies.py -- the buyer end of the chain.

    python3 harvest_companies.py --uk
    python3 harvest_companies.py --australia
    python3 harvest_companies.py --uflpa
    python3 harvest_companies.py --all -v

Writes companies.json.

WHY THIS IS THE HOLE WORTH FILLING
----------------------------------
Every determination on this map names a producer, a commodity or a country. The
leverage is at the other end. A workplace has little to lose; the brand several
tiers above it has a reputation, a compliance obligation and a legal exposure,
and is reachable in a way a subcontractor is not.

Open Supply Hub is the route to facility-to-buyer links and it is behind a
subscription. But two governments already compel the buyer end to publish, and
those registries are open:

  uk          The UK Modern Slavery Statement Registry. Every organisation over
              the turnover threshold that supplies goods or services in the UK
              must publish an annual statement. Thousands of companies, with the
              statement text, the year, and whether the required approvals were
              given.

  australia   The Australian Modern Slavery Register. Same shape, mandatory
              reporting criteria, and statements are assessed against them.

  uflpa       The DHS UFLPA Entity List. Companies whose goods are presumed
              made with forced labour and barred from US entry. Not a
              disclosure -- a determination, and the sharpest one in this whole
              field because the consequence is automatic.

WHAT A STATEMENT IS AND IS NOT
------------------------------
A published statement is not evidence of good practice, and its absence is not
evidence of bad. The obligation is to publish, not to have found anything. The
research consistently finds most statements are boilerplate.

That is exactly what makes the registry useful here, and every record says so:
it gives you a named company, a date, a document you can quote back, and a legal
duty they are already under. A statement that says the company found nothing,
next to a determination naming its supplier country and commodity, is a
question someone has to answer.

REGISTRY RECORDS ARE COMPANIES, NOT PLACES
------------------------------------------
They carry no site. They are written country-level, which means the map puts
them in the country hover panel rather than drawing them as dots -- the same
rule that moved the listed goods off the map. A company is not a location.
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
OUT = os.path.join(HERE, "companies.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

UK_SOURCES = [
    "https://modern-slavery-statement-registry.service.gov.uk/download",
    "https://modern-slavery-statement-registry.service.gov.uk/api/statements",
]
AU_SOURCES = [
    "https://modernslaveryregister.gov.au/api/statements",
    "https://data.gov.au/data/dataset/modern-slavery-register",
]
UFLPA_SOURCES = [
    "https://www.dhs.gov/uflpa-entity-list",
    "https://data.opensanctions.org/datasets/latest/us_dhs_uflpa/targets.nested.json",
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
        if low.endswith((".csv", ".json", ".xlsx")) and any(p in low for p in patterns):
            p = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return p
    return None


def rows_from(src):
    raw = open(src, "rb").read() if isinstance(src, str) else src
    txt = raw.decode("utf-8", "replace").lstrip()
    if txt[:1] in "[{":
        try:
            j = json.loads(txt)
        except Exception:
            return []
        if isinstance(j, list):
            return j
        for k in ("statements", "results", "data", "items", "entities"):
            if isinstance(j.get(k), list):
                return j[k]
        return []
    return list(csv.DictReader(io.StringIO(txt)))


def low_keys(r):
    return {str(k).lower().replace(" ", "").replace("_", ""): v for k, v in r.items()}


STATEMENT_CAVEAT = (
    " <b>A published statement is not evidence of good practice, and its absence is not "
    "evidence of bad.</b> The legal duty is to publish, not to have found anything, and "
    "the research consistently finds most statements are boilerplate. What it gives you "
    "is a named company, a date, a document you can quote back, and a duty they are "
    "already under \u2014 which is what a question needs to be answerable.")


# ======================================================================= UK
def harvest_uk(a):
    src = find_export("uk_modern_slavery", "msa_uk", "statement_registry", "ukmsr")
    raw = src
    if not raw:
        for u in UK_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s" % u)
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-60s %s" % (u[:60], str(ex)[:34]))
    if not raw:
        print("  The UK Modern Slavery Statement Registry publishes a bulk download at "
              "modern-slavery-statement-registry.service.gov.uk. Take it and commit it "
              "to data/ with 'ukmsr' or 'statement_registry' in the filename.")
        return []

    out = []
    for r in rows_from(raw):
        lo = low_keys(r)
        name = str(lo.get("organisationname") or lo.get("companyname")
                   or lo.get("name") or "").strip()
        if not name:
            continue
        year = str(lo.get("year") or lo.get("periodend") or lo.get("statementyear") or "")[:4]
        url = str(lo.get("statementurl") or lo.get("url") or "").strip()
        sector = str(lo.get("sector") or lo.get("industry") or "").strip()
        approved = str(lo.get("boardapproval") or lo.get("approved") or "").strip()
        out.append({
            "name": name[:130],
            "source": "ukmsr",
            "type": "Modern slavery statement (UK)",
            "iso": "GBR",
            "state": "United Kingdom",
            "precise": False,
            "impact": 2,
            "status": ("Statement %s" % year) if year else "Statement published",
            "url": url or "https://modern-slavery-statement-registry.service.gov.uk/",
            "desc": (("<b>%s</b> published a modern slavery statement%s%s. "
                      % (name, (" for %s" % year) if year else "",
                         (", %s" % sector) if sector else ""))
                     + (("Board approval recorded: %s. " % approved) if approved else "")
                     + "Required under section 54 of the Modern Slavery Act 2015 of any "
                       "organisation over the turnover threshold supplying goods or "
                       "services in the UK."
                     + STATEMENT_CAVEAT
                     + " Read it against the determinations for the countries and "
                       "commodities this company buys from: a statement saying nothing "
                       "was found, next to a listed good from a sourcing country, is a "
                       "question someone has to answer."),
        })
    print("  UK statements: %d" % len(out))
    return out


# ================================================================ AUSTRALIA
def harvest_australia(a):
    src = find_export("australia", "au_modern", "modernslaveryregister", "aumsr")
    raw = src
    if not raw:
        for u in AU_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s" % u)
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-60s %s" % (u[:60], str(ex)[:34]))
    if not raw:
        print("  The Australian Modern Slavery Register (modernslaveryregister.gov.au) "
              "publishes statements and a dataset on data.gov.au. Commit either to "
              "data/ with 'aumsr' or 'australia' in the filename.")
        return []

    out = []
    for r in rows_from(raw):
        lo = low_keys(r)
        name = str(lo.get("entityname") or lo.get("reportingentity")
                   or lo.get("name") or "").strip()
        if not name:
            continue
        year = str(lo.get("reportingperiod") or lo.get("year") or "")[:4]
        url = str(lo.get("statementurl") or lo.get("link") or lo.get("url") or "").strip()
        out.append({
            "name": name[:130],
            "source": "aumsr",
            "type": "Modern slavery statement (Australia)",
            "iso": "AUS",
            "state": "Australia",
            "precise": False,
            "impact": 2,
            "status": ("Statement %s" % year) if year else "Statement published",
            "url": url or "https://modernslaveryregister.gov.au/",
            "desc": (("<b>%s</b> published a modern slavery statement%s. "
                      % (name, (" for %s" % year) if year else ""))
                     + "Required under Australia's Modern Slavery Act 2018, which unlike "
                       "the UK Act sets <b>mandatory reporting criteria</b> that a "
                       "statement must address \u2014 so an Australian statement can be "
                       "assessed against a standard rather than only read."
                     + STATEMENT_CAVEAT),
        })
    print("  Australian statements: %d" % len(out))
    return out


# ==================================================================== UFLPA
def harvest_uflpa(a):
    src = find_export("uflpa", "entitylist", "dhs")
    raw = src
    if not raw:
        for u in UFLPA_SOURCES:
            try:
                raw = fetch(u)
                print("  using: %s" % u)
                break
            except Exception as ex:
                if a.verbose:
                    print("  %-60s %s" % (u[:60], str(ex)[:34]))
    if not raw:
        print("  The DHS UFLPA Entity List is published at dhs.gov/uflpa-entity-list as "
              "a page rather than a feed; OpenSanctions mirrors it as structured data. "
              "Commit either to data/ with 'uflpa' in the filename.")
        return []

    rows = rows_from(raw)
    out = []
    for r in rows:
        lo = low_keys(r)
        props = r.get("properties") if isinstance(r, dict) else None
        if isinstance(props, dict):
            nm = props.get("name")
            name = (nm[0] if isinstance(nm, list) and nm else nm) or r.get("caption") or ""
            country = props.get("country") or [""]
            country = country[0] if isinstance(country, list) and country else str(country)
        else:
            name = str(lo.get("entity") or lo.get("name") or lo.get("company") or "")
            country = str(lo.get("country") or "")
        name = str(name).strip()
        if not name:
            continue
        iso = "CHN" if (not country or str(country).lower()[:2] in ("cn", "ch")) else ""
        out.append({
            "name": name[:130],
            "source": "uflpa",
            "type": "UFLPA Entity List",
            "iso": iso or "CHN",
            "state": str(country) or "China",
            "precise": False,
            "impact": 5,
            "status": "Import presumed barred",
            "url": "https://www.dhs.gov/uflpa-entity-list",
            "desc": ("<b>%s</b> is on the UFLPA Entity List. Goods made wholly or in "
                     "part by this entity are <b>presumed</b> to be made with forced "
                     "labour and barred from US entry unless an importer rebuts that "
                     "presumption with clear and convincing evidence. "
                     "This is not a disclosure and not a risk score \u2014 it is a "
                     "determination with an automatic consequence, which makes it the "
                     "sharpest instrument on this map. It is also the one most worth "
                     "checking against the current list before citing: entities are "
                     "added and, occasionally, removed." % name),
        })
    print("  UFLPA entities: %d" % len(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    for f in ("uk", "australia", "uflpa", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.uk, a.australia, a.uflpa, a.all]):
        ap.error("choose --uk, --australia, --uflpa or --all")

    recs = []
    if a.uflpa or a.all:
        print("=== DHS UFLPA Entity List ===")
        recs += harvest_uflpa(a)
    if a.uk or a.all:
        print("=== UK Modern Slavery Statement Registry ===")
        recs += harvest_uk(a)
    if a.australia or a.all:
        print("=== Australian Modern Slavery Register ===")
        recs += harvest_australia(a)

    print("total: %d" % len(recs))
    if a.dry_run:
        for r in recs[:15]:
            print("  %-52s %s" % (r["name"][:52], r["type"]))
        return 0
    if not recs:
        print("nothing harvested; companies.json left alone")
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "note": ("The buyer end: companies under a disclosure duty, and "
                            "entities under an import ban. Company records, not places "
                            "\u2014 they appear in the country panel rather than as dots."),
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
