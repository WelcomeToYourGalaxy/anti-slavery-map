# Live Global Slavery & Child Labour Map — build notes

A retune of the *Live Global Project Map* engine (`index2.html`) to opposition
against forced labour and child labour worldwide, and resources for victims.

## What shipped

| File | Size | What it is |
|---|---|---|
| `index.html` | 2.30 MB | The map. Self-contained except for the runtime fetches below. |
| `trackerdata.json` | 38 KB | Country directory seed — 25 countries, 2 subnational units, 67 entries. |
| `verify_links.py` | — | Link checker for expanding the directory safely. |

Deploy `trackerdata.json` next to `index.html`. Without it the map runs, but
every country popup reports no mapped source.

## What was kept unchanged

The engine is subject-agnostic and was not touched: Leaflet map, the embedded
world plate and its zoom-3→5 crossfade to satellite, the embedded `SUBGEO`
geometry, the `gb*` country→ADM1→ADM4 drilldown against the CGAZ boundary
files, the index panel, the wire panel and its region/subregion/language
filters, the facility canvas layer, the case-dot layer, every filter pill row,
and the drag-and-collapse behaviour on all panels. Every element, box, filter
row and interaction is where it was.

The **twelve lens `key` strings are identical to the source** (`projects`,
`corporate`, `spending`, `courts`, `environment`, `records`, `financial`,
`people`, `osint`, `advocacy`, `organizing`, `conserve`). Only labels,
descriptions and sub-lists changed. That keeps `ANGLE_LENS`, `INTENTS` and the
guide wiring working, and means any future tooling written against the sibling
maps still applies.

## Palette

The one deliberate visual departure. The source's green accent set reads as
land defence; carrying it across unchanged would have made this look like a
copy of the sibling map rather than its own thing. It is now **ember / amber on
near-black brown**:

| | source | here |
|---|---|---|
| `--accent` | `#356b45` | `#9a6a2e` |
| `--accent-hi` | `#7fae86` | `#e0ad6d` |
| `--accent-soft` | `rgba(53,107,69,.26)` | `rgba(154,106,46,.32)` |
| body / map / popup | `#05100a` `#0b1c1a` `#0e2014` | `#0d0906` `#17110b` `#1a1209` |

Twenty-five named colours were mapped by hand; every surviving green or teal
hex was then hue-rotated toward amber with lightness and saturation preserved,
so contrast ratios are unchanged. **0 green hexes remain.** Nothing else about
the design moved — same fonts, same spacing, same layout, same behaviour.

## What was retuned

- **Title / header** — "Live Global Slavery & Child Labour Map".
- **12 lenses, 62 sub-filters.** `conserve` was "Land Protection"; it is now
  **Survivor Support & Remedy** and is listed **first**, because that is the
  lens someone needs at the moment they actually need this map. `environment`
  became Inspection & Working Conditions; `projects` became Find a Case or Site.
- **22 goals in the intention selector**, numbered and grouped into six phases
  with disabled separator rows, in the order an investigation actually unfolds.
  The three survivor goals are **phase one**, above everything investigative.
  Each hint says why the step, why now, and what you come away with.
- **4 angles** (`wallet` / `media` / `legal` / `other`) remapped to purchasing
  power, media, law, and investigation.
- **12-step Start-here tour.** Step 1 is the emergency route and says plainly
  that an enquiry reaching an employer first has got people punished, moved and
  deported. Steps 2–12 are one worked example — a man on a contract at a fish
  plant with a recruitment debt, a held passport and company housing — run
  screen by screen from the risk lists to the buyer, the ban lists, the
  complaint mechanisms and the lawyers.
- **Help panel** rewritten as a technical walkthrough: what each element does
  and how to use it, element by element.
- **Wire lead** rewritten as a pedagogical introduction to the subject and to
  how people work on it — flowing paragraphs, no bolded category headers.
- **11 wire threads, 40 feeds, retuned scoring and stop-lists** (see below).
- **11 international bodies, 74 entries** — the ILO supervisory system, UN
  special procedures with the submission portal, IOM/CTDC, the US and EU
  enforcement instruments, public complaint mechanisms, watchdogs and
  benchmarks, survivor services, strategic-litigation organisations, company
  and supply-chain tools, and a body for work at sea.
- **Case layer** (`PJ_*`): 34 sector types with a new classifier, 14 source
  families, 5 context overlays, 14 hand-entered seed cases, and severity /
  status filters replacing the dollar-value and permit-phase ones.
- **Facility layer**: fire stations dropped (no relevance here), courthouses
  added to the default fetch set, all descriptions rewritten. The police-station
  description says outright that in several jurisdictions a worker without
  status who walks into a police station is treated as an immigration case.
- **`_GUIDES` emptied** — the source's per-country community-resistance PDFs
  don't exist for this subject, and dead buttons are worse than no buttons.

## Verified anchors

Every figure that appears in the map's own copy was checked this session:

- **27.6 million** people in forced labour on any given day in 2021, of a
  49.6 million modern-slavery total including 22 million in forced marriage;
  3.3 million of those in forced labour are children. ILO / Walk Free / IOM,
  modelled from 68 forced-labour surveys and extrapolated — the map says so.
- **138 million** children in child labour in 2024, 54 million in hazardous
  work; down 22 million since 2020 and from 246 million in 2000; the 2025
  elimination target was missed. ILO / UNICEF, June 2025.
- **204 goods across 82 countries and areas** on the US DOL TVPRA list as of
  5 September 2024 — its largest edition, adding 72 items and removing four.
- **144 entities** on the UFLPA Entity List after the 15 January 2025
  expansion, the largest single addition since the Act took effect.
- **EU Forced Labour Regulation (EU) 2024/3015** — published 12 December 2024,
  in force 13 December 2024, **applies 14 December 2027**. Commission
  implementation guidelines, the **Forced Labour Single Portal** and the
  forced-labour risk database went live **26 June 2026**. The Portal carries a
  single information submission point open to any person or organisation, and
  the Whistleblower Directive was amended to protect people who use it.
- **UK modern slavery statement registry** — 33,194 organisations registered,
  21,227 unique statements, CSV download; submission currently voluntary.
- **Brazil `Cadastro de Empregadores` ("lista suja")** — published every six
  months by the MTE under Portaria Interministerial 18/2024; the April 2026
  update added 169 employers for a register of 613, reflecting ~2,200 workers
  removed from conditions analogous to slavery.
