from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db
from routers import matches_router, factors_router, logic_router, predict_router, leagues_router, football_data_router, teams_router, world_cup_router
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Football Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches_router)
app.include_router(factors_router)
app.include_router(logic_router)
app.include_router(predict_router)
app.include_router(leagues_router)
app.include_router(football_data_router)
app.include_router(teams_router)
app.include_router(world_cup_router)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/history")
async def get_history():
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, m.home_team || ' vs ' || m.away_team as match_name
        FROM predictions p
        LEFT JOIN matches m ON p.match_id = m.id
        ORDER BY p.created_at DESC
        LIMIT 200
    """).fetchall()
    conn.close()

    predictions = []
    for r in rows:
        d = dict(r)
        if d.get('market_data'):
            try:
                d['market_data'] = json.loads(d['market_data'])
            except:
                d['market_data'] = []
        if d.get('score_breakdown'):
            try:
                d['score_breakdown'] = json.loads(d['score_breakdown'])
            except:
                pass
        predictions.append(d)

    return {'predictions': predictions}


@app.get("/api/history/stats")
async def history_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM predictions").fetchone()['c']
    correct = conn.execute("SELECT COUNT(*) as c FROM predictions WHERE is_correct = 1").fetchone()['c']
    wrong = conn.execute("SELECT COUNT(*) as c FROM predictions WHERE is_correct = 0").fetchone()['c']
    pending = conn.execute("SELECT COUNT(*) as c FROM predictions WHERE is_correct IS NULL").fetchone()['c']
    conn.close()

    accuracy = round(correct / (correct + wrong) * 100, 1) if (correct + wrong) > 0 else 0

    return {
        'total': total,
        'correct': correct,
        'wrong': wrong,
        'pending': pending,
        'accuracy': accuracy,
    }


@app.put("/api/history/{prediction_id}/result")
async def update_prediction_result(prediction_id: int, body: dict = None):
    conn = get_db()
    pred = conn.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,)).fetchone()
    if not pred:
        conn.close()
        raise HTTPException(404, 'Prediction not found')

    actual_result = body.get('actual_result') if body else None
    valid = ('home', 'draw', 'away')
    if actual_result not in valid:
        conn.close()
        raise HTTPException(400, f'Invalid result. Must be one of: {", ".join(valid)}')

    is_correct = 1 if pred['predicted_winner'] == actual_result else 0
    conn.execute(
        "UPDATE predictions SET is_correct = ?, actual_result = ? WHERE id = ?",
        (is_correct, actual_result, prediction_id)
    )
    conn.commit()
    conn.close()

    return {'id': prediction_id, 'is_correct': bool(is_correct), 'actual_result': actual_result}


@app.delete("/api/history/{prediction_id}")
async def delete_prediction(prediction_id: int):
    conn = get_db()
    conn.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    conn.commit()
    conn.close()
    return {'deleted': True}
