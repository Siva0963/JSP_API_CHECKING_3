from fastapi import FastAPI
from app.api.auth_routes import router as auth_router
from app.api.location_routes import router as location_router

app = FastAPI(title="Voting Master API")

app.include_router(auth_router)
app.include_router(location_router)