- **GLAA** — 0800 432 0804; **UK Modern Slavery & Exploitation Helpline**
  (Unseen) — 0800 0121 700; **US National Human Trafficking Hotline** —
  1-888-373-7888 / text 233733, 200+ languages, not law enforcement.
- **Global Modern Slavery Directory** — 2,600+ organisations across ~200
  countries, filterable by service type.
- **NAPTIP** (Nigeria, 2003, mandate expressly covers forced and child labour),
  **PENCiL portal** (India, Ministry of Labour & Employment).

## The case layer is honest about being empty

`projects.json` is **not** shipped. The harvester has not been run for this
subject. The map's own provenance panel says this in the first line rather than
burying it, and the seed set of 14 cases is labelled as hand-entered.

Almost every seed case is a **dashed ring**, not a pin. That is not a
limitation of the build — it is what the sources are. Credible reporting in this
field publishes at country, sector or commodity level, both to protect witnesses
and because the reporter usually does not know the exact site. **Any map of this
subject showing crisp points everywhere should be doubted.** The two datasets
that genuinely give you locatable points are Brazil's employer register and the
UFLPA Entity List, and the harvest manifest starts with those.

The panel also refuses to state a coverage percentage, and says why: nobody has
counted this, the leading estimate is modelled and says so, and a coverage
figure would have to be invented. It makes the further point that **the absence
of a dot means nothing** — coverage tracks the reach of inspectorates, courts,
unions and journalists, not the distribution of the harm, so the blank areas are
frequently the ones to worry about most.

## Wire noise filtering

This subject has worse false-positive traps than the source's. `WIRE_OFF`
explicitly kills: metaphorical use of the vocabulary (*wage slave*, *slave to
fashion*, *slave to the algorithm*), historical-slavery coverage, the **UK
Labour Party** (*labour leader*, *labour MP*, *shadow cabinet*), **childbirth**
(*went into labour*, *labour ward*), and **childcare policy** (*child benefit*,
*childcare funding*) — each of which would otherwise flood a feed keyed on
"labour" and "child". Sports, markets and promos are killed as in the source.

## Bugs caught during the build

- `pjTypeCat` inherited a substring-matching pattern that misfires badly on this
  vocabulary. `"cement"` matched **enfor*cement***, sending the Gulf kafala case
  to "Bricks & building materials"; `"tile"` would have matched **tex*tile***,
  sending every garment case to bricks. Also fixed: `"coal"` in *charcoal*, bare
  `"stone"` in *milestone*, `"match "` in *matched*, and `"tin "` needing a
  leading space. Regression tests for all five are in `chk/pj.js`.
- Ordering bug: `gold` was tested before `battery_min`, so the DRC cobalt case
  classified as "Gold & diamonds" because its description also mentions gold.
- `voice:"advocacy"` was used on three entries — `advocacy` is a *kind*, not a
  *voice*. The engine would have silently dropped them from the voice filter.
- `_GUIDES` and the `facLightKinds` dead lens keys (`caselaw`, `enforcement`)
  were leftovers from an ancestor build; both repointed.

## Validation run on the shipped files

All five inline `<script>` blocks pass `node --check`. The body `<div>`s
balance and all required element IDs are present. `trackerdata.json` parses as
JSON, and a cross-validation pass over `DOMAINS`, `INTENTS`, the intent
selector, `internationalBodies` and `trackerdata.json` reports **0 problems**:

```
lenses 12   subs 62
intl bodies 11   entries 74
trackerdata countries 25   regions 2   entries 67
intents 23   tour 12   wire threads 11
VALIDATION CLEAN — 0 problems
```

What that check enforces, entry by entry: every `tags` value resolves to a real
`lens:sub` pair, no entry ships untagged, every `url` is absolute `http(s)`,
every `kind` is in `KINDS`, every `skind` in `SKINDS`, every `voice` in
`VOICES`, every country carries a display `name`, every `INTENTS` lens and sub
exists, every selector value has an `INTENTS` entry, and every `INTENTS` entry
is offered in the selector. Re-run it after any edit; a mistyped tag fails
silently at runtime rather than throwing, which is how the `voice:"advocacy"`
bug above survived as long as it did.

## Still open

1. **Verify the directory URLs.** Roughly two thirds of the 141 entries use
   URLs confirmed in this session's searches; the rest are official top-level
   domains entered from knowledge. Run `verify_links.py` before deploying —
   this project's no-fabrication standard means a dead or wrong link is a defect,
   not a cosmetic issue.

   ```
   python3 verify_links.py --csv report.csv
   ```

   It collects from `trackerdata.json`, `internationalBodies`, the case seed
   and `WIRE_FEEDS`, de-duplicates, tries `HEAD` then falls back to `GET`, and
   separates `REDIRECT` / `403` / `TIMEOUT` from genuine `DEAD`, because
   national labour ministries block bots and time out constantly and a naive
   checker would have you deleting live links. Exit code 1 on any dead or
   errored URL, so it can gate a deploy. It was only smoke-tested here — the
   build sandbox has no general egress, so every request returned 403. Run it
   somewhere with a real network.
2. **Expand `trackerdata.json`.** 25 countries is a seed. The efficient route to
   full coverage is the same one that worked on the GMO map: harvest the
   institutional list rather than hand-writing it. For this subject the
   authoritative per-country lists are the **ILO NORMLEX** country pages (which
   give the ratification status and the national competent bodies) and the
   **State Department TIP report** country chapters (which name each government's
   anti-trafficking unit and its shelters). Both are one entry per country of
   exactly the kind each remaining country needs first.
3. **Build the harvester** for `projects.json`, starting with Brazil's register
   and the UFLPA Entity List, since those are the only two sources that yield
   locatable named entities.
4. **Wire harvester** — `wire.json` needs generating, with the geo-tagging done
   server-side as on the sibling map (`iso`, `region`, `lang` populated at
   harvest time) rather than in the browser, which is where the sibling's
   all-zeros region filter came from.
5. **Overlay GeoJSON.** Four of the five context overlays need building; `sez`
   can reuse the existing file. The most valuable is **ILO Convention
   ratifications** — buildable directly from NORMLEX.
