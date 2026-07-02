import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            country TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            league_id INTEGER,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            status TEXT DEFAULT 'scheduled',
            match_time DATETIME,
            odds_home REAL,
            odds_draw REAL,
            odds_away REAL,
            markets_data TEXT DEFAULT '[]',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (league_id) REFERENCES leagues(id)
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            home_team TEXT,
            away_team TEXT,
            predicted_winner TEXT NOT NULL,
            confidence REAL NOT NULL,
            score_breakdown TEXT,
            market_data TEXT,
            is_correct BOOLEAN,
            actual_result TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches(id)
        );

        CREATE TABLE IF NOT EXISTS custom_logic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condition_field TEXT NOT NULL,
            operator TEXT NOT NULL,
            condition_value REAL NOT NULL,
            logic_connector TEXT DEFAULT 'AND',
            result_recommendation TEXT NOT NULL,
            weight_modifier REAL DEFAULT 0,
            priority INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bet_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            market_type INTEGER,
            market_name TEXT,
            event_count INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT,
            name TEXT NOT NULL,
            league_id INTEGER,
            form TEXT,
            position INTEGER,
            points INTEGER,
            played INTEGER,
            won INTEGER,
            drawn INTEGER,
            lost INTEGER,
            last_updated DATETIME,
            FOREIGN KEY (league_id) REFERENCES leagues(id)
        );
    """)

    # Migration: add columns if missing (for existing DB)
    migs = [
        "ALTER TABLE predictions ADD COLUMN home_team TEXT",
        "ALTER TABLE predictions ADD COLUMN away_team TEXT",
        "ALTER TABLE predictions ADD COLUMN market_data TEXT",
        "ALTER TABLE matches ADD COLUMN markets_data TEXT DEFAULT '[]'",
    ]
    for m in migs:
        try:
            conn.execute(m)
        except:
            pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized at", DB_PATH)
