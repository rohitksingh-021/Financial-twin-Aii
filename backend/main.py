"""Financial Twin AI — FastAPI Backend"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import customers, dashboard, vitality, twin, wealth_gps, simulator, advisor, stress, life_events

app = FastAPI(
    title="Financial Twin AI",
    description="AI-Powered Financial Digital Twin Engine for Banking",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/api", tags=["Customer Data"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(vitality.router, prefix="/api", tags=["Vitality Score"])
app.include_router(twin.router, prefix="/api", tags=["Financial Twin"])
app.include_router(wealth_gps.router, prefix="/api", tags=["Wealth GPS"])
app.include_router(simulator.router, prefix="/api", tags=["Simulator"])
app.include_router(advisor.router, prefix="/api", tags=["AI Advisor"])
app.include_router(stress.router, prefix="/api", tags=["Stress Monitor"])
app.include_router(life_events.router, prefix="/api", tags=["Life Events"])


@app.get("/")
def root():
    return {"status": "running", "app": "Financial Twin AI", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
