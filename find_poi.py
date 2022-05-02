from requests import get


def find_subcategories(category, lat, lon, r):
    url = "https://api.tomtom.com/search/2/nearbySearch/.json"
    params = {
        "lat": lat,
        "lon": lon,
        "radius": r,
        "view": "Unified",
        "categorySet": str(category),
        "relatedPois": "off",
        "key": "joA6ejluFqgrbSGdhuDQ1n0LqgnbCMQN"
    }
    response = get(url, params=params).json()
    results = response.results
    subcategories = []
    for result in results:
        subcategories.append(result["poi"]["categorySet"][0]["id"])
    return subcategories
