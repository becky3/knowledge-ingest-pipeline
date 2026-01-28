import subprocess
import json
import sys
import os

GH_PATH = r"C:\Program Files\GitHub CLI\gh.exe"

def run_gh_command(args):
    cmd = [GH_PATH] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            shell=False  # No need for shell=True with absolute path
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return []
    except json.JSONDecodeError:
        print("Failed to decode JSON response", file=sys.stderr)
        return []
    except FileNotFoundError:
         print(f"Executable not found at {GH_PATH}", file=sys.stderr)
         return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_reviews.py <pr_number>")
        sys.exit(1)

    pr_number = sys.argv[1]
    
    print(f"Fetching reviews for PR #{pr_number}...")

    # Fetch review comments (inline comments)
    comments = run_gh_command(["api", f"repos/becky3/knowledge-ingest-pipeline/pulls/{pr_number}/comments"])
    
    # Fetch top-level reviews
    reviews = run_gh_command(["api", f"repos/becky3/knowledge-ingest-pipeline/pulls/{pr_number}/reviews"])

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
