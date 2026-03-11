"""
Data Validation Agent — Streamlit UI
AI Compliance Monitoring System — Agent 3
"""
import streamlit as st
import pandas as pd
import sys
import os

# Path setup so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import agent_a, agent_b, agent_c
from core.logger import get_recent_runs

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Data Validation Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0e1a; }
    .stApp { background-color: #0a0e1a; color: #e2e8f0; }

    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-critical { border-left: 4px solid #f87171; }
    .metric-warning  { border-left: 4px solid #fbbf24; }
    .metric-passed   { border-left: 4px solid #34d399; }
    .metric-info     { border-left: 4px solid #60a5fa; }

    .layer-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 10px;
    }
    .badge-critical {
        background: rgba(248,113,113,0.15);
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.3);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-warning {
        background: rgba(251,191,36,0.15);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.3);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-passed {
        background: rgba(52,211,153,0.15);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.3);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .ai-box {
        background: rgba(167,139,250,0.06);
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 10px;
        padding: 20px;
        font-family: 'Georgia', serif;
        line-height: 1.7;
        color: #c4b5fd;
    }
    div[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Data Validation Agent")
    st.markdown("*AI Compliance Monitoring — Agent 3*")
    st.divider()

    agent_mode = st.radio(
        "**Agent Mode**",
        options=["⚙️ Agent A — Pure Engine", "🤖 Agent B — Full AI", "⚡ Agent C — Hybrid"],
        index=0,
        help="A=No LLM | B=Groq reasons every issue | C=Pipeline + Groq report"
    )

    st.divider()

    # API key + model only for B and C
    groq_key = ""
    selected_model = "llama-3.3-70b-versatile"

    if "Agent A" not in agent_mode:
        groq_key = st.text_input(
            "🔑 Groq API Key",
            type="password",
            placeholder="gsk_..."
        )
        selected_model = st.selectbox(
            "🤖 Groq Model",
            options=[
                "llama-3.3-70b-versatile",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "llama-3.1-8b-instant"
            ],
            index=0
        )

    st.divider()

    # Data source
    data_source = st.radio(
        "**Data Source**",
        ["📂 Use Sample Data", "📤 Upload CSV"],
        index=0
    )

    sample_choice = None
    uploaded_file = None

    if data_source == "📂 Use Sample Data":
        sample_choice = st.selectbox(
            "Select Scenario",
            ["✅ Valid Data", "⚠️ Missing Fields", "🔴 Anomalous Data"],
        )
    else:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    st.divider()
    run_btn = st.button("▶ RUN VALIDATION", use_container_width=True, type="primary")

    st.divider()
    st.markdown("**Recent Runs**")
    try:
        recent = get_recent_runs(5)
        if recent:
            for r in recent:
                st.caption(f"`{r[0]}` — {r[2]} — {r[7]}🔴 {r[6]}⚠️")
        else:
            st.caption("No runs yet")
    except Exception:
        st.caption("Log unavailable")

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 20px 0 10px'>
    <div style='font-size:11px; letter-spacing:0.4em; color:#00d4ff; margin-bottom:6px'>
        AI COMPLIANCE MONITORING SYSTEM
    </div>
    <h1 style='font-size:2.2rem; font-weight:700; margin:0;
        background: linear-gradient(135deg, #00d4ff, #a78bfa, #f472b6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        Data Validation Agent
    </h1>
    <div style='font-size:12px; color:#475569; margin-top:6px; letter-spacing:0.2em'>
        REGULATORY COMPLIANCE PIPELINE
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
def load_data(data_source, sample_choice, uploaded_file):
    base = os.path.join(os.path.dirname(__file__), "data")
    if data_source == "📂 Use Sample Data":
        mapping = {
            "✅ Valid Data":      ("sample_valid.csv",     "valid"),
            "⚠️ Missing Fields": ("sample_missing.csv",   "missing"),
            "🔴 Anomalous Data": ("sample_anomalies.csv", "anomalous"),
        }
        fname, label = mapping[sample_choice]
        df = pd.read_csv(os.path.join(base, fname))
        return df, label
    elif uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df, uploaded_file.name
    return None, None

# ─────────────────────────────────────────
# SHOW DATA PREVIEW
# ─────────────────────────────────────────
df_preview, _ = load_data(data_source, sample_choice, uploaded_file)
if df_preview is not None:
    with st.expander("📋 Data Preview", expanded=False):
        st.dataframe(df_preview, use_container_width=True, height=220)
        st.caption(f"{len(df_preview)} records × {len(df_preview.columns)} columns")

# ─────────────────────────────────────────
# RUN VALIDATION
# ─────────────────────────────────────────
if run_btn:
    df, dataset_label = load_data(data_source, sample_choice, uploaded_file)

    if df is None:
        st.error("Please select or upload a dataset first.")
        st.stop()

    if "Agent A" not in agent_mode and not groq_key:
        st.error("Please enter your Groq API key in the sidebar for Agent B/C.")
        st.stop()

    # Determine which agent to run
    with st.spinner(f"Running validation pipeline..."):
        try:
            if "Agent A" in agent_mode:
                results = agent_a.run(df, dataset_name=dataset_label)
            elif "Agent B" in agent_mode:
                results = agent_b.run(df, dataset_name=dataset_label,
                                      api_key=groq_key, model=selected_model)
            else:
                results = agent_c.run(df, dataset_name=dataset_label,
                                      api_key=groq_key, model=selected_model)
        except Exception as e:
            st.error(f"Validation error: {e}")
            st.stop()

    # ── Status Banner ──
    status = results["status"]
    status_colors = {"PASSED": "#34d399", "WARNING": "#fbbf24", "CRITICAL": "#f87171"}
    status_color = status_colors.get(status, "#94a3b8")

    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.03); border:1px solid {status_color}44;
                border-left: 4px solid {status_color}; border-radius:10px;
                padding:16px 24px; margin:16px 0; display:flex;
                align-items:center; gap:16px;'>
        <span style='font-size:1.8rem'>{"✅" if status=="PASSED" else "⚠️" if status=="WARNING" else "🔴"}</span>
        <div>
            <div style='font-size:1.1rem; font-weight:700; color:{status_color}'>
                Overall Status: {status}
            </div>
            <div style='font-size:12px; color:#64748b; margin-top:2px'>
                Run ID: {results["run_id"]} · Mode: {results["agent_mode"]} · Dataset: {results["dataset"]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics Row ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-card metric-info'>
            <div style='font-size:2rem; font-weight:700; color:#60a5fa'>{results['total_records']}</div>
            <div style='font-size:12px; color:#64748b; margin-top:4px'>TOTAL RECORDS</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card metric-passed'>
            <div style='font-size:2rem; font-weight:700; color:#34d399'>{results['passed_count']}</div>
            <div style='font-size:12px; color:#64748b; margin-top:4px'>PASSED</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card metric-warning'>
            <div style='font-size:2rem; font-weight:700; color:#fbbf24'>{results['warning_count']}</div>
            <div style='font-size:12px; color:#64748b; margin-top:4px'>WARNINGS</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='metric-card metric-critical'>
            <div style='font-size:2rem; font-weight:700; color:#f87171'>{results['critical_count']}</div>
            <div style='font-size:12px; color:#64748b; margin-top:4px'>CRITICAL</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Layer Results ──
    st.markdown("### 🔍 Validation Layers")
    layer_icons = ["🛡️", "⚖️", "🤖", "🔗"]
    layer_colors = ["#a78bfa", "#34d399", "#f59e0b", "#f87171"]

    for i, layer in enumerate(results["layers"]):
        icon = layer_icons[i] if i < len(layer_icons) else "•"
        color = layer_colors[i] if i < len(layer_colors) else "#94a3b8"
        count = layer["issue_count"]
        badge = (f"<span class='badge-critical'>{count} CRITICAL</span>"
                 if any(x["severity"] == "CRITICAL" for x in layer["issues"])
                 else f"<span class='badge-warning'>{count} WARNINGS</span>"
                 if count > 0
                 else "<span class='badge-passed'>✓ PASSED</span>")

        with st.expander(f"{icon} {layer['layer']}  —  {badge}", expanded=(count > 0)):
            if layer["issues"]:
                issues_df = pd.DataFrame(layer["issues"])[
                    ["record_id", "field", "severity", "message", "regulation"]
                ]
                # Color-code severity
                def highlight_severity(val):
                    if val == "CRITICAL":
                        return "background-color: rgba(248,113,113,0.15); color: #f87171"
                    elif val == "WARNING":
                        return "background-color: rgba(251,191,36,0.15); color: #fbbf24"
                    return ""

                styled = issues_df.style.applymap(
                    highlight_severity, subset=["severity"]
                )
                st.dataframe(styled, use_container_width=True, hide_index=True)
            else:
                st.success("All records passed this validation layer.")

    # ── AI Narrative (B & C only) ──
    if results.get("ai_narrative"):
        model_used = results.get("model_used", "")
        st.markdown(f"### 🤖 AI Compliance Analysis")
        st.caption(f"Generated by Groq · Model: `{model_used}`")
        st.markdown(f"""
        <div class='ai-box'>
            {results['ai_narrative'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

    # ── Full Issues Table ──
    if results["all_issues"]:
        st.markdown("### 📋 All Validation Issues")
        all_df = pd.DataFrame(results["all_issues"])[
            ["record_id", "layer", "field", "severity", "message", "regulation"]
        ]
        st.dataframe(all_df, use_container_width=True, hide_index=True, height=300)

        # Download button
        csv_out = all_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Issues CSV",
            data=csv_out,
            file_name=f"validation_issues_{results['run_id']}.csv",
            mime="text/csv"
        )

    # ── Save AI report as text (C mode) ──
    if results.get("ai_narrative") and "Agent C" in agent_mode:
        report_text = f"""COMPLIANCE VALIDATION REPORT
Run ID: {results['run_id']}
Mode: {results['agent_mode']}
Dataset: {results['dataset']}
Status: {results['status']}
Total: {results['total_records']} | Passed: {results['passed_count']} | Warnings: {results['warning_count']} | Critical: {results['critical_count']}

{'='*60}

{results['ai_narrative']}
"""
        st.download_button(
            label="📄 Download Full Compliance Report",
            data=report_text,
            file_name=f"compliance_report_{results['run_id']}.txt",
            mime="text/plain"
        )

else:
    # ── Empty State ──
    st.markdown("""
    <div style='text-align:center; padding:60px 20px; color:#334155'>
        <div style='font-size:3rem; margin-bottom:16px'>🛡️</div>
        <div style='font-size:1.1rem; color:#475569; margin-bottom:8px'>
            Select a dataset and agent mode, then click <strong style='color:#60a5fa'>▶ RUN VALIDATION</strong>
        </div>
        <div style='font-size:13px; color:#334155; max-width:500px; margin:0 auto; line-height:1.7'>
            Agent A runs a pure 4-layer pipeline with ML anomaly detection.<br>
            Agent B sends every failure to Groq for AI reasoning.<br>
            Agent C runs the pipeline then generates a formal compliance report.
        </div>
    </div>
    """, unsafe_allow_html=True)