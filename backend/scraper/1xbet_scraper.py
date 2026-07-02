"""
1xBet scraper — FULL dynamic market extraction via API JSON.
- Uses undetected_chromedriver to bypass Cloudflare
- Calls LineFeed API from within browser context via fetch()
- Parses ALL market types from G (Game Events) array
- Maps Type ID (T) → market name, extracts Parameter (P) + Odds (C)
- Saves complete structured data to JSON
"""

import json
import time
import zlib
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ============================================================
# COMPREHENSIVE MARKET TYPE MAPPING (Type ID → Name)
# ============================================================
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
    44: 'Home Score in Both Halves',
    45: 'Away Score in Both Halves',
    46: '1st 10 Min Winner',
    47: 'Last 10 Min Winner',
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
    82: 'Home Total Goals',
    83: 'Away Total Goals',
    84: 'Home Corners',
    85: 'Away Corners',
    86: 'Home Yellow Cards',
    87: 'Away Yellow Cards',
    88: 'Home Fouls',
    89: 'Away Fouls',
    90: 'Home Offsides',
    91: 'Away Offsides',
    92: 'Home Shots on Target',
    93: 'Away Shots on Target',
    94: 'Home Goal Kicks',
    95: 'Away Goal Kicks',
    96: 'Home Free Kicks',
    97: 'Away Free Kicks',
    98: 'Home Throw-ins',
    99: 'Away Throw-ins',
    100: 'Home Substitutions',
    101: 'Away Substitutions',
    102: '1st Half Draw No Bet',
    103: '2nd Half Draw No Bet',
    104: 'Home to Score',
    105: 'Away to Score',
    106: '1st Half BTTS',
    107: '2nd Half BTTS',
    108: 'Home 1st Half Clean Sheet',
    109: 'Away 1st Half Clean Sheet',
    110: 'Home 2nd Half Clean Sheet',
    111: 'Away 2nd Half Clean Sheet',
    112: 'Both Teams Score 1st Half',
    113: 'Both Teams Score 2nd Half',
    114: '1st Half Total Goals',
    115: '2nd Half Total Goals',
    116: 'Home Odd/Even Goals',
    117: 'Away Odd/Even Goals',
    118: 'First Team to Score',
    119: 'Last Team to Score',
    120: 'Both Teams to Score & Win',
    121: 'Win to Nil',
    122: 'Home Win to Nil',
    123: 'Away Win to Nil',
    124: '1st Half Correct Score Home',
    125: '1st Half Correct Score Away',
    126: 'Score After 10 Min',
    127: 'Score After 20 Min',
    128: 'Score After 30 Min',
    129: 'Score After 40 Min',
    130: 'Score After 50 Min',
    131: 'Score After 60 Min',
    132: 'Score After 70 Min',
    133: 'Score After 80 Min',
    134: 'Minute of First Goal Range',
    135: 'Minute of Last Goal Range',
    136: '1st Goal Between',
    137: 'Goal Scored by Team in Both Halves',
    138: '1st Half Winner & BTTS',
    139: '2nd Half Winner & BTTS',
    140: 'Half With Most Goals',
    141: 'Winning Margin',
    142: 'Home Winning Margin',
    143: 'Away Winning Margin',
}

# Outcome labels for common Type IDs
OUTCOME_LABELS = {
    1: ['1', 'X', '2'],
    2: ['1X', '12', 'X2'],
    3: ['Yes', 'No'],
    20: ['Home (DNB)', 'Away (DNB)'],
    33: ['Yes', 'No'],
    24: ['Yes', 'No'],
    25: ['Yes', 'No'],
    26: ['Yes', 'No'],
    27: ['Yes', 'No'],
    44: ['Yes', 'No'],
    45: ['Yes', 'No'],
    53: ['Yes', 'No'],
    54: ['Yes', 'No'],
    55: ['Yes', 'No'],
    104: ['Yes', 'No'],
    105: ['Yes', 'No'],
    118: ['Home', 'Away', 'No Goal'],
    119: ['Home', 'Away', 'No Goal'],
    141: ['1', '2', '3+'],
    142: ['1', '2', '3+'],
    143: ['1', '2', '3+'],
    52: ['Header', 'Shot', 'Free Kick', 'Penalty', 'Own Goal'],
    46: ['Home', 'Away', 'Draw'],
    47: ['Home', 'Away', 'Draw'],
    48: ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90', 'No Goal'],
    51: ['Yes', 'No'],
}


def fmt_param(p):
    if p is None:
        return ''
    if isinstance(p, (int, float)):
        if p > 0:
            return f'+{p}'
        return str(p)
    return str(p)


