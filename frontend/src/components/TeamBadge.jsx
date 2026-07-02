import { useState, useEffect, useRef } from 'react';

const TEAM_COLORS = {
  'Manchester City': { color: '#6CABDD', bg: '#EBF3FB' },
  'Arsenal': { color: '#EF0107', bg: '#FDE6E7' },
  'Liverpool': { color: '#C8102E', bg: '#F9E4E8' },
  'Aston Villa': { color: '#670E36', bg: '#EDE0E8' },
  'Tottenham': { color: '#132257', bg: '#E0E2EB' },
  'Manchester United': { color: '#DA291C', bg: '#FBE4E2' },
  'Chelsea': { color: '#034694', bg: '#E0E6F0' },
  'Newcastle': { color: '#241F20', bg: '#E3E3E3' },
  'Real Madrid': { color: '#FEBE10', bg: '#FFF8E0' },
  'Barcelona': { color: '#A50044', bg: '#F6E0EB' },
  'Girona': { color: '#CF1322', bg: '#F9E4E6' },
  'Atletico Madrid': { color: '#CB3524', bg: '#FAE6E3' },
  'Athletic Bilbao': { color: '#EE2230', bg: '#FDE4E6' },
  'Inter Milan': { color: '#010E80', bg: '#E0E1F0' },
  'AC Milan': { color: '#FB090B', bg: '#FEE4E4' },
  'Juventus': { color: '#000000', bg: '#E8E8E8' },
  'Napoli': { color: '#12A0D8', bg: '#E3F4FB' },
  'Roma': { color: '#8E1F2F', bg: '#F4E4E7' },
  'Bayern Munich': { color: '#DC052D', bg: '#FBE4E8' },
  'Borussia Dortmund': { color: '#FDE100', bg: '#FFFDE6' },
  'RB Leipzig': { color: '#DD0741', bg: '#FBE4EB' },
  'Bayer Leverkusen': { color: '#E32221', bg: '#FDE4E4' },
  'PSG': { color: '#004170', bg: '#E0EAF0' },
  'Monaco': { color: '#E63E32', bg: '#FDE8E6' },
  'Marseille': { color: '#2FAEE0', bg: '#E6F4FB' },
  'Lyon': { color: '#1D2C6B', bg: '#E2E4F0' },
  'Nice': { color: '#E81E2E', bg: '#FDE4E6' },
  'Lille': { color: '#C9252B', bg: '#F9E4E5' },
  'Team A': { color: '#6366F1', bg: '#EEF0FF' },
  'Team B': { color: '#EC4899', bg: '#FDE8F3' },
  'England': { color: '#0B479D', bg: '#E2EDFB' },
  'France': { color: '#002654', bg: '#E0E6F0' },
  'Brazil': { color: '#009739', bg: '#E0F4EA' },
  'Argentina': { color: '#75AADB', bg: '#EBF3FB' },
  'Germany': { color: '#DD0000', bg: '#FBE4E4' },
  'Italy': { color: '#009246', bg: '#E0F4EA' },
  'Spain': { color: '#AA151B', bg: '#F6E4E5' },
  'Netherlands': { color: '#FF6600', bg: '#FFF0E0' },
  'Portugal': { color: '#006600', bg: '#E0F0E0' },
  'Belgium': { color: '#E22726', bg: '#FDE4E4' },
};

