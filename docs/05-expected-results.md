# Expected results – check your build

Calculated directly from the CSVs with the same rules as the DAX measures. If a card in Power BI shows a different number, check the relationship, the data types in Power Query, and that `DimDate` is marked as the date table. Lost km figures are rounded to whole km.

## 1. Whole period (1 Jan 2024 – 31 Dec 2025), no filters

| Measure | Expected value |
|---|---|
| Scheduled Journeys | 299,136 |
| Operated Journeys | 294,841 |
| Journeys Not Operated | 4,295 |
| Scheduled Km | 8,141,442 |
| Operated Km | 7,960,110 |
| Lost Km | 181,332 |
| Lost Km % | 2.23% |
| Tracked Departures | 290,804 |
| On-Time Departures | 262,785 |
| Punctuality % | 90.4% |
| Non-Tracking Journeys | 4,037 |
| AVL Tracking Rate % | 98.6% |
| Passengers | 10,834,641 |

## 2. By year (Year slicer)

| Year | Scheduled Journeys | Scheduled Km | Lost Km | Lost Km % | Punctuality % | AVL Tracking Rate % | Passengers |
|---|---|---|---|---|---|---|---|
| 2024 | 149,816 | 4,077,432 | 85,587 | 2.10% | 90.4% | 98.6% | 5,437,070 |
| 2025 | 149,320 | 4,064,010 | 95,745 | 2.36% | 90.4% | 98.7% | 5,397,571 |

`Lost Km % YoY Change (pp)` with Year = 2025 selected: **+0.26 percentage points**.

## 3. By region, whole period (also the RLS test values)

| Region | Scheduled Journeys | Scheduled Km | Lost Km | Lost Km % | Punctuality % | AVL Tracking Rate % | Passengers |
|---|---|---|---|---|---|---|---|
| East | 54,270 | 2,449,958 | 61,804 | 2.52% | 82.7% | 98.6% | 2,011,259 |
| Mid-West | 47,074 | 1,355,986 | 29,088 | 2.15% | 92.0% | 98.8% | 1,587,728 |
| North-West | 22,930 | 911,960 | 19,450 | 2.13% | 91.3% | 96.6% | 564,628 |
| South | 75,738 | 1,492,724 | 34,704 | 2.32% | 91.5% | 98.8% | 3,019,194 |
| South-East | 47,322 | 912,298 | 16,286 | 1.79% | 92.6% | 98.9% | 1,602,383 |
| West | 51,802 | 1,018,516 | 20,001 | 1.96% | 92.8% | 98.8% | 2,049,449 |

### RLS: Scheduled Journeys when viewing as each user (dynamic role)

| View as | Regions visible | Scheduled Journeys |
|---|---|---|
| analyst.southwest@example.com | South, West | 127,540 |
| head.of.operations@example.com | All six | 299,136 |
| manager.east@example.com | East | 54,270 |
| manager.midwest@example.com | Mid-West | 47,074 |
| manager.northwest@example.com | North-West | 22,930 |
| manager.south@example.com | South | 75,738 |
| manager.southeast@example.com | South-East | 47,322 |
| manager.west@example.com | West | 51,802 |
| someone.else@example.com | none | (blank) |

## 4. By month (network)

| YearMonth | Lost Km | Lost Km % | Lost Km MoM % | Punctuality % | AVL Tracking Rate % |
|---|---|---|---|---|---|
| 2024-01 | 8,656 | 2.47% |  | 89.4% | 98.4% |
| 2024-02 | 6,457 | 2.00% | -25.4% | 89.9% | 98.4% |
| 2024-03 | 6,857 | 2.04% | +6.2% | 90.6% | 98.5% |
| 2024-04 | 5,154 | 1.53% | -24.8% | 90.8% | 98.7% |
| 2024-05 | 6,256 | 1.79% | +21.4% | 91.5% | 98.4% |
| 2024-06 | 5,295 | 1.64% | -15.4% | 90.9% | 98.4% |
| 2024-07 | 5,530 | 1.54% | +4.4% | 91.1% | 98.6% |
| 2024-08 | 5,393 | 1.57% | -2.5% | 91.3% | 98.5% |
| 2024-09 | 5,447 | 1.62% | +1.0% | 90.5% | 98.6% |
| 2024-10 | 9,408 | 2.69% | +72.7% | 90.0% | 98.6% |
| 2024-11 | 9,384 | 2.77% | -0.3% | 89.1% | 98.7% |
| 2024-12 | 11,749 | 3.52% | +25.2% | 88.9% | 98.8% |
| 2025-01 | 23,018 | 6.58% | +95.9% | 89.2% | 98.6% |
| 2025-02 | 9,225 | 2.98% | -59.9% | 89.8% | 98.3% |
| 2025-03 | 8,017 | 2.39% | -13.1% | 90.4% | 98.6% |
| 2025-04 | 5,685 | 1.69% | -29.1% | 90.7% | 98.6% |
| 2025-05 | 6,244 | 1.82% | +9.8% | 91.1% | 98.6% |
| 2025-06 | 5,275 | 1.61% | -15.5% | 91.4% | 98.7% |
| 2025-07 | 5,715 | 1.60% | +8.3% | 91.5% | 99.0% |
| 2025-08 | 4,895 | 1.46% | -14.3% | 91.6% | 98.8% |
| 2025-09 | 5,780 | 1.68% | +18.1% | 90.0% | 98.8% |
| 2025-10 | 6,640 | 1.90% | +14.9% | 90.1% | 98.8% |
| 2025-11 | 8,461 | 2.56% | +27.4% | 89.8% | 98.9% |
| 2025-12 | 6,790 | 1.99% | -19.7% | 88.9% | 98.8% |

## 5. Top 5 routes by Lost Km (whole period)

| Rank | Route | Lost Km | Lost Km % |
|---|---|---|---|
| 1 | DM01 · Drogheda – Dublin City | 23,325 | 2.67% |
| 2 | DM02 · Navan – Dublin City | 20,597 | 2.50% |
| 3 | DR04 · Dundalk – Dublin Airport | 15,534 | 2.40% |
| 4 | MR03 · Limerick – Tralee | 13,221 | 2.07% |
| 5 | SR04 · Cork – Killarney | 12,001 | 2.22% |

## 6. Lost km by cause (whole period)

| Cause | Category | Lost Km | Share of Lost Km % |
|---|---|---|---|
| Vehicle defect / breakdown | Internal | 55,950 | 30.9% |
| Driver availability | Internal | 47,209 | 26.0% |
| Severe weather | External | 28,130 | 15.5% |
| Traffic congestion | External | 21,624 | 11.9% |
| Road works / diversion | External | 18,783 | 10.4% |
| Road traffic incident | External | 9,636 | 5.3% |

`Top Cause of Lost Km` with no filters: **Vehicle defect / breakdown**. `Internal Share of Lost Km %`: **56.9%**.

## 7. Breakdown Lost Km per 1,000 Km by vehicle age band

| AgeBand | Breakdown Lost Km per 1,000 Km |
|---|---|
| 0–3 years | 5.56 |
| 4–7 years | 6.20 |
| 8–11 years | 7.77 |
| 12+ years | 7.71 |

## 8. Data-quality check: North-West AVL upgrade

AVL Tracking Rate % in North-West: **95.7%** Jan 2024 – May 2025, **98.8%** Jun – Dec 2025.
