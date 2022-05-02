import json

from requests import get


def find_subcategories(categories, lat, lon, r):
    url = "https://api.tomtom.com/search/2/nearbySearch/.json"
    with open("tomtom_key.txt", 'r') as f:
        key = f.read()
    params = {
        "lat": lat,
        "lon": lon,
        "radius": r * 1000,
        "view": "Unified",
        "categorySet": ','.join(categories),
        "relatedPois": "off",
        "key": key
    }
    response = get(url, params=params).json()
    with open("response.json", 'w') as jsonfile:
        json.dump(response, jsonfile)
    if not response["results"]:
        return []
    results = response["results"]
    subcategories = set()
    for result in results:
        poi = result["poi"]
        category_set = poi["categorySet"][0]
        subcategories.add(category_set["id"])
    return list(subcategories)
