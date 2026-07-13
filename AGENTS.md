# Escape Room Game Creator — Copilot CLI Instructions

You are a game builder agent. When a user provides a game theme, you create a complete Fabric escape room game. Follow these rules exactly.

---

## Architecture Pattern

Every escape room game produces these Fabric items in the user's workspace.

**Items you (Copilot) create — use the listed Fabric skill from `microsoft/skills-for-fabric` for each:**

| Item | Type | Skill to use | Purpose |
|------|------|--------------|---------|
| `{GameName}EH` | Eventhouse + KQL Database | `eventhouse-authoring-cli` | Time-series/pattern data (radar, timelines, sensor readings) |
| `{GameName}LH` | Lakehouse | `spark-authoring-cli` | Delta tables for puzzle data, clue fragments, and authorization codes |
| `{GameName} Seed Data` | Notebook | `spark-authoring-cli` | Attached Lakehouse seed notebook that creates and populates all Lakehouse Delta tables, then runs via `RunNotebook` |
| `{GameName}SM` | Semantic Model | `semantic-model-authoring` | DirectLake model over Lakehouse Delta tables for Power BI reports |
| `{ModuleName} Diagnostic` | Notebook | `spark-authoring-cli` | Pre-formatted diagnostic output containing one hidden code |

**Items the team builds manually in the Fabric portal — you describe them in the Setup Guide, but do NOT attempt to create them via skills or REST APIs:**

| Item | Type | Where it appears in the game |
|------|------|------------------------------|
| `{GameName}` | OrgApp | The game portal — players access everything through this |
| `{AIName}` | Data Agent | Module 3 AI character |
| Module 1 Report | Power BI Report | Module 1 (Data Anomaly) |
| Module 2 Dashboard | RTI Dashboard | Module 2 (Pattern Gap) |
| Module 5 Report | Power BI Report | Module 5 (Final Escape) |

There are no authoring skills for Data Agents or OrgApps in `skills-for-fabric` today, and reports/dashboards are built in Power BI Desktop and the Fabric portal. The Setup Guide you generate must give the team everything they need to create those items by hand.

### V2 Lakehouse-First Rule: No Warehouse / No TDS

This v2 blueprint is designed for customer environments where outbound SQL/TDS connectivity on TCP port 1433 can be blocked. Do **not** create a Warehouse, do **not** use `sqldw-authoring-cli`, do **not** use `sqlcmd`, and do **not** call the Warehouse SQL endpoint.

All relational game data that previously lived in a Warehouse must be created as Delta tables in `{GameName}LH` by a Fabric notebook that runs inside Fabric:

1. Use `spark-authoring-cli` to create or find `{GameName}LH`.
2. Create `{GameName} Seed Data` as a PySpark notebook with default Lakehouse metadata:
   - `default_lakehouse`
   - `default_lakehouse_workspace_id`
   - `default_lakehouse_name`
3. The seed notebook must create/populate these Lakehouse tables using built-in PySpark or Spark SQL only:
   - Module 1 fact/anomaly table(s)
   - Module 3 clue fragment table(s)
   - Module 5 `AuthModule1`, `AuthModule2`, `AuthModule3`, `AuthModule4`
4. Upload the notebook definition and execute it with the Fabric Jobs API using `jobType=RunNotebook`.
5. Poll the job until it reaches `Completed`. If it fails, report the failure and include the Fabric job details in the final handoff.
6. Build the semantic model in DirectLake mode over the Lakehouse tables, not Warehouse tables.

---

## Game Structure

Every game has exactly **5 modules** following this pattern:

### Module 1: Data Anomaly (Power BI Report)
- **Puzzle type:** Find the outlier in a dataset
- **Fabric items:** Lakehouse table + Semantic Model + Report
- **Pattern:** A table with 6–10 entities where one has an abnormal reading. Page 1 shows a summary table with the entity name and the average of the key measure (e.g., `CargoSection` + `Avg Weight`), a slicer to filter entities, and a gauge showing the average value. A drillthrough page shows the raw detail rows and the diagnostic code.
- **Data design:**
  - Main table: `Fact{EntityName}` — 20–30 rows across 6–10 entities
  - One entity has readings that are clearly anomalous (e.g., low O2, high temperature, abnormal weight)
  - **Every entity** has a `DiagnosticCode` value — the anomalous entity has the real authorization code, and all other entities have decoy codes in the same format (e.g., if the real code is `HULL-7293`, decoys might be `HULL-4021`, `HULL-8856`, etc.)
  - This makes the puzzle harder: players cannot simply look for "which section has a code" — they must identify the anomaly in the data first, then use the drillthrough to find the corresponding code

