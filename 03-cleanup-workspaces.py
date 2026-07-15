"""
Delete all team workspaces created by 01-create-workspaces.py

Usage:
    python 03-cleanup-workspaces.py [--input path/to/teams-resolved.xlsx] [--dry-run]

Requirements:
    - Azure CLI installed and authenticated: az login
    - Excel file with WorkspaceId column
    - User running this script needs Fabric workspace deletion permissions
"""

import argparse
import sys
import json
import subprocess
from pathlib import Path
import pandas as pd


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


def delete_workspace(token: str, workspace_id: str, workspace_name: str, dry_run: bool = False) -> bool:
    """Delete a Fabric workspace."""
    if dry_run:
        print(f"[DRY RUN] Would delete workspace: {workspace_name} ({workspace_id})")
        return True

    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}",
        headers=headers,
    )

    if response.status_code == 200:
        print(f"✅ Deleted workspace: {workspace_name}")
        return True
    else:
        print(f"❌ Failed to delete {workspace_name}: {response.status_code}")
        print(response.text)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Delete all team workspaces created by 01-create-workspaces.py"
    )
    parser.add_argument(
        "--input",
        default="teams-resolved.xlsx",
        help="Path to results Excel file (default: teams-resolved.xlsx)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without executing",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )

    args = parser.parse_args()

    # Load Excel file
    if not Path(args.input).exists():
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)

    print(f"📂 Loading {args.input}...")
    df = pd.read_excel(args.input)

    if "WorkspaceId" not in df.columns:
        print(f"❌ File must have 'WorkspaceId' column")
        print(f"   Found columns: {df.columns.tolist()}")
        sys.exit(1)

    # Get unique workspaces
    workspaces = df.drop_duplicates(subset=["WorkspaceId"])[["TeamName", "WorkspaceId"]].to_dict(orient="records")
    print(f"✅ Found {len(workspaces)} workspaces to delete\n")

    if not workspaces:
        print("No workspaces found to delete.")
        sys.exit(0)

    # Confirmation
    if not args.dry_run and not args.yes:
        print("⚠️  WARNING: This will DELETE all team workspaces!")
        print("Workspaces to delete:")
        for ws in workspaces:
            print(f"  - {ws['TeamName']}: {ws['WorkspaceId']}")
        print()
        response = input("Type 'yes' to confirm: ")
        if response.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)

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

    # Delete workspaces
    successful = 0
    failed = 0

    for ws in workspaces:
        team_name = ws["TeamName"]
        workspace_id = ws["WorkspaceId"]

        if delete_workspace(token, workspace_id, team_name, dry_run=args.dry_run):
            successful += 1
        else:
            failed += 1

    print(f"\n✨ Done! Deleted {successful} workspaces" + (f", {failed} failed" if failed > 0 else ""))


if __name__ == "__main__":
    main()
