"""
Layer 1 — Schema & Missing Value Validator
Checks: required fields, nulls, data types
"""
import pandas as pd
from core.rule_engine import RuleEngine


def validate(df: pd.DataFrame, engine: RuleEngine) -> dict:
    issues = []
    required = engine.required_fields

    for idx, row in df.iterrows():
        record_id = str(row.get("transaction_id", f"ROW-{idx}"))

        # Missing value check
        for field in required:
            if field not in df.columns:
                issues.append({
                    "record_id": record_id,
                    "field": field,
                    "severity": "CRITICAL",
                    "message": f"Required column '{field}' is missing from dataset",
                    "layer": "Schema",
                    "regulation": "Data Integrity Standard"
                })
            elif pd.isna(row.get(field)) or str(row.get(field, "")).strip() == "":
                issues.append({
                    "record_id": record_id,
                    "field": field,
                    "severity": "CRITICAL",
                    "message": f"Required field '{field}' is null or empty",
                    "layer": "Schema",
                    "regulation": "Data Integrity Standard"
                })

    passed = len(df) - len(set(i["record_id"] for i in issues if i["severity"] == "CRITICAL"))
    return {
        "layer": "Layer 1 — Schema & Missing Values",
        "issues": issues,
        "total_checked": len(df) * len(required),
        "passed": max(0, passed),
        "issue_count": len(issues)
    }