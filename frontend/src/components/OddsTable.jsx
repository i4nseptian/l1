export default function OddsTable({ odds }) {
  if (!odds) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="text-left px-3 py-2 font-medium text-gray-600">Market</th>
            <th className="text-center px-3 py-2 font-medium text-gray-600">1 (Home)</th>
            <th className="text-center px-3 py-2 font-medium text-gray-600">X (Draw)</th>
            <th className="text-center px-3 py-2 font-medium text-gray-600">2 (Away)</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {Object.entries(odds).map(([market, values]) => (
            <tr key={market} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-medium capitalize">{market.replace(/_/g, ' ')}</td>
              <td className="px-3 py-2 text-center">{values.home?.toFixed(2) || '-'}</td>
              <td className="px-3 py-2 text-center">{values.draw?.toFixed(2) || '-'}</td>
              <td className="px-3 py-2 text-center">{values.away?.toFixed(2) || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
