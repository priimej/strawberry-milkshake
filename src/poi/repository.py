from typing import List
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from poi.models import PointOfInterest
import uuid

_db_url: str = None

def set_db_url(url: str):
    global _db_url
    _db_url = url
    
def require_db_url() -> str:
    if _db_url is None:
        raise ValueError("Database URL not set")
    return _db_url
    
class POIRepository:
    def __init__(self):
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=require_db_url()
        )
        
    def add_poi(self, city: str, name: str, lat: float, lng: float, author: str | None, category: str | None):
        poi_id = str(uuid.uuid4())

        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pois (id, city, name, lat, lng, author, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (poi_id, city, name, lat, lng, author, category)
                )
                conn.commit()
        finally:
            self.pool.putconn(conn)

        return poi_id

    def get_pois_for_city(self, city: str) -> List[PointOfInterest]:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, city, name, lat, lng, author, category
                    FROM pois
                    WHERE city = %s
                    """,
                    (city,)
                )
                rows = cur.fetchall()
        finally:
            self.pool.putconn(conn)

        return [
            PointOfInterest(*row)
            for row in rows
        ]
