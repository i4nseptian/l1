# Football Prediction App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web app that scrapes 1xBet odds & football-data.org stats, runs rule-based predictions, and lets users add custom betting logic.

**Architecture:** FastAPI backend serves REST API; React (Vite) frontend with Tailwind CSS. SQLite for history and user logic. Prediction engine combines form, H2H, odds movement, and bet factors.

**Tech Stack:** Python FastAPI, SQLite, React 18, Vite, Tailwind CSS, Football-Data.org API, 1xBet scrapers (existing)

## Global Constraints

- All Python dependencies in `backend/requirements.txt`
- React app bootstrapped with Vite, not CRA
- Use `pip` for Python packages, `npm` for frontend
- SQLite only — no PostgreSQL / MySQL

---

### Task 1: Project Scaffold — React + FastAPI

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `frontend/` (via Vite)

**Interfaces:**
- Produces: FastAPI app at `localhost:8000`, React dev server at `localhost:5173`
- Produces: `backend/requirements.txt` with fastapi, uvicorn, openpyxl, httpx, sqlite3

- [ ] **Step 1: Create backend directory & install deps**

```bash
mkdir -p D:\scraping\backend\data
cd D:\scraping\backend
```

Write `requirements.txt`:
```
fastapi==0.115.0
uvicorn==0.30.0
openpyxl==3.1.5
httpx==0.27.0
python-dotenv==1.0.1
```

Run:
```bash
cd D:\scraping\backend
pip install -r requirements.txt
```

- [ ] **Step 2: Create FastAPI entry point**

Write `backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Football Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 3: Create React frontend with Vite**

```bash
cd D:\scraping
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
```

Configure Vite for Tailwind — write `frontend/vite.config.js`:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

Replace `frontend/src/index.css`:
```css
@import "tailwindcss";
```

- [ ] **Step 4: Verify both servers start**

Terminal 1:
```bash
cd D:\scraping\backend
uvicorn main:app --reload
```
Expected: `Uvicorn running on http://127.0.0.1:8000`

Terminal 2:
```bash
cd D:\scraping\frontend
npm run dev
```
Expected: `VITE v6.x  ready at http://localhost:5173`

---

### Task 2: Parse Excel Data → Structured JSON

**Files:**
- Create: `backend/parse_factors.py`
- Produce: `backend/data/factors.json`

**Interfaces:**
- Produces: `backend/data/factors.json` — parsed, structured bet factors

- [ ] **Step 1: Write parser script**

Write `backend/parse_factors.py`:
```python
import openpyxl
import json
import re
import os

def parse_excel_to_json(excel_path, output_path):
    wb = openpyxl.load_workbook(excel_path)
    ws = wb['Sheet1']
    
    all_lines = []
    for i in range(1, ws.max_row + 1):
        v = ws.cell(row=i, column=1).value
        if v is not None:
            all_lines.append(str(v))
    
    text = '\n'.join(all_lines)
    
    # Convert to valid JSON
    # 1. Quote all keys (word: before comma/newline/colon)
    text = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', text)
    # 2. Quote string values
    text = re.sub(r':\s*"([^"]*)"', r': "\1"', text)
    # 3. Fix true/false
    text = text.replace(': true', ': true').replace(': false', ': false')
    # 4. Remove trailing commas before ] or }
    text = re.sub(r',\s*([\]}])', r'\1', text)
    
    data = json.loads(text)
    
    # Extract SG (Sports Groups) into flat list
    sg_list = data.get('Value', {}).get('SG', [])
    
    # Extract unique tournament groups
    tgs = set()
    markets_summary = []
    for item in sg_list:
        tg = item.get('TG', '') or item.get('PN', '') or 'Unknown'
        tgs.add(tg)
        for mec in item.get('MEC', []):
            markets_summary.append({
                'sport_id': item.get('N'),
                'period': item.get('P'),
                'period_name': item.get('PN', ''),
                'group': tg,
                'market_type': mec.get('MT'),
                'market_name': mec.get('N', ''),
                'event_count': mec.get('EC', 0)
            })
    
    result = {
        'total_sports': len(sg_list),
        'total_markets': len(markets_summary),
        'tournament_groups': sorted(tgs),
        'markets': markets_summary
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Parsed {len(sg_list)} sports, {len(markets_summary)} markets")
    print(f"Tournament groups: {sorted(tgs)}")
    return result

if __name__ == '__main__':
    excel_path = r'D:\data scraping ian.xlsx'
    output_path = r'D:\scraping\backend\data\factors.json'
    parse_excel_to_json(excel_path, output_path)
```

- [ ] **Step 2: Run parser**

```bash
cd D:\scraping\backend
python parse_factors.py
```

Expected output:
```
Parsed X sports, Y markets
Tournament groups: [...list...]
```

- [ ] **Step 3: Verify output exists**

```bash
python -c "import json; d=json.load(open('data/factors.json')); print(f'Keys: {list(d.keys())}')"
```

Expected: `Keys: ['total_sports', 'total_markets', 'tournament_groups', 'markets']`

---

### Task 3: Database Setup (SQLite)

**Files:**
- Create: `backend/database.py`

**Interfaces:**
- Produces: `init_db()` — creates tables
- Produces: `get_db()` — returns connection

- [ ] **Step 1: Write database module**

Write `backend/database.py`:
```python
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (league_id) REFERENCES leagues(id)
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            predicted_winner TEXT NOT NULL,
            confidence REAL NOT NULL,
            score_breakdown TEXT,
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized at", DB_PATH)
```

- [ ] **Step 2: Initialize database**

```bash
cd D:\scraping\backend
python database.py
```

Expected: `Database initialized at D:\scraping\backend\data\app.db`

- [ ] **Step 3: Verify tables**

```bash
python -c "import sqlite3; conn=sqlite3.connect('data/app.db'); tables=conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall(); print([t[0] for t in tables])"
```

Expected: `['leagues', 'matches', 'predictions', 'custom_logic', 'bet_factors', 'teams']`

---

### Task 4: Prediction Engine (Rule-Based)

**Files:**
- Create: `backend/prediction/__init__.py`
- Create: `backend/prediction/engine.py`

