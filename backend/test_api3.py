import os, httpx
from datetime import datetime

os.environ['FOOTBALL_DATA_API_KEY'] = '902947a711c14897a9791bbf544299d9'
headers = {'X-Auth-Token': os.environ['FOOTBALL_DATA_API_KEY']}

today = datetime.now().strftime('%Y-%m-%d')

# Check competitions with active matches
comp_ids = [2013, 2016, 2021, 2001, 2015, 2002, 2019, 2003, 2017, 2014, 2000, 2006, 2152, 2004, 2007, 2008, 2010, 2012, 2018, 2022, 2023, 2024, 2025]

for cid in comp_ids:
    try:
        url = f'https://api.football-data.org/v4/competitions/{cid}/matches?dateFrom={today}'
        resp = httpx.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            count = data.get('count', 0)
            if count > 0:
                name = data.get('competition', {}).get('name', 'Unknown')
                print(f'{cid}: {name} - {count} upcoming matches')
                for m in data['matches'][:2]:
                    print(f'  {m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]} ({m["status"]})')
        elif resp.status_code == 403:
            pass  # no access
    except:
        pass

print('\n--- Checking 2026 World Cup (WC 2026 might be active) ---')
# Try FIFA World Cup
try:
    url = 'https://api.football-data.org/v4/competitions/2000/matches'
    resp = httpx.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f'WC matches: {data.get("count", 0)}')
        for m in data.get('matches', [])[:5]:
            print(f'  {m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]} - {m["status"]} - {m["utcDate"][:10]}')
    else:
        print(f'WC status: {resp.status_code}')
except Exception as e:
    print(f'Error: {e}')
