# Event Prerequisites

This checklist is sourced from the `next-bis-day` repo prerequisites and adapted into a quick preflight format.

## Required Before Event Day

- Microsoft Fabric workspace with capacity (F64+ recommended)
- Contributor or Member role on the workspace
- Power BI Pro license
- Power BI Desktop installed
- GitHub account linked to the Next GitHub Enterprise license
- GitHub Copilot license
- Azure CLI installed

## Run Local Preflight

Use the local script to validate what can be checked automatically:

```powershell
pwsh ./scripts/check-event-prereqs.ps1
```

Or in Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-event-prereqs.ps1
```

The script checks local tooling and sign-in status, then prints manual checks for Fabric permissions and licensing.
