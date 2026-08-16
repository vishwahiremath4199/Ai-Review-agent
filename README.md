# ReviewPilot - AI Code Review Agent

An automated AI-powered code review system that integrates with GitHub to review pull requests using Claude AI, powered by a React dashboard for managing review rules and analytics.

## 🎯 Features

- **Automatic PR Reviews**: Triggers on every pull request, analyzing code changes within ~30-60 seconds
- **Structured Comments**: Posts inline comments on specific lines with categorized issues (security, bugs, code-quality, testing, style, database, frontend)
- **Severity Levels**: Each review comment has a severity (critical, warning, suggestion)
- **Configurable Rules**: YAML-based rules file with glob pattern matching for path-specific review criteria
- **General Intelligence**: LLM also applies best practices beyond explicit rules based on code context
- **Dashboard UI**: 
  - View all reviewed PRs with aggregated stats
  - Detailed review breakdown by file and issue
  - Edit review rules via a form-based interface
  - Analytics with charts (issues by category, severity distribution, latency trends, cost analysis)
- **Simple Auth**: JWT-based authentication for dashboard access
- **Dockerized**: Complete Docker Compose setup for local development and deployment

---

## 🏗️ Architecture

```
GitHub PR opened/updated
        ↓
GitHub Actions workflow triggers
        ↓
review-agent/main.py runs
  ├─ Fetch PR diff via GitHub API
  ├─ Load review-rules.yaml
  ├─ Match changed files against rule scopes
  ├─ Call Claude API with prompt
  ├─ Parse structured JSON response
  └─ Post comments back to PR + push to dashboard

Dashboard (FastAPI + React + PostgreSQL)
  ├─ GET /reviews - list past reviews
  ├─ GET /rules - current rules
  ├─ PUT /rules - update rules
  └─ GET /analytics - aggregated stats
```

---

## 📁 Project Structure

```
ai-code-review-agent/
├── review-agent/                 # Python package + GitHub Action
│   ├── main.py                   # Entrypoint run by GitHub Actions
│   ├── github_client.py          # GitHub API integration
│   ├── rules_loader.py           # YAML rule loading & matching
│   ├── llm_client.py             # Claude API integration
│   ├── models.py                 # Pydantic models
│   └── requirements.txt
│
├── dashboard/
│   ├── backend/                  # FastAPI application
│   │   ├── app/
│   │   │   ├── main.py           # FastAPI app entry
│   │   │   ├── models.py         # SQLAlchemy models
│   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   ├── database.py       # DB connection
│   │   │   ├── auth.py           # JWT authentication
│   │   │   └── routers/
│   │   │       ├── reviews.py    # Review endpoints
│   │   │       ├── rules.py      # Rules endpoints
│   │   │       └── analytics.py  # Analytics endpoints
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/                 # React + TypeScript
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── ReviewDetail.tsx
│       │   │   ├── RulesEditor.tsx
│       │   │   ├── Analytics.tsx
│       │   │   └── Login.tsx
│       │   ├── api/client.ts
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── index.html
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── package.json
│       ├── Dockerfile
│       └── tsconfig.json
│
├── .github/
│   └── workflows/
│       └── ai-review.yml         # GitHub Action workflow
│
├── review-rules.yaml             # Example rules file
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Review Agent**: Python 3.11+, GitHub account with repo access
- **Dashboard**: Docker & Docker Compose (or Node.js 18+, PostgreSQL 16)
- **API Keys**: Anthropic API key, GitHub token

### 1. Setup Review Agent

1. Copy this repository to your target repo:
   ```bash
   # In your target repo
   cp -r review-agent/ .
   cp .github/workflows/ai-review.yml .github/workflows/
   cp review-rules.yaml .
   ```

2. Set up repository secrets in GitHub:
   - `ANTHROPIC_API_KEY`: Your Claude API key
   - `GITHUB_TOKEN`: (automatically provided by GitHub Actions)
   - `DASHBOARD_API_URL`: (optional) URL to dashboard backend

3. The action will trigger on all new/updated PRs automatically!

### 2. Setup Dashboard (Local Development)

1. **Using Docker Compose** (recommended):
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Edit .env with your values (at minimum: ANTHROPIC_API_KEY)
   
   # Start all services
   docker-compose up
   
   # Access:
   # - Frontend: http://localhost:5173
   # - Backend API: http://localhost:8000
   # - API Docs: http://localhost:8000/docs
   ```

2. **Manual Setup**:
   ```bash
   # Backend
   cd dashboard/backend
   pip install -r requirements.txt
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reviewpilot
   python -m app.database  # Initialize DB
   uvicorn app.main:app --reload
   
   # Frontend (in another terminal)
   cd dashboard/frontend
   npm install
   npm run dev
   ```

### 3. Initial Login

Demo credentials (can be changed):
- Email: `demo@example.com`
- Password: `demo`

Or register a new account on the login page.

---

## 🔧 Configuration

### Review Rules (`review-rules.yaml`)

The rules file lives in your repository root and defines review criteria:

```yaml
version: 1

general_instructions: >
  Review this PR like a senior engineer. Check for security issues,
  bugs, and code quality problems.

rules:
  - match: "**/auth/**"
    category: security
    checks:
      - "No plaintext passwords"
      - "JWT tokens must have expiry"
      - "Rate limiting on auth endpoints"

  - match: "**/models/**"
    category: database
    checks:
      - "Foreign key columns indexed"
      - "Migrations are reversible"

  - match: "**/*.py"
    category: code-quality
    checks:
      - "No bare except clauses"
      - "Public functions documented"

severity_guidance:
  critical: "Security vulnerabilities, data loss risk"
  warning: "Bugs, missing error handling"
  suggestion: "Style, naming, refactoring"
```

