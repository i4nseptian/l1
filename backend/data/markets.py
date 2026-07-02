"""Calculate odds for ALL football betting markets with value ratings."""

import math
import json
import os

FACTORS_PATH = os.path.join(os.path.dirname(__file__), 'factors.json')

FACTOR_GROUPS = {}
try:
    with open(FACTORS_PATH, 'r', encoding='utf-8') as f:
        fc = json.load(f)
    for m in fc.get('markets', []):
        tid = m.get('market_type')
        if tid not in FACTOR_GROUPS:
            FACTOR_GROUPS[tid] = {'group': m.get('group', 'Other'), 'name': m.get('market_name', f'Type {tid}')}
except:
    pass


TYPE_ID_MAP = {
    1: 'Match Winner (1X2)',
    2: 'Double Chance',
    3: 'Both Teams to Score',
    4: 'Over/Under Total Goals',
    5: 'Asian Handicap',
    6: 'Correct Score',
    7: 'Total Goals Odd/Even',
    8: 'Exact Total Goals',
    9: 'Over/Under Asian Total',
    10: 'Individual Total 1',
    11: 'Individual Total 2',
    12: 'Home Team Exact Goals',
    13: 'Away Team Exact Goals',
    14: 'Home Correct Score',
    15: 'Home Total Odd/Even',
    16: 'Away Total Odd/Even',
    17: 'Home Team O/U',
    18: 'Away Team O/U',
    20: 'Draw No Bet',
    21: '1st Half Winner',
    31: '1st Half O/U',
    32: '2nd Half O/U',
    33: 'Win Both Halves',
    34: '1st Half Exact Goals',
    35: '2nd Half Exact Goals',
    42: '1st Half Odd/Even',
    141: 'Winning Margin',
    93: 'Highest Scoring Half',
}


def implied_prob(odds):
    return 1 / odds if odds and odds > 0 else 0


def fair_odds(prob):
    return round(1 / prob, 2) if prob > 0 else 999


def poisson(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.e ** (-lam)) * (lam ** k) / math.factorial(k)


def value_score(fair_prob, market_odds):
    """Return value rating: difference between fair probability and implied probability."""
    if not market_odds or market_odds <= 0:
        return 0
    implied = 1 / market_odds
    return round((fair_prob - implied) * 100, 1)


def value_label(val):
    if val > 5:
        return 'excellent'
    if val > 2:
        return 'good'
    if val > -2:
        return 'fair'
    return 'poor'


def make_market(type_id, selections, category=None):
    """Build a standardized market entry with value ratings."""
    outcomes = []
    for key, data in selections.items():
        v = value_score(data['prob'] / 100, data.get('odds'))
        outcomes.append({
            'label': key,
            'odds': data.get('odds'),
            'prob': data['prob'],
            'value': v,
            'value_label': value_label(v),
        })
    fc = FACTOR_GROUPS.get(type_id, {})
    return {
        'type_id': type_id,
        'name': TYPE_ID_MAP.get(type_id, fc.get('name', f'Market {type_id}')),
        'category': category or fc.get('group', 'General'),
        'outcomes': outcomes,
    }


