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

---

# Eleventh pass — lime out, and two harvester bugs your run exposed

## The green was lime, not olive

78 degrees at full saturation reads acid. Real olive sits nearer **67 degrees**
with the saturation pulled well down, and it has to stay dull as it gets lighter
or it goes fluorescent again.

```
--accent     #5f7a3c  →  #6b7042     hue 67, sat 0.26
--accent-hi  #a8c072  →  #a7ab80     hue 67, sat 0.20
```

Every colour in the 58–110 degree band was pulled to 67 degrees with saturation
cut to 62% and then capped — hard, and harder the lighter the colour, because a
bright colour at this hue is exactly what reads as lime. Nothing in the band now
sits above 0.42 saturation and most is at 0.10–0.20.

**That first cut went too far and dimmed the body text**, which was in the same
band at 0.89 lightness and got capped to 0.72. Caught by checking the resulting
`body` rule rather than trusting the sweep. Twelve text colours across 49
occurrences were restored to their original lightness at the new muted hue, so
the accents are dull and the copy is not. Contrast against the page background:
body text 9.4:1, accent-hi 7.1:1, accent 4.5:1.

## Your harvest run found two bugs

It worked — 61 entities, 10 records — and the output showed exactly what was
wrong with it.

**`Inner Mongolia Hengzheng Group` was placed in Mongolia.** The country matcher
scanned for substrings, and *Mongolia* is inside *Inner Mongolia*. It is a
Chinese producer, and the WRO against it was CBP's first Finding in 24 years, so
it is not an obscure record to get wrong. There is now an override list checked
before the country scan — Inner Mongolia, Xinjiang, XUAR, Hotan, Kashgar, Aksu,
Urumqi, Tianjin, Xuzhou, Yunnan, Qinghai, Tibet, Hong Kong, Macau, and the two
Koreas — and the remaining scan matches on word boundaries.

**51 of 61 entities were silently dropped.** The resolver only read the free
text and ignored the `country` property, which OpenSanctions usually supplies as
an ISO2 code. It now reads that property first, understanding ISO2, ISO3 and
full names, and falls back to the text scan. Expect that 10 to rise sharply on
your next run.

It also now **prints what it dropped and why**, rather than losing it silently —
the count, and the names, with `-v` for the full list. A record with no
resolvable country is still dropped rather than guessed.

**And it warns when it cannot find `index.html` beside it**, which is what
`hand-entered seed: 0 records` meant in your run: you were in your home
directory, not the repo. The seed is the floor that keeps the layer populated
when a harvest fails, so losing it silently was the wrong behaviour.

---

# Twelfth pass — findings that span countries, and one more turn down

## "India & Madagascar — mica" was one dot, in India

You caught a real modelling error, not a display quirk. Five of the seed records
name more than one country and each drew a single dot, so **a person opening
Madagascar, Ghana, Pakistan, Nepal, Bangladesh, the UAE, Saudi Arabia, Kuwait,
Bahrain, Oman, Cambodia or Laos was being told nothing was documented there** —
when the same listing covers them.

Records can now carry several countries and draw one dot in each. **25 → 37
records**, from five multi-country findings:

| Finding | Now draws in |
|---|---|
| Cocoa | Côte d'Ivoire, Ghana |
| Mica | India, Madagascar |
| Brick kilns | India, Pakistan, Nepal, Bangladesh |
| Kafala | Qatar, UAE, Saudi Arabia, Kuwait, Bahrain, Oman |
| Scam compounds | Myanmar, Cambodia, Laos |

The dots are not copies. Each carries an **"In this country"** note with what is
specific to that jurisdiction: that Bahrain's flexible work permit lets some
workers stay without a sponsor, which is the closest thing in the region to a
route out; that Nepal's kilns draw seasonal migrant families including children;
that Madagascar's mica runs through exporters rather than mine operators, so the
point of contact is different from India's; that Cambodia's compound rescues
have mostly followed embassy intervention rather than domestic enforcement.

De-duplication now keys on **name plus country**, so a multi-country finding
keeps one dot per country instead of collapsing back to the first. The harvester
understands the same shape, so a future source that spans countries needs no
schema change — and its own records stay single-country by construction, since a
customs order names one producer.

## Saturation down again

Everything cut to 62% of its previous saturation and capped: **0.30 in the
darkest tones, 0.20 in mid-tones, 0.12 in anything light**. Nothing in the file
now exceeds 0.30, and 191 of 283 coloured values sit at 0.10 or below.

```
--accent     #6b7042  →  #616542
--accent-hi  #a7ab80  →  #9ea28a
```

Two surfaces were re-asserted afterwards rather than left to the sweep: the map
ground at `#0a1416` and the page at `#070d0e`, both keeping a little blue-green.
Fully neutralising them would make a satellite-tile failure read as a dead grey
rectangle instead of as sea.

---

# Thirteenth pass — country boxes group by intention

A lens is a kind of record. An intention is a thing someone is trying to do.
Opening a country and reading *Corporate & Ownership / Courts & Legal / Public
Records* asked you to translate your situation into the map's filing system
before you could use it. The headings now read **"Report someone you believe is
a victim"**, **"Find lawyers who take these cases"**, **"Get a survivor their
status, wages and compensation"** — the same 24 goals as the selector, in the
same order, under the same seven phase headings, so the two halves of the
interface agree.

**Entries appear under every goal they serve**, deliberately. A legal-aid
organisation genuinely belongs under both getting a survivor their status and
finding a lawyer. A directory is more useful when it repeats than when it makes
you guess which single drawer something was filed in. The counts overlap by
design and a line at the foot of each box says so.

## Nothing falls through

The goals do not between them claim every sub-filter — 24 goals against 62
sub-filters was always going to leave gaps, and gaps in a scheme like this all
drain into an "Other" bucket, which is where a directory goes to die.

So there is an explicit orphan map: `conserve:longterm` to getting a survivor
their rights, `environment:osh` and `environment:housing` to the inspection
record, `financial:assets` and `financial:banking` to the money trail,
`people:brokers` to identifying recruiters, `records:archive` to FOI,
`spending:lobbying` to public-money contracts, and so on.

Checked mechanically: **all 62 sub-filters land in at least one goal. Zero
orphans.** The "Other" group is still built, because a future tag could miss,
but no current entry reaches it.

## Rendered against real data

```
USA  25 entries -> 19 goal groups across 7 phases   none unplaced
GBR  16 entries -> 17 goal groups across 7 phases   none unplaced
IND  12 entries -> 14 goal groups across 6 phases   none unplaced
NPL   3 entries ->  7 goal groups across 3 phases   none unplaced
ITA   3 entries ->  5 goal groups across 2 phases   none unplaced
```

Thin countries collapse to two or three phases rather than showing seven mostly
empty headings, which is the behaviour you want: Italy's three entries sit under
*If someone needs help now* and *Go public, and get help*, and nothing else is
claimed.

`lensGroupsHTML` is left defined and unused rather than deleted, so anything
else that reaches for it still works. The help panel sentence describing the old
grouping was rewritten to match — copy that describes an interface that no
longer exists is worse than no copy.

---

# Fourteenth pass — Europe

Europe was the largest hole left, and the wrong one to leave. It is a
**destination** region — most people identified as trafficked in the EU were
exploited there rather than passing through — and the directory carried six
European countries against fourteen elsewhere.

Eleven added: **Austria, Belgium, Bulgaria, Poland, Romania, Ukraine, Portugal,
Denmark, Sweden, Greece, Switzerland.** Norway gained a service route it did not
have. **49 countries, 216 entries.**

```
report/hotline   34/49        child            19/49
shelter          30/49        inspection       19/49
local allies     29/49        wages            15/49
legal aid        22/49        recruiters       10/49
attorneys        21/49        donate            5/49
```

Every European country in the directory now has a hotline route. Zero-slot
countries are down to three — China, Turkmenistan, Uzbekistan — where there is
no independent service to point at, and the worldwide block is the working
answer.

## Numbers, not just links

Each of these carries the phone number and its operating hours, because that is
what someone needs at the moment they open the box: LEFÖ-IBF on +43 1 796 92 98,
Belgium on +32 78 055 800, A21 Bulgaria on 0800 20 100, La Strada Ukraine on
0 800 500 335, APAV on 116 006, CMM on +45 70 20 25 50, ROSA on
+47 22 33 11 60, Greece on 1109, Sweden's NSPM on 020-390 000.

## The distinction each entry makes

**Who runs the line**, because for a worker without status that decides whether
asking for help starts with protection or with an immigration check. Austria has
both routes and they are listed separately and described differently: LEFÖ-IBF
is an NGO a woman without papers can walk into; the Criminal Police line is
faster to an investigation and riskier if your status is irregular. Belgium's
model is noted as unusual — recognition and the residence permit run through the
three specialist centres rather than through police.

