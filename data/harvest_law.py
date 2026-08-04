#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_law.py -- what each country is already legally obliged to do.

    python3 harvest_law.py
    python3 harvest_law.py --dry-run -v

Writes law.json.

WHY THIS LAYER
--------------
Every other layer here describes what is happening or what was found. This one
describes what a state has already promised, and it changes what a user can ask
for.

"Please do something about this" is a request. "Your country ratified Convention
29 in 1957 and Protocol 29 in 2019, which obliges it to provide victims with
access to remedies including compensation irrespective of their presence or
legal status in the territory" is a citation. The second is the one that gets an
answer from a ministry, and it is the difference between a complaint and a
claim.

It is also the layer that makes the map's own gaps legible. A country with no
services in the directory and full ratification of the forced labour
instruments is a different problem from a country with neither -- the first has
made commitments it is not meeting, the second has not made them. Those need
different asks of different people.

THE SIX INSTRUMENTS
-------------------
  C029  Forced Labour Convention, 1930
  P029  Protocol of 2014 to C029 -- the remedies and compensation obligations
  C105  Abolition of Forced Labour Convention, 1957
  C138  Minimum Age Convention, 1973
  C182  Worst Forms of Child Labour Convention, 1999
  C188  Work in Fishing Convention, 2007 -- the one that matters at sea

C138 and C182 are near-universal, which is itself worth knowing: on child
labour, almost no state can say it has not undertaken the obligation. C188 is
not, and the gap between the fleets that fish and the states that have ratified
it is one of the more legible failures in this whole field.