const TEAM_FLAGS = {
  'Manchester City': 'gb-eng',
  'Arsenal': 'gb-eng',
  'Liverpool': 'gb-eng',
  'Aston Villa': 'gb-eng',
  'Tottenham': 'gb-eng',
  'Manchester United': 'gb-eng',
  'Chelsea': 'gb-eng',
  'Newcastle': 'gb-eng',
  'Real Madrid': 'es',
  'Barcelona': 'es',
  'Girona': 'es',
  'Atletico Madrid': 'es',
  'Athletic Bilbao': 'es',
  'Inter Milan': 'it',
  'AC Milan': 'it',
  'Juventus': 'it',
  'Napoli': 'it',
  'Roma': 'it',
  'Bayern Munich': 'de',
  'Borussia Dortmund': 'de',
  'RB Leipzig': 'de',
  'Bayer Leverkusen': 'de',
  'PSG': 'fr',
  'Monaco': 'fr',
  'Marseille': 'fr',
  'Lyon': 'fr',
  'Nice': 'fr',
  'Lille': 'fr',
  'England': 'gb-eng',
  'France': 'fr',
  'Brazil': 'br',
  'Argentina': 'ar',
  'Germany': 'de',
  'Italy': 'it',
  'Spain': 'es',
  'Netherlands': 'nl',
  'Portugal': 'pt',
  'Belgium': 'be',
  'Team A': 'gb-eng',
  'Team B': 'gb-eng',
};

function getInitials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

export default function TeamBadge({ name, size = 'md', showName = true }) {
  const colors = TEAM_COLORS[name] || { color: '#6B7280', bg: '#F3F4F6' };
  const flagCode = TEAM_FLAGS[name] || 'gb-eng';
  const [flagOk, setFlagOk] = useState(true);

  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-14 h-14 text-base',
    xl: 'w-20 h-20 text-xl',
  };

  return (
    <div className="flex items-center gap-3">
      <div
        className={`${sizes[size] || sizes.md} rounded-full flex items-center justify-center font-bold shadow-sm border-2 overflow-hidden relative`}
        style={{
          backgroundColor: colors.bg,
          borderColor: colors.color,
          color: colors.color,
        }}
      >
        {flagOk ? (
          <img
            src={`https://hatscripts.github.io/circle-flags/flags/${flagCode}.svg`}
            alt={flagCode}
            className="w-full h-full object-cover"
            onError={() => setFlagOk(false)}
          />
        ) : (
          getInitials(name)
        )}
      </div>
      {showName && (
        <div>
          <span className="font-semibold text-gray-900 text-sm block leading-tight">{name}</span>
        </div>
      )}
    </div>
  );
}

export function TeamBadgeSmall({ name }) {
  const colors = TEAM_COLORS[name] || { color: '#6B7280', bg: '#F3F4F6' };
  const flagCode = TEAM_FLAGS[name] || 'gb-eng';
  const [flagOk, setFlagOk] = useState(true);

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm shadow-sm border-2 overflow-hidden"
        style={{
          backgroundColor: colors.bg,
          borderColor: colors.color,
          color: colors.color,
        }}
      >
        {flagOk ? (
          <img
            src={`https://hatscripts.github.io/circle-flags/flags/${flagCode}.svg`}
            alt={flagCode}
            className="w-full h-full object-cover"
            onError={() => setFlagOk(false)}
          />
        ) : (
          getInitials(name)
        )}
      </div>
      <span className="text-xs font-medium text-gray-700 text-center leading-tight max-w-[80px] truncate">
        {name}
      </span>
    </div>
  );
}

export function TeamSelect({ value, onChange, options }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handle = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, []);

  const selected = options.find(o => o === value);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 outline-none hover:border-gray-300 transition-colors"
      >
        <TeamBadge name={value} size="sm" showName={false} />
        <span className="font-medium text-gray-900 flex-1 text-left">{value}</span>
        <span className={`text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}>▼</span>
      </button>
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-xl max-h-60 overflow-y-auto">
          {options.map(opt => (
            <button
              key={opt}
              type="button"
              onClick={() => { onChange(opt); setOpen(false); }}
              className={`w-full flex items-center gap-2 px-3 py-2.5 text-sm hover:bg-gray-50 transition-colors ${
                opt === value ? 'bg-green-50' : ''
              }`}
            >
              <TeamBadge name={opt} size="sm" showName={false} />
              <span className="font-medium text-gray-900">{opt}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export { TEAM_COLORS, TEAM_FLAGS };