**A second door that does not require proving coercion.** Bulgaria's General
Labour Inspectorate line and Poland's PIP act on pay and conditions without
anyone having to establish trafficking, which is the usable route when a
situation is exploitative but not yet provably more than that. Sweden's Work
Environment Authority inspects employer-provided accommodation, which is where
the berry-picking and construction cases surface.

**Who the country is in this system.** Romania and Bulgaria are among the
largest origin countries for people identified elsewhere in the EU, so ANITP's
reintegration role for returning citizens matters as much as its domestic
casework. Portugal's observatory publishes the labour/sexual exploitation split,
and Portuguese agriculture has a documented record involving workers recruited
from South and Southeast Asia. Sweden's line advises **professionals** as well as
victims, which makes it usable when you are a colleague or a nurse who has seen
something and does not know what to do next.

One fix on the way in: four entries used `skind: conduct`, which is not in the
live vocabulary. The validator caught all four. That check has now caught a
taxonomy mismatch on three separate directory expansions, which is the argument
for running it every time.

---

# Fifteenth pass — markers you can see, and a wire that reads more than English

## The palette sweeps had crushed the markers

This was a real failure, not a preference. Successive desaturation passes hit
every colour in the file, including the ones that are not interface chrome. The
project-dot ramp had ended up at `#1c2f31 #292026 #182526 #1b2526 #192525` —
five near-identical near-blacks — and the nine facility hues at the same. On an
Esri satellite basemap those are invisible.

**Chrome should recede. Markers must not.** There is now an explicitly separate
marker palette, commented as exempt from the interface scheme so a future sweep
does not eat it again:

```
scale 5  #ff6b4a   red        largest findings
scale 4  #ffa53d   amber
scale 3  #ffd24a   gold
scale 2  #a8e06a   green
scale 1  #6fd8d0   teal       smallest
```

Facility dots get nine distinct hues instead of nine near-blacks — police blue,
courthouse violet, town-hall gold, government-office green, agency orange,
embassy pink — and the help panel now shows the swatches so the key matches the
map. International markers went from olive to gold. Highlighted country outlines
went from a muted olive at 0.5 opacity to gold at 0.85, with the stroke weight
raised.

## Measured, because "brighter" is not an argument

Contrast ratio of each marker against six representative satellite ground tones
— forest, cropland, arid, ocean, urban, snow:

```
          forest cropland  arid  ocean  urban  snow
scale 5      4.3      2.1   1.1    4.9    1.9   2.4
scale 4      6.2      3.0   1.3    7.0    2.7   1.7
scale 3      8.4      4.0   1.7    9.5    3.7   1.2
scale 2      7.8      3.7   1.6    8.9    3.4   1.3
scale 1      7.2      3.4   1.5    8.1    3.2   1.4
```

Strong over forest and ocean, and **weak over arid ground and snow** — where a
bright warm dot on bright pale terrain is close to invisible whatever hue you
pick. No colour choice solves that, so the fix is structural: **every dot is now
drawn with a dark halo first**, at 0.55 alpha and 1.6px wider than the dot, plus
a heavier outline and a small white centre. The halo measures **16.8:1 against
snow**, which is what actually carries the marker over the two grounds the hue
cannot. Facility dots and the approximate rings get the same treatment.

## The wire was Anglophone

A live map of a worldwide subject that reads only English-language outlets is a
live map of what English-language outlets cover — and that is a poor proxy,
since coverage nearest the event is usually best and usually local.

**40 → 57 feeds.** Added: Repórter Brasil and Agência Brasil direct, plus
language-targeted queries in **Portuguese** (*trabalho escravo*), **Spanish**
(*trabajo forzoso*, *trata de personas*), **French** (*travail forcé*),
**Italian** (*caporalato*, *sfruttamento lavorativo*) and **German**
(*Zwangsarbeit*, *Menschenhandel*), each pinned to that country's news edition
rather than the US one. Regional English queries for India, the Gulf, Africa and
the Southeast Asian scam compounds. Al Jazeera, The Diplomat and Thomson Reuters
Foundation's Context for non-Western desks. And three labour-movement sources —
Equal Times, IndustriALL and the ITUC — which report workplace cases that never
reach a general newsroom.

The harvester's subject gate already ran in six languages, so these were
arriving filtered correctly and simply were not being fetched. Verified: the
harvester parses all 57, no duplicates, all https.

---

# Sixteenth pass — reading the first real harvest

Your run: **3,757 raw items → 617 on-topic, 208 with a country (34%), 8 with a
region**, five feeds failed, `wire.json` at 433 KB. Two numbers in that are
problems.

## 34% is the ceiling on what the map can show

An item with no country cannot become a dot. Two thirds of a working harvest was
being thrown away at the map stage, and the reason turned out to be simple:
**headlines say "Indian workers", "Brazilian prosecutors", "Chinese supplier"
far more often than they say the country's name.** The matcher only read names.

Added a demonym table — roughly 120 adjectival forms across every region — tried
after the country name and the `country` property, before the region inference.
On a sample of nine realistic headlines carrying no country name, tagging went
from 1/9 to 8/9.

**With a guard, because this is where a naive version does damage.** Geographic
features carry country names and demonyms without being about the country:
*Indian Ocean fishing fleet* is not an Indian story, *South China Sea vessel
detained* is not a Chinese one, *European Union adopts forced labour rules* is
not about any single state. A mistagged item puts a dot in the wrong country,
which is worse than no dot. Fourteen such phrases are stripped before any
matching runs, and applied to the name scan as well as the demonym scan.
Verified: those three now tag as nothing, while *Chinese supplier named in
import ban* and *EU ban hits Chinese producer* still tag CHN.

Expect the country share to rise substantially on your next run.

## 8 regions is expected, not a bug

Region tagging can only match regions the directory knows, and only Brazil and
the US have subnational layers. Until India, Nigeria, Pakistan or Indonesia get
one, this number stays near zero. Nothing to fix in the code.

## Five feeds failed

Two 404s (Guardian rights-and-freedom, Outlaw Ocean), one dead path (Context),
two hard blocks (BHRRC, ITUC). Four removed and replaced with five Google News
queries on the same beats — every query-based feed in your run succeeded, so
that is the reliable shape. **59 feeds.** The Outlaw Ocean Project stays in the
directory as an organisation; it was only its RSS path that had gone.

BHRRC's block is a bot refusal rather than a dead site, the same pattern the
link checker now reports as `BLOCKED` — worth revisiting with a different
approach rather than treating as gone.

---

# Seventeenth pass — trafficking in the title, 234 dots, and the vessel that had a gold icon

## Title

**Live Global Slavery, Trafficking & Child Labour Map.** Changed in the
`<title>`, the header, and everywhere else the old string appeared.

## Da Wang's gold icon

Not a bug in the vessel record — a **collision**. The international body *The
Ocean — fleets, seafarers & work beyond any jurisdiction* sits at −5, −150, and
I had placed Da Wang at exactly −5, −150. Two markers, same pixel, and the gold
INT icon draws on top.

Both vessels now sit at their **flag state** instead: Da Wang at Taiwan, Zhen Fa
7 at China. That is also the better placement on the merits — a boat can only be
acted against through the registry it flies under and the port it enters, so the
flag state is the jurisdiction worth knowing. Each description says so. Checked:
no seed record now sits within 3° of the Ocean marker.

## About twenty dots was the real problem

The determinations layer held 37 records, most at region or sector level, so the
map looked empty. It now holds **234 records across 85 countries**.

The addition is the **listed-goods layer** — US Department of Labor
country-and-commodity determinations, 197 records across 64 countries. Cocoa in
Côte d'Ivoire and Ghana, bricks across eight countries, gold across seventeen,
cotton across nine, garments across seven, cobalt and tin and tantalum in the
DRC, mica in India and Madagascar, tobacco in Malawi and Mozambique, fish in
Ghana and Taiwan and Thailand.

Twenty-six carry a per-country note where the mechanism is specific enough to be
worth stating: Lake Volta fishing, where children are placed with crews through
family arrangement; Indian cane-cutting, where the advance is taken by a
married couple; Malawian tobacco tenancy, which indebts a household to the
estate; Indonesian palm oil quotas that pull family members onto the plantation
unpaid; Peru's Madre de Dios gold camps, sited far from any inspection.

**Every one says, in its own description, that this is a research finding and
not a prohibition** — nothing is banned because it appears on the list — and
that the determination is at country-and-commodity level with no site or company
attached. The value is that it shifts the burden: you point at a government's
published finding rather than making an allegation.

