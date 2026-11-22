"""CDFW 상어 사고 데이터를 정리해 웹페이지용 JSON으로 만든다.

입력: CDFW SharkIncidents_1950_2022_220302.xlsx (시트 Attacks_1950_2021)
출력: data/incidents.json (사건 목록 + 위치 묶음)
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
CLUSTER_KM = 12  # 이 거리 안의 사건은 한 지점으로 묶는다 (원본 좌표는 표시용 근사치)

df = pd.read_excel(SRC, sheet_name="Attacks_1950_2021")
df = df[pd.to_numeric(df["IncidentNum"], errors="coerce").notna()].copy()  # 'NOT COUNTED' 등 제외
df["IncidentNum"] = df["IncidentNum"].astype(int)
df["Date"] = pd.to_datetime(df["Date"])
for c in ["County", "Location", "Mode", "Injury", "Species", "Comment", "Depth"]:
    df[c] = df[c].fillna("").astype(str).str.strip()
df["Injury"] = df["Injury"].str.lower()


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


# 간단한 탐욕적 묶기: 사건 수가 많은 곳부터 중심을 잡는다
pts = df[["Latitude", "Longitude"]].to_numpy().tolist()
order = sorted(range(len(pts)), key=lambda i: -sum(km(pts[i], p) < CLUSTER_KM for p in pts))
cid = [-1] * len(pts)
centers = []
for i in order:
    if cid[i] != -1:
        continue
    k = len(centers)
    members = [j for j in range(len(pts)) if cid[j] == -1 and km(pts[i], pts[j]) < CLUSTER_KM]
    for j in members:
        cid[j] = k
    centers.append(members)
df["cluster"] = cid

clusters = []
for k, members in enumerate(centers):
    sub = df.iloc[members]
    name = sub["Location"].value_counts().index[0]
    clusters.append({
        "id": k,
        "name": name,
        "county": sub["County"].value_counts().index[0],
        "lat": round(sub["Latitude"].mean(), 4),
        "lon": round(sub["Longitude"].mean(), 4),
        "n": len(sub),
        "injury": sub["Injury"].value_counts().to_dict(),
    })

incidents = [{
    "id": int(r.IncidentNum),
    "date": r.Date.strftime("%Y-%m-%d"),
    "year": r.Date.year,
    "month": r.Date.month,
    "county": r.County,
    "location": r.Location,
    "mode": r.Mode,
    "injury": r.Injury,
    "species": r.Species,
    "depth": r.Depth,
    "comment": r.Comment,
    "lat": round(float(r.Latitude), 4),
    "lon": round(float(r.Longitude), 4),
    "cluster": int(r.cluster),
} for r in df.itertuples()]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"incidents": incidents, "clusters": clusters}, ensure_ascii=False))
print(f"{len(incidents)} incidents -> {len(clusters)} clusters; max n = {max(c['n'] for c in clusters)}")
print(df["Injury"].value_counts().to_dict())
