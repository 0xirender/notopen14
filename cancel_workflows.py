"""
Script to cancel all running or queued GitHub Action workflow runs across all repos in repos.json.
"""

import json
import os
import subprocess
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    repos_file = os.path.join(root_dir, "repos.json")

    if not os.path.exists(repos_file):
        print(f"[!] Error: {repos_file} not found.")
        sys.exit(1)

    with open(repos_file, "r", encoding="utf-8") as f:
        repos_urls = json.load(f)

    print(f"[*] Checking active workflow runs across {len(repos_urls)} repositories...\n")

    cancelled_count = 0

    for idx, repo_url in enumerate(repos_urls, 1):
        full_repo = repo_url.replace("https://github.com/", "").strip("/")
        print(f"[{idx}/{len(repos_urls)}] Checking {full_repo}...")

        # Fetch runs in progress or queued
        res = subprocess.run(
            ["gh", "run", "list", "--repo", full_repo, "--json", "databaseId,status,conclusion"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if res.returncode != 0:
            print(f"[!] Failed to list runs for {full_repo}: {res.stderr.strip()}")
            continue

        try:
            runs = json.loads(res.stdout.strip())
        except json.JSONDecodeError:
            runs = []

        active_runs = [r for r in runs if r.get("status") in ("in_progress", "queued", "waiting", "requested")]

        if not active_runs:
            print(f"    [-] No active runs found on {full_repo}.")
            continue

        for r in active_runs:
            run_id = str(r["databaseId"])
            status = r.get("status")
            print(f"    [*] Cancelling Run ID: {run_id} (Status: {status})...")
            cancel_res = subprocess.run(
                ["gh", "run", "cancel", run_id, "--repo", full_repo, "--force"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            if cancel_res.returncode == 0:
                print(f"    [OK] Run {run_id} cancellation requested.")
                cancelled_count += 1
            else:
                print(f"    [!] Error cancelling run {run_id}: {cancel_res.stderr.strip()}")

    print("\n========================================================")
    print(f" [*] FINISHED. Total active workflow runs cancelled: {cancelled_count}")
    print("========================================================\n")


if __name__ == "__main__":
    main()
