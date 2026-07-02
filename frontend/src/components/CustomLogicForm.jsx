import { useState, useEffect } from 'react';
import { getCustomRules, createCustomRule, deleteCustomRule } from '../api';

const FIELDS = [
  { value: 'odds_home', label: 'Odds Home' },
  { value: 'odds_draw', label: 'Odds Draw' },
  { value: 'odds_away', label: 'Odds Away' },
  { value: 'form_home', label: 'Form Home (0-100)' },
  { value: 'form_away', label: 'Form Away (0-100)' },
  { value: 'position_home', label: 'Position Home' },
  { value: 'position_away', label: 'Position Away' },
];

const OPERATORS = [
  { value: '<', label: '<' },
  { value: '>', label: '>' },
  { value: '=', label: '=' },
  { value: '>=', label: '>=' },
  { value: '<=', label: '<=' },
];

const RECOMMENDATIONS = [
  { value: 'home', label: 'Home Win' },
  { value: 'draw', label: 'Draw' },
  { value: 'away', label: 'Away Win' },
];

export default function CustomLogicForm() {
  const [rules, setRules] = useState([]);
  const [field, setField] = useState('odds_home');
  const [op, setOp] = useState('<');
  const [val, setVal] = useState('2.0');
  const [rec, setRec] = useState('home');
  const [weight, setWeight] = useState('10');

  useEffect(() => {
    getCustomRules().then(d => setRules(d.rules || []));
  }, []);

  const handleAdd = async () => {
    await createCustomRule({
      condition_field: field,
      operator: op,
      condition_value: parseFloat(val),
      result_recommendation: rec,
      weight_modifier: parseFloat(weight),
    });
    const d = await getCustomRules();
    setRules(d.rules || []);
  };

  const handleDelete = async (id) => {
    await deleteCustomRule(id);
    setRules(rules.filter(r => r.id !== id));
  };

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h3 className="font-bold text-lg mb-3">My Custom Logic</h3>

      <div className="grid grid-cols-5 gap-2 mb-3">
        <select className="border rounded px-2 py-1 text-sm" value={field} onChange={e => setField(e.target.value)}>
          {FIELDS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
        </select>
        <select className="border rounded px-2 py-1 text-sm" value={op} onChange={e => setOp(e.target.value)}>
          {OPERATORS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <input className="border rounded px-2 py-1 text-sm" value={val} onChange={e => setVal(e.target.value)} />
        <select className="border rounded px-2 py-1 text-sm" value={rec} onChange={e => setRec(e.target.value)}>
          {RECOMMENDATIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
        <input className="border rounded px-2 py-1 text-sm" value={weight} onChange={e => setWeight(e.target.value)} placeholder="Weight +-" />
      </div>

      <button onClick={handleAdd} className="bg-green-700 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-green-800">
        + Add Rule
      </button>

      {rules.length > 0 && (
        <ul className="mt-3 space-y-1">
          {rules.map(r => (
            <li key={r.id} className="flex justify-between items-center bg-gray-50 px-3 py-1.5 rounded text-sm">
              <span>
                IF <strong>{r.condition_field}</strong> {r.operator} {r.condition_value}
                &rarr; <strong className="text-green-700">{r.result_recommendation}</strong> ({r.weight_modifier > 0 ? '+' : ''}{r.weight_modifier}%)
              </span>
              <button onClick={() => handleDelete(r.id)} className="text-red-500 hover:text-red-700 text-xs">&times;</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
