from fastapi import APIRouter
from services import router_engine
from pydantic import BaseModel

router = APIRouter()

class Coordinates(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates

# Once the cords are sent from the frontend, this function calculates the route by sending it to main and letting the calculations be done throught that.
@router.post("/main")
async def calculate_route(request: RouteRequest):
    """Calculate skating route between two points"""
    try:
        result = router_engine.compute_skate_route(
            start_lat=request.start.lat,
            start_lng=request.start.lng,
            end_lat=request.end.lat,
            end_lng=request.end.lng
        )
        return result
    except Exception as e:
        return {"error": str(e)}


