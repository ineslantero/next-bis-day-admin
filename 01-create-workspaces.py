"""
Create Fabric workspaces per team and add individual users from Excel template.

Usage:
    python 01-create-workspaces.py [--input path/to/teams.xlsx] [--dry-run]

Requirements:
    - Azure CLI installed and authenticated: az login
    - Excel file with columns: TeamName, MemberEmail
    - Fabric capacity ID configured in the script
    - User running this script needs Fabric workspace creation permissions
"""

import argparse
import sys
import json
import subprocess
from pathlib import Path
import pandas as pd


# Configuration
WORKSPACE_PREFIX = "bis-day"
CAPACITY_ID = "21F29096-B423-437C-AB24-60F1830444A2"  # Update with your capacity ID
OUTPUT_FILE = "teams-resolved.xlsx"


def run_command(cmd: list, check=True) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        raise


def get_bearer_token() -> str:
    """Get Azure bearer token for Fabric API."""
    token = run_command(
        ["az", "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com"]
    )
    token_obj = json.loads(token)
    return token_obj["accessToken"]


def create_workspace(token: str, workspace_name: str, dry_run: bool = False) -> str | None:
    """Create a Fabric workspace. Returns workspace ID."""
    if dry_run:
        print(f"[DRY RUN] Would create workspace: {workspace_name}")
        return "00000000-0000-0000-0000-000000000000"

    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "displayName": workspace_name,
    }

    response = requests.post(
        "https://api.fabric.microsoft.com/v1/workspaces",
        headers=headers,
        json=payload,
    )

    if response.status_code == 201:
        workspace_id = response.json().get("id")
        print(f"✅ Created workspace: {workspace_name} ({workspace_id})")
        return workspace_id
    elif response.status_code == 400:
        # Workspace might already exist - try to find it
        print(f"⚠️  Workspace might exist: {workspace_name}. Attempting to find...")
        existing_id = find_workspace_by_name(token, workspace_name)
        if existing_id:
            print(f"✅ Using existing workspace: {workspace_name} ({existing_id})")
            return existing_id
    else:
        print(f"❌ Failed to create workspace: {response.status_code}")
        print(response.text)
        return None


def find_workspace_by_name(token: str, workspace_name: str) -> str | None:
    """Find workspace ID by display name."""
    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(
        "https://api.fabric.microsoft.com/v1/workspaces",
        headers=headers,
    )

    if response.status_code == 200:
        for workspace in response.json().get("value", []):
            if workspace.get("displayName") == workspace_name:
                return workspace.get("id")
    return None


def assign_capacity(token: str, workspace_id: str, capacity_id: str, dry_run: bool = False) -> bool:
    """Assign capacity to workspace."""
    if dry_run:
        print(f"[DRY RUN] Would assign capacity {capacity_id} to workspace {workspace_id}")
        return True

    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {"capacityId": capacity_id}

    response = requests.post(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/assignToCapacity",
        headers=headers,
        json=payload,
    )

    if response.status_code == 200:
        print(f"  ✓ Assigned capacity {capacity_id}")
        return True
    else:
        print(f"  ✗ Failed to assign capacity: {response.status_code}")
        print(response.text)
        return False


def get_user_id(token: str, user_email: str) -> str | None:
    """Get user ID from email using Microsoft Graph."""
    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Note: This uses the Fabric API token which may not work with Graph.
    # Consider using a separate Graph token if this fails.
    response = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{user_email}",
        headers=headers,
    )

    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"  ⚠️  Could not resolve user ID for {user_email}")
        return None


def add_user_to_workspace(token: str, workspace_id: str, user_email: str, role: str = "Contributor", dry_run: bool = False) -> bool:
    """Add user to workspace with specified role."""
    if dry_run:
        print(f"[DRY RUN] Would add {user_email} as {role} to workspace {workspace_id}")
        return True

    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "principal": {
            "id": user_email,
            "type": "User",
        },
        "role": role,
    }

    response = requests.post(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/roleAssignments",
        headers=headers,
        json=payload,
    )

    if response.status_code == 200:
        print(f"    ✓ Added {user_email} as {role}")
        return True
    else:
        print(f"    ✗ Failed to add {user_email}: {response.status_code}")
        print(response.text)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create Fabric workspaces and add individual users from Excel template."
    )
    parser.add_argument(
        "--input",
        default="teams-template.xlsx",
        help="Path to input Excel file (default: teams-template.xlsx)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without executing",
    )

    args = parser.parse_args()

    # Load Excel file
    if not Path(args.input).exists():
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)

    print(f"📂 Loading {args.input}...")
    df = pd.read_excel(args.input)

    required_columns = {"TeamName", "MemberEmail"}
    missing = required_columns.difference(df.columns)
    if missing:
        print(f"❌ Missing required columns: {missing}")
        print(f"   Found columns: {df.columns.tolist()}")
        sys.exit(1)

    # Get unique teams
    teams = df["TeamName"].unique()
    print(f"✅ Found {len(teams)} teams with {len(df)} total members\n")

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")

    # Get token
    print("🔐 Getting Azure token...")
    try:
        token = get_bearer_token()
        print("✅ Token acquired\n")
    except Exception as e:
        print(f"❌ Failed to get token: {e}")
        print("   Make sure you've run 'az login' first")
        sys.exit(1)

    # Track results
    results = []

    # Create workspace for each team
    for team in teams:
        workspace_name = f"{WORKSPACE_PREFIX}-{team}"
        print(f"📦 Processing {team}...")

        # Create workspace
        workspace_id = create_workspace(token, workspace_name, dry_run=args.dry_run)
        if not workspace_id:
            print(f"  ❌ Failed to create workspace for {team}")
            continue

        # Assign capacity
        if not args.dry_run:
            assign_capacity(token, workspace_id, CAPACITY_ID, dry_run=args.dry_run)

        # Get team members
        team_members = df[df["TeamName"] == team]["MemberEmail"].tolist()

        # Add each member to workspace
        for member_email in team_members:
            add_user_to_workspace(token, workspace_id, member_email, role="Contributor", dry_run=args.dry_run)

            # Record result
            results.append({
                "TeamName": team,
                "WorkspaceName": workspace_name,
                "WorkspaceId": workspace_id,
                "MemberEmail": member_email,
                "Role": "Member",
            })

        print()

    # Save results to Excel
    if not args.dry_run and results:
        print(f"💾 Saving results to {OUTPUT_FILE}...")
        results_df = pd.DataFrame(results)
        results_df.to_excel(OUTPUT_FILE, index=False, sheet_name="Teams")
        print(f"✅ Saved {len(results)} team member assignments")
    else:
        print(f"⏭️  Skipping save (dry run mode)")

    print("\n✨ Done!")


if __name__ == "__main__":
    main()
