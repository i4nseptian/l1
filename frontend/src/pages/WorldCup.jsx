import { useState, useEffect } from 'react';

const FLAGS = {
  'Algeria': 'dz', 'Argentina': 'ar', 'Australia': 'au', 'Austria': 'at',
  'Belgium': 'be', 'Brazil': 'br', 'Canada': 'ca', 'Cape Verde Islands': 'cv',
  'Colombia': 'co', 'Congo DR': 'cd', 'Croatia': 'hr', 'Curacao': 'cw',
  'Czechia': 'cz', 'Ecuador': 'ec', 'Egypt': 'eg', 'England': 'gb-eng',
  'France': 'fr', 'Germany': 'de', 'Haiti': 'ht', 'Iran': 'ir',
  'Iraq': 'iq', 'Ivory Coast': 'ci', 'Japan': 'jp', 'Jordan': 'jo',
  'Mexico': 'mx', 'Morocco': 'ma', 'Netherlands': 'nl', 'New Zealand': 'nz',
  'Norway': 'no', 'Paraguay': 'py', 'Portugal': 'pt', 'Qatar': 'qa',
  'Saudi Arabia': 'sa', 'Scotland': 'gb-sct', 'Senegal': 'sn',
  'South Africa': 'za', 'South Korea': 'kr', 'Spain': 'es', 'Sweden': 'se',
  'Switzerland': 'ch', 'Tunisia': 'tn', 'Turkey': 'tr',
  'United States': 'us', 'Uruguay': 'uy', 'Uzbekistan': 'uz',
  'Bosnia-Herzegovina': 'ba',
};

function Flag({ name, size = 20 }) {
  const code = FLAGS[name] || 'unknown';
  const [ok, setOk] = useState(true);
  if (!ok) return <span className="text-xs font-bold text-gray-400 w-5 h-5 flex items-center justify-center rounded-full bg-gray-100">{name?.[0] || '?'}</span>;
  return (
    <img src={`https://hatscripts.github.io/circle-flags/flags/${code}.svg`}
      alt={name} width={size} height={size}
      className="rounded-full inline-block flex-shrink-0 shadow-sm"
      onError={() => setOk(false)} />
  );
}

function FormDots({ form }) {
  return (
    <div className="flex gap-1">
      {(form || []).map((f, i) => (
        <span key={i} className={`w-3.5 h-3.5 rounded-full text-[7px] font-bold flex items-center justify-center ${
          f === 'M' || f === 'W' ? 'bg-emerald-500 text-white' :
          f === 'S' || f === 'D' ? 'bg-amber-400 text-white' :
          'bg-red-400 text-white'
        }`}>
          {f === 'M' || f === 'W' ? 'W' : f === 'S' || f === 'D' ? 'D' : 'L'}
        </span>
      ))}
    </div>
  );
}

function StatBar({ label, value, max = 100, color = 'bg-blue-500' }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-gray-500 w-24 text-right flex-shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
      <span className="font-bold text-gray-700 w-8 text-right">{value}</span>
    </div>
  );
}

function ConfGauge({ pct }) {
  const color = pct >= 70 ? 'text-emerald-600' : pct >= 50 ? 'text-amber-600' : 'text-gray-400';
  const bg = pct >= 70 ? 'bg-emerald-100 border-emerald-200' : pct >= 50 ? 'bg-amber-50 border-amber-200' : 'bg-gray-100 border-gray-200';
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${bg} ${color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${pct >= 70 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-gray-400'}`} />
      {pct.toFixed(0)}%
    </span>
  );
}

function TeamCard({ team, groupName }) {
  const [expanded, setExpanded] = useState(false);
  const s = team.stats || {};
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all">
      <button onClick={() => setExpanded(!expanded)} className="w-full text-left p-3.5 flex items-center gap-3 hover:bg-gray-50/50 transition-colors">
        <span className="flex items-center justify-center w-6 h-6 rounded-full text-[10px] font-extrabold bg-gradient-to-br from-gray-800 to-gray-700 text-white shadow-sm flex-shrink-0">
          {team.rank}
        </span>
        <Flag name={team.nama} size={22} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm text-gray-900 truncate">{team.nama}</span>
            <span className="text-[10px] font-bold text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded flex-shrink-0">{team.played}P</span>
            <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded flex-shrink-0">{team.points}pts</span>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <FormDots form={team.form} />
            <span className="text-[10px] text-gray-400">{team.won}W {team.drawn}D {team.lost}L</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-bold flex-shrink-0">
          <span className="text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">{team.goals_for}:{team.goals_against}</span>
          <span className={`w-1.5 h-1.5 rounded-full transition-transform duration-200 ${expanded ? 'rotate-90' : ''}`}>▶</span>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 pt-1 border-t border-gray-50 space-y-2.5">
          <StatBar label="Goals For" value={team.goals_for} max={15} color="bg-emerald-500" />
          <StatBar label="Goals Against" value={team.goals_against} max={15} color="bg-red-400" />
          <StatBar label="Clean Sheets" value={team.clean_sheets} max={5} color="bg-blue-500" />
          <StatBar label="Strength" value={team.strength} max={100} color="bg-violet-500" />
          <div className="flex items-center gap-2 text-xs text-gray-500 pt-1 border-t border-gray-50">
            <span className="font-medium">Form:</span>
            <FormDots form={team.form} />
          </div>
        </div>
      )}
    </div>
  );
}

