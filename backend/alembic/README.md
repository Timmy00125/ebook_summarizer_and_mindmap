# Database Migrations with Alembic

This directory contains database migration scripts managed by Alembic.

## Prerequisites

1. Ensure PostgreSQL is running
2. Set `DATABASE_URL` environment variable in your `.env` file
3. Install dependencies: `pip install -r requirements.txt`

## Common Commands

### Create a new migration (auto-generate from model changes)

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply all pending migrations

```bash
cd backend
alembic upgrade head
```

### Rollback one migration

```bash
cd backend
alembic downgrade -1
```

### View current migration status

```bash
cd backend
alembic current
```

### View migration history

```bash
cd backend
alembic history --verbose
```

### Create empty migration (manual)

```bash
cd backend
alembic revision -m "Description"
```

## Initial Setup (First Time)

After creating models, generate the initial migration:

```bash
cd backend
alembic revision --autogenerate -m "Initial schema with users, documents, summaries, mindmaps, api_logs"
alembic upgrade head
```

## Migration File Structure

```
alembic/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Template for new migration files
├── versions/           # Individual migration files
│   └── xxxxx_initial_schema.py
└── README.md           # This file
```

## Important Notes

- Always review auto-generated migrations before applying
- Test migrations on development database first
- Keep migrations small and focused
- Never edit applied migrations (create new ones instead)
- Commit migration files to version control

## Environment Configuration

Alembic reads `DATABASE_URL` from environment variables or `.env` file:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## Troubleshooting

### "Can't locate revision identified by 'xxxxx'"

Reset the alembic version table:

```bash
psql -d your_database -c "DELETE FROM alembic_version;"
alembic stamp head
```

### "Target database is not up to date"

```bash
alembic upgrade head
```

### Models not detected in autogenerate

Ensure all models are imported in `backend/src/models/__init__.py` and that file is imported in `alembic/env.py`.
