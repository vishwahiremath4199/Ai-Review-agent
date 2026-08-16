"""
Loads and matches review rules from YAML against changed files.
"""

import yaml
from pathlib import Path
from fnmatch import fnmatch
from typing import Optional
from models import RuleSet, Rule


def load_rules(rules_path: str) -> RuleSet:
    """
    Load rules from a YAML file.
    
    Args:
        rules_path: Path to review-rules.yaml
        
    Returns:
        RuleSet object with parsed rules
        
    Raises:
        FileNotFoundError: If rules file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    with open(rules_path, "r") as f:
        data = yaml.safe_load(f)
    
    return RuleSet(
        version=data.get("version", 1),
        general_instructions=data.get("general_instructions", ""),
        rules=[Rule(**rule) for rule in data.get("rules", [])],
        severity_guidance=data.get("severity_guidance", {})
    )


def match_rules_to_files(ruleset: RuleSet, changed_files: list[str]) -> list[Rule]:
    """
    Match changed files against rule patterns.
    
    Args:
        ruleset: The RuleSet to check
        changed_files: List of file paths that changed in the PR
        
    Returns:
        List of Rule objects whose match patterns matched at least one changed file
    """
    matched_rules = []
    matched_patterns = set()
    
    for rule in ruleset.rules:
        for file_path in changed_files:
            # Use fnmatch for glob-style pattern matching
            if fnmatch(file_path, rule.match):
                # Only add each unique rule once, even if multiple files match
                if rule.match not in matched_patterns:
                    matched_rules.append(rule)
                    matched_patterns.add(rule.match)
                break
    
    return matched_rules


def format_rules_for_prompt(matched_rules: list[Rule]) -> str:
    """
    Format matched rules for inclusion in the LLM prompt.
    
    Args:
        matched_rules: List of matched Rule objects
        
    Returns:
        Formatted string suitable for the prompt
    """
    if not matched_rules:
        return "No specific rules matched the changed files. Apply general best practices."
    
    formatted = []
    for rule in matched_rules:
        formatted.append(f"\n**{rule.category.upper()} ({rule.match})**")
        for check in rule.checks:
            formatted.append(f"  - {check}")
    
    return "\n".join(formatted)
