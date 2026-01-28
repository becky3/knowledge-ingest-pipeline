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

def fetch_review_threads_graphql(owner, repo, pr_number):
    query = """
    query($owner:String!, $name:String!, $pr:Int!) {
      repository(owner:$owner, name:$name) {
        pullRequest(number:$pr) {
          reviewThreads(last: 50) {
            nodes {
              isResolved
              path
              line
              originalLine
              comments(first: 1) {
                nodes {
                  body
                  author { login }
                  createdAt
                }
              }
            }
          }
        }
      }
    }
    """
    
    # Construct fields correctly for gh api graphql
    args = [
        "api", "graphql",
        "-f", f"query={query}",
        "-F", f"owner={owner}",
        "-F", f"name={repo}",
        "-F", f"pr={int(pr_number)}"
    ]
    
    return run_gh_command(args)

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_reviews.py <pr_number> [--all]")
        sys.exit(1)

    pr_number = sys.argv[1]
    show_all = "--all" in sys.argv
    
    print(f"Fetching reviews for PR #{pr_number}...")

    # Fetch repo info to get owner/repo
    repo_info = run_gh_command(["repo", "view", "--json", "nameWithOwner"])
    if not isinstance(repo_info, dict) or "nameWithOwner" not in repo_info:
        print("Error: Unable to determine repository information from 'gh repo view'.")
        sys.exit(1)
    
    repo_full_name = repo_info["nameWithOwner"]
    owner, repo_name = repo_full_name.split("/", 1)

    # Use GraphQL to get threads with resolved status
    data = fetch_review_threads_graphql(owner, repo_name, pr_number)
    
    threads = []
    if data and "data" in data:
        threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]

    print("\n" + "="*80)
    print(f"PR #{pr_number} UNRESOLVED THREADS" + (" (Showing ALL)" if show_all else ""))
    print("="*80 + "\n")

    unresolved_count = 0
    
    for thread in threads:
        is_resolved = thread.get("isResolved", False)
        
        if is_resolved and not show_all:
            continue
            
        unresolved_count += 1
        path = thread.get("path", "Unknown")
        # Line info is sometimes top-level or on the comment
        line = thread.get("line") or thread.get("originalLine") 
        
        comments = thread.get("comments", {}).get("nodes", [])
        if not comments:
            continue
            
        first_comment = comments[0]
        user = first_comment.get("author", {}).get("login", "Unknown")
        body = first_comment.get("body", "").replace("\n", "\n  ")
        created_at = first_comment.get("createdAt")
        status_str = "[RESOLVED]" if is_resolved else "[OPEN]"

        print(f"{status_str} FILE: {path}")
        print("-" * 60)
        print(f"Line {line} | {user} ({created_at}):")
        print(f"  {body}")
        print("-" * 60)
        print("\n")

    if unresolved_count == 0:
        print("No unresolved review threads found! Good job!")
    




if __name__ == "__main__":
    main()
