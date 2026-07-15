# Setup Instructions: Next BIS Day Admin Workspace

Follow these steps to set up the admin workspace and run all notebooks in Fabric.

## 1️⃣ Create Admin Workspace in Fabric

1. Open [fabric.microsoft.com](https://fabric.microsoft.com)
2. **New → Workspace**
3. Name it: **`next-bis-day-admin`**
4. Click **Create**

## 2️⃣ Add Lakehouse to Admin Workspace

1. In the workspace, click **+ New item** (top left)
2. Select **Lakehouse**
3. Name it: **`admin-data`** (or any name you prefer)
4. Click **Create**

The workspace now has a Lakehouse where you'll store Excel files and notebooks.

## 3️⃣ Prepare & Upload Excel Template

### Step 1: Download the template from the repo

1. Go to [this repo](https://github.com/ineslantero/next-bis-day-admin)
2. Download `teams-template.xlsx` to your computer

### Step 2: Update the Excel file with real data

1. Open `teams-template.xlsx` in Excel and fill in:
   - **Column A (TeamName)**: Use names like `team01`, `team02`, ... `team10`
   - **Column B (MemberEmail)**: Real email addresses of participants
   - Keep the same team name repeated for all 5 members on that team
2. Save the file

### Step 3: Upload to your Lakehouse

1. In your admin workspace, open the **Lakehouse**
2. Click **Files** in the explorer pane (left side)
3. Click **Upload files**
4. Select the updated `teams-template.xlsx` from your computer
5. Click **Upload**

**Example:**

| TeamName | MemberEmail |
|----------|------------|
| team01 | alice@company.com |
| team01 | bob@company.com |
| team01 | carol@company.com |
| team01 | dave@company.com |
| team01 | eve@company.com |
| team02 | frank@company.com |
| ... | ... |

## 4️⃣ Download & Import Notebooks

You have three notebooks to run in sequence:

| Notebook | Purpose |
|----------|----------|
| **01-create-workspaces.ipynb** | Create workspaces & add individual users |
| **02-add-security-group-viewer.ipynb** | (Optional) Add security group as Viewer |
| **03-cleanup-workspaces.ipynb** | Delete workspaces after event |

### Import Notebooks via Upload

1. In your admin workspace, go to the **Data Engineering** home (or workspace home)
2. Click **Import notebook** → **From this computer**
3. Download the `.ipynb` files from [this repo](https://github.com/ineslantero/next-bis-day-admin):
   - `01-create-workspaces.ipynb`
   - `02-add-security-group-viewer.ipynb`
   - `03-cleanup-workspaces.ipynb`
4. Select all three `.ipynb` files and click **Upload**
5. Once imported, the notebooks appear in your workspace ready to configure and run

> **Alternatively:** You can open each notebook in the repo on GitHub, copy the raw code, create a new notebook in Fabric, and paste the content.

## 5️⃣ Run: Create Workspaces

1. Open **`01-create-workspaces`** notebook
2. **Edit configuration:**
   - Line 3: `EXCEL_PATH = "Files/teams-template.xlsx"` ← Keep as is
   - Line 4: `WORKSPACE_PREFIX = "bis-day"` ← Keep as is (creates `bis-day-team01`, etc.)
   - Line 5: **`CAPACITY_ID`** ← **UPDATE with your Fabric capacity ID**
   - Line 6: `DRY_RUN = True` ← First run with True to preview
3. Click **Run all** (or run cells one by one)
4. Review the output to ensure it looks correct
5. Change `DRY_RUN = False` and run again to create workspaces

**Output:** `teams-resolved.xlsx` file saved to Lakehouse with all workspace IDs

## 6️⃣ Run: Add Security Group (Optional)

If you want observers/admins to view all team workspaces:

1. Open **`02-add-security-group-viewer`** notebook
2. **Edit configuration:**
   - Line 3: `RESULTS_FILE = "Files/teams-resolved.xlsx"` ← Keep as is
   - Line 4: **`SECURITY_GROUP_ID`** ← Replace with your Entra security group ID
   - Line 5: **`SECURITY_GROUP_NAME`** ← Name of the group (e.g., `Event-Observers`)
   - Line 6: `DRY_RUN = True` ← First run to preview
3. Click **Run all**
4. Change `DRY_RUN = False` and run again to add the group to all workspaces

**Result:** The security group now has **Viewer** access to all team workspaces

## 7️⃣ Run: Cleanup (After Event)

When the event is over, delete all team workspaces:

1. Open **`03-cleanup-workspaces`** notebook
2. **Edit configuration:**
   - Line 3: `RESULTS_FILE = "Files/teams-resolved.xlsx"` ← Keep as is
   - Line 4: `DRY_RUN = True` ← First run to preview
   - Line 5: `SKIP_CONFIRMATION = False` ← If True, skips the confirmation prompt
3. Click **Run all**
4. When prompted, type **`yes`** to confirm deletion
5. All workspaces will be deleted

---

## 🎯 Quick Summary

| Step | Notebook | When | What |
|------|----------|------|------|
| 1 | `01-create-workspaces` | Before event | Create 10 workspaces, add users as Contributors |
| 2 | `02-add-security-group-viewer` | Before event (optional) | Add observers as Viewers to all workspaces |
| 3 | `03-cleanup-workspaces` | After event | Delete all workspaces |

---

## ⚠️ Important Notes

- **Capacity ID**: Find yours at [app.fabric.microsoft.com/capacities](https://app.fabric.microsoft.com/capacities)
- **Email addresses**: Must exist in your Entra tenant for users to be added
- **Permissions needed**:
  - Workspace creation & capacity assignment
  - User role assignment
  - Workspace deletion
- **Roles**:
  - Team members: **Contributor** (can build & edit)
  - Security group: **Viewer** (read-only)

---

## 🆘 Troubleshooting

### "Module not found: pandas"
Pandas is pre-installed in Fabric notebooks. If you see this error, restart the notebook kernel.

### "Token acquisition failed"
You may lack permissions to call Fabric APIs. Verify you have workspace creation permissions.

### Workspace creation fails
- Check `CAPACITY_ID` is correct
- Verify you have capacity assignment permissions
- Make sure email addresses exist in your Entra tenant

### Can't find `teams-resolved.xlsx`
- Ensure Step 1 ran successfully (not in dry-run mode)
- Check the file is in the Lakehouse `Files/` folder
- Try downloading and re-uploading the file
