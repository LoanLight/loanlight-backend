from fastapi import FastAPI
from routes.health_routes import router as health_router
from routes.auth_routes import router as auth_router
from routes.federal_loan_routes import router as federal_router
from routes.private_loan_routes import router as private_router
from routes.job_offer_routes import router as job_offer_router
from routes.housing_routes import router as housing_router
from routes.plan_routes import router as plan_router

app = FastAPI()

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(federal_router)
app.include_router(private_router)
app.include_router(job_offer_router)
app.include_router(housing_router)
app.include_router(plan_router)