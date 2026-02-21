# LoanLight Backend

## run locally 
1. Open in VS Code
2. "Reopen in Container"
3. API runs at http://localhost:8000

## reset DB (local)
Inside container:
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@db:5432/loanlight"
python scripts/db_reset.py reset --force

## when Switching to RDS
Set ENV=dev and update .env.dev DATABASE_URL.
On EC2:
export ENV=dev
export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@RDS_ENDPOINT:5432/loanlight"
python scripts/db_reset.py reset --force
uvicorn app.main:app --host 0.0.0.0 --port 8000