from fastapi import APIRouter

router = APIRouter(prefix='/api')

LEAGUES = [
    {'id': 1, 'name': 'English Premier League', 'country': 'England', 'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'code': 'ENG'},
    {'id': 2, 'name': 'La Liga', 'country': 'Spain', 'flag': '🇪🇸', 'code': 'ESP'},
    {'id': 3, 'name': 'Serie A', 'country': 'Italy', 'flag': '🇮🇹', 'code': 'ITA'},
    {'id': 4, 'name': 'Bundesliga', 'country': 'Germany', 'flag': '🇩🇪', 'code': 'GER'},
    {'id': 5, 'name': 'Ligue 1', 'country': 'France', 'flag': '🇫🇷', 'code': 'FRA'},
    {'id': 6, 'name': 'World Cup', 'country': 'International', 'flag': '🌍', 'code': 'INT'},
    {'id': 7, 'name': 'Eredivisie', 'country': 'Netherlands', 'flag': '🇳🇱', 'code': 'NED'},
    {'id': 8, 'name': 'Primeira Liga', 'country': 'Portugal', 'flag': '🇵🇹', 'code': 'POR'},
    {'id': 9, 'name': 'Serie B', 'country': 'Italy', 'flag': '🇮🇹', 'code': 'ITB'},
    {'id': 10, 'name': 'Championship', 'country': 'England', 'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'code': 'ECH'},
]

@router.get('/leagues')
async def get_leagues():
    return {'leagues': LEAGUES}

@router.get('/countries')
async def get_countries():
    countries = {}
    for l in LEAGUES:
        if l['country'] not in countries:
            countries[l['country']] = l['flag']
    return {'countries': countries}