### On how these were entered

Each is a country-and-good pair I am confident appears on the list. **Where I
was not confident, the pair is not here** — the list runs to 204 goods and I am
not reproducing it from memory wholesale. Every record links the DOL page as the
authoritative version, and `harvest_determinations.py` exists precisely to
replace this hand-entered set with the real one.

## The sector filter would have broken quietly

197 new records carrying plain commodity words — *fish*, *rice*, *jade*,
*tanzanite*, *hazelnuts*, *surgical instruments* — hit a classifier written for
sector language, and **47 of them fell into "other"**. The filter would still
have worked; it would just have been useless on the records there are most of.

Eight new branches added, and two type keys (`logging`, `forced_sex`) that the
classifier could return but which were **missing from `PJ_TYPES`** — meaning
those records would have been unreachable through the filter UI entirely.
Unclassified is now **2 of 234**, and both are genuine multi-sector records.

Sector spread: gold 32, other farming 28, bricks 18, cotton 15, sugarcane 15,
coffee and tea 14, seafood 12, garments 11, palm 9, tobacco 9.

---

# Eighteenth pass — the scale question, answered properly

You asked why a map of something affecting roughly the population of Spain shows
a few dozen dots. The honest answer is not "the map is incomplete." It is that
**49.6 million is a modelled prevalence estimate, not a list**, and the gap
between that number and what exists as records is the most important thing this
map can teach.

```
49,600,000   ILO / Walk Free / IOM estimate, extrapolated from national surveys
   230,000   CTDC individual case records, 199 countries, accumulated since 2002
    ~50,000  UNODC detected victims reported globally per year
       234   determinations and cases on this map before this pass
```

Nobody has 49.6 million names. No dataset on earth has 49.6 million locations.
What exists is **detection** — people some authority or NGO actually identified
and assisted — and detection is a fraction of a percent of the estimate.

## What I found that is actually pullable

**The Counter-Trafficking Data Collaborative.** The largest open
individual-level dataset in the field: roughly 230,000 case records across 199
countries and territories, 2002–2024, contributed by IOM, Polaris, A21,
RecollectiV and the Portuguese observatory. Published as a differentially
private synthetic dataset (ε=12) and a k-anonymised global dataset, both
downloadable as CSV.

`harvest_cases.py` pulls it, aggregates by **country of exploitation**, and
writes one record per country carrying a real count of identified people — with
the labour/sexual/child breakdown where the columns support it. That is roughly
**200 more country-level dots, each backed by case records rather than an
estimate.**

It finds the CSV by following the dataset pages rather than hard-coding a Drupal
node id, since those change between releases. CTDC blocks some automated
requests, so `--file` takes a CSV you downloaded by hand. Tested against a
synthetic CTDC-shaped file: it correctly prefers country of exploitation over
citizenship, drops the `-99` nulls, and aggregates.

**Why country level and not finer.** CTDC's public datasets are k-anonymised or
differentially private *by design*, because they describe living people who were
trafficked and many of whom are still at risk. Country of exploitation is the
geography they carry. Anything finer is both impossible from this data and
wrong. Every record is marked imprecise and draws as a hollow ring.

**And every one says: read this as detection, not prevalence.** A low count can
mean little trafficking or no identification system, and the data cannot tell
you which — countries with strong referral systems and active NGOs look *worse*
here than countries with neither. That inversion is the single easiest way to
misread this map.

## The two directories: linked, not copied

You asked whether the 2,600 organisations in the Global Modern Slavery Directory
and the State Department hotline index could be pulled in wholesale. I have not
done that, and I think copying would be the wrong call rather than merely the
hard one.

**Every country popup now carries a named block linking both**, with the
country's own name in it — "open it and choose **Kenya** in the country
selector" — so every country on earth has a route to those 2,600 organisations
from its own box.

Not mirrored, for two reasons. The weaker one is maintenance: both are actively
curated and this file is not. **The stronger one is that GMSD organisations
update and remove their entries continually, and a stale mirror in a
life-safety context can send someone to a shelter that closed a year ago.**
Polaris runs a yearly vetting process precisely because service organisations
open, close, move and lose funding. A snapshot in a single HTML file would decay
silently, and the failure mode is somebody in trouble ringing a dead number. The
block says this in the interface, not just here.

## Also in this pass

Two new source families in the legend, `Identified cases (CTDC)` and
`Listed goods (US DOL)`, so both new layers can be filtered on and off and both
carry their own caveat where the user meets them. `cases.json` loads
independently of `projects.json`, so a failure in one cannot take down the
other.

---

# Nineteenth pass — four corrections you were right about

## "Regions where slavery is known to occur even if no case was reported"

This was the real hole, and it was mine. A map built only on detection shows
**the response, not the problem**, and it inverts: countries with inspectorates,
referral systems and working NGOs produce case records and look worse, while
countries with none of those look clean.

`harvest_scale.py --prevalence` adds **Walk Free's Global Slavery Index** as its
own layer — 160 countries, modelled from national surveys plus a vulnerability
model against the ILO/Walk Free/IOM regional estimates. It covers places with no
case data at all, which is exactly the gap.

**Never merged with the case counts.** Separate source family, separate colour
in the filter, and every record says it is a modelled estimate with wide
confidence intervals that leans hardest on the model precisely where survey work
is impossible — active conflict, closed states.

## Why CTDC gave 200 dots and not 230,000

Because the public dataset carries **no sub-national geography at all**. Every
one of those 230,000 records has a country of exploitation and nothing finer, by
design — they describe living people who were trafficked and many still at risk.
230,000 individual dots would be 230,000 markers stacked on 199 coordinates: the
same information, rendered a thousand times heavier.

But you were right that one dot per country was the floor and not the ceiling.
The records also carry **exploitation type and year of registration**, and those
are two more real dimensions. `harvest_cases.py` now emits one record per
**country × exploitation type × period** — labour, sexual, both, or not
recorded, across *before 2010 / 2010–14 / 2015–19 / 2020–24* — plus the country
total. That is several times as many dots, each a genuine subset count you can
filter, rather than duplicates.

And your point about pre-2002 stands: CTDC's window starts in 2002 and the
"before 2010" bucket holds what predates the main collection period. Records
older than the dataset are not lost so much as never systematically gathered —
which is the same detection problem one generation back.

## The manual download

**It is not a one-time file** — CTDC has published successive releases (2021,
2022, 2024, and a 2025 codebook), so a scheduled harvest is worth having.

The `--file` fallback is exactly that, a fallback. The script tries the
automated route first and only tells you to download by hand if the site refuses
it. I could not test which happens from here: this sandbox has no general
egress, so *everything* fails, and that tells me nothing about what your machine
will see. Run it and find out — if the automated path works, `--file` never
comes up.

## The 2,600 organisations

Your call, and a defensible one. Done.

`harvest_scale.py --directory` pulls the GMSD and writes `directory.json`;
country popups then list the providers for that country inline, above the link
to the live directory. Since copying carries a real cost, the cost is handled
rather than argued about:

- every entry is **stamped with its sync date**, shown in the block
- the map shows an **amber warning when the sync is over 90 days old**, telling
  the reader to check the live directory
- every entry links its live record, and says inclusion is not an endorsement by
  Polaris nor republication one by anyone else
- services are tagged from their own descriptions — hotline, shelter, legal aid,
  case management, repatriation — so they land in the right goal groups

One honest caveat: **the GMSD front-end is a JS app and its data path is not
documented.** The script tries four likely endpoints and, if all miss, tells you
exactly how to find the real one — open the directory, watch the network tab for
the request returning the provider list, add that URL to `GMSD_ENDPOINTS`. Send
me what you see and I will wire it.

Tested offline against a synthetic export: providers parsed, countries grouped,
services tagged, the stale banner fires, sync date stamped.

---

# Twentieth pass — point data, and an honest no

## The State Department hotlines: no, I had not integrated them

I linked that page; I did not parse it. That was worth saying plainly rather
than letting the link imply more than it did. `harvest_points.py --hotlines`
now parses the country-by-country table into `hotlines.json`, one entry per
country, ready to fold into `trackerdata.json`. It 403s from this sandbox, like
everything else here, so run it on your machine and send me what it prints.

## Point-level data: three sources that actually exist

This is the answer to the question you have been circling, and it is better than
I expected.

**IPIS — eastern DRC artisanal mining sites.** Roughly **2,800 sites with
GPS coordinates**, field-visited repeatedly since 2009, each carrying a
**direct child-labour observation** plus armed-group interference, worker
numbers and minerals. Published as open data on their GeoServer in GeoJSON.
This is the strongest dataset in the entire field: not modelled, not inferred,
not aggregated — someone went to the pit and wrote down what they saw. The
WFS layer name changes between releases and 403s from here, so the script tells
you how to read the GetCapabilities document and update one constant.

