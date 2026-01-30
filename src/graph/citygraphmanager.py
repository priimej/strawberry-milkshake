from dataclasses import dataclass
import time
import threading
import time
from collections import OrderedDict
from services.graph.osm_graph import load_graph_from_osm
from services.graph.graph import Graph

@dataclass
class CityGraph:
    city_id: str
    graph: Graph               # your custom graph
    node_index: dict           # optional: node lookup
    bounds: tuple              # (min_lat, min_lon, max_lat, max_lon)
    memory_mb: float
    loaded_at: float
    last_accessed: float

# Assumptions. Since we are pulling city_id from the front end,
# we can assume that city_id is a valid identifier for a city we support.

class CityGraphManager:
    def __init__(
        self,
        max_memory_mb: int = 3000,
        max_cities: int = 5
    ):
        self.max_memory_mb = max_memory_mb
        self.max_cities = max_cities

        # LRU cache: city_id -> CityGraph
        self._graphs = OrderedDict()

        self._current_memory_mb = 0.0
        self._lock = threading.Lock()

    # ---------- Public API ----------

    def get_city(self, city_id: str) -> CityGraph:
        with self._lock:
            if city_id in self._graphs:
                city: CityGraph = self._graphs.pop(city_id)
                city.last_accessed = time.time()
                self._graphs[city_id] = city  # move to end (LRU)
                return city

        # Load outside lock (important!)
        city = self._load_city(city_id)

        with self._lock:
            self._ensure_capacity(city.memory_mb)
            self._graphs[city_id] = city
            self._current_memory_mb += city.memory_mb

        return city

    def list_loaded_cities(self):
        with self._lock:
            return [
                {
                    "city": city.city_id,
                    "memory_mb": city.memory_mb,
                    "last_accessed": city.last_accessed
                }
                for city in self._graphs.values()
            ]

    def unload_city(self, city_id: str):
        with self._lock:
            city: CityGraph = self._graphs.pop(city_id, None)
            if city:
                self._current_memory_mb -= city.memory_mb

    # ---------- Internal helpers ----------

    # Given a new graph of size incoming_mb, evict cities until we have capacity
    # to ensure we have enough space to handle the new graph
    def _ensure_capacity(self, incoming_mb: float):
        while (
            len(self._graphs) >= self.max_cities
            or self._current_memory_mb + incoming_mb > self.max_memory_mb
        ):
            evicted: CityGraph = self._graphs.popitem(last=False)
            self._current_memory_mb -= evicted.memory_mb

    def _load_city(self, city_id: str):
        # --- EXPENSIVE STEP ---
        graph, bounds, memory_mb = load_graph_from_osm(city_id)
        now = time.time()
        return CityGraph(
            city_id=city_id,
            graph=graph,
            node_index={},  # optional
            bounds=bounds,
            memory_mb=memory_mb,
            loaded_at=now,
            last_accessed=now,
        )
            
    

