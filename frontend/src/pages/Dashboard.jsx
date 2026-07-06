import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMatches } from '../api';
import PredictionBadge from '../components/PredictionBadge';

const FLAGS = {
  'Argentina': 'ar', 'Brazil': 'br', 'England': 'gb-eng', 'France': 'fr',
  'Germany': 'de', 'Netherlands': 'nl', 'Portugal': 'pt', 'Spain': 'es',
  'Mexico': 'mx', 'Belgium': 'be', 'Japan': 'jp', 'South Korea': 'kr',
  'United States': 'us', 'Uruguay': 'uy', 'Croatia': 'hr', 'Colombia': 'co',
  'Switzerland': 'ch', 'Senegal': 'sn', 'Iran': 'ir', 'Morocco': 'ma',
  'Australia': 'au', 'Denmark': 'dk', 'Tunisia': 'tn', 'Canada': 'ca',
  'Cameroon': 'cm', 'Ghana': 'gh', 'Saudi Arabia': 'sa', 'Ecuador': 'ec',
  'Qatar': 'qa', 'Paraguay': 'py', 'Ivory Coast': 'ci', 'Sweden': 'se',
  'Norway': 'no', 'Turkey': 'tr', 'Czechia': 'cz', 'Austria': 'at',
  'Scotland': 'gb-sct', 'New Zealand': 'nz', 'South Africa': 'za',
  'Algeria': 'dz', 'Egypt': 'eg', 'Iraq': 'iq', 'Jordan': 'jo',
  'Cape Verde Islands': 'cv', 'Congo DR': 'cd', 'Haiti': 'ht',
  'Bosnia-Herzegovina': 'ba', 'Curacao': 'cw', 'Uzbekistan': 'uz',
  'Slovenia': 'si', 'Poland': 'pl',
};

function Flag({ name, size = 16 }) {
  const code = FLAGS[name] || '';
  const [ok, setOk] = useState(true);
  if (!code || !ok) return <span className="text-[9px] font-bold text-gray-400 w-4 h-4 flex items-center justify-center rounded-full bg-gray-100">{name?.[0] || '?'}</span>;
  return (
    <img src={`https://hatscripts.github.io/circle-flags/flags/${code}.svg`}
      alt={name} width={size} height={size} className="rounded-full flex-shrink-0 shadow-sm"
      onError={() => setOk(false)} />
  );
}

function FormDots({ form }) {
  return (
    <div className="flex gap-0.5">
      {(form || []).slice(0, 5).map((f, i) => (
        <span key={i} className={`w-2.5 h-2.5 rounded-full ${
          f === 'M' || f === 'W' ? 'bg-emerald-500' :
          f === 'S' || f === 'D' ? 'bg-amber-400' : 'bg-red-400'
        }`} />
      ))}
    </div>
  );
}

