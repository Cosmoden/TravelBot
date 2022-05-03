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
    desc = f"""{properties["name"]}
    {properties["description"]}
    Телефон: {properties["CompanyMetaData"]["Phones"][0]["formatted"]}
    Часы работы: {properties["CompanyMetaData"]["Hours"]["text"]}
    {website}"""

    return desc
