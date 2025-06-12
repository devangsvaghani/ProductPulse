import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { FaUsers, FaFileUpload, FaTasks, FaCheckCircle, FaTimesCircle, FaLightbulb } from 'react-icons/fa';

const StatCard = ({ icon, title, value, color }) => (
  <div className={`bg-white shadow rounded-lg p-6 flex items-center ${color}`}>
    <div className="mr-4 text-3xl">{icon}</div>
    <div>
      <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
      <dd className="mt-1 text-3xl font-semibold text-gray-900">{value}</dd>
    </div>
  </div>
);

const AdminDashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get('/api/v1/admin/analytics');
        setStats(response.data);
      } catch (error) {
        console.error("Failed to fetch analytics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading || !stats) {
    return <div className="p-8 text-center">Loading Admin Dashboard...</div>;
  }

  const { total_users, total_uploads, uploads_by_status, total_analysis_results } = stats;

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Admin Dashboard</h1>
        
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard icon={<FaUsers />} title="Total Users" value={total_users} />
          <StatCard icon={<FaFileUpload />} title="Total Files Uploaded" value={total_uploads} />
          <StatCard icon={<FaLightbulb />} title="Total AI Summaries" value={total_analysis_results} color="text-purple-500" />
          <StatCard icon={<FaTasks />} title="Processing" value={uploads_by_status.processing || 0} />
          <StatCard icon={<FaCheckCircle />} title="Completed" value={uploads_by_status.completed || 0} color="text-green-500" />
          <StatCard icon={<FaTimesCircle />} title="Failed" value={uploads_by_status.failed || 0} color="text-red-500" />
        </div>

        <div className="mt-10">
          <Link 
            to="/admin/users" 
            className="inline-block bg-indigo-600 text-white font-bold py-2 px-4 rounded hover:bg-indigo-700"
          >
            Manage Users
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;