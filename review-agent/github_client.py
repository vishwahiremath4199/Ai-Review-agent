"""
GitHub client for fetching PR diffs and posting review comments.
"""

import requests
from typing import tuple
import json
from models import ReviewResult


class GitHubClient:
    """
    Interface to GitHub API for PR analysis and review posting.
    """
    
    def __init__(self, token: str, repo: str):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub API token (GITHUB_TOKEN from Actions)
            repo: Repository in format "owner/repo"
        """
        self.token = token
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Media-Type": "github.v3",
        }
    
    def get_pr_diff(self, pr_number: int) -> tuple[str, list[str]]:
        """
        Fetch the unified diff and changed files for a PR.
        
        Args:
            pr_number: PR number
            
        Returns:
            Tuple of (diff_text, list_of_changed_files)
        """
        # Fetch list of changed files with patches
        files_url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}/files"
        files_response = requests.get(files_url, headers=self.headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        changed_files = []
        diff_lines = []
        
        for file_info in files_data:
            changed_files.append(file_info["filename"])
            
            # Add filename header
            diff_lines.append(f"--- a/{file_info['filename']}")
            diff_lines.append(f"+++ b/{file_info['filename']}")
            
            # Add patch if available
            if "patch" in file_info:
                diff_lines.append(file_info["patch"])
        
        diff_text = "\n".join(diff_lines)
        
        return diff_text, changed_files
    
    def post_review(self, pr_number: int, result: ReviewResult) -> None:
        """
        Post review comments back to the PR.
        
        Args:
            pr_number: PR number to post review to
            result: ReviewResult object with comments and summary
        """
        # Prepare review comments grouped by file
        review_comments = []
        
        for comment in result.comments:
            review_comments.append({
                "path": comment.file,
                "line": comment.line,
                "side": "RIGHT",  # The new code side
                "body": self._format_comment_body(comment),
            })
        
        # Create the review
        review_url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}/reviews"
        review_payload = {
            "body": self._format_summary_body(result),
            "comments": review_comments,
            "event": "COMMENT",  # COMMENT, APPROVE, or REQUEST_CHANGES
        }
        
        response = requests.post(review_url, json=review_payload, headers=self.headers)
        response.raise_for_status()
        print(f"Review posted successfully to PR #{pr_number}")
    
    def push_to_dashboard(self, dashboard_url: str, result: ReviewResult) -> None:
        """
        Push review result to the dashboard backend for storage/analytics.
        
        Args:
            dashboard_url: Base URL of the dashboard (e.g., https://dashboard.example.com/api)
            result: ReviewResult object to store
        """
        url = f"{dashboard_url.rstrip('/')}/reviews"
        payload = result.model_dump()
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Review result pushed to dashboard at {url}")
    
    @staticmethod
    def _format_comment_body(comment) -> str:
        """Format a single review comment for GitHub."""
        severity_emoji = {
            "critical": "🔴",
            "warning": "🟡",
            "suggestion": "💡",
        }
        
        emoji = severity_emoji.get(comment.severity, "")
        body = f"{emoji} **{comment.severity.upper()}** | {comment.category}\n\n"
        body += comment.explanation
        
        if comment.suggested_fix:
            body += f"\n\n**Suggested fix:**\n```\n{comment.suggested_fix}\n```"
        
        return body
    
    @staticmethod
    def _format_summary_body(result: ReviewResult) -> str:
        """Format the overall summary comment for GitHub."""
        verdict_emoji = "✅" if result.summary.critical_count == 0 else "⚠️"
        
        summary = f"{verdict_emoji} **AI Code Review Summary**\n\n"
        summary += f"**Verdict:** {result.summary.verdict}\n\n"
        summary += f"**Issues by Severity:**\n"
        summary += f"- 🔴 Critical: {result.summary.critical_count}\n"
        summary += f"- 🟡 Warning: {result.summary.warning_count}\n"
        summary += f"- 💡 Suggestion: {result.summary.suggestion_count}\n"
        
        if result.latency_seconds:
            summary += f"\n**Review Time:** {result.latency_seconds:.2f}s\n"
        if result.llm_cost_usd:
            summary += f"**API Cost:** ${result.llm_cost_usd:.4f}\n"
        
        summary += "\n_Reviewed by AI Code Review Agent • [View Rules](https://github.com/search?q=review-rules.yaml)_"
        
        return summary