6. **Subnational depth.** Only the US has `sub` entries. Brazil (state labour
   offices and MPT regional units) and India (state labour departments, which
   is where bonded-labour enforcement actually sits) are the highest-value next
   additions.

---

# Second pass — live incidents, reporting routes, giving

Changes made after the first delivery, in response to: drop the schooling
phrase; make it a live map of incidents; carry the resources for victims and
for people reporting someone else, at every unit; add where to give money; add
attorneys.

## The schooling phrase is gone

`back into school` appeared twice — in the wire lead and as goal 3's label —
and is out of both. Goal 3 is now **"Get a child out of hazardous work"**, and
its hint no longer assumes a return: most children in this work are supporting
a household, so unless the lost income is replaced the child goes back to the
work or to something worse, and many were never in education to begin with. The
hint now says that, and points at what the agency can offer the household.

## The map is now live

The dot layer previously had one source: `projects.json`, harvested separately
and not shipped. It now has two, and the second runs in the browser every
session.

**How it works.** The wire is already fetched and geo-tagged each session.
`buildIncidents()` filters those items down to reported *incidents* — a raid, a
rescue, a charge, a conviction, a death, a named employer, an inspection
finding — scores each on an event-verb list, and rejects anything matching a
not-an-event list (`report finds`, `analysis`, `explainer`, `anniversary`,
`opinion`). Survivors get a severity 1–5, a stage of **Reported** or **Acted
on**, and a type, and are merged into the same layer, so every existing filter,
the search box, the popups and the recency pills work on them unchanged. The
manual wire refresh rebuilds them.

**Placement.** Country centroids are computed at load from the world-atlas
boundary geometry the map already fetches — area-weighted per polygon, so a
country with scattered islands still lands on its mainland — rather than
shipping a coordinate table that would be one more thing to be wrong. Where the
text names a region the map has geometry for, the dot moves to that region.
Co-located dots are spread on a golden-angle spiral so twenty incidents in one
country are twenty dots, not one.

**Every incident dot is a hollow ring**, because every one is a centroid. No
feed in this field carries coordinates, and this map would not plot a live site
to a street address if one did — the reasons are in the provenance panel.

**What it is not.** It is a register of incidents *reported in the press and
picked up by these feeds*, which is a much smaller and differently-shaped thing
than a register of incidents. The source description says so, each dot's own
description says so, and both say that a blank area reflects where these outlets
report rather than where this happens. The legend carries a live count, and says
plainly when the wire is quiet or `wire.json` is not deployed rather than
showing an empty map and letting you assume the world is clean.

Tested headless (`inc_test.js`): 8 synthetic wire items in, 5 incidents out,
with the report launch, the opinion piece and the explainer correctly dropped,
severity and stage assigned as expected, and two same-country dots confirmed
jittered apart.

## Reporting someone else, and giving

Two new goals, taking the selector to 25:

- **Goal 2 — "Report someone I believe is a victim."** The hint covers the three
  things worth knowing before calling: most lines take an anonymous report and
  none require certainty; some route to an NGO and some straight to police or
  immigration, which for a worker without status decides whether the outcome is
  protection or removal; and what to have ready. It also says not to confront
  the employer or tell the person, because both have got people moved,
  dismissed and deported.
- **Goal 24 — "Give money to the organisations fighting this."** Says that
  unrestricted money beats earmarked money because casework is the hardest cost
  to raise and the first to run out, and that regranting funds and direct local
  giving move more of it to the ground than international intermediaries do.

## Every popup now ends with a worldwide block

The directory is uneven and will stay uneven. Coverage of the resource slots
across the 25 catalogued countries:

```
inspection         15/25      shelter              6/25
hotline/report     10/25      wages/compensation   5/25
legal aid/status    7/25      attorneys            4/25
local allies        7/25      child protection     3/25
```

Leaving someone looking at "no sources in this lens" is the wrong failure mode
when global referral indexes cover every country on earth — and the countries
with the fewest entries are frequently the ones where the problem is worst. So
**every country and region popup now ends with five worldwide routes**: find the
helpline for this country, report someone you believe is a victim, if the person
at risk is a child, complain about a company from anywhere, and give money where
it reaches the work. They are badged **Worldwide**, explicitly marked as not
local services, and carry the instruction to call local emergency services first
if anyone is in immediate danger.

The no-data message also changed. It used to read "No sources in this lens /
subcategory here." It now reads that nothing has been catalogued there **yet,
which reflects what has been catalogued and not what exists on the ground** —
the distinction matters most exactly where the map is thinnest.

## Directory additions

`trackerdata.json` is now 25 countries / **90 entries** (from 67), and five
global referral indexes were added to the international bodies (79 entries, from
74): the EU Commission's member-state hotline list, the US State Department's
worldwide hotline index, the Global Modern Slavery Directory (~2,600
organisations, ~200 countries), ICMEC's child helplines, and Child Helpline
International.

New per-country material covers the reporting route, the enforcement authority,
the wage-recovery route, legal aid and attorneys, and where to give — for the US,
UK, India, Brazil, Nigeria, Philippines, Qatar, Thailand, Malaysia, Australia,
Canada, Germany, France, Netherlands, South Africa, Kenya, Ghana, Côte d'Ivoire,
Uzbekistan, China, Mexico, Pakistan, Indonesia and Norway.

Where I had no confident entry for a slot in a country, **that slot is empty
rather than filled with a plausible-looking guess.** That is why the coverage
table above has holes in it. Filling them is directory work, not build work: the
route is the State Department hotline index and the ILO NORMLEX country pages,
both of which are one authoritative entry per country of exactly the kind each
remaining country needs first.

## Re-validation

All six inline script blocks parse; static markup balances at 95/95; the
worldwide block renders with balanced divs, five `https` links and the emergency
caveat present; the incident builder passes its behavioural test; and the
cross-validation over `DOMAINS`, `INTENTS`, the selector, `internationalBodies`
and `trackerdata.json` is clean:

```
lenses 12   subs 62
intl bodies 11   entries 79
trackerdata countries 25   regions 2   entries 90
intents 25   tour 12   wire threads 11
VALIDATION CLEAN — 0 problems
```

One correction worth recording: the new directory entries were written against
the taxonomy from my working notes rather than the one actually in the shipped
file, so 21 tags and 16 `skind` values were wrong on first merge — `environment:epa`
where the live key is `environment:inspect`, `council` where it is
`inspectorate`. The validator caught every one. Mistyped tags fail *silently* at
runtime, which is why that check exists and why it should be re-run after any
edit to the directory.

