import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import ReviewDetail from './pages/ReviewDetail';
import RulesEditor from './pages/RulesEditor';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import apiClient from './api/client';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (token in localStorage)
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (token: string) => {
    apiClient.setToken(token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    apiClient.logout();
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {isAuthenticated ? (
          <div className="flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-lg">
              <div className="p-6 border-b">
                <h1 className="text-2xl font-bold text-gray-800">ReviewPilot</h1>
                <p className="text-sm text-gray-500">AI Code Review Dashboard</p>
              </div>
              <nav className="p-4 space-y-2">
                <NavLink href="/" label="Dashboard" />
                <NavLink href="/analytics" label="Analytics" />
                <NavLink href="/rules" label="Review Rules" />
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded"
                >
                  Logout
                </button>
              </nav>
            </aside>

            {/* Main content */}
            <main className="flex-1 p-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/reviews/:id" element={<ReviewDetail />} />
                <Route path="/rules" element={<RulesEditor />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
            </main>
          </div>
        ) : (
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        )}
      </div>
    </Router>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  const isActive = window.location.pathname === href;
  return (
    <a
      href={href}
      className={`block px-4 py-2 rounded transition ${
        isActive
          ? 'bg-blue-50 text-blue-600 font-semibold'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      {label}
    </a>
  );
}

export default App;