def parse_all_markets(event):
    """
    Parse ALL markets from the G (Game Events) array of a single match event.
    Returns list of market objects:
      { type_id, name, outcomes: [{ odds, param, label }] }
    """
    all_markets = []
    raw_markets = event.get('G', []) or event.get('GE', [])

    for gm in raw_markets:
        type_id = gm.get('T', 0)
        outcomes_raw = gm.get('E', [])
        market_name = MARKET_TYPES.get(type_id, f'Unknown Type {type_id}')
        default_labels = OUTCOME_LABELS.get(type_id, [])

        outcomes = []

        for i, oc in enumerate(outcomes_raw):
            odds = oc.get('C')
            param = oc.get('P')
            sub_type = oc.get('T')

            out = {
                'odds': float(odds) if odds else None,
            }

            if param is not None:
                out['param'] = param

            # Assign label
            if i < len(default_labels):
                label = default_labels[i]
                # Append param if it's a handicap/O/U line
                if type_id in (5, 36, 37, 70) and param is not None:
                    label = f'{label} ({fmt_param(param)})'
                elif type_id in (4, 9, 17, 18, 31, 32, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80) and param is not None:
                    label = f'{label} {param}'
                out['label'] = label
            elif param is not None:
                if type_id in (4, 9):
                    out['label'] = f'Over {param}' if i == 0 else f'Under {param}'
                elif type_id in (5,):
                    out['label'] = f'Home {fmt_param(param)}' if i == 0 else f'Away {fmt_param(-param) if isinstance(param, (int, float)) else param}'
                elif type_id in (10, 17, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100):
                    out['label'] = f'Home Over {param}' if i == 0 else f'Home Under {param}'
                elif type_id in (11, 18, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101):
                    out['label'] = f'Away Over {param}' if i == 0 else f'Away Under {param}'

            outcomes.append(out)

        if outcomes:
            all_markets.append({
                'type_id': type_id,
                'name': market_name,
                'outcomes': outcomes,
            })

    return all_markets


def fetch_via_browser(driver, url, params=None):
    """Execute fetch from within browser context to bypass Cloudflare."""
    param_str = json.dumps(params or {})
    script = f"""
        const url = '{url}' + '?' + new URLSearchParams({param_str}).toString();
        return fetch(url, {{
            headers: {{
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            }}
        }})
        .then(r => {{
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        }})
        .catch(e => e.message);
    """
    result = driver.execute_async_script(script)
    return parse_response_text(result)


