"""
1xBet scraper — FULL market parsing from LineFeed API.
Extracts ALL market types from GE array, not just 1X2.
"""

import httpx
import json
import zlib
from datetime import datetime
from database import get_db

BASE_URL = "https://1xbet.com"

# Type ID → Market name mapping (comprehensive)
MARKET_TYPES = {
    1: 'Match Winner (1X2)',
    2: 'Double Chance',
    3: 'Both Teams to Score',
    4: 'Over/Under Total Goals',
    5: 'Asian Handicap',
    6: 'Correct Score',
    7: 'Total Goals (Odd/Even)',
    8: 'Exact Total Goals',
    9: 'Over/Under (Asian Total)',
    10: 'Individual Total Home',
    11: 'Individual Total Away',
    12: 'Home Team Exact Goals',
    13: 'Away Team Exact Goals',
    14: 'Correct Score (Home)',
    15: 'Home Team Total Odd/Even',
    16: 'Away Team Total Odd/Even',
    17: 'Home Team Over/Under',
    18: 'Away Team Over/Under',
    19: 'Both Teams to Score 1st Half',
    20: 'Draw No Bet',
    21: '1st Half Winner',
    22: '2nd Half Winner',
    23: 'Highest Scoring Half',
    24: 'Home to Win to Nil',
    25: 'Away to Win to Nil',
    26: 'Home Clean Sheet',
    27: 'Away Clean Sheet',
    28: 'Both Halves Over 1.5',
    29: '1st Half Both Teams to Score',
    30: '2nd Half Both Teams to Score',
    31: '1st Half Over/Under',
    32: '2nd Half Over/Under',
    33: 'Win Both Halves',
    34: '1st Half Exact Goals',
    35: '2nd Half Exact Goals',
    36: '1st Half Asian Handicap',
    37: '2nd Half Asian Handicap',
    38: '1st Half Double Chance',
    39: '2nd Half Double Chance',
    40: '1st Half Correct Score',
    41: '2nd Half Correct Score',
    42: '1st Half Total Odd/Even',
    43: 'HT/FT Double',
    44: 'Home Team to Score in Both Halves',
    45: 'Away Team to Score in Both Halves',
    46: '1st 10 Minutes Winner',
    47: 'Last 10 Minutes Winner',
    48: 'Time of First Goal',
    49: 'Time of First Home Goal',
    50: 'Time of First Away Goal',
    51: 'Goal in Both Halves',
    52: 'First Goal Method',
    53: 'Penalty Awarded',
    54: 'Own Goal',
    55: 'Red Card',
    56: 'Corner Kicks',
    57: 'Goal Kicks',
    58: 'Free Kicks',
    59: 'Throw-ins',
    60: 'Offsides',
    61: 'Yellow Cards',
    62: 'Cards Total',
    63: 'Substitutions',
    64: 'Shots on Target',
    65: 'Shots Off Target',
    66: 'Total Shots',
    67: 'Fouls',
    68: 'Corners 1st Half',
    69: 'Corners 2nd Half',
    70: 'Corners Asian Handicap',
    71: 'Corners Over/Under',
    72: 'Cards Over/Under',
    73: 'Goal Kicks Over/Under',
    74: 'Free Kicks Over/Under',
    75: 'Throw-ins Over/Under',
    76: 'Offsides Over/Under',
    77: 'Yellow Cards Over/Under',
    78: 'Substitutions Over/Under',
    79: 'Shots on Target Over/Under',
    80: 'Fouls Over/Under',
    81: '3-Way Handicap',
    82: 'Home Team Total Goals',
    83: 'Away Team Total Goals',
    84: 'Home Team Corners',
    85: 'Away Team Corners',
    86: 'Home Team Yellow Cards',
    87: 'Away Team Yellow Cards',
    88: 'Home Team Fouls',
    89: 'Away Team Fouls',
    90: 'Home Team Offsides',
    91: 'Away Team Offsides',
    92: 'Home Team Shots on Target',
    93: 'Away Team Shots on Target',
    94: 'Home Team Goal Kicks',
    95: 'Away Team Goal Kicks',
    96: 'Home Team Free Kicks',
    97: 'Away Team Free Kicks',
    98: 'Home Team Throw-ins',
    99: 'Away Team Throw-ins',
    100: 'Home Team Substitutions',
    101: 'Away Team Substitutions',
}

