"""
Automated Multi-Repository Deployment and Secret Configuration Script
Creates 20 repositories (notopen1 .. notopen20), commits files, pushes to GitHub,
and sets GitHub Action secrets from .env file for each repository.
"""

import os
import subprocess
import sys


def run_cmd(cmd, cwd=None, check=True):
    print(f"[RUN] {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"[STDERR] {res.stderr.strip()}")
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}: {cmd}\n{res.stderr}")
    return res


def load_env(env_path):
    secrets = {}
    if not os.path.exists(env_path):
        print(f"[WARN] .env not found at {env_path}")
        return secrets
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k:
                secrets[k] = v
    return secrets


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(root_dir, ".env")
    
    # 1. Parse secrets from .env
    secrets = load_env(env_file)
    print(f"[*] Found {len(secrets)} secrets to set: {list(secrets.keys())}")

    # 2. Configure local git repo
    git_dir = os.path.join(root_dir, ".git")
    if not os.path.exists(git_dir):
        run_cmd("git init -b main", cwd=root_dir)
        run_cmd("git config user.name \"0xirender\"", cwd=root_dir)
        run_cmd("git config user.email \"0xirender@users.noreply.github.com\"", cwd=root_dir)
    else:
        run_cmd("git branch -M main", cwd=root_dir, check=False)
    
    run_cmd("git add -A", cwd=root_dir)
    # Check if there are changes to commit
    st = subprocess.run("git status --porcelain", shell=True, cwd=root_dir, capture_output=True, text=True)
    if st.stdout.strip():
        run_cmd('git commit -m "Initial commit Telegram Automation"', cwd=root_dir)
    else:
        print("[*] Git working tree clean, ready to push.")

    # 3. Target repositories
    username = "0xirender"
    repo_names = [f"notopen{i}" for i in range(1, 21)]

    print(f"\n[*] Starting deployment for {len(repo_names)} repositories...\n")

    for idx, repo in enumerate(repo_names, 1):
        full_repo = f"{username}/{repo}"
        print(f"\n========================================================")
        print(f"[{idx}/20] Processing: {full_repo}")
        print(f"========================================================")

        # Check if repo exists, create if not
        check_res = subprocess.run(f"gh repo view {full_repo}", shell=True, capture_output=True, text=True)
        if check_res.returncode != 0:
            print(f"[*] Creating repo {full_repo} on GitHub...")
            run_cmd(f"gh repo create {full_repo} --public --confirm")
        else:
            print(f"[✓] Repo {full_repo} already exists.")

        # Set GitHub Action secrets
        for k, v in secrets.items():
            print(f"[*] Setting secret {k} on {full_repo}...")
            # Use subprocess with stdin or -b flag
            proc = subprocess.run(
                ["gh", "secret", "set", k, "-b", str(v), "--repo", full_repo],
                capture_output=True,
                text=True
            )
            if proc.returncode != 0:
                print(f"[!] Warning setting secret {k}: {proc.stderr.strip()}")
            else:
                print(f"[✓] Secret {k} set.")

        # Push files to remote
        print(f"[*] Pushing root files to {full_repo}...")
        remote_url = f"https://github.com/{full_repo}.git"
        push_cmd = f"git push {remote_url} main --force"
        run_cmd(push_cmd, cwd=root_dir)
        print(f"[✓] Successfully deployed and synced {full_repo}!")

    print("\n========================================================")
    print(" [★] ALL 20 REPOSITORIES CREATED, SECRETS ADDED & FILES PUSHED!")
    print("========================================================\n")


if __name__ == "__main__":
    main()