---

# Third pass — the wire actually runs

The second pass built a live incident layer on top of the wire. The wire read
`wire.json`, and `wire.json` was not shipped and had no harvester, so the live
layer had nothing to be live from. That is now fixed twice over, because the
two fixes fail differently.

## `harvest_wire.py` — the proper path

Reads `WIRE_FEEDS` **out of `index.html`**, so there is one canonical feed list
rather than two that drift apart. Fetches all 40 feeds concurrently, parses RSS
2.0 and Atom with the standard library (no dependency), strips HTML, applies the
subject gate, de-duplicates on a normalised title, windows to `--days` (default
30), tags geography, scores significance, and writes `wire.json`.

**Geography is tagged here, not in the browser, and that is the point.** The
sibling map tags client-side by matching region names against headline text
after the feed loads — and its matcher only sees names for countries that
already have entries in `trackerdata.json`, which is exactly where its
all-zeros subregion filter came from. Doing it at harvest time means the
geography is computed once, against the full country list, and shipped as data.

Country matching is **longest-name-wins**, so "South Africa" is not eaten by
"Africa" and "Guinea-Bissau" not by "Guinea" — verified in the test below. It
also carries **local-language country forms**, pulled from the map's own
`ENDONYM` table plus a short manual list, so a Portuguese headline about
*Brasil* or an Italian one about *Italia* gets tagged instead of silently
falling out.

The subject gate runs in six languages. An English-only gate quietly drops the
coverage nearest the event, which is usually the best coverage there is:
*trabalho escravo*, *trata de personas*, *caporalato*, *Zwangsarbeit*, *travail
forcé*, *kinderarbeit* all pass. The kill-list handles the traps this vocabulary
has and the sibling's does not — metaphor (*wage slave*, *a slave to*),
historical slavery and plantation museums, the **UK Labour Party**, **childbirth**
(*went into labour*, *labour ward*), and **childcare policy** (*child benefit*,
*childcare funding*).

What it deliberately does not do: **geocode to a place.** A headline saying "raid
on a farm outside Almería" could be resolved to a point and should not be. The
workers are still there, the report is unverified, and the map's convention is
that anything without coordinates in the source is drawn as a centroid ring.
Country and region is as far as it goes.

A GitHub Actions workflow that runs it every six hours and commits the result is
in the file, commented out.

Offline test against a synthetic feed: 5 items in, the brick-kiln rescue kept
and tagged `IND`, the Labour Party item, the childbirth item and the slave-trade
museum item all correctly dropped, HTML stripped from the description, and the
Portuguese item kept and tagged `BRA` once local forms were added.

## The browser fallback — because a map that needs a cron job is a blank map

If `wire.json` is missing or empty, the incident layer stops waiting after
about twelve seconds and pulls the same feed list live through a public
RSS-to-JSON bridge, applying the same subject gate and the same
longest-name-wins country matcher.

It is worse than the harvested path in three specific ways, and the UI says all
three rather than letting the difference pass unnoticed: **slower**, **dependent
on a third-party bridge** that can rate-limit, and **country-level only**, so
the subregion filter stays thin. The count under the layer checkbox reads
"pulled live in your browser — country-level only. Run harvest_wire.py and
commit wire.json for region tagging and a longer window."

Headless test with a stubbed bridge: 6 items in, 3 kept, HTML stripped,
`South Africa` correctly beating `Guinea` on longest match, and the Portuguese
item tagged `BRA`.

## The provenance panel now describes both

A new section at the top of the panel separates the two kinds of dot —
**live incidents** (press-reported, hollow rings, a news report is not a
finding) and **determinations** (published government findings, citable as they
stand) — and explains which of the two wire paths is in use and what the
difference costs you.

It repeats the point that matters most: **an absence of dots over a country
means these feeds do not report there.** Coverage tracks journalism,
inspectorates and courts, not the distribution of the harm.

## Files now

| File | What it is |
|---|---|
| `index.html` | The map. |
| `trackerdata.json` | Country directory — deploy next to `index.html`. |
| `harvest_wire.py` | Builds `wire.json`. Run on a schedule; workflow included. |
| `verify_links.py` | Link checker. Run before deploying. |
| `BUILD-NOTES.md` | This file. |

`wire.json` is generated, not shipped. Without it the map still runs and still
shows live incidents, via the browser fallback.

## Re-validation

Seven inline script blocks parse; static markup balances at 95/95; both live
paths pass their behavioural tests; and the cross-validation is clean:

```
lenses 12   subs 62
intl bodies 11   entries 79
trackerdata countries 25   regions 2   entries 90
intents 25   tour 12   wire threads 11
VALIDATION CLEAN — 0 problems
```

One number in there is the honest weak spot: **regions 2**. Only the US has
subnational entries, so `harvest_wire.py` prints "1 country with regions" on
startup and region tagging will do almost nothing until `trackerdata.json`
grows a subnational layer. Brazil (MPT regional units and state labour offices)
and India (state labour departments, where bonded-labour enforcement actually
sits) are the two highest-value additions, and both would immediately make the
subregion filter mean something.

---

# Fourth pass — the subnational layer, and the wire tagger that can use it

The last pass ended by naming `regions 2` as the honest weak spot: only the US
had subnational entries, so region tagging had almost nothing to bind to. That
is now `regions 29`, and the tagger that consumes it has been fixed twice over.

## Brazil, state by state

Brazil is the right country to give a subnational layer first. It is the only
state that publishes the names of employers found to have used slave labour,
and the institution that drives that enforcement — the Ministério Público do
Trabalho — is organised regionally, one Procuradoria Regional per state.
Complaints go to the regional office, not to Brasília, so **the state is the
unit at which this is actually usable.**

All **27 states and the Federal District** now carry two entries each:

- the **MPT regional office**, which has its own investigative powers, brings
  public civil actions and negotiates binding conduct adjustment agreements —
  and does not depend on a criminal prosecution succeeding first. Anyone may
  file, anonymously, including from outside Brazil.
- the **regional labour inspectorate superintendence**, which is a different
  door: inspectors carry out the rescue operations and make the finding that
  puts an employer on the national register, and they act on conditions and
  unpaid wages without anyone having to prove trafficking.

