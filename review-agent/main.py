"""
Main entrypoint for the AI Code Review agent, executed by GitHub Actions.

Environment variables expected:
  - GITHUB_REPOSITORY: "owner/repo"
  - GITHUB_EVENT_PATH: Path to GitHub Actions event JSON
  - GITHUB_TOKEN: GitHub API token (provided automatically by GitHub Actions)
  - ANTHROPIC_API_KEY: Anthropic API key (from repo secrets)
  - DASHBOARD_API_URL: Optional URL to push results to dashboard backend
"""

import os
import json
import sys
import time
from pathlib import Path

from github_client import GitHubClient
from rules_loader import load_rules, match_rules_to_files
from llm_client import LLMClient
from models import ReviewResult


def main():
    """Main review agent logic."""
    try:
        # Extract GitHub context
        repo = os.environ.get("GITHUB_REPOSITORY")
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        github_token = os.environ.get("GITHUB_TOKEN")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        dashboard_url = os.environ.get("DASHBOARD_API_URL")
        
        if not all([repo, event_path, github_token, anthropic_key]):
            print("❌ Missing required environment variables")
            sys.exit(1)
        
        # Load GitHub event (contains PR number and other info)
        with open(event_path, "r") as f:
            event = json.load(f)
        
        pr_number = event.get("pull_request", {}).get("number")
        if not pr_number:
            print("❌ Could not extract PR number from event")
            sys.exit(1)
        
        print(f"🔍 Starting review of {repo} PR #{pr_number}")
        
        # Initialize clients
        gh_client = GitHubClient(token=github_token, repo=repo)
        llm_client = LLMClient(api_key=anthropic_key)
        
        # 1. Fetch PR diff
        print("📥 Fetching PR diff...")
        diff_text, changed_files = gh_client.get_pr_diff(pr_number)
        print(f"   Found {len(changed_files)} changed files")
        
        # 2. Load and match rules
        print("📋 Loading review rules...")
        rules_path = Path("review-rules.yaml")
        if not rules_path.exists():
            print("⚠️  review-rules.yaml not found, using general review only")
            ruleset = None
            matched_rules = []
        else:
            ruleset = load_rules(str(rules_path))
            matched_rules = match_rules_to_files(ruleset, changed_files)
            print(f"   Matched {len(matched_rules)} rule groups")
        
        # 3. Call LLM for review
        print("🤖 Analyzing code with Claude...")
        start_time = time.time()
        
        if ruleset:
            result = llm_client.review_diff(
                diff_text=diff_text,
                matched_rules=matched_rules,
                ruleset=ruleset,
                pr_number=pr_number,
                repo=repo,
            )
        else:
            # Fallback if no rules - create a basic ruleset
            from models import RuleSet
            basic_ruleset = RuleSet(
                version=1,
                general_instructions="Review this PR for security issues, bugs, and code quality problems.",
                rules=[],
                severity_guidance={
                    "critical": "Security vulnerabilities, data loss risk",
                    "warning": "Bugs, missing error handling",
                    "suggestion": "Style, naming, minor refactors",
                }
            )
            result = llm_client.review_diff(
                diff_text=diff_text,
                matched_rules=[],
                ruleset=basic_ruleset,
                pr_number=pr_number,
                repo=repo,
            )
        
        result.latency_seconds = time.time() - start_time
        
        print(f"   Review complete in {result.latency_seconds:.2f}s")
        print(f"   Issues: {result.summary.critical_count} critical, "
              f"{result.summary.warning_count} warning, "
              f"{result.summary.suggestion_count} suggestion")
        
        # 4. Post comments back to GitHub
        print("📝 Posting review to GitHub...")
        gh_client.post_review(pr_number, result)
        
        # 5. Optional: push to dashboard
        if dashboard_url:
            print(f"📊 Pushing results to dashboard...")
            try:
                gh_client.push_to_dashboard(dashboard_url, result)
            except Exception as e:
                print(f"⚠️  Failed to push to dashboard: {e}")
                # Don't fail the entire action if dashboard push fails
        
        print("✅ Review complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
