from requests import get
from math import cos, pi


def info(org_name, lon, lat, r):
    lon = float(lon)
    lat = float(lat)
    search_api_server = "https://search-maps.yandex.ru/v1/"
    with open("search_key.txt", 'r') as f:
        api_key = f.read()
    d1 = r / (111.321 * cos(lat / 180 * pi))
    d2 = r / 111.135
    search_params = {
        "apikey": api_key,
        "text": org_name,
        "lang": "ru_RU",
        "ll": ','.join(map(str, [lon, lat])),
        "spn": ','.join(map(str, [d1, d2])),
        "type": "biz"
    }
    response = get(search_api_server, params=search_params)
    json_response = response.json()
    properties = json_response["features"][0]["properties"]
    try:
        website = f"""Сайт: {properties["CompanyMetaData"]["url"]}"""
    except KeyError:
        website = ""
    org_ll = ','.join(
        map(str, json_response["features"][0]["geometry"]["coordinates"]))
    static_api_request = f"https://static-maps.yandex.ru/1.x/?ll={','.join(map(str, [lon, lat]))}&" \
                         f"spn={','.join(map(str, [d1, d2]))}&l=map&pt={org_ll},pm2rdm"
    if "Phones" in properties["CompanyMetaData"] and "Hours" in properties["CompanyMetaData"]:
        return [properties["name"], properties["description"],
                properties["CompanyMetaData"]["Phones"][0]["formatted"],
                properties["CompanyMetaData"]["Hours"]["text"], website, static_api_request]
    elif "Phones" in properties["CompanyMetaData"]:
        return [properties["name"], properties["description"],
                properties["CompanyMetaData"]["Phones"][0]["formatted"], website, static_api_request]
    elif "Hours" in properties["CompanyMetaData"]:
        return [properties["name"], properties["description"],
                properties["CompanyMetaData"]["Hours"]["text"], website, static_api_request]
    else:
        return [properties["name"], properties["description"], website, static_api_request]
