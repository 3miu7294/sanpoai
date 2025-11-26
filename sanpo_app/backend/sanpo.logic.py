import requests, polyline, math, time

API_KEY = "AIzaSyAk2JMfS9AJ8VapsL_B3-4OVU6HA95zvW8"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_directions(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "walking",
        "key": API_KEY
    }
    res = requests.get(url, params=params).json()
    points = res["routes"][0]["overview_polyline"]["points"]
    route_coords = polyline.decode(points)
    return route_coords

def search_places(origin, destination, mode):
    route = get_directions(origin, destination)

    return {
        "route": route,  # [[lat,lng], [lat,lng], ...]
        "mode": mode
    }