function WcStandings({ wcData }) {
  const groups = Object.entries(wcData || {});
  if (groups.length === 0) return null;
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-5 py-3.5 bg-gradient-to-r from-amber-600 to-yellow-500 text-white flex items-center gap-2">
        <span className="text-lg">🏆</span>
        <span className="font-bold text-sm">World Cup 2026 Standings</span>
        <span className="text-[10px] text-amber-200 ml-auto">{groups.length} groups</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4">
        {groups.slice(0, 6).map(([g, data]) => (
          <div key={g} className="bg-gray-50 rounded-xl overflow-hidden border border-gray-100">
            <div className="px-3 py-2 bg-gray-100/80 flex items-center justify-between">
              <span className="font-bold text-xs text-gray-700">{g}</span>
              <span className="text-[10px] text-gray-400">{data.standings.length} teams</span>
            </div>
            <div className="divide-y divide-gray-100/50">
              {data.standings.slice(0, 4).map((t, i) => (
                <div key={t.nama} className="flex items-center gap-2 px-3 py-2 hover:bg-white/50 transition-colors">
                  <span className={`w-4 h-4 rounded-full text-[8px] font-extrabold flex items-center justify-center flex-shrink-0 ${
                    t.rank <= 2 ? 'bg-emerald-500 text-white' : 'bg-gray-200 text-gray-500'
                  }`}>{t.rank}</span>
                  <Flag name={t.nama} size={14} />
                  <span className="flex-1 text-xs font-semibold text-gray-800 truncate">{t.nama}</span>
                  <FormDots form={t.form} />
                  <span className="text-[10px] font-bold text-gray-500 ml-1">{t.points}pts</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="px-5 py-2.5 border-t border-gray-50 text-center">
        <Link to="/world-cup" className="text-xs font-bold text-amber-600 hover:text-amber-700 transition-colors">
          View full standings & predictions →
        </Link>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [matches, setMatches] = useState([]);
  const [wcData, setWcData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getMatches('', '', true),
      fetch('/api/world-cup/predictions').then(r => r.json()).catch(() => null),
    ]).then(([m, wc]) => {
      setMatches(m.matches || []);
      setWcData(wc);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const liveMatches = matches.filter(m => m.status === 'live' || m.status === 'in_play');
  const upcomingMatches = matches.filter(m => m.status === 'scheduled' || m.status === 'TIMED' || m.status === 'SCHEDULED');
  const finishedMatches = matches.filter(m => m.status === 'finished' || m.status === 'FINISHED');

  return (
    <div>
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-green-900 to-emerald-800 rounded-2xl p-8 sm:p-10 mb-6 text-white shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-green-500/10 rounded-full translate-y-1/2 -translate-x-1/2" />
        <div className="relative z-10">
          <span className="text-5xl block mb-3">⚽</span>
          <h1 className="text-3xl sm:text-4xl font-extrabold mb-2 tracking-tight">PrediksiBola</h1>
          <p className="text-green-200 text-sm sm:text-base mb-6 max-w-xl">
            Prediksi pertandingan berbasis AI — analisis form, statistik tim, odds market, dan 583 faktor taruhan 1xBet.
          </p>
          <div className="flex flex-wrap gap-2.5">
            <Link to="/manual-predict" className="inline-flex items-center gap-1.5 bg-white text-green-900 px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-green-50 transition-all shadow-lg shadow-black/10">
              <span>🔮</span> Manual Predict
            </Link>
            <Link to="/world-cup" className="inline-flex items-center gap-1.5 bg-white/10 text-white px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-white/20 transition-all border border-white/20 backdrop-blur-sm">
              <span>🏆</span> World Cup 2026
            </Link>
            <Link to="/factors" className="inline-flex items-center gap-1.5 bg-white/10 text-white px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-white/20 transition-all border border-white/20 backdrop-blur-sm">
              <span>📋</span> Bet Markets
            </Link>
          </div>
        </div>
      </div>

      {/* World Cup Standings */}
      {wcData && <div className="mb-6"><WcStandings wcData={wcData} /></div>}

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        {[
          { icon: '🔮', title: 'Manual Predict', desc: 'Prediksi + odds semua market', link: '/manual-predict', color: 'from-emerald-600 to-green-700' },
          { icon: '📋', title: '583 Bet Markets', desc: 'Data faktor dari 1xBet', link: '/factors', color: 'from-blue-600 to-blue-700' },
          { icon: '🏆', title: 'World Cup 2026', desc: 'Standings, stats & prediksi', link: '/world-cup', color: 'from-amber-600 to-orange-600' },
        ].map(c => (
          <Link key={c.title} to={c.link} className={`bg-gradient-to-br ${c.color} rounded-xl p-4 text-white shadow-md hover:shadow-lg transition-all hover:-translate-y-0.5`}>
            <span className="text-2xl block mb-2">{c.icon}</span>
            <h3 className="font-bold text-sm mb-0.5">{c.title}</h3>
            <p className="text-[11px] opacity-80">{c.desc}</p>
          </Link>
        ))}
      </div>

      {/* Matches */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm">Loading matches...</span>
          </div>
        </div>
      ) : matches.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <span className="text-5xl block mb-3">📅</span>
          <p className="text-base font-medium text-gray-500 mb-1">Belum ada pertandingan</p>
          <p className="text-xs text-gray-400">Gunakan Manual Predict untuk coba prediksi sekarang</p>
          <Link to="/manual-predict" className="inline-flex items-center gap-1.5 mt-4 bg-green-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-green-800 transition-all shadow-md">
            <span>🔮</span> Coba Prediksi Manual
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {liveMatches.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-red-600 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" /> LIVE ({liveMatches.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 mb-5">
                {liveMatches.map(m => <MatchCard key={m.id} match={m} />)}
              </div>
            </div>
          )}

          {upcomingMatches.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-3">📅 Upcoming ({upcomingMatches.length})</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 mb-5">
                {upcomingMatches.map(m => <MatchCard key={m.id} match={m} />)}
              </div>
            </div>
          )}

          {finishedMatches.length > 0 && (
            <div>
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                ✅ Finished ({finishedMatches.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {finishedMatches.slice(-8).reverse().map(m => <MatchCard key={m.id} match={m} />)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function FormDotsSmall({ form }) {
  if (!form) return null;
  const arr = typeof form === 'string' ? form.split('') : (form || []);
  return (
    <div className="flex gap-0.5">
      {arr.slice(0, 5).map((f, i) => (
        <span key={i} className={`w-2 h-2 rounded-full ${
          f === 'M' || f === 'W' ? 'bg-emerald-500' :
          f === 'S' || f === 'D' ? 'bg-amber-400' : 'bg-red-400'
        }`} />
      ))}
    </div>
  );
}

function MatchCard({ match }) {
  const isLive = match.status === 'live' || match.status === 'in_play';
  const isFinished = match.status === 'finished' || match.status === 'FINISHED';
  const pred = match.prediction;
  const isUpcoming = !isLive && !isFinished;
  const stats = pred?.team_stats || {};
  const homeForm = stats.home?.form || match.home_form || '';
  const awayForm = stats.away?.form || match.away_form || '';
  const analysis = pred?.analysis || [];

  return (
    <Link
      to={`/match/${match.id}`}
      className={`bg-white rounded-xl shadow-sm border p-3.5 hover:shadow-md transition-all block ${
        isLive ? 'border-red-200 ring-1 ring-red-100' :
        isUpcoming && pred ? 'border-emerald-200 border-l-4 border-l-emerald-500' :
        'border-gray-100'
      }`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] text-gray-400">{match.match_time?.slice(0, 10) || 'TBD'}</span>
        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
          isLive ? 'bg-red-50 text-red-600 animate-pulse' :
          isFinished ? 'bg-green-50 text-green-600' :
          'bg-blue-50 text-blue-600'
        }`}>
          {isLive ? 'LIVE' : isFinished ? 'FT' : 'Upcoming'}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex-1 text-right font-bold text-sm text-gray-900 truncate pr-2">{match.home_team}</div>
        <div className="text-center px-2.5">
          {match.home_score !== null ? (
            <span className="text-base font-extrabold text-gray-900">{match.home_score} - {match.away_score}</span>
          ) : (
            <span className="text-[10px] font-bold text-gray-400">VS</span>
          )}
        </div>
        <div className="flex-1 text-left font-bold text-sm text-gray-900 truncate pl-2">{match.away_team}</div>
      </div>

      {/* Form dots */}
      {(homeForm || awayForm) && (
        <div className="flex items-center justify-center gap-3 mt-1.5">
          <FormDotsSmall form={homeForm} />
          <span className="text-[9px] text-gray-400 font-medium">form</span>
          <FormDotsSmall form={awayForm} />
        </div>
      )}

      {/* Prediction badge */}
      {pred && (
        <div className="mt-1.5 flex justify-center">
          <PredictionBadge winner={pred.winner} confidence={pred.confidence} size="sm" />
        </div>
      )}

      {/* Analysis */}
      {pred && analysis.length > 0 && (
        <div className="mt-2 bg-gradient-to-r from-gray-50 to-green-50/50 rounded-lg px-2.5 py-2">
          <div className="text-[9px] font-bold text-gray-400 uppercase tracking-wider mb-1">Analisis</div>
          {analysis.slice(0, 3).map((line, i) => (
            <div key={i} className="text-[10px] text-gray-600 leading-tight mb-0.5 flex items-start gap-1">
              <span className="text-green-600 mt-0.5">•</span>
              <span>{line}</span>
            </div>
          ))}
        </div>
      )}

      {/* Odds */}
      {match.odds_home && (
        <div className="flex justify-center gap-2.5 mt-1.5 text-[9px] text-gray-400 font-medium">
          <span>{match.odds_home.toFixed(2)}</span>
          <span className="text-gray-300">|</span>
          <span>{match.odds_draw?.toFixed(2)}</span>
          <span className="text-gray-300">|</span>
          <span>{match.odds_away?.toFixed(2)}</span>
        </div>
      )}
    </Link>
  );
}