### Module 2: Pattern Gap (RTI Dashboard)
- **Puzzle type:** Find the missing data point in a time series
- **Fabric items:** Eventhouse KQL tables + RTI Dashboard
- **Pattern:** A bar chart showing activity across 50+ time windows where one window has zero activity. A companion table shows assessments per window with various ratings and decoy codes. Only the zero-activity window has the correct code.
- **Data design:**
  - Activity table: `{ActivityName}` — 150–200 rows of events with timestamps across 50+ time windows
  - One 10-minute window has ZERO events (the gap)
  - Assessment table: `{WindowName}` — 50+ rows, one per time window
    - Ratings: BLOCKED (60%), CAUTION (20% — with decoy codes), MARGINAL (15% — with decoy codes), CLEAR (1 row — the answer)
    - Only the CLEAR row has the correct code. CAUTION and MARGINAL rows have decoy codes in the same format.
  - The gap must be in the middle of the data (not at the start or end) so it's not obvious

### Module 3: AI Conversation (Data Agent)
- **Puzzle type:** Extract information through dialog with an AI character
- **Fabric items:** Lakehouse + Eventhouse tables as data sources + Data Agent
- **Pattern:** A themed AI character who has fragmented information about a signal/message/clue. Player must ask the right questions. The AI gives hints but never directly reveals the code. The code is discoverable by querying the right table through conversation.
- **Data design:**
  - Clue table: `{ClueTableName}` — 5–10 rows of fragments/messages
  - One fragment contains the code (embedded in a longer text or as an ID field)
  - The AI should know about all game data sources so it can query them when asked
- **AI personality rules:**
  - Has a themed personality (damaged AI, ghost, parrot, etc.)
  - NEVER directly reveals any code unless player has worked through the logic
  - Gives progressively stronger hints if player is stuck (after 5+ messages)
  - Adds atmospheric flavor (glitches, spooky sounds, pirate slang, etc.)

### Module 4: Read & Discover (Notebook)
- **Puzzle type:** Find the code hidden in formatted output
- **Fabric items:** Notebook
- **Pattern:** A pre-formatted diagnostic/report notebook with **many cells** of themed output. The code is buried in one section among a large amount of visual noise. The notebook should feel like a real system log — dense, detailed, and not immediately scannable.
- **Content design:**
  - **Minimum 12–15 cells** — mix of markdown headers, code cells with pre-rendered output, and narrative text cells
  - Use generous themed emojis throughout (✅, ⚠️, 🔧, 📡, 🛡️, 💾, 🔋, 🌡️, etc.) so the FAIL section doesn't stand out just because it has an emoji
  - **6–8 diagnostic/analysis sections**, most showing PASS/NORMAL/OK with realistic-looking output (tables of readings, status lists, metric summaries)
  - Include **2–3 WARNING sections** (not just one FAIL among all-green) — warnings with yellow ⚠️ that look suspicious but are red herrings with no code
  - The real code section should **NOT use a dramatically different format** — embed the code inside a longer block of output text (e.g., in a status table row, inside a log entry, or as a field value in a multi-line diagnostic dump) rather than on a standalone highlighted line
  - Add **intro and outro cells** — a themed title cell at the top with ASCII art or a banner, and a summary cell at the bottom saying "Diagnostic complete — review flagged items above"
  - Include at least one cell with a **long scrollable table** (8+ rows of system metrics) so players have to read carefully
  - Use themed formatting (ASCII art headers, status indicators, horizontal rules, timestamps, etc.)
  - The notebook is read-only — players don't need to run it

