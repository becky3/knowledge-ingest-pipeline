import subprocess
import json
import shutil
import os
import sys

def get_gh_command():
    gh_path = shutil.which("gh")
    if gh_path:
        return [gh_path]
    
    # Fallback to hardcoded path on Windows if not in PATH (development environment specific)
    win_path = r"C:\Program Files\GitHub CLI\gh.exe"
    if sys.platform == "win32" and os.path.exists(win_path):
         return [win_path]
    
    return ["gh"] # Expecting it in PATH

def run_gh_command(args):
    cmd = get_gh_command() + args
    print(f"DEBUG: Running command: {cmd}", file=sys.stderr)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            shell=False,
            encoding='utf-8' # Force utf-8
        )
        # print(f"DEBUG: Output: {result.stdout[:100]}...", file=sys.stderr) 
        if not result.stdout:
            print("DEBUG: stdout is empty/None")
            return []
            
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}", file=sys.stderr)
        print(f"Raw Output: {result.stdout}", file=sys.stderr)
        return []
    except FileNotFoundError:
         print(f"Executable not found: 'gh'", file=sys.stderr)
         return []
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_reviews.py <pr_number>")
        sys.exit(1)

    pr_number = sys.argv[1]
    
    print(f"Fetching reviews for PR #{pr_number}...")

    # Fetch repo info to get owner/repo
    repo_info = run_gh_command(["repo", "view", "--json", "nameWithOwner"])
    repo_full_name = repo_info.get("nameWithOwner", "becky3/knowledge-ingest-pipeline") if isinstance(repo_info, dict) else "becky3/knowledge-ingest-pipeline"

    # Fetch review comments (inline comments)
    comments = run_gh_command(["api", f"repos/{repo_full_name}/pulls/{pr_number}/comments"])
    
    # Fetch top-level reviews
    reviews = run_gh_command(["api", f"repos/{repo_full_name}/pulls/{pr_number}/reviews"])

    print("\n" + "="*80)
    print(f"PR #{pr_number} REVIEWS")
    print("="*80 + "\n")

    # Group inline comments by path
    comments_by_file = {}
    for c in comments:
        path = c.get("path", "Unknown")
        if path not in comments_by_file:
            comments_by_file[path] = []
        comments_by_file[path].append(c)

    for path, file_comments in comments_by_file.items():
        print(f"FILE: {path}")
        print("-" * len(f"FILE: {path}"))
        for c in file_comments:
            line = c.get("line") or c.get("original_line")
            user = c.get("user", {}).get("login", "Unknown")
            body = c.get("body", "").replace("\n", "\n  ")
            created_at = c.get("created_at")
            
            print(f"Line {line} | {user} ({created_at}):")
            print(f"  {body}")
            print("-" * 40)
        print("\n")

    print("\n" + "="*80)
    print("GENERAL REVIEWS")
    print("="*80 + "\n")
    
    for r in reviews:
        state = r.get("state")
        # if state == "COMMENTED" and not r.get("body"):
        #     continue # Skip empty comments
            
        user = r.get("user", {}).get("login", "Unknown")
        body = r.get("body", "").replace("\n", "\n  ")
        submitted_at = r.get("submitted_at")
        
        print(f"User: {user} | State: {state} | {submitted_at}")
        print(f"  {body}")
        print("-" * 40)

if __name__ == "__main__":
    main()
