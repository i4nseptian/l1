import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getMatch, getPrediction } from '../api';
import PredictionBadge from '../components/PredictionBadge';
import FormChart from '../components/FormChart';
import CustomLogicForm from '../components/CustomLogicForm';

export default function MatchDetail() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [tab, setTab] = useState('info');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getMatch(id),
      getPrediction(id),
    ]).then(([m, p]) => {
      setMatch(m);
      setPrediction(p);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!match) return <div className="text-center py-12 text-gray-500">Match not found</div>;

  const tabs = [
    { key: 'info', label: 'Info Tim' },
    { key: 'factors', label: 'Faktor Bet' },
    { key: 'prediction', label: 'Prediksi' },
    { key: 'logic', label: 'Logika Saya' },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-md p-6 mb-4">
        <div className="flex justify-between items-center mb-4">
          <div className="text-center flex-1">
            <div className="text-lg font-bold text-gray-900 mb-1">{match.home_team}</div>
            <div className="text-sm text-gray-500">Home</div>
          </div>
          <div className="text-center px-6">
            <div className="text-3xl font-extrabold text-gray-900">
              {match.home_score !== null ? `${match.home_score} - ${match.away_score}` : 'VS'}
            </div>
            {match.status === 'live' && (
              <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-semibold">LIVE</span>
            )}
          </div>
          <div className="text-center flex-1">
            <div className="text-lg font-bold text-gray-900 mb-1">{match.away_team}</div>
            <div className="text-sm text-gray-500">Away</div>
          </div>
        </div>

        {prediction && (
          <div className="flex justify-center">
            <PredictionBadge winner={prediction.winner} confidence={prediction.confidence} />
          </div>
        )}
      </div>

      <div className="flex gap-1 mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              tab === t.key ? 'bg-green-700 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        {tab === 'info' && (
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Form 5 Laga Terakhir</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{match.home_team}</p>
                  <FormChart form={match.form_home} team={match.home_team} />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{match.away_team}</p>
                  <FormChart form={match.form_away} team={match.away_team} />
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Odds 1X2</h3>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1">1 (Home)</div>
                  <div className="text-xl font-bold text-gray-900">{match.odds_home?.toFixed(2) || '-'}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1">X (Draw)</div>
                  <div className="text-xl font-bold text-gray-900">{match.odds_draw?.toFixed(2) || '-'}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1">2 (Away)</div>
                  <div className="text-xl font-bold text-gray-900">{match.odds_away?.toFixed(2) || '-'}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {tab === 'factors' && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Available Bet Factors (from 1xBet)</h3>
            <p className="text-sm text-gray-500 mb-4">Data faktor dari file Excel yang sudah diparse &mdash; menampilkan semua jenis pasar yang tersedia.</p>
            <FactorsList />
          </div>
        )}

        {tab === 'prediction' && prediction && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Prediction Breakdown</h3>
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-green-50 rounded-lg p-3 text-center border border-green-200">
                  <div className="text-xs text-gray-500">Home</div>
                  <div className="text-xl font-bold text-gray-900">{prediction.scores?.home?.toFixed(1)}</div>
                </div>
                <div className="bg-yellow-50 rounded-lg p-3 text-center border border-yellow-200">
                  <div className="text-xs text-gray-500">Draw</div>
                  <div className="text-xl font-bold text-gray-900">{prediction.scores?.draw?.toFixed(1)}</div>
                </div>
                <div className="bg-red-50 rounded-lg p-3 text-center border border-red-200">
                  <div className="text-xs text-gray-500">Away</div>
                  <div className="text-xl font-bold text-gray-900">{prediction.scores?.away?.toFixed(1)}</div>
                </div>
              </div>

              {prediction.breakdown && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Score Breakdown</h4>
                  {Object.entries(prediction.breakdown).map(([key, val]) => (
                    <div key={key} className="flex justify-between py-1 text-sm">
                      <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="font-medium">{val.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {tab === 'logic' && <CustomLogicForm />}
      </div>
    </div>
  );
}

function FactorsList() {
  const [factors, setFactors] = useState([]);

  useEffect(() => {
    fetch('/api/factors').then(r => r.json()).then(d => {
      setFactors(d.markets || []);
    });
  }, []);

  const groups = {};
  for (const f of factors) {
    const g = f.group || 'Unknown';
    if (!groups[g]) groups[g] = new Set();
    groups[g].add(f.market_name);
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {Object.entries(groups).sort().map(([group, markets]) => (
        <div key={group} className="bg-gray-50 rounded-lg p-3">
          <h4 className="font-semibold text-sm text-gray-900 mb-1">{group}</h4>
          <p className="text-xs text-gray-500">{[...markets].sort().join(', ')}</p>
        </div>
      ))}
    </div>
  );
}
