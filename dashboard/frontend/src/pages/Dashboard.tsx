import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient, { Review } from '../api/client';

export default function Dashboard() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getReviews();
      setReviews(data);
      setError('');
    } catch (err: any) {
      setError('Failed to load reviews');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this review?')) {
      try {
        await apiClient.deleteReview(id);
        setReviews(reviews.filter(r => r.id !== id));
      } catch (err: any) {
        setError('Failed to delete review');
      }
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Review History</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {reviews.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 text-lg">No reviews yet. Pull requests will appear here.</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {reviews.map((review) => (
            <div
              key={review.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 cursor-pointer"
              onClick={() => navigate(`/reviews/${review.id}`)}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">
                    {review.repo} #{review.pr_number}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(review.created_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(review.id);
                  }}
                  className="text-red-500 hover:text-red-700 font-medium text-sm"
                >
                  Delete
                </button>
              </div>

              <p className="text-gray-700 mb-4">{review.verdict}</p>

              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-red-50 p-3 rounded">
                  <div className="text-2xl font-bold text-red-600">{review.critical_count}</div>
                  <div className="text-sm text-red-700 font-medium">Critical</div>
                </div>
                <div className="bg-yellow-50 p-3 rounded">
                  <div className="text-2xl font-bold text-yellow-600">{review.warning_count}</div>
                  <div className="text-sm text-yellow-700 font-medium">Warning</div>
                </div>
                <div className="bg-blue-50 p-3 rounded">
                  <div className="text-2xl font-bold text-blue-600">{review.suggestion_count}</div>
                  <div className="text-sm text-blue-700 font-medium">Suggestion</div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-2xl font-bold text-gray-600">
                    ${review.llm_cost_usd?.toFixed(4) || '0.00'}
                  </div>
                  <div className="text-sm text-gray-700 font-medium">API Cost</div>
                </div>
              </div>

              {review.latency_seconds && (
                <div className="text-sm text-gray-600">
                  ⏱️ Analyzed in {review.latency_seconds.toFixed(2)}s
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
