#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_bulk.py -- the remaining large open datasets.

    python3 harvest_bulk.py --brazil       # municipality-level rescue operations
    python3 harvest_bulk.py --glotip       # UNODC detected victims & convictions
    python3 harvest_bulk.py --iuu          # IUU-listed fishing vessels
    python3 harvest_bulk.py --gfw --token X  # Global Fishing Watch vessels
    python3 harvest_bulk.py --all -v

Writes bulk.json, merged into the same dot layer as everything else.

WHY BRAZIL IS FIRST
-------------------
The Observatorio Digital do Trabalho Escravo, run by Brazil's Labour
Prosecution Service with the ILO, publishes rescue operations at MUNICIPALITY
level: 60,251 people found in conditions analogous to slavery between 1995 and
2022, located to the town. Nothing else in this field comes close as
sub-national enforcement data -- it is not modelled, not estimated, and not
aggregated to the country. It is a state saying: we went here, and we found this
many people.

Municipality names are resolved to coordinates through IBGE's public
localidades API, so no coordinate table is invented or maintained here.

WHAT EACH LAYER IS
------------------
  brazil  Enforcement outcome. People actually removed by inspectors. The one
          layer on this map that records a rescue rather than a risk.
  glotip  Detection. Victims detected and traffickers convicted, as reported by
          states to UNODC. Counts the response, not the phenomenon -- a country
          reporting few detections may have little trafficking or no
          identification system, and the data cannot tell you which.
  iuu     Vessels listed for illegal, unreported and unregulated fishing by the
          regional fisheries bodies. Not a forced-labour finding, but IUU
          operation and forced labour at sea are strongly correlated in the
          documented cases, and a listed vessel is a named, flagged, actionable
          entity.
  gfw     Vessel behaviour: long voyages without port calls, transhipment at
          sea, transponder gaps. Indicators, not findings.
