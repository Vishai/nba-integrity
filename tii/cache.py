"""SQLite caching layer for raw API data and computed metrics."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "tii_cache.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS team_game_logs (
    team_id       INTEGER NOT NULL,
    season        TEXT NOT NULL,
    game_id       TEXT NOT NULL,
    game_date     TEXT NOT NULL,
    matchup       TEXT NOT NULL,
    wl            TEXT,
    w             INTEGER,
    l             INTEGER,
    pts           INTEGER,
    opp_pts       INTEGER,
    plus_minus    REAL,
    game_number   INTEGER,
    PRIMARY KEY (team_id, season, game_id)
);

CREATE TABLE IF NOT EXISTS player_game_logs (
    player_id     INTEGER NOT NULL,
    player_name   TEXT,
    team_id       INTEGER NOT NULL,
    season        TEXT NOT NULL,
    game_id       TEXT NOT NULL,
    game_date     TEXT NOT NULL,
    matchup       TEXT,
    wl            TEXT,
    minutes       REAL,
    pts           INTEGER,
    reb           INTEGER,
    ast           INTEGER,
    plus_minus    REAL,
    PRIMARY KEY (player_id, season, game_id)
);

CREATE TABLE IF NOT EXISTS standings_snapshots (
    season        TEXT NOT NULL,
    team_id       INTEGER NOT NULL,
    team_name     TEXT,
    conference    TEXT,
    wins          INTEGER,
    losses        INTEGER,
    win_pct       REAL,
    league_rank   INTEGER,
    PRIMARY KEY (season, team_id)
);

CREATE TABLE IF NOT EXISTS box_scores_advanced (
    game_id       TEXT NOT NULL,
    team_id       INTEGER NOT NULL,
    season        TEXT NOT NULL,
    off_rating    REAL,
    def_rating    REAL,
    net_rating    REAL,
    pace          REAL,
    ts_pct        REAL,
    PRIMARY KEY (game_id, team_id)
);

CREATE TABLE IF NOT EXISTS box_scores_advanced_players (
    game_id       TEXT NOT NULL,
    team_id       INTEGER NOT NULL,
    player_id     INTEGER NOT NULL,
    player_name   TEXT,
    season        TEXT NOT NULL,
    minutes       REAL,
    off_rating    REAL,
    def_rating    REAL,
    net_rating    REAL,
    usg_pct       REAL,
    ts_pct        REAL,
    PRIMARY KEY (game_id, team_id, player_id)
);

CREATE TABLE IF NOT EXISTS team_splits (
    team_id       INTEGER NOT NULL,
    season        TEXT NOT NULL,
    split_type    TEXT NOT NULL,
    gp            INTEGER,
    w             INTEGER,
    l             INTEGER,
    win_pct       REAL,
    plus_minus    REAL,
    off_rating    REAL,
    def_rating    REAL,
    net_rating    REAL,
    PRIMARY KEY (team_id, season, split_type)
);

CREATE TABLE IF NOT EXISTS computed_metrics (
    case_id       TEXT NOT NULL,
    team_id       INTEGER NOT NULL,
    season        TEXT NOT NULL,
    component     TEXT NOT NULL,
    data_json     TEXT NOT NULL,
    score         REAL,
    computed_at   TEXT NOT NULL,
    PRIMARY KEY (case_id, component)
);
"""


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    conn.executescript(_SCHEMA)
    conn.close()


def has_data(table: str, **where) -> bool:
    """Check if any rows exist matching the WHERE conditions."""
    conn = _get_conn()
    clauses = " AND ".join(f"{k} = ?" for k in where)
    vals = list(where.values())
    cur = conn.execute(f"SELECT 1 FROM {table} WHERE {clauses} LIMIT 1", vals)
    result = cur.fetchone() is not None
    conn.close()
    return result


def count_rows(table: str, **where) -> int:
    """Count rows matching WHERE conditions."""
    conn = _get_conn()
    clauses = " AND ".join(f"{k} = ?" for k in where)
    vals = list(where.values())
    cur = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {clauses}", vals)
    result = cur.fetchone()[0]
    conn.close()
    return result


def store_df(table: str, df: pd.DataFrame, if_exists: str = "replace"):
    """Write a DataFrame to a cache table."""
    conn = _get_conn()
    df.to_sql(table, conn, if_exists=if_exists, index=False)
    conn.close()


def append_df(table: str, df: pd.DataFrame):
    """Append rows to a cache table, ignoring duplicates."""
    conn = _get_conn()
    df.to_sql(table, conn, if_exists="append", index=False)
    conn.close()


def upsert_df(table: str, df: pd.DataFrame):
    """Insert rows, replacing on primary key conflict."""
    conn = _get_conn()
    if df.empty:
        conn.close()
        return
    cols = list(df.columns)
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    sql = f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})"
    conn.executemany(sql, df.values.tolist())
    conn.commit()
    conn.close()


def load_df(table: str, **where) -> pd.DataFrame:
    """Load rows from a cache table as a DataFrame."""
    conn = _get_conn()
    if where:
        clauses = " AND ".join(f"{k} = ?" for k in where)
        vals = list(where.values())
        df = pd.read_sql_query(f"SELECT * FROM {table} WHERE {clauses}", conn, params=vals)
    else:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df


def store_computed(case_id: str, team_id: int, season: str, component: str,
                   data: dict, score: float | None = None):
    """Store a computed metric result."""
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO computed_metrics "
        "(case_id, team_id, season, component, data_json, score, computed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (case_id, team_id, season, component, json.dumps(data),
         score, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def load_computed(case_id: str, component: str) -> dict | None:
    """Load a computed metric result, or None if not found."""
    conn = _get_conn()
    cur = conn.execute(
        "SELECT data_json, score FROM computed_metrics "
        "WHERE case_id = ? AND component = ?",
        (case_id, component),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return {"data": json.loads(row[0]), "score": row[1]}


# Initialize on import
init_db()
