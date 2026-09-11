"""
Script to trigger GitHub Actions workflow for all repositories in repos.json with a 4-second delay.
"""

import json
import os
import subprocess
import sys
import time

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

    workflow_name = "main.yml"
    gap_seconds = 4

    print(f"[*] Found {len(repos_urls)} repositories.")
    print(f"[*] Triggering workflow '{workflow_name}' with {gap_seconds}s gap between runs...\n")

    for idx, repo_url in enumerate(repos_urls, 1):
        full_repo = repo_url.replace("https://github.com/", "").strip("/")
        print(f"[{idx}/{len(repos_urls)}] Triggering workflow on {full_repo}...")

        cmd = [
            "gh",
            "workflow",
            "run",
            workflow_name,
            "--repo",
            full_repo,
        ]

        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

        if res.returncode != 0:
            print(f"[!] Failed to trigger {full_repo}: {res.stderr.strip()}")
        else:
            print(f"[OK] Workflow successfully triggered for {full_repo}!")

        # Pause between triggers (except after the last one)
        if idx < len(repos_urls):
            print(f"[*] Waiting {gap_seconds} seconds before next trigger...")
            time.sleep(gap_seconds)

    print("\n========================================================")
    print(" [*] ALL REPOSITORY WORKFLOWS TRIGGERED SUCCESSFULLY!")
    print("========================================================\n")


if __name__ == "__main__":
    main()
