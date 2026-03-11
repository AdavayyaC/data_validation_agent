"""
Layer 4 — Cross-Field Business Logic Validator
Checks relationships BETWEEN fields — what single-field rules miss.
"""
import pandas as pd
from core.rule_engine import RuleEngine


def validate(df: pd.DataFrame, engine: RuleEngine) -> dict:
    issues = []

    for idx, row in df.iterrows():
        record_id = str(row.get("transaction_id", f"ROW-{idx}"))

        for rule in engine.cross_field_rules:

            # Rule type 1: conditional requirement
            if "condition_field" in rule:
                cond_field = rule["condition_field"]
                cond_val = rule["condition_value"]
                req_field = rule["required_field"]

                actual = str(row.get(cond_field, "")).strip().upper()
                if actual == cond_val.upper():
                    req_val = str(row.get(req_field, "")).strip()
                    if not req_val or req_val.lower() == "nan":
                        issues.append({
                            "record_id": record_id,
                            "field": req_field,
                            "severity": rule["severity"],
                            "message": (
                                f"Cross-field rule '{rule['rule']}': "
                                f"'{req_field}' is required when '{cond_field}' = '{cond_val}' "
                                f"({rule.get('regulation', '')})"
                            ),
                            "layer": "Cross-Field",
                            "regulation": rule.get("regulation", "")
                        })

            # Rule type 2: allowed values enum
            elif "allowed_values" in rule:
                field = rule["field"]
                if field not in df.columns:
                    continue
                val = str(row.get(field, "")).strip().upper()
                allowed = [v.upper() for v in rule["allowed_values"]]
                if val and val != "NAN" and val not in allowed:
                    issues.append({
                        "record_id": record_id,
                        "field": field,
                        "severity": rule["severity"],
                        "message": (
                            f"'{field}' = '{val}' is not in allowed values: "
                            f"{rule['allowed_values']} ({rule.get('regulation', '')})"
                        ),
                        "layer": "Cross-Field",
                        "regulation": rule.get("regulation", "")
                    })

    passed = len(df) - len(set(i["record_id"] for i in issues))
    return {
        "layer": "Layer 4 — Cross-Field Logic",
        "issues": issues,
        "total_checked": len(df),
        "passed": max(0, passed),
        "issue_count": len(issues)
    }