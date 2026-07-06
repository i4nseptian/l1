import PredictionBadge from './PredictionBadge';

function FormDots({ form }) {
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

export default function MatchCard({ match, prediction }) {
  const pred = prediction || match?.prediction || null;
  const stats = pred?.team_stats || {};
  const homeForm = stats.home?.form || match?.home_form || '';
  const awayForm = stats.away?.form || match?.away_form || '';
  const analysis = pred?.analysis || [];
  const isLive = match.status === 'live' || match.status === 'in_play';
  const isFinished = match.status === 'finished' || match.status === 'FINISHED';

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-4 sm:p-5 border border-gray-100 hover:border-green-200 hover:-translate-y-1 cursor-pointer">
      <div className="flex justify-between items-center mb-3">
        <span className="text-[11px] sm:text-xs font-medium text-gray-400">
          {match.match_time
            ? new Date(match.match_time).toLocaleDateString('id-ID', { weekday: 'short', month: 'short', day: 'numeric' }) + ' ' +
              new Date(match.match_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : 'Today'}
        </span>
        <span className={`text-[9px] sm:text-xs font-bold px-2 py-0.5 sm:px-3 sm:py-1 rounded-full ${
          isLive ? 'bg-red-50 text-red-600 animate-pulse' :
          isFinished ? 'bg-green-50 text-green-600' :
          'bg-blue-50 text-blue-600'
        }`}>
          {isLive ? 'LIVE' : isFinished ? 'FT' : 'Upcoming'}
        </span>
      </div>

      <div className="flex justify-between items-center mb-3">
        <div className="flex-1 text-right font-bold text-sm sm:text-base text-gray-900 truncate pr-2">{match.home_team}</div>
        <div className="text-center px-2 sm:px-3 flex-shrink-0">
          <div className="text-sm sm:text-lg font-black text-gray-400">
            {match.home_score !== null ? `${match.home_score} - ${match.away_score}` : 'VS'}
          </div>
        </div>
        <div className="flex-1 text-left font-bold text-sm sm:text-base text-gray-900 truncate pl-2">{match.away_team}</div>
      </div>

      {(homeForm || awayForm) && (
        <div className="flex items-center justify-center gap-2 sm:gap-3 mb-3">
          <FormDots form={homeForm} />
          <span className="text-[9px] text-gray-400 font-medium">form</span>
          <FormDots form={awayForm} />
        </div>
      )}

      <div className="bg-gradient-to-r from-gray-50 via-white to-gray-50 rounded-xl p-2.5 sm:p-3 mb-3">
        <div className="grid grid-cols-3 gap-1 sm:gap-2 text-center">
          <div>
            <div className="text-[9px] sm:text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">1</div>
            <div className="text-xs sm:text-sm font-bold text-gray-800">{match.odds_home?.toFixed(2) || '-'}</div>
          </div>
          <div className="border-x border-gray-200">
            <div className="text-[9px] sm:text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">X</div>
            <div className="text-xs sm:text-sm font-bold text-gray-800">{match.odds_draw?.toFixed(2) || '-'}</div>
          </div>
          <div>
            <div className="text-[9px] sm:text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">2</div>
            <div className="text-xs sm:text-sm font-bold text-gray-800">{match.odds_away?.toFixed(2) || '-'}</div>
          </div>
        </div>
      </div>

      {pred && (
        <div className="flex justify-center mb-2">
          <PredictionBadge winner={pred.winner} confidence={pred.confidence} size="sm" />
        </div>
      )}

      {pred && analysis.length > 0 && (
        <div className="bg-gradient-to-r from-gray-50 to-green-50/50 rounded-lg px-2.5 py-2 sm:py-2.5">
          <div className="text-[9px] font-bold text-gray-400 uppercase tracking-wider mb-1">Analisis</div>
          {analysis.slice(0, 3).map((line, i) => (
            <div key={i} className="text-[10px] text-gray-600 leading-tight mb-0.5 flex items-start gap-1">
              <span className="text-green-600 mt-0.5 flex-shrink-0">•</span>
              <span>{line}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
