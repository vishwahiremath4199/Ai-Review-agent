import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import apiClient, { Analytics } from '../api/client';

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [topIssues, setTopIssues] = useState<any[]>([]);
  const [days, setDays] = useState(30);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true);
      setError('');

      const [analyticsData, reviewsTimeline, issuesTimeline, costTimeline, topIssuesData] =
        await Promise.all([
          apiClient.getAnalyticsSummary(days),
          apiClient.getTimeline('reviews', days),
          apiClient.getTimeline('latency', days),
          apiClient.getTimeline('cost', days),
          apiClient.getTopIssues(10),
        ]);

      setAnalytics(analyticsData);

      // Combine timelines
      const combined = reviewsTimeline.map((item, idx) => ({
        date: item.date,
        reviews: item.value,
        latency: issuesTimeline[idx]?.value || 0,
        cost: costTimeline[idx]?.value || 0,
      }));
      setTimelineData(combined);
      setTopIssues(issuesTimeline);
    } catch (err: any) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Failed to load analytics'}
      </div>
    );
  }

  const categoryData = Object.entries(analytics.issues_by_category || {}).map(
    ([name, value]) => ({
      name,
      value,
    })
  );

  const severityData = Object.entries(analytics.issues_by_severity || {}).map(
    ([name, value]) => ({
      name,
      value,
    })
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Analytics</h1>
        <select
          value={days}
          onChange={(e) => setDays(parseInt(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-blue-600">{analytics.total_reviews}</div>
          <div className="text-gray-600 text-sm mt-2">Total Reviews</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-green-600">
            {analytics.avg_latency_seconds?.toFixed(2) || '0'}s
          </div>
          <div className="text-gray-600 text-sm mt-2">Avg. Latency</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-orange-600">
            ${analytics.avg_cost_usd?.toFixed(4) || '0.00'}
          </div>
          <div className="text-gray-600 text-sm mt-2">Avg. Cost</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-purple-600">
            {Object.values(analytics.issues_by_severity || {}).reduce((a, b) => a + b, 0)}
          </div>
          <div className="text-gray-600 text-sm mt-2">Total Issues</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Issues by Category */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Issues by Category</h2>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>

        {/* Severity Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Severity Distribution</h2>
          {severityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>
      </div>

      {/* Timeline */}
      {timelineData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Review Timeline</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="reviews" stroke="#3b82f6" />
              <Line yAxisId="right" type="monotone" dataKey="cost" stroke="#f59e0b" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Issues */}
      {topIssues.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Top Issues</h2>
          <div className="space-y-3">
            {topIssues.slice(0, 10).map((issue, idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b last:border-b-0">
                <span className="text-gray-700 flex-1">{issue.explanation?.substring(0, 60)}...</span>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                  {issue.value} occurrence{issue.value > 1 ? 's' : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