function MatchRow({ match, idx }) {
  const isHome = match.status === 'M';
  const isDraw = match.status === 'S';
  const isLoss = match.status === 'K';
  const statusColor = isHome ? 'text-emerald-600 bg-emerald-50' : isDraw ? 'text-amber-600 bg-amber-50' : 'text-red-600 bg-red-50';
  const statusLabel = isHome ? 'W' : isDraw ? 'D' : 'L';

  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-gray-50 transition-colors">
      <div className="flex items-center gap-1.5 w-[30%] justify-end">
        <span className="text-xs font-semibold truncate text-right">{match.home_team}</span>
        <Flag name={match.home_team} size={14} />
      </div>
      <div className="flex items-center gap-1 flex-shrink-0">
        <span className="text-xs font-extrabold text-gray-900 min-w-[40px] text-center">{match.score}</span>
        <span className={`text-[9px] font-bold px-1 py-0.5 rounded ${statusColor}`}>{statusLabel}</span>
      </div>
      <div className="flex items-center gap-1.5 w-[30%]">
        <Flag name={match.away_team} size={14} />
        <span className="text-xs font-semibold truncate">{match.away_team}</span>
      </div>
      <div className="flex items-center gap-1 ml-auto">
        <span className="text-[9px] text-gray-400">{match.date}</span>
      </div>
    </div>
  );
}

