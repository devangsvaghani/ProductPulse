import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadsListPage from './pages/UploadsListPage';
import DetailPage from './pages/DetailPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 font-sans">
        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <h1 className="text-2xl font-bold text-gray-900 leading-tight">ProductPulse</h1>
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<UploadsListPage />} />
            <Route path="/upload/:uploadId" element={<DetailPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;