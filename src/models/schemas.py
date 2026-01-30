from pydantic import BaseModel

class Coordinates(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates
    city: str
    
class CityRequest(BaseModel):
    city: str

class POICreateRequest(BaseModel):
    city: str
    name: str
    lat: float
    lng: float
    author: str | None = None
    category: str | None = None
