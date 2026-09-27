# InsightFlow — AI-Powered Business Intelligence Platform

InsightFlow is a full-stack portfolio project combining **Data Analytics, Data Engineering, Machine Learning, AI-assisted analytics, and Full Stack Development**.

## Features
- Professional responsive analytics SaaS UI
- CSV upload and validation
- Pandas ETL pipeline
- PostgreSQL support (SQLite fallback for immediate local demo)
- Data-quality scoring
- KPI analytics and interactive charts
- Sales forecasting baseline
- RFM + K-Means customer segmentation
- Isolation Forest anomaly detection
- Grounded Business Analyst with supported natural-language intents
- Business insights generated from real data
- Sample e-commerce dataset generator
- Docker Compose for PostgreSQL + API + frontend
- API documentation through FastAPI
- Tests for core API and ETL functionality

## Architecture

React + TypeScript + Vite
        ↓
FastAPI
        ↓
ETL / Analytics / ML / Analyst Services
        ↓
SQLAlchemy
        ↓
PostgreSQL

## Quick start — easiest

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

The default local `.env` uses SQLite so the project can run without database provisioning. For PostgreSQL, set:
`DATABASE_URL=postgresql+psycopg://user:password@host:5432/insightflow`

## Docker
```bash
docker compose up --build
```

## Sample data
The backend can generate and load 10,000+ realistic e-commerce records:
```bash
cd backend
python -m app.seed --rows 12000
```

## Portfolio positioning
InsightFlow demonstrates:
- Python / FastAPI
- React / TypeScript
- SQL / relational data modeling
- ETL and data validation
- Business analytics
- Forecasting
- Unsupervised ML
- Anomaly detection
- API design
- Testing
- Docker / deployment readiness

## Important
This is a portfolio MVP, not a production multi-tenant BI product. Authentication, billing, distributed queues, and external LLM integration are intentionally outside the first version.
