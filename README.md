# Daily Expense App

FastAPI + Postgres backend with a Vite (React/TS) front-end to track daily expenses, categories, and simple budgets.

## Prerequisites
- Python 3.11+
- Node 18+
- Postgres running locally (or connection string available)

## Backend
1. Create env file:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Update `DATABASE_URL` if needed (defaults to `postgresql://postgres:postgres@localhost:5432/expenses`).
3. Install deps and run the API:
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --env-file .env
   ```
4. (Optional) Seed demo data once the database exists:
   ```bash
   cd backend
   python -m app.seed
   ```
5. API docs will be at `http://localhost:8000/api/docs`.

Key endpoints (prefix `/api`):
- `POST /users` create user
- `GET /categories` list by `owner_id`
- `POST /expenses` create expense
- `GET /expenses/daily` daily totals (query `owner_id`)
- `GET /reports/dashboard` aggregate totals/top categories

## Frontend
1. Install and run:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. The app expects the backend at `http://localhost:8000/api`. Override with `.env` in `frontend`:
   ```bash
   VITE_API_URL=http://localhost:8000/api
   ```

## Docker
1. Ensure you have Docker and Docker Compose installed.
2. Build and run the stack (Postgres, backend, frontend):
   ```bash
   docker compose up --build
   ```
3. Frontend will be available at `http://localhost:4173` (or your host IP); API at `http://localhost:8000/api`.
4. Environment overrides:
   - Backend CORS origins are set in `docker-compose.yml` (`CORS_ORIGINS`). Add your host/IP:port if accessing from another device.
   - Frontend API base can be set via `VITE_API_URL` build arg/env in `docker-compose.yml` (defaults to the host API URL). If your host IP changes, update it and rebuild the frontend: `docker compose build frontend`.

## Project layout
- `backend/app/main.py` – FastAPI app + routers
- `backend/app/models.py` – SQLAlchemy models (users, categories, expenses, budgets)
- `backend/app/seed.py` – inserts demo user/categories/expenses
- `frontend/src` – React UI (forms, dashboard, charts)

## Notes
- Data is scoped by `owner_id`; the seed script creates a demo user with ID `1` used by the front-end by default.
- Tables auto-create on startup; Alembic migrations are provided for controlled upgrades/rollbacks.
- Authentication: simple email/password + bearer token is included for demos; harden before production (password policies, HTTPS, refresh tokens, user roles).
