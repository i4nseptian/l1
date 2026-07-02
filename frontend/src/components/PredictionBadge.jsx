export default function PredictionBadge({ winner, confidence, size = 'md' }) {
  if (!winner) return null;

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  let config;

  if (confidence >= 80) {
    const colors = {
      home: 'bg-gradient-to-r from-green-600 to-green-500 text-white',
      away: 'bg-gradient-to-r from-red-600 to-red-500 text-white',
      draw: 'bg-gradient-to-r from-yellow-500 to-amber-400 text-white',
    };
    const labels = {
      home: '🏠 Home Win',
      away: '✈️ Away Win',
      draw: '⚖️ Draw',
    };
    config = { color: colors[winner] || colors.home, label: labels[winner] || labels.home };
  } else if (confidence >= 60) {
    const colors = {
      home: 'bg-gradient-to-r from-green-400 to-green-300 text-white',
      away: 'bg-gradient-to-r from-red-400 to-red-300 text-white',
      draw: 'bg-gradient-to-r from-yellow-400 to-amber-300 text-white',
    };
    const labels = {
      home: '⬆️ Lean Home',
      away: '⬇️ Lean Away',
      draw: '⇔ Lean Draw',
    };
    config = { color: colors[winner] || colors.home, label: labels[winner] || labels.home };
  } else {
    config = {
      color: 'bg-gradient-to-r from-gray-400 to-gray-300 text-white',
      label: '❓ No Clear Pick',
    };
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-bold shadow-sm ${sizes[size] || sizes.md} ${config.color}`}>
      <span>{config.label}</span>
      <span className="opacity-90 bg-white/20 rounded px-1.5">{confidence}%</span>
    </span>
  );
}
