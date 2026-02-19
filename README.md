# Marketing OS MVP

A registry-driven Marketing OS MVP where approved templates are validated from Figma, activated per size, and used for deterministic bulk rendering.

## Scope
Included:
- Template governance lifecycle (submit, validate, approve/reject, activate)
- Schema-driven dynamic content injection
- Bulk creation engine (CSV ingest + mapping + review + generate)
- Figma REST API integration (validation preview + render exports)

Excluded:
- Scheduling/publishing
- Analytics
- AI generation
- Campaign calendar

## Architecture
- `backend/` FastAPI service with Supabase-backed persistence and JWT verification
- `supabase/migrations/` SQL schema + `activate_template(template_uuid)` RPC
- `frontend/` minimal React UI showing schema-driven bulk workflow

## Local setup

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3) Supabase migration
Apply SQL from:
- `supabase/migrations/202602190001_marketing_os_mvp.sql`

## API endpoints

### Template governance
- `POST /templates/submit`
- `GET /templates/pending`
- `POST /templates/{id}/approve`
- `POST /templates/{id}/reject`
- `POST /templates/{id}/activate`
- `GET /packs`
- `POST /packs`
- `GET /packs/{id}/coverage`

### Bulk
- `POST /bulk-jobs`
- `POST /bulk-jobs/{id}/upload`
- `POST /bulk-jobs/{id}/map`
- `GET /bulk-jobs/{id}/rows`
- `POST /bulk-jobs/{id}/generate`
- `GET /bulk-jobs/{id}/status`

## Validation rules
- Placeholder regex: `^\{\{[a-zA-Z0-9_]+\}\}$`
- Required placeholder schemas enforced per template type
- Detects: missing required placeholders, duplicates, and TEXT/IMAGE node mismatches

## Notes
- Templates are never hardcoded; active templates are looked up via registry (`templates` with `is_active=true` and `status='APPROVED'`).
- Dynamic injection occurs only during generation.
- Figma calls are used at validation and generation boundaries.
