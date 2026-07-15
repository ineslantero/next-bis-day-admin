# Next BIS Day Admin

This repo provides a complete **Fabric-based workflow** to set up team workspaces for the BIS Day escape room event.

## 🎯 Workflow Overview

All work happens **in Fabric notebooks** — no local setup needed!

```
Create admin workspace → Upload Excel → Run Notebooks → Clean up after event
```

### What It Does

1. **Create Fabric workspaces** for each team (one workspace per team)
2. **Add team members** directly to their workspace as **Contributors** (can build & edit items)
3. **Assign workspaces** to your Fabric capacity
4. (Optional) **Add security group** as **Viewer** for observers/admins
5. **Delete all workspaces** after the event

---

## 🚀 Quick Start (5 minutes)

1. **See [SETUP-GUIDE.md](SETUP-GUIDE.md)** for detailed step-by-step instructions
2. **Key steps:**
   - Create a Fabric workspace named `next-bis-day-admin`
   - Add a Lakehouse to it
   - Upload & update `teams-template.xlsx` with real team emails
   - Copy the 3 notebook files into Fabric
   - Run notebooks in order: 01 → 02 (optional) → 03

---

## 📁 Files in This Repo

| File | Purpose | Where |
|------|---------|-------|
| **SETUP-GUIDE.md** | Detailed setup instructions | Read locally |
| **teams-template.xlsx** | Excel template (10 teams × 5 people) | Upload to Lakehouse |
| **01-create-workspaces.ipynb** | Create workspaces & add users | Run in Fabric |
| **02-add-security-group-viewer.ipynb** | Add security group as Viewer (optional) | Run in Fabric |
| **03-cleanup-workspaces.ipynb** | Delete workspaces after event | Run in Fabric |
| **_deprecated/** | Old local Python scripts (reference) | — |

---

## 📊 Workspace Naming

Team workspaces are automatically named:

```
bis-day-team01
bis-day-team02
...
bis-day-team10
```

Each workspace includes 5 **Contributors** (the team members from your Excel file).

---

## 🔐 User Roles

- **Team Members**: **Contributor** (can create, edit, and delete items in the workspace)
- **Security Group** (if added): **Viewer** (read-only access to monitor progress)

---

## ⚙️ Configuration

Before running notebooks, you must update:

### Notebook 1: Create Workspaces
```python
CAPACITY_ID = "YOUR_CAPACITY_ID_HERE"  # Find at https://app.fabric.microsoft.com/capacities
```

### Notebook 2: Add Security Group (Optional)
```python
SECURITY_GROUP_ID = "GROUP_ID_HERE"  # Your Entra security group ID
SECURITY_GROUP_NAME = "Group Display Name"
```

All other settings are pre-configured and reference files in the Lakehouse.

---

## 📋 Quick Summary

| Step | Notebook | When | Output |
|------|----------|------|--------|
| 1 | `01-create-workspaces` | Before event | `teams-resolved.xlsx` with workspace IDs |
| 2 | `02-add-security-group-viewer` | Before event (optional) | Security group added to all workspaces |
| 3 | `03-cleanup-workspaces` | After event | All team workspaces deleted |

---

## 🆘 Support

**First time?** Start here: [SETUP-GUIDE.md](SETUP-GUIDE.md)

**Troubleshooting?** See the troubleshooting section in SETUP-GUIDE.md

**Questions?** Check the inline notebook comments for detailed explanations.

---

## ✅ Permissions Required

- **Fabric workspace creation** (to create `bis-day-teamXX` workspaces)
- **Capacity assignment** (to assign workspaces to your Fabric capacity)
- **User role assignment** (to add users to workspaces)
- **Workspace deletion** (for cleanup after event)

If you lack any of these, contact your Fabric administrator.
