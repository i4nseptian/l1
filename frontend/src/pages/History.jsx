import { useState, useEffect } from 'react';

export default function History() {
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([
      fetch('/api/history').then(r => r.json()),
      fetch('/api/history/stats').then(r => r.json()),
    ]).then(([h, s]) => {
      setPredictions(h.predictions || []);
      setStats(s);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(load, []);

  const recordResult = async (id, result) => {
    await fetch(`/api/history/${id}/result`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ actual_result: result }),
    });
    load();
  };

  const deletePrediction = async (id) => {
    if (!confirm('Hapus prediksi ini?')) return;
    await fetch(`/api/history/${id}`, { method: 'DELETE' });
    load();
  };

  if (loading) return (
    <div className="flex justify-center py-16">
      <div className="flex items-center gap-3 text-gray-400">
        <div className="w-6 h-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
        <span>Loading history...</span>
      </div>
    </div>
  );

  const pendings = predictions.filter(p => p.is_correct === null);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Prediction History</h1>
          <p className="text-gray-500 text-sm mt-1">Track accuracy & record actual results</p>
        </div>
        <button onClick={load} className="text-xs text-gray-400 hover:text-gray-600 px-3 py-1.5 rounded-lg border border-gray-200">
          ↻ Refresh
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
          {[
            { label: 'Total', value: stats.total, color: 'text-gray-900', bg: 'bg-gray-50', border: 'border-gray-200' },
            { label: 'Correct', value: stats.correct, color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200' },
            { label: 'Wrong', value: stats.wrong, color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200' },
            { label: 'Pending', value: stats.pending, color: 'text-yellow-700', bg: 'bg-yellow-50', border: 'border-yellow-200' },
            { label: 'Accuracy', value: `${stats.accuracy}%`, color: stats.accuracy >= 60 ? 'text-green-700' : 'text-red-700', bg: 'bg-gray-50', border: 'border-gray-200' },
          ].map(s => (
            <div key={s.label} className={`${s.bg} rounded-2xl border ${s.border} p-4 text-center`}>
              <div className={`text-2xl font-black ${s.color}`}>{s.value}</div>
              <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Pending Results Alert */}
      {pendings.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">⏳</span>
            <span className="font-bold text-amber-800 text-sm">{pendings.length} prediksi belum direkam hasilnya</span>
          </div>
          <p className="text-xs text-amber-600">Klik tombol Home / Draw / Away untuk mencatat hasil sebenarnya.</p>
        </div>
      )}

      {/* Table */}
      {predictions.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-16 text-center">
          <span className="text-6xl block mb-4">📊</span>
          <p className="text-lg font-medium text-gray-500 mb-1">Belum ada prediksi</p>
          <p className="text-sm text-gray-400">Buat prediksi dari halaman Manual Predict</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">#</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Date</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Match</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Prediction</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Conf.</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Scores</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Actual Result</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Status</th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-500 text-[10px] uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {predictions.map((p, i) => {
                  const scores = p.score_breakdown || {};
                  return (
                    <tr key={p.id} className={`hover:bg-gray-50/50 transition-colors ${
                      p.is_correct === true ? 'bg-green-50/30' :
                      p.is_correct === false ? 'bg-red-50/30' : ''
                    }`}>
                      <td className="px-4 py-3 text-[10px] text-gray-400 font-mono">{p.id}</td>
                      <td className="px-4 py-3 text-xs text-gray-500 whitespace-nowrap">
                        {p.created_at?.slice(0, 10)}
                        <br /><span className="text-[10px] text-gray-400">{p.created_at?.slice(11, 16)}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-gray-900 text-xs">{p.home_team || 'N/A'}</div>
                        <div className="text-[10px] text-gray-400">vs</div>
                        <div className="font-semibold text-gray-900 text-xs">{p.away_team || 'N/A'}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold ${
                          p.predicted_winner === 'home' ? 'bg-green-50 text-green-700' :
                          p.predicted_winner === 'away' ? 'bg-blue-50 text-blue-700' :
                          'bg-yellow-50 text-yellow-700'
                        }`}>
                          {p.predicted_winner === 'home' ? '🏠' : p.predicted_winner === 'away' ? '✈️' : '⚖️'}
                          {p.predicted_winner}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`font-black text-sm ${
                          p.confidence >= 80 ? 'text-green-600' :
                          p.confidence >= 60 ? 'text-yellow-600' :
                          'text-gray-400'
                        }`}>{p.confidence}%</span>
                      </td>
                      <td className="px-4 py-3 text-[10px] text-gray-500">
                        {scores.home != null && (
                          <div className="space-y-0.5">
                            <div>H: {scores.home?.toFixed(1)}</div>
                            <div>D: {scores.draw?.toFixed(1)}</div>
                            <div>A: {scores.away?.toFixed(1)}</div>
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {p.is_correct === null ? (
                          <div className="flex gap-1">
                            {['home', 'draw', 'away'].map(r => (
                              <button key={r} onClick={() => recordResult(p.id, r)}
                                className="px-2 py-1 text-[10px] font-bold rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors capitalize">
                                {r === 'home' ? '🏠' : r === 'away' ? '✈️' : '⚖️'} {r}
                              </button>
                            ))}
                          </div>
                        ) : (
                          <span className={`text-xs font-bold ${
                            p.actual_result === 'home' ? 'text-green-600' :
                            p.actual_result === 'away' ? 'text-blue-600' :
                            'text-yellow-600'
                          }`}>
                            {p.actual_result === 'home' ? '🏠' : p.actual_result === 'away' ? '✈️' : '⚖️'}
                            {' '}{p.actual_result}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {p.is_correct === true && (
                          <span className="inline-flex items-center gap-1 text-xs font-bold text-green-700 bg-green-100 px-2.5 py-1 rounded-full">
                            ✅ Correct
                          </span>
                        )}
                        {p.is_correct === false && (
                          <span className="inline-flex items-center gap-1 text-xs font-bold text-red-700 bg-red-100 px-2.5 py-1 rounded-full">
                            ❌ Wrong
                          </span>
                        )}
                        {p.is_correct === null && (
                          <span className="text-[10px] text-gray-400 bg-gray-100 px-2.5 py-1 rounded-full">
                            Pending
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button onClick={() => deletePrediction(p.id)}
                          className="text-[10px] text-red-400 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50 transition-colors">
                          🗑
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Learning Feedback Note */}
      {stats && stats.total >= 5 && (
        <div className="mt-6 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-2xl border border-indigo-100 p-5">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧠</span>
            <div>
              <h3 className="font-bold text-indigo-900 text-sm">Machine Learning Aktif</h3>
              <p className="text-xs text-indigo-600 mt-0.5">
                Riwayat {stats.total} prediksi digunakan sebagai umpan balik untuk meningkatkan akurasi prediksi berikutnya.
                Akurasi saat ini: <strong className="text-indigo-900">{stats.accuracy}%</strong>
                {stats.accuracy >= 70 ? ' 👍 Teruskan!' : stats.accuracy >= 50 ? ' ⚠️ Masih perlu perbaikan.' : ' 📉 Perlu evaluasi ulang.'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
