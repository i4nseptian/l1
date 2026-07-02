import { Outlet, Link, useLocation } from 'react-router-dom';

const nav = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/manual-predict', label: 'Manual Predict', icon: '⚽' },
  { path: '/factors', label: 'Bet Markets', icon: '📋' },
  { path: '/world-cup', label: 'World Cup', icon: '🏆' },
  { path: '/history', label: 'History', icon: '📜' },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-green-50">
      <nav className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <span className="text-2xl">⚽</span>
            <span className="text-xl font-extrabold bg-gradient-to-r from-green-700 to-emerald-500 bg-clip-text text-transparent group-hover:from-emerald-500 group-hover:to-green-700 transition-all">
              PrediksiBola
            </span>
          </Link>
          <div className="flex gap-1 overflow-x-auto">
            {nav.map(item => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 whitespace-nowrap ${
                    isActive
                      ? 'bg-gradient-to-r from-green-700 to-emerald-600 text-white shadow-md shadow-green-200'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <Outlet />
      </main>
    </div>
  );
}
