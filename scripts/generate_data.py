"""
Synthetic data generator for the Irish Regional Bus Network Performance project.

Every row is generated. No real operator data, timetables, vehicles or people
are used. Route names use Irish place names only to make the scenario realistic.

Run:  python generate_data.py          (writes CSVs to ../data)
Seed is fixed, so the output is reproducible.
"""
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(2026)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

START, END = date(2024, 1, 1), date(2025, 12, 31)

# ---------------------------------------------------------------- DimDate
BANK_HOLIDAYS = {
    date(2024, 1, 1), date(2024, 2, 5), date(2024, 3, 17), date(2024, 3, 18),
    date(2024, 4, 1), date(2024, 5, 6), date(2024, 6, 3), date(2024, 8, 5),
    date(2024, 10, 28), date(2024, 12, 25), date(2024, 12, 26),
    date(2025, 1, 1), date(2025, 2, 3), date(2025, 3, 17), date(2025, 4, 21),
    date(2025, 5, 5), date(2025, 6, 2), date(2025, 8, 4), date(2025, 10, 27),
    date(2025, 12, 25), date(2025, 12, 26),
}
# Simulated severe-weather days (red/orange warning style disruption)
STORM_DAYS = {date(2024, 1, 21): 0.35, date(2024, 12, 7): 0.30,
              date(2025, 1, 24): 0.85, date(2025, 1, 25): 0.30,
              date(2025, 11, 20): 0.15}

days = [START + timedelta(d) for d in range((END - START).days + 1)]
dim_date = pd.DataFrame({"Date": pd.to_datetime(days)})
d = dim_date["Date"]
dim_date["DateKey"] = d.dt.strftime("%Y%m%d").astype(int)
dim_date["Year"] = d.dt.year
dim_date["Quarter"] = "Q" + d.dt.quarter.astype(str)
dim_date["MonthNo"] = d.dt.month
dim_date["MonthName"] = d.dt.strftime("%b")
dim_date["YearMonth"] = d.dt.strftime("%Y-%m")
dim_date["MonthStart"] = d.dt.to_period("M").dt.start_time
dim_date["WeekdayNo"] = d.dt.weekday + 1          # 1 = Monday
dim_date["WeekdayName"] = d.dt.strftime("%a")
dim_date["IsBankHoliday"] = [x in BANK_HOLIDAYS for x in days]
dim_date["DayType"] = np.where(
    dim_date["IsBankHoliday"] | (dim_date["WeekdayNo"] == 7), "Sunday / Bank Holiday",
    np.where(dim_date["WeekdayNo"] == 6, "Saturday", "Weekday"))
dim_date = dim_date[["DateKey", "Date", "Year", "Quarter", "MonthNo", "MonthName",
                     "YearMonth", "MonthStart", "WeekdayNo", "WeekdayName",
                     "IsBankHoliday", "DayType"]]