def all_market_odds(match_data):
    oh = match_data.get('odds_home', 2.0)
    od = match_data.get('odds_draw', 3.0)
    oa = match_data.get('odds_away', 4.0)

    imp_h = 1 / oh
    imp_d = 1 / od
    imp_a = 1 / oa
    margin = imp_h + imp_d + imp_a
    fair_h = imp_h / margin
    fair_d = imp_d / margin
    fair_a = imp_a / margin

    home_strength = (1 - fair_a) * 3
    away_strength = (1 - fair_h) * 3
    lam_h = home_strength
    lam_a = away_strength
    lam_t = lam_h + lam_a

    markets = []

    # 1X2
    markets.append(make_market(1, {
        '1': {'odds': round(oh, 2), 'prob': round(fair_h * 100, 1)},
        'X': {'odds': round(od, 2), 'prob': round(fair_d * 100, 1)},
        '2': {'odds': round(oa, 2), 'prob': round(fair_a * 100, 1)},
    }, 'Match Result'))

    # Double Chance
    dc_1x = fair_h + fair_d
    dc_12 = fair_h + fair_a
    dc_x2 = fair_d + fair_a
    markets.append(make_market(2, {
        '1X': {'odds': fair_odds(dc_1x), 'prob': round(dc_1x * 100, 1)},
        '12': {'odds': fair_odds(dc_12), 'prob': round(dc_12 * 100, 1)},
        'X2': {'odds': fair_odds(dc_x2), 'prob': round(dc_x2 * 100, 1)},
    }, 'Match Result'))

    # Draw No Bet
    dnb_total = fair_h + fair_a
    markets.append(make_market(20, {
        'Home': {'odds': fair_odds(fair_h / dnb_total), 'prob': round(fair_h / dnb_total * 100, 1)},
        'Away': {'odds': fair_odds(fair_a / dnb_total), 'prob': round(fair_a / dnb_total * 100, 1)},
    }, 'Match Result'))

    # BTTS
    btts_yes = 1 - (poisson(0, lam_h) * poisson(0, lam_a))
    markets.append(make_market(3, {
        'Yes': {'odds': fair_odds(btts_yes), 'prob': round(btts_yes * 100, 1)},
        'No': {'odds': fair_odds(1 - btts_yes), 'prob': round((1 - btts_yes) * 100, 1)},
    }, 'Both Teams to Score'))

    # Over / Under
    for line in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]:
        prob_over = 1 - sum(poisson(k, lam_t) for k in range(int(line)))
        prob_under = 1 - prob_over
        markets.append(make_market(4, {
            f'Over {line}': {'odds': fair_odds(prob_over), 'prob': round(prob_over * 100, 1)},
            f'Under {line}': {'odds': fair_odds(prob_under), 'prob': round(prob_under * 100, 1)},
        }, 'Over / Under'))

    # Asian Handicap
    handicap_prob = fair_h - fair_a
    if abs(handicap_prob) > 0.15:
        h_home = fair_h + fair_d * 0.3
        h_away = fair_a + fair_d * 0.7
    else:
        h_home = fair_h + fair_d * 0.4
        h_away = fair_a + fair_d * 0.6
    markets.append(make_market(5, {
        'Home -0.5': {'odds': fair_odds(h_home), 'prob': round(h_home * 100, 1)},
        'Away +0.5': {'odds': fair_odds(h_away), 'prob': round(h_away * 100, 1)},
    }, 'Handicap'))

    # Individual Total Home (O/U)
    for line in [0.5, 1.5, 2.5]:
        prob_over = 1 - sum(poisson(k, lam_h) for k in range(int(line)))
        prob_under = 1 - prob_over
        markets.append(make_market(17, {
            f'Over {line}': {'odds': fair_odds(prob_over), 'prob': round(prob_over * 100, 1)},
            f'Under {line}': {'odds': fair_odds(prob_under), 'prob': round(prob_under * 100, 1)},
        }, 'Individual Total'))

    # Individual Total Away (O/U)
    for line in [0.5, 1.5, 2.5]:
        prob_over = 1 - sum(poisson(k, lam_a) for k in range(int(line)))
        prob_under = 1 - prob_over
        markets.append(make_market(18, {
            f'Over {line}': {'odds': fair_odds(prob_over), 'prob': round(prob_over * 100, 1)},
            f'Under {line}': {'odds': fair_odds(prob_under), 'prob': round(prob_under * 100, 1)},
        }, 'Individual Total'))

    # Home Exact Goals
    home_goals = {}
    for g in range(5):
        prob_g = poisson(g, lam_h)
        home_goals[f'{g} goals'] = {'odds': fair_odds(prob_g), 'prob': round(prob_g * 100, 1)}
    markets.append(make_market(12, home_goals, 'Team Goals'))

    # Away Exact Goals
    away_goals = {}
    for g in range(5):
        prob_g = poisson(g, lam_a)
        away_goals[f'{g} goals'] = {'odds': fair_odds(prob_g), 'prob': round(prob_g * 100, 1)}
    markets.append(make_market(13, away_goals, 'Team Goals'))

    # Total Goals
    total_g = {}
    for g in range(7):
        prob_g = poisson(g, lam_t)
        total_g[f'{g} goals'] = {'odds': fair_odds(prob_g), 'prob': round(prob_g * 100, 1)}
    total_g['7+ goals'] = {
        'odds': fair_odds(1 - sum(poisson(k, lam_t) for k in range(7))),
        'prob': round((1 - sum(poisson(k, lam_t) for k in range(7))) * 100, 1),
    }
    markets.append(make_market(8, total_g, 'Total Goals'))

    # Odd / Even
    prob_odd = sum(poisson(k, lam_t) for k in range(0, 15) if k % 2 == 1)
    prob_even = 1 - prob_odd
    markets.append(make_market(7, {
        'Odd': {'odds': fair_odds(prob_odd), 'prob': round(prob_odd * 100, 1)},
        'Even': {'odds': fair_odds(prob_even), 'prob': round(prob_even * 100, 1)},
    }, 'Total Goals'))

    # 1st Half Winner (simplified — 45% of total goals)
    lam_1h = lam_t * 0.45
    lam_h_1h = lam_h * 0.45
    lam_a_1h = lam_a * 0.45
    prob_1h_h = 1 - poisson(0, lam_h_1h)  # simplified: home scores in 1H
    prob_1h_a = 1 - poisson(0, lam_a_1h)
    prob_1h_d = 1 - prob_1h_h - prob_1h_a
    if prob_1h_d < 0: prob_1h_d = 0.1
    total_1h = prob_1h_h + prob_1h_a + prob_1h_d
    markets.append(make_market(21, {
        '1': {'odds': fair_odds(prob_1h_h / total_1h), 'prob': round(prob_1h_h / total_1h * 100, 1)},
        'X': {'odds': fair_odds(prob_1h_d / total_1h), 'prob': round(prob_1h_d / total_1h * 100, 1)},
        '2': {'odds': fair_odds(prob_1h_a / total_1h), 'prob': round(prob_1h_a / total_1h * 100, 1)},
    }, 'First Half'))

    # 1st Half O/U 0.5, 1.5
    for line in [0.5, 1.5]:
        prob_over = 1 - sum(poisson(k, lam_1h) for k in range(int(line)))
        prob_under = 1 - prob_over
        markets.append(make_market(31, {
            f'Over {line}': {'odds': fair_odds(prob_over), 'prob': round(prob_over * 100, 1)},
            f'Under {line}': {'odds': fair_odds(prob_under), 'prob': round(prob_under * 100, 1)},
        }, 'First Half'))

    # 1st Half Odd/Even
    prob_1h_odd = sum(poisson(k, lam_1h) for k in range(0, 10) if k % 2 == 1)
    prob_1h_even = 1 - prob_1h_odd
    markets.append(make_market(42, {
        'Odd': {'odds': fair_odds(prob_1h_odd), 'prob': round(prob_1h_odd * 100, 1)},
        'Even': {'odds': fair_odds(prob_1h_even), 'prob': round(prob_1h_even * 100, 1)},
    }, 'First Half'))

    # 1st Half Exact Goals
    gh_1h = {}
    for g in range(4):
        prob_g = poisson(g, lam_1h)
        gh_1h[f'{g} goals'] = {'odds': fair_odds(prob_g), 'prob': round(prob_g * 100, 1)}
    markets.append(make_market(34, gh_1h, 'First Half'))

    # Win Both Halves (simplified)
    markets.append(make_market(33, {
        'Yes': {'odds': fair_odds(0.25), 'prob': 25.0},
        'No': {'odds': fair_odds(0.75), 'prob': 75.0},
    }, 'Match Result'))

    # Highest Scoring Half
    lam_2h = lam_t * 0.55
    prob_h1 = 1 - poisson(0, lam_1h)  # prob at least 1 goal in 1H
    prob_h2 = 1 - poisson(0, lam_2h)
    if prob_h1 + prob_h2 > 1:
        prob_h1 *= 0.8  # normalize
        prob_h2 *= 0.8
    prob_even_halves = 1 - prob_h1 - prob_h2
    if prob_even_halves < 0: prob_even_halves = 0
    total_hh = prob_h1 + prob_h2 + prob_even_halves
    markets.append(make_market(93, {
        '1st Half': {'odds': fair_odds(prob_h1 / total_hh), 'prob': round(prob_h1 / total_hh * 100, 1)},
        '2nd Half': {'odds': fair_odds(prob_h2 / total_hh), 'prob': round(prob_h2 / total_hh * 100, 1)},
        'Equal': {'odds': fair_odds(prob_even_halves / total_hh), 'prob': round(prob_even_halves / total_hh * 100, 1)},
    }, 'First Half'))

    # Home Team Total Odd/Even
    prob_h_odd = sum(poisson(k, lam_h) for k in range(0, 10) if k % 2 == 1)
    prob_h_even = 1 - prob_h_odd
    markets.append(make_market(15, {
        'Odd': {'odds': fair_odds(prob_h_odd), 'prob': round(prob_h_odd * 100, 1)},
        'Even': {'odds': fair_odds(prob_h_even), 'prob': round(prob_h_even * 100, 1)},
    }, 'Team Goals'))

    # Away Team Total Odd/Even
    prob_a_odd = sum(poisson(k, lam_a) for k in range(0, 10) if k % 2 == 1)
    prob_a_even = 1 - prob_a_odd
    markets.append(make_market(16, {
        'Odd': {'odds': fair_odds(prob_a_odd), 'prob': round(prob_a_odd * 100, 1)},
        'Even': {'odds': fair_odds(prob_a_even), 'prob': round(prob_a_even * 100, 1)},
    }, 'Team Goals'))

    # Correct Score (top 12)
    cs_list = []
    for hg in range(5):
        for ag in range(5):
            prob_score = poisson(hg, lam_h) * poisson(ag, lam_a)
            if prob_score > 0.005:
                cs_list.append((prob_score, f'{hg}-{ag}'))
    cs_list.sort(reverse=True)
    cs_dict = {}
    for prob_score, label in cs_list[:12]:
        cs_dict[label] = {'odds': fair_odds(prob_score), 'prob': round(prob_score * 100, 1)}
    markets.append(make_market(6, cs_dict, 'Correct Score'))

    expected_goals = {
        'home': round(lam_h, 2),
        'away': round(lam_a, 2),
        'total': round(lam_t, 2),
    }

    return {
        'expected_goals': expected_goals,
        'markets': markets,
    }
