import httpx
import os
import time
from datetime import datetime, timedelta
from database import get_db, init_db

BASE_URL = "https://api.football-data.org/v4"

COMPETITIONS = [
    (2000, 'FIFA World Cup', 'International'),
    (2001, 'UEFA Champions League', 'International'),
    (2002, 'Bundesliga', 'Germany'),
    (2003, 'Eredivisie', 'Netherlands'),
    (2013, 'Campeonato Brasileiro Serie A', 'Brazil'),
    (2014, 'La Liga', 'Spain'),
    (2015, 'Ligue 1', 'France'),
    (2016, 'EFL Championship', 'England'),
    (2017, 'Primeira Liga', 'Portugal'),
    (2019, 'Serie A', 'Italy'),
    (2021, 'English Premier League', 'England'),
    (2022, 'MLS', 'United States'),
    (2024, 'Copa America', 'International'),
    (2025, 'UEFA Europa League', 'International'),
]

class FootballDataClient:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY', '')
        self.client = httpx.Client(
            base_url=BASE_URL,
            headers={'X-Auth-Token': self.api_key},
            timeout=15
        )
        self._last_req = 0.0

    def _rate_limit(self):
        elapsed = time.time() - self._last_req
        if elapsed < 6.5:
            time.sleep(6.5 - elapsed)
        self._last_req = time.time()

    def _get(self, path, params=None):
        self._rate_limit()
        resp = self.client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_team_form(self, team_id):
        try:
            data = self._get(f'/teams/{team_id}/matches', params={'status': 'FINISHED', 'limit': 5})
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
            print(f"  [form error] {e}")
            return ''

    def get_standings(self, competition_id):
        try:
            data = self._get(f'/competitions/{competition_id}/standings')
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
            print(f"  [standings error] {e}")
            return []

    def get_matches(self, competition_id, date_from=None, date_to=None):
        params = {'dateFrom': date_from or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}
        params['dateTo'] = date_to or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        try:
            data = self._get(f'/competitions/{competition_id}/matches', params=params)
            return data.get('matches', [])
        except Exception as e:
            print(f"  [matches error] {e}")
            return []

    def sync_standings_to_db(self, competition_id, competition_name, country=''):
        standings = self.get_standings(competition_id)
        if not standings:
            print(f"  No standings data for {competition_name}")
            return 0

        conn = get_db()
        conn.execute("INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)", (competition_name, country))
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

        conn.commit()
        conn.close()
        print(f"  Synced {len(standings)} teams for {competition_name}")
        return len(standings)

    def sync_matches_to_db(self, competition_id, competition_name, country=''):
        matches = self.get_matches(competition_id)
        if not matches:
            print(f"  No match data for {competition_name}")
            return 0

        conn = get_db()
        conn.execute("INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)", (competition_name, country))
        league = conn.execute("SELECT id FROM leagues WHERE name = ?", (competition_name,)).fetchone()
        league_id = league['id']

        saved = 0
        for m in matches:
            external_id = str(m.get('id', ''))
            home = m.get('homeTeam', {}).get('name', '')
            away = m.get('awayTeam', {}).get('name', '')
            if not home or not away:
                continue

            score = m.get('score', {})
            full_time = score.get('fullTime', {}) or {}
            home_score = full_time.get('home')
            away_score = full_time.get('away')

            status = m.get('status', 'SCHEDULED')
            if status == 'FINISHED':
                db_status = 'completed'
            elif status in ('IN_PLAY', 'PAUSED'):
                db_status = 'live'
            elif status == 'POSTPONED':
                db_status = 'postponed'
            else:
                db_status = 'scheduled'

            match_time = m.get('utcDate', '').replace('Z', '') if m.get('utcDate') else None

            conn.execute(
                """INSERT OR REPLACE INTO matches
                (external_id, league_id, home_team, away_team, home_score, away_score, status, match_time, markets_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, '[]')""",
                (external_id, league_id, home, away, home_score, away_score, db_status, match_time)
            )
            saved += 1

        conn.commit()
        conn.close()
        print(f"  Saved {saved} matches for {competition_name}")
        return saved

    def sync_all(self):
        total_teams = 0
        total_matches = 0
        ok = 0
        fail = 0
        for cid, cname, country in COMPETITIONS:
            print(f"\n[{cname}] ({cid})...")
            try:
                t = self.sync_standings_to_db(cid, cname, country)
                total_teams += t
                if t:
                    ok += 1
                else:
                    fail += 1
            except Exception as e:
                print(f"  ERROR standings: {e}")
                fail += 1
            try:
                m = self.sync_matches_to_db(cid, cname, country)
                total_matches += m
            except Exception as e:
                print(f"  ERROR matches: {e}")

        print(f"\n{'='*50}")
        print(f"Done. {ok} competitions synced, {fail} skipped.")
        print(f"Total teams: {total_teams} | Total matches: {total_matches}")

    def close(self):
        self.client.close()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    init_db()
    client = FootballDataClient()
    client.sync_all()
    client.close()
