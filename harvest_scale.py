#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_scale.py -- the two layers that are not detection.

    python3 harvest_scale.py --prevalence     # writes prevalence.json
    python3 harvest_scale.py --directory      # writes directory.json
    python3 harvest_scale.py --all -v

WHY PREVALENCE IS A SEPARATE LAYER FROM CASES
---------------------------------------------
Case records only exist where somebody was identified. Whole regions where
slavery is well documented to occur produce almost no case records, because
there is no inspectorate, no referral system, and no NGO able to operate. A map
built only on detection therefore shows the *response*, not the problem, and it
makes the countries with the best systems look worst.

Walk Free's Global Slavery Index estimates prevalence for 160 countries from
national surveys plus a vulnerability model, extrapolated against the ILO/Walk
Free/IOM regional estimates. It covers places with no case data at all. That is
exactly the gap, and it belongs on the map as its own layer with its own
caveats, never merged with the case counts.

These are ESTIMATES. Modelled, wide confidence intervals, and in the countries
where direct survey work is impossible they lean hardest on the model. Every
record says so.

ON THE DIRECTORY
----------------
This pulls the Global Modern Slavery Directory: roughly 2,600 organisations
across about 200 countries, run by Polaris. Pulling it was a deliberate choice
and it carries a real cost, so the cost is handled rather than ignored:

  * every entry is stamped with the date it was synced
  * every entry carries a link to its live GMSD record
  * the map shows a staleness warning when the sync is more than 90 days old
  * organisations open, close, move and lose funding, so a copy decays; re-run
    this on a schedule or the copy will send somebody to a dead number

