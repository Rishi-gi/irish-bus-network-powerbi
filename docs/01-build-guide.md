# Build guide: Power BI Desktop, step by step

Expect about two evenings. Evening 1 covers Parts A–D (data, model, measures, theme). Evening 2 covers Parts E–G (report pages, RLS and the paginated report), then publishing to GitHub.

**You need:** Windows, [Power BI Desktop](https://aka.ms/pbidesktopstore) (free, from the Microsoft Store), and this repository downloaded or cloned to your laptop.

---

## Part A – Load the data (Power Query)

1. Open Power BI Desktop > **Blank report**.
2. **Home > Transform data** opens the Power Query editor.
3. **Manage Parameters > New Parameter**:
   - Name `DataFolder`, Type `Text`
   - Current value: the full path to the `data` folder, **ending in a backslash**, e.g. `C:\Users\Rishikesh\Documents\irish-bus-network-powerbi\data\`
4. For each of the seven queries in [`powerbi/power-query.m`](../powerbi/power-query.m):
   **New Source > Blank Query > Advanced Editor** > paste the query > **Done** > rename the query to its exact name (`FactJourney`, `DimDate`, `DimRoute`, `DimVehicle`, `DimJourneyStatus`, `DimLostKmCause`, `SecurityUserRegion`).
5. Click through each query and check the column icons show the right type (calendar for dates, `1.2` for decimals, `123` for whole numbers).
6. **Close & Apply**. The fact table loads 299,136 rows.

> Why a parameter? If the folder moves, you change one value instead of seven file paths. In an interview: *"the source path is parameterised so the model can be repointed to a different environment."*

---

## Part B – Model

Switch to **Model view** (third icon on the left).

1. **Relationships.** Power BI may auto-detect some. Delete any it got wrong and make sure exactly these five exist, all **one-to-many, single direction**:
   - `DimDate[DateKey]` → `FactJourney[DateKey]`
   - `DimRoute[RouteKey]` → `FactJourney[RouteKey]`
   - `DimVehicle[VehicleKey]` → `FactJourney[VehicleKey]`
   - `DimJourneyStatus[StatusKey]` → `FactJourney[StatusKey]`
   - `DimLostKmCause[CauseKey]` → `FactJourney[CauseKey]`

   `SecurityUserRegion` has **no** relationship. If one was auto-created, delete it.
2. **Mark the date table.** Select `DimDate` > **Table tools > Mark as date table** > Date column `Date`. Time-intelligence measures such as previous month and same period last year depend on this.
3. **Sort-by columns** (select the column > Column tools > Sort by column):
   - `DimDate[MonthName]` by `MonthNo`
   - `DimDate[WeekdayName]` by `WeekdayNo`
   - `FactJourney[TimeBand]` by `TimeBandOrder`
4. **Hide technical columns** (right-click > Hide in report view): every `…Key` column in `FactJourney`, `TimeBandOrder`, `JourneyID`, and the whole `SecurityUserRegion` table. Report users should drag fields from the dimensions, not from the fact keys.
5. **Stop implicit sums.** Select `DimDate[Year]`, `DimRoute[KmPerTrip]`, `DimVehicle[YearIntroduced]`, `FactJourney[DepartureHour]` > Column tools > **Summarization: Don't summarize**.
6. Arrange the diagram as a star: fact in the middle, dimensions around it. **Take a screenshot** for the README (`images/model.png`).

---

## Part C – Measures

1. **Home > Enter data** > name the table `_Measures` > **Load**.
2. Select `_Measures` and, for each measure in [`powerbi/measures.dax`](../powerbi/measures.dax), choose **Modeling > New measure** and paste one measure at a time (name, `=`, expression). Comment lines starting with `//` can stay or go.
3. Set the format shown in the `[brackets]` comment (Measure tools > Format).
4. Group measures into **display folders** (Model view > select measure > Properties > Display folder): `1 Base`, `2 Punctuality`, `3 Data Quality`, `4 Targets`, `5 Time Intelligence`, `6 Ranking & Cause`, `7 Text`.
5. Delete the dummy `Column1` in `_Measures`. The table icon changes to a calculator, and the table moves to the top of the Fields pane.

> **Quick test:** a card with `Scheduled Journeys` should show **299,136**, `Lost Km %` **2.23%**, and `Punctuality %` **90.4%**. All the check numbers are in [05-expected-results.md](05-expected-results.md).

---

## Part D – Theme

**View > Themes > Browse for themes** > `powerbi/theme.json`. This applies a consistent colour palette, RAG (Red / Amber / Green) colours, fonts, a light page background and white visual cards.

Page size: **Format page > Canvas settings > 16:9, 1280 × 720**.

---

## Part E – Report pages

Build five pages plus one hidden check page. Every page gets the same **header strip**: a text box with the page title on the left, and cards with `Selected Regions Text` and `Period Text` on the right.

**Sync slicers:** add three slicers on page 1 (`DimDate[Year]` as tiles, `DimRoute[Region]` as a dropdown, `DimRoute[ServiceType]` as a dropdown). Then **View > Sync slicers** and tick *Sync* and *Visible* for pages 1–4, so a selection follows the user from page to page.

### Page 1 – Network Overview
*Question it answers: how is the network doing against target?*

| Visual | Fields | Settings |
|---|---|---|
| 6 × Card (new) | `Scheduled Km`, `Lost Km %`, `Punctuality %`, `AVL Tracking Rate %`, `Passengers`, `Journeys Not Operated` | Reference label = matching target measure. Callout colour: Conditional formatting > Field value > `Lost Km RAG Colour` / `Punctuality RAG Colour` |
| Line and clustered column chart | X: `DimDate[MonthStart]` (Date hierarchy off). Column: `Lost Km`. Lines: `Lost Km %`, `Target Lost Km %` | Secondary Y-axis on. Target line dashed and grey |
| Clustered bar chart | Y: `DimRoute[Region]`. X: `Lost Km %` | Bar colour: Field value `Lost Km RAG Colour`. Sort descending |
| Line chart | X: `MonthStart`. Y: `Punctuality %`, `Target Punctuality %` | Y-axis start 0.80 so changes are visible; say so in the title |
| Card | `Top Cause of Lost Km` | Title "Largest cause of lost km" |

Expected story: January 2025 towers above the rest (severe weather), Oct 2024 – Mar 2025 runs above target (driver availability), and East has the weakest punctuality.

### Page 2 – Lost Kilometres
*Question: where and why are we losing kilometres?*

| Visual | Fields | Settings |
|---|---|---|
| Stacked column chart | X: `MonthStart`. Y: `Lost Km`. Legend: `DimLostKmCause[Cause]` | Filter Cause ≠ "No issue" and ≠ "AVL / GPS data issue" |
| Decomposition tree | Analyse: `Lost Km`. Explain by: `Region`, `Depot`, `RouteLabel`, `Cause`, `JourneyStatus`, `VehicleType`, `AgeBand` | Lets a manager drill freely; good interview demo |
| Matrix | Rows: `Region` > `RouteLabel`. Values: `Lost Km`, `Lost Km %`, `Lost Km % PY`, `Lost Km % YoY Change (pp)`, `Route Rank by Lost Km` | Background colour on `Lost Km %` from `Lost Km RAG Colour`. Turn on +/- icons |
| Clustered column chart | X: `DimVehicle[AgeBand]`. Y: `Breakdown Lost Km per 1,000 Km` | Shows older vehicles break down more |
| Donut or 100% bar | Legend: `CauseCategory`. Values: `Lost Km` | Internal vs external share |

### Page 3 – Punctuality
*Question: when and where are departures late?*

| Visual | Fields | Settings |
|---|---|---|
| Matrix (heatmap) | Rows: `FactJourney[TimeBand]`. Columns: `DimDate[WeekdayName]`. Values: `Punctuality %` | Background colour > gradient, red (low) to green (high). Turn off totals |
| Clustered bar | Y: `ServiceType`. X: `Punctuality %` | Add a constant line at 0.90 (Analytics pane) |
| Line chart | X: `MonthStart`. Y: `Punctuality %`. Legend: `Region` | Small multiples by Region is a nice alternative |
| Column chart | X: `FactJourney[DepartureDelayMins]` (Don't summarize). Y: `Tracked Departures` | Visual filter: delay between −3 and 20. This is the delay distribution |
| 3 × Card | `Average Departure Delay (mins)`, `Late Departures`, `Early Departures` | |

### Page 4 – Data Quality (AVL)
*Question: can we trust the tracking data, and is it improving?*

| Visual | Fields | Settings |
|---|---|---|
| Line chart | X: `MonthStart`. Y: `AVL Tracking Rate %`. Legend: `Region` | Constant line at 0.98. Note the North-West step-change in June 2025 |
| Clustered bar | Y: `Region`. X: `Non-Tracking Journeys` | |
| Table | `RouteLabel`, `ServiceType`, `Non-Tracking Journeys`, `AVL Tracking Rate %` | Sort by tracking rate ascending |
| Text box | Short explanation: a journey missing from AVL is checked against duty and vehicle records. If it ran, it is classed as *Operated - AVL non-tracking* and is **not** counted as lost km | This is the analytical point of the page |

### Page 5 – Route Detail (drill-through)
1. Add `DimRoute[RouteLabel]` to the **Drill through** well of this page. Power BI adds a Back button automatically.
2. Cards: `Scheduled Journeys`, `Lost Km %`, `Punctuality %`, `AVL Tracking Rate %`, `Passengers per Operated Journey`.
3. Line chart: `MonthStart` against `Lost Km %` and `Punctuality %` (secondary axis).
4. Table: `DimDate[Date]`, `Journeys Not Operated`, `Lost Km`, `Top Cause of Lost Km`. Use a visual filter Top N = 10 by `Lost Km` to show the 10 worst days.
5. Test it: on Page 2, right-click a route in the matrix > **Drill through > Route Detail**.

### Hidden page – RLS check
Two cards: `Current User` and `Selected Regions Text`, plus a table of `Region` × `Scheduled Journeys`. Right-click the page tab > **Hide page**.

### Finishing touches (where most portfolio reports fall short)
- Every visual has a title that is a **sentence or question**, e.g. "Lost km % by region vs 2% target", not "Lost Km % by Region".
- Turn on **tooltips** with the RAG measure values.
- **Edit interactions** (Format > Edit interactions) so the region bar on Page 1 filters the trend charts and doesn't just highlight them.
- **Optional stretch:** a *field parameter* (Modeling > New parameter > Fields) with `Lost Km %`, `Punctuality %` and `AVL Tracking Rate %`, so one regional bar chart can switch metric.
- **Optional stretch:** a **bookmark** pair that toggles the Page 1 trend between "Lost km" and "Punctuality".

---

## Part F – Row-Level Security
Follow [03-row-level-security.md](03-row-level-security.md).

## Part G – Paginated monthly MI report
Follow [04-paginated-mi-report.md](04-paginated-mi-report.md).

---

## Part H – Save, screenshot and push to GitHub

1. **File > Save as** `Irish-Bus-Network-Performance.pbix` in the `powerbi` folder. The file will be roughly 10–20 MB, which is fine for GitHub.
2. *Optional, and good for interviews:* also **File > Save as > Power BI project (.pbip)**. This saves the model and report as text files (TMDL (Tabular Model Definition Language) and JSON), so Git can show line-by-line changes to measures. If the option isn't visible, enable it under Options > Preview features.
3. Screenshot each page at full size into `images/` (`overview.png`, `lost-km.png`, `punctuality.png`, `data-quality.png`, `route-detail.png`, `model.png`, `rls-test.png`, `mi-report.png`). The README already points at these names.
4. Commit and push:
   ```bash
   git add .
   git commit -m "Add Power BI regional bus network performance project"
   git push
   ```
5. Add a short entry for the project to the README of your `data-analytics-portfolio` repo, linking to this one.