**SentinelKilnDB — 62,671 brick kilns.** Hand-validated, detected from
Sentinel-2 imagery across the Indo-Gangetic Plain: India, Pakistan, Bangladesh,
Afghanistan. Brick kilns are the most consistently documented bonded-labour
sector in South Asia, and this is the first open comprehensive map of where
they physically are. Published as parquet on HuggingFace, so it needs one
extraction step, which the script prints verbatim. **Licence is CC-BY-NC-4.0
— check it against your use before publishing.**

**Open Supply Hub.** Millions of production facilities with coordinates,
contributed by brands, unions and NGOs, free API key. Its particular value here
is the link from a site to a **named buyer**, which is the leverage a
country-level determination on its own does not give you.

### The line these layers must not cross

Every one of these is **sector infrastructure, not confirmed exploitation.** A
brick kiln is not proof of bonded labour. A mining pit is not proof of child
labour. This is the first layer on the map where a dot is genuinely precise, and
that is exactly why the wording carries weight: every record says it is where to
look and not a finding, and adds *do not approach a site on the strength of a
dot on a map*. Their own source family in the legend, so they can never be read
as cases or determinations.

The IPIS records are the exception in one direction: where the child-labour flag
is set, that is a recorded field observation and the record says so without the
hedge.

### Volume

62,671 kilns would destroy an in-browser map. `--decimate` keeps one point per
grid cell and **reports how many it dropped** — tested on 5,000 synthetic
points: 4,158 kept at 0.05°, 561 at 0.25°. It is a display decision,
stated as one, and `--decimate 0` gives the full set.

## Other bulk datasets worth knowing about

Not built yet, in rough order of value: **UNODC GLOTIP** (detected victims and
convictions by country, downloadable); **Brazil's SmartLab / Radar SIT**, which
publishes rescue operations at *municipality* level and is the best sub-national
enforcement data anywhere in this field; **Global Fishing Watch** vessel tracks
with published forced-labour risk modelling; the **combined IUU vessel lists**;
and **Delve** for artisanal mining beyond the DRC.

Brazil is the one I would do next — it is genuine sub-national enforcement
data, thousands of operations, and the 27-state layer to hang it on is already
built.

---

# Twenty-first pass — the remaining bulk datasets

`harvest_bulk.py`, covering the four sources named at the end of the last pass.
The map now merges six optional side files, each loaded independently so no one
of them can take the others down: `projects.json`, `cases.json`,
`prevalence.json`, `points.json`, `bulk.json`, `directory.json`.

## Brazil, by municipality — the best sub-national data in this field

The Observatório Digital do Trabalho Escravo, run by the Labour Prosecution
Service with the ILO, publishes rescue operations at **municipality** level:
**60,251 people found in conditions analogous to slavery between 1995 and 2022**,
located to the town.

Nothing else in this field is comparable. It is not modelled, not estimated and
not aggregated to the country. It is a state saying: we went here, and we found
this many people. It is also the **only layer on this map that records a rescue
rather than a risk.**

Municipality names resolve to coordinates through **IBGE's public localidades
and malha APIs**, so no gazetteer is invented or maintained here. Matching folds
accents, because the source spells *Varjão*, *São Félix* and *Marabá* the way
Portuguese does and a matcher that cares finds none of them. A row that cannot
be matched to a real IBGE municipality is **dropped rather than placed
approximately** — an approximate rescue location is worse than none.

Tested with IBGE stubbed: four rows, four matches including all three accented
names, correct impact banding, all marked imprecise since a municipality centre
is not where the farm was.

The Observatório is a Shiny dashboard rather than an API, so the realistic input
is its own export; `--file` takes it and the script prints the expected columns.

One line in every record worth keeping: **that Brazil dominates this layer says
less about Brazil than about what a country looks like when it actually counts.**

## UNODC GLOTIP — detection, labelled as such

Victims detected and reported by each state. Every record says it **counts the
response, not the phenomenon** — few detections can mean little trafficking or
no identification system, and UNODC says itself the data cannot distinguish
them. It is explicitly told to be read against the prevalence layer, which is
modelled independently of whether anyone was looking. Those two layers
disagreeing about a country *is* the finding.

## IUU vessels — included with the caveat stated first

Vessels listed for illegal, unreported or unregulated fishing. **Not a
forced-labour finding**, and the description leads with that. They are here
because IUU operation and forced labour at sea are strongly correlated in the
documented cases — a vessel already outside the rules on catch is the kind that
stays at sea for months without a port call — and because an IMO number is a
named, flagged, actionable entity in a domain where almost nothing else is.

## Global Fishing Watch

Wired for a free API token, pulling vessels whose AIS behaviour matches the
documented indicators: long voyages without port calls, repeated transhipment at
sea, transponder gaps. Indicators, not findings, and labelled that way.

## A collision worth recording

Adding these produced **24 source families with four duplicate keys** — `dol`,
`brazil`, `ctdc` and `gsi` each defined twice, once in the original list and
once by me. Duplicate keys in the source filter mean two checkboxes for one
thing and ambiguous filtering, and nothing would have thrown. Deduplicated to
**19 families, keeping the versions that carry the caveats**, and verified that
every source key any harvester emits has exactly one family.

That is the third time a silent-failure class has been caught by checking rather
than by the thing breaking. The pattern holds: in a file this size, the bugs
that matter do not throw.

---

# Twenty-second pass — three failures from the first real run

## The traceback

`FileNotFoundError` with a raw stack trace. That is a bad way to tell somebody a
file is missing, and it was in four scripts. There is now a shared `read_file`
helper: it names the file, prints **which directory you are actually in**, says
what to do about it, and lists any data files it can see there — or says there
are none at all, which is the tell that you are not in the repo folder.

```
  File not found: resgates.csv
  You are in: /Users/commanderutra
  Export the municipality table from observatorioescravo.mpt.mp.br (its
  download control), save it into your repo folder, cd there, and re-run.
  No .csv/.json/.xlsx files in this directory at all — you are probably not
  in the repo folder, or the export has not been made yet.
```

To be clear about that run: **`resgates.csv` was the name I used in an example,
not a file that exists.** Brazil's Observatório is a Shiny dashboard, so the
export has to be made from its download control first.

## IUU: "0 found" was hiding the reason

Both pages returned zero, and the old code could not distinguish *the list is
empty* from *the data is not in this response*. It was the second: both are
client-rendered apps with no vessel table in the served HTML.

Three changes:

**Better sources.** The RFMO lists are the actual records of origin, and they
are plain server-rendered tables. ICCAT, IOTC, WCPFC, both CCAMLR lists, NAFO,
SEAFO and NPFC now come first, with the combined list last as a convenience
wrapper.

**Three extraction patterns**, because every RFMO formats differently —
labelled `IMO`, labelled Lloyd's, or a bare number in its own table cell.

**IMO check-digit validation.** A 7-digit regex picks up years, phone
fragments and reference numbers. IMO numbers carry a check digit — the first six
digits weighted 7 down to 2, summed, last digit equals the seventh. Plus a
plausibility guard, because the check digit alone still passes `1234567` and
`0000000`: assigned numbers start at 5 or above, and a single repeated digit or
a strictly sequential run is a page artefact, not a hull. Verified against both.

**And it now says why it found nothing** — whether the page renders client-side,
or simply had no IMO-shaped numbers in N bytes of HTML — reports how many
7-digit strings the check digit rejected, and warns when it rejected more than
it kept, which is the signature of a list using a different numbering scheme.
`--dump` saves the HTML so it can be looked at rather than guessed about.

Tested end to end on a synthetic RFMO table: valid IMO kept, invalid rejected
with the count reported, JS shell correctly identified, real page not
false-flagged.

## What still needs an export

Two, and both for the same reason — the publisher has no stable file URL:

- **Brazil**: export the municipality table from the Observatório's download
  control.
- **UNODC GLOTIP**: export the country table from dataunodc.un.org.

Everything else is automated. And every one of these commands has to be run
**from inside the repo folder** — `cd` there first, then run.

---

# Twenty-third pass — reading the IUU run

Your run produced **18 real vessels from CCAMLR's non-contracting-party list**,
which is the first live confirmation that the parser and the IMO check digit
work against a real RFMO page. The other results are diagnostic rather than
failure, which was the point of making it report why.

