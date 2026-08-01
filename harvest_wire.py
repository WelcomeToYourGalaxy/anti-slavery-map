#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_wire.py -- build wire.json for the Live Global Slavery & Child Labour Map.

Reads the feed list straight out of index.html (so there is one list, not two
that drift apart), fetches each feed, filters to the subject, tags each item
with a country and where possible a region, and writes wire.json next to the
map.

    python3 harvest_wire.py                    # write wire.json
    python3 harvest_wire.py --days 45          # widen the window
    python3 harvest_wire.py --dry-run -v       # show what would ship

Run it on a schedule. A GitHub Actions workflow doing this every six hours is
at the bottom of this file, commented out.

WHY THE TAGGING HAPPENS HERE, NOT IN THE BROWSER
------------------------------------------------
The sibling map tags country and region client-side, by matching region names
against headline text after the feed loads. That is where its all-zeros
subregion filter came from: the matcher only sees names for countries that
already have entries in trackerdata.json, so most items never get a region and
the filter has nothing to group. Doing it at harvest time means the geography
is computed once, against the full country list, and shipped as data.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not geocode to a place. A headline saying "raid on a farm outside
Almeria" could be resolved to a point by a geocoder, and should not be: the
workers are still there, the report is unverified, and the map's convention is
that anything without coordinates in the source is drawn as a centroid ring.
Country and region are as far as this goes.
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")
OUT = os.path.join(HERE, "wire.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

# --------------------------------------------------------------- subject gate
# An item must carry at least one of these to be about this subject at all.
ON = [
    "forced labour", "forced labor", "modern slavery", "human trafficking",
    "labour trafficking", "labor trafficking", "trafficked", "trafficking ring",
    "child labour", "child labor", "children working", "underage worker",
    "debt bondage", "bonded labour", "bonded labor", "indentured", "servitude",
    "slave labour", "slave labor", "recruitment fee", "labour broker",
    "labor broker", "gangmaster", "passport confiscat", "withheld passport",
    "wage theft", "unpaid wages", "kafala", "sponsorship system",
    "withhold release order", "uflpa", "forced labour regulation",
    "domestic servitude", "forced marriage", "worst forms of child labour",
    # Non-English. Several feeds are Google News queries that return items in
    # the local language of the story; an English-only gate silently drops the
    # coverage nearest the event, which is usually the best coverage there is.
    "trabajo forzoso", "trabajo forzado", "trata de personas", "trabajo infantil",
    "esclavitud moderna", "servidumbre",
    "trabalho for\u00e7ado", "trabalho escravo", "tr\u00e1fico de pessoas",
    "trabalho infantil", "escravid\u00e3o",
    "travail forc\u00e9", "traite des \u00eatres humains", "travail des enfants",
    "esclavage moderne",
    "zwangsarbeit", "menschenhandel", "kinderarbeit", "moderne sklaverei",
    "lavoro forzato", "tratta di esseri umani", "lavoro minorile", "caporalato",
]

# Killed even when a term above matches. Each of these floods a feed keyed on
# "labour" and "child" and none of them is this subject.
OFF = [
    # metaphor
    "wage slave", "slave to fashion", "slave to the algorithm", "slaves to",
    "fashion slave", "a slave to", "slave away",
    # the historical institution, which has its own literature and is not this
    "transatlantic slave", "slave trade history", "abolition of slavery anniversary",
    "slave ship wreck", "plantation museum", "civil war", "confederate",
    # UK party politics
    "labour party", "labour leader", "labour mp", "labour government",
    "shadow cabinet", "labour manifesto", "labour councillor", "keir starmer",
    # childbirth
    "went into labour", "labour ward", "induced labour", "labour pains",
    "in labour with", "labour and delivery",
    # childcare policy
    "child benefit", "childcare funding", "child tax credit", "child care costs",
    # noise
    "horoscope", "box office", "recipe", "match report", "transfer window",
    "share price", "quarterly earnings", "webinar", "register now",
    "call for papers", "book launch", "save the date",
]

LANG_HINT = {
    "es": ["trabajo forzoso", "trata de personas", "trabajo infantil", "esclavitud"],
    "pt": ["trabalho forçado", "trabalho escravo", "tráfico de pessoas", "trabalho infantil"],
    "fr": ["travail forcé", "traite des êtres humains", "travail des enfants", "esclavage"],
    "de": ["zwangsarbeit", "menschenhandel", "kinderarbeit"],
    "it": ["lavoro forzato", "tratta di esseri umani", "lavoro minorile", "caporalato"],
}


# --------------------------------------------------------------- feed list
def feeds_from_index(path):
    """Pull WIRE_FEEDS out of index.html so there is one canonical list."""
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    m = re.search(r"const WIRE_FEEDS\s*=\s*(\[.*?\]);", doc, re.S)
    if not m:
        sys.exit("WIRE_FEEDS not found in " + path)
    return re.findall(r'\["([^"]+)",\s*"(https?://[^"]+)"\]', m.group(1))


def countries_from_index(path):
    """ISO3 -> display name, and ISO2 -> ISO3, both already in the map."""
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    a2to3 = {}
    m = re.search(r"var _WIRE_A2TO3=(\{.*?\});", doc, re.S)
    if m:
        a2to3 = json.loads(m.group(1))
    names = {}
    m = re.search(r"var _wireISONAME=\{(.*?)\};", doc, re.S)
    if m:
        for a2, nm in re.findall(r"(\w{2}):'([^']+)'", m.group(1)):
            names[a2to3.get(a2, a2)] = nm
    # Local-language country names, so a Portuguese or Italian headline about
    # "Brasil" or "Italia" is not left untagged. ENDONYM is keyed by the English
    # name, which is how it joins back to the ISO code.
    alias = {}
    m = re.search(r"const ENDONYM=(\{.*?\});", doc, re.S)
    if m:
        try:
            endo = json.loads(m.group(1))
            back = {v: k for k, v in names.items()}
            for en, local in endo.items():
                iso = back.get(en)
                if not iso:
                    continue
                for form in re.split(r"[/(]", local):
                    form = form.strip().strip(")").strip()
                    # drop a parenthesised romanisation, keep the script form
                    if len(form) >= 4 and not form.isdigit():
                        alias.setdefault(iso, []).append(form)
        except Exception:
            pass
    # A few high-traffic forms the endonym table does not carry.
    for iso, forms in {"BRA": ["Brasil"], "ITA": ["Italia"], "ESP": ["Espana"],
                       "MEX": ["M\u00e9xico"], "DEU": ["Deutschland"],
                       "CIV": ["Cote d'Ivoire", "Ivory Coast"],
                       "USA": ["U.S.", "United States of America"],
                       "GBR": ["Britain", "UK"], "ARE": ["UAE"],
                       "KOR": ["South Korea"], "PRK": ["North Korea"],
                       "COD": ["DR Congo", "DRC"]}.items():
        alias.setdefault(iso, []).extend(forms)
    return names, a2to3, alias


def regions_from_trackerdata(path):
    """ISO3 -> [region names], for the subregion filter."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {iso: list((c.get("sub") or {}).keys()) for iso, c in data.items()}


# --------------------------------------------------------------- fetching
def fetch(url, timeout):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", s).strip()


def parse_feed(raw, outlet):
    """RSS 2.0 and Atom, without a third-party dependency."""
    out = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return out
    ns = {"a": "http://www.w3.org/2005/Atom"}
    nodes = root.findall(".//item") or root.findall(".//a:entry", ns)
    for n in nodes:
        def get(tag, atom=None):
            el = n.find(tag)
            if el is None and atom is not None:
                el = n.find(atom, ns)
            return (el.text or "") if el is not None else ""

        title = strip_html(get("title", "a:title"))
        if not title:
            continue
        link = get("link", None)
        if not link:
            le = n.find("a:link", ns)
            link = le.get("href", "") if le is not None else ""
        desc = strip_html(get("description", "a:summary") or get("content:encoded"))
        date = (get("pubDate") or get("published", "a:published")
                or get("updated", "a:updated"))
        ts = None
        for parser in (parsedate_to_datetime,
                       lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))):
            try:
                ts = parser(date.strip())
                break
            except Exception:
                continue
        if ts and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        out.append({"title": title, "link": link, "snippet": desc[:400],
                    "date": ts.isoformat() if ts else "", "name": outlet})
    return out


# --------------------------------------------------------------- tagging
def on_topic(text, title=None):
    """A subject phrase in the TITLE, or two different ones anywhere.

    A single subject phrase buried in a body paragraph is how a story about
    something else ends up in the feed: wire services drop 'human trafficking'
    into the last line of a crime round-up, and a one-hit gate takes it. The
    map's own gate now works the same way, so the two agree."""
    t = " " + text.lower() + " "
    if any(x in t for x in OFF):
        return False
    if title:
        h = " " + title.lower() + " "
        if any(x in h for x in ON):
            return True
    return len({x for x in ON if x in t}) >= 2


def guess_lang(text):
    t = text.lower()
    for code, words in LANG_HINT.items():
        if any(w in t for w in words):
            return code
    return "en"


def fold(s):
    """Lowercase, strip accents, reduce to letters and digits. Feeds spell the
    same place 'Para', 'Pará' and 'PARA' in the same hour, and a matcher that
    cares about the difference finds none of them."""
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " " + re.sub(r"[^a-z0-9]+", " ", s).strip() + " "


_REGION_INDEX = None


def region_index(regions):
    """Region name -> ISO3, keeping only names distinctive enough to imply a
    country on their own. Drops anything short, and anything claimed by more
    than one country, so 'Georgia' the US state never resolves a headline about
    Georgia the country."""
    global _REGION_INDEX
    if _REGION_INDEX is not None:
        return _REGION_INDEX
    seen, dupes = {}, set()
    for iso, names in regions.items():
        for r in names:
            k = fold(r).strip()
            if len(k) < 6 or " " not in k and len(k) < 8:
                continue
            if k in seen and seen[k] != iso:
                dupes.add(k)
            seen[k] = iso
    _REGION_INDEX = {k: v for k, v in seen.items() if k not in dupes}
    return _REGION_INDEX


# Demonyms and adjectival forms. A third of the harvest carried no country
# because headlines say "Indian workers", "Brazilian prosecutors" or "Chinese
# supplier" far more often than they say the country's name -- and an untagged
# item cannot become a dot, so this directly limits what the map can show.
DEMONYM = {
    "indian": "IND", "pakistani": "PAK", "bangladeshi": "BGD", "nepali": "NPL",
    "nepalese": "NPL", "sri lankan": "LKA", "afghan": "AFG", "burmese": "MMR",
    "myanmar": "MMR", "cambodian": "KHM", "vietnamese": "VNM", "thai": "THA",
    "lao": "LAO", "laotian": "LAO", "filipino": "PHL", "filipina": "PHL",
    "indonesian": "IDN", "malaysian": "MYS", "singaporean": "SGP",
    "chinese": "CHN", "uyghur": "CHN", "uighur": "CHN", "taiwanese": "TWN",
    "japanese": "JPN", "korean": "KOR", "mongolian": "MNG",
    "brazilian": "BRA", "mexican": "MEX", "argentine": "ARG",
    "argentinian": "ARG", "chilean": "CHL", "peruvian": "PER",
    "colombian": "COL", "bolivian": "BOL", "venezuelan": "VEN",
    "ecuadorian": "ECU", "paraguayan": "PRY", "haitian": "HTI",
    "guatemalan": "GTM", "honduran": "HND", "salvadoran": "SLV",
    "nigerian": "NGA", "ghanaian": "GHA", "ivorian": "CIV", "kenyan": "KEN",
    "ethiopian": "ETH", "ugandan": "UGA", "tanzanian": "TZA",
    "zimbabwean": "ZWE", "zambian": "ZMB", "malawian": "MWI",
    "mozambican": "MOZ", "senegalese": "SEN", "malian": "MLI",
    "sudanese": "SDN", "eritrean": "ERI", "somali": "SOM",
    "south african": "ZAF", "congolese": "COD", "moroccan": "MAR",
    "egyptian": "EGY", "tunisian": "TUN", "libyan": "LBY",
    "mauritanian": "MRT", "cameroonian": "CMR",
    "qatari": "QAT", "emirati": "ARE", "saudi": "SAU", "kuwaiti": "KWT",
    "bahraini": "BHR", "omani": "OMN", "jordanian": "JOR",
    "lebanese": "LBN", "syrian": "SYR", "iraqi": "IRQ", "iranian": "IRN",
    "yemeni": "YEM", "israeli": "ISR", "turkish": "TUR",
    "british": "GBR", "english": "GBR", "scottish": "GBR", "welsh": "GBR",
    "irish": "IRL", "french": "FRA", "german": "DEU", "italian": "ITA",
    "spanish": "ESP", "portuguese": "PRT", "dutch": "NLD", "belgian": "BEL",
    "polish": "POL", "romanian": "ROU", "bulgarian": "BGR",
    "hungarian": "HUN", "czech": "CZE", "slovak": "SVK", "greek": "GRC",
    "swedish": "SWE", "norwegian": "NOR", "danish": "DNK", "finnish": "FIN",
    "austrian": "AUT", "swiss": "CHE", "ukrainian": "UKR", "russian": "RUS",
    "belarusian": "BLR", "moldovan": "MDA", "albanian": "ALB",
    "serbian": "SRB", "croatian": "HRV", "lithuanian": "LTU",
    "latvian": "LVA", "estonian": "EST", "uzbek": "UZB", "turkmen": "TKM",
    "kazakh": "KAZ", "kyrgyz": "KGZ", "tajik": "TJK",
    "american": "USA", "canadian": "CAN", "australian": "AUS",
    "new zealand": "NZL",
}


def tag_geo(item, names, regions, alias=None):
    """Country first, then region within it. Longest name wins, so
    'South Africa' is not eaten by 'Africa' and 'Guinea-Bissau' not by 'Guinea'.
    If no country matched but a distinctive region name did, the region implies
    the country -- a headline about a rescue in Rio Grande do Sul rarely says
    'Brazil' as well."""
    t = fold(item["title"] + " " + item["snippet"])
    # Geographic features carry country names and demonyms without being about
    # the country: "Indian Ocean fishing fleet" is not an Indian story and
    # "South China Sea" is not a Chinese one. Mistagging puts a dot in the wrong
    # place, which is worse than no dot, so these are removed before any match.
    for _ph in ("indian ocean", "south china sea", "east china sea",
                "persian gulf", "arabian sea", "korean peninsula",
                "english channel", "irish sea", "north american",
                "south american", "latin american", "african union",
                "european union", "asian development bank"):
        t = t.replace(" " + _ph + " ", " ")
    best, best_len = None, 0
    forms = {}
    for iso, nm in names.items():
        forms.setdefault(iso, []).append(nm)
    for iso, extra in (alias or {}).items():
        forms.setdefault(iso, []).extend(extra)
    for iso, nms in forms.items():
        for nm in nms:
            key = fold(nm)
            if key.strip() and key in t and len(nm) > best_len:
                best, best_len = iso, len(nm)

    # demonym, when the country name itself was not used.
    # Geographic features carry demonyms without being about the country:
    # "Indian Ocean fishing fleet" is not an Indian story, and mistagging it
    # would put a dot in the wrong place, which is worse than no dot.
    if not best:
        hit_len = 0
        for word, iso in DEMONYM.items():
            if (" " + word + " ") in t and len(word) > hit_len:
                best, hit_len = iso, len(word)

    # region implies country, when neither the name nor a demonym appeared
    if not best:
        ridx = region_index(regions)
        hit_len = 0
        for k, iso in ridx.items():
            if (" " + k + " ") in t and len(k) > hit_len:
                best, hit_len = iso, len(k)

    if best:
        item["iso"] = best
        best_r, best_rl = None, 0
        for r in regions.get(best, []):
            if fold(r) in t and len(r) > best_rl:
                best_r, best_rl = r, len(r)
        if best_r:
            item["region"] = best_r
    return item


def significance(item):
    """A crude 0-10 used only to order the feed; the map re-scores anyway."""
    t = (item["title"] + " " + item["snippet"]).lower()
    v = 0
    for w, n in [("convicted", 3), ("sentenced", 3), ("rescued", 3), ("freed", 3),
                 ("raid", 2), ("charged", 2), ("died", 3), ("killed", 3),
                 ("children", 2), ("import ban", 3), ("withhold release order", 3),
                 ("hundreds", 2), ("thousands", 3), ("compensation", 2)]:
        if w in t:
            v += n
    return min(10, v)


# --------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max", type=int, default=1200)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="write even when nothing was harvested")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    feeds = feeds_from_index(INDEX)
    names, _, alias = countries_from_index(INDEX)
    regions = regions_from_trackerdata(os.path.join(HERE, "trackerdata.json"))
    print("%d feeds, %d country names, %d countries with regions"
          % (len(feeds), len(names), sum(1 for v in regions.values() if v)))

    raw_items, failed = [], []

    def one(f):
        outlet, url = f
        try:
            return outlet, parse_feed(fetch(url, args.timeout), outlet), None
        except Exception as ex:
            return outlet, [], str(ex)[:80]

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for outlet, items, err in pool.map(one, feeds):
            if err:
                failed.append((outlet, err))
            raw_items.extend(items)
            if args.verbose:
                print("  %-42s %s" % (outlet, err or ("%d items" % len(items))))

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    kept, seen = [], set()
    for it in raw_items:
        blob = it["title"] + " " + it["snippet"]
        if not on_topic(blob, it["title"]):
            continue
        key = re.sub(r"[^a-z0-9]", "", it["title"].lower())[:70]
        if key in seen:
            continue
        seen.add(key)
        if it["date"]:
            try:
                if datetime.fromisoformat(it["date"]) < cutoff:
                    continue
            except Exception:
                pass
        it["lang"] = guess_lang(blob)
        it["sig"] = significance(it)
        kept.append(tag_geo(it, names, regions, alias))

    kept.sort(key=lambda x: (x.get("date") or ""), reverse=True)
    kept = kept[:args.max]

    withiso = sum(1 for x in kept if x.get("iso"))
    withreg = sum(1 for x in kept if x.get("region"))
    print("\n%d raw -> %d on-topic, %d with a country (%d%%), %d with a region"
          % (len(raw_items), len(kept), withiso,
             round(100 * withiso / max(1, len(kept))), withreg))
    if failed:
        print("failed feeds:")
        for o, e in failed:
            print("  %-42s %s" % (o, e))

    if args.dry_run:
        for x in kept[:15]:
            print("  [%s|%s] %s" % (x.get("iso", "--"), x.get("region", ""), x["title"][:88]))
        return 0

    # An empty harvest is almost always an outage, a firewall or a proxy -- not
    # a quiet news month. Writing [] over a good file would blank the live layer
    # until the next successful run, and on a six-hourly schedule that is a
    # silent regression nobody notices. Refuse, unless told otherwise.
    if not kept:
        have = 0
        if os.path.exists(OUT):
            try:
                with open(OUT, encoding="utf-8") as f:
                    have = len(json.load(f) or [])
            except Exception:
                have = 0
        if have and not args.force:
            print("\nNOT WRITING: 0 items harvested, and %s already holds %d. "
                  "Every feed failed, which means the network refused them, not "
                  "that nothing happened. The existing file is left in place. "
                  "Use --force to overwrite it anyway." % (os.path.basename(OUT), have))
            return 1
        if not have:
            print("\n0 items harvested and no existing file to preserve. Writing "
                  "nothing rather than an empty file: the map falls back to "
                  "pulling feeds live in the browser, which is better than a "
                  "wire.json that says the world is quiet.")
            return 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


# ---------------------------------------------------------------------------
# .github/workflows/wire.yml
# ---------------------------------------------------------------------------
# name: harvest wire
# on:
#   schedule: [{cron: "0 */6 * * *"}]
#   workflow_dispatch:
# permissions: {contents: write}
# jobs:
#   harvest:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: python3 harvest_wire.py --days 30
#       - run: |
#           git config user.name  "wire-bot"
#           git config user.email "wire-bot@users.noreply.github.com"
#           git add wire.json
#           git diff --staged --quiet || git commit -m "wire: $(date -u +%F\ %H:%M)"
#           git push
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
