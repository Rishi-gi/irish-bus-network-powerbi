"""
Pre-aggregates the journey data for the web preview dashboard.
Every file includes "All" rows (grouping sets) for Year, Region and ServiceType,
so the preview can filter without recalculating. Ratios use the same rules as the
DAX measures and are always re-computed from their parts, never averaged.
"""
from itertools import product
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D, OUT = ROOT / "data", ROOT / "preview"
OUT.mkdir(exist_ok=True)

f = pd.read_csv(D / "FactJourney.csv")
route = pd.read_csv(D / "DimRoute.csv")
date = pd.read_csv(D / "DimDate.csv")
cause = pd.read_csv(D / "DimLostKmCause.csv")
veh = pd.read_csv(D / "DimVehicle.csv")
veh["AgeBand"] = pd.cut(2025 - veh["YearIntroduced"], [-1, 3, 7, 11, 99],
                        labels=["0–3 yrs", "4–7 yrs", "8–11 yrs", "12+ yrs"]).astype(str)

f = (f.merge(route[["RouteKey", "RouteCode", "RouteName", "Region", "ServiceType"]], on="RouteKey")
      .merge(date[["DateKey", "Year", "YearMonth", "WeekdayNo", "WeekdayName"]], on="DateKey")
      .merge(cause[["CauseKey", "Cause", "CauseCategory"]], on="CauseKey")
      .merge(veh[["VehicleKey", "AgeBand"]], on="VehicleKey"))
f["Year"] = f["Year"].astype(str)
f["Operated"] = (f.StatusKey != 4).astype(int)
f["NotOperated"] = (f.StatusKey == 4).astype(int)
f["NonTracking"] = (f.StatusKey == 5).astype(int)
f["Tracked"] = f.DepartureDelayMins.notna().astype(int)
f["OnTime"] = f.DepartureDelayMins.between(-1, 5).astype(int)
f["BreakdownLost"] = f.LostKm.where(f.CauseKey == 2, 0.0)
f["Journeys"] = 1

DIMS = ["Year", "Region", "ServiceType"]
SUMS = ["Journeys", "Operated", "NotOperated", "NonTracking", "Tracked", "OnTime",
        "ScheduledKm", "LostKm", "Passengers", "BreakdownLost"]


def grouping_sets(df, extra, dims=DIMS):
    """Aggregate df by `extra` columns plus every All/specific combination of `dims`."""
    parts = []
    for mask in product([True, False], repeat=len(dims)):
        keep = [d for d, k in zip(dims, mask) if k]
        if keep + extra:
            g = df.groupby(keep + extra, observed=True)[SUMS].sum().reset_index()
        else:
            g = df[SUMS].sum().to_frame().T
        for d, k in zip(dims, mask):
            if not k:
                g[d] = "All"
        for col in ["Journeys", "Operated", "NotOperated", "NonTracking", "Tracked", "OnTime", "Passengers"]:
            g[col] = g[col].astype(int)
        parts.append(g)
    return pd.concat(parts, ignore_index=True)


def ratios(t):
    t["LostKmPct"] = (t.LostKm / t.ScheduledKm).round(4)
    t["PunctualityPct"] = (t.OnTime / t.Tracked).round(4)
    t["AVLTrackingPct"] = (1 - t.NonTracking / t.Operated).round(4)
    t["ScheduledKm"] = t.ScheduledKm.round(0).astype(int)
    t["LostKm"] = t.LostKm.round(0).astype(int)
    return t


# 1. headline KPIs, with the previous year for Year = 2025
kpi = ratios(grouping_sets(f, []))
prev = kpi[kpi.Year == "2024"][["Region", "ServiceType", "LostKmPct", "PunctualityPct", "AVLTrackingPct"]]
prev = prev.rename(columns=lambda c: c + "PY" if c.endswith("Pct") else c).assign(Year="2025")
kpi = kpi.merge(prev, on=DIMS, how="left")
kpi = kpi[DIMS + ["Journeys", "NotOperated", "ScheduledKm", "LostKm", "Passengers",
                  "LostKmPct", "PunctualityPct", "AVLTrackingPct",
                  "LostKmPctPY", "PunctualityPctPY", "AVLTrackingPctPY"]]
kpi.to_csv(OUT / "kpi.csv", index=False)

# 2. monthly trend (Year kept as a column so the page can show one year or both)
trend = ratios(grouping_sets(f, ["YearMonth"], ["Region", "ServiceType"]))
trend["Year"] = trend.YearMonth.str[:4]
trend[["YearMonth", "Year", "Region", "ServiceType", "ScheduledKm", "LostKm",
       "LostKmPct", "PunctualityPct", "AVLTrackingPct"]].to_csv(OUT / "trend.csv", index=False)

# 3. lost km by cause
c = grouping_sets(f[f.LostKm > 0], ["Cause", "CauseCategory"])
c["LostKm"] = c.LostKm.round(0).astype(int)
c["Share"] = (c.LostKm / c.groupby(DIMS).LostKm.transform("sum")).round(4)
c[DIMS + ["Cause", "CauseCategory", "LostKm", "Share"]].to_csv(OUT / "cause.csv", index=False)

# 4. punctuality heatmap: time band x weekday
order = {"Early": 1, "AM Peak": 2, "Interpeak": 3, "PM Peak": 4, "Evening": 5}
h = grouping_sets(f[f.Tracked == 1], ["TimeBand", "WeekdayNo", "WeekdayName"])
h["TimeBandOrder"] = h.TimeBand.map(order)
h["PunctualityPct"] = (h.OnTime / h.Tracked).round(4)
h = h.rename(columns={"WeekdayName": "Weekday"})
h[DIMS + ["TimeBand", "TimeBandOrder", "WeekdayNo", "Weekday", "Tracked", "PunctualityPct"]] \
    .to_csv(OUT / "heat.csv", index=False)

# 5. breakdown lost km per 1,000 scheduled km by vehicle age band
a = grouping_sets(f, ["AgeBand"])
a["BreakdownPer1000Km"] = (a.BreakdownLost / a.ScheduledKm * 1000).round(2)
a[DIMS + ["AgeBand", "BreakdownPer1000Km"]].to_csv(OUT / "age.csv", index=False)

# 6. route table by year (and All years)
r = pd.concat([f.groupby(["Year", "RouteCode", "RouteName", "Region", "ServiceType"])[SUMS].sum().reset_index(),
               f.groupby(["RouteCode", "RouteName", "Region", "ServiceType"])[SUMS].sum().reset_index().assign(Year="All")])
r = ratios(r)
r[["Year", "RouteCode", "RouteName", "Region", "ServiceType", "Journeys", "LostKm", "LostKmPct",
   "PunctualityPct", "AVLTrackingPct", "Passengers"]].to_csv(OUT / "routes.csv", index=False)

for p in sorted(OUT.glob("*.csv")):
    print(p.name, sum(1 for _ in open(p)) - 1, "rows", p.stat().st_size, "bytes")