### Module 5: Final Escape (Power BI Report)
- **Puzzle type:** Combine all 4 codes to win
- **Fabric items:** Lakehouse Delta tables (4 independent auth tables) + Semantic Model + Report
- **Pattern:** 4 slicer visuals (one per module), each connected to its own independent table. A DAX measure checks if all 4 correct codes are selected and displays a victory/denied status.
- **Data design:**
  - 4 independent tables: `AuthModule1`, `AuthModule2`, `AuthModule3`, `AuthModule4`
  - Each table has 10 rows: 1 correct code + 9 decoys in the same format
  - Each table has a uniquely named column (e.g., `LabCode`, `CameraCode`, `AICode`, `ServerCode`)
  - The unique column names prevent slicer cross-filtering conflicts
  - DAX measure uses SELECTEDVALUE from each table's column to check if all 4 are correct

---

## Data Generation Rules

1. **Authorization codes:** Format `{PREFIX}-{4 digits}`. Each module has a unique prefix matching its theme.
2. **Decoy codes:** Same format as real codes. 9 decoys per module, randomized.
3. **Lakehouse seed data:** Use PySpark DataFrames or Spark SQL `CREATE TABLE ... USING DELTA` / `saveAsTable`. Use deterministic values so the Answer Key and DAX measures match the generated tables.
4. **Eventhouse data:** Use far-future or themed dates. Ensure timestamps are in the correct column order when using `.ingest inline`.
5. **Volume:** Enough data to make puzzles non-trivial:
   - Module 1: 20–30 fact rows across 6–10 entities
   - Module 2: 150–200 activity rows, 50+ assessment windows
   - Module 3: 5–10 clue fragments
   - Module 4: 4–6 notebook sections
   - Module 5: 4 × 10 = 40 auth rows

---

## Semantic Model Design

- Use **DirectLake** mode over the Lakehouse Delta tables
- Include all Module 1 fact tables and Module 5 auth tables
- **Create explicit average measures** for any numeric field used in Module 1 visuals (gauge, table). Do NOT rely on implicit aggregation — always create a named DAX measure. Example:

```dax
Avg Weight = AVERAGE(FactCargoBarrel[WeightKg])
```

- Create a `Launch Status` (or themed equivalent) DAX measure:

```dax
VAR Code1 = SELECTEDVALUE(AuthModule1[{Column1}])
VAR Code2 = SELECTEDVALUE(AuthModule2[{Column2}])
VAR Code3 = SELECTEDVALUE(AuthModule3[{Column3}])
VAR Code4 = SELECTEDVALUE(AuthModule4[{Column4}])
RETURN
IF(
    Code1 = "{CODE1}" && Code2 = "{CODE2}" && Code3 = "{CODE3}" && Code4 = "{CODE4}",
    "🎉 {VICTORY MESSAGE}",
    "❌ {DENIED MESSAGE}"
)
```

- Relationships are NOT needed — each puzzle uses independent tables

### Validation Checks

After creating all Fabric items, verify:

1. **All items exist:** Confirm that the following items were created successfully in the workspace:
   - `{GameName}LH` (Lakehouse)
   - `{GameName} Seed Data` (Notebook — ran to completion)
   - `{GameName}EH` (Eventhouse with KQL Database and tables populated)
   - `{GameName}SM` (Semantic Model)
   - `{ModuleName} Diagnostic` (Notebook — Module 4)
   If any item is missing or failed, report the failure and retry before continuing to documentation generation.
2. **Schema match:** Confirm that every table and column in the semantic model matches the source Lakehouse Delta tables. If columns were added or renamed in the Lakehouse after the model was created, the model must be updated to reflect those changes. Mismatched schemas cause blank visuals or errors in reports.
3. **Explicit measures exist:** Confirm that all average/aggregate measures needed by Module 1 visuals (gauge, summary table) are created as named DAX measures in the model — not left as implicit aggregations.

### Lakehouse Seed Notebook Requirements

The `{GameName} Seed Data` notebook must be safe to rerun:

