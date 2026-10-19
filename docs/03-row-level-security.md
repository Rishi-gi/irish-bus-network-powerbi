# Row-Level Security (RLS)

**Goal:** each regional manager opens the same report but sees only their own region. A head of operations sees every region. One report, one semantic model, no copies per region.

RLS works by attaching a DAX (Data Analysis Expressions) filter to a table inside a *role*. When a user is in that role, the filter is applied before any visual is calculated, and it flows from the dimension to the fact table through the relationship. Because `DimRoute` filters `FactJourney`, filtering routes by region filters every journey, every km and every punctuality figure.

This project shows both patterns:

| Pattern | How it decides | Good for | Weakness |
|---|---|---|---|
| Static | Region is hard-coded in the role | Small, stable org | One role per region; changes need a republish |
| Dynamic | Looks up the signed-in user's email in `SecurityUserRegion` | Real deployments | Needs a maintained mapping table |

---

## 1. Static roles (start here)

1. **Modeling > Manage roles > New**.
2. Name: `Region - South`.
3. Select table **DimRoute** and switch to the DAX editor. Enter:
   ```dax
   [Region] = "South"
   ```
4. Repeat for `Region - West`, `Region - Mid-West`, `Region - South-East`, `Region - North-West`, `Region - East`.
5. **Save**.

**Test:** Modeling > **View as** > tick `Region - South` > OK. Every visual should now show South only. The `Selected Regions Text` card should read "Regions: South". Click **Stop viewing** when done.

---

## 2. Dynamic role (the one to talk about in interviews)

`SecurityUserRegion.csv` maps user emails to regions:

| UserEmail | Region |
|---|---|
| manager.south@example.com | South |
| manager.west@example.com | West |
| … one manager per region … | … |
| head.of.operations@example.com | every region (6 rows) |
| analyst.southwest@example.com | South **and** West |

The two-region analyst shows that one user can hold several regions without a new role.

1. Make sure `SecurityUserRegion` has **no relationship** to other tables. Right-click it > **Hide in report view**.
2. **Modeling > Manage roles > New**, name it `Regional Manager (dynamic)`.
3. On table **SecurityUserRegion** add:
   ```dax
   [UserEmail] = LOWER ( USERPRINCIPALNAME () )
   ```
   This stops a user reading other people's mappings.
4. On table **DimRoute** add:
   ```dax
   [Region]
       IN CALCULATETABLE (
           VALUES ( SecurityUserRegion[Region] ),
           SecurityUserRegion[UserEmail] = LOWER ( USERPRINCIPALNAME () )
       )
   ```
   In words: *keep the routes whose region appears against my email in the security table.*
5. **Save**.

**Test in Desktop:** Modeling > **View as** > tick **Other user**, type `manager.west@example.com`, tick `Regional Manager (dynamic)` > OK.

| Test as | Expected regions | Expected Scheduled Journeys |
|---|---|---|
| manager.west@example.com | West | 51,802 |
| manager.northwest@example.com | North-West | 22,930 |
| analyst.southwest@example.com | South, West | 127,540 |
| head.of.operations@example.com | All six | 299,136 |
| someone.else@example.com | none (blank visuals) | blank |

The last test matters. An unknown user must see **nothing**, not everything. That is the safe failure mode.

Put the `Current User` and `Selected Regions Text` measures in two cards on a hidden "RLS check" page. They show who Power BI thinks you are and what you can see.

---

## 3. In the Power BI service

1. Publish the report.
2. Workspace > semantic model > **⋯ > Security**.
3. Add people or, better, **security groups** to each role.
4. Use **Test as role** to confirm.

> **RLS only restricts users with the *Viewer* workspace role (or people the report/app is shared with).** Admins, Members and Contributors can edit the model, so RLS does not apply to them. Test with a Viewer account.

The paginated MI (Management Information) report connects to this same semantic model, so it inherits the same RLS. A regional manager running the monthly PDF also gets only their region.

---

## 4. How to explain it in an interview (about 30 seconds)

> "I filtered on the route dimension instead of the fact table. Region lives on `DimRoute`, and the one-to-many relationship carries the filter to roughly 300,000 journey rows. I built static roles first to prove the logic. Then I replaced them with one dynamic role that looks up `USERPRINCIPALNAME()` in a mapping table, so adding a manager is a data change rather than a model change. I tested it with View as > Other user, including an unknown email, to confirm that an unmapped user sees nothing rather than everything."
