import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import StocksPage from './pages/StocksPage'
import StockDetailPage from './pages/StockDetailPage'
import PatternsPage from './pages/PatternsPage'
import PatternCreatePage from './pages/PatternCreatePage'
import WatchlistPage from './pages/WatchlistPage'
import NotificationSettingsPage from './pages/NotificationSettingsPage'
import AuthGuard from './components/AuthGuard'
import Layout from './components/Layout'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<AuthGuard />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/stocks" element={<StocksPage />} />
            <Route path="/stocks/:code" element={<StockDetailPage />} />
            <Route path="/patterns" element={<PatternsPage />} />
            <Route path="/patterns/new" element={<PatternCreatePage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/settings/notifications" element={<NotificationSettingsPage />} />
          </Route>
        </Route>
      </Routes>
    </div>
  )
}

export default App