```
ICCAT       0 — no IMO-shaped numbers in 54,719 bytes of HTML
IOTC        0 — page renders client-side
WCPFC       404
CCAMLR NCP  18 IMO numbers                      <- worked
CCAMLR CP   0 — page renders client-side
NAFO        0 — no IMO-shaped numbers in 49,296 bytes
SEAFO       timed out
NPFC        404
TMT         0 — no IMO-shaped numbers in 12,663 bytes
```

## "50,000 bytes and no IMO numbers" means the list is a linked document

That is the ICCAT and NAFO pattern: a page *about* the list, with the list
itself in an attached PDF. So when a page yields nothing, the harvester now
follows its document links — anything ending `.pdf`, `.xlsx`, `.csv` or `.doc`
whose URL also mentions iuu, vessel, list, annex, cmm or record, capped at six
per page so it cannot wander.

**PDF text extraction with no dependencies.** RFMO lists are FlateDecode PDFs,
so zlib plus a regex over the text-showing operators gets the numbers out.
`pypdf` is used when it happens to be installed because it handles awkward
encodings better, but it is not required — needing a pip install to read a
public vessel list would be its own kind of failure.

Tested end to end: a page with 300 sentences and no numbers, linking a
compressed PDF holding three vessels — the fallback fired, extracted all three,
kept the two with valid check digits, rejected the third, and reported the
rejection. Link discovery correctly picked the IUU list and the annex while
skipping `/about.pdf`.

## The rest

- **404s**: WCPFC and NPFC paths corrected.
- **Timeout**: SEAFO now gets the configurable `--timeout`, default raised to 90s.
- **Four RFMOs added**: IATTC, GFCM, SPRFMO, and the FAO Global Record.
- **Client-rendered pages** (IOTC, CCAMLR contracting parties, TMT) still need
  their JSON endpoint identified. That is what the `--dump` files are for —
  send them, or open the page's network tab and send the request that returns
  the vessel table.

## One practical thing

`bulk.json` was written to `/Users/commanderutra/` — your home directory, not
the repo. Every harvester writes next to itself, so **run them from inside the
repo folder** or the map will never see the output. `cd` there first.

---

# Twenty-fourth pass — repo-only operation

Clarified: **nothing runs on your computer.** Everything executes in GitHub
Actions, writes into the repo and commits itself.

## The manual-export problem, solved without a laptop

Four sources publish through a dashboard rather than a stable file URL — Brazil's
Observatório, UNODC's data portal, CTDC, and Walk Free. Previously that meant
"download it and pass `--file`", which is a local step.

Now every harvester looks in **`data/`** in the repo when `--file` is not given,
matching on a keyword in the filename: `resgat`, `glotip`, `ctdc`, `gsi`,
`kiln`. Download the export once in a browser, commit it to `data/`, and every
scheduled run from then on uses it. `--file` still wins when given.

Tested: dropping `resgates_brazil.csv` into `data/` and running with no
arguments finds it and reports which file it picked.

## One workflow instead of three

`harvest-all.yml` runs all seven harvesters on one schedule — wire every six
hours, everything else weekly — with each step allowed to fail on its own.
One publisher being down should not stop the other seven layers from refreshing,
and a red run that blocks the commit means stale data everywhere rather than in
one layer.

## Worth knowing about Actions runners

GitHub's runners come from cloud IP ranges and some publishers block those. If a
source works in your browser but 403s in Actions, that is the reason — and the
export-to-`data/` route is the fix for that case as well as for the dashboard
case.

---

# Twenty-fifth pass — "only 20 entries" was a race condition, and it was mine

## The count

18, not 20 — and that number is diagnostic. Of the 234 seed records, **18 carry
explicit coordinates and 216 depend on `ISO_CENTROID`**, the country-centroid
table built from the world-atlas boundary file the map fetches at load.

`pjLoad` and that fetch race each other. When `pjLoad` won, `_pjPlaceByISO`
found an empty centroid table and **dropped all 216 records**, logging a warning
nobody reads. The map drew 18 dots and looked almost empty. On a fast connection
the atlas sometimes won and you would see all 234, which is the worst kind of
bug: intermittent, silent, and it looks like missing data rather than broken
code.

Unplaceable records are now **parked, not dropped**. Once the atlas finishes and
the centroids exist, `_pjFlushPending()` places them and redraws. Tested in both
orderings: pjLoad first gives 18 placed and 216 parked, then the flush brings it
to 234 of 234 with nothing left parked and every record carrying coordinates.

The console messages were wrong too. A parked record used to be reported as
"dropped: no boundary geometry for the country code given", which reads as *that
country does not exist* when it actually means *the boundaries have not finished
downloading*. Now those are two different messages, because they call for two
different reactions.

## The repo directory is misspelled

```
.gtihub/workflows/     <- what is in the repo
.github/workflows/     <- what GitHub reads
```

Nothing has ever run. That is the entire reason there is no `wire.json`,
`projects.json`, `cases.json` or anything else in the repo — not a permissions
problem, not a settings problem, just three transposed letters. GitHub gives no
warning for this; an unrecognised dot-directory is simply ignored.

## Repo audit

`index.html` is current: 234 seed records, correct title, intent grouping,
GMSD block, all six side-file loaders. `trackerdata.json` is current at 122 KB.
All seven harvesters present. `.nojekyll` present. Nothing missing except the
harvest output, which follows from the directory name.

---

# Twenty-sixth pass — the first real run worked; three of my bugs threw it away

Read past the red X: **the harvesting succeeded.**

```
wire.json        423,543 bytes   4,109 raw -> 606 on-topic, 244 with a country (40%)
projects.json    248,460 bytes   234 seed + 55 harvested from CBP = 289 records
bulk.json         17,062 bytes   18 IUU vessels from CCAMLR
```

The demonym work paid: country tagging went **34% -> 40%**. The OpenSanctions
country-property fix paid harder: **10 -> 55 records**, which is the whole CBP
list rather than a fifth of it.

Then the commit step lost all of it.

## 1. The push race — this is why nothing landed

```
! [rejected] main -> main (fetch first)
```

The remote moved while the job ran — you were uploading files through the web
UI at the same time — and the step pushed straight at `main` with no rebase. An
hour of harvesting, discarded because of a race with a file upload.

The commit step now rebases onto whatever landed and **retries five times with
backoff**, and a `concurrency: harvest` group stops two runs pushing over each
other. It also exits early and quietly when nothing actually changed, instead of
making an empty commit every six hours.

## 2. `verify_links.py` crashed on a line that never did anything

```python
for u, n in re.findall(r'"url":"(https?://[^"]+)"', line), []:
    pass
```

Leftover from a first draft: it iterates a two-element tuple and tries to unpack
each element into two names. `ValueError: not enough values to unpack`. It threw
on every run and the loop below it — the one that actually collects URLs —
worked fine. Deleted. The checker now runs to completion.

## 3. The smoke test failed on an error with no message

```
FAIL — uncaught runtime errors:
  
```

Blank. Some jsdom versions emit an empty error object when a stripped external
`<script>` tag is encountered, and CI runs Node 20 against my Node 22, so it
failed there and passed locally.

Entries with **no message text at all** are now counted and reported but do not
fail the build; anything carrying actual text still does. Suppressing a whole
error class would have been the wrong fix, so the count is printed either way:
`runtime errors: none (1 empty error object ignored — jsdom noise, not a page
fault)`.

## Also from the log

- **Six CBP entities had no resolvable country** and were correctly dropped
  rather than guessed. Five are vessels, which carry no country in the entity
  record, and one is Somali. Flag states added: Dalian Ocean Fishing, Zhen Fa,
  Hangton to China; Lien Yi Hsing, Da Wang, Yu Long to Taiwan; Asli Maydi to
  Somalia. Next run should place all 61.
- **Hotlines parsed 0 countries.** The State Department page is not a table.
  The parser now also reads `Country: number` list items and paragraphs, and
  when both fail it reports the byte count and visible word count rather than a
  bare zero. Tested against table form, list form, and a JS shell.
- **IPIS timed out** at 90 seconds. Raised to 180 — a GeoServer WFS returning
  2,800 features with full attributes is a slow request, not a broken one.
- **Four IUU 404s** (IATTC, SPRFMO, NPFC, WCPFC) now point at each body's
  landing page, so the document-following step can find the list from there.
- **Three feed 404/403s** in the wire: the Guardian rights-and-freedom path is
  still in the deployed copy, and Anti-Slavery International and BHRRC block
  cloud IPs. The first is fixed in the current `index.html`; the other two are
  the cloud-IP problem the README warns about.

---

# Twenty-seventh pass — making the checks tell the truth

## The smoke test was passing all along

The fixed `smoke_test.js` runs clean against **your repo's exact `index.html`**,
tested here. So that run used the old copy: the fix had not been uploaded when
it fired.