function PredictionCard({ match }) {
  const isWin = match.status === 'M' || match.status === 'S' || match.status === 'K';
  if (!isWin) return null;

  const barH = match.home_prob || 33;
  const barD = match.draw_prob || 33;
  const barA = match.away_prob || 34;

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-xl p-3 shadow-lg text-white">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5 flex-1 min-w-0">
          <Flag name={match.home_team} size={16} />
          <span className="text-xs font-bold truncate">{match.home_team}</span>
        </div>
        <span className="text-[10px] text-white/40 mx-2">vs</span>
        <div className="flex items-center gap-1.5 flex-1 min-w-0 justify-end">
          <span className="text-xs font-bold truncate">{match.away_team}</span>
          <Flag name={match.away_team} size={16} />
        </div>
      </div>

      <div className="flex gap-0.5 h-5 rounded-full overflow-hidden mb-1.5">
        <div className="bg-emerald-500 h-full transition-all" style={{ width: `${barH}%` }} />
        <div className="bg-amber-400 h-full transition-all" style={{ width: `${barD}%` }} />
        <div className="bg-red-400 h-full transition-all" style={{ width: `${barA}%` }} />
      </div>

      <div className="flex justify-between text-[9px] text-white/60">
        <span>{match.home_team}: {barH}%</span>
        <span>Draw: {barD}%</span>
        <span>{match.away_team}: {barA}%</span>
      </div>

      <div className="mt-1.5 flex items-center justify-between border-t border-white/10 pt-1.5">
        <span className="text-[9px] text-white/40">{match.date}</span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
          match.predicted_winner === match.home_team ? 'bg-emerald-500/20 text-emerald-300' :
          match.predicted_winner === match.away_team ? 'bg-blue-500/20 text-blue-300' :
          'bg-amber-500/20 text-amber-300'
        }`}>
          {match.predicted_winner === match.home_team ? '🏠 ' : match.predicted_winner === match.away_team ? '✈️ ' : '⚖️ '}
          {match.predicted_winner}
        </span>
        <ConfGauge pct={match.confidence} />
      </div>
    </div>
  );
}

export default function WorldCup() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeGroup, setActiveGroup] = useState(null);
  const [tab, setTab] = useState('standings');
  const [fdStatus, setFdStatus] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch('/api/world-cup/predictions').then(r => r.json()),
      fetch('/api/football-data/status').then(r => r.json()).catch(() => ({ connected: false })),
    ]).then(([wc, fd]) => {
      setData(wc);
      setFdStatus(fd);
      const groups = Object.keys(wc);
      if (groups.length > 0) setActiveGroup(groups[0]);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex justify-center py-20">
      <div className="flex items-center gap-3 text-gray-400">
        <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-medium">Loading World Cup 2026...</span>
      </div>
    </div>
  );

  if (!data) return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-16 text-center">
      <span className="text-6xl block mb-4">🏆</span>
      <h2 className="text-xl font-bold text-gray-800 mb-2">Data Tidak Tersedia</h2>
      <p className="text-gray-500 text-sm">Pastikan backend berjalan dengan benar</p>
    </div>
  );

  const groups = Object.entries(data);
  const currentGroup = activeGroup ? data[activeGroup] : null;

  const allMatches = groups.flatMap(([g, d]) =>
    (d.predictions || []).map(m => ({ ...m, group: g }))
  );
  const wonMatches = allMatches.filter(m => m.status === 'M');
  const upcomingMatches = allMatches.filter(m => m.predicted_winner && m.status !== 'M' && m.status !== 'S' && m.status !== 'K');

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-br from-amber-600 via-yellow-500 to-orange-500 rounded-2xl p-6 sm:p-8 mb-5 text-white shadow-xl">
        <div className="flex items-center gap-4">
          <span className="text-5xl">🏆</span>
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">World Cup 2026</h1>
            <p className="text-amber-100 text-sm mt-1">
              {Object.keys(data).length} groups · {groups.reduce((a, [_, d]) => a + d.standings.length, 0)} teams · {allMatches.length} matches
              {fdStatus?.connected ? ' · football-data.org connected' : ''}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-5 overflow-x-auto pb-1">
        {[
          { key: 'standings', label: 'Standings', icon: '📊' },
          { key: 'predictions', label: `Predictions (${wonMatches.length})`, icon: '🔮' },
          { key: 'upcoming', label: `Upcoming (${upcomingMatches.length})`, icon: '📅' },
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-xl text-sm font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
              tab === t.key
                ? 'bg-gradient-to-r from-amber-600 to-yellow-500 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200 shadow-sm'
            }`}>
            <span>{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* ===== TAB: STANDINGS ===== */}
      {tab === 'standings' && (
        <div>
          {/* Group nav */}
          <div className="flex gap-1.5 mb-4 overflow-x-auto pb-1">
            {groups.map(([g]) => (
              <button key={g} onClick={() => setActiveGroup(g)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all ${
                  activeGroup === g
                    ? 'bg-amber-600 text-white shadow-md'
                    : 'bg-white text-gray-500 hover:bg-gray-100 border border-gray-200'
                }`}>
                {g}
              </button>
            ))}
          </div>

          {currentGroup && (
            <div className="space-y-5">
              {/* Group header */}
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-extrabold text-gray-900">{activeGroup}</h2>
                <span className="text-xs text-gray-400 bg-gray-100 px-2.5 py-1 rounded-full font-medium">
                  {currentGroup.standings.length} teams
                </span>
              </div>

              {/* Standings */}
              <div className="space-y-2">
                {currentGroup.standings.map((t, i) => (
                  <TeamCard key={t.nama} team={t} groupName={activeGroup} />
                ))}
              </div>

              {/* Match Predictions for this group */}
              {currentGroup.predictions && currentGroup.predictions.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <span>📋 Match Results</span>
                    <span className="text-[10px] font-normal text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                      {currentGroup.predictions.length} matches
                    </span>
                  </h3>
                  <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="divide-y divide-gray-50">
                      {currentGroup.predictions.map((m, i) => (
                        <MatchRow key={i} match={m} idx={i} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ===== TAB: PREDICTIONS ===== */}
      {tab === 'predictions' && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">All Match Predictions</span>
            <span className="text-[10px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{wonMatches.length} matches</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {wonMatches.map((m, i) => (
              <PredictionCard key={i} match={m} />
            ))}
          </div>
        </div>
      )}

      {/* ===== TAB: UPCOMING ===== */}
      {tab === 'upcoming' && (
        <div>
          {upcomingMatches.length === 0 ? (
            <div className="bg-white rounded-2xl p-16 text-center border border-gray-100 shadow-sm">
              <span className="text-6xl block mb-4">📅</span>
              <h3 className="text-lg font-bold text-gray-500 mb-1">No Upcoming Matches</h3>
              <p className="text-sm text-gray-400">All group stage matches have been completed</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {upcomingMatches.map((m, i) => (
                <PredictionCard key={i} match={m} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
