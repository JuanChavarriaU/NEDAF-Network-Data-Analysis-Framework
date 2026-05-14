from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import data, explore, graph, ai

app = FastAPI(title="NEDAF Backend API", description="Polars-powered backend for NEDAF Web")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/api/data", tags=["Data Management"])
app.include_router(explore.router, prefix="/api/explore", tags=["Data Exploration"])
app.include_router(graph.router, prefix="/api/graph", tags=["Network Visualization"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Insights"])

@app.get("/")
def read_root():
    return {"message": "Welcome to NEDAF Backend API"}
