import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient, { Review } from '../api/client';

export default function ReviewDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [review, setReview] = useState<Review | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    fetchReview();
  }, [id]);

  const fetchReview = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getReview(id!);
      setReview(data);
      setError('');
    } catch (err: any) {
      setError('Failed to load review');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityEmoji = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🔴';
      case 'warning':
        return '🟡';
      default:
        return '💡';
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      security: 'bg-red-50 border-red-200 text-red-900',
      'bug-risk': 'bg-orange-50 border-orange-200 text-orange-900',
      'code-quality': 'bg-blue-50 border-blue-200 text-blue-900',
      testing: 'bg-green-50 border-green-200 text-green-900',
      style: 'bg-purple-50 border-purple-200 text-purple-900',
      database: 'bg-pink-50 border-pink-200 text-pink-900',
      frontend: 'bg-indigo-50 border-indigo-200 text-indigo-900',
    };
    return colors[category] || 'bg-gray-50 border-gray-200 text-gray-900';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Review not found'}
      </div>
    );
  }

  const commentsByFile = review.comments.reduce((acc, comment) => {
    if (!acc[comment.file]) acc[comment.file] = [];
    acc[comment.file].push(comment);
    return acc;
  }, {} as Record<string, typeof review.comments>);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-800">
          {review.repo} #{review.pr_number}
        </h1>
        <button
          onClick={() => navigate('/')}
          className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg"
        >
          ← Back
        </button>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Verdict</h2>
        <p className="text-gray-700 mb-6 text-lg">{review.verdict}</p>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-red-50 p-4 rounded border border-red-200">
            <div className="text-3xl font-bold text-red-600">{review.critical_count}</div>
            <div className="text-sm text-red-700 font-medium mt-1">Critical</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded border border-yellow-200">
            <div className="text-3xl font-bold text-yellow-600">{review.warning_count}</div>
            <div className="text-sm text-yellow-700 font-medium mt-1">Warning</div>
          </div>
          <div className="bg-blue-50 p-4 rounded border border-blue-200">
            <div className="text-3xl font-bold text-blue-600">{review.suggestion_count}</div>
            <div className="text-sm text-blue-700 font-medium mt-1">Suggestion</div>
          </div>
          <div className="bg-gray-50 p-4 rounded border border-gray-200">
            <div className="text-3xl font-bold text-gray-600">
              ${review.llm_cost_usd?.toFixed(4) || '0.00'}
            </div>
            <div className="text-sm text-gray-700 font-medium mt-1">API Cost</div>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          <p>⏱️ Analyzed in {review.latency_seconds?.toFixed(2) || '?'}s</p>
          <p>📅 {new Date(review.created_at).toLocaleString()}</p>
        </div>
      </div>

      {/* Comments by File */}
      <div className="space-y-6">
        {Object.entries(commentsByFile).map(([file, comments]) => (
          <div key={file} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">{file}</h3>
            <div className="space-y-4">
              {comments.map((comment) => (
                <div
                  key={comment.id}
                  className={`border-l-4 p-4 rounded ${getCategoryColor(comment.category)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="text-2xl mr-2">{getSeverityEmoji(comment.severity)}</span>
                      <span className="font-semibold">{comment.category}</span>
                      <span className="ml-2 text-sm font-medium">Line {comment.line}</span>
                    </div>
                    <span className="text-xs font-semibold uppercase px-2 py-1 rounded bg-white bg-opacity-50">
                      {comment.severity}
                    </span>
                  </div>
                  <p className="text-gray-900 mb-2">{comment.explanation}</p>
                  {comment.suggested_fix && (
                    <div className="mt-3 bg-black bg-opacity-5 p-3 rounded font-mono text-sm text-gray-800">
                      <pre className="whitespace-pre-wrap">{comment.suggested_fix}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {review.comments.length === 0 && (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 text-lg">✅ No issues found in this review!</p>
        </div>
      )}
    </div>
  );
}
