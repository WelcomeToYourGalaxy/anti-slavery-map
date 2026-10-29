# Brief: data for the five context overlays

The anti-slavery map (forced labour, trafficking, child labour) has five context overlays that were listed but never
built. Each colours countries (or draws lines) to show context. Build the data from official published sources you open
yourself. No fabrication: every value must come from a source you opened; leave a country out rather than guess.

Output for each overlay: one JSON file in /home/claude/anti-slavery-map/data/overlays/ named `<key>.json`:
```json
{"k": "<key>", "label": "...", "source": "name of the publication", "url": "...", "as_of": "year or date of the data",
 "method": "one or two plain sentences: what the value is and how it was counted",
 "countries": {"ISO3": {"v": <number or category string>, "text": "one plain line shown in the box", "url": "optional page for this country"}},
 "lines": [ {"from": "ISO3", "to": "ISO3", "v": <number or null>, "text": "...", "url": "..."} ]   (corridors only)
}
```
Use ISO 3166-1 alpha-3 codes. Validate with python3 json.load. Do not edit any other file. Report what you built,
how many countries, and anything you could not confirm.
