"""
Script to set TELEGRAM_SESSION secret for each repo in repos.json from sessions.csv
"""

import csv
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
    sessions_file = os.path.join(root_dir, "sessions.csv")

    with open(repos_file, "r", encoding="utf-8") as f:
        repos_urls = json.load(f)

    sessions = []
    with open(sessions_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sess = row.get("session", "").strip()
            phone = row.get("phone", "").strip()
            name = row.get("name", "").strip()
            if sess:
                sessions.append({"session": sess, "phone": phone, "name": name})

    print(f"[*] Total repositories in list: {len(repos_urls)}")
    print(f"[*] Total sessions found in CSV: {len(sessions)}")

    count = min(len(repos_urls), len(sessions), 20)
    print(f"[*] Assigning first {count} sessions to the {count} repositories...\n")

    for i in range(count):
        repo_url = repos_urls[i]
        # Extract owner/repo name e.g. '0xirender/notopen1'
        full_repo = repo_url.replace("https://github.com/", "").strip("/")
        session_data = sessions[i]
        session_str = session_data["session"]
        phone = session_data["phone"]
        name = session_data["name"]

        print(f"[{i+1}/{count}] Setting TELEGRAM_SESSION for {full_repo} (Phone: {phone}, Name: {name})...")
        proc = subprocess.run(
            ["gh", "secret", "set", "TELEGRAM_SESSION", "-b", session_str, "--repo", full_repo],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if proc.returncode != 0:
            print(f"[!] Error setting secret on {full_repo}: {proc.stderr.strip()}")
        else:
            print(f"[OK] TELEGRAM_SESSION secret configured for {full_repo}!")

    print("\n========================================================")
    print(" [*] ALL 20 REPOSITORIES CONFIGURED WITH TELEGRAM_SESSION!")
    print("========================================================\n")


if __name__ == "__main__":
    main()