Fourteen states also carry the documented sector pattern in their description
rather than a generic line — Pará on cattle and charcoal along the frontier,
Minas Gerais on coffee and charcoal for pig iron, São Paulo on garment
workshops worked largely by Bolivian and Paraguayan migrants two or three tiers
below a retail brand, Maranhão and Piauí as *origin* states for recruitment
into work elsewhere, which makes the recruitment-side case as important there
as the destination-side one. The São Paulo entry also flags that the interior is
covered by the 15th Region in Campinas, not the office in the capital — the
kind of thing that wastes a week if you find it out by filing wrongly.

The 24 regions follow the labour-court division. Eight of the state-to-region
assignments were confirmed against MPT's own sites this session (RJ, SP, RS, BA,
PR, PI, MT, MS) and the URL pattern `www.prtN.mpt.mp.br` with them. **The
remaining URLs are constructed from that verified pattern, which is not the
same as each one having been opened** — run `verify_links.py` before deploying.

Every one of the 27 region names joins exactly to the map's `SUBGEO` geometry:
27 in the geometry, 27 in the directory, zero on either side without a
counterpart. That join is what makes the region clickable and the subregion
filter real.

## Two bugs in the wire tagger, found by having data to test against

The subnational layer immediately exposed that `harvest_wire.py` could not use
it.

**Accents.** The matcher compared feed text stripped of punctuation against
region names carrying diacritics, so *Pará*, *São Paulo* and *Piauí* never
matched — and those are the states this subject concerns most. Both sides now
run through a fold that lowercases, strips diacritics via NFD, and reduces to
letters and digits. Feeds spell the same place *Para*, *Pará* and *PARA* within
the same hour, and a matcher that cares about the difference finds none of them.

**Region never implied country.** Region matching only ran *after* a country
matched, so "Fiscais resgatam trabalhadores em vinícola no Rio Grande do Sul"
got neither: the headline never says Brazil. Region now implies country when the
country was not named — with a guard, because that inference is where a naive
version breaks. Region names shorter than six characters are excluded, and any
name claimed by more than one country is dropped entirely, so **"Georgia court
hears trafficking case" resolves to Georgia the country and not to a US state.**
Region matching within a country is longest-wins, so "Mato Grosso do Sul" is not
eaten by "Mato Grosso".

Verified across seven cases: four Brazilian states from Portuguese headlines
with no country named, a US state, the Georgia ambiguity, and the
longest-match pair.

## And the dots land in the right place

Tested against the map's real embedded geometry: a Pará incident renders at
-1.71, -51.48; Rio Grande do Sul at -30.22, -52.87; São Paulo at -22.84, -48.06;
and an incident with no state named falls back to the national centroid at
-10.42, -52.80. All hollow rings, because all are centroids.

## India was considered and not done

India is the other obvious candidate — 35 units in the geometry, and
bonded-labour enforcement sits with state labour departments and district
magistrates rather than with Delhi, so the state is the operative unit there
too. It is not in this pass because I could not confirm the state labour
department URLs to the standard the rest of this file is held to, and 35
plausible-looking guesses would be worse than nothing. The national entries
already say the thing that matters most for India: the District Magistrate holds
the release-certificate power, and the certificate is the bottleneck, because
without it the rehabilitation payment does not follow.

## Counts now

```
trackerdata countries 25   regions 29   entries 144
intl bodies 11   entries 79
lenses 12   subs 62   intents 25   tour 12   wire threads 11
VALIDATION CLEAN — 0 problems
```

---

# Fifth pass — two fatal bugs, found by actually running the page

You said the map background does not show. I stopped guessing and put the page
under jsdom with stubbed Leaflet and topojson, so it executes for real and any
uncaught error surfaces with a line number. That found two aborts. **One of them
was mine.**

## `facActive` had been deleted — my bug, and fatal

The facility-layer line in the source ends:

```js
var FACCOL={...}, FACLAB={...}; var facActive={po:1,th:1,fs:1,go:1,mi:1,ch:1};
```

When I retuned `FACLAB` in the first pass — renaming "Ministry / dept HQ" to
"Agency HQ" and dropping fire stations — the replacement truncated the line and
took `facActive` with it. Every call into `buildFacFilter()` then threw
`ReferenceError: facActive is not defined`, and the facility filter never
rendered.

This is precisely the class of failure I said the validator exists to catch, and
the validator did not catch it, because it checks data against the taxonomy and
this was code. Running the page is what caught it. `facActive` is restored, with
the type list matching the new order (`po, ch, th, go, mi, dp` — fire stations
out, embassies in).

## `legActive` — inherited from the source map, and it aborts init

```js
document.getElementById('legActive').style.background=d.accent;
```

There is no element with that id anywhere in the markup. `applyAccent()` therefore
throws on **every init and every lens change** — and because it is called from
the middle of the init line:

```js
renderPills(); ... applyAccent(); updateStats();
initIndex(); syncHistToggle();
```

`updateStats()`, `initIndex()` and `syncHistToggle()` never ran. The Index panel
was being built by a function that was never reached.

**This one is not mine.** I ran your original `index2.html` through the same
harness and it throws the identical error at its own line 113. So it is in the
sibling maps too, and worth fixing wherever else that line appears. Here, all
three lookups are now guarded and the comment says why.

After both fixes the page executes with **zero uncaught errors**; the original
still reports one.

## On the background itself — what I can and cannot tell you

I could not reproduce a broken background from the file, and I want to be exact
about why rather than claim I fixed something I did not find.

- The embedded plate image decodes as a **valid 400,138-byte WEBP**, RIFF header
  and declared size both intact.
- A diff of the map-initialisation region against your original shows **one
  changed line, and it is a colour**.
- A diff of the CSS with all colours normalised shows **three added rules, all
  mine, all for the worldwide block**.
- Instrumenting Leaflet shows both builds constructing the same background:
  `L.map`, `L.imageOverlay` (the plate), and two `L.tileLayer` calls (Esri
  imagery and boundaries).

So the background code is intact. The most likely remaining explanation is
environmental, and the page previously handled it in the worst possible way: the
plate fades out between zoom 3 and 5 and hands over to Esri satellite tiles, so
**if those tiles never arrive, the plate has already been removed and you are
left looking at the container's background colour.** Nothing on screen said
which layer failed. Note also that I changed that container colour from the
source's dark teal to near-black brown with the palette, which would make the
same failure look considerably more like "nothing is there".

