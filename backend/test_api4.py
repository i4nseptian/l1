import os, httpx
os.environ['FOOTBALL_DATA_API_KEY'] = '902947a711c14897a9791bbf544299d9'
headers = {'X-Auth-Token': os.environ['FOOTBALL_DATA_API_KEY']}

# Get World Cup 2026 FINAL matches (recent)
url = 'https://api.football-data.org/v4/competitions/2000/matches?dateFrom=2026-06-28&dateTo=2026-07-01'
resp = httpx.get(url, headers=headers, timeout=10)
data = resp.json()
print(f'WC Final stage matches: {data.get("count", 0)}')
for m in data.get('matches', []):
    home = m['homeTeam']['name']
    away = m['awayTeam']['name']
    status = m['status']
    score_h = m['score']['fullTime']['home']
    score_a = m['score']['fullTime']['away']
    date = m['utcDate'][:10]
    winner = m['score']['winner']
    print(f'  {date}: {home} {score_h}-{score_a} {away} ({status}) Winner: {winner}')

# Get WC standings/groups
url2 = 'https://api.football-data.org/v4/competitions/2000/standings'
resp2 = httpx.get(url2, headers=headers, timeout=10)
if resp2.status_code == 200:
    data2 = resp2.json()
    print(f'\nWC Standings:')
    for s in data2.get('standings', []):
        print(f'  Group: {s.get("group", "N/A")} - {s.get("type", "")}')
        for entry in s.get('table', [])[:2]:
            print(f'    {entry["position"]}. {entry["team"]["name"]} - {entry["points"]}pts')
else:
    print(f'WC standings status: {resp2.status_code}')

# Check if any live matches exist globally
url3 = 'https://api.football-data.org/v4/matches'
resp3 = httpx.get(url3, headers={'X-Auth-Token': os.environ['FOOTBALL_DATA_API_KEY']}, timeout=10)
if resp3.status_code == 200:
    data3 = resp3.json()
    matches = data3.get('matches', [])
    print(f'\nTotal matches: {len(matches)}')
    for m in matches[:5]:
        print(f'  {m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]} - {m["status"]} - {m["utcDate"][:10]}')
