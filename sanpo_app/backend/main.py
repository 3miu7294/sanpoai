from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, polyline

API_KEY = "AIzaSyAk2JMfS9AJ8VapsL_B3-4OVU6HA95zvW8"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_directions(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "walking",
        "language": "ja",
        "key": API_KEY,
    }
    res = requests.get(url, params=params).json()
    if res["status"] != "OK":
        return []

    points = res["routes"][0]["overview_polyline"]["points"]
    route_coords = polyline.decode(points) 
    return route_coords

@app.get("/search")
def search(origin: str, destination: str, mode: str = "high"):
    route = get_directions(origin, destination)
    return {"route": route, "mode": mode}