# Outcome type mappings for well-known market types
OUTCOME_LABELS = {
    1: {0: '1', 1: 'X', 2: '2'},           # 1X2
    2: {0: '1X', 1: '12', 2: 'X2'},        # Double Chance
    3: {0: 'Yes', 1: 'No'},                # BTTS
    6: {0: 'Score'},                        # Correct Score
    19: {0: 'Yes (1st Half)', 1: 'No (1st Half)'},  # BTTS 1st Half
    20: {0: 'Home (DNB)', 1: 'Away (DNB)'}, # Draw No Bet
    33: {0: 'Yes', 1: 'No'},                # Win Both Halves
    43: {0: 'Yes', 1: 'No'},                # Home Win to Nil
    44: {0: 'Yes', 1: 'No'},                # Away Win to Nil
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
        try:
            resp = self.client.get(f'{BASE_URL}/LineFeed/GetSportsShortZip')
            if resp.status_code == 200:
                data = self._parse_response(resp.text)
                if data:
                    return self._extract_matches(data)

            resp = self.client.get(f'{BASE_URL}/LineFeed/GetChampionshipsZip', params={
                'sports': 1,
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
        try:
            return json.loads(text)
        except:
            pass
        try:
            decompressed = zlib.decompress(text.encode('latin1'), -zlib.MAX_WBITS)
            return json.loads(decompressed)
        except:
            pass
        return None

    def _extract_matches(self, data):
        matches = []
        sg = data.get('Value', {}).get('SG', [])

        for sport_group in sg:
            for event in sport_group.get('E', []):
                markets = self._parse_all_markets(event)
                has_1x2 = any(m['type_id'] == 1 for m in markets)

                match = {
                    'external_id': str(event.get('I', '')),
                    'home_team': event.get('O1', '') or event.get('H', ''),
                    'away_team': event.get('O2', '') or event.get('A', ''),
                    'home_score': event.get('S1'),
                    'away_score': event.get('S2'),
                    'status': 'live' if event.get('S', 0) == 1 else 'scheduled',
                    'all_markets': markets,
                    'market_count': len(markets),
                }

                # Extract 1X2 odds for quick access
                for m in markets:
                    if m['type_id'] == 1 and len(m['outcomes']) >= 3:
                        match['odds_home'] = m['outcomes'][0].get('odds')
                        match['odds_draw'] = m['outcomes'][1].get('odds')
                        match['odds_away'] = m['outcomes'][2].get('odds')
                        break

                matches.append(match)

        return matches

    def _parse_all_markets(self, event):
        """
        Parse ALL markets from the G (Game Events) array.
        Each market has:
          T (Type ID)      → market category
          E[] (Outcomes)   → choices within this market
            C (Coefficient) → odds
            P (Parameter)   → line value (handicap, O/U line, etc.)
            T (sub-type)    → outcome type within this market
        """
        all_markets = []
        raw_markets = event.get('G', []) or event.get('GE', [])

        for gm in raw_markets:
            type_id = gm.get('T', 0)
            outcomes_raw = gm.get('E', [])

            market_name = MARKET_TYPES.get(type_id, f'Unknown Type {type_id}')
            outcomes = []

            for oc in outcomes_raw:
                odds = oc.get('C')
                param = oc.get('P')
                sub_type = oc.get('T')

                # Try to determine label
                label = None
                type_labels = OUTCOME_LABELS.get(type_id)
                if type_labels:
                    label = type_labels.get(len(outcomes))

                # For O/U and handicap, param is the line value
                if param is not None and param > 0:
                    if type_id in (4, 9, 17, 18, 31, 32, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80):
                        label = f'Over {param}' if 'Over' in str(outcomes) else f'Under {param}'

                outcome = {
                    'odds': float(odds) if odds else None,
                }
                if param is not None:
                    outcome['parameter'] = param
                if label:
                    outcome['label'] = label

                outcomes.append(outcome)

            # Assign labels for common patterns
            if type_id in (1,) and len(outcomes) >= 1:
                if len(outcomes) >= 1: outcomes[0]['label'] = '1'
                if len(outcomes) >= 2: outcomes[1]['label'] = 'X'
                if len(outcomes) >= 3: outcomes[2]['label'] = '2'
            elif type_id == 2 and len(outcomes) >= 1:
                if len(outcomes) >= 1: outcomes[0]['label'] = '1X'
                if len(outcomes) >= 2: outcomes[1]['label'] = '12'
                if len(outcomes) >= 3: outcomes[2]['label'] = 'X2'
            elif type_id == 3 and len(outcomes) >= 1:
                if len(outcomes) >= 1: outcomes[0]['label'] = 'Yes'
                if len(outcomes) >= 2: outcomes[1]['label'] = 'No'
            elif type_id == 5 and len(outcomes) >= 2:
                if outcomes[0].get('parameter') is not None:
                    outcomes[0]['label'] = f"Home {_fmt_param(outcomes[0].get('parameter'))}"
                    outcomes[1]['label'] = f"Away {_fmt_param(-outcomes[1].get('parameter'))}" if outcomes[1].get('parameter') else 'Away'

            if outcomes:
                all_markets.append({
                    'type_id': type_id,
                    'name': market_name,
                    'outcomes': outcomes,
                })

        return all_markets

    def sync_to_db(self):
        matches = self.fetch_live_matches()
        conn = get_db()
        conn.execute("DELETE FROM matches WHERE status = 'scheduled'")

        for m in matches[:50]:
            markets_json = json.dumps(m.get('all_markets', []), ensure_ascii=False)
            conn.execute(
                """INSERT OR REPLACE INTO matches 
                (external_id, home_team, away_team, home_score, away_score, status, odds_home, odds_draw, odds_away, markets_data, match_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (m['external_id'], m['home_team'], m['away_team'],
                 m['home_score'], m['away_score'], m['status'],
                 m.get('odds_home'), m.get('odds_draw'), m.get('odds_away'),
                 markets_json, datetime.now())
            )

        conn.commit()
        conn.close()
        print(f"Synced {len(matches)} matches from 1xBet ({sum(m['market_count'] for m in matches)} total markets)")


def _fmt_param(p):
    if p is None:
        return ''
    if p > 0:
        return f'+{p}'
    return str(p)
