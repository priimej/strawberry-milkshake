# Helper file that contains the terrain penalty data and function

SURFACE_PENALTIES = {
    "asphalt": 0.85,
    "paved": 0.89,
    "concrete": 1,
    "paving_stones": 1.4,
    "cobblestone": 2.0,
    "gravel": 2.5,
    "dirt": 3.0,
    "sand": 5.0,
}

HIGHWAY_PENALTIES = {
    "steps": 10.0,
    "footway": 1.2,
    "path": 1.3,
    "cycleway": 0.85,   # skating bonus
    "residential": 1.0,
    "service": 1.1
}

def terrain_penalty(surface, highway):
    # if the input is a list, arbitrarily pick the first element
    if (isinstance(surface, list)):
        surface = surface[0]
        
    if (isinstance(highway, list)):
        if( "steps" in highway):
            highway = "steps"
        else:
            highway = highway[0]
            
    s = SURFACE_PENALTIES.get(surface, 1.3)
    h = HIGHWAY_PENALTIES.get(highway, 1.1)
    return s * h
