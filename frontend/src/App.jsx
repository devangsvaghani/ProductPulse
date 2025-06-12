import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import UploadsListPage from './pages/UploadsListPage';
import DetailPage from './pages/DetailPage';
import LoginPage from './pages/LoginPage';
import ProtectedRoute from './components/ProtectedRoute';
import AdminProtectedRoute from './components/AdminProtectedRoute';
import AdminDashboardPage from './pages/AdminDashboardPage';
import UserManagementPage from './pages/UserManagementPage';

const Header = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  if (!user) return null; 

  return (
    <header className="bg-white shadow-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 leading-tight">ProductPulse</h1>
        <nav className="flex items-center space-x-4">
          <Link to="/" className={`text-sm font-medium ${location.pathname === '/' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>My Dashboard</Link>
          {user.is_admin && (
            <Link to="/admin" className={`text-sm font-medium ${location.pathname.startsWith('/admin') ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}>Admin</Link>
          )}
          <button onClick={logout} className="text-sm font-medium text-gray-500 hover:text-gray-700">Logout</button>
        </nav>
      </div>
    </header>
  );
};


function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

function AppContent() {
  const { loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Header />
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<UploadsListPage />} />
            <Route path="/upload/:uploadId" element={<DetailPage />} />
          </Route>

          <Route element={<AdminProtectedRoute />}>
            <Route path="/admin" element={<AdminDashboardPage />} />
            <Route path="/admin/users" element={<UserManagementPage />} />
          </Route>

        </Routes>
      </main>
    </div>
  );
}

export default App;