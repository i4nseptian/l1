from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter(prefix='/api/custom-logic')

class LogicRule(BaseModel):
    condition_field: str
    operator: str
    condition_value: float
    logic_connector: str = 'AND'
    result_recommendation: str
    weight_modifier: float = 0
    priority: int = 0

@router.get('/')
async def get_rules():
    conn = get_db()
    rows = conn.execute("SELECT * FROM custom_logic WHERE is_active = 1 ORDER BY priority").fetchall()
    conn.close()
    return {'rules': [dict(r) for r in rows]}

@router.post('/')
async def create_rule(rule: LogicRule):
    conn = get_db()
    conn.execute(
        """INSERT INTO custom_logic 
        (condition_field, operator, condition_value, logic_connector, result_recommendation, weight_modifier, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (rule.condition_field, rule.operator, rule.condition_value, rule.logic_connector, rule.result_recommendation, rule.weight_modifier, rule.priority)
    )
    conn.commit()
    rule_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return {'id': rule_id, 'message': 'Rule created'}

@router.delete('/{rule_id}')
async def delete_rule(rule_id: int):
    conn = get_db()
    conn.execute("DELETE FROM custom_logic WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return {'message': 'Rule deleted'}