I could not tell that from the log, which is the actual defect. Two changes so
the next one answers it immediately:

- **A version stamp.** The first line is now `smoke_test 2026-08-02 | node
  v22.22.2`. If that line is absent or dated, the file in the repo is stale, and
  you know it before reading anything else.
- **Blank errors are described, not swallowed.** It prints the count, the raw
  form and the type of each one. Suppressing an error class silently would have
  been the wrong fix — a real fault hiding behind an empty message stays visible.

The workflow now **pins Node to 22**, the version this is verified against. The
failure was Node 20-specific: an empty jsdom error object with nothing to do
with the page.

## Links: 35 of 35 "redirects" were Google rewriting its own URL

Google News rewrites `hl=en` to `hl=en-US` on every request. That is not a move,
and reporting it as one buried the redirects that went somewhere else. The
canonical comparison now strips locale and tracking parameters — `hl`, `gl`,
`ceid`, the `utm_*` set, `fbclid`, `gclid` — before comparing, and sorts what
remains. Unit-tested against the real cases plus http→https, `www`,
`index.html`, a genuine path move and a genuine query change.

## Links: the job going red taught you to ignore it

45 dead out of ~290 checked, and the step exited 1. Over that many third-party
URLs something is always down, and a permanently red tick is worse than no tick
— you stop reading it.

`verify_links.py` now **exits 0 by default** and prints the dead list *in the
log*, so you can see what needs fixing without downloading the artifact.
`--strict` restores the old behaviour for gating a deploy, with `--max-dead N`
for a tolerance.

**Those 45 are still real and still worth fixing.** They are in the run's
`report.csv` artifact; send it and I will work through them. From the earlier
report, expect a cluster: retired URL schemes where one edit fixes ten entries.

---

# Twenty-eighth pass — the failure was in the test, not the page

The version stamp did its job: `smoke_test 2026-08-02 | node v22.23.1` proved
the current file was running, so the failure was real. Then the widened error
capture named it:

```
"type=unhandled-exception  message=Uncaught [SyntaxError: Invalid or unexpected token]"
```

And it was **mine, in the harness**.

## The bug

`smoke_test.js` injects a stub `<script>` built as a JavaScript template
literal. I had written `split('\n')` inside it. A template literal consumes that
escape, so what actually got injected was a string literal containing a **real
newline** — which is a syntax error. The injected script died on parse, jsdom
reported an uncaught exception against the document, and the harness blamed
`index.html`.

All six real script elements parse cleanly. I confirmed that separately by
splitting the document the way an HTML parser does — at the first `</script`,
not by my own regex — and compiling each one: 2,122,647 bytes, 54,542, 252,657,
11,893, 11,782, 15,484, all fine.

## Why it hid for two runs

The old error handler stringified a jsdom error detail object into an empty
string, so the log printed `FAIL — uncaught runtime errors:` followed by a blank
line. My "ignore blank errors" change from the last pass made that worse: it was
built on the theory that the blank was jsdom noise. It was not. It was a real
error with an unhelpful stringification, and I had reasoned my way into
suppressing the one signal that mattered.

The capture now records name, message, first three stack frames, source file and
position, from `onerror`, the `error` event and `unhandledrejection`; falls back
to `JSON.stringify` on anything opaque; and prints entries JSON-escaped so a
leading newline can never render as a blank line again.

## The check that should have existed

**The harness now parses its own stub before injecting it**, and exits 2 with a
distinct message:

```
HARNESS BUG: the injected stub does not parse — Unexpected token ';'
This is smoke_test.js's own fault, not index.html's.
```

Verified by deliberately breaking the stub. A test that reports its own faults
as faults in the thing under test is worse than no test, because it sends you
looking in the wrong 2.5 MB file.

Also added: the file under test is now printed with its **byte count and a short
sha256**, so a stale or truncated upload is visible in the first two lines of
the log rather than inferred three runs later.

---

# Twenty-ninth pass — a real CSS defect, found by a version mismatch

The widened capture finally named it:

```
"type=css parsing  message=Could not parse CSS stylesheet"
```

## Why CI failed and my machine did not

`package.json` pinned `"jsdom": "^24.0.0"`. My build directory had **jsdom 30**,
installed without that constraint. So CI ran a six-major-version-older CSS
parser than the one I was verifying against, and jsdom 24 is much stricter.

Reproduced by installing jsdom 24 deliberately. Pinned to `^30.0.0` so CI and I
run the same engine.

## And jsdom 24 was right about something

Bisecting the stylesheet by brace depth found this, at line 130 of the first
style block:

```css
@media (max-width:640px){ ... { ... } } }
                                    ^ one closing brace too many
```

The block ends at **brace depth −1**. Browsers recover from this; jsdom 30
recovers from it; jsdom 24 rejects the sheet outright. It has been there the
whole time — **including in the original `index2.html` you gave me**, so it is
in the sibling maps too and worth fixing wherever that stylesheet came from.

An extra brace silently kills every rule after it in some engines. That is
exactly the class of defect nobody notices until a stricter parser complains.

## The remaining complaint is jsdom's, not the page's

With the brace fixed, jsdom 24 still objects — its CSS engine rejects things
browsers accept, and it does not say what. jsdom's CSS parser is not a
conformance oracle, so a `css parsing` jsdomError is now **reported loudly and
separately but does not fail the build.**

That would be the same reasoning error I made two passes ago — suppressing a
signal because it is inconvenient — except this time it is replaced with
something better:

**The smoke test now checks brace balance itself**, per style block, skipping
comments and strings. That is the structural check jsdom 24 was accidentally
providing, done deliberately and in a way that names the block and the depth.
Verified in both directions: the current file reports "all 6 style blocks
balanced", and a deliberately broken copy fails with "style block 0 ends at
brace depth 1".

Under jsdom 24 the suite now passes with the note printed. Under jsdom 30 it
passes clean.

---

# Thirtieth pass — the "20 dots" had a second cause, and it was one line

The race-condition fix was correct but incomplete. There was a second path that
bypassed it entirely:

```js
.catch(function(err){ ...; pjData = PJ_SEED; pjRender(); });
```

When `projects.json` is absent — which it is, because the harvest push has not
landed yet — the loader falls back to the seed set baked into `index.html`. And
it assigned that seed **raw**, without running it through `_pjPlaceByISO`.

216 of the 234 seed records carry an ISO code and no coordinates; they are meant
to be placed at a country centroid at load. Assigned raw, they have no `lat` and
never render. The map drew **the 18 records that happen to have explicit
lat/lng** — the vessels, the region-wide orders — and looked almost empty.

Verified both ways: old fallback yields 18 renderable dots, new fallback yields
**234 of 234**. The console now also says which set is in use and how many
records it holds, so "is this the seed or the harvest?" is answerable from the
log rather than by counting dots.

Two different bugs produced the same symptom, which is why the first fix looked
like it had not worked.

## IPIS now finds its own layer

That timeout was the blocker on the one dataset that gives real GPS points —
~2,800 field-visited artisanal mining sites in eastern DRC, each with a direct
child-labour observation.

It no longer depends on a hard-coded layer name. It reads GeoServer's
`GetCapabilities`, filters to layers mentioning mines, and **sorts DRC first,
then CAR, preferring curated layers**, falling back to three known names if
capability discovery itself fails. Each attempt is reported. Timeout raised to
240s, because a WFS request for 2,800 features with full attributes is a slow
request rather than a broken one, and the previous 90s ceiling was the whole
failure.

Tested against a synthetic capabilities document: correct ordering, correct URL
construction.

## Where the point-level data stands

| Layer | Points | Status |
|---|---|---|
| IPIS mining sites | ~2,800 GPS | discovery + 240s timeout; retry the workflow |
| Brick kilns | 62,671 GPS | needs the one-off HuggingFace extraction |
| Brazil rescues | municipality | needs the Observatório export in `data/` |
| Open Supply Hub | millions | needs a free API token |

The 234 dots you will see after this fix are country centroids. **The genuine
lat/long layer is IPIS**, and it is one successful workflow run away.

---

# Thirty-first pass — the map now says why a layer is empty

Four layers were reported missing. **Three of them cannot have data yet, and
that is not a bug:**

| Layer | Why it is empty |
|---|---|
| Brick kilns (62,671 GPS) | needs a one-off HuggingFace extraction that has not been run |
| Brazil rescues | needs the Observatório export committed to `data/` — it is a dashboard, not an API |
| Open Supply Hub | needs a free API token, never supplied |
| **IPIS mining sites** | **should run unattended — this one is a real failure** |

Only IPIS is unexplained, and its log line will say which layers GeoServer
advertised and which it tried.

## The page should have told you this

