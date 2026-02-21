from fastapi import FastAPI

from routes.health_routes import router as health_router
from routes.auth_routes import router as auth_router
from routes.loan_routes import router as loan_router
from routes.offer_routes import router as offer_router
from routes.plan_routes import router as plan_router
from routes.hud_routes import router as hud_router
from routes.narrative_routes import router as narrative_router

# Ensure entities are imported so create_all sees them
import entities.account_entity  # noqa: F401
import entities.loan_entity     # noqa: F401
import entities.offer_entity    # noqa: F401
import entities.plan_entity     # noqa: F401

from database.session import engine
from database.base import Base

app = FastAPI(title="LoanLight API")

# Hackathon mode: auto-create tables at startup (no Alembic).
# Comment out if you prefer running scripts/db_reset.py.
Base.metadata.create_all(bind=engine)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(loan_router)
app.include_router(offer_router)
app.include_router(plan_router)
app.include_router(hud_router)
app.include_router(narrative_router)