Edit rules directly in the dashboard UI (Rules Editor page) and they'll be saved to the repository.

---

## 🔌 GitHub Action Setup

The workflow is defined in `.github/workflows/ai-review.yml`:

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r review-agent/requirements.txt
      - name: Run AI review
        run: python review-agent/main.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## 📊 Dashboard Pages

### 1. **Dashboard** (`/`)
- Table of recent reviews with repo, PR number, verdict badge, and severity counts
- Click through to detailed review
- Delete reviews

### 2. **Review Detail** (`/reviews/:id`)
- Full breakdown by file
- Comments grouped with category/severity badges
- Suggested fixes displayed in code blocks
- Overall verdict and statistics

### 3. **Rules Editor** (`/rules`)
- Form-based UI for adding/editing/removing rules
- File pattern input with glob support
- Category selection dropdown
- Check list management
- Validates and saves back to repository

### 4. **Analytics** (`/analytics`)
- Total reviews, avg latency, avg cost summary cards
- Bar chart: Issues by category
- Pie chart: Severity distribution
- Line chart: Review timeline
- Top recurring issues list
- Configurable time range (7/30/90/365 days)

---

## 🔐 Authentication

- Simple JWT-based auth
- Default single-user or register new accounts
- Tokens stored in localStorage
- Email + password model (no OAuth in v1.0)

For production, implement proper auth:
- OAuth 2.0 via GitHub/Google
- Enterprise SSO
- Rate limiting
- HTTPS only

---

## 📈 API Reference

### Authentication

```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "password"
}

POST /auth/register
{
  "email": "user@example.com",
  "password": "password"
}
```

### Reviews

```bash
POST /reviews              # Ingest new review from agent
GET /reviews               # List reviews (paginated)
GET /reviews/{id}          # Get review detail
DELETE /reviews/{id}       # Delete review
```

### Rules

```bash
GET /rules                 # Get current rules YAML
PUT /rules                 # Update rules
POST /rules/validate       # Validate ruleset
```

### Analytics

```bash
GET /analytics/summary     # Aggregate stats
GET /analytics/timeline    # Daily timeline data
GET /analytics/top-issues  # Most common issues
```

Full interactive docs at `http://localhost:8000/docs` (Swagger UI)

---

## 🛠️ Development

### Backend Development

```bash
cd dashboard/backend

# Install dependencies
pip install -r requirements.txt

# Run locally
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reviewpilot
uvicorn app.main:app --reload

# Run tests
pytest

# Database migrations (Alembic)
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

### Frontend Development

```bash
cd dashboard/frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Review Agent Development

```bash
cd review-agent

# Install dependencies
pip install -r requirements.txt

# Test locally
export ANTHROPIC_API_KEY=your_key
export GITHUB_TOKEN=your_token
export GITHUB_REPOSITORY=owner/repo
export GITHUB_EVENT_PATH=./test_event.json  # Mock PR event

python main.py
```

---

## 🐛 Troubleshooting

### "Failed to load reviews" error

- Check backend is running: `curl http://localhost:8000/health`
- Check database connection: `DATABASE_URL` in .env
- Check network tab in browser for 401/403 errors

### Claude API rate limits

- Use cost per input/output token estimates: ~$0.003/$0.015 per 1K tokens
- Implement caching for re-runs on same diff
- Use batch processing for high-volume repos

### GitHub Action not triggering

- Confirm `ANTHROPIC_API_KEY` is set in repo secrets
- Check GitHub Actions is enabled in repo settings
- Workflow file must be in `.github/workflows/`
- Trigger on `pull_request` event

### Rules not matching files

- Use `fnmatch` glob syntax: `**/auth/**`, `**/*.py`
- Test pattern matching: use debug print in `rules_loader.py`
- Rules are case-sensitive on Linux/Mac

---

## 📦 Deployment

### Deploy to Production

1. **Backend** (example: Railway, Render, or AWS):
   ```bash
   # Environment variables:
   DATABASE_URL=postgresql://...
   JWT_SECRET=strong-random-secret
   CORS_ORIGINS=https://yourdomain.com
   ENV=production
   
   # Command:
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Frontend** (example: Vercel, Netlify, or CloudFront):
   ```bash
   npm run build
   # Deploy ./dist folder
   ```

3. **Database** (Managed PostgreSQL):
   - Use AWS RDS, Railway, or similar managed service
   - Backups enabled, minimum 30 GB

4. **GitHub Action** in target repo:
   - Set secrets: `ANTHROPIC_API_KEY`, `DASHBOARD_API_URL`
   - Workflow runs automatically on PRs

---

## 🎯 Stretch Goals

- [ ] Support GitLab/Bitbucket
- [ ] Read linked issues/tickets for context
- [ ] Re-review button without new commits
- [ ] Human feedback loop (thumbs-up/-down comments)
- [ ] Caching layer for duplicate diffs
- [ ] Parallel review processing
- [ ] Cost optimization with cheaper models
- [ ] PR conversation integration (threaded reviews)
- [ ] Review accuracy dashboard + model fine-tuning

---

## 📝 License

MIT

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@reviewpilot.example.com
- Documentation: https://reviewpilot.example.com/docs

---

## 🎉 Acknowledgments

- Built with [Claude AI](https://anthropic.com) for code review intelligence
- Dashboard UI with [React](https://react.dev), [Tailwind CSS](https://tailwindcss.com), [Recharts](https://recharts.org)
- Backend with [FastAPI](https://fastapi.tiangolo.com), [SQLAlchemy](https://sqlalchemy.org), [Alembic](https://alembic.sqlalchemy.org)
- CI/CD with [GitHub Actions](https://github.com/features/actions)

---

**Happy Reviewing! 🚀**