Three changes so it fails visibly instead:

1. **The plate is held up if the imagery fails.** Three tile errors, or twelve
   seconds with nothing loaded at all, and the fade stops and the plate stays at
   0.85 opacity. Half a background beats none, and the painted plate is a
   readable map at zoom 9.
2. **A line appears in the map key** saying satellite imagery is not loading and
   that the plate is being held instead — and that the rest of the map is
   unaffected.
3. **`mapDiag()`** in the browser console prints zoom, how many plate layers are
   attached, whether the plate is being held, the plate's byte length, satellite
   and boundary status, tiles loaded, tile errors, the country layer state, the
   directory size and the live incident count.

If it is still blank after this, open the console, run `mapDiag()`, and send me
the output — that will say which of the two layers is actually failing instead
of us both guessing.

## Your link report changed how the checker classifies

The CSV you sent is from the sibling map's directory, and it is the best test
data the checker has had. It showed the classification was wrong in two ways
that would have had you deleting working links.

**403 is not dead.** `cdc.gov`, `nrc.gov`, `phmsa.dot.gov`, `dec.ny.gov`,
`muckrock.com`, `mass.gov`, `citizen.org` and `baykeeper.org` all came back
`DEAD 403`. Every one opens fine in a browser: they refuse scripted requests.
There is now a **`BLOCKED`** status for 401/403/405/406/429 that says "refused a
scripted request; open it by hand".

**Most redirects were normalisation.** `http`→`https`, adding or dropping `www`,
a trailing slash, an `index.html` — none of which is a move. Those now compare
canonically and report `OK`, leaving the redirect list to the ones that
genuinely went somewhere else.

Re-scoring your 1,013 rows under the new rules:

```
status      before    after
OK             749       790
REDIRECT       125        84
BLOCKED          0        57
TIMEOUT         24        24
ERROR           20        20
DEAD            95        38
```

**38 genuinely dead**, not 95. And a pattern in them worth acting on: every
`epa.gov/aboutepa/epa-region-N` link is a 404 — that URL scheme has been retired,
so all ten regional entries need re-pointing in one edit rather than ten
investigations. `eplanning.blm.gov/eplanning-ui/home`,
`lobbyingdisclosure.house.gov` and the EPA EIS filing-system page are likewise
single fixes affecting several entries.

---

# Sixth pass — a test that would have caught it, and the repo

## `smoke_test.js`

The `facActive` bug shipped past every check I had, because all of them checked
data against the taxonomy and that break was code. This runs the page.

Leaflet and topojson are stubbed with a proxy that absorbs any call, and `fetch`
resolves empty, so it does not test that the map *looks* right. It tests the
thing that actually breaks: that every inline script parses, runs top to bottom,
and reaches the end without throwing. It also asserts 17 required element IDs
exist and 11 functions wired to inline `onclick`/`onchange` attributes are
defined — a handler pointing at nothing is the other silent failure in a file
this size.

Verified both directions: **passes** on the current build, and on a copy with
`var facActive={...}` deleted it prints

```
FAIL — uncaught runtime errors:
  unhandled rejection: facActive is not defined
SMOKE TEST FAILED
```

with exit 1. It catches the exact bug that shipped.

## Repo files added

`README.md` (layout, setup, Pages and Weebly embed, both workflows,
`package.json`, and the standing rules), `package.json` (jsdom plus `npm test`,
`npm run links`, `npm run wire`, `npm run serve`), and `.nojekyll`.

Two workflows are in the README ready to paste: **wire.yml** harvests every six
hours and commits `wire.json`; **check.yml** runs the smoke test on every push
and the link checker as `continue-on-error`, uploading `report.csv` as an
artifact. The link job is deliberately non-blocking — a third-party outage is
not a reason to fail your build, but you still want the report.

One deploy note that matters: **embed via iframe, do not paste `index.html`
into Weebly.** At 2.3 MB the editor will mangle the inline scripts.

## Where this stands

Working: 12 lenses / 62 sub-filters, 25 goals, 12-slide tour, 11 international
bodies with 79 entries, 25 countries and 29 regions with 144 directory entries,
a live incident layer with two feed paths, the worldwide fallback block in every
popup, and background failure that announces itself.

Still open, in the order I would take them:

1. **`verify_links.py` against everything**, including the 54 constructed
   Brazilian `prtN` URLs. Never deployed unverified.
2. **Directory coverage.** 90 national entries across 25 countries, with real
   holes — attorneys in 4 countries, donation routes in 1. The State Department
   hotline index and ILO NORMLEX country pages are one authoritative entry per
   country each.
3. **India's subnational layer**, once state labour department URLs can be
   confirmed. 35 units are already in the geometry waiting.
4. **`projects.json`**, starting with Brazil's employer register and the UFLPA
   Entity List — the only two sources that yield locatable named entities.

---

# Seventh pass — panel side, palette, and a wire that stopped padding itself

## The country box now flies in from the right

`#infoPanel` slid in from `translateX(-380px)` and was positioned by measuring
the **left** help panel. Both are reversed: it enters from `+380px` and is
positioned against the right-hand control column.

It does **not** stack under the controls, which is what a naive fix would do —
the controls run to `calc(100vh - 88px)`, so anything beneath them starts below
the fold. It sits as a **second column immediately to their left**, top-aligned
at 70px and running to 18px from the bottom. The map's fit padding was flipped
with it, so opening a country now pans the map clear on the right instead of the
left. Checked at four viewport widths: 380px wide down to 1024, narrowing to
300px at 820, never off-screen.

## Deep olive green and blue

```
--accent       #9a6a2e  →  #5f7a3c     deep olive
--accent-hi    #e0ad6d  →  #a8c072     lifted olive
body           #0d0906  →  #060c0e     near-black blue-green
map            #17110b  →  #0b1518
popups/panels  #1a1209  →  #0d1a1c
```

Twelve named anchors mapped by hand, then every remaining hex in the amber band
(10°–62°) rotated to **78° olive**, except the darkest tones — anything below
0.16 lightness goes to **185° blue-green**, which is what gives the panels and
map ground their blue cast while the accents stay olive. Lightness is preserved
throughout, so every contrast ratio in the sheet survives unchanged, and greys
below 0.05 saturation are left alone rather than tinted.

