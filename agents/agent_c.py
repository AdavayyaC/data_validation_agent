"""
Agent C — Hybrid: Deterministic Pipeline + Groq Compliance Report
Best of both worlds: reliable validation + AI-generated narrative report.
Degrades gracefully if API is unavailable.
"""
import pandas as pd
import uuid
from groq import Groq
from core.rule_engine import RuleEngine
from core import logger
from validators import schema_validator, threshold_validator, anomaly_detector, crossfield_validator


REPORT_SYSTEM_PROMPT = """You are a compliance reporting AI for a regulated financial institution.
Generate a formal compliance validation report in the style of an official regulatory document.
Be precise, professional, and reference specific regulations where mentioned.
Structure the report clearly with sections."""


def generate_compliance_report(results: dict, model: str, api_key: str) -> str:
    """Generate a formal compliance report narrative from validation summary."""
    client = Groq(api_key=api_key)

    critical = results["critical_count"]
    warnings = results["warning_count"]
    total = results["total_records"]
    passed = results["passed_count"]

    # Summarize top issues per layer
    layer_summaries = []
    for layer in results["layers"]:
        if layer["issues"]:
            sample = layer["issues"][:3]
            layer_summaries.append(
                f"{layer['layer']}: {layer['issue_count']} issues — "
                + "; ".join(i["message"][:80] for i in sample)
            )

    summary_text = "\n".join(layer_summaries) if layer_summaries else "No issues found."

    prompt = f"""Generate a formal Compliance Validation Report based on these results:

VALIDATION SUMMARY:
- Dataset: {results['dataset']}
- Total Records: {total}
- Passed: {passed} ({round(passed/total*100, 1) if total else 0}%)
- Critical Failures: {critical}
- Warnings: {warnings}
- Overall Status: {results['status']}

LAYER FINDINGS:
{summary_text}

Generate a report with these sections:
1. Executive Summary
2. Validation Findings by Layer
3. Regulatory Risk Assessment
4. Recommended Remediation Actions
5. Escalation Requirements (if any)

Use formal compliance language. Reference specific regulations mentioned."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Report generation unavailable: {str(e)}\n\nRaw summary: {summary_text}"


def run(df: pd.DataFrame, dataset_name: str = "uploaded",
        api_key: str = "", model: str = "llama-3.3-70b-versatile") -> dict:
    run_id = str(uuid.uuid4())[:8]
    engine = RuleEngine()

    results = {
        "run_id": run_id,
        "agent_mode": "C — Hybrid (Pipeline + Groq Report)",
        "dataset": dataset_name,
        "total_records": len(df),
        "layers": []
    }

    # Same deterministic pipeline as Agent A
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

    # 🤖 Agent C: Groq writes the formal compliance report
    ai_narrative = generate_compliance_report(results, model=model, api_key=api_key)
    results["ai_narrative"] = ai_narrative
    results["model_used"] = model

    logger.log_run(
        run_id=run_id,
        agent_mode="C",
        dataset=dataset_name,
        total=len(df),
        passed=results["passed_count"],
        warnings=len(warnings),
        critical=len(critical),
        summary={"ai_model": model, "total_issues": len(all_issues)}
    )

    return results