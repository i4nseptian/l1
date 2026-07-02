from fastapi import APIRouter, HTTPException, Query
from prediction import predict, predict_with_custom_logic
from database import get_db
from data.markets import all_market_odds
import json

router = APIRouter(prefix='/api')

def _compute_prediction_for_match(match, conn):
    home_team = conn.execute("SELECT * FROM teams WHERE name = ?", (match['home_team'],)).fetchone()
    away_team = conn.execute("SELECT * FROM teams WHERE name = ?", (match['away_team'],)).fetchone()
    h2h_records = conn.execute(
        """SELECT home_team, away_team, home_score, away_score FROM matches
           WHERE (home_team = ? AND away_team = ?) OR (home_team = ? AND away_team = ?)
           ORDER BY match_time DESC LIMIT 5""",
        (match['home_team'], match['away_team'], match['away_team'], match['home_team'])
    ).fetchall()
    h2h = []
    for r in h2h_records:
        if r['home_score'] is not None and r['away_score'] is not None:
            if r['home_team'] == match['home_team']:
                result = 'home' if r['home_score'] > r['away_score'] else ('away' if r['away_score'] > r['home_score'] else 'draw')
            else:
                result = 'away' if r['home_score'] > r['away_score'] else ('home' if r['away_score'] > r['home_score'] else 'draw')
            h2h.append(result)
    odds_h = match.get('odds_home') or 2.0
    odds_d = match.get('odds_draw') or 3.0
    odds_a = match.get('odds_away') or 4.0
    match_data = {
        'form_home': home_team['form'] if home_team else '',
        'form_away': away_team['form'] if away_team else '',
        'position_home': home_team['position'] if home_team else None,
        'position_away': away_team['position'] if away_team else None,
        'h2h': [{'result': r} for r in h2h],
        'odds_home': odds_h,
        'odds_draw': odds_d,
        'odds_away': odds_a,
        'odds_opening_home': odds_h,
        'odds_opening_away': odds_a,
        'total_teams': 20,
    }
    rules = conn.execute("SELECT * FROM custom_logic WHERE is_active = 1 ORDER BY priority").fetchall()
    if rules:
        result = predict_with_custom_logic(match_data, [dict(r) for r in rules])
    else:
        result = predict(match_data)
    return {
        'winner': result['winner'],
        'confidence': result['confidence'],
        'scores': result['scores'],
    }

@router.get('/matches')
async def get_matches(league: str = None, date: str = None, predictions: bool = Query(False)):
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
    matches = []
    for r in rows:
        m = dict(r)
        if m.get('markets_data'):
            try:
                m['markets_data'] = json.loads(m['markets_data'])
            except:
                m['markets_data'] = []
        else:
            m['markets_data'] = []
        m['market_count'] = len(m['markets_data']) if isinstance(m['markets_data'], list) else 0
        if predictions and m['status'] not in ('live', 'in_play'):
            try:
                m['prediction'] = _compute_prediction_for_match(m, conn)
            except Exception as e:
                m['prediction'] = {'winner': 'draw', 'confidence': 33.3, 'error': str(e)}
        matches.append(m)
    conn.close()
    return {'matches': matches}

@router.get('/matches/{match_id}')
async def get_match(match_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, 'Match not found')
    result = dict(row)
    if result.get('markets_data'):
        try:
            result['markets_data'] = json.loads(result['markets_data'])
        except:
            pass
    return result

