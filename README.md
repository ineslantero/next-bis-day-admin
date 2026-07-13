# Next BIS Day Admin

This repo includes the minimum files to:

- Prepare team input in a template workbook
- Create or reuse Entra security groups locally
- Create or reuse Fabric workspaces from the resolved workbook
- Run prerequisites and local preflight checks

## Files in this Repo

- `teams-template.xlsx`: Input workbook teams should fill in.
- `01-create-security-groups.py`: Local script that creates/reuses Entra groups and writes `teams-resolved.xlsx`.
- `02-create-workspaces.ipynb`: Fabric notebook that creates/reuses workspaces and assigns capacity/roles from `teams-resolved.xlsx`.
- `EVENT-PREREQS.md`: Event prerequisites checklist.
- `scripts/check-event-prereqs.ps1`: Local prerequisites check script.

## 1) Complete the Team Template

Open `teams-template.xlsx` and fill one row per team member.

Required columns:

- `TeamName`: Team identifier used for workspace and group naming (for example: `team1`, `team2`).
- `MemberEmail`: Entra UPN/email for each participant.

Rules:

- Repeat the same `TeamName` across multiple rows for multiple members on that team.
- Use valid user emails that exist in your tenant.
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

Expected result:

- Security groups are created or reused as `sg-bis-day-<TeamName>`.
- Users are added to each group.
- `teams-resolved.xlsx` is created with `SecurityGroupName` and `SecurityGroupId`.

## 3) Run Fabric Workspace Notebook

Run `02-create-workspaces.ipynb` in Fabric.

Before running:

1. Attach the target Lakehouse.
2. Upload `teams-resolved.xlsx` to Lakehouse `Files`.
3. Confirm notebook config values:
	- `EXCEL_PATH = "Files/teams-resolved.xlsx"`
	- `WORKSPACE_PREFIX` as needed
	- `CAPACITY_ID` set to your capacity GUID
	- `DRY_RUN = False` when ready to execute

Then run all notebook cells.

Expected result:

- Workspaces are created or reused per team.
- Each workspace is assigned to the configured capacity.
- Role assignments are applied using each team's `SecurityGroupId`.

## 4) Prerequisites and Check Script

1. Review prerequisites in `EVENT-PREREQS.md`.
2. Run the local check script:

```powershell
pwsh .\scripts\check-event-prereqs.ps1
```

Alternative (Windows PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-event-prereqs.ps1
```

The script validates local tooling/sign-in and prints manual checks for licensing, permissions, and tenant settings.