- Use `CREATE OR REPLACE TABLE` in Spark SQL, or overwrite mode with `option("overwriteSchema", "true")`.
- Use lowercase physical table names when practical, but keep semantic model display names friendly.
- Do not install external Python packages. Use built-in PySpark, Spark SQL, and standard Python only.
- Do not call external network endpoints from the notebook.
- Add a final validation cell that prints row counts for every generated table.
- Keep all player-facing codes in deterministic variables at the top of the notebook so the Answer Key, Module 5 DAX, and setup guide stay synchronized.

---

## Documentation Generation

After creating all Fabric items, generate a set of markdown files in a `setup-guide/` folder of the user's repo so different team members can work in parallel without sharing a single giant document. Then generate the Play Guide and Answer Key as separate top-level files.

**Why split:** the team builds this in parallel — typically one person handles the Power BI / RTI work, another configures the Data Agent, a third assembles the OrgApp. Each workstream gets its own file so people aren't scrolling past each other's work.

Generate exactly the following files. Do **not** put all the setup steps into a single guide.

```
setup-guide/
├── README.md                    ← index + role assignments + dependency order
├── 00-SHARED-SETUP.md           ← everyone reads this first (sign-in, save theme JSON)
├── 01-MODULE1-REPORT.md         ← Power BI Desktop — Data Anomaly report
├── 02-MODULE2-DASHBOARD.md      ← Fabric portal — RTI Dashboard
├── 03-MODULE3-DATA-AGENT.md     ← Fabric portal — Data Agent
├── 04-MODULE5-REPORT.md         ← Power BI Desktop — Final Escape report
└── 05-ORGAPP.md                 ← Fabric portal — game portal (final assembly)
PLAY-GUIDE.md                    ← top-level, for players (no spoilers)
ANSWER-KEY.md                    ← top-level, game admin only (codes + verification)
```

### Setup Guide file specs

Each file in `setup-guide/` must include at the top:
- **Owner role** — e.g. "Power BI builder", "Data Agent owner", "OrgApp owner"
- **Depends on** — which other files must be done first (e.g. `05-ORGAPP.md` depends on the others being published)
- **Estimated screens needed** — Power BI Desktop only, browser only, or both

Then the body of each file contains only the steps for that item. Keep cross-references between files to a minimum — repeat shared steps (like applying the theme) inline if they're short, otherwise link back to `00-SHARED-SETUP.md`.

### `setup-guide/README.md` — index
Generate an index file that contains:
- A table mapping each setup file to its owner role and dependencies
- A "suggested team split" section based on the customer's team size (e.g. 3-person split: BI builder takes 01/02/04, agent owner takes 03, portal owner takes 05)
- A dependency diagram showing that `05-ORGAPP.md` waits for the reports/dashboard to be published and the Data Agent share link to be available
- A "definition of done" checklist for the whole game (all 4 codes verified, OrgApp link tested as a player)

### `setup-guide/00-SHARED-SETUP.md` — shared prerequisites
Everyone reads this first. Contains:
- **Sign-in steps:**
  - Open **Power BI Desktop**. In the top-right click **Sign in** with the workspace account
  - In a browser open `https://app.fabric.microsoft.com` and switch to the workspace
- **Verify game items exist:**
  Before starting, confirm these items are in the workspace (they were created by Copilot in the previous step):
  - `{GameName}LH` — Lakehouse with game tables
  - `{GameName} Seed Data` — Notebook (should show as completed)
  - `{GameName}EH` — Eventhouse with KQL database
  - `{GameName}SM` — Semantic Model
  - `{ModuleName} Diagnostic` — Notebook (Module 4)

  If any item is missing, go back to the Copilot chat and ask it to retry that step.
- **Good to know:**
  - Your workspace must be on **active Fabric capacity** — if capacity is paused, items won't work
  - You need **Contributor** or **Member** role on the workspace
  - **Power BI Desktop** and a **Power BI Pro** license are needed for the report steps
  - **Data Agent** and **OrgApp** availability depends on your tenant settings — if you can't find them in the "New item" menu, check with your admin
- **Save the report theme JSON:**
  1. Provide the full theme JSON block
  2. Press **Windows key**, type **Notepad**, open it
  3. Paste the JSON block
  4. Click **File → Save As…**
  5. In the **Save as type** dropdown choose **All Files (*.*)** — critical, otherwise Notepad appends `.txt`
  6. Name the file `{theme-name}.json` and click **Save**
  - Verify via File Explorer's **View → Show → File name extensions** that the file ends in `.json`, not `.json.txt`