Result across the whole file: **241 colours at olive, 52 at blue/blue-green, one
stray in the amber band.** The map container is a deep blue-green, so a tile
failure now reads as sea rather than as void.

## The wire was padding itself out with near-misses

You were right, and the cause was specific. When fewer than eight items passed
the strict gate, the code fell back to a "floor" list containing **bare nouns**:
`worker`, `workers`, `migrant`, `mining`, `fishing`, `factory`, `recruitment`.
Any story with the word *workers* in it cleared that floor. On a quiet day the
strict gate would pass three items and the floor would pass ninety, so what you
mostly saw was the floor.

Replaced with a two-tier gate, applied identically in the map and in
`harvest_wire.py` so the two agree:

- **Pass** if a subject phrase is in the **title**, or if **two different**
  subject phrases appear anywhere. One subject phrase buried in a body paragraph
  is exactly how a crime round-up with "human trafficking" in its last line ends
  up in the feed.
- **Title matches rank first** — a +6 significance bonus, so headline relevance
  sorts above body relevance.
- **Thin-archive fallback uses compound phrases only** — every one at least two
  words and specific to exploitation: *migrant workers*, *conditions analogous
  to slavery*, *illegal recruitment*, *workers rescued*, *held against their
  will*. Never a bare noun. If that still yields nothing the wire says it is
  quiet rather than filling up.

The kill list also grew by three families that share this vocabulary without
being this subject: **historical and commemorative** (slavery museum,
reparations, abolitionist, Juneteenth, emancipation day, slavery memorial),
**labour economics** (labour market, labour force, labour costs, labour
shortage, labour productivity, Labour Day), and **entertainment** (TV series,
album, novel about, video game, travel guide).

Tested against fifteen realistic headlines. Kept: the brick-kiln rescue, the
seafood-plant inspection, the gangmaster jailing, the cocoa lawsuit, the
migrant unpaid-wages story. Dropped: *UK labour market cools*, *Labour shortage
hits fruit farms*, *Juneteenth events*, *Mining company reports record quarter*,
*Fishing fleet expands*, *Factory fire kills six*, *Report finds workers in the
supply chain*. The transatlantic-slave-trade museum piece and the childcare
funding piece are killed outright by the OFF list. Server-side, a crime round-up
mentioning trafficking once is dropped while one carrying two distinct subject
phrases is kept.

---

# Eighth pass — the two thinnest slots

Attorneys stood at 4 countries and somewhere to give money at 1. Both were the
worst numbers in the directory and both were things you had asked for
specifically. They are now 14 and 4, with nine new countries.

**34 countries, 29 regions, 174 entries** (from 25 / 29 / 144), plus four more
international entries.

## Coverage by slot, all 34 countries

```
local allies       20/34        attorneys          14/34
shelter            18/34        wages              10/34
report/hotline     17/34        recruiters          7/34
legal aid          16/34        donate              4/34
inspection         15/34        child               3/34
```

## Attorneys, which was the point

The gap was not that lawyers do not exist, it was that generic legal-aid links
are useless here — trafficking, unpaid wages and immigration status are three
different specialisms and a survivor needs all three at once. The additions are
organisations that do this specific work:

- **Human Trafficking Legal Center** (US) — trains pro bono counsel and keeps a
  public database of federal civil trafficking cases, so you can check what has
  been argued and what damages courts actually awarded before filing.
- **National Immigrant Justice Center** (US) — T and U visa work, because in
  most US cases the immigration question has to be settled *before* anyone
  approaches law enforcement, not after.
- **Kalayaan** (UK) — migrant domestic workers, and the group that documented
  what the tied visa does in practice: leaving an abusive employer means losing
  the right to be in the country.
- **Human Rights Law Network** (India) — offices in most states, and public
  interest litigation, which is the route that has actually forced district
  administrations to act on bonded labour where individual complaints did not.
- **Defensoria Pública da União** (Brazil) — the division of labour worth
  knowing there: the MPT prosecutes, the DPU represents the worker in the claim
  for wages and damages afterwards.
- **CCEM** (France) on domestic servitude including diplomatic households,
  **Proyecto ESPERANZA** (Spain), **MRCI** (Ireland), **HAART** (Kenya),
  **BLAST** (Bangladesh), **KAFA** (Lebanon).

## Nine new countries

Nepal, Bangladesh, Vietnam, Singapore, Lebanon, Hong Kong, Italy, Spain and
Ireland — chosen as origin countries, destination countries and the two
jurisdictions with the most specific documented patterns (Italian *caporalato*,
Gulf domestic work via Lebanon).

Two are worth calling out. **Hong Kong** carries Liberty Shared, which files the
forced-labour petitions that produce customs import bans — including the one
behind the Sime Darby palm oil order — so it belongs on the enforcement side as
much as the services side. **Nepal** carries the Foreign Employment Board,
because Nepal is overwhelmingly an origin country and the leverage is at the
recruiter and the licence, not at a workplace inside Nepal.

## Money

Four global additions, all regranting or survivor-led rather than
intermediaries: **Global Fund to End Modern Slavery** (publishes its
evaluations, including the ones that did not work), **Survivor Alliance** (run
by survivors, pays survivors for consultancy rather than asking them to tell
their story for free — the organisation to hire from as well as fund),
**Global Fund for Children** (small unrestricted grants to locally led groups),
and the ILO's **IPEC+** programme as the reference for what a child-labour
intervention is supposed to look like.

## Four countries still have no service slot at all

China, Turkmenistan, Uzbekistan and Norway. For the first three that is not an
omission — there is no independent service to point at, and inventing one would
be worse than the blank. Norway's entry is a due-diligence supervisor, which is
a different kind of thing. In all four the worldwide block at the foot of every
popup is the working route, which is exactly the case it was built for.

## Standing caveat

None of the 30 new URLs have been opened from here — this sandbox has no general
egress. Run `verify_links.py` before deploying, and read `BLOCKED` as "a live
site refusing a script", not as dead.

---

# Ninth pass — child routes, recruiters, and named producers on the map

## Child protection: 3 → 18 countries

The worst gap on a map whose title carries the words *child labour*.

