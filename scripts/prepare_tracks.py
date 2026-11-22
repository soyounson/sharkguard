"""Satellite-tag shark tracks (ERDDAP CSV) -> data/tracks.json for the map.

Works with either ATN ERDDAP export:
  - stanford_import_ssm_public  (TOPP state-space tracks): common_name, topp_id, time, latitude, longitude
  - atn_collection              (ATN Argos locations):     taxon_name, deploy_id, time, latitude, longitude

Usage: python3 prepare_tracks.py input1.csv [input2.csv ...] data/tracks.json
"""
import csv
import json
import sys
from collections import defaultdict

# species keyword -> (species key, map group)
SPECIES = [
    (("white shark", "carcharodon"), ("white", "white")),
    (("salmon shark", "lamna ditropis"), ("salmon", "pelagic")),
    (("thresher", "alopias"), ("thresher", "pelagic")),
    (("hammerhead", "sphyrna"), ("hammerhead", "pelagic")),
    (("leopard shark", "triakis"), ("leopard", "coastal")),
    (("sevengill", "notorynchus"), ("sevengill", "coastal")),
]
BBOX = dict(lat=(30.0, 44.0), lon=(-128.5, -114.5))  # California coast and a margin around the map


def classify(name):
    n = (name or "").lower()
    for keys, val in SPECIES:
        if any(k in n for k in keys):
            return val
    return None


*inputs, out = sys.argv[1:]
tracks = defaultdict(dict)  # (species, id) -> {date: (lat, lon)}
meta = {}
juv = set()
sources = set()
for path in inputs:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if rows and rows[0].get("latitude", "").strip() in ("degrees_north", ""):
        rows = rows[1:]  # ERDDAP puts a units row under the header
    for r in rows:
        name = r.get("common_name") or r.get("taxon_name") or ""
        cls = classify(name)
        if not cls:
            continue
        try:
            lat, lon = float(r["latitude"]), float(r["longitude"])
        except (KeyError, ValueError):
            continue
        if lon > 180:
            lon -= 360
        if not (BBOX["lat"][0] <= lat <= BBOX["lat"][1] and BBOX["lon"][0] <= lon <= BBOX["lon"][1]):
            continue
        tid = (r.get("topp_id") or r.get("deploy_id") or r.get("ptt") or "?").strip()
        day = r["time"][:10]
        tracks[(cls[0], tid)][day] = (round(lat, 3), round(lon, 3))  # one point per day (last one wins)
        meta[(cls[0], tid)] = cls
        if "juvenile" in name.lower():
            juv.add((cls[0], tid))
        sources.add("TOPP" if "topp_id" in r else "ATN")

result = []
for key, days in tracks.items():
    if len(days) < 5:
        continue
    sp, group = meta[key]
    pts = [[d, *days[d]] for d in sorted(days)]
    result.append({"id": key[1], "species": sp, "group": group, "juvenile": key in juv, "pts": pts})

json.dump({"source": " / ".join(sorted(sources)) + " satellite tags via U.S. Animal Telemetry Network",
           "tracks": result}, open(out, "w"))
by = defaultdict(int)
for t in result:
    by[t["species"]] += 1
print(f"{len(result)} tracks:", dict(by), "| points:", sum(len(t["pts"]) for t in result))
