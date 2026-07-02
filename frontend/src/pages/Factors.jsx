import { useState, useEffect } from 'react';
import { getFactors } from '../api';

export default function FactorsPage() {
  const [factors, setFactors] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    getFactors().then(d => setFactors(d));
  }, []);

  if (!factors) return (
    <div className="flex justify-center py-16">
      <div className="flex items-center gap-3 text-gray-400">
        <div className="w-6 h-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
        <span>Loading factors...</span>
      </div>
    </div>
  );

  const filtered = filter
    ? factors.markets.filter(m => m.group?.toLowerCase().includes(filter.toLowerCase()) || m.market_name?.toLowerCase().includes(filter.toLowerCase()))
    : factors.markets;

  const groups = {};
  for (const m of filtered) {
    const g = m.group || 'Unknown';
    if (!groups[g]) groups[g] = [];
    groups[g].push(m);
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-gray-900">📋 Bet Factors</h1>
        <p className="text-gray-500 text-sm mt-1">
          {factors.total_markets} markets across {factors.total_sports} sports from 1xBet data
        </p>
      </div>

      <input
        className="w-full border border-gray-200 rounded-xl px-4 py-3 mb-6 text-sm bg-white shadow-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
        placeholder="🔍 Search market or group name..."
        value={filter}
        onChange={e => setFilter(e.target.value)}
      />

      <div className="space-y-3">
        {Object.entries(groups).sort().map(([group, markets]) => (
          <details key={group} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden group" open>
            <summary className="px-5 py-3.5 font-bold text-gray-900 cursor-pointer hover:bg-gray-50 transition-colors flex items-center justify-between">
              <span>{group}</span>
              <span className="text-xs text-gray-400 font-normal bg-gray-100 px-2.5 py-1 rounded-full">
                {markets.length} markets
              </span>
            </summary>
            <div className="px-5 pb-4 pt-2 border-t border-gray-50">
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {markets.map((m, i) => (
                  <div key={i} className="bg-gray-50 rounded-xl px-3.5 py-2.5 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">{m.market_name}</span>
                    <span className="text-xs text-gray-400 ml-2 font-mono">{m.event_count}</span>
                  </div>
                ))}
              </div>
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
