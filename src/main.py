from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# API routes
from api.routes import router as api_router

# Graph + engine
from services.osm_graph import build_brooklyn_graph
from services import router_engine

# --------------------------------------------------
# App initialization
# --------------------------------------------------

app = FastAPI(
    title="Skate Maps API",
    description="Terrain- and elevation-aware skating routing engine for Brooklyn",
    version="1.0.0",
)

# --------------------------------------------------
# CORS (frontend access)
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Startup: load heavy resources ONCE
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    """
    Run this once! Only at startup
    """

    print("Starting Skate Maps backend...")
    print("Loading Brooklyn OSM graph...")

    graph = build_brooklyn_graph()

    # Inject graph into routing engine (single source of truth)
    router_engine.initialize(graph)

    print(f"✅ Graph loaded with {len(graph.nodes)} nodes")
    print("🛹 Routing engine ready")

# --------------------------------------------------
# Routes: Sending all of the HTTPs to the router
# --------------------------------------------------

app.include_router(api_router)

# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "skate-maps-backend"
    }