RATIFICATION IS NOT COMPLIANCE
------------------------------
It is a promise, not a practice, and several of the worst records on this map
belong to states that ratified decades ago. Every record says so. What
ratification gives you is standing: a supervisory body that accepts complaints,
a reporting cycle, and an obligation the government has already accepted in
writing and cannot argue was never agreed.
"""

import argparse
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
OUT = os.path.join(HERE, "law.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

CONVENTIONS = {
    "C029": ("Forced Labour Convention, 1930",
             "Obliges the state to suppress forced or compulsory labour in all its "
             "forms and to make the exaction of it punishable as a penal offence, "
             "with penalties that are really adequate and strictly enforced."),
    "P029": ("Protocol of 2014 to the Forced Labour Convention",
             "The remedies instrument. Obliges the state to provide victims with "
             "access to appropriate and effective remedies including compensation, "
             "<b>irrespective of their presence or legal status in the territory</b> "
             "\u2014 which is the sentence to quote when a worker without papers is "
             "told their status disqualifies them."),
    "C105": ("Abolition of Forced Labour Convention, 1957",
             "Prohibits forced labour as political coercion, as a method of "
             "mobilising labour for economic development, as labour discipline, as "
             "punishment for strikes, and as racial or other discrimination."),
    "C138": ("Minimum Age Convention, 1973",
             "Requires a national minimum age for admission to employment, not less "
             "than the age of completing compulsory schooling."),
    "C182": ("Worst Forms of Child Labour Convention, 1999",
             "Requires immediate and effective measures to secure the prohibition and "
             "elimination of the worst forms of child labour as a matter of urgency, "
             "including slavery, debt bondage, trafficking and hazardous work."),
    "C188": ("Work in Fishing Convention, 2007",
             "The instrument that matters at sea: written work agreements, minimum "
             "age, hours of rest, repatriation, medical care and social security for "
             "fishers \u2014 and port state inspection powers over foreign vessels."),
}

NORMLEX = ("https://normlex.ilo.org/dyn/normlex/en/f?p=NORMLEXPUB:11300:0::NO::"
           "P11300_INSTRUMENT_ID:%s")
NORMLEX_IDS = {"C029": "312174", "P029": "3174672", "C105": "312250",
               "C138": "312283", "C182": "312327", "C188": "312333"}

RATIFICATION_CAVEAT = (
    " <b>Ratification is a promise, not a practice.</b> Several of the worst records "
    "on this map belong to states that ratified decades ago. What it gives you is "
    "standing: a supervisory body that accepts complaints, a reporting cycle, and an "
    "obligation the government has already accepted in writing and cannot argue was "
    "never agreed.")


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
        if low.endswith((".csv", ".json")) and any(p in low for p in patterns):
            p = os.path.join(DATA_DIR, f)
            print("  found export in data/: %s" % f)
            return p
    return None


def parse_normlex(html, code):
    """NORMLEX renders ratifications as an HTML table: country, date, status.
    It is a server-rendered page rather than an API, so this reads the table."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I)
    out = {}
    for r in rows:
        cells = [re.sub(r"<[^>]+>", " ", c) for c in
                 re.findall(r"<td[^>]*>(.*?)</td>", r, re.S | re.I)]
        cells = [" ".join(c.split()) for c in cells]
        if len(cells) < 2:
            continue
        country = cells[0]
        date = next((c for c in cells[1:] if re.search(r"\d{2}\s+\w+\s+\d{4}|\d{4}", c)), "")
        if not country or not date or len(country) > 60:
            continue
        if country.lower() in ("country", "ratification date"):
            continue
        out[country] = re.search(r"\d{4}", date).group(0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    # by country -> {code: year}
    rat = {}

    src = find_export("normlex", "ratification", "ilo")
    if src:
        try:
            j = json.loads(open(src, encoding="utf-8").read())
            rat = j if isinstance(j, dict) else {}
            print("  loaded %d countries from the committed export" % len(rat))
        except Exception as ex:
            print("  could not read %s: %s" % (os.path.basename(src), str(ex)[:50]))

    if not rat:
        for code, iid in NORMLEX_IDS.items():
            try:
                html = fetch(NORMLEX % iid).decode("utf-8", "replace")
            except Exception as ex:
                print("  %-6s %s" % (code, str(ex)[:56]))
                continue
            got = parse_normlex(html, code)
            print("  %-6s %d ratifications" % (code, len(got)))
            for country, year in got.items():
                rat.setdefault(country, {})[code] = year

    if not rat:
        print("\n  NORMLEX is a server-rendered search application rather than an API, "
              "and it refuses automated requests from some networks. If this keeps "
              "failing, the ratification tables are one page per convention at "
              "normlex.ilo.org \u2014 save them as a single JSON of "
              "{country: {code: year}} and commit it to data/ with 'normlex' in the "
              "filename.")
        print("  Conventions to cover: " + ", ".join(CONVENTIONS))
        return 1

    out = []
    for country, codes in sorted(rat.items()):
        if not codes:
            continue
        have = sorted(codes)
        missing = [c for c in CONVENTIONS if c not in codes]
        lines = []
        for c in have:
            title, oblig = CONVENTIONS[c]
            lines.append("<b>%s</b> (%s), ratified %s. %s" % (c, title, codes[c], oblig))
        desc = ("Instruments this state has ratified:<br>" + "<br>".join(lines))
        if missing:
            desc += ("<br><br><b>Not ratified:</b> "
                     + ", ".join("%s (%s)" % (m, CONVENTIONS[m][0]) for m in missing)
                     + ". A state that has not ratified has not undertaken the "
                       "obligation \u2014 which is a different ask, of different people, "
                       "from a state that has and is not meeting it.")
        desc += RATIFICATION_CAVEAT
        out.append({
            "name": "%s \u2014 %d of %d instruments ratified" % (country, len(have),
                                                                 len(CONVENTIONS)),
            "source": "normlex",
            "type": "ILO ratifications",
            "country_name": country,
            "state": country,
            "precise": False,
            "impact": 2 if len(have) >= 5 else 3,
            "status": "%d/%d ratified" % (len(have), len(CONVENTIONS)),
            "url": "https://normlex.ilo.org/",
            "desc": desc,
        })

    print("total: %d countries" % len(out))
    if a.dry_run:
        for r in out[:15]:
            print("  %-40s %s" % (r["state"][:40], r["status"]))
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "source": "ILO NORMLEX",
                   "note": ("What each state has already promised. Ratification is a "
                            "promise, not a practice."),
                   "projects": out}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
