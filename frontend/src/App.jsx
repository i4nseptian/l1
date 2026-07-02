import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ManualPredict from './pages/ManualPredict';
import Factors from './pages/Factors';
import History from './pages/History';
import MatchDetail from './pages/MatchDetail';
import WorldCup from './pages/WorldCup';
import Layout from './components/Layout';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/manual-predict" element={<ManualPredict />} />
          <Route path="/factors" element={<Factors />} />
          <Route path="/history" element={<History />} />
          <Route path="/match/:id" element={<MatchDetail />} />
          <Route path="/world-cup" element={<WorldCup />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
