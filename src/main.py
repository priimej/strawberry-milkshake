from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# API routes
from api.path_router import router as api_router
from poi.poi_router import router as poi_router

# Graph + engine
from services.algos import router_engine
from services.graph.citygraphmanager import CityGraph, CityGraphManager

# POI Repository
from poi.repository import POIRepository, set_db_url


# --------------------------------------------------
# App initialization
# --------------------------------------------------

app = FastAPI(
    title="Skate Maps API",
    description="Terrain- and elevation-aware skating routing engine for Brooklyn",
    version="1.0.0",
)

city_manager = CityGraphManager(
    max_memory_mb=4000,
    max_cities=5
)

db_url = "postgresql://skate_user:skate_password@localhost:5432/skate_db"

# --------------------------------------------------
# CORS (frontend access)
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # OK for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Startup: Load the entire brooklyn graph into cache
# --------------------------------------------------
@app.on_event("startup")
def warm_start():
    
    print("[startup] Starting Strawberry Milkshake Backend")
    
    try:
        print("[startup] Beginning loading Brooklyn graph process")
        city_manager.get_city("Brooklyn")
        print("[startup] Brooklyn graph loaded")
        print(f"[startup] Brooklyn graph memory: {city_manager._current_memory_mb:.2f} MB")
        bklyn_graph: CityGraph = city_manager._graphs["Brooklyn"].graph
        print(f"[startup] Number of nodes in Brooklyn: {len(bklyn_graph.nodes)}")
    except Exception as e:
        print(f"[startup] Failed to load Brooklyn: {e}")
    try:
        print("[startup] Setting POI repository database URL")
        set_db_url(db_url)
        print("[startup] POI repository database URL set")
    except Exception as e:
        print(f"[startup] Failed to set POI repository database URL: {e}")
        
    # inject the city manager object into the router engine
    # further references to the city manager will be done through the router engine
    router_engine.initialize(city_manager)

# --------------------------------------------------
# Route to routerrrr
# --------------------------------------------------

app.include_router(api_router)
app.include_router(poi_router)

# --------------------------------------------------
# Health check (optional but recommended)
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "skate-maps-backend"
    }