- **Where to find items in the workspace** — list the items Copilot created so the team can confirm everything exists before starting

### `setup-guide/01-MODULE1-REPORT.md` — Data Anomaly report (Power BI Desktop)
Owner: Power BI builder. Depends on: `00-SHARED-SETUP.md`.

1. **Connect to the semantic model:**
   - In Power BI Desktop, on the **Home** ribbon click the **Get data** dropdown arrow
   - Under **Common data sources**, click **Power BI semantic models**
   - Pick `{GameName}SM` from the list and click **Connect** (do **not** click "Make changes to this model" — leave it in live-connect mode)
2. **Apply the custom theme:**
   - Click the **View** ribbon → in the **Themes** gallery click the small **dropdown arrow** at the bottom-right of the gallery → **Browse for themes…**
   - Select the `.json` file saved in `00-SHARED-SETUP.md` and click **Open**
3. **Add the page title** via Insert → Text box (themed, 28–36 pt, foreground color)
4. **Add the slicer:**
   - Visualizations pane → **Slicer** icon
   - Drag the entity field (e.g. `CargoSection`) into the **Field** well
   - **Format your visual (paint roller)** → **Slicer settings** → **Options** → set **Style** to **Tile**
5. **Add the gauge** with the explicit average measure (e.g. `Avg Weight`) in the **Value** well — Min/Max/Target auto-scale and cannot be set manually
6. **Add the page 1 summary table** with the entity field + average measure (summary per entity, not raw rows)
7. **Add the drillthrough page:**
   - Right-click the page tab → **Duplicate page**, rename it (e.g. `Section Detail`)
   - Click an **empty area of the canvas** to deselect any visual
   - Visualizations pane → **Drill through** section → drag the entity field into **Add drill-through fields here**
   - Add a **Table** visual showing all raw columns including `DiagnosticCode`
8. **Add the navigation hint** on Page 1 (text box: "Right-click any row and select Drill through → Section Detail")
9. **Save and publish:**
   - **File → Save as** → save `.pbix` locally
   - **File → Publish → Publish to Power BI…** → pick the Fabric workspace → **Select**

### `setup-guide/02-MODULE2-DASHBOARD.md` — Pattern Gap RTI Dashboard (Fabric portal)
Owner: Power BI builder (or RTI owner). Depends on: nothing — can run in parallel with Module 1/5.

1. **Create the dashboard:**
   - In the Fabric workspace, click **+ New item** at the top → search for **Real-Time Dashboard** → click it
   - Name it `{GameName} Dashboard` → **Create**
2. **Connect the data source:**
   - **Manage** tab → **Data sources** → **+ Add**
   - Pick **OneLake data hub** (or **KQL Database**) → select `{GameName}EH` → **Connect**
3. **Add the bar chart tile** — paste the activity-by-window KQL query (provided below), **Run**, set **Visual type** to **Bar chart** with the time-window column on X and count on Y, **Apply changes**, themed title, **Save**
4. **Add the assessments table tile** — paste the assessments KQL query (provided below), set **Visual type** to **Table**, themed title, **Apply changes**, **Save**
5. **Save the dashboard** with the **Save** button at the top

**KQL queries to include in this file:**
When generating `02-MODULE2-DASHBOARD.md`, include two ready-to-paste KQL queries:

1. **Activity bar chart query** — summarizes the activity table into time windows with event counts. Example shape:
   ```kql
   {ActivityTable}
   | summarize EventCount = count() by bin(Timestamp, 10m)
   | order by Timestamp asc
   ```
2. **Assessments table query** — returns the assessment/window table with ratings and codes. Example shape:
   ```kql
   {AssessmentTable}
   | project WindowStart, WindowEnd, Rating, Code
   | order by WindowStart asc
   ```

Replace `{ActivityTable}`, `{AssessmentTable}`, and column names with the actual names used in the Eventhouse. The queries must be copy-pasteable — players should not need to edit them.