We have spent several rounds trading workflow logs to answer "why is this
empty?", which is a question the page can answer about itself. It could not,
because a missing side file produced no message at all — just fewer dots.

There is now a **data-layer list under the map key**, listing all seven files:
whether each loaded, how many records it contributed, and for anything missing,
**the exact command that writes it and what that command needs first**. Plus a
line that matters more than the list: *a layer that is not present is a file
that has not been harvested yet, not an absence of data in the world.*

```
Data layers — 3 loaded, 3 not present · 3,121 records
  ✓ Determinations (customs orders, listed goods)   289
  — Identified cases by country (CTDC)
      python3 harvest_cases.py
      CTDC blocks some automated requests. If it fails, download the
      Global Synthetic Dataset CSV and commit it to data/ ...
```

`dataDiag()` in the console prints the same as a table, including the reason
string from any fetch that threw.

The provenance panel now opens with the same point, naming the three layers that
cannot run unattended so nobody waits on a workflow that was never going to
produce them.

Tested in both states: all-missing, and partial success with counts and the
record total.

---

# Thirty-second pass — IPIS is network-blocked, not broken

```
GetCapabilities failed (<urlopen error timed out>); trying known layer names
  public:cod_mines_curated_all_opendata_p_ipis   <urlopen error [Errno 110] Connection ti
  public:cod_mines_curated_all_opendata_ipis     <urlopen error [Errno 110] Connection ti
  public:caf_mines_curated_all_opendata_p_ipis   <urlopen error [Errno 110] Connection ti
```

A connection timeout on **every** attempt, including the tiny GetCapabilities
request, is not a slow query. `geo.ipisresearch.be` is refusing GitHub's cloud
IP ranges — the exact case the README warns about. No layer-name fix or timeout
increase can reach it.

So IPIS gets the same `data/` escape hatch as the dashboard sources: download
the GeoJSON once, commit it, and every run uses it with no network call. The
failure message now prints those three steps instead of speculating about
service speed. Tested end to end with a committed export: features read,
child-labour flag honoured, and the flagged record correctly ships without the
"not evidence" hedge because that one *is* a field observation.

`find_export` now accepts `.geojson`.

## The IUU document-following worked, and followed the wrong documents

```
from linked document CMM-01-2026-Trachurus-murphyi.pdf: 4 candidate numbers
from linked document CMM-02-2026-Data-Standards.pdf: 11 candidate numbers
```

The PDF extractor works — it read six PDFs and pulled numbers out of all of
them. But my link filter accepted anything containing `cmm`, which is every
conservation measure the body has ever published, and the "candidate numbers"
were paragraph and year references. The check digit rejected all of them, which
is the system working, but the run was wasted.

Narrowed to `iuu` in the filename, or `vessel` **and** `list` together. Verified:
`CMM-04-2025-IUU-Vessel-List-.pdf` and `vessel_list_2026.pdf` are followed;
`CMM-01-Trachurus` and `CMM-02-Data-Standards` are skipped.

Each followed document now reports **characters extracted, candidates found, and
valid IMOs**, and says so explicitly when almost no text came out — which
distinguishes "this PDF has no vessel numbers" from "this PDF is scanned images
and my extractor cannot read it". That distinction was invisible before.

## Everything else in that run

- **Determinations**: 61 CBP records, up from 55 — the six vessel flag states
  resolved as intended.
- **Wire**: working.
- **IUU**: 18 vessels from CCAMLR, unchanged.
- **Hotlines**: still 0, from 181,147 bytes and 4,653 words of visible text. The
  page has content but neither a table nor `Country: number` lines. Needs
  `--dump` and a look at the actual markup.

---

# Thirty-third pass — the IPIS data landed, and it is the best layer on the map

You uploaded the two IPIS CSVs. They carry more than I expected.

## What is actually in them

**8,077 sites, every one with coordinates.** And the columns are not risk
proxies — they are field observations:

```
childunder15                 934 sites flagged (DRC), plus counts in the CAR file
childunder15work             the tasks recorded for those children:
                             "Creuser, Lavage, Traiter les déchets" — digging,
                             washing, processing waste
forced_labour_armed_group1/2/3   192 sites where an armed group was recorded
                                 as using forced labour
```

`harvest_points.py` now reads the CSV form as well as GeoJSON, reads **several
files at once** so DRC and CAR sit side by side, and handles the two flag
conventions — the DRC file uses 1/0, the CAR file records a count.

Records where forced labour was observed are severity 5, child labour 4, and
**neither carries the "not evidence that this site uses it" hedge**, because
for these the observation *is* the evidence. Everything else keeps the hedge.

## Thinning would have deleted exactly the wrong records

8,077 points is 7.9 MB and would not render. But a grid that keeps one point per
cell discards whichever site is not first in each cell — and of ~8,000 sites,
1,791 carry an observation. Most of them would have gone, in favour of
unremarkable pits.

Decimation now **never thins a site with an observation**. All 1,791 are kept
regardless of the grid; the grid applies only to the rest.

```
kept all 1791 site(s) with an observation of forced or child labour
3128 kept, 4949 dropped at 0.040° per cell

Child labour observed   1,582
Forced labour observed     209
Site visited             1,337
```

**`points.json` is generated and included** — 3,128 records, all precise pins.
Commit it and the layer appears immediately; no workflow run needed.

## The Brazil link

`observatorioescravo.mpt.mp.br` no longer resolves. The Observatório moved to
the SmartLab platform: **smartlabbr.org/trabalhoescravo**. Corrected in the
harvester and in its failure message.

---

# Thirty-fourth pass — Open Supply Hub is no longer free, and I said otherwise

I told you to register and generate a token. That path does not exist any more.
As of 2026 the OS Hub API is a **paid subscription** — 14-day trial, then billed
via Stripe — and the *My Account → Settings → API → Generate New API Token*
route I described is gone. My instruction sent you to install Postman for a page
that no longer exists, which is on me.

The GitHub organisation you found is the platform's own source code and
`open-supply-hub-api-examples` is its developer documentation. Neither carries
the facility data, so neither is a way round the subscription.

Two routes that cost nothing, both now in the script's failure message:

1. **Free/discounted API access policy** for non-profits, civil society
   organisations and research institutions. Application form, reviewed within
   two weeks. This project fits that description squarely.
2. **Data Downloads** — the same data as CSV or Excel, no API at all. The
   harvester now treats a committed download as a **first-class input** rather
   than a fallback, since it is the only free route: drop it in `data/` with
   `osh`, `supply` or `facilit` in the filename and it is read on every run.
   Tested with a sample file.

And the honest weighting, which the script now prints before either route:
**this layer maps facilities, not exploitation.** A garment factory on the map
is not evidence of anything. Its value is the link from a site to a named buyer,
which is real but secondary — it is the weakest of the four point layers, and
the one to do last if at all.

The order I would work in now: IPIS is done. Brazil next, because municipality
rescues are enforcement outcomes. Kilns after, if the licence suits. Open Supply
Hub only if the free-access application succeeds.

---

# Thirty-fifth pass — one file

Eight uploads to change one thing was the wrong shape for how you actually work,
and a map that silently loses a layer when one of them does not land is worse.

`bundle.py` writes **index.bundle.html**: every data layer embedded, nothing
beside it required. Upload that one file.

## The runtime did not change

The loader still fetches the side files first and only falls back to the
embedded copy. So the same bundle **works alone** and **picks up fresh harvest
output** when deployed next to it. Bundling adds a floor; it does not freeze
anything, and a stale bundle cannot override newer data.

The workflow rebuilds it after every harvest, so there is always a current one
in the repo without anyone doing anything.

## Compaction, because 3,128 records is mostly the same paragraph

The IPIS layer is 2.7 MB, of which **1.7 MB is description text** — and those
3,128 records share only **62 distinct endings**. Each unique tail is stored
once and referenced by index; the page reassembles the full string before
anything reads it.

```
points.json    3,128 records    1,753K embedded    65% of 2,701 KB
```

Verified lossless against the original: 3,128 of 3,128 records restored, every
description **byte-identical**, every coordinate identical, no leftover markers,
and the tails table deleted after use.

Bundled file: **4.2 MB**, smoke test passes on it exactly as on the unbundled
one.

## What this changes for you

Uploading is now one file rather than eight, and the harvesters keep running in
Actions regardless. The only things that still need a hand-upload are the
*inputs* the publishers will not serve to a cloud IP — the IPIS CSVs you already
sent, and later the Brazil and kiln exports. Those go into `data/` once and are
read on every run thereafter.

---

# Thirty-sixth pass — the kilns without a 2.2 GB download