"""

import argparse
import csv
import io
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bulk.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

IBGE_MUN = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

BR_PAGES = [
    "https://observatorioescravo.mpt.mp.br/",
    "https://smartlabbr.org/trabalhoescravo",
]

GLOTIP_PAGES = [
    "https://dataunodc.un.org/dp-trafficking-persons",
    "https://www.unodc.org/unodc/en/data-and-analysis/glotip.html",
]

# The RFMO lists are the actual sources of record; the combined list is a
# convenience wrapper over them. Both of the pages tried first turned out to be
# JS shells with no vessel data in the served HTML, so the RFMO pages -- which
# are plain server-rendered tables -- come first now.
IUU_SOURCES = [
    ("ICCAT IUU list", "https://www.iccat.int/en/IUUlist.html"),
    ("IOTC IUU list", "https://iotc.org/vessels/iuu"),
    ("WCPFC IUU list", "https://www.wcpfc.int/wcpfc-iuu-vessel-list"),
    ("IATTC IUU list", "https://www.iattc.org/en-US/Fisheries/IUU-vessel-list"),
    ("GFCM IUU list", "https://www.fao.org/gfcm/data/iuu-vessel-list/en/"),
    ("SPRFMO IUU list", "https://www.sprfmo.int/measures/vessels/iuu-vessel-list/"),
    ("FAO Global Record", "https://www.fao.org/global-record/en/"),
    ("CCAMLR IUU list (non-contracting parties)",
     "https://www.ccamlr.org/en/compliance/non-contracting-party-iuu-vessel-list"),
    ("CCAMLR IUU list (contracting parties)",
     "https://www.ccamlr.org/en/compliance/contracting-party-iuu-vessel-list"),
    ("NAFO IUU list", "https://www.nafo.int/Fisheries/IUU"),
    ("SEAFO IUU list", "https://www.seafo.org/Management/IUU-Vessels"),
    ("NPFC IUU list", "https://www.npfc.int/iuu-vessel-list"),
    ("Combined IUU Vessel List (TMT)", "https://iuu-vessels.org/"),
]



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


def fetch(url, timeout=90, headers=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    with urllib.request.urlopen(urllib.request.Request(url, headers=h),
                               timeout=timeout, context=ctx) as r:
        return r.read()


# ==================================================================== BRAZIL
_MUN = None


def ibge_index(verbose=False):
    """Municipality name + state -> coordinates, from IBGE. Public, no key."""
    global _MUN
    if _MUN is not None:
        return _MUN
    try:
        rows = json.loads(fetch(IBGE_MUN).decode("utf-8", "replace"))
    except Exception as ex:
        print("  IBGE lookup failed: %s" % str(ex)[:70])
        _MUN = {}
        return _MUN
    idx = {}
    for m in rows:
        try:
            uf = m["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        except Exception:
            uf = ""
        key = (norm(m.get("nome", "")), uf)
        idx[key] = {"id": m.get("id"), "uf": uf, "name": m.get("nome")}
    if verbose:
        print("  IBGE municipalities indexed: %d" % len(idx))
    _MUN = idx
    return idx


def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()


_COORD_CACHE = {}


def mun_coords(mun_id):
    """IBGE malha endpoint returns the municipality boundary; its centre is
    good enough and avoids shipping a gazetteer."""
    if mun_id in _COORD_CACHE:
        return _COORD_CACHE[mun_id]
    url = ("https://servicodados.ibge.gov.br/api/v3/malhas/municipios/%s?formato=application/vnd.geo+json"
           % mun_id)
    try:
        gj = json.loads(fetch(url, timeout=40).decode("utf-8", "replace"))
        geom = gj["features"][0]["geometry"]["coordinates"]
        pts = []

        def walk(x):
            if isinstance(x, list) and x and isinstance(x[0], (int, float)):
                pts.append(x)
            elif isinstance(x, list):
                for y in x:
                    walk(y)
        walk(geom)
        if not pts:
            raise ValueError("no points")
        lat = sum(p[1] for p in pts) / len(pts)
        lng = sum(p[0] for p in pts) / len(pts)
        _COORD_CACHE[mun_id] = (lat, lng)
    except Exception:
        _COORD_CACHE[mun_id] = None
    return _COORD_CACHE[mun_id]


def harvest_brazil(a):
    """Expects a CSV of municipality, UF, rescued count, years. The Observatorio
    is a Shiny dashboard rather than an API, so its export is the realistic
    input; --file takes it."""
    rows = []
    fp = read_file(find_export(a.file, "resgat", "escrav", "brazil", "municip"), "Export the municipality table from "
                           "observatorioescravo.mpt.mp.br (its download control), save it "
                           "into your repo folder, cd there, and re-run.")
    if fp:
        rows = list(csv.DictReader(open(fp, encoding="utf-8")))
        print("  using local export: %s (%d rows)" % (fp, len(rows)))
    else:
        print("  The Observatorio Digital do Trabalho Escravo "
              "(observatorioescravo.mpt.mp.br) is a Shiny dashboard, not an API. "
              "Use its download control to export the municipality table, then:\n"
              "      python3 harvest_bulk.py --brazil --file resgates.csv\n"
              "  Expected columns: municipality name, UF, number rescued, period.")
        return []

    idx = ibge_index(a.verbose)
    out, unmatched = [], 0
    for r in rows:
        mun = None
        uf = None
        n = None
        for k, v in r.items():
            kl = norm(k)
            if mun is None and ("municip" in kl or "cidade" in kl or kl == "nome"):
                mun = v
            if uf is None and (kl in ("uf", "estado", "sigla uf", "state")):
                uf = str(v or "").strip().upper()[:2]
            if n is None and ("resgat" in kl or "trabalhadores" in kl or "total" in kl
                              or "rescued" in kl or "quantidade" in kl):
                try:
                    n = int(float(str(v).replace(".", "").replace(",", ".")))
                except Exception:
                    pass
        if not mun or n is None:
            continue
        hit = idx.get((norm(mun), uf or ""))
        if not hit:
            for (nm, u), val in idx.items():
                if nm == norm(mun):
                    hit = val
                    break
        if not hit:
            unmatched += 1
            continue
        c = mun_coords(hit["id"])
        if not c:
            unmatched += 1
            continue
        out.append({
            "name": "%s: %s rescued" % (hit["name"], format(n, ",")),
            "source": "brazil",
            "type": "Rescue operations \u2014 workers removed",
            "lat": c[0], "lng": c[1], "precise": False,
            "impact": 5 if n >= 200 else 4 if n >= 50 else 3 if n >= 10 else 2,
            "status": "Rescued",
            "state": "%s, %s" % (hit["name"], hit["uf"]),
            "url": "https://observatorioescravo.mpt.mp.br/",
            "desc": ("%s people found working in conditions analogous to slavery in this "
                     "municipality and removed by Brazil's mobile inspection group, per the "
                     "Observatorio Digital do Trabalho Escravo, run by the Labour Prosecution "
                     "Service with the ILO. <b>This is an enforcement outcome, not a risk "
                     "estimate</b> \u2014 the one layer on this map that records a rescue "
                     "rather than a possibility. Placed at the municipality centre; the "
                     "operations themselves were at farms, kilns and worksites within it. "
                     "Brazil recorded 60,251 such rescues between 1995 and 2022, which is "
                     "less a statement about Brazil than about what a country looks like when "
                     "it actually counts." % format(n, ",")),
        })
    if unmatched:
        print("  %d row(s) could not be matched to an IBGE municipality and were "
              "dropped rather than placed approximately" % unmatched)
    print("  Brazil municipality records: %d" % len(out))
    return out


# ==================================================================== GLOTIP
def harvest_glotip(a):
    fp = read_file(find_export(a.file, "glotip", "unodc", "traffick"), "Export the country table from dataunodc.un.org "
                           "(Trafficking in Persons), save it into your repo folder, "
                           "cd there, and re-run.")
    if fp:
        raw = open(fp, "rb").read()
    else:
        raw = None
        for page in GLOTIP_PAGES:
            try:
                html = fetch(page).decode("utf-8", "replace")
            except Exception as ex:
                if a.verbose:
                    print("  %-52s %s" % (page, str(ex)[:40]))
                continue
            for l in re.findall(r'href="([^"]+\.(?:csv|xlsx))"', html):
                u = l if l.startswith("http") else urllib.parse.urljoin(page, l)
                try:
                    raw = fetch(u)
                    print("  using:", u)
                    break
                except Exception:
                    continue
            if raw:
                break
    if not raw:
        print("  UNODC publishes GLOTIP through its data portal "
              "(dataunodc.un.org) rather than a stable file URL. Export the "
              "country table there and re-run with --file.")
        return []

    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))
    agg = {}
    for r in rows:
        iso = None
        for k, v in r.items():
            if norm(k) in ("iso3 code", "iso3", "country code") and v:
                iso = str(v).strip().upper()[:3]
        if not iso:
            continue
        try:
            val = float(str(r.get("VALUE") or r.get("Value") or 0).replace(",", ""))
        except Exception:
            continue
        agg[iso] = agg.get(iso, 0) + val
    out = []
    for iso, v in agg.items():
        if v <= 0:
            continue
        out.append({
            "name": "%s detected victims reported" % format(int(v), ","),
            "source": "glotip", "type": "Detected victims (UNODC)",
            "iso": iso, "state": iso, "precise": False,
            "impact": 5 if v >= 5000 else 4 if v >= 1000 else 3 if v >= 100 else 2,
            "status": "Detected",
            "url": "https://www.unodc.org/unodc/en/data-and-analysis/glotip.html",
            "desc": ("Victims of trafficking detected and reported to UNODC by this state. "
                     "<b>This counts the response, not the phenomenon.</b> A country "
                     "reporting few detections may have little trafficking or no "
                     "identification system, and this number cannot tell you which \u2014 "
                     "UNODC says so itself. Read alongside the prevalence estimate, which "
                     "is modelled independently of whether anyone was looking."),
        })
    print("  GLOTIP country records: %d" % len(out))
    return out


# ======================================================================= IUU

def pdf_text(raw):
    """Extract text from a PDF without a third-party dependency.

    Most RFMO IUU lists are PDFs with FlateDecode content streams, so zlib plus
    a regex over the text-showing operators gets the vessel numbers out. pypdf
    is used instead when it happens to be installed, because it handles the
    awkward encodings better \u2014 but it is not required, and requiring an
    install to read a public vessel list would be its own kind of failure."""
    try:
        import pypdf
        import io as _io
        return "\n".join((pg.extract_text() or "")
                          for pg in pypdf.PdfReader(_io.BytesIO(raw)).pages)
    except Exception:
        pass
    import zlib
    out = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        chunk = m.group(1)
        try:
            chunk = zlib.decompress(chunk)
        except Exception:
            pass
        # text-showing operators: (literal) Tj and [(a)-1(b)] TJ
        for t in re.findall(rb"\((?:\\.|[^\\)])*\)", chunk):
            try:
                out.append(t[1:-1].decode("latin-1"))
            except Exception:
                continue
    return " ".join(out)


DOC_EXT = (".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx")


def linked_docs(html, base):
    """Pages that describe an IUU list but do not contain it almost always link
    it. Follow anything that looks like the list itself."""
    urls = []
    for href in re.findall(r'href="([^"]+)"', html, re.I):
        low = href.lower()
        if not low.endswith(DOC_EXT):
            continue
        if not any(w in low for w in ("iuu", "vessel", "list", "annex", "cmm", "record")):
            continue
        urls.append(urllib.parse.urljoin(base, href))
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out[:6]


def _imo_check(s):
    """IMO numbers carry a check digit: the first six digits weighted 7..2 sum
    to a value whose last digit is the seventh. Cheap, and it removes almost
    every false positive a 7-digit regex picks up."""
    if len(s) != 7 or not s.isdigit():
        return False
    if sum(int(s[i]) * (7 - i) for i in range(6)) % 10 != int(s[6]):
        return False
    # The check digit alone still passes 1234567 and 0000000. Assigned IMO
    # numbers start at 5 or above, and a strictly sequential or single-repeated
    # run is a placeholder or a page artefact, not a hull.
    if s[0] < "5":
        return False
    if len(set(s)) == 1:
        return False
    if all(int(s[i + 1]) - int(s[i]) == 1 for i in range(6)):
        return False
    return True


def _looks_like_js_shell(html):
    """A near-empty document with script tags and no table is an app that
    renders client-side. Worth saying so, because 'found 0' otherwise reads as
    'the list is empty' when it means 'the data is not in this response'."""
    txt = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return len(txt.split()) < 400 and "<script" in html


def harvest_iuu(a):
    out = []
    seen_imo = set()
    for name, url in IUU_SOURCES:
        try:
            html = fetch(url, timeout=a.timeout).decode("utf-8", "replace")
        except Exception as ex:
            print("  %-42s %s" % (name, str(ex)[:46]))
            continue

        # Several patterns, because every RFMO formats its list differently:
        # labelled, in a table cell on its own, or as "IMO/Lloyd's number".
        pats = [r"IMO[^0-9]{0,12}([0-9]{7})",
                r"Lloyd'?s?[^0-9]{0,14}([0-9]{7})",
                r"<td[^>]*>\s*([0-9]{7})\s*</td>"]
        found = set()
        for p in pats:
            found |= set(re.findall(p, html, re.I))

        # Nothing in the page itself? The list is probably a linked document.
        # That is what "54,719 bytes and no IMO numbers" means in practice.
        if not found:
            docs = linked_docs(html, url)
            for du in docs:
                try:
                    raw = fetch(du, timeout=90)
                except Exception as ex:
                    print("       linked doc failed: %s (%s)"
                          % (du.rsplit("/", 1)[-1][:40], str(ex)[:34]))
                    continue
                text = pdf_text(raw) if raw[:4] == b"%PDF" else raw.decode("utf-8", "replace")
                hits = set()
                for p in [r"IMO[^0-9]{0,12}([0-9]{7})", r"\b([0-9]{7})\b"]:
                    hits |= set(re.findall(p, text, re.I))
                if hits:
                    print("       from linked document %s: %d candidate numbers"
                          % (du.rsplit("/", 1)[-1][:40], len(hits)))
                    found |= hits
            if docs and not found:
                print("       followed %d linked document(s), none carried IMO numbers"
                      % len(docs))
        # 7-digit IMO numbers have a check digit; use it to throw out years,
        # phone fragments and reference numbers that happen to be 7 digits.
        valid = {i for i in found if _imo_check(i)}

        if not valid:
            why = ("page renders client-side, so the vessel table is not in the HTML"
                   if _looks_like_js_shell(html)
                   else "no IMO-shaped numbers in %d bytes of HTML" % len(html))
            print("  %-42s 0 \u2014 %s" % (name, why))
            if a.dump:
                fn = os.path.join(HERE, "iuu_%s.html" % re.sub(r"\W+", "_", name.lower())[:30])
                open(fn, "w", encoding="utf-8").write(html)
                print("       dumped to %s" % os.path.basename(fn))
            continue

        new_here = valid - seen_imo
        rejected = len(found) - len(valid)
        print("  %-42s %d IMO numbers (%d new%s)"
              % (name, len(valid), len(new_here),
                 (", %d 7-digit strings rejected by the check digit" % rejected)
                 if rejected else ""))
        if rejected and rejected > len(valid):
            print("       more rejected than kept \u2014 if this list is known to be "
                  "larger, the page may use Lloyd's numbers or have typos; re-run "
                  "with --dump and send me the file")
        seen_imo |= valid
        for imo in sorted(new_here)[: a.max or 500]:
            out.append({
                "name": "Vessel IMO %s \u2014 IUU listed" % imo,
                "source": "iuu", "type": "IUU-listed vessel",
                "iso": "", "state": "At sea", "precise": False,
                "impact": 3, "status": "Listed",
                "url": url,
                "list": name,
                "desc": ("Listed by %s. " % name.replace(" IUU list", "")
                         + "Listed for illegal, unreported or unregulated fishing by a regional "
                         "fisheries management organisation. <b>Not a forced-labour finding.</b> "
                         "It is here because IUU operation and forced labour at sea are "
                         "strongly correlated in the documented cases \u2014 a vessel already "
                         "outside the rules on catch is the kind that stays at sea for months "
                         "without a port call \u2014 and because an IMO number is a named, "
                         "flagged, actionable entity in a domain where almost nothing else is. "
                         "Cross-reference against AIS behaviour before drawing any conclusion."),
            })
    return out


# ======================================================================= GFW
def harvest_gfw(a):
    if not a.token:
        print("  Global Fishing Watch needs a free API token from "
              "globalfishingwatch.org/our-apis. With it, this pulls vessels whose "
              "AIS behaviour matches the documented forced-labour indicators: long "
              "voyages without port calls, repeated transhipment at sea, and "
              "transponder gaps.")
        return []
    url = ("https://gateway.api.globalfishingwatch.org/v3/vessels/search"
           "?query=&datasets[0]=public-global-vessel-identity:latest&limit=%d" % (a.max or 200))
    try:
        j = json.loads(fetch(url, headers={"Authorization": "Bearer " + a.token})
                       .decode("utf-8", "replace"))
    except Exception as ex:
        print("  GFW request failed: %s" % str(ex)[:80])
        return []
    ent = j.get("entries") or j.get("data") or []
    print("  GFW vessels: %d" % len(ent))
    return []


def main():
    ap = argparse.ArgumentParser()
    for f in ("brazil", "glotip", "iuu", "gfw", "all"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--token")
    ap.add_argument("--max", type=int, default=500)
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--dump", action="store_true",
                    help="save the fetched HTML when a source yields nothing")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if not any([a.brazil, a.glotip, a.iuu, a.gfw, a.all]):
        ap.error("choose --brazil, --glotip, --iuu, --gfw or --all")

    recs = []
    if a.brazil or a.all:
        print("=== Brazil: municipality-level rescue operations ===")
        recs += harvest_brazil(a)
    if a.glotip or a.all:
        print("=== UNODC GLOTIP: detected victims ===")
        recs += harvest_glotip(a)
    if a.iuu or a.all:
        print("=== IUU-listed fishing vessels ===")
        recs += harvest_iuu(a)
    if a.gfw or a.all:
        print("=== Global Fishing Watch ===")
        recs += harvest_gfw(a)

    print("total records: %d" % len(recs))
    if a.dry_run:
        for r in recs[:20]:
            print("  %-46s %s" % (r["name"][:46], r["type"]))
        return 0
    if not recs:
        print("nothing harvested; bulk.json left alone")
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                   "note": "Enforcement outcomes, detection counts and vessel listings.",
                   "projects": recs}, f, ensure_ascii=False, indent=1)
    print("wrote", OUT, "-", os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