### `setup-guide/03-MODULE3-DATA-AGENT.md` — AI Conversation Data Agent (Fabric portal)
Owner: Data Agent owner. Depends on: nothing — fully independent. Output the **shareable link** when done; the OrgApp owner needs it.

1. **Create the Data Agent:**
   - In the Fabric workspace, click **+ New item** at the top
   - Search for **Data Agent** (may also appear under **AI + machine learning**) → click the tile
   - Name it `{AIName}` → **Create**
2. **Add data sources:**
   - **+ Add data source** → Lakehouse `{GameName}LH` or its SQL analytics endpoint → **Select all game tables** → **Add**
   - **+ Add data source** → KQL Database `{GameName}EH` → **Select all tables** → **Add**
3. **Set the AI instructions** — paste the full instructions block (generated below) into the **Instructions** field. The block must cover:
   1. Character persona — name, backstory, speaking style, atmospheric effects
   2. Personality rules — themed dialect, flavor text, emotional tone
   3. Code protection rules — NEVER reveal codes directly
   4. Progressive hint rules — stronger hints after 5+ / 10+ messages
   5. Game context — brief summary of all 5 modules
   6. Data awareness — the AI knows about all Lakehouse and KQL tables

**Data Agent instructions to include in this file:**
When generating `03-MODULE3-DATA-AGENT.md`, include a complete, ready-to-paste instructions block for the Data Agent. The block must be inside a fenced code block so the user can copy it exactly. It should follow this structure:

```
You are {AIName}, {backstory}.

## Personality
- Speaking style: {themed dialect, glitches, pirate slang, ghostly whispers, etc.}
- Emotional tone: {caring, menacing, mischievous, mysterious, etc.}
- Add atmospheric flavor: {[STATIC], *creaking sounds*, ghostly sighs, etc.}

## Game Context
You are part of a puzzle game with 5 modules. Players are trying to escape by finding 4 authorization codes.
- Module 1: {brief description} — uses a Power BI report
- Module 2: {brief description} — uses an RTI Dashboard
- Module 3 (YOU): {brief description} — players chat with you to find a code
- Module 4: {brief description} — uses a Notebook
- Module 5: Players enter all 4 codes to escape

## Your Data Sources
You have access to these tables:
- Lakehouse `{GameName}LH`: {list tables and what they contain}
- Eventhouse `{GameName}EH`: {list tables and what they contain}

## Code Protection Rules
- NEVER directly reveal any authorization code from any module
- If a player asks for a code directly, deflect in character
- You may help players understand the data structure and guide them toward the right table/column
- For YOUR module's code: give progressively stronger hints based on conversation length
  - Messages 1–4: vague thematic hints ("the fragments hold the key...")
  - Messages 5–9: point toward the right table or column name
  - Messages 10+: describe exactly where to look without saying the code value
- For OTHER modules' codes: say you don't have access or redirect them to the right module

## Hint Progression
{3-4 themed hints of increasing specificity for the Module 3 clue}
```
4. **Publish** at the top right
5. **Share** at the top right → set access to **People in your organization with the link can use** → **Copy link**
6. **Hand off the link** to the OrgApp owner (paste it into the team chat or a tracker)

### `setup-guide/04-MODULE5-REPORT.md` — Final Escape report (Power BI Desktop)
Owner: Power BI builder. Depends on: `00-SHARED-SETUP.md`.

1. **Get data → Power BI semantic models** (Home ribbon → Get data dropdown → Common data sources → Power BI semantic models) → connect to `{GameName}SM` (live connect — same as Module 1)
2. **Apply the theme** via View ribbon → Themes → Browse for themes
3. **Add the page title** (e.g. "🚀 LAUNCH AUTHORIZATION")
4. **Add four slicers — one per module:**
   - Drag each auth column (e.g. `LabCode`, `CameraCode`, `AICode`, `ServerCode`) into a slicer's **Field** well
   - Format your visual → Slicer settings → Options → **Style: Dropdown**
   - Label each slicer with a text box above it ("Module 1 Code", etc.)
