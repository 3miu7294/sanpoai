!pip install requests folium polyline ipywidgets shapely

import requests, polyline, folium, time, math
import ipywidgets as widgets
from IPython.display import display, clear_output
from folium import Popup

API_KEY = "AIzaSyAk2JMfS9AJ8VapsL_B3-4OVU6HA95zvW8"

origin_input = widgets.Text(value="", description="出発地:", style={'description_width': 'initial'})
destination_input = widgets.Text(value="", description="目的地:", style={'description_width': 'initial'})
mode_select = widgets.ToggleButtons(options=[("⭐ 高評価重視", "high"), ("💰 リーズナブル重視", "cheap")], description="条件:", style={'description_width': 'initial'})
search_button = widgets.Button(description="検索", button_style='success', icon='search')
display(origin_input, destination_input, mode_select, search_button)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_directions(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {"origin": origin, "destination": destination, "mode": "walking", "language": "ja", "key": API_KEY}
    res = requests.get(url, params=params).json()
    if res["status"] != "OK":
        print("Directions API error:", res)
        return [], None, None
    route = res["routes"][0]["overview_polyline"]["points"]
    leg = res["routes"][0]["legs"][0]
    distance = leg["distance"]["text"]
    duration = leg["duration"]["text"]
    return polyline.decode(route), distance, duration

def get_nearby_places(lat, lng, radius, place_type="restaurant", open_now=True):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
#①
        "opennow": str(open_now).lower(),
#②
        "language": "ja"
    }
    res = requests.get(url, params=params).json()
    return res.get("results", [])

#③
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": API_KEY,
        "language": "ja",
        "fields": "name,rating,price_level,formatted_address,opening_hours,editorial_summary,geometry"
    }
    res = requests.get(url, params=params).json()
    if res.get("status") == "OK":
        return res["result"]
    return {}

def is_within_route(place_lat, place_lng, route_coords, max_meter=50):
    for rlat, rlng in route_coords:
        d = haversine(place_lat, place_lng, rlat, rlng)
        if d <= max_meter:
            return True
    return False

def run_search(_):
    clear_output(wait=True)
    display(origin_input, destination_input, mode_select, search_button)
    origin = origin_input.value.strip()
    destination = destination_input.value.strip()
    mode = mode_select.value
    if not origin or not destination:
        print("出発地と目的地を入力してください。")
        return
    if mode == "high":
        min_rating, max_price = 4.2, 4
    else:
        min_rating, max_price = 0, 2
    print(f"🚶 経路を取得中... ({origin} → {destination})")
    route_coords, distance, duration = get_directions(origin, destination)
    if not route_coords:
        print("経路が取得できませんでした。")
        return
    print(f"🗺️ 距離: {distance} / 所要時間: {duration}")
#④
    sample_points = route_coords[::max(1, len(route_coords)//10)]
    places = []
    for lat, lng in sample_points:
        data = get_nearby_places(lat, lng, radius=150)
        for p in data:
            rating = p.get("rating", 0)
            price = p.get("price_level", 5)
            plat = p["geometry"]["location"]["lat"]
            plng = p["geometry"]["location"]["lng"]
            if rating < min_rating or price > max_price:
                continue
            if not is_within_route(plat, plng, route_coords, max_meter=50):
                continue
            details = get_place_details(p["place_id"])
            places.append({
                "name": p["name"],
                "rating": rating,
                "price": price,
                "lat": plat,
                "lng": plng,
                "vicinity": details.get("formatted_address", p.get("vicinity", "")),
                "hours": "<br>".join(details.get("opening_hours", {}).get("weekday_text", [])),
                "summary": details.get("editorial_summary", {}).get("overview", "")
            })
  #⑤
        time.sleep(1)
    unique_places = {p["name"]: p for p in places}.values()
    center_lat = sum([c[0] for c in route_coords]) / len(route_coords)
    center_lng = sum([c[1] for c in route_coords]) / len(route_coords)
    m = folium.Map(location=[center_lat, center_lng], zoom_start=14)
    folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.7).add_to(m)
    for p in unique_places:
        info = f"{p['name']} ⭐{p['rating']} / ¥{p['price']}<br>{p['vicinity']}"
        if p["hours"]:
            info += f"<br>{p['hours']}"
        if p["summary"]:
            info += f"<br>{p['summary']}"
        popup = Popup(info, max_width=300)
        folium.Marker(
            [p["lat"], p["lng"]],
            popup=popup,
            icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
        ).add_to(m)
    display(m)

search_button.on_click(run_search)