@router.get('/matches/{match_id}/prediction')
async def get_prediction(match_id: int):
    conn = get_db()
    match = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    if not match:
        conn.close()
        raise HTTPException(404, 'Match not found')

    home_team = conn.execute("SELECT * FROM teams WHERE name = ?", (match['home_team'],)).fetchone()
    away_team = conn.execute("SELECT * FROM teams WHERE name = ?", (match['away_team'],)).fetchone()

    rules = conn.execute("SELECT * FROM custom_logic WHERE is_active = 1 ORDER BY priority").fetchall()
    conn.close()

    # Build H2H from past matches between these teams
    h2h_records = conn.execute(
        """SELECT home_team, away_team, home_score, away_score FROM matches
           WHERE (home_team = ? AND away_team = ?) OR (home_team = ? AND away_team = ?)
           ORDER BY match_time DESC LIMIT 5""",
        (match['home_team'], match['away_team'], match['away_team'], match['home_team'])
    ).fetchall()
    h2h = []
    for r in h2h_records:
        if r['home_score'] is not None and r['away_score'] is not None:
            if r['home_team'] == match['home_team']:
                result = 'home' if r['home_score'] > r['away_score'] else ('away' if r['away_score'] > r['home_score'] else 'draw')
            else:
                result = 'away' if r['home_score'] > r['away_score'] else ('home' if r['away_score'] > r['home_score'] else 'draw')
            h2h.append({
                'home_team': r['home_team'],
                'away_team': r['away_team'],
                'home_score': r['home_score'],
                'away_score': r['away_score'],
                'result': result,
            })

    match_data = {
        'form_home': home_team['form'] if home_team else '',
        'form_away': away_team['form'] if away_team else '',
        'position_home': home_team['position'] if home_team else None,
        'position_away': away_team['position'] if away_team else None,
        'h2h': h2h,
        'odds_home': match['odds_home'],
        'odds_draw': match['odds_draw'],
        'odds_away': match['odds_away'],
        'odds_opening_home': match.get('odds_home'),
        'odds_opening_away': match.get('odds_away'),
        'total_teams': 20,
    }

    if rules:
        result = predict_with_custom_logic(match_data, [dict(r) for r in rules])
    else:
        result = predict(match_data)

    result['home_team'] = match['home_team']
    result['away_team'] = match['away_team']

    # Add all market odds
    # Prefer live scraped markets_data over calculated odds
    if match.get('markets_data'):
        try:
            live = json.loads(match['markets_data'])
            if live:
                result['all_markets'] = live
        except:
            pass
    if not result.get('all_markets'):
        result['all_markets'] = all_market_odds(match_data)

    result['h2h'] = h2h

    # Add team stats
    result['team_stats'] = {
        'home': {
            'name': match['home_team'],
            'form': home_team['form'] if home_team else '',
            'position': home_team['position'] if home_team else None,
            'points': home_team['points'] if home_team else 0,
            'played': home_team['played'] if home_team else 0,
            'won': home_team['won'] if home_team else 0,
            'drawn': home_team['drawn'] if home_team else 0,
            'lost': home_team['lost'] if home_team else 0,
        },
        'away': {
            'name': match['away_team'],
            'form': away_team['form'] if away_team else '',
            'position': away_team['position'] if away_team else None,
            'points': away_team['points'] if away_team else 0,
            'played': away_team['played'] if away_team else 0,
            'won': away_team['won'] if away_team else 0,
            'drawn': away_team['drawn'] if away_team else 0,
            'lost': away_team['lost'] if away_team else 0,
        },
    }

    return result


@router.get('/live-market-types')
async def get_live_market_types():
    conn = get_db()
    rows = conn.execute(
        "SELECT markets_data FROM matches WHERE markets_data IS NOT NULL AND markets_data != '[]'"
    ).fetchall()
    conn.close()

    type_counts = {}
    for r in rows:
        try:
            markets = json.loads(r['markets_data'])
            for m in markets:
                tid = m.get('type_id', 0)
                name = m.get('name', f'Unknown {tid}')
                type_counts[tid] = type_counts.get(tid, {'name': name, 'type_id': tid, 'count': 0})
                type_counts[tid]['count'] += 1
        except:
            pass

    return {
        'total_matches_with_markets': len([r for r in rows if r['markets_data'] and r['markets_data'] != '[]']),
        'market_types': sorted(type_counts.values(), key=lambda x: -x['count']),
    }
