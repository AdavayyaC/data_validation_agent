"""
Validation Logger — SQLite-backed audit trail.
Every validation event is timestamped and queryable.
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS validation_runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT,
            agent_mode TEXT,
            dataset TEXT,
            total_records INTEGER,
            passed INTEGER,
            warnings INTEGER,
            critical INTEGER,
            summary_json TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS validation_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            layer TEXT,
            record_id TEXT,
            field TEXT,
            severity TEXT,
            message TEXT,
            regulation TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_run(run_id: str, agent_mode: str, dataset: str,
            total: int, passed: int, warnings: int, critical: int, summary: dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO validation_runs
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (run_id, datetime.now().isoformat(), agent_mode, dataset,
          total, passed, warnings, critical, json.dumps(summary)))
    conn.commit()
    conn.close()


def log_event(run_id: str, layer: str, record_id: str,
              field: str, severity: str, message: str, regulation: str = ""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO validation_events
        (run_id, layer, record_id, field, severity, message, regulation, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (run_id, layer, record_id, field, severity,
          message, regulation, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_recent_runs(limit: int = 10) -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT run_id, timestamp, agent_mode, dataset,
               total_records, passed, warnings, critical
        FROM validation_runs
        ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows