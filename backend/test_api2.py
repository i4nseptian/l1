import os, httpx
os.environ['FOOTBALL_DATA_API_KEY'] = '902947a711c14897a9791bbf544299d9'

# Direct test
url = 'https://api.football-data.org/v4/competitions/2021/standings'
headers = {'X-Auth-Token': os.environ['FOOTBALL_DATA_API_KEY']}
resp = httpx.get(url, headers=headers, timeout=15)
data = resp.json()
print('Standings type:', data.get('competition', {}).get('name'))
for standing in data.get('standings', []):
    print(f"Type: {standing.get('type')}, Table entries: {len(standing.get('table', []))}")
    for entry in standing.get('table', [])[:3]:
        print(f"  {entry['position']}. {entry['team']['name']} - {entry['points']}pts")

# Try getting matches with wider date range
url2 = 'https://api.football-data.org/v4/competitions/2021/matches?dateFrom=2025-01-01&dateTo=2026-12-31'
resp2 = httpx.get(url2, headers=headers, timeout=15)
print(f'\nMatches status: {resp2.status_code}')
if resp2.status_code == 200:
    data2 = resp2.json()
    print(f'Total matches: {data2.get("count", 0)}')
    for m in data2.get('matches', [])[:3]:
        print(f'  {m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]} - {m["status"]}')

# Try getting available competitions
url3 = 'https://api.football-data.org/v4/competitions'
resp3 = httpx.get(url3, headers=headers, timeout=15)
if resp3.status_code == 200:
    data3 = resp3.json()
    print(f'\nAvailable competitions:')
    for comp in data3.get('competitions', [])[:10]:
        print(f'  {comp["id"]}: {comp["name"]} ({comp.get("area", {}).get("name", "")}) - {comp.get("plan", "")}')
