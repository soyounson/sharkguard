# SharkGuard California

Check shark history and a seasonal risk score for a California beach before you surf, swim, dive or paddle.

**Live site:** https://soyounson.github.io/sharkguard/

## What it does

- **Check a spot**: pick a beach and a date. The page shows a 0–100 seasonal score (green 0–49, yellow 50–74, red 75–100), a short "Heads up" memo, the score for every month, and nearby incidents since 2000.
- **Relief map**: NASA shaded relief and seafloor, light/dark theme, filters for activity and injury. Rings show incidents per stretch of coast for the selected season; zoom in to see each incident (color = injury, icon = activity, badge = shark group).
- **Shark movement by season**: white, salmon and thresher sharks replay real satellite-tag tracks (TOPP, 2002–2013). Leopard, sevengill and hammerhead paths are illustrative, based on published seasonal patterns.
- **3D opener**: a procedurally modeled white shark in three.js, animated on the GPU.

## Risk score (provisional)

For the chosen spot and month: λ = incidents within 40 km in that month ±1 (2000 – Feb 2022) ÷ 3 ÷ 22.2 years.
Score = 100 × √(λ ÷ λmax), where λmax is the highest value at any incident site in any month.
Historical pattern only. It is not a prediction and does not guarantee safety.

## Project layout

```
index.html                 SharkGuard site
dashboard.html             personal analysis dashboard (cross-filtered charts)
data/incidents.json        CDFW incidents, cleaned and grouped (scripts/prepare_data.py)
data/tracks.json           satellite-tag tracks for the map (scripts/prepare_tracks.py)
data/geo.json              coastline and state outlines
data/raw/                  original tag CSV (ATN ERDDAP export)
assets/relief.jpg          NASA Blue Marble shaded relief + bathymetry, zoom 8 tiles stitched
assets/emoji/              Twemoji SVGs (shark icons recolored for species groups)
scripts/                   data preparation (Python)
WORKFLOW.md                working notes, decisions and feedback log
```

## Rebuild the data

```
python3 scripts/prepare_data.py SharkIncidents_1950_2022_220302.xlsx data/incidents.json
python3 scripts/prepare_tracks.py data/raw/topp_ssm_sharks_california.csv data/tracks.json
```

Run locally with any static server, for example `python3 -m http.server`, then open http://localhost:8000.

## Data and credits

- Incidents: California Department of Fish and Wildlife (CDFW), Shark Incident Database, 1950 – Feb 2022.
- Shark tracks: TOPP (Tagging of Pacific Predators) state-space tracks, `stanford_import_ssm_public`, via the U.S. Animal Telemetry Network (ATN). Free to use and redistribute.
- Relief map: NASA Blue Marble shaded relief and bathymetry (NASA Earth Observatory), tiles via FreeTiler.
- Coastline: US Census (us-atlas), Natural Earth (world-atlas).
- Emoji: Twemoji, CC BY 4.0. Shark group icons are recolored Twemoji.
- Libraries: D3, Apache ECharts, three.js.

**For reference only.** This site shows historical records and general seasonal patterns. It does not predict where sharks are now and does not guarantee anyone's safety. Always follow local beach postings and lifeguard advice.
