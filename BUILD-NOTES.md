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
