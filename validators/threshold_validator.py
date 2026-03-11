"""
Layer 2 — Regulatory Threshold Validator
Checks: numeric ranges, regex patterns — all from rules.yaml
"""
import pandas as pd
import re
from core.rule_engine import RuleEngine


def validate(df: pd.DataFrame, engine: RuleEngine) -> dict:
    issues = []

    for idx, row in df.iterrows():
        record_id = str(row.get("transaction_id", f"ROW-{idx}"))

        # Numeric threshold checks
        for field, rule in engine.thresholds.items():
            if field not in df.columns:
                continue
            val = row.get(field)
            if pd.isna(val):
                continue
            try:
                val = float(val)
            except (ValueError, TypeError):
                issues.append({
                    "record_id": record_id,
                    "field": field,
                    "severity": rule["severity"],
                    "message": f"'{field}' value '{val}' is not numeric",
                    "layer": "Threshold",
                    "regulation": rule.get("regulation", "")
                })
                continue

            if val < rule["min"]:
                issues.append({
                    "record_id": record_id,
                    "field": field,
                    "severity": rule["severity"],
                    "message": (
                        f"'{field}' = {val:.4f} is BELOW minimum {rule['min']} "
                        f"({rule.get('regulation', '')})"
                    ),
                    "layer": "Threshold",
                    "regulation": rule.get("regulation", "")
                })
            elif val > rule["max"]:
                issues.append({
                    "record_id": record_id,
                    "field": field,
                    "severity": rule["severity"],
                    "message": (
                        f"'{field}' = {val:.4f} EXCEEDS maximum {rule['max']} "
                        f"({rule.get('regulation', '')})"
                    ),
                    "layer": "Threshold",
                    "regulation": rule.get("regulation", "")
                })

        # Regex pattern checks
        for field, rule in engine.patterns.items():
            if field not in df.columns:
                continue
            val = str(row.get(field, "")).strip()
            if val in ("", "nan"):
                continue
            if not re.match(rule["regex"], val):
                issues.append({
                    "record_id": record_id,
                    "field": field,
                    "severity": rule["severity"],
                    "message": (
                        f"'{field}' = '{val}' does not match required format "
                        f"'{rule['regex']}' ({rule.get('regulation', '')})"
                    ),
                    "layer": "Threshold",
                    "regulation": rule.get("regulation", "")
                })

    passed = len(df) - len(set(i["record_id"] for i in issues))
    return {
        "layer": "Layer 2 — Regulatory Thresholds",
        "issues": issues,
        "total_checked": len(df),
        "passed": max(0, passed),
        "issue_count": len(issues)
    }