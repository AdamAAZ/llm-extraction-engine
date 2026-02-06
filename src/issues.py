from __future__ import annotations
from dataclasses import dataclass

SEVERITY_RANK  = {"error": 2, "warning": 1}

@dataclass(frozen=True)
class Issue:
    field: str
    severity: str
    message: str
    
def is_valid(issues: list[Issue]) -> bool:
    return all(i.severity != "error" for i in issues)

def sort_issues(issues: list[Issue]) -> list[Issue]:
    return sorted(issues, key=lambda i: SEVERITY_RANK.get(i.severity, 0), reverse=True)