# ---------------------------------------------------------------- DimRoute
# (route code, name, service type, depot, region, km per trip, weekday trips per direction)
ROUTES = [
    ("SC01", "Cork City Centre – Ballincollig", "City", "Cork City", "South", 13, 16),
    ("SC02", "Cork City Centre – Douglas", "City", "Cork City", "South", 9, 16),
    ("SC03", "Cork Kent Station – Mahon Point", "City", "Cork City", "South", 11, 14),
    ("SR04", "Cork – Killarney", "Regional", "Cork City", "South", 88, 5),
    ("SM05", "Cork – Midleton", "Commuter", "Cork City", "South", 24, 12),
    ("WC01", "Galway City – Knocknacarra", "City", "Galway", "West", 10, 15),
    ("WC02", "Galway City – Ballybrit", "City", "Galway", "West", 8, 14),
    ("WR03", "Galway – Clifden", "Regional", "Galway", "West", 79, 4),
    ("WM04", "Galway – Athenry", "Commuter", "Galway", "West", 26, 10),
    ("MC01", "Limerick City – Castletroy", "City", "Limerick", "Mid-West", 9, 15),
    ("MT02", "Ennis Town Service", "Town", "Ennis", "Mid-West", 10, 10),
    ("MR03", "Limerick – Tralee", "Regional", "Limerick", "Mid-West", 104, 5),
    ("MM04", "Limerick – Nenagh", "Commuter", "Limerick", "Mid-West", 40, 9),
    ("EC01", "Waterford City – Ardkeen", "City", "Waterford", "South-East", 8, 13),
    ("ET02", "Kilkenny Town Service", "Town", "Kilkenny", "South-East", 9, 10),
    ("ER03", "Waterford – Wexford", "Regional", "Waterford", "South-East", 82, 5),
    ("EM04", "Waterford – Tramore", "Commuter", "Waterford", "South-East", 13, 11),
    ("NT01", "Sligo Town Service", "Town", "Sligo", "North-West", 8, 9),
    ("NR02", "Sligo – Letterkenny", "Regional", "Sligo", "North-West", 115, 4),
    ("NR03", "Letterkenny – Derry Road Link", "Regional", "Letterkenny", "North-West", 36, 6),
    ("DM01", "Drogheda – Dublin City", "Commuter", "Drogheda", "East", 52, 14),
    ("DM02", "Navan – Dublin City", "Commuter", "Navan", "East", 49, 14),
    ("DT03", "Drogheda Town Service", "Town", "Drogheda", "East", 9, 10),
    ("DR04", "Dundalk – Dublin Airport", "Regional", "Drogheda", "East", 75, 7),
]
dim_route = pd.DataFrame(ROUTES, columns=["RouteCode", "RouteName", "ServiceType", "Depot",
                                          "Region", "KmPerTrip", "WeekdayTripsPerDirection"])
dim_route.insert(0, "RouteKey", range(1, len(dim_route) + 1))

# ---------------------------------------------------------------- DimVehicle
VTYPES = {
    "City": [("Double-deck", "Diesel", .55), ("Single-deck", "Diesel", .25), ("Single-deck", "Battery electric", .20)],
    "Town": [("Single-deck", "Diesel", .6), ("Single-deck", "Hybrid", .4)],
    "Commuter": [("Double-deck", "Diesel", .5), ("Coach", "Diesel", .5)],
    "Regional": [("Coach", "Diesel", 1.0)],
}
vrows, fleet = [], 100
depot_fleet = {}
for depot, grp in dim_route.groupby("Depot"):
    keys = []
    for stype, g2 in grp.groupby("ServiceType"):
        n = int(g2["WeekdayTripsPerDirection"].sum() / 2.2) + 3
        opts = VTYPES[stype]
        for _ in range(n):
            vt = opts[RNG.choice(len(opts), p=[o[2] for o in opts])]
            yr = int(RNG.integers(2023, 2026)) if vt[1] == "Battery electric" else int(RNG.integers(2010, 2025))
            fleet += 1
            vrows.append((len(vrows) + 1, f"FV{fleet}", vt[0], vt[1], yr, depot, stype))
            keys.append((len(vrows), stype, yr))
    depot_fleet[depot] = keys
dim_vehicle = pd.DataFrame(vrows, columns=["VehicleKey", "FleetNumber", "VehicleType", "FuelType",
                                           "YearIntroduced", "HomeDepot", "AllocatedService"])

# ---------------------------------------------------------------- Dim status / cause
dim_status = pd.DataFrame([
    (1, "Operated in full", "Operated", True, False),
    (2, "Partially operated", "Operated", True, True),
    (3, "Stops bypassed", "Operated", True, True),
    (4, "Not operated", "Not operated", False, True),
    (5, "Operated - AVL non-tracking", "Operated", True, False),
], columns=["StatusKey", "JourneyStatus", "StatusGroup", "IsOperated", "IsLostService"])

dim_cause = pd.DataFrame([
    (0, "No issue", "None", False),
    (1, "Driver availability", "Internal", True),
    (2, "Vehicle defect / breakdown", "Internal", True),
    (3, "Traffic congestion", "External", True),
    (4, "Road works / diversion", "External", True),
    (5, "Severe weather", "External", True),
    (6, "Road traffic incident", "External", True),
    (7, "AVL / GPS data issue", "Data quality", False),
], columns=["CauseKey", "Cause", "CauseCategory", "CountsAsLostKm"])

