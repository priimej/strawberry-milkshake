from fastapi import APIRouter
from models.schemas import RouteRequest
import services.router_engine

router = APIRouter()

# All route definitions here:

#given the request to calculate a route, and the data regarding the start and end points
# calculate the skate route using the router engine service

#returns a dictionary with the route information
@router.get("/calculate_route_annon")
def calculate_route(data: RouteRequest):
    
    route = services.router_engine.compute_skate_route(
        data.start.lat, data.start.lng,
        data.end.lat, data.end.lng)
    
    if route is None:
        raise ValueError("No route found between the specified points.")
    #sending back a JSON file
    return { route }
