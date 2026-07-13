"""Create Entra security groups locally from a teams workbook.

This script runs on the admin machine, not in Fabric. It creates or reuses one
security group per team, adds the listed members, and writes a resolved workbook
with the resulting group IDs so the Fabric notebook can stay Graph-free.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import time
from pathlib import Path

import pandas as pd
import requests


GRAPH_RESOURCE = "https://graph.microsoft.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create BIS Day security groups locally.")
    parser.add_argument("--input", default="teams-template.xlsx", help="Input workbook with TeamName and MemberEmail columns.")
    parser.add_argument("--output", default="teams-resolved.xlsx", help="Output workbook with SecurityGroupName and SecurityGroupId columns.")
    parser.add_argument("--prefix", default="bis-day", help="Workspace prefix used in group names.")
    parser.add_argument("--token", default=os.environ.get("GRAPH_TOKEN", ""), help="Optional Graph token. If omitted, uses az account get-access-token.")
    return parser.parse_args()


def get_graph_token(token_override: str) -> str:
    if token_override:
        return token_override.strip()

    az_executable = shutil.which("az") or shutil.which("az.cmd")
    command = [
        az_executable or "az",
        "account",
        "get-access-token",
        "--resource",
        GRAPH_RESOURCE,
        "--query",
        "accessToken",
        "-o",
        "tsv",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        # Fallback for Windows environments where az is available in shell but
        # not directly resolvable from Python subprocess PATH.
        shell_command = (
            "az account get-access-token --resource "
            f'"{GRAPH_RESOURCE}" --query accessToken -o tsv'
        )
        result = subprocess.run(shell_command, capture_output=True, text=True, check=False, shell=True)

    token = result.stdout.strip()
    if result.returncode != 0 or not token:
        raise RuntimeError(
            "Unable to get a Graph token. Sign in with `az login` or set GRAPH_TOKEN. "
            f"Azure CLI output: {result.stderr.strip() or result.stdout.strip()}"
        )
    return token


def escape_odata(value: str) -> str:
    return value.replace("'", "''")


def graph_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def load_teams(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path)
    required_columns = {"TeamName", "MemberEmail"}
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    return frame


def find_group_id(session: requests.Session, headers: dict[str, str], group_name: str) -> str | None:
    query = escape_odata(group_name)
    response = session.get(
        f"{GRAPH_RESOURCE}/v1.0/groups?$filter=displayName eq '{query}'",
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    groups = response.json().get("value", [])
    return groups[0]["id"] if groups else None


def create_group(session: requests.Session, headers: dict[str, str], group_name: str, team_name: str) -> str:
    body = {
        "displayName": group_name,
        "description": f"BIS Day team workspace contributors - {team_name}",
        "mailEnabled": False,
        "mailNickname": group_name.replace("-", ""),
        "securityEnabled": True,
        "groupTypes": [],
    }
    response = session.post(f"{GRAPH_RESOURCE}/v1.0/groups", headers=headers, json=body, timeout=60)
    if response.status_code == 201:
        return response.json()["id"]
    if response.status_code == 400 and "already exists" in response.text.lower():
        existing_id = find_group_id(session, headers, group_name)
        if existing_id:
            return existing_id
    raise RuntimeError(f"Failed to create group {group_name}: {response.status_code} {response.text}")


def resolve_user_id(session: requests.Session, headers: dict[str, str], email: str) -> str | None:
    response = session.get(f"{GRAPH_RESOURCE}/v1.0/users/{email}", headers=headers, timeout=60)
    if response.status_code == 200:
        return response.json()["id"]
    return None


def add_member(session: requests.Session, headers: dict[str, str], group_id: str, user_id: str) -> str:
    response = session.post(
        f"{GRAPH_RESOURCE}/v1.0/groups/{group_id}/members/$ref",
        headers=headers,
        json={"@odata.id": f"{GRAPH_RESOURCE}/v1.0/directoryObjects/{user_id}"},
        timeout=60,
    )
    if response.status_code == 204:
        return "added"
    if response.status_code == 400 and "already exist" in response.text.lower():
        return "already_member"
    return f"failed: {response.status_code}"


def write_resolved_workbook(source: pd.DataFrame, resolved_groups: dict[str, dict[str, str]], output_path: Path) -> None:
    resolved = source.copy()
    resolved["SecurityGroupName"] = resolved["TeamName"].map(lambda team: resolved_groups[team]["name"])
    resolved["SecurityGroupId"] = resolved["TeamName"].map(lambda team: resolved_groups[team]["id"])
    resolved.to_excel(output_path, index=False)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    frame = load_teams(input_path)
    teams = frame.groupby("TeamName")["MemberEmail"].apply(list).to_dict()

    print(f"Loaded {len(frame)} rows from {input_path}")
    print(f"Found {len(teams)} teams")

    token = get_graph_token(args.token)
    headers = graph_headers(token)
    session = requests.Session()

    resolved_groups: dict[str, dict[str, str]] = {}
    results: list[dict[str, object]] = []

    for team_name, member_emails in teams.items():
        group_name = f"sg-{args.prefix}-{team_name}"
        print(f"\nTeam: {team_name}")
        print(f"  Group: {group_name}")

        group_id = find_group_id(session, headers, group_name)
        if group_id:
            print(f"  Reused group: {group_id}")
        else:
            group_id = create_group(session, headers, group_name, team_name)
            print(f"  Created group: {group_id}")

        added = 0
        missing_members: list[str] = []
        for email in member_emails:
            user_id = resolve_user_id(session, headers, email)
            if not user_id:
                print(f"    Missing user: {email}")
                missing_members.append(email)
                continue
            member_status = add_member(session, headers, group_id, user_id)
            print(f"    {email}: {member_status}")
            if member_status in {"added", "already_member"}:
                added += 1

        resolved_groups[team_name] = {"name": group_name, "id": group_id}
        results.append(
            {
                "team": team_name,
                "group": group_name,
                "group_id": group_id,
                "members_total": len(member_emails),
                "members_resolved": added,
                "members_missing": len(missing_members),
            }
        )
        time.sleep(0.5)

    write_resolved_workbook(frame, resolved_groups, output_path)

    print("\nSUMMARY")
    print(pd.DataFrame(results).to_string(index=False))
    print(f"\nResolved workbook written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