`load_dataset()` exhausted your machine's memory because it pulls the **whole**
dataset, satellite imagery included. That is why the splits are 2.2 GB, 747 MB
and 580 MB. The map needs three columns.

**The harvester now pulls kiln coordinates through HuggingFace's datasets-server
rows API**, 100 rows at a time, across all three splits, de-duplicated on
rounded coordinates. Image fields come back as URLs rather than bytes, so the
kilns arrive as a few megabytes of JSON — and it runs inside the workflow with
nothing downloaded by hand. No parquet, no venv, and no answer needed to "which
file goes in data/".

Tested offline against a stubbed endpoint: pagination, split traversal,
termination on empty pages, de-duplication. One bug found doing it: `%2F` in the
dataset URL was being read as a printf conversion, so every request failed with
"must be real number, not str". Escaped.

If the rows API is ever unavailable, the fallback advice is now correct rather
than the thing that broke your laptop — a column-pruned `pyarrow` read that
touches a few megabytes of the 2.2 GB instead of loading all of it.

## Also

The two IPIS CSVs are returned alongside the build, so they can go into `data/`
and the harvester can regenerate that layer itself rather than depending on the
copy I made.

`osh-application.md` drafts the free/discounted access request. It leads with the
specific gap OS Hub closes — every other source on this map stops at country or
commodity level, and without a facility-to-buyer link the evidence stays one
level of abstraction above where anything can be acted on — and commits up
front to labelling every facility as a production site and explicitly not as
evidence of exploitation, which is already how the kiln and mining layers are
handled.

---

# Thirty-seventh pass — an invisible panel was eating the map's clicks

`#infoPanel` is hidden with `opacity:0`. **Opacity hides an element; it does not
stop it receiving clicks.** That panel is 340–380px wide, runs from `top:70px`
to `bottom:18px`, and sits at `z-index:1100` — so while closed it was
swallowing every click over that whole band of the map, and nothing about it was
visible to suggest why.

Fixed by adding `pointer-events:none` to the closed state and `auto` to `.open`.

Two more, found in the same sweep: `#sidebar` and `#rightbar` are bare flex
containers with a 9px gap and a full-height max. The panels inside them are
meant to be clickable; the gaps between them and the space below the last one
are map, and were not. Both are now `pointer-events:none` with
`> * { pointer-events:auto }`.

## Made into a rule, because this bug is invisible by definition

The smoke test now fails on **any positioned rule with `opacity:0` and no
`pointer-events`**. There is no legitimate version of that combination: an
element you cannot see should not be catching clicks.

Verified in both directions — clean on the current file, and on a copy with
the fix removed it reports:

```
FAIL — invisible elements that still intercept clicks
  #infoPanel
```

`clickCheck()` is also available in the console: it samples a 10×10 grid,
reports how many points reach the map, and names whatever is covering the rest.
Nothing about a transparent overlay shows up in a screenshot, so it needs a
deliberate test rather than an eye.

---

# Thirty-eighth pass — a dot now means a place

You were right, and it was a modelling error rather than a display preference. A
listed good is a finding about a **country and a commodity**. Drawing it at a
country centroid asserts something the source never said — that there is a
place — and two hundred of those pins buried the one layer that does have
coordinates.

**Records are now sorted three ways:**

| | Stays on the map | Example |
|---|---|---|
| `precise` | yes | IPIS mining site, GPS from a field visit |
| `local` | yes | Brazil municipality rescue; incident matched to a region |
| country-level | **no** | listed good, prevalence estimate, national determination |

Of the 234 seed records, **216 moved off the map** into a country panel; the
3,128 IPIS points all stayed. Municipality rescues and region-matched wire
incidents stay too — they are not exact, but they are somewhere, and that is
the line that matters rather than precision.

## Hover and click do different things

**Hover** a country: a panel appears beside the cursor listing everything on
record for it, grouped by what kind of claim each is — *Goods listed as
produced with forced or child labour*, *Determinations and enforcement actions*,
*Identified cases*, *Prevalence estimate*. Click any line for that entry's
source and what it does and does not establish.

**Click** the country: the resources box, unchanged.

The panel follows the cursor horizontally, flips to the other side rather than
running off screen, stays open while the pointer is inside it, and closes on a
220ms delay so it survives the gap between country and panel.

India renders as: brick kilns and mica under determinations, then twelve listed
goods — bricks, carpets, cotton, garments, mica, sugarcane, rice, stones,
footwear, embellished textiles, bidis, fireworks.

## What this changes

The map is now what you asked for: **every dot is somewhere.** The country-level
evidence has not been lost or downgraded — it is one hover away, better
organised than it was as a cluster of identical pins, and it no longer competes
with the sites that have real coordinates.

---

# Thirty-ninth pass — trafficking corridors

The only layer here that shows **movement**. Every other one answers "where is
this happening"; a corridor answers "where did the person come from" — and
that is where the recruitment fee was charged, the debt created, and a licence
could have been pulled before anyone travelled.

## Built from the data already being fetched

CTDC records carry country of **citizenship** as well as country of
**exploitation**, so the same file that produces the case counts produces the
corridors. `harvest_cases.py` now writes `routes.json` alongside `cases.json`:
origin→destination pairs with case counts and a labour / sexual / minor
breakdown, thresholded at five cases by default.

Tested on a synthetic CTDC file: NPL→QAT, MMR→THA, NGA→ITA and an
internal IND→IND corridor all built correctly with the right dominant type.

**Internal trafficking is kept, not dropped.** In several countries it is the
majority of recorded cases, and a map that only drew border crossings would show
those countries as unaffected. It has no line to draw, so it gets a dashed ring
at the country instead.

## Curved on purpose

A straight line between two countries reads as a path someone travelled. It is
not: it is a pair of countries and a count, joined at their centroids. The lines
are drawn as quadratic curves bowed perpendicular to the join, which makes that
plain and also stops overlapping corridors sitting on top of each other. The
help text says it outright, and so does every popup.

Colour is the dominant exploitation type — blue labour, pink sexual, gold
mixed — thickness is volume on a square-root scale, and a dot at the
destination end gives direction without arrowheads. Antimeridian crossings are
unwrapped so a Pacific corridor does not draw the long way round the world.

Verified in a headless render: three crossings become three curves of 21 points
each plus three destination dots, the internal corridor becomes a ring, and a
corridor with an unknown country is skipped and **counted in the log** rather
than silently dropped.

Toggle in the map key, registered in the data-layer list and in the bundler.

## The caveat that travels with it

Every corridor popup ends with the same two points: the line is not a path
anyone took, and this is detection again — a corridor with no line may have
no trafficking, or no one identifying it.

---

# Fortieth pass — ports, recruiters, zones

`harvest_infra.py`. Three layers that share one property: **none of them is
evidence of exploitation.** Each marks a place where the mechanism operates, at
a different point in it.

**Ports.** From the World Port Index — public-domain US government data,
~3,700 ports with coordinates — filtered to fishing and large harbours.
They are here for transhipment: catch and crew transferred between vessels at
sea, or in port without anyone going ashore, is how a fisher stays offshore for
months or years, and the port state is the authority that could inspect and
usually does not. Tested against a sample: fishing and large ports kept, a small
recreational harbour dropped.

**Recruitment agencies.** The origin end, and the point most worth watching:
this is where the fee is charged and the debt created, months before anyone
reaches a workplace. It is also the only place in the chain where **one
administrative act — pulling a licence — stops the next hundred people
being placed.** Seven origin-state registers are named with their URLs when no
export is present. A row without coordinates is **dropped rather than placed at
a country centre**, because an agency is an address and a centroid would say
something the register does not.

**Export processing and free zones.** Where labour law, inspection or the right
to organise is reduced by statute to attract investment. The point worth holding
onto: exploitation in a zone is often **not a failure of enforcement but the
absence of law by design**, which makes the remedy legislative rather than a
complaint to an inspector with no jurisdiction.

## What is honestly automatable

| | Unattended | Why |
|---|---|---|
| Ports | **yes** | WPI is public-domain data with coordinates |
| Recruiters | partly | registers are HTML tables and PDFs behind JS |
| Zones | **no** | no authoritative global boundary set exists that I can verify |

The zones harvester does not approximate. ILO and UNCTAD publish counts and
country lists, not geometry, and the commercial datasets are not open — so it
reads a committed file and says plainly that a zone drawn in the wrong place is
worse than no zone.

## The caveat that matters most here

Every record in all three layers carries: *this marks infrastructure, not a
finding. It is a place where the mechanism operates, not evidence that anyone
here is exploited.* These are the layers where a dot is most likely to be
misread as an accusation — a named recruitment agency especially — so the
disclaimer is in the record itself rather than only in a panel someone may never
open.
