"""
Layer 3 — ML Anomaly Detector
Uses Isolation Forest (scikit-learn) + Z-Score
This is the AI differentiator — catches what rules miss.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from core.rule_engine import RuleEngine


def validate(df: pd.DataFrame, engine: RuleEngine) -> dict:
    issues = []
    config = engine.anomaly_config
    features = [f for f in config["features"] if f in df.columns]

    if not features:
        return {
            "layer": "Layer 3 — ML Anomaly Detection",
            "issues": [],
            "total_checked": 0,
            "passed": len(df),
            "issue_count": 0
        }

    # Build numeric feature matrix (drop rows with nulls for ML)
    feature_df = df[features].copy()
    for col in features:
        feature_df[col] = pd.to_numeric(feature_df[col], errors="coerce")

    valid_mask = feature_df.notna().all(axis=1)
    feature_clean = feature_df[valid_mask]

    anomaly_records = set()

    # --- Isolation Forest ---
    if len(feature_clean) >= 5:
        iso = IsolationForest(
            contamination=config["contamination"],
            random_state=42,
            n_estimators=100
        )
        preds = iso.fit_predict(feature_clean)
        scores = iso.decision_function(feature_clean)

        for i, (orig_idx, pred) in enumerate(zip(feature_clean.index, preds)):
            if pred == -1:  # Anomaly
                row = df.iloc[orig_idx]
                record_id = str(row.get("transaction_id", f"ROW-{orig_idx}"))
                anomaly_records.add(record_id)
                confidence = round(abs(float(scores[i])), 4)
                vals = {f: round(float(feature_clean.iloc[i][f]), 4) for f in features}
                issues.append({
                    "record_id": record_id,
                    "field": ", ".join(features),
                    "severity": "WARNING",
                    "message": (
                        f"Isolation Forest flagged anomaly "
                        f"(confidence score: {confidence}) — values: {vals}"
                    ),
                    "layer": "Anomaly",
                    "regulation": "Internal Risk Policy",
                    "anomaly_score": confidence
                })

    # --- Z-Score check (per feature) ---
    zscore_thresh = config["zscore_threshold"]
    for feat in features:
        col = feature_clean[feat]
        if col.std() == 0:
            continue
        zscores = (col - col.mean()) / col.std()
        for orig_idx, z in zscores.items():
            if abs(z) > zscore_thresh:
                row = df.iloc[orig_idx]
                record_id = str(row.get("transaction_id", f"ROW-{orig_idx}"))
                if record_id not in anomaly_records:
                    anomaly_records.add(record_id)
                    issues.append({
                        "record_id": record_id,
                        "field": feat,
                        "severity": "WARNING",
                        "message": (
                            f"Z-Score outlier on '{feat}': "
                            f"value={float(col[orig_idx]):.2f}, "
                            f"z={float(z):.2f} (threshold ±{zscore_thresh})"
                        ),
                        "layer": "Anomaly",
                        "regulation": "Statistical Process Control",
                        "anomaly_score": round(abs(float(z)), 4)
                    })

    passed = len(df) - len(anomaly_records)
    return {
        "layer": "Layer 3 — ML Anomaly Detection",
        "issues": issues,
        "total_checked": len(df),
        "passed": max(0, passed),
        "issue_count": len(issues)
    }