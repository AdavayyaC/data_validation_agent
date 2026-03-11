"""
Agent B — Full AI Agent with Groq
Every validation failure gets reasoned about by the LLM.
Shows: AI-native thinking, natural language compliance explanations.
"""
import pandas as pd
import uuid
from groq import Groq
from core.rule_engine import RuleEngine
from core import logger
from validators import schema_validator, threshold_validator, anomaly_detector, crossfield_validator


SYSTEM_PROMPT = """You are a senior compliance officer AI assistant for a financial institution.
Your role is to analyze validation failures and provide:
1. A clear, professional explanation of why this is a compliance risk
2. The potential regulatory impact
3. A specific recommended action

Be concise (3-4 sentences max). Use formal but accessible language.
Reference the specific regulation mentioned when available."""


def reason_about_issues(issues: list, model: str, api_key: str) -> str:
    """Send all issues to Groq and get a structured reasoning response."""
    client = Groq(api_key=api_key)

    if not issues:
        return "✅ No compliance issues detected. All records passed validation."

    # Format issues for the LLM
    issues_text = "\n".join([
        f"- [{i['severity']}] Record {i['record_id']}: {i['message']}"
        for i in issues[:20]  # Cap at 20 to stay within context
    ])

    prompt = f"""Analyze these compliance validation failures from a financial dataset:

{issues_text}

Provide:
1. Overall risk assessment (1-2 sentences)
2. Top 3 most critical issues with specific remediation steps
3. Recommended escalation path (who should be notified)
4. Estimated compliance risk level: LOW / MEDIUM / HIGH / CRITICAL"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.3
    )
    return response.choices[0].message.content


def run(df: pd.DataFrame, dataset_name: str = "uploaded",
        api_key: str = "", model: str = "llama-3.3-70b-versatile") -> dict:
    run_id = str(uuid.uuid4())[:8]
    engine = RuleEngine()

    results = {
        "run_id": run_id,
        "agent_mode": "B — AI Agent (Groq)",
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

    # 🤖 Agent B: Groq reasons about ALL issues
    ai_narrative = reason_about_issues(all_issues, model=model, api_key=api_key)

    results["all_issues"] = all_issues
    results["critical_count"] = len(critical)
    results["warning_count"] = len(warnings)
    results["passed_count"] = len(df) - len(set(i["record_id"] for i in critical))
    results["status"] = "CRITICAL" if critical else ("WARNING" if warnings else "PASSED")
    results["ai_narrative"] = ai_narrative
    results["model_used"] = model

    logger.log_run(
        run_id=run_id,
        agent_mode="B",
        dataset=dataset_name,
        total=len(df),
        passed=results["passed_count"],
        warnings=len(warnings),
        critical=len(critical),
        summary={"ai_model": model, "total_issues": len(all_issues)}
    )

    return results