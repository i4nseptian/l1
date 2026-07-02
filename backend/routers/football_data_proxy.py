"""Proxy router untuk Football-Data.org API (real data)."""
from fastapi import APIRouter
import os
import httpx

router = APIRouter(prefix='/api/football-data')

BASE = 'https://api.football-data.org/v4'

def get_headers():
    key = os.getenv('FOOTBALL_DATA_API_KEY', '')
    if not key:
        return None
    return {'X-Auth-Token': key}

@router.get('/status')
async def api_status():
    headers = get_headers()
    if not headers:
        return {'connected': False, 'error': 'API key not configured', 'setup': 'Add FOOTBALL_DATA_API_KEY to .env'}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f'{BASE}/competitions/2000', headers=headers, timeout=10)
            return {'connected': r.status_code == 200, 'status': r.status_code}
    except Exception as e:
        return {'connected': False, 'error': str(e)}

@router.get('/matches')
async def get_matches(competition: int = None, date_from: str = None, date_to: str = None):
    headers = get_headers()
    if not headers:
        return {'error': 'API key not configured'}
    
    params = {}
    if competition:
        params['competitions'] = str(competition)
    if date_from:
        params['dateFrom'] = date_from
    if date_to:
        params['dateTo'] = date_to
    
    try:
        async with httpx.AsyncClient() as client:
            if competition:
                url = f'{BASE}/competitions/{competition}/matches'
            else:
                url = f'{BASE}/matches'
            r = await client.get(url, headers=headers, params=params, timeout=15)
            if r.status_code == 200:
                return r.json()
            return {'error': f'API returned {r.status_code}', 'detail': r.text[:200]}
    except Exception as e:
        return {'error': str(e)}

@router.get('/standings/{competition_id}')
async def get_standings(competition_id: int):
    headers = get_headers()
    if not headers:
        return {'error': 'API key not configured'}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f'{BASE}/competitions/{competition_id}/standings', headers=headers, timeout=15)
            if r.status_code == 200:
                return r.json()
            return {'error': f'API returned {r.status_code}'}
    except Exception as e:
        return {'error': str(e)}

@router.get('/competitions')
async def get_competitions():
    headers = get_headers()
    if not headers:
        return {'error': 'API key not configured'}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f'{BASE}/competitions', headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                return {
                    'competitions': [
                        {'id': c['id'], 'name': c['name'], 'area': c.get('area', {}).get('name', ''),
                         'emblem': c.get('emblem', ''), 'plan': c.get('plan', '')}
                        for c in data.get('competitions', [])
                        if c.get('plan') in ('TIER_ONE', 'TIER_TWO')
                    ]
                }
            return {'error': f'API returned {r.status_code}'}
    except Exception as e:
        return {'error': str(e)}

@router.get('/team/{team_id}')
async def get_team(team_id: int):
    headers = get_headers()
    if not headers:
        return {'error': 'API key not configured'}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f'{BASE}/teams/{team_id}', headers=headers, timeout=15)
            if r.status_code == 200:
                return r.json()
            return {'error': f'API returned {r.status_code}'}
    except Exception as e:
        return {'error': str(e)}