# ---------------------------------------------------------------- Security table (dynamic RLS)
REGIONS = ["South", "West", "Mid-West", "South-East", "North-West", "East"]
sec = [(f"manager.{r.lower().replace('-', '')}@example.com", r) for r in REGIONS]
sec += [("head.of.operations@example.com", r) for r in REGIONS]
sec += [("analyst.southwest@example.com", r) for r in ["South", "West"]]
dim_security = pd.DataFrame(sec, columns=["UserEmail", "Region"])

# ---------------------------------------------------------------- FactJourney
REGION_FACTORS = {  # cancel, congestion, avl_gap
    "South": (1.0, 1.15, 1.0), "West": (0.9, 1.0, 1.0), "Mid-West": (1.1, 0.95, 1.0),
    "South-East": (0.85, 0.85, 0.9), "North-West": (1.25, 0.7, 3.2), "East": (1.2, 1.45, 1.1),
}
AVL_UPGRADE = pd.Timestamp("2025-06-01")   # North-West tracking equipment upgrade
TYPE_BASE = {  # cancel prob, partial prob, bypass prob, delay mean, passengers mean
    "City": (0.010, 0.012, 0.014, 1.6, 34), "Town": (0.008, 0.006, 0.006, 0.9, 16),
    "Commuter": (0.011, 0.010, 0.008, 2.4, 38), "Regional": (0.009, 0.014, 0.004, 3.0, 27),
}
PEAK = {7: 1.5, 8: 1.7, 9: 1.2, 16: 1.3, 17: 1.6, 18: 1.4}


def month_factor(m):
    return {1: 1.25, 2: 1.2, 3: 1.05, 4: 0.95, 5: 0.9, 6: 0.85, 7: 0.85, 8: 0.85,
            9: 1.05, 10: 1.1, 11: 1.2, 12: 1.3}[m]


def timetable(n_per_dir, stype):
    first, last = (6.5, 23.0) if stype in ("City", "Town") else (6.0, 21.0)
    if stype == "Regional":
        first, last = 7.0, 19.5
    t = np.linspace(first, last, n_per_dir)
    return [round(x * 60 / 5) * 5 for x in t]   # minutes past midnight, 5-min grid


