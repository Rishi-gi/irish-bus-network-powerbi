# Paginated monthly MI report (Power BI Report Builder)

**What it is:** a print-ready, multi-page PDF (Portable Document Format) report called **"Monthly Service Performance MI (Management Information) Pack"**. You pick a month. It produces a network summary page, then one page per region with route-level figures, a lost-km-by-cause table and a one-line commentary. This is the kind of fixed-layout report that gets emailed to managers or filed for compliance, where an interactive dashboard doesn't fit.

**Interactive report vs paginated report**

| | Power BI report (.pbix) | Paginated report (.rdl) |
|---|---|---|
| Built in | Power BI Desktop | Power BI Report Builder |
| Purpose | Explore, slice, drill | Print, export, distribute |
| Layout | Fits one screen | Grows across as many pages as the data needs |
| Typical use | Daily monitoring | Month-end MI pack, regulatory returns, invoices |

Power BI Report Builder is a free download from the Microsoft Download Center. It doesn't need a Pro licence to author reports.

---

## Choose your route

| Route | Needs | What you can show |
|---|---|---|
| **A. Connect to the published semantic model** (best) | A Power BI account with a **work or school email** (the service doesn't accept Gmail/Outlook.com addresses). A free licence can publish to *My workspace* | One model feeding both reports; RLS applies to the PDF too |
| **B. Offline with "Enter Data"** (fallback) | Nothing beyond Report Builder | Full layout, parameters, grouping, page breaks, expressions, PDF export |

Both routes produce the same layout. Do Route B first if you can't get a work or school account, and upgrade to Route A later.

---

## Route A – connect to the semantic model

1. In Power BI Desktop, **Publish** the report to *My workspace*.
2. Open Report Builder > sign in with the same account.
3. **Report Data pane > Data Sources > Add Power BI Semantic Model Connection** > pick *Irish-Bus-Network-Performance*.
4. **Datasets > Add Dataset** > choose the data source > **Query Designer**. You can drag fields there, or switch to text and paste the queries below.

### Parameter dataset: `dsMonths`
```dax
EVALUATE
SUMMARIZECOLUMNS ( DimDate[YearMonth] )
ORDER BY DimDate[YearMonth] DESC
```

### Main dataset: `dsRouteMonth`
Create a query parameter `@YearMonth` (Text).
```dax
EVALUATE
SUMMARIZECOLUMNS (
    DimRoute[Region],
    DimRoute[RouteCode],
    DimRoute[RouteName],
    DimRoute[ServiceType],
    TREATAS ( { @YearMonth }, DimDate[YearMonth] ),
    "ScheduledJourneys", [Scheduled Journeys],
    "JourneysNotOperated", [Journeys Not Operated],
    "ScheduledKm", [Scheduled Km],
    "LostKm", [Lost Km],
    "LostKmPct", [Lost Km %],
    "PunctualityPct", [Punctuality %],
    "AVLTrackingPct", [AVL Tracking Rate %],
    "Passengers", [Passengers],
    // counts so percentages can be re-aggregated correctly at region/total level
    "OnTimeDepartures", [On-Time Departures],
    "TrackedDepartures", [Tracked Departures],
    "OperatedJourneys", [Operated Journeys],
    "NonTrackingJourneys", [Non-Tracking Journeys]
)
ORDER BY DimRoute[Region], DimRoute[RouteCode]
```

### Cause dataset: `dsCauseMonth`
```dax
EVALUATE
SUMMARIZECOLUMNS (
    DimRoute[Region],
    DimLostKmCause[Cause],
    DimLostKmCause[CauseCategory],
    TREATAS ( { @YearMonth }, DimDate[YearMonth] ),
    "LostKm", [Lost Km]
)
ORDER BY DimRoute[Region], [LostKm] DESC
```

### Commentary dataset: `dsCommentary`
```dax
EVALUATE
SUMMARIZECOLUMNS (
    DimRoute[Region],
    TREATAS ( { @YearMonth }, DimDate[YearMonth] ),
    "Commentary", [MI Commentary]
)
```

Because the queries run against the semantic model, **RLS applies**. A regional manager who runs this report gets only their own region's pages.

---

## Route B – offline with "Enter Data"

The `data/paginated/` folder holds pre-aggregated monthly files made from the same data and the same rules:

- `MonthlyRouteSummary.csv`: one row per month × route (576 rows)
- `MonthlyCauseSummary.csv`: one row per month × region × cause
- `MonthlyRegionSummary.csv`: one row per month × region (144 rows), including a ready-made commentary column

1. Report Builder > **Data Sources > Add Data Source > Enter Data**. (Older versions: New Data Source > *Embedded* > type **Enter Data**.)
2. Open the CSV in Excel, copy all cells including headers, and paste into the Enter Data grid. Set column types (Text, Integer, Decimal).
3. Make one dataset per file: `dsRouteMonth`, `dsCauseMonth`, `dsRegionMonth`.
4. Create the report parameter `YearMonth` (below). On each dataset add a **Filter**: `[YearMonth] = [@YearMonth]`.

---

## Build the layout (same for both routes)

### 1. Report parameter
- **Parameters > Add Parameter**: Name `YearMonth`, Prompt "Month", Data type Text.
- Available values: *Get values from a query* > `dsMonths` (Route A), or *Specify values* typed from `2025-12` down to `2024-01` (Route B).
- Default value: `2025-12`.

### 2. Page set-up
- Report Properties: **A4 portrait** (21 cm × 29.7 cm), margins 1.5 cm.
- Page **header**: title "Monthly Service Performance MI Pack", subtitle textbox `="Month: " & Format(CDate(Parameters!YearMonth.Value & "-01"), "MMMM yyyy")`, and a small "SYNTHETIC DATA – PORTFOLIO PROJECT" label.
- Page **footer**: `="Page " & Globals!PageNumber & " of " & Globals!TotalPages` on the right, `="Run " & Format(Globals!ExecutionTime, "dd MMM yyyy HH:mm") & " by " & User!UserID` on the left.

### 3. Page 1 – Network summary
A **Table** on `dsRouteMonth` grouped by `Region` (one row per region, details hidden):

| Region | Scheduled journeys | Not operated | Scheduled km | Lost km | Lost km % | Punctuality % | AVL tracking % |
|---|---|---|---|---|---|---|---|
| `=Fields!Region.Value` | `=Sum(...)` | … | … | … | `=Sum(Fields!LostKm.Value)/Sum(Fields!ScheduledKm.Value)` | see note | … |

Add a **Total** row (right-click group > Add Total > After).

> **Note on percentages.** Never `Sum` or `Avg` a percentage column across routes. Recalculate it from its parts. Lost km % = Sum(lost) / Sum(scheduled). For punctuality, Route B's CSVs include `OnTimeDepartures` and `TrackedDepartures`, so use `=Sum(Fields!OnTimeDepartures.Value)/Sum(Fields!TrackedDepartures.Value)`. In Route A, add those two counts to the query and do the same. Averaging percentages is the most common MI-report mistake.

Under the table, insert a **page break** (Rectangle > Page break after).

### 4. One page per region
1. Insert a **List** on `dsRouteMonth`. Row group = `Region`. In Group Properties > **Page Breaks > Between each instance of a group**.
2. Inside the list:
   - Textbox heading `=Fields!Region.Value & " region"`.
   - Four KPI (Key Performance Indicator) textboxes: Lost km, Lost km %, Punctuality %, AVL tracking %.
   - A **Table** of routes: Route code, Route name, Service type, Scheduled journeys, Lost km, Lost km %, Punctuality %, Passengers.
   - **Conditional colour** on Lost km %: Textbox properties > Font > Colour > expression `=IIf(Fields!LostKmPct.Value > 0.02, "#C5221F", "Black")`. Do the same for Punctuality % with `< 0.90`.
   - A small **bar chart** or table from `dsCauseMonth` showing lost km by cause, filtered to the current region (Chart properties > Filters > `[Region] = Fields!Region.Value` uses the list's scope; or nest the chart inside the list).
   - A commentary textbox (Route A: `dsCommentary`; Route B: the `Commentary` column of `dsRegionMonth`), using a `Lookup` such as `=Lookup(Fields!Region.Value, Fields!Region.Value, Fields!Commentary.Value, "dsRegionMonth")`.
3. Set **Repeat header rows on each page** on the route table (Advanced mode > Row Groups > Static > RepeatOnNewPage = True).

### 5. Export and test
- **Run**, choose `2025-01`. You should get 7 pages: the summary plus six regions. January 2025 lost km % should be about 6.6% network-wide, almost all of it weather.
- Export > **PDF** and save it as `images/mi-report-2025-01.pdf`, with a PNG screenshot of page 1 as `images/mi-report.png`.
- Save the report definition as `powerbi/Monthly-MI-Pack.rdl` and commit it.

---

## Going further (talking points, no build needed)
- **Subscriptions:** in the Power BI service, a paginated report can be emailed as a PDF on a schedule, e.g. the 3rd working day of each month. Sending to other users needs a Pro or Premium Per User licence.
- **Data-driven / dynamic per-recipient subscriptions** can send each regional manager their own region's PDF from one report.
- **Drill-through link:** add a textbox action that opens the interactive Power BI report filtered to the same region and month.
