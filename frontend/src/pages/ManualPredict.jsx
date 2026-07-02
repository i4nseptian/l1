import { useState, useEffect } from 'react';
import { manualPredict, getTeams } from '../api';
import TeamBadge, { TeamSelect } from '../components/TeamBadge';

const FALLBACK_TEAMS = [
  'Manchester City', 'Arsenal', 'Liverpool', 'Aston Villa', 'Tottenham',
  'Manchester United', 'Chelsea', 'Newcastle', 'Real Madrid', 'Barcelona',
  'Atletico Madrid', 'Inter Milan', 'AC Milan', 'Juventus', 'Napoli',
  'Bayern Munich', 'Borussia Dortmund', 'PSG',
];

const FORM_OPTIONS = [
  'WWWWW', 'WWWWL', 'WWWLD', 'WWLWW', 'WWLWD',
  'WLWWW', 'WLWLD', 'WLWDL', 'WLLWW',
  'LWWWW', 'LWWLW', 'LWWDW', 'LDDWD',
];

function ValueBadge({ label, size = 'sm' }) {
  const map = {
    excellent: { bg: 'bg-green-100', text: 'text-green-800', dot: 'bg-green-500', label: 'Excellent' },
    good: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500', label: 'Good Value' },
    fair: { bg: 'bg-gray-50', text: 'text-gray-500', dot: 'bg-gray-400', label: 'Fair' },
    poor: { bg: 'bg-red-50', text: 'text-red-600', dot: 'bg-red-500', label: 'Poor' },
  };
  const v = map[label] || map.fair;
  const s = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-bold ${s} ${v.bg} ${v.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${v.dot}`} />
      {v.label}
    </span>
  );
}

function ConfidenceGauge({ pct }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  const color = pct >= 80 ? '#16a34a' : pct >= 60 ? '#d97706' : '#9ca3af';
  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      <svg className="transform -rotate-90 w-24 h-24" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r={r} fill="none" stroke="#e5e7eb" strokeWidth="6" />
        <circle cx="40" cy="40" r={r} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-2xl font-black" style={{ color }}>{pct.toFixed(0)}%</span>
        <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider">confidence</span>
      </div>
    </div>
  );
}

export default function ManualPredict() {
  const [teamList, setTeamList] = useState(FALLBACK_TEAMS);
  const [teamsLoading, setTeamsLoading] = useState(true);
  const [home, setHome] = useState('Manchester City');
  const [away, setAway] = useState('Arsenal');
  const [formHome, setFormHome] = useState('WWWDW');
  const [formAway, setFormAway] = useState('WWLWW');
  const [oddsHome, setOddsHome] = useState('1.85');
  const [oddsDraw, setOddsDraw] = useState('3.60');
  const [oddsAway, setOddsAway] = useState('4.20');
  const [posHome, setPosHome] = useState('1');
  const [posAway, setPosAway] = useState('3');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    getTeams().then(data => {
      if (data?.teams?.length > 10) {
        setTeamList([...new Set(data.teams.map(t => t.name))].sort());
      }
      setTeamsLoading(false);
    }).catch(() => setTeamsLoading(false));
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    setActiveCategory('all');
    setSearchQuery('');
    setShowAll(false);
    try {
      const res = await manualPredict({
        home_team: home, away_team: away,
        form_home: formHome, form_away: formAway,
        odds_home: parseFloat(oddsHome), odds_draw: parseFloat(oddsDraw), odds_away: parseFloat(oddsAway),
        position_home: parseInt(posHome) || null, position_away: parseInt(posAway) || null,
      });
      setResult(res);
    } catch {
      setError('Gagal dapat prediksi. Pastikan backend jalan.');
    }
    setLoading(false);
  };

  const markets = result?.all_markets?.markets || [];
  const expectedGoals = result?.all_markets?.expected_goals || null;
  const categories = ['all', ...new Set(markets.map(m => m.category))];

  const filtered = markets.filter(m => {
    if (activeCategory !== 'all' && m.category !== activeCategory) return false;
    if (searchQuery && !m.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const valueCounts = { excellent: 0, good: 0, fair: 0, poor: 0 };
  for (const m of markets) {
    const best = Math.max(...m.outcomes.map(o => o.value || 0));
    if (best > 5) valueCounts.excellent++;
    else if (best > 2) valueCounts.good++;
    else if (best > -2) valueCounts.fair++;
    else valueCounts.poor++;
  }

  const topBets = markets
    .map(m => ({ ...m, bestValue: Math.max(...m.outcomes.map(o => o.value || 0)) }))
    .filter(m => m.bestValue > 2)
    .sort((a, b) => b.bestValue - a.bestValue)
    .slice(0, 3);

  const displayMarkets = showAll ? filtered : filtered.slice(0, 6);

  const totalValue = markets.reduce((sum, m) => sum + Math.max(...m.outcomes.map(o => o.value || 0)), 0);
  const avgValue = markets.length ? (totalValue / markets.length).toFixed(1) : 0;

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-gray-900">Manual Predict</h1>
        <p className="text-gray-500 text-sm mt-1">
          Pilih tim, input odds & form — dapatkan prediksi lengkap + rating value untuk semua market taruhan
        </p>
      </div>

      {teamsLoading && (
        <div className="mb-3 flex items-center gap-2 text-xs text-gray-400 bg-gray-50 rounded-xl px-4 py-2">
          <div className="w-3 h-3 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
          Memuat data tim...
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* LEFT: Form */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Pilih Tim</span>
            <span className="text-[10px] text-gray-400">{teamList.length} tim tersedia</span>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-5">
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Home</label>
              <TeamSelect value={home} onChange={setHome} options={teamList} />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Away</label>
              <TeamSelect value={away} onChange={setAway} options={teamList} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-5">
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Form Home</label>
              <select className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={formHome} onChange={e => setFormHome(e.target.value)}>
                {FORM_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Form Away</label>
              <select className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={formAway} onChange={e => setFormAway(e.target.value)}>
                {FORM_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3 mb-5">
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Odds 1</label>
              <input className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm font-bold bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={oddsHome} onChange={e => setOddsHome(e.target.value)} type="number" step="0.01" />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Odds X</label>
              <input className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm font-bold bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={oddsDraw} onChange={e => setOddsDraw(e.target.value)} type="number" step="0.01" />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Odds 2</label>
              <input className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm font-bold bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={oddsAway} onChange={e => setOddsAway(e.target.value)} type="number" step="0.01" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Posisi Home</label>
              <input className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={posHome} onChange={e => setPosHome(e.target.value)} type="number" />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1.5 block">Posisi Away</label>
              <input className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                value={posAway} onChange={e => setPosAway(e.target.value)} type="number" />
            </div>
          </div>
          <button onClick={handlePredict} disabled={loading || home === away}
            className="w-full bg-gradient-to-r from-green-700 to-emerald-600 text-white py-3.5 rounded-xl font-bold text-sm hover:from-green-800 hover:to-emerald-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            {loading ? (
              <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Memprediksi...</>
            ) : '🔮 Dapatkan Prediksi'}
          </button>
          {error && <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm font-medium">{error}</div>}
          {home === away && <div className="mt-3 text-xs text-amber-600 font-medium">Tim Home dan Away harus berbeda!</div>}
        </div>

        {/* RIGHT: Result */}
        <div>
          {result ? (
            <div className="space-y-4">
              {/* ===== PREDICTION HEADER ===== */}
              <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl shadow-2xl p-6 text-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex flex-col items-center flex-1">
                    <TeamBadge name={result.home_team} size="xl" />
                    <div className="text-xs font-bold text-white/70 mt-1.5">{result.home_team}</div>
                  </div>
                  <div className="flex flex-col items-center px-4">
                    <div className="text-xl font-black text-white/20 mb-2">VS</div>
                    <ConfidenceGauge pct={result.confidence} />
                    <div className={`mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold shadow-lg ${
                      result.winner === 'home' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                      result.winner === 'away' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                    }`}>
                      <span>{result.winner === 'home' ? '🏠' : result.winner === 'away' ? '✈️' : '⚖️'}</span>
                      <span>{result.winner === 'home' ? 'HOME WIN' : result.winner === 'away' ? 'AWAY WIN' : 'DRAW'}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-center flex-1">
                    <TeamBadge name={result.away_team} size="xl" />
                    <div className="text-xs font-bold text-white/70 mt-1.5">{result.away_team}</div>
                  </div>
                </div>

                {/* Score bars */}
                <div className="flex gap-3 mt-2">
                  {[
                    { label: 'Home', value: result.scores?.home, pct: result.scores?.home / Math.max(result.scores?.home + result.scores?.draw + result.scores?.away, 1) * 100, color: 'from-green-500 to-emerald-400' },
                    { label: 'Draw', value: result.scores?.draw, pct: result.scores?.draw / Math.max(result.scores?.home + result.scores?.draw + result.scores?.away, 1) * 100, color: 'from-yellow-500 to-amber-400' },
                    { label: 'Away', value: result.scores?.away, pct: result.scores?.away / Math.max(result.scores?.home + result.scores?.draw + result.scores?.away, 1) * 100, color: 'from-blue-500 to-indigo-400' },
                  ].map(s => (
                    <div key={s.label} className="flex-1 text-center">
                      <div className="text-[10px] text-white/40 font-bold uppercase tracking-wider mb-1.5">{s.label}</div>
                      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-1.5">
                        <div className={`h-full rounded-full bg-gradient-to-r ${s.color}`} style={{ width: `${s.pct}%` }} />
                      </div>
                      <div className="text-xl font-black text-white">{s.value?.toFixed(1)}</div>
                    </div>
                  ))}
                </div>

                {expectedGoals && (
                  <div className="mt-3 flex items-center justify-center gap-4 text-xs bg-white/5 rounded-xl py-2.5 px-4">
                    <span className="text-green-300 font-bold">{result.home_team}: {expectedGoals.home}</span>
                    <span className="text-white/20">|</span>
                    <span className="text-white font-bold">xG {expectedGoals.total}</span>
                    <span className="text-white/20">|</span>
                    <span className="text-blue-300 font-bold">{result.away_team}: {expectedGoals.away}</span>
                  </div>
                )}
              </div>

              {/* ===== VALUE SUMMARY BAR ===== */}
              {markets.length > 0 && (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-4">
                  <div className="flex items-center gap-4 flex-wrap">
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Value Overview</span>
                    <div className="flex gap-2 flex-wrap flex-1">
                      {Object.entries(valueCounts).map(([k, v]) => (
                        <span key={k} className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                          k === 'excellent' ? 'bg-green-100 text-green-800' :
                          k === 'good' ? 'bg-emerald-50 text-emerald-700' :
                          k === 'fair' ? 'bg-gray-50 text-gray-500' :
                          'bg-red-50 text-red-600'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            k === 'excellent' ? 'bg-green-500' :
                            k === 'good' ? 'bg-emerald-500' :
                            k === 'fair' ? 'bg-gray-400' :
                            'bg-red-500'
                          }`} />
                          {v} {k}
                        </span>
                      ))}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-black text-gray-900">{avgValue}%</div>
                      <div className="text-[10px] text-gray-400 font-medium">avg value</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-black text-gray-900">{markets.length}</div>
                      <div className="text-[10px] text-gray-400 font-medium">markets</div>
                    </div>
                  </div>
                </div>
              )}

              {/* ===== TOP BETS ===== */}
              {topBets.length > 0 && (
                <div className="bg-gradient-to-r from-green-600 to-emerald-500 rounded-2xl shadow-lg p-5 text-white">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">🏆</span>
                    <h3 className="font-extrabold text-sm uppercase tracking-wider">Top Recommended Bets</h3>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {topBets.map((m, i) => {
                      const best = m.outcomes.reduce((a, b) => (a.value || 0) > (b.value || 0) ? a : b);
                      return (
                        <div key={i} className="bg-white/10 rounded-xl p-3 text-center backdrop-blur-sm border border-white/10">
                          <div className="text-[10px] text-emerald-200 font-bold mb-1">{m.name}</div>
                          <div className="text-lg font-black">{best.label}</div>
                          <div className="flex items-center justify-center gap-2 mt-1">
                            <span className="text-sm font-bold">@{best.odds}</span>
                            <span className="text-[10px] bg-white/20 rounded px-1.5 py-0.5 font-bold">+{best.value}% EV</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* ===== CATEGORY FILTERS ===== */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-4">
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {categories.map(cat => (
                    <button key={cat} onClick={() => setActiveCategory(cat)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        activeCategory === cat
                          ? 'bg-green-700 text-white shadow-md'
                          : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                      }`}>
                      {cat === 'all' ? `All (${markets.length})` : cat}
                    </button>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input className="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm bg-gray-50 focus:ring-2 focus:ring-green-500 outline-none"
                    placeholder="🔍 Cari market..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
                  <select className="border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none"
                    value={showAll ? 'all' : 'top'} onChange={e => setShowAll(e.target.value === 'all')}>
                    <option value="top">Top 6</option>
                    <option value="all">Show all</option>
                  </select>
                </div>
              </div>

              {/* ===== MARKET CARDS ===== */}
              {displayMarkets.length === 0 ? (
                <div className="bg-white rounded-2xl shadow border border-gray-100 p-8 text-center">
                  <span className="text-4xl block mb-2">🔍</span>
                  <p className="text-gray-400 text-sm font-medium">No markets match filter</p>
                </div>
              ) : (
                displayMarkets.map((market, idx) => {
                  const bestValue = Math.max(...market.outcomes.map(o => o.value || 0));
                  const bestOutcome = market.outcomes.reduce((a, b) => (a.value || 0) > (b.value || 0) ? a : b);
                  const isHot = bestValue > 5;
                  const isGood = bestValue > 2;
                  return (
                    <div key={idx} className={`bg-white rounded-2xl shadow-lg border overflow-hidden ${
                      isHot ? 'border-green-300 ring-2 ring-green-100' :
                      isGood ? 'border-emerald-200' :
                      'border-gray-100'
                    }`}>
                      {/* Market header */}
                      <div className={`flex items-center justify-between px-5 py-3 border-b ${
                        isHot ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-100' :
                        'bg-gray-50 border-gray-100'
                      }`}>
                        <div className="flex items-center gap-2.5">
                          {isHot && <span className="text-lg">🔥</span>}
                          <div>
                            <h3 className="font-bold text-gray-900 text-sm">{market.name}</h3>
                            <span className="text-[10px] text-gray-400">Type {market.type_id} · {market.category}</span>
                          </div>
                        </div>
                        {isGood && (
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-green-700 bg-green-100 px-2.5 py-1 rounded-full">
                              Best: {bestOutcome.label} @{bestOutcome.odds}
                            </span>
                            {isHot && <span className="text-xs font-bold text-white bg-green-600 px-2 py-1 rounded-full">HOT</span>}
                          </div>
                        )}
                      </div>
                      {/* Outcomes grid */}
                      <div className="px-5 py-3">
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                          {market.outcomes.map((outcome, oi) => {
                            const vl = outcome.value_label || 'fair';
                            const isPos = vl === 'excellent' || vl === 'good';
                            return (
                              <div key={oi} className={`rounded-xl p-3 border transition-all ${
                                isPos ? 'bg-green-50 border-green-200 shadow-sm' :
                                vl === 'poor' ? 'bg-red-50 border-red-100' :
                                'bg-gray-50 border-gray-100'
                              }`}>
                                <div className="flex items-center justify-between mb-1.5">
                                  <span className="text-xs font-bold text-gray-700">{outcome.label}</span>
                                  <span className={`text-xs font-bold ${
                                    isPos ? 'text-green-600' : vl === 'poor' ? 'text-red-400' : 'text-gray-400'
                                  }`}>
                                    {outcome.value > 0 ? '+' : ''}{outcome.value}%
                                  </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <span className="text-lg font-black text-gray-900">{outcome.odds}</span>
                                  <span className="text-[10px] text-gray-400 font-medium">{outcome.prob}%</span>
                                </div>
                                {isPos && <ValueBadge label={vl} size="sm" />}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}

              {/* Show more / less */}
              {filtered.length > 6 && (
                <button onClick={() => setShowAll(!showAll)}
                  className="w-full py-3 text-sm font-bold text-green-700 bg-white rounded-2xl shadow-sm border border-gray-100 hover:bg-green-50 transition-all">
                  {showAll ? `▲ Show less` : `▼ Show all ${filtered.length} markets`}
                </button>
              )}

              {/* ===== FACTOR ANALYSIS ===== */}
              {result.breakdown && (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Factor Analysis</span>
                  </div>
                  <div className="space-y-3">
                    {Object.entries(result.breakdown).map(([key, val]) => (
                      <div key={key}>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs text-gray-600 capitalize font-medium">{key.replace(/_/g, ' ')}</span>
                          <span className="text-xs font-bold text-gray-800">{val.toFixed(1)}</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className="h-full rounded-full bg-gradient-to-r from-green-500 to-emerald-400 transition-all"
                            style={{ width: `${val}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white/50 rounded-2xl border-2 border-dashed border-gray-200 p-12 text-center h-full flex flex-col items-center justify-center">
              <span className="text-6xl mb-4">📊</span>
              <h3 className="text-lg font-bold text-gray-400 mb-2">Belum Ada Hasil</h3>
              <p className="text-sm text-gray-400 max-w-xs">
                Pilih tim dan masukkan data di sebelah kiri, lalu klik tombol prediksi untuk melihat hasil lengkap semua market.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