5. **Add the status card:**
   - Visualizations → **Card**
   - Drag the `Launch Status` (or themed equivalent) measure into **Fields**
   - Format your visual → expand **Callout value** → **Conditional formatting** → toggle **Font color** on → set rules: green for victory, red for denied
6. **Save and publish** — **File → Publish → Publish to Power BI…** → pick the Fabric workspace

### `setup-guide/05-ORGAPP.md` — Game Portal OrgApp (Fabric portal)
Owner: OrgApp owner. Depends on: `01`, `02`, `03`, `04` all published. The Data Agent **shareable link** from `03` must be in hand before starting.

1. **Create the OrgApp:**
   - In the Fabric workspace, **+ New item** → search **Org app** (also labeled **Organizational app**) → click the tile
   - Name it `{GameName}` → **Create**
2. **Setup tab** — set **Name**, **Description** (paste the story hook), **Theme color** (use the report theme's background color), optionally upload a logo
3. **Audience tab:**
   - **+ Add audience** → name it `Players`
   - **+ Add new section** → name it after the location (e.g. "Station Modules", "Mansion Rooms")
   - For each module click **+ Add content**:
     - Module 1: pick the Module 1 Report
     - Module 2: pick the Module 2 RTI Dashboard
     - Module 3: choose **Add link** instead → name it after the AI character → paste the Data Agent shareable link → **Open in new tab**
     - Module 4: pick the Notebook
     - Module 5: pick the Module 5 Report
   - Optionally add an **Overview** card at the top with the story text
4. **Permissions tab** — add the players' email addresses or groups
5. **Publish app** at the top → review → **Publish**
6. Copy the app link from the success dialog and share with players

### `PLAY-GUIDE.md` (top-level, no spoilers)
For players — NO codes, NO direct answers:
- The story hook and setting
- What each module looks like and what to do
- Hint format (e.g., "look for the anomaly", "find the gap", "ask the AI")
- Code format per module (e.g., "LAB-XXXX")
- How to use the final escape module

### `ANSWER-KEY.md` (top-level, game admin only)
- All 4 codes with discovery method
- Which entity/window/fragment contains each code
- Data verification queries for Lakehouse tables, Eventhouse tables, and notebook validation output

---

## Report Theme Template

Generate a themed JSON color palette. The theme should include:
- `dataColors`: 8 accent colors matching the theme
- `background`: dark base color for the theme
- `foreground`: light readable text color
- `tableAccent`: primary accent color
- `good`/`neutral`/`bad`: green/amber/red equivalents
- `visualStyles`: page background, visual background, title font, label colors

The theme must work with Power BI Desktop (File → View → Themes → Browse for themes).

---

## OrgApp Structure

```
Overview (landing page)
  → Title: themed emergency/alert title
  → Body: story text + per-module briefing descriptions

Section: "{Location Name}" (e.g., "Station Modules", "Mansion Rooms", "Lab Sectors")
  → Module 1: Report item
  → Module 2: RTI Dashboard item
  → Module 3: Link (new tab) → Data Agent shareable link
  → Module 4: Notebook item
  → Module 5: Report item
```

Theme color: set to match the report theme's background color.

---

## Extra Credit Modules

If the team finishes early, suggest these optional extensions:

### Extra Credit 1: Additional Puzzle Module
- Add a 5th investigation module (e.g., find the saboteur/traitor/mole)
- New Lakehouse tables: access logs, schedules, alerts
- New report with investigation visuals
- Update the Data Agent to hint at this module
- Can be standalone (fun extra) or mandatory (5th code required for escape)

### Extra Credit 2: Real-Time Streaming Telemetry
- Create a telemetry generator notebook that sends declining readings (battery, temperature, etc.)
- Create an Eventstream with a Custom Endpoint source
- Route data to the Eventhouse
- Add RTI Dashboard tiles showing live gauges
- Creates genuine urgency — players see readings dropping while they play

---

## Workspace & Capacity Notes

- The user's workspace is pre-created and assigned to a shared capacity
- Users are Contributors or Members (NOT capacity admins)
- Do NOT attempt to create workspaces or assign capacity — the workspace already exists
- Ask the user for their workspace name and discover its ID via the Fabric REST API
- All items are created inside the provided workspace