def parse_response_text(text):
    """Try JSON parse, then zlib decompress + JSON parse."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        decompressed = zlib.decompress(text.encode('latin1'), -zlib.MAX_WBITS)
        return json.loads(decompressed)
    except Exception:
        pass
    return None


def scrape():
    """Main entry point — returns structured match data with ALL markets."""
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(30)

    try:
        print('[1/3] Opening 1xBet...')
        driver.get('https://1xbet.com/en')
        time.sleep(4)

        # Dismiss any popups
        try:
            for sel in ['.cookie__btn', '.modal__close', '.close-btn', '[data-role="close"]']:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    try:
                        el.click()
                        time.sleep(0.3)
                    except:
                        pass
        except:
            pass

        # Navigate to football
        try:
            football = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    '[data-name="football"], .sport-item__football, a[href*="football"]'
                ))
            )
            football.click()
            time.sleep(2)
        except:
            print('Football link not found; using current page')

        print('[2/3] Fetching API data from browser context...')

        # Try multiple API endpoints
        api_urls = [
            ('https://1xbet.com/LineFeed/GetSportsShortZip', {}),
            ('https://1xbet.com/LineFeed/GetChampionshipsZip', {
                'sports': 1, 'lng': 'en', 'tf': '2200000'
            }),
        ]

        raw = None
        for url, params in api_urls:
            raw = fetch_via_browser(driver, url, params)
            if raw and raw.get('Value'):
                break

        if not raw or not raw.get('Value'):
            print('Failed to fetch API data. Falling back to HTML parsing...')
            return scrape_html_fallback(driver)

        print('[3/3] Parsing ALL markets dynamically...')

        all_matches = []
        sg = raw['Value'].get('SG', [])
        for sport_group in sg:
            for event in sport_group.get('E', []):
                markets = parse_all_markets(event)

                has_1x2 = any(m['type_id'] == 1 for m in markets)
                match_entry = {
                    'match_id': event.get('I'),
                    'home_team': event.get('O1', '') or event.get('H', ''),
                    'away_team': event.get('O2', '') or event.get('A', ''),
                    'home_score': event.get('S1'),
                    'away_score': event.get('S2'),
                    'status': 'live' if event.get('S', 0) == 1 else 'prematch',
                    'sport_id': event.get('N'),
                    'start_time': event.get('ST'),
                    'total_markets': len(markets),
                    'markets': markets,
                }

                # Pull 1X2 odds for convenience
                for m in markets:
                    if m['type_id'] == 1 and len(m['outcomes']) >= 3:
                        match_entry['odds_1'] = m['outcomes'][0].get('odds')
                        match_entry['odds_X'] = m['outcomes'][1].get('odds')
                        match_entry['odds_2'] = m['outcomes'][2].get('odds')
                        break

                all_matches.append(match_entry)

        output = {
            'source': '1xBet',
            'scrape_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'total_matches': len(all_matches),
            'total_markets': sum(m['total_markets'] for m in all_matches),
            'matches': all_matches,
        }

        # Save to JSON
        with open('1xbet_full_odds.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f'\nDone! {len(all_matches)} matches, {output["total_markets"]} total markets')
        print(f'Saved to 1xbet_full_odds.json')

        # Also print summary per match
        for m in all_matches[:10]:
            print(f'  {m["home_team"]} vs {m["away_team"]} — {m["total_markets"]} markets')

        return output

    finally:
        driver.quit()


def scrape_html_fallback(driver):
    """
    Fallback: parse visible HTML markets dynamically.
    Looks for all market buttons/links and extracts via data attributes.
    """
    print('Using HTML fallback (limited markets)...')
    all_data = []

    try:
        matches = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                '.c-events__item, .event__item, [class*="match"], [class*="event"]'
            ))
        )
    except TimeoutException:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(2)
        matches = driver.find_elements(
            By.CSS_SELECTOR,
            '.c-events__item, .event__item, [class*="match"], [class*="event"]'
        )

    print(f'Found {len(matches)} match elements (HTML)')

    for idx, match in enumerate(matches[:10]):
        try:
            driver.execute_script('arguments[0].scrollIntoView({block: "center"});', match)
            time.sleep(0.3)

            # Try expanding markets
            try:
                expand = match.find_element(By.CSS_SELECTOR, '[class*="more"], [class*="expand"]')
                expand.click()
                time.sleep(0.5)
            except:
                pass

            home = 'Unknown'
            away = 'Unknown'
            try:
                home = match.find_element(By.CSS_SELECTOR, '.c-events__team._home, .team-home, .home-team').text.strip()
                away = match.find_element(By.CSS_SELECTOR, '.c-events__team._away, .team-away, .away-team').text.strip()
            except:
                try:
                    teams = match.find_elements(By.CSS_SELECTOR, '.c-events__team')
                    if len(teams) >= 2:
                        home = teams[0].text.strip()
                        away = teams[1].text.strip()
                except:
                    pass

            markets = []
            # Find ALL bet buttons - each represents a market outcome
            all_btns = match.find_elements(By.CSS_SELECTOR, '[class*="bet"], [class*="odds"], [data-market]')
            for btn in all_btns:
                try:
                    mtype = btn.get_attribute('data-market') or btn.get_attribute('data-type') or ''
                    odds_text = btn.text.strip()
                    odds_val = float(odds_text) if odds_text.replace('.', '').isdigit() else None

                    if odds_val:
                        # Determine market category from HTML classes/data
                        classes = (btn.get_attribute('class') or '') + ' ' + mtype
                        param = btn.get_attribute('data-param') or btn.get_attribute('data-line')

                        market_name = 'Unknown'
                        outcome_label = classes

                        if 'handicap' in classes.lower() or 'fora' in classes.lower():
                            market_name = 'Handicap'
                        elif 'over' in classes.lower() or 'under' in classes.lower() or 'total' in classes.lower():
                            market_name = 'Over/Under'
                        elif 'double' in classes.lower() or 'chance' in classes.lower():
                            market_name = 'Double Chance'
                        elif 'btts' in classes.lower() or 'both' in classes.lower():
                            market_name = 'Both Teams to Score'
                        elif 'correct' in classes.lower() or 'score' in classes.lower():
                            market_name = 'Correct Score'
                        elif ' 1' == mtype or ' X' == mtype or ' 2' == mtype:
                            market_name = '1X2'
                            outcome_label = mtype.strip()

                        markets.append({
                            'name': market_name,
                            'outcome': outcome_label,
                            'odds': odds_val,
                            'parameter': param,
                        })
                except:
                    pass

            entry = {
                'home_team': home,
                'away_team': away,
                'total_markets': len(markets),
                'markets': markets,
            }
            all_data.append(entry)
            print(f'  [{idx+1}] {home} vs {away} — {len(markets)} outcomes')

        except Exception as e:
            print(f'  [{idx+1}] Error: {e}')
            continue

    with open('1xbet_fallback_odds.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f'\nHTML fallback done: {len(all_data)} matches → 1xbet_fallback_odds.json')
    return all_data


if __name__ == '__main__':
    result = scrape()
    if result:
        print(f'\nSummary: {result["total_matches"]} matches, {result["total_markets"]} market groups')
        print('Market types found:')
        type_ids = set()
        for m in result['matches']:
            for mk in m['markets']:
                type_ids.add(mk['type_id'])
        for tid in sorted(type_ids):
            print(f'  T={tid}: {MARKET_TYPES.get(tid, "Unknown")}')
