# Next BIS Day Admin

This repo includes the minimum files to:

- Prepare team input in a template workbook (10 teams × 5 people each)
- Create Fabric workspaces per team
- Add individual users directly to workspaces as Members
- Optionally add a security group as Viewer to all workspaces
- Clean up workspaces when done

## Workflow Overview

```
Step 1: Fill Excel template → Step 2: Create workspaces & add users → Step 3: Add security group viewer → Step 4: Cleanup
```

### Step 1: Complete the Team Template ✅

Open `teams-template.xlsx` and update it with real email addresses. The template includes 10 teams with 5 people per team (sample data).

**Required columns:**
- `TeamName`: Team identifier (example: `team01`, `team02`, ... `team10`)
- `MemberEmail`: Email address of each participant (example: `alice@company.com`)

**Rules:**
- Repeat the same `TeamName` across multiple rows for each team member
- Use valid user emails that exist in your Entra tenant

### Step 2: Create Workspaces & Add Individual Users ⚡

Run the Python script locally. It will:
1. Create a Fabric workspace for each team (prefixed with `bis-day-`)
2. Assign the workspace to your Fabric capacity
3. Add each team member directly as a **Contributor** to their team workspace

**Usage:**
```bash
# Preview changes (recommended first)
python 01-create-workspaces.py --dry-run

# Create workspaces and add users
python 01-create-workspaces.py

# Custom input file
python 01-create-workspaces.py --input path/to/teams.xlsx
```

**Output:**
- `teams-resolved.xlsx`: Records of all workspaces created and members added

**Requirements:**
- Python 3.8+ with pandas and requests
- Azure CLI installed and authenticated: `az login`
- Fabric workspace creation permissions in your tenant
- Capacity assignment permissions

### Step 3: Add Security Group as Viewer (Optional) 🔐

After workspaces are created, optionally add a security group (e.g., for event observers) as **Viewer** to all team workspaces.

**Usage:**
1. Open `02-add-security-group-viewer.ipynb` in Fabric
2. Edit configuration:
   - `RESULTS_FILE`: Path to `teams-resolved.xlsx` in Lakehouse
   - `SECURITY_GROUP_ID`: Entra group ID to add
   - `SECURITY_GROUP_NAME`: Display name of the group
   - `DRY_RUN`: Set to `False` to make changes
3. Run all cells

**Workspace naming:** `bis-day-team01`, `bis-day-team02`, ... `bis-day-team10`

**User roles:**
- Team members: **Contributor** (can build and edit items)
```
SECURITY_GROUP_ID = "12345678-1234-1234-1234-123456789012"
SECURITY_GROUP_NAME = "Event-Observers"
DRY_RUN = False
```

### Step 4: Cleanup — Delete Workspaces 🧹

After the event, delete all team workspaces.

**Usage:**
```bash
# Preview deletions (recommended first)
python 03-cleanup-workspaces.py --dry-run

# Delete all workspaces (with confirmation prompt)
python 03-cleanup-workspaces.py

# Skip confirmation
python 03-cleanup-workspaces.py --yes

# Custom input file
python 03-cleanup-workspaces.py --input path/to/teams-resolved.xlsx
```

**Requirements:**
- Azure CLI authenticated: `az login`
- Fabric workspace deletion permissions

---

## Files in This Repo

| File | Purpose |
|------|---------|
| `teams-template.xlsx` | Excel input file: 10 teams × 5 people (update with real emails) |
| `01-create-workspaces.py` | Python script: Create workspaces & add individual users |
| `02-add-security-group-viewer.ipynb` | Fabric notebook: Add security group as Viewer to all workspaces |
| `03-cleanup-workspaces.py` | Python script: Delete all team workspaces |
| `teams-resolved.xlsx` | Generated output: Record of created workspaces & members |
| `scripts/check-event-prereqs.ps1` | Local prerequisites check script |
| `EVENT-PREREQS.md` | Event prerequisites checklist |

---

## Required Permissions

### To run Step 2 (`01-create-workspaces.py`):
- Azure CLI access with `az login`
- **Fabric workspace creation permissions** in your tenant
- **Capacity assignment permissions** to assign workspaces to the target capacity
- **User role assignment permissions** to add users to workspaces

### To run Step 3 (`02-add-security-group-viewer.ipynb`):
- Fabric notebook execution permissions
- Fabric REST API access
- **Group role assignment permissions** to add security groups to workspaces

### To run Step 4 (`03-cleanup-workspaces.py`):
- Azure CLI access with `az login`
- **Fabric workspace deletion permissions** in your tenant

