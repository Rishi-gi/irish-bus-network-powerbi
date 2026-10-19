"""
Builds the derived outputs from the generated CSVs, using the same business
rules as the DAX measures:
  * docs/05-expected-results.md      – numbers to check your Power BI build against
  * data/paginated/*.csv             – monthly aggregates for the offline paginated report
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
f = pd.read_csv(D / "FactJourney.csv")
route = pd.read_csv(D / "DimRoute.csv")
veh = pd.read_csv(D / "DimVehicle.csv")
cause = pd.read_csv(D / "DimLostKmCause.csv")
date = pd.read_csv(D / "DimDate.csv")
sec = pd.read_csv(D / "SecurityUserRegion.csv")

TARGET_LOST, TARGET_PUNCT, TARGET_AVL = 0.02, 0.90, 0.98

f = f.merge(route[["RouteKey", "RouteCode", "RouteName", "Region", "ServiceType", "Depot"]], on="RouteKey")
f = f.merge(date[["DateKey", "Year", "YearMonth", "WeekdayNo"]], on="DateKey")
f = f.merge(cause[["CauseKey", "Cause", "CauseCategory"]], on="CauseKey")
veh["AgeBand"] = pd.cut(2025 - veh["YearIntroduced"], [-1, 3, 7, 11, 99],
                        labels=["0–3 years", "4–7 years", "8–11 years", "12+ years"]).astype(str)
f = f.merge(veh[["VehicleKey", "AgeBand"]], on="VehicleKey")

f["Operated"] = (f.StatusKey != 4).astype(int)
f["NotOperated"] = (f.StatusKey == 4).astype(int)
f["NonTracking"] = (f.StatusKey == 5).astype(int)
f["Tracked"] = f.DepartureDelayMins.notna().astype(int)
f["OnTime"] = f.DepartureDelayMins.between(-1, 5).astype(int)
f["BreakdownLost"] = f.LostKm.where(f.CauseKey == 2, 0)


def kpis(g):
    s = g[["Operated", "NotOperated", "NonTracking", "Tracked", "OnTime",
           "ScheduledKm", "OperatedKm", "LostKm", "Passengers"]].sum()
    return {
        "Scheduled Journeys": len(g), "Operated Journeys": int(s.Operated),
        "Journeys Not Operated": int(s.NotOperated), "Scheduled Km": s.ScheduledKm,
        "Operated Km": s.OperatedKm, "Lost Km": s.LostKm,
        "Lost Km %": s.LostKm / s.ScheduledKm,
        "Tracked Departures": int(s.Tracked), "On-Time Departures": int(s.OnTime),
        "Punctuality %": s.OnTime / s.Tracked if s.Tracked else None,
        "Non-Tracking Journeys": int(s.NonTracking),
        "AVL Tracking Rate %": 1 - s.NonTracking / s.Operated if s.Operated else None,
        "Passengers": int(s.Passengers),
    }


def fmt(k, v):
    if v is None:
        return "(blank)"
    if k.endswith("%"):
        return f"{v * 100:.2f}%" if "Lost" in k else f"{v * 100:.1f}%"
    if isinstance(v, float):
        return f"{v:,.0f}" if abs(v - round(v)) > 1e-9 or True else f"{v:,}"
    return f"{v:,}"


def table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


md = ["# Expected results – check your build", "",
      "Calculated directly from the CSVs with the same rules as the DAX measures. "
      "If a card in Power BI shows a different number, check the relationship, the data types in Power Query, "
      "and that `DimDate` is marked as the date table. Lost km figures are rounded to whole km.", ""]

net = kpis(f)
md += ["## 1. Whole period (1 Jan 2024 – 31 Dec 2025), no filters", "",
       table([(k, fmt(k, v)) for k, v in net.items()], ["Measure", "Expected value"]), ""]

show = ["Scheduled Journeys", "Scheduled Km", "Lost Km", "Lost Km %", "Punctuality %", "AVL Tracking Rate %", "Passengers"]
yr = {y: kpis(g) for y, g in f.groupby("Year")}
md += ["## 2. By year (Year slicer)", "",
       table([[y] + [fmt(k, yr[y][k]) for k in show] for y in yr], ["Year"] + show), "",
       f"`Lost Km % YoY Change (pp)` with Year = 2025 selected: **{(yr[2025]['Lost Km %'] - yr[2024]['Lost Km %']) * 100:+.2f} percentage points**.", ""]

rg = {r: kpis(g) for r, g in f.groupby("Region")}
md += ["## 3. By region, whole period (also the RLS test values)", "",
       table([[r] + [fmt(k, rg[r][k]) for k in show] for r in sorted(rg)], ["Region"] + show), ""]

rls = []
for user, g in sec.groupby("UserEmail"):
    regs = sorted(g.Region)
    rls.append((user, ", ".join(regs) if len(regs) < 6 else "All six", f"{int(f.Region.isin(regs).sum()):,}"))
rls.append(("someone.else@example.com", "none", "(blank)"))
md += ["### RLS: Scheduled Journeys when viewing as each user (dynamic role)", "",
       table(rls, ["View as", "Regions visible", "Scheduled Journeys"]), ""]

ym = {m: kpis(g) for m, g in f.groupby("YearMonth")}
months = sorted(ym)
rows = []
for i, m in enumerate(months):
    k = ym[m]
    mom = "" if i == 0 else f"{(k['Lost Km'] - ym[months[i - 1]]['Lost Km']) / ym[months[i - 1]]['Lost Km'] * 100:+.1f}%"
    rows.append((m, fmt("Lost Km", k["Lost Km"]), fmt("Lost Km %", k["Lost Km %"]), mom,
                 fmt("Punctuality %", k["Punctuality %"]), fmt("AVL Tracking Rate %", k["AVL Tracking Rate %"])))
md += ["## 4. By month (network)", "",
       table(rows, ["YearMonth", "Lost Km", "Lost Km %", "Lost Km MoM %", "Punctuality %", "AVL Tracking Rate %"]), ""]

top = f.groupby(["RouteCode", "RouteName"]).agg(LostKm=("LostKm", "sum"), Sched=("ScheduledKm", "sum")).reset_index()
top["pct"] = top.LostKm / top.Sched
top = top.sort_values("LostKm", ascending=False).head(5)
md += ["## 5. Top 5 routes by Lost Km (whole period)", "",
       table([(i + 1, f"{r.RouteCode} · {r.RouteName}", f"{r.LostKm:,.0f}", f"{r.pct * 100:.2f}%")
              for i, r in enumerate(top.itertuples())], ["Rank", "Route", "Lost Km", "Lost Km %"]), ""]

cz = f[f.LostKm > 0].groupby(["Cause", "CauseCategory"]).LostKm.sum().sort_values(ascending=False)
tot = cz.sum()
md += ["## 6. Lost km by cause (whole period)", "",
       table([(c, cat, f"{v:,.0f}", f"{v / tot * 100:.1f}%") for (c, cat), v in cz.items()],
             ["Cause", "Category", "Lost Km", "Share of Lost Km %"]), "",
       f"`Top Cause of Lost Km` with no filters: **{cz.index[0][0]}**. "
       f"`Internal Share of Lost Km %`: **{cz[cz.index.get_level_values(1) == 'Internal'].sum() / tot * 100:.1f}%**.", ""]

ab = f.groupby("AgeBand").agg(b=("BreakdownLost", "sum"), s=("ScheduledKm", "sum"))
ab["v"] = ab.b / ab.s * 1000
order = ["0–3 years", "4–7 years", "8–11 years", "12+ years"]
md += ["## 7. Breakdown Lost Km per 1,000 Km by vehicle age band", "",
       table([(a, f"{ab.loc[a, 'v']:.2f}") for a in order], ["AgeBand", "Breakdown Lost Km per 1,000 Km"]), ""]

nw = f[f.Region == "North-West"]
pre, post = kpis(nw[nw.YearMonth < "2025-06"]), kpis(nw[nw.YearMonth >= "2025-06"])
md += ["## 8. Data-quality check: North-West AVL upgrade", "",
       f"AVL Tracking Rate % in North-West: **{pre['AVL Tracking Rate %'] * 100:.1f}%** Jan 2024 – May 2025, "
       f"**{post['AVL Tracking Rate %'] * 100:.1f}%** Jun – Dec 2025.", ""]
(ROOT / "docs" / "05-expected-results.md").write_text("\n".join(md), encoding="utf-8")

# ---------------------------------------------------------- paginated CSVs
P = D / "paginated"
P.mkdir(exist_ok=True)
agg = dict(ScheduledJourneys=("JourneyID", "count"), JourneysNotOperated=("NotOperated", "sum"),
           OperatedJourneys=("Operated", "sum"), NonTrackingJourneys=("NonTracking", "sum"),
           ScheduledKm=("ScheduledKm", "sum"), LostKm=("LostKm", "sum"),
           TrackedDepartures=("Tracked", "sum"), OnTimeDepartures=("OnTime", "sum"),
           Passengers=("Passengers", "sum"))


def add_pcts(t):
    t["LostKmPct"] = (t.LostKm / t.ScheduledKm).round(4)
    t["PunctualityPct"] = (t.OnTimeDepartures / t.TrackedDepartures).round(4)
    t["AVLTrackingPct"] = (1 - t.NonTrackingJourneys / t.OperatedJourneys).round(4)
    t["ScheduledKm"] = t.ScheduledKm.round(1)
    t["LostKm"] = t.LostKm.round(1)
    return t


rm = add_pcts(f.groupby(["YearMonth", "Region", "RouteCode", "RouteName", "ServiceType"]).agg(**agg).reset_index())
rm.to_csv(P / "MonthlyRouteSummary.csv", index=False)
cm = (f[f.LostKm > 0].groupby(["YearMonth", "Region", "Cause", "CauseCategory"]).LostKm.sum().round(1).reset_index())
cm.to_csv(P / "MonthlyCauseSummary.csv", index=False)
reg = add_pcts(f.groupby(["YearMonth", "Region"]).agg(**agg).reset_index())
topc = (f[f.LostKm > 0].groupby(["YearMonth", "Region", "Cause"]).LostKm.sum().reset_index()
        .sort_values("LostKm", ascending=False).drop_duplicates(["YearMonth", "Region"]))
reg = reg.merge(topc[["YearMonth", "Region", "Cause"]].rename(columns={"Cause": "TopCause"}), how="left")
reg["TopCause"] = reg.TopCause.fillna("none")
reg["Commentary"] = [
    f"{pd.Timestamp(r.YearMonth + '-01'):%B %Y}: {r.LostKm:,.0f} km lost ({r.LostKmPct * 100:.2f}% of scheduled; "
    f"target 2.0%). Punctuality {r.PunctualityPct * 100:.1f}% against a 90% target. "
    f"Largest cause of lost km: {r.TopCause}."
    for r in reg.itertuples()]
reg.to_csv(P / "MonthlyRegionSummary.csv", index=False)

print("network:", {k: fmt(k, v) for k, v in net.items()})
