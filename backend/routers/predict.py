from fastapi import APIRouter
from pydantic import BaseModel
from prediction import predict
from data.markets import all_market_odds
from database import get_db
import json

router = APIRouter(prefix='/api')


class ManualPredictRequest(BaseModel):
    home_team: str
    away_team: str
    form_home: str = ''
    form_away: str = ''
    position_home: int | None = None
    position_away: int | None = None
    odds_home: float = 2.0
    odds_draw: float = 3.0
    odds_away: float = 4.0
    total_teams: int = 20


@router.post('/predict/manual')
async def manual_predict(req: ManualPredictRequest):
    match_data = {
        'form_home': req.form_home,
        'form_away': req.form_away,
        'position_home': req.position_home,
        'position_away': req.position_away,
        'h2h': [],
        'odds_home': req.odds_home,
        'odds_draw': req.odds_draw,
        'odds_away': req.odds_away,
        'odds_opening_home': req.odds_home,
        'odds_opening_away': req.odds_away,
        'total_teams': req.total_teams,
    }
    result = predict(match_data)
    result['home_team'] = req.home_team
    result['away_team'] = req.away_team
    all_markets = all_market_odds(match_data)
    result['all_markets'] = all_markets

    # Save to prediction history
    try:
        conn = get_db()
        conn.execute(
            """INSERT INTO predictions (match_id, home_team, away_team, predicted_winner, confidence, score_breakdown, market_data)
               VALUES (-1, ?, ?, ?, ?, ?, ?)""",
            (req.home_team, req.away_team, result['winner'], result['confidence'],
             json.dumps(result.get('scores', {})),
             json.dumps(all_markets.get('markets', []), ensure_ascii=False))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Save history error: {e}")

    return result