---

## Quick Start Checklist

- [ ] **Step 1:** Update `teams-template.xlsx` with real team names and email addresses
- [ ] **Step 2:** Run `python 01-create-workspaces.py --dry-run` to preview
- [ ] **Step 2:** Run `python 01-create-workspaces.py` to create workspaces (watch for output file `teams-resolved.xlsx`)
- [ ] **Step 3 (Optional):** Run `02-add-security-group-viewer.ipynb` in Fabric to add observer group
- [ ] **After event:** Run `python 03-cleanup-workspaces.py --dry-run` to preview deletions
- [ ] **After event:** Run `python 03-cleanup-workspaces.py` to clean up all workspaces

---

## Troubleshooting

### `az login` fails
Make sure Azure CLI is installed: `az --version`
Then authenticate: `az login`

### `ModuleNotFoundError: No module named 'pandas'`
Install dependencies:
```bash
pip install pandas requests openpyxl
```

### Workspace creation fails with 400 error
- The workspace name might already exist. The script will try to reuse it.
- Check your capacity ID is correct: `CAPACITY_ID` in the script

### Users not added to workspace
- Verify email addresses are valid Entra users in your tenant
- Check you have workspace role assignment permissions

### Can't delete workspaces
- Make sure `teams-resolved.xlsx` has the correct `WorkspaceId` column
- Verify you have Fabric workspace deletion permissions
- Keep team names short and consistent (avoid spaces/special characters when possible).

Example:

| TeamName | MemberEmail |
|----------|-------------|
| team1 | user1@contoso.com |
| team1 | user2@contoso.com |
| team2 | user3@contoso.com |

## 2) Run Security Group Script Locally

From the repo root:

```powershell
az login
python .\01-create-security-groups.py --input teams-template.xlsx --output teams-resolved.xlsx --prefix bis-day
```

How the script finds the Excel file:

- By default, the script reads the path passed in `--input`.
- In the example above, `teams-template.xlsx` means the file is expected in the current working directory.
- If you run the command from the repo root, the script will find `teams-template.xlsx` and write `teams-resolved.xlsx` back to the repo root.
- If your file is elsewhere, use a relative or absolute path, for example:

```powershell
python .\01-create-security-groups.py --input .\my-folder\teams-template.xlsx --output .\my-folder\teams-resolved.xlsx --prefix bis-day
```

Expected result:

- Security groups are created or reused as `sg-bis-day-<TeamName>`.
- Users are added to each group.
- `teams-resolved.xlsx` is created with `SecurityGroupName` and `SecurityGroupId`.

## 3) Run Fabric Workspace Notebook

Run `02-create-workspaces.ipynb` in Fabric.

Before running:

1. Attach the target Lakehouse.
2. Upload the `teams-resolved.xlsx` file produced by the local script to Lakehouse `Files`.
3. Confirm notebook config values:
	- `EXCEL_PATH = "Files/teams-resolved.xlsx"`
	- `WORKSPACE_PREFIX` as needed
	- `CAPACITY_ID` set to your capacity GUID
	- `DRY_RUN = False` when ready to execute

How the notebook finds the Excel file:

- The notebook reads the file from the Lakehouse path in `EXCEL_PATH`.
- With `EXCEL_PATH = "Files/teams-resolved.xlsx"`, it expects the workbook to be uploaded to the root of the Lakehouse `Files` area.
- If you upload it into a subfolder, update `EXCEL_PATH` to match, for example `Files/admin-input/teams-resolved.xlsx`.

Then run all notebook cells.

Expected result:

- Workspaces are created or reused per team.
- Each workspace is assigned to the configured capacity.
- Role assignments are applied using each team's `SecurityGroupId`.

## 4) Prerequisites and Check Script

Use this GitHub Player prerequisite list as the source of truth for event-day setup:

- GitHub account linked to the Next GitHub Enterprise license
- GitHub Copilot license
- VS Code installed (CLI available as `code`)
- Azure CLI installed and signed in (`az login`)
- Power BI Desktop installed
- Power BI Pro license
- `curl` available on PATH
- `jq` available on PATH
- `sqlcmd` available on PATH

1. Review prerequisites in `EVENT-PREREQS.md`.
2. Run the local check script:

```powershell
pwsh .\scripts\check-event-prereqs.ps1
```

Alternative (Windows PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-event-prereqs.ps1
```

The script validates local tooling and sign-in status, then prints any remaining manual checks.
