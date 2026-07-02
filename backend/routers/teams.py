"""Team sync & query endpoints — pulls teams from Football-Data.org and 1xBet."""

from fastapi import APIRouter, HTTPException
from database import get_db
import os
import httpx
import asyncio

router = APIRouter(prefix='/api')

FOOTBALL_DATA_BASE = 'https://api.football-data.org/v4'

def get_fd_headers():
    key = os.getenv('FOOTBALL_DATA_API_KEY', '')
    if not key:
        return None
    return {'X-Auth-Token': key}


@router.get('/teams')
async def get_teams(league: str = None, search: str = None):
    conn = get_db()
    query = "SELECT t.*, l.name as league_name, l.country FROM teams t LEFT JOIN leagues l ON t.league_id = l.id WHERE 1=1"
    params = []
    if league:
        query += " AND l.name = ?"
        params.append(league)
    if search:
        query += " AND t.name LIKE ?"
        params.append(f'%{search}%')
    query += " ORDER BY l.country, t.name LIMIT 2000"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return {'teams': [dict(r) for r in rows], 'total': len(rows)}


@router.get('/teams/leagues')
async def get_team_leagues():
    conn = get_db()
    rows = conn.execute("""
        SELECT l.id, l.name, l.country, COUNT(t.id) as team_count
        FROM leagues l
        LEFT JOIN teams t ON t.league_id = l.id
        GROUP BY l.id
        ORDER BY l.country, l.name
    """).fetchall()
    conn.close()
    return {'leagues': [dict(r) for r in rows]}


@router.post('/teams/sync')
async def sync_teams():
    """Sync teams from Football-Data.org for all accessible competitions."""
    headers = get_fd_headers()
    if not headers:
        raise HTTPException(400, 'FOOTBALL_DATA_API_KEY not configured')

    conn = get_db()
    synced = {'leagues': 0, 'teams': 0, 'errors': []}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Step 1: Get all competitions
            r = await client.get(f'{FOOTBALL_DATA_BASE}/competitions', headers=headers)
            if r.status_code != 200:
                raise HTTPException(502, f'API returned {r.status_code}')
            data = r.json()
            competitions = [c for c in data.get('competitions', [])
                           if c.get('plan') in ('TIER_ONE', 'TIER_TWO')]

            # Step 2: For each competition, get teams
            for comp in competitions:
                try:
                    cid = comp['id']
                    cname = comp['name']
                    area = comp.get('area', {}).get('name', '')

                    # Insert or get league
                    conn.execute(
                        "INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)",
                        (cname, area)
                    )
                    conn.commit()
                    league = conn.execute(
                        "SELECT id FROM leagues WHERE name = ?", (cname,)
                    ).fetchone()
                    if not league:
                        continue
                    lid = league['id']

                    # Fetch teams for this competition
                    tr = await client.get(
                        f'{FOOTBALL_DATA_BASE}/competitions/{cid}/teams',
                        headers=headers
                    )
                    if tr.status_code != 200:
                        synced['errors'].append(f'{cname}: HTTP {tr.status_code}')
                        continue

                    team_data = tr.json()
                    for team in team_data.get('teams', []):
                        tid = team.get('id')
                        tname = team.get('name', '')
                        if not tname:
                            continue
                        conn.execute(
                            """INSERT OR IGNORE INTO teams (external_id, name, league_id)
                               VALUES (?, ?, ?)""",
                            (str(tid), tname, lid)
                        )
                        synced['teams'] += 1

                    synced['leagues'] += 1

                except Exception as e:
                    synced['errors'].append(f'{comp.get("name", "?")}: {str(e)}')

            conn.commit()

    except httpx.HTTPError as e:
        conn.close()
        raise HTTPException(502, f'API connection error: {str(e)}')

    conn.close()
    synced['teams'] = len(conn.execute("SELECT id FROM teams").fetchall())
    return synced


@router.post('/teams/sync-from-scraper')
async def sync_from_scraper():
    """Extract team names from 1xBet scraper matches and store in DB."""
    from scraper.onexbet import OnexbetScraper

    scraper = OnexbetScraper()
    matches = scraper.fetch_live_matches()
    conn = get_db()

    # Create an "Other" league for teams without a league
    conn.execute("INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)",
                 ('1xBet Live Matches', 'Various'))
    conn.commit()
    league = conn.execute(
        "SELECT id FROM leagues WHERE name = '1xBet Live Matches'"
    ).fetchone()
    lid = league['id'] if league else None

    added = 0
    for m in matches:
        for team in [m.get('home_team'), m.get('away_team')]:
            if team:
                existing = conn.execute(
                    "SELECT id FROM teams WHERE name = ?", (team,)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO teams (name, league_id) VALUES (?, ?)",
                        (team, lid)
                    )
                    added += 1

    conn.commit()
    conn.close()
    return {'matches_parsed': len(matches), 'new_teams_added': added}