**Interfaces:**
- `predict(match_data: dict) -> dict` — returns `{winner: str, confidence: float, breakdown: dict}`

- [ ] **Step 1: Create prediction package**

```bash
mkdir D:\scraping\backend\prediction
```

Write `backend/prediction/__init__.py`:
```python
from .engine import predict, predict_with_custom_logic
```

- [ ] **Step 2: Write scoring engine**

Write `backend/prediction/engine.py`:
```python
DEFAULT_WEIGHTS = {
    'form': 0.25,
    'h2h': 0.15,
    'position': 0.10,
    'odds_movement': 0.15,
    'factors': 0.10,
    'draw_bias': 0.05,
}

def _score_form(form_str):
    """Convert form string like 'WWDLW' to score 0-100"""
    if not form_str:
        return 50
    scores = {'W': 100, 'D': 50, 'L': 0}
    vals = [scores.get(c, 50) for c in form_str.upper()[:5]]
    return sum(vals) / len(vals) if vals else 50

def _score_position(pos, total_teams=20):
    """Higher position = higher score"""
    if pos is None:
        return 50
    return max(0, 100 - ((pos - 1) / max(total_teams - 1, 1)) * 100)

def _score_h2h(h2h_records, team):
    """Score head-to-head for given team"""
    if not h2h_records:
        return 50
    total = 0
    for rec in h2h_records[-5:]:
        result = rec.get('result', '')
        if result == team:
            total += 100
        elif result == 'draw':
            total += 50
        else:
            total += 0
    return total / len(h2h_records) if h2h_records else 50

def _score_odds_movement(odds_current, odds_opening):
    """Score based on odds movement. Shortening odds = confidence"""
    if not odds_opening or not odds_current or odds_opening == 0:
        return 50
    change = ((odds_opening - odds_current) / odds_opening) * 100
    return min(100, max(0, 50 + change * 10))

def predict(match_data):
    """
    match_data: {
        'form_home': 'WWDLW',
        'form_away': 'LDDWL',
        'position_home': 3,
        'position_away': 15,
        'h2h': [{'result': 'home'}, {'result': 'home'}, ...],
        'odds_home': 1.85,
        'odds_draw': 3.40,
        'odds_away': 4.50,
        'odds_opening_home': 2.00,
        'odds_opening_draw': 3.30,
        'odds_opening_away': 4.00,
        'total_teams': 20,
    }
    """
    w = DEFAULT_WEIGHTS
    
    form_h = _score_form(match_data.get('form_home', ''))
    form_a = _score_form(match_data.get('form_away', ''))
    pos_h = _score_position(match_data.get('position_home'), match_data.get('total_teams', 20))
    pos_a = _score_position(match_data.get('position_away'), match_data.get('total_teams', 20))
    h2h_h = _score_h2h(match_data.get('h2h', []), 'home')
    h2h_a = _score_h2h(match_data.get('h2h', []), 'away')
    odds_mov_h = _score_odds_movement(match_data.get('odds_home'), match_data.get('odds_opening_home'))
    odds_mov_a = _score_odds_movement(match_data.get('odds_away'), match_data.get('odds_opening_away'))
    
    # Odds implied probability
    odds_h = match_data.get('odds_home', 2.0)
    odds_d = match_data.get('odds_draw', 3.0)
    odds_a = match_data.get('odds_away', 3.0)
    imp_h = (1 / odds_h) * 100
    imp_d = (1 / odds_d) * 100
    imp_a = (1 / odds_a) * 100
    total_imp = imp_h + imp_d + imp_a
    imp_h = (imp_h / total_imp) * 100
    imp_a = (imp_a / total_imp) * 100
    
    home_score = (
        w['form'] * form_h +
        w['h2h'] * h2h_h +
        w['position'] * pos_h +
        w['odds_movement'] * odds_mov_h +
        w['factors'] * imp_h
    )
    
    away_score = (
        w['form'] * form_a +
        w['h2h'] * h2h_a +
        w['position'] * pos_a +
        w['odds_movement'] * odds_mov_a +
        w['factors'] * imp_a
    )
    
    draw_score = (form_h + form_a) / 2 * w['draw_bias'] + imp_d * w['factors']
    
    scores = {
        'home': round(home_score, 1),
        'draw': round(draw_score, 1),
        'away': round(away_score, 1),
    }
    
    winner = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = round((scores[winner] / total) * 100, 1)
    
    return {
        'winner': winner,
        'confidence': confidence,
        'scores': scores,
        'breakdown': {
            'form_home': round(form_h, 1),
            'form_away': round(form_a, 1),
            'position_home': round(pos_h, 1),
            'position_away': round(pos_a, 1),
            'h2h_home': round(h2h_h, 1),
            'h2h_away': round(h2h_a, 1),
            'odds_movement_home': round(odds_mov_h, 1),
            'odds_movement_away': round(odds_mov_a, 1),
        }
    }

def predict_with_custom_logic(match_data, custom_rules):
    result = predict(match_data)
    for rule in custom_rules:
        if not rule.get('is_active', True):
            continue
        field = rule['condition_field']
        op = rule['operator']
        val = rule['condition_value']
        actual = match_data.get(field)
        if actual is None:
            continue
        match_found = False
        if op == '<':
            match_found = actual < val
        elif op == '>':
            match_found = actual > val
        elif op == '=':
            match_found = actual == val
        elif op == '>=':
            match_found = actual >= val
        elif op == '<=':
            match_found = actual <= val
        if match_found:
            result['scores'][rule['result_recommendation']] += rule['weight_modifier']
            result['scores'][rule['result_recommendation']] = max(0, result['scores'][rule['result_recommendation']])
    
    # Recalculate winner after custom logic
    winner = max(result['scores'], key=result['scores'].get)
    total = sum(result['scores'].values()) or 1
    result['winner'] = winner
    result['confidence'] = round((result['scores'][winner] / total) * 100, 1)
    return result
```

---

### Task 5: FastAPI — Load Factors & Match Endpoints

**Files:**
- Modify: `backend/main.py`
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/matches.py`
- Create: `backend/routers/factors.py`
- Create: `backend/routers/custom_logic.py`

**Interfaces:**
- `GET /api/factors` — returns parsed bet factors
- `GET /api/leagues` — returns league list
- `GET /api/matches?league=X` — returns matches + predictions
- `GET /api/matches/:id` — match detail
- `GET /api/matches/:id/prediction` — run prediction
- `POST /api/custom-logic` — save rule
- `GET /api/custom-logic` — get user rules

- [ ] **Step 1: Create routers directory**

```bash
mkdir D:\scraping\backend\routers
```

Write `backend/routers/__init__.py`:
```python
from .matches import router as matches_router
from .factors import router as factors_router
from .custom_logic import router as logic_router
```

- [ ] **Step 2: Write factors router**

Write `backend/routers/factors.py`:
```python
from fastapi import APIRouter
import json
import os

router = APIRouter(prefix='/api')

FACTORS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'factors.json')

@router.get('/factors')
async def get_factors():
    if not os.path.exists(FACTORS_PATH):
        return {'error': 'Factors not parsed yet'}
    with open(FACTORS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@router.get('/leagues')
async def get_leagues():
    return {
        'leagues': [
            {'id': 1, 'name': 'English Premier League', 'country': 'England'},
            {'id': 2, 'name': 'La Liga', 'country': 'Spain'},
            {'id': 3, 'name': 'Serie A', 'country': 'Italy'},
            {'id': 4, 'name': 'Bundesliga', 'country': 'Germany'},
            {'id': 5, 'name': 'Ligue 1', 'country': 'France'},
            {'id': 6, 'name': 'World Cup', 'country': 'International'},
        ]
    }
```

- [ ] **Step 3: Write matches router**

Write `backend/routers/matches.py`:
```python
from fastapi import APIRouter, HTTPException
from prediction import predict, predict_with_custom_logic
from database import get_db
import json

router = APIRouter(prefix='/api')

@router.get('/matches')
async def get_matches(league: str = None, date: str = None):
    conn = get_db()
    cur = conn.cursor()
    query = "SELECT * FROM matches WHERE 1=1"
    params = []
    if league:
        query += " AND league_id = (SELECT id FROM leagues WHERE name = ?)"
        params.append(league)
    if date:
        query += " AND date(match_time) = ?"
        params.append(date)
    query += " ORDER BY match_time ASC LIMIT 50"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return {'matches': [dict(r) for r in rows]}

@router.get('/matches/{match_id}')
async def get_match(match_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, 'Match not found')
    return dict(row)

@router.get('/matches/{match_id}/prediction')
async def get_prediction(match_id: int):
    conn = get_db()
    match = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    if not match:
        conn.close()
        raise HTTPException(404, 'Match not found')
    
    # Get team data
    home_team = conn.execute("SELECT * FROM teams WHERE name = ?", (match['home_team'],)).fetchone()
    away_team = conn.execute("SELECT * FROM teams WHERE name = ?", (match['away_team'],)).fetchone()
    
    # Get custom rules
    rules = conn.execute("SELECT * FROM custom_logic WHERE is_active = 1 ORDER BY priority").fetchall()
    conn.close()
    
    match_data = {
        'form_home': home_team['form'] if home_team else '',
        'form_away': away_team['form'] if away_team else '',
        'position_home': home_team['position'] if home_team else None,
        'position_away': away_team['position'] if away_team else None,
        'h2h': [],
        'odds_home': match['odds_home'],
        'odds_draw': match['odds_draw'],
        'odds_away': match['odds_away'],
        'total_teams': 20,
    }
    
    if rules:
        result = predict_with_custom_logic(match_data, [dict(r) for r in rules])
    else:
        result = predict(match_data)
    
    return result
```

- [ ] **Step 4: Write custom logic router**

Write `backend/routers/custom_logic.py`:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter(prefix='/api/custom-logic')

class LogicRule(BaseModel):
    condition_field: str
    operator: str
    condition_value: float
    logic_connector: str = 'AND'
    result_recommendation: str
    weight_modifier: float = 0
    priority: int = 0

@router.get('/')
async def get_rules():
    conn = get_db()
    rows = conn.execute("SELECT * FROM custom_logic WHERE is_active = 1 ORDER BY priority").fetchall()
    conn.close()
    return {'rules': [dict(r) for r in rows]}

@router.post('/')
async def create_rule(rule: LogicRule):
    conn = get_db()
    conn.execute(
        """INSERT INTO custom_logic 
        (condition_field, operator, condition_value, logic_connector, result_recommendation, weight_modifier, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (rule.condition_field, rule.operator, rule.condition_value, rule.logic_connector, rule.result_recommendation, rule.weight_modifier, rule.priority)
    )
    conn.commit()
    rule_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return {'id': rule_id, 'message': 'Rule created'}

@router.delete('/{rule_id}')
async def delete_rule(rule_id: int):
    conn = get_db()
    conn.execute("DELETE FROM custom_logic WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return {'message': 'Rule deleted'}
```

- [ ] **Step 5: Wire routers into main.py**

Modify `backend/main.py` to read:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import matches_router, factors_router, logic_router
from parse_factors import parse_excel_to_json
import os

app = FastAPI(title="Football Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches_router)
app.include_router(factors_router)
app.include_router(logic_router)

@app.on_event("startup")
async def startup():
    init_db()
    factors_path = os.path.join(os.path.dirname(__file__), 'data', 'factors.json')
    if not os.path.exists(factors_path):
        excel_path = r'D:\data scraping ian.xlsx'
        if os.path.exists(excel_path):
            parse_excel_to_json(excel_path, factors_path)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Verify server starts**

```bash
cd D:\scraping\backend
uvicorn main:app --reload
```

Open browser: `http://localhost:8000/api/health` → `{"status":"ok"}`
Open: `http://localhost:8000/api/factors` → parsed factors JSON
Open: `http://localhost:8000/api/leagues` → league list

---

### Task 6: Football-Data.org Client

**Files:**
- Create: `backend/scraper/__init__.py`
- Create: `backend/scraper/football_data.py`

- [ ] **Step 1: Create scraper package**

```bash
mkdir D:\scraping\backend\scraper
```

Write `backend/scraper/__init__.py`:
```python
from .football_data import FootballDataClient
```

- [ ] **Step 2: Write Football-Data.org client**

Write `backend/scraper/football_data.py`:
```python
import httpx
import os
from datetime import datetime, timedelta
from database import get_db

BASE_URL = "https://api.football-data.org/v4"

class FootballDataClient:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY', '')
        self.client = httpx.Client(
            base_url=BASE_URL,
            headers={'X-Auth-Token': self.api_key},
            timeout=15
        )
    
    def get_team_form(self, team_id):
        """Get last 5 matches for a team"""
        try:
            resp = self.client.get(f'/teams/{team_id}/matches', params={
                'status': 'FINISHED',
                'limit': 5
            })
            resp.raise_for_status()
            data = resp.json()
            matches = data.get('matches', [])[:5]
            form = ''
            for m in matches:
                winner = m.get('score', {}).get('winner')
                if winner == 'HOME_TEAM':
                    form += 'W' if m['homeTeam']['id'] == team_id else 'L'
                elif winner == 'AWAY_TEAM':
                    form += 'W' if m['awayTeam']['id'] == team_id else 'L'
                else:
                    form += 'D'
            return form
        except Exception as e:
            print(f"Error fetching team form: {e}")
            return ''
    
    def get_standings(self, competition_id):
        """Get league standings"""
        try:
            resp = self.client.get(f'/competitions/{competition_id}/standings')
            resp.raise_for_status()
            data = resp.json()
            standings = []
            for entry in data.get('standings', [{}])[0].get('table', []):
                team = entry['team']
                standings.append({
                    'team_id': team['id'],
                    'name': team['name'],
                    'position': entry['position'],
                    'played': entry['playedGames'],
                    'won': entry['won'],
                    'drawn': entry['draw'],
                    'lost': entry['lost'],
                    'points': entry['points'],
                })
            return standings
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []
    
    def get_matches(self, competition_id, date_from=None, date_to=None):
        """Get matches for a competition within date range"""
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'dateFrom': date_from or today}
        if date_to:
            params['dateTo'] = date_to
        else:
            params['dateTo'] = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        try:
            resp = self.client.get(f'/competitions/{competition_id}/matches', params=params)
            resp.raise_for_status()
            return resp.json().get('matches', [])
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return []
    
    def sync_teams_to_db(self, competition_id, competition_name):
        """Sync standings to database"""
        standings = self.get_standings(competition_id)
        conn = get_db()
        # Ensure league exists
        conn.execute(
            "INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)",
            (competition_name, '')
        )
        league = conn.execute("SELECT id FROM leagues WHERE name = ?", (competition_name,)).fetchone()
        league_id = league['id']
        
        for s in standings:
            conn.execute(
                """INSERT OR REPLACE INTO teams 
                (external_id, name, league_id, form, position, points, played, won, drawn, lost, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (s['team_id'], s['name'], league_id, '', s['position'], s['points'],
                 s['played'], s['won'], s['drawn'], s['lost'], datetime.now())
            )
            # Update form
            form = self.get_team_form(s['team_id'])
            conn.execute("UPDATE teams SET form = ? WHERE external_id = ?", (form, s['team_id']))
        
        conn.commit()
        conn.close()
        print(f"Synced {len(standings)} teams for {competition_name}")
```

---

### Task 7: 1xBet Scraper Integration

**Files:**
- Create: `backend/scraper/onexbet.py`

- [ ] **Step 1: Write 1xBet scraper module**

Write `backend/scraper/onexbet.py`:
```python
"""
Simple 1xBet scraper using HTTP requests to fetch current matches.
Falls back to existing Selenium scrapers if needed.
"""
import httpx
import json
import re
from datetime import datetime
from database import get_db

BASE_URL = "https://1xbet.com"

# Common league IDs mapping (approximate — needs updating)
LEAGUES = {
    'English Premier League': 1,
    'La Liga': 2,
    'Serie A': 3,
    'Bundesliga': 4,
    'Ligue 1': 5,
}

class OnexbetScraper:
    def __init__(self):
        self.client = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            },
            timeout=15,
            follow_redirects=True
        )
    
    def fetch_live_matches(self):
        """Fetch currently available matches from 1xBet API"""
        try:
            # Try LineFeed API endpoint
            resp = self.client.get(f'{BASE_URL}/LineFeed/GetSportsShortZip')
            if resp.status_code == 200:
                data = self._parse_response(resp.text)
                if data:
                    return self._extract_matches(data)
            
            # Fallback: try different endpoint
            resp = self.client.get(f'{BASE_URL}/LineFeed/GetChampionshipsZip', params={
                'sports': 1,  # football
                'lng': 'en',
                'tf': '2200000',
            })
            if resp.status_code == 200:
                data = self._parse_response(resp.text)
                if data:
                    return self._extract_matches(data)
        except Exception as e:
            print(f"1xBet scrape error: {e}")
        
        return []
    
    def _parse_response(self, text):
        """Parse the ZLib-compressed or JSON response"""
        try:
            return json.loads(text)
        except:
            pass
        try:
            import zlib
            decompressed = zlib.decompress(text.encode('latin1'), -zlib.MAX_WBITS)
            return json.loads(decompressed)
        except:
            pass
        return None
    
    def _extract_matches(self, data):
        """Extract match info from API response"""
        matches = []
        sg = data.get('Value', {}).get('SG', [])
        for sport_group in sg:
            for match in sport_group.get('E', []):  # 'E' might be events
                matches.append({
                    'external_id': str(match.get('I', '')),
                    'home_team': match.get('O1', '') or match.get('H', ''),
                    'away_team': match.get('O2', '') or match.get('A', ''),
                    'home_score': match.get('S1'),
                    'away_score': match.get('S2'),
                    'odds_home': self._extract_odds(match, 1),
                    'odds_draw': self._extract_odds(match, 0),
                    'odds_away': self._extract_odds(match, 2),
                    'status': 'live' if match.get('S', 0) == 1 else 'scheduled',
                })
        return matches
    
    def _extract_odds(self, match, outcome):
        """Extract odds for a given outcome (0=draw, 1=home, 2=away)"""
        try:
            markets = match.get('G', [])
            if markets:
                for m in markets:
                    if m.get('T', 0) == 1:  # 1X2 market type
                        outcomes = m.get('E', [])
                        if len(outcomes) > outcome:
                            return float(outcomes[outcome].get('C', 0))
        except:
            pass
        return None
    
    def sync_to_db(self):
        """Fetch and save matches to database"""
        matches = self.fetch_live_matches()
        conn = get_db()
        conn.execute("DELETE FROM matches WHERE status = 'scheduled'")
        
        for m in matches[:50]:  # limit to 50
            conn.execute(
                """INSERT OR REPLACE INTO matches 
                (external_id, home_team, away_team, home_score, away_score, status, odds_home, odds_draw, odds_away, match_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (m['external_id'], m['home_team'], m['away_team'],
                 m['home_score'], m['away_score'], m['status'],
                 m['odds_home'], m['odds_draw'], m['odds_away'], datetime.now())
            )
        
        conn.commit()
        conn.close()
        print(f"Synced {len(matches)} matches from 1xBet")
```

---

### Task 8: Frontend — Dashboard Page

**Files:**
- Create: `frontend/src/pages/Dashboard.jsx`
- Create: `frontend/src/components/MatchCard.jsx`
- Create: `frontend/src/components/PredictionBadge.jsx`
- Modify: `frontend/src/App.jsx`
- Create: `frontend/src/api.js`

- [ ] **Step 1: Create API helper**

Write `frontend/src/api.js`:
```js
const BASE = '/api';

export async function getLeagues() {
  const res = await fetch(`${BASE}/leagues`);
  return res.json();
}

export async function getMatches(league = '', date = '') {
  const params = new URLSearchParams();
  if (league) params.set('league', league);
  if (date) params.set('date', date);
  const res = await fetch(`${BASE}/matches?${params}`);
  return res.json();
}

export async function getMatch(id) {
  const res = await fetch(`${BASE}/matches/${id}`);
  return res.json();
}

export async function getPrediction(id) {
  const res = await fetch(`${BASE}/matches/${id}/prediction`);
  return res.json();
}

export async function getFactors() {
  const res = await fetch(`${BASE}/factors`);
  return res.json();
}

export async function getCustomRules() {
  const res = await fetch(`${BASE}/custom-logic/`);
  return res.json();
}

export async function createCustomRule(rule) {
  const res = await fetch(`${BASE}/custom-logic/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rule),
  });
  return res.json();
}

export async function deleteCustomRule(id) {
  const res = await fetch(`${BASE}/custom-logic/${id}`, { method: 'DELETE' });
  return res.json();
}
```

- [ ] **Step 2: Create PredictionBadge component**

Write `frontend/src/components/PredictionBadge.jsx`:
```jsx
export default function PredictionBadge({ winner, confidence }) {
  if (!winner) return null;
  
  let color = 'bg-red-500';
  let label = 'No Clear Pick';
  
  if (confidence >= 80) {
    color = 'bg-green-600';
    label = winner === 'home' ? 'Home Win' : winner === 'away' ? 'Away Win' : 'Draw';
  } else if (confidence >= 60) {
    color = 'bg-yellow-500';
    label = winner === 'home' ? 'Lean Home' : winner === 'away' ? 'Lean Away' : 'Lean Draw';
  }
  
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold text-white ${color}`}>
      <span>{label}</span>
      <span className="opacity-80">{confidence}%</span>
    </span>
  );
}
```

- [ ] **Step 3: Create MatchCard component**

Write `frontend/src/components/MatchCard.jsx`:
```jsx
import PredictionBadge from './PredictionBadge';

export default function MatchCard({ match, prediction }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition cursor-pointer border border-gray-100">
      <div className="flex justify-between items-center mb-3">
        <span className="text-xs text-gray-500 font-medium">
          {match.match_time ? new Date(match.match_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Live'}
        </span>
        {match.status === 'live' && (
          <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-semibold animate-pulse">LIVE</span>
        )}
      </div>
      
      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center">
          <span className="font-semibold text-gray-800">{match.home_team}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="font-semibold text-gray-800">{match.away_team}</span>
        </div>
      </div>
      
      <div className="flex gap-2 text-center text-sm mb-3">
        <div className="flex-1 bg-gray-50 rounded-lg py-1 font-medium">{match.odds_home?.toFixed(2) || '-'}</div>
        <div className="flex-1 bg-gray-50 rounded-lg py-1 font-medium">{match.odds_draw?.toFixed(2) || '-'}</div>
        <div className="flex-1 bg-gray-50 rounded-lg py-1 font-medium">{match.odds_away?.toFixed(2) || '-'}</div>
      </div>
      
      {prediction && <PredictionBadge winner={prediction.winner} confidence={prediction.confidence} />}
    </div>
  );
}
```

- [ ] **Step 4: Create Dashboard page**

Write `frontend/src/pages/Dashboard.jsx`:
```jsx
import { useState, useEffect } from 'react';
import MatchCard from '../components/MatchCard';
import { getMatches, getLeagues, getPrediction } from '../api';

export default function Dashboard() {
  const [matches, setMatches] = useState([]);
  const [leagues, setLeagues] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState('');
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    getLeagues().then(d => setLeagues(d.leagues || []));
  }, []);
  
  useEffect(() => {
    setLoading(true);
    getMatches(selectedLeague).then(async (data) => {
      const matchList = data.matches || [];
      setMatches(matchList);
      
      const preds = {};
      for (const m of matchList) {
        try {
          const p = await getPrediction(m.id);
          preds[m.id] = p;
        } catch {}
      }
      setPredictions(preds);
      setLoading(false);
    });
  }, [selectedLeague]);
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Football Predictions</h1>
        <select
          className="border border-gray-300 rounded-lg px-4 py-2 text-sm bg-white"
          value={selectedLeague}
          onChange={e => setSelectedLeague(e.target.value)}
        >
          <option value="">All Leagues</option>
          {leagues.map(l => (
            <option key={l.id} value={l.name}>{l.name}</option>
          ))}
        </select>
      </div>
      
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading matches...</div>
      ) : matches.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No matches available</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {matches.map(m => (
            <a key={m.id} href={`/match/${m.id}`} className="block">
              <MatchCard match={m} prediction={predictions[m.id]} />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: Wire App.jsx with React Router**

```bash
cd D:\scraping\frontend
npm install react-router-dom
```

Write `frontend/src/App.jsx`:
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import MatchDetail from './pages/MatchDetail';
import History from './pages/History';
import Factors from './pages/Factors';
import Layout from './components/Layout';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/match/:id" element={<MatchDetail />} />
          <Route path="/history" element={<History />} />
          <Route path="/factors" element={<Factors />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

Write `frontend/src/components/Layout.jsx`:
```jsx
import { Outlet, Link, useLocation } from 'react-router-dom';

const nav = [
  { path: '/', label: 'Dashboard' },
  { path: '/history', label: 'History' },
  { path: '/factors', label: 'Factors' },
];

export default function Layout() {
  const location = useLocation();
  
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-green-700">PrediksiBola</Link>
          <div className="flex gap-1">
            {nav.map(item => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  location.pathname === item.path
                    ? 'bg-green-700 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
```

---

### Task 9: Frontend — Match Detail Page

**Files:**
- Create: `frontend/src/pages/MatchDetail.jsx`
- Create: `frontend/src/components/CustomLogicForm.jsx`
- Create: `frontend/src/components/OddsTable.jsx`
- Create: `frontend/src/components/FormChart.jsx`

- [ ] **Step 1: Create FormChart component**

Write `frontend/src/components/FormChart.jsx`:
```jsx
export default function FormChart({ form, team }) {
  if (!form) return <span className="text-gray-400">No data</span>;
  
  return (
    <div className="flex gap-1">
      {form.split('').map((r, i) => (
        <span
          key={i}
          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
            r === 'W' ? 'bg-green-500' : r === 'D' ? 'bg-yellow-500' : 'bg-red-500'
          }`}
        >
          {r}
        </span>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create CustomLogicForm**

Write `frontend/src/components/CustomLogicForm.jsx`:
```jsx
import { useState, useEffect } from 'react';
import { getCustomRules, createCustomRule, deleteCustomRule } from '../api';

const FIELDS = [
  { value: 'odds_home', label: 'Odds Home' },
  { value: 'odds_draw', label: 'Odds Draw' },
  { value: 'odds_away', label: 'Odds Away' },
  { value: 'form_home', label: 'Form Home (0-100)' },
  { value: 'form_away', label: 'Form Away (0-100)' },
  { value: 'position_home', label: 'Position Home' },
  { value: 'position_away', label: 'Position Away' },
];

const OPERATORS = [
  { value: '<', label: '<' },
  { value: '>', label: '>' },
  { value: '=', label: '=' },
  { value: '>=', label: '>=' },
  { value: '<=', label: '<=' },
];

const RECOMMENDATIONS = [
  { value: 'home', label: 'Home Win' },
  { value: 'draw', label: 'Draw' },
  { value: 'away', label: 'Away Win' },
];

export default function CustomLogicForm() {
  const [rules, setRules] = useState([]);
  const [field, setField] = useState('odds_home');
  const [op, setOp] = useState('<');
  const [val, setVal] = useState('2.0');
  const [rec, setRec] = useState('home');
  const [weight, setWeight] = useState('10');
  
  useEffect(() => {
    getCustomRules().then(d => setRules(d.rules || []));
  }, []);
  
  const handleAdd = async () => {
    await createCustomRule({
      condition_field: field,
      operator: op,
      condition_value: parseFloat(val),
      result_recommendation: rec,
      weight_modifier: parseFloat(weight),
    });
    const d = await getCustomRules();
    setRules(d.rules || []);
  };
  
  const handleDelete = async (id) => {
    await deleteCustomRule(id);
    setRules(rules.filter(r => r.id !== id));
  };
  
  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h3 className="font-bold text-lg mb-3">My Custom Logic</h3>
      
      <div className="grid grid-cols-5 gap-2 mb-3">
        <select className="border rounded px-2 py-1 text-sm" value={field} onChange={e => setField(e.target.value)}>
          {FIELDS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
        </select>
        <select className="border rounded px-2 py-1 text-sm" value={op} onChange={e => setOp(e.target.value)}>
          {OPERATORS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <input className="border rounded px-2 py-1 text-sm" value={val} onChange={e => setVal(e.target.value)} />
        <select className="border rounded px-2 py-1 text-sm" value={rec} onChange={e => setRec(e.target.value)}>
          {RECOMMENDATIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
        <input className="border rounded px-2 py-1 text-sm" value={weight} onChange={e => setWeight(e.target.value)} placeholder="Weight +-" />
      </div>
      
      <button onClick={handleAdd} className="bg-green-700 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-green-800">
        + Add Rule
      </button>
      
      {rules.length > 0 && (
        <ul className="mt-3 space-y-1">
          {rules.map(r => (
            <li key={r.id} className="flex justify-between items-center bg-gray-50 px-3 py-1.5 rounded text-sm">
              <span>
                IF <strong>{r.condition_field}</strong> {r.operator} {r.condition_value}
                → <strong className="text-green-700">{r.result_recommendation}</strong> ({r.weight_modifier > 0 ? '+' : ''}{r.weight_modifier}%)
              </span>
              <button onClick={() => handleDelete(r.id)} className="text-red-500 hover:text-red-700 text-xs">✕</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create MatchDetail page**

Write `frontend/src/pages/MatchDetail.jsx`:
```jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getMatch, getPrediction } from '../api';
import PredictionBadge from '../components/PredictionBadge';
import FormChart from '../components/FormChart';
import CustomLogicForm from '../components/CustomLogicForm';

export default function MatchDetail() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [tab, setTab] = useState('info');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setLoading(true);
    Promise.all([
      getMatch(id),
      getPrediction(id),
    ]).then(([m, p]) => {
      setMatch(m);
      setPrediction(p);
      setLoading(false);
    });
  }, [id]);
  
  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!match) return <div className="text-center py-12 text-gray-500">Match not found</div>;
  
  const tabs = [
    { key: 'info', label: 'Info Tim' },
    { key: 'factors', label: 'Faktor Bet' },
    { key: 'prediction', label: 'Prediksi' },
    { key: 'logic', label: 'Logika Saya' },
  ];
  
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-4">
        <div className="flex justify-between items-center mb-4">
          <div className="text-center flex-1">
            <div className="text-lg font-bold text-gray-900 mb-1">{match.home_team}</div>
            <div className="text-sm text-gray-500">Home</div>
          </div>
          <div className="text-center px-6">
            <div className="text-3xl font-extrabold text-gray-900">
              {match.home_score !== null ? `${match.home_score} - ${match.away_score}` : 'VS'}
            </div>
            {match.status === 'live' && (
              <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-semibold">LIVE</span>
            )}
          </div>
          <div className="text-center flex-1">
            <div className="text-lg font-bold text-gray-900 mb-1">{match.away_team}</div>
            <div className="text-sm text-gray-500">Away</div>
          </div>
        </div>
        
        {prediction && (
          <div className="flex justify-center">
            <PredictionBadge winner={prediction.winner} confidence={prediction.confidence} />
          </div>
        )}
      </div>
      
      {/* Tabs */}
      <div className="flex gap-1 mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              tab === t.key ? 'bg-green-700 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      
      {/* Tab Content */}
      <div className="bg-white rounded-xl shadow-md p-6">
        {tab === 'info' && (
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Form 5 Laga Terakhir</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{match.home_team}</p>
                  <FormChart form={match.form_home} team={match.home_team} />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{match.away_team}</p>
                  <FormChart form={match.form_away} team={match.away_team} />
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Odds 1X2</h3>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1">1 (Home)</div>
                  <div className="text-xl font-bold text-gray-900">{match.odds_home?.toFixed(2) || '-'}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1">X (Draw)</div>
                  <div className="text-xl font-bold text-gray-900">{match.odds_draw?.toFixed(2) || '-'}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1">2 (Away)</div>
                  <div className="text-xl font-bold text-gray-900">{match.odds_away?.toFixed(2) || '-'}</div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {tab === 'factors' && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Available Bet Factors (from 1xBet)</h3>
            <p className="text-sm text-gray-500 mb-4">Data faktor dari file Excel yang sudah diparse — menampilkan semua jenis pasar yang tersedia.</p>
            <FactorsList />
          </div>
        )}
        
        {tab === 'prediction' && prediction && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Prediction Breakdown</h3>
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-green-50 rounded-lg p-3 text-center border border-green-200">
                  <div className="text-xs text-gray-500">Home</div>
                  <div className="text-xl font-bold text-gray-900">{prediction.scores?.home?.toFixed(1)}</div>
                </div>
                <div className="bg-yellow-50 rounded-lg p-3 text-center border border-yellow-200">
                  <div className="text-xs text-gray-500">Draw</div>
                  <div className="text-xl font-bold text-gray-900">{prediction.scores?.draw?.toFixed(1)}</div>
                </div>
                <div className="bg-red-50 rounded-lg p-3 text-center border border-red-200">
                  <div className="text-xs text-gray-500">Away</div>
                  <div className="text-xl font-bold text-gray-900">{prediction.scores?.away?.toFixed(1)}</div>
                </div>
              </div>
              
              {prediction.breakdown && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Score Breakdown</h4>
                  {Object.entries(prediction.breakdown).map(([key, val]) => (
                    <div key={key} className="flex justify-between py-1 text-sm">
                      <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="font-medium">{val.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        
        {tab === 'logic' && <CustomLogicForm />}
      </div>
    </div>
  );
}

function FactorsList() {
  const [factors, setFactors] = useState([]);
  
  useEffect(() => {
    import('../api').then(m => m.getFactors()).then(d => {
      setFactors(d.markets || []);
    });
  }, []);
  
  const groups = {};
  for (const f of factors) {
    const g = f.group || 'Unknown';
    if (!groups[g]) groups[g] = new Set();
    groups[g].add(f.market_name);
  }
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {Object.entries(groups).sort().map(([group, markets]) => (
        <div key={group} className="bg-gray-50 rounded-lg p-3">
          <h4 className="font-semibold text-sm text-gray-900 mb-1">{group}</h4>
          <p className="text-xs text-gray-500">{[...markets].sort().join(', ')}</p>
        </div>
      ))}
    </div>
  );
}
```

---

### Task 10: Frontend — History & Factors Pages

**Files:**
- Create: `frontend/src/pages/History.jsx`
- Create: `frontend/src/pages/Factors.jsx`

- [ ] **Step 1: Create History page**

Write `frontend/src/pages/History.jsx`:
```jsx
import { useState, useEffect } from 'react';

export default function History() {
  const [predictions, setPredictions] = useState([]);
  
  useEffect(() => {
    fetch('/api/history')
      .then(r => r.json())
      .then(d => setPredictions(d.predictions || []))
      .catch(() => setPredictions([]));
  }, []);
  
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Prediction History</h1>
      
      {predictions.length === 0 ? (
        <div className="bg-white rounded-xl shadow-md p-12 text-center text-gray-500">
          <p className="text-lg mb-2">No predictions yet</p>
          <p className="text-sm">Start making predictions from the Dashboard</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Date</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Match</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Prediction</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Confidence</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Result</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Accurate</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {predictions.map(p => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-600">{p.created_at?.slice(0, 10)}</td>
                  <td className="px-4 py-3 font-medium">{p.match || 'N/A'}</td>
                  <td className="px-4 py-3 capitalize">{p.predicted_winner}</td>
                  <td className="px-4 py-3">{p.confidence}%</td>
                  <td className="px-4 py-3">{p.actual_result || '-'}</td>
                  <td className="px-4 py-3">
                    {p.is_correct === true && <span className="text-green-600 font-bold">✓</span>}
                    {p.is_correct === false && <span className="text-red-600 font-bold">✗</span>}
                    {p.is_correct === null && <span className="text-gray-400">-</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create Factors page**

Write `frontend/src/pages/Factors.jsx`:
```jsx
import { useState, useEffect } from 'react';
import { getFactors } from '../api';

export default function FactorsPage() {
  const [factors, setFactors] = useState(null);
  const [filter, setFilter] = useState('');
  
  useEffect(() => {
    getFactors().then(d => setFactors(d));
  }, []);
  
  if (!factors) return <div className="text-center py-12 text-gray-500">Loading factors...</div>;
  
  const filtered = filter
    ? factors.markets.filter(m => m.group?.toLowerCase().includes(filter.toLowerCase()))
    : factors.markets;
  
  const groups = {};
  for (const m of filtered) {
    const g = m.group || 'Unknown';
    if (!groups[g]) groups[g] = [];
    groups[g].push(m);
  }
  
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Bet Factors</h1>
      <p className="text-gray-500 text-sm mb-4">
        {factors.total_markets} markets across {factors.total_sports} sports from 1xBet
      </p>
      
      <input
        className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-6 text-sm"
        placeholder="Filter by group name..."
        value={filter}
        onChange={e => setFilter(e.target.value)}
      />
      
      <div className="space-y-4">
        {Object.entries(groups).sort().map(([group, markets]) => (
          <div key={group} className="bg-white rounded-xl shadow-md p-4">
            <h3 className="font-bold text-gray-900 mb-2">{group}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {markets.map((m, i) => (
                <div key={i} className="bg-gray-50 rounded px-3 py-1.5 text-sm flex justify-between">
                  <span className="text-gray-700">{m.market_name}</span>
                  <span className="text-gray-400 text-xs mt-0.5">{m.event_count}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### Task 11: Final Integration & Seed Data

**Files:**
- Create: `backend/seed_data.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create seed data script**

Write `backend/seed_data.py`:
```python
"""Seed database with sample data for testing"""
from database import init_db, get_db
from datetime import datetime, timedelta

def seed():
    init_db()
    conn = get_db()
    
    # Seed leagues
    leagues = [
        ('English Premier League', 'England'),
        ('La Liga', 'Spain'),
        ('Serie A', 'Italy'),
    ]
    for name, country in leagues:
        conn.execute("INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)", (name, country))
    
    # Get league IDs
    epl = conn.execute("SELECT id FROM leagues WHERE name = 'English Premier League'").fetchone()[0]
    
    # Seed teams
    teams_data = [
        ('Manchester City', epl, 'WWWDW', 1, 82, 32, 25, 5, 2),
        ('Arsenal', epl, 'WWWWD', 2, 75, 32, 23, 6, 3),
        ('Liverpool', epl, 'WWWLW', 3, 71, 32, 21, 8, 3),
        ('Aston Villa', epl, 'WLWDW', 4, 66, 32, 20, 6, 6),
        ('Tottenham', epl, 'LWWDL', 5, 60, 32, 18, 6, 8),
        ('Manchester United', epl, 'WLLWW', 6, 55, 32, 16, 7, 9),
        ('Chelsea', epl, 'DWLDL', 7, 50, 32, 14, 8, 10),
        ('Newcastle', epl, 'WDLDL', 8, 48, 32, 14, 6, 12),
    ]
    for name, lid, form, pos, pts, p, w, d, l in teams_data:
        conn.execute(
            """INSERT OR REPLACE INTO teams (name, league_id, form, position, points, played, won, drawn, lost, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, lid, form, pos, pts, p, w, d, l, datetime.now())
        )
    
    # Seed sample matches
    now = datetime.now()
    for i, (home, away, oh, od, oa) in enumerate([
        ('Manchester City', 'Arsenal', 1.75, 3.60, 4.50),
        ('Liverpool', 'Tottenham', 1.50, 4.20, 6.00),
        ('Chelsea', 'Manchester United', 2.40, 3.30, 2.90),
        ('Newcastle', 'Aston Villa', 2.60, 3.40, 2.70),
    ]):
        conn.execute(
            """INSERT OR IGNORE INTO matches (external_id, league_id, home_team, away_team, status, odds_home, odds_draw, odds_away, match_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (f'sample_{i}', epl, home, away, 'scheduled', oh, od, oa, now + timedelta(hours=i+1))
        )
    
    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
```

- [ ] **Step 2: Run seed & verify**

```bash
cd D:\scraping\backend
python seed_data.py
```

Verify:
```bash
python -c "import sqlite3; conn=sqlite3.connect('data/app.db'); print('Matches:', len(conn.execute('SELECT * FROM matches').fetchall())); print('Teams:', len(conn.execute('SELECT * FROM teams').fetchall()))"
```

- [ ] **Step 3: Add history endpoint to main.py**

Add to `backend/main.py` imports:
```python
from database import get_db
```

Add endpoint before `@app.get("/api/health")`:
```python
@app.get("/api/history")
async def get_history():
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, m.home_team || ' vs ' || m.away_team as match
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        ORDER BY p.created_at DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return {'predictions': [dict(r) for r in rows]}
```

- [ ] **Step 4: Final test — start both servers**

Terminal 1:
```bash
cd D:\scraping\backend
uvicorn main:app --reload
```

Terminal 2:
```bash
cd D:\scraping\frontend
npm run dev
```

Open `http://localhost:5173` - should see dashboard with sample matches from seed data.

---

## Task Summary

| # | Task | Files |
|---|------|-------|
| 1 | Project Scaffold | `backend/main.py`, `frontend/` |
| 2 | Parse Excel → JSON | `backend/parse_factors.py` |
| 3 | Database Setup | `backend/database.py` |
| 4 | Prediction Engine | `backend/prediction/engine.py` |
| 5 | API Endpoints | `backend/routers/*.py`, `backend/main.py` |
| 6 | Football-Data.org | `backend/scraper/football_data.py` |
| 7 | 1xBet Scraper | `backend/scraper/onexbet.py` |
| 8 | Frontend Dashboard | `frontend/src/pages/Dashboard.jsx`, `MatchCard.jsx`, `PredictionBadge.jsx`, `Layout.jsx`, `App.jsx`, `api.js` |
| 9 | Frontend Match Detail | `frontend/src/pages/MatchDetail.jsx`, `CustomLogicForm.jsx`, `FormChart.jsx` |
| 10 | Frontend History & Factors | `frontend/src/pages/History.jsx`, `frontend/src/pages/Factors.jsx` |
| 11 | Final Integration & Seed | `backend/seed_data.py` |
