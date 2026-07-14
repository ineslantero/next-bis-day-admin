# Next BIS Day Admin

This repo includes the minimum files to:

- Prepare team input in a template workbook
- Create or reuse Entra security groups locally
- Create or reuse Fabric workspaces from the resolved workbook
- Run prerequisites and local preflight checks

## Required Permissions

- Step 1, complete the template: no admin permissions required. You only need the participant email addresses and permission to edit the workbook.
- Step 2, run the security group script locally: you must be able to sign in with `az login` and have Entra permissions to create security groups, look up users, and add members to groups.
- Step 3, run the Fabric workspace notebook: you must have permission to create workspaces, assign them to the target capacity, and add role assignments for the team security groups. You also need access to the Lakehouse used to store `teams-resolved.xlsx`.
- Step 4, run the prerequisites check script: no admin permissions are required, but you need access to the local machine and the ability to sign in to the tools the script validates.

## Files in this Repo

- `teams-template.xlsx`: Input workbook teams should fill in.
- `01-create-security-groups.py`: Local script that creates/reuses Entra groups and writes `teams-resolved.xlsx`.
- `02-create-workspaces.ipynb`: Fabric notebook that creates/reuses workspaces and assigns capacity/roles from `teams-resolved.xlsx`.
- `EVENT-PREREQS.md`: Event prerequisites checklist.
- `scripts/check-event-prereqs.ps1`: Local prerequisites check script.

## 1) Complete the Team Template

Open `teams-template.xlsx` and fill one row per team member.

Where to save it:

- Keep the completed file in the repo root, next to `01-create-security-groups.py`.
- The simplest option is to edit the included `teams-template.xlsx` file in place and save it with the same name.
- If you save it with a different name or in a different folder, you must pass that path to the local script with `--input`.

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
