"""
Validation Logger — SQLite audit trail + escalation log.
Every event is timestamped. Escalations are stored separately.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "output" / "audit_log.db"


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS validation_runs (
        run_id TEXT PRIMARY KEY, timestamp TEXT, agent_mode TEXT,
        dataset TEXT, total_records INTEGER, passed INTEGER,
        warnings INTEGER, critical INTEGER, escalation_level TEXT, summary_json TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS validation_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT, layer TEXT, record_id TEXT, field TEXT,
        severity TEXT, message TEXT, regulation TEXT, timestamp TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS escalation_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT, timestamp TEXT, escalation_level TEXT,
        notify TEXT, action TEXT, critical_count INTEGER,
        warning_count INTEGER, dataset TEXT
    )""")
    conn.commit()
    conn.close()


def log_run(run_id, agent_mode, dataset, total, passed, warnings, critical, escalation_level, summary):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute(
        "INSERT OR REPLACE INTO validation_runs VALUES (?,?,?,?,?,?,?,?,?,?)",
        (run_id, datetime.now().isoformat(), agent_mode, dataset,
         total, passed, warnings, critical, escalation_level, json.dumps(summary))
    )
    conn.commit(); conn.close()


def log_event(run_id, layer, record_id, field, severity, message, regulation=""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute(
        "INSERT INTO validation_events (run_id,layer,record_id,field,severity,message,regulation,timestamp) VALUES (?,?,?,?,?,?,?,?)",
        (run_id, layer, record_id, field, severity, message, regulation, datetime.now().isoformat())
    )
    conn.commit(); conn.close()


def log_escalation(run_id, level, notify, action, critical_count, warning_count, dataset):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute(
        "INSERT INTO escalation_log (run_id,timestamp,escalation_level,notify,action,critical_count,warning_count,dataset) VALUES (?,?,?,?,?,?,?,?)",
        (run_id, datetime.now().isoformat(), level, notify, action, critical_count, warning_count, dataset)
    )
    conn.commit(); conn.close()


def get_recent_runs(limit=8):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.cursor().execute(
        "SELECT run_id, timestamp, agent_mode, dataset, total_records, passed, warnings, critical, escalation_level FROM validation_runs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows