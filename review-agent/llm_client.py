"""
LLM client for calling Anthropic Claude API and parsing review results.
"""

import json
import re
import os
from typing import Optional
from anthropic import Anthropic
from models import ReviewResult, ReviewSummary, ReviewComment, RuleSet


class LLMClient:
    """Interface to Anthropic Claude API for code reviews."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet
        
    def review_diff(
        self,
        diff_text: str,
        matched_rules: list,
        ruleset: RuleSet,
        pr_number: int,
        repo: str,
    ) -> ReviewResult:
        """
        Call Claude to review a PR diff and return structured results.
        
        Args:
            diff_text: Unified diff content
            matched_rules: Rules that matched changed files
            ruleset: Full RuleSet for general instructions
            pr_number: PR number
            repo: Repository name
            
        Returns:
            ReviewResult object
        """
        from rules_loader import format_rules_for_prompt
        
        # Build the prompt
        prompt = self._build_prompt(
            diff_text,
            matched_rules,
            ruleset,
            format_rules_for_prompt
        )
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        
        # Extract and parse response
        response_text = response.content[0].text
        
        # Extract JSON from response (handle markdown code fences)
        json_data = self._extract_json(response_text)
        parsed = json.loads(json_data)
        
        # Calculate cost (approximate: 0.003 input, 0.015 output per 1K tokens)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        llm_cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
        
        # Build ReviewResult
        comments = [ReviewComment(**c) for c in parsed.get("comments", [])]
        summary = ReviewSummary(**parsed.get("summary", {}))
        
        return ReviewResult(
            pr_number=pr_number,
            repo=repo,
            summary=summary,
            comments=comments,
            llm_cost_usd=round(llm_cost, 4),
        )
    
    def _build_prompt(self, diff_text: str, matched_rules: list, ruleset: RuleSet, format_fn) -> str:
        """Build the prompt for Claude."""
        matched_rules_text = format_fn(matched_rules)
        
        severity_guidance = ""
        if ruleset.severity_guidance:
            for severity, description in ruleset.severity_guidance.items():
                severity_guidance += f"- **{severity}**: {description}\n"
        
        prompt = f"""You are a senior software engineer performing a code review on a GitHub Pull Request.

GENERAL INSTRUCTIONS:
{ruleset.general_instructions}

APPLICABLE TEAM RULES FOR THE CHANGED FILES:
{matched_rules_text}

SEVERITY DEFINITIONS:
{severity_guidance}

PR DIFF (unified diff format, includes file paths and changed lines with line numbers):
```
{diff_text}
```

TASK:
Review the diff above. For each issue you find, identify:
- file path
- line number (from the diff's new-file line numbers)
- category (security | bug-risk | code-quality | testing | style | database | frontend)
- severity (critical | warning | suggestion)
- a concise explanation (1-3 sentences)
- a suggested fix (short code snippet or instruction, if applicable)

Also provide an overall summary: total issues by severity, and a one-paragraph verdict on whether this PR looks safe to merge.

Respond ONLY with valid JSON in this exact shape, no markdown fences, no extra text:

{{
  "summary": {{
    "verdict": "string",
    "critical_count": 0,
    "warning_count": 0,
    "suggestion_count": 0
  }},
  "comments": [
    {{
      "file": "path/to/file.py",
      "line": 42,
      "category": "security",
      "severity": "critical",
      "explanation": "string",
      "suggested_fix": "string or null"
    }}
  ]
}}"""
        
        return prompt
    
    @staticmethod
    def _extract_json(response_text: str) -> str:
        """
        Extract JSON from response, handling markdown code fences.
        
        Args:
            response_text: Raw response text from Claude
            
        Returns:
            Valid JSON string
        """
        # Try to find JSON in markdown code fences
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Otherwise, look for JSON object directly
        match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if match:
            return match.group(1)
        
        raise ValueError(f"Could not extract JSON from response: {response_text}")
