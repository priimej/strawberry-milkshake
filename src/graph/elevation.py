import requests

OPEN_ELEVATION_URL = "https://api.open-elevation.com/api/v1/lookup"

# Basic helper function to obtain data from the elevation api.
# given the latitude and longitude, return elevation in meters
# get the elevation from open elevation api

def get_elevation(lat, lng):
    res = requests.post(
        OPEN_ELEVATION_URL,
        json={"locations": [{"latitude": lat, "longitude": lng}]}
    )
    data = res.json()
    return data["results"][0]["elevation"]  # meters

# IN THE FUTURE, ADD SAFETY THRESHOLD TO ADJUST DOWNHILL PENALTIES
# e.g., if elevation drop > X meters over Y distance, turn the bonus into a penalty to avoid danger
# very niche fine tuning heuristic for later

def elevation_delta(node_a, node_b):
    elev_a = get_elevation(node_a.lat, node_a.lng)
    elev_b = get_elevation(node_b.lat, node_b.lng)
    
    delta = elev_b - elev_a  # positive if uphill, negative if downhill
    
    # Define penalty factors
    if delta > 0:
        # Uphill penalty
        return 1 + (delta / 100)  # example: 1% increase per meter of elevation gain
    elif delta < 0:
        # Downhill BONUS 
        # Very important to fine tune this. Safety is paramount but also users do want downhill routes.
        return 1 - (delta / 300)  # example: 0.33% increase per meter of elevation loss
    else:
        return 1  # flat terrain