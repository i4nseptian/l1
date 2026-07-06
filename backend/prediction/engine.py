"""Prediction engine with historical accuracy feedback."""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'app.db')

DEFAULT_WEIGHTS = {
    'form': 0.25,
    'h2h': 0.15,
    'position': 0.10,
    'odds_movement': 0.15,
    'factors': 0.10,
    'draw_bias': 0.05,
}


def _get_accuracy_stats():
    """Return historical accuracy by predicted winner type."""
    stats = {'home': {'total': 0, 'correct': 0}, 'draw': {'total': 0, 'correct': 0}, 'away': {'total': 0, 'correct': 0}}
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT predicted_winner, is_correct FROM predictions WHERE is_correct IS NOT NULL"
        ).fetchall()
        conn.close()
        for winner, correct in rows:
            if winner in stats:
                stats[winner]['total'] += 1
                if correct:
                    stats[winner]['correct'] += 1
    except:
        pass
    for k in stats:
        if stats[k]['total'] > 0:
            stats[k]['accuracy'] = stats[k]['correct'] / stats[k]['total']
        else:
            stats[k]['accuracy'] = 0.5
    return stats


def _score_form(form_str):
    if not form_str:
        return 50
    scores = {'W': 100, 'D': 50, 'L': 0}
    vals = [scores.get(c, 50) for c in form_str.upper()[:5]]
    return sum(vals) / len(vals) if vals else 50


def _score_position(pos, total_teams=20):
    if pos is None:
        return 50
    return max(0, 100 - ((pos - 1) / max(total_teams - 1, 1)) * 100)


def _score_h2h(h2h_records, team):
    if not h2h_records:
        return 50
    total = 0
    for rec in h2h_records[-5:]:
        result = rec.get('result', '')
        if result == team:
            total += 100
        elif result == 'draw':
            total += 50
        else:
            total += 0
    return total / len(h2h_records) if h2h_records else 50


def _score_odds_movement(odds_current, odds_opening):
    if not odds_opening or not odds_current or odds_opening == 0:
        return 50
    change = ((odds_opening - odds_current) / odds_opening) * 100
    return min(100, max(0, 50 + change * 10))


def generate_analysis(match_data, result, team_stats=None):
    lines = []
    home = team_stats.get('home', {}) if team_stats else {}
    away = team_stats.get('away', {}) if team_stats else {}
    home_name = home.get('name', 'Home')
    away_name = away.get('name', 'Away')

    # Form analysis
    form_h = match_data.get('form_home', '')
    form_a = match_data.get('form_away', '')
    if form_h and form_a:
        h_wins = form_h.upper().count('W')
        a_wins = form_a.upper().count('W')
        h_losses = form_h.upper().count('L')
        a_losses = form_a.upper().count('L')
        if h_wins > a_wins + 1:
            lines.append(f"{home_name} lebih konsisten ({form_h[:5]}) vs {away_name} ({form_a[:5]})")
        elif a_wins > h_wins + 1:
            lines.append(f"{away_name} lebih konsisten ({form_a[:5]}) vs {home_name} ({form_h[:5]})")
        elif h_losses > a_losses + 1:
            lines.append(f"{away_name} lebih stabil ({form_a[:5]}) vs {home_name} ({form_h[:5]})")
        elif a_losses > h_losses + 1:
            lines.append(f"{home_name} lebih stabil ({form_h[:5]}) vs {away_name} ({form_a[:5]})")

    # Position analysis
    pos_h = match_data.get('position_home')
    pos_a = match_data.get('position_away')
    if pos_h is not None and pos_a is not None:
        if pos_h < pos_a:
            lines.append(f"{home_name} unggul klasemen (#{pos_h} vs #{pos_a})")
        elif pos_a < pos_h:
            lines.append(f"{away_name} unggul klasemen (#{pos_a} vs #{pos_h})")

    # H2H analysis
    h2h = match_data.get('h2h', [])
    if h2h:
        h_wins = sum(1 for r in h2h if r.get('result') == 'home')
        a_wins = sum(1 for r in h2h if r.get('result') == 'away')
        draws = sum(1 for r in h2h if r.get('result') == 'draw')
        if h_wins > a_wins:
            lines.append(f"Rekor H2H: {home_name} unggul ({h_wins}W {draws}D {a_wins}L)")
        elif a_wins > h_wins:
            lines.append(f"Rekor H2H: {away_name} unggul ({a_wins}W {draws}D {h_wins}L)")
        elif draws >= 3:
            lines.append(f"Keduanya sering imbang ({draws}X dari {len(h2h)} pertemuan)")

    # Odds analysis
    odds_h = match_data.get('odds_home', 0)
    odds_a = match_data.get('odds_away', 0)
    if odds_h and odds_a:
        if odds_h < odds_a and odds_h < 2.0:
            lines.append(f"Market kuat mendukung {home_name} (odds {odds_h:.2f})")
        elif odds_a < odds_h and odds_a < 2.0:
            lines.append(f"Market kuat mendukung {away_name} (odds {odds_a:.2f})")
        elif abs(odds_h - odds_a) < 0.5:
            lines.append(f"Odds seimbang ({odds_h:.2f} vs {odds_a:.2f}) menandakan laga ketat")

    # Goal stats
    if home.get('won') is not None and home.get('played'):
        h_win_rate = home['won'] / max(home['played'], 1) * 100
        a_win_rate = away['won'] / max(away['played'], 1) * 100
        if h_win_rate > 60:
            lines.append(f"{home_name} punya rekor kandang kuat ({home['won']}W/{home['played']}P)")
        if a_win_rate > 60:
            lines.append(f"{away_name} punya rekor tandang kuat ({away['won']}W/{away['played']}P)")

    # Draw analysis
    draw_score = result.get('scores', {}).get('draw', 0)
    total_score = sum(result.get('scores', {}).values()) or 1
    draw_pct = draw_score / total_score * 100
    if draw_pct >= 35:
        lines.append("Kedua tim memiliki performa berimbang, potensi imbang tinggi")

    # Winner explanation
    winner = result.get('winner', 'draw')
    if winner == 'home':
        lines.append(f"Kesimpulan: {home_name} lebih diunggulkan berdasarkan analisis statistik")
    elif winner == 'away':
        lines.append(f"Kesimpulan: {away_name} lebih diunggulkan berdasarkan analisis statistik")
    else:
        lines.append("Kesimpulan: Pertandingan diprediksi berakhir imbang")

    return lines


