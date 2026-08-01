#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_cases.py -- identified trafficking cases, by country, from CTDC.

    python3 harvest_cases.py              # writes cases.json
    python3 harvest_cases.py --dry-run -v

WHY THIS EXISTS
---------------
The map showed a few dozen dots for a phenomenon the ILO, Walk Free and IOM put
at 49.6 million people. That gap is real and it needs explaining rather than
papering over, because the explanation is the single most important thing this
map can teach.

  * 49.6 million is a MODELLED PREVALENCE ESTIMATE, extrapolated from national
    surveys. It is not a list. Nobody has 49.6 million names, and no dataset on
    earth has 49.6 million locations.
  * What exists as records is DETECTION: people some authority or NGO actually
    identified and assisted. UNODC's global count of detected victims runs in
    the tens of thousands a year. The Counter-Trafficking Data Collaborative --
    the largest open individual-level dataset in the field -- holds roughly
    230,000 case records across 199 countries, accumulated since 2002.
  * The distance between 49.6 million and 230,000 is not this map being
    incomplete. It is the actual state of what is known, and it is the finding.

So: this pulls the CTDC case records and aggregates them to one record per
country of exploitation. That turns a few dozen dots into ~200, each carrying a
real count of identified people rather than an estimate.

WHY COUNTRY LEVEL AND NOT FINER
-------------------------------
CTDC's public datasets are k-anonymised or differentially private *by design*,
because these are records about living people who were trafficked and many of
whom are still at risk. The geography they carry is the country of exploitation.
Publishing anything finer would be both impossible from this data and wrong.
Every record this writes is marked imprecise and draws as a hollow ring.

