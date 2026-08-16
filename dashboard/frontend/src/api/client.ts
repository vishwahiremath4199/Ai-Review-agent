import axios, { AxiosInstance } from 'axios';

// In development, use /api proxy; in production, use the env var or direct URL
const API_BASE_URL = (() => {
  if (import.meta.env.DEV) {
    return '/api';
  }
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
})();

export interface Review {
  id: string;
  repo: string;
  pr_number: number;
  verdict: string;
  critical_count: number;
  warning_count: number;
  suggestion_count: number;
  llm_cost_usd: number | null;
  latency_seconds: number | null;
  created_at: string;
  comments: ReviewComment[];
}

export interface ReviewComment {
  id: string;
  file: string;
  line: number;
  category: string;
  severity: string;
  explanation: string;
  suggested_fix: string | null;
}

export interface Rule {
  match: string;
  category: string;
  checks: string[];
}

export interface RuleSet {
  version: number;
  general_instructions: string;
  rules: Rule[];
  severity_guidance?: Record<string, string>;
}

export interface Analytics {
  total_reviews: number;
  avg_latency_seconds: number | null;
  avg_cost_usd: number | null;
  issues_by_category: Record<string, number>;
  issues_by_severity: Record<string, number>;
}

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Restore token from localStorage if available
    this.token = localStorage.getItem('token');
    if (this.token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    }

    // Add interceptor for token refresh on 401
    this.client.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  logout() {
    this.token = null;
    localStorage.removeItem('token');
    delete this.client.defaults.headers.common['Authorization'];
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<{ access_token: string }> {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async register(email: string, password: string): Promise<{ access_token: string }> {
    const response = await this.client.post('/auth/register', { email, password });
    return response.data;
  }

  // Review endpoints
  async getReviews(repo?: string, severity?: string, skip = 0, limit = 50): Promise<Review[]> {
    const response = await this.client.get('/reviews', {
      params: { repo, severity, skip, limit },
    });
    return response.data;
  }

  async getReview(id: string): Promise<Review> {
    const response = await this.client.get(`/reviews/${id}`);
    return response.data;
  }

  async deleteReview(id: string): Promise<void> {
    await this.client.delete(`/reviews/${id}`);
  }

  // Rules endpoints
  async getRules(): Promise<RuleSet> {
    const response = await this.client.get('/rules');
    return response.data;
  }

  async updateRules(ruleset: RuleSet): Promise<RuleSet> {
    const response = await this.client.put('/rules', ruleset);
    return response.data;
  }

  async validateRules(ruleset: RuleSet): Promise<{ valid: boolean; message: string }> {
    const response = await this.client.post('/rules/validate', ruleset);
    return response.data;
  }

  // Analytics endpoints
  async getAnalyticsSummary(days = 30): Promise<Analytics> {
    const response = await this.client.get('/analytics/summary', {
      params: { days },
    });
    return response.data;
  }

  async getTimeline(metric: 'reviews' | 'cost' | 'latency', days = 30): Promise<Array<{ date: string; value: number }>> {
    const response = await this.client.get('/analytics/timeline', {
      params: { metric, days },
    });
    return response.data;
  }

  async getTopIssues(limit = 10): Promise<Array<{ explanation: string; count: number }>> {
    const response = await this.client.get('/analytics/top-issues', {
      params: { limit },
    });
    return response.data;
  }
}

export default new APIClient();