def predict(match_data):
    w = DEFAULT_WEIGHTS
    history = _get_accuracy_stats()

    form_h = _score_form(match_data.get('form_home', ''))
    form_a = _score_form(match_data.get('form_away', ''))
    pos_h = _score_position(match_data.get('position_home'), match_data.get('total_teams', 20))
    pos_a = _score_position(match_data.get('position_away'), match_data.get('total_teams', 20))
    h2h_h = _score_h2h(match_data.get('h2h', []), 'home')
    h2h_a = _score_h2h(match_data.get('h2h', []), 'away')
    odds_mov_h = _score_odds_movement(match_data.get('odds_home'), match_data.get('odds_opening_home'))
    odds_mov_a = _score_odds_movement(match_data.get('odds_away'), match_data.get('odds_opening_away'))

    odds_h = match_data.get('odds_home', 2.0)
    odds_d = match_data.get('odds_draw', 3.0)
    odds_a = match_data.get('odds_away', 3.0)
    imp_h = (1 / odds_h) * 100
    imp_d = (1 / odds_d) * 100
    imp_a = (1 / odds_a) * 100
    total_imp = imp_h + imp_d + imp_a
    imp_h = (imp_h / total_imp) * 100
    imp_a = (imp_a / total_imp) * 100

    # Historical accuracy boost
    hist_h = history['home']['accuracy']
    hist_d = history['draw']['accuracy']
    hist_a = history['away']['accuracy']
    hist_factor = 0.08

    home_score = (
        w['form'] * form_h +
        w['h2h'] * h2h_h +
        w['position'] * pos_h +
        w['odds_movement'] * odds_mov_h +
        w['factors'] * imp_h +
        hist_factor * (hist_h * 100)
    )

    away_score = (
        w['form'] * form_a +
        w['h2h'] * h2h_a +
        w['position'] * pos_a +
        w['odds_movement'] * odds_mov_a +
        w['factors'] * imp_a +
        hist_factor * (hist_a * 100)
    )

    draw_score = (form_h + form_a) / 2 * w['draw_bias'] + imp_d * w['factors'] + hist_factor * (hist_d * 100)

    scores = {
        'home': round(home_score, 1),
        'draw': round(draw_score, 1),
        'away': round(away_score, 1),
    }

    winner = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = round((scores[winner] / total) * 100, 1)

    return {
        'winner': winner,
        'confidence': confidence,
        'scores': scores,
        'breakdown': {
            'form_home': round(form_h, 1),
            'form_away': round(form_a, 1),
            'position_home': round(pos_h, 1),
            'position_away': round(pos_a, 1),
            'h2h_home': round(h2h_h, 1),
            'h2h_away': round(h2h_a, 1),
            'odds_movement_home': round(odds_mov_h, 1),
            'odds_movement_away': round(odds_mov_a, 1),
        },
        'history_accuracy': {
            'home_win': round(history['home']['accuracy'] * 100, 1),
            'draw': round(history['draw']['accuracy'] * 100, 1),
            'away_win': round(history['away']['accuracy'] * 100, 1),
        },
    }


def predict_with_custom_logic(match_data, custom_rules):
    result = predict(match_data)
    for rule in custom_rules:
        if not rule.get('is_active', True):
            continue
        field = rule['condition_field']
        op = rule['operator']
        val = rule['condition_value']
        actual = match_data.get(field)
        if actual is None:
            continue
        match_found = False
        if op == '<':
            match_found = actual < val
        elif op == '>':
            match_found = actual > val
        elif op == '=':
            match_found = actual == val
        elif op == '>=':
            match_found = actual >= val
        elif op == '<=':
            match_found = actual <= val
        if match_found:
            result['scores'][rule['result_recommendation']] += rule['weight_modifier']
            result['scores'][rule['result_recommendation']] = max(0, result['scores'][rule['result_recommendation']])

    winner = max(result['scores'], key=result['scores'].get)
    total = sum(result['scores'].values()) or 1
    result['winner'] = winner
    result['confidence'] = round((result['scores'][winner] / total) * 100, 1)
    return result
