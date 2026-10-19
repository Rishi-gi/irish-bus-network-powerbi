// =====================================================================
//  Power Query (M language) for every table in the model.
//  How to use: Home > Transform data > New Source > Blank Query >
//  Advanced Editor, paste one query, rename it to the name in the header.
//  Create the DataFolder parameter first.
// =====================================================================


// ---------- Parameter: DataFolder -------------------------------------
// Home > Manage Parameters > New Parameter
//   Name: DataFolder   Type: Text
//   Current value: the folder holding the CSVs, ending with a backslash, e.g.
//   C:\Users\Rishikesh\Documents\irish-bus-network-powerbi\data\


// ---------- Helper used by every query (optional) ---------------------
// Each query below repeats the same three steps:
//   1. read the CSV as UTF-8   2. promote the header row   3. set data types
// Setting types with the "en-IE" culture keeps dates and decimals correct
// whatever your Windows regional settings are.


// ===================== Query name: FactJourney ========================
let
    Source = Csv.Document(
        File.Contents(DataFolder & "FactJourney.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"JourneyID", Int64.Type}, {"DateKey", Int64.Type}, {"RouteKey", Int64.Type},
            {"VehicleKey", Int64.Type}, {"ScheduledDeparture", type time},
            {"DepartureHour", Int64.Type}, {"TimeBand", type text}, {"Direction", type text},
            {"StatusKey", Int64.Type}, {"CauseKey", Int64.Type},
            {"ScheduledKm", type number}, {"OperatedKm", type number}, {"LostKm", type number},
            {"DepartureDelayMins", Int64.Type}, {"IsTracked", Int64.Type},
            {"Passengers", Int64.Type}
        },
        "en-IE"
    ),
    // 1/0 flag -> true/false so DAX can test FactJourney[IsTracked] = TRUE()
    TrackedAsLogical = Table.TransformColumns(
        ChangedTypes, {{"IsTracked", each _ = 1, type logical}}
    ),
    // Sort key so time bands appear in the order of the day, not alphabetically
    AddedTimeBandOrder = Table.AddColumn(
        TrackedAsLogical, "TimeBandOrder",
        each
            if [TimeBand] = "Early" then 1
            else if [TimeBand] = "AM Peak" then 2
            else if [TimeBand] = "Interpeak" then 3
            else if [TimeBand] = "PM Peak" then 4
            else 5,
        Int64.Type
    )
in
    AddedTimeBandOrder


// ===================== Query name: DimDate ============================
let
    Source = Csv.Document(
        File.Contents(DataFolder & "DimDate.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"DateKey", Int64.Type}, {"Date", type date}, {"Year", Int64.Type},
            {"Quarter", type text}, {"MonthNo", Int64.Type}, {"MonthName", type text},
            {"YearMonth", type text}, {"MonthStart", type date}, {"WeekdayNo", Int64.Type},
            {"WeekdayName", type text}, {"IsBankHoliday", type logical}, {"DayType", type text}
        },
        "en-IE"
    )
in
    ChangedTypes


// ===================== Query name: DimRoute ===========================
let
    Source = Csv.Document(
        File.Contents(DataFolder & "DimRoute.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"RouteKey", Int64.Type}, {"RouteCode", type text}, {"RouteName", type text},
            {"ServiceType", type text}, {"Depot", type text}, {"Region", type text},
            {"KmPerTrip", type number}, {"WeekdayTripsPerDirection", Int64.Type}
        },
        "en-IE"
    ),
    // Friendly label for slicers and tables, e.g. "SC01 · Cork City Centre – Ballincollig"
    AddedRouteLabel = Table.AddColumn(
        ChangedTypes, "RouteLabel", each [RouteCode] & " · " & [RouteName], type text
    )
in
    AddedRouteLabel


// ===================== Query name: DimVehicle =========================
let
    Source = Csv.Document(
        File.Contents(DataFolder & "DimVehicle.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"VehicleKey", Int64.Type}, {"FleetNumber", type text}, {"VehicleType", type text},
            {"FuelType", type text}, {"YearIntroduced", Int64.Type}, {"HomeDepot", type text},
            {"AllocatedService", type text}
        },
        "en-IE"
    ),
    // Age band at the end of the data period (2025) – useful for breakdown analysis
    AddedAgeBand = Table.AddColumn(
        ChangedTypes, "AgeBand",
        each
            let age = 2025 - [YearIntroduced]
            in if age <= 3 then "0–3 years"
               else if age <= 7 then "4–7 years"
               else if age <= 11 then "8–11 years"
               else "12+ years",
        type text
    )
in
    AddedAgeBand


// ===================== Query name: DimJourneyStatus ===================
let
    Source = Csv.Document(
        File.Contents(DataFolder & "DimJourneyStatus.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"StatusKey", Int64.Type}, {"JourneyStatus", type text}, {"StatusGroup", type text},
            {"IsOperated", type logical}, {"IsLostService", type logical}
        },
        "en-IE"
    )
in
    ChangedTypes


// ===================== Query name: DimLostKmCause =====================
let
    Source = Csv.Document(
        File.Contents(DataFolder & "DimLostKmCause.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"CauseKey", Int64.Type}, {"Cause", type text}, {"CauseCategory", type text},
            {"CountsAsLostKm", type logical}
        },
        "en-IE"
    )
in
    ChangedTypes


// ===================== Query name: SecurityUserRegion =================
// Used only by Row-Level Security. No relationship; hide it in Report view.
let
    Source = Csv.Document(
        File.Contents(DataFolder & "SecurityUserRegion.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders, {{"UserEmail", type text}, {"Region", type text}}, "en-IE"
    ),
    // Emails are compared in lower case so "Manager.South@..." still matches
    LowerCaseEmail = Table.TransformColumns(ChangedTypes, {{"UserEmail", Text.Lower, type text}})
in
    LowerCaseEmail
