import { TeamBadgeSmall } from './TeamBadge';
import PredictionBadge from './PredictionBadge';

export default function MatchCard({ match, prediction }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-5 border border-gray-100 hover:border-green-200 hover:-translate-y-1 cursor-pointer">
      <div className="flex justify-between items-center mb-4">
        <span className="text-xs font-medium text-gray-400">
          {match.match_time
            ? new Date(match.match_time).toLocaleDateString('id-ID', { weekday: 'short', month: 'short', day: 'numeric' }) + ' ' +
              new Date(match.match_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : 'Today'}
        </span>
        {match.status === 'live' ? (
          <span className="flex items-center gap-1.5 text-xs bg-red-50 text-red-600 px-3 py-1 rounded-full font-bold">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            LIVE
          </span>
        ) : (
          <span className="text-xs bg-gray-100 text-gray-500 px-3 py-1 rounded-full font-medium">Upcoming</span>
        )}
      </div>

      <div className="flex justify-between items-center mb-4">
        <TeamBadgeSmall name={match.home_team} />
        <div className="text-center px-2">
          <div className="text-lg font-black text-gray-400">VS</div>
          {match.status === 'live' && (
            <div className="text-2xl font-extrabold text-gray-900">
              {match.home_score ?? '-'}:{match.away_score ?? '-'}
            </div>
          )}
        </div>
        <TeamBadgeSmall name={match.away_team} />
      </div>

      <div className="bg-gradient-to-r from-gray-50 via-white to-gray-50 rounded-xl p-3 mb-3">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">1</div>
            <div className="text-sm font-bold text-gray-800">{match.odds_home?.toFixed(2) || '-'}</div>
          </div>
          <div className="border-x border-gray-200">
            <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">X</div>
            <div className="text-sm font-bold text-gray-800">{match.odds_draw?.toFixed(2) || '-'}</div>
          </div>
          <div>
            <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">2</div>
            <div className="text-sm font-bold text-gray-800">{match.odds_away?.toFixed(2) || '-'}</div>
          </div>
        </div>
      </div>

      {prediction && (
        <div className="flex justify-center">
          <PredictionBadge winner={prediction.winner} confidence={prediction.confidence} />
        </div>
      )}
    </div>
  );
}