DATA SOURCE
-----------
CTDC is a Drupal site; its datasets are exposed as CSV at /node/<id>/download,
linked from the dataset pages. This script finds the link rather than
hard-coding a node id, since those change between releases.
"""

import argparse
import csv
import io
import json
import os
import re
import ssl
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

PAGES = [
    "https://www.ctdatacollaborative.org/download-global-dataset",
    "https://www.ctdatacollaborative.org/dataset/global-synthetic-data-and-resources",
    "https://www.ctdatacollaborative.org/page/global-dataset",
]

# Column names CTDC has used across releases for country of exploitation.
COUNTRY_COLS = ["citizenship", "CountryOfExploitation", "countryOfExploitation",
                "country_of_exploitation", "Country of Exploitation",
                "ExploitCountry", "exploit_country"]
# Preference order: where the exploitation happened beats where they were from.
PREFER = ["countryofexploitation", "exploitcountry", "country_of_exploitation",
          "countryofexploitationiso", "citizenship"]

TYPE_COLS = ["typeOfExploitConcatenated", "majorityStatus", "typeOfLabourConcatenated",
             "isForcedLabour", "isSexualExploit"]



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
        if low.endswith((".csv", ".xlsx", ".json")) and any(p in low for p in patterns):
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


def fetch(url, timeout=60):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def find_csv(verbose=False):
    """Follow the dataset pages and pick up the first CSV download link."""
    seen = set()
    for page in PAGES:
        try:
            html = fetch(page).decode("utf-8", "replace")
        except Exception as ex:
            if verbose:
                print("  %-62s %s" % (page, str(ex)[:50]))
            continue
        cand = re.findall(r'href="([^"]*(?:/node/\d+/download|\.csv)[^"]*)"', html)
        for c in cand:
            u = c if c.startswith("http") else ("https://www.ctdatacollaborative.org" + c)
            if u in seen:
                continue
            seen.add(u)
            if verbose:
                print("  candidate:", u)
            try:
                raw = fetch(u)
            except Exception as ex:
                if verbose:
                    print("    fetch failed:", str(ex)[:50])
                continue
            head = raw[:400].decode("utf-8", "replace").lower()
            if "," in head and any(k.lower() in head for k in COUNTRY_COLS + ["year"]):
                print("  using:", u, "(%d bytes)" % len(raw))
                return raw
    return None


def pick_country_col(fields):
    low = {f.lower().replace(" ", "").replace("_", ""): f for f in fields}
    for p in PREFER:
        k = p.replace("_", "").replace(" ", "")
        if k in low:
            return low[k]
    for f in fields:
        if "country" in f.lower():
            return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="a CSV already downloaded by hand, when "
                                   "CTDC blocks the automated request")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min", type=int, default=1,
                    help="drop countries with fewer than this many records")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    fp = read_file(find_export(args.file, "ctdc", "synthetic", "victim"), "Download the Global Synthetic Dataset CSV from "
                              "ctdatacollaborative.org, save it into your repo folder, "
                              "cd there, and re-run.") if args.file else None
    if args.file and not fp:
        return 1
    if fp:
        with open(fp, "rb") as f:
            raw = f.read()
        print("using local file: %s (%d bytes)" % (fp, len(raw)))
    else:
        print("looking for the CTDC dataset CSV...")
        raw = find_csv(args.verbose)
    if not raw:
        print("\nCould not reach the CTDC dataset. Nothing written \u2014 the existing "
              "cases.json, if any, is left alone. CTDC blocks some automated "
              "requests; if this keeps failing, download the Global Synthetic "
              "Dataset by hand from ctdatacollaborative.org and re-run with "
              "--file <path>.")
        return 1

    text = raw.decode("utf-8", "replace")
    rdr = csv.DictReader(io.StringIO(text))
    fields = rdr.fieldnames or []
    col = pick_country_col(fields)
    if not col:
        print("no country column found. Columns were:", fields[:25])
        return 1
    print("country column: %r" % col)

    counts = Counter()
    slices = Counter()
    kinds = {}
    total = 0
    for row in rdr:
        total += 1
        c = (row.get(col) or "").strip()
        if not c or c in ("-99", "NA", "Unknown", ""):
            continue
        c = c.upper()[:3] if len(c) == 3 else c
        counts[c] += 1
        blob = " ".join(str(row.get(t, "")) for t in TYPE_COLS).lower()
        k = kinds.setdefault(c, Counter())
        lab = "forced labour" in blob or "labour" in blob or row.get("isForcedLabour") == "1"
        sex = "sexual" in blob or row.get("isSexualExploit") == "1"
        if lab:
            k["labour"] += 1
        if sex:
            k["sexual"] += 1
        if "minor" in blob:
            k["minor"] += 1

        kind = ("labour exploitation" if lab and not sex else
                "sexual exploitation" if sex and not lab else
                "both labour and sexual exploitation" if lab and sex else
                "exploitation type not recorded")
        yr = None
        for yc in ("yearOfRegistration", "Year", "year", "yearOfRegistrat"):
            v = row.get(yc)
            if v and str(v).strip().isdigit():
                yr = int(str(v).strip())
                break
        era = ("2020\u20132024" if yr and yr >= 2020 else
               "2015\u20132019" if yr and yr >= 2015 else
               "2010\u20132014" if yr and yr >= 2010 else
               "before 2010" if yr else "year not recorded")
        slices[(c, kind, era)] += 1

    print("rows read: %d | countries with records: %d" % (total, len(counts)))

    # Finer slices. One dot per country was the honest floor, not the ceiling:
    # the records carry exploitation type and year of registration as well as
    # country, so those are three real dimensions rather than one. What they do
    # NOT carry is any sub-national geography, so slicing further than this
    # would produce more dots at the same coordinates without adding anything.
    recs = []
    for (iso, kind, era), n in sorted(slices.items(), key=lambda kv: -kv[1]):
        if n < args.min or len(iso) != 3:
            continue
        recs.append({
            "name": "%s identified: %s, %s" % (format(n, ","), kind, era),
            "source": "ctdc",
            "type": "Identified cases \u2014 %s" % kind,
            "iso": iso,
            "state": iso,
            "impact": 5 if n >= 2000 else 4 if n >= 500 else 3 if n >= 50 else 2,
            "precise": False,
            "status": "Identified",
            "period": era,
            "url": "https://www.ctdatacollaborative.org/",
            "desc": (
                "%s individual case records from the Counter-Trafficking Data "
                "Collaborative where this was the country of exploitation, the "
                "recorded exploitation type was <b>%s</b>, and the person was "
                "identified in <b>%s</b>. Contributed by IOM, Polaris, A21, "
                "RecollectiV and the Portuguese observatory. "
                "<b>Detection, not prevalence.</b> These are people an organisation "
                "actually identified and assisted; a low number can mean little "
                "trafficking or no identification system, and the data cannot tell you "
                "which. Country level only \u2014 the records describe living people "
                "who were trafficked and carry no sub-national geography by design."
                % (format(n, ","), kind, era)),
        })

    for iso, n in counts.most_common():
        if n < args.min or len(iso) != 3:
            continue
        k = kinds.get(iso, Counter())
        parts = []
        if k.get("labour"):
            parts.append("%d recorded with labour exploitation" % k["labour"])
        if k.get("sexual"):
            parts.append("%d with sexual exploitation" % k["sexual"])
        if k.get("minor"):
            parts.append("%d who were children at the time" % k["minor"])
        breakdown = ("Of these, " + "; ".join(parts) + ".") if parts else ""
        recs.append({
            "name": "%s identified trafficking cases on record" % format(n, ","),
            "source": "ctdc",
            "type": "Identified cases (CTDC)",
            "iso": iso,
            "state": iso,
            "impact": 5 if n >= 5000 else 4 if n >= 1000 else 3 if n >= 100 else 2,
            "precise": False,
            "status": "Identified",
            "url": "https://www.ctdatacollaborative.org/",
            "desc": (
                "%s individual case records where this was the country of exploitation, "
                "from the Counter-Trafficking Data Collaborative \u2014 the largest open "
                "individual-level dataset in this field, contributed by IOM, Polaris, "
                "A21, RecollectiV and the Portuguese observatory. %s "
                "<b>Read this as detection, not prevalence.</b> These are people some "
                "organisation actually identified and assisted. A low number can mean "
                "little trafficking or no identification system, and the data cannot tell "
                "you which \u2014 countries with strong referral systems and active NGOs "
                "appear worse here than countries with neither. The records are "
                "de-identified and country-level by design, because they describe living "
                "people who were trafficked and many of whom are still at risk."
                % (format(n, ","), breakdown)).strip(),
        })

    print("records: %d (%d sliced by type and period, %d country totals)"
          % (len(recs), len(recs) - len(counts), len(counts)))
    if args.dry_run:
        for r in recs[:20]:
            print("  [%s] %s" % (r["iso"], r["name"]))
        return 0

    if not recs and os.path.exists(OUT) and not args.force:
        print("0 records and cases.json already exists \u2014 not overwriting.")
        return 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "source": "Counter-Trafficking Data Collaborative",
                   "note": ("Identified case counts by country of exploitation. "
                            "Detection, not prevalence. Country level only, by design."),
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
