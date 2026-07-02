import os
os.environ['FOOTBALL_DATA_API_KEY'] = '902947a711c14897a9791bbf544299d9'
from scraper.football_data import FootballDataClient

c = FootballDataClient()

matches = c.get_matches(2021)
print(f'Got {len(matches)} PL matches')
if matches:
    for i, m in enumerate(matches[:5]):
        home = m['homeTeam']['name']
        away = m['awayTeam']['name']
        status = m['status']
        date = m['utcDate']
        print(f'  {i+1}. {home} vs {away} - {status} - {date[:10]}')

standings = c.get_standings(2021)
print(f'\nGot {len(standings)} teams in standings')
if standings:
    for s in standings[:5]:
        print(f'  {s["position"]}. {s["name"]} - {s["points"]}pts')

if standings:
    team = standings[0]
    form = c.get_team_form(team['team_id'])
    print(f'\n{team["name"]} form: {form}')
