# Next BIS Day Admin

This repo contains only the core files for:

- Creating/reusing Entra security groups
- Creating/reusing Fabric workspaces from a resolved workbook
- Checking local event prerequisites before the session

## Files

- `01-create-security-groups.py`: Reads team input and creates/reuses Entra groups, then outputs `teams-resolved.xlsx`.
- `02-create-workspaces.ipynb`: Reads the resolved workbook and creates/reuses Fabric workspaces, assigns capacity, and applies workspace roles.
- `EVENT-PREREQS.md`: Attendee/admin prerequisite checklist.
- `scripts/check-event-prereqs.ps1`: Local preflight script for tooling/login checks.

## Run Order

1. Complete the checklist in `EVENT-PREREQS.md`.
2. Run `scripts/check-event-prereqs.ps1` locally.
3. Run `01-create-security-groups.py` to generate `teams-resolved.xlsx`.
4. Run `02-create-workspaces.ipynb` with your `CAPACITY_ID` set.

## Notes

- The notebook expects a resolved workbook (output of step 3), not the raw template.
- Azure CLI sign-in is required for Graph/Fabric token acquisition.
