from fastapi import APIRouter
from models.schemas import POICreateRequest 
from typing import List
from poi.models import PointOfInterest
from poi.repository import POIRepository as poi_repo

router = APIRouter(prefix="/poi")

# create a new point of interest
@router.post("")
def create_poi(req: POICreateRequest):
    poi_id = poi_repo.add_poi(
        city=req.city,
        name=req.name,
        lat=req.lat,
        lng=req.lng,
        author=req.author,
        category=req.category
    )
    return {"id": poi_id}

# pull all points of interest for a given city
@router.get("")
def list_pois(city: str):
    pois: List[PointOfInterest] = poi_repo.get_pois_for_city(city)
    return [
        {
            "id": p.id,
            "name": p.name,
            "coord": [p.lat, p.lng],
            "category": p.category
        }
        for p in pois
    ]