Inclusion in the GMSD is not an endorsement by Polaris, and republishing it here
is not an endorsement by anyone either.
"""

import argparse
import io
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")



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


# ===================================================================== GMSD
# The directory front-end is a JS app. These are the endpoints it is most
# likely to be reading; each is tried in turn and the first that returns a
# recognisable provider list wins. If they all miss, --file takes an export.
GMSD_ENDPOINTS = [
    "https://globalmodernslavery.org/directory/data/providers.json",
    "https://globalmodernslavery.org/directory/providers.json",
    "https://globalmodernslavery.org/wp-json/wp/v2/provider?per_page=100",
    "https://globalmodernslavery.org/wp-json/gmsd/v1/providers",
]

SERVICE_TAGS = [
    (("hotline", "helpline", "crisis line"), "conserve:hotline"),
    (("shelter", "housing", "safe house", "accommodation"), "conserve:shelter"),
    (("legal", "attorney", "lawyer", "immigration"), "conserve:legalaid"),
    (("case management", "case work", "casework", "social service"), "organizing:help"),
    (("repatriation", "reintegration", "return"), "conserve:longterm"),
    (("medical", "health", "counsel", "mental"), "organizing:help"),
    (("law enforcement", "police", "prosecut"), "courts:criminal"),
    (("training", "awareness", "prevention", "advocacy"), "advocacy:watchdog"),
]


def gmsd_records(rows, synced):
    out = []
    for r in rows:
        name = r.get("name") or r.get("title") or r.get("organization") or r.get("org_name")
        if isinstance(name, dict):                      # WP REST shape
            name = name.get("rendered")
        if not name:
            continue
        iso = (r.get("country_code") or r.get("iso3") or r.get("countryCode") or "").upper()
        country = r.get("country") or r.get("country_name") or ""
        url = r.get("website") or r.get("url") or r.get("link") or ""
        blob = " ".join(str(v) for v in r.values() if isinstance(v, (str, int))).lower()

        tags = []
        for words, tag in SERVICE_TAGS:
            if any(w in blob for w in words) and tag not in tags:
                tags.append(tag)
        if not tags:
            tags = ["organizing:help"]

        phone = r.get("phone") or r.get("hotline") or ""
        desc = (r.get("description") or r.get("services") or "").strip()
        out.append({
            "name": str(name).strip()[:140],
            "url": url if str(url).startswith("http") else "https://globalmodernslavery.org/directory/",
            "iso": iso if len(iso) == 3 else "",
            "country": country,
            "phone": str(phone)[:60],
            "tags": tags,
            "kind": "institution",
            "voice": "interpretive",
            "skind": "ngo",
            "synced": synced,
            "desc": ((desc[:600] + " ") if desc else "") +
                    ("Listed in the Global Modern Slavery Directory, run by Polaris. "
                     "Synced %s \u2014 <b>confirm it is still operating before relying on it.</b> "
                     "Service organisations open, close, move and lose funding, and this is a "
                     "copy rather than the live record. Inclusion in the directory is not an "
                     "endorsement by Polaris, and republication here is not one by anyone else."
                     % synced),
        })
    return out


def harvest_directory(args):
    synced = datetime.now(timezone.utc).date().isoformat()
    rows = None
    fp = read_file(find_export(args.file, "gmsd", "directory", "provider"), "Save the GMSD export into data/ in your repo, "
                              "and re-run.") if args.file else None
    if args.file and not fp:
        return 1
    if fp:
        with open(fp, encoding="utf-8") as f:
            rows = json.load(f)
        print("using local export: %s" % fp)
    else:
        for ep in GMSD_ENDPOINTS:
            try:
                raw = fetch(ep)
            except Exception as ex:
                if args.verbose:
                    print("  %-64s %s" % (ep, str(ex)[:40]))
                continue
            try:
                j = json.loads(raw.decode("utf-8", "replace"))
            except Exception:
                if args.verbose:
                    print("  %-64s not JSON" % ep)
                continue
            cand = j if isinstance(j, list) else (
                j.get("providers") or j.get("data") or j.get("results") or [])
            if cand:
                print("  using: %s (%d rows)" % (ep, len(cand)))
                rows = cand
                break

    if rows is None:
        print("\nNo GMSD endpoint responded. The directory front-end is a JS app and "
              "its data path is not documented, so this may need updating \u2014 open "
              "globalmodernslavery.org/directory, watch the network tab for the "
              "request that returns the provider list, and add that URL to "
              "GMSD_ENDPOINTS. Or export it and pass --file. Nothing written.")
        return 1

    recs = gmsd_records(rows, synced)
    byiso = {}
    for r in recs:
        byiso.setdefault(r["iso"] or "??", []).append(r)
    print("providers: %d across %d countries" % (len(recs), len(byiso)))
    if args.dry_run:
        for iso, v in sorted(byiso.items(), key=lambda kv: -len(kv[1]))[:15]:
            print("  %-4s %d" % (iso, len(v)))
        return 0

    out = os.path.join(HERE, "directory.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"synced": synced,
                   "source": "Global Modern Slavery Directory (Polaris)",
                   "note": ("A copy, not the live record. Re-run on a schedule; "
                            "entries decay as organisations close or move."),
                   "providers": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", out, "-", os.path.getsize(out), "bytes")
    return 0


# =============================================================== PREVALENCE
GSI_PAGES = [
    "https://www.walkfree.org/global-slavery-index/downloads/",
    "https://www.walkfree.org/global-slavery-index/",
]


def harvest_prevalence(args):
    """Find and parse Walk Free's country-level data file."""
    fp = read_file(find_export(args.file, "gsi", "slavery-index", "slavery_index", "walkfree", "prevalence"), "Download the Global Slavery Index country data from "
                              "walkfree.org/global-slavery-index/downloads, save it into "
                              "your repo folder, cd there, and re-run.") if args.file else None
    if args.file and not fp:
        return 1
    if fp:
        raw = open(fp, "rb").read()
        print("using local file: %s" % fp)
    else:
        raw = None
        for page in GSI_PAGES:
            try:
                html = fetch(page).decode("utf-8", "replace")
            except Exception as ex:
                if args.verbose:
                    print("  %-58s %s" % (page, str(ex)[:40]))
                continue
            links = re.findall(r'href="([^"]+\.(?:xlsx|csv))"', html)
            for l in links:
                u = l if l.startswith("http") else ("https://www.walkfree.org" + l)
                if not any(k in u.lower() for k in ("data", "prevalence", "index", "country")):
                    continue
                try:
                    raw = fetch(u)
                    print("  using:", u, "(%d bytes)" % len(raw))
                    break
                except Exception:
                    continue
            if raw:
                break

    if not raw:
        print("\nCould not retrieve the Global Slavery Index country data. It is "
              "published as a spreadsheet on the downloads page rather than as an "
              "API, and the filename changes between editions. Download it by hand "
              "from walkfree.org/global-slavery-index/downloads and re-run with "
              "--file. Nothing written.")
        return 1

    # xlsx needs openpyxl; csv does not. Handle both, complain clearly.
    rows = []
    if raw[:2] == b"PK":
        try:
            import openpyxl
        except ImportError:
            print("\nThat file is a spreadsheet and openpyxl is not installed.\n"
                  "    pip3 install openpyxl\nThen re-run.")
            return 1
        wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
        for ws in wb.worksheets:
            data = list(ws.values)
            if not data or len(data) < 3:
                continue
            hdr = None
            for i, r in enumerate(data[:8]):
                joined = " ".join(str(x or "").lower() for x in r)
                if "country" in joined and ("prevalence" in joined or "estimated" in joined):
                    hdr = i
                    break
            if hdr is None:
                continue
            cols = [str(x or "").strip() for x in data[hdr]]
            for r in data[hdr + 1:]:
                rows.append(dict(zip(cols, r)))
            if rows:
                break
    else:
        import csv as _csv
        rows = list(_csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))

    def col(d_, *keys):
        for k in d_:
            kl = str(k).lower()
            if any(x in kl for x in keys):
                return d_[k]
        return None

    recs = []
    for r in rows:
        country = col(r, "country")
        est = col(r, "estimated number", "population in modern slavery", "absolute")
        per1k = col(r, "per 1,000", "per 1000", "prevalence")
        if not country or (est is None and per1k is None):
            continue
        country = str(country).strip()
        if not country or country.lower() in ("nan", "none", "total"):
            continue
        try:
            n = int(float(str(est).replace(",", ""))) if est is not None else None
        except Exception:
            n = None
        try:
            p = float(str(per1k).replace(",", "")) if per1k is not None else None
        except Exception:
            p = None
        recs.append({
            "name": (("%s people estimated in modern slavery" % format(n, ",")) if n
                     else ("%.1f per 1,000 estimated in modern slavery" % p)),
            "source": "gsi",
            "type": "Prevalence estimate",
            "state": country,
            "country_name": country,
            "impact": 5 if (p or 0) >= 10 else 4 if (p or 0) >= 5 else 3 if (p or 0) >= 2 else 2,
            "precise": False,
            "status": "Estimated",
            "url": "https://www.walkfree.org/global-slavery-index/",
            "desc": (
                "Walk Free's Global Slavery Index estimate for this country"
                + ((", %.1f people per 1,000" % p) if p else "") + ". "
                "<b>This is a modelled estimate, not a count.</b> It is built from national "
                "surveys plus a vulnerability model, extrapolated against the ILO / Walk Free "
                "/ IOM regional estimates, and the confidence intervals are wide. In countries "
                "where survey work is impossible \u2014 active conflict, closed states \u2014 it "
                "leans hardest on the model and should be treated most cautiously. "
                "<b>It is here precisely because case records are not enough:</b> whole regions "
                "where this is well documented produce almost no case data, because there is no "
                "inspectorate, no referral system and no NGO able to operate. A map built only "
                "on detection shows the response, not the problem."),
        })

    print("prevalence records: %d" % len(recs))
    if args.dry_run:
        for r in recs[:15]:
            print("  %-28s %s" % (r["state"][:28], r["name"]))
        return 0

    out = os.path.join(HERE, "prevalence.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "source": "Walk Free, Global Slavery Index",
                   "note": "Modelled prevalence estimates, not counts. Country level.",
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", out, "-", os.path.getsize(out), "bytes")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prevalence", action="store_true")
    ap.add_argument("--directory", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not (a.prevalence or a.directory or a.all):
        ap.error("choose --prevalence, --directory or --all")
    rc = 0
    if a.prevalence or a.all:
        print("=== prevalence (Walk Free GSI) ===")
        rc |= harvest_prevalence(a)
    if a.directory or a.all:
        print("=== directory (GMSD) ===")
        rc |= harvest_directory(a)
    return rc


if __name__ == "__main__":
    sys.exit(main())
