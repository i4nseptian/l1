from fastapi import APIRouter
import json
import os

router = APIRouter(prefix='/api')

FACTORS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'factors.json')

@router.get('/factors')
async def get_factors():
    if not os.path.exists(FACTORS_PATH):
        return {'error': 'Factors not parsed yet'}
    with open(FACTORS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


