"""
Agent A — Pure Engineering Pipeline
No LLM. Deterministic. Fast. Rock-solid.
Shows: architecture, rule engine, ML anomaly detection.
"""
import pandas as pd
import uuid
from core.rule_engine import RuleEngine
from core import logger
from validators import schema_validator, threshold_validator, anomaly_detector, crossfield_validator


def run(df: pd.DataFrame, dataset_name: str = "uploaded") -> dict:
    run_id = str(uuid.uuid4())[:8]
    engine = RuleEngine()

    # Run all 4 layers
    results = {
        "run_id": run_id,
        "agent_mode": "A — Pure Engine",
        "dataset": dataset_name,
        "total_records": len(df),
        "layers": []
    }

    layers = [
        schema_validator.validate(df, engine),
        threshold_validator.validate(df, engine),
        anomaly_detector.validate(df, engine),
        crossfield_validator.validate(df, engine),
    ]

    all_issues = []
    for layer_result in layers:
        results["layers"].append(layer_result)
        all_issues.extend(layer_result["issues"])

        # Log each issue to SQLite
        for issue in layer_result["issues"]:
            logger.log_event(
                run_id=run_id,
                layer=issue["layer"],
                record_id=issue["record_id"],
                field=issue["field"],
                severity=issue["severity"],
                message=issue["message"],
                regulation=issue.get("regulation", "")
            )

    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    results["all_issues"] = all_issues
    results["critical_count"] = len(critical)
    results["warning_count"] = len(warnings)
    results["passed_count"] = len(df) - len(set(i["record_id"] for i in critical))
    results["status"] = "CRITICAL" if critical else ("WARNING" if warnings else "PASSED")
    results["ai_narrative"] = None  # Agent A has no LLM narrative

    logger.log_run(
        run_id=run_id,
        agent_mode="A",
        dataset=dataset_name,
        total=len(df),
        passed=results["passed_count"],
        warnings=len(warnings),
        critical=len(critical),
        summary={"layers": len(layers), "total_issues": len(all_issues)}
    )

    return results