rows = []
jid = 0
for _, r in dim_route.iterrows():
    stype, region = r.ServiceType, r.Region
    cfac, gfac, afac = REGION_FACTORS[region]
    pc, pp, pb, dmean, pax = TYPE_BASE[stype]
    vehicles = [v for v in depot_fleet[r.Depot] if v[1] == stype]
    full_tt = timetable(r.WeekdayTripsPerDirection, stype)
    for day in days:
        ts = pd.Timestamp(day)
        dt = "Sunday" if (day in BANK_HOLIDAYS or day.weekday() == 6) else (
            "Saturday" if day.weekday() == 5 else "Weekday")
        keep = {"Weekday": 1, "Saturday": 2, "Sunday": 3}[dt]   # every Nth departure
        tt = full_tt[::keep]
        mf = month_factor(day.month)
        storm = STORM_DAYS.get(day, 0.0)
        # driver shortage: early 2025 and late 2024 pressure
        driver = 1.0
        if ts >= pd.Timestamp("2024-10-01") and ts < pd.Timestamp("2025-04-01"):
            driver = 1.9 if region in ("East", "South") else 1.4
        school = 1.0 if day.month in (7, 8) else 1.15
        for direction in ("Outbound", "Inbound"):
            for mins in tt:
                jid += 1
                hour = mins // 60
                veh = vehicles[RNG.integers(len(vehicles))]
                age = day.year - veh[2]
                km = float(r.KmPerTrip)
                status, cause, op_km, delay, tracked = 1, 0, km, None, True

                p_cancel = pc * cfac * (0.7 + 0.3 * mf) * (1 + (driver - 1) * 0.9) + storm
                p_driver_share = 0.45 * driver
                p_partial = pp * mf * (PEAK.get(hour, 1.0) ** 0.5)
                p_bypass = pb * gfac * PEAK.get(hour, 1.0) * mf
                u = RNG.random()
                if u < p_cancel:
                    status, op_km = 4, 0.0
                    if storm and RNG.random() < storm / (p_cancel):
                        cause = 5
                    else:
                        w = np.array([p_driver_share, 0.30 * (1 + age / 12), 0.06,
                                      0.08 * (mf - 0.7) * 2, 0.05])
                        cause = [1, 2, 4, 5, 6][RNG.choice(5, p=w / w.sum())]
                elif u < p_cancel + p_partial:
                    status = 2
                    op_km = round(km * RNG.uniform(0.3, 0.85), 1)
                    w = np.array([0.30 * (1 + age / 12), 0.25 * gfac, 0.22, 0.10 * mf, 0.13])
                    cause = [2, 3, 4, 5, 6][RNG.choice(5, p=w / w.sum())]
                elif u < p_cancel + p_partial + p_bypass:
                    status = 3
                    op_km = round(km * RNG.uniform(0.7, 0.92), 1)
                    cause = 3 if RNG.random() < 0.75 else 4

                if status != 4:
                    p_gap = 0.012 * afac
                    if region == "North-West" and ts >= AVL_UPGRADE:
                        p_gap = 0.010
                    if stype == "Regional":
                        p_gap *= 1.4
                    if status == 1 and RNG.random() < p_gap:
                        status, cause, tracked = 5, 7, False
                    else:
                        base = dmean * gfac * PEAK.get(hour, 1.0) * (0.6 + 0.4 * mf)
                        if dt != "Weekday":
                            base *= 0.6
                        if status in (2, 3):
                            base += 4
                        delay = int(round(RNG.gamma(1.6, base / 1.6) - RNG.uniform(0, 2.2)))
                        delay = max(delay, -3)
                lost = round(km - op_km, 1) if status in (2, 3, 4) else 0.0
                # passengers
                if status == 4:
                    p = 0
                else:
                    lam = pax * PEAK.get(hour, 1.0) * (0.55 if dt != "Weekday" else 1.0)
                    lam *= school if stype in ("City", "Commuter") else (1.25 if day.month in (6, 7, 8) else 1.0)
                    lam *= op_km / km if km else 1
                    p = int(RNG.poisson(max(lam, 1)))
                band = ("AM Peak" if 7 <= hour <= 9 else "PM Peak" if 16 <= hour <= 18
                        else "Evening" if hour >= 19 else "Early" if hour < 7 else "Interpeak")
                rows.append((jid, int(day.strftime("%Y%m%d")), int(r.RouteKey), veh[0],
                             f"{mins // 60:02d}:{mins % 60:02d}", hour, band, direction,
                             status, cause, km, op_km, lost, delay, int(tracked), p))

fact = pd.DataFrame(rows, columns=[
    "JourneyID", "DateKey", "RouteKey", "VehicleKey", "ScheduledDeparture", "DepartureHour",
    "TimeBand", "Direction", "StatusKey", "CauseKey", "ScheduledKm", "OperatedKm", "LostKm",
    "DepartureDelayMins", "IsTracked", "Passengers"])
fact["DepartureDelayMins"] = fact["DepartureDelayMins"].astype("Int64")

dim_date.to_csv(OUT / "DimDate.csv", index=False, date_format="%Y-%m-%d")
dim_route.to_csv(OUT / "DimRoute.csv", index=False)
dim_vehicle.to_csv(OUT / "DimVehicle.csv", index=False)
dim_status.to_csv(OUT / "DimJourneyStatus.csv", index=False)
dim_cause.to_csv(OUT / "DimLostKmCause.csv", index=False)
dim_security.to_csv(OUT / "SecurityUserRegion.csv", index=False)
fact.to_csv(OUT / "FactJourney.csv", index=False)
print(f"FactJourney rows: {len(fact):,}")