Sixteen national child helplines added: NSPCC and ISPCC, Childhelp, Kids Help
Phone, Kids Helpline, 119 Allo Enfance en Danger, Nummer gegen Kummer, Telefono
Azzurro, ANAR, De Kindertelefoon, Childline South Africa, Childline Kenya, Cece
Yara, Bantay Bata 163, CWIN 1098.

**Helplines rather than child-protection ministries, deliberately.** A helpline
takes a call from a member of the public about a child they do not know; a
ministry does not. Each description carries the detail that decides whether
someone actually calls — that ANAR's number does not appear on a phone bill,
which matters when the household is the problem; that Kids Helpline has web chat,
which is the usable route when a child cannot speak aloud where they are; that
Childhelp will tell you what the mandatory-reporting rules are in your specific
state before you decide what to do.

## Recruiters: 7 → 10 countries

The fee and the licence are where the debt is created, upstream of every
workplace on this map, and the licence can only be pulled in the origin country.
Added **eMigrate** (India), **BMET** (Bangladesh), the **Sri Lanka Bureau of
Foreign Employment**, and **Ethiopia's Ministry of Labour and Skills** for the
Gulf domestic-work corridor. Sri Lanka's entry carries the detail that matters
there: registration before departure is what makes a worker eligible for the
welfare fund, and unregistered departure — which is common — forfeits it.

Four new countries with it: Sri Lanka, Ethiopia, Myanmar, Cambodia.

**38 countries, 29 regions, 195 entries.**

```
report/hotline   22/38      inspection       16/38
local allies     22/38      attorneys        15/38
shelter          18/38      wages            12/38
child            18/38      recruiters       10/38
legal aid        16/38      donate            4/38
```

## The determinations layer now names companies

14 → **25 records**, and the eleven added are the category the layer was missing:
**named producers and named vessels**, not regions and commodities.

Top Glove, FGV Holdings, Sime Darby Plantation, Taepyung Salt Farm, Linglong
International Europe, Giant Manufacturing, the vessels Zhen Fa 7 and Da Wang,
the Marange diamond fields, eastern DRC artisanal gold, and Turkmenistan's
country-wide cotton order. Every one is a published customs order confirmed
against CBP's own enforcement page this session.

This is the only category on the map where a dot can honestly carry a company
name, because the naming was done by a government and published — not inferred
here. They are still hollow rings: an order names a company, not a site.

Three are on the map for what they show about how this works rather than only
for who they name. **Top Glove** reimbursed recruitment fees and had its order
modified — the clearest documented instance anywhere of an import ban putting
money back in workers' hands. **Sime Darby** began with an NGO petition rather
than a government investigation. **Giant Manufacturing** is a well-known
consumer brand, not an anonymous subcontractor, which is worth sitting with.

Checked mechanically: all 25 records carry every required field, all classify
(the single `other` is Brazil's multi-sector register, which correctly has no
single type), phases split 14 determined / 11 open, no out-of-range coordinates,
and every record is a ring.

## Still open

1. `verify_links.py` over everything — now 195 directory URLs plus the
   international set, none opened from this sandbox.
2. `donate` is 4/38. Global funders cover it via the worldwide block, but
   country-level giving routes are still thin.
3. India's subnational layer — 35 units in the geometry, blocked on confirming
   state labour department URLs.
4. A real `projects.json` harvester, starting with Brazil's register and the
   UFLPA Entity List.

---

# Tenth pass — the determinations layer gets a harvester

`projects.json` was the last thing on the map with no way to build it. It has
one now.

## `harvest_determinations.py`

**What goes in:** only findings a government has published. Not allegations, not
prevalence estimates, not press reports — those are the wire's job and are drawn
differently.

**Where from:** US CBP Withhold Release Orders and Findings, via
**OpenSanctions**, which republishes the CBP list as structured data and
refreshes it daily. CBP itself publishes an HTML table with no API, so the real
choice is between a documented third-party mirror and a brittle scraper. The
mirror wins — and **every entry names CBP as the source of record**, so nobody
mistakes the mirror for the authority. The description says outright: check the
CBP page before citing it.

**No coordinates are invented.** Records carry an ISO3 code and no lat/lng,
because a customs order names a company and not a place. The map fills the
position at load from the country centroid it already computes off the boundary
geometry — so no coordinate table is shipped or maintained anywhere — flags the
record imprecise, and draws a hollow ring. Co-located records spread on the same
golden-angle spiral the incidents use. **A record whose country has no geometry
is dropped rather than parked at 0,0**, which is otherwise how a map ends up with
a cluster of forced-labour dots in the Gulf of Guinea.

**A failed harvest does not empty the map.** The 25 hand-entered records in
`index.html` are read back out and used as the floor, so if OpenSanctions is
unreachable the layer is unchanged rather than blank. The run prints which of
the two happened.

Tested offline with a synthetic payload: Top Glove → `MYS`, XPCC → `CHN`, Da
Wang → `TWN` (longest-name match, so Taiwan is not swallowed by China), a record
with an unresolvable country dropped rather than guessed. Commodity mapping puts
each on the right sector filter. Runtime placement tested separately: seven
records in, five out, the two unplaceable ones dropped with a console warning,
two Malaysian records jittered apart, hand-entered coordinates untouched, and no
0,0 placements.

**One thing to confirm on first run.** The OpenSanctions dataset path is
constructed from their documented layout, and this sandbox has no egress, so it
has not been fetched. Run `python3 harvest_determinations.py --dry-run -v` — it
prints the row count per candidate file and falls through three filenames before
giving up. If all three miss, the path needs correcting; the seed floor means
nothing breaks meanwhile.

Wired into `README.md`, `package.json` (`npm run determinations`) and the
six-hourly workflow alongside the wire harvest.

## Where the whole thing stands

| Layer | Source | State |
|---|---|---|
| Directory | hand-written, verified | 38 countries, 29 regions, 195 entries |
| International | hand-written, verified | 11 bodies, 83 entries |
| Determinations | `harvest_determinations.py` + 25-record seed | harvester untested against the live feed |
| Live incidents | wire, two paths | working; harvested path preferred |
| Wire | `harvest_wire.py` or in-browser fallback | working |

Still open: `verify_links.py` over all 195 URLs; country-level giving routes at
4/38; India's subnational layer, blocked on confirming state labour department
URLs; and confirming that OpenSanctions path.
